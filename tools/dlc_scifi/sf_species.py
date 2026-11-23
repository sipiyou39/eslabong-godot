"""Espèces sci-fi : robot (chassis métallique articulé, cartoon, massif) et alien (silhouette fine, grande tête, 3 doigts).
Masque : robot -> peau = chassis métal, R = carénages peints (primaire), G = articulations sombres / câbles, B = lueurs.
         alien -> peau = épiderme lisse, R = petit short, B = marques phosphorescentes discrètes."""
from sf_common import *
from heads import neck_piece, eyes_dark
import humanoid


def nm_fn(sp):
    return lambda p: f"body_{sp}_{p}"


# =============================================================================================== ROBOT
RK = dict(tw=1.06, td=1.04)


def robot_torso(nm):
    t = Part(nm("torso"), PV["torso"])
    rows = [(0.72, 0.165, 0.12, 0.0), (0.775, 0.19, 0.135, 0.0), (0.84, 0.205, 0.14, 0.0), (0.92, 0.245, 0.152, 0.004), (1.0, 0.272, 0.166, 0.01),
            (1.08, 0.288, 0.172, 0.012), (1.13, 0.262, 0.155, 0.005), (1.165, 0.13, 0.095, 0.0), (1.19, 0.095, 0.08, 0.0)]
    t.add(rows_loft(rows, n=24, e=2.7, k=12), SKIN, angle=55)
    # plastron peint + noyau lumineux
    t.add(box_at((0, 1.0, 0.178), (0.31, 0.17, 0.05), r=0.022, s=1), R, angle=55)
    t.add(box_at((0, 0.89, 0.162), (0.2, 0.06, 0.04), r=0.014, s=1), R, angle=55)
    t.add(zdisc(0, 1.02, 0.188, 0.037, depth=0.022, n=14), B, ao=1.0)
    t.add(zdisc(0, 1.02, 0.176, 0.05, depth=0.016, n=14), G, angle=60)
    t.add(led_row(-0.1, 0.1, 1.07, 0.2, n=3, r=0.008), B, ao=1.0)
    # soufflet de taille (anneaux sombres)
    for y in (0.81, 0.835, 0.86):
        rx, rz = np.interp(y, [0.72, 0.84, 0.92], [0.19, 0.205, 0.245]), np.interp(y, [0.72, 0.84, 0.92], [0.135, 0.14, 0.152])
        t.add(rows_loft([(y - 0.009, rx + 0.006, rz + 0.006, 0.0), (y + 0.009, rx + 0.006, rz + 0.006, 0.0)], n=24, e=2.7, cap0=None, cap1='ngon'), G, angle=60)
    # collier + prise de cou
    t.add(rows_loft([(1.14, 0.12, 0.1, 0.0), (1.2, 0.09, 0.08, 0.0)], n=18, e=2.1, cap0='ngon', cap1='ngon'), G, angle=60)
    # dos : grilles et échappements
    for y in (0.95, 0.99, 1.03):
        t.add(cube((0, y, -0.172), (0.15, 0.014, 0.02)), G, angle=40)
    t.add([cyl_between((sx * 0.12, 0.92, -0.17), (sx * 0.12, 1.02, -0.19), 0.025, 0.02, n=8) for sx in (-1, 1)], G, angle=60)
    t.add(bolts([(sx * 0.2, 1.06, 0.188) for sx in (-1, 1)] + [(sx * 0.2, 0.93, 0.168) for sx in (-1, 1)], 0.009), B, ao=1.0)
    return t


def robot_pelvis(nm):
    p = Part(nm("pelvis"), PV["pelvis"])
    rows = [(0.60, 0.15, 0.115, 0.0), (0.66, 0.205, 0.148, 0.0), (0.74, 0.222, 0.156, 0.004), (0.82, 0.205, 0.148, 0.004), (0.86, 0.15, 0.115, 0.0)]
    p.add(rows_loft(rows, n=22, e=2.8, k=9), R, angle=55)
    p.add(rows_loft([(0.775, 0.228, 0.162, 0.004), (0.815, 0.228, 0.162, 0.004)], n=22, e=2.8, cap0='ngon', cap1='ngon'), G, angle=60)
    p.add(box_at((0, 0.795, 0.168), (0.07, 0.05, 0.02), r=0.008), B, ao=1.0)
    p.add([sphere(0.077, 0.077, 0.077, n=12, m=7).t(sx * 0.13, 0.715, 0.0) for sx in (-1, 1)], G, angle=60)
    p.add(box_at((0, 0.64, 0.125), (0.1, 0.07, 0.03), r=0.012), SKIN, angle=55)
    return p


