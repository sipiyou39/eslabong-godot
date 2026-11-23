extends Node
## Réglages (fichier user://settings.cfg, mêmes sections/clés que le jeu d'origine) + table d'entrées.

const PATH := "user://settings.cfg"

# section -> { clé : défaut }
var DEFAULTS := {
	"Interface": {"ui_theme": "original", "legacy_tactics_menu": false},
	"UI": {"market_fighter_sort": "HP_DESC", "roster_bench_sort_key": "hp", "roster_bench_sort_descending": true,
		"roster_active_full_cards": false, "market_relic_sort_key": "price", "market_relic_sort_ascending": false},
	"Gameplay": {"relic_inventory_auto_sort": false, "swap_equipped_relics_on_drop": true, "confirm_relic_replacement": false,
		"prefer_empty_relic_slots": true, "relic_compatibility_highlights": true, "draft_fast_picks": false, "show_relic_swap_preview": true,
		"protect_favorite_relics": true, "double_click_relic_equip": true, "click_to_carry_relics": true,
		"friendly_fire_multiplier": 0.5, "battle_hud_visible": true, "battle_hud_opacity": 1.0, "show_hp_bars": true, "show_unit_names": 0,
		"player_locator_mode": 0, "show_ability_cooldowns": true, "show_allied_ability_cooldowns": true, "show_tactic_intent_status": true,
		"save_mid_battle_tactics_changes": false, "cast_icon_size_mode": 2, "kill_feed_display_mode": 2, "target_highlight_mode": 0,
		"show_cast_icons": true, "show_rank_indicators": true, "injuries_enabled": true, "fighter_form_enabled": true,
		"damage_numbers_player_mode": 1, "damage_numbers_spectator_mode": 1, "damage_numbers_font_size_mode": 2,
		"status_effect_text_enabled": true, "battle_speed_mode": 0, "player_1_input_mode": 2, "player_2_input_mode": 0,
		"controller_aim_speed": 600.0, "controller_aim_deadzone": 0.1, "controller_move_deadzone": 0.17, "controller_aim_assist_strength": 0.3,
		"controller_aim_style": 0, "controller_target_nearest_priority": 0, "next_campaign_difficulty": 1, "ability_cast_mode": 0,
		"channel_input_mode": 0, "colorblind_mode": false, "classic_stat_colors": false, "reduce_screen_shake": false,
		"unit_outlines_enabled": true, "aim_assist": 0, "control_scheme": 0, "haptics": true, "hold_to_attack_enabled": false,
		"health_bar_team_1_color": Color(0.18, 0.74, 0.28), "health_bar_team_2_color": Color(0.89, 0.28, 0.31),
		"health_bar_team_3_color": Color(0.62, 0.32, 0.95), "health_bar_team_4_color": Color(0.95, 0.8, 0.28)},
	"Tips": {"touch_tip_seen": false},
	"Packs": {"pack_cosmos": false, "pack_olympe": false},
	"Controls": {"player_3_remote_enabled": true, "player_4_remote_enabled": true},
	"Video": {"postfx_enabled": true, "impact_flash_enabled": true, "battle_lighting_level": 2, "battle_lighting_enabled": true, "vfx_style": 0,
		"ssao": true, "volumetric_fog": true, "shadows_quality": 2, "msaa": 2, "dof": true, "gfx_quality": 2},
	"Camera": {"aim_lookahead_far": 0.15, "aim_lookahead_close": 0.2, "aim_lookahead_vertical": 0.45, "zoom_scroll_speed_mode": 1},
	"Audio": {"master_volume": 1.0, "ui_volume": 1.0, "combat_volume": 1.0, "music_volume": 0.5, "combat_music_volume": 0.7,
		"chest_opening_music_enabled": true, "mute_when_unfocused": true},
	"Localization": {"language_code": "fr", "keep_class_names_in_english": false, "keep_champion_names_in_english": false},
	"Display": {"window_mode": 0, "window_size_percent": 1.0, "fps_cap": 0, "vsync_mode": 1, "menu_scale": 1.0, "text_scale": 1.0, "ui_scale": 1.0},
	"Accessibility": {"cursor_size_mode": 1, "readable_font_mode": true, "wide_scrollbars": false, "tooltip_details_expanded": false},
}

var _values: Dictionary = {}   # "Section/key" -> valeur
var _section_of: Dictionary = {}  # key -> section

func _ready() -> void:
	for sec in DEFAULTS:
		for k in DEFAULTS[sec]:
			_values[sec + "/" + k] = DEFAULTS[sec][k]
			_section_of[k] = sec
	var first_run := not FileAccess.file_exists(PATH)
	_load()
	if first_run and OS.has_feature("mobile"):
		_apply_mobile_defaults()
	Data.rebuild_class_list()
	_setup_input_map()
	apply_display()
	apply_audio()

func _load() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(PATH) != OK:
		return
	for sec in cfg.get_sections():
		for k in cfg.get_section_keys(sec):
			_values[sec + "/" + k] = cfg.get_value(sec, k)
			_section_of[k] = sec

