"""Construit assets/models/kit/kit_bodies.glb (+ manifest).  Usage :
   Blender -b --python build_kit_bodies.py -- [espèce ...]
Le GLB est réécrit après chaque espèce pour qu'une version utilisable existe en permanence."""
import sys, os, json, time, traceback
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import bpy
import kitlib, species

ROOT = os.path.abspath(os.path.join(here, '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'models', 'kit')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
wanted = argv or species.ORDER

kitlib.reset_scene()
objs, manifest = [], {}
for sp in species.ORDER:
    if sp not in wanted or sp not in species.REGISTRY:
        continue
    t0 = time.time()
    try:
        parts = species.REGISTRY[sp]()
    except Exception:
        traceback.print_exc()
        continue
    for k, p in parts.items():
        ob, tri = kitlib.build_part(p)
        objs.append(ob)
        manifest[p.name] = dict(species=sp, part=k, triangles=tri, pivot=list(p.pivot),
                                note=("> 3000 tri" if tri > 3000 else ""))
    kitlib.export_glb(objs, os.path.join(OUT, 'kit_bodies.glb'))
    print(f'[{sp}] ok {time.time() - t0:.1f}s, {len(objs)} pièces')
    with open(os.path.join(OUT, 'kit_bodies_manifest.json'), 'w') as f:
        json.dump(dict(version=1, bodies=manifest, conventions={
            'mask': 'COLOR_0 RGBA : R primaire, G secondaire, B accent, reste = peau ; A = AO cuite (0.28..1)',
            'human_default_outfit': 'pantalon = R, bottes/ceinture/bracelets = G, boucles = B, torse/bras/visage = peau',
            'pivots': 'origine de chaque noeud = pivot du contrat, géométrie en pose de repos autour du pivot',
            'species_scale_in_game': {'goblin': 0.8, 'minotaur': 1.35},
            'notes': {
                'orc': 'carrure x1.14 (torse), bras x1.22, défenses/oreilles en peau',
                'goblin': 'crâne x1.25, oreilles ~0.3 m, membres fins ; chapeaux à scaler ~1.22 autour du pivot tête',
                'minotaur': 'cornes + anneau de nez en B (accent) ; sabots fendus, poils en peau',
                'skeleton': 'tout en peau (os) ; orbites = B (accent, AO=1)',
                'beast': 'loup-garou : jambes digitigrades à griffes, fraise de poils ; pupilles B',
                'demon': 'cornes, yeux B, jambes digitigrades à sabots, pagne R'}}), f, indent=1)
