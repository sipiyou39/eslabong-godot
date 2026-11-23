from wcommon import *
from registry import weapon


def shaft(top=0.95, bottom=-0.68, r=0.0205, twist=0.0, rtop=None, color=R, seg=8, n=11):
    rtop = r if rtop is None else rtop
    ys = np.linspace(bottom, top, n)
    t = np.linspace(0, 1, n)
    pts = np.stack([twist * np.sin(ys * 5.0), ys, twist * 0.8 * np.cos(ys * 4.3)], 1)
    return tube(pts, r + (rtop - r) * t, seg=seg, color=color)


def base_gear(bottom=-0.68, r=0.0205, gripc=R):
    p = [grip(-0.16, 0.12, r * 1.2, pitch=0.036, color=gripc),
         cone(r * 0.95, 0.08, 6, G, pos=(0, bottom, 0.0), rot=(180, 0, 0)),
         band(bottom + 0.09, r * 1.15, 0.03)]
    return p


def grow(parts, k=1.3, y0=0.88):
    return [q.xf(s=k, pos=(0, y0 * (1 - k), 0)) for q in parts]


def finish_staff(p, n0, k, y0, ysq=0.64, xz=1.12):
    """fût raccourci/épaissi, tête agrandie sans déformation."""
    body = [q.xf(s=(xz, ysq, xz)) for q in p[:n0]]
    head = [q.xf(s=k * xz, pos=(0, y0 * (1 - k * xz) + (ysq - 1.0) * y0 + 0.0, 0)) for q in p[n0:]]
    return body + head


def collar(y, r=0.024, h=0.09, color=G, flare=1.6):
    return lathe([(r, y), (r * flare, y + h * 0.35), (r * 1.15, y + h * 0.75), (r * 1.3, y + h)], 8, color, bevel=0.003)


def prongs(n, y0, y1, r0, r1, rad, color=G, bulge=0.04, phase=0.0, seg=5, tilt=0.0):
    out = []
    for k in range(n):
        a = math.radians(phase + 360.0 * k / n)
        ca, sa = math.cos(a), math.sin(a)
        p0 = (r0 * ca, y0, r0 * sa)
        p3 = (r1 * ca, y1, r1 * sa)
        p1 = ((r0 + bulge * 1.4) * ca, y0 + (y1 - y0) * 0.25, (r0 + bulge * 1.4) * sa)
        p2 = ((r1 + bulge) * ca, y0 + (y1 - y0) * 0.75, (r1 + bulge) * sa)
        pts = bezier(p0, p1, p2, p3, 9)
        out.append(tube(pts, np.linspace(rad, rad * 0.45, 9), seg=seg, color=color))
    return out


@weapon("wpn_staff_wood", accent=(0.45, 0.85, 0.35), notes="bâton noueux de druide 1,9 m, fourche et gemme")
def staff_wood():
    p = [shaft(0.9, -0.68, 0.0215, twist=0.012, rtop=0.03, seg=8)]
    p += base_gear(-0.68, 0.0215)
    for y, rr in ((-0.3, 0.024), (0.35, 0.027), (0.6, 0.029)):
        p.append(sphere(rr * 0.9, 6, 4, R, pos=(0.012 * math.sin(y * 5), y, 0.01), s=(1.1, 0.9, 1.0)))
    n0 = len(p)
    p.append(band(0.86, 0.034, 0.034, G, flare=1.15))
    for k in range(3):
        a = math.radians(90 + 120 * k)
        ca, sa = math.cos(a), math.sin(a)
        pts = bezier((0, 0.87, 0), (0.1 * ca, 0.93, 0.1 * sa), (0.13 * ca, 1.1, 0.13 * sa), (0.04 * ca, 1.24, 0.04 * sa), 10)
        p.append(tube(pts, np.linspace(0.02, 0.008, 10), seg=6, color=R))
        p.append(sphere(0.012, 5, 3, R, pos=pts[-1]))
    p.append(gem(0.05, 0.13, 6, B, pos=(0, 1.08, 0)))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        p.append(cyl((0.034 * math.cos(a), 0.83, 0.034 * math.sin(a)), (0.052 * math.cos(a), 0.76, 0.052 * math.sin(a)), 0.01, 0.0, seg=4, color=R))
    p = finish_staff(p, n0, 1.3, 0.86)
    return p


