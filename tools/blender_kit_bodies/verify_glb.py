import json, struct, sys
def info(path):
    d = open(path, 'rb').read()
    n = struct.unpack('<I', d[12:16])[0]
    js = json.loads(d[20:20 + n])
    return js
if __name__ == '__main__':
    js = info(sys.argv[1])
    nodes = js['nodes']
    print(len(nodes), 'nodes;', len(js['meshes']), 'meshes;', len(js['materials']), 'materials')
    bad = 0
    for nd in nodes:
        m = js['meshes'][nd['mesh']]
        at = m['primitives'][0]['attributes']
        if 'COLOR_0' not in at or 'NORMAL' not in at:
            bad += 1
            print('MISSING', nd['name'], at.keys())
    print('missing color/normal:', bad)
    for nd in nodes[:3]:
        print(nd['name'], nd.get('translation'), js['meshes'][nd['mesh']]['primitives'][0]['attributes'])
    acc = js['accessors']
    c0 = js['meshes'][nodes[0]['mesh']]['primitives'][0]['attributes']['COLOR_0']
    print('COLOR_0 accessor', acc[c0])
