#!/bin/bash
#
# 医药宝管理系统 - 一键启动脚本（Mac/Linux）
# 功能：检查端口占用，若占用则杀死进程，然后启动服务
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 加载统一配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
else
    echo -e "${YELLOW}警告：找不到 .env 配置文件，使用默认值 localhost${NC}"
    echo -e "${YELLOW}      如需自定义IP，请在项目根目录创建 .env 文件${NC}"
fi

# 配置（优先使用 .env 中的值，否则使用默认值）
SERVICE_HOST=${SERVICE_HOST:-localhost}
BACKEND_PORT=${BACKEND_PORT:-8000}
ADMIN_PORT=${ADMIN_PORT:-5173}
USER_PORT=${USER_PORT:-3001}

# 导出给子进程（Vite 前端需要）
export SERVICE_HOST BACKEND_PORT ADMIN_PORT USER_PORT
export VITE_SERVICE_HOST=$SERVICE_HOST
export VITE_BACKEND_PORT=$BACKEND_PORT
export VITE_ADMIN_PORT=$ADMIN_PORT
export VITE_USER_PORT=$USER_PORT
# 覆盖前端 .env.development 中的默认值
export VITE_ADMIN_URL=http://$SERVICE_HOST:$ADMIN_PORT
export VITE_USER_WEB_URL=http://$SERVICE_HOST:$USER_PORT
export VITE_API_BASE_URL=http://$SERVICE_HOST:$BACKEND_PORT

# 调试输出（确认配置已加载）
echo "[配置] 服务IP: $SERVICE_HOST, 后端端口: $BACKEND_PORT, 管理端口: $ADMIN_PORT, 用户端口: $USER_PORT"

PID_DIR="$SCRIPT_DIR/.pids"
LOG_DIR="$SCRIPT_DIR/.logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查并释放端口
free_port() {
    local port=$1
    local name=$2
    local pids=$(lsof -Pi :"$port" -sTCP:LISTEN -t 2>/dev/null)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}端口 $port 被占用，正在释放 ($name)...${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# 启动后端
start_backend() {
    free_port $BACKEND_PORT "后端服务"
    cd "$SCRIPT_DIR/django"
    . venv/bin/activate
    nohup python manage.py runserver 0.0.0.0:$BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$PID_DIR/backend.pid"
    echo -e "${GREEN}✓ 后端服务已启动${NC} ${BLUE}http://$SERVICE_HOST:$BACKEND_PORT${NC}"
}

# 启动管理端
start_admin() {
    free_port $ADMIN_PORT "后台管理系统"
    cd "$SCRIPT_DIR/web"
    nohup npm run dev > "$LOG_DIR/admin.log" 2>&1 &
    echo $! > "$PID_DIR/admin.pid"
    echo -e "${GREEN}✓ 后台管理系统已启动${NC} ${BLUE}http://$SERVICE_HOST:$ADMIN_PORT${NC}"
}

# 启动用户端
start_user() {
    free_port $USER_PORT "用户端系统"
    cd "$SCRIPT_DIR/user_web"
    nohup npm run dev > "$LOG_DIR/user.log" 2>&1 &
    echo $! > "$PID_DIR/user.pid"
    echo -e "${GREEN}✓ 用户端系统已启动${NC} ${BLUE}http://$SERVICE_HOST:$USER_PORT${NC}"
}

# 主流程
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}       医药宝管理系统 - 启动服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

start_backend
sleep 2
start_admin
sleep 2
start_user

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}       所有服务启动完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}访问地址：${NC}"
echo -e "  后端 API:      http://$SERVICE_HOST:$BACKEND_PORT"
echo -e "  Django Admin:  http://$SERVICE_HOST:$BACKEND_PORT/admin"
echo -e "  后台管理系统:  http://$SERVICE_HOST:$ADMIN_PORT"
echo -e "  用户端系统:    http://$SERVICE_HOST:$USER_PORT"
echo ""
echo -e "${BLUE}日志文件：${NC}"
echo -e "  后端:  $LOG_DIR/backend.log"
echo -e "  管理:  $LOG_DIR/admin.log"
echo -e "  用户:  $LOG_DIR/user.log"
echo ""
