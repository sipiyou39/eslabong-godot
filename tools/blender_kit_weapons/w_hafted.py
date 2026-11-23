from wcommon import *
from registry import weapon


def eye_block(y, w=0.07, hgt=0.1, d=0.07, color=G):
    return box((w, hgt, d), (0, y, 0), color=color, bevel=0.006)


@weapon("wpn_axe_hand", notes="hache à une main 0,72 m, taillant à +Z")
def axe_hand():
    p = []
    p.append(haft(-0.20, 0.50, 0.0185, 0.0205, bow=0.012))
    p.append(grip(-0.14, 0.04, 0.0235, pitch=0.034))
    p.append(sphere(0.026, 8, 5, G, pos=(0, -0.205, 0.0)))
    head = [(0.455, -0.040), (0.455, 0.035), (0.495, 0.085), (0.52, 0.165), (0.472, 0.185), (0.418, 0.198), (0.364, 0.185), (0.316, 0.165),
            (0.341, 0.085), (0.381, 0.035), (0.381, -0.040)]
    ins = [0, 0, 0.012, 0.05, 0.05, 0.05, 0.05, 0.05, 0.012, 0, 0]
    hh = [0.024, 0.024, 0.02, 0.014, 0.014, 0.014, 0.014, 0.014, 0.02, 0.024, 0.024]
    p.append(plate(head, hh, ins, bevel=None))
    p.append(eye_block(0.418, 0.062, 0.098, 0.088))
    p.append(cone(0.016, 0.05, 6, G, pos=(0, 0.462, 0)))
    p.append(box((0.04, 0.05, 0.04), (0, 0.418, -0.05), color=G, bevel=0.005))
    return p


@weapon("wpn_axe_great", notes="grande hache à deux mains 1,3 m, pointe dorsale et sommitale")
def axe_great():
    p = []
    p.append(haft(-0.45, 0.90, 0.021, 0.0235, bow=0.01))
    p.append(grip(-0.22, 0.10, 0.0265, pitch=0.038))
    p.append(sphere(0.032, 8, 5, G, pos=(0, -0.46, 0.0)))
    p.append(band(-0.32, 0.027, 0.03))
    p.append(band(0.18, 0.027, 0.03))
    head = [(0.88, -0.06), (0.88, 0.05), (0.945, 0.12), (0.97, 0.27), (0.90, 0.31), (0.81, 0.335), (0.72, 0.31), (0.65, 0.27),
            (0.675, 0.12), (0.74, 0.05), (0.74, -0.06)]
    ins = [0, 0, 0.012, 0.075, 0.075, 0.075, 0.075, 0.075, 0.012, 0, 0]
    hh = [0.032, 0.032, 0.026, 0.018, 0.018, 0.018, 0.018, 0.018, 0.026, 0.032, 0.032]
    p.append(plate(head, hh, ins))
    p.append(eye_block(0.81, 0.08, 0.17, 0.115))
    p.append(cone(0.022, 0.15, 6, B, pos=(0, 0.89, 0)))
    p.append(cyl((0, 0.81, -0.05), (0, 0.775, -0.2), 0.026, 0.006, seg=6, color=B, bevel=None))
    p.append(band(0.89, 0.026, 0.03))
    return p


@weapon("wpn_axe_double", notes="hache double (2 taillants, ±Z) 1,0 m")
def axe_double():
    p = []
    p.append(haft(-0.34, 0.66, 0.0195, 0.0215, bow=0.0))
    p.append(grip(-0.17, 0.07, 0.025, pitch=0.036))
    p.append(sphere(0.03, 8, 5, G, pos=(0, -0.35, 0.0)))
    p.append(band(-0.25, 0.026, 0.028))
    base = [(0.63, 0.03), (0.675, 0.085), (0.70, 0.19), (0.65, 0.215), (0.595, 0.225), (0.54, 0.215), (0.49, 0.19), (0.515, 0.085), (0.56, 0.03)]
    ins = [0, 0.012, 0.055, 0.055, 0.055, 0.055, 0.055, 0.012, 0]
    hh = [0.026, 0.021, 0.015, 0.015, 0.015, 0.015, 0.015, 0.021, 0.026]
    head_f = plate(base, hh, ins)
    head_b = plate([(y, -z) for y, z in base], hh, ins)
    p += [head_f, head_b]
    p.append(eye_block(0.595, 0.07, 0.15, 0.09))
    p.append(cone(0.019, 0.075, 6, B, pos=(0, 0.655, 0)))
    p.append(band(0.66, 0.024, 0.026))
    return p


