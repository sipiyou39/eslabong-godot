class_name BattleHUD
extends CanvasLayer
## Interface de combat : barres d'unités, équipes, barre de compétences, bannières, fil d'éliminations, pause, résultats.

var battle: Battle
var root: Control
var unit_ui: Dictionary = {}          # Fighter -> {root, hp, mana, sta, name, status}
var team_rows: Dictionary = {}        # Fighter -> {bar, label, root}
var banner: Label
var banner_sub: Label
var count_label: Label
var timer_label: Label
var score_label: Label
var feed_box: VBoxContainer
var event_box: VBoxContainer
var ability_bar: HBoxContainer
var slot_nodes: Array = []
var self_bars: Dictionary = {}
var self_panel: Control
var speed_label: Label
var hint_label: Label
var pause_panel: Control
var result_panel: Control
var _banner_tw: Tween
var _hint_t: float = 9.0
var _ctrl: Fighter = null
var _team_panels: Array[VBoxContainer] = []

const SLOT_KEYS := ["LMB", "ESPACE", "RMB", "Q", "E", "R"]

func _ready() -> void:
	layer = 20
	process_mode = Node.PROCESS_MODE_ALWAYS
	root = Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.theme = UI.theme()
	add_child(root)
	_build_scoreboard()
	_build_team_panels()
	_build_feed()
	_build_banner()
	_build_ability_bar()
	for f in battle.fighters:
		_make_unit_ui(f)
	_build_speed_hint()

func _unhandled_input(ev: InputEvent) -> void:
	# la scène de combat est en pause : seul le HUD (process ALWAYS) peut reprendre
	if pause_panel and is_instance_valid(pause_panel) and ev.is_action_pressed("pause"):
		toggle_pause()
		get_viewport().set_input_as_handled()

func on_control_changed(f: Fighter) -> void:
	_ctrl = f
	_rebuild_slots()

# ----------------------------------------------------------------------------------------------
func _build_scoreboard() -> void:
	var box := UI.panel("glass")
	box.set_anchors_preset(Control.PRESET_CENTER_TOP)
	box.position = Vector2(-170, 10)
	box.custom_minimum_size = Vector2(340, 0)
	box.grow_horizontal = Control.GROW_DIRECTION_BOTH
	root.add_child(box)
	var v := UI.vbox(0)
	box.add_child(v)
	score_label = UI.lbl("", 26, UI.GOLD, false, true)
	score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(score_label)
	timer_label = UI.lbl("0:00", 20, UI.TEXT_DIM, true)
	timer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(timer_label)

func _build_team_panels() -> void:
	var n := battle.team_count
	for ti in n:
		var p := UI.vbox(3)
		p.mouse_filter = Control.MOUSE_FILTER_IGNORE
		root.add_child(p)
		_team_panels.append(p)
		var cols := 2 if n <= 2 else 2
		if ti == 0:
			p.set_anchors_preset(Control.PRESET_TOP_LEFT)
			p.offset_left = 14
			p.offset_top = 14
		elif ti == 1:
			p.set_anchors_preset(Control.PRESET_TOP_RIGHT)
			p.offset_left = -254
			p.offset_right = -14
			p.offset_top = 14
		elif ti == 2:
			p.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
			p.offset_left = 14
			p.offset_top = -240
		else:
			p.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
			p.offset_left = -254
			p.offset_right = -14
			p.offset_top = -240
		p.custom_minimum_size = Vector2(240, 0)
		var title := UI.lbl(String(battle.teams[ti].get("name", "Équipe")), 18, Settings.team_color(ti).lightened(0.3), true)
		title.add_theme_font_override("font", Game.font_title())
		UI.shadowed(title)
		if not battle.ffa:
			p.add_child(title)
		for f in battle.fighters:
			if f.team == ti and not f.is_summon:
				_make_team_row(f, p)

