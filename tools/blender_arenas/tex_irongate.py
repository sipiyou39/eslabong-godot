"""Textures de la Porte de fer : pavés usés, boue, ornières, marquages à la craie."""
import math
import numpy as np
import tex as T
from tex import *


def ground():
    rng = np.random.default_rng(91)
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    n_big = fbm(X / 6.0, Z / 6.0, 4, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 9, Z * 9, 4, 3)
    # --- pavés
    wx = fbm(X * 1.2, Z * 1.2, 3, 5) * 0.6
    wz = fbm(X * 1.2 + 5, Z * 1.2, 3, 6) * 0.6
    row = np.floor(Z * 1.5)
    f1, f2, cid = cell(X * 1.5 + 0.5 * (row % 2) + wx, Z * 1.5 + wz, 7)
    e = (f2 - f1) / 1.5
    pal = grad(cid, [(0, hexc('#6c675f')), (0.35, hexc('#85806f')), (0.7, hexc('#6f6a62')), (1, hexc('#97907c'))])
    dome = smooth(0.0, 0.24, e)
    img = pal * (0.62 + 0.5 * dome[..., None]) * (1 + (n_fine[..., None] - 0.5) * 0.3)
    gap = smooth(0.045, 0.012, e)
    img = comp(img, hexc('#2e261d'), gap * 0.95)
    hgt = (dome * 0.05 - gap * 0.03 + n_fine * 0.004).astype(np.float32)
    # --- dalles de la voie vers la porte (+X)
    SX = 1.9
    rowv = np.floor((Z + 6.0) / SX)
    colv = np.floor((X + 0.5 * SX * (rowv % 2)) / SX)
    u = (X + 0.5 * SX * (rowv % 2)) / SX - colv
    v = (Z + 6.0) / SX - rowv
    sid = hash01(colv.astype(np.int64), rowv.astype(np.int64), 3)
    ed = np.minimum(np.minimum(u * SX, (1 - u) * SX), np.minimum(v * SX, (1 - v) * SX))
    slab = grad(np.clip(sid * 0.6 + n_mid * 0.4, 0, 1), [(0, hexc('#6a655b')), (0.5, hexc('#7d786a')), (1, hexc('#928b7a'))])
    slab = slab * (1 + (n_fine[..., None] - 0.5) * 0.2)
    sj = smooth(0.04, 0.012, ed)
    slab = comp(slab, hexc('#2a231b'), sj * 0.9)
    road = smooth(5.8, 4.6, np.abs(Z)) * smooth(4.0, 9.0, X) * (1 - 0.0)
    road = np.clip(road + smooth(5.5, 4.4, np.abs(Z)) * smooth(-30, -22, X) * 0.0, 0, 1)
    img = comp(img, slab, road)
    hgt = hgt * (1 - road) + road * (smooth(0.0, 0.05, ed) * 0.04 - sj * 0.02 + n_fine * 0.003)
    # plaques de fer encastrées devant la porte
    plates = np.zeros((GH, GW), np.float32)
    for k in range(3):
        zc = (k - 1) * 3.0
        x0 = 21.0
        plates = np.maximum(plates, smooth(0.03, 0.0, np.maximum(np.abs(X - (x0 + 1.9)) - 1.8, np.abs(Z - zc) - 1.3)) * 1.0)
    ironc = grad(np.clip(fbm(X * 3, Z * 3, 4, 21), 0, 1), [(0, hexc('#2a2b30')), (1, hexc('#3d3f47'))])
    img = comp(img, ironc, plates * 0.95)
    for k in range(3):
        for dx in (-1.5, 1.5):
            for dz in (-1.0, 1.0):
                pass
    # --- boue + ornières
    mud_n = fbm(X * 0.6 + 3, Z * 0.6, 5, 11)
    mud = smooth(0.58, 0.72, mud_n) * (1 - road * 0.8)
    mudc = grad(np.clip(fbm(X * 3, Z * 3, 4, 12), 0, 1), [(0, hexc('#3a2d20')), (1, hexc('#5c4730'))])
    img = comp(img, mudc, mud * 0.9)
    # flaques (reflet bleuté)
    pud = smooth(0.74, 0.8, mud_n) * (1 - road)
    img = comp(img, hexc('#4a5560'), pud * 0.75)
    hgt = hgt - mud * 0.02
    # ornières de charrettes vers la porte
    wob = fbm(X * 0.4, Z * 0.4, 3, 13) * 0.9
    ruts = np.zeros((GH, GW), np.float32)
    for off in (-0.95, 0.95):
        ruts = np.maximum(ruts, smooth(0.28, 0.06, np.abs(Z - off - wob + 0.45 + 0.25 * np.sin(X * 0.2)))) 
    ruts = ruts * smooth(-22, -10, X) * (1 - 0.0) * (0.5 + 0.5 * smooth(0.3, 0.6, fbm(X * 0.8, Z * 0.8, 4, 14)))
    img = comp(img, mudc * 0.8, ruts * 0.7)
    hgt = hgt - ruts * 0.025
    # taches de brûlure / suie
    scorch = smooth(0.62, 0.8, fbm(X * 0.5 + 8, Z * 0.5, 5, 15))
    img = img * (1 - 0.55 * scorch[..., None])
    for (bx, bz, br) in ((-4, 2.5, 2.2), (6, -9, 1.7), (-14, -8, 1.9), (13, 10, 1.4)):
        d = np.hypot(X - bx, Z - bz) / br
        img = img * (1 - 0.65 * smooth(1.0, 0.0, d + (n_mid - 0.5) * 0.8)[..., None])
    # mousse près des murs
    moss = smooth(1.4, 0.0, depth - (n_mid - 0.5) * 2.0) * smooth(0.45, 0.65, fbm(X * 1.4, Z * 1.4, 4, 16))
    img = comp(img, hexc('#4e6a2e'), moss * 0.6)
    # --- marquages
    chalk = hexc('#ece4cc')
    teamL = hexc('#b4552c')
    teamR = hexc('#4f78a8')
    wornm = smooth(0.3, 0.6, fbm(X * 1.3, Z * 1.3, 5, 31)) * 0.65 + 0.35
    # sigle central : anneau de pierre + herse
    ring = np.maximum(c.ring(0, 0, 5.8, 0.28), c.ring(0, 0, 3.6, 0.14))
    ring = np.maximum(ring, draw_segs(c, ring_segs(0, 0, 4.7, 96), 0.06))
    arch = []
    for i in range(24):
        a0 = math.pi * i / 24
        a1 = math.pi * (i + 1) / 24
        arch.append((2.2 * math.cos(a0), -0.4 - 2.2 * math.sin(a0), 2.2 * math.cos(a1), -0.4 - 2.2 * math.sin(a1)))
    arch += [(2.2, -0.4, 2.2, 2.3), (-2.2, -0.4, -2.2, 2.3), (-2.2, 2.3, 2.2, 2.3)]
    bars = [(x_, -2.4, x_, 2.3) for x_ in np.linspace(-1.8, 1.8, 7)] + [(-2.2, y_, 2.2, y_) for y_ in (-1.0, 0.2, 1.4)]
    emb = np.maximum(ring, draw_segs(c, arch, 0.14))
    emb = np.maximum(emb, draw_segs(c, bars, 0.06))
    img = comp(img, chalk, emb * wornm * 0.8)
    img = comp(img, hexc('#2b2b30'), draw_circles(c, [(0, 0, 0.0001)]))
    # zones : cercles + lignes de défense
    for sgn, col_ in ((-1, teamL), (1, teamR)):
        cx = 19.0 * sgn
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.16), c.ring(cx, 0, 2.7, 0.09))
        z_ = np.maximum(z_, draw_segs(c, [(cx - 2, 0, cx + 2, 0), (cx, -2, cx, 2)], 0.1))
        z_ = np.maximum(z_, c.dashed(13.0 * sgn, -12.5, 13.0 * sgn, 12.5, 0.15, 0.9, 0.45))
        img = comp(img, col_, z_ * wornm * 0.8)
    # arc de défense devant la porte
    arcm = np.zeros((GH, GW), np.float32)
    arcm = np.maximum(arcm, c.ring(26.0, 0.0, 8.0, 0.18) * (X < 26.0))
    img = comp(img, chalk, arcm * wornm * 0.7)
    # --- AO de contact + pile
    ao = c.contact_ao(wall=0.30, wall_len=0.8, obst=0.55, obst_len=0.65)
    img = img * ao[..., None]
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        img = comp(img, hexc('#3d362e'), smooth(r + 0.05, r - 0.1, d))
        ring_m = smooth(r + 1.3, r + 0.2, d) * (d > r)
        img = comp(img, mudc, ring_m * 0.35 * smooth(0.3, 0.6, fbm(X * 3, Z * 3, 3, 41)))
    save('irongate_ground.png', img)
    save('irongate_ground_n.png', to_normal(down(hgt, 2), 3.5, MPP * 2))


