# 医药宝管理系统 - 系统功能文档

> **Medicine Management System Documentation**
> 
> 版本: v1.0 | 最后更新: 2026-03-24

---

## 1. 系统概述 (System Overview)

### 1.1 系统简介

**医药宝管理系统**是一款面向医药行业的企业级信息管理平台，旨在提供全面、高效的药品信息管理解决方案。系统支持药品基础数据管理、分类体系维护、厂商信息维护等核心功能，同时提供Excel批量导入、智能搜索、图片上传等便捷功能。

### 1.2 系统特点

| 特性 | 说明 |
|------|------|
| 安全认证 | 基于JWT的双token认证机制，支持Access Token自动刷新 |
| 数据管理 | 完整的CRUD操作，支持批量导入和批量删除 |
| 智能搜索 | 多字段模糊搜索，支持药品名、商品名、厂商等多维度检索 |
| 图片管理 | 支持药品图片上传和预览 |
| 响应式设计 | 现代化UI界面，支持多端适配 |
| 分级架构 | 两级分类体系，清晰的数据组织结构 |

### 1.3 技术栈概览

```
前端层 (Frontend): Vue 3 + TypeScript + Element Plus + Pinia
后端层 (Backend): Django + DRF + JWT + MySQL + Redis
```

---

## 2. 技术架构 (Technical Architecture)

### 2.1 后端架构

#### 2.1.1 核心技术

| 技术组件 | 版本 | 用途说明 |
|----------|------|----------|
| Django | 4.x | Web应用主框架 |
| Django REST Framework | 3.x | RESTful API开发 |
| djangorestframework-simplejwt | - | JWT认证实现 |
| MySQL | 8.x | 关系型数据库 |
| Redis | 6.x | 缓存与会话存储 |
| Pandas | - | Excel数据处理 |

#### 2.1.2 项目结构

```
django/
├── simpleserver/           # 项目配置
│   ├── settings.py         # 全局配置
│   ├── urls.py             # 根路由
│   └── wsgi.py             # WSGI入口
├── susers/                 # 用户模块
│   ├── models.py           # User模型
│   ├── views.py            # 视图逻辑
│   └── urls.py             # 路由配置
├── syyb/                   # 药品管理核心模块
│   ├── models.py           # 数据模型定义
│   ├── views.py            # API视图
│   ├── serializers.py      # 序列化器
│   └── urls.py             # 路由配置
├── media/                  # 上传文件存储
│   └── drug_images/        # 药品图片
└── manage.py               # Django管理脚本
```

