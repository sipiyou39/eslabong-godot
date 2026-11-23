"""Rendu EEVEE des pièces avec un matériau test qui colore selon le masque de sommets."""
import math, os
import numpy as np
import bpy
from mathutils import Vector

PRIM = (0.55, 0.06, 0.07)
SEC = (0.10, 0.30, 0.75)
ACC = (1.0, 0.72, 0.12)
SKINC = (0.93, 0.78, 0.62)


def test_material(prim=PRIM, sec=SEC, acc=ACC, skin=SKINC, name="M_Test"):
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vc = nt.nodes.new("ShaderNodeVertexColor")
    vc.layer_name = "Color"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(vc.outputs["Color"], sep.inputs["Color"])

    def vm(op):
        n = nt.nodes.new("ShaderNodeVectorMath")
        n.operation = op
        return n

    def math_(op, a=None, b=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        n.use_clamp = False
        return n

    # poids peau = 1 - R - G - B
    s1 = math_('ADD')
    nt.links.new(sep.outputs[0], s1.inputs[0])
    nt.links.new(sep.outputs[1], s1.inputs[1])
    s2 = math_('ADD')
    nt.links.new(s1.outputs[0], s2.inputs[0])
    nt.links.new(sep.outputs[2], s2.inputs[1])
    s3 = math_('SUBTRACT')
    s3.inputs[0].default_value = 1.0
    nt.links.new(s2.outputs[0], s3.inputs[1])
    s3.use_clamp = True

    def colterm(col, wsock):
        n = vm('SCALE')
        n.inputs[0].default_value = col
        nt.links.new(wsock, n.inputs['Scale'])
        return n.outputs[0]

    t = [colterm(PRIM if False else prim, sep.outputs[0]), colterm(sec, sep.outputs[1]),
         colterm(acc, sep.outputs[2]), colterm(skin, s3.outputs[0])]
    a = vm('ADD'); nt.links.new(t[0], a.inputs[0]); nt.links.new(t[1], a.inputs[1])
    b = vm('ADD'); nt.links.new(a.outputs[0], b.inputs[0]); nt.links.new(t[2], b.inputs[1])
    c = vm('ADD'); nt.links.new(b.outputs[0], c.inputs[0]); nt.links.new(t[3], c.inputs[1])
    ao = vm('SCALE')
    nt.links.new(c.outputs[0], ao.inputs[0])
    nt.links.new(vc.outputs["Alpha"], ao.inputs['Scale'])
    nt.links.new(ao.outputs[0], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.55
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return m


def set_material(objs, mat):
    for o in objs:
        if o.type == 'MESH':
            o.data.materials.clear()
            o.data.materials.append(mat)


def setup_scene(w=480, h=640, bg=(0.30, 0.31, 0.34)):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = 'Standard'
    except Exception:
        pass
    sc.view_settings.look = 'None'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    world = bpy.data.worlds.new("w") if not bpy.data.worlds else bpy.data.worlds[0]
    sc.world = world
    world.use_nodes = True
    bgn = world.node_tree.nodes["Background"]
    bgn.inputs[0].default_value = (*bg, 1)
    bgn.inputs[1].default_value = 0.9
    for o in [o for o in bpy.data.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(o)
    def sun(name, rot, energy, col=(1, 1, 1)):
        l = bpy.data.lights.new(name, 'SUN')
        l.energy = energy
        l.color = col
        l.angle = math.radians(25)
        ob = bpy.data.objects.new(name, l)
        ob.rotation_euler = rot
        sc.collection.objects.link(ob)
    sun("key", (math.radians(55), math.radians(10), math.radians(-35)), 3.2, (1.0, 0.96, 0.9))
    sun("fill", (math.radians(65), 0, math.radians(140)), 1.2, (0.8, 0.88, 1.0))
    sun("rim", (math.radians(110), 0, math.radians(180)), 1.6, (1, 1, 1))
    cam = bpy.data.cameras.new("cam")
    cam.lens = 90
    cam.clip_end = 100
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    return co


def aim_camera(cam, target, azim_deg, elev_deg, dist, ortho=None):
    """azim 0 = vue de face (le perso regarde -Y blender → caméra en -Y). repère BLENDER."""
    a = math.radians(azim_deg)
    e = math.radians(elev_deg)
    tx, ty, tz = target
    # position : face = -Y ; azim positif = tourne vers +X
    pos = Vector((tx + dist * math.cos(e) * math.sin(a), ty - dist * math.cos(e) * math.cos(a), tz + dist * math.sin(e)))
    cam.location = pos
    d = Vector(target) - pos
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if ortho:
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = ortho
    else:
        cam.data.type = 'PERSP'


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
