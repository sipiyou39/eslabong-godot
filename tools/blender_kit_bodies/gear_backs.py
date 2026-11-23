"""Dos : origine = pivot torse (0,0.78,0). Le dos du perso est à z<0."""
from gear_common import *


def B_(name):
    return Part(name, TORSO_P)


def cape(name, y_top, y_bot, w_top, w_bot, folds, hem_col=G):
    p = B_(name)

    def fn(u, v):
        w = w_top + (w_bot - w_top) * v
        zc = -0.225 - 0.07 * v ** 1.2
        x = u * w
        fold = 0.012 * math.sin(u * folds * 1.5) * v
        return (x, y_top + (y_bot - y_top) * v, zc + 0.15 * u * u * (1 - v * 0.7) + fold)
    p.add(cloth_sheet(fn, nu=15, nv=8, thick=0.016, nz=(0, 0, -1)), R, angle=60)
    p.add(cloth_sheet(lambda u, v: fn(u, 1.0 - 0.05 * v), nu=15, nv=2, thick=0.02, nz=(0, 0, -1)), hem_col, angle=60)
    p.add(torus(0.13, 0.017, 22, 6).sc(1, 1, 0.8).t(0, 1.17, -0.01), hem_col)
    p.add(sphere(0.026, 0.026, 0.015, n=8, m=5).t(0, 1.15, 0.13), B)
    p.add(tube(np.array([(-0.1, 1.17, 0.1), (0, 1.15, 0.13), (0.1, 1.17, 0.1)]), [0.012] * 3, n=6), hem_col)
    return p


def back_cape_short():
    return cape("back_cape_short", 1.15, 0.72, 0.27, 0.34, 3)


def back_cape_long():
    return cape("back_cape_long", 1.15, 0.05, 0.28, 0.42, 4)


def back_quiver():
    p = B_("back_quiver")
    a, b = np.array([-0.04, 0.72, -0.2]), np.array([0.12, 1.3, -0.27])
    d = b - a
    q = lathe([(0.075, 0.0), (0.082, 0.03), (0.088, 0.3), (0.095, 0.5), (0.098, 0.6)], n=14, rz=1.0).aim(d).at(a)
    p.add(q, R, angle=60)
    top = a + d / np.linalg.norm(d) * 0.6
    p.add(torus(0.098, 0.012, 16, 5).aim(d).at(top), G)
    p.add(torus(0.082, 0.01, 16, 5).aim(d).at(a + d / np.linalg.norm(d) * 0.1), G)
    for i, (dx, dz, L) in enumerate([(-0.03, 0.0, 0.17), (0.03, 0.02, 0.2), (0.0, -0.03, 0.15), (0.045, -0.02, 0.13), (-0.04, 0.03, 0.12)]):
        base = top + np.array([dx, 0, dz]) - d / np.linalg.norm(d) * 0.08
        tip = base + d / np.linalg.norm(d) * (0.14 + L) + np.array([dx * 1.5, 0, dz * 1.5])
        p.add(tube(np.array([base, tip]), [0.007, 0.007], n=5), G)
        p.add(spike(tip - (tip - base) / np.linalg.norm(tip - base) * 0.03, tip + (tip - base) / np.linalg.norm(tip - base) * 0.025, r=0.016, n=6, bulge=0.9), B if i % 2 == 0 else G) if False else None
        fl = base + (tip - base) * 0.35
        p.add(leaf(fl, fl + (tip - base) * 0.35, 0.02, 0.004, up=(1, 0, 0), m=4, n=5), B)
    p.add(strap([(0.18, 1.17, -0.1), (0.09, 1.0, 0.2), (-0.06, 0.88, 0.2), (-0.17, 0.8, 0.0)], w=0.025, th=0.011), G)
    p.add(rbox(0.03, 0.03, 0.014, r=0.006).t(0.09, 1.02, 0.19), B)
    return p


def wing_frame_bat(sx=1.0):
    return None


