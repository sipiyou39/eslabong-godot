"""Textures de l'Atlantide : marbre perle bleuté, caustiques, trident incrusté, corail, sable, rayons de lumière."""
import math
import numpy as np
from PIL import Image
import tex as T
from tex import *
from tex_greek import *


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    img, h, sid, ed = slab_floor(c, 2.65, ('#cfe6e2', '#c3dcda', '#d9eee9', '#bcd5d4', '#d2e4e6'), '#4d8088', '#6fa6a8', 511, vein_amt=0.45, joint_w=0.024, wear=0.4)
    s, dep, tot = c.perim()
    gold = hexc('#e0b44a')
    teal = hexc('#2e8a9a')
    worn = smooth(0.25, 0.6, fbm(X * 1.2 + 4, Z * 1.2, 5, 531)) * 0.35 + 0.65
    # frise de vagues dorées / turquoise le long du mur
    inside, pat = edge_band(c, s, dep, gold, teal, 0.55, 1.0, 0.5)
    img = comp(img, gold, inside * 0.95 * worn)
    img = comp(img, teal, inside * pat * 0.85)
    # coraux incrustés au pied du mur (taches roses)
    cor = smooth(0.58, 0.78, fbm(X * 1.8, Z * 1.8, 4, 533)) * smooth(0.9, 0.2, dep) * 0.8
    img = comp(img, hexc('#e8738a'), cor * 0.55)
    # médaillon : anneaux + trident (pointe vers le nord = -z) + vagues
    emb = np.zeros(X.shape, np.float32)
    for r_, w_ in ((6.0, 0.36), (3.6, 0.18), (6.7, 0.1)):
        emb = np.maximum(emb, c.ring(0, 0, r_, w_))
    segs = []
    segs.append((0, 2.8, 0, -3.1))
    segs.append((0, -3.1, 0, -4.6))
    segs += [(0.0, -3.1, 0.38, -3.9), (0.38, -3.9, 0.0, -4.6), (0.0, -3.1, -0.38, -3.9), (-0.38, -3.9, 0.0, -4.6)]
    for sx in (-1, 1):
        pts = [(0, -1.4), (sx * 0.75, -1.5), (sx * 1.3, -2.1), (sx * 1.5, -3.0), (sx * 1.45, -3.9)]
        segs += [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(len(pts) - 1)]
        segs += [(sx * 1.45, -3.9, sx * 1.1, -3.4), (sx * 1.45, -3.9, sx * 1.85, -3.4), (sx * 1.45, -3.9, sx * 1.45, -4.5)]
    segs += [(-0.7, 2.5, 0.7, 2.5), (-0.5, 2.2, 0.5, 2.2)]
    emb = draw_segs(c, segs, 0.2, out=emb)
    wave = []
    for k in range(120):
        a0 = 2 * math.pi * k / 120
        a1 = 2 * math.pi * (k + 1) / 120
        r0 = 4.7 + 0.2 * math.sin(a0 * 14)
        r1 = 4.7 + 0.2 * math.sin(a1 * 14)
        wave.append((r0 * math.cos(a0), r0 * math.sin(a0), r1 * math.cos(a1), r1 * math.sin(a1)))
    emb = draw_segs(c, wave, 0.1, out=emb)
    emb = np.maximum(emb, c.circle(0, 2.9, 0.35))
    img = img * (1 - 0.15 * ndi.gaussian_filter(emb, 3)[..., None] * (1 - emb)[..., None])
    img = comp(img, mix(hexc('#f2dc8c'), gold, smooth(0.45, 0.7, fbm(X * 3, Z * 3, 3, 535))), emb * worn * 0.96)
    # zones d'équipe : corail (gauche) / océan (droite)
    img, _ = team_zones(c, img, None, left='#d84a6a', right='#2a62c4', a=0.78, worn=worn)
    # caustiques : réseau lumineux doux (deux couches)
    n1 = fbm(X * 0.4, Z * 0.4, 3, 541)
    f1, f2, _ = cell(X * 0.55 + n1 * 1.2, Z * 0.55 + n1 * 1.2, 543)
    f1b, f2b, _ = cell(X * 0.8 - n1 * 1.0 + 7, Z * 0.8 - n1 * 1.0, 545)
    caus = np.clip(smooth(0.2, 0.0, f2 - f1) + 0.7 * smooth(0.18, 0.0, f2b - f1b), 0, 1) * (0.45 + 0.55 * smooth(0.3, 0.8, fbm(X * 0.3, Z * 0.3, 3, 547)))
    img = img * (1 - 0.06) + caus[..., None] * hexc('#dffff6') * 0.22
    ao = c.contact_ao(wall=0.2, wall_len=0.8, obst=0.45, obst_len=0.6)
    img = img * ao[..., None]
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#e8a09a'), under * 0.85)
        ring_ = c.ring(ox, oz, r + 0.35, 0.09) * worn
        img = comp(img, gold, ring_ * 0.85)
    finish_ground('atlantis_ground', img, h)


def coral():
    size = 512
    X, Y = tile_coords(size, 2.0)
    n = fbm(X * 1.5, Y * 1.5, 4, 561, (3, 3))
    f1, f2, cid = cell(X * 6.0 + n * 1.2, Y * 6.0 + n * 1.2, 563, (12, 12))
    e = f2 - f1
    dome = smooth(0.0, 0.5, e)
    col = grad(np.clip(cid * 0.7 + n * 0.3, 0, 1), [(0, hexc('#d9566a')), (0.5, hexc('#ee8470')), (1, hexc('#f5b585'))])
    col = col * (0.55 + 0.55 * dome[..., None])
    pores = smooth(0.08, 0.02, f1) * 0.35
    col = col * (1 - pores[..., None])
    save('atlantis_coral.png', col)
    save('atlantis_coral_n.png', to_normal(dome * 0.05 + n * 0.01, 2.0, 2.0 / size, wrap=True))


def ray():
    W, H = 128, 512
    x = np.linspace(-1, 1, W)[None, :]
    y = np.linspace(0, 1, H)[:, None]
    a = np.exp(-(x * 1.6) ** 2 * 2.2) * (1 - y) ** 1.1 * (0.55 + 0.45 * np.sin(y * 9 + x * 3) ** 2)
    a = np.clip(a * 0.55, 0, 1)
    rgb = np.zeros((H, W, 3), np.float32)
    rgb[...] = np.array([0.72, 1.0, 0.95], np.float32)
    rgba = np.concatenate([rgb, a[..., None].astype(np.float32)], -1)
    Image.fromarray((np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(TEXDIR + '/atlantis_ray.png', optimize=True)
    print('texture atlantis_ray.png')


def tiles():
    tile_marble('atlantis_marble', 512, c0='#e4f1ee', c1='#c4dedb', vein='#7eaeb0', seed=501, vein_amt=0.4, grain=0.03)
    tile_ashlar('atlantis_stone', 512, palette=('#cde2df', '#c0d8d6', '#d6e8e4', '#b8d0d0'), joint='#4d7c84', rows=6, block_w=(1.0, 1.8), seed=502, wear=0.3, shade=0.08)
    tile_rock('atlantis_rock', 512, c0='#2f4c55', c1='#58808a', c2='#92b8bc', seed=503, strata=0.4)
    tile_noise('atlantis_sand', 512, base='#d9cfae', var=0.12, seed=504, scale=1.4, grain=0.06, tint2='#b9b496')
    tile_noise('atlantis_cloth', 256, base='#ffffff', var=0.1, seed=505, scale=1.3, grain=0.04)
    coral()
    ray()


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['tiles', 'ground']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
