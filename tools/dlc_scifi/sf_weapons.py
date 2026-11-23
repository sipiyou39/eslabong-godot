"""Armes sci-fi : origine = prise en main, axe +Y ; canon/avant vers +Z (plat de lame vers ±X).
R = carrosserie principale, G = métal sombre, B = énergie / lueur / liquide, K (peau) = métal clair."""
from sf_common import *

O = (0.0, 0.0, 0.0)


def W_(name):
    return Part(name, O)


def zc(x, y, z0, z1, r0, r1=None, n=10, caps=True):
    return cyl_between((x, y, z0), (x, y, z1), r0, r1, n=n, caps=caps)


def hexring(ro, ri, z0, z1, rot=0.0):
    """anneau hexagonal (plan XY, épaisseur z0..z1)."""
    def ring(r, z):
        t = rot + 2 * np.pi * np.arange(6) / 6
        return np.stack([r * np.cos(t), r * np.sin(t), np.full(6, z)], 1)
    return loft([ring(ro, z0), ring(ro, z1), ring(ri, z1), ring(ri, z0), ring(ro, z0)], cap0=False, cap1=False)


def hexslab(r, z0, z1, rot=0.0):
    return zloft([(z0, r, r, 0.0, 0.0, 2.0), (z1, r, r, 0.0, 0.0, 2.0)], n=6, cap0='ngon', cap1='ngon') if rot == 0 else None


def blade_geo(y0, y1, hw, th, tip=0.07, n=8, e=2.6, taper=0.85):
    """lame le long de +Y : largeur hw selon Z, épaisseur th selon X, pointe en y1."""
    rows = [(y0, th, hw, 0.0), (y0 + (y1 - y0 - tip) * 0.5, th * 0.95, hw * 0.96, 0.0), (y1 - tip, th * 0.8, hw * taper, 0.0), (y1 - tip * 0.45, th * 0.5, hw * 0.55, 0.0), (y1, 0.0, 0.0, 0.0)]
    return rows_loft(rows, n=n, e=e, cap0='ngon', cap1='fan')


# ------------------------------------------------------------------------------------------------------------ armes à feu
def wpn_blaster():
    p = W_("wpn_blaster")
    p.add(box_at((0, -0.012, -0.02), (0.046, 0.15, 0.06), r=0.01, pitch=-12), R, angle=55)          # crosse inclinée
    p.add(box_at((0, -0.088, -0.045), (0.05, 0.02, 0.07), r=0.006, pitch=-12), G, angle=55)          # talon : pile
    p.add(box_at((0, 0.1, 0.07), (0.056, 0.08, 0.27), r=0.014), R, angle=55)                          # carcasse
    p.add(box_at((0, 0.152, 0.09), (0.036, 0.014, 0.2), r=0.005), G, angle=55)                         # rail supérieur
    p.add(zc(0, 0.105, 0.2, 0.32, 0.021, 0.018, n=10), G, angle=55)                                   # canon
    for z in (0.23, 0.265, 0.3):
        p.add(zc(0, 0.105, z - 0.008, z + 0.008, 0.028, n=10), R, angle=55)
    p.add(zc(0, 0.105, 0.318, 0.332, 0.026, 0.022, n=10), B, ao=1.0)                                   # bouche d'énergie
    p.add([box_at((sx * 0.029, 0.1, 0.08), (0.008, 0.034, 0.1), r=0.003) for sx in (-1, 1)], B, ao=1.0)   # cellule visible
    p.add(box_at((0, 0.17, 0.0), (0.014, 0.02, 0.014), r=0.003), G)                                      # cran de mire
    p.add(box_at((0, 0.165, 0.2), (0.01, 0.016, 0.01), r=0.003), B, ao=1.0)
    gp = np.array([[0.0, 0.056, 0.115], [0.0, 0.0, 0.118], [0.0, 0.005, 0.066]])
    p.add(ctube(gp, 0.006, m=2, n=5), G)                                                              # pontet
    p.add(box_at((0, 0.03, 0.06), (0.012, 0.03, 0.01), r=0.003, pitch=14), G)
    return p


