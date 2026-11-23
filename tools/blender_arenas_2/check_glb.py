"""Contrôle de contrat d'un GLB d'arène (python du venv) : triangles, poids des textures, torches, obstacles, éléments au-dessus du terrain.
usage : check_glb.py <id> [<id> ...]"""
import json
import math
import os
import struct
import sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAYOUT = json.load(open(ROOT + '/data/arena_layout.json'))


def sdf(x, z, hx=26.0, hz=16.0, r=5.0):
    qx = np.abs(x) - (hx - r)
    qz = np.abs(z) - (hz - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qz, 0)) + np.minimum(np.maximum(qx, qz), 0) - r


def load(path):
    d = open(path, 'rb').read()
    jl = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20 + jl])
    off = 20 + jl
    bl = struct.unpack('<I', d[off:off + 4])[0]
    binb = d[off + 8:off + 8 + bl]
    return j, binb


def accessor(j, binb, idx):
    a = j['accessors'][idx]
    bv = j['bufferViews'][a['bufferView']]
    comp = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[a['componentType']]
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = bv.get('byteStride', 0)
    item = np.dtype(comp).itemsize * n
    if stride and stride != item:
        arr = np.frombuffer(binb, dtype=np.uint8, count=a['count'] * stride, offset=start).reshape(a['count'], stride)[:, :item].copy().view(comp).reshape(a['count'], n)
    else:
        arr = np.frombuffer(binb, dtype=comp, count=a['count'] * n, offset=start).reshape(a['count'], n)
    return arr


def check(name):
    path = f'{ROOT}/assets/models/arenas/arena_{name}.glb'
    j, binb = load(path)
    size = os.path.getsize(path) / 1e6
    tris = 0
    for m in j['meshes']:
        for p in m['primitives']:
            tris += j['accessors'][p['indices']]['count'] // 3
    imgs = 0
    biggest = 0
    for im in j.get('images', []):
        bv = j['bufferViews'][im['bufferView']]
        imgs += bv['byteLength']
    for tex_i in j.get('images', []):
        pass
    print(f'== {name}: {size:.1f} Mo, {tris} triangles, {len(j["materials"])} matériaux, {len(j.get("images", []))} images ({imgs / 1e6:.1f} Mo)')
    for m in j['materials']:
        if m.get('alphaMode', 'OPAQUE') != 'OPAQUE':
            print('   alpha', m['name'], m['alphaMode'])
    nodes = {n.get('name'): n for n in j['nodes'] if 'name' in n}
    # torches
    miss = 0
    for i, t in enumerate(LAYOUT['torches']):
        n = nodes.get(f'Torch_{i + 1:02d}')
        if n is None:
            miss += 1
            continue
        tr = n.get('translation', [0, 0, 0])
        if abs(tr[0] - t['x']) > 0.01 or abs(tr[2] - t['z']) > 0.01:
            print('   torche décalée', i + 1, tr)
    print('   torches ok' if not miss else f'   torches manquantes: {miss}')
    # obstacles
    worst = []
    over = 0
    over_names = {}
    for n in j['nodes']:
        if 'mesh' not in n:
            continue
        nm = n.get('name', '')
        tr = np.array(n.get('translation', [0, 0, 0]), float)
        V = []
        for p in j['meshes'][n['mesh']]['primitives']:
            V.append(accessor(j, binb, p['attributes']['POSITION']).astype(float) + tr)
        V = np.concatenate(V)
        if nm.startswith('Obstacle_'):
            k = int(nm.split('_')[1]) - 1
            o = LAYOUT['obstacles'][k]
            low = V[V[:, 1] < 0.25]
            rad = np.hypot(low[:, 0] - o['x'], low[:, 2] - o['z']).max() if len(low) else 0.0
            ctr = (tr[0] - o['x'], tr[2] - o['z'])
            worst.append((nm, round(float(rad), 2), o['r'], round(float(V[:, 1].max()), 2), (round(ctr[0], 2), round(ctr[1], 2))))
        elif nm not in ('Ground',) and not nm.startswith(('Banner_', 'Torch_', 'Light_')):
            ins = (sdf(V[:, 0], V[:, 2]) < -0.02) & (V[:, 1] > 0.06)
            c = int(ins.sum())
            if c:
                over_names[nm] = (c, round(float(V[ins][:, 1].max()), 2))
        elif nm == 'Ground':
            print('   Ground y max', round(float(V[:, 1].max()), 3))
    for w in worst:
        flag = '' if w[1] <= w[2] + 0.06 else '  <-- DÉPASSE'
        print('   ', w, flag)
    print('   au-dessus du terrain (hors obstacles):', over_names or 'aucun')
    # Banners / Lights
    print('   noeuds:', sorted(k for k in nodes if k and k.split('_')[0] in ('Ground', 'Walls', 'Decor', 'Stands', 'Lava', 'Aurora', 'Clouds', 'Sun', 'Water', 'Rays')))


if __name__ == '__main__':
    for n in sys.argv[1:]:
        check(n)
