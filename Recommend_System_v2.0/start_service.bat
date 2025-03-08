@echo off
echo 正在启动推荐系统服务...

REM 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 已获取管理员权限
) else (
    echo 请以管理员权限运行此脚本！
    echo 右键点击此文件，选择"以管理员身份运行"
    pause
    exit
)

REM 检查服务是否已安装
sc query RecommendationSystem >nul 2>&1
if %errorLevel% == 0 (
    echo 服务已存在，正在启动...
    python run_service.py start
) else (
    echo 首次运行，正在安装服务...
    python run_service.py install
    python run_service.py start
)

echo 正在打开网页界面...
start http://localhost:5000

echo 服务已启动！可以通过 http://localhost:5000 访问
echo 如需停止服务，请运行 stop_service.bat
pause 