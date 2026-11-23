class_name MercLogic
extends RefCounted
## Logique des mercenaires persistants : tirages de naissance, croissance, niveaux, maîtrises, médailles, blessures, reliques.

const MAX_LEVEL := 40
const STAT_KEYS := ["hp", "mana", "sta", "dmg", "def", "spd"]
const GROWTH_STYLES := {
	"balanced": {"hp": 1.0, "mana": 1.0, "sta": 1.0, "dmg": 1.0, "def": 1.0, "spd": 1.0, "name": "Équilibré"},
	"bulwark": {"hp": 1.25, "mana": 0.9, "sta": 1.1, "dmg": 0.85, "def": 1.3, "spd": 0.9, "name": "Rempart"},
	"glass": {"hp": 0.8, "mana": 1.0, "sta": 1.0, "dmg": 1.35, "def": 0.8, "spd": 1.1, "name": "Canon de verre"},
	"swift": {"hp": 0.95, "mana": 1.0, "sta": 1.2, "dmg": 1.0, "def": 0.9, "spd": 1.4, "name": "Fulgurant"},
	"arcane": {"hp": 0.9, "mana": 1.4, "sta": 0.9, "dmg": 1.15, "def": 0.9, "spd": 1.0, "name": "Arcanique"},
}
const MASTERY_OPTIONS := [
	{"id": "hp", "name": "Vitalité", "desc": "+8% PV max", "mods": {"hp_perc": 8}},
	{"id": "dmg", "name": "Férocité", "desc": "+6% Puissance", "mods": {"atk_perc": 6}},
	{"id": "def", "name": "Cuirasse", "desc": "+8% Défense", "mods": {"def_perc": 8}},
	{"id": "mana", "name": "Érudition", "desc": "+12% Mana max", "mods": {"man_perc": 12}},
	{"id": "spd", "name": "Agilité", "desc": "+4% Vitesse", "mods": {"msp_perc": 4}},
	{"id": "cdr", "name": "Maîtrise du tempo", "desc": "-6% temps de recharge", "mods": {"cdr": 0.06}},
]

static func xp_needed(level: int) -> int:
	return int(70.0 + 38.0 * pow(float(level), 1.18))

# ----------------------------------------------------------------------------------------------
# Génération
# ----------------------------------------------------------------------------------------------
static func new_uid(rnd: RandomNumberGenerator) -> String:
	return "m%d_%d" % [Time.get_ticks_usec() % 1000000, rnd.randi() % 1000000]

static func generate(class_id: String, level: int, rnd: RandomNumberGenerator, opts: Dictionary = {}) -> Dictionary:
	var tpl := Data.template(class_id)
	var birth := {}
	var exceptional := false
	var best_roll := 0.0
	for k in STAT_KEYS:
		var v := clampf(rnd.randfn(1.0, 0.065), 0.84, 1.2)
		if opts.has("quality"):
			v = clampf(v + float(opts["quality"]), 0.84, 1.25)
		birth[k] = snappedf(v, 0.001)
		best_roll = maxf(best_roll, v)
		if v >= 1.13:
			exceptional = true
	var style_keys: Array = GROWTH_STYLES.keys()
	var style: String = String(opts.get("style", style_keys[rnd.randi() % style_keys.size()]))
	var gs: Dictionary = GROWTH_STYLES[style]
	var growth := {}
	for k in STAT_KEYS:
		growth[k] = snappedf(0.062 * float(gs[k]) * rnd.randf_range(0.9, 1.12), 0.0001)
	var shiny: bool = bool(opts.get("shiny", rnd.randf() < float(opts.get("shiny_chance", 0.02))))
	var legendary: bool = bool(opts.get("legendary", rnd.randf() < float(opts.get("legendary_chance", 0.004))))
	var quirk_ids: Array = Data.quirks.keys()
	var quirk: String = String(opts.get("quirk", quirk_ids[rnd.randi() % quirk_ids.size()] if rnd.randf() < 0.38 else ""))
	var m := {
		"uid": new_uid(rnd), "name": String(opts.get("name", NameGen.random_name(rnd))), "class_id": class_id,
		"level": 1, "xp": 0, "age": rnd.randi_range(19, 33), "birth": birth, "exceptional": exceptional, "growth": growth, "growth_style": style,
		"bonus": {"hp": 0.0, "damage": 0.0, "defense": 0.0, "move_speed": 0.0}, "pending_levels": 0, "choice": {}, "reroll_used": false,
		"mastery": [], "quirk": quirk, "relics": [], "shiny": shiny, "legendary": legendary, "ascended": false, "ascend_ability": "", "rebirth_count": 0,
		"rebirth_target": 0, "injury": {}, "injuries_sustained": 0, "form": 0, "medals": {}, "medal_equipped": [],
		"career": {"kills": 0, "assists": 0, "healing": 0.0, "res": 0, "damage": 0.0, "taken": 0.0, "wins": 0, "battles": 0, "mvp": 0, "clutch": 0},
		"tactics": MatchFactory.default_tactics(tpl, rnd), "variant": rnd.randi() % 1000, "kit_variant": [], "from_scouting": bool(opts.get("scouting", false)),
		"is_academy_filler": bool(opts.get("filler", false)), "superstar": false, "legendary_pity": 0,
	}
	m["salary"] = salary_for(m)
	var target := maxi(level, 1)
	var guard := 0
	while int(m["level"]) < target and guard < 60:
		guard += 1
		_apply_level(m, rnd)
		auto_pick_stat(m, rnd)
	return m