def robot_arm(nm):
    a = Part(nm("arm_l"), PV["arm_l"])
    a.add(sphere(0.082, 0.078, 0.082, n=14, m=8).t(0.30, 1.115, 0.0), G, angle=60)
    up = tube(np.array([[0.305, 1.105, 0.0], [0.312, 1.0, 0.0], [0.318, 0.9, 0.0]]), [(0.068, 0.068)] * 3, n=12, cap0='ngon', cap1='ngon')
    a.add(up, SKIN, angle=55)
    a.add(cyl_between((0.30, 1.04, -0.062), (0.315, 0.9, -0.058), 0.017, n=8), G, angle=60)    # vérin
    a.add(rows_loft([(0.94, 0.078, 0.078, 0.0, 0.315), (0.99, 0.078, 0.078, 0.0, 0.312)], n=14, cap0='ngon', cap1='ngon'), R, angle=60)
    a.add(sphere(0.064, 0.064, 0.064, n=12, m=7).t(0.322, 0.872, -0.004), G, angle=60)
    fa = tube(np.array([[0.326, 0.85, 0.0], [0.332, 0.78, 0.004], [0.338, 0.70, 0.01]]), [(0.074, 0.074), (0.078, 0.078), (0.062, 0.062)], n=12, cap0='ngon', cap1='ngon')
    a.add(fa, R, angle=55)
    a.add(rows_loft([(0.69, 0.066, 0.066, 0.012, 0.338), (0.72, 0.07, 0.07, 0.01, 0.338)], n=14, cap0='ngon', cap1='ngon'), G, angle=60)
    a.add([rbox(0.058, 0.058, 0.056, r=0.022, s=1).t(0.34, 0.612, 0.025), sphere(0.026, 0.034, 0.03, n=8, m=5).rz(-18).t(0.298, 0.64, 0.06)], SKIN, angle=55)
    a.add([box_at((0.34, 0.612 + dy, 0.082), (0.09, 0.007, 0.008), r=0.003, s=1) for dy in (-0.02, 0.0, 0.02)], G)
    a.add(sphere(0.012, 0.012, 0.01, n=6, m=4).t(0.38, 0.77, 0.03), B, ao=1.0)
    return a


def robot_leg(nm):
    lg = Part(nm("leg_l"), PV["leg_l"])
    x0 = 0.13
    lg.add(sphere(0.078, 0.078, 0.078, n=12, m=7).t(x0, 0.715, 0.0), G, angle=60)
    lg.add(tube(np.array([[x0, 0.69, 0.0], [x0, 0.57, 0.004], [x0, 0.46, 0.0]]), [(0.088, 0.09), (0.082, 0.085), (0.07, 0.072)], n=14, cap0='ngon', cap1='ngon'), SKIN, angle=55)
    lg.add(sphere(0.074, 0.074, 0.074, n=12, m=7).t(x0, 0.44, 0.0), G, angle=60)
    lg.add(box_at((x0, 0.44, 0.07), (0.08, 0.085, 0.03), r=0.012, s=1), R, angle=55)
    shin = tube(np.array([[x0, 0.405, 0.0], [x0, 0.32, 0.004], [x0, 0.21, 0.0]]), [(0.078, 0.082), (0.082, 0.088), (0.062, 0.064)], n=14, cap0='ngon', cap1='ngon')
    lg.add(shin, R, angle=55)
    lg.add(cyl_between((x0, 0.40, -0.075), (x0, 0.22, -0.065), 0.018, n=8), G, angle=60)
    lg.add(rows_loft([(0.185, 0.076, 0.076, 0.0, x0), (0.215, 0.07, 0.07, 0.0, x0)], n=14, cap0='ngon', cap1='ngon'), G, angle=60)
    foot = zloft([(-0.1, 0.05, 0.04, 0.07, x0), (-0.07, 0.085, 0.07, 0.076, x0), (0.0, 0.098, 0.082, 0.082, x0), (0.08, 0.1, 0.07, 0.07, x0),
                  (0.17, 0.094, 0.055, 0.058, x0), (0.235, 0.075, 0.042, 0.046, x0), (0.262, 0.04, 0.03, 0.04, x0)], n=14, e=2.8)
    lg.add(foot, SKIN, angle=55)
    sole = zloft([(-0.108, 0.055, 0.02, 0.02, x0), (-0.04, 0.092, 0.02, 0.02, x0), (0.12, 0.104, 0.02, 0.02, x0), (0.24, 0.08, 0.02, 0.02, x0), (0.272, 0.042, 0.02, 0.02, x0)], n=14, e=3.2)
    lg.add(sole, G, angle=55)
    lg.add(box_at((x0, 0.11, 0.125), (0.1, 0.012, 0.012), r=0.004, s=1), B, ao=1.0)
    return lg


