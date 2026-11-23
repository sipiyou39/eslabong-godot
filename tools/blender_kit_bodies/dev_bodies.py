"""Rendu de développement : Blender -b --python dev_bodies.py -- <espèce> [out_dir]"""
import sys, os, math, importlib
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import bpy
import numpy as np
import kitlib, preview_lib
argv = sys.argv[sys.argv.index('--') + 1:]
species = argv[0]
out = argv[1] if len(argv) > 1 else '/tmp'
kitlib.reset_scene()
import species as SPM
parts = SPM.REGISTRY[species]()
objs = []
tot = 0
for k, p in parts.items():
    ob, tri = kitlib.build_part(p)
    objs.append(ob)
    print(p.name, tri)
    tot += tri
print('TOTAL', tot)
mat = preview_lib.test_material()
preview_lib.set_material(objs, mat)
cam = preview_lib.setup_scene(600, 800)
sc = bpy.context.scene
views = [('front', -25, 12), ('back34', 145, 20), ('head', -20, 8)]
for name, az, el in views:
    if name == 'head':
        preview_lib.aim_camera(cam, (0, 0, 1.4), az, el, 5.0)
        cam.data.lens = 200
    else:
        preview_lib.aim_camera(cam, (0, 0, 0.85), az, el, 5.2)
        cam.data.lens = 70
    preview_lib.render(os.path.join(out, f'dev_{species}_{name}.png'))