static func salary_for(m: Dictionary) -> int:
	var base := 14.0 + 3.1 * float(m["level"])
	if m.get("shiny", false): base *= 1.35
	if m.get("legendary", false): base *= 1.8
	if m.get("exceptional", false): base *= 1.15
	return int(base)

static func value_of(m: Dictionary) -> int:
	var lv := float(m["level"])
	var v := 260.0 + pow(lv, 1.62) * 46.0
	var r := rating(m)
	v *= 0.8 + r / 260.0
	if m.get("shiny", false): v *= 1.6
	if m.get("legendary", false): v *= 3.0
	if m.get("exceptional", false): v *= 1.25
	if m.get("superstar", false): v *= 2.2
	return int(v / 10.0) * 10

# ----------------------------------------------------------------------------------------------
# Statistiques
# ----------------------------------------------------------------------------------------------
static func lerp_hp_factor(m: Dictionary) -> float:
	return 1.0

static func stats(m: Dictionary) -> Dictionary:
	var tpl := Data.template(String(m["class_id"]))
	var b: Dictionary = tpl.get("base", {})
	var lv: float = float(int(m["level"]) - 1)
	var birth: Dictionary = m["birth"]
	var gr: Dictionary = m["growth"]
	var sm: float = float(tpl.get("stat_mult", 1.0))
	var bonus: Dictionary = m["bonus"]
	var form_mul := 1.0
	if Settings.gb("fighter_form_enabled"):
		form_mul += float(m.get("form", 0)) * 0.012
	var hp: float = float(b["hp"]) * float(birth["hp"]) * (1.0 + float(gr["hp"]) * lv) * sm * (1.0 + float(bonus["hp"]) / 100.0)
	var power: float = float(b["power"]) * float(birth["dmg"]) * (1.0 + float(gr["dmg"]) * lv) * (1.0 + (sm - 1.0) * 0.5) * (1.0 + float(bonus["damage"]) / 100.0)
	var defense: float = float(b["defense"]) * float(birth["def"]) * (1.0 + float(gr["def"]) * lv * 0.8) * (1.0 + (sm - 1.0) * 0.4) * (1.0 + float(bonus["defense"]) / 100.0)
	var speed: float = float(b["speed"]) * float(birth["spd"]) * (1.0 + float(gr["spd"]) * lv * 0.12) * (1.0 + float(bonus["move_speed"]) / 100.0)
	var mana: float = float(b["mana"]) * float(birth["mana"]) * (1.0 + float(gr["mana"]) * lv * 0.5)
	var sta: float = float(b["stamina"]) * float(birth["sta"]) * (1.0 + float(gr["sta"]) * lv * 0.4)
	var inj: Dictionary = m.get("injury", {})
	var inj_mul := 0.8 if not inj.is_empty() else 1.0
	return {"hp": hp * form_mul * inj_mul, "mana": mana, "stamina": sta, "power": power * form_mul * inj_mul, "defense": defense * form_mul,
		"mres": float(b["mres"]) * (1.0 + float(gr["def"]) * lv * 0.5), "speed": speed}

static func rating(m: Dictionary) -> float:
	var s := stats(m)
	return s["hp"] * 0.05 + s["power"] * 1.5 + s["defense"] * 0.9 + s["mres"] * 0.35 + s["speed"] * 3.5 + float(m["level"]) * 0.6

