"""Équipement de torse (origine = pivot torse (0,0.78,0)) et jupes (origine = pivot bassin (0,0.74,0))."""
from gear_common import *


def T_(name):
    return Part(name, TORSO_P)


def S_(name):
    return Part(name, PELVIS_P)


def tsh(y0=0.75, y1=1.16, gx=0.05, gz=0.036, **kw):
    return torso_shell(y0, y1, gx=gx, gz=gz, **kw)


def belt(p, y0=0.74, y1=0.80, col=G, buckle=True, gx=0.045, gz=0.04):
    rx, rz, cz = torso_r(0.77)
    p.add(rows_loft([(y0, rx + gx, rz + gz, cz), (y1, rx + gx, rz + gz, cz)], n=28, e=2.3, cap0='ngon', cap1='ngon'), col, angle=60)
    if buckle:
        p.add(rbox(0.035, 0.032, 0.014, r=0.01).t(0, 0.77, cz + rz + gz + 0.005), B)


def collar(p, y=1.15, r=0.135, col=R, h=0.07, trim=G):
    p.add(rows_loft([(y - 0.03, r + 0.04, r * 0.8 + 0.04, -0.005), (y + h, r, r * 0.8, -0.005)], n=24, e=2.2, cap0='ngon', cap1='ngon'), col, angle=60)
    p.add(torus(r + 0.015, 0.014, 24, 6).sc(1.0, 1.0, 0.8).t(0, y + h, -0.005), trim)


def armor_plate():
    p = T_("armor_plate")
    p.add(tsh(), R, angle=60)
    for sx in (-1, 1):
        p.add(sphere(0.115, 0.08, 0.05, n=12, m=7).rz(sx * -8).at(torso_pt(1.04, 90 + sx * 30, 0.05)), R)
    p.add(tube(np.array([torso_pt(0.86, 90, 0.05), torso_pt(0.95, 90, 0.06), torso_pt(1.04, 90, 0.07), torso_pt(1.12, 90, 0.055)]), [(0.016, 0.02)] * 4, n=8, cap0='ngon', cap1='ngon', up=(1, 0, 0)), G)
    for y in (0.81, 0.89):
        rx, rz, cz = torso_r(y)
        p.add(rows_loft([(y - 0.005, rx + 0.058, rz + 0.052, cz), (y + 0.07, rx + 0.048, rz + 0.044, cz)], n=24, e=2.3, cap0='ngon', cap1='ngon'), R, angle=50)
        p.add(rows_loft([(y - 0.012, rx + 0.062, rz + 0.056, cz), (y + 0.004, rx + 0.062, rz + 0.056, cz)], n=24, e=2.3, cap0='ngon', cap1='ngon'), G, angle=50)
    collar(p, 1.13, 0.15, R, 0.06, G)
    belt(p, 0.74, 0.8, G)
    p.add([sphere(0.01, 0.01, 0.01, n=6, m=4).at(torso_pt(1.1, a, 0.05)) for a in (45, 60, 120, 135)], B)
    p.add(sphere(0.025, 0.025, 0.012, n=8, m=5).at(torso_pt(1.1, 90, 0.08)), B)
    return p


def armor_leather():
    p = T_("armor_leather")
    p.add(tsh(), R, angle=60)
    for sx in (-1, 1):
        p.add(tube(np.array([torso_pt(1.14, 90 - sx * 16, 0.04), torso_pt(1.0, 90 - sx * 8, 0.04), torso_pt(0.85, 90 - sx * 5, 0.04), torso_pt(0.77, 90 - sx * 4, 0.04)]),
                   [(0.014, 0.012)] * 4, n=6, up=(1, 0, 0)), G)
        p.add(strap([torso_pt(1.13, 90 + sx * 25, 0.045), torso_pt(1.0, 90 - sx * 10, 0.045), torso_pt(0.88, 90 - sx * 60, 0.045)], w=0.022, th=0.01), G) if False else None
    p.add(strap([torso_pt(1.13, 60, 0.045), torso_pt(1.0, 100, 0.045), torso_pt(0.9, 135, 0.045)], w=0.02, th=0.01), G)
    p.add(strap([torso_pt(1.13, 120, 0.045), torso_pt(1.0, 80, 0.045), torso_pt(0.9, 45, 0.045)], w=0.02, th=0.01), G)
    collar(p, 1.14, 0.14, R, 0.05, G)
    belt(p, 0.75, 0.81, G)
    p.add([rbox(0.012, 0.012, 0.008, r=0.003, s=1).at(torso_pt(y, 90, 0.052)) for y in (0.88, 0.95, 1.02)], B)
    p.add([sphere(0.02, 0.025, 0.015, n=8, m=5).at(torso_pt(0.86, a, 0.06)) for a in (30, 150)], G)
    return p


