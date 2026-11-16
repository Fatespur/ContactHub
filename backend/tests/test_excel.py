"""Excel HTTP contracts, real workbook contents and SQLite atomicity."""

from io import BytesIO
import sqlite3
from zipfile import ZIP_STORED, ZipFile

from openpyxl import Workbook, load_workbook
import pytest

from app import create_app
from app.db import CHILD_FIELDS
from app.excel import HEADERS, MAX_FILE_SIZE, MIME_TYPE


URL = "/api/v1/contacts"


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "contacts.sqlite3")})


@pytest.fixture
def client(app):
    return app.test_client()


def workbook_bytes(rows=(), headers=HEADERS):
    workbook = Workbook()
    workbook.active.append(headers)
    for row in rows:
        workbook.active.append(row)
    output = BytesIO()
    workbook.save(output)
    workbook.close()
    return output.getvalue()


def upload(client, data, filename="contacts.xlsx"):
    return client.post(URL + "/import", data={"file": (BytesIO(data), filename)})


def assert_invalid_file(response):
    assert response.status_code == 400
    assert response.json == {
        "code": 400, "error_code": "INVALID_FILE",
        "message": "请上传有效的 Excel 文件 (.xlsx)，且文件不得超过 10MB", "details": None,
    }


def contacts(client):
    return client.get(URL + "?page_size=100").json["data"]["items"]


def test_export_all_filtered_contacts_with_download_headers(client):
    for index in range(12):
        assert client.post(URL, json={
            "name": f"匹配{index}", "group": "同学", "is_favorite": True,
            "phones": [{"number": "123"}, {"number": "1234"}],
        }).status_code == 201
    client.post(URL, json={"name": "不匹配", "group": "其他", "is_favorite": True})
    client.post(URL, json={"name": "不收藏", "group": "同学"})
    response = client.get(URL + "/export", query_string={
        "keyword": "123", "group": "同学", "is_favorite": "TrUe", "page": 2, "page_size": 1,
    })
    assert response.status_code == 200
    assert response.content_type == MIME_TYPE
    disposition = response.headers["Content-Disposition"]
    assert disposition.startswith("attachment;") and "contacts_export_" in disposition
    assert disposition.endswith(".xlsx")
    workbook = load_workbook(BytesIO(response.data))
    rows = list(workbook.active.values)
    assert rows[0] == HEADERS and len(rows) == 13
    assert rows[1][3] == "手机:123\n手机:1234" and rows[-1][0] == "匹配11"
    workbook.close()
    assert client.get(URL + "/export?is_favorite=invalid").status_code == 400
    empty = client.get(URL + "/export?keyword=not_found")
    workbook = load_workbook(BytesIO(empty.data))
    assert list(workbook.active.values) == [HEADERS]
    workbook.close()


def test_normal_roundtrip_multiple_contacts_and_repeat_import(app, client):
    body = {
        "name": "张三", "group": "同学", "is_favorite": True, "notes": "备注\n第二行",
        "phones": [
            {"label": "工作", "number": "+86(591)-123", "is_primary": False},
            {"label": "手机", "number": "001234", "is_primary": True},
        ],
        "emails": [{"label": "个人", "email": "a@example.com", "is_primary": True}],
        "social_accounts": [
            {"platform": "GitHub", "account": "https://github.com/a"},
            {"platform": "微信", "account": "abc"},
        ],
        "addresses": [
            {"label": "公司", "address": "园区;A座:三楼", "is_primary": True},
            {"label": "家庭", "address": "福州", "is_primary": False},
        ],
    }
    client.post(URL, json=body)
    client.post(URL, json={"name": "李四"})
    exported = client.get(URL + "/export").data
    for _ in range(2):
        response = upload(client, exported)
        assert response.status_code == 200
        assert response.json == {
            "code": 200, "message": "导入完成", "data": {
                "total_rows": 2, "success_count": 2, "failed_count": 0, "errors": [],
            },
        }
    stored = contacts(client)
    assert len({item["id"] for item in stored}) == 6
    for item in stored[::2]:
        assert {key: item[key] for key in body} == body
    restarted = create_app({"TESTING": True, "DATABASE": app.config["DATABASE"]})
    assert contacts(restarted.test_client()) == stored


