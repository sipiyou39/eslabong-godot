"""Invocations sci-fi : drone volant (centré à y=0.65) et tourelle laser (pose au sol, canons vers +Z)."""
from sf_common import *

O = (0.0, 0.0, 0.0)


def summon_drone():
    p = Part("summon_drone", O)
    cy = 0.65
    p.add(sphere(0.2, 0.135, 0.23, n=14, m=7).t(0, cy, 0), R, angle=60)
    p.add(torus(0.2, 0.02, 14, 3).sc(1.0, 1.0, 1.15).t(0, cy, 0), G)                     # ceinture
    # œil capteur à l'avant
    p.add(sphere(0.095, 0.095, 0.05, n=12, m=6).t(0, cy + 0.01, 0.2), G, angle=60)
    p.add(sphere(0.07, 0.07, 0.035, n=10, m=5).t(0, cy + 0.01, 0.225), SKIN, ao=0.08)
    p.add(sphere(0.032, 0.032, 0.02, n=10, m=6).t(0, cy + 0.01, 0.255), B, ao=1.0)
    # quatre bras à rotor protégé
    for sx in (-1, 1):
        for sz in (-1, 1):
            e = np.array([sx * 0.36, cy + 0.07, sz * 0.3])
            p.add(cyl_between((sx * 0.14, cy + 0.02, sz * 0.12), tuple(e), 0.028, 0.022, n=6), G, angle=55)
            p.add(cyl_between(e - np.array([0, 0.045, 0]), e + np.array([0, 0.045, 0]), 0.045, n=8), R, angle=55)
            p.add(torus(0.18, 0.012, 12, 3).t(e[0], e[1] + 0.065, e[2]), G)
            p.add(disc(0.165, e[1] + 0.06, n=12, h=0.006, cx=e[0], cz=e[2]), B, ao=0.6)
            p.add(cyl_between(e + np.array([0, 0.045, 0]), e + np.array([0, 0.068, 0]), 0.012, n=5), G)
    # nacelle de tir sous le ventre + antenne dorsale
    p.add(box_at((0, cy - 0.15, 0.1), (0.1, 0.07, 0.16), r=0.015), G, angle=55)
    p.add(zc_(0, cy - 0.155, 0.17, 0.3, 0.018, 0.014), G, angle=55)
    p.add(zc_(0, cy - 0.155, 0.298, 0.312, 0.016, 0.016), B, ao=1.0)
    p.add(cyl_between((0.04, cy + 0.12, -0.12), (0.06, cy + 0.3, -0.16), 0.008, n=5), G)
    p.add(sphere(0.02, 0.02, 0.02, n=6, m=4).t(0.06, cy + 0.305, -0.16), B, ao=1.0)
    p.add([sphere(0.016, 0.016, 0.016, n=6, m=4).t(sx * 0.1, cy - 0.1, -0.15) for sx in (-1, 1)], B, ao=1.0)
    return p


def zc_(x, y, z0, z1, r0, r1=None, n=8):
    return cyl_between((x, y, z0), (x, y, z1), r0, r1, n=n)


def summon_turret_laser():
    p = Part("summon_turret_laser", O)
    # embase + trépied
    p.add(lathe([(0.0, 0.0), (0.42, 0.0), (0.44, 0.03), (0.4, 0.07), (0.2, 0.09), (0.0, 0.09)], n=12, rz=1.0), G, angle=55)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        c, s_ = math.cos(a), math.sin(a)
        p.add(cyl_between((0.12 * c, 0.1, 0.12 * s_), (0.4 * c, 0.05, 0.4 * s_), 0.035, 0.05, n=7), R, angle=55)
        p.add(box_at((0.42 * c, 0.03, 0.42 * s_), (0.12, 0.05, 0.12), r=0.012, yaw=-a), G, angle=55)
    # colonne + collerette tournante
    p.add(lathe([(0.12, 0.09), (0.1, 0.2), (0.1, 0.5), (0.14, 0.54)], n=12, rz=1.0), R, angle=55)
    p.add(torus(0.13, 0.025, 14, 4).t(0, 0.56, 0), G)
    p.add([cyl_between((sx * 0.1, 0.2, -0.08), (sx * 0.1, 0.5, -0.08), 0.02, n=6) for sx in (-1, 1)], G, angle=55)
    # tourelle
    p.add(box_at((0, 0.72, 0.0), (0.36, 0.26, 0.44), r=0.045), R, angle=55)
    p.add(box_at((0, 0.72, 0.17), (0.3, 0.2, 0.14), r=0.03), G, angle=55)
    p.add(box_at((0, 0.88, -0.06), (0.22, 0.08, 0.26), r=0.02), R, angle=55)
    for sx in (-1, 1):
        # canons jumeaux avec bobines
        p.add(zc_(sx * 0.1, 0.73, 0.22, 0.78, 0.04, 0.032, n=8), G, angle=55)
        for z in (0.36, 0.52, 0.68):
            p.add(zc_(sx * 0.1, 0.73, z - 0.014, z + 0.014, 0.055, n=8), R, angle=55)
        p.add(zc_(sx * 0.1, 0.73, 0.775, 0.8, 0.03, 0.044, n=10), G, angle=55)
        p.add(zc_(sx * 0.1, 0.73, 0.795, 0.806, 0.026, n=10), B, ao=1.0)
        p.add(box_at((sx * 0.185, 0.72, 0.02), (0.025, 0.14, 0.2), r=0.006), G, angle=55)
        p.add(box_at((sx * 0.195, 0.72, 0.02), (0.01, 0.1, 0.14), r=0.003), B, ao=1.0)
    # capteur en dôme + antenne + évents arrière
    p.add(sphere(0.07, 0.05, 0.07, n=12, m=6).t(0, 0.94, 0.0), G, angle=55)
    p.add(sphere(0.035, 0.035, 0.03, n=8, m=5).t(0, 0.955, 0.05), B, ao=1.0)
    p.add(cyl_between((-0.1, 0.92, -0.14), (-0.12, 1.12, -0.16), 0.008, n=5), G)
    p.add(sphere(0.018, 0.018, 0.018, n=6, m=4).t(-0.12, 1.125, -0.16), B, ao=1.0)
    p.add([cube((0, 0.66 + 0.04 * i, -0.225), (0.2, 0.014, 0.014)) for i in range(4)], G, angle=40)
    return p


SUMMONS = [summon_drone, summon_turret_laser]
