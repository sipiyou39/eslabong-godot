"""Couvre-chefs sci-fi (joint tête, origine = pivot tête (0,1.20,0)). R principal, G secondaire (cheveux = G), B accent/lueur."""
from sf_common import *
from gear_hats import ybot_front, band_arc, ring_arc, smooth, brow_ring, full_band
from heads import HUMAN_ROWS

HC = -0.005


def P_(name):
    return Part(name, HEAD_P)


def ellip_edge(c, radii, y_edge, g=0.0, m=26, r=0.012, n=5):
    cx, cy, cz = c
    rx, ry, rz = radii
    pts = []
    for i in range(m + 1):
        th = 2 * math.pi * i / m
        ye = y_edge(th)
        sb = max(-0.98, min(0.98, (ye - cy) / (ry + g)))
        ph = math.asin(sb)
        cp = math.cos(ph)
        pts.append((cx + (rx + g) * cp * math.cos(th), cy + (ry + g) * sb, cz + (rz + g) * cp * math.sin(th)))
    return tube(np.array(pts), [r] * len(pts), n=n, cap0='ngon', cap1='ngon', up=(0, 1, 0))


def edge_tube(ybot, g, th0=0, th1=360, m=28, r=0.012, col_up=(0, 1, 0), n=5):
    """tube suivant le bord inférieur d'une calotte head_cap (theta en degrés)."""
    pts = []
    for i in range(m):
        th = math.radians(th0 + (th1 - th0) * i / (m - 1))
        y = ybot(th)
        x, z, rx, rz = head_surface(y, th)
        cz = interp_rows(HUMAN_ROWS, y)[2]
        nx, nz = x / max(rx, 1e-3), (z - cz) / max(rz, 1e-3)
        nl = math.hypot(nx, nz) + 1e-9
        gg = g
        pts.append((x + gg * nx / nl, y, z + gg * nz / nl))
    return tube(np.array(pts), [r] * len(pts), n=n, cap0='ngon', cap1='ngon', up=col_up)


def head_patch(th0, th1, y_lo, y_hi, g=0.034, g_in=0.004, n=14, k=8, rows=HUMAN_ROWS):
    """plaque qui épouse le crâne entre theta th0..th1 (deg) ; y_lo(u), y_hi(u) bords bas/haut selon u∈[0,1]. Solide mince."""
    def grid(gg):
        V = []
        for i in range(n):
            u = i / (n - 1)
            th = math.radians(th0 + (th1 - th0) * u)
            for j in range(k):
                t = j / (k - 1)
                y = y_lo(u) + (y_hi(u) - y_lo(u)) * t
                x, z, rx, rz = head_surface(y, th, rows)
                cz = interp_rows(rows, y)[2]
                nx, nz = x / max(rx, 1e-3), (z - cz) / max(rz, 1e-3)
                nl = math.hypot(nx, nz) + 1e-9
                V.append((x + gg * nx / nl, y, z + gg * nz / nl))
        return np.array(V)
    Vo, Vi = grid(g), grid(g_in)
    off = len(Vo)
    V = np.vstack([Vo, Vi])
    F = []
    for i in range(n - 1):
        for j in range(k - 1):
            a, b, c, d = i * k + j, (i + 1) * k + j, (i + 1) * k + j + 1, i * k + j + 1
            F.append((a, b, c, d))
    # bords : relie ext/int
    for i in range(n - 1):
        F.append((i * k, off + i * k, off + (i + 1) * k, (i + 1) * k))
        F.append((i * k + k - 1, (i + 1) * k + k - 1, off + (i + 1) * k + k - 1, off + i * k + k - 1))
    for j in range(k - 1):
        F.append((j, j + 1, off + j + 1, off + j))
        F.append(((n - 1) * k + j, off + (n - 1) * k + j, off + (n - 1) * k + j + 1, (n - 1) * k + j + 1))
    return Geo(V, F).fix()


def ellip_cap(c, radii, y_edge, n=24, k=9, g=0.0, thick=0.012, pole_flat=0.0):
    """coque ellipsoïdale (dôme) centrée en c, bord bas donné par y_edge(theta) ; theta 0=+x, 90deg=+z (devant). Solide mince."""
    cx, cy, cz = c
    rx, ry, rz = radii

    def layer(gg):
        V = []
        for i in range(n):
            th = 2 * math.pi * i / n
            ye = y_edge(th)
            sb = max(-0.98, min(0.98, (ye - cy) / (ry + gg)))
            pb = math.asin(sb)
            for j in range(k):
                ph = pb + (math.pi / 2 - pb) * (j / (k - 1))
                cp = math.cos(ph)
                V.append((cx + (rx + gg) * cp * math.cos(th), cy + (ry + gg) * math.sin(ph), cz + (rz + gg) * cp * math.sin(th)))
        return np.array(V)
    Vo, Vi = layer(g), layer(g - thick)
    off = len(Vo)
    F = []
    for i in range(n):
        i2 = (i + 1) % n
        for j in range(k - 2):
            F.append((i * k + j, i2 * k + j, i2 * k + j + 1, i * k + j + 1))
        F.append((i * k + k - 2, i2 * k + k - 2, i * k + k - 1))
        F.append((i * k, off + i * k, off + i2 * k, i2 * k))
    return Geo(np.vstack([Vo, Vi]), F).fix()


