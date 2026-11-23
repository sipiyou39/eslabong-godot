from pcommon import *
from registry import prop


def stone_block(w, h, d, pos, rot=(0, 0, 0), color=G, bevel=0.015):
    return box((w, h, d), pos, rot, color=color, bevel=bevel)


@prop("summon_turret_arcane", accent=(0.45, 0.7, 1.0), notes="tourelle arcanique 1,25 m : piédestal runique, cristal flottant, anneaux")
def turret_arcane():
    p = []
    p.append(lathe([(0.34, 0.0), (0.34, 0.05), (0.27, 0.1), (0.22, 0.14), (0.2, 0.2)], 8, G, bevel=0.004, phase=22))
    p.append(lathe([(0.19, 0.2), (0.17, 0.27), (0.15, 0.55), (0.18, 0.6), (0.27, 0.64), (0.27, 0.69), (0.14, 0.7)], 8, G, bevel=0.004, phase=22))
    for yy, w in ((0.32, 0.015), (0.44, 0.015)):
        p.append(band(yy, 0.157, w * 1.6, B, seg=8, flare=1.0).xf(rot=(0, 22, 0)))
    for k in range(4):
        a = math.radians(90 * k + 45)
        p.append(box((0.03, 0.12, 0.012), (0.158 * math.cos(a), 0.38, 0.158 * math.sin(a)), rot=(0, -math.degrees(a) + 90, 0), color=B, bevel=0.002))
    p += prongs(4, 0.7, 0.98, 0.17, 0.09, 0.028, G, 0.05, 45, seg=5)
    cy = 1.0
    p.append(lathe([(0.0, -0.17), (0.09, -0.06), (0.1, 0.08), (0.0, 0.26)], 6, B, phase=30).xf(pos=(0, cy, 0)))
    p.append(torus(0.2, 0.011, 24, 5, plane="XZ", color=G).xf(rot=(24, 0, 0)).xf(pos=(0, cy, 0)))
    p.append(torus(0.25, 0.009, 24, 5, plane="XZ", color=G).xf(rot=(-30, 0, 40)).xf(pos=(0, cy, 0)))
    for k in range(5):
        a = math.radians(72 * k + 10)
        p.append(gem(0.017, 0.055, 4, B, pos=(0.27 * math.cos(a), cy + 0.12 * math.sin(a * 1.7), 0.27 * math.sin(a)), rot=(10 * k, 0, 12)))
    return p


@prop("summon_turret_rail", accent=(1.0, 0.7, 0.3), notes="tourelle à rail 1,0 m, canon vers +Z")
def turret_rail():
    p = []
    for k in range(3):
        a = math.radians(120 * k + 90)
        top = np.array([0.0, 0.5, 0.0])
        foot = np.array([0.38 * math.cos(a), 0.0, 0.38 * math.sin(a)])
        p.append(cyl(foot, top, 0.028, 0.04, seg=6, color=G))
        p.append(box((0.1, 0.03, 0.1), foot + np.array([0, 0.015, 0]), rot=(0, -math.degrees(a), 0), color=G, bevel=0.005))
    p.append(lathe([(0.12, 0.45), (0.15, 0.5), (0.15, 0.56), (0.11, 0.6)], 10, G, bevel=0.004))
    p.append(box((0.22, 0.2, 0.3), (0, 0.7, 0.0), color=G, bevel=0.012))
    p.append(box((0.2, 0.05, 0.18), (0, 0.82, -0.05), color=R, bevel=0.01))
    p.append(box((0.07, 0.07, 0.2), (0.0, 0.7, -0.22), color=B, bevel=0.01))
    for s in (1, -1):
        p.append(cyl((s * 0.065, 0.74, 0.1), (s * 0.065, 0.74, 0.86), 0.028, 0.028, seg=6, color=G, bevel=0.003))
        p.append(box((0.03, 0.03, 0.62), (s * 0.065, 0.66, 0.45), color=G, bevel=0.004))
        for zz in np.linspace(0.2, 0.78, 5):
            p.append(torus(0.045, 0.012, 10, 4, plane="XY", color=B, pos=(s * 0.065, 0.74, zz)))
    p.append(box((0.22, 0.12, 0.05), (0, 0.74, 0.88), color=G, bevel=0.006))
    p.append(cone(0.05, 0.06, 6, B, pos=(0, 0.74, 0.88), rot=(90, 0, 0)))
    for s in (1, -1):
        p.append(box((0.04, 0.2, 0.04), (s * 0.15, 0.62, -0.05), rot=(20, 0, 0), color=G, bevel=0.005))
        p.append(sphere(0.026, 6, 4, B, pos=(s * 0.15, 0.7, -0.1)))
    return p