def wpn_rifle_plasma():
    p = W_("wpn_rifle_plasma")
    p.add(box_at((0, 0.0, -0.03), (0.05, 0.14, 0.07), r=0.01, pitch=-14), G, angle=55)                # poignée
    p.add(box_at((0, 0.095, 0.1), (0.07, 0.12, 0.4), r=0.016), R, angle=55)                           # carcasse
    p.add(box_at((0, 0.1, -0.2), (0.05, 0.1, 0.26), r=0.012, pitch=4), R, angle=55)                    # crosse
    p.add(box_at((0, 0.1, -0.34), (0.055, 0.13, 0.03), r=0.008), G, angle=55)
    p.add(zc(0, 0.1, 0.28, 0.66, 0.036, 0.03, n=10), G, angle=55)                                      # tube de canon
    for z in (0.34, 0.41, 0.48, 0.55):
        p.add(zc(0, 0.1, z - 0.012, z + 0.012, 0.044, n=10), R, angle=55)
    p.add(zc(0, 0.1, 0.65, 0.7, 0.04, 0.054, n=10), G, angle=55)                                       # évasement
    p.add(zc(0, 0.1, 0.695, 0.705, 0.03, n=10), B, ao=1.0)
    # chambre à plasma (visible sur le dessus)
    p.add(zc(0, 0.17, 0.0, 0.24, 0.03, n=10), B, ao=1.0)
    p.add([zc(0, 0.17, z - 0.01, z + 0.01, 0.037, n=10) for z in (-0.005, 0.12, 0.245)], G, angle=55)
    p.add(box_at((0, 0.215, 0.1), (0.014, 0.022, 0.1), r=0.003), G)
    # garde-main + chargeur à cellule
    p.add(box_at((0, 0.03, 0.32), (0.04, 0.08, 0.1), r=0.01), G, angle=55)
    p.add(box_at((0, 0.01, 0.17), (0.04, 0.12, 0.06), r=0.01), R, angle=55)
    p.add(box_at((0, -0.06, 0.17), (0.034, 0.02, 0.05), r=0.004), B, ao=1.0)
    p.add(ctube(np.array([[0.0, 0.057, 0.14], [0.0, 0.0, 0.14], [0.0, 0.0, 0.08]]), 0.007, m=2, n=5), G)
    p.add(box_at((0.0, 0.16, -0.12), (0.03, 0.03, 0.04), r=0.004), G)
    return p


def wpn_railgun():
    p = W_("wpn_railgun")
    p.add(box_at((0, 0.0, -0.03), (0.05, 0.14, 0.07), r=0.01, pitch=-14), G, angle=55)
    p.add(box_at((0, 0.1, 0.12), (0.075, 0.15, 0.5), r=0.018), R, angle=55)                           # carcasse
    p.add(box_at((0, 0.09, -0.26), (0.06, 0.2, 0.28), r=0.014, pitch=-3), R, angle=55)                  # crosse épaulée
    p.add(box_at((0, 0.2, -0.28), (0.04, 0.05, 0.2), r=0.01), G, angle=55)                             # appuie-joue
    p.add(box_at((0, 0.0, -0.4), (0.07, 0.17, 0.04), r=0.01), G, angle=55)                              # plaque de crosse
    # deux rails parallèles + bobines
    for sx in (-1, 1):
        p.add(box_at((sx * 0.032, 0.115, 0.7), (0.018, 0.026, 0.88), r=0.004), G, angle=50)
    for z in (0.38, 0.5, 0.62, 0.74, 0.86, 0.98):
        p.add(box_at((0, 0.115, z), (0.1, 0.075, 0.025), r=0.006), R, angle=50)
    p.add([cube((sx * 0.052, 0.115, z), (0.006, 0.04, 0.02)) for sx in (-1, 1) for z in (0.38, 0.5, 0.62, 0.74, 0.86, 0.98)], B, ao=1.0, angle=40)
    p.add(box_at((0, 0.115, 1.17), (0.07, 0.07, 0.05), r=0.01), G, angle=55)
    p.add(zdisc(0, 0.115, 1.19, 0.022, depth=0.01, n=10), B, ao=1.0)
    # lunette
    p.add(zc(0, 0.235, -0.05, 0.3, 0.036, n=12), G, angle=55)
    p.add(zc(0, 0.235, 0.26, 0.34, 0.044, n=12), R, angle=55)
    p.add(zdisc(0, 0.235, 0.335, 0.034, depth=0.008, n=12), B, ao=1.0)
    p.add(box_at((0, 0.19, 0.08), (0.02, 0.05, 0.12), r=0.004), G)
    p.add(box_at((0, 0.19, 0.22), (0.02, 0.05, 0.06), r=0.004), G)
    # bipied replié + garde
    p.add(ctube(np.array([[0.0, 0.03, 0.46], [0.0, -0.04, 0.55], [0.0, -0.03, 0.66]]), 0.007, m=2, n=5), G)
    p.add(box_at((0, 0.03, 0.38), (0.05, 0.1, 0.12), r=0.01), G, angle=55)
    p.add(box_at((0, 0.205, 0.5), (0.02, 0.03, 0.2), r=0.005), B, ao=1.0)
    return p


