"""arena_frost.glb — forteresse de glace : dalles gelées + neige, piliers de cristal, stalactites, gradins enneigés, brasiers bleus."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_common import *

T = lambda n: TEXDIR + '/' + n
G.seed(202)
rng = np.random.default_rng(202)

defmat('M_ground', tex=T('frost_ground.png'), norm=T('frost_ground_n.png'), emit_tex=T('frost_ground_e.png'), emit_str=1.3, rough=0.55, uv=1,
       norm_str=1.0, spec=0.6)
defmat('M_stone', tex=T('frost_stone.png'), norm=T('frost_stone_n.png'), rough=0.85, uv=4.0)
defmat('M_stone_light', tex=T('frost_stone_light.png'), norm=T('frost_stone_light_n.png'), rough=0.85, uv=4.0)
defmat('M_marble', tex=T('frost_marble.png'), norm=T('frost_marble_n.png'), rough=0.5, uv=4.0, spec=0.6)
defmat('M_snow', tex=T('frost_snow.png'), norm=T('frost_snow_n.png'), rough=0.95, uv=4.0, spec=0.2)
defmat('M_ice', tex=T('frost_ice.png'), norm=T('frost_ice_n.png'), rough=0.18, uv=4.0, spec=0.9)
defmat('M_crystal', emit='#3aa8ff', emit_str=0.45, rough=0.1, spec=0.9)
defmat('M_gold', rough=0.3, metal=0.9)
defmat('M_bronze', tex=T('frost_metal.png'), norm=T('frost_metal_n.png'), rough=0.45, metal=0.8, uv=2.0)
defmat('M_cloth', tex=T('frost_cloth.png'), rough=0.9, uv=2.0, double=True)
defmat('M_wood', tex=T('frost_wood.png'), rough=0.85, uv=4.0)
defmat('M_crowd', rough=0.95, spec=0.2)
defmat('M_rock', tex=T('frost_rock.png'), norm=T('frost_rock_n.png'), rough=0.9, uv=10.0)
defmat('M_dark', rough=0.5, metal=0.6, spec=0.5)
defmat('M_flame', emit='#3fb4ff', emit_str=2.6, vcol=False, color='#3fb4ff')
defmat('M_glow', emit='#5ac8ff', emit_str=0.8, vcol=False, color='#5ac8ff')
defmat('M_roof', tex=T('frost_ice.png'), rough=0.3, uv=4.0)

BLUE = '#2f5f9e'
WHITE = '#e9f1fa'
SILVER = '#aebccd'
ICE = (0.8, 0.9, 1.0)
STT = (0.85, 0.93, 1.0)

sc = Scene('arena_frost')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
build_ground(sc, step=0.6)

# ------------------------------------------------------------------ murs
GATE_W = 6.8
skip = []
for sx in (1, -1):
    s0 = rr.s_nearest(26.0 * sx, 0.0)
    skip.append((s0 - GATE_W / 2, s0 + GATE_W / 2))
FACE_D = 0.36
build_walls(sc, rr, T=1.5, H=HW, face_d=FACE_D,
            mats=dict(face='M_stone_light', panel='M_stone', trim='M_stone_light', top='M_stone_light'),
            tints=dict(panel=(0.78, 0.9, 1.1), face=(1, 1, 1.02), trim=(1.0, 1.0, 1.05), top=(1, 1, 1.05)), skip=skip, panel_y=1.8)
walls = sc.part('Walls')
snow_cap(walls, rr, 0.0, 1.5, HW, skip=skip)
add_strip(walls, rr, [(FACE_D - 0.015, 1.8), (FACE_D - 0.015, 1.92)], 'M_ice', 'in', (0.7, 0.9, 1.1), skip, 4.0)
# givre le long du pied du mur
add_strip(walls, rr, [(FACE_D - 0.01, 0.62), (FACE_D - 0.01, 0.95), (FACE_D - 0.03, 1.2)], 'M_snow', 'in', (1, 1, 1), skip, 4.0)

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
pilasters_on_wall(dec, rr, pil, FACE_D, HW, 'M_marble', (0.9, 0.97, 1.1), cap_mat='M_stone_light', cap_tint=(0.95, 1.0, 1.1), w=0.74)

# stalactites le long de la corniche du mur
icicle_line(dec, rr, 0.12, HW - 0.35, 0.55, rng, lmin=0.2, lmax=0.85, rmin=0.03, rmax=0.07)
for sx in (1, -1):
    nxz = (float(sx), 0.0)
    pos = (26.0 * sx, 0.0)
    ow = 3.4
    arch_block(walls, pos, nxz, GATE_W, HW, ow, 0.0, 1.5, mat='M_stone_light', tint=(1, 1, 1.05), kind='gothic', glow_mat='M_glow')
    # dents de glace dans l'arche
    pts = []
    for k in range(7):
        t = k / 6.0
        th = math.radians(60) * (1 - t)
        lx = -(ow / 2 - ow * math.cos(th)) if False else (ow / 2 - ow * math.cos(math.radians(60) * (1 - t)))
        ly = ow * math.sin(math.radians(60) * (1 - t))
        for sgn_ in (-1, 1):
            wx, wz = local_to_world(pos, nxz, sgn_ * lx, 0.12)
            pts.append((wx, ly - 0.02, wz))
    icicles(dec, pts, rng, 0.3, 0.7, 0.05, 0.1)
    # cristaux d'entrée
    x1, z1 = local_to_world(pos, nxz, 0.0, 0.3)
    dec.crystal(0.35, 2.4, pos=(x1, 0, z1), mat='M_crystal', seed=3, tint=(0.4, 0.75, 1.0))

# ------------------------------------------------------------------ gradins
ROWS = 8
D0, TREAD, RISE, Y0 = 1.5, 0.95, 0.55, HW
tiers, dend, ytop = build_tiers(sc, rr, D0, Y0, ROWS, TREAD, RISE, 'M_snow', 'M_stone', tint_tread=(0.95, 0.98, 1.05),
                                tint_riser=(0.8, 0.9, 1.1), back=1.3)
D_ARC = dend + 1.3
solid_ring(sc, rr, 'Stands', D_ARC, D_ARC + 1.3, 0.0, ytop, 'M_stone', tint=(0.8, 0.9, 1.1), inner=False, top=False)
crowd_pal = ['#2a4a7a', '#3a6aa8', '#e8eef6', '#9fb4cc', '#5a6a7a', '#233556', '#7a5a4a', '#c0c8d4', '#b33a3a', '#4a8ac0', '#f2f6fb', '#6d7f96']
skin = ['#f4d9c4', '#ecc4a4', '#d9a98a', '#b98366', '#f8e2d2']
hair = ['#f2f6fb', '#c9d4e2', '#8a9bb0', '#4a5568', '#e6eef8', '#7a8a9e', '#2a3140']
BOX_X = 5.6


def in_box(px, pz):
    return pz < 0 and abs(px) < BOX_X and (-(pz + 16.0)) > 1.3 and (-(pz + 16.0)) < 6.4


cnt = crowd(sc.part('Stands'), rr, tiers, crowd_pal, skin, hair, spacing=1.0, skip=0.1, rng=rng, exclude=in_box)
print('spectateurs', cnt)

# ------------------------------------------------------------------ loge de givre (côté -Z)
zc = -(16.0 + 3.7)
ybase = Y0 + RISE * 3
zf, zb = -(16.0 + 1.8), -(16.0 + 5.7)
dec.box((BOX_X * 2, 0.5, 4.9), pos=(0, ybase - 0.45, zc), mat='M_stone_light', tint=(1, 1, 1.05), bev=0.05)
dec.box((BOX_X * 2 + 0.5, 0.18, 5.2), pos=(0, ybase + 0.03, zc), mat='M_marble', tint=(0.95, 1.0, 1.08), bev=0.04)
dec.box((BOX_X * 2 - 0.3, 0.05, 4.6), pos=(0, ybase + 0.2, zc), mat='M_cloth', tint=(0.15, 0.3, 0.6))
for xx in (-BOX_X + 0.5, -BOX_X / 3, BOX_X / 3, BOX_X - 0.5):
    for zz in (zf, zb):
        column(dec, (xx, zz), 0.36, 3.5, mat='M_marble', tint=(0.92, 0.98, 1.1), capital=True, seg=16, flutes=(8, 0.06), drums=2, base_h=0.25,
               shaft_ratio=0.76, cap_mat='M_stone_light', y0=ybase + 0.2)
yr = ybase + 3.7
dec.box((BOX_X * 2 + 0.8, 0.4, 5.4), pos=(0, yr, zc), mat='M_stone_light', tint=(0.95, 1.0, 1.1), bev=0.06)
roof = p_extrude_xy([(-3.0, 0), (3.0, 0), (0.0, 2.2)], -(BOX_X + 0.6), BOX_X + 0.6)
dec.add(roof, 'M_ice', pos=(0, yr + 0.4, zc), yaw=math.pi / 2, tint=(0.7, 0.88, 1.1))
snow = p_extrude_xy([(-3.1, 0), (3.1, 0), (0.0, 2.3)], -(BOX_X + 0.65), BOX_X + 0.65)
dec.add(snow, 'M_snow', pos=(0, yr + 0.48, zc), yaw=math.pi / 2, tint=(1, 1, 1.02), scale=(1, 0.18, 1) if False else 1.0) if False else None
icicle_pos = [(x, yr + 0.38, zf - 0.55) for x in np.linspace(-BOX_X - 0.4, BOX_X + 0.4, 18)]
icicles(dec, icicle_pos, rng, 0.3, 0.9, 0.04, 0.08)
for xx in (-BOX_X / 3 * 2, 0, BOX_X / 3 * 2):
    dec.add(p_banner(BOX_X * 0.55, 2.4, 3, 5, 0.1, 0.0)[:2], 'M_cloth', pos=(xx, yr - 0.1, zf - 0.1), tint=(0.1, 0.25, 0.55), yaw=math.pi)
dec.box((1.5, 1.1, 0.8), pos=(0, ybase + 0.2, zb + 0.3), mat='M_ice', tint=(0.7, 0.9, 1.1), bev=0.08)
dec.box((1.6, 2.2, 0.25), pos=(0, ybase + 0.2, zb + 0.75), mat='M_ice', tint=(0.7, 0.9, 1.1), bev=0.06)
for xx in (-BOX_X + 0.4, BOX_X - 0.4):
    brazier(dec, (xx, ybase + 0.2, zf + 0.5), h=0.8, r=0.35, tint=(0.4, 0.45, 0.55))
sc.empty('Light_05', 0.0, ybase + 2.0, zc)

# ------------------------------------------------------------------ façade gothique + stalactites
Yp = ytop
ARC_H = 6.2
arcade_ring(sc, rr, 'Decor', D_ARC, Yp, ARC_H, bay=3.7, open_ratio=0.62, spring=2.3, depth=1.3, mat='M_stone_light', tint=(0.92, 0.98, 1.1),
            glow_mat='M_glow', kind='gothic')
solid_ring(sc, rr, 'Decor', D_ARC - 0.15, D_ARC + 1.6, Yp + ARC_H, Yp + ARC_H + 0.5, 'M_stone_light', tint=(0.95, 1.0, 1.1), inner=True, top=True, outer=True)
snow_cap(dec, rr, D_ARC - 0.15, D_ARC + 1.6, Yp + ARC_H + 0.5, puff=0.45)
add_strip(dec, rr, [(D_ARC - 0.2, Yp + ARC_H + 0.18), (D_ARC - 0.2, Yp + ARC_H + 0.3)], 'M_ice', 'in', (0.7, 0.9, 1.1), None, 4.0)
# grands stalactites sous la corniche
Pst, Nst, Tst, sst = rr.along(0.85, D_ARC - 0.12, offset=0.2)
posn = [(p[0], Yp + ARC_H - 0.02, p[1]) for p in Pst]
icicles(dec, posn, rng, 0.5, 2.6, 0.07, 0.17, tint=(0.8, 0.92, 1.0))

# pinacles + brasiers bleus sur le sommet
P2, N2, T2, s2 = rr.along(7.4, D_ARC + 0.8, offset=1.0)
ytop_arc = Yp + ARC_H + 0.5
for i in range(len(P2)):
    x, z = P2[i]
    if i % 2 == 0:
        dec.cone(0.5, 3.2, pos=(x, ytop_arc + 0.3, z), mat='M_ice', seg=6, tint=(0.7, 0.88, 1.1))
        dec.box((0.9, 0.3, 0.9), pos=(x, ytop_arc, z), mat='M_stone_light', tint=(0.95, 1, 1.1), bev=0.04)
    else:
        brazier(dec, (x, ytop_arc + 0.3, z), h=1.0, r=0.55, tint=(0.4, 0.45, 0.55), flame_h=1.2)

# tours de cristal aux 4 coins
li = 1
for sx in (-1, 1):
    for sz in (-1, 1):
        a = math.radians(45)
        px, pz = sx * (21.0 + (5 + 8.7) * math.cos(a)), sz * (11.0 + (5 + 8.7) * math.sin(a))
        dec.lathe([(1.4, Yp), (1.4, Yp + 0.6), (1.1, Yp + 0.9)], pos=(px, 0, pz), mat='M_stone_light', seg=10, tint=(0.95, 1, 1.1))
        crystal_cluster(dec, px, pz, 1.2, 8.5, rng, n=5, y0=Yp + 0.9, seed=li * 11)
        sc.empty(f'Light_{li:02d}', px, Yp + 6.0, pz)
        li += 1

# bannières
bi = 1
for x in (-21, -15, -9, -3, 3, 9, 15, 21):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, -(16 + 0.2)), math.pi, 1.5, 2.0, BLUE, SILVER, WHITE, phase=bi, mat='M_cloth', rod_tint=(0.7, 0.78, 0.9))
    bi += 1
for x in (-18, -6, 6, 18):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, 16 + 0.2), 0.0, 1.5, 2.0, '#1f3f70', SILVER, WHITE, phase=bi, mat='M_cloth', rod_tint=(0.7, 0.78, 0.9))
    bi += 1


def frost_sconce(md, mf, Fp, n, arm):
    sconce(md, mf, Fp, n, arm, tint=(0.75, 0.82, 0.92))


torches(sc, rr, y=2.2, sconce_fn=frost_sconce)

# ------------------------------------------------------------------ obstacles : piliers de cristal
specs = [dict(h=3.9, n=6), dict(h=3.4, n=5), dict(h=3.7, n=7), dict(h=3.9, n=6), dict(h=3.2, n=5), dict(h=3.6, n=6)]
for i, sp in enumerate(specs):
    mb, o = obstacle_part(sc, i)
    r = o['r']
    x, z = o['x'], o['z']
    # socle de roche gelée + neige
    mb.lathe([(r, 0), (r, 0.18), (r * 0.9, 0.42), (r * 0.7, 0.55), (r * 0.5, 0.58)], pos=(x, 0, z), mat='M_rock', seg=14, tint=(0.75, 0.85, 1.0), jitter=0.06)
    mb.lathe([(r * 0.98, 0.12), (r * 0.92, 0.3), (r * 0.78, 0.5), (r * 0.5, 0.62), (0.0, 0.66)], pos=(x, 0, z), mat='M_snow', seg=14, tint=(1, 1, 1.02), jitter=0.05)
    crystal_cluster(mb, x, z, r, sp['h'], rng, n=sp['n'], y0=0.5, seed=i * 7 + 1)
    # éclats au sol dans le rayon
    for k in range(4):
        a = rng.uniform(0, 2 * math.pi)
        rho = r * rng.uniform(0.75, 0.9)
        mb.crystal(0.1, rng.uniform(0.3, 0.6), pos=(x + rho * math.cos(a), 0.45, z + rho * math.sin(a)), mat='M_crystal', seed=k, seg=5, tint=(0.5, 0.8, 1.0), skew=0.3)

# ------------------------------------------------------------------ décor lointain
far = dec
far.add(p_cyl(160, 0.2, 40, cap0=False, cap1=True), 'M_snow', pos=(0, -0.3, 0), tint=(0.85, 0.92, 1.05))
for i in range(28):
    a = 2 * math.pi * i / 28 + rng.uniform(-0.1, 0.1)
    R = rng.uniform(95, 140)
    w = rng.uniform(40, 80)
    h = rng.uniform(25, 55)
    mound(far, (R * math.cos(a), -2, R * math.sin(a)), (w, h, w * 0.8), seed=i, tint=(0.75, 0.85, 1.0), mat='M_rock', rough=0.3,
          vf=lambda V, hh=h: np.where(V[:, 1] > hh * 0.55, 1.6, 0.9)[:, None] * np.array([1.0, 1.05, 1.15])[None, :] * (0.8 + 0.5 * np.clip(V[:, 1] / hh, 0, 1))[:, None])
# spires de cristal lointains
for i in range(40):
    a = rng.uniform(0, 2 * math.pi)
    R = rng.uniform(55, 100)
    x, z = R * math.cos(a), R * math.sin(a)
    if float(rr.sdf(np.array(x), np.array(z))) < 24:
        continue
    far.crystal(rng.uniform(1.5, 3.5), rng.uniform(10, 38), pos=(x, 0, z), mat='M_crystal', seed=i, tint=(0.35, 0.7, 1.0), skew=rng.uniform(-0.25, 0.25),
                yaw=rng.uniform(0, 3), tip=0.3)
# tours/remparts de glace
for i in range(46):
    a = rng.uniform(0, 2 * math.pi)
    R = rng.uniform(52, 90)
    x, z = R * math.cos(a), R * math.sin(a)
    if float(rr.sdf(np.array(x), np.array(z))) < 22:
        continue
    w, d = rng.uniform(3.5, 8), rng.uniform(3.5, 8)
    h = rng.uniform(6, 22)
    building(far, (x, 0, z), w, d, h, yaw=rng.uniform(0, 3.14), mat='M_stone_light', tint=(0.85, 0.93, 1.08), roof='cone', roof_tint=(0.6, 0.85, 1.1))

sc.ao_opts = {'Ground': 0.72, 'Decor': 0.5}
sc.build(ao_samples=40, ao_dist=3.0, ao_floor=0.45)
sc.export(OUTDIR + '/arena_frost.glb')