def back_wings_bat():
    p = B_("back_wings_bat")
    pts = {'root': (0.07, 1.08, -0.2), 'elbow': (0.4, 1.42, -0.3), 'wrist': (0.72, 1.62, -0.4), 't1': (1.12, 1.78, -0.5), 't2': (1.18, 1.38, -0.52),
           't3': (1.0, 1.0, -0.5), 't4': (0.66, 0.84, -0.4), 'rb': (0.1, 0.84, -0.22)}
    def bone(a, b, r0, r1, m=5):
        pa, pb = np.array(pts[a]), np.array(pts[b])
        path = np.array([pa + (pb - pa) * k / (m - 1) for k in range(m)])
        return tube(path, [r0 + (r1 - r0) * k / (m - 1) for k in range(m)], n=6, cap0='ngon', cap1='ngon')
    bones = [bone('root', 'elbow', 0.032, 0.026), bone('elbow', 'wrist', 0.026, 0.02), bone('wrist', 't1', 0.016, 0.006), bone('wrist', 't2', 0.016, 0.006),
             bone('wrist', 't3', 0.016, 0.006), bone('wrist', 't4', 0.014, 0.006)]
    for k in ('elbow', 'wrist'):
        bones.append(sphere(0.035, 0.035, 0.035, n=8, m=5).at(np.array(pts[k])))
    bones.append(spike(np.array(pts['wrist']), np.array(pts['wrist']) + np.array([0.05, 0.14, 0.0]), r=0.022, n=6))
    p.add(bones, G, angle=60)

    def mid(a, b, dep, dz=0.0):
        pa, pb = np.array(pts[a]), np.array(pts[b])
        m = (pa + pb) / 2
        v = np.array([pb[1] - pa[1], pa[0] - pb[0], 0.0])
        v /= np.linalg.norm(v) + 1e-9
        return m + v * dep + np.array([0, 0, dz])
    outline = [pts['root'], pts['elbow'], pts['wrist'], pts['t1'], tuple(mid('t1', 't2', -0.1)), pts['t2'], tuple(mid('t2', 't3', -0.12)), pts['t3'],
               tuple(mid('t3', 't4', -0.1)), pts['t4'], tuple(mid('t4', 'rb', -0.08)), pts['rb']]
    # membrane : polygone XY extrudé fin, légèrement bombé vers l'arrière
    poly = np.array([[o[0], o[1]] for o in outline])
    g = poly_lathe(poly, [(1.0, 0.0), (1.0, 0.012)])
    zs = np.array([np.interp(v[0], [0.07, 0.4, 0.72, 1.18], [-0.2, -0.3, -0.4, -0.52]) for v in g.V])
    g.V[:, 2] += zs
    # ondulation
    g.V[:, 2] += 0.02 * np.sin(g.V[:, 1] * 12) * (g.V[:, 0] > 0.3)
    p.add(g, R, angle=70)
    scale_part(p, 0.62, (0.07, 1.08, -0.2))
    return mirror_part_pair(p)


def scale_part(p, k, about):
    about = np.array(about, float)
    for pc in p.pieces:
        pc.geo.V = (pc.geo.V - about) * k + about
    return p


def mirror_part_pair(p):
    """duplique le côté gauche vers la droite dans la même pièce (ailes symétriques)."""
    q = Part(p.name, p.pivot)
    for pc in p.pieces:
        q.pieces.append(pc)
        q.pieces.append(type(pc)(pc.geo.mir(), pc.col, pc.sub, pc.angle, pc.flat, pc.ao, pc.bev))
    return q


def back_wings_angel():
    p = B_("back_wings_angel")
    feathers_main, feathers_cov, feathers_small = [], [], []
    for i in range(8):
        t = i / 7.0
        base = np.array([0.1 + 0.05 * t, 1.06 - 0.05 * t, -0.2 - 0.02 * t])
        ang = math.radians(25 + 80 * t)
        L = 0.62 + 0.38 * math.sin(math.pi * (0.1 + 0.8 * t)) * (1 - 0.3 * t)
        tip = base + np.array([math.cos(ang) * L * 0.9, math.sin(ang) * L * 0.9 * (0.9 if t < 0.5 else 1.0) - 0.3 * t, -0.28 - 0.1 * t])
        feathers_main.append(leaf(base, tip, 0.095, 0.016, up=(0, 0, 1), m=7, n=6, cd=(0, 0.05, -0.04), swap=True))
    for i in range(6):
        t = i / 5.0
        base = np.array([0.08 + 0.03 * t, 1.1, -0.2])
        ang = math.radians(35 + 65 * t)
        L = 0.38 + 0.12 * math.sin(math.pi * t)
        tip = base + np.array([math.cos(ang) * L, math.sin(ang) * L, -0.2 - 0.05 * t])
        feathers_cov.append(leaf(base, tip, 0.08, 0.014, up=(0, 0, 1), m=6, n=6, swap=True))
    for i in range(5):
        t = i / 4.0
        base = np.array([0.07, 1.12, -0.19])
        ang = math.radians(40 + 50 * t)
        L = 0.2
        tip = base + np.array([math.cos(ang) * L, math.sin(ang) * L, -0.1])
        feathers_small.append(leaf(base, tip, 0.06, 0.012, up=(0, 0, 1), m=5, n=5, swap=True))
    p.add(feathers_main, R, angle=70)
    p.add(feathers_cov, G, angle=70)
    p.add(feathers_small, R, angle=70)
    p.add(sphere(0.04, 0.045, 0.03, n=8, m=5).t(0.08, 1.1, -0.2), B)
    scale_part(p, 0.8, (0.08, 1.08, -0.2))
    return mirror_part_pair(p)


