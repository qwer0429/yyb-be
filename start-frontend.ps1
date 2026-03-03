# 启动前端服务脚本（PowerShell）
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath\web

Write-Host "正在启动 Vue 前端服务..." -ForegroundColor Green
Write-Host "访问地址: http://localhost:5173" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

npm run dev
