#!/bin/bash
#
# 医药宝管理系统 - 一键停止脚本（Mac/Linux）
# 功能：根据 PID 文件或端口占用停止所有服务
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 加载统一配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    . "$SCRIPT_DIR/.env" 2>/dev/null
    set +a
fi

# 配置（优先使用 .env 中的值，否则使用默认值）
BACKEND_PORT=${BACKEND_PORT:-8000}
ADMIN_PORT=${ADMIN_PORT:-5173}
USER_PORT=${USER_PORT:-3001}

PID_DIR="$SCRIPT_DIR/.pids"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 根据 PID 文件停止服务（先优雅终止，再强制终止）
stop_by_pid() {
    local pid_file=$1
    local name=$2
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file" 2>/dev/null | tr -d '[:space:]')
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill -15 "$pid" 2>/dev/null
            sleep 1
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
                sleep 0.5
            fi
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${RED}✗ $name 停止失败 (PID: $pid)${NC}"
            else
                echo -e "${GREEN}✓ $name 已停止 (PID: $pid)${NC}"
            fi
        else
            echo -e "${YELLOW}! $name 进程已不存在 (PID: $pid)${NC}"
        fi
        rm -f "$pid_file"
    fi
}

# 根据端口停止服务（兜底清理）
stop_by_port() {
    local port=$1
    local name=$2
    local pids=$(lsof -Pi :"$port" -sTCP:LISTEN -t 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✓ $name (端口 $port) 已停止${NC}"
    fi
}

# 主流程
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}       医药宝管理系统 - 停止服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 先尝试通过 PID 文件停止
stop_by_pid "$PID_DIR/backend.pid" "后端服务"
stop_by_pid "$PID_DIR/admin.pid" "后台管理系统"
stop_by_pid "$PID_DIR/user.pid" "用户端系统"

# 兜底：通过端口强制清理残留进程
stop_by_port $BACKEND_PORT "后端服务"
stop_by_port $ADMIN_PORT "后台管理系统"
stop_by_port $USER_PORT "用户端系统"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}       所有服务已停止！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
