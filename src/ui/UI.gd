class_name UI
extends RefCounted
## Fabrique d'interface : thème sombre/or, boutons animés, icônes avec repli procédural.

const BG := Color("0e0c16")
const BG2 := Color("171424")
const PANEL := Color("1d1930")
const PANEL_HI := Color("2a2444")
const GOLD := Color("e0b85a")
const GOLD_DIM := Color("9a7a3a")
const EMBER := Color("ff9a3c")
const TEXT := Color("efe6d2")
const TEXT_DIM := Color("a89fb8")
const GOOD := Color("6ad07a")
const BAD := Color("e8505a")
const BLUE := Color("5aa8ff")

static var _theme: Theme
static var _icon_cache: Dictionary = {}
static var _skin_manifest: Dictionary = {}
static var _skin_loaded := false

static func _load_skin() -> void:
	if _skin_loaded:
		return
	_skin_loaded = true
	var p := "res://assets/ui/skin/ui_manifest.json"
	if FileAccess.file_exists(p):
		var v: Variant = JSON.parse_string(FileAccess.get_file_as_string(p))
		if v is Dictionary:
			_skin_manifest = v

static func skin_tex(name: String) -> Texture2D:
	var p := "res://assets/ui/skin/%s.png" % name
	if _icon_cache.has(p):
		return _icon_cache[p]
	var t: Texture2D = load(p) if ResourceLoader.exists(p) else null
	_icon_cache[p] = t
	return t

## StyleBox : texture 9-patch si dispo, sinon plat arrondi
static func style_flat(bg: Color, border: Color = Color.TRANSPARENT, radius: int = 8, bw: int = 0, shadow: int = 0, pad: int = 10) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	s.set_border_width_all(bw)
	s.set_corner_radius_all(radius)
	s.content_margin_left = pad
	s.content_margin_right = pad
	s.content_margin_top = pad * 0.6
	s.content_margin_bottom = pad * 0.6
	if shadow > 0:
		s.shadow_color = Color(0, 0, 0, 0.5)
		s.shadow_size = shadow
		s.shadow_offset = Vector2(0, 2)
	s.anti_aliasing = true
	return s

static func style_tex(name: String, fallback: StyleBox) -> StyleBox:
	_load_skin()
	var t := skin_tex(name)
	if t == null:
		return fallback
	var m: Dictionary = _skin_manifest.get(name + ".png", _skin_manifest.get(name, {}))
	var st := StyleBoxTexture.new()
	st.texture = t
	var mg: Array = m.get("margins", [16, 16, 16, 16])
	st.texture_margin_left = mg[0]
	st.texture_margin_top = mg[1]
	st.texture_margin_right = mg[2]
	st.texture_margin_bottom = mg[3]
	st.content_margin_left = maxf(mg[0], 10)
	st.content_margin_right = maxf(mg[2], 10)
	st.content_margin_top = maxf(mg[1] * 0.7, 6)
	st.content_margin_bottom = maxf(mg[3] * 0.7, 6)
	return st

static func panel_style(kind: String = "dark") -> StyleBox:
	match kind:
		"gold":
			return style_tex("panel_dark_gold", style_flat(PANEL, GOLD_DIM, 10, 2, 8, 14))
		"glass":
			return style_tex("panel_glass", style_flat(Color(0.08, 0.07, 0.14, 0.78), Color(1, 1, 1, 0.1), 10, 1, 6, 12))
		"inset":
			return style_tex("panel_inset", style_flat(Color(0.05, 0.04, 0.09, 0.9), Color(1, 1, 1, 0.06), 8, 1, 0, 10))
		"card":
			return style_tex("card_frame", style_flat(PANEL, Color(1, 1, 1, 0.12), 10, 1, 6, 10))
		"header":
			return style_tex("panel_header", style_flat(PANEL_HI, GOLD_DIM, 8, 1, 0, 12))
		_:
			return style_tex("panel_dark", style_flat(PANEL, Color(1, 1, 1, 0.09), 10, 1, 8, 14))

