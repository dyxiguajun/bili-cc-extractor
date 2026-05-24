import os
import re
import json
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


COOKIE_FILE = os.path.join(os.path.dirname(__file__), ".bili_cookie")
PROFILE_FILE = os.path.join(os.path.dirname(__file__), ".bili_profile.json")


def get_cookie_value() -> str:
    """
    读取当前本地 Cookie。
    优先使用环境变量 BILI_COOKIE；如果没有，则读取 backend/.bili_cookie。
    """
    cookie = os.getenv("BILI_COOKIE", "").strip()
    if cookie:
        return cookie

    if os.path.exists(COOKIE_FILE):
        try:
            return open(COOKIE_FILE, "r", encoding="utf-8").read().strip()
        except Exception:
            return ""

    return ""


def get_saved_cookie_value() -> str:
    if os.path.exists(COOKIE_FILE):
        try:
            return open(COOKIE_FILE, "r", encoding="utf-8").read().strip()
        except Exception:
            return ""
    return ""


def set_profile_value(profile, persist: bool = True) -> None:
    profile = profile or {}
    os.environ["BILI_PROFILE_JSON"] = json.dumps(profile, ensure_ascii=False)
    if persist:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)


def get_profile_value() -> dict:
    raw = os.getenv("BILI_PROFILE_JSON", "").strip()
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    if os.path.exists(PROFILE_FILE):
        try:
            return json.load(open(PROFILE_FILE, "r", encoding="utf-8"))
        except Exception:
            return {}
    return {}


def clear_profile_value() -> None:
    os.environ.pop("BILI_PROFILE_JSON", None)
    if os.path.exists(PROFILE_FILE):
        try:
            os.remove(PROFILE_FILE)
        except Exception:
            pass


def fetch_nav_profile(cookie=None) -> dict:
    """Fetch current Bilibili user profile from the nav API. Never returns cookie."""
    h = make_headers()
    if cookie:
        h["Cookie"] = cookie
    r = requests.get("https://api.bilibili.com/x/web-interface/nav", headers=h, timeout=15)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 0 or not (j.get("data") or {}).get("isLogin"):
        return {}
    d = j.get("data") or {}
    return {
        "mid": d.get("mid"),
        "nickname": d.get("uname") or d.get("name"),
        "avatar_url": (d.get("face") or "").replace("http://", "https://"),
    }


def set_cookie_value(cookie: str, persist: bool = True) -> None:
    cookie = (cookie or "").strip()
    os.environ["BILI_COOKIE"] = cookie

    if persist:
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            f.write(cookie)


def clear_cookie_value(clear_saved: bool = True) -> None:
    os.environ.pop("BILI_COOKIE", None)
    if clear_saved and os.path.exists(COOKIE_FILE):
        try:
            os.remove(COOKIE_FILE)
        except Exception:
            pass
    if clear_saved:
        clear_profile_value()


def make_headers(bvid: str = "") -> dict:
    """
    更像浏览器访问视频页：对字幕/封面更友好。
    Cookie 仅保存在本机 backend/.bili_cookie，不会上传到任何服务器。
    """
    h = {
        "User-Agent": UA,
        "Referer": f"https://www.bilibili.com/video/{bvid}" if bvid else "https://www.bilibili.com/",
    }
    cookie = get_cookie_value()
    if cookie:
        h["Cookie"] = cookie
    return h


def parse_bvid(url: str) -> str:
    m = re.search(r"(BV[0-9A-Za-z]{10})", url)
    if not m:
        raise ValueError("没找到BV号：请粘贴包含 BVxxxx 的B站链接")
    return m.group(1)


def parse_page_number(url: str) -> int:
    m = re.search(r"[?&]p=(\d+)", url)
    if not m:
        return 1
    return max(int(m.group(1)), 1)


def fetch_view_info(bvid: str) -> dict:
    api = "https://api.bilibili.com/x/web-interface/view"
    r = requests.get(api, params={"bvid": bvid}, headers=make_headers(bvid), timeout=15)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 0:
        raise RuntimeError(f"view接口失败：code={j.get('code')} msg={j.get('message')}")
    return j["data"]


