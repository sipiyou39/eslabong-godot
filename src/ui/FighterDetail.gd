class_name FighterDetail
extends Control
## Fiche complète d'un mercenaire : portrait 3D, stats, compétences, niveaux (choix + reroll), maîtrises, médailles, reliques, tactiques, actions.

signal closed
signal changed

var hub: Node
var c: Campaign
var uid: String
var m: Dictionary
var body: HBoxContainer
var stage: CharacterStage

func setup(h: Node, campaign: Campaign, u: String) -> void:
	hub = h
	c = campaign
	uid = u

func _ready() -> void:
	theme = UI.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.82)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(1480, 840))
	add_child(p)
	body = UI.hbox(18)
	p.add_child(body)
	refresh()
	UI.pop_in(p)

func close() -> void:
	closed.emit()
	queue_free()

func refresh() -> void:
	m = c.merc_by_uid(uid)
	if m.is_empty():
		close()
		return
	for ch in body.get_children():
		ch.queue_free()
	body.add_child(_left())
	body.add_child(_center())
	body.add_child(_right())
	changed.emit()

# ----------------------------------------------------------------------------------------------
func _left() -> Control:
	var v := UI.vbox(8)
	v.custom_minimum_size = Vector2(350, 0)
	var tpl := MercLogic.tpl_for(m)
	var nm := UI.lbl(String(m["name"]), 30, UI.GOLD, false, true)
	v.add_child(nm)
	var sub := UI.hbox(6)
	sub.add_child(UI.tex_rect(UI.class_icon(String(m["class_id"])), Vector2(36, 36)))
	var role: String = String(tpl.get("role", ""))
	sub.add_child(UI.lbl("%s • %s" % [tpl["display_name"], Data.ROLE_NAME_FR.get(role, "")], 19, Data.ROLE_COLOR.get(role, UI.TEXT), true))
	v.add_child(sub)
	stage = CharacterStage.new(Vector2(350, 400))
	stage.set_merc(m)
	v.add_child(stage)
	var tags := UI.hbox(6)
	tags.add_child(UI.lbl("★".repeat(MercLogic.star_rating(m)) + "☆".repeat(5 - MercLogic.star_rating(m)), 22, UI.GOLD))
	if m["shiny"]:
		tags.add_child(UI.lbl("✦ SHINY", 17, Color("8affff"), true))
	if m["legendary"]:
		tags.add_child(UI.lbl("⚜ LÉGENDAIRE", 17, Color("ffd060"), true))
	if m["exceptional"]:
		tags.add_child(UI.lbl("Tirage exceptionnel", 15, Color("ff9aff"), true))
	if m["ascended"]:
		tags.add_child(UI.lbl("Ascendant", 15, Color("ffb060"), true))
	v.add_child(tags)
	var lv := UI.hbox(8)
	lv.add_child(UI.lbl("Niveau %d" % int(m["level"]), 22, UI.TEXT, true))
	if int(m.get("rebirth_count", 0)) > 0:
		lv.add_child(UI.lbl("↻ ×%d" % int(m["rebirth_count"]), 18, Color("c8a0ff"), true))
	v.add_child(lv)
	var xp := UIBar.new(Color("5aa8ff"), 14)
	xp.show_text = true
	xp.text_override = "XP %d / %d" % [int(m["xp"]), MercLogic.xp_needed(int(m["level"]))]
	xp.set_values(float(m["xp"]), float(MercLogic.xp_needed(int(m["level"]))))
	v.add_child(xp)
	var info := UI.vbox(2)
	info.add_child(UI.lbl("Âge %d • Salaire %s/sem. • Valeur %s" % [m["age"], Game.format_gold(m["salary"]), Game.format_gold(MercLogic.value_of(m))], 15, UI.TEXT_DIM))
	info.add_child(UI.lbl("Style de croissance : %s" % MercLogic.GROWTH_STYLES[m["growth_style"]]["name"], 15, UI.TEXT_DIM))
	if m["quirk"] != "":
		var q: Dictionary = Data.quirks[m["quirk"]]
		var ql := UI.lbl("Trait : %s — %s" % [q["name"], q["desc"]], 15, Color("c8e0ff"))
		ql.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ql.custom_minimum_size = Vector2(340, 0)
		info.add_child(ql)
	if not (m["injury"] as Dictionary).is_empty():
		info.add_child(UI.lbl("🩹 Blessé : %s (%d match)" % [m["injury"]["desc"], m["injury"]["battles"]], 16, UI.BAD, true))
	if Settings.gb("fighter_form_enabled"):
		var f := int(m["form"])
		info.add_child(UI.lbl("Forme : %s%d" % ["+" if f > 0 else "", f], 16, UI.GOOD if f > 0 else (UI.BAD if f < 0 else UI.TEXT_DIM), true))
	v.add_child(info)
	return v

