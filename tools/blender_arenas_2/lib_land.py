"""Bibliothèque « paysage » pour les arènes ouvertes (volcan, glacier, ciel, jungle).
S'ajoute aux libs de blender_arenas (copiées ici) : bruit numpy pur (utilisable dans Blender), terrain en anneaux autour du
rectangle de jeu, tubes/balayages (lianes, racines, cordes, ponts), torches sur socle, nuages, arbres, cristaux de glace, etc.
Coordonnées JEU (x droite, y haut, z vers le joueur)."""
import math
import numpy as np
import lib_geo as G
from lib_geo import *
from lib_geo import _fix_closed
from arena_common import *

TAU = 2 * math.pi


def TP(name):
    """chemin d'une texture de l'arène (extension .jpg ou .png, avec ou sans suffixe donné)."""
    import os
    base = name.rsplit('.', 1)[0] if name.endswith(('.png', '.jpg')) else name
    for ext in ('.jpg', '.png'):
        p = TEXDIR + '/' + base + ext
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


# ------------------------------------------------------------------ bruit numpy (déterministe, sans scipy)
def _hash(ix, iy, seed):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + int(seed) * 1442695041 + 12345) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return ((n & 0xFFFFFF) / 16777216.0)


def vn(x, y, seed=0):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    x0, y0 = np.floor(x), np.floor(y)
    fx, fy = x - x0, y - y0
    u, v = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _hash(x0, y0, seed), _hash(x0 + 1, y0, seed)
    c, d = _hash(x0, y0 + 1, seed), _hash(x0 + 1, y0 + 1, seed)
    return (a + (b - a) * u) + ((c + (d - c) * u) - (a + (b - a) * u)) * v


def fbm2(x, y, octv=4, seed=0, gain=0.5):
    out, amp, f, norm = 0.0, 1.0, 1.0, 0.0
    for o in range(octv):
        out = out + amp * vn(x * f, y * f, seed + 17 * o)
        norm += amp
        amp *= gain
        f *= 2.03
    return out / norm


def ridge2(x, y, octv=4, seed=0):
    """bruit en crêtes (0..1), arêtes vives."""
    out, amp, f, norm = 0.0, 1.0, 1.0, 0.0
    for o in range(octv):
        n = 1.0 - np.abs(2 * vn(x * f, y * f, seed + 31 * o) - 1)
        out = out + amp * n * n
        norm += amp
        amp *= 0.5
        f *= 2.1
    return out / norm