# ------------------------------------------------------------------------------------------------------------ mêlée / énergie
def hilt(p, length=0.22, emit_y=None, guard_w=0.06):
    y0 = -length * 0.55
    y1 = y0 + length
    p.add(lathe([(0.021, y0), (0.025, y0 + 0.01), (0.022, y0 + length * 0.5), (0.025, y1 - 0.02), (0.02, y1)], n=10), R, angle=55)
    for i in range(3):
        y = y0 + 0.03 + i * length * 0.25
        p.add(torus(0.025, 0.006, 10, 3).t(0, y, 0), G)
    p.add(box_at((0, y1 + 0.01, 0), (guard_w, 0.024, 0.032), r=0.006), G, angle=55)
    p.add(box_at((0, y0 - 0.008, 0), (0.044, 0.026, 0.044), r=0.008), G, angle=55)
    return y1


def wpn_energy_blade():
    p = W_("wpn_energy_blade")
    y1 = hilt(p, 0.26, guard_w=0.1)
    p.add(lathe([(0.026, y1 + 0.02), (0.022, y1 + 0.05), (0.018, y1 + 0.075)], n=10), G, angle=55)
    p.add(box_at((0, y1 + 0.03, 0.0), (0.035, 0.02, 0.03), r=0.004), B, ao=1.0)
    p.add(blade_geo(y1 + 0.07, y1 + 0.07 + 0.82, 0.034, 0.012, tip=0.1), B, ao=1.0, angle=55)
    p.add(box_at((0, y1 + 0.03, -0.025), (0.026, 0.014, 0.014), r=0.003), B, ao=1.0)
    return p


def dagger_geo(name, side):
    p = W_(name)
    y1 = hilt(p, 0.15, guard_w=0.06)
    p.add(lathe([(0.02, y1 + 0.012), (0.016, y1 + 0.03)], n=8), G, angle=55)
    p.add(blade_geo(y1 + 0.03, y1 + 0.03 + 0.34, 0.026, 0.01, tip=0.07), B, ao=1.0, angle=55)
    # garde-poing côté extérieur
    arc = np.array([[0.0, y1 - 0.14, 0.0], [0.045, y1 - 0.12, 0.0], [0.055, y1 - 0.06, 0.0], [0.045, y1, 0.0]])
    p.add(ctube(arc, 0.008, m=2, n=5), G)
    p.add(sphere(0.012, 0.012, 0.012, n=6, m=4).t(0.055, y1 - 0.06, 0.0), B, ao=1.0)
    return p


def wpn_energy_dagger():
    l = dagger_geo("wpn_energy_dagger_l", 1)
    r = l.mirrored("wpn_energy_dagger_r", O)
    return [l, r]


