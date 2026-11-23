class_name Projectile
extends Node3D
## Projectile générique (flèches, orbes, lames, crochets…) piloté par la compétence.

var battle: Battle
var owner_f: Fighter
var ab: Dictionary = {}
var dir: Vector3 = Vector3.FORWARD
var speed: float = 20.0
var max_dist: float = 16.0
var hit_radius: float = 0.45
var travelled: float = 0.0
var pierce_left: int = 0
var homing: float = 0.0
var explode_r: float = 0.0
var bounces_left: int = 0
var returning: bool = false
var returning_active: bool = false
var is_hook: bool = false
var hit_set: Array = []
var color: Color = Color.WHITE
var element: String = "physical"
var target: Fighter = null
var visual: Node3D
var light: OmniLight3D
var style: String = "orb"
var spin: float = 0.0
var dead: bool = false
var start_pos: Vector3

func setup(p: Dictionary) -> void:
	owner_f = p["owner"]
	battle = owner_f.battle
	ab = p["ab"]
	dir = Abilities.flat(p["dir"]).normalized()
	speed = p["speed"]
	max_dist = p["range"]
	hit_radius = p["radius"]
	pierce_left = p["pierce"]
	homing = p["homing"]
	explode_r = p["explode"]
	bounces_left = p["bounces"]
	returning = p["returning"]
	is_hook = p.get("hook", false)
	target = p.get("target") if (p.get("target") != null and is_instance_valid(p.get("target"))) else null
	element = String(ab.get("element", "physical"))
	color = Data.elem_color(element)
	global_position = p["pos"]
	start_pos = global_position
	var id := String(ab.get("id", "")).to_lower()
	if element == "physical" and (id.contains("arrow") or id.contains("shot") or id.contains("shoot") or id.contains("bolt") or id.contains("javalin") or id.contains("lance") or id.contains("impal") or id.contains("nail") or id.contains("stake") or id.contains("spear") or id.contains("slingshot") or id.contains("pew") or id.contains("volley")):
		style = "arrow"
	elif id.contains("axe") or id.contains("knife") or id.contains("blade") or id.contains("shuriken") or id.contains("spinning") or id.contains("guillotine") or id.contains("hammer_throw") or id.contains("shield_throw") or id.contains("boomerang"):
		style = "spinner"
	elif id.contains("arrow") or id.contains("javalin") or id.contains("lance"):
		style = "arrow"
	if is_hook:
		style = "hook"
	_build_visual()
	look_at(global_position + dir, Vector3.UP)

func _build_visual() -> void:
	match style:
		"arrow":
			var mi := MeshInstance3D.new()
			var bm := BoxMesh.new()
			bm.size = Vector3(0.06, 0.06, 0.75)
			mi.mesh = bm
			var m := StandardMaterial3D.new()
			m.albedo_color = Color(0.85, 0.8, 0.7).lerp(color, 0.35 if element != "physical" else 0.0)
			m.emission_enabled = element != "physical"
			m.emission = color
			m.emission_energy_multiplier = 2.0
			m.metallic = 0.5
			mi.material_override = m
			add_child(mi)
			visual = mi
			var tr := battle.vfx.trail(self, color.lerp(Color.WHITE, 0.4), 0.2, 24, 0.25, "soft_glow")
			tr.position = Vector3(0, 0, -0.3)
		"spinner":
			var mi2 := MeshInstance3D.new()
			var bm2 := BoxMesh.new()
			bm2.size = Vector3(0.7, 0.07, 0.22)
			mi2.mesh = bm2
			var m2 := StandardMaterial3D.new()
			m2.albedo_color = Color(0.85, 0.87, 0.92)
			m2.metallic = 0.8
			m2.roughness = 0.3
			m2.emission_enabled = true
			m2.emission = color
			m2.emission_energy_multiplier = 1.2
			mi2.material_override = m2
			add_child(mi2)
			visual = mi2
			battle.vfx.trail(self, color, 0.35, 22, 0.3, "soft_glow")
		"hook":
			var mi3 := MeshInstance3D.new()
			var cm := CylinderMesh.new()
			cm.top_radius = 0.0
			cm.bottom_radius = 0.14
			cm.height = 0.5
			mi3.mesh = cm
			mi3.rotation_degrees = Vector3(90, 0, 0)
			var m3 := StandardMaterial3D.new()
			m3.albedo_color = Color(0.7, 0.7, 0.75)
			m3.metallic = 0.9
			mi3.material_override = m3
			add_child(mi3)
			visual = mi3
		_:
			var g := battle.vfx.sphere_glow(color, 0.45 + hit_radius * 0.5)
			add_child(g)
			visual = g
			var tr2 := battle.vfx.trail(self, color, 0.5 + hit_radius * 0.4, 30, 0.35, "soft_glow")
			battle.vfx.trail(self, Color.WHITE, 0.25, 12, 0.18, "spark_star4")
			tr2.position = Vector3.ZERO
			if battle.vfx.active_lights < battle.vfx.max_lights:
				battle.vfx.active_lights += 1
				light = OmniLight3D.new()
				light.light_color = color
				light.light_energy = 1.8
				light.omni_range = 4.5
				light.shadow_enabled = false
				add_child(light)

func _exit_tree() -> void:
	if light and battle and battle.vfx:
		battle.vfx.active_lights = maxi(battle.vfx.active_lights - 1, 0)