func _make_team_row(f: Fighter, parent: Control) -> void:
	var row := UI.hbox(6)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var icon := UI.tex_rect(UI.class_icon(String(f.tpl.get("id", ""))), Vector2(34, 34))
	row.add_child(icon)
	var v := UI.vbox(1)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var nm := UI.lbl(f.display_name, 15, UI.TEXT, true)
	nm.clip_text = true
	nm.custom_minimum_size = Vector2(180, 0)
	v.add_child(nm)
	var bar := UIBar.new(Settings.team_color(f.team), 9)
	bar.custom_minimum_size = Vector2(170, 9)
	v.add_child(bar)
	row.add_child(v)
	parent.add_child(row)
	team_rows[f] = {"bar": bar, "label": nm, "root": row, "icon": icon}

func _make_unit_ui(f: Fighter) -> void:
	if unit_ui.has(f):
		return
	var r := Control.new()
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(r)
	var nm := UI.lbl(f.display_name, 14, UI.TEXT, true)
	nm.position = Vector2(-60, -20)
	nm.custom_minimum_size = Vector2(120, 0)
	nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UI.shadowed(nm)
	r.add_child(nm)
	var w := 74.0 if not f.is_summon else 44.0
	var hp := UIBar.new(Settings.team_color(f.team), 8)
	hp.size = Vector2(w, 8)
	hp.position = Vector2(-w * 0.5, 0)
	r.add_child(hp)
	var mana := UIBar.new(Color("4a90ff"), 3)
	mana.size = Vector2(w, 3)
	mana.position = Vector2(-w * 0.5, 9)
	mana.radius = 1.0
	var sta := UIBar.new(Color("6ad07a"), 3)
	sta.size = Vector2(w, 3)
	sta.position = Vector2(-w * 0.5, 13)
	sta.radius = 1.0
	if not f.is_summon:
		r.add_child(mana)
		r.add_child(sta)
	var st := HBoxContainer.new()
	st.position = Vector2(-w * 0.5, 17)
	st.add_theme_constant_override("separation", 2)
	st.mouse_filter = Control.MOUSE_FILTER_IGNORE
	r.add_child(st)
	var cast := UIBar.new(Color("ffd060"), 3)
	cast.size = Vector2(w, 3)
	cast.position = Vector2(-w * 0.5, -3)
	cast.radius = 1.0
	cast.visible = false
	r.add_child(cast)
	unit_ui[f] = {"root": r, "hp": hp, "mana": mana, "sta": sta, "name": nm, "status": st, "cast": cast, "status_cache": ""}

func _build_feed() -> void:
	feed_box = UI.vbox(3)
	feed_box.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	feed_box.position = Vector2(-330, 250 if battle.team_count <= 2 else 14)
	feed_box.custom_minimum_size = Vector2(316, 0)
	feed_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(feed_box)
	event_box = UI.vbox(3)
	event_box.set_anchors_preset(Control.PRESET_CENTER_TOP)
	event_box.position = Vector2(-200, 90)
	event_box.custom_minimum_size = Vector2(400, 0)
	event_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(event_box)

func _build_banner() -> void:
	banner = UI.lbl("", 72, UI.GOLD, false, true)
	UI.center(banner, Vector2(1000, 0))
	banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	banner.grow_horizontal = Control.GROW_DIRECTION_BOTH
	banner.modulate.a = 0.0
	UI.shadowed(banner, Color(0, 0, 0, 0.9), 12)
	root.add_child(banner)
	banner_sub = UI.lbl("", 28, UI.TEXT, true)
	UI.center(banner_sub, Vector2(1000, 0))
	banner_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	banner_sub.modulate.a = 0.0
	UI.shadowed(banner_sub, Color(0, 0, 0, 0.9), 8)
	root.add_child(banner_sub)
	count_label = UI.lbl("", 190, Color.WHITE, false, true)
	UI.center(count_label, Vector2(600, 0))
	count_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	count_label.modulate.a = 0.0
	UI.shadowed(count_label, Color(0, 0, 0, 0.9), 16)
	root.add_child(count_label)

