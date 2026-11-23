"""arena_volcano.glb — « Cratère de Lave » : arène taillée dans la caldeira d'un volcan actif.
Plateau de colonnes de basalte hexagonales, rivière de lave autour du terrain, ponts de pierre, paroi de caldeira avec coulées,
cheminées de fumée, porte ruinée, braseros d'obsidienne."""
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_land import *

T = TP
G.seed(707)
rng = np.random.default_rng(707)

defmat('M_ground', tex=T('volcano_ground.png'), norm=T('volcano_ground_n.png'), emit_tex=T('volcano_ground_e.png'), emit_str=1.5, rough=0.7, uv=1, norm_str=1.0, spec=0.45)
defmat('M_basalt', tex=T('volcano_basalt.png'), norm=T('volcano_basalt_n.png'), rough=0.9, uv=5.0)
defmat('M_bank', tex=T('volcano_bank.png'), norm=T('volcano_bank_n.png'), emit_tex=T('volcano_bank_e.png'), emit_str=0.9, rough=0.9, uv=5.0)
defmat('M_rock', tex=T('volcano_rock.png'), norm=T('volcano_rock_n.png'), rough=0.92, uv=6.0)
defmat('M_cliff', tex=T('volcano_cliff.png'), norm=T('volcano_cliff_n.png'), rough=0.95, uv=9.0)
defmat('M_ash', tex=T('volcano_hot.png'), norm=T('volcano_hot_n.png'), emit_tex=T('volcano_hot_e.png'), emit_str=0.85, rough=1.0, uv=7.0)
defmat('M_stone', tex=T('volcano_stone.png'), norm=T('volcano_stone_n.png'), rough=0.85, uv=4.0)
defmat('M_iron', tex=T('volcano_iron.png'), norm=T('volcano_iron_n.png'), rough=0.5, metal=0.6, uv=2.0)
defmat('M_bronze', tex=T('volcano_iron.png'), norm=T('volcano_iron_n.png'), rough=0.45, metal=0.65, uv=2.0)
defmat('M_obsidian', tex=T('volcano_obsidian.png'), norm=T('volcano_obsidian_n.png'), rough=0.22, metal=0.3, spec=1.0, uv=4.0)
defmat('M_lava', tex=T('volcano_lava.png'), norm=T('volcano_lava_n.png'), emit_tex=T('volcano_lava_e.png'), emit_str=0.8, rough=0.5, uv=4.0)
defmat('M_flame', emit='#ff7a1c', emit_str=2.6, vcol=False, color='#ff7a1c')
defmat('M_glow', emit='#ff6a1a', emit_str=1.3, vcol=False, color='#ff6a1a')
defmat('M_smoke', rough=1.0, spec=0.1)
defmat('M_cloth', tex=T('volcano_cloth.png'), rough=0.95, uv=2.0, double=True)
defmat('M_gold', rough=0.35, metal=0.9)
defmat('M_dark', rough=0.5, metal=0.6)

LAVA_Y = -1.5
sc = Scene('arena_volcano')
rr = RR(step=1.0)
walls = sc.part('Walls')
dec = sc.part('Decor')
lava = sc.part('Lava')
sc.noao.add('Lava')
build_ground(sc, step=0.8)

# ------------------------------------------------------------------ relief
BR = [((0.0, -16.0), (0.0, -1.0)), ((0.0, 16.0), (0.0, 1.0)), ((-26.0, 0.0), (-1.0, 0.0)), ((26.0, 0.0), (1.0, 0.0))]
STREAMS = [dict(x0=-17.0, amp=3.2, fr=0.11, ph=0.4, z0=-74.0, z1=-20.0, w=3.4),
           dict(x0=15.5, amp=2.6, fr=0.13, ph=2.1, z0=-70.0, z1=-20.5, w=2.6),
           dict(x0=-44.0, amp=2.0, fr=0.10, ph=1.0, z0=-46.0, z1=-8.0, w=2.2)]


def stream_x(s, z):
    return s['x0'] + s['amp'] * np.sin(np.asarray(z) * s['fr'] + s['ph'])


def bridge_mask(x, z):
    m = np.zeros_like(np.asarray(x, float))
    for (P, n) in BR:
        al = (x - P[0]) * n[0] + (z - P[1]) * n[1]
        lat = (x - P[0]) * (-n[1]) + (z - P[1]) * n[0]
        m = np.maximum(m, np.exp(-(lat / 2.1) ** 2) * (al > -1.5))
    return m


