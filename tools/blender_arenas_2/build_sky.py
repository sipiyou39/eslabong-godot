"""arena_sky.glb — « Îles des Nuages » : grande plate-forme de pierre claire flottante (rebords, rose des vents solaire),
îlots flottants, ponts de cordes, voiles et drapeaux, mer de nuages dorés, soleil couchant."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_land import *

T = TP
G.seed(909)
rng = np.random.default_rng(909)

defmat('M_ground', tex=T('sky_ground'), norm=T('sky_ground_n'), emit_tex=T('sky_ground_e'), emit_str=0.8, rough=0.62, uv=1, norm_str=1.0, spec=0.5)
defmat('M_stone', tex=T('sky_stone'), norm=T('sky_stone_n'), rough=0.8, uv=4.0)
defmat('M_marble', tex=T('sky_marble'), norm=T('sky_marble_n'), rough=0.45, uv=4.0, spec=0.7)
defmat('M_rock', tex=T('sky_rock'), norm=T('sky_rock_n'), rough=0.92, uv=6.0)
defmat('M_grass', tex=T('sky_grass'), rough=0.95, uv=5.0)
defmat('M_wood', tex=T('sky_wood'), rough=0.85, uv=3.0)
defmat('M_rope', tex=T('sky_rope'), rough=1.0, uv=1.5)
defmat('M_cloth', tex=T('sky_cloth'), rough=0.95, uv=2.0, double=True)
defmat('M_leaf', tex=T('sky_leaf'), rough=0.9, uv=3.0)
defmat('M_plaster', tex=T('sky_plaster'), rough=0.9, uv=3.0)
defmat('M_roof', tex=T('sky_roof'), rough=0.8, uv=2.0)
defmat('M_bronze', tex=T('sky_bronze'), norm=T('sky_bronze_n'), rough=0.4, metal=0.8, uv=2.0)
defmat('M_gold', rough=0.3, metal=0.9)
defmat('M_dark', rough=0.5, metal=0.5)
defmat('M_cloud', emit='#ff9050', emit_str=0.10, rough=1.0, spec=0.0)
defmat('M_flame', emit='#ffa040', emit_str=2.4, vcol=False, color='#ffa040')
defmat('M_glow', emit='#ffc060', emit_str=1.0, vcol=False, color='#ffc060')
defmat('M_sun', emit='#ffd890', emit_str=3.0, vcol=False, color='#ffd890')
defmat('M_sunglow', emit='#ff9a50', emit_str=0.9, vcol=False, color='#ff9a50')
defmat('M_water', emit='#9fd8ff', emit_str=0.12, rough=0.2, spec=0.8)

sc = Scene('arena_sky')
rr = RR(step=1.0)
walls = sc.part('Walls')
dec = sc.part('Decor')
far = sc.part('Clouds')
sunp = sc.part('Sun')
sc.noao.add('Sun')

# ------------------------------------------------------------------ sol : plateforme (pas d'apron débordant le bord de dalle)
V_, F_, UV_ = ground_mesh(step=1.0, apron=0.7)
sc.part('Ground').add((V_, F_), 'M_ground', uv=UV_)

# ------------------------------------------------------------------ ponts de cordes : positions (point du bord, normale sortante)
BR = [((-6.0, -16.0), (0.0, -1.0)), ((6.0, -16.0), (0.0, -1.0)), ((-26.0, 0.0), (-1.0, 0.0)), ((26.0, 0.0), (1.0, 0.0))]
GAP = 1.9
skips = []
for (P, n) in BR:
    s0 = rr.s_nearest(P[0], P[1])
    skips.append((s0 - GAP, s0 + GAP))

STONE_T = (1.0, 0.97, 0.9)
# rebord : parapet à moulure + dalle épaisse
add_strip(walls, rr, [(0.02, 0.0), (0.02, 0.5), (0.1, 0.56), (0.1, 0.66)], 'M_marble', 'in', STONE_T, skips, 4.0)
add_strip(walls, rr, [(0.1, 0.66), (0.7, 0.66)], 'M_marble', 'up', STONE_T, skips, 4.0)
add_strip(walls, rr, [(0.7, 0.66), (0.7, 0.3), (0.7, 0.0)], 'M_marble', 'out', STONE_T, skips, 4.0)
add_strip(walls, rr, [(0.7, 0.0), (0.7, -0.55), (0.7, -1.1)], 'M_stone', 'out', (0.95, 0.92, 0.85), None, 4.0)
# bande d'or sur la moulure
add_strip(walls, rr, [(0.1, 0.64), (0.1, 0.5)], 'M_gold', 'in', (0.85, 0.65, 0.25), skips, 4.0)
# extrémités des ouvertures (bouts du parapet)
for (P, n) in BR:
    s0 = rr.s_nearest(P[0], P[1])
    for sg in (-1, 1):
        Pw, nn = rr.at_base(s0 + sg * GAP)
        c = Pw + nn * 0.4
        walls.add(p_box(0.78, 1.25, 0.78), 'M_marble', pos=(c[0], 0.0, c[1]), yaw=yaw_of(nn[0], nn[1]), tint=STONE_T, bev=0.03)
        walls.add(p_box(0.95, 0.16, 0.95), 'M_stone', pos=(c[0], 1.22, c[1]), yaw=yaw_of(nn[0], nn[1]), tint=STONE_T)
        walls.add(p_lathe([(0.0, 0.0), (0.16, 0.08), (0.2, 0.2), (0.14, 0.34), (0.0, 0.4)], 8, False, False), 'M_gold', pos=(c[0], 1.35, c[1]), tint=(0.85, 0.65, 0.25))

# ------------------------------------------------------------------ dessous : dalle, roche en entonnoir, stalactites
UX = [-4.6, -3.8, -2.6, -1.4, -0.4, 0.3, 0.68, 0.7]
UY = [-14.0, -11.6, -8.4, -5.4, -3.2, -2.0, -1.3, -1.1]


def h_under(x, z, D):
    y = np.interp(D, UX, UY)
    y = y + (fbm2(x * 0.25, z * 0.25, 4, 61) - 0.5) * 3.2 * sstep(0.0, -2.4, D)
    return y


def tint_under(V, D):
    y = V[:, 1]
    t = np.clip((-y - 1.0) / 13.0, 0, 1)
    col = cgrad(t, [(0.0, '#d8bd96'), (0.35, '#a87c58'), (0.75, '#6e4a3a'), (1.0, '#4a3030')])
    return col * (0.85 + 0.3 * fbm2(V[:, 0] * 0.4, V[:, 2] * 0.4, 3, 62))[:, None]


ds_u = [0.7, 0.3, -0.4, -1.4, -2.6, -3.8, -4.6]
ring_terrain(dec, rr, ds_u, h_under, 'M_rock', tintfun=tint_under, flip=True)
cap_poly = [(float(p[0]), float(p[1])) for p in rr.pts(-4.6)[0][::2]]
dec.add(p_extrude_xz(cap_poly, -14.6, -14.0), 'M_rock', tint=(0.5, 0.4, 0.36), jit=0.0)
# gros pic central + stalactites
dec.add(p_lathe([(11.0, 0.0), (9.0, -3.5), (6.5, -9.0), (4.0, -16.0), (2.0, -24.0), (0.0, -34.0)], 14, False, False, jitter=0.1), 'M_rock', pos=(0, -14.4, 0),
        scale=(1.85, 1.0, 1.0), tint=(0.5, 0.4, 0.36))
for k in range(9):
    a = rng.uniform(0, TAU)
    px, pz = math.cos(a) * rng.uniform(8, 18) * 1.2, math.sin(a) * rng.uniform(4, 9)
    L = rng.uniform(7, 16)
    dec.add(p_lathe([(rng.uniform(1.8, 3.4), 0.0), (1.2, -L * 0.5), (0.0, -L)], 7, False, False, jitter=0.12), 'M_rock', pos=(px, -14.2, pz), tint=(0.55, 0.43, 0.38))

# ------------------------------------------------------------------ mer de nuages dorés
CLOUD_Y = -17.0


def h_cloud(x, z, D):
    return CLOUD_Y + (fbm2(x * 0.05, z * 0.05, 3, 71) - 0.5) * 3.5


def tint_cloud(V, D):
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    n = fbm2(x * 0.1, z * 0.1, 3, 73)
    col = cgrad(0.5 + (n - 0.5) * 0.9, [(0.0, '#e8985c'), (0.4, '#f8c888'), (0.75, '#ffe6b4'), (1.0, '#fff4da')])
    far_ = sstep(40, 150, D)[:, None]
    return col * (1 - far_ * 0.15) + far_ * lin('#ffb470')[None, :] * 0.3


ds_c = [3.0, 6.0, 10.0, 15.0, 22.0, 32.0, 46.0, 64.0, 90.0, 125.0, 170.0]
ring_terrain(far, rr, ds_c, h_cloud, 'M_cloud', tintfun=tint_cloud)

# bourrelet de nuages collé au pourtour de l'île
P_, N_, T_, s_ = rr.along(5.6, -1.6, offset=0.5)
for i in range(len(P_)):
    y = rng.uniform(-6.5, -2.2)
    sz = rng.uniform(2.2, 3.6)
    cloud(far, P_[i, 0] + N_[i, 0] * rng.uniform(0, 1.2), y, P_[i, 1] + N_[i, 1] * rng.uniform(0, 1.2), sz * 1.3, sz * 0.7, sz * 1.3, rng, n=2,
          top='#fff0d8', bot='#f4b890')
# cumulus dispersés (blobs lissés ; sub=0 pour les petits/lointains)
for k in range(78):
    a = rng.uniform(0, TAU)
    Rr = rng.uniform(0.15, 1.0) ** 0.8
    px, pz = math.cos(a) * (Rr * 100 + 14), math.sin(a) * (Rr * 62 + 9)
    if float(outline_sdf(np.array(px), np.array(pz))) < 5:
        continue
    sz = rng.uniform(4.0, 10.0) * (1 + Rr * 0.6)
    cloud(far, px, rng.uniform(-17.0, -9.0), pz, sz * 1.6, sz * 0.75, sz * 1.3, rng, n=3, top='#fff4dc', bot='#f2a878', sub=1 if sz > 7 else 0)
for k in range(12):
    a = math.radians(rng.uniform(205, 335))
    Rr = rng.uniform(110, 170)
    sz = rng.uniform(18, 34)
    cloud(far, math.cos(a) * Rr, rng.uniform(-8, 22), math.sin(a) * Rr, sz * 1.8, sz * 0.9, sz * 1.5, rng, n=4, top='#ffeacc', bot='#f0985e')


# ------------------------------------------------------------------ ponts de cordes
def rope_bridge(mb, p0, p1, y0, y1, width=1.9, sag=0.8, n=20):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = float(np.hypot(d[0], d[1]))
    yaw = math.atan2(d[0], d[1])
    side = np.array([math.cos(yaw), -math.sin(yaw)])
    ts = (np.arange(n) + 0.5) / n
    ycen = lambda t: y0 + (y1 - y0) * t - sag * 4 * t * (1 - t)
    pos = np.array([[p0[0] + d[0] * t, ycen(t), p0[1] + d[1] * t] for t in ts])
    dy = np.array([(y1 - y0) - sag * 4 * (1 - 2 * t) for t in ts])
    pitch = -np.arctan2(dy, L)
    tint = np.tile(s2l((0.8, 0.62, 0.42)), (n, 1)) * rng.uniform(0.8, 1.15, (n, 1))
    mb.add_many(p_box(width, 0.08, (L / n) * 0.82), 'M_wood', pos, yaw=np.full(n, yaw), pitch=pitch, tint=tint)
    # mains courantes + filins bas
    for sg in (-1, 1):
        for (h, rad) in ((1.0, 0.05), (0.05, 0.04)):
            pts = []
            for k in range(13):
                t = k / 12
                c = np.array([p0[0] + d[0] * t, 0.0, p0[1] + d[1] * t]) + np.array([side[0], 0.0, side[1]]) * sg * (width / 2)
                c[1] = ycen(t) + h - (0.12 * 4 * t * (1 - t) if h > 0.5 else 0.0)
                pts.append(c)
            V, F = p_tube(pts, rad, seg=4, cap0=False, cap1=False)
            mb.add((V, F), 'M_rope', tint=(0.85, 0.7, 0.5))
        # tirants verticaux
        for k in range(1, n, 3):
            t = ts[k]
            c = np.array([p0[0] + d[0] * t, ycen(t), p0[1] + d[1] * t]) + np.array([side[0], 0.0, side[1]]) * sg * (width / 2)
            mb.add(p_box(0.03, 0.98 - 0.12 * 4 * t * (1 - t), 0.03), 'M_rope', pos=(c[0], c[1] + 0.04, c[2]), tint=(0.85, 0.7, 0.5))
    # poteaux d'extrémité
    for (pp, yy) in ((p0, y0), (p1, y1)):
        for sg in (-1, 1):
            c = np.array([pp[0], yy, pp[1]]) + np.array([side[0], 0.0, side[1]]) * sg * (width / 2 + 0.05)
            mb.add(p_box(0.2, 1.7, 0.2), 'M_wood', pos=(c[0], c[1] - 0.1, c[2]), tint=(0.7, 0.55, 0.4), yaw=yaw, bev=0.02)
            mb.add(p_lathe([(0.0, 0.0), (0.14, 0.06), (0.1, 0.2), (0.0, 0.26)], 6, False, False), 'M_bronze', pos=(c[0], c[1] + 1.6, c[2]), tint=(0.95, 0.8, 0.5))


# ------------------------------------------------------------------ îlots
def tree(mb, x, y, z, h, rng_):
    lean = rng_.uniform(-0.5, 0.5) * h * 0.2
    pts = [(x, y - 0.2, z), (x + lean * 0.3, y + h * 0.35, z), (x + lean * 0.8, y + h * 0.7, z + lean * 0.3), (x + lean, y + h, z + lean * 0.4)]
    V, F = p_tube(pts, [0.2 * h / 4, 0.15 * h / 4, 0.11 * h / 4, 0.08 * h / 4], seg=5, cap0=False, cap1=False)
    mb.add((V, F), 'M_wood', tint=(0.75, 0.6, 0.45))
    for k in range(4):
        a = rng_.uniform(0, TAU)
        rho = rng_.uniform(0, 0.9) * h * 0.4
        V, F = p_ico(1.0, 1)
        rr_ = h * rng_.uniform(0.28, 0.45)
        V = V * np.array([rr_, rr_ * 0.5, rr_]) + np.array([x + lean + math.cos(a) * rho, y + h + rng_.uniform(-0.15, 0.25) * h * 0.3, z + lean * 0.4 + math.sin(a) * rho])
        t = np.clip((V[:, 1] - (y + h * 0.8)) / (h * 0.5), 0, 1)
        mb.add((V, F), 'M_leaf', tint=cgrad(t, [(0.0, '#4a7a30'), (0.5, '#7aa63a'), (1.0, '#c8c450')]) * rng_.uniform(0.9, 1.1))


def columns_ruin(mb, x, y, z, yaw, rng_):
    for k, dx in enumerate((-1.6, 1.6)):
        cx, cz = x + math.cos(yaw) * dx, z - math.sin(yaw) * dx
        h = 3.2 if k == 0 else 2.2
        mb.add(p_lathe([(0.45, 0.0), (0.38, 0.2), (0.34, h * 0.9), (0.4, h), (0.46, h + 0.15)], 10, True, True, flutes=(8, 0.06)), 'M_marble', pos=(cx, y, cz), tint=(1.0, 0.96, 0.88))
    mb.add(p_box(4.1, 0.38, 0.8), 'M_marble', pos=(x, y + 3.35, z), yaw=yaw, tint=(1.0, 0.96, 0.88), bev=0.03)


def islet(x, y, z, rad, depth, rng_, trees=2, kind='tree', waterfall=False):
    prof = [(0.0, -depth), (rad * 0.16, -depth * 0.85), (rad * 0.45, -depth * 0.52), (rad * 0.8, -depth * 0.2), (rad * 0.97, -0.5), (rad, -0.05)]
    V, F = p_lathe(prof, 10, False, False, jitter=0.1)
    V = V + np.array([x, y, z])
    t = np.clip((y - V[:, 1]) / depth, 0, 1)
    dec.add((V, F), 'M_rock', tint=cgrad(t, [(0.0, '#d2b088'), (0.4, '#a67a58'), (1.0, '#5a3a30')]) * rng_.uniform(0.9, 1.1))
    V, F = p_lathe([(rad, -0.05), (rad * 0.55, 0.18), (0.0, 0.3)], 10, False, False, jitter=0.04)
    V = V + np.array([x, y, z])
    dec.add((V, F), 'M_grass', tint=cgrad(fbm2(V[:, 0] * 0.3, V[:, 2] * 0.3, 2, 81), [(0.0, '#8aa84a'), (0.5, '#a8b858'), (1.0, '#d0c870')]))
    # rochers de lisière
    for k in range(3):
        a = rng_.uniform(0, TAU)
        s = rng_.uniform(0.4, 1.0)
        dec.rock((s * 1.3, s, s), pos=(x + math.cos(a) * rad * 0.8, y + 0.05, z + math.sin(a) * rad * 0.8), mat='M_rock', seed=k, sub=1, tint=(1.0, 0.85, 0.7), yaw=a)
    for k in range(trees):
        a = rng_.uniform(0, TAU)
        rho = rng_.uniform(0.15, 0.6) * rad
        tree(dec, x + math.cos(a) * rho, y + 0.25, z + math.sin(a) * rho, rng_.uniform(3.2, 5.0), rng_)
    if kind == 'ruin':
        columns_ruin(dec, x, y + 0.25, z, rng_.uniform(0, 3), rng_)
    elif kind == 'house':
        building(dec, (x, y + 0.25, z), 2.6, 2.2, 2.0, yaw=rng_.uniform(0, 3), mat='M_plaster', tint=(1.0, 0.95, 0.85), roof='gable', roof_tint=(1.0, 0.8, 0.7))
    if waterfall:
        a = rng_.uniform(0, TAU)
        L = rng_.uniform(7, 12)
        dec.add(p_box(0.5, L, 0.18, top=(1.2, 0.42)), 'M_water', pos=(x + math.cos(a) * (rad - 0.2), y - L + 0.05, z + math.sin(a) * (rad - 0.2)), yaw=-a + math.pi / 2,
                tint=(0.8, 0.92, 1.0), vfun=vgrad(y - L, y, 0.55, 1.0))
        cloud(far, x + math.cos(a) * (rad - 0.2), y - L + 0.2, z + math.sin(a) * (rad - 0.2), 4.0, 2.2, 4.0, rng_, n=3, top='#ffffff', bot='#f8d0b0')


# îlots des ponts
isl_pos = []
for i, (P, n) in enumerate(BR):
    rad = [6.0, 7.5, 6.5, 7.0][i]
    dd = 14.0 + rad * 0.9
    cx, cz = P[0] + n[0] * dd, P[1] + n[1] * dd
    cy = [-0.35, 0.4, -0.2, 0.2][i]
    islet(cx, cy, cz, rad, rad * 1.1, rng, trees=2 + i % 2, kind=['ruin', 'house', 'tree', 'ruin'][i], waterfall=(i % 2 == 0))
    isl_pos.append((cx, cz, rad))
    p0 = (P[0] + n[0] * 0.7, P[1] + n[1] * 0.7)
    p1 = (P[0] + n[0] * (dd - rad * 0.92), P[1] + n[1] * (dd - rad * 0.92))
    rope_bridge(dec, p0, p1, 0.0, cy + 0.15, width=1.9, sag=0.9, n=18)

# îlots d'ambiance
tries = 0
cnt = 0
while cnt < 11 and tries < 400:
    tries += 1
    a = rng.uniform(0, TAU)
    Rr = rng.uniform(34, 95)
    px, pz = math.cos(a) * Rr * 1.5, math.sin(a) * Rr * 1.05
    if float(outline_sdf(np.array(px), np.array(pz))) < 16:
        continue
    rad = rng.uniform(3.0, 9.0)
    if any(math.hypot(px - q[0], pz - q[1]) < rad + q[2] + 6 for q in isl_pos):
        continue
    py = rng.uniform(-9, 12)
    islet(px, py, pz, rad, rad * rng.uniform(1.0, 1.7), rng, trees=int(rng.integers(0, 3)), kind=rng.choice(['tree', 'ruin', 'house', 'tree']), waterfall=rng.random() < 0.4)
    isl_pos.append((px, pz, rad))
    cnt += 1

# ------------------------------------------------------------------ poteaux de rebord, torches, mâts à voiles, bannières
excl = [(P[0], P[1], 2.6) for (P, n) in BR]
FLAME_Y = 2.2
MASTS = [(-20.0, -16.0), (-9.0, -16.0), (9.0, -16.0), (20.0, -16.0), (-15.0, 16.0), (15.0, 16.0), (-26.0, -8.0), (-26.0, 8.0), (26.0, -8.0), (26.0, 8.0)]


def sky_sconce(md, mf, Fp, n, arm):
    x, y, z = Fp
    sconce(md, mf, Fp, n, arm, tint=(0.8, 0.62, 0.3), mat='M_bronze', scale=1.1)
    px, pz = x + n[0] * (arm + 0.12), z + n[1] * (arm + 0.12)
    yaw = yaw_of(n[0], n[1])
    md.add(p_box(0.36, y - 0.55, 0.36, top=(0.26, 0.26)), 'M_marble', pos=(px, 0.66, pz), yaw=yaw, tint=STONE_T, bev=0.02)
    md.add(p_box(0.5, 0.14, 0.5), 'M_stone', pos=(px, y - 0.47, pz), yaw=yaw, tint=STONE_T)
    md.add(p_box(0.5, 0.2, 0.5, top=(0.34, 0.34)), 'M_stone', pos=(px, 0.66, pz), yaw=yaw, tint=STONE_T)


for i in range(10):
    x, z, nx, nz, sdv = torch_frame(i)
    sc.empty(f'Torch_{i + 1:02d}', x, FLAME_Y, z)
    arm = max(0.5, -sdv + 0.5)
    sky_sconce(walls, dec, (x, FLAME_Y, z), (nx, nz), arm)
    excl.append((x, z, 1.7))
for (mx, mz) in MASTS:
    excl.append((mx, mz, 1.5))

# poteaux de parapet
Pp, Np, Tp, sp = rr.along(3.3, 0.4, offset=0.9)
for i in range(len(Pp)):
    px, pz = Pp[i]
    if any(math.hypot(px - ex, pz - ez) < er for ex, ez, er in excl):
        continue
    yaw = yaw_of(Np[i][0], Np[i][1])
    walls.add(p_box(0.5, 0.5, 0.5, top=(0.4, 0.4)), 'M_marble', pos=(px, 0.66, pz), yaw=yaw, tint=STONE_T, bev=0.02)
    walls.add(p_lathe([(0.0, 0.0), (0.15, 0.06), (0.17, 0.2), (0.11, 0.34), (0.0, 0.42)], 7, False, False), 'M_gold', pos=(px, 1.14, pz), tint=(0.85, 0.65, 0.25))


def sail(base, mast_h, boom, yaw, c_main, c_edge, bi, nout):
    x, y, z = base
    dec.add(p_lathe([(0.17, 0.0), (0.1, mast_h)], 6, True, True), 'M_wood', pos=(x, y, z), tint=(0.7, 0.55, 0.4))
    tx, tz = math.cos(yaw), -math.sin(yaw)   # tangente
    gh = 1.7
    dec.add(p_box(boom, 0.11, 0.11), 'M_wood', pos=(x + tx * boom / 2, y + gh, z + tz * boom / 2), yaw=yaw + math.pi / 2, tint=(0.7, 0.55, 0.4))
    # voile triangulaire bombée
    nu, nv = 6, 7
    V, Fq, tt = [], [], []
    for iu in range(nu + 1):
        u = iu / nu
        for iv in range(nv + 1):
            v = iv / nv
            hh = (mast_h - 0.6 - gh) * (1 - u * 0.92)
            px_ = x + tx * u * boom * 0.97
            pz_ = z + tz * u * boom * 0.97
            py_ = y + gh + 0.12 + v * hh
            bil = 0.75 * math.sin(math.pi * min(u * 1.1, 1.0)) * math.sin(math.pi * v) * (0.5 + 0.5 * (1 - u))
            nx_, nz_ = nout
            V.append((px_ + nx_ * bil, py_, pz_ + nz_ * bil))
            edge = (u > 0.9) or (v < 0.07) or (iu == 0)
            tt.append(lin(c_edge) if edge else lin(c_main))
    for iu in range(nu):
        for iv in range(nv):
            a = iu * (nv + 1) + iv
            Fq.append((a, a + nv + 1, a + nv + 2, a + 1))
    dec.add((np.array(V, float), Fq), 'M_cloth', tint=np.array(tt))
    # hauban
    top = (x, y + mast_h - 0.5, z)
    end = (x + tx * boom, y + gh, z + tz * boom)
    Vt, Ft = p_tube([top, ((top[0] + end[0]) / 2, (top[1] + end[1]) / 2 - 0.05, (top[2] + end[2]) / 2), end], 0.03, seg=4, cap0=False, cap1=False)
    dec.add((Vt, Ft), 'M_rope', tint=(0.85, 0.7, 0.5))
    # fanion en tête de mât
    pennant(dec, (x, y, z), mast_h, 0.5, 1.5, yaw + 0.3, c_edge, c_main, mat='M_cloth', wave=0.18, phase=bi)


SAILC = [('#f2e4c0', '#c8452a'), ('#d9733a', '#f2e4c0'), ('#f2e4c0', '#2a7a8a'), ('#c8452a', '#f2e4c0'), ('#f2e4c0', '#d9a53a')]
bi = 1
for k, (mx, mz) in enumerate(MASTS):
    s_ = rr.s_nearest(mx, mz)
    Pw, nn = rr.at_base(s_)
    base = (Pw[0] + nn[0] * 0.4, 0.66, Pw[1] + nn[1] * 0.4)
    tang = np.array([-nn[1], nn[0]])
    yaw = math.atan2(-tang[1], tang[0])     # tx = cos(yaw), tz = -sin(yaw)
    cm, ce = SAILC[k % len(SAILC)]
    sail(base, 8.2 - (k % 3) * 0.8, 4.2, yaw, cm, ce, k, (float(nn[0]), float(nn[1])))
    # bannière suspendue au bout de la bôme
    bx, bz = base[0] + math.cos(yaw) * 3.6, base[2] - math.sin(yaw) * 3.6
    banner_object(sc, f'Banner_{bi:02d}', (bx, 0.66 + 1.75, bz), math.atan2(nn[0], nn[1]), 1.1, 2.1, ce, cm, '#d9a53a', phase=k, mat='M_cloth', rod=False)
    bi += 1

# lumières supplémentaires
sc.empty('Light_01', -20.0, 7.5, -17.2)
sc.empty('Light_02', 20.0, 7.5, -17.2)
sc.empty('Light_03', -26.9, 7.5, 0.0)
sc.empty('Light_04', 26.9, 7.5, 0.0)

# ------------------------------------------------------------------ soleil couchant
sunp.add(p_cyl(15.0, 0.6, 28), 'M_sun', pos=(0, 30.0, -200.0), pitch=math.pi / 2, tint=(1, 1, 1))
sunp.add(p_cyl(34.0, 0.4, 28), 'M_sunglow', pos=(0, 30.0, -200.6), pitch=math.pi / 2, tint=(1, 1, 1))
sunp.add(p_cyl(62.0, 0.3, 28), 'M_sunglow', pos=(0, 28.0, -201.2), pitch=math.pi / 2, tint=(1, 1, 1))


# ------------------------------------------------------------------ obstacles : piliers solaires (0,2,4) et cairns de nuage (1,3,5)
def sun_pillar(mb, x, z, r, h):
    mb.add(p_lathe([(r, 0.0), (r, 0.28), (r * 0.9, 0.38), (r * 0.74, 0.46)], 14, True, True), 'M_stone', pos=(x, 0, z), tint=(1, 0.96, 0.88))
    mb.add(p_lathe([(r * 0.8, 0.0), (r * 0.64, 0.12), (r * 0.58, h - 1.1), (r * 0.66, h - 0.95), (r * 0.78, h - 0.8)], 14, False, True, flutes=(10, 0.06)), 'M_marble', pos=(x, 0.45, z), tint=(1.0, 0.97, 0.9))
    mb.add(p_lathe([(r * 0.76, 0.0), (r * 0.82, 0.05), (r * 0.82, 0.12), (r * 0.76, 0.17)], 14, False, False), 'M_gold', pos=(x, 0.55, z), tint=(0.85, 0.65, 0.25))
    mb.add(p_lathe([(r * 0.78, 0.0), (r * 0.84, 0.05), (r * 0.84, 0.12), (r * 0.78, 0.17)], 14, False, False), 'M_gold', pos=(x, h - 1.0, z), tint=(0.85, 0.65, 0.25))
    yc = h + 0.55
    # emblème solaire : couronne d'or + rayons
    mb.add(p_lathe([(r * 0.55, h - 0.65), (r * 0.7, h - 0.5), (r * 0.5, h - 0.4)], 12, False, True), 'M_marble', pos=(x, 0.0, z), tint=(1, 0.97, 0.9))
    mb.add(p_torus(0.5, 0.075, 18, 6), 'M_gold', pos=(x, yc, z), tint=(0.9, 0.7, 0.28), pitch=math.pi / 2, yaw=0.4)
    for k in range(12):
        a = TAU * k / 12
        L = 0.34 if k % 2 == 0 else 0.22
        cx_, cy_ = math.cos(a) * 0.58, math.sin(a) * 0.58
        px = x + cx_ * math.cos(0.4)
        pz = z - cx_ * math.sin(0.4)
        mb.add(p_cone(0.07, L, 4), 'M_gold', pos=(px, yc + cy_, pz), tint=(0.9, 0.7, 0.28), yaw=0.4, roll=a - math.pi / 2)
    V, F = p_ico(0.2, 1)
    mb.add((V, F), 'M_glow', pos=(x, yc, z), tint=(1, 1, 1))


def cloud_cairn(mb, x, z, r, h, seed):
    rg = np.random.default_rng(seed)
    y = 0.0
    n = 5
    for k in range(n):
        t = k / (n - 1)
        rad = r * (1.0 - 0.5 * t) * 0.98
        hh = h * (0.26 - 0.03 * t)
        V, F = p_ico(1.0, 1)
        V = V * np.array([rad * 0.97, hh * 0.62, rad * 0.97])
        V[:, 0] += rg.uniform(-0.05, 0.05)
        V = V + np.array([x, y + hh * 0.48, z])
        V[:, 1] = np.maximum(V[:, 1], y)
        mb.add((V, F), 'M_marble', tint=(1.0, 0.96 - 0.04 * (k % 2), 0.88), jit=0.05)
        if k in (1, 3):
            mb.add(p_lathe([(rad * 0.9, 0.0), (rad * 0.95, 0.07), (rad * 0.9, 0.14)], 12, False, False), 'M_bronze', pos=(x, y + hh * 0.5, z), tint=(0.95, 0.8, 0.5))
        y += hh * 0.8
    mb.add(p_lathe([(0.035, 0.0), (0.03, 1.55)], 5, True, True), 'M_wood', pos=(x, y, z), tint=(0.7, 0.55, 0.4))
    pennant(mb, (x, y, z), 1.45, 0.55, 1.1, 0.5, '#c8452a', '#f2e4c0', mat='M_cloth', wave=0.13, phase=seed)
    V, F = p_ico(0.16, 1)
    mb.add((V, F), 'M_glow', pos=(x, y + 1.7, z), tint=(1, 1, 1))


for i in range(6):
    mb, o = obstacle_part(sc, i)
    if i in (0, 2, 4):
        sun_pillar(mb, o['x'], o['z'], o['r'], [3.6, 3.4, 3.7][i // 2])
    else:
        cloud_cairn(mb, o['x'], o['z'], o['r'], [3.4, 3.2, 3.5][i // 2], i + 31)

sc.ao_opts = {'Ground': 0.76, 'Decor': 0.55, 'Walls': 0.6, 'Clouds': 0.85}
sc.build(ao_samples=36, ao_dist=3.0, ao_floor=0.5)
sc.export(OUTDIR + '/arena_sky.glb')
