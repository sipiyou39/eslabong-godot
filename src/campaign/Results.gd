class_name Results
extends RefCounted
## Construction des matchs de campagne, application des résultats, simulation rapide, avancement des semaines et fin de saison.

const ARENAS := ["colosseum", "frost", "forge", "irongate"]

static func _arena_for(c: Campaign, key: String) -> String:
	return ARENAS[absi(hash(key + str(c.season))) % ARENAS.size()]

static func player_team(c: Campaign, n: int = 5, uids: Array = []) -> Dictionary:
	var mercs: Array = []
	if uids.is_empty():
		mercs = c.lineup_mercs().slice(0, n)
	else:
		for u in uids:
			var m := c.merc_by_uid(u)
			if not m.is_empty():
				mercs.append(m)
	return {"name": c.team_name, "fighters": c.specs_for(mercs), "logo": c.logo}

static func ai_team(c: Campaign, tid: String, n: int = 5) -> Dictionary:
	return {"name": c.team_name_of(tid), "fighters": c.ai_specs(tid, n), "logo": c.logo_of(tid), "id": tid}

static func league_config(c: Campaign, event: Dictionary) -> Dictionary:
	var opp: String = event["opp"]
	return {"teams": [player_team(c), ai_team(c, opp)], "arena": _arena_for(c, opp), "rounds_to_win": 2, "player_team": 0, "allow_control": true, "mode": "league",
		"id": event["id"], "music": "music_battle_1"}

static func cup_config(c: Campaign, event: Dictionary) -> Dictionary:
	var opp: String = event["opp"]
	var cfg := league_config(c, event)
	cfg["mode"] = "cup"
	cfg["arena"] = "colosseum"
	cfg["music"] = "music_cup"
	cfg["teams"] = [player_team(c), ai_team(c, opp)]
	return cfg

static func special_config(c: Campaign, event: Dictionary) -> Dictionary:
	var teams: Array = [player_team(c, 3)]
	var ids: Array = (c.divisions[c.player_div] as Array).filter(func(x): return x != c.player_id)
	ids.shuffle()
	for i in 3:
		teams.append(ai_team(c, ids[i], 3))
	return {"teams": teams, "arena": "colosseum", "rounds_to_win": 2, "player_team": 0, "allow_control": true, "mode": "special", "id": "special", "music": "music_cup"}

static func academy_config(c: Campaign, event: Dictionary) -> Dictionary:
	var bench := c.bench_mercs()
	var uids: Array = []
	for m in bench:
		if MercLogic.is_available(m):
			uids.append(m["uid"])
		if uids.size() >= 3:
			break
	var rnd := c.rng
	var specs: Array = c.specs_for(bench.slice(0, 3))
	while specs.size() < 3:
		var fill := MercLogic.generate(Data.class_list[rnd.randi() % Data.class_list.size()]["id"], maxi(c.div_level(3), 2), rnd, {"filler": true})
		specs.append(MercLogic.combatant_spec(fill, {}))
	var opp := ai_team(c, "KanishkaAcademy" if c.ai_teams.has("KanishkaAcademy") else String(c.divisions[c.player_div][0]), 3)
	opp["name"] = "Académie " + String(opp["name"])
	for sp in opp["fighters"]:
		var st: Dictionary = sp["stats"]
		for k in ["hp", "power"]:
			st[k] = float(st[k]) * 0.8
	return {"teams": [{"name": c.team_name + " (Académie)", "fighters": specs, "logo": c.logo}, opp], "arena": "colosseum", "rounds_to_win": 2, "player_team": 0, "allow_control": true,
		"mode": "academy", "id": event["id"], "music": "music_battle_1"}

