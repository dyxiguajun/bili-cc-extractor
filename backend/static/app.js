const I18N = {
  zh: {
    appTitle: "B站字幕提取器",
    urlPlaceholder: "粘贴B站链接（BV号）",
    extract: "提取",
    extracting: "提取中...",
    qrLogin: "扫码登录",
    manualCookie: "手动Cookie",
    clearCookie: "清空Cookie",
    logout: "退出登录",
    notLoggedIn: "未登录",
    loggedIn: "已登录",
    localOnly: "Cookie 仅保存在本机",
    scanTitle: "使用 Bilibili 手机 App 扫码登录",
    qrPlaceholder: "点击“扫码登录”生成二维码",
    rememberMe: "记住我，下次可快速登录",
    qrIdle: "请点击“扫码登录”生成二维码",
    cookieHint: "Cookie 仅保存在本机，不会上传到任何服务器。",
    quickLoginTitle: "已保存的登录",
    quickLoginHint: "点击快速登录，无需扫码",
    subtitlePlaceholder: "字幕会显示在这里，可复制",
    copy: "一键复制",
    downloadSrt: "下载SRT",
    enterUrl: "请先输入 B站链接或 BV号",
    extractingWait: "提取中，请稍等...",
    done: "完成 ✅",
    noSubtitle: "未获取到可用字幕，请稍后再试或切换轨道。",
    copied: "已复制到剪贴板 ✅",
    cookieDetected: "已检测到本地登录 Cookie ✅",
    qrGenerating: "正在生成二维码...",
    qrUseApp: "请使用 Bilibili 手机 App 扫码。",
    waitingScan: "等待扫码...",
    waitingConfirm: "已扫码，请在手机上确认登录...",
    qrExpired: "二维码已过期，请重新点击“扫码登录”。",
    loginSuccess: "登录成功 ✅",
    loginSuccessCookie: "Bilibili 登录成功，Cookie 已保存到本机 ✅",
    loginSuccessSession: "Bilibili 登录成功，本次运行期间有效 ✅",
    noCookie: "扫码成功，但没有获取到 Cookie。请使用手动 Cookie 模式。",
    networkLoginError: "网络或接口异常，请稍后再试。",
    qrFail: "二维码生成失败，请检查网络。",
    quickLoginOk: "已使用保存的 Cookie 快速登录 ✅",
    quickLoginFail: "快速登录失败，请重新扫码。",
    cleared: "已清空本地 Cookie ✅",
    loggedOut: "已退出登录并清除当前 Cookie ✅",
    manualPrompt: "⚠️ 仅本地使用：请粘贴你自己的 B站 Cookie（不要分享/不要截图）。\n\n粘贴后点确定保存；点取消不保存。",
    cookieSet: "Cookie 已设置 ✅（已保存到本机）",
    setCookieFail: "设置 Cookie 失败",
    requestFail: "请求失败",
    extractFail: "提取失败",
    loginMenu: "用户菜单"
  },
  en: {
    appTitle: "Bilibili Subtitle Extractor",
    urlPlaceholder: "Paste Bilibili link or BV ID",
    extract: "Extract",
    extracting: "Extracting...",
    qrLogin: "QR Login",
    manualCookie: "Manual Cookie",
    clearCookie: "Clear Cookie",
    logout: "Log out",
    notLoggedIn: "Not logged in",
    loggedIn: "Logged in",
    localOnly: "Cookie is stored locally only",
    scanTitle: "Scan with the Bilibili mobile app",
    qrPlaceholder: "Click “QR Login” to generate a QR code",
    rememberMe: "Remember me for quick login next time",
    qrIdle: "Click “QR Login” to generate a QR code",
    cookieHint: "Cookie is stored only on this computer and is never uploaded to any server.",
    quickLoginTitle: "Saved login",
    quickLoginHint: "Click to log in quickly without scanning",
    subtitlePlaceholder: "Subtitles will appear here and can be copied",
    copy: "Copy",
    downloadSrt: "Download SRT",
    enterUrl: "Please enter a Bilibili link or BV ID first",
    extractingWait: "Extracting, please wait...",
    done: "Done ✅",
    noSubtitle: "No usable subtitles found. Try again later or switch tracks.",
    copied: "Copied to clipboard ✅",
    cookieDetected: "Local login Cookie detected ✅",
    qrGenerating: "Generating QR code...",
    qrUseApp: "Please scan with the Bilibili mobile app.",
    waitingScan: "Waiting for scan...",
    waitingConfirm: "Scanned. Please confirm on your phone...",
    qrExpired: "QR code expired. Please click “QR Login” again.",
    loginSuccess: "Login successful ✅",
    loginSuccessCookie: "Bilibili login successful. Cookie saved locally ✅",
    loginSuccessSession: "Bilibili login successful for this session ✅",
    noCookie: "Scanned successfully, but no Cookie was received. Please use manual Cookie mode.",
    networkLoginError: "Network or API error. Please try again later.",
    qrFail: "Failed to generate QR code. Please check network.",
    quickLoginOk: "Quick login with saved Cookie succeeded ✅",
    quickLoginFail: "Quick login failed. Please scan again.",
    cleared: "Local Cookie cleared ✅",
    loggedOut: "Logged out and current Cookie cleared ✅",
    manualPrompt: "⚠️ Local use only: paste your own Bilibili Cookie. Do not share it or screenshot it.\n\nClick OK to save; Cancel to skip.",
    cookieSet: "Cookie set ✅ (saved locally)",
    setCookieFail: "Failed to set Cookie",
    requestFail: "Request failed",
    extractFail: "Extraction failed",
    loginMenu: "User menu"
  }
};

