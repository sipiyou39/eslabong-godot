"""Équipement de torse sci-fi (origine = pivot torse (0,0.78,0)) et jupes (origine = pivot bassin (0,0.74,0)). R principal, G secondaire, B accent/lueur."""
from sf_common import *
from gear_torso import tsh, T_, S_

def belt(p, y0=0.74, y1=0.80, col=G, buckle=True, gx=0.045, gz=0.04):
    rx, rz, cz = torso_r(0.77)
    p.add(rows_loft([(y0, rx + gx, rz + gz, cz), (y1, rx + gx, rz + gz, cz)], n=22, e=2.3, cap0='ngon', cap1='ngon'), col, angle=60)
    if buckle:
        p.add(box_at((0, 0.77, cz + rz + gz + 0.005), (0.035, 0.032, 0.014), r=0.004), B)


def collar(p, y=1.15, r=0.135, col=R, h=0.07, trim=G):
    p.add(rows_loft([(y - 0.03, r + 0.04, r * 0.8 + 0.04, -0.005), (y + h, r, r * 0.8, -0.005)], n=20, e=2.2, cap0='ngon', cap1='ngon'), col, angle=60)
    p.add(torus(r + 0.015, 0.014, 18, 4).sc(1.0, 1.0, 0.8).t(0, y + h, -0.005), trim)


def sash(p, col=G, y=0.80, knot=True):
    rx, rz, cz = torso_r(y)
    p.add(rows_loft([(y - 0.04, rx + 0.06, rz + 0.055, cz), (y + 0.04, rx + 0.055, rz + 0.05, cz)], n=22, e=2.3, cap0='ngon', cap1='ngon'), col, angle=60)


ZF = 0.19     # z approximatif de la face avant du torse humain (avec marge)


def front_z(y, gz=0.036):
    rx, rz, cz = torso_r(y)
    return cz + rz + gz + 0.5 * 0.03 * math.exp(-0.5 * ((y - 1.04) / 0.09) ** 2)


def shell(y0, y1, gx, gz, n=22, k=8, e=2.3, **kw):
    return torso_shell(y0, y1, gx=gx, gz=gz, n=min(n, 18), k=min(k, 6), e=e, **kw)


def ring(y0, y1, gx, gz, n=22, e=2.3, y_ref=None, cz=None):
    yr = (y0 + y1) / 2 if y_ref is None else y_ref
    rx, rz, c = torso_r(yr)
    return rows_loft([(y0, rx + gx, rz + gz, c if cz is None else cz), (y1, rx + gx, rz + gz, c if cz is None else cz)], n=n, e=e, cap0='ngon', cap1='ngon')


def vial(c, h=0.05, r=0.009):
    return cyl_between((c[0], c[1] - h / 2, c[2]), (c[0], c[1] + h / 2, c[2]), r, n=6)


# --------------------------------------------------------------------------------------------------------------------
def armor_spacesuit():
    p = T_("armor_spacesuit")
    p.add(shell(0.74, 1.165, 0.075, 0.066, n=24, k=8), R, angle=60)
    # épaules matelassées : bagues articulées (axe X) aux emmanchures
    for sx in (-1, 1):
        p.add(torus(0.108, 0.024, 12, 4).rz(90).t(sx * 0.3, 1.06, 0.0), G)
    # col étanche (bague d'attache du casque)
    p.add(rows_loft([(1.13, 0.2, 0.17, -0.005), (1.2, 0.17, 0.145, -0.005)], n=22, e=2.1, cap0='ngon', cap1='ngon'), G, angle=60)
    p.add(torus(0.185, 0.022, 16, 4).sc(1.0, 1.0, 0.86).t(0, 1.2, -0.005), R)
    # boîtier de commandes sur la poitrine
    zf = front_z(1.0, 0.066)
    p.add(box_at((0, 1.0, zf), (0.2, 0.14, 0.06), r=0.014, s=1), G, angle=55)
    p.add(zdisc(-0.045, 1.02, zf + 0.028, 0.032, depth=0.012, n=12, rx=0.04, ry=0.028, e=3.0), B, ao=1.0)
    p.add([cube((0.02 + 0.03 * i, 0.975, zf + 0.032), (0.02, 0.02, 0.012)) for i in range(3)], B, ao=1.0, angle=40)
    p.add(sphere(0.014, 0.014, 0.014, n=6, m=4).t(0.075, 1.04, zf + 0.032), R)
    # durites vers les poches de taille
    for sx in (-1, 1):
        path = np.array([[sx * 0.1, 0.96, zf - 0.0], [sx * 0.2, 0.93, zf - 0.015], [sx * 0.28, 0.86, zf - 0.07], [sx * 0.285, 0.8, zf - 0.14]])
        p.add(ctube(path, 0.015, m=2, n=6), G)
        p.add(cyl_between((sx * 0.1, 0.96, zf - 0.01), (sx * 0.1, 0.96, zf + 0.015), 0.024, n=8), G, angle=60)
    # ceinture de service + poches
    belt(p, 0.74, 0.8, G)
    p.add([box_at((sx * 0.23, 0.79, 0.1), (0.07, 0.07, 0.07), r=0.012, s=1) for sx in (-1, 1)], R, angle=55)
    # écusson de mission + sangles
    p.add(box_at((0.15, 1.08, zf - 0.005), (0.07, 0.035, 0.012), r=0.004, s=1), B)
    p.add(box_at((0.05, 0.88, 0.17), (0.03, 0.03, 0.02), r=0.006, s=1), G)
    return p