func _process(dt: float) -> void:
	if dead:
		return
	if battle.state == Battle.State.ROUND_END and false:
		return
	# guidage
	if homing > 0.0:
		var t := target
		if t == null or not t.alive:
			t = _nearest_enemy()
			target = t
		if t:
			var want := Abilities.dir_to(global_position, t.global_position + Vector3(0, 0.0, 0))
			dir = dir.slerp(want, clampf(homing * dt * 5.0, 0.0, 1.0)).normalized()
	if returning and not returning_active and travelled >= max_dist * 0.95:
		returning_active = true
		hit_set.clear()
	if returning_active:
		var back := Abilities.dir_to(global_position, owner_f.global_position + Vector3(0, 1, 0))
		dir = dir.slerp(back, clampf(dt * 9.0, 0.0, 1.0)).normalized()
		if Abilities.flat(owner_f.global_position - global_position).length() < 1.0:
			_remove()
			return
	var step_total := speed * dt
	var nsteps := maxi(int(ceil(step_total / 0.45)), 1)
	var sub := step_total / nsteps
	for i in nsteps:
		var prev := global_position
		global_position += dir * sub
		travelled += sub
		if visual and style == "spinner":
			spin += dt * 25.0 / nsteps
			visual.rotation.y = spin
		# obstacles
		var hit_obs: Variant = battle.arena.segment_hits_obstacle(prev, global_position, hit_radius * 0.5)
		if hit_obs != null:
			_impact(global_position, null)
			return
		if not battle.arena.inside(global_position, -2.0):
			_impact(global_position, null)
			return
		# ennemis
		for e in battle.fighters:
			if not e.alive or e.team == owner_f.team or e in hit_set:
				continue
			if Abilities.flat(e.global_position - global_position).length() <= hit_radius + e.radius * 0.9:
				if e.has_status("invisible") and e != target:
					continue
				if _on_hit(e):
					return
		if travelled >= max_dist and not returning:
			_impact(global_position, null)
			return
	if returning and travelled > max_dist * 2.2:
		_remove()

func _nearest_enemy() -> Fighter:
	var best: Fighter = null
	var bd := 12.0
	for e in battle.fighters:
		if e.alive and e.team != owner_f.team:
			var d := Abilities.flat(e.global_position - global_position).length()
			if d < bd:
				bd = d
				best = e
	return best

func _on_hit(e: Fighter) -> bool:
	hit_set.append(e)
	var dist_scale := 1.0
	var dist_bonus := owner_f._m("distance_dmg") / 100.0
	if dist_bonus > 0.0:
		dist_scale += dist_bonus * clampf(travelled / (max_dist * 0.75), 0.0, 1.0)
	var amt := owner_f.power * float(ab.get("dmg", 1.0)) * dist_scale
	var opts := Abilities.hit_opts(owner_f, ab, {"kb": 1.2 if not bool(ab.get("basic", false)) else 0.4, "kb_dir": dir, "proj": true})
	battle.deal_damage(owner_f, e, amt, opts)
	Abilities.apply_statuses(owner_f, e, ab)
	battle.vfx.hit_fx(e.global_position, element, false, 1.0)
	if is_hook:
		var to := owner_f.global_position + Abilities.dir_to(owner_f.global_position, e.global_position) * (owner_f.radius + e.radius + 0.3)
		if e.kind != "boss":
			e.forced = {"type": "pulled", "to": to, "speed": 34.0, "t": 0.0, "dur": 0.6, "ab": ab}
		_remove()
		return true
	if explode_r > 0.0:
		_explode(global_position, e)
	if bounces_left > 0:
		bounces_left -= 1
		var nxt: Fighter = null
		var bd := 11.0
		for o in battle.fighters:
			if o.alive and o.team != owner_f.team and not (o in hit_set):
				var d := Abilities.flat(o.global_position - global_position).length()
				if d < bd:
					bd = d
					nxt = o
		if nxt:
			dir = Abilities.dir_to(global_position, nxt.global_position)
			travelled = maxf(0.0, travelled - 6.0)
			return false
	if pierce_left > 0:
		pierce_left -= 1
		return false
	if returning:
		return false
	_impact(global_position, e)
	return true

func _explode(pos: Vector3, direct: Fighter) -> void:
	for o in Abilities.enemies_in_circle(owner_f, pos, explode_r):
		if o != direct:
			battle.deal_damage(owner_f, o, owner_f.power * float(ab.get("dmg", 1.0)) * 0.7, Abilities.hit_opts(owner_f, ab, {"aoe": true, "kb": 2.0, "kb_dir": Abilities.dir_to(pos, o.global_position)}))
			Abilities.apply_statuses(owner_f, o, ab, 0.7)
	for a in Abilities.allies_in_circle(owner_f, pos, explode_r, true):
		battle.deal_damage(owner_f, a, owner_f.power * float(ab.get("dmg", 1.0)) * 0.7, Abilities.hit_opts(owner_f, ab, {"aoe": true, "ff": true}))
	battle.vfx.element_burst(pos, element, explode_r)

func _impact(pos: Vector3, e: Fighter) -> void:
	if dead:
		return
	if e == null:
		battle.vfx.burst(pos + Vector3(0, 0.1, 0), color, 6, 3.0, 0.3, 0.25, "spark_star4", -2.0, 90.0)
		if explode_r > 0.0:
			_explode(pos, null)
	_remove()

func _remove() -> void:
	dead = true
	queue_free()
