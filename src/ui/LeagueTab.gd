class_name LeagueTab
extends Control
## Onglet Ligue & Calendrier : classements des 4 divisions, calendrier du joueur, tableau de la Coupe des Champions.

var hub: Node
var c: Campaign
var shown_div: int = 0

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	shown_div = hub.c.player_div
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
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("LIGUE & CALENDRIER", 30, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	for d in c.divisions.size():
		var b := UI.btn("D%d" % (d + 1), "primary" if d == shown_div else "secondary", Vector2(64, 38))
		b.pressed.connect(func():
			shown_div = d
			rebuild())
		hd.add_child(b)
	v.add_child(hd)
	var body := UI.hbox(16)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	body.add_child(_table())
	body.add_child(_right())

func _table() -> Control:
	var sc := ScrollContainer.new()
	sc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := UI.vbox(3)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v)
	v.add_child(UI.lbl("%s  •  1er & 2e promus, 12e & 13e relégués" % c.division_name(shown_div), 16, UI.TEXT_DIM, true))
	var head := UI.hbox(0)
	for h in [["#", 36], ["Club", 300], ["J", 40], ["V", 40], ["D", 40], ["Manches", 90], ["Pts", 60]]:
		var l := UI.lbl(h[0], 15, UI.TEXT_DIM, true)
		l.custom_minimum_size = Vector2(h[1], 0)
		head.add_child(l)
	v.add_child(head)
	var sorted := c.sorted_standings(shown_div)
	for i in sorted.size():
		var tid: String = sorted[i]
		var st: Dictionary = c.standings[tid]
		var mine := tid == c.player_id
		var row := PanelContainer.new()
		var bg := Color(0.9, 0.7, 0.2, 0.16) if mine else (Color(0.2, 0.7, 0.3, 0.1) if i < 2 and shown_div > 0 else (Color(0.8, 0.2, 0.2, 0.1) if i >= sorted.size() - 2 and shown_div < 3 else Color(0, 0, 0, 0.25)))
		row.add_theme_stylebox_override("panel", UI.style_flat(bg, Color.TRANSPARENT, 6, 0, 0, 6))
		var h := UI.hbox(0)
		row.add_child(h)
		var col := UI.GOLD if mine else UI.TEXT
		var l1 := UI.lbl(str(i + 1), 17, UI.TEXT_DIM, true)
		l1.custom_minimum_size = Vector2(36, 0)
		h.add_child(l1)
		var nbox := UI.hbox(8)
		nbox.custom_minimum_size = Vector2(300, 0)
		nbox.add_child(LogoView.new(c.logo_of(tid), 26))
		nbox.add_child(UI.lbl(c.team_name_of(tid), 17, col, mine))
		h.add_child(nbox)
		for val in [[str(st["p"]), 40], [str(st["w"]), 40], [str(st["l"]), 40], ["%d-%d" % [st["rf"], st["ra"]], 90], [str(st["pts"]), 60]]:
			var l := UI.lbl(val[0], 17, col, true)
			l.custom_minimum_size = Vector2(val[1], 0)
			h.add_child(l)
		v.add_child(row)
	return sc

func _right() -> Control:
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(520, 0)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := UI.vbox(6)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v)
	if not c.cup.is_empty():
		v.add_child(UI.lbl("Coupe des Champions", 22, UI.GOLD, true))
		for pr in c.cup.get("pairs", []):
			var a: String = pr[0]
			var b: String = pr[1]
			v.add_child(UI.lbl("%s  vs  %s" % [c.team_name_of(a), c.team_name_of(b)], 16, UI.GOLD if (a == c.player_id or b == c.player_id) else UI.TEXT))
		if c.cup.get("winner", "") != "":
			v.add_child(UI.lbl("🏆 Vainqueur : %s" % c.team_name_of(String(c.cup["winner"])), 18, UI.GOLD, true))
		v.add_child(UI.hsep())
	v.add_child(UI.lbl("Calendrier de la saison %d" % c.season, 22, UI.GOLD, true))
	var cal := ""
	for w in range(1, Campaign.WEEKS + 1):
		var tags: Array[String] = []
		if w <= Campaign.MATCHDAYS:
			var md: Array = c.fixtures[c.player_div][w - 1]
			var opp := ""
			for pr in md:
				if pr[0] == c.player_id:
					opp = c.team_name_of(pr[1]) + " (D)"
				elif pr[1] == c.player_id:
					opp = c.team_name_of(pr[0]) + " (E)"
			tags.append("Ligue : " + (opp if opp != "" else "exempt"))
		if w in Campaign.SPECIAL_WEEKS: tags.append("Coupe 3v3v3v3")
		if w in Campaign.ACADEMY_WEEKS: tags.append("Académie")
		if w == 25: tags.append("Placement Académie")
		if w in Campaign.TOWER_WEEKS: tags.append("Tour du Défi")
		if w in Campaign.DRAFT_WEEKS: tags.append("Draft")
		if w == 26: tags.append("Chaos Thunder")
		if w >= 27: tags.append("Coupe des Champions")
		var row := UI.hbox(8)
		var wl := UI.lbl("S%02d" % w, 15, UI.GOLD if w == c.week else UI.TEXT_DIM, true)
		wl.custom_minimum_size = Vector2(44, 0)
		row.add_child(wl)
		var tl := UI.lbl(" • ".join(tags), 14, UI.GOLD if w == c.week else (UI.TEXT_DIM if w < c.week else UI.TEXT))
		tl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		tl.custom_minimum_size = Vector2(440, 0)
		row.add_child(tl)
		v.add_child(row)
	return sc
