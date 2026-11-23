"""Têtes grecques : origine = pivot tête (0,1.20,0). R principal, G secondaire (crêtes, cheveux), B accent (or / flammes)."""
from gk import *


def head_pt(y, ang_deg, off=0.0):
    th = math.radians(ang_deg)
    x, z, rx, rz = head_surface(y, th)
    cz = interp_rows(HUMAN_ROWS, y)[2]
    n = np.array([x / max(rx, 1e-3), 0, (z - cz) / max(rz, 1e-3)])
    n /= np.linalg.norm(n) + 1e-9
    return np.array([x, y, z]) + n * off


def crest(p, y_peak=1.92, z_front=0.19, z_back=-0.36, half=0.1, w=0.021, col=G, base_col=B):
    """cimier : socle doré collé au crâne + crinière en lame courbe."""
    base = tube(bez((0, 1.63, 0.16), (0, 1.75, 0.12), (0, 1.76, -0.1), (0, 1.60, -0.2), 8), [(0.026, 0.017)] * 8, n=6, e=3.0, cap0='ngon', cap1='ngon', up=(1, 0, 0))
    p.add(base, base_col)
    path = bez((0, 1.73, z_front), (0, y_peak, z_front - 0.05), (0, y_peak + 0.02, z_back + 0.2), (0, 1.70, z_back), 11)
    rad = [(w + 0.006 * math.sin(math.pi * k / 10), 0.035 + (half - 0.035) * math.sin(math.pi * (k + 0.3) / 10.6) ** 0.9) for k in range(11)]
    p.add(tube(path, rad, n=8, e=2.4, cap0='ngon', cap1='ngon', up=(1, 0, 0)), col)


def helm_corinthian():
    p = P_("helm_corinthian")
    p.add(head_cap(ybot_front(1.49, 1.225, 1.17, w0=0.5, w1=0.97), g_out=0.037, n=22, k=7), R, angle=70)
    p.add(brow_ring(1.455, 1.495, off=0.039, front=0.036, n=26, k=2), B)
    p.add(band_arc(1.19, 190, 350, off=0.04, r=0.014, m=10, n=5), B)
    # nasal, arcs sourciliers dorés, joues évasées
    p.add(cbox(0.016, 0.085, 0.012, c=(0, 1.415, 0.285)).rx(-4, about=(0, 1.415, 0.285)), R)
    for sx in (-1, 1):
        p.add(tube(bez((sx * 0.015, 1.455, 0.262), (sx * 0.06, 1.475, 0.262), (sx * 0.1, 1.465, 0.25), (sx * 0.14, 1.435, 0.23), 6), [0.011] * 6, n=5, cap0='ngon', cap1='ngon'), B)
        p.add(sphere(0.05, 0.07, 0.014, n=8, m=5).rz(sx * 8).t(sx * 0.2, 1.285, 0.12), R)
        p.add(sphere(0.011, 0.011, 0.011, n=6, m=4).t(sx * 0.226, 1.36, 0.09), B)
    crest(p, 1.9, 0.19, -0.36, 0.1)
    return p


