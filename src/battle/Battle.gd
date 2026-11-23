class_name Battle
extends Node3D
## Match en temps réel : monde 3D, manches, dégâts, caméra, contrôle joueur, résultat.

enum State { INTRO, COUNTDOWN, FIGHTING, ROUND_END, MATCH_END }

var config: Dictionary = {}
var state: int = State.INTRO
var arena: Arena
var vfx: Vfx
var camera: Camera3D
var hud: BattleHUD
var fighters: Array[Fighter] = []
var zones: Array = []
var fx_root: Node3D
var time: float = 0.0
var round_time: float = 0.0
var round_no: int = 0
var wins: Array[int] = []
var teams: Array = []
var team_count: int = 2
var rounds_to_win: int = 2
var time_limit: float = 90.0
var storm_start: float = 55.0
var controlled: Array[Fighter] = []
var cam_center: Vector3 = Vector3.ZERO
var cam_height: float = 30.0
var cam_pos_smooth: Vector3
var cam_pitch: float = deg_to_rad(60.0)
var zoom_mult: float = 1.0
var intro_t: float = 0.0
var state_t: float = 0.0
var player_aim_pt: Vector3 = Vector3.ZERO
var speed_mode: int = 0
var paused_menu: bool = false
var last_round_winner: int = -1
var result: Dictionary = {}
var kill_log: Array = []
var ffa: bool = false
var spectator_click_cd: float = 0.0
var storm_warned: bool = false
var slowmo_t: float = 0.0
var allow_control: bool = true
var _count_last: int = -1
var fighter_cycle_idx: int = 0

func _ready() -> void:
	name = "Battle"
	teams = config.get("teams", [])
	team_count = teams.size()
	ffa = bool(config.get("ffa", false))
	rounds_to_win = int(config.get("rounds_to_win", 2))
	time_limit = float(config.get("time_limit", 90.0))
	storm_start = float(config.get("storm_start", 55.0))
	allow_control = bool(config.get("allow_control", true))
	for i in team_count:
		wins.append(0)
	fx_root = Node3D.new()
	fx_root.name = "FX"
	add_child(fx_root)
	vfx = Vfx.new()
	vfx.root = fx_root
	add_child(vfx)
	arena = Arena.new()
	add_child(arena)
	camera = Camera3D.new()
	camera.fov = 36.0
	camera.near = 0.5
	camera.far = 260.0
	camera.current = true
	add_child(camera)
	vfx.camera = camera
	arena.setup(String(config.get("arena", "colosseum")), vfx)
	_apply_camera_attributes()
	_spawn_all()
	hud = BattleHUD.new()
	hud.battle = self
	add_child(hud)
	speed_mode = Settings.gi("battle_speed_mode")
	_apply_speed()
	Audio.music(String(config.get("music", "music_battle_1")))
	Audio.loop_start("crowd_ambience_loop", -10.0)
	cam_center = Vector3.ZERO
	cam_height = 46.0
	cam_pos_smooth = Vector3(0, 40, 36)
	_set_state(State.INTRO)

func _exit_tree() -> void:
	Audio.loop_stop("crowd_ambience_loop")
	Engine.time_scale = 1.0

func _apply_camera_attributes() -> void:
	if not Settings.gb("postfx_enabled") or not Settings.gb("dof"):
		return
	var attrs := CameraAttributesPractical.new()
	attrs.dof_blur_far_enabled = true
	attrs.dof_blur_far_distance = 55.0
	attrs.dof_blur_far_transition = 25.0
	attrs.dof_blur_amount = 0.04
	attrs.dof_blur_near_enabled = true
	attrs.dof_blur_near_distance = 14.0
	attrs.dof_blur_near_transition = 8.0
	camera.attributes = attrs

# ----------------------------------------------------------------------------------------------
# Création des combattants
# ----------------------------------------------------------------------------------------------
func _spawn_all() -> void:
	for ti in team_count:
		var t: Dictionary = teams[ti]
		var specs: Array = t.get("fighters", [])
		var spawns := arena.spawn_positions(ti, specs.size(), team_count)
		for i in specs.size():
			var f := spawn_fighter(specs[i], ti, spawns[i])
			f.set_meta("spawn", spawns[i])
	# contrôle joueur : le premier combattant de l'équipe 0
	if allow_control and not ffa or (ffa and allow_control):
		var mine: Array[Fighter] = _team_fighters(int(config.get("player_team", 0)))
		if not mine.is_empty() and bool(config.get("auto_control", true)):
			take_control(mine[0], 0)

