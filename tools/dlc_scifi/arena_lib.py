"""Bibliothèque des arènes sci-fi (exécutée dans Blender) : réutilise tools/blender_arenas (lib_geo, lib_scene, kit, arena_common)
et ajoute poutres/tuyaux annulaires, garde-corps, réservoirs, planètes à UV sphériques, étoiles, arches de roche."""
import arena_env
arena_env.load('lib_scene')
import math
import numpy as np
from arena_common import *          # noqa: F401,F403  (G, np, RR, Scene, defmat, LAYOUT, build_*, add_strip, torches...)
import lib_geo as G                 # noqa: E402

ROOT = arena_env.ROOT
TEXDIR = arena_env.TEXDIR
OUTDIR = arena_env.OUTDIR


def T(n):
    return TEXDIR + '/' + n


# ------------------------------------------------------------------------------------------------ géométrie générique
def rot_to_y(d):
    """matrice 3x3 envoyant +Y vers d."""
    d = np.asarray(d, float)
    d = d / (np.linalg.norm(d) + 1e-12)
    y = np.array([0, 1.0, 0])
    c = float(y @ d)
    if c > 1 - 1e-9:
        return np.eye(3)
    if c < -1 + 1e-9:
        return np.diag([1.0, -1.0, -1.0])
    v = np.cross(y, d)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))


def cyl_between(mb, p0, p1, r0, r1=None, mat='M_steel', tint=(1, 1, 1), seg=8, caps=True, **kw):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    r1 = r0 if r1 is None else r1
    L = float(np.linalg.norm(p1 - p0))
    V, F = p_lathe([(r0, 0), (r1, L)], seg, caps, caps)
    V = V @ rot_to_y(p1 - p0).T + p0
    mb.add((V, F), mat, tint=tint, **kw)


def pipe_path(mb, pts, r, mat='M_steel', tint=(1, 1, 1), seg=7, joints=True, jr=1.35):
    pts = np.asarray(pts, float)
    for a, b in zip(pts[:-1], pts[1:]):
        cyl_between(mb, a, b, r, mat=mat, tint=tint, seg=seg, caps=False)
    if joints:
        for p in pts:
            mb.add(p_sphere(r * jr, seg, 4), mat, tint=tint, pos=tuple(p))


