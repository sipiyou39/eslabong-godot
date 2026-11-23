"""Dos grecs : origine = pivot torse (0,0.78,0). Le dos du perso est à z<0."""
from gk import *


def feather(root, ang_deg, L, w, zback=0.06, t=0.012, side=1):
    a = math.radians(ang_deg)
    d = np.array([side * math.cos(a) * L, math.sin(a) * L, -zback])
    return leaf4(root, root + d, w, t, up=(0, 0, 1))


def back_cape_royal():
    p = B_("back_cape_royal")
    y_top, y_bot, w_top, w_bot = 1.16, 0.03, 0.3, 0.5

    def fn(u, v):
        w = w_top + (w_bot - w_top) * v
        zc = -0.225 - 0.1 * v ** 1.2
        return (u * w, y_top + (y_bot - y_top) * v, zc + 0.17 * u * u * (1 - v * 0.55) + 0.02 * math.sin(u * 6.5 + 0.5) * v)
    p.add(cloth_sheet(fn, nu=15, nv=8, thick=0.018, nz=(0, 0, -1)), R, angle=60)
    p.add(cloth_sheet(lambda u, v: fn(u, 1.0 - 0.05 * v), nu=15, nv=2, thick=0.022, nz=(0, 0, -1)), B, angle=60)
    # col de cape + attaches sur les épaules + agrafe dorée
    p.add(torus(0.135, 0.02, 20, 6).sc(1, 1, 0.8).t(0, 1.165, -0.01), G)
    for sx in (-1, 1):
        p.add(strap([(sx * 0.14, 1.17, -0.17), (sx * 0.2, 1.19, 0.0), (sx * 0.15, 1.12, 0.12)], w=0.032, th=0.011), R)
        p.add(sphere(0.034, 0.034, 0.014, n=8, m=5).t(sx * 0.15, 1.115, 0.135), B)
        p.add(sphere(0.016, 0.016, 0.01, n=6, m=4).t(sx * 0.15, 1.115, 0.146), R)
    p.add(tube(bez((-0.15, 1.105, 0.145), (-0.06, 1.04, 0.19), (0.06, 1.04, 0.19), (0.15, 1.105, 0.145), 8), [0.0075] * 8, n=5, cap0='ngon', cap1='ngon'), B)
    p.add(sphere(0.025, 0.03, 0.012, n=8, m=5).t(0, 1.03, 0.2), B)
    return p


def back_wings_hermes():
    p = B_("back_wings_hermes")
    root = np.array([0.09, 1.08, -0.2])
    arm = bez(root, root + np.array([0.1, 0.12, -0.03]), root + np.array([0.2, 0.3, -0.07]), root + np.array([0.3, 0.4, -0.1]), 12)

    def at(t):
        return arm[min(int(t * 11), 11)]
    main, cov, small = [], [], []
    for i in range(7):                      # rémiges : pendent depuis le bord d'attaque, les plus longues au milieu
        t = 0.1 + 0.9 * i / 6
        ang = math.radians(-62 + 50 * t)
        L = 0.56 - 0.2 * abs(t - 0.55)
        d = np.array([math.cos(ang) * L, math.sin(ang) * L, -0.05 - 0.01 * i])
        b = at(t)
        main.append(leaf4(b, b + d, 0.07, 0.014, up=(0, 0, 1)))
    for i in range(6):
        t = 0.15 + 0.8 * i / 5
        ang = math.radians(-58 + 48 * t)
        L = 0.34 - 0.1 * abs(t - 0.5)
        b = at(t) + np.array([0, 0.012, -0.012])
        cov.append(leaf4(b, b + np.array([math.cos(ang) * L, math.sin(ang) * L, -0.04]), 0.062, 0.013, up=(0, 0, 1)))
    for i in range(5):
        t = 0.1 + 0.85 * i / 4
        ang = math.radians(-55 + 45 * t)
        b = at(t) + np.array([0, 0.03, -0.024])
        small.append(leaf_geo(b, b + np.array([math.cos(ang) * 0.17, math.sin(ang) * 0.17, -0.03]), 0.045, 0.011, up=(0, 0, 1)))
    left = [merge(main), merge(cov), merge(small), tube(arm, [0.022 * (1 - 0.5 * k / 11) for k in range(12)], n=5, cap0='ngon', cap1='ngon')]
    cols = [B, R, B, G]
    for g, c in zip(left, cols):
        p.add(g, c, angle=80)
        p.add(g.mir(), c, angle=80)
    return p


