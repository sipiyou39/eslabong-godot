class_name Arena
extends Node3D
## Arène : décor 3D (GLB Blender ou repli procédural), éclairage/ambiance par thème, bornes, obstacles, tempête rétrécissante.

const THEMES := {
	"colosseum": {"file": "arena_colosseum.glb", "sun": Color("ffe3c0"), "sun_e": 1.55, "sun_rot": Vector3(-48, -38, 0),
		"sky_top": Color("2a2450"), "sky_hor": Color("e8956a"), "ambient": Color("9a90b4"), "ambient_e": 0.62,
		"fog": Color("c9a584"), "fog_d": 0.0022, "torch": Color("ff9a40"), "ember": Color("ffb060"), "ground_a": Color("b8955f"), "ground_b": Color("8f6e42"), "line": Color("f0d890"), "name": "Colisée de Sable"},
	"frost": {"file": "arena_frost.glb", "sun": Color("c8e0ff"), "sun_e": 1.5, "sun_rot": Vector3(-55, 30, 0),
		"sky_top": Color("14224a"), "sky_hor": Color("8fb8e0"), "ambient": Color("7a9ac8"), "ambient_e": 0.7,
		"fog": Color("9cc4e8"), "fog_d": 0.006, "torch": Color("6ad0ff"), "ember": Color("d8f4ff"), "ground_a": Color("c8dcec"), "ground_b": Color("98b4d0"), "line": Color("eaffff"), "name": "Forteresse de Glace"},
	"forge": {"file": "arena_forge.glb", "sun": Color("ff9060"), "sun_e": 1.3, "sun_rot": Vector3(-50, -20, 0),
		"sky_top": Color("200808"), "sky_hor": Color("a83a18"), "ambient": Color("8a4a3a"), "ambient_e": 0.6,
		"fog": Color("6a2a18"), "fog_d": 0.008, "torch": Color("ff5a20"), "ember": Color("ff8a30"), "ground_a": Color("3a2e2c"), "ground_b": Color("241c1c"), "line": Color("ff6a2a"), "name": "Forge Volcanique"},
	"irongate": {"file": "arena_irongate.glb", "sun": Color("ffe0b8"), "sun_e": 1.4, "sun_rot": Vector3(-45, 55, 0),
		"sky_top": Color("1c2238"), "sky_hor": Color("a07a68"), "ambient": Color("707a8a"), "ambient_e": 0.6,
		"fog": Color("8a8090"), "fog_d": 0.006, "torch": Color("ffb060"), "ember": Color("ffc880"), "ground_a": Color("8a8478"), "ground_b": Color("625e58"), "line": Color("c8c0a8"), "name": "Porte de Fer"},
	"thunder": {"file": "arena_thunder.glb", "sun": Color("a8a0ff"), "sun_e": 1.2, "sun_rot": Vector3(-60, 10, 0),
		"sky_top": Color("0a0820"), "sky_hor": Color("4a3a8a"), "ambient": Color("5a50a0"), "ambient_e": 0.8,
		"fog": Color("3a2e70"), "fog_d": 0.01, "torch": Color("b080ff"), "ember": Color("c8a0ff"), "ground_a": Color("3a3458"), "ground_b": Color("262240"), "line": Color("8ad0ff"), "name": "Arène Chaos Thunder"},
	"club": {"file": "club_hall.glb", "sun": Color("ffd0a0"), "sun_e": 1.2, "sun_rot": Vector3(-35, -30, 0),
		"sky_top": Color("1a1428"), "sky_hor": Color("6a4a3a"), "ambient": Color("8a7060"), "ambient_e": 0.7,
		"fog": Color("6a5040"), "fog_d": 0.005, "torch": Color("ff9a40"), "ember": Color("ffb060"), "ground_a": Color("8a7458"), "ground_b": Color("6a5a44"), "line": Color("d8b878"), "name": "Quartier Général"},
}

var theme_id: String = "colosseum"
var theme: Dictionary = {}
var hx: float = 26.0
var hz: float = 16.0
var corner_r: float = 5.0
var obstacles: Array[Dictionary] = []   # {pos: Vector3, r: float}
var torches: Array[Dictionary] = []
var shrink: float = 1.0                  # 1 = taille complète ; <1 = tempête
var sun: DirectionalLight3D
var world_env: WorldEnvironment
var env: Environment
var vfx: Vfx
var _torch_lights: Array[OmniLight3D] = []
var _flicker_t: float = 0.0
var storm_walls: Array[MeshInstance3D] = []
var storm_mat: ShaderMaterial
var loaded_glb: bool = false
var lightning_timer: float = 4.0
var is_club: bool = false