def gully(x, z):
    g = np.zeros_like(np.asarray(x, float))
    for s in STREAMS:
        lat = (x - stream_x(s, z)) / s['w']
        zz = np.clip((z - s['z0']) / 6.0, 0, 1) * np.clip((s['z1'] - z) / 6.0, 0, 1)
        g = np.maximum(g, np.exp(-lat ** 2 * 1.4) * np.clip(zz * 2, 0, 1))
    return g


PX = [-1.0, 0.0, 0.10, 0.55, 1.0, 1.7, 2.7, 4.0, 6.4, 8.0, 9.4, 11.0, 30.0]
PY = [0.0, 0.0, 0.55, 0.62, 0.58, 0.12, -2.0, -2.2, -2.2, -1.3, 0.25, 0.4, 0.45]


def hfun(x, z, D):
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    D = np.asarray(D, float)
    sh = 2.6 * sstep(0.8, 3.5, D) * (fbm2(x * 0.05 + 3, z * 0.05, 3, 5) - 0.5) * 2
    dd = D - sh
    bm = bridge_mask(x, z)
    y = np.interp(dd, PX, PY)
    y = np.where(dd < 1.8, y * (1 - 0.93 * bm) + 0.05 * bm, y)
    # rives irrégulières et îlots dans le chenal
    chan = sstep(2.4, 3.6, dd) * (1 - sstep(7.0, 8.2, dd))
    isl = sstep(0.66, 0.74, fbm2(x * 0.30, z * 0.30, 3, 9)) * (1 - bm) * chan
    y = y + 2.6 * isl
    y = y + (fbm2(x * 1.3, z * 1.3, 2, 14) - 0.5) * 0.35 * sstep(0.5, 2.0, D) * (1 - sstep(8, 11, D))   # banc rugueux
    # terrasse de cendres
    gul = gully(x, z)
    ter = (fbm2(x * 0.11, z * 0.11, 4, 11) - 0.5) * 2.4 * sstep(10, 16, D) * (1 - sstep(24, 34, D))
    y = y + ter * (1 - 0.8 * gul)
    # paroi de la caldeira (plus haute et plus proche au fond, côté -Z)
    back = sstep(2.0, -30.0, z)
    Hb = 15.0 + 25.0 * back + 6.0 * sstep(18.0, 36.0, np.abs(x)) * (1 - back)
    D0 = 17.0 - 5.0 * back
    Lw = 34.0
    u = sstep(D0, D0 + Lw, D)
    yw = Hb * u ** 1.15
    yw = yw + (ridge2(x * 0.05, z * 0.05, 4, 13) - 0.35) * 9.0 * sstep(D0, D0 + 14, D) * (1 - 0.9 * gul)
    yw = yw + (fbm2(x * 0.35, z * 0.35, 3, 17) - 0.5) * 1.6 * u
    yw = yw - 0.65 * np.maximum(D - (D0 + Lw + 6), 0) * sstep(D0 + Lw, D0 + Lw + 12, D)
    y = y + yw * (1 - 0.0) - 2.0 * gul * u * (1 - 0.0) * 1.0
    # sillons des coulées
    y = y - 1.0 * gul * sstep(11, 20, D)
    return y


def H(x, z):
    D = np.maximum(outline_sdf(x, z), 0.0)
    return hfun(x, z, D)


def tint_terrain(V, D):
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    n1 = fbm2(x * 0.08, z * 0.08, 3, 31)
    n2 = fbm2(x * 0.55, z * 0.55, 2, 32)
    f = 0.85 + 0.6 * n1 + 0.2 * (n2 - 0.5)
    col = np.stack([f * 1.05, f * 0.95, f * 0.9], 1)
    heat = np.exp(-np.clip(y - LAVA_Y, 0, None) / 0.9) * (D < 14) * (y < 1.2) * (D > 1.0)
    col[:, 0] += heat * 2.4
    col[:, 1] += heat * 0.75
    col[:, 2] += heat * 0.06
    ash = sstep(10, 38, y)[:, None]
    col = col * (1 - ash * 0.25) + ash * lin('#8a7a72')[None, :] * 0.42
    far = sstep(45, 130, D)[:, None]
    col = col * (1 - far * 0.45) + far * lin('#7a3a26')[None, :] * 0.5
    return col


