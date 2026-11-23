"""kitlib : mini-bibliothèque de modélisation procédurale (Blender/bmesh + numpy).

Repère de travail = repère glTF/Godot (Y haut, +Z avant, ±X côtés). Les primitives sont
construites avec leur axe le long de +Y. Chaque face porte un masque couleur (R,G,B) :
R = matériau principal, G = secondaire / métal sombre, B = accent / lame / gemme, K = base.
"""
import math
import numpy as np
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = (1.0, 0.0, 0.0)
G = (0.0, 1.0, 0.0)
B = (0.0, 0.0, 1.0)
K = (0.0, 0.0, 0.0)

# ----------------------------------------------------------------------------- maths


def rotmat(rx=0.0, ry=0.0, rz=0.0):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def rot_to(d, roll=0.0):
    """rotation envoyant +Y sur d."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    y = np.array([0, 1.0, 0])
    c = float(y @ d)
    if c > 1 - 1e-9:
        M = np.eye(3)
    elif c < -1 + 1e-9:
        M = np.diag([1.0, -1.0, -1.0])
    else:
        v = np.cross(y, d)
        s2 = float(v @ v)
        vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        M = np.eye(3) + vx + vx @ vx * ((1 - c) / s2)
    if roll:
        M = M @ rotmat(0, roll, 0)
    return M


def unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-12)


# ----------------------------------------------------------------------------- Part


class Part:
    __slots__ = ("V", "F", "C")

    def __init__(self, V, F, C):
        self.V = np.asarray(V, float).reshape(-1, 3)
        self.F = [tuple(int(i) for i in f) for f in F]
        self.C = list(C)

    def xf(self, pos=(0, 0, 0), rot=(0, 0, 0), s=1.0, M=None):
        sv = np.broadcast_to(np.asarray(s, float), (3,))
        V = self.V * sv
        Mm = M if M is not None else rotmat(*rot)
        V = V @ np.asarray(Mm).T + np.asarray(pos, float)
        F = self.F
        if np.prod(sv) < 0:
            F = [f[::-1] for f in F]
        return Part(V, F, self.C)

    def mx(self):
        """miroir X (gauche <-> droite)."""
        return Part(self.V * np.array([-1.0, 1, 1]), [f[::-1] for f in self.F], self.C)

    def recolor(self, c):
        return Part(self.V, self.F, [c] * len(self.F))

    def ntri(self):
        return sum(len(f) - 2 for f in self.F)


def _weld(V, F, C, tol=1e-5):
    key = np.round(V / tol).astype(np.int64)
    _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    V2 = V[idx]
    F2, C2 = [], []
    for f, c in zip(F, C):
        g = []
        for i in f:
            j = int(inv[i])
            if not g or g[-1] != j:
                g.append(j)
        if len(g) > 1 and g[0] == g[-1]:
            g.pop()
        if len(g) < 3 or len(set(g)) != len(g):
            continue
        F2.append(tuple(g))
        C2.append(c)
    return V2, F2, C2


def _bevel(p, w, segs=1, ang=38.0, profile=0.5):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in p.V]
    pal = []
    lay = bm.faces.layers.int.new("ci")
    for f, c in zip(p.F, p.C):
        try:
            fc = bm.faces.new([vs[i] for i in f])
        except ValueError:
            continue
        if c not in pal:
            pal.append(c)
        fc[lay] = pal.index(c)
    bm.verts.index_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(ang)]
    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=w, offset_type="OFFSET", profile=profile, segments=segs,
                        affect="EDGES", clamp_overlap=True, loop_slide=True)
    bm.verts.index_update()
    V = np.array([v.co[:] for v in bm.verts])
    F = [tuple(v.index for v in f.verts) for f in bm.faces]
    C = [pal[f[lay]] if f[lay] < len(pal) else pal[0] for f in bm.faces]
    bm.free()
    return Part(V, F, C)


def mk(V, F, C, bevel=None):
    V, F, C = _weld(np.asarray(V, float), F, C)
    p = Part(V, F, C)
    if bevel:
        if isinstance(bevel, (int, float)):
            bevel = (bevel, 1)
        p = _bevel(p, *bevel)
    return p


def merge(*parts):
    parts = [q for p in parts for q in (p if isinstance(p, (list, tuple)) else [p])]
    V, F, C, off = [], [], [], 0
    for p in parts:
        V.append(p.V)
        F += [tuple(i + off for i in f) for f in p.F]
        C += p.C
        off += len(p.V)
    return Part(np.concatenate(V), F, C)


# ----------------------------------------------------------------------------- loft / sweep


def loft(rings, color=R, pair_colors=None, seg_colors=None, cap0=True, cap1=True, closed=True, wrap=False,
         bevel=None, cap_colors=None):
    rings = [np.asarray(r, float) for r in rings]
    Kn, M = len(rings), len(rings[0])
    V = np.concatenate(rings)
    F, C = [], []
    nseg = M if closed else M - 1
    npair = Kn if wrap else Kn - 1
    for k in range(npair):
        k2 = (k + 1) % Kn
        for i in range(nseg):
            j = (i + 1) % M
            F.append((k * M + i, k * M + j, k2 * M + j, k2 * M + i))
            if seg_colors is not None:
                C.append(seg_colors[i])
            elif pair_colors is not None:
                C.append(pair_colors[k])
            else:
                C.append(color)
    if closed and not wrap:
        cc = cap_colors or (pair_colors[0] if pair_colors else color, pair_colors[-1] if pair_colors else color)
        if cap0:
            F.append(tuple(range(M))[::-1])
            C.append(cc[0])
        if cap1:
            F.append(tuple(range((Kn - 1) * M, Kn * M)))
            C.append(cc[1])
    return mk(V, F, C, bevel)


def _ring(r, seg, y, sx=1.0, sz=1.0, phase=0.0):
    a = math.radians(phase) + 2 * np.pi * np.arange(seg) / seg
    return np.stack([r * sx * np.cos(a), np.full(seg, y), r * sz * np.sin(a)], 1)


def lathe(profile, seg=12, color=R, sx=1.0, sz=1.0, phase=0.0, bevel=None, cap=True):
    """profile : [(r, y[, couleur de la bande depuis le point précédent]), ...]"""
    rings, cols = [], []
    for p in profile:
        rings.append(_ring(p[0], seg, p[1], sx, sz, phase))
        cols.append(p[2] if len(p) > 2 else color)
    pc = cols[1:]
    return loft(rings, color=color, pair_colors=pc, cap0=cap, cap1=cap, cap_colors=(pc[0], pc[-1]), bevel=bevel)


def cyl(p0, p1, r0, r1=None, seg=10, color=R, bevel=None, sx=1.0, sz=1.0, phase=0.0, roll=0.0, cap=True):
    r1 = r0 if r1 is None else r1
    L = float(np.linalg.norm(np.subtract(p1, p0)))
    part = lathe([(r0, 0), (r1, L)], seg=seg, color=color, sx=sx, sz=sz, phase=phase, bevel=bevel, cap=cap)
    return part.xf(pos=p0, M=rot_to(np.subtract(p1, p0), roll))


def frustum(w0, d0, w1, d1, h, color=R, bevel=None, y0=0.0, off1=(0, 0)):
    """tronc à base rectangulaire (largeur X, profondeur Z)."""
    def rect(w, d, y, ox=0.0, oz=0.0):
        return np.array([[-w / 2 + ox, y, -d / 2 + oz], [w / 2 + ox, y, -d / 2 + oz],
                         [w / 2 + ox, y, d / 2 + oz], [-w / 2 + ox, y, d / 2 + oz]])
    return loft([rect(w0, d0, y0), rect(w1, d1, y0 + h, off1[0], off1[1])], color=color, bevel=bevel)


def box(size, pos=(0, 0, 0), rot=(0, 0, 0), color=R, bevel=0.006, taper=None):
    sx_, sy_, sz_ = size
    if taper is None:
        p = frustum(sx_, sz_, sx_, sz_, sy_, color=color, bevel=bevel, y0=-sy_ / 2)
    else:
        p = frustum(sx_, sz_, sx_ * taper[0], sz_ * taper[1], sy_, color=color, bevel=bevel, y0=-sy_ / 2)
    return p.xf(pos=pos, rot=rot)


def sphere(r, seg=10, rings=6, color=R, pos=(0, 0, 0), s=1.0, rot=(0, 0, 0), bevel=None):
    prof = [(r * math.sin(math.pi * k / rings), -r * math.cos(math.pi * k / rings)) for k in range(rings + 1)]
    return lathe(prof, seg=seg, color=color, bevel=bevel).xf(pos=pos, rot=rot, s=s)


def cone(r, h, seg=8, color=B, pos=(0, 0, 0), rot=(0, 0, 0), bevel=None, base_r=None):
    return lathe([(r, 0), (0, h)], seg=seg, color=color, bevel=bevel).xf(pos=pos, rot=rot)


def gem(r=0.03, h=None, seg=6, color=B, pos=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    h = h or r * 1.8
    return lathe([(0, -h * 0.55), (r, -h * 0.05), (r, h * 0.12), (0, h * 0.5)], seg=seg, color=color, phase=15).xf(pos=pos, rot=rot, s=s)


def poly_ring(pts2, y=0.0):
    pts2 = np.asarray(pts2, float)
    return np.stack([pts2[:, 0], np.full(len(pts2), y), pts2[:, 1]], 1)


def sweep(path, ring, scale=1.0, ref=None, color=R, seg_colors=None, pair_colors=None, cap0=True, cap1=True,
          closed_path=False, bevel=None, cap_colors=None):
    """ring : (M,2) en coordonnées (a,b) ; scale : scalaire, (sa,sb), fn(t)->scalaire|(sa,sb) ou tableau (N,)|(N,2)."""
    path = np.asarray(path, float)
    N = len(path)
    if closed_path:
        T = np.roll(path, -1, 0) - np.roll(path, 1, 0)
    else:
        T = np.zeros_like(path)
        T[1:-1] = path[2:] - path[:-2]
        T[0] = path[1] - path[0]
        T[-1] = path[-1] - path[-2]
    T = T / (np.linalg.norm(T, axis=1, keepdims=True) + 1e-12)
    A = np.zeros_like(path)
    if ref is not None:
        ref = unit(ref)
        prev = None
        for i in range(N):
            a = ref - T[i] * (ref @ T[i])
            if np.linalg.norm(a) < 1e-4:
                a = prev if prev is not None else unit(np.cross(T[i], [0, 0, 1]))
            A[i] = unit(a)
            prev = A[i]
    else:
        t0 = T[0]
        a = np.cross(t0, [1.0, 0, 0])
        if np.linalg.norm(a) < 1e-3:
            a = np.cross(t0, [0, 0, 1.0])
        A[0] = unit(a)
        for i in range(1, N):
            a = A[i - 1] - T[i] * (A[i - 1] @ T[i])
            A[i] = unit(a)
    Bv = np.cross(A, T)
    ring = np.asarray(ring, float)
    rings = []
    for i in range(N):
        t = i / max(N - 1, 1)
        if callable(scale):
            s = scale(t)
        elif isinstance(scale, np.ndarray):
            s = scale[i]
        else:
            s = scale
        sa, sb = (s, s) if np.isscalar(s) else (s[0], s[1])
        rings.append(path[i] + np.outer(ring[:, 0] * sa, A[i]) + np.outer(ring[:, 1] * sb, Bv[i]))
    return loft(rings, color=color, seg_colors=seg_colors, pair_colors=pair_colors, cap0=cap0, cap1=cap1,
                wrap=closed_path, bevel=bevel, cap_colors=cap_colors)


def circle2(n=8, phase=0.0):
    a = math.radians(phase) + 2 * np.pi * np.arange(n) / n
    return np.stack([np.cos(a), np.sin(a)], 1)


def tube(path, r, seg=8, color=R, cap0=True, cap1=True, closed_path=False, bevel=None, ref=None, ring=None):
    return sweep(path, circle2(seg) if ring is None else ring, scale=r, color=color, cap0=cap0, cap1=cap1,
                 closed_path=closed_path, bevel=bevel, ref=ref)


def bezier(p0, p1, p2, p3, n=12):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, float) for p in (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def polyline(pts, n_each=1):
    return np.asarray(pts, float)


def arc(c, r, a0, a1, n=12, plane="XY", ry=None):
    """points d'un arc ; plane 'XY','YZ','XZ' (angle 0 = 1er axe, 90 = 2e axe)."""
    ry = r if ry is None else ry
    a = np.radians(np.linspace(a0, a1, n))
    u, v = r * np.cos(a), ry * np.sin(a)
    c = np.asarray(c, float)
    pts = np.zeros((n, 3))
    iu, iv = {"XY": (0, 1), "YZ": (1, 2), "XZ": (0, 2), "ZY": (2, 1), "YX": (1, 0), "ZX": (2, 0)}[plane]
    pts[:, iu] = u
    pts[:, iv] = v
    return pts + c