def crown_laurel():
    p = P_("crown_laurel")
    leaves = []
    N = 22
    for side in (-1, 1):
        for i in range(N):
            t = (i + 0.5) / N
            a = math.radians(90 + side * (8 + 160 * t))
            y = 1.575 - 0.045 * t ** 1.4
            b = np.array([0.207 * math.cos(a), y, 0.207 * math.sin(a) - 0.005])
            tang = np.array([-math.sin(a) * side * -1, 0, math.cos(a) * side * -1])
            # direction : le long de l'arc (vers l'arrière), un peu vers l'extérieur et le haut
            tg = np.array([math.sin(a) * side, 0, -math.cos(a) * side])
            nrm = np.array([math.cos(a), 0, math.sin(a)])
            for j, sgn in enumerate((1, -1)):
                d = tg * 0.8 + nrm * 0.25 * sgn + np.array([0, 0.28 * sgn + 0.0, 0])
                d /= np.linalg.norm(d)
                L = 0.092 * (1.0 - 0.2 * t)
                leaves.append(leaf_geo(b + nrm * 0.014, b + nrm * 0.014 + d * L, 0.026, 0.006, up=nrm))
    p.add(leaves, B, angle=80)
    # tige
    pts = []
    for i in range(0, 41):
        a = math.radians(-70 + 320 * i / 40)
        pts.append((0.208 * math.cos(a), 1.567 - 0.04 * max(0.0, -math.sin(a)), 0.208 * math.sin(a) - 0.005))
    p.add(tube(np.array(pts), [0.0075] * len(pts), n=5, cap0='ngon', cap1='ngon'), G)
    # rubans à l'arrière
    for sx in (-1, 1):
        p.add(tube(bez((sx * 0.02, 1.54, -0.215), (sx * 0.06, 1.46, -0.27), (sx * 0.1, 1.38, -0.27), (sx * 0.15, 1.3, -0.24), 7),
                   [(0.024 * (1 - 0.35 * k / 6), 0.008) for k in range(7)], n=5, e=3.0, up=(0, 0, 1)), R)
    p.add(sphere(0.022, 0.022, 0.016, n=6, m=4).t(0, 1.545, -0.218), B)
    return p


def helm_winged():
    p = P_("helm_winged")
    p.add(head_cap(ybot_front(1.46, 1.37, 1.35), g_out=0.035, n=22, k=7), R, angle=70)
    p.add(band_arc(1.475, 0, 360, off=0.038, r=0.016, m=22, n=5), B)
    p.add(sphere(0.026, 0.026, 0.014, n=8, m=5).t(0, 1.52, 0.232), B)
    for sx in (-1, 1):
        base = np.array([sx * 0.222, 1.52, -0.01])
        p.add(sphere(0.03, 0.032, 0.03, n=6, m=4).at(base), B)
        fe = []
        for i in range(7):
            t = i / 6.0
            a = math.radians(80 - 96 * t)
            d = np.array([sx * 0.3, math.sin(a) * 0.9, -math.cos(a)])
            d /= np.linalg.norm(d)
            L = 0.44 - 0.1 * abs(t - 0.35)
            fe.append(leaf_geo(base + np.array([0, 0.0, -0.01 * i]), base + d * L, 0.062, 0.012, up=(sx, 0.0, 0.0), mid=0.55))
        p.add(fe, B, angle=70)
        fe = []
        for i in range(5):
            t = i / 4.0
            a = math.radians(72 - 84 * t)
            d = np.array([sx * 0.3, math.sin(a) * 0.9, -math.cos(a)])
            d /= np.linalg.norm(d)
            o = np.array([sx * 0.014, -0.02, 0.0])
            fe.append(leaf_geo(base + o, base + o + d * 0.27, 0.05, 0.011, up=(sx, 0, 0), mid=0.55))
        p.add(fe, G, angle=70)
    return p


def helm_hades():
    p = P_("helm_hades")
    p.add(head_cap(ybot_front(1.48, 1.27, 1.2, w0=0.5, w1=0.97), g_out=0.038, n=22, k=7), R, angle=70)
    p.add(band_arc(1.49, 0, 360, off=0.041, r=0.018, m=22, n=5), G)
    p.add(brow_ring(1.455, 1.50, off=0.043, front=0.04, n=26, k=2), G)
    p.add(cbox(0.016, 0.09, 0.014, c=(0, 1.40, 0.284)).rx(-4, about=(0, 1.4, 0.284)), G)
    for sx in (-1, 1):
        p.add(sphere(0.05, 0.075, 0.014, n=8, m=5).rz(sx * 6).t(sx * 0.21, 1.31, 0.1), G)
        base = np.array([sx * 0.15, 1.60, 0.03])
        tip = np.array([sx * 0.31, 1.84, -0.02])
        p.add(horn(base, tip, r=0.055, curve_out=0.05, curve_dir=(sx * 0.4, 0, -0.5), n=6, m=6), G)
        p.add(torus(0.05, 0.017, 12, 6).rz(sx * 78).t(sx * 0.165, 1.605, 0.03), B)
    for i, (z, L, lean) in enumerate([(0.14, 0.21, 0.5), (0.06, 0.3, 0.7), (-0.03, 0.34, 0.9), (-0.12, 0.28, 1.0), (-0.2, 0.2, 1.1)]):
        y0 = 1.62 + 0.02 * math.cos(z * 7) - 0.03 * max(0, -z - 0.1) * 3
        base = np.array([0.0, y0, z])
        tip = base + np.array([0.0, L, -L * 0.45 * lean])
        p.add(horn(base, tip, r=0.052, curve_out=0.05, curve_dir=(0, 0, -1), n=6, m=5), B)
    return p


