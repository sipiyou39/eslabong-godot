"""Géométrie procédurale (coordonnées JEU : x droite, y haut, z vers le joueur).
Conversion vers Blender (Z haut) : (x, y, z) -> (x, -z, y), l'export glTF y-up redonne les coordonnées jeu."""
import math
import numpy as np

RNG = np.random.default_rng(1)


def seed(n):
    global RNG
    RNG = np.random.default_rng(n)


def s2l(c):
    """sRGB (hex '#rrggbb' ou tuple 0..1) -> linéaire (np.array(3))"""
    if isinstance(c, str):
        c = c.lstrip('#')
        c = tuple(int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    c = np.asarray(c[:3], float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lerp(a, b, t):
    return a + (b - a) * t


def rotm(yaw=0.0, pitch=0.0, roll=0.0):
    cy, sy = math.cos(yaw), math.sin(yaw)
    cx, sx = math.cos(pitch), math.sin(pitch)
    cz, sz = math.cos(roll), math.sin(roll)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


# ------------------------------------------------------------------ triangulation
def ear_clip(poly):
    """poly: liste de (u,v) ; renvoie liste de triangles (indices) CCW (u à droite, v en haut)."""
    pts = [tuple(p) for p in poly]
    n = len(pts)
    area = 0.0
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    idx = list(range(n))
    if area < 0:
        idx.reverse()
    tris = []

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def inside(p, a, b, c):
        d1 = cross(a, b, p)
        d2 = cross(b, c, p)
        d3 = cross(c, a, p)
        return d1 >= -1e-12 and d2 >= -1e-12 and d3 >= -1e-12

    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        ear = False
        m = len(idx)
        for k in range(m):
            i0, i1, i2 = idx[(k - 1) % m], idx[k], idx[(k + 1) % m]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if cross(a, b, c) <= 1e-12:
                continue
            ok = True
            for j in idx:
                if j in (i0, i1, i2):
                    continue
                if inside(pts[j], a, b, c):
                    ok = False
                    break
            if ok:
                tris.append((i0, i1, i2))
                idx.pop(k)
                ear = True
                break
        if not ear:
            # polygone dégénéré : on coupe en éventail
            for k in range(1, len(idx) - 1):
                tris.append((idx[0], idx[k], idx[k + 1]))
            idx = []
            break
    if len(idx) == 3:
        tris.append(tuple(idx))
    return tris


# ------------------------------------------------------------------ primitives locales (V ndarray, F liste de tuples)
def p_box(sx, sy, sz, top=None, base=0.0):
    hx, hz = sx / 2, sz / 2
    tx, tz = (top if top else (sx, sz))
    tx, tz = tx / 2, tz / 2
    V = np.array([(-hx, base, -hz), (hx, base, -hz), (hx, base, hz), (-hx, base, hz),
                  (-tx, base + sy, -tz), (tx, base + sy, -tz), (tx, base + sy, tz), (-tx, base + sy, tz)], float)
    F = [(0, 1, 2, 3), (7, 6, 5, 4), (3, 2, 6, 7), (1, 0, 4, 5), (2, 1, 5, 6), (0, 3, 7, 4)]
    return V, F


def p_lathe(profile, seg=12, cap0=True, cap1=True, flutes=None, jitter=0.0, phase=0.0):
    """profile : [(r,y),...] du bas vers le haut. r=0 -> sommet unique."""
    prof = [(float(r), float(y)) for r, y in profile]
    V = []
    rings = []
    for (r, y) in prof:
        if r <= 1e-6:
            rings.append(('pt', len(V)))
            V.append((0.0, y, 0.0))
        else:
            start = len(V)
            for j in range(seg):
                th = phase + 2 * math.pi * j / seg
                rr = r
                if flutes:
                    n, dep = flutes
                    rr = r * (1 - dep * 0.5 * (1 - math.cos(n * th)))
                if jitter:
                    rr *= 1 + jitter * (RNG.random() * 2 - 1)
                V.append((rr * math.cos(th), y, rr * math.sin(th)))
            rings.append(('ring', start))
    F = []
    for i in range(len(prof) - 1):
        a, b = rings[i], rings[i + 1]
        if a[0] == 'pt' and b[0] == 'pt':
            continue
        for j in range(seg):
            j2 = (j + 1) % seg
            if a[0] == 'pt':
                F.append((a[1], b[1] + j, b[1] + j2))
            elif b[0] == 'pt':
                F.append((a[1] + j, b[1], a[1] + j2))
            else:
                F.append((a[1] + j, b[1] + j, b[1] + j2, a[1] + j2))
    if cap0 and rings[0][0] == 'ring':
        F.append(tuple(rings[0][1] + j for j in range(seg)))
    if cap1 and rings[-1][0] == 'ring':
        F.append(tuple(rings[-1][1] + j for j in reversed(range(seg))))
    return np.array(V, float), F


def p_cyl(r, h, seg=12, r2=None, cap0=True, cap1=True, **kw):
    r2 = r if r2 is None else r2
    return p_lathe([(r, 0), (r2, h)], seg, cap0, cap1, **kw)


def p_cone(r, h, seg=8, cap0=True):
    return p_lathe([(r, 0), (0, h)], seg, cap0, False)


def p_sphere(r, nu=8, nv=5, yscale=1.0):
    prof = [(0, -r * yscale)]
    for k in range(1, nv):
        a = -math.pi / 2 + math.pi * k / nv
        prof.append((r * math.cos(a), r * math.sin(a) * yscale))
    prof.append((0, r * yscale))
    return p_lathe(prof, nu)


_ICO = None


def p_ico(r=1.0, sub=0):
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    V = [np.array(v, float) / np.linalg.norm(v) for v in V]
    for _ in range(sub):
        cache = {}
        nf = []

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                m = (V[a] + V[b]) / 2
                V.append(m / np.linalg.norm(m))
                cache[k] = len(V) - 1
            return cache[k]
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = nf
    return np.array(V) * r, F


def p_extrude_xz(poly, y0, y1, caps=True):
    """polygone (x,z) extrudé de y0 à y1 (faces latérales + dessus/dessous)."""
    poly = [tuple(p) for p in poly]
    n = len(poly)
    # orientation : aire signée dans le plan (x,z) -> on veut le dessus (+Y) correct
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    if area > 0:
        poly = poly[::-1]  # on se met en sens où (x -> z) tourne négativement
    V = [(x, y0, z) for x, z in poly] + [(x, y1, z) for x, z in poly]
    F = []
    for i in range(n):
        j = (i + 1) % n
        F.append((i, n + i, n + j, j))
    if caps:
        tr = ear_clip(poly)
        for a, b, c in tr:
            F.append((n + a, n + c, n + b))  # dessus
            F.append((a, b, c))              # dessous
    V = np.array(V, float)
    return _fix_closed(V, F)


def p_extrude_xy(poly, z0, z1, caps=True):
    """polygone (x,y) (y = haut) extrudé de z0 à z1 ; face avant = +Z."""
    poly = [tuple(p) for p in poly]
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    if area < 0:
        poly = poly[::-1]  # CCW vu depuis +Z
    V = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    F = []
    for i in range(n):
        j = (i + 1) % n
        F.append((i, j, n + j, n + i))
    if caps:
        tr = ear_clip(poly)
        for a, b, c in tr:
            F.append((n + a, n + b, n + c))  # +Z
            F.append((a, c, b))              # -Z
    V = np.array(V, float)
    return _fix_closed(V, F)


def _fix_closed(V, F):
    """si le volume signé est négatif, on retourne toutes les faces."""
    vol = 0.0
    for f in F:
        for k in range(1, len(f) - 1):
            a, b, c = V[f[0]], V[f[k]], V[f[k + 1]]
            vol += np.dot(a, np.cross(b, c)) / 6.0
    if vol < 0:
        F = [tuple(reversed(f)) for f in F]
    return V, F


def p_torus(R, r, seg_big=16, seg_small=6, phase=0.0):
    V = []
    for i in range(seg_big):
        a = 2 * math.pi * i / seg_big
        for j in range(seg_small):
            b = phase + 2 * math.pi * j / seg_small
            rr = R + r * math.cos(b)
            V.append((rr * math.cos(a), r * math.sin(b), rr * math.sin(a)))
    F = []
    for i in range(seg_big):
        i2 = (i + 1) % seg_big
        for j in range(seg_small):
            j2 = (j + 1) % seg_small
            F.append((i * seg_small + j, i2 * seg_small + j, i2 * seg_small + j2, i * seg_small + j2))
    return _fix_closed(np.array(V, float), F)


def p_grid(x0, z0, x1, z1, nx, nz, y=0.0):
    xs = np.linspace(x0, x1, nx + 1)
    zs = np.linspace(z0, z1, nz + 1)
    V = np.array([(x, y, z) for z in zs for x in xs], float)
    F = []
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            F.append((a, a + (nx + 1), a + (nx + 1) + 1, a + 1))
    return V, F


def p_quad(a, b, c, d):
    return np.array([a, b, c, d], float), [(0, 1, 2, 3)]


def _noise3(p, seed):
    """bruit lisse pseudo-aléatoire sur points 3D (n,3) via sommes de sinus (rapide, déterministe)."""
    r = np.random.default_rng(abs(int(seed)))
    out = np.zeros(len(p))
    for _ in range(4):
        d = r.normal(size=3)
        d /= np.linalg.norm(d)
        f = r.uniform(1.0, 3.0)
        ph = r.uniform(0, 6.28)
        out += np.sin(p @ d * f * 2 + ph)
    return out / 4


def p_rock(sx, sy, sz, seed=0, sub=1, flat=0.35, rough=0.25):
    V, F = p_ico(1.0, sub)
    n = _noise3(V * 1.7, seed)
    V = V * (1 + rough * n[:, None])
    V = V * np.array([sx / 2, sy / 2, sz / 2])
    V[:, 1] += sy * 0.5 * (1 - flat)
    V[:, 1] = np.maximum(V[:, 1], 0.0)
    return V, F


def p_crystal(r, h, seg=6, tip=0.28, seed=0, skew=0.0, base_r=None, jit=0.12):
    """cristal : prisme à pointe. base_r : rayon de base (par défaut r)."""
    rg = np.random.default_rng(abs(int(seed)))
    base_r = r if base_r is None else base_r
    ang = np.array([2 * math.pi * j / seg for j in range(seg)]) + rg.uniform(0, 1)
    rj = 1 + jit * (rg.random(seg) * 2 - 1)
    V = []
    for a, k in zip(ang, rj):
        V.append((base_r * k * math.cos(a), 0, base_r * k * math.sin(a)))
    hb = h * (1 - tip)
    for a, k in zip(ang, rj):
        V.append((r * k * math.cos(a) + skew * hb, hb, r * k * math.sin(a)))
    V.append((skew * h, h, 0))
    V = np.array(V, float)
    F = []
    for j in range(seg):
        j2 = (j + 1) % seg
        F.append((j, seg + j, seg + j2, j2))
        F.append((seg + j, 2 * seg, seg + j2))
    F.append(tuple(range(seg)))
    return V, F


def p_bevel(V, F, w, seg=1):
    import bmesh
    bm = bmesh.new()
    vs = [bm.verts.new(tuple(v)) for v in V]
    for f in F:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=w, offset_type='OFFSET', segments=seg, profile=0.5,
                    affect='EDGES', clamp_overlap=True, loop_slide=True)
    bm.verts.index_update()
    V2 = np.array([tuple(v.co) for v in bm.verts], float)
    F2 = [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    return V2, F2


# ------------------------------------------------------------------ MeshBuffer
class MB:
    def __init__(self, name, origin=(0, 0, 0)):
        self.name = name
        self.origin = np.array(origin, float)
        self.P, self.T, self.UV = [], [], []
        self.F = {3: [], 4: [], 0: []}
        self.M = {3: [], 4: [], 0: []}
        self.mats = []
        self.n = 0

    def mid(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def add(self, VF, mat, tint=(1, 1, 1), pos=(0, 0, 0), yaw=0.0, pitch=0.0, roll=0.0, scale=1.0,
            vfun=None, jit=0.0, uv=None, bev=0.0, bev_seg=1, flip=False):
        V, F = VF
        V = np.asarray(V, float).copy()
        F = list(F)
        if bev > 0:
            V, F = p_bevel(V, F, bev, bev_seg)
        if not np.isscalar(scale):
            V = V * np.asarray(scale)
        elif scale != 1.0:
            V = V * scale
        if yaw or pitch or roll:
            V = V @ rotm(yaw, pitch, roll).T
        V = V + np.asarray(pos, float)
        if flip:
            F = [tuple(reversed(f)) for f in F]
        t = s2l(tint) if not isinstance(tint, np.ndarray) or tint.ndim == 1 else tint
        t = np.broadcast_to(np.asarray(t, float), (len(V), 3)).copy()
        if jit:
            t = t * (1 + jit * (RNG.random() * 2 - 1))
        if vfun is not None:
            f = np.asarray(vfun(V), float)
            t = t * (f[:, None] if f.ndim == 1 else f)
        self._store(V, F, mat, t, uv)

    def _store(self, V, F, mat, t, uv):
        base = self.n
        mi = self.mid(mat)
        self.P.append(V)
        self.T.append(t)
        self.UV.append(np.full((len(V), 2), np.nan) if uv is None else np.asarray(uv, float))
        self.n += len(V)
        g3 = [f for f in F if len(f) == 3]
        g4 = [f for f in F if len(f) == 4]
        gn = [f for f in F if len(f) > 4]
        if g3:
            self.F[3].append(np.array(g3, np.int64) + base)
            self.M[3].append(np.full(len(g3), mi, np.int32))
        if g4:
            self.F[4].append(np.array(g4, np.int64) + base)
            self.M[4].append(np.full(len(g4), mi, np.int32))
        if gn:
            self.F[0].extend([[i + base for i in f] for f in gn])
            self.M[0].extend([mi] * len(gn))

    def add_many(self, VF, mat, pos, yaw=None, scale=None, tint=None, pitch=None, jit=0.0, roll=None, slots=None):
        """instances vectorisées. pos (k,3), yaw (k,), scale (k,) ou (k,3), tint (k,3) sRGB hex tuples -> linéaire déjà converti."""
        V0, F0 = VF
        V0 = np.asarray(V0, float)
        k = len(pos)
        if k == 0:
            return
        pos = np.asarray(pos, float)
        yaw = np.zeros(k) if yaw is None else np.asarray(yaw, float)
        pitch = np.zeros(k) if pitch is None else np.asarray(pitch, float)
        roll = np.zeros(k) if roll is None else np.asarray(roll, float)
        if scale is None:
            sc = np.ones((k, 3))
        else:
            sc = np.asarray(scale, float)
            sc = np.repeat(sc[:, None], 3, 1) if sc.ndim == 1 else sc
        Vs = V0[None, :, :] * sc[:, None, :]
        # roll (Z) puis pitch (X) puis yaw (Y)
        if np.any(roll):
            c, s = np.cos(roll)[:, None], np.sin(roll)[:, None]
            x, y = Vs[..., 0], Vs[..., 1]
            Vs = np.stack([c * x - s * y, s * x + c * y, Vs[..., 2]], -1)
        if np.any(pitch):
            c, s = np.cos(pitch)[:, None], np.sin(pitch)[:, None]
            y, z = Vs[..., 1], Vs[..., 2]
            Vs = np.stack([Vs[..., 0], c * y - s * z, s * y + c * z], -1)
        c, s = np.cos(yaw)[:, None], np.sin(yaw)[:, None]
        x, z = Vs[..., 0], Vs[..., 2]
        Vs = np.stack([c * x + s * z, Vs[..., 1], -s * x + c * z], -1)
        Vs = Vs + pos[:, None, :]
        nv = len(V0)
        t = np.ones((k, 3)) if tint is None else np.asarray(tint, float)
        if t.ndim == 3:
            t = t[:, np.asarray(slots), :]
        else:
            t = np.repeat(t[:, None, :], nv, 1)
        if jit:
            t = t * (1 + jit * (RNG.random((k, 1, 1)) * 2 - 1))
        mi = self.mid(mat)
        base = self.n
        self.P.append(Vs.reshape(-1, 3))
        self.T.append(t.reshape(-1, 3))
        self.UV.append(np.full((k * nv, 2), np.nan))
        self.n += k * nv
        offs = (np.arange(k) * nv + base)[:, None, None]
        for L in (3, 4):
            g = [f for f in F0 if len(f) == L]
            if g:
                g = np.array(g, np.int64)[None] + offs
                self.F[L].append(g.reshape(-1, L))
                self.M[L].append(np.full(len(g.reshape(-1, L)), mi, np.int32))
        gn = [f for f in F0 if len(f) > 4]
        for i in range(k):
            for f in gn:
                self.F[0].append([a + base + i * nv for a in f])
                self.M[0].append(mi)

    # ---------------- raccourcis
    def box(self, size, pos=(0, 0, 0), mat='M_stone', top=None, base=0.0, **kw):
        self.add(p_box(size[0], size[1], size[2], top, base), mat, pos=pos, **kw)

    def cyl(self, r, h, pos=(0, 0, 0), mat='M_stone', seg=12, r2=None, cap0=True, cap1=True, **kw):
        fl = kw.pop('flutes', None)
        self.add(p_cyl(r, h, seg, r2, cap0, cap1, flutes=fl), mat, pos=pos, **kw)

    def lathe(self, profile, pos=(0, 0, 0), mat='M_stone', seg=12, cap0=True, cap1=True, flutes=None, jitter=0.0, **kw):
        self.add(p_lathe(profile, seg, cap0, cap1, flutes, jitter), mat, pos=pos, **kw)

    def cone(self, r, h, pos=(0, 0, 0), mat='M_stone', seg=8, **kw):
        self.add(p_cone(r, h, seg), mat, pos=pos, **kw)

    def sphere(self, r, pos=(0, 0, 0), mat='M_stone', nu=8, nv=5, yscale=1.0, **kw):
        self.add(p_sphere(r, nu, nv, yscale), mat, pos=pos, **kw)

    def ico(self, r, pos=(0, 0, 0), mat='M_stone', sub=1, scale=1.0, **kw):
        self.add(p_ico(r, sub), mat, pos=pos, scale=scale, **kw)

    def torus(self, R, r, pos=(0, 0, 0), mat='M_stone', sb=16, ss=6, **kw):
        self.add(p_torus(R, r, sb, ss), mat, pos=pos, **kw)

    def poly_xz(self, poly, y0, y1, mat='M_stone', **kw):
        self.add(p_extrude_xz(poly, y0, y1), mat, **kw)

    def poly_xy(self, poly, z0, z1, mat='M_stone', **kw):
        self.add(p_extrude_xy(poly, z0, z1), mat, **kw)

    def rock(self, size, pos=(0, 0, 0), mat='M_rock', seed=0, sub=1, **kw):
        self.add(p_rock(size[0], size[1], size[2], seed, sub), mat, pos=pos, **kw)

    def crystal(self, r, h, pos=(0, 0, 0), mat='M_crystal', seg=6, seed=0, tip=0.28, skew=0.0, base_r=None, **kw):
        self.add(p_crystal(r, h, seg, tip, seed, skew, base_r), mat, pos=pos, **kw)

    def quad(self, a, b, c, d, mat='M_cloth', **kw):
        self.add(p_quad(a, b, c, d), mat, **kw)

    # ---------------- finalisation
    def finalize(self, uvsize):
        """renvoie dict de tableaux. uvsize: dict mat->mètres/tuile."""
        P = np.concatenate(self.P)
        T = np.concatenate(self.T)
        UVx = np.concatenate(self.UV)
        loops_v, loop_start, face_mat = [], [], []
        face_len = []
        cursor = 0
        groups = []
        for L in (3, 4):
            if self.F[L]:
                F = np.concatenate(self.F[L])
                M = np.concatenate(self.M[L])
                groups.append((L, F, M))
        out_faces_first = []
        nf = 0
        lv = []
        lstart = []
        fmat = []
        flen = []
        for L, F, M in groups:
            k = len(F)
            lv.append(F.ravel())
            lstart.append(cursor + np.arange(k) * L)
            fmat.append(M)
            flen.append(np.full(k, L))
            cursor += k * L
        if self.F[0]:
            for f, m in zip(self.F[0], self.M[0]):
                lv.append(np.array(f, np.int64))
                lstart.append(np.array([cursor]))
                fmat.append(np.array([m], np.int32))
                flen.append(np.array([len(f)]))
                cursor += len(f)
        lv = np.concatenate(lv)
        lstart = np.concatenate(lstart)
        fmat = np.concatenate(fmat).astype(np.int32)
        flen = np.concatenate(flen)
        # normales de faces (3 premiers sommets)
        v0, v1, v2 = P[lv[lstart]], P[lv[lstart + 1]], P[lv[lstart + 2]]
        nrm = np.cross(v1 - v0, v2 - v0)
        ax = np.argmax(np.abs(nrm), axis=1)
        # UV auto
        fi = np.repeat(np.arange(len(lstart)), flen)
        Pl = P[lv]
        axl = ax[fi]
        u = np.where(axl == 0, Pl[:, 2], Pl[:, 0])
        v = np.where(axl == 1, Pl[:, 2], Pl[:, 1])
        sz = np.array([uvsize.get(m, 4.0) for m in self.mats], float)[fmat][fi]
        uv = np.stack([u / sz, v / sz], 1)
        ex = UVx[lv]
        has = ~np.isnan(ex[:, 0])
        uv[has] = ex[has]
        return dict(P=P, T=T, lv=lv, lstart=lstart, flen=flen, fmat=fmat, uv=uv)