def armor_exo():
    p = T_("armor_exo")
    # sous-combinaison moulante sombre
    p.add(shell(0.76, 1.165, 0.022, 0.02, n=22, k=8), G, angle=60)
    zf = front_z(1.0, 0.02)
    # plastron partiel + brassière de côtes
    p.add(box_at((0, 1.04, zf + 0.012), (0.26, 0.15, 0.036), r=0.015, s=1), R, angle=55)
    p.add([box_at((0, 0.9 + 0.045 * i, zf - 0.005), (0.2 - 0.018 * i, 0.022, 0.026), r=0.008, s=1) for i in range(3)], R, angle=55)
    # colonne vertébrale articulée dans le dos
    zb = -0.15
    p.add(ctube(np.array([[0, 1.15, zb - 0.0], [0, 1.0, zb - 0.025], [0, 0.88, zb - 0.02], [0, 0.78, zb + 0.0]]), 0.018, m=2, n=6), G)
    p.add([sphere(0.03, 0.016, 0.03, n=6, m=3).t(0, 1.12 - 0.08 * i, zb - 0.012 - 0.02 * math.sin(i * 0.9)) for i in range(4)], R, angle=60)
    p.add(box_at((0, 1.0, -0.2), (0.16, 0.16, 0.05), r=0.015, s=1), R, angle=55)
    p.add(zdisc(0, 1.0, -0.228, 0.03, depth=0.01, n=10), B, ao=1.0) if False else None
    # arceaux d'épaule et pistons latéraux
    for sx in (-1, 1):
        arc = np.array([[sx * 0.125, 1.16, 0.12], [sx * 0.22, 1.2, 0.06], [sx * 0.3, 1.19, -0.02], [sx * 0.31, 1.15, -0.1]])
        p.add(ctube(arc, 0.014, m=2, n=6), R)
        p.add(cyl_between((sx * 0.265, 0.82, 0.0), (sx * 0.275, 1.0, 0.0), 0.014, n=6), G, angle=60)
        p.add(cyl_between((sx * 0.272, 0.9, 0.0), (sx * 0.28, 1.04, 0.0), 0.022, n=7), R, angle=60)
        p.add(sphere(0.026, 0.026, 0.026, n=8, m=5).t(sx * 0.27, 0.8, 0.0), G, angle=60)
        # lignes lumineuses sur le plastron
        p.add(ctube(np.array([[sx * 0.02, 1.1, zf + 0.03], [sx * 0.08, 1.1, zf + 0.03], [sx * 0.13, 1.04, zf + 0.03], [sx * 0.13, 0.97, zf + 0.025]]), 0.005, m=2, n=4), B, ao=1.0)
    # ceinture à batterie
    p.add(ring(0.755, 0.805, 0.045, 0.038, n=22), R, angle=55)
    p.add(box_at((0, 0.78, zf - 0.02), (0.1, 0.06, 0.04), r=0.012, s=1), G, angle=55)
    p.add(zdisc(0, 0.78, zf + 0.0, 0.02, depth=0.012, n=10), B, ao=1.0)
    collar(p, 1.14, 0.14, G, 0.05, R)
    return p


