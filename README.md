# 医药宝管理系统

前后端分离的药品信息管理系统，包含**后台管理系统**（管理员端）和**用户端系统**（普通用户）。

## 系统简介

医药宝管理系统是一款面向医药行业的专业药品信息管理平台，提供完整的药品信息管理、分类管理、厂商管理、智慧药箱等功能，支持药品数据的批量导入、智能搜索和多维度筛选。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                         │
│  ┌──────────────────────┐      ┌──────────────────────┐         │
│  │   后台管理系统        │      │    用户端系统         │         │
│  │   (web/)             │      │    (user_web/)       │         │
│  │   - Vue 3            │      │    - Vue 3           │         │
│  │   - TypeScript       │      │    - TypeScript      │         │
│  │   - Element Plus     │      │    - Element Plus    │         │
│  │   - 端口: 5173       │      │    - 端口: 3001      │         │
│  └──────────┬───────────┘      └──────────┬───────────┘         │
└─────────────┼────────────────────────────┼─────────────────────┘
              │                            │
              └────────────┬───────────────┘
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端层 (Backend)                          │
│                        (django/)                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐      │
│  │    Django   │  │     DRF     │  │    JWT Auth         │      │
│  │  (Web框架)   │  │  (REST框架)  │  │   (认证)             │      │
│  └─────────────┘  └─────────────┘  └─────────────────────┘      │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────┐      ┌─────────────────────┐            │
│  │       MySQL         │      │       Redis         │            │
│  │    (主数据库)        │      │    (缓存)            │            │
│  └─────────────────────┘      └─────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 环境要求

### 后端环境

| 组件 | 版本要求 | 安装包/下载地址 |
|------|---------|----------------|
| Python | 3.9+ | https://www.python.org/downloads/ |
| MySQL | 8.0+ | https://dev.mysql.com/downloads/ |
| Redis | 6.0+ | https://redis.io/download |

**Python 安装包下载：**

| 操作系统 | 安装包名称 |
|---------|-----------|
| Windows (64-bit) | `python-3.9.x-amd64.exe` |
| macOS (Intel) | `python-3.9.x-macos11.pkg` |
| macOS (Apple Silicon) | `python-3.9.x-macos11.pkg` |
| Linux | 通过包管理器安装 |

### 前端环境

| 组件 | 版本要求 | 安装包/下载地址 |
|------|---------|----------------|
| Node.js | 18+ | https://nodejs.org/ |
| npm | 9+ | 随 Node.js 一起安装 |

**Node.js 安装包下载：**

| 操作系统 | 安装包名称 |
|---------|-----------|
| Windows (64-bit) | `node-v18.x.x-x64.msi` |
| macOS (Intel) | `node-v18.x.x.pkg` |
| macOS (Apple Silicon) | `node-v18.x.x-arm64.pkg` |
| Linux (x64) | `node-v18.x.x-linux-x64.tar.xz` |

## 项目结构

```
yyb-be/                         # 项目根目录
├── README.md                   # 项目说明文档
├── SYSTEM_DOCUMENTATION.md     # 系统详细文档
├── FUNCTION_DOCUMENTATION.md   # 功能模块文档
├── system.md                   # 功能开发清单
├── start.sh                    # Mac/Linux 总启动脚本
├── start.bat                   # Windows 启动脚本
├── start-backend.ps1           # 后端启动脚本（PowerShell）
├── start-frontend.ps1          # 后台管理启动脚本（PowerShell）
├── start-user-web.ps1          # 用户端启动脚本（PowerShell）
├── start-user-web.sh           # 用户端启动脚本（Mac/Linux）
│
├── django/                     # 后端 Django 项目
│   ├── manage.py               # Django 管理脚本
│   ├── requirements.txt        # Python 依赖
│   ├── venv/                   # 虚拟环境
│   ├── yyb/                    # 项目配置
│   ├── susers/                 # 用户模块
│   └── syyb/                   # 药品模块
│
├── web/                        # 后台管理系统（管理员端）
│   ├── package.json            # Node.js 依赖
│   ├── vite.config.ts          # Vite 配置
│   ├── src/                    # 源代码
│   └── README.md               # 前端部署文档
│
└── user_web/                   # 用户端系统（普通用户）
    ├── package.json            # Node.js 依赖
    ├── vite.config.ts          # Vite 配置
    └── src/                    # 源代码
```

## 部署步骤

### 一、后端部署

#### 1. 安装 Python 3.9+

**Windows:**
1. 下载 `python-3.9.x-amd64.exe`
2. 安装时勾选 "Add Python to PATH"
3. 点击 "Install Now"

**macOS:**
```bash
# 使用 Homebrew 安装
brew install python@3.9
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-pip
```

#### 2. 安装 MySQL 8.0+

参考官方文档安装并创建数据库：
```sql
CREATE DATABASE yyb_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 3. 安装 Redis 6.0+

**Windows:** 下载安装包或使用 WSL  
**macOS:** `brew install redis`  
**Linux:** `sudo apt install redis-server`

#### 4. 配置并启动后端

```bash
cd django

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置数据库（编辑 yyb/settings.py 中的数据库配置）

