import bili
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
import time
import hashlib
import os
import io
import base64
import requests
import qrcode
import threading
from fastapi import Body

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/mock_extract")
def mock_extract(url: str):
    return {
        "title": "示例标题",
        "cover_url": "https://placehold.co/480x270",
        "subtitle_text": "MOCK\n"
    }


from fastapi.responses import PlainTextResponse  

from fastapi import HTTPException

@app.get("/api/extract")
def extract(url: str, track: int = 0, debug: int = 0):
    requested_track = track

    try:
        info = bili.extract_with_tracks(url)

        # v1.2.1：不缓存字幕结果。B站字幕接口偶发波动时，缓存旧结果容易造成“串台”。

        expected = int(info.get("page_duration", 0))  # 本P时长（秒）

        def ok_by_duration(sub_json: dict, chosen_track: dict) -> bool:
            """用字幕最大时间戳和视频时长做基本一致性校验，过滤串台"""
            if not expected:
                return True

            max_to = bili.subtitle_max_to_seconds(sub_json)

            lan = (chosen_track.get("lan") or "").lower()
            is_ai = lan.startswith("ai-") or chosen_track.get("ai_status") in (1, 2)

            if is_ai:
                # AI 字幕通常覆盖更完整：严格一些
                return (max_to >= expected * 0.85) and (max_to <= expected * 1.20)
            else:
                # UP 手动字幕可能不全：宽松一些
                return (max_to >= expected * 0.30) and (max_to <= expected * 1.50)
            
        def subtitle_fingerprint(sub_json: dict) -> str:
            txt = bili.subtitle_json_to_text(sub_json)
            # 只取前3000字符做指纹，够区分不同视频
            s = txt[:3000].encode("utf-8", errors="ignore")
            return hashlib.sha1(s).hexdigest()

        def fetch_stable_subtitle(bvid: str, sub_url: str):
            """同一URL抓两次，要求内容一致，否则视为不稳定（疑似串台/抖动）"""
            j1 = bili.fetch_subtitle_json(bvid, sub_url)
            h1 = subtitle_fingerprint(j1)

            time.sleep(0.12)

            j2 = bili.fetch_subtitle_json(bvid, sub_url)
            h2 = subtitle_fingerprint(j2)

            if h1 != h2:
                return None, None  # 不稳定
            return j2, h2

        tracks = []
        need_login = None
        player = None

        #只在“全部校验通过”时才认领为最终结果
        good_sub_json = None
        good_chosen = None
        good_sub_url = ""
        effective_track = None

        max_retry = 8 if requested_track != 0 else 5  # 非中文轨多给点重试次数

        for attempt in range(max_retry):
            player = bili.fetch_player_info(info["bvid"], info["aid"], info["cid"])
            need_login = player.get("need_login_subtitle", None)

            sub = player.get("subtitle") or {}
            tracks = sub.get("subtitles") or []

            if not tracks:
                break

            # 严格按用户选择的 requested_track
            effective_track = max(0, min(requested_track, len(tracks) - 1))
            chosen = tracks[effective_track]
            sub_url = (chosen.get("subtitle_url") or "").strip()

            # 该语言轨偶发没有 url：等一下再试（不要换轨）
            if not sub_url:
                time.sleep(0.25)
                continue

            sub_json, fp = fetch_stable_subtitle(info["bvid"], sub_url)
            if sub_json is None:
                # 同一URL两次内容不一致：高度怀疑串台/抖动，直接重试
                time.sleep(0.25)
                continue

            # 下面继续你的时长校验/语言校验
            if not ok_by_duration(sub_json, chosen):
                time.sleep(0.25)
                continue

            text_preview = bili.subtitle_json_to_text(sub_json)
            lan = (chosen.get("lan") or "").lower()

           
            # 中文也建议加一层“中文字符比例”校验（避免英文轨/别的视频混入）
            if requested_track == 0:
                if bili.detect_lang_score(text_preview, "zh") < 0.02:
                    time.sleep(0.25)
                    continue

            # 只有到这里才认领为 good_sub_json
            good_sub_json = sub_json
            good_chosen = chosen
            good_sub_url = sub_url
            break

            # 1) 时长校验不过：继续重试
            if not ok_by_duration(sub_json, chosen):
                time.sleep(0.35)
                continue

            # 2) 语言一致性校验：避免“日语/英文轨却返回中文”
            text_preview = bili.subtitle_json_to_text(sub_json)
            lan = (chosen.get("lan") or "").lower()

            if "ja" in lan:
                # 日语轨：要求至少一点假名
                if bili.detect_lang_score(text_preview, "ja") < 0.002:
                    time.sleep(0.35)
                    continue

            if "en" in lan:
                # 英文轨：要求有一定比例字母（先放宽到 1%）
                if bili.detect_lang_score(text_preview, "en") < 0.01:
                    time.sleep(0.35)
                    continue

            # 通过全部校验，认领为最终结果
            good_sub_json = sub_json
            good_chosen = chosen
            good_sub_url = sub_url
            break

        # 仍然没拿到字幕：不缓存失败
        if not good_sub_json:
            resp = {
                "title": info["title"],
                "cover_url": info["cover_url"],
                "subtitle_text": "该语言轨暂时获取不到（可能无字幕/需登录/风控/接口波动），请稍后再试或切换轨道。",
                "effective_track": effective_track,
                "tracks": [
                    {
                        "i": i,
                        "lan": t.get("lan"),
                        "lan_doc": t.get("lan_doc"),
                        "ai_status": t.get("ai_status"),
                        "ai_type": t.get("ai_type"),
                        "id": t.get("id"),
                    }
                    for i, t in enumerate(tracks or [])
                ],
                "need_login_subtitle": need_login,
            }
            if debug and player:
                resp.update({
                    "requested_track": requested_track,
                    "selected_subtitle_url": good_sub_url,
                    "player_bvid": player.get("bvid"),
                    "player_cid": player.get("cid"),
                    "aid": info["aid"],
                    "cid": info["cid"],
                    "bvid": info["bvid"],
                })
            return resp

        text = bili.subtitle_json_to_text(good_sub_json)

        resp = {
            "title": info["title"],
            "cover_url": info["cover_url"],
            "subtitle_text": text,
            "effective_track": effective_track,
            "tracks": [
                {
                    "i": i,
                    "lan": t.get("lan"),
                    "lan_doc": t.get("lan_doc"),
                    "ai_status": t.get("ai_status"),
                    "ai_type": t.get("ai_type"),
                    "id": t.get("id"),
                }
                for i, t in enumerate(tracks)
            ],
        }

        if debug:
            resp.update({
                "requested_track": requested_track,
                "effective_track": effective_track,
                "selected_lan_doc": (good_chosen or {}).get("lan_doc"),
                "selected_ai_type": (good_chosen or {}).get("ai_type"),
                "selected_subtitle_url": good_sub_url,
                "need_login_subtitle": need_login,
                "player_bvid": (player or {}).get("bvid"),
                "player_cid": (player or {}).get("cid"),
                "aid": info["aid"],
                "cid": info["cid"],
                "bvid": info["bvid"],
                "expected_duration": expected,
            })

        return resp

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/set_cookie")
def set_cookie(payload: dict = Body(...)):
    cookie = (payload.get("cookie") or "").strip()
    remember = bool(payload.get("remember", True))
    if not cookie:
        raise HTTPException(status_code=400, detail="cookie 不能为空")
    bili.set_cookie_value(cookie, persist=remember)
    profile = {}
    try:
        profile = bili.fetch_nav_profile(cookie)
        bili.set_profile_value(profile, persist=remember)
    except Exception:
        profile = {}
    return {"ok": True, "profile": profile}