def sash(p, col=G, y=0.80, knot=True):
    rx, rz, cz = torso_r(y)
    p.add(rows_loft([(y - 0.04, rx + 0.06, rz + 0.055, cz), (y + 0.04, rx + 0.055, rz + 0.05, cz)], n=28, e=2.3, cap0='ngon', cap1='ngon'), col, angle=60)
    if knot:
        p.add(sphere(0.04, 0.035, 0.03, n=10, m=6).t(0.08, y, cz + rz + 0.065), B)
        for sx, L in ((1, 0.2), (0.4, 0.14)):
            p.add(tube(bez((0.08, y - 0.02, cz + rz + 0.07), (0.1 + 0.05 * sx, y - 0.1, cz + rz + 0.08), (0.12, y - 0.18, cz + rz + 0.07), (0.1 + 0.05 * sx, y - 0.18 - L * 0.4, cz + rz + 0.06), 7),
                       [(0.026, 0.01)] * 7, n=6, up=(0, 0, 1)), col)


def armor_robe():
    p = T_("armor_robe")
    p.add(tsh(0.74, 1.16, gx=0.045, gz=0.04, sx=1.0), R, angle=60)
    collar(p, 1.14, 0.14, R, 0.04, G)
    # col en V
    for sx in (-1, 1):
        path = np.array([torso_pt(1.17, 90 + sx * -40, 0.045), torso_pt(1.07, 90 - sx * 20, 0.05), torso_pt(0.97, 90, 0.052)])
        p.add(tube(curve(path, 3), [(0.022, 0.02)] * 7, n=8, up=(1, 0, 0)), G)
    sash(p, G, 0.82)
    return p


def armor_robe_long():
    p = T_("armor_robe_long")
    p.add(tsh(0.74, 1.17, gx=0.05, gz=0.045), R, angle=60)
    p.add(rows_loft([(1.12, 0.17, 0.14, -0.005), (1.20, 0.14, 0.12, -0.005), (1.27, 0.125, 0.11, -0.005)], n=24, e=2.2, k=3, cap0='ngon', cap1='ngon'), R, angle=60)
    p.add(torus(0.135, 0.016, 24, 6).t(0, 1.27, -0.005), G)
    p.add(torus(0.17, 0.016, 24, 6).sc(1, 1, 0.85).t(0, 1.12, -0.005), G)
    p.add(tube(curve(np.array([torso_pt(1.13, 90, 0.05), torso_pt(1.0, 90, 0.055), torso_pt(0.82, 90, 0.055)]), 3), [(0.03, 0.01)] * 7, n=6, e=3, up=(1, 0, 0)), G)
    p.add([sphere(0.012, 0.012, 0.012, n=6, m=4).at(torso_pt(y, 90, 0.06)) for y in (1.06, 0.98, 0.9)], B)
    sash(p, G, 0.8, knot=False)
    p.add(rbox(0.03, 0.03, 0.014, r=0.008).t(0, 1.12, 0.215), B)
    return p


