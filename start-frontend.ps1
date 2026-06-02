# 启动后台管理系统脚本（PowerShell）
# 医药宝管理系统 - 后台管理前端启动脚本

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 加载统一配置
$envFile = Join-Path $scriptPath ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        if ($line -match '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
            $key = $matches[1]
            $value = $matches[2].Trim() -replace "^['\"]|['\"]$"
            if ($value -notmatch '\$\{') {
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
}

# 配置（优先使用 .env 中的值）
$SERVICE_HOST = if ($env:SERVICE_HOST) { $env:SERVICE_HOST } else { 'localhost' }
$ADMIN_PORT = if ($env:ADMIN_PORT) { $env:ADMIN_PORT } else { '5173' }
$BACKEND_PORT = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { '8000' }
$WEB_PATH = "./web"

# 导出给 Vite 前端
[Environment]::SetEnvironmentVariable("VITE_SERVICE_HOST", $SERVICE_HOST, "Process")
[Environment]::SetEnvironmentVariable("VITE_BACKEND_PORT", $BACKEND_PORT, "Process")
[Environment]::SetEnvironmentVariable("VITE_ADMIN_PORT", $ADMIN_PORT, "Process")

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    医药宝后台管理系统启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Node.js
Write-Host "[检查] Node.js 环境..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] Node.js 未安装" -ForegroundColor Red
    Write-Host "[提示] 请安装 Node.js 18+ : https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "[通过] Node.js 版本: $nodeVersion" -ForegroundColor Green

# 检查目录
if (-not (Test-Path $WEB_PATH)) {
    Write-Host "[错误] 找不到 web 目录" -ForegroundColor Red
    exit 1
}

# 检查端口占用
$portInUse = Get-NetTCPConnection -LocalPort $ADMIN_PORT -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[提示] 端口 $ADMIN_PORT 已被占用" -ForegroundColor Yellow
    Write-Host "[提示] 后台管理系统可能已在运行" -ForegroundColor Yellow
    Write-Host "[提示] 访问地址: http://$SERVICE_HOST`:$ADMIN_PORT" -ForegroundColor Cyan
    exit 0
}

Set-Location $WEB_PATH

# 检查并安装依赖
if (-not (Test-Path "./node_modules")) {
    Write-Host "[提示] 依赖未安装，正在安装..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 依赖安装失败" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
}

Write-Host "[启动] 正在启动 Vue 开发服务器..." -ForegroundColor Yellow
Write-Host ""
Write-Host "访问地址: http://$SERVICE_HOST`:$ADMIN_PORT" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

# 启动服务
npm run dev
