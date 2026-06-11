# 医药宝管理系统 — 详细说明文档

> **文档版本**: v2.0 | **更新日期**: 2026-06-11 | **文档状态**: 正式发布

---

## 目录

1. [系统概述](#一系统概述)
2. [系统架构设计](#二系统架构设计)
3. [技术栈详解](#三技术栈详解)
4. [数据库设计](#四数据库设计)
5. [后端详细设计](#五后端详细设计)
6. [前端详细设计](#六前端详细设计)
7. [功能模块详解](#七功能模块详解)
8. [API接口规范](#八api接口规范)
9. [认证与权限系统](#九认证与权限系统)
10. [部署与运维指南](#十部署与运维指南)
11. [安全架构](#十一安全架构)
12. [性能优化策略](#十二性能优化策略)
13. [项目目录结构](#十三项目目录结构)
14. [附录](#十四附录)

---

## 一、系统概述

### 1.1 系统简介

**医药宝管理系统**是一款面向医药行业的企业级药品信息管理平台，采用前后端分离架构设计。系统包含**后台管理系统**（管理员端）和**用户端系统**（普通用户端）两套独立前端，通过统一的 REST API 后端服务进行数据交互。

系统核心功能涵盖：
- 完整的药品信息生命周期管理（增删改查、批量导入）
- 两级分类体系维护（一级分类 → 二级分类 → 药品）
- 厂商信息独立管理（上市许可持有人与生产厂商分离）
- 智慧药箱功能（个人药品库存管理、有效期提醒）
- 智能医生问答（通过 iframe 集成 FastGPT AI 服务）
- 多维度药品搜索与筛选

### 1.2 系统定位

| 维度 | 说明 |
|------|------|
| **目标用户** | 医药企业管理人员、药品经销商、医疗机构、普通消费者 |
| **应用场景** | 药品目录维护、库存管理、药品信息查询、用药指导 |
| **核心价值** | 提升药品数据管理效率，降低人工维护成本，保障用药安全 |

### 1.3 系统特点

| 特性 | 说明 |
|------|------|
| 🔐 安全认证 | 基于 JWT 的双 Token 认证机制，支持 Access Token 自动刷新 |
| 📦 数据管理 | 完整的 CRUD 操作，支持 Excel 批量导入和批量删除 |
| 🔍 智能搜索 | 多字段模糊搜索，支持药品名、商品名、厂商等多维度检索 |
| 🖼️ 图片管理 | 支持药品图片上传和预览 |
| 📱 响应式设计 | 现代化 UI 界面，基于 Element Plus 组件库 |
| 🏗️ 分级架构 | 两级分类体系，清晰的数据组织结构 |
| 💊 智慧药箱 | 个人药品库存管理，自动过期提醒 |
| 🤖 AI 集成 | 集成智能医生问答功能 |

### 1.4 用户角色

| 角色 | 说明 | 可访问系统 |
|------|------|-----------|
| **超级管理员** | 系统最高权限，可管理所有数据和用户 | 后台管理系统 + 用户端系统 |
| **管理员** | 拥有药品管理、分类管理、厂商管理、用户管理权限 | 后台管理系统 + 用户端系统 |
| **普通用户** | 可浏览药品信息，管理个人药箱 | 用户端系统 |

---

## 二、系统架构设计

### 2.1 总体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           客户端层 (Client Layer)                            │
│  ┌─────────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │     后台管理系统              │    │          用户端系统                  │ │
│  │     (web/)                  │    │          (user_web/)                 │ │
│  │  • Vue 3 + TypeScript       │    │  • Vue 3 + TypeScript                │ │
│  │  • Element Plus UI          │    │  • Element Plus UI                   │ │
│  │  • Pinia 状态管理            │    │  • Pinia 状态管理                    │ │
│  │  • Vue Router 路由           │    │  • Vue Router 路由                   │ │
│  │  • Axios HTTP请求            │    │  • Axios HTTP请求                    │ │
│  │  • 端口: 5173               │    │  • 端口: 3001                        │ │
│  └──────────────┬──────────────┘    └──────────────────┬──────────────────┘ │
└─────────────────┼──────────────────────────────────────┼────────────────────┘
                  │                                      │
                  └──────────────────┬───────────────────┘
                                     │ HTTP/REST API
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           网关层 (Gateway Layer)                             │
│                    Nginx / 开发环境直接访问                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           后端层 (Backend Layer)                             │
│                           (django/)                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Django 6.0.3                                 │   │
│  │                    (Python Web 框架)                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  Django REST     │  │  JWT 认证        │  │  Django ORM             │  │
│  │  Framework 3.17  │  │  SimpleJWT 5.5.1 │  │  (数据库操作)            │  │
│  │  (REST API)      │  │  (Token认证)     │  │                          │  │
│  └────────┬─────────┘  └──────────────────┘  └────────────┬─────────────┘  │
│           │                                               │                │
│  ┌────────▼───────────────────────────────────────────────▼────────────┐   │
│  │                                                                     │   │
│  │   ┌──────────────┐              ┌──────────────┐                   │   │
│  │   │    MySQL     │              │    Redis     │                   │   │
│  │   │   (主数据库)  │              │   (缓存)      │                   │   │
│  │   │   端口: 3306 │              │   端口: 6379 │                   │   │
│  │   └──────────────┘              └──────────────┘                   │   │
│  │                                                                     │   │
│  │   ┌──────────────────────────────────────────────────────────┐    │   │
│  │   │              媒体文件存储 (Media Files)                    │    │   │
│  │   │         (药品图片等上传文件)                               │    │   │
│  │   └──────────────────────────────────────────────────────────┘    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                              端口: 8000                                    │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           外部服务 (External Services)                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     FastGPT / AI 问答服务                            │   │
│  │              (智能医生功能，通过 iframe 集成)                          │   │
│  │                        地址: http://192.168.50.20:3020               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 架构分层说明

| 层级 | 组件 | 职责 |
|------|------|------|
| **客户端层** | 后台管理系统 (web)、用户端系统 (user_web) | 用户界面展示、用户交互处理 |
| **网关层** | Nginx (生产) / Vite Dev Server (开发) | 请求路由、负载均衡、静态文件服务 |
| **后端层** | Django + DRF | 业务逻辑处理、数据校验、权限控制 |
| **数据层** | MySQL 8.0+ | 持久化数据存储 |
| **缓存层** | Redis 6.0+ | 会话缓存、热点数据缓存 |
| **外部服务** | FastGPT | AI 智能问答服务 |

---

## 三、技术栈详解

### 3.1 后端技术栈

| 技术组件 | 版本 | 用途说明 | 选择理由 |
|----------|------|----------|----------|
| **Python** | 3.12 | 编程语言 | 语法简洁，生态丰富，适合快速开发 |
| **Django** | 6.0.3 | Web 应用主框架 | 内置 ORM、Admin、认证，开发效率高 |
| **Django REST Framework** | 3.17.0 | RESTful API 开发 | 完整的 REST 支持，序列化器强大 |
| **djangorestframework-simplejwt** | 5.5.1 | JWT 认证实现 | 无状态认证，适合前后端分离 |
| **MySQL** | 8.0+ | 关系型数据库 | 成熟稳定，性能好，便于维护 |
| **Redis** | 6.0+ | 缓存与会话存储 | 高性能缓存，支持多种数据结构 |
| **django-redis** | 6.0.0 | Django Redis 集成 | 方便的缓存后端配置 |
| **django-cors-headers** | 4.9.0 | 跨域处理 | 解决前后端分离的跨域问题 |
| **django-filter** | 25.2 | 高级过滤 | 支持复杂查询过滤 |
| **django-guardian** | 3.3.0 | 对象级权限 | 细粒度的权限控制 |
| **django-haystack** | 3.3.0 | 全文搜索框架 | 统一的搜索接口，支持多种搜索引擎 |
| **Whoosh** | 2.7.4 | 本地全文搜索引擎 | 无需额外服务，适合中小型项目 |
| **Pandas** | 3.0.1 | Excel 数据处理 | 强大的数据处理能力 |
| **openpyxl** | 3.1.5 | Excel 文件读写 | 读写 .xlsx 格式 |
| **Pillow** | 12.1.1 | 图片处理 | 图片上传、压缩、格式转换 |
| **pycryptodome** | 3.23.0 | 加密算法 | RSA + AES 混合加密 |
| **PyYAML** | 6.0.3 | YAML 配置解析 | 配置文件管理 |
| **gunicorn** | 25.1.0 | WSGI HTTP 服务器 | 生产环境部署 |

### 3.2 前端技术栈

#### 3.2.1 后台管理系统 (web/)

| 技术组件 | 版本 | 用途说明 |
|----------|------|----------|
| **Vue** | 3.5.25 | 渐进式 JavaScript 框架 |
| **TypeScript** | 5.9.3 | 类型安全的 JavaScript 超集 |
| **Element Plus** | 2.13.2 | UI 组件库 |
| **Pinia** | 3.0.4 | 状态管理 |
| **Vue Router** | 5.0.2 | 路由管理 |
| **Axios** | 1.13.5 | HTTP 客户端 |
| **Vite** | 8.0.0-beta.13 | 构建工具 |
| **crypto-js** | 4.2.0 | 前端加密（RSA + AES） |
| **@element-plus/icons-vue** | 2.3.2 | Element Plus 图标库 |

#### 3.2.2 用户端系统 (user_web/)

| 技术组件 | 版本 | 用途说明 |
|----------|------|----------|
| **Vue** | 3.4.0 | 渐进式 JavaScript 框架 |
| **TypeScript** | 5.3.0 | 类型安全的 JavaScript 超集 |
| **Element Plus** | 2.5.0 | UI 组件库 |
| **Pinia** | 2.1.7 | 状态管理 |
| **Vue Router** | 4.2.5 | 路由管理 |
| **Axios** | 1.6.0 | HTTP 客户端 |
| **Vite** | 5.0.0 | 构建工具 |
| **crypto-js** | 4.2.0 | 前端加密 |
| **@element-plus/icons-vue** | 2.3.1 | Element Plus 图标库 |

### 3.3 技术选型理由

#### 为什么选择 Django + DRF？

| 优势 | 说明 |
|------|------|
| **快速开发** | 内置 ORM、Admin、认证等，开发效率高 |
| **RESTful** | DRF 提供完整的 REST API 支持 |
| **安全性** | 内置防护 SQL 注入、XSS、CSRF 等 |
| **扩展性** | 丰富的第三方库生态 |
| **Python 生态** | 便于集成数据分析（Pandas）和 AI 功能 |

#### 为什么选择 Vue 3？

| 优势 | 说明 |
|------|------|
| **响应式** | Composition API，更好的代码组织 |
| **TypeScript** | 类型安全，IDE 支持好 |
| **性能** | 虚拟 DOM 优化，加载速度快 |
| **生态** | Element Plus 组件丰富 |
| **工程化** | Vite 构建工具，开发体验好 |

#### 为什么选择 MySQL + Redis？

| 组件 | 用途 | 理由 |
|------|------|------|
| **MySQL** | 主数据库 | 成熟稳定、性能好、便于维护 |
| **Redis** | 缓存 | 高性能缓存、Session 存储 |

---

## 四、数据库设计

### 4.1 实体关系图 (ER Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据库关系图                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐         ┌──────────────┐                                │
│   │  susers_user │         │syyb_type1drug│                                │
│   │   (用户表)    │         │  (一级分类)   │                                │
│   └──────┬───────┘         └──────┬───────┘                                │
│          │                        │                                         │
│          │                        │ 1:N                                     │
│          │                        ▼                                         │
│          │               ┌──────────────┐                                  │
│          │               │syyb_type2drug│                                  │
│          │               │  (二级分类)   │                                  │
│          │               └──────┬───────┘                                  │
│          │                      │ 1:N                                       │
│          │                      ▼                                          │
│          │               ┌──────────────┐                                  │
│          │               │   syyb_drug  │                                  │
│          │               │   (药品表)    │                                  │
│          │               └──────┬───────┘                                  │
│          │                      │                                          │
│          │         ┌────────────┼────────────┐                            │
│          │         │            │            │                            │
│          │         N:1         N:1         N:1                            │
│          │         │            │            │                            │
│          │    ┌────▼────┐ ┌────▼────┐ ┌────▼────┐                       │
│          │    │manufact-│ │manufact-│ │type2drug│                       │
│          │    │  urer   │ │holder   │ │         │                       │
│          │    │(生产厂商)│ │(持有人)  │ │(二级分类)│                       │
│          │    └─────────┘ └─────────┘ └─────────┘                       │
│          │                                                                │
│          │ 1:N                                                            │
│          ▼                                                                │
│   ┌──────────────┐         ┌──────────────┐                              │
│   │syyb_medicine │  1:N    │syyb_cabinet  │                              │
│   │   cabinet    │────────▶│    drug      │                              │
│   │   (药箱表)    │         │ (药箱药品)    │                              │
│   └──────────────┘         └──────┬───────┘                              │
│                                   │ N:1                                   │
│                                   ▼                                       │
│                            ┌──────────────┐                              │
│                            │   syyb_drug  │                              │
│                            │   (药品表)    │                              │
│                            └──────────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 数据表结构

#### 4.2.1 User 表 (susers_user)

继承自 Django 的 AbstractUser，扩展了以下字段：

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| username | VARCHAR(150) | Unique, Not Null | 用户名 |
| password | VARCHAR(128) | Not Null | 密码（PBKDF2 加密） |
| mobile | VARCHAR(100) | Unique, Nullable | 手机号 |
| name | VARCHAR(150) | Nullable | 真实姓名 |
| birthday | DATE | Nullable | 生日 |
| sex | INT | Default=1 | 性别（1男/2女/3保密） |
| is_admin | BOOLEAN | Default=False | 是否管理员 |
| is_active | BOOLEAN | Default=True | 是否启用 |
| is_staff | BOOLEAN | Default=False | 是否 staff |
| need_reset | BOOLEAN | Default=False | 是否需要重置密码 |
| is_default_password | BOOLEAN | Default=False | 是否默认密码 |
| permissions | JSON | Default=list | 可访问系统权限列表 |
| date_joined | DATETIME | Auto | 注册时间 |
| last_login | DATETIME | Nullable | 最后登录时间 |

**特殊方法：**
- `get_accessible_systems()`: 获取用户可访问的系统列表，管理员自动包含 `admin_system`

#### 4.2.2 Drug 表 (syyb_drug)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| drug_name | VARCHAR(255) | Not Null | 药品名称 |
| drug_name_en | VARCHAR(255) | Nullable | 英文名称 |
| trade_name | VARCHAR(255) | Nullable | 商品名 |
| trade_name_en | VARCHAR(255) | Nullable | 英文商品名 |
| category | VARCHAR(255) | Nullable | 收录类别（冗余字段） |
| is_hot | BOOLEAN | Default=False | 是否热门 |
| family_use | VARCHAR(100) | Nullable | 家庭常用清单分类 |
| medical_insurance | VARCHAR(255) | Nullable | 医保类型 |
| jd_url | TEXT | Nullable | 京东链接 |
| type2_drug_id | INT | FK → Type2Drug | 二级分类外键 |
| specification | VARCHAR(255) | Nullable | 规格 |
| dosage_form | VARCHAR(100) | Nullable | 剂型 |
| administration_route | VARCHAR(100) | Nullable | 给药途径 |
| manufacturer_holder_id | INT | FK → ManufacturerHolder | 持证商外键 |
| manufacturer_id | INT | FK → Manufacturer | 生产商外键 |
| active_ingredient | VARCHAR(255) | Nullable | 活性成分 |
| active_ingredient_en | VARCHAR(1000) | Nullable | 英文活性成分 |
| approval_number | VARCHAR(100) | Nullable | 批准文号 |
| approval_date | DATE | Nullable | 批准日期 |
| atc_code | VARCHAR(50) | Unique, Nullable | ATC 编码 |
| market_status | VARCHAR(100) | Nullable | 市场状态 |
| drug_image | VARCHAR(500) | Nullable | 药品图片 URL |
| description | TEXT | Nullable | 药品说明 |
| indications | TEXT | Nullable | 适用症状 |
| created_at | DATETIME | Auto | 创建时间 |
| updated_at | DATETIME | Auto | 更新时间 |

**数据库索引：**
```python
indexes = [
    models.Index(fields=['drug_name'], name='idx_drug_name'),
    models.Index(fields=['trade_name'], name='idx_trade_name'),
    models.Index(fields=['atc_code'], name='idx_atc_code'),
    models.Index(fields=['is_hot'], name='idx_is_hot'),
    models.Index(fields=['type2_drug'], name='idx_type2_drug'),
]
```

#### 4.2.3 Type1Drug 表 (syyb_type1drug) — 一级分类

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| name | VARCHAR(255) | Unique, Not Null | 分类名称 |

#### 4.2.4 Type2Drug 表 (syyb_type2drug) — 二级分类

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| name | VARCHAR(255) | Not Null | 分类名称 |
| type1_drug_id | INT | FK, Not Null | 所属一级分类 |

**联合唯一约束：** `(name, type1_drug)`

#### 4.2.5 ManufacturerHolder 表 (syyb_manufacturerholder) — 上市许可持有人

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| name | VARCHAR(255) | Unique, Not Null | 持有人全称 |
| abbreviation | VARCHAR(100) | Nullable | 简称 |

#### 4.2.6 Manufacturer 表 (syyb_manufacturer) — 生产厂商

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| name | VARCHAR(255) | Unique, Not Null | 厂商全称 |
| abbreviation | VARCHAR(100) | Nullable | 简称 |

#### 4.2.7 MedicineCabinet 表 (syyb_medicinecabinet) — 药箱

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| user_id | INT | FK → User, Not Null | 所属用户 |
| name | VARCHAR(100) | Not Null | 药箱名称 |
| cabinet_type | VARCHAR(20) | Default='home' | 药箱类型 |
| description | TEXT | Nullable | 药箱描述 |
| is_default | BOOLEAN | Default=False | 是否默认药箱 |
| created_at | DATETIME | Auto | 创建时间 |
| updated_at | DATETIME | Auto | 更新时间 |

**约束：** 每个用户的默认药箱只能有一个（`unique_default_cabinet_per_user`）

**药箱类型选项：**
- `home` — 家庭药箱
- `travel` — 旅行药箱
- `office` — 办公室药箱
- `other` — 其他

#### 4.2.8 CabinetDrug 表 (syyb_cabinetdrug) — 药箱药品关系

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, Auto | 主键 |
| cabinet_id | INT | FK → MedicineCabinet | 所属药箱 |
| drug_id | INT | FK → Drug | 药品 |
| quantity | INT | Default=1 | 数量 |
| unit | VARCHAR(50) | Nullable | 单位 |
| production_date | DATE | Nullable | 生产日期 |
| valid_until | DATE | Nullable | 有效期至 |
| batch_number | VARCHAR(100) | Nullable | 批号 |
| remind_before_days | INT | Default=7 | 过期前提醒天数 |
| is_reminded | BOOLEAN | Default=False | 是否已提醒 |
| notes | TEXT | Nullable | 备注 |
| added_at | DATETIME | Auto | 添加时间 |
| updated_at | DATETIME | Auto | 更新时间 |

**业务方法：**
- `is_expired()`: 检查药品是否已过期
- `is_expiring_soon()`: 检查药品是否即将过期（按 `remind_before_days`）
- `days_until_expiry()`: 返回距离过期还有多少天

**数据库索引：**
```python
indexes = [
    models.Index(fields=['cabinet', 'drug'], name='idx_cabinet_drug'),
    models.Index(fields=['valid_until'], name='idx_valid_until'),
    models.Index(fields=['cabinet', 'valid_until'], name='idx_cabinet_valid'),
]
```

### 4.3 关键字段约束汇总

| 表名 | 字段 | 约束类型 | 说明 |
|------|------|----------|------|
| susers_user | username | UNIQUE | 用户名唯一 |
| susers_user | mobile | UNIQUE | 手机号唯一 |
| syyb_type1drug | name | UNIQUE | 一级分类名称唯一 |
| syyb_type2drug | name + type1_drug | UNIQUE together | 同一一级分类下二级分类名称唯一 |
| syyb_manufacturerholder | name | UNIQUE | 持有人全称唯一 |
| syyb_manufacturer | name | UNIQUE | 厂商全称唯一 |
| syyb_drug | atc_code | UNIQUE | ATC 编码唯一 |

---

## 五、后端详细设计

### 5.1 Django 项目结构

```
django/
├── simpleserver/                 # 项目配置包
│   ├── __init__.py
│   ├── settings.py               # 全局配置（数据库、缓存、JWT、CORS等）
│   ├── urls.py                   # 根路由配置
│   ├── wsgi.py                   # WSGI 入口
│   ├── config.yml                # YAML 配置文件（数据库、Redis、邮件等）
│   └── views.py                  # 根视图
│
├── susers/                       # 用户认证模块
│   ├── __init__.py
│   ├── models.py                 # User 模型（扩展 AbstractUser）
│   ├── views.py                  # 用户认证/管理视图（登录、注册、CRUD）
│   ├── serializers.py            # 用户序列化器
│   ├── urls.py                   # 用户模块路由
│   ├── crypto_util.py            # 密码加密工具（RSA + AES）
│   └── tests.py                  # 单元测试
│
├── syyb/                         # 药品管理核心模块
│   ├── __init__.py
│   ├── models.py                 # 数据模型（Drug、Type1Drug、Type2Drug等）
│   ├── views.py                  # API 视图（药品、分类、厂商、药箱）
│   ├── serializers.py            # 序列化器
│   ├── urls.py                   # 路由配置
│   ├── pagination.py             # 自定义分页配置
│   ├── import_tasks.py           # 异步导入任务
│   └── search_indexes.py         # Haystack 搜索索引
│
├── media/                        # 上传文件存储
│   └── drug_images/              # 药品图片目录
│
├── whoosh_index/                 # Whoosh 全文搜索索引
│
├── manage.py                     # Django 管理脚本
├── requirements.txt              # Python 依赖清单
└── venv/                         # Python 虚拟环境
```

### 5.2 配置管理 (settings.py)

系统采用 **YAML 配置文件 + Django settings** 的双层配置模式：

```python
class ConfigManager:
    def __init__(self):
        self.config = self.get_config()

    def get_config(self):
        with open('simpleserver/config.yml', 'rt', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config

    def get(self, item):
        value = self.config.get(item)
        return value

CONFIG = ConfigManager()
```

**配置项包括：**
- `SECRET_KEY` — Django 密钥
- `DB_NAME/DB_HOST/DB_PORT/DB_USER/DB_PASSWORD` — 数据库连接
- `REDIS_HOST/REDIS_PORT` — Redis 连接
- `LOG_PATH/ERROR_LOG_PATH` — 日志路径
- `EMAIL_HOST/EMAIL_PORT/EMAIL_HOST_USER` — 邮件服务
- `ONE_CHAT_URL/ONE_CHAT_MODEL` — AI 聊天服务
- `FSAT_YYB_TOKEN/FSAT_YYB_URL` — 外部 API 认证

### 5.3 REST Framework 配置

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_PAGINATION_CLASS': 'syyb.pagination.CustomPagination',
    'PAGE_SIZE': 50,
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=3),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=30),
    'LEEWAY': 60,
}
```

### 5.4 CORS 配置

```python
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]
```

### 5.5 缓存配置

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{CONFIG.REDIS_HOST}:{CONFIG.REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

### 5.6 日志配置

系统配置了三类日志处理器：
- `log_file` — INFO 级别 rotating 日志（最大 10MB，保留 20 个备份）
- `console` — DEBUG 级别控制台输出（仅开发环境）
- `error_file` — ERROR 级别 rotating 日志

### 5.7 全文搜索配置

使用 Haystack + Whoosh 实现本地全文搜索：

```python
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
```

---

## 六、前端详细设计

### 6.1 后台管理系统 (web/)

#### 项目结构

```
web/
├── public/                       # 静态资源
├── src/
│   ├── api/
│   │   └── index.ts              # Axios 封装与拦截器
│   ├── assets/                   # 静态资源（图片、样式）
│   ├── components/               # 公共组件
│   ├── router/
│   │   └── index.ts              # 路由配置（含路由守卫）
│   ├── stores/
│   │   └── auth.ts               # 认证状态管理（Pinia）
│   ├── types/                    # TypeScript 类型定义
│   ├── views/                    # 页面视图
│   │   ├── LoginView.vue         # 登录页
│   │   ├── HomeView.vue          # 首页仪表盘
│   │   ├── DrugListView.vue      # 药品管理（CRUD、导入）
│   │   ├── CategoryView.vue      # 分类管理
│   │   ├── ManufacturerView.vue  # 厂商管理
│   │   ├── MedicineCabinetView.vue # 智慧药箱
│   │   ├── UserManagementView.vue  # 用户管理
│   │   └── NotFoundView.vue      # 404 页面
│   ├── App.vue                   # 根组件
│   └── main.ts                   # 入口文件
├── package.json
├── vite.config.ts                # Vite 构建配置
├── tsconfig.json                 # TypeScript 配置
└── index.html                    # 入口 HTML
```

#### 路由配置

| 路由 | 路径 | 组件 | 权限 | 说明 |
|------|------|------|------|------|
| login | /login | LoginView.vue | 公开 | 用户登录 |
| home | / | HomeView.vue | 需登录 | 数据仪表盘 |
| drugs | /drugs | DrugListView.vue | 需登录 | 药品管理 |
| categories | /categories | CategoryView.vue | 需登录 | 分类管理 |
| manufacturers | /manufacturers | ManufacturerView.vue | 需登录 | 厂商管理 |
| cabinets | /cabinets | MedicineCabinetView.vue | 需登录 | 智慧药箱 |
| users | /users | UserManagementView.vue | 需登录 | 用户管理 |
| not-found | /* | NotFoundView.vue | 公开 | 404 页面 |

#### 路由守卫特性

1. **单点登录支持**：检测 URL 中的 `portal_token` 参数，自动完成登录
2. **登录状态检查**：未登录用户访问受保护页面自动重定向到登录页
3. **已登录用户保护**：已登录用户访问登录页自动重定向到首页
4. **页面标题设置**：根据路由 meta 自动设置页面标题

### 6.2 用户端系统 (user_web/)

#### 项目结构

```
user_web/
├── public/                       # 静态资源
├── src/
│   ├── api/
│   │   └── index.ts              # Axios 封装
│   ├── assets/                   # 静态资源
│   ├── components/               # 公共组件
│   ├── router/
│   │   └── index.ts              # 路由配置
│   ├── stores/
│   │   └── auth.ts               # 认证状态管理
│   ├── views/                    # 页面视图
│   │   ├── LoginView.vue         # 登录页
│   │   ├── RegisterView.vue      # 注册页
│   │   ├── HomeView.vue          # 首页
│   │   ├── DrugBrowseView.vue    # 药品浏览
│   │   ├── CategoryBrowseView.vue # 分类浏览
│   │   ├── MedicineCabinetView.vue # 我的药箱
│   │   ├── SmartDoctorView.vue   # 智能医生（AI 问答）
│   │   ├── SystemPortalView.vue  # 系统门户
│   │   └── NotFoundView.vue      # 404 页面
│   ├── App.vue
│   └── main.ts
├── package.json
├── vite.config.ts
├── tsconfig.json
└── index.html
```

#### 路由配置

| 路由 | 路径 | 组件 | 权限 | 说明 |
|------|------|------|------|------|
| login | /login | LoginView.vue | 公开 | 用户登录 |
| register | /register | RegisterView.vue | 公开 | 用户注册 |
| home | / | HomeView.vue | user_portal | 首页 |
| drugs | /drugs | DrugBrowseView.vue | user_portal | 药品浏览 |
| categories | /categories | CategoryBrowseView.vue | user_portal | 分类浏览 |
| cabinets | /cabinets | MedicineCabinetView.vue | user_portal | 我的药箱 |
| smart-doctor | /smart-doctor | SmartDoctorView.vue | smart_doctor | 智能医生 |
| system-portal | /system/:key | SystemPortalView.vue | - | 系统门户 |
| not-found | /* | NotFoundView.vue | 公开 | 404 页面 |

#### 权限控制

用户端路由增加了 `permission` 元数据，支持基于权限的页面访问控制：
- `user_portal` — 所有用户默认权限
- `smart_doctor` — 智能医生功能权限

### 6.3 Axios 封装设计

两个前端项目均对 Axios 进行了统一封装，主要特性：

1. **基础配置**：统一设置 `baseURL`、`timeout`、`headers`
2. **请求拦截器**：自动在请求头中附加 `Authorization: Bearer <token>`
3. **响应拦截器**：统一处理错误码（401 跳转登录、403 无权限等）
4. **Token 刷新**：自动处理 Access Token 过期，使用 Refresh Token 续期

### 6.4 状态管理设计 (Pinia)

认证状态管理 (`auth.ts`) 核心功能：

| 状态 | 类型 | 说明 |
|------|------|------|
| token | string | Access Token |
| refreshToken | string | Refresh Token |
| user | object | 当前用户信息 |
| isAuthenticated | boolean | 是否已认证（计算属性） |

| Action | 说明 |
|--------|------|
| login(credentials) | 用户登录，存储 Token 和用户信息 |
| logout() | 退出登录，清除所有状态 |
| refreshAccessToken() | 使用 Refresh Token 获取新的 Access Token |
| autoLoginFromToken(portalToken) | 从门户 Token 自动登录 |
| hasPermission(permission) | 检查用户是否拥有指定权限 |

---

## 七、功能模块详解

### 7.1 用户认证模块

#### 7.1.1 功能清单

| 功能 | 说明 | 适用端 |
|------|------|--------|
| 用户注册 | 新用户注册（默认普通用户） | 用户端 |
| 用户登录 | JWT Token 认证登录 | 双端 |
| Token 刷新 | Access Token 过期自动刷新 | 双端 |
| 用户信息获取 | 获取当前登录用户详情 | 双端 |
| 用户信息修改 | 修改个人资料 | 双端 |
| 密码修改 | 修改登录密码 | 双端 |
| 单点登录 | 从系统门户 iframe 跳转自动登录 | 后台管理 |

#### 7.1.2 密码安全机制

系统采用 **RSA + AES 混合加密** 方案保护密码传输安全：

```
前端输入密码
     │
     ▼
┌─────────────────┐
│  1. 前端AES加密  │ ◀── 使用随机AES密钥
│  (crypto_util)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 使用RSA公钥  │ ◀── 加密AES密钥
│  加密AES密钥     │
└────────┬────────┘
         │
         ▼
    发送到后端
         │
         ▼
┌─────────────────┐
│  3. 后端RSA私钥  │
│  解密获取AES密钥 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. AES解密      │
│  获取原始密码    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. Django      │
│  PBKDF2哈希     │
└────────┬────────┘
         │
         ▼
    存储到数据库
```

### 7.2 药品管理模块

#### 7.2.1 核心功能

| 功能 | 说明 | 权限 |
|------|------|------|
| 药品列表 | 分页展示药品信息，支持排序和筛选 | 公开/登录 |
| 新增药品 | 填写药品详细信息，上传药品图片 | 需登录 |
| 编辑药品 | 修改药品信息，更新图片 | 需登录 |
| 删除药品 | 单条删除或批量删除 | 需登录 |
| Excel 导入 | 批量导入药品数据 | 需登录 |
| 药品搜索 | 多字段模糊搜索 | 公开/登录 |
| 药品详情 | 查看药品完整信息 | 公开/登录 |

#### 7.2.2 药品信息字段

**基本信息：**
- 药品名称 (drug_name)、英文名称 (drug_name_en)
- 商品名 (trade_name)、英文商品名 (trade_name_en)
- 药品图片 (drug_image)
- 是否热门 (is_hot)、家庭常备 (family_use)

**分类信息：**
- 一级分类（通过二级分类关联）
- 二级分类 (type2_drug)
- 收录类别 (category)

**规格信息：**
- 规格 (specification)
- 剂型 (dosage_form)
- 给药途径 (administration_route)

**厂商信息：**
- 上市许可持有人 (manufacturer_holder)
- 生产企业 (manufacturer)

**药品属性：**
- 活性成分 (active_ingredient)、英文活性成分 (active_ingredient_en)
- 批准文号 (approval_number)、批准日期 (approval_date)
- ATC 编码 (atc_code) — 全局唯一
- 市场状态 (market_status)
- 医保类型 (medical_insurance)
- 京东链接 (jd_url)

**扩展信息：**
- 药品说明 (description)
- 适用症状 (indications)

#### 7.2.3 Excel 导入字段映射

| Excel 列名 | 模型字段 | 必填 | 说明 |
|-----------|----------|------|------|
| drug_name | drug_name | 是 | 药品名 |
| drug_name_en | drug_name_en | 否 | 药品英文名 |
| trade_name | trade_name | 否 | 商品名 |
| trade_name_en | trade_name_en | 否 | 商品名英文名 |
| medical_insurance | medical_insurance | 否 | 医保 |
| jd_url | jd_url | 否 | 京东链接 |
| category | category | 否 | 收录类别 |
| Type1Drug_name | Type1Drug | 是 | 一级分类（必须已存在） |
| Type2Drug_name | Type2Drug | 是 | 二级分类（必须已存在） |
| specification | specification | 否 | 规格 |
| dosage_form | dosage_form | 否 | 剂型 |
| administration_route | administration_route | 否 | 给药途径 |
| ManufacturerHolder_name | manufacturer_holder | 否 | 上市许可持有人（必须已存在） |
| ManufacturerHolder_abb | manufacturer_holder.abbreviation | 否 | 持有人简称 |
| Manufacturer_name | manufacturer | 否 | 生产厂商（必须已存在） |
| Manufacturer_abb | manufacturer.abbreviation | 否 | 厂商简称 |
| active_ingredient | active_ingredient | 否 | 活性成分 |
| active_ingredient_en | active_ingredient_en | 否 | 活性成分英文 |
| approval_number | approval_number | 否 | 批准文号 |
| approval_date | approval_date | 否 | 批准日期（YYYY-MM-DD） |
| atc_code | atc_code | 否 | ATC 代码（唯一） |
| market_status | market_status | 否 | 上市销售状况 |
| family_use | family_use | 否 | 家庭常用清单 |

#### 7.2.4 导入流程

```
管理员选择 Excel 文件
         │
         ▼
前端上传文件到后端
         │
         ▼
后端读取 Excel（openpyxl / pandas）
         │
         ▼
逐行解析数据
         │
         ▼
数据校验（字段验证、外键检查）
         │
         ▼
检查重复（ATC 编码、批准文号等）
         │
         ▼
自动创建/更新关联数据（分类、厂商）
         │
         ▼
批量插入药品数据
         │
         ▼
返回导入结果（成功数、失败数、错误详情）
```

### 7.3 分类管理模块

#### 7.3.1 两级分类体系

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

#### 7.3.2 功能清单

| 功能 | 说明 |
|------|------|
| 一级分类 CRUD | 增删改查一级分类 |
| 二级分类 CRUD | 增删改查二级分类，关联一级分类 |
| 分类树结构 | 获取所有分类的层级结构 |
| 分类下药品 | 获取某分类下的所有药品 |

### 7.4 厂商管理模块

#### 7.4.1 两个独立实体

| 实体 | 描述 | 对应字段 |
|------|------|----------|
| **上市许可持有人** (ManufacturerHolder) | 持有药品上市许可的企业 | manufacturer_holder |
| **生产企业** (Manufacturer) | 实际生产药品的企业 | manufacturer |

#### 7.4.2 功能清单

| 功能 | 说明 |
|------|------|
| 持证商 CRUD | 增删改查上市许可持有人（名称、简称） |
| 生产商 CRUD | 增删改查生产厂商（名称、简称） |
| 按厂商搜索药品 | 根据厂商名称搜索关联药品 |

### 7.5 智慧药箱模块

#### 7.5.1 功能清单

| 功能 | 说明 | 权限 |
|------|------|------|
| 药箱列表 | 查看个人所有药箱 | 需登录 |
| 创建药箱 | 创建新药箱（家庭/旅行/办公室/其他） | 需登录 |
| 更新药箱 | 修改药箱信息 | 需登录（仅自己） |
| 删除药箱 | 删除药箱 | 需登录（不能删默认） |
| 默认药箱 | 自动获取/创建默认药箱 | 需登录 |
| 添加药品 | 从药品库添加药品到药箱 | 需登录 |
| 更新数量 | 增加/减少药品数量 | 需登录 |
| 更新信息 | 修改药品生产日期、有效期等 | 需登录 |
| 删除药品 | 从药箱移除药品 | 需登录 |
| 过期提醒 | 自动计算并提醒即将过期药品 | 需登录 |
| 药品筛选 | 按状态筛选（全部/有效/即将过期/已过期/库存不足） | 需登录 |

#### 7.5.2 有效期管理逻辑

```python
class CabinetDrug(models.Model):
    # ...
    
    def is_expired(self):
        """检查药品是否已过期"""
        if self.valid_until:
            from datetime import date
            return self.valid_until < date.today()
        return False

    def is_expiring_soon(self):
        """检查药品是否即将过期"""
        if self.valid_until:
            from datetime import date, timedelta
            return (self.valid_until - date.today()).days <= self.remind_before_days
        return False

    def days_until_expiry(self):
        """返回距离过期还有多少天"""
        if self.valid_until:
            from datetime import date
            return (self.valid_until - date.today()).days
        return None
```

#### 7.5.3 数据隔离

- 每个用户只能查看和管理自己的药箱
- 药箱与药品的关系表中 `cabinet` 外键关联到用户的药箱
- 后端通过 `request.user` 严格校验药箱所有权

### 7.6 智能医生模块

#### 7.6.1 实现方式

用户端系统通过 **iframe 集成 FastGPT** AI 问答服务：

- 外部服务地址：`http://192.168.50.20:3020`
- 集成方式：在 `SmartDoctorView.vue` 中嵌入 iframe
- 功能：提供用药指导、禁忌人群判断、症状咨询等 AI 问答服务

### 7.7 用户管理模块（仅管理员）

#### 7.7.1 功能清单

| 功能 | 说明 |
|------|------|
| 用户列表 | 分页展示所有用户，支持搜索和筛选 |
| 创建用户 | 管理员创建新用户 |
| 编辑用户 | 修改用户信息、角色 |
| 删除用户 | 单条或批量删除 |
| 重置密码 | 重置指定用户密码（默认 123456） |
| 切换状态 | 启用/禁用用户 |
| 用户统计 | 获取用户统计数据 |

#### 7.7.2 筛选条件

- 搜索关键词（用户名/姓名/手机号）
- 角色筛选（admin / user）
- 状态筛选（启用 / 禁用）

---

## 八、API 接口规范

### 8.1 接口基础信息

| 属性 | 内容 |
|------|------|
| 基础 URL | `http://localhost:8000` |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |
| 认证方式 | JWT Bearer Token |
| 时间格式 | `YYYY-MM-DD HH:MM:SS` |

### 8.2 认证相关接口

#### 8.2.1 用户登录

| 属性 | 内容 |
|------|------|
| **接口地址** | `POST /api/token/` |
| **请求参数** | `username` (string, 必填), `password` (string, 必填, 加密后) |
| **响应示例** | 见下文 |

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "name": "管理员",
    "mobile": "13800138000",
    "is_admin": true,
    "is_staff": true
  }
}
```

#### 8.2.2 刷新 Token

| 属性 | 内容 |
|------|------|
| **接口地址** | `POST /api/refresh/` |
| **请求参数** | `refresh` (string, 必填) |

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 8.2.3 用户注册

| 属性 | 内容 |
|------|------|
| **接口地址** | `POST /api/register/` |
| **请求参数** | `username`, `password`, `password_confirm`, `mobile`, `name` |

#### 8.2.4 获取当前用户信息

| 属性 | 内容 |
|------|------|
| **接口地址** | `GET /api/me/` |
| **权限要求** | 需登录 |

#### 8.2.5 修改密码

| 属性 | 内容 |
|------|------|
| **接口地址** | `POST /api/change_password/` |
| **请求参数** | `old_password`, `new_password`, `confirm_password` |

### 8.3 用户管理接口（仅管理员）

| 方法 | 接口 | 说明 |
|------|------|------|
| GET | `/users/` | 获取用户列表（支持搜索、筛选、分页） |
| POST | `/users/` | 创建用户 |
| GET | `/users/{id}/` | 获取用户详情 |
| PUT/PATCH | `/users/{id}/` | 更新用户 |
| DELETE | `/users/{id}/` | 删除用户 |
| DELETE | `/users/batch_delete/` | 批量删除用户 |
| POST | `/users/{id}/reset_password/` | 重置密码 |
| POST | `/users/{id}/toggle_status/` | 切换用户状态 |
| GET | `/users/statistics/` | 用户统计 |

### 8.4 药品管理接口

| 方法 | 接口 | 说明 | 权限 |
|------|------|------|------|
| GET | `/syyb/drug/` | 药品列表（分页） | 公开/登录 |
| POST | `/syyb/drug/` | 创建药品 | 需登录 |
| GET | `/syyb/drug/{id}/` | 药品详情 | 公开/登录 |
| PUT/PATCH | `/syyb/drug/{id}/` | 更新药品 | 需登录 |
| DELETE | `/syyb/drug/{id}/` | 删除药品 | 需登录 |
| DELETE | `/syyb/batch_delete_drugs/` | 批量删除 | 需登录 |
| POST | `/syyb/search_anything/` | 模糊搜索 | 公开/登录 |
| POST | `/syyb/add_drugs_from_excel/` | Excel 导入 | 需登录 |
| GET | `/syyb/download_import_template/` | 下载导入模板 | 公开 |
| POST | `/syyb/preview_import_excel/` | 预览导入数据 | 需登录 |
| POST | `/syyb/async_import_drugs/` | 异步批量导入 | 需登录 |
| GET | `/syyb/import_task_status/{task_id}/` | 查询导入任务状态 | 需登录 |
| POST | `/syyb/family_use_list/` | 按家庭常用清单筛选 | 公开/登录 |

**药品列表查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| page | INT | 页码，默认 1 |
| page_size | INT | 每页数量，默认 50 |
| ordering | STRING | 排序字段，前缀 `-` 表示倒序 |
| type2_drug | INT | 按二级分类筛选 |
| manufacturer | INT | 按生产商筛选 |
| is_hot | BOOL | 按热门筛选 |
| medical_insurance | STRING | 按医保类型筛选 |

### 8.5 分类管理接口

| 方法 | 接口 | 说明 |
|------|------|------|
| GET/POST | `/syyb/type1drug/` | 一级分类列表/创建 |
| GET/PUT/DELETE | `/syyb/type1drug/{id}/` | 一级分类详情/更新/删除 |
| GET/POST | `/syyb/type2drug/` | 二级分类列表/创建 |
| GET/PUT/DELETE | `/syyb/type2drug/{id}/` | 二级分类详情/更新/删除 |
| GET | `/syyb/all_type1_with_type2/` | 获取完整分类树 |
| GET | `/syyb/type1_type2/{type1_id}/` | 获取一级分类下的二级分类 |
| GET | `/syyb/type2_drugs/{type2_id}/` | 获取二级分类下的药品 |

### 8.6 厂商管理接口

| 方法 | 接口 | 说明 |
|------|------|------|
| GET/POST | `/syyb/manufacturerholder/` | 持证商列表/创建 |
| GET/PUT/DELETE | `/syyb/manufacturerholder/{id}/` | 持证商详情/更新/删除 |
| GET/POST | `/syyb/manufacturer/` | 生产商列表/创建 |
| GET/PUT/DELETE | `/syyb/manufacturer/{id}/` | 生产商详情/更新/删除 |
| POST | `/syyb/search_manufacturer/` | 按厂商搜索药品 |
| POST | `/syyb/search_manufacturer_holder/` | 按持有人搜索药品 |

### 8.7 药箱管理接口

| 方法 | 接口 | 说明 |
|------|------|------|
| GET/POST | `/syyb/cabinets/` | 药箱列表/创建 |
| GET/PUT/DELETE | `/syyb/cabinets/{id}/` | 药箱详情/更新/删除 |
| GET | `/syyb/default_cabinet/` | 获取/创建默认药箱 |
| GET | `/syyb/cabinets/{cabinet_id}/drugs/` | 获取药箱中的药品 |
| POST | `/syyb/cabinet_drugs/` | 添加药品到药箱 |
| PUT/PATCH/DELETE | `/syyb/cabinet_drugs/{id}/` | 更新/删除药箱药品 |
| POST | `/syyb/cabinet_drugs/{id}/quantity/` | 更新药品数量 |

**药箱药品查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| filter | STRING | 筛选类型（all/valid/expiring_soon/expired/low_stock） |
| sort | STRING | 排序字段 |

### 8.8 通用响应格式

#### 成功响应（列表）

```json
{
  "count": 100,
  "next": "http://localhost:8000/syyb/drug/?page=2",
  "previous": null,
  "results": [...]
}
```

#### 成功响应（单条）

```json
{
  "id": 1,
  "drug_name": "阿莫西林胶囊",
  "...": "..."
}
```

#### 错误响应

```json
{
  "detail": "错误信息描述",
  "code": "error_code"
}
```

---

## 九、认证与权限系统

### 9.1 JWT 认证流程

```
┌──────────┐                     ┌──────────┐                     ┌──────────┐
│   客户端  │                     │   后端   │                     │  数据库  │
└────┬─────┘                     └────┬─────┘                     └────┬─────┘
     │                                │                                │
     │ 1. POST /api/token/            │                                │
     │    {username, password}        │                                │
     │───────────────────────────────▶│                                │
     │                                │ 2. 验证用户信息                 │
     │                                │───────────────────────────────▶│
     │                                │                                │
     │                                │◀───────────────────────────────│
     │                                │ 3. 生成JWT Token               │
     │ 4. 返回 {access, refresh, user}│                                │
     │◀───────────────────────────────│                                │
     │                                │                                │
     │ 5. 后续请求携带 Header:        │                                │
     │    Authorization: Bearer {access}                               │
     │───────────────────────────────▶│                                │
     │                                │ 6. 验证Token有效性              │
     │ 7. 返回受保护的数据             │                                │
     │◀───────────────────────────────│                                │
     │                                │                                │
     │ 8. Token过期后 POST /api/refresh/                                │
     │    {refresh}                   │                                │
     │───────────────────────────────▶│ 9. 返回新的access token        │
     │◀───────────────────────────────│                                │
     │                                │                                │
```

### 9.2 Token 有效期

| Token 类型 | 有效期 | 用途 |
|-----------|--------|------|
| Access Token | 3 天 | 日常 API 请求认证 |
| Refresh Token | 30 天 | 刷新 Access Token |
| LeeWay | 60 秒 | 刷新缓冲期 |

### 9.3 权限控制体系

| 权限类 | 说明 | 适用场景 |
|--------|------|----------|
| `AllowAny` | 允许任何人访问 | 公开接口（如药品搜索、登录） |
| `IsAuthenticated` | 需登录 | 普通用户接口 |
| `IsAdminUserCustom` | 需管理员身份 | 用户管理、数据导入等 |
| `IsRegularUser` | 需普通用户身份 | 用户端特定功能 |

### 9.4 用户角色与系统访问权限

```python
def get_accessible_systems(self):
    """
    获取用户可访问的系统列表
    默认普通用户可访问 user_portal
    管理员额外可访问 admin_system
    """
    systems = set(self.permissions) if self.permissions else set()
    systems.add('user_portal')  # 所有用户默认可以访问用户端
    
    if self.is_admin or self.is_superuser:
        systems.add('admin_system')  # 管理员可访问后台系统
        
    return list(systems)
```

---

## 十、部署与运维指南

### 10.1 环境要求

#### 后端环境

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.12 | 编程语言 |
| MySQL | 8.0+ | 主数据库 |
| Redis | 6.0+ | 缓存服务 |

#### 前端环境

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Node.js | 18+ | JavaScript 运行时 |
| npm | 9+ | 包管理器 |

### 10.2 服务端口说明

| 服务 | 端口 | 访问地址 | 说明 |
|------|------|----------|------|
| Django 后端 | 8000 | http://localhost:8000 | REST API 服务 |
| Django Admin | 8000 | http://localhost:8000/admin | 管理员后台 |
| 后台管理系统 | 5173 | http://localhost:5173 | 管理员前端 |
| 用户端系统 | 3001 | http://localhost:3001 | 普通用户前端 |
| MySQL | 3306 | localhost:3306 | 数据库 |
| Redis | 6379 | localhost:6379 | 缓存 |

### 10.3 后端部署步骤

```bash
# 1. 进入后端目录
cd django

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate     # Windows

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置数据库（编辑 simpleserver/config.yml）

# 6. 创建数据库
mysql -u root -p -e "CREATE DATABASE yyb_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 7. 执行迁移
python manage.py migrate

# 8. 创建超级管理员
python manage.py createsuperuser

# 9. 启动服务
python manage.py runserver
```

### 10.4 前端部署步骤

#### 后台管理系统

```bash
cd web

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
# 输出目录: web/dist
```

#### 用户端系统

```bash
cd user_web

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
# 输出目录: user_web/dist
```

### 10.5 一键启动脚本

系统提供了多个启动脚本，支持不同操作系统：

#### Mac/Linux

```bash
# 总启动脚本（推荐）
chmod +x start.sh
./start.sh

# 单独启动各服务
./start-user-web.sh       # 启动用户端系统
```

**脚本菜单选项：**
1. 启动后端服务 (Django) — 端口 8000
2. 启动后台管理系统 (管理员端) — 端口 5173
3. 启动用户端系统 — 端口 3001
4. 启动所有服务
5. 查看服务状态
6. 停止所有服务
7. 退出

#### Windows

```powershell
# 总启动脚本（推荐）
.\start.bat

# 或单独启动各服务
.\start-backend.ps1      # 启动后端服务
.\start-frontend.ps1     # 启动后台管理系统
.\start-user-web.ps1     # 启动用户端系统
```

#### 脚本特性

- ✅ 自动检测环境依赖（Python、Node.js、MySQL、Redis）
- ✅ 自动检测端口占用，避免冲突
- ✅ 自动安装缺失的 npm 依赖
- ✅ 支持服务状态查看
- ✅ 支持一键停止所有服务
- ✅ 日志输出到 `.logs/` 目录

### 10.6 生产环境部署建议

```
┌─────────────────────────────────────────────────────────────────┐
│                         Nginx 反向代理                            │
│                     (负载均衡、HTTPS、静态文件)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  管理员前端      │ │   用户前端       │ │   Django后端    │
│  (静态文件)      │ │   (静态文件)     │ │   (Gunicorn)   │
│  /web/dist      │ │   /user_web/dist │ │   多进程部署    │
└─────────────────┘ └─────────────────┘ └────────┬────────┘
                                                 │
                    ┌────────────────────────────┼────────────┐
                    │                            │            │
                    ▼                            ▼            ▼
            ┌──────────────┐            ┌──────────────┐ ┌──────────────┐
            │    MySQL     │            │    Redis     │ │   文件存储   │
            │   主从复制    │            │   哨兵模式   │ │   对象存储   │
            └──────────────┘            └──────────────┘ └──────────────┘
```

**生产环境推荐配置：**
- **Nginx**: 反向代理、SSL 终端、静态文件服务
- **Gunicorn**: WSGI HTTP 服务器，多 worker 部署
- **MySQL**: 主从复制，定期备份
- **Redis**: 持久化配置，考虑哨兵模式
- **静态文件**: CDN 加速（生产环境）

### 10.7 日志管理

系统日志输出到 `.logs/` 目录：

| 日志文件 | 说明 |
|---------|------|
| `.logs/backend.log` | 后端服务日志 |
| `.logs/admin.log` | 后台管理系统日志 |
| `.logs/user.log` | 用户端系统日志 |

**查看日志命令：**
```bash
# 实时查看后端日志
tail -f .logs/backend.log

# 实时查看后台管理日志
tail -f .logs/admin.log

# 实时查看用户端日志
tail -f .logs/user.log
```

### 10.8 进程管理

系统使用 `.pids/` 目录存储进程 ID：

| PID 文件 | 说明 |
|---------|------|
| `.pids/admin.pid` | 后台管理系统进程 |
| `.pids/backend.pid` | 后端服务进程 |
| `.pids/user.pid` | 用户端系统进程 |

---

## 十一、安全架构

### 11.1 安全措施汇总

| 层面 | 安全措施 | 实现方式 |
|------|---------|---------|
| **传输安全** | HTTPS | Nginx SSL 配置（生产环境） |
| **认证** | JWT Token | djangorestframework-simplejwt |
| **密码传输** | 前端加密 | RSA + AES 混合加密 |
| **密码存储** | 哈希存储 | Django PBKDF2 算法 |
| **接口权限** | 角色控制 | 自定义权限类 |
| **SQL 注入** | ORM 防护 | Django ORM 参数化查询 |
| **XSS 防护** | 内容转义 | Vue 模板自动转义 |
| **CSRF 防护** | Token 验证 | Django CSRF Middleware（开发环境关闭） |
| **文件上传** | 类型/大小限制 | 后端验证 + Pillow 处理 |
| **CORS** | 跨域控制 | django-cors-headers |

### 11.2 密码加密流程

详见 [7.1.2 密码安全机制](#712-密码安全机制)

### 11.3 数据隔离

- **药品数据**: 所有用户可浏览，仅管理员可修改
- **药箱数据**: 严格的用户级隔离，只能操作自己的药箱
- **用户数据**: 管理员可查看所有用户，普通用户只能查看自己

---

## 十二、性能优化策略

### 12.1 后端优化

| 策略 | 实现方式 |
|------|---------|
| **数据库索引** | 在药品名、商品名、ATC 代码等字段添加索引 |
| **查询优化** | 使用 `select_related` 和 `prefetch_related` 减少 N+1 查询 |
| **分页加载** | 默认每页 50 条，支持自定义页大小 |
| **异步导入** | 大批量数据导入使用后台线程处理 |
| **缓存** | 使用 Redis 缓存热门数据 |
| **全文搜索** | Haystack + Whoosh 实现高效全文检索 |

### 12.2 前端优化

| 策略 | 实现方式 |
|------|---------|
| **懒加载** | 路由组件按需加载 (`() => import(...)`) |
| **虚拟滚动** | 大数据列表使用虚拟滚动 |
| **图片优化** | 图片懒加载、压缩 |
| **CDN** | 生产环境使用 CDN 加速静态资源 |
| **构建优化** | Vite 构建工具，Tree Shaking |

---

## 十三、项目目录结构

### 13.1 完整目录树

```
yyb-be/                                 # 项目根目录
├── .git/                               # Git 版本控制
├── .history/                           # 历史配置备份
├── .logs/                              # 日志输出目录
│   ├── admin.log
│   ├── backend.log
│   └── user.log
├── .pids/                              # 进程 PID 文件
│   ├── admin.pid
│   ├── backend.pid
│   └── user.pid
│
├── django/                             # 后端 Django 项目
│   ├── simpleserver/                   # 项目配置包
│   │   ├── __init__.py
│   │   ├── settings.py                 # 全局配置
│   │   ├── urls.py                     # 根路由
│   │   ├── wsgi.py                     # WSGI 入口
│   │   ├── config.yml                  # YAML 配置文件
│   │   └── views.py
│   ├── susers/                         # 用户认证模块
│   │   ├── __init__.py
│   │   ├── models.py                   # User 模型
│   │   ├── views.py                    # 用户视图
│   │   ├── serializers.py              # 序列化器
│   │   ├── urls.py                     # 路由
│   │   └── crypto_util.py              # 加密工具
│   ├── syyb/                           # 药品管理核心模块
│   │   ├── __init__.py
│   │   ├── models.py                   # 数据模型
│   │   ├── views.py                    # API 视图
│   │   ├── serializers.py              # 序列化器
│   │   ├── urls.py                     # 路由
│   │   ├── pagination.py               # 分页配置
│   │   ├── import_tasks.py             # 异步导入任务
│   │   └── search_indexes.py           # 搜索索引
│   ├── media/                          # 上传文件存储
│   │   └── drug_images/                # 药品图片
│   ├── whoosh_index/                   # Whoosh 搜索索引
│   ├── venv/                           # Python 虚拟环境
│   ├── manage.py                       # Django 管理脚本
│   └── requirements.txt                # Python 依赖
│
├── web/                                # 后台管理系统（管理员端）
│   ├── dist/                           # 生产构建输出
│   ├── node_modules/                   # npm 依赖
│   ├── public/                         # 静态资源
│   ├── src/
│   │   ├── api/
│   │   │   └── index.ts                # Axios 封装
│   │   ├── assets/                     # 静态资源
│   │   ├── components/                 # 公共组件
│   │   ├── router/
│   │   │   └── index.ts                # 路由配置
│   │   ├── stores/
│   │   │   └── auth.ts                 # 认证状态
│   │   ├── types/                      # TS 类型定义
│   │   ├── views/                      # 页面视图
│   │   │   ├── LoginView.vue
│   │   │   ├── HomeView.vue
│   │   │   ├── DrugListView.vue
│   │   │   ├── CategoryView.vue
│   │   │   ├── ManufacturerView.vue
│   │   │   ├── MedicineCabinetView.vue
│   │   │   ├── UserManagementView.vue
│   │   │   └── NotFoundView.vue
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
│
├── user_web/                           # 用户端系统（普通用户）
│   ├── dist/                           # 生产构建输出
│   ├── node_modules/                   # npm 依赖
│   ├── src/
│   │   ├── api/
│   │   │   └── index.ts                # Axios 封装
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   │   └── index.ts                # 路由配置
│   │   ├── stores/
│   │   │   └── auth.ts                 # 认证状态
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── HomeView.vue
│   │   │   ├── DrugBrowseView.vue
│   │   │   ├── CategoryBrowseView.vue
│   │   │   ├── MedicineCabinetView.vue
│   │   │   ├── SmartDoctorView.vue
│   │   │   ├── SystemPortalView.vue
│   │   │   └── NotFoundView.vue
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
│
├── performance_test/                   # 性能测试
│   ├── reports/                        # 测试报告
│   ├── ai_perf_test.py                 # AI 性能测试
│   ├── api_client.py                   # API 测试客户端
│   ├── crypto_utils.py                 # 加密工具
│   ├── performance_test.py             # 性能测试脚本
│   └── ...
│
├── .env                                # 环境变量
├── .gitignore                          # Git 忽略配置
│
├── start.sh                            # Mac/Linux 总启动脚本
├── start.bat                           # Windows 总启动脚本
├── start-backend.ps1                   # 后端启动脚本（PowerShell）
├── start-frontend.ps1                  # 后台管理启动脚本
├── start-user-web.ps1                  # 用户端启动脚本（PowerShell）
├── start-user-web.sh                   # 用户端启动脚本（Mac/Linux）
├── configure.sh                        # Mac/Linux 配置脚本
├── configure.ps1                       # Windows 配置脚本
├── stop.sh                             # 停止服务脚本
│
├── README.md                           # 项目说明文档
├── SYSTEM_DOCUMENTATION.md             # 系统详细文档
├── FUNCTION_DOCUMENTATION.md           # 功能模块文档
├── API_DOCUMENTATION.md                # API 接口文档
├── ARCHITECTURE.md                     # 技术架构文档
├── DETAILED_SYSTEM_DOCUMENTATION.md    # 本文档
└── system.md                           # 功能开发清单
```

---

## 十四、附录

### 14.1 缩略语说明

| 缩略语 | 全称 | 说明 |
|--------|------|------|
| JWT | JSON Web Token | 认证令牌 |
| DRF | Django REST Framework | REST API 框架 |
| CRUD | Create, Read, Update, Delete | 增删改查操作 |
| API | Application Programming Interface | 应用程序接口 |
| ATC | Anatomical Therapeutic Chemical | 解剖学治疗学及化学分类 |
| ORM | Object-Relational Mapping | 对象关系映射 |
| WSGI | Web Server Gateway Interface | Web 服务器网关接口 |
| CORS | Cross-Origin Resource Sharing | 跨域资源共享 |
| CSRF | Cross-Site Request Forgery | 跨站请求伪造 |
| XSS | Cross-Site Scripting | 跨站脚本攻击 |
| SQL | Structured Query Language | 结构化查询语言 |

### 14.2 参考文档

- Django 官方文档: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Vue 3 官方文档: https://vuejs.org/
- Element Plus: https://element-plus.org/
- Pinia: https://pinia.vuejs.org/
- Vite: https://vitejs.dev/

### 14.3 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-03-24 | 初始版本，基础功能 |
| v1.1 | 2026-04-08 | 增加智慧药箱、用户管理 |
| v2.0 | 2026-06-11 | 完善文档，增加详细说明 |

### 14.4 版权信息

本项目为毕业设计项目，仅供学习交流使用。

---

*文档结束 — 医药宝管理系统详细说明文档*