static func chaos_config(c: Campaign, uid: String) -> Dictionary:
	var m := c.merc_by_uid(uid)
	var teams: Array = [{"name": String(m["name"]), "fighters": [MercLogic.combatant_spec(m, c.relic_inv)], "logo": c.logo}]
	var pool: Array = Data.champions + Data.bosses.slice(0, 6)
	pool.shuffle()
	for i in 7:
		var n: Dictionary = pool[i]
		var lvl := maxi(c.div_level(1) + 4, int(m["level"]))
		var cm := MercLogic.generate(String(n["id"]), lvl, c.rng, {"name": String(n["name"])})
		var sp := MercLogic.combatant_spec(cm, {})
		teams.append({"name": String(n["name"]), "fighters": [sp], "logo": c._random_logo()})
	return {"teams": teams, "arena": "thunder", "rounds_to_win": 1, "player_team": 0, "allow_control": true, "mode": "chaos", "ffa": true, "time_limit": 120.0, "storm_start": 45.0,
		"id": "chaos", "music": "music_chaos_thunder"}

static func tower_config(c: Campaign, floor_n: int) -> Dictionary:
	var rnd := RandomNumberGenerator.new()
	rnd.seed = c.seed_value + floor_n * 7919 + c.season
	var lvl := c.div_level(c.player_div) + floor_n * 2
	var t := MatchFactory.random_team("Défi de l'étage %d" % floor_n, 5, lvl, rnd)
	for sp in t["fighters"]:
		var st: Dictionary = Data.template(String(sp["template_id"]))
		sp["stats"] = {}
	var cfg := {"teams": [player_team(c), t], "arena": "frost", "rounds_to_win": 1, "player_team": 0, "allow_control": true, "mode": "tower", "id": "tower", "music": "music_battle_2"}
	cfg["floor"] = floor_n
	return cfg

static func irongate_config(c: Campaign, floor_n: int) -> Dictionary:
	var rnd := RandomNumberGenerator.new()
	rnd.seed = c.seed_value + floor_n * 3571
	var lvl := maxi(c.div_level(c.player_div), 3) + floor_n * 2
	var pool := ["Merc_Orc_Warrior", "Merc_Orc_Berserker", "Merc_Archer_Goblin", "Merc_Goblin_Ambusher", "Merc_Orc_Shaman", "Merc_Minotaur_Bullbreaker", "Merc_Werewolf", "Merc_Warrior_Barbarian"]
	var fighters: Array = []
	var n := mini(3 + floor_n / 2, 7)
	var boss_floor := floor_n % 5 == 0
	if boss_floor:
		var tpl := Data.template("Merc_Hellforged").duplicate(true)
		tpl["display_name"] = "Poroxi" if floor_n == 5 else "Poroxi Déchaîné"
		tpl["scale"] = 1.55
		tpl["kind"] = "boss"
		tpl["aura"] = "#ff5a1c"
		var bm := MercLogic.generate("Merc_Hellforged", lvl + 4, rnd, {"name": String(tpl["display_name"])})
		var sp := MercLogic.combatant_spec(bm, {})
		sp["tpl"] = tpl
		var st: Dictionary = sp["stats"]
		st["hp"] = float(st["hp"]) * 4.0
		st["power"] = float(st["power"]) * 1.4
		fighters.append(sp)
		n = 3
	for i in n:
		var cid: String = pool[rnd.randi() % pool.size()]
		var m := MercLogic.generate(cid, lvl + rnd.randi_range(-1, 1), rnd)
		fighters.append(MercLogic.combatant_spec(m, {}))
	return {"teams": [player_team(c), {"name": "Horde de la Porte" if not boss_floor else "Poroxi & sa garde", "fighters": fighters}], "arena": "irongate", "rounds_to_win": 1, "player_team": 0,
		"allow_control": true, "mode": "irongate", "id": "irongate", "floor": floor_n, "time_limit": 120.0, "storm_start": 80.0, "music": "music_battle_boss" if boss_floor else "music_battle_2"}

