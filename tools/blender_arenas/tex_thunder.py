"""Textures de l'arène du Chaos Thunder : dalles sombres, circuits runiques lumineux (albédo + émissif)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import tex as T
from tex import *


def octagon_segs(r, rot=math.pi / 8, cx=0.0, cz=0.0):
    pts = [(cx + r * math.cos(rot + k * math.pi / 4), cz + r * math.sin(rot + k * math.pi / 4)) for k in range(9)]
    return [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(8)]


def ground():
    rng = np.random.default_rng(111)
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    n_big = fbm(X / 6.0, Z / 6.0, 4, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 9, Z * 9, 4, 3)
    # dalles larges 3.2 x 3.2 en appareil régulier
    SX = 3.2
    col = np.floor((X + 27.2) / SX)
    row = np.floor((Z + 17.6) / SX)
    u = (X + 27.2) / SX - col
    v = (Z + 17.6) / SX - row
    sid = hash01(col.astype(np.int64), row.astype(np.int64), 5)
    ed = np.minimum(np.minimum(u * SX, (1 - u) * SX), np.minimum(v * SX, (1 - v) * SX))
    base = grad(np.clip(sid * 0.45 + n_big * 0.55, 0, 1), [(0, hexc('#14121f')), (0.5, hexc('#211e36')), (1, hexc('#2f2b4d'))])
    base = base * (1 + (n_fine[..., None] - 0.5) * 0.25)
    # brillance métallique en veines
    mv = smooth(0.62, 0.8, fbm(X * 1.5, Z * 1.5, 5, 7))
    base = comp(base, hexc('#4a4670'), mv * 0.35)
    bevel = smooth(0.0, 0.14, ed)
    base = base * (0.7 + 0.35 * bevel[..., None])
    joint = smooth(0.05, 0.012, ed)
    base = comp(base, hexc('#07060d'), joint * 0.95)
    hgt = (bevel * 0.03 - joint * 0.03 + n_fine * 0.004).astype(np.float32)
    em = np.zeros((GH, GW, 3), np.float32)
    cyan = hexc('#4fd6ff')
    violet = hexc('#b46bff')
    # fissures d'énergie
    f1, f2, cid = cell(X * 0.45 + n_mid * 1.1, Z * 0.45 + n_mid * 1.1, 17)
    crack = smooth(0.03, 0.0, f2 - f1) * smooth(0.55, 0.75, fbm(X * 0.4, Z * 0.4, 4, 19)) * 0.9
    base = comp(base, hexc('#8fe6ff'), crack * 0.5)
    em += crack[..., None] * cyan * 0.7
    # circuits le long des joints (traces fines) avec noeuds
    trace_off = 0.16
    tr = smooth(0.012, 0.004, np.abs(ed - trace_off)) * (hash01(col.astype(np.int64), row.astype(np.int64), 21) > 0.35)
    node = np.zeros((GH, GW), np.float32)
    base = comp(base, hexc('#2a8cb0'), tr * 0.8)
    em += tr[..., None] * cyan * 0.35
    # --- grand sceau octogonal central
    img = base
    seal = np.zeros((GH, GW), np.float32)
    for r_ in (11.0, 8.2, 5.6, 3.0):
        seal = np.maximum(seal, draw_segs(c, octagon_segs(r_), 0.14 if r_ > 6 else 0.1))
    for r_, rot in ((10.0, 0.0), (6.9, 0.0)):
        seal = np.maximum(seal, draw_segs(c, octagon_segs(r_, rot=rot + math.pi / 8 + math.pi / 8), 0.05))
    spokes = [(3.0 * math.cos(math.pi / 8 + k * math.pi / 4), 3.0 * math.sin(math.pi / 8 + k * math.pi / 4),
               11.0 * math.cos(math.pi / 8 + k * math.pi / 4), 11.0 * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    seal = np.maximum(seal, draw_segs(c, spokes, 0.08))
    seal = np.maximum(seal, draw_segs(c, ring_segs(0, 0, 9.4, 120), 0.05))
    seal = np.maximum(seal, draw_segs(c, ring_segs(0, 0, 4.3, 90), 0.06))
    seal = np.maximum(seal, draw_segs(c, rune_segs(0, 0, 6.9, 32, 0.6, seed=3), 0.045))
    seal = np.maximum(seal, draw_segs(c, rune_segs(0, 0, 9.7, 48, 0.7, seed=4), 0.05))
    seal = np.maximum(seal, draw_circles(c, [(0, 0, 0.9)]))
    star = [(2.0 * math.cos(k * math.pi / 2 + 0.0), 2.0 * math.sin(k * math.pi / 2), 2.0 * math.cos((k + 1) * math.pi / 2), 2.0 * math.sin((k + 1) * math.pi / 2)) for k in range(4)]
    seal = np.maximum(seal, draw_segs(c, star, 0.07))
    wornm = smooth(0.15, 0.45, fbm(X * 1.1, Z * 1.1, 5, 31)) * 0.4 + 0.6
    seal = seal * wornm
    img = comp(img, hexc('#9fe8ff'), seal * 0.85)
    em += seal[..., None] * cyan * 1.0
    # --- zones d'équipe
    for sgn, col_ in ((-1, violet), (1, cyan)):
        cx = 19.0 * sgn
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.14), c.ring(cx, 0, 2.6, 0.08))
        z_ = np.maximum(z_, draw_segs(c, octagon_segs(2.1, cx=cx), 0.07))
        z_ = np.maximum(z_, draw_segs(c, rune_segs(cx, 0, 4.4, 20, 0.45, seed=9 + sgn), 0.045))
        z_ = np.maximum(z_, c.dashed(13.0 * sgn, -12.5, 13.0 * sgn, 12.5, 0.13, 0.9, 0.45))
        z_ = z_ * wornm
        img = comp(img, col_ * 0.9 + 0.1, z_ * 0.85)
        em += z_[..., None] * col_ * 0.95
        em += (c.circle(cx, 0, 3.6) * 0.08)[..., None] * col_
    # liseré lumineux le long du mur
    rim = smooth(0.1, 0.03, np.abs(depth - 0.12)) * wornm
    img = comp(img, hexc('#8fe6ff'), rim * 0.6)
    em += rim[..., None] * cyan * 0.55
    # AO de contact
    ao = c.contact_ao(wall=0.22, wall_len=0.7, obst=0.5, obst_len=0.6)
    img = img * ao[..., None]
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#0b0a14'), under)
        em = em * (1 - under[..., None])
        ring_ = c.ring(ox, oz, r + 0.5, 0.07) * wornm
        img = comp(img, hexc('#9fe8ff'), ring_ * 0.7)
        em += ring_[..., None] * violet * 0.8
    em = np.clip(em, 0, 1.4)
    save('thunder_ground.png', img)
    save('thunder_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    save('thunder_ground_e.png', np.clip(em / 1.4, 0, 1))


def rune_tex():
    """texture runique émissive (tuile 512) : colonnes de glyphes lumineux sur fond sombre."""
    W = 512
    im = Image.new('RGB', (W, W), (0, 0, 0))
    d = ImageDraw.Draw(im)
    rg = np.random.default_rng(5)
    cols, rows = 4, 8
    cw, rh = W / cols, W / rows
    for i in range(cols):
        for j in range(rows):
            if rg.random() < 0.12:
                continue
            cx, cy = (i + 0.5) * cw, (j + 0.5) * rh
            pts = [(cx + (a - 1) * cw * 0.22, cy + (b - 2) * rh * 0.16) for a in range(3) for b in range(5)]
            n = rg.integers(3, 6)
            idx = sorted(rg.choice(len(pts), n, replace=False), key=lambda k: pts[k][1])
            if rg.random() < 0.8:
                d.line([(cx, cy - rh * 0.32), (cx, cy + rh * 0.32)], fill=(120, 230, 255), width=4)
            for a_, b_ in zip(idx[:-1], idx[1:]):
                d.line([pts[a_], pts[b_]], fill=(120, 230, 255), width=4)
    im2 = im.filter(ImageFilter.GaussianBlur(1.2))
    em = np.asarray(im2, np.float32) / 255.0
    glow = np.asarray(im.filter(ImageFilter.GaussianBlur(7)), np.float32) / 255.0
    em = np.clip(em * 1.2 + glow * 0.7, 0, 1)
    alb = np.clip(0.07 + em * 0.9, 0, 1) * np.array([0.6, 0.9, 1.0], np.float32) * 1.0
    alb = np.maximum(alb, 0.05)
    save('thunder_rune.png', alb)
    save('thunder_rune_e.png', em * np.array([0.5, 0.9, 1.0], np.float32))


def tiles():
    tile_ashlar('thunder_stone', 512, palette=('#2c2a44', '#252339', '#34314f', '#1f1d33'), joint='#09080f', rows=6, block_w=(1.0, 2.0),
                seed=121, wear=0.3, shade=0.1)
    tile_metal('thunder_metal', 512, base='#7f8299', seed=122, rust=0.0, scale_m=2.0, plates=4)
    tile_rock('thunder_rock', 512, '#1e1a2c', '#4a4262', '#7d7399', seed=123, strata=0.6)
    tile_marble('thunder_obsidian', 512, '#1a1730', '#0f0d1c', '#3a3a70', seed=124, strata=0.0, vein_amt=0.5, grain=0.02)
    tile_noise('thunder_cloth', 512, base='#3a2f66', var=0.15, seed=125, scale=1.3, grain=0.05)
    rune_tex()


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
