"""Textures de la salle du club : sol de dalles chaudes + tapis, carte stratégique, rayons de lumière."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import tex as T
from tex import *

CW, CH = 2048, 1472
CX0, CX1 = -14.0, 14.0
CMPP = (CX1 - CX0) / CW
CZ0 = -(CH * CMPP) / 2
CZ1 = (CH * CMPP) / 2


class FloorCanvas(Canvas):
    def __init__(self):
        cols = (np.arange(CW) + 0.5) * CMPP + CX0
        rows = (np.arange(CH) + 0.5) * CMPP + CZ0
        self.X, self.Z = np.meshgrid(cols.astype(np.float32), rows.astype(np.float32))
        self.W, self.H = CW, CH


def _seg_mask(c, segs, w, edge=0.012):
    out = np.zeros(c.X.shape, np.float32)
    for (x0, z0, x1, z1) in segs:
        dx, dz = x1 - x0, z1 - z0
        L2 = dx * dx + dz * dz + 1e-9
        j0 = int(max(0, (min(x0, x1) - w - CX0) / CMPP - 3)); j1 = int(min(CW, (max(x0, x1) + w - CX0) / CMPP + 4))
        i0 = int(max(0, (min(z0, z1) - w - CZ0) / CMPP - 3)); i1 = int(min(CH, (max(z0, z1) + w - CZ0) / CMPP + 4))
        if i1 <= i0 or j1 <= j0:
            continue
        X = c_X[i0:i1, j0:j1]; Z = c_Z[i0:i1, j0:j1]
        t = np.clip(((X - x0) * dx + (Z - z0) * dz) / L2, 0, 1)
        d = np.hypot(X - (x0 + t * dx), Z - (z0 + t * dz))
        out[i0:i1, j0:j1] = np.maximum(out[i0:i1, j0:j1], smooth(w / 2 + edge, w / 2 - edge, d))
    return out


def floor():
    global c_X, c_Z
    rng = np.random.default_rng(131)
    c = FloorCanvas()
    c_X, c_Z = c.X, c.Z
    X, Z = c.X, c.Z
    n_big = fbm(X / 5.0, Z / 5.0, 4, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 8, Z * 8, 4, 3)
    # dalles en appareil décalé 1.5 x 0.95
    SX, SZ = 1.5, 0.95
    row = np.floor((Z + 11.0) / SZ)
    off = hash01(row.astype(np.int64), row.astype(np.int64) * 0 + 4, 7) * SX
    col = np.floor((X + 15.0 + off) / SX)
    u = (X + 15.0 + off) / SX - col
    v = (Z + 11.0) / SZ - row
    sid = hash01(col.astype(np.int64), row.astype(np.int64), 3)
    ed = np.minimum(np.minimum(u * SX, (1 - u) * SX), np.minimum(v * SZ, (1 - v) * SZ))
    img = grad(np.clip(sid * 0.65 + n_big * 0.35, 0, 1), [(0, hexc('#8c6c4c')), (0.35, hexc('#a98660')), (0.7, hexc('#c0a077')), (1, hexc('#d2b890'))])
    img = img * (1 + (n_fine[..., None] - 0.5) * 0.22) * (1 + (n_mid[..., None] - 0.5) * 0.18)
    bevel = smooth(0.0, 0.1, ed)
    img = img * (0.8 + 0.25 * bevel[..., None])
    joint = smooth(0.032, 0.01, ed)
    img = comp(img, hexc('#3a2a1c'), joint * 0.9)
    hgt = (bevel * 0.015 - joint * 0.015 + n_fine * 0.003).astype(np.float32)
    # usure : allées sombres, fissures
    wear = smooth(0.6, 0.8, fbm(X * 0.6, Z * 0.6, 4, 9)) * 0.25
    img = img * (1 - wear[..., None])
    # tapis rond sous la table + tapis rectangulaire vers l'entrée
    red = hexc('#8c1f26')
    gold = hexc('#d4a53a')
    dark = hexc('#4a1015')
    rd = np.hypot(X, Z)
    carpet = smooth(4.95, 4.85, rd)
    # tapis long (entrée -> table)
    runner = smooth(1.75, 1.65, np.abs(X)) * smooth(-10.2, -9.9, Z) * smooth(2.0, 1.4, Z)
    carpet = np.maximum(carpet, runner)
    weave = 0.5 + 0.5 * np.sin(X * 90) * np.sin(Z * 90)
    pat = grad(np.clip(fbm(X * 3, Z * 3, 3, 12), 0, 1), [(0, red * 0.85), (1, red * 1.1)])
    cmask = carpet
    img = comp(img, pat * (0.92 + 0.08 * weave[..., None]), cmask)
    # bordures dorées + motifs
    bd1 = np.maximum(c.ring(0, 0, 4.7, 0.12), c.ring(0, 0, 3.9, 0.06))
    bd2 = np.maximum(c.ring(0, 0, 4.4, 0.04), c.ring(0, 0, 2.6, 0.05))
    star = _seg_mask(c, [(2.5 * math.cos(k * math.pi / 4), 2.5 * math.sin(k * math.pi / 4), 4.3 * math.cos(k * math.pi / 4), 4.3 * math.sin(k * math.pi / 4)) for k in range(8)], 0.1)
    edge_run = smooth(0.12, 0.06, np.abs(np.abs(X) - 1.5)) * smooth(-10.1, -9.8, Z) * smooth(1.9, 1.3, Z) * (np.abs(X) < 1.7)
    img = comp(img, gold, np.maximum(np.maximum(bd1, bd2), np.maximum(star * 0.9, edge_run)) * 0.9)
    img = comp(img, dark, smooth(0.04, 0.0, np.abs(rd - 4.95)) * 0.5)
    # franges du tapis long
    for k in range(40):
        zz = -10.0 + k * 0.01
    # blason central (cercle sous la table)
    crest = np.maximum(c.ring(0, 0, 1.4, 0.1), c.circle(0, 0, 0.35))
    img = comp(img, gold, crest * 0.85)
    # foyer : pierre noircie devant la cheminée (z ~ +8.5..+10)
    hearth = smooth(4.2, 3.6, np.abs(X)) * smooth(7.7, 8.2, Z)
    img = comp(img, hexc('#3b3027'), hearth * 0.75 * (0.7 + 0.3 * n_mid))
    soot = np.exp(-((X / 3.0) ** 2 + ((Z - 9.5) / 2.5) ** 2))
    img = img * (1 - 0.35 * soot[..., None])
    # zones de lumière des fenêtres (taches chaudes) : parallélogrammes doux
    lightp = np.zeros_like(X)
    for (wx, wz) in ((-14, -6.0), (-14, -0.5), (-14, 5.0), (14, -6.0), (14, -0.5), (14, 5.0), (-5.0, 10), (5.0, 10)):
        if abs(wx) > 10:
            cx_ = wx - np.sign(wx) * 5.2
            cz_ = wz + 2.0
            lightp = np.maximum(lightp, smooth(1.4, 0.3, np.hypot((X - cx_) * 0.55, (Z - cz_) * 0.9)))
        else:
            cx_ = wx + 1.5
            cz_ = wz - 4.0
            lightp = np.maximum(lightp, smooth(1.5, 0.3, np.hypot((X - cx_) * 0.8, (Z - cz_) * 0.55)))
    img = img * (1 + 0.28 * lightp[..., None] * np.array([1.0, 0.92, 0.75]))
    save('club_floor.png', img)
    save('club_floor_n.png', to_normal(down(hgt, 2), 3.0, CMPP * 2))


def mapimg():
    W, H = 1024, 512
    rg = np.random.default_rng(7)
    xs = np.arange(W)[None, :] / 100.0
    ys = np.arange(H)[:, None] / 100.0
    X = np.broadcast_to(xs, (H, W)).astype(np.float32)
    Y = np.broadcast_to(ys, (H, W)).astype(np.float32)
    land = fbm(X * 0.7, Y * 0.7, 6, 5)
    land = land - 0.25 * (np.hypot((X - 5.1) / 5.1, (Y - 2.55) / 2.55)) ** 2
    pap = grad(np.clip(fbm(X * 3, Y * 3, 5, 3), 0, 1), [(0, hexc('#c9a870')), (1, hexc('#e6cf9c'))])
    sea = np.array(hexc('#7fa3a8'))
    coast = smooth(0.5, 0.52, land)
    img = pap.copy()
    img = comp(img, sea * 0.85 + 0.15 * pap, 1 - coast)
    # contour de côte
    cl = smooth(0.012, 0.0, np.abs(land - 0.51))
    img = comp(img, hexc('#4a3520'), cl * 0.85)
    # reliefs (collines)
    hill = smooth(0.62, 0.78, land)
    img = comp(img, hexc('#9a7a4a'), hill * 0.35)
    forest = smooth(0.55, 0.62, land) * smooth(0.45, 0.65, fbm(X * 2, Y * 2, 4, 9)) * (1 - hill)
    img = comp(img, hexc('#6e7a46'), forest * 0.4)
    # rivières
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    for k in range(5):
        x, y = rg.uniform(1, 9), rg.uniform(0.5, 4.5)
        pts = []
        for s in range(30):
            x += rg.normal(0.12, 0.12)
            y += rg.normal(0.08, 0.12)
            pts.append((x * 100, y * 100))
        d.line(pts, fill=(80, 120, 140), width=3)
    # routes pointillées + villes
    towns = []
    tries = 0
    while len(towns) < 9 and tries < 500:
        tries += 1
        tx, ty = rg.uniform(1, 9.2), rg.uniform(0.6, 4.4)
        if land[int(ty * 100), int(tx * 100)] > 0.56:
            towns.append((tx, ty))
    towns = sorted(towns, key=lambda t: t[0])
    for i in range(len(towns) - 1):
        a, b = towns[i], towns[i + 1]
        n = 20
        for s in range(0, n, 2):
            t0, t1 = s / n, (s + 1) / n
            d.line([(a[0] * 100 + (b[0] - a[0]) * 100 * t0, a[1] * 100 + (b[1] - a[1]) * 100 * t0), (a[0] * 100 + (b[0] - a[0]) * 100 * t1, a[1] * 100 + (b[1] - a[1]) * 100 * t1)], fill=(110, 50, 30), width=2)
    for (x, y) in towns:
        d.ellipse([x * 100 - 7, y * 100 - 7, x * 100 + 7, y * 100 + 7], fill=(150, 40, 35), outline=(60, 25, 15), width=2)
        d.rectangle([x * 100 - 3, y * 100 - 3, x * 100 + 3, y * 100 + 3], fill=(235, 210, 150))
    # rose des vents
    cx, cy = 900, 400
    d.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], outline=(70, 40, 25), width=3)
    for a in range(8):
        ang = a * math.pi / 4
        L = 60 if a % 2 == 0 else 36
        d.line([(cx, cy), (cx + L * math.sin(ang), cy - L * math.cos(ang))], fill=(70, 40, 25), width=3 if a % 2 == 0 else 2)
    d.polygon([(cx, cy - 66), (cx - 8, cy - 48), (cx + 8, cy - 48)], fill=(150, 40, 35))
    # cadre
    d.rectangle([6, 6, W - 7, H - 7], outline=(80, 50, 30), width=6)
    d.rectangle([16, 16, W - 17, H - 17], outline=(150, 110, 60), width=2)
    arr = np.asarray(pil.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255.0
    # vieillissement : bords foncés
    yy, xx = np.mgrid[0:H, 0:W]
    edge = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)) / 60.0
    arr = arr * (0.75 + 0.25 * np.clip(edge, 0, 1))[..., None]
    save('club_map.png', arr)


def rays():
    W, H = 128, 256
    xx = np.linspace(-1, 1, W)[None, :]
    yy = np.linspace(0, 1, H)[:, None]
    a = (1 - yy) ** 1.4 * smooth(1.0, 0.15, np.abs(xx)) * 0.3
    a = a * (0.8 + 0.2 * np.sin(xx * 9 + yy * 3)) 
    rgba = np.zeros((H, W, 4), np.float32)
    rgba[..., 0] = 1.0
    rgba[..., 1] = 0.9
    rgba[..., 2] = 0.65
    rgba[..., 3] = np.clip(a, 0, 1)
    arr = (rgba * 255).astype(np.uint8)
    Image.fromarray(arr, 'RGBA').save(os.path.join(TEXDIR, 'club_ray.png'), optimize=True)
    print('texture club_ray.png')


import os


def tiles():
    tile_ashlar('club_stone', 512, palette=('#b99b75', '#aa8c68', '#c7a982', '#a08262'), joint='#4a3724', rows=6, block_w=(0.9, 1.7), seed=141, wear=0.4, shade=0.1)
    tile_wood('club_wood', 512, '#2e1d11', '#6a4426', seed=142)
    tile_wood('club_wood_light', 512, '#5a3a1f', '#a47a45', seed=143, planks=5)
    tile_metal('club_iron', 512, base='#8a8a92', seed=144, rust=0.2, rust_col='#5a3a1e', scale_m=2.0, plates=4, rivets=False)
    tile_noise('club_cloth', 512, base='#8c1f26', var=0.18, seed=145, scale=1.4, grain=0.07, tint2='#a8342a')
    tile_noise('club_burlap', 512, base='#a08a5c', var=0.2, seed=146, scale=3.5, grain=0.12, tint2='#7a6a44')
    tile_noise('club_plaster', 512, base='#c8b08a', var=0.14, seed=147, scale=1.2, grain=0.05)
    tile_rock('club_rock', 512, '#6a5a48', '#9a8466', '#c0a888', seed=148)
    tile_marble('club_marble', 512, '#d8c8a8', '#bfa985', '#8a7552', seed=149, strata=0.4)


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['floor', 'map', 'rays', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'map' in what:
        mapimg()
    if 'rays' in what:
        rays()
    if 'floor' in what:
        floor()
