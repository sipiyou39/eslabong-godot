class_name Market
extends RefCounted
## Marché des transferts, reliques, installations, personnel, coffres.

static func facility_cost(c: Campaign, fid: String) -> int:
	var lv: int = int(c.facilities.get(fid, 1))
	return int(700.0 * pow(1.85, lv - 1))

static func facility_max(fid: String) -> int:
	for f in Data.facility_defs:
		if f["id"] == fid:
			return int(f["max_level"])
	return 5

static func upgrade_facility(c: Campaign, fid: String) -> bool:
	var lv: int = int(c.facilities.get(fid, 1))
	if lv >= facility_max(fid):
		return false
	var cost := facility_cost(c, fid)
	if c.gold < cost:
		return false
	c.gold -= cost
	c.facilities[fid] = lv + 1
	c._news("Amélioration du club : %s niveau %d" % [_fname(fid), lv + 1], "club")
	return true

static func _fname(fid: String) -> String:
	for f in Data.facility_defs:
		if f["id"] == fid:
			return String(f["name"])
	return fid

static func staff_cost(c: Campaign, sid: String) -> int:
	return 600 + 250 * c.staff.size()

static func staff_weekly(c: Campaign) -> int:
	return 45 * c.staff.size()

static func hire_staff(c: Campaign, sid: String) -> bool:
	if c.staff.has(sid):
		return false
	var cost := staff_cost(c, sid)
	if c.gold < cost:
		return false
	c.gold -= cost
	c.staff[sid] = {"name": NameGen.random_name(c.rng, 0.0) + " " + ["Ndiaye", "Vale", "Delacroix", "Okonkwo", "Brandt", "Moreau", "Tanaka", "Haddad"][c.rng.randi() % 8], "level": 1}
	c._news("Personnel recruté : %s (%s)" % [c.staff[sid]["name"], sid], "club")
	return true

static func fire_staff(c: Campaign, sid: String) -> void:
	c.staff.erase(sid)

static func roster_capacity(c: Campaign) -> int:
	return 10 + 2 * int(c.facilities.get("club_house", 1))

static func weekly_income(c: Campaign) -> int:
	return 140 + 55 * int(c.facilities.get("club_house", 1)) + (60 if c.player_div < 2 else 0)

static func weekly_costs(c: Campaign) -> int:
	var s := 0
	for m in c.roster:
		s += int(m["salary"])
	return s + staff_weekly(c)

# ----------------------------------------------------------------------------------------------
# Reliques
# ----------------------------------------------------------------------------------------------
static func new_relic_item(c: Campaign, rid: String) -> Dictionary:
	var iid := "ri%d_%d" % [Time.get_ticks_usec() % 100000, c.rng.randi() % 100000]
	var item := {"iid": iid, "rid": rid, "roll": snappedf(c.rng.randf_range(0.9, 1.15), 0.01), "fav": false}
	c.relic_inv[iid] = item
	return item

static func random_relic_id(c: Campaign, tier: int) -> String:
	# tier 0 : commun…  tier 4 : légendaire
	var weights := {"common": [60, 30, 8, 2, 0], "uncommon": [30, 40, 20, 8, 2], "rare": [10, 30, 40, 15, 5], "epic": [0, 10, 40, 40, 10], "legendary": [0, 0, 10, 50, 40]}
	var kinds := ["common", "uncommon", "rare", "epic", "legendary"]
	var w: Array = [0, 0, 0, 0, 0]
	var tt := clampi(tier, 0, 4)
	for k in kinds.size():
		w[k] = float(weights[["common", "uncommon", "rare", "epic", "legendary"][tt]][k]) if false else 0.0
	var table := [[60, 30, 8, 2, 0], [30, 40, 20, 8, 2], [10, 30, 40, 15, 5], [0, 10, 40, 40, 10], [0, 0, 10, 50, 40]]
	var tw: Array = table[tt]
	var total := 0.0
	for x in tw:
		total += float(x)
	var r := c.rng.randf() * total
	var acc := 0.0
	var pick := 0
	for i in tw.size():
		acc += float(tw[i])
		if r <= acc:
			pick = i
			break
	var pool: Array = []
	for rel in Data.relic_list:
		if rel["rarity"] == kinds[pick]:
			pool.append(rel)
	if pool.is_empty():
		pool = Data.relic_list
	return String(pool[c.rng.randi() % pool.size()]["id"])

