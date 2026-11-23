"""Construit assets/models/kit/kit_greek.glb (équipement grec + armes + invocations) et data/dlc/kit_greek_parts.json.
   Blender -b --python build_kit_greek.py [-- --out <dossier>]
Deux bibliothèques 'kitlib' coexistent (corps/équipement, puis armes) : la seconde est importée après purge des modules."""
import sys, os, json, time, traceback
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import gk_paths
ROOT = gk_paths.ROOT
BODIES = os.path.join(ROOT, 'tools', 'blender_kit_bodies')
WEAPONS = os.path.join(ROOT, 'tools', 'blender_kit_weapons')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = os.path.join(ROOT, 'assets', 'models', 'kit')
if '--out' in argv:
    OUT = argv[argv.index('--out') + 1]
os.makedirs(OUT, exist_ok=True)

import bpy

# ---------------------------------------------------------------- phase 1 : équipement (kitlib corps)
sys.path.insert(0, BODIES)
import gk
import kitlib
import kg_all
kitlib.reset_scene()
objs, tris, groups = [], {}, {}
t0 = time.time()
ORDER = ['heads', 'torso', 'skirts', 'shoulders', 'backs']
for g in ORDER:
    for fn in kg_all.GROUPS.get(g, []):
        try:
            parts = fn()
        except Exception:
            traceback.print_exc()
            continue
        parts = parts if isinstance(parts, list) else [parts]
        for p in parts:
            ob, tri = kitlib.build_part(p)
            objs.append(ob)
            tris[p.name] = tri
            groups[p.name] = g
            print(f'TRIS {p.name:26s} {tri:5d}', flush=True)
print(f'[gear] {len(objs)} pièces {time.time() - t0:.1f}s')

# ---------------------------------------------------------------- phase 2 : armes + invocations (kitlib armes)
for m in list(sys.modules):
    if m in ('kitlib', 'bodies_common', 'gear_common', 'heads', 'gk', 'kg_all', 'kg_heads', 'kg_torso', 'kg_shoulders', 'kg_backs', 'gear_hats', 'gear_torso',
             'gear_shoulders', 'gear_backs'):
        del sys.modules[m]
sys.path.remove(BODIES)
sys.path.insert(0, WEAPONS)
import kw_build
import kw_greek
t0 = time.time()
wobjs, winfos = kw_build.build_all()
for i in winfos:
    tris[i['name']] = i['triangles']
    groups[i['name']] = 'summons' if i['kind'] == 'prop' else 'weapons'
print(f'[weapons] {len(wobjs)} pièces {time.time() - t0:.1f}s')

# ---------------------------------------------------------------- export
bpy.ops.object.select_all(action='DESELECT')
glb = os.path.join(OUT, 'kit_greek.glb')
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=False, export_yup=True, export_vertex_color='ACTIVE',
                          export_all_vertex_colors=False, export_materials='EXPORT', export_texcoords=False, export_cameras=False, export_lights=False,
                          export_apply=False, export_normals=True, export_tangents=False, export_extras=False, export_animations=False)
print('EXPORTED', glb, os.path.getsize(glb) // 1024, 'Ko')
names = [o.name for o in objs] + [o.name for o in wobjs]
over = {k: v for k, v in tris.items() if v > 1500}
print('OVER 1500 :', over)
info = {i['name']: i for i in winfos}
parts_json = {'parts': names, 'triangles': {n: tris[n] for n in names}}
dlc = os.path.join(ROOT, 'data', 'dlc')
os.makedirs(dlc, exist_ok=True)
if OUT == os.path.join(ROOT, 'assets', 'models', 'kit'):
    json.dump(parts_json, open(os.path.join(dlc, 'kit_greek_parts.json'), 'w'), indent=1)
manifest = {'file': 'kit_greek.glb', 'count': len(names), 'groups': groups,
            'pieces': [dict(name=n, triangles=tris[n], group=groups[n], **({k: info[n][k] for k in ('length', 'size', 'views', 'accent', 'notes')} if n in info else {})) for n in names]}
json.dump(manifest, open(os.path.join(gk_paths.SP, 'kit_greek_manifest.json'), 'w'), indent=1)
