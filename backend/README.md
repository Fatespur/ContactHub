# Backend - EE308FZ-AddressBook

使用 Flask、原生 sqlite3、Flask-CORS 和 openpyxl，实现联系人 CRUD、分页搜索、分组筛选、收藏及 Excel 导入导出。

在 `backend/` 目录下运行（Python 3.10+）：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python run.py
```

服务地址为 `http://127.0.0.1:5000`，API 前缀为 `/api/v1`。首次启动自动建表，数据存储于 `backend/instance/address_book.sqlite3`，重启保留数据。前端继续使用 Vite Proxy；CORS 允许 `http://localhost:5173`。

Vite Proxy 将 `/api` 请求转发至 `http://127.0.0.1:5000`，保留原路径；前端使用 `/api/v1/...` 相对地址。配置示例见 [API 文档第一节](../docs/API.md)。

运行测试（使用独立的真实 SQLite 文件，不写入运行数据库）：

```powershell
New-Item -ItemType Directory -Path instance -Force | Out-Null
$testTemp = 'instance/pytest-' + [guid]::NewGuid().ToString('N')
.\.venv\Scripts\python -m pytest tests -q --basetemp=$testTemp
```

指定项目内临时目录可避开 Windows 系统临时目录权限问题。

PUT 必须包含全部 8 个可编辑字段，缺少任一字段返回 `400` 且不写入；显式提交 `[]` 或 `null` 清空对应字段。具体字段、默认值及响应结构见 [API 契约](../docs/API.md)。

Excel 接口：

- `GET /api/v1/contacts/export`：按 `keyword`、`group`、`is_favorite` 筛选全部联系人，忽略分页；返回 `.xlsx` 二进制下载。
- `POST /api/v1/contacts/import`：以 multipart 字段 `file` 上传不超过 10 MB 的 `.xlsx`，第一张工作表须包含契约规定的固定八列表头。全空行跳过，错误行计入统计，重复导入新增记录。
- 每行联系人及子项在一个事务中写入。数据库内部故障返回 500，当前行回滚并停止；此前已成功的行保留。文件格式及大小错误返回 `400 INVALID_FILE`。
- 导出公式样式的文本仍写为字符串；导入实际公式单元格时拒绝该行，不执行或读取公式缓存值。

Excel 往返限制（沿用现有契约，不增加转义或隐藏字段）：

- 标准数据、多联系方式、收藏及每类恰好一个主标记可保留；新 ID 和时间戳重新生成。
- 同类主标记全为 false 时，导入会将首项设为 true；多个 true 时只保留首个。
- 单元格无换行时，分号会拆项，例如单个地址 `园区;A座` 会变成两个地址；有多项换行时，项内分号保留。
- 项内换行会被拆项，标签或平台中的冒号会被当作分界，标签末尾的 `*` 会被当作主标记。值内冒号（如已带平台标签的 HTTPS 链接）保留。
- 空字符串与 null 在空单元格中无法区分。超过 Excel 单元格 32767 字符或包含 XML 禁用控制字符的文本导出返回 400，避免静默截断。

因此当前格式不能承诺任意合法 API 数据无损往返；需要消除这些歧义时，须先协商更新契约。