func _center() -> Control:
	var v := UI.vbox(8)
	v.custom_minimum_size = Vector2(430, 0)
	if int(m["pending_levels"]) > 0:
		v.add_child(_levelup_box())
	v.add_child(UI.lbl("Caractéristiques", 24, UI.GOLD, false, true))
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 20)
	for row in MercLogic.describe_stats(m):
		var h := UI.hbox(6)
		h.add_child(UI.tex_rect(UI.stat_icon(row[0]), Vector2(24, 24)))
		var l := UI.lbl(str(row[1]), 18, UI.TEXT_DIM)
		l.custom_minimum_size = Vector2(110, 0)
		h.add_child(l)
		h.add_child(UI.lbl(str(row[2]), 19, UI.TEXT, true))
		grid.add_child(h)
	v.add_child(grid)
	var birth := UI.lbl("Tirages de naissance : " + "  ".join(MercLogic.STAT_KEYS.map(func(k): return "%s %+d%%" % [k, int(round((float(m["birth"][k]) - 1.0) * 100.0))])), 14, UI.TEXT_DIM)
	birth.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	birth.custom_minimum_size = Vector2(420, 0)
	v.add_child(birth)
	v.add_child(UI.hsep())
	v.add_child(UI.lbl("Compétences", 24, UI.GOLD, false, true))
	var tpl := MercLogic.tpl_for(m)
	var kit: Array = tpl["kit"]
	var labels := ["Attaque de base", "Esquive", "Compétence 1", "Compétence 2", "Compétence 3", "Compétence ultime"]
	for i in kit.size():
		var ab: Dictionary = Data.ability(String(kit[i]))
		if ab.is_empty():
			continue
		var row := UI.hbox(10)
		var ic := UI.tex_rect(UI.ability_icon(ab), Vector2(46, 46))
		ic.mouse_filter = Control.MOUSE_FILTER_PASS
		ic.tooltip_text = BattleHUD._ability_desc(ab)
		row.add_child(ic)
		var tv := UI.vbox(0)
		tv.add_child(UI.lbl(String(ab["name"]), 18, Data.elem_color(String(ab["element"])).lightened(0.35), true))
		tv.add_child(UI.lbl("%s • %s  •  CD %.1fs" % [labels[min(i, 5)], Data.ELEM_NAME_FR.get(String(ab["element"]), ""), float(ab["cd"])], 14, UI.TEXT_DIM))
		row.add_child(tv)
		v.add_child(row)
	v.add_child(UI.hsep())
	var mrow := UI.hbox(8)
	mrow.add_child(UI.lbl("Maîtrises", 20, UI.GOLD, true))
	for mid in m["mastery"]:
		for o in MercLogic.MASTERY_OPTIONS:
			if o["id"] == mid:
				var l2 := UI.lbl("✦ %s" % o["name"], 16, Color("c8e0ff"), true)
				l2.tooltip_text = o["desc"]
				l2.mouse_filter = Control.MOUSE_FILTER_PASS
				mrow.add_child(l2)
	if m.get("pending_mastery", false):
		var mb := UI.btn("Choisir une maîtrise", "primary", Vector2(0, 34))
		mb.pressed.connect(_mastery_dialog)
		mrow.add_child(mb)
	v.add_child(mrow)
	var medrow := UI.hbox(8)
	medrow.add_child(UI.lbl("Médailles", 20, UI.GOLD, true))
	for md in Data.medals:
		var tier := int(m["medals"].get(md["id"], 0))
		var l3 := UI.lbl("%s %s" % [md["name"], "I".repeat(tier) if tier > 0 else "—"], 15, UI.GOLD if tier > 0 else UI.TEXT_DIM, true)
		l3.tooltip_text = String(md["desc"])
		l3.mouse_filter = Control.MOUSE_FILTER_PASS
		medrow.add_child(l3)
	v.add_child(medrow)
	return v

