@echo off
echo 正在停止推荐系统服务...

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

python run_service.py stop
echo 服务已停止！
pause 