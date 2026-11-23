class_name DraftScreen
extends Control
## Coupe Draft : frais d'entrée, 5 choix de combattants parmi 4 propositions, puis lancement des 3 matchs.

signal closed

var hub: Node
var c: Campaign
var ev: Dictionary
var picks: Array = []
var round_i: int = 0
var rnd := RandomNumberGenerator.new()
var body: VBoxContainer
var level: int = 5
const ENTRY_FEE := 400

func setup(h: Node, camp: Campaign, e: Dictionary) -> void:
	hub = h
	c = camp
	ev = e

func _ready() -> void:
	theme = UI.theme()
	rnd.randomize()
	level = c.div_level(c.player_div) + 2
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.82)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1260, 700))
	add_child(p)
	body = UI.vbox(10)
	p.add_child(body)
	_intro()

func _clear() -> void:
	for ch in body.get_children():
		ch.queue_free()

func _intro() -> void:
	_clear()
	body.add_child(UI.lbl("COUPE DRAFT", 40, UI.GOLD, false, true))
	var d := UI.lbl("Frais d'entrée : %d or. Tu drafteras 5 combattants (4 propositions par tour) pour une équipe temporaire, puis tu affronteras 3 équipes. Plus tu gagnes, plus la récompense est grande ; 3 victoires = trophée.\nTes combattants habituels ne sont pas engagés et ne gagnent pas d'XP." % ENTRY_FEE, 20, UI.TEXT)
	d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	d.custom_minimum_size = Vector2(1100, 0)
	body.add_child(d)
	body.add_child(UI.spacer(0, 0, true))
	var h := UI.hbox(12)
	var go := UI.btn("Participer (-%d or)" % ENTRY_FEE, "primary", Vector2(300, 58))
	go.disabled = c.gold < ENTRY_FEE
	go.pressed.connect(func():
		c.gold -= ENTRY_FEE
		hub.update_topbar()
		_next_round())
	h.add_child(go)
	var back := UI.btn("Annuler", "secondary", Vector2(160, 58))
	back.pressed.connect(func():
		closed.emit()
		queue_free())
	h.add_child(back)
	body.add_child(h)

func _next_round() -> void:
	_clear()
	if round_i >= 5:
		_bracket()
		return
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("TOUR %d / 5 — choisis un combattant" % (round_i + 1), 30, UI.GOLD, false, true))
	body.add_child(hd)
	var roster_txt := ", ".join(picks.map(func(m): return String(m["name"])))
	body.add_child(UI.lbl("Équipe : %s" % (roster_txt if roster_txt != "" else "—"), 17, UI.TEXT_DIM))
	var row := UI.hbox(14)
	row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(row)
	for i in 4:
		var cdef: Dictionary = Data.class_list[rnd.randi() % Data.class_list.size()]
		var m := MercLogic.generate(cdef["id"], level + rnd.randi_range(-1, 2), rnd, {"shiny_chance": 0.05})
		row.add_child(_card(m))

func _card(m: Dictionary) -> Control:
	var p := UI.panel("card")
	var v := UI.vbox(4)
	p.add_child(v)
	var st := CharacterStage.new(Vector2(270, 300))
	st.set_merc(m)
	v.add_child(st)
	var tpl := Data.template(String(m["class_id"]))
	v.add_child(UI.lbl(String(m["name"]), 20, UI.GOLD, true))
	v.add_child(UI.lbl("Niv. %d • %s" % [m["level"], tpl["name"]], 16, Data.ROLE_COLOR.get(tpl["role"], UI.TEXT_DIM), true))
	for row in MercLogic.describe_stats(m).slice(0, 4):
		v.add_child(UI.lbl("%s : %s" % [row[1], row[2]], 14, UI.TEXT_DIM))
	var b := UI.btn("Drafter", "primary", Vector2(0, 42))
	b.pressed.connect(func():
		picks.append(m)
		round_i += 1
		Audio.ui("ui_confirm")
		_next_round())
	v.add_child(b)
	return p

func _bracket() -> void:
	_clear()
	body.add_child(UI.lbl("TON ÉQUIPE DRAFTÉE", 34, UI.GOLD, false, true))
	var row := UI.hbox(10)
	for m in picks:
		var tpl := Data.template(String(m["class_id"]))
		var v := UI.vbox(2)
		v.add_child(UI.tex_rect(UI.class_icon(String(m["class_id"])), Vector2(80, 80)))
		v.add_child(UI.lbl(String(m["name"]), 16, UI.TEXT, true))
		v.add_child(UI.lbl("Niv. %d %s" % [m["level"], tpl["name"]], 13, UI.TEXT_DIM))
		row.add_child(v)
	body.add_child(row)
	body.add_child(UI.spacer(0, 0, true))
	var go := UI.btn("Lancer le tournoi (3 matchs)", "primary", Vector2(380, 62))
	go.pressed.connect(func():
		c.draft_run = {"picks": picks, "match": 0, "wins": 0, "level": level}
		closed.emit()
		queue_free()
		DraftSeries.start_match(c, ev))
	body.add_child(go)
