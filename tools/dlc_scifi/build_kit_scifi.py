"""Construit assets/models/kit/kit_scifi.glb (+ data/dlc/kit_scifi_parts.json).
   Blender -b --python build_kit_scifi.py -- [groupe ...]    groupes: species hats torso skirts shoulders backs weapons summons"""
import sys, os, json, time, traceback
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import bpy
from sf_common import *
import kitlib
import sf_kit

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
groups = argv or ['species', 'hats', 'torso', 'skirts', 'shoulders', 'backs', 'weapons', 'summons']
OUT = os.path.join(KIT_DIR, 'kit_scifi.glb')

kitlib.reset_scene()
objs, tris = [], {}
for g in groups:
    t0 = time.time()
    for fn in sf_kit.GROUPS[g]:
        try:
            parts = fn()
        except Exception:
            traceback.print_exc()
            continue
        if isinstance(parts, dict):
            parts = list(parts.values())
        parts = parts if isinstance(parts, list) else [parts]
        for p in parts:
            ob, tri = kitlib.build_part(p)
            objs.append(ob)
            tris[p.name] = tri
            if tri > LIMIT_TRI:
                print('OVER', p.name, tri)
    kitlib.export_glb(objs, OUT)
    print(f'[{g}] ok {time.time() - t0:.1f}s, {len(objs)} pièces')
os.makedirs(DATA_DIR, exist_ok=True)
names = [o.name for o in objs]
json.dump({"species": ["robot", "alien"], "parts": names, "triangles": tris,
           "notes": {"alien": "tête allongée (haut du crâne à y=1.90) : les couvre-chefs sont modélisés pour le crâne humain, à scaler ~(1.12, 1.18, 1.12) autour du pivot tête pour l'alien",
                     "mask": "COLOR_0 : R primaire, G secondaire (cheveux), B accent/lueur, reste = peau/chassis, A = AO",
                     "helm_astronaut": "dôme (accent B) dégagé sur le visage : le shader du jeu n'écrit pas d'alpha",
                     "pairs": "wpn_energy_dagger_l/_r, wpn_gauntlet_l/_r (gauche = +X)",
                     "controller": "dos vers -Z, face (hologramme) vers +Z, centré",
                     "summons": "summon_drone centré à y=0.65 ; summon_turret_laser posée au sol, canons vers +Z"}},
          open(os.path.join(DATA_DIR, 'kit_scifi_parts.json'), 'w'), indent=1, ensure_ascii=False)
print('OVER BUDGET', [(k, v) for k, v in tris.items() if v > LIMIT_TRI])
print('TOTAL', len(names), 'pièces')
