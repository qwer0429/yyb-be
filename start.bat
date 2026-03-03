@echo off
chcp 65001 >nul
echo ===================================
echo    医药宝管理系统 - 启动脚本
echo ===================================
echo.
echo 请选择要启动的服务：
echo 1. 启动后端服务 (Django)
echo 2. 启动前端服务 (Vue)
echo 3. 同时启动前后端（需要两个窗口）
echo.
set /p choice=请输入选项 (1/2/3): 

if "%choice%"=="1" (
    echo.
    echo 正在启动后端服务...
    cd django
    echo 访问地址: http://127.0.0.1:8000
    python manage.py runserver
) else if "%choice%"=="2" (
    echo.
    echo 正在启动前端服务...
    cd web
    echo 访问地址: http://localhost:5173
    npm run dev
) else if "%choice%"=="3" (
    echo.
    echo 正在启动后端服务（新窗口）...
    start "Django Backend" cmd /k "cd django && python manage.py runserver"
    echo 正在启动前端服务（新窗口）...
    start "Vue Frontend" cmd /k "cd web && npm run dev"
    echo.
    echo 服务已启动：
    echo 后端: http://127.0.0.1:8000
    echo 前端: http://localhost:5173
    pause
) else (
    echo 无效选项，请重新运行脚本
    pause
)
