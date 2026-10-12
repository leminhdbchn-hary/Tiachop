#!/usr/bin/env python3
"""Tạo giọng đọc AI cho game Bé Vui Học.
Đọc tools/phrases.json -> tạo audio/<mã>.mp3 (bỏ qua file đã có) -> ghi audio/manifest.json.
Giọng: tiếng Việt vi-VN-HoaiMyNeural (nữ, giọng miền Bắc, đọc chậm), tiếng Anh en-US-AnaNeural (giọng bé gái).
Chạy: pip install edge-tts && python3 tools/make_audio.py
Muốn tạo lại toàn bộ: xoá thư mục audio/ rồi chạy lại.

Azure Speech (dịch vụ chính thức của Microsoft, cùng giọng, gói miễn phí F0): đặt biến môi trường AZURE_SPEECH_KEY và
AZURE_SPEECH_REGION (ví dụ southeastasia) thì script dùng Azure thay cho edge-tts. Trên GitHub: Settings > Secrets and
variables > Actions, thêm hai secret cùng tên. Gói F0 giới hạn khoảng 20 câu/phút nên script tự đọc chậm lại (AZURE_RPM)."""
import asyncio, json, os, re, sys, time, urllib.request
from xml.sax.saxutils import escape
import aiohttp
import edge_tts
import edge_tts.communicate as _ec
import edge_tts.constants as _ek


def edge_version():  # bản Edge mới nhất; máy chủ đọc từ chối (403) khi edge-tts khai báo bản Edge quá cũ
    v = os.environ.get("EDGE_VERSION", "").strip()
    if v:
        return v
    try:
        req = urllib.request.Request("https://edgeupdates.microsoft.com/api/products", headers={"User-Agent": "Mozilla/5.0"})
        for p in json.load(urllib.request.urlopen(req, timeout=20)):
            if p.get("Product") == "Stable":
                for r in p.get("Releases", []):
                    if r.get("Platform") == "Windows" and r.get("ProductVersion"):
                        return r["ProductVersion"]
    except Exception as e:
        print("không lấy được phiên bản Edge:", e, file=sys.stderr)
    return None


def patch_edge():
    new, old = edge_version(), _ek.CHROMIUM_FULL_VERSION
    if not new or tuple(map(int, new.split("."))) <= tuple(map(int, old.split("."))):
        return
    oldm, newm = old.split(".")[0], new.split(".")[0]
    _ec.SEC_MS_GEC_VERSION = _ek.SEC_MS_GEC_VERSION = "1-" + new
    for h in (_ek.BASE_HEADERS, _ek.WSS_HEADERS, _ek.VOICE_HEADERS, _ec.WSS_HEADERS):
        for k in list(h):
            h[k] = h[k].replace(oldm + ".0.0.0", newm + ".0.0.0").replace('v="%s"' % oldm, 'v="%s"' % newm)
    print("Dùng phiên bản Edge", new)

VOICES = {"vi": ("vi-VN-HoaiMyNeural", "-8%", "+0Hz"), "en": ("en-US-AnaNeural", "-5%", "+0Hz")}
SIG = json.dumps(VOICES, sort_keys=True) + "|v4"  # đổi giọng/cách đọc -> tự tạo lại toàn bộ file
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "audio")


def clip_id(text, lang):  # phải khớp hàm clipId() trong index.html (FNV-1a 32 bit)
    h = 2166136261
    for b in (lang + "|" + text.strip()).encode("utf-8"):
        h ^= b
        h = (h * 16777619) & 0xFFFFFFFF
    return "%08x" % h


def spoken(text):  # bỏ dấu ngoặc kép để giọng đọc không đọc ra thành tiếng
    t = re.sub(r"[“”\"«»]", "", text).replace("’", "'")
    return re.sub(r"\s+", " ", t).strip()


AZ_KEY = os.environ.get("AZURE_SPEECH_KEY", "").strip()
AZ_REGION = os.environ.get("AZURE_SPEECH_REGION", "").strip()
AZ = {"gap": 60.0 / max(1, int(os.environ.get("AZURE_RPM", "18") or 18)), "next": 0.0, "lock": None, "http": None}