#### 2.1.3 JWT认证配置

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
```

### 2.2 前端架构

#### 2.2.1 核心技术

| 技术组件 | 版本 | 用途说明 |
|----------|------|----------|
| Vue | 3.x | 渐进式JavaScript框架 |
| TypeScript | 5.x | 类型安全的JavaScript超集 |
| Element Plus | 2.x | UI组件库 |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 路由管理 |
| Axios | 1.x | HTTP客户端 |

#### 2.2.2 项目结构

```
web/
├── src/
│   ├── api/
│   │   └── index.ts           # Axios封装与拦截器
│   ├── router/
│   │   └── index.ts           # 路由配置
│   ├── stores/
│   │   └── auth.ts            # 认证状态管理
│   ├── views/                 # 页面视图
│   │   ├── LoginView.vue      # 登录页
│   │   ├── HomeView.vue       # 首页仪表盘
│   │   ├── DrugListView.vue   # 药品列表
│   │   ├── CategoryView.vue   # 分类管理
│   │   └── ManufacturerView.vue # 厂商管理
│   ├── App.vue                # 根组件
│   └── main.ts                # 入口文件
└── package.json
```


---

## 3. 功能模块 (Functional Modules)

### 3.1 用户认证模块 (User Authentication)

#### 3.1.1 功能说明

基于JWT的双token认证机制，提供安全的用户身份验证和会话管理。

#### 3.1.2 认证流程

1. 客户端提交用户名和密码
2. 后端验证用户信息
3. 验证通过后返回 Access Token 和 Refresh Token
4. 客户端存储 Token，后续请求携带 Access Token
5. Access Token 过期后，使用 Refresh Token 获取新的 Access Token

#### 3.1.3 API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/token/ | POST | 获取Access Token和Refresh Token |
| /api/refresh/ | POST | 使用Refresh Token刷新Access Token |
| /api/verify/ | POST | 验证Token有效性 |

#### 3.1.4 Token有效期

- **Access Token**: 3天
- **Refresh Token**: 7天

---

### 3.2 药品管理模块 (Drug Management)

#### 3.2.1 功能说明

药品管理是系统的核心模块，提供药品信息的增删改查、批量导入、图片上传等功能。

#### 3.2.2 数据模型

| 字段名 | 类型 | 说明 |
|--------|------|------|
| drug_name | CharField | 药品通用名 |
| drug_name_en | CharField | 药品英文名 |
| trade_name | CharField | 商品名 |
| trade_name_en | CharField | 商品名英文名 |
| specification | CharField | 规格 |
| dosage_form | CharField | 剂型 |
| administration_route | CharField | 给药途径 |
| manufacturer | ForeignKey | 生产厂商 |
| manufacturer_holder | ForeignKey | 上市许可持有人 |
| approval_number | CharField | 批准文号 |
| approval_date | DateField | 批准日期 |
| atc_code | CharField | ATC编码 |
| medical_insurance | CharField | 医保类型 |
| drug_image | ImageField | 药品图片 |
| is_hot | BooleanField | 是否热门 |
| family_use | CharField | 家庭常用清单分类 |

#### 3.2.3 API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /syyb/drug/ | GET | 获取药品列表（分页） |
| /syyb/drug/ | POST | 创建新药品 |
| /syyb/drug/{id}/ | GET | 获取药品详情 |
| /syyb/drug/{id}/ | PUT | 更新药品信息 |
| /syyb/drug/{id}/ | DELETE | 删除药品 |
| /syyb/batch_delete_drugs/ | DELETE | 批量删除药品 |
| /syyb/add_drugs_from_excel/ | POST | Excel批量导入 |
| /syyb/search_anything/ | POST | 多字段模糊搜索 |
| /syyb/family_use_list/ | POST | 按家庭常用清单筛选 |

#### 3.2.4 Excel导入字段映射

| Excel列名 | 模型字段 | 说明 |
|-----------|----------|------|
| drug_name | drug_name | 药品名 |
| drug_name_en | drug_name_en | 药品英文名 |
| trade_name | trade_name | 商品名 |
| trade_name_en | trade_name_en | 商品名英文名 |
| medical_insurance | medical_insurance | 医保 |
| jd_url | jd_url | 京东链接 |
| category | category | 收录类别 |
| Type1Drug_name | Type1Drug | 一级分类 |
| Type2Drug_name | Type2Drug | 二级分类 |
| specification | specification | 规格 |
| dosage_form | dosage_form | 剂型 |
| administration_route | administration_route | 给药途径 |
| ManufacturerHolder_name | manufacturer_holder | 上市许可持有人 |
| ManufacturerHolder_abb | manufacturer_holder.abbreviation | 持有人简称 |
| Manufacturer_name | manufacturer | 生产厂商 |
| Manufacturer_abb | manufacturer.abbreviation | 厂商简称 |
| active_ingredient | active_ingredient | 活性成分 |
| active_ingredient_en | active_ingredient_en | 活性成分英文 |
| approval_number | approval_number | 批准文号 |
| approval_date | approval_date | 批准日期 |
| atc_code | atc_code | ATC代码 |
| market_status | market_status | 上市销售状况 |
| family_use | family_use | 家庭常用清单 |


---

### 3.3 分类管理模块 (Category Management)

#### 3.3.1 功能说明

采用两级分类体系：一级分类(Type1)和二级分类(Type2)。每个二级分类必须属于一个一级分类。

#### 3.3.2 数据模型

**Type1Drug（一级分类）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键ID |
| name | CharField | 一级分类名称，唯一 |

**Type2Drug（二级分类）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键ID |
| name | CharField | 二级分类名称 |
| type1_drug | ForeignKey | 所属一级分类 |

#### 3.3.3 API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /syyb/type1drug/ | GET | 获取一级分类列表 |
| /syyb/type1drug/ | POST | 创建一级分类 |
| /syyb/type1drug/{id}/ | GET | 获取一级分类详情 |
| /syyb/type1drug/{id}/ | PUT | 更新一级分类 |
| /syyb/type1drug/{id}/ | DELETE | 删除一级分类 |
| /syyb/type2drug/ | GET | 获取二级分类列表 |
| /syyb/type2drug/ | POST | 创建二级分类 |
| /syyb/type2drug/{id}/ | GET | 获取二级分类详情 |
| /syyb/type2drug/{id}/ | PUT | 更新二级分类 |
| /syyb/type2drug/{id}/ | DELETE | 删除二级分类 |
| /syyb/type1_type2/{type1_id}/ | GET | 获取一级分类下的二级分类 |
| /syyb/type2_drugs/{type2_id}/ | GET | 获取二级分类下的所有药品 |
| /syyb/all_type1_with_type2/ | GET | 获取所有分类层级结构 |

---

### 3.4 厂商管理模块 (Manufacturer Management)

#### 3.4.1 功能说明

管理药品的生产厂商和上市许可持有人信息，支持全称和简称。

#### 3.4.2 数据模型

**ManufacturerHolder（上市许可持有人）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键ID |
| name | CharField | 持有人全称，唯一 |
| abbreviation | CharField | 持有人简称 |

**Manufacturer（生产厂商）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键ID |
| name | CharField | 厂商全称，唯一 |
| abbreviation | CharField | 厂商简称 |

#### 3.4.3 API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /syyb/manufacturerholder/ | GET | 获取持有人列表 |
| /syyb/manufacturerholder/ | POST | 创建持有人 |
| /syyb/manufacturerholder/{id}/ | GET | 获取持有人详情 |
| /syyb/manufacturerholder/{id}/ | PUT | 更新持有人信息 |
| /syyb/manufacturerholder/{id}/ | DELETE | 删除持有人 |
| /syyb/manufacturer/ | GET | 获取厂商列表 |
| /syyb/manufacturer/ | POST | 创建厂商 |
| /syyb/manufacturer/{id}/ | GET | 获取厂商详情 |
| /syyb/manufacturer/{id}/ | PUT | 更新厂商信息 |
| /syyb/manufacturer/{id}/ | DELETE | 删除厂商 |
| /syyb/search_manufacturer/ | POST | 按厂商搜索药品 |
| /syyb/search_manufacturer_holder/ | POST | 按持有人搜索药品 |


---

## 4. 数据库设计 (Database Design)

### 4.1 实体关系说明

```
Type1Drug (1) ----< (N) Type2Drug (1) ----< (N) Drug
                                           
