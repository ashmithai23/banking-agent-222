@echo off
REM Start VectraBank on Windows. Usage: start.bat [dev^|prod]
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