def robot_head(nm):
    h = Part(nm("head"), PV["head"])
    h.add(rows_loft([(1.1, 0.07, 0.07, 0.0), (1.2, 0.062, 0.062, 0.0), (1.28, 0.062, 0.062, 0.0)], n=12, cap0='ngon', cap1='ngon'), G, angle=60)
    rows = [(1.255, 0.085, 0.08, 0.0), (1.29, 0.15, 0.14, 0.0), (1.345, 0.198, 0.19, 0.0), (1.41, 0.218, 0.208, 0.0), (1.48, 0.222, 0.212, -0.002),
            (1.55, 0.208, 0.2, -0.005), (1.61, 0.17, 0.165, -0.006), (1.65, 0.1, 0.1, -0.006), (1.665, 0.0, 0.0, -0.006)]
    h.add(rows_loft(rows, n=26, e=2.3, k=14), SKIN, angle=55)
    # écran-visière (verre sombre), yeux lumineux, bouche à LED
    h.add(zdisc(0, 1.45, 0.178, 1.0, depth=0.034, n=20, rx=0.15, ry=0.085, r2=0.97, e=3.0), SKIN, ao=0.1, angle=60)
    h.add(zdisc(0, 1.45, 0.16, 1.0, depth=0.012, n=20, rx=0.165, ry=0.098, e=3.0), G, angle=60)
    for sx in (-1, 1):
        h.add(zdisc(sx * 0.06, 1.455, 0.205, 1.0, depth=0.016, n=12, rx=0.026, ry=0.036, e=2.4), B, ao=1.0)
    h.add(led_row(-0.045, 0.045, 1.37, 0.205, n=5, r=0.0085), B, ao=1.0)
    h.add(box_at((0, 1.33, 0.2), (0.11, 0.028, 0.018), r=0.006), G)
    h.add([xdisc(sx * 0.225, 1.43, 0.0, 0.068, depth=0.045, n=12) for sx in (-1, 1)], G, angle=60)
    h.add([xdisc(sx * 0.255, 1.43, 0.0, 0.034, depth=0.02, n=10) for sx in (-1, 1)], SKIN, angle=60)
    h.add(rows_loft([(1.64, 0.052, 0.05, -0.005), (1.672, 0.045, 0.043, -0.005)], n=12, cap0='ngon', cap1='ngon'), G, angle=60)
    return h


def robot():
    nm = nm_fn('robot')
    parts = {"torso": robot_torso(nm), "pelvis": robot_pelvis(nm), "head": robot_head(nm)}
    a = robot_arm(nm)
    parts["arm_l"] = a
    parts["arm_r"] = a.mirrored(nm("arm_r"), PV["arm_r"])
    l = robot_leg(nm)
    parts["leg_l"] = l
    parts["leg_r"] = l.mirrored(nm("leg_r"), PV["leg_r"])
    return parts


# =============================================================================================== ALIEN
def alien_torso(nm):
    t = Part(nm("torso"), PV["torso"])
    rows = [(0.72, 0.125, 0.09, 0.0), (0.80, 0.135, 0.095, 0.0), (0.90, 0.16, 0.108, 0.004), (1.0, 0.195, 0.118, 0.008), (1.07, 0.212, 0.12, 0.008),
            (1.13, 0.19, 0.105, 0.0), (1.17, 0.085, 0.07, -0.004), (1.19, 0.06, 0.055, -0.004)]
    tg = rows_loft(rows, n=24, e=2.3, k=14)
    stamp(tg, (0.0, 1.0, 0.12), (0.1, 0.1, 0.05), 0.006)
    stamp(tg, (0.0, 1.05, 0.12), (0.012, 0.08, 0.03), -0.006)
    t.add(tg, SKIN, angle=None)
    # marques phosphorescentes discrètes sur le sternum
    t.add([sphere(0.009, 0.009, 0.006, n=6, m=4).t(0, y, 0.133) for y in (1.1, 1.06, 1.02)], B, ao=1.0)
    return t


