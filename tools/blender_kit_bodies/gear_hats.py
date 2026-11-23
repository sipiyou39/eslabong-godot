"""Couvre-chefs, masques, coiffures. Origine = pivot tête (0,1.20,0). Colonnes : R principal, G secondaire, B accent."""
from gear_common import *

HC = -0.005  # décalage z du centre du crâne


def P_(name):
    return Part(name, HEAD_P)


def smooth(x, a, b):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def ybot_front(yf, ys, yb=None, w0=0.35, w1=0.9):
    """bord bas : yf au front, ys sur les côtés, yb (ou ys) à l'arrière."""
    if yb is None:
        yb = ys

    def f(th):
        c = math.sin(th)       # >0 devant
        sd = abs(math.cos(th))
        base = ys + (yb - ys) * smooth(-c, 0.1, 0.9)
        return base + (yf - base) * smooth(c, w0, w1)
    return f


def ring_arc(y, r_off, th0, th1, m=14, rows=HUMAN_ROWS, dy=None):
    """points d'un arc suivant la surface du crâne à la hauteur y (décalé de r_off)."""
    pts = []
    for i in range(m):
        th = math.radians(th0 + (th1 - th0) * i / (m - 1))
        x, z, rx, rz = head_surface(y if dy is None else y + dy(th), th, rows)
        cz = interp_rows(rows, y)[2]
        nx, nz = x / max(rx, 1e-3), (z - cz) / max(rz, 1e-3)
        nl = math.hypot(nx, nz) + 1e-9
        pts.append((x + r_off * nx / nl, y if dy is None else y + dy(th), z + r_off * nz / nl))
    return np.array(pts)


def band_arc(y, th0, th1, off=0.03, r=0.014, w=None, m=16, dy=None, n=8, up=(0, 1, 0)):
    pts = ring_arc(y, off, th0, th1, m, dy=dy)
    rad = [(r, r) if w is None else (w, r)] * len(pts)
    return tube(pts, rad, n=n, cap0='ngon', cap1='ngon', up=up)


def full_band(y, off=0.03, h=0.03, th=0.014, n=36):
    rows = []
    rr = interp_rows(HUMAN_ROWS, y)
    rows = [(y - h / 2, rr[0] + off, rr[1] + off, rr[2]), (y + h / 2, rr[0] + off, rr[1] + off, rr[2])]
    return rows_loft(rows, n=n, e=2.3, cap0='ngon', cap1='ngon')


def brow_ring(y0, y1, off=0.028, front=0.036, n=34, k=3):
    rows = []
    for y in np.linspace(y0, y1, k):
        rx, rz, cz = interp_rows(HUMAN_ROWS, y)
        rows.append((y, rx + off, rz + off + front * 0.5, cz + front * 0.5))
    return rows_loft(rows, n=n, e=2.3, cap0='ngon', cap1='ngon')


def spikes_ring(y, off, count, length, r, th0=0, th1=360, tilt=0.4, col_n=6):
    out = []
    for i in range(count):
        th = math.radians(th0 + (th1 - th0) * i / max(1, count - (0 if th1 - th0 < 360 else 0)))
        x, z, rx, rz = head_surface(y, th)
        n = np.array([x / rx, 0, (z - interp_rows(HUMAN_ROWS, y)[2]) / rz])
        n /= np.linalg.norm(n)
        base = np.array([x, y, z]) + n * off
        d = n + np.array([0, tilt * 2, 0])
        out.append(spike(base, base + d / np.linalg.norm(d) * length, r=r, n=col_n, bulge=0.7))
    return out


# ------------------------------------------------------------------------------------------------
def hat_none():
    p = P_("hat_none")
    p.add(Geo([(0, 0, 0), (0.001, 0, 0), (0, 0.001, 0)], [(0, 1, 2)]), SKIN, ao=1.0)
    p.note = "pièce vide (triangle de 1 mm)"
    return p


def helm_knight():
    p = P_("helm_knight")
    p.add(head_cap(ybot_front(1.475, 1.33, 1.28), g_out=0.034, k=10), R, sub=0, angle=70)
    p.add(band_arc(1.485, 10, 170, off=0.036, r=0.016, m=20), G)
    p.add(rbox(0.012, 0.075, 0.012, r=0.008).t(0, 1.425, 0.238), G)
    for sx in (-1, 1):
        p.add(rbox(0.016, 0.07, 0.085, r=0.01).rz(sx * -4).t(sx * 0.222, 1.36, 0.02), R)
        p.add(sphere(0.011, 0.011, 0.011, n=6, m=4).t(sx * 0.236, 1.40, 0.05), B)
    crest = tube(bez((0, 1.62, 0.17), (0, 1.74, 0.1), (0, 1.76, -0.1), (0, 1.58, -0.21), 10), [(0.016, 0.035)] * 10, n=8, cap0='ngon', cap1='ngon', up=(1, 0, 0))
    p.add(crest, G)
    p.add(sphere(0.19, 0.075, 0.06, n=16, m=7).rx(14).t(0, 1.31, -0.2), R)
    p.add([sphere(0.012, 0.012, 0.012, n=6, m=4).t(x, 1.64, z) for x, z in [(0.0, 0.0)]], B)
    return p


