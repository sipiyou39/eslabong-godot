class_name Fighter
extends Node3D
## Combattant en match : stats, ressources, statuts, mouvement, lancement de compétences, rendu 3D.

signal died(f: Fighter, killer: Fighter)

var battle: Battle
var spec: Dictionary = {}
var tpl: Dictionary = {}
var display_name: String = ""
var team: int = 0
var uid: String = ""
var level: int = 1
var kind: String = "class"
var is_summon: bool = false
var owner_f: Fighter = null
var life_time: float = -1.0
var summon_role: String = "melee"

# stats
var max_hp: float = 500.0
var hp: float = 500.0
var max_mana: float = 100.0
var mana: float = 100.0
var max_sta: float = 100.0
var sta: float = 100.0
var power: float = 30.0
var defense: float = 10.0
var mres: float = 10.0
var base_speed: float = 6.0
var mods: Dictionary = {}
var radius: float = 0.55
var alive: bool = true

# compétences
var kit: Array[Dictionary] = []
var cds: Array[float] = []
var cd_max: Array[float] = []
var cast: Dictionary = {}
var first_use_done: Dictionary = {}
var first_mana_used: bool = false
var statuses: Dictionary = {}
var shield_hp: float = 0.0

# mouvement
var move_input: Vector3 = Vector3.ZERO
var vel: Vector3 = Vector3.ZERO
var facing_dir: Vector3 = Vector3(1, 0, 0)
var forced: Dictionary = {}
var post_cast_slow: float = 0.0
var sta_regen_delay: float = 0.0
var hist: Array = []
var hist_t: float = 0.0

# contrôle
var player_index: int = -1
var ai: FighterAI
var target: Fighter = null
var tactics: Dictionary = {}

# stats de match
var st := {"damage": 0.0, "taken": 0.0, "healing": 0.0, "kills": 0, "assists": 0, "deaths": 0, "res": 0, "blocked": 0.0, "last_hit_by": null}
var damagers: Dictionary = {}   # Fighter id -> temps
var round_time_alive: float = 0.0
var model: CharacterModel
var ring: MeshInstance3D
var ring_mat: StandardMaterial3D
var aura_particles: CPUParticles3D
var status_fx: Dictionary = {}
var shadow_blob: MeshInstance3D
var echo_ready_until: float = 0.0
var echo_cd: float = 0.0
var kill_reset_cd: float = 0.0
var invisible_break := false
var hit_flash_cd: float = 0.0
var death_tw: Tween
var input_buf: Dictionary = {}

func setup(b: Battle, s: Dictionary, team_idx: int) -> void:
	battle = b
	spec = s
	team = team_idx
	tpl = s.get("tpl", Data.template(String(s.get("template_id", "Merc_Warrior_Fighter"))))
	display_name = String(s.get("name", tpl.get("display_name", "???")))
	uid = String(s.get("uid", str(randi())))
	level = int(s.get("level", 1))
	kind = String(tpl.get("kind", "class"))
	tactics = s.get("tactics", {}).duplicate()
	mods = s.get("mods", {}).duplicate()
	var stt: Dictionary = s.get("stats", {})
	if stt.is_empty():
		stt = _default_stats()
	max_hp = float(stt.get("hp", 500.0)) * (1.0 + _m("hp_perc") / 100.0)
	max_mana = float(stt.get("mana", 100.0)) * (1.0 + _m("man_perc") / 100.0)
	max_sta = float(stt.get("stamina", 100.0)) * (1.0 + _m("sta_perc") / 100.0)
	power = float(stt.get("power", 30.0)) * (1.0 + (_m("atk_perc") + _m("glass_cannon")) / 100.0)
	defense = float(stt.get("defense", 10.0)) * (1.0 + _m("def_perc") / 100.0)
	mres = float(stt.get("mres", 10.0))
	base_speed = float(stt.get("speed", 6.0)) * (1.0 + (_m("msp_perc") + _m("glass_cannon")) / 100.0) + _m("msp_flat") * 0.01
	hp = max_hp
	mana = max_mana
	sta = max_sta
	radius = 0.5 * float(tpl.get("scale", 1.0)) * CharacterModel.GLOBAL_SCALE
	var kit_ids: Array = s.get("kit", tpl.get("kit", []))
	for id in kit_ids:
		var ab: Dictionary = Data.ability(String(id)).duplicate()
		if ab.is_empty():
			continue
		kit.append(ab)
		cds.append(0.0)
		cd_max.append(float(ab.get("cd", 1.0)))
	is_summon = bool(s.get("is_summon", false))
	summon_role = String(s.get("summon_role", "melee"))
	_build_visuals()
	ai = FighterAI.new()
	ai.f = self

