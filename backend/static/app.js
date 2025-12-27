const urlInput = document.getElementById("urlInput");
const btn = document.getElementById("btn");
const statusEl = document.getElementById("status");
const coverEl = document.getElementById("cover");
const titleEl = document.getElementById("title");
const subtitleEl = document.getElementById("subtitle");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");

function setStatus(msg) {
  statusEl.textContent = msg;
}

btn.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  if (!url) return setStatus("请先输入链接或 test");

  setStatus("提取中...");

  const resp = await fetch(`/api/mock_extract?url=${encodeURIComponent(url)}`);
  if (!resp.ok) {
    setStatus("请求失败，请检查后端是否在运行");
    return;
  }
  const data = await resp.json();

  titleEl.textContent = data.title;
  coverEl.src = data.cover_url;
  subtitleEl.value = data.subtitle_text;

  // 下载：把文本变成 blob
  const blob = new Blob([data.subtitle_text], { type: "text/plain;charset=utf-8" });
  downloadBtn.href = URL.createObjectURL(blob);

  setStatus("完成 ✅");
});

copyBtn.addEventListener("click", async () => {
  await navigator.clipboard.writeText(subtitleEl.value);
  setStatus("已复制到剪贴板 ✅");
});