def helm_great():
    p = P_("helm_great")
    rows = [(1.17, 0.215, 0.21, 0.02), (1.22, 0.235, 0.235, 0.02), (1.40, 0.255, 0.258, 0.0), (1.55, 0.248, 0.25, -0.005),
            (1.63, 0.222, 0.225, -0.005), (1.68, 0.16, 0.165, -0.005), (1.705, 0.08, 0.085, -0.005), (1.715, 0.0, 0.0, -0.005)]
    p.add(rows_loft(rows, n=26, e=2.6, k=14), R, angle=60)
    p.add(rbox(0.12, 0.016, 0.02, r=0.01).t(0, 1.43, 0.255), SKIN, ao=0.08)     # fente de visée
    p.add(rbox(0.016, 0.2, 0.014, r=0.008).t(0, 1.40, 0.26), G)                   # barre verticale
    p.add(rbox(0.15, 0.016, 0.014, r=0.008).t(0, 1.505, 0.255), G)
    p.add([sphere(0.008, 0.008, 0.006, n=5, m=3).t(sx * 0.07, y, 0.262) for sx in (-1, 1) for y in (1.30, 1.34, 1.38)], SKIN, ao=0.1)
    p.add(torus(0.245, 0.014, 28, 6).sc(1.0, 1.0, 1.02).t(0, 1.205, 0.018), G)
    p.add(rbox(0.016, 0.03, 0.2, r=0.01).t(0, 1.72, 0.0), G)
    p.add([sphere(0.012, 0.012, 0.012, n=6, m=4).t(sx * 0.19, 1.66, 0.1) for sx in (-1, 1)], B)
    return p


def helm_horned():
    p = P_("helm_horned")
    p.add(head_cap(ybot_front(1.47, 1.37, 1.34), g_out=0.034, k=10), R, angle=70)
    p.add(band_arc(1.48, 0, 180, off=0.037, r=0.017, m=22), G)
    p.add(band_arc(1.46, 180, 360, off=0.037, r=0.017, m=22), G)
    p.add(rbox(0.014, 0.1, 0.012, r=0.008).t(0, 1.41, 0.24), G)
    for sx in (-1, 1):
        path = bez((sx * 0.2, 1.54, 0.0), (sx * 0.34, 1.52, 0.0), (sx * 0.4, 1.62, 0.06), (sx * 0.36, 1.78, 0.16), 9)
        rad = [0.052 * (1 - k / 8) ** 0.7 + 0.002 for k in range(9)]
        rad[-1] = 0.0
        p.add(tube(path, rad, n=9, cap0='ngon', up=(0, 1, 0)), B)
        p.add(torus(0.05, 0.016, 12, 6).rz(sx * 90).t(sx * 0.215, 1.54, 0.0), G)
    return p


def helm_nasal():
    p = P_("helm_nasal")
    rows = [(1.38, 0.222, 0.24, 0.02), (1.46, 0.226, 0.25, 0.02), (1.55, 0.205, 0.215, 0.0), (1.63, 0.15, 0.16, -0.01),
            (1.72, 0.07, 0.075, -0.012), (1.78, 0.0, 0.0, -0.012)]
    p.add(rows_loft(rows, n=28, e=2.2, k=14), R, angle=70)
    p.add(rows_loft([(1.40, 0.23, 0.248, 0.02), (1.46, 0.232, 0.256, 0.02)], n=28, e=2.2, cap0='ngon', cap1='ngon'), G)
    p.add(rbox(0.014, 0.1, 0.012, r=0.008).rx(-8).t(0, 1.4, 0.27), G)
    p.add(sphere(0.012, 0.012, 0.012, n=6, m=4).t(0, 1.79, -0.012), B)
    p.add(sphere(0.17, 0.05, 0.05, n=14, m=6).rx(12).t(0, 1.33, -0.195), R)
    return p


def helm_plume():
    p = P_("helm_plume")
    p.add(head_cap(ybot_front(1.48, 1.34, 1.29), g_out=0.034, k=10), R, angle=70)
    p.add(band_arc(1.49, 5, 175, off=0.037, r=0.016, m=20), B)
    p.add(rbox(0.012, 0.075, 0.012, r=0.008).t(0, 1.425, 0.238), B)
    p.add(rbox(0.03, 0.045, 0.05, r=0.012).t(0, 1.675, 0.0), B)
    path = bez((0, 1.70, 0.05), (0, 1.95, 0.0), (0, 1.9, -0.25), (0, 1.55, -0.34), 12)
    rad = [(0.03 + 0.035 * math.sin(math.pi * k / 11), 0.06 + 0.05 * math.sin(math.pi * k / 11)) for k in range(12)]
    rad[-1] = (0.0, 0.0)
    p.add(tube(path, rad, n=10, cap0='ngon', up=(1, 0, 0)), G)
    p.add(sphere(0.18, 0.07, 0.05, n=14, m=6).rx(14).t(0, 1.31, -0.2), R)
    return p


