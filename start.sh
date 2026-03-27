#!/bin/bash
#
# 医药宝管理系统 - 一键启动脚本（Mac/Linux）
# 功能：启动后端服务、后台管理系统、用户端系统
#

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# PID 文件目录
PID_DIR="$SCRIPT_DIR/.pids"
LOG_DIR="$SCRIPT_DIR/.logs"

# 创建必要的目录
mkdir -p "$PID_DIR" "$LOG_DIR"

# 服务配置
BACKEND_PORT=8000
ADMIN_PORT=5173
USER_PORT=3001

# ==================== 工具函数 ====================

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        return 1
    fi
    return 0
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 获取占用端口的进程 PID
get_port_pid() {
    local port=$1
    lsof -Pi :"$port" -sTCP:LISTEN -t 2>/dev/null
}

# 检查服务是否运行
check_service_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# ==================== 检查函数 ====================

# 检查 Python 环境
check_python() {
    echo -e "${CYAN}检查 Python 环境...${NC}"
    if ! check_command python3; then
        echo -e "${RED}✗ Python3 未安装${NC}"
        echo -e "${YELLOW}请安装 Python 3.9+ : https://www.python.org/downloads/${NC}"
        return 1
    fi
    
    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python 版本: $python_version${NC}"
    return 0
}

# 检查 Node.js 环境
check_nodejs() {
    echo -e "${CYAN}检查 Node.js 环境...${NC}"
    if ! check_command node; then
        echo -e "${RED}✗ Node.js 未安装${NC}"
        echo -e "${YELLOW}请安装 Node.js 18+ : https://nodejs.org/${NC}"
        return 1
    fi
    
    local node_version=$(node --version)
    echo -e "${GREEN}✓ Node.js 版本: $node_version${NC}"
    return 0
}

# 检查 MySQL
check_mysql() {
    echo -e "${CYAN}检查 MySQL...${NC}"
    if check_command mysql; then
        local mysql_version=$(mysql --version 2>&1 | awk '{print $3}' | tr -d ',')
        echo -e "${GREEN}✓ MySQL 版本: $mysql_version${NC}"
    else
        echo -e "${YELLOW}! MySQL 客户端未找到，请确保 MySQL 服务已运行${NC}"
    fi
    return 0
}

# 检查 Redis
check_redis() {
    echo -e "${CYAN}检查 Redis...${NC}"
    if check_command redis-cli; then
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis 服务运行正常${NC}"
        else
            echo -e "${YELLOW}! Redis 客户端已安装，但服务可能未运行${NC}"
            echo -e "${YELLOW}  请启动 Redis: redis-server${NC}"
        fi
    else
        echo -e "${YELLOW}! Redis 未安装（可选）${NC}"
    fi
    return 0
}

# 检查虚拟环境
check_venv() {
    if [ ! -d "$SCRIPT_DIR/django/venv" ]; then
        echo -e "${RED}✗ Python 虚拟环境不存在${NC}"
        echo -e "${YELLOW}请先创建虚拟环境:${NC}"
        echo -e "  cd django"
        echo -e "  python3 -m venv venv"
        echo -e "  source venv/bin/activate"
        echo -e "  pip install -r requirements.txt"
        return 1
    fi
    echo -e "${GREEN}✓ Python 虚拟环境已存在${NC}"
    return 0
}

# 检查 node_modules
check_node_modules() {
    local dir=$1
    local name=$2
    if [ ! -d "$dir/node_modules" ]; then
        echo -e "${YELLOW}! $name 依赖未安装，将自动安装...${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ $name 依赖已安装${NC}"
    return 0
}

# 检查所有依赖
check_all_dependencies() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}       环境依赖检查${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    local has_error=0
    
    check_python || has_error=1
    check_nodejs || has_error=1
    check_mysql
    check_redis
    
    echo ""
    
    if [ $has_error -eq 1 ]; then
        echo -e "${RED}✗ 环境检查失败，请先安装缺失的依赖${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ 基础环境检查通过${NC}"
    return 0
}