func _team_fighters(ti: int) -> Array[Fighter]:
	var out: Array[Fighter] = []
	for f in fighters:
		if f.team == ti and not f.is_summon:
			out.append(f)
	return out

func spawn_fighter(spec: Dictionary, team_idx: int, pos: Vector3) -> Fighter:
	var f := Fighter.new()
	f.name = String(spec.get("name", "F"))
	add_child(f)
	f.setup(self, spec, team_idx)
	f.global_position = pos
	f.facing_dir = Vector3(1, 0, 0) if pos.x < 0 else Vector3(-1, 0, 0)
	if ffa:
		f.facing_dir = (-pos).normalized()
	f.rotation.y = atan2(f.facing_dir.x, f.facing_dir.z)
	fighters.append(f)
	f.died.connect(_on_fighter_died)
	if bool(spec.get("is_summon", false)):
		f.mods["start_speed_perc"] = 0
	return f

func add_fx(n: Node) -> void:
	fx_root.add_child(n)

func take_control(f: Fighter, pidx: int) -> void:
	for c in controlled:
		if is_instance_valid(c) and c != f:
			c.player_index = -1
	f.player_index = pidx
	controlled = [f]
	if hud:
		hud.on_control_changed(f)

func controlled_fighter() -> Fighter:
	for c in controlled:
		if is_instance_valid(c) and c.alive:
			return c
	return null

# ----------------------------------------------------------------------------------------------
# États
# ----------------------------------------------------------------------------------------------
func _set_state(s: int) -> void:
	state = s
	state_t = 0.0
	match s:
		State.INTRO:
			round_no += 1
			_reset_round()
			intro_t = 0.0
			hud.show_banner(_intro_title(), _intro_sub(), 2.4)
		State.COUNTDOWN:
			_count_last = -1
		State.FIGHTING:
			round_time = 0.0
			arena.shrink = 1.0
			arena.set_storm_strength(0.0)
			storm_warned = false
			hud.show_banner("COMBAT !", "", 0.8)
			Audio.play("round_start_horn", 0.0, 1.0, true)
		State.ROUND_END:
			pass
		State.MATCH_END:
			_finish_match()

func _intro_title() -> String:
	if round_no == 1:
		var names: Array[String] = []
		for t in teams:
			names.append(String(t.get("name", "?")))
		return " VS ".join(names) if not ffa else "CHAOS THUNDER"
	return "MANCHE %d" % round_no

func _intro_sub() -> String:
	if ffa:
		return "Le dernier survivant l'emporte"
	var parts: Array[String] = []
	for i in team_count:
		parts.append(str(wins[i]))
	return "Score  " + " - ".join(parts) if round_no > 1 else "Premier à %d manches" % rounds_to_win

func _reset_round() -> void:
	# supprime les invocations, remet tout le monde en place
	for f in fighters.duplicate():
		if f.is_summon:
			fighters.erase(f)
			f.queue_free()
	for z in zones.duplicate():
		if is_instance_valid(z):
			z.queue_free()
	zones.clear()
	for n in fx_root.get_children():
		if n is Projectile:
			n.queue_free()
	arena.shrink = 1.0
	arena.set_storm_strength(0.0)
	for f in fighters:
		f.reset_round()
		if f.ai:
			f.ai.target = null
			f.ai.ally_target = null
			f.ai.plan = {}
		if f.has_meta("spawn"):
			var sp: Vector3 = f.get_meta("spawn")
			f.global_position = sp
			f.facing_dir = Vector3(1, 0, 0) if sp.x < 0 else Vector3(-1, 0, 0)
			if ffa:
				f.facing_dir = (-sp).normalized()
			f.rotation.y = atan2(f.facing_dir.x, f.facing_dir.z)
		f.model.trigger("", 0.1)

