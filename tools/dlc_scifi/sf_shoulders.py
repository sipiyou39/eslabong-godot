"""Épaulières sci-fi : shoulder_<nom>_l / _r, origine = pivot épaule (0.30,1.10,0). Modélisées côté gauche (+x) puis miroir."""
from sf_common import *
from gear_shoulders import dome, place, SC


def mk(name, side_geos):
    l = Part(f"shoulder_{name}_l", PIVOTS["shoulder_l"])
    for g, col, kw in side_geos:
        l.add(g, col, **kw)
    r = l.mirrored(f"shoulder_{name}_r", PIVOTS["shoulder_r"])
    return [l, r]


def at(g, tilt, dx=0.0, dy=0.0, dz=0.0):
    return place(g, tilt, dx, dy, dz)


def sh_tech():
    out = []
    out.append((box_at((SC[0] + 0.012, SC[1] + 0.012, 0.0), (0.25, 0.058, 0.25), r=0.016, roll=-20), R, {'angle': 55}))
    out.append((box_at((SC[0] + 0.006, SC[1] + 0.068, 0.0), (0.17, 0.046, 0.18), r=0.014, roll=-20), R, {'angle': 55}))
    out.append((box_at((SC[0] + 0.118, SC[1] - 0.03, 0.0), (0.036, 0.08, 0.25), r=0.01, roll=-20), G, {'angle': 55}))
    out.append((box_at((SC[0] + 0.01, SC[1] + 0.04, 0.13), (0.25, 0.03, 0.03), r=0.007, roll=-20), G, {'angle': 55}))
    out.append((box_at((SC[0] + 0.01, SC[1] + 0.04, -0.13), (0.25, 0.03, 0.03), r=0.007, roll=-20), G, {'angle': 55}))
    out.append((box_at((SC[0] + 0.132, SC[1] - 0.008, 0.0), (0.012, 0.024, 0.19), r=0.004, roll=-20), B, {'ao': 1.0}))
    out.append((cyl_between((SC[0] - 0.04, SC[1] + 0.1, -0.1), (SC[0] - 0.06, SC[1] + 0.24, -0.11), 0.008, n=6), G, {}))
    out.append((sphere(0.016, 0.016, 0.016, n=6, m=4).t(SC[0] - 0.06, SC[1] + 0.245, -0.11), B, {'ao': 1.0}))
    out.append((merge([sphere(0.011, 0.011, 0.011, n=5, m=3).t(SC[0] + x, SC[1] + 0.096, z) for (x, z) in ((0.045, 0.06), (0.045, -0.06), (-0.035, 0.06), (-0.035, -0.06))]), B, {'ao': 1.0}))
    out.append((box_at((SC[0] - 0.02, SC[1] + 0.105, 0.0), (0.06, 0.02, 0.07), r=0.006, roll=-20), G, {'angle': 50}))
    return mk("tech", out)


def sh_jet():
    out = []
    out.append((at(dome(0.135, 0.085, n=16), 20), R, {'angle': 60}))
    out.append((at(torus(0.135, 0.011, 14, 4), 20, 0.0, -0.02), G, {}))
    # nacelle propulseur sur le dessus, tuyère vers l'arrière
    z0, y0, x0 = 0.04, SC[1] + 0.09, SC[0] - 0.01
    body = lathe([(0.052, 0.0), (0.058, 0.04), (0.058, 0.17), (0.05, 0.2)], n=12, rz=1.0)
    body.rx(-90).t(x0, y0, z0)                       # axe local Y -> -Z (vers l'arrière)
    out.append((body, R, {'angle': 55}))
    noz = lathe([(0.05, 0.0), (0.06, 0.03), (0.082, 0.1), (0.088, 0.12)], n=12, rz=1.0)
    noz.rx(-90).t(x0, y0, z0 - 0.2)
    out.append((noz, G, {'angle': 55}))
    out.append((zdisc(x0, y0, z0 - 0.286, 0.055, depth=0.006, n=12), B, {'ao': 1.0}))
    out.append((zdisc(x0, y0, z0 - 0.288, 0.024, depth=0.01, n=10), SKIN, {'ao': 1.0}))
    out.append((box_at((x0, y0 - 0.045, z0 + 0.02), (0.04, 0.05, 0.12), r=0.008), G, {'angle': 55}))
    out.append((cube((x0 + 0.062, y0, z0 - 0.06), (0.01, 0.018, 0.08)), B, {'ao': 1.0}))
    return mk("jet", out)


def sh_dome():
    out = [(at(dome(0.18, 0.14, n=18), 15, 0.015, 0.0), R, {'angle': 60}),
           (at(torus(0.18, 0.016, 16, 4), 15, 0.015, -0.02), G, {}),
           (at(dome(0.115, 0.1, n=14), 15, 0.015, 0.075), G, {'angle': 60}),
           (at(torus(0.09, 0.011, 14, 4), 15, 0.015, 0.14), B, {'ao': 1.0}),
           (at(sphere(0.026, 0.02, 0.026, n=8, m=5), 15, 0.015, 0.22), B, {'ao': 1.0})]
    for a in (0, 90, 180, 270):
        th = math.radians(a)
        out.append((at(cube((0.15 * math.cos(th), 0.075, 0.15 * math.sin(th)), (0.022, 0.03, 0.022)), 15, 0.015, 0.0), G, {'angle': 40}))
    return mk("dome", out)


SHOULDERS = [sh_tech, sh_jet, sh_dome]