def wpn_energy_shield():
    p = W_("wpn_energy_shield")
    R0 = 0.4
    p.add(hexring(R0, R0 - 0.07, -0.025, 0.035), R, angle=50)
    p.add(hexring(R0 - 0.07, R0 - 0.09, -0.01, 0.025), G, angle=50)
    # champ d'énergie (plaque hexagonale lumineuse)
    p.add(zloft([(0.0, R0 - 0.085, R0 - 0.085, 0.0, 0.0, 2.0), (0.012, R0 - 0.085, R0 - 0.085, 0.0, 0.0, 2.0)], n=6, cap0='ngon', cap1='ngon'), B, ao=1.0, angle=50)
    # alvéoles gravées (nid d'abeille) : petits hexagones sombres en relief
    cells = []
    for (cx, cy) in [(0, 0), (0.12, 0.07), (-0.12, 0.07), (0, 0.14), (0, -0.14), (0.12, -0.07), (-0.12, -0.07)]:
        cells.append(hexring(0.052, 0.04, 0.012, 0.02).t(cx, cy, 0.0))
    p.add(cells, G, angle=50)
    # bossage central et émetteurs aux sommets
    p.add(sphere(0.06, 0.06, 0.035, n=12, m=6).t(0, 0, 0.035), R, angle=55)
    p.add(sphere(0.026, 0.026, 0.02, n=8, m=5).t(0, 0, 0.065), B, ao=1.0)
    for k in range(6):
        a = 2 * math.pi * k / 6
        p.add(sphere(0.03, 0.03, 0.026, n=8, m=5).t(R0 * math.cos(a), R0 * math.sin(a), 0.035), G, angle=55)
        p.add(sphere(0.014, 0.014, 0.012, n=6, m=4).t(R0 * math.cos(a), R0 * math.sin(a), 0.058), B, ao=1.0)
    # poignée + brassard au dos
    p.add(box_at((0, 0, -0.06), (0.05, 0.2, 0.04), r=0.01), G, angle=55)
    p.add(box_at((0, 0.0, -0.04), (0.28, 0.035, 0.02), r=0.006), G, angle=55)
    p.add(box_at((0, 0.0, -0.1), (0.04, 0.05, 0.06), r=0.01), R, angle=55)
    return p


def wpn_wrench():
    p = W_("wpn_wrench")
    # manche
    p.add(lathe([(0.03, -0.4), (0.036, -0.38), (0.03, -0.34), (0.03, 0.0), (0.034, 0.05), (0.04, 0.3), (0.05, 0.4)], n=10, rz=0.7), G, angle=55)
    p.add(lathe([(0.04, -0.34), (0.04, -0.12)], n=10, rz=0.72), R, angle=55)
    p.add(lathe([(0.037, -0.3), (0.037, -0.28)], n=10, rz=0.72), G, angle=55)
    p.add(sphere(0.045, 0.03, 0.03, n=10, m=5).t(0, -0.4, 0.0), G, angle=55)
    # tête : mâchoire fixe + mâchoire mobile
    p.add(box_at((0, 0.5, 0.0), (0.2, 0.18, 0.052), r=0.016), G, angle=55)
    p.add(box_at((0.1, 0.62, 0.0), (0.06, 0.18, 0.052), r=0.012), G, angle=55)              # joue fixe
    p.add(box_at((-0.068, 0.64, 0.0), (0.06, 0.13, 0.05), r=0.012), R, angle=55)             # mâchoire mobile
    p.add(box_at((-0.095, 0.53, 0.0), (0.05, 0.1, 0.046), r=0.01), R, angle=55)
    # vis sans fin
    p.add(zc(-0.095, 0.5, -0.032, 0.032, 0.022, n=10), B, angle=55)
    for i in range(4):
        p.add(zc(-0.095, 0.5, -0.022 + i * 0.014, -0.014 + i * 0.014, 0.027, n=10), G, angle=55)
    p.add(box_at((0, 0.58, 0.0), (0.12, 0.012, 0.056), r=0.003), G)
    p.add([sphere(0.012, 0.012, 0.012, n=6, m=4).t(sx * 0.06, 0.46, 0.028) for sx in (-1, 1)], B, ao=1.0)
    return p