func _default_stats() -> Dictionary:
	var b: Dictionary = tpl.get("base", {"hp": 500, "mana": 100, "stamina": 100, "power": 30, "defense": 10, "mres": 10, "speed": 6.0})
	var lv := 1.0 + 0.07 * (level - 1)
	var m: float = float(tpl.get("stat_mult", 1.0))
	return {"hp": b["hp"] * lv * m, "mana": b["mana"], "stamina": b["stamina"], "power": b["power"] * lv * (1.0 + (m - 1.0) * 0.5), "defense": b["defense"] * (1.0 + 0.02 * level) * (1.0 + (m - 1.0) * 0.4),
		"mres": b["mres"], "speed": b["speed"]}

func _m(k: String) -> float:
	return float(mods.get(k, 0.0))

func _build_visuals() -> void:
	model = CharacterModel.new()
	add_child(model)
	var pal: Array = spec.get("palette", [])
	model.build(tpl, pal, int(spec.get("variant", 0)), bool(spec.get("shiny", false)))
	# anneau d'équipe
	ring = MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(1, 1)
	q.orientation = PlaneMesh.FACE_Y
	ring.mesh = q
	ring_mat = battle.vfx.additive_mat("glow_ring", Settings.team_color(team) if not is_summon else Settings.team_color(team).darkened(0.2), false).duplicate()
	ring.material_override = ring_mat
	ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var rs := radius * 2.9
	ring.scale = Vector3(rs, 1, rs)
	ring.position = Vector3(0, 0.05, 0)
	add_child(ring)
	if kind != "class" or bool(spec.get("legendary", false)) or bool(spec.get("shiny", false)):
		var ac: Color = Color(str(tpl.get("aura", "#ffd060"))) if kind != "class" else (Color("ffe9a0") if bool(spec.get("legendary", false)) else Color("8affff"))
		aura_particles = battle.vfx.trail(self, ac, 0.22, 18, 1.0, "spark_star4")
		aura_particles.position = Vector3(0, 0.9, 0)
		aura_particles.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
		aura_particles.emission_sphere_radius = 0.6 * radius * 2.0
		aura_particles.local_coords = true
		aura_particles.gravity = Vector3(0, 0.8, 0)
		model.set_glow(1.4)
	if is_summon:
		model.set_tint(Color(0.6, 0.8, 1.0), 0.25)

func is_enemy_of(o: Fighter) -> bool:
	return o.team != team

func hp_pct() -> float:
	return hp / maxf(max_hp, 1.0)

# ----------------------------------------------------------------------------------------------
# Statuts
# ----------------------------------------------------------------------------------------------
func has_status(s: String) -> bool:
	return statuses.has(s)

