#!/usr/bin/env python3
"""Tạo giọng thuyết minh clip "Hỗ trợ tác nghiệp SME" bằng VieNeu-TTS (Apache-2.0, chạy CPU).
Đọc sme-clip/loi_doc.json (chỉ lời thuyết minh chung, không có dữ liệu khách hàng), ghi sme-clip/audio/<giọng>/<số>.mp3"""
import json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
GIONG = ["Quốc Tuấn"]
SPEED = 0.95

def load():
    from vieneu import Vieneu
    try:
        return Vieneu()
    except Exception as e:
        print("Sửa bộ nhớ đệm:", e, flush=True)
        root = os.environ.get("HF_HUB_CACHE") or os.path.expanduser("~/.cache/huggingface/hub")
        for d, _, fs in os.walk(root):
            for f in fs:
                p = os.path.join(d, f)
                if os.path.islink(p):
                    s = os.path.realpath(p); os.unlink(p); shutil.copyfile(s, p)
        return Vieneu()

def main():
    texts = json.load(open(os.path.join(HERE, "loi_doc.json"), encoding="utf8"))
    tts = load()
    voices = tts.list_preset_voices()
    print("Giọng có sẵn:", voices, flush=True)
    for g in GIONG:
        match = [v for v in voices if g in str(v[0] if isinstance(v, (list, tuple)) else v)]
        if not match:
            print("Không thấy giọng", g, file=sys.stderr); continue
        lab = match[0][0] if isinstance(match[0], (list, tuple)) else match[0]
        vid = match[0][1] if isinstance(match[0], (list, tuple)) else match[0]
        out = os.path.join(HERE, "audio", g.replace(" ", "_"))
        os.makedirs(out, exist_ok=True)
        for i, t in enumerate(texts):
            mp3 = os.path.join(out, "%02d.mp3" % i)
            try:
                a = tts.infer(t, voice=lab)
            except Exception:
                a = tts.infer(t, voice=vid)
            wav = mp3 + ".wav"; tts.save(a, wav)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "24000",
                            "-af", "atempo=%s,loudnorm=I=-18:TP=-2:LRA=7" % SPEED, "-b:a", "48k", mp3], check=True)
            os.remove(wav)
            print(g, i + 1, "/", len(texts), flush=True)

if __name__ == "__main__":
    main()