@prop("summon_totem_storm", accent=(0.6, 0.85, 1.0), notes="totem de tempête 1,6 m : poteau sculpté, ailes, cristaux d'éclair")
def totem_storm():
    p = []
    p.append(lathe([(0.3, 0.0), (0.3, 0.07), (0.22, 0.12), (0.2, 0.16)], 8, G, bevel=0.004, phase=22))
    p.append(lathe([(0.115, 0.1), (0.13, 0.5), (0.115, 1.0), (0.1, 1.2)], 8, R, bevel=0.004))
    for yy in (0.28, 0.62, 0.95):
        p.append(band(yy, 0.135, 0.07, G, seg=8, flare=1.05))
        p.append(band(yy, 0.14, 0.02, B, seg=8, flare=1.0))
    # visage
    for s in (1, -1):
        p.append(sphere(0.03, 6, 4, B, pos=(s * 0.05, 0.78, 0.115), s=(1, 1, 0.5)))
        p.append(box((0.07, 0.02, 0.04), (s * 0.05, 0.82, 0.115), rot=(0, 0, -s * 15), color=G, bevel=0.004))
    p.append(cone(0.03, 0.1, 4, B, pos=(0, 0.72, 0.12), rot=(90, 0, 0)))
    for s in (1, -1):
        wing = plate([(0.0, 0.0), (0.12, 0.03), (0.24, 0.1), (0.3, 0.22), (0.15, 0.2), (0.0, 0.14)], 0.016, 0.014, plane="XY", color=R, edge_color=G)
        p.append(wing.xf(pos=(s * 0.1, 0.6, 0.0), s=(s, 1, 1)))
        p.append(cone(0.02, 0.12, 4, B, pos=(s * 0.4, 0.78, 0.0), rot=(0, 0, -s * 80)))
    p.append(lathe([(0.0, 0.0), (0.09, 0.04), (0.1, 0.2), (0.0, 0.42)], 6, B, phase=20).xf(pos=(0, 1.2, 0)))
    for k in range(4):
        a = math.radians(90 * k + 20)
        p.append(lathe([(0.0, 0.0), (0.05, 0.03), (0.045, 0.12), (0.0, 0.26)], 5, B).xf(rot=(math.sin(a) * 38, 0, -math.cos(a) * 38)).xf(pos=(0.07 * math.cos(a), 1.2, 0.07 * math.sin(a))))
    p.append(torus(0.17, 0.012, 20, 4, plane="XZ", color=B, pos=(0, 1.1, 0)))
    p.append(tube([(0.0, 1.62, 0.0), (0.04, 1.7, 0.0), (-0.03, 1.76, 0.0), (0.02, 1.84, 0.0)], np.linspace(0.015, 0.004, 4), seg=4, color=B))
    return p


@prop("summon_totem_stone", accent=(0.9, 0.5, 0.2), notes="totem de pierre 1,35 m : blocs empilés, visage et runes lumineux")
def totem_stone():
    p = []
    p.append(stone_block(0.62, 0.14, 0.62, (0, 0.07, 0), color=G, bevel=0.025))
    p.append(stone_block(0.5, 0.42, 0.5, (0, 0.35, 0), rot=(0, 8, 0), color=G, bevel=0.03))
    p.append(stone_block(0.42, 0.4, 0.42, (0, 0.76, 0), rot=(0, -5, 0), color=G, bevel=0.03))
    p.append(stone_block(0.5, 0.18, 0.5, (0, 1.05, 0), rot=(0, 12, 0), color=G, bevel=0.025))
    p.append(lathe([(0.0, 0.0), (0.15, 0.0), (0.12, 0.14), (0.0, 0.22)], 4, G, phase=45).xf(pos=(0, 1.14, 0)))
    ang = math.radians(-5)
    # visage (étage moyen)
    zf = 0.21 + 0.012
    for s in (1, -1):
        p.append(sphere(0.035, 6, 4, B, pos=(s * 0.1, 0.84, 0.21), s=(1, 0.8, 0.5)))
        p.append(box((0.12, 0.03, 0.04), (s * 0.1, 0.9, 0.215), rot=(0, 0, -s * 18), color=G, bevel=0.005))
    p.append(box((0.05, 0.09, 0.06), (0, 0.78, 0.22), color=G, bevel=0.008))
    p.append(box((0.16, 0.025, 0.02), (0, 0.67, 0.215), color=B, bevel=0.003))
    # runes
    for k, yy in enumerate((0.28, 0.4)):
        for s in (1, -1):
            p.append(box((0.016, 0.1, 0.012), (s * 0.12, yy, 0.255), rot=(0, 0, s * 20 * (1 if k else -1)), color=B, bevel=0.002))
        p.append(box((0.1, 0.016, 0.012), (0, yy + 0.02, 0.255), color=B, bevel=0.002))
    p.append(gem(0.04, 0.09, 6, B, pos=(0, 1.02, 0.25), rot=(90, 0, 0)))
    for s in (1, -1):
        p.append(cone(0.05, 0.18, 4, G, pos=(s * 0.19, 1.12, 0), rot=(0, 0, -s * 35)))
        p.append(sphere(0.07, 6, 4, R, pos=(s * 0.28, 0.1, 0.25), s=(1, 0.5, 1)))
    return p