def hp(th, y, g=0.034):
    """point sur la surface du crâne (theta deg, y) décalé de g."""
    t = math.radians(th)
    x, z, rx, rz = head_surface(y, t)
    cz = interp_rows(HUMAN_ROWS, y)[2]
    nx, nz = x / max(rx, 1e-3), (z - cz) / max(rz, 1e-3)
    nl = math.hypot(nx, nz) + 1e-9
    return np.array([x + g * nx / nl, y, z + g * nz / nl])


def hnorm(th):
    t = math.radians(th)
    return np.array([math.cos(t), 0.0, math.sin(t)])


# ---------------------------------------------------------------------------------------------------------------
def helm_astronaut():
    """casque d'astronaute : col métal + dôme de verre (B) dégagé sur le visage (le shader n'a pas de transparence)."""
    p = P_("helm_astronaut")
    p.add(rows_loft([(1.16, 0.2, 0.19, 0.0), (1.215, 0.205, 0.195, 0.0), (1.265, 0.185, 0.175, 0.0)], n=24, e=2.2, cap0='ngon', cap1='ngon'), G, angle=60)
    p.add(torus(0.205, 0.022, 22, 5).sc(1.0, 1.0, 0.95).t(0, 1.215, 0.0), R)
    p.add([rbox(0.03, 0.026, 0.026, r=0.01, s=1).t(sx * 0.235, 1.215, 0.0) for sx in (-1, 1)], G, angle=60)
    p.add([cube((0.2 * math.cos(math.radians(a)), 1.215, 0.19 * math.sin(math.radians(a)) + 0.0), (0.02, 0.02, 0.02)) for a in (35, 60, 90, 120, 145)], B, ao=1.0)
    yb0 = ybot_front(1.60, 1.31, 1.27, w0=0.25, w1=0.75)
    p.add(ellip_cap((0.0, 1.43, 0.0), (0.265, 0.285, 0.272), lambda th: yb0(th), n=22, k=8, g=0.0, thick=0.012), B, angle=65)
    p.add(ellip_edge((0.0, 1.43, 0.0), (0.265, 0.285, 0.272), lambda th: yb0(th), 0.0, m=26, r=0.012), R)
    # lampe + antenne latérale
    p.add(box_at((0.2, 1.215, 0.12), (0.05, 0.05, 0.05), r=0.015, s=1), G, angle=60)
    p.add(zdisc(0.2, 1.215, 0.15, 0.015, depth=0.012, n=8), B, ao=1.0)
    p.add(cyl_between((-0.22, 1.28, -0.02), (-0.27, 1.5, -0.06), 0.008, n=6), G, angle=60)
    p.add(sphere(0.014, 0.014, 0.014, n=6, m=4).t(-0.27, 1.51, -0.06), B, ao=1.0)
    return p


def helm_visor():
    """casque tactique : coque R, rails et oreillettes G, visière enveloppante B."""
    p = P_("helm_visor")
    yb = ybot_front(1.50, 1.30, 1.23, w0=0.4, w1=0.95)
    p.add(head_cap(yb, g_out=0.036, g_in=0.004, n=26, k=8), R, angle=65)
    vis = head_patch(32, 148, lambda u: 1.375 + 0.012 * math.sin(math.pi * u), lambda u: 1.495 - 0.01 * abs(2 * u - 1), g=0.052, g_in=0.03, n=14, k=4)
    p.add(vis, B, angle=60)
    p.add(edge_tube(lambda th: 1.375 + 0.012 * math.sin((th - 32) / 116 * math.pi), 0.054, 32, 148, m=14, r=0.011), G)
    p.add(edge_tube(lambda th: 1.495 - 0.01 * abs((th - 90) / 58), 0.054, 32, 148, m=14, r=0.011), G)
    pts = np.array([hp(90, 1.57, 0.062), hp(90, 1.63, 0.052), np.array([0.0, 1.668, 0.08]), np.array([0.0, 1.678, 0.0]), np.array([0.0, 1.66, -0.12]), np.array([0.0, 1.57, -0.2])])
    p.add(ctube(pts, (0.014, 0.026), m=2, n=6, up=(1, 0, 0)), G)
    for sx in (-1, 1):
        p.add(xdisc(sx * 0.225, 1.38, 0.0, 0.07, depth=0.05, n=10), G, angle=60)
        p.add(xdisc(sx * 0.255, 1.38, 0.0, 0.04, depth=0.012, n=8), B, ao=1.0)
    p.add(tube(np.array([[0.215, 1.36, 0.05], [0.19, 1.27, 0.14], [0.08, 1.235, 0.215]]), [0.008] * 3, n=5), G)
    p.add(sphere(0.016, 0.016, 0.016, n=6, m=4).t(0.08, 1.235, 0.215), B, ao=1.0)
    p.add(sphere(0.012, 0.012, 0.012, n=6, m=4).t(0.1, 1.575, 0.1), B, ao=1.0)
    return p


