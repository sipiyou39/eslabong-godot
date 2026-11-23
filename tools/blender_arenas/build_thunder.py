"""arena_thunder.glb — « Chaos Thunder » : plateforme runique flottant dans un ciel d'orage, obélisques tesla, îles de roche, anneaux d'énergie."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_common import *

T = lambda n: TEXDIR + '/' + n
G.seed(505)
rng = np.random.default_rng(505)

defmat('M_ground', tex=T('thunder_ground.png'), norm=T('thunder_ground_n.png'), emit_tex=T('thunder_ground_e.png'), emit_str=1.9, rough=0.5, metal=0.2, uv=1, norm_str=1.0, spec=0.6)
defmat('M_stone', tex=T('thunder_stone.png'), norm=T('thunder_stone_n.png'), rough=0.7, uv=4.0, spec=0.5)
defmat('M_metal', tex=T('thunder_metal.png'), norm=T('thunder_metal_n.png'), rough=0.4, metal=0.7, uv=2.0)
defmat('M_obsidian', tex=T('thunder_obsidian.png'), norm=T('thunder_obsidian_n.png'), rough=0.18, metal=0.2, uv=4.0, spec=1.0)
defmat('M_rock', tex=T('thunder_rock.png'), norm=T('thunder_rock_n.png'), rough=0.9, uv=8.0)
defmat('M_rune', tex=T('thunder_rune.png'), emit_tex=T('thunder_rune_e.png'), emit_str=2.2, rough=0.4, uv=2.0)
defmat('M_energy', emit='#6ad8ff', emit_str=2.4, vcol=False, color='#6ad8ff')
defmat('M_energy_v', emit='#b46bff', emit_str=2.4, vcol=False, color='#b46bff')
defmat('M_crystal', emit='#9a5cff', emit_str=1.6, rough=0.1, spec=1.0)
defmat('M_crystal_c', emit='#4fd0ff', emit_str=1.6, rough=0.1, spec=1.0)
defmat('M_flame', emit='#a974ff', emit_str=3.0, vcol=False, color='#a974ff')
defmat('M_glow', emit='#5ac8ff', emit_str=1.0, vcol=False, color='#5ac8ff')
defmat('M_cloth', tex=T('thunder_cloth.png'), rough=0.8, uv=2.0, double=True)
defmat('M_bronze', tex=T('thunder_metal.png'), norm=T('thunder_metal_n.png'), rough=0.35, metal=0.9, uv=2.0)
defmat('M_gold', rough=0.3, metal=0.9)
defmat('M_dark', rough=0.5, metal=0.5)
defmat('M_crowd', rough=0.9)
defmat('M_dirt', tex=T('thunder_rock.png'), rough=1.0, uv=10.0)
defmat('M_roof', tex=T('thunder_metal.png'), rough=0.4, metal=0.8, uv=2.0)

OBS = (0.7, 0.7, 0.9)
sc = Scene('arena_thunder')
rr = RR(step=1.0)
HW = LAYOUT['wall_height']
dec = sc.part('Decor')
walls = sc.part('Walls')
build_ground(sc, step=0.6)

GATE_W = 6.8
skip = []
for sx in (1, -1):
    s0 = rr.s_nearest(26.0 * sx, 0.0)
    skip.append((s0 - GATE_W / 2, s0 + GATE_W / 2))
FACE_D = 0.36
build_walls(sc, rr, T=1.5, H=HW, face_d=FACE_D, mats=dict(face='M_obsidian', panel='M_stone', trim='M_metal', top='M_metal'),
            tints=dict(panel=(0.9, 0.9, 1.0), face=(0.9, 0.9, 1.0), trim=(0.75, 0.75, 0.9), top=(0.7, 0.7, 0.85)), skip=skip, panel_y=1.8)
# conduits d'énergie et panneaux runiques
add_strip(walls, rr, [(FACE_D - 0.02, 1.8), (FACE_D - 0.02, 1.9)], 'M_energy', 'in', (1, 1, 1), skip, 4.0)
add_strip(walls, rr, [(0.0, HW - 0.02), (0.75, HW - 0.02)], 'M_stone', 'up', (1, 1, 1), skip, 4.0) if False else None
add_strip(walls, rr, [(0.7, HW + 0.01), (0.78, HW + 0.01)], 'M_energy_v', 'up', (1, 1, 1), skip, 4.0)
L = rr.length()
rs = list(skip)
s_ = 0.0
while s_ < L:
    rs.append((s_ + 3.0, s_ + 6.0))
    s_ += 6.0
add_strip(walls, rr, [(FACE_D - 0.02, 0.75), (FACE_D - 0.02, 1.7)], 'M_rune', 'in', (1, 1, 1), rs, 2.0)

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
pilasters_on_wall(dec, rr, pil, FACE_D, HW, 'M_obsidian', (0.8, 0.8, 1.0), cap_mat='M_metal', cap_tint=(0.7, 0.7, 0.9), w=0.72)
for (x, z) in pil:
    s_ = rr.s_nearest(x, z)
    P, n = rr.at_base(s_)
    c = P + n * 0.2
    dec.box((0.07, HW - 1.2, 0.04), pos=(c[0] - n[0] * 0.0 - 0.0, 0.6, c[1]), mat='M_energy', tint=(1, 1, 1), yaw=yaw_of(n[0], n[1])) if False else None

# portails d'énergie aux extrémités
for sx in (1, -1):
    nxz = (float(sx), 0.0)
    pos = (26.0 * sx, 0.0)
    yaw = yaw_of(*nxz)
    arch_block(walls, pos, nxz, GATE_W, HW, 4.2, 0.7, 1.5, mat='M_obsidian', tint=(0.8, 0.8, 1.0), glow_mat='M_energy_v')
    x1, z1 = local_to_world(pos, nxz, 0, 0.12)
    dec.add(p_torus(2.2, 0.08, 20, 5), 'M_energy', pos=(x1, 0.7, z1), yaw=yaw, pitch=math.pi / 2, tint=(1, 1, 1))
    for sg in (-1, 1):
        cx_, cz_ = local_to_world(pos, nxz, sg * 3.0, 0.6)
        crystal_cluster(dec, cx_, cz_, 0.7, 2.6, rng, n=4, mat='M_crystal', c_lo='#6a3ad0', c_hi='#d9b8ff', seed=sx * 5 + sg)

# ------------------------------------------------------------------ terrasses (sans foule)
ROWS = 7
D0, TREAD, RISE, Y0 = 1.5, 1.0, 0.55, HW
tiers, dend, ytop = build_tiers(sc, rr, D0, Y0, ROWS, TREAD, RISE, 'M_stone', 'M_obsidian', tint_tread=(0.8, 0.8, 0.95), tint_riser=(0.7, 0.7, 0.9),
                                back=1.4)
stands = sc.part('Stands')
for k in range(ROWS):
    dk = D0 + k * TREAD
    yk = Y0 + RISE * (k + 1)
    if k % 2 == 0:
        add_strip(stands, rr, [(dk - 0.01, yk - 0.12), (dk - 0.01, yk - 0.04)], 'M_energy' if k % 4 == 0 else 'M_energy_v', 'in', (1, 1, 1), None, 4.0)
D_ARC = dend + 1.4
# lanternes d'énergie flottantes sur les terrasses
for k in (1, 3, 5):
    P, N, T_, s = rr.along(3.4, D0 + k * TREAD + 0.55, offset=k * 0.7)
    yk = Y0 + RISE * (k + 1)
    for i in range(len(P)):
        c_ = ('M_crystal', '#7a46e8', '#d6b6ff') if (i + k) % 2 == 0 else ('M_crystal_c', '#2a90d0', '#c6f1ff')
        dec.box((0.2, 0.9, 0.2), pos=(P[i][0], yk, P[i][1]), mat='M_metal', tint=(0.5, 0.5, 0.65), top=(0.1, 0.1)) if False else None
        dec.crystal(0.14, 0.62, pos=(P[i][0], yk + 0.9 + 0.1 * math.sin(i * 1.7), P[i][1]), mat=c_[0], seg=4, seed=i, tip=0.4, tint=c_[2], yaw=i * 0.7)
        dec.add(p_cone(0.1, 0.4, 4), c_[0], pos=(P[i][0], yk + 0.5 + 0.1 * math.sin(i * 1.7), P[i][1]), pitch=math.pi, tint=c_[2])
solid_ring(sc, rr, 'Stands', D_ARC, D_ARC + 1.3, 0.0, ytop, 'M_stone', tint=(0.7, 0.7, 0.9), inner=False, top=False)

# ------------------------------------------------------------------ façade : travées + pylônes tesla
Yp = ytop
ARC_H = 4.6
pier = arcade_ring(sc, rr, 'Decor', D_ARC, Yp, ARC_H, bay=3.7, open_ratio=0.6, spring=2.2, depth=1.3, mat='M_obsidian', tint=(0.8, 0.8, 1.0),
                   glow_mat='M_glow', glow_every=2)
solid_ring(sc, rr, 'Decor', D_ARC - 0.15, D_ARC + 1.6, Yp + ARC_H, Yp + ARC_H + 0.5, 'M_metal', tint=(0.7, 0.7, 0.9), inner=True, top=True, outer=True)
add_strip(dec, rr, [(D_ARC - 0.2, Yp + ARC_H + 0.18), (D_ARC - 0.2, Yp + ARC_H + 0.3)], 'M_energy', 'in', (1, 1, 1), None, 4.0)
ytop_arc = Yp + ARC_H + 0.5
tops = []
for i, (mid, nrm, wd, p0) in enumerate(pier):
    x, z = p0[0] + nrm[0] * 0.65, p0[1] + nrm[1] * 0.65
    h = 8.5 if i % 2 == 0 else 13.0
    yaw = yaw_of(nrm[0], nrm[1])
    # pylône effilé
    dec.box((1.0, h, 1.0), pos=(x, ytop_arc, z), mat='M_obsidian', tint=(0.75, 0.75, 1.0), top=(0.42, 0.42), yaw=yaw + math.pi / 4, bev=0.04)
    dec.box((1.25, 0.35, 1.25), pos=(x, ytop_arc, z), mat='M_metal', tint=(0.6, 0.6, 0.8), yaw=yaw + math.pi / 4, bev=0.03)
    dec.add(p_cone(0.3, 0.9, 4), 'M_obsidian', pos=(x, ytop_arc + h, z), tint=(0.75, 0.75, 1.0), yaw=yaw + math.pi / 4)
    # panneau runique
    dec.add(p_box(0.55, h * 0.6, 0.02), 'M_rune', pos=(x - nrm[0] * 0.0 + nrm[0] * (-0.46 + 0.0), ytop_arc + 0.9, z + nrm[1] * (-0.46)), yaw=yaw) if False else None
    # gemme flottante + anneau
    cc = ('M_crystal', '#7a46e8', '#d6b6ff') if i % 2 == 0 else ('M_crystal_c', '#2a90d0', '#c6f1ff')
    dec.crystal(0.32, 1.2, pos=(x, ytop_arc + h + 1.2, z), mat=cc[0], seg=4, tip=0.5, tint=cc[2])
    dec.add(p_cone(0.32, 0.8, 4), cc[0], pos=(x, ytop_arc + h + 1.2, z), pitch=math.pi, tint=cc[2])
    dec.add(p_torus(0.75, 0.04, 16, 4), 'M_energy' if i % 2 else 'M_energy_v', pos=(x, ytop_arc + h + 1.8, z), tint=(1, 1, 1))
    tops.append((x, ytop_arc + h + 0.8, z))
# arcs électriques entre sommets
for i in range(len(tops)):
    a, b = np.array(tops[i]), np.array(tops[(i + 1) % len(tops)])
    if np.linalg.norm(a - b) > 8:
        continue
    pts = [a]
    n_ = 4
    for k in range(1, n_):
        t = k / n_
        p = a + (b - a) * t + np.array([rng.uniform(-0.3, 0.3), rng.uniform(-0.6, 0.6), rng.uniform(-0.3, 0.3)])
        pts.append(p)
    pts.append(b)
    for k in range(len(pts) - 1):
        p0, p1 = pts[k], pts[k + 1]
        d = p1 - p0
        Ls = np.linalg.norm(d)
        yaw = math.atan2(d[0], d[2])
        pitch = -math.atan2(d[1], math.hypot(d[0], d[2]))
        dec.add(p_box(0.07, 0.07, Ls), 'M_energy' if i % 2 else 'M_energy_v', pos=(p0 + p1) / 2 - np.array([0, 0.035, 0]), yaw=yaw, pitch=pitch, tint=(1, 1, 1))
li = 1
for sx in (-1, 1):
    for sz in (-1, 1):
        a = math.radians(45)
        px, pz = sx * (21.0 + (5 + 9.0) * math.cos(a)), sz * (11.0 + (5 + 9.0) * math.sin(a))
        sc.empty(f'Light_{li:02d}', px, ytop_arc + 12, pz)
        li += 1

# bannières
bi = 1
for x in (-21, -15, -9, -3, 3, 9, 15, 21):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, -(16 + 0.2)), math.pi, 1.5, 2.0, '#3a2f66', '#6ad8ff', '#b46bff', phase=bi, mat='M_cloth', rod_mat='M_metal', rod_tint=(0.6, 0.6, 0.8))
    bi += 1
for x in (-18, -6, 6, 18):
    banner_object(sc, f'Banner_{bi:02d}', (x, 2.7, 16 + 0.2), 0.0, 1.5, 2.0, '#2a2152', '#b46bff', '#6ad8ff', phase=bi, mat='M_cloth', rod_mat='M_metal', rod_tint=(0.6, 0.6, 0.8))
    bi += 1


def tesla_lamp(md, mf, Fp, n, arm):
    x, y, z = Fp
    yaw = yaw_of(n[0], n[1])
    wx, wz = x + n[0] * arm, z + n[1] * arm
    md.box((0.3, 0.6, 0.08), pos=(wx - n[0] * 0.02, y - 0.5, wz - n[1] * 0.02), mat='M_metal', tint=(0.5, 0.5, 0.7), yaw=yaw, bev=0.02)
    md.box((0.07, 0.07, arm + 0.08), pos=(x + n[0] * arm * 0.5, y - 0.3, z + n[1] * arm * 0.5), mat='M_metal', tint=(0.5, 0.5, 0.7), yaw=yaw)
    md.lathe([(0.06, y - 0.38), (0.1, y - 0.28), (0.2, y - 0.2), (0.12, y - 0.12)], pos=(x, 0, z), mat='M_metal', seg=8, tint=(0.5, 0.5, 0.7))
    md.add(p_torus(0.22, 0.025, 12, 4), 'M_metal', pos=(x, y - 0.05, z), tint=(0.6, 0.6, 0.8))
    mf.sphere(0.2, pos=(x, y + 0.1, z), mat='M_flame', nu=8, nv=4)
    mf.add(p_cone(0.08, 0.7, 5), 'M_flame', pos=(x, y + 0.25, z))


torches(sc, rr, y=2.2, sconce_fn=tesla_lamp)

# ------------------------------------------------------------------ obstacles : obélisques à runes
for i in range(6):
    mb, o = obstacle_part(sc, i)
    r = o['r']
    x, z = o['x'], o['z']
    h = [3.7, 3.4, 3.9, 3.6, 3.2, 3.5][i]
    ya = 0.35 * i
    # socle octogonal (sommets exactement au rayon r)
    mb.lathe([(r, 0), (r, 0.28), (r * 0.9, 0.42), (r * 0.78, 0.5)], pos=(x, 0, z), mat='M_metal', seg=8, tint=(0.55, 0.55, 0.75), phase=0.0) if False else \
        mb.add(p_lathe([(r, 0), (r, 0.28), (r * 0.9, 0.42), (r * 0.78, 0.5)], 8, True, True, phase=math.pi / 8), 'M_metal', pos=(x, 0, z), tint=(0.55, 0.55, 0.75))
    mb.add(p_lathe([(r * 0.98, 0.0), (r * 1.0, 0.04)], 8, False, False, phase=math.pi / 8), 'M_energy' if i % 2 else 'M_energy_v', pos=(x, 0.26, z), tint=(1, 1, 1))
    # fût effilé à section carrée tournée de 45°
    s0 = r * 1.15
    shaft_h = h - 0.9
    mb.box((s0, shaft_h, s0), pos=(x, 0.5, z), mat='M_obsidian', tint=(0.75, 0.75, 1.0), top=(s0 * 0.55, s0 * 0.55), yaw=math.pi / 4 + ya * 0.2, bev=0.04)
    mb.add(p_cone(s0 * 0.4, 0.5, 4), 'M_obsidian', pos=(x, 0.5 + shaft_h, z), yaw=math.pi / 4 + ya * 0.2 + 0.0, tint=(0.75, 0.75, 1.0))
    # panneaux runiques sur les 4 faces
    for k in range(4):
        a = math.pi / 4 + ya * 0.2 + k * math.pi / 2
        # normale de la face : angle a - pi/4 + pi/4 ... les faces d'un carré yawé de a0 sont orientées à a0 + k*pi/2 (+ pi/4 de décalage des coins)
        fa = math.pi / 4 + ya * 0.2 + k * math.pi / 2
        # direction normale (cos(fa - pi/4), sin(fa - pi/4)) en coordonnées XZ après rotation yaw
        yawf = math.pi / 4 + ya * 0.2
        # +Z local tourné par yawf donne (sin yawf, cos yawf) ; faces à +Z, +X, -Z, -X
        loc = [(0, 1), (1, 0), (0, -1), (-1, 0)][k]
        c_, s_ = math.cos(yawf), math.sin(yawf)
        nx_ = loc[1] * s_ + loc[0] * c_ if False else (loc[0] * c_ + loc[1] * s_, -loc[0] * s_ + loc[1] * c_)[0]
        # +X local -> (cos yaw, -sin yaw) ; +Z local -> (sin yaw, cos yaw)
        fx = loc[0] * c_ + loc[1] * s_
        fz = -loc[0] * s_ + loc[1] * c_
        hw0 = s0 / 2
        off = hw0 + 0.02
        py = 0.5 + shaft_h * 0.42
        ph = shaft_h * 0.62
        pw = s0 * 0.5
        mb.add(p_box(pw, ph, 0.03, top=(pw * 0.82, 0.03)), 'M_rune', pos=(x + fx * off * 0.93, py - ph / 2 + shaft_h * 0.0, z + fz * off * 0.93), yaw=math.atan2(fx, fz), tint=(1, 1, 1),
               uv=None)
    # gemme flottante + anneaux d'énergie
    gy = 0.5 + shaft_h + 0.5 + 0.1
    cc = ('M_crystal', '#7a46e8', '#d6b6ff') if i % 2 == 0 else ('M_crystal_c', '#2a90d0', '#c6f1ff')
    mb.crystal(0.28, 0.9, pos=(x, gy + 0.2, z), mat=cc[0], seg=4, tip=0.5, tint=cc[2])
    mb.add(p_cone(0.28, 0.6, 4), cc[0], pos=(x, gy + 0.2, z), pitch=math.pi, tint=cc[2])
    mb.add(p_torus(0.62, 0.035, 18, 4), 'M_energy' if i % 2 else 'M_energy_v', pos=(x, gy + 0.35, z), pitch=0.35, tint=(1, 1, 1))
    mb.add(p_torus(0.5, 0.03, 16, 4), 'M_energy_v' if i % 2 else 'M_energy', pos=(x, gy + 0.7, z), pitch=-0.3, yaw=0.8, tint=(1, 1, 1))

# ------------------------------------------------------------------ dessous de la plateforme + îles flottantes
far = dec
solid_ring(sc, rr, 'Decor', D_ARC + 1.3, D_ARC + 1.3, -9.0, 0.0, 'M_rock', tint=(0.5, 0.5, 0.65), inner=False, top=False, outer=True)
# grand plateau octogonal runique sous l'ensemble (visible dans les vues larges)
oct_pts = [(52 * math.cos(math.pi / 8 + k * math.pi / 4), 52 * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
far.add(p_extrude_xz(oct_pts, -13.5, -11.5), 'M_metal', tint=(0.55, 0.55, 0.75))
for (R_, mat_, w_) in ((51.2, 'M_energy', 0.7), (46.0, 'M_energy_v', 0.5)):
    for k in range(8):
        a0 = math.pi / 8 + k * math.pi / 4
        a1 = a0 + math.pi / 4
        p0 = (R_ * math.cos(a0), R_ * math.sin(a0))
        p1 = (R_ * math.cos(a1), R_ * math.sin(a1))
        Lk = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        far.add(p_box(Lk, 0.16, w_), mat_, pos=((p0[0] + p1[0]) / 2, -11.45, (p0[1] + p1[1]) / 2), yaw=math.atan2(-(p1[1] - p0[1]), (p1[0] - p0[0])), tint=(1, 1, 1))
# racine de roche sous la plateforme (ellipsoïde pointu)
far.add(p_lathe([(30.0, 0.0), (29.0, -6), (24, -14), (17, -24), (10, -36), (4, -48), (0, -56)], 14, False, False, jitter=0.07), 'M_rock', pos=(0, -9.0, 0),
        scale=(1.28, 1.0, 0.95), tint=(0.42, 0.4, 0.55))
for k in range(18):
    a = rng.uniform(0, 2 * math.pi)
    rr_ = rng.uniform(10, 26)
    far.crystal(rng.uniform(0.7, 1.6), rng.uniform(5, 14), pos=(rr_ * math.cos(a) * 1.25, -14 - rng.uniform(0, 16), rr_ * math.sin(a) * 0.9), mat='M_crystal',
                seed=k, seg=5, tip=0.35, tint=(0.5, 0.35, 0.9), pitch=math.pi + rng.uniform(-0.2, 0.2))

# îles
for i in range(22):
    a = 2 * math.pi * i / 22 + rng.uniform(-0.2, 0.2)
    R = rng.uniform(62, 120)
    cx, cz = R * math.cos(a), R * math.sin(a)
    cy = rng.uniform(-18, 26)
    rad = rng.uniform(5, 15)
    th = rng.uniform(1.2, 2.6)
    far.add(p_lathe([(0.0, 0.0), (rad * 0.92, 0.0), (rad, -th * 0.4), (rad * 0.9, -th), (rad * 0.6, -th - rad * 0.5), (rad * 0.3, -th - rad * 1.2), (0.0, -th - rad * rng.uniform(1.4, 2.2))], 10, False, False, jitter=0.1),
            'M_rock', pos=(cx, cy, cz), tint=(0.5, 0.48, 0.62))
    far.add(p_lathe([(0.0, 0.0), (rad * 0.92, 0.0)], 10, False, True), 'M_stone', pos=(cx, cy + 0.02, cz), tint=(0.7, 0.7, 0.95)) if False else None
    far.add(p_cyl(rad * 0.97, 0.12, 10, cap0=False, cap1=True), 'M_stone', pos=(cx, cy - 0.02, cz), tint=(0.55, 0.55, 0.75))
    # anneau runique
    far.add(p_torus(rad * 0.7, 0.07, 28, 4), 'M_energy' if i % 2 else 'M_energy_v', pos=(cx, cy + 0.2, cz), tint=(1, 1, 1))
    k_ = i % 3
    if k_ == 0:
        far.box((1.4, rng.uniform(5, 9), 1.4), pos=(cx, cy, cz), mat='M_obsidian', tint=(0.7, 0.7, 1.0), top=(0.6, 0.6), yaw=rng.uniform(0, 3), bev=0.03)
        far.crystal(0.35, 1.2, pos=(cx, cy + 10.5, cz), mat='M_crystal', seg=4, tip=0.5, tint=(0.8, 0.65, 1.0))
    elif k_ == 1:
        crystal_cluster(far, cx, cz, min(rad * 0.4, 3.0), rng.uniform(5, 11), rng, n=5, mat='M_crystal_c', c_lo='#2a78b8', c_hi='#c6f1ff', y0=cy, seed=i)
    else:
        # arche en ruine
        far.box((1.0, 6.0, 1.2), pos=(cx - 2.2, cy, cz), mat='M_stone', tint=(0.6, 0.6, 0.85))
        far.box((1.0, 4.0, 1.2), pos=(cx + 2.2, cy, cz), mat='M_stone', tint=(0.6, 0.6, 0.85))
        far.box((5.6, 0.9, 1.2), pos=(cx - 0.3, cy + 5.2, cz), mat='M_stone', tint=(0.6, 0.6, 0.85), yaw=0.0)
    # faisceau d'énergie vers le ciel / chaîne entre îles
    if i % 4 == 0:
        far.add(p_cyl(0.12, rng.uniform(20, 45), 6), 'M_energy', pos=(cx, cy, cz))
# rochers satellites
for i in range(60):
    a = rng.uniform(0, 2 * math.pi)
    R = rng.uniform(48, 130)
    cx, cz = R * math.cos(a), R * math.sin(a)
    cy = rng.uniform(-25, 35)
    s = rng.uniform(1.5, 5)
    far.rock((s * 1.4, s, s * 1.4), pos=(cx, cy, cz), mat='M_rock', seed=i, sub=1, tint=(0.5, 0.48, 0.62))
# anneaux d'énergie lointains
for k in range(4):
    a = 2 * math.pi * k / 4 + 0.6
    far.add(p_torus(rng.uniform(22, 36), 0.18, 56, 4), 'M_energy' if k % 2 else 'M_energy_v',
            pos=(95 * math.cos(a), rng.uniform(8, 30), 95 * math.sin(a)), pitch=rng.uniform(0.9, 1.4), yaw=rng.uniform(0, 3), tint=(1, 1, 1))

sc.ao_opts = {'Ground': 0.72, 'Decor': 0.5}
sc.build(ao_samples=40, ao_dist=3.0, ao_floor=0.45)
sc.export(OUTDIR + '/arena_thunder.glb')