def crown_sun():
    p = P_("crown_sun")
    p.add(rows_loft([(1.53, 0.218, 0.218, -0.005), (1.60, 0.214, 0.214, -0.005)], n=32, e=2.0, cap0='ngon', cap1='ngon'), B)
    p.add(rows_loft([(1.525, 0.221, 0.221, -0.005), (1.54, 0.221, 0.221, -0.005)], n=32, e=2.0, cap0='ngon', cap1='ngon'), R)
    rays = []
    N = 14
    for i in range(N):
        a = 2 * math.pi * i / N + 0.1
        c, s = math.cos(a), math.sin(a)
        base = np.array([c * 0.214, 1.585, s * 0.214 - 0.005])
        L = 0.25 if i % 2 == 0 else 0.15
        d = np.array([c * 0.62, 0.78, s * 0.62])
        d /= np.linalg.norm(d)
        rays.append(spike(base, base + d * L, r=0.034 if i % 2 == 0 else 0.026, n=5, bulge=0.7))
    p.add(rays, B)
    p.add(sphere(0.034, 0.034, 0.014, n=10, m=6).t(0, 1.575, 0.222), R)
    return p


def crown_moon():
    p = P_("crown_moon")
    p.add(rows_loft([(1.545, 0.209, 0.209, -0.005), (1.585, 0.205, 0.205, -0.005)], n=32, e=2.0, cap0='ngon', cap1='ngon'), G)
    pts = []
    m = 15
    for k in range(m):
        a = math.radians(158 + 224 * k / (m - 1))
        pts.append((0.095 * math.cos(a), 1.665 + 0.095 * math.sin(a), 0.216))
    rad = [(0.016, 0.027 * math.sin(math.pi * (k + 0.35) / (m - 0.3)) ** 0.75 + 0.003) for k in range(m)]
    rad[0] = (0.004, 0.004)
    rad[-1] = (0.004, 0.004)
    p.add(tube(np.array(pts), rad, n=8, cap0='ngon', cap1='ngon', up=(0, 0, 1)), B)
    p.add(sphere(0.022, 0.022, 0.013, n=8, m=5).t(0, 1.665, 0.216), R)
    for sx in (-1, 1):
        p.add(sphere(0.012, 0.012, 0.012, n=6, m=4).t(sx * 0.13, 1.59, 0.17), B)
        p.add(tube(bez((sx * 0.02, 1.575, -0.215), (sx * 0.05, 1.5, -0.27), (sx * 0.08, 1.42, -0.27), (sx * 0.12, 1.36, -0.25), 7),
                   [(0.02 * (1 - 0.3 * k / 6), 0.007) for k in range(7)], n=5, e=3.0, up=(0, 0, 1)), G)
    return p


