@echo off
echo ============================================
echo   AI Interview Assistant - Frontend UI
echo ============================================
echo.
set PYTHONPATH=%~dp0
call venv\Scripts\activate
echo Starting Streamlit Frontend at http://127.0.0.1:8501 ...
echo.
venv\Scripts\streamlit.exe run frontend/app.py --server.port 8501
