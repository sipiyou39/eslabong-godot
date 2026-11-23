"""Briques communes aux props / invocations."""
import math
import numpy as np
from kitlib import *
from wcommon import *


def limb(p0, p1, r0, r1=None, color=R, seg=6, caps=True):
    r1 = r0 if r1 is None else r1
    out = [cyl(p0, p1, r0, r1, seg=seg, color=color)]
    if caps:
        out.append(sphere(r0, seg, 3, color, pos=p0))
        out.append(sphere(r1, seg, 3, color, pos=p1))
    return out


def body_loft(secs, seg=10, belly=K, top=R, side=None, bevel=None):
    """secs : (z, cy, rx, ry[, cx]) le long de +Z ; ventre en couleur 'belly'."""
    path = np.array([(s[4] if len(s) > 4 else 0.0, s[1], s[0]) for s in secs])
    sc = np.array([(s[2], s[3]) for s in secs])
    cols = []
    for i in range(seg):
        ph = (i + 0.5) * 2 * math.pi / seg
        up = -math.sin(ph)
        cols.append(top if up > -0.35 else belly)
    return sweep(path, circle2(seg), scale=sc, ref=(1, 0, 0), seg_colors=cols, bevel=bevel)


def leg(top, bottom, r0, r1, color=R, hoof=G, bend=0.0, seg=6, hoof_h=0.05, bend_dir=(0, 0, 1)):
    top, bottom = np.array(top, float), np.array(bottom, float)
    mid = (top + bottom) / 2 + np.array(bend_dir) * bend
    pts = bezier(top, (top + mid) / 2 + np.array(bend_dir) * bend * 0.4, (bottom + mid) / 2 + np.array(bend_dir) * bend * 0.4, bottom + np.array([0, hoof_h, 0]), 7)
    out = [tube(pts, np.linspace(r0, r1, 7), seg=seg, color=color)]
    out.append(cyl(bottom + np.array([0, hoof_h, 0]), bottom, r1 * 1.05, r1 * 1.3, seg=seg, color=hoof))
    return out


def spike_row(path_pts, h, r, color=G, tilt=(0, 0.2, -0.35), seg=4):
    out = []
    for pt in path_pts:
        d = np.array(tilt, float)
        d = d / np.linalg.norm(d)
        out.append(cyl(np.array(pt) - d * 0.005, np.array(pt) + d * h, r, 0.0, seg=seg, color=color))
    return out
from w_staffs import prongs