def test_import_parsing_defaults_primary_and_partial_failures(client):
    data = workbook_bytes([
        ("张三", "同学", "TRUE", "123;工作*:456；备用*:789", "a@example.com",
         "GitHub：https://github.com/a\r\nQQ:123", "公司:园区;A座\n家庭:福州", "备注"),
        (None,) * 8,
        (None, None, None, "123", None, None, None, None),
        ("坏邮箱", None, "否", None, "invalid", None, None, None),
        ("坏电话", None, "否", "abc", None, None, None, None),
        ("坏收藏", None, "yes", None, None, None, None, None),
        ("李四", None, "0", None, None, "wx_user", None, None),
    ])
    result = upload(client, data).json["data"]
    assert {key: result[key] for key in ("total_rows", "success_count", "failed_count")} == {
        "total_rows": 6, "success_count": 2, "failed_count": 4,
    }
    assert [error["row"] for error in result["errors"]] == [4, 5, 6, 7]
    assert all(
        set(error) == {"row", "name", "reason"} and error["reason"]
        for error in result["errors"]
    )
    first, second = contacts(client)
    assert first["is_favorite"] is True and second["is_favorite"] is False
    assert first["phones"] == [
        {"label": "手机", "number": "123", "is_primary": False},
        {"label": "工作", "number": "456", "is_primary": True},
        {"label": "备用", "number": "789", "is_primary": False},
    ]
    assert first["emails"][0]["is_primary"] is True
    assert first["addresses"][0]["address"] == "园区;A座"
    assert first["social_accounts"][0]["account"] == "https://github.com/a"
    assert second["social_accounts"] == [{"platform": "其他", "account": "wx_user"}]


@pytest.mark.parametrize("favorite,expected", [("是", True), ("否", False), (1, True), (0, False),
                                               ("false", False), (None, False)])
def test_favorite_excel_values(client, favorite, expected):
    response = upload(client, workbook_bytes([("张", None, favorite)]))
    assert response.json["data"]["success_count"] == 1
    assert contacts(client)[0]["is_favorite"] is expected


@pytest.mark.parametrize("data,filename", [
    (b"", "x.xlsx"), (b"not excel", "x.xlsx"), (b"<xml/>", "x.xlsx"),
    (b"fake", "x.xls"), (b"fake", "x.csv"), (b"fake", ""),
])
def test_invalid_uploads(client, data, filename):
    assert_invalid_file(upload(client, data, filename))
    assert contacts(client) == []