# 执行迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动服务
python manage.py runserver
```

后端服务启动后访问：http://127.0.0.1:8000

### 二、前端部署

#### 1. 安装 Node.js 18+

根据操作系统下载对应安装包并安装。

#### 2. 部署后台管理系统

```bash
cd web

# 安装依赖
npm install

# 开发模式启动
npm run dev
```

访问地址：http://localhost:5173

#### 3. 部署用户端系统

```bash
cd user_web

# 安装依赖
npm install

# 开发模式启动
npm run dev
```

访问地址：http://localhost:3001

## 快速启动（使用脚本）

### 一键启动所有服务

脚本功能特点：
- ✅ 自动检测环境依赖（Python、Node.js、MySQL、Redis）
- ✅ 自动检测端口占用，避免冲突
- ✅ 自动安装缺失的 npm 依赖
- ✅ 支持服务状态查看
- ✅ 支持一键停止所有服务
- ✅ 日志输出到 `.logs/` 目录

### Windows

双击运行或在 PowerShell 中执行：

```powershell
# 使用总启动脚本（推荐）
.\start.bat

# 或单独启动各服务
.\start-backend.ps1      # 启动后端服务
.\start-frontend.ps1     # 启动后台管理系统
.\start-user-web.ps1     # 启动用户端系统
```

**脚本菜单选项：**
1. 启动后端服务 (Django) - 端口 8000
2. 启动后台管理系统 (管理员端) - 端口 5173
3. 启动用户端系统 - 端口 3001
4. 启动所有服务
5. 查看服务状态
6. 停止所有服务
7. 退出

### Mac/Linux

```bash
# 使用总启动脚本（推荐）
chmod +x start.sh
./start.sh

# 或单独启动各服务
./start-backend.sh        # 启动后端服务（如需要可创建）
./start-user-web.sh       # 启动用户端系统
```

**脚本菜单选项：**
1. 启动后端服务 (Django) - 端口 8000
2. 启动后台管理系统 (管理员端) - 端口 5173
3. 启动用户端系统 - 端口 3001
4. 启动所有服务
5. 查看服务状态
6. 停止所有服务
7. 退出

### 启动脚本文件说明

| 脚本文件 | 适用系统 | 功能 |
|---------|---------|------|
| `start.bat` | Windows | 总启动脚本，支持菜单选择 |
| `start.sh` | Mac/Linux | 总启动脚本，支持菜单选择 |
| `start-backend.ps1` | Windows | 单独启动后端服务 |
| `start-frontend.ps1` | Windows | 单独启动后台管理系统 |
| `start-user-web.ps1` | Windows | 单独启动用户端系统 |
| `start-user-web.sh` | Mac/Linux | 单独启动用户端系统 |

## 服务端口说明

| 服务 | 端口 | 访问地址 | 说明 |
|------|------|----------|------|
| Django 后端 | 8000 | http://localhost:8000 | REST API 服务 |
| Django Admin | 8000 | http://localhost:8000/admin | 管理员后台 |
| 后台管理系统 | 5173 | http://localhost:5173 | 管理员前端 |
| 用户端系统 | 3001 | http://localhost:3001 | 普通用户前端 |

## 用户类型与权限

### 1. 管理员 (is_admin = true)
- 登录后台管理系统 (`http://localhost:5173`)
- 拥有所有管理权限：
  - 药品信息管理（增删改查、搜索、分页）
  - 药品分类管理（一级/二级分类）
  - 厂商管理（上市许可持有人、生产厂商）
  - 用户管理
  - Excel 批量导入药品

### 2. 普通用户 (is_admin = false)
- 登录用户端系统 (`http://localhost:3001`)
- 功能权限：
  - 浏览所有药品（只读）
  - 浏览分类（只读）
  - 管理个人药箱（增删改查自己的药品）
  - 有效期提醒

## 创建用户

### 创建管理员账号

```bash
cd django
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows

python manage.py createsuperuser
# 按提示输入用户名、邮箱、密码
```

### 创建普通用户

**方式一：通过 Django Admin**
1. 访问 http://127.0.0.1:8000/admin
2. 使用管理员账号登录
3. 进入 "用户" 管理，添加新用户
4. 确保新用户的 "是否管理员" 字段为 **未选中** 状态

**方式二：通过 API 注册**
前端用户端系统提供用户注册功能。

## 主要功能

### 后台管理系统（管理员端）

| 功能模块 | 功能描述 |
|---------|---------|
| 🔐 用户认证 | JWT Token 认证，登录/登出 |
| 📦 药品管理 | 增删改查、搜索、分页、图片上传 |
| 📥 Excel 导入 | 批量导入药品数据 |
| 🏷️ 分类管理 | 一级/二级分类 CRUD |
| 🏭 厂商管理 | 持证商和生产商管理 |
| 📊 数据统计 | 可视化数据仪表盘 |

### 用户端系统（普通用户）

| 功能模块 | 功能描述 |
|---------|---------|
| 🔐 用户认证 | 注册、登录、JWT Token |
| 🔍 药品浏览 | 搜索、查看详情、分类筛选 |
| 📦 智慧药箱 | 创建药箱、添加药品、管理库存 |
| ⏰ 有效期提醒 | 自动计算过期时间、即将过期提醒 |

