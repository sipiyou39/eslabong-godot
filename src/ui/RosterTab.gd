class_name RosterTab
extends Control
## Onglet Effectif : cartes de tous les mercenaires, tri, titulaires, aperçu 3D.

var hub: Node
var c: Campaign
var sort_key: String = "rating"
var grid: GridContainer
var stage: CharacterStage
var preview_label: Label
var cap_label: Label

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	rebuild()

func rebuild() -> void:
	for ch in get_children():
		ch.queue_free()
	c = hub.c
	var p := UI.panel("glass")
	p.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(p)
	var v := UI.vbox(8)
	p.add_child(v)
	var hd := UI.hbox(10)
	hd.add_child(UI.lbl("EFFECTIF", 30, UI.GOLD, false, true))
	cap_label = UI.lbl("%d / %d" % [c.roster.size(), Market.roster_capacity(c)], 20, UI.TEXT_DIM, true)
	hd.add_child(cap_label)
	hd.add_child(UI.spacer(0, 0, true))
	hd.add_child(UI.lbl("Trier par", 17, UI.TEXT_DIM, true))
	var so := OptionButton.new()
	var keys := ["rating", "level", "role", "name", "kills"]
	for n in ["Force", "Niveau", "Rôle", "Nom", "Éliminations"]:
		so.add_item(n)
	so.selected = keys.find(sort_key)
	so.item_selected.connect(func(i: int):
		sort_key = keys[i]
		rebuild())
	hd.add_child(so)
	var auto := UI.btn("Composition auto", "secondary", Vector2(170, 38))
	auto.pressed.connect(func():
		c.auto_lineup()
		hub.refresh())
	hd.add_child(auto)
	v.add_child(hd)
	var body := UI.hbox(14)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	var sc := ScrollContainer.new()
	sc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	body.add_child(sc)
	grid = GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(grid)
	var arr := c.roster.duplicate()
	arr.sort_custom(func(a, b):
		match sort_key:
			"level": return int(a["level"]) > int(b["level"])
			"name": return String(a["name"]) < String(b["name"])
			"kills": return int(a["career"]["kills"]) > int(b["career"]["kills"])
			"role": return String(Data.template(a["class_id"])["role"]) < String(Data.template(b["class_id"])["role"])
		return MercLogic.rating(a) > MercLogic.rating(b))
	for m in arr:
		grid.add_child(_card(m))
	var side := UI.vbox(6)
	side.custom_minimum_size = Vector2(330, 0)
	stage = CharacterStage.new(Vector2(330, 470))
	side.add_child(stage)
	preview_label = UI.lbl("Survole un combattant", 18, UI.TEXT_DIM, true)
	side.add_child(preview_label)
	body.add_child(side)
	if not arr.is_empty():
		_preview(arr[0])

func _preview(m: Dictionary) -> void:
	stage.set_merc(m)
	preview_label.text = "%s — niv. %d" % [m["name"], m["level"]]

func _card(m: Dictionary) -> Control:
	var in_line: bool = m["uid"] in c.lineup
	var b := Button.new()
	b.custom_minimum_size = Vector2(0, 118)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.focus_mode = Control.FOCUS_NONE
	var border := UI.GOLD if in_line else Color("4a4068")
	if m["shiny"]:
		border = Color("8affff")
	if m["legendary"]:
		border = Color("ffd060")
	b.add_theme_stylebox_override("normal", UI.style_flat(Color(0.07, 0.06, 0.13, 0.9), border, 10, 2, 0, 8))
	b.add_theme_stylebox_override("hover", UI.style_flat(Color(0.14, 0.12, 0.24, 0.95), UI.GOLD, 10, 3, 0, 8))
	b.add_theme_stylebox_override("pressed", UI.style_flat(Color(0.14, 0.12, 0.24, 0.95), UI.GOLD, 10, 3, 0, 8))
	var tpl := Data.template(String(m["class_id"]))
	var hb := UI.hbox(8)
	hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hb.offset_left = 8
	hb.offset_top = 6
	hb.offset_right = -8
	hb.add_child(UI.tex_rect(UI.class_icon(String(m["class_id"])), Vector2(64, 64)))
	var tv := UI.vbox(0)
	tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var nm := UI.lbl(String(m["name"]) + ("  ✦" if m["shiny"] else "") + ("  ⚜" if m["legendary"] else ""), 18, UI.TEXT, true)
	nm.clip_text = true
	tv.add_child(nm)
	tv.add_child(UI.lbl("Niv. %d • %s" % [m["level"], tpl["name"]], 14, Data.ROLE_COLOR.get(tpl["role"], UI.TEXT_DIM), true))
	tv.add_child(UI.lbl("Force %d • %s" % [int(MercLogic.rating(m)), "★".repeat(MercLogic.star_rating(m))], 14, UI.TEXT_DIM))
	var flags := ""
	if int(m["pending_levels"]) > 0: flags += "⬆ "
	if m.get("pending_mastery", false): flags += "✦ "
	if not (m["injury"] as Dictionary).is_empty(): flags += "🩹 "
	if flags != "":
		tv.add_child(UI.lbl(flags, 15, UI.GOLD, true))
	hb.add_child(tv)
	var rb := UI.vbox(2)
	rb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rb.add_child(UI.lbl("TITULAIRE" if in_line else "", 12, UI.GOLD, true))
	hb.add_child(rb)
	b.add_child(hb)
	var uid: String = m["uid"]
	b.mouse_entered.connect(func(): _preview(m))
	b.pressed.connect(func(): hub.open_fighter(uid))
	# bascule titulaire (clic droit)
	b.gui_input.connect(func(ev: InputEvent):
		if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_RIGHT:
			if in_line:
				c.lineup.erase(uid)
			elif c.lineup.size() < 5:
				c.lineup.append(uid)
			else:
				Game.toast("Équipe complète : retire un titulaire d'abord.", "error")
				return
			hub.refresh())
	b.tooltip_text = "Clic : fiche détaillée • Clic droit : titulaire / remplaçant"
	return b