@weapon("wpn_staff_crystal", accent=(0.35, 0.65, 1.0), notes="bâton de mage à grand cristal 1,9 m")
def staff_crystal():
    p = [shaft(0.9, -0.68, 0.0205, rtop=0.0225)]
    p += base_gear(-0.68, 0.0205)
    p.append(band(0.3, 0.025, 0.025))
    p.append(band(0.6, 0.025, 0.025))
    n0 = len(p)
    p.append(collar(0.88, 0.026, 0.1))
    p += prongs(4, 0.97, 1.2, 0.058, 0.032, 0.012, G, 0.05, 45)
    p.append(lathe([(0, 1.0), (0.062, 1.07), (0.07, 1.16), (0.04, 1.27), (0, 1.38)], 6, B, phase=30))
    p.append(lathe([(0.036, 1.19), (0.0, 1.26)], 6, G) if False else cone(0.014, 0.05, 5, G, pos=(0, 1.38, 0)))
    for s in (1, -1):
        p.append(gem(0.018, 0.05, 5, B, pos=(s * 0.1, 1.2, 0.0), rot=(0, 0, s * 18)))
        p.append(gem(0.012, 0.035, 5, B, pos=(s * 0.13, 1.06, 0.03), rot=(0, 0, s * -10)))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        p.append(gem(0.011, 0.024, 4, B, pos=(0.04 * math.cos(a), 0.9, 0.04 * math.sin(a))))
    p = finish_staff(p, n0, 1.3, 0.88)
    return p


@weapon("wpn_staff_fire", accent=(1.0, 0.5, 0.12), notes="bâton de feu 1,8 m, coupe et flamme")
def staff_fire():
    p = [shaft(0.9, -0.68, 0.0205, rtop=0.023)]
    p += base_gear(-0.68, 0.0205)
    p.append(band(0.4, 0.025, 0.025))
    n0 = len(p)
    p.append(lathe([(0.026, 0.86), (0.05, 0.92), (0.085, 1.0), (0.1, 1.07), (0.092, 1.1), (0.075, 1.09), (0.08, 1.05), (0.058, 0.99), (0.0, 0.97)], 10, G, bevel=0.002))
    for k in range(5):
        a = 72 * k
        ar = math.radians(a)
        p.append(cyl((0.09 * math.cos(ar), 1.06, 0.09 * math.sin(ar)), (0.125 * math.cos(ar), 1.16, 0.125 * math.sin(ar)), 0.016, 0.0, seg=4, color=G))
    p.append(lathe([(0.0, 0.98), (0.06, 1.03), (0.074, 1.1), (0.06, 1.2), (0.032, 1.3), (0.0, 1.42)], 8, B))
    for k in range(3):
        a = 120 * k + 30
        ar = math.radians(a)
        p.append(lathe([(0, 0), (0.026, 0.03), (0.02, 0.1), (0.0, 0.2)], 6, B).xf(pos=(0.052 * math.cos(ar), 1.08, 0.052 * math.sin(ar)), rot=(math.sin(ar) * 22, 0, -math.cos(ar) * 22)))
    p = finish_staff(p, n0, 1.3, 0.86)
    return p


@weapon("wpn_staff_ice", accent=(0.55, 0.9, 1.0), notes="bâton de givre 1,85 m, grappe de cristaux")
def staff_ice():
    p = [shaft(0.9, -0.68, 0.0205, twist=0.006, rtop=0.024)]
    p += base_gear(-0.68, 0.0205)
    p.append(band(0.35, 0.026, 0.025))
    n0 = len(p)
    p.append(collar(0.86, 0.027, 0.09))
    p.append(lathe([(0.0, 0.96), (0.05, 1.02), (0.052, 1.2), (0.0, 1.5)], 6, B, phase=20))
    specs = [(0, 28, 0.036, 0.34), (72, 22, 0.03, 0.27), (144, 34, 0.03, 0.3), (216, 20, 0.027, 0.24), (288, 30, 0.032, 0.28)]
    for ang, tilt, rr, hh in specs:
        ar = math.radians(ang)
        cr = lathe([(0.0, 0.0), (rr, 0.05), (rr * 0.95, hh * 0.65), (0.0, hh)], 6, B, phase=ang)
        p.append(cr.xf(pos=(0.03 * math.cos(ar), 0.95, 0.03 * math.sin(ar)), rot=(math.sin(ar) * tilt, 0, -math.cos(ar) * tilt)))
    for k in range(6):
        a = math.radians(60 * k + 20)
        p.append(cone(0.012, 0.05, 4, B, pos=(0.04 * math.cos(a), 0.88, 0.04 * math.sin(a)), rot=(180 - math.sin(a) * 35, 0, math.cos(a) * 35 + 0)))
    p = finish_staff(p, n0, 1.25, 0.86)
    return p


