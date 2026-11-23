"""Construit assets/models/kit/kit_gear.glb (chapeaux, torse, jupes, épaulières, dos) + manifeste.
   Blender -b --python build_kit_gear.py -- [groupe ...]    groupes: hats torso skirts shoulders backs"""
import sys, os, json, time, traceback
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import bpy
import kitlib, gear

ROOT = os.path.abspath(os.path.join(here, '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'models', 'kit')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
groups = argv or ['hats', 'torso', 'skirts', 'shoulders', 'backs']

kitlib.reset_scene()
objs, manifest = [], {}
for g in groups:
    t0 = time.time()
    for fn in gear.GROUPS[g]:
        try:
            parts = fn()
        except Exception:
            traceback.print_exc()
            continue
        parts = parts if isinstance(parts, list) else [parts]
        for p in parts:
            ob, tri = kitlib.build_part(p)
            objs.append(ob)
            manifest[p.name] = dict(group=g, triangles=tri, pivot=list(p.pivot), note=p.note + ("; > 2500 tri" if tri > 2500 else ""))
    kitlib.export_glb(objs, os.path.join(OUT, 'kit_gear.glb'))
    with open(os.path.join(OUT, 'kit_gear_manifest.json'), 'w') as f:
        json.dump(dict(version=1, gear=manifest, fit_hints={
            'base': 'toutes les pièces sont modélisées sur la silhouette human (tête : HUMAN, torse : human) avec ~0.05 m de marge',
            'orc': {'torso_gear': 'tel quel (carrure x1.14, marge incluse)', 'hats': 'tel quel', 'shoulders': 'tel quel'},
            'goblin': {'hats': 'scale ~1.22 autour du pivot tête (crâne x1.25)', 'torso_gear': 'tel quel (torse x0.82, flotte légèrement)'},
            'minotaur': {'hats': 'chapeaux fermés déconseillés (cornes) ; capuches/cheveux sans objet', 'torso_gear': 'tel quel (x1.15)'},
            'skeleton': {'all': 'tel quel (os fins sous les vêtements)'},
            'beast': {'hats': 'oreilles hautes : préférer hat_none/bandana', 'torso_gear': 'tel quel'},
            'demon': {'hats': 'cornes : préférer hat_none/circlet/crown', 'torso_gear': 'tel quel'}}), f, indent=1)
    print(f'[{g}] ok {time.time() - t0:.1f}s, {len(objs)} pièces')
over = [(k, v['triangles']) for k, v in manifest.items() if v['triangles'] > 2500]
print('OVER BUDGET', over)
