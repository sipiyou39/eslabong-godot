"""Textures du Mont Olympe : dalles de marbre crème, incrustations d'or, soleil central, zones d'équipe."""
import math
import numpy as np
import tex as T
from tex import *
from tex_greek import *


def ground():
    rng = np.random.default_rng(301)
    c = Canvas()
    X, Z = c.X, c.Z
    img, h, sid, ed = slab_floor(c, 2.65, ('#efe4cc', '#e6dac0', '#f5ecd6', '#dcd0b4', '#ebe1d2', '#e9dcc0'), '#b3a077', '#a8997a', 311, vein_amt=0.5, joint_w=0.022)
    s, dep, tot = c.perim()
    gold = hexc('#d9aa3c')
    dark = hexc('#7c5a24')
    worn = smooth(0.25, 0.6, fbm(X * 1.2 + 4, Z * 1.2, 5, 331)) * 0.35 + 0.65
    # frise le long du mur : bande dorée + damier
    inside, pat = edge_band(c, s, dep, gold, dark, 0.55, 1.0, 0.5)
    img = comp(img, gold, inside * 0.95 * worn)
    img = comp(img, dark, inside * pat * 0.8)
    band2 = smooth(0.1, 0.14, dep) * smooth(0.2, 0.16, dep)
    img = comp(img, gold, band2 * 0.8)
    # médaillon solaire central + éclairs
    emb = sun_emblem(c, rings=((6.0, 0.42), (3.4, 0.24), (6.65, 0.12)))
    img = img * (1 - 0.4 * ndi.gaussian_filter(emb, 2.5)[..., None] * (1 - emb)[..., None])
    img = comp(img, mix(hexc('#e8c25c'), hexc('#c8921f'), smooth(0.45, 0.7, fbm(X * 3, Z * 3, 3, 333)))[...], emb * 0.98)
    # éclairs dorés entre les anneaux
    bolts = np.zeros(X.shape, np.float32)
    for k in range(8):
        a0 = k * math.pi / 4 + math.pi / 8
        pts = [(4.0, a0 - 0.05), (4.5, a0 + 0.07), (5.0, a0 - 0.06), (5.5, a0 + 0.04), (5.95, a0)]
        bolts = draw_segs(c, polar_segs(0, 0, pts), 0.11, out=bolts)
    img = comp(img, hexc('#e8b84a'), bolts * worn * 0.9)
    # zones d'équipe
    img, _ = team_zones(c, img, None, left='#a8303c', right='#2d5fa6', a=0.78, worn=worn)
    # ombre de contact des murs / obstacles
    ao = c.contact_ao(wall=0.2, wall_len=0.8, obst=0.45, obst_len=0.6)
    img = img * ao[..., None]
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#c9bb9a'), under * 0.9)
        ring_ = c.ring(ox, oz, r + 0.35, 0.09) * worn
        img = comp(img, gold, ring_ * 0.85)
    finish_ground('olympus_ground', img, h)


def tiles():
    tile_marble('olympus_marble', 512, c0='#f3ecda', c1='#ded3b9', vein='#a99b7a', seed=201, vein_amt=0.4, grain=0.03)
    tile_ashlar('olympus_stone', 512, palette=('#e4d8ba', '#dacda9', '#ece2c6', '#d0c29d'), joint='#8d7c58', rows=6, block_w=(1.0, 1.8), seed=202, wear=0.22, shade=0.08)
    tile_rock('olympus_rock', 512, c0='#6c6058', c1='#9c8c7a', c2='#cfbea3', seed=203, strata=0.5)
    tile_noise('olympus_cloth', 256, base='#ffffff', var=0.1, seed=205, scale=1.3, grain=0.04)


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['tiles', 'ground']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
