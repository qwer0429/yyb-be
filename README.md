# 医药宝管理系统

前后端分离的药品信息管理系统。

## 项目结构

```
yyb-be/
├── django/                 # 后端项目（Django + DRF）
│   ├── manage.py
│   ├── requirements.txt
│   ├── simpleserver/       # Django 配置
│   ├── susers/            # 用户模块
│   └── syyb/              # 药品模块
├── web/                    # 前端项目（Vue 3 + TypeScript）
│   ├── src/               # 源代码
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 快速开始

### 1. 后端启动（Django）

```bash
# 进入后端目录
cd django

# 创建虚拟环境（如果还没有）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 迁移数据库
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动服务（端口 8000）
python manage.py runserver
```

后端服务启动后访问：http://127.0.0.1:8000/admin

### 2. 前端启动（Vue）

```bash
# 进入前端目录
cd web

# 安装依赖（如果还没有）
npm install

# 启动开发服务器（端口 5173）
npm run dev
```

前端访问地址：http://localhost:5173

## 登录说明

系统使用 JWT 认证，默认登录接口：
- 需要先在后端创建用户：`python manage.py createsuperuser`
- 前端登录页面使用创建的用户名和密码登录

## 环境要求

- **后端**: Python 3.8+
- **前端**: Node.js 16+

## 主要功能

- 药品信息管理（增删改查、搜索、分页）
- 药品分类管理（一级/二级分类）
- 厂商管理（上市许可持有人、生产厂商）
- JWT 用户认证
- Excel 批量导入药品

## 开发说明

### 后端 API 路径

- 登录获取 Token: `POST /api/token/`
- 刷新 Token: `POST /api/refresh/`
- 药品管理: `/syyb/drug/`
- 分类管理: `/syyb/type1drug/`、`/syyb/type2drug/`
- 厂商管理: `/syyb/manufacturer/`、`/syyb/manufacturerholder/`

### 前端代理配置

前端开发服务器配置代理，将 API 请求转发到后端：
- `/api/*` → `http://127.0.0.1:8000`
- `/syyb/*` → `http://127.0.0.1:8000`
- `/media/*` → `http://127.0.0.1:8000`

### 构建生产环境

```bash
cd web
npm run build
```

构建后的文件在 `web/dist` 目录，可以部署到 Nginx 等静态服务器。