func _levelup_box() -> Control:
	var p := UI.panel("header")
	var v := UI.vbox(6)
	p.add_child(v)
	v.add_child(UI.lbl("⬆ NIVEAU SUPÉRIEUR — %d choix en attente" % int(m["pending_levels"]), 20, UI.GOLD, true))
	if (m["choice"] as Dictionary).is_empty() or not m["choice"].has("opts"):
		m["choice"] = {"opts": MercLogic.roll_choices(m, c.rng)}
	var row := UI.hbox(8)
	for opt in m["choice"]["opts"]:
		var b := UI.btn("", "secondary", Vector2(130, 76))
		var bv := UI.vbox(0)
		bv.mouse_filter = Control.MOUSE_FILTER_IGNORE
		bv.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		var names := {"hp": "PV", "damage": "Puissance", "defense": "Défense", "move_speed": "Vitesse"}
		var icons := {"hp": "hp", "damage": "power", "defense": "defense", "move_speed": "speed"}
		var t := UI.lbl("+%s%%" % str(opt["value"]), 24, UI.GOOD, true)
		t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		bv.add_child(t)
		var t2 := UI.lbl(String(names[opt["stat"]]), 16, UI.TEXT, true)
		t2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		bv.add_child(t2)
		b.add_child(bv)
		b.pressed.connect(func():
			MercLogic.apply_choice(m, opt)
			Audio.ui("ui_levelup")
			Game.toast("%s : +%s%% %s" % [m["name"], str(opt["value"]), names[opt["stat"]]], "good")
			refresh())
		row.add_child(b)
	v.add_child(row)
	var br := HBoxContainer.new()
	br.add_theme_constant_override("separation", 8)
	var cost := 100 + 20 * int(m["level"])
	var reroll := UI.btn("Relancer (%d or%s)" % [cost, " — gratuit" if not m["reroll_used"] else ""], "secondary", Vector2(0, 34))
	reroll.pressed.connect(func():
		if m["reroll_used"]:
			if c.gold < cost:
				Game.toast("Pas assez d'or.", "error")
				return
			c.gold -= cost
		m["reroll_used"] = true
		m["choice"] = {"opts": MercLogic.roll_choices(m, c.rng)}
		refresh())
	br.add_child(reroll)
	var auto := UI.btn("Auto", "secondary", Vector2(0, 34))
	auto.pressed.connect(func():
		MercLogic.auto_pick_stat(m, c.rng)
		refresh())
	br.add_child(auto)
	v.add_child(br)
	return p

func _mastery_dialog() -> void:
	var dlg := Control.new()
	dlg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.7)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dlg.add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(600, 0))
	dlg.add_child(p)
	var v := UI.vbox(8)
	p.add_child(v)
	v.add_child(UI.lbl("Choisir une maîtrise", 28, UI.GOLD, false, true))
	var opts := MercLogic.MASTERY_OPTIONS.duplicate()
	opts.shuffle()
	for o in opts.slice(0, 3):
		var b := UI.btn("%s — %s" % [o["name"], o["desc"]], "secondary", Vector2(0, 50))
		b.pressed.connect(func():
			m["mastery"].append(o["id"])
			m["pending_mastery"] = false
			dlg.queue_free()
			Audio.ui("ui_unlock")
			refresh())
		v.add_child(b)
	add_child(dlg)

# ----------------------------------------------------------------------------------------------
func _right() -> Control:
	var v := UI.vbox(8)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var hd := UI.hbox(6)
	hd.add_child(UI.spacer(0, 0, true))
	var close_b := UI.btn("Fermer", "secondary", Vector2(110, 40))
	close_b.pressed.connect(close)
	hd.add_child(close_b)
	v.add_child(hd)
	var tabs := TabContainer.new()
	tabs.size_flags_vertical = Control.SIZE_EXPAND_FILL
	tabs.add_child(_relic_tab())
	tabs.add_child(_tactics_tab())
	tabs.add_child(_career_tab())
	tabs.set_tab_title(0, "Reliques")
	tabs.set_tab_title(1, "Tactiques")
	tabs.set_tab_title(2, "Carrière")
	v.add_child(tabs)
	v.add_child(_actions())
	return v