def pick_cid(view_data: dict, p: int) -> int:
    pages = view_data.get("pages", [])
    if not pages:
        raise RuntimeError("该视频没有 pages 信息，可能不可访问")
    idx = min(max(p - 1, 0), len(pages) - 1)
    return int(pages[idx]["cid"])


def fetch_player_info(bvid: str, aid: int, cid: int) -> dict:
    api = "https://api.bilibili.com/x/player/v2"
    params = {"bvid": bvid, "aid": aid, "cid": cid}  
    r = requests.get(api, params=params, headers=make_headers(bvid), timeout=15)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 0:
        raise RuntimeError(f"player接口失败：code={j.get('code')} msg={j.get('message')}")
    return j["data"]


def to_https(url: str) -> str:
    if url.startswith("//"):
        return "https:" + url
    return url.replace("http://", "https://")


import time
import requests

def fetch_subtitle_json(bvid: str, subtitle_url: str) -> dict:
    u = to_https(subtitle_url).strip()
    if not u:
        raise ValueError("empty subtitle_url")

    #cache-bust：避免 CDN 返回旧/错内容
    sep = "&" if "?" in u else "?"
    u = f"{u}{sep}_ts={int(time.time() * 1000)}"

    r = requests.get(u, headers=make_headers(bvid), timeout=15)
    r.raise_for_status()
    return r.json()

def subtitle_json_to_text(sub_json: dict) -> str:
    items = sub_json.get("body", [])
    lines = []
    for it in items:
        content = (it.get("content") or "").strip()
        if content:
            lines.append(content)
    return "\n".join(lines)


def _srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h = ms // 3600000
    ms -= h * 3600000
    m = ms // 60000
    ms -= m * 60000
    s = ms // 1000
    ms -= s * 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def subtitle_json_to_srt(sub_json: dict) -> str:
    items = sub_json.get("body", [])
    out = []
    idx = 1
    for it in items:
        start = float(it.get("from", 0))
        end = float(it.get("to", 0))
        text = (it.get("content") or "").strip()
        if not text:
            continue
        out.append(str(idx))
        out.append(f"{_srt_time(start)} --> {_srt_time(end)}")
        out.append(text)
        out.append("")
        idx += 1
    return "\n".join(out)


def extract_with_tracks(url: str) -> dict:
    bvid = parse_bvid(url)
    p = parse_page_number(url)

    view = fetch_view_info(bvid)
    title = view.get("title", "")
    cover = (view.get("pic", "") or "").replace("http://", "https://")
    aid = int(view.get("aid", 0))

    pages = view.get("pages", [])
    if not pages:
        raise RuntimeError("该视频没有 pages 信息，可能不可访问")

    idx = min(max(p - 1, 0), len(pages) - 1)
    cid = int(pages[idx]["cid"])

    # 本P时长（秒）
    page_duration = int(pages[idx].get("duration", 0) or 0)

    player = fetch_player_info(bvid=bvid, aid=aid, cid=cid)
    sub = (player.get("subtitle") or {})
    tracks = sub.get("subtitles") or []

    return {
        "title": title,
        "cover_url": cover,
        "bvid": bvid,
        "p": p,
        "aid": aid,
        "cid": cid,
        "tracks": tracks,
        "page_duration": page_duration,  
    }

def subtitle_max_to_seconds(sub_json: dict) -> float:
    body = sub_json.get("body", []) or []
    if not body:
        return 0.0
    return max(float(it.get("to", 0) or 0) for it in body)

import re

def detect_lang_score(text: str, lang: str) -> float:
    """
    粗略判断字幕文本是否符合目标语言。
    返回 0~1 的比例，越高越像该语言。
    lang: 'ja' / 'en' / 'zh'
    """
    if not text:
        return 0.0

    s = text[:5000]  # 只看前5000字符，够用了
    total = len(s)
    if total == 0:
        return 0.0

    if lang == "ja":
        # 平假名/片假名
        m = re.findall(r"[\u3040-\u30ff]", s)
        return len(m) / total

    if lang == "en":
        m = re.findall(r"[A-Za-z]", s)
        return len(m) / total

    if lang == "zh":
        m = re.findall(r"[\u4e00-\u9fff]", s)
        return len(m) / total

    return 0.0