func _process(dt: float) -> void:
	time += dt
	state_t += dt
	match state:
		State.INTRO:
			intro_t += dt
			if state_t >= 2.4:
				_set_state(State.COUNTDOWN)
		State.COUNTDOWN:
			var n := 3 - int(state_t)
			if n != _count_last and n >= 1:
				_count_last = n
				hud.show_count(n)
				Audio.play("countdown_beep", 0.0, 1.0 + (3 - n) * 0.12, true)
			if state_t >= 3.0:
				Audio.play("countdown_go", 0.0, 1.0, true)
				_set_state(State.FIGHTING)
		State.FIGHTING:
			round_time += dt
			_storm(dt)
			_check_round_end()
		State.ROUND_END:
			if state_t >= 3.2:
				if _match_decided():
					_set_state(State.MATCH_END)
				else:
					_set_state(State.INTRO)
	if slowmo_t > 0.0:
		slowmo_t -= dt
		if slowmo_t <= 0.0:
			_apply_speed()
	_handle_global_input(dt)
	_update_camera(dt)
	if state == State.FIGHTING:
		_update_spectator_click(dt)

# ----------------------------------------------------------------------------------------------
# Tempête, fin de manche
# ----------------------------------------------------------------------------------------------
func _storm(dt: float) -> void:
	if round_time < storm_start:
		return
	if not storm_warned:
		storm_warned = true
		hud.show_banner("LA TEMPÊTE SE REFERME", "", 2.0)
		Audio.play("timer_warning", 0.0, 1.0, true)
	var u := clampf((round_time - storm_start) / 40.0, 0.0, 1.0)
	arena.shrink = lerpf(1.0, 0.38, u)
	arena.set_storm_strength(minf((round_time - storm_start) * 0.4, 1.0))
	for f in fighters:
		if f.alive and not arena.inside(f.global_position, f.radius * 0.5):
			deal_damage(null, f, f.max_hp * 0.03 * dt * 2.0, {"element": "lightning", "dot": true, "true": true, "tick": true})
			if randf() < dt * 6.0:
				vfx.lightning(f.global_position + Vector3(0, 4, 0), f.global_position + Vector3(0, 0.5, 0), Color("c8a0ff"), 0.2, 0.15, 0.4)

func _alive_teams() -> Dictionary:
	var d := {}
	for f in fighters:
		if f.alive and not f.is_summon:
			d[f.team] = d.get(f.team, 0) + 1
	return d

func _check_round_end() -> void:
	var at := _alive_teams()
	if at.size() <= 1:
		var win := -1
		if at.size() == 1:
			win = at.keys()[0]
		_end_round(win)
		return
	if round_time >= time_limit + 40.0:
		_end_round(_winner_by_hp())

func _winner_by_hp() -> int:
	var best := -1
	var bv := -1.0
	for ti in team_count:
		var s := 0.0
		for f in fighters:
			if f.team == ti and not f.is_summon and f.alive:
				s += f.hp
		if s > bv:
			bv = s
			best = ti
	return best

func _end_round(winner: int) -> void:
	last_round_winner = winner
	if winner >= 0:
		wins[winner] += 1
	_set_state(State.ROUND_END)
	slowmo_t = 0.9
	Engine.time_scale = 0.35
	var win_name := String(teams[winner].get("name", "?")) if winner >= 0 else "Égalité"
	hud.show_banner("MANCHE POUR " + win_name.to_upper() if winner >= 0 else "ÉGALITÉ", "", 2.6)
	for f in fighters:
		if f.alive and f.team == winner and not f.is_summon:
			f.model.trigger("victory", 3.0)
	if winner == int(config.get("player_team", 0)):
		Audio.play("victory_fanfare", -4.0, 1.0, true)
	else:
		Audio.play("defeat_sting", -4.0, 1.0, true)
	Game.postfx_pulse(0.01, Color(1, 1, 1, 0.35), 0.4)

func _match_decided() -> bool:
	for i in team_count:
		if wins[i] >= rounds_to_win:
			return true
	return false

