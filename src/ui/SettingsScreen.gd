class_name SettingsScreen
extends Control
## Réglages : Jeu, Contrôles, Vidéo, Audio, Accessibilité, Interface. Modifie Settings et sauvegarde.

signal closed

# [clé, libellé, type, params...]
const ROWS := {
	"Jeu": [
		["friendly_fire_multiplier", "Tir allié (multiplicateur)", "slider", 0.0, 1.0, 0.05],
		["injuries_enabled", "Blessures activées", "bool"], ["fighter_form_enabled", "Forme des combattants", "bool"],
		["battle_speed_mode", "Vitesse de combat par défaut", "opt", ["Normale ×1", "Rapide ×2", "Très rapide ×3"]],
		["damage_numbers_player_mode", "Nombres de dégâts (joueur)", "opt", ["Aucun", "Tous", "Mes dégâts"]],
		["show_hp_bars", "Barres de vie des unités", "bool"], ["show_unit_names", "Noms des unités", "opt", ["Toujours", "Contrôlé seulement"]],
		["show_ability_cooldowns", "Afficher les recharges", "bool"], ["show_cast_icons", "Icônes de lancer", "bool"],
		["kill_feed_display_mode", "Fil d'éliminations", "opt", ["Masqué", "Joueur", "Les deux"]],
		["status_effect_text_enabled", "Texte des altérations d'état", "bool"], ["hold_to_attack_enabled", "Maintenir pour attaquer", "bool"],
		["draft_fast_picks", "Choix rapides en Draft", "bool"], ["protect_favorite_relics", "Protéger les reliques favorites", "bool"],
		["confirm_relic_replacement", "Confirmer le remplacement de relique", "bool"], ["double_click_relic_equip", "Double-clic pour équiper", "bool"],
		["relic_compatibility_highlights", "Surbrillance de compatibilité", "bool"],
	],
	"Contrôles": [
		["controller_aim_speed", "Vitesse de visée manette", "slider", 200.0, 1200.0, 25.0], ["controller_aim_deadzone", "Zone morte visée", "slider", 0.0, 0.4, 0.01],
		["controller_move_deadzone", "Zone morte déplacement", "slider", 0.0, 0.4, 0.01], ["controller_aim_assist_strength", "Assistance à la visée", "slider", 0.0, 1.0, 0.05],
		["aim_lookahead_close", "Anticipation caméra (proche)", "slider", 0.0, 0.6, 0.01], ["aim_lookahead_far", "Anticipation caméra (loin)", "slider", 0.0, 0.6, 0.01],
		["player_3_remote_enabled", "Joueur 3 (Remote Play)", "bool"], ["player_4_remote_enabled", "Joueur 4 (Remote Play)", "bool"],
	],
	"Vidéo": [
		["window_mode", "Mode d'affichage", "opt", ["Fenêtré", "Maximisé", "Plein écran", "Plein écran exclusif"]], ["vsync_mode", "VSync", "opt", ["Désactivée", "Activée"]],
		["fps_cap", "Limite de FPS (0 = illimité)", "slider", 0.0, 240.0, 10.0], ["msaa", "Anticrénelage MSAA", "opt", ["Désactivé", "2x", "4x", "8x"]],
		["postfx_enabled", "Post-traitement (bloom, vignette…)", "bool"], ["ssao", "Occlusion ambiante SSAO", "bool"], ["volumetric_fog", "Brouillard volumétrique", "bool"],
		["dof", "Profondeur de champ", "bool"], ["shadows_quality", "Ombres", "opt", ["Désactivées", "Moyennes", "Élevées"]], ["impact_flash_enabled", "Flashs d'impact", "bool"],
		["unit_outlines_enabled", "Contours des unités", "bool"], ["reduce_screen_shake", "Réduire les tremblements d'écran", "bool"], ["ui_scale", "Échelle de l'interface", "slider", 0.75, 1.5, 0.05],
	],
	"Audio": [
		["master_volume", "Volume général", "slider", 0.0, 1.0, 0.05], ["music_volume", "Musique", "slider", 0.0, 1.0, 0.05], ["combat_music_volume", "Musique de combat", "slider", 0.0, 1.0, 0.05],
		["combat_volume", "Effets de combat", "slider", 0.0, 1.0, 0.05], ["ui_volume", "Interface", "slider", 0.0, 1.0, 0.05], ["chest_opening_music_enabled", "Musique d'ouverture de coffre", "bool"],
		["mute_when_unfocused", "Couper le son hors focus", "bool"],
	],
	"Accessibilité": [
		["colorblind_mode", "Mode daltonien", "bool"], ["classic_stat_colors", "Couleurs de stats classiques", "bool"], ["readable_font_mode", "Police lisible", "bool"],
		["text_scale", "Taille du texte", "slider", 0.8, 1.5, 0.05], ["cursor_size_mode", "Taille du curseur", "opt", ["Petit", "Normal", "Grand"]], ["tooltip_details_expanded", "Infobulles détaillées", "bool"],
	],
	"Interface": [
		["language_code", "Langue", "opt_str", ["fr", "en"]], ["keep_class_names_in_english", "Noms de classes en anglais", "bool"], ["keep_champion_names_in_english", "Noms de champions en anglais", "bool"],
		["next_campaign_difficulty", "Difficulté de la prochaine campagne", "opt", ["Facile", "Normal", "Difficile", "Cauchemar"]],
	],
}
const ACTION_LABELS := {"move_up": "Haut", "move_down": "Bas", "move_left": "Gauche", "move_right": "Droite", "dash": "Dash", "ability_1": "Compétence 1", "ability_2": "Compétence 2",
	"ability_3": "Compétence 3", "ability_4": "Compétence 4", "switch_fighter": "Changer de combattant", "pause": "Pause", "speed_cycle": "Vitesse", "tactic_1": "Tactique 1", "tactic_2": "Tactique 2", "tactic_3": "Tactique 3", "tactic_4": "Tactique 4"}

