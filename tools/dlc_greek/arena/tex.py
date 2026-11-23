"""Bibliothèque de textures procédurales (numpy). À exécuter avec le python du venv du projet."""
import math
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEXDIR = ROOT + "/assets/textures/arena"
os.makedirs(TEXDIR, exist_ok=True)

GX0, GX1 = -26.5, 26.5
GZ0, GZ1 = -16.5625, 16.5625
GW, GH = 2048, 1280
MPP = (GX1 - GX0) / GW

OBST = [(-9, -6, 1.4), (9, -6, 1.4), (-9, 6, 1.4), (9, 6, 1.4), (0, -10.5, 1.2), (0, 10.5, 1.2)]
TORCH = [(-24.5, -14.5), (-12, -15.4), (0, -15.4), (12, -15.4), (24.5, -14.5),
         (-24.5, 14.5), (-12, 15.4), (0, 15.4), (12, 15.4), (24.5, 14.5)]


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


def save(name, arr):
    a = np.clip(arr, 0, 1)
    a = (a * 255 + 0.5).astype(np.uint8)
    if a.ndim == 3 and a.shape[2] == 1:
        a = a[:, :, 0]
    Image.fromarray(a).save(os.path.join(TEXDIR, name), optimize=True)
    print('texture', name, a.shape)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    a = np.asarray(a, np.float32)
    b = np.asarray(b, np.float32)
    t = np.asarray(t, np.float32)
    if t.ndim == 2:
        t = t[..., None]
    return a + (b - a) * t


def hash01(ix, iy, seed):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + int(seed) * 1442695041 + 12345) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return ((n & 0xFFFFFF) / 16777216.0).astype(np.float32)


def vnoise(X, Y, seed=0, period=None):
    x0 = np.floor(X)
    y0 = np.floor(Y)
    fx = (X - x0).astype(np.float32)
    fy = (Y - y0).astype(np.float32)
    u = fx * fx * (3 - 2 * fx)
    v = fy * fy * (3 - 2 * fy)
    ix = x0.astype(np.int64)
    iy = y0.astype(np.int64)
    ix1, iy1 = ix + 1, iy + 1
    if period:
        px, py = period
        ix, ix1 = ix % px, ix1 % px
        iy, iy1 = iy % py, iy1 % py
    a = hash01(ix, iy, seed)
    b = hash01(ix1, iy, seed)
    c = hash01(ix, iy1, seed)
    d = hash01(ix1, iy1, seed)
    return (a + (b - a) * u) + ((c + (d - c) * u) - (a + (b - a) * u)) * v


def fbm(X, Y, oct=5, seed=0, period=None, gain=0.5, lac=2.0):
    tot = 0
    amp = 1.0
    norm = 0
    f = 1.0
    out = 0
    for o in range(oct):
        per = (int(period[0] * f), int(period[1] * f)) if period else None
        out = out + amp * vnoise(X * f, Y * f, seed + o * 17, per)
        norm += amp
        amp *= gain
        f *= lac
    return (out / norm).astype(np.float32)


def cell(X, Y, seed=0, period=None):
    """Worley : retourne F1, F2, id (0..1)"""
    x0 = np.floor(X).astype(np.int64)
    y0 = np.floor(Y).astype(np.int64)
    f1 = np.full(X.shape, 9.0, np.float32)
    f2 = np.full(X.shape, 9.0, np.float32)
    cid = np.zeros(X.shape, np.float32)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            cx = x0 + dx
            cy = y0 + dy
            if period:
                cxm, cym = cx % period[0], cy % period[1]
            else:
                cxm, cym = cx, cy
            jx = hash01(cxm, cym, seed)
            jy = hash01(cxm, cym, seed + 101)
            px = cx + jx
            py = cy + jy
            d = np.hypot(X - px, Y - py).astype(np.float32)
            ident = hash01(cxm, cym, seed + 303)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            cid = np.where(closer, ident, cid)
            f1 = np.where(closer, d, f1)
    return f1, f2, cid


def blur(a, s):
    if a.ndim == 3:
        return np.stack([ndi.gaussian_filter(a[..., i], s) for i in range(a.shape[2])], -1)
    return ndi.gaussian_filter(a, s)


