class_name ModesTab
extends Control
## Onglet Modes de jeu : ligue, académie, coupes, tour du défi, Defend the Iron Gate, Hall des légendes, entraînement.

var hub: Node
var c: Campaign
var gate_floor: int = 1

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	gate_floor = hub.c.stats.get("iron_gate_best", 0) + 1
	rebuild()

func rebuild() -> void:
	for ch in get_children():
		ch.queue_free()
	c = hub.c
	var p := UI.panel("glass")
	p.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(p)
	var v := UI.vbox(8)
	p.add_child(v)
	v.add_child(UI.lbl("MODES DE JEU", 30, UI.GOLD, false, true))
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(sc)
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 12)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(grid)
	var evs := c.events_this_week()
	grid.add_child(_mode("league", "Ligue principale", "5v5 • 4 divisions, 24 journées, promotion/relégation. Un match par semaine.",
		"Semaine %d / %d • %s" % [mini(c.week, Campaign.MATCHDAYS), Campaign.MATCHDAYS, c.division_name(c.player_div)], "Voir le classement", func(): hub.open_tab("league")))
	grid.add_child(_mode("academy", "Ligue Académie", "3v3 avec les remplaçants • semaines 8, 12, 16, 20, 23 + placement S25. Récompenses et Tomes de développement.",
		"Réservistes disponibles : %d" % c.bench_mercs().size(), "Jouer (si événement cette semaine)", func(): _ev_btn("academy")))
	grid.add_child(_mode("cup", "Coupe des Champions", "Élimination directe à 8 clubs : quarts S27, demies S28, finale S29.",
		"Statut : %s" % ("en lice" if c._cup_alive(c.player_id) else ("pas commencée" if c.cup.is_empty() else "éliminé")), "Calendrier", func(): hub.open_tab("league")))
	grid.add_child(_mode("thunder", "Coupe Chaos Thunder", "Un de tes champions contre 7 champions ou chefs, arène Chaos Thunder. Dernier survivant gagnant. Aucune blessure. Semaine 26.",
		"Trophées : %d" % c.trophies.size(), "Jouer (S26)", func(): _ev_btn("chaos")))
	grid.add_child(_mode("trophy", "Coupe spéciale 3v3v3v3", "Quatre équipes de trois dans la même arène (S6, S22).", "Utilise les 4 couleurs d'équipe", "Jouer (S6 / S22)", func(): _ev_btn("special")))
	grid.add_child(_mode("draft", "Coupe Draft", "Frais d'entrée 400 or : drafte 5 combattants parmi des choix aléatoires puis affronte 3 équipes (S11, S15, S19).",
		"Récompenses selon le classement", "Participer", func(): _ev_btn("draft")))
	grid.add_child(_mode("tower", "Tour du Défi", "Grimpe les étages : des équipes de plus en plus fortes. Récompenses aux jalons (S6, S15, S27 + entraînement libre).",
		"Meilleur étage : %d" % c.stats.get("tower_best", 0), "Étage %d" % (c.tower_floor + 1), func(): hub.launch_tower()))
	grid.add_child(_gate_card())
	grid.add_child(_mode("hall", "Hall des légendes", "Panthéon des champions, trophées, combattants légendaires et historique des saisons.", "", "Ouvrir", func(): hub.open_modal(HallScreen.new())))
	grid.add_child(_mode("training", "Entraînement / Match personnalisé", "Compose librement les équipes, l'arène et les règles. Sans conséquence sur la campagne.", "", "Ouvrir", func(): hub.open_modal(CustomMatchScreen.new())))
	grid.add_child(_mode("achievement", "Succès", "Tous les succès Steam de la version d'origine.", "%d / %d" % [c.achievements.size(), Achievements.LIST.size()], "Ouvrir", func(): hub.open_modal(AchievementsScreen.new())))

func _ev_btn(id: String) -> void:
	for ev in c.events_this_week():
		if ev["id"] == id or (id == "special" and ev["kind"] == "special_3v3v3v3"):
			if ev["done"]:
				Game.toast("Déjà joué cette semaine.", "info")
			else:
				hub.play_event(ev)
			return
	Game.toast("Cet événement n'est pas disponible cette semaine (voir le calendrier).", "info")

func _mode(icon: String, title: String, desc: String, status: String, btn_text: String, cb: Callable) -> Control:
	var p := UI.panel("card")
	var h := UI.hbox(14)
	p.add_child(h)
	h.add_child(UI.tex_rect(UI.stat_icon(icon), Vector2(66, 66)))
	var tv := UI.vbox(2)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(UI.lbl(title, 22, UI.GOLD, false, true))
	var d := UI.lbl(desc, 15, UI.TEXT)
	d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	d.custom_minimum_size = Vector2(360, 0)
	tv.add_child(d)
	if status != "":
		tv.add_child(UI.lbl(status, 14, UI.TEXT_DIM, true))
	h.add_child(tv)
	var b := UI.btn(btn_text, "secondary", Vector2(170, 44))
	b.pressed.connect(cb)
	h.add_child(b)
	return p

func _gate_card() -> Control:
	var p := UI.panel("card")
	var h := UI.hbox(14)
	p.add_child(h)
	h.add_child(UI.tex_rect(UI.stat_icon("gate"), Vector2(66, 66)))
	var tv := UI.vbox(2)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(UI.lbl("Defend the Iron Gate", 22, UI.GOLD, false, true))
	var d := UI.lbl("Survie par étages contre des hordes ; le boss Poroxi garde l'étage 5. Récompenses croissantes.", 15, UI.TEXT)
	d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	d.custom_minimum_size = Vector2(360, 0)
	tv.add_child(d)
	tv.add_child(UI.lbl("Meilleur étage : %d" % c.stats.get("iron_gate_best", 0), 14, UI.TEXT_DIM, true))
	h.add_child(tv)
	var col := UI.vbox(4)
	var sp := SpinBox.new()
	sp.min_value = 1
	sp.max_value = maxi(int(c.stats.get("iron_gate_best", 0)) + 1, 1)
	sp.value = gate_floor
	sp.prefix = "Étage "
	sp.value_changed.connect(func(x: float): gate_floor = int(x))
	col.add_child(sp)
	var b := UI.btn("Défendre !", "secondary", Vector2(170, 40))
	b.pressed.connect(func(): hub.launch_irongate(gate_floor))
	col.add_child(b)
	h.add_child(col)
	return p
