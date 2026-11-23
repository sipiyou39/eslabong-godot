"""Coque d'arène commune : sol, mur d'enceinte, gradins, foule, torches, obstacles utilitaires."""
import math
import numpy as np
import json
import lib_geo as G
from lib_geo import *
from lib_scene import *
from kit import *

LAYOUT = json.load(open(ROOT + '/data/arena_layout.json'))
OBSTACLES = LAYOUT['obstacles']
TORCHES = LAYOUT['torches']


def build_ground(sc, mat='M_ground', step=0.5):
    V, F, UV = ground_mesh(step=step)
    sc.part('Ground').add((V, F), mat, uv=UV)


def add_strip(mb, rr, rows, mat, ref, tint=(1, 1, 1), skip=None, uvsize=4.0, vfun=None, jit=0.0):
    V, F, UV = ring_strip(rr, rows, ref=ref, skip=skip, uvsize=uvsize)
    if not F:
        return
    mb.add((V, F), mat, tint=tint, uv=UV, vfun=vfun, jit=jit)


def build_walls(sc, rr, T=1.5, H=3.2, face_d=0.36, mats=None, tints=None, skip=None, panel_y=1.85, uv=4.0, plinth=0.5, cornice=True,
                outer=True):
    m = dict(face='M_stone', panel='M_stone', trim='M_stone', top='M_stone')
    m.update(mats or {})
    t = dict(face=(1, 1, 1), panel=(1, 1, 1), trim=(1, 1, 1), top=(1, 1, 1))
    t.update(tints or {})
    mb = sc.part('Walls')
    # plinthe
    add_strip(mb, rr, [(0.0, 0.0), (0.0, plinth * 0.5), (0.0, plinth)], m['trim'], 'in', t['trim'], skip, uv)
    add_strip(mb, rr, [(0.0, plinth), (face_d * 0.5, plinth + 0.05), (face_d, plinth + 0.12)], m['trim'], 'up', t['trim'], skip, uv)
    # panneau bas
    ys = np.linspace(plinth + 0.12, panel_y, 5)
    add_strip(mb, rr, [(face_d, y) for y in ys], m['panel'], 'in', t['panel'], skip, uv)
    # face haute
    top0 = H - 0.45
    ys = np.linspace(panel_y, top0, 4)
    add_strip(mb, rr, [(face_d, y) for y in ys], m['face'], 'in', t['face'], skip, uv)
    # corniche
    if cornice:
        add_strip(mb, rr, [(face_d, top0), (0.02, top0 + 0.1)], m['trim'], 'down', t['trim'], skip, uv)
        add_strip(mb, rr, [(0.02, top0 + 0.1), (0.0, top0 + 0.1), (0.0, H - 0.08), (0.02, H)], m['trim'], 'in', t['trim'], skip, uv)
    else:
        add_strip(mb, rr, [(face_d, top0), (0.0, H)], m['trim'], 'in', t['trim'], skip, uv)
    add_strip(mb, rr, [(0.0, H), (T * 0.5, H), (T, H)], m['top'], 'up', t['top'], skip, uv)
    if outer:
        add_strip(mb, rr, [(T, H), (T, H * 0.5), (T, 0.0)], m['face'], 'out', t['face'], skip, uv)


def build_tiers(sc, rr, d0, y_start, rows, tread, rise, mat_tread, mat_riser, tint_tread=(1, 1, 1), tint_riser=(0.8, 0.8, 0.8), skip=None,
                uv=4.0, back=1.2, mat_back=None, tint_back=None, aisles=None, tread_vf=None):
    """gradins annulaires. Retourne liste (d_centre, y) pour la foule."""
    mb = sc.part('Stands')
    tiers = []
    y_prev = y_start
    for k in range(rows):
        dk = d0 + k * tread
        yk = y_start + rise * (k + 1)
        # contremarche
        add_strip(mb, rr, [(dk, y_prev), (dk, (y_prev + yk) / 2), (dk, yk)], mat_riser, 'in', tint_riser, skip, uv)
        # marche
        add_strip(mb, rr, [(dk, yk), (dk + tread * 0.5, yk), (dk + tread, yk)], mat_tread, 'up', tint_tread, skip, uv, vfun=tread_vf)
        tiers.append((dk + tread * 0.58, yk))
        y_prev = yk
    dend = d0 + rows * tread
    if back:
        add_strip(mb, rr, [(dend, y_prev), (dend + back * 0.5, y_prev), (dend + back, y_prev)], mat_back or mat_tread, 'up',
                  tint_back or tint_tread, skip, uv)
    return tiers, dend, y_prev


