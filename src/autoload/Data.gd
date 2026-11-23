extends Node
## Catalogues de données (classes, compétences, reliques, équipes…) chargés depuis res://data/*.json

const ELEM_COLOR := {
	"fire": Color("ff6a2b"), "ice": Color("6fd6ff"), "lightning": Color("ffe14a"), "void": Color("a06bff"),
	"shadow": Color("8a5fc0"), "holy": Color("ffe9a0"), "blood": Color("e0344a"), "wind": Color("8affd8"),
	"earth": Color("b08a4a"), "arcane": Color("5aa0ff"), "nature": Color("6ad05a"), "physical": Color("d8dce6"),
}
const ELEM_NAME_FR := {
	"fire": "Feu", "ice": "Glace", "lightning": "Foudre", "void": "Vide", "shadow": "Ombre", "holy": "Sacré",
	"blood": "Sang", "wind": "Vent", "earth": "Terre", "arcane": "Arcane", "nature": "Nature", "physical": "Physique",
}
const ROLE_NAME_FR := {
	"tank": "Tank", "bruiser": "Bagarreur", "assassin": "Assassin", "ranged": "Tireur", "mage": "Mage",
	"healer": "Soigneur", "support": "Soutien", "summoner": "Invocateur",
}
const ROLE_COLOR := {
	"tank": Color("5aa0ff"), "bruiser": Color("ff8a3c"), "assassin": Color("c05aff"), "ranged": Color("7ad05a"),
	"mage": Color("5ae0ff"), "healer": Color("6aff9a"), "support": Color("ffe14a"), "summoner": Color("d08aff"),
}
const STATUS_INFO := {
	"slow": {"name": "Ralenti", "color": Color("6fd6ff"), "good": false},
	"stun": {"name": "Étourdi", "color": Color("ffe14a"), "good": false},
	"root": {"name": "Immobilisé", "color": Color("8acf5a"), "good": false},
	"fear": {"name": "Terrorisé", "color": Color("a06bff"), "good": false},
	"silence": {"name": "Réduit au silence", "color": Color("b0b0c0"), "good": false},
	"bleed": {"name": "Saignement", "color": Color("e0344a"), "good": false},
	"burn": {"name": "Brûlure", "color": Color("ff6a2b"), "good": false},
	"poison": {"name": "Poison", "color": Color("6ad05a"), "good": false},
	"freeze": {"name": "Gelé", "color": Color("bff0ff"), "good": false},
	"mark": {"name": "Marqué", "color": Color("ff9a3c"), "good": false},
	"weaken": {"name": "Affaibli", "color": Color("8a6fc0"), "good": false},
	"armor_break": {"name": "Armure brisée", "color": Color("c08a5a"), "good": false},
	"haste": {"name": "Hâte", "color": Color("8affd8"), "good": true},
	"empower": {"name": "Puissance", "color": Color("ff8a3c"), "good": true},
	"shield": {"name": "Barrière", "color": Color("9fd8ff"), "good": true},
	"regen": {"name": "Régénération", "color": Color("6aff9a"), "good": true},
	"thorns": {"name": "Épines", "color": Color("d08a5a"), "good": true},
	"lifesteal": {"name": "Vol de vie", "color": Color("ff4a6a"), "good": true},
	"invisible": {"name": "Invisible", "color": Color("c0c0e0"), "good": true},
	"invulnerable": {"name": "Invulnérable", "color": Color("fff0a0"), "good": true},
	"taunted": {"name": "Provoqué", "color": Color("ff5a3c"), "good": false},
	"armor_up": {"name": "Armure", "color": Color("b0c0d8"), "good": true},
}
const RARITY_COLOR := {
	"common": Color("b8bcc8"), "uncommon": Color("5ad05a"), "rare": Color("4a9aff"), "epic": Color("b05aff"), "legendary": Color("ffb030"),
}
const RARITY_NAME_FR := {"common": "Commune", "uncommon": "Peu commune", "rare": "Rare", "epic": "Épique", "legendary": "Légendaire"}

var abilities: Dictionary = {}
var classes: Dictionary = {}
var class_list: Array = []
var named: Dictionary = {}
var champions: Array = []
var bosses: Array = []
var specials: Array = []
var relics: Dictionary = {}
var relic_list: Array = []
var relic_names: Array = []
var teams: Array = []
var quirks: Dictionary = {}
var medals: Array = []
var staff_defs: Array = []
var facility_defs: Array = []
var arena_layout: Dictionary = {}

func _ready() -> void:
	_load_all()

func _read_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		push_warning("Data: fichier manquant " + path)
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	var txt := f.get_as_text()
	var parsed: Variant = JSON.parse_string(txt)
	return parsed

func _load_all() -> void:
	var ab: Variant = _read_json("res://data/abilities.json")
	if ab is Array:
		for a in ab:
			abilities[a["id"]] = a
	var cl: Variant = _read_json("res://data/classes.json")
	if cl is Array:
		class_list = cl
		for c in cl:
			classes[c["id"]] = c
	var nm: Variant = _read_json("res://data/named.json")
	if nm is Dictionary:
		champions = nm.get("champions", [])
		bosses = nm.get("bosses", [])
		specials = nm.get("specials", [])
		for arr in [champions, bosses, specials]:
			for n in arr:
				named[n["id"]] = n
	var rl: Variant = _read_json("res://data/relics.json")
	if rl is Dictionary:
		relic_list = rl.get("relics", [])
		relic_names = rl.get("names", [])
		for r in relic_list:
			relics[r["id"]] = r
	var meta: Variant = _read_json("res://data/meta.json")
	if meta is Dictionary:
		teams = meta.get("teams", [])
		for q in meta.get("quirks", []):
			quirks[q["id"]] = q
		medals = meta.get("medals", [])
		staff_defs = meta.get("staff", [])
		facility_defs = meta.get("facilities", [])
	var lay: Variant = _read_json("res://data/arena_layout.json")
	if lay is Dictionary:
		arena_layout = lay
	print("[Data] ", abilities.size(), " compétences, ", classes.size(), " classes, ", named.size(), " nommés, ", relics.size(), " reliques, ", teams.size(), " équipes")

func ability(id: String) -> Dictionary:
	return abilities.get(id, {})

## Renvoie un gabarit de combattant complet : classe de base + modifs nommées.
func template(id: String) -> Dictionary:
	if classes.has(id):
		var c: Dictionary = classes[id].duplicate(true)
		c["kind"] = "class"
		c["display_name"] = c["name"]
		return c
	if named.has(id):
		var n: Dictionary = named[id]
		var base: Dictionary = classes[n["base_class"]].duplicate(true)
		base["kind"] = n["kind"]
		base["named_id"] = id
		base["display_name"] = n["name"]
		base["aura"] = n["aura"]
		base["stat_mult"] = n["stat_mult"]
		base["scale"] = base["scale"] * n["scale_mult"]
		var kit: Array = base["kit"].duplicate()
		kit[kit.size() - 1] = n["signature"]
		base["kit"] = kit
		return base
	return {}

func elem_color(e: String) -> Color:
	return ELEM_COLOR.get(e, Color.WHITE)

func hex(s: String) -> Color:
	return Color(s)
