"""Icones de statuts 32x32 (assets/icons/status) : badge rond + glyphe."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from shapes import *

OUT = ASSETS + '/icons/status'
ST = {}
RIM = {'buff': 'gold', 'debuff': 'ruby', 'neutral': 'steel'}
BG = {'buff': ('#2a6a3a', '#0c2a1c'), 'debuff': ('#7a1a2a', '#2a0610'), 'neutral': ('#3a4a7a', '#12183a')}


def status(kind, bgc=None):
    def deco(fn):
        ST[fn.__name__.rstrip('_')] = (fn, kind, bgc)
        return fn
    return deco


def mk(P, n, m, **k):
    return P.L(n, m, **k)


@status('debuff', ('#2a4a8a', '#0a1636'))
def slow(P):
    D = mk(P, 'sh', 'bronze', outline=0.05)
    D.circle(-0.1, -0.12, 0.5)
    D = mk(P, 'bd', 'parch', outline=0.05)
    D.rrect(-0.85, 0.2, 0.8, 0.55, 0.17)
    D.path([(0.58, 0.28), (0.7, -0.05)], 0.1)
    D.path([(0.72, 0.28), (0.9, -0.02)], 0.1)
    mk(P, 'sp', 'dark', outline=0.0, bevel=0.03, spec=0).path(catmull([(-0.1, -0.12), (-0.02, -0.18), (0.0, -0.05), (-0.18, 0.0), (-0.3, -0.2), (-0.1, -0.38)], 6), 0.07)


@status('debuff', ('#6a5a1a', '#241c06'))
def stun(P):
    for i, (x, y, s) in enumerate(((0, -0.5, 0.36), (-0.55, 0.3, 0.33), (0.55, 0.3, 0.33))):
        sh_star(mk(P, 's%d' % i, 'topaz', outline=0.05), x, y, s)
    D = mk(P, 'r', 'white', outline=0.0, bevel=0.03, spec=0)
    D.arc(0, 0.05, 0.62, 20, 160, 0.07)


@status('debuff', ('#4a3a1a', '#1c1406'))
def root(P):
    D = mk(P, 'r', 'wood', outline=0.05)
    for a, (x1, y1) in enumerate(((-0.8, 0.8), (-0.45, 0.95), (0.0, 0.9), (0.45, 0.95), (0.8, 0.8))):
        D.path(catmull([(0, -0.15), (x1 * 0.3, 0.3), (x1, y1)], 6), 0.17)
    D = mk(P, 'g', 'green', outline=0.04)
    sh_leaf(D, -0.2, -0.4, 0.34, -30)
    sh_leaf(D, 0.22, -0.45, 0.38, 25)


@status('debuff', ('#3a2a6a', '#120a2a'))
def fear(P):
    D = mk(P, 'g', 'white', outline=0.05)
    D.poly(catmull([(-0.6, 0.85), (-0.65, -0.3), (-0.4, -0.8), (0.4, -0.8), (0.65, -0.3), (0.6, 0.85), (0.3, 0.55), (0, 0.85), (-0.3, 0.55)], 6, closed=True))
    D = mk(P, 'e', 'dark', outline=0.0, bevel=0.03, spec=0)
    D.ell(-0.24, -0.25, 0.14, 0.2)
    D.ell(0.24, -0.25, 0.14, 0.2)
    D.ell(0, 0.18, 0.15, 0.22)


@status('debuff', ('#5a2a5a', '#1a0a2a'))
def silence(P):
    D = mk(P, 'b', 'white', outline=0.05)
    D.rrect(-0.8, -0.7, 0.8, 0.35, 0.3)
    D.poly([(-0.3, 0.3), (-0.1, 0.3), (-0.5, 0.82)])
    D = mk(P, 'd', 'dark', outline=0, bevel=0.03, spec=0)
    for x in (-0.4, 0, 0.4):
        D.circle(x, -0.18, 0.1)
    D = mk(P, 'sl', 'ruby', outline=0.04, bevel=0.04)
    D.ring(0, 0, 0.82, 0.14)
    D.line(-0.6, -0.6, 0.6, 0.6, 0.14)


@status('debuff')
def bleed(P):
    sh_drop(mk(P, 'a', 'blood', outline=0.05), -0.25, -0.1, 0.62)
    sh_drop(mk(P, 'b', 'blood', outline=0.05), 0.38, 0.35, 0.45)


@status('debuff', ('#8a3a10', '#2a0e04'))
def burn(P):
    sh_flame(mk(P, 'a', 'fire', outline=0.05), 0, 0.05, 0.85)
    sh_flame(mk(P, 'b', 'topaz', outline=0.0, bevel=0.06), 0, 0.35, 0.42)


@status('debuff', ('#2a6a1a', '#0a2a06'))
def poison(P):
    sh_skull(mk(P, 'a', 'green', outline=0.05), 0, -0.15, 0.7)
    sh_drop(mk(P, 'b', 'emerald', outline=0.05), 0.55, 0.62, 0.3)
    sh_drop(mk(P, 'c', 'emerald', outline=0.05), -0.55, 0.65, 0.22)


@status('debuff', ('#1a5a8a', '#06203a'))
def freeze(P):
    D = mk(P, 'a', 'ice', outline=0.05)
    for k in range(3):
        with D.at(0, 0, k * 60):
            D.rrect(-0.92, -0.08, 0.92, 0.08, 0.04)
            for sgn in (-1, 1):
                for t in (-0.5, 0.5):
                    D.path([(t, 0), (t + 0.2 * (1 if t > 0 else -1) * 0.8, sgn * 0.3)], 0.07)
    D.circle(0, 0, 0.16)


@status('debuff', ('#7a1a1a', '#2a0606'))
def mark(P):
    D = mk(P, 'a', 'ruby', outline=0.05)
    D.ring(0, 0, 0.58, 0.16)
    for a in (0, 90, 180, 270):
        with D.at(0, 0, a):
            D.rect(0.3, -0.07, 0.98, 0.07)
    D.circle(0, 0, 0.14)


@status('buff', ('#8a7a1a', '#2a2406'))
def haste(P):
    sh_bolt(mk(P, 'a', 'topaz', outline=0.05), 0.05, 0, 0.9)


@status('buff', ('#8a3a1a', '#2a0e06'))
def empower(P):
    sword(P, -0.55, 0.85, -90, L=1.7, w=0.26, guard_w=0.34, tag='sw')
    sh_arrow_r(mk(P, 'ar', 'ruby', outline=0.045), 0.55, 0.05, 0.55, -90, w=0.4, hw=1.0, hl=0.8)


@status('buff', ('#2a4a8a', '#0a1636'))
def shield(P):
    sh_shield(mk(P, 'a', 'steel', outline=0.05), 0, 0.02, 0.88)
    sh_shield(mk(P, 'b', 'sapphire', outline=0.03), 0, 0.05, 0.6)


@status('buff', ('#2a6a3a', '#0c2a1c'))
def regen(P):
    sh_heart(mk(P, 'a', 'emerald', outline=0.05), 0, 0.03, 0.88)
    sh_plus(mk(P, 'b', 'white', outline=0.02, bevel=0.04), 0, -0.02, 0.38, t=0.5)


@status('buff', ('#2a5a1a', '#0a200a'))
def thorns(P):
    D = mk(P, 'a', 'green', outline=0.05)
    D.star(0, 0, 8, 0.98, 0.52, -90)
    D = mk(P, 'b', 'dark', outline=0.0, bevel=0.03, spec=0)
    D.circle(0, 0, 0.26)


@status('buff', ('#8a1a3a', '#2a0614'))
def lifesteal(P):
    sh_heart(mk(P, 'a', 'blood', outline=0.05), 0, -0.1, 0.8)
    D = mk(P, 'f', 'white', outline=0.04)
    D.poly([(-0.36, 0.35), (-0.14, 0.35), (-0.26, 0.9)])
    D.poly([(0.14, 0.35), (0.36, 0.35), (0.26, 0.9)])


@status('neutral', ('#3a4a6a', '#10142a'))
def invisible(P):
    D = mk(P, 'e', 'glass', outline=0.05)
    sh_eye(D, 0, 0, 0.95)
    D = mk(P, 's', 'dark', outline=0.04, bevel=0.04, spec=0)
    D.line(-0.7, 0.7, 0.7, -0.7, 0.14)


@status('buff', ('#8a7a2a', '#2a2406'))
def invulnerable(P):
    sh_shield(mk(P, 'a', 'gold', outline=0.05), 0, 0.02, 0.9)
    sh_star(mk(P, 'b', 'white', outline=0.0, bevel=0.05), 0, -0.05, 0.4)


@status('debuff', ('#8a2a1a', '#2a0a06'))
def taunted(P):
    D = mk(P, 'a', 'bone', outline=0.05)
    D.poly(catmull([(-0.85, 0.35), (-0.5, -0.1), (0.0, -0.55), (0.55, -0.5), (0.85, -0.1)], 8) )
    D.poly(np.vstack([catmull([(-0.85, 0.5), (-0.4, 0.05), (0.1, -0.35), (0.5, -0.3)], 8), [(0.85, 0.5), (0.6, 0.8), (0.0, 0.7)]]))
    D = mk(P, 'e', 'ruby', outline=0.04, bevel=0.04)
    D.rrect(0.72, -0.85, 0.9, -0.2, 0.05)
    D.circle(0.81, 0.0, 0.1)


@status('debuff', ('#6a2a2a', '#1c0808'))
def weaken(P):
    sword(P, -0.6, 0.8, -90, L=1.55, w=0.24, guard_w=0.32, tag='sw')
    sh_arrow_r(mk(P, 'ar', 'ruby', outline=0.045), 0.55, 0.05, 0.6, 90, w=0.42, hw=1.0, hl=0.8)


@status('buff', ('#2a5a6a', '#0a1e26'))
def armor_up(P):
    sh_shield(mk(P, 'a', 'iron', outline=0.05), -0.12, 0.08, 0.78)
    sh_arrow_r(mk(P, 'ar', 'emerald', outline=0.045), 0.58, -0.1, 0.55, -90, w=0.42, hw=1.0, hl=0.8)


@status('debuff', ('#6a2a2a', '#1c0808'))
def armor_break(P):
    D = mk(P, 'a', 'iron', outline=0.05)
    sh_shield(D, 0, 0.02, 0.92)
    D.poly([(0.02, -0.95), (0.12, -0.45), (-0.1, -0.2), (0.14, 0.2), (-0.05, 0.5), (0.08, 0.98), (-0.1, 0.98), (-0.2, 0.5), (0.0, 0.2), (-0.24, -0.2), (-0.02, -0.45), (-0.12, -0.95)], 0)
    sh_arrow_r(mk(P, 'ar', 'ruby', outline=0.045), 0.62, 0.55, 0.38, 90, w=0.42, hw=1.0, hl=0.8)


ORDER = ['slow', 'stun', 'root', 'fear', 'silence', 'bleed', 'burn', 'poison', 'freeze', 'mark', 'haste', 'empower', 'shield', 'regen', 'thorns',
         'lifesteal', 'invisible', 'invulnerable', 'taunted', 'weaken', 'armor_up', 'armor_break']


def badge_parts(name, P, tx=0, ty=0, s=1.0, scale_glyph=0.64):
    """ajoute un badge de statut (rim + fond + glyphe) a Parts P."""
    fn, kind, bgc = ST[name]
    bgc = bgc or BG[kind]
    B = SubParts(P, tx, ty, s, prefix='bd_')
    B.L('rim', RIM[kind], outline=0.05, bevel=0.1).circle(0, 0, 0.98)
    B.L('bg', (hexc(bgc[0]), hexc(bgc[1])), outline=0.0, bevel=0.25, spec=0.15).circle(0, 0, 0.78)
    fn(SubParts(P, tx, ty, s * scale_glyph, prefix='bg_'))


def run():
    for n in ORDER:
        S, ss = 32, 8
        P = Parts(S, S, ss)
        badge_parts(n, P)
        cv = render_parts(P, bevel=0.1, outline=0.05, shadow=0.04, spec=0.4)
        save(finalize(cv, S, S), f'{OUT}/{n}.png')
    return ORDER


if __name__ == '__main__':
    print(len(run()))