let currentLang = localStorage.getItem("ui_lang") || "zh";
let extractRequestSeq = 0;
let lastExtractUrl = "";
let currentQrKey = null;
let loginPollTimer = null;
let currentUser = null;
let savedProfile = null;

const $ = (id) => document.getElementById(id);

const urlInput = $("urlInput");
const btn = $("btn");
const loginBtn = $("loginBtn");
const trackSelect = $("trackSelect");
const statusEl = $("status");
const titleEl = $("title");
const coverEl = $("cover");
const subtitleEl = $("subtitle");
const copyBtn = $("copyBtn");
const downloadBtn = $("downloadBtn");
const loginPanel = $("loginPanel");
const qrImg = $("qrImg");
const qrPlaceholder = $("qrPlaceholder");
const loginStatus = $("loginStatus");
const rememberMe = $("rememberMe");
const languageSelect = $("languageSelect");
const avatarBtn = $("avatarBtn");
const avatarImg = $("avatarImg");
const avatarFallback = $("avatarFallback");
const userMenu = $("userMenu");
const menuAvatar = $("menuAvatar");
const menuNickname = $("menuNickname");
const menuSub = $("menuSub");
const menuManualCookieBtn = $("menuManualCookieBtn");
const menuClearCookieBtn = $("menuClearCookieBtn");
const menuLogoutBtn = $("menuLogoutBtn");
const quickLoginBox = $("quickLoginBox");
const quickLoginBtn = $("quickLoginBtn");
const quickAvatar = $("quickAvatar");
const quickName = $("quickName");

function t(key) {
  return (I18N[currentLang] && I18N[currentLang][key]) || I18N.zh[key] || key;
}

function applyI18n() {
  document.documentElement.lang = currentLang;
  languageSelect.value = currentLang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  btn.textContent = btn.disabled ? t("extracting") : t("extract");
  downloadBtn.textContent = t("downloadSrt");
  avatarBtn.setAttribute("aria-label", t("loginMenu"));
  renderUserState();
}

function setStatus(msg) { statusEl.textContent = msg || ""; }

