"""Textures de l'arène « Temple de la Jungle » : dallage de cour moussu, calendrier de pierre gravé (jade émissif), racines, humus, écorce, feuillage, jade, eau."""
import math
import numpy as np
import tex as T
from tex import *

TAU_ = 2 * math.pi


def bez_path(rg, p0, p1, bend, n=40):
    """courbe de Bézier quadratique p0 -> p1 avec un point de contrôle décalé."""
    mx, mz = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dz)
    c = (mx - dz / L * bend, mz + dx / L * bend)
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0]
        z = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]
        pts.append((x, z))
    return pts


def glyph_boxes(cx, cz, r, n, size, seed):
    """cases carrées gravées (contour) disposées sur un anneau, chacune avec un petit glyphe."""
    rg = np.random.default_rng(seed)
    segs = []
    for k in range(n):
        a = TAU_ * k / n
        px, pz = cx + r * math.cos(a), cz + r * math.sin(a)
        ux, uz = -math.sin(a), math.cos(a)
        vx, vz = math.cos(a), math.sin(a)
        h = size / 2

        def P(lx, lz):
            return (px + ux * lx + vx * lz, pz + uz * lx + vz * lz)
        corners = [P(-h, -h), P(h, -h), P(h, h), P(-h, h)]
        for i in range(4):
            a_, b_ = corners[i], corners[(i + 1) % 4]
            segs.append((a_[0], a_[1], b_[0], b_[1]))
        # glyphe : 2 à 4 traits aléatoires dans la case
        pts = [(-0.3, -0.3), (0.3, -0.3), (0.0, 0.0), (-0.3, 0.3), (0.3, 0.3), (0.0, -0.35), (0.0, 0.35)]
        m = rg.integers(2, 5)
        idx = rg.choice(len(pts), m, replace=False)
        for j in range(m - 1):
            p0 = P(pts[idx[j]][0] * size, pts[idx[j]][1] * size)
            p1 = P(pts[idx[j + 1]][0] * size, pts[idx[j + 1]][1] * size)
            segs.append((p0[0], p0[1], p1[0], p1[1]))
    return segs


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    n_big = fbm(X / 6.0, Z / 6.0, 4, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 9, Z * 9, 4, 3)
    n_vf = fbm(X * 36, Z * 36, 3, 4)
    # --- dalles irrégulières (pavage de ruine)
    wx = fbm(X * 0.4, Z * 0.4, 4, 5) - 0.5
    wz = fbm(X * 0.4 + 7, Z * 0.4, 4, 6) - 0.5
    f1, f2, cid = cell(X * 0.42 + wx * 0.7, Z * 0.42 + wz * 0.7, 9)
    ed = (f2 - f1) / 0.42
    pal = [hexc('#8e8a7a'), hexc('#7f7d6c'), hexc('#999484'), hexc('#76786a'), hexc('#8a8576')]
    pi_ = (cid * len(pal)).astype(int) % len(pal)
    base = np.zeros(X.shape + (3,), np.float32)
    for k, col in enumerate(pal):
        base[pi_ == k] = col
    base = base * (0.84 + 0.3 * cid[..., None]) * (1 + (n_mid[..., None] - 0.5) * 0.2)
    base = base * (1 + (n_fine[..., None] - 0.5) * 0.12) * (1 - smooth(0.68, 0.8, n_vf)[..., None] * 0.14)
    bevel = smooth(0.0, 0.16, ed)
    base = base * (0.74 + 0.3 * bevel[..., None])
    joint = smooth(0.06, 0.02, ed)
    base = comp(base, hexc('#2e2a22'), joint * 0.9)
    # --- mousse : dans les joints, au bord et en plaques
    mossn = fbm(X * 0.8 + n_mid * 2, Z * 0.8, 5, 11)
    moss_m = np.clip(smooth(0.52, 0.72, mossn) * 0.75 + joint * 0.55 + smooth(2.2, 0.0, depth) * 0.35 * smooth(0.3, 0.6, n_mid), 0, 1)
    mcol = mix(hexc('#3a6020'), hexc('#6c9a34'), smooth(0.3, 0.8, fbm(X * 4, Z * 4, 3, 13)))
    base = comp(base, mcol, moss_m * 0.85)
    # touffes d'herbe dans les joints
    tuft = joint * smooth(0.6, 0.78, fbm(X * 1.6, Z * 1.6, 4, 17))
    base = comp(base, hexc('#5e8e2e'), tuft * 0.9)
    # taches d'humidité
    wet = smooth(0.6, 0.8, fbm(X * 0.55, Z * 0.55, 5, 19))
    base = base * (1 - wet[..., None] * 0.2)
    img = base
    em = np.zeros((GH, GW, 3), np.float32)
    hgt = (n_fine * 0.004 + bevel * 0.04 - joint * 0.05 + moss_m * 0.01).astype(np.float32)
    # --- calendrier de pierre gravé au centre
    R = np.hypot(X, Z)
    disc = c.circle(0, 0, 9.5, edge=0.04)
    clean = grad(np.clip(fbm(X * 1.4, Z * 1.4, 5, 23), 0, 1), [(0, hexc('#8a8676')), (1, hexc('#aaa592'))])
    clean = clean * (1 + (n_fine[..., None] - 0.5) * 0.1)
    img = comp(img, clean, disc * 0.93)
    # un peu de mousse qui mord sur le disque
    img = comp(img, mcol, disc * smooth(0.64, 0.8, mossn) * 0.35)
    hgt = hgt * (1 - disc) + (n_fine * 0.002) * disc
    groove = np.zeros((GH, GW), np.float32)
    for r_, w_ in ((9.25, 0.16), (8.5, 0.08), (7.0, 0.09), (5.4, 0.12), (3.6, 0.1), (1.9, 0.08)):
        groove = np.maximum(groove, c.ring(0, 0, r_, w_))
    groove = np.maximum(groove, draw_segs(c, glyph_boxes(0, 0, 7.75, 20, 0.6, seed=31), 0.045))
    groove = np.maximum(groove, draw_segs(c, rune_segs(0, 0, 4.5, 30, 0.5, seed=33), 0.045))
    for k in range(8):
        a = k * math.pi / 4
        groove = np.maximum(groove, draw_segs(c, [(0.5 * math.cos(a), 0.5 * math.sin(a), 1.8 * math.cos(a), 1.8 * math.sin(a))], 0.07))
    for k in range(4):
        a = k * math.pi / 2
        tri = [(5.6 * math.cos(a - 0.1), 5.6 * math.sin(a - 0.1), 6.6 * math.cos(a), 6.6 * math.sin(a)), (6.6 * math.cos(a), 6.6 * math.sin(a), 5.6 * math.cos(a + 0.1), 5.6 * math.sin(a + 0.1))]
        groove = np.maximum(groove, draw_segs(c, tri, 0.07))
    wornm = smooth(0.12, 0.45, fbm(X * 1.0, Z * 1.0, 5, 41)) * 0.4 + 0.6
    groove = groove * wornm
    img = comp(img, hexc('#2c2a22'), groove * 0.8)
    hgt = hgt - groove * 0.025
    # incrustations de jade (anneaux 8.5 et 3.6 + cœur)
    jade = np.maximum(c.ring(0, 0, 8.5, 0.05), c.ring(0, 0, 3.6, 0.06))
    jade = np.maximum(jade, draw_segs(c, [(2.4 * math.cos(k * math.pi / 4 + 0.39), 2.4 * math.sin(k * math.pi / 4 + 0.39), 3.4 * math.cos(k * math.pi / 4 + 0.39), 3.4 * math.sin(k * math.pi / 4 + 0.39)) for k in range(8)], 0.09))
    jade = jade * wornm
    core = c.circle(0, 0, 0.8, edge=0.03)
    img = comp(img, hexc('#2fb89a'), jade * 0.9)
    em += jade[..., None] * hexc('#2fe0b8') * 0.45
    img = comp(img, hexc('#37d6b0'), core)
    em += core[..., None] * hexc('#5affd0') * 0.8
    # --- zones d'équipe : médaillons gravés terracotta (G) / jade (D)
    for sg, colv, ecol in ((-1, hexc('#d9552e'), hexc('#ff6a38')), (1, hexc('#33c4a6'), hexc('#44f0c8'))):
        cx = 19.0 * sg
        pad = c.circle(cx, 0, 4.0, edge=0.04)
        img = comp(img, clean * 0.62, pad * 0.92)
        gv = np.maximum(c.ring(cx, 0, 3.75, 0.22), c.ring(cx, 0, 2.9, 0.11))
        gv = np.maximum(gv, draw_segs(c, glyph_boxes(cx, 0, 3.3, 12, 0.34, seed=41 + sg), 0.035))
        gv = np.maximum(gv, c.ring(cx, 0, 1.4, 0.1))
        for k in range(8):
            a = k * math.pi / 4 + math.pi / 8
            gv = np.maximum(gv, draw_segs(c, [(cx + 0.5 * math.cos(a), 0.5 * math.sin(a), cx + 1.3 * math.cos(a), 1.3 * math.sin(a))], 0.07))
        gv = np.maximum(gv, c.dashed(13.0 * sg, -12.5, 13.0 * sg, 12.5, 0.14, 0.9, 0.45))
        gv = gv * wornm
        img = comp(img, hexc('#2c2a22'), np.maximum(c.ring(cx, 0, 3.75, 0.2) * 0.4, 0) * wornm)
        img = comp(img, colv, gv * 0.9)
        em += gv[..., None] * ecol * 0.4
    # --- racines qui rampent sur le dallage (sinueuses, effilées, ramifiées)
    rg = np.random.default_rng(77)
    rootm = np.zeros((GH, GW), np.float32)

    def root(p, ang, length, w0, depth_=0):
        x, z = p
        n = int(length / 0.25)
        for i in range(n):
            t = i / n
            ang += rg.normal(0, 0.16) + 0.05 * math.sin(i * 0.35 + depth_)
            nx, nz = x + math.cos(ang) * 0.25, z + math.sin(ang) * 0.25
            w = w0 * (1 - t) ** 0.85 + 0.05
            draw_segs(c, [(x, z, nx, nz)], w, out=rootm)
            x, z = nx, nz
            if depth_ < 2 and w > 0.12 and rg.random() < 0.05:
                root((x, z), ang + rg.choice([-1, 1]) * rg.uniform(0.5, 1.0), length * rg.uniform(0.3, 0.5), w * 0.55, depth_ + 1)

    for (sx, sz, ang) in [(-26.5, -12.0, 0.35), (-25.0, 11.0, -0.35), (26.5, -8.0, math.pi - 0.3), (25.0, 12.5, math.pi + 0.4), (-8.0, 16.5, -1.2),
                          (13.0, -16.5, 1.5), (-15.0, -16.5, 1.3), (3.0, 16.5, -1.7), (-26.5, 2.0, 0.1), (26.5, 3.0, math.pi)]:
        root((sx, sz), ang, rg.uniform(4.5, 8.0), rg.uniform(0.45, 0.65))
    rootm = rootm * (1 - disc)
    rsh = blur(rootm, 7.0) * (1 - rootm)
    img = img * (1 - rsh[..., None] * 0.35)
    rcol = grad(np.clip(fbm(X * 7, Z * 7, 3, 51), 0, 1), [(0, hexc('#3a2616')), (0.6, hexc('#5e4228')), (1, hexc('#86603a'))])
    rcol = comp(rcol, hexc('#4a7a26'), smooth(0.6, 0.78, fbm(X * 2.5, Z * 2.5, 3, 53)) * 0.5)
    img = comp(img, rcol, rootm * 0.97)
    hgt = hgt + rootm * 0.06
    # --- feuilles mortes
    lit = blobs(c, 1100, 0.05, 0.13, 61, strength=0.8)
    lcol = grad(fbm(X * 3, Z * 3, 2, 63), [(0, hexc('#8a5a22')), (0.5, hexc('#b88a30')), (1, hexc('#6a7a2a'))])
    img = comp(img, lcol, lit * 0.55 * (1 - groove[..., None][..., 0]) * (1 - disc * 0.7))
    # --- AO de contact + ombres des obstacles
    ao = c.contact_ao(wall=0.3, wall_len=0.9, obst=0.5, obst_len=0.7)
    img = img * ao[..., None]
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        under = smooth(r + 0.05, r - 0.1, d)
        img = comp(img, hexc('#4a483c'), under)
        em = em * (1 - under[..., None])
        ring_ = c.ring(ox, oz, r + 0.6, 0.07) * wornm
        img = comp(img, hexc('#2c2a22'), ring_ * 0.6)
        sh = np.exp(-np.maximum(d - r, 0) / 0.6) * (d > r)
        img = comp(img, hexc('#2a3a1a'), sh * 0.3)
    # rais de lumière dans les arbres (taches de soleil douces sur le sol)
    sun_pat = smooth(0.58, 0.78, fbm(X * 0.28 + 5, Z * 0.28, 4, 71)) * 0.22
    img = img * (1 - 0.05) + sun_pat[..., None] * np.array([0.5, 0.45, 0.2], np.float32)
    em = np.clip(em, 0, 1.0)
    save('jungle_ground.png', img)
    save('jungle_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    save('jungle_ground_e.png', np.clip(em, 0, 1))


# ------------------------------------------------------------------ tuiles
def tile_bark(name, size=512, seed=500, scale_m=4.0):
    X, Y = tile_coords(size, scale_m)
    w = fbm(X * 0.5, Y * 0.5, 3, seed, (2, 2)) - 0.5
    fib = fbm(X * 6.0 + w * 2, Y * 0.5, 5, seed + 1, (24, 2))
    ridge = smooth(0.1, 0.0, np.abs(fib - 0.5)) * 0.8
    col = grad(np.clip(fib, 0, 1), [(0, hexc('#2c1e14')), (0.5, hexc('#5a3e28')), (1, hexc('#7e5c3c'))])
    col = col * (1 - ridge[..., None] * 0.45)
    col = comp(col, hexc('#4a6a28'), smooth(0.62, 0.8, fbm(X * 1.5, Y * 1.0, 4, seed + 4, (6, 4))) * 0.35)
    save(name + '.png', col)
    save(name + '_n.png', to_normal(fib * 0.12 - ridge * 0.04, 1.4, scale_m / size, wrap=True))


def tile_cliffrock(name, size=512, seed=530, scale_m=4.0):
    """roche de falaise humide : coulures verticales, strates, plaques de mousse (sans motif en pavés)."""
    X, Y = tile_coords(size, scale_m)
    w = fbm(X * 0.5, Y * 0.5, 4, seed, (2, 2)) - 0.5
    base = fbm(X * 1.5 + w, Y * 0.75, 6, seed + 1, (6, 3))
    strata = 0.5 + 0.5 * np.sin((Y * 3.0 + fbm(X * 1.0, Y * 1.0, 3, seed + 2, (4, 4)) * 2.0) * TAU_)
    stain = smooth(0.45, 0.8, fbm(X * 4.0, Y * 0.4, 5, seed + 3, (16, 2)))
    col = grad(np.clip(base * 0.8 + strata * 0.15, 0, 1), [(0, hexc('#2c382a')), (0.5, hexc('#566448')), (1, hexc('#8c9a72'))])
    col = col * (1 - stain[..., None] * 0.35)
    moss = smooth(0.52, 0.72, fbm(X * 1.6, Y * 1.2, 5, seed + 5, (6, 5)))
    col = comp(col, mix(hexc('#3a6a24'), hexc('#6c9a30'), fbm(X * 6, Y * 6, 3, seed + 6, (24, 24))), moss * 0.7)
    col = col * (1 + (fbm(X * 18, Y * 18, 3, seed + 7, (72, 72))[..., None] - 0.5) * 0.18)
    h = base * 0.12 + strata * 0.02 + moss * 0.03
    save(name + '.png', col)
    save(name + '_n.png', to_normal(h, 1.3, scale_m / size, wrap=True))


def tile_water(name, size=512, seed=520, scale_m=4.0):
    """eau vive : stries verticales blanc-bleu-vert (cascade)."""
    X, Y = tile_coords(size, scale_m)
    w = fbm(X * 1.0, Y * 1.0, 3, seed, (4, 4)) - 0.5
    st = fbm(X * 5.0 + w * 1.5, Y * 0.5, 5, seed + 1, (20, 2))
    fo = smooth(0.55, 0.8, fbm(X * 3.0, Y * 1.0, 4, seed + 3, (12, 4)))
    col = grad(np.clip(st, 0, 1), [(0, hexc('#2f8aa0')), (0.5, hexc('#7ad0dc')), (1, hexc('#e8fbff'))])
    col = comp(col, hexc('#ffffff'), fo * 0.55)
    save(name + '.png', col)


def tiles():
    tile_ashlar('jungle_stone', 512, palette=('#8c8878', '#7c7a6a', '#98937f', '#72746a'), joint='#2e2a22', rows=6, block_w=(1.0, 1.9), seed=501, wear=0.5,
                shade=0.1, moss='#4a7a26')
    tile_noise('jungle_moss', 512, base='#3c6024', var=0.3, seed=502, scale=2.0, grain=0.14, tint2='#6a7430')
    tile_noise('jungle_dirt', 512, base='#4e3d2a', var=0.28, seed=503, scale=2.0, grain=0.16, tint2='#7a6238')
    tile_cliffrock('jungle_rock', 512, seed=530)
    tile_bark('jungle_bark', 512, seed=505)
    tile_noise('jungle_leaf', 512, base='#437f2a', var=0.32, seed=506, scale=2.0, grain=0.1, tint2='#92b83e')
    tile_marble('jungle_jade', 512, '#3fb496', '#1f7a62', '#9affe0', seed=507, strata=0.0, vein_amt=0.5, grain=0.02)
    tile_wood('jungle_wood', 512, '#2a1c10', '#6a4a2a', seed=508)
    tile_metal('jungle_bronze', 512, base='#9a7a48', seed=509, rust=0.3, rust_col='#3a6a48', scale_m=2.0, plates=2, rivets=False)
    tile_noise('jungle_cloth', 512, base='#a8452a', var=0.2, seed=510, scale=1.5, grain=0.08, tint2='#6a2a18')
    tile_water('jungle_water', 512, seed=520)


def ray_tex(name='jungle_ray', W=128, H=512):
    """rayon de soleil : RGBA, profil doux en travers, dégradé vertical (plus fort en haut), grain de poussière."""
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(H)[::-1] + 0.5) / H
    U, V = np.meshgrid(u.astype(np.float32), v.astype(np.float32))
    side = np.clip(1 - np.abs(U * 2 - 1), 0, 1) ** 1.5
    vert = smooth(0.0, 0.25, V) * (0.5 + 0.5 * V)
    dust = 0.75 + 0.25 * fbm(U * 6, V * 20, 3, 5)
    alpha = np.clip(side * vert * dust * 0.26, 0, 1)
    col = np.ones(U.shape + (3,), np.float32) * hexc('#fff0b0')
    rgba = np.concatenate([col, alpha[..., None]], -1)
    a = (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(a, 'RGBA').save(os.path.join(TEXDIR, name + '.png'), optimize=True)
    print('texture', name + '.png', a.shape)


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'tiles', 'ray']
    if 'tiles' in what:
        tiles()
    if 'ray' in what:
        ray_tex()
    if 'ground' in what:
        ground()
