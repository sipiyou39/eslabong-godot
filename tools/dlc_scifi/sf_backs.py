"""Dos sci-fi : origine = pivot torse (0,0.78,0). Le dos du perso est à z<0."""
from sf_common import *


def B_(name):
    return Part(name, TORSO_P)


def straps(p):
    for sx in (-1, 1):
        p.add(strap([(sx * 0.14, 1.17, -0.12), (sx * 0.15, 1.12, 0.1), (sx * 0.2, 0.95, 0.16), (sx * 0.2, 0.8, 0.05)], w=0.022, th=0.01), G)


def back_jetpack():
    p = B_("back_jetpack")
    for sx in (-1, 1):
        x = sx * 0.115
        body = lathe([(0.0, 0.0), (0.072, 0.0), (0.078, 0.03), (0.078, 0.42), (0.068, 0.45), (0.0, 0.46)], n=14, rz=1.0).t(x, 0.74, -0.29)
        p.add(body, R, angle=55)
        p.add(lathe([(0.05, 0.0), (0.065, -0.04), (0.09, -0.1), (0.098, -0.13)], n=12, rz=1.0).t(x, 0.74, -0.29), G, angle=55)
        p.add(zdisc(0, 0, 0, 0.001), B, ao=1.0) if False else None
        p.add(lathe([(0.075, 0.0), (0.0, 0.0)], n=12, cap=None).t(x, 0.615, -0.29), B, ao=1.0)
        p.add(torus(0.079, 0.012, 12, 4).t(x, 0.9, -0.29), G)
        p.add(torus(0.079, 0.012, 12, 4).t(x, 1.1, -0.29), G)
        p.add(box_at((x, 1.2, -0.29), (0.05, 0.02, 0.05), r=0.005), B, ao=1.0)
    p.add(box_at((0, 0.98, -0.235), (0.26, 0.05, 0.05), r=0.01), G, angle=55)
    p.add(box_at((0, 0.82, -0.235), (0.26, 0.05, 0.05), r=0.01), G, angle=55)
    p.add(box_at((0, 0.9, -0.225), (0.07, 0.3, 0.03), r=0.008), R, angle=55)
    straps(p)
    return p


def back_drone():
    p = B_("back_drone")
    c = np.array([0.3, 1.4, -0.3])
    p.add(sphere(0.105, 0.088, 0.105, n=14, m=8).t(*c), R, angle=60)
    p.add(torus(0.118, 0.018, 16, 4).t(*c), G)
    p.add(sphere(0.05, 0.05, 0.03, n=10, m=6).t(c[0], c[1] + 0.012, c[2] + 0.098), SKIN, ao=0.08)
    p.add(sphere(0.028, 0.028, 0.016, n=8, m=5).t(c[0], c[1] + 0.012, c[2] + 0.12), B, ao=1.0)
    for sx in (-1, 1):
        p.add(box_at((c[0] + sx * 0.14, c[1] + 0.012, c[2] - 0.01), (0.09, 0.02, 0.04), r=0.005), G, angle=55)
        p.add(disc(0.07, c[1] + 0.04, n=12, h=0.01, cx=c[0] + sx * 0.19, cz=c[2] - 0.01), G, angle=55)
        p.add(cyl_between((c[0] + sx * 0.19, c[1] + 0.012, c[2] - 0.01), (c[0] + sx * 0.19, c[1] + 0.04, c[2] - 0.01), 0.01, n=6), R)
    p.add(cyl_between((c[0] - 0.02, c[1] + 0.08, c[2] - 0.02), (c[0] - 0.05, c[1] + 0.2, c[2] - 0.05), 0.007, n=5), G)
    p.add(sphere(0.016, 0.016, 0.016, n=6, m=4).t(c[0] - 0.05, c[1] + 0.205, c[2] - 0.05), B, ao=1.0)
    p.add(sphere(0.018, 0.018, 0.018, n=6, m=4).t(c[0], c[1] - 0.085, c[2]), B, ao=1.0)
    # support de maintien discret sur l'omoplate
    p.add(box_at((0.26, 1.15, -0.25), (0.08, 0.05, 0.1), r=0.012), G, angle=55)
    straps(p)
    return p


