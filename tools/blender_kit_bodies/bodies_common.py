"""Briques communes pour les corps (repère contrat : x gauche, y haut, z avant)."""
import numpy as np
from kitlib import *

PARTS = ["torso", "pelvis", "head", "arm_l", "arm_r", "leg_l", "leg_r"]
PV = {"torso": PIVOTS["torso"], "pelvis": PIVOTS["pelvis"], "head": PIVOTS["head"],
      "arm_l": PIVOTS["shoulder_l"], "arm_r": PIVOTS["shoulder_r"],
      "leg_l": PIVOTS["hip_l"], "leg_r": PIVOTS["hip_r"]}


def rows_loft(rows, n=16, e=2.3, cap0='fan', cap1='fan', k=None, warp=0.0):
    """rows : [(y, rx, rz, cz[, cx[, e]])] -> loft vertical ; k = nombre de lignes après rééchantillonnage."""
    if k:
        rows = resample_rows([tuple(list(r) + [0.0] * (5 - len(r))) if len(r) < 5 else tuple(r[:5]) for r in rows], k)
    rings = []
    for r in rows:
        y, rx, rz = r[0], max(r[1], 0.0), max(r[2], 0.0)
        cz = r[3] if len(r) > 3 else 0.0
        cx = r[4] if len(r) > 4 else 0.0
        ee = r[5] if len(r) > 5 else e
        if rx < 1e-6:
            rings.append(np.array([cx, y, cz]))
        else:
            rings.append(sec(y, rx, rz, cx, cz, n, ee, warp=warp))
    return loft(rings, cap0, cap1)


def eye_pair(cx, y, z, r=0.028, sep=0.07, col_ao=0.12, depth=0.0, sq=1.0):
    """deux petits yeux (parties sombres via AO forcé)."""
    out = []
    for sx in (-1, 1):
        g = sphere(r, r * sq, r * 0.8, n=10, m=6).t(cx + sx * sep, y, z)
        out.append(g)
    return out


def fist(c, hx=0.05, hy=0.053, hz=0.052, side=1, finger=True):
    """poing fermé autour d'un axe vertical ; c = centre. retourne liste de Geo."""
    cx, cy, cz = c
    out = [rbox(hx, hy, hz, r=0.022, s=2).t(cx, cy, cz)]
    if finger:
        for k, dy in enumerate((-0.68, -0.23, 0.23, 0.68)):
            f = rbox(hx * 0.92, hy * 0.2, hz * 0.45, r=0.01, s=1).t(cx, cy + dy * hy, cz + hz * 0.82)
            out.append(f)
    th = sphere(hx * 0.42, hy * 0.62, hz * 0.55, n=8, m=6).rz(-18 * side).t(cx - side * hx * 0.1, cy + hy * 0.95, cz + hz * 0.45)
    out.append(th)
    return out


def foot_boot(cx, base=0.0, length=0.30, width=0.07, h=0.11, back=0.075, toe_up=0.0, shape=(0.8, 0.9)):
    """pied/botte : retourne (corps, semelle, bout) géométries ; cx = x du pied ; pointe vers +Z."""
    zc = (length / 2) - back
    body = sphere(width, h * 0.52, length * 0.5, n=14, m=9, e=shape).t(cx, base + h * 0.5 + 0.01, zc)
    toe = sphere(width * 0.97, h * 0.42, length * 0.2, n=12, m=7).t(cx, base + h * 0.42 + 0.01, zc + length * 0.30)
    sole = rbox(width * 1.04, 0.017, length * 0.5, r=0.014, s=2).t(cx, base + 0.017, zc)
    return body, toe, sole


def limb(rows, n=12, e=2.0, cap0='fan', cap1='fan'):
    """rows [(y, rx, rz, cx, cz)] tube vertical qui peut dévier."""
    rings = []
    for r in rows:
        y, rx, rz = r[0], r[1], r[2]
        cx = r[3] if len(r) > 3 else 0.0
        cz = r[4] if len(r) > 4 else 0.0
        rings.append(sec(y, rx, rz, cx, cz, n, e))
    return loft(rings, cap0, cap1)


def zloft(rows, n=14, e=2.2, cap0='fan', cap1='fan'):
    """loft le long de Z : rows [(z, rx, ry, cy[, cx[, e]])] anneaux dans le plan XY."""
    rings = []
    for r in rows:
        z, rx, ry, cy = r[0], r[1], r[2], r[3]
        cx = r[4] if len(r) > 4 else 0.0
        ee = r[5] if len(r) > 5 else e
        if rx < 1e-6:
            rings.append(np.array([cx, cy, z]))
            continue
        t = 2 * np.pi * np.arange(n) / n
        p = 2.0 / ee
        x = cx + rx * np.sign(np.cos(t)) * np.abs(np.cos(t)) ** p
        y = cy + ry * np.sign(np.sin(t)) * np.abs(np.sin(t)) ** p
        rings.append(np.stack([x, y, np.full(n, z)], axis=1))
    return loft(rings, cap0, cap1)
