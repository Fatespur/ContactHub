"""Dedicated test suite for Chinese localization, CRUD, search, Excel exchange and API compatibility."""

from io import BytesIO
import pytest
from openpyxl import load_workbook, Workbook

from app import create_app
from app.excel import HEADERS


URL = "/api/v1/contacts"


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "chinese_test.sqlite3")})


@pytest.fixture
def client(app):
    return app.test_client()


def test_chinese_crud(client):
    """Test full CRUD lifecycle for contacts with rich Chinese text and metadata."""
    payload = {
        "name": "诸葛孔明",
        "group": "蜀汉研发组",
        "is_favorite": True,
        "notes": "鞠躬尽瘁，死而后已。负责后端分布式系统架构设计。",
        "phones": [
            {"label": "工作", "number": "13912345678", "is_primary": True},
            {"label": "住宅", "number": "+86(028)-88886666", "is_primary": False},
        ],
        "emails": [
            {"label": "工作", "email": "zhuge@shuhan.org", "is_primary": True},
            {"label": "个人", "email": "kongming@wodang.cn", "is_primary": False},
        ],
        "social_accounts": [
            {"platform": "微信", "account": "zhuge_kongming"},
            {"platform": "GitHub", "account": "https://github.com/zhuge"},
        ],
        "addresses": [
            {"label": "工作", "address": "四川省成都市武侯祠大街231号", "is_primary": True},
            {"label": "住宅", "address": "湖北省襄阳市古隆中景区", "is_primary": False},
        ],
    }

    # 1. Create
    res_create = client.post(URL, json=payload)
    assert res_create.status_code == 201
    contact_id = res_create.json["data"]["id"]
    assert res_create.json["message"] == "联系人创建成功"

    # 2. Read Detail
    res_get = client.get(f"{URL}/{contact_id}")
    assert res_get.status_code == 200
    detail = res_get.json["data"]
    assert detail["name"] == "诸葛孔明"
    assert detail["group"] == "蜀汉研发组"
    assert detail["is_favorite"] is True
    assert "武侯祠大街231号" in detail["addresses"][0]["address"]
    assert detail["phones"][0]["label"] == "工作"
    assert detail["social_accounts"][0]["platform"] == "微信"

    # 3. Update
    update_payload = {
        "name": "诸葛武侯",
        "group": "战略规划部",
        "is_favorite": False,
        "notes": "隆中对核心起草人",
        "phones": [{"label": "紧急", "number": "13800000000", "is_primary": True}],
        "emails": [{"label": "工作", "email": "wuhou@shuhan.org", "is_primary": True}],
        "social_accounts": [{"platform": "微信", "account": "wuhou_2026"}],
        "addresses": [{"label": "办公", "address": "陕西省汉中市勉县定军山", "is_primary": True}],
    }
    res_update = client.put(f"{URL}/{contact_id}", json=update_payload)
    assert res_update.status_code == 200
    assert res_update.json["message"] == "联系人更新成功"

    res_updated_get = client.get(f"{URL}/{contact_id}")
    updated_data = res_updated_get.json["data"]
    assert updated_data["name"] == "诸葛武侯"
    assert updated_data["group"] == "战略规划部"
    assert updated_data["is_favorite"] is False
    assert updated_data["addresses"][0]["address"] == "陕西省汉中市勉县定军山"

    # 4. Favorite Toggle
    res_fav = client.patch(f"{URL}/{contact_id}/favorite", json={"is_favorite": True})
    assert res_fav.status_code == 200
    assert res_fav.json["data"]["is_favorite"] is True

    # 5. Delete
    res_del = client.delete(f"{URL}/{contact_id}")
    assert res_del.status_code == 200
    assert res_del.json["message"] == "联系人已删除"

    # Verify not found after delete
    res_after = client.get(f"{URL}/{contact_id}")
    assert res_after.status_code == 404


