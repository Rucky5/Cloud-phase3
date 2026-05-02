@echo off
cd /d "%~dp0"
set "PATH=%PATH%;C:\ffmpeg-8.1-essentials_build\bin"
call .venv\Scripts\activate.bat
start http://127.0.0.1:8000
python run_app.py