def back_wings_astral():
    p = B_("back_wings_astral")
    blades = []
    for i, (a, L, w) in enumerate([(70, 0.95, 0.07), (50, 1.05, 0.07), (30, 0.95, 0.065), (12, 0.8, 0.06), (-8, 0.62, 0.05), (95, 0.62, 0.05)]):
        base = np.array([0.1, 1.08, -0.2])
        th = math.radians(a)
        tip = base + np.array([math.cos(th) * L * 0.8, math.sin(th) * L, -0.3 - 0.04 * i])
        blades.append(leaf(base, tip, w, 0.01, up=(0, 0, 1), m=8, n=6, cd=(0.0, -0.05, -0.05), swap=True))
    p.add(blades, B, angle=70)
    cores = []
    for i, (a, L) in enumerate([(70, 0.8), (50, 0.9), (30, 0.8), (12, 0.65)]):
        base = np.array([0.1, 1.08, -0.2])
        th = math.radians(a)
        tip = base + np.array([math.cos(th) * L * 0.75, math.sin(th) * L * 0.95, -0.3 - 0.04 * i])
        cores.append(tube(np.array([base + (tip - base) * 0.05, tip - (tip - base) * 0.05]), [0.011, 0.005], n=5, cap0='ngon', cap1='ngon'))
    p.add(cores, R, angle=70)
    p.add([sphere(0.03, 0.03, 0.03, n=8, m=5).t(0.62 + 0.2 * k, 1.35 + 0.25 * k, -0.45 - 0.05 * k) for k in range(3)], R)
    p.add(torus(0.07, 0.014, 18, 6).rx(90).t(0.09, 1.08, -0.2), R)
    scale_part(p, 0.75, (0.09, 1.08, -0.2))
    return mirror_part_pair(p)


def back_tail_beast():
    p = B_("back_tail_beast")
    path = bez((0, 0.8, -0.13), (0, 0.72, -0.4), (0, 0.9, -0.62), (0, 1.22, -0.58), 12)
    rad = [(0.055 + 0.06 * math.sin(math.pi * (k + 1) / 12) ** 0.8, 0.055 + 0.06 * math.sin(math.pi * (k + 1) / 12) ** 0.8) for k in range(12)]
    rad[-1] = (0.01, 0.01)
    p.add(tube(path, rad, n=10, cap0='ngon', cap1='fan', up=(1, 0, 0)), SKIN, angle=60)
    tip = path[-1]
    ts = [tip + np.array([0.02 * math.cos(a), 0.02 * math.sin(a * 2), 0.02 * math.sin(a)]) for a in np.linspace(0, 6.28, 9)[:-1]]
    p.add(tufts(ts, (0, 1, 0.1), length=0.13, r=0.03, seed=2), SKIN)
    p.add(tufts([path[k] + np.array([0, 0.03, 0.04]) for k in (4, 6, 8)] + [path[k] + np.array([0.03, 0, 0.0]) for k in (5, 7)], (0, 1, 0.6), length=0.09, r=0.025, seed=4), SKIN)
    return p


