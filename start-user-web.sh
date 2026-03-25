#!/bin/bash

# 医药宝用户端系统启动脚本（Mac/Linux）

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}      医药宝用户端系统启动脚本${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 检查是否在正确的目录
if [ ! -d "$SCRIPT_DIR/user_web" ]; then
    echo -e "${RED}错误：请在项目根目录下运行此脚本${NC}"
    exit 1
fi

# 进入用户端目录
cd "$SCRIPT_DIR/user_web"

# 检查是否需要安装依赖
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}正在安装依赖...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}依赖安装失败${NC}"
        exit 1
    fi
fi

# 启动开发服务器
echo -e "${GREEN}正在启动用户端系统...${NC}"
echo -e "${BLUE}访问地址: http://localhost:3001${NC}"
echo ""
npm run dev
