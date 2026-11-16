# EE308FZ-AddressBook RESTful API Specification & Contract

> [!IMPORTANT]
> **Status**: Formal Frozen Contract.
> **Collaboration Model**: Frontend (Vue 3 + Element Plus) and Backend (Python Flask + SQLite + openpyxl) are developed independently and verified strictly against this contract document.

---

## Table of Contents

- [1. Network Environment & Integration](#1-network-environment--integration)
  - [1.1 Server Addresses & Ports](#11-server-addresses--ports)
  - [1.2 CORS & Proxy Strategy](#12-cors--proxy-strategy)
- [2. Protocol Conventions & Design Guidelines](#2-protocol-conventions--design-guidelines)
- [3. Core Data Models & Schema Definitions](#3-core-data-models--schema-definitions)
  - [3.1 Contact Object](#31-contact-object)
  - [3.2 Child Objects](#32-child-objects)
- [4. API Endpoints Specification](#4-api-endpoints-specification)
  - [4.1 List Contacts (`GET /contacts`)](#41-list-contacts-get-contacts)
  - [4.2 Get Contact Detail (`GET /contacts/{id}`)](#42-get-contact-detail-get-contactsid)
  - [4.3 Create Contact (`POST /contacts`)](#43-create-contact-post-contacts)
  - [4.4 Update Contact (`PUT /contacts/{id}`)](#44-update-contact-put-contactsid)
  - [4.5 Delete Contact (`DELETE /contacts/{id}`)](#45-delete-contact-delete-contactsid)
  - [4.6 Toggle Favorite Status (`PATCH /contacts/{id}/favorite`)](#46-toggle-favorite-status-patch-contactsidfavorite)
  - [4.7 Export Contacts (`GET /contacts/export`)](#47-export-contacts-get-contactsexport)
  - [4.8 Import Contacts (`POST /contacts/import`)](#48-import-contacts-post-contactsimport)
- [5. Excel Import & Export Specifications](#5-excel-import--export-specifications)
  - [5.1 Eight-Column Structure](#51-eight-column-structure)
  - [5.2 Encoding & Reversible Format Rules](#52-encoding--reversible-format-rules)
- [6. Contract Alignment & Decisions](#6-contract-alignment--decisions)

---

## 1. Network Environment & Integration

### 1.1 Server Addresses & Ports
- **Frontend Development Server (Vite)**: `http://localhost:5173`
- **Backend API Service (Flask)**: `http://127.0.0.1:5000`
- **Unified API Routing Prefix**: `/api/v1`

### 1.2 CORS & Proxy Strategy
To prevent browser CORS issues and ensure seamless header transmission, local development uses Vite's reverse proxy:
- Frontend requests are sent to relative path: `/api/v1/...`
- Vite proxy configuration (`frontend/vite.config.js`):
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
- **Backend Fallback**: Backend enables `flask-cors` allowing `http://localhost:5173` as well as configurable domains via the `CORS_ORIGINS` environment variable.

---

## 2. Protocol Conventions & Design Guidelines

1. **Protocol**: HTTP/1.1 with `UTF-8` encoding.
2. **Naming Convention**: All JSON request and response keys must strictly use **lowercase snake_case (`snake_case`)**.
3. **Content Types**:
   - Standard requests and responses: `Content-Type: application/json; charset=utf-8`
   - File upload (import): `Content-Type: multipart/form-data`
   - File download (export): `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (direct binary stream, not wrapped in JSON)
4. **Unified Response Formats**:
   - **Success Response (HTTP 200 / 201)**:
     ```json
     {
       "code": 200,
       "message": "success",
       "data": {}
     }
     ```
   - **Error Response (HTTP 4xx / 5xx)**:
     ```json
     {
       "code": 400,
       "error_code": "VALIDATION_ERROR",
       "message": "输入参数有误",
       "details": {
         "name": ["姓名不能为空且长度不能超过 50 字符"]
       }
     }
     ```
     *Note: For non-field validation errors (e.g. 404, 500), `details` is returned as `null`.*
5. **HTTP Status Code Mapping**:
   - `200 OK`: Successful query, update, delete, or Excel export.
   - `201 Created`: Resource successfully created.
   - `400 Bad Request`: Missing parameters, invalid formats, validation failures, or unaccepted file types (`VALIDATION_ERROR`, `INVALID_FILE`).
   - `404 Not Found`: Contact ID not found (`NOT_FOUND`).
   - `500 Internal Server Error`: Internal server error (`INTERNAL_SERVER_ERROR`).
   - *Status Code Design Note*: To ensure Axios response interceptors can uniformly unpack JSON responses, this project **does not use 204 No Content**. Deletions return `200 OK` with `{ "code": 200, "message": "联系人已删除", "data": null }`.

---

## 3. Core Data Models & Schema Definitions

The data model fully supports multiple phone numbers, email addresses, social accounts, and physical addresses per contact.

### 3.1 Contact Object

| Field | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | integer | Yes (Auto) | - | Unique contact ID |
| `name` | string | Yes | - | Contact full name (1–50 characters, trimmed) |
| `group` | string \| null | No | `null` | Group tag (e.g., 家人, 朋友, 同事, 同学) |
| `is_favorite` | boolean | No | `false` | Favorite status (`true` / `false`) |
| `notes` | string \| null | No | `null` | Notes / remarks (max 500 characters) |
| `phones` | array[Phone] | No | `[]` | List of phone numbers (0 to N) |
| `emails` | array[Email] | No | `[]` | List of email addresses (0 to N) |
| `social_accounts` | array[SocialAccount] | No | `[]` | List of social accounts (0 to N) |
| `addresses` | array[Address] | No | `[]` | List of physical addresses (0 to N) |
| `created_at` | string | Yes (Auto) | - | Creation timestamp (ISO 8601 UTC, e.g. `2026-11-15T08:30:00Z`) |
| `updated_at` | string | Yes (Auto) | - | Update timestamp (ISO 8601 UTC, e.g. `2026-11-15T08:30:00Z`) |

---

### 3.2 Child Objects

#### Phone
| Field | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `label` | string | No | `"手机"` | Label type (e.g. "手机", "工作", "住宅", "其他") |
| `number` | string | Yes | - | Phone number (digits, `+`, `-`, `(`, `)`); no whitespace allowed |
| `is_primary` | boolean | No | `false` | Primary phone flag |

```json
{
  "label": "手机",
  "number": "13800138000",
  "is_primary": true
}
```

#### Email
| Field | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `label` | string | No | `"个人"` | Label type (e.g. "个人", "工作", "其他") |
| `email` | string | Yes | - | Email address (standard email format) |
| `is_primary` | boolean | No | `false` | Primary email flag |

```json
{
  "label": "个人",
  "email": "zhangsan@example.com",
  "is_primary": true
}
```

#### SocialAccount
| Field | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `platform` | string | No | `"其他"` | Platform name (e.g. "微信", "QQ", "GitHub", "微博", "LinkedIn", "其他") |
| `account` | string | Yes | - | Account username, handle, or profile URL |

```json
{
  "platform": "微信",
  "account": "wx_zhangsan"
}
```

#### Address
| Field | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `label` | string | No | `"其他"` | Label type (e.g. "家庭", "公司", "学校", "其他") |
| `address` | string | Yes | - | Detailed address string (max 200 characters) |
| `is_primary` | boolean | No | `false` | Primary address flag |

```json
{
  "label": "家庭",
  "address": "福建省福州市大学城",
  "is_primary": true
}
```

---

## 4. API Endpoints Specification

### 4.1 List Contacts (`GET /contacts`)
Retrieve a paginated list of contacts supporting keyword search, group filtering, and favorite filtering. The response includes full child arrays (`phones`, `emails`, `social_accounts`, `addresses`) for every item.

- **Method**: `GET`
- **URL**: `/api/v1/contacts`
- **Query Parameters**:
  | Parameter | Type | Required | Default | Allowed Values & Description |
  | :--- | :--- | :---: | :---: | :--- |
  | `page` | integer | No | `1` | Must be an integer `>= 1`. Values `< 1` return HTTP `400` |
  | `page_size` | integer | No | `10` | Must be an integer between `1` and `100`. Values out of range return HTTP `400` |
  | `keyword` | string | No | `""` | Search keyword matching name, phone, email, or notes |
  | `is_favorite` | string | No | - | `"true"` / `"false"` or `"1"` / `"0"` (case-insensitive). Invalid values return HTTP `400` |
  | `group` | string | No | - | Filter by group name (e.g. "同学"). Omit to query all |

- **Success Response (HTTP 200)**:
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

### 4.2 Get Contact Detail (`GET /contacts/{id}`)
Retrieve full details of a specific contact by ID.

- **Method**: `GET`
- **URL**: `/api/v1/contacts/{id}`
- **Path Parameters**:
  - `id` (integer, required): Unique contact ID
- **Success Response (HTTP 200)**:
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
- **Error Response (HTTP 404)**:
```json
{
  "code": 404,
  "error_code": "NOT_FOUND",
  "message": "联系人不存在",
  "details": null
}
```

---

### 4.3 Create Contact (`POST /contacts`)
Create a new contact record with associated contact details. Duplicate names are permitted by design; every successful request generates a new independent record.

- **Method**: `POST`
- **URL**: `/api/v1/contacts`
- **Headers**: `Content-Type: application/json`
- **Request Body Example**:
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
- **Success Response (HTTP 201)**:
```json
{
  "code": 201,
  "message": "联系人创建成功",
  "data": {
    "id": 2
  }
}
```
- **Error Response (HTTP 400 - Validation Failure)**:
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

### 4.4 Update Contact (`PUT /contacts/{id}`)
**Full Replacement Update (Strict Whole-Resource Replacement)**.

> [!WARNING]
> **Strict Update Rules**:
> 1. The client must supply all 8 editable fields: `name`, `group`, `is_favorite`, `notes`, `phones`, `emails`, `social_accounts`, and `addresses`.
> 2. Missing any editable field returns `400 VALIDATION_ERROR` and makes no modifications to the existing database record. To clear contact lists, explicitly submit an empty array `[]`.
> 3. To clear `group` or `notes`, explicitly submit `null`. To unmark favorite, explicitly submit `is_favorite: false`.
> 4. To toggle favorite status alone, use the dedicated `PATCH /contacts/{id}/favorite` endpoint. Partial updates via `PUT` are disallowed.

- **Method**: `PUT`
- **URL**: `/api/v1/contacts/{id}`
- **Path Parameters**:
  - `id` (integer, required): Unique contact ID
- **Request Body Example**:
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
- **Success Response (HTTP 200)**:
```json
{
  "code": 200,
  "message": "联系人更新成功",
  "data": {
    "id": 2
  }
}
```
- **Error Response (HTTP 404)**:
```json
{
  "code": 404,
  "error_code": "NOT_FOUND",
  "message": "联系人不存在",
  "details": null
}
```

---

### 4.5 Delete Contact (`DELETE /contacts/{id}`)
Delete a contact and all cascaded child records (phones, emails, socials, addresses).

- **Method**: `DELETE`
- **URL**: `/api/v1/contacts/{id}`
- **Path Parameters**:
  - `id` (integer, required): Unique contact ID
- **Success Response (HTTP 200)**:
```json
{
  "code": 200,
  "message": "联系人已删除",
  "data": null
}
```
- **Error Response (HTTP 404)**:
```json
{
  "code": 404,
  "error_code": "NOT_FOUND",
  "message": "联系人不存在或已被删除",
  "details": null
}
```

---

### 4.6 Toggle Favorite Status (`PATCH /contacts/{id}/favorite`)
Dedicated endpoint to star or unstar a contact from list or detail views without submitting the entire contact payload.

- **Method**: `PATCH`
- **URL**: `/api/v1/contacts/{id}/favorite`
- **Path Parameters**:
  - `id` (integer, required): Unique contact ID
- **Request Body Example**:
```json
{
  "is_favorite": true
}
```
- **Success Response (HTTP 200)**:
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

### 4.7 Export Contacts (`GET /contacts/export`)
Export filtered contacts as an Excel binary spreadsheet (`.xlsx`).

- **Method**: `GET`
- **URL**: `/api/v1/contacts/export`
- **Query Parameters** (same as list query):
  - `keyword` (string, optional): Search keyword
  - `is_favorite` (string, optional): `"true"` / `"false"` / `"1"` / `"0"`
  - `group` (string, optional): Group filter
- **Response Headers**:
  - `Content-Type`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `Content-Disposition`: `attachment; filename="contacts_export_20261115_160000.xlsx"`
- **Response Body**: Binary `.xlsx` spreadsheet stream (not wrapped in JSON).

---

### 4.8 Import Contacts (`POST /contacts/import`)
Bulk upload and parse an Excel spreadsheet (`.xlsx`) to populate the address book.

> [!NOTE]
> **Duplicate Handling**:
> 1. Duplicate names are allowed; each row is inserted as a newly generated record with a unique ID without overwriting existing data.
> 2. Re-importing the same file inserts new rows without automatic client-side deduplication.

- **Method**: `POST`
- **URL**: `/api/v1/contacts/import`
- **Headers**: `Content-Type: multipart/form-data`
- **Form Fields**:
  - `file` (File, required): `.xlsx` format, max size 10 MB.
- **Success Response (HTTP 200)**:
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
- **Error Response (HTTP 400 - Invalid File or Size Exceeded)**:
```json
{
  "code": 400,
  "error_code": "INVALID_FILE",
  "message": "请上传有效的 Excel 文件 (.xlsx)，且文件不得超过 10MB",
  "details": null
}
```

---

## 5. Excel Import & Export Specifications

### 5.1 Eight-Column Structure

| Column | Header Name | Required | Cell Format & Value Rules |
| :---: | :--- | :---: | :--- |
| A | **姓名** | **Yes** | Plain text, e.g. `张三` |
| B | **分组** | No | Plain text, e.g. `同学`, `同事` |
| C | **是否收藏** | No | Exported as `是` or `否`. Import accepts `是`/`否`, `true`/`false`, `1`/`0` |
| D | **电话** | No | Multi-line `Label:Number`. Primary marked with trailing `*`, e.g. `手机*:13800138000\n工作:0591-88888888` |
| E | **邮箱** | No | Multi-line `Label:Email`. Primary marked with trailing `*`, e.g. `个人*:zhangsan@example.com\n工作:zhang@work.com` |
| F | **社交账号** | No | Multi-line `Platform:Account`, e.g. `微信:zhangsan_wx\nGitHub:https://github.com/zhangsan` |
| G | **地址** | No | Multi-line `Label:Address`. Primary marked with trailing `*`, e.g. `家庭*:福建省福州市大学城\n公司:软件园C区` |
| H | **备注** | No | Plain text remarks |

---

### 5.2 Encoding & Reversible Format Rules

#### (1) Multi-Item Delimiters
- **Export**: Items within a cell are joined with **newline (`\n`)** (rendered as Alt+Enter inside Excel).
- **Import**: Cells are split on newlines (`\r\n` or `\n`). If no newline is present, semicolons (`;` or `；`) act as delimiters.

#### (2) Label and Value Separation (Colon Processing)
- Standard format is `Label:Value` (e.g. `手机*:13800138000` or `GitHub:https://github.com/zhangsan`).
- Splitting occurs **strictly on the first colon (`:` or `：`)**:
  - The substring before the first colon is the **Label / Platform**.
  - All remaining content after the first colon is preserved as the **Value** (preserving URLs like `https://`).
- **No-Colon Fallback**: If no colon is present, the entire cell value is treated as the value, and the label falls back to category defaults (`"手机"`, `"个人"`, `"其他"`).

#### (3) Primary Flag (`is_primary`) Rules
- Applicable to `phones`, `emails`, and `addresses`.
- **Export**: If `is_primary === true`, a trailing asterisk `*` is appended to the label (e.g. `手机*`, `个人*`).
- **Import**: If a label ends with `*`, the asterisk is stripped and `is_primary` is set to `true`. If no item is marked with `*`, the **first item** defaults to `is_primary: true`. If multiple items have `*`, only the **first** retains `true`.

---

## 6. Contract Alignment & Decisions

1. **Strict PUT Replacement**: `PUT /contacts/{id}` requires all 8 editable fields. Missing fields yield HTTP 400.
2. **Unified JSON Response**: All business endpoints return `{ code, message, data }` JSON bodies (export returns raw binary stream).
3. **No 204 Status**: Avoids client Axios response interceptor edge cases.
4. **Formula Injection Defense**: Formulas in exported cells are formatted as text; incoming cells with real formula types are rejected during import.
