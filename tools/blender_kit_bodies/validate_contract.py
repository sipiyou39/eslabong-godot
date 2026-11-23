"""Vérifie que kit_bodies.glb / kit_gear.glb contiennent exactement les noms du contrat, avec COLOR_0 + NORMAL + pivots."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_glb import info
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
c = json.load(open(os.path.join(root, 'data', 'kit_contract.json')))
want_b = {f"body_{s}_{p}" for s in c['species'] for p in c['body_parts_per_species']}
want_g = set(c['hats']) | set(c['torso_gear']) | set(c['torso_gear_skirts']) | set(c['backs'])
want_g |= {f"shoulder_{n}_{s}" for n in c['shoulders'] for s in ('l', 'r')}
pv = c['pivots']
ptp = {'torso': 'torso', 'pelvis': 'pelvis', 'head': 'head', 'arm_l': 'shoulder_l', 'arm_r': 'shoulder_r', 'leg_l': 'hip_l', 'leg_r': 'hip_r'}
for fn, want in (('kit_bodies.glb', want_b), ('kit_gear.glb', want_g)):
    js = info(os.path.join(root, 'assets/models/kit', fn))
    got = {n['name']: n for n in js['nodes']}
    print(fn, 'missing:', sorted(want - set(got)), 'extra:', sorted(set(got) - want))
    bad = 0
    for name, nd in got.items():
        at = js['meshes'][nd['mesh']]['primitives'][0]['attributes']
        if 'COLOR_0' not in at or 'NORMAL' not in at:
            bad += 1
    print('  sans COLOR_0/NORMAL:', bad)
    if fn == 'kit_bodies.glb':
        for name, nd in got.items():
            part = name.split('_', 2)[2]
            exp = pv[ptp[part]]
            t = nd.get('translation', [0, 0, 0])
            if max(abs(a - b) for a, b in zip(t, exp)) > 1e-4:
                print('  PIVOT KO', name, t, exp)