def test_chinese_search_and_filter(client):
    """Verify keyword search across Chinese name, notes, and addresses, plus group/favorite filters."""
    c1 = {
        "name": "林则徐",
        "group": "福州校友",
        "is_favorite": True,
        "notes": "苟利国家生死以，岂因祸福避趋之",
        "phones": [{"number": "13905910001"}],
        "emails": [{"email": "lin@fuzhou.edu.cn"}],
        "social_accounts": [],
        "addresses": [{"address": "福建省福州市鼓楼区澳门路19号林则徐纪念馆", "is_primary": True}],
    }
    c2 = {
        "name": "严复",
        "group": "福州校友",
        "is_favorite": False,
        "notes": "天演论翻译家，北京大学首任校长",
        "phones": [{"number": "13905910002"}],
        "emails": [{"email": "yan@pku.edu.cn"}],
        "social_accounts": [],
        "addresses": [{"address": "福建省福州市仓山区下渡街道", "is_primary": True}],
    }
    c3 = {
        "name": "鲁迅",
        "group": "文学社",
        "is_favorite": True,
        "notes": "横眉冷对千夫指，俯首甘为孺子牛",
        "phones": [{"number": "13812345678"}],
        "emails": [{"email": "luxun@shaoxing.cn"}],
        "social_accounts": [],
        "addresses": [{"address": "浙江省绍兴市越城区鲁迅中路241号", "is_primary": True}],
    }

    client.post(URL, json=c1)
    client.post(URL, json=c2)
    client.post(URL, json=c3)

    # 1. Search by Chinese Name
    res = client.get(URL, query_string={"keyword": "则徐"}).json["data"]
    assert res["total"] == 1
    assert res["items"][0]["name"] == "林则徐"

    # 2. Search by Chinese Notes
    res = client.get(URL, query_string={"keyword": "天演论"}).json["data"]
    assert res["total"] == 1
    assert res["items"][0]["name"] == "严复"

    # 3. Search by Chinese Address
    res = client.get(URL, query_string={"keyword": "澳门路"}).json["data"]
    assert res["total"] == 1
    assert res["items"][0]["name"] == "林则徐"

    res_campus = client.get(URL, query_string={"keyword": "越城区"}).json["data"]
    assert res_campus["total"] == 1
    assert res_campus["items"][0]["name"] == "鲁迅"

    # 4. Group filter
    res_group = client.get(URL, query_string={"group": "福州校友"}).json["data"]
    assert res_group["total"] == 2

    # 5. Composite filter: group + favorite + keyword
    res_combo = client.get(
        URL, query_string={"group": "福州校友", "is_favorite": "true", "keyword": "纪念馆"}
    ).json["data"]
    assert res_combo["total"] == 1
    assert res_combo["items"][0]["name"] == "林则徐"


