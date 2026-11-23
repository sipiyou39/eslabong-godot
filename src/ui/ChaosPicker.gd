class_name ChaosPicker
extends Control
## Coupe Chaos Thunder : choisir un champion (mercenaire) parmi l'effectif.

signal closed

var hub: Node
var c: Campaign
var ev: Dictionary

func setup(h: Node, camp: Campaign, e: Dictionary) -> void:
	hub = h
	c = camp
	ev = e

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.8)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(800, 680))
	add_child(p)
	var v := UI.vbox(8)
	p.add_child(v)
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("COUPE CHAOS THUNDER", 32, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	var back := UI.btn("Annuler", "secondary", Vector2(120, 40))
	back.pressed.connect(func():
		closed.emit()
		queue_free())
	hd.add_child(back)
	v.add_child(hd)
	var d := UI.lbl("Ton champion affronte 7 champions ou chefs nommés. Chacun pour soi : le dernier survivant gagne. Aucune blessure.", 17, UI.TEXT_DIM)
	d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	d.custom_minimum_size = Vector2(740, 0)
	v.add_child(d)
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(sc)
	var list := UI.vbox(6)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(list)
	var pool := c.roster.duplicate()
	pool.sort_custom(func(a, b): return MercLogic.rating(a) > MercLogic.rating(b))
	for m in pool:
		var b := UI.btn("", "secondary", Vector2(0, 64))
		var hb := UI.hbox(10)
		hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
		hb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		hb.offset_left = 8
		hb.add_child(UI.tex_rect(UI.class_icon(String(m["class_id"])), Vector2(50, 50)))
		var tpl := Data.template(String(m["class_id"]))
		var tv := UI.vbox(0)
		tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tv.add_child(UI.lbl("%s%s" % [m["name"], "  ⚜ Champion" if m["legendary"] or tpl["kind"] != "class" else ""], 19, UI.TEXT, true))
		tv.add_child(UI.lbl("Niv. %d • %s • force %d" % [m["level"], tpl["display_name"], int(MercLogic.rating(m))], 14, UI.TEXT_DIM))
		hb.add_child(tv)
		b.add_child(hb)
		var uid: String = m["uid"]
		b.pressed.connect(func():
			var cfg := Results.chaos_config(c, uid)
			closed.emit()
			queue_free()
			hub.run_event(ev, cfg, false))
		list.add_child(b)
