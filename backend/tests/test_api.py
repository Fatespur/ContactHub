"""HTTP contracts and persistence against a real temporary SQLite database."""

import sqlite3
from datetime import datetime

import pytest

from app import create_app
from app.db import CHILD_FIELDS, get_db


URL = "/api/v1/contacts"


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "contacts.sqlite3")})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def contact():
    return {
        "name": "  张三  ", "group": "同学", "is_favorite": False, "notes": "软件工程",
        "phones": [
            {"number": "13800138000", "is_primary": True},
            {"label": "工作", "number": "+86(591)-88888888"},
        ],
        "emails": [{"email": "zhang@example.com"}, {"email": "work@example.com"}],
        "social_accounts": [{"platform": "GitHub", "account": "https://github.com/zhang"}],
        "addresses": [{"address": "福州大学", "is_primary": True}],
    }


def create(client, body):
    response = client.post(URL, json=body)
    assert response.status_code == 201
    assert response.json == {
        "code": 201, "message": "联系人创建成功", "data": {"id": response.json["data"]["id"]},
    }
    return response.json["data"]["id"]


def assert_error(response, status, code):
    assert response.status_code == status
    assert set(response.json) == {"code", "error_code", "message", "details"}
    assert response.json["code"] == status
    assert response.json["error_code"] == code
    if status != 400:
        assert response.json["details"] is None


def test_create_detail_defaults_and_persistence(app, client, contact):
    contact_id = create(client, contact)
    assert create(client, contact) != contact_id  # Duplicate names are allowed.
    expected = {**contact, "id": contact_id, "name": "张三"}
    expected["phones"] = [
        {"label": "手机", "number": "13800138000", "is_primary": True},
        {"label": "工作", "number": "+86(591)-88888888", "is_primary": False},
    ]
    expected["emails"] = [
        {"label": "个人", "email": email["email"], "is_primary": False}
        for email in contact["emails"]
    ]
    expected["addresses"] = [{"label": "其他", "address": "福州大学", "is_primary": True}]
    stored = client.get(f"{URL}/{contact_id}").json["data"]
    for field in ("created_at", "updated_at"):
        assert stored[field].endswith("Z")
        assert datetime.fromisoformat(stored[field]).utcoffset().total_seconds() == 0
        expected[field] = stored[field]
    assert stored == expected
    restarted = create_app({"TESTING": True, "DATABASE": app.config["DATABASE"]})
    assert restarted.test_client().get(f"{URL}/{contact_id}").json["data"] == expected
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT count(*) FROM contacts").fetchone()[0] == 2
        assert db.execute("SELECT count(*) FROM phones").fetchone()[0] == 4
    minimal_id = create(client, {"name": "李四"})
    minimal = client.get(f"{URL}/{minimal_id}").json["data"]
    assert {key: minimal[key] for key in ("group", "notes", "is_favorite", *CHILD_FIELDS)} == {
        "group": None, "notes": None, "is_favorite": False,
        "phones": [], "emails": [], "social_accounts": [], "addresses": [],
    }


def test_list_search_filters_and_pagination(client, contact):
    contact_id = create(client, contact)
    create(client, {"name": "另一个人", "is_favorite": True})
    expected = client.get(f"{URL}/{contact_id}").json["data"]
    for keyword in ("张", "138001", "example.com", "软件工程"):
        data = client.get(URL, query_string={"keyword": keyword}).json["data"]
        assert data == {"total": 1, "page": 1, "page_size": 10, "items": [expected]}
    data = client.get(URL, query_string={
        "group": "同学", "is_favorite": "FALSE", "keyword": "张",
    }).json["data"]
    assert data["total"] == 1
    assert client.get(URL + "?is_favorite=1").json["data"]["total"] == 1
    assert client.get(URL + "?is_favorite=0").json["data"]["total"] == 1
    assert client.get(URL + "?is_favorite=TrUe").json["data"]["total"] == 1
    page = client.get(URL + "?page=2&page_size=1").json["data"]
    assert page["total"] == 2 and page["page"] == 2 and len(page["items"]) == 1
    assert client.get(URL + "?page=3&page_size=1").json["data"]["items"] == []
    assert client.get(URL + "?page=" + "9" * 30).json["data"]["items"] == []
    assert client.get(URL, query_string={"keyword": "' OR 1=1 --"}).json["data"]["total"] == 0
    create(client, {"name": "100%_完成"})
    assert client.get(URL, query_string={"keyword": "%_"}).json["data"]["total"] == 1


@pytest.mark.parametrize("query", [
    "page=0", "page=-1", "page=x", "page=1.5", "page_size=0", "page_size=101",
    "page_size=abc", "is_favorite=yes", "is_favorite=", "page=",
])
def test_invalid_query(client, query):
    assert_error(client.get(f"{URL}?{query}"), 400, "VALIDATION_ERROR")


