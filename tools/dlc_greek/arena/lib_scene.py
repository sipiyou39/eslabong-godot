"""Outline arrondi, bandes annulaires, sol, matériaux, assemblage de scène Blender, bake AO, export GLB."""
import math
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_geo as G
from lib_geo import MB, s2l, rotm, p_box, p_lathe, p_cyl, p_sphere, p_extrude_xz, p_extrude_xy, p_torus, p_ico

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEXDIR = ROOT + "/assets/textures/arena"
OUTDIR = ROOT + "/assets/models/arenas"

HX, HZ, CR = 26.0, 16.0, 5.0


# ------------------------------------------------------------------ outline rectangle arrondi
class RR:
    def __init__(self, hx=HX, hz=HZ, r=CR, step=1.0):
        self.hx, self.hz, self.r = hx, hz, r
        self.nx = max(2, int(math.ceil(2 * (hx - r) / step)))
        self.nz = max(2, int(math.ceil(2 * (hz - r) / step)))
        self.na = max(6, int(math.ceil(r * math.pi / 2 / step)))
        self._dense = {}

    def _raw(self, d):
        hx, hz, r = self.hx, self.hz, self.r
        P, Nn = [], []
        ax, az = hx - r, hz - r
        for k in range(self.nx):
            P.append((-ax + 2 * ax * k / self.nx, -(hz + d)))
            Nn.append((0, -1))
        for k in range(self.na):
            f = -math.pi / 2 + (math.pi / 2) * k / self.na
            P.append((ax + (r + d) * math.cos(f), -az + (r + d) * math.sin(f)))
            Nn.append((math.cos(f), math.sin(f)))
        for k in range(self.nz):
            P.append((hx + d, -az + 2 * az * k / self.nz))
            Nn.append((1, 0))
        for k in range(self.na):
            f = (math.pi / 2) * k / self.na
            P.append((ax + (r + d) * math.cos(f), az + (r + d) * math.sin(f)))
            Nn.append((math.cos(f), math.sin(f)))
        for k in range(self.nx):
            P.append((ax - 2 * ax * k / self.nx, hz + d))
            Nn.append((0, 1))
        for k in range(self.na):
            f = math.pi / 2 + (math.pi / 2) * k / self.na
            P.append((-ax + (r + d) * math.cos(f), az + (r + d) * math.sin(f)))
            Nn.append((math.cos(f), math.sin(f)))
        for k in range(self.nz):
            P.append((-(hx + d), az - 2 * az * k / self.nz))
            Nn.append((-1, 0))
        for k in range(self.na):
            f = math.pi + (math.pi / 2) * k / self.na
            P.append((-ax + (r + d) * math.cos(f), -az + (r + d) * math.sin(f)))
            Nn.append((math.cos(f), math.sin(f)))
        return np.array(P), np.array(Nn)

    def pts(self, d):
        """(P (N,2), N (N,2) normales sortantes, s (N) abscisse curviligne de la courbe de base d=0)"""
        P, Nn = self._raw(d)
        return P, Nn, self.s_base()

    def s_base(self):
        if 'sb' not in self._dense:
            pp, _ = self._raw(0.0)
            seg = np.linalg.norm(np.roll(pp, -1, 0) - pp, axis=1)
            s = np.concatenate([[0], np.cumsum(seg)[:-1]])
            self._dense['sb'] = (s, float(seg.sum()))
        return self._dense['sb'][0]

    def length(self):
        self.s_base()
        return self._dense['sb'][1]

    def dense(self, d, step=0.05):
        key = ('d', round(d, 4), step)
        if key not in self._dense:
            rr = RR(self.hx, self.hz, self.r, step)
            P, Nn, _ = rr.pts(d)
            Pc = np.vstack([P, P[:1]])
            seg = np.linalg.norm(np.diff(Pc, axis=0), axis=1)
            cum = np.concatenate([[0], np.cumsum(seg)])
            Nc = np.vstack([Nn, Nn[:1]])
            self._dense[key] = (Pc, Nc, cum)
        return self._dense[key]

    def along(self, spacing, d=0.0, offset=0.0, count=None):
        """points équirépartis le long de la courbe décalée d. retourne P (k,2), N (k,2), T (k,2), s (k)"""
        Pc, Nc, cum = self.dense(d)
        L = cum[-1]
        k = count if count else max(1, int(round(L / spacing)))
        s = (offset + np.arange(k) * L / k) % L
        x = np.interp(s, cum, Pc[:, 0])
        z = np.interp(s, cum, Pc[:, 1])
        nx = np.interp(s, cum, Nc[:, 0])
        nz = np.interp(s, cum, Nc[:, 1])
        nn = np.hypot(nx, nz)
        nx, nz = nx / nn, nz / nn
        P = np.stack([x, z], 1)
        N = np.stack([nx, nz], 1)
        T = np.stack([-nz, nx], 1)  # tangent (rotation +90°)
        return P, N, T, s

    def at_base(self, s, d=0.0):
        """point d'abscisse curviligne de base s décalé de d."""
        Pc, Nc, cum = self.dense(0.0)
        s = s % cum[-1]
        x = np.interp(s, cum, Pc[:, 0])
        z = np.interp(s, cum, Pc[:, 1])
        nx = np.interp(s, cum, Nc[:, 0])
        nz = np.interp(s, cum, Nc[:, 1])
        n = math.hypot(nx, nz)
        nx, nz = nx / n, nz / n
        return np.array([x + d * nx, z + d * nz]), np.array([nx, nz])

    def s_nearest(self, x, z):
        Pc, Nc, cum = self.dense(0.0)
        i = np.argmin((Pc[:, 0] - x) ** 2 + (Pc[:, 1] - z) ** 2)
        return cum[i]

    def sdf(self, x, z, d=0.0):
        qx = np.abs(x) - (self.hx - self.r)
        qz = np.abs(z) - (self.hz - self.r)
        out = np.hypot(np.maximum(qx, 0), np.maximum(qz, 0)) + np.minimum(np.maximum(qx, qz), 0) - self.r
        return out - d


