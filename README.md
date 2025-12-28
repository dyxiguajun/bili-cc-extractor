# B站字幕提取器（本地 Web 工具）｜Bili CC/AI Subtitle Extractor (Local)

一个本地运行的 Web 小工具：输入哔哩哔哩视频链接（含 BV 号），返回 **封面 + 标题 + 字幕文本**，支持 **多语言轨道选择**、**一键复制**、**下载 SRT**。

> ⚠️ 本项目默认建议本地运行（localhost）。如需登录态字幕，可在页面里手动粘贴 Cookie（仅用于本机后端进程，重启后失效）。

---

## 功能 Features

- ✅ 输入 B 站视频链接 / BV 号，提取：
  - 封面（cover）
  - 标题（title）
  - 字幕文本（subtitle）
- ✅ 多轨道/多语言选择（如：中文/英文/日语等，取决于该视频是否提供）
- ✅ 一键复制字幕到剪贴板
- ✅ 下载字幕为 `.srt`
- ✅ 稳定性增强：
  - 重试（retry）
  - 一致性校验（duration/lang validation）
  - 缓存（cache）
  - 双次一致性确认（double-fetch consistency check）用于降低上游偶发错配

---

## 技术栈 Tech Stack

- Backend: **FastAPI + Uvicorn**
- HTTP: **requests**
- Frontend: **Vanilla HTML/CSS/JS**
- Platform: Windows / macOS（本地运行）

---

## 项目结构 Project Structure
（以实际目录为准）
~~~text
bili-cc-extractor/
  start.bat              # 一键启动（Windows）
  backend/
    app.py               # FastAPI 入口
    bili.py              # B站接口封装/解析
    requirements.txt
    static/
      app.js
      style.css
    templates/
      index.html
~~~

---

## 快速开始 Quick Start (Windows)

### 方法 A：一键启动（推荐）

1. 确保已安装 Python（建议 3.12）
2. 双击项目根目录的 `start.bat`
3. 浏览器会自动打开：`http://127.0.0.1:8000/`

> 首次启动会自动创建虚拟环境并安装依赖（如果脚本检测到缺失）。

### 方法 B：手动启动

在 `backend/` 目录下：

~~~bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\activate

pip install -r requirements.txt
python -m uvicorn app:app --reload
~~~

打开：`http://127.0.0.1:8000/`

---

## 使用说明 How to Use

1. 打开网页，粘贴 B站视频链接（必须包含 BV 号）
2. 点击「提取」
3. 如有多语言轨道，可用下拉框切换轨道
4. 点击「一键复制」或「下载 SRT」

---

## 登录态字幕（可选）Cookie 说明

某些视频字幕需要登录态（接口会返回 `need_login_subtitle = true`）。

本项目提供 **本机 Cookie 设置**（页面按钮粘贴）：

- Cookie 仅发送到 `localhost` 后端
- 仅保存在当前后端进程（内存/环境变量），重启后失效
- 不会写入文件/不会自动上传

⚠️ **不要将 Cookie 提交到 GitHub，不要分享，不要截图。**

---

## API（开发调试用）

- 提取字幕  
  `GET /api/extract?url=BVxxxx&track=0`

- 调试模式（返回更多字段）  
  `GET /api/extract?url=BVxxxx&track=0&debug=1`

- 下载 SRT  
  `GET /api/download_srt?url=BVxxxx&track=0`

- 设置/清除 Cookie（仅本地）  
  `POST /api/set_cookie`  
  `POST /api/clear_cookie`

---

## 可靠性设计 Reliability

为降低 B站字幕上游接口的偶发错配/抖动，本项目做了以下工程化处理：

- **Retry**：接口波动时自动重试
- **Validation**：
  - 基于视频时长的字幕一致性校验
  - 语言一致性校验（英文/日文轨道）
- **Double-fetch consistency**：同一 `subtitle_url` 连续抓取两次，内容不一致则视为不稳定并重试
- **Cache**：成功结果按 `(bvid, cid, track)` 缓存，减少重复请求与风控概率

---

## Roadmap（可选）

- [ ] 更美观的 Cookie 输入弹窗（替代 prompt）
- [ ] 支持导出 TXT / JSON / VTT
- [ ] Docker 化（仅本地）
- [ ] 前端显示轨道更多信息（ai_status / language）

---

## 免责声明 Disclaimer

本项目仅用于个人学习/研究与本地使用。请遵守哔哩哔哩相关服务条款与当地法律法规。

---

## License

MIT
