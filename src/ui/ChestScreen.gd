class_name ChestScreen
extends Control
## Ouverture de coffre : coffre 3D (kit Blender) avec couvercle animé, puis révélation de la récompense.

signal closed

var reward: Dictionary = {}
var vp: SubViewport
var lid: Node3D
var chest: Node3D
var opened := false
var reveal_box: VBoxContainer
var sparkle: CPUParticles3D
var cam: Camera3D
var vfx: Vfx
var fx_root: Node3D

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	if Settings.gb("chest_opening_music_enabled"):
		Audio.music("music_chest", 0.5)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.88)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var svc := SubViewportContainer.new()
	svc.stretch = true
	UI.center(svc, Vector2(760, 520))
	add_child(svc)
	vp = SubViewport.new()
	vp.transparent_bg = true
	vp.own_world_3d = true
	vp.msaa_3d = Viewport.MSAA_4X
	svc.add_child(vp)
	_build_scene()
	reveal_box = UI.vbox(8)
	UI.center(reveal_box, Vector2(600, 0))
	add_child(reveal_box)
	var open_b := UI.btn("Ouvrir", "primary", Vector2(240, 58))
	open_b.name = "OpenBtn"
	open_b.pressed.connect(func():
		open_b.queue_free()
		_open())
	reveal_box.add_child(open_b)

func _build_scene() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8a7aa8")
	env.ambient_light_energy = 0.7
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.glow_enabled = true
	env.glow_intensity = 1.0
	env.glow_bloom = 0.15
	var we := WorldEnvironment.new()
	we.environment = env
	vp.add_child(we)
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-40, 30, 0)
	key.light_energy = 1.3
	key.shadow_enabled = true
	vp.add_child(key)
	fx_root = Node3D.new()
	vp.add_child(fx_root)
	vfx = Vfx.new()
	vfx.root = fx_root
	vp.add_child(vfx)
	cam = Camera3D.new()
	cam.fov = 30.0
	vp.add_child(cam)
	cam.position = Vector3(0, 2.2, 4.8)
	cam.look_at(Vector3(0, 0.6, 0))
	vfx.camera = cam
	Kit.ensure_loaded()
	var tier := int(reward.get("tier", 0))
	var pal: Array[Color] = [Color("8a5a2a"), Color("3a2a1a"), [Color("c9a24a"), Color("6ad0ff"), Color("b05aff"), Color("ffb030"), Color("ff5a3c")][clampi(tier, 0, 4)], Color("d8b090")]
	chest = Node3D.new()
	vp.add_child(chest)
	var mat := ShaderMaterial.new()
	mat.shader = load("res://src/shaders/toon_character.gdshader")
	mat.set_shader_parameter("c_primary", pal[0])
	mat.set_shader_parameter("c_secondary", pal[1])
	mat.set_shader_parameter("c_accent", pal[2])
	mat.set_shader_parameter("c_skin", pal[3])
	mat.set_shader_parameter("accent_glow", 0.7)
	var body_name := "prop_chest_closed" if Kit.has_part("prop_chest_closed") else ""
	if body_name != "":
		var body := Kit.make_part("prop_chest_body_open" if Kit.has_part("prop_chest_body_open") else "prop_chest_closed")
		body.material_override = mat
		chest.add_child(body)
		if Kit.has_part("prop_chest_lid") and Kit.has_part("prop_chest_body_open"):
			lid = Node3D.new()
			lid.position = Kit.part_origin("prop_chest_lid")
			chest.add_child(lid)
			var lm := Kit.make_part("prop_chest_lid")
			lm.material_override = mat
			lid.add_child(lm)
	else:
		var box := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(1.2, 0.7, 0.8)
		box.mesh = bm
		box.position.y = 0.35
		var sm := StandardMaterial3D.new()
		sm.albedo_color = pal[0]
		box.material_override = sm
		chest.add_child(box)
		lid = Node3D.new()
		lid.position = Vector3(0, 0.7, -0.4)
		chest.add_child(lid)
		var lb := MeshInstance3D.new()
		var lbm := BoxMesh.new()
		lbm.size = Vector3(1.2, 0.2, 0.8)
		lb.mesh = lbm
		lb.position = Vector3(0, 0.1, 0.4)
		lb.material_override = sm
		lid.add_child(lb)
	chest.scale = Vector3.ONE * 1.6
	chest.rotation.y = 0.5
	var glow := OmniLight3D.new()
	glow.light_color = pal[2]
	glow.light_energy = 0.0
	glow.omni_range = 6.0
	glow.name = "Glow"
	glow.position = Vector3(0, 1.0, 0.4)
	vp.add_child(glow)