def torus(R_, r, seg=16, tube_seg=6, plane="XZ", pos=(0, 0, 0), color=G, bevel=None, ry=None, a0=0, a1=None, cap=True):
    """anneau (plan donné). a0..a1 pour un arc (extrémités fermées)."""
    full = a1 is None
    pts = arc((0, 0, 0), R_, a0, 360 + a0 if full else a1, seg if not full else seg + 1, plane, ry)
    if full:
        pts = pts[:-1]
    return tube(pts, r, seg=tube_seg, color=color, closed_path=full, cap0=not full, cap1=not full, bevel=bevel).xf(pos=pos)


def radial(part, n, axis="y", phase=0.0):
    out = []
    for k in range(n):
        a = phase + 360.0 * k / n
        rot = {"y": (0, a, 0), "x": (a, 0, 0), "z": (0, 0, a)}[axis]
        out.append(part.xf(rot=rot))
    return out


# ----------------------------------------------------------------------------- plate (plaque effilée)


def plate(poly, h, inset=0.0, plane="YZ", color=G, edge_color=B, bevel=None, max_miter=2.2):
    """polygone 2D (u,v) -> plaque d'épaisseur 2h dont le contour s'effile (inset) vers l'arête.
    h / inset : scalaires ou tableaux par sommet. plane : 'XY'(épaisseur Z), 'YZ'(épaisseur X), 'XZ'(épaisseur Y)."""
    P = np.asarray(poly, float)
    n = len(P)
    h = np.broadcast_to(np.asarray(h, float), (n,))
    ins = np.broadcast_to(np.asarray(inset, float), (n,))
    area = 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
    sgn = 1.0 if area > 0 else -1.0
    inner = np.zeros_like(P)
    for i in range(n):
        d1 = unit(np.append(P[i] - P[i - 1], 0))[:2]
        d2 = unit(np.append(P[(i + 1) % n] - P[i], 0))[:2]
        n1 = sgn * np.array([-d1[1], d1[0]])
        n2 = sgn * np.array([-d2[1], d2[0]])
        b = n1 + n2
        den = max(1 + float(n1 @ n2), 1.0 / (max_miter ** 2))
        inner[i] = P[i] + b / den * ins[i]

    def to3(uv, w):
        out = np.zeros((len(uv), 3))
        iu, iv, iw = {"XY": (0, 1, 2), "YZ": (1, 2, 0), "XZ": (0, 2, 1)}[plane]
        out[:, iu] = uv[:, 0]
        out[:, iv] = uv[:, 1]
        out[:, iw] = w
        return out

    rings = [to3(inner, -h), to3(P, 0.0), to3(inner, h)]
    segc = [edge_color if (ins[i] > 1e-4 and ins[(i + 1) % n] > 1e-4) else color for i in range(n)]
    return loft(rings, color=color, seg_colors=segc, cap_colors=(color, color), bevel=bevel)


