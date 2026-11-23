"""arena_atlantis.glb — « Atlantide » : temple sous-marin de Poséidon, colonnes de marbre à chapiteaux de corail, coquillages géants,
tridents dorés, rayons de lumière bleu-vert, bulles, poissons."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from greek_common import *

T = lambda n: TEXDIR + '/' + n
G.seed(901)
rng = np.random.default_rng(901)

defmat('M_ground', tex=T('atlantis_ground.png'), norm=T('atlantis_ground_n.png'), rough=0.4, metal=0.0, uv=1, norm_str=0.8, spec=0.65)
defmat('M_marble', tex=T('atlantis_marble.png'), norm=T('atlantis_marble_n.png'), rough=0.38, uv=4.0, spec=0.65)
defmat('M_stone', tex=T('atlantis_stone.png'), norm=T('atlantis_stone_n.png'), rough=0.8, uv=4.0, spec=0.35)
defmat('M_rock', tex=T('atlantis_rock.png'), norm=T('atlantis_rock_n.png'), rough=0.95, uv=10.0)
defmat('M_sand', tex=T('atlantis_sand.png'), rough=1.0, uv=8.0, spec=0.1)
defmat('M_coral', tex=T('atlantis_coral.png'), norm=T('atlantis_coral_n.png'), rough=0.7, uv=2.0, spec=0.3)
defmat('M_cloth', tex=T('atlantis_cloth.png'), rough=0.85, uv=2.0, double=True)
defmat('M_gold', rough=0.28, metal=0.9, spec=0.7)
defmat('M_pearl', tex=T('atlantis_marble.png'), rough=0.2, uv=4.0, spec=1.0)
defmat('M_kelp', rough=0.8, spec=0.2)
defmat('M_fish', rough=0.5, spec=0.5, double=True)
defmat('M_flame', emit='#7affe8', emit_str=1.9, vcol=False, color='#7affe8')
defmat('M_glow', emit='#9affee', emit_str=1.3, vcol=False, color='#9affee')
defmat('M_bubble', emit='#bff6ff', emit_str=0.5, rough=0.1, spec=1.0, vcol=False, color='#bff6ff')
defmat('M_ray', tex=T('atlantis_ray.png'), emit_tex=T('atlantis_ray.png'), emit_str=0.8, rough=1.0, alpha=True, vcol=False, double=True, uv=1.0)

MART = (1.0, 1.0, 1.0)
GOLDT = (0.96, 0.74, 0.28)
CORT = (1.0, 0.82, 0.78)
sc = Scene('arena_atlantis')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
walls = sc.part('Walls')
temple = sc.part('Temple')
reef = sc.part('Reef')
fx = sc.part('Far')
rays = sc.part('Rays')
sc.noao = {'Far', 'Rays'}
build_ground(sc, step=1.0)

# ------------------------------------------------------------------ rebord de corail, parvis, péristyle de marbre perle
skip_n = []
s0 = rr.s_nearest(0.0, -16.0)
skip_n.append((s0 - 9.5, s0 + 9.5))
parapet(sc, rr, 'Walls', 0.0, 0.6, 0.85, 'M_stone', MART, gold='M_coral', t_gold=CORT, skip=skip_n, capw=0.1)
ring_band(sc, 'Walls', rr, [(0.6, 0.0), (3.9, 0.0)], 'M_marble', MART, 'up', None, 4.0)
ring_band(sc, 'Walls', rr, [(0.6, 0.0), (0.64, -0.5), (3.9, -0.5)], 'M_stone', (0.9, 0.95, 0.95), 'in', None, 4.0)
COL_D, COL_R, COL_H = 2.3, 0.4, 5.6
cols, ytop = peristyle(sc, rr, 'Decor', COL_D, 0.0, COL_H, 5.4, COL_R, ent_h=1.3, ent_w=0.62, ent=False, mats=dict(shaft='M_marble', gold='M_coral', ent='M_marble', trim='M_coral'),
                       tints=dict(shaft=MART, gold=CORT, ent=MART, trim=CORT), seg=10, cap='ionic', skip=lambda x, z: z < -17 and abs(x) < 9.0, skip_s=skip_n)
ZN = -(COL_D + 16.0)
for sx in (-1, 1):
    dec.box((13.0, 0.9, 1.3), pos=(sx * 15.5, COL_H, ZN), mat='M_marble', tint=MART, bev=0.02)
    dec.box((13.2, 0.5, 1.45), pos=(sx * 15.5, COL_H + 0.9, ZN), mat='M_coral', tint=CORT, bev=0.02)
bi = 1
for x in (-20, -12, 12, 20):
    banner_object(sc, f'Banner_{bi:02d}', (x, COL_H + 0.1, ZN + 0.9), math.pi, 1.5, 3.4, '#1d6a8e', '#e0b44a', '#f2dc8c', phase=bi, mat='M_cloth', rod_mat='M_gold', rod_tint=GOLDT)
    bi += 1
torches(sc, rr, y=2.2, sconce_fn=make_torch_fn(mat='M_marble', gold='M_gold', flame='M_flame', t=MART, t_gold=GOLDT))

# ------------------------------------------------------------------ obstacles : colonnes surmontées de tridents d'or
def small_trident(mb, x, y, z, s=1.0, tint=GOLDT):
    mb.add(p_cyl(0.07 * s, 1.1 * s, 6), 'M_gold', pos=(x, y, z), tint=tint)
    for dx in (-1, 0, 1):
        h_ = 0.78 if dx == 0 else 0.62
        mb.add(p_cone(0.05 * s, h_ * s, 5), 'M_gold', pos=(x + dx * 0.25 * s, y + 1.0 * s + (0.0 if dx == 0 else 0.0), z), tint=tint)
    mb.add(p_box(0.6 * s, 0.07 * s, 0.07 * s), 'M_gold', pos=(x, y + 1.0 * s, z), tint=tint)
    mb.add(p_cyl(0.045 * s, 0.34 * s, 5), 'M_gold', pos=(x - 0.25 * s, y + 1.0 * s, z), tint=tint)
    mb.add(p_cyl(0.045 * s, 0.34 * s, 5), 'M_gold', pos=(x + 0.25 * s, y + 1.0 * s, z), tint=tint)


for i in range(6):
    mb, o = obstacle_part(sc, i)
    r = o['r']
    x, z = o['x'], o['z']
    h = [3.8, 3.5, 4.0, 3.7, 3.4, 3.6][i]
    # monticule de corail (rayon exact r au sol) + socle
    mb.lathe([(r, 0.0), (r * 0.98, 0.18), (r * 0.82, 0.42), (r * 0.66, 0.58)], pos=(x, 0, z), mat='M_coral', seg=14, tint=CORT, cap0=False, jit=0.06)
    for k in range(5):
        a = 2 * math.pi * k / 5 + i
        hh = rng.uniform(0.7, 1.3)
        mb.add(p_lathe([(0.17, 0.2), (0.12, hh * 0.6), (0.0, hh)], 5, False, False), 'M_coral', pos=(x + r * 0.78 * math.cos(a), 0, z + r * 0.78 * math.sin(a)), tint=CORT)
    fluted_column(mb, x, z, 0.62 * r / 1.28 * 1.28 * 0.78, h - 0.55, 0.5, 'M_marble', 'M_gold', MART, GOLDT, seg=12, cap='ionic', flutes=(8, 0.07), base_h=0.3, cap_h=0.38)
    small_trident(mb, x, h + 0.05, z, 1.1)
    mb.sphere(0.2, pos=(x, 0.95, z + 0.0), mat='M_pearl', nu=8, nv=5, tint=(1, 1, 1)) if False else None
    fx.sphere(0.16, pos=(x, h + 1.9, z), mat='M_glow', nu=7, nv=4)

# ------------------------------------------------------------------ grand escalier + temple de Poséidon (nord)
YP = 2.4
steps = 8
for k in range(steps):
    zb = -19.2 - k * 0.78
    temple.box((19.0, YP * (k + 1) / steps, abs(-27.0 - zb) + 0.1), pos=(0, 0, (zb - 27.0) / 2), mat='M_marble', tint=MART, bev=0.02)
temple.box((54.0, YP, 22.0), pos=(0, 0, -38.0), mat='M_marble', tint=MART, bev=0.04)
temple.box((56.0, YP * 0.35, 24.0), pos=(0, 0, -38.0), mat='M_stone', tint=(0.95, 1.0, 1.0), bev=0.04)
for k, (w, d, hh) in enumerate([(40.0, 20.0, 0.32), (38.4, 18.8, 0.32), (37.0, 17.8, 0.32)]):
    temple.box((w, hh, d), pos=(0, YP + 0.32 * k, -33.0), mat='M_marble', tint=MART, bev=0.03)
Y0T = YP + 0.96
TH = 9.0
TR = 0.82
xs = np.linspace(-16.0, 16.0, 9)
zs = np.linspace(-25.5, -40.0, 5)
tcols = []
for x in xs:
    tcols += [(x, zs[0]), (x, zs[-1])]
for z in zs[1:-1]:
    tcols += [(xs[0], z), (xs[-1], z)]
for (x, z) in tcols:
    fluted_column(temple, x, z, TR, TH, Y0T, 'M_marble', 'M_coral', MART, CORT, seg=10, cap='ionic', flutes=(8, 0.06), base_h=0.42, cap_h=0.5)
cw, cd = 25.0, 9.5
zface = -28.5
temple.box((cw, TH + 0.6, cd), pos=(0, Y0T - 0.1, zface - cd / 2), mat='M_stone', tint=(0.97, 1.0, 1.0), bev=0.03)
temple.box((6.0, 7.2, 0.3), pos=(0, Y0T, zface + 0.1), mat='M_glow', tint=(1, 1, 1))
for sx in (-1, 1):
    temple.box((0.7, 7.6, 0.6), pos=(sx * 3.5, Y0T, zface + 0.2), mat='M_gold', tint=GOLDT, bev=0.03)
temple.box((7.8, 0.8, 0.6), pos=(0, Y0T + 7.2, zface + 0.2), mat='M_gold', tint=GOLDT, bev=0.03)
YE = Y0T + TH
for (w, d, y_, hh, mat, tint) in ((38.0, 18.4, 0.0, 0.9, 'M_marble', MART), (38.6, 19.0, 0.9, 0.8, 'M_coral', CORT), (39.4, 19.8, 1.7, 0.35, 'M_gold', GOLDT)):
    temple.box((w, hh, d), pos=(0, YE + y_, -33.0), mat=mat, tint=tint, bev=0.02)
# toit : coupole en coquille géante (nervures) + lanterne de perle
temple.add(p_lathe([(20.0, YE + 2.0), (19.0, YE + 4.0), (15.0, YE + 7.0), (9.0, YE + 9.6), (3.5, YE + 11.2), (0.0, YE + 11.6)], 28, False, True, flutes=(14, 0.16)), 'M_coral',
           pos=(0, 0, -33.0), scale=(1.0, 1.0, 0.55), tint=CORT)
temple.add(p_lathe([(0.5, YE + 11.4), (0.7, YE + 12.0), (0.4, YE + 12.6), (0.0, YE + 12.9)], 8, False, True), 'M_gold', pos=(0, 0, -33.0), tint=GOLDT)
temple.add(p_sphere(0.9, 10, 6), 'M_pearl', pos=(0, YE + 12.1, -33.0), tint=(1, 0.97, 0.95))
# fronton triangulaire bas devant la coupole
temple.add(p_extrude_xy([(-19.4, 0.0), (19.4, 0.0), (0.0, 3.6)], -24.9, -23.8), 'M_marble', pos=(0, YE + 2.05, 0), tint=MART)
temple.add(p_extrude_xy([(-17.0, 0.35), (17.0, 0.35), (0.0, 3.0)], -23.8, -23.62), 'M_coral', pos=(0, YE + 2.05, 0), tint=CORT)


def big_trident(mb, x, z, y0, H=11.0, tint=GOLDT):
    """statue monumentale : socle, fût, tête à trois dents (silhouette extrudée)."""
    mb.lathe([(1.5, y0), (1.5, y0 + 0.4), (1.2, y0 + 0.9), (0.9, y0 + 1.6), (0.8, y0 + 2.2)], pos=(x, 0, z), mat='M_marble', seg=10, tint=MART)
    mb.lathe([(0.3, y0 + 2.1), (0.3, y0 + 2.4), (0.34, y0 + 2.6), (0.3, y0 + 2.8)], pos=(x, 0, z), mat='M_gold', seg=8, tint=tint)
    mb.add(p_cyl(0.22, H * 0.55, 8), 'M_gold', pos=(x, y0 + 2.6, z), tint=tint)
    yb = y0 + 2.6 + H * 0.55
    c_ = [(-0.22, 0.0), (0.22, 0.0), (0.22, 1.6), (0.55, 1.6), (0.0, 4.6), (-0.55, 1.6), (-0.22, 1.6)]
    mb.add(p_extrude_xy(c_, -0.18, 0.18), 'M_gold', pos=(x, yb, z), tint=tint)
    for sx in (-1, 1):
        pts = [(sx * 0.2, 0.2), (sx * 1.4, 0.35), (sx * 1.85, 1.2), (sx * 1.9, 2.5), (sx * 2.3, 2.5), (sx * 1.8, 3.6), (sx * 1.35, 2.5), (sx * 1.6, 2.5), (sx * 1.55, 1.6),
               (sx * 1.15, 1.0), (sx * 0.2, 0.9)]
        mb.add(p_extrude_xy(pts, -0.15, 0.15), 'M_gold', pos=(x, yb, z), tint=tint)


for sx in (-1, 1):
    big_trident(dec, sx * 11.0, -20.4, 0.0, 9.5)
    fx.sphere(0.7, pos=(sx * 11.0, 17.4, -20.4), mat='M_glow', nu=8, nv=5) if False else None

# ------------------------------------------------------------------ fond marin : sable, récifs, algues, coquillages géants
reef.add(p_lathe([(0.0, -0.5), (14.0, -0.5), (26.0, -0.75), (40.0, -1.5), (70.0, -3.0), (120.0, -5.5)], 40, False, False), 'M_sand', tint=(1.0, 0.97, 0.9))
ring_band(sc, 'Reef', rr, [(3.9, 0.0), (3.9, -0.3)], 'M_stone', (0.9, 0.95, 0.95), 'out', None, 4.0)
temple.add(p_box(60.0, 14.0, 30.0), 'M_sand', pos=(0, -14.0, -38.0), tint=(0.9, 0.9, 0.82))


def sand_y(x, z):
    return float(np.interp(math.hypot(x, z), [0, 14, 26, 40, 70, 120], [-0.5, -0.5, -0.75, -1.5, -3.0, -5.5]))


def coral_cluster(mb, x, y, z, rng, s=1.0):
    base_t = [np.array(c) for c in ((1.0, 0.55, 0.62), (1.0, 0.7, 0.45), (0.85, 0.5, 0.85), (1.0, 0.82, 0.55))]
    t = base_t[int(rng.integers(len(base_t)))] * rng.uniform(0.85, 1.1)
    for k in range(int(rng.integers(3, 6))):
        a = rng.uniform(0, 6.28)
        lean = rng.uniform(0.0, 0.5)
        hh = rng.uniform(1.4, 3.4) * s
        rr_ = rng.uniform(0.2, 0.4) * s
        V, F = p_lathe([(rr_, -0.2), (rr_ * 0.7, hh * 0.5), (rr_ * 0.9, hh * 0.7), (0.0, hh)], 5, False, False)
        mb.add((V, F), 'M_coral', pos=(x + math.cos(a) * 0.5 * s, y, z + math.sin(a) * 0.5 * s), pitch=lean * math.cos(a), roll=lean * math.sin(a), tint=t)
        mb.add(p_lathe([(rr_ * 0.6, hh * 0.5), (0.0, hh * 0.85)], 5, False, False), 'M_coral', pos=(x + math.cos(a) * 0.5 * s + lean * hh * 0.3, y + hh * 0.2, z + math.sin(a) * 0.5 * s), tint=t * 1.1)
    mb.add(p_sphere(1.0 * s, 7, 4, 0.5), 'M_coral', pos=(x, y, z), tint=t * 0.9)


for i in range(46):
    a = rng.uniform(0, 2 * math.pi)
    d = rng.uniform(5.0, 38.0)
    P_, N_ = rr.at_base(rng.uniform(0, rr.length()), d)
    x, z = P_
    if z < -17 and abs(x) < 24:
        continue
    y = sand_y(x, z)
    coral_cluster(reef, x, y, z, rng, s=rng.uniform(0.8, 1.6))
for i in range(70):
    P_, N_ = rr.at_base(rng.uniform(0, rr.length()), rng.uniform(4.5, 16.0))
    x, z = P_
    if z < -17 and abs(x) < 24:
        continue
    y = sand_y(x, z)
    hh = rng.uniform(3.0, 8.5)
    reef.add(p_lathe([(0.16, y - 0.1), (0.1, y + hh * 0.5), (0.0, y + hh)], 4, False, False), 'M_kelp', pos=(x, 0, z), roll=rng.uniform(-0.12, 0.12), pitch=rng.uniform(-0.12, 0.12),
             tint=(0.2 + rng.uniform(0, 0.15), 0.55 + rng.uniform(0, 0.15), 0.28))
# coquillages géants (dômes nervurés) + perles
for k, (x, z, rad) in enumerate([(-30.0, 17.0, 2.6), (30.0, 18.0, 3.0), (-33.0, -9.0, 2.2), (33.0, -6.0, 2.6), (-12.0, 21.0, 2.0), (16.0, 22.0, 2.4)]):
    y = sand_y(x, z)
    tn = (1.0, 0.86, 0.84) if k % 2 == 0 else (1.0, 0.95, 0.9)
    yaw = rng.uniform(0, 6.28)
    reef.add(p_lathe([(rad, y), (rad * 0.97, y + rad * 0.3), (rad * 0.75, y + rad * 0.75), (rad * 0.38, y + rad * 0.98), (0.0, y + rad * 1.05)], 24, False, True, flutes=(12, 0.22)),
             'M_coral', pos=(x, 0, z), yaw=yaw, scale=(1.0, 0.9, 0.8), tint=tn)
    reef.add(p_sphere(rad * 0.28, 8, 5), 'M_pearl', pos=(x + math.sin(yaw) * rad * 0.45, y + rad * 0.3, z + math.cos(yaw) * rad * 0.45), tint=(1, 0.98, 0.96))
# ruines englouties au loin
for i in range(16):
    a = rng.uniform(0, 2 * math.pi)
    d = rng.uniform(26, 48)
    P_, N_ = rr.at_base(rng.uniform(0, rr.length()), d)
    x, z = P_
    if z < -17 and abs(x) < 26:
        continue
    y = sand_y(x, z)
    hh = rng.uniform(2.5, 8.5)
    reef.add(p_lathe([(0.7, y - 0.3), (0.62, y + hh), (0.55, y + hh + 0.05)], 8, False, True, flutes=(8, 0.08)), 'M_marble', pos=(x, 0, z), roll=rng.uniform(-0.08, 0.08), tint=(0.8, 0.9, 0.9))
    reef.add(p_lathe([(1.0, y - 0.3), (1.0, y + 0.4)], 8, False, True), 'M_coral', pos=(x, 0, z), tint=CORT)

# ------------------------------------------------------------------ rayons, bulles, poissons
for k in range(10):
    x0 = rng.uniform(-42, 42)
    z0 = rng.uniform(-38, 10)
    wd = rng.uniform(5.0, 9.0)
    ang = rng.uniform(-0.22, 0.22)
    hgt = 46.0
    V = np.array([(-wd / 2, 0.0, 0.0), (wd / 2, 0.0, 0.0), (wd / 2 * 0.7, hgt, 0.0), (-wd / 2 * 0.7, hgt, 0.0)], float)
    # image : y=0 en bas du quad ; la texture a l'opacité maximale en v=0 (haut) -> on retourne
    uv = np.array([(0, 1), (1, 1), (1, 0), (0, 0)], float)
    rays.add((V, [(0, 1, 2, 3)]), 'M_ray', pos=(x0, -3.0, z0), yaw=rng.uniform(0, 3.14), roll=ang, tint=(1, 1, 1), uv=uv)
bub = []
for i in range(130):
    x = rng.uniform(-44, 44)
    z = rng.uniform(-30, 30)
    y = rng.uniform(0.5, 22)
    r = rng.uniform(0.08, 0.28)
    fx.add(p_ico(r, 0), 'M_bubble', pos=(x, y, z), tint=(1, 1, 1))
for k in range(16):
    c = (rng.uniform(-40, 40), rng.uniform(4, 16), rng.uniform(-30, 20))
    col = [(1.0, 0.55, 0.2), (0.3, 0.7, 1.0), (1.0, 0.85, 0.3), (0.9, 0.4, 0.55)][k % 4]
    for j in range(int(rng.integers(3, 6))):
        px, py, pz = c[0] + rng.uniform(-3, 3), c[1] + rng.uniform(-1.5, 1.5), c[2] + rng.uniform(-3, 3)
        yaw = k * 0.8
        fx.add(p_lathe([(0.0, -0.5), (0.22, -0.2), (0.28, 0.1), (0.14, 0.4), (0.0, 0.55)], 6, False, False), 'M_fish', pos=(px, py, pz), yaw=yaw, pitch=math.pi / 2, scale=(1.0, 1.0, 0.6), tint=col)
        fx.add(p_extrude_xy([(0.0, 0.0), (0.0, -0.3), (0.0, 0.3)], -0.02, 0.02), 'M_fish', pos=(px, py, pz), yaw=yaw, tint=col) if False else None
        fx.add(p_box(0.04, 0.4, 0.3), 'M_fish', pos=(px - math.sin(yaw) * 0.55, py - 0.2, pz - math.cos(yaw) * 0.55), yaw=yaw, tint=col)
sc.empty('Light_01', -10.0, 14.0, -12.0)
sc.empty('Light_02', 12.0, 14.0, -8.0)
sc.empty('Light_03', 0.0, 16.0, 6.0)

report(sc)
sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5, 'Temple': 0.55, 'Reef': 0.5}
sc.build(ao_samples=36, ao_dist=3.0, ao_floor=0.45)
sc.export(OUTDIR + '/arena_atlantis.glb')
