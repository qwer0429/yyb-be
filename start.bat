@echo off
chcp 65001

echo ========================================
echo    医药宝管理系统启动脚本
echo ========================================
echo.
echo 请选择要启动的系统：
echo 1. 启动后端服务 (Django)
echo 2. 启动后台管理系统 (管理员端)
echo 3. 启动用户端系统
echo 4. 启动所有服务
echo 5. 退出
echo.

set /p choice=请输入选项 (1-5): 

if "%choice%"=="1" goto start_backend
if "%choice%"=="2" goto start_admin
if "%choice%"=="3" goto start_user
if "%choice%"=="4" goto start_all
if "%choice%"=="5" goto end

echo 无效的选项，请重新运行脚本
pause
exit

:start_backend
echo 正在启动后端服务...
cd django
start cmd /k "venv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"
cd ..
goto end

:start_admin
echo 正在启动后台管理系统...
cd web
start cmd /k "npm run dev"
cd ..
goto end

:start_user
echo 正在启动用户端系统...
cd user_web
start cmd /k "npm install && npm run dev"
cd ..
goto end

:start_all
echo 正在启动所有服务...
cd django
start cmd /k "venv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"
cd ..
cd web
start cmd /k "npm run dev"
cd ..
cd user_web
start cmd /k "npm install && npm run dev"
cd ..
goto end

:end
pause
