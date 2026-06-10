@echo off
cd /d %~dp0
echo ========================================
echo   AI 自动营销系统
echo   %date% %time%
echo ========================================
python engines/scheduler.py
echo.
echo 执行完毕，运行 /review 审核草稿
pause
