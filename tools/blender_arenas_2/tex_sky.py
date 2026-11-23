"""Textures de l'arène « Îles des Nuages » : dalles de pierre claire à incrustations d'or (rose des vents solaire), pierre, roche, herbe, bois, voiles."""
import math
import numpy as np
import tex as T
from tex import *

TAU_ = 2 * math.pi


def spiral_segs(cx, cz, r0, r1, turns, phase=0.0, steps=140):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = phase + TAU_ * turns * t
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(steps)]


def ray_polys(cx, cz, n, r_in, r_long, r_short, w_long, w_short, rot=0.0):
    """pointes de rose des vents : (liste de triangles) -> masque via distances aux arêtes."""
    tris = []
    for k in range(n):
        a = rot + TAU_ * k / n
        long_ = k % 2 == 0
        rl = r_long if long_ else r_short
        w = w_long if long_ else w_short
        p0 = (cx + r_in * math.cos(a - w), cz + r_in * math.sin(a - w))
        p1 = (cx + rl * math.cos(a), cz + rl * math.sin(a))
        p2 = (cx + r_in * math.cos(a + w), cz + r_in * math.sin(a + w))
        tris.append((p0, p1, p2))
    return tris


def fill_tris(c, tris):
    out = np.zeros((GH, GW), np.float32)
    for (p0, p1, p2) in tris:
        xs = [p0[0], p1[0], p2[0]]
        zs = [p0[1], p1[1], p2[1]]
        i0, i1, j0, j1 = T._win(c, min(xs), min(zs), max(xs), max(zs), 0.05)
        X = c.X[i0:i1, j0:j1]
        Z = c.Z[i0:i1, j0:j1]

        def edge(a, b):
            return (b[0] - a[0]) * (Z - a[1]) - (b[1] - a[1]) * (X - a[0])
        d0, d1, d2 = edge(p0, p1), edge(p1, p2), edge(p2, p0)
        L = lambda a, b: math.hypot(b[0] - a[0], b[1] - a[1])
        s0, s1, s2 = d0 / L(p0, p1), d1 / L(p1, p2), d2 / L(p2, p0)
        sgn = 1.0 if ((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])) > 0 else -1.0
        m = smooth(-0.012, 0.012, np.minimum(np.minimum(s0 * sgn, s1 * sgn), s2 * sgn))
        out[i0:i1, j0:j1] = np.maximum(out[i0:i1, j0:j1], m)
    return out


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    n_big = fbm(X / 6.0, Z / 6.0, 4, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 9, Z * 9, 4, 3)
    n_vf = fbm(X * 38, Z * 38, 3, 4)
    # --- dalles claires 2.6 m, appareil en quinconce
    SX = 2.6
    row = np.floor((Z + 17.2) / SX)
    off = (row % 2) * 0.5
    col_i = np.floor((X + 27.0) / SX + off)
    u = (X + 27.0) / SX + off - col_i
    v = (Z + 17.2) / SX - row
    ed = np.minimum(np.minimum(u * SX, (1 - u) * SX), np.minimum(v * SX, (1 - v) * SX))
    sid = hash01(col_i.astype(np.int64), row.astype(np.int64), 7)
    pal = [hexc('#e9dcc0'), hexc('#dfd0b0'), hexc('#f1e6cd'), hexc('#d6c6a4'), hexc('#e4d3b2')]
    pi_ = (sid * len(pal)).astype(int) % len(pal)
    base = np.zeros(X.shape + (3,), np.float32)
    for k, col in enumerate(pal):
        base[pi_ == k] = col
    base = base * (0.9 + 0.2 * sid[..., None]) * (1 + (n_mid[..., None] - 0.5) * 0.14)
    # veines de marbre doux
    wv = fbm(X * 0.35, Z * 0.35, 4, 5)
    vein = smooth(0.03, 0.0, np.abs(np.sin((X * 0.55 + Z * 0.8 + wv * 4.0) * 2.2) * 0.5)) * smooth(0.5, 0.7, fbm(X * 0.9, Z * 0.9, 3, 6))
    base = comp(base, hexc('#b9a888'), vein * 0.4)
    base = base * (1 + (n_fine[..., None] - 0.5) * 0.10) * (1 - smooth(0.7, 0.82, n_vf)[..., None] * 0.12)
    # biseau + joints
    bevel = smooth(0.0, 0.10, ed)
    base = base * (0.8 + 0.22 * bevel[..., None])
    joint = smooth(0.035, 0.012, ed)
    base = comp(base, hexc('#8a7a5e'), joint * 0.85)
    # herbe dans certains joints (touffes éparses)
    tuft = joint * smooth(0.62, 0.8, fbm(X * 1.3, Z * 1.3, 4, 11))
    base = comp(base, hexc('#7f9a3c'), tuft * 0.8)
    # taches de patine / usure chaude
    patina = smooth(0.60, 0.80, fbm(X * 0.5, Z * 0.5, 5, 12))
    base = comp(base, hexc('#c8a870'), patina * 0.22)
    img = base
    em = np.zeros((GH, GW, 3), np.float32)
    gold = hexc('#d9a53a')
    lapis = hexc('#2f5aa8')
    wornm = smooth(0.1, 0.45, fbm(X * 1.0, Z * 1.0, 5, 41)) * 0.35 + 0.65
    # --- bordure incrustée le long du rebord : double filet d'or + tirets
    rim_d = depth
    line1 = smooth(0.075, 0.03, np.abs(rim_d - 1.35))
    line2 = smooth(0.045, 0.015, np.abs(rim_d - 1.65))
    frame = np.maximum(line1, line2) * wornm
    img = comp(img, gold, frame * 0.9)
    # frise bleue fine
    band = smooth(0.05, 0.02, np.abs(rim_d - 1.0)) * wornm
    img = comp(img, lapis, band * 0.55)
    # --- rose des vents solaire centrale
    ring = np.zeros((GH, GW), np.float32)
    for r_, w_ in ((9.0, 0.18), (8.55, 0.06), (6.9, 0.1), (4.15, 0.12), (1.7, 0.08)):
        ring = np.maximum(ring, c.ring(0, 0, r_, w_))
    ring = np.maximum(ring, draw_segs(c, rune_segs(0, 0, 7.75, 36, 0.55, seed=23), 0.045))
    ring = np.maximum(ring, draw_segs(c, spiral_segs(0, 0, 0.0, 0.0, 1, steps=2), 0.01))
    rays = fill_tris(c, ray_polys(0, 0, 16, 4.4, 8.3, 6.1, 0.2, 0.15, rot=math.pi / 16 * 0))
    rays_in = fill_tris(c, ray_polys(0, 0, 16, 4.4, 7.9, 5.7, 0.1, 0.075, rot=0))
    disc_back = c.circle(0, 0, 9.2, edge=0.04)
    img = comp(img, hexc('#efe4c8'), disc_back * 0.55)
    img = comp(img, hexc('#c89a34'), rays * wornm * 0.95)
    img = comp(img, lapis, rays_in * wornm * 0.9)
    img = comp(img, gold, ring * wornm * 0.95)
    # petites pointes cardinales
    card = []
    for k in range(4):
        a = k * math.pi / 2
        card.append(((10.2 * math.cos(a - 0.08), 10.2 * math.sin(a - 0.08)), (11.3 * math.cos(a), 11.3 * math.sin(a)), (10.2 * math.cos(a + 0.08), 10.2 * math.sin(a + 0.08))))
    cm = fill_tris(c, card)
    img = comp(img, gold, cm * wornm)
    sun = c.circle(0, 0, 1.45, edge=0.03)
    sun_col = grad(np.clip(1.0 - np.hypot(X, Z) / 1.45, 0, 1) * 0.7 + 0.2, [(0, hexc('#d9a53a')), (0.5, hexc('#f3c85a')), (1.0, hexc('#fff0b0'))])
    img = comp(img, sun_col, sun)
    em += sun[..., None] * hexc('#ffc850') * 0.55
    em += (ring * wornm)[..., None] * hexc('#ffb840') * 0.10
    # --- zones d'équipe : spirales de nuage corail (G) / azur (D)
    for sg, colv, ecol in ((-1, hexc('#e4573a'), hexc('#ff6a40')), (1, hexc('#3d92dc'), hexc('#58aaf5'))):
        cx = 19.0 * sg
        z_ = np.maximum(c.ring(cx, 0, 3.75, 0.16), c.ring(cx, 0, 3.15, 0.07))
        z_ = np.maximum(z_, draw_segs(c, spiral_segs(cx, 0, 0.35, 2.8, 2.3, phase=0.0), 0.1))
        z_ = np.maximum(z_, draw_segs(c, spiral_segs(cx, 0, 0.35, 2.8, 2.3, phase=math.pi), 0.07))
        z_ = np.maximum(z_, draw_segs(c, rune_segs(cx, 0, 4.5, 20, 0.45, seed=9 + sg), 0.045))
        z_ = np.maximum(z_, c.dashed(13.0 * sg, -12.5, 13.0 * sg, 12.5, 0.14, 0.9, 0.45))
        z_ = z_ * wornm
        img = comp(img, hexc('#f4ead2'), c.circle(cx, 0, 3.95, edge=0.05) * 0.45)
        img = comp(img, colv, z_ * 0.9)
        em += z_[..., None] * ecol * 0.14
    # --- AO de contact + ombres des obstacles
    ao = c.contact_ao(wall=0.18, wall_len=0.8, obst=0.5, obst_len=0.7)
    img = img * ao[..., None]
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#cdbd9c'), under)
        ring_ = c.ring(ox, oz, r + 0.6, 0.07) * wornm
        img = comp(img, gold, ring_ * 0.8)
        sh = np.exp(-np.maximum(d - r, 0) / 0.6) * (d > r)
        img = comp(img, hexc('#8a7458'), sh * 0.25)
        em = em * (1 - under[..., None])
    # fissures fines
    f1, f2, _ = cell(X * 0.9 + n_mid, Z * 0.9 + n_mid, 33)
    thin = smooth(0.03, 0.0, f2 - f1) * smooth(0.6, 0.82, fbm(X * 0.4, Z * 0.4, 4, 35)) * smooth(0.05, 0.12, ed)
    img = img * (1 - thin[..., None] * 0.35)
    hgt = (n_fine * 0.004 + bevel * 0.03 - joint * 0.03 - thin * 0.02 + (frame + ring) * 0.004).astype(np.float32)
    em = np.clip(em, 0, 1.0)
    save('sky_ground.png', img)
    save('sky_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    save('sky_ground_e.png', np.clip(em, 0, 1))


def tiles():
    tile_ashlar('sky_stone', 512, palette=('#e4d6b8', '#d8c8a6', '#ede0c4', '#cdbb98'), joint='#8a7a5c', rows=6, block_w=(1.0, 1.9),
                seed=401, wear=0.4, shade=0.1)
    tile_marble('sky_marble', 512, '#f2ead6', '#ddd0b2', '#b8a888', seed=402, strata=0.0, vein_amt=0.45, grain=0.03)
    tile_rock('sky_rock', 512, '#5a3f34', '#9a7050', '#d2a878', seed=403, strata=0.9, crack=0.5)
    tile_noise('sky_grass', 512, base='#74923a', var=0.25, seed=404, scale=1.5, grain=0.1, tint2='#b4b04a')
    tile_wood('sky_wood', 512, '#4a3320', '#9a6e40', seed=405)
    tile_noise('sky_rope', 512, base='#b49a68', var=0.25, seed=406, scale=2.0, grain=0.12, tint2='#7a6644')
    tile_noise('sky_cloth', 512, base='#efe2c0', var=0.12, seed=407, scale=1.3, grain=0.06)
    tile_noise('sky_leaf', 512, base='#6e9a3a', var=0.3, seed=408, scale=2.0, grain=0.1, tint2='#c0b848')
    tile_noise('sky_roof', 512, base='#b4552f', var=0.22, seed=410, scale=1.5, grain=0.1, tint2='#8a3a20')
    tile_noise('sky_plaster', 512, base='#efe1c4', var=0.1, seed=411, scale=1.4, grain=0.06)
    tile_metal('sky_bronze', 512, base='#a0804c', seed=409, rust=0.0, scale_m=2.0, plates=2, rivets=False)


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
