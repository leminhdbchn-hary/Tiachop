#!/usr/bin/env python3
"""Tạo giọng đọc AI cho game Bé Vui Học.
Đọc tools/phrases.json -> tạo audio/<mã>.mp3 (bỏ qua file đã có) -> ghi audio/manifest.json.
Giọng: tiếng Việt vi-VN-HoaiMyNeural (nữ, giọng miền Bắc, đọc chậm), tiếng Anh en-US-AnaNeural (giọng bé gái).
Chạy: pip install edge-tts && python3 tools/make_audio.py
Muốn tạo lại toàn bộ: xoá thư mục audio/ rồi chạy lại."""
import asyncio, json, os, re, sys
import edge_tts

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


async def make(sem, text, lang, path):
    voice, rate, pitch = VOICES[lang]
    text = spoken(text)
    async with sem:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)
                if os.path.getsize(path) > 500:
                    return True
            except Exception as e:  # thử lại
                print("lỗi", attempt + 1, text, e, file=sys.stderr)
            await asyncio.sleep(1.5 * (attempt + 1))
    if os.path.exists(path):
        os.remove(path)
    return False


async def main():
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
    failed = [cid for (cid, _), ok in zip(jobs, res) if not ok]
    good = {c: t for c, t in clips.items() if c not in failed}
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"sig": SIG, "clips": good}, f, ensure_ascii=False, indent=0)
    print("Tạo mới %d, thành công %d/%d, lỗi %d" % (len(jobs), len(good), len(clips), len(failed)))
    if len(good) < len(clips) * 0.9:
        sys.exit(1)


asyncio.run(main())
