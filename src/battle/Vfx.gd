class_name Vfx
extends Node
## Fabrique d'effets visuels 3D (particules additives, anneaux, éclairs, décals, nombres flottants).

var root: Node3D
var camera: Camera3D
var _tex_cache: Dictionary = {}
var _quad: QuadMesh
var _mat_cache: Dictionary = {}
var shake_amount: float = 0.0
var max_lights: int = 24
var active_lights: int = 0
const TEX_DIR := "res://assets/textures/vfx/"

func _init() -> void:
	_quad = QuadMesh.new()
	_quad.size = Vector2(1, 1)

# ----------------------------------------------------------------------------------------------
# Textures / matériaux
# ----------------------------------------------------------------------------------------------
func tex(name: String) -> Texture2D:
	if _tex_cache.has(name):
		return _tex_cache[name]
	var path := TEX_DIR + name + ".png"
	var t: Texture2D = null
	if ResourceLoader.exists(path):
		t = load(path)
	if t == null:
		t = _fallback_tex(name)
	_tex_cache[name] = t
	return t

func _fallback_tex(name: String) -> Texture2D:
	var g := Gradient.new()
	var gt := GradientTexture2D.new()
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(1.0, 0.5)
	gt.width = 128
	gt.height = 128
	if name.contains("ring"):
		g.offsets = PackedFloat32Array([0.0, 0.72, 0.88, 0.97, 1.0])
		g.colors = PackedColorArray([Color(1, 1, 1, 0), Color(1, 1, 1, 0), Color(1, 1, 1, 1), Color(1, 1, 1, 0.1), Color(1, 1, 1, 0)])
	elif name.contains("spark") or name.contains("star"):
		g.offsets = PackedFloat32Array([0.0, 0.25, 1.0])
		g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0.5), Color(1, 1, 1, 0)])
	else:
		g.offsets = PackedFloat32Array([0.0, 0.35, 1.0])
		g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0.45), Color(1, 1, 1, 0)])
	gt.gradient = g
	return gt

func additive_mat(texname: String, color: Color = Color.WHITE, particles: bool = true) -> StandardMaterial3D:
	var key := "%s|%s|%s" % [texname, color.to_html(), str(particles)]
	if _mat_cache.has(key):
		return _mat_cache[key]
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.vertex_color_use_as_albedo = true
	m.albedo_color = color
	m.albedo_texture = tex(texname)
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.no_depth_test = false
	m.disable_receive_shadows = true
	if particles:
		m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
		m.billboard_keep_scale = true
	_mat_cache[key] = m
	return m

# ----------------------------------------------------------------------------------------------
# Particules
# ----------------------------------------------------------------------------------------------
func burst(pos: Vector3, color: Color, count: int = 18, speed: float = 5.0, life: float = 0.5, size: float = 0.3,
		texname: String = "soft_glow", gravity: float = -4.0, spread: float = 180.0, dir: Vector3 = Vector3.UP, grow: float = 0.0) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.mesh = _quad
	p.material_override = additive_mat(texname, Color.WHITE)
	p.amount = maxi(count, 1)
	p.lifetime = life
	p.one_shot = true
	p.explosiveness = 0.95
	p.direction = dir
	p.spread = spread
	p.initial_velocity_min = speed * 0.5
	p.initial_velocity_max = speed
	p.gravity = Vector3(0, gravity, 0)
	p.scale_amount_min = size * 0.6
	p.scale_amount_max = size * 1.2
	var curve := Curve.new()
	curve.add_point(Vector2(0, 0.4))
	curve.add_point(Vector2(0.2, 1.0))
	curve.add_point(Vector2(1, 0.1 + grow))
	p.scale_amount_curve = curve
	var grad := Gradient.new()
	grad.offsets = PackedFloat32Array([0.0, 0.2, 1.0])
	grad.colors = PackedColorArray([color, color, Color(color.r, color.g, color.b, 0.0)])
	p.color_ramp = grad
	p.emitting = true
	root.add_child(p)
	p.global_position = pos
	_autofree(p, life + 0.3)
	return p

