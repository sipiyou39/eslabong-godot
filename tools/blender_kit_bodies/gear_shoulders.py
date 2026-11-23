"""Épaulières : shoulder_<nom>_l / _r, origine = pivot épaule (0.30,1.10,0)."""
from gear_common import *

SC = np.array([0.315, 1.135, 0.0])      # centre approximatif du dôme d'épaule (côté gauche, x>0)


def dome(R=0.14, h=0.11, n=18, tilt=18, rz=None, y0=-0.03, e=2.0, steps=5, lip=True):
    prof = []
    if lip:
        prof.append((R * 0.97, y0))
    for k in range(steps + 1):
        a = math.pi / 2 * k / steps
        prof.append((R * math.cos(a) + (0.003 if k == 0 else 0), h * math.sin(a)))
    prof[-1] = (0.0, h)
    g = lathe(prof, n=n, rz=rz if rz else 1.0, e=e)
    return g


def place(g, tilt=18, dx=0.0, dy=0.0, dz=0.0, roll=0.0):
    g.rz(-tilt)
    if roll:
        g.rx(roll)
    return g.t(SC[0] + dx, SC[1] + dy, SC[2] + dz)


def rim(R, tilt, y=0.0, r=0.012, dx=0.0, dy=0.0, dz=0.0):
    return place(torus(R, r, 22, 6), tilt, dx, dy + y, dz)


def mk(name, side_geos):
    """side_geos : liste de (geo, col, kwargs) pour le côté gauche ; renvoie (part_l, part_r)."""
    l = Part(f"shoulder_{name}_l", PIVOTS["shoulder_l"])
    for g, col, kw in side_geos:
        l.add(g, col, **kw)
    r = l.mirrored(f"shoulder_{name}_r", PIVOTS["shoulder_r"])
    return [l, r]


def sh_plate():
    out = []
    for k, (rr, h, dy, dx) in enumerate([(0.15, 0.1, 0.0, 0.0), (0.135, 0.09, 0.02, 0.0), (0.115, 0.08, 0.04, -0.005)]):
        out.append((place(dome(rr, h, n=20), 20, dx, dy), R, {'angle': 60}))
        out.append((rim(rr, 20, dy - 0.02, 0.011, dx, 0.0), G, {}))
    out.append((place(sphere(0.022, 0.022, 0.022, n=8, m=5), 20, 0.0, 0.17), B, {}))
    out.append((place(sphere(0.012, 0.012, 0.012, n=6, m=4), 20, 0.11, 0.03, 0.06), B, {}))
    return mk("plate", out)


def sh_spiked():
    out = [(place(dome(0.145, 0.1, n=20), 20), R, {'angle': 60}), (rim(0.145, 20, -0.02, 0.014), B, {})]
    for ax, az, L in [(0, 0, 0.17), (0.07, 0.07, 0.11), (0.07, -0.07, 0.11), (-0.06, 0.0, 0.09)]:
        base = np.array([SC[0] + ax - 0.02 * (ax > 0), SC[1] + 0.085 - 0.01 * abs(ax) * 6, az])
        d = np.array([ax * 2 + 0.2, 1.0, az * 2])
        out.append((spike(base, base + d / np.linalg.norm(d) * L, r=0.032, n=8, bulge=0.75), G, {}))
    return mk("spiked", out)


def sh_fur():
    out = [(place(dome(0.12, 0.09, n=18), 22), R, {'angle': 60})]
    ts = []
    rng = np.random.RandomState(4)
    for k in range(26):
        a = 2 * math.pi * k / 26
        for ring, (rr, yy) in enumerate([(0.14, 1.12), (0.1, 1.2)]):
            if ring == 1 and k % 2:
                continue
            ts.append((SC[0] + rr * math.cos(a) * 1.0 + 0.0, yy - 0.03 * math.cos(a), rr * math.sin(a) * 1.1))
    out.append((merge(tufts(ts, (0.4, 0.5, 0.0), length=0.1, r=0.04, seed=2, jitter=0.5)), G, {}))
    out.append((rim(0.135, 22, -0.025, 0.014), G, {}))
    out.append((place(sphere(0.02, 0.02, 0.02, n=8, m=5), 22, 0.0, 0.1), B, {}))
    return mk("fur", out)


def sh_mantle():
    out = []
    prof = [(0.17, -0.15), (0.165, -0.12), (0.15, -0.04), (0.125, 0.04), (0.08, 0.1), (0.0, 0.125)]
    g = lathe(prof, n=24, rz=1.0)
    g = place(g, 25, 0.015, 0.0)
    out.append((g, R, {'angle': 60}))
    out.append((place(lathe([(0.176, -0.158), (0.176, -0.12), (0.168, -0.12), (0.168, -0.158)], n=24), 25, 0.015, 0.0), G, {'angle': 60}))
    out.append((place(sphere(0.02, 0.02, 0.014, n=8, m=5), 25, 0.12, 0.0, 0.14), B, {}))
    return mk("mantle", out)