def sstep(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def lin(c):
    """couleur sRGB (hex ou tuple) -> linéaire np.array(3)."""
    return np.asarray(s2l(c), float)


def cgrad(t, stops):
    """dégradé linéaire : t (n,) ; stops [(pos, '#hex'), ...] -> (n,3) linéaire."""
    t = np.clip(np.asarray(t, float), 0, 1)
    pos = [p for p, _ in stops]
    cols = [lin(c) for _, c in stops]
    return np.stack([np.interp(t, pos, [c[k] for c in cols]) for k in range(3)], -1)


def outline_sdf(x, z):
    return RRECT.sdf(np.asarray(x, float), np.asarray(z, float))


# ------------------------------------------------------------------ terrain en anneaux
def ring_terrain(mb, rr, ds, hfun, mat, tintfun=None, tint=(1, 1, 1), skip=None, hide=None, uv=None, flip=False, split=None):
    """maille en anneaux concentriques (offsets ds par rapport au bord du terrain) ; la hauteur vient de hfun(x, z, d) -> y.
    tintfun(V, D) -> (n,3) linéaire. hide(cx, cy, cz, d) -> bool retire des faces.
    mat : nom de matériau ou liste de noms ; split(cx, cy, cz, ny, d) -> indice dans la liste (ny = composante Y de la normale)."""
    rows = [(float(d), 0.0) for d in ds]
    V, F, UV = ring_strip(rr, rows, ref='up', skip=skip, uvsize=4.0)
    V = V.copy()
    W = len(V) // len(ds)
    D = np.repeat(np.array(ds, float), W)
    V[:, 1] = hfun(V[:, 0], V[:, 2], D)
    mats = mat if isinstance(mat, (list, tuple)) else [mat]
    groups = [[] for _ in mats]
    for f in F:
        pts = V[list(f)]
        c = pts.mean(0)
        Dm = float(np.mean([D[i] for i in f]))
        if hide is not None and hide(c[0], c[1], c[2], Dm):
            continue
        k = 0
        if split is not None:
            nrm = np.cross(pts[1] - pts[0], pts[-1] - pts[0])
            ny = abs(nrm[1]) / max(np.linalg.norm(nrm), 1e-9)
            k = int(split(c[0], c[1], c[2], ny, Dm))
        groups[k].append(tuple(reversed(f)) if flip else f)
    t = tintfun(V, D) if tintfun is not None else tint
    for m_, g in zip(mats, groups):
        if not g:
            continue
        used = np.unique(np.array([i for f in g for i in f]))
        remap = -np.ones(len(V), np.int64)
        remap[used] = np.arange(len(used))
        g2 = [tuple(int(remap[i]) for i in f) for f in g]
        t2 = t[used] if isinstance(t, np.ndarray) and t.ndim == 2 else t
        mb.add((V[used], g2), m_, tint=t2, uv=None if uv is None else uv[used])
    return V, F


def ring_pts(rr, d):
    P, N, _ = rr.pts(d)
    return P, N


# ------------------------------------------------------------------ tubes / balayages
def _frames(pts):
    pts = np.asarray(pts, float)
    n = len(pts)
    T = np.zeros_like(pts)
    T[1:-1] = pts[2:] - pts[:-2]
    T[0] = pts[1] - pts[0]
    T[-1] = pts[-1] - pts[-2]
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-9)
    ref = np.array([0.0, 1.0, 0.0]) if abs(T[0][1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    N = np.zeros_like(T)
    B = np.zeros_like(T)
    n0 = np.cross(T[0], ref)
    n0 /= np.linalg.norm(n0)
    N[0] = n0
    for i in range(1, n):
        v = N[i - 1] - T[i] * np.dot(N[i - 1], T[i])
        ln = np.linalg.norm(v)
        N[i] = v / ln if ln > 1e-9 else N[i - 1]
    for i in range(n):
        B[i] = np.cross(T[i], N[i])
    return T, N, B


def p_tube(pts, radii, seg=6, cap0=True, cap1=True, flat=None):
    """tube balayé le long d'une polyligne 3D (rayons par point). flat=(ky,kn) pour aplatir la section (rubans)."""
    pts = np.asarray(pts, float)
    n = len(pts)
    if np.isscalar(radii):
        radii = np.full(n, float(radii))
    radii = np.asarray(radii, float)
    T, N, B = _frames(pts)
    V = []
    for i in range(n):
        for j in range(seg):
            a = TAU * j / seg
            ca, sa = math.cos(a), math.sin(a)
            kn, kb = (1.0, 1.0) if flat is None else flat
            V.append(pts[i] + radii[i] * (ca * kn * N[i] + sa * kb * B[i]))
    F = []
    for i in range(n - 1):
        for j in range(seg):
            j2 = (j + 1) % seg
            F.append((i * seg + j, (i + 1) * seg + j, (i + 1) * seg + j2, i * seg + j2))
    # orientation vers l'extérieur
    a, b, c, d = F[0]
    V = np.array(V, float)
    nrm = np.cross(V[b] - V[a], V[d] - V[a])
    if np.dot(nrm, V[a] - pts[0]) < 0:
        F = [tuple(reversed(f)) for f in F]
    if cap0:
        cf = tuple(range(seg))
        # normale vers -T
        nn = np.cross(V[1] - V[0], V[2] - V[0])
        F.append(cf if np.dot(nn, -T[0]) > 0 else tuple(reversed(cf)))
    if cap1:
        cf = tuple((n - 1) * seg + j for j in range(seg))
        nn = np.cross(V[(n - 1) * seg + 1] - V[(n - 1) * seg], V[(n - 1) * seg + 2] - V[(n - 1) * seg])
        F.append(cf if np.dot(nn, T[-1]) > 0 else tuple(reversed(cf)))
    return V, F


def p_sweep(profile, path, up=(0, 1, 0), caps=True):
    """balaie un profil fermé 2D (lat, haut) le long d'un chemin 3D ; le profil est dans le plan (côté, haut)."""
    path = np.asarray(path, float)
    n = len(path)
    m = len(profile)
    T = np.zeros_like(path)
    T[1:-1] = path[2:] - path[:-2]
    T[0] = path[1] - path[0]
    T[-1] = path[-1] - path[-2]
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-9)
    upv = np.asarray(up, float)
    V = []
    for i in range(n):
        side = np.cross(upv, T[i])
        side /= max(np.linalg.norm(side), 1e-9)
        upi = np.cross(T[i], side)
        for (u, v) in profile:
            V.append(path[i] + side * u + upi * v)
    V = np.array(V, float)
    F = []
    for i in range(n - 1):
        for k in range(m):
            k2 = (k + 1) % m
            F.append((i * m + k, i * m + k2, (i + 1) * m + k2, (i + 1) * m + k))
    if caps:
        F.append(tuple(reversed(range(m))))
        F.append(tuple((n - 1) * m + k for k in range(m)))
    return _fix_closed(V, F)


def polyline_len(pts):
    pts = np.asarray(pts, float)
    return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))


