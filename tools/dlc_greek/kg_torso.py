"""Torses grecs (pivot torse (0,0.78,0)) et jupes (pivot bassin (0,0.74,0)). R principal, G secondaire (cuir), B accent (or)."""
from gk import *


def pleat(g, folds=14, amp=0.007, cz=0.0, y0=0.75, y1=1.16, grow=0.0):
    """plis verticaux : décale radialement les sommets d'une coque (angle autour de l'axe y)."""
    V = g.V
    th = np.arctan2(V[:, 2] - cz, V[:, 0])
    k = amp * (1.0 + grow * np.clip((y1 - V[:, 1]) / (y1 - y0), 0, 1))
    d = np.stack([np.cos(th), np.zeros(len(V)), np.sin(th)], 1)
    g.V = V + d * (k * np.cos(th * folds))[:, None]
    return g


def armor_cuirass_greek():
    p = T_("armor_cuirass_greek")
    kw = dict(gx=0.032, gz=0.03)
    sh = torso_shell(0.755, 1.16, n=22, k=10, chest=0.03, **kw)
    stamp(sh, (0.0, 0.99, 0.21), (0.012, 0.19, 0.05), -0.012)
    stamp(sh, (0.0, 0.97, -0.2), (0.012, 0.2, 0.05), -0.012)                          # colonne
    stamp(sh, (0.1, 1.0, -0.185), (0.075, 0.1, 0.05), 0.014, mirror=True)             # omoplates
    p.add(sh, R, angle=60)
    # musculature en volumes : pectoraux + abdominaux (bas-relief), lignes dorées incrustées
    for sx in (-1, 1):
        a = 90 - sx * 24
        p.add(sphere(0.11, 0.07, 0.034, n=8, m=5).rz(sx * 7).at(torso_pt(1.05, a, 0.026, **kw)), R, angle=60)
        p.add(sphere(0.012, 0.012, 0.01, n=5, m=3).at(torso_pt(1.03, 90 - sx * 31, 0.075, **kw)), B)
        for k, y in enumerate((0.945, 0.888, 0.83)):
            p.add(sphere(0.046, 0.03, 0.02, n=6, m=4).at(torso_pt(y, 90 - sx * 12, 0.02, **kw)), R, angle=60)
        p.add(strap([torso_pt(1.125, 90 - sx * 30, 0.045, **kw), (sx * 0.22, 1.168, 0.0), torso_pt(1.12, 270 + sx * 30, 0.045, **kw)], w=0.045, th=0.011), R)
        p.add([sphere(0.009, 0.009, 0.009, n=5, m=3).t(sx * 0.292, y, 0.0) for y in (0.85, 0.94, 1.03)], B)
    p.add(tube(curve([torso_pt(1.13, 90, 0.04, **kw), torso_pt(1.0, 90, 0.04, **kw), torso_pt(0.84, 90, 0.04, **kw)], 3), [0.006] * 7, n=4, cap0='ngon', cap1='ngon'), B)
    p.add(torus(0.128, 0.014, 20, 6).sc(1.0, 1.0, 0.85).t(0, 1.158, -0.004), B)
    rx, rz, cz = torso_r(0.775)
    p.add(rows_loft([(0.752, rx + 0.046, rz + 0.042, cz), (0.795, rx + 0.04, rz + 0.037, cz)], n=22, e=2.3, cap0='ngon', cap1='ngon'), B, angle=60)
    p.add(sphere(0.024, 0.024, 0.014, n=8, m=5).at(torso_pt(0.775, 90, 0.052, **kw)), B)
    return p


def armor_cuirass_greek_skirt():
    p = S_("armor_cuirass_greek_skirt")
    hem = lambda a: -0.045 * (0.5 - 0.5 * math.cos(18 * a))
    p.add(skirt(0.865, 0.46, (0.228, 0.172), (0.325, 0.265), n=36, k=4, folds=18, fold_amp=0.012, curve=0.9, hem_fn=hem), G, angle=50)
    hem2 = lambda a: -0.04 * (0.5 - 0.5 * math.cos(18 * a + math.pi))
    p.add(skirt(0.86, 0.56, (0.232, 0.176), (0.31, 0.25), n=36, k=4, folds=18, fold_amp=0.01, curve=0.9, hem_fn=hem2), R, angle=50)
    p.add(skirt(0.87, 0.835, (0.236, 0.18), (0.248, 0.19), n=30, k=2), B, angle=50)
    p.add([sphere(0.011, 0.011, 0.008, n=5, m=3).t(0.256 * math.cos(2 * math.pi * i / 9 + 0.17), 0.8, 0.2 * math.sin(2 * math.pi * i / 9 + 0.17)) for i in range(9)], B)
    return p


