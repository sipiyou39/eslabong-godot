class_name AchievementsScreen
extends Control
## Liste des succès (mêmes identifiants que Steam) avec progression locale.

signal closed

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.8)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(900, 700))
	add_child(p)
	var v := UI.vbox(10)
	p.add_child(v)
	var c: Campaign = Game.campaign if Game.campaign else Campaign.load_from()
	var owned: Dictionary = c.achievements if c else {}
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("SUCCÈS  %d / %d" % [owned.size(), Achievements.LIST.size()], 34, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	var back := UI.btn("Fermer", "secondary", Vector2(120, 42))
	back.pressed.connect(func():
		closed.emit()
		queue_free())
	hd.add_child(back)
	v.add_child(hd)
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(sc)
	var list := UI.vbox(6)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(list)
	for id in Achievements.LIST:
		var has := owned.has(id)
		var row := UI.panel("inset")
		var h := UI.hbox(12)
		row.add_child(h)
		var ic := UI.tex_rect(UI.stat_icon("achievement" if has else "lock"), Vector2(44, 44), Color.WHITE if has else Color(0.5, 0.5, 0.55))
		h.add_child(ic)
		var tv := UI.vbox(0)
		tv.add_child(UI.lbl(Achievements.name_of(id), 21, UI.GOLD if has else UI.TEXT_DIM, true))
		tv.add_child(UI.lbl(Achievements.desc_of(id), 16, UI.TEXT_DIM))
		h.add_child(tv)
		if has:
			h.add_child(UI.spacer(0, 0, true))
			h.add_child(UI.lbl("Saison %d • sem. %d" % [owned[id]["s"], owned[id]["w"]], 15, UI.TEXT_DIM))
		list.add_child(row)
