"""Briques d'architecture réutilisables (coordonnées jeu)."""
import math
import numpy as np
import lib_geo as G
from lib_geo import *
from lib_scene import *

TAU = 2 * math.pi


def yaw_of(nx, nz):
    """yaw pour que le +Z local pointe vers (nx,nz)."""
    return math.atan2(nx, nz)


def vgrad(y0, y1, lo, hi):
    """facteur multiplicatif vertical : lo en y0 -> hi en y1."""
    def f(V):
        t = np.clip((V[:, 1] - y0) / (y1 - y0), 0, 1)
        return lo + (hi - lo) * t
    return f


def vnoise_f(amp=0.1, scale=1.0, seed=0):
    r = np.random.default_rng(seed)
    d1, d2, d3 = r.normal(size=(3, 3))
    p1, p2, p3 = r.uniform(0, 6, 3)

    def f(V):
        n = (np.sin(V @ d1 * scale + p1) + np.sin(V @ d2 * scale * 1.7 + p2) + np.sin(V @ d3 * scale * 2.9 + p3)) / 3
        return 1 + amp * n
    return f


def vmul(*fs):
    def f(V):
        out = 1.0
        for g in fs:
            r = np.asarray(g(V), float)
            out = out * (r[:, None] if r.ndim == 1 else r)
        return out if np.ndim(out) > 0 else np.full(len(V), out)
    return f


def _arch_curve(ow, spring, n, kind='round'):
    """courbe d'intrados de gauche à droite."""
    if kind == 'gothic':
        R = ow
        left = []
        for i in range(n + 1):
            th = math.radians(60) * i / n
            left.append((ow / 2 - R * math.cos(th), spring + R * math.sin(th)))
        right = [(-x, y) for (x, y) in reversed(left[:-1])]
        return left + right
    return [((ow / 2) * math.cos(math.pi - math.pi * i / n), spring + (ow / 2) * math.sin(math.pi - math.pi * i / n)) for i in range(n + 1)]


def arch_poly(W, H, ow, spring, n=10, base=0.0, kind='round'):
    curve = _arch_curve(ow, spring, n, kind)
    # contour : bas-gauche mur -> haut -> bas-droite -> ouverture droite -> courbe (droite vers gauche) -> ouverture gauche
    pts = [(-W / 2, base), (-W / 2, H), (W / 2, H), (W / 2, base), (ow / 2, base)]
    pts += list(reversed(curve))
    pts += [(-ow / 2, base)]
    return pts


def opening_poly(ow, spring, n=10, base=0.0, kind='round'):
    curve = _arch_curve(ow, spring, n, kind)
    return [(-ow / 2, base), (ow / 2, base)] + list(reversed(curve))


def arch_block(mb, pos, nxz, W, H, ow, spring, depth, mat='M_stone', y0=0.0, tint=(1, 1, 1), glow_mat=None, glow_tint=(1, 1, 1),
               n=10, vfun=None, jit=0.04, bev=0.0, kind='round'):
    """bloc de mur avec ouverture en arc. pos = centre au sol de la face arène, nxz = normale sortante."""
    yaw = yaw_of(nxz[0], nxz[1])
    poly = arch_poly(W, H, ow, spring, n, kind=kind)
    mb.add(p_extrude_xy(poly, 0, depth), mat, tint=tint, pos=(pos[0], y0, pos[1]), yaw=yaw, vfun=vfun, jit=jit, bev=bev)
    if glow_mat:
        op = opening_poly(ow - 0.02, spring, n, kind=kind)
        mb.add(p_extrude_xy(op, depth * 0.55, depth * 0.55 + 0.04), glow_mat, tint=glow_tint, pos=(pos[0], y0, pos[1]), yaw=yaw)


def local_to_world(pos, nxz, lx, lz):
    """point dans le repère local d'un bloc : +Z sortant, +X tangent."""
    nx, nz = nxz
    # +X local = (nz, -nx)
    return (pos[0] + lx * nz + lz * nx, pos[1] - lx * nx + lz * nz)