def slab(poly, h, plane="XY", color=R, bevel=0.005):
    """extrusion droite du polygone, épaisseur 2h centrée."""
    P = np.asarray(poly, float)

    def to3(uv, w):
        out = np.zeros((len(uv), 3))
        iu, iv, iw = {"XY": (0, 1, 2), "YZ": (1, 2, 0), "XZ": (0, 2, 1)}[plane]
        out[:, iu] = uv[:, 0]
        out[:, iv] = uv[:, 1]
        out[:, iw] = w
        return out
    return loft([to3(P, -h), to3(P, h)], color=color, bevel=bevel)


# ----------------------------------------------------------------------------- lames


def ring_blade(e=0.2, bev=0.62, fuller=0.0, edge_c=G, face_c=B):
    """section de lame double tranchant. a = épaisseur (X), b = largeur (Z, +1 = tranchant avant)."""
    pts, cols = [], []
    pts.append((e, 1.0))
    if fuller > 0:
        pts += [(1.0, bev), (1.0, fuller), (0.55, fuller * 0.6), (0.55, -fuller * 0.6), (1.0, -fuller), (1.0, -bev)]
    else:
        pts += [(1.0, bev), (1.0, -bev)]
    pts += [(e, -1.0), (-e, -1.0)]
    mirror = [(-a, b) for (a, b) in pts[1:-1]][::-1]
    pts += mirror
    pts.append((-e, 1.0))
    n = len(pts)
    seg = []
    for i in range(n):
        a0, a1 = pts[i], pts[(i + 1) % n]
        broad = abs(a0[0]) > 0.5 and abs(a1[0]) > 0.5 and (abs(a0[1]) <= bev + 1e-9 and abs(a1[1]) <= bev + 1e-9)
        seg.append(face_c if broad else edge_c)
    return np.array(pts), seg


