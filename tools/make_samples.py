#!/usr/bin/env python3
"""Tạo trang nghe thử nhiều kiểu giọng đọc: voicetest/index.html (Pages: .../Tiachop/voicetest/)."""
import asyncio, os, sys, html
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "voicetest")
VI = [
    ("A", "Hiện tại: HoaiMy, chậm nhẹ", "vi-VN-HoaiMyNeural", "-8%", "+4Hz"),
    ("B", "HoaiMy tự nhiên (tốc độ chuẩn)", "vi-VN-HoaiMyNeural", "+0%", "+0Hz"),
    ("C", "HoaiMy vui tươi, cao giọng", "vi-VN-HoaiMyNeural", "-5%", "+12Hz"),
    ("D", "HoaiMy chậm rõ, cao giọng", "vi-VN-HoaiMyNeural", "-15%", "+8Hz"),
    ("E", "NamMinh (giọng nam), tốc độ chuẩn", "vi-VN-NamMinhNeural", "+0%", "+0Hz"),
    ("F", "NamMinh chậm, hơi cao", "vi-VN-NamMinhNeural", "-12%", "+6Hz"),
]
EN = [
    ("A", "Hiện tại: Ana (trẻ em)", "en-US-AnaNeural", "-8%", "+0Hz"),
    ("B", "Ana tốc độ chuẩn", "en-US-AnaNeural", "+0%", "+0Hz"),
    ("C", "Jenny", "en-US-JennyNeural", "-5%", "+0Hz"),
    ("D", "Maisie (trẻ em, giọng Anh)", "en-GB-MaisieNeural", "-5%", "+0Hz"),
]
VI_S = ["Con gì kêu “gâu gâu”?", "Đúng rồi! Con chó kêu gâu gâu.", "Có ba quả táo.", "Hoan hô! Bé giỏi quá!"]
EN_S = ["Who says “woof woof”?", "Great job! The dog says woof woof.", "There are three apples."]


async def one(sem, text, voice, rate, pitch, path):
    async with sem:
        for a in range(4):
            try:
                await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)
                if os.path.getsize(path) > 500:
                    return
            except Exception as e:
                print("lỗi", voice, e, file=sys.stderr)
            await asyncio.sleep(1.5 * (a + 1))


async def main():
    os.makedirs(OUT, exist_ok=True)
    sem = asyncio.Semaphore(4)
    jobs, rows = [], []
    for lang, variants, sents in (("vi", VI, VI_S), ("en", EN, EN_S)):
        rows.append('<h2>%s</h2>' % ("Tiếng Việt" if lang == "vi" else "Tiếng Anh"))
        for k, name, voice, rate, pitch in variants:
            cells = []
            for i, s in enumerate(sents):
                fn = "%s_%s_%d.mp3" % (lang, k, i)
                jobs.append(one(sem, s, voice, rate, pitch, os.path.join(OUT, fn)))
                cells.append('<div class="c"><small>%s</small><audio controls preload="none" src="%s"></audio></div>' % (html.escape(s), fn))
            rows.append('<section><h3>%s · %s</h3>%s</section>' % (lang.upper() + k, html.escape(name), "".join(cells)))
    await asyncio.gather(*jobs)
    page = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Nghe thử giọng</title><style>body{font:16px system-ui;max-width:720px;margin:0 auto;padding:14px}'
            'section{border:1px solid #ccc;border-radius:12px;padding:10px;margin:10px 0}h3{margin:0 0 6px}'
            '.c{margin:8px 0}audio{width:100%%}small{display:block;color:#555}</style>'
            '<h1>Nghe thử giọng đọc</h1><p>Nghe từng kiểu rồi báo mình kiểu nào (ví dụ: tiếng Việt C, tiếng Anh A).</p>%s' % "".join(rows))
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
    print("xong", len(jobs), "file")


asyncio.run(main())
