# Backend - EE308FZ-AddressBook

后端服务模块目录，基于 Python Flask 构建。

## 技术栈计划

- **Web 框架**：Flask
- **数据库**：SQLite
- **ORM / 数据操作**：SQLAlchemy 或原生 sqlite3
- **Excel 处理**：openpyxl
- **CORS 跨域**：Flask-CORS

## 目录规划

```text
backend/
├── app/
│   ├── __init__.py     # Flask 应用工厂与扩展初始化
│   ├── models/         # 数据库模型 (Contact 等)
│   ├── routes/         # RESTful API 路由与控制器
│   └── services/       # 业务逻辑与 Excel 导入导出处理
├── tests/              # 单元测试与接口测试
├── config.py           # 基础配置文件
├── requirements.txt    # Python 依赖清单
└── run.py              # 应用启动入口
```

> 当前阶段仅建立基础目录结构，后续阶段正式集成 Flask 及相关数据模型。