def to_normal(h, strength=1.0, mpp=MPP, wrap=False):
    """height (H,W) en mètres -> normal map RGB (convention OpenGL, G vers le haut de l'image)."""
    mode = 'wrap' if wrap else 'nearest'
    dx = ndi.sobel(h, axis=1, mode=mode) / 8.0 / mpp
    dy = ndi.sobel(h, axis=0, mode=mode) / 8.0 / mpp
    nx = -dx * strength
    ny = dy * strength
    nz = np.ones_like(h)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    n = np.stack([nx / ln, ny / ln, nz / ln], -1)
    return n * 0.5 + 0.5


def grad(t, stops):
    """stops : [(pos, rgb), ...] ; t array -> rgb array"""
    t = np.clip(t, 0, 1)
    pos = np.array([p for p, _ in stops])
    out = np.zeros(t.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(t, pos, [col[c] for _, col in stops])
    return out


def comp(base, col, alpha):
    a = np.clip(alpha, 0, 1)[..., None]
    return base * (1 - a) + np.asarray(col, np.float32) * a


# ------------------------------------------------------------------ canevas sol
class Canvas:
    def __init__(self):
        cols = (np.arange(GW) + 0.5) * MPP + GX0
        rows = (np.arange(GH) + 0.5) * MPP + GZ0
        self.X, self.Z = np.meshgrid(cols.astype(np.float32), rows.astype(np.float32))
        self.sd = self.rr_sdf(self.X, self.Z)
        self.depth = -self.sd  # distance au mur (positif à l'intérieur)

    @staticmethod
    def rr_sdf(x, z, hx=26.0, hz=16.0, r=5.0):
        qx = np.abs(x) - (hx - r)
        qz = np.abs(z) - (hz - r)
        return np.hypot(np.maximum(qx, 0), np.maximum(qz, 0)) + np.minimum(np.maximum(qx, qz), 0) - r

    def perim(self):
        """(s, depth) : abscisse curviligne du point le plus proche sur le périmètre + profondeur."""
        X, Z = self.X, self.Z
        hx, hz, r = 26.0, 16.0, 5.0
        ax, az = hx - r, hz - r
        qx = np.clip(X, -ax, ax)
        qz = np.clip(Z, -az, az)
        vx, vz = X - qx, Z - qz
        L = np.hypot(vx, vz)
        ang = np.arctan2(vz, vx)  # angle autour du centre de coin (z vers le bas)
        # longueurs
        Ltop = 2 * ax
        Lside = 2 * az
        Larc = r * math.pi / 2
        s = np.zeros_like(X)
        # région coin : |x|>ax et |z|>az
        corner = (np.abs(X) > ax) & (np.abs(Z) > az)
        # abscisses de départ
        # top : de x=-ax à ax  (s: 0..Ltop), arc TR: Larc, right: z -az..az, arc BR, bottom, arc BL, left, arc TL
        tot = 2 * Ltop + 2 * Lside + 4 * Larc
        s_top = (X + ax)
        s_tr = Ltop + (ang + math.pi / 2) * r
        s_right = Ltop + Larc + (Z + az)
        s_br = Ltop + Larc + Lside + ang * r
        s_bottom = Ltop + 2 * Larc + Lside + (ax - X)
        s_bl = 2 * Ltop + 2 * Larc + Lside + (ang - math.pi / 2) * r
        s_left = 2 * Ltop + 3 * Larc + Lside + (az - Z)
        s_tl = 2 * Ltop + 3 * Larc + 2 * Lside + (ang + math.pi) * r
        # sélection par quadrants
        s = np.where(Z < -az, s_top, s)
        sel_edge = ~corner
        dx = hx - np.abs(X)
        dz = hz - np.abs(Z)
        top = sel_edge & (dz < dx) & (Z < 0)
        bot = sel_edge & (dz < dx) & (Z >= 0)
        rgt = sel_edge & (dx <= dz) & (X >= 0)
        lft = sel_edge & (dx <= dz) & (X < 0)
        s = np.where(top, s_top, s)
        s = np.where(bot, s_bottom, s)
        s = np.where(rgt, s_right, s)
        s = np.where(lft, s_left, s)
        tr = corner & (X > 0) & (Z < 0)
        br = corner & (X > 0) & (Z >= 0)
        bl = corner & (X <= 0) & (Z >= 0)
        tl = corner & (X <= 0) & (Z < 0)
        s = np.where(tr, s_tr, s)
        s = np.where(br, s_br, s)
        s = np.where(bl, s_bl, s)
        a_tl = np.where(ang < 0, ang + 2 * math.pi, ang)  # TL : angles pi..3pi/2
        s_tl = 2 * Ltop + 3 * Larc + 2 * Lside + (a_tl - math.pi) * r
        s = np.where(tl, s_tl, s)
        return s.astype(np.float32), self.depth, tot

    def contact_ao(self, wall=0.28, wall_len=0.9, obst=0.5, obst_len=0.7, obstacles=OBST):
        ao = 1.0 - wall * np.exp(-np.maximum(self.depth, 0) / wall_len)
        for (x, z, r) in obstacles:
            d = np.hypot(self.X - x, self.Z - z) - r
            ao *= 1.0 - obst * np.exp(-np.maximum(d, 0) / obst_len) * (d < 3.5)
            ao = np.where(d < 0, ao * 0.6, ao)
        return ao.astype(np.float32)

    def circle(self, cx, cz, r, edge=0.02):
        d = np.hypot(self.X - cx, self.Z - cz)
        return smooth(r + edge, r - edge, d)

    def ring(self, cx, cz, r, w, edge=0.015):
        d = np.abs(np.hypot(self.X - cx, self.Z - cz) - r)
        return smooth(w / 2 + edge, w / 2 - edge, d)

    def seg(self, x0, z0, x1, z1, w, edge=0.012):
        dx, dz = x1 - x0, z1 - z0
        L2 = dx * dx + dz * dz
        t = np.clip(((self.X - x0) * dx + (self.Z - z0) * dz) / L2, 0, 1)
        d = np.hypot(self.X - (x0 + t * dx), self.Z - (z0 + t * dz))
        return smooth(w / 2 + edge, w / 2 - edge, d)

    def dashed(self, x0, z0, x1, z1, w, dash, gap, edge=0.012):
        dx, dz = x1 - x0, z1 - z0
        L = math.hypot(dx, dz)
        L2 = L * L
        tt = ((self.X - x0) * dx + (self.Z - z0) * dz) / L2
        t = np.clip(tt, 0, 1)
        d = np.hypot(self.X - (x0 + t * dx), self.Z - (z0 + t * dz))
        along = tt * L
        per = dash + gap
        m = smooth(0.0, 0.03, (along % per)) * smooth(0.0, 0.03, dash - (along % per))
        return smooth(w / 2 + edge, w / 2 - edge, d) * m * (tt >= 0) * (tt <= 1)

    def rep(self):
        pass


def save_pair(name, rgb, height=None, nstr=1.0, emit=None):
    save(name + '.png', rgb)
    if height is not None:
        save(name + '_n.png', to_normal(height, nstr))
    if emit is not None:
        save(name + '_e.png', emit)


# ------------------------------------------------------------------ tuiles (tileables)
def tile_coords(size, meters):
    """coordonnées en mètres pour une tuile carrée size px -> meters m."""
    c = (np.arange(size) + 0.5) * (meters / size)
    X, Y = np.meshgrid(c.astype(np.float32), c.astype(np.float32))
    return X, Y


def tile_noise(name, size=512, base='#808080', var=0.18, seed=1, scale=1.6, grain=0.04, tint2=None):
    X, Y = tile_coords(size, 4.0)
    p = (int(4 * scale), int(4 * scale))
    n = fbm(X * scale, Y * scale, 5, seed, p)
    b = hexc(base)
    col = b[None, None, :] * (1 + var * (n[..., None] - 0.5) * 2)
    if tint2:
        col = mix(col, hexc(tint2)[None, None, :], smooth(0.4, 0.75, fbm(X * 2.3, Y * 2.3, 3, seed + 5, (9, 9))))
    g = (np.random.default_rng(seed).random((size, size)).astype(np.float32) - 0.5) * grain
    col = col * (1 + g[..., None])
    save(name + '.png', col)
    return col


def tile_ashlar(name, size=512, palette=('#cfc3a8', '#c4b693', '#d8cdb3', '#bfae8a'), joint='#6f6552', rows=8,
                block_w=(0.9, 1.7), seed=2, wear=0.35, norm=True, chip=0.5, moss=None, snow=None, scale_m=4.0, shade=0.12):
    """appareil de pierre régulier (rangées de blocs) tileable sur scale_m mètres."""
    rng = np.random.default_rng(seed)
    X, Y = tile_coords(size, scale_m)
    rowh = scale_m / rows
    ri = np.floor(Y / rowh).astype(np.int32)
    img = np.zeros((size, size, 3), np.float32)
    hgt = np.zeros((size, size), np.float32)
    cols = [hexc(c) for c in palette]
    # blocs par rangée
    ids = np.zeros((size, size), np.float32)
    joint_d = np.full((size, size), 9.0, np.float32)
    fx = np.zeros((size, size), np.float32)
    for r in range(rows):
        # largeurs aléatoires qui bouclent sur scale_m
        widths = []
        tot = 0
        while tot < scale_m - 0.4:
            w = rng.uniform(*block_w)
            widths.append(w)
            tot += w
        widths = np.array(widths) * (scale_m / np.sum(widths))
        edges = np.concatenate([[0], np.cumsum(widths)])
        off = rng.uniform(0, scale_m)
        m = (ri == r)
        xs = (X[m] - off) % scale_m
        bi = np.searchsorted(edges, xs, side='right') - 1
        bi = np.clip(bi, 0, len(widths) - 1)
        left = xs - edges[bi]
        right = edges[bi + 1] - xs
        dj = np.minimum(left, right)
        ycell = Y[m] - r * rowh
        dj = np.minimum(dj, np.minimum(ycell, rowh - ycell))
        joint_d[m] = dj
        cid = (bi * 7.31 + r * 3.17 + seed) % 1.0
        ids[m] = rng.random(len(widths))[bi]
        fx[m] = left / widths[bi]
    base = np.zeros((size, size, 3), np.float32)
    for k, c in enumerate(cols):
        sel = (ids * len(cols)).astype(int) % len(cols) == k
        base[sel] = c
    n1 = fbm(X * 3, Y * 3, 5, seed + 3, (12, 12))
    n2 = fbm(X * 11, Y * 11, 3, seed + 7, (44, 44))
    shade_b = 1 + shade * (ids - 0.5) * 2
    base = base * shade_b[..., None] * (1 + (n1[..., None] - 0.5) * wear) * (1 + (n2[..., None] - 0.5) * 0.18)
    jmask = smooth(0.035, 0.012, joint_d)
    # bord de bloc plus clair / dessous plus sombre (biseau)
    bevel = smooth(0.0, 0.07, joint_d)
    base = base * (0.86 + 0.14 * bevel[..., None])
    base = comp(base, hexc(joint) * 0.8, jmask * 0.95)
    # éclats
    ch = fbm(X * 9, Y * 9, 3, seed + 11, (36, 36))
    base = base * (1 - 0.18 * smooth(0.62, 0.8, ch)[..., None] * chip)
    if moss:
        mm = smooth(0.58, 0.78, fbm(X * 2.2, Y * 2.2, 4, seed + 13, (9, 9))) * smooth(0.0, 0.3, 0.5 - Y / scale_m * 0)
        base = comp(base, hexc(moss), mm * 0.5)
    h = bevel * 0.012 + n2 * 0.004 + (1 - jmask) * 0.0
    h = h - jmask * 0.01
    save(name + '.png', base)
    if norm:
        save(name + '_n.png', to_normal(h, 3.0, scale_m / size, wrap=True))
    return base


def tile_cobble(name, size=512, palette=('#7b766e', '#8b857a', '#6b665f', '#938b7d'), joint='#3f3a34', seed=3,
                cells=11, gap=0.07, norm=True, scale_m=4.0, dirt='#5b4a38'):
    rng = np.random.default_rng(seed)
    X, Y = tile_coords(size, scale_m)
    sx = cells / scale_m
    # grille décalée par rangées (pavés)
    row = np.floor(Y * sx * 1.3).astype(np.int64)
    Xs = X * sx + 0.5 * (row % 2)
    f1, f2, cid = cell(Xs * 1.0, Y * sx * 1.0, seed, (cells, cells))
    e = f2 - f1
    cols = [hexc(c) for c in palette]
    ci = (cid * len(cols)).astype(int) % len(cols)
    base = np.zeros((size, size, 3), np.float32)
    for k, c in enumerate(cols):
        base[ci == k] = c
    n = fbm(X * 6, Y * 6, 4, seed + 1, (24, 24))
    base = base * (0.8 + 0.4 * cid[..., None]) * (1 + (n[..., None] - 0.5) * 0.35)
    dome = smooth(0.0, 0.45, e)
    base = base * (0.7 + 0.45 * dome[..., None])
    jm = smooth(gap, gap * 0.35, e)
    base = comp(base, hexc(joint), jm * 0.92)
    dm = smooth(0.5, 0.8, fbm(X * 2, Y * 2, 4, seed + 4, (8, 8)))
    base = comp(base, hexc(dirt), dm * 0.3 * jm + dm * 0.12)
    h = dome * 0.05 + n * 0.01 - jm * 0.03
    save(name + '.png', base)
    if norm:
        save(name + '_n.png', to_normal(h, 3.0, scale_m / size, wrap=True))
    return base


def tile_rock(name, size=512, c0='#4b4a52', c1='#7d7a82', c2='#a8a39a', seed=4, strata=0.0, norm=True, scale_m=4.0, crack=0.5):
    X, Y = tile_coords(size, scale_m)
    n = fbm(X * 1.2, Y * 1.2, 6, seed, (5, 5))
    w = fbm(X * 0.8 + n * 1.5, Y * 0.8 + n * 1.5, 5, seed + 3, (3, 3))
    f1, f2, cid = cell(X * 2.2 + n * 0.8, Y * 2.2 + n * 0.8, seed + 9, (9, 9))
    e = f2 - f1
    t = np.clip(w * 0.7 + cid * 0.3, 0, 1)
    if strata:
        t = np.clip(t * 0.7 + 0.3 * (0.5 + 0.5 * np.sin((Y * 6 + n * 3) * 2 * math.pi / 1.0 * strata)), 0, 1)
    col = grad(t, [(0.0, hexc(c0)), (0.55, hexc(c1)), (1.0, hexc(c2))])
    col = col * (0.75 + 0.35 * smooth(0.0, 0.5, e)[..., None])
    cr = smooth(0.05, 0.015, e) * crack
    col = col * (1 - 0.55 * cr[..., None])
    gr = fbm(X * 24, Y * 24, 3, seed + 2, (96, 96))
    col = col * (1 + (gr[..., None] - 0.5) * 0.25)
    h = n * 0.15 + w * 0.1 + smooth(0.0, 0.5, e) * 0.05 - cr * 0.04
    save(name + '.png', col)
    if norm:
        save(name + '_n.png', to_normal(h, 1.2, scale_m / size, wrap=True))
    return col


def tile_wood(name, size=512, c0='#4b3220', c1='#8a5e36', seed=5, planks=6, scale_m=4.0, norm=False):
    rng = np.random.default_rng(seed)
    X, Y = tile_coords(size, scale_m)
    pw = scale_m / planks
    pi_ = np.floor(X / pw).astype(np.int32)
    px = (X % pw) / pw
    grainx = fbm(X * 0.8, Y * 14, 5, seed, (3, 56))
    wob = fbm(X * 1.0 + 0, Y * 3.0, 3, seed + 2, (4, 12))
    t = np.clip(0.5 + (grainx - 0.5) * 1.4 + (np.array([rng.uniform(-0.18, 0.18) for _ in range(planks)])[pi_ % planks]), 0, 1)
    rings = 0.5 + 0.5 * np.sin((X * 24 + wob * 6) * 1.0)
    t = np.clip(t * 0.75 + rings * 0.25, 0, 1)
    col = grad(t, [(0, hexc(c0)), (1, hexc(c1))])
    edge = np.minimum(px, 1 - px) * pw
    col = comp(col, hexc(c0) * 0.35, smooth(0.012, 0.0, edge))
    col = col * (1 + (fbm(X * 30, Y * 6, 2, seed + 8, (120, 24))[..., None] - 0.5) * 0.18)
    save(name + '.png', col)
    return col


def tile_metal(name, size=512, base='#5b5f66', seed=6, rust=0.0, rust_col='#7a3b1e', scale_m=2.0, plates=4, rivets=True, norm=True):
    X, Y = tile_coords(size, scale_m)
    n = fbm(X * 2, Y * 2, 5, seed, (4, 4))
    br = fbm(X * 1.5, Y * 40, 4, seed + 1, (3, 80))
    col = np.ones((size, size, 3), np.float32) * hexc(base)
    col = col * (0.82 + 0.3 * n[..., None]) * (0.92 + 0.16 * br[..., None])
    pw = scale_m / plates
    gx = np.minimum(X % pw, pw - X % pw)
    gy = np.minimum(Y % pw, pw - Y % pw)
    gd = np.minimum(gx, gy)
    seam = smooth(0.02, 0.006, gd)
    col = col * (1 - 0.55 * seam[..., None])
    h = -seam * 0.01 + n * 0.003
    if rivets:
        # rivets aux angles de plaque
        fx = (X % (pw / 2)) / (pw / 2)
        fy = (Y % (pw / 2)) / (pw / 2)
        for ox, oy in ((0.5, 0.5),):
            pass
        px = X % pw
        py = Y % pw
        rv = np.zeros_like(X)
        for cx in (0.07 * pw, 0.93 * pw):
            for cy in (0.07 * pw, 0.93 * pw):
                d = np.hypot(px - cx, py - cy)
                rv = np.maximum(rv, smooth(0.022, 0.012, d))
        col = col * (1 + 0.35 * rv[..., None])
        h = h + rv * 0.012
    if rust > 0:
        rm = smooth(0.5, 0.75, fbm(X * 3, Y * 3, 5, seed + 5, (6, 6)) + (1 - smooth(0.0, 0.1, gd)) * 0.25) * rust
        col = comp(col, hexc(rust_col), rm)
    save(name + '.png', col)
    if norm:
        save(name + '_n.png', to_normal(h, 2.0, scale_m / size, wrap=True))
    return col


def tile_snow(name, size=512, seed=7, base='#e8f0fa', shade='#b8cbe0'):
    X, Y = tile_coords(size, 4.0)
    n = fbm(X * 2, Y * 2, 5, seed, (8, 8))
    col = mix(hexc(shade)[None, None, :], hexc(base)[None, None, :], smooth(0.25, 0.7, n))
    sp = hash01(np.floor(X * 90).astype(np.int64) % 360, np.floor(Y * 90).astype(np.int64) % 360, seed)
    col = col * (1 + (sp[..., None] - 0.5) * 0.06)
    h = n * 0.1
    save(name + '.png', col)
    save(name + '_n.png', to_normal(h, 1.0, 4.0 / size, wrap=True))
    return col


def tile_ice(name, size=512, seed=8, c0='#7fb6d8', c1='#d6f1ff', c2='#3c78a8'):
    X, Y = tile_coords(size, 4.0)
    n = fbm(X * 1.5, Y * 1.5, 5, seed, (6, 6))
    f1, f2, cid = cell(X * 1.8 + n, Y * 1.8 + n, seed + 4, (7, 7))
    e = f2 - f1
    cr = smooth(0.06, 0.0, e)
    col = grad(np.clip(n * 0.8 + cid * 0.2, 0, 1), [(0, hexc(c2)), (0.5, hexc(c0)), (1, hexc(c1))])
    col = comp(col, hexc(c1), cr * 0.55)
    fine = fbm(X * 22, Y * 22, 3, seed + 9, (88, 88))
    col = col * (1 + (fine[..., None] - 0.5) * 0.12)
    h = n * 0.05 - cr * 0.02
    save(name + '.png', col)
    save(name + '_n.png', to_normal(h, 1.5, 4.0 / size, wrap=True))
    return col


def tile_marble(name, size=512, c0='#e6dcc4', c1='#cfc2a4', vein='#a89a7c', seed=30, strata=0.0, norm=True, vein_amt=0.35, scale_m=4.0, grain=0.04):
    """pierre lisse veinée, sans joints (fûts, dalles, moulures)."""
    X, Y = tile_coords(size, scale_m)
    n = fbm(X * 1.0, Y * 1.0, 6, seed, (4, 4))
    w = fbm(X * 0.9 + n * 1.2, Y * 0.9 + n * 1.2, 5, seed + 2, (4, 4))
    t = np.clip(0.5 + (w - 0.5) * 1.6, 0, 1)
    col = mix(hexc(c1)[None, None, :], hexc(c0)[None, None, :], t)
    v = np.abs(np.sin((X * 1.1 + Y * 0.7 + w * 3.0) * 2 * math.pi * 0.5))
    vm = smooth(0.06, 0.0, v) * smooth(0.45, 0.65, fbm(X * 2, Y * 2, 3, seed + 5, (8, 8)))
    col = comp(col, hexc(vein), vm * vein_amt)
    if strata:
        st = 0.5 + 0.5 * np.sin((Y * 4 + n * 2) * 2 * math.pi * strata)
        col = col * (1 - 0.06 * st[..., None])
    g = np.random.default_rng(seed).random((size, size)).astype(np.float32) - 0.5
    col = col * (1 + g[..., None] * grain) * (1 + (fbm(X * 14, Y * 14, 3, seed + 7, (56, 56))[..., None] - 0.5) * 0.12)
    save(name + '.png', col)
    if norm:
        h = n * 0.01 + fbm(X * 18, Y * 18, 3, seed + 9, (72, 72)) * 0.004
        save(name + '_n.png', to_normal(h, 1.5, scale_m / size, wrap=True))
    return col


# ------------------------------------------------------------------ outils de dessin vectoriel sur le canevas
def _win(c, x0, z0, x1, z1, pad):
    j0 = int(max(0, math.floor((min(x0, x1) - pad - GX0) / MPP)))
    j1 = int(min(GW, math.ceil((max(x0, x1) + pad - GX0) / MPP) + 1))
    i0 = int(max(0, math.floor((min(z0, z1) - pad - GZ0) / MPP)))
    i1 = int(min(GH, math.ceil((max(z0, z1) + pad - GZ0) / MPP) + 1))
    return i0, i1, j0, j1


def draw_segs(c, segs, w, edge=0.012, out=None):
    """segs : [(x0,z0,x1,z1), ...] -> masque (max des capsules)."""
    if out is None:
        out = np.zeros((GH, GW), np.float32)
    for (x0, z0, x1, z1) in segs:
        i0, i1, j0, j1 = _win(c, x0, z0, x1, z1, w + edge * 2)
        if i1 <= i0 or j1 <= j0:
            continue
        X = c.X[i0:i1, j0:j1]
        Z = c.Z[i0:i1, j0:j1]
        dx, dz = x1 - x0, z1 - z0
        L2 = dx * dx + dz * dz + 1e-9
        t = np.clip(((X - x0) * dx + (Z - z0) * dz) / L2, 0, 1)
        d = np.hypot(X - (x0 + t * dx), Z - (z0 + t * dz))
        m = smooth(w / 2 + edge, w / 2 - edge, d)
        out[i0:i1, j0:j1] = np.maximum(out[i0:i1, j0:j1], m)
    return out


def draw_circles(c, items, edge=0.015, out=None):
    """items: [(cx,cz,r)] disques pleins"""
    if out is None:
        out = np.zeros((GH, GW), np.float32)
    for (cx, cz, r) in items:
        i0, i1, j0, j1 = _win(c, cx - r, cz - r, cx + r, cz + r, edge * 2)
        X = c.X[i0:i1, j0:j1]
        Z = c.Z[i0:i1, j0:j1]
        m = smooth(r + edge, r - edge, np.hypot(X - cx, Z - cz))
        out[i0:i1, j0:j1] = np.maximum(out[i0:i1, j0:j1], m)
    return out


def polar_segs(cx, cz, pts_polar):
    """liste de points (r, angle) -> segments."""
    pts = [(cx + r * math.cos(a), cz + r * math.sin(a)) for r, a in pts_polar]
    return [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(len(pts) - 1)]


def ring_segs(cx, cz, r, n=96, a0=0.0, a1=2 * math.pi):
    out = []
    for i in range(n):
        t0 = a0 + (a1 - a0) * i / n
        t1 = a0 + (a1 - a0) * (i + 1) / n
        out.append((cx + r * math.cos(t0), cz + r * math.sin(t0), cx + r * math.cos(t1), cz + r * math.sin(t1)))
    return out


def rune_segs(cx, cz, r, n, size, seed=0, tangential=True):
    """glyphes runiques (suites de traits) disposés sur un anneau."""
    rg = np.random.default_rng(seed)
    segs = []
    grid = [(i, j) for i in range(3) for j in range(5)]
    for k in range(n):
        a = 2 * math.pi * k / n
        px, pz = cx + r * math.cos(a), cz + r * math.sin(a)
        ux, uz = -math.sin(a), math.cos(a)   # tangent
        vx, vz = math.cos(a), math.sin(a)    # radial
        pts = [grid[i] for i in rg.choice(len(grid), size=rg.integers(3, 6), replace=False)]
        pts = sorted(pts, key=lambda p: (p[1], p[0]))
        # trait vertical central presque toujours
        glyph = []
        if rg.random() < 0.8:
            glyph.append(((1, 0), (1, 4)))
        for i in range(len(pts) - 1):
            if rg.random() < 0.85:
                glyph.append((pts[i], pts[i + 1]))
        for (a_, b_) in glyph:
            def P(g):
                lx = (g[0] - 1) * size * 0.42
                lz = (g[1] - 2) * size * 0.28
                return (px + ux * lx + vx * lz, pz + uz * lx + vz * lz)
            p0, p1 = P(a_), P(b_)
            segs.append((p0[0], p0[1], p1[0], p1[1]))
    return segs


def snowflake_segs(cx, cz, R, branches=(0.3, 0.5, 0.72), rot=0.0):
    segs = []
    for k in range(6):
        a = rot + k * math.pi / 3
        ex, ez = cx + R * math.cos(a), cz + R * math.sin(a)
        segs.append((cx, cz, ex, ez))
        for f in branches:
            bx, bz = cx + R * f * math.cos(a), cz + R * f * math.sin(a)
            bl = R * 0.34 * (1 - f * 0.45)
            for s in (-1, 1):
                aa = a + s * math.radians(55)
                segs.append((bx, bz, bx + bl * math.cos(aa), bz + bl * math.sin(aa)))
        # petit v à la pointe
        tl = R * 0.16
        for s in (-1, 1):
            aa = a + s * math.radians(40)
            segs.append((ex, ez, ex - tl * math.cos(aa), ez - tl * math.sin(aa)))
    return segs


def blobs(c, n, rmin, rmax, seed, region=None, strength=1.0, sigma=0.0):
    """semis de disques doux (cailloux, flocons...). retourne masque."""
    rg = np.random.default_rng(seed)
    out = np.zeros((GH, GW), np.float32)
    px = rg.uniform(GX0, GX1, n)
    pz = rg.uniform(GZ0, GZ1, n)
    rr = rg.uniform(rmin, rmax, n)
    for x, z, r in zip(px, pz, rr):
        if region is not None:
            # region(x,z)-> bool
            if not region(x, z):
                continue
        j = int((x - GX0) / MPP)
        i = int((z - GZ0) / MPP)
        k = int(r / MPP) + 2
        i0, i1, j0, j1 = max(0, i - k), min(GH, i + k + 1), max(0, j - k), min(GW, j + k + 1)
        X = c.X[i0:i1, j0:j1]
        Z = c.Z[i0:i1, j0:j1]
        m = smooth(r, r * 0.4, np.hypot(X - x, Z - z)) * rg.uniform(0.5, 1.0)
        out[i0:i1, j0:j1] = np.maximum(out[i0:i1, j0:j1], m)
    return out * strength


def down(arr, f=2):
    """réduction de résolution (moyenne) pour normal maps."""
    H, W = arr.shape[:2]
    a = arr[:H // f * f, :W // f * f]
    return a.reshape(H // f, f, W // f, f, -1).mean((1, 3)) if a.ndim == 3 else a.reshape(H // f, f, W // f, f).mean((1, 3))