function resetResultArea(message = "") {
  titleEl.textContent = "";
  coverEl.removeAttribute("src");
  coverEl.classList.add("hidden");
  subtitleEl.value = "";
  trackSelect.innerHTML = "";
  downloadBtn.removeAttribute("href");
  downloadBtn.download = "subtitle.srt";
  downloadBtn.textContent = t("downloadSrt");
  if (message) setStatus(message);
}

function hideQrImage() {
  qrImg.removeAttribute("src");
  qrImg.classList.add("hidden");
  qrPlaceholder.classList.remove("hidden");
}

function showQrImage(src) {
  qrImg.src = src;
  qrImg.classList.remove("hidden");
  qrPlaceholder.classList.add("hidden");
}

function setBusy(isBusy) {
  btn.disabled = isBusy;
  btn.textContent = isBusy ? t("extracting") : t("extract");
}

function profileAvatar(profile) {
  return profile && (profile.avatar_url || profile.face || profile.avatar);
}

function profileName(profile) {
  return profile && (profile.nickname || profile.uname || profile.name);
}

function setImgOrHide(img, url) {
  if (url) {
    img.src = `/api/proxy_image?url=${encodeURIComponent(url)}`;
    img.classList.remove("hidden");
  } else {
    img.removeAttribute("src");
    img.classList.add("hidden");
  }
}

function renderUserState() {
  const loggedIn = !!(currentUser && currentUser.has_cookie);
  const profile = loggedIn ? currentUser.profile : null;
  const avatar = profileAvatar(profile);
  const name = profileName(profile);

  if (loggedIn && avatar) {
    setImgOrHide(avatarImg, avatar);
    avatarFallback.classList.add("hidden");
  } else {
    avatarImg.removeAttribute("src");
    avatarImg.classList.add("hidden");
    avatarFallback.classList.remove("hidden");
  }

  if (loggedIn && avatar) setImgOrHide(menuAvatar, avatar);
  else setImgOrHide(menuAvatar, "");

  menuNickname.textContent = loggedIn ? (name || t("loggedIn")) : t("notLoggedIn");
  menuSub.textContent = t("localOnly");
  menuLogoutBtn.classList.toggle("hidden", !loggedIn);
  loginBtn.classList.toggle("hidden", loggedIn);

  if (savedProfile && savedProfile.has_saved_cookie && profileName(savedProfile.profile)) {
    quickLoginBox.classList.remove("hidden");
    quickName.textContent = profileName(savedProfile.profile);
    setImgOrHide(quickAvatar, profileAvatar(savedProfile.profile));
  } else {
    quickLoginBox.classList.add("hidden");
  }
}

async function readError(resp, fallback) {
  let msg = fallback || `${t("requestFail")}（HTTP ${resp.status}）`;
  try {
    const err = await resp.json();
    if (err.detail) msg = err.detail;
    else if (err.message) msg = err.message;
    else msg = JSON.stringify(err);
  } catch {
    try { msg = await resp.text(); } catch {}
  }
  return msg;
}