@weapon("wpn_staff_storm", accent=(0.6, 0.85, 1.0), notes="bâton de tempête 1,85 m, deux cornes et éclair")
def staff_storm():
    p = [shaft(0.9, -0.68, 0.0205, rtop=0.023)]
    p += base_gear(-0.68, 0.0205)
    p.append(band(0.4, 0.025, 0.025))
    n0 = len(p)
    p.append(collar(0.86, 0.026, 0.09))
    for s in (1, -1):
        pts = bezier((s * 0.02, 0.93, 0), (s * 0.15, 0.98, 0), (s * 0.2, 1.12, 0), (s * 0.06, 1.32, 0), 12)
        p.append(tube(pts, np.linspace(0.02, 0.008, 12), seg=6, color=G))
        p.append(cone(0.012, 0.05, 5, B, pos=pts[-1] + np.array([0, 0.0, 0]), rot=(0, 0, s * -20)))
    p.append(sphere(0.045, 8, 6, B, pos=(0, 1.1, 0)))
    zz = [(0.0, 1.0, 0.0), (0.035, 1.08, 0.0), (-0.03, 1.14, 0.0), (0.03, 1.22, 0.0), (-0.01, 1.3, 0.0)]
    p.append(tube([(0.0, 1.0, 0.0), (0.04, 1.07, 0.0), (-0.035, 1.13, 0.0), (0.04, 1.2, 0.0), (-0.02, 1.27, 0.0), (0.0, 1.36, 0.0)], np.linspace(0.013, 0.004, 6), seg=4, color=B))
    p.append(torus(0.036, 0.007, 14, 4, plane="XZ", pos=(0, 0.92, 0), color=B))
    p = finish_staff(p, n0, 1.3, 0.86)
    return p


@weapon("wpn_staff_void", accent=(0.7, 0.25, 1.0), notes="bâton du néant 1,85 m, orbe et anneaux flottants")
def staff_void():
    p = [shaft(0.9, -0.68, 0.0185, twist=0.0, rtop=0.02, color=G)]
    p += base_gear(-0.68, 0.0185, gripc=G)
    p.append(band(0.4, 0.023, 0.024, R))
    n0 = len(p)
    p.append(collar(0.86, 0.024, 0.09, R))
    p += prongs(3, 0.95, 1.0, 0.04, 0.035, 0.01, G, 0.02, 0)
    p.append(sphere(0.07, 12, 8, B, pos=(0, 1.15, 0)))
    p.append(torus(0.13, 0.008, 18, 4, plane="XZ", color=G).xf(rot=(0, 0, 32)).xf(pos=(0, 1.15, 0)))
    p.append(torus(0.16, 0.007, 18, 4, plane="XZ", color=R).xf(rot=(32, 0, -50)).xf(pos=(0, 1.15, 0)))
    for k in range(3):
        a = math.radians(120 * k + 20)
        p.append(gem(0.018, 0.07, 4, B, pos=(0.19 * math.cos(a), 1.15 + 0.06 * math.sin(a * 2), 0.19 * math.sin(a)), rot=(10 * k, 0, 15)))
    p.append(gem(0.022, 0.08, 4, B, pos=(0.0, 1.38, 0.0)))
    for s in (1, -1):
        p.append(cone(0.012, 0.06, 4, G, pos=(s * 0.04, 0.85, 0), rot=(180, 0, 0)))
    p = finish_staff(p, n0, 1.25, 0.86)
    return p