def helm_frost():
    p = P_("helm_frost")
    p.add(head_cap(ybot_front(1.46, 1.34, 1.3), g_out=0.032, k=10), R, angle=70)
    p.add(band_arc(1.475, 0, 360, off=0.036, r=0.018, m=30), G)
    for i, (a, L, r, tl) in enumerate([(90, 0.2, 0.034, 15), (60, 0.15, 0.028, 25), (120, 0.15, 0.028, 25), (30, 0.12, 0.024, 35), (150, 0.12, 0.024, 35),
                                       (270, 0.18, 0.03, 20), (240, 0.13, 0.026, 30), (300, 0.13, 0.026, 30), (0, 0.1, 0.022, 45), (180, 0.1, 0.022, 45)]):
        th = math.radians(a)
        x, z, rx, rz = head_surface(1.56, th)
        base = np.array([x * 1.0, 1.56, z])
        d = np.array([math.cos(th) * math.sin(math.radians(tl)), math.cos(math.radians(tl)), math.sin(th) * math.sin(math.radians(tl))])
        p.add(spike(base, base + d * L, r=r, n=6, bulge=0.5), B)
    p.add(spikes_ring(1.50, 0.03, 6, 0.07, 0.016, th0=200, th1=340), G)
    return p


def helm_flame():
    p = P_("helm_flame")
    p.add(head_cap(ybot_front(1.47, 1.35, 1.3), g_out=0.032, k=10), R, angle=70)
    p.add(band_arc(1.48, 0, 360, off=0.036, r=0.016, m=30), G)
    for i, (a, L, r, tl) in enumerate([(90, 0.26, 0.05, 12), (70, 0.2, 0.04, 25), (110, 0.2, 0.04, 25), (270, 0.28, 0.05, 20), (250, 0.2, 0.04, 32), (290, 0.2, 0.04, 32),
                                       (0, 0.17, 0.035, 40), (180, 0.17, 0.035, 40)]):
        th = math.radians(a)
        x, z, rx, rz = head_surface(1.57, th)
        base = np.array([x, 1.57, z])
        d = np.array([math.cos(th) * math.sin(math.radians(tl)), math.cos(math.radians(tl)), math.sin(th) * math.sin(math.radians(tl))])
        tip = base + d * L + np.array([0, 0, -0.03])
        p.add(horn(base, tip, r=r, curve_out=0.04, curve_dir=(math.cos(th) * 0.5, 0, math.sin(th) * 0.5 - 0.3), n=7, m=7), B)
    return p


def helm_skull():
    p = P_("helm_skull")
    p.add(head_cap(ybot_front(1.20, 1.36, 1.3, w0=0.2, w1=0.8), g_out=0.034, n=26, k=11, front=0.045), G, angle=70)
    for sx in (-1, 1):
        p.add(sphere(0.052, 0.05, 0.03, n=10, m=6).rz(sx * 10).t(sx * 0.082, 1.415, 0.232), SKIN, ao=0.06)      # orbites
        p.add(sphere(0.075, 0.025, 0.04, n=12, m=6).rz(sx * -16).t(sx * 0.085, 1.475, 0.222), G)                # arcade
        p.add(sphere(0.045, 0.035, 0.035, n=10, m=6).t(sx * 0.115, 1.335, 0.2), G)                               # pommette
    p.add(sphere(0.03, 0.04, 0.02, n=10, m=6).t(0, 1.345, 0.262), SKIN, ao=0.06)                                # cavité nasale
    p.add(sphere(0.026, 0.05, 0.03, n=8, m=5).t(0, 1.39, 0.248), G)
    teeth = []
    for i in range(7):
        x = -0.066 + i * 0.022
        teeth.append(lathe([(0.01, 0.0), (0.01, 0.02), (0.0, 0.024)], n=5, rz=0.8).t(x, 1.268, 0.235 - abs(x) * 0.5))
    p.add(teeth, G)
    p.add(rbox(0.08, 0.012, 0.01, r=0.004, s=1).t(0, 1.27, 0.23), SKIN, ao=0.1)
    p.add(band_arc(1.545, 0, 360, off=0.04, r=0.014, m=30), R)
    for sx in (-1, 1):
        path = bez((sx * 0.14, 1.62, 0.0), (sx * 0.24, 1.68, -0.02), (sx * 0.3, 1.8, 0.0), (sx * 0.24, 1.9, 0.06), 8)
        rad = [0.035 * (1 - k / 7) ** 0.8 + 0.002 for k in range(8)]
        rad[-1] = 0
        p.add(tube(path, rad, n=7, cap0='ngon', up=(0, 0, 1)), R)
    return p


