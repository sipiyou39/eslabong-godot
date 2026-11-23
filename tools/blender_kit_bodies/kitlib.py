"""Bibliothèque de modélisation procédurale du kit (Blender 5.2, exécutée avec `Blender -b --python`).

Convention : toute la géométrie est écrite en repère CONTRAT (x gauche du perso, y haut, z avant),
convertie vers Blender (x, -z, y) à la création du mesh ; l'export glTF (Y-up) restitue donc exactement
les coordonnées du contrat.
Masque de couleur COLOR_0 : (R,G,B) = primaire / secondaire / accent, reste = peau ; A = AO cuite.
"""
import math, os, sys, json
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SKIN = (0.0, 0.0, 0.0)
R = (1.0, 0.0, 0.0)
G = (0.0, 1.0, 0.0)
B = (0.0, 0.0, 1.0)

PIVOTS = {
    "pelvis": (0.0, 0.74, 0.0), "torso": (0.0, 0.78, 0.0), "head": (0.0, 1.20, 0.0),
    "shoulder_l": (0.30, 1.10, 0.0), "shoulder_r": (-0.30, 1.10, 0.0),
    "hip_l": (0.13, 0.72, 0.0), "hip_r": (-0.13, 0.72, 0.0),
    "hand_l": (0.34, 0.62, 0.02), "hand_r": (-0.34, 0.62, 0.02),
}


def _sp(x, p):
    return np.sign(x) * np.abs(x) ** p


# --------------------------------------------------------------------------- géométrie
class Geo:
    """Maillage numpy : V (n,3), F liste de tuples (quads / tris / ngons)."""

    def __init__(s, V, F):
        s.V = np.asarray(V, float).reshape(-1, 3)
        s.F = [tuple(int(i) for i in f) for f in F]

    def copy(s):
        return Geo(s.V.copy(), list(s.F))

    # transformations (en place, chaînables)
    def t(s, x=0.0, y=0.0, z=0.0):
        s.V = s.V + np.array([x, y, z], float)
        return s

    def at(s, p):
        return s.t(*p)

    def sc(s, x=1.0, y=None, z=None):
        if y is None:
            y = x
        if z is None:
            z = x
        s.V = s.V * np.array([x, y, z], float)
        if x * y * z < 0:
            s.F = [tuple(reversed(f)) for f in s.F]
        return s

    def rot(s, axis, deg, about=(0, 0, 0)):
        a = math.radians(deg)
        c, sn = math.cos(a), math.sin(a)
        if axis == 0:
            M = np.array([[1, 0, 0], [0, c, -sn], [0, sn, c]])
        elif axis == 1:
            M = np.array([[c, 0, sn], [0, 1, 0], [-sn, 0, c]])
        else:
            M = np.array([[c, -sn, 0], [sn, c, 0], [0, 0, 1]])
        o = np.array(about, float)
        s.V = (s.V - o) @ M.T + o
        return s

    def rx(s, d, about=(0, 0, 0)):
        return s.rot(0, d, about)

    def ry(s, d, about=(0, 0, 0)):
        return s.rot(1, d, about)

    def rz(s, d, about=(0, 0, 0)):
        return s.rot(2, d, about)

    def aim(s, d, roll=0.0):
        """tourne la géométrie pour que son axe +Y pointe vers d."""
        d = np.asarray(d, float)
        d = d / (np.linalg.norm(d) + 1e-12)
        y = np.array([0, 1.0, 0])
        v = np.cross(y, d)
        c = float(np.dot(y, d))
        if np.linalg.norm(v) < 1e-9:
            M = np.eye(3) if c > 0 else np.diag([1, -1, -1.0])
        else:
            vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
            M = np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))
        if roll:
            s.rot(1, roll)
        s.V = s.V @ M.T
        return s

    def mir(s):
        g = s.copy()
        g.V[:, 0] *= -1
        g.F = [tuple(reversed(f)) for f in g.F]
        return g

    def map(s, fn):
        s.V = np.asarray(fn(s.V), float)
        return s

    def fix(s):
        """oriente les faces vers l'extérieur (volume signé > 0)."""
        vol = 0.0
        for f in s.F:
            for k in range(1, len(f) - 1):
                a, b, c = s.V[f[0]], s.V[f[k]], s.V[f[k + 1]]
                vol += np.dot(a, np.cross(b, c))
        if vol < 0:
            s.F = [tuple(reversed(f)) for f in s.F]
        return s

    def tris(s):
        return sum(len(f) - 2 for f in s.F)


