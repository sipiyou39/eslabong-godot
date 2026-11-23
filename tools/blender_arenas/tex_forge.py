"""Textures de la forge volcanique : basalte fissuré, veines de lave (albédo + émissif)."""
import math
import numpy as np
import tex as T
from tex import *


def ground():
    rng = np.random.default_rng(71)
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    n_big = fbm(X / 6.0, Z / 6.0, 4, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 8, Z * 8, 4, 3)
    # --- cellules de basalte
    wx = fbm(X * 0.5, Z * 0.5, 4, 5) * 1.2
    wz = fbm(X * 0.5 + 9, Z * 0.5, 4, 6) * 1.2
    f1, f2, cid = cell(X * 0.5 + wx * 0.8, Z * 0.5 + wz * 0.8, 7)
    e = (f2 - f1)  # en unités de cellule (~1.6 m)
    ee = e / 0.5   # en mètres (approx)
    base = grad(np.clip(cid * 0.7 + n_mid * 0.3, 0, 1), [(0, hexc('#1f1a19')), (0.5, hexc('#2e2623')), (1, hexc('#43372f'))])
    dome = smooth(0.0, 0.6, ee)
    base = base * (0.65 + 0.5 * dome[..., None])
    base = base * (1 + (n_fine[..., None] - 0.5) * 0.35)
    # rouille / cendre
    ash = smooth(0.55, 0.8, fbm(X * 0.8, Z * 0.8, 5, 9))
    base = comp(base, hexc('#4b4440'), ash * 0.35)
    # largeur des veines : plus large au bord du mur et dans certaines zones
    wmod = 0.18 + 1.5 * smooth(0.5, 0.78, fbm(X * 0.3, Z * 0.3, 4, 11))
    wmod = wmod * (1 + 1.2 * smooth(2.6, 0.0, depth))
    vw = 0.06 * wmod  # demi-largeur en mètres
    vein = smooth(vw, vw * 0.25, ee)
    glow_halo = np.exp(-np.maximum(ee - vw, 0) / 0.20) * (ee > 0)
    # intensité de la lave : bande centrale plus chaude
    heat = np.clip(1 - ee / (vw + 1e-4), 0, 1)
    lava = grad(heat ** 0.7, [(0.0, hexc('#9e1c08')), (0.35, hexc('#ff5a14')), (0.75, hexc('#ffa22a')), (1.0, hexc('#ffe9a0'))])
    # fissures secondaires fines
    f1b, f2b, _ = cell(X * 2.3 + wx * 2, Z * 2.3 + wz * 2, 13)
    thin = smooth(0.04, 0.0, f2b - f1b) * smooth(0.62, 0.8, fbm(X * 0.5, Z * 0.5, 4, 15)) * 0.8
    # fleuves de lave : bandes sinueuses larges
    river = np.abs(fbm(X * 0.18 + wx * 0.4, Z * 0.22 + wz * 0.3, 5, 17) - 0.5)
    river_m = smooth(0.012, 0.0, river) * smooth(0.5, 0.0, n_big * 0 + (np.abs(X) - 14.0) * 0.0 + 0.0 - 0.2 + 0.2) * 0
    img = base
    img = comp(img, hexc('#ff6a1a') * 0.55, glow_halo * 0.55 * (1 - vein))
    img = comp(img, lava, np.clip(vein + thin * 0.55, 0, 1))
    emis = np.zeros((GH, GW, 3), np.float32)
    emis += (lava * np.clip(vein + thin * 0.45, 0, 1)[..., None]) * 1.0
    emis += (hexc('#ff4a10') * glow_halo[..., None] * 0.22 * (1 - vein)[..., None])
    hgt = (n_fine * 0.004 + dome * 0.05 - vein * 0.05).astype(np.float32)
    # --- marquages : anneau central en acier forgé + runes ardentes
    steel = grad(np.clip(fbm(X * 3, Z * 3, 4, 21), 0, 1), [(0, hexc('#25262b')), (1, hexc('#4a4c55'))])
    ang = np.arctan2(Z, X)
    R = np.hypot(X, Z)
    plate = c.circle(0, 0, 6.3) * (1 - c.circle(0, 0, 3.2))
    # segments de plaque
    segs = (np.abs(np.sin(ang * 12 + 0.2)) > 0.04)
    plate = plate * segs
    img = comp(img, steel * (0.8 + 0.2 * smooth(0, 0.06, np.abs(R - 6.3))[..., None]), plate)
    inner = c.circle(0, 0, 3.0)
    img = comp(img, hexc('#23201f'), inner * 0.9)
    rune = np.maximum(c.ring(0, 0, 5.6, 0.12), c.ring(0, 0, 3.4, 0.1))
    rune = np.maximum(rune, draw_segs(c, rune_segs(0, 0, 4.5, 28, 0.62, seed=5), 0.06))
    star = np.zeros((GH, GW), np.float32)
    star = np.maximum(star, draw_segs(c, polar_segs(0, 0, [(2.8, k * math.pi / 4 + 0.0) for k in range(0, 9)][:1] + [(0.0, 0)]), 0.05)) * 0
    spokes = []
    for k in range(8):
        a = k * math.pi / 4
        spokes.append((1.0 * math.cos(a), 1.0 * math.sin(a), 2.8 * math.cos(a), 2.8 * math.sin(a)))
    rune = np.maximum(rune, draw_segs(c, spokes, 0.1))
    rune = np.maximum(rune, draw_circles(c, [(0, 0, 0.7)]))
    wornm = smooth(0.2, 0.5, fbm(X * 1.3, Z * 1.3, 5, 31)) * 0.5 + 0.5
    rune = rune * wornm
    img = comp(img, hexc('#ffb040'), rune * 0.9)
    emis += rune[..., None] * hexc('#ff8a22') * 0.95
    # zones d'équipe : anneaux ardents rouge (G) / jaune-blanc (D)
    for sgn, col_ in ((-1, hexc('#ff3a1a')), (1, hexc('#ffc23a'))):
        cx = 19.0 * sgn
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.14), c.ring(cx, 0, 2.6, 0.08))
        sp = [(cx + 0.5 * math.cos(a), 0.5 * math.sin(a), cx + 2.4 * math.cos(a), 2.4 * math.sin(a)) for a in [k * math.pi / 3 for k in range(6)]]
        z_ = np.maximum(z_, draw_segs(c, sp, 0.09))
        z_ = np.maximum(z_, draw_segs(c, rune_segs(cx, 0, 4.5, 16, 0.4, seed=9 + sgn), 0.045))
        z_ = np.maximum(z_, c.dashed(13.0 * sgn, -12.5, 13.0 * sgn, 12.5, 0.13, 0.9, 0.45))
        z_ = z_ * wornm
        img = comp(img, col_, z_ * 0.85)
        emis += z_[..., None] * col_ * 0.8
        # plaque d'acier sombre sous le pad
        img = comp(img, hexc('#2a2a30'), c.circle(cx, 0, 3.7) * 0.5 * (1 - z_))
    # --- AO de contact
    ao = c.contact_ao(wall=0.25, wall_len=0.8, obst=0.5, obst_len=0.6)
    img = img * (0.35 + 0.65 * ao[..., None]) ** 1 if False else img * ao[..., None]
    emis = emis * (0.55 + 0.45 * ao[..., None])
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#161212'), under)
        emis = emis * (1 - under[..., None])
        # lueur tout autour des piliers (pierre chauffée)
        halo = np.exp(-np.maximum(d - r, 0) / 0.5) * (d > r)
        img = comp(img, hexc('#6a2410'), halo * 0.35)
    emis = np.clip(emis, 0, 1.5)
    save('forge_ground.png', img)
    save('forge_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    save('forge_ground_e.png', np.clip(emis / 1.5 * 1.0, 0, 1))


def tiles():
    tile_ashlar('forge_stone', 512, palette=('#4a403b', '#3d3430', '#554a43', '#352d2a'), joint='#120e0d', rows=6, block_w=(1.0, 1.9),
                seed=81, wear=0.45, shade=0.12)
    tile_metal('forge_metal', 512, base='#8a8a92', seed=82, rust=0.55, rust_col='#6a2f14', scale_m=2.0, plates=4)
    tile_metal('forge_iron', 512, base='#76767e', seed=83, rust=0.25, rust_col='#5a2a12', scale_m=2.0, plates=2, rivets=False)
    tile_rock('forge_rock', 512, '#3a1d18', '#7a3626', '#b9663f', seed=84, strata=0.5)
    tile_rock('forge_basalt', 512, '#1c1819', '#2f2926', '#4a403a', seed=85, crack=0.7)
    tile_noise('forge_cloth', 512, base='#6b4a32', var=0.2, seed=86, scale=1.4, grain=0.07, tint2='#3a2a20')
    tile_wood('forge_wood', 512, '#23190f', '#54381f', seed=87)
    tile_noise('forge_soot', 512, base='#24201e', var=0.25, seed=88, scale=1.2, grain=0.1, tint2='#3a2a22')


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