def armor_jacket_tech():
    p = T_("armor_jacket_tech")
    p.add(shell(0.74, 1.165, 0.05, 0.045, n=24, k=8), R, angle=60)
    # grand col montant
    p.add(rows_loft([(1.12, 0.18, 0.15, -0.01), (1.2, 0.165, 0.14, -0.02), (1.27, 0.19, 0.16, -0.025)], n=22, e=2.1, cap0='ngon', cap1='ngon', k=5), R, angle=60)
    p.add(rows_loft([(1.265, 0.19, 0.16, -0.025), (1.285, 0.195, 0.165, -0.025)], n=22, e=2.1, cap0='ngon', cap1='ngon'), G, angle=60)
    zf = front_z(1.0, 0.045)
    # fermeture + poches plaquées
    p.add(box_at((0, 0.97, zf + 0.002), (0.022, 0.4, 0.014), r=0.005, s=1), G, angle=55)
    for sx in (-1, 1):
        p.add(box_at((sx * 0.14, 0.9, zf - 0.012), (0.1, 0.075, 0.03), r=0.01, s=1), G, angle=55)
        p.add(box_at((sx * 0.14, 0.935, zf + 0.004), (0.1, 0.012, 0.012), r=0.004, s=1), R)
        # passepoils lumineux sur les pectoraux, empiècements d'épaule
        p.add(ctube(np.array([[sx * 0.04, 1.12, zf + 0.012], [sx * 0.16, 1.1, zf + 0.0], [sx * 0.22, 1.04, zf - 0.04]]), 0.006, m=2, n=4), B, ao=1.0)
        p.add(box_at((sx * 0.22, 1.1, 0.0), (0.06, 0.03, 0.2), r=0.01, s=1, roll=-sx * 18), G, angle=55)
    # ceinture de tissu à boucle lumineuse
    belt(p, 0.74, 0.8, G, buckle=False)
    p.add(box_at((0, 0.77, front_z(0.77, 0.04) + 0.006), (0.06, 0.04, 0.012), r=0.006, s=1), B, ao=1.0)
    # dos : empiècement et prise d'air
    p.add(box_at((0, 1.02, -0.205), (0.2, 0.1, 0.02), r=0.008, s=1), G, angle=55)
    p.add([cube((0, 1.02 + dy, -0.218), (0.14, 0.008, 0.008)) for dy in (-0.025, 0.0, 0.025)], R, angle=40)
    return p


def armor_mech():
    p = T_("armor_mech")
    p.add(shell(0.74, 1.17, 0.088, 0.078, n=24, k=8, e=2.6), R, angle=55)
    zf = front_z(1.0, 0.078)
    # plastron massif en deux blocs + évents latéraux
    for sx in (-1, 1):
        p.add(box_at((sx * 0.115, 1.03, zf + 0.0), (0.17, 0.17, 0.09), r=0.025, s=1, roll=sx * 4), R, angle=55)
        p.add([cube((sx * 0.2, 0.96 + 0.032 * i, zf - 0.04), (0.06, 0.012, 0.03)) for i in range(3)], G, angle=40)
    # noyau réacteur
    p.add(box_at((0, 1.03, zf - 0.005), (0.08, 0.17, 0.07), r=0.012, s=1), G, angle=55)
    p.add(zdisc(0, 1.03, zf + 0.03, 0.046, depth=0.02, n=14), G, angle=60)
    p.add(zdisc(0, 1.03, zf + 0.048, 0.03, depth=0.01, n=14), B, ao=1.0)
    # carapace abdominale en lames
    for i, y in enumerate((0.86,)):
        rx, rz, cz = torso_r(y)
        p.add(rows_loft([(y - 0.03, rx + 0.1, rz + 0.092, cz), (y + 0.03, rx + 0.092, rz + 0.085, cz)], n=22, e=2.5, cap0='ngon', cap1='ngon'), G if i == 0 else R, angle=50)
    # bagues d'épaule + gorgerin
    for sx in (-1, 1):
        p.add(torus(0.1, 0.03, 12, 4).rz(90).t(sx * 0.285, 1.08, 0.0), G)
        p.add(box_at((sx * 0.22, 1.18, 0.03), (0.12, 0.06, 0.28), r=0.02, s=1, roll=-sx * 18), R, angle=55)
    p.add(rows_loft([(1.12, 0.2, 0.18, -0.005), (1.2, 0.16, 0.14, -0.005)], n=22, e=2.2, cap0='ngon', cap1='ngon'), G, angle=60)
    p.add(torus(0.18, 0.026, 18, 4).sc(1.0, 1.0, 0.85).t(0, 1.2, -0.005), R)
    # ceinture blindée
    p.add(ring(0.745, 0.8, 0.098, 0.088, n=22, e=2.5), G, angle=50)
    p.add(box_at((0, 0.77, zf - 0.04), (0.12, 0.07, 0.04), r=0.012, s=1), R, angle=55)
    # dos : plaque et tuyères de refroidissement
    p.add(box_at((0, 1.0, -0.265), (0.34, 0.24, 0.05), r=0.02, s=1), R, angle=55)
    p.add([cyl_between((sx * 0.1, 0.95, -0.29), (sx * 0.1, 1.08, -0.31), 0.03, 0.04, n=8) for sx in (-1, 1)], G, angle=60)
    p.add([zdisc(sx * 0.1, 1.08, -0.318, 0.026, depth=0.006, n=8) for sx in (-1, 1)], B, ao=1.0)
    return p