RRECT = RR()


def ring_strip(rr, rows, ref='up', skip=None, uvsize=4.0, wrap_uv=True, vmode='auto'):
    """rows : [(d, y), ...]. Quads entre lignes successives, boucle fermée.
    skip : liste de (s0, s1) abscisses de base à ne pas remplir. Retourne (V, F, UV)."""
    ptsets = []
    for d, y in rows:
        P, Nn, s = rr.pts(d)
        ptsets.append((P, Nn, s, d, y))
    N = len(ptsets[0][0])
    L = rr.length()
    nrep = max(1, round(L / uvsize))
    ukey = nrep / L
    V = []
    UV = []
    for (P, Nn, s, d, y) in ptsets:
        for i in range(N + 1):
            ii = i % N
            V.append((P[ii, 0], y, P[ii, 1]))
        for i in range(N + 1):
            ss = s[i] if i < N else L
            UV.append((ss * ukey, 0.0))
    V = np.array(V, float)
    UV = np.array(UV, float)
    M = len(rows)
    W = N + 1
    # v coordinate
    for k in range(M):
        d, y = rows[k]
        if k == 0:
            vacc = 0.0
        else:
            d0, y0 = rows[k - 1]
            vacc += math.hypot(d - d0, y - y0)
        UV[k * W:(k + 1) * W, 1] = vacc / uvsize
    F = []
    sb = ptsets[0][2]
    for k in range(M - 1):
        fl = []
        for i in range(N):
            if skip:
                sm = sb[i] + 0.5 * (rr.length() / N)
                if any(a <= sm <= b for a, b in skip):
                    continue
            a = k * W + i
            b = k * W + i + 1
            c = (k + 1) * W + i + 1
            dd = (k + 1) * W + i
            fl.append((a, b, c, dd))
        if not fl:
            continue
        # orientation
        a, b, c, dd = fl[0]
        n = np.cross(V[b] - V[a], V[dd] - V[a])
        if ref == 'up':
            rv = np.array([0, 1, 0.0])
        elif ref == 'down':
            rv = np.array([0, -1, 0.0])
        else:
            Nn0 = ptsets[0][1][fl[0][0] % W % N]
            rv = np.array([Nn0[0], 0, Nn0[1]])
            if ref == 'in':
                rv = -rv
        if np.dot(n, rv) < 0:
            fl = [tuple(reversed(f)) for f in fl]
        F += fl
    return V, F, UV


