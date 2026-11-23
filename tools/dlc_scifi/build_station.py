"""arena_station.glb — « Station Orbitale » : pont d'une station spatiale rétro-industrielle, baie vitrée sur la Terre et les étoiles,
panneaux de tôle, tuyaux, caillebotis, réservoirs. Palette : acier usé, béton/crème, rouille, laiton, verre fumé, petites lampes orange/teal."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_lib import *

G.seed(8101)
rng = np.random.default_rng(8101)

defmat('M_ground', tex=T('station_ground.jpg'), norm=T('station_ground_n.png'), emit_tex=T('station_ground_e.png'), emit_str=1.5, rough=0.62, metal=0.35, uv=1, spec=0.5)
defmat('M_cream', tex=T('station_cream.jpg'), norm=T('station_cream_n.jpg'), rough=0.6, metal=0.25, uv=2.0)
defmat('M_steel', tex=T('station_steel.jpg'), norm=T('station_steel_n.jpg'), rough=0.5, metal=0.6, uv=2.0)
defmat('M_dark', tex=T('station_dark.jpg'), norm=T('station_dark_n.jpg'), rough=0.5, metal=0.6, uv=2.0)
defmat('M_hazard', tex=T('station_hazard.jpg'), rough=0.6, metal=0.2, uv=1.0)
defmat('M_grate', tex=T('station_grate.jpg'), norm=T('station_grate_n.jpg'), rough=0.55, metal=0.6, uv=1.0)
defmat('M_cloth', tex=T('station_cloth.jpg'), rough=0.9, uv=2.0, double=True)
defmat('M_brass', rough=0.35, metal=0.85)
defmat('M_earth', tex=T('station_earth.jpg'), emit_tex=T('station_earth.jpg'), emit_str=0.28, rough=0.7, vcol=False, uv=1.0)
defmat('M_atmo', emit='#5aa8ff', emit_str=0.9, vcol=False, color='#5aa8ff')
defmat('M_star', emit='#ffffff', emit_str=3.0, vcol=False, color='#ffffff')
defmat('M_lamp_o', emit='#ff9030', emit_str=2.6, vcol=False, color='#ff9030')
defmat('M_lamp_t', emit='#40e0d0', emit_str=2.0, vcol=False, color='#40e0d0')
defmat('M_glass', emit='#2a6a78', emit_str=0.55, rough=0.15, metal=0.2, spec=1.0)
defmat('M_panel', rough=0.35, metal=0.4, spec=0.8)

sc = Scene('arena_station')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
walls = sc.part('Walls')
gal = sc.part('Gallery')
build_ground(sc, step=1.0)

# ------------------------------------------------------------------ mur d'enceinte + sas aux extrémités
GATE_W = 6.8
skip = []
for sx in (1, -1):
    s0 = rr.s_nearest(26.0 * sx, 0.0)
    skip.append((s0 - GATE_W / 2, s0 + GATE_W / 2))
FACE_D = 0.36
build_walls(sc, rr, T=1.5, H=HW, face_d=FACE_D, mats=dict(face='M_cream', panel='M_dark', trim='M_steel', top='M_steel'),
            tints=dict(face=(0.95, 0.93, 0.9), panel=(0.9, 0.9, 0.95), trim=(0.8, 0.82, 0.88), top=(0.7, 0.72, 0.78)), skip=skip, panel_y=1.5)
# bande de danger au pied du mur + conduit teal lumineux
add_strip(walls, rr, [(FACE_D - 0.02, 0.18), (FACE_D - 0.02, 0.5)], 'M_hazard', 'in', (0.85, 0.85, 0.85), skip, 1.0)
add_strip(walls, rr, [(FACE_D - 0.03, 1.52), (FACE_D - 0.03, 1.62)], 'M_lamp_t', 'in', (1, 1, 1), skip, 4.0)
ring_beam(walls, rr, FACE_D - 0.1, FACE_D + 0.02, 2.35, 2.55, 'M_steel', (0.7, 0.72, 0.78), skip, 2.0)
# nervures verticales (poutres en I) tous les ~6 m
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
pilasters_on_wall(dec, rr, pil, FACE_D, HW, 'M_dark', (0.75, 0.78, 0.85), cap_mat='M_steel', cap_tint=(0.8, 0.82, 0.9), w=0.55)

# sas : cadre massif, linteau, vantail baissé à moitié (rayures de danger)
for sx in (1, -1):
    nxz = (float(sx), 0.0)
    pos = (26.0 * sx, 0.0)
    yaw = yaw_of(*nxz)
    OW = 4.2
    jw = (GATE_W - OW) / 2
    for sg in (-1, 1):
        x1, z1 = local_to_world(pos, nxz, sg * (OW / 2 + jw / 2), 0.75)
        walls.box((jw, HW, 1.5), pos=(x1, 0, z1), mat='M_cream', tint=(0.85, 0.85, 0.9), yaw=yaw, bev=0.03)
        x2, z2 = local_to_world(pos, nxz, sg * (OW / 2 + 0.12), 0.1)
        dec.box((0.34, 2.75, 0.3), pos=(x2, 0, z2), mat='M_dark', tint=(0.7, 0.72, 0.8), yaw=yaw)
    x1, z1 = local_to_world(pos, nxz, 0, 0.75)
    walls.box((OW + 0.02, HW - 2.7, 1.5), pos=(x1, 2.7, z1), mat='M_cream', tint=(0.85, 0.85, 0.9), yaw=yaw)
    x1, z1 = local_to_world(pos, nxz, 0, 0.12)
    dec.box((OW + 0.4, 0.3, 0.34), pos=(x1, 2.62, z1), mat='M_dark', tint=(0.7, 0.72, 0.8), yaw=yaw)
    dec.box((OW - 0.4, 0.07, 0.04), pos=(x1, 2.52, z1), mat='M_lamp_t', tint=(1, 1, 1), yaw=yaw)
    # vantail à demi baissé, chevrons de danger
    x1, z1 = local_to_world(pos, nxz, 0, 0.5)
    dec.box((OW - 0.1, 0.9, 0.16), pos=(x1, 1.7, z1), mat='M_hazard', tint=(0.9, 0.9, 0.9), yaw=yaw)
    dec.box((OW - 0.1, 0.12, 0.2), pos=(x1, 1.62, z1), mat='M_dark', tint=(0.6, 0.62, 0.7), yaw=yaw)
    # fond du sas sombre éclairé
    x1, z1 = local_to_world(pos, nxz, 0, 1.45)
    dec.box((OW, 2.6, 0.1), pos=(x1, 0, z1), mat='M_dark', tint=(0.45, 0.5, 0.6), yaw=yaw)
    for k in (-1, 1):
        x1, z1 = local_to_world(pos, nxz, k * 1.2, 1.37)
        dec.box((0.12, 1.9, 0.05), pos=(x1, 0.4, z1), mat='M_lamp_o', tint=(1, 1, 1), yaw=yaw)

# ------------------------------------------------------------------ coursive (caillebotis) + garde-corps
D_IN, D_OUT = 1.5, 5.5
add_strip(gal, rr, [(D_IN, HW), (D_OUT, HW)], 'M_grate', 'up', (0.9, 0.9, 0.95), None, 1.0)
# poutrelles sous le caillebotis (visibles depuis le haut à travers les ajours : sombres)
add_strip(gal, rr, [(D_IN, HW - 0.02), (D_OUT, HW - 0.02)], 'M_dark', 'up', (0.35, 0.35, 0.4), None, 2.0)
ring_beam(gal, rr, D_IN, D_IN + 0.18, HW - 0.06, HW + 0.06, 'M_steel', (0.7, 0.72, 0.78), None, 2.0)
ring_beam(gal, rr, D_OUT - 0.2, D_OUT, HW - 0.06, HW + 0.1, 'M_steel', (0.7, 0.72, 0.78), None, 2.0)
# garde-corps sur le mur (côté arène)
ring_rail(dec, rr, 0.32, HW, 0.95, 2.4, 'M_steel', (0.82, 0.84, 0.9), skip)
# jambes de force sous la coursive (vues de l'extérieur)
ring_posts(gal, rr, D_OUT - 0.5, 0.0, HW, 4.0, 0.3, 'M_dark', (0.6, 0.62, 0.7), offset=0.5, depth=0.5)

# ------------------------------------------------------------------ cloison arrière + baie vitrée au fond (-Z)
L = rr.length()
top_edge = rr.s_nearest(0.0, -(16.0 + D_OUT))
# la baie occupe le côté -Z : s de x=-21 à x=+21 sur la courbe de base (s ~ 0..42)
WIN = [(-3.0, 46.0), (L - 3.0, L + 0.1)]
Y_BULK = 9.2
add_strip(gal, rr, [(D_OUT, HW), (D_OUT, 5.0)], 'M_cream', 'in', (0.9, 0.9, 0.95), WIN, 2.0)
add_strip(gal, rr, [(D_OUT, 5.0), (D_OUT, 5.35)], 'M_dark', 'in', (0.7, 0.72, 0.8), WIN, 2.0)
add_strip(gal, rr, [(D_OUT, 5.35), (D_OUT, Y_BULK - 0.5)], 'M_steel', 'in', (0.8, 0.82, 0.88), WIN, 2.0)
add_strip(gal, rr, [(D_OUT, Y_BULK - 0.5), (D_OUT, Y_BULK - 0.35)], 'M_lamp_o', 'in', (1, 1, 1), WIN, 4.0)
ring_beam(gal, rr, D_OUT - 0.1, D_OUT + 1.6, Y_BULK - 0.35, Y_BULK + 0.15, 'M_dark', (0.65, 0.67, 0.75), WIN, 2.0)
# conduites en laiton et acier le long de la cloison
ring_pipe(dec, rr, D_OUT - 0.25, 4.1, 0.2, 'M_brass', (0.95, 0.75, 0.45), WIN, 1.0)
ring_pipe(dec, rr, D_OUT - 0.2, 4.6, 0.11, 'M_steel', (0.8, 0.82, 0.9), WIN, 1.0, k=6)
ring_pipe(dec, rr, D_OUT - 0.3, 8.3, 0.25, 'M_steel', (0.75, 0.78, 0.86), WIN, 1.0)
# hublots tous les 3,7 m
P, N, Tn, s_ = rr.along(3.7, D_OUT - 0.05, offset=1.0)
keep = [i for i in range(len(P)) if not (P[i][1] < -14 and abs(P[i][0]) < 22.5)]
fr_V, fr_F = p_torus(0.5, 0.075, 16, 5)
fr_V = fr_V @ rotm(0, math.pi / 2, 0).T
gl_V, gl_F = p_lathe([(0.5, 0), (0.46, 0.02), (0.0, 0.06)], 16, False, False)
gl_V = gl_V @ rotm(0, math.pi / 2, 0).T
pos = np.array([(P[i][0], 6.7, P[i][1]) for i in keep])
yaw = np.array([yaw_of(-N[i][0], -N[i][1]) for i in keep])
dec.add_many((fr_V, fr_F), 'M_steel', pos, yaw=yaw, tint=np.tile(s2l((0.75, 0.78, 0.85)), (len(keep), 1)))
dec.add_many((gl_V, gl_F), 'M_glass', pos + 0.0, yaw=yaw, tint=np.tile(s2l((0.8, 1.0, 1.0)), (len(keep), 1)))
# colonnes verticales entre les hublots
P2, N2, T2, s2 = rr.along(7.4, D_OUT - 0.2, offset=2.85)
for i in range(len(P2)):
    if P2[i][1] < -14 and abs(P2[i][0]) < 22.5:
        continue
    cyl_between(dec, (P2[i][0], HW, P2[i][1]), (P2[i][0], Y_BULK - 0.4, P2[i][1]), 0.15, mat='M_steel', tint=(0.75, 0.78, 0.86), seg=8)
    dec.box((0.5, 0.35, 0.5), pos=(P2[i][0], HW, P2[i][1]), mat='M_dark', tint=(0.65, 0.67, 0.75), yaw=yaw_of(N2[i][0], N2[i][1]))

# baie vitrée : meneaux, traverses, appui
ZW = -(16.0 + D_OUT)
XW0, XW1 = -22.0, 22.0
n_m = 9
for k in range(n_m):
    x = XW0 + (XW1 - XW0) * k / (n_m - 1)
    dec.box((0.55, Y_BULK - HW, 0.8), pos=(x, HW, ZW - 0.25), mat='M_dark', tint=(0.65, 0.68, 0.76), bev=0.03)
    dec.box((0.3, Y_BULK - HW, 0.12), pos=(x, HW, ZW + 0.2), mat='M_steel', tint=(0.8, 0.82, 0.9))
    for yy in np.arange(HW + 0.6, Y_BULK - 0.4, 0.9):
        dec.add(p_box(0.07, 0.07, 0.07), 'M_brass', pos=(x - 0.2, yy, ZW + 0.27), tint=(0.95, 0.78, 0.5))
        dec.add(p_box(0.07, 0.07, 0.07), 'M_brass', pos=(x + 0.2, yy, ZW + 0.27), tint=(0.95, 0.78, 0.5))
dec.box((XW1 - XW0 + 1.2, 0.5, 0.9), pos=((XW0 + XW1) / 2, Y_BULK - 0.55, ZW - 0.2), mat='M_dark', tint=(0.65, 0.68, 0.76), bev=0.03)
dec.box((XW1 - XW0 + 1.2, 0.18, 0.7), pos=((XW0 + XW1) / 2, 5.4, ZW - 0.1), mat='M_steel', tint=(0.78, 0.8, 0.88))
dec.box((XW1 - XW0 + 1.2, 0.5, 0.85), pos=((XW0 + XW1) / 2, HW, ZW - 0.1), mat='M_cream', tint=(0.85, 0.85, 0.9), bev=0.03)
dec.box((XW1 - XW0, 0.08, 0.1), pos=((XW0 + XW1) / 2, Y_BULK - 0.64, ZW + 0.3), mat='M_lamp_t', tint=(1, 1, 1))
# cadre arrondi vers les coins (retours de la baie)
for sx in (-1, 1):
    dec.box((0.9, Y_BULK - HW, 0.9), pos=(sx * 22.6, HW, ZW + 0.1), mat='M_dark', tint=(0.65, 0.68, 0.76), bev=0.04)

# ------------------------------------------------------------------ lampes murales (Torch_xx) : projecteurs de pont ambre
def station_lamp(md, mf, Fp, n, arm):
    x, y, z = Fp
    nx, nz = n
    yaw = yaw_of(nx, nz)
    wx, wz = x + nx * arm, z + nz * arm
    md.box((0.3, 0.55, 0.1), pos=(wx - nx * 0.04, y - 0.45, wz - nz * 0.04), mat='M_dark', tint=(0.7, 0.72, 0.8), yaw=yaw)
    md.box((0.09, 0.09, arm + 0.04), pos=(x + nx * arm * 0.5, y - 0.2, z + nz * arm * 0.5), mat='M_dark', tint=(0.7, 0.72, 0.8), yaw=yaw)
    md.lathe([(0.12, y - 0.2), (0.17, y - 0.12), (0.19, y + 0.06), (0.14, y + 0.12), (0.0, y + 0.13)], pos=(x, 0, z), mat='M_steel', seg=10, tint=(0.8, 0.82, 0.9))
    mf.lathe([(0.0, y - 0.19), (0.12, y - 0.17), (0.15, y - 0.05), (0.12, y + 0.07), (0.0, y + 0.1)], pos=(x, 0, z), mat='M_lamp_o', seg=9, cap0=False, cap1=False)


torches(sc, rr, y=2.2, sconce_fn=station_lamp)

# ------------------------------------------------------------------ obstacles : réservoirs (0,3), colonnes générateur (1,2), fûts (4,5)
def fuel_tank(mb, x, z, r, tint, seed):
    h = 2.7
    tank(mb, x, z, r, h, mat='M_steel', band_mat='M_dark', tint=tint, seg=22, bands=(0.2, 0.52, 0.84), y0=0.0, dome_h=0.5)
    mb.lathe([(r, 0.0), (r, 0.18), (r * 0.96, 0.24)], pos=(x, 0, z), mat='M_dark', seg=22, tint=(0.6, 0.62, 0.7))
    # bande de danger, raccord latéral + vanne
    mb.lathe([(r * 1.005, 1.2), (r * 1.005, 1.5)], pos=(x, 0, z), mat='M_hazard', seg=22, cap0=False, cap1=False, tint=(0.9, 0.9, 0.9))
    a = rng.uniform(0, 6.28)
    cx_, cz_ = x + math.cos(a) * r, z + math.sin(a) * r
    cyl_between(mb, (cx_ * 1.0, 1.9, cz_ * 1.0), (x + math.cos(a) * (r + 0.45), 1.9, z + math.sin(a) * (r + 0.45)), 0.1, mat='M_brass', tint=(0.95, 0.75, 0.45), seg=8) if False else None
    mb.add(p_torus(0.17, 0.035, 12, 5), 'M_brass', pos=(x + math.cos(a) * (r + 0.07), 1.95, z + math.sin(a) * (r + 0.07)), yaw=-a + math.pi / 2, pitch=0, roll=0, tint=(0.95, 0.75, 0.45))
    mb.cyl(0.05, 0.35, pos=(x + math.cos(a) * (r + 0.07), 1.78, z + math.sin(a) * (r + 0.07)), mat='M_brass', seg=6, tint=(0.95, 0.75, 0.45))
    # échelle d'inspection
    b = a + 2.2
    for yy in np.arange(0.4, 2.7, 0.3):
        mb.box((0.34, 0.04, 0.04), pos=(x + math.cos(b) * (r + 0.05) - 0.17 * math.sin(b), yy, z + math.sin(b) * (r + 0.05) + 0.17 * math.cos(b)), mat='M_dark', tint=(0.7, 0.72, 0.8), yaw=-b)
    mb.lathe([(0.12, 2.95), (0.1, 3.15), (0.0, 3.2)], pos=(x, 0, z), mat='M_brass', seg=8, tint=(0.95, 0.75, 0.45))


def gen_column(mb, x, z, r, seed):
    mb.lathe([(r, 0.0), (r, 0.45), (r * 0.84, 0.55)], pos=(x, 0, z), mat='M_dark', seg=22, tint=(0.7, 0.72, 0.8))
    mb.lathe([(r * 0.8, 0.5), (r * 0.8, 2.55)], pos=(x, 0, z), mat='M_cream', seg=22, tint=(0.95, 0.92, 0.88), cap0=False, cap1=False)
    for yy in (0.95, 1.55, 2.15):
        mb.lathe([(r * 0.82, yy - 0.1), (r * 0.9, yy - 0.04), (r * 0.9, yy + 0.04), (r * 0.82, yy + 0.1)], pos=(x, 0, z), mat='M_dark', seg=22, cap0=False, cap1=False,
                 tint=(0.7, 0.72, 0.8))
        mb.lathe([(r * 0.9, yy - 0.03), (r * 0.9, yy + 0.03)], pos=(x, 0, z), mat='M_lamp_t', seg=22, cap0=False, cap1=False)
    mb.lathe([(r * 0.88, 2.55), (r * 0.95, 2.62), (r * 0.9, 2.8), (r * 0.55, 2.95), (r * 0.2, 3.0), (0, 3.0)], pos=(x, 0, z), mat='M_steel', seg=22, tint=(0.8, 0.82, 0.9))
    for k in range(3):
        a = 2 * math.pi * k / 3 + seed
        cyl_between(mb, (x + math.cos(a) * r * 0.86, 0.5, z + math.sin(a) * r * 0.86), (x + math.cos(a) * r * 0.86, 2.6, z + math.sin(a) * r * 0.86), 0.07,
                    mat='M_brass', tint=(0.95, 0.75, 0.45), seg=6)
    cyl_between(mb, (x, 3.0, z), (x + 0.1, 3.9, z), 0.035, mat='M_dark', tint=(0.7, 0.72, 0.8), seg=5)
    mb.add(p_sphere(0.07, 6, 4), 'M_lamp_o', pos=(x + 0.1, 3.9, z))


def drums(mb, x, z, r, seed):
    mb.lathe([(r, 0.0), (r, 0.14), (r * 0.96, 0.17)], pos=(x, 0, z), mat='M_dark', seg=20, tint=(0.65, 0.67, 0.75))
    cols = [(0.78, 0.38, 0.14), (0.55, 0.58, 0.64), (0.2, 0.5, 0.58), (0.7, 0.62, 0.45), (0.65, 0.2, 0.15)]
    br = 0.38
    spots = [(0, 0)] + [(0.74 * math.cos(a), 0.74 * math.sin(a)) for a in np.arange(0, 2 * math.pi, math.pi / 3) + seed * 0.4]
    for i, (dx, dz) in enumerate(spots):
        tint = cols[(i + int(seed)) % len(cols)]
        mb.lathe([(br, 0.17), (br * 1.02, 0.2), (br * 1.02, 0.9), (br * 0.96, 0.95), (br * 0.85, 0.96), (0.0, 0.96)], pos=(x + dx, 0, z + dz), mat='M_cream', seg=12, tint=tint, jit=0.05)
        for yy in (0.34, 0.55, 0.76):
            mb.lathe([(br * 1.02, yy - 0.02), (br * 1.06, yy), (br * 1.02, yy + 0.02)], pos=(x + dx, 0, z + dz), mat='M_dark', seg=12, cap0=False, cap1=False, tint=(0.7, 0.72, 0.8))
    # deuxième niveau + sangle
    for i, a in enumerate(np.arange(0, 2 * math.pi, math.pi / 2) + 0.5):
        dx, dz = 0.5 * math.cos(a), 0.5 * math.sin(a)
        tint = cols[(i + 2 + int(seed)) % len(cols)]
        mb.lathe([(br, 0.96), (br * 1.02, 0.99), (br * 1.02, 1.69), (br * 0.96, 1.74), (br * 0.85, 1.75), (0.0, 1.75)], pos=(x + dx, 0, z + dz), mat='M_cream', seg=12, tint=tint, jit=0.05)
    mb.add(p_torus(r * 0.82, 0.03, 18, 4), 'M_brass', pos=(x, 0.98, z), tint=(0.95, 0.75, 0.45))
    mb.box((0.5, 0.06, 0.34), pos=(x + 0.1, 1.75, z), mat='M_hazard', tint=(0.9, 0.9, 0.9), yaw=0.4)


for i in range(6):
    mb, o = obstacle_part(sc, i)
    if i in (0, 3):
        fuel_tank(mb, o['x'], o['z'], o['r'], (0.75, 0.68, 0.6) if i == 0 else (0.62, 0.66, 0.72), i)
    elif i in (1, 2):
        gen_column(mb, o['x'], o['z'], o['r'], i)
    else:
        drums(mb, o['x'], o['z'], o['r'], i)

# ------------------------------------------------------------------ coque extérieure (jupe) + vide : Terre, étoiles
outer = sc.part('Hull')
add_strip(outer, rr, [(D_OUT + 1.6, Y_BULK + 0.15), (D_OUT + 1.6, 0.0), (D_OUT + 1.6, -8.0)], 'M_dark', 'out', (0.7, 0.72, 0.8), None, 4.0)
add_strip(outer, rr, [(D_OUT + 1.6, -8.0), (D_OUT - 2.0, -8.5)], 'M_dark', 'down', (0.5, 0.5, 0.58), None, 4.0)
add_strip(outer, rr, [(D_OUT + 1.6, Y_BULK + 0.15), (D_OUT - 0.1, Y_BULK + 0.15)], 'M_dark', 'up', (0.7, 0.72, 0.8), WIN, 4.0)
# sous la coursive et au pied du mur : fermer le volume
add_strip(outer, rr, [(D_OUT, HW - 0.1), (D_OUT, 0.0), (D_OUT, -6.0)], 'M_steel', 'out', (0.65, 0.68, 0.76), None, 4.0)
# sol de l'enceinte sous la coursive (fond)
add_strip(outer, rr, [(0.0, -0.02), (D_OUT, -0.02)], 'M_dark', 'up', (0.3, 0.3, 0.35), None, 4.0)
# nervures de coque
ring_posts(outer, rr, D_OUT + 1.6, -6.0, Y_BULK + 6.0, 6.0, 0.5, 'M_steel', (0.7, 0.72, 0.8), depth=0.6, offset=1.0)

space = sc.part('Space')
sc.noao.add('Space')
EARTH_C = (-27.0, -192.0, -173.0)
EARTH_R = 122.0
V, F, UV = sphere_uv_mesh(EARTH_R, 56, 30, EARTH_C, tilt=0.4)
space.add((V, F), 'M_earth', uv=UV)
stars(space, rng, 700, (0.0, 8.0, 0.0), 260, 380, az=(-85, 85), el=(-72, -2), size=(0.45, 1.1))
sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5, 'Gallery': 0.5, 'Walls': 0.5}
sc.build(ao_samples=24, ao_dist=3.0, ao_floor=0.45)
print('[tris]', sc.tri_total)
sc.export(OUTDIR + '/arena_station.glb')
