# 启动后端服务脚本（PowerShell）
# 医药宝管理系统 - Django 后端启动脚本

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    医药宝后端服务启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 配置
$BACKEND_PORT = 8000
$VENV_PATH = "./django/venv"

# 检查 Python
Write-Host "[检查] Python 环境..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] Python 未安装" -ForegroundColor Red
    Write-Host "[提示] 请安装 Python 3.9+ : https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "[通过] $pythonVersion" -ForegroundColor Green

# 检查虚拟环境
if (-not (Test-Path $VENV_PATH)) {
    Write-Host "[错误] Python 虚拟环境不存在" -ForegroundColor Red
    Write-Host "[提示] 请先创建虚拟环境:" -ForegroundColor Yellow
    Write-Host "  cd django"
    Write-Host "  python -m venv venv"
    Write-Host "  venv\Scripts\activate"
    Write-Host "  pip install -r requirements.txt"
    exit 1
}

# 检查端口占用
$portInUse = Get-NetTCPConnection -LocalPort $BACKEND_PORT -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[提示] 端口 $BACKEND_PORT 已被占用" -ForegroundColor Yellow
    Write-Host "[提示] 后端服务可能已在运行" -ForegroundColor Yellow
    Write-Host "[提示] 访问地址: http://127.0.0.1:$BACKEND_PORT" -ForegroundColor Cyan
    exit 0
}

# 启动后端
Set-Location django

Write-Host "[启动] 正在激活虚拟环境..." -ForegroundColor Yellow
Write-Host "[启动] 正在启动 Django 服务..." -ForegroundColor Yellow
Write-Host ""
Write-Host "访问地址: http://127.0.0.1:$BACKEND_PORT" -ForegroundColor Green
Write-Host "管理员后台: http://127.0.0.1:$BACKEND_PORT/admin" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

# 激活虚拟环境并启动
& venv\Scripts\Activate.ps1
python manage.py runserver
