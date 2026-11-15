# EE308FZ-AddressBook RESTful API 接口规范契约

> [!IMPORTANT]
> **当前状态**：接口规范契约（待前端确认部分细节，业务功能尚未开发）。  
> **协作模式**：前端（Vue 3 + Element Plus）与后端（Python Flask + SQLite + openpyxl）独立并行开发，联调严格以本文档为唯一基准契约。

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
   - 文件下载（导出）：`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
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
         "name": ["姓名不能为空"],
         "phones": ["第 1 项号码格式不正确"]
       }
     }
     ```
5. **HTTP 状态码约定**：
   - `200 OK`：查询、更新成功
   - `201 Created`：资源创建成功
   - `204 No Content`：删除成功（无响应体）或返回 `200` 带有统一响应结构
   - `400 Bad Request`：参数缺失、校验失败或格式错误
   - `404 Not Found`：请求的联系人 ID 不存在
   - `409 Conflict`：业务冲突（如导入文件存在不可恢复的冲突）
   - `500 Internal Server Error`：服务端未捕获异常

---

## 三、核心数据模型与字段定义

数据模型严格支持一位联系人拥有**多个电话号码、多个邮箱、多个社交账号和多个地址**。

### 1. Contact（联系人主体对象）

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :---: | :--- | :--- |
| `id` | integer | 是(系统生成) | - | 联系人唯一标识 ID |
| `name` | string | 是 | - | 联系人姓名（1-50 字符，前后自动去除首尾空格） |
| `group` | string \| null | 否 | null | 分组标签（如：家人、朋友、同事、同学、业务客户） |
| `is_favorite` | boolean | 否 | `false` | 是否收藏 |
| `notes` | string \| null | 否 | null | 备注说明信息（最长 500 字符） |
| `phones` | array[Phone] | 否 | `[]` | 电话列表（至少支持 0~N 个） |
| `emails` | array[Email] | 否 | `[]` | 邮箱列表（至少支持 0~N 个） |
| `social_accounts` | array[SocialAccount] | 否 | `[]` | 社交账号列表（至少支持 0~N 个） |
| `addresses` | array[Address] | 否 | `[]` | 地址列表（至少支持 0~N 个） |
| `created_at` | string | 是(系统生成) | - | 创建时间（ISO 8601 格式，如 `2026-11-15T08:30:00Z`） |
| `updated_at` | string | 是(系统生成) | - | 更新时间（ISO 8601 格式，如 `2026-11-15T08:30:00Z`） |

---

### 2. 子对象结构定义

#### Phone（电话项）
```json
{
  "label": "手机",        // string, 标签类型（推荐："手机" | "工作" | "住宅" | "其他" 或自定义）
  "number": "13800138000",// string, 电话号码（必填，允许包含 +、-、空格）
  "is_primary": true      // boolean, 是否作为主联系电话（默认 false）
}
```

#### Email（邮箱项）
```json
{
  "label": "个人",               // string, 标签类型（推荐："个人" | "工作" | "其他" 或自定义）
  "email": "zhangsan@example.com", // string, 邮箱地址（必填，符合标准 email 格式）
  "is_primary": true             // boolean, 是否为主邮箱（默认 false）
}
```

#### SocialAccount（社交账号项）
```json
{
  "platform": "微信",    // string, 平台名称（推荐："微信" | "QQ" | "GitHub" | "微博" | "LinkedIn" | "其他"）
  "account": "wx_zhangsan" // string, 账号名/ID/主页链接（必填）
}
```

#### Address（地址项）
```json
{
  "label": "家庭",             // string, 标签类型（推荐："家庭" | "公司" | "学校" | "其他"）
  "address": "福建省福州市大学城", // string, 详细地址（必填，最长 200 字符）
  "is_primary": true           // boolean, 是否为默认联系地址（默认 false）
}
```

---

## 四、接口详细规范

### 1. 联系人列表查询 (GET /contacts)
用于分页、检索和筛选联系人列表。返回联系人的核心概览信息（为优化列表传输性能，列表项中 `phones`、`emails`、`addresses`、`social_accounts` 保留首项或完整数组）。