def p_broken_cyl(r, r2, h, seg=16, jag=0.5, seed=0, flutes=None, cap=True):
    rg = np.random.default_rng(seed)
    ph = rg.uniform(0, TAU)
    V = []
    for j in range(seg):
        a = TAU * j / seg
        V.append((r * math.cos(a), 0, r * math.sin(a)))
    ks = rg.uniform(0, 1, 4)
    for j in range(seg):
        a = TAU * j / seg
        rr = r2
        if flutes:
            n, dep = flutes
            rr = r2 * (1 - dep * 0.5 * (1 - math.cos(n * a)))
        # dent de scie irrégulière
        t = 0.5 + 0.5 * math.sin(a * 2 + ph) * 0.6 + 0.25 * math.sin(a * 5 + ks[0] * 6) + 0.15 * math.sin(a * 9 + ks[1] * 6)
        V.append((rr * math.cos(a), h + jag * (t - 0.5), rr * math.sin(a)))
    cx = (0, h, 0)
    V.append(cx)
    V = np.array(V, float)
    F = []
    for j in range(seg):
        j2 = (j + 1) % seg
        F.append((j, seg + j, seg + j2, j2))
        if cap:
            F.append((seg + j, 2 * seg, seg + j2))
    F.append(tuple(range(seg)))
    return V, F


def column(mb, pos, r_base, h, mat='M_stone', tint=(1, 1, 1), capital=True, seg=24, flutes=(12, 0.07), broken=0.0, seed=0,
           gold=None, drums=3, base_h=0.35, shaft_ratio=0.8, cap_mat=None, taper=0.14, y0=0.0):
    """colonne dorique : socle étagé, fût cannelé en tambours (entasis), chapiteau galbé (ou cassure)."""
    x, z = pos
    rs = r_base * shaft_ratio
    cm = cap_mat or mat
    mb.lathe([(r_base, y0), (r_base, y0 + base_h * 0.55), (r_base * 0.97, y0 + base_h * 0.62), (r_base * 0.9, y0 + base_h * 0.7),
              (rs * 1.12, y0 + base_h * 0.78), (rs * 1.17, y0 + base_h * 0.9), (rs * 1.12, y0 + base_h * 1.0), (rs * 1.04, y0 + base_h * 1.1)],
             pos=(x, 0, z), mat=cm, seg=seg, tint=tint, jit=0.03)
    y = y0 + base_h * 1.1
    top = y0 + h - (0.7 if capital else 0.0)
    dh = (top - y) / drums
    rg = np.random.default_rng(seed)
    H0 = max(top - y, 1e-3)
    for i in range(drums):
        t0 = (y - (y0 + base_h * 1.1)) / H0
        t1 = (y + dh - (y0 + base_h * 1.1)) / H0
        r0 = rs * (1 - taper * t0) * (1 + 0.025 * math.sin(math.pi * t0))
        r1 = rs * (1 - taper * t1) * (1 + 0.025 * math.sin(math.pi * t1))
        last = (i == drums - 1)
        ox, oz = rg.uniform(-0.02, 0.02, 2)
        if last and broken > 0:
            V, F = p_broken_cyl(r0, r1, dh, seg, jag=broken, seed=seed, flutes=flutes)
            mb.add((V, F), mat, pos=(x + ox, y, z + oz), tint=tint, jit=0.03)
        else:
            mb.add(p_lathe([(r0, 0), (r1, dh)], seg, False, True, flutes=flutes), mat, pos=(x + ox, y, z + oz), yaw=rg.uniform(0, 1),
                   tint=tint, jit=0.04)
        y += dh
    if capital and broken <= 0:
        rr_ = rs * (1 - taper)
        mb.lathe([(rr_ * 1.0, 0), (rr_ * 0.9, 0.07), (rr_ * 0.92, 0.13), (rr_ * 1.08, 0.2), (rr_ * 1.24, 0.3), (rr_ * 1.34, 0.42)],
                 pos=(x, top, z), mat=cm, seg=seg, tint=tint, jit=0.02, cap1=True)
        mb.lathe([(rr_ * 1.42, 0), (rr_ * 1.42, 0.2), (rr_ * 1.36, 0.26)], pos=(x, top + 0.42, z), mat=cm, seg=12, tint=tint, yaw=0.3)
        if gold:
            mb.lathe([(rr_ * 1.0, 0), (rr_ * 1.04, 0.04), (rr_ * 1.04, 0.1), (rr_ * 1.0, 0.14)], pos=(x, top - 0.14, z), mat='M_gold', seg=seg,
                     tint=(0.9, 0.68, 0.25), cap0=False, cap1=False)
    return y