func _build_speed_hint() -> void:
	speed_label = UI.lbl("", 22, UI.GOLD, true)
	speed_label.set_anchors_preset(Control.PRESET_TOP_LEFT)
	speed_label.position = Vector2(14, 300)
	root.add_child(speed_label)
	hint_label = UI.lbl("ZQSD / WASD : bouger   •   Clic gauche : attaque   •   Clic droit, A/Q, E, R : compétences   •   ESPACE : dash   •   TAB : changer de combattant   •   T : vitesse   •   ÉCHAP : pause", 16, UI.TEXT_DIM, false)
	hint_label.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	hint_label.position = Vector2(-560, -30)
	hint_label.custom_minimum_size = Vector2(1120, 0)
	hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UI.shadowed(hint_label)
	root.add_child(hint_label)

func _build_ability_bar() -> void:
	self_panel = UI.panel("glass")
	self_panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	self_panel.position = Vector2(-300, -140)
	self_panel.custom_minimum_size = Vector2(600, 0)
	self_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	self_panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	root.add_child(self_panel)
	var v := UI.vbox(6)
	self_panel.add_child(v)
	ability_bar = UI.hbox(8)
	ability_bar.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_child(ability_bar)
	var hp := UIBar.new(Color("e8505a"), 18)
	hp.show_text = true
	var mana := UIBar.new(Color("4a90ff"), 12)
	mana.show_text = true
	var sta := UIBar.new(Color("6ad07a"), 12)
	sta.show_text = true
	v.add_child(hp)
	var h2 := UI.hbox(6)
	mana.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sta.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h2.add_child(mana)
	h2.add_child(sta)
	v.add_child(h2)
	self_bars = {"hp": hp, "mana": mana, "sta": sta}
	self_panel.visible = false

func _rebuild_slots() -> void:
	for c in ability_bar.get_children():
		c.queue_free()
	slot_nodes.clear()
	if _ctrl == null:
		self_panel.visible = false
		return
	self_panel.visible = true
	for i in mini(_ctrl.kit.size(), 6):
		var ab := _ctrl.kit[i]
		var holder := Control.new()
		holder.custom_minimum_size = Vector2(70, 70) if i != 1 else Vector2(56, 56)
		var bg := Panel.new()
		bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		bg.add_theme_stylebox_override("panel", UI.style_flat(Color(0.05, 0.04, 0.09, 0.9), Data.elem_color(String(ab.get("element", "physical"))).darkened(0.1), 8, 2, 0, 0))
		holder.add_child(bg)
		var ic := UI.tex_rect(UI.ability_icon(ab), holder.custom_minimum_size - Vector2(8, 8))
		ic.position = Vector2(4, 4)
		holder.add_child(ic)
		var cd := ColorRect.new()
		cd.color = Color(0, 0, 0, 0.62)
		cd.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		cd.mouse_filter = Control.MOUSE_FILTER_IGNORE
		cd.visible = false
		holder.add_child(cd)
		var cdl := UI.lbl("", 22, Color.WHITE, true)
		cdl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		cdl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		cdl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		UI.shadowed(cdl)
		holder.add_child(cdl)
		var key := UI.lbl(SLOT_KEYS[i], 12, UI.GOLD, true)
		key.position = Vector2(4, holder.custom_minimum_size.y - 18)
		UI.shadowed(key)
		holder.add_child(key)
		holder.tooltip_text = "%s\n%s" % [String(ab.get("name", "")), _ability_desc(ab)]
		holder.mouse_filter = Control.MOUSE_FILTER_PASS
		ability_bar.add_child(holder)
		slot_nodes.append({"cd": cd, "cdl": cdl, "bg": bg, "holder": holder})

static func _ability_desc(ab: Dictionary) -> String:
	var parts: Array[String] = []
	parts.append("%s • %s" % [String(ab.get("arch", "")).replace("_", " "), Data.ELEM_NAME_FR.get(String(ab.get("element", "physical")), "")])
	if float(ab.get("mana", 0)) > 0:
		parts.append("Mana %d" % int(ab["mana"]))
	if float(ab.get("sta", 0)) > 0:
		parts.append("Endurance %d" % int(ab["sta"]))
	parts.append("Recharge %.1fs" % float(ab.get("cd", 0)))
	return "\n".join(parts)

