@echo off
echo ============================================
echo   AI Interview Assistant - Backend Server
echo ============================================
echo.
call venv\Scripts\activate
echo Starting FastAPI backend at http://127.0.0.1:8000 ...
echo API Docs available at http://127.0.0.1:8000/docs
echo.
venv\Scripts\uvicorn.exe backend.main:app --reload --host 127.0.0.1 --port 8000