def armor_chiton():
    p = T_("armor_chiton")
    sh = torso_shell(0.75, 1.165, gx=0.044, gz=0.038, n=26, k=8)
    pleat(sh, folds=15, amp=0.007, y0=0.75, y1=1.165, grow=0.8)
    p.add(sh, R, angle=60)
    # encolure + fibules d'épaule
    p.add(torus(0.13, 0.013, 22, 6).sc(1.0, 1.0, 0.85).t(0, 1.158, -0.004), B)
    for sx in (-1, 1):
        p.add(sphere(0.022, 0.022, 0.012, n=8, m=5).at(np.array([sx * 0.195, 1.17, 0.062])), B)
        p.add(sphere(0.016, 0.016, 0.01, n=6, m=4).at(np.array([sx * 0.195, 1.17, -0.062])), B)
    # cordon sous la poitrine, noué devant
    rx, rz, cz = torso_r(1.0)
    p.add(rows_loft([(0.985, rx + 0.05, rz + 0.044, cz), (1.0, rx + 0.05, rz + 0.044, cz)], n=26, e=2.3, cap0='ngon', cap1='ngon'), G, angle=60)
    p.add(sphere(0.03, 0.026, 0.02, n=8, m=5).at(torso_pt(0.99, 90, 0.06)), B)
    for sx in (-1, 1):
        p.add(tube(bez((sx * 0.015, 0.985, 0.222), (sx * 0.04, 0.93, 0.235), (sx * 0.05, 0.86, 0.23), (sx * 0.055, 0.8, 0.225), 6), [(0.016 * (1 - 0.3 * k / 5), 0.008) for k in range(6)], n=5, e=3.0, up=(1, 0, 0)), G)
    rx, rz, cz = torso_r(0.775)
    p.add(rows_loft([(0.748, rx + 0.052, rz + 0.046, cz), (0.77, rx + 0.052, rz + 0.046, cz)], n=26, e=2.3, cap0='ngon', cap1='ngon'), B, angle=60)
    return p


def armor_chiton_skirt():
    p = S_("armor_chiton_skirt")
    g = skirt(0.845, 0.42, (0.226, 0.17), (0.315, 0.262), n=30, k=6, folds=15, fold_amp=0.013, curve=0.85)
    p.add(g, R, angle=50)
    p.add(skirt(0.435, 0.40, (0.31, 0.258), (0.318, 0.266), n=30, k=2, folds=15, fold_amp=0.013), B, angle=50)    # galon doré
    p.add(skirt(0.425, 0.41, (0.314, 0.262), (0.32, 0.268), n=30, k=2, folds=15, fold_amp=0.013), G, angle=50)
    p.add(skirt(0.85, 0.74, (0.228, 0.172), (0.262, 0.205), n=30, k=3, folds=15, fold_amp=0.008, curve=0.9), R, angle=50)  # apoptygma
    p.add(skirt(0.745, 0.73, (0.262, 0.205), (0.267, 0.21), n=30, k=2, folds=15, fold_amp=0.008), B, angle=50)
    return p


def armor_toga():
    p = T_("armor_toga")
    # enroulement de la taille
    sh = torso_shell(0.75, 0.99, gx=0.05, gz=0.045, n=24, k=5)
    pleat(sh, folds=11, amp=0.01, y0=0.75, y1=0.99, grow=0.3)
    p.add(sh, R, angle=60)
    # pan diagonal sur l'épaule gauche (côté +x), traversant la poitrine jusqu'à la hanche droite
    pts = [torso_pt(1.17, 12, 0.055), torso_pt(1.11, 52, 0.07), torso_pt(1.02, 92, 0.085), torso_pt(0.93, 132, 0.085), torso_pt(0.85, 172, 0.065)]
    p.add(strap(pts, w=0.085, th=0.02, n=6), R)
    p.add(strap([torso_pt(1.17, 12, 0.068), torso_pt(1.11, 52, 0.083), torso_pt(1.02, 92, 0.098), torso_pt(0.93, 132, 0.098), torso_pt(0.85, 172, 0.078)], w=0.012, th=0.008), B)
    # drapé de l'épaule + pan dorsal
    p.add(place(dome(0.135, 0.1, n=16, steps=4), 22, 0.0, 0.01), R, angle=60)
    pts2 = [torso_pt(1.17, 348, 0.05), torso_pt(1.06, 300, 0.06), torso_pt(0.96, 255, 0.06), torso_pt(0.86, 215, 0.055)]
    p.add(strap(pts2, w=0.085, th=0.018, n=6), R)
    p.add(tube(np.array([(0.30, 1.04, 0.0), (0.33, 0.86, -0.02), (0.34, 0.72, 0.03)]), [(0.035, 0.012)] * 3, n=6, e=3.0, up=(0, 0, 1)), R)
    # bande de ceinture dorée + fibule
    rx, rz, cz = torso_r(0.775)
    p.add(rows_loft([(0.745, rx + 0.058, rz + 0.052, cz), (0.78, rx + 0.056, rz + 0.05, cz)], n=26, e=2.3, cap0='ngon', cap1='ngon'), B, angle=60)
    p.add(sphere(0.026, 0.026, 0.014, n=8, m=5).t(0.255, 1.165, 0.04), B)
    return p


def armor_toga_skirt():
    p = S_("armor_toga_skirt")
    p.add(skirt(0.845, 0.2, (0.23, 0.172), (0.345, 0.3), n=30, k=7, folds=12, fold_amp=0.026, curve=0.75, hem_fn=jag_hem(0.025, 8, 5)), R, angle=50)
    p.add(skirt(0.215, 0.185, (0.343, 0.298), (0.351, 0.306), n=30, k=2, folds=12, fold_amp=0.026), B, angle=50)
    # pan de drapé avant (bord oblique doré)
    def fn(u, v):
        return (0.02 + u * 0.12 + 0.05 * v, 0.84 - 0.46 * v, 0.19 + 0.05 * v + 0.015 * math.sin(u * 3 + v * 4))
    p.add(cloth_sheet(fn, nu=5, nv=6, thick=0.016, nz=(0, 0, 1)), R, angle=60)
    return p


TORSO = [armor_toga, armor_cuirass_greek, armor_chiton]
SKIRTS = [armor_toga_skirt, armor_cuirass_greek_skirt, armor_chiton_skirt]
