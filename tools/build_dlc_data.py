"""Génère les données des packs (DLC) : classes + compétences au schéma d'origine.
Packs : « cosmos » (science-fiction) et « olympe » (dieux grecs). Les compétences sont construites à partir de
gabarits d'archétypes existants (mêmes paramètres que les 618 compétences d'origine), puis renommées/retintées.
Sortie : data/dlc/classes_<pack>.json, data/dlc/abilities_<pack>.json, data/dlc/packs.json
Lancer : tools/.venv/bin/python tools/build_dlc_data.py
"""
import json, os, statistics, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "dlc")
os.makedirs(OUT, exist_ok=True)
ABIL = json.load(open(os.path.join(ROOT, "data", "abilities.json")))
CLASSES = json.load(open(os.path.join(ROOT, "data", "classes.json")))


def median_template(arch, basic):
    c = [a for a in ABIL if a["arch"] == arch and bool(a["basic"]) == basic and a["folder"] not in ("Champions", "FutureClasses", "Bosses")]
    if not c:
        c = [a for a in ABIL if a["arch"] == arch and bool(a["basic"]) == basic]
    if not c:
        c = [a for a in ABIL if a["arch"] == arch]
    c.sort(key=lambda a: a.get("cd", 0))
    return copy.deepcopy(c[len(c) // 2])


ROLE_BASE = {}
for role in set(x["role"] for x in CLASSES):
    ls = [x for x in CLASSES if x["role"] == role]
    ROLE_BASE[role] = {
        "base": {k: statistics.mean(y["base"][k] for y in ls) for k in ls[0]["base"]},
        "ai": {k: statistics.mean(y["ai"].get(k, 0) for y in ls) for k in ("aggression", "preferred_range")},
    }

GLYPH_BY_ARCH = {}
for a in ABIL:
    GLYPH_BY_ARCH.setdefault(a["arch"], a["icon_glyph"])

# (nom, archétype, élément, options)
# options : status=[...], cdk (multiplicateur de recharge), dmgk, rangek, radiusk, count, kind, dur
PACKS = {
    "cosmos": {
        "name": "Pack Cosmos", "tagline": "Science-fiction", "color": "#4aa8d8",
        "desc": "Marines, androïdes et aliens : 8 nouvelles classes et 3 arènes spatiales.",
        "arenas": ["station", "alien", "reactor"],
        "classes": [
            {"key": "Sci_Marine", "name": "Marine Orbital", "role": "ranged", "element": "physical", "species": "human", "head": "helm_astronaut", "torso": "spacesuit", "shoulder": "tech", "back": "jetpack",
             "weapon_main": "blaster", "weapon_off": "", "palette": ["#d8dce6", "#3a5a8a", "#e8a030", "#e0b48f"], "scale": 1.0,
             "kit": [("Tir de blaster", "projectile", "physical", {}), ("Propulsion", "dash", "physical", {}), ("Rafale", "volley", "physical", {}), ("Grenade flash", "ground_aoe", "lightning", {"status": ["stun"]}),
                     ("Bouclier orbital", "shield", "arcane", {}), ("Frappe orbitale", "ground_aoe", "fire", {"dmgk": 1.3, "radiusk": 1.2})]},
            {"key": "Sci_Titan", "name": "Titan Mécanique", "role": "tank", "element": "physical", "species": "robot", "head": "none", "torso": "mech", "shoulder": "dome", "back": "reactor",
             "weapon_main": "gauntlet", "weapon_off": "energy_shield", "palette": ["#6a7a8c", "#2a3240", "#e8a030", "#9aa8b8"], "scale": 1.2,
             "kit": [("Poing hydraulique", "melee_arc", "physical", {}), ("Charge turbo", "charge", "physical", {}), ("Bouclier d'énergie", "shield", "arcane", {}), ("Onde de choc", "nova", "lightning", {"status": ["stun"]}),
                     ("Alarme de combat", "taunt", "physical", {}), ("Surcharge du réacteur", "buff", "fire", {})]},
            {"key": "Sci_Plasma", "name": "Sergent Plasma", "role": "bruiser", "element": "arcane", "species": "human", "head": "helm_pilot", "torso": "exo", "shoulder": "jet", "back": "none",
             "weapon_main": "energy_blade", "weapon_off": "", "palette": ["#3a4a6a", "#9a3a2a", "#4ad0e8", "#e0b48f"], "scale": 1.05,
             "kit": [("Lame plasma", "melee_arc", "arcane", {}), ("Bond propulsé", "leap", "arcane", {}), ("Estoc ionique", "melee_thrust", "lightning", {}), ("Tourbillon plasma", "melee_aoe", "arcane", {"status": ["burn"]}),
                     ("Coup fatal", "execute", "arcane", {}), ("Mode berserk", "buff", "fire", {})]},
            {"key": "Sci_Spectre", "name": "Spectre", "role": "assassin", "element": "void", "species": "alien", "head": "none", "torso": "jacket_tech", "shoulder": "none", "back": "none",
             "weapon_main": "energy_dagger", "weapon_off": "", "palette": ["#3a2a5a", "#6a3a8a", "#d060e8", "#7a8a9a"], "scale": 1.0,
             "kit": [("Entaille d'énergie", "melee_arc", "void", {}), ("Saut dimensionnel", "blink", "void", {}), ("Camouflage optique", "stealth", "void", {}), ("Frappe dans le dos", "melee_thrust", "void", {"status": ["bleed"]}),
                     ("Mine spectrale", "trap", "void", {}), ("Exécution", "execute", "void", {})]},
            {"key": "Sci_Sniper", "name": "Sniper Rail", "role": "ranged", "element": "lightning", "species": "human", "head": "helm_visor", "torso": "jacket_tech", "shoulder": "tech", "back": "none",
             "weapon_main": "railgun", "weapon_off": "", "palette": ["#4a5a3a", "#2a2a30", "#e8d040", "#d8b48f"], "scale": 1.0,
             "kit": [("Tir rail", "projectile", "lightning", {}), ("Roulade tactique", "dash", "physical", {}), ("Rayon de précision", "beam", "lightning", {}), ("Marque cible", "curse", "lightning", {"status": ["mark"]}),
                     ("Salve perforante", "volley", "lightning", {}), ("Tir de la mort", "projectile", "lightning", {"dmgk": 2.4, "cdk": 1.3})]},
            {"key": "Sci_Psion", "name": "Psion", "role": "mage", "element": "arcane", "species": "alien", "head": "none", "torso": "psi_robe", "shoulder": "none", "back": "none",
             "weapon_main": "plasma_staff", "weapon_off": "", "palette": ["#5a3a9a", "#2a1a4a", "#58e0e8", "#8ab0a8"], "scale": 1.05,
             "kit": [("Éclat psychique", "projectile", "arcane", {}), ("Téléportation", "blink", "arcane", {}), ("Implosion", "ground_aoe", "arcane", {}), ("Onde mentale", "nova", "arcane", {"status": ["silence"]}),
                     ("Distorsion", "time", "arcane", {}), ("Foudre psi", "chain", "arcane", {})]},
            {"key": "Sci_Medic", "name": "Docteur Nano", "role": "healer", "element": "nature", "species": "robot", "head": "none", "torso": "medic", "shoulder": "none", "back": "drone",
             "weapon_main": "med_gun", "weapon_off": "", "palette": ["#e8ecf0", "#3aa860", "#e84a4a", "#a8b4c0"], "scale": 0.95,
             "kit": [("Seringue laser", "projectile", "nature", {}), ("Glissade", "dash", "physical", {}), ("Nanosoin", "heal", "nature", {}), ("Brume réparatrice", "heal_aoe", "nature", {}),
                     ("Bouclier nano", "shield", "arcane", {}), ("Réanimation", "resurrect", "holy", {})]},
            {"key": "Sci_Drone", "name": "Pilote de Drones", "role": "summoner", "element": "lightning", "species": "human", "head": "helm_pilot", "torso": "jacket_tech", "shoulder": "none", "back": "drone",
             "weapon_main": "plasma_staff", "weapon_off": "controller", "palette": ["#3a6a8a", "#8a5a2a", "#58e8d8", "#e0b48f"], "scale": 1.0,
             "kit": [("Décharge de drone", "projectile", "lightning", {}), ("Pas de côté", "dash", "physical", {}), ("Tourelle laser", "summon", "lightning", {"kind": "turret", "role": "turret", "count": 1}),
                     ("Essaim de drones", "summon", "lightning", {"kind": "spirit", "role": "ranged", "count": 2}), ("Surcharge", "buff", "lightning", {}), ("Bombardement", "ground_aoe", "lightning", {"dmgk": 1.2})]},
        ],
    },
    "olympe": {
        "name": "Pack Olympe", "tagline": "Dieux grecs", "color": "#e0b84a",
        "desc": "Zeus, Athéna, Poséidon et leurs compagnons : 8 divinités et 3 arènes mythologiques.",
        "arenas": ["olympus", "underworld", "atlantis"],
        "classes": [
            {"key": "Greek_Zeus", "name": "Zeus", "role": "mage", "element": "lightning", "species": "human", "head": "hair_beard_long", "torso": "toga", "shoulder": "laurel", "back": "cape_royal",
             "weapon_main": "thunderbolt", "weapon_off": "", "palette": ["#f0ece0", "#7a3a9a", "#f0c840", "#e8c4a0"], "scale": 1.15,
             "kit": [("Éclair", "projectile", "lightning", {}), ("Course des nuées", "blink", "lightning", {}), ("Foudre en chaîne", "chain", "lightning", {}), ("Tempête divine", "ground_aoe", "lightning", {"status": ["stun"]}),
                     ("Colère de Zeus", "nova", "lightning", {}), ("Jugement", "beam", "lightning", {"dmgk": 1.3})]},
            {"key": "Greek_Athena", "name": "Athéna", "role": "tank", "element": "holy", "species": "human", "head": "helm_corinthian", "torso": "cuirass_greek", "shoulder": "gorget", "back": "aegis",
             "weapon_main": "spear_greek", "weapon_off": "shield_aegis", "palette": ["#c8a050", "#3a5a8a", "#f0e090", "#e8c4a0"], "scale": 1.05,
             "kit": [("Lance de sagesse", "melee_thrust", "holy", {}), ("Charge sacrée", "charge", "holy", {}), ("Égide", "shield", "holy", {}), ("Cri de guerre", "taunt", "physical", {}),
                     ("Chouette d'Athéna", "summon", "holy", {"kind": "spirit", "role": "ranged", "count": 1}), ("Stratégie divine", "buff", "holy", {})]},
            {"key": "Greek_Poseidon", "name": "Poséidon", "role": "bruiser", "element": "ice", "species": "human", "head": "hair_beard_long", "torso": "chiton", "shoulder": "pteruges", "back": "none",
             "weapon_main": "trident", "weapon_off": "", "palette": ["#3a8aa8", "#2a5a7a", "#e0d070", "#8ac0d0"], "scale": 1.15,
             "kit": [("Coup de trident", "melee_thrust", "ice", {}), ("Vague", "leap", "ice", {}), ("Raz-de-marée", "ground_aoe", "ice", {"status": ["slow"]}), ("Tentacule", "hook", "ice", {}),
                     ("Tremblement", "nova", "earth", {"status": ["stun"]}), ("Jet des abysses", "beam", "ice", {})]},
            {"key": "Greek_Hades", "name": "Hadès", "role": "summoner", "element": "shadow", "species": "human", "head": "helm_hades", "torso": "cult_robe", "shoulder": "none", "back": "cape_royal",
             "weapon_main": "bident", "weapon_off": "", "palette": ["#2a2a3a", "#6a2a5a", "#58e090", "#a8b0b0"], "scale": 1.1,
             "kit": [("Flamme spectrale", "projectile", "shadow", {}), ("Pas d'ombre", "blink", "shadow", {}), ("Âmes damnées", "summon", "shadow", {"kind": "skeleton", "role": "melee", "count": 3}), ("Malédiction des Enfers", "curse", "shadow", {"status": ["weaken"]}),
                     ("Aspiration d'âme", "drain", "shadow", {}), ("Porte des Enfers", "ground_aoe", "shadow", {"dmgk": 1.3})]},
            {"key": "Greek_Artemis", "name": "Artémis", "role": "ranged", "element": "nature", "species": "human", "head": "crown_moon", "torso": "chiton", "shoulder": "none", "back": "quiver_gold",
             "weapon_main": "bow_golden", "weapon_off": "", "palette": ["#e8e4d0", "#3a7a4a", "#d8e0f0", "#e8c4a0"], "scale": 1.0,
             "kit": [("Flèche d'argent", "projectile", "nature", {}), ("Bond de chasseuse", "dash", "nature", {}), ("Pluie de flèches", "volley", "nature", {}), ("Piège sylvestre", "trap", "nature", {"status": ["root"]}),
                     ("Camouflage lunaire", "stealth", "holy", {}), ("Flèche de lune", "projectile", "holy", {"dmgk": 2.2, "cdk": 1.3})]},
            {"key": "Greek_Apollo", "name": "Apollon", "role": "healer", "element": "holy", "species": "human", "head": "crown_sun", "torso": "toga", "shoulder": "laurel", "back": "sun_disk",
             "weapon_main": "bow_golden", "weapon_off": "lyre", "palette": ["#f0e8c0", "#d8a030", "#fff0a0", "#e8c4a0"], "scale": 1.05,
             "kit": [("Rayon solaire", "projectile", "holy", {}), ("Course du soleil", "blink", "holy", {}), ("Chant guérisseur", "heal", "holy", {}), ("Hymne", "heal_aoe", "holy", {}),
                     ("Inspiration", "buff", "holy", {}), ("Renaissance solaire", "resurrect", "holy", {})]},
            {"key": "Greek_Ares", "name": "Arès", "role": "bruiser", "element": "blood", "species": "human", "head": "helm_ares", "torso": "cuirass_greek", "shoulder": "spiked", "back": "none",
             "weapon_main": "kopis", "weapon_off": "shield_hoplon", "palette": ["#a83030", "#3a2a2a", "#d8a030", "#e0b090"], "scale": 1.15,
             "kit": [("Coup de kopis", "melee_arc", "blood", {}), ("Charge guerrière", "charge", "blood", {}), ("Tourbillon sanglant", "melee_aoe", "blood", {"status": ["bleed"]}), ("Fureur", "buff", "blood", {}),
                     ("Mise à mort", "execute", "blood", {}), ("Cri de guerre", "nova", "blood", {"status": ["fear"]})]},
            {"key": "Greek_Medusa", "name": "Méduse", "role": "assassin", "element": "nature", "species": "human", "head": "hair_snakes", "torso": "chiton", "shoulder": "none", "back": "tail_snake",
             "weapon_main": "caduceus", "weapon_off": "", "palette": ["#4a8a5a", "#2a4a3a", "#e8d060", "#a8c890"], "scale": 1.05,
             "kit": [("Crachat de venin", "projectile", "nature", {"status": ["poison"]}), ("Glissade", "dash", "nature", {}), ("Regard pétrifiant", "curse", "earth", {"status": ["freeze"]}), ("Souffle de serpents", "cone", "nature", {"status": ["poison"]}),
                     ("Nid de serpents", "trap", "nature", {}), ("Pétrification", "ground_aoe", "earth", {"status": ["stun"], "dmgk": 1.2})]},
        ],
    },
}


def make_ability(cls_key, folder, idx, spec):
    name, arch, elem, o = spec
    basic = idx == 0
    a = median_template(arch, basic)
    slug = "".join(ch for ch in name.lower().replace(" ", "_").replace("'", "") if ch.isalnum() or ch == "_")
    for src, dst in (("é", "e"), ("è", "e"), ("ê", "e"), ("à", "a"), ("ô", "o"), ("î", "i"), ("û", "u"), ("ç", "c"), ("ï", "i"), ("â", "a")):
        slug = slug.replace(src, dst)
    a["id"] = f"{cls_key.lower()}_{slug}"
    a["name"] = name
    a["folder"] = folder
    a["element"] = elem
    a["basic"] = basic
    a["icon_glyph"] = a.get("icon_glyph") or GLYPH_BY_ARCH.get(arch, "bolt")
    if "cd" in a:
        a["cd"] = round(float(a["cd"]) * float(o.get("cdk", 1.0)), 2)
    if "dmg" in a and a["dmg"]:
        a["dmg"] = round(float(a["dmg"]) * float(o.get("dmgk", 1.0)), 2)
    if "range" in a and o.get("rangek"):
        a["range"] = round(float(a["range"]) * float(o["rangek"]), 2)
    if "radius" in a and o.get("radiusk"):
        a["radius"] = round(float(a["radius"]) * float(o["radiusk"]), 2)
    if "status" in o:
        a["status"] = list(o["status"])
    elif not basic and arch in ("projectile", "melee_arc", "melee_thrust", "volley", "ground_aoe", "nova", "cone", "chain", "beam", "curse", "hook"):
        a["status"] = a.get("status", [])
    if arch == "summon":
        a["summon_kind"] = o.get("kind", a.get("summon_kind", "spirit"))
        a["summon_role"] = o.get("role", a.get("summon_role", "melee"))
        a["count"] = o.get("count", a.get("count", 2))
    return a


def build():
    all_packs = []
    existing_ids = {a["id"] for a in ABIL}
    for pid, P in PACKS.items():
        classes, abilities = [], []
        for c in P["classes"]:
            cid = "Merc_" + c["key"]
            kit_ids = []
            for i, spec in enumerate(c["kit"]):
                a = make_ability(c["key"], c["key"], i, spec)
                assert a["id"] not in existing_ids, a["id"]
                existing_ids.add(a["id"])
                abilities.append(a)
                kit_ids.append(a["id"])
            rb = ROLE_BASE[c["role"]]
            base = {k: round(v * (1.0 if k in ("speed",) else 1.0), 2) for k, v in rb["base"].items()}
            if c["species"] == "robot":
                base["hp"] = round(base["hp"] * 1.08, 1)
            ai = {k: round(v, 2) for k, v in rb["ai"].items()}
            classes.append({
                "id": cid, "name": c["name"], "species": c["species"], "role": c["role"], "element": c["element"],
                "weapon_main": c["weapon_main"], "weapon_off": c["weapon_off"], "head": c["head"], "torso": c["torso"], "shoulder": c["shoulder"], "back": c["back"],
                "palette": c["palette"], "scale": c["scale"], "kit": kit_ids, "mods": {}, "note": P["tagline"], "base": base, "ai": ai, "pack": pid,
                "path": "res://Data/DLC/%s.tres" % cid,
            })
        json.dump(classes, open(os.path.join(OUT, f"classes_{pid}.json"), "w"), ensure_ascii=False, indent=1)
        json.dump(abilities, open(os.path.join(OUT, f"abilities_{pid}.json"), "w"), ensure_ascii=False, indent=1)
        all_packs.append({"id": pid, "name": P["name"], "tagline": P["tagline"], "desc": P["desc"], "color": P["color"], "arenas": P["arenas"], "classes": [c["id"] for c in classes]})
        print(pid, len(classes), "classes", len(abilities), "compétences")
    json.dump(all_packs, open(os.path.join(OUT, "packs.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    build()
