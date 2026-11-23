"""club_hall.glb — salle du club de mercenaires (hub / scène de menu), ~28x20 m, plafond voûté ouvert côté caméra (-Z)."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_common import *
class TC:
    CW, CH = 2048, 1472
    CX0, CX1 = -14.0, 14.0
    CMPP = (CX1 - CX0) / CW
    CZ0 = -(CH * CMPP) / 2
    CZ1 = (CH * CMPP) / 2


T = lambda n: TEXDIR + '/' + n
G.seed(606)
rng = np.random.default_rng(606)

defmat('M_ground', tex=T('club_floor.png'), norm=T('club_floor_n.png'), rough=0.75, uv=1, norm_str=0.8, spec=0.3)
defmat('M_stone', tex=T('club_stone.png'), norm=T('club_stone_n.png'), rough=0.88, uv=4.0)
defmat('M_marble', tex=T('club_marble.png'), norm=T('club_marble_n.png'), rough=0.6, uv=4.0, spec=0.5)
defmat('M_wood', tex=T('club_wood.png'), rough=0.75, uv=4.0)
defmat('M_wood_l', tex=T('club_wood_light.png'), rough=0.6, uv=4.0)
defmat('M_iron', tex=T('club_iron.png'), norm=T('club_iron_n.png'), rough=0.55, metal=0.6, uv=2.0)
defmat('M_bronze', tex=T('club_iron.png'), rough=0.4, metal=0.85, uv=2.0)
defmat('M_gold', rough=0.3, metal=0.9)
defmat('M_cloth', tex=T('club_cloth.png'), rough=0.9, uv=2.0, double=True)
defmat('M_burlap', tex=T('club_burlap.png'), rough=1.0, uv=1.0)
defmat('M_plaster', tex=T('club_plaster.png'), rough=0.9, uv=4.0)
defmat('M_rock', tex=T('club_rock.png'), rough=1.0, uv=8.0)
defmat('M_map', tex=T('club_map.png'), rough=0.75, uv=1.0, vcol=True)
defmat('M_roof', tex=T('club_rock.png'), rough=0.9, uv=6.0)
defmat('M_dark', rough=0.9)
defmat('M_steel', rough=0.3, metal=0.9, spec=0.7)
defmat('M_flame', emit='#ff7a1c', emit_str=2.8, vcol=False, color='#ff7a1c')
defmat('M_glow', emit='#ffb050', emit_str=0.8, vcol=False, color='#ffb050')
defmat('M_window', emit='#e8e4d8', emit_str=0.9, vcol=False, color='#e8e4d8')
defmat('M_ray', tex=T('club_ray.png'), emit='#ffd890', emit_str=0.9, alpha=True, vcol=False, double=True, rough=1.0)
defmat('M_crowd', rough=0.9)
defmat('M_dirt', tex=T('club_rock.png'), rough=1.0, uv=10.0)

WOODT = (0.8, 0.7, 0.6)
STT = (1.0, 0.95, 0.9)
GOLDT = (0.9, 0.68, 0.25)
IRT = (0.45, 0.45, 0.5)
RED = '#8c1f26'
GOLD = '#d4a53a'

sc = Scene('club_hall')
dec = sc.part('Decor')
walls = sc.part('Walls')
fx = sc.part('DecorFX')
sc.noao = {'DecorFX'}
sc.join_fx = ('DecorFX', 'Decor')
stands = sc.part('Stands')

# ------------------------------------------------------------------ sol
V, F = p_grid(-14.0, TC.CZ0, 14.0, TC.CZ1, 28, 20, 0.0)
nx_, nz_ = 28, 20
UV = np.stack([(V[:, 0] - TC.CX0) / (TC.CX1 - TC.CX0), 1.0 - (V[:, 2] - TC.CZ0) / (TC.CZ1 - TC.CZ0)], 1)
sc.part('Ground').add((V, F), 'M_ground', uv=UV)
# prolongement sous les murs (invisible)
sc.part('Ground').add(p_box(32, 0.3, 24), 'M_stone', pos=(0, -0.32, 0.5), tint=(0.5, 0.5, 0.5))
# marches avant (côté ouvert)
dec.box((30, 0.3, 1.2), pos=(0, -0.3, -10.4), mat='M_stone', tint=STT)

# ------------------------------------------------------------------ murs (baies à fenêtres hautes)
WALL_H = 8.0
T_W = 1.2
SILL = 2.2
WIN_OW = 1.9
WIN_H = WALL_H - SILL
WIN_SPR = 3.0


def bay(pos, nxz, W):
    arch_block(walls, pos, nxz, W, WIN_H, WIN_OW, WIN_SPR, T_W, mat='M_stone', y0=SILL, tint=STT, glow_mat='M_window', jit=0.03)
    x1, z1 = local_to_world(pos, nxz, 0, 0.6)
    yaw = yaw_of(*nxz)
    # allège pleine sous la fenêtre
    walls.add(p_box(W, SILL, T_W), 'M_stone', pos=local_to_world(pos, nxz, 0, T_W / 2) and (pos[0] + nxz[0] * T_W / 2, 0, pos[1] + nxz[1] * T_W / 2), yaw=yaw, tint=STT)
    # meneaux
    walls.add(p_box(0.07, WIN_H * 0.7, 0.12), 'M_iron', pos=(x1, SILL, z1), yaw=yaw, tint=IRT)
    for yy in (SILL + 1.3, SILL + WIN_SPR - 0.0, SILL + 2.0):
        walls.add(p_box(WIN_OW, 0.07, 0.12), 'M_iron', pos=(x1, yy, z1), yaw=yaw, tint=IRT)
    # encadrement en relief
    fz = 0.0
    return


for zc in (-7.5, -2.5, 2.5, 7.5):
    bay((-14.0, zc), (-1.0, 0.0), 5.0)
    bay((14.0, zc), (1.0, 0.0), 5.0)
for xc in (-11.5, -6.5, 6.5, 11.5):
    bay((xc, 10.0), (0.0, 1.0), 5.0)
# piles d'angle côté ouvert
for sx in (-1, 1):
    walls.box((1.8, WALL_H + 0.4, 1.8), pos=(sx * 14.6, 0, -10.3), mat='M_stone', tint=STT, bev=0.05)
    walls.box((2.1, 0.5, 2.1), pos=(sx * 14.6, WALL_H - 0.6, -10.3), mat='M_marble', tint=STT, bev=0.05)
    walls.box((2.1, 0.5, 2.1), pos=(sx * 14.6, 0, -10.3), mat='M_marble', tint=STT, bev=0.05)
# murs de fond au-dessus du mur gouttereau
walls.add(p_box(31.0, 0.4, 1.5), 'M_stone', pos=(0, WALL_H, 10.6), tint=STT)

# lambris
for (c, ln, yawv, off) in (((-13.88, 0.0), 20.0, math.pi / 2, 0), ((13.88, 0.0), 20.0, math.pi / 2, 0)):
    walls.add(p_box(ln, 1.7, 0.1), 'M_wood', pos=(c[0], 0.0, c[1]), yaw=yawv, tint=WOODT)
    walls.add(p_box(ln, 0.08, 0.16), 'M_wood_l', pos=(c[0] + (0.03 if c[0] < 0 else -0.03), 1.7, c[1]), yaw=yawv, tint=WOODT)
walls.add(p_box(28.0, 1.7, 0.1), 'M_wood', pos=(0, 0.0, 9.88), tint=WOODT)
walls.add(p_box(28.0, 0.08, 0.16), 'M_wood_l', pos=(0, 1.7, 9.86), tint=WOODT)

# ------------------------------------------------------------------ voûte
VA, VB = 14.0, 5.5


def ell(n=28, a=VA, b=VB, y0=WALL_H):
    th = np.linspace(0, math.pi, n + 1)
    return np.stack([-a * np.cos(th), y0 + b * np.sin(th)], 1)


def vault_surface(z0, z1, a, b, nz, inward=True, mat='M_plaster', tint=(1, 1, 1), part=walls, uvs=4.0):
    pts = ell(28, a, b)
    zs = np.linspace(z0, z1, nz + 1)
    Vv = np.array([(x, y, z) for z in zs for (x, y) in pts], float)
    n = len(pts)
    F = []
    for j in range(nz):
        for i in range(n - 1):
            a0 = j * n + i
            F.append((a0, a0 + 1, a0 + n + 1, a0 + n))
    # orientation : normale au sommet doit pointer vers le bas si inward
    k = (nz // 2) * 0 * n + (n // 2)
    f = F[n // 2 - 1]
    nm = np.cross(Vv[f[1]] - Vv[f[0]], Vv[f[3]] - Vv[f[0]])
    want = -1 if inward else 1
    if nm[1] * want < 0:
        F = [tuple(reversed(ff)) for ff in F]
    part.add((Vv, F), mat, tint=tint)


vault_surface(-4.0, 11.2, VA, VB, 10, True, 'M_plaster', (1.0, 0.93, 0.8))
vault_surface(-4.0, 11.2, VA + 0.55, VB + 0.55, 10, False, 'M_roof', (0.8, 0.55, 0.45))
# frontons de la voûte (mur du fond)
pts = [tuple(p) for p in ell(28)]
walls.add(p_extrude_xy(pts, 10.0, 11.2), 'M_stone', tint=STT)
# nervures
for z in (-10.0, -6.0, -2.0, 2.0, 6.0, 9.6):
    inner = ell(28, VA, VB)
    outer = ell(28, VA + 0.6, VB + 0.6)
    poly = [tuple(p) for p in inner] + [tuple(p) for p in outer[::-1]]
    walls.add(p_extrude_xy(poly, z - 0.3, z + 0.3), 'M_stone', tint=(0.95, 0.9, 0.82))
# poutres de liaison
for z in (-6.0, 2.0, 6.0):
    walls.add(p_box(28.0, 0.35, 0.4), 'M_wood', pos=(0, WALL_H + 2.4, z), tint=WOODT)
    for sx in (-1, 1):
        walls.add(p_box(0.3, 2.4, 0.3, top=(0.5, 0.3)), 'M_wood', pos=(sx * 13.7, WALL_H, z), tint=WOODT) if False else None

# ------------------------------------------------------------------ cheminée monumentale (mur du fond)
FZ = 9.9  # face intérieure du mur du fond
# piédroits
for sx in (-1, 1):
    dec.box((1.6, 3.8, 1.8), pos=(sx * 2.9, 0, FZ - 0.9), mat='M_stone', tint=STT, bev=0.05)
    dec.box((2.0, 0.5, 2.1), pos=(sx * 2.9, 0, FZ - 1.0), mat='M_marble', tint=STT, bev=0.05)
    dec.box((1.9, 0.4, 2.0), pos=(sx * 2.9, 3.6, FZ - 1.0), mat='M_marble', tint=STT, bev=0.05)
dec.box((7.8, 0.7, 2.1), pos=(0, 3.8, FZ - 1.0), mat='M_marble', tint=STT, bev=0.05)       # linteau
dec.box((8.2, 0.3, 2.3), pos=(0, 4.5, FZ - 1.1), mat='M_marble', tint=STT, bev=0.04)        # tablette
# hotte pyramidale
dec.add(p_box(7.6, 5.6, 1.9, top=(3.4, 0.8)), 'M_stone', pos=(0, 4.8, FZ - 0.95), tint=STT)
dec.add(p_box(3.4, 3.2, 0.8), 'M_stone', pos=(0, 10.3, FZ - 0.4), tint=STT) if False else None
# fond du foyer
dec.add(p_box(3.6, 2.6, 0.2), 'M_dark', pos=(0, 0.2, FZ - 0.15), tint=(0.03, 0.03, 0.03))
dec.add(p_box(3.8, 0.2, 1.4), 'M_stone', pos=(0, 0, FZ - 0.85), tint=(0.35, 0.3, 0.28))
# marche du foyer
stands.box((8.6, 0.25, 2.4), pos=(0, 0, FZ - 2.0), mat='M_stone', tint=(0.85, 0.8, 0.75), bev=0.04)
stands.box((9.4, 0.12, 0.7), pos=(0, 0, FZ - 3.4), mat='M_stone', tint=(0.9, 0.85, 0.8), bev=0.03)
# feu : bûches + flammes + braises
for k in range(4):
    a = 0.4 * (k - 1.5)
    dec.add(p_cyl(0.13, 1.5, 8), 'M_wood', pos=(a * 1.4, 0.35 + 0.1 * (k % 2), FZ - 0.9 + 0.1 * k), roll=math.pi / 2, yaw=0.15 * (k - 2), tint=(0.35, 0.22, 0.12))
fx.add(p_box(2.4, 0.08, 0.9), 'M_flame', pos=(0, 0.3, FZ - 0.9), tint=(1, 1, 1))
for k in range(7):
    xx = (k - 3) * 0.42
    h = 1.4 + 0.5 * math.sin(k * 1.9) + 0.4 * (1 - abs(k - 3) / 3)
    fx.lathe([(0.0, 0.0), (0.24, 0.06), (0.33, 0.3), (0.3, h * 0.45), (0.2, h * 0.68), (0.1, h * 0.88), (0.0, h)], pos=(xx, 0.35, FZ - 0.9 + 0.12 * math.sin(k)), mat='M_flame', seg=8, cap0=False, cap1=False, roll=0.12 * math.sin(k * 2.3))
for sx in (-1, 1):  # chenets
    dec.add(p_box(0.12, 0.7, 0.12), 'M_iron', pos=(sx * 1.4, 0.2, FZ - 1.4), tint=IRT)
    dec.add(p_box(0.1, 0.1, 1.3), 'M_iron', pos=(sx * 1.4, 0.35, FZ - 0.95), tint=IRT)
    dec.sphere(0.13, pos=(sx * 1.4, 0.95, FZ - 1.4), mat='M_iron', tint=IRT, nu=8, nv=4)
sc.empty('Torch_01', 0.0, 1.2, FZ - 0.9)
# blason au-dessus
dec.add(p_lathe([(0.9, 0), (0.95, 0.06), (0.8, 0.14), (0.0, 0.2)], 12, True, False), 'M_gold', pos=(0, 6.6, FZ - 1.55), pitch=math.pi / 2, tint=GOLDT)
dec.add(p_lathe([(0.7, 0), (0.0, 0.1)], 12, False, False), 'M_cloth', pos=(0, 6.6, FZ - 1.66), pitch=math.pi / 2, tint=(0.55, 0.1, 0.12))
for sg in (-1, 1):
    dec.add(p_box(0.12, 3.4, 0.04), 'M_steel', pos=(0, 5.5 if sg > 0 else 5.5, FZ - 1.7), roll=sg * 0.6, tint=(0.8, 0.8, 0.85))
    dec.add(p_box(0.9, 0.12, 0.08), 'M_gold', pos=(sg * 0.5 + 0.0, 6.7, FZ - 1.7), roll=sg * 0.6, tint=GOLDT)
# objets sur la tablette
for xx, k in ((-3.0, 0), (-1.8, 1), (1.7, 2), (3.0, 3)):
    dec.lathe([(0.08, 0), (0.1, 0.06), (0.05, 0.3), (0.12, 0.4)], pos=(xx, 4.8, FZ - 1.0), mat='M_gold', seg=8, tint=GOLDT)
for xx in (-2.3, 2.3):
    dec.cyl(0.06, 0.35, pos=(xx, 4.8, FZ - 1.0), mat='M_plaster', seg=6, tint=(1, 0.95, 0.8))
    fx.lathe([(0.0, 0), (0.05, 0.05), (0.03, 0.14), (0.0, 0.22)], pos=(xx, 5.15, FZ - 1.0), mat='M_flame', seg=5, cap0=False, cap1=False)

# ------------------------------------------------------------------ table de stratégie
tb, otb = sc.part('Obstacle_01', origin=(0, 0, 0)), None
TY = 1.0
tb.box((5.8, 0.22, 3.0), pos=(0, TY - 0.22, 0), mat='M_wood_l', tint=WOODT, bev=0.05)
tb.box((6.1, 0.12, 3.3), pos=(0, TY, 0), mat='M_wood_l', tint=WOODT, bev=0.04)
tb.box((5.0, 0.04, 2.5), pos=(0, TY + 0.12, 0), mat='M_wood', tint=WOODT)
# carte (plan avec UV explicites)
Vq = np.array([(-2.5, TY + 0.165, -1.25), (2.5, TY + 0.165, -1.25), (2.5, TY + 0.165, 1.25), (-2.5, TY + 0.165, 1.25)], float)
Fq = [(3, 2, 1, 0)]
UVq = np.array([(0, 1), (1, 1), (1, 0), (0, 0)], float)  # (x-, z-) = haut-gauche de l'image
tb.add((Vq, Fq), 'M_map', uv=UVq)
for sx in (-1, 1):
    for sz in (-1, 1):
        tb.lathe([(0.2, 0), (0.22, 0.06), (0.16, 0.15), (0.2, 0.45), (0.14, 0.6), (0.2, 0.75), (0.24, 0.8)], pos=(sx * 2.6, 0.0, sz * 1.3), mat='M_wood_l', seg=10, tint=WOODT)
tb.box((5.4, 0.12, 0.12), pos=(0, 0.28, 1.3), mat='M_wood_l', tint=WOODT)
tb.box((5.4, 0.12, 0.12), pos=(0, 0.28, -1.3), mat='M_wood_l', tint=WOODT)
tb.box((0.12, 0.12, 2.6), pos=(0, 0.28, 0), mat='M_wood_l', tint=WOODT)
# figurines / forteresses / marqueurs
rg = np.random.default_rng(12)
for k in range(8):
    x, z = rg.uniform(-2.2, 2.2), rg.uniform(-1.0, 1.0)
    cc = ['#8c1f26', '#2c4a7a', '#3a6a3a', '#c8a030'][k % 4]
    tb.cone(0.07, 0.22, pos=(x, TY + 0.165, z), mat='M_wood', seg=6, tint=cc)
    tb.cyl(0.07, 0.04, pos=(x, TY + 0.165, z), mat='M_wood', seg=6, tint=cc)
for (x, z) in ((-1.4, -0.4), (1.2, 0.5), (0.2, -0.7)):
    tb.box((0.34, 0.2, 0.34), pos=(x, TY + 0.165, z), mat='M_stone', tint=STT)
    for ax, az in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        tb.cyl(0.05, 0.3, pos=(x + ax * 0.15, TY + 0.165, z + az * 0.15), mat='M_stone', seg=6, tint=STT)
        tb.box((0.1, 0.05, 0.1), pos=(x + ax * 0.15, TY + 0.465, z + az * 0.15), mat='M_stone', tint=STT)
tb.add(p_box(0.8, 0.02, 0.5), 'M_burlap', pos=(1.7, TY + 0.165, -0.8), yaw=0.4, tint=(0.95, 0.9, 0.8))   # parchemin
# chandeliers de table
for sx in (-1, 1):
    tb.lathe([(0.15, 0), (0.12, 0.04), (0.05, 0.3), (0.1, 0.34)], pos=(sx * 2.6, TY + 0.165, 0), mat='M_gold', seg=8, tint=GOLDT)
    fx.lathe([(0.0, 0), (0.07, 0.06), (0.04, 0.2), (0.0, 0.34)], pos=(sx * 2.6, TY + 0.5, 0), mat='M_flame', seg=5, cap0=False, cap1=False)
sc.empty('Torch_10', 2.6, TY + 0.7, 0)
# chaises
chair = []
for (x, z, yw) in ((-1.8, 1.9, math.pi), (0, 1.9, math.pi), (1.8, 1.9, math.pi), (-1.8, -1.9, 0), (0, -1.9, 0), (1.8, -1.9, 0), (-3.7, 0, -math.pi / 2), (3.7, 0, math.pi / 2)):
    stands.box((0.6, 0.08, 0.6), pos=(x, 0.5, z), mat='M_wood', tint=WOODT, yaw=yw, bev=0.015)
    for ax, az in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, pz = ax * 0.25, az * 0.25
        c_, s_ = math.cos(yw), math.sin(yw)
        stands.box((0.07, 0.5, 0.07), pos=(x + px * c_ + pz * s_, 0, z - px * s_ + pz * c_), mat='M_wood', tint=WOODT)
    c_, s_ = math.cos(yw), math.sin(yw)
    bx, bz = x + 0.28 * s_, z + 0.28 * c_
    stands.box((0.6, 1.0, 0.07), pos=(bx, 0.55, bz), mat='M_wood', tint=WOODT, yaw=yw, bev=0.015)
    stands.box((0.5, 0.6, 0.02), pos=(bx - 0.0 * s_ - 0.03 * s_, 0.75, bz - 0.04 * c_), mat='M_cloth', tint=(0.55, 0.12, 0.14), yaw=yw)

# ------------------------------------------------------------------ râteliers d'armes
def sword(mb, x, y, z, yaw, L=1.0, roll=0.0, pitch=0.0):
    mb.add(p_box(0.07, L, 0.018, top=(0.035, 0.012)), 'M_steel', pos=(x, y, z), yaw=yaw, roll=roll, pitch=pitch, tint=(0.85, 0.87, 0.92))
    mb.add(p_box(0.3, 0.04, 0.05), 'M_gold', pos=(x, y - 0.02, z), yaw=yaw, roll=roll, pitch=pitch, tint=GOLDT)
    mb.add(p_box(0.04, 0.2, 0.04), 'M_wood', pos=(x, y - 0.22, z), yaw=yaw, roll=roll, pitch=pitch, tint=(0.4, 0.28, 0.2))
    mb.add(p_ico(0.04, 0), 'M_gold', pos=(x, y - 0.24, z), tint=GOLDT)


def spear(mb, x, y, z, L=2.2, tilt=0.08, yaw=0.0):
    mb.add(p_cyl(0.022, L, 5), 'M_wood', pos=(x, y, z), yaw=yaw, pitch=tilt, tint=(0.55, 0.4, 0.28))
    mb.add(p_cone(0.05, 0.28, 4), 'M_steel', pos=(x + math.sin(yaw) * math.sin(tilt) * L, y + math.cos(tilt) * L, z + math.cos(yaw) * math.sin(tilt) * L), yaw=yaw, pitch=tilt, tint=(0.85, 0.87, 0.92))


def shield(mb, x, y, z, r, yaw, col):
    mb.add(p_lathe([(r, 0.0), (r * 0.98, 0.04), (r * 0.5, 0.1), (0.07, 0.16), (0.0, 0.2)], 14, True, False), 'M_wood', pos=(x, y, z), yaw=yaw, pitch=math.pi / 2, tint=(0.85, 0.8, 0.75))
    mb.add(p_lathe([(r * 0.95, 0.0), (r * 0.5, 0.06)], 14, False, False), 'M_cloth', pos=(x, y, z), yaw=yaw, pitch=math.pi / 2, tint=col) if False else None


# rack A : râtelier à lances au sol (mur gauche, z=-5)
mA, oA = sc.part('Obstacle_02', origin=(-13.0, 0, -5.0)), None
mA.box((0.6, 0.15, 3.2), pos=(-12.9, 0.0, -5.0), mat='M_wood', tint=WOODT, bev=0.02)
for dz in (-1.5, 1.5):
    mA.box((0.14, 1.7, 0.14), pos=(-12.9, 0.0, -5.0 + dz), mat='M_wood', tint=WOODT)
mA.box((0.14, 0.1, 3.2), pos=(-12.9, 0.85, -5.0), mat='M_wood', tint=WOODT)
mA.box((0.14, 0.1, 3.2), pos=(-12.9, 1.55, -5.0), mat='M_wood', tint=WOODT)
for k in range(7):
    spear(mA, -12.82 + rng.uniform(-0.08, 0.08), 0.15, -5.0 - 1.3 + k * 0.43, L=2.3 + 0.15 * (k % 3), tilt=0.06 + 0.02 * (k % 2), yaw=0.0)
# rack B : épées au mur (z=0) + boucliers
mB, oB = sc.part('Obstacle_03', origin=(-13.0, 0, 0.0)), None
mB.box((0.12, 2.0, 3.6), pos=(-13.82, 1.6, 0.0), mat='M_wood', tint=WOODT, bev=0.02)
for yy in (2.2, 3.0):
    mB.box((0.14, 0.1, 3.6), pos=(-13.73, yy, 0.0), mat='M_wood_l', tint=WOODT)
for k in range(6):
    sword(mB, -13.65, 2.25 if k % 2 == 0 else 3.05, -1.4 + k * 0.56, 0.0, L=1.0, roll=0.0, pitch=0.0) if False else None
for k in range(5):
    zz = -1.5 + k * 0.75
    sword(mB, -13.6, 2.25, zz, math.pi / 2, L=1.1, roll=0.0)
    mB.add(p_box(0.07, 1.1, 0.018, top=(0.035, 0.012)), 'M_steel', pos=(-13.6, 3.0 - 0.0, zz), yaw=math.pi / 2, tint=(0.85, 0.87, 0.92)) if False else None
for k, col in enumerate(((0.55, 0.1, 0.12), (0.2, 0.3, 0.5), (0.55, 0.1, 0.12))):
    zz = -1.2 + k * 1.2
    mB.add(p_lathe([(0.45, 0.0), (0.43, 0.05), (0.25, 0.14), (0.08, 0.2), (0.0, 0.22)], 16, True, False), 'M_cloth', pos=(-13.6, 3.0, zz), roll=-math.pi / 2, tint=col)
    mB.add(p_torus(0.44, 0.03, 16, 4), 'M_iron', pos=(-13.65, 3.0, zz), roll=-math.pi / 2, tint=IRT)
# rack C : haches et arcs
mC = dec
mC.box((0.12, 2.0, 3.0), pos=(-13.82, 1.6, 5.0), mat='M_wood', tint=WOODT, bev=0.02)
for yy in (2.2, 3.0):
    mC.box((0.14, 0.1, 3.0), pos=(-13.73, yy, 5.0), mat='M_wood_l', tint=WOODT)
for k in range(4):
    zz = 3.9 + k * 0.7
    mC.add(p_cyl(0.025, 1.0, 5), 'M_wood', pos=(-13.62, 2.25, zz), pitch=0, roll=0, tint=(0.5, 0.35, 0.25))
    mC.add(p_box(0.04, 0.3, 0.3, top=(0.04, 0.08)), 'M_steel', pos=(-13.62, 3.15, zz), tint=(0.8, 0.82, 0.88))
for k in range(3):
    zz = 4.2 + k * 0.8
    mC.add(p_torus(0.5, 0.025, 16, 4), 'M_wood', pos=(-13.62, 3.0, zz), roll=-math.pi / 2, tint=(0.45, 0.3, 0.2)) if False else None

# ------------------------------------------------------------------ mannequins d'entraînement + cibles (mur droit)
mD = sc.part('Obstacle_04', origin=(12.0, 0, 0.0))
for (x, z, yw) in ((11.8, -5.5, -0.5), (12.3, -2.0, 0.3), (11.7, 1.5, -0.2), (12.2, 5.0, 0.4)):
    mD.box((1.2, 0.12, 0.12), pos=(x, 0.0, z), mat='M_wood', tint=WOODT, yaw=yw)
    mD.box((0.12, 0.12, 1.2), pos=(x, 0.0, z), mat='M_wood', tint=WOODT, yaw=yw)
    mD.add(p_cyl(0.1, 1.9, 8), 'M_wood', pos=(x, 0.1, z), tint=WOODT)
    mD.add(p_lathe([(0.26, 0), (0.3, 0.25), (0.26, 0.6), (0.18, 0.72)], 8, True, True), 'M_burlap', pos=(x, 0.85, z), tint=(1, 0.95, 0.85))
    mD.add(p_box(1.15, 0.1, 0.1), 'M_wood', pos=(x, 1.45, z), yaw=yw, tint=WOODT)
    mD.add(p_sphere(0.16, 8, 4), 'M_burlap', pos=(x, 1.85, z), tint=(1, 0.95, 0.85))
    sword(mD, x + 0.55 * math.cos(yw), 1.45, z - 0.55 * math.sin(yw), yw, L=0.8, roll=0.9)
# cibles de tir
for (x, z) in ((13.2, -8.2), (13.2, 8.0)):
    mD.add(p_cyl(0.05, 1.9, 5), 'M_wood', pos=(x - 0.2, 0.0, z - 0.4), pitch=0.25, tint=WOODT)
    mD.add(p_cyl(0.05, 1.9, 5), 'M_wood', pos=(x - 0.2, 0.0, z + 0.4), pitch=-0.25, tint=WOODT)
    for k, (rad, col) in enumerate(((0.62, '#e8e0cc'), (0.5, '#222222'), (0.38, '#2c5a9a'), (0.26, '#a82a2a'), (0.12, '#e0b030'))):
        mD.add(p_cyl(rad, 0.03, 18, cap0=True), 'M_plaster', pos=(x - 0.18 - k * 0.012, 1.2, z), roll=math.pi / 2, yaw=0.0, tint=col) if False else \
            mD.add(p_lathe([(rad, 0.0), (rad, 0.03)], 18, True, True), 'M_plaster', pos=(x - 0.2 - 0.0, 1.1, z), pitch=0.0, roll=math.pi / 2, tint=col) if False else None
    mD.add(p_lathe([(0.62, 0.0), (0.6, 0.06), (0.0, 0.1)], 16, True, False), 'M_plaster', pos=(x - 0.25, 1.1, z), roll=-math.pi / 2, tint=(0.9, 0.85, 0.7))
    for k, (rad, col) in enumerate(((0.5, '#202020'), (0.38, '#2c5a9a'), (0.26, '#a82a2a'), (0.12, '#e0b030'))):
        mD.add(p_lathe([(rad, 0.0), (rad, 0.01)], 16, True, True), 'M_plaster', pos=(x - 0.31 - k * 0.006, 1.1, z), roll=-math.pi / 2, tint=col)

# ------------------------------------------------------------------ tonneaux, caisses, sacs (coin arrière gauche) + coffre
mE = sc.part('Obstacle_05', origin=(-11.0, 0, 8.0))


def barrel(mb, x, z, h=1.0, tint=(0.8, 0.7, 0.6)):
    mb.lathe([(0.37, 0), (0.45, h * 0.28), (0.5, h * 0.55), (0.45, h * 0.82), (0.37, h)], pos=(x, 0, z), mat='M_wood', seg=12, tint=tint, jit=0.06)
    for yy, rr_ in ((0.12, 0.395), (0.35, 0.49), (0.65, 0.5), (0.88, 0.42)):
        mb.lathe([(rr_ * 0.99, 0), (rr_ * 1.02, 0.07), (rr_ * 0.99, 0.12)], pos=(x, yy * h, z), mat='M_iron', seg=12, tint=IRT, cap0=False, cap1=False)


for (x, z) in ((-12.6, 8.9), (-11.7, 9.0), (-12.2, 8.0), (-10.7, 9.1), (-9.7, 9.2)):
    barrel(mE, x, z, h=rng.uniform(0.95, 1.1), tint=tuple(np.array(WOODT) * rng.uniform(0.85, 1.05)))
for (x, z, s, yw) in ((-11.3, 7.9, 0.9, 0.2), (-10.3, 8.1, 0.8, -0.3), (-10.8, 7.9, 0.7, 0.5)):
    pass
for (x, z, s, yw, y0) in ((-9.0, 8.4, 0.95, 0.3, 0.0), (-8.0, 8.6, 0.85, -0.2, 0.0), (-8.6, 8.5, 0.7, 0.6, 0.95)):
    mE.box((s, s, s), pos=(x, y0, z), mat='M_wood', tint=tuple(np.array(WOODT) * 0.95), yaw=yw, bev=0.02)
    mE.box((s * 1.02, 0.08, s * 1.02), pos=(x, y0 + s * 0.25, z), mat='M_iron', tint=IRT, yaw=yw)
    mE.box((s * 1.02, 0.08, s * 1.02), pos=(x, y0 + s * 0.75, z), mat='M_iron', tint=IRT, yaw=yw)
for (x, z) in ((-12.6, 6.6), (-12.0, 6.9), (-11.4, 6.5)):
    mE.add(p_ico(0.34, 1), 'M_burlap', pos=(x, 0.0, z), scale=(1.0, 0.8, 0.8), tint=(1.0, 0.95, 0.85), yaw=rng.uniform(0, 3))
# autres tonneaux côté opposé (coin avant droit près des cibles)
for (x, z) in ((12.8, 7.2), (12.0, 7.7)):
    barrel(dec, x, z, h=1.0)
# coffre
mF = sc.part('Obstacle_06', origin=(7.0, 0, 7.5))
cx, cz = 7.0, 7.5
mF.box((1.5, 0.85, 0.9), pos=(cx, 0.0, cz), mat='M_wood', tint=(0.7, 0.55, 0.45), bev=0.03)
mF.add(p_cyl(0.45, 1.5, 14), 'M_wood', pos=(cx, 0.85, cz), roll=math.pi / 2, tint=(0.75, 0.58, 0.46), scale=(1, 1, 1))
for dx in (-0.55, 0.0, 0.55):
    mF.add(p_lathe([(0.47, 0), (0.47, 0.1)], 14, False, False), 'M_iron', pos=(cx + dx, 0.85, cz), roll=math.pi / 2, tint=IRT) if False else None
    mF.box((0.12, 0.9, 0.97), pos=(cx + dx, 0.0, cz), mat='M_iron', tint=IRT)
    mF.add(p_cyl(0.465, 0.12, 14), 'M_iron', pos=(cx + dx - 0.06, 0.85, cz), roll=math.pi / 2, tint=IRT)
mF.box((0.2, 0.3, 0.06), pos=(cx, 0.65, cz - 0.47), mat='M_gold', tint=GOLDT, bev=0.01)
for sx in (-1, 1):
    for sz in (-1, 1):
        mF.box((0.14, 0.16, 0.14), pos=(cx + sx * 0.7, 0.0, cz + sz * 0.4), mat='M_gold', tint=GOLDT)
# petit coffre + pièces d'or
mF.box((0.8, 0.5, 0.5), pos=(5.7, 0.0, 8.3), mat='M_wood', tint=(0.7, 0.55, 0.45), yaw=0.4, bev=0.02)
mF.box((0.84, 0.08, 0.54), pos=(5.7, 0.45, 8.3), mat='M_iron', tint=IRT, yaw=0.4)

# ------------------------------------------------------------------ lustres
for k, (x, z) in enumerate(((-5.0, 1.0), (5.0, 1.0), (-5.0, 6.5), (5.0, 6.5))):
    y = 8.6
    dec.add(p_torus(1.15, 0.06, 20, 5), 'M_iron', pos=(x, y, z), tint=IRT)
    dec.add(p_torus(0.55, 0.04, 14, 4), 'M_iron', pos=(x, y - 0.1, z), tint=IRT)
    dec.add(p_box(2.3, 0.05, 0.05), 'M_iron', pos=(x, y, z), tint=IRT)
    dec.add(p_box(0.05, 0.05, 2.3), 'M_iron', pos=(x, y, z), tint=IRT)
    for a in range(4):
        aa = a * math.pi / 2 + math.pi / 4
        dec.add(p_box(0.04, 3.0, 0.04), 'M_iron', pos=(x + 1.1 * math.cos(aa) * 0.5, y + 0.0, z + 1.1 * math.sin(aa) * 0.5), pitch=0.0, tint=IRT) if False else None
    for a in range(8):
        aa = a * math.pi / 4
        px, pz = x + 1.15 * math.cos(aa), z + 1.15 * math.sin(aa)
        dec.cyl(0.05, 0.28, pos=(px, y + 0.06, pz), mat='M_plaster', seg=6, tint=(1, 0.95, 0.8))
        fx.lathe([(0.0, 0), (0.06, 0.05), (0.035, 0.18), (0.0, 0.3)], pos=(px, y + 0.34, pz), mat='M_flame', seg=5, cap0=False, cap1=False)
    # chaînes jusqu'à la voûte
    for a in range(3):
        aa = a * 2 * math.pi / 3
        top = (x + 0.15 * math.cos(aa), WALL_H + VB - 0.4, z + 0.15 * math.sin(aa))
        bot = (x + 1.15 * math.cos(aa), y, z + 1.15 * math.sin(aa))
        L_ = math.dist(top, bot)
        dec.add(p_cyl(0.025, L_, 4), 'M_iron', pos=bot, tint=IRT, yaw=math.atan2(top[0] - bot[0], top[2] - bot[2]),
                pitch=math.atan2(math.hypot(top[0] - bot[0], top[2] - bot[2]), top[1] - bot[1])) if False else None
    dec.add(p_cyl(0.03, WALL_H + VB - 0.4 - y, 4), 'M_iron', pos=(x, y, z), tint=IRT)
    sc.empty(f'Torch_{k + 2:02d}', x, y + 0.45, z)

# ------------------------------------------------------------------ appliques murales (Torch_06..09)
for k, (x, z, n) in enumerate(((-13.35, -5.0 + 2.5, (1, 0)), (-13.35, 7.5, (1, 0)), (13.35, -5.0, (-1, 0)), (13.35, 5.0, (-1, 0)))):
    pass
wall_torches = [(-13.5, 2.5, -1.0), (13.5, -5.0, 1.0), (13.5, 5.0, 1.0), (-13.5, -7.5, -1.0)]
for k, (x, z, sg) in enumerate(wall_torches):
    nrm = (sg, 0.0)
    sconce(dec, fx, (x, 2.6, z), nrm, 0.45, tint=(0.35, 0.3, 0.25))
    sc.empty(f'Torch_{k + 6:02d}', x, 2.6, z)

# ------------------------------------------------------------------ bannières
bi = 1
for (x, z, yw, w, h, ay) in ((-13.8, -7.5, math.pi / 2, 1.6, 3.4, 7.6), (-13.8, 5.0, math.pi / 2, 1.6, 3.4, 7.6), (13.8, -2.5, -math.pi / 2, 1.6, 3.4, 7.6),
                             (13.8, 7.5, -math.pi / 2, 1.6, 3.4, 7.6), (-8.0, 9.8, math.pi, 1.8, 4.2, 7.8), (8.0, 9.8, math.pi, 1.8, 4.2, 7.8),
                             (-4.8, -9.6, 0.0, 1.5, 3.8, 7.9), (4.8, -9.6, 0.0, 1.5, 3.8, 7.9)):
    banner_object(sc, f'Banner_{bi:02d}', (x, ay, z), yw if abs(yw) > 1 else yw, w, h, RED, GOLD, GOLD, phase=bi, mat='M_cloth')
    bi += 1

# ------------------------------------------------------------------ rayons de lumière (plans)
for (wx, wz, sg) in ((-14.0, -7.5, 1), (-14.0, -2.5, 1), (-14.0, 2.5, 1), (-14.0, 7.5, 1), (14.0, -7.5, -1), (14.0, -2.5, -1), (14.0, 2.5, -1), (14.0, 7.5, -1)):
    for (da, dw) in ((0.0, 0.95), (1.0, 0.95)):
        top_y = 6.1
        dx, dz = sg * 6.4, 2.2
        if da == 0.0:
            P0 = (wx + sg * 0.6, top_y, wz - dw)
            P1 = (wx + sg * 0.6, top_y, wz + dw)
        else:
            P0 = (wx + sg * 0.6, top_y - 1.6, wz - 0.0)
            P1 = (wx + sg * 0.6 + sg * 0.0, top_y, wz)
            P0 = (wx + sg * 0.6 - sg * 0.001, top_y, wz - dw)
            P1 = (wx + sg * 0.6, top_y, wz + dw)
        Vr = np.array([P0, P1, (P1[0] + dx, 0.06, P1[2] + dz), (P0[0] + dx, 0.06, P0[2] + dz)], float)
        if da == 1.0:
            # second plan : perpendiculaire (croisé)
            Vr = np.array([(wx + sg * 0.6 - 0.7, top_y - 0.2, wz), (wx + sg * 0.6 + 0.7, top_y - 0.2, wz), (wx + sg * 0.6 + 0.7 + dx, 0.06, wz + dz), (wx + sg * 0.6 - 0.7 + dx, 0.06, wz + dz)], float)
            Vr[:, 1] = Vr[:, 1]
        UVr = np.array([(0, 1), (1, 1), (1, 0), (0, 0)], float)
        fx.add((Vr, [(0, 1, 2, 3)]), 'M_ray', uv=UVr, tint=(1, 1, 1))
for (wx, wz) in ((-11.5, 10.0), (-6.5, 10.0), (6.5, 10.0), (11.5, 10.0)):
    dx, dz = 0.0, -6.0
    Vr = np.array([(wx - 0.95, 6.1, wz - 0.6), (wx + 0.95, 6.1, wz - 0.6), (wx + 0.95 + 2.0, 0.06, wz + dz), (wx - 0.95 + 2.0, 0.06, wz + dz)], float)
    fx.add((Vr, [(0, 1, 2, 3)]), 'M_ray', uv=np.array([(0, 1), (1, 1), (1, 0), (0, 0)], float), tint=(1, 1, 1))

# ------------------------------------------------------------------ colonnes de l'arc d'ouverture + extérieur
for sx in (-1, 1):
    for zz in (-10.3,):
        pass
# grand arc frontal (z=-10) avec bannière : déjà par la nervure ; sol extérieur
dec.add(p_cyl(160, 0.2, 40, cap0=False, cap1=True), 'M_dirt', pos=(0, -0.7, 0), tint=(0.6, 0.55, 0.5))

sc.ao_opts = {'Ground': 0.65, 'Decor': 0.5, 'Walls': 0.5}
sc.build(ao_samples=48, ao_dist=2.5, ao_floor=0.42)
sc.export(OUTDIR + '/club_hall.glb')
