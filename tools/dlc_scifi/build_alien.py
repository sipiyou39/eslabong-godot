"""arena_alien.glb — « Planète Rouge » : désert rocheux martien, arches de roche, cristaux, deux lunes, ruines d'une base abandonnée."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_lib import *

G.seed(8202)
rng = np.random.default_rng(8202)

defmat('M_ground', tex=T('alien_ground.jpg'), norm=T('alien_ground_n.png'), emit_tex=T('alien_ground_e.png'), emit_str=1.6, rough=0.9, uv=1, spec=0.3)
defmat('M_rock', tex=T('alien_rock.jpg'), norm=T('alien_rock_n.jpg'), rough=0.92, uv=5.0)
defmat('M_stone', tex=T('alien_stone.jpg'), norm=T('alien_stone_n.jpg'), rough=0.88, uv=4.0)
defmat('M_metal', tex=T('alien_metal.jpg'), norm=T('alien_metal_n.jpg'), rough=0.6, metal=0.45, uv=2.0)
defmat('M_iron', tex=T('alien_iron.jpg'), norm=T('alien_iron_n.jpg'), rough=0.6, metal=0.5, uv=2.0)
defmat('M_sand', tex=T('alien_sand.jpg'), rough=1.0, uv=14.0)
defmat('M_cloth', tex=T('alien_cloth.jpg'), rough=0.95, uv=2.0, double=True)
defmat('M_moon', tex=T('alien_moon.jpg'), emit_tex=T('alien_moon.jpg'), emit_str=0.6, rough=1.0, vcol=True, uv=1.0)
defmat('M_crystal', emit='#34d8c4', emit_str=1.5, rough=0.12, spec=1.0)
defmat('M_crystal_v', emit='#9a5ae0', emit_str=1.3, rough=0.12, spec=1.0)
defmat('M_lamp', emit='#ff9030', emit_str=2.6, vcol=False, color='#ff9030')
defmat('M_glow', emit='#3ad8c8', emit_str=1.2, vcol=False, color='#3ad8c8')
defmat('M_panel', rough=0.3, metal=0.5, spec=0.9)
defmat('M_dark', rough=0.55, metal=0.5)

sc = Scene('arena_alien')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
walls = sc.part('Walls')
build_ground(sc, step=1.0)
L = rr.length()
RED = (1.0, 0.85, 0.78)

# ------------------------------------------------------------------ enceinte : mur de roche + maçonnerie de ruine, portes en arche
GATE_W = 6.8
skip = []
for sx in (1, -1):
    s0 = rr.s_nearest(26.0 * sx, 0.0)
    skip.append((s0 - GATE_W / 2, s0 + GATE_W / 2))
FACE_D = 0.36
build_walls(sc, rr, T=1.5, H=HW, face_d=FACE_D, mats=dict(face='M_rock', panel='M_stone', trim='M_rock', top='M_rock'),
            tints=dict(face=(0.85, 0.68, 0.6), panel=(0.9, 0.78, 0.72), trim=(0.75, 0.58, 0.5), top=(0.82, 0.64, 0.55)), skip=skip, panel_y=1.7, plinth=0.6)
# lits de poussière au pied du mur
add_strip(walls, rr, [(FACE_D + 0.0, 0.5), (0.0, 0.5)], 'M_sand', 'up', (1.0, 0.85, 0.75), skip, 4.0) if False else None

for sx in (1, -1):
    nxz = (float(sx), 0.0)
    pos = (26.0 * sx, 0.0)
    arch_block(walls, pos, nxz, GATE_W, HW, 4.2, 0.7, 1.5, mat='M_stone', tint=(0.9, 0.75, 0.65))
    for sg in (-1, 1):
        cx_, cz_ = local_to_world(pos, nxz, sg * 3.7, 1.3)
        crystal_cluster(dec, cx_, cz_, 0.6, 2.0, rng, n=4, mat='M_crystal', c_lo='#1a8a80', c_hi='#b8fff0', seed=sx * 7 + sg)
    x1, z1 = local_to_world(pos, nxz, 0, 0.1)
    dec.box((4.6, 0.35, 0.5), pos=(x1, 2.75, z1), mat='M_stone', tint=(0.85, 0.7, 0.6), yaw=yaw_of(*nxz), bev=0.04)

# ------------------------------------------------------------------ gradins naturels : terrasses de roche qui montent en cratère
VISTA = [(0.0, 47.0), (L - 4.0, L + 0.1)]
ROWS, D0, TREAD, RISE = 5, 1.5, 1.9, 0.95
tiers, dend, ytop = build_tiers(sc, rr, D0, HW, ROWS, TREAD, RISE, 'M_rock', 'M_rock', tint_tread=(0.92, 0.74, 0.62), tint_riser=(0.7, 0.5, 0.42), skip=VISTA, back=1.0, uv=5.0)
cliff = sc.part('Cliff')
D_C = dend + 1.0
add_strip(cliff, rr, [(D_C, ytop), (D_C, ytop + 4.0), (D_C - 0.6, ytop + 8.0), (D_C - 1.4, ytop + 11.0)], 'M_rock', 'in', (0.66, 0.48, 0.42), VISTA, 5.0,
          vfun=vnoise_f(0.25, 0.5, 4))
add_strip(cliff, rr, [(D_C - 1.4, ytop + 11.0), (D_C + 3.0, ytop + 11.0)], 'M_rock', 'up', (0.95, 0.72, 0.58), VISTA, 5.0)
add_strip(cliff, rr, [(D_C + 3.0, ytop + 11.0), (D_C + 3.0, 0.0)], 'M_rock', 'out', (0.8, 0.58, 0.46), VISTA, 5.0)
# plateau ouvert au fond (-Z) : dalle de sable à hauteur du mur, puis falaise
PL_W = 10.0
add_strip(cliff, rr, [(1.5, HW), (PL_W, HW)], 'M_sand', 'up', (1.0, 0.85, 0.75), [(46.5, L - 3.5)], 8.0)
add_strip(cliff, rr, [(PL_W, HW), (PL_W + 0.3, HW - 1.5), (PL_W + 1.2, HW - 6.0), (PL_W + 2.5, -12.0)], 'M_rock', 'out', (0.85, 0.6, 0.48), [(46.5, L - 3.5)], 5.0,
          vfun=vnoise_f(0.25, 0.6, 9))

# rochers : couronne au sommet du mur, éboulis sur les terrasses, bords de falaise
P, N, Tn, s_ = rr.along(1.7, 0.8, offset=0.4)
pos, siz = [], []
for i in range(len(P)):
    sh = rr.s_nearest(P[i][0], P[i][1])
    if any(a - 1.6 <= sh <= b + 1.6 for a, b in skip):
        continue
    pos.append((P[i][0], HW - 0.15, P[i][1]))
    siz.append((rng.uniform(1.3, 2.2), rng.uniform(0.8, 1.9), rng.uniform(1.3, 2.2)))
boulders(dec, rng, pos, siz, tint=(1.0, 0.8, 0.68))
for k in range(ROWS):
    P, N, Tn, s_ = rr.along(3.2, D0 + k * TREAD + 0.9, offset=rng.uniform(0, 3))
    yk = HW + RISE * (k + 1)
    pos, siz = [], []
    for i in range(len(P)):
        sh = rr.s_nearest(P[i][0], P[i][1])
        if any(a - 1.0 <= sh <= b + 1.0 for a, b in VISTA) or rng.random() < 0.4:
            continue
        pos.append((P[i][0] + rng.uniform(-0.3, 0.3), yk - 0.1, P[i][1] + rng.uniform(-0.3, 0.3)))
        siz.append((rng.uniform(0.7, 1.7), rng.uniform(0.6, 1.5), rng.uniform(0.7, 1.7)))
    boulders(dec, rng, pos, siz, tint=(0.95, 0.72, 0.6))
Pc, Nc, Tc, sc_ = rr.along(2.6, D_C - 0.5, offset=1.0)
pos, siz = [], []
for i in range(len(Pc)):
    sh = rr.s_nearest(Pc[i][0], Pc[i][1])
    if any(a - 1.0 <= sh <= b + 1.0 for a, b in VISTA):
        continue
    pos.append((Pc[i][0], ytop + 10.5 + rng.uniform(-0.5, 1.0), Pc[i][1]))
    siz.append((rng.uniform(2.0, 4.2), rng.uniform(2.0, 5.0), rng.uniform(2.0, 4.2)))
boulders(dec, rng, pos, siz, tint=(0.9, 0.62, 0.5))
# bords du plateau sud
pos, siz = [], []
for x in np.arange(-19, 20, 2.3):
    pos.append((x + rng.uniform(-0.4, 0.4), HW - 0.2, -(16 + PL_W - 0.3) + rng.uniform(-0.5, 0.5)))
    siz.append((rng.uniform(1.4, 2.6), rng.uniform(0.8, 1.8), rng.uniform(1.2, 2.2)))
boulders(dec, rng, pos, siz, tint=(0.95, 0.7, 0.58))
# bastions aux extrémités de la trouée
for sx in (-1, 1):
    for (x, z, w, h) in ((sx * 22.5, -21.0, 6.0, 7.5), (sx * 26.5, -17.0, 5.0, 6.0), (sx * 24.0, -25.5, 5.5, 5.0)):
        dec.rock((w, h, w * 0.9), pos=(x, HW - 0.5, z), mat='M_rock', seed=int(abs(x) * 3 + h), sub=1, tint=(0.9, 0.66, 0.54), yaw=rng.uniform(0, 3))

# cristaux sur les terrasses et le plateau
for (x, z, r, h, c) in [(-21, -19.5, 0.9, 2.6, 0), (20, -20.5, 1.0, 3.0, 1), (-9, -24.0, 0.8, 2.0, 1), (11, -22.5, 0.7, 1.8, 0), (-27.5, 16.5, 0.9, 2.2, 1), (27.0, 17.0, 0.9, 2.4, 0),
                        (-33, 7, 0.8, 2.0, 0), (34, -9, 0.8, 2.2, 1)]:
    y0 = HW if z < -15 else HW + RISE * 2
    if c:
        crystal_cluster(dec, x, z, r, h, rng, n=5, mat='M_crystal_v', c_lo='#4a2a8a', c_hi='#d8b8ff', y0=y0, seed=int(abs(x * z)) % 50)
    else:
        crystal_cluster(dec, x, z, r, h, rng, n=5, mat='M_crystal', c_lo='#1a8a80', c_hi='#b8fff0', y0=y0, seed=int(abs(x * z)) % 50)

# ------------------------------------------------------------------ ruines de la base abandonnée (plateau sud)
ru = sc.part('Ruins')
Y0 = HW


def hab_module(mb, x, z, yaw, length=7.0, r=1.5, broken=True):
    """module d'habitation couché : cylindre de tôle avec bandes, hublots, bout éventré."""
    c, s = math.cos(yaw), math.sin(yaw)
    p0 = np.array([x - c * length / 2, Y0 + r, z + s * length / 2])
    p1 = np.array([x + c * length / 2, Y0 + r, z - s * length / 2])
    cyl_between(mb, p0, p1 - (p1 - p0) * (0.12 if broken else 0.0), r, mat='M_metal', tint=(0.95, 0.9, 0.85), seg=14, caps=False)
    for t in (0.18, 0.5, 0.82):
        q = p0 + (p1 - p0) * t
        cyl_between(mb, q - (p1 - p0) / length * 0.12, q + (p1 - p0) / length * 0.12, r * 1.04, mat='M_iron', tint=(0.8, 0.7, 0.62), seg=14, caps=False)
    for t in (0.34, 0.66):
        q = p0 + (p1 - p0) * t + np.array([-s, 0, -c]) * (r * 0.98) * 0
        mb.add(p_cyl(0.36, 0.06, 10), 'M_dark', pos=(q[0] + (-s) * r * 0.0, q[1] + r * 0.7, q[2] + (-c) * 0.0), tint=(0.5, 0.55, 0.6))
    # capot arrière + éclats
    mb.add(p_sphere(r * 0.98, 12, 5), 'M_metal', pos=tuple(p0), scale=(0.6, 1.0, 1.0) if False else 1.0, tint=(0.9, 0.85, 0.8))
    for k in range(6):
        a = rng.uniform(0, 6.28)
        q = p1 - (p1 - p0) * 0.12
        mb.add(p_box(rng.uniform(0.4, 0.9), 0.05, rng.uniform(0.3, 0.7)), 'M_iron', pos=(q[0] + math.cos(a) * r * 0.9, q[1] + math.sin(a) * r * 0.9, q[2]), yaw=a, roll=rng.uniform(0, 1), tint=(0.8, 0.65, 0.55))