func _finish_match() -> void:
	var win := 0
	var bw := -1
	for i in team_count:
		if wins[i] > bw:
			bw = wins[i]
			win = i
	var res := {"winner": win, "wins": wins.duplicate(), "teams": [], "rounds": round_no, "mode": config.get("mode", "quick"), "kill_log": kill_log, "config_id": config.get("id", "")}
	for ti in team_count:
		var arr: Array = []
		for f in fighters:
			if f.team == ti and not f.is_summon:
				arr.append({"uid": f.uid, "name": f.display_name, "template": String(f.tpl.get("id", f.tpl.get("named_id", ""))), "class_name": String(f.tpl.get("name", "")), "stats": f.st.duplicate(), "alive": f.alive, "hp_pct": f.hp_pct(), "level": f.level})
		res["teams"].append({"name": teams[ti].get("name", "?"), "fighters": arr})
	result = res
	Game.last_battle_result = res
	hud.show_result(res)
	if config.get("auto_exit", false):
		get_tree().create_timer(1.5, true, false, true).timeout.connect(finish_and_exit)
	Audio.music("music_victory" if win == int(config.get("player_team", 0)) else "music_defeat")

func finish_and_exit() -> void:
	Engine.time_scale = 1.0
	var cb: Variant = config.get("on_finish")
	if cb is Callable and (cb as Callable).is_valid():
		(cb as Callable).call(result)
	else:
		Game.goto_main_menu()

# ----------------------------------------------------------------------------------------------
# Dégâts / soins
# ----------------------------------------------------------------------------------------------
func deal_damage(src: Fighter, dst: Fighter, amount: float, o: Dictionary) -> float:
	if dst == null or not dst.alive:
		return 0.0
	var is_dot: bool = bool(o.get("dot", false))
	var tick: bool = bool(o.get("tick", false))
	var is_basic: bool = bool(o.get("basic", false))
	if dst.has_status("invulnerable"):
		if not is_dot:
			vfx.float_text(dst.global_position + Vector3(0, dst.model.height() + 0.3, 0), "Immunisé", Color("fff0a0"), 0.6, 0.9, 0.6)
		return 0.0
	var amt := amount
	if src != null:
		if src.has_status("empower"):
			amt *= 1.25
		if src.has_status("weaken"):
			amt *= 0.8
		if not is_dot:
			if is_basic:
				amt *= 1.0 + src._m("basic_damage_perc") / 100.0
			elif not o.get("relic", false) and not tick:
				amt *= 1.0 + src._m("ability_damage_perc") / 100.0
			if src._m("lone_wolf") > 0.0:
				var near := false
				for a in fighters:
					if a != src and a.alive and a.team == src.team and Abilities.flat(a.global_position - src.global_position).length() < 8.0:
						near = true
				if not near:
					amt *= 1.0 + src._m("lone_wolf") / 100.0
		if src.team == dst.team and src != dst:
			if not o.get("ff", false) and not o.get("aoe", false):
				return 0.0
			amt *= Settings.gf("friendly_fire_multiplier")
	var crit := false
	if not is_dot and not tick and not o.get("true", false) and src != null and src.team != dst.team:
		if randf() < 0.07 + (0.06 if src.has_status("mark") else 0.0) + float(src.spec.get("crit_bonus", 0.0)):
			crit = true
			amt *= 1.6
	amt *= randf_range(0.95, 1.05)
	var mag: bool = bool(o.get("mag", false))
	if not o.get("true", false):
		var d := dst.defense_now(mag)
		var mult := 100.0 / (100.0 + maxf(d, 0.0) * 1.6)
		if dst.has_status("mark"):
			mult *= 1.15
		mult *= 1.0 + (dst._m("damage_taken_perc") + dst._m("glass_cannon")) / 100.0
		amt *= mult
	amt = maxf(amt, 1.0)
	# barrière
	var absorbed := 0.0
	if dst.shield_hp > 0.0:
		absorbed = minf(dst.shield_hp, amt)
		dst.shield_hp -= absorbed
		amt -= absorbed
		dst.st["blocked"] += absorbed
		if dst.shield_hp <= 0.0:
			dst.remove_status("shield")
			vfx.burst(dst.global_position + Vector3(0, 1, 0), Color("9fd8ff"), 12, 4.0, 0.4, 0.4, "shield_hex", 0.0, 180.0)
			Audio.play_at("shield_break", dst.global_position)
	dst.hp -= amt
	var shown := amt + absorbed
	# stats & assists
	if src != null:
		src.st["damage"] += amt
		dst.damagers[src.get_instance_id()] = time
		dst.st["last_hit_by"] = src
		if src.has_status("lifesteal") and not is_dot and src.team != dst.team:
			heal(src, src, amt * 0.2, {})
		if src._m("second_wind") > 0.0 and false:
			pass
	dst.st["taken"] += amt
	# réaction visuelle
	if not is_dot:
		dst.take_hit_visual(crit)
		if not tick:
			var el := String(o.get("element", "physical"))
			Audio.play_at("hit_crit" if crit else ("hit_magic" if mag else "hit_slash"), dst.global_position, -6.0 if not crit else -2.0)
			if crit:
				vfx.hit_fx(dst.global_position, el, true, 1.2)
				vfx.shake(0.18)
				Game.postfx_pulse(0.006, Color(1, 1, 1, 0.0), 0.15)
	# knockback
	var kb: float = float(o.get("kb", 0.0))
	if kb > 0.0 and not is_dot and dst.forced.is_empty() and dst.kind != "boss" and dst.alive and not dst.is_summon:
		var kd: Vector3 = o.get("kb_dir", Vector3.ZERO)
		if kd == Vector3.ZERO and src != null:
			kd = Abilities.dir_to(src.global_position, dst.global_position)
		if kd != Vector3.ZERO:
			dst.forced = {"type": "knock", "dir": kd, "speed": kb * 3.2, "t": 0.0, "dur": 0.18, "ab": o.get("ab", {})}
	# épines
	if dst.has_status("thorns") and src != null and not is_dot and not o.get("reflected", false) and src.team != dst.team:
		deal_damage(dst, src, amt * 0.25, {"element": "physical", "reflected": true, "dot": true, "true": true})
	# nombres flottants
	var show_numbers := true
	if tick and randf() > 0.5:
		show_numbers = false
	if show_numbers and src != null or show_numbers and is_dot:
		var colr := Color("ffffff")
		if src != null and src.team == dst.team:
			colr = Color("ffb0b0")
		elif crit:
			colr = Color("ffd23a")
		elif is_dot:
			colr = Data.elem_color(String(o.get("element", "physical"))).lightened(0.2)
		elif String(o.get("element", "physical")) != "physical":
			colr = Data.elem_color(String(o.get("element", "physical"))).lightened(0.5)
		var sz := 0.8 + clampf(shown / 160.0, 0.0, 0.8) + (0.4 if crit else 0.0)
		if tick or is_dot:
			sz *= 0.75
		vfx.float_text(dst.global_position + Vector3(0, dst.model.height() + 0.1, 0), str(int(round(shown))) + ("!" if crit else ""), colr, sz)
	if dst.hp <= 0.0:
		dst.die(src)
	return amt