## Réglages d'un premier lancement sur téléphone : rendu allégé, interface plus grande
func apply_quality(q: int) -> void:
	s("gfx_quality", q)
	match q:
		0:
			s("shadows_quality", 0)
			s("msaa", 0)
			s("postfx_enabled", false)
			s("ssao", false)
			s("volumetric_fog", false)
			s("dof", false)
		1:
			s("shadows_quality", 1)
			s("msaa", 1)
			s("postfx_enabled", true)
			s("ssao", false)
			s("volumetric_fog", false)
			s("dof", false)
		_:
			s("shadows_quality", 2)
			s("msaa", 2)
			s("postfx_enabled", true)
			s("ssao", true)
			s("volumetric_fog", true)
			s("dof", true)

func _apply_mobile_defaults() -> void:
	apply_quality(1)
	s("ui_scale", 1.35)
	s("fps_cap", 60)

func save() -> void:
	var cfg := ConfigFile.new()
	for key in _values:
		var parts: PackedStringArray = key.split("/")
		cfg.set_value(parts[0], parts[1], _values[key])
	cfg.save(PATH)

func g(key: String) -> Variant:
	var sec: String = _section_of.get(key, "")
	return _values.get(sec + "/" + key, null)

func s(key: String, value: Variant) -> void:
	var sec: String = _section_of.get(key, "Gameplay")
	_section_of[key] = sec
	_values[sec + "/" + key] = value

func gb(key: String) -> bool:
	return bool(g(key))

func gf(key: String) -> float:
	return float(g(key))

func gi(key: String) -> int:
	return int(g(key))

func team_color(i: int) -> Color:
	if i >= 4:
		return Color.from_hsv(fposmod(0.08 + float(i) * 0.137, 1.0), 0.65, 0.95)
	var c: Variant = g("health_bar_team_%d_color" % (i + 1))
	return c if c is Color else Color.WHITE

func apply_display() -> void:
	var mode: int = gi("window_mode")
	match mode:
		0: DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		1: DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_MAXIMIZED)
		2: DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
		3: DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if gi("vsync_mode") == 1 else DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = gi("fps_cap")
	var vp := get_tree().root
	vp.msaa_3d = [Viewport.MSAA_DISABLED, Viewport.MSAA_2X, Viewport.MSAA_4X, Viewport.MSAA_8X][clampi(gi("msaa"), 0, 3)]
	get_tree().root.content_scale_factor = gf("ui_scale")

func apply_audio() -> void:
	if has_node("/root/Audio"):
		get_node("/root/Audio").apply_volumes()

# ----------------------------------------------------------------------------------------------
# Entrées
# ----------------------------------------------------------------------------------------------
const ACTIONS := {
	"move_up": [KEY_W, KEY_UP], "move_down": [KEY_S, KEY_DOWN], "move_left": [KEY_A, KEY_LEFT], "move_right": [KEY_D, KEY_RIGHT],
	"dash": [KEY_SPACE], "ability_1": [], "ability_2": [KEY_Q], "ability_3": [KEY_E], "ability_4": [KEY_R],
	"switch_fighter": [KEY_TAB], "pause": [KEY_ESCAPE], "speed_cycle": [KEY_T], "tactic_1": [KEY_F1], "tactic_2": [KEY_F2],
	"tactic_3": [KEY_F3], "tactic_4": [KEY_F4], "toggle_hud": [KEY_H], "zoom_in": [], "zoom_out": [],
}

func _add_key(action: String, keycode: int) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = keycode as Key
	InputMap.action_add_event(action, ev)

func _add_btn(action: String, idx: int) -> void:
	var ev := InputEventJoypadButton.new()
	ev.button_index = idx as JoyButton
	InputMap.action_add_event(action, ev)

func _add_mouse(action: String, idx: int) -> void:
	var ev := InputEventMouseButton.new()
	ev.button_index = idx as MouseButton
	InputMap.action_add_event(action, ev)

func _add_axis(action: String, axis: int, val: float) -> void:
	var ev := InputEventJoypadMotion.new()
	ev.axis = axis as JoyAxis
	ev.axis_value = val
	InputMap.action_add_event(action, ev)

func _setup_input_map() -> void:
	for a in ACTIONS:
		if not InputMap.has_action(a):
			InputMap.add_action(a, 0.2)
		for k in ACTIONS[a]:
			_add_key(a, k)
	for a in ["attack"]:
		if not InputMap.has_action(a):
			InputMap.add_action(a, 0.2)
	_add_mouse("attack", MOUSE_BUTTON_LEFT)
	_add_mouse("ability_1", MOUSE_BUTTON_RIGHT)
	_add_mouse("zoom_in", MOUSE_BUTTON_WHEEL_UP)
	_add_mouse("zoom_out", MOUSE_BUTTON_WHEEL_DOWN)
	# manette
	_add_axis("move_left", JOY_AXIS_LEFT_X, -1.0)
	_add_axis("move_right", JOY_AXIS_LEFT_X, 1.0)
	_add_axis("move_up", JOY_AXIS_LEFT_Y, -1.0)
	_add_axis("move_down", JOY_AXIS_LEFT_Y, 1.0)
	_add_axis("attack", JOY_AXIS_TRIGGER_RIGHT, 1.0)
	_add_btn("dash", JOY_BUTTON_A)
	_add_btn("ability_1", JOY_BUTTON_X)
	_add_btn("ability_2", JOY_BUTTON_Y)
	_add_btn("ability_3", JOY_BUTTON_B)
	_add_btn("ability_4", JOY_BUTTON_RIGHT_SHOULDER)
	_add_btn("switch_fighter", JOY_BUTTON_LEFT_SHOULDER)
	_add_btn("pause", JOY_BUTTON_START)
