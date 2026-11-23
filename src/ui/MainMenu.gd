class_name MainMenu
extends Node3D
## Menu principal : quartier général en 3D, titre, boutons.

var backdrop: ClubBackdrop
var ui: CanvasLayer
var root: Control
var menu_box: VBoxContainer
var overlay: Control = null

func _ready() -> void:
	Audio.music("music_menu")
	backdrop = ClubBackdrop.new()
	add_child(backdrop)
	backdrop.setup("club")
	var rnd := RandomNumberGenerator.new()
	rnd.randomize()
	var mercs: Array = []
	var picks := ["Merc_Paladin_Templar", "Merc_Mage_Fire", "Merc_Rogue_Assasin", "Merc_Orc_Berserker", "Merc_Healer_Priest"]
	picks.shuffle()
	for id in picks:
		mercs.append(MercLogic.generate(String(id), 8, rnd, {"shiny": rnd.randf() < 0.2}))
	backdrop.show_mercs(mercs)
	backdrop.orbit_radius = 11.0
	backdrop.orbit_height = 3.6
	backdrop.orbit_center = Vector3(-2.0, 1.4, 0)
	ui = CanvasLayer.new()
	ui.layer = 10
	add_child(ui)
	root = Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.theme = UI.theme()
	ui.add_child(root)
	_build()

func _build() -> void:
	var shade := ColorRect.new()
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.color = Color(0, 0, 0, 0)
	root.add_child(shade)
	# bandeau gauche dégradé
	var grad := Gradient.new()
	grad.offsets = PackedFloat32Array([0.0, 0.6, 1.0])
	grad.colors = PackedColorArray([Color(0.04, 0.03, 0.08, 0.92), Color(0.04, 0.03, 0.08, 0.55), Color(0.04, 0.03, 0.08, 0.0)])
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.fill_from = Vector2(0, 0)
	gt.fill_to = Vector2(1, 0)
	var band := TextureRect.new()
	band.texture = gt
	band.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	band.stretch_mode = TextureRect.STRETCH_SCALE
	band.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	band.size_flags_horizontal = Control.SIZE_FILL
	band.anchor_right = 0.55
	band.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(band)
	var col := UI.vbox(10)
	col.position = Vector2(90, 70)
	col.custom_minimum_size = Vector2(440, 0)
	root.add_child(col)
	var logo := UI.skin_tex("logo_emblem")
	if logo:
		var tr := UI.tex_rect(logo, Vector2(150, 150))
		col.add_child(tr)
	var title := UI.lbl("ESLABONG", 84, UI.GOLD, false, true)
	UI.shadowed(title, Color(0, 0, 0, 0.9), 14)
	col.add_child(title)
	var sub := UI.lbl("CLUB DE MERCENAIRES • ARÈNE TACTIQUE", 20, UI.TEXT_DIM, true)
	col.add_child(sub)
	col.add_child(UI.spacer(26))
	menu_box = UI.vbox(10)
	col.add_child(menu_box)
	var has_save := FileAccess.file_exists(Campaign.save_path)
	if has_save:
		var s := Campaign.summary_of()
		var cont := UI.btn("Continuer  —  %s  (S%d, sem. %d)" % [s.get("team_name", "?"), int(s.get("season", 1)), int(s.get("week", 1))], "primary", Vector2(440, 56))
		cont.pressed.connect(_continue)
		menu_box.add_child(cont)
	var items: Array = [
		["Nouvelle campagne", _new_campaign], ["Match rapide / personnalisé", _custom_match], ["Entraînement", _training],
		["Hall des légendes", _hall], ["Succès", _achievements], ["Réglages", _settings], ["Quitter", func(): get_tree().quit()],
	]
	for it in items:
		var b := UI.btn(it[0], "secondary", Vector2(440, 50))
		b.pressed.connect(it[1])
		menu_box.add_child(b)
	var ver := UI.lbl("v0.1 — reproduction Godot 4.7 • Build de référence 26856521", 14, UI.TEXT_DIM)
	ver.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	ver.position = Vector2(20, -34)
	root.add_child(ver)
	UI.fade_in(col, 0.9, 0.2)

func _set_overlay(o: Control) -> void:
	if overlay and is_instance_valid(overlay):
		overlay.queue_free()
	overlay = o
	root.add_child(o)

func _continue() -> void:
	var c := Campaign.load_from()
	if c == null:
		Game.toast("Sauvegarde illisible.", "error")
		return
	Game.campaign = c
	Audio.ui("ui_confirm")
	Game.goto_hub()

func _new_campaign() -> void:
	var s := NewCampaignScreen.new()
	_set_overlay(s)

func _custom_match() -> void:
	var s := CustomMatchScreen.new()
	_set_overlay(s)

func _training() -> void:
	var s := CustomMatchScreen.new()
	s.training = true
	_set_overlay(s)

func _hall() -> void:
	var s := HallScreen.new()
	_set_overlay(s)

func _achievements() -> void:
	var s := AchievementsScreen.new()
	_set_overlay(s)

func _settings() -> void:
	var s := SettingsScreen.new()
	_set_overlay(s)