def box_between(mb, p0, p1, w, h, mat='M_steel', tint=(1, 1, 1), up=(0, 1, 0), **kw):
    """poutre rectangulaire entre deux points (section w x h)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    V, F = p_box(w, L, h)
    V = V @ rot_to_y(d).T + p0
    mb.add((V, F), mat, tint=tint, **kw)


def sphere_uv_mesh(R, nu=40, nv=22, c=(0, 0, 0), tilt=0.0):
    """sphère avec UV équirectangulaires. Retourne V, F, UV (couture dupliquée)."""
    V, UV = [], []
    for j in range(nv + 1):
        lat = math.pi * (0.5 - j / nv)
        for i in range(nu + 1):
            lon = 2 * math.pi * i / nu
            x, y, z = math.cos(lat) * math.cos(lon), math.sin(lat), math.cos(lat) * math.sin(lon)
            V.append((R * x, R * y, R * z))
            UV.append((i / nu, 1.0 - j / nv))
    V = np.array(V, float)
    if tilt:
        c_, s_ = math.cos(tilt), math.sin(tilt)
        V = V @ np.array([[c_, -s_, 0], [s_, c_, 0], [0, 0, 1]]).T
    V = V + np.asarray(c)
    F = []
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            F.append((a, a + 1, a + nu + 2, a + nu + 1))
    # orientation vers l'extérieur
    a, b, cc, d = F[nu * 3 + 5]
    n = np.cross(V[b] - V[a], V[d] - V[a])
    mid = (V[a] + V[b] + V[cc] + V[d]) / 4 - np.asarray(c)
    if np.dot(n, mid) < 0:
        F = [tuple(reversed(f)) for f in F]
    return V, F, np.array(UV)


def stars(mb, rng, n, center, rmin, rmax, az=(-80, 80), el=(-60, 25), size=(0.5, 1.4), mat='M_star', tints=None):
    """étoiles : petits tétraèdres émissifs sur une calotte (angles en degrés, el<0 = sous l'horizon)."""
    cx, cy, cz = center
    pos, scl, tint = [], [], []
    base = [(1.0, 0.95, 0.85), (0.85, 0.92, 1.0), (1.0, 1.0, 1.0), (1.0, 0.8, 0.6)]
    for i in range(n):
        a = math.radians(rng.uniform(*az))
        e = math.radians(rng.uniform(*el))
        r = rng.uniform(rmin, rmax)
        pos.append((cx + r * math.sin(a) * math.cos(e), cy + r * math.sin(e), cz - r * math.cos(a) * math.cos(e)))
        scl.append(rng.uniform(*size) * (1.0 + 1.4 * rng.random() ** 6))
        tint.append(s2l(base[rng.integers(len(base))]))
    tpl = p_cone(0.5, 1.0, 3)
    mb.add_many(tpl, mat, np.array(pos), yaw=rng.uniform(0, 6.28, n), pitch=rng.uniform(0, 6.28, n), scale=np.array(scl), tint=np.array(tint))


# ------------------------------------------------------------------------------------------------ éléments annulaires (le long du mur)
def ring_poly(mb, rr, rows_ref, mat, tint=(1, 1, 1), skip=None, uv=4.0, vfun=None):
    """rows_ref : liste de (rows, ref) ; chaque bande est une face."""
    for rows, ref in rows_ref:
        add_strip(mb, rr, rows, mat, ref, tint, skip, uv, vfun=vfun)


def ring_beam(mb, rr, d0, d1, y0, y1, mat='M_steel', tint=(1, 1, 1), skip=None, uv=2.0, bottom=True):
    ring_poly(mb, rr, [([(d0, y0), (d0, y1)], 'in'), ([(d0, y1), (d1, y1)], 'up'), ([(d1, y1), (d1, y0)], 'out')] +
              ([([(d1, y0), (d0, y0)], 'down')] if bottom else []), mat, tint, skip, uv)


def ring_pipe(mb, rr, d, y, r, mat='M_steel', tint=(1, 1, 1), skip=None, uv=1.0, k=8):
    ang = [2 * math.pi * i / k for i in range(k + 1)]
    for i in range(k):
        t0, t1 = ang[i], ang[i + 1]
        tm = (t0 + t1) / 2
        c, s = math.cos(tm), math.sin(tm)
        if abs(s) > abs(c):
            ref = 'up' if s > 0 else 'down'
        else:
            ref = 'out' if c > 0 else 'in'
        rows = [(d + r * math.cos(t0), y + r * math.sin(t0)), (d + r * math.cos(t1), y + r * math.sin(t1))]
        add_strip(mb, rr, rows, mat, ref, tint, skip, uv)


def ring_posts(mb, rr, d, y0, h, spacing, w=0.08, mat='M_steel', tint=(1, 1, 1), offset=0.0, skip_fn=None, depth=None):
    P, N, Tn, s = rr.along(spacing, d, offset=offset)
    k = 0
    for i in range(len(P)):
        if skip_fn is not None and skip_fn(P[i][0], P[i][1]):
            continue
        yaw = yaw_of(N[i][0], N[i][1])
        mb.box((w, h, depth or w), pos=(P[i][0], y0, P[i][1]), mat=mat, tint=tint, yaw=yaw)
        k += 1
    return k


def ring_rail(mb, rr, d, y0, h=1.05, post_sp=2.4, mat='M_steel', tint=(0.8, 0.8, 0.82), skip=None, skip_fn=None, r=0.032):
    ring_posts(mb, rr, d, y0, h, post_sp, 0.06, mat, tint, skip_fn=skip_fn)
    ring_pipe(mb, rr, d, y0 + h, r, mat, tint, skip, 1.0, k=6)
    ring_pipe(mb, rr, d, y0 + h * 0.5, r * 0.8, mat, tint, skip, 1.0, k=6)


def ring_lamps(mb, rr, d, y, spacing, mat='M_lamp_o', tint=(1, 1, 1), size=(0.22, 0.12, 0.1), offset=0.0, skip_fn=None, face='in'):
    """petites lampes encastrées/plaquées le long d'un mur (émissives)."""
    P, N, Tn, s = rr.along(spacing, d, offset=offset)
    for i in range(len(P)):
        if skip_fn is not None and skip_fn(P[i][0], P[i][1]):
            continue
        yaw = yaw_of(N[i][0], N[i][1])
        mb.box(size, pos=(P[i][0], y, P[i][1]), mat=mat, tint=tint, yaw=yaw)


def porthole_template(r=0.42, depth=0.12):
    """hublot face +Z : cadre (tore) + vitre bombée."""
    V1, F1 = p_torus(r, r * 0.16, 16, 5)
    V1 = V1 @ rotm(0, math.pi / 2, 0).T
    return V1, F1


def tank(mb, x, z, r, h, mat='M_steel', band_mat='M_dark', tint=(1, 1, 1), seg=20, domed=True, bands=(0.25, 0.75), y0=0.0, dome_h=None):
    """réservoir vertical : fût + dôme + bandes de renfort."""
    dh = dome_h if dome_h is not None else r * 0.35
    prof = [(r, y0), (r, y0 + h)]
    if domed:
        prof += [(r * 0.92, y0 + h + dh * 0.45), (r * 0.7, y0 + h + dh * 0.8), (r * 0.35, y0 + h + dh * 0.97), (0.0, y0 + h + dh)]
    mb.lathe(prof, pos=(x, 0, z), mat=mat, seg=seg, tint=tint, cap0=True, cap1=not domed)
    for b in bands:
        yb = y0 + h * b
        mb.lathe([(r * 1.0, yb - 0.07), (r * 1.045, yb - 0.04), (r * 1.045, yb + 0.04), (r * 1.0, yb + 0.07)], pos=(x, 0, z), mat=band_mat, seg=seg,
                 cap0=False, cap1=False)


def yaw_of_vec(v):
    return math.atan2(v[0], v[2])


def boulders(mb, rng, pos, sizes, mat='M_rock', tint=(1, 1, 1), n_tpl=6, sub=1, rough=0.32, flat=0.3, tints=None):
    """semis de rochers par instanciation : pos (k,3), sizes (k,3) = dimensions (x,y,z)."""
    pos = np.asarray(pos, float)
    sizes = np.asarray(sizes, float)
    k = len(pos)
    if k == 0:
        return
    tpl_id = rng.integers(0, n_tpl, k)
    for t in range(n_tpl):
        m = tpl_id == t
        if not np.any(m):
            continue
        VF = p_rock(1.0, 1.0, 1.0, 100 + t * 7, sub, flat=flat, rough=rough)
        kk = int(m.sum())
        if tints is None:
            tt = np.tile(s2l(tint), (kk, 1)) * rng.uniform(0.82, 1.12, (kk, 1))
        else:
            tt = np.asarray(tints)[m]
        mb.add_many(VF, mat, pos[m], yaw=rng.uniform(0, 6.28, kk), scale=sizes[m], tint=tt)


def rock_arch(mb, x, z, W, H, T, depth, yaw, rng, mat='M_rock', tint=(1, 1, 1), n=14, jit=0.25, y0=0.0):
    """arche de roche : polygone extrudé (profil irrégulier)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = math.pi * i / n
        j = 1 + jit * (rng.random() - 0.5) * 0.7
        outer.append((W / 2 * math.cos(t) * j, H * math.sin(t) * (1 + jit * (rng.random() - 0.5) * 0.4) + 0.0))
    for i in range(n + 1):
        t = math.pi * (n - i) / n
        j = 1 + jit * (rng.random() - 0.5) * 0.5
        inner.append(((W / 2 - T) * math.cos(t) * j, (H - T * 0.9) * math.sin(t) * (1 + jit * (rng.random() - 0.5) * 0.3)))
    # contour : base droite -> extérieur (droite vers gauche) -> base gauche -> intérieur (gauche vers droite)
    poly = [(W / 2, -0.5)] + outer + [(-W / 2, -0.5), (-(W / 2 - T), -0.5)] + [(p[0], max(p[1], -0.4)) for p in inner] + [((W / 2 - T), -0.5)]
    mb.add(p_extrude_xy(poly, -depth / 2, depth / 2), mat, pos=(x, y0, z), yaw=yaw, tint=tint, vfun=vnoise_f(0.18, 0.7, int(x * 7 + z * 3) & 255))


def mesa(mb, x, z, R, H, seed, y0=0.0, mat='M_rock', tint=(1, 1, 1), seg=12):
    prof = [(R, y0), (R * 0.97, y0 + H * 0.16), (R * 0.8, y0 + H * 0.2), (R * 0.82, y0 + H * 0.46), (R * 0.66, y0 + H * 0.5), (R * 0.67, y0 + H * 0.8),
            (R * 0.54, y0 + H * 0.84), (R * 0.55, y0 + H), (0.0, y0 + H)]
    rg = np.random.default_rng(seed)
    mb.lathe(prof, pos=(x, 0, z), mat=mat, seg=seg, tint=tint, jitter=0.08, cap0=False, cap1=False, yaw=rg.uniform(0, 6.28), vfun=vgrad(y0, y0 + H, 0.55, 1.2))