# ----------------------------------------------------------------------------------------------
# Simulation rapide d'un événement du joueur
# ----------------------------------------------------------------------------------------------
static func quick_sim_event(c: Campaign, cfg: Dictionary) -> Dictionary:
	var teams: Array = cfg["teams"]
	var ratings: Array = []
	for t in teams:
		var s := 0.0
		for sp in t["fighters"]:
			var st: Dictionary = sp["stats"]
			if st.is_empty():
				st = {"hp": 500, "power": 30, "defense": 10, "mres": 10, "speed": 6.0}
			s += float(st["hp"]) * 0.05 + float(st["power"]) * 1.5 + float(st["defense"]) * 0.9 + float(st["mres"]) * 0.35 + float(st["speed"]) * 3.5 + float(sp["level"]) * 0.6
		ratings.append(s)
	var n := teams.size()
	var score: Array = []
	for i in n:
		score.append(0.0)
	var rtw := int(cfg.get("rounds_to_win", 2))
	var wins: Array = []
	for i in n:
		wins.append(0)
	var guard := 0
	while guard < 12:
		guard += 1
		var best := 0
		var bv := -1.0
		for i in n:
			var v := float(ratings[i]) * c.rng.randf_range(0.7, 1.3)
			if v > bv:
				bv = v
				best = i
		wins[best] += 1
		if wins[best] >= rtw:
			break
	var winner := 0
	var bw := -1
	for i in n:
		if wins[i] > bw:
			bw = wins[i]
			winner = i
	var res_teams: Array = []
	for ti in n:
		var arr: Array = []
		var won: bool = ti == winner
		for sp in teams[ti]["fighters"]:
			var role: String = String(sp["tpl"].get("role", "bruiser"))
			var kills := c.rng.randi_range(0, 3 if won else 2)
			var dmg := float(sp["stats"].get("power", 30)) * c.rng.randf_range(12.0, 26.0) * (1.0 if won else 0.75)
			var heal := 0.0
			if role in ["healer", "support"]:
				heal = c.rng.randf_range(500.0, 1500.0)
				dmg *= 0.3
			arr.append({"uid": sp["uid"], "name": sp["name"], "template": String(sp["template_id"]), "class_name": String(sp["tpl"].get("name", "")), "alive": won and c.rng.randf() < 0.6, "hp_pct": 0.3,
				"level": sp["level"], "stats": {"damage": dmg, "taken": dmg * c.rng.randf_range(0.7, 1.3), "healing": heal, "kills": kills, "assists": c.rng.randi_range(0, 3), "deaths": c.rng.randi_range(0, 2), "res": 0, "blocked": 0.0}})
		res_teams.append({"name": teams[ti]["name"], "fighters": arr})
	return {"winner": winner, "wins": wins, "teams": res_teams, "rounds": wins.reduce(func(a, b): return a + b, 0), "mode": cfg.get("mode", "league"), "simulated": true}

# ----------------------------------------------------------------------------------------------
# Application des résultats
# ----------------------------------------------------------------------------------------------
static func _reward_gold(c: Campaign, kind: String, won: bool, extra: Dictionary) -> int:
	var d := c.player_div
	match kind:
		"league": return (260 + 130 * (3 - d)) if won else 70
		"special":
			var pl: int = int(extra.get("placement", 4))
			return [900, 400, 200, 80][clampi(pl - 1, 0, 3)]
		"academy": return 160 if won else 50
		"academy_placement": return 400 if won else 100
		"cup":
			var rd := int(c.cup.get("round", 0))
			return ([700, 1500, 4000][clampi(rd, 0, 2)]) if won else 120
		"chaos":
			var pl2: int = int(extra.get("placement", 8))
			return [5000, 2200, 1200, 700, 400, 250, 150, 100][clampi(pl2 - 1, 0, 7)]
		"tower": return 120 * int(extra.get("floor", 1)) if won else 60
		"irongate": return 140 * int(extra.get("floor", 1)) if won else 0
	return 0