def armor_medic():
    p = T_("armor_medic")
    p.add(shell(0.74, 1.165, 0.052, 0.044, n=24, k=8), R, angle=60)
    zf = front_z(1.0, 0.044)
    # croix médicale (accent) devant à gauche + dans le dos
    for (cx, cy, cz, d) in ((0.1, 1.06, zf + 0.004, 1.0), (0.0, 1.02, -0.215, -1.0)):
        p.add([box_at((cx, cy, cz), (0.1, 0.03, 0.014), r=0.004, s=1), box_at((cx, cy, cz), (0.03, 0.1, 0.014), r=0.004, s=1)], B, ao=1.0)
    # col, ceinture, sangle porte-fioles
    collar(p, 1.14, 0.14, G, 0.05, R)
    belt(p, 0.74, 0.8, G, buckle=False)
    p.add(box_at((0, 0.77, front_z(0.77, 0.045) + 0.004), (0.05, 0.04, 0.014), r=0.005, s=1), B, ao=1.0)
    strap_pts = [torso_pt(1.14, 150, 0.05), torso_pt(1.04, 100, 0.054), torso_pt(0.9, 48, 0.054), torso_pt(0.8, 28, 0.05)]
    p.add(strap(strap_pts, w=0.026, th=0.01), G)
    p.add([vial(tuple(np.array(strap_pts[1]) + (np.array(strap_pts[2]) - np.array(strap_pts[1])) * t + np.array([0, 0.0, 0.022])), 0.05, 0.011) for t in (0.2, 0.42, 0.64)], B, ao=1.0)
    # poches de taille + injecteur holographique
    for sx in (-1, 1):
        p.add(box_at((sx * 0.215, 0.8, 0.09), (0.075, 0.08, 0.08), r=0.012, s=1), G, angle=55)
        p.add(box_at((sx * 0.22, 1.09, 0.0), (0.05, 0.026, 0.2), r=0.008, s=1), G, angle=55)    # bande d'épaule
    p.add(box_at((-0.04, 1.14, front_z(1.14, 0.04) - 0.0), (0.05, 0.03, 0.02), r=0.006, s=1), B, ao=1.0)
    p.add(cube((0, 0.95, zf + 0.0), (0.012, 0.28, 0.01)), G, angle=40)
    return p


