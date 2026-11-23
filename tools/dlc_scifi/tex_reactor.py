"""Textures de « Cœur de Réacteur » : dalles de béton, tôle d'acier, caillebotis de maintenance, anneaux de confinement lumineux."""
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from tex_lib import *

NAME = 'reactor'


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    # --- dalles de béton 4 x 3.2 m + plaques d'acier boulonnées dans la zone centrale
    pw, ph = 3.4, 3.2
    gx = (X + 26.6) % pw
    gz = (Z + 16.6) % ph
    dj = np.minimum(np.minimum(gx, pw - gx), np.minimum(gz, ph - gz))
    pid = hash01(np.floor((X + 26.6) / pw).astype(np.int64), np.floor((Z + 16.6) / ph).astype(np.int64), 7)
    n_big = fbm(X * 0.35, Z * 0.35, 4, 3)
    n_fine = fbm(X * 11, Z * 11, 4, 4)
    pores = hash01(np.floor(X * 70).astype(np.int64), np.floor(Z * 70).astype(np.int64), 9)
    base = grad(np.clip(pid * 0.6 + n_big * 0.5, 0, 1), [(0, hexc('#55524d')), (0.5, hexc('#68655e')), (1, hexc('#7a766d'))])
    base = base * (0.9 + 0.2 * n_fine[..., None]) * (0.96 + 0.08 * pores[..., None])
    stain = smooth(0.55, 0.85, fbm(X * 0.7, Z * 0.7, 5, 8))
    base = comp(base, hexc('#3c3a36'), stain * 0.35)
    oil = smooth(0.7, 0.9, fbm(X * 1.3, Z * 1.3, 5, 12)) * 0.5
    base = comp(base, hexc('#262628'), oil * 0.5)
    seam = smooth(0.05, 0.015, dj)
    base = base * (1 - 0.6 * seam[..., None])
    hgt = (-seam * 0.015 + n_fine * 0.003).astype(np.float32)
    img = base
    emis = np.zeros((GH, GW, 3), np.float32)
    R = np.hypot(X, Z)
    ang = np.arctan2(Z, X)
    # plaque centrale : acier sombre, anneaux de confinement lumineux (teal) et noyau orange
    steel = grad(np.clip(fbm(X * 3, Z * 3, 4, 21), 0, 1), [(0, hexc('#2d2f33')), (1, hexc('#4b4e54'))])
    segs = (np.abs(np.sin(ang * 12 + 0.2)) > 0.025)
    plate = c.circle(0, 0, 7.0) * segs
    img = comp(img, steel, plate)
    rim = c.ring(0, 0, 7.0, 0.25)
    img = comp(img, hexc('#c89a1a'), rim * 0.0)
    teal = np.maximum(c.ring(0, 0, 6.2, 0.14), c.ring(0, 0, 4.6, 0.1))
    teal = np.maximum(teal, c.ring(0, 0, 3.4, 0.06))
    rad_ = [(1.0 * math.cos(a), 1.0 * math.sin(a), 3.3 * math.cos(a), 3.3 * math.sin(a)) for a in [k * math.pi / 4 + math.pi / 8 for k in range(8)]]
    teal = np.maximum(teal, draw_segs(c, rad_, 0.08))
    teal = teal * (0.7 + 0.3 * smooth(0.2, 0.6, fbm(X * 2, Z * 2, 4, 31)))
    img = comp(img, hexc('#6cf0e0'), teal * 0.9)
    emis += teal[..., None] * hexc('#38e0d0') * 0.9
    core = c.circle(0, 0, 1.05)
    img = comp(img, hexc('#ffb050'), core * 0.95)
    emis += core[..., None] * hexc('#ff8a2a') * 1.0
    img = comp(img, hexc('#e08a30'), c.ring(0, 0, 2.2, 0.16) * 0.9)
    emis += c.ring(0, 0, 2.2, 0.16)[..., None] * hexc('#ff8a2a') * 0.8
    # --- bandes de danger le long des murs (fines) et couloirs de caillebotis lumineux (rail orange en dessous)
    band = smooth(0.38, 0.42, depth) * smooth(0.95, 0.9, depth)
    diag = (np.sin((X + Z) * 3.0) > 0).astype(np.float32)
    hz = np.where(diag[..., None] > 0.5, hexc('#c4981c')[None, None, :], hexc('#1c1c1e')[None, None, :]) * (0.75 + 0.35 * fbm(X * 6, Z * 6, 4, 11))[..., None]
    hz = comp(hz, base * 0.8, smooth(0.45, 0.8, fbm(X * 1.5, Z * 1.5, 5, 12)) * 0.55)
    img = comp(img, hz, band * 0.9)
    # caniveaux de refroidissement (teal) le long des zones d'équipe
    for zc in (-13.2, 13.2):
        ch = smooth(0.5, 0.45, np.abs(Z - zc)) * smooth(15.0, 14.6, np.abs(X))
        grate = (np.abs(((X * 5) % 1.0) - 0.5) < 0.38).astype(np.float32)
        img = comp(img, hexc('#202226'), ch * 0.92)
        glowc = ch * (0.5 + 0.5 * grate)
        emis += glowc[..., None] * hexc('#ff7a22') * 0.4 * (0.6 + 0.4 * fbm(X * 0.8, Z * 6, 3, 33))[..., None]
        img = comp(img, hexc('#d86a22'), glowc * 0.2)
    # --- repères d'équipe : anneaux orange (G) / teal (D), lignes de rive pointillées
    for sgn, col in ((-1, '#ff8a2a'), (1, '#38d8c8')):
        cx = 19.0 * sgn
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.22), c.ring(cx, 0, 2.5, 0.12))
        sp = [(cx + 0.7 * math.cos(a), 0.7 * math.sin(a), cx + 2.3 * math.cos(a), 2.3 * math.sin(a)) for a in [k * math.pi / 3 for k in range(6)]]
        z_ = np.maximum(z_, draw_segs(c, sp, 0.1))
        z_ = np.maximum(z_, c.dashed(13.0 * sgn, -12.5, 13.0 * sgn, 12.5, 0.16, 0.9, 0.5))
        z_ = z_ * (0.55 + 0.45 * smooth(0.25, 0.6, fbm(X * 2.2, Z * 2.2, 4, 41 + sgn)))
        img = comp(img, hexc('#1f2024'), c.circle(cx, 0, 3.7) * 0.45)
        img = comp(img, hexc(col), z_ * 0.85)
        emis += z_[..., None] * hexc(col) * 0.6
    # --- empreintes d'obstacles : plaques d'acier + anneau de danger
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        img = comp(img, hexc('#26282c'), smooth(r + 0.6, r + 0.5, d) * 0.85)
        ring_h = smooth(r + 0.5, r + 0.45, d) * smooth(r + 0.2, r + 0.25, d)
        stripes = (np.sin((np.arctan2(Z - oz, X - ox)) * 14) > 0).astype(np.float32)
        hz2 = np.where(stripes[..., None] > 0.5, hexc('#c4981c')[None, None, :], hexc('#1c1c1e')[None, None, :])
        img = comp(img, hz2, ring_h * 0.9)
        emis += (smooth(r + 0.2, r + 0.12, d) * smooth(r - 0.02, r + 0.03, d))[..., None] * hexc('#38d8c8') * 0.35
        img = comp(img, hexc('#0e0f11'), smooth(r + 0.05, r - 0.05, d))
    ao = c.contact_ao(wall=0.32, wall_len=0.9, obst=0.4, obst_len=0.6)
    img = img * (0.5 + 0.5 * ao[..., None])
    emis = emis * (0.6 + 0.4 * ao[..., None])
    savej(NAME + '_ground.jpg', img, 88)
    savep(NAME + '_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    savep(NAME + '_ground_e.png', np.clip(down(emis, 2), 0, 1))


def tiles():
    # béton brut (parois)
    X, Y = tile_coords(512, 4.0)
    n = fbm(X * 1.3, Y * 1.3, 6, 71, (5, 5))
    fine = fbm(X * 14, Y * 14, 4, 72, (56, 56))
    pores = hash01(np.floor(X * 60).astype(np.int64) % 240, np.floor(Y * 60).astype(np.int64) % 240, 73)
    col = grad(n, [(0, hexc('#57544e')), (0.5, hexc('#6e6a62')), (1, hexc('#84807a'))])
    col = col * (0.88 + 0.24 * fine[..., None]) * (0.95 + 0.1 * pores[..., None])
    col = comp(col, hexc('#38362f'), smooth(0.6, 0.85, fbm(X * 2, Y * 2, 5, 74, (8, 8))) * 0.4)
    gx = np.minimum(X % 2.0, 2.0 - X % 2.0)
    gy = np.minimum(Y % 1.0, 1.0 - Y % 1.0)
    seam = smooth(0.03, 0.008, np.minimum(gx, gy))
    col = col * (1 - 0.5 * seam[..., None])
    tile_pair('reactor_concrete', col, -seam * 0.01 + fine * 0.004, 2.0, scale_m=4.0)
    tile_metal('reactor_steel', 512, base='#74787f', seed=1601, rust=0.3, rust_col='#6e3c22', scale_m=2.0, plates=2, rivets=True)
    png2jpg('reactor_steel')
    tile_metal('reactor_dark', 512, base='#3a3d44', seed=1602, rust=0.15, rust_col='#5a3420', scale_m=2.0, plates=4, rivets=True)
    png2jpg('reactor_dark')
    tile_metal('reactor_cuve', 512, base='#a8a392', seed=1603, rust=0.45, rust_col='#7a4426', scale_m=2.0, plates=2, rivets=True)
    png2jpg('reactor_cuve')
    X, Y = tile_coords(512, 1.0)
    diag = (np.sin((X + Y) * 2 * math.pi * 2.0) > 0).astype(np.float32)
    hz = np.where(diag[..., None] > 0.5, hexc('#c89c1c')[None, None, :], hexc('#1c1c1f')[None, None, :]) * (0.8 + 0.3 * fbm(X * 8, Y * 8, 4, 81, (8, 8)))[..., None]
    hz = comp(hz, hexc('#5a4a30'), smooth(0.5, 0.8, fbm(X * 3, Y * 3, 5, 82, (3, 3))) * 0.5)
    savej('reactor_hazard.jpg', hz)
    X, Y = tile_coords(512, 1.0)
    cell_ = 0.125
    gx = np.abs(((X % cell_) / cell_) - 0.5)
    gy = np.abs(((Y % cell_) / cell_) - 0.5)
    bars = np.maximum(smooth(0.34, 0.4, gx), smooth(0.34, 0.4, gy))
    gcol = np.ones((512, 512, 3), np.float32) * hexc('#585a60') * (0.8 + 0.4 * fbm(X * 6, Y * 6, 3, 91, (6, 6)))[..., None]
    glow = (1 - bars)
    gcol = gcol * (0.2 + 0.8 * bars[..., None])
    gcol = gcol + glow[..., None] * hexc('#7a3410') * 0.7   # lueur orange sous les ajours
    savej('reactor_grate.jpg', gcol)
    savej('reactor_grate_n.jpg', to_normal(-(1 - bars) * 0.01, 2.0, 1.0 / 512, wrap=True))


if __name__ == '__main__':
    what = sys.argv[1:] or ['ground', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