static func btn_style(kind: String, state: String) -> StyleBox:
	var name := "btn_%s_%s" % [kind, state]
	var bg := PANEL_HI
	var border := GOLD_DIM
	match kind:
		"primary":
			bg = Color("c9922c") if state != "pressed" else Color("a87618")
			if state == "hover":
				bg = Color("e8b040")
			if state == "disabled":
				bg = Color("4a4030")
			border = Color("ffe08a")
		"danger":
			bg = Color("8a2a34") if state != "hover" else Color("b0343f")
			if state == "pressed":
				bg = Color("6a1e26")
			if state == "disabled":
				bg = Color("3a2a2e")
			border = Color("ff8a94")
		_:
			bg = Color("2a2444") if state != "hover" else Color("3a3260")
			if state == "pressed":
				bg = Color("1c1830")
			if state == "disabled":
				bg = Color("1c1a28")
			border = Color("6a5a98") if state != "hover" else GOLD
	var fb := style_flat(bg, border, 8, 2, 4, 14)
	return style_tex(name, fb)

static func theme() -> Theme:
	if _theme:
		return _theme
	var t := Theme.new()
	t.default_font = Game.font_body()
	t.default_font_size = 18
	t.set_color("font_color", "Label", TEXT)
	t.set_font("font", "Label", Game.font_body())
	t.set_color("font_color", "Button", TEXT)
	t.set_color("font_hover_color", "Button", Color.WHITE)
	t.set_color("font_pressed_color", "Button", Color("fff0c0"))
	t.set_color("font_disabled_color", "Button", Color("6a6478"))
	t.set_font("font", "Button", Game.font_bold())
	t.set_font_size("font_size", "Button", 20)
	t.set_stylebox("normal", "Button", btn_style("secondary", "normal"))
	t.set_stylebox("hover", "Button", btn_style("secondary", "hover"))
	t.set_stylebox("pressed", "Button", btn_style("secondary", "pressed"))
	t.set_stylebox("disabled", "Button", btn_style("secondary", "disabled"))
	t.set_stylebox("focus", "Button", style_flat(Color.TRANSPARENT, GOLD, 8, 2, 0, 4))
	t.set_stylebox("panel", "PanelContainer", panel_style("dark"))
	t.set_stylebox("panel", "Panel", panel_style("dark"))
	t.set_color("font_color", "LineEdit", TEXT)
	t.set_stylebox("normal", "LineEdit", style_flat(Color("0e0c18"), Color("4a4068"), 6, 2, 0, 10))
	t.set_stylebox("focus", "LineEdit", style_flat(Color("0e0c18"), GOLD, 6, 2, 0, 10))
	t.set_color("font_color", "CheckBox", TEXT)
	t.set_color("font_color", "OptionButton", TEXT)
	t.set_stylebox("normal", "OptionButton", btn_style("secondary", "normal"))
	t.set_stylebox("hover", "OptionButton", btn_style("secondary", "hover"))
	t.set_stylebox("pressed", "OptionButton", btn_style("secondary", "pressed"))
	t.set_stylebox("panel", "PopupMenu", style_flat(Color("171424"), GOLD_DIM, 6, 2, 8, 6))
	t.set_stylebox("hover", "PopupMenu", style_flat(Color("3a3260"), Color.TRANSPARENT, 4, 0, 0, 6))
	t.set_font("font", "PopupMenu", Game.font_body())
	t.set_stylebox("panel", "TooltipPanel", style_flat(Color("0e0c16"), GOLD_DIM, 6, 2, 8, 10))
	t.set_color("font_color", "TooltipLabel", TEXT)
	t.set_font_size("font_size", "TooltipLabel", 17)
	# onglets
	t.set_stylebox("tab_selected", "TabContainer", style_flat(PANEL_HI, GOLD, 8, 2, 0, 12))
	t.set_stylebox("tab_unselected", "TabContainer", style_flat(Color("14111f"), Color("3a3358"), 8, 1, 0, 12))
	t.set_stylebox("tab_hovered", "TabContainer", style_flat(Color("221d38"), GOLD_DIM, 8, 1, 0, 12))
	t.set_stylebox("panel", "TabContainer", style_flat(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 0, 0, 0))
	t.set_color("font_selected_color", "TabContainer", GOLD)
	t.set_color("font_unselected_color", "TabContainer", TEXT_DIM)
	t.set_color("font_hovered_color", "TabContainer", Color.WHITE)
	# scroll
	t.set_stylebox("scroll", "VScrollBar", style_flat(Color(0, 0, 0, 0.35), Color.TRANSPARENT, 5, 0, 0, 2))
	t.set_stylebox("grabber", "VScrollBar", style_flat(Color("5a4c88"), Color.TRANSPARENT, 5, 0, 0, 2))
	t.set_stylebox("grabber_highlight", "VScrollBar", style_flat(GOLD_DIM, Color.TRANSPARENT, 5, 0, 0, 2))
	t.set_stylebox("grabber_pressed", "VScrollBar", style_flat(GOLD, Color.TRANSPARENT, 5, 0, 0, 2))
	t.set_stylebox("scroll", "HScrollBar", style_flat(Color(0, 0, 0, 0.35), Color.TRANSPARENT, 5, 0, 0, 2))
	t.set_stylebox("grabber", "HScrollBar", style_flat(Color("5a4c88"), Color.TRANSPARENT, 5, 0, 0, 2))
	t.set_stylebox("slider", "HSlider", style_flat(Color("0c0a14"), Color("3a3358"), 4, 1, 0, 2))
	t.set_stylebox("grabber_area", "HSlider", style_flat(GOLD_DIM, Color.TRANSPARENT, 4, 0, 0, 2))
	t.set_stylebox("grabber_area_highlight", "HSlider", style_flat(GOLD, Color.TRANSPARENT, 4, 0, 0, 2))
	# curseurs et menus déroulants plus faciles à toucher
	var gi := _grabber_icon(false)
	var gh := _grabber_icon(true)
	for nm in ["grabber", "grabber_disabled"]:
		t.set_icon(nm, "HSlider", gi)
	t.set_icon("grabber_highlight", "HSlider", gh)
	t.set_stylebox("slider", "HSlider", style_flat(Color("0c0a14"), Color("3a3358"), 6, 1, 0, 2))
	t.set_font_size("font_size", "PopupMenu", 22 if touch_ui() else 18)
	t.set_constant("v_separation", "PopupMenu", 14 if touch_ui() else 6)
	_theme = t
	return t

