"""Bibliotheque de formes vectorielles (coordonnees normalisees -1..1, y vers le bas) + moteur de rendu par calques."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

MAT.update({
    'ruby': (hexc('#ff8a98'), hexc('#8a0a24')), 'sapphire': (hexc('#a0d8ff'), hexc('#1a3c9a')),
    'emerald': (hexc('#a0ffb0'), hexc('#0a7a30')), 'amethyst': (hexc('#e0b8ff'), hexc('#5a1a9a')),
    'topaz': (hexc('#fff0a0'), hexc('#c07a10')), 'cloth_red': (hexc('#e8505e'), hexc('#6a1020')),
    'cloth_blue': (hexc('#6a8ae8'), hexc('#1a2a6a')), 'leather': (hexc('#b88458'), hexc('#4a2c16')),
    'fire': (hexc('#fff0a0'), hexc('#e0501a')), 'ice': (hexc('#f0fcff'), hexc('#3a9ad0')),
    'green': (hexc('#b0f0a0'), hexc('#2a8a30')), 'black': (hexc('#4a4a5c'), hexc('#0a0a12')),
    'blood': (hexc('#ff8090'), hexc('#8a0a20')), 'shadowm': (hexc('#c09ae0'), hexc('#3a1a5a')),
    'parch': (hexc('#f4e6bc'), hexc('#b49a60')), 'glass': (hexc('#e8f6ff'), hexc('#7ab0d8')),
})


class Parts:
    def __init__(self, w, h=None, ss=4, norm=True):
        self.w, self.h, self.ss, self.norm = w, h or w, ss, norm
        self.layers = {}
        self.order = []

    def L(self, name, mat='steel', **opts):
        if name not in self.layers:
            self.layers[name] = (Draw(self.w, self.h, self.ss, self.norm), mat, opts)
            self.order.append(name)
        return self.layers[name][0]

    def union(self):
        m = None
        for n in self.order:
            x = self.layers[n][0].mask()
            m = x if m is None else np.maximum(m, x)
        return m


def render_parts(P, bevel=0.06, outline=0.022, shadow=0.0, outline_col=None, spec=0.35, strength=1.0, depth=1.0, light=(-0.5, -0.7),
                 canvas=None, shadow_op=0.55, rows=None, ls=1.0):
    N = P.w * P.ss
    Hh = P.h * P.ss
    cv = blank(N, Hh) if canvas is None else canvas
    px = (min(P.w, P.h) / 2 * P.ss)
    oc = np.array([0.03, 0.04, 0.08], F32) if outline_col is None else outline_col
    if shadow > 0:
        u = P.union()
        drop_shadow(cv, dilate(u, outline * px), shadow * px * 0.3, shadow * px, shadow * px * 1.2, [0, 0, 0], shadow_op)
    for n in P.order:
        D, mat, o = P.layers[n]
        m = D.mask()
        if 'clip' in o:
            m = m * o['clip']
        if m.max() <= 0:
            continue
        hi, lo = MAT[mat] if isinstance(mat, str) else mat
        ow = (o['outline'] * ls if 'outline' in o else outline) * px
        if ow > 0:
            put(cv, dilate(m, ow), oc if 'ocol' not in o else o['ocol'])
        over(cv, lit(m, edt_in(m), hi, lo, (o['bevel'] * ls if 'bevel' in o else bevel) * px, spec=o.get('spec', spec), strength=o.get('strength', strength),
                     depth=o.get('depth', depth), light=light, rows=rows or bbox_rows(m)))
    return cv


# ------------------------------------------------------------------ formes
def sword(P, x, y, rot, L=1.0, w=0.09, tag='sw', blade='steel', hilt='gold', grip='leather', guard_w=0.17, curved=0.0):
    """epee pointant vers +x (avant rotation), pommeau en (0,0)."""
    with P.L(tag + 'b', blade).at(x, y, rot) as D:
        tip = L
        pts = [(0.26, -w / 2), (tip - 0.15, -w / 2 * (1 + curved)), (tip, 0), (tip - 0.15, w / 2), (0.26, w / 2)]
        D.poly(pts)
    with P.L(tag + 'g', grip).at(x, y, rot) as D:
        D.rrect(0.05, -0.04 * (w / 0.09) ** 0.5, 0.27, 0.04 * (w / 0.09) ** 0.5, 0.02)
    with P.L(tag + 'h', hilt).at(x, y, rot) as D:
        D.rrect(0.21, -guard_w, 0.275, guard_w, 0.025)
        D.circle(0.0, 0, 0.05)
        D.circle(0.215, -guard_w, 0.032)
        D.circle(0.215, guard_w, 0.032)


def crown(P, x, y, s=1.0, tag='cr', mat='gold', gem='ruby', pts=3):
    D = P.L(tag, mat)
    with D.at(x, y, 0, s):
        w = 0.34
        poly = [(-w, 0.12), (-w, -0.1), (-w * 0.5, 0.0)]
        poly = [(-w, 0.14), (-w * 1.0, -0.16)]
        n = pts
        xs = np.linspace(-w, w, 2 * n - 1)
        pl = [(-w, 0.14)]
        for i, xx in enumerate(xs):
            pl.append((xx, -0.17 if i % 2 == 0 else 0.0))
        pl += [(w, 0.14)]
        D.poly(pl)
        D.rrect(-w - 0.02, 0.06, w + 0.02, 0.17, 0.03)
        for i, xx in enumerate(xs):
            if i % 2 == 0:
                D.circle(xx, -0.19, 0.036)
    G = P.L(tag + 'g', gem, outline=0.012)
    with G.at(x, y, 0, s):
        w = 0.34
        xs = np.linspace(-w, w, 2 * pts - 1)
        G.circle(0, 0.115, 0.04)
        for i in range(1, pts - 1):
            pass
        G.circle(-w * 0.6, 0.115, 0.028)
        G.circle(w * 0.6, 0.115, 0.028)


def shield_pts(w=0.56, top=-0.5, bot=0.66, n=16):
    """ecu de heraut classique, retourne polygone ferme."""
    P = [(-w, top + 0.06), (-w * 0.5, top - 0.02), (0, top + 0.03), (w * 0.5, top - 0.02), (w, top + 0.06),
         (w, top + (bot - top) * 0.45), (w * 0.82, top + (bot - top) * 0.7), (w * 0.4, top + (bot - top) * 0.9), (0, bot),
         (-w * 0.4, top + (bot - top) * 0.9), (-w * 0.82, top + (bot - top) * 0.7), (-w, top + (bot - top) * 0.45)]
    return catmull(P, n, closed=True)


def star_shape(D, cx, cy, r, n=5, inner=0.45, rot=-90):
    D.star(cx, cy, n, r, r * inner, rot)


def gem_diamond(D, cx, cy, r):
    D.poly([(cx, cy - r), (cx + r * 0.8, cy), (cx, cy + r), (cx - r * 0.8, cy)])


# ================================================================== silhouettes mono-calque : sh_*(D, x, y, s, rot=0)
# chaque forme est dessinee dans un repere local de rayon ~1 puis placee/echelonnee par D.at(x, y, rot, s)

def _sh(fn):
    def w(D, x=0, y=0, s=1.0, rot=0, v=255, **kw):
        with D.at(x, y, rot, s):
            fn(D, v, **kw)
        return D
    w.__name__ = fn.__name__
    return w


@_sh
def sh_heart(D, v):
    t = np.linspace(0, 2 * PI_, 80)
    x = 16 * np.sin(t) ** 3 / 17.0
    y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)) / 17.0 - 0.05
    D.poly(np.stack([x, y], 1) * 1.05, v)


PI_ = math.pi


@_sh
def sh_drop(D, v):
    D.poly(catmull([(0, -1), (0.28, -0.5), (0.58, -0.05), (0.6, 0.3), (0.4, 0.78), (0, 0.95), (-0.4, 0.78), (-0.6, 0.3), (-0.58, -0.05), (-0.28, -0.5)], 8, closed=True), v)


@_sh
def sh_bolt(D, v):
    D.poly([(0.32, -1.0), (-0.52, 0.12), (-0.08, 0.12), (-0.38, 1.0), (0.56, -0.18), (0.1, -0.18), (0.55, -1.0)][:6] + [(0.1, -0.18)], v)


@_sh
def sh_plus(D, v, t=0.34):
    D.rrect(-t / 2, -1, t / 2, 1, 0.1, v)
    D.rrect(-1, -t / 2, 1, t / 2, 0.1, v)


@_sh
def sh_cross(D, v):
    D.rrect(-0.2, -1, 0.2, 1, 0.06, v)
    D.rrect(-0.62, -0.5, 0.62, -0.1, 0.06, v)


@_sh
def sh_star(D, v, n=5, inner=0.46):
    D.star(0, 0, n, 1.0, inner, -90, v)


@_sh
def sh_gear(D, v, n=8, ri=0.72, hole=0.3):
    pts = []
    for k in range(n):
        a0 = 2 * PI_ * k / n
        da = 2 * PI_ / n
        for fr, r in ((0.0, ri), (0.18, ri), (0.28, 1.0), (0.72, 1.0), (0.82, ri)):
            a = a0 + da * fr
            pts.append((r * math.cos(a), r * math.sin(a)))
    D.poly(pts, v)
    if hole > 0:
        D.circle(0, 0, hole, 0)


@_sh
def sh_arrow_r(D, v, w=0.34, hw=0.78, hl=0.8):
    D.poly([(-1, -w / 2), (1 - hl, -w / 2), (1 - hl, -hw / 2), (1, 0), (1 - hl, hw / 2), (1 - hl, w / 2), (-1, w / 2)], v)


@_sh
def sh_chevron(D, v, w=0.5):
    D.poly([(-0.9, 0.7), (0, -0.2), (0.9, 0.7), (0.9, 0.7 - w), (0, -0.2 - w), (-0.9, 0.7 - w)], v)


@_sh
def sh_person(D, v):
    D.circle(0, -0.5, 0.34, v)
    D.poly(catmull([(-0.8, 0.9), (-0.78, 0.35), (-0.5, 0.02), (0.5, 0.02), (0.78, 0.35), (0.8, 0.9)], 6), v)


@_sh
def sh_house(D, v):
    D.poly([(-1, -0.05), (0, -0.95), (1, -0.05), (0.82, -0.05), (0.82, 0.9), (-0.82, 0.9), (-0.82, -0.05)], v)
    D.rrect(-0.2, 0.2, 0.2, 0.9, 0.06, 0)


@_sh
def sh_skull(D, v):
    D.poly(catmull([(-0.78, -0.1), (-0.7, -0.62), (-0.35, -0.92), (0.35, -0.92), (0.7, -0.62), (0.78, -0.1), (0.55, 0.3), (0.45, 0.62), (-0.45, 0.62), (-0.55, 0.3)], 8, closed=True), v)
    D.rrect(-0.46, 0.5, 0.46, 0.95, 0.1, v)
    D.ell(-0.34, -0.12, 0.24, 0.27, 0, 0)
    D.ell(0.34, -0.12, 0.24, 0.27, 0, 0)
    D.poly([(0, 0.1), (0.12, 0.38), (-0.12, 0.38)], 0)
    for x in (-0.22, 0, 0.22):
        D.line(x, 0.62, x, 0.92, 0.05, 0)


@_sh
def sh_key(D, v):
    D.circle(-0.55, 0, 0.42, v)
    D.circle(-0.55, 0, 0.2, 0)
    D.rrect(-0.2, -0.1, 1.0, 0.1, 0.04, v)
    D.rect(0.6, 0.0, 0.76, 0.42, v)
    D.rect(0.84, 0.0, 1.0, 0.32, v)


@_sh
def sh_flask(D, v):
    D.rrect(-0.2, -1, 0.2, -0.35, 0.05, v)
    D.rrect(-0.3, -1.04, 0.3, -0.88, 0.05, v)
    D.poly(catmull([(-0.2, -0.4), (-0.85, 0.5), (-0.7, 0.92), (0.7, 0.92), (0.85, 0.5), (0.2, -0.4)], 8), v)


@_sh
def sh_bell(D, v):
    D.poly(catmull([(0, -0.95), (0.42, -0.7), (0.52, -0.05), (0.7, 0.5), (0.95, 0.62), (0.95, 0.7), (-0.95, 0.7), (-0.95, 0.62), (-0.7, 0.5), (-0.52, -0.05), (-0.42, -0.7)], 8, closed=True), v)
    D.circle(0, 0.88, 0.2, v)


@_sh
def sh_moon(D, v):
    D.circle(0, 0, 1.0, v)
    D.circle(0.45, -0.2, 0.82, 0)


@_sh
def sh_sun(D, v, rays=12):
    D.circle(0, 0, 0.55, v)
    for k in range(rays):
        a = 360 * k / rays
        with D.at(0, 0, a):
            D.poly([(0.7, -0.09), (1.0, 0), (0.7, 0.09)], v)


@_sh
def sh_flame(D, v):
    D.poly(catmull([(0.05, -1), (0.35, -0.55), (0.72, -0.1), (0.72, 0.4), (0.4, 0.88), (0, 0.98), (-0.4, 0.88), (-0.72, 0.4), (-0.68, -0.05), (-0.42, -0.35), (-0.3, -0.12), (-0.12, -0.5)], 8, closed=True), v)


@_sh
def sh_leaf(D, v):
    D.poly(catmull([(0, -1), (0.55, -0.45), (0.62, 0.15), (0.3, 0.75), (0, 1), (-0.3, 0.75), (-0.62, 0.15), (-0.55, -0.45)], 8, closed=True), v)


@_sh
def sh_eye(D, v):
    x = np.linspace(-1, 1, 40)
    up = np.stack([x, -0.62 * (1 - x ** 2) ** 0.85], 1)
    lo = np.stack([x, 0.62 * (1 - x ** 2) ** 0.85], 1)
    D.poly(np.vstack([up, lo[::-1]]), v)
    D.circle(0, 0, 0.3, 0)


@_sh
def sh_cloud(D, v):
    D.circle(-0.45, 0.2, 0.42, v)
    D.circle(0.05, -0.1, 0.55, v)
    D.circle(0.55, 0.15, 0.42, v)
    D.rrect(-0.85, 0.2, 0.97, 0.62, 0.2, v)


@_sh
def sh_wing(D, v):
    for k, (L, a) in enumerate(((1.0, -62), (0.92, -40), (0.8, -20), (0.66, 0), (0.5, 20))):
        with D.at(-0.6, 0.55, a):
            D.taper([(0, 0), (L * 0.5, -0.04), (L * 1.0, 0.0)], lambda t: 0.36 * (1 - t ** 3) * min(1, t * 8 + 0.3))


@_sh
def sh_shield(D, v):
    D.poly(shield_pts(0.82, -0.95, 1.0, 12), v)


@_sh
def sh_coin(D, v):
    D.circle(0, 0, 1.0, v)


@_sh
def sh_gem(D, v):
    D.poly([(-0.55, -0.95), (0.55, -0.95), (1.0, -0.3), (0, 1.0), (-1.0, -0.3)], v)


@_sh
def sh_hourglass(D, v):
    D.poly([(-0.7, -0.95), (0.7, -0.95), (0.7, -0.78), (0.12, -0.05), (0.12, 0.05), (0.7, 0.78), (0.7, 0.95), (-0.7, 0.95), (-0.7, 0.78), (-0.12, 0.05), (-0.12, -0.05), (-0.7, -0.78)], v)


@_sh
def sh_tower(D, v):
    D.rect(-0.55, -0.4, 0.55, 1.0, v)
    for x in (-0.7, -0.24, 0.22):
        D.rect(x, -0.95, x + 0.48, -0.35, v)
    D.rrect(-0.15, 0.2, 0.15, 1.0, 0.15, 0)
    D.rect(-0.05, -0.2, 0.05, 0.0, 0)


@_sh
def sh_envelope(D, v):
    D.rrect(-1, -0.65, 1, 0.65, 0.1, v)
    D.path([(-0.85, -0.5), (0, 0.15), (0.85, -0.5)], 0.1, v=0)


@_sh
def sh_lock(D, v):
    D.rrect(-0.7, -0.1, 0.7, 0.95, 0.15, v)
    D.path(Draw.arc_pts(0, -0.15, 0.42, 0.55, 180, 360, 20), 0.22, v=v)
    D.circle(0, 0.42, 0.14, 0)
    D.rect(-0.05, 0.42, 0.05, 0.7, 0)


@_sh
def sh_check(D, v, w=0.34):
    D.path([(-0.85, 0.05), (-0.3, 0.65), (0.9, -0.7)], w, v=v)


@_sh
def sh_cross_x(D, v, w=0.34):
    D.path([(-0.8, -0.8), (0.8, 0.8)], w, v=v)
    D.path([(0.8, -0.8), (-0.8, 0.8)], w, v=v)


@_sh
def sh_dumbbell(D, v):
    D.rrect(-0.6, -0.12, 0.6, 0.12, 0.05, v)
    for sx in (-1, 1):
        D.rrect(sx * 0.62 - 0.14, -0.62, sx * 0.62 + 0.14, 0.62, 0.08, v)
        D.rrect(sx * 0.88 - 0.1, -0.42, sx * 0.88 + 0.1, 0.42, 0.06, v)


@_sh
def sh_fist(D, v):
    D.rrect(-0.55, -0.4, 0.62, 0.62, 0.2, v)
    for i in range(4):
        D.rrect(-0.55 + i * 0.29, -0.78, -0.55 + i * 0.29 + 0.27, -0.2, 0.12, v)
    D.rrect(-0.85, 0.0, -0.4, 0.5, 0.12, v)
    D.rrect(-0.4, 0.55, 0.45, 0.95, 0.1, v)


@_sh
def sh_pentagram(D, v):
    pts = [(math.cos(math.radians(-90 + 72 * k)), math.sin(math.radians(-90 + 72 * k))) for k in range(5)]
    for k in range(5):
        D.line(*pts[k], *pts[(k + 2) % 5], 0.12, v)
    D.ring(0, 0, 0.95, 0.1, v)


@_sh
def sh_anchor(D, v):
    D.ring(0, -0.78, 0.2, 0.12, v)
    D.line(0, -0.6, 0, 0.88, 0.14, v)
    D.line(-0.35, -0.38, 0.35, -0.38, 0.12, v)
    D.path(Draw.arc_pts(0, 0.1, 0.8, 0.75, 20, 160, 20), 0.14, v=v)
    D.poly([(-0.95, 0.35), (-0.62, 0.58), (-0.98, 0.65)], v)
    D.poly([(0.95, 0.35), (0.62, 0.58), (0.98, 0.65)], v)


# ================================================================== sous-calques (echelle / decalage) pour badges & glyphes
class SubParts:
    """Proxy de Parts : chaque Draw cree recoit une transformation supplementaire (tx, ty, scale[, rot, flip])."""

    def __init__(self, P, tx=0, ty=0, s=1.0, rot=0, flip=False, prefix=''):
        self.P, self.prefix = P, prefix
        c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        fx = -1 if flip else 1
        self.T = np.array([[c * s * fx, -sn * s, tx], [sn * s * fx, c * s, ty], [0, 0, 1]])

    def L(self, name, mat='steel', **opts):
        n = self.prefix + name
        new = n not in self.P.layers
        d = self.P.L(n, mat, **opts)
        if new:
            d.stack.append(d.stack[-1] @ self.T)
        return d

    @property
    def layers(self):
        return self.P.layers