func heal(src: Fighter, dst: Fighter, amount: float, o: Dictionary) -> float:
	if dst == null or not dst.alive:
		return 0.0
	var amt := amount
	if src != null:
		amt *= 1.0 + src._m("healing_done_perc") / 100.0
		if dst.hp_pct() < 0.5:
			amt *= 1.0 + src._m("heal_low_perc") / 100.0
	amt *= 1.0 + dst._m("healing_received_perc") / 100.0
	var before := dst.hp
	dst.hp = minf(dst.max_hp, dst.hp + amt)
	var got := dst.hp - before
	if src != null:
		src.st["healing"] += got
	if got > 1.0 and not o.get("hot", false):
		vfx.float_text(dst.global_position + Vector3(0, dst.model.height() + 0.1, 0), "+" + str(int(round(got))), Color("6aff9a"), 0.85)
		Audio.play_at("heal_chime", dst.global_position, -8.0)
	return got

func apply_status(src: Fighter, dst: Fighter, s: String, dur: float, pw: float = 1.0) -> void:
	dst.add_status(s, dur, pw, src)

func hud_event_text(t: String, c: Color) -> void:
	if hud:
		hud.add_event(t, c)

func hud_hint_status(f: Fighter, t: String) -> void:
	vfx.float_text(f.global_position + Vector3(0, f.model.height() + 0.5, 0), t, Color("bfe8ff"), 0.6, 0.9, 0.7)