def merge(geos):
    Vs, Fs, off = [], [], 0
    for g in geos:
        Vs.append(g.V)
        Fs += [tuple(i + off for i in f) for f in g.F]
        off += len(g.V)
    return Geo(np.vstack(Vs), Fs)


# --------------------------------------------------------------------------- primitives
def sec(y, rx, rz=None, cx=0.0, cz=0.0, n=12, e=2.0, phase=0.0, warp=0.0):
    """anneau (n,3) superelliptique dans le plan XZ à la hauteur y. e=2 ellipse, e>2 plus carré.
    warp>0 : densifie les points vers l'avant (+Z)."""
    if rz is None:
        rz = rx
    t = phase + 2 * np.pi * np.arange(n) / n
    if warp:
        t = t - warp * np.sin(t - np.pi / 2)
    c, s_ = np.cos(t), np.sin(t)
    p = 2.0 / e
    x = rx * _sp(c, p) + cx
    z = rz * _sp(s_, p) + cz
    return np.stack([x, np.full(n, y), z], axis=1)


def loft(rings, cap0=True, cap1=True, closed=True):
    """rings : liste d'anneaux (n,3) de même n, ou de points (3,) isolés (pôles)."""
    V, F = [], []
    idx = []
    for r in rings:
        r = np.asarray(r, float)
        if r.ndim == 1:
            idx.append(('p', len(V)))
            V.append(r)
        else:
            idx.append(('r', len(V)))
            V.extend(r)
    n = max(len(r) for r in rings if np.asarray(r).ndim == 2)
    for i in range(len(rings) - 1):
        (ka, a), (kb, b) = idx[i], idx[i + 1]
        for j in range(n):
            j2 = (j + 1) % n
            if ka == 'p' and kb == 'p':
                continue
            if ka == 'p':
                F.append((a, b + j2, b + j))
            elif kb == 'p':
                F.append((a + j, a + j2, b))
            else:
                F.append((a + j, a + j2, b + j2, b + j))
    # bouchons
    for cap, (k, a), flip in ((cap0, idx[0], True), (cap1, idx[-1], False)):
        if cap and k == 'r':
            if cap == 'fan':
                c = len(V)
                V.append(np.mean(V[a:a + n], axis=0))
                for j in range(n):
                    f = (c, a + (j + 1) % n, a + j) if flip else (c, a + j, a + (j + 1) % n)
                    F.append(f)
            else:
                f = tuple(range(a, a + n))
                F.append(tuple(reversed(f)) if flip else f)
    return Geo(np.array(V), F).fix()


def lathe(profile, n=16, rx=1.0, rz=None, e=2.0, cx=0.0, cz=0.0, y0=0.0, phase=0.0, cap='ngon'):
    """surface de révolution autour de Y ; profile = [(rayon, y), ...] du bas vers le haut."""
    if rz is None:
        rz = rx
    rings = []
    for k, (r, y) in enumerate(profile):
        if r < 1e-6:
            rings.append(np.array([cx, y + y0, cz]))
        else:
            rings.append(sec(y + y0, r * rx, r * rz, cx, cz, n, e, phase))
    return loft(rings, cap0=cap, cap1=cap)