# anneaux : basalte (rim + chenal), cendres (terrasse), falaise (paroi)
ds_a = [-0.04, 0.1, 0.5, 1.0, 1.5] + list(np.arange(2.0, 12.01, 0.7))
ds_b = [ds_a[-1]] + list(np.arange(12.0, 30.01, 2.0))[1:]
ds_c = [ds_b[-1]] + list(np.arange(30.0, 62.01, 3.2))[1:] + list(np.arange(70.0, 142.0, 8.0))
ring_terrain(dec, rr, ds_a, hfun, 'M_bank', tintfun=tint_terrain)
ring_terrain(dec, rr, ds_b, hfun, 'M_ash', tintfun=tint_terrain)
ring_terrain(dec, rr, ds_c, hfun, 'M_cliff', tintfun=tint_terrain)

# plan de lave (sous le terrain : visible dans le chenal)
ring_terrain(lava, rr, [0.8, 2.5, 4.5, 6.5, 8.5, 10.5], lambda x, z, d: np.full_like(d, LAVA_Y), 'M_lava', tint=(1, 1, 1))

# coulées de lave le long de la paroi
for s in STREAMS:
    zs = np.arange(s['z0'], s['z1'] + 0.01, 1.8)
    path = np.stack([stream_x(s, zs), zs], 1)
    wd = s['w'] * (0.8 + 0.5 * np.sin(zs * 0.31 + s['ph'])) * (0.6 + 0.6 * np.clip((zs - s['z0']) / 20, 0, 1))
    drape_ribbon(lava, path, wd, H, 'M_lava', yoff=0.32, across=5, tint=(1, 1, 1), uvlen=4.0, edge_sink=0.55)

# ------------------------------------------------------------------ ponts de pierre sur la rivière de lave
STONE_T = (0.78, 0.74, 0.72)
bridge_end = []
for (P, n) in BR:
    p0 = (P[0] + n[0] * 0.0, P[1] + n[1] * 0.0)
    p1 = (P[0] + n[0] * 10.4, P[1] + n[1] * 10.4)
    stone_bridge(walls, p0, p1, 3.6, 0.04, 0.40, 0.95, 'M_stone', tint=STONE_T, par_h=0.55, par_w=0.34, thick=0.7, n=16, piers=2, pier_bottom=-3.2, post_every=2)
    bridge_end.append((p1, n))
    # pylônes d'obsidienne + braseros géants à l'extrémité côté terrasse
    lat = np.array([-n[1], n[0]])
    for sg in (-1, 1):
        px, pz = p1[0] + lat[0] * sg * 2.4 + n[0] * 0.6, p1[1] + lat[1] * sg * 2.4 + n[1] * 0.6
        y0 = float(H(np.array(px), np.array(pz))) - 0.4
        V_, F_ = hex_prism(0.5, 3.1 - y0 + 0.0, rot=0.3)
        walls.add((V_, F_), 'M_obsidian', pos=(px, y0, pz), tint=(0.35, 0.3, 0.38))
        V_, F_ = hex_prism(0.66, 0.35, rot=0.3, top_cut=0.0)
        walls.add((V_, F_), 'M_stone', pos=(px, 3.0, pz), tint=(0.6, 0.55, 0.55))
        brazier(dec, (px, 3.25, pz), h=0.3, r=0.62, tint=(0.25, 0.22, 0.22), flame_h=1.5, seg=8)
    # grandes dents d'obsidienne
    for sg in (-1, 1):
        px, pz = p1[0] + lat[0] * sg * 2.4 + n[0] * 0.6, p1[1] + lat[1] * sg * 2.4 + n[1] * 0.6
        for k in range(3):
            a = rng.uniform(0, TAU)
            walls.add(p_cone(0.16, 0.85, 5), 'M_obsidian', pos=(px + math.cos(a) * 0.42, 3.3, pz + math.sin(a) * 0.42), tint=(0.3, 0.26, 0.34), pitch=0.35 * math.cos(a), roll=0.35 * math.sin(a))
sc.empty('Light_01', 0.0, 4.2, -26.8)
sc.empty('Light_02', 0.0, 4.2, 26.8)
sc.empty('Light_03', -36.8, 4.2, 0.0)
sc.empty('Light_04', 36.8, 4.2, 0.0)

# ------------------------------------------------------------------ rebord de basalte : torches sur piliers hexagonaux
FLAME_Y = 2.2