def helm_demon():
    p = P_("helm_demon")
    p.add(head_cap(ybot_front(1.46, 1.33, 1.28), g_out=0.034, k=10), R, angle=70)
    p.add(band_arc(1.475, 0, 360, off=0.037, r=0.015, m=30), B)
    for sx in (-1, 1):
        path = bez((sx * 0.1, 1.64, 0.04), (sx * 0.16, 1.80, 0.02), (sx * 0.3, 1.88, -0.1), (sx * 0.34, 1.98, -0.3), 10)
        rad = [0.055 * (1 - k / 9) ** 0.75 + 0.002 for k in range(10)]
        rad[-1] = 0.0
        p.add(tube(path, rad, n=9, cap0='ngon', up=(0, 0, 1)), G)
        p.add(rbox(0.014, 0.08, 0.05, r=0.01).rz(sx * 8).t(sx * 0.215, 1.38, 0.05), R)
    p.add(spike((0, 1.49, 0.235), (0, 1.42, 0.28), r=0.03, n=6), B)
    p.add(spikes_ring(1.64, 0.02, 5, 0.08, 0.025, th0=250, th1=290, tilt=0.8), G)
    return p


def hood_rogue():
    p = P_("hood_rogue")
    # capuche : coque + pointe vers l'arrière + cape de col
    p.add(head_cap(ybot_front(1.50, 1.30, 1.18), g_out=0.052, g_in=0.0, k=10, bulge=0.015), R, angle=80)
    # bord de l'ouverture (rebord roulé)
    p.add(band_arc(1.495, 12, 168, off=0.052, r=0.022, m=24, dy=lambda th: -0.15 * smooth(math.cos(th) ** 2, 0.3, 1.0)), G)
    # pointe arrière
    p.add(tube(bez((0, 1.58, -0.2), (0, 1.62, -0.3), (0, 1.55, -0.38), (0, 1.38, -0.4), 8), [(0.05 * (1 - k / 7) + 0.004, 0.09 * (1 - k / 7) + 0.004) for k in range(8)], n=8, up=(1, 0, 0)), R)
    # col / mantelet
    p.add(rows_loft([(1.08, 0.3, 0.2, -0.01), (1.14, 0.29, 0.19, -0.01), (1.2, 0.2, 0.15, -0.01)], n=26, e=2.3, cap0='ngon', cap1='ngon'), R, angle=70)
    p.add(rows_loft([(1.075, 0.305, 0.205, -0.01), (1.095, 0.305, 0.205, -0.01)], n=26, e=2.3, cap0='ngon', cap1='ngon'), G, angle=70)
    return p


def hood_cowl():
    p = P_("hood_cowl")
    p.add(head_cap(ybot_front(1.47, 1.28, 1.14), g_out=0.062, g_in=0.0, k=10, bulge=0.025), R, angle=80)
    p.add(band_arc(1.465, 15, 165, off=0.064, r=0.026, m=24, dy=lambda th: -0.18 * smooth(math.cos(th) ** 2, 0.3, 1.0)), G)
    p.add(rows_loft([(1.00, 0.36, 0.25, -0.02), (1.08, 0.35, 0.24, -0.02), (1.16, 0.28, 0.18, -0.01), (1.22, 0.2, 0.15, -0.01)], n=28, e=2.3, k=8, cap0='ngon', cap1='ngon'), R, angle=70)
    p.add(rows_loft([(0.985, 0.365, 0.255, -0.02), (1.01, 0.365, 0.255, -0.02)], n=28, e=2.3, cap0='ngon', cap1='ngon'), G, angle=70)
    p.add(tube(bez((0, 1.6, -0.2), (0, 1.62, -0.3), (0, 1.5, -0.36), (0, 1.3, -0.34), 8), [(0.04 * (1 - k / 7) + 0.004, 0.1 * (1 - k / 7) + 0.004) for k in range(8)], n=8, up=(1, 0, 0)), R)
    return p


