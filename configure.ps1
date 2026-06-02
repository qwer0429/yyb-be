# ============================================
# 医药宝管理系统 - 统一配置同步脚本 (Windows)
# 功能：读取根目录 .env，一键同步到所有相关配置文件
# ============================================

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

$envFile = Join-Path $scriptPath ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "错误：找不到 .env 配置文件" -ForegroundColor Red
    Write-Host "请确保 .env 文件位于项目根目录" -ForegroundColor Yellow
    exit 1
}

# 读取 .env 文件
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq "" -or $line.StartsWith("#")) { return }
    if ($line -match '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
        $key = $matches[1]
        $value = $matches[2].Trim()
        # 去除引号
        $value = $value -replace "^['\"]|['\"]$"
        # 跳过包含变量引用的行
        if ($value -notmatch '\$\{') {
            $envVars[$key] = $value
        }
    }
}

# 获取配置值
$SERVICE_HOST = if ($envVars.ContainsKey('SERVICE_HOST')) { $envVars['SERVICE_HOST'] } else { 'localhost' }
$BACKEND_PORT = if ($envVars.ContainsKey('BACKEND_PORT')) { $envVars['BACKEND_PORT'] } else { '8000' }
$ADMIN_PORT   = if ($envVars.ContainsKey('ADMIN_PORT'))   { $envVars['ADMIN_PORT'] }   else { '5173' }
$USER_PORT    = if ($envVars.ContainsKey('USER_PORT'))    { $envVars['USER_PORT'] }    else { '3001' }

$BACKEND_URL = "http://${SERVICE_HOST}:${BACKEND_PORT}"
$ADMIN_URL   = "http://${SERVICE_HOST}:${ADMIN_PORT}"
$USER_URL    = "http://${SERVICE_HOST}:${USER_PORT}"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       医药宝 - 统一配置同步工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "当前统一配置：" -ForegroundColor Yellow
Write-Host "  服务IP:   $SERVICE_HOST" -ForegroundColor Green
Write-Host "  后端端口: $BACKEND_PORT" -ForegroundColor Green
Write-Host "  管理端口: $ADMIN_PORT" -ForegroundColor Green
Write-Host "  用户端口: $USER_PORT" -ForegroundColor Green
Write-Host ""

$updated = 0

function Update-FileContent {
    param(
        [string]$FilePath,
        [string]$Pattern,
        [string]$Replacement,
        [string]$Description
    )
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw
        if ($content -match $Pattern) {
            $content = $content -replace $Pattern, $Replacement
            Set-Content $FilePath $content -NoNewline
            Write-Host "  $Description" -ForegroundColor Green
            return $true
        }
    }
    return $false
}

# 1. web/vite.config.ts
if (Update-FileContent -FilePath "web/vite.config.ts" `
    -Pattern "target: 'http://[^']*:${BACKEND_PORT}'" `
    -Replacement "target: '${BACKEND_URL}'" `
    -Description "web/vite.config.ts  代理地址 → $BACKEND_URL") {
    $updated++
}

# 2. user_web/vite.config.ts
if (Update-FileContent -FilePath "user_web/vite.config.ts" `
    -Pattern "target: 'http://[^']*:${BACKEND_PORT}'" `
    -Replacement "target: '${BACKEND_URL}'" `
    -Description "user_web/vite.config.ts  代理地址 → $BACKEND_URL") {
    $updated++
}

# 3. web/.env.development
if (Test-Path "web/.env.development") {
    $content = Get-Content "web/.env.development" -Raw
    if ($content -match "VITE_USER_WEB_URL") {
        $content = $content -replace "VITE_USER_WEB_URL.*", "VITE_USER_WEB_URL = '${USER_URL}'"
    } else {
        $content += "`nVITE_USER_WEB_URL = '${USER_URL}'"
    }
    Set-Content "web/.env.development" $content -NoNewline
    Write-Host "  web/.env.development  VITE_USER_WEB_URL → $USER_URL" -ForegroundColor Green
    $updated++
}

