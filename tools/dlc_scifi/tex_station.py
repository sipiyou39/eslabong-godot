"""Textures de « Station Orbitale » : pont de tôle usée, bandes de danger, grilles, hublots, planète Terre peinte."""
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from tex_lib import *

NAME = 'station'


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    rg = np.random.default_rng(1101)
    # --- plaques de pont : 2.0 x 1.6 m, légèrement décalées une rangée sur deux
    pw, ph = 2.0, 1.6
    row = np.floor((Z + 16.6) / ph).astype(np.int64)
    off = 0.0 * pw
    gx = (X + 26.6 + off) % pw
    gz = (Z + 16.6) % ph
    dj = np.minimum(np.minimum(gx, pw - gx), np.minimum(gz, ph - gz))
    pid = hash01(np.floor((X + 26.6 + off) / pw).astype(np.int64), row, 5)
    base = grad(np.clip(pid * 0.8 + fbm(X * 0.4, Z * 0.4, 4, 3) * 0.4, 0, 1), [(0, hexc('#383c44')), (0.5, hexc('#474b53')), (1, hexc('#575b63'))])
    n_f = fbm(X * 9, Z * 9, 4, 4)
    brush = fbm(X * 1.2, Z * 55, 3, 6)
    base = base * (0.88 + 0.22 * n_f[..., None]) * (0.94 + 0.12 * brush[..., None])
    # usure / rouille aux joints et au pied des murs
    wear = smooth(0.5, 0.85, fbm(X * 0.7, Z * 0.7, 5, 8)) * (0.35 + 0.65 * smooth(1.6, 0.0, depth))
    base = comp(base, hexc('#6b4128'), wear * 0.5)
    seam = smooth(0.045, 0.012, dj)
    base = base * (1 - 0.6 * seam[..., None])
    bev = smooth(0.0, 0.1, dj)
    base = base * (0.9 + 0.1 * bev[..., None])
    # rivets aux quatre coins de plaque
    rv = np.zeros_like(X)
    for ox in (0.14, pw - 0.14):
        for oz in (0.14, ph - 0.14):
            d = np.hypot(gx - ox, gz - oz)
            rv = np.maximum(rv, smooth(0.045, 0.02, d))
    base = base * (1 + 0.35 * rv[..., None])
    hgt = (-seam * 0.012 + rv * 0.01 + n_f * 0.002).astype(np.float32)
    img = base
    emis = np.zeros((GH, GW, 3), np.float32)
    # --- bandes de danger le long des murs
    hz_in, hz_out = 0.5, 1.25
    band = smooth(hz_in - 0.03, hz_in + 0.03, depth) * smooth(hz_out + 0.03, hz_out - 0.03, depth)
    diag = (np.sin((X + Z) * 2.6) > 0).astype(np.float32)
    hazard = np.where(diag[..., None] > 0.5, hexc('#c89a1a')[None, None, :], hexc('#1b1b1e')[None, None, :])
    hazard = hazard * (0.75 + 0.35 * fbm(X * 6, Z * 6, 4, 11))[..., None]
    worn = smooth(0.45, 0.8, fbm(X * 1.5, Z * 1.5, 5, 12))
    hazard = comp(hazard, base * 0.8, worn * 0.55)
    img = comp(img, hazard, band * 0.95)
    # portes : plus de bande devant les sas (x=±26)
    for sgn in (-1, 1):
        gate = smooth(5.2, 4.6, np.abs(Z)) * smooth(26.0 * sgn - 6.5 * sgn, 26.0 * sgn - 5.0 * sgn, X) if sgn > 0 else smooth(5.2, 4.6, np.abs(Z)) * smooth(-26.0 + 6.5, -26.0 + 5.0, -X + 0) * 0
    # --- emblème central : anneaux de peinture ambre
    R = np.hypot(X, Z)
    ang = np.arctan2(Z, X)
    disc_ = c.circle(0, 0, 6.6)
    img = comp(img, hexc('#2f333a'), disc_ * 0.65)
    paint = hexc('#d89a30')
    pm = np.maximum(c.ring(0, 0, 6.3, 0.28), c.ring(0, 0, 3.6, 0.2))
    pm = np.maximum(pm, c.ring(0, 0, 5.5, 0.07))
    spokes = [(3.7 * math.cos(a), 3.7 * math.sin(a), 5.4 * math.cos(a), 5.4 * math.sin(a)) for a in [k * math.pi / 3 + math.pi / 6 for k in range(6)]]
    pm = np.maximum(pm, draw_segs(c, spokes, 0.34))
    # trois branches intérieures (logo)
    tri = []
    for k in range(3):
        a = k * 2 * math.pi / 3 + math.pi / 2
        tri.append((0.0, 0.0, 3.0 * math.cos(a), 3.0 * math.sin(a)))
    pm = np.maximum(pm, draw_segs(c, tri, 0.5))
    pm = np.maximum(pm, c.circle(0, 0, 0.85))
    wornp = 0.55 + 0.45 * smooth(0.25, 0.6, fbm(X * 2.0, Z * 2.0, 5, 21))
    pm = pm * wornp
    img = comp(img, paint, pm * 0.92)
    # --- repères d'équipe : cercles orange / teal avec chevrons, lignes pointillées blanches usées
    for sgn, col in ((-1, '#e0762a'), (1, '#33c4b8')):
        cx = 19.0 * sgn
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.22), c.ring(cx, 0, 2.5, 0.12))
        chev = []
        for k in range(3):
            xk = cx + (-0.9 + 0.9 * k) * -sgn * 0 + (k - 1) * 0.8
            chev.append((xk - 0.35 * sgn, -0.6, xk + 0.15 * sgn, 0.0))
            chev.append((xk + 0.15 * sgn, 0.0, xk - 0.35 * sgn, 0.6))
        z_ = np.maximum(z_, draw_segs(c, chev, 0.2))
        z_ = np.maximum(z_, c.dashed(13.0 * sgn, -12.5, 13.0 * sgn, 12.5, 0.16, 0.9, 0.5))
        z_ = z_ * (0.6 + 0.4 * smooth(0.25, 0.6, fbm(X * 2.2, Z * 2.2, 4, 31 + sgn)))
        img = comp(img, hexc(col), z_ * 0.85)
        img = comp(img, hexc('#272a31'), c.circle(cx, 0, 3.7) * 0.35 * (1 - z_))
        emis += z_[..., None] * hexc(col) * 0.35
    # --- fentes lumineuses teal autour de la plaque centrale (balises de pont)
    slots = np.zeros((GH, GW), np.float32)
    for k in range(24):
        a = k * 2 * math.pi / 24
        slots = np.maximum(slots, draw_segs(c, [(7.2 * math.cos(a), 7.2 * math.sin(a), 7.9 * math.cos(a), 7.9 * math.sin(a))], 0.11))
    img = comp(img, hexc('#6fe8de'), slots * 0.95)
    emis += slots[..., None] * hexc('#40e0d0') * 0.9
    # --- empreintes d'obstacles : plaques sombres + anneau de danger
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        plate = smooth(r + 0.62, r + 0.5, d)
        img = comp(img, hexc('#202328'), plate * 0.85)
        ring_h = smooth(r + 0.5, r + 0.45, d) * smooth(r + 0.2, r + 0.25, d)
        stripes = (np.sin((np.arctan2(Z - oz, X - ox)) * 14) > 0).astype(np.float32)
        hz2 = np.where(stripes[..., None] > 0.5, hexc('#c89a1a')[None, None, :], hexc('#1b1b1e')[None, None, :])
        img = comp(img, hz2, ring_h * 0.9)
        under = smooth(r + 0.05, r - 0.05, d)
        img = comp(img, hexc('#111214'), under)
    # --- AO de contact
    ao = c.contact_ao(wall=0.3, wall_len=0.9, obst=0.4, obst_len=0.6)
    img = img * (0.5 + 0.5 * ao[..., None])
    emis = emis * (0.6 + 0.4 * ao[..., None])
    savej(NAME + '_ground.jpg', img, 88)
    savep(NAME + '_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    savep(NAME + '_ground_e.png', np.clip(down(emis, 2), 0, 1))


def tiles():
    # tôle peinte crème usée (panneaux de coque)
    X, Y = tile_coords(512, 2.0)
    rg = np.random.default_rng(1201)
    n = fbm(X * 2, Y * 2, 5, 31, (4, 4))
    col = np.ones((512, 512, 3), np.float32) * hexc('#bdb6a2')
    col = col * (0.82 + 0.3 * n[..., None]) * (0.95 + 0.1 * fbm(X * 1.5, Y * 40, 3, 32, (3, 80))[..., None])
    pw = 1.0
    gx = np.minimum(X % pw, pw - X % pw)
    gy = np.minimum(Y % 0.5, 0.5 - Y % 0.5)
    gd = np.minimum(gx, gy)
    seam = smooth(0.016, 0.004, gd)
    col = col * (1 - 0.55 * seam[..., None])
    rv = np.zeros_like(X)
    for cx in np.arange(0.1, 2.0, 0.5):
        for cy in (0.06, 0.44):
            rv = np.maximum(rv, smooth(0.016, 0.008, np.hypot((X % 0.5) - 0.1 * 0 - (cx % 0.5), (Y % 0.5) - cy)))
    col = col * (1 + 0.25 * rv[..., None])
    wear = smooth(0.55, 0.8, fbm(X * 3, Y * 3, 5, 33, (6, 6))) * (0.4 + 0.6 * (1 - smooth(0.0, 0.12, gd)))
    col = comp(col, hexc('#7a4a2c'), wear * 0.55)
    streak = smooth(0.6, 0.85, fbm(X * 4, Y * 0.6, 4, 34, (8, 2))) * 0.25
    col = col * (1 - streak[..., None])
    tile_pair('station_cream', col, -seam * 0.006 + rv * 0.004 + n * 0.002, 2.0)
    # acier sombre, rouille
    c1 = tile_metal('station_steel_', 512, base='#6a6f78', seed=1202, rust=0.4, rust_col='#7a4326', scale_m=2.0, plates=2, norm=True)
    # tile_metal écrit des PNG : on les convertit en JPG et on supprime les PNG
    for nm in ('station_steel_',):
        for suf in ('', '_n'):
            p = os.path.join(TEXDIR, nm + suf + '.png')
            if os.path.exists(p):
                im = Image.open(p).convert('RGB')
                im.save(os.path.join(TEXDIR, 'station_steel' + suf + '.jpg'), quality=90, optimize=True)
                os.remove(p)
    c2 = tile_metal('station_dark_', 512, base='#383c44', seed=1203, rust=0.2, rust_col='#5a3420', scale_m=2.0, plates=4, rivets=True, norm=True)
    for suf in ('', '_n'):
        p = os.path.join(TEXDIR, 'station_dark_' + suf + '.png')
        if os.path.exists(p):
            im = Image.open(p).convert('RGB')
            im.save(os.path.join(TEXDIR, 'station_dark' + suf + '.jpg'), quality=90, optimize=True)
            os.remove(p)
    # bande de danger (tileable 1 m)
    X, Y = tile_coords(512, 1.0)
    diag = (np.sin((X + Y) * 2 * math.pi * 2.0) > 0).astype(np.float32)
    hz = np.where(diag[..., None] > 0.5, hexc('#cf9f1d')[None, None, :], hexc('#1c1c1f')[None, None, :]) * (0.8 + 0.3 * fbm(X * 8, Y * 8, 4, 41, (8, 8)))[..., None]
    wornh = smooth(0.5, 0.8, fbm(X * 3, Y * 3, 5, 42, (3, 3)))
    hz = comp(hz, hexc('#5a4a30'), wornh * 0.5)
    savej('station_hazard.jpg', hz)
    # caillebotis
    X, Y = tile_coords(512, 1.0)
    cell_ = 0.125
    gx = np.abs(((X % cell_) / cell_) - 0.5)
    gy = np.abs(((Y % cell_) / cell_) - 0.5)
    bars = np.maximum(smooth(0.34, 0.4, gx), smooth(0.34, 0.4, gy))
    gcol = np.ones((512, 512, 3), np.float32) * hexc('#4e5258') * (0.8 + 0.4 * fbm(X * 6, Y * 6, 3, 51, (6, 6)))[..., None]
    gcol = gcol * (0.25 + 0.75 * bars[..., None])
    gcol = comp(gcol, hexc('#6c4429'), smooth(0.55, 0.8, fbm(X * 3, Y * 3, 4, 52, (3, 3))) * 0.3)
    savej('station_grate.jpg', gcol)
    savej('station_grate_n.jpg', to_normal(-(1 - bars) * 0.01, 2.0, 1.0 / 512, wrap=True))
    # bois/cuir : tissu de siège / câblage (tapis de passerelle)
    tile_noise('station_cloth', 512, base='#5b4636', var=0.2, seed=1301, scale=1.4, grain=0.08, tint2='#3a2d24')
    im = Image.open(os.path.join(TEXDIR, 'station_cloth.png')).convert('RGB')
    im.save(os.path.join(TEXDIR, 'station_cloth.jpg'), quality=90)
    os.remove(os.path.join(TEXDIR, 'station_cloth.png'))


def earth():
    W, H = 1024, 512
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(H) + 0.5) / H
    U, V = np.meshgrid(u, v)
    lon = U * 2 * math.pi
    lat = (0.5 - V) * math.pi
    # bruit sphérique via coordonnées 3D (sans couture)
    x3, y3, z3 = np.cos(lat) * np.cos(lon), np.sin(lat), np.cos(lat) * np.sin(lon)
    def n3(f, seed, octv=6):
        # fbm 3D pauvre : somme de sinus déformés
        rg = np.random.default_rng(seed)
        out = np.zeros_like(x3)
        amp, fr = 1.0, f
        tot = 0
        for o in range(octv):
            d = rg.normal(size=(3, 3))
            ph = rg.uniform(0, 6.28, 3)
            t = (np.sin(x3 * d[0, 0] * fr + y3 * d[0, 1] * fr + z3 * d[0, 2] * fr + ph[0]) +
                 np.sin(x3 * d[1, 0] * fr * 1.3 + y3 * d[1, 1] * fr * 1.3 + z3 * d[1, 2] * fr * 1.3 + ph[1]) +
                 np.sin(x3 * d[2, 0] * fr * 1.7 + y3 * d[2, 1] * fr * 1.7 + z3 * d[2, 2] * fr * 1.7 + ph[2])) / 3
            out += amp * t
            tot += amp
            amp *= 0.5
            fr *= 2.0
        return out / tot * 0.5 + 0.5
    land = n3(2.2, 7)
    land = smooth(0.52, 0.58, land)
    ocean = grad(np.clip(0.5 + 0.5 * n3(3.0, 8), 0, 1), [(0, hexc('#10386a')), (0.5, hexc('#18508e')), (1, hexc('#256aaa'))])
    veg = n3(4.0, 9)
    ground_c = mix(hexc('#4f7a3a'), hexc('#b49a5c'), smooth(0.4, 0.65, veg))
    ground_c = ground_c * (0.85 + 0.3 * n3(9.0, 10))[..., None]
    col = mix(ocean, ground_c, land)
    ice = smooth(0.8, 0.92, np.abs(np.sin(lat)))
    col = comp(col, hexc('#eef3f8'), ice)
    cl = smooth(0.58, 0.8, n3(3.5, 11))
    col = comp(col, hexc('#f4f6fa'), cl * 0.7)
    savej('station_earth.jpg', col, 90)


if __name__ == '__main__':
    what = sys.argv[1:] or ['ground', 'tiles', 'earth']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
    if 'earth' in what:
        earth()
