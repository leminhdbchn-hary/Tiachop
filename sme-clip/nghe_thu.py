#!/usr/bin/env python3
"""Mọi giọng VieNeu đọc thử 2 câu thuyết minh clip SME -> sme-clip/nghe_thu/<số>_<câu>.mp3 + giong.json"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tao_giong import load
HERE = os.path.dirname(os.path.abspath(__file__))
CAU = ["Bước 2: Tab Giấy nhận nợ, gõ tên hoặc CIF để chọn khách hàng.",
       "Kết quả: Thông báo tác nghiệp điền sẵn, xem trước cùng dữ liệu trước khi tải file Word."]
tts = load(); voices = tts.list_preset_voices(); out = os.path.join(HERE, "nghe_thu"); os.makedirs(out, exist_ok=True)
info = []
for n, v in enumerate(voices):
    lab = v[0] if isinstance(v, (list, tuple)) else v
    vid = v[1] if isinstance(v, (list, tuple)) else v
    for k, c in enumerate(CAU):
        try:
            try: a = tts.infer(c, voice=lab)
            except Exception: a = tts.infer(c, voice=vid)
            wav = os.path.join(out, "t.wav"); tts.save(a, wav)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "24000", "-af",
                            "atempo=0.95,loudnorm=I=-18:TP=-2:LRA=7", "-b:a", "48k", os.path.join(out, "%02d_%d.mp3" % (n, k))], check=True)
            os.remove(wav)
        except Exception as e:
            print("lỗi", lab, e, file=sys.stderr)
    info.append({"n": n, "label": str(lab), "id": str(vid)}); print(n, lab, flush=True)
json.dump({"cau": CAU, "giong": info}, open(os.path.join(out, "giong.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
