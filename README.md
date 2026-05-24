# Bili CC Extractor Tools

一个本地运行的 Bilibili CC / AI 字幕提取工具。输入 B 站视频链接或 BV 号后，可以提取封面、标题、字幕文本，并支持多语言轨道选择、复制字幕、下载 SRT。

> 默认仅在本机 `localhost` 运行。扫码登录获取的 Cookie 只保存在本机 `backend/.bili_cookie`，不要提交到 GitHub。

## Features

- 提取 B 站视频标题、封面、字幕
- 支持多语言字幕轨道选择
- 一键复制字幕
- 下载 `.srt` 字幕文件
- 支持 Bilibili 手机 App 扫码登录，自动获取并保存本地 Cookie
- 保留手动 Cookie 模式作为备用
- 后端包含重试、缓存、字幕时长校验和双次一致性校验

## Requirements

- Python 3.10 或更高版本
- Windows / macOS / Linux

## Quick Start

### Windows

双击运行：

```text
Start Windows.bat
```

### macOS

推荐使用 Terminal 运行，避免 macOS 权限问题：

```bash
cd path/to/bili-cc-extractor-tools
bash scripts/start-macos.sh
```

也可以给启动器授权后双击：

```bash
chmod +x "Start macOS.command"
./"Start macOS.command"
```

如果双击时 macOS 提示无法打开，可以右键点击 `Start macOS.command`，选择“打开”。

### Linux

```bash
cd path/to/bili-cc-extractor-tools
bash scripts/start-linux.sh
```

启动后默认访问：

```text
http://127.0.0.1:8000/
```

## Project Structure

```text
bili-cc-extractor-tools/
├── backend/
│   ├── app.py
│   ├── bili.py
│   ├── requirements.txt
│   ├── static/
│   └── templates/
├── scripts/
│   ├── start-macos.sh
│   ├── start-windows.bat
│   └── start-linux.sh
├── Start macOS.command
├── Start Windows.bat
├── README.md
└── .gitignore
```

## Manual Start

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

## Login / Cookie Notice

某些视频字幕可能需要登录态。推荐使用页面里的“扫码登录”：

1. 点击“扫码登录”
2. 使用 Bilibili 手机 App 扫码
3. 在手机上确认登录
4. 工具会自动保存 Cookie 到本机 `backend/.bili_cookie`

Cookie 仅用于本地请求 Bilibili 接口，不会上传到任何第三方服务器。

如果扫码登录失败，可以使用“手动Cookie”作为备用。不要把 Cookie 写入代码、截图或提交到 GitHub。

## API

- `GET /api/extract?url=BVxxxx&track=0`
- `GET /api/extract?url=BVxxxx&track=0&debug=1`
- `GET /api/download_srt?url=BVxxxx&track=0`
- `GET /api/login/qrcode`
- `GET /api/login/qrcode/poll?qrcode_key=...`
- `GET /api/cookie_status`
- `POST /api/set_cookie`
- `POST /api/clear_cookie`

## GitHub Notes

上传到 GitHub 前请不要提交这些文件：

- `backend/.venv/`
- `backend/__pycache__/`
- `.DS_Store`
- `__MACOSX/`
- `backend/.bili_cookie`
- 任何包含 Cookie、账号、私密信息的文件

## Disclaimer

本项目仅用于个人学习、研究与本地使用。请遵守哔哩哔哩相关服务条款与当地法律法规。

## License

MIT
