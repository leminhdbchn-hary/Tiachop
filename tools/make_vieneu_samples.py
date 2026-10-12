#!/usr/bin/env python3
"""Trang nghe thử giọng VieNeu-TTS (mã nguồn mở, Apache-2.0, chạy trên CPU, không cần tài khoản):
voicetest/vieneu/index.html (Pages: .../Tiachop/voicetest/vieneu/). Mỗi giọng có sẵn đọc cùng các câu mẫu,
kèm giọng HoaiMy hiện tại để so sánh. Chạy: pip install vieneu && python3 tools/make_vieneu_samples.py (cần ffmpeg)."""
import html, os, subprocess, sys, traceback
from vieneu import Vieneu

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "voicetest", "vieneu")
# 4 câu đầu giống trang nghe thử cũ (voicetest/vi_A_*.mp3 là HoaiMy) để so sánh
VI_S = ["Con gì kêu “gâu gâu”?", "Đúng rồi! Con chó kêu gâu gâu.", "Có ba quả táo.", "Hoan hô! Bé giỏi quá!",
        "Xe kem màu trắng, chạy giữa trời nắng. Leng keng leng keng, mời bé ăn kem.",
        "Dung dăng dung dẻ, dắt trẻ đi chơi."]
EN_S = ["Who says woof woof?", "Great job! The dog says woof woof."]


def mp3(audio, tts, path):
    wav = path[:-4] + ".wav"
    tts.save(audio, wav)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "24000", "-b:a", "64k", path], check=True)
    os.remove(wav)


def main():
    os.makedirs(OUT, exist_ok=True)
    tts = Vieneu()
    voices = tts.list_preset_voices()
    print("Giọng có sẵn:", voices)
    rows = ['<section><h3>Hiện tại · HoaiMy (Microsoft)</h3>%s</section>' % "".join(
        '<div class="c"><small>%s</small><audio controls preload="none" src="../vi_A_%d.mp3"></audio></div>' % (html.escape(s), i)
        for i, s in enumerate(VI_S[:4]))]
    for n, (label, vid) in enumerate(voices):
        cells = []
        for lang, sents in (("vi", VI_S), ("en", EN_S)):
            for i, s in enumerate(sents):
                fn = "v%d_%s_%d.mp3" % (n, lang, i)
                try:
                    try:
                        audio = tts.infer(s.replace("“", "").replace("”", ""), voice=label)
                    except Exception:
                        audio = tts.infer(s.replace("“", "").replace("”", ""), voice=vid)
                    mp3(audio, tts, os.path.join(OUT, fn))
                    cells.append('<div class="c"><small>%s</small><audio controls preload="none" src="%s"></audio></div>' % (html.escape(s), fn))
                except Exception:
                    traceback.print_exc()
        rows.append('<section><h3>%d · %s</h3>%s</section>' % (n + 1, html.escape(str(label)), "".join(cells)))
        print("xong giọng", label, flush=True)
    page = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Nghe thử giọng VieNeu</title><style>body{font:16px system-ui;max-width:720px;margin:0 auto;padding:14px}'
            'section{border:1px solid #ccc;border-radius:12px;padding:10px;margin:10px 0}h3{margin:0 0 6px}'
            '.c{margin:8px 0}audio{width:100%}small{display:block;color:#555}</style>'
            '<h1>Nghe thử giọng VieNeu-TTS</h1><p>Nghe từng giọng rồi báo số giọng bé thích nhất (ví dụ: giọng 3). '
            'Giọng đầu tiên là HoaiMy đang dùng, để so sánh.</p>' + "".join(rows))
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
    if len(rows) < 2:
        sys.exit("Không tạo được giọng nào")


main()
