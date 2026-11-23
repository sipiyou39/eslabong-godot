from pcommon import *
from registry import prop


@prop("summon_boar", accent=(1.0, 0.35, 0.2), notes="sanglier 0,95 m (long) x 0,62 (haut), regarde +Z")
def boar():
    p = []
    secs = [(-0.43, 0.40, 0.05, 0.07), (-0.39, 0.40, 0.13, 0.15), (-0.22, 0.43, 0.2, 0.21), (0.0, 0.46, 0.225, 0.24), (0.16, 0.49, 0.225, 0.26),
            (0.29, 0.46, 0.19, 0.23), (0.36, 0.42, 0.15, 0.18)]
    p.append(body_loft(secs, 10, belly=K, top=R))
    # tête
    head = [(0.28, 0.42, 0.16, 0.18), (0.42, 0.39, 0.15, 0.16), (0.55, 0.34, 0.11, 0.12), (0.64, 0.31, 0.085, 0.085), (0.68, 0.31, 0.075, 0.07)]
    p.append(body_loft(head, 9, belly=K, top=R))
    p.append(cyl((0, 0.31, 0.665), (0, 0.31, 0.71), 0.085, 0.07, seg=9, color=K, sx=1.0, sz=1.0))
    for s in (1, -1):
        p.append(sphere(0.012, 5, 3, G, pos=(s * 0.03, 0.31, 0.715)))
        p.append(sphere(0.02, 6, 4, B, pos=(s * 0.095, 0.44, 0.52), s=(0.7, 1, 1)))
        p.append(sphere(0.011, 5, 3, G, pos=(s * 0.1, 0.44, 0.535)))
        # défenses
        tusk = bezier((s * 0.07, 0.3, 0.6), (s * 0.13, 0.28, 0.66), (s * 0.17, 0.34, 0.7), (s * 0.15, 0.43, 0.72), 8)
        p.append(tube(tusk, np.linspace(0.026, 0.004, 8), seg=5, color=B))
        # oreilles
        p.append(cone(0.06, 0.15, 4, G, pos=(s * 0.1, 0.52, 0.34), rot=(-20, 0, -s * 25)))
        # pattes
        for zz, x in ((0.22, 0.13), (-0.26, 0.13)):
            p += leg((s * x, 0.3, zz), (s * x, 0.0, zz + 0.01), 0.095, 0.055, R, G, bend=0.0, seg=7, hoof_h=0.06)
    # crête
    cr = [(0.0, 0.7 - 0.02 * abs(z) * 0 + (0.0 if abs(z) < 0.15 else -0.0), z) for z in np.linspace(0.27, -0.33, 8)]
    ys = [0.72, 0.745, 0.735, 0.715, 0.69, 0.66, 0.615, 0.57]
    cr = [(0.0, y - 0.02, z) for y, z in zip(ys, np.linspace(0.27, -0.33, 8))]
    p += spike_row(cr, 0.1, 0.03, G, tilt=(0, 0.6, -0.55), seg=4)
    # queue
    p.append(tube(bezier((0, 0.44, -0.41), (0, 0.5, -0.5), (0.04, 0.55, -0.5), (0.0, 0.5, -0.45), 6), np.linspace(0.02, 0.008, 6), seg=4, color=G))
    return p