## Applique les statistiques d'un résultat aux mercenaires du joueur. Renvoie le rapport affichable.
static func finish_event(c: Campaign, event: Dictionary, result: Dictionary, cfg: Dictionary, played_uids: Array = []) -> Dictionary:
	var kind: String = String(event.get("kind", "league"))
	if kind == "special_3v3v3v3":
		kind = "special"
	var won: bool = int(result.get("winner", 1)) == 0 and not bool(result.get("forfeit", false))
	var mine: Array = []
	if result.get("teams", []).size() > 0:
		mine = result["teams"][0]["fighters"]
	var report := {"kind": kind, "won": won, "gold": 0, "fighters": [], "chest": {}, "news": [], "mvp": "", "result": result, "event": event}
	var wins: Array = result.get("wins", [0, 0])
	var rounds_won := int(wins[0]) if wins.size() > 0 else 0
	var rounds_lost := 0
	for i in range(1, wins.size()):
		rounds_lost += int(wins[i])
	var barracks := 1.0 + 0.08 * float(int(c.facilities.get("barracks", 1)) - 1) + (0.1 if c.staff.has("coach") else 0.0)
	var medic := 1.0 - (0.25 if c.staff.has("medic") else 0.0)
	var best_score := -1.0
	var best_uid := ""
	var casualties := 0
	var team_effort := true
	var ace := false
	var medic_flag := false
	var placement := 1
	if result.get("wins", []).size() > 2:
		var sorted := []
		for i in wins.size():
			sorted.append([i, int(wins[i])])
		sorted.sort_custom(func(a, b): return a[1] > b[1])
		for i in sorted.size():
			if sorted[i][0] == 0:
				placement = i + 1
	if kind == "chaos":
		placement = 1 if won else 1 + int(c.rng.randi_range(1, 7)) if int(result.get("winner", 1)) != 0 else 1
		if bool(result.get("forfeit", false)):
			placement = 8
	for fi in mine:
		var m := c.merc_by_uid(String(fi["uid"]))
		var s: Dictionary = fi["stats"]
		if int(s["deaths"]) > 0:
			casualties += 1
		if int(s["kills"]) < 1 and int(s["assists"]) < 1:
			team_effort = false
		if int(s["kills"]) >= 4:
			ace = true
		if float(s["healing"]) >= 1500.0:
			medic_flag = true
		var score := float(s["damage"]) * 0.01 + float(s["kills"]) * 3.0 + float(s["assists"]) + float(s["healing"]) * 0.012 + float(s["res"]) * 4.0
		if score > best_score:
			best_score = score
			best_uid = String(fi["uid"])
		if m.is_empty():
			continue
		var cr: Dictionary = m["career"]
		cr["kills"] = int(cr["kills"]) + int(s["kills"])
		cr["assists"] = int(cr["assists"]) + int(s["assists"])
		cr["healing"] = float(cr["healing"]) + float(s["healing"])
		cr["res"] = int(cr["res"]) + int(s["res"])
		cr["damage"] = float(cr["damage"]) + float(s["damage"])
		cr["taken"] = float(cr["taken"]) + float(s["taken"])
		cr["battles"] = int(cr["battles"]) + 1
		if won:
			cr["wins"] = int(cr["wins"]) + 1
		c.stats["kills"] = int(c.stats["kills"]) + int(s["kills"])
		c.stats["assists"] = int(c.stats["assists"]) + int(s["assists"])
		c.stats["healing"] = float(c.stats["healing"]) + float(s["healing"])
		c.stats["res"] = int(c.stats["res"]) + int(s["res"])
		c.stats["damage"] = float(c.stats["damage"]) + float(s["damage"])
	if won:
		c.stats["wins"] = int(c.stats["wins"]) + 1
	else:
		c.stats["losses"] = int(c.stats["losses"]) + 1
	# XP / niveaux / blessures
	var pool_uids: Array = []
	for fi in mine:
		pool_uids.append(String(fi["uid"]))
	for fi in mine:
		var m2 := c.merc_by_uid(String(fi["uid"]))
		if m2.is_empty():
			continue
		var s2: Dictionary = fi["stats"]
		var xp := 45 + (35 if won else 0) + int(s2["kills"]) * 9 + int(s2["assists"]) * 4 + int(float(s2["healing"]) / 70.0) + int(float(s2["damage"]) / 220.0) + int(s2["res"]) * 10
		if String(fi["uid"]) == best_uid:
			xp += 20
			m2["career"]["mvp"] = int(m2["career"]["mvp"]) + 1
		if kind == "academy" or kind == "academy_placement":
			xp = int(xp * 1.3)
		var before := int(m2["level"])
		var lv := MercLogic.add_xp(m2, xp, c.rng, barracks)
		var f_row := {"uid": m2["uid"], "name": m2["name"], "xp": int(xp * barracks), "levels": lv, "level": m2["level"], "injury": "", "medals": [], "mvp": String(fi["uid"]) == best_uid, "class_id": m2["class_id"],
			"kills": int(s2["kills"]), "assists": int(s2["assists"]), "damage": int(s2["damage"]), "healing": int(s2["healing"])}
		# forme
		if Settings.gb("fighter_form_enabled"):
			var delta := (1 if won else -1) + (1 if String(fi["uid"]) == best_uid else 0)
			m2["form"] = clampi(int(m2["form"]) + delta, -4, 4)
		# blessures
		if kind != "chaos" and bool(fi.get("alive", true)) == false:
			if MercLogic.roll_injury(m2, c.rng, medic):
				f_row["injury"] = String(m2["injury"]["desc"])
				c._news("%s est blessé (%s) pour %d match(s)." % [m2["name"], m2["injury"]["desc"], int(m2["injury"]["battles"])], "injury")
		if won and rounds_lost == 0 and false:
			pass
		f_row["medals"] = MercLogic.update_medals(m2)
		if won and mine.size() > 0 and int(s2["deaths"]) == 0 and casualties == mine.size() - 1 and mine.size() >= 3:
			m2["career"]["clutch"] = int(m2["career"]["clutch"]) + 1
		(report["fighters"] as Array).append(f_row)
		# évènement : l'XP du banc
	for m3 in c.roster:
		if not (String(m3["uid"]) in pool_uids) and kind in ["league", "cup", "special"]:
			var bench_xp := int(32.0 * barracks * (1.0 + (0.35 if c.staff.has("coach") else 0.0)))
			var lvb := MercLogic.add_xp(m3, bench_xp, c.rng, 1.0)
			(report["fighters"] as Array).append({"uid": m3["uid"], "name": m3["name"], "xp": bench_xp, "levels": lvb, "level": m3["level"], "injury": "", "medals": [], "mvp": false, "bench": true, "class_id": m3["class_id"]})
			MercLogic.tick_injury(m3)
	for m4 in c.roster:
		if String(m4["uid"]) in pool_uids:
			MercLogic.tick_injury(m4)
	report["mvp"] = best_uid
	# or
	var gold := _reward_gold(c, kind, won, {"placement": placement, "floor": int(cfg.get("floor", 1))})
	gold = int(gold * [0.85, 1.0, 1.15, 1.35][clampi(c.difficulty, 0, 3)])
	c.gold += gold
	report["gold"] = gold
	report["placement"] = placement
	# coffre
	var chest_chance := 0.25
	var tier := 0
	match kind:
		"cup", "chaos": chest_chance = 1.0 if won else 0.4; tier = 3 if won else 1
		"tower": chest_chance = 0.5; tier = 1 + int(cfg.get("floor", 1)) / 3
		"irongate": chest_chance = 0.45; tier = 1 + int(cfg.get("floor", 1)) / 3
		"special": chest_chance = 0.6 if placement <= 2 else 0.2; tier = 2
		"league": tier = 0 if c.player_div > 1 else 1
	if won and c.rng.randf() < chest_chance or (kind in ["cup", "chaos"] and c.rng.randf() < chest_chance):
		report["chest"] = Market.open_chest(c, tier)
	# classement / coupes
	match kind:
		"league":
			var opp: String = String(event["opp"])
			_record_league(c, c.player_id, opp, [rounds_won, rounds_lost] if true else [])
			c.week_done["league"] = true
		"special":
			c.week_done["special"] = true
			if placement == 1:
				c.trophies.append({"name": "Coupe spéciale 3v3v3v3", "s": c.season, "w": c.week})
				c.stats["trophies"] = int(c.stats["trophies"]) + 1
				c._unlock("ACH_CUP_CHAMPION")
		"academy":
			c.week_done["academy"] = true
		"academy_placement":
			c.week_done["academy_placement"] = true
		"cup":
			c.week_done["cup"] = true
			_cup_record(c, won)
		"chaos":
			c.week_done["chaos"] = true
			if won or placement == 1:
				c.trophies.append({"name": "Coupe Chaos Thunder", "s": c.season, "w": c.week})
				c.stats["trophies"] = int(c.stats["trophies"]) + 1
				c._unlock("ACH_CHAOS_THUNDER_CUP")
				c._unlock("ACH_CUP_CHAMPION")
		"tower":
			c.week_done["tower"] = true
			if won:
				c.tower_floor = maxi(c.tower_floor, int(cfg.get("floor", 1)))
				c.stats["tower_best"] = maxi(int(c.stats["tower_best"]), int(cfg.get("floor", 1)))
		"irongate":
			if won:
				var fl := int(cfg.get("floor", 1))
				c.stats["iron_gate_best"] = maxi(int(c.stats["iron_gate_best"]), fl)
				if fl >= 5:
					c._unlock("ACH_IRON_GATE_FIVE")
				if fl >= 5 and fl % 5 == 0:
					c._unlock("ACH_IRON_GATE_BOSS_POROXI")
	var mvp_ours := best_uid != "" and not c.merc_by_uid(best_uid).is_empty() and best_score >= 0.0
	Achievements.check_match(c, {"won": won, "rounds_won": rounds_won, "rounds_lost": rounds_lost, "first_round_lost": won and rounds_lost > 0 and int(wins[0]) == rounds_won and rounds_lost >= 1 and rounds_won >= 2,
		"no_casualties": casualties == 0, "mvp_is_ours": mvp_ours and won, "ace": ace, "team_effort": team_effort and won, "field_medic": medic_flag})
	if c.trophies.size() >= 5:
		c._unlock("ACH_TROPHIES_5")
	var w_txt := "Victoire" if won else "Défaite"
	c.results_log.push_front({"s": c.season, "w": c.week, "kind": kind, "won": won, "score": [rounds_won, rounds_lost], "opp": String(event.get("opp", "")), "gold": gold})
	c._news("%s — %s%s (%d-%d), +%s or." % [w_txt, String(event.get("label", kind)), (" contre " + c.team_name_of(String(event["opp"]))) if event.has("opp") else "", rounds_won, rounds_lost, Game.format_gold(gold)], "match")
	return report