def catenary(p0, p1, sag, n=10):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    out = []
    for k in range(n + 1):
        t = k / n
        p = p0 + (p1 - p0) * t
        p[1] -= sag * 4 * t * (1 - t)
        out.append(p)
    return np.array(out)


# ------------------------------------------------------------------ torche/brasero sur socle, à l'extérieur du terrain
def torch_frame(i):
    """(x, z, nx, nz, sdf) : position torche i, normale sortante du contour de jeu, distance signée."""
    t = TORCHES[i]
    s = RRECT.s_nearest(t['x'], t['z'])
    Pw, n = RRECT.at_base(s)
    return t['x'], t['z'], float(n[0]), float(n[1]), float(RRECT.sdf(np.array(t['x']), np.array(t['z'])))


# ------------------------------------------------------------------ nuages (blobs, opaques)
def cloud(mb, cx, cy, cz, sx, sy, sz, rng, mat='M_cloud', n=6, top='#fff4dc', bot='#f0b890', sub=1):
    """nuage cartoon : blobs d'icosphères lissés, teinte haute chaude, ventre plus ambré."""
    for k in range(n):
        a = rng.uniform(0, TAU)
        rho = rng.uniform(0.0, 0.62)
        r = rng.uniform(0.5, 1.0)
        bx, bz = cx + math.cos(a) * rho * sx, cz + math.sin(a) * rho * sz
        by = cy + rng.uniform(-0.1, 0.25) * sy
        V, F = p_ico(1.0, sub)
        V = V * np.array([sx * r * 0.5, sy * r * 0.5 * rng.uniform(0.7, 1.0), sz * r * 0.5])
        V = V + np.array([bx, by, bz])
        t = np.clip((V[:, 1] - (cy - sy * 0.4)) / (sy * 0.9), 0, 1)[:, None]
        col = lin(bot)[None, :] * (1 - t) + lin(top)[None, :] * t
        mb.add((V, F), mat, tint=col * rng.uniform(0.92, 1.05))


# ------------------------------------------------------------------ colonnes hexagonales
def hex_prism(r, h, rot=0.0, tilt=0.0, top_cut=0.0):
    """prisme hexagonal (rayon circonscrit r, hauteur h) ; top_cut = biseau d'une face du dessus."""
    V = []
    for j in range(6):
        a = rot + TAU * j / 6
        V.append((r * math.cos(a), 0.0, r * math.sin(a)))
    for j in range(6):
        a = rot + TAU * j / 6
        y = h - top_cut * (0.5 + 0.5 * math.cos(a - tilt))
        V.append((r * math.cos(a), y, r * math.sin(a)))
    V = np.array(V, float)
    F = []
    for j in range(6):
        j2 = (j + 1) % 6
        F.append((j, 6 + j, 6 + j2, j2))
    F.append((11, 10, 9, 8, 7, 6))
    F.append(tuple(range(6)))
    return _fix_closed(V, F)