func add_status(s: String, dur: float, pw: float = 1.0, src: Fighter = null) -> void:
	if not alive:
		return
	var info: Dictionary = Data.STATUS_INFO.get(s, {})
	var good: bool = info.get("good", false)
	if not good:
		if has_status("invulnerable"):
			return
		dur *= clampf(1.0 - _m("cc_reduction") / 100.0, 0.2, 1.0)
		if s in ["stun", "freeze", "fear", "root", "silence"] and kind == "boss":
			dur *= 0.5
	if statuses.has(s):
		var cur: Dictionary = statuses[s]
		cur["t"] = maxf(cur["t"], dur)
		cur["power"] = maxf(cur["power"], pw)
		cur["src"] = src
	else:
		statuses[s] = {"t": dur, "power": pw, "src": src, "tick": 0.0}
		_status_visual_on(s)
	if s == "shield":
		shield_hp = pw
	if not good and battle and Settings.gb("status_effect_text_enabled") and (s in ["stun", "freeze", "fear", "root", "silence"]):
		battle.vfx.float_text(global_position + Vector3(0, model.height() + 0.4, 0), String(info.get("name", s)), info.get("color", Color.WHITE), 0.7, 1.0, 0.7)

func remove_status(s: String) -> void:
	if statuses.has(s):
		statuses.erase(s)
		_status_visual_off(s)

func _status_visual_on(s: String) -> void:
	var info: Dictionary = Data.STATUS_INFO.get(s, {})
	var col: Color = info.get("color", Color.WHITE)
	match s:
		"freeze":
			model.set_tint(Color(0.7, 0.9, 1.0), 0.65)
		"stun":
			model.stunned = true
		"invisible":
			model.set_ghost(0.75)
		"invulnerable":
			model.set_param("rim_strength", 1.8)
			model.set_param("rim_color", Color(1, 0.95, 0.6))
		"burn", "poison", "bleed", "regen", "haste", "empower", "thorns", "lifesteal", "mark", "weaken", "slow", "armor_up", "armor_break", "taunted", "silence", "root", "fear", "shield":
			if not status_fx.has(s):
				var p := battle.vfx.trail(self, col, 0.25, 10, 0.7, "spark_star4")
				p.position = Vector3(0, 0.9, 0)
				p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
				p.emission_sphere_radius = 0.45
				p.local_coords = true
				p.gravity = Vector3(0, 0.6 if info.get("good", false) else -0.2, 0)
				status_fx[s] = p

func _status_visual_off(s: String) -> void:
	match s:
		"freeze":
			model.set_tint(Color.WHITE, 0.0)
		"stun":
			model.stunned = false
		"invisible":
			model.set_ghost(0.0)
		"invulnerable":
			model.set_param("rim_strength", 0.55)
			model.set_param("rim_color", model.accent_color.lerp(Color(0.7, 0.85, 1.0), 0.5))
	if status_fx.has(s):
		var p: CPUParticles3D = status_fx[s]
		if is_instance_valid(p):
			p.emitting = false
			p.get_tree().create_timer(1.0).timeout.connect(p.queue_free)
		status_fx.erase(s)

func speed_mult() -> float:
	var m := 1.0
	if has_status("slow"):
		m *= 1.0 - minf(0.6, 0.35 * float(statuses["slow"]["power"]))
	if has_status("haste"):
		m *= 1.0 + 0.3 * float(statuses["haste"]["power"])
	if battle.round_time < 6.0 and mods.has("start_speed_perc"):
		m *= 1.0 + _m("start_speed_perc") / 100.0
	return m

func defense_now(magic: bool) -> float:
	var d := mres if magic else defense
	if has_status("armor_up"):
		d *= 1.3
	if has_status("armor_break"):
		d *= 0.7
	if shield_hp > 0.0 and mods.has("shield_def_flat"):
		d += _m("shield_def_flat")
	if mods.has("dash_def_perc") and statuses.has("dash_def"):
		d *= 1.0 + _m("dash_def_perc") / 100.0
	return d

func can_act() -> bool:
	return alive and not has_status("stun") and not has_status("freeze") and battle.state == Battle.State.FIGHTING

func can_move() -> bool:
	return can_act() and not has_status("root") and (cast.is_empty() or Abilities.cast_allows_move(cast))