# ----------------------------------------------------------------------------------------------
func _process(dt: float) -> void:
	if battle == null or battle.camera == null:
		return
	var cam := battle.camera
	var real_dt := dt / maxf(Engine.time_scale, 0.01)
	_hint_t -= real_dt
	hint_label.visible = _hint_t > 0.0 and battle.state != Battle.State.MATCH_END
	hint_label.modulate.a = clampf(_hint_t / 2.0, 0.0, 1.0)
	# spectateur : invite
	if battle.controlled_fighter() == null and battle.allow_control and battle.state == Battle.State.FIGHTING:
		hint_label.text = "Spectateur — clique sur un de tes combattants pour en prendre le contrôle"
		hint_label.visible = true
		hint_label.modulate.a = 1.0
	# scoreboard
	var parts: Array[String] = []
	for i in battle.team_count:
		parts.append(str(battle.wins[i]))
	score_label.text = " : ".join(parts) if not battle.ffa else "MANCHE %d" % battle.round_no
	var t := int(battle.round_time)
	timer_label.text = "%d:%02d" % [t / 60, t % 60]
	if battle.state == Battle.State.FIGHTING and battle.round_time >= battle.storm_start:
		timer_label.add_theme_color_override("font_color", Color("ff6a6a"))
	else:
		timer_label.add_theme_color_override("font_color", UI.TEXT_DIM)
	# unités
	for f in unit_ui.keys():
		if not is_instance_valid(f):
			unit_ui.erase(f)
			continue
		var u: Dictionary = unit_ui[f]
		var r: Control = u["root"]
		if not f.alive or not Settings.gb("show_hp_bars"):
			r.visible = false
			continue
		var wp: Vector3 = f.global_position + Vector3(0, f.model.height() + 0.45, 0)
		if cam.is_position_behind(wp):
			r.visible = false
			continue
		r.visible = true
		r.position = cam.unproject_position(wp)
		(u["hp"] as UIBar).set_values(f.hp, f.max_hp)
		(u["hp"] as UIBar).shield = f.shield_hp
		(u["mana"] as UIBar).set_values(f.mana, f.max_mana)
		(u["sta"] as UIBar).set_values(f.sta, f.max_sta)
		var cb: UIBar = u["cast"]
		if not f.cast.is_empty() and float(f.cast["dur"]) > 0.35 and not bool(f.cast["fired"]):
			cb.visible = true
			cb.set_values(float(f.cast["t"]), float(f.cast["dur"]))
		else:
			cb.visible = false
		(u["name"] as Label).visible = (f == _ctrl) or Settings.gi("show_unit_names") == 0
		# icônes de statut
		var sig := ",".join(f.statuses.keys())
		if sig != u["status_cache"]:
			u["status_cache"] = sig
			var sb: HBoxContainer = u["status"]
			for c in sb.get_children():
				c.queue_free()
			for s in f.statuses.keys():
				sb.add_child(UI.tex_rect(UI.status_icon(s), Vector2(14, 14)))
		r.scale = Vector2.ONE * (1.25 if f == _ctrl else 1.0)
	for f in team_rows.keys():
		if not is_instance_valid(f):
			continue
		var tr: Dictionary = team_rows[f]
		(tr["bar"] as UIBar).set_values(f.hp, f.max_hp)
		(tr["root"] as Control).modulate = Color.WHITE if f.alive else Color(0.45, 0.45, 0.5, 0.7)
		var lab: Label = tr["label"]
		lab.add_theme_color_override("font_color", UI.GOLD if f == _ctrl else UI.TEXT)
	# barre de compétences
	if _ctrl and is_instance_valid(_ctrl):
		(self_bars["hp"] as UIBar).set_values(_ctrl.hp, _ctrl.max_hp)
		(self_bars["hp"] as UIBar).shield = _ctrl.shield_hp
		(self_bars["mana"] as UIBar).set_values(_ctrl.mana, _ctrl.max_mana)
		(self_bars["sta"] as UIBar).set_values(_ctrl.sta, _ctrl.max_sta)
		self_panel.visible = _ctrl.alive
		for i in slot_nodes.size():
			var sn: Dictionary = slot_nodes[i]
			var cdv := _ctrl.cds[i] if i < _ctrl.cds.size() else 0.0
			var can := _ctrl.can_pay(i)
			sn["cd"].visible = cdv > 0.0 or not can
			sn["cdl"].text = ("%.1f" % cdv) if cdv > 0.0 else ("" if can else "!")
			(sn["holder"] as Control).modulate = Color.WHITE if (cdv <= 0.0 and can) else Color(0.8, 0.8, 0.85)
	if _ctrl and not _ctrl.alive and battle.controlled_fighter() == null:
		self_panel.visible = false

