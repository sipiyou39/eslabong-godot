"""Textures du colisée : sol de sable doré + pierre claire."""
import math
import numpy as np
from scipy import spatial
import tex as T
from tex import *


def ground():
    rng = np.random.default_rng(11)
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    # --- sable
    n_big = fbm(X / 6.0 + 3, Z / 6.0, 5, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 9, Z * 9, 4, 3)
    sand = grad(np.clip(n_big * 0.65 + n_mid * 0.35, 0, 1),
                [(0.0, hexc('#c49858')), (0.35, hexc('#d9ae68')), (0.7, hexc('#ebc982')), (1.0, hexc('#f5deA6'))])
    sand = sand * (1 + (n_fine[..., None] - 0.5) * 0.16)
    # grain
    g = (rng.random(sand.shape[:2]).astype(np.float32) - 0.5)
    sand = sand * (1 + g[..., None] * 0.07)
    height = (n_fine * 0.006 + n_mid * 0.01 + g * 0.0015).astype(np.float32)
    # --- ratissage concentrique
    dist = np.hypot(X * 0.92, Z * 1.15)
    warp = fbm(X * 0.5, Z * 0.5, 3, 5) * 1.6
    rake = np.sin((dist + warp) * 2 * math.pi / 0.46)
    rmask = smooth(0.50, 0.72, fbm(X * 0.22 + 7, Z * 0.22, 4, 6))
    sand = sand * (1 + rake[..., None] * 0.045 * rmask[..., None])
    height += rake * 0.012 * rmask
    # --- zones piétinées : chemins sombres + taches
    paths = []
    pts_def = [((-19, 0), (-3, -2)), ((19, 0), (3, 2)), ((-19, 0), (-9, 6)), ((19, 0), (9, -6)), ((-6, -8), (7, 8)), ((-14, 7), (12, -9)),
               ((0, -12), (0, 12))]
    samples = []
    for (a, b) in pts_def:
        for t in np.linspace(0, 1, 60):
            bend = math.sin(t * math.pi) * rng.uniform(-3, 3)
            x = a[0] + (b[0] - a[0]) * t + bend * 0.3
            z = a[1] + (b[1] - a[1]) * t + bend
            samples.append((x, z))
    # petits points d'usure autour des obstacles et du centre
    for (ox, oz, r) in OBST:
        for t in np.linspace(0, 2 * math.pi, 30, endpoint=False):
            rr = r + 0.9 + rng.uniform(0, 0.6)
            samples.append((ox + rr * math.cos(t), oz + rr * math.sin(t)))
    tree = spatial.cKDTree(np.array(samples))
    sx, sz = X[::4, ::4], Z[::4, ::4]
    dd, _ = tree.query(np.stack([sx.ravel(), sz.ravel()], 1))
    dd = dd.reshape(sx.shape).astype(np.float32)
    dd = np.kron(dd, np.ones((4, 4), np.float32))[:GH, :GW]
    wear = np.exp(-(dd / 1.0) ** 2) * smooth(0.4, 0.75, fbm(X * 0.7, Z * 0.7, 4, 12)) * 0.7
    sand = sand * (1 - 0.12 * wear[..., None])
    sand = comp(sand, hexc('#a07a44'), wear * 0.14)
    height -= wear * 0.01
    # taches sombres (sang séché / poussière) très légères
    stain = smooth(0.66, 0.86, fbm(X * 0.9, Z * 0.9, 5, 14))
    sand = comp(sand, hexc('#8a5e34'), stain * 0.12)
    # --- cailloux / éclats
    ns = 1800
    px = rng.uniform(GX0, GX1, ns)
    pz = rng.uniform(GZ0, GZ1, ns)
    mask = np.zeros((GH, GW), np.float32)
    ii = ((pz - GZ0) / MPP).astype(int).clip(0, GH - 1)
    jj = ((px - GX0) / MPP).astype(int).clip(0, GW - 1)
    mask[ii, jj] = rng.uniform(0.4, 1.0, ns)
    mask = ndi.gaussian_filter(mask, 1.1) * 22
    mask = np.clip(mask, 0, 1)
    sand = sand * (1 - 0.20 * mask[..., None])
    mask2 = np.zeros((GH, GW), np.float32)
    ii = rng.integers(0, GH, 2500)
    jj = rng.integers(0, GW, 2500)
    mask2[ii, jj] = rng.uniform(0.4, 1.0, 2500)
    mask2 = np.clip(ndi.gaussian_filter(mask2, 1.2) * 30, 0, 1)
    sand = comp(sand, hexc('#fff0c8'), mask2 * 0.35)
    height += mask * 0.01
    # --- bordure en dalles de pierre
    s, dep, tot = c.perim()
    # joints de dalles le long de s
    widths = []
    tt = 0
    while tt < tot + 2:
        w = rng.uniform(1.1, 1.9)
        widths.append(w)
        tt += w
    edges = np.concatenate([[0], np.cumsum(widths)])
    bi = np.clip(np.searchsorted(edges, s, side='right') - 1, 0, len(widths) - 1)
    ds = np.minimum(s - edges[bi], edges[bi + 1] - s)
    slab_id = rng.random(len(widths))[bi]
    stone = grad(np.clip(slab_id * 0.8 + fbm(X * 1.5, Z * 1.5, 4, 21) * 0.4, 0, 1),
                 [(0, hexc('#c8b48a')), (0.5, hexc('#dac9a2')), (1, hexc('#ebdcb8'))])
    stone = stone * (1 + (fbm(X * 8, Z * 8, 4, 22)[..., None] - 0.5) * 0.25)
    # deux rangées
    slabh = 1.24
    row = np.floor(dep / slabh)
    dd2 = np.minimum(dep - row * slabh, (row + 1) * slabh - dep)
    jd = np.minimum(ds, dd2)
    joint = smooth(0.03, 0.012, jd)
    stone = stone * (0.85 + 0.15 * smooth(0, 0.08, jd)[..., None])
    stone = comp(stone, hexc('#6a5238'), joint * 0.75)
    band_w = 1.3
    inside_band = smooth(band_w + 0.05, band_w - 0.05, dep)
    # sable qui déborde sur la pierre
    drift = smooth(0.0, 1.0, fbm(X * 0.8, Z * 0.8, 4, 23) * 1.6 + dep * 0.55 - 0.55)
    drift = smooth(0.35, 0.65, drift * 0.9 + (n_fine - 0.5) * 0.3 + (dep - 0.55) * 0.6)
    stone_alpha = inside_band * (1 - drift * 0.9)
    sand = comp(sand, stone, stone_alpha)
    height = height + stone_alpha * 0.02 - joint * stone_alpha * 0.02
    # liseré d'or près du mur
    # --- emblème central
    ivory = hexc('#f0e4c4')
    gold = hexc('#d8a73c')
    dark = hexc('#7b5a2c')
    wornmask = smooth(0.30, 0.62, fbm(X * 1.2 + 4, Z * 1.2, 5, 31)) * 0.75 + 0.25
    emb = np.zeros((GH, GW), np.float32)
    for rad, w in ((6.0, 0.30), (3.4, 0.16), (6.55, 0.08)):
        emb = np.maximum(emb, c.ring(0, 0, rad, w))
    ang = np.arctan2(Z, X)
    R = np.hypot(X, Z)
    # étoile à 8 branches
    star = np.zeros_like(emb)
    for k in range(8):
        a0 = k * math.pi / 4
        # distance perpendiculaire au rayon
        perp = np.abs(-(X) * math.sin(a0) + (Z) * math.cos(a0))
        par = X * math.cos(a0) + Z * math.sin(a0)
        wd = 0.20 * (1 - np.clip((par - 0.5) / 5.5, 0, 1)) + 0.02
        star = np.maximum(star, smooth(wd + 0.015, wd - 0.015, perp) * ((par > 0.5) & (par < 6.0)))
    emb = np.maximum(emb, star)
    emb = np.maximum(emb, c.circle(0, 0, 0.75))
    # petits points runiques entre les anneaux
    for k in range(24):
        a0 = k * math.pi / 12
        rr_ = 4.8
        emb = np.maximum(emb, c.circle(rr_ * math.cos(a0), rr_ * math.sin(a0), 0.07, 0.015) * (k % 3 != 0))
    # ombre portée de l'inlay
    inl = emb * wornmask
    sand = sand * (1 - 0.22 * ndi.gaussian_filter(emb, 3)[..., None] * (1 - emb)[..., None])
    sand = comp(sand, mix(ivory, gold, smooth(0.5, 0.7, fbm(X * 3, Z * 3, 3, 33))), inl * 0.96)
    # filet doré autour du grand anneau
    gr = np.maximum(c.ring(0, 0, 5.75, 0.05), c.ring(0, 0, 6.25, 0.05))
    sand = comp(sand, gold, gr * wornmask * 0.9)
    height += inl * 0.012
    # --- zones d'équipe
    teamL = hexc('#a8362a')
    teamR = hexc('#2f5f8f')
    for sgn, col in ((-1, teamL), (1, teamR)):
        cx = 19.0 * sgn
        pad = c.circle(cx, 0, 3.7)
        ring1 = np.maximum(c.ring(cx, 0, 3.7, 0.14), c.ring(cx, 0, 2.6, 0.08))
        cross = np.maximum(c.seg(cx - 2.0, 0, cx + 2.0, 0, 0.1), c.seg(cx, -2.0, cx, 2.0, 0.1))
        diag = np.maximum(c.seg(cx - 1.4, -1.4, cx + 1.4, 1.4, 0.07), c.seg(cx - 1.4, 1.4, cx + 1.4, -1.4, 0.07))
        wn = smooth(0.25, 0.65, fbm(X * 1.5 + sgn * 5, Z * 1.5, 5, 41 + sgn)) * 0.7 + 0.3
        sand = comp(sand, col, pad * 0.16 * wn)
        sand = comp(sand, col, np.maximum(ring1, np.maximum(cross, diag)) * 0.7 * wn)
        # ligne de zone
        lx = 13.0 * sgn
        ln = c.dashed(lx, -12.5, lx, 12.5, 0.14, 0.9, 0.45)
        ln2 = np.maximum(c.seg(lx, -12.5, lx + 0.6 * sgn, -12.5, 0.14), c.seg(lx, 12.5, lx + 0.6 * sgn, 12.5, 0.14))
        sand = comp(sand, col, np.maximum(ln, ln2) * 0.65 * wn)
        height -= np.maximum(ring1, ln) * 0.004
    # --- AO de contact (mur + obstacles)
    ao = c.contact_ao(wall=0.30, wall_len=0.8, obst=0.55, obst_len=0.65)
    sand = sand * ao[..., None]
    # sous les piliers : pierre/ombre
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        base = smooth(r + 0.06, r - 0.1, d)
        sand = comp(sand, hexc('#8d7b5e') * 0.7, base)
        # gravats
        grv = np.zeros((GH, GW), np.float32)
        for _ in range(26):
            a = rng.uniform(0, 2 * math.pi)
            rr_ = rng.uniform(r + 0.2, r + 1.6)
            grv = np.maximum(grv, c.circle(ox + rr_ * math.cos(a), oz + rr_ * math.sin(a), rng.uniform(0.05, 0.13), 0.02))
        sand = comp(sand, hexc('#c9b78f'), grv * 0.8)
        sand = sand * (1 - 0.25 * ndi.gaussian_filter(grv, 2)[..., None])
    # vignette douce (assombrit très légèrement les bords)
    save('colosseum_ground.png', sand)
    save('colosseum_ground_n.png', to_normal(down(height, 2), 2.5, MPP * 2))


