"""Emblemes de classes 96x96 : ecu + bande de palette + silhouette d'arme + pastille de role."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from shapes import *
from weapons import WP

OUT = ASSETS + '/icons/classes'
S, SS = 96, 6
ROLE_RIM = {'tank': 'iron', 'bruiser': 'bronze', 'assassin': 'dark', 'mage': 'gold', 'ranged': 'wood', 'healer': 'white', 'summoner': 'amethyst', 'support': 'topaz'}
ROLE_COL = {'tank': '#8ab4ff', 'bruiser': '#ff9a4a', 'assassin': '#ff5a6a', 'mage': '#b58cff', 'ranged': '#9ae070', 'healer': '#7affb0', 'summoner': '#c090ff', 'support': '#ffe07a'}


def role_icon(P, role, x, y, s):
    B = SubParts(P, x, y, s, prefix='rl_')
    B.L('disc', (hexc(ROLE_COL[role]), darken(hexc(ROLE_COL[role]), 0.6)), outline=0.07, bevel=0.35).circle(0, 0, 1.0)
    g = SubParts(P, x, y, s * 0.62, prefix='rg_')
    if role == 'tank':
        sh_shield(g.L('a', 'steel', outline=0.1), 0, 0, 1.0)
    elif role == 'bruiser':
        sh_fist(g.L('a', 'dark', outline=0.1), 0, 0, 1.0)
    elif role == 'assassin':
        sh_drop(g.L('a', 'dark', outline=0.1), 0, 0, 1.0)
    elif role == 'mage':
        sh_star(g.L('a', 'white', outline=0.1), 0, 0, 1.0)
    elif role == 'ranged':
        g.L('a', 'dark', outline=0.0).ring(0, 0, 0.75, 0.22)
        g.L('b', 'dark', outline=0.0).circle(0, 0, 0.2)
    elif role == 'healer':
        sh_plus(g.L('a', 'white', outline=0.1), 0, 0, 1.0, t=0.55)
    elif role == 'summoner':
        sh_pentagram(g.L('a', 'white', outline=0.08), 0, 0, 1.0)
    else:
        sh_wing(g.L('a', 'white', outline=0.1), 0.15, -0.1, 1.2)


def render_class(c):
    pal = [hexc(x) for x in c['palette']]
    role = c['role']
    seed = seed_of(c['id'])
    rs = np.random.RandomState(seed)
    P = Parts(S, S, SS)
    sp = shield_pts(0.80, -0.84, 0.92, 14)
    rimmat = ROLE_RIM.get(role, 'iron')
    P.L('rim', rimmat, outline=0.035, bevel=0.07, spec=0.5).poly(sp)
    ip = shield_pts(0.70, -0.74, 0.82, 14)
    inner = Draw(S, S, SS)
    inner.poly(ip)
    im = inner.mask()
    f = P.L('field', (lighten(pal[0], 0.12), darken(pal[0], 0.5)), outline=0.0, bevel=0.1, spec=0.15)
    f.poly(ip)
    # bande diagonale (bend) de la 2e couleur
    b = P.L('band', (lighten(pal[1], 0.1), darken(pal[1], 0.4)), outline=0.0, bevel=0.05, spec=0.1, clip=im)
    b.poly([(-1.2, 0.35), (-1.2, 0.95), (1.2, -0.35), (1.2, -0.95)])
    for k, o in enumerate((-0.0,)):
        l = P.L('bl', (lighten(pal[2], 0.15), darken(pal[2], 0.3)), outline=0.0, bevel=0.03, spec=0.2, clip=im)
        l.poly([(-1.2, 0.3), (-1.2, 0.38), (1.2, -0.92), (1.2, -1.0)])
        l.poly([(-1.2, 0.98), (-1.2, 1.06), (1.2, -0.26), (1.2, -0.34)])
    # chevron bas : accent
    ch = P.L('chev', (lighten(pal[2], 0.1), darken(pal[2], 0.4)), outline=0.0, bevel=0.04, clip=im)
    ch.poly([(-1, 0.72), (0, 0.42), (1, 0.72), (1, 0.62), (0, 0.32), (-1, 0.62)])
    # arme
    kind = c['weapon_main']
    if kind in WP:
        WP[kind](SubParts(P, -0.66, 0.66, 1.0, -45, prefix='wp_'))
    off = c.get('weapon_off')
    if off in ('shield_kite', 'shield_round', 'shield_buckler', 'shield_tower'):
        sh_shield(P.L('os', 'iron', outline=0.035), 0.42, 0.42, 0.42)
        sh_shield(P.L('os2', (lighten(pal[2], 0.1), darken(pal[2], 0.4)), outline=0.0), 0.42, 0.44, 0.28)
    role_icon(P, role, 0.5, 0.64, 0.19)
    cv = render_parts(P, bevel=0.05, outline=0.026, shadow=0.02, spec=0.4)
    x, y = grid(S * SS, S * SS)
    return finalize(cv, S, S)


def run():
    cl = json.load(open(ROOT + '/data/classes.json'))
    for c in cl:
        save(render_class(c), f'{OUT}/{c["id"]}.png')
    return len(cl)


if __name__ == '__main__':
    print(run())
