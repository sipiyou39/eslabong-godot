class_name PostMatchScreen
extends Control
## Rapport de fin de match : résultat, or, XP et niveaux, MVP, blessures, médailles, coffre.

signal closed

var hub: Node
var c: Campaign
var rep: Dictionary

func setup(h: Node, camp: Campaign, r: Dictionary) -> void:
	hub = h
	c = camp
	rep = r

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.82)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1100, 740))
	add_child(p)
	var v := UI.vbox(8)
	p.add_child(v)
	var won: bool = rep["won"]
	var title := UI.lbl("VICTOIRE" if won else "DÉFAITE", 60, UI.GOLD if won else Color("e8505a"), false, true)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UI.shadowed(title, Color(0, 0, 0, 0.8), 10)
	v.add_child(title)
	var res: Dictionary = rep.get("result", {})
	var ev: Dictionary = rep.get("event", {})
	var sub := String(ev.get("label", ""))
	if res.has("wins"):
		sub += "  •  manches " + " - ".join((res["wins"] as Array).map(func(x): return str(x)))
	if res.get("simulated", false):
		sub += "  (simulé)"
	var sl := UI.lbl(sub, 20, UI.TEXT_DIM, true)
	sl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(sl)
	var gr := UI.hbox(8)
	gr.alignment = BoxContainer.ALIGNMENT_CENTER
	gr.add_child(UI.tex_rect(UI.stat_icon("gold"), Vector2(32, 32)))
	gr.add_child(UI.lbl("+%s or" % Game.format_gold(rep["gold"]), 28, UI.GOLD, true))
	if int(rep.get("placement", 1)) > 1 or String(ev.get("kind", "")) in ["special_3v3v3v3", "chaos"]:
		gr.add_child(UI.lbl("  •  place %d" % int(rep.get("placement", 1)), 22, UI.TEXT, true))
	v.add_child(gr)
	v.add_child(UI.hsep())
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(sc)
	var list := UI.vbox(5)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(list)
	for f in rep["fighters"]:
		list.add_child(_row(f))
	var bh := UI.hbox(10)
	bh.alignment = BoxContainer.ALIGNMENT_CENTER
	if not (rep.get("chest", {}) as Dictionary).is_empty():
		var cb := UI.btn("🎁  Ouvrir le coffre", "primary", Vector2(260, 54))
		cb.pressed.connect(func():
			var ch := ChestScreen.new()
			ch.reward = rep["chest"]
			hub.open_modal(ch)
			cb.disabled = true)
		bh.add_child(cb)
	var ok := UI.btn("Continuer", "secondary", Vector2(220, 54))
	ok.pressed.connect(func():
		closed.emit()
		queue_free()
		hub.refresh())
	bh.add_child(ok)
	v.add_child(bh)
	UI.pop_in(p)
	Audio.ui("ui_unlock" if won else "ui_back")

func _row(f: Dictionary) -> Control:
	var p := UI.panel("inset")
	var h := UI.hbox(10)
	p.add_child(h)
	h.add_child(UI.tex_rect(UI.class_icon(String(f.get("class_id", ""))), Vector2(44, 44)))
	var tv := UI.vbox(0)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var nm := UI.lbl(("★ MVP  " if f.get("mvp", false) else "") + String(f["name"]) + ("  (banc)" if f.get("bench", false) else ""), 19, UI.GOLD if f.get("mvp", false) else UI.TEXT, true)
	tv.add_child(nm)
	var details: Array[String] = []
	if f.has("kills"):
		details.append("%d éliminations • %d assist. • %d dégâts • %d soins" % [f["kills"], f["assists"], f["damage"], f["healing"]])
	if String(f["injury"]) != "":
		details.append("🩹 Blessé : %s" % f["injury"])
	for md in f["medals"]:
		details.append("🏅 Médaille : %s (palier %d)" % [md["medal"], md["tier"]])
	tv.add_child(UI.lbl("  •  ".join(details), 14, UI.BAD if String(f["injury"]) != "" else UI.TEXT_DIM))
	h.add_child(tv)
	h.add_child(UI.lbl("+%d XP" % f["xp"], 18, Color("8ac8ff"), true))
	if int(f["levels"]) > 0:
		h.add_child(UI.lbl("⬆ Niveau %d !" % f["level"], 20, UI.GOLD, true))
	return p