async function extractSubtitle(forceTrack = null) {
  const url = urlInput.value.trim();
  if (!url) {
    resetResultArea(t("enterUrl"));
    return;
  }

  lastExtractUrl = url;
  const requestId = ++extractRequestSeq;
  const selectedTrack = forceTrack ?? (trackSelect.value || 0);

  resetResultArea(t("extractingWait"));
  setBusy(true);

  try {
    const resp = await fetch(`/api/extract?url=${encodeURIComponent(url)}&track=${encodeURIComponent(selectedTrack)}&_=${Date.now()}`, { cache: "no-store" });
    if (requestId !== extractRequestSeq || url !== lastExtractUrl) return;

    if (!resp.ok) {
      setStatus(await readError(resp, `${t("requestFail")}（HTTP ${resp.status}）`));
      return;
    }

    const data = await resp.json();
    if (requestId !== extractRequestSeq || url !== lastExtractUrl) return;

    const tracks = data.tracks || [];
    trackSelect.innerHTML = "";
    tracks.forEach((track) => {
      const opt = document.createElement("option");
      opt.value = String(track.i);
      opt.textContent = `${track.i} - ${track.lan_doc || track.lan || "unknown"} (ai_type=${track.ai_type ?? ""})`;
      trackSelect.appendChild(opt);
    });

    const effectiveTrack = String(data.effective_track ?? selectedTrack ?? 0);
    if ([...trackSelect.options].some(o => o.value === effectiveTrack)) trackSelect.value = effectiveTrack;
    else if (trackSelect.options.length > 0) trackSelect.value = trackSelect.options[0].value;

    titleEl.textContent = data.title || "";

    if (data.cover_url) {
      coverEl.src = `/api/proxy_image?url=${encodeURIComponent(data.cover_url)}`;
      coverEl.classList.remove("hidden");
    } else {
      coverEl.removeAttribute("src");
      coverEl.classList.add("hidden");
    }

    subtitleEl.value = data.subtitle_text || "";
    downloadBtn.href = `/api/download_srt?url=${encodeURIComponent(url)}&track=${encodeURIComponent(trackSelect.value || 0)}&_=${Date.now()}`;
    downloadBtn.download = "subtitle.srt";
    downloadBtn.textContent = t("downloadSrt");

    const hasRealSubtitle = data.subtitle_text && !data.subtitle_text.includes("该语言轨暂时获取不到");
    setStatus(hasRealSubtitle ? t("done") : t("noSubtitle"));
  } catch (e) {
    if (requestId !== extractRequestSeq) return;
    setStatus(`${t("extractFail")}：${e.message || e}`);
  } finally {
    if (requestId === extractRequestSeq) setBusy(false);
  }
}

btn.addEventListener("click", () => extractSubtitle());

trackSelect.addEventListener("change", () => {
  if (urlInput.value.trim()) extractSubtitle(trackSelect.value || 0);
});

copyBtn.addEventListener("click", async () => {
  await navigator.clipboard.writeText(subtitleEl.value || "");
  setStatus(t("copied"));
});

function stopLoginPolling() {
  if (loginPollTimer) {
    clearInterval(loginPollTimer);
    loginPollTimer = null;
  }
}

async function refreshAuthStatus(showStatus = false) {
  try {
    const resp = await fetch("/api/cookie_status", { cache: "no-store" });
    const data = await resp.json();
    currentUser = { has_cookie: !!data.has_cookie, profile: data.profile || null };
    savedProfile = { has_saved_cookie: !!data.has_saved_cookie, profile: data.saved_profile || null };
    renderUserState();
    if (showStatus && data.has_cookie) setStatus(t("cookieDetected"));
  } catch {
    currentUser = { has_cookie: false, profile: null };
    renderUserState();
  }
}

async function pollLoginStatus() {
  if (!currentQrKey) return;

  try {
    const remember = rememberMe.checked ? "1" : "0";
    const resp = await fetch(`/api/login/qrcode/poll?qrcode_key=${encodeURIComponent(currentQrKey)}&remember=${remember}&_=${Date.now()}`, { cache: "no-store" });
    const data = await resp.json();

    if (!resp.ok) {
      loginStatus.textContent = data.detail || t("networkLoginError");
      stopLoginPolling();
      return;
    }

    if (data.status === "waiting_scan") { loginStatus.textContent = t("waitingScan"); return; }
    if (data.status === "waiting_confirm") { loginStatus.textContent = t("waitingConfirm"); return; }

    if (data.status === "expired") {
      loginStatus.textContent = t("qrExpired");
      hideQrImage();
      stopLoginPolling();
      return;
    }

    if (data.status === "success") {
      loginStatus.textContent = t("loginSuccess");
      setStatus(rememberMe.checked ? t("loginSuccessCookie") : t("loginSuccessSession"));
      stopLoginPolling();
      currentUser = { has_cookie: true, profile: data.profile || null };
      if (rememberMe.checked) savedProfile = { has_saved_cookie: true, profile: data.profile || null };
      renderUserState();
      setTimeout(() => {
        loginPanel.classList.add("hidden");
        hideQrImage();
      }, 1000);
      return;
    }

    if (data.status === "success_no_cookie") {
      loginStatus.textContent = data.message || t("noCookie");
      setStatus(t("noCookie"));
      stopLoginPolling();
      return;
    }

    loginStatus.textContent = data.message || `Unknown status: ${data.code}`;
  } catch (e) {
    loginStatus.textContent = t("networkLoginError");
    stopLoginPolling();
  }
}

