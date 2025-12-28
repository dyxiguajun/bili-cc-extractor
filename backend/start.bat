@echo off
setlocal

cd /d "%~dp0"

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM （可选）如果你想一启动就带Cookie，把下一行开头的 REM 删掉，然后粘贴Cookie
REM set "BILI_COOKIE=在这里粘贴你的Cookie"

REM 先打开网页（稍后后端起来就能访问）
start "" "http://127.0.0.1:8000/"

REM 启动后端
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

endlocal