@weapon("wpn_hammer_war", notes="marteau de guerre 0,9 m, face carrée +Z et bec -Z")
def hammer_war():
    p = []
    p.append(haft(-0.25, 0.52, 0.0185, 0.021, bow=0.0))
    p.append(grip(-0.18, 0.06, 0.0235, pitch=0.034))
    p.append(sphere(0.027, 8, 5, G, pos=(0, -0.255, 0.0)))
    p.append(band(0.04, 0.0235, 0.03))
    p.append(box((0.085, 0.095, 0.09), (0, 0.46, 0.0), color=G, bevel=0.008))
    # face de frappe (avant)
    p.append(frustum(0.088, 0.088, 0.108, 0.108, 0.04, color=B, bevel=0.007).xf(pos=(0, 0.46, 0.04), rot=(90, 0, 0)))
    # bec arrière
    p.append(cyl((0, 0.46, -0.04), (0, 0.44, -0.17), 0.029, 0.005, seg=6, color=B, bevel=None, sx=1.0, sz=1.0))
    p.append(cone(0.022, 0.07, 6, B, pos=(0, 0.505, 0.0)))
    p.append(band(0.51, 0.024, 0.02))
    return p


@weapon("wpn_hammer_great", notes="maillet à deux mains 1,3 m")
def hammer_great():
    p = []
    p.append(haft(-0.45, 0.85, 0.022, 0.025, bow=0.0))
    p.append(grip(-0.22, 0.10, 0.028, pitch=0.04))
    p.append(sphere(0.034, 8, 5, G, pos=(0, -0.46, 0.0)))
    p.append(band(-0.33, 0.029, 0.034))
    p.append(band(0.2, 0.029, 0.034))
    p.append(box((0.19, 0.17, 0.2), (0, 0.84, 0.0), color=G, bevel=0.012))
    for s in (1, -1):
        p.append(frustum(0.17, 0.17, 0.2, 0.2, 0.05, color=B, bevel=0.009).xf(pos=(0, 0.84, s * 0.095), rot=(s * 90, 0, 0)))
    p.append(cone(0.03, 0.1, 6, B, pos=(0, 0.925, 0.0)))
    for s in (1, -1):
        p.append(studs(4, 0.0, 0.0, 0.0) if False else sphere(0.012, 5, 3, B, pos=(s * 0.095, 0.88, 0.0)))
        p.append(sphere(0.012, 5, 3, B, pos=(s * 0.095, 0.80, 0.0)))
    p.append(band(0.84, 0.0, 0.0) if False else box((0.205, 0.03, 0.17), (0, 0.84, 0), color=G, bevel=0.006))
    return p


@weapon("wpn_mace", notes="masse à ailettes 0,85 m")
def mace():
    p = []
    p.append(haft(-0.22, 0.48, 0.0175, 0.02, bow=0.0))
    p.append(grip(-0.15, 0.05, 0.0225, pitch=0.034))
    p.append(sphere(0.027, 8, 5, G, pos=(0, -0.225, 0.0)))
    p.append(band(0.07, 0.022, 0.03))
    p.append(sphere(0.052, 10, 6, G, pos=(0, 0.52, 0.0)))
    fl = [(0.04, -0.075), (0.088, -0.05), (0.108, -0.02), (0.108, 0.02), (0.088, 0.05), (0.04, 0.075)]
    fp = plate([(r, y) for r, y in fl], 0.015, [0.0, 0.014, 0.02, 0.02, 0.014, 0.0], plane="XY", color=B, edge_color=G, bevel=None)
    # plaque dans le plan (r,y) -> épaisseur en Z ; 7 ailettes autour de Y
    fp = fp.xf(pos=(0, 0.52, 0.0))
    p += radial(fp, 7, "y", 0)
    p.append(cone(0.028, 0.085, 7, B, pos=(0, 0.565, 0.0)))
    p.append(band(0.455, 0.024, 0.03))
    return p


