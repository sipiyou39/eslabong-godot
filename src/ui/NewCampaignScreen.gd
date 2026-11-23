class_name NewCampaignScreen
extends Control
## Création de campagne : nom, logo (héraldique), difficulté, 5 combattants de départ.

signal closed

var name_edit: LineEdit
var logo_view: LogoView
var recipe: Dictionary = {"shield": 3, "division": 5, "charge": 17, "base_color": "#1a1a22", "field_color": "#f2ead0", "charge_color": "#c0392b", "division_color": "#2f5ea8"}
var diff_opt: OptionButton
var candidates: Array = []
var picked: Array[String] = []
var cand_buttons: Dictionary = {}
var stage: CharacterStage
var count_label: Label
var found_btn: Button
var info_box: VBoxContainer
const PALETTE := ["#1a1a22", "#f2ead0", "#c0392b", "#2f5ea8", "#c9a227", "#2e7d4f", "#6a2c8a", "#e0e0e8", "#d9731c", "#12121a", "#8a1f2a", "#3aa0c8"]

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var rnd := RandomNumberGenerator.new()
	rnd.randomize()
	var roles := ["tank", "bruiser", "healer", "ranged", "mage", "assassin", "support", "bruiser", "ranged", "tank"]
	for i in 10:
		var pool := MatchFactory.classes_by_role(roles[i])
		var cdef: Dictionary = pool[rnd.randi() % pool.size()]
		candidates.append(MercLogic.generate(cdef["id"], rnd.randi_range(2, 3), rnd, {"quality": -0.01}))
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1380, 760))
	add_child(p)
	var v := UI.vbox(10)
	p.add_child(v)
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("NOUVELLE CAMPAGNE", 36, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	var back := UI.btn("Retour", "secondary", Vector2(120, 42))
	back.pressed.connect(func():
		closed.emit()
		queue_free())
	hd.add_child(back)
	v.add_child(hd)
	var body := UI.hbox(24)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	body.add_child(_left_col())
	body.add_child(_right_col())
	_refresh_picked()

func _left_col() -> Control:
	var v := UI.vbox(10)
	v.custom_minimum_size = Vector2(420, 0)
	v.add_child(UI.lbl("Nom du club", 20, UI.TEXT_DIM, true))
	name_edit = LineEdit.new()
	name_edit.text = ["Skvell D", "Ironvale Raiders", "Crimson Wolves", "Ashen Vanguard", "Gilded Ravens"][randi() % 5]
	name_edit.custom_minimum_size = Vector2(0, 44)
	name_edit.max_length = 24
	name_edit.add_theme_font_size_override("font_size", 22)
	v.add_child(name_edit)
	v.add_child(UI.lbl("Emblème", 20, UI.TEXT_DIM, true))
	var lrow := UI.hbox(14)
	logo_view = LogoView.new(recipe, 140)
	lrow.add_child(logo_view)
	var opts := UI.vbox(6)
	for it in [["Écu", "shield", 8], ["Partition", "division", 16], ["Meuble", "charge", 64]]:
		var r := UI.hbox(6)
		var lb := UI.lbl(it[0], 17)
		lb.custom_minimum_size = Vector2(90, 0)
		r.add_child(lb)
		var bl := UI.btn("◀", "secondary", Vector2(36, 34))
		var br := UI.btn("▶", "secondary", Vector2(36, 34))
		bl.pressed.connect(func(): _step(it[1], it[2], -1))
		br.pressed.connect(func(): _step(it[1], it[2], 1))
		r.add_child(bl)
		r.add_child(br)
		opts.add_child(r)
	var rb := UI.btn("Aléatoire", "secondary", Vector2(0, 34))
	rb.pressed.connect(_randomize_logo)
	opts.add_child(rb)
	lrow.add_child(opts)
	v.add_child(lrow)
	for it in [["Fond", "base_color"], ["Champ", "field_color"], ["Partition", "division_color"], ["Meuble", "charge_color"]]:
		v.add_child(_color_row(it[0], it[1]))
	v.add_child(UI.lbl("Difficulté", 20, UI.TEXT_DIM, true))
	diff_opt = OptionButton.new()
	for d in Campaign.DIFFICULTY_NAMES:
		diff_opt.add_item(d)
	diff_opt.selected = clampi(Settings.gi("next_campaign_difficulty"), 0, 3)
	diff_opt.custom_minimum_size = Vector2(0, 40)
	v.add_child(diff_opt)
	v.add_child(UI.spacer(0, 0, true))
	found_btn = UI.btn("Fonder le club", "primary", Vector2(0, 58))
	found_btn.pressed.connect(_found)
	v.add_child(found_btn)
	return v

func _color_row(label: String, key: String) -> Control:
	var r := UI.hbox(4)
	var l := UI.lbl(label, 16)
	l.custom_minimum_size = Vector2(80, 0)
	r.add_child(l)
	for c in PALETTE:
		var b := Button.new()
		b.custom_minimum_size = Vector2(24, 24)
		b.focus_mode = Control.FOCUS_NONE
		b.add_theme_stylebox_override("normal", UI.style_flat(Color(c), Color(1, 1, 1, 0.25), 4, 1, 0, 0))
		b.add_theme_stylebox_override("hover", UI.style_flat(Color(c), UI.GOLD, 4, 2, 0, 0))
		b.add_theme_stylebox_override("pressed", UI.style_flat(Color(c), UI.GOLD, 4, 2, 0, 0))
		b.pressed.connect(func():
			recipe[key] = c
			logo_view.set_recipe(recipe)
			Audio.ui("ui_click"))
		r.add_child(b)
	return r

func _step(key: String, mod: int, d: int) -> void:
	recipe[key] = (int(recipe[key]) + d + mod) % mod
	logo_view.set_recipe(recipe)
	Audio.ui("ui_click")

func _randomize_logo() -> void:
	recipe["shield"] = randi() % 8
	recipe["division"] = randi() % 16
	recipe["charge"] = randi() % 64
	for k in ["base_color", "field_color", "division_color", "charge_color"]:
		recipe[k] = PALETTE[randi() % PALETTE.size()]
	logo_view.set_recipe(recipe)

func _right_col() -> Control:
	var v := UI.vbox(8)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var h := UI.hbox(8)
	h.add_child(UI.lbl("Choisis tes 5 premiers mercenaires", 24, UI.GOLD, false, true))
	h.add_child(UI.spacer(0, 0, true))
	count_label = UI.lbl("0 / 5", 24, UI.TEXT, true)
	h.add_child(count_label)
	v.add_child(h)
	var body := UI.hbox(14)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(grid)
	for m in candidates:
		var b := Button.new()
		b.toggle_mode = true
		b.custom_minimum_size = Vector2(300, 84)
		b.focus_mode = Control.FOCUS_NONE
		b.add_theme_stylebox_override("normal", UI.style_flat(UI.PANEL, Color("4a4068"), 8, 2, 0, 8))
		b.add_theme_stylebox_override("hover", UI.style_flat(UI.PANEL_HI, UI.GOLD_DIM, 8, 2, 0, 8))
		b.add_theme_stylebox_override("pressed", UI.style_flat(Color("3a3050"), UI.GOLD, 8, 3, 0, 8))
		b.add_theme_stylebox_override("hover_pressed", UI.style_flat(Color("3a3050"), UI.GOLD, 8, 3, 0, 8))
		var hb := UI.hbox(10)
		hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
		hb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		hb.offset_left = 8
		hb.offset_right = -8
		hb.offset_top = 6
		hb.offset_bottom = -6
		hb.add_child(UI.tex_rect(UI.class_icon(String(m["class_id"])), Vector2(60, 60)))
		var tv := UI.vbox(0)
		tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var tpl := Data.template(String(m["class_id"]))
		tv.add_child(UI.lbl(String(m["name"]), 20, UI.TEXT, true))
		tv.add_child(UI.lbl("%s • %s" % [tpl["name"], Data.ROLE_NAME_FR.get(tpl["role"], "")], 15, Data.ROLE_COLOR.get(tpl["role"], UI.TEXT_DIM), true))
		tv.add_child(UI.lbl("Niv. %d • %s %s" % [m["level"], "★".repeat(MercLogic.star_rating(m)), "  ✦ " + String(Data.quirks[m["quirk"]]["name"]) if m["quirk"] != "" else ""], 14, UI.TEXT_DIM))
		hb.add_child(tv)
		b.add_child(hb)
		var uid: String = m["uid"]
		b.toggled.connect(func(on: bool): _toggle(uid, on, b))
		b.mouse_entered.connect(func(): _preview(m))
		cand_buttons[uid] = b
		grid.add_child(b)
	var side := UI.vbox(6)
	side.custom_minimum_size = Vector2(330, 0)
	stage = CharacterStage.new(Vector2(330, 360))
	side.add_child(stage)
	info_box = UI.vbox(4)
	side.add_child(info_box)
	body.add_child(side)
	_preview(candidates[0])
	return v

func _preview(m: Dictionary) -> void:
	stage.set_merc(m)
	for c in info_box.get_children():
		c.queue_free()
	var tpl := Data.template(String(m["class_id"]))
	info_box.add_child(UI.lbl("%s — %s" % [m["name"], tpl["name"]], 22, UI.GOLD, true))
	for row in MercLogic.describe_stats(m):
		var h := UI.hbox(6)
		h.add_child(UI.tex_rect(UI.stat_icon(row[0]), Vector2(20, 20)))
		var l := UI.lbl(str(row[1]), 17, UI.TEXT_DIM)
		l.custom_minimum_size = Vector2(110, 0)
		h.add_child(l)
		h.add_child(UI.lbl(str(row[2]), 17, UI.TEXT, true))
		info_box.add_child(h)
	var kit: Array = tpl["kit"]
	var abl := UI.hbox(4)
	for id in kit:
		var ab: Dictionary = Data.ability(String(id))
		var ic := UI.tex_rect(UI.ability_icon(ab), Vector2(44, 44))
		ic.mouse_filter = Control.MOUSE_FILTER_PASS
		ic.tooltip_text = "%s\n%s" % [ab.get("name", ""), BattleHUD._ability_desc(ab)]
		abl.add_child(ic)
	info_box.add_child(abl)

func _toggle(uid: String, on: bool, b: Button) -> void:
	if on:
		if picked.size() >= 5:
			b.set_pressed_no_signal(false)
			Audio.ui("ui_error")
			return
		picked.append(uid)
	else:
		picked.erase(uid)
	_refresh_picked()

func _refresh_picked() -> void:
	count_label.text = "%d / 5" % picked.size()
	count_label.add_theme_color_override("font_color", UI.GOOD if picked.size() == 5 else UI.TEXT)
	found_btn.disabled = picked.size() != 5

func _found() -> void:
	var nm := name_edit.text.strip_edges()
	if nm == "":
		nm = "Sans-Nom"
	var starters: Array = []
	for m in candidates:
		if m["uid"] in picked:
			starters.append(m)
	var c := Campaign.create(nm, recipe, diff_opt.selected, starters)
	Game.campaign = c
	c.save()
	Audio.ui("ui_confirm")
	Game.goto_hub()
