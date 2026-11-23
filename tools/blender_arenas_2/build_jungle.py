"""arena_jungle.glb — « Temple de la Jungle » : cour d'un temple ancien envahi par la végétation (dallage moussu, calendrier de pierre),
muret éboulé, grand temple à degrés au fond, statues gardiennes, bassin, cascade, arbres à contreforts, lianes, racines, rayons de soleil."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_land import *

T = TP
G.seed(1010)
rng = np.random.default_rng(1010)

defmat('M_ground', tex=T('jungle_ground'), norm=T('jungle_ground_n'), emit_tex=T('jungle_ground_e'), emit_str=0.9, rough=0.85, uv=1, norm_str=1.0, spec=0.3)
defmat('M_stone', tex=T('jungle_stone'), norm=T('jungle_stone_n'), rough=0.88, uv=4.0)
defmat('M_moss', tex=T('jungle_moss'), rough=1.0, uv=6.0)
defmat('M_dirt', tex=T('jungle_dirt'), rough=1.0, uv=6.0)
defmat('M_rock', tex=T('jungle_rock'), norm=T('jungle_rock_n'), rough=0.92, uv=13.0)
defmat('M_bark', tex=T('jungle_bark'), norm=T('jungle_bark_n'), rough=0.95, uv=3.0)
defmat('M_leaf', tex=T('jungle_leaf'), rough=0.85, uv=3.0, double=True)
defmat('M_vine', tex=T('jungle_leaf'), rough=0.9, uv=2.0)
defmat('M_jade', tex=T('jungle_jade'), norm=T('jungle_jade_n'), rough=0.2, spec=1.0, uv=2.0)
defmat('M_jadeglow', emit='#3ae0b8', emit_str=1.0, rough=0.2, spec=1.0)
defmat('M_bronze', tex=T('jungle_bronze'), norm=T('jungle_bronze_n'), rough=0.45, metal=0.7, uv=2.0)
defmat('M_wood', tex=T('jungle_wood'), rough=0.9, uv=3.0)
defmat('M_cloth', tex=T('jungle_cloth'), rough=0.95, uv=2.0, double=True)
defmat('M_gold', rough=0.3, metal=0.9)
defmat('M_dark', rough=0.6, metal=0.2)
defmat('M_water', tex=T('jungle_water'), emit_tex=T('jungle_water'), emit_str=0.07, rough=0.15, spec=1.0, uv=3.0)
defmat('M_flame', emit='#ff8a2c', emit_str=2.4, vcol=False, color='#ff8a2c')
defmat('M_glow', emit='#ffb040', emit_str=1.0, vcol=False, color='#ffb040')
defmat('M_ray', tex=T('jungle_ray'), emit_tex=T('jungle_ray'), emit_str=0.45, vcol=False, alpha=True, double=True, rough=1.0)

sc = Scene('arena_jungle')
rr = RR(step=1.0)
walls = sc.part('Walls')
dec = sc.part('Decor')
water = sc.part('Water')
rays = sc.part('Rays')
sc.noao.add('Rays')
sc.noao.add('Water')
build_ground(sc, step=1.0)

# ------------------------------------------------------------------ relief
FLOOR = -0.8
TEMPLE_Z = -27.0
STREAMS = [dict(x0=-27.0, amp=1.4, fr=0.2, ph=0.3, z0=-70.0, z1=-37.0, w=3.0), dict(x0=28.0, amp=1.4, fr=0.2, ph=2.0, z0=-72.0, z1=-38.0, w=3.4)]


def stream_x(s, z):
    return s['x0'] + s['amp'] * np.sin(np.asarray(z) * s['fr'] + s['ph'])


def pool_mask(x, z):
    a = sstep(-17.6, -18.6, z) * sstep(-27.0, -26.0, z)
    return a * (1 - sstep(22.5, 24.5, np.abs(x)))


def fall_pool(x, z):
    m = np.zeros_like(np.asarray(x, float))
    for s in STREAMS:
        d = np.hypot((x - s['x0']) / 7.5, (z - (s['z1'] + 1.0)) / 5.0)
        m = np.maximum(m, 1 - sstep(0.7, 1.0, d))
    return m


def hfun(x, z, D):
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    D = np.asarray(D, float)
    back = sstep(-6.0, -32.0, z)
    front = sstep(4.0, 20.0, z)
    floor = FLOOR + (fbm2(x * 0.08, z * 0.08, 4, 101) - 0.5) * 1.5 * sstep(1.5, 8, D)
    pm = np.maximum(pool_mask(x, z), fall_pool(x, z))
    y = floor * (1 - pm) + (-1.9) * pm
    hills = (fbm2(x * 0.035, z * 0.035, 4, 102) - 0.32) * 24.0 * sstep(14, 46, D) * (1 - 0.7 * front)
    Hb = 15.0 + 22.0 * back
    D0 = 23.0 - 8.0 * back
    u = sstep(D0, D0 + 30.0, D)
    yw = Hb * u ** 0.9 + (ridge2(x * 0.04, z * 0.04, 3, 103) - 0.35) * 8.0 * sstep(D0, D0 + 12, D)
    yw = yw + (fbm2(x * 0.5, z * 0.5, 3, 104) - 0.5) * 1.2 * u
    yw = yw - 0.5 * np.maximum(D - (D0 + 52), 0) * sstep(D0 + 40, D0 + 60, D)
    return y + hills + yw


def H(x, z):
    return hfun(x, z, np.maximum(outline_sdf(x, z), 0.0))


def slope_at(x, z, e=0.8):
    gx = (H(x + e, z) - H(x - e, z)) / (2 * e)
    gz = (H(x, z + e) - H(x, z - e)) / (2 * e)
    return np.hypot(gx, gz)


def tint_terrain(V, D):
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    n1 = fbm2(x * 0.09, z * 0.09, 3, 111)
    n2 = fbm2(x * 0.6, z * 0.6, 2, 112)
    sl = slope_at(x, z)
    dirt_m = sstep(0.55, 0.72, fbm2(x * 0.16 + 4, z * 0.16, 4, 113))[:, None]
    green = np.stack([0.5 + 0.2 * n1, 0.74 + 0.15 * n1, 0.36 + 0.1 * n2], 1) * (1 - dirt_m) + np.stack([0.72 + 0.1 * n1, 0.62 + 0.1 * n1, 0.5 + 0.06 * n2], 1) * dirt_m
    rock = np.array([0.9, 0.95, 0.8])[None, :] * (0.8 + 0.4 * n1[:, None])
    fl = sstep(0.95, 0.5, sl)[:, None]
    col = green * fl + rock * (1 - fl)
    # terre nue autour des portails et sentiers
    path = np.maximum(sstep(3.5, 1.0, np.abs(x)) * sstep(-18, -26, z) * 0.0, 0.0)
    far = sstep(40, 140, D)[:, None]
    col = col * (1 - far * 0.35) + far * lin('#7aa07a')[None, :] * 0.5
    col = col * (0.75 + 0.35 * sstep(-1.5, 3.0, y)[:, None])
    return col


def split_terrain(cx, cy, cz, ny, d):
    return 1 if ny < 0.72 else 0


ds = [1.2, 1.35, 1.9, 2.8, 4.0, 5.5, 7.5, 10.0, 13.0, 16.0, 19.5, 23.0, 27.0, 31.5, 36.5, 42.0, 48.0, 55.0, 63.0, 72.0, 82.0, 94.0, 108.0, 124.0, 142.0]
ring_terrain(dec, rr, ds, hfun, ['M_moss', 'M_rock'], tintfun=tint_terrain, split=split_terrain)

# ------------------------------------------------------------------ muret éboulé autour de la cour, ouvertures
GATES = [(0.0, -16.0, 6.4), (-26.0, 0.0, 2.4), (26.0, 0.0, 2.4)]
skips = []
for (gx, gz, hw) in GATES:
    s0 = rr.s_nearest(gx, gz)
    skips.append((s0 - hw, s0 + hw))


def h_wall(x, z, D):
    n = fbm2(x * 0.32, z * 0.32, 3, 91)
    Hw = 0.32 + 0.78 * sstep(0.32, 0.55, n) + (fbm2(x * 1.7, z * 1.7, 2, 92) - 0.5) * 0.18
    y = np.where(D < 0.0, 0.0, Hw)
    y = np.where(D > 1.17, FLOOR - 0.2, y)
    y = np.where(D > 1.08, Hw * 0.8, y)
    y = np.where(D > 1.21, FLOOR - 0.2, y)
    y = np.where(D < 0.0, 0.0, y)
    return y


def tint_wall(V, D):
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    m = sstep(0.45, 0.75, fbm2(x * 0.45, z * 0.45, 3, 93)) * sstep(0.0, 0.4, y)
    stone = np.array([0.9, 0.9, 0.84])
    moss = np.array([0.5, 0.95, 0.38])
    col = stone[None, :] * (1 - m[:, None]) + moss[None, :] * m[:, None]
    return col * (0.8 + 0.3 * fbm2(x * 2, z * 2, 2, 94))[:, None]


ring_terrain(walls, rr, [-0.04, 0.04, 0.6, 1.1, 1.22], h_wall, 'M_stone', tintfun=tint_wall, skip=skips)

# chaussée vers le temple, paliers des portes latérales
walls.add(p_box(12.0, 1.3, 11.4), 'M_stone', pos=(0.0, -1.3, -21.6), tint=(0.85, 0.85, 0.8), bev=0.03)
walls.add(p_box(26.0, 1.3, 4.4), 'M_stone', pos=(0.0, -1.3, -25.0), tint=(0.85, 0.85, 0.8), bev=0.03)
for sg in (-1, 1):
    walls.add(p_box(5.0, 1.3, 4.6), 'M_stone', pos=(sg * 28.4, -1.3, 0.0), tint=(0.85, 0.85, 0.8), bev=0.03)
    for k in range(3):
        walls.add(p_box(5.0, 0.28, 0.9), 'M_stone', pos=(sg * (31.1 + 0.8 * k), -1.3 + 1.3 - 0.28 * (k + 1) + 0.0, 0.0), yaw=math.pi / 2, tint=(0.85, 0.85, 0.8))
# bassin devant le temple
wq = [(-26.0, -1.15, -17.4), (26.0, -1.15, -17.4), (26.0, -1.15, -27.0), (-26.0, -1.15, -27.0)]
water.add(p_quad(wq[0], wq[1], wq[2], wq[3]), 'M_water', tint=(0.16, 0.36, 0.32))


# ------------------------------------------------------------------ utilitaires végétaux
def vine(mb, x, y, z, L, rng_, rad=0.045, n=7):
    pts = []
    sx, sz = rng_.uniform(-0.5, 0.5), rng_.uniform(-0.5, 0.5)
    for k in range(n + 1):
        t = k / n
        pts.append((x + sx * math.sin(t * 2.5) * 0.6 * L * 0.1, y - L * t, z + sz * math.sin(t * 2.0) * 0.6 * L * 0.1))
    V, F = p_tube(pts, [rad * (1 - 0.5 * k / n) for k in range(n + 1)], seg=3, cap0=False, cap1=False)
    t = np.clip((y - V[:, 1]) / L, 0, 1)
    mb.add((V, F), 'M_vine', tint=cgrad(t, [(0.0, '#3a6a24'), (1.0, '#6a9a34')]) * rng_.uniform(0.85, 1.1))


def leaf_blob(mb, x, y, z, r, rng_, sub=1, flat=0.62, c_lo='#2c5a22', c_hi='#8ab83a'):
    V, F = p_ico(1.0, sub)
    V = V * np.array([r, r * flat, r]) + np.array([x, y, z])
    t = np.clip((V[:, 1] - (y - r * flat)) / (2 * r * flat), 0, 1)
    mb.add((V, F), 'M_leaf', tint=cgrad(t, [(0.0, c_lo), (0.5, '#4e8a2a'), (1.0, c_hi)]) * rng_.uniform(0.85, 1.12))


def big_tree(mb, x, y0, z, h, rng_):
    lean = rng_.uniform(-1, 1) * h * 0.05
    pts = [(x, y0 - 0.6, z), (x + lean * 0.2, y0 + h * 0.3, z), (x + lean * 0.6, y0 + h * 0.65, z + lean * 0.3), (x + lean, y0 + h, z + lean * 0.4)]
    V, F = p_tube(pts, [1.2, 0.85, 0.62, 0.45], seg=7, cap0=False, cap1=True)
    mb.add((V, F), 'M_bark', tint=(0.95, 0.9, 0.85))
    for k in range(5):
        a = TAU * k / 5 + rng_.uniform(-0.3, 0.3)
        ca, sa = math.cos(a), math.sin(a)
        rp = [(x + ca * 0.5, y0 + 2.8, z + sa * 0.5), (x + ca * 1.3, y0 + 1.3, z + sa * 1.3), (x + ca * 2.4, y0 + 0.3, z + sa * 2.4), (x + ca * 3.6, y0 - 0.3, z + sa * 3.6)]
        V, F = p_tube(rp, [0.5, 0.4, 0.28, 0.16], seg=5, cap0=False, cap1=True)
        mb.add((V, F), 'M_bark', tint=(0.9, 0.85, 0.78))
    cx, cz = x + lean, z + lean * 0.4
    for k in range(7):
        a = rng_.uniform(0, TAU)
        rho = rng_.uniform(0.0, 0.42) * h
        r = h * rng_.uniform(0.2, 0.32)
        bx_, bz_ = cx + math.cos(a) * rho, cz + math.sin(a) * rho
        if float(outline_sdf(np.array(bx_), np.array(bz_))) < r * 0.9 + 1.0:
            continue
        leaf_blob(mb, bx_, y0 + h + rng_.uniform(-0.12, 0.14) * h, bz_, r, rng_, sub=1 if k < 4 else 0)
    for k in range(5):
        a = rng_.uniform(0, TAU)
        rho = rng_.uniform(0.15, 0.4) * h
        vine(mb, cx + math.cos(a) * rho, y0 + h * 0.95, cz + math.sin(a) * rho, rng_.uniform(0.35, 0.7) * h, rng_)


def palm(mb, x, y, z, h, rng_):
    lean = rng_.uniform(-0.8, 0.8)
    pts = [(x, y - 0.2, z), (x + lean * 0.3, y + h * 0.5, z + lean * 0.1), (x + lean, y + h, z + lean * 0.3)]
    V, F = p_tube(pts, [0.2, 0.15, 0.1], seg=5, cap0=False, cap1=True)
    mb.add((V, F), 'M_bark', tint=(0.95, 0.9, 0.8))
    top = np.array([x + lean, y + h, z + lean * 0.3])
    for k in range(8):
        a = TAU * k / 8 + rng_.uniform(-0.2, 0.2)
        L = rng_.uniform(2.1, 3.0)
        w = 0.55
        dh = np.array([math.cos(a), 0.0, math.sin(a)])
        sd = np.array([-dh[2], 0.0, dh[0]])
        Vf, Ff = [], []
        n = 6
        for i in range(n + 1):
            t = i / n
            c = top + dh * L * t + np.array([0, 0.5 * math.sin(math.pi * t * 0.8) - 1.1 * t * t, 0]) * L * 0.5
            ww = w * (1 - t) ** 0.7 * (1 + 0.5 * math.sin(math.pi * t))
            Vf.append(c - sd * ww)
            Vf.append(c + sd * ww)
        for i in range(n):
            Ff.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
        Vf = np.array(Vf, float)
        t = np.clip((Vf[:, 1] - (y + h - 1)) / 2.0, 0, 1)
        mb.add((Vf, Ff), 'M_leaf', tint=cgrad(t, [(0.0, '#2c5a22'), (1.0, '#8ab83a')]) * rng_.uniform(0.85, 1.1))


def face_block(mb, x, y, z, yaw, s=1.0, tint=(0.9, 0.9, 0.84), eyes=True):
    """tête sculptée (bloc, arcades, nez, bouche, yeux de jade)."""
    mb.add(p_box(1.0 * s, 1.1 * s, 0.9 * s, top=(0.92 * s, 0.82 * s)), 'M_stone', pos=(x, y, z), yaw=yaw, tint=tint, bev=0.03)
    cy, sy = math.cos(yaw), math.sin(yaw)

    def fp(lx, ly, lz):
        return (x + lx * cy + lz * sy, y + ly, z - lx * sy + lz * cy)
    mb.add(p_box(0.92 * s, 0.14 * s, 0.14 * s), 'M_stone', pos=fp(0, 0.72 * s, 0.46 * s), yaw=yaw, tint=tint)
    mb.add(p_box(0.16 * s, 0.34 * s, 0.16 * s), 'M_stone', pos=fp(0, 0.34 * s, 0.46 * s), yaw=yaw, tint=tint)
    mb.add(p_box(0.5 * s, 0.1 * s, 0.08 * s), 'M_dark', pos=fp(0, 0.14 * s, 0.46 * s), yaw=yaw, tint=(0.2, 0.2, 0.18))
    if eyes:
        for sg in (-1, 1):
            mb.add(p_box(0.17 * s, 0.14 * s, 0.1 * s), 'M_jadeglow', pos=fp(sg * 0.26 * s, 0.58 * s, 0.46 * s), yaw=yaw, tint=(1, 1, 1))


def statue(mb, x, y, z, yaw, s=1.0):
    t = (0.88, 0.9, 0.82)
    mb.add(p_box(2.3 * s, 0.9 * s, 2.3 * s), 'M_stone', pos=(x, y, z), yaw=yaw, tint=t, bev=0.04)
    mb.add(p_box(1.9 * s, 1.5 * s, 1.7 * s, top=(1.6 * s, 1.4 * s)), 'M_stone', pos=(x, y + 0.9 * s, z), yaw=yaw, tint=t, bev=0.04)
    mb.add(p_box(1.5 * s, 1.9 * s, 1.2 * s, top=(1.2 * s, 1.0 * s)), 'M_stone', pos=(x, y + 2.4 * s, z), yaw=yaw, tint=t, bev=0.04)
    cy, sy = math.cos(yaw), math.sin(yaw)
    for sg in (-1, 1):
        mb.add(p_box(0.5 * s, 1.5 * s, 0.6 * s), 'M_stone', pos=(x + sg * 1.0 * s * cy, y + 2.5 * s, z - sg * 1.0 * s * sy), yaw=yaw, tint=t, bev=0.03)
    face_block(mb, x, y + 4.3 * s, z, yaw, s=1.15 * s, tint=t)
    # coiffe à plumes
    for k in range(7):
        a = (k - 3) * 0.32
        lx = math.sin(a) * 1.2 * s
        ly = math.cos(a) * 1.1 * s
        fx, fz = x + lx * cy, z - lx * sy
        col = (0.2, 0.7, 0.55) if k % 2 == 0 else (0.85, 0.65, 0.2)
        mb.add(p_box(0.28 * s, 1.0 * s, 0.1 * s, top=(0.1 * s, 0.06 * s)), 'M_cloth', pos=(fx, y + 4.9 * s + ly * 0.1, fz), yaw=yaw, roll=-a, tint=col)
    # collier de jade
    mb.add(p_lathe([(0.8 * s, 0.0), (0.9 * s, 0.1), (0.8 * s, 0.2)], 8, False, False), 'M_jade', pos=(x, y + 3.9 * s, z), tint=(1, 1, 1))


# ------------------------------------------------------------------ temple à degrés + escalier central
STAIR_N = 28
S_TOP = 12.8
tiers = [(34.0, 14.0, 2.6), (28.5, 11.5, 6.0), (23.0, 9.0, 9.4), (17.5, 6.5, S_TOP)]


def moss_fac(y0, y1):
    def f(V):
        t = np.clip((V[:, 1] - y0) / max(y1 - y0, 1e-3), 0, 1)[:, None]
        low = np.array([0.55, 0.88, 0.42])
        hi = np.array([1.0, 1.0, 0.95])
        return low * (1 - t) + hi * t
    return f


for k, (w, d, top) in enumerate(tiers):
    zf = TEMPLE_Z - 2.45 * k
    base = tiers[k - 1][2] if k else -1.8
    h = top - base
    dec.add(p_box(w, h, d), 'M_stone', pos=(0.0, base, zf - d / 2), tint=(0.92, 0.9, 0.84), bev=0.05, vfun=moss_fac(base, top))
    # corniche saillante
    dec.add(p_box(w + 0.5, 0.32, d + 0.5), 'M_stone', pos=(0.0, top - 0.32, zf - d / 2), tint=(0.95, 0.93, 0.86), bev=0.03)
    # frise de losanges de jade sur la face avant (hors escalier)
    if k % 2 == 1:
        for sg in (-1, 1):
            xs = np.arange(5.0 + 0.9, w / 2 - 0.9, 1.5)
            for xx in xs:
                dec.add(p_box(0.55, 0.55, 0.12), 'M_jade', pos=(sg * xx, base + h * 0.45, zf + 0.04), yaw=0.0, roll=math.pi / 4, tint=(1, 1, 1))
# escalier
STAIR_Z0 = TEMPLE_Z + 2.6 / (3.4 / 2.45)          # la rampe suit la ligne des coins avant des degrés
STAIR_Z1 = TEMPLE_Z - 2.45 * 3
rise = S_TOP / STAIR_N
tread = (STAIR_Z0 - STAIR_Z1) / STAIR_N
pts_ = [(0.0, -1.4), (0.0, 0.0)]
for i in range(STAIR_N):
    pts_.append((tread * i, rise * (i + 1)))
    pts_.append((tread * (i + 1), rise * (i + 1)))
pts_ += [(tread * STAIR_N, -1.4)]
dec.add(p_extrude_xy(pts_, -3.7, 3.7), 'M_stone', pos=(0.0, 0.0, STAIR_Z0), yaw=math.pi / 2, tint=(0.96, 0.94, 0.88), vfun=moss_fac(0.0, 6.0))
# balustrades inclinées
for sg in (-1, 1):
    path = [(sg * 4.05, 0.3, STAIR_Z0 + 0.4), (sg * 4.05, S_TOP + 0.3, STAIR_Z1)]
    pp = [(-0.35, 0.0), (0.35, 0.0), (0.3, 0.9), (-0.3, 0.9)]
    dec.add(p_sweep(pp, path, caps=True), 'M_stone', tint=(0.9, 0.88, 0.82), vfun=moss_fac(0.0, 8.0))
    dec.add(p_box(0.9, 1.6, 0.9, top=(0.7, 0.7)), 'M_stone', pos=(sg * 4.05, -0.3, STAIR_Z0 + 0.9), tint=(0.9, 0.88, 0.82), bev=0.03)
    face_block(dec, sg * 4.05, 1.3, STAIR_Z0 + 0.9, 0.0, s=0.8)
# sanctuaire au sommet
sz_f = TEMPLE_Z - 2.45 * 4
arch_block(dec, (0.0, sz_f - 1.2), (0.0, 1.0), 9.4, 4.8, 2.6, 2.2, 1.8, mat='M_stone', y0=S_TOP, tint=(0.92, 0.9, 0.84), glow_mat='M_glow', glow_tint=(1, 1, 1))
dec.add(p_box(9.4, 4.8, 3.2), 'M_stone', pos=(0.0, S_TOP, sz_f - 3.6 - 1.2), tint=(0.92, 0.9, 0.84), bev=0.04)
dec.add(p_box(11.2, 0.7, 6.4), 'M_stone', pos=(0.0, S_TOP + 4.8, sz_f - 2.7), tint=(0.95, 0.93, 0.86), bev=0.05)
dec.add(p_box(8.6, 3.0, 0.9, top=(5.2, 0.6)), 'M_stone', pos=(0.0, S_TOP + 5.5, sz_f - 2.7), tint=(0.9, 0.88, 0.82), bev=0.03, vfun=moss_fac(S_TOP + 5, S_TOP + 8))
for sg in (-1, 1):
    brazier(dec, (sg * 5.2, S_TOP + 0.1, sz_f + 0.3), h=0.9, r=0.42, mat='M_dark', tint=(0.3, 0.28, 0.24), flame_h=1.3, seg=8)
    face_block(dec, sg * 3.9, S_TOP + 2.6, sz_f - 0.1, 0.0, s=0.75)
sc.empty('Light_01', -5.2, S_TOP + 2.2, sz_f + 0.3)
sc.empty('Light_02', 5.2, S_TOP + 2.2, sz_f + 0.3)
sc.empty('Light_03', 0.0, S_TOP + 2.0, sz_f - 2.0)

# statues gardiennes sur le parvis
statue(dec, -9.5, 0.0, -24.8, 0.0, 1.0)
statue(dec, 9.5, 0.0, -24.8, 0.0, 1.0)
for sg in (-1, 1):
    for xx in (sg * 14.0, sg * 19.0):
        face_block(dec, xx, 0.0, -24.8, 0.0, s=1.0)

# ------------------------------------------------------------------ torches : colonnes de pierre + vasque de bronze
FLAME_Y = 2.2


def jungle_sconce(md, mf, Fp, n, arm):
    x, y, z = Fp
    sconce(md, mf, Fp, n, arm, tint=(0.6, 0.5, 0.3), mat='M_bronze', scale=1.15)
    px, pz = x + n[0] * (arm + 0.12), z + n[1] * (arm + 0.12)
    y0 = 0.25
    md.add(p_lathe([(0.34, 0.0), (0.3, 0.3), (0.26, y - y0 - 0.5), (0.34, y - y0 - 0.25), (0.42, y - y0 - 0.12), (0.42, y - y0 + 0.05)], 8, True, True), 'M_stone', pos=(px, y0, pz), tint=(0.9, 0.9, 0.82))
    vine(md, px + 0.2, y - 0.3, pz, 1.2, rng)


for i in range(10):
    x, z, nx, nz, sdv = torch_frame(i)
    sc.empty(f'Torch_{i + 1:02d}', x, FLAME_Y, z)
    arm = max(0.5, -sdv + 0.5)
    jungle_sconce(walls, dec, (x, FLAME_Y, z), (nx, nz), arm)

# têtes sculptées sur le muret + bannières
Pp, Np, Tp, sp = rr.along(9.0, 0.6, offset=2.0)
cnt = 0
for i in range(len(Pp)):
    px, pz = Pp[i]
    if pz > 8 and abs(px) < 22:
        continue
    if any(math.hypot(px - gx, pz - gz) < hw + 1.5 for (gx, gz, hw) in GATES):
        continue
    if any(math.hypot(px - t['x'], pz - t['z']) < 2.2 for t in TORCHES):
        continue
    walls.add(p_box(0.9, 1.5, 0.9, top=(0.8, 0.8)), 'M_stone', pos=(px, 0.2, pz), yaw=yaw_of(Np[i][0], Np[i][1]), tint=(0.9, 0.9, 0.82), bev=0.03)
    face_block(walls, px, 1.65, pz, yaw_of(-Np[i][0], -Np[i][1]), s=0.85)
    cnt += 1
bi = 1
for (px, pz) in [(-18.0, -16.7), (-9.0, -16.7), (9.0, -16.7), (18.0, -16.7), (-26.7, -9.0), (26.7, -9.0), (-26.7, 8.0), (26.7, 8.0)]:
    s_ = rr.s_nearest(px, pz)
    Pw, nn = rr.at_base(s_)
    bx, bz = Pw[0] + nn[0] * 0.6, Pw[1] + nn[1] * 0.6
    walls.add(p_lathe([(0.1, 0.0), (0.07, 3.2)], 6, True, True), 'M_wood', pos=(bx, 0.2, bz), tint=(0.8, 0.7, 0.55))
    walls.add(p_box(1.5, 0.08, 0.08), 'M_wood', pos=(bx, 3.0, bz), yaw=math.atan2(nn[0], nn[1]) + math.pi / 2, tint=(0.8, 0.7, 0.55))
    banner_object(sc, f'Banner_{bi:02d}', (bx, 3.0, bz), math.atan2(nn[0], nn[1]), 1.3, 2.4, '#a8452a' if bi % 2 else '#2a8a74', '#e0b040', '#e0b040', phase=bi, mat='M_cloth', rod=False)
    bi += 1

# ------------------------------------------------------------------ cascades + bassins
for s in STREAMS:
    zs = np.arange(s['z0'], s['z1'] + 0.01, 1.8)
    path = np.stack([stream_x(s, zs), zs], 1)
    wd = s['w'] * (0.85 + 0.2 * np.sin(zs * 0.4)) * (0.55 + 0.6 * np.clip((zs - s['z0']) / 14, 0, 1))
    drape_ribbon(water, path, wd, H, 'M_water', yoff=0.55, across=5, tint=(0.9, 1.0, 1.0), uvlen=3.0, edge_sink=0.5)
    px, pz = s['x0'], s['z1'] + 1.0
    water.add(p_lathe([(0.0, 0.0), (7.0, 0.0)], 14, False, True), 'M_water', pos=(px, -1.25, pz), tint=(0.16, 0.36, 0.32), scale=(1.0, 1.0, 0.7))
    for k in range(9):
        a = rng.uniform(0, TAU)
        leaf_blob(dec, px + math.cos(a) * rng.uniform(0.5, 3.2), -1.0, pz + math.sin(a) * rng.uniform(0.5, 2.2) - 1.0, rng.uniform(0.7, 1.3), rng, sub=1, flat=0.55, c_lo='#d8f0f0', c_hi='#ffffff')

# ------------------------------------------------------------------ arbres, palmiers, buissons, rochers moussus
placed = 0
tries = 0
while placed < 13 and tries < 600:
    tries += 1
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(7.0, 34.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if z > 6 or (abs(x) < 20 and -45 < z < -16) or (abs(z) < 5 and abs(x) > 24 and d < 10):
        continue
    if float(fall_pool(np.array(x), np.array(z))) > 0.05 or float(slope_at(np.array(x), np.array(z))) > 0.7:
        continue
    y0 = float(H(np.array(x), np.array(z)))
    big_tree(dec, x, y0, z, rng.uniform(15, 23), rng)
    placed += 1
# arbres de lisière côté +Z (bas)
for k in range(9):
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(5.0, 22.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if z < 4 or abs(z) < 5 and abs(x) > 24:
        continue
    y0 = float(H(np.array(x), np.array(z)))
    palm(dec, x, y0, z, rng.uniform(4.5, 7.5), rng)
for k in range(10):
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(4.0, 22.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if float(pool_mask(np.array(x), np.array(z))) > 0.05 or (abs(x) < 20 and -45 < z < -16):
        continue
    y0 = float(H(np.array(x), np.array(z)))
    palm(dec, x, y0, z, rng.uniform(5, 8), rng)
for k in range(70):
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(2.5, 28.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if float(pool_mask(np.array(x), np.array(z))) > 0.05 or (abs(x) < 22 and -46 < z < -16) or (abs(z) < 3 and abs(x) > 24 and d < 10):
        continue
    y0 = float(H(np.array(x), np.array(z)))
    leaf_blob(dec, x, y0 + 0.2, z, rng.uniform(0.7, 1.6), rng, sub=0, flat=0.7)
for k in range(46):
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(3.0, 40.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if float(pool_mask(np.array(x), np.array(z))) > 0.05 or (abs(x) < 20 and -46 < z < -16):
        continue
    s = rng.uniform(0.8, 2.6) * (1 + d / 60)
    y = float(H(np.array(x), np.array(z))) - s * 0.25
    dec.rock((s * 1.3, s, s * 1.2), pos=(x, y, z), mat='M_rock', seed=k, sub=1, tint=(0.7, 0.9, 0.55), yaw=rng.uniform(0, 3))
# sous-bois dense autour du muret : fougères et touffes
def fern(mb, x, y, z, s, rng_):
    for k in range(7):
        a = TAU * k / 7 + rng_.uniform(-0.3, 0.3)
        L = s * rng_.uniform(0.9, 1.3)
        dh = np.array([math.cos(a), 0.0, math.sin(a)])
        sd = np.array([-dh[2], 0.0, dh[0]])
        Vf, Ff = [], []
        n = 4
        for i in range(n + 1):
            t = i / n
            c = np.array([x, y + 0.1, z]) + dh * L * t + np.array([0, 0.55 * math.sin(math.pi * t * 0.9) - 0.5 * t * t, 0]) * L * 0.6
            ww = 0.34 * s * (1 - t) ** 0.6 * (1 + 0.4 * math.sin(math.pi * t))
            Vf.append(c - sd * ww)
            Vf.append(c + sd * ww)
        for i in range(n):
            Ff.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
        Vf = np.array(Vf, float)
        tt = np.clip((Vf[:, 1] - y) / (0.7 * s), 0, 1)
        mb.add((Vf, Ff), 'M_leaf', tint=cgrad(tt, [(0.0, '#27501e'), (1.0, '#7ab038')]) * rng_.uniform(0.8, 1.1))


tries = 0
cnt = 0
while cnt < 50 and tries < 900:
    tries += 1
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(1.7, 9.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if float(pool_mask(np.array(x), np.array(z))) > 0.05 or (abs(x) < 8.2 and z < -16) or (abs(z) < 3 and abs(x) > 24 and d < 10) or (abs(x) < 14 and -28 < z < -16):
        continue
    if any(math.hypot(x - t_['x'], z - t_['z']) < 2.4 for t_ in TORCHES):
        continue
    y0 = float(H(np.array(x), np.array(z)))
    fern(dec, x, y0, z, rng.uniform(1.0, 1.7), rng)
    cnt += 1
# racines qui enjambent le muret (finissent à ras du dallage)
for k in range(9):
    for _t in range(20):
        P, n_ = rr.at_base(rng.uniform(0, rr.length()))
        if all(math.hypot(P[0] - gx, P[1] - gz) > hw + 1.5 for (gx, gz, hw) in GATES) and not (P[1] > 8 and abs(P[0]) < 22):
            break
    tang = np.array([-n_[1], n_[0]])
    wob = rng.uniform(-1.5, 1.5)
    pts = []
    for t_, (dd, yy) in enumerate([(7.0, FLOOR + 0.1), (4.5, FLOOR + 0.6), (2.6, FLOOR + 1.3), (1.4, 1.35), (0.7, 1.25), (0.35, 0.5), (0.1, 0.2), (0.02, 0.06)]):
        q = P + n_ * dd + tang * (wob * (dd / 7.0) ** 2)
        pts.append((q[0], yy, q[1]))
    V, F = p_tube(pts, [0.32, 0.28, 0.24, 0.2, 0.18, 0.15, 0.08, 0.03], seg=5, cap0=True, cap1=True)
    dec.add((V, F), 'M_bark', tint=(0.9, 0.85, 0.78))
# lianes sur le muret
for k in range(26):
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    if any(math.hypot(P[0] - gx, P[1] - gz) < hw + 1.0 for (gx, gz, hw) in GATES) or (P[1] > 8 and abs(P[0]) < 22):
        continue
    q = P + n_ * 1.05
    vine(dec, q[0], 1.0, q[1], rng.uniform(1.0, 1.9), rng, rad=0.04, n=5)
# canopées sur les versants
for k in range(70):
    a = rng.uniform(0, TAU)
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(26.0, 70.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if z > 12 and rng.random() < 0.6:
        continue
    y = float(H(np.array(x), np.array(z)))
    r = rng.uniform(3.0, 7.0)
    leaf_blob(dec, x, y + r * 0.3, z, r, rng, sub=0, flat=0.7)
# lianes pendues sur les degrés du temple
for k in range(16):
    tier = int(rng.integers(0, 4))
    w, d_, top = tiers[tier]
    zf = TEMPLE_Z - 2.45 * tier
    xx = rng.uniform(-w / 2 + 1.0, w / 2 - 1.0)
    if abs(xx) < 4.6:
        continue
    vine(dec, xx, top - 0.1, zf + 0.15, rng.uniform(1.8, 3.6), rng, rad=0.06)

# ------------------------------------------------------------------ rayons de soleil (hors du terrain de jeu)
for (x, z, tilt, yaw, w, hh) in [(-39.0, -12.0, 0.28, 0.4, 9.0, 26.0), (33.0, -22.0, -0.28, -0.3, 10.0, 26.0),
                                (-40.0, 7.0, 0.25, 0.5, 8.0, 24.0), (38.0, 10.0, -0.25, -0.5, 8.0, 24.0)]:
    y0 = float(H(np.array(x), np.array(z)))
    for a in (0.0, math.pi / 2):
        yw_ = yaw + a
        c, s_ = math.cos(yw_), math.sin(yw_)
        dx, dz = c * w / 2, -s_ * w / 2
        tx_ = tilt * hh
        P0 = (x - dx, y0, z - dz)
        P1 = (x + dx, y0, z + dz)
        P2 = (x + dx + tx_, y0 + hh, z + dz)
        P3 = (x - dx + tx_, y0 + hh, z - dz)
        Vq = np.array([P0, P1, P2, P3], float)
        rays.add((Vq, [(0, 1, 2, 3)]), 'M_ray', tint=(1, 1, 1), uv=np.array([(0, 0), (1, 0), (1, 1), (0, 1)], float))


# ------------------------------------------------------------------ obstacles : piliers-totems moussus (0,2,4), autels de jade (1,3,5)
def totem_pillar(mb, x, z, r, h, seed):
    rg = np.random.default_rng(seed)
    mb.add(p_lathe([(r, 0.0), (r, 0.3), (r * 0.9, 0.42)], 12, True, True), 'M_stone', pos=(x, 0, z), tint=(0.9, 0.9, 0.82))
    n = 3
    y = 0.42
    for k in range(n):
        rad = r * (0.78 - 0.08 * k)
        hh = (h - 1.3) / n
        mb.add(p_lathe([(rad * 0.98, 0.0), (rad * 1.0, hh * 0.1), (rad * 0.94, hh * 0.9), (rad * 1.02, hh)], 12, False, True), 'M_stone', pos=(x, y, z),
               yaw=rg.uniform(0, 1), tint=(0.88, 0.9, 0.8), jit=0.06, vfun=None)
        mb.add(p_lathe([(rad * 1.0, 0.0), (rad * 1.06, 0.04), (rad * 1.06, 0.1), (rad * 1.0, 0.14)], 12, False, False), 'M_jade', pos=(x, y + hh - 0.02, z), tint=(1, 1, 1))
        # visage gravé sur chaque tambour (face tournée vers l'extérieur du terrain central)
        ang = rg.uniform(0, TAU)
        fx, fz = x + math.cos(ang) * rad * 0.98, z + math.sin(ang) * rad * 0.98
        mb.add(p_box(rad * 0.7, hh * 0.45, 0.07), 'M_stone', pos=(fx, y + hh * 0.3, fz), yaw=math.atan2(math.cos(ang), math.sin(ang)), tint=(0.8, 0.84, 0.72))
        for sg in (-1, 1):
            ex = fx + math.sin(ang) * sg * rad * 0.2 * -1
            ez = fz + math.cos(ang) * sg * rad * 0.2
            mb.add(p_box(0.1, 0.08, 0.06), 'M_jadeglow', pos=(ex, y + hh * 0.62, ez), yaw=math.atan2(math.cos(ang), math.sin(ang)), tint=(1, 1, 1))
        y += hh
    # chapiteau
    mb.add(p_box(r * 1.5, 0.3, r * 1.5, top=(r * 1.75, r * 1.75)), 'M_stone', pos=(x, y, z), tint=(0.92, 0.9, 0.84), yaw=rg.uniform(0, 1), bev=0.03)
    mb.add(p_box(r * 1.35, 0.1, r * 1.35), 'M_jade', pos=(x, y + 0.3, z), tint=(1, 1, 1), yaw=0.0)
    # liane en spirale
    pts = []
    for k in range(34):
        t = k / 33
        a = t * TAU * 2.3 + seed
        pts.append((x + math.cos(a) * r * 0.74, 0.5 + t * (h - 1.1), z + math.sin(a) * r * 0.74))
    V, F = p_tube(pts, 0.06, seg=3, cap0=False, cap1=False)
    mb.add((V, F), 'M_vine', tint=(0.28, 0.5, 0.2))


def jade_altar(mb, x, z, r, h, seed):
    mb.add(p_lathe([(r, 0.0), (r, 0.45), (r * 0.9, 0.6), (r * 0.84, 0.62)], 8, True, True, phase=math.pi / 8), 'M_stone', pos=(x, 0, z), tint=(0.9, 0.9, 0.82))
    mb.add(p_lathe([(r * 0.78, 0.0), (r * 0.78, 0.55), (r * 0.7, 0.7), (r * 0.62, 0.72)], 8, False, True, phase=math.pi / 8), 'M_stone', pos=(x, 0.6, z), tint=(0.86, 0.88, 0.8))
    mb.add(p_lathe([(r * 0.5, 0.0), (r * 0.46, 0.9), (r * 0.52, 1.0)], 8, False, True, phase=math.pi / 8), 'M_stone', pos=(x, 1.3, z), tint=(0.88, 0.9, 0.82))
    mb.add(p_lathe([(r * 0.82, 0.0), (r * 0.86, 0.04), (r * 0.86, 0.1), (r * 0.82, 0.14)], 8, False, False, phase=math.pi / 8), 'M_jade', pos=(x, 0.5, z), tint=(1, 1, 1))
    V, F = p_crystal(r * 0.22, h - 2.4, 6, 0.3, seed, 0.0, r * 0.36, 0.05)
    mb.add((V, F), 'M_jadeglow', pos=(x, 2.4, z), tint=(1, 1, 1))
    for k in range(4):
        a = TAU * k / 4 + 0.4
        V, F = p_crystal(r * 0.1, 0.9 + 0.3 * (k % 2), 5, 0.4, seed + k, 0.3, r * 0.17, 0.05)
        mb.add((V, F), 'M_jadeglow', pos=(x + math.cos(a) * r * 0.3, 2.4, z + math.sin(a) * r * 0.3), yaw=-a, tint=(1, 1, 1))
    # mousse sur le socle
    V, F = p_ico(1.0, 1)
    V = V * np.array([r * 0.9, 0.2, r * 0.9]) + np.array([x, 0.5, z])
    mb.add((V, F), 'M_moss', tint=(0.6, 1.0, 0.5))


for i in range(6):
    mb, o = obstacle_part(sc, i)
    if i in (0, 2, 4):
        totem_pillar(mb, o['x'], o['z'], o['r'], [3.7, 3.5, 3.8][i // 2], i + 3)
    else:
        jade_altar(mb, o['x'], o['z'], o['r'], [3.6, 3.4, 3.7][i // 2], i + 9)

sc.ao_opts = {'Ground': 0.74, 'Decor': 0.55, 'Walls': 0.58}
sc.build(ao_samples=40, ao_dist=3.0, ao_floor=0.5)
sc.export(OUTDIR + '/arena_jungle.glb')