def volcano_sconce(md, mf, Fp, n, arm):
    x, y, z = Fp
    sconce(md, mf, Fp, n, arm, tint=(0.34, 0.31, 0.33), mat='M_iron', scale=1.15)
    px, pz = x + n[0] * (arm + 0.12), z + n[1] * (arm + 0.12)
    y0 = float(H(np.array(px), np.array(pz))) - 0.25
    V_, F_ = hex_prism(0.34, y - y0 + 0.05, rot=yaw_of(n[0], n[1]))
    md.add((V_, F_), 'M_obsidian', pos=(px, y0, pz), tint=(0.32, 0.28, 0.34))
    V_, F_ = hex_prism(0.42, 0.18, rot=yaw_of(n[0], n[1]))
    md.add((V_, F_), 'M_stone', pos=(px, y - 0.28, pz), tint=(0.62, 0.56, 0.55))


for i in range(10):
    x, z, nx, nz, sdv = torch_frame(i)
    sc.empty(f'Torch_{i + 1:02d}', x, FLAME_Y, z)
    arm = max(0.5, -sdv + 0.5)
    volcano_sconce(walls, dec, (x, FLAME_Y, z), (nx, nz), arm)

# ------------------------------------------------------------------ pierres de gué, colonnes basaltiques, blocs
# pierres hexagonales dans la lave
for k in range(70):
    for _try in range(20):
        a = rng.uniform(0, TAU)
        P, n_ = rr.at_base(rng.uniform(0, rr.length()))
        d = rng.uniform(3.2, 7.2)
        x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
        if bridge_mask(np.array(x), np.array(z)) < 0.15 and float(H(np.array(x), np.array(z))) < LAVA_Y - 0.3:
            break
    else:
        continue
    h = rng.uniform(0.5, 1.5)
    V_, F_ = hex_prism(rng.uniform(0.4, 0.8), h, rot=rng.uniform(0, 1), tilt=rng.uniform(0, TAU), top_cut=rng.uniform(0, 0.3))
    dec.add((V_, F_), 'M_basalt', pos=(x, LAVA_Y - 0.5, z), tint=(0.6, 0.5, 0.45), jit=0.1)

