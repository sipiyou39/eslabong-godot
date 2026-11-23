class_name HubScreen
extends Node3D
## Hub de campagne : décor 3D du QG + barre supérieure + onglets (Accueil, Effectif, Marché, Club, Ligue, Modes, Actualités).

var c: Campaign
var backdrop: ClubBackdrop
var ui: CanvasLayer
var root: Control
var topbar: PanelContainer
var content: Control
var tab_btns: Dictionary = {}
var current_tab: String = ""
var tab_node: Control = null
var modal_layer: Control
var gold_label: Label
var week_label: Label
var div_label: Label
var name_label: Label
var logo_view: LogoView
const TABS := [["home", "Accueil", "club"], ["roster", "Effectif", "roster"], ["market", "Marché", "market"], ["club", "Club", "facility_clubhouse"],
	["league", "Ligue & Calendrier", "league"], ["modes", "Modes de jeu", "cup"], ["news", "Actualités", "message"]]

func _ready() -> void:
	c = Game.campaign
	if c == null:
		Game.goto_main_menu()
		return
	Audio.music("music_club")
	backdrop = ClubBackdrop.new()
	add_child(backdrop)
	backdrop.setup("club")
	_refresh_backdrop_mercs()
	backdrop.orbit_radius = 12.5
	backdrop.orbit_height = 4.2
	backdrop.orbit_center = Vector3(0, 1.3, 0)
	backdrop.pan_x = 3.5
	ui = CanvasLayer.new()
	ui.layer = 10
	add_child(ui)
	root = Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.theme = UI.theme()
	ui.add_child(root)
	_build_frame()
	modal_layer = Control.new()
	modal_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	modal_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	modal_layer.theme = UI.theme()
	ui.add_child(modal_layer)
	open_tab("home")
	# rapport de match en attente (retour de combat)
	if not Game.pending_report.is_empty():
		var rep: Dictionary = Game.pending_report
		Game.pending_report = {}
		call_deferred("show_report", rep)

func _refresh_backdrop_mercs() -> void:
	backdrop.show_mercs(c.lineup_mercs())

# ----------------------------------------------------------------------------------------------
func _build_frame() -> void:
	topbar = UI.panel("glass")
	topbar.set_anchors_preset(Control.PRESET_TOP_WIDE)
	topbar.offset_left = 16
	topbar.offset_right = -16
	topbar.offset_top = 12
	topbar.offset_bottom = 84
	root.add_child(topbar)
	var h := UI.hbox(16)
	topbar.add_child(h)
	logo_view = LogoView.new(c.logo, 52)
	h.add_child(logo_view)
	var nv := UI.vbox(0)
	name_label = UI.lbl(c.team_name, 26, UI.GOLD, false, true)
	nv.add_child(name_label)
	div_label = UI.lbl("", 16, UI.TEXT_DIM, true)
	nv.add_child(div_label)
	h.add_child(nv)
	h.add_child(UI.spacer(0, 0, true))
	week_label = UI.lbl("", 22, UI.TEXT, true)
	h.add_child(week_label)
	h.add_child(UI.spacer(30))
	var gold_row := UI.hbox(6)
	gold_row.add_child(UI.tex_rect(UI.stat_icon("gold"), Vector2(30, 30)))
	gold_label = UI.lbl("", 26, UI.GOLD, true)
	gold_row.add_child(gold_label)
	h.add_child(gold_row)
	h.add_child(UI.spacer(14))
	var sv := UI.btn("Sauver", "secondary", Vector2(90, 40))
	sv.pressed.connect(func():
		c.save()
		Game.toast("Partie sauvegardée.", "good"))
	h.add_child(sv)
	var st := UI.btn("Réglages", "secondary", Vector2(100, 40))
	st.pressed.connect(func(): open_modal(SettingsScreen.new()))
	h.add_child(st)
	var mm := UI.btn("Menu", "secondary", Vector2(80, 40))
	mm.pressed.connect(func():
		c.save()
		Game.goto_main_menu())
	h.add_child(mm)
	# navigation
	var nav := UI.panel("glass")
	nav.set_anchors_preset(Control.PRESET_TOP_LEFT)
	nav.offset_left = 16
	nav.offset_top = 100
	root.add_child(nav)
	var nv2 := UI.vbox(6)
	nav.add_child(nv2)
	for t in TABS:
		var b := UI.btn(t[1], "secondary", Vector2(190, 50))
		b.icon = UI.stat_icon(t[2])
		b.expand_icon = true
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.pressed.connect(func(): open_tab(t[0]))
		nv2.add_child(b)
		tab_btns[t[0]] = b
	content = Control.new()
	content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	content.offset_left = 232
	content.offset_top = 100
	content.offset_right = -16
	content.offset_bottom = -16
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(content)
	update_topbar()