func _on_fighter_died(f: Fighter, killer: Fighter) -> void:
	var assisters: Array[Fighter] = []
	for k in f.damagers:
		if time - f.damagers[k] < 6.0:
			var o: Object = instance_from_id(k)
			if o is Fighter and o != killer and (o as Fighter).team != f.team:
				assisters.append(o)
	if killer != null and killer.team != f.team and not f.is_summon:
		killer.st["kills"] += 1
		if killer._m("kill_heal") > 0.0:
			heal(killer, killer, killer.max_hp * killer._m("kill_heal") / 100.0, {})
		if killer.mods.has("kill_reset") and killer.kill_reset_cd <= 0.0:
			killer.kill_reset_cd = 8.0
			for i in killer.cds.size():
				killer.cds[i] = 0.0
	for a in assisters:
		a.st["assists"] += 1
	if not f.is_summon:
		kill_log.append({"t": round_time, "killer": killer.display_name if killer else "Tempête", "victim": f.display_name, "round": round_no})
		hud.add_kill_feed(killer, f)
		vfx.shake(0.3)
		Audio.play("kill_ding", -6.0)
		if state == State.FIGHTING:
			Engine.time_scale = 0.4
			slowmo_t = 0.18

func _apply_speed() -> void:
	var sp := 1.0
	match speed_mode:
		1: sp = 2.0
		2: sp = 3.0
	Engine.time_scale = sp

func cycle_speed() -> void:
	speed_mode = (speed_mode + 1) % 3
	_apply_speed()
	hud.show_speed(speed_mode)

# ----------------------------------------------------------------------------------------------
# Entrées joueur
# ----------------------------------------------------------------------------------------------
func _mouse_ground_point() -> Vector3:
	var mp := get_viewport().get_mouse_position()
	var ro := camera.project_ray_origin(mp)
	var rd := camera.project_ray_normal(mp)
	if absf(rd.y) < 0.0001:
		return player_aim_pt
	var t := -ro.y / rd.y
	return ro + rd * t

func player_aim(f: Fighter) -> Vector3:
	return player_aim_pt

func player_input(f: Fighter, dt: float) -> void:
	var mv := Vector2(Input.get_axis("move_left", "move_right"), Input.get_axis("move_up", "move_down"))
	if mv.length() > 0.12:
		f.move_input = Vector3(mv.x, 0, mv.y).limit_length(1.0)
	# visée
	var joy_aim := Vector2(Input.get_joy_axis(0, JOY_AXIS_RIGHT_X), Input.get_joy_axis(0, JOY_AXIS_RIGHT_Y))
	if joy_aim.length() > Settings.gf("controller_aim_deadzone") + 0.1:
		player_aim_pt = f.global_position + Vector3(joy_aim.x, 0, joy_aim.y).normalized() * 9.0
	else:
		var m := _mouse_ground_point()
		if Input.get_last_mouse_velocity().length() > 0.0 or player_aim_pt == Vector3.ZERO:
			player_aim_pt = m
	var aim := player_aim_pt
	if aim.distance_to(f.global_position) < 0.5:
		aim = f.global_position + f.facing_dir * 3.0
	# visée assistée : cible la plus proche du curseur
	var tgt: Fighter = null
	var bd := 3.0
	for e in fighters:
		if e.alive and e != f:
			var d := Abilities.flat(e.global_position - aim).length()
			if d < bd:
				bd = d
				tgt = e
	var enemy_tgt: Fighter = tgt if (tgt != null and tgt.team != f.team) else null
	var any_tgt: Fighter = tgt
	# file d'attente d'entrées (0,35 s) pour ne pas perdre un appui pendant une animation
	if Input.is_action_just_pressed("dash"):
		f.input_buf = {"slot": 1, "aim": aim if f.move_input.length() < 0.2 else f.global_position + f.move_input * 5.0, "tgt": null, "t": 0.35}
	for i in 4:
		var act := "ability_%d" % (i + 1)
		if Input.is_action_just_pressed(act):
			var slot := 2 + i
			if slot < f.kit.size():
				var ab := f.kit[slot]
				var t2: Fighter = any_tgt
				if String(ab.get("arch", "")) in ["heal", "heal_hot", "heal_chain", "shield"]:
					t2 = tgt if (tgt != null and tgt.team == f.team) else null
				f.input_buf = {"slot": slot, "aim": aim, "tgt": t2, "t": 0.35}
	if not f.input_buf.is_empty():
		f.input_buf["t"] -= dt
		if f.input_buf["t"] <= 0.0:
			f.input_buf = {}
		else:
			var bt: Variant = f.input_buf.get("tgt")
			var tg2: Fighter = bt if (bt != null and is_instance_valid(bt)) else null
			if f.try_cast(int(f.input_buf["slot"]), f.input_buf["aim"] if int(f.input_buf["slot"]) == 1 else aim, tg2):
				f.input_buf = {}
			elif not f.cast.is_empty() and int(f.input_buf["slot"]) > 0 and f.ability_ready(int(f.input_buf["slot"])) == false and f.cds[int(f.input_buf["slot"])] > 0.0:
				f.input_buf = {}
	if Input.is_action_pressed("attack") and f.input_buf.is_empty():
		f.try_cast(0, aim, enemy_tgt)
	if dt > 0.0:
		pass