static func _grabber_icon(hi: bool) -> Texture2D:
	var key := "grabber_%s" % hi
	if _icon_cache.has(key):
		return _icon_cache[key]
	var n := 44
	var img := Image.create(n, n, false, Image.FORMAT_RGBA8)
	for y in n:
		for x in n:
			var dx := (x - (n - 1) * 0.5) / (n * 0.5)
			var dy := (y - (n - 1) * 0.5) / (n * 0.5)
			var r := sqrt(dx * dx + dy * dy)
			if r > 0.98:
				continue
			var c := Color("0e0c16")
			if r < 0.84:
				var t := clampf(1.0 - r - dy * 0.35, 0.0, 1.0)
				c = Color("9a7a3a").lerp(Color("ffe08a") if hi else Color("e8b848"), t)
			img.set_pixel(x, y, c)
	var tex := ImageTexture.create_from_image(img)
	_icon_cache[key] = tex
	return tex

# ----------------------------------------------------------------------------------------------
# Composants
# ----------------------------------------------------------------------------------------------
static func lbl(text: String, size: int = 18, color: Color = TEXT, bold: bool = false, title: bool = false) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	if title:
		l.add_theme_font_override("font", Game.font_title())
	elif bold:
		l.add_theme_font_override("font", Game.font_bold())
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l

static func shadowed(l: Label, col: Color = Color(0, 0, 0, 0.8), size: int = 4) -> Label:
	l.add_theme_color_override("font_outline_color", col)
	l.add_theme_constant_override("outline_size", size)
	return l