def alien_pelvis(nm):
    p = Part(nm("pelvis"), PV["pelvis"])
    rows = [(0.60, 0.115, 0.085, 0.0), (0.66, 0.15, 0.108, 0.003), (0.74, 0.165, 0.115, 0.003), (0.82, 0.15, 0.11, 0.003), (0.86, 0.11, 0.085, 0.0)]
    p.add(rows_loft(rows, n=20, e=2.3, k=9), R, angle=60)
    p.add(rows_loft([(0.79, 0.17, 0.12, 0.003), (0.825, 0.168, 0.118, 0.003)], n=20, cap0='ngon', cap1='ngon'), G, angle=60)
    return p


def finger(base, d, L, r, curl=0.0, n=6):
    """doigt fin : 3 segments qui s'incurvent."""
    base = np.asarray(base, float)
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    side = np.cross(d, [0, 1, 0]) if abs(d[1]) < 0.9 else np.array([1.0, 0, 0])
    side /= np.linalg.norm(side)
    pts = [base]
    cur = d
    for k in range(3):
        cur = cur + side * 0.0 + np.array([0, -curl, curl * 0.6])
        cur = cur / np.linalg.norm(cur)
        pts.append(pts[-1] + cur * L / 3)
    pts = np.array(pts)
    rad = [r, r * 0.9, r * 0.75, r * 0.5]
    g = tube(pts, rad, n=n, cap0='ngon', cap1='fan')
    g2 = sphere(r * 0.62, r * 0.62, r * 0.62, n=6, m=4).at(pts[-1])
    return [g, g2]


def alien_arm(nm):
    a = Part(nm("arm_l"), PV["arm_l"])
    keys = [(1.19, 0.03, 0.03, 0.29, 0.0), (1.165, 0.052, 0.052, 0.295, 0.0), (1.15, 0.06, 0.06, 0.298, 0.0), (1.10, 0.058, 0.058, 0.303, 0.0),
            (1.02, 0.05, 0.05, 0.308, 0.0), (0.93, 0.043, 0.043, 0.313, -0.003), (0.87, 0.041, 0.041, 0.318, -0.004), (0.80, 0.047, 0.047, 0.326, 0.004),
            (0.72, 0.037, 0.037, 0.334, 0.012), (0.67, 0.032, 0.032, 0.338, 0.016)]
    ys = [1.19, 1.17, 1.15, 1.10, 1.02, 0.93, 0.87, 0.80, 0.74, 0.69, 0.66]
    ag = limb(humanoid.arm_rows(keys, ys), n=12)
    a.add(ag, SKIN, angle=None)
    # main : paume + 3 longs doigts + pouce opposable
    hx = 0.34
    a.add(sphere(0.036, 0.042, 0.028, n=10, m=6).t(hx, 0.635, 0.02), SKIN, angle=60)
    for k, dx in enumerate((-0.022, 0.0, 0.022)):
        a.add(finger((hx + dx, 0.61, 0.036), (0.0, -0.55, 0.78), 0.1 - 0.008 * abs(k - 1), 0.0095, curl=0.35), SKIN, angle=60)
    a.add(finger((hx - 0.034, 0.64, 0.025), (-0.9, -0.25, 0.4), 0.065, 0.011, curl=0.3), SKIN, angle=60)
    return a


