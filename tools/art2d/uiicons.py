"""Icones UI 48x48 (assets/ui/icons) - dessinees par calques + biseau."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from shapes import *

OUT = ASSETS + '/ui/icons'
ICONS = {}


def icon(fn):
    ICONS[fn.__name__] = fn
    return fn


def gloss(P, x, y, rx, ry, rot=-30, name='gl'):
    P.L(name, 'white', outline=0, bevel=0.04, spec=0).ell(x, y, rx, ry, rot)


def mk(P, name, mat, **k):
    return P.L(name, mat, **k)


@icon
def hp(P):
    sh_heart(mk(P, 'a', 'blood'), 0, 0.02, 0.88)
    gloss(P, -0.38, -0.36, 0.2, 0.1)


@icon
def mana(P):
    sh_drop(mk(P, 'a', 'sapphire'), 0, 0.04, 0.88)
    gloss(P, -0.24, 0.12, 0.1, 0.22, 15)


@icon
def stamina(P):
    sh_wing(mk(P, 'a', 'emerald'), 0.2, -0.1, 1.5)


@icon
def power(P):
    sword(P, -0.88, 0.88, -45, L=2.45, w=0.3, guard_w=0.42, tag='s')


@icon
def speed(P):
    sh_chevron(mk(P, 'a', 'ice'), -0.32, 0, 0.9, 90)
    sh_chevron(mk(P, 'b', 'ice'), 0.4, 0, 0.9, 90)


@icon
def defense(P):
    sh_shield(mk(P, 'a', 'iron'), 0, 0, 0.92)
    sh_shield(mk(P, 'b', 'steel', outline=0.025), 0, 0.03, 0.62)


@icon
def mres(P):
    sh_shield(mk(P, 'a', 'amethyst'), 0, 0, 0.92)
    sh_star(mk(P, 'b', 'white', outline=0.03), 0, -0.05, 0.4)


@icon
def gold(P):
    sh_coin(mk(P, 'a', 'gold'), 0, 0, 0.92)
    mk(P, 'b', 'bronze', outline=0.0, bevel=0.05).ring(0, 0, 0.62, 0.1)
    sh_star(mk(P, 'c', 'bronze', outline=0.0, bevel=0.05), 0, 0.02, 0.34)


@icon
def gem(P):
    sh_gem(mk(P, 'a', 'sapphire'), 0, 0.02, 0.9)
    D = mk(P, 'b', 'white', outline=0, bevel=0.03, spec=0)
    D.poly([(-0.55, -0.7), (-0.2, -0.7), (-0.5, -0.32)])


@icon
def star(P):
    sh_star(mk(P, 'a', 'gold'), 0, 0.04, 0.95)


@icon
def crown_(P):
    crown(P, 0, 0.12, 2.5, tag='c')


@icon
def skull(P):
    sh_skull(mk(P, 'a', 'bone'), 0, 0, 0.92)


@icon
def heal(P):
    sh_plus(mk(P, 'a', 'emerald'), 0, 0, 0.85, t=0.56)
    gloss(P, -0.14, -0.55, 0.1, 0.06, 0)


@icon
def shield(P):
    sh_shield(mk(P, 'a', 'steel'), 0, 0, 0.92)
    sh_shield(mk(P, 'b', 'cloth_blue', outline=0.02), 0, 0.03, 0.66)
    sh_star(mk(P, 'c', 'gold', outline=0.02), 0, -0.08, 0.28)


@icon
def injury(P):
    for a in (45, -45):
        D = mk(P, 'p%d' % a, 'parch', bevel=0.07)
        with D.at(0, 0, a):
            D.rrect(-0.95, -0.28, 0.95, 0.28, 0.12)
    D = mk(P, 'd', 'ruby', outline=0.02, bevel=0.03)
    for dx, dy in ((0.0, 0.0),):
        D.rrect(-0.2, -0.2, 0.2, 0.2, 0.08)


@icon
def form_up(P):
    sh_arrow_r(mk(P, 'a', 'emerald'), 0, 0, 0.95, -90, w=0.5, hw=1.05, hl=0.95)


@icon
def form_down(P):
    sh_arrow_r(mk(P, 'a', 'ruby'), 0, 0, 0.95, 90, w=0.5, hw=1.05, hl=0.95)


@icon
def form_flat(P):
    sh_arrow_r(mk(P, 'a', 'topaz'), 0, 0, 0.95, 0, w=0.5, hw=1.05, hl=0.95)


def medal_base(P, ribbon=('cloth_red', 'cloth_blue')):
    for sx, mt in ((-1, ribbon[0]), (1, ribbon[1])):
        D = mk(P, 'rb%d' % sx, mt, bevel=0.05)
        D.poly([(sx * 0.1, -0.95), (sx * 0.55, -0.95), (sx * 0.28, -0.1), (sx * -0.1, -0.1)])
    sh_coin(mk(P, 'disc', 'gold'), 0, 0.3, 0.62)
    mk(P, 'ring', 'bronze', outline=0, bevel=0.04).ring(0, 0.3, 0.48, 0.07)


@icon
def medal_iron_wall(P):
    medal_base(P)
    D = mk(P, 'in', 'iron', outline=0.015, bevel=0.03)
    for r, (y, off) in enumerate(((0.12, 0), (0.3, 0.14), (0.48, 0))):
        for c in range(2 + (0 if off == 0 else 1)):
            x = -0.2 + c * 0.2 - (0.1 if off else 0) + (0.0)
            D.rect(x - 0.09, y - 0.07, x + 0.09, y + 0.07)


@icon
def medal_wrecking_hand(P):
    medal_base(P)
    sh_fist(mk(P, 'in', 'dark', outline=0.015, bevel=0.03), 0, 0.3, 0.32)


@icon
def medal_clutch(P):
    medal_base(P)
    sh_bolt(mk(P, 'in', 'dark', outline=0.015, bevel=0.03), 0, 0.3, 0.34)


@icon
def medal_lifesaver(P):
    medal_base(P)
    sh_plus(mk(P, 'in', 'ruby', outline=0.015, bevel=0.03), 0, 0.3, 0.32, t=0.5)


@icon
def calendar(P):
    D = mk(P, 'pg', 'parch')
    D.rrect(-0.85, -0.7, 0.85, 0.9, 0.12)
    D = mk(P, 'hd', 'cloth_red', outline=0.02)
    D.rrect(-0.85, -0.7, 0.85, -0.2, 0.12)
    D.rect(-0.85, -0.4, 0.85, -0.2)
    D = mk(P, 'rg', 'iron', outline=0.02)
    for x in (-0.4, 0.4):
        D.rrect(x - 0.07, -0.95, x + 0.07, -0.5, 0.05)
    D = mk(P, 'gd', 'dark', outline=0.0, bevel=0.03)
    for r in range(2):
        for c in range(3):
            D.rrect(-0.6 + c * 0.45, 0.0 + r * 0.38, -0.6 + c * 0.45 + 0.3, 0.0 + r * 0.38 + 0.22, 0.04)


@icon
def trophy(P):
    D = mk(P, 'h', 'gold')
    D.path(Draw.arc_pts(-0.62, -0.25, 0.3, 0.32, 90, 270, 14), 0.14)
    D.path(Draw.arc_pts(0.62, -0.25, 0.3, 0.32, -90, 90, 14), 0.14)
    D = mk(P, 'c', 'gold')
    D.poly(catmull([(-0.6, -0.8), (0.6, -0.8), (0.55, -0.2), (0.3, 0.2), (0.12, 0.35), (-0.12, 0.35), (-0.3, 0.2), (-0.55, -0.2)], 6))
    D.rect(-0.12, 0.3, 0.12, 0.62)
    D.rrect(-0.5, 0.58, 0.5, 0.92, 0.08)
    sh_star(mk(P, 's', 'bronze', outline=0.0, bevel=0.04), 0, -0.34, 0.26)


@icon
def swords(P):
    sword(P, -0.9, 0.9, -45, L=2.45, w=0.26, guard_w=0.36, tag='a')
    sword(P, 0.9, 0.9, -135, L=2.45, w=0.26, guard_w=0.36, tag='b')


@icon
def flag(P):
    D = mk(P, 'pole', 'wood')
    D.rrect(-0.72, -0.95, -0.56, 0.95, 0.06)
    D = mk(P, 'f', 'cloth_red')
    D.poly([(-0.56, -0.85), (0.1, -0.7), (0.5, -0.85), (0.9, -0.7), (0.9, 0.0), (0.5, 0.15), (0.1, 0.0), (-0.56, 0.1)])
    D = mk(P, 'ball', 'gold', outline=0.02)
    D.circle(-0.64, -0.97, 0.13)


@icon
def lock(P):
    sh_lock(mk(P, 'a', 'gold'), 0, 0, 0.92)


@icon
def check(P):
    sh_check(mk(P, 'a', 'emerald'), 0, 0, 0.95, w=0.46)


@icon
def cross_close(P):
    sh_cross_x(mk(P, 'a', 'ruby'), 0, 0, 0.9, w=0.44)


@icon
def settings(P):
    sh_gear(mk(P, 'a', 'iron'), 0, 0, 0.95, n=8, ri=0.72, hole=0.34)


@icon
def sound(P):
    D = mk(P, 'sp', 'iron')
    D.poly([(-0.9, -0.28), (-0.5, -0.28), (-0.05, -0.7), (-0.05, 0.7), (-0.5, 0.28), (-0.9, 0.28)])
    D = mk(P, 'w', 'steel', outline=0.03, bevel=0.04)
    D.arc(-0.05, 0, 0.5, -45, 45, 0.13)
    D.arc(-0.05, 0, 0.82, -45, 45, 0.13)


@icon
def gamepad(P):
    D = mk(P, 'b', 'iron')
    D.rrect(-0.95, -0.5, 0.95, 0.45, 0.35)
    D.circle(-0.55, 0.45, 0.28)
    D.circle(0.55, 0.45, 0.28)
    D = mk(P, 'k', 'dark', outline=0.015, bevel=0.03)
    D.rect(-0.58, -0.12, -0.26, 0.0)
    D.rect(-0.46, -0.28, -0.38, 0.16)
    D = mk(P, 'o', 'ruby', outline=0.015, bevel=0.03)
    D.circle(0.4, -0.12, 0.09)
    D.circle(0.6, 0.03, 0.09)
    D.circle(0.4, 0.14, 0.09)
    D.circle(0.2, 0.03, 0.09)


@icon
def mouse(P):
    D = mk(P, 'b', 'steel')
    D.rrect(-0.55, -0.95, 0.55, 0.95, 0.5)
    D = mk(P, 'l', 'dark', outline=0.0, bevel=0.03)
    D.rect(-0.03, -0.9, 0.03, -0.15)
    D.rrect(-0.52, -0.16, 0.52, -0.08, 0.02)
    D = mk(P, 'w', 'ruby', outline=0.02, bevel=0.03)
    D.rrect(-0.09, -0.62, 0.09, -0.3, 0.07)


@icon
def keyboard(P):
    D = mk(P, 'b', 'iron')
    D.rrect(-0.98, -0.55, 0.98, 0.55, 0.14)
    D = mk(P, 'k', 'steel', outline=0.012, bevel=0.03)
    for r in range(3):
        for c in range(5):
            if r == 2 and c in (1, 2, 3):
                continue
            D.rrect(-0.82 + c * 0.34, -0.38 + r * 0.3, -0.82 + c * 0.34 + 0.27, -0.38 + r * 0.3 + 0.22, 0.04)
        if r == 2:
            D.rrect(-0.48, -0.38 + r * 0.3, 0.54, -0.38 + r * 0.3 + 0.22, 0.04)


@icon
def search(P):
    D = mk(P, 'h', 'bronze')
    with D.at(0, 0, 45):
        D.rrect(0.35, -0.13, 1.0, 0.13, 0.06)
    D = mk(P, 'r', 'steel')
    D.ring(-0.22, -0.22, 0.5, 0.2)
    D = mk(P, 'g', 'glass', outline=0.0, bevel=0.1, spec=0.6)
    D.circle(-0.22, -0.22, 0.42)
    P.layers['g'][0].img.putalpha(P.layers['g'][0].img) if False else None


@icon
def filter_(P):
    D = mk(P, 'a', 'iron')
    D.poly([(-0.95, -0.85), (0.95, -0.85), (0.2, 0.0), (0.2, 0.9), (-0.2, 0.65), (-0.2, 0.0)])


def _bars(P, up):
    D = mk(P, 'b', 'steel')
    for i in range(3):
        L = (0.4 + 0.3 * i) if up else (1.0 - 0.3 * i)
        D.rrect(-0.9, -0.62 + i * 0.5, -0.9 + L, -0.62 + i * 0.5 + 0.3, 0.08)
    sh_arrow_r(mk(P, 'ar', 'emerald' if up else 'ruby'), 0.62, 0, 0.5, -90 if up else 90, w=0.34, hw=0.8, hl=0.7)


@icon
def sort_asc(P):
    _bars(P, True)


@icon
def sort_desc(P):
    _bars(P, False)


@icon
def arrow_left(P):
    sh_arrow_r(mk(P, 'a', 'gold'), 0, 0, 0.95, 180, w=0.5, hw=1.1, hl=0.9)


@icon
def arrow_right(P):
    sh_arrow_r(mk(P, 'a', 'gold'), 0, 0, 0.95, 0, w=0.5, hw=1.1, hl=0.9)


@icon
def play(P):
    mk(P, 'a', 'emerald').poly([(-0.6, -0.85), (0.9, 0), (-0.6, 0.85)])


@icon
def pause(P):
    D = mk(P, 'a', 'steel')
    D.rrect(-0.7, -0.8, -0.15, 0.8, 0.1)
    D.rrect(0.15, -0.8, 0.7, 0.8, 0.1)


@icon
def ff(P):
    D = mk(P, 'a', 'steel')
    D.poly([(-0.95, -0.75), (0.0, 0), (-0.95, 0.75)])
    D.poly([(0.0, -0.75), (0.95, 0), (0.0, 0.75)])


@icon
def camera(P):
    D = mk(P, 'b', 'iron')
    D.rrect(-0.95, -0.5, 0.95, 0.72, 0.16)
    D.rrect(-0.4, -0.78, 0.2, -0.4, 0.08)
    D = mk(P, 'o', 'steel', outline=0.02)
    D.circle(0, 0.1, 0.46)
    D = mk(P, 'l', 'sapphire', outline=0.02, bevel=0.15)
    D.circle(0, 0.1, 0.3)


@icon
def tactics(P):
    D = mk(P, 'b', 'wood')
    D.rrect(-0.8, -0.95, 0.8, 0.95, 0.12)
    D = mk(P, 'p', 'parch', outline=0.02)
    D.rrect(-0.65, -0.72, 0.65, 0.8, 0.06)
    D = mk(P, 'cl', 'iron', outline=0.02)
    D.rrect(-0.3, -1.0, 0.3, -0.6, 0.08)
    D = mk(P, 'm', 'ruby', outline=0.015, bevel=0.03)
    D.path([(-0.4, -0.3), (-0.1, 0.0)], 0.1)
    D.path([(-0.1, -0.3), (-0.4, 0.0)], 0.1)
    D = mk(P, 'o', 'sapphire', outline=0.015, bevel=0.03)
    D.ring(0.35, 0.45, 0.15, 0.1)
    D = mk(P, 'ar', 'dark', outline=0.0, bevel=0.03)
    D.path(catmull([(-0.3, 0.3), (-0.1, 0.5), (0.1, 0.1), (0.2, -0.15)], 6), 0.07)
    D.poly([(0.1, -0.3), (0.34, -0.12), (0.12, 0.0)])


@icon
def roster(P):
    sh_person(mk(P, 'a', 'iron'), -0.52, 0.0, 0.55)
    sh_person(mk(P, 'b', 'iron'), 0.52, 0.0, 0.55)
    sh_person(mk(P, 'c', 'steel'), 0.0, 0.18, 0.72)


@icon
def market(P):
    D = mk(P, 'c', 'wood')
    D.rect(-0.8, 0.0, 0.8, 0.95)
    D = mk(P, 'aw', 'cloth_red')
    D.poly([(-0.95, -0.2), (-0.7, -0.85), (0.7, -0.85), (0.95, -0.2)])
    for k in range(4):
        D.ell(-0.71 + k * 0.475, -0.2, 0.24, 0.2)
    D = mk(P, 'st', 'parch', outline=0.02)
    for k in (-1, 1):
        D.poly([(k * 0.35 - 0.18, -0.82), (k * 0.35 + 0.18, -0.82), (k * 0.35 + 0.2, -0.2), (k * 0.35 - 0.2, -0.2)])
    sh_coin(mk(P, 'co', 'gold', outline=0.02), 0, 0.45, 0.26)


@icon
def club(P):
    sh_shield(mk(P, 'a', 'gold'), 0, 0, 0.95)
    sh_shield(mk(P, 'b', 'cloth_blue', outline=0.02), 0, 0.03, 0.72)
    sword(P, -0.34, 0.45, -52, L=0.95, w=0.14, tag='c', guard_w=0.2)
    sword(P, 0.34, 0.45, -128, L=0.95, w=0.14, tag='d', guard_w=0.2)


@icon
def league(P):
    for sx in (-1, 1):
        D = mk(P, 'l%d' % sx, 'emerald', outline=0.025, bevel=0.05)
        for k in range(6):
            a = math.radians(-70 + k * 28)
            cx, cy = sx * 0.72 * math.cos(a) * 0 + sx * (0.78 * math.cos(math.radians(0 + 0))) * 0, 0
            px = sx * 0.78 * math.cos(a + math.pi * 0.0) * 0.9
            py = 0.85 * math.sin(a) * 0.95
            with D.at(sx * (0.15 + 0.6 * math.cos(math.radians(k * 24 - 24))), -0.8 + k * 0.32, sx * (-35 + k * 10)):
                D.ell(0, 0, 0.26, 0.12)
    sh_star(mk(P, 's', 'gold'), 0, -0.05, 0.42)


@icon
def cup(P):
    D = mk(P, 'a', 'gold')
    D.poly(catmull([(-0.8, -0.7), (0.8, -0.7), (0.7, -0.1), (0.35, 0.3), (-0.35, 0.3), (-0.7, -0.1)], 6, closed=True))
    D.rect(-0.1, 0.25, 0.1, 0.65)
    D.rrect(-0.5, 0.6, 0.5, 0.92, 0.1)
    D = mk(P, 'r', 'ruby', outline=0.02)
    D.rect(-0.8, -0.82, 0.8, -0.62)
    D.circle(0, -0.2, 0.2)


@icon
def tower(P):
    sh_tower(mk(P, 'a', 'iron'), 0, 0, 0.95)
    D = mk(P, 'f', 'cloth_red', outline=0.02)
    D.poly([(0, -0.95), (0.4, -0.85), (0, -0.74)])


@icon
def gate(P):
    D = mk(P, 'a', 'iron')
    D.rect(-0.95, -0.2, -0.45, 0.95)
    D.rect(0.45, -0.2, 0.95, 0.95)
    D.poly(np.vstack([[(-0.95, 0.95), (-0.95, -0.1)], Draw.arc_pts(0, -0.1, 0.95, 0.85, 180, 360, 24), [(0.95, 0.95)]]))
    D.poly(np.vstack([Draw.arc_pts(0, -0.1, 0.5, 0.5, 180, 360, 14), [(0.5, 0.95), (-0.5, 0.95)]]), 0)
    D = mk(P, 'b', 'dark', outline=0.015, bevel=0.03)
    for x in (-0.38, -0.13, 0.13, 0.38):
        D.rect(x - 0.05, -0.45, x + 0.05, 0.9)
    D.rect(-0.46, 0.1, 0.46, 0.18)


@icon
def thunder(P):
    sh_cloud(mk(P, 'a', 'iron'), 0, -0.3, 0.85)
    sh_bolt(mk(P, 'b', 'topaz'), 0.05, 0.5, 0.5)


@icon
def draft(P):
    for k, (a, dx) in enumerate(((-18, -0.38), (0, 0.0), (18, 0.38))):
        D = mk(P, 'c%d' % k, 'parch' if k != 1 else 'white', bevel=0.05)
        with D.at(dx, 0.12, a):
            D.rrect(-0.38, -0.7, 0.38, 0.7, 0.07)
    sh_star(mk(P, 's', 'gold', outline=0.02), 0, 0.0, 0.28)


@icon
def academy(P):
    D = mk(P, 'b', 'dark')
    D.poly([(-0.55, 0.05), (-0.55, 0.55), (0, 0.8), (0.55, 0.55), (0.55, 0.05)])
    D = mk(P, 't', 'cloth_blue')
    D.poly([(-1.0, -0.2), (0, -0.7), (1.0, -0.2), (0, 0.3)])
    D = mk(P, 'ta', 'gold', outline=0.02)
    D.path([(0.7, -0.15), (0.78, 0.5)], 0.06)
    D.circle(0.78, 0.55, 0.1)


@icon
def training(P):
    sh_dumbbell(mk(P, 'a', 'iron'), 0, 0, 0.95, -35)


@icon
def hall(P):
    D = mk(P, 'a', 'bone')
    D.poly([(-0.98, -0.35), (0, -0.9), (0.98, -0.35)])
    for x in (-0.65, -0.22, 0.22, 0.65):
        D.rrect(x - 0.1, -0.3, x + 0.1, 0.65, 0.03)
    D.rrect(-0.98, 0.62, 0.98, 0.94, 0.05)
    D = mk(P, 's', 'gold', outline=0.015, bevel=0.03)
    D.star(0, -0.5, 5, 0.17, 0.08)


@icon
def staff(P):
    sh_person(mk(P, 'a', 'iron'), 0, 0.0, 0.85)
    D = mk(P, 'b', 'gold', outline=0.02)
    D.ell(0.38, 0.55, 0.28, 0.28)
    sh_star(mk(P, 'c', 'dark', outline=0, bevel=0.03), 0.38, 0.55, 0.17)


@icon
def facility_clubhouse(P):
    sh_house(mk(P, 'a', 'bronze'), 0, 0.1, 0.88)
    D = mk(P, 'f', 'cloth_red', outline=0.02)
    D.rect(0.5, -0.98, 0.56, -0.5)
    D.poly([(0.56, -0.98), (0.95, -0.82), (0.56, -0.65)])


@icon
def facility_scouting(P):
    D = mk(P, 'a', 'iron')
    D.rrect(-0.95, -0.45, -0.1, 0.9, 0.2)
    D.rrect(0.1, -0.45, 0.95, 0.9, 0.2)
    D.rect(-0.15, -0.1, 0.15, 0.2)
    D.rrect(-0.85, -0.7, -0.2, -0.35, 0.05)
    D.rrect(0.2, -0.7, 0.85, -0.35, 0.05)
    D = mk(P, 'l', 'sapphire', outline=0.02, bevel=0.1)
    D.circle(-0.52, 0.55, 0.28)
    D.circle(0.52, 0.55, 0.28)


@icon
def facility_barracks(P):
    D = mk(P, 'a', 'cloth_red')
    D.poly([(0, -0.95), (0.98, 0.9), (-0.98, 0.9)])
    D = mk(P, 'd', 'dark', outline=0.02, bevel=0.04)
    D.poly([(0, -0.05), (0.32, 0.9), (-0.32, 0.9)])
    D = mk(P, 'p', 'gold', outline=0.02)
    D.rect(-0.03, -1.0, 0.03, -0.65)


@icon
def facility_grounds(P):
    D = mk(P, 'a', 'iron')
    D.ell(0, 0, 0.98, 0.7)
    D = mk(P, 'g', 'green', outline=0.02)
    D.ell(0, 0.02, 0.8, 0.5)
    D = mk(P, 'l', 'white', outline=0.0, bevel=0.03, spec=0)
    D.path([(0, -0.46), (0, 0.5)], 0.07)
    D.ring(0, 0.02, 0.2, 0.07)


@icon
def shiny(P):
    D = mk(P, 'a', 'white')
    D.poly(catmull([(0, -1), (0.12, -0.12), (1, 0), (0.12, 0.12), (0, 1), (-0.12, 0.12), (-1, 0), (-0.12, -0.12)], 2, closed=True) if False else [(0, -1), (0.2, -0.2), (0.95, 0), (0.2, 0.2), (0, 1), (-0.2, 0.2), (-0.95, 0), (-0.2, -0.2)])
    D = mk(P, 'b', 'topaz', outline=0.02)
    D.poly([(0.62, -0.95), (0.7, -0.7), (0.95, -0.62), (0.7, -0.54), (0.62, -0.3), (0.54, -0.54), (0.3, -0.62), (0.54, -0.7)])
    D.poly([(-0.65, 0.5), (-0.58, 0.7), (-0.38, 0.77), (-0.58, 0.84), (-0.65, 1.0), (-0.72, 0.84), (-0.92, 0.77), (-0.72, 0.7)])


@icon
def legendary(P):
    D = mk(P, 'a', 'topaz')
    D.star(0, 0, 8, 0.98, 0.62, -90)
    sh_gem(mk(P, 'g', 'ruby', outline=0.02), 0, 0.02, 0.48)


@icon
def relic_slot(P):
    D = mk(P, 'a', 'iron')
    D.path([(0.0 + 0.9 * math.cos(math.radians(-90 + 60 * k)), 0.9 * math.sin(math.radians(-90 + 60 * k))) for k in range(6)], 0.2, closed=True)
    D = mk(P, 'b', 'amethyst', outline=0.02, bevel=0.05)
    gem_diamond(D, 0, 0, 0.3)


@icon
def chest(P):
    D = mk(P, 'a', 'wood')
    D.rrect(-0.92, 0.0, 0.92, 0.9, 0.08)
    D.poly(np.vstack([[(-0.92, 0.02)], Draw.arc_pts(0, 0.02, 0.92, 0.82, 180, 360, 20), [(0.92, 0.02)]]))
    D = mk(P, 'b', 'gold', outline=0.02)
    D.rect(-0.66, -0.75, -0.5, 0.9)
    D.rect(0.5, -0.75, 0.66, 0.9)
    D.rrect(-0.92, -0.04, 0.92, 0.1, 0.02)
    D.rrect(-0.18, -0.12, 0.18, 0.4, 0.06)
    D = mk(P, 'k', 'dark', outline=0.0, bevel=0.02)
    D.circle(0, 0.1, 0.06)


@icon
def coin_stack(P):
    for k in range(3):
        D = mk(P, 'c%d' % k, 'gold', bevel=0.06)
        y = 0.55 - k * 0.38
        D.rect(-0.7, y - 0.1, 0.7, y + 0.2)
        D.ell(0, y - 0.1, 0.7, 0.28)
        D.ell(0, y + 0.2, 0.7, 0.28)
    D = mk(P, 't', 'bronze', outline=0.0, bevel=0.04)
    D.ell(0, -0.62, 0.45, 0.14)


@icon
def ticket(P):
    D = mk(P, 'a', 'parch')
    D.rrect(-0.98, -0.55, 0.98, 0.55, 0.1)
    D.circle(-0.98, 0, 0.2, 0)
    D.circle(0.98, 0, 0.2, 0)
    sh_star(mk(P, 's', 'cloth_red', outline=0.02), -0.12, 0, 0.32)
    D = mk(P, 'd', 'dark', outline=0, bevel=0.03)
    for y in (-0.34, -0.12, 0.1, 0.32):
        D.rect(0.5, y, 0.7, y + 0.1)


@icon
def quest(P):
    D = mk(P, 'a', 'parch')
    D.rrect(-0.72, -0.75, 0.72, 0.75, 0.08)
    D = mk(P, 'r', 'bronze')
    D.rrect(-0.92, -0.92, 0.92, -0.58, 0.16)
    D.rrect(-0.92, 0.58, 0.92, 0.92, 0.16)
    D = mk(P, 'e', 'cloth_red', outline=0.02, bevel=0.04)
    D.rrect(-0.1, -0.4, 0.1, 0.18, 0.06)
    D.circle(0, 0.38, 0.12)


@icon
def achievement(P):
    medal_base(P, ('cloth_blue', 'cloth_red'))
    sh_star(mk(P, 'st', 'bronze', outline=0.0, bevel=0.05), 0, 0.3, 0.38)


@icon
def rebirth(P):
    D = mk(P, 'a', 'emerald')
    D.arc(0, 0, 0.7, 200, 340, 0.24)
    D.arc(0, 0, 0.7, 20, 160, 0.24)
    D.poly([(0.62, -0.62), (1.0, -0.3), (0.45, -0.18)])
    D.poly([(-0.62, 0.62), (-1.0, 0.3), (-0.45, 0.18)])
    sh_flame(mk(P, 'f', 'fire'), 0, 0.05, 0.38)


@icon
def ascend(P):
    sh_arrow_r(mk(P, 'a', 'ice'), 0, -0.2, 0.8, -90, w=0.6, hw=1.2, hl=0.95)
    sh_chevron(mk(P, 'b', 'ice'), 0, 0.72, 0.8, 0)


@icon
def shop_buy(P):
    D = mk(P, 'a', 'leather')
    D.poly(catmull([(-0.55, -0.35), (0.55, -0.35), (0.85, 0.3), (0.7, 0.9), (-0.7, 0.9), (-0.85, 0.3)], 6, closed=True))
    D.path(Draw.arc_pts(0, -0.35, 0.34, 0.3, 180, 360, 12), 0.13)
    sh_coin(mk(P, 'c', 'gold', outline=0.02), 0, 0.36, 0.3)
    sh_plus(mk(P, 'p', 'emerald', outline=0.025), 0.62, -0.62, 0.34, t=0.55)


@icon
def shop_sell(P):
    D = mk(P, 'a', 'leather')
    D.poly(catmull([(-0.55, -0.35), (0.55, -0.35), (0.85, 0.3), (0.7, 0.9), (-0.7, 0.9), (-0.85, 0.3)], 6, closed=True))
    D.path(Draw.arc_pts(0, -0.35, 0.34, 0.3, 180, 360, 12), 0.13)
    sh_coin(mk(P, 'c', 'gold', outline=0.02), 0, 0.36, 0.3)
    D = mk(P, 'm', 'ruby', outline=0.025)
    D.rrect(0.3, -0.7, 0.96, -0.54, 0.05)


@icon
def info(P):
    sh_coin(mk(P, 'a', 'sapphire'), 0, 0, 0.95)
    D = mk(P, 'b', 'white', outline=0.0, bevel=0.04, spec=0)
    D.circle(0, -0.45, 0.13)
    D.rrect(-0.11, -0.2, 0.11, 0.58, 0.05)


@icon
def warning(P):
    D = mk(P, 'a', 'topaz')
    D.poly(catmull([(0, -0.9), (0.98, 0.85), (-0.98, 0.85)], 1) if False else [(0, -0.92), (1.0, 0.82), (-1.0, 0.82)])
    D = mk(P, 'b', 'dark', outline=0.0, bevel=0.04, spec=0)
    D.rrect(-0.09, -0.3, 0.09, 0.32, 0.05)
    D.circle(0, 0.58, 0.1)


@icon
def message(P):
    sh_envelope(mk(P, 'a', 'parch'), 0, 0, 0.97)


@icon
def home(P):
    sh_house(mk(P, 'a', 'bronze'), 0, 0.02, 0.95)


NAMES = ['hp', 'mana', 'stamina', 'power', 'speed', 'defense', 'mres', 'gold', 'gem', 'star', 'crown', 'skull', 'heal', 'shield', 'injury', 'form_up',
         'form_down', 'form_flat', 'medal_iron_wall', 'medal_wrecking_hand', 'medal_clutch', 'medal_lifesaver', 'calendar', 'trophy', 'swords', 'flag',
         'lock', 'check', 'cross_close', 'settings', 'sound', 'gamepad', 'mouse', 'keyboard', 'search', 'filter', 'sort_asc', 'sort_desc', 'arrow_left',
         'arrow_right', 'play', 'pause', 'ff', 'camera', 'tactics', 'roster', 'market', 'club', 'league', 'cup', 'tower', 'gate', 'thunder', 'draft',
         'academy', 'training', 'hall', 'staff', 'facility_clubhouse', 'facility_scouting', 'facility_barracks', 'facility_grounds', 'shiny', 'legendary',
         'relic_slot', 'chest', 'coin_stack', 'ticket', 'quest', 'achievement', 'rebirth', 'ascend', 'shop_buy', 'shop_sell', 'info', 'warning', 'message', 'home']
FN = {'crown': 'crown_', 'filter': 'filter_'}


def render_icon(fn, S=48, ss=8, bevel=0.1, outline=0.055, shadow=0.05):
    P = Parts(S, S, ss)
    fn(P)
    cv = render_parts(P, bevel=bevel, outline=outline, shadow=shadow, spec=0.4)
    return finalize(cv, S, S)


def run():
    for n in NAMES:
        fn = ICONS[FN.get(n, n)]
        save(render_icon(fn), f'{OUT}/{n}.png')
    return NAMES


if __name__ == '__main__':
    print(len(run()))