var tabs: TabContainer
var _listening: String = ""
var _listen_btn: Button

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.7)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(900, 640))
	add_child(p)
	var v := UI.vbox(10)
	p.add_child(v)
	var hd := UI.hbox(8)
	hd.add_child(UI.lbl("RÉGLAGES", 34, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	var close := UI.btn("Fermer", "secondary", Vector2(120, 42))
	close.pressed.connect(_close)
	hd.add_child(close)
	v.add_child(hd)
	tabs = TabContainer.new()
	tabs.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(tabs)
	for tab_name in ROWS:
		tabs.add_child(_make_tab(tab_name))
	tabs.add_child(_make_keys_tab())
	tabs.set_tab_title(tabs.get_tab_count() - 1, "Touches")
	UI.pop_in(p)

func _close() -> void:
	Settings.save()
	closed.emit()
	queue_free()

func _make_tab(tab_name: String) -> Control:
	var sc := ScrollContainer.new()
	sc.name = tab_name
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := UI.vbox(6)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v)
	for row in ROWS[tab_name]:
		v.add_child(_make_row(row))
	return sc

func _make_row(row: Array) -> Control:
	var key: String = row[0]
	var h := UI.hbox(10)
	h.custom_minimum_size = Vector2(0, 38)
	var l := UI.lbl(row[1], 19)
	l.custom_minimum_size = Vector2(420, 0)
	h.add_child(l)
	match row[2]:
		"bool":
			var cb := CheckButton.new()
			cb.button_pressed = Settings.gb(key)
			cb.toggled.connect(func(on: bool):
				Settings.s(key, on)
				Settings.apply_display()
				Audio.ui("ui_click"))
			h.add_child(cb)
		"slider":
			var sl := HSlider.new()
			sl.min_value = row[3]
			sl.max_value = row[4]
			sl.step = row[5]
			sl.value = float(Settings.g(key))
			sl.custom_minimum_size = Vector2(300, 28)
			sl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			var val := UI.lbl(str(snappedf(sl.value, 0.01)), 18, UI.TEXT_DIM)
			sl.value_changed.connect(func(v: float):
				var cur: Variant = Settings.g(key)
				Settings.s(key, int(v) if cur is int else v)
				val.text = str(snappedf(v, 0.01))
				Settings.apply_display()
				Settings.apply_audio())
			h.add_child(sl)
			h.add_child(val)
		"opt", "opt_str":
			var ob := OptionButton.new()
			var opts: Array = row[3]
			for o in opts:
				ob.add_item(String(o))
			var cur2: Variant = Settings.g(key)
			ob.selected = opts.find(cur2) if row[2] == "opt_str" else clampi(int(cur2), 0, opts.size() - 1)
			ob.item_selected.connect(func(i: int):
				Settings.s(key, opts[i] if row[2] == "opt_str" else i)
				Settings.apply_display())
			h.add_child(ob)
	return h

func _make_keys_tab() -> Control:
	var sc := ScrollContainer.new()
	sc.name = "Touches"
	var v := UI.vbox(6)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v)
	v.add_child(UI.lbl("Clique sur une touche puis appuie sur la nouvelle touche (Échap pour annuler).", 16, UI.TEXT_DIM))
	for a in ACTION_LABELS:
		var h := UI.hbox(10)
		var l := UI.lbl(ACTION_LABELS[a], 19)
		l.custom_minimum_size = Vector2(300, 0)
		h.add_child(l)
		var b := UI.btn(_action_text(a), "secondary", Vector2(220, 36))
		b.pressed.connect(func():
			_listening = a
			_listen_btn = b
			b.text = "… appuie sur une touche …")
		h.add_child(b)
		v.add_child(h)
	return sc

func _action_text(a: String) -> String:
	var parts: Array[String] = []
	for ev in InputMap.action_get_events(a):
		if ev is InputEventKey:
			parts.append(OS.get_keycode_string((ev as InputEventKey).physical_keycode))
		elif ev is InputEventMouseButton:
			parts.append("Souris %d" % (ev as InputEventMouseButton).button_index)
		elif ev is InputEventJoypadButton:
			parts.append("Manette %d" % (ev as InputEventJoypadButton).button_index)
	return " / ".join(parts) if not parts.is_empty() else "—"

func _unhandled_key_input(ev: InputEvent) -> void:
	if _listening == "" or not (ev is InputEventKey) or not ev.pressed:
		return
	var k := ev as InputEventKey
	if k.physical_keycode == KEY_ESCAPE:
		_listen_btn.text = _action_text(_listening)
		_listening = ""
		get_viewport().set_input_as_handled()
		return
	for e in InputMap.action_get_events(_listening).duplicate():
		if e is InputEventKey:
			InputMap.action_erase_event(_listening, e)
	var nk := InputEventKey.new()
	nk.physical_keycode = k.physical_keycode
	InputMap.action_add_event(_listening, nk)
	_listen_btn.text = _action_text(_listening)
	_listening = ""
	get_viewport().set_input_as_handled()