static func _record_league(c: Campaign, a: String, b: String, score: Array) -> void:
	var sa: Dictionary = c.standings[a]
	var sb: Dictionary = c.standings[b]
	sa["p"] += 1
	sb["p"] += 1
	sa["rf"] += int(score[0])
	sa["ra"] += int(score[1])
	sb["rf"] += int(score[1])
	sb["ra"] += int(score[0])
	if int(score[0]) > int(score[1]):
		sa["w"] += 1
		sa["pts"] += 3
		sb["l"] += 1
	else:
		sb["w"] += 1
		sb["pts"] += 3
		sa["l"] += 1

static func _cup_record(c: Campaign, won: bool) -> void:
	var opp := c._cup_opponent()
	if opp == "":
		return
	var loser := opp if won else c.player_id
	c.cup["alive"].erase(loser)

static func resolve_ai_cup(c: Campaign) -> void:
	if c.cup.is_empty():
		return
	var winners: Array = []
	for p in c.cup["pairs"]:
		var a: String = p[0]
		var b: String = p[1]
		if a == c.player_id or b == c.player_id:
			if not (a in c.cup["alive"]) or not (b in c.cup["alive"]):
				winners.append(a if a in c.cup["alive"] else b)
			else:
				winners.append(a if a != c.player_id else a)   # le joueur n'a pas joué : simulation
				var ra := c.ai_team_rating(a) if a != c.player_id else c.team_rating(c.lineup_mercs())
				var rb := c.ai_team_rating(b) if b != c.player_id else c.team_rating(c.lineup_mercs())
				var r := c.quick_sim_pair(ra, rb)
				var win := a if r["a_win"] else b
				winners.pop_back()
				winners.append(win)
				c.cup["alive"].erase(b if win == a else a)
			continue
		var r2 := c.quick_sim_pair(c.ai_team_rating(a), c.ai_team_rating(b))
		var w := a if r2["a_win"] else b
		winners.append(w)
		c.cup["alive"].erase(b if w == a else a)
	c.cup["round"] = int(c.cup["round"]) + 1
	if winners.size() == 1:
		c.cup["winner"] = winners[0]
		if winners[0] == c.player_id:
			c.trophies.append({"name": "Coupe des Champions", "s": c.season, "w": c.week})
			c.stats["trophies"] = int(c.stats["trophies"]) + 1
			c._unlock("ACH_CHAMPIONS_CUP")
			c._unlock("ACH_CUP_CHAMPION")
			c._news("🏆 %s remporte la Coupe des Champions !" % c.team_name, "trophy")
			c.hall_of_legends.append({"s": c.season, "t": "Coupe des Champions", "who": c.team_name})
		else:
			c._news("%s remporte la Coupe des Champions." % c.team_name_of(winners[0]), "info")
			c.hall_of_legends.append({"s": c.season, "t": "Coupe des Champions", "who": c.team_name_of(winners[0])})
	else:
		c.cup["alive"] = winners
		c._cup_make_pairs()

