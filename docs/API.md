# EE308FZ-AddressBook RESTful API 接口设计草案

> [!WARNING]
> **状态：草案（Draft / Unimplemented）**
> 本文档定义了通讯录系统的后端接口草案。当前阶段后端尚未实现，所有数据结构及接口路径仅作为双人协作开发与前后端对齐的契约参考。

---

## 通用约定

- **基础 URL**：`http://localhost:5000/api/v1`
- **数据格式**：请求体与响应体均采用 `application/json; charset=utf-8`（除文件上传/下载接口外）。
- **统一响应结构**：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

- 常见业务状态码：
  - `200`：请求成功
  - `201`：资源创建成功
  - `400`：请求参数错误
  - `404`：未找到对应资源
  - `500`：服务器内部错误

---

## 接口总览

| 模块 | 方法 | 端点 | 说明 | 实现状态 |
| :--- | :--- | :--- | :--- | :--- |
| **联系人管理** | `GET` | `/contacts` | 获取联系人列表（支持分页、搜索、筛选） | ⏳ 尚未实现 |
| **联系人管理** | `GET` | `/contacts/{id}` | 获取单个联系人详情 | ⏳ 尚未实现 |
| **联系人管理** | `POST` | `/contacts` | 创建新联系人 | ⏳ 尚未实现 |
| **联系人管理** | `PUT` | `/contacts/{id}` | 全量/部分更新联系人信息 | ⏳ 尚未实现 |
| **联系人管理** | `DELETE` | `/contacts/{id}` | 删除指定联系人 | ⏳ 尚未实现 |
| **收藏管理** | `PATCH` | `/contacts/{id}/favorite` | 切换联系人收藏状态 | ⏳ 尚未实现 |
| **数据导入导出** | `GET` | `/contacts/export` | 导出联系人为 Excel 文件 | ⏳ 尚未实现 |
| **数据导入导出** | `POST` | `/contacts/import` | 通过 Excel 批量导入联系人 | ⏳ 尚未实现 |

---

## 接口详细草案

### 1. 获取联系人列表
- **Endpoint**: `GET /api/v1/contacts`
- **Query 参数**：
  - `page` (int, 可选, 默认 1): 当前页码
  - `page_size` (int, 可选, 默认 10): 每页数量
  - `keyword` (string, 可选): 姓名/电话/邮箱模糊搜索关键字
  - `is_favorite` (bool, 可选): 是否仅筛选收藏联系人
  - `group` (string, 可选): 分组筛选（如：家人、朋友、同事）
- **响应示例**：
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
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "address": "福建省福州市大学城",
        "group": "同学",
        "is_favorite": false,
        "created_at": "2026-11-15T12:00:00Z",
        "updated_at": "2026-11-15T12:00:00Z"
      }
    ]
  }
}
```

---

### 2. 获取联系人详情
- **Endpoint**: `GET /api/v1/contacts/{id}`
- **Path 参数**：
  - `id` (int): 联系人唯一 ID
- **响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "address": "福建省福州市大学城",
    "group": "同学",
    "is_favorite": false,
    "created_at": "2026-11-15T12:00:00Z",
    "updated_at": "2026-11-15T12:00:00Z"
  }
}
```

---

### 3. 创建联系人
- **Endpoint**: `POST /api/v1/contacts`
- **请求体 (JSON)**：
```json
{
  "name": "李四",
  "phone": "13900139000",
  "email": "lisi@example.com",
  "address": "福建省福州市鼓楼区",
  "group": "同事",
  "is_favorite": false
}
```
- **响应示例**：
```json
{
  "code": 201,
  "message": "Contact created successfully",
  "data": {
    "id": 2
  }
}
```

---

### 4. 更新联系人
- **Endpoint**: `PUT /api/v1/contacts/{id}`
- **Path 参数**：
  - `id` (int): 联系人唯一 ID
- **请求体 (JSON)**：
```json
{
  "name": "李四",
  "phone": "13911112222",
  "email": "lisi_updated@example.com",
  "address": "福建省福州市旗山校区",
  "group": "好友",
  "is_favorite": true
}
```
- **响应示例**：
```json
{
  "code": 200,
  "message": "Contact updated successfully",
  "data": {
    "id": 2
  }
}
```

---

### 5. 删除联系人
- **Endpoint**: `DELETE /api/v1/contacts/{id}`
- **Path 参数**：
  - `id` (int): 联系人唯一 ID
- **响应示例**：
```json
{
  "code": 200,
  "message": "Contact deleted successfully",
  "data": null
}
```

---

### 6. 切换联系人收藏状态
- **Endpoint**: `PATCH /api/v1/contacts/{id}/favorite`
- **Path 参数**：
  - `id` (int): 联系人唯一 ID
- **请求体 (JSON)**：
```json
{
  "is_favorite": true
}
```
- **响应示例**：
```json
{
  "code": 200,
  "message": "Favorite status updated",
  "data": {
    "id": 2,
    "is_favorite": true
  }
}
```

---

### 7. 导出联系人 (Excel)
- **Endpoint**: `GET /api/v1/contacts/export`
- **Query 参数**：
  - `keyword` (string, 可选): 导出指定搜索结果
  - `group` (string, 可选): 导出指定分组
- **响应头**：
  - `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `Content-Disposition: attachment; filename="contacts_export_20261115.xlsx"`
- **响应体**：二进制 Excel 文件流

---

### 8. 导入联系人 (Excel)
- **Endpoint**: `POST /api/v1/contacts/import`
- **Content-Type**: `multipart/form-data`
- **Form 参数**：
  - `file` (binary): 上传的 `.xlsx` 文件
- **响应示例**：
```json
{
  "code": 200,
  "message": "Import completed successfully",
  "data": {
    "total_rows": 25,
    "success_count": 25,
    "failed_count": 0,
    "errors": []
  }
}
```
