class_name HubHome
extends Control
## Onglet Accueil : événements de la semaine, alignement, classement, finances, alertes.

var hub: Node
var c: Campaign
var left_col: VBoxContainer
var right_col: VBoxContainer
var bottom: Control

func _ready() -> void:
	c = hub.c
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	rebuild()

func rebuild() -> void:
	for ch in get_children():
		ch.queue_free()
	c = hub.c
	# colonne gauche : événements
	left_col = UI.vbox(10)
	left_col.position = Vector2(0, 0)
	left_col.custom_minimum_size = Vector2(520, 0)
	add_child(left_col)
	left_col.add_child(_week_card())
	for ev in c.events_this_week():
		if ev["kind"] != "bye":
			left_col.add_child(_event_card(ev))
	var nxt := UI.btn("▶  SEMAINE SUIVANTE", "primary", Vector2(0, 62))
	nxt.disabled = not c.main_event_done()
	nxt.pressed.connect(hub.next_week)
	left_col.add_child(nxt)
	if not c.main_event_done():
		var tip := UI.lbl("Joue ou simule l'événement principal pour avancer.", 15, UI.TEXT_DIM)
		left_col.add_child(tip)
	# colonne droite
	right_col = UI.vbox(10)
	right_col.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	right_col.offset_left = -440
	right_col.custom_minimum_size = Vector2(440, 0)
	add_child(right_col)
	right_col.add_child(_alerts_card())
	right_col.add_child(_table_card())
	right_col.add_child(_finance_card())
	# bandeau bas : alignement
	bottom = _lineup_strip()
	bottom.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	bottom.grow_horizontal = Control.GROW_DIRECTION_BOTH
	bottom.grow_vertical = Control.GROW_DIRECTION_BEGIN
	add_child(bottom)

func _week_card() -> Control:
	var p := UI.panel("glass")
	var v := UI.vbox(2)
	p.add_child(v)
	v.add_child(UI.lbl(c.week_title().to_upper(), 24, UI.GOLD, false, true))
	var opp := c.opponent_id()
	if opp != "" and c.is_league_week():
		var h := UI.hbox(10)
		h.add_child(LogoView.new(c.logo_of(opp), 44))
		var tv := UI.vbox(0)
		tv.add_child(UI.lbl("Prochain adversaire : %s" % c.team_name_of(opp), 19, UI.TEXT, true))
		var orat := c.ai_team_rating(opp)
		var mrat := c.team_rating(c.lineup_mercs())
		var diff := mrat - orat
		var txt := "Favoris" if diff > mrat * 0.08 else ("Outsiders" if diff < -mrat * 0.08 else "Match équilibré")
		tv.add_child(UI.lbl("%s • force %d vs %d" % [txt, int(mrat), int(orat)], 15, UI.TEXT_DIM))
		h.add_child(tv)
		v.add_child(h)
	return p

func _event_card(ev: Dictionary) -> Control:
	var p := UI.panel("glass")
	var h := UI.hbox(10)
	p.add_child(h)
	var icon: String = {"league": "league", "cup": "cup", "special_3v3v3v3": "trophy", "academy": "academy", "academy_placement": "academy", "tower": "tower", "draft": "draft", "chaos": "thunder"}.get(String(ev["kind"]), "swords")
	h.add_child(UI.tex_rect(UI.stat_icon(icon), Vector2(38, 38)))
	var tv := UI.vbox(0)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(UI.lbl(String(ev["label"]), 19, UI.TEXT, true))
	var sub := "Événement principal" if ev["main"] else "Optionnel"
	if ev.has("opp"):
		sub += " • vs " + c.team_name_of(String(ev["opp"]))
	tv.add_child(UI.lbl(sub, 14, UI.GOLD if ev["main"] else UI.TEXT_DIM))
	h.add_child(tv)
	if ev["done"]:
		h.add_child(UI.lbl("✔ Terminé", 17, UI.GOOD, true))
	else:
		var play := UI.btn("Jouer", "primary", Vector2(96, 42))
		play.pressed.connect(func(): hub.play_event(ev))
		h.add_child(play)
		if ev["kind"] in ["league", "cup", "special_3v3v3v3", "academy", "academy_placement"]:
			var sim := UI.btn("Simuler", "secondary", Vector2(96, 42))
			sim.pressed.connect(func():
				var cfg: Dictionary = hub.build_config(ev)
				hub.run_event(ev, cfg, true))
			h.add_child(sim)
	return p