def dome_ruin(mb, x, z, R):
    prof = [(R, Y0), (R * 0.99, Y0 + R * 0.35), (R * 0.9, Y0 + R * 0.65), (R * 0.68, Y0 + R * 0.88), (R * 0.36, Y0 + R * 1.02)]
    mb.lathe(prof, pos=(x, 0, z), mat='M_metal', seg=16, tint=(0.95, 0.9, 0.85), cap0=False, cap1=False, jitter=0.0)
    for k in range(8):
        a = 2 * math.pi * k / 8
        mb.add(p_box(0.16, R * 1.0, 0.16), 'M_iron', pos=(x + math.cos(a) * R * 0.5, Y0 + R * 0.62, z + math.sin(a) * R * 0.5), yaw=-a, roll=-1.0 * math.cos(0) * 0.0, tint=(0.7, 0.6, 0.52)) if False else None
    mb.lathe([(R * 1.04, Y0), (R * 1.04, Y0 + 0.5), (R * 1.0, Y0 + 0.5)], pos=(x, 0, z), mat='M_stone', seg=16, tint=(0.85, 0.7, 0.6))
    mb.box((1.4, 2.0, 0.5), pos=(x + R * 0.9, Y0, z), mat='M_dark', tint=(0.35, 0.3, 0.3), yaw=math.pi / 2)    # porte éventrée


