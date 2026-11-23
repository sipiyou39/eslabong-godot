"""Briques partagées des arènes grecques (Olympe, Enfers, Atlantide) : colonnes, péristyle, parapet, braseros, nuages, rochers."""
import math
import numpy as np
from arena_common import *


def fluted_column(mb, x, z, r, h, y0=0.0, shaft='M_marble', gold='M_gold', t_shaft=(1, 1, 1), t_gold=(0.9, 0.68, 0.25), seg=12, flutes=(6, 0.07),
                  cap='ionic', band=True, base_h=0.3, jit=0.03, cap_h=0.34):
    """colonne grecque : base moulurée, fût cannelé à entasis, bague, chapiteau (ionique à volutes / dorique / sans)."""
    rs = r * 0.8
    mb.lathe([(r * 1.28, y0), (r * 1.28, y0 + base_h * 0.4), (r * 1.1, y0 + base_h * 0.62), (rs * 1.12, y0 + base_h)], pos=(x, 0, z), mat=gold, seg=seg, tint=t_gold,
             cap0=False)
    ys = y0 + base_h
    yt = y0 + h - cap_h
    L = yt - ys
    prof = [(rs * 1.1, ys), (rs * 1.12, ys + L * 0.05), (rs * 1.15, ys + L * 0.45), (rs * 1.05, ys + L * 0.8), (rs * 0.95, yt)]
    mb.add(p_lathe(prof, seg, False, True, flutes=flutes), shaft, pos=(x, 0, z), tint=t_shaft, jit=jit)
    if band:
        mb.lathe([(rs * 1.07, yt - 0.34), (rs * 1.14, yt - 0.3), (rs * 1.14, yt - 0.22), (rs * 1.0, yt - 0.18)], pos=(x, 0, z), mat=gold, seg=seg, tint=t_gold, cap0=False,
                 cap1=False)
    if cap == 'none':
        return
    mb.lathe([(rs * 0.98, yt), (rs * 1.2, yt + cap_h * 0.3), (rs * 1.38, yt + cap_h * 0.8), (rs * 1.45, yt + cap_h)], pos=(x, 0, z), mat=gold, seg=seg, tint=t_gold, cap0=False)
    mb.add(p_box(rs * 2.5, 0.09, rs * 2.5), gold, pos=(x, yt + cap_h, z), tint=t_gold)
    if cap == 'ionic':
        for sx in (-1, 1):
            mb.add(p_torus(rs * 0.55, rs * 0.2, 9, 4), gold, pos=(x + sx * rs * 1.38, yt + cap_h * 0.55, z), pitch=math.pi / 2, tint=t_gold)


def peristyle(sc, rr, part, d, y0, h, spacing, r, ent_h=1.3, ent_w=None, mats=None, tints=None, skip=None, seg=12, cap='ionic', jit_pos=0.0, rng=None, flutes=(6, 0.07),
              offset=0.0, gold_cap=True, skip_s=None, ent=True):
    """anneau de colonnes (centre à l'offset d du mur) + entablement continu au-dessus."""
    m = dict(shaft='M_marble', gold='M_gold', ent='M_marble', trim='M_gold')
    m.update(mats or {})
    t = dict(shaft=(1, 1, 1), gold=(0.9, 0.68, 0.25), ent=(1, 1, 1), trim=(0.9, 0.68, 0.25))
    t.update(tints or {})
    mb = sc.part(part)
    P, N, T, s = rr.along(spacing, d, offset=offset)
    out = []
    for i in range(len(P)):
        x, z = P[i]
        if skip and skip(x, z):
            continue
        fluted_column(mb, x, z, r, h, y0, m['shaft'], m['gold'], t['shaft'], t['gold'], seg=seg, cap=cap, flutes=flutes)
        out.append((x, z, N[i]))
    w = ent_w or r * 1.7
    yb = y0 + h
    if not ent:
        return out, yb
    solid_ring(sc, rr, part, d - w, d + w, yb, yb + ent_h * 0.62, m['ent'], tint=t['ent'], inner=True, top=True, outer=True, skip=skip_s)
    solid_ring(sc, rr, part, d - w * 1.12, d + w * 1.12, yb + ent_h * 0.62, yb + ent_h, m['ent'], tint=t['ent'], inner=True, top=True, outer=True, skip=skip_s)
    add_strip(mb, rr, [(d - w * 1.13, yb + ent_h * 0.62 + 0.03), (d - w * 1.13, yb + ent_h * 0.62 + 0.15)], m['trim'], 'in', t['trim'], skip_s, 4.0)
    add_strip(mb, rr, [(d - w * 1.13, yb + ent_h - 0.12), (d - w * 1.13, yb + ent_h - 0.03)], m['trim'], 'in', t['trim'], skip_s, 4.0)
    return out, yb + ent_h


def parapet(sc, rr, part='Walls', d0=0.0, d1=0.55, h=1.0, mat='M_marble', tint=(1, 1, 1), gold='M_gold', t_gold=(0.9, 0.68, 0.25), skip=None, capw=0.08):
    solid_ring(sc, rr, part, d0, d1, 0.0, h, mat, tint=tint, inner=True, top=False, outer=True, skip=skip)
    solid_ring(sc, rr, part, d0 - capw, d1 + capw, h, h + 0.1, gold, tint=t_gold, inner=True, top=True, outer=True, skip=skip)
    mb = sc.part(part)
    add_strip(mb, rr, [(d0 - 0.005, 0.22), (d0 - 0.005, 0.3)], gold, 'in', t_gold, skip, 4.0)


