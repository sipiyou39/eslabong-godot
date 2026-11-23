"""arena_underworld.glb — « Les Enfers » : plateforme de basalte cernée par le Styx vert-bleuté, falaises noires, portes de bronze, braseros spectraux."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from greek_common import *

T = lambda n: TEXDIR + '/' + n
G.seed(801)
rng = np.random.default_rng(801)

defmat('M_ground', tex=T('underworld_ground.png'), norm=T('underworld_ground_n.png'), emit_tex=T('underworld_ground_e.png'), emit_str=1.5, rough=0.62, metal=0.1, uv=1,
       norm_str=0.9, spec=0.5)
defmat('M_basalt', tex=T('underworld_basalt.png'), norm=T('underworld_basalt_n.png'), rough=0.6, metal=0.1, uv=4.0, spec=0.5)
defmat('M_rock', tex=T('underworld_rock.png'), norm=T('underworld_rock_n.png'), rough=0.92, uv=12.0)
defmat('M_stone', tex=T('underworld_stone.png'), norm=T('underworld_stone_n.png'), rough=0.8, uv=4.0, spec=0.35)
defmat('M_bronze', tex=T('underworld_bronze.png'), norm=T('underworld_bronze_n.png'), rough=0.42, metal=0.75, uv=2.0)
defmat('M_water', tex=T('underworld_water.png'), emit_tex=T('underworld_water_e.png'), emit_str=1.6, rough=0.15, metal=0.0, uv=6.0, spec=0.7, vcol=True)
defmat('M_cloth', tex=T('underworld_cloth.png'), rough=0.9, uv=2.0, double=True)
defmat('M_bone', rough=0.8, spec=0.3)
defmat('M_wood', rough=0.9, spec=0.2)
defmat('M_dark', rough=0.5, metal=0.5, spec=0.4)
defmat('M_flame', emit='#30f0a8', emit_str=1.7, vcol=False, color='#30f0a8')
defmat('M_rune', emit='#52ffc4', emit_str=2.2, vcol=False, color='#52ffc4')
defmat('M_ember', emit='#ff3c10', emit_str=1.15, vcol=False, color='#ff3c10')
defmat('M_glow', emit='#7affd6', emit_str=1.2, vcol=False, color='#7affd6')

BRZ = (0.85, 0.62, 0.36)
BAS = (1.15, 1.1, 1.25)
sc = Scene('arena_underworld')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
walls = sc.part('Walls')
water = sc.part('Water')
far = sc.part('Far')
sc.noao = {'Water', 'Far'}
build_ground(sc, step=1.0)

# ------------------------------------------------------------------ rebord de l'île, Styx, falaises
LIP_H = 0.55
solid_ring(sc, rr, 'Walls', 0.0, 0.7, -1.5, LIP_H, 'M_stone', tint=BAS, inner=True, top=True, outer=True)
solid_ring(sc, rr, 'Walls', -0.06, 0.76, LIP_H, LIP_H + 0.1, 'M_bronze', tint=BRZ, inner=True, top=True, outer=True)
add_strip(walls, rr, [(0.0, -1.5), (0.0, -1.4)], 'M_stone', 'in', BAS, None, 4.0)
RIV_Y = -1.4
RIV_W = 9.0
ring_band(sc, 'Water', rr, [(0.7, RIV_Y), (RIV_W, RIV_Y)], 'M_water', (1, 1, 1), 'up', None, 6.0)
vn = vnoise_f(0.25, 0.5, 5)
ring_band(sc, 'Decor', rr, [(RIV_W, RIV_Y), (RIV_W + 0.5, 1.0), (RIV_W + 2.0, 5.0), (RIV_W + 4.5, 9.5), (RIV_W + 8.0, 13.0), (RIV_W + 14.0, 15.0), (RIV_W + 24.0, 15.5)],
          'M_rock', (0.85, 0.82, 0.9), 'in', None, 12.0, vfun=vn)
ring_band(sc, 'Decor', rr, [(RIV_W + 24.0, 15.5), (RIV_W + 24.0, 30.0)], 'M_rock', (0.8, 0.78, 0.85), 'in', None, 12.0)
skip_e = []
Lr = rr.length()
for k in range(24):
    s0_ = rng.uniform(0, Lr)
    skip_e.append((s0_, s0_ + rng.uniform(2.0, 5.0)))
# on inverse : on ne remplit QUE les segments de braise (le reste est 'skip')
skip_inv = []
cur = 0.0
for a_, b_ in sorted(skip_e):
    if a_ > cur:
        skip_inv.append((cur, a_))
    cur = max(cur, b_)
skip_inv.append((cur, Lr + 1))
ring_band(sc, 'Far', rr, [(RIV_W - 0.45, RIV_Y + 0.04), (RIV_W + 0.05, RIV_Y + 0.04)], 'M_ember', (1, 1, 1), 'up', skip_inv, 6.0)
# colonnes de basalte hexagonales le long de la rive + aiguilles rocheuses
P, Nn, Tn, s = rr.along(2.3, RIV_W + 1.5, offset=0.4)
for i in range(len(P)):
    x, z = P[i] + rng.uniform(-0.5, 0.5, 2)
    if abs(z) < 4.0 and abs(x) > 30:
        continue
    if z < -10 and abs(x) < 8:
        continue
    r = rng.uniform(0.45, 0.8)
    top = rng.uniform(2.0, 8.0) * (1.4 if i % 5 == 0 else 1.0)
    prof = [(r, RIV_Y - 0.4), (r, top)]
    dec.add(p_lathe(prof, 6, False, True, phase=rng.uniform(0, 1), jitter=0.04), 'M_basalt', pos=(x, 0, z), tint=BAS, jit=0.08)
    if i % 3 == 0:
        dec.add(p_lathe([(r * 0.8, top - 0.05), (0.0, top + r * rng.uniform(0.8, 2.0))], 6, False, False, phase=0.3), 'M_basalt', pos=(x, 0, z), tint=BAS, jit=0.08)
P, Nn, Tn, s = rr.along(7.0, RIV_W + 5.0, offset=1.7)
for i in range(len(P)):
    x, z = P[i] + rng.uniform(-1.5, 1.5, 2)
    if abs(z) < 5.0 and abs(x) > 30:
        continue
    if z < -10 and abs(x) < 10:
        continue
    rock_spire(far, x, z, rng.uniform(1.5, 3.0), rng.uniform(8, 16), rng, y0=6.0, seg=7, mat='M_rock', tint=(0.8, 0.78, 0.86))

# ------------------------------------------------------------------ ponts + portes de bronze
def hades_gate(pos, nxz, W, H, ow, spring, depth, name_idx):
    yaw = yaw_of(*nxz)
    arch_block(dec, pos, nxz, W, H, ow, spring, depth, mat='M_basalt', tint=BAS, glow_mat='M_ember', glow_tint=(1, 1, 1))
    x1, z1 = local_to_world(pos, nxz, 0, depth * 0.55 + 0.1)
    # vantaux de bronze entrouverts
    for sg in (-1, 1):
        xl, zl = local_to_world(pos, nxz, sg * (ow / 2 - 0.5), depth * 0.55 + 0.2)
        dec.add(p_box(ow / 2 - 0.2, spring + ow * 0.18, 0.28), 'M_bronze', pos=(xl, 0.0, zl), yaw=yaw + sg * 0.55, tint=BRZ, bev=0.03)
    for yb in (0.6, spring * 0.5, spring - 0.3):
        dec.add(p_box(ow + 0.6, 0.22, 0.34), 'M_bronze', pos=(x1, yb, z1), yaw=yaw, tint=BRZ)
    # crâne au sommet
    xs_, zs_ = local_to_world(pos, nxz, 0, depth * 0.55 + 0.45)
    sk_y = spring + ow / 2 + 0.9
    dec.add(p_sphere(0.8, 8, 5, 1.1), 'M_bone', pos=(xs_, sk_y, zs_), yaw=yaw, tint=(0.88, 0.84, 0.72))
    for sg in (-1, 1):
        xe, ze = local_to_world(pos, nxz, sg * 0.3, depth * 0.55 + 1.15)
        dec.add(p_sphere(0.22, 6, 4), 'M_rune', pos=(xe, sk_y + 0.1, ze), tint=(1, 1, 1))
    sc.empty(f'Light_{name_idx:02d}', x1, 3.0, z1)


for k, sx in enumerate((1, -1)):
    pos = (35.2 * sx, 0.0)
    hades_gate(pos, (float(sx), 0.0), 10.0, 10.5, 5.8, 5.4, 1.8, k + 1)
    # pont
    for sg in (-1, 1):
        dec.add(p_box(8.8, 1.6, 0.7), 'M_stone', pos=(30.6 * sx, -1.4, sg * 2.75), tint=BAS, bev=0.04)
        dec.add(p_box(8.8, 0.18, 0.9), 'M_bronze', pos=(30.6 * sx, 0.2, sg * 2.75), tint=BRZ)
    dec.add(p_box(8.8, 0.5, 5.6), 'M_basalt', pos=(30.6 * sx, -0.5, 0.0), tint=BAS, bev=0.04)
    for xx in (27.5, 30.0, 32.5, 35.0):
        dec.add(p_cyl(0.28, 1.4, 6), 'M_bronze', pos=(xx * sx, 0.2, 2.75), tint=BRZ)
        dec.add(p_cyl(0.28, 1.4, 6), 'M_bronze', pos=(xx * sx, 0.2, -2.75), tint=BRZ)
        far.add(p_lathe([(0.0, 1.62), (0.16, 1.66), (0.2, 1.9), (0.12, 2.3), (0.0, 2.6)], 6, False, False), 'M_flame', pos=(xx * sx, 0, 2.75))
        far.add(p_lathe([(0.0, 1.62), (0.16, 1.66), (0.2, 1.9), (0.12, 2.3), (0.0, 2.6)], 6, False, False), 'M_flame', pos=(xx * sx, 0, -2.75))
# la grande porte d'Hadès au fond (nord)
hades_gate((0.0, -25.2), (0.0, -1.0), 15.0, 14.0, 8.4, 6.6, 2.2, 3)
for sx in (-1, 1):
    for k in range(3):
        dec.add(p_box(1.6, 8.5 + 1.5 * k, 1.6), 'M_basalt', pos=(sx * (10.5 + k * 2.2), 0.0, -25.0 - k * 0.6), tint=BAS, bev=0.05, yaw=0.3 * k)

# ------------------------------------------------------------------ braseros spectraux
torches(sc, rr, y=2.2, sconce_fn=make_torch_fn(mat='M_basalt', gold='M_bronze', flame='M_flame', t=BAS, t_gold=BRZ))

# ------------------------------------------------------------------ obstacles : orgues de basalte
for i in range(6):
    mb, o = obstacle_part(sc, i)
    r = o['r']
    x, z = o['x'], o['z']
    h = [4.4, 4.0, 4.7, 4.2, 3.9, 4.1][i]
    mb.add(p_lathe([(r, 0.0), (r, 0.3), (r * 0.92, 0.46)], 12, False, True, phase=0.0), 'M_basalt', pos=(x, 0, z), tint=BAS)
    mb.add(p_lathe([(r * 0.97, 0.26), (r * 0.99, 0.32)], 12, False, False), 'M_rune', pos=(x, 0, z), tint=(1, 1, 1))
    mb.add(p_lathe([(r * 0.58, 0.4), (r * 0.54, h)], 6, False, True, phase=0.2), 'M_basalt', pos=(x, 0, z), tint=BAS, jit=0.04)
    mb.add(p_lathe([(r * 0.5, h - 0.4), (0.0, h + 0.45 + 0.25 * (i % 3))], 6, False, False, phase=0.2), 'M_basalt', pos=(x, 0, z), tint=BAS)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3 * i
        hh = h * rng.uniform(0.35, 0.65)
        rx_, rz_ = x + r * 0.74 * math.cos(a), z + r * 0.74 * math.sin(a)
        mb.add(p_lathe([(r * 0.3, 0.3), (r * 0.28, hh)], 6, False, True, phase=0.5), 'M_basalt', pos=(rx_, 0, rz_), tint=BAS, jit=0.05)
        mb.add(p_lathe([(r * 0.28, hh - 0.04), (0.0, hh + r * 0.25)], 6, False, False, phase=0.5), 'M_basalt', pos=(rx_, 0, rz_), tint=BAS)
    # bandes runiques lumineuses sur le fût central
    mb.add(p_lathe([(r * 0.575, h * 0.62), (r * 0.57, h * 0.62 + 0.14)], 6, False, False, phase=0.2), 'M_rune', pos=(x, 0, z), tint=(1, 1, 1))
    mb.add(p_lathe([(r * 0.56, h * 0.3), (r * 0.555, h * 0.3 + 0.1)], 6, False, False, phase=0.2), 'M_rune', pos=(x, 0, z), tint=(1, 1, 1))
    far.sphere(0.22, pos=(x, h + 1.1 + 0.2 * (i % 3), z), mat='M_flame', nu=7, nv=4)

# ------------------------------------------------------------------ feux follets sur le Styx + barque de Charon
for i in range(26):
    a = rng.uniform(0, 2 * math.pi)
    d = rng.uniform(1.5, 8.0)
    P_, N_ = rr.at_base(rng.uniform(0, rr.length()), d)
    x, z = P_
    if abs(z) < 4.0 and abs(x) > 26:
        continue
    y = rng.uniform(0.2, 3.2)
    far.add(p_sphere(0.16, 6, 4), 'M_flame', pos=(x, y, z), scale=(1, 1.1, 1))
    far.add(p_lathe([(0.12, 0.0), (0.0, 0.7)], 6, False, False), 'M_flame', pos=(x, y + 0.1, z), pitch=math.pi, tint=(1, 1, 1))
bx, bz = -9.0, 16.0 + 4.6
dec.add(p_lathe([(0.0, 0.0), (0.55, 0.12), (0.78, 0.5), (0.7, 0.75), (0.58, 0.78)], 8, True, False), 'M_wood', pos=(bx, RIV_Y - 0.05, bz), scale=(1.0, 1.0, 3.0), tint=(0.34, 0.24, 0.17))
dec.add(p_box(0.1, 2.4, 0.1), 'M_wood', pos=(bx, RIV_Y + 0.5, bz + 1.8), tint=(0.3, 0.22, 0.15))
far.sphere(0.2, pos=(bx, RIV_Y + 2.95, bz + 1.8), mat='M_flame', nu=7, nv=4)
dec.add(p_box(0.06, 2.2, 0.06), 'M_wood', pos=(bx + 0.9, RIV_Y + 0.3, bz - 0.4), roll=0.5, tint=(0.3, 0.22, 0.15))

report(sc)
sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5}
sc.build(ao_samples=36, ao_dist=3.0, ao_floor=0.4)
sc.export(OUTDIR + '/arena_underworld.glb')