func setup(id: String, v: Vfx, with_lighting: bool = true) -> void:
	theme_id = id if (THEMES.has(id) or Data.extra_arena_themes.has(id)) else "colosseum"
	theme = THEMES[theme_id] if THEMES.has(theme_id) else Data.extra_arena_themes[theme_id]
	vfx = v
	is_club = theme_id == "club"
	var lay: Dictionary = Data.arena_layout
	if not lay.is_empty():
		hx = float(lay["half_extents"][0]) - 1.2
		hz = float(lay["half_extents"][1]) - 2.0
		corner_r = float(lay.get("corner_radius", 5.0))
		for o in lay["obstacles"]:
			obstacles.append({"pos": Vector3(o["x"], 0, o["z"]), "r": float(o["r"])})
	_build_scenery()
	if with_lighting:
		_build_lighting()
	if not is_club:
		_build_storm()

# ----------------------------------------------------------------------------------------------
func _build_scenery() -> void:
	var path := "res://assets/models/arenas/" + String(theme["file"])
	if ResourceLoader.exists(path):
		var ps: Variant = load(path)
		if ps is PackedScene:
			var inst: Node = (ps as PackedScene).instantiate()
			add_child(inst)
			loaded_glb = true
			_process_glb(inst)
			return
	_build_fallback()

func _process_glb(root: Node) -> void:
	# lumières de torches à partir des empties Torch_*
	var found := 0
	for n in root.find_children("Torch_*", "Node3D", true, false):
		var nd := n as Node3D
		torches.append({"pos": nd.global_position})
		found += 1
	if found == 0:
		_default_torches()
	# les matériaux émissifs du GLB reçoivent un peu plus d'éclat
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		for s in m.get_surface_override_material_count():
			var mat := m.mesh.surface_get_material(s)
			if mat is StandardMaterial3D and (mat as StandardMaterial3D).emission_enabled:
				var dup: StandardMaterial3D = (mat as StandardMaterial3D).duplicate()
				dup.emission_energy_multiplier = maxf(dup.emission_energy_multiplier, 1.0) * 2.2
				m.set_surface_override_material(s, dup)

func _default_torches() -> void:
	for t in Data.arena_layout.get("torches", []):
		torches.append({"pos": Vector3(t["x"], 2.4, t["z"])})

func _build_fallback() -> void:
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2((hx + 14) * 2, (hz + 14) * 2)
	pm.subdivide_width = 1
	pm.subdivide_depth = 1
	ground.mesh = pm
	var gm := ShaderMaterial.new()
	gm.shader = load("res://src/shaders/ground_fallback.gdshader")
	gm.set_shader_parameter("base_a", theme["ground_a"])
	gm.set_shader_parameter("base_b", theme["ground_b"])
	gm.set_shader_parameter("line_color", theme["line"])
	gm.set_shader_parameter("half_extents", Vector2(hx, hz))
	ground.material_override = gm
	ground.name = "Ground"
	add_child(ground)
	var stone := StandardMaterial3D.new()
	stone.albedo_color = Color(theme["ground_b"]).lerp(Color(0.5, 0.5, 0.55), 0.4)
	stone.roughness = 0.9
	# murs d'enceinte
	var wall_h := 3.2
	for side in 4:
		var w := MeshInstance3D.new()
		var b := BoxMesh.new()
		var horiz := side < 2
		b.size = Vector3((hx + 2) * 2 if horiz else 2.0, wall_h, 2.0 if horiz else (hz + 2) * 2)
		w.mesh = b
		w.material_override = stone
		var sgn := 1.0 if side % 2 == 0 else -1.0
		w.position = Vector3(0 if horiz else sgn * (hx + 1.0), wall_h * 0.5, sgn * (hz + 1.0) if horiz else 0)
		add_child(w)
	# gradins
	for tier in 3:
		var st := MeshInstance3D.new()
		var sb := BoxMesh.new()
		sb.size = Vector3((hx + 4 + tier * 3) * 2, 1.2, (hz + 4 + tier * 3) * 2)
		st.mesh = sb
		st.position = Vector3(0, 0.6 + tier * 1.2 + wall_h * 0.5 - 1.2, 0)
		st.material_override = stone
		st.visible = false
	# piliers
	for o in obstacles:
		var pil := MeshInstance3D.new()
		var cm := CylinderMesh.new()
		cm.top_radius = o["r"] * 0.85
		cm.bottom_radius = o["r"]
		cm.height = 3.6
		cm.radial_segments = 14
		pil.mesh = cm
		pil.material_override = stone
		pil.position = o["pos"] + Vector3(0, 1.8, 0)
		add_child(pil)
	_default_torches()
	for t in torches:
		var post := MeshInstance3D.new()
		var pc := CylinderMesh.new()
		pc.top_radius = 0.1
		pc.bottom_radius = 0.14
		pc.height = 2.4
		post.mesh = pc
		post.material_override = stone
		post.position = Vector3(t["pos"].x, 1.2, t["pos"].z)
		add_child(post)

