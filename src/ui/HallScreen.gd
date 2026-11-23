class_name HallScreen
extends Control
## Hall des légendes : champions de ligue/coupes, combattants légendaires, trophées du club, historique des saisons.

signal closed

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.8)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1100, 700))
	add_child(p)
	var v := UI.vbox(10)
	p.add_child(v)
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("HALL DES LÉGENDES", 36, UI.GOLD, false, true))
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
	var c: Campaign = Game.campaign
	if c == null:
		c = Campaign.load_from()
	if c == null:
		list.add_child(UI.lbl("Aucune campagne en cours. Fonde un club pour écrire ta légende !", 22, UI.TEXT_DIM))
		return
	list.add_child(UI.lbl("Club : %s — %d trophée(s)" % [c.team_name, c.trophies.size()], 24, UI.GOLD, true))
	for t in c.trophies:
		list.add_child(UI.lbl("🏆  %s  (saison %d, semaine %d)" % [t["name"], t["s"], t["w"]], 20, UI.TEXT))
	list.add_child(UI.hsep())
	list.add_child(UI.lbl("Panthéon", 24, UI.GOLD, true))
	if c.hall_of_legends.is_empty():
		list.add_child(UI.lbl("Le panthéon est vide pour l'instant.", 18, UI.TEXT_DIM))
	var arr := c.hall_of_legends.duplicate()
	arr.reverse()
	for h in arr:
		var extra := ("  (niv. %d)" % int(h["level"])) if h.has("level") else ""
		list.add_child(UI.lbl("Saison %d • %s — %s%s" % [h["s"], h["t"], h["who"], extra], 18, UI.TEXT))
	list.add_child(UI.hsep())
	list.add_child(UI.lbl("Historique des saisons", 24, UI.GOLD, true))
	for h in c.history:
		list.add_child(UI.lbl("Saison %d : %s, rang %d • champion D1 : %s" % [h["season"], c.division_name(int(h["player_div"])), int(h["rank"]), ", ".join(h["champions"])], 18, UI.TEXT))
	list.add_child(UI.hsep())
	list.add_child(UI.lbl("Meilleurs combattants", 24, UI.GOLD, true))
	var best := c.roster.duplicate()
	best.sort_custom(func(a, b): return int(a["career"]["kills"]) > int(b["career"]["kills"]))
	for m in best.slice(0, 5):
		list.add_child(UI.lbl("%s — %d éliminations, %d assistances, %d PV soignés, MVP ×%d" % [m["name"], m["career"]["kills"], m["career"]["assists"], int(m["career"]["healing"]), m["career"]["mvp"]], 18, UI.TEXT))