# ------------------------------------------------------------------ bannières
def p_banner(w, h, nx=4, ny=9, wave=0.07, notch=0.22, seed=0, phase=0.0):
    """tissu suspendu, origine = milieu du bord haut ; plan XY, faces +Z / -Z (double face via matériau). Retourne V,F,(u,v)"""
    V = []
    uv = []
    for j in range(ny + 1):
        t = j / ny
        for i in range(nx + 1):
            s = i / nx
            x = (s - 0.5) * w
            y = -t * h
            # échancrure en V en bas
            if j == ny:
                y += notch * h * (1 - abs(2 * s - 1))
            z = wave * math.sin(t * 5.0 + s * 2.0 + phase) * (0.3 + t)
            V.append((x, y, z))
            uv.append((s, t))
    F = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            F.append((a, a + nx + 1, a + nx + 2, a + 1))
    return np.array(V, float), F, np.array(uv)


def banner_tints(uv, c_main, c_edge, c_emb, border=0.08, emblem=True):
    cm, ce, cb = s2l(c_main), s2l(c_edge), s2l(c_emb)
    out = np.tile(cm, (len(uv), 1))
    s, t = uv[:, 0], uv[:, 1]
    edge = (np.minimum(s, 1 - s) < border) | (t < border * 0.6)
    out[edge] = ce
    if emblem:
        d = np.hypot((s - 0.5) * 1.0, (t - 0.38) * 1.6)
        out[d < 0.22] = cb
        out[(d >= 0.22) & (d < 0.28)] = ce
    return out


def banner_object(sc, name, attach, yaw, w, h, c_main, c_edge, c_emb, mat='M_cloth', wave=0.07, seed=0, phase=0.0, emblem=True, rod=True,
                  rod_mat='M_gold', rod_tint=(0.85, 0.65, 0.25)):
    """objet séparé Banner_xx : origine = point d'attache (haut)."""
    mb = sc.part(name, origin=(attach[0], attach[1], attach[2]))
    V, F, uv = p_banner(w, h, wave=wave, seed=seed, phase=phase)
    t = banner_tints(uv, c_main, c_edge, c_emb, emblem=emblem)
    mb.add((V, F), mat, tint=t, pos=attach, yaw=yaw)
    if rod:
        mb.add(p_box(w + 0.3, 0.07, 0.07), rod_mat, pos=(attach[0], attach[1] - 0.02, attach[2]), yaw=yaw, tint=rod_tint)


def pennant(mb, base, h, w, length, yaw, c_main, c_edge, mat='M_cloth', wave=0.15, phase=0.0, ny=8):
    """long fanion horizontal flottant, attaché en haut d'un mât."""
    V = []
    F = []
    nx = 7
    uv = []
    for j in range(2):
        for i in range(nx + 1):
            s = i / nx
            tail = 1 - 0.85 * s
            y = (0.5 - j) * w * tail
            x = s * length
            z = wave * math.sin(s * 4.0 + phase) * s
            V.append((x, y, z))
            uv.append((s, j))
    for i in range(nx):
        F.append((i, nx + 1 + i, nx + 2 + i, i + 1))
    V = np.array(V, float)
    t = np.tile(s2l(c_main), (len(V), 1))
    t[np.array(uv)[:, 0] > 0.82] = s2l(c_edge)
    mb.add((V, F), mat, tint=t, pos=(base[0], base[1] + h, base[2]), yaw=yaw)