def tiles():
    tile_ashlar('irongate_stone', 512, palette=('#8a8478', '#7c776c', '#979182', '#6f6b62'), joint='#25211b', rows=5, block_w=(1.1, 2.2),
                seed=101, wear=0.5, shade=0.14, moss='#52702f')
    tile_ashlar('irongate_stone_dark', 512, palette=('#625e57', '#575350', '#6c6760', '#4d4a46'), joint='#1c1916', rows=6, block_w=(0.9, 1.8),
                seed=102, wear=0.45, shade=0.12)
    tile_metal('irongate_iron', 512, base='#8d8f99', seed=103, rust=0.3, rust_col='#5b3a1e', scale_m=2.0, plates=3)
    tile_wood('irongate_wood', 512, '#2c2015', '#5e4630', seed=104)
    tile_rock('irongate_rock', 512, '#3f3d3d', '#6b6867', '#8d8a85', seed=105)
    tile_noise('irongate_cloth', 512, base='#4a5568', var=0.18, seed=106, scale=1.4, grain=0.07)
    tile_noise('irongate_mud', 512, base='#4a3a28', var=0.25, seed=107, scale=1.3, grain=0.1, tint2='#2e2418')
    tile_noise('irongate_sand', 512, base='#a08c62', var=0.22, seed=108, scale=3.5, grain=0.12, tint2='#7a6a48')


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