def gauntlet(name):
    p = W_(name)
    # brassard + vérins
    p.add(lathe([(0.065, -0.14), (0.07, -0.12), (0.072, 0.0), (0.066, 0.04)], n=12, rz=1.0), R, angle=55)
    p.add(torus(0.07, 0.012, 12, 4).t(0, -0.12, 0.0), G)
    for sx in (-1, 1):
        p.add(cyl_between((sx * 0.07, -0.1, -0.02), (sx * 0.075, 0.04, -0.02), 0.014, n=6), G, angle=55)
    # poing massif : bloc + phalanges plates
    p.add(box_at((0, 0.12, 0.0), (0.15, 0.13, 0.15), r=0.028), G, angle=55)
    for i in range(4):
        x = -0.054 + i * 0.036
        p.add(box_at((x, 0.125, 0.085), (0.034, 0.1, 0.04), r=0.008), R, angle=55)
        p.add(box_at((x, 0.185, 0.07), (0.034, 0.03, 0.05), r=0.008), R, angle=55)
        p.add(sphere(0.011, 0.011, 0.01, n=6, m=4).t(x, 0.2, 0.098), B, ao=1.0)
    p.add(box_at((0.085, 0.1, 0.04), (0.05, 0.1, 0.08), r=0.012, roll=-10), G, angle=55)    # pouce
    p.add(box_at((0, 0.06, 0.0), (0.12, 0.03, 0.14), r=0.008), R, angle=55)
    p.add(zdisc(0, 0.04, -0.075, 0.03, depth=0.01, n=10), B, ao=1.0)
    return p


def wpn_gauntlet():
    l = gauntlet("wpn_gauntlet_l")
    r = l.mirrored("wpn_gauntlet_r", O)
    return [l, r]


def wpn_plasma_staff():
    p = W_("wpn_plasma_staff")
    p.add(lathe([(0.02, -0.72), (0.026, -0.7), (0.022, -0.5), (0.02, 0.0), (0.022, 0.5), (0.026, 0.85), (0.03, 0.9)], n=9), G, angle=55)
    p.add(cone(0.026, 0.08, n=8).rx(180).t(0, -0.7, 0), G, angle=55)
    p.add(lathe([(0.028, -0.16), (0.028, 0.14)], n=9), R, angle=55)
    for y in (-0.16, 0.0, 0.14, 0.6):
        p.add(torus(0.028, 0.007, 10, 3).t(0, y, 0), G)
    # tête : trois arceaux autour de l'orbe
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 2
        c, s_ = math.cos(a), math.sin(a)
        path = np.array([[0.03 * c, 0.86, 0.03 * s_], [0.1 * c, 0.95, 0.1 * s_], [0.115 * c, 1.08, 0.115 * s_], [0.06 * c, 1.19, 0.06 * s_], [0.0, 1.22, 0.0]])
        p.add(ctube(path, 0.011, m=2, n=5), G)
    p.add(sphere(0.085, 0.085, 0.085, n=14, m=8).t(0, 1.04, 0.0), B, ao=1.0)
    p.add(torus(0.12, 0.01, 18, 4).rx(75).t(0, 1.04, 0.0), G)
    p.add(torus(0.105, 0.007, 16, 4).rz(70).t(0, 1.04, 0.0), B, ao=1.0)
    p.add(lathe([(0.04, 0.88), (0.05, 0.93), (0.03, 0.97)], n=9), G, angle=55)
    p.add([cube((0.0, 1.04 + 0.0, 0.0), (0.001, 0.001, 0.001))], G) if False else None
    p.add([sphere(0.013, 0.013, 0.013, n=6, m=4).t(0.14 * math.cos(a), 1.04 + 0.06 * math.sin(2 * a), 0.14 * math.sin(a)) for a in (0.4, 2.5, 4.4)], B, ao=1.0)
    return p