# ------------------------------------------------------------------ torche / brasero
def sconce(mb_decor, mb_fx, F_pos, n_out, arm, style='bronze', flame_col='M_flame', scale=1.0, tint=(0.8, 0.6, 0.3), mat='M_bronze'):
    """applique murale : F_pos=(x,y,z) position de la flamme, n_out normale sortante (vers le mur)."""
    x, y, z = F_pos
    nx, nz = n_out
    yaw = yaw_of(nx, nz)
    s = scale
    # plaque murale
    wx, wz = x + nx * arm, z + nz * arm
    mb_decor.box((0.32, 0.62, 0.08), pos=(wx - nx * 0.02, y - 0.48, wz - nz * 0.02), mat=mat, tint=tint, yaw=yaw, bev=0.02)
    # bras
    mb_decor.box((0.08, 0.08, arm + 0.08), pos=(x + nx * (arm * 0.5), y - 0.34, z + nz * (arm * 0.5)), mat=mat, tint=tint, yaw=yaw)
    # support + coupe
    mb_decor.lathe([(0.06, y - 0.4), (0.07, y - 0.3), (0.2 * s, y - 0.22), (0.26 * s, y - 0.08), (0.27 * s, y), (0.22 * s, y - 0.04), (0.0, y - 0.1)],
                   pos=(x, 0, z), mat=mat, seg=8, tint=tint)
    # flamme émissive
    mb_fx.lathe([(0.0, y - 0.04), (0.17 * s, y + 0.0), (0.23 * s, y + 0.1), (0.21 * s, y + 0.24), (0.14 * s, y + 0.4), (0.07 * s, y + 0.56), (0.0, y + 0.72)],
                pos=(x, 0, z), mat=flame_col, seg=7, cap0=False, cap1=False, tint=(1, 1, 1))


def brazier(mb, pos, h=1.1, r=0.5, mat='M_dark', flame_mat='M_flame', fx=None, tint=(0.25, 0.25, 0.27), legs=3, flame_h=0.9, seg=8):
    """brasero sur trépied : coupe + flamme."""
    x, y, z = pos
    fx = fx or mb
    for k in range(legs):
        a = TAU * k / legs
        lx, lz = x + math.cos(a) * r * 0.55, z + math.sin(a) * r * 0.55
        mb.add(p_box(0.1, h, 0.1, top=(0.06, 0.06)), mat, pos=(lx, y, lz), yaw=-a, pitch=0, roll=0, tint=tint)
    mb.lathe([(0.05, y + h - 0.15), (r * 0.5, y + h - 0.1), (r, y + h + 0.1), (r * 1.1, y + h + 0.22), (r * 0.95, y + h + 0.22), (r * 0.8, y + h + 0.12), (0, y + h + 0.1)],
             pos=(x, 0, z), mat=mat, seg=seg, tint=tint)
    fx.lathe([(0.0, y + h + 0.1), (r * 0.82, y + h + 0.16), (r * 0.8, y + h + 0.4), (r * 0.58, y + h + flame_h * 0.7), (r * 0.32, y + h + flame_h * 1.1), (r * 0.1, y + h + flame_h * 1.45), (0, y + h + flame_h * 1.7)],
             pos=(x, 0, z), mat=flame_mat, seg=8, cap0=False, cap1=False)


# ------------------------------------------------------------------ paysage lointain
def mound(mb, center, size, seed, mat='M_rock', tint=(1, 1, 1), sub=1, rough=0.35, vf=None, flat=0.15):
    V, F = p_rock(size[0], size[1], size[2], seed, sub, flat=flat, rough=rough)
    mb.add((V, F), mat, pos=center, tint=tint, vfun=vf)


