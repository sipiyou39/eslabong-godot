"""arena_irongate.glb — « Porte de fer » : cour de forteresse en ruines, énorme porte de fer côté +X, tours, herses, pavés usés, barricades."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_common import *

T = lambda n: TEXDIR + '/' + n
G.seed(404)
rng = np.random.default_rng(404)

defmat('M_ground', tex=T('irongate_ground.png'), norm=T('irongate_ground_n.png'), rough=0.9, uv=1, norm_str=1.0, spec=0.3)
defmat('M_stone', tex=T('irongate_stone.png'), norm=T('irongate_stone_n.png'), rough=0.9, uv=4.0)
defmat('M_stone_dark', tex=T('irongate_stone_dark.png'), norm=T('irongate_stone_dark_n.png'), rough=0.9, uv=4.0)
defmat('M_iron', tex=T('irongate_iron.png'), norm=T('irongate_iron_n.png'), rough=0.6, metal=0.55, uv=2.0)
defmat('M_bronze', tex=T('irongate_iron.png'), norm=T('irongate_iron_n.png'), rough=0.5, metal=0.8, uv=2.0)
defmat('M_gold', rough=0.4, metal=0.85)
defmat('M_wood', tex=T('irongate_wood.png'), rough=0.9, uv=4.0)
defmat('M_rock', tex=T('irongate_rock.png'), norm=T('irongate_rock_n.png'), rough=0.95, uv=10.0)
defmat('M_cloth', tex=T('irongate_cloth.png'), rough=0.95, uv=2.0, double=True)
defmat('M_sand', tex=T('irongate_sand.png'), rough=1.0, uv=1.5)
defmat('M_dirt', tex=T('irongate_mud.png'), rough=1.0, uv=10.0)
defmat('M_crowd', rough=0.9, spec=0.2)
defmat('M_dark', rough=0.8)
defmat('M_roof', tex=T('irongate_stone_dark.png'), rough=0.8, uv=4.0)
defmat('M_flame', emit='#ff7a1c', emit_str=2.6, vcol=False, color='#ff7a1c')
defmat('M_glow', emit='#ff9a3a', emit_str=0.5, vcol=False, color='#ff9a3a')

IRT = (0.55, 0.55, 0.6)
STT = (1, 1, 1)

sc = Scene('arena_irongate')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
walls = sc.part('Walls')
build_ground(sc, step=0.6)

# ------------------------------------------------------------------ secteurs
GX = 26.0
skip = []
s_gate0, s_gate1 = rr.s_nearest(GX, -9.5), rr.s_nearest(GX, 9.5)
skip.append((s_gate0, s_gate1))
for zz in (-1, 1):
    s0 = rr.s_nearest(0.0, zz * 16.0)
    skip.append((s0 - 2.9, s0 + 2.9))
sec = (rr.s_nearest(GX, -14.5), rr.s_nearest(GX, 14.5))


def in_gate_zone(x, z):
    return x > 23.5 and abs(z) < 15.0


FACE_D = 0.36
build_walls(sc, rr, T=1.5, H=HW, face_d=FACE_D, mats=dict(face='M_stone', panel='M_stone_dark', trim='M_stone', top='M_stone_dark'),
            tints=dict(panel=(0.9, 0.9, 0.95), face=(1, 1, 1), trim=(0.95, 0.95, 0.95), top=(0.85, 0.85, 0.88)), skip=skip, panel_y=1.8, cornice=False)
# ceintures de fer
add_strip(walls, rr, [(FACE_D - 0.02, 1.78), (FACE_D - 0.02, 1.92)], 'M_iron', 'in', IRT, skip, 4.0)

# merlons en ruine
Pm, Nm, Tm, sm = rr.along(1.75, 0.7, offset=0.3)
for i in range(len(Pm)):
    s_here = rr.s_nearest(Pm[i][0], Pm[i][1])
    if any(a - 1.0 <= s_here <= b + 1.0 for a, b in skip):
        continue
    if rng.random() < 0.28:
        continue
    yaw = yaw_of(Nm[i][0], Nm[i][1])
    h = rng.choice([0.55, 0.8, 1.0, 1.0, 1.1])
    walls.box((0.95, h, 0.95), pos=(Pm[i][0], HW, Pm[i][1]), mat='M_stone', tint=(0.9, 0.9, 0.9), yaw=yaw + rng.uniform(-0.05, 0.05), jit=0.1, top=(0.88, 0.85))
    if rng.random() < 0.25:
        dec.rock((0.5, 0.35, 0.5), pos=(Pm[i][0] + rng.uniform(-0.5, 0.5), HW, Pm[i][1] + rng.uniform(-0.5, 0.5)), mat='M_stone', seed=i, sub=0, tint=(0.8, 0.8, 0.8))

pil = []
for x in (-24, -18, -12, -6, 6, 12, 18, 24):
    pil += [(x, 15.9), (x, -15.9)]
for z in (-5.2, 5.2) if False else ():
    pass
for k in range(3):
    a = math.radians(15 + 30 * k)
    for sx in (1, -1):
        for sz in (1, -1):
            if sx == 1:
                continue
            pil.append((sx * (21 + 5 * math.cos(a)), sz * (11 + 5 * math.sin(a))))
for z in (-8.5, -5.2, 0, 5.2, 8.5):
    pil.append((-25.9, z))
pilasters_on_wall(dec, rr, pil, FACE_D, HW, 'M_stone', (0.95, 0.95, 0.95), cap_mat='M_stone_dark', cap_tint=(0.9, 0.9, 0.95), w=0.8)

# ------------------------------------------------------------------ poternes avec herses (±Z, x=0)
def portcullis(mb, pos, nxz, ow, h_bar, zloc, spacing=0.3):
    yaw = yaw_of(*nxz)
    n = int(ow / spacing)
    for k in range(-n // 2, n // 2 + 1):
        lx = k * spacing
        if abs(lx) > ow / 2 - 0.12:
            continue
        x1, z1 = local_to_world(pos, nxz, lx, zloc)
        mb.add(p_box(0.07, h_bar, 0.07), 'M_iron', pos=(x1, 0.0, z1), tint=IRT)
        mb.add(p_cone(0.06, 0.28, 4), 'M_iron', pos=(x1, -0.0, z1), pitch=math.pi, tint=IRT) if False else None
    for yb in (0.5, 1.4, h_bar * 0.9):
        x1, z1 = local_to_world(pos, nxz, 0, zloc)
        mb.add(p_box(ow - 0.2, 0.08, 0.09), 'M_iron', pos=(x1, yb, z1), yaw=yaw, tint=IRT)


for zz in (-1, 1):
    pos = (0.0, zz * 16.0)
    nxz = (0.0, float(zz))
    yaw = yaw_of(*nxz)
    arch_block(walls, pos, nxz, 5.8, HW, 3.4, 0.9, 1.5, mat='M_stone', tint=STT, jit=0.03)
    x1, z1 = local_to_world(pos, nxz, 0, 1.2)
    walls.add(p_extrude_xy(opening_poly(3.38, 0.9, 10), 1.1, 1.18), 'M_dark', pos=(pos[0], 0, pos[1]), yaw=yaw, tint=(0.06, 0.06, 0.06))
    portcullis(dec, pos, nxz, 3.4, 2.7, 0.55)
    # linteau de fer
    x2, z2 = local_to_world(pos, nxz, 0, 0.1)
    dec.add(p_box(3.8, 0.18, 0.2), 'M_iron', pos=(x2, 2.75, z2), yaw=yaw, tint=IRT)
    sc.empty(f'Light_{(zz + 1) // 2 + 1:02d}', 0.0 + 0.0, 3.0, zz * 15.4)

# ------------------------------------------------------------------ la grande porte de fer (+X)
nxz = (1.0, 0.0)
gpos = (GX, 0.0)
gyaw = yaw_of(*nxz)
OW, SPR = 9.0, 5.0
arch_block(walls, gpos, nxz, 19.0, 14.0, OW, SPR, 9.0, mat='M_stone', tint=(0.95, 0.95, 0.95), jit=0.03)
# fond sombre du passage
walls.add(p_extrude_xy(opening_poly(OW - 0.02, SPR, 14), 5.2, 5.3), 'M_dark', pos=(gpos[0], 0, gpos[1]), yaw=gyaw, tint=(0.04, 0.04, 0.04))
# vantaux
leaf = opening_poly(OW - 0.3, SPR, 14)
dec.add(p_extrude_xy(leaf, 0.8, 1.25), 'M_iron', pos=(gpos[0], 0, gpos[1]), yaw=gyaw, tint=(0.9, 0.9, 0.98))
for yb in (1.0, 2.9, 4.8, 6.7, 8.6):
    hw_ = 4.45 if yb < SPR else math.sqrt(max(0.1, (OW / 2 - 0.15) ** 2 - (yb - SPR) ** 2)) - 0.1
    x1, z1 = local_to_world(gpos, nxz, 0, 0.72)
    dec.add(p_box(2 * hw_, 0.28, 0.14), 'M_iron', pos=(x1, yb, z1), yaw=gyaw, tint=(0.38, 0.38, 0.42), bev=0.02)
    for k in np.arange(-hw_ + 0.3, hw_ - 0.2, 0.7):
        xr, zr = local_to_world(gpos, nxz, k, 0.65)
        dec.add(p_ico(0.07, 0), 'M_iron', pos=(xr, yb + 0.0, zr), tint=(0.7, 0.7, 0.75))
x1, z1 = local_to_world(gpos, nxz, 0, 0.72)
dec.add(p_box(0.16, 9.0, 0.14), 'M_iron', pos=(x1, 0.0, z1), tint=(0.3, 0.3, 0.34))  # joint central
for sgn_ in (-1, 1):
    xr, zr = local_to_world(gpos, nxz, sgn_ * 1.1, 0.5)
    dec.add(p_torus(0.55, 0.09, 12, 5), 'M_iron', pos=(xr, 4.0, zr), roll=0, yaw=gyaw, pitch=math.pi / 2, tint=(0.3, 0.3, 0.34))
    dec.add(p_cyl(0.8, 0.08, 10), 'M_iron', pos=(xr, 4.0, zr), pitch=math.pi / 2, yaw=gyaw, tint=(0.35, 0.35, 0.4))
# barre de verrouillage
xr, zr = local_to_world(gpos, nxz, 0, 0.45)
dec.add(p_box(9.6, 0.5, 0.42), 'M_wood', pos=(xr, 3.6, zr), yaw=gyaw, tint=(0.55, 0.45, 0.35), bev=0.04)
for sgn_ in (-1, 1):
    xb, zb = local_to_world(gpos, nxz, sgn_ * 4.2, 0.5)
    dec.add(p_box(0.5, 1.3, 0.5), 'M_iron', pos=(xb, 3.0, zb), yaw=gyaw, tint=IRT, bev=0.03)
# herse relevée (pointes visibles)
yb0 = 7.4
for k in range(-8, 9):
    lx = k * 0.52
    ytop_k = SPR + math.sqrt(max(0.05, (OW / 2 - 0.2) ** 2 - lx ** 2)) - 0.1
    if ytop_k < yb0 + 0.6:
        continue
    xb, zb = local_to_world(gpos, nxz, lx, 0.25)
    dec.add(p_box(0.11, ytop_k - yb0, 0.11), 'M_iron', pos=(xb, yb0, zb), tint=(0.34, 0.34, 0.38))
    dec.add(p_lathe([(0.08, 0), (0.0, -0.55)], 4, True, False), 'M_iron', pos=(xb, yb0, zb), tint=(0.34, 0.34, 0.38))
for yb in (8.1, 9.0):
    xb, zb = local_to_world(gpos, nxz, 0, 0.25)
    hw_ = math.sqrt(max(0.05, (OW / 2 - 0.2) ** 2 - (yb - SPR) ** 2)) - 0.1
    dec.add(p_box(2 * hw_, 0.12, 0.12), 'M_iron', pos=(xb, yb, zb), yaw=gyaw, tint=(0.34, 0.34, 0.38))
# encadrement de pierre moulurée + clef de voûte + créneaux de la gatehouse
xk, zk = local_to_world(gpos, nxz, 0, 0.02)
dec.add(p_box(1.4, 1.6, 0.4), 'M_stone_dark', pos=(xk, SPR + OW / 2 - 0.2, zk), yaw=gyaw, tint=(0.9, 0.9, 0.95), bev=0.05)
for k in range(-8, 9):
    xm, zm = local_to_world(gpos, nxz, k * 1.12, 0.6)
    if rng.random() < 0.15:
        continue
    dec.box((0.8, 0.9, 0.8), pos=(xm, 14.0, zm), mat='M_stone', tint=(0.9, 0.9, 0.9), yaw=gyaw, jit=0.1)
# bannières géantes de part et d'autre
for sgn_ in (-1, 1):
    banner_object(sc, f'Banner_{(sgn_ + 1) // 2 + 1:02d}', (GX + 0.06, 11.8, sgn_ * 7.2), -math.pi / 2, 2.6, 6.0, '#2d3a52', '#b8bcc4', '#d9a02a', phase=sgn_, mat='M_cloth',
                  rod_mat='M_iron', rod_tint=IRT)
# tours
for sgn_ in (-1, 1):
    tx, tz = GX + 4.5, sgn_ * 13.0
    dec.add(p_lathe([(4.9, 0), (4.7, 3), (4.5, 15), (5.2, 15.3), (5.2, 16.4), (4.6, 16.6), (4.6, 17.2)], 16, False, True), 'M_stone', pos=(tx, 0, tz), tint=(0.92, 0.92, 0.92))
    dec.add(p_cone(5.3, 5.5, 16), 'M_roof', pos=(tx, 17.2, tz), tint=(0.5, 0.5, 0.58))
    dec.add(p_lathe([(5.35, 0), (5.1, 0.25)], 16, False, False), 'M_iron', pos=(tx, 17.2, tz), tint=IRT)
    for k in range(10):
        a = 2 * math.pi * k / 10
        dec.box((0.25, 1.1, 0.12), pos=(tx + 4.55 * math.cos(a), 6.5 + (k % 3) * 2.8, tz + 4.55 * math.sin(a)), mat='M_dark', tint=(0.08, 0.08, 0.08), yaw=-a + math.pi / 2)
    dec.add(p_cyl(0.05, 5.0, 4), 'M_wood', pos=(tx, 22.6, tz), tint=(0.4, 0.3, 0.2))
    pennant(dec, (tx, 0, tz), 24.0, 1.1, 3.4, yaw=math.pi / 2 + 0.2, c_main='#2d3a52', c_edge='#b8bcc4', phase=sgn_)

# ------------------------------------------------------------------ gradins (rempart)
ROWS = 6
D0, TREAD, RISE, Y0 = 1.5, 0.95, 0.5, HW
tiers, dend, ytop = build_tiers(sc, rr, D0, Y0, ROWS, TREAD, RISE, 'M_wood', 'M_stone_dark', tint_tread=(0.85, 0.75, 0.65), tint_riser=(0.8, 0.8, 0.85),
                                back=1.3, skip=[sec])
D_ARC = dend + 1.3
solid_ring(sc, rr, 'Stands', D_ARC, D_ARC + 1.3, 0.0, ytop, 'M_stone_dark', tint=(0.8, 0.8, 0.85), inner=False, top=False, skip=[sec])
crowd_pal = ['#2a3140', '#3a4256', '#4a3a2a', '#5a2a24', '#6a6a70', '#2e2e32', '#3a4a3a', '#7a6a50', '#8a2a26']
skin = ['#e8c4a4', '#d4a07a', '#b88060', '#9a6648', '#f0d4b8']
hair = ['#8a8f99', '#6a6f78', '#a0a4ad', '#4a4e56', '#7a5a3a', '#5a4030']
BOX_X = 5.6


def ex(px, pz):
    return in_gate_zone(px, pz) or (pz < 0 and abs(px) < BOX_X and (-(pz + 16.0)) > 1.3 and (-(pz + 16.0)) < 6.0)


cnt = crowd(sc.part('Stands'), rr, tiers, crowd_pal, skin, hair, spacing=1.15, skip=0.2, rng=rng, exclude=ex)
print('spectateurs', cnt)

# loge d'état-major (côté -Z) : estrade de bois + bannières
zc = -(16.0 + 3.6)
ybase = Y0 + RISE * 3
zf, zb = -(16.0 + 1.8), -(16.0 + 5.4)
dec.box((BOX_X * 2, 0.5, 4.5), pos=(0, ybase - 0.45, zc), mat='M_stone_dark', tint=(0.85, 0.85, 0.9), bev=0.05)
dec.box((BOX_X * 2 + 0.4, 0.15, 4.8), pos=(0, ybase + 0.03, zc), mat='M_wood', tint=(0.8, 0.7, 0.6), bev=0.03)
for xx in (-BOX_X + 0.4, -BOX_X / 3, BOX_X / 3, BOX_X - 0.4):
    for zz in (zf, zb):
        dec.box((0.4, 3.4, 0.4), pos=(xx, ybase + 0.15, zz), mat='M_wood', tint=(0.7, 0.6, 0.5), bev=0.03)
yr = ybase + 3.5
dec.box((BOX_X * 2 + 0.6, 0.35, 5.0), pos=(0, yr, zc), mat='M_wood', tint=(0.7, 0.6, 0.5), bev=0.04)
dec.add(p_extrude_xy([(-2.8, 0), (2.8, 0), (0.0, 1.3)], -(BOX_X + 0.5), BOX_X + 0.5), 'M_roof', pos=(0, yr + 0.35, zc), yaw=math.pi / 2, tint=(0.6, 0.6, 0.65))
for xx in (-BOX_X / 3 * 2, 0, BOX_X / 3 * 2):
    dec.add(p_banner(BOX_X * 0.55, 2.4, 3, 5, 0.1, 0.0)[:2], 'M_cloth', pos=(xx, yr - 0.1, zf - 0.1), tint=(0.17, 0.22, 0.34), yaw=math.pi)
brazier(dec, (-BOX_X + 0.4, ybase + 0.15, zf + 0.5), h=0.8, r=0.35, tint=(0.25, 0.25, 0.28))
brazier(dec, (BOX_X - 0.4, ybase + 0.15, zf + 0.5), h=0.8, r=0.35, tint=(0.25, 0.25, 0.28))

# ------------------------------------------------------------------ rempart extérieur (fentes de tir), créneaux, tours
Yp = ytop
ARC_H = 7.0
arcade_ring(sc, rr, 'Decor', D_ARC, Yp, ARC_H, bay=3.7, open_ratio=0.27, spring=3.6, depth=1.3, mat='M_stone_dark', tint=(0.9, 0.9, 0.95),
            glow_mat=None, kind='round', n=8, skip_fn=lambda x, z: in_gate_zone(x, z) or (x > 30 and abs(z) < 20))
solid_ring(sc, rr, 'Decor', D_ARC - 0.15, D_ARC + 1.6, Yp + ARC_H, Yp + ARC_H + 0.5, 'M_stone', tint=(0.9, 0.9, 0.92), inner=True, top=True, outer=True, skip=[sec])
Pm2, Nm2, Tm2, sm2 = rr.along(1.9, D_ARC + 0.1, offset=0.2)
for i in range(len(Pm2)):
    if in_gate_zone(Pm2[i][0], Pm2[i][1]) or rng.random() < 0.18:
        continue
    yaw = yaw_of(Nm2[i][0], Nm2[i][1])
    dec.box((1.1, rng.choice([0.9, 1.1, 1.3]), 0.9), pos=(Pm2[i][0], Yp + ARC_H + 0.5, Pm2[i][1]), mat='M_stone', tint=(0.9, 0.9, 0.9), yaw=yaw, jit=0.1)
# tours rondes tous les ~24 m
Pt, Nt, Tt, st = rr.along(24.0, D_ARC + 0.7, offset=3.0)
for i in range(len(Pt)):
    x, z = Pt[i]
    if in_gate_zone(x, z) or x > 30:
        continue
    h = Yp + ARC_H + rng.uniform(3, 6)
    dec.add(p_lathe([(3.2, 0), (3.0, 2), (2.9, h - 1.4), (3.5, h - 1.2), (3.5, h), (3.0, h + 0.2), (3.0, h + 0.8)], 12, False, True), 'M_stone', pos=(x, 0, z), tint=(0.88, 0.88, 0.9))
    dec.add(p_cone(3.7, 3.6, 12), 'M_roof', pos=(x, h + 0.8, z), tint=(0.5, 0.5, 0.58))
    for k in range(6):
        a = 2 * math.pi * k / 6
        dec.box((0.22, 0.9, 0.1), pos=(x + 2.95 * math.cos(a), h * 0.55, z + 2.95 * math.sin(a)), mat='M_dark', tint=(0.08, 0.08, 0.08), yaw=-a + math.pi / 2)
    sc.empty(f'Light_{3 + (i % 4):02d}', x, h * 0.55, z) if i < 4 else None

# mâts à torche sur le promenoir
P3, N3, T3, s3 = rr.along(8.0, D_ARC - 0.4, offset=0.5)
for i in range(len(P3)):
    x, z = P3[i]
    if in_gate_zone(x, z) or x > 28:
        continue
    dec.box((0.14, 3.6, 0.14), pos=(x, Yp, z), mat='M_wood', tint=(0.5, 0.4, 0.3))
    brazier(dec, (x, Yp + 2.4, z), h=0.45, r=0.35, tint=(0.25, 0.25, 0.28), flame_h=0.9, legs=3)

# bannières murales
bi = 3
for x in (-21, -15, -9, -3, 3, 9, 15, 21):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, -(16 + 0.2)), math.pi, 1.5, 2.0, '#2d3a52', '#8a8f99', '#c9a02a', phase=bi, mat='M_cloth', rod_mat='M_iron', rod_tint=IRT)
    bi += 1


def iron_sconce(md, mf, Fp, n, arm):
    sconce(md, mf, Fp, n, arm, tint=(0.32, 0.32, 0.36))


torches(sc, rr, y=2.2, sconce_fn=iron_sconce)

# ------------------------------------------------------------------ obstacles
def bastion(mb, x, z, r, h):
    mb.lathe([(r, 0), (r, 0.5), (r * 0.94, 0.62), (r * 0.94, h - 0.5), (r * 1.06, h - 0.38), (r * 1.06, h)], pos=(x, 0, z), mat='M_stone', seg=8, tint=(0.95, 0.95, 0.95), jit=0.04)
    for yb in (0.95, 1.8, 2.5):
        mb.lathe([(r * 0.945, 0), (r * 0.99, 0.13), (r * 0.945, 0.2)], pos=(x, yb, z), mat='M_iron', seg=8, tint=(0.4, 0.4, 0.45), cap0=False, cap1=False)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        mb.box((0.55, 0.5, 0.4), pos=(x + r * 0.9 * math.cos(a), h, z + r * 0.9 * math.sin(a)), mat='M_stone', tint=(0.9, 0.9, 0.9), yaw=-a + math.pi / 2, jit=0.08)
    mb.lathe([(r * 0.85, h), (r * 0.7, h + 0.05)], pos=(x, 0, z), mat='M_dark', seg=8, tint=(0.15, 0.15, 0.15))
    brazier(mb, (x, h, z), h=0.3, r=0.45, tint=(0.25, 0.25, 0.28), flame_h=0.45, legs=3)


def barricade(mb, x, z, r, hs):
    # anneaux de sacs de sable
    bag = p_box(0.56, 0.26, 0.36, top=(0.46, 0.28))
    for row in range(4):
        rho = r - 0.19 - 0.05 * row
        n = int(2 * math.pi * rho / 0.6)
        pos, yaw, sc_, tint = [], [], [], []
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * (row % 2)) / n
            pos.append((x + rho * math.cos(a), 0.26 * row, z + rho * math.sin(a)))
            yaw.append(-(a + math.pi / 2) + rng.uniform(-0.08, 0.08))
            sc_.append((1.0, rng.uniform(0.9, 1.1), 1.0))
            tint.append(s2l('#a89468') * rng.uniform(0.75, 1.05))
        mb.add_many(bag, 'M_sand', pos, yaw=yaw, scale=np.array(sc_), tint=np.array(tint))
    mb.add(p_cyl(r * 0.72, 0.1, 14), 'M_dirt', pos=(x, 0.9, z), tint=(0.6, 0.55, 0.5))
    # palissade de pieux inclinés vers l'extérieur
    nst = 14
    for k in range(nst):
        a = 2 * math.pi * k / nst
        hh = hs + rng.uniform(-0.25, 0.2)
        rho = r * 0.66
        mb.add(p_box(0.2, hh, 0.2, top=(0.03, 0.03)), 'M_wood', pos=(x + rho * math.cos(a), 0.7, z + rho * math.sin(a)), yaw=math.pi / 2 - a, pitch=0.18,
               tint=(0.55 + rng.uniform(-0.08, 0.08),) * 3, jit=0.1)
    for yb in (1.7, 2.5):
        mb.lathe([(r * 0.74, 0), (r * 0.76, 0.12), (r * 0.74, 0.22)], pos=(x, yb, z), mat='M_iron', seg=14, tint=(0.35, 0.35, 0.4), cap0=False, cap1=False)


def ironblock(mb, x, z, r, h):
    s = r * math.sqrt(2.0)
    mb.box((s, h, s), pos=(x, 0, z), mat='M_stone_dark', tint=(0.9, 0.9, 0.95), yaw=math.pi / 4, bev=0.06, top=(s * 0.92, s * 0.92))
    for yb in (0.45, 1.45, 2.45):
        mb.box((s * 0.98 + 0.12, 0.2, s * 0.98 + 0.12), pos=(x, yb, z), mat='M_iron', tint=(0.4, 0.4, 0.45), yaw=math.pi / 4, bev=0.02)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        mb.box((0.2, h, 0.2), pos=(x + (r - 0.08) * math.cos(a), 0, z + (r - 0.08) * math.sin(a)), mat='M_iron', tint=(0.35, 0.35, 0.4), yaw=math.pi / 4)
        mb.add(p_cone(0.13, 0.55, 5), 'M_iron', pos=(x + (r * 0.8) * math.cos(a), h, z + (r * 0.8) * math.sin(a)), tint=(0.4, 0.4, 0.45))
    mb.add(p_cone(0.17, 0.7, 5), 'M_iron', pos=(x, h, z), tint=(0.4, 0.4, 0.45))
    # flammes de suie : plaques d'identification
    mb.add(p_box(0.9, 0.5, 0.05), 'M_iron', pos=(x + (r * 0.55) * math.cos(0.0), 1.9, z - r * 0.5), yaw=0, tint=(0.3, 0.3, 0.34))


kinds = ['bastion', 'barricade', 'block', 'bastion', 'barricade', 'block']
hts = [3.7, 3.3, 3.4, 3.8, 3.2, 3.6]
for i in range(6):
    mb, o = obstacle_part(sc, i)
    if kinds[i] == 'bastion':
        bastion(mb, o['x'], o['z'], o['r'], hts[i] - 0.5)
    elif kinds[i] == 'barricade':
        barricade(mb, o['x'], o['z'], o['r'], hts[i] - 0.4)
    else:
        ironblock(mb, o['x'], o['z'], o['r'], hts[i] - 0.5)

# ------------------------------------------------------------------ décor lointain
far = dec
far.add(p_cyl(160, 0.2, 40, cap0=False, cap1=True), 'M_dirt', pos=(0, -0.3, 0), tint=(0.8, 0.75, 0.7))
for i in range(26):
    a = 2 * math.pi * i / 26 + rng.uniform(-0.1, 0.1)
    R = rng.uniform(95, 140)
    w = rng.uniform(40, 75)
    h = rng.uniform(16, 40)
    mound(far, (R * math.cos(a), -2, R * math.sin(a)), (w, h, w * 0.8), seed=i, tint=(0.62, 0.62, 0.68), mat='M_rock', rough=0.3, vf=vgrad(0, h, 0.6, 1.25))
for i in range(70):
    a = rng.uniform(0, 2 * math.pi)
    R = rng.uniform(52, 95)
    x, z = R * math.cos(a), R * math.sin(a)
    if float(rr.sdf(np.array(x), np.array(z))) < 24 or (x > 20 and abs(z) < 30):
        continue
    w, d = rng.uniform(3.5, 9), rng.uniform(3.5, 9)
    h = rng.uniform(5, 20)
    building(far, (x, 0, z), w, d, h, yaw=rng.uniform(0, 3.14), mat='M_stone_dark', tint=(0.85, 0.85, 0.9), roof=rng.choice(['flat', 'gable', 'cone']), roof_tint=(0.45, 0.42, 0.45))
for i in range(36):  # arbres morts
    a = rng.uniform(0, 2 * math.pi)
    R = rng.uniform(45, 100)
    x, z = R * math.cos(a), R * math.sin(a)
    if float(rr.sdf(np.array(x), np.array(z))) < 20 or (x > 20 and abs(z) < 30):
        continue
    far.add(p_lathe([(0.35, 0), (0.18, 4), (0.05, 7)], 5, False, False), 'M_wood', pos=(x, 0, z), tint=(0.35, 0.3, 0.27), pitch=rng.uniform(-0.1, 0.1))
# camp / forteresse au loin derrière la porte
for k in range(5):
    far.add(p_box(6, 0.8, 6), 'M_dark', pos=(45 + k * 9, 0, -10 + k * 5), tint=(0.1, 0.1, 0.1)) if False else None
sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5}
sc.build(ao_samples=40, ao_dist=3.0, ao_floor=0.45)
sc.export(OUTDIR + '/arena_irongate.glb')
