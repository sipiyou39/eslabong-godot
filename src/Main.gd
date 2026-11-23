extends Node
## Point d'entrée : menu principal, ou harnais de test (--test-battle).

func _ready() -> void:
	if Game.args.has("nopostfx"):
		Settings.s("postfx_enabled", false)
	if Game.args.has("novfog"):
		Settings.s("volumetric_fog", false)
	for k in Game.args:
		if String(k).begins_with("test-"):
			Campaign.save_path = "user://test_run_save.json"
	await get_tree().process_frame
	await get_tree().process_frame
	if Game.args.has("test-battle"):
		_test_battle()
		return
	if Game.args.has("test-model"):
		_test_model()
		return
	if Game.args.has("test-hub"):
		_test_hub()
		return
	if Game.args.has("test-mode"):
		_test_mode()
		return
	if Game.args.has("test-screen"):
		_test_screen()
		return
	if Game.args.has("test-sim"):
		_test_sim()
		return
	if Game.args.has("test-menu"):
		await get_tree().create_timer(4.0).timeout
		Game.goto_main_menu()
		var base_p := String(Game.args.get("shot", "/tmp/eslab_menu.png"))
		var last_t := 0.0
		for d in String(Game.args.get("times", "4")).split(","):
			await get_tree().create_timer(float(d) - last_t).timeout
			last_t = float(d)
			Game.screenshot(base_p.replace(".png", "_t%s.png" % d))
		get_tree().quit()
		return
	Game.goto_main_menu()

func _test_battle() -> void:
	var rnd := RandomNumberGenerator.new()
	rnd.seed = int(Game.args.get("seed", "7"))
	var n := int(Game.args.get("n", "5"))
	var lvl := int(Game.args.get("level", "6"))
	var a := MatchFactory.random_team("Skvell D", n, lvl, rnd)
	var b := MatchFactory.random_team("Black Ravens", n, lvl, rnd)
	for key in ["teamA", "teamB"]:
		if Game.args.has(key):
			var fl: Array = []
			for id in String(Game.args[key]).split(","):
				fl.append(MatchFactory.random_spec(String(id), lvl, rnd))
			if key == "teamA":
				a["fighters"] = fl
			else:
				b["fighters"] = fl
	var cfg := MatchFactory.config_for([a, b], String(Game.args.get("theme", "colosseum")))
	cfg["rounds_to_win"] = int(Game.args.get("rounds", "1"))
	if Game.args.has("auto"):
		cfg["allow_control"] = false
	if Game.args.has("speed"):
		Settings.s("battle_speed_mode", int(Game.args["speed"]))
	if Game.args.has("quit-on-finish"):
		cfg["auto_exit"] = true
		cfg["on_finish"] = func(res: Dictionary):
			print("RESULT winner=", res.get("winner"), " wins=", res.get("wins"), " rounds=", res.get("rounds"))
			get_tree().quit()
	Game.start_battle(cfg)
	if Game.args.has("control-test"):
		await get_tree().create_timer(8.0).timeout
		var bt := Game.current_scene as Battle
		if bt and bt.controlled_fighter():
			var f := bt.controlled_fighter()
			print("CTRL before pos=", f.global_position, " cds=", f.cds, " mana=", f.mana)
			Input.action_press("move_down")
			Input.action_press("attack")
			await get_tree().create_timer(1.0).timeout
			Input.action_press("ability_1")
			await get_tree().create_timer(0.05).timeout
			print("CTRL dbg buf=", f.input_buf, " cast_empty=", f.cast.is_empty(), " ready2=", f.ability_ready(2), " kit2=", f.kit[2].get("id"), " cost=", f.cost_mana(2), " can_act=", f.can_act(), " state=", bt.state, " pidx=", f.player_index, " just=", Input.is_action_just_pressed("ability_1"))
			await get_tree().create_timer(0.15).timeout
			Input.action_release("ability_1")
			Input.action_press("dash")
			await get_tree().create_timer(0.2).timeout
			Input.action_release("dash")
			await get_tree().create_timer(1.0).timeout
			Input.action_release("move_down")
			Input.action_release("attack")
			print("CTRL after pos=", f.global_position, " cds=", f.cds, " mana=", f.mana, " sta=", f.sta)
		else:
			print("CTRL none")
	if Game.args.has("shot"):
		var delay := float(Game.args.get("shot-delay", "6"))
		var count := int(Game.args.get("shot-count", "1"))
		for i in count:
			await get_tree().create_timer(delay).timeout
			var p := String(Game.args["shot"])
			if count > 1:
				p = p.replace(".png", "_%d.png" % i)
			Game.screenshot(p)
		if not Game.args.has("keep"):
			get_tree().quit()

