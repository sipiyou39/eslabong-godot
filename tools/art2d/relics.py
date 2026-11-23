"""Icones de reliques 96x96 (objet + fond teinte par rarete) et cadres de rarete."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from shapes import *

OUT = ASSETS + '/icons/relics'
SKIN = ASSETS + '/ui/skin'
S, SS = 96, 6
RAR = {'common': '#c9ced8', 'uncommon': '#6ad05a', 'rare': '#5aa0ff', 'epic': '#a06bff', 'legendary': '#ffb830'}
RAR_METAL = {'common': (hexc('#e4e8f0'), hexc('#4a5266')), 'uncommon': (hexc('#c4f0b4'), hexc('#2a6a30')), 'rare': (hexc('#cfe4ff'), hexc('#2a4a9a')),
             'epic': (hexc('#e8d4ff'), hexc('#4a2a8a')), 'legendary': (hexc('#fff0a8'), hexc('#a8620e'))}
R = {}


def rel(fn):
    R[fn.__name__[2:]] = fn
    return fn


def M(P, n, m, **k):
    return P.L(n, m, **k)


def cord(P, pts, w=0.035, mat='leather', n='cd'):
    M(P, n, mat, outline=0.025).path(pts, w)


@rel
def r_ApprenticesTome(P):
    M(P, 'pg', 'parch', outline=0.03).rrect(-0.46, -0.66, 0.6, 0.72, 0.06)
    M(P, 'cv', 'cloth_blue', outline=0.035).rrect(-0.6, -0.72, 0.5, 0.66, 0.08)
    M(P, 'sp', 'gold', outline=0.025).rect(-0.6, -0.72, -0.44, 0.66)
    sh_star(M(P, 'st', 'gold', outline=0.025), 0.0, -0.03, 0.25)
    for (x, y) in ((-0.45, -0.58), (0.38, -0.58), (-0.45, 0.52), (0.38, 0.52)):
        M(P, 'cn%d' % int(x * 10 + y * 3), 'gold', outline=0.015).circle(x + 0.05, y + 0.04, 0.045)


@rel
def r_ArcaneWhisper(P):
    sh_gem(M(P, 'gm', 'sapphire', outline=0.035), 0.0, 0.12, 0.42)
    for k, s in enumerate((-1, 1)):
        D = M(P, 'wh%d' % k, (hexc('#e0f0ff'), hexc('#5aa0ff')), outline=0.025)
        D.taper(bez([(s * 0.1, 0.0), (s * 0.55, -0.2), (s * 0.35, -0.55), (s * 0.12, -0.45)], 18), lambda t: 0.18 * (1 - t) ** 0.7 + 0.015)
    sh_star(M(P, 'sp', 'white', outline=0.02), 0.0, -0.62, 0.12)


@rel
def r_BriskAnklet(P):
    M(P, 'rg', 'leather', outline=0.035).path(Draw.arc_pts(0, 0.1, 0.5, 0.4, 0, 360, 40)[:-1], 0.17, closed=True)
    M(P, 'bk', 'gold', outline=0.03).rrect(-0.12, -0.38, 0.12, -0.2, 0.04)
    sh_wing(M(P, 'wg', 'white', outline=0.03), 0.3, -0.12, 0.8)


@rel
def r_BristleGuard(P):
    M(P, 'br', 'leather', outline=0.04).poly(catmull([(-0.55, -0.4), (0.55, -0.4), (0.62, 0.55), (-0.62, 0.55)], 4))
    D = M(P, 'sk', 'iron', outline=0.03)
    for k in range(5):
        x = -0.5 + k * 0.25
        D.poly([(x - 0.1, -0.4), (x, -0.72), (x + 0.1, -0.4)])
    M(P, 'bd', 'steel', outline=0.025).rrect(-0.6, 0.0, 0.6, 0.12, 0.03)
    M(P, 'bk', 'gold', outline=0.025).rrect(-0.1, -0.02, 0.1, 0.14, 0.03)


@rel
def r_BrokenHourglass(P):
    sh_hourglass(M(P, 'hg', 'gold', outline=0.035), 0, 0, 0.7)
    D = M(P, 'sn', (hexc('#ffe9a0'), hexc('#c08020')), outline=0.0)
    D.poly([(-0.34, -0.5), (0.34, -0.5), (0.06, -0.12), (-0.06, -0.12)])
    D.poly([(-0.4, 0.62), (0.4, 0.62), (0.2, 0.4), (-0.2, 0.4)])
    M(P, 'ck', 'black', outline=0.0, spec=0).path([(0.1, -0.7), (-0.05, -0.35), (0.12, -0.1), (-0.06, 0.25)], 0.05)


@rel
def r_BucklerSigil(P):
    M(P, 'sh', 'iron', outline=0.04, bevel=0.12).circle(0, 0, 0.66)
    M(P, 'sg', 'cloth_blue', outline=0.02).circle(0, 0, 0.5)
    sh_star(M(P, 'st', 'gold', outline=0.025), 0, 0, 0.3)
    for k in range(8):
        a = math.radians(45 * k)
        M(P, 'rv%d' % k, 'steel', outline=0.0, bevel=0.02).circle(0.58 * math.cos(a), 0.58 * math.sin(a), 0.035)


@rel
def r_CenteringStone(P):
    for k, (y, rx, ry, m) in enumerate(((0.45, 0.6, 0.22, 'iron'), (0.1, 0.46, 0.2, 'dark'), (-0.22, 0.32, 0.17, 'iron'))):
        M(P, 's%d' % k, m, outline=0.035, bevel=0.1).ell(0, y, rx, ry)
    M(P, 'rn', (hexc('#c0e0ff'), hexc('#5aa0ff')), outline=0.0, bevel=0.03).ring(0, -0.22, 0.09, 0.04)
    M(P, 'rg', (hexc('#c0e0ff'), hexc('#5aa0ff')), outline=0.0).circle(0, -0.22, 0.03)
    M(P, 'gl', 'ice', outline=0.0, spec=0).ell(0, -0.55, 0.12, 0.04)


@rel
def r_Cometspur(P):
    D = M(P, 'tl', (hexc('#c0f0ff'), hexc('#4a8aff')), outline=0.03)
    D.taper(bez([(0.2, -0.15), (-0.2, -0.45), (-0.55, -0.7), (-0.8, -0.8)], 14), lambda t: 0.34 * (1 - t) ** 0.8 + 0.01)
    sh_gear(M(P, 'sp', 'steel', outline=0.04), 0.2, 0.15, 0.55, n=9, ri=0.55, hole=0.22)
    M(P, 'hb', 'gold', outline=0.03).circle(0.2, 0.15, 0.1)


@rel
def r_DeepwellPendant(P):
    M(P, 'ch', 'gold', outline=0.03).path(Draw.arc_pts(0, -0.45, 0.45, 0.4, 20, 160, 20)[::-1] * np.array([1, -1]) * np.array([1, 1]) + np.array([0, 0]), 0.035) if False else M(P, 'ch', 'gold', outline=0.03).path(Draw.arc_pts(0, -0.2, 0.55, 0.6, 200, 340, 24), 0.04)
    sh_drop(M(P, 'bz', 'gold', outline=0.035), 0, 0.28, 0.46, 180)
    sh_drop(M(P, 'gm', 'sapphire', outline=0.02), 0, 0.3, 0.34, 180)
    M(P, 'gl', 'white', outline=0.0, spec=0).ell(-0.08, 0.2, 0.05, 0.11)


@rel
def r_EmberFlask(P):
    sh_flask(M(P, 'fl', 'glass', outline=0.035), 0, 0.05, 0.72)
    D = M(P, 'lq', 'fire', outline=0.0)
    D.poly(catmull([(-0.52, 0.2), (-0.15, 0.1), (0.15, 0.2), (0.52, 0.2), (0.6, 0.55), (0.45, 0.7), (-0.45, 0.7), (-0.6, 0.55)], 4))
    M(P, 'ck', 'wood', outline=0.03).rrect(-0.15, -0.82, 0.15, -0.56, 0.04)
    sh_flame(M(P, 'fm', 'fire', outline=0.025), 0, -0.05, 0.22)


@rel
def r_EnduringGirdle(P):
    M(P, 'bt', 'leather', outline=0.04).rrect(-0.85, -0.2, 0.85, 0.22, 0.06)
    for k in range(6):
        if abs(-0.7 + k * 0.28) < 0.2:
            continue
        M(P, 'st%d' % k, 'gold', outline=0.0, bevel=0.02).circle(-0.7 + k * 0.28, 0.01, 0.04)
    M(P, 'bk', 'gold', outline=0.035).rrect(-0.28, -0.34, 0.28, 0.36, 0.08)
    M(P, 'bi', 'dark', outline=0.02).rrect(-0.16, -0.22, 0.16, 0.24, 0.05)
    sh_gem(M(P, 'gm', 'ruby', outline=0.02), 0, 0.01, 0.1)


@rel
def r_FeatherstepCharm(P):
    cord(P, Draw.arc_pts(0, -0.2, 0.5, 0.55, 190, 350, 20), 0.04, n='cd')
    M(P, 'bd', 'gold', outline=0.02).circle(0, -0.74, 0.07) if False else None
    D = M(P, 'ft', 'white', outline=0.03)
    D.taper(bez([(-0.2, 0.7), (-0.05, 0.2), (0.15, -0.1), (0.08, -0.5)], 18), lambda t: 0.34 * math.sin(PI_ * min(t * 1.05, 1)) ** 0.7 + 0.02)
    M(P, 'sp', 'steel', outline=0.0).line(-0.2, 0.7, 0.08, -0.5, 0.025)
    M(P, 'bd2', 'gold', outline=0.025).circle(-0.2, 0.62, 0.08)


PI_ = math.pi


@rel
def r_FletchersPin(P):
    D = M(P, 'sh', 'steel', outline=0.03)
    with D.at(0, 0, -45):
        D.rrect(-0.7, -0.03, 0.55, 0.03, 0.02)
    with M(P, 'hd', 'steel', outline=0.03).at(0, 0, -45) as D:
        D.poly([(0.5, -0.12), (0.8, 0), (0.5, 0.12)])
    with M(P, 'ft', 'cloth_red', outline=0.03).at(0, 0, -45) as D:
        for s in (-1, 1):
            D.poly([(-0.72, 0), (-0.5, s * 0.22), (-0.2, s * 0.22), (-0.35, 0)])
    M(P, 'gm', 'gold', outline=0.025).circle(-0.5, 0.5, 0.1)


@rel
def r_GhostglassWard(P):
    M(P, 'rg', 'iron', outline=0.04).ring(0, 0, 0.58, 0.14)
    M(P, 'gl', (hexc('#e8f6ff'), hexc('#8ab8e0')), outline=0.0, bevel=0.2).circle(0, 0, 0.5)
    D = M(P, 'gh', 'white', outline=0.02)
    D.poly(catmull([(-0.28, 0.34), (-0.3, -0.12), (-0.15, -0.34), (0.15, -0.34), (0.3, -0.12), (0.28, 0.34), (0.14, 0.2), (0, 0.34), (-0.14, 0.2)], 6, closed=True))
    M(P, 'ey', 'dark', outline=0.0, spec=0).circle(-0.1, -0.1, 0.05)
    M(P, 'ey2', 'dark', outline=0.0, spec=0).circle(0.1, -0.1, 0.05)
    M(P, 'hl', 'white', outline=0.0, spec=0).ell(-0.28, -0.38, 0.1, 0.04, -40)


@rel
def r_GlassComet(P):
    D = M(P, 'tl', (hexc('#e0f6ff'), hexc('#6ab8ff')), outline=0.03)
    D.taper(bez([(0.2, -0.2), (-0.15, -0.45), (-0.5, -0.65), (-0.85, -0.7)], 14), lambda t: 0.36 * (1 - t) ** 0.8 + 0.01)
    D = M(P, 'cm', 'glass', outline=0.035)
    D.poly([(0.0, -0.25), (0.28, -0.35), (0.58, -0.05), (0.5, 0.35), (0.15, 0.55), (-0.15, 0.3), (-0.12, -0.05)])
    M(P, 'ht', 'white', outline=0.0, spec=0).poly([(0.05, -0.15), (0.22, -0.22), (0.1, 0.05)])


@rel
def r_HealersThimble(P):
    M(P, 'th', 'steel', outline=0.04, bevel=0.1).poly(catmull([(-0.5, 0.6), (-0.48, -0.1), (-0.3, -0.5), (0.3, -0.5), (0.48, -0.1), (0.5, 0.6)], 6))
    M(P, 'rm', 'iron', outline=0.03).rrect(-0.6, 0.5, 0.6, 0.72, 0.05)
    sh_plus(M(P, 'pl', 'emerald', outline=0.025), 0, 0.02, 0.26, 0, t=0.5)
    D = M(P, 'dt', 'iron', outline=0.0, bevel=0.015, spec=0)
    for (x, y) in ((-0.28, -0.3), (0.0, -0.38), (0.28, -0.3), (-0.4, 0.2), (0.4, 0.2)):
        D.circle(x, y, 0.035)


@rel
def r_IronLung(P):
    for s in (-1, 1):
        M(P, 'lg%d' % s, 'iron', outline=0.04, bevel=0.1).poly(catmull([(s * 0.08, -0.35), (s * 0.55, -0.1), (s * 0.7, 0.4), (s * 0.4, 0.62), (s * 0.12, 0.45)], 6, closed=True))
    M(P, 'tb', 'steel', outline=0.035).rrect(-0.07, -0.72, 0.07, -0.05, 0.03)
    M(P, 'tb2', 'steel', outline=0.03).path([(0, -0.1), (-0.3, 0.0)], 0.06)
    M(P, 'tb3', 'steel', outline=0.03).path([(0, -0.1), (0.3, 0.0)], 0.06)
    for s in (-1, 1):
        for k, y in enumerate((0.1, 0.3)):
            M(P, 'rv%d%d' % (s, k), 'gold', outline=0.0, bevel=0.015).circle(s * 0.38, y, 0.035)


@rel
def r_LastingStitch(P):
    M(P, 'pt', 'cloth_red', outline=0.035).rrect(-0.6, -0.5, 0.6, 0.5, 0.05)
    D = M(P, 'ss', 'bone', outline=0.0, bevel=0.015, spec=0)
    for k in range(7):
        D.rrect(-0.5 + k * 0.155, -0.46, -0.5 + k * 0.155 + 0.09, -0.42, 0.01)
        D.rrect(-0.5 + k * 0.155, 0.42, -0.5 + k * 0.155 + 0.09, 0.46, 0.01)
    with M(P, 'nd', 'steel', outline=0.03).at(0, 0, -50) as D:
        D.rrect(-0.55, -0.025, 0.5, 0.025, 0.02)
        D.ell(-0.45, 0, 0.05, 0.03, 0)
    M(P, 'th', 'bone', outline=0.02).path(catmull([(-0.3, 0.3), (-0.1, 0.1), (0.1, 0.28), (0.3, 0.05)], 8), 0.035)


@rel
def r_LongshotLocket(P):
    M(P, 'ch', 'gold', outline=0.025).path(Draw.arc_pts(0, -0.45, 0.35, 0.45, 200, 340, 18), 0.035)
    M(P, 'lk', 'gold', outline=0.04, bevel=0.1).ell(0, 0.18, 0.46, 0.55)
    M(P, 'in', 'cloth_blue', outline=0.02).ell(0, 0.18, 0.36, 0.45)
    sword  # noqa
    D = M(P, 'ar', 'bone', outline=0.0, bevel=0.015, spec=0)
    with D.at(0, 0.18, -40):
        D.rrect(-0.28, -0.025, 0.22, 0.025, 0.02)
        D.poly([(0.2, -0.09), (0.34, 0), (0.2, 0.09)])


@rel
def r_MendersPin(P):
    D = M(P, 'pn', 'gold', outline=0.035)
    D.ell(0, -0.2, 0.36, 0.36)
    D.poly([(-0.3, 0.1), (0.3, 0.1), (0.0, 0.75)])
    sh_plus(M(P, 'pl', 'emerald', outline=0.025), 0, -0.2, 0.2, 0, t=0.55)
    M(P, 'ph', 'steel', outline=0.0).rrect(-0.03, 0.2, 0.03, 0.62, 0.02)


@rel
def r_MercyBand(P):
    M(P, 'rg', 'gold', outline=0.04, bevel=0.1).path(Draw.arc_pts(0, 0.1, 0.55, 0.5, 0, 360, 44)[:-1], 0.22, closed=True)
    sh_heart(M(P, 'ht', 'blood', outline=0.03), 0, -0.52, 0.22)
    M(P, 'gl', 'white', outline=0.0, spec=0).ell(-0.08, -0.6, 0.05, 0.035)


@rel
def r_MessisFarewellLetter(P):
    M(P, 'ev', 'parch', outline=0.04).rrect(-0.7, -0.5, 0.7, 0.5, 0.05)
    M(P, 'fl', (hexc('#e8d8a8'), hexc('#a89060')), outline=0.025).poly([(-0.7, -0.5), (0.7, -0.5), (0.0, 0.1)])
    sh_coin(M(P, 'sl', 'ruby', outline=0.03), 0, 0.08, 0.2)
    sh_star(M(P, 'st', (hexc('#ffb0b8'), hexc('#a0102a')), outline=0.0, spec=0), 0, 0.08, 0.11)
    M(P, 'rb', 'cloth_blue', outline=0.0).path([(-0.55, 0.38), (0.55, 0.38)], 0.04)


@rel
def r_RedhideWrap(P):
    for k in range(4):
        M(P, 'ws%d' % k, (hexc('#e0605a'), hexc('#7a1a1a')) if k % 2 == 0 else (hexc('#c04a40'), hexc('#5a1010')), outline=0.035).poly([(-0.62, -0.62 + k * 0.32), (0.62, -0.38 + k * 0.32), (0.62, -0.1 + k * 0.32), (-0.62, -0.34 + k * 0.32)])
    M(P, 'tr', 'bone', outline=0.02).path([(-0.55, -0.55), (-0.55, 0.65)], 0.03)
    M(P, 'tr2', 'bone', outline=0.02).circle(-0.55, 0.65, 0.05)


def boot(P, x=0.0, y=0.0, s=1.0, mat='leather', tag='bt'):
    D = M(P, tag, mat, outline=0.04, bevel=0.1)
    with D.at(x, y, 0, s):
        D.poly(catmull([(-0.35, -0.75), (0.2, -0.75), (0.25, 0.0), (0.7, 0.3), (0.78, 0.6), (-0.4, 0.6)], 5))
    M(P, tag + 's', 'dark', outline=0.03).rrect(x - 0.4 * s, y + 0.52 * s, x + 0.82 * s, y + 0.72 * s, 0.05)
    M(P, tag + 'c', 'cloth_red', outline=0.025).rrect(x - 0.37 * s, y - 0.8 * s, x + 0.22 * s, y - 0.62 * s, 0.04)


@rel
def r_SafeStep(P):
    boot(P, -0.05, -0.05, 0.9)
    sh_shield(M(P, 'sd', 'steel', outline=0.03), 0.5, -0.45, 0.28)
    sh_check(M(P, 'ck', 'emerald', outline=0.0), 0.5, -0.45, 0.14, w=0.35)


@rel
def r_SteadyFooting(P):
    boot(P, -0.15, -0.15, 0.85)
    M(P, 'rk', 'iron', outline=0.04, bevel=0.12).poly(catmull([(-0.75, 0.75), (-0.55, 0.62), (0.4, 0.62), (0.75, 0.75), (0.7, 0.85), (-0.7, 0.85)], 4))


@rel
def r_SunlitCharm(P):
    sh_sun(M(P, 'sn', 'gold', outline=0.035), 0, 0, 0.82, 0, rays=12)
    M(P, 'fc', 'topaz', outline=0.035, bevel=0.2).circle(0, 0, 0.42)
    M(P, 'hl', 'white', outline=0.0, spec=0).ell(-0.14, -0.14, 0.12, 0.07, -40)


@rel
def r_SwiftSole(P):
    D = M(P, 'sl', 'leather', outline=0.04, bevel=0.1)
    D.poly(catmull([(-0.55, 0.3), (0.55, 0.0), (0.8, 0.1), (0.8, 0.35), (-0.45, 0.55)], 4))
    sh_wing(M(P, 'wg', 'white', outline=0.03), -0.05, -0.05, 0.85)
    M(P, 'st', 'gold', outline=0.02).path([(-0.3, 0.38), (0.6, 0.18)], 0.04)


@rel
def r_TinLocket(P):
    M(P, 'rg', 'iron', outline=0.03).ring(0, -0.62, 0.1, 0.05)
    M(P, 'lk', 'iron', outline=0.04, bevel=0.14).circle(0, 0.1, 0.55)
    M(P, 'ft', 'steel', outline=0.03, bevel=0.1).circle(0, 0.1, 0.4)
    M(P, 'cl', 'steel', outline=0.025).rrect(-0.06, -0.52, 0.06, -0.3, 0.02)
    sh_star(M(P, 'st', 'iron', outline=0.0, spec=0.1), 0, 0.1, 0.2)


@rel
def r_VanguardCrest(P):
    sh_shield(M(P, 'sh', 'gold', outline=0.04), 0, 0.05, 0.78)
    sh_shield(M(P, 'in', 'cloth_red', outline=0.025), 0, 0.07, 0.62)
    D = M(P, 'cv', 'gold', outline=0.02)
    for y in (0.0, 0.26):
        D.path([(-0.3, y + 0.2), (0, y - 0.05), (0.3, y + 0.2)], 0.1)
    sh_wing(M(P, 'wl', 'white', outline=0.03), -0.6, -0.5, 0.45, 0) if False else None


@rel
def r_VitalSip(P):
    sh_flask(M(P, 'fl', 'glass', outline=0.035), 0, 0.1, 0.6)
    D = M(P, 'lq', 'blood', outline=0.0)
    D.poly(catmull([(-0.44, 0.35), (-0.1, 0.3), (0.1, 0.4), (0.44, 0.35), (0.5, 0.62), (0.4, 0.7), (-0.4, 0.7), (-0.5, 0.62)], 4))
    M(P, 'ck', 'wood', outline=0.03).rrect(-0.12, -0.68, 0.12, -0.46, 0.04)
    sh_heart(M(P, 'ht', 'white', outline=0.0, spec=0), 0, 0.5, 0.12)


@rel
def r_WarmBandage(P):
    M(P, 'rl', 'parch', outline=0.04, bevel=0.12).rrect(-0.55, -0.45, 0.55, 0.55, 0.12)
    for y in (-0.2, 0.05, 0.3):
        M(P, 'ln%d' % int(y * 10), (hexc('#d8c898'), hexc('#a89060')), outline=0.0, spec=0).rrect(-0.55, y, 0.55, y + 0.05, 0.02)
    M(P, 'tl', 'parch', outline=0.03).poly([(0.1, -0.45), (0.55, -0.45), (0.8, -0.7), (0.62, -0.78), (0.3, -0.62)])
    sh_flame(M(P, 'fl', 'fire', outline=0.025), 0, -0.05, 0.2)


@rel
def r_WellspringSigil(P):
    M(P, 'rg', 'iron', outline=0.04).circle(0, 0, 0.7)
    M(P, 'dk', 'sapphire', outline=0.02, bevel=0.2).circle(0, 0, 0.56)
    sh_drop(M(P, 'dr', 'white', outline=0.025), 0, 0.0, 0.3)
    M(P, 'rp', 'ice', outline=0.0, bevel=0.02).ring(0, 0, 0.45, 0.04)
    D = M(P, 'ds', 'ice', outline=0.0, bevel=0.02)
    for k in range(6):
        a = math.radians(60 * k)
        D.circle(0.62 * math.cos(a), 0.62 * math.sin(a), 0.035)


@rel
def r_WhettedFang(P):
    D = M(P, 'fg', 'bone', outline=0.04)
    D.taper(bez([(-0.35, -0.7), (0.15, -0.55), (0.35, 0.0), (0.12, 0.75)], 22), lambda t: 0.5 * (1 - t) ** 0.75 + 0.01)
    M(P, 'ed', 'white', outline=0.0, spec=0).taper(bez([(-0.15, -0.6), (0.2, -0.45), (0.28, 0.0), (0.1, 0.65)], 18), lambda t: 0.05 * (1 - t) + 0.005)
    sh_star(M(P, 'sp', 'topaz', outline=0.02), 0.5, 0.45, 0.14)
    sh_star(M(P, 'sp2', 'topaz', outline=0.02), 0.62, 0.15, 0.08)


@rel
def r_WomboCombo(P):
    sh_star(M(P, 's1', 'topaz', outline=0.035), -0.2, 0.0, 0.55, 12)
    sh_star(M(P, 's2', 'ruby', outline=0.035), 0.25, 0.0, 0.45, -8)
    M(P, 'rg', 'gold', outline=0.03).ring(0.0, 0.0, 0.72, 0.06)
    sh_star(M(P, 'sp', 'white', outline=0.0, spec=0), 0.02, 0.0, 0.18)


@rel
def r_MirrorbreakerGlove(P):
    sh_fist(M(P, 'gv', 'iron', outline=0.04), -0.1, 0.1, 0.6)
    D = M(P, 'sh', 'glass', outline=0.03)
    D.poly([(0.45, -0.75), (0.75, -0.55), (0.6, -0.3)])
    D.poly([(0.55, -0.1), (0.85, 0.05), (0.7, 0.25)])
    D.poly([(0.3, -0.45), (0.45, -0.15), (0.2, -0.2)])
    M(P, 'cf', 'gold', outline=0.03).rrect(-0.55, 0.62, 0.35, 0.82, 0.04)


@rel
def r_SecondString(P):
    D = M(P, 'bw', 'wood', outline=0.04)
    D.taper(bez([(0.0, -0.78), (0.65, -0.35), (0.65, 0.35), (0.0, 0.78)], 28), lambda t: 0.16 * math.sin(math.pi * t) ** 0.5 + 0.04)
    M(P, 's1', 'bone', outline=0.015).line(0.0, -0.78, 0.0, 0.78, 0.03)
    M(P, 's2', 'cloth_red', outline=0.015).path([(0.0, -0.78), (-0.2, 0.0), (0.0, 0.78)], 0.035)
    M(P, 'gr', 'leather', outline=0.03).rrect(0.5, -0.12, 0.7, 0.12, 0.04)


@rel
def r_SiegeBell(P):
    M(P, 'fr', 'wood', outline=0.04).rrect(-0.8, -0.78, 0.8, -0.62, 0.03)
    sh_bell(M(P, 'bl', 'gold', outline=0.04), 0, 0.05, 0.62)
    M(P, 'cb', 'iron', outline=0.03).path([(0, -0.7), (0, -0.52)], 0.05)
    M(P, 'cl', 'dark', outline=0.03).circle(0, 0.72, 0.1)


@rel
def r_WindCharm(P):
    cord(P, Draw.arc_pts(0, -0.1, 0.52, 0.6, 195, 345, 20), 0.04)
    D = M(P, 'sw', (hexc('#e0fff4'), hexc('#4ad8b0')), outline=0.03)
    for k in range(3):
        with D.at(0, 0.12, k * 120):
            D.taper(arc_pts(0, 0, 0.3, -30, 110), lambda t: 0.2 * math.sin(math.pi * t) ** 0.8 + 0.01)
    M(P, 'bd', 'gold', outline=0.025).circle(0, 0.12, 0.09)
    M(P, 'ft', 'white', outline=0.025).taper([(0.2, 0.55), (0.45, 0.78)], lambda t: 0.2 * (1 - t) + 0.01) if False else None


def arc_pts(cx, cy, r, a0, a1):
    return Draw.arc_pts(cx, cy, r, r, a0, a1, 30)


def backdrop(rar):
    N = S * SS
    base = hexc(RAR[rar])
    sd = sdf_rrect(N, N, 4 * SS, 4 * SS, N - 4 * SS, N - 4 * SS, 12 * SS)
    a = cov(sd)
    yy, xx = grid(N, N)
    r = np.hypot((xx - N / 2) / (N / 2), (yy - N * 0.46) / (N / 2))
    col = radial(N, N, N / 2, N * 0.46, N * 0.72, mix(base, NAVY, 0.62), mix(base, NAVY, 0.93), 0.9)
    img = blank(N)
    put(img, a, col)
    put(img, np.clip(1 - (-sd) / (9 * SS), 0, 1) ** 2 * a, [0, 0, 0], 0.45)
    return img


def frame(rar):
    N = S * SS
    P = Parts(S, S, SS)
    hi, lo = RAR_METAL[rar]
    ring = P.L('rg', (hi, lo), outline=0.02, bevel=0.06, spec=0.55)
    ring.rrect(-0.97, -0.97, 0.97, 0.97, 0.26)
    ring.rrect(-0.84, -0.84, 0.84, 0.84, 0.17, 0)
    b = hexc(RAR[rar])
    li = P.L('li', (lighten(b, 0.6), b), outline=0.0, bevel=0.012, spec=0.2)
    li.path([(-0.82, -0.7), (-0.7, -0.82), (0.7, -0.82), (0.82, -0.7), (0.82, 0.7), (0.7, 0.82), (-0.7, 0.82), (-0.82, 0.7)], 0.02, closed=True)
    if rar in ('uncommon', 'rare', 'epic', 'legendary'):
        g = P.L('gm', (lighten(b, 0.6), darken(b, 0.5)), outline=0.02, bevel=0.04, spec=0.9)
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.circle(sx * 0.84, sy * 0.84, 0.075)
    if rar in ('epic', 'legendary'):
        f = P.L('fn', MAT['gold'] if rar == 'legendary' else (hi, lo), outline=0.022, bevel=0.03, spec=0.6)
        for k in range(4):
            with f.at(0, 0, 90 * k):
                f.poly([(-0.09, -0.96), (0, -1.0), (0.09, -0.96), (0.0, -0.84)])
    cv = render_parts(P, bevel=0.06, outline=0.02, spec=0.5)
    if rar == 'legendary':
        m = P.layers['rg'][0].mask()
        glow(cv, blur(m, 3 * SS) * 0.6, hexc('#ffb830'), 0.55)
    return cv


def render_relic(rl):
    key, rar = rl['key'], rl['rarity']
    P = Parts(S, S, SS)
    R[key](SubParts(P, 0, -0.02, 0.9))
    N = S * SS
    cv = backdrop(rar)
    u = P.union()
    glow(cv, blur(u, 5 * SS) * cov(sdf_rrect(N, N, 6 * SS, 6 * SS, N - 6 * SS, N - 6 * SS, 10 * SS)), hexc(RAR[rar]), 0.5)
    ob = render_parts(P, bevel=0.06, outline=0.03, shadow=0.03, spec=0.45)
    over(cv, ob)
    return finalize(cv, S, S)


def run():
    rl = json.load(open(ROOT + '/data/relics.json'))
    byk = {r['key']: r for r in rl['relics']}
    n = 0
    for key in rl['names']:
        r = byk.get(key) or {'key': key, 'rarity': 'common'}
        save(render_relic(r), f'{OUT}/{key}.png')
        n += 1
    for rar in RAR:
        save(finalize(frame(rar), S, S), f'{SKIN}/rarity_{rar}.png')
    # manifest ui
    mp = SKIN + '/ui_manifest.json'
    cur = json.load(open(mp)) if os.path.exists(mp) else {}
    for rar in RAR:
        cur[f'rarity_{rar}.png'] = {'margins': [0, 0, 0, 0], 'size': [96, 96], 'note': f'cadre de rareté {rar} pour icône de relique (centre transparent)'}
    json.dump(dict(sorted(cur.items())), open(mp, 'w'), indent=1, ensure_ascii=False)
    return n


if __name__ == '__main__':
    print(run())
