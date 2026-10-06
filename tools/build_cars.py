#!/usr/bin/env python3
"""Quét thư mục cars/ : thu nhỏ ảnh (tối đa 900px, JPG) và tạo cars/cars.json cho game.
Tên file: "<tên tiếng Việt>__<English>.jpg"  ví dụ  "xe tải__truck.jpg"  (phần __English có thể bỏ)."""
import json, os, re, sys, urllib.request
from PIL import Image, ImageOps
try:
    import pillow_heif; pillow_heif.register_heif_opener()
except Exception:
    pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "cars")
EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def art(en):
    return ("an " if re.match(r"[aeiou]", en.lower()) else "a ") + en


def fetch_links():
    """cars/links.txt: mỗi dòng  <đường dẫn ảnh> | <tên tiếng Việt> | <English>  -> tải về cars/<vi>__<en>.<đuôi>"""
    p = os.path.join(D, "links.txt")
    if not os.path.exists(p):
        return
    for line in open(p, encoding="utf-8"):
        parts = [x.strip() for x in line.split("|")]
        if len(parts) < 2 or not parts[0].startswith("http"):
            continue
        url, vi = parts[0], parts[1]
        en = parts[2] if len(parts) > 2 else ""
        ext = os.path.splitext(url.split("?")[0])[1].lower() or ".jpg"
        stem = vi + ("__" + en if en else "")
        if any(os.path.exists(os.path.join(D, stem + e)) for e in (ext, ".jpg")):
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r, open(os.path.join(D, stem + ext), "wb") as f:
                f.write(r.read())
            print("đã tải", url)
        except Exception as e:
            print("không tải được", url, e, file=sys.stderr)


def main():
    os.makedirs(D, exist_ok=True)
    fetch_links()
    cars = []
    for fn in sorted(os.listdir(D)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in EXT:
            continue
        src = os.path.join(D, fn)
        dst_name = stem + ".jpg"
        dst = os.path.join(D, dst_name)
        try:
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            if max(im.size) > 900 or ext.lower() != ".jpg":
                im.thumbnail((900, 900))
                im.save(dst, "JPEG", quality=84, optimize=True)
                if dst != src:
                    os.remove(src)
        except Exception as e:
            print("bỏ qua", fn, e, file=sys.stderr)
            continue
        parts = stem.split("__")
        vi = parts[0].replace("_", " ").strip()
        en = parts[1].replace("_", " ").strip() if len(parts) > 1 else ""
        if not vi:
            continue
        c = {"file": dst_name, "vi": vi, "en": en,
             "pickvi": "Đâu là %s?" % vi, "picken": ("Which one is the %s?" % en) if en else "",
             "winvi": "Đây là %s." % vi, "winen": ("This is %s." % art(en)) if en else ""}
        cars.append(c)
    with open(os.path.join(D, "cars.json"), "w", encoding="utf-8") as f:
        json.dump({"cars": cars}, f, ensure_ascii=False, indent=1)
    print("Số ảnh ô tô:", len(cars))


main()
