"""Aides communes du kit grec (pièces d'équipement : bibliothèque numpy 'kitlib' du kit de corps).
Toute la géométrie est en repère CONTRAT (x gauche du perso, y haut, z avant) ; masque COLOR_0 : R primaire, G secondaire, B accent."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BODIES = os.path.join(ROOT, 'tools', 'blender_kit_bodies')
WEAPONS = os.path.join(ROOT, 'tools', 'blender_kit_weapons')
SP = os.environ.get('GK_SCRATCH', '/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/greek')
os.makedirs(SP, exist_ok=True)
if BODIES not in sys.path:
    sys.path.insert(0, BODIES)

from gear_common import *                      # kitlib, bodies_common, heads.HUMAN_ROWS, torso_shell, skirt, strap, tufts ...
from gear_hats import P_, smooth, ybot_front, ring_arc, band_arc, full_band, brow_ring, spikes_ring, HC
from gear_torso import T_, S_, tsh, belt, collar
from gear_shoulders import SC, dome, place, rim, mk
from gear_backs import B_


def leaf_geo(base, tip, w, t, up=(0, 0, 1), mid=0.42):
    """feuille / plume très légère (8 triangles, lisse) : base -> tip, largeur w dans le plan, épaisseur t selon `up`."""
    b, tp = np.asarray(base, float), np.asarray(tip, float)
    d = tp - b
    L = np.linalg.norm(d)
    dn = d / (L + 1e-12)
    u = np.asarray(up, float)
    u = u - dn * np.dot(u, dn)
    if np.linalg.norm(u) < 1e-6:
        u = np.cross(dn, [1.0, 0, 0])
        if np.linalg.norm(u) < 1e-6:
            u = np.cross(dn, [0, 0, 1.0])
    u = u / np.linalg.norm(u)
    s = np.cross(dn, u)
    m = b + d * mid
    V = [b, tp, m + s * w, m - s * w, m + u * t, m - u * t]
    F = [(0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2), (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)]
    return Geo(np.array(V), F).fix()


def leaf4(base, tip, w, t, up=(0, 0, 1)):
    """feuille à 2 segments (plus galbée) : 14 triangles."""
    b, tp = np.asarray(base, float), np.asarray(tip, float)
    d = tp - b
    L = np.linalg.norm(d)
    dn = d / (L + 1e-12)
    u = np.asarray(up, float)
    u = u - dn * np.dot(u, dn)
    if np.linalg.norm(u) < 1e-6:
        u = np.cross(dn, [1.0, 0, 0])
    u = u / np.linalg.norm(u)
    s = np.cross(dn, u)
    V = [b, tp]
    rings = []
    for f, ww, tt in ((0.28, 0.82, 0.8), (0.62, 0.7, 0.5)):
        m = b + d * f
        rings.append(len(V))
        V += [m + s * w * ww, m + u * t * tt, m - s * w * ww, m - u * t * tt]
    F = []
    a, c = rings
    for i in range(4):
        j = (i + 1) % 4
        F.append((0, a + i, a + j))
        F.append((a + i, c + i, c + j, a + j))
        F.append((1, c + j, c + i))
    return Geo(np.array(V), F).fix()


def wavy(p0, p1, amp=0.02, waves=2.0, m=9, axis=(1, 0, 0), phase=0.0):
    """chemin entre p0 et p1 avec ondulation latérale sinusoïdale."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    t = np.linspace(0, 1, m)[:, None]
    path = p0 + (p1 - p0) * t
    off = np.sin(t * waves * 2 * math.pi + phase) * amp * np.sin(np.pi * np.clip(t * 1.0, 0, 1)) ** 0.5
    return path + off * np.asarray(axis, float)


def groove(g, positions, sig, amp, along=None):
    """sillons / bosses gaussiens (strands) sur une surface."""
    for c in positions:
        stamp(g, c, sig, amp, along=along)
    return g


def ngon_pts(cx, cy, cz, r, n, a0=0.0, plane='xz'):
    out = []
    for i in range(n):
        a = a0 + 2 * math.pi * i / n
        if plane == 'xz':
            out.append((cx + r * math.cos(a), cy, cz + r * math.sin(a)))
        else:
            out.append((cx + r * math.cos(a), cy + r * math.sin(a), cz))
    return out


def cbox(hx, hy, hz, top=1.0, c=(0, 0, 0)):
    """boîte simple (12 triangles) ; top = facteur d'échelle de la face haute en x,z (fût effilé)."""
    V = np.array([(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz),
                  (-hx * top, hy, -hz * top), (hx * top, hy, -hz * top), (hx * top, hy, hz * top), (-hx * top, hy, hz * top)], float)
    F = [(0, 1, 2, 3), (7, 6, 5, 4), (3, 2, 6, 7), (1, 0, 4, 5), (2, 1, 5, 6), (0, 3, 7, 4)]
    return Geo(V + np.array(c, float), F).fix()