def armor_tabard():
    p = T_("armor_tabard")
    p.add(tsh(0.75, 1.15), R, angle=60)
    # plastron de tabard devant (panneau) + emblème
    rx, rz, cz = torso_r(0.95)
    p.add(rbox(0.13, 0.19, 0.012, r=0.008, s=1, d=(1, 1, 1)).t(0, 0.95, cz + rz + 0.045), R)
    p.add(sphere(0.065, 0.065, 0.014, n=14, m=7).t(0, 1.0, cz + rz + 0.057), B)
    p.add([rbox(0.012, 0.05, 0.01, r=0.004, s=1).t(0, 1.0, cz + rz + 0.068), rbox(0.05, 0.012, 0.01, r=0.004, s=1).t(0, 1.0, cz + rz + 0.068)], R)
    for sx in (-1, 1):
        p.add(strap([torso_pt(1.17, 90 + sx * 50, 0.04), torso_pt(1.15, 90 + sx * 25, 0.045), torso_pt(1.0, 90 + sx * 28, 0.045)], w=0.03, th=0.01), R) if False else None
        p.add(rbox(0.012, 0.19, 0.012, r=0.005, s=1).t(sx * 0.13, 0.95, cz + rz + 0.046), G)
    collar(p, 1.14, 0.14, R, 0.04, G)
    belt(p, 0.75, 0.8, G)
    return p


def scale_rows(p, ys, col, edge, gx=0.045, gz=0.04, teeth=14, amp=0.01):
    for k, y in enumerate(ys):
        rx, rz, cz = torso_r(y)
        n = teeth * 2
        rings = []
        for yy, w in ((y + 0.055, 0.0), (y + 0.02, 0.0), (y - 0.01, 1.0), (y - 0.035, 1.0)):
            th = 2 * np.pi * np.arange(n) / n
            sc = 1.0 + (0.012 if yy > y else 0.0)
            pts = sec(yy, rx + gx + (0.006 if w == 0 else 0.0), rz + gz + 0.012 + (0.006 if w == 0 else 0.0), 0.0, cz + 0.006, n, 2.3)
            if w:
                pts[:, 1] -= amp * (0.5 + 0.5 * np.cos(th * teeth)) * (1.0 if yy < y - 0.02 else 0.6)
            rings.append(pts)
        p.add(loft(rings, 'ngon', 'ngon'), col, angle=40)


def armor_scale():
    p = T_("armor_scale")
    p.add(tsh(0.78, 1.15), R, angle=60)
    scale_rows(p, [1.08, 1.0, 0.92, 0.84], R, G)
    collar(p, 1.13, 0.15, R, 0.05, G)
    belt(p, 0.74, 0.79, G)
    p.add([sphere(0.01, 0.01, 0.01, n=6, m=4).at(torso_pt(1.13, a, 0.05)) for a in range(30, 160, 25)], B)
    return p


def armor_wraps():
    p = T_("armor_wraps")
    n = 9
    for a0, a1 in ((20, 160), (160, 20), (200, 340), (340, 200)):
        pts = [torso_pt(1.14 - 0.34 * t, a0 + (a1 - a0) * t, 0.022) for t in np.linspace(0, 1, n)]
        p.add(tube(curve(pts, 3), [(0.03, 0.012)] * (len(pts) * 3 - 2), n=8, e=2.6, up=(0, 1, 0), cap0='ngon', cap1='ngon'), R, angle=70)
    for y in (0.8, 0.85):
        rx, rz, cz = torso_r(y)
        p.add(rows_loft([(y - 0.02, rx + 0.03, rz + 0.028, cz), (y + 0.02, rx + 0.03, rz + 0.028, cz)], n=28, e=2.3, cap0='ngon', cap1='ngon'), G, angle=60)
    p.add(sphere(0.03, 0.03, 0.02, n=8, m=5).at(torso_pt(1.05, 90, 0.04)), B)
    p.add(tube(bez((0.1, 0.8, 0.2), (0.14, 0.7, 0.22), (0.12, 0.6, 0.2), (0.16, 0.5, 0.2), 6), [(0.022, 0.01)] * 6, n=6, up=(0, 0, 1)), R)
    return p


