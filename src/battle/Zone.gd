class_name Zone
extends Node3D
## Zone au sol : sorts ciblés différés (télégraphie → détonation → champ persistant) et pièges.

var battle: Battle
var owner_f: Fighter
var team: int = 0
var ab: Dictionary = {}
var mode: String = "ground"      # ground | trap
var radius: float = 3.5
var delay: float = 0.8
var elapsed: float = 0.0
var detonated: bool = false
var linger: float = 0.0
var linger_t: float = 0.0
var tick_t: float = 0.0
var armed: bool = false
var life: float = 20.0
var telegraph: MeshInstance3D
var tmat: ShaderMaterial
var element: String = "physical"
var color: Color = Color.WHITE
var field_fx: CPUParticles3D

const LINGER_RX := "blizzard|storm|rain|minefield|volcanic|gravity_well|tornado|huracan|holy_fire|eruption|sanctuary|ice_pillar|firestorm|blood_storm|reap_the_void|stasis|haunt|apocalypse|armageddon|megameteor|meteor_rain"

func _make_telegraph(col: Color) -> void:
	telegraph = MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(radius * 2.1, radius * 2.1)
	q.orientation = PlaneMesh.FACE_Y
	telegraph.mesh = q
	tmat = ShaderMaterial.new()
	tmat.shader = load("res://src/shaders/telegraph.gdshader")
	tmat.set_shader_parameter("color", col)
	tmat.set_shader_parameter("progress", 0.0)
	var rune_path := "res://assets/textures/vfx/rune_circle_%d.png" % (absi(hash(String(ab.get("id", "")))) % 6)
	if ResourceLoader.exists(rune_path):
		tmat.set_shader_parameter("rune_tex", load(rune_path))
		tmat.set_shader_parameter("use_rune", true)
	telegraph.material_override = tmat
	telegraph.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(telegraph)
	telegraph.position = Vector3(0, 0.07, 0)

func setup_ground(f: Fighter, a: Dictionary, center: Vector3, total_delay: float) -> void:
	owner_f = f
	battle = f.battle
	team = f.team
	ab = a
	mode = "ground"
	radius = float(ab.get("radius", 3.5))
	delay = maxf(total_delay, 0.2)
	element = String(ab.get("element", "physical"))
	color = Data.elem_color(element)
	global_position = Vector3(center.x, 0, center.z)
	linger = 3.5 if String(ab.get("id", "")).to_lower().contains("storm") or _matches_linger() else 0.0
	var tc := color.lerp(Color(1, 0.25, 0.2), 0.45) if f.team != 0 else color
	_make_telegraph(tc * 1.4)
	battle.zones.append(self)

func _matches_linger() -> bool:
	var rx := RegEx.new()
	rx.compile(LINGER_RX)
	return rx.search(String(ab.get("id", "")).to_lower()) != null

func setup_trap(f: Fighter, a: Dictionary, center: Vector3) -> void:
	owner_f = f
	battle = f.battle
	team = f.team
	ab = a
	mode = "trap"
	radius = float(ab.get("radius", 2.4))
	delay = 0.7
	life = float(ab.get("dur", 20.0))
	element = String(ab.get("element", "physical"))
	color = Data.elem_color(element)
	global_position = Vector3(center.x, 0, center.z)
	_make_telegraph(color * 0.7)
	battle.zones.append(self)
	battle.vfx.burst(global_position + Vector3(0, 0.1, 0), color, 6, 2.0, 0.4, 0.3, "dust_puff", 0.0, 80.0)

func time_to_detonate() -> float:
	if detonated:
		return -1.0
	return maxf(delay - elapsed, 0.0)

func _exit_tree() -> void:
	if battle:
		battle.zones.erase(self)

func _process(dt: float) -> void:
	elapsed += dt
	if tmat:
		tmat.set_shader_parameter("time_s", elapsed)
	if mode == "ground":
		if not detonated:
			if tmat:
				tmat.set_shader_parameter("progress", clampf(elapsed / delay, 0.0, 1.0))
			if elapsed >= delay:
				_detonate()
		else:
			linger_t += dt
			tick_t += dt
			if linger > 0.0:
				if tick_t >= 0.5:
					tick_t -= 0.5
					_tick_damage()
				if linger_t >= linger:
					_end()
			else:
				if linger_t > 0.6:
					_end()
	else:
		life -= dt
		if not armed and elapsed >= delay:
			armed = true
			if tmat:
				tmat.set_shader_parameter("progress", 1.0)
				tmat.set_shader_parameter("intensity", 0.45)
		if armed and not detonated:
			for e in battle.fighters:
				if e.alive and e.team != team:
					if Abilities.flat(e.global_position - global_position).length() < radius * 0.7 + e.radius:
						_detonate()
						break
		if life <= 0.0 or (detonated and linger_t > 0.5):
			_end()
		if detonated:
			linger_t += dt

func _detonate() -> void:
	detonated = true
	var amt := owner_f.power * float(ab.get("dmg", 2.0)) if owner_f else 50.0
	for e in Abilities.enemies_in_circle(owner_f, global_position, radius):
		battle.deal_damage(owner_f, e, amt, Abilities.hit_opts(owner_f, ab, {"aoe": true, "kb": 3.5, "kb_dir": Abilities.dir_to(global_position, e.global_position)}))
		Abilities.apply_statuses(owner_f, e, ab)
	for a in Abilities.allies_in_circle(owner_f, global_position, radius, true):
		battle.deal_damage(owner_f, a, amt, Abilities.hit_opts(owner_f, ab, {"aoe": true, "ff": true}))
	battle.vfx.element_burst(global_position, element, radius)
	Audio.play_at("explosion_small" if radius < 4.0 else "explosion_big", global_position, -2.0)
	if tmat:
		tmat.set_shader_parameter("progress", 1.0)
		tmat.set_shader_parameter("intensity", 2.5)
		var tw := create_tween()
		tw.tween_method(func(v: float): if tmat: tmat.set_shader_parameter("intensity", v), 2.5, 0.0, 0.5)
	if linger > 0.0:
		field_fx = battle.vfx.burst(global_position + Vector3(0, 0.3, 0), color, 40, 3.0, 1.0, 0.7, "soft_glow", 1.0, 40.0)
		field_fx.one_shot = false
		field_fx.explosiveness = 0.0
		field_fx.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
		field_fx.emission_sphere_radius = radius * 0.8
		field_fx.amount = 36
		field_fx.lifetime = 1.1
		field_fx.emitting = true
		for ch in field_fx.get_children():
			if ch is Timer:
				ch.queue_free()

func _tick_damage() -> void:
	var amt := owner_f.power * float(ab.get("dmg", 2.0)) * 0.22 if owner_f else 20.0
	for e in Abilities.enemies_in_circle(owner_f, global_position, radius):
		battle.deal_damage(owner_f, e, amt, Abilities.hit_opts(owner_f, ab, {"tick": true, "aoe": true}))
		e.add_status("slow", 0.8, 0.6, owner_f)
	for a in Abilities.allies_in_circle(owner_f, global_position, radius, true):
		battle.deal_damage(owner_f, a, amt, Abilities.hit_opts(owner_f, ab, {"tick": true, "aoe": true, "ff": true}))

func _end() -> void:
	if field_fx and is_instance_valid(field_fx):
		field_fx.emitting = false
		field_fx.get_tree().create_timer(1.2).timeout.connect(field_fx.queue_free)
	queue_free()