def brazier_pedestal(dec, fx, F_pos, n_out, arm, mat='M_marble', gold='M_gold', flame='M_flame', t=(1, 1, 1), t_gold=(0.9, 0.68, 0.25), flame_scale=1.0, y_base=0.0):
    """braséro sur piédestal : la flamme est à F_pos (y de l'empty Torch)."""
    x, y, z = F_pos
    yb = y_base
    h = y - 0.42 - yb
    dec.lathe([(0.34, yb), (0.34, yb + 0.15), (0.24, yb + 0.3), (0.2, yb + h * 0.5), (0.24, yb + h * 0.9), (0.3, yb + h)], pos=(x, 0, z), mat=mat, seg=10, tint=t)
    dec.lathe([(0.3, yb + h), (0.34, yb + h + 0.08), (0.46, yb + h + 0.24), (0.5, yb + h + 0.3), (0.42, yb + h + 0.3), (0.0, yb + h + 0.14)], pos=(x, 0, z), mat=gold, seg=10,
              tint=t_gold, cap0=True)
    s = flame_scale
    fx.lathe([(0.0, y - 0.15), (0.3 * s, y - 0.08), (0.34 * s, y + 0.05), (0.26 * s, y + 0.25), (0.15 * s, y + 0.5), (0.06 * s, y + 0.75), (0.0, y + 0.98)],
             pos=(x, 0, z), mat=flame, seg=7, cap0=False, cap1=False, tint=(1, 1, 1))


def make_torch_fn(**kw):
    def fn(md, mf, Fp, n, arm):
        brazier_pedestal(md, mf, Fp, n, arm, **kw)
    return fn


def cloud_puffs(mb, rng, centers, size=(8.0, 14.0), mat='M_cloud', sub=1, top_y=0.0, flat=0.42, tint_hi=(1.0, 0.95, 0.85), tint_lo=(0.62, 0.66, 0.8), n_sub=6, spread=0.9):
    """nuages : amas de 'puffs' (icosphères aplaties) dont le dessus est éclairé (teinte haute) et le dessous bleuté."""
    for (cx, cy, cz) in centers:
        base = rng.uniform(*size)
        k = int(rng.integers(max(3, n_sub - 2), n_sub + 3))
        for j in range(k):
            ox = rng.uniform(-1, 1) * base * spread
            oz = rng.uniform(-1, 1) * base * spread * 0.8
            oy = rng.uniform(0.0, 0.6) * base * 0.35
            sz = base * rng.uniform(0.45, 0.85)
            V, F = p_ico(1.0, sub)
            lo = np.array(s2l(tint_lo))
            hi = np.array(s2l(tint_hi))

            def vf(Vw, cy_=cy + oy, h_=sz * flat, lo=lo, hi=hi):
                t = np.clip((Vw[:, 1] - (cy_ - h_)) / (2 * h_), 0, 1)[:, None]
                return lo[None, :] * (1 - t) + hi[None, :] * t
            mb.add((V * np.array([sz, sz * flat, sz * 0.9]), F), mat, pos=(cx + ox, cy + oy, cz + oz), yaw=rng.uniform(0, 6.28), tint=(1, 1, 1), vfun=vf)


def rock_spire(mb, x, z, r, h, rng, mat='M_rock', tint=(1, 1, 1), y0=0.0, seg=7, taper=0.25, jitter=0.12, lean=0.0):
    """aiguille rocheuse : lathe irrégulier effilé."""
    prof = [(r, y0 - 0.5), (r * 0.95, y0 + h * 0.2), (r * (0.8 - 0.3 * taper), y0 + h * 0.55), (r * (0.45 - 0.2 * taper), y0 + h * 0.85), (0.0, y0 + h)]
    mb.add(p_lathe(prof, seg, False, False, jitter=jitter), mat, pos=(x, 0, z), tint=tint, yaw=rng.uniform(0, 6.28), jit=0.06)


def ring_band(sc, part, rr, rows, mat, tint=(1, 1, 1), ref='up', skip=None, uv=4.0, vfun=None, jit=0.0):
    mb = sc.part(part)
    add_strip(mb, rr, rows, mat, ref, tint, skip, uv, vfun=vfun, jit=jit)


def lightning_bolt(mb, p0, p1, rng, mat='M_bolt', w=0.4, n=7, amp=3.5, tint=(1, 1, 1)):
    """éclair lointain : suite de poutres émissives en zigzag de p0 à p1."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    pts = [p0]
    for k in range(1, n):
        t = k / n
        pts.append(p0 + (p1 - p0) * t + rng.uniform(-amp, amp, 3) * np.array([1, 0.2, 1]))
    pts.append(p1)
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        d = b - a
        L = np.linalg.norm(d)
        yaw = math.atan2(d[0], d[2])
        pitch = -math.atan2(d[1], math.hypot(d[0], d[2]))
        ww = w * (1 - 0.6 * k / n)
        mb.add(p_box(ww, ww, L), mat, pos=(a + b) / 2 - np.array([0, ww / 2, 0]), yaw=yaw, pitch=pitch, tint=tint)


def part_tris(mb):
    t = 0
    for a in mb.F[3]:
        t += len(a)
    for a in mb.F[4]:
        t += 2 * len(a)
    for f in mb.F[0]:
        t += len(f) - 2
    return t


def report(sc):
    tot = 0
    for n, mb in sc.parts.items():
        k = part_tris(mb)
        tot += k
        if k > 300:
            print(f'[tris] {n:14s} {k}')
    print(f'[tris] TOTAL {tot}')