def hat_wizard():
    p = P_("hat_wizard")
    p.add(rows_loft([(1.505, 0.38, 0.38, -0.005), (1.52, 0.4, 0.4, -0.005), (1.53, 0.3, 0.3, -0.005), (1.535, 0.22, 0.22, -0.005)], n=34, e=2.0, cap0='ngon', cap1='ngon'), R, angle=70)
    brim = lathe([(0.0, 0.0), (0.2, 0.0), (0.37, 0.012), (0.42, 0.045), (0.42, 0.058), (0.37, 0.03), (0.2, 0.025), (0.0, 0.025)], n=34).t(0, 1.50, -0.005)
    p.add(brim, R, angle=70)
    rows = [(1.52, 0.225, 0.225, -0.005), (1.62, 0.2, 0.2, -0.005), (1.76, 0.15, 0.15, -0.03), (1.9, 0.09, 0.09, -0.07),
            (2.0, 0.06, 0.06, -0.12), (2.07, 0.035, 0.035, -0.19), (2.1, 0.0, 0.0, -0.25)]
    p.add(rows_loft(rows, n=24, e=2.0, k=14), R, angle=70)
    p.add(rows_loft([(1.545, 0.232, 0.232, -0.005), (1.585, 0.222, 0.222, -0.005)], n=26, e=2.0, cap0='ngon', cap1='ngon'), G)
    p.add(rbox(0.035, 0.035, 0.012, r=0.008).t(0, 1.565, 0.232), B)
    return p


def hat_witch_hunter():
    p = P_("hat_witch_hunter")
    brim = lathe([(0.0, 0.0), (0.22, 0.0), (0.36, 0.01), (0.46, 0.04), (0.5, 0.075), (0.46, 0.065), (0.36, 0.03), (0.22, 0.026), (0.0, 0.026)], n=36).t(0, 1.505, -0.005)
    p.add(brim, R, angle=70)
    p.add(rows_loft([(1.51, 0.235, 0.235, -0.005), (1.58, 0.222, 0.222, -0.005), (1.66, 0.2, 0.2, -0.005), (1.7, 0.18, 0.18, -0.005), (1.705, 0.12, 0.12, -0.005)],
                    n=28, e=2.1, k=10), R, angle=70)
    p.add(rows_loft([(1.545, 0.236, 0.236, -0.005), (1.6, 0.224, 0.224, -0.005)], n=28, e=2.1, cap0='ngon', cap1='ngon'), G)
    p.add(rbox(0.04, 0.04, 0.012, r=0.008).t(0, 1.575, 0.235), B)
    p.add(tube(bez((0.15, 1.62, 0.17), (0.28, 1.7, 0.1), (0.36, 1.8, -0.1), (0.3, 1.92, -0.22), 9), [(0.04 * math.sin(math.pi * (k + 0.5) / 9.5) + 0.004, 0.012) for k in range(9)], n=8, up=(0, 0, 1)), G)
    return p


def hat_mitre():
    p = P_("hat_mitre")
    p.add(brow_ring(1.49, 1.53, off=0.04, front=0.03), B)
    rows = [(1.50, 0.232, 0.232, -0.005), (1.58, 0.236, 0.226, -0.005), (1.68, 0.228, 0.19, -0.005), (1.79, 0.19, 0.13, -0.005), (1.9, 0.11, 0.07, -0.005), (1.97, 0.05, 0.03, -0.005),
            (1.995, 0.0, 0.0, -0.005)]
    p.add(rows_loft(rows, n=26, e=2.2, k=14), R, angle=70)
    p.add(rbox(0.02, 0.33, 0.012, r=0.008).t(0, 1.74, 0.19), B)
    p.add(rbox(0.1, 0.02, 0.012, r=0.008).t(0, 1.78, 0.19), B)
    for sx in (-1, 1):
        p.add(rbox(0.035, 0.12, 0.012, r=0.008).rz(sx * 6).t(sx * 0.14, 1.38, -0.2), B)
    p.add(rbox(0.04, 0.2, 0.012, r=0.008).t(0, 1.35, -0.215), G)
    return p


def crown():
    p = P_("crown")
    p.add(rows_loft([(1.53, 0.217, 0.217, -0.005), (1.6, 0.213, 0.213, -0.005)], n=32, e=2.0, cap0='ngon', cap1='ngon'), B)
    for i in range(8):
        th = 2 * math.pi * i / 8
        x, z = math.cos(th) * 0.212, math.sin(th) * 0.212 - 0.005
        base = np.array([x, 1.6, z])
        tip = np.array([x * 1.05, 1.6 + (0.1 if i % 2 == 0 else 0.07), z * 1.05])
        p.add(spike(base, tip, r=0.04, n=8, bulge=0.8), B)
        p.add(sphere(0.014, 0.014, 0.014, n=6, m=4).at(tip + np.array([0, 0.012, 0])), R if i % 2 == 0 else G)
    for sx in (-1, 1):
        p.add(sphere(0.03, 0.03, 0.02, n=8, m=5).t(sx * 0.0 + 0.0, 1.565, 0.222 if sx == 1 else -0.232), R)
    p.add(rows_loft([(1.52, 0.221, 0.221, -0.005), (1.54, 0.221, 0.221, -0.005)], n=32, e=2.0, cap0='ngon', cap1='ngon'), G)
    return p


