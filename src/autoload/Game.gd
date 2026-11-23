extends Node
## État global, gestion de scènes (avec fondu), polices, utilitaires.

signal scene_changed

var campaign: Campaign = null
var scene_root: Node
var current_scene: Node
var fade_layer: CanvasLayer
var fade_rect: ColorRect
var postfx_layer: CanvasLayer
var postfx_rect: ColorRect
var postfx_mat: ShaderMaterial
var _font_title: Font
var _font_body: Font
var _font_body_bold: Font
var args: Dictionary = {}
var transitioning := false
var last_battle_result: Dictionary = {}
var pending_report: Dictionary = {}
var toast_layer: CanvasLayer
var toast_box: VBoxContainer

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--"):
			var kv := a.substr(2).split("=", true, 1)
			args[kv[0]] = kv[1] if kv.size() > 1 else "1"
	_setup_fonts()
	_setup_layers()

func _setup_fonts() -> void:
	var ft := FontFile.new()
	if FileAccess.file_exists("res://assets/fonts/Cinzel.ttf"):
		ft.data = FileAccess.get_file_as_bytes("res://assets/fonts/Cinzel.ttf")
		var fv := FontVariation.new()
		fv.base_font = ft
		fv.variation_opentype = {"wght": 700}
		_font_title = fv
	else:
		_font_title = ThemeDB.fallback_font
	var fb := FontFile.new()
	if FileAccess.file_exists("res://assets/fonts/Rajdhani-Medium.otf"):
		fb.data = FileAccess.get_file_as_bytes("res://assets/fonts/Rajdhani-Medium.otf")
		_font_body = fb
		var fbb := FontFile.new()
		fbb.data = FileAccess.get_file_as_bytes("res://assets/fonts/Rajdhani-Bold.otf")
		_font_body_bold = fbb
	else:
		_font_body = ThemeDB.fallback_font
		_font_body_bold = ThemeDB.fallback_font

func font_title() -> Font:
	return _font_title

func font_body() -> Font:
	return _font_body

func font_bold() -> Font:
	return _font_body_bold

func _setup_layers() -> void:
	scene_root = Node.new()
	scene_root.name = "SceneRoot"
	get_tree().root.add_child.call_deferred(scene_root)
	postfx_layer = CanvasLayer.new()
	postfx_layer.layer = 90
	add_child(postfx_layer)
	postfx_rect = ColorRect.new()
	postfx_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	postfx_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	postfx_mat = ShaderMaterial.new()
	postfx_mat.shader = load("res://src/shaders/postfx.gdshader")
	var grain_path := "res://assets/textures/vfx/film_grain.png"
	if ResourceLoader.exists(grain_path):
		postfx_mat.set_shader_parameter("grain_tex", load(grain_path))
	else:
		var n := FastNoiseLite.new()
		var nt := NoiseTexture2D.new()
		nt.noise = n
		nt.width = 256
		nt.height = 256
		nt.seamless = true
		postfx_mat.set_shader_parameter("grain_tex", nt)
	postfx_rect.material = postfx_mat
	postfx_layer.add_child(postfx_rect)
	toast_layer = CanvasLayer.new()
	toast_layer.layer = 95
	add_child(toast_layer)
	toast_box = VBoxContainer.new()
	toast_box.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	toast_box.position = Vector2(-420, 110)
	toast_box.custom_minimum_size = Vector2(400, 0)
	toast_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toast_box.add_theme_constant_override("separation", 8)
	toast_layer.add_child(toast_box)
	fade_layer = CanvasLayer.new()
	fade_layer.layer = 100
	add_child(fade_layer)
	fade_rect = ColorRect.new()
	fade_rect.color = Color(0.02, 0.015, 0.03, 1.0)
	fade_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fade_rect.modulate.a = 0.0
	fade_layer.add_child(fade_rect)

var _fps_t: float = 0.0

func _process(delta: float) -> void:
	if args.has("fpslog"):
		_fps_t += delta / maxf(Engine.time_scale, 0.01)
		if _fps_t >= 1.0:
			_fps_t = 0.0
			print("FPS ", Engine.get_frames_per_second())
	if postfx_mat:
		postfx_mat.set_shader_parameter("time_s", Time.get_ticks_msec() / 1000.0)
		var fx_on: bool = Settings.gb("postfx_enabled")
		postfx_rect.visible = fx_on

