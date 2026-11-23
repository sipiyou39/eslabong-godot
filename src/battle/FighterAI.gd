class_name FighterAI
extends RefCounted
## IA tactique d'un combattant : choix de cible, déplacement par rôle, utilisation des compétences, esquive des zones.

var f: Fighter
var think_t: float = 0.0
var target: Fighter = null
var ally_target: Fighter = null
var goal: Vector3 = Vector3.ZERO
var strafe: float = 1.0
var strafe_t: float = 0.0
var plan: Dictionary = {}
var dodge_t: float = 0.0
var last_target_swap: float = 0.0
var retreating: bool = false
var rnd := RandomNumberGenerator.new()
var intent: String = ""

func _init() -> void:
	rnd.randomize()

func tac(key: String, default: Variant) -> Variant:
	return f.tactics.get(key, default)

func role() -> String:
	return String(f.tpl.get("role", "bruiser"))

func pref_range() -> float:
	var r: float = float(f.tpl.get("ai", {}).get("preferred_range", 3.0))
	if f.is_summon:
		match f.summon_role:
			"ranged": r = 10.0
			"healer": r = 9.0
			"turret": r = 0.0
	return r * float(tac("distance", 1.0))

func aggression() -> float:
	return float(tac("aggression", f.tpl.get("ai", {}).get("aggression", 0.6)))

func is_melee() -> bool:
	return pref_range() <= 4.5

func update(dt: float) -> void:
	think_t -= dt
	strafe_t -= dt
	if strafe_t <= 0.0:
		strafe_t = rnd.randf_range(0.9, 2.2)
		strafe = -strafe if rnd.randf() < 0.55 else strafe
	if think_t <= 0.0:
		var refl: float = float(tac("reflexes", 0.6))
		think_t = lerpf(0.30, 0.08, refl) + rnd.randf() * 0.05
		_think()
	_act(dt)

# ----------------------------------------------------------------------------------------------
func _enemies() -> Array[Fighter]:
	var out: Array[Fighter] = []
	for o in f.battle.fighters:
		if o.alive and o.team != f.team:
			out.append(o)
	return out

func _allies() -> Array[Fighter]:
	var out: Array[Fighter] = []
	for o in f.battle.fighters:
		if o.alive and o.team == f.team and o != f:
			out.append(o)
	return out

func _dist(o: Fighter) -> float:
	return Abilities.flat(o.global_position - f.global_position).length()

func _pick_target() -> Fighter:
	var enemies := _enemies()
	if enemies.is_empty():
		return null
	if f.has_status("taunted"):
		var src: Variant = f.statuses["taunted"]["src"]
		if src != null and is_instance_valid(src) and src.alive:
			return src
	var prio := String(tac("target_priority", "nearest"))
	var best: Fighter = null
	var best_s := -1e9
	for e in enemies:
		if e.has_status("invisible") and _dist(e) > 3.5:
			continue
		var d := _dist(e)
		var s := 0.0
		match prio:
			"lowest_health":
				s = -e.hp - d * 4.0
			"high_threat":
				var threat := e.power * (1.4 if e.tpl.get("role", "") in ["mage", "ranged", "assassin"] else 1.0)
				s = threat * 3.0 - d * 6.0 - e.hp * 0.05
			_:
				s = -d
		if e == target and target.alive:
			s += 12.0 if prio == "nearest" else 40.0
		if e.has_status("mark"):
			s += 25.0
		# les soigneurs sont des cibles prioritaires pour les assassins
		if role() == "assassin" and e.tpl.get("role", "") in ["healer", "mage", "ranged"]:
			s += 35.0
		if s > best_s:
			best_s = s
			best = e
	return best

func _pick_ally() -> Fighter:
	var best: Fighter = null
	var bs := 2.0
	var pool: Array[Fighter] = _allies()
	pool.append(f)
	for a in pool:
		var p: float = a.hp_pct()
		if p < bs:
			bs = p
			best = a
	return best

