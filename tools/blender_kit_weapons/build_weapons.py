"""Construit kit_weapons.glb (+ manifest). usage: Blender -b --python build_weapons.py [-- --only a,b]"""
import sys, os, json, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from kitlib import *
import registry

OUT = os.path.abspath(os.path.join(HERE, "..", "..", "assets", "models", "kit"))
MODULES = ["w_swords", "w_hafted", "w_polearms", "w_ranged", "w_staffs", "w_shields", "w_misc"]
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
    if e["kind"] != "weapon":
        continue
    if only and not any(e["name"].startswith(o) for o in only):
        continue
    parts = e["fn"]()
    parts = [p for q in parts for p in (q if isinstance(q, (list, tuple)) else [q])]
    if e.get("scale"):
        parts = [p.xf(s=e["scale"]) for p in parts]
    variants = [(e["name"], parts)]
    if e["pair"]:
        variants = [(e["name"] + "_l", parts), (e["name"] + "_r", [p.mx() for p in parts])]
    for name, ps in variants:
        m = Model(name, e["accent"], e["notes"], e["ao"])
        m.add(ps)
        ob = build_object(m)
        info = ob_info(ob)
        vw = e["views"]
        if vw == "side,tq" and info["length"] > 1.3:
            vw = "side,tq@top"
        info.update(name=name, notes=e["notes"], accent=list(e["accent"]) if e["accent"] else None, views=vw)
        pieces.append(info)
        print(f'{name:24s} tris={info["triangles"]:5d} len={info["length"]:.2f} size={info["size"]}')
if only:   # mode dev : ne touche pas aux livrables
    OUT = "/tmp/eslabong_scratch/dev"
os.makedirs(OUT, exist_ok=True)
glb = os.path.join(OUT, "kit_weapons.glb")
export_glb(glb)
json.dump({"file": "kit_weapons.glb", "count": len(pieces), "meta": META, "pieces": pieces}, open(os.path.join(OUT, "kit_weapons_manifest.json"), "w"), indent=1, ensure_ascii=False)
print("EXPORTED", glb, len(pieces))