def stones():
    tile_ashlar('colosseum_stone', 512, palette=('#d9ccae', '#cfc0a0', '#e2d6bb', '#c6b693'), joint='#6a5c46', rows=6, block_w=(1.0, 1.9),
                seed=21, wear=0.4)
    tile_ashlar('colosseum_stone_warm', 512, palette=('#c9a874', '#bf9c68', '#d4b482', '#b69160'), joint='#5b4630', rows=8,
                block_w=(0.8, 1.5), seed=22, wear=0.4)
    tile_noise('colosseum_plaster', 512, base='#d8c9a6', var=0.12, seed=23, scale=1.2, grain=0.05)
    tile_wood('colosseum_wood', 512, '#3d2918', '#7d5430', seed=24)
    tile_metal('colosseum_bronze', 512, base='#a07a3a', seed=25, rust=0.15, rust_col='#3f6b4d')
    tile_noise('colosseum_dirt', 512, base='#b48c58', var=0.2, seed=26, scale=1.5, grain=0.08, tint2='#8d6a3c')
    tile_rock('colosseum_rock', 512, '#6d5a47', '#9a8264', '#c0a885', seed=27)
    tile_marble('colosseum_marble', 512, '#eadfc6', '#d6c8a8', '#b09c78', seed=28, strata=0.5)


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'stones']
    if 'stones' in what:
        stones()
    if 'ground' in what:
        ground()