# ----------------------------------------------------------------------------------------------
func _build_lighting() -> void:
	env = Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var psm := ProceduralSkyMaterial.new()
	psm.sky_top_color = theme["sky_top"]
	psm.sky_horizon_color = theme["sky_hor"]
	psm.ground_bottom_color = Color(theme["sky_top"]).darkened(0.4)
	psm.ground_horizon_color = theme["sky_hor"]
	psm.sky_energy_multiplier = 0.9
	sky.sky_material = psm
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = theme["ambient"]
	env.ambient_light_energy = theme["ambient_e"]
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.tonemap_exposure = 0.95
	env.tonemap_white = 6.0
	var post: bool = Settings.gb("postfx_enabled")
	env.glow_enabled = post
	env.glow_intensity = 0.7
	env.glow_strength = 1.1
	env.glow_bloom = 0.1
	env.glow_hdr_threshold = 1.15
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT
	env.set("glow_levels/2", 1.0)
	env.set("glow_levels/3", 1.0)
	env.set("glow_levels/4", 0.6)
	env.ssao_enabled = post and Settings.gb("ssao") and RenderingServer.get_current_rendering_method() == "forward_plus"
	env.ssao_radius = 1.8
	env.ssao_intensity = 2.2
	env.ssao_power = 1.6
	env.ssil_enabled = false
	env.fog_enabled = true
	env.fog_light_color = theme["fog"]
	env.fog_density = theme["fog_d"]
	env.fog_sky_affect = 0.4
	env.fog_aerial_perspective = 0.3
	if Settings.gb("volumetric_fog") and post and RenderingServer.get_current_rendering_method() == "forward_plus":
		env.volumetric_fog_enabled = true
		env.volumetric_fog_density = 0.012
		env.volumetric_fog_albedo = Color(theme["fog"]).lightened(0.2)
		env.volumetric_fog_emission = Color(theme["fog"]).darkened(0.6)
		env.volumetric_fog_emission_energy = 0.4
		env.volumetric_fog_anisotropy = 0.55
		env.volumetric_fog_length = 90.0
		env.volumetric_fog_detail_spread = 2.0
		env.volumetric_fog_temporal_reprojection_enabled = false
		env.volumetric_fog_ambient_inject = 0.3
	env.adjustment_enabled = true
	env.adjustment_brightness = 1.0
	env.adjustment_contrast = 1.1
	env.adjustment_saturation = 1.04
	world_env = WorldEnvironment.new()
	world_env.environment = env
	add_child(world_env)
	sun = DirectionalLight3D.new()
	sun.light_color = theme["sun"]
	sun.light_energy = theme["sun_e"]
	sun.rotation_degrees = theme["sun_rot"]
	sun.shadow_enabled = Settings.gi("shadows_quality") > 0
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
	sun.directional_shadow_max_distance = 70.0
	sun.shadow_blur = 1.6
	sun.shadow_bias = 0.04
	sun.light_volumetric_fog_energy = 1.0
	add_child(sun)
	# torches
	var lit := 0
	for t in torches:
		lit += 1
		var l := OmniLight3D.new()
		l.light_color = theme["torch"]
		l.light_energy = 2.2
		l.omni_range = 11.0
		l.omni_attenuation = 1.4
		l.shadow_enabled = false
		l.light_volumetric_fog_energy = 1.5
		l.visible = lit <= (6 if RenderingServer.get_current_rendering_method() != "forward_plus" else 99)
		add_child(l)
		l.global_position = t["pos"] + Vector3(0, 0.4, 0)
		_torch_lights.append(l)
		var flame := vfx.burst(t["pos"], theme["torch"], 12, 0.0, 0.9, 0.7, "flame_sprite", 0.0, 0.0) if vfx else null
		if flame:
			_make_continuous_flame(flame, t["pos"])
	if vfx and not is_club:
		vfx.ambient_embers(Vector3(0, 3, 0), Vector3(hx + 4, 3, hz + 4), theme["ember"], 70, 0.1)

