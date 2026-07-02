@echo off
REM =====================================================================
REM SpotiFlopy launcher.
REM Double-click this file. It runs setup.ps1 with the execution policy
REM bypassed FOR THIS PROCESS ONLY (your system policy is not changed).
REM
REM cd /d "%~dp0" means: change to the folder this .bat lives in, so the
REM script always finds main2.py, requirements.txt, and .env regardless
REM of how Windows launched it.
REM =====================================================================
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