def solar_row(mb, x0, z, n, dx=2.8, tilt=0.45):
    for i in range(n):
        x = x0 + i * dx
        broken = (i % 3 == 1)
        mb.add(p_box(0.12, 1.4, 0.12), 'M_iron', pos=(x, Y0, z), tint=(0.7, 0.6, 0.52))
        mb.add(p_box(2.4, 0.07, 1.5), 'M_panel', pos=(x, Y0 + 1.35, z), pitch=-tilt + (0.5 if broken else 0.0), roll=(0.2 if broken else 0.0), tint=(0.18, 0.2, 0.3))
        mb.add(p_box(2.5, 0.05, 0.05), 'M_iron', pos=(x, Y0 + 1.4, z + 0.62 * math.cos(tilt)), pitch=-tilt, tint=(0.7, 0.6, 0.52))


def dish(mb, x, z, yaw):
    mb.cyl(0.14, 2.2, pos=(x, Y0, z), mat='M_iron', seg=8, tint=(0.75, 0.62, 0.52))
    d = p_lathe([(0.0, 0.0), (0.7, 0.05), (1.3, 0.22), (1.75, 0.5), (1.7, 0.53), (1.25, 0.28), (0.65, 0.11), (0.0, 0.06)], 16, False, False)
    mb.add(d, 'M_metal', pos=(x, Y0 + 2.3, z), pitch=2.0, yaw=yaw, tint=(0.95, 0.9, 0.85))
    mb.cyl(0.04, 1.3, pos=(x, Y0 + 2.4, z), mat='M_iron', seg=5, pitch=0.5, yaw=yaw, tint=(0.75, 0.62, 0.52))