## Impulsion d'aberration chromatique / flash écran
func postfx_pulse(aberration: float = 0.012, flash: Color = Color(1, 1, 1, 0.0), t: float = 0.25) -> void:
	if not Settings.gb("impact_flash_enabled"):
		return
	var tw := create_tween().set_parallel(true)
	postfx_mat.set_shader_parameter("aberration", aberration)
	tw.tween_method(func(v: float): postfx_mat.set_shader_parameter("aberration", v), aberration, 0.0, t)
	if flash.a > 0.0:
		postfx_mat.set_shader_parameter("flash", flash)
		tw.tween_method(func(v: float): postfx_mat.set_shader_parameter("flash", Color(flash.r, flash.g, flash.b, v)), flash.a, 0.0, t)

func set_vignette(v: float) -> void:
	postfx_mat.set_shader_parameter("vignette", v)

# ----------------------------------------------------------------------------------------------
# Scènes
# ----------------------------------------------------------------------------------------------
func change_scene(node: Node, fade_time: float = 0.35) -> void:
	if transitioning:
		node.queue_free()
		return
	transitioning = true
	if fade_time > 0.0 and current_scene != null:
		var tw := create_tween()
		tw.tween_property(fade_rect, "modulate:a", 1.0, fade_time)
		await tw.finished
	if current_scene and is_instance_valid(current_scene):
		current_scene.queue_free()
		await get_tree().process_frame
	Engine.time_scale = 1.0
	current_scene = node
	if scene_root == null or not scene_root.is_inside_tree():
		await get_tree().process_frame
	scene_root.add_child(node)
	scene_changed.emit()
	if fade_time > 0.0:
		var tw2 := create_tween()
		tw2.tween_property(fade_rect, "modulate:a", 0.0, fade_time)
		await tw2.finished
	transitioning = false

func goto_main_menu() -> void:
	var s := MainMenu.new()
	change_scene(s)

func goto_hub() -> void:
	var s := HubScreen.new()
	change_scene(s)

func start_battle(config: Dictionary) -> void:
	var b := Battle.new()
	b.config = config
	change_scene(b, 0.45)

func screenshot(path: String) -> void:
	var img := get_viewport().get_texture().get_image()
	img.save_png(path)
	print("[shot] ", path, " ", img.get_size())

# ----------------------------------------------------------------------------------------------
# Utilitaires
# ----------------------------------------------------------------------------------------------
func format_gold(v: float) -> String:
	var n := int(round(v))
	var s := str(abs(n))
	var out := ""
	var cnt := 0
	for i in range(s.length() - 1, -1, -1):
		out = s[i] + out
		cnt += 1
		if cnt % 3 == 0 and i > 0:
			out = " " + out
	return ("-" if n < 0 else "") + out

func rng_from(seed_val: int) -> RandomNumberGenerator:
	var r := RandomNumberGenerator.new()
	r.seed = seed_val
	return r

# ----------------------------------------------------------------------------------------------
# Notifications
# ----------------------------------------------------------------------------------------------
func toast(text: String, kind: String = "info", dur: float = 3.2) -> void:
	if toast_box == null:
		return
	var p := PanelContainer.new()
	var col: Color = {"info": UI.BLUE, "error": UI.BAD, "good": UI.GOOD, "achievement": UI.GOLD, "gold": UI.GOLD}.get(kind, UI.BLUE)
	p.add_theme_stylebox_override("panel", UI.style_flat(Color(0.07, 0.06, 0.12, 0.94), col, 10, 2, 8, 14))
	var l := UI.lbl(text, 19, UI.TEXT, true)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(360, 0)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.add_child(l)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toast_box.add_child(p)
	p.modulate.a = 0.0
	var tw := p.create_tween()
	tw.tween_property(p, "modulate:a", 1.0, 0.2)
	tw.tween_interval(dur)
	tw.tween_property(p, "modulate:a", 0.0, 0.5)
	tw.tween_callback(p.queue_free)
	if kind == "error":
		Audio.ui("ui_error")
	elif kind == "achievement":
		Audio.ui("ui_achievement")
	else:
		Audio.ui("ui_notification")

func achievement_popup(id: String) -> void:
	toast("🏆 Succès : %s\n%s" % [Achievements.name_of(id), Achievements.desc_of(id)], "achievement", 4.5)