# 4. web/.env.production
if (Test-Path "web/.env.production") {
    $content = Get-Content "web/.env.production" -Raw
    if ($content -match "VITE_API_BASE_URL") {
        $content = $content -replace "VITE_API_BASE_URL.*", "VITE_API_BASE_URL = '${BACKEND_URL}'"
    } else {
        $content += "`nVITE_API_BASE_URL = '${BACKEND_URL}'"
    }
    Set-Content "web/.env.production" $content -NoNewline
    Write-Host "  web/.env.production   VITE_API_BASE_URL → $BACKEND_URL" -ForegroundColor Green
    $updated++
}

# 5. user_web/.env.development
if (Test-Path "user_web/.env.development") {
    $content = Get-Content "user_web/.env.development" -Raw
    if ($content -match "VITE_API_BASE_URL") {
        $content = $content -replace "VITE_API_BASE_URL.*", "VITE_API_BASE_URL=${BACKEND_URL}"
    } else {
        $content += "`nVITE_API_BASE_URL=${BACKEND_URL}"
    }
    if ($content -match "VITE_ADMIN_URL") {
        $content = $content -replace "VITE_ADMIN_URL.*", "VITE_ADMIN_URL=${ADMIN_URL}"
    } else {
        $content += "`nVITE_ADMIN_URL=${ADMIN_URL}"
    }
    Set-Content "user_web/.env.development" $content -NoNewline
    Write-Host "  user_web/.env.development  VITE_API_BASE_URL → $BACKEND_URL" -ForegroundColor Green
    Write-Host "  user_web/.env.development  VITE_ADMIN_URL    → $ADMIN_URL" -ForegroundColor Green
    $updated++
}

# 6. LoginView.vue
if (Update-FileContent -FilePath "user_web/src/views/LoginView.vue" `
    -Pattern "'http://[^']*:${ADMIN_PORT}'" `
    -Replacement "'${ADMIN_URL}'" `
    -Description "LoginView.vue  管理端跳转地址 → $ADMIN_URL") {
    $updated++
}

# 7. SystemPortalView.vue
if (Update-FileContent -FilePath "user_web/src/views/SystemPortalView.vue" `
    -Pattern "'http://[^']*:${ADMIN_PORT}'" `
    -Replacement "'${ADMIN_URL}'" `
    -Description "SystemPortalView.vue  管理端地址 → $ADMIN_URL") {
    $updated++
}

# 8. 启动脚本 - 替换 localhost 为 SERVICE_HOST
$scriptFiles = @('start.sh', 'start-user-web.sh', 'start.bat', 'start-backend.ps1', 'start-frontend.ps1', 'start-user-web.ps1')
foreach ($sf in $scriptFiles) {
    if (Test-Path $sf) {
        $content = Get-Content $sf -Raw
        $hasChange = $false
        if ($content -match 'http://localhost:') {
            $content = $content -replace 'http://localhost:', "http://$SERVICE_HOST`:"
            $hasChange = $true
        }
        if ($content -match 'http://127\.0\.0\.1:') {
            $content = $content -replace 'http://127\.0\.0\.1:', "http://$SERVICE_HOST`:"
            $hasChange = $true
        }
        if ($hasChange) {
            Set-Content $sf $content -NoNewline
            Write-Host "  $sf  访问地址 → $SERVICE_HOST" -ForegroundColor Green
            $updated++
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "       同步完成！共更新 $updated 处配置" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "统一访问地址：" -ForegroundColor Cyan
Write-Host "  后端 API:      $BACKEND_URL"
Write-Host "  Django Admin:  ${BACKEND_URL}/admin"
Write-Host "  后台管理系统:  $ADMIN_URL"
Write-Host "  用户端系统:    $USER_URL"
Write-Host ""
Write-Host "提示：修改 .env 后重新运行此脚本即可更新所有配置" -ForegroundColor Yellow
Write-Host ""
