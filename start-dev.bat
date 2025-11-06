@echo off
echo ========================================
echo Starting MediFlow Lite Development Environment
echo ========================================
echo.

REM Start backend in a new window
echo Starting Backend Server...
start "MediFlow Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend in a new window
echo Starting Frontend Server...
start "MediFlow Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo MediFlow Lite is starting...
echo ========================================
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to stop all servers...
pause > nul

REM Kill the servers
taskkill /FI "WINDOWTITLE eq MediFlow Backend*" /F
taskkill /FI "WINDOWTITLE eq MediFlow Frontend*" /F