def sh_big():
    out = [(place(dome(0.19, 0.15, n=22), 15, 0.015, 0.0), R, {'angle': 60}), (rim(0.19, 15, -0.02, 0.016, 0.015), G, {}),
           (place(dome(0.12, 0.12, n=18), 15, 0.015, 0.06), R, {'angle': 60}), (rim(0.12, 15, 0.06 - 0.01, 0.012, 0.015), G, {}),
           (place(sphere(0.04, 0.03, 0.04, n=10, m=6), 15, 0.015, 0.2), B, {})]
    for a in (0, 120, 240):
        th = math.radians(a)
        out.append((place(sphere(0.012, 0.012, 0.012, n=6, m=4), 15, 0.015 + 0.17 * math.cos(th), 0.07, 0.17 * math.sin(th)), B, {}))
    return mk("big", out)


def sh_bone():
    out = [(place(dome(0.125, 0.08, n=18), 20), G, {'angle': 60}), (rim(0.125, 20, -0.02, 0.016), R, {})]
    for az, L in [(0.06, 1.0), (-0.06, 1.0)]:
        base = np.array([SC[0] + 0.05, SC[1] + 0.06, az])
        tip = np.array([SC[0] + 0.1, SC[1] + 0.27 * L, az * 1.8])
        out.append((horn(base, tip, r=0.035, curve_out=0.05, curve_dir=(0.8, 0.0, 0.0), n=8, m=7), G, {}))
    out.append((place(sphere(0.03, 0.03, 0.03, n=8, m=5), 20, -0.04, 0.09, 0.0), G, {}))
    return mk("bone", out)


def sh_flame():
    out = [(place(dome(0.14, 0.09, n=20), 20), R, {'angle': 60}), (rim(0.14, 20, -0.02, 0.013), G, {})]
    for ax, az, L, r in [(0.0, 0.0, 0.26, 0.04), (0.06, 0.08, 0.18, 0.032), (0.06, -0.08, 0.18, 0.032), (-0.05, 0.03, 0.13, 0.026)]:
        base = np.array([SC[0] + ax, SC[1] + 0.08, az])
        tip = base + np.array([0.03 + ax, L, az * 0.5 - 0.05])
        out.append((horn(base, tip, r=r, curve_out=0.04, curve_dir=(0.5, 0.0, -0.5), n=7, m=7), B, {}))
    return mk("flame", out)


def sh_frost():
    out = [(place(dome(0.14, 0.09, n=20), 20), R, {'angle': 60}), (rim(0.14, 20, -0.02, 0.013), G, {})]
    for ax, az, L, r, tl in [(0.0, 0.0, 0.2, 0.04, 0), (0.07, 0.07, 0.15, 0.03, 30), (0.07, -0.07, 0.15, 0.03, -30), (-0.06, 0.02, 0.11, 0.026, 10), (0.12, 0.0, 0.1, 0.024, 50)]:
        base = np.array([SC[0] + ax, SC[1] + 0.07, az])
        d = np.array([math.sin(math.radians(abs(tl))) * (1 if ax >= 0 else -1) + 0.2, math.cos(math.radians(tl)), az * 2])
        out.append((spike(base, base + d / np.linalg.norm(d) * L, r=r, n=5, bulge=0.45), B, {}))
    return mk("frost", out)


def sh_leather():
    out = [(place(dome(0.13, 0.07, n=18), 20), R, {'angle': 60}), (rim(0.13, 20, -0.02, 0.012), G, {})]
    out.append((place(rbox(0.012, 0.02, 0.13, r=0.006), 20, 0.0, 0.075), G, {}))
    out.append((place(rbox(0.13, 0.014, 0.012, r=0.006), 20, 0.0, 0.065, 0.0), G, {}))
    out.append((place(sphere(0.014, 0.014, 0.012, n=6, m=4), 20, 0.0, 0.092), B, {}))
    out.append((place(sphere(0.011, 0.011, 0.011, n=6, m=4), 20, 0.1, 0.03, 0.06), B, {}))
    out.append((place(sphere(0.011, 0.011, 0.011, n=6, m=4), 20, 0.1, 0.03, -0.06), B, {}))
    return mk("leather", out)


SHOULDER_FN = [("plate", sh_plate), ("spiked", sh_spiked), ("fur", sh_fur), ("mantle", sh_mantle), ("big", sh_big), ("bone", sh_bone),
               ("flame", sh_flame), ("frost", sh_frost), ("leather", sh_leather)]
# chaque fonction renvoie [part_l, part_r]
SHOULDERS = [fn for _, fn in SHOULDER_FN]