func _test_model() -> void:
	if Game.args.has("no-outline"):
		Settings.s("unit_outlines_enabled", false)
	var ids: Array = String(Game.args.get("ids", "Merc_Warrior_Fighter,Merc_Mage_Fire,Merc_Orc_Berserker,Merc_Goblin_Ambusher,Merc_Minotaur_Bullbreaker,Merc_Necromancer,Merc_Werewolf,Merc_Hellforged")).split(",")
	var layer := CanvasLayer.new()
	add_child(layer)
	var bg := ColorRect.new()
	bg.color = Color("1a1626")
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.add_child(bg)
	var grid := GridContainer.new()
	grid.columns = mini(ids.size(), 4)
	grid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.add_child(grid)
	for id in ids:
		var st := CharacterStage.new(Vector2(480, 520))
		st.spin = false
		grid.add_child(st)
		st.set_template(Data.template(String(id)))
	await get_tree().create_timer(1.5).timeout
	Game.screenshot(String(Game.args.get("shot", "/tmp/eslab_models.png")))
	get_tree().quit()

func _test_hub() -> void:
	var rnd := RandomNumberGenerator.new()
	rnd.seed = 5
	var starters: Array = []
	for id in ["Merc_Warrior_Fighter", "Merc_Mage_Fire", "Merc_Healer_Priest", "Merc_Archer_Bowman", "Merc_Orc_Berserker", "Merc_Rogue_Assasin", "Merc_Paladin_Templar"]:
		starters.append(MercLogic.generate(id, 4, rnd))
	starters[0]["pending_levels"] = 1
	Game.campaign = Campaign.create("Skvell D", {"shield": 3, "division": 5, "charge": 17, "base_color": "#1a1a22", "field_color": "#f2ead0", "charge_color": "#c0392b", "division_color": "#2f5ea8"}, 1, starters, 123)
	Game.campaign.lineup = Game.campaign.lineup.slice(0, 5)
	Game.goto_hub()
	await get_tree().create_timer(3.0).timeout
	var tabs: Array = String(Game.args.get("tabs", "home,roster,market,club,league,modes,news")).split(",")
	var base := String(Game.args.get("shot", "/tmp/eslab_hub.png"))
	for t in tabs:
		var hub := Game.current_scene as HubScreen
		if hub == null:
			print("hub null")
			break
		hub.open_tab(String(t))
		await get_tree().create_timer(1.6).timeout
		Game.screenshot(base.replace(".png", "_%s.png" % t))
	if Game.args.has("detail"):
		var hub2 := Game.current_scene as HubScreen
		hub2.open_fighter(Game.campaign.roster[0]["uid"])
		await get_tree().create_timer(1.6).timeout
		print("DBG modal_layer ", hub2.modal_layer.size, hub2.modal_layer.get_global_rect(), " detail ", hub2.modal_layer.get_child(0).size, hub2.modal_layer.get_child(0).get_global_rect(), " root ", hub2.root.size, " vp ", get_viewport().get_visible_rect())
		Game.screenshot(base.replace(".png", "_detail.png"))
	get_tree().quit()

## Simulation de campagne sans rendu : enchaîne des semaines (événements simulés), teste sauvegarde/chargement et fin de saison
func _test_sim() -> void:
	var rnd := RandomNumberGenerator.new()
	rnd.seed = 9
	var starters: Array = []
	for id in ["Merc_Warrior_Fighter", "Merc_Mage_Fire", "Merc_Healer_Priest", "Merc_Archer_Bowman", "Merc_Orc_Berserker", "Merc_Rogue_Assasin", "Merc_Paladin_Templar"]:
		starters.append(MercLogic.generate(id, 4, rnd))
	var c := Campaign.create("Test FC", {"shield": 1, "division": 2, "charge": 3, "base_color": "#111111", "field_color": "#eeeeee", "charge_color": "#aa2222", "division_color": "#2244aa"}, 1, starters, 77)
	Game.campaign = c
	var weeks := int(Game.args.get("weeks", "70"))
	for w in weeks:
		var evs := c.events_this_week()
		for ev in evs:
			if ev["done"]:
				continue
			var kind: String = String(ev["kind"])
			var cfg := {}
			match kind:
				"league": cfg = Results.league_config(c, ev)
				"cup": cfg = Results.cup_config(c, ev)
				"special_3v3v3v3": cfg = Results.special_config(c, ev)
				"academy", "academy_placement": cfg = Results.academy_config(c, ev)
				"chaos": cfg = Results.chaos_config(c, c.roster[0]["uid"])
				"tower": cfg = Results.tower_config(c, c.tower_floor + 1)
				_: continue
			var res := Results.quick_sim_event(c, cfg)
			var rep := Results.finish_event(c, ev, res, cfg)
			if kind in ["tower"] and c.stats["tower_best"] > 5:
				pass
		# auto-pick des niveaux
		for m in c.roster:
			MercLogic.auto_pick_stat(m, c.rng)
		var before_w := c.week
		var before_s := c.season
		Results.advance_week(c)
		if c.season != before_s:
			print("SEASON END -> season ", c.season, " div ", c.player_div, " gold ", int(c.gold), " trophies ", c.trophies.size(), " roster ", c.roster.size())
	var sd := c.to_dict()
	var js := JSON.stringify(sd)
	var c2 := Campaign.from_dict(JSON.parse_string(js))
	print("SIM DONE season=", c.season, " week=", c.week, " gold=", int(c.gold), " wins=", c.stats["wins"], " losses=", c.stats["losses"], " ach=", c.achievements.keys().size(), " save_bytes=", js.length(), " reload_ok=", c2.roster.size() == c.roster.size())
	print("ACH: ", c.achievements.keys())
	for m in c.roster.slice(0, 3):
		print("  ", m["name"], " lvl ", m["level"], " rating ", int(MercLogic.rating(m)))
	get_tree().quit()

