"""Armes et invocations grecques (bibliothèque 'kitlib' du kit d'armes : faces colorées R/G/B/K + bevels).
Repère glTF : +Y haut, +Z avant. Armes : origine = prise en main ; invocations : sol y=0.
Les pièces s'enregistrent dans REG (nom, fonction, genre...)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
WEAPONS = os.path.join(ROOT, 'tools', 'blender_kit_weapons')
if WEAPONS not in sys.path:
    sys.path.insert(0, WEAPONS)
import numpy as np
from kitlib import *          # bibliothèque d'armes (celle-ci doit être le module 'kitlib' courant)
from wcommon import grip, band, haft, smooth_handle, studs
from w_shields import face, back_handle

REG = []


def piece(name, kind='weapon', accent=None, notes='', views='side,tq', ao=0.10, pair=False):
    def deco(fn):
        REG.append(dict(name=name, fn=fn, kind=kind, accent=accent, notes=notes, views=views, ao=ao))
        return fn
    return deco


GOLD = (1.0, 0.82, 0.3)


def zig(base, up, side, length, amp, n, r0, r1, color=B, seg=4):
    """éclair en zigzag : n segments de `base` vers `up` (unité), décalés alternativement le long de `side`."""
    base, up, side = (np.asarray(v, float) for v in (base, up, side))
    pts = [base]
    for k in range(1, n + 1):
        t = k / n
        sgn = 1 if k % 2 else -1
        off = amp * (1.0 - 0.45 * t) * (0 if k == n else sgn)
        pts.append(base + up * length * t + side * off)
    out = []
    for k in range(n):
        ra = r0 + (r1 - r0) * k / n
        rb = r0 + (r1 - r0) * (k + 1) / n
        out.append(cyl(pts[k], pts[k + 1], ra, rb, seg=seg, color=color, phase=45))
        if k < n - 1:
            out.append(sphere(rb * 1.02, seg + 2, 3, color, pos=pts[k + 1]))
    return out


@piece('wpn_thunderbolt', accent=GOLD, notes="foudre de Zeus 1,0 m : poignée centrale, trois éclairs en zigzag vers +Y, trois pointes courtes vers -Y")
def thunderbolt():
    p = []
    p.append(grip(-0.085, 0.085, 0.022, color=R, pitch=0.034))
    p.append(lathe([(0.02, 0.085), (0.036, 0.1), (0.04, 0.125), (0.026, 0.14)], 10, B, bevel=0.003))
    p.append(lathe([(0.02, -0.085), (0.036, -0.1), (0.04, -0.125), (0.026, -0.14)], 10, B, bevel=0.003))
    p.append(band(0.0, 0.0245, 0.026, G))
    p.append(sphere(0.03, 8, 5, G, pos=(0, 0.14, 0)))
    p.append(sphere(0.03, 8, 5, G, pos=(0, -0.14, 0)))
    # éclair central + deux éclairs latéraux (éventail)
    p += zig((0, 0.14, 0), (0, 1, 0), (0, 0, 1), 0.62, 0.12, 4, 0.036, 0.008)
    for s_ in (1, -1):
        up = np.array([s_ * 0.55, 1.0, 0.0])
        up /= np.linalg.norm(up)
        p += zig((s_ * 0.014, 0.15, 0), up, (0, 0, 1), 0.44, 0.09, 3, 0.028, 0.007)
    # pointes basses
    p += zig((0, -0.14, 0), (0, -1, 0), (0, 0, 1), 0.24, 0.06, 2, 0.028, 0.008)
    for s_ in (1, -1):
        up = np.array([s_ * 0.55, -1.0, 0.0])
        up /= np.linalg.norm(up)
        p += zig((s_ * 0.01, -0.145, 0), up, (0, 0, 1), 0.2, 0.05, 2, 0.022, 0.007)
    # petites ailes à la garde
    for s in (1, -1):
        w = plate([(0.0, 0.0), (0.05, 0.03), (0.11, 0.07), (0.16, 0.07), (0.12, 0.035), (0.17, 0.025), (0.12, 0.0), (0.15, -0.025), (0.06, -0.02)],
                  0.006, 0.0, plane="XY", color=G, edge_color=G)
        p.append(w.xf(pos=(s * 0.03, 0.0, 0.0), s=(s, 1, 1)))
    return p


@piece('wpn_trident', accent=GOLD, notes="trident de Poséidon 2,05 m : trois dents barbelées dorées, hampe cannelée")
def trident():
    p = []
    p.append(haft(-0.5, 0.92, 0.0215, 0.023, bow=0.0, seg=7, n=6))
    p.append(grip(-0.14, 0.14, 0.0255, pitch=0.036))
    p.append(cone(0.022, 0.1, 6, G, pos=(0, -0.5, 0.0), rot=(180, 0, 0)))
    p.append(band(-0.4, 0.0245, 0.03, G))
    p.append(band(0.4, 0.0245, 0.03, B))
    # douille + traverse
    p.append(lathe([(0.0225, 0.88), (0.04, 0.94), (0.044, 1.0), (0.034, 1.06), (0.026, 1.1)], 10, B, bevel=0.003))
    p.append(sphere(0.034, 8, 5, G, pos=(0, 0.93, 0)))
    # dent centrale (fer en feuille)
    p.append(cyl((0, 1.08, 0), (0, 1.25, 0), 0.02, 0.016, seg=8, color=B, bevel=0.002))
    keys = [(1.22, 0.034, 0.012), (1.3, 0.055, 0.0135), (1.38, 0.05, 0.013), (1.46, 0.03, 0.01), (1.53, 0.012, 0.005), (1.58, 0, 0)]
    p.append(blade(keys, ring_blade(e=0.2, bev=0.45), n_sub=1))
    # dents latérales courbes
    for s in (1, -1):
        pts = bezier((s * 0.02, 1.06, 0), (s * 0.15, 1.08, 0), (s * 0.19, 1.2, 0), (s * 0.17, 1.34, 0), 9)
        p.append(tube(pts, np.linspace(0.02, 0.012, 9), seg=5, color=B))
        keys = [(0.0, 0.026, 0.011), (0.07, 0.04, 0.0125), (0.15, 0.03, 0.01), (0.22, 0.012, 0.005), (0.26, 0, 0)]
        b = blade([(1.33 + k[0], k[1], k[2]) for k in keys], ring_blade(e=0.2, bev=0.45), n_sub=1)
        p.append(b.xf(pos=(s * 0.17, 0, 0)).xf(pos=(0, 0, 0), rot=(0, 0, 0)))
        # barbillons
        p.append(cone(0.013, 0.07, 4, B, pos=(s * 0.172, 1.38, 0), rot=(0, 0, s * 38)))
    for s in (1, -1):
        p.append(cone(0.014, 0.075, 4, B, pos=(s * 0.016, 1.34, 0), rot=(0, 0, -s * 40)))
    p.append(sphere(0.02, 6, 4, G, pos=(0, 1.1, 0.0), s=(1.0, 0.8, 1.0)))
    return p


@piece('wpn_bident', accent=(0.55, 0.9, 0.6), notes="bident d'Hadès 1,95 m : deux dents sombres, pointes vertes")
def bident():
    p = []
    p.append(haft(-0.45, 0.9, 0.02, 0.022, bow=0.0, seg=7, color=G, n=6))
    p.append(grip(-0.13, 0.13, 0.0245, pitch=0.034, color=G))
    p.append(cone(0.021, 0.09, 6, B, pos=(0, -0.45, 0.0), rot=(180, 0, 0)))
    p.append(band(-0.37, 0.0235, 0.03, B))
    p.append(band(0.45, 0.0235, 0.03, R))
    p.append(lathe([(0.0215, 0.86), (0.042, 0.92), (0.046, 0.98), (0.036, 1.04), (0.027, 1.08)], 10, R, bevel=0.003))
    p.append(sphere(0.038, 8, 5, G, pos=(0, 0.92, 0)))
    for s in (1, -1):
        pts = bezier((s * 0.015, 1.04, 0), (s * 0.14, 1.07, 0), (s * 0.16, 1.2, 0), (s * 0.095, 1.36, 0), 9)
        p.append(tube(pts, np.linspace(0.021, 0.012, 9), seg=5, color=G))
        keys = [(0.0, 0.03, 0.012), (0.08, 0.036, 0.013), (0.17, 0.026, 0.01), (0.25, 0.01, 0.005), (0.3, 0, 0)]
        b = blade([(1.34 + k[0], k[1], k[2]) for k in keys], ring_blade(e=0.2, bev=0.45), n_sub=1)
        p.append(b.xf(pos=(s * 0.09, 0, 0), rot=(0, 0, -s * 6)))
        p.append(cone(0.013, 0.075, 4, B, pos=(s * 0.11, 1.4, 0.0), rot=(0, 0, s * 42)))
    p.append(gem(0.02, 0.05, 6, B, pos=(0, 1.12, 0.0)))
    return p


@piece('wpn_lyre', accent=GOLD, notes="lyre dorée 0,5 m, centrée sur l'origine, cordes face +Z, dos -Z (main gauche, style lancer)", views="front,tq", ao=0.12)
def lyre():
    p = []
    for s in (1, -1):
        pts = bezier((s * 0.085, -0.13, 0), (s * 0.2, -0.08, 0), (s * 0.235, 0.12, 0), (s * 0.15, 0.27, 0), 14)
        p.append(tube(pts, np.linspace(0.02, 0.013, 14), seg=6, color=B))
        # volute
        p.append(torus(0.024, 0.008, 10, 4, plane="XY", pos=(s * 0.126, 0.285, 0), color=B))
        p.append(sphere(0.018, 6, 4, R, pos=(s * 0.15, 0.27, 0)))
    p.append(cyl((-0.15, 0.27, 0), (0.15, 0.27, 0), 0.013, 0.013, seg=8, color=B, bevel=0.002).xf(rot=(0, 0, 0)))
    p.append(cyl((-0.17, 0.27, 0), (-0.14, 0.27, 0), 0.02, 0.02, seg=8, color=R))
    p.append(cyl((0.14, 0.27, 0), (0.17, 0.27, 0), 0.02, 0.02, seg=8, color=R))
    # caisse de résonance : coque dorée, table de résonance, ouïes en croissant, soleil
    p.append(sphere(0.115, 12, 7, B, pos=(0, -0.145, -0.005), s=(1.05, 0.95, 0.5)))
    p.append(sphere(0.088, 12, 7, R, pos=(0, -0.145, 0.0), s=(1.0, 0.92, 0.5)).xf(pos=(0, 0, 0.02)))
    for s_ in (1, -1):
        p.append(sphere(0.012, 6, 4, G, pos=(s_ * 0.06, -0.135, 0.062), s=(1, 3.2, 0.3)))
    p.append(sphere(0.02, 8, 5, B, pos=(0, -0.145, 0.066), s=(1, 1, 0.4)))
    p.append(box((0.1, 0.012, 0.014), (0, -0.215, 0.05), color=B, bevel=0.003))
    # cordes
    for i in range(7):
        x = -0.1 + 0.2 * i / 6
        xb = x * 0.55
        p.append(cyl((x, 0.27, 0.012), (xb, -0.2, 0.052), 0.0032, 0.0032, seg=3, color=G))
    return p


@piece('wpn_bow_golden', accent=GOLD, notes="arc doré d'Artémis/Apollon 1,45 m ; branches le long de Y, ventre +Z, corde -Z")
def bow_golden():
    p = []
    half, depth, k, n = 0.72, 0.19, 2.2, 15
    t = np.linspace(-1, 1, n)
    y = half * t
    z = -depth * (t ** 2 * (1 + k) - k * t ** 4)
    path = np.stack([np.zeros(n), y, z], 1)
    s = np.abs(t)
    sx = 0.026 + (0.011 - 0.026) * s ** 1.3
    sz = 0.02 + (0.009 - 0.02) * s ** 1.3
    sx = sx * (1 + 0.35 * np.exp(-(t / 0.1) ** 2))
    p.append(sweep(path, circle2(6), scale=np.stack([sx, sz], 1), ref=(1, 0, 0), color=B))
    p.append(lathe([(0.021, -0.085), (0.026, -0.072), (0.026, 0.072), (0.021, 0.085)], 8, R, bevel=0.002))
    p.append(band(0.1, 0.027, 0.022, G, seg=8))
    p.append(band(-0.1, 0.027, 0.022, G, seg=8))
    for sg in (1, -1):
        for tt in (0.45, 0.72):
            zz = -depth * (tt ** 2 * (1 + k) - k * tt ** 4)
            p.append(band(0.0, 0.0155, 0.014, R, seg=8).xf(pos=(0, sg * half * tt, zz), rot=(sg * 14 + 0, 0, 0)))
    tipz = z[-1]
    for sg, i in ((1, -1), (-1, 0)):
        tp = path[i]
        p.append(sphere(0.016, 6, 4, B, pos=tp + np.array([0, sg * 0.006, 0.0]), s=(0.8, 1.3, 0.9)))
        p.append(cone(0.011, 0.05, 5, B, pos=tp + np.array([0, sg * 0.02, 0.0]), rot=(0 if sg > 0 else 180, 0, 0)))
    a, b = path[0], path[-1]
    p.append(tube([a, (a + b) / 2 + np.array([0, 0, -0.004]), b], 0.0055, seg=4, color=G))
    # motif solaire sur le repose-flèche
    p.append(face(lathe([(0.0, 0.0), (0.03, 0.0), (0.03, 0.012), (0.0, 0.014)], 12, B), 0.0).xf(pos=(0, 0.12, 0.012)))
    for kk in range(6):
        a_ = math.radians(60 * kk)
        p.append(cone(0.007, 0.03, 4, B, pos=(0, 0, 0), rot=(0, 0, 0)).xf(pos=(0, 0.032, 0)).xf(rot=(0, 0, -60 * kk)).xf(pos=(0, 0.12, 0.014)))
    p.append(box((0.02, 0.05, 0.026), (0.0, 0.07, 0.012), color=G, bevel=0.003) if False else sphere(0.012, 6, 4, G, pos=(0, 0.0, 0.03)))
    return p


@piece('wpn_kopis', accent=GOLD, notes="kopis 0,85 m : lame courbée vers l'avant (+Z), tranchant côté concave, manche à tête d'oiseau")
def kopis():
    p = []
    p.append(grip(-0.075, 0.07, 0.019, pitch=0.03))
    # pommeau à bec d'oiseau (courbé vers l'arrière)
    pts = bezier((0, -0.07, 0), (0, -0.1, -0.02), (0, -0.115, -0.07), (0, -0.075, -0.115), 8)
    p.append(tube(pts, np.linspace(0.02, 0.014, 8), seg=7, color=B))
    p.append(sphere(0.021, 7, 4, B, pos=(0, -0.075, -0.115), s=(0.9, 1.0, 1.2)))
    p.append(cone(0.012, 0.04, 5, G, pos=(0, -0.078, -0.14), rot=(-80, 0, 0)))
    p.append(sphere(0.007, 5, 3, G, pos=(0.013, -0.068, -0.115)))
    p.append(sphere(0.007, 5, 3, G, pos=(-0.013, -0.068, -0.115)))
    p.append(box((0.03, 0.032, 0.05), (0, 0.082, 0.0), color=B, bevel=0.005))
    p.append(box((0.07, 0.014, 0.022), (0, 0.1, 0.0), color=G, bevel=0.003))
    for s in (1, -1):
        p.append(sphere(0.011, 5, 3, B, pos=(s * 0.036, 0.1, 0)))
    L = 0.72
    y0 = 0.1
    ks = [(0.0, 0.03, 0.0105), (0.28, 0.036, 0.0105), (0.5, 0.047, 0.0105), (0.68, 0.052, 0.0098), (0.82, 0.044, 0.0085), (0.93, 0.024, 0.0055), (0.985, 0.008, 0.003), (1.0, 0, 0)]
    keys = [(y0 + a * L, w, t) for a, w, t in ks]
    p.append(blade(keys, ring_sabre(), bend=lambda y: 0.17 * ((y - y0) / L) ** 2.0, n_sub=3))
    return p


@piece('wpn_spear_greek', accent=GOLD, notes="dory 2,1 m : lance à fer en feuille de bronze, talon (sauroter), bandes")
def spear_greek():
    p = []
    p.append(haft(-0.5, 1.0, 0.02, 0.021, bow=0.0, seg=8, n=6))
    p.append(grip(-0.12, 0.14, 0.0245, pitch=0.034))
    p.append(cone(0.02, 0.14, 4, G, pos=(0, -0.5, 0.0), rot=(180, 0, 0)))
    p.append(lathe([(0.02, -0.4), (0.034, -0.37), (0.03, -0.32), (0.021, -0.29)], 8, B, bevel=0.003))
    p.append(band(-0.2, 0.0235, 0.03, G))
    p.append(band(0.5, 0.0235, 0.028, B))
    p.append(lathe([(0.021, 0.96), (0.03, 1.0), (0.034, 1.06), (0.025, 1.12)], 8, B, bevel=0.003))
    keys = [(1.08, 0.03, 0.013), (1.15, 0.062, 0.016), (1.24, 0.075, 0.0165), (1.33, 0.056, 0.0135), (1.41, 0.03, 0.01), (1.47, 0.011, 0.005), (1.5, 0, 0)]
    p.append(blade(keys, ring_blade(e=0.18, bev=0.4, fuller=0.0), n_sub=2))
    p.append(cyl((0, 1.1, 0), (0, 1.36, 0), 0.0075, 0.0065, seg=4, color=G, bevel=None))
    for k in range(6):
        ar = math.radians(60 * k)
        p0 = (0.024 * math.cos(ar), 0.94, 0.024 * math.sin(ar))
        p1 = (0.065 * math.cos(ar), 0.84, 0.065 * math.sin(ar))
        p.append(cyl(p0, p1, 0.011, 0.004, seg=4, color=R))
    return p


@piece('wpn_caduceus', accent=GOLD, notes="caducée d'Hermès 1,5 m : bâton doré, deux serpents entrelacés, petites ailes", views="side,front")
def caduceus():
    p = []
    p.append(haft(-0.6, 0.9, 0.02, 0.021, bow=0.0, seg=8, color=B))
    p.append(grip(-0.1, 0.12, 0.024, pitch=0.034, color=R))
    p.append(cone(0.02, 0.08, 6, G, pos=(0, -0.6, 0.0), rot=(180, 0, 0)))
    p.append(band(-0.5, 0.0235, 0.03, G))
    p.append(sphere(0.045, 9, 6, B, pos=(0, 0.95, 0)))
    for ph in (0.0, math.pi):
        pts = []
        N = 22
        for i in range(N):
            t = i / (N - 1)
            ang = ph + 2 * math.pi * 2.3 * t
            r = 0.05 * (1 - 0.0 * t) * (1.0 if t < 0.8 else 1.0 - 0.9 * (t - 0.8) / 0.2) + 0.0
            pts.append((r * math.cos(ang), 0.22 + 0.66 * t, r * math.sin(ang)))
        rad = np.linspace(0.016, 0.012, N)
        p.append(tube(np.array(pts), rad, seg=6, color=G))
    for s in (1, -1):
        p.append(sphere(0.022, 7, 5, G, pos=(s * 0.056, 0.91, 0.0), s=(1.0, 0.9, 1.3)))
        p.append(sphere(0.006, 4, 3, B, pos=(s * 0.056, 0.92, 0.024)))
        wing = plate([(0.0, 0.0), (0.06, 0.04), (0.15, 0.09), (0.25, 0.11), (0.31, 0.1), (0.25, 0.07), (0.32, 0.055), (0.24, 0.03), (0.3, 0.005), (0.2, 0.0), (0.12, -0.02), (0.03, -0.02)],
                     0.007, 0.0, plane="XY", color=B, edge_color=B)
        p.append(wing.xf(pos=(s * 0.03, 0.95, 0.0), s=(s, 1, 1), rot=(0, 0, 0)))
    return p


def gorgon_face(z0=0.0, scale=1.0, snakes=10):
    p = []
    S = scale
    p.append(sphere(0.12 * S, 10, 6, K, pos=(0, 0.0, z0 + 0.03 * S), s=(1.0, 1.05, 0.5)))
    for sx in (-1, 1):
        p.append(sphere(0.034 * S, 8, 5, G, pos=(sx * 0.052 * S, 0.03 * S, z0 + 0.085 * S), s=(1, 1, 0.45)))
        p.append(sphere(0.016 * S, 6, 4, B, pos=(sx * 0.052 * S, 0.03 * S, z0 + 0.098 * S), s=(1, 1, 0.5)))
        p.append(box((0.07 * S, 0.014 * S, 0.02 * S), (sx * 0.054 * S, 0.075 * S, z0 + 0.082 * S), rot=(0, 0, -sx * 16), color=G, bevel=0.003))
        p.append(cone(0.011 * S, 0.04 * S, 4, B, pos=(sx * 0.026 * S, -0.058 * S, z0 + 0.095 * S), rot=(180, 0, 0)))
    p.append(sphere(0.026 * S, 6, 4, K, pos=(0, -0.012 * S, z0 + 0.105 * S), s=(1, 1.2, 0.8)))
    p.append(box((0.1 * S, 0.026 * S, 0.02 * S), (0, -0.062 * S, z0 + 0.092 * S), color=G, bevel=0.004))
    p.append(box((0.026 * S, 0.05 * S, 0.016 * S), (0, -0.095 * S, z0 + 0.09 * S), color=R, bevel=0.003))
    for k in range(snakes):
        a = 2 * math.pi * (k + 0.5) / snakes + math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        pa, pb = np.array([-sa, ca]), np.array([ca, sa])
        wob = 0.05 * S * (1 if k % 2 else -1)
        r0, r1 = 0.09 * S, 0.3 * S
        pts = [np.array([pb[0] * r + pa[0] * wob * math.sin(math.pi * (r - r0) / (r1 - r0) * 1.5), pb[1] * r + pa[1] * wob * math.sin(math.pi * (r - r0) / (r1 - r0) * 1.5), z0 + 0.045 * S + 0.02 * S * (r - r0) / (r1 - r0)])
               for r in np.linspace(r0, r1, 6)]
        p.append(tube(np.array(pts), np.linspace(0.021 * S, 0.01 * S, 6), seg=4, color=G, cap1=True))
        hd = pts[-1] + np.array([pb[0], pb[1], 0.0]) * 0.012 * S
        p.append(sphere(0.019 * S, 5, 3, G, pos=hd, s=(1, 1, 0.8)))
    return p


@piece('wpn_shield_aegis', accent=GOLD, notes="bouclier de l'égide 0,8 m, face +Z : tête de Gorgone en relief et serpents", views="front,tq", ao=0.1)
def shield_aegis():
    p = []
    prof = [(0, -0.012), (0.2, -0.014), (0.37, -0.022), (0.37, 0.012), (0.2, 0.026), (0.09, 0.034), (0.0, 0.036)]
    p.append(face(lathe(prof, 16, R)))
    p.append(torus(0.37, 0.02, 18, 4, plane="XY", color=B, pos=(0, 0, -0.004)))
    p += gorgon_face(0.03, 1.0, 6)
    p += back_handle(0.14, -0.045, 0.0)
    return p


@piece('wpn_shield_hoplon', accent=GOLD, notes="hoplon 0,9 m, face +Z : grand bouclier rond de bronze bombé, bord large, lambda doré", views="front,tq", ao=0.1)
def shield_hoplon():
    p = []
    prof = [(0, -0.02), (0.2, -0.026), (0.34, -0.04), (0.43, -0.026), (0.43, 0.018), (0.37, 0.04), (0.2, 0.054), (0.0, 0.058)]
    p.append(face(lathe(prof, 20, R)))
    p.append(face(lathe([(0.375, 0.0), (0.44, 0.0), (0.44, 0.03), (0.4, 0.045), (0.375, 0.035)], 20, G, bevel=0.002), 0.002))
    p.append(torus(0.44, 0.014, 22, 4, plane="XY", color=B, pos=(0, 0, 0.012)))
    # lambda doré
    for s in (1, -1):
        p.append(box((0.07, 0.34, 0.016), (s * 0.075, 0.0, 0.07), rot=(0, 0, s * 22), color=B, bevel=0.004))
    p.append(box((0.1, 0.05, 0.016), (0.0, 0.17, 0.074), color=B, bevel=0.003))
    p.append(face(lathe([(0.0, 0.0), (0.075, 0.0), (0.08, 0.025), (0.05, 0.055), (0.0, 0.065)], 14, G, bevel=0.002), 0.058).xf(pos=(0, -0.0, 0)))
    p.append(sphere(0.022, 6, 4, B, pos=(0, 0, 0.128)))
    for k in range(8):
        a = math.radians(45 * k + 22.5)
        p.append(sphere(0.012, 4, 2, B, pos=(0.34 * math.cos(a), 0.34 * math.sin(a), 0.032)))
    p += back_handle(0.16, -0.05, 0.0)
    return p


# ---------------------------------------------------------------------------------------- invocations
@piece('summon_shade', kind='prop', accent=(0.5, 0.95, 0.85), notes="ombre / spectre d'Hadès : revenant à capuche flottant, 1,8 m, yeux, rune et éclats en accent B", views="tq,side", ao=0.2)
def shade():
    p = []
    # robe effilée qui se défait en lambeaux ondulants
    prof = [(0.02, 0.42), (0.1, 0.5), (0.2, 0.66), (0.25, 0.88), (0.22, 1.1), (0.18, 1.25), (0.15, 1.36), (0.1, 1.41)]
    p.append(lathe(prof, 10, R, sz=0.8, cap=False))
    for k in range(8):
        a = 2 * math.pi * k / 8 + 0.2
        c, s_ = math.cos(a), math.sin(a)
        L = 0.45 + 0.22 * (0.5 + 0.5 * math.sin(k * 2.3))
        b0 = np.array([0.12 * c, 0.52, 0.1 * s_])
        pts = bezier(b0, b0 + np.array([0.08 * c, -L * 0.35, 0.07 * s_ + 0.05]), b0 + np.array([0.02 * c + 0.06, -L * 0.7, 0.06 * s_ - 0.06]), b0 + np.array([0.1 * c, -L, 0.08 * s_]), 6)
        p.append(tube(pts, np.linspace(0.06, 0.004, 6), seg=4, color=G if k % 2 else R))
    # tête sous capuche pointue
    p.append(sphere(0.155, 10, 7, R, pos=(0, 1.55, -0.01), s=(0.95, 1.12, 1.0)))
    p.append(cone(0.14, 0.26, 7, R, pos=(0, 1.62, -0.08), rot=(-40, 0, 0)))
    p.append(sphere(0.105, 9, 6, G, pos=(0, 1.53, 0.075), s=(0.95, 1.05, 0.7)))
    for s_ in (1, -1):
        p.append(sphere(0.03, 6, 4, B, pos=(s_ * 0.05, 1.54, 0.128), s=(1.0, 1.4, 0.6)))
    p.append(box((0.07, 0.016, 0.02), (0, 1.465, 0.14), color=B, bevel=0.003))
    # épaules, bras tendus, manches en lambeaux, mains osseuses
    p.append(sphere(0.2, 10, 6, R, pos=(0, 1.3, -0.01), s=(1.1, 0.45, 0.75)))
    p.append(gem(0.03, 0.08, 4, B, pos=(0, 1.0, 0.2), rot=(90, 0, 0)))
    for s_ in (1, -1):
        sh = np.array([s_ * 0.2, 1.28, 0.0])
        el = np.array([s_ * 0.27, 1.05, 0.15])
        hd = np.array([s_ * 0.22, 1.0, 0.42])
        p.append(cyl(sh, el, 0.05, 0.04, seg=6, color=R))
        p.append(cyl(el, hd, 0.04, 0.025, seg=6, color=R))
        for j in range(3):
            base = el + np.array([s_ * 0.0, -0.03, 0.03 * (j - 1)])
            p.append(cyl(base, base + np.array([s_ * 0.05, -0.38 - 0.06 * j, 0.02]), 0.04, 0.0, seg=4, color=G if j % 2 else R))
        p.append(sphere(0.032, 6, 4, K, pos=hd + np.array([0, 0.0, 0.03]), s=(0.8, 0.6, 1.2)))
        for j in (-1, 0, 1):
            p.append(cone(0.007, 0.07, 3, K, pos=hd + np.array([j * 0.017, -0.005, 0.06]), rot=(90, 0, 0)))
    for k in range(5):
        a = math.radians(72 * k + 15)
        p.append(gem(0.018, 0.06, 4, B, pos=(0.4 * math.cos(a), 0.7 + 0.5 * ((k * 3) % 5) / 4, 0.4 * math.sin(a)), rot=(10 * k, 0, 15)))
    return p


@piece('summon_owl', kind='prop', accent=(1.0, 0.8, 0.25), notes="chouette d'Athéna en vol, envergure 1,05 m, centre du corps à y=0,65, regarde +Z", views="tq,front", ao=0.14)
def owl():
    p = []
    cy = 0.65
    p.append(sphere(0.1, 10, 7, R, pos=(0, cy, 0), s=(0.95, 1.3, 0.9), rot=(-12, 0, 0)))
    p.append(sphere(0.085, 9, 6, K, pos=(0, cy - 0.01, 0.045), s=(0.85, 1.15, 0.5), rot=(-12, 0, 0)))
    for k in range(3):
        p.append(box((0.07, 0.012, 0.012), (0, cy + 0.04 - 0.04 * k, 0.083 - 0.01 * k), color=R, bevel=0.002))
    # tête + disque facial + oreilles
    p.append(sphere(0.088, 10, 7, R, pos=(0, cy + 0.15, 0.03), s=(1.08, 0.92, 0.95)))
    for s in (1, -1):
        p.append(sphere(0.055, 8, 5, K, pos=(s * 0.043, cy + 0.15, 0.085), s=(1, 1, 0.4)))
        p.append(sphere(0.03, 8, 5, B, pos=(s * 0.043, cy + 0.155, 0.103), s=(1, 1, 0.55)))
        p.append(sphere(0.014, 6, 4, G, pos=(s * 0.043, cy + 0.155, 0.12), s=(1, 1, 0.5)))
        p.append(cone(0.024, 0.08, 4, R, pos=(s * 0.055, cy + 0.215, 0.0), rot=(-8, 0, -s * 18)))
    p.append(cone(0.016, 0.045, 4, G, pos=(0, cy + 0.14, 0.11), rot=(115, 0, 0)))
    # ailes déployées (bord de fuite en plumes)
    for s in (1, -1):
        poly = [(0.07, 0.07), (0.2, 0.12), (0.36, 0.14), (0.52, 0.1), (0.54, -0.02), (0.5, -0.1), (0.46, -0.03), (0.43, -0.16), (0.37, -0.07), (0.33, -0.2),
                (0.26, -0.09), (0.2, -0.19), (0.14, -0.08), (0.07, -0.1)]
        pl = plate([(x * s, z) for x, z in poly], 0.008, 0.0, plane="XZ", color=R, edge_color=R)
        p.append(pl.xf(rot=(0, 0, s * 14), pos=(0, cy + 0.04, -0.03)))
        poly2 = [(0.08, 0.06), (0.2, 0.09), (0.3, 0.08), (0.34, 0.0), (0.28, -0.04), (0.2, -0.02), (0.12, -0.04)]
        pl2 = plate([(x * s, z) for x, z in poly2], 0.011, 0.0, plane="XZ", color=G, edge_color=G)
        p.append(pl2.xf(rot=(0, 0, s * 14), pos=(0, cy + 0.052, -0.02)))
        for k, (x, z) in enumerate([(0.54, -0.02), (0.46, -0.03), (0.37, -0.07), (0.26, -0.09)]):
            pt = np.array([x * s, 0.0, z]) @ rotmat(0, 0, s * 14).T + np.array([0, cy + 0.04, -0.03])
            p.append(sphere(0.012, 4, 3, K, pos=pt))
    # queue en éventail + serres repliées
    tail = plate([(-0.07, 0.0), (0.07, 0.0), (0.1, -0.2), (0.05, -0.23), (0.0, -0.21), (-0.05, -0.23), (-0.1, -0.2)], 0.008, 0.0, plane="XZ", color=R, edge_color=G)
    p.append(tail.xf(rot=(-18, 0, 0), pos=(0, cy - 0.1, -0.06)))
    for s in (1, -1):
        p.append(cyl((s * 0.04, cy - 0.12, 0.03), (s * 0.04, cy - 0.2, 0.07), 0.016, 0.012, seg=5, color=K))
        for j in (-1, 0, 1):
            p.append(cone(0.007, 0.04, 3, G, pos=(s * 0.04 + j * 0.013, cy - 0.2, 0.07), rot=(120, 0, 0)))
    return p