func _make_continuous_flame(p: CPUParticles3D, pos: Vector3) -> void:
	p.one_shot = false
	p.explosiveness = 0.0
	p.amount = 14
	p.lifetime = 0.9
	p.spread = 12.0
	p.direction = Vector3.UP
	p.initial_velocity_min = 0.6
	p.initial_velocity_max = 1.4
	p.gravity = Vector3(0, 1.2, 0)
	p.scale_amount_min = 0.5
	p.scale_amount_max = 0.85
	var tmr: Variant = null
	for c in p.get_children():
		if c is Timer:
			tmr = c
	if tmr:
		(tmr as Timer).queue_free()
	p.emitting = true
	p.global_position = pos

func _process(dt: float) -> void:
	_flicker_t += dt
	for i in _torch_lights.size():
		var l := _torch_lights[i]
		l.light_energy = 2.2 + sin(_flicker_t * 11.0 + i * 1.7) * 0.35 + sin(_flicker_t * 23.0 + i) * 0.2
	if theme_id == "thunder" and env and not is_club:
		lightning_timer -= dt
		if lightning_timer <= 0.0:
			lightning_timer = randf_range(3.0, 7.0)
			_lightning_flash()
	_update_storm_visual()

func _lightning_flash() -> void:
	if sun == null:
		return
	var tw := create_tween()
	tw.tween_property(sun, "light_energy", 5.0, 0.04)
	tw.tween_property(sun, "light_energy", 1.0, 0.06)
	tw.tween_property(sun, "light_energy", 3.8, 0.04)
	tw.tween_property(sun, "light_energy", theme["sun_e"], 0.3)
	Audio.play("thunder_crack", -8.0)

# ----------------------------------------------------------------------------------------------
# Tempête rétrécissante
# ----------------------------------------------------------------------------------------------
func _build_storm() -> void:
	storm_mat = ShaderMaterial.new()
	var sh := Shader.new()
	sh.code = """
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled;
uniform vec4 col : source_color = vec4(0.7, 0.4, 1.0, 1.0);
uniform float strength = 0.0;
float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x), mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x), f.y); }
void fragment(){
	float t = TIME * 0.9;
	float v = n(vec2(UV.x * 24.0, UV.y * 3.0 - t)) * 0.6 + n(vec2(UV.x * 60.0 + t, UV.y * 7.0 - t * 1.7)) * 0.4;
	float edge = pow(1.0 - UV.y, 1.5);
	float a = edge * (0.25 + v * 0.9) * strength;
	ALBEDO = col.rgb * (1.0 + v);
	ALPHA = clamp(a, 0.0, 1.0);
}
"""
	storm_mat.shader = sh
	storm_mat.set_shader_parameter("col", Color(theme["torch"]).lightened(0.2))
	for i in 4:
		var mi := MeshInstance3D.new()
		var q := QuadMesh.new()
		q.size = Vector2(1, 1)
		mi.mesh = q
		mi.material_override = storm_mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(mi)
		storm_walls.append(mi)
	_update_storm_visual()

func set_storm_strength(s: float) -> void:
	if storm_mat:
		storm_mat.set_shader_parameter("strength", s)

func _update_storm_visual() -> void:
	if storm_walls.is_empty():
		return
	var ex := hx * shrink + 0.5
	var ez := hz * shrink + 0.5
	var hgt := 7.0
	# 0: +z, 1: -z, 2: +x, 3: -x
	var cfg := [
		[Vector3(0, hgt * 0.5, ez), 0.0, Vector2(ex * 2.0, hgt)],
		[Vector3(0, hgt * 0.5, -ez), PI, Vector2(ex * 2.0, hgt)],
		[Vector3(ex, hgt * 0.5, 0), PI * 0.5, Vector2(ez * 2.0, hgt)],
		[Vector3(-ex, hgt * 0.5, 0), -PI * 0.5, Vector2(ez * 2.0, hgt)],
	]
	for i in 4:
		var m := storm_walls[i]
		m.position = cfg[i][0]
		m.rotation.y = cfg[i][1]
		(m.mesh as QuadMesh).size = cfg[i][2]
		m.visible = shrink < 0.995

