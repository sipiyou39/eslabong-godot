"""Briques communes du kit SCI-FI (DLC « Cosmos »). Réutilise tools/blender_kit_bodies (kitlib, bodies_common, gear_common, humanoid…).
Repère contrat : x = gauche du perso, y haut, z avant. Masque COLOR_0 : R primaire, G secondaire, B accent/lueur, reste = peau, A = AO."""
import os
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BODIES = os.path.join(ROOT, 'tools', 'blender_kit_bodies')
if BODIES not in sys.path:
    sys.path.insert(0, BODIES)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np                      # noqa: E402
from kitlib import *                    # noqa: E402,F401,F403
from bodies_common import *             # noqa: E402,F401,F403
from gear_common import *               # noqa: E402,F401,F403

KIT_DIR = os.path.join(ROOT, 'assets', 'models', 'kit')
PRE_DIR = os.path.join(KIT_DIR, 'preview_scifi')
DATA_DIR = os.path.join(ROOT, 'data', 'dlc')

LIMIT_TRI = 1500


def disc(r, y, n=14, h=0.012, e=2.0, cx=0.0, cz=0.0, r2=None):
    """petite galette verticale (axe Y) : r en bas, r2 en haut."""
    r2 = r if r2 is None else r2
    return rows_loft([(y, r, r, cz, cx), (y + h, r2, r2, cz, cx)], n=n, e=e, cap0='ngon', cap1='ngon')


def zdisc(cx, cy, z, r, depth=0.02, n=14, rx=None, ry=None, r2=1.0, e=2.0):
    """galette dont l'axe est Z (hublot, écran, lentille) : face avant à z+depth."""
    rx = r if rx is None else rx
    ry = r if ry is None else ry
    return zloft([(z, rx, ry, cy, cx, e), (z + depth, rx * r2, ry * r2, cy, cx, e)], n=n, e=e, cap0='ngon', cap1='ngon')


def xdisc(cx, cy, cz, r, depth=0.02, n=12, ry=None, rz=None):
    """galette d'axe X (oreille/disque latéral) : centrée en cx, épaisseur depth."""
    rz = r if rz is None else rz
    ry = r if ry is None else ry
    g = zloft([(0.0, ry, rz, 0.0, 0.0, 2.0), (depth, ry, rz, 0.0, 0.0, 2.0)], n=n, cap0='ngon', cap1='ngon')
    g.rot(1, 90).t(cx - depth / 2, cy, cz)
    return g


def bolts(pts, r=0.008, col=None):
    return [sphere(r, r * 0.8, r, n=6, m=4).t(*p) for p in pts]


def tube_pts(pts, r, n=8, e=2.0, caps=True, up=(0, 0, 1.0)):
    pts = np.asarray(pts, float)
    rad = [r] * len(pts) if np.isscalar(r) else r
    return tube(pts, rad, n=n, e=e, cap0='ngon' if caps else False, cap1='ngon' if caps else False, up=up)


def led_row(x0, x1, y, z, n=4, r=0.008, ax='x'):
    out = []
    for i in range(n):
        t = i / max(1, n - 1)
        x = x0 + (x1 - x0) * t
        out.append(sphere(r, r, r * 0.8, n=6, m=4).t(x, y, z))
    return out


def cyl_between(p0, p1, r0, r1=None, n=10, e=2.0, caps=True):
    """cylindre/cône entre deux points (extrémités plates)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    r1 = r0 if r1 is None else r1
    d = p1 - p0
    L = np.linalg.norm(d)
    g = lathe([(r0, 0.0), (r1, L)], n=n, e=e, cap='ngon' if caps else None)
    return g.aim(d).at(p0)


def cbox(c, size, ch=0.01, yaw=0.0, pitch=0.0, roll=0.0):
    """boîte à arêtes chanfreinées (44 triangles) centrée en c ; ch = chanfrein."""
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    ch = min(ch, 0.45 * min(size))
    if ch > 1e-4:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=ch, offset_type='OFFSET', segments=1, profile=0.5, affect='EDGES')
    bm.verts.index_update()
    V = np.array([tuple(v.co) for v in bm.verts], float)
    F = [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    g = Geo(V, F).fix()
    if roll:
        g.rz(roll)
    if pitch:
        g.rx(pitch)
    if yaw:
        g.ry(yaw)
    return g.t(*c)


def box_at(c, size, r=0.01, yaw=0.0, pitch=0.0, roll=0.0, s=1):
    """boîte arrondie/chanfreinée centrée en c (taille totale size). s>=2 : vraie boîte arrondie (lourde)."""
    if s >= 2:
        g = rbox(size[0] / 2, size[1] / 2, size[2] / 2, r=r, s=s)
        if roll:
            g.rz(roll)
        if pitch:
            g.rx(pitch)
        if yaw:
            g.ry(yaw)
        return g.t(*c)
    return cbox(c, size, ch=r, yaw=yaw, pitch=pitch, roll=roll)


def tri_count(part):
    return sum(pc.geo.tris() for pc in part.pieces)


def cube(c, size, yaw=0.0, pitch=0.0, roll=0.0):
    """boîte plate à 12 triangles (petits détails)."""
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    V = np.array([(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)], float)
    F = [(0, 1, 2, 3), (7, 6, 5, 4), (3, 2, 6, 7), (1, 0, 4, 5), (2, 1, 5, 6), (0, 3, 7, 4)]
    g = Geo(V, F).fix()
    if roll:
        g.rz(roll)
    if pitch:
        g.rx(pitch)
    if yaw:
        g.ry(yaw)
    return g.t(*c)


def ctube(pts, rad, m=2, n=6, e=2.0, caps=True, up=(0, 0, 1.0), taper=None):
    """tube suivant une spline passant par pts ; rad = scalaire, (rx,rz) ou liste de clés (scalaires/couples) interpolées le long du tracé."""
    path = curve(np.asarray(pts, float), m)
    L = len(path)
    if np.isscalar(rad):
        rr = [(rad, rad)] * L
    elif isinstance(rad, tuple) and len(rad) == 2 and np.isscalar(rad[0]):
        rr = [rad] * L
    else:
        keys = [(k, k) if np.isscalar(k) else k for k in rad]
        t = np.linspace(0, len(keys) - 1, L)
        rr = [(float(np.interp(x, range(len(keys)), [k[0] for k in keys])), float(np.interp(x, range(len(keys)), [k[1] for k in keys]))) for x in t]
    if taper is not None:
        rr = [(a * taper(i / max(1, L - 1)), b * taper(i / max(1, L - 1))) for i, (a, b) in enumerate(rr)]
    return tube(path, rr, n=n, e=e, cap0='ngon' if caps else False, cap1='ngon' if caps else False, up=up)