def alien_leg(nm):
    lg = Part(nm("leg_l"), PV["leg_l"])
    x0 = 0.13
    keys = [(0.76, 0.075, 0.08, x0, 0.0), (0.66, 0.068, 0.072, x0, 0.0), (0.52, 0.054, 0.058, x0, 0.0), (0.44, 0.044, 0.048, x0, 0.0),
            (0.36, 0.04, 0.043, x0, -0.004), (0.26, 0.034, 0.037, x0, -0.004), (0.16, 0.032, 0.035, x0, 0.0), (0.09, 0.034, 0.04, x0, 0.01)]
    rows = [(y,) + tuple(humanoid.lerp_rows(keys, y)) for y in (0.76, 0.7, 0.62, 0.54, 0.46, 0.38, 0.3, 0.22, 0.15, 0.09)]
    lgm = limb(rows, n=12, cap0='fan', cap1='ngon')
    stamp(lgm, (x0, 0.5, 0.045), (0.04, 0.08, 0.04), 0.004)
    lg.add(lgm, SKIN, angle=None)
    # pied à 3 orteils longs + talon
    lg.add(sphere(0.042, 0.032, 0.058, n=10, m=6).t(x0, 0.045, 0.01), SKIN, angle=60)
    for dx in (-0.032, 0.0, 0.032):
        pts = np.array([[x0 + dx * 0.5, 0.05, 0.05], [x0 + dx * 1.1, 0.03, 0.12], [x0 + dx * 1.5, 0.018, 0.195]])
        lg.add(tube(pts, [0.02, 0.018, 0.013], n=8, cap0='fan', cap1='fan'), SKIN, angle=60)
        lg.add(sphere(0.014, 0.011, 0.014, n=6, m=4).t(*pts[-1]), SKIN, angle=60)
    return lg


def alien_head(nm):
    h = Part(nm("head"), PV["head"])
    neck_piece(h, 0.052)
    rows = [(1.17, 0.05, 0.047, 0.115), (1.21, 0.085, 0.072, 0.1), (1.27, 0.115, 0.108, 0.075), (1.33, 0.14, 0.135, 0.05), (1.40, 0.185, 0.17, 0.022),
            (1.48, 0.222, 0.2, 0.0), (1.57, 0.24, 0.215, -0.018), (1.66, 0.235, 0.215, -0.04), (1.75, 0.205, 0.19, -0.058), (1.82, 0.15, 0.14, -0.068),
            (1.87, 0.08, 0.08, -0.07), (1.895, 0.0, 0.0, -0.07)]
    hd = rows_loft(rows, n=26, e=2.15, k=15, warp=0.3)
    # arcades discrètes, joues creuses, menton fin, petits trous de narines
    stamp(hd, (0.1, 1.55, 0.2), (0.07, 0.02, 0.05), 0.012, mirror=True, rotz=-18)
    stamp(hd, (0.095, 1.5, 0.2), (0.075, 0.04, 0.04), -0.016, mirror=True, rotz=-24)
    stamp(hd, (0.13, 1.36, 0.14), (0.05, 0.05, 0.05), -0.012, mirror=True)
    stamp(hd, (0.0, 1.22, 0.1), (0.03, 0.03, 0.04), 0.008)
    stamp(hd, (0.0, 1.30, 0.158), (0.034, 0.008, 0.02), -0.008)
    stamp(hd, (0.0, 1.38, 0.18), (0.014, 0.03, 0.025), 0.01)
    hd2 = hd
    h.add(hd2, SKIN, angle=None)
    # grands yeux sombres en amande + reflet
    for sx in (-1, 1):
        g = sphere(0.088, 0.046, 0.034, n=14, m=8).rz(sx * 24).t(sx * 0.105, 1.5, 0.188)
        h.add(g, SKIN, ao=0.06, angle=70)
        h.add(sphere(0.012, 0.012, 0.008, n=6, m=4).t(sx * 0.095 + 0.0, 1.512, 0.218), SKIN, ao=1.0)
    h.add([sphere(0.006, 0.006, 0.005, n=5, m=3).t(sx * 0.014, 1.355, 0.192) for sx in (-1, 1)], SKIN, ao=0.15)
    # petite marque phosphorescente frontale
    h.add(sphere(0.012, 0.016, 0.006, n=7, m=4).t(0, 1.66, 0.2), B, ao=1.0)
    return h


def alien():
    nm = nm_fn('alien')
    parts = {"torso": alien_torso(nm), "pelvis": alien_pelvis(nm), "head": alien_head(nm)}
    a = alien_arm(nm)
    parts["arm_l"] = a
    parts["arm_r"] = a.mirrored(nm("arm_r"), PV["arm_r"])
    l = alien_leg(nm)
    parts["leg_l"] = l
    parts["leg_r"] = l.mirrored(nm("leg_r"), PV["leg_r"])
    return parts


SPECIES = {'robot': robot, 'alien': alien}
