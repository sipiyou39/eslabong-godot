"""Rend des vues PNG (fond transparent) de chaque objet d'un GLB, avec un matériau test qui colore selon le masque.
usage : Blender -b --python render_views.py -- <fichier.glb> <dossier_sortie> [--views a,b,c] [--res 480x640] [noms...]
"""
import bpy
import sys
import os
import math
import json
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
glb, outdir = argv[0], argv[1]
rest = argv[2:]
views = ["side", "tq"]
views_forced = False
res = (480, 640)
only = []
i = 0
while i < len(rest):
    if rest[i] == "--views":
        views = rest[i + 1].split(",")
        views_forced = True
        i += 2
    elif rest[i] == "--res":
        w, h = rest[i + 1].split("x")
        res = (int(w), int(h))
        i += 2
    else:
        only.append(rest[i])
        i += 1
os.makedirs(outdir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
scn = bpy.context.scene
scn.render.engine = "BLENDER_EEVEE"
scn.render.resolution_x, scn.render.resolution_y = res
scn.render.film_transparent = True
scn.view_settings.view_transform = "Standard"
try:
    scn.eevee.taa_render_samples = 24
except Exception:
    pass

# monde
world = bpy.data.worlds.new("W")
scn.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.55, 0.57, 0.62, 1)
bg.inputs["Strength"].default_value = 0.85

# lumières (repère Blender : l'avant du perso = -Y)
def sun(rot, energy, col=(1, 1, 1)):
    d = bpy.data.lights.new("s", "SUN")
    d.energy = energy
    d.color = col
    d.angle = math.radians(25)
    o = bpy.data.objects.new("s", d)
    scn.collection.objects.link(o)
    o.rotation_euler = [math.radians(a) for a in rot]
    return o

sun((50, 0, -35), 3.2, (1.0, 0.96, 0.9))
sun((70, 0, 140), 1.1, (0.8, 0.88, 1.0))

cam_d = bpy.data.cameras.new("c")
cam_d.type = "ORTHO"
cam = bpy.data.objects.new("c", cam_d)
scn.collection.objects.link(cam)
scn.camera = cam

PAL = {"base": (0.80, 0.76, 0.66), "R": (0.46, 0.27, 0.13), "G": (0.17, 0.19, 0.27), "B": (0.80, 0.85, 0.94)}


def srgb(c):
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def preview_mat(attr_name, accent):
    m = bpy.data.materials.new("P")
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    for n in list(nodes):
        nodes.remove(n)
    at = nodes.new("ShaderNodeAttribute")
    at.attribute_name = attr_name
    at.attribute_type = "GEOMETRY"
    sep = nodes.new("ShaderNodeSeparateColor")
    links.new(at.outputs["Color"], sep.inputs["Color"])
    cB = srgb(accent) if accent else srgb(PAL["B"])
    cols = [srgb(PAL["base"]), srgb(PAL["R"]), srgb(PAL["G"]), cB]
    prev = None
    for k, ch in enumerate(["Red", "Green", "Blue"]):
        mx = nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        links.new(sep.outputs[ch], mx.inputs[0])
        if prev is None:
            mx.inputs[6].default_value = (*cols[0], 1)
        else:
            links.new(prev.outputs[2], mx.inputs[6])
        mx.inputs[7].default_value = (*cols[k + 1], 1)
        prev = mx
    ao = nodes.new("ShaderNodeMix")
    ao.data_type = "RGBA"
    ao.blend_type = "MULTIPLY"
    ao.inputs[0].default_value = 1.0
    links.new(prev.outputs[2], ao.inputs[6])
    comb = nodes.new("ShaderNodeCombineColor")
    for ch in ("Red", "Green", "Blue"):
        links.new(at.outputs["Alpha"], comb.inputs[ch])
    links.new(comb.outputs["Color"], ao.inputs[7])
    bs = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(ao.outputs[2], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.55
    if accent:
        links.new(sep.outputs["Blue"], bs.inputs["Emission Strength"])
        bs.inputs["Emission Color"].default_value = (*cB, 1)
        bs.inputs["Emission Strength"].default_value = 0.0
        mul = nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = 0.35
        links.new(sep.outputs["Blue"], mul.inputs[0])
        links.new(mul.outputs[0], bs.inputs["Emission Strength"])
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    return m


VIEWS = {  # direction caméra -> objet (repère Blender), up = Z
    "side": (1.0, 0.0, 0.0),
    "tq": (0.62, -0.62, 0.48),
    "front": (0.0, -1.0, 0.0),
    "top": (0.0, -0.45, 0.9),
    "back": (-0.62, 0.62, 0.48),
}

try:
    meta = {}
    mp = os.path.join(os.path.dirname(glb), os.path.basename(glb).replace(".glb", "_manifest.json"))
    if os.path.exists(mp):
        for e in json.load(open(mp)).get("pieces", []):
            meta[e["name"]] = e
except Exception:
    meta = {}

todo = [o for o in objs if (not only or any(o.name.startswith(n) or o.name == n for n in only))]
todo.sort(key=lambda o: o.name)
for o in objs:
    o.hide_render = True
for o in todo:
    me = o.data
    attr = me.color_attributes.active_color or me.color_attributes[0]
    accent = None
    if o["accent"] if "accent" in o.keys() else False:
        accent = tuple(o["accent"])
    elif o.name in meta and meta[o.name].get("accent"):
        accent = tuple(meta[o.name]["accent"])
    me.materials.clear()
    me.materials.append(preview_mat(attr.name, accent))
    o.hide_render = False
    corners = np.array([o.matrix_world @ Vector(c) for c in o.bound_box])
    ctr = (corners.min(0) + corners.max(0)) / 2
    pv_list = meta[o.name].get('views', '').split(',') if (o.name in meta and meta[o.name].get('views') and not views_forced) else views
    for vname in pv_list:
        vn, _, crop = vname.partition('@')
        d = Vector(VIEWS[vn]).normalized()
        cam.location = Vector(ctr) + d * 6
        direction = -d
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        mw = cam.matrix_world.to_3x3()
        right, up = mw @ Vector((1, 0, 0)), mw @ Vector((0, 1, 0))
        cs = corners
        if crop:
            ys = corners[:, 2]
            lo, hi = ys.min(), ys.max()
            frac = 0.30
            if crop == 'top':
                cs = corners.copy()
                cs[:, 2] = np.where(corners[:, 2] < hi - (hi - lo) * frac, hi - (hi - lo) * frac, corners[:, 2])
            elif crop == 'bot':
                cs = corners.copy()
                cs[:, 2] = np.where(corners[:, 2] > lo + (hi - lo) * frac, lo + (hi - lo) * frac, corners[:, 2])
        pu = cs @ np.array(right)
        pv = cs @ np.array(up)
        ext_u, ext_v = pu.max() - pu.min(), pv.max() - pv.min()
        cu, cv = (pu.max() + pu.min()) / 2, (pv.max() + pv.min()) / 2
        aspect = res[0] / res[1]
        scale = max(ext_v, ext_u / aspect) * 1.12 + 0.03
        cam_d.ortho_scale = scale
        # recentrer
        cc = Vector(ctr)
        cur_u = cc.dot(right)
        cur_v = cc.dot(up)
        cam.location = cam.location + right * (cu - cur_u) + up * (cv - cur_v)
        scn.render.filepath = os.path.join(outdir, f"{o.name}__{vname}.png")
        bpy.ops.render.render(write_still=True)
    o.hide_render = True
print("RENDER_DONE", len(todo))
