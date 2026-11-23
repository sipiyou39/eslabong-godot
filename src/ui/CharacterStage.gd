class_name CharacterStage
extends SubViewportContainer
## Portrait 3D d'un personnage (SubViewport avec éclairage studio), utilisé dans les fiches, cartes, recrutement.

var vp: SubViewport
var pivot: Node3D
var model: CharacterModel
var cam: Camera3D
var spin: bool = true
var spin_speed: float = 0.6
var anim_demo: bool = false
var _t: float = 0.0
var rim: DirectionalLight3D
var key: DirectionalLight3D
var tpl_cache: Dictionary = {}
var zoom: float = 1.0
var base_cam_dist: float = 4.0
var cam_y: float = 1.0
var aura: Color = Color(0, 0, 0, 0)
var ground: MeshInstance3D

func _init(size_px: Vector2 = Vector2(320, 380)) -> void:
	custom_minimum_size = size_px
	stretch = true
	mouse_filter = Control.MOUSE_FILTER_PASS
	vp = SubViewport.new()
	vp.transparent_bg = true
	vp.own_world_3d = true
	vp.msaa_3d = Viewport.MSAA_4X
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8a86b0")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.glow_enabled = true
	env.glow_intensity = 0.6
	env.glow_bloom = 0.05
	env.adjustment_enabled = true
	env.adjustment_saturation = 1.12
	env.adjustment_contrast = 1.08
	var we := WorldEnvironment.new()
	we.environment = env
	vp.add_child(we)
	key = DirectionalLight3D.new()
	key.light_color = Color("fff0d8")
	key.light_energy = 1.05
	key.rotation_degrees = Vector3(-38, 38, 0)
	key.shadow_enabled = true
	key.shadow_blur = 2.0
	vp.add_child(key)
	rim = DirectionalLight3D.new()
	rim.light_color = Color("7aa8ff")
	rim.light_energy = 0.7
	rim.rotation_degrees = Vector3(-20, -150, 0)
	vp.add_child(rim)
	pivot = Node3D.new()
	vp.add_child(pivot)
	cam = Camera3D.new()
	cam.fov = 28.0
	cam.current = true
	vp.add_child(cam)
	# socle
	ground = MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.75
	cm.bottom_radius = 0.82
	cm.height = 0.08
	cm.radial_segments = 40
	ground.mesh = cm
	var gm := StandardMaterial3D.new()
	gm.albedo_color = Color("2a2540")
	gm.metallic = 0.6
	gm.roughness = 0.35
	gm.emission_enabled = true
	gm.emission = Color("e0b85a")
	gm.emission_energy_multiplier = 0.15
	ground.material_override = gm
	ground.position = Vector3(0, -0.04, 0)
	vp.add_child(ground)
	_place_camera()

func _place_camera() -> void:
	var h := 1.0
	if model:
		h = model.height()
	var dist := (base_cam_dist + h * 1.05) * zoom
	cam.look_at_from_position(Vector3(0, h * 0.55 + 0.05, dist), Vector3(0, h * 0.5, 0))

func set_template(tpl: Dictionary, palette: Array = [], variant: int = 0, shiny: bool = false) -> void:
	if model:
		model.queue_free()
		model = null
	model = CharacterModel.new()
	pivot.add_child(model)
	model.build(tpl, palette, variant, shiny)
	_place_camera()
	if String(tpl.get("kind", "class")) != "class" or shiny:
		model.set_glow(1.2)
	if anim_demo:
		model.loco = 0.0

func set_merc(m: Dictionary) -> void:
	var tpl := MercLogic.tpl_for(m)
	set_template(tpl, [], int(m.get("variant", 0)), bool(m.get("shiny", false)))

func play(anim: String, dur: float = 0.6) -> void:
	if model:
		model.trigger(anim, dur)

func _process(dt: float) -> void:
	_t += dt
	if spin and pivot:
		pivot.rotation.y = sin(_t * spin_speed) * 0.6 + 0.2
	if anim_demo and model:
		var cyc := fmod(_t, 4.0)
		model.loco = 1.0 if cyc < 1.2 else 0.0
		if cyc > 2.0 and cyc < 2.05:
			model.attack_anim(0.55)
		elif cyc > 3.0 and cyc < 3.05:
			model.trigger("cast", 0.9)

func _gui_input(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion and (ev as InputEventMouseMotion).button_mask & MOUSE_BUTTON_MASK_LEFT:
		spin = false
		pivot.rotation.y += (ev as InputEventMouseMotion).relative.x * 0.01
	elif ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
		var mb := ev as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
			zoom = clampf(zoom - 0.06, 0.6, 1.4)
			_place_camera()
		elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			zoom = clampf(zoom + 0.06, 0.6, 1.4)
			_place_camera()
