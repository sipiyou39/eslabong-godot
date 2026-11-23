"""Silhouettes d'armes (axe +x depuis la poignee, longueur ~1.75) pour emblemes de classes et reliques."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from shapes import *

PI = math.pi
WP = {}


def wp(fn):
    WP[fn.__name__[2:]] = fn
    return fn


def haft(P, L=1.75, w=0.045, mat='wood', tag='h', x0=0.0):
    P.L(tag, mat, outline=0.03).rrect(x0, -w, L, w, w * 0.6)


def orbtip(P, x, mat, r=0.17, tag='o'):
    P.L(tag + 'g', 'gold', outline=0.03).ell(x - 0.12, 0, 0.06, 0.13)
    P.L(tag, mat, outline=0.03, bevel=r).circle(x + 0.05, 0, r)


@wp
def w_sword_long(P):
    sword(P, 0, 0, 0, L=1.78, w=0.17, guard_w=0.26, tag='w')


@wp
def w_sword_great(P):
    sword(P, 0, 0, 0, L=1.85, w=0.27, guard_w=0.34, tag='w')


@wp
def w_sword_short(P):
    sword(P, 0.3, 0, 0, L=1.35, w=0.17, guard_w=0.24, tag='w')


@wp
def w_dagger(P):
    sword(P, 0.45, 0, 0, L=1.15, w=0.15, guard_w=0.2, tag='w')


@wp
def w_rapier(P):
    sword(P, 0.1, 0, 0, L=1.8, w=0.07, guard_w=0.2, tag='w')
    P.L('cup', 'gold', outline=0.03).ell(0.38, 0, 0.1, 0.21)


@wp
def w_katana(P):
    P.L('wr', 'cloth_red', outline=0.03).rrect(0.0, -0.045, 0.42, 0.045, 0.03)
    P.L('ts', 'gold', outline=0.03).ell(0.45, 0, 0.05, 0.17)
    D = P.L('bl', 'steel', outline=0.03)
    D.taper(bez([(0.48, 0), (1.0, -0.02), (1.5, -0.06), (1.8, -0.2)], 24), lambda t: 0.12 * (1 - t ** 4) + 0.01)


@wp
def w_axe_great(P):
    haft(P)
    D = P.L('hd', 'steel', outline=0.035)
    D.poly(catmull([(1.2, -0.04), (1.1, -0.45), (1.38, -0.62), (1.68, -0.5), (1.62, -0.2), (1.5, -0.04)], 6) )
    D.poly(catmull([(1.2, 0.04), (1.1, 0.45), (1.38, 0.62), (1.68, 0.5), (1.62, 0.2), (1.5, 0.04)], 6))
    P.L('sp', 'steel', outline=0.03).poly([(1.74, -0.06), (1.95, 0), (1.74, 0.06)])


@wp
def w_axe_double(P):
    haft(P, L=1.6)
    for s in (-1, 1):
        D = P.L('hd%d' % s, 'steel', outline=0.035)
        D.poly(catmull([(1.45, s * 0.04), (1.18, s * 0.34), (1.12, s * 0.62), (1.52, s * 0.58), (1.64, s * 0.3), (1.58, s * 0.05)], 6))
    P.L('ct', 'gold', outline=0.03).circle(1.48, 0, 0.07)


@wp
def w_axe_hand(P):
    haft(P, L=1.4)
    D = P.L('hd', 'steel', outline=0.035)
    D.poly(catmull([(1.12, -0.04), (1.0, -0.4), (1.32, -0.5), (1.5, -0.28), (1.38, -0.04)], 6))


@wp
def w_hammer_war(P):
    haft(P)
    P.L('hd', 'iron', outline=0.035).rrect(1.28, -0.28, 1.72, 0.28, 0.06)
    P.L('bd', 'steel', outline=0.03).rrect(1.22, -0.3, 1.3, 0.3, 0.03)
    P.L('sp', 'steel', outline=0.03).poly([(1.72, -0.07), (1.92, 0), (1.72, 0.07)])


@wp
def w_hammer_great(P):
    haft(P, w=0.055)
    P.L('hd', 'iron', outline=0.035).rrect(1.15, -0.42, 1.8, 0.42, 0.08)
    P.L('bd', 'gold', outline=0.03).rrect(1.1, -0.44, 1.2, 0.44, 0.03)
    P.L('bd2', 'gold', outline=0.03).rrect(1.75, -0.44, 1.85, 0.44, 0.03)


@wp
def w_mace(P):
    haft(P, L=1.5)
    P.L('bl', 'iron', outline=0.035, bevel=0.2).circle(1.55, 0, 0.27)
    D = P.L('sk', 'steel', outline=0.03)
    for k in range(8):
        with D.at(1.55, 0, k * 45):
            D.poly([(0.22, -0.07), (0.4, 0), (0.22, 0.07)])


@wp
def w_pick(P):
    haft(P, L=1.6)
    D = P.L('hd', 'iron', outline=0.035)
    D.taper(bez([(1.5, -0.55), (1.45, -0.2), (1.45, 0.2), (1.5, 0.55)], 20), lambda t: 0.16 * math.sin(PI * t) ** 0.7 + 0.03)
    D.poly([(1.4, -0.06), (1.7, 0), (1.4, 0.06)])


@wp
def w_halberd(P):
    haft(P, L=1.8)
    D = P.L('hd', 'steel', outline=0.035)
    D.poly(catmull([(1.2, -0.04), (1.1, -0.5), (1.4, -0.58), (1.55, -0.12), (1.55, -0.04)], 6))
    P.L('tp', 'steel', outline=0.035).poly([(1.74, -0.1), (2.0, 0), (1.74, 0.1)])
    P.L('bk', 'iron', outline=0.03).poly([(1.25, 0.04), (1.5, 0.28), (1.5, 0.04)])


@wp
def w_spear(P):
    haft(P, L=1.55)
    P.L('hd', 'steel', outline=0.035).poly([(1.5, 0), (1.62, -0.15), (2.0, 0), (1.62, 0.15)])
    P.L('co', 'gold', outline=0.03).rrect(1.45, -0.09, 1.55, 0.09, 0.03)
    P.L('tl', 'cloth_red', outline=0.03).poly([(1.4, 0.02), (1.25, 0.2), (1.3, 0.02)])


@wp
def w_scythe(P):
    haft(P, L=1.75)
    D = P.L('bl', 'steel', outline=0.035)
    D.taper(bez([(1.65, 0), (1.65, -0.5), (1.1, -0.72), (0.65, -0.55)], 24), lambda t: 0.2 * math.sin(PI * min(t * 1.1, 1)) ** 0.8 * (1 - t) + 0.02)


@wp
def w_bow_long(P):
    D = P.L('bw', 'wood', outline=0.035)
    D.taper(bez([(0.6, -0.9), (1.25, -0.45), (1.25, 0.45), (0.6, 0.9)], 28), lambda t: 0.1 * math.sin(PI * t) ** 0.5 + 0.03)
    P.L('st', 'bone', outline=0.015).line(0.6, -0.9, 0.6, 0.9, 0.025)
    sword  # noqa
    D = P.L('ar', 'wood', outline=0.03)
    D.rrect(0.1, -0.025, 1.45, 0.025, 0.02)
    P.L('ah', 'steel', outline=0.03).poly([(1.4, -0.09), (1.62, 0), (1.4, 0.09)])


@wp
def w_bow_short(P):
    D = P.L('bw', 'wood', outline=0.035)
    D.taper(bez([(0.7, -0.65), (1.2, -0.3), (1.2, 0.3), (0.7, 0.65)], 24), lambda t: 0.1 * math.sin(PI * t) ** 0.5 + 0.03)
    P.L('st', 'bone', outline=0.015).line(0.7, -0.65, 0.7, 0.65, 0.025)
    P.L('ar', 'wood', outline=0.03).rrect(0.25, -0.025, 1.5, 0.025, 0.02)
    P.L('ah', 'steel', outline=0.03).poly([(1.45, -0.09), (1.68, 0), (1.45, 0.09)])


@wp
def w_crossbow(P):
    P.L('sk', 'wood', outline=0.035).rrect(0.1, -0.08, 1.5, 0.08, 0.05)
    D = P.L('pr', 'iron', outline=0.035)
    D.taper(bez([(1.1, -0.85), (1.45, -0.35), (1.45, 0.35), (1.1, 0.85)], 24), lambda t: 0.1 * math.sin(PI * t) ** 0.5 + 0.04)
    P.L('st', 'bone', outline=0.015).path([(1.1, -0.85), (0.75, 0), (1.1, 0.85)], 0.025)
    P.L('bt', 'steel', outline=0.03).poly([(0.8, -0.03), (1.65, 0), (0.8, 0.03), (0.78, 0)])


@wp
def w_staff_wood(P):
    D = P.L('hf', 'wood', outline=0.035)
    D.taper(bez([(0, 0), (0.6, 0.06), (1.2, -0.06), (1.65, 0)], 24), lambda t: 0.1 - 0.02 * t)
    P.L('og', 'emerald', outline=0.03, bevel=0.15).circle(1.75, 0, 0.18)
    D = P.L('lf', 'green', outline=0.03)
    sh_leaf(D, 1.55, -0.18, 0.12, -100)
    sh_leaf(D, 1.55, 0.18, 0.12, 100)


@wp
def w_staff_crystal(P):
    haft(P, L=1.55)
    D = P.L('cr', 'sapphire', outline=0.035)
    D.poly([(1.45, 0), (1.62, -0.17), (1.95, 0), (1.62, 0.17)])
    P.L('cg', 'gold', outline=0.03).rrect(1.38, -0.12, 1.48, 0.12, 0.03)


@wp
def w_staff_holy(P):
    haft(P, L=1.55, mat='gold')
    P.L('rg', 'gold', outline=0.035).ring(1.75, 0, 0.2, 0.08)
    P.L('og', 'white', outline=0.0, bevel=0.2).circle(1.75, 0, 0.12)
    D = P.L('wg', 'white', outline=0.03)
    for s in (-1, 1):
        D.taper(bez([(1.55, s * 0.05), (1.5, s * 0.3), (1.4, s * 0.45)], 8), lambda t: 0.1 * (1 - t) + 0.01)


@wp
def w_staff_storm(P):
    haft(P, L=1.5)
    P.L('og', 'gold', outline=0.03).ring(1.72, 0, 0.22, 0.07)
    sh_bolt(P.L('bt', 'topaz', outline=0.03), 1.72, 0, 0.2, 90)


@wp
def w_staff_skull(P):
    haft(P, L=1.55, mat='dark')
    sh_skull(P.L('sk', 'bone', outline=0.035), 1.78, 0, 0.26, 90)


@wp
def w_staff_fire(P):
    haft(P, L=1.55)
    P.L('cp', 'gold', outline=0.03).poly([(1.5, 0), (1.62, -0.16), (1.7, -0.16), (1.7, 0.16), (1.62, 0.16)])
    sh_flame(P.L('fl', 'fire', outline=0.035), 1.88, 0, 0.26, 90)


@wp
def w_staff_ice(P):
    haft(P, L=1.5)
    D = P.L('cr', 'ice', outline=0.035)
    D.poly([(1.4, 0), (1.55, -0.15), (1.95, 0), (1.55, 0.15)])
    D.poly([(1.5, -0.1), (1.7, -0.3), (1.78, -0.05)])
    D.poly([(1.5, 0.1), (1.7, 0.3), (1.78, 0.05)])


@wp
def w_staff_void(P):
    haft(P, L=1.5, mat='dark')
    P.L('rg', 'amethyst', outline=0.035).ring(1.78, 0, 0.26, 0.07)
    P.L('og', 'black', outline=0.03, bevel=0.2).circle(1.78, 0, 0.17)
    spark = P.L('sp', 'amethyst', outline=0.0, bevel=0.02)
    spark.star(1.78, 0, 4, 0.16, 0.04, 0)


@wp
def w_staff_totem(P):
    haft(P, L=1.55)
    D = P.L('tt', 'wood', outline=0.035)
    D.rrect(1.45, -0.2, 1.85, 0.2, 0.06)
    P.L('ey', 'cloth_red', outline=0.0).circle(1.6, -0.08, 0.05)
    P.L('ey2', 'cloth_red', outline=0.0).circle(1.6, 0.08, 0.05)
    D = P.L('fe', 'cloth_blue', outline=0.03)
    for s in (-1, 1):
        D.taper([(1.8, s * 0.12), (1.95, s * 0.3)], lambda t: 0.12 * (1 - t) + 0.01)


@wp
def w_wand(P):
    haft(P, L=1.4, w=0.035, mat='dark')
    sh_star(P.L('st', 'topaz', outline=0.03), 1.55, 0, 0.2, 90)


@wp
def w_censer(P):
    P.L('ch', 'iron', outline=0.03).path(catmull([(0.2, 0), (0.7, -0.15), (1.15, 0.0), (1.4, 0.05)], 8), 0.05)
    P.L('bw', 'gold', outline=0.035, bevel=0.15).circle(1.55, 0.05, 0.26)
    P.L('hl', 'dark', outline=0.0).ell(1.55, 0.05, 0.1, 0.12)
    D = P.L('sm', 'white', outline=0.02)
    D.taper(bez([(1.55, -0.22), (1.7, -0.5), (1.45, -0.7), (1.62, -0.95)], 14), lambda t: 0.14 * math.sin(PI * min(t * 1.3, 1)) + 0.01)


@wp
def w_fists(P):
    for k, (x, y) in enumerate(((1.05, -0.28), (1.0, 0.3))):
        sh_fist(P.L('f%d' % k, 'leather', outline=0.035), x, y, 0.5, 0)
    D = P.L('sp', 'steel', outline=0.025)
    for (x, y) in ((1.45, -0.34), (1.45, -0.18), (1.4, 0.24), (1.4, 0.4)):
        D.circle(x, y, 0.045)


@wp
def w_claws(P):
    for k, y in enumerate((-0.22, 0.0, 0.22)):
        D = P.L('c%d' % k, 'bone', outline=0.03)
        D.taper(bez([(0.9, y * 1.0), (1.3, y * 1.2 - 0.12), (1.6, y * 1.6 - 0.1), (1.8, y * 2.0 + 0.1)], 18), lambda t: 0.15 * (1 - t) ** 0.7 + 0.01)
    P.L('gr', 'leather', outline=0.035).rrect(0.55, -0.34, 1.0, 0.34, 0.1)


@wp
def w_paddles(P):
    for s in (-1, 1):
        D = P.L('pd%d' % s, 'wood', outline=0.035)
        with D.at(0.1, 0, s * 22):
            D.rrect(0, -0.045, 0.7, 0.045, 0.03)
        with P.L('pf%d' % s, 'cloth_red', outline=0.03).at(0.1, 0, s * 22) as F:
            F.ell(0.95, 0, 0.36, 0.34)


def draw_weapon(P, kind, tx=-0.62, ty=0.62, rot=-45, s=1.0):
    WP['w_' + kind if False else kind](SubParts(P, tx, ty, s, rot, prefix='wp_'))


WP = {k: v for k, v in WP.items()}
