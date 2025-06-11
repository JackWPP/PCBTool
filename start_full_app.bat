@echo off
echo Starting PCB Tool Application...
echo.

echo Installing/Updating dependencies...
pip install -r requirements.txt
echo.

echo Starting Backend Server...
start "Backend" cmd /k "cd /d %~dp0 && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Interface...
start "Frontend" cmd /k "cd /d %~dp0 && python frontend_new.py"

echo.
echo Both services are starting...
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:7860
echo API Documentation: http://localhost:8000/docs
echo.
pause