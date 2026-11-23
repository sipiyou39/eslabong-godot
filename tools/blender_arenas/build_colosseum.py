"""arena_colosseum.glb — colisée de sable doré, pierre claire, arches, drapeaux rouges/or, colonnes cassées."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_common import *

T = lambda n: TEXDIR + '/' + n
G.seed(101)
rng = np.random.default_rng(101)

# ------------------------------------------------------------------ matériaux
defmat('M_ground', tex=T('colosseum_ground.png'), norm=T('colosseum_ground_n.png'), rough=0.97, uv=1, norm_str=0.9, spec=0.2)
defmat('M_stone', tex=T('colosseum_stone.png'), norm=T('colosseum_stone_n.png'), rough=0.88, uv=4.0, spec=0.3)
defmat('M_stone_warm', tex=T('colosseum_stone_warm.png'), norm=T('colosseum_stone_warm_n.png'), rough=0.9, uv=4.0, spec=0.3)
defmat('M_marble', tex=T('colosseum_marble.png'), norm=T('colosseum_marble_n.png'), rough=0.7, uv=4.0, spec=0.45)
defmat('M_plaster', tex=T('colosseum_plaster.png'), rough=0.85, uv=4.0)
defmat('M_gold', rough=0.32, metal=0.9, spec=0.6)
defmat('M_bronze', tex=T('colosseum_bronze.png'), norm=T('colosseum_bronze_n.png'), rough=0.42, metal=0.75, uv=2.0)
defmat('M_cloth', tex=T('colosseum_plaster.png'), rough=0.88, uv=2.0, double=True)
defmat('M_wood', tex=T('colosseum_wood.png'), rough=0.8, uv=4.0)
defmat('M_crowd', rough=0.9, spec=0.2)
defmat('M_rock', tex=T('colosseum_rock.png'), norm=T('colosseum_rock_n.png'), rough=0.95, uv=10.0)
defmat('M_dirt', tex=T('colosseum_dirt.png'), rough=1.0, uv=10.0)
defmat('M_roof', tex=T('colosseum_plaster.png'), rough=0.75, uv=3.0)
defmat('M_dark', rough=0.55, metal=0.5, spec=0.4)
defmat('M_flame', emit='#ff7a1c', emit_str=2.6, vcol=False, color='#ff7a1c')
defmat('M_glow', emit='#ff9a3a', emit_str=0.55, vcol=False, color='#ff9a3a')

RED = '#a3262c'
GOLD = '#dcab3c'
CREAM = '#eadcb8'
DARKRED = '#6e1a20'
GOLDT = (0.9, 0.68, 0.25)
STONET = (1.0, 0.96, 0.86)
WARMT = (1.0, 0.92, 0.78)

sc = Scene('arena_colosseum')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')

build_ground(sc, step=0.6)

# ------------------------------------------------------------------ murs, portes
GATE_W = 6.8
skip = []
for sx in (1, -1):
    s0 = rr.s_nearest(26.0 * sx, 0.0)
    skip.append((s0 - GATE_W / 2, s0 + GATE_W / 2))
FACE_D = 0.36
build_walls(sc, rr, T=1.5, H=HW, face_d=FACE_D,
            mats=dict(face='M_stone', panel='M_plaster', trim='M_stone', top='M_stone_warm'),
            tints=dict(panel=(0.85, 0.28, 0.27), face=(1, 1, 1), trim=(1.0, 0.96, 0.86), top=(1, 0.95, 0.85)), skip=skip, panel_y=1.8)
walls = sc.part('Walls')
add_strip(walls, rr, [(FACE_D - 0.015, 1.8), (FACE_D - 0.015, 1.98)], 'M_gold', 'in', GOLDT, skip, 4.0)
add_strip(walls, rr, [(FACE_D - 0.015, 0.62), (FACE_D - 0.015, 0.7)], 'M_gold', 'in', GOLDT, skip, 4.0)

pil = []
for x in (-24, -18, -12, -6, 0, 6, 12, 18, 24):
    pil += [(x, 15.9), (x, -15.9)]
for z in (-8.5, -5.2, 5.2, 8.5):
    pil += [(25.9, z), (-25.9, z)]
for k in range(3):
    a = math.radians(15 + 30 * k)
    for sx in (1, -1):
        for sz in (1, -1):
            pil.append((sx * (21 + 5 * math.cos(a)), sz * (11 + 5 * math.sin(a))))
pilasters_on_wall(dec, rr, pil, FACE_D, HW, 'M_marble', STONET, cap_mat='M_stone_warm', cap_tint=(1.0, 0.95, 0.8), w=0.78)

for sx in (1, -1):
    nxz = (float(sx), 0.0)
    pos = (26.0 * sx, 0.0)
    yaw = yaw_of(*nxz)
    ow = 4.2
    arch_block(walls, pos, nxz, GATE_W, HW, ow, 0.7, 1.5, mat='M_stone', tint=STONET)
    n = 12
    R0, R1 = ow / 2, ow / 2 + 0.28
    outer = [(R1 * math.cos(math.pi * i / n), 0.7 + R1 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    inner = [(R0 * math.cos(math.pi * i / n), 0.7 + R0 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    band = [(R1, 0), (R1, 0.7)] + outer[1:-1] + [(-R1, 0.7), (-R1, 0), (-R0, 0), (-R0, 0.7)] + inner[::-1][1:-1] + [(R0, 0.7), (R0, 0)]
    dec.add(p_extrude_xy(band, 0.0, 0.1), 'M_gold', pos=(pos[0], 0, pos[1]), yaw=yaw, tint=GOLDT)
    door = opening_poly(ow - 0.05, 0.7, 12)
    dec.add(p_extrude_xy(door, 0.9, 1.08), 'M_wood', pos=(pos[0], 0, pos[1]), yaw=yaw, tint=(0.8, 0.62, 0.42))
    x1, z1 = local_to_world(pos, nxz, 0, 1.12)
    for yb, L in ((0.5, 4.1), (1.5, 4.1), (2.35, 3.0)):
        dec.add(p_box(L, 0.15, 0.09), 'M_bronze', pos=(x1, yb, z1), yaw=yaw, tint=(0.75, 0.55, 0.28))
    dec.add(p_box(0.1, 3.0, 0.1), 'M_dark', pos=(x1, 0.0, z1), yaw=yaw, tint=(0.3, 0.3, 0.32))

# ------------------------------------------------------------------ gradins
ROWS = 8
D0, TREAD, RISE, Y0 = 1.5, 0.95, 0.55, HW


def tread_vf(V):
    ang = np.arctan2(V[:, 2] * 1.6, V[:, 0])
    st = 0.5 + 0.5 * np.cos(ang * 18)
    return 1 - 0.12 * (st > 0.93)


tiers, dend, ytop = build_tiers(sc, rr, D0, Y0, ROWS, TREAD, RISE, 'M_stone_warm', 'M_stone', tint_tread=(1.0, 0.93, 0.8),
                                tint_riser=(0.95, 0.88, 0.76), back=1.3, tread_vf=tread_vf)
D_ARC = dend + 1.3
solid_ring(sc, rr, 'Stands', D_ARC, D_ARC + 1.3, 0.0, ytop, 'M_stone_warm', tint=(0.95, 0.88, 0.75), inner=False, top=False)

BOX_X = 5.6


def in_box(px, pz):
    d = pz - 16.0
    return pz < 0 and (abs(px) < BOX_X) and (-d > 1.3) and (-d < 6.4)


crowd_pal = ['#b3262c', '#c9322f', '#e9d9b0', '#f0e6c8', '#d9a437', '#8a1d2b', '#355c8c', '#4d7a4a', '#a8742f', '#f2efe6', '#7a3b4f',
             '#c46a2b', '#e0c070']
skin = ['#f1c9a0', '#e0a97a', '#c68a5b', '#a56a40', '#8a5230', '#f4d3b2']
hair = ['#2a1d14', '#4a2e1a', '#7a5226', '#c9a14a', '#1a1412', '#8a8a8a', '#5a2a1a', '#a3262c', '#dcab3c']
cnt = crowd(sc.part('Stands'), rr, tiers, crowd_pal, skin, hair, spacing=0.95, skip=0.1, rng=rng, exclude=in_box)
print('spectateurs', cnt)

# ------------------------------------------------------------------ loge d'honneur (côté -Z, face à la caméra)
sgn = -1
zc = sgn * (16.0 + 3.7)
ybase = Y0 + RISE * 3
zf, zb = sgn * (16.0 + 1.8), sgn * (16.0 + 5.7)
dec.box((BOX_X * 2, 0.5, 4.9), pos=(0, ybase - 0.45, zc), mat='M_stone', tint=STONET, bev=0.05)
dec.box((BOX_X * 2 + 0.5, 0.18, 5.2), pos=(0, ybase + 0.03, zc), mat='M_stone_warm', tint=WARMT, bev=0.04)
dec.box((BOX_X * 2 - 0.3, 0.05, 4.6), pos=(0, ybase + 0.2, zc), mat='M_plaster', tint=(0.55, 0.1, 0.12))
for xx in (-BOX_X + 0.5, -BOX_X / 3, BOX_X / 3, BOX_X - 0.5):
    for zz in (zf, zb):
        column(dec, (xx, zz), 0.36, 3.5, mat='M_marble', tint=STONET, capital=True, seg=16, flutes=(8, 0.06), drums=2, base_h=0.25,
               shaft_ratio=0.76, gold=True, cap_mat='M_stone_warm', y0=ybase + 0.2)
yr = ybase + 3.7
dec.box((BOX_X * 2 + 0.8, 0.4, 5.4), pos=(0, yr, zc), mat='M_stone_warm', tint=WARMT, bev=0.06)
dec.box((BOX_X * 2 + 1.2, 0.18, 5.8), pos=(0, yr + 0.4, zc), mat='M_gold', tint=GOLDT, bev=0.03)
# toit à deux pans (faîtage le long de X) en tuiles
roof = p_extrude_xy([(-3.0, 0), (3.0, 0), (0.0, 2.0)], -(BOX_X + 0.6), BOX_X + 0.6)
dec.add(roof, 'M_roof', pos=(0, yr + 0.58, zc), yaw=math.pi / 2, tint=(0.78, 0.28, 0.2), jit=0.05)
dec.add(p_extrude_xy([(-3.2, 0), (3.2, 0), (0.0, 2.15)], -(BOX_X + 0.65), -(BOX_X + 0.4)), 'M_gold', pos=(0, yr + 0.5, zc), yaw=math.pi / 2, tint=GOLDT)
dec.add(p_extrude_xy([(-3.2, 0), (3.2, 0), (0.0, 2.15)], BOX_X + 0.4, BOX_X + 0.65), 'M_gold', pos=(0, yr + 0.5, zc), yaw=math.pi / 2, tint=GOLDT)
for xx in (-BOX_X / 3 * 2, 0, BOX_X / 3 * 2):
    dec.add(p_banner(BOX_X * 0.55, 2.4, 3, 5, 0.1, 0.0)[:2], 'M_cloth', pos=(xx, yr - 0.1, zf - 0.1), tint=(0.62, 0.1, 0.14), yaw=math.pi)
dec.box((1.5, 1.1, 0.8), pos=(0, ybase + 0.2, zb + 0.3), mat='M_gold', tint=GOLDT, bev=0.08)
dec.box((1.6, 2.2, 0.25), pos=(0, ybase + 0.2, zb + 0.75), mat='M_gold', tint=GOLDT, bev=0.06)
for xx in (-BOX_X + 0.4, BOX_X - 0.4):
    brazier(dec, (xx, ybase + 0.2, zf + 0.5), h=0.8, r=0.35, tint=(0.35, 0.28, 0.2))
sc.empty('Light_05', 0.0, ybase + 2.0, zc)

# ------------------------------------------------------------------ arcade de façade
Yp = ytop
nbay = int(round((rr.length() + 2 * math.pi * D_ARC) / 3.7))
P, N, Tn, s = rr.along(0, D_ARC, count=nbay)
ARC_H = 5.6
for i in range(nbay):
    p0, p1 = P[i], P[(i + 1) % nbay]
    mid = (p0 + p1) / 2
    t = p1 - p0
    wd = float(np.hypot(*t)) + 0.01
    nrm = np.array([t[1], -t[0]])
    nrm /= np.linalg.norm(nrm)
    if np.dot(nrm, mid) < 0:
        nrm = -nrm
    arch_block(dec, (mid[0], mid[1]), (nrm[0], nrm[1]), wd, ARC_H, wd * 0.62, 2.9, 1.3, mat='M_stone_warm', y0=Yp, tint=(1.0, 0.91, 0.78),
               glow_mat='M_glow' if (i % 3 != 1) else None, glow_tint=(1, 1, 1))
solid_ring(sc, rr, 'Decor', D_ARC - 0.15, D_ARC + 1.6, Yp + ARC_H, Yp + ARC_H + 0.5, 'M_stone_warm', tint=WARMT, inner=True, top=True, outer=True)
add_strip(dec, rr, [(D_ARC - 0.2, Yp + ARC_H + 0.18), (D_ARC - 0.2, Yp + ARC_H + 0.34)], 'M_gold', 'in', GOLDT, None, 4.0)
add_strip(dec, rr, [(D_ARC + 1.5, Yp + ARC_H + 0.5), (D_ARC + 1.5, Yp + ARC_H + 1.2)], 'M_stone_warm', 'in', WARMT, None, 4.0)
add_strip(dec, rr, [(D_ARC + 1.5, Yp + ARC_H + 1.2), (D_ARC + 1.7, Yp + ARC_H + 1.2)], 'M_stone_warm', 'up', WARMT, None, 4.0)

P2, N2, T2, s2 = rr.along(7.4, D_ARC + 0.9, offset=1.0)
ytop_arc = Yp + ARC_H + 0.5
for i in range(len(P2)):
    x, z = P2[i]
    nx, nz = N2[i]
    if i % 2 == 0:
        dec.box((0.16, 7.5, 0.16), pos=(x, ytop_arc, z), mat='M_wood', tint=(0.5, 0.35, 0.2), top=(0.1, 0.1))
        dec.sphere(0.18, pos=(x, ytop_arc + 7.65, z), mat='M_gold', tint=GOLDT, nu=6, nv=3)
        col = RED if (i // 2) % 2 == 0 else GOLD
        pennant(dec, (x, ytop_arc, z), 6.2, 1.1, 3.8, yaw=math.atan2(-nz, nx) + rng.uniform(-0.3, 0.3), c_main=col,
                c_edge=GOLD if col == RED else RED, phase=rng.uniform(0, 6))
    else:
        brazier(dec, (x, ytop_arc, z), h=1.0, r=0.55, tint=(0.3, 0.26, 0.2), flame_h=1.1)

# colonnes de victoire aux 4 coins (sur le promenoir)
li = 1
for sx in (-1, 1):
    for sz in (-1, 1):
        a = math.radians(45)
        px, pz = sx * (21.0 + (5 + 8.7) * math.cos(a)), sz * (11.0 + (5 + 8.7) * math.sin(a))
        yb = Yp
        dec.lathe([(1.05, yb), (1.05, yb + 0.5), (0.9, yb + 0.7)], pos=(px, 0, pz), mat='M_stone_warm', seg=12, tint=WARMT)
        cy = yb + 0.7
        dec.add(p_lathe([(0.78, 0), (0.7, 6.0)], 20, False, False, flutes=(10, 0.07)), 'M_marble', pos=(px, cy, pz), tint=STONET)
        dec.lathe([(0.9, 0), (0.95, 0.15), (1.2, 0.4), (1.3, 0.6)], pos=(px, cy + 6.0, pz), mat='M_stone_warm', seg=16, tint=WARMT)
        dec.cyl(0.72, 0.18, pos=(px, cy + 6.6, pz), mat='M_gold', seg=12, tint=GOLDT)
        brazier(dec, (px, cy + 6.7, pz), h=0.5, r=0.8, tint=(0.3, 0.24, 0.16), flame_h=1.6)
        sc.empty(f'Light_{li:02d}', px, cy + 8.2, pz)
        li += 1

# ------------------------------------------------------------------ bannières animables
bi = 1
for x in (-21, -15, -9, -3, 3, 9, 15, 21):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, -(16 + 0.2)), math.pi, 1.5, 2.0, RED, GOLD, GOLD, phase=bi)
    bi += 1
for x in (-18, -6, 6, 18):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, 16 + 0.2), 0.0, 1.5, 2.0, DARKRED, GOLD, GOLD, phase=bi)
    bi += 1

torches(sc, rr, y=2.2)

# ------------------------------------------------------------------ obstacles : colonnes
specs = [
    dict(h=3.9, broken=0.9, drums=4, ribbon=True),
    dict(h=3.3, broken=0.8, drums=3, ribbon=False),
    dict(h=3.7, broken=0.6, drums=4, ribbon=False),
    dict(h=3.6, broken=1.0, drums=4, ribbon=True),
    dict(h=3.0, broken=0.7, drums=3, ribbon=False),
    dict(h=3.8, broken=0.5, drums=4, ribbon=True),
]
for i, sp in enumerate(specs):
    mb, o = obstacle_part(sc, i)
    r = o['r']
    column(mb, (o['x'], o['z']), r, sp['h'], mat='M_marble', tint=STONET, capital=(sp['broken'] == 0), seg=42, flutes=(14, 0.06),
           broken=sp['broken'], seed=i + 5, drums=sp['drums'], gold=False, base_h=0.5, cap_mat='M_marble', shaft_ratio=0.8)
    if sp['ribbon']:
        mb.lathe([(r * 0.74, 0), (r * 0.77, 0.14), (r * 0.74, 0.28)], pos=(o['x'], 2.2, o['z']), mat='M_cloth', seg=20, tint=(0.62, 0.1, 0.14), cap0=False, cap1=False)
        mb.lathe([(r * 0.77, 0), (r * 0.79, 0.05)], pos=(o['x'], 2.2 + 0.28, o['z']), mat='M_gold', seg=20, tint=GOLDT, cap0=False, cap1=False)
        mb.lathe([(r * 0.77, 0), (r * 0.79, 0.05)], pos=(o['x'], 2.2 - 0.05, o['z']), mat='M_gold', seg=20, tint=GOLDT, cap0=False, cap1=False)
    else:
        for k in range(4):
            a = rng.uniform(0, 2 * math.pi)
            mb.rock((0.32, 0.2, 0.32), pos=(o['x'] + (r * 0.72) * math.cos(a), 0.45, o['z'] + (r * 0.72) * math.sin(a)), mat='M_marble', seed=k + i, sub=0, tint=STONET)

# ------------------------------------------------------------------ décor lointain
far = dec
far.add(p_cyl(160, 0.2, 40, cap0=False, cap1=True), 'M_dirt', pos=(0, -0.3, 0), tint=(0.9, 0.75, 0.55))
for i in range(26):
    a = 2 * math.pi * i / 26 + rng.uniform(-0.1, 0.1)
    R = rng.uniform(95, 135)
    w = rng.uniform(40, 70)
    h = rng.uniform(14, 34)
    mound(far, (R * math.cos(a), -2, R * math.sin(a)), (w, h, w * 0.8), seed=i, tint=(0.85, 0.66, 0.58), vf=vgrad(0, 30, 0.7, 1.15), rough=0.3)
for i in range(120):
    a = rng.uniform(0, 2 * math.pi)
    R = rng.uniform(52, 92)
    x, z = R * math.cos(a), R * math.sin(a)
    if float(rr.sdf(np.array(x), np.array(z))) < 24:
        continue
    w, d = rng.uniform(3.5, 9), rng.uniform(3.5, 9)
    h = rng.uniform(4, 15) * (1 + (R - 52) / 90)
    tint = [(0.95, 0.82, 0.62), (0.9, 0.72, 0.52), (0.98, 0.9, 0.76), (0.85, 0.6, 0.45)][rng.integers(4)]
    roof = ['flat', 'gable', 'dome', 'cone'][rng.integers(4)]
    building(far, (x, 0, z), w, d, h, yaw=rng.uniform(0, 3.14), tint=tint, roof=roof, roof_tint=(0.75, 0.3, 0.2) if roof != 'dome' else (0.85, 0.7, 0.35))
for k in range(22):
    arch_block(far, (-80 + k * 7.4, -78), (0, 1.0), 7.4, 15.0, 4.6, 6.0, 3.0, mat='M_stone_warm', tint=(0.95, 0.82, 0.62), n=8)
far.box((170, 1.4, 3.4), pos=(0, 15.0, -78 + 1.5), mat='M_stone_warm', tint=(0.9, 0.78, 0.6))
for (x, z) in ((-60, 50), (70, 30), (10, 95), (-85, -20), (88, -40)):
    far.cyl(5.0, 22, pos=(x, 0, z), mat='M_stone_warm', seg=14, tint=(0.95, 0.82, 0.62))
    far.lathe([(5.6, 0), (5.6, 0.8), (4.5, 2.5), (2.5, 4.5), (0.0, 5.5)], pos=(x, 22, z), mat='M_roof', seg=14, tint=(0.8, 0.65, 0.3))

# ------------------------------------------------------------------ assemblage
sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5}
sc.build(ao_samples=40, ao_dist=3.0, ao_floor=0.42)
sc.export(OUTDIR + '/arena_colosseum.glb')