func _handle_global_input(dt: float) -> void:
	if Input.is_action_just_pressed("pause") and state != State.MATCH_END:
		hud.toggle_pause()
	if Input.is_action_just_pressed("speed_cycle"):
		cycle_speed()
	if Input.is_action_just_pressed("toggle_hud"):
		hud.visible = not hud.visible
	if Input.is_action_just_pressed("switch_fighter") and allow_control:
		var mine := _team_fighters(int(config.get("player_team", 0)))
		var alive_mine: Array[Fighter] = []
		for m in mine:
			if m.alive:
				alive_mine.append(m)
		if not alive_mine.is_empty():
			fighter_cycle_idx = (fighter_cycle_idx + 1) % alive_mine.size()
			take_control(alive_mine[fighter_cycle_idx], 0)
	for ti in 4:
		if Input.is_action_just_pressed("tactic_%d" % (ti + 1)) and allow_control and state == State.FIGHTING:
			_quick_tactic(ti)
	if Input.is_action_just_pressed("zoom_in"):
		zoom_mult = clampf(zoom_mult - 0.08, 0.6, 1.4)
	if Input.is_action_just_pressed("zoom_out"):
		zoom_mult = clampf(zoom_mult + 0.08, 0.6, 1.4)
	# si le contrôlé meurt : bascule automatique vers un allié vivant
	if allow_control and state == State.FIGHTING and controlled_fighter() == null and not controlled.is_empty():
		var mine2 := _team_fighters(int(config.get("player_team", 0)))
		for m in mine2:
			if m.alive:
				take_control(m, 0)
				break

## Ordres tactiques rapides F1-F4 appliqués aux alliés non contrôlés
func _quick_tactic(idx: int) -> void:
	var pt := int(config.get("player_team", 0))
	var labels := ["Tous à l'attaque !", "Repli défensif", "Focus : cible la plus faible", "Ordres neutres"]
	for f in _team_fighters(pt):
		if f.player_index >= 0:
			continue
		var t: Dictionary = f.tactics
		match idx:
			0:
				t["aggression"] = minf(float(f.spec.get("tactics", {}).get("aggression", 0.6)) + 0.3, 1.0)
				t["distance"] = 0.85
			1:
				t["aggression"] = maxf(float(f.spec.get("tactics", {}).get("aggression", 0.6)) - 0.3, 0.05)
				t["distance"] = 1.25
			2:
				t["target_priority"] = "lowest_health"
			3:
				var base: Dictionary = f.spec.get("tactics", {})
				t["aggression"] = base.get("aggression", 0.6)
				t["distance"] = base.get("distance", 1.0)
				t["target_priority"] = base.get("target_priority", "nearest")
	hud.add_event(labels[idx], UI.GOLD)
	Audio.ui("ui_notification")

