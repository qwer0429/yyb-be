# 医药宝用户端系统启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    医药宝用户端系统启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在正确的目录
if (-not (Test-Path "./user_web")) {
    Write-Host "错误：请在项目根目录下运行此脚本" -ForegroundColor Red
    exit 1
}

# 进入用户端目录
Set-Location user_web

# 检查是否需要安装依赖
if (-not (Test-Path "./node_modules")) {
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
}

# 启动开发服务器
Write-Host "正在启动用户端系统..." -ForegroundColor Green
Write-Host "访问地址: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
npm run dev

# 返回根目录
Set-Location ..
