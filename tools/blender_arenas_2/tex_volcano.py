"""Textures de l'arène « Cratère de Lave » : colonnes de basalte hexagonales (sol), lave tuilable, roche de caldeira, cendres, pierre de ponts."""
import math
import numpy as np
import tex as T
from tex import *

LAVA = [(0.0, hexc('#6a0e06')), (0.3, hexc('#d6360e')), (0.62, hexc('#ff8a1e')), (0.85, hexc('#ffc850')), (1.0, hexc('#fff0b0'))]


def hex_cells(X, Z, R, seed=0, warp=0.0, wscale=0.35):
    """grille hexagonale (sommet à 0°) de circonscrit R, déformée par du bruit. -> (edge_dist m, id 0..1, lx, lz)"""
    if warp:
        Xw = X + (fbm(X * wscale, Z * wscale, 3, seed + 1) - 0.5) * 2 * warp
        Zw = Z + (fbm(X * wscale + 17, Z * wscale + 5, 3, seed + 2) - 0.5) * 2 * warp
    else:
        Xw, Zw = X, Z
    q = (2.0 / 3.0 * Xw) / R
    r = (-1.0 / 3.0 * Xw + math.sqrt(3) / 3.0 * Zw) / R
    # arrondi cubique
    x_, z_ = q, r
    y_ = -x_ - z_
    rx, ry, rz = np.round(x_), np.round(y_), np.round(z_)
    dx, dy, dz = np.abs(rx - x_), np.abs(ry - y_), np.abs(rz - z_)
    fx = (dx > dy) & (dx > dz)
    fy = (~fx) & (dy > dz)
    rx = np.where(fx, -ry - rz, rx)
    rz = np.where(~fx & ~fy, -rx - ry, rz)
    cq, cr = rx, rz
    cx = R * 1.5 * cq
    cz = R * (math.sqrt(3) / 2 * cq + math.sqrt(3) * cr)
    lx, lz = Xw - cx, Zw - cz
    a = R * math.sqrt(3) / 2
    ed = np.full(X.shape, -9.0, np.float32)
    mx = np.zeros(X.shape, np.float32)
    for k in range(3):
        ang = math.radians(30 + 60 * k)
        mx = np.maximum(mx, np.abs(lx * math.cos(ang) + lz * math.sin(ang)))
    ed = (a - mx).astype(np.float32)
    cid = hash01(cq.astype(np.int64), cr.astype(np.int64), seed + 5)
    return ed, cid, lx.astype(np.float32), lz.astype(np.float32), cq, cr


def glyph_flames(cx, cz, r0, r1, n, w=0.22, rot=0.0):
    segs = []
    for k in range(n):
        a = rot + TAU_ * k / n
        p0 = (cx + r0 * math.cos(a - w), cz + r0 * math.sin(a - w))
        p1 = (cx + r1 * math.cos(a), cz + r1 * math.sin(a))
        p2 = (cx + r0 * math.cos(a + w), cz + r0 * math.sin(a + w))
        segs.append((p0[0], p0[1], p1[0], p1[1]))
        segs.append((p1[0], p1[1], p2[0], p2[1]))
    return segs


