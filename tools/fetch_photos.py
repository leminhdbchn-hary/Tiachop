#!/usr/bin/env python3
"""Tải ảnh thật (Wikimedia Commons, giấy phép mở) cho các con vật, đồ vật, nghề nghiệp... trong game Bé Vui Học.

Đọc tools/photo_items.json -> tìm ảnh trên Wikimedia Commons -> tải bản 600px, cắt vuông 480px
-> lưu photos/<tên>.jpg -> ghi photos/manifest.json (kèm tên tác giả, giấy phép, link nguồn),
photos/CREDITS.md và photos/preview.html (trang xem trước để duyệt ảnh).

Chỉ nhận ảnh CC0 / Public domain / CC BY / CC BY-SA (bỏ NC, ND). Tự bỏ ảnh có trẻ em, sơ đồ, tranh vẽ, logo...
Ảnh chưa vừa ý?  - Thêm tên file (dạng File:Ten.jpg) vào photos/skip.txt  -> lần chạy sau tự chọn ảnh khác.
                 - Hoặc chọn tay: thêm dòng  tên_khoá = File:Ten.jpg  vào photos/overrides.txt
Chạy: pip install requests pillow && python3 tools/fetch_photos.py   (GitHub Action make-photos.yml tự chạy)"""
import html, io, json, os, re, sys, time
import requests
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "photos")
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "BeVuiHoc/1.0 (educational kids game; https://github.com/leminhdbchn-hary/Tiachop) python-requests"}
SIZE = 480
CATS = ['incategory:"Quality images"', 'incategory:"Featured pictures on Wikimedia Commons"', 'incategory:"Valued images"', ""]
OK_LICENSE = re.compile(r"^(CC0|CC[ -]?Zero|Public domain|PD\b|CC[ -]BY(-SA)?\b)", re.I)
BAD_LICENSE = re.compile(r"(\bNC\b|-NC|\bND\b|-ND|GFDL only|fair use|copyrighted|non-?free)", re.I)
BAD_TITLE = re.compile(r"(diagram|map\b|drawing|logo|icon|sketch|stamp|illustration|vintage|antique|engraving|poster|cartoon|clipart|"
                       r"dead|killed|butcher|roast|skeleton|fossil|skull|child|children|kid\b|kids|boy\b|boys|girl\b|girls|baby|toddler|"
                       r"pupil|student|infant|nude|naked|bikini|war\b|weapon|gun\b|blood|accident|crash|fire damage|corpse)", re.I)
MIN_W, MIN_H = 640, 480


def read_list(path):
    try:
        return [l.strip() for l in open(path, encoding="utf-8") if l.strip() and not l.strip().startswith("#")]
    except FileNotFoundError:
        return []


def api(params):
    p = {"action": "query", "format": "json", "formatversion": "2", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
         "iiurlwidth": "600", "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|Credit"}
    p.update(params)
    for attempt in range(4):
        try:
            r = requests.get(API, params=p, headers=UA, timeout=40)
            if r.status_code == 200:
                time.sleep(0.25)
                return r.json()
        except Exception as e:
            print("  lỗi mạng:", e, file=sys.stderr)
        time.sleep(2 * (attempt + 1))
    return {}


def meta(v, k):
    return html.unescape(re.sub(r"<[^>]+>", "", str((v.get("extmetadata", {}).get(k) or {}).get("value", "")))).strip()


def usable(page, term_words):
    """Trả về (điểm, thông tin) nếu ảnh dùng được, không thì None."""
    ii = (page.get("imageinfo") or [None])[0]
    if not ii:
        return None
    title = page.get("title", "")
    if BAD_TITLE.search(title):
        return None
    if ii.get("mime") not in ("image/jpeg", "image/png"):
        return None
    w, h = ii.get("width", 0), ii.get("height", 0)
    if w < MIN_W or h < MIN_H:
        return None
    ratio = w / max(h, 1)
    if ratio > 1.8 or ratio < 0.6:
        return None
    lic = meta(ii, "LicenseShortName")
    if not OK_LICENSE.search(lic) or BAD_LICENSE.search(lic):
        return None
    desc = meta(ii, "ImageDescription").lower()
    if BAD_TITLE.search(desc[:200]):
        return None
    tl = title.lower()
    score = -float(page.get("index", 50))
    score += 6 * sum(1 for t in term_words if t in tl)
    score += 2 * sum(1 for t in term_words if t in desc)
    score -= 3 * abs(ratio - 1.25)
    author = meta(ii, "Artist") or meta(ii, "Credit") or "Unknown"
    return score, {"title": title, "thumb": ii.get("thumburl") or ii.get("url"), "a": author[:90], "l": lic[:30], "u": ii.get("descriptionurl", "")}


