"""Environnement des scripts d'arène : charge les bibliothèques de tools/blender_arenas (non modifiées) en corrigeant le ROOT
(les originaux contiennent le chemin factice /path/to/elsasko) et expose les chemins du projet."""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ARENAS = os.path.join(ROOT, 'tools', 'blender_arenas')
if ARENAS not in sys.path:
    sys.path.insert(0, ARENAS)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
TEXDIR = ROOT + '/assets/textures/arena'
OUTDIR = ROOT + '/assets/models/arenas'


def _patched(name):
    if name in sys.modules and getattr(sys.modules[name], '_sf_patched', False):
        return sys.modules[name]
    path = os.path.join(ARENAS, name + '.py')
    src = open(path).read().replace('"/path/to/elsasko"', repr(ROOT))
    mod = types.ModuleType(name)
    mod.__file__ = path
    mod._sf_patched = True
    sys.modules[name] = mod
    exec(compile(src, path, 'exec'), mod.__dict__)
    return mod


def load(*names):
    return [_patched(n) for n in names]