func _think() -> void:
	target = _pick_target()
	ally_target = _pick_ally()
	plan = {}
	goal = f.global_position
	intent = "idle"
	if f.kit.is_empty():
		return
	if f.base_speed <= 0.1:
		# tourelle / totem : tire seulement
		_choose_cast()
		return
	var pos := f.global_position
	var r_pref := pref_range()
	var enemies := _enemies()
	# 1. esquive des zones dangereuses
	var danger := _zone_danger()
	if danger != Vector3.ZERO and rnd.randf() < float(tac("reflexes", 0.6)) + 0.25:
		goal = pos + danger * 5.0
		intent = "dodge"
		_choose_cast()
		return
	# 2. mouvement par rôle
	var rl := role()
	if rl in ["healer", "support"] and not f.is_summon or (f.is_summon and f.summon_role == "healer"):
		var hurt: Fighter = null
		var hs := 0.75
		for a in _allies():
			if a.hp_pct() < hs and a.alive:
				hs = a.hp_pct()
				hurt = a
		var ctr := _centroid(_allies())
		if hurt and _dist(hurt) > 8.0:
			goal = hurt.global_position
			intent = "to_ally"
		elif enemies.size() > 0:
			var ne := _nearest(enemies)
			var away := Abilities.dir_to(ne.global_position, pos)
			var keep := r_pref
			if _dist(ne) < keep - 2.0:
				goal = pos + away * 5.0
				intent = "keep_away"
			elif ctr != Vector3.ZERO and Abilities.flat(ctr - pos).length() > 8.0 * (1.0 + (1.0 - float(tac("cohesion", 0.5)))):
				goal = ctr
				intent = "regroup"
			else:
				goal = pos + Abilities.dir_to(pos, ctr) * 0.0
		_choose_cast()
		return
	if target == null:
		_choose_cast()
		return
	var d := _dist(target)
	var tp := target.global_position
	if is_melee():
		var reach := _basic_reach() * 0.8
		var engage := aggression()
		var low_hp := f.hp_pct() < 0.28 and String(tac("defense_style", "balanced")) == "kite"
		if low_hp:
			goal = pos + Abilities.dir_to(tp, pos) * 6.0
			intent = "retreat"
		elif d > reach:
			goal = tp
			intent = "chase"
		else:
			# tourne autour de la cible
			var perp := Vector3(-(tp - pos).z, 0, (tp - pos).x).normalized() * strafe
			goal = pos + perp * 2.0
			intent = "circle"
		# assassins : contournent par le flanc si l'ennemi est entouré
		if role() == "assassin" and d > 6.0:
			var around := Vector3(-(tp - pos).z, 0, (tp - pos).x).normalized() * strafe * 3.0
			goal = tp + around
	else:
		var panic := 5.5 * (1.0 + (1.0 - aggression()) * 0.5)
		var ne2 := _nearest(enemies)
		var dn := _dist(ne2)
		if dn < panic and String(tac("defense_style", "kite")) != "block":
			goal = pos + Abilities.dir_to(ne2.global_position, pos) * 6.0
			# acculé : strafe
			if not f.battle.arena.inside(goal, 2.0):
				var perp2 := Vector3(-(ne2.global_position - pos).z, 0, (ne2.global_position - pos).x).normalized() * strafe
				goal = pos + perp2 * 4.0
			intent = "kite"
		elif d > r_pref + 2.5:
			goal = tp
			intent = "approach"
		elif d < r_pref - 3.0:
			goal = pos + Abilities.dir_to(tp, pos) * 3.0
			intent = "back"
		else:
			var perp3 := Vector3(-(tp - pos).z, 0, (tp - pos).x).normalized() * strafe
			goal = pos + perp3 * 2.5
			intent = "strafe"
	_choose_cast()

func _centroid(arr: Array[Fighter]) -> Vector3:
	if arr.is_empty():
		return Vector3.ZERO
	var s := Vector3.ZERO
	for a in arr:
		s += a.global_position
	return s / arr.size()

func _nearest(arr: Array[Fighter]) -> Fighter:
	var best: Fighter = null
	var bd := 1e9
	for a in arr:
		var d := _dist(a)
		if d < bd:
			bd = d
			best = a
	return best

func _basic_reach() -> float:
	if f.kit.is_empty():
		return 2.5
	var ab := f.kit[0]
	var r: float = float(ab.get("range", 2.8))
	return r

func _zone_danger() -> Vector3:
	var pos := f.global_position
	for z in f.battle.zones:
		if not is_instance_valid(z) or z.team == f.team or z.detonated or z.mode != "ground":
			continue
		var d := Abilities.flat(pos - z.global_position)
		if d.length() < z.radius + 1.2 and z.time_to_detonate() < 1.4:
			return d.normalized() if d.length() > 0.1 else Vector3(1, 0, 0)
	return Vector3.ZERO

