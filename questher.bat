@echo off
REM Questher - Technical Question Answering Tool
REM Windows batch file for easy execution using module syntax

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run setup first or create virtual environment
    pause
    exit /b 1
)

REM Run Questher using module syntax
.venv\Scripts\python.exe -m questher %*
