"""Rendu de développement des pièces sci-fi (matériau test à masque).
Blender -b --python dev_sf.py -- <groupe> <out_dir> [noms séparés par ,] [--base human|robot|alien] [--views a,b]
groupes: species hats torso skirts shoulders backs weapons summons"""
import sys, os, math, json
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import bpy
from sf_common import *
import kitlib, preview_lib as pl
import sf_kit

argv = sys.argv[sys.argv.index('--') + 1:]
group, out = argv[0], argv[1]
rest = argv[2:]
names = None
base = 'human'
if rest and not rest[0].startswith('--'):
    names = rest[0].split(',')
if '--base' in rest:
    base = rest[rest.index('--base') + 1]
os.makedirs(out, exist_ok=True)
kitlib.reset_scene()
mat = pl.test_material()
cam = pl.setup_scene(520, 560)
sc = bpy.context.scene

PAR = ["torso", "pelvis", "head", "arm_l", "arm_r", "leg_l", "leg_r"]


def base_parts():
    if base == 'human':
        import species
        return species.REGISTRY['human']()
    return {'robot': sf_kit.GROUPS['species'][0], 'alien': sf_kit.GROUPS['species'][1]}[base]()


VIEWS = {'hats': [(-32, 12, (0, 0, 1.45), 2.6, 85), (32, 12, (0, 0, 1.45), 2.6, 85), (150, 14, (0, 0, 1.45), 2.6, 85)],
         'torso': [(-32, 14, (0, 0, 0.95), 3.4, 85), (150, 16, (0, 0, 0.95), 3.4, 85)],
         'skirts': [(-32, 10, (0, 0, 0.62), 3.6, 85), (150, 10, (0, 0, 0.62), 3.6, 85)],
         'shoulders': [(-25, 25, (0, 0, 1.12), 3.4, 85), (150, 20, (0, 0, 1.12), 3.4, 85)],
         'backs': [(150, 14, (0, 0, 0.95), 5.0, 70), (-32, 12, (0, 0, 0.95), 5.0, 70)],
         'species': [(-28, 12, (0, 0, 0.9), 5.2, 70), (150, 18, (0, 0, 0.9), 5.2, 70), (-22, 8, (0, 0, 1.45), 5.0, 200)],
         'weapons': [(-90, 8, (0, 0, 0.0), 3.6, 70), (-35, 22, (0, 0, 0.0), 3.6, 70)],
         'summons': [(-35, 20, (0, 0, 0.6), 4.2, 70), (130, 25, (0, 0, 0.6), 4.2, 70)]}
views = VIEWS[group]

items = sf_kit.GROUPS[group]
jobs = []
imgs, labels = [], []
bobjs = []
if group not in ('species', 'weapons', 'summons'):
    bobjs = [kitlib.build_part(p)[0] for p in base_parts().values()]
    pl.set_material(bobjs, mat)
for it in items:
    parts = it() if callable(it) else it
    if isinstance(parts, dict):
        parts = list(parts.values())
    parts = parts if isinstance(parts, list) else [parts]
    if names and not any(p.name in names or p.name.rsplit('_', 1)[0] in names for p in parts) and not (group == 'species' and names and parts[0].name.split('_')[1] in names):
        continue
    objs, tri = [], 0
    for pt in parts:
        o, t = kitlib.build_part(pt)
        objs.append(o)
        tri += t
        if t > LIMIT_TRI:
            print('OVER', pt.name, t, sorted([(pc.geo.tris(), i) for i, pc in enumerate(pt.pieces)], reverse=True)[:6])
    pl.set_material(objs, mat)
    if group in ('weapons', 'summons'):
        import numpy as _np
        Vs = _np.vstack([_np.array([list(v.co) for v in o.data.vertices]) + _np.array(list(o.location)) for o in objs])
        mn, mx = Vs.min(0), Vs.max(0)
        ctr = (mn + mx) / 2
        ext = float(_np.max(mx - mn))
        ctr_game = (ctr[0], ctr[2], -ctr[1])
        views = [(-90, 6, (ctr[0], ctr[1], ctr[2]), ext * 2.6 + 0.4, 70), (-40, 24, (ctr[0], ctr[1], ctr[2]), ext * 2.6 + 0.4, 70)]
    lab = parts[0].name if group != 'species' else parts[0].name.rsplit('_', 1)[0] + '_*'
    for vi, v in enumerate(views):
        az, el, tgt, dist, lens = v
        pl.aim_camera(cam, tgt, az, el, dist)
        cam.data.lens = lens
        p = os.path.join(out, f'{group}_{lab}_{vi}.png')
        pl.render(p)
        imgs.append(p)
        labels.append(f'{lab} {tri}t' if vi == 0 else '')
    for o in objs:
        bpy.data.objects.remove(o)
    print(lab, [(p.name, tri_count(p)) for p in parts])
ncol = {'species': 3, 'weapons': 4, 'summons': 4, 'hats': 3}.get(group, 4)
json.dump([dict(images=imgs, labels=labels, cols=ncol, path=os.path.join(out, f'sheet_{group}.png'), tile=[300, 322] if group != 'hats' else [300, 300], title=group)], open(os.path.join(out, 'jobs_dev.json'), 'w'))
