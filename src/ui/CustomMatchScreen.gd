class_name CustomMatchScreen
extends Control
## Match rapide / personnalisé et mode Entraînement : composition libre des équipes, arène, niveau, manches.

signal closed

var training: bool = false
var team_slots: Array = []         # Array of Array[OptionButton]
var teams_box: HBoxContainer
var arena_opt: OptionButton
var level_spin: SpinBox
var rounds_opt: OptionButton
var format_opt: OptionButton
var ids: Array = []
var names: Array = []
const FORMATS := [["1v1", [1, 1]], ["2v2", [2, 2]], ["3v3", [3, 3]], ["4v4", [4, 4]], ["5v5", [5, 5]], ["3v3v3v3 (4 équipes)", [3, 3, 3, 3]], ["Chaos Thunder (8 combattants, chacun pour soi)", [1, 1, 1, 1, 1, 1, 1, 1]]]
var ARENAS: Array = []

func _ready() -> void:
	ARENAS = Data.arena_choices()
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ids = ["__random"]
	names = ["🎲 Aléatoire"]
	for c in Data.class_list:
		ids.append(c["id"])
		names.append(String(c["name"]) + " (" + String(Data.ROLE_NAME_FR.get(c["role"], "")) + ")")
	for n in Data.champions:
		ids.append(n["id"])
		names.append("★ " + String(n["name"]))
	for n in Data.bosses:
		ids.append(n["id"])
		names.append("☠ " + String(n["name"]))
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1200, 700))
	add_child(p)
	var v := UI.vbox(10)
	p.add_child(v)
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("ENTRAÎNEMENT" if training else "MATCH PERSONNALISÉ", 34, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	var back := UI.btn("Retour", "secondary", Vector2(120, 42))
	back.pressed.connect(func():
		closed.emit()
		queue_free())
	hd.add_child(back)
	v.add_child(hd)
	var opts := UI.hbox(14)
	v.add_child(opts)
	format_opt = OptionButton.new()
	for f in FORMATS:
		format_opt.add_item(f[0])
	format_opt.selected = 4
	format_opt.item_selected.connect(func(_i): _rebuild_teams())
	opts.add_child(UI.lbl("Format", 18, UI.TEXT_DIM, true))
	opts.add_child(format_opt)
	arena_opt = OptionButton.new()
	for a in ARENAS:
		arena_opt.add_item(a[1])
	opts.add_child(UI.lbl("Arène", 18, UI.TEXT_DIM, true))
	opts.add_child(arena_opt)
	level_spin = SpinBox.new()
	level_spin.min_value = 1
	level_spin.max_value = 40
	level_spin.value = 10
	opts.add_child(UI.lbl("Niveau", 18, UI.TEXT_DIM, true))
	opts.add_child(level_spin)
	rounds_opt = OptionButton.new()
	for r in ["1 manche", "2 manches gagnantes", "3 manches gagnantes"]:
		rounds_opt.add_item(r)
	rounds_opt.selected = 0
	opts.add_child(UI.lbl("Manches", 18, UI.TEXT_DIM, true))
	opts.add_child(rounds_opt)
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(sc)
	teams_box = UI.hbox(18)
	teams_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(teams_box)
	_rebuild_teams()
	var go := UI.btn("Combattre !", "primary", Vector2(300, 58))
	go.pressed.connect(_go)
	var hb := UI.hbox(0)
	hb.alignment = BoxContainer.ALIGNMENT_CENTER
	hb.add_child(go)
	v.add_child(hb)

func _rebuild_teams() -> void:
	for c in teams_box.get_children():
		c.queue_free()
	team_slots.clear()
	var fmt: Array = FORMATS[format_opt.selected][1]
	for ti in fmt.size():
		var col := UI.panel("inset")
		var cv := UI.vbox(6)
		col.add_child(cv)
		cv.add_child(UI.lbl("Équipe %d" % (ti + 1), 20, Settings.team_color(ti).lightened(0.3), true))
		var slots: Array = []
		for i in fmt[ti]:
			var ob := OptionButton.new()
			for n in names:
				ob.add_item(String(n))
			ob.selected = 0
			ob.custom_minimum_size = Vector2(250, 36)
			cv.add_child(ob)
			slots.append(ob)
		team_slots.append(slots)
		teams_box.add_child(col)

func _go() -> void:
	var rnd := RandomNumberGenerator.new()
	rnd.randomize()
	var teams: Array = []
	var lvl := int(level_spin.value)
	for ti in team_slots.size():
		var fighters: Array = []
		for ob in team_slots[ti]:
			var id: String = ids[(ob as OptionButton).selected]
			if id == "__random":
				id = Data.class_list[rnd.randi() % Data.class_list.size()]["id"]
			var m := MercLogic.generate(id, lvl, rnd)
			fighters.append(MercLogic.combatant_spec(m, {}))
		teams.append({"name": "Équipe %d" % (ti + 1), "fighters": fighters})
	var ffa: bool = team_slots.size() >= 8
	var cfg := {"teams": teams, "arena": ARENAS[arena_opt.selected][0], "rounds_to_win": rounds_opt.selected + 1, "player_team": 0, "allow_control": true, "mode": "quick",
		"ffa": ffa, "music": "music_battle_1" if randf() < 0.5 else "music_battle_2", "on_finish": func(_r): Game.goto_main_menu()}
	if ffa:
		cfg["time_limit"] = 120.0
		cfg["music"] = "music_chaos_thunder"
	Audio.ui("ui_confirm")
	Game.start_battle(cfg)
