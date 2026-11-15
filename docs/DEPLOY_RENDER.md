# 部署到 Render（前后端完整流程）

本文档面向本项目（Flask + SQLite 后端、Vue 3 + Vite 前端）在 [Render](https://render.com) 上的完整部署，
包含本地验证结论、两种部署方式（Dashboard 手动 / Blueprint 一键）、数据持久化取舍和排错清单。

- 仓库：<https://github.com/JiahuiYe-FZU/EE308FZ-AddressBook>
- 后端源码在 `backend/` 分支，前端源码目前只在本地工作区（`frontend/`），**部署前必须先把整个项目推到 GitHub**，见第 1 节。

---

## 0. 本地验证结论（部署前已跑通）

| 验证项 | 命令 | 结果 |
| --- | --- | --- |
| 后端单元 / 接口测试 | `python -m pytest tests -q` | **55 passed** |
| 后端真实服务冒烟（26 项：CORS、CRUD、分页、搜索、收藏、字段校验、404/405、Excel 导入导出） | 启动 `run.py` 后逐条请求 | **全部通过** |
| 生产 WSGI 入口 `wsgi:app`（用 waitress 模拟 gunicorn 的 `0.0.0.0:$PORT` 绑定） | `serve(wsgi.app, host='0.0.0.0', port=... )` | **200 / 201，CORS 头正确** |
| 前端生产构建 | `npm run build` | **成功**，产物 `frontend/dist/` |
| 前端开发代理 | `npm run dev` + `GET /api/v1/contacts` | **200，代理正常** |
| 前端构建产物 + 真实后端（跨域） | 静态托管 `dist/`，浏览器访问 | **列表、详情、分组计数均来自真实数据库** |

前端连真实后端的实拍（数据来自 SQLite，而不是 Mock 的 20 条演示数据）：

![本地联调：构建产物 + 真实后端](preview/local-run-real-api.png)

---

## 1. 先把代码推到 GitHub（必须做）

当前远程仓库的三个分支里，`main` / `frontend` 只有 `README.md`，`backend` 分支只有后端代码。
如果直接连仓库部署，前端会因为找不到 `frontend/package.json` 而构建失败。请在本机项目根目录执行：

```bash
cd <项目根目录>            # 包含 backend/ frontend/ render.yaml 的目录
git init                                  # 若还不是 git 仓库
git add .
git commit -m "feat: backend + frontend + render deployment config"
git branch -M main
git remote add origin https://github.com/JiahuiYe-FZU/EE308FZ-AddressBook.git
git push -u origin main --force           # 覆盖远端 main；如不想覆盖，请推到新分支或新仓库
```

推送后到 GitHub 上确认这几项存在（否则部署一定失败）：

- [ ] `backend/requirements.txt`、`backend/wsgi.py`、`backend/app/`、`backend/app/schema.sql`
- [ ] `frontend/package.json`、`frontend/package-lock.json`、`frontend/vite.config.js`、`frontend/src/`
- [ ] `frontend/public/templates/contacts-import-template.xlsx`（导入模板，**`.gitignore` 曾用 `*.xlsx` 把整个文件忽略掉**，本仓库已加白名单，务必在 GitHub 页面上确认能看到这个文件）
- [ ] 根目录 `render.yaml`（用方式 B 时需要）

> 本地依赖目录 `backend/.venv/`、`frontend/node_modules/`、`frontend/dist/`、`backend/instance/` 都已在 `.gitignore` 中，不需要也不应该提交。

---

## 2. 部署架构

```
浏览器
  │  https://addressbook-web.onrender.com        （Static Site，CDN，免费）
  │      └─ axios baseURL = https://addressbook-api.onrender.com/api/v1
  ▼
https://addressbook-api.onrender.com             （Web Service，Python + gunicorn，免费实例）
  │      └─ Flask app（/api/v1/...），Flask-CORS 按 CORS_ORIGINS 放行前端域名
  ▼
SQLite 文件 backend/instance/address_book.sqlite3（临时文件系统；挂 Disk 才持久）
```

两个服务域名不同，所以做了两处适配（已在代码里，无需你改代码）：

1. 后端 `CORS_ORIGINS` 环境变量决定允许哪些前端来源；
2. 前端 `VITE_API_BASE_URL` 构建时注入后端绝对地址（不设置则退回同源 `/api/v1`，本地 Vite 代理用的就是它）。

---

## 3. 方式 A：Dashboard 手动部署（推荐，步骤最直观）

### 3.1 创建后端 Web Service

Render Dashboard → **New +** → **Web Service** → 选择 `EE308FZ-AddressBook` 仓库。

| 表单项 | 填写值 |
| --- | --- |
| Name | `addressbook-api` |
| Language / Runtime | `Python 3` |
| Region | `Singapore`（国内访问更快） |
| Branch | `main` |
| **Root Directory** | `backend` ← 关键，否则找不到 `requirements.txt` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn -b 0.0.0.0:$PORT --workers 1 --threads 4 wsgi:app` |
| Instance Type | `Free` |
| Health Check Path（Advanced） | `/api/v1/contacts` |

**Environment Variables** 里加：

| Key | Value |
| --- | --- |
| `PYTHON_VERSION` | `3.13.4` |
| `CORS_ORIGINS` | 先填 `*`（临时放行），3.3 步再收紧为前端域名 |

点 **Create Web Service**，等待日志出现 `Booting worker` / `Listening at: http://0.0.0.0:10000`，状态变 **Live**（首次构建约 2–5 分钟）。

验证（把域名换成你自己的）：

```bash
curl https://addressbook-api.onrender.com/api/v1/contacts
# {"code":200,"data":{"items":[],"page":1,"page_size":10,"total":0},"message":"success"}
```

> 免费实例 15 分钟无请求会休眠，第一次访问可能等 30–60 秒才返回；这是正常现象，不是 502 故障。

### 3.2 创建前端 Static Site

Dashboard → **New +** → **Static Site** → 同一个仓库。

| 表单项 | 填写值 |
| --- | --- |
| Name | `addressbook-web` |
| Branch | `main` |
| **Root Directory** | `frontend` ← 关键 |
| Build Command | `npm install && npm run build` |
| **Publish Directory** | `dist` |

**Environment Variables**：

| Key | Value |
| --- | --- |
| `NODE_VERSION` | `22.12.0`（Vite 7 要求 Node ≥ 20.19 / 22.12） |
| `VITE_USE_MOCK` | `false`（否则页面用的是前端假数据） |
| `VITE_API_BASE_URL` | `https://addressbook-api.onrender.com/api/v1`（换成 3.1 步的实际地址，**末尾不要加斜杠**） |

**Redirects/Rewrites**（Settings 里，或在创建页的 Advanced 区域）新增一条，否则刷新 `/settings` 会 404：

| Source | Destination | Action |
| --- | --- | --- |
| `/*` | `/index.html` | `Rewrite` |

> `VITE_*` 是**构建期**变量：改动后必须 **Manual Deploy → Clear build cache & deploy**，仅重启不会生效。

### 3.3 回填后端 CORS 并重新部署

把后端 `CORS_ORIGINS` 从 `*` 改成前端实际域名（多个用英文逗号分隔，不要带末尾 `/`）：

```
https://addressbook-web.onrender.com
```

保存后 Render 会自动重新部署；没有自动触发就点 **Manual Deploy → Deploy latest commit**。

> 如果前端域名被占用、Render 生成了带后缀的名字（如 `addressbook-web-a1b2`），必须用真实地址回填，否则浏览器报 CORS 错误。
> 也可以继续用 `*`：本项目没有登录态与 Cookie，风险可控，但不建议作为最终交付配置。

### 3.4 打开前端验证

访问 `https://addressbook-web.onrender.com`，按第 5 节清单验收。

---

## 4. 方式 B：用 `render.yaml` 一键创建（Blueprint）

仓库根目录已提供 `render.yaml`（两个服务 + 全部命令与环境变量）。操作：

1. Dashboard → **New +** → **Blueprint** → 选择仓库（分支 `main`）；
2. Render 解析出 `addressbook-api`、`addressbook-web`；
3. 创建时会提示填写 `VITE_API_BASE_URL`（`sync: false`），可先留空，等后端域名确定后再补；
4. **Apply** 等待两个服务都 Live，然后到前端服务的 Environment 补 `VITE_API_BASE_URL` 并重新部署。

蓝图里 `CORS_ORIGINS` 默认是 `*`，请按 3.3 改成前端域名。

本地也能先校验语法（需安装 [Render CLI](https://render.com/docs/cli)）：

```bash
render blueprints validate render.yaml
```

---

## 5. 部署后验收清单

- [ ] `GET https://addressbook-api.onrender.com/api/v1/contacts` 返回 JSON（不是 502 / 404）
- [ ] 打开前端首页，列表**为空**或显示你导入过的真实数据；如果出现 20 条“张三/李四…”演示数据，说明 `VITE_USE_MOCK` 没生效
- [ ] 新增联系人 → 列表出现 → 刷新页面仍在（同一实例内）
- [ ] 编辑、删除、收藏（PATCH）正常，错误提示为中文
- [ ] 搜索、分组筛选、分页（10/20/50）正常
- [ ] 导出 Excel：下载 `.xlsx`，可被 Excel/WPS 打开
- [ ] 导入 Excel：先下载模板 → 填 2 行 → 上传，返回「成功 2 / 失败 0」
- [ ] 浏览器 DevTools → Network：`contacts` 请求的域名是后端域名，Response Headers 含 `access-control-allow-origin`
- [ ] 直接访问 `https://addressbook-web.onrender.com/settings` 不 404（SPA rewrite 生效）

---

## 6. 数据持久化：免费 vs 付费（务必先读）

| | 免费实例（默认） | 付费 + 持久磁盘 |
| --- | --- | --- |
| 数据存放 | 容器临时文件系统 `backend/instance/address_book.sqlite3` | 磁盘挂载点 `/var/data/address_book.sqlite3` |
| 重新部署 / 重启后 | **数据清空** | 保留 |
| 休眠 | 15 分钟无请求休眠，首次访问冷启动 30–60 秒 | Starter 不休眠 |
| 费用 | 0（750 实例小时/月） | Starter ≈ $7/月 + 磁盘 $0.25/GB/月 |
| 其他限制 | — | 单实例、不能横向扩容、部署期间短暂中断、构建阶段访问不到磁盘 |

**课程演示 / 一次性验收**：免费方案够用，验收前重新导入 Excel 即可。

**需要数据不丢**：按下面步骤挂磁盘（必须先把实例类型从 Free 改成付费）：

1. 后端服务 → **Settings → Instance Type** → 改成 `Starter`；
2. **Disks → Add Disk**：Name `addressbook-data`，Mount Path `/var/data`，Size `1 GB`；
3. **Environment** 新增 `DATABASE=/var/data/address_book.sqlite3`；
4. **Manual Deploy** 重新部署，验收「新增 → 再部署 → 数据还在」。

> 也可以把 `render.yaml` 里后端 `plan` 改成 `starter`，取消 `disk` 与 `DATABASE` 两段注释，效果一样。
> 生产环境更推荐 PostgreSQL，但本项目 `backend/app/db.py` 是原生 `sqlite3` + `?` 占位符，迁移需要改代码，本次未做。

---

## 7. 排错速查

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 部署日志 `Failed to bind to $PORT` / `Invalid value for '--bind'` | 启动命令没监听 `0.0.0.0` 或没用 `$PORT` | 用本文的命令；不要写死 `127.0.0.1:5000`（那是 `run.py` 的本地调试端口） |
| `Exited with status 1`，日志 `ModuleNotFoundError: No module named 'app'` | Root Directory 不是 `backend`，或启动命令不是 `wsgi:app` | 改 Root Directory，Start Command 用 `gunicorn ... wsgi:app` |
| 首次访问很慢 / 502 后重试就好 | 免费实例休眠冷启动 | 正常；需要常驻就升级 Starter |
| 浏览器控制台 `blocked by CORS policy` | `CORS_ORIGINS` 不含前端域名（协议/端口/末尾斜杠不一致） | 精确填写 `https://xxx.onrender.com`，保存后重新部署 |
| 页面显示 20 条演示联系人 | `VITE_USE_MOCK` 不是 `false`，或改完没重新构建 | 设置 `VITE_USE_MOCK=false` → Clear build cache & deploy |
| 页面提示「请求失败（404）」 | 没设 `VITE_API_BASE_URL`，请求打到静态站点自己身上 | 填后端地址 + `/api/v1`，重新构建 |
| 刷新 `/settings` 404 | 缺少 SPA rewrite | 加 `/* → /index.html`（Rewrite） |
| 导入模板下载 404 | `dist/templates/*.xlsx` 没进构建产物（`*.xlsx` 被 gitignore） | 确认 `frontend/public/templates/contacts-import-template.xlsx` 已在 GitHub 上 |
| 导入返回 `400 INVALID_FILE` | 表头不是固定 8 列，或不是 `.xlsx` / 超过 10MB | 用仓库自带模板，第一张表表头必须完全一致 |
| 部署后数据全没了 | 免费实例临时磁盘 | 见第 6 节 |
| 日志里 `sqlite3.OperationalError: unable to open database file` | `DATABASE` 指向未挂载的路径（如 `/var/data/...` 但没加磁盘） | 先加 Disk，或删掉 `DATABASE` 用默认路径 |

---

## 8. 为部署所做的代码改动（相对原始代码）

| 文件 | 改动 | 原因 |
| --- | --- | --- |
| `backend/wsgi.py` | 新增，暴露 `app = create_app()` | gunicorn 的生产入口 |
| `backend/app/__init__.py` | `DATABASE` 支持环境变量；`CORS_ORIGINS` 支持环境变量（逗号分隔）；自动创建数据库父目录 | 本地/云端同一套代码；允许跨域访问 |
| `backend/requirements.txt` | 增加 `gunicorn`（仅非 Windows 安装） | Render 用 gunicorn；Windows 本地开发仍用 `run.py` |
| `frontend/src/api/request.js` | `baseURL = VITE_API_BASE_URL \|\| '/api/v1'` | 前后端不同域名时指向后端 |
| `frontend/src/api/contacts.js` | 未显式设置 `VITE_USE_MOCK` 时，生产构建默认走真实后端 | 避免部署后仍在用 Mock 数据 |
| `frontend/.env.example` | 补充 `VITE_API_BASE_URL` 说明 | 本地联调说明 |
| `.gitignore` | 放行 `frontend/public/templates/*.xlsx`、`docs/acceptance/*.xlsx` | 原来 `*.xlsx` 会把导入模板一起忽略 |
| `render.yaml` | 新增 | Blueprint 一键部署 |
| `docs/DEPLOY_RENDER.md` | 新增（本文） | 部署说明 |

本地开发方式不变：后端 `python run.py`（`127.0.0.1:5000`），前端 `npm run dev`（`5173`，`/api` 代理到后端，
默认 Mock，`frontend/.env.local` 里设 `VITE_USE_MOCK=false` 即连真实后端）。