func smoke(pos: Vector3, color: Color = Color(0.35, 0.32, 0.3, 0.6), count: int = 8, size: float = 0.8, life: float = 0.9) -> void:
	var p := CPUParticles3D.new()
	p.mesh = _quad
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.vertex_color_use_as_albedo = true
	m.albedo_texture = tex("smoke_puff_0")
	m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	m.billboard_keep_scale = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	p.material_override = m
	p.amount = count
	p.lifetime = life
	p.one_shot = true
	p.explosiveness = 0.9
	p.direction = Vector3.UP
	p.spread = 70.0
	p.initial_velocity_min = 0.6
	p.initial_velocity_max = 2.2
	p.gravity = Vector3(0, 0.6, 0)
	p.scale_amount_min = size * 0.6
	p.scale_amount_max = size
	var curve := Curve.new()
	curve.add_point(Vector2(0, 0.3))
	curve.add_point(Vector2(1, 1.4))
	p.scale_amount_curve = curve
	var grad := Gradient.new()
	grad.offsets = PackedFloat32Array([0.0, 0.3, 1.0])
	grad.colors = PackedColorArray([Color(color.r, color.g, color.b, 0.0), color, Color(color.r, color.g, color.b, 0.0)])
	p.color_ramp = grad
	p.emitting = true
	root.add_child(p)
	p.global_position = pos
	_autofree(p, life + 0.3)

func trail(parent: Node3D, color: Color, size: float = 0.35, rate: int = 28, life: float = 0.35, texname: String = "soft_glow") -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.mesh = _quad
	p.material_override = additive_mat(texname, Color.WHITE)
	p.amount = rate
	p.lifetime = life
	p.local_coords = false
	p.direction = Vector3.ZERO
	p.spread = 180.0
	p.initial_velocity_min = 0.0
	p.initial_velocity_max = 0.6
	p.gravity = Vector3.ZERO
	p.scale_amount_min = size * 0.7
	p.scale_amount_max = size
	var curve := Curve.new()
	curve.add_point(Vector2(0, 1.0))
	curve.add_point(Vector2(1, 0.0))
	p.scale_amount_curve = curve
	var grad := Gradient.new()
	grad.offsets = PackedFloat32Array([0.0, 1.0])
	grad.colors = PackedColorArray([color, Color(color.r, color.g, color.b, 0.0)])
	p.color_ramp = grad
	p.emitting = true
	parent.add_child(p)
	return p

func ambient_embers(pos: Vector3, extents: Vector3, color: Color, amount: int = 80, size: float = 0.12) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.mesh = _quad
	p.material_override = additive_mat("soft_glow", Color.WHITE)
	p.amount = amount
	p.lifetime = 6.0
	p.preprocess = 6.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = extents
	p.direction = Vector3.UP
	p.spread = 25.0
	p.initial_velocity_min = 0.3
	p.initial_velocity_max = 1.0
	p.gravity = Vector3(0.15, 0.25, 0.0)
	p.scale_amount_min = size * 0.5
	p.scale_amount_max = size
	var grad := Gradient.new()
	grad.offsets = PackedFloat32Array([0.0, 0.2, 0.8, 1.0])
	grad.colors = PackedColorArray([Color(color.r, color.g, color.b, 0.0), color, color, Color(color.r, color.g, color.b, 0.0)])
	p.color_ramp = grad
	p.emitting = true
	root.add_child(p)
	p.global_position = pos
	return p

# ----------------------------------------------------------------------------------------------
# Formes plates (anneaux, arcs, décals)
# ----------------------------------------------------------------------------------------------
func _flat_quad(texname: String, color: Color, size: float) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(size, size)
	q.orientation = PlaneMesh.FACE_Y
	mi.mesh = q
	mi.material_override = additive_mat(texname, color, false)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi

func ring(pos: Vector3, color: Color, radius: float, life: float = 0.45, texname: String = "shock_ring", y: float = 0.08) -> void:
	var mi := _flat_quad(texname, color, 2.0)
	root.add_child(mi)
	mi.global_position = Vector3(pos.x, y, pos.z)
	mi.scale = Vector3(0.1, 1.0, 0.1) * radius * 0.5
	var tw := mi.create_tween().set_parallel(true)
	tw.tween_property(mi, "scale", Vector3(radius, 1.0, radius) * 1.0, life).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(mi.material_override, "albedo_color:a", 0.0, life).set_ease(Tween.EASE_IN)
	tw.chain().tween_callback(mi.queue_free)
	mi.material_override = mi.material_override.duplicate()

func decal(pos: Vector3, color: Color, radius: float, texname: String = "scorch_decal", life: float = 4.0) -> void:
	var mi := _flat_quad(texname, color, 2.0)
	var mat: StandardMaterial3D = mi.material_override.duplicate()
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	mi.material_override = mat
	root.add_child(mi)
	mi.global_position = Vector3(pos.x, 0.03, pos.z)
	mi.rotation.y = randf() * TAU
	mi.scale = Vector3(radius, 1, radius)
	var tw := mi.create_tween()
	tw.tween_interval(life * 0.4)
	tw.tween_property(mat, "albedo_color:a", 0.0, life * 0.6)
	tw.tween_callback(mi.queue_free)