def ring_sabre(back=1.0, edge_c=G, face_c=B, spine_c=G):
    """lame à un tranchant (katana, cimeterre) : tranchant +b, dos plat -b."""
    pts = np.array([(0.08, 1.0), (1.0, 0.45), (1.0, -0.85), (0.8, -1.0), (-0.8, -1.0), (-1.0, -0.85), (-1.0, 0.45), (-0.08, 1.0)])
    seg = [edge_c, face_c, spine_c, spine_c, spine_c, face_c, edge_c, edge_c]
    return pts, seg


def ring_ridge(edge_c=G, face_c=B):
    pts = np.array([(0.0, 1.0), (1.0, 0.0), (0.0, -1.0), (-1.0, 0.0)])
    return pts, [face_c, face_c, face_c, face_c]


def blade(keys, ring=None, ref=(1, 0, 0), bevel=None, base=(0, 0, 0), bend=None, n_sub=1):
    """keys : [(y, demi-largeur, demi-épaisseur[, z_offset]) ...] du talon à la pointe (pointe : largeur 0).
    La pointe se referme en un sommet. 'bend' : fn(y)->z décalage de courbure."""
    ring_pts, segc = ring if ring is not None else ring_blade()
    keys = [tuple(k) for k in keys]
    if n_sub > 1:
        nk = []
        for a, b in zip(keys[:-1], keys[1:]):
            a4 = tuple(a) + (0.0,) * (4 - len(a))
            b4 = tuple(b) + (0.0,) * (4 - len(b))
            for s in range(n_sub):
                f = s / n_sub
                nk.append(tuple(a4[i] * (1 - f) + b4[i] * f for i in range(4)))
        nk.append(tuple(keys[-1]))
        keys = nk
    path, sc = [], []
    for k in keys:
        y, w, t = k[0], k[1], k[2]
        zo = k[3] if len(k) > 3 else 0.0
        if bend:
            zo += bend(y)
        path.append((base[0], y + base[1], zo + base[2]))
        sc.append((t, w))
    path = np.array(path)
    sc = np.array(sc)
    return sweep(path, ring_pts, scale=sc, ref=ref, seg_colors=segc, bevel=bevel, cap_colors=(B, B))


