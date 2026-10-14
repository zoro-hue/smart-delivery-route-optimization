@echo off
echo ========================================================
echo Starting Smart Delivery Route Optimization Backend
echo ========================================================
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