func _alerts_card() -> Control:
	var p := UI.panel("glass")
	var v := UI.vbox(3)
	p.add_child(v)
	v.add_child(UI.lbl("Alertes", 20, UI.GOLD, true))
	var any := false
	for m in c.roster:
		if int(m["pending_levels"]) > 0:
			any = true
			var b := UI.btn("⬆ %s : choix de niveau" % m["name"], "secondary", Vector2(0, 32))
			var uid: String = m["uid"]
			b.pressed.connect(func(): hub.open_fighter(uid))
			v.add_child(b)
		elif m.get("pending_mastery", false):
			any = true
			var b2 := UI.btn("✦ %s : maîtrise disponible" % m["name"], "secondary", Vector2(0, 32))
			var uid2: String = m["uid"]
			b2.pressed.connect(func(): hub.open_fighter(uid2))
			v.add_child(b2)
		if not (m["injury"] as Dictionary).is_empty():
			any = true
			v.add_child(UI.lbl("🩹 %s — %s (%d)" % [m["name"], m["injury"]["desc"], m["injury"]["battles"]], 15, UI.BAD))
	for l in c.market["fighters"]:
		if l.get("superstar", false):
			any = true
			v.add_child(UI.lbl("🔥 Fièvre des transferts : %s au marché !" % l["merc"]["name"], 15, Color("ffb060"), true))
			break
	if c.roster.size() > Market.roster_capacity(c):
		v.add_child(UI.lbl("Effectif au-dessus de la capacité !", 15, UI.BAD))
	if c.lineup.size() < 5:
		any = true
		v.add_child(UI.lbl("⚠ Équipe incomplète (%d/5)" % c.lineup.size(), 15, UI.BAD, true))
	if not any:
		v.add_child(UI.lbl("Rien à signaler.", 16, UI.TEXT_DIM))
	return p

func _table_card() -> Control:
	var p := UI.panel("glass")
	var v := UI.vbox(2)
	p.add_child(v)
	v.add_child(UI.lbl("%s — Classement" % c.division_name(c.player_div), 20, UI.GOLD, true))
	var sorted := c.sorted_standings(c.player_div)
	var my := sorted.find(c.player_id)
	var show: Array = []
	for i in sorted.size():
		if i < 4 or abs(i - my) <= 1 or i >= sorted.size() - 1:
			show.append(i)
	var last := -2
	for i in show:
		if i > last + 1:
			v.add_child(UI.lbl("   …", 14, UI.TEXT_DIM))
		last = i
		var tid: String = sorted[i]
		var st: Dictionary = c.standings[tid]
		var row := UI.hbox(6)
		var col := UI.GOLD if tid == c.player_id else UI.TEXT
		var l1 := UI.lbl("%2d" % (i + 1), 16, UI.TEXT_DIM, true)
		l1.custom_minimum_size = Vector2(28, 0)
		row.add_child(l1)
		row.add_child(LogoView.new(c.logo_of(tid), 22))
		var nm := UI.lbl(c.team_name_of(tid), 16, col, tid == c.player_id)
		nm.custom_minimum_size = Vector2(220, 0)
		nm.clip_text = true
		row.add_child(nm)
		row.add_child(UI.lbl("%dV-%dD" % [st["w"], st["l"]], 15, UI.TEXT_DIM))
		var pts := UI.lbl("%d pts" % st["pts"], 16, col, true)
		pts.custom_minimum_size = Vector2(60, 0)
		pts.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		row.add_child(pts)
		v.add_child(row)
	return p

