@echo off
title DayJournal Web Server
cd /d "%~dp0"

echo =======================================================
echo  Starting DayJournal Web Interface...
echo  Opening browser at http://localhost:5000
echo =======================================================
python app_web.py
pause