def helm_cyborg():
    """demi-visage mécanique (côté +X, gauche du perso) + oeil optique ; la moitié droite du visage reste libre."""
    p = P_("helm_cyborg")

    def yb(th):
        d = (math.degrees(th) + 180) % 360 - 180            # -180..180, 90 = devant
        w = smooth(d, -10, 10) * (1.0 - smooth(d, 84, 100))   # région de plaque faciale gauche
        base = 1.50 if abs(d) > 100 else 1.56 + 0.0 * d
        if d > 100:
            base = 1.57
        if abs(d) > 120:
            base = 1.50
        return base + (1.265 - base) * w
    p.add(head_cap(yb, g_out=0.03, g_in=0.004, n=30, k=8, front=0.0), R, angle=55)
    # arête de plaque (liseré G le long du bord de visage)
    p.add(ctube(np.array([hp(95, 1.565, 0.032), hp(90, 1.52, 0.032), hp(86, 1.42, 0.034), hp(80, 1.34, 0.034), hp(70, 1.28, 0.032)]), (0.009, 0.009), m=2, n=5), G)
    # œil optique
    ex, ey, ez = 0.082, 1.405, 0.215
    p.add(zdisc(ex, ey, ez - 0.012, 0.052, depth=0.026, n=14), G, angle=60)
    p.add(zdisc(ex, ey, ez + 0.012, 0.04, depth=0.022, n=14, r2=0.85), G, angle=60)
    p.add(zdisc(ex, ey, ez + 0.032, 0.028, depth=0.01, n=12), B, ao=1.0)
    p.add(zdisc(ex, ey, ez + 0.04, 0.012, depth=0.008, n=8), SKIN, ao=0.04)
    p.add(box_at((0.09, 1.462, 0.205), (0.15, 0.024, 0.04), r=0.008, s=1, roll=-10), G, angle=60)
    # mâchoire mécanique, câbles, oreille
    p.add([cube(hp(66 + 8 * i, 1.30 - 0.012 * i, 0.034), (0.03, 0.01, 0.014)) for i in range(4)], G, angle=40)
    p.add(ctube(np.array([hp(40, 1.33, 0.04), hp(10, 1.32, 0.07), hp(-25, 1.34, 0.06), np.array([0.14, 1.3, -0.14]), np.array([0.1, 1.22, -0.15])]), 0.011, m=2, n=5), G)
    p.add(xdisc(0.222, 1.4, 0.0, 0.055, depth=0.03, n=10), G, angle=60)
    p.add(cyl_between((0.225, 1.45, 0.0), (0.27, 1.64, -0.03), 0.01, 0.006, n=6), G, angle=60)
    p.add(sphere(0.012, 0.012, 0.012, n=6, m=4).t(0.27, 1.65, -0.03), B, ao=1.0)
    p.add(bolts([hp(40, 1.48, 0.035), hp(20, 1.42, 0.035), hp(75, 1.52, 0.035)], 0.01), B, ao=1.0)
    p.add(ctube(np.array([hp(30, 1.57, 0.034), hp(0, 1.6, 0.04), hp(-30, 1.6, 0.04), np.array([0.05, 1.5, -0.2])]), 0.009, m=2, n=5), B)
    return p