def hex_cluster(mb, x, z, r_out, heights, mat, tint, rng, top_mat=None, jit=0.08, gap=0.03, tops=None):
    """grappe de colonnes hexagonales (1 centrale + 6) dont la base reste dans le rayon r_out."""
    rho = r_out / (1 + math.sqrt(3))  # circonscrit
    rho_c = rho * (1 - gap)
    centers = [(0.0, 0.0)] + [(math.sqrt(3) * rho * math.cos(math.pi / 6 + k * math.pi / 3 + 0.0),
                               math.sqrt(3) * rho * math.sin(math.pi / 6 + k * math.pi / 3 + 0.0)) for k in range(6)]
    # hexagones « pointe en haut » : sommets à rot=pi/6 pour que les voisins se touchent par les côtés
    out = []
    for i, (cx, cz) in enumerate(centers):
        h = heights[i % len(heights)]
        V, F = hex_prism(rho_c, h, rot=0.0, tilt=rng.uniform(0, TAU), top_cut=rng.uniform(0.0, 0.35) * (i > 0))
        t = np.asarray(tint, float) * rng.uniform(1 - jit, 1 + jit)
        mb.add((V, F), mat, pos=(x + cx, 0.0, z + cz), tint=t)
        out.append((x + cx, h, z + cz))
    return out


# ------------------------------------------------------------------ ruban plaqué sur le terrain (coulées de lave, ruisseaux, chemins)
def drape_ribbon(mb, path, widths, hfun, mat, yoff=0.25, across=5, tint=(1, 1, 1), uvlen=4.0, edge_sink=0.35, tint_edge=None):
    """path (n,2) xz ; widths (n,) ; hfun(x,z)->y. UV : u le long du ruban, v en travers (flux le long de U)."""
    path = np.asarray(path, float)
    n = len(path)
    widths = np.broadcast_to(np.asarray(widths, float), (n,)).copy()
    T = np.zeros_like(path)
    T[1:-1] = path[2:] - path[:-2]
    T[0] = path[1] - path[0]
    T[-1] = path[-1] - path[-2]
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-9)
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    cum = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    V, UV, TT = [], [], []
    c0 = lin(tint) if not isinstance(tint, np.ndarray) else tint
    ce = c0 if tint_edge is None else lin(tint_edge)
    for i in range(n):
        for j in range(across):
            f = j / (across - 1)
            lat = (f - 0.5) * widths[i]
            x, z = path[i, 0] + N[i, 0] * lat, path[i, 1] + N[i, 1] * lat
            e = abs(2 * f - 1)
            y = float(hfun(np.array(x), np.array(z))) + yoff - edge_sink * e ** 3
            V.append((x, y, z))
            UV.append((cum[i] / uvlen, f * widths[i] / uvlen))
            TT.append(c0 * (1 - e ** 2) + ce * e ** 2)
    F = []
    for i in range(n - 1):
        for j in range(across - 1):
            a = i * across + j
            F.append((a, a + 1, a + across + 1, a + across))
    V = np.array(V, float)
    # orientation vers le haut
    a, b, c, d = F[0]
    if np.cross(V[b] - V[a], V[d] - V[a])[1] < 0:
        F = [tuple(reversed(f)) for f in F]
    mb.add((V, F), mat, tint=np.array(TT), uv=np.array(UV))