def back_tail_demon():
    p = B_("back_tail_demon")
    path = bez((0, 0.8, -0.13), (0, 0.62, -0.42), (0, 1.0, -0.6), (0, 0.8, -0.95), 14)
    path2 = bez(path[-1], path[-1] + np.array([0, -0.15, -0.1]), path[-1] + np.array([0, -0.4, -0.05]), path[-1] + np.array([0, -0.5, 0.05]), 8)
    full = np.vstack([path, path2[1:]])
    rad = [0.045 * (1 - 0.7 * k / (len(full) - 1)) + 0.012 for k in range(len(full))]
    p.add(tube(full, rad, n=8, cap0='ngon', cap1='ngon', up=(1, 0, 0)), SKIN, angle=60)
    tip = full[-1]
    d = full[-1] - full[-3]
    d /= np.linalg.norm(d)
    # fer de lance
    spade = poly_lathe(np.array([[0, 0.0], [0.05, 0.05], [0.0, 0.16], [-0.05, 0.05]]), [(1.0, -0.008), (1.0, 0.008)])
    spade.V[:, [0, 1, 2]] = spade.V[:, [2, 1, 0]] * np.array([1, 1, 1])
    g = Geo(np.array([[0, 0, -0.008], [0.05, 0.05, -0.008], [0, 0.16, -0.008], [-0.05, 0.05, -0.008], [0, 0, 0.008], [0.05, 0.05, 0.008], [0, 0.16, 0.008], [-0.05, 0.05, 0.008]], float),
            [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]).fix()
    g.aim(d).rz(90, about=(0, 0, 0)).at(tip) if False else g.aim(d).at(tip)
    p.add(g, SKIN, angle=40)
    return p


def back_backpack():
    p = B_("back_backpack")
    p.add(rbox(0.17, 0.2, 0.09, r=0.045, s=2).t(0, 0.98, -0.26), R, angle=60)
    p.add(rbox(0.175, 0.09, 0.095, r=0.035, s=1).t(0, 1.13, -0.265), R, angle=60)
    p.add(rbox(0.17, 0.02, 0.1, r=0.01).t(0, 1.0, -0.27), G)
    p.add(rbox(0.05, 0.05, 0.05, r=0.02, s=1).t(0, 1.08, -0.325), G)
    for sx in (-1, 1):
        p.add(rbox(0.07, 0.1, 0.06, r=0.03, s=1).t(sx * 0.19, 0.88, -0.25), R, angle=60)
        p.add(rbox(0.07, 0.015, 0.065, r=0.006).t(sx * 0.19, 0.93, -0.25), G)
        p.add(strap([(sx * 0.14, 1.17, -0.17), (sx * 0.2, 1.2, 0.0), (sx * 0.16, 1.06, 0.17), (sx * 0.14, 0.88, 0.17)], w=0.026, th=0.011), G)
    bed = lathe([(0.055, -0.2), (0.06, -0.19), (0.06, 0.19), (0.055, 0.2)], n=12).rz(90).t(0, 1.27, -0.26)
    p.add(bed, G, angle=50)
    p.add([rbox(0.012, 0.012, 0.01, r=0.004, s=1).t(sx * 0.1, 1.04, -0.31) for sx in (-1, 1)], B)
    p.add(sphere(0.025, 0.025, 0.015, n=8, m=5).t(0, 0.93, -0.315), B)
    return p


def back_banner():
    p = B_("back_banner")
    p.add(tube(np.array([(0, 0.5, -0.24), (0, 2.18, -0.24)]), [0.018, 0.018], n=8, cap0='ngon', cap1='ngon'), G, angle=60)
    p.add(rbox(0.26, 0.016, 0.016, r=0.008).t(0, 2.02, -0.24), G)
    p.add(spike(np.array([0, 2.17, -0.24]), np.array([0, 2.3, -0.24]), r=0.03, n=8), B)
    p.add([sphere(0.024, 0.024, 0.024, n=8, m=5).t(sx * 0.27, 2.02, -0.24) for sx in (-1, 1)], B)

    def fn(u, v):
        return (u * 0.23, 2.0 - 0.72 * v + 0.14 * (1 - abs(u)) * v ** 4 * 0 - 0.12 * (1 - abs(u)) * max(0, v - 0.8) / 0.2 * 0 + 0.0, -0.245 + 0.02 * math.sin(v * 5 + u))
    banner = cloth_sheet(lambda u, v: (u * 0.23, 2.0 - 0.72 * v + 0.16 * (1 - abs(u)) * v ** 3 * 0.0 - 0.0, -0.245 + 0.012 * math.sin(v * 5 + u * 2)), nu=7, nv=8, thick=0.014, nz=(0, 0, -1))
    # queue d'hirondelle : on découpe en déplaçant les sommets du bas
    V = banner.V
    m = V[:, 1] < 1.35
    V[m, 1] += 0.16 * (1 - np.abs(V[m, 0]) / 0.23) * ((1.35 - V[m, 1]) / 0.05).clip(0, 1) * 0 + 0.0
    p.add(banner, R, angle=60)
    p.add(rbox(0.23, 0.02, 0.022, r=0.008).t(0, 1.31, -0.25), G)
    p.add(sphere(0.07, 0.07, 0.012, n=14, m=7).t(0, 1.75, -0.26), B)
    p.add(rbox(0.012, 0.045, 0.01, r=0.004, s=1).t(0, 1.75, -0.268), G)
    p.add(rbox(0.045, 0.012, 0.01, r=0.004, s=1).t(0, 1.75, -0.268), G)
    return p