def lamp_post(mb, x, z, h=3.6):
    mb.cyl(0.07, h, pos=(x, Y0, z), mat='M_iron', seg=6, tint=(0.7, 0.6, 0.52))
    mb.add(p_sphere(0.17, 8, 5), 'M_lamp', pos=(x, Y0 + h + 0.15, z))
    mb.lathe([(0.2, Y0 + h - 0.05), (0.18, Y0 + h + 0.15), (0.0, Y0 + h + 0.32)], pos=(x, 0, z), mat='M_iron', seg=8, cap0=False, tint=(0.65, 0.55, 0.48))


hab_module(ru, -12.5, -21.5, 0.12, 7.0, 1.5)
hab_module(ru, 14.0, -19.8, -0.2, 5.0, 1.3)
dome_ruin(ru, 3.0, -23.0, 3.4)
dome_ruin(ru, -22.5, -22.2, 2.2)
solar_row(ru, -8.0, -19.2, 4, 2.8)
solar_row(ru, 17.0, -23.5, 3, 2.8, 0.35)
dish(ru, 22.5, -19.5, 0.5)
dish(ru, -17.5, -19.2, -0.7)
lamp_post(ru, -3.5, -19.0)
lamp_post(ru, 8.5, -19.3)
lamp_post(ru, -19.5, -22.5)
# caisses et fûts épars
for (x, z) in [(-5.5, -20.8), (0.4, -20.0), (6.5, -21.0), (-15.5, -23.5), (11.0, -24.5), (19.0, -21.5)]:
    ru.box((rng.uniform(0.9, 1.4), rng.uniform(0.7, 1.1), rng.uniform(0.9, 1.4)), pos=(x, Y0, z), mat='M_metal', tint=(0.9, 0.82, 0.75), yaw=rng.uniform(0, 3), bev=0.03)