def sphere(rx=0.5, ry=None, rz=None, n=16, m=10, e=(1.0, 1.0), c=(0, 0, 0)):
    """superellipsoïde ; e=(e_lat, e_lon) ; 1 = sphère, <1 = plus carré."""
    if ry is None:
        ry = rx
    if rz is None:
        rz = rx
    V, F = [], []
    V.append((c[0], c[1] - ry, c[2]))
    for i in range(1, m):
        phi = -np.pi / 2 + np.pi * i / m
        cp, sp = math.cos(phi), math.sin(phi)
        yy = _sp(sp, e[0]) * ry
        k = _sp(cp, e[0])
        for j in range(n):
            th = 2 * np.pi * j / n
            V.append((c[0] + k * _sp(math.cos(th), e[1]) * rx, c[1] + yy, c[2] + k * _sp(math.sin(th), e[1]) * rz))
    V.append((c[0], c[1] + ry, c[2]))
    top = len(V) - 1
    for j in range(n):
        F.append((0, 1 + (j + 1) % n, 1 + j))
    for i in range(m - 2):
        a, b = 1 + i * n, 1 + (i + 1) * n
        for j in range(n):
            j2 = (j + 1) % n
            F.append((a + j, a + j2, b + j2, b + j))
    a = 1 + (m - 2) * n
    for j in range(n):
        F.append((a + j, a + (j + 1) % n, top))
    return Geo(np.array(V), F).fix()


def _axis_pts(h, r, s, d):
    pts = []
    for j in range(s, -1, -1):
        pts.append(-(h - r) - r * math.tan(math.radians(45.0 * j / s)))
    for k in range(1, d):
        pts.append(-(h - r) + 2 * (h - r) * k / d)
    for j in range(0, s + 1):
        pts.append((h - r) + r * math.tan(math.radians(45.0 * j / s)))
    return pts