TAU_ = 2 * math.pi


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    n_big = fbm(X / 6.0, Z / 6.0, 4, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 9, Z * 9, 4, 3)
    n_vfine = fbm(X * 40, Z * 40, 3, 4)
    # --- colonnes de basalte hexagonales
    R = 0.86
    ed, cid, lx, lz, cq, cr = hex_cells(X, Z, R, seed=7, warp=0.25)
    h2 = hash01(cq.astype(np.int64), cr.astype(np.int64), 91)
    h3 = hash01(cq.astype(np.int64), cr.astype(np.int64), 92)
    pal = [hexc('#322a27'), hexc('#3d332e'), hexc('#2a2524'), hexc('#46392f'), hexc('#2b2c32'), hexc('#37302d')]
    pi_ = (cid * len(pal)).astype(int) % len(pal)
    base = np.zeros(X.shape + (3,), np.float32)
    for k, col in enumerate(pal):
        base[pi_ == k] = col
    base = base * (0.78 + 0.5 * h2[..., None]) * (1 + (n_mid[..., None] - 0.5) * 0.28)
    # pente propre à chaque colonne (éclairage cuit : plus clair côté soleil)
    tx, tz = (h2 - 0.5) * 2, (h3 - 0.5) * 2
    slope = (lx * tx + lz * tz) / R
    base = base * (1 + slope[..., None] * 0.20)
    # biseau et bords sombres
    bevel = smooth(0.0, 0.16, ed)
    base = base * (0.62 + 0.44 * bevel[..., None])
    # vésicules / piqûres + grain
    pit = smooth(0.66, 0.78, n_vfine) * 0.45
    base = base * (1 - pit[..., None]) * (1 + (n_fine[..., None] - 0.5) * 0.30)
    # coulées refroidies (reflets plus clairs, striés)
    ripple = 0.5 + 0.5 * np.sin((X * 2.2 + n_mid * 5.0) * 2.0 + Z * 0.5)
    cooled = smooth(0.62, 0.84, fbm(X * 0.5, Z * 0.5, 4, 11)) * 0.5
    base = comp(base, hexc('#4b3f39'), cooled * (0.35 + 0.35 * ripple))
    # --- joints : sombres, avec veines de lave dans les zones chaudes
    seam_w = 0.05
    seam = smooth(seam_w, seam_w * 0.25, ed)
    heat_zone = smooth(0.56, 0.74, fbm(X * 0.26 + 3.0, Z * 0.26, 4, 21))
    heat_zone = np.clip(heat_zone + smooth(2.6, 0.2, depth) * 0.5, 0, 1)   # plus chaud près du bord (rivière de lave dehors)
    flick = 0.45 + 0.55 * smooth(0.3, 0.7, fbm(X * 2.2, Z * 2.2, 3, 23))
    seam_heat = np.clip(heat_zone * flick * 1.1, 0, 1)
    seam_dark = comp(base, hexc('#0d0a0a'), seam * 0.95)
    lava_col = grad(np.clip(0.30 + 0.5 * seam_heat * (0.55 + 0.45 * (ed < seam_w * 0.4)), 0, 0.8), LAVA)
    lav = seam * seam_heat
    img = comp(seam_dark, lava_col, lav)
    # halo orangé sur la pierre voisine des joints chauds
    halo = np.exp(-np.maximum(ed - seam_w, 0) / 0.07) * (ed > 0) * seam_heat
    img = comp(img, hexc('#c8501c'), halo * 0.22)
    em = np.zeros((GH, GW, 3), np.float32)
    em += lava_col * lav[..., None] * 0.95
    em += hexc('#ff5a14') * (halo * 0.10)[..., None]
    # fissures fines dans quelques colonnes
    f1, f2, _ = cell(X * 1.4 + n_mid * 1.4, Z * 1.4 + n_mid * 1.2, 33)
    thin = smooth(0.035, 0.0, f2 - f1) * smooth(0.60, 0.80, fbm(X * 0.4, Z * 0.4, 4, 35)) * smooth(0.04, 0.12, ed)
    img = comp(img, lava_col * 0.8, thin * 0.5 * heat_zone)
    em += lava_col * (thin * 0.38 * heat_zone)[..., None]
    img = img * (1 - thin[..., None] * 0.2 * (1 - heat_zone[..., None]))
    # cendres
    ash = smooth(0.58, 0.84, fbm(X * 0.7, Z * 0.7, 5, 41)) * (0.6 + 0.4 * smooth(2.0, 0.0, depth * 0.5 + 1.0))
    img = comp(img, hexc('#6e6762'), ash * 0.28 * (1 - lav))
    # --- plaques d'obsidienne polie (centre + zones d'équipe) : disques lisses sous les marquages
    hgt = (n_fine * 0.004 + bevel * 0.05 + (h2 - 0.5) * 0.02 + slope * 0.012 - seam * 0.06).astype(np.float32)
    ang = np.arctan2(Z, X)
    Rr = np.hypot(X, Z)
    obs_tex = grad(np.clip(fbm(X * 1.7 + n_mid, Z * 0.9, 5, 51), 0, 1), [(0, hexc('#0f0d0f')), (0.6, hexc('#1c1819')), (1, hexc('#2d2628'))])
    obs_tex = obs_tex * (1 + 0.15 * np.sin((X * 3 - Z * 2) * 1.2 + n_mid * 4))[..., None]
    plate_c = c.circle(0, 0, 9.35, edge=0.03)
    pads = {sg: c.circle(19.0 * sg, 0, 4.1, edge=0.03) for sg in (-1, 1)}
    plates = plate_c
    for sg in (-1, 1):
        plates = np.maximum(plates, pads[sg])
    rimline = np.maximum(c.ring(0, 0, 9.35, 0.10), np.maximum(c.ring(-19.0, 0, 4.1, 0.08), c.ring(19.0, 0, 4.1, 0.08)))
    img = comp(img, obs_tex, plates * 0.96)
    em = em * (1 - plates[..., None] * 0.9)
    img = comp(img, hexc('#0b0909'), rimline * 0.8)
    hgt = hgt * (1 - plates) + (n_fine * 0.002) * plates
    wornm = smooth(0.15, 0.45, fbm(X * 1.1, Z * 1.1, 5, 61)) * 0.45 + 0.55
    gold = hexc('#ffb347')
    # --- sceau central : anneaux dorés, flammes, runes, étoile à 8 branches, cœur de lave
    seal = np.maximum(c.ring(0, 0, 8.7, 0.17), c.ring(0, 0, 8.05, 0.06))
    seal = np.maximum(seal, draw_segs(c, glyph_flames(0, 0, 6.5, 7.6, 16, 0.2, rot=0.0), 0.075))
    seal = np.maximum(seal, c.ring(0, 0, 6.2, 0.07))
    seal = np.maximum(seal, draw_segs(c, rune_segs(0, 0, 5.3, 28, 0.6, seed=12), 0.05))
    seal = np.maximum(seal, c.ring(0, 0, 4.2, 0.12))
    for k in range(8):
        a = k * math.pi / 4
        seal = np.maximum(seal, draw_segs(c, [(1.2 * math.cos(a), 1.2 * math.sin(a), 4.2 * math.cos(a), 4.2 * math.sin(a))], 0.12 if k % 2 == 0 else 0.07))
    star = [(2.7 * math.cos(k * math.pi / 4), 2.7 * math.sin(k * math.pi / 4), 2.7 * math.cos((k + 3) * math.pi / 4), 2.7 * math.sin((k + 3) * math.pi / 4)) for k in range(8)]
    seal = np.maximum(seal, draw_segs(c, star, 0.06))
    seal = np.maximum(seal, c.ring(0, 0, 1.45, 0.08))
    seal = seal * wornm
    core = c.circle(0, 0, 0.95, edge=0.02)
    img = comp(img, gold, seal * 0.92)
    em += seal[..., None] * hexc('#ff9a2a') * 0.9
    core_col = grad(np.clip(1.0 - Rr / 0.95, 0, 1) ** 0.6 * 0.6 + 0.35, LAVA)
    img = comp(img, core_col, core)
    em += core_col * core[..., None] * 1.1
    # --- zones d'équipe : G ember rouge, D acier bleuté
    for sg, colv, ecol in ((-1, hexc('#ff5a2a'), hexc('#ff3a12')), (1, hexc('#9fd4ff'), hexc('#5aaaf0'))):
        cx = 19.0 * sg
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.15), c.ring(cx, 0, 2.7, 0.08))
        z_ = np.maximum(z_, draw_segs(c, glyph_flames(cx, 0, 2.1, 3.0, 8, 0.28, rot=math.pi / 8), 0.07))
        z_ = np.maximum(z_, draw_segs(c, rune_segs(cx, 0, 4.45, 20, 0.45, seed=9 + sg), 0.045))
        z_ = np.maximum(z_, c.ring(cx, 0, 1.0, 0.07))
        z_ = np.maximum(z_, c.dashed(13.0 * sg, -12.5, 13.0 * sg, 12.5, 0.14, 0.9, 0.45))
        z_ = z_ * wornm
        img = comp(img, colv, z_ * 0.88)
        em += z_[..., None] * ecol * (0.72 if sg < 0 else 0.5)
    # --- liseré de chaleur au bord du terrain
    edge_glow = np.exp(-np.maximum(depth, 0) / 0.55)
    img = comp(img, hexc('#d0541c'), edge_glow * 0.18 * smooth(0.35, 0.75, fbm(X * 0.6, Z * 0.6, 3, 71)))
    em += hexc('#ff5a14') * (edge_glow * 0.10)[..., None]
    # --- AO de contact
    ao = c.contact_ao(wall=0.30, wall_len=0.9, obst=0.55, obst_len=0.7)
    img = img * ao[..., None]
    em = em * (0.6 + 0.4 * ao[..., None])
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#120e0d'), under)
        em = em * (1 - under[..., None])
        halo2 = np.exp(-np.maximum(d - r, 0) / 0.55) * (d > r)
        img = comp(img, hexc('#74280f'), halo2 * 0.30)
        em += hexc('#ff4a10') * (halo2 * 0.07)[..., None]
        scorch = c.ring(ox, oz, r + 0.55, 0.06) * wornm
        img = comp(img, hexc('#ff8a3a'), scorch * 0.35)
        em += scorch[..., None] * hexc('#ff6a1e') * 0.3
    em = np.clip(em, 0, 1.5)
    save('volcano_ground.png', img)
    save('volcano_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    save('volcano_ground_e.png', np.clip(em / 1.5, 0, 1))


def tile_lava(name, size=512, seed=21, scale_m=4.0):
    """lave tuilable : croûte sombre fissurée, fleuve strié (flux le long de U), cœurs incandescents."""
    X, Y = tile_coords(size, scale_m)
    p = lambda s: (int(round(scale_m * s)),) * 2
    n = fbm(X * 0.5, Y * 2.0, 4, seed, (2, 8))
    n2 = fbm(X * 1.0, Y * 4.0, 4, seed + 3, (4, 16))
    wx = fbm(X * 0.5, Y * 0.5, 4, seed + 5, (2, 2)) - 0.5
    f1, f2, cid = cell(X * 1.0 + wx * 0.6, Y * 3.0 + (n - 0.5) * 0.9, seed + 9, (4, 12))
    e = f2 - f1
    q = fbm(X * 0.5, Y * 1.5, 4, seed + 14, (2, 6))
    plate = smooth(0.02, 0.11, e)
    plate_on = smooth(0.40, 0.58, q)
    crust_amt = plate * plate_on
    crack = (1 - plate) * plate_on
    heat = np.clip(0.18 + 0.36 * n2 + 0.12 * crack, 0, 1)
    lavac = grad(heat, LAVA)
    crust = grad(np.clip(n * 0.7 + cid * 0.3, 0, 1), [(0, hexc('#170c0a')), (0.55, hexc('#2a1712')), (1, hexc('#40251a'))])
    crust = crust * (0.75 + 0.35 * smooth(0.05, 0.4, e)[..., None])
    # bord de plaque incandescent
    rim = smooth(0.3, 0.06, e) * plate_on * crust_amt
    col = comp(lavac * 0.45, crust, crust_amt)
    col = comp(col, grad(np.full(rim.shape, 0.42, np.float32), LAVA) * 0.45, rim * 0.6)
    emis = lavac * np.clip(1 - crust_amt + rim * 0.55, 0, 1)[..., None]
    h = plate * plate_on * 0.05 + n * 0.02 - crack * 0.03
    save(name + '.png', col)
    save(name + '_e.png', np.clip(emis, 0, 1))
    save(name + '_n.png', to_normal(h, 1.5, scale_m / size, wrap=True))


def tile_hot(name, size=512, seed=31, c0='#1c1716', c1='#33292a', c2='#4d3f3a', scale_m=4.0, density=0.6, glow=1.0):
    """roche fissurée tuilable avec fissures incandescentes (albédo + émissif + normale)."""
    X, Y = tile_coords(size, scale_m)
    n = fbm(X * 1.25, Y * 1.25, 5, seed, (5, 5))
    w = (n - 0.5) * 0.7
    f1, f2, cid = cell(X * 1.75 + w, Y * 1.75 + w, seed + 4, (7, 7))
    e = f2 - f1
    col = grad(np.clip(n * 0.7 + cid * 0.3, 0, 1), [(0, hexc(c0)), (0.5, hexc(c1)), (1, hexc(c2))])
    col = col * (0.72 + 0.4 * smooth(0.0, 0.5, e)[..., None])
    fine = fbm(X * 22, Y * 22, 3, seed + 9, (88, 88))
    col = col * (1 + (fine[..., None] - 0.5) * 0.25)
    region = smooth(1 - density - 0.12, 1 - density + 0.12, fbm(X * 0.75, Y * 0.75, 3, seed + 7, (3, 3)))
    crack = smooth(0.06, 0.0, e) * region
    f1b, f2b, _ = cell(X * 3.5 + w * 2, Y * 3.5 + w * 2, seed + 12, (14, 14))
    thin = smooth(0.05, 0.0, f2b - f1b) * smooth(0.55, 0.8, fbm(X * 1.5, Y * 1.5, 3, seed + 15, (6, 6))) * 0.7
    hot = np.clip(crack + thin * 0.8, 0, 1)
    lavac = grad(np.clip(0.28 + 0.42 * hot * (0.6 + 0.6 * n), 0, 1), LAVA)
    col = comp(col, lavac, hot * 0.9)
    emis = lavac * (hot * glow)[..., None]
    halo = np.exp(-np.maximum(e - 0.0, 0) / 0.06) * region
    col = comp(col, hexc('#8a3a14'), halo * 0.12)
    h = n * 0.08 + smooth(0.0, 0.5, e) * 0.05 - crack * 0.05 - thin * 0.02
    save(name + '.png', col)
    save(name + '_e.png', np.clip(emis, 0, 1))
    save(name + '_n.png', to_normal(h, 1.4, scale_m / size, wrap=True))


def tiles():
    tile_hot('volcano_bank', 512, seed=231, c0='#171313', c1='#2a2322', c2='#40352f', density=0.6, glow=0.85)
    tile_hot('volcano_hot', 512, seed=232, c0='#2a2321', c1='#3c3230', c2='#574a43', density=0.40, glow=0.8)
    tile_rock('volcano_basalt', 512, '#1b1717', '#2d2725', '#4a3f39', seed=185, crack=0.8)
    tile_rock('volcano_rock', 512, '#2c1914', '#6a3a28', '#a86a44', seed=186, strata=0.7, crack=0.6)
    tile_rock('volcano_cliff', 512, '#221615', '#4e2d24', '#7b4a36', seed=187, strata=1.2, crack=0.9)
    tile_ashlar('volcano_stone', 512, palette=('#4d4540', '#40393a', '#585049', '#383232'), joint='#14100f', rows=6, block_w=(1.0, 1.9),
                seed=189, wear=0.5, shade=0.12)
    tile_metal('volcano_iron', 512, base='#6c6a6e', seed=190, rust=0.4, rust_col='#5a2a12', scale_m=2.0, plates=2, rivets=False)
    tile_marble('volcano_obsidian', 512, '#1d1819', '#100d0e', '#4a3a40', seed=191, strata=0.0, vein_amt=0.3, grain=0.02)
    tile_lava('volcano_lava', 512, seed=193)


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
