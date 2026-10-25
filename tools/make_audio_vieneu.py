#!/usr/bin/env python3
"""Tạo giọng đọc tiếng Việt cho game Bé Vui Học bằng VieNeu-TTS, giọng "Ngọc Linh" (mã nguồn mở, Apache-2.0, chạy trên CPU).
Thay cho giọng Microsoft/Google cũ: ghi đè audio/<mã>.mp3 của các câu tiếng Việt (mã câu giữ nguyên nên index.html không đổi).
Tiếng Anh vẫn do tools/make_audio.py tạo.

  python3 tools/make_audio_vieneu.py --shard 0 --of 4     # chia việc cho nhiều máy chạy song song
Câu nào đã xong được ghi vào audio/vieneu_done_<tốc độ>_<shard>.txt nên chạy lại là làm tiếp, không làm lại.
Trong GitHub Actions (biến CI) script tự commit và push sau mỗi CHECKPOINT câu để nếu bị ngắt cũng không mất công.
Muốn đổi giọng hoặc tốc độ: sửa VOICE_NAME / SPEED (đổi SPEED là tự tạo lại toàn bộ); đổi giọng thì xoá các file audio/vieneu_done_*.txt."""
import argparse, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_audio import ROOT, OUT, clip_id, load_phrases, spoken  # noqa: E402

VOICE_NAME = "Ngọc Linh"
SPEED = 0.9  # tốc độ đọc so với bình thường (0.9 = chậm hơn 10%, giữ nguyên cao độ giọng); bé nghe rõ hơn
TAG = "s%d" % round(SPEED * 100)  # đổi SPEED hoặc giọng thì tên file tiến độ đổi theo nên tự tạo lại toàn bộ
CHECKPOINT = 300
MIN_BYTES = 800


def pick_voice(tts):
    voices = tts.list_preset_voices()
    for label, vid in voices:
        if VOICE_NAME in str(label):
            return label, vid
    sys.exit("Không thấy giọng %s trong: %s" % (VOICE_NAME, [l for l, _ in voices]))


def load():
    try:
        from vieneu import Vieneu
        return Vieneu()
    except Exception as e:  # onnxruntime mới không mở được symlink trong bộ nhớ đệm Hugging Face: đổi thành file thật
        import shutil
        print("Lỗi khi mở mô hình, sửa bộ nhớ đệm rồi thử lại:", e, flush=True)
        root = os.environ.get("HF_HUB_CACHE") or os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        for d, _, files in os.walk(root):
            for f in files:
                p = os.path.join(d, f)
                if os.path.islink(p):
                    src = os.path.realpath(p)
                    os.unlink(p)
                    shutil.copyfile(src, p)
        from vieneu import Vieneu
        return Vieneu()


def to_mp3(tts, audio, path):
    wav = path + ".wav"
    tmp = path + ".tmp.mp3"
    tts.save(audio, wav)
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "24000",
                        "-af", "atempo=%s,loudnorm=I=-18:TP=-2:LRA=7" % SPEED, "-b:a", "48k", tmp], check=True)
        if os.path.getsize(tmp) < MIN_BYTES:
            raise RuntimeError("file quá nhỏ")
        os.replace(tmp, path)
    finally:
        for f in (wav, tmp):
            if os.path.exists(f):
                os.remove(f)


def checkpoint(done_file, note):
    if not os.environ.get("CI"):
        return
    sh = lambda *a: subprocess.run(a, cwd=ROOT, capture_output=True, text=True)
    sh("git", "config", "user.name", "github-actions")
    sh("git", "config", "user.email", "github-actions@users.noreply.github.com")
    sh("git", "add", "-A", "audio")
    if sh("git", "diff", "--cached", "--quiet").returncode == 0:
        return
    sh("git", "commit", "-m", "Giọng Ngọc Linh: " + note)
    for i in range(6):
        sh("git", "pull", "--rebase", "-X", "theirs")
        r = sh("git", "push")
        if r.returncode == 0:
            print("đã lưu lên GitHub:", note, flush=True)
            return
        time.sleep(3 * (i + 1))
    print("Chưa push được, sẽ thử lại ở lần lưu sau", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0, help="chỉ làm tối đa N câu (để thử)")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    seen = {}
    for text, lang in load_phrases():
        if lang == "vi":
            seen.setdefault(clip_id(text, lang), text)
    ids = sorted(seen)[a.shard::a.of]
    done_file = os.path.join(OUT, "vieneu_done_%s_%d.txt" % (TAG, a.shard))
    done = set(open(done_file).read().split()) if os.path.exists(done_file) else set()
    todo = [c for c in ids if c not in done]
    if a.limit:
        todo = todo[:a.limit]
    print("Phần %d/%d: %d câu, đã xong %d, còn %d" % (a.shard + 1, a.of, len(ids), len(done), len(todo)), flush=True)
    if not todo:
        return
    tts = load()
    label, vid = pick_voice(tts)
    print("Giọng:", label, flush=True)
    t0, n, bad, since = time.time(), 0, [], 0
    for cid in todo:
        text = spoken(seen[cid], "vi")
        ok = False
        for attempt in range(3):
            try:
                try:
                    audio = tts.infer(text, voice=label)
                except Exception:
                    audio = tts.infer(text, voice=vid)
                to_mp3(tts, audio, os.path.join(OUT, cid + ".mp3"))
                ok = True
                break
            except Exception as e:
                print("lỗi", attempt + 1, repr(text), e, file=sys.stderr, flush=True)
        if ok:
            with open(done_file, "a") as f:
                f.write(cid + "\n")
            n += 1
            since += 1
        else:
            bad.append(cid)
        if (n + len(bad)) % 50 == 0:
            print("%d/%d xong, lỗi %d, %.1f giây/câu" % (n, len(todo), len(bad), (time.time() - t0) / max(1, n + len(bad))), flush=True)
        if since >= CHECKPOINT:
            checkpoint(done_file, "phần %d, %d câu" % (a.shard + 1, n))
            since = 0
    checkpoint(done_file, "phần %d, xong %d câu" % (a.shard + 1, n))
    print("Xong phần %d: %d câu, lỗi %d" % (a.shard + 1, n, len(bad)))
    if bad:
        print("Câu lỗi (sẽ thử lại ở lần chạy sau):", bad[:20], file=sys.stderr)
        sys.exit(1 if len(bad) > len(todo) * 0.05 else 0)


if __name__ == "__main__":
    main()