def test_missing_file_headers_and_invalid_ooxml(client):
    assert_invalid_file(client.post(URL + "/import"))
    for headers in (("姓名",), HEADERS[::-1], (*HEADERS, "额外列"), ("错误", *HEADERS[1:])):
        assert_invalid_file(upload(client, workbook_bytes(headers=headers)))
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("[Content_Types].xml", "<broken")
    assert_invalid_file(upload(client, output.getvalue()))
    valid = workbook_bytes()
    output = BytesIO()
    with ZipFile(BytesIO(valid)) as source, ZipFile(output, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name == "[Content_Types].xml":
                data = data.replace(
                    b"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
                    b"application/vnd.ms-excel.sheet.macroEnabled.main+xml",
                )
            target.writestr(name, data)
    assert_invalid_file(upload(client, output.getvalue()))


def test_actual_upload_size_boundary_and_request_limit(client):
    original = workbook_bytes([("张三",)])
    # Add an ignored ZIP member of a calculated size to create a valid 10 MB workbook.
    stream = BytesIO(original)
    with ZipFile(stream, "a", compression=ZIP_STORED) as archive:
        archive.writestr("padding", b"")
    overhead = len(stream.getvalue()) - len(original)
    stream = BytesIO(original)
    with ZipFile(stream, "a", compression=ZIP_STORED) as archive:
        archive.writestr("padding", b"0" * (MAX_FILE_SIZE - len(original) - overhead))
    exact = stream.getvalue()
    assert len(exact) == MAX_FILE_SIZE
    assert upload(client, exact).json["data"]["success_count"] == 1
    assert_invalid_file(upload(client, exact + b"x"))
    assert_invalid_file(upload(client, b"x" * (MAX_FILE_SIZE + 2 * 1024 * 1024)))


def test_formula_export_is_text_and_formula_import_is_row_error(client):
    body = {
        "name": '=HYPERLINK("https://example.com","test")', "group": "+1+1",
        "notes": "=1+1", "social_accounts": [{"platform": "=1", "account": "=2"}],
    }
    client.post(URL, json=body)
    exported = client.get(URL + "/export").data
    workbook = load_workbook(BytesIO(exported), data_only=False)
    for column, value in ((1, body["name"]), (2, "+1+1"), (6, "=1:=2"), (8, "=1+1")):
        cell = workbook.active.cell(2, column)
        assert cell.value == value and cell.data_type == "s"
    workbook.close()
    assert upload(client, exported).json["data"]["success_count"] == 1
    assert contacts(client)[-1]["name"] == body["name"]
    malicious = workbook_bytes([
        ("公式行", None, None, None, None, None, None, "=1+1"),
        ("有效行",),
    ])
    result = upload(client, malicious).json["data"]
    assert result["success_count"] == 1 and result["failed_count"] == 1
    assert result["errors"][0]["row"] == 2
    assert "公式" in result["errors"][0]["reason"]


def test_database_failure_rolls_back_whole_row_without_false_success(app, client, caplog):
    with sqlite3.connect(app.config["DATABASE"]) as db:
        db.execute(
            "CREATE TRIGGER reject_email BEFORE INSERT ON emails "
            "WHEN NEW.email = 'fail@example.com' "
            "BEGIN SELECT RAISE(ABORT, 'injected excel database failure'); END"
        )
    response = upload(client, workbook_bytes([
        ("有效行", None, None, "123", "ok@example.com"),
        ("故障行", None, None, "456", "fail@example.com"),
        ("不再处理",),
    ]))
    assert response.status_code == 500
    assert response.json["error_code"] == "INTERNAL_SERVER_ERROR"
    assert "injected" not in response.get_data(as_text=True)
    assert "injected excel database failure" in caplog.text
    assert [item["name"] for item in contacts(client)] == ["有效行"]
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT number FROM phones").fetchall() == [("123",)]
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def test_documented_roundtrip_limitations_are_visible(client):
    client.post(URL, json={
        "name": "歧义数据", "phones": [{"label": "工作*", "number": "123"}],
        "emails": [{"email": "a@example.com"}, {"email": "b@example.com"}],
        "addresses": [{"label": "家庭", "address": "园区;A座"}],
        "social_accounts": [{"platform": "自:定义", "account": "abc"}],
    })
    original = contacts(client)[0]
    assert upload(client, client.get(URL + "/export").data).json["data"]["success_count"] == 1
    restored = contacts(client)[1]
    assert original["phones"][0]["label"] == "工作*"
    assert restored["phones"][0] == {"label": "工作", "number": "123", "is_primary": True}
    assert [item["is_primary"] for item in restored["emails"]] == [True, False]
    assert len(restored["addresses"]) == 2
    assert restored["social_accounts"] == [{"platform": "自", "account": "定义:abc"}]


def test_export_does_not_silently_truncate_excel_text(client):
    client.post(URL, json={"name": "长账号", "social_accounts": [{"account": "x" * 32768}]})
    response = client.get(URL + "/export")
    assert response.status_code == 400 and response.json["error_code"] == "VALIDATION_ERROR"
