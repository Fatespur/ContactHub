# ContactHub 后端服务 (Flask RESTful API)

本模块为 **ContactHub（联系人管理与数据交换系统）** 的核心后端服务，基于 Python Flask、原生 `sqlite3`、Flask-CORS 与 openpyxl 构建。提供联系人全生命周期管理（CRUD）、多字段智能检索、多维联系方式维护、分页统计、快捷收藏置顶以及标准化 Excel（`.xlsx`）双向数据交换能力。

---

## 1. 快速开始

在 `backend/` 目录下操作（要求 Python 3.10+）：

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python run.py

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python run.py
```

服务将监听在 `http://127.0.0.1:5000`，API 前缀为 `/api/v1`。数据库表结构在首次启动时自动初始化，并存储于 `backend/instance/address_book.sqlite3`，支持跨重启持久化。本地开发默认允许来自 `http://localhost:5173` 的跨域请求。

---

## 2. 生产部署指南

部署到 Linux 主机或容器平台时：

- 服务根目录设为 `backend`。
- 构建命令：`pip install -r requirements.txt`。
- 启动命令：`gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 4 --threads 2`。

### 核心环境变量

| 变量名 | 说明 | 示例 |
| --- | --- | --- |
| `DATABASE` | SQLite 数据库文件绝对或相对路径 | `/var/data/contacthub.sqlite3` |
| `CORS_ORIGINS` | 允许跨域的前端 Origin（逗号分隔或 `*`） | `https://contacthub.example.com` |

---

## 3. 执行自动化测试

测试套件运行于隔离的临时 SQLite 数据库，完全不污染本地业务数据：

```bash
python -m pytest
```

已针对 Windows 环境在 `pytest.ini` 中配置了本地临时目录，规避了中文用户名或系统目录的临时权限限制。

测试包含：
- `tests/test_api.py`：基础 API 与 CRUD 契约。
- `tests/test_chinese_features.py`：中文全流程 CRUD、多字段检索（姓名/备注/地址）、Excel 中文编解码一致性、接口兼容性及安全防注入。
- `tests/test_deployment.py`：生产部署环境与 WSGI 启动入口校验。
- `tests/test_excel.py`：Excel 边界、公式注入安全拦截与事务原子性校验。

---

## 4. 接口契约与校验规则

- **全量更新契约 (`PUT /api/v1/contacts/{id}`)**：必须提供全部 8 个可编辑字段（`name`, `group`, `is_favorite`, `notes`, `phones`, `emails`, `social_accounts`, `addresses`）。缺失任何字段将返回 `400 VALIDATION_ERROR` 并不做任何写操作；如需清空字段请显式传 `null` 或 `[]`。
- **电话号码规则**：严格符合正则 `^[0-9+()\-]+$`，不允许包含未转义空格。
- **中文与字符集**：完整支持 UTF-8 编码的中文汉字、少数民族文字、标点符号，严格校验姓名（1–50 字）、备注（<= 500 字）、地址（<= 200 字）。

---

## 5. Excel 导入导出规范

- **导出 (`GET /api/v1/contacts/export`)**：按照查询参数（`keyword`, `group`, `is_favorite`）过滤联系人，忽略分页，流式返回标准 `.xlsx` 文件。
- **导入 (`POST /api/v1/contacts/import`)**：通过 `file` 字段接收不超过 10MB 的 `.xlsx` 文件。严格校验表头 8 列；逐行独立事务导入，跳过空行，汇总失败清单。
- **公式注入防护**：导出时将文本单元格显式声明为字符串类型；导入时若发现实际公式单元格即行级拦截，杜绝恶意公式执行。
