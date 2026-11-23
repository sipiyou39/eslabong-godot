"""Construit kit_props.glb (+ manifest). usage: Blender -b --python build_props.py [-- --only a,b]"""
import sys, os, json, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from kitlib import *
import registry

OUT = os.path.abspath(os.path.join(HERE, "..", "..", "assets", "models", "kit"))
MODULES = ["w_swords", "w_hafted", "w_polearms", "w_ranged", "w_staffs", "w_shields", "w_misc", "props_animals", "props_structs", "props_more"]
reset_scene()
for m in MODULES:
    if os.path.exists(os.path.join(HERE, m + ".py")):
        importlib.import_module(m)

only = None
if "--" in sys.argv:
    a = sys.argv[sys.argv.index("--") + 1:]
    if "--only" in a:
        only = a[a.index("--only") + 1].split(",")

META = {
    "coordinate_system": "glTF/Godot : +Y haut, +Z avant. Chaque pièce est un noeud racine à la transformation identité ; la géométrie est autour de l'origine (prise en main pour les armes, sol y=0 pour les props).",
    "vertex_color": "COLOR_0 (RGBA) : R = matériau principal (bois/cuir/tissu/pelage), G = secondaire (métal sombre/bordures/pierre), B = accent (lame brillante/or/gemme/cristal/flamme, zones émissives), 0,0,0 = base (os, paille, pages...). A = occlusion ambiante cuite (0,28..1).",
    "material": "M_Kit unique (Principled lisant l'attribut couleur). 'accent' d'une pièce = teinte suggérée pour B (aperçu seulement).",
}
pieces = []
for e in registry.REG:
    if e["kind"] != "prop":
        continue
    if only and not any(e["name"].startswith(o) for o in only):
        continue
    parts = e["fn"]()
    parts = [p for q in parts for p in (q if isinstance(q, (list, tuple)) else [q])]
    if e.get("scale"):
        parts = [p.xf(s=e["scale"]) for p in parts]
    m = Model(e["name"], e["accent"], e["notes"], e["ao"], kind="prop")
    m.add(parts)
    ob = build_object(m)
    info = ob_info(ob)
    info.update(name=e["name"], notes=e["notes"], accent=list(e["accent"]) if e["accent"] else None, views=e["views"])
    pieces.append(info)
    print(f'{e["name"]:28s} tris={info["triangles"]:5d} len={info["length"]:.2f} size={info["size"]}')
if only:
    OUT = "/tmp/eslabong_scratch/dev"
os.makedirs(OUT, exist_ok=True)
glb = os.path.join(OUT, "kit_props.glb")
export_glb(glb)
json.dump({"file": "kit_props.glb", "count": len(pieces), "meta": META, "pieces": pieces}, open(os.path.join(OUT, "kit_props_manifest.json"), "w"), indent=1, ensure_ascii=False)
print("EXPORTED", glb, len(pieces))
