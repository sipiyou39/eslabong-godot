class_name MatchPrep
extends Control
## Préparation de match : adversaire, composition (clic pour titulaire/remplaçant), tactiques rapides, mode de contrôle, lancement.

signal closed

var hub: Node
var c: Campaign
var ev: Dictionary
var chosen: Array = []
var max_n: int = 5
var list_box: VBoxContainer
var count_lbl: Label
var go_btn: Button
var sim_btn: Button
var manual_check: CheckBox
var posture: String = "balanced"
var academy: bool = false

func setup(h: Node, camp: Campaign, e: Dictionary) -> void:
	hub = h
	c = camp
	ev = e
	academy = String(e["kind"]) in ["academy", "academy_placement"]
	max_n = 3 if academy or String(e["kind"]) == "special_3v3v3v3" else 5

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1300, 740))
	add_child(p)
	var v := UI.vbox(10)
	p.add_child(v)
	var hd := UI.hbox(10)
	hd.add_child(UI.lbl(String(ev["label"]).to_upper(), 32, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	var back := UI.btn("Annuler", "secondary", Vector2(120, 42))
	back.pressed.connect(func():
		closed.emit()
		queue_free())
	hd.add_child(back)
	v.add_child(hd)
	var body := UI.hbox(18)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	body.add_child(_left())
	body.add_child(_right())
	_init_chosen()
	_refresh()

func _init_chosen() -> void:
	chosen = []
	if academy:
		for m in c.bench_mercs():
			if chosen.size() < 3 and MercLogic.is_available(m):
				chosen.append(m["uid"])
	else:
		for u in c.lineup:
			if chosen.size() < max_n:
				chosen.append(u)

func _left() -> Control:
	var v := UI.vbox(6)
	v.custom_minimum_size = Vector2(640, 0)
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("Ta composition", 24, UI.GOLD, true))
	count_lbl = UI.lbl("", 22, UI.TEXT, true)
	hd.add_child(count_lbl)
	v.add_child(hd)
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(sc)
	list_box = UI.vbox(5)
	list_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(list_box)
	var pool := c.roster.duplicate()
	pool.sort_custom(func(a, b): return MercLogic.rating(a) > MercLogic.rating(b))
	for m in pool:
		list_box.add_child(_row(m))
	return v

func _row(m: Dictionary) -> Control:
	var uid: String = m["uid"]
	var b := Button.new()
	b.toggle_mode = true
	b.custom_minimum_size = Vector2(0, 62)
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_stylebox_override("normal", UI.style_flat(Color(0.07, 0.06, 0.13, 0.9), Color("3a3358"), 8, 2, 0, 6))
	b.add_theme_stylebox_override("hover", UI.style_flat(Color(0.14, 0.12, 0.24, 0.95), UI.GOLD_DIM, 8, 2, 0, 6))
	b.add_theme_stylebox_override("pressed", UI.style_flat(Color(0.22, 0.18, 0.1, 0.95), UI.GOLD, 8, 3, 0, 6))
	b.add_theme_stylebox_override("hover_pressed", UI.style_flat(Color(0.22, 0.18, 0.1, 0.95), UI.GOLD, 8, 3, 0, 6))
	b.button_pressed = uid in chosen
	var tpl := Data.template(String(m["class_id"]))
	var hb := UI.hbox(10)
	hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hb.offset_left = 8
	hb.offset_top = 4
	hb.add_child(UI.tex_rect(UI.class_icon(String(m["class_id"])), Vector2(48, 48)))
	var tv := UI.vbox(0)
	tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(UI.lbl(String(m["name"]), 18, UI.TEXT, true))
	tv.add_child(UI.lbl("Niv. %d • %s • force %d" % [m["level"], tpl["name"], int(MercLogic.rating(m))], 14, Data.ROLE_COLOR.get(tpl["role"], UI.TEXT_DIM)))
	hb.add_child(tv)
	if not (m["injury"] as Dictionary).is_empty():
		hb.add_child(UI.lbl("🩹 -20%", 16, UI.BAD, true))
	b.add_child(hb)
	b.toggled.connect(func(on: bool):
		if on:
			if chosen.size() >= max_n:
				b.set_pressed_no_signal(false)
				Audio.ui("ui_error")
				return
			chosen.append(uid)
		else:
			chosen.erase(uid)
		_refresh())
	return b

func _right() -> Control:
	var v := UI.vbox(10)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var opp_id: String = String(ev.get("opp", ""))
	var card := UI.panel("card")
	var cv := UI.vbox(6)
	card.add_child(cv)
	if opp_id != "":
		var oh := UI.hbox(14)
		oh.add_child(LogoView.new(c.logo_of(opp_id), 84))
		var ov := UI.vbox(2)
		ov.add_child(UI.lbl(c.team_name_of(opp_id), 30, UI.TEXT, false, true))
		var mrat := c.team_rating(_chosen_mercs())
		var orat := c.ai_team_rating(opp_id, max_n)
		ov.add_child(UI.lbl("Force : %d (toi) vs %d" % [int(mrat), int(orat)], 18, UI.TEXT_DIM, true))
		var win_prob := 1.0 / (1.0 + exp(-(mrat - orat) / maxf((mrat + orat) * 0.1, 1.0)))
		ov.add_child(UI.lbl("Chances estimées : %d%%" % int(win_prob * 100.0), 18, UI.GOOD if win_prob > 0.55 else (UI.BAD if win_prob < 0.45 else UI.TEXT), true))
		oh.add_child(ov)
		cv.add_child(oh)
		cv.add_child(UI.hsep())
		cv.add_child(UI.lbl("Leur équipe", 18, UI.GOLD, true))
		for sp in c.ai_specs(opp_id, max_n):
			var r := UI.hbox(8)
			r.add_child(UI.tex_rect(UI.class_icon(String(sp["template_id"])), Vector2(32, 32)))
			r.add_child(UI.lbl("%s — niv. %d %s" % [sp["name"], sp["level"], sp["tpl"]["name"]], 16))
			cv.add_child(r)
	else:
		cv.add_child(UI.lbl(String(ev["label"]), 24, UI.TEXT, false, true))
		cv.add_child(UI.lbl("Adversaires générés selon ta division.", 17, UI.TEXT_DIM))
	v.add_child(card)
	var tp := UI.panel("inset")
	var tv := UI.vbox(6)
	tp.add_child(tv)
	tv.add_child(UI.lbl("Posture tactique de l'équipe", 18, UI.GOLD, true))
	var pr := UI.hbox(6)
	for it in [["aggressive", "Offensive"], ["balanced", "Équilibrée"], ["defensive", "Défensive"]]:
		var b := UI.btn(String(it[1]), "primary" if posture == it[0] else "secondary", Vector2(130, 38))
		b.pressed.connect(func():
			posture = it[0]
			_apply_posture()
			for ch in pr.get_children():
				ch.queue_free()
			_posture_btns(pr))
		pr.add_child(b)
	tv.add_child(pr)
	manual_check = CheckBox.new()
	manual_check.text = "Prendre le contrôle direct d'un combattant (sinon : mode Manager / Spectateur)"
	manual_check.button_pressed = Settings.gi("player_1_input_mode") != 0
	manual_check.add_theme_font_size_override("font_size", 17)
	tv.add_child(manual_check)
	v.add_child(tp)
	v.add_child(UI.spacer(0, 0, true))
	var bh := UI.hbox(10)
	go_btn = UI.btn("COMBATTRE", "primary", Vector2(0, 62))
	go_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	go_btn.pressed.connect(func(): _launch(false))
	bh.add_child(go_btn)
	sim_btn = UI.btn("Simuler", "secondary", Vector2(160, 62))
	sim_btn.pressed.connect(func(): _launch(true))
	bh.add_child(sim_btn)
	v.add_child(bh)
	return v

func _posture_btns(pr: HBoxContainer) -> void:
	for it in [["aggressive", "Offensive"], ["balanced", "Équilibrée"], ["defensive", "Défensive"]]:
		var b := UI.btn(String(it[1]), "primary" if posture == it[0] else "secondary", Vector2(130, 38))
		b.pressed.connect(func():
			posture = it[0]
			_apply_posture()
			for ch in pr.get_children():
				ch.queue_free()
			_posture_btns(pr))
		pr.add_child(b)

func _apply_posture() -> void:
	for m in c.roster:
		var t: Dictionary = m["tactics"]
		match posture:
			"aggressive":
				t["aggression"] = minf(float(t.get("aggression", 0.6)) + 0.0, 1.0)
				t["posture"] = "aggressive"
			"defensive":
				t["posture"] = "defensive"
			_:
				t["posture"] = "balanced"

func _chosen_mercs() -> Array:
	var out: Array = []
	for u in chosen:
		var m := c.merc_by_uid(u)
		if not m.is_empty():
			out.append(m)
	return out

func _refresh() -> void:
	count_lbl.text = "%d / %d" % [chosen.size(), max_n]
	count_lbl.add_theme_color_override("font_color", UI.GOOD if chosen.size() == max_n else UI.BAD)
	if go_btn:
		go_btn.disabled = chosen.size() != max_n
		sim_btn.disabled = chosen.size() != max_n

func _launch(simulate: bool) -> void:
	if chosen.size() != max_n:
		return
	if not academy and String(ev["kind"]) != "special_3v3v3v3":
		c.lineup = chosen.duplicate()
	var cfg: Dictionary
	if academy:
		c.academy_lineup = chosen.duplicate()
		var cfg0 := Results.academy_config(c, ev)
		var mercs := _chosen_mercs()
		cfg0["teams"][0]["fighters"] = c.specs_for(mercs)
		cfg = cfg0
	elif String(ev["kind"]) == "special_3v3v3v3":
		cfg = Results.special_config(c, ev)
		cfg["teams"][0] = Results.player_team(c, 3, chosen)
	else:
		cfg = hub.build_config(ev)
	if posture == "aggressive":
		for sp in cfg["teams"][0]["fighters"]:
			sp["tactics"] = sp["tactics"].duplicate()
			sp["tactics"]["aggression"] = minf(float(sp["tactics"].get("aggression", 0.6)) + 0.2, 1.0)
	elif posture == "defensive":
		for sp in cfg["teams"][0]["fighters"]:
			sp["tactics"] = sp["tactics"].duplicate()
			sp["tactics"]["aggression"] = maxf(float(sp["tactics"].get("aggression", 0.6)) - 0.2, 0.05)
			sp["tactics"]["distance"] = 1.15
	Audio.ui("ui_confirm")
	var hubref: Node = hub
	var evc := ev
	queue_free()
	closed.emit()
	hubref.run_event(evc, cfg, simulate, manual_check.button_pressed if false else true)