def circlet():
    p = P_("circlet")
    p.add(rows_loft([(1.55, 0.208, 0.208, -0.005), (1.585, 0.204, 0.204, -0.005)], n=32, e=2.0, cap0='ngon', cap1='ngon'), B)
    p.add(sphere(0.026, 0.034, 0.016, n=10, m=7).t(0, 1.572, 0.208), R)
    p.add(spike((0.0, 1.592, 0.205), (0, 1.64, 0.2), r=0.012, n=6), B)
    for sx in (-1, 1):
        p.add(spike((sx * 0.06, 1.59, 0.2), (sx * 0.065, 1.625, 0.195), r=0.01, n=6), B)
    return p


def mask_bandit():
    p = P_("mask_bandit")
    # bandeau d'yeux
    p.add(brow_ring(1.375, 1.455, off=0.022, front=0.05), G)
    p.add(sphere(0.215, 0.05, 0.215, n=30, m=6).t(0, 1.46, 0.0), G) if False else None
    # foulard remontant sur le nez/la bouche
    rows = [(1.18, 0.1, 0.09, 0.1), (1.24, 0.17, 0.15, 0.07), (1.3, 0.2, 0.18, 0.04), (1.37, 0.208, 0.215, 0.03)]
    p.add(rows_loft(rows, n=30, e=2.3, k=8, cap0='ngon', cap1='ngon'), R, angle=70)
    p.add(sphere(0.045, 0.05, 0.045, n=10, m=6).t(0, 1.355, 0.225), R)
    p.add(tube(bez((0.2, 1.42, -0.05), (0.26, 1.35, -0.15), (0.3, 1.25, -0.2), (0.34, 1.15, -0.2), 7), [(0.035, 0.012)] * 7, n=6, up=(0, 0, 1)), R)
    p.add(tube(bez((0.2, 1.4, -0.08), (0.28, 1.3, -0.12), (0.3, 1.2, -0.12), (0.26, 1.1, -0.09), 7), [(0.03, 0.012)] * 7, n=6, up=(0, 0, 1)), R)
    p.add(sphere(0.03, 0.03, 0.03, n=8, m=5).t(0.2, 1.4, -0.07), G)
    return p


def mask_luchador():
    p = P_("mask_luchador")
    rows = [(1.19, 0.1, 0.09, 0.105), (1.25, 0.16, 0.145, 0.075), (1.31, 0.192, 0.185, 0.045), (1.37, 0.205, 0.215, 0.032), (1.44, 0.208, 0.23, 0.02),
            (1.50, 0.205, 0.225, 0.01), (1.545, 0.195, 0.205, 0.0), (1.585, 0.17, 0.18, -0.008), (1.615, 0.13, 0.14, -0.01), (1.638, 0.076, 0.085, -0.01), (1.657, 0.0, 0.0, -0.01)]
    p.add(rows_loft(rows, n=34, e=2.3, k=22, warp=0.3), R, angle=70)
    p.add(sphere(0.05, 0.06, 0.05, n=10, m=6).t(0, 1.365, 0.255), R)
    for sx in (-1, 1):
        p.add(sphere(0.066, 0.046, 0.02, n=12, m=7).rz(sx * 16).t(sx * 0.082, 1.41, 0.245), G)
        p.add(sphere(0.036, 0.022, 0.014, n=8, m=5).rz(sx * 16).t(sx * 0.082, 1.41, 0.258), SKIN, ao=0.12)
    p.add(sphere(0.075, 0.034, 0.02, n=12, m=6).t(0, 1.285, 0.222), G)
    p.add(sphere(0.042, 0.013, 0.012, n=8, m=5).t(0, 1.285, 0.238), SKIN, ao=0.15)
    star = []
    for i in range(5):
        a = math.radians(90 + i * 72)
        tip = np.array([math.cos(a) * 0.055, 1.54 + math.sin(a) * 0.055, 0.24])
        star.append(spike(np.array([0, 1.54, 0.245]), tip, r=0.02, n=6, bulge=0.9))
    p.add(star, B)
    p.add(rows_loft([(1.185, 0.098, 0.09, 0.105), (1.215, 0.12, 0.105, 0.1)], n=34, e=2.3, cap0='ngon', cap1='ngon'), G)
    return p


# --------------------------------------------------------------------------------- cheveux (G)
def hair_short():
    p = P_("hair_short")
    p.add(head_cap(ybot_front(1.535, 1.43, 1.34), g_out=0.04, k=10, bulge=0.012), G, angle=80)
    p.add([sphere(0.045, 0.03, 0.04, n=8, m=5).rz(-20 * i + 0).t(-0.1 + 0.05 * i, 1.53, 0.205 - abs(-0.1 + 0.05 * i) * 0.4) for i in range(5)], G)
    p.add([sphere(0.02, 0.06, 0.04, n=8, m=5).t(sx * 0.2, 1.42, 0.03) for sx in (-1, 1)], G)
    p.add([spike((x, 1.55, 0.205 - abs(x) * 0.5 + 0.02), (x * 1.1, 1.485, 0.235 - abs(x) * 0.5), r=0.034, n=6, bulge=0.8) for x in (-0.12, -0.06, 0.0, 0.06, 0.12)], G)
    p.add([spike((x, 1.64, z), (x * 1.5, 1.7, z - 0.05), r=0.05, n=6, bulge=0.8) for x, z in ((0.02, 0.03), (-0.04, -0.03), (0.06, -0.05))], G)
    return p


