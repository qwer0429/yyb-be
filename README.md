# 医药宝管理系统

前后端分离的药品信息管理系统，包含**后台管理系统**（管理员端）和**用户端系统**。

## 项目结构

```
yyb-be/
├── django/                 # 后端项目（Django + DRF）
│   ├── manage.py
│   ├── requirements.txt
│   ├── simpleserver/       # Django 配置
│   ├── susers/            # 用户模块
│   └── syyb/              # 药品模块
├── web/                    # 后台管理系统（Vue 3 + TypeScript）- 管理员端
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── user_web/               # 用户端系统（Vue 3 + TypeScript）- 普通用户
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 系统说明

### 后台管理系统（web/）
- **访问对象**: 管理员
- **功能**: 药品管理、分类管理、厂商管理、用户管理等完整功能
- **端口**: 5173

### 用户端系统（user_web/）
- **访问对象**: 普通用户
- **功能**: 
  - 浏览所有药品（只读）
  - 浏览分类（只读）
  - 管理个人药箱（增删改查自己的药品）
- **端口**: 3001

## 角色权限控制

系统分为两种角色：

1. **管理员** (`is_admin = true`)
   - 登录后台管理系统 (`http://localhost:5173`)
   - 拥有所有管理权限

2. **普通用户** (`is_admin = false`)
   - 登录用户端系统 (`http://localhost:3001`)
   - 只能浏览药品和分类
   - 只能管理自己的药箱

## 快速开始

### 方式一：使用启动脚本

```bash
# Windows
start.bat

# Mac/Linux (后台管理系统)
./start-frontend.ps1

# Mac/Linux (用户端系统)
./start-user-web.ps1
```

### 方式二：手动启动

#### 1. 启动后端服务（Django）

```bash
cd django

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖（首次）
pip install -r requirements.txt

# 迁移数据库（首次）
python manage.py migrate

# 创建超级用户（管理员）
python manage.py createsuperuser

# 启动服务
python manage.py runserver
```

后端服务: http://127.0.0.1:8000

#### 2. 启动后台管理系统（管理员端）

```bash
cd web

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

后台管理: http://localhost:5173

#### 3. 启动用户端系统（普通用户）

```bash
cd user_web

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

用户端: http://localhost:3001

## 首次使用设置

### 1. 创建管理员账号

```bash
cd django
source venv/bin/activate
python manage.py createsuperuser
# 按提示输入用户名、邮箱、密码
```

### 2. 创建普通用户

有两种方式：

**方式一：通过 Django Admin**
1. 访问 http://127.0.0.1:8000/admin
2. 使用管理员账号登录
3. 进入 "用户" 管理，添加新用户
4. 确保新用户的 "是否管理员" 字段为 **未选中** 状态

**方式二：通过数据库直接修改**
```bash
cd django
source venv/bin/activate
python manage.py shell

# 在 shell 中执行
from susers.models import User
user = User.objects.create_user('username', 'email@example.com', 'password')
user.is_admin = False  # 设置为普通用户
user.save()
```

## 环境要求

- **后端**: Python 3.8+
- **前端**: Node.js 16+

## 主要功能

### 后台管理系统（管理员）
- 药品信息管理（增删改查、搜索、分页）
- 药品分类管理（一级/二级分类）
- 厂商管理（上市许可持有人、生产厂商）
- 用户管理
- JWT 用户认证
- Excel 批量导入药品

### 用户端系统（普通用户）
- 药品浏览（搜索、查看详情）
- 分类浏览（一级/二级分类）
- 智慧药箱（创建药箱、添加药品、管理库存、有效期提醒）

## 开发说明

### 后端 API 路径

- 登录获取 Token: `POST /api/token/`
- 刷新 Token: `POST /api/refresh/`
- 药品管理: `/syyb/drug/`
- 分类管理: `/syyb/type1drug/`、`/syyb/type2drug/`
- 厂商管理: `/syyb/manufacturer/`、`/syyb/manufacturerholder/`
- 药箱管理: `/syyb/cabinets/`、`/syyb/cabinet_drugs/`

### Token 响应格式

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true
  }
}
```

### 构建生产环境

```bash
# 构建后台管理系统
cd web
npm run build

# 构建用户端系统
cd ../user_web
npm run build
```

构建后的文件分别在 `web/dist` 和 `user_web/dist` 目录。

## 端口说明

| 服务 | 端口 | 访问地址 |
|------|------|----------|
| Django 后端 | 8000 | http://localhost:8000 |
| 后台管理系统 | 5173 | http://localhost:5173 |
| 用户端系统 | 3001 | http://localhost:3001 |