static func open_chest(c: Campaign, tier: int) -> Dictionary:
	var reward := {"tier": tier, "gold": 0, "relic": {}}
	if c.rng.randf() < 0.35:
		reward["gold"] = int(120 * (tier + 1) * c.rng.randf_range(0.8, 1.6))
		c.gold += reward["gold"]
	else:
		var rid := random_relic_id(c, tier)
		reward["relic"] = new_relic_item(c, rid)
	return reward

static func sell_relic(c: Campaign, iid: String) -> int:
	var item: Dictionary = c.relic_inv.get(iid, {})
	if item.is_empty():
		return 0
	var r: Dictionary = Data.relics.get(String(item["rid"]), {})
	var price := int(float(r.get("price", 100)) * 0.45)
	for m in c.roster:
		(m["relics"] as Array).erase(iid)
	c.relic_inv.erase(iid)
	c.gold += price
	return price

static func equip_relic(c: Campaign, uid: String, iid: String) -> bool:
	var m := c.merc_by_uid(uid)
	if m.is_empty() or not c.relic_inv.has(iid):
		return false
	for o in c.roster:
		(o["relics"] as Array).erase(iid)
	var slots := MercLogic.relic_slots(m)
	var arr: Array = m["relics"]
	if arr.size() >= slots:
		arr.pop_front()
	arr.append(iid)
	return true

static func unequip_relic(c: Campaign, iid: String) -> void:
	for m in c.roster:
		(m["relics"] as Array).erase(iid)

static func relic_owner(c: Campaign, iid: String) -> String:
	for m in c.roster:
		if iid in m["relics"]:
			return String(m["name"])
	return ""

# ----------------------------------------------------------------------------------------------
# Marché des combattants
# ----------------------------------------------------------------------------------------------
static func scouting_level(c: Campaign) -> int:
	return int(c.facilities.get("scouting_office", 1))