def hair_beard_long():
    p = P_("hair_beard_long")
    p.add(head_cap(ybot_front(1.55, 1.40, 1.28), g_out=0.044, n=18, k=6, bulge=0.012), G, angle=80)
    p.add([sphere(0.05, 0.03, 0.04, n=6, m=3).t(-0.1 + 0.05 * i, 1.54, 0.205 - abs(-0.1 + 0.05 * i) * 0.4) for i in range(5)], G)
    # nappe arrière (coupée haut) + longues mèches ondulées
    back = rows_loft([(1.52, 0.2, 0.08, -0.18), (1.40, 0.225, 0.09, -0.2), (1.28, 0.215, 0.09, -0.225), (1.18, 0.2, 0.085, -0.24)], n=14, e=2.2, k=6)
    p.add(back, G, angle=70)
    locks = []
    for i, x in enumerate((-0.15, -0.075, 0.0, 0.075, 0.15)):
        L = 0.42 + 0.1 * math.cos(i * 1.3) + 0.05 * (1 - abs(x) / 0.17)
        path = wavy((x, 1.26, -0.235), (x * 1.1, 1.26 - L, -0.26), amp=0.022, waves=1.5, m=7, axis=(1, 0, 0), phase=i * 1.7)
        rad = [(0.036 * (1 - 0.55 * (k / 6) ** 1.6) + 0.004, 0.04 * (1 - 0.4 * (k / 6))) for k in range(7)]
        rad[-1] = (0.0, 0.0)
        locks.append(tube(path, rad, n=5, cap0='ngon', up=(0, 0, 1)))
    p.add(locks, G, angle=70)
    for sx in (-1, 1):
        path = wavy((sx * 0.197, 1.46, 0.0), (sx * 0.2, 1.0, 0.03), amp=0.025, waves=1.5, m=7, axis=(0, 0, 1), phase=sx)
        rad = [(0.036 * (1 - 0.6 * (k / 6) ** 2) + 0.004, 0.032 * (1 - 0.5 * (k / 6))) for k in range(7)]
        rad[-1] = (0.0, 0.0)
        p.add(tube(path, rad, n=6, cap0='ngon', up=(0, 0, 1)), G)
    # grande barbe majestueuse : masse + 3 mèches bouclées
    rows = [(1.40, 0.2, 0.1, 0.085), (1.34, 0.215, 0.11, 0.105), (1.27, 0.2, 0.095, 0.145), (1.19, 0.18, 0.08, 0.18), (1.11, 0.155, 0.07, 0.21),
            (1.03, 0.12, 0.06, 0.23), (0.97, 0.07, 0.045, 0.24), (0.93, 0.0, 0.0, 0.24)]
    beard = rows_loft(rows, n=16, e=2.2, k=8)
    for x in (-0.14, -0.07, 0.0, 0.07, 0.14):
        stamp(beard, (x, 1.1, 0.3), (0.012, 0.2, 0.05), -0.022, along=(0, 0, 1))
    stamp(beard, (0, 1.325, 0.19), (0.07, 0.03, 0.05), -0.03, along=(0, 0, 1))
    p.add(beard, G, angle=75)
    curls = []
    for x, L in ((-0.075, 0.1), (0.0, 0.14), (0.075, 0.1)):
        path = bez((x, 1.0, 0.235), (x + 0.03, 0.93, 0.25), (x - 0.03, 0.88, 0.25), (x, 0.84 - L * 0.3, 0.24), 7)
        rad = [(0.04 * (1 - 0.85 * (k / 6) ** 1.4) + 0.003, 0.034 * (1 - 0.8 * (k / 6))) for k in range(7)]
        rad[-1] = (0.0, 0.0)
        curls.append(tube(path, rad, n=6, cap0='ngon', up=(0, 0, 1)))
    p.add(curls, G, angle=70)
    for sx in (-1, 1):
        p.add(tube(bez((sx * 0.005, 1.315, 0.208), (sx * 0.05, 1.335, 0.225), (sx * 0.11, 1.30, 0.2), (sx * 0.15, 1.24, 0.17), 7),
                   [0.02 * (1 - 0.5 * k / 6) for k in range(7)], n=6, cap0='ngon', cap1='ngon'), G)
    return p


