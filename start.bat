@echo off
echo 启动PCB工具后端服务...

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查requirements.txt是否存在
if not exist "requirements.txt" (
    echo 错误：未找到requirements.txt文件
    pause
    exit /b 1
)

:: 安装依赖包
echo 正在安装依赖包...
pip install -r requirements.txt

:: 创建.env文件（如果不存在）
if not exist ".env" (
    echo 正在创建.env配置文件...
    copy ".env.example" ".env"
    echo 请编辑.env文件配置相关参数
)

:: 启动服务
echo 正在启动服务...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