# ==================== 启动函数 ====================

# 启动后端服务
start_backend() {
    echo ""
    echo -e "${CYAN}----------------------------------------${NC}"
    echo -e "${CYAN}       启动后端服务 (Django)${NC}"
    echo -e "${CYAN}----------------------------------------${NC}"
    echo ""
    
    # 检查端口占用
    if check_port $BACKEND_PORT; then
        local pid=$(get_port_pid $BACKEND_PORT)
        echo -e "${YELLOW}! 端口 $BACKEND_PORT 已被占用 (PID: $pid)${NC}"
        echo -e "${YELLOW}  后端服务可能已在运行${NC}"
        echo -e "${BLUE}  访问地址: http://localhost:$BACKEND_PORT${NC}"
        return 0
    fi
    
    # 检查虚拟环境
    if ! check_venv; then
        return 1
    fi
    
    cd "$SCRIPT_DIR/django"
    
    # 激活虚拟环境并启动
    echo -e "${YELLOW}正在启动 Django 服务...${NC}"
    source venv/bin/activate
    
    # 检查数据库迁移
    echo -e "${CYAN}检查数据库...${NC}"
    python manage.py migrate --check > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}! 数据库需要迁移，正在执行...${NC}"
        python manage.py migrate
    fi
    
    # 启动服务（后台运行）
    nohup python manage.py runserver 0.0.0.0:$BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    
    # 保存 PID
    echo $BACKEND_PID > "$PID_DIR/backend.pid"
    
    # 等待服务启动
    sleep 2
    
    if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 后端服务已启动${NC}"
        echo -e "${BLUE}  PID: $BACKEND_PID${NC}"
        echo -e "${BLUE}  访问地址: http://localhost:$BACKEND_PORT${NC}"
        echo -e "${BLUE}  日志文件: .logs/backend.log${NC}"
    else
        echo -e "${RED}✗ 后端服务启动失败${NC}"
        echo -e "${YELLOW}  请查看日志: .logs/backend.log${NC}"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    return 0
}

# 启动后台管理系统
start_admin() {
    echo ""
    echo -e "${CYAN}----------------------------------------${NC}"
    echo -e "${CYAN}    启动后台管理系统 (管理员端)${NC}"
    echo -e "${CYAN}----------------------------------------${NC}"
    echo ""
    
    # 检查端口占用
    if check_port $ADMIN_PORT; then
        local pid=$(get_port_pid $ADMIN_PORT)
        echo -e "${YELLOW}! 端口 $ADMIN_PORT 已被占用 (PID: $pid)${NC}"
        echo -e "${YELLOW}  后台管理系统可能已在运行${NC}"
        echo -e "${BLUE}  访问地址: http://localhost:$ADMIN_PORT${NC}"
        return 0
    fi
    
    cd "$SCRIPT_DIR/web"
    
    # 检查并安装依赖
    if ! check_node_modules "$SCRIPT_DIR/web" "后台管理系统"; then
        echo -e "${YELLOW}正在安装依赖...${NC}"
        npm install
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ 依赖安装失败${NC}"
            cd "$SCRIPT_DIR"
            return 1
        fi
    fi
    
    # 启动服务
    echo -e "${YELLOW}正在启动 Vue 开发服务器...${NC}"
    nohup npm run dev > "$LOG_DIR/admin.log" 2>&1 &
    ADMIN_PID=$!
    
    # 保存 PID
    echo $ADMIN_PID > "$PID_DIR/admin.pid"
    
    # 等待服务启动
    sleep 3
    
    if ps -p "$ADMIN_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 后台管理系统已启动${NC}"
        echo -e "${BLUE}  PID: $ADMIN_PID${NC}"
        echo -e "${BLUE}  访问地址: http://localhost:$ADMIN_PORT${NC}"
        echo -e "${BLUE}  日志文件: .logs/admin.log${NC}"
    else
        echo -e "${RED}✗ 后台管理系统启动失败${NC}"
        echo -e "${YELLOW}  请查看日志: .logs/admin.log${NC}"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    return 0
}