def armor_coat():
    p = T_("armor_coat")
    p.add(tsh(0.74, 1.16, gx=0.045, gz=0.04), R, angle=60)
    # revers
    for sx in (-1, 1):
        lap = cloth_sheet(lambda u, v, sx=sx: (sx * (0.02 + 0.1 * u * 0 + (0.1 - 0.06 * v) * (u * 0.5 + 0.5) + 0.0), 1.15 - 0.2 * v, 0.215 - 0.02 * v + 0.0 * u), nu=3, nv=5, thick=0.02, nz=(0, 0, 1))
        p.add(lap, G, angle=60)
    collar(p, 1.15, 0.15, R, 0.08, G)
    p.add([sphere(0.012, 0.012, 0.012, n=6, m=4).at(torso_pt(y, 90, 0.052)) for y in (0.82, 0.9, 0.98)], B)
    belt(p, 0.75, 0.8, G)
    for sx in (-1, 1):
        p.add(rbox(0.04, 0.02, 0.014, r=0.006).at(torso_pt(0.9, 90 + sx * 28, 0.045)), G)
    return p


def armor_fur():
    p = T_("armor_fur")
    p.add(tsh(0.76, 1.15), R, angle=60)
    ts = []
    for k in range(24):
        a = 360.0 * k / 24
        ts.append(torso_pt(1.13 + 0.02 * ((k % 3) - 1), a, 0.04))
    p.add(tufts(ts, (0, 1, 0.25), length=0.11, r=0.04, seed=3), G)
    ts2 = [torso_pt(0.8 + 0.01 * (k % 2), 360.0 * k / 20, 0.045) for k in range(20)]
    p.add(tufts(ts2, (0, -1, 0.1), length=0.1, r=0.04, seed=5), G)
    ts3 = [torso_pt(1.04 - 0.1 * (k // 5), 70 + 8 * (k % 5) + 20 * (k // 5), 0.06) for k in range(10)]
    p.add(tufts(ts3, (0, -0.4, 1), length=0.08, r=0.035, seed=7), G)
    p.add(strap([torso_pt(1.14, 150, 0.06), torso_pt(1.0, 100, 0.07), torso_pt(0.85, 40, 0.07)], w=0.025, th=0.012), G)
    p.add(sphere(0.03, 0.03, 0.015, n=8, m=5).at(torso_pt(1.0, 100, 0.08)), B)
    belt(p, 0.75, 0.8, G)
    return p


def armor_vest_ranger():
    p = T_("armor_vest_ranger")
    p.add(tsh(0.76, 1.15), R, angle=60)
    # bords de l'ouverture avant
    for sx in (-1, 1):
        p.add(tube(curve(np.array([torso_pt(1.15, 90 - sx * 14, 0.034), torso_pt(1.0, 90 - sx * 8, 0.036), torso_pt(0.85, 90 - sx * 7, 0.036), torso_pt(0.77, 90 - sx * 6, 0.036)]), 3),
                   [(0.016, 0.014)] * 10, n=8, up=(1, 0, 0)), G)
    p.add(strap([torso_pt(1.14, 130, 0.05), torso_pt(1.0, 80, 0.055), torso_pt(0.85, 25, 0.05)], w=0.026, th=0.01), G)
    for i, y in enumerate((0.86, 0.94, 1.02)):
        p.add(tube(np.array([torso_pt(y, 90 - 12, 0.04), torso_pt(y, 90 + 12, 0.04)]), [(0.012, 0.01)] * 2, n=6, up=(0, 1, 0)), G)
        p.add(sphere(0.008, 0.008, 0.008, n=5, m=3).at(torso_pt(y, 90 + 12, 0.045)), B)
    collar(p, 1.14, 0.14, R, 0.04, G)
    belt(p, 0.75, 0.8, G)
    p.add(rbox(0.04, 0.03, 0.02, r=0.006).at(torso_pt(0.9, 160, 0.06)), G)
    return p


def armor_ragged():
    p = T_("armor_ragged")
    p.add(tsh(0.9, 1.15), R, angle=60)
    hem = jag_hem(0.07, 12, 4)
    rx, rz, cz = torso_r(0.9)
    p.add(skirt(0.93, 0.78, (rx + 0.028, rz + 0.026), (rx + 0.045, rz + 0.04), n=26, k=5, hem_fn=hem, cz=cz), R, angle=60)
    p.add(rbox(0.05, 0.04, 0.01, r=0.004, s=1).at(torso_pt(1.03, 60, 0.04)), G)
    p.add(rbox(0.04, 0.05, 0.01, r=0.004, s=1).at(torso_pt(0.92, 130, 0.04)), G)
    p.add(rbox(0.04, 0.04, 0.01, r=0.004, s=1).at(torso_pt(1.08, 250, 0.04)), G)
    for sx in (-1, 1):
        p.add(tube(np.array([torso_pt(1.17, 90 + sx * 28, 0.04), torso_pt(1.12, 90 + sx * 26, 0.05)]), [(0.02, 0.01)] * 2, n=6, up=(0, 1, 0)), R)
    p.add(rbox(0.03, 0.03, 0.012, r=0.004, s=1).at(torso_pt(0.97, 90, 0.045)), B)
    belt(p, 0.74, 0.78, G, buckle=False)
    return p


def armor_cult_robe():
    p = T_("armor_cult_robe")
    p.add(tsh(0.74, 1.17, gx=0.05, gz=0.045), R, angle=60)
    p.add(rows_loft([(1.1, 0.2, 0.16, -0.03), (1.2, 0.17, 0.14, -0.04), (1.3, 0.12, 0.1, -0.04)], n=24, e=2.2, k=3, cap0='ngon', cap1='ngon'), R, angle=60)
    p.add(torus(0.125, 0.018, 24, 6).t(0, 1.3, -0.04), G)
    p.add(torus(0.065, 0.011, 20, 6).rx(90).t(0, 1.0, 0.222), B)
    p.add([rbox(0.007, 0.05, 0.009, r=0.003, s=1).rz(a).t(0, 1.0, 0.226) for a in (0, 60, 120)], B)
    p.add(sphere(0.012, 0.012, 0.01, n=6, m=4).t(0, 1.0, 0.226), B)
    p.add(tube(bez((-0.2, 0.84, 0.17), (-0.1, 0.8, 0.22), (0.1, 0.8, 0.22), (0.2, 0.84, 0.17), 8), [0.02] * 8, n=6), G)
    p.add(tube(bez((0.08, 0.805, 0.22), (0.1, 0.72, 0.24), (0.1, 0.62, 0.23), (0.11, 0.52, 0.22), 6), [0.016] * 6, n=6), G)
    p.add(sphere(0.026, 0.026, 0.026, n=8, m=5).t(0.11, 0.51, 0.22), B)
    return p


TORSO = [armor_plate, armor_leather, armor_robe, armor_robe_long, armor_tabard, armor_scale, armor_wraps, armor_coat, armor_fur, armor_vest_ranger,
         armor_ragged, armor_cult_robe]


# ------------------------------------------------------------------------------------------------ jupes
def armor_robe_skirt():
    p = S_("armor_robe_skirt")
    p.add(skirt(0.84, 0.36, (0.23, 0.17), (0.34, 0.29), n=30, k=8, folds=9, fold_amp=0.02, cz=0.0, curve=0.8), R, angle=50)
    p.add(skirt(0.37, 0.33, (0.335, 0.285), (0.345, 0.295), n=30, k=2, folds=9, fold_amp=0.02), G, angle=50)
    return p


def armor_robe_long_skirt():
    p = S_("armor_robe_long_skirt")
    p.add(skirt(0.84, 0.08, (0.23, 0.17), (0.38, 0.33), n=32, k=10, folds=10, fold_amp=0.025, curve=0.75), R, angle=50)
    p.add(skirt(0.09, 0.05, (0.378, 0.328), (0.388, 0.338), n=32, k=2, folds=10, fold_amp=0.025), G, angle=50)
    return p


def panel(y_top, y_bot, w_top, w_bot, z_top, z_bot, col, thick=0.02, nu=7, nv=7, curve_amt=0.04, side=1):
    def fn(u, v):
        w = w_top + (w_bot - w_top) * v
        return (u * w, y_top + (y_bot - y_top) * v, z_top + (z_bot - z_top) * v + curve_amt * (u * u) * (1 - 0.3 * v))
    return cloth_sheet(fn, nu, nv, thick, nz=(0, 0, -side))


def armor_tabard_skirt():
    p = S_("armor_tabard_skirt")
    p.add(panel(0.82, 0.38, 0.15, 0.16, 0.175, 0.2, R, 0.022, side=-1), R, angle=50)
    p.add(panel(0.82, 0.38, 0.15, 0.16, -0.15, -0.2, R, 0.022, side=1), R, angle=50)
    p.add(panel(0.40, 0.37, 0.152, 0.162, 0.2, 0.2, R, 0.026, nv=2, side=-1), G, angle=50)
    p.add(panel(0.40, 0.37, 0.152, 0.162, -0.2, -0.2, R, 0.026, nv=2, side=1), G, angle=50)
    p.add(sphere(0.045, 0.05, 0.012, n=10, m=6).t(0, 0.6, 0.205), B)
    p.add(rbox(0.22, 0.03, 0.17, r=0.01).t(0, 0.84, 0.0), G) if False else None
    p.add(skirt(0.84, 0.76, (0.22, 0.16), (0.225, 0.165), n=26, k=2), G, angle=50)
    return p


def armor_coat_skirt():
    p = S_("armor_coat_skirt")
    p.add(skirt(0.84, 0.30, (0.23, 0.17), (0.31, 0.27), n=30, k=8, folds=6, fold_amp=0.014, curve=0.85, e_bot=2.6), R, angle=50)
    p.add(skirt(0.31, 0.27, (0.308, 0.268), (0.316, 0.276), n=30, k=2, folds=6, fold_amp=0.014, e=2.6), G, angle=50)
    p.add([sphere(0.012, 0.012, 0.012, n=6, m=4).t(0.0, y, 0.19 + (0.84 - y) * 0.12) for y in (0.78, 0.66, 0.54)], B)
    p.add(skirt(0.84, 0.78, (0.222, 0.162), (0.226, 0.166), n=26, k=2), G, angle=50)
    return p


def armor_cult_robe_skirt():
    p = S_("armor_cult_robe_skirt")
    p.add(skirt(0.84, 0.06, (0.23, 0.17), (0.4, 0.35), n=32, k=10, folds=11, fold_amp=0.03, curve=0.7, hem_fn=jag_hem(0.045, 16, 8)), R, angle=50)
    p.add([sphere(0.016, 0.016, 0.01, n=6, m=4).t(0.0, 0.5, 0.26)], B)
    return p


def armor_plate_skirt():
    p = S_("armor_plate_skirt")
    for k, (y0, y1, rx0, rz0, fl) in enumerate([(0.86, 0.72, 0.225, 0.17, 0.0), (0.76, 0.6, 0.255, 0.2, 0.03), (0.66, 0.5, 0.285, 0.23, 0.05)]):
        p.add(skirt(y0, y1, (rx0, rz0), (rx0 + fl + 0.04, rz0 + fl + 0.04), n=28, k=3, folds=14, fold_amp=0.005), R, angle=50)
        p.add(skirt(y1 + 0.012, y1 - 0.006, (rx0 + fl + 0.038, rz0 + fl + 0.038), (rx0 + fl + 0.046, rz0 + fl + 0.046), n=28, k=2, folds=14, fold_amp=0.005), G, angle=50)
    p.add([sphere(0.01, 0.01, 0.01, n=6, m=4).t(sx * 0.12, 0.8, 0.2) for sx in (-1, 0, 1)], B)
    p.add(rbox(0.07, 0.11, 0.015, r=0.008).t(0, 0.62, 0.25), R)
    p.add(sphere(0.02, 0.02, 0.01, n=8, m=5).t(0, 0.62, 0.265), B)
    return p


def armor_scale_skirt():
    p = S_("armor_scale_skirt")
    for k, (y, rx, rz) in enumerate([(0.82, 0.235, 0.18), (0.72, 0.265, 0.21), (0.62, 0.295, 0.24), (0.52, 0.325, 0.27)]):
        n = 40
        rings = []
        th = 2 * np.pi * np.arange(n) / n
        for yy, ex, dy in ((y + 0.04, 0.0, 0.0), (y + 0.0, 0.01, 0.0), (y - 0.04, 0.03, 0.0), (y - 0.075, 0.034, 1.0)):
            pts = sec(yy, rx + ex, rz + ex, 0, 0, n, 2.3)
            if dy:
                pts[:, 1] -= 0.014 * (0.5 + 0.5 * np.cos(th * 20))
            rings.append(pts)
        p.add(loft(rings, 'ngon', 'ngon'), R, angle=40)
    p.add(skirt(0.86, 0.8, (0.225, 0.17), (0.23, 0.175), n=28, k=2), G, angle=50)
    p.add(sphere(0.02, 0.02, 0.012, n=8, m=5).t(0, 0.83, 0.19), B)
    return p


def armor_ragged_skirt():
    p = S_("armor_ragged_skirt")
    rng = np.random.RandomState(11)
    n = 15
    strips = []
    for i in range(n):
        th = 2 * math.pi * i / n
        L = 0.22 + 0.2 * rng.rand()
        rx, rz = 0.235, 0.18
        x, z = rx * math.cos(th), rz * math.sin(th)
        nx, nz = math.cos(th) / rx, math.sin(th) / rz
        nl = math.hypot(nx, nz)
        nx, nz = nx / nl, nz / nl
        top = np.array([x, 0.82, z])
        bot = top + np.array([nx * 0.08, -L, nz * 0.08])
        ang = th
        path = bez(top, top + (bot - top) * 0.3, top + (bot - top) * 0.7 + np.array([nx * 0.02, 0, nz * 0.02]), bot, 5)
        rad = [(0.05 * (1 - 0.35 * k / 4), 0.01) for k in range(5)]
        strips.append(tube(path, rad, n=6, e=3.0, up=(nx, 0, nz) if False else (math.cos(th), 0, math.sin(th)), cap0='ngon', cap1='ngon', twist=0.0))
    p.add(strips, R, angle=60)
    p.add(skirt(0.86, 0.79, (0.225, 0.17), (0.23, 0.175), n=28, k=2), G, angle=50)
    p.add(tube(bez((0.0, 0.8, 0.2), (0.04, 0.72, 0.22), (0.02, 0.66, 0.22), (0.06, 0.6, 0.22), 6), [0.015] * 6, n=6), G)
    return p


def armor_fur_skirt():
    p = S_("armor_fur_skirt")
    p.add(skirt(0.86, 0.7, (0.225, 0.17), (0.265, 0.21), n=26, k=3), R, angle=50)
    ts = []
    for r_i, (y, rx, rz, cnt) in enumerate([(0.72, 0.27, 0.215, 24), (0.62, 0.285, 0.23, 24), (0.52, 0.295, 0.24, 22)]):
        for k in range(cnt):
            th = 2 * math.pi * (k + 0.5 * (r_i % 2)) / cnt
            ts.append((rx * math.cos(th), y, rz * math.sin(th)))
    p.add(tufts(ts, (0, -1, 0), length=0.17, r=0.05, seed=9, jitter=0.2), G)
    p.add(skirt(0.86, 0.8, (0.225, 0.17), (0.23, 0.175), n=26, k=2), G, angle=50)
    p.add(rbox(0.03, 0.03, 0.014, r=0.008).t(0, 0.82, 0.19), B)
    return p


SKIRTS = [armor_robe_skirt, armor_robe_long_skirt, armor_tabard_skirt, armor_coat_skirt, armor_cult_robe_skirt, armor_plate_skirt, armor_scale_skirt,
          armor_ragged_skirt, armor_fur_skirt]