- **请求方法**：`GET`
- **请求 URL**：`/api/v1/contacts`
- **Query 参数**：
  | 参数名 | 类型 | 必填 | 默认值 | 说明 |
  | :--- | :--- | :---: | :---: | :--- |
  | `page` | integer | 否 | `1` | 当前页码，从 1 开始 |
  | `page_size` | integer | 否 | `10` | 每页数量（允许范围 1~100） |
  | `keyword` | string | 否 | `""` | 模糊搜索词（匹配：姓名、电话号码、邮箱、备注） |
  | `is_favorite` | boolean | 否 | null | 收藏筛选（`true` 仅看收藏，`false` 仅看未收藏，不传查全部） |
  | `group` | string | 否 | null | 分组筛选（如 "同学"，不传查全部） |

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
          { "label": "手机", "number": "13800138000", "is_primary": true },
          { "label": "工作", "number": "0591-88888888", "is_primary": false }
        ],
        "emails": [
          { "label": "个人", "email": "zhangsan@example.com", "is_primary": true }
        ],
        "social_accounts": [
          { "platform": "微信", "account": "zhangsan_wx" },
          { "platform": "GitHub", "account": "zhangsan-fzu" }
        ],
        "addresses": [
          { "label": "学校", "address": "福建省福州市大学城福州大学旗山校区", "is_primary": true }
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
  - `id` (integer, 必填): 联系人 ID
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
      { "label": "手机", "number": "13800138000", "is_primary": true },
      { "label": "工作", "number": "0591-88888888", "is_primary": false }
    ],
    "emails": [
      { "label": "个人", "email": "zhangsan@example.com", "is_primary": true },
      { "label": "工作", "email": "zhangsan@company.com", "is_primary": false }
    ],
    "social_accounts": [
      { "platform": "微信", "account": "zhangsan_wx" },
      { "platform": "QQ", "account": "10001" },
      { "platform": "GitHub", "account": "zhangsan-fzu" }
    ],
    "addresses": [
      { "label": "学校", "address": "福建省福州市大学城福州大学旗山校区", "is_primary": true },
      { "label": "家庭", "address": "福建省厦门市思明区", "is_primary": false }
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
  "message": "联系人 ID 1 不存在",
  "details": null
}
```

---

### 3. 新增联系人 (POST /contacts)
创建新联系人记录及关联的多联系方式。

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
    { "label": "手机", "number": "13900139000", "is_primary": true }
  ],
  "emails": [
    { "label": "工作", "email": "lisi@tech.com", "is_primary": true }
  ],
  "social_accounts": [
    { "platform": "微信", "account": "lisi_web" }
  ],
  "addresses": [
    { "label": "公司", "address": "福州市软件园 C 区", "is_primary": true }
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
- **错误响应示例 (HTTP 400 - 校验未通过)**：
```json
{
  "code": 400,
  "error_code": "VALIDATION_ERROR",
  "message": "输入参数有误",
  "details": {
    "name": ["姓名不能为空且长度不能超过 50 字符"],
    "emails": ["第 1 项工作邮箱格式不合法"]
  }
}
```

---

### 4. 修改联系人 (PUT /contacts/{id})
全量更新指定联系人信息及其多联系方式列表。

- **请求方法**：`PUT`
- **请求 URL**：`/api/v1/contacts/{id}`
- **Path 参数**：
  - `id` (integer, 必填): 联系人 ID
- **请求 Body 示例**：
```json
{
  "name": "李四 (更新)",
  "group": "好友",
  "is_favorite": true,
  "notes": "全栈开发",
  "phones": [
    { "label": "手机", "number": "13900139000", "is_primary": true },
    { "label": "备用", "number": "13911112222", "is_primary": false }
  ],
  "emails": [
    { "label": "工作", "email": "lisi@newtech.com", "is_primary": true }
  ],
  "social_accounts": [
    { "platform": "微信", "account": "lisi_web" },
    { "platform": "GitHub", "account": "lisi-dev" }
  ],
  "addresses": [
    { "label": "公司", "address": "福州市高新区创新园", "is_primary": true }
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

---

### 5. 删除联系人 (DELETE /contacts/{id})
删除指定联系人记录及其所有级联关联数据（电话、邮箱、社交账号、地址）。

- **请求方法**：`DELETE`
- **请求 URL**：`/api/v1/contacts/{id}`
- **Path 参数**：
  - `id` (integer, 必填): 联系人 ID
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
  - `id` (integer, 必填): 联系人 ID
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
将符合筛选条件的联系人批量导出为 Excel 表格（`.xlsx`）。

- **请求方法**：`GET`
- **请求 URL**：`/api/v1/contacts/export`
- **Query 参数**（与列表筛选保持一致）：
  - `keyword` (string, 可选): 搜索关键字
  - `is_favorite` (boolean, 可选): 收藏状态过滤
  - `group` (string, 可选): 分组过滤
- **响应头 (Headers)**：
  - `Content-Type`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `Content-Disposition`: `attachment; filename="contacts_export_20261115_160000.xlsx"`
- **响应 Body**：二进制文件流（Binary Stream）。前端建议使用 `axios` 设置 `responseType: 'blob'`，通过创建 Object URL 触发浏览器下载。

---

### 8. 导入联系人 (POST /contacts/import)
通过上传 Excel 文件批量解析并写入通讯录。

- **请求方法**：`POST`
- **请求 URL**：`/api/v1/contacts/import`
- **请求头**：`Content-Type: multipart/form-data`
- **Form 参数**：
  - `file` (File, 必填): 上传的 `.xlsx` 或 `.xls` 文件（限制大小 <= 10MB）
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
        "reason": "电话号码格式无效且姓名重复"
      }
    ]
  }
}
```
- **错误响应示例 (HTTP 400 - 文件不合法)**：
```json
{
  "code": 400,
  "error_code": "INVALID_FILE",
  "message": "请上传有效的 Excel 文件 (.xlsx 或 .xls)，且文件不得超过 10MB",
  "details": null
}
```

---

## 五、Excel 导入与导出规范

为了支撑每位联系人多联系方式在二维表格中的表现，前后端约定如下 Excel 列结构与多值解析逻辑。

### 1. 表头列结构设计

| 列序号 | 列名（表头） | 必填 | 格式规范与多值示例 |
| :---: | :--- | :---: | :--- |
| A | **姓名** | **是** | 文本，如 `张三` |
| B | **分组** | 否 | 文本，如 `同学`、`同事` |
| C | **是否收藏** | 否 | `是` / `否`（亦兼容 `true`/`false`、`1`/`0`） |
| D | **电话** | 否 | 支持多条，以分号 `;` 或换行符分隔。<br>示例：`手机:13800138000; 工作:0591-88888888` 或直接写号码 `13800138000; 13900001111`（无标签时默认标签为“手机”） |
| E | **邮箱** | 否 | 支持多条，以分号 `;` 或换行符分隔。<br>示例：`个人:zhangsan@example.com; 工作:zhangsan@work.com` 或直接写 `zhangsan@example.com`（无标签时默认标签为“个人”） |
| F | **社交账号** | 否 | 支持多条，以分号 `;` 或换行符分隔。<br>示例：`微信:zhangsan_wx; QQ:10001; GitHub:zhangsan-fzu` |
| G | **地址** | 否 | 支持多条，以分号 `;` 或换行符分隔。<br>示例：`学校:福州大学旗山校区; 家庭:厦门市思明区` 或直接写地址（无标签时默认标签为“家庭”） |
| H | **备注** | 否 | 文本说明 |

### 2. 导出规则（后端行为）
- 后端使用 `openpyxl` 生成标准 `.xlsx` 文件。
- 首行冻结且设置为粗体浅蓝背景作为标题栏。
- 多联系方式统一按照 `标签:具体值` 格式导出，多条之间使用英文分号加空格（`; `）连接。

### 3. 导入解析规则（后端行为）
1. 校验首行表头列名，缺少“姓名”列则拒绝解析。
2. 空行直接跳过，不计入统计。
3. 对每行进行数据提取与正则校验：
   - 姓名为空：记录行级错误，继续处理下一行。
   - 分割多项数据（支持中英文分号 `;`、`；` 或换行符 `\n`）。
   - 解析冒号（`:`、`：`）前缀作为标签（label/platform），无冒号则自动回退至默认标签。
4. 返回解析完成报告，说明成功行数、失败行数及具体行号的错误原因。

---

## 六、规范确认状态与待确认事项

### 1. 【已确认规范】（双方严格遵守）
- [x] 前端端口 `5173`，后端端口 `5000`，API 前缀统一 `/api/v1`。
- [x] 前端使用 Vite Proxy 反向代理消除开发跨域问题。
- [x] 所有 JSON 传输字段强制使用小写下划线 `snake_case`。
- [x] 完整支持多电话、多邮箱、多社交账号、多地址的对象数组结构。
- [x] 统一使用标准 HTTP 状态码搭配 JSON 业务错误体（`code`, `error_code`, `message`, `details`）。
- [x] Excel 采用八列结构与分号/换行多值表示规范。

### 2. 【待前端成员确认事项】（需双人协商确定）
1. **分页默认值与页码范围**：
   - 目前约定默认每页 `10` 条，最大每页 `100` 条。前端 Element Plus 分页组件是否需要增加 `20`, `50` 的快捷切换？
2. **导入冲突处理策略**：
   - 当导入的联系人“姓名完全相同”时，采用何种策略？
     - *选项 A（默认推荐）*：直接新增一条记录（支持重名）。
     - *选项 B*：若同名则更新覆盖旧联系人信息。
     - *选项 C*：提示冲突报错并跳过该行。
3. **标签自定义程度**：
   - 联系方式的 `label`（如“手机”、“工作”、“家庭”）与社交平台的 `platform`（如“微信”、“QQ”）：前端界面是做成纯下拉选择框（Select），还是允许用户手动输入任意自定义标签（Select with create-tag）？
4. **批量删除功能**：
   - 当前已定义单条删除（`DELETE /contacts/{id}`）。前端是否需要批量勾选删除接口（如 `POST /contacts/batch-delete` 传入 `{ ids: [1, 2, 3] }`）？