@prop("summon_wolf", accent=(0.5, 0.9, 1.0), notes="loup 1,0 m (long) x 0,85 (haut), regarde +Z")
def wolf():
    p = []
    secs = [(-0.38, 0.53, 0.07, 0.09), (-0.34, 0.54, 0.13, 0.16), (-0.18, 0.56, 0.165, 0.21), (0.02, 0.58, 0.19, 0.24), (0.2, 0.6, 0.2, 0.27), (0.33, 0.62, 0.18, 0.25)]
    p.append(body_loft(secs, 10, belly=K, top=R))
    p.append(body_loft([(0.26, 0.62, 0.18, 0.24), (0.42, 0.7, 0.14, 0.18)], 8, belly=R, top=R))
    p.append(sphere(0.14, 9, 6, R, pos=(0, 0.74, 0.5), s=(0.95, 0.92, 1.05)))
    p.append(body_loft([(0.52, 0.72, 0.1, 0.095), (0.64, 0.69, 0.075, 0.07), (0.74, 0.68, 0.052, 0.05)], 8, belly=K, top=R))
    p.append(sphere(0.04, 6, 4, G, pos=(0, 0.7, 0.755), s=(1.0, 0.8, 1.0)))
    p.append(box((0.075, 0.03, 0.2), (0, 0.65, 0.62), color=K, bevel=0.005))
    for s in (1, -1):
        p.append(cone(0.012, 0.035, 4, B, pos=(s * 0.03, 0.668, 0.7), rot=(180, 0, 0)))
        p.append(cone(0.075, 0.2, 4, R, pos=(s * 0.08, 0.84, 0.44), rot=(-12, 0, -s * 14)))
        p.append(cone(0.04, 0.14, 4, G, pos=(s * 0.08, 0.85, 0.45), rot=(-12, 0, -s * 14)))
        p.append(sphere(0.02, 5, 3, B, pos=(s * 0.075, 0.78, 0.6), s=(0.6, 0.8, 1.3)))
        p += leg((s * 0.13, 0.5, 0.25), (s * 0.12, 0.0, 0.28), 0.085, 0.05, R, G, seg=6, hoof_h=0.05)
        p.append(sphere(0.06, 6, 4, G, pos=(s * 0.12, 0.03, 0.3), s=(0.9, 0.55, 1.4)))
        p.append(sphere(0.14, 7, 5, R, pos=(s * 0.15, 0.5, -0.27)))
        p += leg((s * 0.15, 0.46, -0.27), (s * 0.12, 0.0, -0.27), 0.085, 0.05, R, G, bend=0.1, seg=6, hoof_h=0.05, bend_dir=(0, 0, -1))
        p.append(sphere(0.06, 6, 4, G, pos=(s * 0.12, 0.03, -0.25), s=(0.9, 0.55, 1.4)))
        for k in (-1, 0, 1):
            p.append(cone(0.008, 0.035, 3, B, pos=(s * 0.12 + k * 0.022, 0.015, 0.355), rot=(90, 0, 0)))
    # collerette hérissée
    for k in range(12):
        a = math.radians(30 * k)
        c0 = np.array([0.15 * math.cos(a), 0.64 + 0.14 * math.sin(a), 0.34])
        d = np.array([0.5 * math.cos(a), 0.5 * math.sin(a), -0.5])
        p.append(cyl(c0, c0 + d / np.linalg.norm(d) * 0.13, 0.04, 0.0, seg=4, color=G))
    tp = bezier((0, 0.58, -0.4), (0, 0.5, -0.6), (0, 0.35, -0.68), (0, 0.22, -0.6), 9)
    p.append(tube(tp, np.array([0.04, 0.075, 0.095, 0.08, 0.05, 0.03, 0.02, 0.015, 0.01]), seg=6, color=R))
    p.append(sphere(0.045, 5, 3, G, pos=tp[-1], s=(0.8, 1.3, 0.8)))
    ys = np.linspace(0.84, 0.77, 7)
    zs = np.linspace(0.3, -0.3, 7)
    p += spike_row([(0, y - 0.04 + 0.0, z) for y, z in zip(ys, zs)], 0.07, 0.03, G, tilt=(0, 0.6, -0.5), seg=4)
    return p


@prop("summon_bat", accent=(0.8, 0.3, 1.0), notes="chauve-souris, envergure 1,0 m, plane (corps centré à y=0,65)")
def bat():
    p = []
    cy = 0.65
    p.append(sphere(0.08, 9, 6, R, pos=(0, cy, 0), s=(0.9, 1.1, 1.15)))
    p.append(sphere(0.07, 8, 5, R, pos=(0, cy + 0.06, 0.09)))
    p.append(box((0.05, 0.03, 0.05), (0, cy + 0.045, 0.18), color=K, bevel=0.006))
    for s in (1, -1):
        p.append(cone(0.04, 0.16, 4, G, pos=(s * 0.05, cy + 0.11, 0.09), rot=(-8, 0, -s * 8)))
        p.append(sphere(0.014, 5, 3, B, pos=(s * 0.035, cy + 0.085, 0.165)))
        p.append(cone(0.006, 0.03, 3, K, pos=(s * 0.015, cy + 0.03, 0.2), rot=(180, 0, 0)))
        wing_poly = [(0.05, 0.07), (0.2, 0.12), (0.36, 0.2), (0.5, 0.19), (0.66, 0.1), (0.76, -0.06), (0.62, -0.01), (0.56, -0.16), (0.45, -0.04), (0.36, -0.2), (0.26, -0.05), (0.14, -0.16), (0.05, -0.13)]
        pl = plate([(x * s, z) for x, z in wing_poly], 0.006, 0.0, plane="XZ", color=G, edge_color=G)
        pl = pl.xf(rot=(0, 0, s * 20)).xf(pos=(0, cy + 0.02, 0.0))
        p.append(pl)
        # os des ailes
        for tip in ((0.76, -0.06), (0.56, -0.16), (0.36, -0.2), (0.14, -0.16)):
            pts = np.array([(0.08 * s, 0.0, 0.05), (0.42 * s, 0.0, 0.2), (tip[0] * s, 0.0, tip[1])])
            pts = pts @ rotmat(0, 0, s * 20).T + np.array([0, cy + 0.02, 0])
            p.append(tube(pts, [0.009, 0.007, 0.004], seg=4, color=R))
        p.append(sphere(0.018, 5, 3, R, pos=np.array([0.42 * s, 0, 0.2]) @ rotmat(0, 0, s * 20).T + np.array([0, cy + 0.02, 0])))
    p.append(cone(0.03, 0.1, 4, G, pos=(0, cy - 0.03, -0.1), rot=(-105, 0, 0)))
    return p


