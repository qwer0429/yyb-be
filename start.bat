@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: 医药宝管理系统 - 一键启动脚本（Windows）
:: 功能：启动后端服务、后台管理系统、用户端系统

title 医药宝管理系统启动脚本

:: 设置窗口颜色
color 0B

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 加载统一配置
set "SERVICE_HOST=localhost"
set "ENV_FILE=%SCRIPT_DIR%.env"
if exist "%ENV_FILE%" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
        set "key=%%a"
        :: 跳过注释行和空行
        set "firstChar=!key:~0,1!"
        if not "!firstChar!"=="#" (
            if not "!key!"=="" (
                set "%%a=%%b"
            )
        )
    )
)

:: 创建必要的目录
if not exist ".pids" mkdir ".pids"
if not exist ".logs" mkdir ".logs"

:: 服务配置（优先使用 .env 中的值，否则使用默认值）
if not defined BACKEND_PORT set BACKEND_PORT=8000
if not defined ADMIN_PORT set ADMIN_PORT=5173
if not defined USER_PORT set USER_PORT=3001
if not defined SERVICE_HOST set SERVICE_HOST=localhost

:: ==================== 工具函数 ====================

:check_python
    echo [检查] Python 环境...
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [错误] Python 未安装
        echo [提示] 请安装 Python 3.9+ : https://www.python.org/downloads/
        exit /b 1
    )
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
    echo [通过] Python 版本: %PYTHON_VERSION%
    exit /b 0

:check_nodejs
    echo [检查] Node.js 环境...
    node --version >nul 2>&1
    if errorlevel 1 (
        echo [错误] Node.js 未安装
        echo [提示] 请安装 Node.js 18+ : https://nodejs.org/
        exit /b 1
    )
    for /f %%a in ('node --version') do set NODE_VERSION=%%a
    echo [通过] Node.js 版本: %NODE_VERSION%
    exit /b 0

:check_venv
    if not exist "django\venv" (
        echo [错误] Python 虚拟环境不存在
        echo [提示] 请先创建虚拟环境:
        echo   cd django
        echo   python -m venv venv
        echo   venv\Scripts\activate
        echo   pip install -r requirements.txt
        exit /b 1
    )
    echo [通过] Python 虚拟环境已存在
    exit /b 0

:check_port
    set PORT=%~1
    netstat -ano | findstr ":%PORT%" | findstr "LISTENING" >nul
    if errorlevel 1 (
        exit /b 1
    ) else (
        exit /b 0
    )

:check_dependencies
    echo.
    echo ========================================
    echo        环境依赖检查
    echo ========================================
    echo.
    
    call :check_python
    if errorlevel 1 exit /b 1
    
    call :check_nodejs
    if errorlevel 1 exit /b 1
    
    echo.
    echo [通过] 基础环境检查通过
    exit /b 0

:: ==================== 启动函数 ====================

:start_backend
    echo.
    echo ----------------------------------------
    echo        启动后端服务 (Django)
    echo ----------------------------------------
    echo.
    
    :: 检查端口占用
    call :check_port %BACKEND_PORT%
    if not errorlevel 1 (
        echo [提示] 端口 %BACKEND_PORT% 已被占用
        echo [提示] 后端服务可能已在运行
        echo [提示] 访问地址: http://%SERVICE_HOST%:%BACKEND_PORT%
        exit /b 0
    )
    
    :: 检查虚拟环境
    call :check_venv
    if errorlevel 1 exit /b 1
    
    cd django
    
    echo [启动] 正在启动 Django 服务...
    
    :: 在新窗口启动后端服务
    start "后端服务 (Django)" cmd /k "cd /d "%SCRIPT_DIR%\django" && venv\Scripts\activate && echo [启动] Django 服务启动中... && python manage.py runserver 0.0.0.0:%BACKEND_PORT%"
    
    :: 等待服务启动
    timeout /t 3 /nobreak >nul
    
    :: 检查是否启动成功
    call :check_port %BACKEND_PORT%
    if not errorlevel 1 (
        echo [通过] 后端服务已启动
        echo [提示] 访问地址: http://%SERVICE_HOST%:%BACKEND_PORT%
        echo [提示] Admin 后台: http://%SERVICE_HOST%:%BACKEND_PORT%/admin
    ) else (
        echo [等待] 服务启动中，请稍后在浏览器中访问
    )
    
    cd ..
    exit /b 0

