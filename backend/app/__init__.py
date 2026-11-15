"""Minimal Flask application for the EE308FZ address book."""

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, current_app, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .db import (
    CHILD_FIELDS, close_db, get_db, init_db, insert_children, insert_contact, serialize_contact,
)


EDITABLE_FIELDS = {"name", "group", "is_favorite", "notes", *CHILD_FIELDS}
CHILD_DEFAULTS = {
    "phones": {"label": "手机", "is_primary": False},
    "emails": {"label": "个人", "is_primary": False},
    "social_accounts": {"platform": "其他"},
    "addresses": {"label": "其他", "is_primary": False},
}


def validation_error(details: dict) -> None:
    """Raise a field validation error handled by the global JSON handler."""
    abort(400, description=details)


def json_body() -> dict:
    """Read a JSON object, mapping malformed or non-JSON bodies to HTTP 400."""
    if not request.is_json:
        validation_error({"body": ["请求体必须为 JSON 对象"]})
    body = request.get_json()
    if not isinstance(body, dict):
        validation_error({"body": ["请求体必须为 JSON 对象"]})
    return body


def validate_contact(body: dict, full_update: bool = False) -> dict:
    """Validate and apply contract defaults once at the request boundary."""
    if full_update:
        missing = EDITABLE_FIELDS - body.keys()
        if missing:
            validation_error({field: ["全量更新必须提供此字段"] for field in sorted(missing)})
    contact = {"group": None, "notes": None, "is_favorite": False}
    contact.update({field: body[field] for field in EDITABLE_FIELDS if field in body})
    errors = {}
    name = body.get("name")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 50:
        errors["name"] = ["姓名不能为空且长度不能超过 50 字符"]
    else:
        contact["name"] = name.strip()
    for field in ("group", "notes"):
        value = contact[field]
        if value is not None and not isinstance(value, str):
            errors[field] = ["必须为字符串或 null"]
    if isinstance(contact["notes"], str) and len(contact["notes"]) > 500:
        errors["notes"] = ["备注不能超过 500 字符"]
    if type(contact["is_favorite"]) is not bool:
        errors["is_favorite"] = ["必须为 boolean"]
    for table, fields in CHILD_FIELDS.items():
        items = body.get(table, [])
        contact[table] = []
        if not isinstance(items, list):
            errors[table] = ["必须为数组"]
            continue
        for index, item in enumerate(items, 1):
            if not isinstance(item, dict):
                errors.setdefault(table, []).append(f"第 {index} 项必须为对象")
                continue
            child = {**CHILD_DEFAULTS[table], **item}
            for field in fields:
                value = child.get(field)
                if field == "is_primary":
                    valid = type(value) is bool
                else:
                    valid = isinstance(value, str)
                    if field in ("number", "email", "account", "address"):
                        valid = valid and bool(value.strip())
                if valid and field == "number":
                    valid = re.fullmatch(r"[0-9+()\-]+", value) is not None
                if valid and field == "email":
                    valid = re.fullmatch(r"[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+", value) is not None
                if valid and field == "address":
                    valid = len(value) <= 200
                if not valid:
                    errors.setdefault(table, []).append(f"第 {index} 项 {field} 格式不合法")
            contact[table].append(child)
    if errors:
        validation_error(errors)
    return contact


def timestamp() -> str:
    """Return the current time in ISO 8601 UTC format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def success(data=None, message: str = "success", status: int = 200):
    """Build the contract's success response."""
    return jsonify(code=status, message=message, data=data), status


def find_contact(contact_id: int):
    """Fetch a contact or raise the contract's not-found error."""
    row = get_db().execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    if row is None:
        abort(404, description="联系人不存在")
    return row


def contact_filters() -> tuple[str, list]:
    """Build the shared list/export filter using parameterized SQL."""
    conditions, parameters = [], []
    if "is_favorite" in request.args:
        value = request.args["is_favorite"].lower()
        if value not in ("true", "false", "1", "0"):
            validation_error({"is_favorite": ["必须为 true、false、1 或 0"]})
        conditions.append("c.is_favorite = ?")
        parameters.append(value in ("true", "1"))
    if "group" in request.args:
        conditions.append('c."group" = ?')
        parameters.append(request.args["group"])
    keyword = request.args.get("keyword", "")
    if keyword:
        # Treat SQL wildcard characters as literal search text.
        escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = "%" + escaped + "%"
        conditions.append(
            "(c.name LIKE ? ESCAPE '\\' OR c.notes LIKE ? ESCAPE '\\' "
            "OR EXISTS (SELECT 1 FROM phones p WHERE p.contact_id = c.id "
            "AND p.number LIKE ? ESCAPE '\\') "
            "OR EXISTS (SELECT 1 FROM emails e WHERE e.contact_id = c.id "
            "AND e.email LIKE ? ESCAPE '\\'))"
        )
        parameters.extend([pattern] * 4)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    return where, parameters


