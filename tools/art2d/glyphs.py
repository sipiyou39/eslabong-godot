"""Glyphes d'archetype pour les icones de competences. Coordonnees normalisees (-1..1), contenu dans ~ +-0.62.
Signature : g_<nom>(P, M, rs, v, e) ; M = materiaux d'element (core/light/mid/dark), rs = RandomState(id), v = variante, e = element."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from shapes import *

PI = math.pi
NV = {}   # nombre de variantes par glyphe


def glyph(nv):
    def deco(fn):
        fn.nv = nv
        NV[fn.__name__[2:]] = nv
        return fn
    return deco


def arcp(cx, cy, r, a0, a1, n=40):
    return Draw.arc_pts(cx, cy, r, r, a0, a1, n)


def arc_taper(D, cx, cy, r, a0, a1, w, n=40, pw=0.85):
    D.taper(arcp(cx, cy, r, a0, a1, n), lambda t: w * math.sin(PI * t) ** pw + 0.002)


def streak(D, p0, p1, w, n=14, pw=1.0):
    pts = np.linspace(p0, p1, n)
    D.taper(pts, lambda t: w * (1 - t) ** pw + 0.002)


def spark4(D, x, y, r, v=255):
    D.star(x, y, 4, r, r * 0.28, -90, v)


def orb(P, M, tag, x, y, r):
    P.L(tag + 'o1', M['mid'], outline=0.03, bevel=r * 0.9).circle(x, y, r)
    P.L(tag + 'o2', M['core'], outline=0.0, bevel=r * 0.6).circle(x, y, r * 0.58)


def rock_poly(rs, r, n=11, jit=0.22):
    a = np.linspace(0, 2 * PI, n, endpoint=False) + rs.uniform(-0.1, 0.1, n)
    rr = r * (1 + rs.uniform(-jit, jit, n))
    return np.stack([rr * np.cos(a), rr * np.sin(a)], 1)


def arrow(P, M, tag, x, y, rot, L=1.0, w=0.035, head=0.22):
    with P.L(tag + 's', 'wood', outline=0.03).at(x, y, rot) as D:
        D.rrect(0, -w, L - head * 0.5, w, w * 0.5)
    with P.L(tag + 'f', M['light'], outline=0.03).at(x, y, rot) as D:
        for s in (-1, 1):
            D.poly([(-0.02, 0), (0.1, s * 0.13), (0.28, s * 0.13), (0.2, 0)])
    with P.L(tag + 'h', 'steel', outline=0.03).at(x, y, rot) as D:
        D.poly([(L - head, -head * 0.5), (L, 0), (L - head, head * 0.5), (L - head * 0.7, 0)])


# ------------------------------------------------------------------ melee
@glyph(5)
def g_slash(P, M, rs, v, e):
    if v == 0:
        arc_taper(P.L('c1', M['light']), 0, 0.5, 0.78, 200, 340, 0.36)
        arc_taper(P.L('c2', M['mid'], outline=0.02), 0, 0.56, 0.58, 215, 325, 0.13)
        arc_taper(P.L('c3', M['core'], outline=0.0), 0, 0.5, 0.78, 215, 325, 0.1)
        spark4(P.L('s1', M['core'], outline=0.02), 0.62, 0.18, 0.12)
    elif v == 1:
        arc_taper(P.L('c1', M['light']), 0.1, 0.35, 0.72, 175, 300, 0.3)
        sword(P, -0.58, 0.6, -45, L=1.35, w=0.17, guard_w=0.24, tag='sw')
    elif v == 2:
        for k, (a, mt) in enumerate(((45, 'light'), (-45, 'core'))):
            D = P.L('x%d' % k, M[mt], outline=0.03)
            with D.at(0, 0.0, a):
                arc_taper(D, 0, 0.75, 0.85, 235, 305, 0.28)
    elif v == 3:
        for i in (-1, 0, 1):
            D = P.L('cl%d' % i, M['light'] if i else M['core'], outline=0.03)
            o = i * 0.3
            D.taper(bez([(-0.5 + o, -0.62), (-0.18 + o, -0.1), (0.05 + o * 0.7, 0.3), (0.28 + o * 0.5, 0.62)], 20), lambda t: 0.2 * math.sin(PI * min(t * 1.2, 1)) ** 0.7 * (1 - t) + 0.01)
    else:
        for sgn in (-1, 1):
            D = P.L('pa%d' % sgn, M['light'] if sgn > 0 else M['mid'], outline=0.03)
            arc_taper(D, sgn * -0.72, 0, 0.78, -52 if sgn > 0 else 128, 52 if sgn > 0 else 232, 0.3)
        spark4(P.L('s1', M['core'], outline=0.02), 0, 0, 0.17)


@glyph(3)
def g_thrust(P, M, rs, v, e):
    if v == 0:
        for i, o in enumerate((-0.22, 0.0, 0.22)):
            D = P.L('st%d' % i, M['light'] if i != 1 else M['core'], outline=0.02)
            with D.at(0, 0, -45):
                streak(D, (0.6, o), (-0.75, o), 0.07 if i != 1 else 0.05)
        with P.L('sh', 'wood', outline=0.04).at(0, 0, -45) as D:
            D.rrect(-0.55, -0.04, 0.4, 0.04, 0.02)
        with P.L('hd', 'steel', outline=0.04).at(0, 0, -45) as D:
            D.poly([(0.36, 0), (0.5, -0.14), (0.9, 0), (0.5, 0.14)])
        with P.L('co', 'gold', outline=0.03).at(0, 0, -45) as D:
            D.rrect(0.3, -0.09, 0.38, 0.09, 0.02)
    elif v == 1:
        for i, o in enumerate((-0.2, 0.2)):
            D = P.L('st%d' % i, M['light'], outline=0.02)
            with D.at(0, 0, -45):
                streak(D, (0.3, o), (-0.8, o), 0.06)
        sword(P, -0.62, 0.62, -45, L=1.5, w=0.12, guard_w=0.22, tag='sw')
    else:
        D = P.L('b', M['mid'])
        with D.at(0, 0, -45):
            D.poly([(-0.7, 0), (-0.3, -0.13), (0.55, 0), (-0.3, 0.13)])
        D = P.L('c', M['core'], outline=0.0)
        with D.at(0, 0, -45):
            D.poly([(-0.5, 0), (-0.25, -0.05), (0.55, 0), (-0.25, 0.05)])
        for k in range(5):
            a = math.radians(-45 + (k - 2) * 28)
            P.L('r%d' % k, M['light'], outline=0.02).taper([(0.4 + 0.1 * math.cos(a), -0.4 + 0.1 * math.sin(a)), (0.4 + 0.42 * math.cos(a), -0.4 + 0.42 * math.sin(a))], lambda t: 0.08 * (1 - t))
        spark4(P.L('sp', M['core'], outline=0.02), 0.42, -0.42, 0.2)


@glyph(3)
def g_whirl(P, M, rs, v, e):
    if v == 0:
        for k in range(3):
            D = P.L('b%d' % k, 'steel', outline=0.035)
            with D.at(0, 0, k * 120):
                arc_taper(D, 0, 0, 0.46, -40, 115, 0.3)
            D2 = P.L('o%d' % k, M['mid'], outline=0.02)
            with D2.at(0, 0, k * 120 + 20):
                arc_taper(D2, 0, 0, 0.72, 0, 90, 0.09)
        orb(P, M, 'h', 0, 0, 0.14)
    elif v == 1:
        for k in range(4):
            D = P.L('b%d' % k, M['light'] if k % 2 == 0 else M['mid'], outline=0.03)
            with D.at(0, 0, k * 90):
                arc_taper(D, 0, 0, 0.5, -10, 80, 0.26)
        orb(P, M, 'h', 0, 0, 0.17)
    else:
        t = np.linspace(0, 1, 60)
        a = 2 * PI * 1.75 * t - PI / 2
        r = 0.12 + 0.52 * t
        pts = np.stack([r * np.cos(a), r * np.sin(a)], 1)
        P.L('sp', M['light'], outline=0.03).taper(pts, lambda u: 0.04 + 0.2 * u)
        D = P.L('ah', M['core'], outline=0.03)
        a1 = a[-1]
        D.poly([(0.64 * math.cos(a1) + 0.16 * math.cos(a1 + 1.57), 0.64 * math.sin(a1) + 0.16 * math.sin(a1 + 1.57)), (0.64 * math.cos(a1 + 0.5) , 0.64 * math.sin(a1 + 0.5)) , (0.64 * math.cos(a1) - 0.16 * math.cos(a1 + 1.57), 0.64 * math.sin(a1) - 0.16 * math.sin(a1 + 1.57))])
        orb(P, M, 'h', 0, 0, 0.13)


@glyph(3)
def g_burst(P, M, rs, v, e):
    if v == 0:
        D = P.L('sp', M['mid'], outline=0.03)
        n = 12
        pts = []
        for i in range(2 * n):
            r = (0.7 if (i // 2) % 2 == 0 else 0.5) if i % 2 == 0 else 0.26
            a = PI * i / n - PI / 2
            pts.append((r * math.cos(a), r * math.sin(a)))
        D.poly(pts)
        P.L('rg', M['light'], outline=0.03).ring(0, 0, 0.3, 0.09)
        orb(P, M, 'c', 0, 0, 0.19)
    elif v == 1:
        P.L('r1', M['mid'], outline=0.03).ring(0, 0, 0.62, 0.09)
        P.L('r2', M['light'], outline=0.03).ring(0, 0, 0.4, 0.1)
        D = P.L('sp', M['light'], outline=0.03)
        for k in range(8):
            with D.at(0, 0, k * 45):
                D.poly([(0.66, -0.07), (0.88 if k % 2 == 0 else 0.78, 0), (0.66, 0.07)])
        orb(P, M, 'c', 0, 0, 0.2)
    else:
        n = 22
        a = np.linspace(0, 2 * PI, n, endpoint=False)
        rr = np.where(np.arange(n) % 2 == 0, rs.uniform(0.58, 0.72, n), rs.uniform(0.34, 0.44, n))
        P.L('sp', M['mid'], outline=0.03).poly(np.stack([rr * np.cos(a), rr * np.sin(a)], 1))
        P.L('in', M['light'], outline=0.0).poly(np.stack([rr * 0.62 * np.cos(a + 0.1), rr * 0.62 * np.sin(a + 0.1)], 1))
        orb(P, M, 'c', 0, 0, 0.17)


# ------------------------------------------------------------------ projectiles / zones
@glyph(5)
def g_bolt(P, M, rs, v, e):
    if v == 0:
        for k, (o, w) in enumerate(((0.0, 0.4), (-0.2, 0.14), (0.2, 0.14))):
            D = P.L('t%d' % k, M['mid'] if k else M['light'], outline=0.03)
            with D.at(0.3, -0.3, 135):
                streak(D, (0, o * 0.5), (0.95 - abs(o) * 1.5, o * 1.6), w)
        orb(P, M, 'o', 0.3, -0.3, 0.27)
    elif v == 1:
        for i, o in enumerate((-0.24, 0.24)):
            D = P.L('st%d' % i, M['light'], outline=0.02)
            with D.at(0, 0, -45):
                streak(D, (0.4, o), (-0.85, o), 0.07)
        D = P.L('b', M['mid'])
        with D.at(0, 0, -45):
            D.poly([(-0.55, 0), (-0.25, -0.17), (0.7, 0), (-0.25, 0.17)])
        D = P.L('c', M['core'], outline=0.0)
        with D.at(0, 0, -45):
            D.poly([(-0.4, 0), (-0.2, -0.06), (0.6, 0), (-0.2, 0.06)])
    elif v == 2:
        for k, a in enumerate((-28, 0, 28)):
            D = P.L('l%d' % k, M['mid'] if k != 1 else M['light'], outline=0.03)
            with D.at(0.25, -0.25, 135 + a):
                D.taper(bez([(0, 0), (0.3, 0.12 * (k - 1)), (0.6, -0.1 * (k - 1)), (0.85 - 0.1 * abs(k - 1), 0.0)], 14), lambda t: 0.3 * (1 - t) ** 0.8 + 0.01)
        orb(P, M, 'o', 0.25, -0.25, 0.3)
    elif v == 3:
        for i, o in enumerate((-0.2, 0.2)):
            D = P.L('st%d' % i, M['light'], outline=0.02)
            with D.at(0, 0, -45):
                streak(D, (0.1, o), (-0.8, o), 0.07)
        D = P.L('k', M['mid'])
        with D.at(0.15, -0.15, -45):
            D.poly([(-0.18, 0), (0.0, -0.26), (0.55, 0), (0.0, 0.26)])
        D = P.L('k2', M['core'], outline=0.0)
        with D.at(0.15, -0.15, -45):
            D.poly([(-0.06, 0), (0.02, -0.12), (0.4, 0), (0.02, 0.12)])
    else:
        sh_bolt(P.L('z1', M['light'], outline=0.035), 0, 0, 0.78, 12)
        sh_bolt(P.L('z2', M['core'], outline=0.0), 0, 0, 0.46, 12)


@glyph(3)
def g_volley(P, M, rs, v, e):
    if v == 0:
        for i, a in enumerate((-26, 0, 26)):
            arrow(P, M, 'a%d' % i, 0.0, 0.62, a - 90, L=1.1 if i == 1 else 0.98)
    elif v == 1:
        for i in range(5):
            a = math.radians(-90 + (i - 2) * 24)
            d = 0.78 - abs(i - 2) * 0.06
            x, y = 0.0 + d * math.cos(a), 0.62 + d * math.sin(a)
            D = P.L('t%d' % i, M['mid'], outline=0.02)
            streak(D, (x, y), (0.0 + 0.1 * math.cos(a), 0.62 + 0.1 * math.sin(a)), 0.1)
            orb(P, M, 'o%d' % i, x, y, 0.1)
    else:
        for i, o in enumerate((-0.42, -0.14, 0.14, 0.42)):
            with P.L('p%d' % i, 'wood', outline=0.0).at(0, 0, 0) as D:
                pass
            arrow(P, M, 'a%d' % i, -0.35 + o * 0.7 + 0.0, 0.55 - o * 0.7 - 0.0 + 0.0, -50, L=1.0)


def _fall_obj(P, M, rs, e, x, y, sc, trail_dir=(0.6, -0.6)):
    kind = {'fire': 'rock', 'earth': 'rock', 'physical': 'rock', 'ice': 'shard', 'arcane': 'shard', 'holy': 'shard', 'lightning': 'bolt', 'wind': 'orb'}.get(e, 'orb')
    tx, ty = trail_dir
    for k, (o, w) in enumerate(((0.0, 0.3), (-0.16, 0.12), (0.16, 0.12))):
        D = P.L('tr%d' % int(sc * 10 + x * 3) + str(k), M['mid'] if k else M['light'], outline=0.03)
        ang = math.degrees(math.atan2(ty, tx))
        with D.at(x, y, ang):
            streak(D, (0, o * 0.6 * sc), (0.9 * sc - abs(o) * sc, o * 1.8 * sc), w * sc)
    tag = 'ob%d' % int(sc * 10 + x * 3)
    if kind == 'rock':
        D = P.L(tag, 'earth' if False else (hexc('#8a8478'), hexc('#2a2622')), outline=0.035, bevel=0.07)
        with D.at(x, y, 0, sc):
            D.poly(rock_poly(rs, 0.3))
        D = P.L(tag + 'c', M['core'], outline=0.0, bevel=0.03)
        with D.at(x, y, 0, sc):
            D.circle(-0.08, -0.06, 0.07)
            D.circle(0.1, 0.1, 0.05)
    elif kind == 'shard':
        D = P.L(tag, M['light'], outline=0.035)
        with D.at(x, y, 40, sc):
            D.poly([(-0.34, 0), (-0.05, -0.2), (0.34, 0), (-0.05, 0.2)])
        D = P.L(tag + 'c', M['core'], outline=0.0)
        with D.at(x, y, 40, sc):
            D.poly([(-0.2, 0), (-0.05, -0.08), (0.22, 0), (-0.05, 0.08)])
    elif kind == 'bolt':
        sh_bolt(P.L(tag, M['light'], outline=0.035), x, y, 0.34 * sc, 10)
    else:
        orb(P, M, tag, x, y, 0.24 * sc)


@glyph(4)
def g_meteor(P, M, rs, v, e):
    if v == 0:
        if e == 'wind':
            for k in range(6):
                w = 0.62 - k * 0.09
                P.L('f%d' % k, M['light'] if k % 2 == 0 else M['mid'], outline=0.03).ell(0.0, -0.5 + k * 0.17, w, 0.11)
            P.L('rg', M['mid'], outline=0.03).path(arcp(0, 0.62, 0.55, 0, 360, 40)[:-1] * np.array([1, 0.3]) + np.array([0, 0.0]), 0.06, closed=True)
        else:
            P.L('im', M['mid'], outline=0.03).path(Draw.arc_pts(-0.15, 0.55, 0.6, 0.2, 0, 360, 48)[:-1], 0.08, closed=True)
            _fall_obj(P, M, rs, e, -0.1, -0.1, 1.15)
    elif v == 1:
        P.L('im', M['mid'], outline=0.03).path(Draw.arc_pts(0, 0.58, 0.62, 0.2, 0, 360, 48)[:-1], 0.07, closed=True)
        for (x, y, s) in ((-0.38, -0.12, 0.62), (0.05, -0.38, 0.55), (0.3, 0.05, 0.68)):
            _fall_obj(P, M, rs, e, x, y, s)
    elif v == 2:
        D = P.L('pl', M['mid'], outline=0.03)
        D.poly([(-0.25, -0.9), (0.25, -0.9), (0.36, 0.5), (-0.36, 0.5)])
        D = P.L('pc', M['light'], outline=0.0)
        D.poly([(-0.12, -0.9), (0.12, -0.9), (0.2, 0.5), (-0.2, 0.5)])
        D = P.L('pk', M['core'], outline=0.0)
        D.poly([(-0.04, -0.9), (0.04, -0.9), (0.07, 0.5), (-0.07, 0.5)])
        P.L('im', M['mid'], outline=0.03).path(Draw.arc_pts(0, 0.52, 0.62, 0.18, 0, 360, 48)[:-1], 0.08, closed=True)
        orb(P, M, 'ib', 0, 0.5, 0.22)
    else:
        P.L('gr', M['dark'], outline=0.03).ell(0, 0.5, 0.7, 0.2)
        D = P.L('sp', M['light'], outline=0.035)
        for i, (x, h) in enumerate(((-0.5, 0.45), (-0.25, 0.75), (0.0, 0.95), (0.27, 0.7), (0.52, 0.42))):
            D.poly([(x - 0.13, 0.5), (x + 0.02, 0.5 - h), (x + 0.13, 0.5)])
        D = P.L('sc', M['core'], outline=0.0)
        D.poly([(-0.04, 0.5), (0.02, -0.4), (0.08, 0.5)])


@glyph(3)
def g_beam(P, M, rs, v, e):
    def beam(tag, rot, x0, x1, w):
        D1 = P.L(tag + 'a', M['mid'], outline=0.03)
        D2 = P.L(tag + 'b', M['light'], outline=0.0)
        D3 = P.L(tag + 'c', M['core'], outline=0.0)
        with D1.at(0, 0, rot):
            D1.poly([(x0, -w * 0.5), (x1 - 0.1, -w * 0.5), (x1, 0), (x1 - 0.1, w * 0.5), (x0, w * 0.5)])
        with D2.at(0, 0, rot):
            D2.rrect(x0 + 0.05, -w * 0.28, x1 - 0.1, w * 0.28, w * 0.28)
        with D3.at(0, 0, rot):
            D3.rrect(x0 + 0.1, -w * 0.1, x1 - 0.15, w * 0.1, w * 0.1)
    if v == 0:
        beam('b', -28, -0.55, 0.95, 0.34)
        with P.L('sr', M['light'], outline=0.03).at(0, 0, -28) as D:
            D.ring(-0.55, 0, 0.2, 0.07)
        orb(P, M, 'o', -0.55 * math.cos(math.radians(28)), 0.55 * math.sin(math.radians(28)) * 1.0, 0.14)
    elif v == 1:
        beam('b1', -10, -0.8, 0.8, 0.2)
        beam('b2', 22, -0.8, 0.8, 0.2)
        orb(P, M, 'o', 0.0, 0.0, 0.2)
    else:
        pts = [(-0.7, 0.45), (-0.3, 0.1), (-0.1, 0.3), (0.2, -0.15), (0.35, 0.0), (0.7, -0.5)]
        P.L('z1', M['mid'], outline=0.03).path(pts, 0.26)
        P.L('z2', M['light'], outline=0.0).path(pts, 0.14)
        P.L('z3', M['core'], outline=0.0).path(pts, 0.05)
        orb(P, M, 'o', -0.7, 0.45, 0.16)


@glyph(2)
def g_cone(P, M, rs, v, e):
    ax, ay = -0.5, 0.5
    D = P.L('sec', M['light'], outline=0.03)
    pts = [(ax, ay)] + [(ax + 1.4 * math.cos(math.radians(a)), ay + 1.4 * math.sin(math.radians(a))) for a in np.linspace(-62, -18, 20)]
    D.poly(pts)
    if v == 0:
        D = P.L('ar', M['core'], outline=0.0)
        for r in (0.6, 0.95, 1.3):
            D.path([(ax + r * math.cos(math.radians(a)), ay + r * math.sin(math.radians(a))) for a in np.linspace(-60, -20, 14)], 0.07)
        D = P.L('ed', M['mid'], outline=0.03)
        for a in (-62, -18):
            D.path([(ax, ay), (ax + 1.4 * math.cos(math.radians(a)), ay + 1.4 * math.sin(math.radians(a)))], 0.06)
    else:
        for k, a in enumerate((-50, -40, -30)):
            D = P.L('w%d' % k, M['core'] if k != 1 else M['mid'], outline=0.02)
            with D.at(ax, ay, a):
                D.taper([(0.1 + t * 1.2, 0.07 * math.sin(t * 9 + k)) for t in np.linspace(0, 1, 24)], lambda t: 0.16 * math.sin(PI * min(t * 1.5, 1)) * (1 - t * 0.6))
    orb(P, M, 'ap', ax, ay, 0.14)


@glyph(2)
def g_chain(P, M, rs, v, e):
    if v == 0:
        nodes = [(-0.5, 0.4), (-0.02, -0.18), (0.5, 0.3)]
        for i in range(2):
            a, b = np.array(nodes[i]), np.array(nodes[i + 1])
            pts = np.linspace(a, b, 9)
            nrm = np.array([-(b - a)[1], (b - a)[0]]) / np.linalg.norm(b - a)
            for j in range(1, 8):
                pts[j] = pts[j] + nrm * (0.09 if j % 2 else -0.09)
            P.L('z%d' % i, M['light'], outline=0.03).path(pts, 0.09)
            P.L('zc%d' % i, M['core'], outline=0.0).path(pts, 0.035)
        for i, (x, y) in enumerate(nodes):
            orb(P, M, 'n%d' % i, x, y, 0.17 if i == 1 else 0.13)
    else:
        for k in range(3):
            D = P.L('l%d' % k, 'steel', outline=0.035)
            x, y = -0.45 + k * 0.45, 0.4 - k * 0.4
            with D.at(x, y, -45 + (90 if k % 2 else 0)):
                D.ring(0, 0, 0.2, 0.1) if False else D.path(Draw.arc_pts(0, 0, 0.26, 0.15, 0, 360, 32)[:-1], 0.1, closed=True)
        orb(P, M, 'o', 0.5, -0.45, 0.15)


@glyph(2)
def g_leap(P, M, rs, v, e):
    if v == 0:
        pts = bez([(-0.6, 0.45), (-0.45, -0.7), (0.45, -0.7), (0.55, 0.28)], 16)
        D = P.L('d', M['light'], outline=0.03)
        for i, p in enumerate(pts[::2][:-1]):
            D.circle(p[0], p[1], 0.06 + 0.035 * (i / 8))
        D = P.L('ah', M['core'], outline=0.03)
        D.poly([(0.38, 0.22), (0.72, 0.15), (0.52, 0.5)])
        P.L('im', M['mid'], outline=0.03).path(Draw.arc_pts(0.5, 0.58, 0.45, 0.14, 0, 360, 40)[:-1], 0.06, closed=True)
        D = P.L('dp', M['light'], outline=0.03)
        for (x, y, r) in ((0.02, 0.58, 0.15), (0.14, 0.52, 0.12), (1.0, 0.56, 0.1)):
            D.circle(x, y, r)
    else:
        sh_arrow_r(P.L('ar', M['light'], outline=0.035), 0, -0.1, 0.62, -90, w=0.4, hw=1.0, hl=0.8)
        D = P.L('cl', 'white', outline=0.03)
        for (x, y, r) in ((-0.35, 0.55, 0.2), (0.0, 0.5, 0.26), (0.38, 0.56, 0.2)):
            D.circle(x, y, r)
        spark4(P.L('s', M['core'], outline=0.02), 0.5, -0.55, 0.14)


@glyph(2)
def g_charge(P, M, rs, v, e):
    if v == 0:
        for k, (x, mt) in enumerate(((-0.52, 'dark'), (-0.12, 'mid'), (0.28, 'light'))):
            sh_chevron(P.L('c%d' % k, M[mt], outline=0.03), x, 0, 0.5, 90)
        for k, y in enumerate((-0.45, 0.45)):
            streak(P.L('s%d' % k, M['mid'], outline=0.02), (-0.2, y), (-0.85, y), 0.07)
        spark4(P.L('sp', M['core'], outline=0.02), 0.7, 0.0, 0.2)
    else:
        for k, y in enumerate((-0.4, 0.0, 0.4)):
            streak(P.L('s%d' % k, M['light'], outline=0.02), (0.0, y), (-0.9, y), 0.1)
        sh_shield(P.L('sh', 'steel', outline=0.035), 0.35, 0, 0.62, -90)
        sh_shield(P.L('sh2', M['mid'], outline=0.02), 0.35, 0, 0.4, -90)


@glyph(2)
def g_dash(P, M, rs, v, e):
    if v == 0:
        for k, (x, mt) in enumerate(((-0.35, 'dark'), (-0.05, 'mid'))):
            sh_arrow_r(P.L('g%d' % k, M[mt], outline=0.03), x, 0, 0.42, 0, w=0.0001 + 0.4, hw=0.9, hl=0.7)
        sh_arrow_r(P.L('ar', M['light'], outline=0.035), 0.4, 0, 0.5, 0, w=0.4, hw=1.0, hl=0.75)
        for k, y in enumerate((-0.48, 0.48)):
            streak(P.L('s%d' % k, M['mid'], outline=0.02), (-0.1, y), (-0.85, y), 0.08)
    else:
        for k, (o, mt) in enumerate(((0, 'core'), (-0.3, 'light'), (0.3, 'mid'))):
            D = P.L('sw%d' % k, M[mt], outline=0.03)
            D.taper(bez([(-0.8, 0.5 + o * 0.5), (-0.2, 0.4 + o), (0.35, -0.1 + o), (0.7, -0.5 + o * 0.5)], 18), lambda t: 0.2 * math.sin(PI * t) ** 0.7 + 0.01)
        sh_arrow_r(P.L('ah', M['core'], outline=0.03), 0.62, -0.45, 0.28, -52, w=0.0001 + 0.0, hw=1.0, hl=1.0)


@glyph(3)
def g_blink(P, M, rs, v, e):
    if v == 0:
        P.L('p1', M['mid'], outline=0.035).path(Draw.arc_pts(-0.3, 0.28, 0.42, 0.56, 0, 360, 40)[:-1], 0.15, closed=True)
        P.L('p1i', M['core'], outline=0.0).path(Draw.arc_pts(-0.3, 0.28, 0.22, 0.34, 0, 360, 40)[:-1], 0.07, closed=True)
        P.L('p2', M['light'], outline=0.035).path(Draw.arc_pts(0.4, -0.34, 0.28, 0.38, 0, 360, 40)[:-1], 0.12, closed=True)
        D = P.L('dt', M['light'], outline=0.02)
        for t in np.linspace(0.15, 0.85, 6):
            D.circle(-0.1 + 0.4 * t, 0.05 - 0.3 * t, 0.045)
        spark4(P.L('s', M['core'], outline=0.02), 0.5, 0.25, 0.14)
    elif v == 1:
        spark4(P.L('b', M['light'], outline=0.035), 0, 0, 0.62)
        D = P.L('pa', M['mid'], outline=0.02)
        for (x, y, r) in ((-0.45, -0.4, 0.09), (0.5, -0.35, 0.07), (-0.5, 0.35, 0.07), (0.45, 0.45, 0.1), (0.0, -0.62, 0.06), (0.02, 0.62, 0.06)):
            D.circle(x, y, r)
        orb(P, M, 'c', 0, 0, 0.14)
    else:
        P.L('p', M['mid'], outline=0.035).path(Draw.arc_pts(0, 0, 0.42, 0.66, 0, 360, 44)[:-1], 0.14, closed=True)
        P.L('pi', M['light'], outline=0.0).path(Draw.arc_pts(0, 0, 0.24, 0.46, 0, 360, 44)[:-1], 0.08, closed=True)
        spark4(P.L('s', M['core'], outline=0.02), 0.0, 0.0, 0.22)
        D = P.L('st', M['light'], outline=0.02)
        for (x, y, r) in ((-0.62, -0.3, 0.08), (0.62, 0.35, 0.08), (0.6, -0.5, 0.06)):
            spark4(D, x, y, r * 1.6)


@glyph(4)
def g_summon(P, M, rs, v, e):
    P.L('rg', M['mid'], outline=0.03).path(Draw.arc_pts(0, 0.5, 0.66, 0.24, 0, 360, 44)[:-1], 0.08, closed=True)
    P.L('rg2', M['light'], outline=0.0).path(Draw.arc_pts(0, 0.5, 0.42, 0.15, 0, 360, 44)[:-1], 0.04, closed=True)
    if v == 0:
        D = P.L('pl', M['mid'], outline=0.0)
        D.poly([(-0.3, 0.5), (-0.18, -0.55), (0.18, -0.55), (0.3, 0.5)])
        sh_skull(P.L('sk', 'bone', outline=0.04), 0, -0.05, 0.42)
    elif v == 1:
        sh_fist(P.L('hd', 'bone', outline=0.04), 0, 0.05, 0.4, 0)
        D = P.L('pa', M['light'], outline=0.02)
        for x in (-0.3, 0.0, 0.3):
            spark4(D, x, -0.55 - abs(x) * 0.2, 0.1)
    elif v == 2:
        sh_pentagram(P.L('pg', M['light'], outline=0.03), 0, 0.0, 0.46)
        for k in range(5):
            a = math.radians(-90 + 72 * k)
            sh_flame(P.L('fl%d' % k, M['core'], outline=0.02), 0.62 * math.cos(a) * 0.82, 0.62 * math.sin(a) * 0.82 - 0.0, 0.14)
    else:
        D = P.L('pw', 'bone', outline=0.04)
        D.ell(0, 0.08, 0.26, 0.22)
        for (x, y) in ((-0.32, -0.22), (-0.12, -0.38), (0.12, -0.38), (0.32, -0.22)):
            D.ell(x, y, 0.09, 0.12, 0)


@glyph(3)
def g_trap(P, M, rs, v, e):
    if v == 0:
        P.L('rg', 'iron', outline=0.035).path(Draw.arc_pts(0, 0, 0.55, 0.55, 0, 360, 48)[:-1], 0.16, closed=True)
        D = P.L('tt', 'steel', outline=0.03)
        for k in range(10):
            with D.at(0, 0, k * 36):
                D.poly([(0.38, -0.07), (0.2, 0), (0.38, 0.07)])
        P.L('pl', 'bronze', outline=0.03).circle(0, 0, 0.14)
        orb(P, M, 'o', 0, 0, 0.07)
    elif v == 1:
        D = P.L('cs', 'iron', outline=0.035)
        for a in (-90, 30, 150):
            with D.at(0, 0.1, a):
                D.poly([(0, -0.07), (0.75, 0), (0, 0.07)])
        D.circle(0, 0.1, 0.1)
        spark4(P.L('s', M['core'], outline=0.02), 0.0, -0.58, 0.14)
    else:
        P.L('rg', M['mid'], outline=0.035).path(Draw.arc_pts(0, 0, 0.58, 0.58, 0, 360, 48)[:-1], 0.1, closed=True)
        D = P.L('tt', M['light'], outline=0.03)
        for k in range(8):
            with D.at(0, 0, k * 45):
                D.poly([(0.48, -0.09), (0.2, 0), (0.48, 0.09)])
        sh_star(P.L('st', M['core'], outline=0.03), 0, 0, 0.17)


@glyph(3)
def g_hook(P, M, rs, v, e):
    if v == 0:
        D = P.L('rp', 'bronze', outline=0.03)
        D.path(catmull([(0.62, -0.62), (0.4, -0.4), (0.25, -0.15), (0.0, -0.05)], 8), 0.07)
        D = P.L('hk', 'iron', outline=0.04)
        D.path(Draw.arc_pts(-0.05, 0.1, 0.4, 0.4, -100, 130, 24), 0.15)
        D.poly([(-0.34, 0.3), (-0.62, 0.05), (-0.46, 0.38)]) if False else D.poly([(-0.32, 0.4), (-0.6, 0.08), (-0.18, 0.28)])
        D.circle(0.0, -0.22, 0.1)
    elif v == 1:
        sh_anchor(P.L('an', 'iron', outline=0.04), 0, 0.05, 0.62, 20)
        P.L('rp', 'bronze', outline=0.03).path(catmull([(0.15, -0.65), (0.4, -0.5), (0.55, -0.2)], 6), 0.06)
    else:
        D = P.L('hk', 'iron', outline=0.04)
        D.path(bez([(0.0, -0.7), (0.5, -0.5), (0.5, 0.1), (0.05, 0.1)], 24), 0.15)
        D.path(bez([(0.05, 0.1), (-0.35, 0.1), (-0.4, 0.5), (0.0, 0.62)], 20), 0.15)
        D.poly([(-0.15, 0.62), (0.18, 0.58), (0.08, 0.25)])
        D.circle(0.0, -0.72, 0.1)
        orb(P, M, 'o', 0.62, 0.55, 0.1)


@glyph(2)
def g_skull_blade(P, M, rs, v, e):
    if v == 0:
        sword(P, -0.6, 0.62, -45, L=1.6, w=0.17, guard_w=0.26, tag='sw')
        sh_skull(P.L('sk', 'bone', outline=0.045), -0.1, -0.08, 0.5)
    else:
        sword(P, -0.62, 0.62, -50, L=1.55, w=0.15, guard_w=0.24, tag='a')
        sword(P, 0.62, 0.62, -130, L=1.55, w=0.15, guard_w=0.24, tag='b')
        sh_skull(P.L('sk', 'bone', outline=0.045), 0.0, -0.02, 0.5)
        D = P.L('gl', M['core'], outline=0.0)
        D.ell(-0.12, -0.08, 0.06, 0.07)
        D.ell(0.12, -0.08, 0.06, 0.07)


@glyph(2)
def g_drain(P, M, rs, v, e):
    if v == 0:
        for k in range(3):
            D = P.L('sp%d' % k, M['mid'], outline=0.03)
            with D.at(0, 0, k * 120):
                D.taper(arcp(0, 0, 0.6, -20, 120, 24)[::-1], lambda t: 0.04 + 0.14 * (1 - t) ** 1.2)
        sh_heart(P.L('ht', M['light'], outline=0.04), 0, 0.02, 0.36)
        sh_heart(P.L('hc', M['core'], outline=0.0), -0.05, -0.04, 0.14)
    else:
        sh_drop(P.L('d1', M['light'], outline=0.04), 0.3, 0.1, 0.38)
        orb(P, M, 'o', -0.55, -0.35, 0.14)
        D = P.L('fl', M['mid'], outline=0.03)
        D.taper(bez([(-0.45, -0.28), (-0.2, 0.15), (0.0, -0.1), (0.15, 0.1)], 18), lambda t: 0.16 * (1 - t) ** 0.6 + 0.02)
        sh_drop(P.L('d2', M['core'], outline=0.0), 0.26, 0.14, 0.15)


@glyph(4)
def g_curse(P, M, rs, v, e):
    if v == 0:
        P.L('rg', M['mid'], outline=0.035).path(Draw.arc_pts(0, -0.05, 0.62, 0.62, 0, 360, 48)[:-1], 0.09, closed=True)
        D = P.L('ey', 'bone', outline=0.04)
        sh_eye(D, 0, -0.05, 0.5)
        D = P.L('ir', M['light'], outline=0.03)
        D.circle(0, -0.05, 0.17)
        D = P.L('dr', M['mid'], outline=0.03)
        for x in (-0.3, 0.0, 0.3):
            sh_drop(D, x, 0.58 + (0.06 if x == 0 else 0), 0.1)
    elif v == 1:
        for k, a in enumerate((20, 140, 260)):
            D = P.L('w%d' % k, M['mid'], outline=0.03)
            with D.at(0, 0, a):
                D.taper(bez([(0.2, 0), (0.55, -0.28), (0.78, 0.18), (0.55, 0.45)], 18), lambda t: 0.2 * (1 - t) ** 0.7 + 0.015)
        sh_skull(P.L('sk', 'bone', outline=0.04), 0, 0, 0.44)
    elif v == 2:
        sh_skull(P.L('sk', M['light'], outline=0.04), 0, -0.2, 0.42)
        for k, y in enumerate((0.38, 0.52, 0.66)):
            sh_chevron(P.L('c%d' % k, M['mid'], outline=0.03), 0, y + 0.03, 0.2 + 0.02 * k, 180)
    else:
        sh_pentagram(P.L('pg', M['light'], outline=0.035), 0, 0, 0.62)
        orb(P, M, 'o', 0, 0, 0.14)


# ------------------------------------------------------------------ soins
def _plus(P, M, tag, x, y, s, mat='light'):
    sh_plus(P.L(tag, M[mat], outline=0.04), x, y, s, 0, t=0.52)
    sh_plus(P.L(tag + 'c', M['core'], outline=0.0), x, y, s * 0.62, 0, t=0.34)


@glyph(3)
def g_cross(P, M, rs, v, e):
    if v == 0:
        _plus(P, M, 'p', 0, 0, 0.58)
    elif v == 1:
        sh_heart(P.L('h', M['mid'], outline=0.04), 0, 0.04, 0.62)
        sh_plus(P.L('p', 'white', outline=0.0, bevel=0.04), 0, 0.0, 0.3, 0, t=0.5)
    else:
        _plus(P, M, 'p', 0, 0, 0.5)
        D = P.L('lf', M['mid'], outline=0.03)
        sh_leaf(D, -0.55, 0.45, 0.22, -50)
        sh_leaf(D, 0.55, 0.45, 0.22, 50)
        spark4(P.L('s', M['core'], outline=0.02), 0.5, -0.5, 0.14)


@glyph(2)
def g_cross_aura(P, M, rs, v, e):
    P.L('a1', M['mid'], outline=0.03).path(Draw.arc_pts(0, 0, 0.66, 0.66, 0, 360, 48)[:-1], 0.07, closed=True)
    P.L('a2', M['light'], outline=0.03).path(Draw.arc_pts(0, 0, 0.5, 0.5, 0, 360, 48)[:-1], 0.05, closed=True) if v == 1 else None
    _plus(P, M, 'p', 0, 0, 0.36)
    D = P.L('dt', M['core'], outline=0.02)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        D.circle(0.66 * math.cos(a), 0.66 * math.sin(a), 0.055)


@glyph(2)
def g_cross_pulse(P, M, rs, v, e):
    for k, r in enumerate((0.38, 0.54, 0.7)):
        D = P.L('a%d' % k, M['light'] if k == 0 else M['mid'], outline=0.03)
        for a0 in (-50, 130):
            D.arc(0, 0, r, a0, a0 + 100, 0.07)
    _plus(P, M, 'p', 0, 0, 0.3)


@glyph(2)
def g_cross_chain(P, M, rs, v, e):
    nodes = [(-0.55, 0.38), (0.55, 0.38), (0.0, -0.45)]
    for i, (a, b) in enumerate(((0, 2), (2, 1))):
        P.L('l%d' % i, M['mid'], outline=0.03).path([nodes[a], nodes[b]], 0.08)
    for i, (x, y) in enumerate(nodes[:2]):
        orb(P, M, 'o%d' % i, x, y, 0.13)
    _plus(P, M, 'p', 0.0, -0.4, 0.3)


@glyph(2)
def g_ankh(P, M, rs, v, e):
    if v == 0:
        D = P.L('wg', M['light'], outline=0.03)
        for sx in (-1, 1):
            sh_wing(D, sx * 0.0, 0.0, 0.0001)
        for sx in (-1, 1):
            with D.at(0, 0.0, 0, sx, 1):
                D.taper(bez([(0.12, 0.05), (0.5, -0.05), (0.72, -0.28), (0.8, -0.5)], 14), lambda t: 0.16 * (1 - t) ** 0.6 + 0.01)
                D.taper(bez([(0.12, 0.2), (0.5, 0.14), (0.7, 0.0), (0.76, -0.2)], 14), lambda t: 0.14 * (1 - t) ** 0.6 + 0.01)
    D = P.L('an', 'gold', outline=0.04)
    D.path(Draw.arc_pts(0, -0.32, 0.17, 0.25, 0, 360, 36)[:-1], 0.1, closed=True)
    D.rrect(-0.065, -0.1, 0.065, 0.68, 0.03)
    D.rrect(-0.36, 0.04, 0.36, 0.16, 0.03)
    orb(P, M, 'o', 0, 0.05, 0.07)


@glyph(2)
def g_swap(P, M, rs, v, e):
    for k, (a0, a1, mt) in enumerate(((205, 335, 'light'), (25, 155, 'mid'))):
        D = P.L('a%d' % k, M[mt], outline=0.035)
        D.arc(0, 0, 0.46, a0, a1 - 12, 0.16)
        a = math.radians(a1)
        tx, ty = 0.46 * math.cos(a), 0.46 * math.sin(a)
        tdir = a + PI / 2
        hx, hy = math.cos(tdir), math.sin(tdir)
        nx, ny = math.cos(a), math.sin(a)
        D.poly([(tx + 0.12 * hx, ty + 0.12 * hy), (tx + 0.26 * nx, ty + 0.26 * ny), (tx - 0.26 * nx, ty - 0.26 * ny)])
    orb(P, M, 'o1', 0, 0, 0.13)


@glyph(4)
def g_shield(P, M, rs, v, e):
    if v == 0:
        sh_shield(P.L('s1', 'steel', outline=0.04), 0, 0.02, 0.66)
        sh_shield(P.L('s2', M['mid'], outline=0.02), 0, 0.04, 0.5)
        sh_star(P.L('s3', 'gold', outline=0.02), 0, -0.04, 0.2)
    elif v == 1:
        P.L('r1', 'iron', outline=0.04).circle(0, 0, 0.64)
        P.L('r2', M['mid'], outline=0.02).circle(0, 0, 0.5)
        P.L('r3', 'gold', outline=0.03).circle(0, 0, 0.18)
        D = P.L('r4', M['light'], outline=0.0)
        D.ring(0, 0, 0.34, 0.04)
    elif v == 2:
        D = P.L('dm', M['mid'], outline=0.04)
        D.poly(np.vstack([Draw.arc_pts(0, 0.35, 0.66, 0.9, 180, 360, 30), [(0.66, 0.35), (-0.66, 0.35)]]))
        D = P.L('rm', M['light'], outline=0.03)
        D.path(Draw.arc_pts(0, 0.35, 0.66, 0.9, 180, 360, 30), 0.1)
        D.rrect(-0.72, 0.3, 0.72, 0.4, 0.03)
        sh_shield(P.L('in', 'steel', outline=0.03), 0, 0.2, 0.28)
    else:
        D = P.L('t1', 'steel', outline=0.04)
        D.rrect(-0.38, -0.7, 0.38, 0.55, 0.14)
        D.poly([(-0.38, 0.4), (0.38, 0.4), (0.0, 0.8)])
        D = P.L('t2', M['mid'], outline=0.02)
        D.rrect(-0.28, -0.6, 0.28, 0.4, 0.1)
        D.poly([(-0.28, 0.3), (0.28, 0.3), (0.0, 0.62)])
        P.L('t3', M['core'], outline=0.0).rect(-0.04, -0.5, 0.04, 0.45)


@glyph(2)
def g_parry(P, M, rs, v, e):
    if v == 0:
        sword(P, -0.7, 0.7, -50, L=1.5, w=0.15, guard_w=0.24, tag='a')
        sword(P, 0.7, 0.7, -130, L=1.5, w=0.15, guard_w=0.24, tag='b')
        D = P.L('sp', M['core'], outline=0.03)
        D.star(0, -0.12, 8, 0.3, 0.1, -90)
    else:
        sh_shield(P.L('sh', 'steel', outline=0.04), -0.1, 0.1, 0.52)
        sh_shield(P.L('sh2', M['mid'], outline=0.02), -0.1, 0.12, 0.38)
        sword(P, 0.2, 0.7, -70, L=1.4, w=0.14, guard_w=0.22, tag='sw')
        D = P.L('sp', M['core'], outline=0.03)
        D.star(0.35, -0.38, 8, 0.22, 0.07, -90)


@glyph(4)
def g_arrow_up(P, M, rs, v, e):
    if v == 0:
        for k, (y, mt) in enumerate(((0.38, 'dark'), (0.02, 'mid'), (-0.34, 'light'))):
            sh_chevron(P.L('c%d' % k, M[mt], outline=0.035), 0, y + 0.1, 0.62, 0)
    elif v == 1:
        sh_arrow_r(P.L('ar', M['light'], outline=0.04), 0, 0, 0.66, -90, w=0.5, hw=1.2, hl=0.9)
        sh_arrow_r(P.L('ac', M['core'], outline=0.0), 0, 0.05, 0.4, -90, w=0.2, hw=0.5, hl=0.6)
    elif v == 2:
        P.L('rg', M['mid'], outline=0.035).path(Draw.arc_pts(0, 0, 0.58, 0.58, 0, 360, 44)[:-1], 0.1, closed=True)
        sh_arrow_r(P.L('ar', M['light'], outline=0.04), 0, 0, 0.42, -90, w=0.46, hw=1.2, hl=0.9)
    else:
        sh_arrow_r(P.L('ar', M['light'], outline=0.04), 0, 0.05, 0.6, -90, w=0.5, hw=1.2, hl=0.9)
        D = P.L('st', M['core'], outline=0.02)
        for (x, y, r) in ((-0.55, -0.4, 0.13), (0.55, -0.1, 0.1), (-0.5, 0.35, 0.09)):
            spark4(D, x, y, r)


@glyph(1)
def g_horn(P, M, rs, v, e):
    D = P.L('hn', 'bone', outline=0.04)
    D.taper(bez([(-0.78, 0.38), (-0.66, -0.12), (-0.25, -0.3), (0.18, -0.2)], 24), lambda t: 0.1 + 0.42 * t ** 1.4)
    D = P.L('bl', M['mid'], outline=0.03)
    with D.at(0.18, -0.2, 18):
        D.ell(0.02, 0, 0.14, 0.4)
    D = P.L('bd', 'gold', outline=0.03)
    D.rrect(-0.84, 0.3, -0.62, 0.5, 0.05)
    with D.at(0.1, -0.2, 18):
        D.rrect(-0.06, -0.38, 0.06, 0.38, 0.03)
    D = P.L('wv', M['light'], outline=0.03)
    for r in (0.34, 0.54):
        D.arc(0.22, -0.2, r, -50, 50, 0.07)


@glyph(1)
def g_eye_slash(P, M, rs, v, e):
    sh_eye(P.L('ey', 'bone', outline=0.04), 0, 0, 0.7)
    P.L('ir', M['mid'], outline=0.03).circle(0, 0, 0.26)
    P.L('pu', 'black', outline=0.0).circle(0, 0, 0.11)
    D = P.L('sl', M['light'], outline=0.045)
    D.line(-0.55, 0.55, 0.55, -0.55, 0.12)


@glyph(3)
def g_hourglass(P, M, rs, v, e):
    if v == 0:
        D = P.L('gl', 'glass', outline=0.035, bevel=0.05)
        D.poly([(-0.38, -0.55), (0.38, -0.55), (0.38, -0.42), (0.08, -0.02), (0.08, 0.02), (0.38, 0.42), (0.38, 0.55), (-0.38, 0.55), (-0.38, 0.42), (-0.08, 0.02), (-0.08, -0.02), (-0.38, -0.42)])
        D = P.L('sn', M['light'], outline=0.0, bevel=0.05)
        D.poly([(-0.24, -0.36), (0.24, -0.36), (0.05, -0.08), (-0.05, -0.08)])
        D.poly([(-0.3, 0.5), (0.3, 0.5), (0.15, 0.3), (-0.15, 0.3)])
        D = P.L('fr', 'gold', outline=0.04)
        D.rrect(-0.5, -0.7, 0.5, -0.55, 0.05)
        D.rrect(-0.5, 0.55, 0.5, 0.7, 0.05)
    elif v == 1:
        P.L('rg', 'gold', outline=0.04).path(Draw.arc_pts(0, 0, 0.55, 0.55, 0, 360, 48)[:-1], 0.13, closed=True)
        P.L('fc', M['mid'], outline=0.0).circle(0, 0, 0.47)
        D = P.L('tk', 'bone', outline=0.0, bevel=0.03)
        for k in range(12):
            with D.at(0, 0, k * 30):
                D.rect(0.34, -0.025, 0.44, 0.025)
        D = P.L('hd', 'black', outline=0.02, bevel=0.03)
        D.line(0, 0, 0, -0.34, 0.06)
        D.line(0, 0, 0.22, 0.12, 0.06)
        orb(P, M, 'o', 0, 0, 0.07)
    else:
        D = P.L('gl', 'glass', outline=0.035, bevel=0.05)
        D.poly([(-0.28, -0.42), (0.28, -0.42), (0.28, -0.32), (0.06, -0.02), (0.06, 0.02), (0.28, 0.32), (0.28, 0.42), (-0.28, 0.42), (-0.28, 0.32), (-0.06, 0.02), (-0.06, -0.02), (-0.28, -0.32)])
        D = P.L('fr', 'gold', outline=0.04)
        D.rrect(-0.38, -0.54, 0.38, -0.42, 0.04)
        D.rrect(-0.38, 0.42, 0.38, 0.54, 0.04)
        for k, (a0, a1, mt) in enumerate(((210, 330, 'light'), (30, 150, 'mid'))):
            D = P.L('ar%d' % k, M[mt], outline=0.03)
            D.arc(0, 0, 0.66, a0, a1, 0.1)
            a = math.radians(a1)
            tx, ty = 0.66 * math.cos(a), 0.66 * math.sin(a)
            tdir = a + PI / 2
            D.poly([(tx + 0.16 * math.cos(tdir), ty + 0.16 * math.sin(tdir)), (tx + 0.13 * math.cos(a), ty + 0.13 * math.sin(a)), (tx - 0.13 * math.cos(a), ty - 0.13 * math.sin(a))])
        D = P.L('sn', M['light'], outline=0.0, bevel=0.04)
        D.poly([(-0.18, -0.32), (0.18, -0.32), (0.03, -0.06), (-0.03, -0.06)])
        D.poly([(-0.2, 0.4), (0.2, 0.4), (0.1, 0.24), (-0.1, 0.24)])


GLYPHS = {k[2:]: v for k, v in dict(globals()).items() if k.startswith('g_') and callable(v)}
