"""arena_forge.glb — forge volcanique : basalte veiné de lave, enclumes et piliers d'obsidienne, chaînes, soufflets, gradins de roche rouge, cheminées."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_common import *

T = lambda n: TEXDIR + '/' + n
G.seed(303)
rng = np.random.default_rng(303)

defmat('M_ground', tex=T('forge_ground.png'), norm=T('forge_ground_n.png'), emit_tex=T('forge_ground_e.png'), emit_str=1.6, rough=0.75, uv=1, norm_str=1.0, spec=0.4)
defmat('M_stone', tex=T('forge_stone.png'), norm=T('forge_stone_n.png'), rough=0.85, uv=4.0)
defmat('M_metal', tex=T('forge_metal.png'), norm=T('forge_metal_n.png'), rough=0.55, metal=0.7, uv=2.0)
defmat('M_iron', tex=T('forge_iron.png'), norm=T('forge_iron_n.png'), rough=0.5, metal=0.6, uv=2.0)
defmat('M_bronze', tex=T('forge_iron.png'), norm=T('forge_iron_n.png'), rough=0.45, metal=0.65, uv=2.0)
defmat('M_gold', rough=0.35, metal=0.9)
defmat('M_rock', tex=T('forge_rock.png'), norm=T('forge_rock_n.png'), rough=0.92, uv=5.0)
defmat('M_basalt', tex=T('forge_basalt.png'), norm=T('forge_basalt_n.png'), rough=0.9, uv=6.0)
defmat('M_cloth', tex=T('forge_cloth.png'), rough=0.95, uv=2.0, double=True)
defmat('M_wood', tex=T('forge_wood.png'), rough=0.9, uv=4.0)
defmat('M_dirt', tex=T('forge_soot.png'), rough=1.0, uv=10.0)
defmat('M_crowd', rough=0.9, spec=0.2)
defmat('M_dark', rough=0.5, metal=0.6)
defmat('M_obsidian', rough=0.22, metal=0.3, spec=1.0)
defmat('M_flame', emit='#ff7a1c', emit_str=2.6, vcol=False, color='#ff7a1c')
defmat('M_glow', emit='#ff6a1a', emit_str=1.3, vcol=False, color='#ff6a1a')
defmat('M_lava', emit='#ff5a12', emit_str=2.4, vcol=False, color='#ff5a12')
defmat('M_roof', tex=T('forge_metal.png'), rough=0.6, metal=0.5, uv=2.0)

IRONT = (0.62, 0.6, 0.62)
DARK = (0.45, 0.42, 0.42)
RUSTT = (1.0, 0.75, 0.6)

sc = Scene('arena_forge')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
build_ground(sc, step=0.6)

GATE_W = 6.8
skip = []
for sx in (1, -1):
    s0 = rr.s_nearest(26.0 * sx, 0.0)
    skip.append((s0 - GATE_W / 2, s0 + GATE_W / 2))
FACE_D = 0.36
build_walls(sc, rr, T=1.5, H=HW, face_d=FACE_D,
            mats=dict(face='M_stone', panel='M_metal', trim='M_iron', top='M_iron'),
            tints=dict(panel=(0.8, 0.72, 0.68), face=(0.9, 0.85, 0.82), trim=(0.7, 0.68, 0.7), top=(0.65, 0.62, 0.62)), skip=skip, panel_y=1.8)
walls = sc.part('Walls')
# fentes de fournaise lumineuses discontinues au pied du mur
L = rr.length()
glow_skip = list(skip)
seg_len, period = 2.6, 5.2
s_ = 0.0
while s_ < L:
    glow_skip.append((s_ + seg_len, s_ + period))
    s_ += period
add_strip(walls, rr, [(FACE_D - 0.02, 0.78), (FACE_D - 0.02, 0.9)], 'M_lava', 'in', (1, 1, 1), glow_skip, 4.0)
# bande de rivets (ligne de métal)
add_strip(walls, rr, [(FACE_D - 0.02, 1.8), (FACE_D - 0.02, 1.95)], 'M_iron', 'in', (0.7, 0.68, 0.7), skip, 4.0)
# merlons massifs au sommet
Pm, Nm, Tm, sm = rr.along(1.9, 0.75, offset=0.3)
for i in range(len(Pm)):
    s_here = rr.s_nearest(Pm[i][0], Pm[i][1])
    if any(a - 0.8 <= s_here <= b + 0.8 for a, b in skip):
        continue
    yaw = yaw_of(Nm[i][0], Nm[i][1])
    walls.box((1.1, 0.7, 0.9), pos=(Pm[i][0], HW, Pm[i][1]), mat='M_stone', tint=(0.7, 0.66, 0.64), yaw=yaw, top=(0.95, 0.75), jit=0.08)

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
pilasters_on_wall(dec, rr, pil, FACE_D, HW, 'M_iron', (0.6, 0.58, 0.6), cap_mat='M_iron', cap_tint=(0.75, 0.55, 0.4), w=0.7)

for sx in (1, -1):
    nxz = (float(sx), 0.0)
    pos = (26.0 * sx, 0.0)
    yaw = yaw_of(*nxz)
    ow = 4.2
    arch_block(walls, pos, nxz, GATE_W, HW, ow, 0.7, 1.5, mat='M_stone', tint=(0.75, 0.7, 0.68), glow_mat='M_glow')
    # grille de fournaise
    for k in range(-4, 5):
        x1, z1 = local_to_world(pos, nxz, k * 0.47, 0.45)
        dec.box((0.09, 2.7 if abs(k) < 4 else 2.0, 0.09), pos=(x1, 0, z1), mat='M_iron', tint=DARK)
    x1, z1 = local_to_world(pos, nxz, 0, 0.45)
    dec.add(p_box(4.3, 0.12, 0.12), 'M_iron', pos=(x1, 0.9, z1), yaw=yaw, tint=DARK)
    dec.add(p_box(4.3, 0.12, 0.12), 'M_iron', pos=(x1, 1.9, z1), yaw=yaw, tint=DARK)
    # gueule : dents d'acier au sommet de l'arche
    n = 9
    for k in range(n + 1):
        a = math.pi * k / n
        lx, ly = 2.1 * math.cos(a), 0.7 + 2.1 * math.sin(a)
        wx, wz = local_to_world(pos, nxz, lx, 0.1)
        dec.add(p_lathe([(0.1, 0), (0.0, -0.45)], 4, True, False), 'M_iron', pos=(wx, ly + 0.02, wz), tint=DARK)

# ------------------------------------------------------------------ gradins
ROWS = 8
D0, TREAD, RISE, Y0 = 1.5, 0.95, 0.55, HW
tiers, dend, ytop = build_tiers(sc, rr, D0, Y0, ROWS, TREAD, RISE, 'M_rock', 'M_rock', tint_tread=(0.85, 0.62, 0.52),
                                tint_riser=(0.6, 0.42, 0.36), back=1.3)
D_ARC = dend + 1.3
solid_ring(sc, rr, 'Stands', D_ARC, D_ARC + 1.3, 0.0, ytop, 'M_rock', tint=(0.55, 0.4, 0.34), inner=False, top=False)
crowd_pal = ['#5a3a28', '#7a4a2a', '#3a2a24', '#8a2a1a', '#4a3a3a', '#a06a30', '#6a5a4a', '#c05a1a', '#2e2a2a', '#7a2a2a']
skin = ['#d9a07a', '#c27a54', '#a85a3a', '#8a4a30', '#e8b894']
hair = ['#6a6a72', '#8a8a92', '#b87333', '#3a3a40', '#d4a02a', '#5a3a1a', '#1a1412']
BOX_X = 5.6


def in_box(px, pz):
    return pz < 0 and abs(px) < BOX_X and (-(pz + 16.0)) > 1.3 and (-(pz + 16.0)) < 6.4


cnt = crowd(sc.part('Stands'), rr, tiers, crowd_pal, skin, hair, spacing=1.0, skip=0.1, rng=rng, exclude=in_box)
print('spectateurs', cnt)

# ------------------------------------------------------------------ loge (forgeron-chef) côté -Z
zc = -(16.0 + 3.7)
ybase = Y0 + RISE * 3
zf, zb = -(16.0 + 1.8), -(16.0 + 5.7)
dec.box((BOX_X * 2, 0.5, 4.9), pos=(0, ybase - 0.45, zc), mat='M_stone', tint=(0.7, 0.66, 0.64), bev=0.05)
dec.box((BOX_X * 2 + 0.5, 0.18, 5.2), pos=(0, ybase + 0.03, zc), mat='M_iron', tint=(0.6, 0.58, 0.6), bev=0.04)
dec.box((BOX_X * 2 - 0.3, 0.05, 4.6), pos=(0, ybase + 0.2, zc), mat='M_cloth', tint=(0.5, 0.1, 0.06))
for xx in (-BOX_X + 0.5, -BOX_X / 3, BOX_X / 3, BOX_X - 0.5):
    for zz in (zf, zb):
        dec.box((0.5, 3.6, 0.5), pos=(xx, ybase + 0.2, zz), mat='M_iron', tint=(0.55, 0.52, 0.55), top=(0.38, 0.38), bev=0.03)
yr = ybase + 3.8
dec.box((BOX_X * 2 + 0.8, 0.5, 5.4), pos=(0, yr, zc), mat='M_iron', tint=(0.55, 0.52, 0.55), bev=0.05)
dec.add(p_extrude_xy([(-3.0, 0), (3.0, 0), (0.0, 1.6)], -(BOX_X + 0.6), BOX_X + 0.6), 'M_roof', pos=(0, yr + 0.5, zc), yaw=math.pi / 2, tint=(0.5, 0.42, 0.4))
for xx in (-BOX_X / 3 * 2, 0, BOX_X / 3 * 2):
    dec.add(p_banner(BOX_X * 0.55, 2.4, 3, 5, 0.1, 0.0)[:2], 'M_cloth', pos=(xx, yr - 0.1, zf - 0.1), tint=(0.55, 0.08, 0.05), yaw=math.pi)
dec.box((1.6, 1.1, 0.9), pos=(0, ybase + 0.2, zb + 0.3), mat='M_iron', tint=DARK, bev=0.08)
dec.box((1.7, 2.3, 0.3), pos=(0, ybase + 0.2, zb + 0.75), mat='M_iron', tint=DARK, bev=0.06)
for xx in (-BOX_X + 0.4, BOX_X - 0.4):
    brazier(dec, (xx, ybase + 0.2, zf + 0.5), h=0.8, r=0.35, tint=(0.25, 0.22, 0.22))
sc.empty('Light_05', 0.0, ybase + 2.0, zc)

# ------------------------------------------------------------------ façade industrielle
Yp = ytop
ARC_H = 5.8
arcade_ring(sc, rr, 'Decor', D_ARC, Yp, ARC_H, bay=3.7, open_ratio=0.62, spring=2.9, depth=1.3, mat='M_stone', tint=(0.7, 0.62, 0.58),
            glow_mat='M_glow', glow_every=2)
solid_ring(sc, rr, 'Decor', D_ARC - 0.15, D_ARC + 1.6, Yp + ARC_H, Yp + ARC_H + 0.6, 'M_iron', tint=(0.6, 0.57, 0.58), inner=True, top=True, outer=True)
add_strip(dec, rr, [(D_ARC - 0.2, Yp + ARC_H + 0.2), (D_ARC - 0.2, Yp + ARC_H + 0.36)], 'M_lava', 'in', (1, 1, 1), None, 4.0)
add_strip(dec, rr, [(D_ARC + 1.5, Yp + ARC_H + 0.6), (D_ARC + 1.5, Yp + ARC_H + 1.4)], 'M_stone', 'in', (0.6, 0.55, 0.52), None, 4.0)
add_strip(dec, rr, [(D_ARC + 1.5, Yp + ARC_H + 1.4), (D_ARC + 1.7, Yp + ARC_H + 1.4)], 'M_stone', 'up', (0.6, 0.55, 0.52), None, 4.0)

# poteaux de fer + chaînes + brasiers
ytop_arc = Yp + ARC_H + 0.6
P2, N2, T2, s2 = rr.along(7.4, D_ARC + 0.9, offset=1.0)
posts = []
for i in range(len(P2)):
    x, z = P2[i]
    yaw = yaw_of(N2[i][0], N2[i][1])
    dec.box((0.45, 6.0, 0.45), pos=(x, ytop_arc, z), mat='M_iron', tint=DARK, top=(0.3, 0.3), yaw=yaw)
    dec.box((0.9, 0.3, 0.9), pos=(x, ytop_arc + 5.9, z), mat='M_iron', tint=DARK, yaw=yaw)
    brazier(dec, (x, ytop_arc + 6.2, z), h=0.35, r=0.55, tint=(0.25, 0.22, 0.22), flame_h=1.0)
    posts.append((x, ytop_arc + 5.2, z))


def chain(mb, p0, p1, sag=1.6, link=0.36):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = np.linalg.norm(p1 - p0)
    n = max(4, int(d / link))
    pts = []
    for k in range(n + 1):
        t = k / n
        p = p0 + (p1 - p0) * t
        p[1] -= sag * 4 * t * (1 - t)
        pts.append(p)
    pts = np.array(pts)
    mid = (pts[:-1] + pts[1:]) / 2
    dv = pts[1:] - pts[:-1]
    yaw = np.arctan2(dv[:, 0], dv[:, 2])
    pitch = -np.arctan2(dv[:, 1], np.hypot(dv[:, 0], dv[:, 2]))
    roll = np.array([0 if k % 2 == 0 else math.pi / 2 for k in range(len(mid))])
    tpl = p_box(0.07, 0.07, 0.4)
    mb.add_many(tpl, 'M_iron', mid, yaw=yaw, pitch=pitch, roll=roll, tint=np.tile(s2l((0.3, 0.3, 0.32)), (len(mid), 1)))


for i in range(len(posts)):
    a, b = posts[i], posts[(i + 1) % len(posts)]
    if np.linalg.norm(np.array(a) - np.array(b)) < 12:
        chain(dec, a, b, sag=1.8)
        # crochet central
        mx, mz = (a[0] + b[0]) / 2, (a[2] + b[2]) / 2

# cheminées
chim = 0
Pc, Nc, Tc, sc_ = rr.along(15.5, D_ARC + 0.6, offset=4.0)
for i in range(len(Pc)):
    x, z = Pc[i]
    h = rng.uniform(9, 15)
    dec.lathe([(1.5, ytop_arc), (1.3, ytop_arc + h * 0.5), (1.0, ytop_arc + h), (1.15, ytop_arc + h + 0.15), (0.9, ytop_arc + h + 0.18)], pos=(x, 0, z), mat='M_stone',
              seg=10, tint=(0.55, 0.48, 0.45), cap1=False)
    dec.lathe([(1.15, 0), (1.15, 0.5), (0.95, 0.5)], pos=(x, ytop_arc + h * 0.6, z), mat='M_iron', seg=10, tint=DARK, cap0=False, cap1=False)
    dec.cyl(0.92, 0.05, pos=(x, ytop_arc + h + 0.05, z), mat='M_lava', seg=10, vcol=False) if False else dec.add(p_cyl(0.92, 0.05, 10), 'M_lava', pos=(x, ytop_arc + h + 0.05, z))
    sc.empty(f'Light_{chim + 1:02d}', x, ytop_arc + h + 0.8, z) if chim < 4 else None
    chim += 1


# soufflets monumentaux (promenoir, nez tourné vers l'arène)
def bellows(mb, x, z, nx, nz, s=1.0):
    yaw = yaw_of(-nx, -nz)  # +Z local vers l'arène
    y0 = Yp
    mb.box((3.0 * s, 0.5, 2.6 * s), pos=(x, y0, z), mat='M_stone', tint=(0.55, 0.5, 0.48), yaw=yaw, bev=0.05)
    # corps accordéon : coques trapézoïdales empilées (tissu/cuir)
    for k in range(7):
        t = k / 6.0
        h = 0.34 * s
        yk = y0 + 0.5 + k * h * 1.05
        w = (2.4 - 0.2 * math.sin(t * math.pi)) * s
        mb.add(p_box(w, h, 2.0 * s, top=(w * 0.92, 1.85 * s)), 'M_cloth', pos=(x, yk, z), yaw=yaw, tint=(0.55, 0.38, 0.26), bev=0.0)
        mb.add(p_box(w + 0.12, 0.06, 2.1 * s), 'M_wood', pos=(x, yk + h, z), yaw=yaw, tint=(0.4, 0.3, 0.2))
    # tuyère vers l'arène
    cx, cz = x - nx * 0.0, z
    mb.add(p_cone(0.35 * s, 1.4 * s, 8), 'M_iron', pos=(x + (-nx) * 1.0 * s, y0 + 0.9, z + (-nz) * 1.0 * s), yaw=yaw, pitch=math.pi / 2 + 0.0, tint=DARK)
    # levier
    mb.add(p_box(0.12, 2.6 * s, 0.12), 'M_wood', pos=(x + nx * 1.1, y0 + 0.6, z + nz * 1.1), yaw=yaw, roll=0.5, tint=(0.4, 0.3, 0.2))
    # braise sous la tuyère
    mb.add(p_box(0.8, 0.12, 0.8), 'M_lava', pos=(x + (-nx) * 1.9, y0 + 0.5, z + (-nz) * 1.9), yaw=yaw)


for (px, pz) in ((-14, -(16 + 10.4)), (14, -(16 + 10.4)), (-14, 16 + 10.4), (14, 16 + 10.4), (-34.0, 0), (34.0, 0)):
    s_ = rr.s_nearest(px, pz)
    Pn, nn = rr.at_base(s_, 10.1)
    bellows(dec, Pn[0], Pn[1], nn[0], nn[1])

# bannières
bi = 1
for x in (-21, -15, -9, -3, 3, 9, 15, 21):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, -(16 + 0.2)), math.pi, 1.5, 2.0, '#7a1a10', '#d98a2a', '#ffb040', phase=bi, mat='M_cloth', rod_tint=(0.4, 0.38, 0.4), rod_mat='M_iron')
    bi += 1
for x in (-18, -6, 6, 18):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, 16 + 0.2), 0.0, 1.5, 2.0, '#3a1612', '#d98a2a', '#ffb040', phase=bi, mat='M_cloth', rod_tint=(0.4, 0.38, 0.4), rod_mat='M_iron')
    bi += 1


def forge_sconce(md, mf, Fp, n, arm):
    sconce(md, mf, Fp, n, arm, tint=(0.35, 0.33, 0.35))


torches(sc, rr, y=2.2, sconce_fn=forge_sconce)

# ------------------------------------------------------------------ obstacles : enclumes (0,2,4) et piliers d'obsidienne (1,3,5)
def anvil(mb, x, z, r, s=0.95, yaw=0.0):
    ph = 1.5
    mb.lathe([(r, 0), (r, ph - 0.25), (r * 0.95, ph - 0.1), (r * 0.82, ph)], pos=(x, 0, z), mat='M_stone', seg=18, tint=(0.6, 0.55, 0.52), jitter=0.0)
    for yb in (0.3, 0.85):
        mb.lathe([(r * 1.0, 0), (r * 1.015, 0.1)], pos=(x, yb, z), mat='M_iron', seg=18, tint=DARK, cap0=False, cap1=False)
    yb = ph
    mb.box((1.9 * s, 0.35 * s, 1.1 * s), pos=(x, yb, z), mat='M_iron', tint=(0.5, 0.5, 0.55), yaw=yaw, bev=0.05, top=(1.6 * s, 0.95 * s))
    mb.box((1.15 * s, 0.75 * s, 0.7 * s), pos=(x, yb + 0.35 * s, z), mat='M_iron', tint=(0.5, 0.5, 0.55), yaw=yaw, bev=0.04, top=(0.9 * s, 0.62 * s))
    mb.box((2.5 * s, 0.5 * s, 1.0 * s), pos=(x, yb + 1.1 * s, z), mat='M_iron', tint=(0.55, 0.55, 0.6), yaw=yaw, bev=0.06)
    mb.add(p_lathe([(0.5 * s, 0), (0.12 * s, 1.35 * s)], 8, True, True), 'M_iron', pos=(x + math.cos(yaw) * 1.2 * s, yb + 1.35 * s, z - math.sin(yaw) * 1.2 * s),
           yaw=yaw, roll=-math.pi / 2, tint=(0.55, 0.55, 0.6))
    mb.box((0.7 * s, 0.3 * s, 0.9 * s), pos=(x - math.cos(yaw) * 1.2 * s, yb + 1.1 * s, z + math.sin(yaw) * 1.2 * s), mat='M_iron', tint=(0.5, 0.5, 0.55), yaw=yaw, bev=0.04)
    mb.add(p_box(1.3 * s, 0.04, 0.45 * s), 'M_lava', pos=(x - 0.1 * s, yb + 1.6 * s, z), yaw=yaw)


def obsidian(mb, x, z, r, h, seed):
    # socle hexagonal puis flèche principale + éclats inclinés (tout reste dans le rayon r à la base)
    V, F = p_crystal(r * 0.92, 0.5, 6, 0.0, seed, 0.0, r, 0.0)
    mb.add((V, F), 'M_basalt', pos=(x, 0, z), tint=(0.5, 0.45, 0.45), yaw=0.2)
    V, F = p_crystal(r * 0.5, h, 6, 0.12, seed + 1, 0.0, r * 0.84, 0.0)
    mb.add((V, F), 'M_obsidian', pos=(x, 0.45, z), tint=(0.2, 0.17, 0.26), bev=0.05, yaw=0.2)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.4
        br = r * 0.34
        rho = r - br - 0.02
        hh = h * rng.uniform(0.35, 0.65)
        V, F = p_crystal(br * 0.35, hh, 6, 0.3, seed + k + 3, 0.5, br, 0.0)
        mb.add((V, F), 'M_obsidian', pos=(x + rho * math.cos(a), 0.4, z + rho * math.sin(a)), yaw=-a, tint=(0.22, 0.19, 0.28), bev=0.03)
    # joint de magma entre socle et flèche + veines verticales
    mb.add(p_lathe([(r * 0.86, 0), (r * 0.875, 0.12)], 6, False, False, phase=0.0), 'M_lava', pos=(x, 0.4, z), yaw=0.2)
    for k in range(3):
        a = 0.2 + k * 2 * math.pi / 3 + math.pi / 6
        rv = r * 0.84 * 0.62
        mb.add(p_box(0.13, h * 0.55, 0.05), 'M_lava', pos=(x + rv * math.cos(a), 0.7, z + rv * math.sin(a)), yaw=-a + math.pi / 2, tint=(1, 1, 1))


heights = [3.4, 3.8, 3.2, 3.5, 3.0, 3.3]
for i in range(6):
    mb, o = obstacle_part(sc, i)
    if i in (0, 2, 4):
        anvil(mb, o['x'], o['z'], o['r'], s=0.95 if o['r'] > 1.3 else 0.85, yaw=rng.uniform(-0.5, 0.5))
    else:
        obsidian(mb, o['x'], o['z'], o['r'], 3.9 if o['r'] > 1.3 else 3.6, i)

# ------------------------------------------------------------------ décor lointain
far = dec
far.add(p_cyl(160, 0.2, 40, cap0=False, cap1=True), 'M_dirt', pos=(0, -0.3, 0), tint=(0.8, 0.7, 0.65))
for i in range(28):
    a = 2 * math.pi * i / 28 + rng.uniform(-0.1, 0.1)
    R = rng.uniform(95, 140)
    w = rng.uniform(40, 80)
    h = rng.uniform(20, 55)
    mound(far, (R * math.cos(a), -2, R * math.sin(a)), (w, h, w * 0.8), seed=i, tint=(0.6, 0.35, 0.28), mat='M_rock', rough=0.3,
          vf=vgrad(0, h, 0.5, 1.2))
# volcan lointain avec cratère
vx, vz = 0, -125
far.add(p_lathe([(55, -2), (40, 14), (24, 38), (12, 62), (9.5, 66), (8, 64), (0, 56)], 20, False, False), 'M_rock', pos=(vx, 0, vz), tint=(0.45, 0.3, 0.26))
far.add(p_lathe([(8.2, 0.0), (0.0, 0.02)], 20, False, True), 'M_lava', pos=(vx, 64.5, vz))
for k in range(6):
    a = k * math.pi / 3 + 0.3
    far.add(p_box(1.8, 40, 0.5), 'M_lava', pos=(vx + 20 * math.cos(a), 20, vz + 20 * math.sin(a) + 0), yaw=-a, pitch=0.0, roll=0.0, tint=(1, 1, 1)) if False else None
# rivières de lave au sol
for k in range(10):
    a = rng.uniform(0, 2 * math.pi)
    R0 = rng.uniform(58, 90)
    pts = []
    for j in range(12):
        aa = a + j * 0.06 * rng.choice([-1, 1]) * 0 + j * 0.05
        RR_ = R0 + 6 * math.sin(j * 0.9 + k)
        pts.append((RR_ * math.cos(aa), RR_ * math.sin(aa)))
    for j in range(len(pts) - 1):
        (x0, z0), (x1, z1) = pts[j], pts[j + 1]
        if float(rr.sdf(np.array(x0), np.array(z0))) < 22:
            continue
        L_ = math.hypot(x1 - x0, z1 - z0)
        far.add(p_box(L_ + 0.4, 0.05, rng.uniform(2.0, 3.6)), 'M_lava', pos=((x0 + x1) / 2, -0.12, (z0 + z1) / 2), yaw=math.atan2(-(z1 - z0), (x1 - x0)))
for i in range(60):
    a = rng.uniform(0, 2 * math.pi)
    R = rng.uniform(52, 92)
    x, z = R * math.cos(a), R * math.sin(a)
    if float(rr.sdf(np.array(x), np.array(z))) < 22:
        continue
    w, d = rng.uniform(3.5, 8), rng.uniform(3.5, 8)
    h = rng.uniform(5, 18)
    building(far, (x, 0, z), w, d, h, yaw=rng.uniform(0, 3.14), mat='M_stone', tint=(0.5, 0.45, 0.43), roof='gable', roof_tint=(0.3, 0.25, 0.25))
    # lueur de fenêtre
    far.add(p_box(w * 0.6, 0.6, 0.1), 'M_glow', pos=(x, h * 0.5, z), yaw=0.0)

sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5}
sc.build(ao_samples=40, ao_dist=3.0, ao_floor=0.45)
sc.export(OUTDIR + '/arena_forge.glb')