@weapon("wpn_staff_holy", accent=(1.0, 0.85, 0.35), notes="bâton sacré 1,85 m, soleil à rayons, face +Z")
def staff_holy():
    p = [shaft(0.9, -0.68, 0.0205, rtop=0.022)]
    p += base_gear(-0.68, 0.0205)
    p.append(band(0.45, 0.025, 0.025, B))
    p.append(band(0.8, 0.026, 0.03, B))
    n0 = len(p)
    p.append(lathe([(0.026, 0.88), (0.05, 0.95), (0.026, 1.0)], 8, B, bevel=0.003))
    cy = 1.18
    disc = lathe([(0.0, -0.014), (0.05, -0.014), (0.056, 0.0), (0.05, 0.014), (0.0, 0.014)], 14, B).xf(pos=(0, cy, 0), rot=(90, 0, 0))
    p.append(disc)
    p.append(torus(0.1, 0.011, 28, 5, plane="XY", pos=(0, cy, 0), color=B))
    p.append(gem(0.02, 0.05, 6, G, pos=(0, cy, 0.016), rot=(90, 0, 0)))
    for k in range(12):
        a = 30 * k
        long = k % 2 == 0
        p.append(cone(0.016 if long else 0.011, 0.11 if long else 0.065, 4, B, pos=(0, 0, 0), rot=(0, 0, 0)).xf(pos=(0, 0.1, 0)).xf(rot=(0, 0, -a)).xf(pos=(0, cy, 0)))
    p.append(box((0.016, 0.07, 0.02), (0, cy + 0.0, 0.0), color=B, bevel=0.002).xf(pos=(0, 0, 0)))
    for s in (1, -1):   # petites ailes
        wing = plate([(0.0, 0.0), (0.06, 0.04), (0.12, 0.1), (0.09, 0.02), (0.07, -0.02), (0.02, -0.025)], 0.006, 0.0, plane="XY", color=B, edge_color=B)
        p.append(wing.xf(pos=(0, 0.93, 0), s=(s, 1, 1)))
    p = finish_staff(p, n0, 1.25, 0.88)
    return p


def skull(s=1.0, color=K, eye=B, pos=(0, 0, 0), rot=(0, 0, 0)):
    out = []
    out.append(sphere(0.062 * s, 9, 6, color, pos=(0, 0.02 * s, 0), s=(1.0, 1.0, 1.1)))
    out.append(box((0.07 * s, 0.05 * s, 0.07 * s), (0, -0.04 * s, 0.045 * s), color=color, bevel=0.006 * s))
    out.append(box((0.058 * s, 0.026 * s, 0.07 * s), (0, -0.085 * s, 0.035 * s), color=color, bevel=0.004 * s))
    for sx in (1, -1):
        out.append(sphere(0.022 * s, 6, 4, G, pos=(sx * 0.03 * s, 0.01 * s, 0.075 * s), s=(1.0, 1.1, 0.7)))
        out.append(sphere(0.011 * s, 5, 3, eye, pos=(sx * 0.03 * s, 0.01 * s, 0.083 * s)))
    out.append(cone(0.012 * s, 0.026 * s, 3, G, pos=(0, -0.025 * s, 0.092 * s), rot=(180, 0, 0)))
    out.append(box((0.05 * s, 0.014 * s, 0.01 * s), (0, -0.062 * s, 0.083 * s), color=G, bevel=None))
    return [q.xf(pos=pos, rot=rot) for q in out]


@weapon("wpn_staff_skull", accent=(0.5, 1.0, 0.4), notes="bâton au crâne 1,8 m ; os = couleur base (K), yeux B")
def staff_skull():
    p = [shaft(0.88, -0.68, 0.0205, twist=0.008, rtop=0.026)]
    p += base_gear(-0.68, 0.0205)
    p.append(band(0.4, 0.025, 0.025))
    n0 = len(p)
    p.append(collar(0.84, 0.028, 0.08))
    p += skull(1.6, K, B, pos=(0, 1.08, 0.0))
    for s in (1, -1):
        horn = bezier((s * 0.08, 1.14, 0), (s * 0.2, 1.16, 0), (s * 0.22, 1.28, 0), (s * 0.15, 1.36, 0), 8)
        p.append(tube(horn, np.linspace(0.026, 0.004, 8), seg=4, color=K))
    p += prongs(3, 0.9, 0.97, 0.04, 0.05, 0.009, G, 0.02, 90)
    for s in (1, -1):
        p.append(tube(bezier((s * 0.03, 0.86, 0.02), (s * 0.12, 0.8, 0.04), (s * 0.12, 0.7, 0.04), (s * 0.08, 0.6, 0.03), 6), 0.005, seg=3, color=G))
        p.append(gem(0.014, 0.04, 4, B, pos=(s * 0.08, 0.58, 0.03)))
    p = finish_staff(p, n0, 1.2, 0.84)
    return p


