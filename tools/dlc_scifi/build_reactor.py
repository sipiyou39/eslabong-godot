"""arena_reactor.glb — « Cœur de Réacteur » : salle de réacteur, anneaux de confinement autour du noyau, cuves, passerelles, lueur orange/teal douce."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_lib import *

G.seed(8303)
rng = np.random.default_rng(8303)

defmat('M_ground', tex=T('reactor_ground.jpg'), norm=T('reactor_ground_n.png'), emit_tex=T('reactor_ground_e.png'), emit_str=1.6, rough=0.7, metal=0.3, uv=1, spec=0.5)
defmat('M_concrete', tex=T('reactor_concrete.jpg'), norm=T('reactor_concrete_n.jpg'), rough=0.9, uv=4.0)
defmat('M_steel', tex=T('reactor_steel.jpg'), norm=T('reactor_steel_n.jpg'), rough=0.5, metal=0.6, uv=2.0)
defmat('M_dark', tex=T('reactor_dark.jpg'), norm=T('reactor_dark_n.jpg'), rough=0.5, metal=0.6, uv=2.0)
defmat('M_cuve', tex=T('reactor_cuve.jpg'), norm=T('reactor_cuve_n.jpg'), rough=0.55, metal=0.4, uv=2.0)
defmat('M_hazard', tex=T('reactor_hazard.jpg'), rough=0.6, metal=0.2, uv=1.0)
defmat('M_grate', tex=T('reactor_grate.jpg'), norm=T('reactor_grate_n.jpg'), emit_tex=T('reactor_grate.jpg'), emit_str=0.35, rough=0.55, metal=0.6, uv=1.0)
defmat('M_brass', rough=0.35, metal=0.85)
defmat('M_lamp_o', emit='#ff9030', emit_str=2.6, vcol=False, color='#ff9030')
defmat('M_lamp_t', emit='#40e0d0', emit_str=2.2, vcol=False, color='#40e0d0')
defmat('M_core', emit='#ff8a28', emit_str=2.4, vcol=False, color='#ff8a28')
defmat('M_core_t', emit='#34d8c8', emit_str=1.8, vcol=False, color='#34d8c8')
defmat('M_glass', emit='#2a6a78', emit_str=0.5, rough=0.15, metal=0.2, spec=1.0)

sc = Scene('arena_reactor')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
walls = sc.part('Walls')
gal = sc.part('Gallery')
build_ground(sc, step=1.0)
L = rr.length()

# ------------------------------------------------------------------ enceinte de béton + sas
GATE_W = 6.8
skip = []
for sx in (1, -1):
    s0 = rr.s_nearest(26.0 * sx, 0.0)
    skip.append((s0 - GATE_W / 2, s0 + GATE_W / 2))
FACE_D = 0.36
build_walls(sc, rr, T=1.5, H=HW, face_d=FACE_D, mats=dict(face='M_concrete', panel='M_dark', trim='M_steel', top='M_steel'),
            tints=dict(face=(1.0, 0.97, 0.92), panel=(0.9, 0.9, 0.95), trim=(0.8, 0.82, 0.88), top=(0.72, 0.74, 0.8)), skip=skip, panel_y=1.5)
add_strip(walls, rr, [(FACE_D - 0.02, 0.18), (FACE_D - 0.02, 0.45)], 'M_hazard', 'in', (0.85, 0.85, 0.85), skip, 1.0)
# fentes de refroidissement lumineuses discontinues (orange) et bande teal
glow_skip = list(skip)
seg_len, period = 2.4, 4.8
s_ = 0.0
while s_ < L:
    glow_skip.append((s_ + seg_len, s_ + period))
    s_ += period
add_strip(walls, rr, [(FACE_D - 0.03, 2.0), (FACE_D - 0.03, 2.14)], 'M_lamp_o', 'in', (1, 1, 1), glow_skip, 4.0)
add_strip(walls, rr, [(FACE_D - 0.03, 1.52), (FACE_D - 0.03, 1.6)], 'M_lamp_t', 'in', (1, 1, 1), skip, 4.0)
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
pilasters_on_wall(dec, rr, pil, FACE_D, HW, 'M_steel', (0.7, 0.72, 0.8), cap_mat='M_dark', cap_tint=(0.7, 0.72, 0.8), w=0.6)

for sx in (1, -1):
    nxz = (float(sx), 0.0)
    pos = (26.0 * sx, 0.0)
    yaw = yaw_of(*nxz)
    OW = 4.2
    jw = (GATE_W - OW) / 2
    for sg in (-1, 1):
        x1, z1 = local_to_world(pos, nxz, sg * (OW / 2 + jw / 2), 0.75)
        walls.box((jw, HW, 1.5), pos=(x1, 0, z1), mat='M_concrete', tint=(0.95, 0.92, 0.88), yaw=yaw, bev=0.03)
        x2, z2 = local_to_world(pos, nxz, sg * (OW / 2 + 0.12), 0.1)
        dec.box((0.36, 2.8, 0.34), pos=(x2, 0, z2), mat='M_steel', tint=(0.7, 0.72, 0.8), yaw=yaw)
    x1, z1 = local_to_world(pos, nxz, 0, 0.75)
    walls.box((OW + 0.02, HW - 2.7, 1.5), pos=(x1, 2.7, z1), mat='M_concrete', tint=(0.95, 0.92, 0.88), yaw=yaw)
    x1, z1 = local_to_world(pos, nxz, 0, 0.12)
    dec.box((OW + 0.5, 0.34, 0.36), pos=(x1, 2.62, z1), mat='M_steel', tint=(0.7, 0.72, 0.8), yaw=yaw)
    dec.box((OW - 0.4, 0.07, 0.04), pos=(x1, 2.5, z1), mat='M_lamp_o', yaw=yaw)
    # porte blindée à demi relevée + lueur du sas
    x1, z1 = local_to_world(pos, nxz, 0, 0.6)
    dec.box((OW - 0.1, 1.0, 0.18), pos=(x1, 1.65, z1), mat='M_hazard', tint=(0.9, 0.9, 0.9), yaw=yaw)
    x1, z1 = local_to_world(pos, nxz, 0, 1.45)
    dec.box((OW, 2.6, 0.1), pos=(x1, 0, z1), mat='M_dark', tint=(0.5, 0.52, 0.6), yaw=yaw)
    for k in (-1, 1):
        x1, z1 = local_to_world(pos, nxz, k * 1.2, 1.37)
        dec.box((0.12, 1.9, 0.05), pos=(x1, 0.4, z1), mat='M_lamp_t', yaw=yaw)

# ------------------------------------------------------------------ coursive + cloison + cuves
D_IN, D_OUT = 1.5, 5.5
add_strip(gal, rr, [(D_IN, HW), (D_OUT, HW)], 'M_grate', 'up', (0.95, 0.95, 1.0), None, 1.0)
ring_beam(gal, rr, D_IN, D_IN + 0.18, HW - 0.06, HW + 0.06, 'M_steel', (0.7, 0.72, 0.8), None, 2.0)
ring_beam(gal, rr, D_OUT - 0.2, D_OUT, HW - 0.06, HW + 0.1, 'M_steel', (0.7, 0.72, 0.8), None, 2.0)
ring_rail(dec, rr, 0.32, HW, 0.95, 2.4, 'M_steel', (0.82, 0.84, 0.9), skip)
ring_posts(gal, rr, D_OUT - 0.5, 0.0, HW, 4.0, 0.3, 'M_dark', (0.6, 0.62, 0.7), offset=0.5, depth=0.5)

Y_BULK = 10.5
# baie sur le noyau au fond : x ∈ [-7, 7] -> s ∈ [14, 28]
WIN = [(14.0, 28.0)]
add_strip(gal, rr, [(D_OUT, HW), (D_OUT, 5.2)], 'M_concrete', 'in', (0.95, 0.92, 0.88), WIN, 4.0)
add_strip(gal, rr, [(D_OUT, 5.2), (D_OUT, 5.5)], 'M_steel', 'in', (0.7, 0.72, 0.8), WIN, 2.0)
add_strip(gal, rr, [(D_OUT, 5.5), (D_OUT, Y_BULK - 0.6)], 'M_concrete', 'in', (0.9, 0.87, 0.83), WIN, 4.0)
add_strip(gal, rr, [(D_OUT, Y_BULK - 0.6), (D_OUT, Y_BULK - 0.4)], 'M_lamp_o', 'in', (1, 1, 1), WIN, 4.0)
ring_beam(gal, rr, D_OUT - 0.1, D_OUT + 1.6, Y_BULK - 0.4, Y_BULK + 0.2, 'M_steel', (0.65, 0.67, 0.75), WIN, 2.0)
ring_pipe(dec, rr, D_OUT - 0.3, 4.2, 0.24, 'M_brass', (0.95, 0.75, 0.45), WIN, 1.0)
ring_pipe(dec, rr, D_OUT - 0.25, 4.85, 0.12, 'M_steel', (0.8, 0.82, 0.9), WIN, 1.0, k=6)
ring_pipe(dec, rr, D_OUT - 0.4, 8.6, 0.32, 'M_steel', (0.72, 0.75, 0.84), WIN, 1.0)
ring_pipe(dec, rr, D_OUT - 0.4, 9.4, 0.18, 'M_brass', (0.95, 0.75, 0.45), WIN, 1.0, k=6)
# cuves verticales adossées à la cloison
CUVE_R = 1.9
P, N, Tn, s_ = rr.along(8.6, D_OUT + 0.9, offset=3.0)
for i in range(len(P)):
    if P[i][1] < -14 and abs(P[i][0]) < 9.5:
        continue
    x, z = P[i]
    tank(dec, x, z, CUVE_R, Y_BULK - 2.2, mat='M_cuve', band_mat='M_dark', tint=(0.95, 0.92, 0.85), seg=18, bands=(0.12, 0.88), y0=0.0, dome_h=1.0)
    dec.lathe([(CUVE_R * 1.015, 6.0), (CUVE_R * 1.015, 6.3)], pos=(x, 0, z), mat='M_lamp_t', seg=18, cap0=False, cap1=False)
    dec.lathe([(CUVE_R * 1.02, 3.6), (CUVE_R * 1.02, 4.1)], pos=(x, 0, z), mat='M_hazard', seg=18, cap0=False, cap1=False, tint=(0.9, 0.9, 0.9))
    cyl_between(dec, (x, Y_BULK - 1.0, z), (x, Y_BULK + 1.5, z), 0.3, mat='M_steel', tint=(0.75, 0.78, 0.85), seg=8)
# colonnes de soutien et fermes
ring_posts(gal, rr, D_OUT - 0.2, HW, Y_BULK - HW, 4.3, 0.5, 'M_steel', (0.7, 0.72, 0.8), offset=2.1, depth=0.6,
           skip_fn=lambda x, z: z < -14 and abs(x) < 9.0)

# baie du noyau : cadre massif, noyau et anneaux de confinement
ZW = -(16.0 + D_OUT)
XW = 7.0
for sx in (-1, 1):
    dec.box((0.9, Y_BULK - HW, 1.0), pos=(sx * XW, HW, ZW - 0.2), mat='M_steel', tint=(0.7, 0.72, 0.8), bev=0.04)
    dec.box((0.3, 5.0, 0.2), pos=(sx * (XW - 0.6), 3.4, ZW + 0.35), mat='M_lamp_o', tint=(1, 1, 1))
dec.box((2 * XW + 1.0, 1.1, 1.0), pos=(0, 8.9, ZW - 0.2), mat='M_steel', tint=(0.7, 0.72, 0.8), bev=0.04)
dec.box((2 * XW + 1.0, 0.7, 1.0), pos=(0, HW, ZW - 0.2), mat='M_dark', tint=(0.65, 0.68, 0.76), bev=0.04)
for k in range(1, 4):
    x = -XW + 2 * XW * k / 4
    dec.box((0.3, 5.6, 0.5), pos=(x, HW + 0.4, ZW - 0.1), mat='M_dark', tint=(0.65, 0.68, 0.76))
dec.box((2 * XW - 1, 0.08, 0.1), pos=(0, 8.3, ZW + 0.3), mat='M_lamp_t')
# chambre du noyau (derrière la baie)
ZC = ZW - 9.0
dec.box((60.0, 0.6, 60.0), pos=(0, HW - 0.7, ZW - 28.0), mat='M_dark', tint=(0.55, 0.57, 0.65))
for yy, rr_, col in ((0.0, 4.3, 'M_core'),):
    dec.lathe([(rr_, HW), (rr_ * 1.0, 26.0)], pos=(0, 0, ZC), mat='M_core', seg=24, cap0=False, cap1=False)
dec.lathe([(1.2, 0.0), (8.2, 0.0), (8.4, 0.6), (5.0, 0.9)], pos=(0, HW - 0.1, ZC), mat='M_steel', seg=24, tint=(0.7, 0.72, 0.8))
for yy in (4.6, 7.8, 8.8, 12.6, 14.2):
    dec.add(p_torus(4.45, 0.25, 28, 5), 'M_core_t', pos=(0, yy, ZC), tint=(1, 1, 1))
# bassin de refroidissement lumineux devant le noyau (visible par la baie)
dec.add(p_cyl(8.8, 0.08, 36), 'M_core', pos=(0, HW - 0.55, ZC), tint=(1, 0.8, 0.6))

dec.add(p_torus(5.9, 0.7, 36, 6), 'M_steel', pos=(0, 6.0, ZC), tint=(0.72, 0.75, 0.84))
dec.add(p_torus(5.9, 0.3, 36, 5), 'M_lamp_o', pos=(0, 6.0, ZC), tint=(1, 1, 1), scale=(0.9, 1.0, 0.9)) if False else None
dec.add(p_torus(7.6, 0.4, 40, 5), 'M_core_t', pos=(0, 6.2, ZC), tint=(1, 1, 1), scale=(1.0, 1.0, 1.0)) if False else None
dec.add(p_torus(6.6, 0.7, 40, 6), 'M_steel', pos=(0, 10.5, ZC), tint=(0.72, 0.75, 0.84))
dec.add(p_torus(9.4, 0.3, 44, 5), 'M_lamp_o', pos=(0, 11.0 + 0.0, ZC), tint=(1, 1, 1), scale=(1.0, 1.0, 1.0)) if False else None
dec.add(p_torus(7.2, 0.8, 40, 6), 'M_steel', pos=(0, 15.5, ZC), tint=(0.72, 0.75, 0.84))
for k in range(4):
    a = math.pi / 4 + k * math.pi / 2
    box_between(dec, (6.0 * math.cos(a), 6.0, ZC + 6.0 * math.sin(a)), (8.6 * math.cos(a), HW, ZC + 8.6 * math.sin(a)), 0.5, 0.5, mat='M_steel', tint=(0.7, 0.72, 0.8))
# ponts de service vers le noyau
dec.box((2.6, 0.3, 17.0), pos=(0, HW - 0.1, ZW - 9.0), mat='M_grate', tint=(0.9, 0.9, 0.95))
for sx in (-1, 1):
    dec.box((0.08, 1.0, 17.0), pos=(sx * 1.3, HW + 0.2, ZW - 9.0), mat='M_steel', tint=(0.8, 0.82, 0.9))
# lueur diffuse du noyau (halo) : disques emissifs derrière le cylindre
dec.lathe([(4.9, HW), (4.9, 26.0)], pos=(0, 0, ZC), mat='M_core', seg=24, cap0=False, cap1=False, tint=(1, 1, 1)) if False else None

# ------------------------------------------------------------------ lampes grillagées (Torch_xx)
def cage_lamp(md, mf, Fp, n, arm):
    x, y, z = Fp
    nx, nz = n
    yaw = yaw_of(nx, nz)
    wx, wz = x + nx * arm, z + nz * arm
    md.box((0.3, 0.5, 0.1), pos=(wx - nx * 0.04, y - 0.45, wz - nz * 0.04), mat='M_dark', tint=(0.7, 0.72, 0.8), yaw=yaw)
    md.box((0.09, 0.09, arm + 0.04), pos=(x + nx * arm * 0.5, y - 0.2, z + nz * arm * 0.5), mat='M_dark', tint=(0.7, 0.72, 0.8), yaw=yaw)
    md.lathe([(0.1, y - 0.2), (0.16, y - 0.12), (0.17, y + 0.1), (0.1, y + 0.2), (0.0, y + 0.22)], pos=(x, 0, z), mat='M_steel', seg=8, tint=(0.75, 0.78, 0.85))
    mf.lathe([(0.0, y - 0.18), (0.11, y - 0.12), (0.13, y), (0.1, y + 0.12), (0.0, y + 0.16)], pos=(x, 0, z), mat='M_lamp_o', seg=8, cap0=False, cap1=False)


torches(sc, rr, y=2.2, sconce_fn=cage_lamp)

# ------------------------------------------------------------------ obstacles : cuves (0,3), condensateurs (1,2), transformateurs (4,5)
def coolant_tank(mb, x, z, r, tint, seed):
    h = 2.6
    tank(mb, x, z, r, h, mat='M_cuve', band_mat='M_dark', tint=tint, seg=22, bands=(0.2, 0.85), y0=0.0, dome_h=0.55)
    mb.lathe([(r, 0.0), (r, 0.18), (r * 0.96, 0.24)], pos=(x, 0, z), mat='M_dark', seg=22, tint=(0.6, 0.62, 0.7))
    mb.lathe([(r * 1.012, 1.0), (r * 1.012, 1.35)], pos=(x, 0, z), mat='M_lamp_t', seg=22, cap0=False, cap1=False)
    mb.lathe([(r * 1.01, 1.55), (r * 1.01, 1.85)], pos=(x, 0, z), mat='M_hazard', seg=22, cap0=False, cap1=False, tint=(0.9, 0.9, 0.9))
    a = seed * 1.7
    mb.add(p_torus(0.17, 0.035, 12, 5), 'M_brass', pos=(x + math.cos(a) * (r + 0.07), 2.1, z + math.sin(a) * (r + 0.07)), yaw=-a + math.pi / 2, tint=(0.95, 0.75, 0.45))
    cyl_between(mb, (x, 3.1, z), (x, 3.9, z), 0.1, mat='M_brass', tint=(0.95, 0.75, 0.45), seg=8)
    mb.add(p_torus(0.3, 0.04, 14, 4), 'M_steel', pos=(x, 3.7, z), tint=(0.8, 0.82, 0.9))


def capacitor(mb, x, z, r, seed):
    mb.lathe([(r, 0.0), (r, 0.4), (r * 0.8, 0.5)], pos=(x, 0, z), mat='M_dark', seg=22, tint=(0.7, 0.72, 0.8))
    for k in range(3):
        y0 = 0.5 + k * 0.78
        mb.lathe([(r * 0.78, y0), (r * 0.9, y0 + 0.05), (r * 0.9, y0 + 0.5), (r * 0.78, y0 + 0.55)], pos=(x, 0, z), mat='M_steel', seg=22, tint=(0.8, 0.82, 0.9))
        mb.lathe([(r * 0.9, y0 + 0.22), (r * 0.91, y0 + 0.3)], pos=(x, 0, z), mat='M_lamp_o', seg=22, cap0=False, cap1=False)
        mb.lathe([(r * 0.7, y0 + 0.55), (r * 0.7, y0 + 0.78)], pos=(x, 0, z), mat='M_dark', seg=16, cap0=False, cap1=False, tint=(0.6, 0.62, 0.7))
    mb.lathe([(r * 0.8, 2.85), (r * 0.5, 3.0), (0.2, 3.05), (0, 3.05)], pos=(x, 0, z), mat='M_steel', seg=22, tint=(0.8, 0.82, 0.9))
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4 + seed
        cyl_between(mb, (x + math.cos(a) * r * 0.55, 3.0, z + math.sin(a) * r * 0.55), (x + math.cos(a) * r * 0.55, 3.45, z + math.sin(a) * r * 0.55), 0.06, mat='M_steel', tint=(0.85, 0.87, 0.95), seg=6)
        mb.add(p_sphere(0.1, 6, 4), 'M_lamp_t', pos=(x + math.cos(a) * r * 0.55, 3.5, z + math.sin(a) * r * 0.55))


def transformer(mb, x, z, r, seed):
    mb.lathe([(r, 0.0), (r, 0.3), (r * 0.85, 0.35)], pos=(x, 0, z), mat='M_dark', seg=20, tint=(0.7, 0.72, 0.8))
    mb.lathe([(r * 0.82, 0.3), (r * 0.82, 1.9)], pos=(x, 0, z), mat='M_cuve', seg=20, cap0=False, cap1=False, tint=(0.9, 0.86, 0.8))
    for k in range(10):
        a = 2 * math.pi * k / 10
        mb.add(p_box(0.08, 1.4, 0.4), 'M_steel', pos=(x + math.cos(a) * r * 0.92, 0.45, z + math.sin(a) * r * 0.92), yaw=-a + math.pi / 2, tint=(0.75, 0.78, 0.86))
    mb.lathe([(r * 0.86, 1.9), (r * 0.7, 2.0), (r * 0.3, 2.05), (0, 2.05)], pos=(x, 0, z), mat='M_steel', seg=20, tint=(0.8, 0.82, 0.9))
    for k in range(3):
        a = 2 * math.pi * k / 3 + seed
        px, pz = x + math.cos(a) * r * 0.35, z + math.sin(a) * r * 0.35
        mb.lathe([(0.1, 2.0), (0.14, 2.2), (0.1, 2.5), (0.14, 2.7), (0.08, 3.0), (0.0, 3.05)], pos=(px, 0, pz), mat='M_brass', seg=8, tint=(0.95, 0.78, 0.5))
    mb.lathe([(r * 0.83, 1.05), (r * 0.83, 1.2)], pos=(x, 0, z), mat='M_lamp_o', seg=20, cap0=False, cap1=False)


for i in range(6):
    mb, o = obstacle_part(sc, i)
    if i in (0, 3):
        coolant_tank(mb, o['x'], o['z'], o['r'], (0.95, 0.92, 0.85), i)
    elif i in (1, 2):
        capacitor(mb, o['x'], o['z'], o['r'], i)
    else:
        transformer(mb, o['x'], o['z'], o['r'], i)

# ------------------------------------------------------------------ coque extérieure
outer = sc.part('Hull')
sc.noao.add('Hull')
add_strip(outer, rr, [(D_OUT + 1.6, Y_BULK + 0.2), (D_OUT + 1.6, 0.0), (D_OUT + 1.6, -8.0)], 'M_concrete', 'out', (0.8, 0.78, 0.74), None, 4.0)
add_strip(outer, rr, [(D_OUT + 1.6, -8.0), (D_OUT - 2.0, -8.5)], 'M_dark', 'down', (0.5, 0.5, 0.58), None, 4.0)
add_strip(outer, rr, [(D_OUT + 1.6, Y_BULK + 0.2), (D_OUT - 0.1, Y_BULK + 0.2)], 'M_steel', 'up', (0.7, 0.72, 0.8), WIN, 4.0)
add_strip(outer, rr, [(D_OUT, HW - 0.1), (D_OUT, 0.0), (D_OUT, -6.0)], 'M_concrete', 'out', (0.7, 0.68, 0.64), None, 4.0)
add_strip(outer, rr, [(0.0, -0.02), (D_OUT, -0.02)], 'M_dark', 'up', (0.3, 0.3, 0.35), None, 4.0)
# sol de la salle lointaine
far = sc.part('Far')
sc.noao.add('Far')
far.add(p_cyl(300, 0.5, 36, cap0=False, cap1=True), 'M_dark', pos=(0, -9.0, 0), tint=(0.4, 0.42, 0.5))
sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5, 'Gallery': 0.5, 'Walls': 0.5}
sc.build(ao_samples=24, ao_dist=3.0, ao_floor=0.45)
print('[tris]', sc.tri_total)
sc.export(OUTDIR + '/arena_reactor.glb')
