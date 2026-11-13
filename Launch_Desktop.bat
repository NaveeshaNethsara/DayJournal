@echo off
title DayJournal Launcher
cd /d "%~dp0"

echo Starting DayJournal Desktop App...
start "" pythonw app_gui.py
if errorlevel 1 (
    echo pythonw not found in PATH, falling back to python...
    python app_gui.py
)
exit