async def az_save(text, voice, rate, pitch, path):
    """Gọi Azure Speech REST, lưu mp3 cùng định dạng với edge-tts. Tự giãn nhịp theo giới hạn gói miễn phí."""
    lang = voice[:5]
    ssml = ("<speak version='1.0' xml:lang='%s'><voice name='%s'><prosody rate='%s' pitch='%s'>%s</prosody></voice></speak>"
            % (lang, voice, rate, pitch, escape(text)))
    url = "https://%s.tts.speech.microsoft.com/cognitiveservices/v1" % AZ_REGION
    headers = {"Ocp-Apim-Subscription-Key": AZ_KEY, "Content-Type": "application/ssml+xml",
               "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3", "User-Agent": "BeVuiHoc"}
    for _ in range(8):
        async with AZ["lock"]:  # mỗi lần chỉ gửi một câu, cách nhau AZ["gap"] giây
            wait = AZ["next"] - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)
            AZ["next"] = time.monotonic() + AZ["gap"]
            async with AZ["http"].post(url, data=ssml.encode("utf-8"), headers=headers) as r:
                body = await r.read()
                if r.status == 200:
                    with open(path, "wb") as f:
                        f.write(body)
                    return
                if r.status == 429:  # quá giới hạn: chờ rồi thử lại, không tính là lỗi
                    AZ["next"] = time.monotonic() + float(r.headers.get("Retry-After") or 10)
                    continue
                raise RuntimeError("Azure %d %s" % (r.status, body[:200].decode("utf-8", "replace")))
    raise RuntimeError("Azure 429 quá nhiều lần")


FAIL = {"run": 0, "stop": False}  # đếm số câu lỗi liên tiếp; lỗi hàng loạt thì dừng sớm thay vì chạy cả tiếng


async def make(sem, text, lang, path):
    voice, rate, pitch = VOICES[lang]
    text = spoken(text)
    async with sem:
        if FAIL["stop"]:
            return False
        for attempt in range(4):
            try:
                if AZ_KEY:
                    await az_save(text, voice, rate, pitch, path)
                else:
                    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)
                if os.path.getsize(path) > 500:
                    FAIL["run"] = 0
                    return True
            except Exception as e:  # thử lại
                print("lỗi", attempt + 1, text, e, file=sys.stderr)
            await asyncio.sleep(1.5 * (attempt + 1))
    if os.path.exists(path):
        os.remove(path)
    FAIL["run"] += 1
    if FAIL["run"] >= 20 and not FAIL["stop"]:
        FAIL["stop"] = True
        print("DỪNG: 20 câu liên tiếp bị lỗi, máy chủ giọng đọc đang từ chối. Giữ lại các câu đã tạo được.", file=sys.stderr)
    return False


async def main():
    if AZ_KEY:
        if not AZ_REGION:
            sys.exit("Thiếu AZURE_SPEECH_REGION (ví dụ southeastasia)")
        AZ["lock"] = asyncio.Lock()
        AZ["http"] = aiohttp.ClientSession()
        print("Dùng Azure Speech, vùng", AZ_REGION)
    else:
        patch_edge()
    os.makedirs(OUT, exist_ok=True)
    phrases = json.load(open(os.path.join(ROOT, "tools", "phrases.json"), encoding="utf-8"))
    try:  # câu đọc cho ảnh ô tô trong cars/cars.json
        cj = json.load(open(os.path.join(ROOT, "cars", "cars.json"), encoding="utf-8"))["cars"]
    except Exception:
        cj = []
    phrases = [list(p) for p in phrases] + [["Đây là xe gì?", "vi"], ["What car is this?", "en"]]
    for c in cj:
        for k, lg in (("pickvi", "vi"), ("picken", "en"), ("winvi", "vi"), ("winen", "en")):
            if c.get(k):
                phrases.append([c[k], lg])
    sem = asyncio.Semaphore(4)
    try:
        old_sig = json.load(open(os.path.join(OUT, "manifest.json"), encoding="utf-8")).get("sig")
    except Exception:
        old_sig = None
    force = old_sig != SIG
    jobs, clips = [], {}
    for text, lang in phrases:
        cid = clip_id(text, lang)
        path = os.path.join(OUT, cid + ".mp3")
        clips[cid] = text.strip()
        if force or not (os.path.exists(path) and os.path.getsize(path) > 500):
            jobs.append((cid, make(sem, text, lang, path)))
    res = await asyncio.gather(*[j for _, j in jobs])
    if AZ["http"]:
        await AZ["http"].close()
    failed = [cid for (cid, _), ok in zip(jobs, res) if not ok]
    good = {c: t for c, t in clips.items() if c not in failed}
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"sig": SIG, "clips": good}, f, ensure_ascii=False, indent=0)
    print("Tạo mới %d, thành công %d/%d, lỗi %d (%s)" % (len(jobs), len(good), len(clips), len(failed),
          "Azure Speech " + AZ_REGION if AZ_KEY else "edge-tts %s, Edge %s" % (getattr(edge_tts, "__version__", "?"), _ec.SEC_MS_GEC_VERSION)))
    if len(good) < len(clips) * 0.9:
        sys.exit(1)


asyncio.run(main())
