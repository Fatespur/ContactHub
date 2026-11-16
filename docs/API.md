# EE308FZ-AddressBook RESTful API 接口规范契约

> [!IMPORTANT]
> **当前状态**：后端拟定契约技术冻结（待前端成员审阅确认）。  
> **协作模式**：前端（Vue 3 + Element Plus）与后端（Python Flask + SQLite + openpyxl）独立并行开发，联调严格以本文档为基准契约。待双方共同确认后转为正式冻结规范。

---

## 目录

- [一、前后端联调与网络环境](#一前后端联调与网络环境)
- [二、接口通用协议与设计准则](#二接口通用协议与设计准则)
- [三、核心数据模型与字段定义](#三核心数据模型与字段定义)
- [四、接口详细规范](#四接口详细规范)
  - [1. 联系人列表查询 (GET /contacts)](#1-联系人列表查询-get-contacts)
  - [2. 联系人详情查询 (GET /contacts/{id})](#2-联系人详情查询-get-contactsid)
  - [3. 新增联系人 (POST /contacts)](#3-新增联系人-post-contacts)
  - [4. 修改联系人 (PUT /contacts/{id})](#4-修改联系人-put-contactsid)
  - [5. 删除联系人 (DELETE /contacts/{id})](#5-删除联系人-delete-contactsid)
  - [6. 切换联系人收藏状态 (PATCH /contacts/{id}/favorite)](#6-切换联系人收藏状态-patch-contactsidfavorite)
  - [7. 导出联系人 (GET /contacts/export)](#7-导出联系人-get-contactsexport)
  - [8. 导入联系人 (POST /contacts/import)](#8-导入联系人-post-contactsimport)
- [五、Excel 导入与导出规范](#五excel-导入与导出规范)
- [六、规范确认状态与待确认事项](#六规范确认状态与待确认事项)

---

## 一、前后端联调与网络环境

### 1. 服务地址与端口分配
- **前端开发服务（Vite）**：`http://localhost:5173`
- **后端接口服务（Flask）**：`http://127.0.0.1:5000`
- **API 统一路由前缀**：`/api/v1`

### 2. 跨域与代理方案（开发阶段）
为了避免浏览器跨域拦截（CORS）并保证携带 Header 顺畅，前端统一使用 Vite 反向代理：
- 前端请求统一发送至相对路径：`/api/v1/...`
- 前端 `vite.config.js` 配置代理示例：
  ```javascript
  // vite.config.js
  export default defineConfig({
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:5000',
          changeOrigin: true
        }
      }
    }
  })
  ```
- **后端兜底**：后端使用 `flask-cors` 允许 `http://localhost:5173`，以便直接调用测试。

---

## 二、接口通用协议与设计准则

1. **协议规范**：HTTP/1.1，数据传输编码为 `UTF-8`。
2. **命名风格**：JSON 请求体与响应体中的字段命名一律强制使用 **小写下划线命名法（`snake_case`）**。
3. **数据格式**：
   - 常规请求与响应：`Content-Type: application/json; charset=utf-8`
   - 文件上传（导入）：`Content-Type: multipart/form-data`
   - 文件下载（导出）：`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`（直接返回二进制文件流，绝不使用 JSON 包装）
4. **统一响应结构**：
   - **成功响应（200 / 201）**：
     ```json
     {
       "code": 200,
       "message": "success",
       "data": {}
     }
     ```
   - **失败/错误响应（4xx / 5xx）**：
     ```json
     {
       "code": 400,
       "error_code": "VALIDATION_ERROR",
       "message": "输入参数有误，请检查",
       "details": {
         "name": ["姓名不能为空且长度不能超过 50 字符"]
       }
     }
     ```
     *注：非字段校验错误（如 404、500 等）时，`details` 统一返回 `null`。*
5. **HTTP 状态码约定**：
   - `200 OK`：查询成功、更新成功、删除成功、Excel 导出成功。
   - `201 Created`：资源创建成功。
   - `400 Bad Request`：参数缺失、格式错误、校验未通过、非法文件类型等。
   - `404 Not Found`：请求的联系人 ID 不存在。
   - `500 Internal Server Error`：服务器内部错误。
   - *响应体特别说明*：为保证前端 Axios 响应拦截器统一解包，本项目全部业务接口一律返回统一 JSON 响应体（除 Excel 导出返回二进制流外）。HTTP `204 No Content` 依照规范不允许包含任何响应体，与前端统一拦截器冲突，因此本项目**不采用 204 状态码**，删除操作统一返回 `200 OK` 伴随统一 JSON。

---

## 三、核心数据模型与字段定义

数据模型严格支持一位联系人拥有**多个电话号码、多个邮箱、多个社交账号和多个地址**。

### 1. Contact（联系人主体对象）

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :---: | :--- | :--- |
| `id` | integer | 是(系统自增) | - | 联系人唯一标识 ID |
| `name` | string | 是 | - | 联系人姓名（1-50 字符，自动去除首尾空白） |
| `group` | string \| null | 否 | null | 分组标签（如：家人、朋友、同事、同学） |
| `is_favorite` | boolean | 否 | `false` | 是否收藏（`true` / `false`） |
| `notes` | string \| null | 否 | null | 备注信息（最长 500 字符） |
| `phones` | array[Phone] | 否 | `[]` | 电话列表（支持 0~N 项） |
| `emails` | array[Email] | 否 | `[]` | 邮箱列表（支持 0~N 项） |
| `social_accounts` | array[SocialAccount] | 否 | `[]` | 社交账号列表（支持 0~N 项） |
| `addresses` | array[Address] | 否 | `[]` | 地址列表（支持 0~N 项） |
| `created_at` | string | 是(系统生成) | - | 创建时间（ISO 8601 UTC 格式，如 `2026-11-15T08:30:00Z`） |
| `updated_at` | string | 是(系统生成) | - | 更新时间（ISO 8601 UTC 格式，如 `2026-11-15T08:30:00Z`） |

---

### 2. 子对象结构定义

#### Phone（电话项）

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :---: | :--- | :--- |
| `label` | string | 否 | `"手机"` | 标签类型（推荐："手机", "工作", "住宅", "其他" 或自定义） |
| `number` | string | 是 | - | 电话号码（必填，允许数字、加号、中划线、括号） |
| `is_primary` | boolean | 否 | `false` | 是否为主电话 |

```json
{
  "label": "手机",
  "number": "13800138000",
  "is_primary": true
}
```

#### Email（邮箱项）

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :---: | :--- | :--- |
| `label` | string | 否 | `"个人"` | 标签类型（推荐："个人", "工作", "其他" 或自定义） |
| `email` | string | 是 | - | 电子邮箱（必填，必须符合标准 Email 格式） |
| `is_primary` | boolean | 否 | `false` | 是否为主邮箱 |

```json
{
  "label": "个人",
  "email": "zhangsan@example.com",
  "is_primary": true
}
```

#### SocialAccount（社交账号项）

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :---: | :--- | :--- |
| `platform` | string | 否 | `"其他"` | 平台名称（推荐："微信", "QQ", "GitHub", "微博", "LinkedIn", "其他"） |
| `account` | string | 是 | - | 账号名 / ID / 主页链接 |

```json
{
  "platform": "微信",
  "account": "wx_zhangsan"
}
```

#### Address（地址项）

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :---: | :--- | :--- |
| `label` | string | 否 | `"其他"` | 标签类型（推荐："家庭", "公司", "学校", "其他"） |
| `address` | string | 是 | - | 详细地址文本（必填，最长 200 字符） |
| `is_primary` | boolean | 否 | `false` | 是否为默认地址 |

```json
{
  "label": "家庭",
  "address": "福建省福州市大学城",
  "is_primary": true
}
```

---

## 四、接口详细规范

### 1. 联系人列表查询 (GET /contacts)
用于分页、检索和筛选联系人列表。返回联系人列表项，**一律返回完整的多联系方式数组（`phones`, `emails`, `social_accounts`, `addresses`）**，与详情接口保持一致。

- **请求方法**：`GET`
- **请求 URL**：`/api/v1/contacts`
- **Query 参数**：
  | 参数名 | 类型 | 必填 | 默认值 | 合法取值与说明 |
  | :--- | :--- | :---: | :---: | :--- |
  | `page` | integer | 否 | `1` | 必须 `>= 1` 的整数。若 `< 1` 返回 `400` |
  | `page_size` | integer | 否 | `10` | 必须在 `1` 到 `100` 之间的整数。超出范围返回 `400` |
  | `keyword` | string | 否 | `""` | 模糊搜索词，匹配姓名、电话、邮箱、备注 |
  | `is_favorite` | string | 否 | - | 合法取值为 `"true"`、`"false"` 或 `"1"`、`"0"`（不区分大小写）。不传查询全部，非法值返回 `400` |
  | `group` | string | 否 | - | 分组筛选（如 "同学"），不传查询全部 |

- **成功响应示例 (HTTP 200)**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 1,
    "page": 1,
    "page_size": 10,
    "items": [
      {
        "id": 1,
        "name": "张三",
        "group": "同学",
        "is_favorite": true,
        "notes": "福州大学软件工程",
        "phones": [
          {
            "label": "手机",
            "number": "13800138000",
            "is_primary": true
          },
          {
            "label": "工作",
            "number": "0591-88888888",
            "is_primary": false
          }
        ],
        "emails": [
          {
            "label": "个人",
            "email": "zhangsan@example.com",
            "is_primary": true
          }
        ],
        "social_accounts": [
          {
            "platform": "微信",
            "account": "zhangsan_wx"
          },
          {
            "platform": "GitHub",
            "account": "https://github.com/zhangsan-fzu"
          }
        ],
        "addresses": [
          {
            "label": "学校",
            "address": "福建省福州市大学城福州大学旗山校区",
            "is_primary": true
          }
        ],
        "created_at": "2026-11-15T08:00:00Z",
        "updated_at": "2026-11-15T08:00:00Z"
      }
    ]
  }
}
```

---

### 2. 联系人详情查询 (GET /contacts/{id})
获取指定 ID 联系人的完整详情。

- **请求方法**：`GET`
- **请求 URL**：`/api/v1/contacts/{id}`
- **Path 参数**：
  - `id` (integer, 必填): 联系人唯一 ID
- **成功响应示例 (HTTP 200)**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "张三",
    "group": "同学",
    "is_favorite": true,
    "notes": "福州大学软件工程",
    "phones": [
      {
        "label": "手机",
        "number": "13800138000",
        "is_primary": true
      },
      {
        "label": "工作",
        "number": "0591-88888888",
        "is_primary": false
      }
    ],
    "emails": [
      {
        "label": "个人",
        "email": "zhangsan@example.com",
        "is_primary": true
      }
    ],
    "social_accounts": [
      {
        "platform": "微信",
        "account": "zhangsan_wx"
      }
    ],
    "addresses": [
      {
        "label": "学校",
        "address": "福建省福州市大学城福州大学旗山校区",
        "is_primary": true
      }
    ],
    "created_at": "2026-11-15T08:00:00Z",
    "updated_at": "2026-11-15T08:00:00Z"
  }
}
```
- **错误响应示例 (HTTP 404)**：
```json
{
  "code": 404,
  "error_code": "NOT_FOUND",
  "message": "联系人不存在",
  "details": null
}
```

---

### 3. 新增联系人 (POST /contacts)
创建新联系人记录及关联的多联系方式。系统默认允许同名联系人，每次请求均创建全新独立记录。

- **请求方法**：`POST`
- **请求 URL**：`/api/v1/contacts`
- **请求头**：`Content-Type: application/json`
- **请求 Body 示例**：
```json
{
  "name": "李四",
  "group": "同事",
  "is_favorite": false,
  "notes": "前端架构师",
  "phones": [
    {
      "label": "手机",
      "number": "13900139000",
      "is_primary": true
    }
  ],
  "emails": [
    {
      "label": "工作",
      "email": "lisi@tech.com",
      "is_primary": true
    }
  ],
  "social_accounts": [
    {
      "platform": "微信",
      "account": "lisi_web"
    }
  ],
  "addresses": [
    {
      "label": "公司",
      "address": "福州市软件园 C 区",
      "is_primary": true
    }
  ]
}
```
- **成功响应示例 (HTTP 201)**：
```json
{
  "code": 201,
  "message": "联系人创建成功",
  "data": {
    "id": 2
  }
}
```
- **错误响应示例 (HTTP 400 - 参数校验失败)**：
```json
{
  "code": 400,
  "error_code": "VALIDATION_ERROR",
  "message": "输入参数有误",
  "details": {
    "name": ["姓名不能为空且长度不能超过 50 字符"],
    "emails": ["第 1 项邮箱格式不合法"]
  }
}
```

---

### 4. 修改联系人 (PUT /contacts/{id})
**完整资源更新（Full Replacement Update）**。

> [!WARNING]
> **更新规则说明**：  
> 1. 客户端提交时必须提供所有可编辑字段（`name`, `group`, `is_favorite`, `notes`, `phones`, `emails`, `social_accounts`, `addresses`）。  
> 2. 缺少任一可编辑字段时返回 `400 VALIDATION_ERROR`，且不修改已有数据；清空联系方式须显式提交相应空数组 `[]`。
> 3. 清空 `group` 或 `notes` 须显式提交 `null`；取消收藏须显式提交 `is_favorite: false`。
> 4. 若仅需切换收藏状态，请使用专用的 `PATCH /contacts/{id}/favorite` 接口，禁止使用 `PUT` 做局部字段更新。

- **请求方法**：`PUT`
- **请求 URL**：`/api/v1/contacts/{id}`
- **Path 参数**：
  - `id` (integer, 必填): 联系人唯一 ID
- **请求 Body 示例**：
```json
{
  "name": "李四 (更新)",
  "group": "好友",
  "is_favorite": true,
  "notes": "全栈开发",
  "phones": [
    {
      "label": "手机",
      "number": "13900139000",
      "is_primary": true
    },
    {
      "label": "备用",
      "number": "13911112222",
      "is_primary": false
    }
  ],
  "emails": [
    {
      "label": "工作",
      "email": "lisi@newtech.com",
      "is_primary": true
    }
  ],
  "social_accounts": [
    {
      "platform": "微信",
      "account": "lisi_web"
    },
    {
      "platform": "GitHub",
      "account": "https://github.com/lisi-dev"
    }
  ],
  "addresses": [
    {
      "label": "公司",
      "address": "福州市高新区创新园",
      "is_primary": true
    }
  ]
}
```
- **成功响应示例 (HTTP 200)**：
```json
{
  "code": 200,
  "message": "联系人更新成功",
  "data": {
    "id": 2
  }
}
```
- **错误响应示例 (HTTP 404)**：
```json
{
  "code": 404,
  "error_code": "NOT_FOUND",
  "message": "联系人不存在",
  "details": null
}
```

---

### 5. 删除联系人 (DELETE /contacts/{id})
删除指定联系人记录及其所有级联关联数据（电话、邮箱、社交账号、地址）。

- **请求方法**：`DELETE`
- **请求 URL**：`/api/v1/contacts/{id}`
- **Path 参数**：
  - `id` (integer, 必填): 联系人唯一 ID
- **成功响应示例 (HTTP 200)**：
```json
{
  "code": 200,
  "message": "联系人已删除",
  "data": null
}
```
- **错误响应示例 (HTTP 404)**：
```json
{
  "code": 404,
  "error_code": "NOT_FOUND",
  "message": "联系人不存在或已被删除",
  "details": null
}
```

---

### 6. 切换联系人收藏状态 (PATCH /contacts/{id}/favorite)
针对列表页或详情页的“点击一键星标/取消星标”操作，避免提交完整表单。

- **请求方法**：`PATCH`
- **请求 URL**：`/api/v1/contacts/{id}/favorite`
- **Path 参数**：
  - `id` (integer, 必填): 联系人唯一 ID
- **请求 Body 示例**：
```json
{
  "is_favorite": true
}
```
- **成功响应示例 (HTTP 200)**：
```json
{
  "code": 200,
  "message": "收藏状态更新成功",
  "data": {
    "id": 2,
    "is_favorite": true
  }
}
```

---

### 7. 导出联系人 (GET /contacts/export)
将符合筛选条件的联系人批量导出为 Excel 表格（限定为 `.xlsx`）。

- **请求方法**：`GET`
- **请求 URL**：`/api/v1/contacts/export`
- **Query 参数**（与列表筛选规则保持一致）：
  - `keyword` (string, 可选): 搜索关键字
  - `is_favorite` (string, 可选): `"true"` / `"false"` / `"1"` / `"0"`
  - `group` (string, 可选): 分组过滤
- **响应头 (Headers)**：
  - `Content-Type`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `Content-Disposition`: `attachment; filename="contacts_export_20261115_160000.xlsx"`
- **响应 Body**：二进制 Excel 文件流（Binary Stream）。**直接返回文件流，不使用 JSON 包装**。前端通过 Axios 设置 `responseType: 'blob'` 接收后触发浏览器下载。

---

### 8. 导入联系人 (POST /contacts/import)
通过上传 `.xlsx` 格式的 Excel 文件批量解析并写入通讯录。

> [!NOTE]
> **重复导入与重复联系人处理原则**：  
> 1. 系统默认允许同名联系人，导入时每行均按新增独立记录插入，分配新 ID，不覆盖原有数据。  
> 2. 重复导入同一文件，后端将再次全部作为新增记录插入，不会自动去重。如需去重，由用户在界面上自行管理。

- **请求方法**：`POST`
- **请求 URL**：`/api/v1/contacts/import`
- **请求头**：`Content-Type: multipart/form-data`
- **Form 参数**：
  - `file` (File, 必填): 仅接受 `.xlsx` 格式的 Excel 文件，大小不能超过 10 MB。
- **成功响应示例 (HTTP 200)**：
```json
{
  "code": 200,
  "message": "导入完成",
  "data": {
    "total_rows": 10,
    "success_count": 9,
    "failed_count": 1,
    "errors": [
      {
        "row": 4,
        "name": "王五",
        "reason": "第 4 行姓名为空或格式无法识别"
      }
    ]
  }
}
```
- **错误响应示例 (HTTP 400 - 文件不合法或超限)**：
```json
{
  "code": 400,
  "error_code": "INVALID_FILE",
  "message": "请上传有效的 Excel 文件 (.xlsx)，且文件不得超过 10MB",
  "details": null
}
```

---

## 五、Excel 导入与导出规范

为了支撑每位联系人拥有多个电话、邮箱、社交账号和地址，且保证数据在导出后可无损、确定、可逆地重新导入，约定如下 Excel 表格规范与编解码规则。

### 1. 表头列结构设计（固定 8 列）

| 列号 | 列名（表头） | 必填 | 单元格格式与内容规则 |
| :---: | :--- | :---: | :--- |
| A | **姓名** | **是** | 文本，如 `张三` |
| B | **分组** | 否 | 文本，如 `同学`、`同事` |
| C | **是否收藏** | 否 | 文本，导出为 `是` 或 `否`（导入时兼容 `true`/`false`、`1`/`0`） |
| D | **电话** | 否 | 单元格内换行多项，格式为 `标签:号码`。主电话标签带 `*`，如 `手机*:13800138000\n工作:0591-88888888` |
| E | **邮箱** | 否 | 单元格内换行多项，格式为 `标签:邮箱`。主邮箱标签带 `*`，如 `个人*:zhangsan@example.com\n工作:zhang@work.com` |
| F | **社交账号** | 否 | 单元格内换行多项，格式为 `平台:账号`，如 `微信:zhangsan_wx\nGitHub:https://github.com/zhangsan` |
| G | **地址** | 否 | 单元格内换行多项，格式为 `标签:详细地址`。主地址标签带 `*`，如 `家庭*:福建省福州市大学城\n公司:软件园C区` |
| H | **备注** | 否 | 文本说明 |

---

### 2. 多联系方式编解码与可逆规则

#### (1) 多项条目的分隔规则
- **导出规则**：同一单元格内有多条记录时，**统一使用换行符（`\n`）** 进行连接（在 Excel 中展现为 Alt+Enter 单元格内换行）。
- **导入规则**：优先按换行符（`\r\n` 或 `\n`）拆分为多个条目。若单元格内不包含换行符，则兼容按分号（英文分号 `;` 或中文分号 `；`）进行拆分。
- *优势*：使用换行符作为主分隔符，能够彻底避免地址或社交账号中包含分号而导致的误拆分问题。

#### (2) 标签与具体值的切分规则（冒号处理）
- 每一项的标准格式为：`标签:值`（如 `手机*:13800138000` 或 `GitHub:https://github.com/zhangsan`）。
- **关键解析规则**：为防止值中本身包含冒号（例如社交链接中的 `https://`，或地址中的冒号），后端解析时**严格仅以第一个出现的英文冒号 `:` 或中文冒号 `：` 为界分割一次**：
  - 第一个冒号左侧为**标签（Label/Platform）**；
  - 第一个冒号右侧的剩余全部文本完整作为**具体值（Value）**。
- **无冒号回退规则**：若某项不包含任何冒号（如用户直接填写 `13800138000`）：
  - 整行文本直接作为具体值；
  - 标签自动回退为该类别的默认标签（电话默认为 `"手机"`，邮箱默认为 `"个人"`，社交账号默认为 `"其他"`，地址默认为 `"其他"`）。

#### (3) 主联系方式（`is_primary`）的保存与恢复规则
- 适用范围：`phones`、`emails`、`addresses`（`social_accounts` 不设 primary 标记）。
- **导出规则**：
  - 若该项 `is_primary === true`，在标签末尾附加星号 `*`（例如 `手机*`、`个人*`、`家庭*`），拼接为 `标签*:值`。
  - 若为 `false`，则不带星号，即 `标签:值`。
- **导入规则**：
  - 若解析出的标签以 `*` 结尾（例如 `手机*`），则将标签修正为去除 `*` 后的名称（`手机`），并将该项标记为 `is_primary: true`。
  - 若一个联系人的某类别多项中均未带 `*`，则默认将**第 1 项**自动设为 `is_primary: true`，其余为 `false`。
  - 若有多项标记了 `*`，则以**最先出现的带 `*` 项**为 `is_primary: true`，其余自动重置为 `false`，保证数据唯一合法性。

---

## 六、规范确认状态与待确认事项

### 1. 【后端拟定技术基准】（待前端审阅）
- 前端端口 `5173`，后端端口 `5000`，API 前缀统一 `/api/v1`。
- 前端使用 Vite Proxy 反向代理消除跨域。
- 所有 JSON 传输字段强制使用小写下划线 `snake_case`。
- 完整支持多电话、多邮箱、多社交账号、多地址的对象数组结构，列表接口与详情接口格式保持一致。
- Excel 统一限定为 `.xlsx` 格式，文件上限 10 MB；采用 8 列表格与基于换行符/星号的可逆编解码规则。
- 允许同名联系人，导入操作均作为独立新增记录处理，重复导入同一文件不会覆盖或自动去重。
- `PUT` 接口为全量更新；`DELETE` 接口统一返回 `200 OK` 伴随统一 JSON 响应体；Excel 导出直接返回二进制文件。

### 2. 【待前端成员确认事项】（需双人协商确定）
1. **分页默认值与页码范围**：
   - 目前约定默认每页 `10` 条，最大每页 `100` 条。前端 Element Plus 分页组件是否需要增加 `20`, `50` 的快捷切换？
2. **标签录入交互**：
   - 联系方式的 `label` 与社交平台的 `platform`：前端界面是采用**固定的下拉选择框（Select）**，还是**支持用户自行输入任意自定义标签（Select with create-tag）**？
3. **批量删除需求**：
   - 当前契约仅提供单条删除（`DELETE /contacts/{id}`）。前端是否需要批量勾选删除接口（如 `POST /contacts/batch-delete` 传入 `{ ids: [1, 2, 3] }`）？
4. **代码格式化与合并策略**：
   - 前端是否统一配置 Prettier 规则（如单引号、无分号、2空格缩进）？
   - GitHub PR 合并时统一采用 `Squash and merge` 还是保留完整分支历史的 Merge Commit？
