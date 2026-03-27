# 启动后台管理系统脚本（PowerShell）
# 医药宝管理系统 - 后台管理前端启动脚本

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    医药宝后台管理系统启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 配置
$ADMIN_PORT = 5173
$WEB_PATH = "./web"

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
    Write-Host "[提示] 访问地址: http://localhost:$ADMIN_PORT" -ForegroundColor Cyan
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
Write-Host "访问地址: http://localhost:$ADMIN_PORT" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

# 启动服务
npm run dev