# ------------------------------------------------------------------ pont de pierre en arc
def stone_bridge(mb, p0, p1, width, y0, y1, rise, mat_deck='M_stone', tint=(1, 1, 1), par_h=0.5, par_w=0.3, thick=0.6, n=14, piers=2,
                 pier_mat=None, pier_bottom=-3.0, post_every=2, glow_mat=None):
    """pont de (x,z) p0 à p1 ; tablier arqué (de y0 à y1 + rise*sin), parapets, piles qui plongent jusqu'à pier_bottom."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    ts = np.linspace(0, 1, n + 1)
    path = np.array([[p0[0] + (p1[0] - p0[0]) * t, y0 + (y1 - y0) * t + rise * math.sin(math.pi * t), p0[1] + (p1[1] - p0[1]) * t] for t in ts])
    hw = width / 2
    prof = [(-hw, -thick), (hw, -thick), (hw, 0.0), (-hw, 0.0)]
    mb.add(p_sweep(prof, path, caps=True), mat_deck, tint=tint)
    # bordures / parapets
    for sg in (-1, 1):
        lat = sg * (hw - par_w / 2)
        pp = [(lat - par_w / 2, 0.0), (lat + par_w / 2, 0.0), (lat + par_w / 2 * 0.9, par_h), (lat - par_w / 2 * 0.9, par_h)]
        mb.add(p_sweep(pp, path, caps=True), mat_deck, tint=tint)
    # piles
    pm = pier_mat or mat_deck
    d = p1 - p0
    yaw = math.atan2(d[0], d[1])
    for k in range(1, piers + 1):
        t = k / (piers + 1)
        x, z = p0[0] + d[0] * t, p0[1] + d[1] * t
        yt = y0 + (y1 - y0) * t + rise * math.sin(math.pi * t) - thick * 0.9
        h = yt - pier_bottom
        mb.add(p_box(width * 0.78, h, 1.0, top=(width * 0.7, 0.8)), pm, pos=(x, pier_bottom, z), yaw=yaw, tint=tint, jit=0.05)
        mb.add(p_box(width * 0.9, 0.22, 1.2), pm, pos=(x, yt - 0.22, z), yaw=yaw, tint=tint)
    # potelets sur les parapets
    for k in range(post_every, n, post_every):
        pt = path[k]
        side = np.array([math.cos(yaw), -math.sin(yaw)])
        for sg in (-1, 1):
            c = pt + np.array([side[0] * sg * (hw - par_w / 2), 0.0, side[1] * sg * (hw - par_w / 2)])
            mb.add(p_box(par_w * 1.25, par_h + 0.32, par_w * 1.25), mat_deck, pos=(c[0], c[1], c[2]), yaw=yaw, tint=tint, bev=0.02)
    return path


# ------------------------------------------------------------------ colonne de fumée (blobs opaques, dégradé de teinte)
def smoke_column(mb, x, y0, z, h, r0, rng, mat='M_smoke', wind=(0.5, 0.3), n=10, c_low='#b8602c', c_mid='#4a4341', c_top='#8d867f', grow=3.0, sub=1):
    """colonne de fumée : blobs lissés de plus en plus gros (2 par palier en haut), dégradé chaud -> gris."""
    for k in range(n):
        t0 = k / max(n - 1, 1)
        for b in range(1 if t0 < 0.35 else 2):
            t = float(np.clip(t0 + rng.uniform(-0.05, 0.05), 0, 1))
            r = r0 * (0.65 + grow * t ** 0.85) * rng.uniform(0.7, 1.2)
            yy = y0 + h * t + r * 0.2
            lat = r * (0.15 + 0.5 * t)
            px = x + wind[0] * h * 0.35 * t * t + rng.uniform(-lat, lat)
            pz = z + wind[1] * h * 0.35 * t * t + rng.uniform(-lat, lat)
            V, F = p_ico(1.0, sub)
            V = V * np.array([r, r * rng.uniform(0.7, 0.95), r])
            V = V + np.array([px, yy, pz])
            tt = np.clip((V[:, 1] - y0) / max(h, 1e-3), 0, 1)
            col = cgrad(tt, [(0.0, c_low), (0.2, c_mid), (1.0, c_top)])
            mb.add((V, F), mat, tint=col * rng.uniform(0.85, 1.1))