func _relic_tab() -> Control:
	var sc := ScrollContainer.new()
	sc.name = "Reliques"
	var v := UI.vbox(6)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v)
	var slots := MercLogic.relic_slots(m)
	v.add_child(UI.lbl("Emplacements : %d / 2  %s" % [slots, "" if slots >= 2 else "(2e emplacement au niveau 5)"], 18, UI.TEXT_DIM, true))
	for i in 2:
		var row := UI.panel("inset")
		var h := UI.hbox(10)
		row.add_child(h)
		if i < m["relics"].size():
			var iid: String = m["relics"][i]
			var item: Dictionary = c.relic_inv.get(iid, {})
			var r: Dictionary = Data.relics.get(String(item.get("rid", "")), {})
			h.add_child(UI.tex_rect(UI.relic_icon(String(r.get("icon", ""))), Vector2(52, 52)))
			var tv := UI.vbox(0)
			tv.add_child(UI.lbl(String(r.get("name", "?")), 19, Data.RARITY_COLOR.get(String(r.get("rarity", "common")), UI.TEXT), true))
			var d := UI.lbl(_relic_desc(item, r), 15, UI.TEXT_DIM)
			d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			d.custom_minimum_size = Vector2(340, 0)
			tv.add_child(d)
			h.add_child(tv)
			var rb := UI.btn("Retirer", "secondary", Vector2(80, 34))
			rb.pressed.connect(func():
				Market.unequip_relic(c, iid)
				refresh())
			h.add_child(rb)
		else:
			h.add_child(UI.tex_rect(UI.stat_icon("relic_slot"), Vector2(52, 52), Color(1, 1, 1, 0.4 if i < slots else 0.15)))
			h.add_child(UI.lbl("Emplacement vide" if i < slots else "Verrouillé (niveau 5)", 18, UI.TEXT_DIM))
		v.add_child(row)
	v.add_child(UI.hsep())
	v.add_child(UI.lbl("Inventaire de reliques", 20, UI.GOLD, true))
	var inv: Array = c.relic_inv.values()
	inv.sort_custom(func(a, b): return Data.relics[a["rid"]]["price"] > Data.relics[b["rid"]]["price"])
	if inv.is_empty():
		v.add_child(UI.lbl("Aucune relique. Gagne des coffres ou visite le marché.", 17, UI.TEXT_DIM))
	for item in inv:
		if item["iid"] in m["relics"]:
			continue
		var r: Dictionary = Data.relics[item["rid"]]
		var row2 := UI.hbox(8)
		row2.add_child(UI.tex_rect(UI.relic_icon(String(r["icon"])), Vector2(38, 38)))
		var tv2 := UI.vbox(0)
		tv2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var owner_name := Market.relic_owner(c, item["iid"])
		tv2.add_child(UI.lbl("%s%s" % [r["name"], "  (équipée : %s)" % owner_name if owner_name != "" else ""], 17, Data.RARITY_COLOR.get(String(r["rarity"]), UI.TEXT), true))
		var dd := UI.lbl(_relic_desc(item, r), 14, UI.TEXT_DIM)
		dd.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		dd.custom_minimum_size = Vector2(300, 0)
		tv2.add_child(dd)
		row2.add_child(tv2)
		var eb := UI.btn("Équiper", "secondary", Vector2(80, 32))
		eb.pressed.connect(func():
			Market.equip_relic(c, uid, item["iid"])
			Audio.ui("ui_confirm")
			refresh())
		row2.add_child(eb)
		var sb := UI.btn("%d" % int(float(r["price"]) * 0.45), "secondary", Vector2(70, 32))
		sb.icon = UI.stat_icon("gold")
		sb.expand_icon = true
		sb.tooltip_text = "Vendre"
		sb.pressed.connect(func():
			var got := Market.sell_relic(c, item["iid"])
			Audio.ui("ui_sell")
			Game.toast("Relique vendue : +%d or" % got, "gold")
			refresh())
		row2.add_child(sb)
		v.add_child(row2)
	return sc

func _relic_desc(item: Dictionary, r: Dictionary) -> String:
	var val := float(r.get("value", 0)) * float(item.get("roll", 1.0))
	var t: String = String(r.get("desc", ""))
	var base_v: float = float(r.get("value", 0))
	var base_s := str(int(base_v) if base_v == int(base_v) else base_v)
	var new_s := str(snappedf(val, 0.1))
	return t.replace(base_s, new_s)

