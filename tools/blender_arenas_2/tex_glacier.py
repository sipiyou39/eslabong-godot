"""Textures de l'arène « Glacier des Géants » : banquise bleutée fracturée, neige, glace de falaise striée, roche, aurore (RGBA)."""
import math
import numpy as np
from PIL import Image
import tex as T
from tex import *

TAU_ = 2 * math.pi


def peaks_segs(cx, cz, r0, r1, n, w=0.3, rot=0.0):
    """couronne de pics triangulaires (clin d'œil aux montagnes)."""
    segs = []
    for k in range(n):
        a = rot + TAU_ * k / n
        p0 = (cx + r0 * math.cos(a - w), cz + r0 * math.sin(a - w))
        p1 = (cx + r1 * math.cos(a), cz + r1 * math.sin(a))
        p2 = (cx + r0 * math.cos(a + w), cz + r0 * math.sin(a + w))
        segs += [(p0[0], p0[1], p1[0], p1[1]), (p1[0], p1[1], p2[0], p2[1])]
    return segs


def wave_ring_segs(cx, cz, r, amp, n_waves, steps=360):
    pts = []
    for i in range(steps + 1):
        a = TAU_ * i / steps
        rr = r + amp * math.sin(a * n_waves)
        pts.append((cx + rr * math.cos(a), cz + rr * math.sin(a)))
    return [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(steps)]


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    n_big = fbm(X / 7.0, Z / 7.0, 4, 1)
    n_mid = fbm(X * 0.7, Z * 0.7, 5, 2)
    n_fine = fbm(X * 8, Z * 8, 4, 3)
    n_vf = fbm(X * 30, Z * 30, 3, 4)
    # --- glace bleutée : dégradé large + veines claires
    t = np.clip(n_big * 0.75 + n_mid * 0.35, 0, 1)
    base = grad(t, [(0.0, hexc('#2c76b8')), (0.35, hexc('#4c9bd2')), (0.7, hexc('#7cc0e8')), (1.0, hexc('#b8e4f8'))])
    base = base * (1 + (n_fine[..., None] - 0.5) * 0.14)
    # stries de pression (crêtes sinueuses claires)
    wx = fbm(X * 0.3, Z * 0.3, 4, 5) * 2.0
    ridge = smooth(0.035, 0.0, np.abs(fbm(X * 0.22 + wx * 0.5, Z * 0.34 + wx * 0.3, 5, 7) - 0.5))
    base = comp(base, hexc('#d6efff'), ridge * 0.55)
    # bulles d'air emprisonnées
    bub = smooth(0.70, 0.82, n_vf) * (0.4 + 0.6 * smooth(0.3, 0.7, n_mid))
    base = comp(base, hexc('#dff3ff'), bub * 0.22)
    # --- grandes fractures (cellules ~5 m) : lignes sombres + givre
    f1, f2, cid = cell(X * 0.22 + (n_mid - 0.5) * 0.55, Z * 0.22 + (n_mid - 0.5) * 0.55, 11)
    ee = (f2 - f1) / 0.22          # mètres
    mask_a = smooth(0.30, 0.55, hash01((cid * 977).astype(np.int64), (cid * 313).astype(np.int64), 3))
    frac_w = 0.045 * (0.55 + 0.9 * smooth(0.3, 0.8, fbm(X * 0.35, Z * 0.35, 3, 13)))
    frac = smooth(frac_w, frac_w * 0.25, ee) * (0.35 + 0.65 * mask_a)
    frost = smooth(0.34, 0.0, ee) * (0.4 + 0.6 * mask_a)
    base = comp(base, hexc('#eaf6ff'), frost * 0.28)
    base = comp(base, hexc('#173a62'), frac * 0.85)
    # fissures fines secondaires
    g1, g2, _ = cell(X * 0.75 + n_mid * 0.9, Z * 0.75 + n_mid * 0.7, 21)
    thin = smooth(0.032, 0.0, g2 - g1) * smooth(0.52, 0.78, fbm(X * 0.5, Z * 0.5, 4, 23))
    base = comp(base, hexc('#1f4a78'), thin * 0.45)
    base = comp(base, hexc('#e6f4ff'), smooth(0.07, 0.015, g2 - g1) * smooth(0.52, 0.78, fbm(X * 0.5, Z * 0.5, 4, 23)) * 0.15)
    # --- congères : neige poudreuse surtout le long des bords + plaques
    edge_snow = smooth(3.8, 0.4, depth + (n_mid - 0.5) * 3.2)
    patch = smooth(0.64, 0.80, fbm(X * 0.45, Z * 0.45, 5, 31))
    snow = np.clip(edge_snow * 0.95 + patch * 0.7, 0, 1)
    snow_col = mix(hexc('#cddff0'), hexc('#f4f9ff'), smooth(0.3, 0.7, n_fine))
    img = comp(base, snow_col, snow * 0.92)
    # --- marquages gravés dans la glace : sceau des géants (anneaux, vagues d'aurore, pics)
    wornm = smooth(0.12, 0.45, fbm(X * 1.0, Z * 1.0, 5, 41)) * 0.4 + 0.6
    em = np.zeros((GH, GW, 3), np.float32)
    seal = np.maximum(c.ring(0, 0, 8.6, 0.2), c.ring(0, 0, 7.8, 0.07))
    seal = np.maximum(seal, draw_segs(c, wave_ring_segs(0, 0, 6.5, 0.4, 24), 0.075))
    seal = np.maximum(seal, draw_segs(c, wave_ring_segs(0, 0, 5.7, 0.3, 16), 0.05))
    seal = np.maximum(seal, draw_segs(c, peaks_segs(0, 0, 4.4, 5.3, 12, 0.18), 0.07))
    seal = np.maximum(seal, c.ring(0, 0, 4.2, 0.1))
    seal = np.maximum(seal, draw_segs(c, rune_segs(0, 0, 7.15, 40, 0.5, seed=17), 0.045))
    for k in range(8):
        a = k * math.pi / 4
        L = 4.0 if k % 2 == 0 else 3.0
        seal = np.maximum(seal, draw_segs(c, [(1.3 * math.cos(a), 1.3 * math.sin(a), L * math.cos(a), L * math.sin(a))], 0.11 if k % 2 == 0 else 0.065))
    seal = np.maximum(seal, draw_segs(c, snowflake_segs(0, 0, 1.25, rot=math.pi / 6), 0.07))
    seal = np.maximum(seal, c.ring(0, 0, 1.55, 0.06))
    seal = seal * wornm
    deep = hexc('#244f7a')
    img = comp(img, deep, c.circle(0, 0, 9.0, edge=0.05) * 0.18)
    img = comp(img, hexc('#c8f2ff'), seal * 0.9)
    em += seal[..., None] * hexc('#4fe6d0') * 0.78
    # aurore froide au cœur
    core = c.circle(0, 0, 0.7, edge=0.03)
    img = comp(img, hexc('#b8fff0'), core)
    em += core[..., None] * hexc('#8affe6') * 1.0
    # --- zones d'équipe : ambre (G) / teal d'aurore (D)
    for sg, colv, ecol in ((-1, hexc('#ffb457'), hexc('#ff9a30')), (1, hexc('#6aecd2'), hexc('#3fd8b8'))):
        cx = 19.0 * sg
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.15), c.ring(cx, 0, 2.7, 0.08))
        z_ = np.maximum(z_, draw_segs(c, peaks_segs(cx, 0, 1.2, 2.4, 6, 0.3, rot=math.pi / 6), 0.075))
        z_ = np.maximum(z_, draw_segs(c, rune_segs(cx, 0, 4.45, 20, 0.45, seed=9 + sg), 0.045))
        z_ = np.maximum(z_, c.ring(cx, 0, 0.9, 0.07))
        z_ = np.maximum(z_, c.dashed(13.0 * sg, -12.5, 13.0 * sg, 12.5, 0.14, 0.9, 0.45))
        z_ = z_ * wornm
        img = comp(img, deep, c.circle(cx, 0, 4.0, edge=0.05) * 0.18)
        img = comp(img, colv, z_ * 0.88)
        em += z_[..., None] * ecol * 0.5
    # --- lueur sous-glaciaire : les fractures profondes émettent un peu de bleu
    em += (frac * (0.35 + 0.65 * mask_a))[..., None] * hexc('#2a8fd0') * 0.16 * (1 - snow[..., None])
    # --- AO de contact + ombres des obstacles
    ao = c.contact_ao(wall=0.22, wall_len=0.8, obst=0.5, obst_len=0.7)
    img = img * (0.82 + 0.18 * ao[..., None]) if False else img * ao[..., None]
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#d6e8f6'), under)
        em = em * (1 - under[..., None])
        ring_ = c.ring(ox, oz, r + 0.65, 0.07) * wornm
        img = comp(img, hexc('#e6f8ff'), ring_ * 0.6)
        em += ring_[..., None] * hexc('#4fe6d0') * 0.28
        shadow = np.exp(-np.maximum(d - r, 0) / 0.6) * (d > r)
        img = comp(img, hexc('#3a6a98'), shadow * 0.28)
    # petits flocons / poudre
    spk = smooth(0.80, 0.9, n_vf) * (1 - snow) * 0.18
    img = comp(img, hexc('#ffffff'), spk)
    hgt = (n_fine * 0.004 + ridge * 0.02 + snow * 0.025 * (n_mid) - frac * 0.07 - thin * 0.012 + frost * 0.004).astype(np.float32)
    hgt = hgt * (1 - 0.7 * seal) - seal * 0.012
    em = np.clip(em, 0, 1.2)
    save('glacier_ground.png', img)
    save('glacier_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    save('glacier_ground_e.png', np.clip(em / 1.2, 0, 1))


# ------------------------------------------------------------------ tuiles
def tile_snowice(name, size=512, seed=300, scale_m=4.0):
    """neige tassée bleutée avec plaques de glace et éclats : sol des terrasses."""
    X, Y = tile_coords(size, scale_m)
    n = fbm(X * 1.25, Y * 1.25, 5, seed, (5, 5))
    n2 = fbm(X * 2.5, Y * 2.5, 4, seed + 3, (10, 10))
    ice = smooth(0.55, 0.72, fbm(X * 0.75, Y * 0.75, 4, seed + 5, (3, 3)))
    snow = mix(hexc('#c4d8ea')[None, None, :], hexc('#f2f8ff')[None, None, :], smooth(0.25, 0.75, n))
    icec = mix(hexc('#7db4d8')[None, None, :], hexc('#bfe2f2')[None, None, :], smooth(0.3, 0.7, n2))
    col = mix(snow, icec, ice * 0.8)
    sp = hash01(np.floor(X * 110).astype(np.int64) % 440, np.floor(Y * 110).astype(np.int64) % 440, seed)
    col = col * (1 + (sp[..., None] - 0.5) * 0.07)
    f1, f2, _ = cell(X * 1.75 + (n - 0.5) * 0.5, Y * 1.75 + (n - 0.5) * 0.5, seed + 8, (7, 7))
    cr = smooth(0.04, 0.0, f2 - f1) * ice
    col = comp(col, hexc('#4a86b4'), cr * 0.5)
    h = n * 0.08 + n2 * 0.02 - cr * 0.03
    save(name + '.png', col)
    save(name + '_n.png', to_normal(h, 1.3, scale_m / size, wrap=True))


def tile_icecliff(name, size=512, seed=310, scale_m=4.0):
    """falaise de glace : cannelures verticales bleu profond -> blanc, strates fines, veines."""
    X, Y = tile_coords(size, scale_m)
    w = fbm(X * 0.5, Y * 0.5, 4, seed, (2, 2)) - 0.5
    flute = fbm(X * 2.0 + w * 1.2, Y * 0.5, 5, seed + 2, (8, 2))
    strata = 0.5 + 0.5 * np.sin((Y * 5.0 + fbm(X * 1.0, Y * 1.0, 3, seed + 4, (4, 4)) * 2.5) * TAU_)
    t = np.clip(flute * 0.55 + strata * 0.1 + 0.3, 0, 1)
    col = grad(t, [(0.0, hexc('#2a5f96')), (0.4, hexc('#5a9ccb')), (0.75, hexc('#a6d6ee')), (1.0, hexc('#eaf6ff'))])
    f1, f2, cid = cell(X * 1.5 + w, Y * 0.75 + w * 0.5, seed + 6, (6, 3))
    cr = smooth(0.05, 0.0, f2 - f1) * 0.55
    col = comp(col, hexc('#1b4676'), cr * 0.25)
    col = col * (1 + (fbm(X * 20, Y * 20, 3, seed + 9, (80, 80))[..., None] - 0.5) * 0.12)
    h = flute * 0.1 + strata * 0.01 - cr * 0.04
    save(name + '.png', col)
    save(name + '_n.png', to_normal(h, 0.7, scale_m / size, wrap=True))


def tile_deep(name, size=512, seed=320, scale_m=4.0):
    """parois de crevasse : bleu-vert profond, veines claires."""
    X, Y = tile_coords(size, scale_m)
    n = fbm(X * 1.25, Y * 2.5, 5, seed, (5, 10))
    v = smooth(0.0, 0.06, np.abs(fbm(X * 0.5 + n * 0.4, Y * 1.5, 4, seed + 3, (2, 6)) - 0.5))
    col = grad(np.clip(n, 0, 1), [(0.0, hexc('#0f2f5a')), (0.5, hexc('#1b5a8c')), (1.0, hexc('#3e9bbf'))])
    col = comp(col, hexc('#9adcf0'), (1 - v) * 0.3)
    save(name + '.png', col)
    save(name + '_n.png', to_normal(n * 0.1, 1.2, scale_m / size, wrap=True))


def aurora_tex(name='glacier_aurora', W=1024, H=256):
    """rideau d'aurore RGBA (v vers le haut = rangées du bas) : rayons verticaux, vert -> teal -> violet. Pas de sRGB complexe."""
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(H)[::-1] + 0.5) / H          # ligne 0 de l'image = haut (v=1)
    U, V = np.meshgrid(u.astype(np.float32), v.astype(np.float32))
    rays = fbm(U * 90.0 + fbm(U * 8, V * 2, 3, 5) * 6.0, V * 0.8, 4, 11)
    rays = smooth(0.25, 0.8, rays)
    soft = fbm(U * 7.0, V * 1.5, 4, 13)
    fade_v = smooth(0.0, 0.08, V) * (1 - smooth(0.35, 1.0, V)) ** 1.4
    alpha = np.clip(fade_v * (0.25 + 0.9 * rays) * (0.6 + 0.7 * soft), 0, 1)
    alpha *= smooth(0.0, 0.06, U) * smooth(1.0, 0.94, U)
    col = grad(np.clip(V * 1.25 + (soft - 0.5) * 0.3, 0, 1), [(0.0, hexc('#8dffa8')), (0.35, hexc('#4de8c0')), (0.7, hexc('#5ab0ff')), (1.0, hexc('#b078ff'))])
    rgba = np.concatenate([col, alpha[..., None]], -1)
    a = (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(a, 'RGBA').save(os.path.join(TEXDIR, name + '.png'), optimize=True)
    print('texture', name + '.png', a.shape)


def tiles():
    tile_snowice('glacier_snow', 512, seed=300)
    tile_icecliff('glacier_cliff', 512, seed=310)
    tile_deep('glacier_deep', 512, seed=320)
    tile_ice('glacier_ice', 512, seed=330, c0='#74aed4', c1='#d4f0ff', c2='#2f6aa0')
    tile_rock('glacier_rock', 512, '#1f2634', '#44516b', '#8794ad', seed=331, strata=0.6, crack=0.8)
    tile_wood('glacier_wood', 512, '#2a1d14', '#5c4129', seed=332)
    tile_metal('glacier_iron', 512, base='#6f7480', seed=333, rust=0.2, rust_col='#5a3a22', scale_m=2.0, plates=2, rivets=False)
    tile_noise('glacier_cloth', 512, base='#7a5a3e', var=0.22, seed=334, scale=1.5, grain=0.1, tint2='#d8c8a8')
    tile_marble('glacier_bone', 512, '#e8dcc4', '#cbbd9f', '#9d8e72', seed=335, strata=0.0, vein_amt=0.4, grain=0.05)
    aurora_tex()


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