static func refresh_market(c: Campaign, first: bool = false) -> void:
	var fighters: Array = []
	var n := 9 + scouting_level(c) * 2
	var base_lvl := maxi(c.div_level(c.player_div) - 1, 1)
	var shiny_bonus := 0.015 * (1.0 if c.staff.has("shiny_catcher") else 0.0) + 0.0
	var scout_q := 0.008 * (scouting_level(c) - 1) + (0.02 if c.staff.has("scout") else 0.0)
	for i in n:
		var cdef: Dictionary = Data.class_list[c.rng.randi() % Data.class_list.size()]
		var lvl := maxi(base_lvl + c.rng.randi_range(-2, 4), 1)
		var m := MercLogic.generate(cdef["id"], lvl, c.rng, {"shiny_chance": 0.025 + shiny_bonus, "legendary_chance": 0.004 + (0.004 if c.staff.has("legendary_expert") else 0.0), "quality": scout_q, "scouting": true})
		var price := MercLogic.value_of(m)
		if m["shiny"]:
			m["shiny_premium"] = true
		fighters.append({"id": "L%d" % c.rng.randi(), "merc": m, "price": price, "seller": _random_seller(c), "kind": "fighter", "week": c.week})
	# champion nommé rare
	if c.rng.randf() < 0.22 + 0.04 * scouting_level(c):
		var champs: Array = Data.champions
		var ch: Dictionary = champs[c.rng.randi() % champs.size()]
		var m2 := MercLogic.generate(String(ch["id"]), maxi(base_lvl + 5, 8), c.rng, {"scouting": true, "quality": 0.04, "name": String(ch["name"])})
		fighters.append({"id": "L%d" % c.rng.randi(), "merc": m2, "price": int(MercLogic.value_of(m2) * 1.4), "seller": _random_seller(c), "kind": "fighter", "week": c.week, "champion": true})
	# superstar (fièvre des transferts)
	if not first and c.rng.randf() < 0.11:
		var cdef2: Dictionary = Data.class_list[c.rng.randi() % Data.class_list.size()]
		var m3 := MercLogic.generate(cdef2["id"], c.div_level(0) + 3, c.rng, {"quality": 0.05, "scouting": true})
		m3["superstar"] = true
		fighters.append({"id": "L%d" % c.rng.randi(), "merc": m3, "price": MercLogic.value_of(m3), "seller": _random_seller(c), "kind": "fighter", "week": c.week, "superstar": true})
		c._news("FIÈVRE DES TRANSFERTS : %s — alerte superstar ! Tous les regards se tournent vers cette recrue de grande valeur." % String(m3["name"]).to_upper(), "transfer")
	var relics: Array = []
	for i in 8:
		var rid := random_relic_id(c, c.rng.randi() % 3 + (1 if scouting_level(c) >= 3 else 0))
		var def: Dictionary = Data.relics[rid]
		relics.append({"id": "R%d" % c.rng.randi(), "rid": rid, "roll": snappedf(c.rng.randf_range(0.9, 1.15), 0.01), "price": int(def["price"] * (0.9 + c.rng.randf() * 0.2) * (0.9 if c.staff.has("quartermaster") else 1.0)), "kind": "relic"})
	c.market = {"fighters": fighters, "relics": relics}

static func _random_seller(c: Campaign) -> String:
	var ids: Array = c.ai_teams.keys()
	return String(c.ai_teams[ids[c.rng.randi() % ids.size()]]["name"])

static func buy_fighter(c: Campaign, listing_id: String) -> String:
	for i in c.market["fighters"].size():
		var l: Dictionary = c.market["fighters"][i]
		if l["id"] == listing_id:
			if c.gold < l["price"]:
				return "Pas assez d'or."
			if c.roster.size() >= roster_capacity(c):
				return "Effectif complet (améliorez la Maison du club)."
			c.gold -= l["price"]
			var m: Dictionary = l["merc"]
			m["superstar"] = false
			c.roster.append(m)
			c.market["fighters"].remove_at(i)
			c._news("Transfert : %s rejoint le club pour %s or." % [m["name"], Game.format_gold(l["price"])], "transfer")
			return ""
	return "Annonce introuvable."

static func sell_fighter(c: Campaign, uid: String) -> int:
	if c.roster.size() <= 5:
		return -1
	var m := c.merc_by_uid(uid)
	if m.is_empty():
		return -1
	var price := int(MercLogic.value_of(m) * 0.55)
	for iid in m["relics"]:
		pass
	c.roster.erase(m)
	c.lineup.erase(uid)
	c.academy_lineup.erase(uid)
	c.gold += price
	c._news("%s est vendu pour %s or." % [m["name"], Game.format_gold(price)], "transfer")
	if c.lineup.size() < 5:
		c.auto_lineup()
	return price

static func buy_relic(c: Campaign, listing_id: String) -> String:
	for i in c.market["relics"].size():
		var l: Dictionary = c.market["relics"][i]
		if l["id"] == listing_id:
			if c.gold < l["price"]:
				return "Pas assez d'or."
			c.gold -= l["price"]
			var item := new_relic_item(c, String(l["rid"]))
			item["roll"] = l["roll"]
			c.market["relics"].remove_at(i)
			return ""
	return "Annonce introuvable."

static func respec_cost(m: Dictionary) -> int:
	return 150 + 40 * int(m["level"])