static func mods(m: Dictionary, relic_inv: Dictionary) -> Dictionary:
	var out := {}
	for rid in m.get("relics", []):
		var item: Dictionary = relic_inv.get(rid, {})
		if item.is_empty():
			continue
		var r: Dictionary = Data.relics.get(String(item["rid"]), {})
		if r.is_empty():
			continue
		var v: float = float(r["value"]) * float(item.get("roll", 1.0))
		out[r["effect"]] = float(out.get(r["effect"], 0.0)) + v
	var q: String = String(m.get("quirk", ""))
	if q != "" and Data.quirks.has(q):
		for k in Data.quirks[q]["mods"]:
			out[k] = float(out.get(k, 0.0)) + float(Data.quirks[q]["mods"][k])
	for mid in m.get("mastery", []):
		for opt in MASTERY_OPTIONS:
			if opt["id"] == mid:
				for k in opt["mods"]:
					out[k] = float(out.get(k, 0.0)) + float(opt["mods"][k])
	for md in m.get("medal_equipped", []):
		var tier: int = int(m.get("medals", {}).get(md, 0))
		if tier > 0:
			match md:
				"iron_wall": out["def_perc"] = float(out.get("def_perc", 0.0)) + 2.0 * tier
				"wrecking_hand": out["atk_perc"] = float(out.get("atk_perc", 0.0)) + 2.0 * tier
				"clutch_player": out["msp_perc"] = float(out.get("msp_perc", 0.0)) + 3.0
				"lifesaver": out["healing_done_perc"] = float(out.get("healing_done_perc", 0.0)) + 6.0
	return out

static func tpl_for(m: Dictionary) -> Dictionary:
	var tpl := Data.template(String(m["class_id"]))
	if m.get("ascended", false) and String(m.get("ascend_ability", "")) != "":
		var kit: Array = tpl["kit"].duplicate()
		kit[kit.size() - 1] = m["ascend_ability"]
		tpl["kit"] = kit
	return tpl

static func combatant_spec(m: Dictionary, relic_inv: Dictionary) -> Dictionary:
	var tpl := tpl_for(m)
	var md := mods(m, relic_inv)
	var spec := {"name": m["name"], "uid": m["uid"], "template_id": m["class_id"], "tpl": tpl, "level": m["level"], "stats": stats(m), "mods": md,
		"tactics": m["tactics"], "shiny": m["shiny"], "legendary": m["legendary"], "variant": m["variant"], "kit": tpl["kit"],
		"cdr": float(md.get("cdr", 0.0)), "merc": m}
	return spec

# ----------------------------------------------------------------------------------------------
# Progression
# ----------------------------------------------------------------------------------------------
static func _apply_level(m: Dictionary, rnd: RandomNumberGenerator) -> void:
	m["level"] = int(m["level"]) + 1
	m["pending_levels"] = int(m["pending_levels"]) + 1
	m["salary"] = salary_for(m)

static func roll_choices(m: Dictionary, rnd: RandomNumberGenerator) -> Array:
	var kinds := ["hp", "damage", "defense", "move_speed"]
	var out: Array = []
	var pool := kinds.duplicate()
	pool.shuffle()
	for i in 3:
		var k: String = pool[i]
		var lo := 3.0
		var hi := 7.0
		match k:
			"hp": lo = 4.0; hi = 9.0
			"damage": lo = 3.0; hi = 6.5
			"defense": lo = 3.5; hi = 8.0
			"move_speed": lo = 1.5; hi = 3.5
		if m.get("exceptional", false):
			hi *= 1.15
		out.append({"stat": k, "value": snappedf(rnd.randf_range(lo, hi), 0.1)})
	return out

static func auto_pick_stat(m: Dictionary, rnd: RandomNumberGenerator) -> void:
	while int(m["pending_levels"]) > 0:
		var ch := roll_choices(m, rnd)
		# l'auto-pick favorise la stat dominante de la classe
		var role: String = String(Data.template(String(m["class_id"])).get("role", "bruiser"))
		var prefer: String = {"tank": "hp", "bruiser": "damage", "assassin": "damage", "ranged": "damage", "mage": "damage", "healer": "hp", "support": "hp", "summoner": "damage"}[role]
		var pick: Dictionary = ch[0]
		for c in ch:
			if c["stat"] == prefer:
				pick = c
		apply_choice(m, pick)

static func apply_choice(m: Dictionary, c: Dictionary) -> void:
	var b: Dictionary = m["bonus"]
	b[c["stat"]] = float(b[c["stat"]]) + float(c["value"])
	m["pending_levels"] = maxi(int(m["pending_levels"]) - 1, 0)
	m["choice"] = {}
	m["reroll_used"] = false

static func add_xp(m: Dictionary, amount: int, rnd: RandomNumberGenerator, xp_mult: float = 1.0) -> int:
	if int(m["level"]) >= MAX_LEVEL:
		return 0
	var mult := xp_mult
	if int(m.get("rebirth_target", 0)) > int(m["level"]):
		mult *= 2.0
	var gain := int(amount * mult)
	m["xp"] = int(m["xp"]) + gain
	var levels := 0
	while int(m["level"]) < MAX_LEVEL and int(m["xp"]) >= xp_needed(int(m["level"])):
		m["xp"] = int(m["xp"]) - xp_needed(int(m["level"]))
		_apply_level(m, rnd)
		levels += 1
		var lv: int = int(m["level"])
		if (lv == 10 and m["mastery"].size() < 1) or (lv == 20 and m["mastery"].size() < 2):
			m["pending_mastery"] = true
	return levels