# ----------------------------------------------------------------------------------------------
# Boucle principale
# ----------------------------------------------------------------------------------------------
func _process(dt: float) -> void:
	if battle == null:
		return
	if not alive:
		return
	if hit_flash_cd > 0.0:
		hit_flash_cd -= dt
	_tick_statuses(dt)
	if not alive:
		return
	if life_time > 0.0:
		life_time -= dt
		if life_time <= 0.0:
			die(null, true)
			return
	# régénération
	var fighting := battle.state == Battle.State.FIGHTING
	if fighting:
		round_time_alive += dt
		mana = minf(max_mana, mana + (3.2 + max_mana * 0.012) * dt)
		sta_regen_delay -= dt
		if sta_regen_delay <= 0.0:
			sta = minf(max_sta, sta + (16.0 + max_sta * 0.08) * dt)
		for i in cds.size():
			if cds[i] > 0.0:
				cds[i] = maxf(0.0, cds[i] - dt)
		_record_history(dt)
	if kill_reset_cd > 0.0:
		kill_reset_cd -= dt
	if echo_cd > 0.0:
		echo_cd -= dt
	# contrôle
	move_input = Vector3.ZERO
	if fighting and can_act():
		if player_index >= 0:
			battle.player_input(self, dt)
		elif ai:
			ai.update(dt)
	if not cast.is_empty():
		Abilities.update_cast(self, cast, dt)
	_move(dt)
	_update_visuals(dt)

func _record_history(dt: float) -> void:
	hist_t += dt
	if hist_t >= 0.25:
		hist_t = 0.0
		hist.append({"pos": global_position, "hp": hp})
		if hist.size() > 16:
			hist.pop_front()

func _tick_statuses(dt: float) -> void:
	var to_remove: Array[String] = []
	for s in statuses:
		var d: Dictionary = statuses[s]
		d["t"] -= dt
		d["tick"] += dt
		match s:
			"burn", "poison", "bleed":
				if d["tick"] >= 0.5:
					d["tick"] -= 0.5
					var srcf: Fighter = d["src"] if (d["src"] != null and is_instance_valid(d["src"])) else null
					var base: float = (srcf.power if srcf else 25.0) * 0.14 * float(d["power"])
					battle.deal_damage(srcf, self, base, {"element": {"burn": "fire", "poison": "nature", "bleed": "blood"}[s], "dot": true, "mag": s != "bleed"})
			"regen":
				if d["tick"] >= 0.5:
					d["tick"] -= 0.5
					battle.heal(d["src"] if d["src"] != null and is_instance_valid(d["src"]) else null, self, float(d["power"]) * 0.5, {"hot": true})
		if d["t"] <= 0.0:
			to_remove.append(s)
	for s in to_remove:
		remove_status(s)
	if shield_hp <= 0.0 and has_status("shield"):
		remove_status("shield")
	if has_status("shield"):
		pass
	if not alive:
		return

