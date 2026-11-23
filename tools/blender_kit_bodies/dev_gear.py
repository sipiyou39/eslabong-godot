"""Rendu de développement de l'équipement sur le corps humain.
Blender -b --python dev_gear.py -- <groupe> <i0> <i1> [out_dir]   groupe: hats|torso|skirts|shoulders|backs"""
import sys, os, math, json
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import bpy
import kitlib, preview_lib as pl, species
argv = sys.argv[sys.argv.index('--') + 1:]
group, i0, i1 = argv[0], int(argv[1]), int(argv[2])
out = argv[3] if len(argv) > 3 else '/tmp'
kitlib.reset_scene()
base = species.REGISTRY[argv[4] if len(argv) > 4 else 'human']()
bobjs = [kitlib.build_part(p)[0] for p in base.values()]
import gear
items = gear.GROUPS[group][i0:i1]
mat = pl.test_material()
cam = pl.setup_scene(520, 560)
sc = bpy.context.scene
pl.set_material(bobjs, mat)
views = {'hats': [((-32, 12, (0, 0, 1.42), 2.7, 85), (150, 14, (0, 0, 1.42), 2.7, 85))],
         'torso': [((-32, 14, (0, 0, 0.95), 3.4, 85), (150, 16, (0, 0, 0.95), 3.4, 85))],
         'skirts': [((-32, 10, (0, 0, 0.62), 3.6, 85), (150, 10, (0, 0, 0.62), 3.6, 85))],
         'shoulders': [((-25, 25, (0, 0, 1.12), 3.4, 85), (150, 20, (0, 0, 1.12), 3.4, 85))],
         'backs': [((150, 14, (0, 0, 0.95), 5.0, 70), (-32, 12, (0, 0, 0.95), 5.0, 70))]}[group][0]
imgs, labels = [], []
for it in items:
    parts = it() if callable(it) else it
    parts = parts if isinstance(parts, list) else [parts]
    objs = []
    tri = 0
    for pt in parts:
        o, t = kitlib.build_part(pt)
        objs.append(o); tri += t
    pl.set_material(objs, mat)
    for vi, v in enumerate(views):
        az, el, tgt, dist, lens = v
        pl.aim_camera(cam, tgt, az, el, dist)
        cam.data.lens = lens
        p = os.path.join(out, f'g_{group}_{parts[0].name}_{vi}.png')
        pl.render(p)
        imgs.append(p); labels.append(f'{parts[0].name} {tri}t' if vi == 0 else '')
    for o in objs:
        bpy.data.objects.remove(o)
    print(parts[0].name, tri)
json.dump([dict(images=imgs, labels=labels, cols=4, path=os.path.join(out, f'sheet_{group}_{i0}.png'), tile=[300, 322], title=group)], open(os.path.join(out, f'jobs_dev.json'), 'w'))
