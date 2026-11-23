from wcommon import *
from registry import weapon


def face(part, z=0.0):
    """pièce de révolution autour de Y -> autour de Z (axe vers +Z)."""
    return part.xf(rot=(90, 0, 0), pos=(0, 0, z))


def back_handle(w=0.14, z=-0.045, y=0.0, strap=True):
    p = [box((w, 0.026, 0.026), (0, y, z), color=G, bevel=0.005),
         box((0.03, 0.04, 0.028), (-w / 2, y, z + 0.012), color=G, bevel=0.004),
         box((0.03, 0.04, 0.028), (w / 2, y, z + 0.012), color=G, bevel=0.004)]
    if strap:
        pts = bezier((0.0, y + 0.14, -0.012), (0.1, y + 0.14, z - 0.05), (0.14, y - 0.12, z - 0.05), (0.0, y - 0.14, -0.012), 10)
        p.append(tube(pts * np.array([1, 1, 1]), 0.014, seg=5, color=R))
    return p


def outline_tube(poly2, r, z=0.0, color=G, seg=6):
    pts = np.array([(x, y, z) for x, y in poly2])
    return tube(pts, r, seg=seg, color=color, closed_path=True)


@weapon("wpn_shield_round", notes="bouclier rond 0,72 m, face +Z, boss central", views="front,tq")
def shield_round():
    p = []
    prof = [(0, -0.012), (0.2, -0.014), (0.345, -0.022), (0.345, 0.012), (0.2, 0.03), (0.09, 0.04), (0.0, 0.042)]
    p.append(face(lathe(prof, 24, R, bevel=None)))
    p.append(torus(0.345, 0.02, 32, 6, plane="XY", color=G, pos=(0, 0, -0.004)))
    for k in range(12):
        a = math.radians(30 * k + 15)
        p.append(sphere(0.012, 5, 3, B, pos=(0.345 * math.cos(a), 0.345 * math.sin(a), 0.016)))
    for k in range(4):   # sangles
        a = 90 * k + 45
        st = box((0.05, 0.3, 0.014), (0, 0.19, 0.03), color=G, bevel=0.003).xf(rot=(0, 0, -a))
        p.append(st)
    p.append(face(lathe([(0.0, 0.0), (0.098, 0.0), (0.098, 0.03), (0.0, 0.03)], 16, G, bevel=0.003), 0.04))
    p.append(face(lathe([(0.085, 0.0), (0.095, 0.02), (0.075, 0.07), (0.035, 0.1), (0.0, 0.11)], 14, B, bevel=0.002), 0.055))
    p.append(cone(0.016, 0.06, 6, B, pos=(0, 0, 0.16), rot=(90, 0, 0)))
    p += back_handle()
    return p


KITE = [(0.0, -0.56), (0.11, -0.47), (0.2, -0.33), (0.25, -0.14), (0.265, 0.06), (0.265, 0.26), (0.235, 0.37), (0.15, 0.405), (0.0, 0.385)]
KITE = KITE + [(-x, y) for x, y in KITE[1:-1]][::-1]


@weapon("wpn_shield_kite", notes="écu 0,95 m, pointe vers -Y, face +Z", views="front,tq")
def shield_kite():
    p = []
    poly = [(x, y) for x, y in KITE]
    n = len(poly)
    p.append(plate(poly, 0.03, 0.1, plane="XY", color=R, edge_color=R))
    p.append(outline_tube(poly, 0.017, 0.0, G))
    p.append(box((0.07, 0.9, 0.012), (0, -0.08, 0.03), color=G, bevel=0.003))
    p.append(box((0.45, 0.07, 0.012), (0, 0.17, 0.03), color=G, bevel=0.003))
    p.append(face(lathe([(0.0, 0.0), (0.07, 0.0), (0.07, 0.03), (0.0, 0.03)], 12, G, bevel=0.003), 0.035).xf(pos=(0, 0.17, 0)))
    p.append(face(lathe([(0.0, 0.0), (0.06, 0.005), (0.05, 0.04), (0.0, 0.06)], 10, B, bevel=0.002), 0.05).xf(pos=(0, 0.17, 0)))
    for x, y in [(-0.2, 0.33), (0.2, 0.33), (-0.19, -0.16), (0.19, -0.16), (0.0, -0.37)]:
        p.append(sphere(0.013, 5, 3, B, pos=(x, y, 0.036)))
    p += back_handle(y=0.0)
    return p


@weapon("wpn_shield_tower", notes="pavois 1,2 m, face +Z, bombé", views="front,tq")
def shield_tower():
    p = []
    W, H = 0.31, 0.6
    xs = np.linspace(-W, W, 9)
    front = [(x, 0.07 * (1 - (x / W) ** 2)) for x in xs]
    back = [(x, 0.07 * (1 - (x / W) ** 2) - 0.035) for x in xs[::-1]]
    sec = front + back
    sec = [(x, z) for x, z in sec]
    p.append(slab(sec, H, plane="XZ", color=R, bevel=0.006))
    for yy in (H - 0.03, -H + 0.03):
        rim = [(x, 0.07 * (1 - (x / (W + 0.02)) ** 2) + 0.012) for x in np.linspace(-W - 0.02, W + 0.02, 9)]
        rim2 = [(x, z - 0.06) for x, z in rim[::-1]]
        p.append(slab(rim + rim2, 0.03, plane="XZ", color=G, bevel=0.005).xf(pos=(0, yy, 0)))
    for x in (-W + 0.0, W):
        p.append(box((0.04, 2 * H, 0.04), (x * 1.0, 0.0, 0.0), color=G, bevel=0.006).xf(pos=(0, 0, 0.07 * (1 - (x / W) ** 2) - 0.012)))
    p.append(box((0.045, 2 * H - 0.1, 0.014), (0, 0, 0.082), color=G, bevel=0.003))
    for yy in (0.3, 0.0, -0.3):
        p.append(box((2 * W, 0.04, 0.012), (0, yy, 0.07 * 0.97 + 0.0), color=G, bevel=0.003) if False else sphere(0.016, 5, 3, B, pos=(0.0, yy, 0.09)))
    for x in (-0.2, 0.2):
        for yy in (0.45, -0.45, 0.0):
            p.append(sphere(0.012, 5, 3, B, pos=(x, yy, 0.07 * (1 - (x / W) ** 2) + 0.004)))
    p.append(box((0.2, 0.06, 0.012), (0, 0.38, 0.092), color=B, bevel=0.002))   # fente de visée (cadre)
    p += back_handle(y=0.0, z=-0.07)
    return p


@weapon("wpn_shield_buckler", notes="rondache 0,36 m, grand boss pointu", views="front,tq")
def shield_buckler():
    p = []
    prof = [(0, -0.01), (0.12, -0.012), (0.17, -0.015), (0.17, 0.01), (0.1, 0.022), (0.0, 0.025)]
    p.append(face(lathe(prof, 18, R)))
    p.append(torus(0.17, 0.013, 24, 6, plane="XY", color=G, pos=(0, 0, 0)))
    p.append(face(lathe([(0.0, 0.0), (0.075, 0.0), (0.082, 0.02), (0.06, 0.05), (0.02, 0.075), (0.0, 0.08)], 12, B, bevel=0.002), 0.025))
    p.append(cone(0.014, 0.08, 6, G, pos=(0, 0, 0.1), rot=(90, 0, 0)))
    for k in range(6):
        a = math.radians(60 * k)
        p.append(sphere(0.009, 5, 3, B, pos=(0.14 * math.cos(a), 0.14 * math.sin(a), 0.02)))
    p += back_handle(0.1, -0.03, 0.0, strap=False)
    return p