# 启动用户端系统
start_user() {
    echo ""
    echo -e "${CYAN}----------------------------------------${NC}"
    echo -e "${CYAN}      启动用户端系统${NC}"
    echo -e "${CYAN}----------------------------------------${NC}"
    echo ""
    
    # 检查端口占用
    if check_port $USER_PORT; then
        local pid=$(get_port_pid $USER_PORT)
        echo -e "${YELLOW}! 端口 $USER_PORT 已被占用 (PID: $pid)${NC}"
        echo -e "${YELLOW}  用户端系统可能已在运行${NC}"
        echo -e "${BLUE}  访问地址: http://localhost:$USER_PORT${NC}"
        return 0
    fi
    
    cd "$SCRIPT_DIR/user_web"
    
    # 检查并安装依赖
    if ! check_node_modules "$SCRIPT_DIR/user_web" "用户端系统"; then
        echo -e "${YELLOW}正在安装依赖...${NC}"
        npm install
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ 依赖安装失败${NC}"
            cd "$SCRIPT_DIR"
            return 1
        fi
    fi
    
    # 启动服务
    echo -e "${YELLOW}正在启动 Vue 开发服务器...${NC}"
    nohup npm run dev > "$LOG_DIR/user.log" 2>&1 &
    USER_PID=$!
    
    # 保存 PID
    echo $USER_PID > "$PID_DIR/user.pid"
    
    # 等待服务启动
    sleep 3
    
    if ps -p "$USER_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 用户端系统已启动${NC}"
        echo -e "${BLUE}  PID: $USER_PID${NC}"
        echo -e "${BLUE}  访问地址: http://localhost:$USER_PORT${NC}"
        echo -e "${BLUE}  日志文件: .logs/user.log${NC}"
    else
        echo -e "${RED}✗ 用户端系统启动失败${NC}"
        echo -e "${YELLOW}  请查看日志: .logs/user.log${NC}"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    return 0
}

# 启动所有服务
start_all() {
    echo ""
    echo -e "${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}       正在启动所有服务${NC}"
    echo -e "${MAGENTA}========================================${NC}"
    echo ""
    
    # 检查依赖
    if ! check_all_dependencies; then
        return 1
    fi
    
    # 启动各个服务
    start_backend
    sleep 2
    start_admin
    sleep 2
    start_user
    
    # 显示汇总信息
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}       所有服务启动完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${CYAN}服务访问地址：${NC}"
    echo -e "  ${BLUE}后端 API:${NC}      http://localhost:$BACKEND_PORT"
    echo -e "  ${BLUE}Django Admin:${NC}  http://localhost:$BACKEND_PORT/admin"
    echo -e "  ${BLUE}后台管理系统:${NC}  http://localhost:$ADMIN_PORT"
    echo -e "  ${BLUE}用户端系统:${NC}    http://localhost:$USER_PORT"
    echo ""
    echo -e "${CYAN}日志文件位置：${NC}"
    echo -e "  ${BLUE}后端:${NC}  .logs/backend.log"
    echo -e "  ${BLUE}管理:${NC}  .logs/admin.log"
    echo -e "  ${BLUE}用户:${NC}  .logs/user.log"
    echo ""
    echo -e "${YELLOW}提示：使用选项 6 可以停止所有服务${NC}"
}

# ==================== 停止函数 ====================

# 停止服务
stop_service() {
    local name=$1
    local pid_file=$2
    local port=$3
    
    echo -e "${YELLOW}正在停止 $name...${NC}"
    
    # 尝试从 PID 文件停止
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null
            sleep 1
            # 强制终止
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null
            fi
        fi
        rm -f "$pid_file"
    fi
    
    # 尝试从端口停止
    if check_port "$port"; then
        local pid=$(get_port_pid "$port")
        if [ -n "$pid" ]; then
            kill -9 "$pid" 2>/dev/null
        fi
    fi
    
    echo -e "${GREEN}✓ $name 已停止${NC}"
}

