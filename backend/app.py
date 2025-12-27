from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 静态文件（JS/CSS）
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/mock_extract")
def mock_extract(url: str):
    return {
        "input_url": url,
        "title": "示例标题（假数据）",
        "cover_url": "https://placehold.co/480x270",
        "subtitle_text": "00:00 Hello\n00:01 This is a mock subtitle.\n"
    }