# ------------------------------------------------------------------ sol
def ground_mesh(rr=RRECT, step=0.5, uvx=(-26.5, 26.5), uvz=(-16.5625, 16.5625), apron=1.2):
    hx, hz, r = rr.hx, rr.hz, rr.r
    xs = np.arange(-hx, hx + 1e-6, step)
    zs = np.arange(-hz, hz + 1e-6, step)
    nx, nz = len(xs), len(zs)
    X, Z = np.meshgrid(xs, zs)
    sd = rr.sdf(X, Z)
    qx = np.clip(X, -(hx - r), hx - r)
    qz = np.clip(Z, -(hz - r), hz - r)
    vx, vz = X - qx, Z - qz
    L = np.hypot(vx, vz)
    outside = L > r
    Xp = np.where(outside, qx + vx / np.maximum(L, 1e-9) * r, X)
    Zp = np.where(outside, qz + vz / np.maximum(L, 1e-9) * r, Z)
    V = np.stack([Xp.ravel(), np.zeros(X.size), Zp.ravel()], 1)
    F = []
    inside = sd < -1e-6
    for j in range(nz - 1):
        for i in range(nx - 1):
            if not (inside[j, i] or inside[j, i + 1] or inside[j + 1, i] or inside[j + 1, i + 1]):
                continue
            a = j * nx + i
            b = a + 1
            c = a + nx + 1
            d = a + nx
            # on retire cellules dégénérées
            q = [V[a], V[b], V[c], V[d]]
            area = 0.5 * abs(sum(q[k][0] * q[(k + 1) % 4][2] - q[(k + 1) % 4][0] * q[k][2] for k in range(4)))
            if area < 1e-5:
                continue
            F.append((a, d, c, b))  # normale +Y
    # apron sous le mur
    P, Nn, s = rr.pts(-0.02)
    P2, _, _ = rr.pts(apron)
    n0 = len(V)
    Vr = np.array([(p[0], -0.01, p[1]) for p in P] + [(p[0], -0.01, p[1]) for p in P2])
    N = len(P)
    for i in range(N):
        j = (i + 1) % N
        F.append((n0 + i, n0 + N + i, n0 + N + j, n0 + j))
    V = np.vstack([V, Vr])
    # orientation globale : première face de l'apron
    a, b, c, d = F[-1]
    nrm = np.cross(V[b] - V[a], V[d] - V[a])
    if nrm[1] < 0:
        F[-N:] = [tuple(reversed(f)) for f in F[-N:]]
    u = (V[:, 0] - uvx[0]) / (uvx[1] - uvx[0])
    v = 1.0 - (V[:, 2] - uvz[0]) / (uvz[1] - uvz[0])
    UV = np.stack([u, v], 1)
    return V, F, UV


# ------------------------------------------------------------------ matériaux
MATS = {}


def defmat(name, tex=None, norm=None, emit_tex=None, emit=None, emit_str=0.0, rough=0.8, metal=0.0,
           uv=4.0, vcol=True, double=False, alpha=False, color=(1, 1, 1), spec=0.5, norm_str=1.0):
    MATS[name] = dict(tex=tex, norm=norm, emit_tex=emit_tex, emit=emit, emit_str=emit_str, rough=rough, metal=metal,
                      uv=uv, vcol=vcol, double=double, alpha=alpha, color=color, spec=spec, norm_str=norm_str)


def uvsizes():
    return {k: v['uv'] for k, v in MATS.items()}


def _img(path, srgb=True):
    import bpy
    key = os.path.basename(path)
    if key in bpy.data.images:
        return bpy.data.images[key]
    im = bpy.data.images.load(path)
    im.name = key
    im.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
    return im