# ----------------------------------------------------------------------------------------------
# Bannières / événements
# ----------------------------------------------------------------------------------------------
func show_banner(t: String, sub: String, dur: float = 2.0) -> void:
	banner.text = t
	banner_sub.text = sub
	if _banner_tw:
		_banner_tw.kill()
	banner.modulate.a = 0.0
	banner_sub.modulate.a = 0.0
	banner.pivot_offset = Vector2(500, 50)
	banner.scale = Vector2(1.4, 1.4)
	_banner_tw = create_tween().set_parallel(true)
	_banner_tw.tween_property(banner, "modulate:a", 1.0, 0.2)
	_banner_tw.tween_property(banner, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	_banner_tw.tween_property(banner_sub, "modulate:a", 1.0, 0.3).set_delay(0.2)
	_banner_tw.chain().tween_interval(maxf(dur - 0.6, 0.1))
	_banner_tw.chain().set_parallel(true)
	_banner_tw.tween_property(banner, "modulate:a", 0.0, 0.4)
	_banner_tw.tween_property(banner_sub, "modulate:a", 0.0, 0.4)

func show_count(n: int) -> void:
	count_label.text = str(n)
	count_label.pivot_offset = Vector2(300, 100)
	count_label.scale = Vector2(1.8, 1.8)
	count_label.modulate.a = 1.0
	var tw := create_tween().set_parallel(true)
	tw.tween_property(count_label, "scale", Vector2.ONE, 0.4).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(count_label, "modulate:a", 0.0, 0.5).set_delay(0.5)

func show_speed(mode: int) -> void:
	speed_label.text = ["", "▶▶  x2", "▶▶▶  x3"][mode]

func add_event(t: String, c: Color) -> void:
	var l := UI.lbl(t, 20, c, true)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UI.shadowed(l)
	event_box.add_child(l)
	var tw := l.create_tween()
	tw.tween_interval(2.8)
	tw.tween_property(l, "modulate:a", 0.0, 0.5)
	tw.tween_callback(l.queue_free)

func add_kill_feed(killer: Fighter, victim: Fighter) -> void:
	var mode := Settings.gi("kill_feed_display_mode")
	if mode == 0:
		return
	var row := UI.panel("glass")
	var h := UI.hbox(8)
	row.add_child(h)
	var kn := killer.display_name if killer else "Tempête"
	var kc := Settings.team_color(killer.team) if killer else Color("c8a0ff")
	h.add_child(UI.lbl(kn, 16, kc.lightened(0.25), true))
	h.add_child(UI.lbl("✕", 16, UI.TEXT_DIM, true))
	h.add_child(UI.lbl(victim.display_name, 16, Settings.team_color(victim.team).lightened(0.25), true))
	feed_box.add_child(row)
	while feed_box.get_child_count() > 6:
		feed_box.get_child(0).queue_free()
		break
	var tw := row.create_tween()
	tw.tween_interval(5.0)
	tw.tween_property(row, "modulate:a", 0.0, 0.5)
	tw.tween_callback(row.queue_free)

# ----------------------------------------------------------------------------------------------
# Pause
# ----------------------------------------------------------------------------------------------
func toggle_pause() -> void:
	if pause_panel and is_instance_valid(pause_panel):
		pause_panel.queue_free()
		pause_panel = null
		get_tree().paused = false
		return
	get_tree().paused = true
	pause_panel = Control.new()
	pause_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	pause_panel.process_mode = Node.PROCESS_MODE_ALWAYS
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.6)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	pause_panel.add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(380, 0))
	pause_panel.add_child(p)
	var v := UI.vbox(12)
	p.add_child(v)
	var t := UI.lbl("PAUSE", 40, UI.GOLD, false, true)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(t)
	var b1 := UI.btn("Reprendre", "primary", Vector2(0, 50))
	b1.pressed.connect(toggle_pause)
	v.add_child(b1)
	var b2 := UI.btn("Vitesse : %s" % ["x1", "x2", "x3"][battle.speed_mode], "secondary", Vector2(0, 46))
	b2.pressed.connect(func():
		battle.cycle_speed()
		b2.text = "Vitesse : %s" % ["x1", "x2", "x3"][battle.speed_mode])
	v.add_child(b2)
	var b3 := UI.btn("Abandonner le match", "danger", Vector2(0, 46))
	b3.pressed.connect(func():
		get_tree().paused = false
		battle.result = {"winner": 1 - int(battle.config.get("player_team", 0)), "forfeit": true, "wins": battle.wins.duplicate(), "teams": [], "mode": battle.config.get("mode", "quick")}
		battle.finish_and_exit())
	v.add_child(b3)
	root.add_child(pause_panel)