def rbox(hx, hy, hz, r=0.02, s=2, d=(1, 1, 1), c=(0, 0, 0)):
    """boîte à arêtes arrondies (rayon r), demi-dimensions hx,hy,hz ; d = subdivisions internes par axe."""
    r = min(r, hx * 0.98, hy * 0.98, hz * 0.98)
    ax = [_axis_pts(hx, r, s, d[0]), _axis_pts(hy, r, s, d[1]), _axis_pts(hz, r, s, d[2])]
    h = np.array([hx, hy, hz])
    pts = {}
    V, F = [], []

    def vid(p):
        key = tuple(np.round(p / 1e-6).astype(np.int64))
        if key not in pts:
            pts[key] = len(V)
            V.append(p)
        return pts[key]

    for a in range(3):
        b, cc = (a + 1) % 3, (a + 2) % 3
        for sg in (-1, 1):
            grid = []
            for ub in ax[b]:
                row = []
                for uc in ax[cc]:
                    p = np.zeros(3)
                    p[a] = sg * h[a]
                    p[b] = ub
                    p[cc] = uc
                    row.append(vid(p.copy()))
                grid.append(row)
            for i in range(len(grid) - 1):
                for j in range(len(grid[0]) - 1):
                    F.append((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    V = np.array(V)
    inner = np.clip(V, -(h - r), (h - r))
    dv = V - inner
    ln = np.linalg.norm(dv, axis=1, keepdims=True)
    V = np.where(ln > 1e-9, inner + dv / np.maximum(ln, 1e-9) * r, V)
    g = Geo(V + np.array(c), F)
    return g.fix()


def tube(path, rad, n=10, e=2.0, cap0=True, cap1=True, up=(0, 0, 1.0), twist=0.0):
    """tube le long d'une courbe ; rad = scalaires ou (rx, rz) ; transport parallèle du repère."""
    path = np.asarray(path, float)
    m = len(path)
    tg = np.zeros_like(path)
    tg[1:-1] = path[2:] - path[:-2]
    tg[0] = path[1] - path[0]
    tg[-1] = path[-1] - path[-2]
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-12
    u0 = np.array(up, float)
    if abs(np.dot(u0, tg[0])) > 0.95:
        u0 = np.array([1.0, 0, 0])
    u = u0 - np.dot(u0, tg[0]) * tg[0]
    u /= np.linalg.norm(u)
    rings = []
    for i in range(m):
        if i > 0:
            u = u - np.dot(u, tg[i]) * tg[i]
            nu = np.linalg.norm(u)
            if nu < 1e-6:
                u = np.cross(tg[i], [0, 0, 1.0])
                nu = np.linalg.norm(u)
            u /= nu
        v = np.cross(tg[i], u)
        ra = rad[i]
        if np.isscalar(ra):
            rx_, rz_ = ra, ra
        else:
            rx_, rz_ = ra
        if rx_ < 1e-6 and rz_ < 1e-6:
            rings.append(path[i].copy())
            continue
        t = 2 * np.pi * np.arange(n) / n + twist * i
        p = 2.0 / e
        cu = _sp(np.cos(t), p) * rx_
        sv = _sp(np.sin(t), p) * rz_
        rings.append(path[i] + np.outer(cu, u) + np.outer(sv, v))
    return loft(rings, cap0, cap1)


def bez(p0, p1, p2, p3, m=8):
    t = np.linspace(0, 1, m)[:, None]
    p0, p1, p2, p3 = [np.asarray(p, float) for p in (p0, p1, p2, p3)]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def curve(pts, m=12):
    """spline Catmull-Rom passant par les points."""
    pts = np.asarray(pts, float)
    P = np.vstack([pts[0] * 2 - pts[1], pts, pts[-1] * 2 - pts[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(m if i < len(P) - 3 else m + 1):
            t = k / m
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def torus(Rr=0.1, r=0.02, n=20, m=8, c=(0, 0, 0)):
    """tore autour de Y."""
    rings = []
    for i in range(n):
        a = 2 * np.pi * i / n
        ctr = np.array([math.cos(a) * Rr, 0, math.sin(a) * Rr])
        rad = np.array([math.cos(a), 0, math.sin(a)])
        rr = []
        for j in range(m):
            b = 2 * np.pi * j / m
            rr.append(ctr + rad * math.cos(b) * r + np.array([0, math.sin(b) * r, 0]))
        rings.append(rr)
    V, F = [], []
    for ring in rings:
        V.extend(ring)
    for i in range(n):
        i2 = (i + 1) % n
        for j in range(m):
            j2 = (j + 1) % m
            F.append((i * m + j, i2 * m + j, i2 * m + j2, i * m + j2))
    return Geo(np.array(V) + np.array(c), F).fix()


def poly_lathe(poly, prof, n_round=None):
    """plaque gonflée : poly (N,2) dans le plan XY, prof = [(facteur_échelle, z), ...] du dos vers le devant.
    facteur 0 = point au centre (bouchon)."""
    poly = np.asarray(poly, float)
    cen = poly.mean(axis=0)
    rings = []
    for k, z in prof:
        if k < 1e-6:
            rings.append(np.array([cen[0], cen[1], z]))
        else:
            p = cen + (poly - cen) * k
            rings.append(np.column_stack([p, np.full(len(p), z)]))
    return loft(rings, cap0='ngon', cap1='ngon')


def cone(r=0.05, h=0.2, n=10, base=0.0, rz=None, tip=None):
    g = lathe([(r, 0.0), (r * 0.55, h * 0.45), (0.0, h)], n=n, rz=rz)
    if base:
        g.t(0, base, 0)
    return g


def spike(base_pt, tip_pt, r=0.04, n=8, bulge=0.6):
    """pointe conique de base_pt à tip_pt."""
    bp, tp = np.asarray(base_pt, float), np.asarray(tip_pt, float)
    d = tp - bp
    L = np.linalg.norm(d)
    g = lathe([(r, 0.0), (r * bulge, L * 0.5), (0.0, L)], n=n)
    return g.aim(d).at(bp)


def horn(base, tip, r=0.06, curve_out=0.1, curve_dir=(0, 0, 1), n=8, m=8, up_hint=(0, 1, 0)):
    """corne courbe : de base à tip, bombée vers curve_dir."""
    b, t = np.asarray(base, float), np.asarray(tip, float)
    cd = np.asarray(curve_dir, float)
    mid1 = b + (t - b) * 0.35 + cd * curve_out
    mid2 = b + (t - b) * 0.7 + cd * curve_out * 0.8
    path = bez(b, mid1, mid2, t, m)
    rad = [r * (1 - k / (m - 1)) ** 0.85 + 1e-4 for k in range(m)]
    rad[-1] = 0.0
    return tube(path, rad, n=n, cap0='ngon', up=up_hint)


def ngon_prism(poly, y0, y1, bev=0.0):
    poly = np.asarray(poly, float)
    return loft([np.column_stack([poly[:, 0], np.full(len(poly), y0), poly[:, 1]]),
                 np.column_stack([poly[:, 0], np.full(len(poly), y1), poly[:, 1]])], 'ngon', 'ngon')


def vnormals(g):
    """normales de sommets (moyenne pondérée par l'aire)."""
    N = np.zeros_like(g.V)
    for f in g.F:
        for k in range(1, len(f) - 1):
            a, b, c = g.V[f[0]], g.V[f[k]], g.V[f[k + 1]]
            n = np.cross(b - a, c - a)
            N[f[0]] += n
            N[f[k]] += n
            N[f[k + 1]] += n
    ln = np.linalg.norm(N, axis=1, keepdims=True)
    return N / np.maximum(ln, 1e-12)


def stamp(g, c, sig, amp, mirror=False, rotz=0.0, rotx=0.0, along=None):
    """bosse/creux gaussien anisotrope (σx,σy,σz) centré sur c, déplacement le long des normales (ou `along`)."""
    N = vnormals(g) if along is None else np.tile(np.asarray(along, float), (len(g.V), 1))
    cs = [np.asarray(c, float)]
    rz_ = [rotz]
    if mirror:
        cs.append(np.array([-c[0], c[1], c[2]]))
        rz_.append(-rotz)
    disp = np.zeros(len(g.V))
    for cc, rzv in zip(cs, rz_):
        d = g.V - cc
        if rzv:
            a = math.radians(rzv)
            ca, sa = math.cos(a), math.sin(a)
            d = np.stack([d[:, 0] * ca + d[:, 1] * sa, -d[:, 0] * sa + d[:, 1] * ca, d[:, 2]], axis=1)
        if rotx:
            a = math.radians(rotx)
            ca, sa = math.cos(a), math.sin(a)
            d = np.stack([d[:, 0], d[:, 1] * ca + d[:, 2] * sa, -d[:, 1] * sa + d[:, 2] * ca], axis=1)
        q = (d[:, 0] / sig[0]) ** 2 + (d[:, 1] / sig[1]) ** 2 + (d[:, 2] / sig[2]) ** 2
        disp += amp * np.exp(-0.5 * q)
    g.V = g.V + N * disp[:, None]
    return g


def resample_rows(rows, k):
    """rééchantillonne une table de sections [(y, rx, rz, cz, ...)] en k lignes (interpolation cubique Catmull-Rom)."""
    A = np.array(rows, float)
    m = len(A)
    t = np.linspace(0, m - 1, k)
    out = []
    P = np.vstack([A[0] * 2 - A[1], A, A[-1] * 2 - A[-2]])
    for tt in t:
        i = min(int(tt), m - 2)
        u = tt - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        v = 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
        out.append(tuple(v))
    return out


# --------------------------------------------------------------------------- pièces
class Piece:
    __slots__ = ("geo", "col", "sub", "angle", "flat", "ao", "bev")

    def __init__(s, geo, col, sub, angle, flat, ao, bev):
        s.geo, s.col, s.sub, s.angle, s.flat, s.ao, s.bev = geo, col, sub, angle, flat, ao, bev


class Part:
    def __init__(s, name, pivot):
        s.name = name
        s.pivot = tuple(pivot)
        s.pieces = []
        s.note = ""

    def add(s, geo, col=SKIN, sub=0, angle=50, flat=False, ao=None, bev=0.0):
        """col : (r,g,b) uniforme ou fonction f(V)->(n,3) ; ao : force l'alpha (parties sombres) ; angle: coupe edge-split."""
        if isinstance(geo, (list, tuple)):
            geo = merge(geo)
        s.pieces.append(Piece(geo, col, sub, angle, flat, ao, bev))
        return s

    def mirrored(s, name, pivot):
        p = Part(name, pivot)
        for pc in s.pieces:
            p.pieces.append(Piece(pc.geo.mir(), pc.col, pc.sub, pc.angle, pc.flat, pc.ao, pc.bev))
        return p


def to_blender(V):
    V = np.asarray(V, float)
    return np.stack([V[:, 0], -V[:, 2], V[:, 1]], axis=1)


def from_blender(V):
    return np.stack([V[:, 0], V[:, 2], -V[:, 1]], axis=1)


_tmp_coll = None


def _eval_piece(pc, pivot):
    """applique subsurf + edge split via Blender, renvoie V (contrat, relatif au pivot), faces, flags."""
    global _tmp_coll
    geo = pc.geo
    Vb = to_blender(geo.V - np.array(pivot)).astype(np.float32)
    me = bpy.data.meshes.new("tmp")
    me.from_pydata(Vb.tolist(), [], [list(f) for f in geo.F])
    me.update()
    n = len(me.polygons)
    if pc.flat:
        me.polygons.foreach_set("use_smooth", [False] * n)
    else:
        me.polygons.foreach_set("use_smooth", [True] * n)
    ob = bpy.data.objects.new("tmp", me)
    bpy.context.scene.collection.objects.link(ob)
    if pc.sub:
        m = ob.modifiers.new("sub", 'SUBSURF')
        m.levels = pc.sub
        m.render_levels = pc.sub
        m.quality = 2
    if pc.angle is not None and not pc.flat:
        m = ob.modifiers.new("es", 'EDGE_SPLIT')
        m.use_edge_angle = True
        m.use_edge_sharp = False
        m.split_angle = math.radians(pc.angle)
    dg = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(dg)
    me2 = oe.to_mesh()
    nv = len(me2.vertices)
    V = np.empty(nv * 3, np.float64)
    me2.vertices.foreach_get("co", V)
    V = V.reshape(-1, 3)
    npoly = len(me2.polygons)
    ls = np.empty(npoly, np.int32)
    lt = np.empty(npoly, np.int32)
    me2.polygons.foreach_get("loop_start", ls)
    me2.polygons.foreach_get("loop_total", lt)
    cv = np.empty(len(me2.loops), np.int32)
    me2.loops.foreach_get("vertex_index", cv)
    sm = np.empty(npoly, np.bool_)
    me2.polygons.foreach_get("use_smooth", sm)
    faces = [tuple(cv[a:a + b]) for a, b in zip(ls, lt)]
    oe.to_mesh_clear()
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(me)
    return V, faces, sm


_ao_dirs = None


def _hemi_dirs(k=28):
    rng = np.random.RandomState(7)
    out = []
    for i in range(k):
        u1 = (i + 0.5) / k
        u2 = (i * 0.61803398875) % 1.0
        r = math.sqrt(u1)
        th = 2 * math.pi * u2
        out.append((r * math.cos(th), r * math.sin(th), math.sqrt(max(0, 1 - u1))))
    return np.array(out)


def bake_ao(V, F, normals, dist=0.14, strength=0.75, k=28):
    bvh = BVHTree.FromPolygons([tuple(v) for v in V.tolist()], [tuple(int(i) for i in f) for f in F], epsilon=0.0)
    dirs = _hemi_dirs(k)
    ao = np.ones(len(V))
    for i in range(len(V)):
        n = normals[i]
        nn = np.linalg.norm(n)
        if nn < 1e-6:
            continue
        n = n / nn
        a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
        t1 = np.cross(n, a)
        t1 /= np.linalg.norm(t1)
        t2 = np.cross(n, t1)
        o = Vector(V[i] + n * 0.004)
        hit = 0.0
        for d in dirs:
            w = t1 * d[0] + t2 * d[1] + n * d[2]
            r = bvh.ray_cast(o, Vector(w), dist)
            if r[0] is not None:
                hit += 1.0 - 0.5 * (r[3] / dist)
        ao[i] = 1.0 - strength * hit / len(dirs)
    ao = np.clip(ao, 0.25, 1.0)
    # lissage sur le voisinage (sommets soudés par position)
    key = {}
    wid = np.empty(len(V), np.int64)
    for i, v in enumerate(V):
        kk = (round(v[0] * 2000), round(v[1] * 2000), round(v[2] * 2000))
        wid[i] = key.setdefault(kk, len(key))
    nb = [set() for _ in range(len(key))]
    for f in F:
        for a in range(len(f)):
            u, w = wid[f[a]], wid[f[(a + 1) % len(f)]]
            nb[u].add(w)
            nb[w].add(u)
    acc = np.zeros(len(key))
    cnt = np.zeros(len(key))
    for i in range(len(V)):
        acc[wid[i]] += ao[i]
        cnt[wid[i]] += 1
    wa = acc / np.maximum(cnt, 1)
    for _ in range(2):
        new = wa.copy()
        for u in range(len(key)):
            if nb[u]:
                new[u] = 0.5 * wa[u] + 0.5 * np.mean([wa[w] for w in nb[u]])
        wa = new
    return np.clip(wa[wid], 0.25, 1.0)


_mat = None


def get_material():
    global _mat
    if _mat is not None and _mat.name in bpy.data.materials:
        return _mat
    m = bpy.data.materials.new("M_Kit")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    cn = nt.nodes.new("ShaderNodeVertexColor")
    cn.layer_name = "Color"
    nt.links.new(cn.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.7
    _mat = m
    return m


def build_part(part, ao=True, ao_dist=0.14):
    """assemble les pièces en un seul objet Blender (origine = pivot), couleurs + AO bakés."""
    Vs, Fs, Cs, Fl, AOf = [], [], [], [], []
    off = 0
    for pc in part.pieces:
        V, F, sm = _eval_piece(pc, part.pivot)
        Vw = V  # relatif au pivot, repère Blender
        if callable(pc.col):
            c = np.asarray(pc.col(from_blender(V) + np.array(part.pivot)), float)
        else:
            c = np.tile(np.array(pc.col, float), (len(V), 1))
        Vs.append(Vw)
        Cs.append(c)
        AOf.append(np.full(len(V), -1.0 if pc.ao is None else pc.ao))
        Fs += [tuple(int(i) + off for i in f) for f in F]
        Fl += [bool(x) for x in sm]
        off += len(V)
    V = np.vstack(Vs)
    C = np.vstack(Cs)
    AOf = np.concatenate(AOf)
    me = bpy.data.meshes.new(part.name)
    me.from_pydata(V.tolist(), [], [list(f) for f in Fs])
    me.update()
    me.polygons.foreach_set("use_smooth", Fl)
    me.update()
    nrm = np.empty(len(me.vertices) * 3)
    me.vertex_normals.foreach_get("vector", nrm) if hasattr(me.vertex_normals, "foreach_get") else None
    nrm = nrm.reshape(-1, 3)
    if ao:
        a = bake_ao(V, Fs, nrm, dist=ao_dist)
    else:
        a = np.ones(len(V))
    a = np.where(AOf >= 0, AOf, a)
    ca = me.color_attributes.new("Color", 'FLOAT_COLOR', 'POINT')
    rgba = np.concatenate([np.clip(C, 0, 1), a[:, None]], axis=1).astype(np.float32)
    ca.data.foreach_set("color", rgba.ravel())
    me.color_attributes.active_color = ca
    me.color_attributes.render_color_index = 0
    me.materials.append(get_material())
    ob = bpy.data.objects.new(part.name, me)
    ob.location = tuple(to_blender(np.array([part.pivot]))[0])
    bpy.context.scene.collection.objects.link(ob)
    tri = sum(len(f) - 2 for f in Fs)
    return ob, tri


def export_glb(objs, path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(
        filepath=path, export_format='GLB', use_selection=True, export_yup=True,
        export_vertex_color='ACTIVE', export_active_vertex_color_when_no_material=True,
        export_all_vertex_colors=False,
        export_materials='EXPORT', export_texcoords=False, export_cameras=False, export_lights=False,
        export_apply=False, export_normals=True, export_tangents=False)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global _mat
    _mat = None
