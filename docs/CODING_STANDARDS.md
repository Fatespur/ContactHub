# EE308FZ-AddressBook 开发规范与协作准则

本文档定义了 EE308FZ 双人软件工程作业团队的代码风格、命名规范、Git Commit 规范、分支策略以及 Pull Request（PR）流程。所有团队成员应严格遵守以下准则。

---

## 一、代码风格规范

### 1. 前端规范 (Vue 3 / JavaScript / CSS)
- **开发范式**：优先使用 Vue 3 Composition API 与 `<script setup>` 语法。
- **缩进与格式**：使用 2 空格缩进，禁止使用 Tab。文件结尾保留单空行。
- **引号规则**：JavaScript/TypeScript 优先使用单引号 `'`，模板内 HTML 属性使用双引号 `"`。
- **分号**：遵循统一的风格（推荐无分号风格或标准 Prettier 格式化）。
- **组件结构顺序**：遵循 `<template>` -> `<script setup>` -> `<style scoped>` 的标准排版。

### 2. 后端规范 (Python / Flask)
- **代码标准**：严格遵循 **PEP 8** 编码规范。
- **缩进与格式**：使用 4 空格缩进，禁止使用 Tab。单行字符数尽量控制在 88 或 100 字符以内。
- **注释与文档**：公开函数与关键接口必须提供简要 docstring，说明参数、返回值与异常情况。
- **类型提示**：鼓励为关键函数签名添加 Python Type Hints（类型注解）。

---

## 二、命名规范

| 类别 | 规则 | 示例 | 说明 |
| :--- | :--- | :--- | :--- |
| **前端组件文件** | PascalCase | `ContactCard.vue`, `ContactList.vue` | 必须具有语义化 |
| **前端工具/常量文件** | camelCase / kebab-case | `request.js`, `format-date.js` | 统一小写或驼峰 |
| **JS 变量与函数** | camelCase | `contactList`, `fetchContacts()` | 动词开头表示动作 |
| **JS 常量** | UPPER_SNAKE_CASE | `DEFAULT_PAGE_SIZE`, `API_BASE_URL` | 全大写下划线分割 |
| **Python 模块/文件名** | snake_case | `contact_service.py`, `models.py` | 全小写下划线分割 |
| **Python 类名** | PascalCase | `Contact`, `DatabaseManager` | 首字母大写 |
| **Python 变量与函数** | snake_case | `contact_id`, `get_contact_by_id()` | 全小写下划线分割 |
| **REST API 路径** | kebab-case / 小写名词复数 | `/api/v1/contacts`, `/contacts/export` | 遵循 RESTful 惯例 |

---

## 三、Git Commit 提交规范

提交信息采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范格式：

```text
<type>(<scope>): <subject>
```

- `<scope>` 为可选项，如 `(frontend)`, `(backend)`, `(docs)` 等。
- `<subject>` 保持简洁明了，概括本次提交的具体变动。

### 常见 Type 类型：
- **`feat`**: 新增业务功能（如添加联系人列表展示、导出 Excel 等）。
- **`fix`**: 修复 Bug 或缺陷。
- **`docs`**: 仅修改文档（如更新 README、API 说明等）。
- **`style`**: 不影响代码含义的代码格式修改（空格、分号、格式化等）。
- **`refactor`**: 代码重构（既不新增功能，也不修复 Bug 的代码变动）。
- **`test`**: 增加或修改测试用例。
- **`chore`**: 构建过程、辅助工具、项目结构或依赖更新（如初始化工程、配置 ignore 等）。

### 示例：
```bash
feat(contact): implement search contacts by keyword
fix(export): handle empty phone numbers when exporting to excel
docs: update API documentation for favorite endpoint
chore: initialize project structure
```

---

## 四、分支管理与 PR 流程

### 1. 分支架构
- **`main`**：受保护的稳定分支，对应随时可展示或发布的稳定版本。禁止直接向 `main` 推送未经审查的代码。
- **`frontend`**：前端主力开发分支。
- **`backend`**：后端主力开发分支。
- **特性分支 (`feat/*`, `fix/*`)**：
  - 从对应开发分支拉取，例如：`feat/contact-crud`、`fix/import-parse-error`。
  - 功能完成后发起 PR 合并回对应的 `frontend` 或 `backend` 分支。

### 2. Pull Request（PR）规范
1. **PR 标题**：简明清晰，符合 Commit 规范风格（如 `feat(backend): add SQLite contact models`）。
2. **PR 描述**：
   - 简述本次修改的目的与实现内容。
   - 说明自测情况或测试方法。
3. **代码审查（Code Review）**：
   - 双人协作中，PR 必须由另一位成员审查（Review）并通过后方可合并。
   - 评审人应检查代码风格、逻辑严谨性与潜在边界情况。
4. **合并策略**：推荐使用 Squash and Merge 或标准 Merge，保持主线提交历史清晰整洁。
