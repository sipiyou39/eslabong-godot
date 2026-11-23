"""arena_glacier.glb — « Glacier des Géants » : banquise bleutée entourée de crevasses à ponts de neige, falaises glaciaires, stalagmites de glace,
portiques en défenses de mammouth, torches de feu de camp, aurore boréale en fond."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_land import *

T = TP
G.seed(808)
rng = np.random.default_rng(808)

defmat('M_ground', tex=T('glacier_ground'), norm=T('glacier_ground_n'), emit_tex=T('glacier_ground_e'), emit_str=1.1, rough=0.32, uv=1, norm_str=1.0, spec=0.8)
defmat('M_snow', tex=T('glacier_snow'), norm=T('glacier_snow_n'), rough=0.85, uv=6.0, spec=0.3)
defmat('M_cliff', tex=T('glacier_cliff'), norm=T('glacier_cliff_n'), rough=0.4, uv=15.0, spec=0.7)
defmat('M_deep', tex=T('glacier_deep'), norm=T('glacier_deep_n'), rough=0.3, uv=5.0, spec=0.8)
defmat('M_ice', tex=T('glacier_ice'), norm=T('glacier_ice_n'), rough=0.16, uv=4.0, spec=1.0)
defmat('M_rock', tex=T('glacier_rock'), norm=T('glacier_rock_n'), rough=0.92, uv=5.0)
defmat('M_wood', tex=T('glacier_wood'), rough=0.9, uv=3.0)
defmat('M_iron', tex=T('glacier_iron'), norm=T('glacier_iron_n'), rough=0.5, metal=0.6, uv=2.0)
defmat('M_bronze', tex=T('glacier_iron'), norm=T('glacier_iron_n'), rough=0.45, metal=0.65, uv=2.0)
defmat('M_bone', tex=T('glacier_bone'), norm=T('glacier_bone_n'), rough=0.6, uv=2.0)
defmat('M_cloth', tex=T('glacier_cloth'), rough=0.95, uv=2.0, double=True)
defmat('M_flame', emit='#ff9a30', emit_str=2.6, vcol=False, color='#ff9a30')
defmat('M_glow', emit='#7ae8ff', emit_str=0.9, vcol=False, color='#7ae8ff')
defmat('M_pine', rough=0.95, spec=0.1)
defmat('M_gold', rough=0.35, metal=0.9)
defmat('M_dark', rough=0.5, metal=0.6)
defmat('M_aurora', tex=T('glacier_aurora'), emit_tex=T('glacier_aurora'), emit_str=2.0, vcol=False, alpha=True, double=True, rough=1.0)

sc = Scene('arena_glacier')
rr = RR(step=1.0)
walls = sc.part('Walls')
dec = sc.part('Decor')
fx = sc.part('Aurora')
sc.noao.add('Aurora')
build_ground(sc, step=1.0)

BR = [((0.0, -16.0), (0.0, -1.0)), ((0.0, 16.0), (0.0, 1.0)), ((-26.0, 0.0), (-1.0, 0.0)), ((26.0, 0.0), (1.0, 0.0))]


def bridge_lat(x, z):
    """(|latéral| min, along) vis-à-vis de la ligne de pont la plus proche."""
    best = np.full_like(np.asarray(x, float), 99.0)
    for (P, n) in BR:
        al = (x - P[0]) * n[0] + (z - P[1]) * n[1]
        lat = np.abs((x - P[0]) * (-n[1]) + (z - P[1]) * n[0])
        best = np.where(al > -1.0, np.minimum(best, lat), best)
    return best


def hfun(x, z, D):
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    D = np.asarray(D, float)
    n1 = fbm2(x * 0.06 + 7, z * 0.06, 3, 41)
    n2 = fbm2(x * 0.05, z * 0.05 + 9, 3, 42)
    e1 = 2.9 + 0.9 * (2 * n1 - 1) * sstep(0.5, 3.0, D)
    e2 = e1 + 5.0 + 1.9 * (2 * n2 - 1)
    lat = bridge_lat(x, z)
    bsharp = sstep(2.55, 1.65, lat)                        # 1 sur le pont de neige
    # rebord de neige
    rim = 0.5 * sstep(0.0, 0.45, D) * (1 - 0.7 * sstep(e1 - 1.5, e1 - 0.1, D)) * (1 - sstep(e1 - 0.1, e1 + 0.35, D))
    rim = rim + (fbm2(x * 0.55, z * 0.55, 3, 43) - 0.5) * 0.34 * sstep(0.4, 1.2, D) * (1 - sstep(e1 - 0.3, e1 + 0.2, D))
    # crevasse : lèvres verticales, fond en V
    inner = sstep(e1 - 0.10, e1 + 0.42, D)
    outer = 1 - sstep(e2 - 0.42, e2 + 0.10, D)
    mid = np.sin(math.pi * np.clip((D - e1) / np.maximum(e2 - e1, 0.1), 0, 1))
    cre = -(5.2 + 7.0 * mid) * inner * outer
    # terrasse
    terr_amp = sstep(e2 - 0.1, e2 + 0.6, D)
    ter = (0.32 + 1.4 * (fbm2(x * 0.1, z * 0.1, 4, 45) - 0.5) * 2 * sstep(e2, e2 + 7, D) * (1 - sstep(26, 38, D))) * terr_amp
    y = rim + cre + ter
    # pont de neige : comble la crevasse, dos d'âne
    bridge_y = 0.04 + 0.12 * sstep(0.0, 1.5, D) + 0.28 * np.sin(math.pi * np.clip((D - e1 + 0.5) / np.maximum(e2 - e1 + 1.0, 0.1), 0, 1))
    bs = bsharp * (1 - sstep(e2 + 0.3, e2 + 1.5, D))
    y = y * (1 - bs) + bs * bridge_y
    # falaises glaciaires (hautes au fond)
    back = sstep(2.0, -30.0, z)
    Hb = 13.0 + 28.0 * back + 5.0 * sstep(18.0, 36.0, np.abs(x)) * (1 - back)
    D0 = 19.5 - 5.5 * back
    Lw = 27.0
    u = sstep(D0, D0 + Lw, D)
    yw = Hb * u ** 0.85
    yw = yw + (ridge2(x * 0.05, z * 0.05, 4, 47) - 0.35) * 11.0 * sstep(D0, D0 + 12, D)
    yw = yw + (fbm2(x * 0.7, z * 0.2, 3, 49) - 0.5) * 1.4 * u                 # cannelures
    yw = yw + 15.0 * ridge2(x * 0.024, z * 0.024, 3, 48) * sstep(D0 + Lw * 0.65, D0 + Lw + 34, D)   # chaîne lointaine
    y = y + yw
    return y


def H(x, z):
    return hfun(x, z, np.maximum(outline_sdf(x, z), 0.0))


def slope_at(x, z, e=0.7):
    gx = (H(x + e, z) - H(x - e, z)) / (2 * e)
    gz = (H(x, z + e) - H(x, z - e)) / (2 * e)
    return np.hypot(gx, gz)


def tint_terrain(V, D):
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    sl = slope_at(x, z)
    n1 = fbm2(x * 0.1, z * 0.1, 3, 51)
    n2 = fbm2(x * 0.6, z * 0.6, 2, 52)
    snow = np.array([1.0, 1.02, 1.06])
    ice = np.array([0.55, 0.86, 1.12])
    fl = sstep(0.9, 0.35, sl)[:, None]                       # plat -> neige
    col = snow[None, :] * (0.86 + 0.2 * n1[:, None] + 0.08 * (n2[:, None] - 0.5)) * fl + ice[None, :] * (1 - fl) * (0.8 + 0.4 * n1[:, None])
    # crevasse : du bleu glace au bleu nuit
    dp = np.clip((-y - 0.4) / 9.0, 0, 1)
    deep = cgrad(dp, [(0.0, '#7ec4e8'), (0.22, '#2a6aa0'), (0.5, '#0e2e58'), (1.0, '#02060e')])
    wdeep = sstep(0.4, 1.4, -y)[:, None]
    col = col * (1 - wdeep) + deep * wdeep * 1.15
    # sommets : blanc ; brume lointaine bleutée
    far = sstep(45, 140, D)[:, None]
    col = col * (1 - far * 0.35) + far * lin('#9ec4e0')[None, :] * 0.5
    return col


def split_terrain(cx, cy, cz, ny, d):
    if cy < -0.8:
        return 2
    if ny < 0.62:
        return 1
    return 0


ds = [-0.04, 0.12, 0.5, 1.0, 1.6] + list(np.arange(2.0, 11.5, 0.4)) + list(np.arange(12.0, 30.1, 2.0)) + list(np.arange(33.0, 62.1, 3.2)) + list(np.arange(70.0, 142.0, 8.0))
ring_terrain(dec, rr, ds, hfun, ['M_snow', 'M_cliff', 'M_deep'], tintfun=tint_terrain, split=split_terrain)

# ------------------------------------------------------------------ outils locaux


def snow_mound(mb, x, y, z, rx, ry, rz, rng_, tint=(1.0, 1.0, 1.03), n=3):
    for k in range(n):
        V, F = p_ico(1.0, 1)
        a = rng_.uniform(0, TAU)
        off = rng_.uniform(0, 0.45)
        V = V * np.array([rx * rng_.uniform(0.55, 1.0), ry * rng_.uniform(0.6, 1.0), rz * rng_.uniform(0.55, 1.0)]) + np.array([x + math.cos(a) * rx * off, y, z + math.sin(a) * rz * off])
        V[:, 1] = np.maximum(V[:, 1], y - 0.02)
        mb.add((V, F), 'M_snow', tint=tuple(np.array(tint) * rng_.uniform(0.92, 1.05)))


def ice_spike_cluster(mb, x, z, y0, r, hs, rng_, mat='M_ice', seed=0, lean=0.0):
    """grappe de pics de glace (prismes pointus). La base reste dans le rayon r."""
    n = len(hs)
    for i, h in enumerate(hs):
        if i == 0:
            cx, cz, br = 0.0, 0.0, r * 0.5
        else:
            a = TAU * (i - 1) / (n - 1) + rng_.uniform(-0.3, 0.3)
            br = r * rng_.uniform(0.28, 0.4)
            rho = r - br - 0.02
            cx, cz = math.cos(a) * rho, math.sin(a) * rho
        V, F = p_crystal(br * 0.55, h, 5, 0.36, seed + i, lean * (0 if i == 0 else 1) * rng_.uniform(0.4, 1.0), br, 0.12)
        t = np.clip(V[:, 1] / h, 0, 1)
        col = cgrad(t, [(0.0, '#4a98c8'), (0.45, '#9ad4ee'), (1.0, '#f4fbff')])
        a2 = math.atan2(cz, cx) if i else 0
        mb.add((V, F), mat, pos=(x + cx, y0, z + cz), yaw=-a2, tint=col * rng_.uniform(0.9, 1.1))


def pine(mb, x, y, z, h, rng_):
    mb.add(p_cyl(h * 0.035, h * 0.18, 5), 'M_wood', pos=(x, y, z), tint=(0.5, 0.4, 0.35))
    for k in range(3):
        t = k / 3
        r = h * (0.30 - 0.07 * k)
        hh = h * (0.4 - 0.05 * k)
        yy = y + h * (0.12 + 0.27 * k)
        V, F = p_lathe([(r, 0.0), (r * 0.3, hh * 0.55), (0.0, hh)], 6, True, False)
        tt = np.clip(V[:, 1] / hh, 0, 1)
        col = cgrad(tt, [(0.0, '#173a30'), (0.6, '#245447'), (0.85, '#9cb8c0'), (1.0, '#f0f6ff')]) * rng_.uniform(0.85, 1.1)
        mb.add((V, F), 'M_pine', pos=(x, yy, z), yaw=rng_.uniform(0, 3), tint=col)


def tusk(mb, base, lateral_dir, fwd, height, reach, rad0, side, mat='M_bone', n=10, tint=(0.95, 0.9, 0.8)):
    """défense de mammouth en arc : base (x,y,z) ; lateral_dir (x,z) unitaire ; fwd (x,z) unitaire."""
    pts, rads = [], []
    for k in range(n + 1):
        th = (k / n) * math.radians(86)
        lat = side * reach * math.cos(th)
        up = height * math.sin(th)
        fw = 0.9 * math.sin(th * 1.3)
        p = np.array([base[0] + lateral_dir[0] * (lat - side * reach) + fwd[0] * fw, base[1] + up, base[2] + lateral_dir[1] * (lat - side * reach) + fwd[1] * fw])
        pts.append(p)
        rads.append(rad0 * (1 - 0.88 * (k / n) ** 1.3) + 0.02)
    V, F = p_tube(pts, rads, seg=7, cap0=True, cap1=False)
    mb.add((V, F), mat, tint=tint, jit=0.04)


# ------------------------------------------------------------------ portiques en défenses aux extrémités des ponts, braseros
gate_info = []
for gi, (P, n) in enumerate(BR):
    e1_ = 2.9
    pe = (P[0] + n[0] * 10.6, P[1] + n[1] * 10.6)       # côté terrasse
    lat = np.array([-n[1], n[0]])
    y0 = float(H(np.array(pe[0]), np.array(pe[1])))
    for sg in (-1, 1):
        base = np.array([pe[0] + lat[0] * sg * 2.9, y0 - 0.3, pe[1] + lat[1] * sg * 2.9])
        tusk(dec, base, lat, n, height=6.2, reach=2.9, rad0=0.42, side=sg, n=12)
        # socle de glace + brasero
        px, pz = pe[0] + lat[0] * sg * 1.55 + n[0] * 0.2, pe[1] + lat[1] * sg * 1.55 + n[1] * 0.2
        dec.add(p_box(1.15, 1.45, 1.15, top=(0.8, 0.8)), 'M_ice', pos=(px, y0 - 0.2, pz), tint=(0.62, 0.84, 1.0), yaw=math.atan2(n[0], n[1]) + 0.3, bev=0.04)
        brazier(dec, (px, y0 + 1.25, pz), h=0.1, r=0.55, mat='M_iron', tint=(0.3, 0.3, 0.34), flame_h=1.35, seg=8)
        snow_mound(dec, px, y0 - 0.1, pz, 0.9, 0.35, 0.9, rng, n=2)
    sc.empty(f'Light_{gi + 1:02d}', pe[0], y0 + 2.6, pe[1])
    gate_info.append((pe, n))

# ------------------------------------------------------------------ torches : poteaux de bois + vasque de fer, congère à la base
FLAME_Y = 2.2


def glacier_sconce(md, mf, Fp, n, arm):
    x, y, z = Fp
    sconce(md, mf, Fp, n, arm, tint=(0.34, 0.34, 0.38), mat='M_iron', scale=1.15)
    px, pz = x + n[0] * (arm + 0.12), z + n[1] * (arm + 0.12)
    y0 = float(H(np.array(px), np.array(pz))) - 0.3
    md.add(p_lathe([(0.2, 0.0), (0.16, 0.5), (0.15, y - y0 - 0.2), (0.18, y - y0 + 0.1)], 7, True, True, jitter=0.04), 'M_wood', pos=(px, y0, pz), tint=(0.8, 0.7, 0.6))
    # lanières de cuir
    for hh in (0.7, 1.1):
        md.add(p_lathe([(0.19, 0.0), (0.19, 0.08)], 7, False, False), 'M_cloth', pos=(px, y0 + hh, pz), tint=(0.5, 0.35, 0.22))
    snow_mound(md, px, y0 + 0.25, pz, 0.55, 0.3, 0.55, rng, n=2)


for i in range(10):
    x, z, nx, nz, sdv = torch_frame(i)
    sc.empty(f'Torch_{i + 1:02d}', x, FLAME_Y, z)
    arm = max(0.5, -sdv + 0.5)
    glacier_sconce(walls, dec, (x, FLAME_Y, z), (nx, nz), arm)

# ------------------------------------------------------------------ bannières en peau sur hampes (fond et côtés)
bi = 1
for (px, pz) in [(-18.0, -17.4), (-6.0, -17.4), (6.0, -17.4), (18.0, -17.4), (-27.4, -8.0), (27.4, -8.0), (-27.4, 8.0), (27.4, 8.0)]:
    y0 = float(H(np.array(px), np.array(pz))) - 0.2
    ypole = 5.4
    walls.add(p_lathe([(0.13, 0.0), (0.1, ypole)], 6, True, True), 'M_wood', pos=(px, y0, pz), tint=(0.8, 0.7, 0.6))
    walls.add(p_box(1.9, 0.09, 0.09), 'M_wood', pos=(px, y0 + ypole - 0.35, pz), tint=(0.8, 0.7, 0.6), yaw=0.0 if abs(pz) > 10 else math.pi / 2)
    walls.add(p_cone(0.17, 0.5, 5), 'M_bone', pos=(px, y0 + ypole, pz), tint=(0.95, 0.9, 0.8))
    yaw = 0.0 if abs(pz) > 10 else math.pi / 2
    banner_object(sc, f'Banner_{bi:02d}', (px, y0 + ypole - 0.4, pz), yaw + (math.pi if (pz < 0 and abs(pz) > 10) else 0.0), 1.5, 2.6, '#2f5f8a', '#e8d8b0', '#e0a050', phase=bi,
                  mat='M_cloth', rod=False)
    bi += 1

# ------------------------------------------------------------------ cascades gelées sur la falaise du fond
for k, (x_, w_, h_) in enumerate([(-24.0, 3.0, 22.0), (-17.0, 2.2, 18.0), (17.5, 2.5, 20.0), (26.0, 3.4, 24.0), (-33.0, 2.6, 16.0), (33.0, 2.8, 15.0)]):
    zf = -(16.0 + 26.0 + rng.uniform(0, 6))
    # trouve z où la falaise atteint la hauteur de la tête de cascade
    zz = np.linspace(-20, -90, 140)
    hh = H(np.full_like(zz, x_), zz)
    idx = np.argmax(hh > h_ * 0.9)
    zf = float(zz[idx])
    y_top = float(hh[idx])
    y_bot = float(H(np.array(x_), np.array(zf + 8.0))) - 0.5
    dy = y_bot - y_top
    prof = sorted([(w_ * 0.4, 0.0), (w_ * 0.9, dy * 0.3), (w_ * 0.65, dy * 0.55), (w_ * 0.95, dy * 0.9), (w_ * 0.5, dy)], key=lambda p: p[1])
    V_, F_ = p_lathe(prof, 8, False, True, jitter=0.06)
    tt = np.clip((V_[:, 1] - (y_bot - y_top)) / abs(y_bot - y_top), 0, 1)
    dec.add((V_, F_), 'M_ice', pos=(x_, y_top, zf + 1.2), scale=(1.0, 1.0, 0.7), tint=cgrad(tt, [(0.0, '#5aa0d0'), (0.5, '#a8dcf2'), (1.0, '#eefaff')]))
    # base : amas de glace
    ice_spike_cluster(dec, x_, zf + 8.5, y_bot - 0.2, 2.6, [3.0, 2.0, 1.6, 2.4, 1.4], rng, seed=k * 11)

# ------------------------------------------------------------------ pics de glace, séracs, congères sur la terrasse
placed = 0
tries = 0
while placed < 28 and tries < 800:
    tries += 1
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(11.0, 44.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if z > 6 and rng.random() < 0.5:
        continue
    if float(bridge_lat(np.array(x), np.array(z))) < 3.4 and d < 20:
        continue
    big = rng.random() < 0.3
    r = rng.uniform(2.0, 3.4) if big else rng.uniform(1.0, 2.0)
    y0 = float(H(np.array(x), np.array(z))) - 0.4
    hh = [rng.uniform(5, 11) if big else rng.uniform(2.2, 5.0)]
    hh += [hh[0] * rng.uniform(0.35, 0.8) for _ in range(rng.integers(3, 6))]
    ice_spike_cluster(dec, x, z, y0, r, hh, rng, seed=placed * 7, lean=0.4)
    snow_mound(dec, x, y0 + 0.2, z, r * 1.15, 0.45, r * 1.15, rng, n=3)
    placed += 1

# séracs : blocs de glace inclinés
for k in range(26):
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(12.0, 40.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if float(bridge_lat(np.array(x), np.array(z))) < 3.4 and d < 20:
        continue
    w, hgt = rng.uniform(1.6, 4.0), rng.uniform(3.0, 9.0)
    y0 = float(H(np.array(x), np.array(z))) - 0.8
    V_, F_ = p_box(w, hgt, w * rng.uniform(0.6, 1.1), top=(w * 0.6, w * 0.5))
    dec.add((V_, F_), 'M_ice', pos=(x, y0, z), yaw=rng.uniform(0, 3), pitch=rng.uniform(-0.12, 0.12), roll=rng.uniform(-0.12, 0.12),
            tint=(0.6, 0.82, 1.0), bev=0.1, vfun=vgrad(y0, y0 + hgt * 0.9, 0.75, 1.5))

# rochers enneigés
for k in range(44):
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(10.0, 55.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if float(bridge_lat(np.array(x), np.array(z))) < 3.2 and d < 20:
        continue
    s = rng.uniform(0.7, 2.4) * (1 + d / 50)
    y = float(H(np.array(x), np.array(z))) - s * 0.28
    dec.rock((s * 1.3, s, s * 1.2), pos=(x, y, z), mat='M_rock', seed=k, sub=1, tint=(0.6, 0.66, 0.78), yaw=rng.uniform(0, 3))
    snow_mound(dec, x, y + s * 0.62, z, s * 0.62, s * 0.2, s * 0.58, rng, n=2)

# sapins (versants bas)
cnt = 0
tries = 0
while cnt < 52 and tries < 1500:
    tries += 1
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(13.0, 52.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if float(bridge_lat(np.array(x), np.array(z))) < 3.6 and d < 22:
        continue
    y = float(H(np.array(x), np.array(z)))
    if y > 9 or float(slope_at(np.array(x), np.array(z))) > 0.55:
        continue
    pine(dec, x, y - 0.2, z, rng.uniform(4.5, 8.5) * (1 + d / 90), rng)
    cnt += 1

# ------------------------------------------------------------------ aurore boréale (rubans RGBA, peu coûteux)
for k, (zc, y0_, hh_, amp, ph) in enumerate([(-96.0, 38.0, 46.0, 14.0, 0.0), (-112.0, 46.0, 52.0, 18.0, 2.0), (-86.0, 52.0, 34.0, 11.0, 4.0)]):
    nseg = 36
    xs = np.linspace(-110, 110, nseg + 1)
    V, UV, F = [], [], []
    for i, xx in enumerate(xs):
        zz = zc + amp * math.sin(xx * 0.035 + ph) + 6 * math.sin(xx * 0.09 + ph * 2)
        yb = y0_ + 6 * math.sin(xx * 0.05 + ph)
        for j in range(5):
            f = j / 4
            V.append((xx, yb + hh_ * f, zz + 7.0 * f * math.sin(xx * 0.04 + ph + 1.0)))
            UV.append((i / nseg, f))
    for i in range(nseg):
        for j in range(4):
            a = i * 5 + j
            F.append((a, a + 5, a + 6, a + 1))
    fx.add((np.array(V, float), F), 'M_aurora', tint=(1, 1, 1), uv=np.array(UV, float))

# ------------------------------------------------------------------ obstacles : cairns de géants (0,2,4) et stalagmites de glace (1,3,5)


def cairn(mb, x, z, r, h, seed):
    rg = np.random.default_rng(seed)
    y = 0.0
    n = 4
    for k in range(n):
        t = k / (n - 1)
        rad = r * (1.0 - 0.45 * t)
        hh = h * (0.27 - 0.03 * t)
        V_, F_ = p_rock(2 * rad / 1.3, hh * 1.5, 2 * rad / 1.3, int(seed * 13 + k), 1, 0.12, 0.26)
        mb.add((V_, F_), 'M_rock', pos=(x + rg.uniform(-0.1, 0.1), y - 0.04, z + rg.uniform(-0.1, 0.1)), yaw=rg.uniform(0, 3),
               tint=(1.25 + 0.15 * t, 1.3 + 0.1 * t, 1.5), jit=0.1)
        if k in (1, n - 1):
            s_ = rad * (0.75 if k == n - 1 else 0.5)
            V2, F2 = p_ico(1.0, 1)
            V2 = V2 * np.array([s_, hh * 0.25, s_ * 0.9]) + np.array([x + (0.2 if k == 1 else 0.0), y + hh * 0.95, z])
            V2[:, 1] = np.maximum(V2[:, 1], y + hh * 0.82)
            mb.add((V2, F2), 'M_snow', tint=(1.0, 1.0, 1.04))
        y += hh * 0.9
    # défenses croisées + fanion de cuir au sommet
    for sg in (-1, 1):
        pts2, rads2 = [], []
        for k in range(9):
            th = (k / 8) * math.radians(80)
            pts2.append((x + sg * (0.24 + 0.6 * (1 - math.cos(th))), y + 1.15 * math.sin(th), z + 0.15 * math.sin(th * 2)))
            rads2.append(0.1 * (1 - 0.85 * (k / 8) ** 1.2) + 0.012)
        V_, F_ = p_tube(pts2, rads2, seg=6, cap0=True, cap1=False)
        mb.add((V_, F_), 'M_bone', tint=(0.95, 0.9, 0.8))
    mb.add(p_lathe([(0.04, 0.0), (0.03, 1.5)], 5, True, True), 'M_wood', pos=(x, y, z), tint=(0.8, 0.7, 0.6))
    pennant(mb, (x, y, z), 1.35, 0.5, 1.0, 0.7, '#2f5f8a', '#e0a050', mat='M_cloth', wave=0.12, phase=seed)
    # congère au pied
    V2, F2 = p_ico(1.0, 1)
    V2 = V2 * np.array([r * 0.98, 0.22, r * 0.98]) + np.array([x, 0.0, z])
    V2[:, 1] = np.maximum(V2[:, 1], 0.0)
    mb.add((V2, F2), 'M_snow', tint=(1.0, 1.0, 1.04))


def stalagmites(mb, x, z, r, h, seed):
    rg = np.random.default_rng(seed)
    snow_ = r * 0.98
    V2, F2 = p_ico(1.0, 1)
    V2 = V2 * np.array([snow_, 0.28, snow_]) + np.array([x, 0.0, z])
    V2[:, 1] = np.maximum(V2[:, 1], 0.0)
    mb.add((V2, F2), 'M_snow', tint=(1, 1, 1.04))
    hs = [h, h * 0.62, h * 0.52, h * 0.7, h * 0.45]
    n = len(hs)
    for i, hh in enumerate(hs):
        if i == 0:
            cx, cz, br = 0.0, 0.0, r * 0.52
        else:
            a = TAU * (i - 1) / (n - 1) + rg.uniform(-0.2, 0.2)
            br = r * 0.34
            rho = r - br - 0.03
            cx, cz = math.cos(a) * rho, math.sin(a) * rho
        V_, F_ = p_crystal(br * 0.5, hh, 5, 0.42, seed + i, 0.0 if i == 0 else 0.45, br, 0.1)
        t = np.clip(V_[:, 1] / hh, 0, 1)
        col = cgrad(t, [(0.0, '#3c8ac0'), (0.4, '#8ccdee'), (1.0, '#f4fbff')])
        a2 = math.atan2(cz, cx) if i else 0.0
        mb.add((V_, F_), 'M_ice', pos=(x + cx, 0.1, z + cz), yaw=-a2, tint=col * rg.uniform(0.92, 1.08))


for i in range(6):
    mb, o = obstacle_part(sc, i)
    if i in (0, 2, 4):
        cairn(mb, o['x'], o['z'], o['r'], [3.4, 3.2, 3.5][i // 2], i + 5)
    else:
        stalagmites(mb, o['x'], o['z'], o['r'], [3.7, 3.5, 3.9][i // 2], i + 17)

sc.ao_opts = {'Ground': 0.74, 'Decor': 0.55, 'Walls': 0.55}
sc.build(ao_samples=40, ao_dist=3.0, ao_floor=0.5)
sc.export(OUTDIR + '/arena_glacier.glb')
