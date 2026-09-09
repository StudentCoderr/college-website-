@echo off
cd /d "%~dp0"
if exist venv\Scripts\python.exe (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please create one first.
    exit /b 1
)
python app.py