# ----------------------------------------------------------------------------------------------
# Avancement
# ----------------------------------------------------------------------------------------------
static func resolve_ai_week(c: Campaign) -> void:
	if c.is_league_week():
		for d in c.divisions.size():
			var md: Array = c.fixtures[d][c.week - 1]
			for p in md:
				var a: String = p[0]
				var b: String = p[1]
				if a == c.player_id or b == c.player_id:
					if c.week_done.has("league"):
						continue
					# match du joueur non joué manuellement → simulation
					var ra := c.team_rating(c.lineup_mercs()) if a == c.player_id else c.ai_team_rating(a)
					var rb := c.team_rating(c.lineup_mercs()) if b == c.player_id else c.ai_team_rating(b)
					var rs := c.quick_sim_pair(ra, rb)
					_record_league(c, a, b, rs["score"])
					continue
				var r := c.quick_sim_pair(c.ai_team_rating(a), c.ai_team_rating(b))
				_record_league(c, a, b, r["score"])
	if c.week >= 27 and c.week <= 29:
		resolve_ai_cup(c)

static func advance_week(c: Campaign) -> Array:
	var msgs: Array = []
	resolve_ai_week(c)
	var income := Market.weekly_income(c)
	var costs := Market.weekly_costs(c)
	c.gold += income - costs
	msgs.append("Sponsors : +%s or • Salaires & personnel : -%s or" % [Game.format_gold(income), Game.format_gold(costs)])
	# blessures et récupération hebdomadaires pour ceux qui n'ont pas joué
	for m in c.roster:
		if not m["injury"].is_empty() and c.rng.randf() < 0.25 + (0.2 if c.staff.has("medic") else 0.0):
			MercLogic.tick_injury(m)
	# l'IA progresse
	if c.week % 4 == 0:
		for tid in c.ai_teams:
			var t: Dictionary = c.ai_teams[tid]
			for m in t["roster"]:
				if c.rng.randf() < 0.35:
					MercLogic.add_xp(m, MercLogic.xp_needed(int(m["level"])), c.rng, 1.0)
					MercLogic.auto_pick_stat(m, c.rng)
	_ai_market_news(c)
	c.week += 1
	c.week_done = {}
	if c.week > Campaign.WEEKS:
		msgs.append_array(end_season(c))
	else:
		Market.refresh_market(c)
		c.auto_lineup_if_needed()
	c.save()
	return msgs

