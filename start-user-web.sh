#!/bin/bash
#
# 医药宝用户端系统启动脚本（Mac/Linux）
#

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 加载统一配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# 配置
SERVICE_HOST=${SERVICE_HOST:-localhost}
USER_PORT=${USER_PORT:-3001}

# 导出给子进程（Vite 前端需要）
export SERVICE_HOST USER_PORT BACKEND_PORT
export VITE_SERVICE_HOST=$SERVICE_HOST
export VITE_BACKEND_PORT=$BACKEND_PORT
export VITE_USER_PORT=$USER_PORT

# 检查 Node.js
echo -e "${CYAN}[检查]${NC} Node.js 环境..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}[错误]${NC} Node.js 未安装"
    echo -e "${YELLOW}[提示]${NC} 请安装 Node.js 18+ : https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}[通过]${NC} Node.js 版本: $NODE_VERSION"

# 检查目录
if [ ! -d "$SCRIPT_DIR/user_web" ]; then
    echo -e "${RED}[错误]${NC} 找不到 user_web 目录"
    exit 1
fi

# 检查端口占用
if lsof -Pi :"$USER_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}[提示]${NC} 端口 $USER_PORT 已被占用"
    echo -e "${YELLOW}[提示]${NC} 用户端系统可能已在运行"
    echo -e "${BLUE}[提示]${NC} 访问地址: http://$SERVICE_HOST:$USER_PORT"
    exit 0
fi

# 进入目录
cd "$SCRIPT_DIR/user_web"

# 检查并安装依赖
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}[提示]${NC} 依赖未安装，正在安装..."
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误]${NC} 依赖安装失败"
        exit 1
    fi
fi

# 启动服务
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}      医药宝用户端系统启动脚本${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}[启动]${NC} 正在启动 Vue 开发服务器..."
echo ""
echo -e "${BLUE}访问地址: http://$SERVICE_HOST:$USER_PORT${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

npm run dev