def build_material(name):
    import bpy
    spec = MATS[name]
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(b.outputs[0], out.inputs[0])
    b.inputs['Roughness'].default_value = spec['rough']
    b.inputs['Metallic'].default_value = spec['metal']
    try:
        b.inputs['Specular IOR Level'].default_value = spec['spec']
    except KeyError:
        pass
    src = None
    if spec['tex']:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = _img(spec['tex'], True)
        t.interpolation = 'Linear'
        t.extension = 'REPEAT'
        src = t.outputs['Color']
    if spec['vcol']:
        vc = nt.nodes.new('ShaderNodeVertexColor')
        vc.layer_name = 'Color'
        if src is not None:
            mx = nt.nodes.new('ShaderNodeMix')
            mx.data_type = 'RGBA'
            mx.blend_type = 'MULTIPLY'
            mx.inputs[0].default_value = 1.0
            nt.links.new(src, mx.inputs[6])
            nt.links.new(vc.outputs['Color'], mx.inputs[7])
            nt.links.new(mx.outputs[2], b.inputs['Base Color'])
        else:
            nt.links.new(vc.outputs['Color'], b.inputs['Base Color'])
    else:
        if src is not None:
            nt.links.new(src, b.inputs['Base Color'])
        else:
            c = s2l(spec['color'])
            b.inputs['Base Color'].default_value = (c[0], c[1], c[2], 1)
    if spec['norm']:
        t2 = nt.nodes.new('ShaderNodeTexImage')
        t2.image = _img(spec['norm'], False)
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = spec['norm_str']
        nt.links.new(t2.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if spec['emit_tex']:
        t3 = nt.nodes.new('ShaderNodeTexImage')
        t3.image = _img(spec['emit_tex'], True)
        nt.links.new(t3.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = spec['emit_str'] or 1.0
    elif spec['emit'] is not None:
        c = s2l(spec['emit'])
        b.inputs['Emission Color'].default_value = (c[0], c[1], c[2], 1)
        b.inputs['Emission Strength'].default_value = spec['emit_str'] or 1.0
    if spec['alpha']:
        m.surface_render_method = 'BLENDED'
        if spec['tex']:
            nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
    m.use_backface_culling = not spec['double']
    return m


# ------------------------------------------------------------------ scène
class Scene:
    def __init__(self, name):
        self.name = name
        self.parts = {}
        self.empties = []
        self.noao = set()
        self.ao_opts = {}
        self.join_fx = None

    def part(self, name, origin=(0, 0, 0)):
        if name not in self.parts:
            self.parts[name] = MB(name, origin)
        return self.parts[name]

    def empty(self, name, x, y, z):
        self.empties.append((name, (x, y, z)))

    def build(self, ao_samples=48, ao_dist=3.0, ao_floor=0.42, ao_gamma=1.0, blend_save=None, smooth_deg=62):
        import bpy
        import bmesh
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        coll = sc.collection
        t0 = time.time()
        objs = {}
        tri_total = 0
        uvs = uvsizes()
        for name, mb in self.parts.items():
            if mb.n == 0:
                continue
            d = mb.finalize(uvs)
            P = d['P'] - mb.origin
            Pb = np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1)  # jeu -> Blender
            me = bpy.data.meshes.new(name)
            nl = len(d['lv'])
            nf = len(d['lstart'])
            me.vertices.add(len(Pb))
            me.vertices.foreach_set('co', Pb.astype(np.float32).ravel())
            me.loops.add(nl)
            me.loops.foreach_set('vertex_index', d['lv'].astype(np.int32))
            me.polygons.add(nf)
            me.polygons.foreach_set('loop_start', d['lstart'].astype(np.int32))
            me.polygons.foreach_set('use_smooth', np.ones(nf, bool))
            me.update(calc_edges=True)
            nf0 = len(me.polygons)
            me.validate()
            if len(me.polygons) != nf0 or len(me.loops) != nl:
                print('[WARN] validate a modifié', name, nf0, len(me.polygons))
            # matériaux
            for mname in mb.mats:
                me.materials.append(build_material(mname))
            me.polygons.foreach_set('material_index', d['fmat'])
            uvl = me.uv_layers.new(name='UVMap')
            uv = d['uv'].copy()
            uvl.data.foreach_set('uv', uv.astype(np.float32).ravel())
            # arêtes vives selon l'angle
            bm = bmesh.new()
            bm.from_mesh(me)
            thr = math.radians(smooth_deg)
            for e in bm.edges:
                if len(e.link_faces) == 2:
                    e.smooth = e.calc_face_angle(0.0) < thr
                else:
                    e.smooth = True
            for f in bm.faces:
                f.smooth = True
            bm.to_mesh(me)
            bm.free()
            # couleurs
            tint_loop = d['T'][d['lv']]
            rgba = np.concatenate([tint_loop, np.ones((nl, 1))], 1).astype(np.float32)
            ca = me.color_attributes.new('Tint', 'FLOAT_COLOR', 'CORNER')
            ca.data.foreach_set('color', rgba.ravel())
            ao = me.color_attributes.new('AO', 'FLOAT_COLOR', 'CORNER')
            col = me.color_attributes.new('Color', 'FLOAT_COLOR', 'CORNER')
            ao.data.foreach_set('color', np.ones(nl * 4, np.float32))
            col.data.foreach_set('color', rgba.ravel())
            me.color_attributes.active_color = ao
            ob = bpy.data.objects.new(name, me)
            ob.location = (mb.origin[0], -mb.origin[2], mb.origin[1])
            coll.objects.link(ob)
            objs[name] = ob
            tri_total += int(np.sum(d['flen'] - 2))
        print(f"[build] meshes ok {time.time() - t0:.1f}s tris={tri_total}")
        # AO bake
        t0 = time.time()
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = ao_samples
        sc.cycles.device = 'CPU'
        w = bpy.data.worlds.new('w')
        sc.world = w
        w.light_settings.distance = ao_dist
        bake_objs = [o for n, o in objs.items() if n not in self.noao]
        for n in self.noao:
            if n in objs:
                objs[n].hide_render = True
        bpy.ops.object.select_all(action='DESELECT')
        for o in bake_objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = bake_objs[0]
        for o in bake_objs:
            o.data.color_attributes.active_color = o.data.color_attributes['AO']
        try:
            bpy.ops.object.bake(type='AO', target='VERTEX_COLORS')
        except Exception as e:
            print("[bake] ERREUR", e)
        for n in self.noao:
            if n in objs:
                objs[n].hide_render = False
        print(f"[build] bake AO {time.time() - t0:.1f}s")
        for name, ob in objs.items():
            me = ob.data
            nl = len(me.loops)
            tint = np.empty(nl * 4, np.float32)
            me.color_attributes['Tint'].data.foreach_get('color', tint)
            tint = tint.reshape(-1, 4)
            if name in self.noao:
                final = tint
            else:
                ao = np.empty(nl * 4, np.float32)
                me.color_attributes['AO'].data.foreach_get('color', ao)
                a = np.clip(ao.reshape(-1, 4)[:, :1], 0, 1) ** ao_gamma
                fl = self.ao_opts.get(name, ao_floor)
                f = fl + (1 - fl) * a
                final = tint.copy()
                final[:, :3] = tint[:, :3] * f
            me.color_attributes['Color'].data.foreach_set('color', final.astype(np.float32).ravel())
            me.color_attributes.remove(me.color_attributes['AO'])
            me.color_attributes.remove(me.color_attributes['Tint'])
            me.color_attributes.active_color = me.color_attributes['Color']
            me.color_attributes.render_color_index = me.color_attributes.active_color_index
        # empties
        for name, (x, y, z) in self.empties:
            e = bpy.data.objects.new(name, None)
            e.empty_display_type = 'PLAIN_AXES'
            e.empty_display_size = 0.3
            e.location = (x, -z, y)
            coll.objects.link(e)
        self.tri_total = tri_total
        if self.join_fx and self.join_fx[0] in objs and self.join_fx[1] in objs:
            bpy.ops.object.select_all(action='DESELECT')
            objs[self.join_fx[0]].select_set(True)
            objs[self.join_fx[1]].select_set(True)
            bpy.context.view_layer.objects.active = objs[self.join_fx[1]]
            bpy.ops.object.join()
        if blend_save:
            bpy.ops.wm.save_as_mainfile(filepath=blend_save)
        return objs

    def export(self, path):
        import bpy
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_vertex_color='ACTIVE',
                                  export_yup=True, export_apply=False, export_cameras=False, export_lights=False,
                                  export_image_format='AUTO', export_materials='EXPORT', export_texcoords=True,
                                  export_normals=True, export_extras=False, use_selection=False,
                                  export_all_vertex_colors=False)
        sz = os.path.getsize(path) / 1e6
        print(f"[export] {path} {sz:.1f} Mo, {self.tri_total} triangles")
        return sz


