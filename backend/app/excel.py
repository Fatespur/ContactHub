"""The contract's fixed eight-column Excel import and export."""

import re
from datetime import datetime, timezone
from io import BytesIO
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from flask import Blueprint, jsonify, request, send_file
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.utils.exceptions import InvalidFileException
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from . import contact_filters, success, timestamp, validate_contact, validation_error
from .db import CHILD_FIELDS, get_db, insert_contact, serialize_contact


excel_api = Blueprint("excel", __name__, url_prefix="/api/v1/contacts")
HEADERS = ("姓名", "分组", "是否收藏", "电话", "邮箱", "社交账号", "地址", "备注")
MAX_FILE_SIZE = 10 * 1024 * 1024
MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class InvalidExcel(BadRequest):
    """An invalid or oversized Excel upload."""


@excel_api.errorhandler(InvalidExcel)
@excel_api.errorhandler(RequestEntityTooLarge)
def invalid_file(error):
    """Return the file-error contract, including framework upload limits."""
    return jsonify(
        code=400, error_code="INVALID_FILE",
        message="请上传有效的 Excel 文件 (.xlsx)，且文件不得超过 10MB", details=None,
    ), 400


def decode_items(text: str, table: str) -> list[dict]:
    """Decode newline-first items, first-colon labels and primary markers."""
    fields = CHILD_FIELDS[table]
    defaults = {"phones": "手机", "emails": "个人", "social_accounts": "其他", "addresses": "其他"}
    parts = re.split(r"\r?\n", text) if "\n" in text else re.split(r"[;；]", text)
    items = []
    for part in parts:
        if not part.strip():
            continue
        pair = re.split(r"[:：]", part, maxsplit=1)
        label, value = pair if len(pair) == 2 else (defaults[table], part)
        item = {fields[0]: label, fields[1]: value}
        if "is_primary" in fields:
            item["is_primary"] = label.endswith("*")
            if item["is_primary"]:
                item[fields[0]] = label[:-1]
        items.append(item)
    if items and "is_primary" in fields:
        primary = next((i for i, item in enumerate(items) if item["is_primary"]), 0)
        for index, item in enumerate(items):
            item["is_primary"] = index == primary
    return items


def encode_items(items: list[dict], table: str) -> str:
    """Encode child arrays using exactly the documented labels and separators."""
    fields = CHILD_FIELDS[table]
    parts = []
    for item in items:
        marker = "*" if "is_primary" in fields and item["is_primary"] else ""
        parts.append(f"{item[fields[0]]}{marker}:{item[fields[1]]}")
    return "\n".join(parts)


@excel_api.get("/export")
def export_contacts():
    """Download every matching contact, ignoring list pagination parameters."""
    where, parameters = contact_filters()
    rows = get_db().execute(
        "SELECT c.* FROM contacts c" + where + " ORDER BY c.id", parameters,
    ).fetchall()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "联系人"
    sheet.append(HEADERS)
    output = BytesIO()
    try:
        for row_number, row in enumerate(rows, 2):
            contact = serialize_contact(row)
            values = [
                contact["name"], contact["group"], "是" if contact["is_favorite"] else "否",
                *(encode_items(contact[table], table) for table in CHILD_FIELDS),
                contact["notes"],
            ]
            for column, value in enumerate(values, 1):
                # openpyxl otherwise silently truncates long strings or treats '=' as a formula.
                if value is not None and (
                    len(value) > 32767 or ILLEGAL_CHARACTERS_RE.search(value)
                ):
                    validation_error({"file": ["联系人文本超出 Excel 单元格可表示范围"]})
                cell = sheet.cell(row_number, column)
                cell.value = value
                cell.data_type = "s"
        workbook.save(output)
    except Exception:
        output.close()
        raise
    finally:
        workbook.close()
    output.seek(0)
    filename = "contacts_export_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + ".xlsx"
    response = send_file(output, mimetype=MIME_TYPE, as_attachment=True, download_name=filename)
    response.call_on_close(output.close)
    return response


def read_upload() -> Workbook:
    """Check actual byte size and OOXML type before parsing a non-macro workbook."""
    # Allow multipart framing above the file limit, while still bounding the whole request.
    request.max_content_length = MAX_FILE_SIZE + 1024 * 1024
    upload = request.files.get("file")
    if upload is None or not upload.filename or not upload.filename.lower().endswith(".xlsx"):
        raise InvalidExcel()
    data = upload.stream.read(MAX_FILE_SIZE + 1)
    if not data or len(data) > MAX_FILE_SIZE:
        raise InvalidExcel()
    try:
        with BytesIO(data) as source, ZipFile(source) as archive:
            manifest = ElementTree.fromstring(archive.read("[Content_Types].xml"))
            expected_type = MIME_TYPE + ".main+xml"
            if not any(item.get("ContentType") == expected_type for item in manifest):
                raise InvalidExcel()
            # A normal (non-read-only) load parses all rows before any database writes.
            workbook = load_workbook(source, data_only=False, keep_links=False)
    except (BadZipFile, InvalidFileException, OSError, EOFError, SyntaxError,
            ValueError, KeyError, TypeError, IndexError) as error:
        raise InvalidExcel() from error
    if not workbook.worksheets:
        workbook.close()
        raise InvalidExcel()
    sheet = workbook.worksheets[0]
    header = tuple(cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1)))
    if header != HEADERS:
        workbook.close()
        raise InvalidExcel()
    return workbook


@excel_api.post("/import")
def import_contacts():
    """Import independent rows atomically and report expected row validation failures."""
    workbook = read_upload()
    statistics = {"total_rows": 0, "success_count": 0, "failed_count": 0, "errors": []}
    try:
        for row_number, cells in enumerate(workbook.worksheets[0].iter_rows(min_row=2), 2):
            if all(cell.value is None or cell.value == "" for cell in cells):
                continue
            statistics["total_rows"] += 1
            values = ["" if cell.value is None else str(cell.value) for cell in cells]
            try:
                if any(cell.data_type == "f" for cell in cells):
                    validation_error({"file": ["不接受公式单元格，请改为文本或普通值"]})
                favorite = values[2].strip().lower()
                if favorite not in ("", "是", "否", "true", "false", "1", "0"):
                    validation_error({"is_favorite": ["收藏状态必须为 是/否、true/false 或 1/0"]})
                body = {
                    "name": values[0], "group": values[1] or None,
                    "is_favorite": favorite in ("是", "true", "1"), "notes": values[7] or None,
                    **{table: decode_items(values[column], table)
                       for column, table in enumerate(CHILD_FIELDS, 3)},
                }
                contact = validate_contact(body)
            except BadRequest as error:
                reason = "; ".join(
                    f"{field}: {', '.join(messages)}"
                    for field, messages in error.description.items()
                )
                statistics["failed_count"] += 1
                statistics["errors"].append({
                    "row": row_number, "name": values[0], "reason": reason,
                })
                continue
            with get_db():
                insert_contact(contact, timestamp())
            statistics["success_count"] += 1
    finally:
        workbook.close()
    return success(statistics, "导入完成")
