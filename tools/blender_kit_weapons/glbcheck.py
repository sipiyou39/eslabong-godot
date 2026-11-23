"""Relit un GLB : liste nodes, attributs (COLOR_0 ...), triangles, bbox, vérifie masque. usage: python glbcheck.py fichier.glb"""
import sys, json, struct
import numpy as np
f = open(sys.argv[1], 'rb').read()
magic, ver, ln = struct.unpack('<III', f[:12])
off = 12
js = None; bin_ = None
while off < ln:
    cl, ct = struct.unpack('<II', f[off:off+8]); data = f[off+8:off+8+cl]; off += 8 + cl
    if ct == 0x4E4F534A: js = json.loads(data)
    elif ct == 0x004E4942: bin_ = data
def acc(i):
    a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
    n = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    dt = {5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}[a['componentType']]
    base = bv.get('byteOffset',0)+a.get('byteOffset',0)
    stride = bv.get('byteStride') 
    arr = np.frombuffer(bin_, dtype=dt, count=a['count']*n, offset=base).reshape(a['count'], n)
    if a.get('normalized'): arr = arr.astype(np.float32)/np.iinfo(dt).max
    return arr
print('materials', [m['name'] for m in js.get('materials',[])], 'nodes', len(js['nodes']), 'meshes', len(js['meshes']))
bad = 0
rows = []
for nd in js['nodes']:
    if 'mesh' not in nd: continue
    m = js['meshes'][nd['mesh']]
    tris = 0; msg = ''
    for pr in m['primitives']:
        at = pr['attributes']
        tris += js['accessors'][pr['indices']]['count'] // 3
        if 'COLOR_0' not in at: msg += ' NO COLOR_0'; bad += 1; continue
        c = acc(at['COLOR_0'])
        P = acc(at['POSITION'])
        msg += f" col={c.shape[1]}c R{c[:,0].mean():.2f} G{c[:,1].mean():.2f} B{c[:,2].mean():.2f} A[{c[:,3].min():.2f}-{c[:,3].max():.2f}]" if c.shape[1] == 4 else f' col={c.shape[1]}'
        msg += f" n={'NORMAL' in at} verts={len(P)} y[{P[:,1].min():.2f},{P[:,1].max():.2f}]"
    t = nd.get('translation'); 
    rows.append(f"{nd['name']:28s} tris={tris:5d} {'T='+str(t) if t else ''}{msg}")
print('\n'.join(rows[:int(sys.argv[2]) if len(sys.argv)>2 else 8]))
print('missing COLOR_0:', bad, ' total nodes with mesh:', len(rows))
