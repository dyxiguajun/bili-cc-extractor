const urlInput = document.getElementById("urlInput");
const btn = document.getElementById("btn");
const statusEl = document.getElementById("status");
const coverEl = document.getElementById("cover");
const titleEl = document.getElementById("title");
const subtitleEl = document.getElementById("subtitle");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const trackSelect = document.getElementById("trackSelect");
const cookieBtn = document.getElementById("cookieBtn");


function setStatus(msg) {
  statusEl.textContent = msg;
}

btn.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  if (!url) return setStatus("请先输入链接或 test");

  setStatus("提取中...");

  const track = trackSelect.value || 0;
  const resp = await fetch(`/api/extract?url=${encodeURIComponent(url)}&track=${track}`);
if (!resp.ok) {
  let msg = `请求失败（HTTP ${resp.status}）`;
  try {
    const err = await resp.json();
    if (err.detail) msg = err.detail;
    else msg = JSON.stringify(err);
  } catch {
    // 有些错误不是json
    try { msg = await resp.text(); } catch {}
  }
  setStatus(msg);
  return;
}
  const data = await resp.json();
  //  记住当前选中（用户可能刚选了某个轨道）
    const prev = String(trackSelect.value || track);

    // 重新填充字幕轨道下拉框
    trackSelect.innerHTML = "";
    (data.tracks || []).forEach((t) => {
      const opt = document.createElement("option");
      opt.value = String(t.i);
      opt.textContent = `${t.i} - ${t.lan_doc || t.lan || "unknown"} (ai_type=${t.ai_type})`;
      trackSelect.appendChild(opt);
    });

    //  恢复用户选择：如果 prev 还存在就选回去，否则选第一个
    if ([...trackSelect.options].some(o => o.value === prev)) {
      trackSelect.value = prev;
    } else if (trackSelect.options.length > 0) {
      trackSelect.value = trackSelect.options[0].value;
    }
  // 切换轨道时自动重新提取
  trackSelect.onchange = () => btn.click();

  titleEl.textContent = data.title;
  coverEl.src = data.cover_url;
  subtitleEl.value = data.subtitle_text;

  // 下载：直接让后端生成 SRT 文件
  downloadBtn.textContent = "下载SRT";
  downloadBtn.download = "subtitle.srt";
  downloadBtn.href = `/api/download_srt?url=${encodeURIComponent(url)}&track=${trackSelect.value || 0}`;

  setStatus("完成 ✅");
});

copyBtn.addEventListener("click", async () => {
  await navigator.clipboard.writeText(subtitleEl.value);
  setStatus("已复制到剪贴板 ✅");
});

cookieBtn.addEventListener("click", async () => {
  const cookie = prompt(
    "⚠️ 仅本地使用：请粘贴你自己的 B站 Cookie（不要分享/不要截图）。\n\n粘贴后点确定保存；点取消不保存。"
  );
  if (cookie === null) return; // 用户取消

  const trimmed = cookie.trim();
  if (!trimmed) {
    // 允许用户输入空来清除
    await fetch("/api/clear_cookie", { method: "POST" });
    setStatus("已清除 Cookie ✅");
    return;
  }

  const resp = await fetch("/api/set_cookie", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cookie: trimmed }),
  });

  if (!resp.ok) {
    let msg = "设置 Cookie 失败";
    try {
      const err = await resp.json();
      if (err.detail) msg = err.detail;
    } catch {}
    setStatus(msg);
    return;
  }

  setStatus("Cookie 已设置 ✅（仅当前后端进程有效，重启后需重新设置）");
});