func _tactics_tab() -> Control:
	var sc := ScrollContainer.new()
	sc.name = "Tactiques"
	var v := UI.vbox(8)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v)
	var t: Dictionary = m["tactics"]
	v.add_child(UI.lbl("Profil tactique de l'IA", 20, UI.GOLD, true))
	for it in [["aggression", "Agressivité", "Se jette dans la mêlée dès l'engagement."], ["aim", "Précision de visée", "Anticipe les mouvements de la cible."],
			["reflexes", "Réflexes", "Réagit plus vite aux zones et dangers."], ["ability_usage", "Usage des compétences", "Fréquence d'utilisation des sorts."],
			["cohesion", "Cohésion", "Reste proche des alliés."], ["distance", "Distance préférée", "Multiplie la portée idéale de combat."]]:
		var row := UI.hbox(8)
		var l := UI.lbl(it[1], 17)
		l.custom_minimum_size = Vector2(170, 0)
		l.tooltip_text = it[2]
		l.mouse_filter = Control.MOUSE_FILTER_PASS
		row.add_child(l)
		var sl := HSlider.new()
		var is_dist: bool = it[0] == "distance"
		sl.min_value = 0.6 if is_dist else 0.0
		sl.max_value = 1.6 if is_dist else 1.0
		sl.step = 0.05
		sl.value = float(t.get(it[0], 1.0 if is_dist else 0.6))
		sl.custom_minimum_size = Vector2(190, 24)
		sl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var val := UI.lbl(str(snappedf(sl.value, 0.01)), 15, UI.TEXT_DIM)
		sl.value_changed.connect(func(x: float):
			t[it[0]] = x
			val.text = str(snappedf(x, 0.01)))
		row.add_child(sl)
		row.add_child(val)
		v.add_child(row)
	var r2 := UI.hbox(8)
	r2.add_child(UI.lbl("Style défensif", 17))
	var ds := OptionButton.new()
	var dopts := ["balanced", "block", "kite"]
	for n in ["Équilibré", "Bloquer", "Maintenir la distance"]:
		ds.add_item(n)
	ds.selected = maxi(dopts.find(String(t.get("defense_style", "balanced"))), 0)
	ds.item_selected.connect(func(i: int): t["defense_style"] = dopts[i])
	r2.add_child(ds)
	v.add_child(r2)
	var r3 := UI.hbox(8)
	r3.add_child(UI.lbl("Priorité de cible", 17))
	var tp := OptionButton.new()
	var topts := ["nearest", "lowest_health", "high_threat"]
	for n in ["Plus proche", "Moins de PV", "Menace élevée"]:
		tp.add_item(n)
	tp.selected = maxi(topts.find(String(t.get("target_priority", "nearest"))), 0)
	tp.item_selected.connect(func(i: int): t["target_priority"] = topts[i])
	r3.add_child(tp)
	v.add_child(r3)
	var r4 := UI.hbox(8)
	r4.add_child(UI.lbl("Min. de cibles pour les zones", 17))
	var sp := SpinBox.new()
	sp.min_value = 1
	sp.max_value = 4
	sp.value = int(t.get("aoe_efficiency", 2))
	sp.value_changed.connect(func(x: float): t["aoe_efficiency"] = int(x))
	r4.add_child(sp)
	v.add_child(r4)
	var ff := CheckBox.new()
	ff.text = "Éviter le tir allié"
	ff.button_pressed = bool(t.get("friendly_fire_avoid", true))
	ff.toggled.connect(func(on: bool): t["friendly_fire_avoid"] = on)
	v.add_child(ff)
	return sc

func _career_tab() -> Control:
	var sc := ScrollContainer.new()
	sc.name = "Carrière"
	var v := UI.vbox(6)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v)
	var cr: Dictionary = m["career"]
	for row in [["Combats", cr["battles"]], ["Victoires", cr["wins"]], ["Éliminations", cr["kills"]], ["Assistances", cr["assists"]], ["Dégâts infligés", int(cr["damage"])],
			["Dégâts subis", int(cr["taken"])], ["PV soignés", int(cr["healing"])], ["Résurrections", cr["res"]], ["MVP", cr["mvp"]], ["Blessures subies", m["injuries_sustained"]]]:
		var h := UI.hbox(6)
		var l := UI.lbl(String(row[0]), 18, UI.TEXT_DIM)
		l.custom_minimum_size = Vector2(200, 0)
		h.add_child(l)
		h.add_child(UI.lbl(Game.format_gold(float(row[1])), 18, UI.TEXT, true))
		v.add_child(h)
	return sc

