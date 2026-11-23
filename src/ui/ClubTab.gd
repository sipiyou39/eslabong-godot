class_name ClubTab
extends Control
## Onglet Club : installations (Maison du club, Bureau des recruteurs, Caserne, Terrain d'entraînement) et personnel.

var hub: Node
var c: Campaign

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
	var v := UI.vbox(10)
	p.add_child(v)
	v.add_child(UI.lbl("LE CLUB", 30, UI.GOLD, false, true))
	var cols := UI.hbox(18)
	cols.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(cols)
	var left := UI.vbox(10)
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.add_child(UI.lbl("Installations", 24, UI.GOLD, true))
	for f in Data.facility_defs:
		left.add_child(_facility(f))
	cols.add_child(left)
	var right := UI.vbox(8)
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right.add_child(UI.lbl("Personnel  (-%s or / semaine)" % Game.format_gold(Market.staff_weekly(c)), 24, UI.GOLD, true))
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var sv := UI.vbox(8)
	sv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(sv)
	for s in Data.staff_defs:
		sv.add_child(_staff(s))
	right.add_child(sc)
	cols.add_child(right)

func _facility(f: Dictionary) -> Control:
	var fid: String = f["id"]
	var lv := int(c.facilities.get(fid, 1))
	var mx := int(f["max_level"])
	var p := UI.panel("card")
	var h := UI.hbox(12)
	p.add_child(h)
	var icon: String = {"club_house": "facility_clubhouse", "scouting_office": "facility_scouting", "barracks": "facility_barracks", "training_grounds": "facility_grounds"}.get(fid, "club")
	h.add_child(UI.tex_rect(UI.stat_icon(icon), Vector2(64, 64)))
	var tv := UI.vbox(2)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(UI.lbl("%s — niveau %d / %d" % [f["name"], lv, mx], 21, UI.TEXT, true))
	var d := UI.lbl(String(f["desc"]), 15, UI.TEXT_DIM)
	d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	d.custom_minimum_size = Vector2(420, 0)
	tv.add_child(d)
	var bar := UIBar.new(UI.GOLD, 10)
	bar.segments = mx
	bar.set_values(float(lv), float(mx))
	tv.add_child(bar)
	var eff := ""
	match fid:
		"club_house": eff = "Capacité %d • sponsors +%d/sem." % [Market.roster_capacity(c), 55 * lv]
		"scouting_office": eff = "%d annonces • meilleurs tirages" % (9 + lv * 2)
		"barracks": eff = "XP du banc +%d%% • entraînement" % (8 * (lv - 1) + 35)
		"training_grounds": eff = "Respec ciblé • Renaissance • Académie"
	tv.add_child(UI.lbl(eff, 14, UI.GOOD))
	h.add_child(tv)
	if lv < mx:
		var cost := Market.facility_cost(c, fid)
		var b := UI.btn("Améliorer  %s" % Game.format_gold(cost), "primary", Vector2(190, 48))
		b.icon = UI.stat_icon("gold")
		b.expand_icon = true
		b.disabled = c.gold < cost
		b.pressed.connect(func():
			if Market.upgrade_facility(c, fid):
				Audio.ui("ui_levelup")
				hub.refresh())
		h.add_child(b)
	else:
		h.add_child(UI.lbl("MAX", 22, UI.GOLD, true))
	return p

func _staff(s: Dictionary) -> Control:
	var sid: String = s["id"]
	var p := UI.panel("card")
	var h := UI.hbox(10)
	p.add_child(h)
	h.add_child(UI.tex_rect(UI.stat_icon("staff"), Vector2(46, 46)))
	var tv := UI.vbox(0)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(UI.lbl(String(s["name"]), 19, UI.TEXT, true))
	var d := UI.lbl(String(s["desc"]), 14, UI.TEXT_DIM)
	d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	d.custom_minimum_size = Vector2(300, 0)
	tv.add_child(d)
	if c.staff.has(sid):
		tv.add_child(UI.lbl("Employé : %s" % c.staff[sid]["name"], 14, UI.GOOD, true))
	h.add_child(tv)
	if c.staff.has(sid):
		var f := UI.btn("Renvoyer", "danger", Vector2(100, 38))
		f.pressed.connect(func():
			Market.fire_staff(c, sid)
			hub.refresh())
		h.add_child(f)
	else:
		var cost := Market.staff_cost(c, sid)
		var b := UI.btn("Recruter %s" % Game.format_gold(cost), "primary", Vector2(160, 38))
		b.disabled = c.gold < cost
		b.pressed.connect(func():
			if Market.hire_staff(c, sid):
				Audio.ui("ui_buy")
				hub.refresh())
		h.add_child(b)
	return p
