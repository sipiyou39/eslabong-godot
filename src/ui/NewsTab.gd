class_name NewsTab
extends Control
## Onglet Actualités : fil des événements (transferts, matchs, succès…), filtrable.

var hub: Node
var c: Campaign
var filter: String = "all"

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
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("ACTUALITÉS", 30, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	for f in [["all", "Tout"], ["match", "Matchs"], ["transfer", "Transferts"], ["market", "Marché IA"], ["achievement", "Succès"]]:
		var b := UI.btn(String(f[1]), "primary" if filter == f[0] else "secondary", Vector2(120, 36))
		b.pressed.connect(func():
			filter = f[0]
			rebuild())
		hd.add_child(b)
	v.add_child(hd)
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(sc)
	var list := UI.vbox(4)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(list)
	for n in c.news:
		if filter != "all" and String(n["k"]) != filter:
			continue
		var col: Color = {"match": UI.TEXT, "transfer": Color("ffb060"), "achievement": UI.GOLD, "trophy": UI.GOLD, "injury": UI.BAD, "promotion": UI.GOOD, "market": UI.TEXT_DIM}.get(String(n["k"]), UI.TEXT)
		var l := UI.lbl("S%d  Sem. %d — %s" % [n["s"], n["w"], n["t"]], 17, col)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(1000, 0)
		list.add_child(l)