def back_antenna_dish():
    p = B_("back_antenna_dish")
    p.add(box_at((0, 0.92, -0.225), (0.2, 0.26, 0.04), r=0.012), G, angle=55)
    p.add(box_at((0, 0.82, -0.255), (0.1, 0.1, 0.04), r=0.01), R, angle=55)
    p.add(ctube(np.array([[0, 0.9, -0.25], [0, 1.15, -0.27], [0.02, 1.4, -0.3]]), 0.016, m=2, n=6), G)
    p.add(sphere(0.026, 0.026, 0.026, n=8, m=5).t(0.02, 1.42, -0.3), G, angle=60)
    # parabole : coque (R) inclinée vers l'arrière/haut + cornet B
    dish = lathe([(0.0, 0.0), (0.06, 0.006), (0.11, 0.026), (0.15, 0.058), (0.17, 0.09), (0.15, 0.092), (0.11, 0.062), (0.06, 0.03), (0.0, 0.016)], n=18, rz=1.0)
    dish.rx(-110).t(0.02, 1.46, -0.31)
    p.add(dish, R, angle=55)
    p.add(torus(0.17, 0.012, 16, 4).rx(-110).t(0.02, 1.46 + 0.09 * math.sin(math.radians(70)) * 0.0 + 0.0, -0.31), G) if False else None
    foc = np.array([0.02, 1.46, -0.31]) + np.array([0, 0.0, 0.0])
    p.add(cyl_between((0.02, 1.47, -0.33), (0.02, 1.54, -0.4), 0.007, n=5), G)
    p.add(sphere(0.02, 0.02, 0.02, n=8, m=5).t(0.02, 1.545, -0.405), B, ao=1.0)
    p.add([cube((0.0 + sx * 0.04, 0.96, -0.247), (0.02, 0.02, 0.012)) for sx in (-1, 0, 1)], B, ao=1.0, angle=40)
    straps(p)
    return p


def back_reactor():
    p = B_("back_reactor")
    p.add(box_at((0, 0.97, -0.3), (0.34, 0.42, 0.15), r=0.02), R, angle=55)
    p.add(box_at((0, 0.97, -0.385), (0.26, 0.34, 0.03), r=0.012), G, angle=55)
    # cœur de réacteur en cylindre vertical, anneaux lumineux
    p.add(lathe([(0.0, 0.0), (0.07, 0.0), (0.075, 0.02), (0.075, 0.26), (0.07, 0.28), (0.0, 0.28)], n=14, rz=1.0).t(0, 0.83, -0.405), G, angle=55)
    for y in (0.87, 0.93, 0.99, 1.05):
        p.add(torus(0.077, 0.012, 14, 4).t(0, y, -0.405), B, ao=1.0)
    p.add(zdisc(0, 0.97, -0.44, 0.03, depth=0.01, n=10), B, ao=1.0) if False else None
    # ailettes de refroidissement latérales
    for sx in (-1, 1):
        for i in range(4):
            p.add(box_at((sx * 0.19, 0.84 + 0.07 * i, -0.3), (0.05, 0.022, 0.12), r=0.004), G, angle=50)
        p.add(cyl_between((sx * 0.12, 1.17, -0.27), (sx * 0.12, 1.28, -0.3), 0.02, 0.016, n=8), G, angle=55)
    # tuyaux vers les épaules
    for sx in (-1, 1):
        p.add(ctube(np.array([[sx * 0.1, 1.2, -0.28], [sx * 0.18, 1.26, -0.2], [sx * 0.25, 1.18, -0.12]]), 0.014, m=2, n=5), G)
    p.add(box_at((0, 1.22, -0.3), (0.2, 0.03, 0.1), r=0.008), G, angle=55)
    p.add([cube((sx * 0.1, 1.2, -0.355), (0.04, 0.02, 0.012)) for sx in (-1, 1)], B, ao=1.0, angle=40)
    straps(p)
    return p


BACKS = [back_jetpack, back_drone, back_antenna_dish, back_reactor]