## API 接口

### 认证接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/token/` | POST | 登录获取 Token |
| `/api/refresh/` | POST | 刷新 Token |

### 药品管理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/syyb/drug/` | GET/POST | 药品列表/创建 |
| `/syyb/drug/{id}/` | GET/PUT/DELETE | 药品详情/更新/删除 |
| `/syyb/search_anything/` | GET | 搜索药品 |
| `/syyb/add_drugs_from_excel/` | POST | Excel 导入药品 |
| `/syyb/batch_delete_drugs/` | POST | 批量删除药品 |

### 分类管理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/syyb/type1drug/` | GET/POST | 一级分类列表/创建 |
| `/syyb/type2drug/` | GET/POST | 二级分类列表/创建 |

### 厂商管理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/syyb/manufacturerholder/` | GET/POST | 持证商列表/创建 |
| `/syyb/manufacturer/` | GET/POST | 生产商列表/创建 |

### 药箱管理接口（用户端）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/syyb/cabinets/` | GET/POST | 药箱列表/创建 |
| `/syyb/cabinet_drugs/` | GET/POST | 药箱药品列表/添加 |

## 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 编程语言 |
| Django | 4.x | Web 框架 |
| Django REST Framework | 3.14+ | REST API 开发 |
| djangorestframework-simplejwt | 5.x | JWT 认证 |
| MySQL | 8.0+ | 主数据库 |
| Redis | 6.x+ | 缓存、Session 存储 |
| openpyxl | 3.x | Excel 文件处理 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.3+ | 前端框架 |
| TypeScript | 5.x | 类型安全 |
| Element Plus | 2.4+ | UI 组件库 |
| Pinia | 2.1+ | 状态管理 |
| Vue Router | 4.x | 路由管理 |
| Axios | 1.6+ | HTTP 请求 |
| Vite | 8.x | 构建工具 |

## Token 响应格式

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

## 生产环境构建

```bash
# 构建后台管理系统
cd web
npm run build
# 输出目录: web/dist

# 构建用户端系统
cd ../user_web
npm run build
# 输出目录: user_web/dist
```

## 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 系统详细文档 | `SYSTEM_DOCUMENTATION.md` | 系统架构、数据库设计、API 详情 |
| 功能模块文档 | `FUNCTION_DOCUMENTATION.md` | 各功能模块详细说明 |
| 开发任务清单 | `system.md` | 功能开发进度跟踪 |
| 前端部署文档 | `web/README.md` | 前端环境配置和部署 |

## 常见问题

### 1. 脚本启动问题

**环境检查失败**
```bash
# 检查 Python
python --version           # Windows
python3 --version          # Mac/Linux

# 检查 Node.js
node --version

# 检查 MySQL 服务是否运行
mysql -u root -p -e "SELECT 1"

# 检查 Redis 服务是否运行
redis-cli ping             # 应返回 PONG
```

**端口被占用**
```bash
# Mac/Linux 查看端口占用
lsof -i :8000
lsof -i :5173
lsof -i :3001

# Windows 查看端口占用
netstat -ano | findstr :8000

# 使用脚本选项 6 停止所有服务，或手动终止进程
```

**依赖安装失败**
```bash
# 清理 npm 缓存
npm cache clean --force

# 删除 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install

# 使用国内镜像源加速
npm config set registry https://registry.npmmirror.com
```

### 2. 后端启动失败

**查看日志**
```bash
# Mac/Linux 使用脚本启动时的日志
tail -f .logs/backend.log

# 手动启动查看详细错误
cd django
source venv/bin/activate
python manage.py runserver
```

**常见问题**
- 检查 MySQL 服务是否启动
- 检查数据库配置是否正确（`django/yyb/settings.py`）
- 确认虚拟环境已激活
- 确认已执行数据库迁移：`python manage.py migrate`

### 3. 前端启动失败

**查看日志**
```bash
# Mac/Linux 使用脚本启动时的日志
tail -f .logs/admin.log      # 后台管理
tail -f .logs/user.log       # 用户端
```

**常见问题**
- 检查 Node.js 版本是否 18+
- 删除 `node_modules` 重新安装：`rm -rf node_modules && npm install`
- 检查后端服务是否已启动

### 4. API 请求失败

- 确认后端服务运行在 http://localhost:8000
- 检查前端代理配置（`vite.config.ts`）
- 确认已正确登录并获取 Token
- 检查浏览器开发者工具中的网络请求错误

### 5. 停止服务

**使用脚本停止（推荐）**
```bash
# Mac/Linux
./start.sh
# 选择选项 6: 停止所有服务

# Windows
.\start.bat
# 选择选项 6: 停止所有服务
```

**手动停止**
```bash
# Mac/Linux 查找并终止进程
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
lsof -ti:3001 | xargs kill -9

# Windows 使用任务管理器
# 或命令行：taskkill /F /IM python.exe /IM node.exe
```

## 版权信息

本项目为毕业设计项目，仅供学习交流使用。
