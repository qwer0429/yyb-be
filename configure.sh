#!/bin/bash
# ============================================
# 医药宝管理系统 - 统一配置同步脚本 (Mac/Linux)
# 功能：读取根目录 .env，一键同步到所有相关配置文件
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ENV_FILE="$SCRIPT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}错误：找不到 .env 配置文件${NC}"
    echo -e "${YELLOW}请确保 .env 文件位于项目根目录${NC}"
    exit 1
fi

# 读取 .env（只读取 KEY=VALUE 格式，忽略注释和变量引用）
while IFS= read -r line || [[ -n "$line" ]]; do
    # 跳过空行和注释行
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    # 跳过包含 ${ 的变量引用行（Shell不支持递归解析）
    [[ "$line" =~ \$\{ ]] && continue
    # 跳过包含 ${ 的变量引用行
    if [[ "$line" == *'${'* ]]; then
        continue
    fi
    # 导出变量
    if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        # 去除首尾空格
        value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        # 去除引号
        value=$(echo "$value" | sed "s/^['\"]//;s/['\"]$//")
        export "$key=$value"
    fi
done < "$ENV_FILE"

# 拼接完整URL（如果上面没有读到）
SERVICE_HOST=${SERVICE_HOST:-localhost}
BACKEND_PORT=${BACKEND_PORT:-8000}
ADMIN_PORT=${ADMIN_PORT:-5173}
USER_PORT=${USER_PORT:-3001}

BACKEND_URL="http://${SERVICE_HOST}:${BACKEND_PORT}"
ADMIN_URL="http://${SERVICE_HOST}:${ADMIN_PORT}"
USER_URL="http://${SERVICE_HOST}:${USER_PORT}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}       医药宝 - 统一配置同步工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}当前统一配置：${NC}"
echo -e "  服务IP:   ${GREEN}${SERVICE_HOST}${NC}"
echo -e "  后端端口: ${GREEN}${BACKEND_PORT}${NC}"
echo -e "  管理端口: ${GREEN}${ADMIN_PORT}${NC}"
echo -e "  用户端口: ${GREEN}${USER_PORT}${NC}"
echo ""

# 计数器
UPDATED=0

# ============================================
# 1. web/vite.config.ts - 代理目标地址
# ============================================
if [ -f "web/vite.config.ts" ]; then
    sed -i '' "s|target: 'http://[^']*:${BACKEND_PORT}'|target: '${BACKEND_URL}'|g" web/vite.config.ts 2>/dev/null || \
    sed -i    "s|target: 'http://[^']*:${BACKEND_PORT}'|target: '${BACKEND_URL}'|g" web/vite.config.ts
    echo -e "${GREEN}✓${NC} web/vite.config.ts  代理地址 → ${BACKEND_URL}"
    UPDATED=$((UPDATED + 1))
fi

# ============================================
# 2. user_web/vite.config.ts - 代理目标地址
# ============================================
if [ -f "user_web/vite.config.ts" ]; then
    sed -i '' "s|target: 'http://[^']*:${BACKEND_PORT}'|target: '${BACKEND_URL}'|g" user_web/vite.config.ts 2>/dev/null || \
    sed -i    "s|target: 'http://[^']*:${BACKEND_PORT}'|target: '${BACKEND_URL}'|g" user_web/vite.config.ts
    echo -e "${GREEN}✓${NC} user_web/vite.config.ts  代理地址 → ${BACKEND_URL}"
    UPDATED=$((UPDATED + 1))
fi

# ============================================
# 3. web/.env.development - 用户端跳转地址
# ============================================
if [ -f "web/.env.development" ]; then
    if grep -q "^VITE_USER_WEB_URL" web/.env.development; then
        sed -i '' "s|^VITE_USER_WEB_URL.*|VITE_USER_WEB_URL = '${USER_URL}'|" web/.env.development 2>/dev/null || \
        sed -i    "s|^VITE_USER_WEB_URL.*|VITE_USER_WEB_URL = '${USER_URL}'|" web/.env.development
    else
        echo "VITE_USER_WEB_URL = '${USER_URL}'" >> web/.env.development
    fi
    echo -e "${GREEN}✓${NC} web/.env.development  VITE_USER_WEB_URL → ${USER_URL}"
    UPDATED=$((UPDATED + 1))
fi

# ============================================
# 4. web/.env.production - API基础地址
# ============================================
if [ -f "web/.env.production" ]; then
    if grep -q "^VITE_API_BASE_URL" web/.env.production; then
        sed -i '' "s|^VITE_API_BASE_URL.*|VITE_API_BASE_URL = '${BACKEND_URL}'|" web/.env.production 2>/dev/null || \
        sed -i    "s|^VITE_API_BASE_URL.*|VITE_API_BASE_URL = '${BACKEND_URL}'|" web/.env.production
    else
        echo "VITE_API_BASE_URL = '${BACKEND_URL}'" >> web/.env.production
    fi
    echo -e "${GREEN}✓${NC} web/.env.production   VITE_API_BASE_URL → ${BACKEND_URL}"
    UPDATED=$((UPDATED + 1))
fi

# ============================================
# 5. user_web/.env.development - API和管理端地址
# ============================================
if [ -f "user_web/.env.development" ]; then
    if grep -q "^VITE_API_BASE_URL" user_web/.env.development; then
        sed -i '' "s|^VITE_API_BASE_URL.*|VITE_API_BASE_URL=${BACKEND_URL}|" user_web/.env.development 2>/dev/null || \
        sed -i    "s|^VITE_API_BASE_URL.*|VITE_API_BASE_URL=${BACKEND_URL}|" user_web/.env.development
    else
        echo "VITE_API_BASE_URL=${BACKEND_URL}" >> user_web/.env.development
    fi
    if grep -q "^VITE_ADMIN_URL" user_web/.env.development; then
        sed -i '' "s|^VITE_ADMIN_URL.*|VITE_ADMIN_URL=${ADMIN_URL}|" user_web/.env.development 2>/dev/null || \
        sed -i    "s|^VITE_ADMIN_URL.*|VITE_ADMIN_URL=${ADMIN_URL}|" user_web/.env.development
    else
        echo "VITE_ADMIN_URL=${ADMIN_URL}" >> user_web/.env.development
    fi
    echo -e "${GREEN}✓${NC} user_web/.env.development  VITE_API_BASE_URL → ${BACKEND_URL}"
    echo -e "${GREEN}✓${NC} user_web/.env.development  VITE_ADMIN_URL    → ${ADMIN_URL}"
    UPDATED=$((UPDATED + 1))
fi

# ============================================
# 6. user_web/src/views/LoginView.vue - 硬编码管理端地址
# ============================================
if [ -f "user_web/src/views/LoginView.vue" ]; then
    sed -i '' "s|'http://[^']*:${ADMIN_PORT}'|'${ADMIN_URL}'|g" user_web/src/views/LoginView.vue 2>/dev/null || \
    sed -i    "s|'http://[^']*:${ADMIN_PORT}'|'${ADMIN_URL}'|g" user_web/src/views/LoginView.vue
    echo -e "${GREEN}✓${NC} LoginView.vue  管理端跳转地址 → ${ADMIN_URL}"
    UPDATED=$((UPDATED + 1))
fi

# ============================================
# 7. user_web/src/views/SystemPortalView.vue - 硬编码管理端地址
# ============================================
if [ -f "user_web/src/views/SystemPortalView.vue" ]; then
    sed -i '' "s|'http://[^']*:${ADMIN_PORT}'|'${ADMIN_URL}'|g" user_web/src/views/SystemPortalView.vue 2>/dev/null || \
    sed -i    "s|'http://[^']*:${ADMIN_PORT}'|'${ADMIN_URL}'|g" user_web/src/views/SystemPortalView.vue
    echo -e "${GREEN}✓${NC} SystemPortalView.vue  管理端地址 → ${ADMIN_URL}"
    UPDATED=$((UPDATED + 1))
fi

# ============================================
# 8. 启动脚本 - 端口配置（保留默认值，增加 .env 读取支持）
# ============================================

# start.sh
if [ -f "start.sh" ]; then
    # 将硬编码端口替换为支持 .env 的动态写法
    sed -i '' 's|^BACKEND_PORT=8000|BACKEND_PORT=${BACKEND_PORT:-8000}|' start.sh 2>/dev/null || \
    sed -i    's|^BACKEND_PORT=8000|BACKEND_PORT=${BACKEND_PORT:-8000}|' start.sh
    sed -i '' 's|^ADMIN_PORT=5173|ADMIN_PORT=${ADMIN_PORT:-5173}|' start.sh 2>/dev/null || \
    sed -i    's|^ADMIN_PORT=5173|ADMIN_PORT=${ADMIN_PORT:-5173}|' start.sh
    sed -i '' 's|^USER_PORT=3001|USER_PORT=${USER_PORT:-3001}|' start.sh 2>/dev/null || \
    sed -i    's|^USER_PORT=3001|USER_PORT=${USER_PORT:-3001}|' start.sh
    # 替换访问地址中的 localhost 为 SERVICE_HOST
    sed -i '' "s|http://localhost:|http://$SERVICE_HOST:|g" start.sh 2>/dev/null || \
    sed -i    "s|http://localhost:|http://$SERVICE_HOST:|g" start.sh
    echo -e "${GREEN}✓${NC} start.sh  已支持 .env 动态端口和IP"
    UPDATED=$((UPDATED + 1))
fi

# start-user-web.sh
if [ -f "start-user-web.sh" ]; then
    sed -i '' 's|^USER_PORT=3001|USER_PORT=${USER_PORT:-3001}|' start-user-web.sh 2>/dev/null || \
    sed -i    's|^USER_PORT=3001|USER_PORT=${USER_PORT:-3001}|' start-user-web.sh
    sed -i '' "s|http://localhost:|http://$SERVICE_HOST:|g" start-user-web.sh 2>/dev/null || \
    sed -i    "s|http://localhost:|http://$SERVICE_HOST:|g" start-user-web.sh
    echo -e "${GREEN}✓${NC} start-user-web.sh  已支持 .env 动态端口和IP"
    UPDATED=$((UPDATED + 1))
fi

# start.bat
if [ -f "start.bat" ]; then
    sed -i '' "s|http://localhost:|http://$SERVICE_HOST:|g" start.bat 2>/dev/null || \
    sed -i    "s|http://localhost:|http://$SERVICE_HOST:|g" start.bat
    echo -e "${GREEN}✓${NC} start.bat  访问地址 → $SERVICE_HOST"
    UPDATED=$((UPDATED + 1))
fi

# PowerShell scripts
for psfile in start-backend.ps1 start-frontend.ps1 start-user-web.ps1; do
    if [ -f "$psfile" ]; then
        sed -i '' "s|http://localhost:|http://$SERVICE_HOST:|g" "$psfile" 2>/dev/null || \
        sed -i    "s|http://localhost:|http://$SERVICE_HOST:|g" "$psfile"
        sed -i '' "s|http://127.0.0.1:|http://$SERVICE_HOST:|g" "$psfile" 2>/dev/null || \
        sed -i    "s|http://127.0.0.1:|http://$SERVICE_HOST:|g" "$psfile"
        echo -e "${GREEN}✓${NC} $psfile  访问地址 → $SERVICE_HOST"
        UPDATED=$((UPDATED + 1))
    fi
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}       同步完成！共更新 ${UPDATED} 处配置${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}统一访问地址：${NC}"
echo -e "  后端 API:      ${BACKEND_URL}"
echo -e "  Django Admin:  ${BACKEND_URL}/admin"
echo -e "  后台管理系统:  ${ADMIN_URL}"
echo -e "  用户端系统:    ${USER_URL}"
echo ""
echo -e "${YELLOW}提示：修改 .env 后重新运行此脚本即可更新所有配置${NC}"
echo ""