def wpn_controller():
    p = W_("wpn_controller")
    # galette hexagonale, face +Z, dos vers -Z
    p.add(zloft([(-0.045, 0.1, 0.1, 0.0, 0.0, 2.0), (-0.02, 0.115, 0.115, 0.0, 0.0, 2.0), (0.01, 0.115, 0.115, 0.0, 0.0, 2.0), (0.025, 0.1, 0.1, 0.0, 0.0, 2.0)], n=6, cap0='ngon', cap1='ngon'), R, angle=50)
    p.add(hexring(0.1, 0.075, 0.02, 0.034), G, angle=50)
    p.add(zloft([(0.02, 0.07, 0.07, 0.0, 0.0, 2.0), (0.032, 0.07, 0.07, 0.0, 0.0, 2.0)], n=6, cap0='ngon', cap1='ngon'), G, angle=50)
    p.add(zdisc(0, 0, 0.03, 0.022, depth=0.012, n=10), B, ao=1.0)
    # hologramme flottant : anneau, losange central, trois satellites
    p.add(torus(0.1, 0.006, 16, 3).rx(90).t(0, 0.0, 0.13), B, ao=1.0)
    dia = lathe([(0.0, -0.05), (0.04, 0.0), (0.0, 0.05)], n=4, cap=None).rx(90).t(0, 0, 0.13)
    p.add(dia, B, ao=1.0)
    p.add([cube((0.1 * math.cos(a), 0.1 * math.sin(a), 0.13), (0.02, 0.02, 0.02), yaw=0.6, roll=0.6) for a in (0.5, 2.6, 4.7)], B, ao=1.0, angle=40)
    for a in (0.5, 2.6, 4.7):
        p.add(cyl_between((0.045 * math.cos(a), 0.045 * math.sin(a), 0.034), (0.05 * math.cos(a), 0.05 * math.sin(a), 0.1), 0.004, n=4), B, ao=1.0)
    # sangle de main au dos
    p.add(box_at((0, 0, -0.065), (0.14, 0.04, 0.03), r=0.008), G, angle=55)
    return p


def wpn_med_gun():
    p = W_("wpn_med_gun")
    p.add(box_at((0, -0.012, -0.015), (0.044, 0.14, 0.056), r=0.01, pitch=-10), R, angle=55)
    p.add(box_at((0, 0.095, 0.03), (0.052, 0.075, 0.16), r=0.012), R, angle=55)
    # seringue : corps transparent (cadre G + liquide B), piston, aiguille
    p.add(zc(0, 0.115, 0.1, 0.27, 0.026, n=12), G, angle=55)
    p.add(zc(0, 0.115, 0.11, 0.26, 0.019, n=12), B, ao=1.0)
    p.add([zc(0, 0.115, z - 0.006, z + 0.006, 0.03, n=12) for z in (0.12, 0.2, 0.265)], G, angle=55)
    p.add(zc(0, 0.115, 0.27, 0.3, 0.02, 0.008, n=10), G, angle=55)
    p.add(spike((0, 0.115, 0.3), (0, 0.115, 0.42), r=0.005, n=6, bulge=0.9), G)
    p.add(zc(0, 0.115, -0.04, 0.1, 0.012, n=8), G, angle=55)
    p.add(zc(0, 0.115, -0.07, -0.04, 0.026, n=10), G, angle=55)
    # croix médicale + gâchette
    p.add([box_at((0.029, 0.1, 0.0), (0.006, 0.05, 0.016), r=0.002), box_at((0.029, 0.1, 0.0), (0.006, 0.016, 0.05), r=0.002)], B, ao=1.0)
    p.add(ctube(np.array([[0.0, 0.056, 0.085], [0.0, 0.0, 0.09], [0.0, 0.004, 0.045]]), 0.006, m=2, n=5), G)
    p.add(cube((0, 0.15, 0.1), (0.016, 0.02, 0.04)), G, angle=40)
    p.add(sphere(0.01, 0.01, 0.01, n=6, m=4).t(0, 0.153, 0.015), B, ao=1.0)
    return p


WEAPONS = [wpn_blaster, wpn_rifle_plasma, wpn_railgun, wpn_energy_blade, wpn_energy_dagger, wpn_energy_shield, wpn_wrench, wpn_gauntlet,
           wpn_plasma_staff, wpn_controller, wpn_med_gun]