Drug (N) ----> (1) ManufacturerHolder
Drug (N) ----> (1) Manufacturer
```

### 4.2 表结构说明

| 表名 | 中文名 | 说明 |
|------|--------|------|
| susers_user | 用户表 | 系统用户信息 |
| syyb_type1drug | 一级分类表 | 药品一级分类 |
| syyb_type2drug | 二级分类表 | 药品二级分类，关联一级分类 |
| syyb_manufacturerholder | 持有人表 | 上市许可持有人信息 |
| syyb_manufacturer | 厂商表 | 生产厂商信息 |
| syyb_drug | 药品表 | 药品详细信息 |

### 4.3 关键字段约束

| 表名 | 字段 | 约束 |
|------|------|------|
| syyb_type1drug | name | UNIQUE |
| syyb_type2drug | name + type1_drug_id | UNIQUE together |
| syyb_manufacturerholder | name | UNIQUE |
| syyb_manufacturer | name | UNIQUE |
| syyb_drug | atc_code | UNIQUE |

---

## 5. API文档 (API Documentation)

### 5.1 认证相关接口

#### 获取Token
- **URL**: /api/token/
- **Method**: POST
- **Body**:
```json
{
  "username": "admin",
  "password": "password123"
}
```
- **Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```

#### 刷新Token
- **URL**: /api/refresh/
- **Method**: POST
- **Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```

### 5.2 药品相关接口

#### 获取药品列表
- **URL**: /syyb/drug/
- **Method**: GET
- **Query Parameters**:
  - page: 页码（默认1）
  - page_size: 每页数量（默认50）

#### 模糊搜索药品
- **URL**: /syyb/search_anything/
- **Method**: POST
- **Body**:
```json
{
  "text": "搜索关键词"
}
```
- **说明**: 支持药品名、英文名、商品名、厂商名等字段的模糊搜索

#### 批量删除药品
- **URL**: /syyb/batch_delete_drugs/
- **Method**: DELETE
- **Body**:
```json
{
  "drug_ids": [1, 2, 3]
}
```

#### Excel批量导入
- **URL**: /syyb/add_drugs_from_excel/
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Parameters**:
  - file: Excel文件(.xls, .xlsx)

### 5.3 分类相关接口

#### 获取分类层级结构
- **URL**: /syyb/all_type1_with_type2/
- **Method**: GET
- **Response**:
```json
{
  "count": 10,
  "results": [
    {
      "value": 1,
      "label": "化学药品",
      "children": [
        {"value": 1, "label": "抗生素"},
        {"value": 2, "label": "解热镇痛"}
      ]
    }
  ]
}
```

### 5.4 通用响应格式

#### 成功响应
```json
{
  "count": 100,
  "results": [...],
  "next": "http://api/next/page",
  "previous": null
}
```

#### 错误响应
```json
{
  "error": "错误信息描述"
}
```


---

## 6. 前端页面 (Frontend Pages)

### 6.1 登录页 (LoginView.vue)

#### 功能说明
- 用户身份验证入口
- 支持用户名和密码登录
- 表单验证和错误提示
- JWT Token存储到本地

#### 页面组件
| 组件 | 说明 |
|------|------|
| el-input | 用户名/密码输入框 |
| el-button | 登录按钮，带加载状态 |
| el-form | 表单验证 |

#### 路由
- **Path**: /login
- **Name**: login
- **Meta**: public: true

---

### 6.2 首页仪表盘 (HomeView.vue)

#### 功能说明
- 系统概览和数据统计
- 快捷操作入口
- 热门药品展示

#### 统计卡片
| 卡片 | 数据指标 |
|------|----------|
| 药品总数 | /syyb/drug/ count |
| 分类数量 | Type1 + Type2 count |
| 厂商数量 | Holder + Manufacturer count |
| 用户数量 | 系统用户数 |

#### 快捷操作
- 药品管理
- 分类管理
- 厂商管理
- 药品搜索

#### 路由
- **Path**: /
- **Name**: home

---

### 6.3 药品列表页 (DrugListView.vue)

#### 功能说明
- 药品信息的完整CRUD管理
- 分页展示和批量操作
- 多维度搜索筛选
- 药品详情查看

#### 核心功能
| 功能 | 说明 |
|------|------|
| 搜索 | 关键词搜索（药品名/商品名/厂商） |
| 筛选 | 按分类层级筛选 |
| 新增 | 创建新药品记录 |
| 编辑 | 修改药品信息 |
| 删除 | 单条或批量删除 |
| 导入 | Excel批量导入 |
| 查看详情 | 弹窗展示完整药品信息 |

#### 表格列
| 列名 | 说明 |
|------|------|
| 药品图片 | el-image预览 |
| 商品名 | 显示热门标签 |
| 通用名 | drug_name |
| 规格 | specification |
| 剂型 | dosage_form |
| 生产厂商 | manufacturer |
| 批准文号 | approval_number |
| 操作 | 查看/编辑/删除 |

#### 路由
- **Path**: /drugs
- **Name**: drugs

---

### 6.4 分类管理页 (CategoryView.vue)

#### 功能说明
- 两级分类体系的维护
- 分类与药品的关联展示

#### 核心功能
| 功能 | 说明 |
|------|------|
| 一级分类 | 增删改查 |
| 二级分类 | 增删改查，关联一级分类 |
| 层级展示 | 树形结构展示 |

#### 路由
- **Path**: /categories
- **Name**: categories

---

### 6.5 厂商管理页 (ManufacturerView.vue)

#### 功能说明
- 上市许可持有人管理
- 生产厂商管理

#### 核心功能
| 功能 | 说明 |
|------|------|
| 持有人管理 | 增删改查，全称/简称 |
| 厂商管理 | 增删改查，全称/简称 |
| 搜索筛选 | 按名称搜索 |

#### 路由
- **Path**: /manufacturers
- **Name**: manufacturers

---

### 6.6 路由配置汇总

| 路由 | 路径 | 组件 | 权限 |
|------|------|------|------|
| login | /login | LoginView.vue | 公开 |
| home | / | HomeView.vue | 需登录 |
| drugs | /drugs | DrugListView.vue | 需登录 |
| categories | /categories | CategoryView.vue | 需登录 |
| manufacturers | /manufacturers | ManufacturerView.vue | 需登录 |
| not-found | /* | NotFoundView.vue | 公开 |

---

## 7. 开发环境配置

### 7.1 后端环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动服务
python manage.py runserver
```