# ------------------------------------------------------------------ foule
def _person(arms=False):
    tor = p_lathe([(0.27, 0.0), (0.23, 0.38), (0.11, 0.6)], 6, False, True)
    hd = p_sphere(0.14, 6, 3)
    hd = (hd[0] + np.array([0, 0.74, 0]), hd[1])
    cap = p_lathe([(0.15, 0.0), (0.0, 0.15)], 6, False, False)
    cap = (cap[0] + np.array([0, 0.79, 0]), cap[1])
    parts = [tor, hd, cap]
    slot_ids = [0, 1, 2]
    if arms:
        for sd in (-1, 1):
            a = p_lathe([(0.055, 0.0), (0.04, 0.46)], 4, False, True)
            V = a[0] @ rotm(0, 0, sd * 0.3).T + np.array([sd * 0.27, 0.5, 0])
            parts.append((V, a[1]))
            slot_ids.append(0)
    V, F, S = [], [], []
    for (v, f), sid in zip(parts, slot_ids):
        base = sum(len(x) for x in V)
        V.append(v)
        F += [tuple(i + base for i in ff) for ff in f]
        S += [sid] * len(v)
    return (np.concatenate(V), F), np.array(S)


def crowd(mb, rr, tiers, palette, skin, hair, spacing=0.9, skip=0.1, rng=None, mat='M_crowd', scale=(0.92, 1.1), exclude=None,
          arms_prob=0.2, d_shift=0.0, hat_pal=None):
    """tiers : liste de (d_centre, y). Spectateurs assis tournés vers l'arène (coordonnées jeu)."""
    rng = rng or G.RNG
    pal = [s2l(c) for c in palette]
    sk = [s2l(c) for c in skin]
    hr = [s2l(c) for c in (hat_pal or hair)]
    data = {False: [], True: []}
    for (dc, y) in tiers:
        P, N, T, s = rr.along(spacing, dc + d_shift, offset=rng.uniform(0, spacing))
        for i in range(len(P)):
            if rng.random() < skip:
                continue
            jit = rng.uniform(-0.07, 0.07, 2)
            px, pz = P[i, 0] + jit[0], P[i, 1] + jit[1]
            if exclude is not None and exclude(px, pz):
                continue
            yaw = math.atan2(-N[i, 0], -N[i, 1]) + rng.uniform(-0.3, 0.3)
            sc_ = rng.uniform(*scale)
            c = pal[rng.integers(len(pal))] * rng.uniform(0.8, 1.15)
            data[rng.random() < arms_prob].append((px, y, pz, yaw, sc_, c,
                                                  sk[rng.integers(len(sk))] * rng.uniform(0.85, 1.1),
                                                  hr[rng.integers(len(hr))] * rng.uniform(0.7, 1.2)))
    total = 0
    for arms, lst in data.items():
        if not lst:
            continue
        VF, slots = _person(arms)
        arr = lst
        pos = np.array([(a[0], a[1], a[2]) for a in arr])
        yaw = np.array([a[3] for a in arr])
        scl = np.array([a[4] for a in arr])
        tint = np.stack([np.stack([a[5], a[6], a[7]]) for a in arr])
        mb.add_many(VF, mat, pos, yaw=yaw, scale=scl, tint=tint, slots=slots)
        total += len(arr)
    return total