func _open() -> void:
	opened = true
	Audio.ui("ui_chest_rare" if int(reward.get("tier", 0)) >= 3 else "ui_chest_open")
	var tw := create_tween()
	if lid:
		tw.tween_property(lid, "rotation:x", -1.9, 0.6).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	var glow: OmniLight3D = vp.get_node("Glow")
	tw.parallel().tween_property(glow, "light_energy", 6.0, 0.5)
	tw.tween_callback(func():
		var tier := int(reward.get("tier", 0))
		var col: Color = [Color("c9a24a"), Color("6ad0ff"), Color("b05aff"), Color("ffb030"), Color("ff5a3c")][clampi(tier, 0, 4)]
		vfx.burst(Vector3(0, 1.2, 0.3), col, 40, 7.0, 1.4, 0.5, "spark_star4", -2.0, 70.0)
		vfx.burst(Vector3(0, 1.4, 0.3), Color.WHITE, 8, 3.0, 0.8, 1.4, "soft_glow", 0.0, 60.0)
		_reveal())

func _reveal() -> void:
	var p := UI.panel("gold")
	var v := UI.vbox(6)
	p.add_child(v)
	if int(reward.get("gold", 0)) > 0:
		var h := UI.hbox(10)
		h.alignment = BoxContainer.ALIGNMENT_CENTER
		h.add_child(UI.tex_rect(UI.stat_icon("coin_stack"), Vector2(64, 64)))
		h.add_child(UI.lbl("+%s or" % Game.format_gold(reward["gold"]), 38, UI.GOLD, false, true))
		v.add_child(h)
	elif not (reward.get("relic", {}) as Dictionary).is_empty():
		var item: Dictionary = reward["relic"]
		var r: Dictionary = Data.relics.get(String(item["rid"]), {})
		var h2 := UI.hbox(14)
		h2.alignment = BoxContainer.ALIGNMENT_CENTER
		h2.add_child(UI.tex_rect(UI.relic_icon(String(r.get("icon", ""))), Vector2(84, 84)))
		var tv := UI.vbox(2)
		tv.add_child(UI.lbl(String(r.get("name", "?")), 32, Data.RARITY_COLOR.get(String(r.get("rarity", "common")), UI.TEXT), false, true))
		tv.add_child(UI.lbl(String(Data.RARITY_NAME_FR.get(String(r.get("rarity", "common")), "")), 17, UI.TEXT_DIM, true))
		var d := UI.lbl(String(r.get("desc", "")), 17, UI.TEXT)
		d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		d.custom_minimum_size = Vector2(420, 0)
		tv.add_child(d)
		h2.add_child(tv)
		v.add_child(h2)
	var ok := UI.btn("Récupérer", "primary", Vector2(0, 50))
	ok.pressed.connect(func():
		closed.emit()
		queue_free())
	v.add_child(ok)
	reveal_box.add_child(p)
	UI.pop_in(p)

func _process(dt: float) -> void:
	if chest and not opened:
		chest.rotation.y = 0.5 + sin(Time.get_ticks_msec() / 900.0) * 0.12
		chest.position.y = sin(Time.get_ticks_msec() / 600.0) * 0.03