# ----------------------------------------------------------------------------------------------
# Géométrie de jeu
# ----------------------------------------------------------------------------------------------
func half_extents() -> Vector2:
	return Vector2(hx * shrink, hz * shrink)

func inside(p: Vector3, margin: float = 0.0) -> bool:
	var ex := hx * shrink - margin
	var ez := hz * shrink - margin
	var cr := maxf(corner_r * shrink - margin, 0.01)
	var ax := absf(p.x)
	var az := absf(p.z)
	if ax > ex or az > ez:
		return false
	var cx := ex - cr
	var cz := ez - cr
	if ax > cx and az > cz:
		return Vector2(ax - cx, az - cz).length() <= cr
	return true

func clamp_point(p: Vector3, radius: float = 0.5) -> Vector3:
	var ex := hx * shrink - radius
	var ez := hz * shrink - radius
	var cr := maxf(corner_r * shrink - radius, 0.2)
	var q := Vector3(clampf(p.x, -ex, ex), p.y, clampf(p.z, -ez, ez))
	var cx := ex - cr
	var cz := ez - cr
	var ax := absf(q.x)
	var az := absf(q.z)
	if ax > cx and az > cz:
		var d := Vector2(ax - cx, az - cz)
		if d.length() > cr:
			d = d.normalized() * cr
			q.x = signf(q.x) * (cx + d.x)
			q.z = signf(q.z) * (cz + d.y)
	return q

func push_out(p: Vector3, radius: float = 0.5) -> Vector3:
	var q := p
	for o in obstacles:
		var c: Vector3 = o["pos"]
		var d := Vector2(q.x - c.x, q.z - c.z)
		var minr: float = o["r"] + radius
		var l := d.length()
		if l < minr:
			if l < 0.001:
				d = Vector2(1, 0)
				l = 1.0
			var n := d / l
			q.x = c.x + n.x * minr
			q.z = c.z + n.y * minr
	return q

func segment_hits_obstacle(a: Vector3, b: Vector3, extra: float = 0.0) -> Variant:
	# renvoie le point d'impact (Vector3) ou null
	var best: Variant = null
	var best_t := 2.0
	var ab := Vector2(b.x - a.x, b.z - a.z)
	var len2 := ab.length_squared()
	if len2 < 0.0001:
		return null
	for o in obstacles:
		var c: Vector3 = o["pos"]
		var ac := Vector2(c.x - a.x, c.z - a.z)
		var t := clampf(ac.dot(ab) / len2, 0.0, 1.0)
		var closest := Vector2(a.x, a.z) + ab * t
		if closest.distance_to(Vector2(c.x, c.z)) < float(o["r"]) + extra and t < best_t:
			best_t = t
			best = Vector3(closest.x, a.y, closest.y)
	return best

func random_point(margin: float = 2.0) -> Vector3:
	for i in 12:
		var p := Vector3(randf_range(-hx * shrink + margin, hx * shrink - margin), 0, randf_range(-hz * shrink + margin, hz * shrink - margin))
		if inside(p, margin) and push_out(p, 1.0).distance_to(p) < 0.01:
			return p
	return Vector3.ZERO

func spawn_positions(team: int, n: int, team_count: int) -> Array[Vector3]:
	var out: Array[Vector3] = []
	var side_x: Array = Data.arena_layout.get("spawn_team_x", [-19.0, 19.0])
	for i in n:
		var p := Vector3.ZERO
		if team_count <= 2:
			var x: float = float(side_x[team % 2])
			var spread := minf(hz * 1.5, 22.0)
			var zz := (float(i) - (n - 1) * 0.5) * (spread / maxf(n, 1))
			p = Vector3(x + (0.0 if i % 2 == 0 else (2.5 if team == 0 else -2.5)), 0, zz)
		else:
			var ang := TAU * (float(team) / team_count) + TAU * 0.125
			var c := Vector3(cos(ang) * hx * 0.72, 0, sin(ang) * hz * 0.72)
			var off := Vector3(cos(ang + PI * 0.5), 0, sin(ang + PI * 0.5)) * ((float(i) - (n - 1) * 0.5) * 2.0)
			p = c + off
		out.append(clamp_point(push_out(p, 0.8), 1.0))
	return out