def solid_ring(sc, rr, part, d0, d1, y0, y1, mat, tint=(1, 1, 1), uv=4.0, skip=None, inner=True, outer=True, top=True):
    """anneau plein (bloc) : face intérieure, dessus, face extérieure."""
    mb = sc.part(part)
    if inner:
        add_strip(mb, rr, [(d0, y0), (d0, (y0 + y1) / 2), (d0, y1)], mat, 'in', tint, skip, uv)
    if top:
        add_strip(mb, rr, [(d0, y1), (d1, y1)], mat, 'up', tint, skip, uv)
    if outer:
        add_strip(mb, rr, [(d1, y1), (d1, (y0 + y1) / 2), (d1, y0)], mat, 'out', tint, skip, uv)


def torches(sc, rr, y=2.2, mat_ok=True, style=None, sconce_fn=None):
    dec = sc.part('Decor')
    fx = sc.part('Decor')
    for i, t in enumerate(TORCHES):
        name = f'Torch_{i + 1:02d}'
        sc.empty(name, t['x'], y, t['z'])
        sdv = float(rr.sdf(np.array(t['x']), np.array(t['z'])))
        s = rr.s_nearest(t['x'], t['z'])
        Pw, n = rr.at_base(s)
        arm = max(0.25, -sdv)
        if sconce_fn:
            sconce_fn(dec, fx, (t['x'], y, t['z']), (n[0], n[1]), arm)
        else:
            sconce(dec, fx, (t['x'], y, t['z']), (n[0], n[1]), arm)


def obstacle_part(sc, i):
    o = OBSTACLES[i]
    return sc.part(f'Obstacle_{i + 1:02d}', origin=(o['x'], 0, o['z'])), o


def pilasters_on_wall(mb, rr, positions, face_d, H, mat, tint, cap_mat=None, cap_tint=None, w=0.8, gold=False):
    """pilastres aux abscisses (x,z) approx. données (projetées sur le périmètre)."""
    for (x, z) in positions:
        s = rr.s_nearest(x, z)
        P, n = rr.at_base(s)
        yaw = yaw_of(n[0], n[1])
        # centre du pilastre : entre d=0 et d=face_d (+0.05)
        depth = face_d + 0.08
        c = P + n * (depth / 2 - 0.0)
        mb.box((w, H - 0.55, depth), pos=(c[0], 0.0, c[1]), mat=mat, tint=tint, yaw=yaw, bev=0.03)
        cm = cap_mat or mat
        ct = cap_tint or tint
        mb.box((w + 0.18, 0.2, depth + 0.1), pos=(c[0], 0.0, c[1]), mat=cm, tint=ct, yaw=yaw, bev=0.03)  # base
        mb.box((w + 0.22, 0.3, depth + 0.14), pos=(c[0], H - 0.75, c[1]), mat=cm, tint=ct, yaw=yaw, bev=0.04)  # chapiteau


def arcade_ring(sc, rr, part, D, y0, H, bay=3.7, open_ratio=0.62, spring=2.9, depth=1.3, mat='M_stone', tint=(1, 1, 1), glow_mat=None,
                glow_every=3, kind='round', n=10, glow_tint=(1, 1, 1), jit=0.04, skip_fn=None):
    """anneau de travées à ouvertures en arc, face intérieure sur la courbe d'offset D."""
    mb = sc.part(part)
    nbay = int(round((rr.length() + 2 * math.pi * D) / bay))
    P, N, Tn, s = rr.along(0, D, count=nbay)
    out = []
    for i in range(nbay):
        p0, p1 = P[i], P[(i + 1) % nbay]
        mid = (p0 + p1) / 2
        t = p1 - p0
        wd = float(np.hypot(*t)) + 0.01
        nrm = np.array([t[1], -t[0]])
        nrm /= np.linalg.norm(nrm)
        if np.dot(nrm, mid) < 0:
            nrm = -nrm
        gm = glow_mat if (glow_mat and (i % glow_every != 1)) else None
        if skip_fn is not None and skip_fn(mid[0], mid[1]):
            out.append((mid, nrm, wd, p0))
            continue
        arch_block(mb, (mid[0], mid[1]), (nrm[0], nrm[1]), wd, H, wd * open_ratio, spring, depth, mat=mat, y0=y0, tint=tint, glow_mat=gm,
                   glow_tint=glow_tint, kind=kind, n=n, jit=jit)
        out.append((mid, nrm, wd, p0))
    return out


def snow_cap(mb, rr, d0, d1, y, mat='M_snow', tint=(1, 1, 1), puff=0.28, uv=4.0, skip=None):
    """bandeau de neige bombé posé sur une surface horizontale entre d0 et d1."""
    dm = (d0 + d1) / 2
    rows = [(d0, y), (d0 + 0.18, y + puff * 0.5), (dm, y + puff), (d1 - 0.18, y + puff * 0.55), (d1, y)]

    def vf(V):
        return 0.92 + 0.12 * np.sin(V[:, 0] * 0.9 + V[:, 2] * 1.3) * np.cos(V[:, 2] * 0.7)
    add_strip(mb, rr, rows, mat, 'up', tint, skip, uv, vfun=vf)