def back_totem_stick():
    p = B_("back_totem_stick")
    a, b = np.array([-0.2, 0.55, -0.22]), np.array([0.22, 1.95, -0.3])
    p.add(tube(np.array([a, b]), [0.022, 0.022], n=8, cap0='ngon', cap1='ngon'), G, angle=60)
    d = (b - a) / np.linalg.norm(b - a)
    sk = a + d * np.linalg.norm(b - a) * 0.92
    p.add(sphere(0.07, 0.075, 0.065, n=12, m=8).at(sk + np.array([0, 0.06, 0])), G)
    p.add([sphere(0.02, 0.022, 0.016, n=6, m=4).at(sk + np.array([sx * 0.03, 0.08, 0.055])) for sx in (-1, 1)], SKIN, ao=0.08)
    p.add(rbox(0.04, 0.03, 0.03, r=0.01).at(sk + np.array([0, 0.0, 0.0])), G)
    for i, (t, col) in enumerate([(0.3, R), (0.5, B), (0.7, R)]):
        c = a + (b - a) * t
        p.add(torus(0.032, 0.012, 12, 5).aim(d).at(c), col)
    for i, dx in enumerate((-0.07, 0.0, 0.07)):
        base = sk + np.array([dx, -0.04, -0.02])
        p.add(leaf(base, base + np.array([dx * 1.5, -0.28 - 0.04 * i, -0.04]), 0.028, 0.006, up=(0, 0, 1), m=5, n=5), R if i != 1 else B)
    p.add([sphere(0.016, 0.016, 0.016, n=6, m=4).at(sk + np.array([0.0, -0.06 - 0.05 * k, 0.04])) for k in range(2)], B)
    return p


def back_tome_chained():
    p = B_("back_tome_chained")
    p.add(rbox(0.16, 0.21, 0.04, r=0.015, s=1).t(0, 1.0, -0.24), R, angle=60)
    p.add(rbox(0.145, 0.195, 0.03, r=0.01, s=1).t(0.012, 1.0, -0.225), G)
    p.add(rbox(0.012, 0.215, 0.05, r=0.006).t(-0.15, 1.0, -0.24), G)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.add(rbox(0.032, 0.032, 0.046, r=0.008, s=1).t(sx * 0.14, 1.0 + sy * 0.19, -0.24), B)
    p.add(sphere(0.04, 0.04, 0.012, n=10, m=6).t(0, 1.0, -0.275), B)
    p.add(torus(0.028, 0.008, 14, 5).rx(90).t(0, 1.0, -0.28), G)
    # chaînes : maillons le long d'un chemin qui contourne le torse
    def chain(path, col=G):
        path = np.asarray(path, float)
        links = []
        L = 0
        seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
        total = seg.sum()
        count = int(total / 0.085)
        for k in range(count):
            s = (k + 0.5) / count * total
            i = np.searchsorted(np.cumsum(seg), s)
            i = min(i, len(seg) - 1)
            t = (s - (np.cumsum(seg)[i] - seg[i])) / seg[i]
            pt = path[i] + (path[i + 1] - path[i]) * t
            d = path[i + 1] - path[i]
            lk = torus(0.02, 0.007, 8, 4).sc(1.0, 1.0, 1.5)
            lk.rx(90 if k % 2 else 0).aim(d).at(pt) if False else lk.rot(1, 90 * (k % 2)).aim(d).at(pt)
            links.append(lk)
        return links
    p.add(chain(curve([(0.14, 1.16, -0.24), (0.2, 1.17, -0.06), (0.2, 1.05, 0.14), (0.0, 0.92, 0.22), (-0.2, 0.85, 0.14)], 4)), G)
    p.add(chain(curve([(-0.14, 1.16, -0.24), (-0.2, 1.15, -0.06), (-0.18, 1.0, 0.1)], 4)), G)
    p.add(chain(curve([(-0.15, 0.84, -0.24), (-0.22, 0.82, -0.05), (-0.2, 0.84, 0.14)], 4)), G)
    return p


BACKS = [back_cape_short, back_cape_long, back_quiver, back_wings_bat, back_wings_angel, back_wings_astral, back_tail_beast, back_tail_demon, back_backpack,
         back_banner, back_totem_stick, back_tome_chained]