def test_chinese_excel_export_and_import(client):
    """Verify Excel export and import consistency for Chinese text and multi-valued fields."""
    contact_body = {
        "name": "沈括",
        "group": "宋代学者",
        "is_favorite": True,
        "notes": "梦溪笔谈作者，涉及天文、地学、数学等领域",
        "phones": [
            {"label": "手机", "number": "13600001234", "is_primary": True},
            {"label": "书房", "number": "+86(0571)-87654321", "is_primary": False},
        ],
        "emails": [{"label": "工作", "email": "shenkuo@song.ac.cn", "is_primary": True}],
        "social_accounts": [{"platform": "知乎", "account": "shenkuo_official"}],
        "addresses": [{"label": "寓所", "address": "江苏省镇江市梦溪园巷21号", "is_primary": True}],
    }
    client.post(URL, json=contact_body)

    # 1. Export Excel
    export_res = client.get(f"{URL}/export")
    assert export_res.status_code == 200
    assert export_res.headers["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    wb = load_workbook(BytesIO(export_res.data))
    sheet = wb.active
    assert sheet.title == "联系人"
    headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
    assert tuple(headers) == HEADERS

    rows = list(sheet.iter_rows(min_row=2, values_only=True))
    assert len(rows) == 1
    row = rows[0]
    assert row[0] == "沈括"
    assert row[1] == "宋代学者"
    assert row[2] == "是"
    assert "手机*:13600001234" in row[3]
    assert "书房:+86(0571)-87654321" in row[3]
    assert "工作*:shenkuo@song.ac.cn" in row[4]
    assert "知乎:shenkuo_official" in row[5]
    assert "寓所*:江苏省镇江市梦溪园巷21号" in row[6]
    assert "梦溪笔谈" in row[7]
    wb.close()

    # 2. Import Excel with new Chinese contacts
    new_wb = Workbook()
    new_sheet = new_wb.active
    new_sheet.append(HEADERS)
    new_sheet.append([
        "苏轼", "东坡居士", "是",
        "手机*:13500009999\n家乡:0571-88889999",
        "词人*:sushi@song.gov.cn",
        "诗词社:dongpo",
        "常居*:海南省儋州市东坡书院",
        "一蓑烟雨任平生",
    ])
    new_sheet.append([
        "李清照", "婉约派", "否",
        "手机*:13711112222",
        "个人*:qingzhao@song.gov.cn",
        "词轩:yian",
        "故里*:山东省济南市章丘区明水街道",
        "如梦令、声声慢",
    ])
    upload_buf = BytesIO()
    new_wb.save(upload_buf)
    new_wb.close()

    import_res = client.post(
        f"{URL}/import",
        data={"file": (BytesIO(upload_buf.getvalue()), "chinese_contacts.xlsx")},
    )
    assert import_res.status_code == 200
    stats = import_res.json["data"]
    assert stats["total_rows"] == 2
    assert stats["success_count"] == 2
    assert stats["failed_count"] == 0

    # Verify query for newly imported contacts
    res_sushi = client.get(URL, query_string={"keyword": "东坡书院"}).json["data"]
    assert res_sushi["total"] == 1
    assert res_sushi["items"][0]["name"] == "苏轼"
    assert res_sushi["items"][0]["is_favorite"] is True

    res_lqz = client.get(URL, query_string={"keyword": "声声慢"}).json["data"]
    assert res_lqz["total"] == 1
    assert res_lqz["items"][0]["name"] == "李清照"


def test_api_backward_compatibility(client):
    """Ensure all JSON responses, keys, and status codes adhere strictly to API.md contract."""
    # List endpoint schema
    res_list = client.get(URL)
    assert res_list.status_code == 200
    assert set(res_list.json.keys()) == {"code", "message", "data"}
    assert set(res_list.json["data"].keys()) == {"page", "page_size", "total", "items"}

    # Create and inspect full fields
    body = {
        "name": "兼容性测试员",
        "group": "QA",
        "is_favorite": False,
        "notes": "保证所有原字段键名不改动",
        "phones": [{"number": "13000000000"}],
        "emails": [{"email": "qa@example.com"}],
        "social_accounts": [{"platform": "微信", "account": "qa_wx"}],
        "addresses": [{"address": "测试实验室1号"}],
    }
    res_create = client.post(URL, json=body)
    cid = res_create.json["data"]["id"]

    res_item = client.get(f"{URL}/{cid}")
    contact = res_item.json["data"]
    expected_keys = {
        "id", "name", "group", "is_favorite", "notes", "created_at", "updated_at",
        "phones", "emails", "social_accounts", "addresses"
    }
    assert set(contact.keys()) == expected_keys

    # Sub-item schemas
    assert set(contact["phones"][0].keys()) == {"label", "number", "is_primary"}
    assert set(contact["emails"][0].keys()) == {"label", "email", "is_primary"}
    assert set(contact["social_accounts"][0].keys()) == {"platform", "account"}
    assert set(contact["addresses"][0].keys()) == {"label", "address", "is_primary"}

    # Standard error schema
    res_err = client.get(f"{URL}/99999999")
    assert res_err.status_code == 404
    assert set(res_err.json.keys()) == {"code", "error_code", "message", "details"}
    assert res_err.json["error_code"] == "NOT_FOUND"


def test_exception_handling_and_security(client):
    """Test validation boundaries, security escapes, and transaction rollbacks."""
    # 1. Overlong Chinese name (> 50 chars)
    long_name = "这是一个超级长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长的中文名字"
    assert len(long_name) > 50
    res = client.post(URL, json={"name": long_name})
    assert res.status_code == 400
    assert "name" in res.json["details"]

    # 2. Overlong Chinese notes (> 500 chars)
    res_notes = client.post(URL, json={"name": "测试员", "notes": "测试" * 260})
    assert res_notes.status_code == 400
    assert "notes" in res_notes.json["details"]

    # 3. Overlong Chinese address (> 200 chars)
    res_addr = client.post(URL, json={
        "name": "测试员",
        "addresses": [{"address": "长地址" * 80}]
    })
    assert res_addr.status_code == 400
    assert "addresses" in res_addr.json["details"]

    # 4. SQL Injection in search keyword
    malicious = "' OR '1'='1' -- 注入测试"
    search_res = client.get(URL, query_string={"keyword": malicious})
    assert search_res.status_code == 200
    assert search_res.json["data"]["total"] == 0

    # 5. Non-xlsx file upload rejection
    fake_file = client.post(
        f"{URL}/import",
        data={"file": (BytesIO(b"not an excel file"), "test.txt")},
    )
    assert fake_file.status_code == 400
    assert fake_file.json["error_code"] == "INVALID_FILE"
