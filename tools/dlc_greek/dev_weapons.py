"""Blender -b --python dev_weapons.py -- [prefixes]  -> GLB + manifeste dans le scratchpad (armes/invocations grecques seulement)."""
import sys, os, json
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import gk_paths
import bpy
import kw_build
from kitlib import reset_scene, export_glb
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
reset_scene()
objs, infos = kw_build.build_all(argv or None)
out = os.path.join(gk_paths.SP, 'dev')
os.makedirs(out, exist_ok=True)
export_glb(os.path.join(out, 'kit_greekw.glb'))
json.dump({'file': 'kit_greekw.glb', 'count': len(infos), 'pieces': infos}, open(os.path.join(out, 'kit_greekw_manifest.json'), 'w'), indent=1)
print('EXPORTED', len(infos))