# grappes de colonnes basaltiques sur la terrasse et le pied de paroi (fond de scène)
placed = 0
tries = 0
while placed < 34 and tries < 600:
    tries += 1
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(11.5, 40.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if z > 4 and rng.random() < 0.5:
        continue
    if bridge_mask(np.array(x), np.array(z)) > 0.2 or float(gully(np.array(x), np.array(z))) > 0.08:
        continue
    y0 = float(H(np.array(x), np.array(z))) - 1.2
    big = rng.random() < 0.4
    ro = rng.uniform(2.6, 4.6) if big else rng.uniform(1.4, 2.4)
    base_h = rng.uniform(5, 13) if big else rng.uniform(2, 5)
    hs = [base_h * rng.uniform(0.55, 1.0) + 1.2 for _ in range(7)]
    hs[0] = base_h + 1.2
    t0 = rng.uniform(0.75, 1.0)
    rho = ro / (1 + math.sqrt(3))
    centers = [(0.0, 0.0)] + [(math.sqrt(3) * rho * math.cos(math.pi / 6 + k * math.pi / 3), math.sqrt(3) * rho * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
    for i_, (cx, cz) in enumerate(centers):
        yy = float(H(np.array(x + cx), np.array(z + cz))) - 1.0
        V_, F_ = hex_prism(rho * 0.97, hs[i_] + (y0 + 1.2 - yy) * 0 + 1.0, rot=0.0, tilt=rng.uniform(0, TAU), top_cut=rng.uniform(0.0, 0.5) * (i_ > 0))
        dec.add((V_, F_), 'M_basalt', pos=(x + cx, yy, z + cz), tint=(0.62 * t0, 0.55 * t0, 0.52 * t0), jit=0.14)
    placed += 1

# blocs de roche
for k in range(90):
    P, n_ = rr.at_base(rng.uniform(0, rr.length()))
    d = rng.uniform(9.0, 55.0)
    x, z = P[0] + n_[0] * d, P[1] + n_[1] * d
    if bridge_mask(np.array(x), np.array(z)) > 0.25 and d < 13:
        continue
    s = rng.uniform(0.7, 2.6) * (1 + d / 40)
    y = float(H(np.array(x), np.array(z))) - s * 0.25
    t0 = rng.uniform(0.7, 1.0)
    dec.rock((s * 1.3, s, s * 1.2), pos=(x, y, z), mat='M_rock' if k % 3 else 'M_basalt', seed=k, sub=1, tint=(0.7 * t0, 0.6 * t0, 0.55 * t0), yaw=rng.uniform(0, 3))

# ------------------------------------------------------------------ porte ruinée au fond (axe du pont nord)
gz = -(16.0 + 13.2)
gy = float(H(np.array(0.0), np.array(gz)))
for sg in (-1, 1):
    gx = sg * 4.0
    dec.add(p_box(1.9, 7.4, 1.9, top=(1.5, 1.5)), 'M_stone', pos=(gx, gy - 0.4, gz), tint=(0.62, 0.58, 0.58), bev=0.04, jit=0.04)
    dec.add(p_box(2.5, 0.5, 2.5), 'M_obsidian', pos=(gx, gy - 0.3, gz), tint=(0.4, 0.34, 0.4))
    dec.add(p_box(2.2, 0.5, 2.2), 'M_obsidian', pos=(gx, gy + 6.6, gz), tint=(0.4, 0.34, 0.4), bev=0.03)
    for k in range(3):
        dec.add(p_cone(0.22, 1.5 + 0.4 * (k % 2), 5), 'M_obsidian', pos=(gx + (k - 1) * 0.65, gy + 7.05, gz), tint=(0.3, 0.26, 0.34), roll=-(k - 1) * 0.22)
    dec.add(p_box(0.36, 4.6, 0.06), 'M_glow', pos=(gx - sg * 0.0, gy + 1.0, gz + 0.97), tint=(1, 1, 1))
dec.add(p_box(10.2, 1.0, 2.2), 'M_stone', pos=(0.0, gy + 6.9, gz), tint=(0.6, 0.56, 0.56), bev=0.04)
dec.add(p_box(7.4, 0.14, 0.1), 'M_glow', pos=(0.0, gy + 6.75, gz + 1.12), tint=(1, 1, 1))
dec.box((8.0, 0.55, 2.0), pos=(0.0, gy + 7.9, gz), mat='M_obsidian', top=(6.0, 1.5), tint=(0.38, 0.32, 0.4), bev=0.03)

# ------------------------------------------------------------------ fumée
for (x, z, h, r0) in [(-30.0, -33.0, 26.0, 1.8), (33.0, -31.0, 22.0, 1.6), (-9.0, -52.0, 40.0, 3.2), (14.0, -58.0, 46.0, 3.6), (-44.0, 9.0, 18.0, 1.4),
                      (44.0, 12.0, 20.0, 1.5), (-52.0, -22.0, 30.0, 2.4), (52.0, -26.0, 30.0, 2.4)]:
    y0 = float(H(np.array(x), np.array(z)))
    smoke_column(dec, x, y0 - 0.5, z, h, r0, rng, wind=(0.6, 0.25), n=11, c_low='#7a3a1c', c_mid='#2a2523', c_top='#4a443f')
    # évent incandescent à la base
    dec.add(p_lathe([(r0 * 1.7, 0.0), (r0 * 1.2, 0.35), (r0 * 0.7, 0.28), (0.0, 0.2)], 8, False, True), 'M_lava', pos=(x, y0 - 0.1, z), tint=(1, 1, 1))
# grand panache de cendres au fond (calotte étalée)
for (x, z, y, s) in [(-5.0, -62.0, 52.0, 26.0), (20.0, -66.0, 56.0, 22.0)]:
    for k in range(6):
        V_, F_ = p_ico(1.0, 1)
        sx_ = s * rng.uniform(0.5, 1.0)
        V_ = V_ * np.array([sx_, sx_ * 0.35, sx_ * 0.8]) + np.array([x + rng.uniform(-s * 0.5, s * 0.5), y + rng.uniform(-3, 3), z + rng.uniform(-s * 0.3, s * 0.3)])
        tt = np.clip((V_[:, 1] - (y - 8)) / 16, 0, 1)
        dec.add((V_, F_), 'M_smoke', tint=cgrad(tt, [(0, '#3a2620'), (0.5, '#3c3532'), (1, '#6a615b')]) * rng.uniform(0.9, 1.1))



# ------------------------------------------------------------------ obstacles
def basalt_obstacle(mb, x, z, r, hs, seed):
    rho = r / 2.75
    centers = [(0.0, 0.0)] + [(math.sqrt(3) * rho * math.cos(math.pi / 6 + k * math.pi / 3 + 0.2), math.sqrt(3) * rho * math.sin(math.pi / 6 + k * math.pi / 3 + 0.2)) for k in range(6)]
    for i_, (cx, cz) in enumerate(centers):
        h = hs[i_ % len(hs)]
        V_, F_ = hex_prism(rho * 0.96, h, rot=0.2, tilt=rng.uniform(0, TAU), top_cut=(0.12 + 0.3 * (i_ % 3) / 2) * (i_ > 0))
        mb.add((V_, F_), 'M_basalt', pos=(x + cx, 0.0, z + cz), tint=(0.62, 0.55, 0.52), jit=0.12)
    # chapeaux de lave incandescents sur deux colonnes
    for i_ in (0, 3):
        cx, cz = centers[i_]
        V_, F_ = hex_prism(rho * 0.74, 0.05, rot=0.2)
        mb.add((V_, F_), 'M_lava', pos=(x + cx, hs[i_ % len(hs)] + 0.01 - (0.0), z + cz), tint=(1, 1, 1))
    # veines de lave entre les colonnes
    for k in range(3):
        a = 0.2 + k * 2.1 + 0.52
        rv = rho * 1.68
        mb.add(p_box(0.08, hs[(k * 2 + 1) % len(hs)] * 0.55, 0.05), 'M_glow', pos=(x + rv * math.cos(a), 0.3, z + rv * math.sin(a)), yaw=-a + math.pi / 2, tint=(1, 1, 1))


def spire_obstacle(mb, x, z, r, h, seed):
    rg = np.random.default_rng(seed)
    n = 5
    y = 0.0
    for k in range(n):
        t = k / (n - 1)
        rad = r * (1.0 - 0.52 * t)
        hh = h * (0.28 - 0.04 * t)
        V_, F_ = p_rock(2 * rad / 1.3, hh * 1.5, 2 * rad / 1.3, int(seed * 10 + k), 1, 0.12, 0.22)
        mb.add((V_, F_), 'M_basalt' if k % 2 == 0 else 'M_rock', pos=(x + rg.uniform(-0.08, 0.08), y - 0.05, z + rg.uniform(-0.08, 0.08)), yaw=rg.uniform(0, 3),
               tint=(0.58 + 0.12 * t, 0.5 + 0.08 * t, 0.46), jit=0.1)
        # veine de lave dans la jointure
        if k < n - 1:
            mb.add(p_lathe([(rad * 0.78, 0.0), (rad * 0.8, 0.07)], 9, False, False), 'M_lava', pos=(x, y + hh * 0.9, z), tint=(1, 1, 1), yaw=rg.uniform(0, 3))
        y += hh * 0.92
    # couronne : cuvette de lave + éclats d'obsidienne
    rc = r * 0.5
    mb.add(p_lathe([(rc, 0), (rc * 1.08, 0.18), (rc * 0.86, 0.2), (0, 0.1)], 8, False, True), 'M_obsidian', pos=(x, y - 0.02, z), tint=(0.3, 0.26, 0.34))
    mb.add(p_lathe([(rc * 0.85, 0.12), (0.0, 0.2)], 8, False, True), 'M_lava', pos=(x, y, z), tint=(1, 1, 1))
    for k in range(5):
        a = TAU * k / 5 + 0.4
        V_, F_ = p_crystal(rc * 0.16, 0.9 + 0.5 * (k % 2), 5, 0.4, seed + k, 0.4, rc * 0.2, 0.05)
        mb.add((V_, F_), 'M_obsidian', pos=(x + math.cos(a) * rc * 0.95, y + 0.1, z + math.sin(a) * rc * 0.95), yaw=-a, tint=(0.28, 0.24, 0.32))
    mb.add(p_lathe([(0.0, 0.0), (rc * 0.7, 0.04), (rc * 0.5, 0.35), (rc * 0.22, 0.7), (0.0, 1.0)], 7, False, False), 'M_flame', pos=(x, y + 0.12, z), tint=(1, 1, 1))


HEIGHTS = [[3.6, 2.5, 3.1, 1.9, 3.3, 2.2, 1.6], [3.2, 2.2, 2.8, 3.5, 1.8, 2.6, 2.0], [3.4, 2.4, 1.7, 3.0, 2.1, 3.2, 2.5]]
for i in range(6):
    mb, o = obstacle_part(sc, i)
    if i in (0, 2, 4):
        basalt_obstacle(mb, o['x'], o['z'], o['r'], HEIGHTS[i // 2], i)
    else:
        spire_obstacle(mb, o['x'], o['z'], o['r'], [3.7, 3.4, 3.5][i // 2], i + 3)

sc.ao_opts = {'Ground': 0.72, 'Decor': 0.55, 'Walls': 0.55}
sc.build(ao_samples=40, ao_dist=3.0, ao_floor=0.45)
sc.export(OUTDIR + '/arena_volcano.glb')
