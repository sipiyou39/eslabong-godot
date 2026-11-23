"""Briques de textures de sol pour les arènes grecques (dalles, incrustations, zones d'équipe)."""
import math
import numpy as np
import tex as T
from tex import *


def slab_floor(c, S, palette, joint, vein, seed, vein_amt=0.4, joint_w=0.03, bevel_amt=0.16, grain=0.04, vein_scale=1.0, wear=0.3, tone=1.0):
    """dalles carrées S x S (appareil régulier) avec veines, biseau, joints. retourne (img, height, slab_id, edge_dist)."""
    X, Z = c.X, c.Z
    col = np.floor((X + 27.2) / S)
    row = np.floor((Z + 17.6) / S)
    u = (X + 27.2) / S - col
    v = (Z + 17.6) / S - row
    sid = hash01(col.astype(np.int64), row.astype(np.int64), seed)
    ed = np.minimum(np.minimum(u * S, (1 - u) * S), np.minimum(v * S, (1 - v) * S))
    cols = [hexc(p) for p in palette]
    base = np.zeros(X.shape + (3,), np.float32)
    k = (sid * len(cols)).astype(int) % len(cols)
    for i, cc in enumerate(cols):
        base[k == i] = cc
    n_big = fbm(X / 5.0, Z / 5.0, 4, seed + 1)
    n_mid = fbm(X * 1.1, Z * 1.1, 5, seed + 2)
    n_fine = fbm(X * 9, Z * 9, 4, seed + 3)
    base = base * (1 + (n_big[..., None] - 0.5) * 0.14 * wear * 2) * (1 + (n_mid[..., None] - 0.5) * 0.1 * wear * 2) * (1 + (n_fine[..., None] - 0.5) * 0.08)
    # veines : orientation et phase propres à chaque dalle
    ph = hash01(col.astype(np.int64), row.astype(np.int64), seed + 7) * 6.28
    ang = hash01(col.astype(np.int64), row.astype(np.int64), seed + 9) * 3.14
    w = fbm(X * 0.8 * vein_scale, Z * 0.8 * vein_scale, 5, seed + 4)
    vv = np.abs(np.sin((X * np.cos(ang) + Z * np.sin(ang)) * 1.6 * vein_scale + w * 4.0 + ph))
    vm = T.smooth(0.07, 0.0, vv) * T.smooth(0.4, 0.62, fbm(X * 1.6, Z * 1.6, 3, seed + 5))
    base = comp(base, hexc(vein), vm * vein_amt)
    base = base * tone
    bev = T.smooth(0.0, 0.1, ed)
    base = base * (1 - bevel_amt + bevel_amt * bev[..., None])
    jm = T.smooth(joint_w, joint_w * 0.35, ed)
    base = comp(base, hexc(joint), jm * 0.9)
    g = (np.random.default_rng(seed).random(X.shape).astype(np.float32) - 0.5) * grain
    base = base * (1 + g[..., None])
    h = (bev * 0.02 - jm * 0.02 + n_fine * 0.004).astype(np.float32)
    return base, h, sid, ed


def team_zones(c, img, em=None, left='#b0303a', right='#2f5fa8', em_left=None, em_right=None, a=0.8, worn=None, lines=True):
    X, Z = c.X, c.Z
    for sgn, col in ((-1, hexc(left)), (1, hexc(right))):
        cx = 19.0 * sgn
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.16), c.ring(cx, 0, 2.7, 0.07))
        for k in range(8):
            a0 = k * math.pi / 4
            z_ = np.maximum(z_, c.seg(cx + 2.7 * math.cos(a0), 0 + 2.7 * math.sin(a0), cx + 3.7 * math.cos(a0), 3.7 * math.sin(a0), 0.07))
        if lines:
            z_ = np.maximum(z_, c.dashed(13.0 * sgn, -12.5, 13.0 * sgn, 12.5, 0.13, 0.9, 0.45))
        if worn is not None:
            z_ = z_ * worn
        img = comp(img, col, z_ * a)
        if em is not None:
            ec = hexc(em_left if sgn < 0 else em_right) if (em_left or em_right) else col
            em = em + z_[..., None] * ec * 0.8
    return img, em


def sun_emblem(c, rings=((6.0, 0.30), (3.4, 0.16), (6.55, 0.08)), rays=12, r_in=0.9, r_mid=3.3, r_out=5.9):
    """médaillon central : anneaux + rayons de soleil (masque 0..1)."""
    X, Z = c.X, c.Z
    emb = np.zeros(X.shape, np.float32)
    for rad, w in rings:
        emb = np.maximum(emb, c.ring(0, 0, rad, w))
    R = np.hypot(X, Z)
    for k in range(rays):
        a0 = k * 2 * math.pi / rays
        perp = np.abs(-X * math.sin(a0) + Z * math.cos(a0))
        par = X * math.cos(a0) + Z * math.sin(a0)
        wd = 0.2 * (1 - np.clip((par - r_in) / (r_mid - r_in), 0, 1)) + 0.02
        emb = np.maximum(emb, T.smooth(wd + 0.015, wd - 0.015, perp) * ((par > r_in) & (par < r_mid)))
        if k % 2 == 0:
            wd2 = 0.16 * (1 - np.clip((par - 3.7) / (r_out - 3.7), 0, 1)) + 0.02
            emb = np.maximum(emb, T.smooth(wd2 + 0.015, wd2 - 0.015, perp) * ((par > 3.7) & (par < r_out)))
    emb = np.maximum(emb, c.circle(0, 0, 0.75))
    return emb


def edge_band(c, s, dep, gold, dark, w0=0.5, w1=0.95, sq=0.55):
    """frise de damier doré le long du mur (profondeur w0..w1)."""
    inside = T.smooth(w0 - 0.02, w0 + 0.02, dep) * T.smooth(w1 + 0.02, w1 - 0.02, dep)
    chk = (np.floor(s / sq) % 2) * (np.floor((dep - w0) / ((w1 - w0) / 2)) % 2)
    chk2 = ((np.floor(s / sq) + 1) % 2) * ((np.floor((dep - w0) / ((w1 - w0) / 2)) + 1) % 2)
    pat = np.clip(chk + chk2, 0, 1)
    return inside, pat


def finish_ground(name, img, h, em=None, nstr=3.0):
    save(name + '.png', img)
    save(name + '_n.png', to_normal(down(h, 2), nstr, MPP * 2))
    if em is not None:
        save(name + '_e.png', np.clip(em, 0, 1))