# ----------------------------------------------------------------------------------------------
# Choix de compétence
# ----------------------------------------------------------------------------------------------
func _choose_cast() -> void:
	plan = {}
	if not f.cast.is_empty() or f.has_status("stun") or f.has_status("freeze"):
		return
	var usage: float = float(tac("ability_usage", 0.85))
	var best_slot := -1
	var best_s := 0.0
	var best_aim := Vector3.ZERO
	var best_t: Fighter = null
	for slot in f.kit.size():
		if slot == 1:
			continue   # le dash est géré à part
		if not f.ability_ready(slot):
			continue
		if slot > 0 and f.has_status("silence"):
			continue
		var r := _score(slot)
		if r.is_empty():
			continue
		var s: float = r["score"]
		if slot > 0 and rnd.randf() > usage:
			continue
		if s > best_s:
			best_s = s
			best_slot = slot
			best_aim = r["aim"]
			best_t = r.get("target")
	if best_slot >= 0:
		plan = {"slot": best_slot, "aim": best_aim, "target": best_t}
		return
	# dash
	if f.kit.size() > 1 and f.ability_ready(1) and not f.has_status("root"):
		var dd := _dash_plan()
		if not dd.is_empty():
			plan = dd

func _dash_plan() -> Dictionary:
	if target == null:
		return {}
	var d := _dist(target)
	var ab := f.kit[1]
	var rng: float = float(ab.get("range", 6.0))
	var dir_to_t := Abilities.dir_to(f.global_position, target.global_position)
	if is_melee():
		if d > rng + _basic_reach() + 1.0 and aggression() > 0.4 and f.sta > f.max_sta * 0.5:
			return {"slot": 1, "aim": f.global_position + dir_to_t * rng, "target": target}
	else:
		for e in _enemies():
			if _dist(e) < 4.0 and f.sta > f.max_sta * 0.4:
				var away := Abilities.dir_to(e.global_position, f.global_position)
				var dest := f.global_position + away * rng
				if f.battle.arena.inside(dest, 1.5):
					return {"slot": 1, "aim": dest, "target": null}
	# esquive d'une zone
	var dz := _zone_danger()
	if dz != Vector3.ZERO and rnd.randf() < 0.5 and f.sta > f.max_sta * 0.4:
		return {"slot": 1, "aim": f.global_position + dz * rng, "target": null}
	return {}

func _lead(t: Fighter, speed: float) -> Vector3:
	var aim_skill: float = float(tac("aim", 0.8))
	var d := _dist(t)
	var tv := t.vel
	var ttime := d / maxf(speed, 1.0)
	return t.global_position + tv * ttime * aim_skill