def armor_psi_robe():
    p = T_("armor_psi_robe")
    p.add(shell(0.74, 1.17, 0.052, 0.048, n=24, k=8), R, angle=60)
    # haut col évasé en éventail
    p.add(rows_loft([(1.12, 0.17, 0.14, -0.01), (1.22, 0.2, 0.15, -0.025), (1.31, 0.27, 0.17, -0.05)], n=18, e=2.4, cap0='ngon', cap1='ngon', k=4), R, angle=60)
    p.add(rows_loft([(1.3, 0.268, 0.168, -0.05), (1.325, 0.272, 0.172, -0.052)], n=22, e=2.4, cap0='ngon', cap1='ngon'), G, angle=60)
    p.add([sphere(0.012, 0.012, 0.012, n=6, m=4).t(sx * 0.2, 1.28, 0.1) for sx in (-1, 1)], B, ao=1.0)
    zf = front_z(1.0, 0.048)
    # écharpe croisée + panneau de tissu avec glyphes
    p.add(strap([torso_pt(1.15, 140, 0.056), torso_pt(1.03, 90, 0.06), torso_pt(0.88, 40, 0.06)], w=0.036, th=0.01), G)
    p.add([cube((0.0 + 0.045 * (i - 1), 0.93 + 0.02 * (i % 2), zf + 0.01), (0.014, 0.03, 0.01), roll=15 * (i - 1)) for i in range(3)], B, ao=1.0, angle=40)
    # ceinture à orbe psi
    sash(p, G, 0.8, knot=False)
    p.add(sphere(0.045, 0.045, 0.04, n=12, m=7).t(0, 0.8, front_z(0.8, 0.055) + 0.025), B, ao=1.0)
    p.add(torus(0.055, 0.01, 12, 4).rx(90).t(0, 0.8, front_z(0.8, 0.055) + 0.012), G)
    # épaulière-cape courte en tissu
    for sx in (-1, 1):
        p.add(lathe([(0.19, -0.14), (0.185, -0.1), (0.16, -0.04), (0.12, 0.03), (0.07, 0.07), (0.0, 0.085)], n=14, rz=1.0).rz(-sx * 24).t(sx * 0.27, 1.15, 0.0), R, angle=60)
        p.add(lathe([(0.2, -0.15), (0.2, -0.125), (0.191, -0.125), (0.191, -0.15)], n=14).rz(-sx * 24).t(sx * 0.27 + sx * 0.005, 1.15, 0.0), G, angle=60)
    return p


# --------------------------------------------------------------------------------------------------------------------
def armor_spacesuit_skirt():
    p = S_("armor_spacesuit_skirt")
    p.add(skirt(0.84, 0.64, (0.225, 0.17), (0.255, 0.2), n=22, k=5, folds=0, e=2.4), R, angle=60)
    p.add(skirt(0.64, 0.6, (0.255, 0.2), (0.25, 0.195), n=22, k=2, e=2.4), G, angle=60)
    p.add(torus(0.215, 0.02, 18, 4).sc(1.0, 1.0, 0.76).t(0, 0.835, 0.0), G)
    for sx in (-1, 1):
        p.add(box_at((sx * 0.245, 0.72, 0.03), (0.07, 0.16, 0.14), r=0.014, s=1), R, angle=55)
        p.add(box_at((sx * 0.282, 0.72, 0.03), (0.012, 0.03, 0.05), r=0.004, s=1), B)
    p.add(box_at((0, 0.72, 0.19), (0.12, 0.08, 0.024), r=0.008, s=1), G, angle=55)
    return p


def armor_exo_skirt():
    p = S_("armor_exo_skirt")
    p.add(torus(0.205, 0.016, 18, 4).sc(1.0, 1.0, 0.76).t(0, 0.80, 0.0), G)
    for sx in (-1, 1):
        p.add(cyl_between((sx * 0.22, 0.78, 0.02), (sx * 0.19, 0.5, 0.02), 0.016, 0.012, n=6), G, angle=60)
        p.add(box_at((sx * 0.2, 0.62, 0.025), (0.036, 0.18, 0.05), r=0.01, s=1), R, angle=55)
        p.add(cyl_between((sx * 0.2, 0.7, 0.06), (sx * 0.165, 0.52, 0.065), 0.01, n=6), G, angle=60)
        p.add(sphere(0.022, 0.022, 0.022, n=8, m=5).t(sx * 0.22, 0.76, 0.02), R, angle=60)
        p.add(cube((sx * 0.2, 0.55, 0.055), (0.012, 0.05, 0.012)), B, ao=1.0)
    p.add(box_at((0, 0.69, 0.185), (0.14, 0.15, 0.03), r=0.012, s=1, pitch=-6), R, angle=55)
    p.add(box_at((0, 0.69, -0.17), (0.12, 0.12, 0.03), r=0.012, s=1), R, angle=55)
    p.add(zdisc(0, 0.69, 0.2, 0.02, depth=0.008, n=10), B, ao=1.0)
    return p