def hair_snakes():
    p = P_("hair_snakes")
    p.add(head_cap(ybot_front(1.545, 1.44, 1.36), g_out=0.038, n=22, k=7, bulge=0.01), G, angle=80)
    snakes, heads, eyes = [], [], []
    spec = [(90, 1.60, 0.9), (58, 1.58, 0.85), (122, 1.58, 0.85), (22, 1.54, 0.9), (158, 1.54, 0.9), (0, 1.53, 1.0), (180, 1.53, 1.0), (305, 1.55, 1.0), (235, 1.55, 1.0), (270, 1.62, 0.9)]
    for i, (ang, y, L) in enumerate(spec):
        a = math.radians(ang)
        o = np.array([math.cos(a), 0, math.sin(a)])
        perp = np.array([-math.sin(a), 0, math.cos(a)])
        x, z, rx, rz = head_surface(y, a)
        P0 = np.array([x * 0.95, y, z * 0.95 + HC])
        sgn = 1 if i % 2 == 0 else -1
        up = 1.0 if y > 1.56 else 0.55
        wp = [P0,
              P0 + o * 0.08 * L + np.array([0, 0.10 * up, 0]) + perp * 0.03 * sgn,
              P0 + o * 0.17 * L + np.array([0, 0.19 * up, 0]) - perp * 0.03 * sgn,
              P0 + o * 0.27 * L + np.array([0, 0.25 * up, 0]) + perp * 0.02 * sgn]
        path = curve(np.array(wp), 2)
        m = len(path)
        rad = [(0.034 * (1 - 0.5 * k / (m - 1)) + 0.005) for k in range(m)]
        snakes.append(tube(path, rad, n=5, cap0='ngon', cap1='ngon'))
        hd = path[-1]
        dd = path[-1] - path[-2]
        dd = dd / np.linalg.norm(dd)
        h = sphere(0.03, 0.045, 0.022, n=5, m=3)
        h.aim(dd).at(hd + dd * 0.02)
        heads.append(h)
        side = np.cross(dd, [0, 1, 0])
        side = side / (np.linalg.norm(side) + 1e-9)
        for sg in ((-1, 1) if i % 2 == 0 else ()):
            eyes.append(sphere(0.008, 0.008, 0.008, n=4, m=3).at(hd + dd * 0.035 + side * 0.02 * sg + np.array([0, 0.012, 0])))
    p.add(snakes, G, angle=70)
    p.add(heads, G, angle=70)
    p.add(eyes, B, ao=1.0)
    return p


ARES_Z = lambda y: float(np.interp(y, [1.25, 1.30, 1.35, 1.40, 1.45, 1.50], [0.237, 0.236, 0.28, 0.31, 0.29, 0.261]))


def helm_ares():
    p = P_("helm_ares")
    p.add(head_cap(ybot_front(1.19, 1.27, 1.19, w0=0.2, w1=0.8), g_out=0.036, n=22, k=8, front=0.05), R, angle=70)
    # visière : fente des yeux, évents, arête nasale
    p.add(cbox(0.075, 0.009, 0.02, c=(0, 1.425, ARES_Z(1.425) + 0.003)), SKIN, ao=0.05)
    p.add(cbox(0.017, 0.07, 0.022, c=(0, 1.355, ARES_Z(1.355) + 0.006)).rx(-6, about=(0, 1.355, 0.3)), G)
    p.add([cbox(0.005, 0.014, 0.012, c=(sx * (0.028 + 0.022 * i), 1.30, 0.245)) for sx in (-1, 1) for i in range(3)], SKIN, ao=0.06)
    p.add(cbox(0.1, 0.014, 0.02, c=(0, 1.462, ARES_Z(1.462) + 0.003)), B)
    p.add(torus(0.215, 0.014, 26, 6).sc(1.0, 1.0, 1.04).t(0, 1.205, 0.0), B)
    for sx in (-1, 1):
        p.add(sphere(0.012, 0.09, 0.1, n=8, m=5).rz(sx * -4).t(sx * 0.235, 1.35, 0.0), G)
        p.add(spike((sx * 0.232, 1.43, 0.08), (sx * 0.29, 1.47, 0.16), r=0.025, n=6), B)
    crest(p, 2.02, 0.2, -0.38, 0.12, w=0.024)
    p.add(cbox(0.026, 0.026, 0.045, c=(0, 1.77, 0.0)), B)
    return p


HEADS = [helm_corinthian, crown_laurel, helm_winged, helm_hades, crown_sun, crown_moon, hair_beard_long, hair_snakes, helm_ares]