@weapon("wpn_club_spiked", notes="gourdin clouté 0,95 m")
def club_spiked():
    p = []
    prof = [(0.0215, -0.28), (0.024, -0.26), (0.0235, -0.1), (0.027, 0.05), (0.04, 0.2), (0.056, 0.35), (0.064, 0.45), (0.058, 0.53), (0.04, 0.58), (0.0, 0.6)]
    p.append(lathe(prof, 9, R, bevel=None))
    p.append(grip(-0.2, 0.0, 0.0295, pitch=0.036))
    p.append(band(0.2, 0.043, 0.03, flare=1.0))
    p.append(band(0.5, 0.062, 0.03, flare=1.0))
    p.append(band(0.38, 0.0585, 0.025, flare=1.0))
    for y, rr, n, ph in [(0.29, 0.05, 6, 0), (0.42, 0.062, 7, 25), (0.51, 0.061, 6, 0), (0.56, 0.047, 5, 30)]:
        for k in range(n):
            a = ph + 360 * k / n
            ar = math.radians(a)
            d = np.array([math.cos(ar), 0.35, math.sin(ar)])
            d = d / np.linalg.norm(d)
            p0 = np.array([rr * math.cos(ar), y, rr * math.sin(ar)])
            p.append(cyl(p0 - d * 0.006, p0 + d * 0.06, 0.013, 0.0, seg=5, color=B))
    p.append(cone(0.022, 0.07, 6, B, pos=(0, 0.585, 0.0)))
    return p


@weapon("wpn_pick", notes="pioche de guerre 0,9 m")
def pick():
    p = []
    p.append(haft(-0.24, 0.5, 0.0185, 0.02, bow=0.0))
    p.append(grip(-0.17, 0.05, 0.0235, pitch=0.034))
    p.append(sphere(0.027, 8, 5, G, pos=(0, -0.245, 0.0)))
    Rr = 0.3
    ph = np.radians(np.linspace(-62, 62, 16))
    path = np.stack([np.zeros(16), 0.49 - Rr + Rr * np.cos(ph), Rr * np.sin(ph)], 1)
    tt = np.linspace(0, 1, 16)
    rad = 0.012 + 0.03 * (1 - np.abs(2 * tt - 1) ** 1.4)
    pk = sweep(path, circle2(6), scale=rad, color=B, ref=(1, 0, 0), cap0=True, cap1=True)
    p.append(pk)
    p.append(eye_block(0.485, 0.07, 0.085, 0.09))
    p.append(band(0.42, 0.024, 0.026))
    return p


@weapon("wpn_cleaver", notes="gros couperet 0,55 m")
def cleaver():
    p = []
    p.append(smooth_handle(-0.11, 0.07, 0.022, 0.021, R, seg=8, sx=0.85))
    p.append(sphere(0.028, 8, 5, G, pos=(0, -0.118, 0.0), s=(0.85, 1, 1)))
    p.append(box((0.036, 0.03, 0.056), (0, 0.082, 0.0), color=G, bevel=0.005))
    for yy in (-0.05, 0.0, 0.05):
        p.append(sphere(0.011, 5, 3, B, pos=(0.0185, yy, 0.0)))
        p.append(sphere(0.011, 5, 3, B, pos=(-0.0185, yy, 0.0)))
    bl = [(0.075, -0.035), (0.075, 0.185), (0.2, 0.2), (0.33, 0.205), (0.385, 0.18), (0.405, 0.12), (0.395, -0.035)]
    ins = [0, 0.0, 0.05, 0.05, 0.05, 0.03, 0.0]
    hh = [0.017, 0.017, 0.015, 0.015, 0.015, 0.016, 0.017]
    p.append(plate(bl, hh, ins, color=B, edge_color=G))
    p.append(box((0.04, 0.34, 0.03), (0, 0.235, -0.04), color=G, bevel=0.005))
    p.append(cyl((-0.026, 0.3, 0.03), (0.026, 0.3, 0.03), 0.026, 0.026, seg=10, color=G, bevel=0.002))
    p.append(cyl((-0.03, 0.3, 0.03), (0.03, 0.3, 0.03), 0.014, 0.014, seg=8, color=K, bevel=None))
    return p