# ----------------------------------------------------------------------------- assemblage


class Model:
    def __init__(self, name, accent=None, notes="", ao_dist=0.10, kind="weapon"):
        self.name, self.accent, self.notes, self.ao_dist, self.kind = name, accent, notes, ao_dist, kind
        self.parts = []

    def add(self, *ps):
        for p in ps:
            if isinstance(p, (list, tuple)):
                self.add(*p)
            else:
                self.parts.append(p)
        return self


def _hemisphere_dirs(n=24):
    dirs = []
    for i in range(n):
        u = (i + 0.5) / n
        phi = i * 2.399963
        r = math.sqrt(u)
        dirs.append((r * math.cos(phi), r * math.sin(phi), math.sqrt(1 - u)))
    return dirs


_HD = _hemisphere_dirs(26)


def get_material():
    mat = bpy.data.materials.get("M_Kit")
    if mat:
        return mat
    mat = bpy.data.materials.new("M_Kit")
    try:
        mat.use_nodes = True
    except Exception:
        pass
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    vc = nt.nodes.new("ShaderNodeVertexColor")
    vc.layer_name = "Color"
    nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    return mat


def to_blender(V):
    """glTF (x,y,z) -> Blender (x,-z,y)."""
    return np.stack([V[:, 0], -V[:, 2], V[:, 1]], 1)


