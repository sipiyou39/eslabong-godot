class_name MatchFactory
extends RefCounted
## Fabrique d'équipes de combat (aléatoires, de test, etc.)

const ROLE_PLAN := [["tank", "bruiser"], ["bruiser", "assassin"], ["healer", "support"], ["ranged", "mage"], ["mage", "ranged", "summoner"]]

static func classes_by_role(role: String) -> Array:
	var out: Array = []
	for c in Data.class_list:
		if c["role"] == role:
			out.append(c)
	return out

static func random_spec(class_id: String, level: int, rnd: RandomNumberGenerator, name: String = "") -> Dictionary:
	var tpl := Data.template(class_id)
	var nm := name if name != "" else NameGen.random_name(rnd)
	return {"name": nm, "template_id": class_id, "tpl": tpl, "level": level, "uid": "f%d" % rnd.randi(), "tactics": default_tactics(tpl, rnd)}

static func default_tactics(tpl: Dictionary, rnd: RandomNumberGenerator) -> Dictionary:
	var role: String = String(tpl.get("role", "bruiser"))
	var ai: Dictionary = tpl.get("ai", {})
	return {
		"aggression": clampf(float(ai.get("aggression", 0.6)) + rnd.randf_range(-0.1, 0.1), 0.05, 1.0),
		"aim": rnd.randf_range(0.6, 0.95), "reflexes": rnd.randf_range(0.4, 0.85),
		"defense_style": "kite" if role in ["ranged", "mage", "healer", "summoner"] else "balanced",
		"target_priority": ["nearest", "lowest_health", "high_threat"][rnd.randi() % 3],
		"ability_usage": 0.85, "aoe_efficiency": 2, "cohesion": 0.5, "distance": 1.0, "friendly_fire_avoid": true,
	}

static func random_team(team_name: String, n: int, level: int, rnd: RandomNumberGenerator, lean: String = "balanced") -> Dictionary:
	var fighters: Array = []
	var plan: Array = []
	for i in n:
		plan.append(ROLE_PLAN[i % ROLE_PLAN.size()])
	for roles in plan:
		var role: String = roles[rnd.randi() % roles.size()]
		if lean != "balanced" and rnd.randf() < 0.3:
			role = lean
		var pool := classes_by_role(role)
		if pool.is_empty():
			pool = Data.class_list
		var c: Dictionary = pool[rnd.randi() % pool.size()]
		fighters.append(random_spec(c["id"], level + rnd.randi_range(-1, 1), rnd))
	return {"name": team_name, "fighters": fighters}

static func config_for(teams: Array, arena: String = "colosseum", extra: Dictionary = {}) -> Dictionary:
	var c := {"teams": teams, "arena": arena, "rounds_to_win": 2, "player_team": 0, "allow_control": true, "mode": "quick"}
	c.merge(extra, true)
	return c