# 停止所有服务
stop_all() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}       正在停止所有服务${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    stop_service "后端服务" "$PID_DIR/backend.pid" $BACKEND_PORT
    stop_service "后台管理系统" "$PID_DIR/admin.pid" $ADMIN_PORT
    stop_service "用户端系统" "$PID_DIR/user.pid" $USER_PORT
    
    echo ""
    echo -e "${GREEN}✓ 所有服务已停止${NC}"
}

# ==================== 状态检查 ====================

check_status() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}       服务运行状态${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    local any_running=false
    
    # 检查后端
    if check_port $BACKEND_PORT; then
        local pid=$(get_port_pid $BACKEND_PORT)
        echo -e "${GREEN}✓ 后端服务${NC}      ${BLUE}运行中${NC} (PID: $pid, 端口: $BACKEND_PORT)"
        any_running=true
    else
        echo -e "${RED}✗ 后端服务${NC}      ${YELLOW}未运行${NC}"
    fi
    
    # 检查后台管理
    if check_port $ADMIN_PORT; then
        local pid=$(get_port_pid $ADMIN_PORT)
        echo -e "${GREEN}✓ 后台管理系统${NC}  ${BLUE}运行中${NC} (PID: $pid, 端口: $ADMIN_PORT)"
        any_running=true
    else
        echo -e "${RED}✗ 后台管理系统${NC}  ${YELLOW}未运行${NC}"
    fi
    
    # 检查用户端
    if check_port $USER_PORT; then
        local pid=$(get_port_pid $USER_PORT)
        echo -e "${GREEN}✓ 用户端系统${NC}    ${BLUE}运行中${NC} (PID: $pid, 端口: $USER_PORT)"
        any_running=true
    else
        echo -e "${RED}✗ 用户端系统${NC}    ${YELLOW}未运行${NC}"
    fi
    
    echo ""
    
    if [ "$any_running" = true ]; then
        echo -e "${CYAN}访问地址：${NC}"
        check_port $BACKEND_PORT && echo -e "  ${BLUE}后端:${NC}      http://localhost:$BACKEND_PORT"
        check_port $ADMIN_PORT && echo -e "  ${BLUE}后台管理:${NC}  http://localhost:$ADMIN_PORT"
        check_port $USER_PORT && echo -e "  ${BLUE}用户端:${NC}    http://localhost:$USER_PORT"
    fi
}

# ==================== 菜单 ====================

show_menu() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}       医药宝管理系统启动脚本${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${GREEN}1.${NC} 启动后端服务 (Django)          ${BLUE}端口: $BACKEND_PORT${NC}"
    echo -e "${GREEN}2.${NC} 启动后台管理系统 (管理员端)    ${BLUE}端口: $ADMIN_PORT${NC}"
    echo -e "${GREEN}3.${NC} 启动用户端系统                 ${BLUE}端口: $USER_PORT${NC}"
    echo -e "${GREEN}4.${NC} 启动所有服务"
    echo -e "${GREEN}5.${NC} 查看服务状态"
    echo -e "${GREEN}6.${NC} 停止所有服务"
    echo -e "${GREEN}7.${NC} 退出"
    echo ""
}

# ==================== 主程序 ====================

# 捕获 Ctrl+C 信号
trap 'echo -e "\n\n${YELLOW}收到中断信号，正在清理...${NC}"; stop_all; exit 0' INT

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (1-7): " choice
    
    case $choice in
        1)
            check_all_dependencies && start_backend
            ;;
        2)
            check_all_dependencies && start_admin
            ;;
        3)
            check_all_dependencies && start_user
            ;;
        4)
            start_all
            ;;
        5)
            check_status
            ;;
        6)
            stop_all
            ;;
        7)
            echo ""
            echo -e "${GREEN}感谢使用，再见！${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效的选项，请重新输入${NC}"
            ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
done