loginBtn.addEventListener("click", async () => {
  stopLoginPolling();
  loginPanel.classList.remove("hidden");
  hideQrImage();
  currentQrKey = null;
  loginStatus.textContent = t("qrGenerating");

  try {
    const resp = await fetch(`/api/login/qrcode?_=${Date.now()}`, { cache: "no-store" });
    const data = await resp.json();
    if (!resp.ok || !data.ok) {
      loginStatus.textContent = data.detail || t("qrFail");
      return;
    }
    currentQrKey = data.qrcode_key;
    showQrImage(data.image);
    loginStatus.textContent = t("qrUseApp");
    loginPollTimer = setInterval(pollLoginStatus, 2500);
  } catch (e) {
    loginStatus.textContent = t("qrFail");
  }
});

quickLoginBtn.addEventListener("click", async () => {
  try {
    const resp = await fetch("/api/use_saved_cookie", { method: "POST", cache: "no-store" });
    const data = await resp.json();
    if (!resp.ok || !data.ok) {
      setStatus(data.detail || t("quickLoginFail"));
      return;
    }
    currentUser = { has_cookie: true, profile: data.profile || null };
    renderUserState();
    loginPanel.classList.add("hidden");
    setStatus(t("quickLoginOk"));
  } catch {
    setStatus(t("quickLoginFail"));
  }
});

async function clearCookie({ logout = false } = {}) {
  stopLoginPolling();
  hideQrImage();
  loginPanel.classList.add("hidden");
  await fetch("/api/clear_cookie", { method: "POST", cache: "no-store" });
  currentUser = { has_cookie: false, profile: null };
  savedProfile = { has_saved_cookie: false, profile: null };
  renderUserState();
  setStatus(logout ? t("loggedOut") : t("cleared"));
}

async function setManualCookie() {
  const cookie = prompt(t("manualPrompt"));
  if (cookie === null) return;
  const trimmed = cookie.trim();
  if (!trimmed) {
    await clearCookie();
    return;
  }

  const resp = await fetch("/api/set_cookie", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cookie: trimmed, remember: true }),
    cache: "no-store",
  });
  if (!resp.ok) {
    setStatus(await readError(resp, t("setCookieFail")));
    return;
  }
  const data = await resp.json();
  currentUser = { has_cookie: true, profile: data.profile || null };
  savedProfile = { has_saved_cookie: true, profile: data.profile || null };
  renderUserState();
  setStatus(t("cookieSet"));
}

avatarBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  userMenu.classList.toggle("hidden");
});

document.addEventListener("click", () => userMenu.classList.add("hidden"));
userMenu.addEventListener("click", (e) => e.stopPropagation());

menuManualCookieBtn.addEventListener("click", () => { userMenu.classList.add("hidden"); setManualCookie(); });
menuClearCookieBtn.addEventListener("click", () => { userMenu.classList.add("hidden"); clearCookie(); });
menuLogoutBtn.addEventListener("click", () => { userMenu.classList.add("hidden"); clearCookie({ logout: true }); });

languageSelect.addEventListener("change", () => {
  currentLang = languageSelect.value;
  localStorage.setItem("ui_lang", currentLang);
  applyI18n();
});

hideQrImage();
resetResultArea();
applyI18n();
refreshAuthStatus(true);