def building(mb, pos, w, d, h, yaw=0.0, mat='M_plaster', tint=(1, 1, 1), roof='flat', roof_tint=(0.5, 0.25, 0.2), jit=0.06):
    mb.box((w, h, d), pos=pos, mat=mat, yaw=yaw, tint=tint, jit=jit, vfun=vgrad(0, h, 0.75, 1.05))
    if roof == 'gable':
        mb.add(p_extrude_xy([(-d / 2 - 0.2, 0), (d / 2 + 0.2, 0), (0, d * 0.35)], -w / 2 - 0.2, w / 2 + 0.2), 'M_roof', pos=(pos[0], pos[1] + h, pos[2]),
               yaw=yaw + math.pi / 2, tint=roof_tint, jit=0.1)
    elif roof == 'dome':
        r = min(w, d) * 0.5
        mb.lathe([(r * 1.02, 0), (r, r * 0.2), (r * 0.8, r * 0.7), (r * 0.4, r * 1.05), (0, r * 1.2)], pos=(pos[0], pos[1] + h, pos[2]), mat='M_roof',
                 seg=10, tint=roof_tint)
    elif roof == 'cone':
        r = min(w, d) * 0.6
        mb.cone(r, r * 1.3, pos=(pos[0], pos[1] + h, pos[2]), mat='M_roof', seg=8, tint=roof_tint)


# ------------------------------------------------------------------ glace / cristaux / divers
def icicles(mb, positions, rng, lmin=0.25, lmax=1.0, rmin=0.04, rmax=0.1, mat='M_ice', tint=(0.85, 0.95, 1.0), seg=5):
    """stalactites : positions (k,3) = point d'attache, pointe vers le bas."""
    pos = np.asarray(positions, float)
    k = len(pos)
    if k == 0:
        return
    tpl = p_lathe([(1.0, 0.0), (0.55, -0.45), (0.0, -1.0)], seg, True, False)
    L = rng.uniform(lmin, lmax, k)
    R = rng.uniform(rmin, rmax, k)
    sc = np.stack([R, L, R], 1)
    t = np.tile(s2l(tint), (k, 1)) * rng.uniform(0.85, 1.1, (k, 1))
    mb.add_many(tpl, mat, pos, yaw=rng.uniform(0, 6.28, k), scale=sc, tint=t)


def icicle_line(mb, rr, d, y, spacing, rng, lmin=0.2, lmax=0.9, **kw):
    P, N, T, s = rr.along(spacing, d, offset=rng.uniform(0, spacing))
    P = P + rng.uniform(-0.12, 0.12, P.shape)
    ys = y + rng.uniform(-0.05, 0.05, len(P))
    icicles(mb, np.stack([P[:, 0], ys, P[:, 1]], 1), rng, lmin, lmax, **kw)


def crystal_cluster(mb, cx, cz, r, h, rng, n=6, mat='M_crystal', c_lo='#2a78b8', c_hi='#bff0ff', y0=0.0, main_ratio=0.62, tip=0.22, seed=0,
                    lean=0.35):
    """grappe de cristaux : la base globale reste dans le rayon r."""
    vf = vgrad(y0, y0 + h, 0.55, 1.35)
    lo, hi = np.array(s2l(c_lo)), np.array(s2l(c_hi))

    def tintf(h0, hh):
        def f(V):
            t = np.clip((V[:, 1] - h0) / hh, 0, 1)[:, None]
            return lo[None, :] * (1 - t) + hi[None, :] * t
        return f
    V, F = p_crystal(r * main_ratio * 0.55, h, 6, tip, seed, 0.0, r * main_ratio, 0.08)
    mb.add((V, F), mat, pos=(cx, y0, cz), tint=lo, vfun=lambda P, hh=h, y00=y0: 0.5 + 1.2 * np.clip((P[:, 1] - y00) / hh, 0, 1))
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        br = r * 0.38
        rho = r - br - 0.01
        hh = h * rng.uniform(0.4, 0.75)
        ox, oz = cx + rho * math.cos(a), cz + rho * math.sin(a)
        V, F = p_crystal(br * 0.5, hh, 6, tip, seed + i + 1, lean, br, 0.1)
        # skew est le long de +x local : on yaw pour viser vers l'extérieur
        mb.add((V, F), mat, pos=(ox, y0, oz), yaw=-a, tint=lo * rng.uniform(0.9, 1.15),
               vfun=lambda P, hh_=hh, y00=y0: 0.5 + 1.3 * np.clip((P[:, 1] - y00) / hh_, 0, 1))
