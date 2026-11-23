"""Construit les objets Blender des armes / invocations grecques (kitlib 'armes' doit être le module kitlib courant)."""
import sys, os
import kw_greek
from kitlib import Model, build_object, ob_info


def build_all(only=None):
    infos, objs = [], []
    for e in kw_greek.REG:
        if only and not any(e['name'].startswith(o) for o in only):
            continue
        parts = e['fn']()
        parts = [p for q in parts for p in (q if isinstance(q, (list, tuple)) else [q])]
        m = Model(e['name'], e['accent'], e['notes'], e['ao'], kind=e['kind'])
        m.add(parts)
        ob = build_object(m)
        info = ob_info(ob)
        info.update(name=e['name'], notes=e['notes'], accent=list(e['accent']) if e['accent'] else None, views=e['views'], kind=e['kind'])
        infos.append(info)
        objs.append(ob)
        print(f"TRIS {e['name']:22s} {info['triangles']:5d} len={info['length']:.2f}", flush=True)
    return objs, infos