func _move(dt: float) -> void:
	var pos := global_position
	var fighting := battle.state == Battle.State.FIGHTING
	if not forced.is_empty():
		Abilities.update_forced(self, dt)
		pos = global_position
	elif fighting and can_move():
		var dir := move_input
		if has_status("fear"):
			var away := Vector3.ZERO
			var src: Fighter = statuses["fear"]["src"] if statuses["fear"]["src"] != null and is_instance_valid(statuses["fear"]["src"]) else null
			away = (global_position - src.global_position) if src else Vector3(randf() - 0.5, 0, randf() - 0.5)
			away.y = 0
			dir = away.normalized()
		var sp := base_speed * speed_mult()
		if not cast.is_empty():
			sp *= Abilities.cast_move_mult(cast)
		if post_cast_slow > 0.0:
			post_cast_slow -= dt
			sp *= 0.55
		var target_v := dir.limit_length(1.0) * sp
		vel = vel.lerp(target_v, 1.0 - exp(-dt * 14.0))
		pos += vel * dt
		if dir.length() > 0.1:
			facing_dir = facing_dir.slerp(dir.normalized(), 1.0 - exp(-dt * 14.0)) if facing_dir.length() > 0.1 else dir.normalized()
	else:
		vel = vel.lerp(Vector3.ZERO, 1.0 - exp(-dt * 12.0))
		if not cast.is_empty() or fighting:
			pos += vel * dt
	# séparation douce entre combattants
	if fighting:
		for o in battle.fighters:
			if o == self or not o.alive:
				continue
			var d := pos - o.global_position
			d.y = 0
			var minr := radius + o.radius
			var l := d.length()
			if l < minr and l > 0.0001:
				var push := (minr - l) * 0.5
				pos += d / l * push * (0.6 if forced.is_empty() else 0.2)
	pos = battle.arena.push_out(pos, radius)
	pos = battle.arena.clamp_point(pos, radius)
	pos.y = 0.0
	global_position = pos
	# orientation
	if not cast.is_empty() and cast.has("aim_dir"):
		var ad: Vector3 = cast["aim_dir"]
		if ad.length() > 0.01:
			facing_dir = facing_dir.slerp(ad.normalized(), 1.0 - exp(-dt * 22.0)) if facing_dir.length() > 0.01 else ad.normalized()
	if facing_dir.length() > 0.01:
		var yaw := atan2(facing_dir.x, facing_dir.z)
		rotation.y = lerp_angle(rotation.y, yaw, 1.0 - exp(-dt * 18.0))

func _update_visuals(dt: float) -> void:
	var spd := Vector2(vel.x, vel.z).length()
	model.loco = clampf(spd / maxf(base_speed, 1.0), 0.0, 1.2)
	model.channeling = cast.has("channel_left") and cast["channel_left"] > 0.0
	ring_mat.albedo_color.a = 1.0 if alive else 0.0
	var pulse := 0.75 + 0.25 * sin(Time.get_ticks_msec() / 220.0 + float(hash(uid) % 10))
	if player_index >= 0:
		ring_mat.albedo_color = Color(1, 1, 1, 1).lerp(Settings.team_color(team), 0.25) * (1.0 + 0.5 * pulse)
		ring.scale = Vector3.ONE * radius * 3.4
	else:
		ring_mat.albedo_color = Settings.team_color(team) * 1.2
		ring_mat.albedo_color.a = 1.0
	# bonus de vitesse/regard
	if has_status("invisible") and player_index < 0:
		model.set_ghost(0.85)

# ----------------------------------------------------------------------------------------------
# Lancer
# ----------------------------------------------------------------------------------------------
func ability_ready(slot: int) -> bool:
	if slot < 0 or slot >= kit.size():
		return false
	return cds[slot] <= 0.0 and can_pay(slot)

func cost_mana(slot: int) -> float:
	var ab := kit[slot]
	var c: float = float(ab.get("mana", 0))
	c *= 1.0 - _m("mana_cost_reduction_perc") / 100.0
	if not first_mana_used and mods.has("first_mana_reduction_perc") and c > 0.0:
		c *= 1.0 - _m("first_mana_reduction_perc") / 100.0
	return c

func cost_sta(slot: int) -> float:
	var ab := kit[slot]
	var c: float = float(ab.get("sta", 0))
	c *= 1.0 - _m("stamina_cost_reduction_perc") / 100.0
	if String(ab.get("arch", "")) in ["dash"] and slot == 1:
		c *= 1.0 - _m("dash_stamina_reduction_perc") / 100.0
		if mods.has("echo_dash"):
			c *= 1.15
	return c

func can_pay(slot: int) -> bool:
	return mana >= cost_mana(slot) and sta >= cost_sta(slot)

func is_basic_slot(slot: int) -> bool:
	return slot == 0

func try_cast(slot: int, aim: Vector3, tgt: Fighter = null) -> bool:
	if not can_act() or not cast.is_empty() or not forced.is_empty():
		return false
	if slot < 0 or slot >= kit.size():
		return false
	var ab := kit[slot]
	if not ability_ready(slot):
		return false
	if has_status("silence") and slot != 0 and slot != 1:
		return false
	var c := Abilities.begin(self, slot, ab, aim, tgt)
	if c.is_empty():
		return false
	return true