@prop("prop_trap_bear", notes="piège à loup ouvert 0,6 m, mâchoires dressées", ao=0.12)
def trap_bear():
    p = []
    p.append(box((0.62, 0.035, 0.16), (0, 0.0175, 0), color=G, bevel=0.006))
    p.append(lathe([(0.0, 0.035), (0.09, 0.035), (0.085, 0.06), (0.0, 0.065)], 10, R, bevel=0.003))
    p.append(sphere(0.02, 6, 4, B, pos=(0, 0.07, 0)))
    X = np.array([1.0, 0, 0])
    th = math.radians(68)
    for s in (1, -1):
        d = np.array([0, math.sin(th), s * math.cos(th)])
        Rr = 0.26
        pts = np.array([np.array([0, 0.045, s * 0.07]) + Rr * (math.cos(f) * X + math.sin(f) * d) for f in np.radians(np.linspace(0, 180, 14))])
        p.append(tube(pts, 0.022, seg=6, color=G))
        for f in np.radians(np.linspace(18, 162, 8)):
            base = np.array([0, 0.045, s * 0.07]) + Rr * (math.cos(f) * X + math.sin(f) * d)
            inward = -(math.cos(f) * X + math.sin(f) * d)
            p.append(cyl(base, base + inward * 0.075, 0.0125, 0.0, seg=4, color=B, phase=45))
        p.append(sphere(0.03, 6, 4, G, pos=(0.0 + 0.26, 0.05, s * 0.07)))
        p.append(sphere(0.03, 6, 4, G, pos=(0.0 - 0.26, 0.05, s * 0.07)))
    for s in (1, -1):
        p.append(box((0.03, 0.05, 0.3), (s * 0.24, 0.06, 0.0), rot=(0, 0, 0), color=R, bevel=0.005))
    ch = [(0.31, 0.04, 0.0), (0.4, 0.03, 0.06), (0.5, 0.02, 0.14), (0.58, 0.02, 0.2)]
    from w_misc import chain
    p += chain(ch, 0.022, 0.013, 0.0055)
    p.append(cone(0.03, 0.22, 4, G, pos=(0.62, 0.0, 0.22), rot=(0, 0, 0)).xf(pos=(0, 0, 0)))
    return p


@prop("prop_mine", accent=(1.0, 0.25, 0.15), notes="mine 0,4 m, voyant rouge", ao=0.1)
def mine():
    p = []
    p.append(lathe([(0.0, 0.0), (0.2, 0.0), (0.21, 0.03), (0.2, 0.065), (0.15, 0.085), (0.0, 0.09)], 12, G, bevel=0.003))
    p.append(lathe([(0.205, 0.035), (0.215, 0.04), (0.21, 0.052), (0.2, 0.05)], 12, B, bevel=0.0015))
    p.append(lathe([(0.0, 0.085), (0.1, 0.087), (0.1, 0.105), (0.0, 0.112)], 10, R, bevel=0.003))
    p.append(sphere(0.03, 6, 4, B, pos=(0, 0.125, 0)))
    for k in range(6):
        a = math.radians(60 * k)
        p.append(cone(0.022, 0.06, 4, G, pos=(0.17 * math.cos(a), 0.03, 0.17 * math.sin(a)), rot=(math.sin(a) * -60, 0, math.cos(a) * 60 + 0)))
        p.append(sphere(0.012, 5, 3, B, pos=(0.13 * math.cos(a + 0.5), 0.1, 0.13 * math.sin(a + 0.5))))
    return p


@prop("prop_tombstone", notes="pierre tombale 1,0 m, tertre, croix incrustée (B), mousse (R)")
def tombstone():
    p = []
    arch = [(-0.3, 0.0), (0.3, 0.0), (0.3, 0.6), (0.27, 0.72), (0.2, 0.82), (0.1, 0.88), (0.0, 0.9), (-0.1, 0.88), (-0.2, 0.82), (-0.27, 0.72), (-0.3, 0.6)]
    p.append(plate(arch, 0.06, 0.05, plane="XY", color=G, edge_color=G).xf(pos=(0, 0.1, 0), rot=(-4, 0, 0)))
    p.append(box((0.07, 0.38, 0.03), (0, 0.62, 0.075), rot=(-4, 0, 0), color=B, bevel=0.004))
    p.append(box((0.24, 0.07, 0.03), (0, 0.7, 0.075), rot=(-4, 0, 0), color=B, bevel=0.004))
    p.append(box((0.2, 0.014, 0.025), (0, 0.4, 0.075), color=B, bevel=0.002))
    p.append(box((0.14, 0.014, 0.025), (0, 0.36, 0.075), color=B, bevel=0.002))
    p.append(lathe([(0.4, 0.0), (0.4, 0.04), (0.3, 0.12), (0.16, 0.17), (0.0, 0.18)], 10, R, bevel=None).xf(pos=(0, 0, 0.38), s=(0.95, 1.0, 1.1)))
    p.append(box((0.5, 0.06, 0.18), (0, 0.03, 0.0), color=G, bevel=0.012))
    for s in (1, -1):
        p.append(sphere(0.06, 6, 4, R, pos=(s * 0.26, 0.74, 0.0), s=(1, 0.6, 1)))
    for k in range(5):
        a = k * 30 - 60
        p.append(cone(0.01, 0.07, 3, R, pos=(0.0 + (k - 2) * 0.09, 0.2, 0.44), rot=(-10, 0, a * 0.4)))
    return p