def hair_spiky():
    p = P_("hair_spiky")
    p.add(head_cap(ybot_front(1.54, 1.44, 1.36), g_out=0.032, k=9), G, angle=80)
    sp = []
    for (a, el, L) in [(90, 55, 0.22), (60, 62, 0.2), (120, 62, 0.2), (30, 70, 0.16), (150, 70, 0.16), (270, 40, 0.24), (240, 55, 0.2), (300, 55, 0.2), (0, 80, 0.13), (180, 80, 0.13), (90, 85, 0.25)]:
        th = math.radians(a)
        y = 1.54 + (1.0 - abs(el - 45) / 60) * 0.1
        x, z, rx, rz = head_surface(1.6, th)
        base = np.array([x * 0.93, 1.6, z * 0.93 + HC])
        d = np.array([math.cos(th) * math.cos(math.radians(el)), math.sin(math.radians(el)), math.sin(th) * math.cos(math.radians(el))])
        sp.append(spike(base, base + d * L, r=0.055, n=7, bulge=0.75))
    p.add(sp, G)
    return p


def hair_long():
    p = P_("hair_long")
    p.add(head_cap(ybot_front(1.535, 1.40, 1.30), g_out=0.042, k=10, bulge=0.012), G, angle=80)
    p.add([sphere(0.045, 0.03, 0.04, n=8, m=5).t(-0.1 + 0.05 * i, 1.53, 0.205 - abs(-0.1 + 0.05 * i) * 0.4) for i in range(5)], G)
    p.add(rows_loft([(1.50, 0.2, 0.07, -0.18), (1.40, 0.22, 0.08, -0.2), (1.30, 0.2, 0.08, -0.215), (1.22, 0.14, 0.06, -0.21), (1.16, 0.0, 0.0, -0.2)], n=16, e=2.2, k=8), G, angle=70)
    for i, (x, L, r) in enumerate([(-0.15, 0.5, 0.06), (-0.08, 0.6, 0.065), (0.0, 0.66, 0.07), (0.08, 0.6, 0.065), (0.15, 0.5, 0.06)]):
        path = bez((x, 1.4, -0.2), (x * 1.2, 1.2, -0.25), (x * 1.3, 1.0, -0.27 - 0.02 * (i % 2)), (x * 1.25 + 0.01, 1.34 - L, -0.26), 9)
        rad = [(r * (1 - 0.8 * (k / 8) ** 1.5) + 0.003, r * 0.8 * (1 - 0.7 * (k / 8))) for k in range(9)]
        rad[-1] = (0.0, 0.0)
        p.add(tube(path, rad, n=8, cap0='ngon', up=(0, 0, 1)), G)
    for sx in (-1, 1):
        path = bez((sx * 0.195, 1.45, 0.02), (sx * 0.235, 1.3, 0.04), (sx * 0.24, 1.15, 0.06), (sx * 0.2, 1.02, 0.08), 9)
        rad = [(0.036 * (1 - 0.7 * (k / 8) ** 2) + 0.003, 0.03) for k in range(9)]
        rad[-1] = (0.0, 0.0)
        p.add(tube(path, rad, n=8, cap0='ngon', up=(0, 0, 1)), G)
    return p


def hair_ponytail():
    p = P_("hair_ponytail")
    p.add(head_cap(ybot_front(1.535, 1.43, 1.36), g_out=0.036, k=10, bulge=0.01), G, angle=80)
    p.add([sphere(0.045, 0.03, 0.04, n=8, m=5).t(-0.1 + 0.05 * i, 1.53, 0.205 - abs(-0.1 + 0.05 * i) * 0.4) for i in range(5)], G)
    path = bez((0, 1.58, -0.2), (0, 1.66, -0.34), (0, 1.5, -0.45), (0, 1.2, -0.36), 12)
    rad = [(0.04 + 0.03 * math.sin(math.pi * k / 11) ** 0.7, 0.04 + 0.025 * math.sin(math.pi * k / 11) ** 0.7) for k in range(12)]
    rad[-1] = (0.0, 0.0)
    p.add(tube(path, rad, n=10, cap0='ngon', up=(1, 0, 0)), G)
    p.add(torus(0.045, 0.016, 12, 6).rx(70).t(0, 1.585, -0.225), R)
    return p