def create_app(test_config: dict | None = None) -> Flask:
    """Create an isolated application; test_config can supply a temporary database."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.environ.get("DATABASE")
        or str(Path(app.instance_path) / "address_book.sqlite3"),
    )
    if test_config is not None:
        app.config.update(test_config)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    app.json.ensure_ascii = False
    app.json.mimetype = "application/json; charset=utf-8"
    origins = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    CORS(app, resources={
        r"/api/v1/*": {
            "origins": "*" if "*" in origins else (origins or "http://localhost:5173"),
        },
    })
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    @app.errorhandler(HTTPException)
    def http_error(error):
        status = error.code
        details = error.description if isinstance(error.description, dict) else None
        codes = {400: "VALIDATION_ERROR", 404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
        message = "输入参数有误" if status == 400 else error.description
        return jsonify(
            code=status, error_code=codes.get(status, error.name.upper().replace(" ", "_")),
            message=message, details=details,
        ), status

    @app.errorhandler(Exception)
    def internal_error(error):
        current_app.logger.exception("Unhandled API error")
        return jsonify(
            code=500, error_code="INTERNAL_SERVER_ERROR", message="服务器内部错误", details=None,
        ), 500

    @app.get("/api/v1/contacts")
    def list_contacts():
        pagination = {}
        for field, default, maximum in (("page", "1", None), ("page_size", "10", 100)):
            raw = request.args.get(field, default)
            if not re.fullmatch(r"[0-9]+", raw):
                validation_error({field: ["必须为合法正整数"]})
            try:
                value = int(raw)
            except ValueError:
                validation_error({field: ["必须为合法正整数"]})
            if value < 1 or (maximum is not None and value > maximum):
                validation_error({field: ["分页参数超出范围"]})
            pagination[field] = value
        where, parameters = contact_filters()
        db = get_db()
        total = db.execute(
            "SELECT count(*) FROM contacts c" + where, parameters,
        ).fetchone()[0]
        offset = (pagination["page"] - 1) * pagination["page_size"]
        rows = []
        if offset < total:
            rows = db.execute(
                "SELECT c.* FROM contacts c" + where + " ORDER BY c.id LIMIT ? OFFSET ?",
                (*parameters, pagination["page_size"], offset),
            ).fetchall()
        return success({
            **pagination, "total": total, "items": [serialize_contact(row) for row in rows],
        })

    @app.get("/api/v1/contacts/<int:contact_id>")
    def get_contact(contact_id: int):
        return success(serialize_contact(find_contact(contact_id)))

    @app.post("/api/v1/contacts")
    def create_contact():
        contact = validate_contact(json_body())
        now = timestamp()
        db = get_db()
        with db:
            contact_id = insert_contact(contact, now)
        return success({"id": contact_id}, "联系人创建成功", 201)

    @app.put("/api/v1/contacts/<int:contact_id>")
    def update_contact(contact_id: int):
        find_contact(contact_id)
        contact = validate_contact(json_body(), full_update=True)
        db = get_db()
        with db:
            db.execute(
                'UPDATE contacts SET name = ?, "group" = ?, is_favorite = ?, notes = ?, '
                "updated_at = ? WHERE id = ?",
                (contact["name"], contact["group"], contact["is_favorite"], contact["notes"],
                 timestamp(), contact_id),
            )
            for table in CHILD_FIELDS:
                db.execute(f"DELETE FROM {table} WHERE contact_id = ?", (contact_id,))
            insert_children(contact_id, contact)
        return success({"id": contact_id}, "联系人更新成功")

    @app.delete("/api/v1/contacts/<int:contact_id>")
    def delete_contact(contact_id: int):
        db = get_db()
        with db:
            cursor = db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            if cursor.rowcount == 0:
                abort(404, description="联系人不存在或已被删除")
        return success(message="联系人已删除")

    @app.patch("/api/v1/contacts/<int:contact_id>/favorite")
    def set_favorite(contact_id: int):
        body = json_body()
        if "is_favorite" not in body or type(body["is_favorite"]) is not bool:
            validation_error({"is_favorite": ["必须提供 boolean"]})
        db = get_db()
        with db:
            cursor = db.execute(
                "UPDATE contacts SET is_favorite = ?, updated_at = ? WHERE id = ?",
                (body["is_favorite"], timestamp(), contact_id),
            )
            if cursor.rowcount == 0:
                abort(404, description="联系人不存在")
        return success({"id": contact_id, "is_favorite": body["is_favorite"]}, "收藏状态更新成功")

    from .excel import excel_api

    app.register_blueprint(excel_api)
    return app
