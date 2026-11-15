# EE308FZ-AddressBook

福州大学 EE308FZ 课程双人软件工程作业 —— 前后端分离的通讯录 Web 应用程序。

> [!NOTE]
> 当前阶段为项目基础框架搭建与规范确立阶段，尚未进行业务功能开发。本项目目前为独立仓库，后续待获取教师原始仓库地址后将迁移至正式 Fork 流程，当前独立仓库并不等同于满足正式 Fork 要求。

---

## 1. 项目用途

本项目旨在设计并实现一个现代化、易用、高效的前后端分离通讯录管理系统。系统主要提供联系人信息的增删改查（CRUD）、收藏标记、分类检索以及基于 Excel 的批量数据导入与导出功能。

---

## 2. 技术方案（暂定）

- **前端框架**：Vue 3 + Vite
- **UI 组件库**：Element Plus
- **后端框架**：Python Flask
- **数据库**：SQLite
- **Excel 处理**：openpyxl
- **通信协议**：RESTful API + JSON

---

## 3. 团队协作方式

本项目由双人协作开发，采用规范化 Git 工作流：

1. **分支策略**：
   - `main`：稳定主分支，仅保留通过验证的稳定版本，禁止直接向 `main` 推送未经测试的代码。
   - `frontend`：前端主要开发分支。
   - `backend`：后端主要开发分支。
   - 特性分支：按需由对应分支切出 `feat/<feature-name>` 或 `fix/<bug-name>` 进行开发。
2. **代码审查与合并**：
   - 功能开发完成后，通过 Pull Request（PR）发起合并申请。
   - 必须经过结对成员评审并确认通过后方可合并。
3. **规范遵从**：
   - 提交信息必须严格遵循 Conventional Commits 规范。
   - 开发前请先阅读 [代码规范文档](docs/CODING_STANDARDS.md) 与 [API 设计草案](docs/API.md)。

---

## 4. 目录结构

```text
EE308FZ-AddressBook/
├── frontend/               # 前端项目目录（Vue 3 + Vite + Element Plus）
├── backend/                # 后端项目目录（Python Flask + SQLite + openpyxl）
├── docs/                   # 项目文档目录
│   ├── CODING_STANDARDS.md # 代码风格、命名、Commit 及 PR 规范
│   └── API.md              # RESTful API 接口定义草案（尚未实现）
├── .gitignore              # Git 忽略配置
└── README.md               # 项目主说明文档
```

---

## 5. 项目状态

- [x] 项目基础仓库与目录结构搭建
- [x] 代码规范与 API 接口草案制定
- [x] 分支管理（main / frontend / backend）初始化
- [ ] 教师原始仓库 Fork 迁移（待下发原始地址）
- [ ] 前端基础脚手架搭建与联调
- [ ] 后端数据模型设计与 REST API 实现
- [ ] 联系人 CRUD 及收藏功能
- [ ] Excel 批量导入导出功能
