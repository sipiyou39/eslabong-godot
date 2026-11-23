"""arena_olympus.glb — « Mont Olympe » : terrasse de marbre au sommet d'une montagne au-dessus d'une mer de nuages,
péristyle de colonnes dorées, temple de Zeus au fond (nord, -Z), foudres lointaines."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from greek_common import *

T = lambda n: TEXDIR + '/' + n
G.seed(701)
rng = np.random.default_rng(701)

defmat('M_ground', tex=T('olympus_ground.png'), norm=T('olympus_ground_n.png'), rough=0.55, metal=0.0, uv=1, norm_str=0.8, spec=0.55)
defmat('M_marble', tex=T('olympus_marble.png'), norm=T('olympus_marble_n.png'), rough=0.42, uv=4.0, spec=0.6)
defmat('M_stone', tex=T('olympus_stone.png'), norm=T('olympus_stone_n.png'), rough=0.8, uv=4.0, spec=0.35)
defmat('M_rock', tex=T('olympus_rock.png'), norm=T('olympus_rock_n.png'), rough=0.95, uv=10.0)
defmat('M_cloth', tex=T('olympus_cloth.png'), rough=0.85, uv=2.0, double=True)
defmat('M_gold', rough=0.3, metal=0.9, spec=0.6)
defmat('M_roof', rough=0.4, metal=0.7, spec=0.6)
defmat('M_cloud', rough=1.0, spec=0.0)
defmat('M_flame', emit='#ffc860', emit_str=2.6, vcol=False, color='#ffc860')
defmat('M_glow', emit='#ffdf96', emit_str=1.1, vcol=False, color='#ffdf96')
defmat('M_door', emit='#ffd27a', emit_str=1.6, vcol=False, color='#ffd27a')
defmat('M_bolt', emit='#fff2c8', emit_str=4.0, vcol=False, color='#fff2c8')

GOLDT = (0.95, 0.72, 0.27)
MART = (1.0, 0.97, 0.9)
sc = Scene('arena_olympus')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
walls = sc.part('Walls')
temple = sc.part('Temple')
cl = sc.part('Clouds')
far = sc.part('Far')
sc.noao = {'Clouds', 'Far'}

build_ground(sc, step=1.0)

# ------------------------------------------------------------------ parapet, pavement, péristyle d'or
skip_n = []
s0 = rr.s_nearest(0.0, -16.0)
skip_n.append((s0 - 9.5, s0 + 9.5))           # grand escalier côté temple
parapet(sc, rr, 'Walls', 0.0, 0.55, 1.0, 'M_marble', MART, skip=skip_n)
ring_band(sc, 'Walls', rr, [(0.55, 0.0), (3.9, 0.0)], 'M_marble', MART, 'up', None, 4.0)
ring_band(sc, 'Walls', rr, [(0.55, 0.0), (0.58, -0.4), (3.9, -0.4)], 'M_marble', (0.9, 0.88, 0.8), 'in', None, 4.0)
COL_D, COL_R, COL_H = 2.3, 0.4, 5.6
cols, ytop = peristyle(sc, rr, 'Decor', COL_D, 0.0, COL_H, 5.4, COL_R, ent_h=1.3, ent_w=0.62, ent=False, mats=dict(shaft='M_marble', gold='M_gold', ent='M_marble', trim='M_gold'),
                       tints=dict(shaft=MART, gold=GOLDT, ent=MART, trim=GOLDT), seg=10, cap='ionic', skip=lambda x, z: z < -17 and abs(x) < 9.0, skip_s=skip_n)
# architrave : poutre continue côté temple uniquement (le reste reste ouvert sur les nuages)
ZN = -(COL_D + 16.0)
for sx in (-1, 1):
    dec.box((13.0, 0.9, 1.3), pos=(sx * 15.5, COL_H, ZN), mat='M_marble', tint=MART, bev=0.02)
    dec.box((13.2, 0.5, 1.45), pos=(sx * 15.5, COL_H + 0.9, ZN), mat='M_marble', tint=MART, bev=0.02)
    dec.box((13.3, 0.12, 1.5), pos=(sx * 15.5, COL_H + 1.4, ZN), mat='M_gold', tint=GOLDT)
# bannières entre les colonnes du nord
bi = 1
for x in (-20, -12, 12, 20):
    banner_object(sc, f'Banner_{bi:02d}', (x, COL_H + 0.1, ZN + 0.9), math.pi, 1.5, 3.4, '#5a2a86', '#e2b64a', '#f4e2a0', phase=bi, mat='M_cloth', rod_mat='M_gold',
                  rod_tint=GOLDT)
    bi += 1
for x in ():
    banner_object(sc, f'Banner_{bi:02d}', (x, COL_H + 0.1, (COL_D + 16.0 - 0.6)), 0.0, 1.5, 3.4, '#2a4f9a', '#e2b64a', '#f4e2a0', phase=bi, mat='M_cloth', rod_mat='M_gold',
                  rod_tint=GOLDT)
    bi += 1

# torches : braseros dorés sur piédestal
torches(sc, rr, y=2.2, sconce_fn=make_torch_fn(mat='M_marble', gold='M_gold', flame='M_flame', t=MART, t_gold=GOLDT))

# ------------------------------------------------------------------ obstacles : colonnes ioniques d'or sur socle
for i in range(6):
    mb, o = obstacle_part(sc, i)
    r = o['r']
    x, z = o['x'], o['z']
    h = [4.3, 4.0, 4.5, 4.2, 3.9, 4.1][i]
    mb.lathe([(r, 0.0), (r, 0.16), (r * 0.9, 0.3), (r * 0.78, 0.52)], pos=(x, 0, z), mat='M_gold', seg=14, tint=GOLDT, cap0=False)
    mb.lathe([(r * 0.78, 0.5), (r * 0.74, 0.6), (r * 0.6, 0.72)], pos=(x, 0, z), mat='M_marble', seg=14, tint=MART, cap0=False)
    fluted_column(mb, x, z, 0.82 * r / 1.28 * 0.9, h - 0.6, 0.62, 'M_marble', 'M_gold', MART, GOLDT, seg=12, cap='ionic', flutes=(8, 0.07), base_h=0.3, cap_h=0.38)
    mb.sphere(0.24, pos=(x, h + 0.2, z), mat='M_glow', nu=8, nv=5, tint=(1, 1, 1))
    mb.add(p_torus(0.34, 0.03, 12, 4), 'M_gold', pos=(x, h + 0.2, z), pitch=0.5, yaw=0.7 * i, tint=GOLDT)

# ------------------------------------------------------------------ grand escalier + temple de Zeus (nord)
YP = 2.4
steps = 8
for k in range(steps):
    zb = -19.2 - k * 0.78                      # bord avant de la marche k
    temple.box((19.0, YP * (k + 1) / steps, abs(-27.0 - zb) + 0.1), pos=(0, 0, (zb - 27.0) / 2), mat='M_marble', tint=MART, bev=0.02)
# plate-forme du temple
temple.box((54.0, YP, 22.0), pos=(0, 0, -38.0), mat='M_marble', tint=MART, bev=0.04)
temple.box((56.0, YP * 0.35, 24.0), pos=(0, 0, -38.0), mat='M_stone', tint=(0.95, 0.92, 0.82), bev=0.04)
# stylobate : 3 degrés
for k, (w, d, hh) in enumerate([(40.0, 20.0, 0.32), (38.4, 18.8, 0.32), (37.0, 17.8, 0.32)]):
    temple.box((w, hh, d), pos=(0, YP + 0.32 * k, -33.0), mat='M_marble', tint=MART, bev=0.03)
Y0T = YP + 0.96
TH = 9.6
TR = 0.82
xs = np.linspace(-16.0, 16.0, 9)
zs = np.linspace(-25.5, -40.0, 5)
tcols = []
for x in xs:
    tcols += [(x, zs[0]), (x, zs[-1])]
for z in zs[1:-1]:
    tcols += [(xs[0], z), (xs[-1], z)]
for (x, z) in tcols:
    fluted_column(temple, x, z, TR, TH, Y0T, 'M_marble', 'M_gold', MART, GOLDT, seg=10, cap='ionic', flutes=(8, 0.06), base_h=0.42, cap_h=0.5)
# cella (mur central) avec grande porte dorée lumineuse
cw, cd = 25.0, 9.5
zface = -28.5
temple.box((cw, TH + 0.6, cd), pos=(0, Y0T - 0.1, zface - cd / 2), mat='M_stone', tint=(1.0, 0.95, 0.84), bev=0.03)
temple.box((6.0, 7.2, 0.3), pos=(0, Y0T, zface + 0.1), mat='M_door', tint=(1, 1, 1))
for sx in (-1, 1):
    temple.box((0.7, 7.6, 0.6), pos=(sx * 3.5, Y0T, zface + 0.2), mat='M_gold', tint=GOLDT, bev=0.03)
temple.box((7.8, 0.8, 0.6), pos=(0, Y0T + 7.2, zface + 0.2), mat='M_gold', tint=GOLDT, bev=0.03)
temple.box((0.16, 7.2, 0.4), pos=(0, Y0T, zface + 0.25), mat='M_gold', tint=GOLDT)
for yy in (2.6, 4.6):
    temple.box((6.0, 0.12, 0.4), pos=(0, Y0T + yy, zface + 0.25), mat='M_gold', tint=GOLDT)
# architrave + frise + corniche
YE = Y0T + TH
for (w, d, y_, hh, mat, tint) in ((38.0, 18.4, 0.0, 0.9, 'M_marble', MART), (38.6, 19.0, 0.9, 0.8, 'M_marble', MART), (39.4, 19.8, 1.7, 0.35, 'M_gold', GOLDT)):
    temple.box((w, hh, d), pos=(0, YE + y_, -33.0), mat=mat, tint=tint, bev=0.02)
for x in np.linspace(-17.0, 17.0, 12):
    temple.add(p_cyl(0.32, 0.08, 10), 'M_gold', pos=(x, YE + 1.3, -23.95), pitch=math.pi / 2, tint=GOLDT)
# fronton + toit
fz0, fz1 = -23.8, -24.9
pedi = [(-19.4, 0.0), (19.4, 0.0), (0.0, 4.9)]
temple.add(p_extrude_xy(pedi, fz1, fz0), 'M_marble', pos=(0, YE + 2.05, 0), tint=MART)
inner = [(-17.0, 0.35), (17.0, 0.35), (0.0, 4.15)]
temple.add(p_extrude_xy(inner, fz0, fz0 + 0.18), 'M_stone', pos=(0, YE + 2.05, 0), tint=(1.0, 0.92, 0.78))
temple.add(p_cyl(1.0, 0.1, 18), 'M_gold', pos=(0, YE + 2.05 + 1.9, fz0 + 0.25), pitch=math.pi / 2, tint=GOLDT)
for sx in (-1, 1):
    for k in range(4):
        a = (k - 1.5) * 0.5
        temple.add(p_box(0.18, 1.7, 0.1), 'M_gold', pos=(sx * (2.4 + 0.1 * k), YE + 2.05 + 1.0 + 0.1 * k, fz0 + 0.27), roll=-a * sx * 0.8, tint=GOLDT)
roof = [(-19.8, 0.0), (19.8, 0.0), (0.0, 5.0)]
temple.add(p_extrude_xy(roof, -43.0, -24.2), 'M_roof', pos=(0, YE + 2.0, 0), tint=(0.9, 0.68, 0.3))
temple.add(p_box(1.2, 0.5, 19.0), 'M_gold', pos=(0, YE + 2.0 + 5.0, -33.6), tint=GOLDT)
for sx in (-1, 1):
    temple.add(p_cone(0.7, 1.8, 6), 'M_gold', pos=(sx * 19.6, YE + 2.0, -24.5), tint=GOLDT)
temple.add(p_cone(0.8, 2.2, 6), 'M_gold', pos=(0, YE + 2.0 + 5.0 + 0.5, -24.5), tint=GOLDT)
# braseros monumentaux de part et d'autre de l'escalier
for sx in (-1, 1):
    x_ = sx * 11.0
    dec.lathe([(0.8, 0.0), (0.8, 0.3), (0.5, 0.7), (0.4, 2.0), (0.7, 2.4), (1.0, 2.8), (0.8, 2.8), (0.0, 2.6)], pos=(x_, 0, -19.7), mat='M_gold', seg=12, tint=GOLDT)
    far.lathe([(0.0, 2.7), (0.8, 2.8), (0.8, 3.4), (0.55, 4.0), (0.28, 4.8), (0.0, 5.5)], pos=(x_, 0, -19.7), mat='M_flame', seg=8, cap0=False, cap1=False)
sc.empty('Light_01', -11.0, 4.3, -19.7)
sc.empty('Light_02', 11.0, 4.3, -19.7)
sc.empty('Light_03', 0.0, Y0T + 3.5, zface + 2.0)

# ------------------------------------------------------------------ falaise de la montagne + mer de nuages
def cliff_vf(V):
    t = np.clip((V[:, 1] + 34) / 34.0, 0, 1)
    n = 1 + 0.18 * np.sin(V[:, 0] * 0.9 + V[:, 2] * 1.3) * np.cos(V[:, 2] * 0.6)
    return (0.55 + 0.5 * t) * n
ring_band(sc, 'Decor', rr, [(3.9, 0.0), (4.1, -0.5), (5.0, -4.0), (7.5, -11.0), (11.5, -21.0), (17.0, -33.0), (26.0, -46.0)], 'M_rock', (1.0, 0.94, 0.86), 'out', None, 16.0, vfun=cliff_vf)
ring_band(sc, 'Decor', rr, [(3.9, 0.0), (3.9, -0.5)], 'M_marble', (0.9, 0.86, 0.76), 'out', None, 4.0)
# socle du temple : falaise nord prolongée
temple.add(p_box(58.0, 40.0, 26.0), 'M_rock', pos=(0, -40.0, -38.0), tint=(0.8, 0.75, 0.68))
# pics rocheux dans la brume
for k in range(7):
    a = rng.uniform(0, 2 * math.pi)
    rd = rng.uniform(55, 110)
    rock_spire(far, rd * math.cos(a) * 1.2, rd * math.sin(a), rng.uniform(5, 11), rng.uniform(30, 58), rng, y0=-24, seg=7, tint=(0.9, 0.82, 0.75))
# nuages : plancher, puffs proches, tours lointaines
cl.add(p_lathe([(0.0, -16.0), (190.0, -16.0), (230.0, -14.0)], 24, True, False), 'M_cloud', tint=(0.86, 0.8, 0.84))
cent_near = []
for i in range(20):
    a = rng.uniform(0, 2 * math.pi)
    rd = rng.uniform(22, 62)
    cent_near.append((rd * math.cos(a) * 1.15, -rng.uniform(5.0, 9.0), rd * math.sin(a) * 0.95))
cloud_puffs(cl, rng, cent_near, size=(6.0, 10.0), sub=1, n_sub=4, tint_hi=(1.0, 0.94, 0.82), tint_lo=(0.66, 0.7, 0.86))
cent_far = []
for i in range(34):
    a = rng.uniform(0, 2 * math.pi)
    rd = rng.uniform(55, 150)
    cent_far.append((rd * math.cos(a), -rng.uniform(3.0, 12.0), rd * math.sin(a)))
cloud_puffs(cl, rng, cent_far, size=(10.0, 20.0), sub=0, n_sub=5, tint_hi=(1.0, 0.9, 0.74), tint_lo=(0.62, 0.66, 0.84))
# couche intermédiaire dense (peu de triangles)
cent_mid = []
for i in range(34):
    a = rng.uniform(0, 2 * math.pi)
    rd = rng.uniform(30, 95)
    cent_mid.append((rd * math.cos(a) * 1.1, -rng.uniform(4.0, 8.0), rd * math.sin(a)))
cloud_puffs(cl, rng, cent_mid, size=(9.0, 15.0), sub=0, n_sub=4, tint_hi=(1.0, 0.92, 0.8), tint_lo=(0.74, 0.74, 0.88))
# bancs de nuages qui frôlent la falaise
for i in range(14):
    a = 2 * math.pi * i / 14 + rng.uniform(-0.1, 0.1)
    rd = rng.uniform(14, 24)
    cx_, cz_ = rd * math.cos(a) * 1.9, rd * math.sin(a) * 1.35
    if cz_ < -12 and abs(cx_) < 34:
        continue
    cloud_puffs(cl, rng, [(cx_, -rng.uniform(3.5, 6.5), cz_)], size=(5.0, 8.0), sub=1, n_sub=3, tint_hi=(1.0, 0.95, 0.85), tint_lo=(0.7, 0.74, 0.88))
# tours de nuages et foudres lointaines
for k in range(9):
    a = rng.uniform(-math.pi * 0.95, -math.pi * 0.05) if k < 6 else rng.uniform(0, 2 * math.pi)
    rd = rng.uniform(90, 160)
    cx_, cz_ = rd * math.cos(a), rd * math.sin(a)
    for j in range(5):
        cloud_puffs(cl, rng, [(cx_ + rng.uniform(-8, 8), -2 + j * 7, cz_ + rng.uniform(-8, 8))], size=(12 - j * 1.4, 18 - j * 2), sub=0, n_sub=4,
                    tint_hi=(1.0, 0.86 - 0.02 * j, 0.7), tint_lo=(0.55, 0.58, 0.8))
for k in range(5):
    a = math.radians(rng.uniform(205, 335))
    rd = rng.uniform(95, 140)
    bx, bz = rd * math.cos(a), rd * math.sin(a)
    lightning_bolt(far, (bx, rng.uniform(32, 46), bz), (bx + rng.uniform(-8, 8), -3.0, bz + rng.uniform(-6, 6)), rng, 'M_bolt', w=0.55, n=7, amp=4.5)

report(sc)
sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5, 'Temple': 0.55}
sc.build(ao_samples=36, ao_dist=3.0, ao_floor=0.45)
sc.export(OUTDIR + '/arena_olympus.glb')