### 7.2 前端环境

```bash
# 进入前端目录
cd web

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

---

## 8. 系统截图说明

### 8.1 登录界面
- 紫色渐变背景
- 居中登录卡片
- 用户名密码输入
- 表单验证提示

### 8.2 首页仪表盘
- 欢迎卡片
- 四个统计卡片（药品/分类/厂商/用户）
- 快捷操作区域
- 热门药品表格

### 8.3 药品管理
- 搜索筛选区域
- 数据表格展示
- 分页组件
- 操作按钮组
- 详情弹窗

---

## 9. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-03-24 | 初始版本，包含基础功能 |

---

## 10. 附录

### 10.1 缩略语说明

| 缩略语 | 全称 | 说明 |
|--------|------|------|
| JWT | JSON Web Token | 认证令牌 |
| DRF | Django REST Framework | REST API框架 |
| CRUD | Create, Read, Update, Delete | 增删改查操作 |
| API | Application Programming Interface | 应用程序接口 |
| ATC | Anatomical Therapeutic Chemical | 解剖学治疗学及化学分类 |

### 10.2 参考文档

- Django官方文档: https://docs.djangoproject.com/
- DRF官方文档: https://www.django-rest-framework.org/
- Vue3官方文档: https://vuejs.org/
- Element Plus: https://element-plus.org/

---

*文档结束*

