"""Rendu de développement de l'équipement grec sur le corps humain.
Blender -b --python dev_gear_greek.py -- <groupe> <noms séparés par des virgules|all> [out_dir]"""
import sys, os, math, json
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import gk
import bpy
import kitlib, preview_lib as pl, species
import kg_all
argv = sys.argv[sys.argv.index('--') + 1:]
group, names = argv[0], argv[1].split(',')
out = argv[2] if len(argv) > 2 else gk.SP
os.makedirs(out, exist_ok=True)
kitlib.reset_scene()
base = species.REGISTRY['human']()
bobjs = [kitlib.build_part(p)[0] for p in base.values()]
mat = pl.test_material()
cam = pl.setup_scene(520, 560)
pl.set_material(bobjs, mat)
views = {'heads': ((-32, 12, (0, 0, 1.52), 3.3, 85), (0, 8, (0, 0, 1.52), 3.3, 85), (150, 14, (0, 0, 1.52), 3.3, 85)),
         'torso': ((-32, 14, (0, 0, 0.85), 3.9, 85), (0, 8, (0, 0, 0.85), 3.9, 85), (150, 16, (0, 0, 0.85), 3.9, 85)),
         'skirts': ((-32, 10, (0, 0, 0.62), 3.6, 85), (0, 8, (0, 0, 0.62), 3.6, 85), (150, 10, (0, 0, 0.62), 3.6, 85)),
         'shoulders': ((-25, 25, (0, 0, 1.12), 3.2, 85), (0, 10, (0, 0, 1.12), 3.2, 85), (150, 20, (0, 0, 1.12), 3.2, 85)),
         'backs': ((150, 14, (0, 0, 0.95), 5.0, 70), (115, 12, (0, 0, 0.95), 5.0, 70), (-32, 12, (0, 0, 0.95), 5.0, 70))}[group]
fns = kg_all.GROUPS[group]
if names != ['all']:
    fns = [f for f in fns if f.__name__ in names]
imgs, labels = [], []
for it in fns:
    parts = it()
    parts = parts if isinstance(parts, list) else [parts]
    if group == 'torso':
        for sf in kg_all.GROUPS.get('skirts', []):
            if sf.__name__ == it.__name__ + '_skirt':
                parts = parts + [sf()]
    objs, tri = [], 0
    for pt in parts:
        o, t = kitlib.build_part(pt)
        objs.append(o); tri += t
        print('PART', pt.name, t)
    pl.set_material(objs, mat)
    pics = []
    for vi, v in enumerate(views):
        az, el, tgt, dist, lens = v
        pl.aim_camera(cam, tgt, az, el, dist)
        cam.data.lens = lens
        p = os.path.join(out, f'g_{group}_{parts[0].name}_{vi}.png')
        pl.render(p)
        pics.append(p)
    imgs.append(pics); labels.append(f'{parts[0].name} {tri}t')
    for o in objs:
        bpy.data.objects.remove(o)
    print('TRI', parts[0].name, tri)
json.dump([dict(images=imgs, labels=labels, cols=2, path=os.path.join(out, f'sheet_{group}.png'), tile=[300 * len(views), 330], title=group)], open(os.path.join(out, 'jobs_dev.json'), 'w'))
