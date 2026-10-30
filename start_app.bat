@echo off
title Kisan Mitra - Plant Disease Assistant
cd /d "%~dp0"

echo ========================================================
echo Starting Kisan Mitra Plant Disease Assistant...
echo ========================================================
echo.
echo Opening browser...
start http://localhost:5000/
echo.
echo Launching Python backend...
python app.py

pause