@prop("summon_wisp", accent=(0.45, 1.0, 0.85), notes="feu follet, flotte (centre à y=0,6), tout en accent B")
def wisp():
    p = []
    cy = 0.6
    p.append(sphere(0.1, 10, 7, B, pos=(0, cy, 0)))
    p.append(lathe([(0.0, 0), (0.07, 0.04), (0.085, 0.1), (0.05, 0.2), (0.0, 0.3)], 8, B).xf(pos=(0, cy + 0.05, 0.0)))
    for k in range(3):
        a = 120 * k + 10
        ar = math.radians(a)
        p.append(lathe([(0.0, 0), (0.045, 0.04), (0.04, 0.12), (0.0, 0.22)], 6, B).xf(rot=(0, 0, 0)).xf(rot=(math.sin(ar) * 55, 0, -math.cos(ar) * 55), pos=(0.06 * math.cos(ar), cy + 0.05, 0.06 * math.sin(ar))) if False else
                 lathe([(0.0, 0), (0.04, 0.04), (0.035, 0.1), (0.0, 0.2)], 6, B).xf(rot=(0, 0, 0)).xf(rot=(0, 0, 0)).xf(pos=(0, 0, 0)).xf(rot=(math.sin(ar) * 60, 0, -math.cos(ar) * 60)).xf(pos=(0.07 * math.cos(ar), cy - 0.02, 0.07 * math.sin(ar))))
    # queue
    tail = bezier((0, cy - 0.05, -0.05), (0, cy - 0.2, -0.2), (0, cy - 0.3, -0.1), (0, cy - 0.5, -0.2), 9)
    p.append(tube(tail, np.linspace(0.07, 0.005, 9), seg=6, color=B))
    for k in range(5):
        a = math.radians(72 * k)
        p.append(gem(0.012, 0.03, 4, B, pos=(0.2 * math.cos(a), cy + 0.08 * math.sin(a * 2), 0.2 * math.sin(a))))
    for s in (1, -1):   # yeux
        p.append(sphere(0.018, 5, 3, G, pos=(s * 0.04, cy + 0.015, 0.088), s=(0.7, 1.1, 0.5)))
    return p


@prop("summon_illusion_mannequin", accent=(0.6, 0.7, 1.0), notes="mannequin d'illusion 1,5 m, pose neutre, joints en accent B")
def mannequin():
    p = []
    sk = K
    p.append(sphere(0.095, 10, 7, sk, pos=(0, 1.38, 0), s=(0.9, 1.1, 1.0)))
    p.append(limb((0, 1.28, 0), (0, 1.2, 0), 0.05, 0.05, sk))
    p.append(lathe([(0.0, 0.0), (0.13, 0.03), (0.17, 0.2), (0.15, 0.34), (0.0, 0.36)], 10, sk).xf(pos=(0, 0.82, 0), s=(1.0, 1.0, 0.65)))
    p.append(lathe([(0.0, 0.0), (0.15, 0.0), (0.14, 0.09), (0.0, 0.1)], 10, G).xf(pos=(0, 0.78, 0), s=(1.0, 1.0, 0.7)))
    for s in (1, -1):
        p.append(sphere(0.055, 7, 5, B, pos=(s * 0.21, 1.12, 0)))
        p += limb((s * 0.21, 1.12, 0), (s * 0.3, 0.88, 0.0), 0.045, 0.04, sk)
        p.append(sphere(0.04, 6, 4, B, pos=(s * 0.3, 0.88, 0)))
        p += limb((s * 0.3, 0.88, 0), (s * 0.34, 0.66, 0.03), 0.04, 0.034, sk)
        p.append(sphere(0.04, 6, 4, sk, pos=(s * 0.34, 0.62, 0.03)))
        p.append(sphere(0.06, 7, 5, B, pos=(s * 0.1, 0.76, 0)))
        p += limb((s * 0.1, 0.76, 0), (s * 0.115, 0.4, 0.0), 0.062, 0.05, sk)
        p.append(sphere(0.05, 6, 4, B, pos=(s * 0.115, 0.4, 0)))
        p += limb((s * 0.115, 0.4, 0), (s * 0.115, 0.06, 0.0), 0.05, 0.04, sk)
        p.append(box((0.07, 0.05, 0.16), (s * 0.115, 0.03, 0.04), color=sk, bevel=0.012))
    p.append(lathe([(0.0, 0.0), (0.2, 0.0), (0.2, 0.02), (0.0, 0.03)], 14, G, bevel=0.003).xf(pos=(0, 0.0, 0.0)))
    p.append(sphere(0.03, 6, 4, B, pos=(0, 1.0, 0.1), s=(1.2, 0.7, 0.5)))
    return p
