# Frontend - EE308FZ-AddressBook

前端模块目录，基于 Vue 3 生态构建。

## 技术栈计划

- **框架**：Vue 3 (Composition API, `<script setup>`)
- **构建工具**：Vite
- **UI 组件库**：Element Plus
- **网络请求**：Axios
- **路由管理**：Vue Router

## 目录规划

```text
frontend/
├── src/
│   ├── assets/        # 静态资源 (样式、图标、图片)
│   ├── components/    # 通用组件 (联系人卡片、弹窗等)
│   ├── views/         # 页面视图 (主页、联系人列表、详情页等)
│   ├── api/           # API 请求封装
│   ├── router/        # 路由配置
│   ├── App.vue        # 根组件
│   └── main.js        # 入口文件
├── index.html         # HTML 模板
├── package.json       # 项目依赖与脚本配置
└── vite.config.js     # Vite 构建配置
```

> 当前阶段仅建立基础目录结构，后续阶段正式集成 Vite 与 Vue 3 脚手架。