func _finance_card() -> Control:
	var p := UI.panel("glass")
	var v := UI.vbox(2)
	p.add_child(v)
	v.add_child(UI.lbl("Finances hebdomadaires", 20, UI.GOLD, true))
	var inc := Market.weekly_income(c)
	var cost := Market.weekly_costs(c)
	v.add_child(UI.lbl("Sponsors : +%s   •   Salaires : -%s" % [Game.format_gold(inc), Game.format_gold(cost)], 16))
	var net := inc - cost
	v.add_child(UI.lbl("Bilan : %s%s or / semaine (hors primes)" % ["+" if net >= 0 else "", Game.format_gold(net)], 16, UI.GOOD if net >= 0 else UI.BAD, true))
	if c.results_log.size() > 0:
		v.add_child(UI.hsep())
		v.add_child(UI.lbl("Derniers résultats", 17, UI.TEXT_DIM, true))
		for r in c.results_log.slice(0, 4):
			var txt := "%s %d-%d  %s" % ["V" if r["won"] else "D", r["score"][0], r["score"][1], c.team_name_of(String(r["opp"])) if String(r["opp"]) != "" else String(r["kind"])]
			v.add_child(UI.lbl(txt, 15, UI.GOOD if r["won"] else UI.BAD))
	return p

func _lineup_strip() -> Control:
	var p := UI.panel("glass")
	var v := UI.vbox(4)
	p.add_child(v)
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("Équipe titulaire", 18, UI.GOLD, true))
	hd.add_child(UI.spacer(0, 0, true))
	var auto := UI.btn("Composition auto", "secondary", Vector2(160, 30))
	auto.pressed.connect(func():
		c.auto_lineup()
		hub.refresh())
	hd.add_child(auto)
	var edit := UI.btn("Gérer l'effectif", "secondary", Vector2(150, 30))
	edit.pressed.connect(func(): hub.open_tab("roster"))
	hd.add_child(edit)
	v.add_child(hd)
	var row := UI.hbox(8)
	for m in c.lineup_mercs():
		row.add_child(_mini_card(m))
	v.add_child(row)
	return p

func _mini_card(m: Dictionary) -> Control:
	var b := Button.new()
	b.custom_minimum_size = Vector2(176, 66)
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_stylebox_override("normal", UI.style_flat(Color(0.06, 0.05, 0.11, 0.85), Color("4a4068"), 8, 2, 0, 6))
	b.add_theme_stylebox_override("hover", UI.style_flat(Color(0.12, 0.1, 0.2, 0.95), UI.GOLD, 8, 2, 0, 6))
	b.add_theme_stylebox_override("pressed", UI.style_flat(Color(0.12, 0.1, 0.2, 0.95), UI.GOLD, 8, 2, 0, 6))
	var hb := UI.hbox(6)
	hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hb.offset_left = 6
	hb.offset_top = 4
	hb.add_child(UI.tex_rect(UI.class_icon(String(m["class_id"])), Vector2(46, 46)))
	var tv := UI.vbox(0)
	tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var tpl := Data.template(String(m["class_id"]))
	var nm := UI.lbl(String(m["name"]), 16, UI.TEXT, true)
	nm.clip_text = true
	nm.custom_minimum_size = Vector2(110, 0)
	tv.add_child(nm)
	tv.add_child(UI.lbl("Niv. %d %s" % [m["level"], tpl["name"]], 13, Data.ROLE_COLOR.get(tpl["role"], UI.TEXT_DIM)))
	if int(m["pending_levels"]) > 0:
		tv.add_child(UI.lbl("⬆ Niveau !", 13, UI.GOLD, true))
	hb.add_child(tv)
	b.add_child(hb)
	var uid: String = m["uid"]
	b.pressed.connect(func(): hub.open_fighter(uid))
	return b
