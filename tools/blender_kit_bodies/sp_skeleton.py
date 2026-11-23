"""Squelette : os épais lisibles (peau = couleur os), orbites lumineuses (B)."""
from bodies_common import *
import heads


def _bone(p0, p1, r0, r1=None, n=8, knob0=0.0, knob1=0.0, mid=0.0):
    """os long : tube avec renflement central léger + épiphyses sphériques."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    if r1 is None:
        r1 = r0
    m = 6
    path = np.array([p0 + (p1 - p0) * k / (m - 1) for k in range(m)])
    rad = [(r0 + (r1 - r0) * k / (m - 1)) * (1.0 - mid * math.sin(math.pi * k / (m - 1)) * 0.0) * (0.85 + 0.15 * math.cos(math.pi * (k / (m - 1) * 2 - 1)) ** 2 * 0 + 0.3 * (1 - abs(k / (m - 1) * 2 - 1))) for k in range(m)]
    # forme en sablier inversé : plus fin au milieu
    rad = [(r0 + (r1 - r0) * k / (m - 1)) * (0.78 + 0.35 * abs(k / (m - 1) * 2 - 1) ** 1.5) for k in range(m)]
    out = [tube(path, rad, n=n, cap0='fan', cap1='fan', up=(0, 0, 1))]
    if knob0:
        out.append(sphere(knob0, knob0 * 0.9, knob0, n=10, m=7).at(p0))
    if knob1:
        out.append(sphere(knob1, knob1 * 0.9, knob1, n=10, m=7).at(p1))
    return out


def build():
    nm = lambda p: f"body_skeleton_{p}"
    parts = {}

    # ---------------- torse : colonne + cage thoracique
    t = Part(nm("torso"), PV["torso"])
    spine_path = curve([(0, 0.72, -0.045), (0, 0.85, -0.06), (0, 1.0, -0.075), (0, 1.12, -0.07), (0, 1.2, -0.05)], 2)
    t.add(tube(spine_path, [0.034] * len(spine_path), n=8), SKIN, angle=60)
    verts = []
    for k in range(9):
        y = 0.74 + k * 0.054
        z = np.interp(y, [0.72, 0.85, 1.0, 1.12, 1.2], [-0.045, -0.06, -0.075, -0.07, -0.05])
        verts.append(sphere(0.045, 0.024, 0.045, n=8, m=4).t(0, y, z))
    t.add(verts, SKIN, angle=60)
    ribs = []
    ys = [1.13, 1.075, 1.02, 0.965, 0.91, 0.855]
    rxs = [0.19, 0.225, 0.235, 0.225, 0.2, 0.17]
    rzs = [0.105, 0.125, 0.135, 0.135, 0.125, 0.11]
    for y, rx, rz in zip(ys, rxs, rzs):
        for sx in (-1, 1):
            pts = []
            for i in range(8):
                phi = -0.47 * math.pi + i * (0.97 * math.pi) / 7
                x = sx * rx * math.cos(phi) * (1 if True else 1)
                z = 0.015 + rz * math.sin(phi)
                pts.append((x, y - 0.04 * (i / 7.0) ** 1.5, z))
            pts[-1] = (sx * 0.02, pts[-1][1], pts[-1][2] + 0.0)
            pts = np.array(pts)
            rad = [0.021 * (1.0 + 0.2 * math.sin(math.pi * k / 7)) for k in range(8)]
            ribs.append(tube(pts, rad, n=6, up=(0, 1, 0)))
    t.add(ribs, SKIN, angle=60)
    sternum = rbox(0.03, 0.12, 0.014, r=0.01).t(0, 0.99, 0.14)
    sternum.map(lambda V: V * 1.0)
    t.add(sternum, SKIN, angle=60)
    for sx in (-1, 1):
        t.add(_bone((sx * 0.02, 1.15, 0.12), (sx * 0.27, 1.14, -0.01), 0.022, 0.02, n=7, knob1=0.035), SKIN, angle=60)   # clavicules
        blade = sphere(0.085, 0.1, 0.014, n=12, m=7).rz(sx * 10).t(sx * 0.12, 1.02, -0.12)
        t.add(blade, SKIN, angle=60)
    parts["torso"] = t

    # ---------------- bassin
    p = Part(nm("pelvis"), PV["pelvis"])
    for sx in (-1, 1):
        wing = sphere(0.11, 0.075, 0.05, n=14, m=8).rz(sx * -22).ry(sx * 12).t(sx * 0.11, 0.8, 0.0)
        p.add(wing, SKIN, angle=60)
        isch = _bone((sx * 0.09, 0.72, 0.03), (sx * 0.03, 0.62, 0.09), 0.03, 0.026, n=8, knob1=0.035)
        p.add(isch, SKIN, angle=60)
    p.add(sphere(0.07, 0.09, 0.04, n=10, m=7).t(0, 0.74, -0.08), SKIN, angle=60)
    p.add(torus(0.09, 0.022, 20, 8).sc(1.0, 1.0, 0.8).t(0, 0.625, 0.04), SKIN, angle=60)
    p.add(torus(0.1, 0.012, 20, 6).sc(1.0, 1.0, 0.9).t(0, 0.86, 0.0), SKIN, angle=60) if False else None
    parts["pelvis"] = p

    # ---------------- crâne
    h = Part(nm("head"), PV["head"])
    for k in range(4):
        h.add(sphere(0.045, 0.02, 0.045, n=10, m=5).t(0, 1.10 + k * 0.045, -0.01), SKIN, angle=60)
    rows = [(1.27, 0.07, 0.07, 0.07), (1.30, 0.115, 0.11, 0.07), (1.34, 0.155, 0.15, 0.05), (1.38, 0.18, 0.18, 0.025), (1.42, 0.195, 0.2, 0.0),
            (1.47, 0.2, 0.21, -0.01), (1.52, 0.196, 0.21, -0.015), (1.575, 0.175, 0.19, -0.02), (1.615, 0.135, 0.15, -0.02),
            (1.64, 0.08, 0.09, -0.02), (1.655, 0.0, 0.0, -0.02)]
    hd = rows_loft(rows, n=30, e=2.2, k=24, warp=0.4)
    stamp(hd, (0.085, 1.43, 0.2), (0.05, 0.045, 0.05), -0.05, mirror=True)          # orbites
    stamp(hd, (0, 1.36, 0.19), (0.03, 0.04, 0.04), -0.045)                             # cavité nasale
    stamp(hd, (0.12, 1.34, 0.13), (0.045, 0.035, 0.05), 0.02, mirror=True)              # pommettes
    stamp(hd, (0.17, 1.35, 0.03), (0.04, 0.05, 0.07), -0.02, mirror=True)               # tempes creuses
    stamp(hd, (0, 1.54, 0.18), (0.1, 0.07, 0.06), 0.012)
    h.add(hd, SKIN, angle=None)
    for sx in (-1, 1):
        h.add(sphere(0.034, 0.034, 0.028, n=8, m=5).t(sx * 0.086, 1.43, 0.15), B, ao=1.0, angle=70)   # lueur
        h.add(sphere(0.052, 0.045, 0.03, n=12, m=7).t(sx * 0.086, 1.43, 0.175), SKIN, ao=0.18, angle=70) if False else None
    # mâchoire + dents
    jaw = tube(curve([(-0.115, 1.34, 0.0), (-0.105, 1.255, 0.07), (-0.06, 1.2, 0.15), (0, 1.185, 0.175), (0.06, 1.2, 0.15), (0.105, 1.255, 0.07),
                      (0.115, 1.34, 0.0)], 2), [0.034] * 13, n=8, cap0='fan', cap1='fan', up=(0, 1, 0))
    h.add(jaw, SKIN, angle=60)
    teeth = []
    for i in range(9):
        a = -0.45 * math.pi + i * 0.9 * math.pi / 8
        x, z = 0.1 * math.sin(a) * 1.0, 0.07 + 0.105 * math.cos(a)
        teeth.append(lathe([(0.012, 0.0), (0.012, 0.02), (0.0, 0.024)], n=5, rz=0.8).t(x, 1.27, z + 0.065))
    for i in range(9):
        a = -0.45 * math.pi + i * 0.9 * math.pi / 8
        x, z = 0.095 * math.sin(a), 0.07 + 0.1 * math.cos(a)
        teeth.append(lathe([(0.012, 0.0), (0.012, 0.018), (0.0, 0.022)], n=5, rz=0.8).t(x, 1.225, z + 0.065))
    h.add(teeth, SKIN, angle=60)
    parts["head"] = h

    # ---------------- bras
    a = Part(nm("arm_l"), PV["arm_l"])
    S, E, W = (0.30, 1.10, 0.0), (0.322, 0.87, -0.008), (0.338, 0.69, 0.02)
    a.add(_bone((0.30, 1.1, 0), E, 0.036, 0.032, n=10, knob0=0.062, knob1=0.045), SKIN, angle=60)
    a.add(_bone((0.322, 0.87, -0.008), (0.335, 0.70, 0.03), 0.028, 0.026, n=8, knob1=0.034), SKIN, angle=60)   # radius
    a.add(_bone((0.30, 0.86, -0.045), (0.325, 0.70, -0.02), 0.024, 0.02, n=8, knob0=0.035), SKIN, angle=60)   # cubitus
    hand = [rbox(0.045, 0.045, 0.04, r=0.015).t(0.34, 0.64, 0.02)]
    for dy in (-0.03, -0.01, 0.01, 0.03):
        hand.append(tube(curve([(0.34 - 0.04, 0.62 + dy, 0.045), (0.34, 0.62 + dy, 0.075), (0.34 + 0.04, 0.62 + dy, 0.045)], 3), [0.012] * 7, n=6))
    hand.append(sphere(0.02, 0.03, 0.02, n=8, m=6).t(0.305, 0.66, 0.06))
    a.add(hand, SKIN, angle=60)
    parts["arm_l"] = a
    parts["arm_r"] = a.mirrored(nm("arm_r"), PV["arm_r"])

    # ---------------- jambe
    lg = Part(nm("leg_l"), PV["leg_l"])
    x0 = 0.13
    lg.add(sphere(0.062, 0.055, 0.062, n=12, m=8).t(x0 + 0.03, 0.74, 0.0), SKIN, angle=60)       # tête du fémur
    lg.add(_bone((x0 + 0.03, 0.74, 0.0), (x0, 0.45, 0.02), 0.04, 0.044, n=10, knob1=0.058), SKIN, angle=60)
    lg.add(sphere(0.052, 0.04, 0.045, n=10, m=7).t(x0, 0.44, 0.055), SKIN, angle=60)             # rotule
    lg.add(_bone((x0, 0.43, 0.0), (x0, 0.11, 0.0), 0.04, 0.036, n=10, knob1=0.05), SKIN, angle=60)   # tibia
    lg.add(_bone((x0 - 0.04, 0.42, -0.02), (x0 - 0.04, 0.12, -0.02), 0.02, 0.018, n=8), SKIN, angle=60)   # péroné
    foot = [rbox(0.055, 0.035, 0.07, r=0.02).t(x0, 0.07, 0.01)]
    for i, dx in enumerate((-0.04, -0.02, 0.0, 0.02, 0.04)):
        foot.append(tube(curve([(x0 + dx, 0.055, 0.06), (x0 + dx, 0.03, 0.13), (x0 + dx * 1.1, 0.02, 0.2)], 3), [0.015 - i * 0.0006] * 7, n=6))
    foot.append(sphere(0.042, 0.04, 0.05, n=10, m=7).t(x0, 0.06, -0.06))
    lg.add(foot, SKIN, angle=60)
    parts["leg_l"] = lg
    parts["leg_r"] = lg.mirrored(nm("leg_r"), PV["leg_r"])
    return parts