static func _ai_market_news(c: Campaign) -> void:
	if c.rng.randf() < 0.6:
		var ids: Array = c.ai_teams.keys()
		var a: String = ids[c.rng.randi() % ids.size()]
		var b: String = ids[c.rng.randi() % ids.size()]
		if a != b:
			var nm := NameGen.random_name(c.rng, 0.5)
			var price := c.rng.randi_range(300, 4200)
			c._news("Semaine %d : %s a acheté %s chez %s pour %dg" % [c.week, c.ai_teams[a]["name"], nm, c.ai_teams[b]["name"], price], "market")

static func end_season(c: Campaign) -> Array:
	var msgs: Array = []
	c.stats["seasons"] = int(c.stats["seasons"]) + 1
	c._unlock("ACH_FIRST_SEASON_COMPLETE")
	var rec := {"season": c.season, "player_div": c.player_div, "rank": 0, "champions": [], "trophies": c.trophies.size()}
	var new_divs: Array = []
	var ranks: Array = []
	for d in c.divisions.size():
		ranks.append(c.sorted_standings(d))
	var champion_of_d0: String = ranks[0][0]
	rec["rank"] = ranks[c.player_div].find(c.player_id) + 1
	rec["champions"] = [c.team_name_of(champion_of_d0)]
	c.hall_of_legends.append({"s": c.season, "t": "Champion de Division 1", "who": c.team_name_of(champion_of_d0)})
	var prize: int = [5500, 2800, 1500, 800][c.player_div]
	if int(rec["rank"]) == 1:
		c._unlock("ACH_LEAGUE_CHAMPION")
		c.trophies.append({"name": "Champion de %s" % c.division_name(c.player_div), "s": c.season, "w": c.week})
		c.stats["trophies"] = int(c.stats["trophies"]) + 1
		c.gold += prize
		msgs.append("🏆 Champion de %s ! Prime de %s or." % [c.division_name(c.player_div), Game.format_gold(prize)])
		c._news("🏆 Vous remportez la %s !" % c.division_name(c.player_div), "trophy")
	elif int(rec["rank"]) <= 3:
		c.gold += prize / 3
		msgs.append("Podium en %s : prime de %s or." % [c.division_name(c.player_div), Game.format_gold(prize / 3)])
	# promotions / relégations
	var old_div := c.player_div
	var up := 2
	var movers_up: Array = []
	var movers_dn: Array = []
	for d in c.divisions.size():
		movers_up.append([])
		movers_dn.append([])
	for d in c.divisions.size():
		var r: Array = ranks[d]
		if d > 0:
			movers_up[d] = r.slice(0, up)
		if d < c.divisions.size() - 1:
			movers_dn[d] = r.slice(r.size() - up, r.size())
	var nd: Array = []
	for d in c.divisions.size():
		nd.append(c.divisions[d].duplicate())
	for d in c.divisions.size():
		for t in movers_up[d]:
			nd[d].erase(t)
			nd[d - 1].append(t)
		for t in movers_dn[d]:
			nd[d].erase(t)
			nd[d + 1].append(t)
	c.divisions = nd
	for d in c.divisions.size():
		if c.player_id in c.divisions[d]:
			c.player_div = d
	if c.player_div < old_div:
		c._unlock("ACH_PROMOTION_DAY")
		msgs.append("📈 Promotion en %s !" % c.division_name(c.player_div))
		c._news("Promotion en %s !" % c.division_name(c.player_div), "promotion")
	elif c.player_div > old_div:
		msgs.append("📉 Relégation en %s." % c.division_name(c.player_div))
		c._news("Relégation en %s." % c.division_name(c.player_div), "info")
	c.history.append(rec)
	# vieillissement et nouvelle saison
	for m in c.roster:
		m["age"] = int(m["age"]) + 1
		m["salary"] = MercLogic.salary_for(m)
		if int(m["level"]) >= 30 or m.get("legendary", false):
			if not _in_hall(c, String(m["uid"])):
				c.hall_of_legends.append({"s": c.season, "t": "Combattant légendaire", "who": String(m["name"]), "uid": m["uid"], "level": m["level"]})
	for tid in c.ai_teams:
		for m in c.ai_teams[tid]["roster"]:
			m["age"] = int(m["age"]) + 1
	# régénère les équipes d'IA selon leur nouvelle division
	for d in c.divisions.size():
		for tid in c.divisions[d]:
			if tid != c.player_id:
				c._gen_ai_roster(tid, d)
	c.season += 1
	c.week = 1
	c._new_season_setup()
	Market.refresh_market(c, true)
	c._news("Saison %d : nouvelle saison en %s." % [c.season, c.division_name(c.player_div)], "season")
	msgs.append("Nouvelle saison : %d" % c.season)
	return msgs

static func _in_hall(c: Campaign, uid: String) -> bool:
	for h in c.hall_of_legends:
		if h.get("uid", "") == uid:
			return true
	return false
