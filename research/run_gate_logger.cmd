@echo off
cd /d D:\AlphaCode\bot-repo
:loop
D:\Python312\python research\gate_logger.py 5 >> research\data\gate\logger.log 2>&1
timeout /t 10 >nul
goto loop