@app.post("/api/clear_cookie")
def clear_cookie():
    bili.clear_cookie_value()
    return {"ok": True}




@app.get("/api/cookie_status")
def cookie_status():
    cookie = bili.get_cookie_value()
    saved_cookie = bili.get_saved_cookie_value()
    profile = bili.get_profile_value() if cookie else {}
    saved_profile = bili.get_profile_value() if saved_cookie else {}

    # 如果有 Cookie 但没有本地昵称/头像，尝试补一次。永远不返回 Cookie 内容。
    if cookie and not profile:
        try:
            profile = bili.fetch_nav_profile(cookie)
            bili.set_profile_value(profile, persist=bool(saved_cookie))
        except Exception:
            profile = {}

    return {
        "has_cookie": bool(cookie),
        "profile": profile,
        "has_saved_cookie": bool(saved_cookie),
        "saved_profile": saved_profile or profile,
    }


@app.post("/api/use_saved_cookie")
def use_saved_cookie():
    cookie = bili.get_saved_cookie_value()
    if not cookie:
        raise HTTPException(status_code=404, detail="没有保存的 Cookie，请重新扫码登录。")
    bili.set_cookie_value(cookie, persist=True)
    profile = bili.get_profile_value()
    if not profile:
        try:
            profile = bili.fetch_nav_profile(cookie)
            bili.set_profile_value(profile, persist=True)
        except Exception:
            profile = {}
    return {"ok": True, "profile": profile}