func _score(slot: int) -> Dictionary:
	var ab: Dictionary = f.kit[slot]
	var arch := String(ab.get("arch", "melee_arc"))
	var rng: float = float(ab.get("range", 0.0))
	var radius_a: float = float(ab.get("radius", 0.0))
	var enemies := _enemies()
	var is_basic := slot == 0
	var pos := f.global_position
	var weight := 1.0 + float(ab.get("dmg", 1.0)) * 0.35
	var ff_avoid: bool = bool(tac("friendly_fire_avoid", true))
	match arch:
		"melee_arc", "melee_thrust", "execute":
			if target == null:
				return {}
			var d := _dist(target)
			var reach := rng + target.radius + 0.2
			if d > reach:
				return {}
			var s := 1.0 if is_basic else 3.0 * weight
			if arch == "execute" and target.hp_pct() < 0.4:
				s += 6.0
			return {"score": s, "aim": target.global_position, "target": target}
		"melee_aoe", "nova":
			var cnt := Abilities.enemies_in_circle(f, pos, radius_a).size()
			var need := int(tac("aoe_efficiency", 2))
			if arch == "melee_aoe":
				need = 1
			if cnt < need:
				return {}
			var allies_hit := Abilities.allies_in_circle(f, pos, radius_a, false).size() if arch == "nova" else 0
			if ff_avoid and allies_hit > 0:
				return {}
			return {"score": 2.5 + cnt * 1.2 * weight, "aim": pos, "target": target}
		"projectile", "curse", "volley", "chain", "hook":
			if target == null:
				return {}
			var d2 := _dist(target)
			if d2 > rng * 0.95:
				return {}
			if arch == "hook" and d2 < 5.0:
				return {}
			if arch == "curse":
				var sts: Array = ab.get("status", [])
				if not sts.is_empty() and target.has_status(String(sts[0])):
					return {}
			if _blocked(pos, target.global_position):
				return {}
			var spd: float = float(ab.get("speed", 24.0))
			var aim := _lead(target, spd) if arch in ["projectile", "curse", "volley"] else target.global_position
			var s2 := (1.2 if is_basic else 2.8 * weight)
			if arch == "volley":
				s2 += 0.6 * Abilities.enemies_in_circle(f, target.global_position, 5.0).size()
			return {"score": s2, "aim": aim, "target": target}
		"beam", "cone", "drain":
			if target == null:
				return {}
			if _dist(target) > rng * 0.95 or _blocked(pos, target.global_position):
				return {}
			if arch == "cone":
				var cnt2 := 0
				for e in enemies:
					if _dist(e) < rng and Abilities.angle_ok(pos, Abilities.dir_to(pos, target.global_position), e.global_position, deg_to_rad(float(ab.get("angle", 65))) * 0.5):
						cnt2 += 1
				return {"score": 2.0 + cnt2 * 1.2, "aim": target.global_position, "target": target}
			return {"score": 3.0 * weight, "aim": target.global_position, "target": target}
		"ground_aoe":
			var best_c := Vector3.ZERO
			var best_n := 0
			for e in enemies:
				if _dist(e) > rng:
					continue
				var c := e.global_position + e.vel * 0.5
				var n := Abilities.enemies_in_circle(f, c, radius_a * 0.85).size()
				var fa := Abilities.allies_in_circle(f, c, radius_a, true).size()
				if ff_avoid and fa > 0:
					continue
				if n > best_n:
					best_n = n
					best_c = c
			if best_n < maxi(1, int(tac("aoe_efficiency", 2)) - 1):
				return {}
			return {"score": 2.5 + best_n * 1.5 * weight, "aim": best_c, "target": null}
		"leap", "charge":
			if target == null:
				return {}
			var d3 := _dist(target)
			if d3 < 3.5 or d3 > rng + 1.5:
				return {}
			return {"score": 3.0 * weight, "aim": target.global_position, "target": target}
		"blink":
			if target == null:
				return {}
			var d4 := _dist(target)
			if is_melee() and d4 > rng:
				return {"score": 2.0, "aim": target.global_position - Abilities.dir_to(pos, target.global_position) * 1.5, "target": target}
			if not is_melee() and d4 < 4.5:
				var away := Abilities.dir_to(target.global_position, pos)
				var dest := pos + away * rng
				if f.battle.arena.inside(dest, 1.5):
					return {"score": 3.0, "aim": dest, "target": null}
			return {}
		"dash":
			return {}
		"summon":
			var mine := 0
			for o in f.battle.fighters:
				if o.is_summon and o.owner_f == f and o.alive:
					mine += 1
			if mine >= 3 or enemies.is_empty():
				return {}
			var ne := _nearest(enemies)
			if _dist(ne) > 18.0:
				return {}
			var spot := pos + Abilities.dir_to(pos, ne.global_position) * minf(rng, 4.5)
			return {"score": 3.5, "aim": spot, "target": null}
		"trap":
			if target == null:
				return {}
			var d5 := _dist(target)
			if d5 > rng or d5 < 3.0:
				return {}
			return {"score": 1.8, "aim": target.global_position + target.vel * 0.7, "target": null}
		"heal", "heal_hot":
			var t: Fighter = ally_target
			if t == null or t.hp_pct() > 0.78:
				return {}
			if _dist(t) > rng:
				return {}
			var urgency := (1.0 - t.hp_pct())
			return {"score": 3.0 + urgency * 8.0, "aim": t.global_position, "target": t}
		"heal_chain":
			var t2: Fighter = ally_target
			if t2 == null or t2.hp_pct() > 0.75 or _dist(t2) > rng:
				return {}
			return {"score": 3.0 + (1.0 - t2.hp_pct()) * 6.0, "aim": t2.global_position, "target": t2}
		"heal_aoe":
			var hurt := 0
			var tot := 0.0
			for a in Abilities.allies_in_circle(f, pos, radius_a, true):
				if a.hp_pct() < 0.7:
					hurt += 1
					tot += 1.0 - a.hp_pct()
			if hurt < 2 and not (hurt == 1 and f.hp_pct() < 0.4):
				return {}
			return {"score": 3.0 + tot * 5.0, "aim": pos, "target": null}
		"resurrect":
			for o in f.battle.fighters:
				if o.team == f.team and not o.alive and not o.is_summon:
					if enemies.size() > 0 and _dist(_nearest(enemies)) > 6.0:
						return {"score": 9.0, "aim": o.global_position, "target": null}
			return {}
		"swap":
			return {}
		"shield":
			var near := Abilities.enemies_in_circle(f, pos, 11.0).size()
			if near == 0 or f.has_status("shield"):
				return {}
			if role() in ["healer", "support"] and ally_target != null and ally_target != f and _dist(ally_target) < 12.0 and ally_target.hp_pct() < 0.8 and not ally_target.has_status("shield"):
				return {"score": 3.5, "aim": ally_target.global_position, "target": ally_target}
			return {"score": 2.2 + (1.0 - f.hp_pct()) * 3.0, "aim": pos, "target": f}
		"guard":
			if f.hp_pct() < 0.4 and Abilities.enemies_in_circle(f, pos, 6.0).size() > 0:
				return {"score": 6.0, "aim": pos, "target": f}
			return {}
		"buff":
			var kind := String(ab.get("buff", "empower"))
			if f.has_status(kind):
				return {}
			if Abilities.enemies_in_circle(f, pos, 12.0).is_empty():
				return {}
			return {"score": 2.4, "aim": pos, "target": f}
		"taunt":
			var n6 := Abilities.enemies_in_circle(f, pos, radius_a).size()
			if n6 < 2:
				return {}
			var lowally := ally_target != null and ally_target != f and ally_target.hp_pct() < 0.6
			return {"score": 2.0 + n6 + (3.0 if lowally else 0.0), "aim": pos, "target": f}
		"stealth":
			if f.hp_pct() < 0.4 and not enemies.is_empty() and _dist(_nearest(enemies)) < 7.0:
				return {"score": 5.0, "aim": pos, "target": f}
			if role() == "assassin" and target != null and _dist(target) > 8.0 and not f.has_status("invisible"):
				return {"score": 2.0, "aim": pos, "target": f}
			return {}
		"time":
			var kind2 := String(ab.get("time_kind", "slow"))
			if kind2 == "rewind" and f.hp_pct() < 0.35:
				return {"score": 6.0, "aim": pos, "target": f}
			if kind2 == "refresh":
				var cdn := 0
				for i in range(2, f.cds.size()):
					if f.cds[i] > 3.0:
						cdn += 1
				if cdn >= 2:
					return {"score": 5.0, "aim": pos, "target": f}
				return {}
			if kind2 in ["stasis", "slow"] and Abilities.enemies_in_circle(f, pos, 9.0).size() >= 2:
				return {"score": 3.5, "aim": pos, "target": f}
			return {}
	return {}

