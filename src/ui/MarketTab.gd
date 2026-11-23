class_name MarketTab
extends Control
## Onglet Marché : combattants à recruter (aperçu 3D), reliques, filtres.

var hub: Node
var c: Campaign
var mode: String = "fighters"
var sort_key: String = "power"
var role_filter: String = "all"
var stage: CharacterStage
var info: VBoxContainer

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	sort_key = String(Settings.g("market_fighter_sort")).to_lower().split("_")[0] if false else "price"
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
	var hd := UI.hbox(10)
	hd.add_child(UI.lbl("MARCHÉ DES TRANSFERTS", 30, UI.GOLD, false, true))
	hd.add_child(UI.spacer(0, 0, true))
	var b1 := UI.btn("Combattants", "primary" if mode == "fighters" else "secondary", Vector2(150, 40))
	b1.pressed.connect(func():
		mode = "fighters"
		rebuild())
	var b2 := UI.btn("Reliques", "primary" if mode == "relics" else "secondary", Vector2(150, 40))
	b2.pressed.connect(func():
		mode = "relics"
		rebuild())
	hd.add_child(b1)
	hd.add_child(b2)
	v.add_child(hd)
	if mode == "fighters":
		_fighters(v)
	else:
		_relics(v)

func _fighters(v: VBoxContainer) -> void:
	var fl := UI.hbox(10)
	fl.add_child(UI.lbl("Rôle", 17, UI.TEXT_DIM, true))
	var ro := OptionButton.new()
	var roles := ["all", "tank", "bruiser", "assassin", "ranged", "mage", "healer", "support", "summoner"]
	ro.add_item("Tous")
	for r in roles.slice(1):
		ro.add_item(String(Data.ROLE_NAME_FR[r]))
	ro.selected = roles.find(role_filter)
	ro.item_selected.connect(func(i: int):
		role_filter = roles[i]
		rebuild())
	fl.add_child(ro)
	fl.add_child(UI.lbl("Trier", 17, UI.TEXT_DIM, true))
	var so := OptionButton.new()
	var keys := ["price", "level", "power", "hp", "rating"]
	for n in ["Prix", "Niveau", "Puissance", "PV", "Force"]:
		so.add_item(n)
	so.selected = keys.find(sort_key)
	so.item_selected.connect(func(i: int):
		sort_key = keys[i]
		rebuild())
	fl.add_child(so)
	fl.add_child(UI.spacer(0, 0, true))
	fl.add_child(UI.lbl("Effectif %d / %d" % [c.roster.size(), Market.roster_capacity(c)], 17, UI.TEXT_DIM, true))
	var rf := UI.btn("Rafraîchir (-150)", "secondary", Vector2(170, 36))
	rf.pressed.connect(func():
		if c.gold < 150:
			Game.toast("Pas assez d'or.", "error")
			return
		c.gold -= 150
		Market.refresh_market(c)
		hub.refresh())
	fl.add_child(rf)
	v.add_child(fl)
	var body := UI.hbox(14)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	var sc := ScrollContainer.new()
	sc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	body.add_child(sc)
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(grid)
	var arr: Array = (c.market["fighters"] as Array).duplicate()
	arr = arr.filter(func(l): return role_filter == "all" or String(Data.template(String(l["merc"]["class_id"]))["role"]) == role_filter)
	arr.sort_custom(func(a, b):
		match sort_key:
			"level": return int(a["merc"]["level"]) > int(b["merc"]["level"])
			"power": return float(MercLogic.stats(a["merc"])["power"]) > float(MercLogic.stats(b["merc"])["power"])
			"hp": return float(MercLogic.stats(a["merc"])["hp"]) > float(MercLogic.stats(b["merc"])["hp"])
			"rating": return MercLogic.rating(a["merc"]) > MercLogic.rating(b["merc"])
		return int(a["price"]) < int(b["price"]))
	for l in arr:
		grid.add_child(_listing(l))
	var side := UI.vbox(6)
	side.custom_minimum_size = Vector2(340, 0)
	stage = CharacterStage.new(Vector2(340, 380))
	side.add_child(stage)
	info = UI.vbox(2)
	side.add_child(info)
	body.add_child(side)
	if not arr.is_empty():
		_preview(arr[0]["merc"])

func _preview(m: Dictionary) -> void:
	stage.set_merc(m)
	for ch in info.get_children():
		ch.queue_free()
	var tpl := MercLogic.tpl_for(m)
	info.add_child(UI.lbl("%s — %s" % [m["name"], tpl["display_name"]], 20, UI.GOLD, true))
	for row in MercLogic.describe_stats(m):
		var h := UI.hbox(6)
		h.add_child(UI.tex_rect(UI.stat_icon(row[0]), Vector2(18, 18)))
		var l := UI.lbl(str(row[1]), 15, UI.TEXT_DIM)
		l.custom_minimum_size = Vector2(110, 0)
		h.add_child(l)
		h.add_child(UI.lbl(str(row[2]), 15, UI.TEXT, true))
		info.add_child(h)
	if m["quirk"] != "":
		info.add_child(UI.lbl("Trait : %s" % Data.quirks[m["quirk"]]["name"], 15, Color("c8e0ff")))

