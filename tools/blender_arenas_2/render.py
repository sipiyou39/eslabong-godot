"""Rendu de contrôle d'un GLB (EEVEE, caméra de jeu). Usage :
Blender -b --python render.py -- <fichier.glb> <sortie.png> <theme> [vue] [WxH]
vue : game | wide | iso | top | cx,cy,cz:tx,ty,tz:fov  (coordonnées jeu)"""
import sys
import os
import math
import json
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from themes import THEMES

argv = sys.argv[sys.argv.index('--') + 1:]
glb, out, theme = argv[0], argv[1], argv[2]
view = argv[3] if len(argv) > 3 else 'game'
res = argv[4] if len(argv) > 4 else '1280x720'
RW, RH = [int(v) for v in res.split('x')]
T = THEMES[theme]


def g2b(p):
    return Vector((p[0], -p[2], p[1]))


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = RW, RH
sc.render.film_transparent = False
try:
    sc.eevee.taa_render_samples = 48
    sc.eevee.use_raytracing = True
    sc.eevee.ray_tracing_method = 'SCREEN'
    sc.eevee.use_shadows = True
except Exception as e:
    print('eevee opts', e)
sc.view_settings.view_transform = T.get('view', 'AgX')
sc.view_settings.look = T.get('look', 'None')
sc.view_settings.exposure = T.get('exposure', 0.0)

# monde (dégradé horizon -> zénith comme le ciel procédural du jeu)
w = bpy.data.worlds.new('w')
w.use_nodes = True
nt = w.node_tree
for n_ in list(nt.nodes):
    nt.nodes.remove(n_)
sky = T['sky']
sky_top = T.get('sky_top', sky)
tc = nt.nodes.new('ShaderNodeTexCoord')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(tc.outputs['Object'], sep.inputs[0])
mr = nt.nodes.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value = -0.05
mr.inputs['From Max'].default_value = 0.85
mr.clamp = True
nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (sky[0], sky[1], sky[2], 1)
ramp.color_ramp.elements[1].color = (sky_top[0], sky_top[1], sky_top[2], 1)
nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
bg = nt.nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = T.get('sky_str', 1.0)
nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
wo = nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(bg.outputs['Background'], wo.inputs['Surface'])
sc.world = w

# soleil
for i, L in enumerate(T['suns']):
    sun = bpy.data.lights.new(f'sun{i}', 'SUN')
    sun.energy = L['e']
    sun.color = L['c']
    sun.angle = math.radians(L.get('ang', 2.0))
    ob = bpy.data.objects.new(f'sun{i}', sun)
    sc.collection.objects.link(ob)
    d = g2b(L['dir'])
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

# lumières aux torches / lights
for o in list(bpy.data.objects):
    if o.name.startswith('Torch_') or o.name.startswith('Light_'):
        tl = T.get('torch', None)
        if o.name.startswith('Light_'):
            tl = T.get('light', tl)
        if tl:
            lt = bpy.data.lights.new('pl', 'POINT')
            lt.color = tl['c']
            lt.energy = tl['e']
            lt.shadow_soft_size = 0.25
            lt.use_shadow = False
            lo = bpy.data.objects.new('pl', lt)
            lo.location = o.matrix_world.translation + Vector((0, 0, 0.3))
            sc.collection.objects.link(lo)
for k, L in enumerate(T.get('points', [])):
    lt = bpy.data.lights.new('pt', 'POINT')
    lt.color = L['c']
    lt.energy = L['e']
    lt.shadow_soft_size = L.get('r', 1.0)
    lo = bpy.data.objects.new('pt', lt)
    lo.location = g2b(L['p'])
    sc.collection.objects.link(lo)

# caméra
cam = bpy.data.cameras.new('cam')
cam.sensor_fit = 'VERTICAL'
cam.clip_end = 600
co = bpy.data.objects.new('cam', cam)
sc.collection.objects.link(co)
sc.camera = co
V = T.get('views', {})
if view in V:
    spec = V[view]
else:
    spec = None
if view == 'game':
    pos, tgt, fov = (0, 26, 22), (0, 0, 0), 55
elif view == 'wide':
    pos, tgt, fov = (0, 70, 62), (0, 2, 0), 45
elif view == 'iso':
    pos, tgt, fov = (-48, 36, 44), (0, 3, 0), 42
elif view == 'top':
    pos, tgt, fov = (0, 90, 0.01), (0, 0, 0), 38
elif spec:
    pos, tgt, fov = spec
else:
    a, b, c = view.split(':')
    pos = tuple(float(v) for v in a.split(','))
    tgt = tuple(float(v) for v in b.split(','))
    fov = float(c)
cam.angle = math.radians(fov)
co.location = g2b(pos)
d = g2b(tgt) - g2b(pos)
co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('rendered', out)