func _blocked(a: Vector3, b: Vector3) -> bool:
	return f.battle.arena.segment_hits_obstacle(a, b, 0.3) != null

# ----------------------------------------------------------------------------------------------
# Action : mouvement + lancer
# ----------------------------------------------------------------------------------------------
func _act(dt: float) -> void:
	if f.kit.is_empty():
		return
	if f.base_speed > 0.1:
		var pos := f.global_position
		var to := Abilities.flat(goal - pos)
		var dir := Vector3.ZERO
		if to.length() > 0.7:
			dir = to.normalized()
		# évitement d'obstacles
		if dir != Vector3.ZERO:
			for o in f.battle.arena.obstacles:
				var c: Vector3 = o["pos"]
				var rel := Abilities.flat(c - pos)
				var dist := rel.length()
				var minr: float = float(o["r"]) + f.radius + 1.4
				if dist < minr + 1.0 and rel.normalized().dot(dir) > 0.2:
					var tang := Vector3(-rel.z, 0, rel.x).normalized()
					if tang.dot(dir) < 0.0:
						tang = -tang
					dir = (dir + tang * 1.4 - rel.normalized() * 0.3).normalized()
		# évite de rester collé aux bords en mode kite
		if not f.battle.arena.inside(pos + dir * 2.0, 1.2):
			var center_dir := Abilities.dir_to(pos, Vector3.ZERO)
			dir = (dir + center_dir * 0.9).normalized()
		f.move_input = dir
	# visée de repos : se tourne vers la cible
	if f.cast.is_empty() and target != null and plan.is_empty() and f.move_input.length() < 0.1:
		f.facing_dir = Abilities.dir_to(f.global_position, target.global_position) if Abilities.dir_to(f.global_position, target.global_position) != Vector3.ZERO else f.facing_dir
	# basique automatique
	if plan.is_empty() and f.cast.is_empty() and f.ability_ready(0) and target != null:
		var r := _score(0)
		if not r.is_empty() and rnd.randf() < 0.95:
			plan = {"slot": 0, "aim": r["aim"], "target": r.get("target")}
	if not plan.is_empty() and f.cast.is_empty():
		var slot: int = plan["slot"]
		if f.ability_ready(slot):
			f.try_cast(slot, plan["aim"], plan.get("target"))
		plan = {}