static func is_available(m: Dictionary) -> bool:
	return (m.get("injury", {}) as Dictionary).is_empty()

static func roll_injury(m: Dictionary, rnd: RandomNumberGenerator, risk_mult: float) -> bool:
	if not Settings.gb("injuries_enabled"):
		return false
	if not m.get("injury", {}).is_empty():
		return false
	if rnd.randf() < 0.16 * risk_mult:
		var n := rnd.randi_range(1, 4)
		var names := ["Entorse", "Fracture", "Commotion", "Brûlure profonde", "Déchirure", "Côtes fêlées"]
		m["injury"] = {"battles": n, "desc": names[rnd.randi() % names.size()]}
		m["injuries_sustained"] = int(m["injuries_sustained"]) + 1
		return true
	return false

static func tick_injury(m: Dictionary) -> void:
	var inj: Dictionary = m.get("injury", {})
	if inj.is_empty():
		return
	inj["battles"] = int(inj["battles"]) - 1
	if int(inj["battles"]) <= 0:
		m["injury"] = {}

static func update_medals(m: Dictionary) -> Array:
	var c: Dictionary = m["career"]
	var gained: Array = []
	var meds: Dictionary = m["medals"]
	var checks := {
		"iron_wall": [float(c["taken"]), [6000.0, 25000.0, 80000.0]],
		"wrecking_hand": [float(c["damage"]), [9000.0, 34000.0, 100000.0]],
		"clutch_player": [float(c["clutch"]), [1.0]],
		"lifesaver": [float(c["healing"]) + float(c["res"]) * 600.0, [3500.0]],
	}
	for k in checks:
		var val: float = checks[k][0]
		var th: Array = checks[k][1]
		var tier := 0
		for i in th.size():
			if val >= float(th[i]):
				tier = i + 1
		if tier > int(meds.get(k, 0)):
			meds[k] = tier
			gained.append({"medal": k, "tier": tier})
			if (m["medal_equipped"] as Array).size() < 2 and not (k in m["medal_equipped"]):
				m["medal_equipped"].append(k)
	return gained

static func relic_slots(m: Dictionary) -> int:
	return 2 if int(m["level"]) >= 5 or m.get("legendary", false) or m.get("ascended", false) else 1

static func rebirth(m: Dictionary, rnd: RandomNumberGenerator) -> void:
	var target := int(float(m["level"]) * 0.7)
	m["rebirth_count"] = int(m["rebirth_count"]) + 1
	m["rebirth_target"] = target
	m["level"] = 1
	m["xp"] = 0
	m["pending_levels"] = 0
	var b: Dictionary = m["bonus"]
	for k in b:
		b[k] = float(b[k]) * 0.35
	m["age"] = maxi(int(m["age"]) - 8, 18)
	m["ascended"] = false
	m["ascend_ability"] = ""
	for k in STAT_KEYS:
		m["growth"][k] = float(m["growth"][k]) * 1.06
	m["salary"] = salary_for(m)

static func ascension_options(m: Dictionary, rnd: RandomNumberGenerator) -> Array:
	var own := Data.template(String(m["class_id"]))
	var pool: Array = []
	var role: String = String(own.get("role", "bruiser"))
	for c in Data.class_list:
		if c["id"] != m["class_id"]:
			var ab_id: String = c["kit"][c["kit"].size() - 1 - rnd.randi() % 3]
			var ab: Dictionary = Data.ability(ab_id)
			if not ab.is_empty() and not ab.get("basic", false) and String(ab["arch"]) != "dash":
				pool.append(ab_id)
	pool.shuffle()
	return pool.slice(0, 3)

static func describe_stats(m: Dictionary) -> Array:
	var s := stats(m)
	return [["hp", "PV", int(s["hp"])], ["power", "Puissance", int(s["power"])], ["defense", "Défense", int(s["defense"])], ["mres", "Rés. magique", int(s["mres"])],
		["speed", "Vitesse", snappedf(s["speed"], 0.1)], ["mana", "Mana", int(s["mana"])], ["stamina", "Endurance", int(s["stamina"])]]

static func star_rating(m: Dictionary) -> int:
	var avg := 0.0
	for k in STAT_KEYS:
		avg += float(m["birth"][k])
	avg /= STAT_KEYS.size()
	return clampi(int(round((avg - 0.92) / 0.05)) + 2, 1, 5)