def back_sun_disk():
    p = B_("back_sun_disk")
    C = np.array([0.0, 1.43, -0.27])
    face = lathe([(0.0, -0.012), (0.3, -0.012), (0.345, 0.0), (0.33, 0.026), (0.28, 0.028), (0.0, 0.02)], n=28).rx(90).at(C)
    p.add(face, B, angle=70)
    p.add(torus(0.352, 0.02, 28, 6).rx(90).at(C + np.array([0, 0, 0.012])), B)
    p.add(torus(0.22, 0.012, 24, 5).rx(90).at(C + np.array([0, 0, 0.032])), R)
    p.add(lathe([(0.0, 0.0), (0.1, 0.0), (0.105, 0.02), (0.07, 0.05), (0.0, 0.06)], n=16).rx(90).at(C + np.array([0, 0, 0.03])), R, angle=70)
    p.add(sphere(0.04, 0.04, 0.022, n=8, m=5).at(C + np.array([0, 0, 0.09])), B)
    rays = []
    N = 16
    for i in range(N):
        a = 2 * math.pi * i / N
        c, s = math.cos(a), math.sin(a)
        L = 0.16 if i % 2 == 0 else 0.1
        b = C + np.array([c * 0.34, s * 0.34, 0.0])
        rays.append(leaf_geo(b, b + np.array([c * L, s * L, 0.0]), 0.034 if i % 2 == 0 else 0.026, 0.01, up=(0, 0, 1), mid=0.2))
    p.add(rays, B, angle=70)
    # harnais : bretelles + patte dans le dos
    p.add(tube(bez((0, 1.12, -0.22), (0, 1.18, -0.26), (0, 1.24, -0.27), (0, 1.3, -0.27), 5), [(0.04, 0.012)] * 5, n=6, e=3.0, up=(0, 0, 1)), B)
    for sx in (-1, 1):
        p.add(strap([(sx * 0.12, 1.17, -0.2), (sx * 0.2, 1.1, 0.0), (sx * 0.14, 0.95, 0.19)], w=0.026, th=0.01), R)
    return p


def back_tail_snake():
    p = B_("back_tail_snake")
    pts = np.array([(0, 0.82, -0.14), (0, 0.72, -0.3), (0.05, 0.55, -0.48), (0.17, 0.35, -0.6), (0.14, 0.17, -0.76), (-0.04, 0.07, -0.92), (-0.2, 0.05, -1.08),
                    (-0.2, 0.06, -1.28), (-0.06, 0.12, -1.36), (0.04, 0.2, -1.3)])
    path = curve(pts, 3)
    m = len(path)
    t = np.linspace(0, 1, m)
    rad = [(0.085 * (1 - t_) ** 0.7 + 0.016 * t_) for t_ in t]
    g = tube(path, rad, n=8, cap0='ngon', cap1='ngon', up=(1, 0, 0))

    def col(V):
        c = np.zeros((len(V), 3))
        stripe = (np.sin(V[:, 2] * 34 + V[:, 1] * 9) > 0.72) & (V[:, 2] < -0.3)
        c[:, 2] = np.where(stripe, 1.0, 0.0)
        c[:, 0] = np.where(stripe, 0.0, 1.0)
        return c
    p.add(g, col, angle=60)
    tip = path[-1]
    p.add(sphere(0.026, 0.03, 0.04, n=6, m=4).at(tip + np.array([0.0, 0.03, 0.03])), B)
    return p