# portique de grue à demi effondré
for sx in (-1, 1):
    ru.box((0.35, 6.0, 0.35), pos=(sx * 5.5, Y0, -26.0), mat='M_iron', tint=(0.7, 0.6, 0.52), top=(0.25, 0.25))
ru.add(p_box(12.4, 0.35, 0.4), 'M_iron', pos=(0, Y0 + 5.4, -26.0), roll=0.12, tint=(0.7, 0.6, 0.52))
ru.add(p_box(0.1, 3.6, 0.1), 'M_iron', pos=(1.4, Y0 + 1.9, -26.0), roll=0.1, tint=(0.7, 0.6, 0.52))
ru.add(p_box(0.9, 0.6, 0.9), 'M_iron', pos=(1.9, Y0 + 1.5, -26.0), tint=(0.7, 0.6, 0.52))
# arches de roche de part et d'autre
rock_arch(dec, -26.0, -30.0, 14.0, 12.0, 3.2, 6.0, 0.35, rng, y0=HW - 0.5, tint=(0.95, 0.68, 0.55))
rock_arch(dec, 27.0, -34.0, 18.0, 15.0, 3.8, 7.0, -0.25, rng, y0=HW - 1.5, tint=(0.9, 0.62, 0.5))

# ------------------------------------------------------------------ torches : lanternes de la base (Torch_xx)
def alien_lamp(md, mf, Fp, n, arm):
    x, y, z = Fp
    nx, nz = n
    yaw = yaw_of(nx, nz)
    wx, wz = x + nx * arm, z + nz * arm
    md.box((0.28, 0.5, 0.1), pos=(wx - nx * 0.04, y - 0.45, wz - nz * 0.04), mat='M_iron', tint=(0.7, 0.62, 0.55), yaw=yaw)
    md.box((0.08, 0.08, arm + 0.04), pos=(x + nx * arm * 0.5, y - 0.2, z + nz * arm * 0.5), mat='M_iron', tint=(0.7, 0.62, 0.55), yaw=yaw)
    md.lathe([(0.1, y - 0.2), (0.16, y - 0.12), (0.17, y + 0.1), (0.1, y + 0.2), (0.0, y + 0.22)], pos=(x, 0, z), mat='M_iron', seg=8, tint=(0.75, 0.65, 0.55))
    mf.lathe([(0.0, y - 0.18), (0.11, y - 0.12), (0.13, y), (0.1, y + 0.12), (0.0, y + 0.16)], pos=(x, 0, z), mat='M_lamp', seg=8, cap0=False, cap1=False)


torches(sc, rr, y=2.2, sconce_fn=alien_lamp)

# ------------------------------------------------------------------ obstacles : pitons rocheux (0,3), cristaux (1,2), amas de roche + balise (4,5)
def spire(mb, x, z, r, h, seed):
    prof = [(r, 0.0), (r * 0.97, 0.6), (r * 0.86, 1.6), (r * 0.74, 2.8), (r * 0.56, 3.8), (r * 0.36, 4.5), (r * 0.12, h * 0.97), (0.0, h)]
    mb.lathe(prof, pos=(x, 0, z), mat='M_rock', seg=8, tint=(0.8, 0.6, 0.52), jitter=0.09, cap0=False, cap1=False, yaw=seed * 0.7, vfun=vgrad(0, h, 0.7, 1.2))
    for k in range(5):
        a = 2 * math.pi * k / 5 + seed
        rr_ = r * 0.74
        mb.add(p_rock(0.9, 0.9, 0.9, seed * 5 + k, 1, flat=0.3, rough=0.3), 'M_rock', pos=(x + rr_ * math.cos(a), 0.0, z + rr_ * math.sin(a)), scale=r * 0.55 / 0.9 * (0.8 + 0.4 * rng.random()),
               tint=(0.85, 0.62, 0.5))


