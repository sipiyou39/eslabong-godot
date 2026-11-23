"""Textures des Enfers : dalles de basalte, fissures de braise, sceau runique vert-bleuté, fleuve Styx, bronze patiné."""
import math
import numpy as np
import tex as T
from tex import *
from tex_greek import *


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    img, h, sid, ed = slab_floor(c, 2.65, ('#2a2530', '#221e28', '#302a36', '#1d1a22', '#27212c'), '#07060a', '#5a3548', 411, vein_amt=0.55, joint_w=0.03, bevel_amt=0.3, tone=1.0,
                                 wear=0.5)
    em = np.zeros(X.shape + (3,), np.float32)
    ember = hexc('#ff6a28')
    teal = hexc('#52ffc4')
    # fissures de braise : arêtes de cellules, filtrées par du bruit
    n_mid = fbm(X * 0.5, Z * 0.5, 4, 413)
    f1, f2, cid = cell(X * 0.38 + n_mid * 0.9, Z * 0.38 + n_mid * 0.9, 417)
    crack = smooth(0.045, 0.0, f2 - f1) * smooth(0.5, 0.72, fbm(X * 0.35 + 5, Z * 0.35, 4, 419))
    img = comp(img, hexc('#ff9a50'), crack * 0.35)
    em += crack[..., None] * ember * 0.85
    # lueur de braise le long des joints (faible)
    jl = smooth(0.012, 0.0, ed) * smooth(0.55, 0.8, fbm(X * 0.8, Z * 0.8, 3, 421))
    em += jl[..., None] * ember * 0.25
    s, dep, tot = c.perim()
    worn = smooth(0.25, 0.6, fbm(X * 1.2 + 4, Z * 1.2, 5, 431)) * 0.4 + 0.6
    # frise de bronze patiné + damier sombre
    bronze = hexc('#7a5a34')
    inside, pat = edge_band(c, s, dep, bronze, bronze, 0.55, 1.0, 0.5)
    img = comp(img, bronze, inside * 0.95 * worn)
    img = comp(img, hexc('#14110f'), inside * pat * 0.85)
    # sceau central : anneaux + étoile à 7 branches + runes, vert-bleuté lumineux
    seal = np.zeros(X.shape, np.float32)
    for r_, w_ in ((6.0, 0.28), (4.2, 0.14), (6.6, 0.1), (2.4, 0.2)):
        seal = np.maximum(seal, c.ring(0, 0, r_, w_))
    star = []
    for k in range(7):
        a0 = k * 2 * math.pi / 7 - math.pi / 2
        a1 = (k + 3) * 2 * math.pi / 7 - math.pi / 2
        star.append((4.2 * math.cos(a0), 4.2 * math.sin(a0), 4.2 * math.cos(a1), 4.2 * math.sin(a1)))
    seal = draw_segs(c, star, 0.14, out=seal)
    seal = draw_segs(c, rune_segs(0, 0, 5.1, 28, 0.55, seed=7), 0.05, out=seal)
    seal = draw_segs(c, rune_segs(0, 0, 3.3, 18, 0.45, seed=8), 0.05, out=seal)
    seal = np.maximum(seal, c.circle(0, 0, 0.6))
    seal = seal * worn
    img = comp(img, hexc('#2f8f80'), seal * 0.8)
    em += seal[..., None] * teal * 0.95
    em += (c.circle(0, 0, 5.8) * 0.05)[..., None] * teal
    # zones d'équipe : braise (gauche) / spectre (droite)
    img, em = team_zones(c, img, em, left='#b8441c', right='#2fa38a', em_left='#ff7a30', em_right='#52ffc4', a=0.75, worn=worn)
    ao = c.contact_ao(wall=0.3, wall_len=0.9, obst=0.5, obst_len=0.7)
    img = img * ao[..., None]
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#0b090e'), under)
        em = em * (1 - under[..., None])
        ring_ = c.ring(ox, oz, r + 0.4, 0.08) * worn
        img = comp(img, hexc('#2f8f80'), ring_ * 0.6)
        em += ring_[..., None] * teal * 0.6
    em = np.clip(em, 0, 1.2)
    finish_ground('underworld_ground', img, h, em / 1.2)


def water():
    size = 512
    X, Y = tile_coords(size, 6.0)
    n = fbm(X * 0.9, Y * 0.9, 5, 441, (5, 5))
    w1 = np.abs(np.sin((X * 1.3 + Y * 0.8 + n * 3.5) * math.pi))
    w2 = np.abs(np.sin((X * -0.7 + Y * 1.5 + n * 4.0 + 1.0) * math.pi))
    veins = smooth(0.2, 0.0, w1) * 0.7 + smooth(0.16, 0.0, w2) * 0.6
    veins = np.clip(veins * (0.45 + 0.8 * smooth(0.35, 0.8, fbm(X * 1.2, Y * 1.2, 4, 443, (7, 7)))), 0, 1)
    base = grad(np.clip(n, 0, 1), [(0, hexc('#06201f')), (0.5, hexc('#0a3836')), (1, hexc('#11524c'))])
    col = comp(base, hexc('#4fe0b8'), veins * 0.55)
    save('underworld_water.png', col)
    emm = veins[..., None] * hexc('#4cf2c2') * 0.8 + (n[..., None] * 0.06) * hexc('#2fd4a8')
    save('underworld_water_e.png', np.clip(emm, 0, 1))


def tiles():
    tile_rock('underworld_basalt', 512, c0='#15131a', c1='#2a2631', c2='#4b4452', seed=451, strata=0.3, crack=0.8)
    tile_rock('underworld_rock', 512, c0='#1a171d', c1='#35303a', c2='#5c5362', seed=452, strata=0.6, crack=0.6)
    tile_metal('underworld_bronze', 512, base='#8d6234', seed=453, rust=0.3, rust_col='#2f6a58', scale_m=2.0, plates=4)
    tile_ashlar('underworld_stone', 512, palette=('#2c2833', '#252129', '#332e3b', '#1f1b24'), joint='#08070a', rows=6, block_w=(1.0, 1.8), seed=454, wear=0.4, shade=0.12)
    tile_noise('underworld_cloth', 256, base='#6a2a2a', var=0.2, seed=455, scale=1.3, grain=0.05)
    water()


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['tiles', 'ground']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
