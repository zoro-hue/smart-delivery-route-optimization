@echo off
echo ========================================================
echo Launching Complete Smart Delivery Route Optimization App
echo ========================================================
start "SDRO Backend" cmd /c "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "SDRO Frontend" cmd /c "%~dp0start_frontend.bat"
echo Both servers started.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
pause