def back_quiver_gold():
    p = B_("back_quiver_gold")
    a, b = np.array([-0.04, 0.72, -0.2]), np.array([0.12, 1.3, -0.27])
    d = b - a
    dn = d / np.linalg.norm(d)
    q = lathe([(0.072, 0.0), (0.082, 0.03), (0.088, 0.3), (0.095, 0.5), (0.098, 0.6)], n=14, rz=1.0).aim(d).at(a)
    p.add(q, B, angle=60)
    top = a + dn * 0.6
    p.add(torus(0.1, 0.014, 16, 5).aim(d).at(top), R)
    p.add(torus(0.085, 0.012, 16, 5).aim(d).at(a + dn * 0.1), R)
    p.add(torus(0.09, 0.011, 16, 5).aim(d).at(a + dn * 0.34), R)
    # bas-relief solaire
    ctr = a + dn * 0.46 + np.array([0.0, 0.0, 0.0])
    for k in range(8):
        ang = 2 * math.pi * k / 8
        pass
    for i, (dx, dz, L) in enumerate([(-0.035, 0.0, 0.17), (0.03, 0.025, 0.2), (0.0, -0.03, 0.15), (0.05, -0.02, 0.13), (-0.04, 0.03, 0.12), (0.01, 0.045, 0.16)]):
        base = top + np.array([dx, 0, dz]) - dn * 0.08
        tip = base + dn * (0.14 + L) + np.array([dx * 1.5, 0, dz * 1.5])
        p.add(tube(np.array([base, tip]), [0.0065, 0.0065], n=5), G)
        p.add(spike(tip - (tip - base) / np.linalg.norm(tip - base) * 0.02, tip + (tip - base) / np.linalg.norm(tip - base) * 0.028, r=0.013, n=5, bulge=0.8), B)
        fl = base + (tip - base) * 0.22
        p.add(leaf_geo(fl, fl + (tip - base) * 0.3, 0.02, 0.004, up=(1, 0, 0)), R)
    p.add(strap([(0.18, 1.17, -0.1), (0.09, 1.0, 0.2), (-0.06, 0.88, 0.2), (-0.17, 0.8, 0.0)], w=0.025, th=0.011), R)
    p.add(sphere(0.026, 0.026, 0.012, n=8, m=5).t(0.09, 1.02, 0.205), B)
    return p


def back_aegis():
    p = B_("back_aegis")
    rows = [(1.225, 0.14, 0.11, -0.008), (1.195, 0.26, 0.17, -0.01), (1.15, 0.38, 0.215, -0.01), (1.07, 0.445, 0.235, -0.01), (0.97, 0.45, 0.24, -0.005), (0.89, 0.44, 0.235, -0.005)]
    g = rows_loft(rows, n=22, e=2.9, k=8, cap0='ngon', cap1='ngon')
    p.add(g, R, angle=60)
    # écailles de l'égide (anneaux) + frange de serpents
    for y, r in ((1.1, 0.4), (1.0, 0.448), (0.92, 0.445)):
        p.add(torus(r, 0.014, 22, 4).sc(1.0, 1.0, 0.54).t(0, y, -0.008), G)
    sn = []
    for i in range(22):
        a = 2 * math.pi * i / 22
        c, s = math.cos(a), math.sin(a)
        base = np.array([0.44 * c, 0.9, 0.235 * s])
        d = np.array([c * 0.45, -1.0, s * 0.45])
        d /= np.linalg.norm(d)
        sn.append(spike(base, base + d * (0.16 + 0.04 * math.sin(i * 2.1)), r=0.034, n=4, bulge=0.75))
    p.add(sn, G, angle=60)
    # gorgonéion central (sur la poitrine)
    p.add(sphere(0.062, 0.062, 0.02, n=10, m=6).t(0, 1.09, 0.268), B)
    p.add([sphere(0.01, 0.01, 0.01, n=5, m=3).t(sx * 0.02, 1.1, 0.284) for sx in (-1, 1)], R, ao=0.1)
    p.add([spike(np.array([0.06 * math.cos(a), 1.09 + 0.06 * math.sin(a), 0.268]), np.array([0.1 * math.cos(a), 1.09 + 0.1 * math.sin(a), 0.275]), r=0.012, n=4) for a in [2 * math.pi * k / 10 for k in range(10)]], G)
    return p


BACKS = [back_cape_royal, back_wings_hermes, back_sun_disk, back_tail_snake, back_quiver_gold, back_aegis]