## Interface tactile (téléphone / tablette, ou --mobile pour tester sur PC) : cibles plus grandes
static func touch_ui() -> bool:
	return OS.has_feature("mobile") or Game.args.has("mobile") or Game.args.has("touch") or Settings.gi("control_scheme") == 1

static func btn(text: String, kind: String = "secondary", min_size: Vector2 = Vector2(0, 44)) -> Button:
	var b := Button.new()
	b.text = text
	if touch_ui():
		min_size.y = maxf(min_size.y, 58.0)
	b.custom_minimum_size = min_size
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_stylebox_override("normal", btn_style(kind, "normal"))
	b.add_theme_stylebox_override("hover", btn_style(kind, "hover"))
	b.add_theme_stylebox_override("pressed", btn_style(kind, "pressed"))
	b.add_theme_stylebox_override("disabled", btn_style(kind, "disabled"))
	b.add_theme_font_override("font", Game.font_bold())
	b.add_theme_font_size_override("font_size", 22 if touch_ui() else 20)
	if kind == "primary":
		b.add_theme_color_override("font_color", Color("1a1208"))
		b.add_theme_color_override("font_hover_color", Color("000000"))
		b.add_theme_color_override("font_pressed_color", Color("000000"))
	b.mouse_entered.connect(func():
		Audio.ui("ui_hover")
		if is_instance_valid(b) and not b.disabled:
			b.pivot_offset = b.size * 0.5
			var tw := b.create_tween()
			tw.tween_property(b, "scale", Vector2(1.03, 1.03), 0.08))
	b.mouse_exited.connect(func():
		if is_instance_valid(b):
			b.pivot_offset = b.size * 0.5
			var tw := b.create_tween()
			tw.tween_property(b, "scale", Vector2.ONE, 0.1))
	b.pressed.connect(func(): Audio.ui("ui_click"))
	return b

## Centre un contrôle (taille fixe) dans son parent, quel que soit le conteneur
static func center(c: Control, sz: Vector2) -> void:
	c.custom_minimum_size = sz
	c.set_anchors_preset(Control.PRESET_CENTER)
	c.offset_left = -sz.x * 0.5
	c.offset_right = sz.x * 0.5
	c.offset_top = -sz.y * 0.5
	c.offset_bottom = sz.y * 0.5
	c.grow_horizontal = Control.GROW_DIRECTION_BOTH
	c.grow_vertical = Control.GROW_DIRECTION_BOTH

static func panel(kind: String = "dark") -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", panel_style(kind))
	return p

static func vbox(sep: int = 8) -> VBoxContainer:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", sep)
	return v

static func hbox(sep: int = 8) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", sep)
	return h

static func margin(c: Control, m: int = 12) -> MarginContainer:
	var mc := MarginContainer.new()
	mc.add_theme_constant_override("margin_left", m)
	mc.add_theme_constant_override("margin_right", m)
	mc.add_theme_constant_override("margin_top", m)
	mc.add_theme_constant_override("margin_bottom", m)
	mc.add_child(c)
	return mc

static func spacer(h: int = 0, w: int = 0, expand: bool = false) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(w, h)
	if expand:
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		c.size_flags_vertical = Control.SIZE_EXPAND_FILL
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c

static func hsep() -> HSeparator:
	var s := HSeparator.new()
	s.add_theme_stylebox_override("separator", style_flat(Color(GOLD_DIM, 0.5), Color.TRANSPARENT, 0, 0, 0, 0))
	s.add_theme_constant_override("separation", 6)
	return s

# ----------------------------------------------------------------------------------------------
# Icônes
# ----------------------------------------------------------------------------------------------
static func _tex(path: String) -> Texture2D:
	if _icon_cache.has(path):
		return _icon_cache[path]
	var t: Texture2D = null
	if ResourceLoader.exists(path):
		t = load(path)
	_icon_cache[path] = t
	return t