def search(term, skip):
    words = [w for w in re.findall(r"[a-z]+", term.lower()) if len(w) > 2]
    best = None
    for cat in CATS:
        q = (term + " " + cat + " filetype:bitmap").strip()
        data = api({"generator": "search", "gsrnamespace": "6", "gsrlimit": "30", "gsrsearch": q})
        for page in (data.get("query", {}) or {}).get("pages", []) or []:
            if page.get("title") in skip:
                continue
            u = usable(page, words)
            if u and (best is None or u[0] > best[0]):
                best = u
        if best and best[0] > -12:  # đủ tốt ở nhóm ảnh chất lượng thì dừng
            break
    return best[1] if best else None


def by_title(title):
    data = api({"titles": title})
    for page in (data.get("query", {}) or {}).get("pages", []) or []:
        u = usable(page, [])
        if u:
            return u[1]
        # ảnh do người dùng chọn tay: chấp nhận miễn đúng giấy phép
        ii = (page.get("imageinfo") or [None])[0]
        if ii and OK_LICENSE.search(meta(ii, "LicenseShortName")):
            return {"title": page["title"], "thumb": ii.get("thumburl") or ii.get("url"), "a": (meta(ii, "Artist") or "Unknown")[:90],
                    "l": meta(ii, "LicenseShortName")[:30], "u": ii.get("descriptionurl", "")}
    return None


def save_square(url, path):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=60)
            if r.status_code == 200 and len(r.content) > 2000:
                im = Image.open(io.BytesIO(r.content)).convert("RGB")
                w, h = im.size
                s = min(w, h)
                im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((SIZE, SIZE), Image.LANCZOS)
                im.save(path, "JPEG", quality=80, optimize=True, progressive=True)
                return True
        except Exception as e:
            print("  lỗi tải ảnh:", e, file=sys.stderr)
        time.sleep(2 * (attempt + 1))
    return False


def slug(key):
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_") or "x"


def main():
    os.makedirs(OUT, exist_ok=True)
    items = json.load(open(os.path.join(ROOT, "tools", "photo_items.json"), encoding="utf-8"))
    skip = set(read_list(os.path.join(OUT, "skip.txt")))
    over = {}
    for l in read_list(os.path.join(OUT, "overrides.txt")):
        if "=" in l:
            k, v = l.split("=", 1)
            over[k.strip()] = v.strip()
    try:
        old = json.load(open(os.path.join(OUT, "manifest.json"), encoding="utf-8")).get("items", {})
    except Exception:
        old = {}
    man, miss = {}, []
    for it in items:
        key = it["key"]
        f = slug(key) + ".jpg"
        path = os.path.join(OUT, f)
        o = old.get(key)
        want = over.get(key)
        keep = o and os.path.exists(path) and o.get("t") not in skip and (not want or o.get("t") == want)
        if keep:
            man[key] = o
            continue
        print("→", key, "(" + it["q"] + ")")
        info = by_title(want) if want else search(it["q"], skip)
        if not info or not save_square(info["thumb"], path):
            miss.append(key)
            if os.path.exists(path):
                os.remove(path)
            continue
        man[key] = {"f": f, "t": info["title"], "a": info["a"], "l": info["l"], "u": info["u"]}
        print("   ", info["title"], "|", info["l"])
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"items": man}, fh, ensure_ascii=False, indent=0)
    with open(os.path.join(OUT, "CREDITS.md"), "w", encoding="utf-8") as fh:
        fh.write("# Nguồn ảnh / Photo credits\n\nẢnh từ [Wikimedia Commons](https://commons.wikimedia.org), giấy phép mở. "
                 "Ảnh được cắt vuông và thu nhỏ.\n\n| Từ | Tác giả | Giấy phép | Nguồn |\n|---|---|---|---|\n")
        for k in sorted(man):
            m = man[k]
            fh.write("| %s | %s | %s | [%s](%s) |\n" % (k, m["a"].replace("|", "/").replace("\n", " "), m["l"], m["t"].replace("|", "/"), m["u"]))
    with open(os.path.join(OUT, "preview.html"), "w", encoding="utf-8") as fh:
        fh.write('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Xem trước ảnh</title>'
                 '<style>body{font-family:system-ui;margin:12px;background:#f4f7fb}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}'
                 '.c{background:#fff;border-radius:12px;padding:8px;font-size:12px;box-shadow:0 1px 4px #0002}img{width:100%;border-radius:8px;display:block}b{font-size:14px}</style>'
                 '<h2>Ảnh trong game (%d/%d)</h2><p>Ảnh nào chưa ổn: chép tên file (dòng nhỏ bên dưới ảnh) vào <code>photos/skip.txt</code> rồi chạy lại Action.</p><div class="g">'.replace("%d/%d", "%d/%d" % (len(man), len(items))))
        for k in sorted(man):
            m = man[k]
            fh.write('<div class="c"><img src="%s" loading="lazy"><b>%s</b><br>%s<br>%s</div>' % (m["f"], html.escape(k), html.escape(m["t"]), html.escape(m["l"])))
        fh.write("</div>")
    print("Có ảnh: %d/%d. Chưa tìm được: %s" % (len(man), len(items), ", ".join(miss) or "không"))


if __name__ == "__main__":
    main()