def helm_pilot():
    """casque d'aviateur en cuir (R), oreillettes G, lunettes d'aviateur sur le front (G monture, B verres)."""
    p = P_("helm_pilot")
    yb = ybot_front(1.50, 1.31, 1.27, w0=0.4, w1=0.95)
    p.add(head_cap(yb, g_out=0.04, g_in=0.004, n=22, k=8), R, angle=70)
    p.add(ctube(np.array([hp(90, 1.52, 0.044), np.array([0.0, 1.66, 0.12]), np.array([0.0, 1.69, 0.0]), np.array([0.0, 1.64, -0.14]), hp(270, 1.5, 0.044)]), (0.011, 0.02), m=2, n=5), G)
    for sx in (-1, 1):
        p.add(box_at((sx * 0.225, 1.36, 0.01), (0.04, 0.17, 0.2), r=0.014, s=1), R, angle=60)
        p.add(xdisc(sx * 0.248, 1.37, 0.01, 0.062, depth=0.03, n=10), G, angle=60)
        p.add(xdisc(sx * 0.268, 1.37, 0.01, 0.03, depth=0.01, n=8), B, ao=1.0)
    p.add(tube(np.array([[0.21, 1.27, 0.02], [0.19, 1.2, 0.09], [0.07, 1.165, 0.17]]), [(0.015, 0.006)] * 3, n=5, e=3.0), G)
    p.add(tube(np.array([[-0.21, 1.27, 0.02], [-0.19, 1.2, 0.09], [-0.07, 1.165, 0.17]]), [(0.015, 0.006)] * 3, n=5, e=3.0), G)
    p.add(brow_ring(1.496, 1.526, off=0.034, front=0.012, n=24), G, angle=60)
    for sx in (-1, 1):
        cx = sx * 0.075
        p.add(torus(0.048, 0.013, 12, 4).rx(90).t(cx, 1.575, 0.228), G)
        p.add(zdisc(cx, 1.575, 0.215, 0.045, depth=0.014, n=14, r2=0.94), B, ao=1.0)
        p.add(cyl_between((cx, 1.575, 0.213), (cx, 1.575, 0.19), 0.05, 0.043, n=12), G, angle=60)
    p.add(box_at((0, 1.578, 0.235), (0.035, 0.016, 0.012), r=0.005, s=1), G)
    p.add(sphere(0.011, 0.011, 0.011, n=6, m=4).t(0, 1.67, 0.0), B, ao=1.0)
    return p


def hat_antenna():
    """petit bonnet à antennes à boules lumineuses."""
    p = P_("hat_antenna")
    yb = ybot_front(1.52, 1.45, 1.42, w0=0.5, w1=0.95)
    p.add(head_cap(yb, g_out=0.032, g_in=0.004, n=24, k=8), R, angle=75)
    p.add(edge_tube(yb, 0.034, 0, 360, m=28, r=0.017), G)
    for sx in (-1, 1):
        base = np.array([sx * 0.07, 1.64, 0.02])
        pts = [base]
        for k in range(1, 7):
            t = k / 6.0
            pts.append(base + np.array([sx * 0.11 * t, 0.2 * t, 0.015 * math.sin(t * 9) - 0.02 * t]))
        pts = np.array(pts)
        p.add(tube(pts, [0.008] * len(pts), n=5, cap0='ngon', cap1='ngon'), G)
        p.add(sphere(0.03, 0.03, 0.03, n=10, m=6).t(*pts[-1]), B, ao=1.0)
        p.add(cyl_between(base - np.array([0, 0.02, 0]), base + np.array([0, 0.03, 0]), 0.022, 0.018, n=8), G, angle=60)
    p.add(sphere(0.02, 0.02, 0.02, n=8, m=5).t(0, 1.665, 0.07), B, ao=1.0)
    return p


def hair_tech():
    """coupe rasée (G) avec crête centrale et rangées de LED éteintes (B sombre) sur les côtés."""
    p = P_("hair_tech")
    yb = ybot_front(1.52, 1.43, 1.36, w0=0.4, w1=0.95)
    p.add(head_cap(yb, g_out=0.014, g_in=0.002, n=24, k=7), G, angle=70)
    pts = np.array([[0.0, 1.57, 0.18], [0.0, 1.66, 0.12], [0.0, 1.72, 0.02], [0.0, 1.72, -0.08], [0.0, 1.66, -0.17], [0.0, 1.55, -0.2]])
    p.add(ctube(pts, (0.03, 0.045), m=2, n=6, e=2.6, up=(1, 0, 0)), G, angle=60)
    for z, y, L in [(0.14, 1.62, 0.13), (0.05, 1.68, 0.15), (-0.04, 1.71, 0.15), (-0.13, 1.67, 0.13)]:
        p.add(spike((0.0, y, z), (0.0, y + L, z - 0.025), r=0.03, n=5, bulge=0.8), G)
    leds = []
    for sx in (-1, 1):
        for row, y in enumerate((1.5, 1.56, 1.62)):
            for j in range(4):
                th = (58 - 14 * j) if sx == 1 else (122 + 14 * j)
                q = hp(th, y - 0.015 * (j / 3.0), 0.02)
                leds.append(cube(q, (0.026, 0.02, 0.026), yaw=-math.radians(th - 90) * 0.0))
    p.add(leds, B, ao=0.3, angle=40)
    p.add([xdisc(sx * 0.202, 1.4, 0.0, 0.03, depth=0.02, n=8) for sx in (-1, 1)], G, angle=60)
    return p


HATS = [helm_astronaut, helm_visor, helm_cyborg, helm_pilot, hat_antenna, hair_tech]