func pay_and_cooldown(slot: int) -> void:
	var ab := kit[slot]
	var cm := cost_mana(slot)
	if cm > 0.0:
		mana -= cm
		first_mana_used = true
	var cs := cost_sta(slot)
	if cs > 0.0:
		sta -= cs
		sta_regen_delay = 0.9
	var cdv: float = float(ab.get("cd", 1.0))
	if slot == 0:
		cdv /= 1.0 + 0.0
	if slot > 0 and not first_use_done.get(slot, false) and mods.has("first_cooldown_reduction_perc"):
		cdv *= 1.0 - _m("first_cooldown_reduction_perc") / 100.0
	first_use_done[slot] = true
	cdv *= 1.0 - float(spec.get("cdr", 0.0))
	cds[slot] = cdv
	cd_max[slot] = cdv

func cd_frac(slot: int) -> float:
	if slot >= cds.size() or cd_max[slot] <= 0.0:
		return 0.0
	return cds[slot] / cd_max[slot]

func reset_round() -> void:
	for i in cds.size():
		cds[i] = 0.0
	first_use_done.clear()
	first_mana_used = false
	statuses.clear()
	for s in status_fx.keys():
		_status_visual_off(s)
	shield_hp = 0.0
	cast.clear()
	forced.clear()
	hist.clear()
	hp = max_hp
	mana = max_mana
	sta = max_sta
	alive = true
	vel = Vector3.ZERO
	round_time_alive = 0.0
	damagers.clear()
	if death_tw:
		death_tw.kill()
	model.revive()
	model.dead = false
	model.os_name = ""
	model.set_param("dissolve", 0.0)
	model.set_ghost(0.0)
	model.set_tint(Color.WHITE, 0.0)
	visible = true
	ring.visible = true
	if mods.has("start_barrier_perc"):
		add_status("shield", 5.0, max_hp * _m("start_barrier_perc") / 100.0, self)

func take_hit_visual(crit: bool) -> void:
	if hit_flash_cd <= 0.0:
		model.flash(Color(1, 1, 1, 0.7 if crit else 0.45), 0.09)
		hit_flash_cd = 0.07
	model.hit_react()

func die(killer: Fighter, silent: bool = false) -> void:
	if not alive:
		return
	alive = false
	hp = 0.0
	cast.clear()
	forced.clear()
	st["deaths"] += 1
	for s in statuses.keys():
		remove_status(s)
	model.die()
	ring.visible = false
	if aura_particles:
		aura_particles.emitting = false
	Audio.play_at("voice_death" if not is_summon else "death_light", global_position)
	if not silent:
		battle.vfx.burst(global_position + Vector3(0, 0.8, 0), Data.elem_color(String(tpl.get("element", "physical"))), 16, 5.0, 0.7, 0.4, "soft_glow", -3.0, 160.0)
		battle.vfx.shake(0.25 if kind == "class" else 0.5)
	if death_tw:
		death_tw.kill()
	death_tw = create_tween()
	death_tw.tween_interval(1.6 if not is_summon else 0.2)
	death_tw.tween_method(func(v: float): if model: model.set_param("dissolve", v), 0.0, 1.0, 0.9)
	if is_summon:
		death_tw.tween_callback(func(): visible = false)
	died.emit(self, killer)

func revive(hp_frac: float) -> void:
	alive = true
	hp = max_hp * hp_frac
	mana = max_mana * 0.5
	sta = max_sta
	statuses.clear()
	cast.clear()
	forced.clear()
	if death_tw:
		death_tw.kill()
	model.revive()
	model.set_param("dissolve", 0.0)
	ring.visible = true
	if aura_particles:
		aura_particles.emitting = true
	add_status("invulnerable", 1.0, 1.0, self)