func slash_arc(pos: Vector3, yaw: float, color: Color, size: float = 3.0, life: float = 0.22, idx: int = -1) -> void:
	var n := idx if idx >= 0 else randi() % 5
	var mi := _flat_quad("slash_arc_%d" % n, color, size)
	var mat: StandardMaterial3D = mi.material_override.duplicate()
	mi.material_override = mat
	root.add_child(mi)
	mi.global_position = Vector3(pos.x, pos.y, pos.z)
	mi.rotation.y = yaw
	mi.scale = Vector3(0.6, 1, 0.6)
	var tw := mi.create_tween().set_parallel(true)
	tw.tween_property(mi, "scale", Vector3(1.15, 1, 1.15), life).set_ease(Tween.EASE_OUT)
	tw.tween_property(mat, "albedo_color:a", 0.0, life).set_delay(life * 0.35)
	tw.chain().tween_callback(mi.queue_free)

func light_flash(pos: Vector3, color: Color, energy: float = 3.0, rng: float = 6.0, life: float = 0.25) -> void:
	if active_lights >= max_lights:
		return
	active_lights += 1
	var l := OmniLight3D.new()
	l.light_color = color
	l.light_energy = energy
	l.omni_range = rng
	l.shadow_enabled = false
	root.add_child(l)
	l.global_position = pos + Vector3(0, 0.8, 0)
	var tw := l.create_tween()
	tw.tween_property(l, "light_energy", 0.0, life).set_ease(Tween.EASE_OUT)
	tw.tween_callback(func():
		active_lights -= 1
		l.queue_free())

func lightning(a: Vector3, b: Vector3, color: Color, width: float = 0.25, life: float = 0.22, jag: float = 0.6) -> void:
	var segs := clampi(int(a.distance_to(b) / 1.1), 4, 18)
	var pts: Array[Vector3] = []
	var dir := (b - a)
	var side := dir.cross(Vector3.UP).normalized()
	for i in segs + 1:
		var t := float(i) / segs
		var p := a.lerp(b, t)
		if i > 0 and i < segs:
			p += side * randf_range(-jag, jag) + Vector3.UP * randf_range(-jag * 0.4, jag * 0.4)
		pts.append(p)
	var im := ImmediateMesh.new()
	var cam_pos := camera.global_position if camera else Vector3(0, 20, 20)
	im.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	for i in pts.size():
		var tang := (pts[min(i + 1, pts.size() - 1)] - pts[max(i - 1, 0)]).normalized()
		var to_cam := (cam_pos - pts[i]).normalized()
		var w: Vector3 = tang.cross(to_cam).normalized() * width * (1.0 - 0.5 * absf(float(i) / segs - 0.5))
		im.surface_set_color(Color(1, 1, 1, 1))
		im.surface_set_uv(Vector2(0, float(i) / segs))
		im.surface_add_vertex(pts[i] - w)
		im.surface_set_color(Color(1, 1, 1, 1))
		im.surface_set_uv(Vector2(1, float(i) / segs))
		im.surface_add_vertex(pts[i] + w)
	im.surface_end()
	var mi := MeshInstance3D.new()
	mi.mesh = im
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = color * 1.6
	m.vertex_color_use_as_albedo = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.albedo_texture = tex("soft_glow")
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(mi)
	var tw := mi.create_tween()
	tw.tween_property(m, "albedo_color:a", 0.0, life)
	tw.tween_callback(mi.queue_free)
	light_flash((a + b) * 0.5, color, 1.5, 7.0, life)

func beam_mesh(width: float, color: Color) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(width, 1.0)
	q.orientation = PlaneMesh.FACE_Y
	q.center_offset = Vector3(0, 0, -0.5)
	mi.mesh = q
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = color * 1.5
	m.albedo_texture = tex("soft_glow")
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi

func sphere_glow(color: Color, size: float = 0.5) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var s := SphereMesh.new()
	s.radius = size * 0.5
	s.height = size
	s.radial_segments = 16
	s.rings = 8
	mi.mesh = s
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = color.lightened(0.35)
	m.emission_enabled = true
	m.emission = color
	m.emission_energy_multiplier = 3.0
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi

# ----------------------------------------------------------------------------------------------
# Textes flottants, tremblements
# ----------------------------------------------------------------------------------------------
func float_text(pos: Vector3, text: String, color: Color, size: float = 1.0, rise: float = 1.6, life: float = 0.9) -> void:
	var l := Label3D.new()
	l.text = text
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.no_depth_test = true
	l.fixed_size = false
	l.pixel_size = 0.0075 * size
	l.font_size = 64
	l.outline_size = 16
	l.modulate = color
	l.outline_modulate = Color(0.04, 0.02, 0.05, 0.95)
	l.shaded = false
	l.double_sided = true
	l.render_priority = 5
	var f := Game.font_title()
	if f:
		l.font = f
	root.add_child(l)
	l.global_position = pos + Vector3(randf_range(-0.3, 0.3), 0.0, randf_range(-0.2, 0.2))
	l.scale = Vector3.ONE * 0.4
	var tw := l.create_tween().set_parallel(true)
	tw.tween_property(l, "scale", Vector3.ONE * 1.0, 0.12).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "global_position:y", pos.y + rise, life).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "modulate:a", 0.0, life * 0.5).set_delay(life * 0.5)
	tw.tween_property(l, "outline_modulate:a", 0.0, life * 0.5).set_delay(life * 0.5)
	tw.chain().tween_callback(l.queue_free)

func shake(amount: float) -> void:
	if Settings.gb("reduce_screen_shake"):
		amount *= 0.25
	shake_amount = maxf(shake_amount, amount)

func _autofree(n: Node, t: float) -> void:
	var timer := Timer.new()
	timer.one_shot = true
	timer.wait_time = t
	n.add_child(timer)
	timer.timeout.connect(n.queue_free)
	timer.start()

# ----------------------------------------------------------------------------------------------
# Effets composés par élément
# ----------------------------------------------------------------------------------------------
func hit_fx(pos: Vector3, element: String, crit: bool = false, power: float = 1.0) -> void:
	var c: Color = Data.elem_color(element)
	var n := int((10 if crit else 6) * power)
	burst(pos + Vector3(0, 0.9, 0), c, n, 5.0 * power, 0.35, 0.28 * power, "spark_star4", -2.0, 180.0)
	burst(pos + Vector3(0, 0.9, 0), Color.WHITE, 3, 2.0, 0.18, 0.7 * power, "soft_glow", 0.0, 180.0)
	if crit:
		ring(pos, c, 2.4, 0.3, "shock_ring", 0.9)
		light_flash(pos, c, 2.5, 5.0, 0.18)

func element_burst(pos: Vector3, element: String, radius: float) -> void:
	var c: Color = Data.elem_color(element)
	ring(pos, c, radius * 1.1, 0.5)
	ring(pos, c.lightened(0.3), radius * 0.7, 0.35, "glow_ring")
	burst(pos + Vector3(0, 0.3, 0), c, int(14 + radius * 5), 6.0 + radius, 0.7, 0.55, "soft_glow", -1.0, 120.0)
	match element:
		"fire":
			burst(pos + Vector3(0, 0.2, 0), c, 14, 4.0, 0.9, 0.9, "fire_tongue_0", 2.0, 40.0)
			smoke(pos + Vector3(0, 0.3, 0), Color(0.15, 0.1, 0.1, 0.7), 6, radius * 0.7)
			decal(pos, Color(0.05, 0.02, 0.02, 0.8), radius, "scorch_decal", 5.0)
		"ice":
			burst(pos + Vector3(0, 0.3, 0), Color(0.8, 0.95, 1.0), 14, 6.0, 0.8, 0.4, "ice_shard_0", -6.0, 70.0)
			decal(pos, Color(0.6, 0.9, 1.0, 0.8), radius, "frost_decal", 5.0)
		"lightning":
			for i in 4:
				var a := Vector3(randf_range(-1, 1), 0, randf_range(-1, 1)).normalized() * radius
				lightning(pos + Vector3(0, 0.4, 0), pos + a + Vector3(0, 0.4, 0), c, 0.18, 0.18, 0.5)
		"shadow", "void":
			decal(pos, c.darkened(0.5), radius, "shadow_blob", 4.0)
			smoke(pos + Vector3(0, 0.3, 0), c.darkened(0.4), 6, radius * 0.7)
		"earth":
			smoke(pos + Vector3(0, 0.2, 0), Color(0.5, 0.4, 0.3, 0.7), 8, radius * 0.8)
			burst(pos + Vector3(0, 0.2, 0), Color(0.6, 0.5, 0.35), 10, 5.0, 0.7, 0.35, "dust_puff", -9.0, 60.0)
		"holy":
			burst(pos + Vector3(0, 0.2, 0), c, 12, 3.0, 1.0, 0.5, "light_ray", 2.0, 30.0)
		"blood":
			decal(pos, Color(0.5, 0.05, 0.08, 0.8), radius * 0.8, "shadow_blob", 4.0)
		"nature":
			burst(pos + Vector3(0, 0.5, 0), c, 12, 3.0, 1.0, 0.35, "leaf", -1.5, 100.0)
	light_flash(pos, c, 3.5, radius * 2.0 + 3.0, 0.3)
	shake(0.15 + radius * 0.04)