:start_admin
    echo.
    echo ----------------------------------------
    echo     启动后台管理系统 (管理员端)
    echo ----------------------------------------
    echo.
    
    :: 检查端口占用
    call :check_port %ADMIN_PORT%
    if not errorlevel 1 (
        echo [提示] 端口 %ADMIN_PORT% 已被占用
        echo [提示] 后台管理系统可能已在运行
        echo [提示] 访问地址: http://%SERVICE_HOST%:%ADMIN_PORT%
        exit /b 0
    )
    
    cd web
    
    :: 检查并安装依赖
    if not exist "node_modules" (
        echo [提示] 后台管理系统依赖未安装，正在安装...
        call npm install
        if errorlevel 1 (
            echo [错误] 依赖安装失败
            cd ..
            exit /b 1
        )
    )
    
    echo [启动] 正在启动 Vue 开发服务器...
    
    :: 在新窗口启动
    start "后台管理系统 (Vue)" cmd /k "cd /d "%SCRIPT_DIR%\web" && echo [启动] 后台管理系统启动中... && npm run dev"
    
    :: 等待服务启动
    timeout /t 3 /nobreak >nul
    
    echo [通过] 后台管理系统已启动
    echo [提示] 访问地址: http://%SERVICE_HOST%:%ADMIN_PORT%
    
    cd ..
    exit /b 0

:start_user
    echo.
    echo ----------------------------------------
    echo          启动用户端系统
    echo ----------------------------------------
    echo.
    
    :: 检查端口占用
    call :check_port %USER_PORT%
    if not errorlevel 1 (
        echo [提示] 端口 %USER_PORT% 已被占用
        echo [提示] 用户端系统可能已在运行
        echo [提示] 访问地址: http://%SERVICE_HOST%:%USER_PORT%
        exit /b 0
    )
    
    cd user_web
    
    :: 检查并安装依赖
    if not exist "node_modules" (
        echo [提示] 用户端系统依赖未安装，正在安装...
        call npm install
        if errorlevel 1 (
            echo [错误] 依赖安装失败
            cd ..
            exit /b 1
        )
    )
    
    echo [启动] 正在启动 Vue 开发服务器...
    
    :: 在新窗口启动
    start "用户端系统 (Vue)" cmd /k "cd /d "%SCRIPT_DIR%\user_web" && echo [启动] 用户端系统启动中... && npm run dev"
    
    :: 等待服务启动
    timeout /t 3 /nobreak >nul
    
    echo [通过] 用户端系统已启动
    echo [提示] 访问地址: http://%SERVICE_HOST%:%USER_PORT%
    
    cd ..
    exit /b 0

:start_all
    echo.
    echo ========================================
    echo          正在启动所有服务
    echo ========================================
    echo.
    
    :: 检查依赖
    call :check_dependencies
    if errorlevel 1 (
        pause
        exit /b 1
    )
    
    :: 启动各个服务
    call :start_backend
    timeout /t 2 /nobreak >nul
    
    call :start_admin
    timeout /t 2 /nobreak >nul
    
    call :start_user
    
    echo.
    echo ========================================
    echo          所有服务启动完成！
    echo ========================================
    echo.
    echo 服务访问地址：
    echo   后端 API:      http://%SERVICE_HOST%:%BACKEND_PORT%
    echo   Django Admin:  http://%SERVICE_HOST%:%BACKEND_PORT%/admin
    echo   后台管理系统:  http://%SERVICE_HOST%:%ADMIN_PORT%
    echo   用户端系统:    http://%SERVICE_HOST%:%USER_PORT%
    echo.
    echo 各服务已在独立窗口中运行，关闭窗口即可停止对应服务
    echo.
    pause
    exit /b 0