# ----------------------------------------------------------------------------------------------
# Résultats
# ----------------------------------------------------------------------------------------------
func show_result(res: Dictionary) -> void:
	if result_panel:
		return
	var player_team := int(battle.config.get("player_team", 0))
	var won: bool = res["winner"] == player_team
	result_panel = Control.new()
	result_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.72)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	result_panel.add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1040, 0))
	result_panel.add_child(p)
	var v := UI.vbox(10)
	p.add_child(v)
	var title := UI.lbl("VICTOIRE" if won else "DÉFAITE", 64, UI.GOLD if won else Color("e8505a"), false, true)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UI.shadowed(title, Color(0, 0, 0, 0.8), 10)
	v.add_child(title)
	var sc := " - ".join((res["wins"] as Array).map(func(x): return str(x)))
	var sub := UI.lbl("Manches : " + sc, 22, UI.TEXT_DIM, true)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(sub)
	var cols := UI.hbox(20)
	v.add_child(cols)
	var mvp: Dictionary = {}
	var best := -1.0
	for t in res["teams"]:
		for fi in t["fighters"]:
			var s: Dictionary = fi["stats"]
			var score: float = float(s["damage"]) * 0.01 + float(s["kills"]) * 3 + float(s["assists"]) + float(s["healing"]) * 0.012 + float(s["res"]) * 4
			if score > best:
				best = score
				mvp = fi
	res["mvp"] = mvp
	for ti in res["teams"].size():
		var t: Dictionary = res["teams"][ti]
		var col := UI.vbox(4)
		col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var hdr := UI.lbl(String(t["name"]), 24, Settings.team_color(ti).lightened(0.3), false, true)
		col.add_child(hdr)
		var head := UI.hbox(0)
		for h in [["Nom", 190], ["K", 34], ["A", 34], ["D", 34], ["Dégâts", 80], ["Soins", 70]]:
			var hl := UI.lbl(h[0], 15, UI.TEXT_DIM, true)
			hl.custom_minimum_size = Vector2(h[1], 0)
			head.add_child(hl)
		col.add_child(head)
		for fi in t["fighters"]:
			var s2: Dictionary = fi["stats"]
			var row := UI.hbox(0)
			var is_mvp: bool = fi == mvp
			var nm := UI.lbl(("★ " if is_mvp else "") + String(fi["name"]), 17, UI.GOLD if is_mvp else UI.TEXT, true)
			nm.custom_minimum_size = Vector2(190, 0)
			row.add_child(nm)
			for val in [[str(s2["kills"]), 34], [str(s2["assists"]), 34], [str(s2["deaths"]), 34], [str(int(s2["damage"])), 80], [str(int(s2["healing"])), 70]]:
				var l := UI.lbl(val[0], 17, UI.TEXT)
				l.custom_minimum_size = Vector2(val[1], 0)
				row.add_child(l)
			col.add_child(row)
		cols.add_child(col)
	var b := UI.btn("Continuer", "primary", Vector2(260, 54))
	b.pressed.connect(func(): battle.finish_and_exit())
	var hb := UI.hbox(0)
	hb.alignment = BoxContainer.ALIGNMENT_CENTER
	hb.add_child(b)
	v.add_child(hb)
	root.add_child(result_panel)
	UI.pop_in(p)