@weapon("wpn_staff_totem", accent=(0.95, 0.75, 0.2), notes="bâton-totem 1,8 m : tête sculptée à 3 étages, ailes, plumes, perles")
def staff_totem():
    p = [shaft(0.86, -0.68, 0.0235, rtop=0.027)]
    p += base_gear(-0.68, 0.0235)
    p.append(band(0.3, 0.03, 0.024, B))
    p.append(band(0.55, 0.03, 0.024, G))
    n0 = len(p)
    p.append(band(0.88, 0.036, 0.04, G, flare=1.2))
    ys = (0.97, 1.1, 1.23)
    for k, yy in enumerate(ys):
        w_ = (0.15, 0.14, 0.13)[k]
        p.append(box((w_, 0.12, w_), (0, yy, 0), color=R, bevel=0.01))
        for s in (1, -1):
            p.append(sphere(0.021, 5, 3, B, pos=(s * 0.036, yy + 0.012, w_ / 2 + 0.002), s=(1, 1, 0.6)))
            p.append(box((0.055, 0.016, 0.026), (s * 0.036, yy + 0.043, w_ / 2), rot=(0, 0, -s * 14), color=G, bevel=None))
    p.append(cone(0.03, 0.09, 4, B, pos=(0, 1.095, 0.07), rot=(90, 0, 0), bevel=None))
    p.append(box((0.07, 0.026, 0.05), (0, 0.945, 0.085), color=G, bevel=None))
    p.append(box((0.05, 0.034, 0.03), (0, 1.215, 0.075), rot=(-20, 0, 0), color=G, bevel=None))
    for s in (1, -1):
        wing = plate([(0.0, 0.0), (0.11, 0.03), (0.2, 0.1), (0.24, 0.2), (0.12, 0.17), (0.0, 0.12)], 0.012, 0.012, plane="XY", color=R, edge_color=G)
        p.append(wing.xf(pos=(s * 0.06, 1.04, 0.0), s=(s, 1, 1)))
        p.append(cone(0.016, 0.1, 4, B, pos=(s * 0.24, 1.14, 0), rot=(0, 0, -s * 70)))
        p.append(cone(0.02, 0.12, 4, R, pos=(s * 0.06, 1.3, 0), rot=(0, 0, -s * 25)))
    p.append(cone(0.035, 0.16, 5, G, pos=(0, 1.29, 0)))
    for k, dx in enumerate((-0.055, 0.0, 0.055)):
        pth = [(dx, 0.84, 0.05), (dx * 1.25, 0.76, 0.06), (dx * 1.4, 0.68, 0.055)]
        p.append(tube(pth, 0.005, seg=3, color=G))
        p.append(lathe([(0.0, 0), (0.017, 0.035), (0.012, 0.11), (0.0, 0.16)], 4, R if k != 1 else B).xf(pos=(dx * 1.4, 0.68, 0.055), rot=(180, 0, 0)))
    p = finish_staff(p, n0, 1.15, 0.86)
    return p


@weapon("wpn_wand", accent=(0.9, 0.5, 1.0), notes="baguette 0,42 m, pointe cristal")
def wand():
    p = []
    p.append(lathe([(0.016, -0.1), (0.021, -0.085), (0.021, 0.05), (0.014, 0.075), (0.01, 0.3)], 8, R, bevel=0.002))
    p.append(band(-0.11, 0.0, 0.0) if False else sphere(0.022, 6, 4, B, pos=(0, -0.105, 0)))
    p.append(band(0.07, 0.022, 0.024, G))
    p.append(band(-0.04, 0.022, 0.016, G))
    p.append(cone(0.01, 0.05, 6, R, pos=(0, 0.28, 0)))
    p += prongs(3, 0.27, 0.34, 0.02, 0.012, 0.005, G, 0.012, 0)
    p.append(gem(0.021, 0.065, 6, B, pos=(0, 0.33, 0)))
    for k in range(3):
        a = math.radians(120 * k)
        p.append(gem(0.007, 0.02, 4, B, pos=(0.035 * math.cos(a), 0.36 + 0.01 * k, 0.035 * math.sin(a))))
    return p