def rock_pile(mb, x, z, r, seed):
    for k in range(7):
        a = 2 * math.pi * k / 7 + seed
        rho = r * 0.62 if k else 0.0
        s = (r * 0.8 if k == 0 else r * 0.5)
        mb.add(p_rock(1.0, 1.0, 1.0, seed * 11 + k, 1, flat=0.25, rough=0.3), 'M_rock', pos=(x + rho * math.cos(a), 0.0, z + rho * math.sin(a)), scale=(s * 1.3, s * (3.0 if k == 0 else 1.5 + 0.4 * rng.random()), s * 1.3),
               tint=(0.9, 0.66, 0.54), yaw=rng.uniform(0, 3))
    cyl_between(mb, (x, 2.9, z), (x, 4.2, z), 0.06, mat='M_iron', tint=(0.7, 0.6, 0.52), seg=5)
    mb.add(p_sphere(0.17, 8, 5), 'M_lamp', pos=(x, 4.3, z))


for i in range(6):
    mb, o = obstacle_part(sc, i)
    if i in (0, 3):
        spire(mb, o['x'], o['z'], o['r'], 5.4 if i == 0 else 4.9, i)
    elif i in (1, 2):
        crystal_cluster(mb, o['x'], o['z'], o['r'], 3.4, rng, n=6, mat='M_crystal' if i == 1 else 'M_crystal_v', c_lo='#1a8a80' if i == 1 else '#4a2a8a',
                        c_hi='#b8fff0' if i == 1 else '#d8b8ff', seed=i * 3)
        mb.add(p_rock(1.0, 1.0, 1.0, 40 + i, 1, flat=0.25, rough=0.3), 'M_rock', pos=(o['x'], 0, o['z']), scale=(o['r'] * 1.9, 0.35, o['r'] * 1.9), tint=(0.85, 0.62, 0.5))
    else:
        rock_pile(mb, o['x'], o['z'], o['r'], i)

# ------------------------------------------------------------------ décor lointain : plaine, mesas, arches, lunes
far = sc.part('Far')
sc.noao.add('Far')
Y_PLAIN = -26.0
far.add(p_cyl(520, 0.5, 40, cap0=False, cap1=True), 'M_sand', pos=(0, Y_PLAIN - 0.5, 0), tint=(1.0, 0.8, 0.68))
for i in range(34):
    a = math.radians(rng.uniform(-170, 170)) - math.pi / 2
    Rr = rng.uniform(90, 300)
    x, z = Rr * math.cos(a), Rr * math.sin(a)
    if float(rr.sdf(np.array(x), np.array(z))) < 60:
        continue
    R_ = rng.uniform(14, 36)
    H_ = rng.uniform(26, 62)
    mesa(far, x, z, R_, H_, seed=i, y0=Y_PLAIN - 1, tint=(0.95, 0.68, 0.54), seg=11)
for (x, z, w, h) in ((-70, -120, 40, 30), (85, -150, 46, 36), (10, -210, 60, 40)):
    rock_arch(far, x, z, w, h, w * 0.22, 14.0, rng.uniform(-0.5, 0.5), rng, y0=Y_PLAIN - 1, tint=(0.92, 0.64, 0.5))
for i in range(40):
    a = rng.uniform(0, 2 * math.pi)
    Rr = rng.uniform(70, 260)
    x, z = Rr * math.cos(a), Rr * math.sin(a)
    if float(rr.sdf(np.array(x), np.array(z))) < 50:
        continue
    far.crystal(rng.uniform(0.8, 1.6), rng.uniform(4, 10), pos=(x, Y_PLAIN - 0.5, z), mat='M_crystal' if i % 2 else 'M_crystal_v', seg=5, seed=i, tip=0.3, tint=(1, 1, 1))
# deux lunes dans le ciel
Vm, Fm, UVm = sphere_uv_mesh(46.0, 40, 22, (-70.0, 105.0, -330.0))
far.add((Vm, Fm), 'M_moon', uv=UVm, tint=(1.0, 0.82, 0.7))
Vm2, Fm2, UVm2 = sphere_uv_mesh(15.0, 30, 16, (120.0, 140.0, -360.0))
far.add((Vm2, Fm2), 'M_moon', uv=UVm2, tint=(0.8, 0.9, 1.0))

sc.ao_opts = {'Ground': 0.7, 'Decor': 0.5, 'Cliff': 0.55, 'Stands': 0.55, 'Ruins': 0.55}
sc.build(ao_samples=24, ao_dist=3.0, ao_floor=0.45)
print('[tris]', sc.tri_total)
sc.export(OUTDIR + '/arena_alien.glb')