def test_full_update_replaces_children_and_explicitly_clears(app, client, contact):
    contact_id = create(client, contact)
    before = client.get(f"{URL}/{contact_id}").json["data"]
    replacement = {
        "name": "李四", "group": None, "notes": None, "is_favorite": True,
        "phones": [{"number": "12345"}], "emails": [], "social_accounts": [], "addresses": [],
    }
    response = client.put(f"{URL}/{contact_id}", json=replacement)
    assert response.json == {"code": 200, "message": "联系人更新成功", "data": {"id": contact_id}}
    after = client.get(f"{URL}/{contact_id}").json["data"]
    assert after["created_at"] == before["created_at"]
    assert after["updated_at"] >= before["updated_at"]
    assert after["phones"] == [{"label": "手机", "number": "12345", "is_primary": False}]
    assert after["group"] is None and after["notes"] is None
    with sqlite3.connect(app.config["DATABASE"]) as db:
        for table in ("emails", "social_accounts", "addresses"):
            assert db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0
    for field in replacement:
        missing = {key: value for key, value in replacement.items() if key != field}
        assert_error(client.put(f"{URL}/{contact_id}", json=missing), 400, "VALIDATION_ERROR")
        assert client.get(f"{URL}/{contact_id}").json["data"] == after


def test_delete_cascades_persistently(app, client, contact):
    contact_id = create(client, contact)
    response = client.delete(f"{URL}/{contact_id}")
    assert response.status_code == 200
    assert response.json == {"code": 200, "message": "联系人已删除", "data": None}
    with sqlite3.connect(app.config["DATABASE"]) as db:
        for table in ("contacts", *CHILD_FIELDS):
            assert db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0
    assert_error(client.delete(f"{URL}/{contact_id}"), 404, "NOT_FOUND")


def test_favorite_explicit_idempotent_and_persistent(app, client):
    contact_id = create(client, {"name": "张三"})
    for value in (True, True, False, False):
        response = client.patch(f"{URL}/{contact_id}/favorite", json={"is_favorite": value})
        assert response.status_code == 200
        assert response.json == {
            "code": 200, "message": "收藏状态更新成功",
            "data": {"id": contact_id, "is_favorite": value},
        }
        with sqlite3.connect(app.config["DATABASE"]) as db:
            assert db.execute("SELECT is_favorite FROM contacts").fetchone()[0] == int(value)
    for value in ("false", "true", 0, 1, None, [], {}):
        assert_error(client.patch(
            f"{URL}/{contact_id}/favorite", json={"is_favorite": value},
        ), 400, "VALIDATION_ERROR")
    assert_error(client.patch(f"{URL}/{contact_id}/favorite", json={}), 400, "VALIDATION_ERROR")
    assert client.get(f"{URL}/{contact_id}").json["data"]["is_favorite"] is False


@pytest.mark.parametrize("body", [
    {}, [], None, {"name": " "}, {"name": 123}, {"name": "x" * 51},
    {"name": "张", "notes": "x" * 501}, {"name": "张", "group": []},
    {"name": "张", "is_favorite": "false"}, {"name": "张", "phones": None},
    {"name": "张", "phones": ["123"]}, {"name": "张", "phones": [{}]},
    {"name": "张", "phones": [{"number": "abc"}]},
    {"name": "张", "phones": [{"number": "123", "is_primary": 1}]},
    {"name": "张", "emails": [{"email": "invalid"}]},
    {"name": "张", "addresses": [{"address": "x" * 201}]},
    {"name": "张", "social_accounts": [{"account": " "}]},
])
def test_invalid_contact_is_not_written(app, client, body):
    assert_error(client.post(URL, json=body), 400, "VALIDATION_ERROR")
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT count(*) FROM contacts").fetchone()[0] == 0


def test_json_errors_not_found_and_cors(client):
    for payload, content_type in (("{bad", "application/json"), ("name=x", "text/plain")):
        response = client.post(URL, data=payload, content_type=content_type)
        assert_error(response, 400, "VALIDATION_ERROR")
    for method, suffix, kwargs in (
        ("get", "/999", {}), ("delete", "/999", {}),
        ("put", "/999", {"json": {}}),
        ("patch", "/999/favorite", {"json": {"is_favorite": True}}),
    ):
        assert_error(getattr(client, method)(URL + suffix, **kwargs), 404, "NOT_FOUND")
    assert_error(client.get("/missing"), 404, "NOT_FOUND")
    assert_error(client.patch(URL), 405, "METHOD_NOT_ALLOWED")
    response = client.get(URL, headers={"Origin": "http://localhost:5173"})
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"


def test_transaction_rollback_and_safe_500(app, client, contact, caplog):
    contact_id = create(client, contact)
    before = client.get(f"{URL}/{contact_id}").json["data"]
    with app.app_context():
        db = get_db()
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        db.execute(
            "CREATE TRIGGER fail_email BEFORE INSERT ON emails "
            "BEGIN SELECT RAISE(ABORT, 'injected database failure'); END"
        )
        db.commit()
    for method, path in (("post", URL), ("put", f"{URL}/{contact_id}")):
        response = getattr(client, method)(path, json={**contact, "name": "不能留下半条记录"})
        assert_error(response, 500, "INTERNAL_SERVER_ERROR")
        assert "injected database failure" not in response.get_data(as_text=True)
        assert client.get(f"{URL}/{contact_id}").json["data"] == before
    assert "injected database failure" in caplog.text
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT count(*) FROM contacts").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM phones").fetchone()[0] == 2
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