static func _fallback_icon(col: Color, key: String) -> Texture2D:
	var ck := "fb:" + col.to_html() + key
	if _icon_cache.has(ck):
		return _icon_cache[ck]
	var img := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	var c0 := col.darkened(0.55)
	var c1 := col.lightened(0.15)
	for y in 64:
		for x in 64:
			var dx := (x - 31.5) / 32.0
			var dy := (y - 31.5) / 32.0
			var r := sqrt(dx * dx + dy * dy)
			if r > 0.96:
				img.set_pixel(x, y, Color(0, 0, 0, 0))
			else:
				var t := clampf(1.0 - r, 0.0, 1.0)
				var cc := c0.lerp(c1, t)
				if r > 0.84:
					cc = Color("e0b85a").darkened(0.2 + (r - 0.84) * 2.0)
				img.set_pixel(x, y, Color(cc.r, cc.g, cc.b, 1.0))
	var tex := ImageTexture.create_from_image(img)
	_icon_cache[ck] = tex
	return tex

static func ability_icon(ab: Dictionary) -> Texture2D:
	var p := "res://assets/icons/abilities/%s.png" % String(ab.get("id", ""))
	var t := _tex(p)
	if t:
		return t
	return _fallback_icon(Data.elem_color(String(ab.get("element", "physical"))), String(ab.get("arch", "")))

static func class_icon(id: String) -> Texture2D:
	var t := _tex("res://assets/icons/classes/%s.png" % id)
	if t:
		return t
	var c: Dictionary = Data.classes.get(id, {})
	return _fallback_icon(Data.ROLE_COLOR.get(String(c.get("role", "bruiser")), Color.GRAY), id)

static func relic_icon(key: String) -> Texture2D:
	var t := _tex("res://assets/icons/relics/%s.png" % key)
	if t:
		return t
	return _fallback_icon(Color("c8a050"), key)

static func status_icon(s: String) -> Texture2D:
	var t := _tex("res://assets/icons/status/%s.png" % s)
	if t:
		return t
	return _fallback_icon(Data.STATUS_INFO.get(s, {}).get("color", Color.GRAY), s)

static func stat_icon(name: String) -> Texture2D:
	var t := _tex("res://assets/ui/icons/%s.png" % name)
	if t:
		return t
	var colmap := {"hp": Color("e8505a"), "mana": Color("5aa8ff"), "stamina": Color("6ad07a"), "power": Color("ff9a3c"), "speed": Color("8affd8"),
		"defense": Color("b0c0d8"), "mres": Color("a06bff"), "gold": Color("ffd23a")}
	return _fallback_icon(colmap.get(name, Color.GRAY), name)

static func tex_rect(t: Texture2D, size: Vector2, modulate_c: Color = Color.WHITE) -> TextureRect:
	var r := TextureRect.new()
	r.texture = t
	r.custom_minimum_size = size
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	r.modulate = modulate_c
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r

## Icône + texte (ex: stat)
static func stat_row(icon_name: String, text: String, col: Color = TEXT, size: int = 18) -> HBoxContainer:
	var h := hbox(6)
	h.add_child(tex_rect(stat_icon(icon_name), Vector2(size + 4, size + 4)))
	h.add_child(lbl(text, size, col))
	return h

static func fade_in(c: Control, t: float = 0.35, delay: float = 0.0) -> void:
	c.modulate.a = 0.0
	var tw := c.create_tween()
	if delay > 0.0:
		tw.tween_interval(delay)
	tw.tween_property(c, "modulate:a", 1.0, t)

static func pop_in(c: Control, delay: float = 0.0) -> void:
	c.modulate.a = 0.0
	await c.get_tree().process_frame
	if not is_instance_valid(c):
		return
	c.pivot_offset = c.size * 0.5
	c.scale = Vector2(0.92, 0.92)
	var tw := c.create_tween().set_parallel(true)
	if delay > 0.0:
		tw.tween_interval(delay)
		tw.chain().set_parallel(true)
	tw.tween_property(c, "modulate:a", 1.0, 0.25)
	tw.tween_property(c, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
