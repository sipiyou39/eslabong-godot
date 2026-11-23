"""Planches contact à partir des PNG rendus. usage: python sheets.py <dossier_png> <manifest.json> <sortie_dossier> <prefixe> [per_sheet] [views]"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont

src, manifest, out, prefix = sys.argv[1:5]
per = int(sys.argv[5]) if len(sys.argv) > 5 else 6
views = (sys.argv[6] if len(sys.argv) > 6 else "side,tq").split(",")
only = sys.argv[7].split(",") if len(sys.argv) > 7 else None
pieces = json.load(open(manifest))["pieces"]
if only:
    pieces = [p for p in pieces if any(p["name"].startswith(o) for o in only)]
os.makedirs(out, exist_ok=True)
CW, CH = 300, 400
cols = 2
rows = (per + cols - 1) // cols
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 17)
    fsm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
except Exception:
    font = fsm = ImageFont.load_default()


def bgimg(w, h):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        c = int(46 - 16 * y / h)
        for x in range(w):
            px[x, y] = (c, c + 3, c + 12)
    return im

bg_cell = bgimg(CW, CH)
n_sheets = (len(pieces) + per - 1) // per
for s in range(n_sheets):
    chunk = pieces[s * per:(s + 1) * per]
    cellw = CW * len(views)
    sheet = Image.new("RGB", (cellw * cols, (CH + 26) * rows), (24, 26, 34))
    d = ImageDraw.Draw(sheet)
    for k, p in enumerate(chunk):
        cx, cy = (k % cols) * cellw, (k // cols) * (CH + 26)
        for vi, vn in enumerate(p.get("views", "side,tq").split(",") if "--forceviews" not in sys.argv else views):
            f = os.path.join(src, f"{p['name']}__{vn}.png")
            cell = bg_cell.copy()
            if os.path.exists(f):
                im = Image.open(f).convert("RGBA")
                im.thumbnail((CW, CH), Image.LANCZOS)
                cell.paste(im, ((CW - im.width) // 2, (CH - im.height) // 2), im)
            sheet.paste(cell, (cx + vi * CW, cy + 26))
        d.text((cx + 8, cy + 3), p["name"], fill=(240, 240, 240), font=font)
        d.text((cx + cellw - 200, cy + 6), f"{p['triangles']} tris  {p['length']:.2f} m", fill=(170, 190, 220), font=fsm)
    path = os.path.join(out, f"{prefix}_{s + 1:02d}.png")
    sheet.save(path)
    print(path)
