#!/bin/bash
# cd ./yyb_be
# ./start.sh
# 医药宝管理系统启动脚本（Mac/Linux）

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

show_menu() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}       医药宝管理系统启动脚本${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo "请选择要启动的系统："
    echo ""
    echo -e "${GREEN}1.${NC} 启动后端服务 (Django)"
    echo -e "${GREEN}2.${NC} 启动后台管理系统 (管理员端) - 端口 5173"
    echo -e "${GREEN}3.${NC} 启动用户端系统 - 端口 3001"
    echo -e "${GREEN}4.${NC} 启动所有服务"
    echo -e "${GREEN}5.${NC} 退出"
    echo ""
}

start_backend() {
    echo -e "${YELLOW}正在启动后端服务...${NC}"
    cd "$SCRIPT_DIR/django"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${RED}错误：虚拟环境不存在，请先创建${NC}"
        return
    fi
    
    # 激活虚拟环境并启动
    source venv/bin/activate
    python manage.py runserver 0.0.0.0:8000 &
    BACKEND_PID=$!
    echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"
    echo -e "${BLUE}访问地址: http://localhost:8000${NC}"
    cd "$SCRIPT_DIR"
}

start_admin() {
    echo -e "${YELLOW}正在启动后台管理系统...${NC}"
    cd "$SCRIPT_DIR/web"
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}正在安装依赖...${NC}"
        npm install
    fi
    
    npm run dev &
    ADMIN_PID=$!
    echo -e "${GREEN}后台管理系统已启动 (PID: $ADMIN_PID)${NC}"
    echo -e "${BLUE}访问地址: http://localhost:5173${NC}"
    cd "$SCRIPT_DIR"
}

start_user() {
    echo -e "${YELLOW}正在启动用户端系统...${NC}"
    cd "$SCRIPT_DIR/user_web"
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}正在安装依赖...${NC}"
        npm install
    fi
    
    npm run dev &
    USER_PID=$!
    echo -e "${GREEN}用户端系统已启动 (PID: $USER_PID)${NC}"
    echo -e "${BLUE}访问地址: http://localhost:3001${NC}"
    cd "$SCRIPT_DIR"
}

start_all() {
    echo -e "${YELLOW}正在启动所有服务...${NC}"
    start_backend
    sleep 2
    start_admin
    sleep 2
    start_user
    echo ""
    echo -e "${GREEN}所有服务已启动！${NC}"
    echo -e "${BLUE}后端: http://localhost:8000${NC}"
    echo -e "${BLUE}后台管理: http://localhost:5173${NC}"
    echo -e "${BLUE}用户端: http://localhost:3001${NC}"
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (1-5): " choice
    
    case $choice in
        1)
            start_backend
            ;;
        2)
            start_admin
            ;;
        3)
            start_user
            ;;
        4)
            start_all
            ;;
        5)
            echo -e "${GREEN}再见！${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效的选项，请重新输入${NC}"
            ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
done