func _test_screen() -> void:
	var which := String(Game.args.get("test-screen", "settings"))
	var rnd := RandomNumberGenerator.new()
	rnd.seed = 5
	var starters: Array = []
	for id in ["Merc_Warrior_Fighter", "Merc_Mage_Fire", "Merc_Healer_Priest", "Merc_Archer_Bowman", "Merc_Orc_Berserker", "Merc_Rogue_Assasin", "Merc_Paladin_Templar"]:
		starters.append(MercLogic.generate(id, 4, rnd))
	Game.campaign = Campaign.create("Skvell D", {"shield": 3, "division": 5, "charge": 17, "base_color": "#1a1a22", "field_color": "#f2ead0", "charge_color": "#c0392b", "division_color": "#2f5ea8"}, 1, starters, 123)
	var c := Game.campaign
	c.relic_inv = {}
	for i in 4:
		Market.new_relic_item(c, Market.random_relic_id(c, i))
	await get_tree().create_timer(0.5).timeout
	Game.goto_main_menu()
	await get_tree().create_timer(2.5).timeout
	var menu := Game.current_scene as MainMenu
	var hub: HubScreen = null
	var node: Control = null
	match which:
		"settings": node = SettingsScreen.new()
		"new": node = NewCampaignScreen.new()
		"custom": node = CustomMatchScreen.new()
		"hall": node = HallScreen.new()
		"ach": node = AchievementsScreen.new()
		_:
			Game.goto_hub()
			await get_tree().create_timer(2.5).timeout
			hub = Game.current_scene as HubScreen
			var ev: Dictionary = c.events_this_week()[0]
			match which:
				"prep":
					var mp := MatchPrep.new()
					mp.setup(hub, c, ev)
					node = mp
				"report":
					var cfg := Results.league_config(c, ev)
					var res := Results.quick_sim_event(c, cfg)
					var rep := Results.finish_event(c, ev, res, cfg)
					rep["chest"] = Market.open_chest(c, 2)
					var ps := PostMatchScreen.new()
					ps.setup(hub, c, rep)
					node = ps
				"chest":
					var ch := ChestScreen.new()
					ch.reward = Market.open_chest(c, 3)
					node = ch
				"draft":
					var d := DraftScreen.new()
					d.setup(hub, c, ev)
					node = d
				"chaos":
					var cp := ChaosPicker.new()
					cp.setup(hub, c, ev)
					node = cp
	if node:
		if hub:
			hub.open_modal(node)
		else:
			menu.root.add_child(node)
	await get_tree().create_timer(1.2).timeout
	if which == "chest" and node:
		node._open()
		await get_tree().create_timer(2.0).timeout
	if which == "draft" and node:
		node.call("_next_round")
		await get_tree().create_timer(1.5).timeout
	Game.screenshot(String(Game.args.get("shot", "/tmp/eslab_screen.png")))
	get_tree().quit()

func _test_mode() -> void:
	var rnd := RandomNumberGenerator.new()
	rnd.seed = 12
	var starters: Array = []
	for id in ["Merc_Warrior_Fighter", "Merc_Mage_Fire", "Merc_Healer_Priest", "Merc_Archer_Bowman", "Merc_Orc_Berserker", "Merc_Rogue_Assasin", "Merc_Paladin_Templar"]:
		starters.append(MercLogic.generate(id, 12, rnd))
	var c := Campaign.create("Test FC", {"shield": 1, "division": 2, "charge": 3, "base_color": "#111111", "field_color": "#eeeeee", "charge_color": "#aa2222", "division_color": "#2244aa"}, 1, starters, 77)
	Game.campaign = c
	var kind := String(Game.args.get("test-mode", "tower"))
	var ev := {"id": kind, "kind": kind, "label": kind}
	var cfg := {}
	match kind:
		"tower": cfg = Results.tower_config(c, 1)
		"irongate": cfg = Results.irongate_config(c, int(Game.args.get("floor", "5")))
		"chaos": cfg = Results.chaos_config(c, c.roster[0]["uid"])
		"special": cfg = Results.special_config(c, ev)
		"academy": cfg = Results.academy_config(c, ev)
		"league":
			ev["opp"] = c.opponent_id()
			cfg = Results.league_config(c, ev)
	cfg["allow_control"] = false
	cfg["auto_exit"] = true
	Settings.s("battle_speed_mode", 2)
	cfg["on_finish"] = func(res: Dictionary):
		print("MODE ", kind, " RESULT winner=", res.get("winner"), " wins=", res.get("wins"), " teams=", res.get("teams").size(), " fighters=", res.get("teams")[0]["fighters"].size())
		get_tree().quit()
	Game.start_battle(cfg)