func _update_spectator_click(dt: float) -> void:
	spectator_click_cd -= dt
	if not allow_control or spectator_click_cd > 0.0:
		return
	if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and controlled_fighter() == null:
		var p := _mouse_ground_point()
		var best: Fighter = null
		var bd := 2.5
		for f in _team_fighters(int(config.get("player_team", 0))):
			if f.alive:
				var d := Abilities.flat(f.global_position - p).length()
				if d < bd:
					bd = d
					best = f
		if best:
			take_control(best, 0)
			spectator_click_cd = 0.3

# ----------------------------------------------------------------------------------------------
# Caméra
# ----------------------------------------------------------------------------------------------
func _update_camera(dt: float) -> void:
	var pts: Array[Vector3] = []
	for f in fighters:
		if f.alive and not f.is_summon:
			pts.append(f.global_position)
	var center := Vector3.ZERO
	var spread := 14.0
	if not pts.is_empty():
		for p in pts:
			center += p
		center /= pts.size()
		var mx := 0.0
		for p in pts:
			mx = maxf(mx, Abilities.flat(p - center).length())
		spread = maxf(mx, 8.0)
	var cf := controlled_fighter()
	var fit_h := 24.0
	if not pts.is_empty():
		var minp := Vector3(1e9, 0, 1e9)
		var maxp := Vector3(-1e9, 0, -1e9)
		for p in pts:
			minp.x = minf(minp.x, p.x)
			minp.z = minf(minp.z, p.z)
			maxp.x = maxf(maxp.x, p.x)
			maxp.z = maxf(maxp.z, p.z)
		var vs := get_viewport().get_visible_rect().size
		var aspect := vs.x / maxf(vs.y, 1.0)
		var vfov := deg_to_rad(camera.fov)
		var tv := tan(vfov * 0.5)
		var th := tv * aspect
		center = (minp + maxp) * 0.5
		var hx := (maxp.x - minp.x) * 0.5 + 5.5
		var hz := (maxp.z - minp.z) * 0.5 + 5.0
		var dist_need := maxf(hx / th, hz * sin(cam_pitch) / tv)
		fit_h = clampf(dist_need * sin(cam_pitch), 15.5, 38.0)
		if cf and state == State.FIGHTING:
			fit_h = minf(fit_h, 26.0)
	if cf and state == State.FIGHTING:
		center = center.lerp(cf.global_position, 0.4)
		var ahead := (player_aim_pt - cf.global_position)
		ahead.y = 0
		center += ahead.limit_length(8.0) * Settings.gf("aim_lookahead_close") * 0.8
	if arena.is_club:
		fit_h = 30.0
	var target_h := fit_h * zoom_mult
	var intro_u := 0.0
	if state == State.INTRO:
		intro_u = clampf(state_t / 2.4, 0.0, 1.0)
		var a := TAU * 0.0 + (1.0 - ease(intro_u, 0.3)) * 0.9
		center = center.lerp(Vector3(sin(a) * 6.0, 0, 0), 1.0 - ease(intro_u, 0.3))
		target_h = lerpf(fit_h * 0.7, fit_h, ease(intro_u, 0.3))
	cam_center = cam_center.lerp(center, 1.0 - exp(-dt * 4.0))
	cam_height = lerpf(cam_height, target_h, 1.0 - exp(-dt * 2.2))
	var yaw_off := 0.0
	if state == State.INTRO:
		yaw_off = (1.0 - ease(intro_u, 0.3)) * 0.8
	var pitch := cam_pitch
	var dist := cam_height / sin(pitch)
	var off := Vector3(sin(yaw_off) * cos(pitch), sin(pitch), cos(yaw_off) * cos(pitch)) * dist
	var target_pos := cam_center + off
	# tremblement
	var sh := vfx.shake_amount
	if sh > 0.001:
		target_pos += Vector3(randf_range(-1, 1), randf_range(-1, 1), randf_range(-1, 1)) * sh * 0.55
		vfx.shake_amount = maxf(0.0, sh - dt * 2.2)
	camera.global_position = target_pos
	camera.look_at(cam_center + Vector3(0, 0.0, 0), Vector3.UP)
	if sh > 0.001:
		camera.rotation.z += randf_range(-1, 1) * sh * 0.01