@app.get("/api/login/qrcode")
def login_qrcode():
    """
    生成 Bilibili Web 端扫码登录二维码。
    返回二维码图片 data URL 和 qrcode_key。
    """
    try:
        api = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
        r = requests.get(api, headers=bili.make_headers(), timeout=15)
        r.raise_for_status()
        j = r.json()

        if j.get("code") != 0:
            raise RuntimeError(f"二维码生成失败：code={j.get('code')} msg={j.get('message')}")

        data = j.get("data") or {}
        login_url = data.get("url") or ""
        qrcode_key = data.get("qrcode_key") or ""

        if not login_url or not qrcode_key:
            raise RuntimeError("二维码接口返回异常：缺少 url 或 qrcode_key")

        img = qrcode.make(login_url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

        return {
            "ok": True,
            "qrcode_key": qrcode_key,
            "url": login_url,
            "image": f"data:image/png;base64,{img_b64}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _cookie_header_from_response(resp: requests.Response) -> str:
    """
    从扫码登录成功响应中提取 Set-Cookie。
    """
    cookie_dict = requests.utils.dict_from_cookiejar(resp.cookies)
    keep = {}
    for k, v in cookie_dict.items():
        if k in {"SESSDATA", "bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid"}:
            keep[k] = v

    if not keep:
        # 兜底：部分环境下 cookies jar 为空，尝试解析 Set-Cookie 原始头
        raw = resp.headers.get("Set-Cookie", "")
        for part in raw.split(","):
            first = part.strip().split(";", 1)[0]
            if "=" not in first:
                continue
            k, v = first.split("=", 1)
            k = k.strip()
            if k in {"SESSDATA", "bili_jct", "DedeUserID", "DedeUserID__ckMd5", "sid"}:
                keep[k] = v.strip()

    return "; ".join(f"{k}={v}" for k, v in keep.items())


@app.get("/api/login/qrcode/poll")
def login_qrcode_poll(qrcode_key: str, remember: int = 1):
    """
    轮询 Bilibili 扫码登录状态。
    常见状态：
    86101 未扫码
    86090 已扫码，等待确认
    86038 二维码已过期
    0 登录成功
    """
    try:
        api = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        r = requests.get(
            api,
            params={"qrcode_key": qrcode_key},
            headers=bili.make_headers(),
            timeout=15,
            allow_redirects=False,
        )
        r.raise_for_status()
        j = r.json()

        if j.get("code") != 0:
            raise RuntimeError(f"登录轮询失败：code={j.get('code')} msg={j.get('message')}")

        data = j.get("data") or {}
        code = data.get("code")
        message = data.get("message") or ""

        if code == 0:
            cookie = _cookie_header_from_response(r)
            if not cookie:
                # 登录成功但未拿到 Cookie，可能是接口策略变化
                return {
                    "ok": False,
                    "status": "success_no_cookie",
                    "code": code,
                    "message": "扫码成功，但没有从响应中获取到 Cookie。请尝试手动 Cookie 模式。",
                }

            persist = bool(int(remember))
            bili.set_cookie_value(cookie, persist=persist)
            profile = {}
            try:
                profile = bili.fetch_nav_profile(cookie)
                bili.set_profile_value(profile, persist=persist)
            except Exception:
                profile = {}
            return {
                "ok": True,
                "status": "success",
                "code": code,
                "message": "登录成功。" if not persist else "登录成功，Cookie 已保存到本机。",
                "profile": profile,
                "remember": persist,
            }

        status_map = {
            86101: "waiting_scan",
            86090: "waiting_confirm",
            86038: "expired",
        }

        return {
            "ok": False,
            "status": status_map.get(code, "unknown"),
            "code": code,
            "message": message,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/proxy_image")
def proxy_image(url: str):
    """
    代理封面图，避免浏览器直接加载 B站图片时出现防盗链/空 src 破图。
    仅用于前端展示封面，不保存图片。
    """
    try:
        u = bili.to_https((url or "").strip())
        if not u.startswith("https://"):
            raise HTTPException(status_code=400, detail="invalid image url")
        r = requests.get(u, headers=bili.make_headers(), timeout=15)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "image/jpeg")
        return Response(
            content=r.content,
            media_type=content_type,
            headers={"Cache-Control": "no-store, max-age=0"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"封面加载失败：{e}")



@app.post("/api/shutdown")
def shutdown_app():
    """Stop the local backend process after returning a response.

    Startup scripts intentionally run uvicorn without --reload, so this exits
    the exact server process and lets the Windows CMD window close normally.
    """
    def _stop():
        time.sleep(0.8)
        os._exit(0)
    threading.Thread(target=_stop, daemon=True).start()
    return {"ok": True, "message": "Bili CC Extractor is shutting down."}

from fastapi.responses import PlainTextResponse

@app.get("/api/download_srt", response_class=PlainTextResponse)
def download_srt(url: str, track: int = 0):
    info = bili.extract_with_tracks(url)

    # 重新拉一次 player，拿最新 tracks（跟 extract 保持一致）
    player = bili.fetch_player_info(info["bvid"], info["aid"], info["cid"])
    sub = player.get("subtitle") or {}
    tracks = sub.get("subtitles") or []

    if not tracks:
        return PlainTextResponse("No subtitles available.", status_code=404)

    track = max(0, min(track, len(tracks) - 1))
    sub_url = (tracks[track].get("subtitle_url") or "").strip()
    if not sub_url:
        return PlainTextResponse("Selected track has no subtitle_url.", status_code=404)

    sub_json = bili.fetch_subtitle_json(info["bvid"], sub_url)
    srt = bili.subtitle_json_to_srt(sub_json)
    return PlainTextResponse(srt, media_type="text/plain; charset=utf-8")