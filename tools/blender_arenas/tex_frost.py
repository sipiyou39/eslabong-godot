"""Textures de la forteresse de glace."""
import math
import numpy as np
import tex as T
from tex import *


def ground():
    rng = np.random.default_rng(51)
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    # --- dalles de glace en appareil décalé
    SX, SZ = 2.3, 2.3
    row = np.floor((Z + 17.0) / SZ)
    col = np.floor((X + 27.0 + 0.5 * SX * (row % 2)) / SX)
    u = ((X + 27.0 + 0.5 * SX * (row % 2)) / SX) - col
    v = ((Z + 17.0) / SZ) - row
    sid = hash01(col.astype(np.int64), row.astype(np.int64), 5)
    sid2 = hash01(col.astype(np.int64), row.astype(np.int64), 9)
    edge = np.minimum(np.minimum(u * SX, (1 - u) * SX), np.minimum(v * SZ, (1 - v) * SZ))
    n_big = fbm(X / 5.0, Z / 5.0, 4, 1)
    n_mid = fbm(X * 0.9, Z * 0.9, 5, 2)
    n_fine = fbm(X * 7, Z * 7, 4, 3)
    t = np.clip(sid * 0.55 + n_big * 0.45, 0, 1)
    ice = grad(t, [(0.0, hexc('#2a6a94')), (0.35, hexc('#3f86b0')), (0.7, hexc('#6fb2d4')), (1.0, hexc('#a6d8ee'))])
    # profondeur : centre plus translucide/sombre, bords givrés
    frost_edge = smooth(0.55, 0.0, edge) * (0.5 + 0.5 * n_mid)
    ice = comp(ice, hexc('#d8eefa'), frost_edge * 0.55)
    # bulles / veines internes
    vein = fbm(X * 2.3 + sid2 * 7, Z * 2.3, 5, 11)
    ice = comp(ice, hexc('#cfeaf8'), smooth(0.6, 0.8, vein) * 0.35)
    ice = ice * (1 + (n_fine[..., None] - 0.5) * 0.14)
    # fissures (Voronoi chaotique)
    f1, f2, cid = cell(X * 0.55 + n_mid * 0.9, Z * 0.55 + n_mid * 0.9, 17)
    crack = smooth(0.045, 0.0, f2 - f1) * (sid2 > 0.45)
    ice = comp(ice, hexc('#e8f6ff'), crack * 0.7)
    h = (n_fine * 0.004 + n_mid * 0.01).astype(np.float32)
    # joints
    joint = smooth(0.05, 0.015, edge)
    ice = comp(ice, hexc('#17334d'), joint * 0.9)
    ice = comp(ice, hexc('#bfe4f5'), smooth(0.11, 0.05, edge) * smooth(0.05, 0.02, edge) * 0.0)
    h = h - joint * 0.02 - crack * 0.006
    # --- dessus de dalles légèrement éclairci (reflets)
    ice = ice * (1 + 0.12 * smooth(0.0, 1.0, (1 - np.abs(u - 0.3)) * (1 - np.abs(v - 0.3)))[..., None] * 0.5)
    # --- neige : bords du mur + coulées + flocons dispersés
    drift_noise = fbm(X * 0.55, Z * 0.55, 5, 21)
    wall_snow = smooth(2.4, 0.3, depth - (drift_noise - 0.5) * 3.2)
    scatter = smooth(0.6, 0.74, fbm(X * 0.8, Z * 0.8, 6, 23)) * 0.85
    snow_m = np.clip(np.maximum(wall_snow, scatter), 0, 1)
    snow = grad(np.clip(fbm(X * 2.2, Z * 2.2, 4, 25) * 1.3, 0, 1), [(0, hexc('#c4d8ec')), (0.5, hexc('#e6f0fa')), (1, hexc('#fbfdff'))])
    snow = snow * (1 + (n_fine[..., None] - 0.5) * 0.06)
    # bords doux de neige (ombre bleutée en bordure)
    ice = comp(ice, hexc('#8fb5d6'), smooth(0.0, 0.5, snow_m) * smooth(1.0, 0.7, snow_m) * 0.4)
    ice = comp(ice, snow, smooth(0.35, 0.6, snow_m))
    h = h + smooth(0.35, 0.6, snow_m) * 0.05 + n_mid * 0.01 * snow_m
    # --- runes lumineuses (émission) : flocon central + anneaux + glyphes
    em = np.zeros((GH, GW), np.float32)
    ring_a = np.maximum(c.ring(0, 0, 7.0, 0.16), c.ring(0, 0, 7.6, 0.06))
    ring_b = np.maximum(c.ring(0, 0, 3.2, 0.12), c.ring(0, 0, 4.9, 0.07))
    emb = np.maximum(ring_a, ring_b)
    emb = np.maximum(emb, draw_segs(c, snowflake_segs(0, 0, 6.4, rot=math.pi / 6), 0.12))
    emb = np.maximum(emb, draw_segs(c, rune_segs(0, 0, 8.3, 36, 0.55, seed=3), 0.05))
    emb = np.maximum(emb, draw_circles(c, [(0, 0, 0.55)]))
    # zones d'équipe
    teamL = hexc('#32d0e6')
    teamR = hexc('#8f7cff')
    em_team = np.zeros((GH, GW, 3), np.float32)
    for sgn, col_ in ((-1, teamL), (1, teamR)):
        cx = 19.0 * sgn
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.14), c.ring(cx, 0, 2.6, 0.07))
        z_ = np.maximum(z_, draw_segs(c, snowflake_segs(cx, 0, 2.3, rot=0.0 + sgn), 0.08))
        z_ = np.maximum(z_, draw_segs(c, rune_segs(cx, 0, 4.3, 18, 0.4, seed=7 + sgn), 0.04))
        ln = c.dashed(13.0 * sgn, -12.5, 13.0 * sgn, 12.5, 0.12, 0.9, 0.45)
        z_ = np.maximum(z_, ln)
        em_team += z_[..., None] * col_
    wornm = smooth(0.25, 0.55, fbm(X * 1.1, Z * 1.1, 5, 31)) * 0.6 + 0.4
    emb = emb * wornm
    em_team = em_team * wornm[..., None]
    # sous la neige l'inlay est atténué
    vis = 1 - smooth(0.4, 0.7, snow_m) * 0.8
    emb = emb * vis
    em_team = em_team * vis[..., None]
    ice = comp(ice, hexc('#bdf4ff'), emb * 0.9)
    ice = ice + em_team * 0.45
    ice = ice * (1 - 0.2 * ndi.gaussian_filter(emb, 4)[..., None] * (1 - emb)[..., None])
    emission = emb[..., None] * hexc('#52d8ff') * 0.9 + em_team * 0.8
    # --- AO de contact
    ao = c.contact_ao(wall=0.28, wall_len=0.8, obst=0.5, obst_len=0.6)
    ice = ice * ao[..., None]
    # sous piliers : neige tassée + glace sombre
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        base = smooth(r + 0.1, r - 0.1, d)
        ice = comp(ice, hexc('#cfe3f4') * 0.9, base)
        mound = smooth(r + 1.0, r + 0.1, d) * (0.6 + 0.4 * fbm(X * 3, Z * 3, 3, 41))
        ice = comp(ice, hexc('#eaf4fc'), mound * 0.7)
        emission = emission * (1 - base[..., None])
    emission = emission * (1 - smooth(0.0, 0.3, 0.3 - depth)[..., None])
    save('frost_ground.png', ice)
    save('frost_ground_n.png', to_normal(down(h, 2), 3.0, MPP * 2))
    save('frost_ground_e.png', emission)


def tiles():
    tile_ashlar('frost_stone', 512, palette=('#8da3b8', '#7d93a9', '#9db2c6', '#6f869c'), joint='#2d4258', rows=6, block_w=(1.0, 1.9),
                seed=61, wear=0.35, shade=0.1)
    tile_ashlar('frost_stone_light', 512, palette=('#b6c8d9', '#a8bccf', '#c4d4e3', '#9db3c8'), joint='#476079', rows=8, block_w=(0.8, 1.5),
                seed=62, wear=0.3)
    tile_marble('frost_marble', 512, '#d6e6f4', '#b4cbe0', '#7fa0c0', seed=63, strata=0.6)
    tile_snow('frost_snow', 512)
    tile_ice('frost_ice', 512)
    tile_rock('frost_rock', 512, '#3d4a5d', '#6c7d93', '#c3d3e4', seed=64, strata=0.4)
    tile_metal('frost_metal', 512, base='#8a97a8', seed=65, rust=0.0, scale_m=2.0, plates=4)
    tile_noise('frost_cloth', 512, base='#c9d7e8', var=0.1, seed=66, scale=1.2, grain=0.05)
    tile_wood('frost_wood', 512, '#33281f', '#6a513a', seed=67)


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['ground', 'tiles']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