def bandana():
    p = P_("bandana")
    p.add(head_cap(lambda th: ybot_front(1.50, 1.44, 1.34)(th), g_out=0.032, k=8, ytop=1.60), R, angle=80) if False else None
    p.add(brow_ring(1.46, 1.55, off=0.016, front=0.04), R, angle=70)
    p.add(head_cap(lambda th: 1.545, g_out=0.026, k=8, ytop=1.648, front=0.0), R, angle=80)
    p.add(sphere(0.045, 0.045, 0.03, n=8, m=5).t(0, 1.5, -0.225), R)
    for sx in (-1, 1):
        p.add(tube(bez((sx * 0.03, 1.5, -0.23), (sx * 0.07, 1.42, -0.3), (sx * 0.1, 1.33, -0.33), (sx * 0.12, 1.24, -0.31), 7),
                   [(0.035 * (1 - k / 7 * 0.5), 0.012) for k in range(7)], n=6, up=(0, 0, 1)), R)
    p.add(brow_ring(1.455, 1.47, off=0.02, front=0.045), G)
    return p


def headband():
    p = P_("headband")
    p.add(brow_ring(1.49, 1.545, off=0.016, front=0.04), R, angle=70)
    p.add(rbox(0.032, 0.032, 0.014, r=0.006).rz(45).t(0, 1.518, 0.245), B)
    for sx in (-1, 1):
        p.add(tube(bez((sx * 0.02, 1.515, -0.205), (sx * 0.05, 1.45, -0.27), (sx * 0.08, 1.36, -0.28), (sx * 0.1, 1.27, -0.26), 7),
                   [(0.026 * (1 - k / 7 * 0.4), 0.01) for k in range(7)], n=6, up=(0, 0, 1)), R)
    return p


def goggles():
    p = P_("goggles")
    p.add(brow_ring(1.485, 1.525, off=0.016, front=0.03), G)
    for sx in (-1, 1):
        p.add(torus(0.045, 0.014, 18, 6).rx(90).t(sx * 0.07, 1.58, 0.225), B)
        p.add(lathe([(0.04, 0.0), (0.04, 0.012), (0.02, 0.022), (0.0, 0.024)], n=16).rx(90).t(sx * 0.07, 1.58, 0.215), B, ao=1.0)
        p.add(sphere(0.012, 0.012, 0.012, n=6, m=4).t(sx * 0.07, 1.58, 0.255), G)
    p.add(rbox(0.03, 0.014, 0.012, r=0.005).t(0, 1.58, 0.24), G)
    return p


def hat_feathered():
    p = P_("hat_feathered")
    brim = lathe([(0.0, 0.0), (0.22, 0.0), (0.34, 0.015), (0.42, 0.05), (0.43, 0.075), (0.38, 0.055), (0.3, 0.032), (0.22, 0.026), (0.0, 0.026)], n=34).t(0, 1.505, -0.005)
    # bord relevé d'un côté
    def lift(V):
        V = V.copy()
        m = (V[:, 0] < -0.15)
        V[m, 1] += (-V[m, 0] - 0.15) * 0.45
        m2 = (V[:, 2] < -0.2)
        V[m2, 1] += (-V[m2, 2] - 0.2) * 0.3
        return V
    brim.map(lift)
    p.add(brim, R, angle=70)
    p.add(rows_loft([(1.51, 0.235, 0.235, -0.005), (1.58, 0.222, 0.222, -0.005), (1.66, 0.2, 0.2, -0.005), (1.69, 0.18, 0.18, -0.005), (1.695, 0.1, 0.1, -0.005)],
                    n=28, e=2.1, k=10), R, angle=70)
    p.add(rows_loft([(1.545, 0.236, 0.236, -0.005), (1.6, 0.224, 0.224, -0.005)], n=28, e=2.1, cap0='ngon', cap1='ngon'), G)
    p.add(sphere(0.025, 0.025, 0.012, n=8, m=5).t(-0.2, 1.575, 0.1), B)
    for i, (dx, dy) in enumerate([(0, 0), (0.03, -0.03), (-0.03, -0.05)]):
        path = bez((-0.22, 1.6, 0.08), (-0.34 + dx, 1.8 + dy, 0.02), (-0.33 + dx, 1.86 + dy, -0.2), (-0.2 + dx, 1.75 + dy, -0.4), 10)
        rad = [(0.05 * math.sin(math.pi * (k + 0.6) / 10.6) ** 0.8 + 0.003, 0.008) for k in range(10)]
        rad[-1] = (0.0, 0.0)
        p.add(tube(path, rad, n=7, cap0='ngon', up=(1, 0, 1)), G if i != 1 else B)
    return p


HATS = [hat_none, helm_knight, helm_great, helm_horned, helm_nasal, helm_plume, helm_frost, helm_flame, helm_skull, helm_demon, hood_rogue, hood_cowl,
        hat_wizard, hat_witch_hunter, hat_mitre, crown, circlet, mask_bandit, mask_luchador, hair_long, hair_short, hair_spiky, hair_ponytail, bandana,
        headband, goggles, hat_feathered]