def build_object(model, smooth=38.0, collection=None, ao=True):
    parts = [p for p in model.parts if len(p.F)]
    P = merge(parts)
    V = to_blender(P.V)
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in V]
    pal = []
    lay = bm.faces.layers.int.new("ci")
    for f, c in zip(P.F, P.C):
        try:
            fc = bm.faces.new([vs[i] for i in f])
        except ValueError:
            continue
        if c not in pal:
            pal.append(c)
        fc[lay] = pal.index(c)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle(0.0) < math.radians(smooth)
        else:
            e.smooth = False
    bm.verts.ensure_lookup_table()
    ao_vals = {}
    if ao:
        bvh = BVHTree.FromBMesh(bm)
        md = model.ao_dist
        for v in bm.verts:
            n = v.normal
            if n.length < 1e-6:
                ao_vals[v.index] = 1.0
                continue
            n = n.normalized()
            t = n.cross(Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))).normalized()
            b = n.cross(t)
            org = v.co + n * 0.0015
            acc = 0.0
            for (x, y, z) in _HD:
                d = t * x + b * y + n * z
                hit = bvh.ray_cast(org, d, md)
                if hit[0] is not None:
                    acc += 1.0 - hit[3] / md * 0.6
            ao_vals[v.index] = max(0.28, 1.0 - 0.9 * acc / len(_HD))
    me = bpy.data.meshes.new(model.name)
    cl = bm.loops.layers.float_color.new("Color")
    for f in bm.faces:
        c = pal[f[lay]]
        for lp in f.loops:
            lp[cl] = (c[0], c[1], c[2], ao_vals.get(lp.vert.index, 1.0))
    bm.to_mesh(me)
    bm.free()
    attr = me.color_attributes.get("Color")
    me.color_attributes.active_color = attr
    me.color_attributes.render_color_index = list(me.color_attributes).index(attr)
    me.materials.append(get_material())
    ob = bpy.data.objects.new(model.name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    ob["accent"] = list(model.accent) if model.accent else []
    return ob


def ob_info(ob):
    me = ob.data
    ntri = sum(len(p.vertices) - 2 for p in me.polygons)
    bb = np.array([list(v) for v in ob.bound_box])
    lo, hi = bb.min(0), bb.max(0)
    # Blender -> glTF : (x, z, -y)
    lo_g = [float(lo[0]), float(lo[2]), float(-hi[1])]
    hi_g = [float(hi[0]), float(hi[2]), float(-lo[1])]
    ext = [hi_g[i] - lo_g[i] for i in range(3)]
    return {"triangles": int(ntri), "bbox_min": [round(x, 3) for x in lo_g], "bbox_max": [round(x, 3) for x in hi_g],
            "size": [round(x, 3) for x in ext], "length": round(max(ext), 3)}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def export_glb(path, objects=None):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=False, export_yup=True,
                              export_apply=False, export_normals=True, export_texcoords=False,
                              export_materials="EXPORT", export_vertex_color="ACTIVE", export_cameras=False,
                              export_lights=False, export_extras=True, export_animations=False)
