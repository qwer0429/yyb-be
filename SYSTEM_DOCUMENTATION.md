# 医药宝管理系统 - 系统文档

> 文档版本: 1.0  
> 更新日期: 2026-03-24  
> 文档状态: 正式发布

---

## 目录

1. [系统概述](#一系统概述)
2. [技术架构](#二技术架构)
3. [功能模块](#三功能模块)
4. [数据库设计](#四数据库设计)
5. [API接口文档](#五api接口文档)
6. [前端界面](#六前端界面)
7. [部署指南](#七部署指南)
8. [安全规范](#八安全规范)

---

## 一、系统概述

### 1.1 系统简介

**医药宝管理系统** 是一款面向医药行业的专业药品信息管理平台。系统提供完整的药品信息管理、分类管理、生产厂家管理等功能，支持药品数据的批量导入、智能搜索和多维度筛选，旨在帮助医药企业高效管理药品数据资产。

### 1.2 系统定位

- **目标用户**: 医药企业、药品经销商、医疗机构
- **应用场景**: 药品信息管理、药品目录维护、数据统计分析
- **核心价值**: 提升药品数据管理效率，降低人工维护成本

### 1.3 功能特性

| 特性 | 描述 |
|------|------|
| 🔐 用户认证 | 基于JWT的安全认证机制 |
| 📦 药品管理 | 完整的药品CRUD操作，支持Excel批量导入 |
| 🏷️ 分类体系 | 两级分类结构（大类-小类），灵活管理 |
| 🏭 厂商管理 | 持证商与生产商独立管理 |
| 🔍 智能搜索 | 多字段模糊搜索，快速定位药品 |
| 📊 数据统计 | 可视化数据仪表盘 |
| 🖼️ 图片管理 | 支持药品图片上传和展示 |

---

## 二、技术架构

### 2.1 技术栈概览

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Vue 3     │  │  TypeScript │  │    Element Plus     │  │
│  │  (框架)     │  │  (类型系统)  │  │    (UI组件库)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Pinia    │  │  Vue Router │  │       Axios         │  │
│  │  (状态管理)  │  │   (路由)     │  │    (HTTP客户端)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                        后端层 (Backend)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Django   │  │     DRF     │  │    JWT Auth         │  │
│  │  (Web框架)   │  │  (REST框架)  │  │   (认证)             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐
│      数据层 (Data)           │  │      缓存层 (Cache)          │
│  ┌─────────────────────┐    │  │  ┌─────────────────────┐    │
│  │       MySQL         │    │  │ │       Redis         │    │
│  │    (关系型数据库)     │    │  │  │    (内存缓存)        │    │
│  └─────────────────────┘    │  │  └─────────────────────┘    │
└─────────────────────────────┘  └─────────────────────────────┘
```

### 2.2 后端技术详情

| 技术组件 | 版本 | 用途 |
|---------|------|------|
| Python | 3.9+ | 编程语言 |
| Django | 4.x | Web框架 |
| Django REST Framework | 3.14+ | REST API开发 |
| djangorestframework-simplejwt | 5.x | JWT认证 |
| MySQL | 8.0+ | 主数据库 |
| Redis | 6.x+ | 缓存、Session存储 |
| openpyxl | 3.x | Excel文件处理 |

### 2.3 前端技术详情

| 技术组件 | 版本 | 用途 |
|---------|------|------|
| Vue | 3.3+ | 前端框架 |
| TypeScript | 5.x | 类型安全 |
| Element Plus | 2.4+ | UI组件库 |
| Pinia | 2.1+ | 状态管理 |
| Vue Router | 4.x | 路由管理 |
| Axios | 1.6+ | HTTP请求 |
| ECharts | 5.x | 数据可视化 |

### 2.4 项目目录结构

```
yyb-be/                         # 项目根目录
├── README.md                   # 项目说明
├── SYSTEM_DOCUMENTATION.md     # 系统文档（本文档）
├── start.bat                   # Windows启动脚本
├── start-backend.ps1           # 后端启动脚本
├── start-frontend.ps1          # 前端启动脚本
├── django/                     # 后端Django项目
│   ├── manage.py               # Django管理脚本
│   ├── susers/                 # 用户管理应用
│   │   ├── models.py           # User模型
│   │   ├── views.py            # 用户相关视图
│   │   └── urls.py             # 用户模块路由
│   ├── syyb/                   # 药品管理应用
│   │   ├── models.py           # 药品相关模型
│   │   ├── views.py            # 药品相关视图
│   │   ├── serializers.py      # 序列化器
│   │   ├── urls.py             # 药品模块路由
│   │   └── utils.py            # 工具函数
│   └── yyb/                    # 项目配置
│       ├── settings.py         # 全局配置
│       ├── urls.py             # 根路由配置
│       └── wsgi.py             # WSGI配置
└── web/                        # 前端Vue项目
    ├── package.json            # 依赖配置
    ├── vite.config.ts          # Vite构建配置
    ├── tsconfig.json           # TypeScript配置
    ├── index.html              # 入口HTML
    └── src/                    # 源代码目录
        ├── main.ts             # 应用入口
        ├── App.vue             # 根组件
        ├── router/             # 路由配置
        ├── stores/             # Pinia状态管理
        ├── views/              # 页面视图
        ├── components/         # 公共组件
        ├── api/                # API接口封装
        ├── types/              # TypeScript类型定义
        └── assets/             # 静态资源
```

---

## 三、功能模块

### 3.1 用户认证模块

#### 功能描述
- 用户登录（JWT Token认证）
- Token自动刷新
- 用户信息获取
- 权限控制

#### 认证流程
```
┌─────────┐     登录请求      ┌─────────┐
│  用户   │ ───────────────> │  后端   │
│ (前端)  │                  │ (Django)│
└─────────┘                  └────┬────┘
     │                            │
     │      返回Access+Refresh    │
     │ <────────────────────────  │
     │                            │
     │      后续请求(带Token)     │
     │ ─────────────────────────> │
     │                            │
     │         返回数据           │
     │ <────────────────────────  │
```

### 3.2 药品管理模块

#### 核心功能

| 功能 | 描述 |
|------|------|
| 药品列表 | 分页展示药品信息，支持排序和筛选 |
| 新增药品 | 填写药品详细信息，上传药品图片 |
| 编辑药品 | 修改药品信息，更新图片 |
| 删除药品 | 单条删除或批量删除 |
| Excel导入 | 批量导入药品数据 |
| 药品搜索 | 多字段模糊搜索 |

#### 药品信息字段

**基本信息：**
- 药品名称、英文名称
- 商品名、英文商品名
- 药品图片

**分类信息：**
- 一级分类（如：化学药品、中成药等）
- 二级分类（如：抗生素、解热镇痛药等）

**规格信息：**
- 规格、剂型
- 给药途径

**厂商信息：**
- 上市许可持有人（持证商）
- 生产企业

**药品属性：**
- 活性成分、英文活性成分
- 批准文号、批准日期
- ATC编码（唯一）
- 市场状态
- 医保类型
- 是否热门
- 家庭常备
- 京东链接

### 3.3 分类管理模块

#### 两级分类体系

```
一级分类 (Type1Drug)
    ├── 化学药品
    │       ├── 抗生素
    │       ├── 解热镇痛药
    │       └── ...
    ├── 中成药
    │       ├── 内科用药
    │       ├── 外科用药
    │       └── ...
    └── 生物制品
            ├── 疫苗
            ├── 血液制品
            └── ...
```

#### 功能
- 一级分类CRUD
- 二级分类CRUD
- 分类关联管理

### 3.4 厂商管理模块

#### 两个独立实体

| 实体 | 描述 |
|------|------|
| **上市许可持有人** (ManufacturerHolder) | 持有药品上市许可的企业 |
| **生产企业** (Manufacturer) | 实际生产药品的企业 |

#### 功能
- 持证商CRUD（名称、简称）
- 生产商CRUD（名称、简称）

---

## 四、数据库设计

### 4.1 实体关系图 (ER Diagram)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    User         │     │     Drug        │     │   Type2Drug     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │◄────┤ id (PK)         │
│ username        │     │ drug_name       │     │ name            │
│ password        │     │ drug_name_en    │     │ type1_drug(FK)  │────┐
│ mobile          │     │ trade_name      │     └─────────────────┘    │
│ name            │     │ trade_name_en   │                            │
│ birthday        │     │ type2_drug(FK)  │                            │
│ sex             │     │ manufacturer(FK)│                            │
└─────────────────┘     │ manufacturer_   │     ┌─────────────────┐    │
                        │    holder(FK)   │     │   Type1Drug     │◄───┘
                        │ atc_code(UQ)    │     ├─────────────────┤
                        │ ...             │     │ id (PK)         │
                        └─────────────────┘     │ name (unique)   │
                               │                └─────────────────┘
                               ▼
              ┌────────────────────────────────┐
              │         Manufacturer           │
              ├────────────────────────────────┤
              │ id (PK)                        │
              │ name (unique)                  │
              │ abbreviation                   │
              └────────────────────────────────┘

              ┌────────────────────────────────┐
              │     ManufacturerHolder         │
              ├────────────────────────────────┤
              │ id (PK)                        │
              │ name (unique)                  │
              │ abbreviation                   │
              └────────────────────────────────┘
```

### 4.2 数据表结构

#### 4.2.1 User 表 (susers_user)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| username | VARCHAR(150) | Unique, Not Null | 用户名 |
| password | VARCHAR(128) | Not Null | 密码（加密存储） |
| mobile | VARCHAR(11) | - | 手机号 |
| name | VARCHAR(50) | - | 真实姓名 |
| birthday | DATE | - | 生日 |
| sex | VARCHAR(10) | - | 性别 |
| is_active | BOOLEAN | Default=True | 是否激活 |
| date_joined | DATETIME | Auto | 注册时间 |

#### 4.2.2 Drug 表 (syyb_drug)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| drug_name | VARCHAR(255) | Not Null | 药品名称 |
| drug_name_en | VARCHAR(255) | - | 英文名称 |
| trade_name | VARCHAR(255) | - | 商品名 |
| trade_name_en | VARCHAR(255) | - | 英文商品名 |
| category | VARCHAR(255) | - | 分类（冗余字段） |
| is_hot | BOOLEAN | Default=False | 是否热门 |
| family_use | BOOLEAN | Default=False | 家庭常备 |
| medical_insurance | VARCHAR(50) | - | 医保类型 |
| jd_url | VARCHAR(500) | - | 京东链接 |
| type2_drug_id | INT | FK | 二级分类外键 |
| specification | VARCHAR(255) | - | 规格 |
| dosage_form | VARCHAR(100) | - | 剂型 |
| administration_route | VARCHAR(100) | - | 给药途径 |
| manufacturer_holder_id | INT | FK | 持证商外键 |
| manufacturer_id | INT | FK | 生产商外键 |
| active_ingredient | TEXT | - | 活性成分 |
| active_ingredient_en | TEXT | - | 英文活性成分 |
| approval_number | VARCHAR(100) | - | 批准文号 |
| approval_date | DATE | - | 批准日期 |
| atc_code | VARCHAR(20) | Unique | ATC编码 |
| market_status | VARCHAR(50) | - | 市场状态 |
| drug_image | VARCHAR(500) | - | 药品图片URL |
| created_at | DATETIME | Auto | 创建时间 |
| updated_at | DATETIME | Auto | 更新时间 |

#### 4.2.3 Type1Drug 表 (syyb_type1drug)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| name | VARCHAR(100) | Unique, Not Null | 分类名称 |
| created_at | DATETIME | Auto | 创建时间 |

#### 4.2.4 Type2Drug 表 (syyb_type2drug)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| name | VARCHAR(100) | Not Null | 分类名称 |
| type1_drug_id | INT | FK, Not Null | 一级分类外键 |
| created_at | DATETIME | Auto | 创建时间 |

#### 4.2.5 ManufacturerHolder 表 (syyb_manufacturerholder)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| name | VARCHAR(255) | Unique, Not Null | 持证商名称 |
| abbreviation | VARCHAR(100) | - | 简称 |
| created_at | DATETIME | Auto | 创建时间 |

#### 4.2.6 Manufacturer 表 (syyb_manufacturer)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| name | VARCHAR(255) | Unique, Not Null | 生产商名称 |
| abbreviation | VARCHAR(100) | - | 简称 |
| created_at | DATETIME | Auto | 创建时间 |

---

## 五、API接口文档

### 5.1 接口规范

- **基础URL**: `http://localhost:8000`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: JWT Bearer Token

### 5.2 认证接口

#### 5.2.1 用户登录

```http
POST /api/token/
Content-Type: application/json

{
    "username": "admin",
    "password": "password123"
}
```

**响应示例：**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 5.2.2 刷新Token

```http
POST /api/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**响应示例：**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 5.3 药品接口

#### 5.3.1 获取药品列表

```http
GET /syyb/drug/?page=1&page_size=10&ordering=-created_at
Authorization: Bearer <access_token>
```

**查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| page | INT | 页码，默认1 |
| page_size | INT | 每页数量，默认10 |
| ordering | STRING | 排序字段，前缀`-`表示倒序 |
| type2_drug | INT | 按二级分类筛选 |
| manufacturer | INT | 按生产商筛选 |
| is_hot | BOOL | 按热门筛选 |
| medical_insurance | STRING | 按医保类型筛选 |

**响应示例：**
```json
{
    "count": 100,
    "next": "http://localhost:8000/syyb/drug/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "drug_name": "阿莫西林胶囊",
            "drug_name_en": "Amoxicillin Capsules",
            "trade_name": "阿莫仙",
            "type2_drug": {"id": 1, "name": "抗生素", "type1_drug": {"id": 1, "name": "化学药品"}},
            "manufacturer": {"id": 1, "name": "华北制药", "abbreviation": "HBZY"},
            "manufacturer_holder": {"id": 1, "name": "华北制药集团", "abbreviation": "HBZYJT"},
            "atc_code": "J01CA04",
            "market_status": "上市",
            "is_hot": true,
            "drug_image": "/media/drugs/amoxicillin.jpg",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### 5.3.2 获取单个药品

```http
GET /syyb/drug/{id}/
Authorization: Bearer <access_token>
```

#### 5.3.3 创建药品

```http
POST /syyb/drug/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "drug_name": "阿莫西林胶囊",
    "drug_name_en": "Amoxicillin Capsules",
    "trade_name": "阿莫仙",
    "type2_drug": 1,
    "specification": "0.25g*24粒",
    "dosage_form": "胶囊剂",
    "administration_route": "口服",
    "manufacturer_holder": 1,
    "manufacturer": 1,
    "active_ingredient": "阿莫西林",
    "approval_number": "国药准字H13020726",
    "atc_code": "J01CA04",
    "market_status": "上市",
    "medical_insurance": "甲类",
    "is_hot": true,
    "family_use": false
}
```

#### 5.3.4 更新药品

```http
PUT /syyb/drug/{id}/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "drug_name": "阿莫西林胶囊",
    "drug_name_en": "Amoxicillin Capsules",
    ...
}
```

#### 5.3.5 部分更新药品

```http
PATCH /syyb/drug/{id}/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "is_hot": false
}
```

#### 5.3.6 删除药品

```http
DELETE /syyb/drug/{id}/
Authorization: Bearer <access_token>
```

#### 5.3.7 批量删除药品

```http
POST /syyb/batch_delete_drugs/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "ids": [1, 2, 3, 4, 5]
}
```

**响应示例：**
```json
{
    "deleted": 5,
    "message": "成功删除5条记录"
}
```

#### 5.3.8 搜索药品

```http
GET /syyb/search_anything/?keyword=阿莫西林&page=1&page_size=10
Authorization: Bearer <access_token>
```

**查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | STRING | 搜索关键词 |
| page | INT | 页码 |
| page_size | INT | 每页数量 |

**搜索范围：**
- 药品名称（drug_name）
- 英文名称（drug_name_en）
- 商品名（trade_name）
- 英文商品名（trade_name_en）
- ATC编码（atc_code）
- 批准文号（approval_number）

#### 5.3.9 Excel导入药品

```http
POST /syyb/add_drugs_from_excel/
Content-Type: multipart/form-data
Authorization: Bearer <access_token>

file: <Excel文件>
```

**Excel模板字段：**

| 字段名 | 必填 | 说明 |
|--------|------|------|
| 药品名称 | 是 | - |
| 英文名称 | 否 | - |
| 商品名 | 否 | - |
| 一级分类 | 是 | 必须已存在 |
| 二级分类 | 是 | 必须已存在 |
| 规格 | 否 | - |
| 剂型 | 否 | - |
| 给药途径 | 否 | - |
| 持证商 | 否 | 必须已存在 |
| 生产商 | 否 | 必须已存在 |
| 活性成分 | 否 | - |
| 批准文号 | 否 | - |
| 批准日期 | 否 | 格式：YYYY-MM-DD |
| ATC编码 | 否 | 唯一 |
| 市场状态 | 否 | - |
| 医保类型 | 否 | - |
| 是否热门 | 否 | 是/否 |
| 家庭常备 | 否 | 是/否 |
| 京东链接 | 否 | - |

**响应示例：**
```json
{
    "success": 100,
    "failed": 5,
    "errors": [
        {"row": 3, "error": "ATC编码已存在"},
        {"row": 10, "error": "一级分类不存在"}
    ]
}
```

### 5.4 分类接口

#### 5.4.1 一级分类

| 方法 | 接口 | 说明 |
|------|------|------|
| GET | /syyb/type1drug/ | 获取列表 |
| POST | /syyb/type1drug/ | 创建分类 |
| PUT | /syyb/type1drug/{id}/ | 更新分类 |
| DELETE | /syyb/type1drug/{id}/ | 删除分类 |

#### 5.4.2 二级分类

| 方法 | 接口 | 说明 |
|------|------|------|
| GET | /syyb/type2drug/ | 获取列表 |
| POST | /syyb/type2drug/ | 创建分类 |
| PUT | /syyb/type2drug/{id}/ | 更新分类 |
| DELETE | /syyb/type2drug/{id}/ | 删除分类 |

### 5.5 厂商接口

| 方法 | 接口 | 说明 |
|------|------|------|
| GET | /syyb/manufacturerholder/ | 获取持证商列表 |
| POST | /syyb/manufacturerholder/ | 创建持证商 |
| GET | /syyb/manufacturer/ | 获取生产商列表 |
| POST | /syyb/manufacturer/ | 创建生产商 |

---

## 六、前端界面

### 6.1 页面清单

| 页面 | 路由 | 功能描述 |
|------|------|----------|
| 登录页 | /login | 用户登录 |
| 首页 | / | 数据仪表盘 |
| 药品列表 | /drugs | 药品管理 |
| 分类管理 | /categories | 两级分类管理 |
| 厂商管理 | /manufacturers | 持证商和生产商管理 |

### 6.2 主要组件

- 数据表格（Element Plus Table）
- 分页组件
- 搜索框和高级筛选
- 表单对话框
- 图片上传组件
- 级联选择器

---

## 七、部署指南

### 7.1 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.9+ |
| Node.js | 18+ |
| MySQL | 8.0+ |
| Redis | 6.0+ |

### 7.2 后端部署步骤

1. 创建虚拟环境
2. 安装依赖: `pip install -r requirements.txt`
3. 配置数据库连接
4. 执行迁移: `python manage.py migrate`
5. 创建超级用户: `python manage.py createsuperuser`
6. 启动服务: `python manage.py runserver`

### 7.3 前端部署步骤

1. 安装依赖: `npm install`
2. 配置API地址
3. 开发模式: `npm run dev`
4. 生产构建: `npm run build`

### 7.4 生产环境部署

推荐使用 Gunicorn + Nginx 部署后端，Nginx 托管前端静态文件。

---

## 八、安全规范

### 8.1 认证安全

- 使用 HTTPS 传输
- JWT Token 设置合理过期时间
- 密码使用 PBKDF2 加密

### 8.2 数据安全

- 敏感信息使用环境变量
- 定期备份数据库
- 文件上传类型白名单
- 使用ORM防止SQL注入

### 8.3 API安全

- 接口权限控制
- 请求频率限制
- CORS 白名单配置

---

## 附录

### A. 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-03-24 | 初始版本发布 |

### B. 项目信息

- 文档版本: 1.0
- 更新日期: 2026-03-24

---

*文档结束 - 医药宝管理系统*
