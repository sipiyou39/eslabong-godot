"""Briques communes aux armes (poignées, pommeaux, gardes...)."""
import math
import numpy as np
from kitlib import *


def grip(y0, y1, r, color=R, seg=8, pitch=0.03, depth=0.13, sx=1.0, sz=1.0):
    """poignée cordée (alternance de crêtes)."""
    n = max(2, round((y1 - y0) / pitch))
    prof = [(r * (1 - depth), y0)]
    for i in range(n):
        a = y0 + (y1 - y0) * i / n
        b = y0 + (y1 - y0) * (i + 1) / n
        prof += [(r, a + (b - a) * 0.2), (r, a + (b - a) * 0.6), (r * (1 - depth), b)]
    return lathe(prof, seg, color, sx=sx, sz=sz)


def smooth_handle(y0, y1, r0, r1=None, color=R, seg=8, sx=1.0, sz=1.0, flare=0.0):
    r1 = r0 if r1 is None else r1
    return lathe([(r0 * (1 + flare), y0), (r0, y0 + 0.012), (r1, y1 - 0.012), (r1 * (1 + flare), y1)], seg, color, sx=sx, sz=sz,
                 bevel=0.003)


def quillons(y, half, thick_z=0.034, h=0.022, curve=0.03, droop=0.0, color=G, tip=None, n=8):
    """garde droite aux deux bras courbés vers la lame (curve>0) ou vers la poignée (curve<0)."""
    out = []
    for s in (1, -1):
        t = np.linspace(0, 1, n)
        pts = np.stack([s * (0.012 + t * half), y + curve * t ** 2 - droop * t, np.zeros(n)], 1)
        ring = np.array([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        out.append(sweep(pts, ring, scale=lambda u: (thick_z / 2 * (1 - 0.35 * u), h / 2 * (1 - 0.4 * u)), ref=(0, 0, 1),
                         color=color, bevel=0.004))
        if tip:
            out.append(sphere(tip, 8, 5, B if color == G else G, pos=pts[-1]))
    return out


def haft(y0, y1, r0, r1=None, bow=0.0, seg=8, color=R, n=8, bevel=None):
    """manche en bois, légèrement courbé (bow = flèche en Z)."""
    r1 = r0 if r1 is None else r1
    ys = np.linspace(y0, y1, n)
    t = np.linspace(0, 1, n)
    pts = np.stack([np.zeros(n), ys, bow * np.sin(np.pi * t)], 1)
    return tube(pts, r0 + (r1 - r0) * t, seg=seg, color=color, bevel=bevel)


def band(y, r, h=0.03, color=G, seg=10, flare=1.0, bevel=0.003, pos=(0, 0, 0)):
    return lathe([(r, y - h / 2), (r * flare, y - h / 2 + h * 0.2), (r * flare, y + h / 2 - h * 0.2), (r, y + h / 2)], seg, color, bevel=bevel).xf(pos=pos)


def studs(n, r, y, rs=0.008, color=B, z0=0.0):
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        out.append(sphere(rs, 5, 3, color, pos=(r * math.cos(a), y, r * math.sin(a))))
    return out


def axe_plate(poly, h, ins, body=G, edge=B, bevel=None):
    return plate(poly, h, ins, plane="YZ", color=body, edge_color=edge, bevel=bevel)