def armor_jacket_tech_skirt():
    p = S_("armor_jacket_tech_skirt")
    hem = jag_hem(0.03, 2, 4)
    p.add(skirt(0.84, 0.4, (0.225, 0.165), (0.285, 0.23), n=26, k=7, folds=5, fold_amp=0.01, e=2.3, hem_fn=lambda a: -0.05 * max(0.0, math.sin(a)) * 0.0 - 0.08 * max(0.0, -math.sin(a) + 0.2)), R, angle=60)
    p.add(skirt(0.405, 0.375, (0.285, 0.23), (0.288, 0.232), n=26, k=2, e=2.3, hem_fn=lambda a: -0.08 * max(0.0, -math.sin(a) + 0.2)), G, angle=60)
    p.add(box_at((0, 0.55, -0.235), (0.016, 0.3, 0.012), r=0.004, s=1), G)
    p.add([box_at((sx * 0.27, 0.62, 0.0), (0.012, 0.2, 0.012), r=0.004, s=1) for sx in (-1, 1)], B, ao=1.0)
    return p


def armor_mech_skirt():
    p = S_("armor_mech_skirt")
    p.add(torus(0.215, 0.022, 18, 4).sc(1.0, 1.0, 0.78).t(0, 0.8, 0.0), G)
    # tassettes : plaques avant/arrière/latérales articulées
    p.add(box_at((0, 0.62, 0.2), (0.25, 0.26, 0.04), r=0.014, s=1, pitch=-8), R, angle=55)
    p.add(box_at((0, 0.6, 0.215), (0.12, 0.1, 0.03), r=0.012, s=1, pitch=-8), G, angle=55)
    p.add(box_at((0, 0.64, -0.2), (0.28, 0.22, 0.04), r=0.014, s=1, pitch=8), R, angle=55)
    for sx in (-1, 1):
        p.add(box_at((sx * 0.25, 0.62, 0.0), (0.04, 0.26, 0.2), r=0.014, s=1, roll=sx * 8), R, angle=55)
        p.add(box_at((sx * 0.215, 0.6, 0.15), (0.04, 0.2, 0.1), r=0.012, s=1, yaw=-sx * 40, roll=sx * 6), G, angle=55)
        p.add(sphere(0.026, 0.026, 0.026, n=8, m=5).t(sx * 0.255, 0.77, 0.0), G, angle=60)
    p.add([zdisc(sx * 0.05, 0.64, 0.225, 0.012, depth=0.006, n=8) for sx in (-1, 1)], B, ao=1.0)
    return p


def armor_medic_skirt():
    p = S_("armor_medic_skirt")
    p.add(skirt(0.84, 0.52, (0.225, 0.165), (0.26, 0.2), n=24, k=6, folds=0, e=2.3), R, angle=60)
    p.add(skirt(0.525, 0.5, (0.26, 0.2), (0.262, 0.202), n=24, k=2, e=2.3), G, angle=60)
    p.add(box_at((0.215, 0.66, 0.1), (0.07, 0.1, 0.07), r=0.012, s=1), G, angle=55)
    p.add(cube((0.215, 0.7, 0.14), (0.04, 0.012, 0.01)), B, ao=1.0)
    p.add(box_at((0, 0.7, 0.2), (0.012, 0.28, 0.01), r=0.004, s=1), G)
    return p


TORSO = [armor_spacesuit, armor_exo, armor_jacket_tech, armor_mech, armor_medic, armor_psi_robe]
SKIRTS = [armor_psi_robe_skirt if False else None, armor_jacket_tech_skirt, armor_mech_skirt, armor_spacesuit_skirt, armor_exo_skirt, armor_medic_skirt]


def armor_psi_robe_skirt():
    p = S_("armor_psi_robe_skirt")
    hem = lambda a: -0.03 * (0.5 + 0.5 * math.cos(a * 6))
    p.add(skirt(0.84, 0.1, (0.225, 0.165), (0.37, 0.33), n=28, k=9, folds=6, fold_amp=0.02, e=2.2, hem_fn=hem, curve=1.2), R, angle=60)
    p.add(skirt(0.14, 0.095, (0.36, 0.32), (0.372, 0.33), n=28, k=2, e=2.2, hem_fn=hem), G, angle=60)
    # glyphes lumineux au bas de la robe
    for i in range(7):
        a = math.radians(40 + 16 * i)
        r = (0.37 * math.cos(a), 0.33 * math.sin(a))
        p.add(cube((r[0] * 1.0, 0.18 + 0.02 * (i % 2), r[1] * 1.0), (0.022, 0.04, 0.012), yaw=-a + math.pi / 2), B, ao=1.0, angle=40)
    p.add(box_at((0, 0.45, 0.29), (0.02, 0.6, 0.012), r=0.004, s=1), G)
    return p


SKIRTS[0] = armor_psi_robe_skirt