func update_topbar() -> void:
	gold_label.text = Game.format_gold(c.gold)
	week_label.text = "Saison %d  •  %s" % [c.season, c.week_title()]
	div_label.text = "%s — %de sur %d  •  %d trophée(s)" % [c.division_name(c.player_div), c.player_position(), c.divisions[c.player_div].size(), c.trophies.size()]

func open_tab(id: String) -> void:
	if tab_node and is_instance_valid(tab_node):
		tab_node.queue_free()
	current_tab = id
	for k in tab_btns:
		var b: Button = tab_btns[k]
		var active: bool = k == id
		b.add_theme_stylebox_override("normal", UI.btn_style("primary" if active else "secondary", "normal"))
		b.add_theme_color_override("font_color", Color("1a1208") if active else UI.TEXT)
	var t: Control = null
	match id:
		"home": t = HubHome.new()
		"roster": t = RosterTab.new()
		"market": t = MarketTab.new()
		"club": t = ClubTab.new()
		"league": t = LeagueTab.new()
		"modes": t = ModesTab.new()
		"news": t = NewsTab.new()
	t.set("hub", self)
	t.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	content.add_child(t)
	tab_node = t
	UI.fade_in(t, 0.25)
	Audio.ui("ui_tab")
	update_topbar()

func refresh() -> void:
	update_topbar()
	_refresh_backdrop_mercs()
	if tab_node and tab_node.has_method("rebuild"):
		tab_node.rebuild()

func open_modal(n: Control) -> Control:
	modal_layer.mouse_filter = Control.MOUSE_FILTER_PASS
	modal_layer.add_child(n)
	if n.has_signal("closed"):
		n.connect("closed", func(): _modal_closed())
	return n

func _modal_closed() -> void:
	await get_tree().process_frame
	if modal_layer.get_child_count() == 0:
		modal_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	refresh()

func open_fighter(uid: String) -> void:
	var fd := FighterDetail.new()
	fd.setup(self, c, uid)
	fd.changed.connect(func():
		update_topbar())
	open_modal(fd)

# ----------------------------------------------------------------------------------------------
# Événements
# ----------------------------------------------------------------------------------------------
func play_event(ev: Dictionary) -> void:
	var kind: String = String(ev["kind"])
	match kind:
		"league", "cup", "special_3v3v3v3", "academy", "academy_placement":
			var mp := MatchPrep.new()
			mp.setup(self, c, ev)
			open_modal(mp)
		"chaos":
			var pick := ChaosPicker.new()
			pick.setup(self, c, ev)
			open_modal(pick)
		"tower":
			launch_tower()
		"draft":
			var d := DraftScreen.new()
			d.setup(self, c, ev)
			open_modal(d)
		_:
			Game.toast("Événement indisponible.", "error")

func build_config(ev: Dictionary) -> Dictionary:
	match String(ev["kind"]):
		"league": return Results.league_config(c, ev)
		"cup": return Results.cup_config(c, ev)
		"special_3v3v3v3": return Results.special_config(c, ev)
		"academy", "academy_placement": return Results.academy_config(c, ev)
	return {}

## Lance un combat (ou simulation) et enregistre le résultat
func run_event(ev: Dictionary, cfg: Dictionary, simulate: bool, auto_control: bool = true) -> void:
	var campaign := c
	if simulate:
		var res := Results.quick_sim_event(campaign, cfg)
		var rep := Results.finish_event(campaign, ev, res, cfg)
		campaign.save()
		show_report(rep)
		return
	cfg["auto_control"] = auto_control
	cfg["allow_control"] = true
	cfg["on_finish"] = func(res: Dictionary):
		var rep2 := Results.finish_event(campaign, ev, res, cfg)
		campaign.save()
		Game.pending_report = rep2
		Game.goto_hub()
	c.save()
	Game.start_battle(cfg)

func show_report(rep: Dictionary) -> void:
	var ps := PostMatchScreen.new()
	ps.setup(self, c, rep)
	open_modal(ps)
	update_topbar()

func launch_tower() -> void:
	var floor_n := c.tower_floor + 1
	var cfg := Results.tower_config(c, floor_n)
	var ev := {"id": "tower", "kind": "tower", "label": "Tour du Défi — étage %d" % floor_n, "main": false}
	run_event(ev, cfg, false)

func launch_irongate(floor_n: int) -> void:
	var cfg := Results.irongate_config(c, floor_n)
	var ev := {"id": "irongate", "kind": "irongate", "label": "Defend the Iron Gate — étage %d" % floor_n, "main": false}
	run_event(ev, cfg, false)

func next_week() -> void:
	if not c.main_event_done():
		Game.toast("Joue ou simule d'abord l'événement principal de la semaine.", "error")
		return
	var msgs := Results.advance_week(c)
	Audio.ui("ui_page")
	for mg in msgs:
		Game.toast(String(mg), "info", 4.0)
	refresh()
	open_tab(current_tab)
