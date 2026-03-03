# 启动后端服务脚本（PowerShell）
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath\django

Write-Host "正在启动 Django 后端服务..." -ForegroundColor Green
Write-Host "访问地址: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "管理员后台: http://127.0.0.1:8000/admin" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver
