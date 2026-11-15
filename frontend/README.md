# AddressBook 前端（Vue 3 + Element Plus）

按 [`docs/UI_DESIGN.md`](../docs/UI_DESIGN.md)、[`docs/UI_DESIGN_PHASE2.md`](../docs/UI_DESIGN_PHASE2.md) 实现。

验收方法见 [`docs/ACCEPTANCE.md`](../docs/ACCEPTANCE.md)（含 10 分钟冒烟清单、分模块步骤与验收数据）。

效果截图：

- 列表 + 详情：`docs/preview/app-1280x960.png`
- 新增联系人弹窗：`docs/preview/app-dialog-create.png`
- 我的收藏筛选：`docs/preview/app-favorites.png`
- 导入结果：`docs/preview/app-import-result.png`
- 1024 详情抽屉：`docs/preview/app-1024-drawer.png`
- 768 图标侧栏 + 精简表格：`docs/preview/app-768.png`、`app-768-drawer.png`
- 首屏骨架：`docs/preview/app-skeleton.png`
- 脏检查 / 字段错误：`docs/preview/app-dirty-check.png`、`app-field-errors.png`
- 系统设置：`docs/preview/app-settings.png`

## 运行

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build    # 产物在 dist/
```

> 需要 Node.js 20.19+ / 22.12+（Vite 7 要求）。

## 数据来源

默认开发环境使用 **Mock 数据**（`src/mock/contacts.js`，20 条与参考图一致的演示数据），
接口行为与 [API.md](../API.md) 保持一致（分页、检索、筛选、全量更新、200/404 等）。
生产构建（`npm run build`）在未显式设置 `VITE_USE_MOCK` 时默认走真实后端，避免部署后误用假数据。

切到真实后端：

```bash
# frontend/.env.local
VITE_USE_MOCK=false
```

开发时前端请求统一发往 `/api/v1`，由 `vite.config.js` 代理到 `http://127.0.0.1:5000`。

前后端分开部署（例如 Render Static Site + Render Web Service）时，用构建期变量指定后端地址，
后端再用 `CORS_ORIGINS` 放行本站域名：

```bash
# frontend/.env.production.local
VITE_API_BASE_URL=https://addressbook-api.onrender.com/api/v1
```

完整部署流程见 [`docs/DEPLOY_RENDER.md`](../docs/DEPLOY_RENDER.md)。

## 已实现

- 三栏布局：顶栏 / 侧边导航（分组计数、筛选）/ 列表卡片 / 详情面板
- 列表：搜索（300ms 防抖）、分组筛选、仅显示收藏、分页（10/20/50）、当前页姓名排序
- 详情：头像、收藏星标、基本信息、多电话 / 邮箱 / 社交账号 / 地址
- 新增 / 编辑：四类联系方式动态行、可搜索可创建的标签、主联系方式互斥
- 删除（含二次确认）、批量删除（逐条 DELETE）、收藏切换（乐观更新 + 失败回滚）
- Excel 导入：拖拽 / 选择文件、10MB 与 `.xlsx` 校验、上传进度、取消、结果统计与失败明细 CSV、模板下载
- Excel 导出：按当前筛选直接下载、空结果禁用、`Content-Disposition` 文件名解析
- 响应式：≥1280 三栏常驻详情；1024–1279 详情改为右侧浮层抽屉；768–1023 图标侧栏 + 精简 5 列表格 + 更多菜单
- 首屏骨架（列表 / 详情）、翻页筛选不闪骨架
- 表单脏检查；后端 `details` 字段级错误映射（姓名 / 分区 / 第 N 项高亮，支持分区内多条同时展示）
- 快捷键：`Ctrl / ⌘ K` 搜索、`Esc` 关闭弹层、行 `Enter` 打开详情；行与抽屉的 `aria-*`、焦点循环，抽屉关闭后焦点回到选中行
- 空态 / 加载态 / 错误重试 / 统一错误提示
- `系统设置`：数据源、模板下载、快捷键、关于

## 导入 / 导出

- 导入模板：`public/templates/contacts-import-template.xlsx`（8 列 + 「填写说明」工作表），构建后由 `/templates/contacts-import-template.xlsx` 提供。
- Mock 模式：导入会模拟 10 行（8 成功 / 2 失败）并向内存追加 8 条演示联系人，刷新页面恢复；导出生成 CSV 演示文件（文件名带 `_mock`）。
- 真实模式：走 `POST /contacts/import`（multipart，60s 超时）与 `GET /contacts/export`（blob），出错时读取 blob 内的 JSON 错误体。
- 导入完成后：刷新列表与分组统计；无筛选时跳到最后一页并选中最后一条新增记录。

## 已知限制

- Mock 导出只覆盖前 100 条（契约 `page_size` 上限）；真实导出不受此限制。
- Mock 导入不解析真实 `.xlsx` 内容，仅用于验收交互；真实解析由后端负责。
- 分组计数通过一次 `page_size=100` 的全量查询聚合；超过 100 条时计数不完整，需要后端提供分组接口。
- 姓名排序为 Element Plus 表头内置排序，仅作用于当前页（契约暂无排序参数）。
- 375px 手机端尚未适配；小于 768px 时页面按 768 最小宽度横向滚动。