:: ==================== 停止函数 ====================

:stop_all
    echo.
    echo ========================================
    echo          正在停止所有服务
    echo ========================================
    echo.
    
    echo [停止] 正在查找并停止相关进程...
    
    :: 停止 Python/Django 进程
    taskkill /F /FI "WINDOWTITLE eq 后端服务 (Django)*" >nul 2>&1
    taskkill /F /IM python.exe >nul 2>&1
    
    :: 停止 Node/Vue 进程
    taskkill /F /FI "WINDOWTITLE eq 后台管理系统 (Vue)*" >nul 2>&1
    taskkill /F /FI "WINDOWTITLE eq 用户端系统 (Vue)*" >nul 2>&1
    taskkill /F /IM node.exe >nul 2>&1
    
    echo [通过] 所有服务已停止
    echo.
    pause
    exit /b 0

:: ==================== 状态检查 ====================

:check_status
    echo.
    echo ========================================
    echo          服务运行状态
    echo ========================================
    echo.
    
    set ANY_RUNNING=false
    
    :: 检查后端
    call :check_port %BACKEND_PORT%
    if not errorlevel 1 (
        echo [运行中] 后端服务      端口: %BACKEND_PORT%
        set ANY_RUNNING=true
    ) else (
        echo [未运行] 后端服务
    )
    
    :: 检查后台管理
    call :check_port %ADMIN_PORT%
    if not errorlevel 1 (
        echo [运行中] 后台管理系统  端口: %ADMIN_PORT%
        set ANY_RUNNING=true
    ) else (
        echo [未运行] 后台管理系统
    )
    
    :: 检查用户端
    call :check_port %USER_PORT%
    if not errorlevel 1 (
        echo [运行中] 用户端系统    端口: %USER_PORT%
        set ANY_RUNNING=true
    ) else (
        echo [未运行] 用户端系统
    )
    
    echo.
    
    if "%ANY_RUNNING%"=="true" (
        echo 访问地址：
        call :check_port %BACKEND_PORT% >nul && echo   后端:      http://%SERVICE_HOST%:%BACKEND_PORT%
        call :check_port %ADMIN_PORT% >nul && echo   后台管理:  http://%SERVICE_HOST%:%ADMIN_PORT%
        call :check_port %USER_PORT% >nul && echo   用户端:    http://%SERVICE_HOST%:%USER_PORT%
    )
    
    echo.
    pause
    exit /b 0

:: ==================== 菜单 ====================

:show_menu
    cls
    echo.
    echo ========================================
    echo        医药宝管理系统启动脚本
    echo ========================================
    echo.
    echo 1. 启动后端服务 (Django)          端口: %BACKEND_PORT%
    echo 2. 启动后台管理系统 (管理员端)    端口: %ADMIN_PORT%
    echo 3. 启动用户端系统                 端口: %USER_PORT%
    echo 4. 启动所有服务
    echo 5. 查看服务状态
    echo 6. 停止所有服务
    echo 7. 退出
    echo.
    exit /b 0

:: ==================== 主程序 ====================

:main_loop
    call :show_menu
    set /p choice=请输入选项 (1-7): 
    
    if "%choice%"=="1" (
        call :check_dependencies && call :start_backend
        pause
        goto main_loop
    )
    
    if "%choice%"=="2" (
        call :check_dependencies && call :start_admin
        pause
        goto main_loop
    )
    
    if "%choice%"=="3" (
        call :check_dependencies && call :start_user
        pause
        goto main_loop
    )
    
    if "%choice%"=="4" (
        call :start_all
        goto main_loop
    )
    
    if "%choice%"=="5" (
        call :check_status
        goto main_loop
    )
    
    if "%choice%"=="6" (
        call :stop_all
        goto main_loop
    )
    
    if "%choice%"=="7" (
        echo.
        echo 感谢使用，再见！
        timeout /t 2 >nul
        exit /b 0
    )
    
    echo.
    echo [错误] 无效的选项，请重新输入
    pause
    goto main_loop

:: 启动主程序
goto main_loop
