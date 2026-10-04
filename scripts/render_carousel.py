"""Gera as imagens do carrossel (1080x1350): capa + N noticias.

Entrada: um dict {"date": "2026-10-05", "headline": "...", "items": [{"title","summary","source"}]}
Saida: lista de caminhos JPEG (slide-01.jpg, ...).
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1350

THEMES = {
    "editorial": dict(bg=(247, 245, 240), accent=(214, 40, 57), text=(18, 18, 18), muted=(110, 110, 110), bar=(18, 18, 18)),
    "amarelo": dict(bg=(10, 10, 10), accent=(255, 214, 10), text=(250, 250, 250), muted=(150, 150, 150), bar=(255, 214, 10)),
    "royal": dict(bg=(22, 48, 168), accent=(255, 214, 10), text=(255, 255, 255), muted=(185, 198, 240), bar=(255, 214, 10)),
}
BG = ACCENT = TEXT = MUTED = BAR = None


def use_theme(name):
    global BG, ACCENT, TEXT, MUTED, BAR
    t = THEMES[name]
    BG, ACCENT, TEXT, MUTED, BAR = t["bg"], t["accent"], t["text"], t["muted"], t["bar"]


use_theme("editorial")

BOLD = [
    ROOT / "fonts" / "bold.ttf",
    Path("C:/Windows/Fonts/segoeuib.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]
REG = [
    ROOT / "fonts" / "regular.ttf",
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]

MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


def font(cands, size):
    for p in cands:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise FileNotFoundError(cands)


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, cands, max_w, max_h, start, stop, step=-2, spacing=1.25):
    for size in range(start, stop, step):
        f = font(cands, size)
        lines = wrap(d, text, f, max_w)
        if len(lines) * int(size * spacing) <= max_h:
            return f, lines, int(size * spacing)
    f = font(cands, stop)
    return f, wrap(d, text, f, max_w), int(stop * spacing)


def base(brand, n, total):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=BAR)
    d.text((80, 70), brand, font=font(BOLD, 34), fill=ACCENT)
    if n:
        s = f"{n}/{total}"
        d.text((W - 80 - d.textlength(s, font=font(REG, 30)), 74), s, font=font(REG, 30), fill=MUTED)
    return img, d


def date_label(iso):
    dt = datetime.strptime(iso, "%Y-%m-%d")
    return f"{dt.day:02d} {MESES[dt.month - 1]} {dt.year}"


def cover(data, cfg, total):
    img, d = base(cfg["brand"], 0, total)
    d.text((80, 330), date_label(data["date"]), font=font(BOLD, 44), fill=MUTED)
    f, lines, lh = fit(d, data["headline"], BOLD, W - 160, 520, 96, 52)
    y = 420
    for ln in lines:
        d.text((80, y), ln, font=f, fill=TEXT)
        y += lh
    d.rectangle([80, y + 30, 240, y + 38], fill=ACCENT)
    d.text((80, H - 190), f"{len(data['items'])} notícias de {cfg['topic']} para hoje", font=font(REG, 38), fill=MUTED)
    d.text((80, H - 120), "Deslize  →", font=font(BOLD, 40), fill=ACCENT)
    return img


def news_slide(item, idx, cfg, total):
    img, d = base(cfg["brand"], idx + 2, total)
    d.text((80, 190), f"{idx + 1:02d}", font=font(BOLD, 120), fill=ACCENT)
    f, lines, lh = fit(d, item["title"], BOLD, W - 160, 380, 68, 40)
    y = 360
    for ln in lines:
        d.text((80, y), ln, font=f, fill=TEXT)
        y += lh
    y += 24
    d.rectangle([80, y, 200, y + 6], fill=ACCENT)
    y += 40
    sf, slines, slh = fit(d, item["summary"], REG, W - 160, H - y - 260, 42, 30, spacing=1.4)
    for ln in slines:
        d.text((80, y), ln, font=sf, fill=TEXT)
        y += slh
    d.text((80, H - 150), f"Fonte: {item['source']}", font=font(REG, 32), fill=MUTED)
    d.text((W - 80 - d.textlength(cfg["handle"], font=font(REG, 30)), H - 148), cfg["handle"], font=font(REG, 30), fill=MUTED)
    return img


def render_all(data, cfg, out_dir):
    use_theme(cfg.get("theme", "editorial"))
    out_dir.mkdir(parents=True, exist_ok=True)
    total = len(data["items"]) + 1
    slides = [cover(data, cfg, total)] + [news_slide(it, i, cfg, total) for i, it in enumerate(data["items"])]
    paths = []
    for i, img in enumerate(slides, 1):
        p = out_dir / f"slide-{i:02d}.jpg"
        img.save(p, "JPEG", quality=95)
        paths.append(p)
    return paths


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "sample.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    for p in render_all(data, cfg, ROOT / "output"):
        print(p)