func _actions() -> Control:
	var h := UI.hbox(8)
	var in_line: bool = uid in c.lineup
	var b1 := UI.btn("Retirer de l'équipe" if in_line else "Titulaire", "secondary", Vector2(0, 44))
	b1.pressed.connect(func():
		if in_line:
			c.lineup.erase(uid)
		else:
			if c.lineup.size() >= 5:
				Game.toast("L'équipe est complète (5). Retire quelqu'un d'abord.", "error")
				return
			c.lineup.append(uid)
		refresh())
	h.add_child(b1)
	var b2 := UI.btn("Vendre", "danger", Vector2(0, 44))
	b2.pressed.connect(func():
		if c.roster.size() <= 5:
			Game.toast("Il faut garder au moins 5 combattants.", "error")
			return
		_confirm("Vendre %s pour %s or ?" % [m["name"], Game.format_gold(MercLogic.value_of(m) * 0.55)], func():
			Market.sell_fighter(c, uid)
			close())
	)
	h.add_child(b2)
	if int(m["level"]) >= 25 and not m["ascended"]:
		var b3 := UI.btn("Ascension", "secondary", Vector2(0, 44))
		b3.pressed.connect(_ascension)
		h.add_child(b3)
	if int(m["level"]) >= 30:
		var b4 := UI.btn("Renaissance", "secondary", Vector2(0, 44))
		b4.pressed.connect(func():
			_confirm("Renaissance : %s repart au niveau 1 avec un rattrapage accéléré et +6%% de croissance." % m["name"], func():
				MercLogic.rebirth(m, c.rng)
				Audio.ui("ui_levelup")
				refresh()))
		h.add_child(b4)
	var cost := Market.respec_cost(m)
	if float(m["bonus"]["hp"]) + float(m["bonus"]["damage"]) + float(m["bonus"]["defense"]) + float(m["bonus"]["move_speed"]) > 0.0:
		var b5 := UI.btn("Respec (%d or)" % cost, "secondary", Vector2(0, 44))
		b5.pressed.connect(func():
			if c.gold < cost:
				Game.toast("Pas assez d'or.", "error")
				return
			c.gold -= cost
			var lv := 0.0
			for k in m["bonus"]:
				if float(m["bonus"][k]) > 0.0:
					lv += 1
			m["bonus"] = {"hp": 0.0, "damage": 0.0, "defense": 0.0, "move_speed": 0.0}
			m["pending_levels"] = int(m["level"]) - 1
			m["choice"] = {}
			Game.toast("Académie : bonus de niveaux réinitialisés, rechoisis-les !", "info")
			refresh())
		h.add_child(b5)
	return h

func _ascension() -> void:
	var opts := MercLogic.ascension_options(m, c.rng)
	var dlg := Control.new()
	dlg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.7)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dlg.add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(680, 0))
	dlg.add_child(p)
	var v := UI.vbox(8)
	p.add_child(v)
	v.add_child(UI.lbl("Ascension : compétence d'une autre classe", 26, UI.GOLD, false, true))
	for id in opts:
		var ab: Dictionary = Data.ability(String(id))
		var b := UI.btn("", "secondary", Vector2(0, 66))
		var hb := UI.hbox(10)
		hb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		hb.offset_left = 10
		hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
		hb.add_child(UI.tex_rect(UI.ability_icon(ab), Vector2(50, 50)))
		var tv := UI.vbox(0)
		tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tv.add_child(UI.lbl(String(ab["name"]), 20, Data.elem_color(String(ab["element"])).lightened(0.3), true))
		tv.add_child(UI.lbl(BattleHUD._ability_desc(ab).replace("\n", "  •  "), 14, UI.TEXT_DIM))
		hb.add_child(tv)
		b.add_child(hb)
		b.pressed.connect(func():
			m["ascended"] = true
			m["ascend_ability"] = id
			Audio.ui("ui_unlock")
			dlg.queue_free()
			refresh())
		v.add_child(b)
	add_child(dlg)

func _confirm(text: String, on_yes: Callable) -> void:
	var dlg := Control.new()
	dlg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.65)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dlg.add_child(dim)
	var p := UI.panel("gold")
	UI.center(p, Vector2(560, 0))
	dlg.add_child(p)
	var v := UI.vbox(12)
	p.add_child(v)
	var l := UI.lbl(text, 21)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(520, 0)
	v.add_child(l)
	var h := UI.hbox(10)
	var yes := UI.btn("Confirmer", "primary", Vector2(180, 44))
	var no := UI.btn("Annuler", "secondary", Vector2(140, 44))
	yes.pressed.connect(func():
		dlg.queue_free()
		on_yes.call())
	no.pressed.connect(func(): dlg.queue_free())
	h.add_child(yes)
	h.add_child(no)
	v.add_child(h)
	add_child(dlg)
