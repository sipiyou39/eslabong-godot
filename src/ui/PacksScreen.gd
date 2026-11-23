class_name PacksScreen
extends Control
## Packs (DLC) : Cosmos (science-fiction) et Olympe (dieux grecs). Activer un pack ajoute ses classes (marché, recrues, match
## personnalisé) et ses arènes (rotation de ligue, matchs rapides).

signal closed

var cards_box: HBoxContainer

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.82)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1420, 760))
	add_child(p)
	var v := UI.vbox(10)
	p.add_child(v)
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("PACKS", 40, UI.GOLD, false, true))
	var sub := UI.lbl("  Contenu supplémentaire — gratuit dans cette version", 20, UI.TEXT_DIM, true)
	sub.size_flags_vertical = Control.SIZE_SHRINK_END
	hd.add_child(sub)
	hd.add_child(UI.spacer(0, 0, true))
	var back := UI.btn("Retour", "secondary", Vector2(150, 50))
	back.pressed.connect(func():
		closed.emit()
		queue_free())
	hd.add_child(back)
	v.add_child(hd)
	cards_box = UI.hbox(16)
	cards_box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(cards_box)
	_build_cards()

func _build_cards() -> void:
	for c in cards_box.get_children():
		c.queue_free()
	for pk in Data.pack_list:
		cards_box.add_child(_card(pk))

func _card(pk: Dictionary) -> Control:
	var pid := String(pk["id"])
	var col := Color(String(pk.get("color", "#e0b85a")))
	var on := Data.pack_enabled(pid)
	var card := UI.panel("inset")
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var v := UI.vbox(8)
	card.add_child(v)
	var title := UI.lbl(String(pk["name"]).to_upper(), 38, col.lightened(0.25), false, true)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(title)
	var tag := UI.lbl(String(pk["tagline"]), 24, UI.TEXT, true)
	tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(tag)
	var ds := UI.lbl(String(pk["desc"]), 17, UI.TEXT_DIM, false)
	ds.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ds.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	ds.custom_minimum_size = Vector2(560, 0)
	v.add_child(ds)
	# vitrine 3D : 3 classes du pack
	var stages := UI.hbox(0)
	stages.alignment = BoxContainer.ALIGNMENT_CENTER
	var cl: Array = pk.get("classes", [])
	for i in mini(3, cl.size()):
		var st := CharacterStage.new(Vector2(190, 250))
		st.spin = true
		st.spin_speed = 0.5
		stages.add_child(st)
		st.set_template(Data.template(String(cl[[1, 0, 4][i] % cl.size()])))
	v.add_child(stages)
	# classes
	var names: Array[String] = []
	for cid in cl:
		names.append(String(Data.classes[cid]["name"]))
	var cn := UI.lbl("Classes : " + ", ".join(names), 17, UI.TEXT, false)
	cn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	cn.custom_minimum_size = Vector2(560, 0)
	v.add_child(cn)
	var an: Array[String] = []
	for aid in pk.get("arenas", []):
		if Data.extra_arena_themes.has(aid):
			an.append(String(Data.extra_arena_themes[aid].get("name", aid)))
	if not an.is_empty():
		var al := UI.lbl("Arènes : " + ", ".join(an), 17, UI.GOLD, true)
		al.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		al.custom_minimum_size = Vector2(560, 0)
		v.add_child(al)
	v.add_child(UI.spacer(0, 0, true))
	var b := UI.btn("Activé — toucher pour désactiver" if on else "Activer ce pack", "secondary" if on else "primary", Vector2(0, 62))
	b.pressed.connect(func():
		Settings.s("pack_" + pid, not Data.pack_enabled(pid))
		Settings.save()
		Data.rebuild_class_list()
		Audio.ui("ui_confirm")
		Game.toast("%s %s." % [String(pk["name"]), "activé" if Data.pack_enabled(pid) else "désactivé"], "good" if Data.pack_enabled(pid) else "info")
		_build_cards())
	v.add_child(b)
	return card