func _listing(l: Dictionary) -> Control:
	var m: Dictionary = l["merc"]
	var tpl := Data.template(String(m["class_id"]))
	var b := Button.new()
	b.custom_minimum_size = Vector2(0, 108)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.focus_mode = Control.FOCUS_NONE
	var border := Color("4a4068")
	if m["shiny"]: border = Color("8affff")
	if m["legendary"]: border = Color("ffd060")
	if l.get("superstar", false): border = Color("ff8a3c")
	b.add_theme_stylebox_override("normal", UI.style_flat(Color(0.07, 0.06, 0.13, 0.9), border, 10, 2, 0, 8))
	b.add_theme_stylebox_override("hover", UI.style_flat(Color(0.14, 0.12, 0.24, 0.95), UI.GOLD, 10, 3, 0, 8))
	b.add_theme_stylebox_override("pressed", UI.style_flat(Color(0.14, 0.12, 0.24, 0.95), UI.GOLD, 10, 3, 0, 8))
	var hb := UI.hbox(8)
	hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hb.offset_left = 8
	hb.offset_top = 6
	hb.offset_right = -8
	hb.add_child(UI.tex_rect(UI.class_icon(String(m["class_id"])), Vector2(58, 58)))
	var tv := UI.vbox(0)
	tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var tags := ""
	if m["shiny"]: tags += " ✦"
	if m["legendary"]: tags += " ⚜"
	if l.get("superstar", false): tags += " 🔥"
	if l.get("champion", false): tags += " ★"
	var nm := UI.lbl(String(m["name"]) + tags, 18, UI.TEXT, true)
	nm.clip_text = true
	tv.add_child(nm)
	tv.add_child(UI.lbl("Niv. %d • %s • %s" % [m["level"], tpl["display_name"], "★".repeat(MercLogic.star_rating(m))], 14, Data.ROLE_COLOR.get(tpl["role"], UI.TEXT_DIM), true))
	tv.add_child(UI.lbl("Vendeur : %s%s" % [l["seller"], " • prime shiny" if m["shiny"] else ""], 13, UI.TEXT_DIM))
	hb.add_child(tv)
	var buy := UI.btn("%s" % Game.format_gold(l["price"]), "primary", Vector2(110, 40))
	buy.icon = UI.stat_icon("gold")
	buy.expand_icon = true
	buy.disabled = c.gold < l["price"]
	var lid: String = l["id"]
	buy.pressed.connect(func():
		var err := Market.buy_fighter(c, lid)
		if err != "":
			Game.toast(err, "error")
		else:
			Audio.ui("ui_buy")
			Game.toast("%s recruté !" % m["name"], "good")
			hub.refresh())
	hb.add_child(buy)
	b.add_child(hb)
	b.mouse_entered.connect(func(): _preview(m))
	return b

func _relics(v: VBoxContainer) -> void:
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(sc)
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(grid)
	var arr: Array = (c.market["relics"] as Array).duplicate()
	arr.sort_custom(func(a, b): return int(a["price"]) > int(b["price"]))
	for l in arr:
		var r: Dictionary = Data.relics[l["rid"]]
		var p := UI.panel("card")
		var h := UI.hbox(10)
		p.add_child(h)
		h.add_child(UI.tex_rect(UI.relic_icon(String(r["icon"])), Vector2(64, 64)))
		var tv := UI.vbox(0)
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tv.add_child(UI.lbl(String(r["name"]), 19, Data.RARITY_COLOR.get(String(r["rarity"]), UI.TEXT), true))
		tv.add_child(UI.lbl(String(Data.RARITY_NAME_FR.get(String(r["rarity"]), "")), 13, UI.TEXT_DIM, true))
		var d := UI.lbl(String(r["desc"]), 14, UI.TEXT)
		d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		d.custom_minimum_size = Vector2(230, 0)
		tv.add_child(d)
		h.add_child(tv)
		var buy := UI.btn("%s" % Game.format_gold(l["price"]), "primary", Vector2(104, 40))
		buy.icon = UI.stat_icon("gold")
		buy.expand_icon = true
		buy.disabled = c.gold < l["price"]
		var lid: String = l["id"]
		buy.pressed.connect(func():
			var err := Market.buy_relic(c, lid)
			if err != "":
				Game.toast(err, "error")
			else:
				Audio.ui("ui_buy")
				Game.toast("%s acquise !" % r["name"], "good")
				hub.refresh())
		h.add_child(buy)
		grid.add_child(p)
