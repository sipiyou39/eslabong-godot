class_name Campaign
extends RefCounted
## État complet d'une campagne : club, effectif, monde (équipes IA, divisions, calendrier), événements de la semaine, sauvegarde.

static var save_path: String = "user://arenabattler_campaign_1.json"
const WEEKS := 29
const DIVISION_COUNT := 4
const TEAMS_PER_DIV := 13
const MATCHDAYS := 24
const SPECIAL_WEEKS := [6, 22]
const ACADEMY_WEEKS := [8, 12, 16, 20, 23]
const TOWER_WEEKS := [6, 15, 27]
const DRAFT_WEEKS := [11, 15, 19]
const DIFFICULTY_NAMES := ["Facile", "Normal", "Difficile", "Cauchemar"]

var version: int = 1
var team_name: String = "Skvell D"
var logo: Dictionary = {"shield": 3, "division": 5, "charge": 17, "base_color": "#1a1a22", "field_color": "#f2ead0", "charge_color": "#c0392b", "division_color": "#2f5ea8"}
var season: int = 1
var week: int = 1
var gold: float = 2000.0
var difficulty: int = 1
var seed_value: int = 1
var roster: Array = []
var lineup: Array = []
var academy_lineup: Array = []
var relic_inv: Dictionary = {}
var facilities: Dictionary = {"club_house": 1, "scouting_office": 1, "barracks": 1, "training_grounds": 1}
var staff: Dictionary = {}
var ai_teams: Dictionary = {}
var divisions: Array = []
var player_div: int = 3
var standings: Dictionary = {}
var fixtures: Array = []
var results_log: Array = []
var news: Array = []
var history: Array = []
var trophies: Array = []
var achievements: Dictionary = {}
var stats: Dictionary = {"kills": 0, "assists": 0, "healing": 0.0, "res": 0, "wins": 0, "losses": 0, "trophies": 0, "damage": 0.0, "iron_gate_best": 0, "tower_best": 0, "seasons": 0}
var market: Dictionary = {"fighters": [], "relics": []}
var chests: Array = []
var cup: Dictionary = {}
var processed: Dictionary = {}
var hall_of_legends: Array = []
var rng := RandomNumberGenerator.new()
var week_done: Dictionary = {}
var tower_floor: int = 0
var draft_run: Dictionary = {}
var player_id: String = "player"

# ----------------------------------------------------------------------------------------------
# Création
# ----------------------------------------------------------------------------------------------
static func create(name: String, logo_recipe: Dictionary, diff: int, starters: Array, seed_val: int = 0) -> Campaign:
	var c := Campaign.new()
	c.team_name = name
	c.logo = logo_recipe
	c.difficulty = diff
	c.seed_value = seed_val if seed_val != 0 else int(Time.get_unix_time_from_system()) % 1000000
	c.rng.seed = c.seed_value
	c.roster = starters
	c.gold = 2000.0 + (0 if diff >= 1 else 800.0)
	c.auto_lineup()
	c.academy_lineup = []
	c._init_world()
	c.refresh_market(true)
	c._news("Votre club « %s » est fondé. Que la gloire vous accompagne !" % name)
	c._unlock("ACH_CLUB_FOUNDED")
	return c

func _init_world() -> void:
	ai_teams.clear()
	var all_ids: Array = []
	var named_pool: Array = []
	var gen_pool: Array = []
	for t in Data.teams:
		if String(t["name"]) == team_name or String(t["id"]) == "gen_skvell_d":
			continue
		if t["named"]:
			named_pool.append(t)
		else:
			gen_pool.append(t)
	var all_teams: Array = named_pool + gen_pool
	all_teams.shuffle()
	var need := DIVISION_COUNT * TEAMS_PER_DIV - 1
	while all_teams.size() < need:
		all_teams.append({"id": "gen_x%d" % all_teams.size(), "name": "Compagnie %s" % NameGen.FIRST[rng.randi() % NameGen.FIRST.size()], "named": false, "lean": "balanced"})
	all_teams = all_teams.slice(0, need)
	divisions = []
	for d in DIVISION_COUNT:
		divisions.append([])
	var idx := 0
	for t in all_teams:
		var d := mini(idx / TEAMS_PER_DIV, DIVISION_COUNT - 1)
		if d == DIVISION_COUNT - 1 and divisions[d].size() >= TEAMS_PER_DIV - 1:
			d = DIVISION_COUNT - 2
		divisions[d].append(t["id"])
		idx += 1
		ai_teams[t["id"]] = {"id": t["id"], "name": t["name"], "lean": t.get("lean", "balanced"), "roster": [], "colors": [rng.randf(), rng.randf()], "logo": _random_logo()}
	player_div = DIVISION_COUNT - 1
	divisions[player_div].append(player_id)
	for d in DIVISION_COUNT:
		for tid in divisions[d]:
			if tid != player_id:
				_gen_ai_roster(tid, d)
	_new_season_setup()

func _random_logo() -> Dictionary:
	var cols := ["#1a1a22", "#f2ead0", "#c0392b", "#2f5ea8", "#c9a227", "#2e7d4f", "#6a2c8a", "#e0e0e8", "#d9731c", "#12121a"]
	return {"shield": rng.randi() % 8, "division": rng.randi() % 16, "charge": rng.randi() % 64, "base_color": cols[rng.randi() % cols.size()], "field_color": cols[rng.randi() % cols.size()],
		"charge_color": cols[rng.randi() % cols.size()], "division_color": cols[rng.randi() % cols.size()]}

func div_level(d: int) -> int:
	return [15, 10, 6, 2][clampi(d, 0, 3)] + [0, 1, 2, 4][clampi(difficulty, 0, 3)] + (season - 1) * 1

func _gen_ai_roster(tid: String, d: int) -> void:
	var t: Dictionary = ai_teams[tid]
	var lean: String = t["lean"]
	var lvl := div_level(d)
	var roles := ["tank", "bruiser", "healer", "ranged", "mage", "assassin", "support", "bruiser"]
	var roster_out: Array = []
	for i in 8:
		var role: String = roles[i]
		if lean != "balanced" and i >= 5 and lean in ["tank", "bruiser", "assassin", "ranged", "mage"]:
			role = lean
		var pool := MatchFactory.classes_by_role(role)
		var cdef: Dictionary = pool[rng.randi() % pool.size()]
		var m := MercLogic.generate(cdef["id"], maxi(lvl + rng.randi_range(-2, 2), 1), rng, {"shiny_chance": 0.01, "legendary_chance": 0.001})
		roster_out.append(m)
	t["roster"] = roster_out

func _new_season_setup() -> void:
	standings.clear()
	for d in divisions.size():
		for tid in divisions[d]:
			standings[tid] = {"w": 0, "l": 0, "pts": 0, "rf": 0, "ra": 0, "p": 0}
	fixtures = []
	for d in divisions.size():
		fixtures.append(_round_robin(divisions[d]))
	cup = {}
	week_done = {}
	results_log = []

## Planning aller-retour par la méthode du cercle ; 26 tours puis troncature à 24
func _round_robin(ids: Array) -> Array:
	var teams: Array = ids.duplicate()
	teams.shuffle()
	if teams.size() % 2 == 1:
		teams.append("BYE")
	var n := teams.size()
	var rounds: Array = []
	var arr: Array = teams.duplicate()
	for r in n - 1:
		var pairs: Array = []
		for i in n / 2:
			var a: String = arr[i]
			var b: String = arr[n - 1 - i]
			if a != "BYE" and b != "BYE":
				pairs.append([a, b] if (r + i) % 2 == 0 else [b, a])
		rounds.append(pairs)
		var last: String = arr.pop_back()
		arr.insert(1, last)
	var all: Array = []
	for r in rounds:
		all.append(r)
	for r in rounds:
		var back: Array = []
		for p in r:
			back.append([p[1], p[0]])
		all.append(back)
	return all.slice(0, MATCHDAYS)

# ----------------------------------------------------------------------------------------------
# Calendrier / événements
# ----------------------------------------------------------------------------------------------
func league_weeks_index() -> int:
	return week - 1

func is_league_week() -> bool:
	return week >= 1 and week <= MATCHDAYS

func team_name_of(tid: String) -> String:
	if tid == player_id:
		return team_name
	return String(ai_teams.get(tid, {}).get("name", tid))

func logo_of(tid: String) -> Dictionary:
	if tid == player_id:
		return logo
	return ai_teams.get(tid, {}).get("logo", logo)

func current_fixture() -> Array:
	if not is_league_week():
		return []
	var md: Array = fixtures[player_div][week - 1]
	for p in md:
		if p[0] == player_id or p[1] == player_id:
			return p
	return []

func opponent_id() -> String:
	var f := current_fixture()
	if f.is_empty():
		return ""
	return f[1] if f[0] == player_id else f[0]

func events_this_week() -> Array:
	var ev: Array = []
	if is_league_week():
		var opp := opponent_id()
		if opp != "":
			ev.append({"id": "league", "kind": "league", "main": true, "label": "Match de ligue", "opp": opp, "done": week_done.has("league")})
		else:
			ev.append({"id": "league_bye", "kind": "bye", "main": true, "label": "Exempt cette semaine", "done": true})
	if week in SPECIAL_WEEKS:
		ev.append({"id": "special", "kind": "special_3v3v3v3", "main": false, "label": "Coupe spéciale 3v3v3v3", "done": week_done.has("special")})
	if week in ACADEMY_WEEKS:
		ev.append({"id": "academy", "kind": "academy", "main": false, "label": "Ligue Académie (3v3)", "done": week_done.has("academy")})
	if week == 25:
		ev.append({"id": "academy_placement", "kind": "academy_placement", "main": false, "label": "Match de placement Académie", "done": week_done.has("academy_placement")})
	if week in TOWER_WEEKS:
		ev.append({"id": "tower", "kind": "tower", "main": false, "label": "Tour du Défi (récompenses saisonnières)", "done": week_done.has("tower")})
	if week in DRAFT_WEEKS:
		ev.append({"id": "draft", "kind": "draft", "main": false, "label": "Coupe Draft (frais d'entrée 400 or)", "done": week_done.has("draft")})
	if week == 26:
		ev.append({"id": "chaos", "kind": "chaos", "main": true, "label": "Coupe Chaos Thunder", "done": week_done.has("chaos")})
	if week >= 27 and week <= 29:
		var stage: String = ["Quarts de finale", "Demi-finales", "Finale"][week - 27]
		var alive := _cup_alive(player_id)
		if week == 27 and cup.is_empty():
			_setup_cup()
			alive = true
		if alive:
			ev.append({"id": "cup", "kind": "cup", "main": true, "label": "Coupe des Champions — " + stage, "opp": _cup_opponent(), "done": week_done.has("cup")})
		else:
			ev.append({"id": "cup_out", "kind": "bye", "main": true, "label": "Éliminé de la Coupe des Champions", "done": true})
	if ev.is_empty() or not _has_main(ev):
		ev.append({"id": "rest", "kind": "bye", "main": true, "label": "Semaine de repos", "done": true})
	return ev

func _has_main(ev: Array) -> bool:
	for e in ev:
		if e["main"]:
			return true
	return false

func main_event_done() -> bool:
	for e in events_this_week():
		if e["main"] and not e["done"]:
			return false
	return true

func week_title() -> String:
	if week <= MATCHDAYS:
		return "Semaine %d — Journée %d" % [week, week]
	if week == 25:
		return "Semaine 25 — Placement Académie"
	if week == 26:
		return "Semaine 26 — Coupe Chaos Thunder"
	return "Semaine %d — Coupe des Champions" % week

# ----------------------------------------------------------------------------------------------
# Coupe des Champions
# ----------------------------------------------------------------------------------------------
func _setup_cup() -> void:
	var picks: Array = []
	for d in divisions.size():
		var sorted := _sorted_standings(d)
		var take: int = [4, 2, 1, 1][d]
		for i in mini(take, sorted.size()):
			if sorted[i] != player_id:
				picks.append(sorted[i])
	picks = picks.slice(0, 7)
	picks.append(player_id)
	picks.shuffle()
	cup = {"round": 0, "teams": picks, "alive": picks.duplicate(), "pairs": [], "winner": ""}
	_cup_make_pairs()
	_news("La Coupe des Champions commence : 8 clubs, un seul trophée !")

func _cup_make_pairs() -> void:
	var a: Array = cup["alive"].duplicate()
	a.shuffle()
	var pairs: Array = []
	# le club du joueur est toujours dans la première paire pour simplifier l'affichage
	if player_id in a:
		a.erase(player_id)
		a.push_front(player_id)
	for i in range(0, a.size() - 1, 2):
		pairs.append([a[i], a[i + 1]])
	cup["pairs"] = pairs

func _cup_alive(tid: String) -> bool:
	return not cup.is_empty() and tid in cup.get("alive", [])

func _cup_opponent() -> String:
	for p in cup.get("pairs", []):
		if p[0] == player_id:
			return p[1]
		if p[1] == player_id:
			return p[0]
	return ""

func _sorted_standings(d: int) -> Array:
	var ids: Array = divisions[d].duplicate()
	ids.sort_custom(func(a, b):
		var sa: Dictionary = standings[a]
		var sb: Dictionary = standings[b]
		if sa["pts"] != sb["pts"]:
			return sa["pts"] > sb["pts"]
		var da: int = int(sa["rf"]) - int(sa["ra"])
		var db: int = int(sb["rf"]) - int(sb["ra"])
		if da != db:
			return da > db
		return String(a) < String(b))
	return ids

func sorted_standings(d: int) -> Array:
	return _sorted_standings(d)

# ----------------------------------------------------------------------------------------------
# Effectif / composition
# ----------------------------------------------------------------------------------------------
func merc_by_uid(uid: String) -> Dictionary:
	for m in roster:
		if m["uid"] == uid:
			return m
	return {}

func auto_lineup() -> void:
	var sorted := roster.duplicate()
	sorted.sort_custom(func(a, b): return MercLogic.rating(a) > MercLogic.rating(b))
	var picks: Array = []
	var healer := false
	for m in sorted:
		if not MercLogic.is_available(m):
			continue
		picks.append(m["uid"])
		if picks.size() >= 5:
			break
	lineup = picks
	for m in roster:
		if m["uid"] in lineup:
			continue

func lineup_mercs() -> Array:
	var out: Array = []
	for uid in lineup:
		var m := merc_by_uid(uid)
		if not m.is_empty():
			out.append(m)
	return out

func bench_mercs() -> Array:
	var out: Array = []
	for m in roster:
		if not (m["uid"] in lineup):
			out.append(m)
	return out

func specs_for(mercs: Array) -> Array:
	var out: Array = []
	for m in mercs:
		out.append(MercLogic.combatant_spec(m, relic_inv))
	return out

func ai_specs(tid: String, n: int = 5) -> Array:
	var t: Dictionary = ai_teams.get(tid, {})
	if t.is_empty():
		return []
	var sorted: Array = (t["roster"] as Array).duplicate()
	sorted.sort_custom(func(a, b): return MercLogic.rating(a) > MercLogic.rating(b))
	var out: Array = []
	var boost := 1.0 + 0.035 * float(difficulty - 1)
	for m in sorted.slice(0, n):
		var sp := MercLogic.combatant_spec(m, {})
		var st: Dictionary = sp["stats"]
		for k in ["hp", "power"]:
			st[k] = float(st[k]) * boost
		out.append(sp)
	return out

func team_rating(specs_or_mercs: Array) -> float:
	var s := 0.0
	var roles := {}
	for m in specs_or_mercs:
		s += MercLogic.rating(m)
		var r: String = String(Data.template(String(m["class_id"])).get("role", ""))
		roles[r] = true
	if roles.has("healer") or roles.has("support"):
		s *= 1.05
	if roles.has("tank"):
		s *= 1.04
	return s

func ai_team_rating(tid: String, n: int = 5) -> float:
	var t: Dictionary = ai_teams.get(tid, {})
	if t.is_empty():
		return 0.0
	var sorted: Array = (t["roster"] as Array).duplicate()
	sorted.sort_custom(func(a, b): return MercLogic.rating(a) > MercLogic.rating(b))
	return team_rating(sorted.slice(0, n)) * (1.0 + 0.035 * float(difficulty - 1))

# ----------------------------------------------------------------------------------------------
# Simulation rapide
# ----------------------------------------------------------------------------------------------
func quick_sim_pair(ra: float, rb: float) -> Dictionary:
	var spread := maxf((ra + rb) * 0.5 * 0.2, 1.0)
	var p := 1.0 / (1.0 + exp(-(ra - rb) / spread))
	var a_wins := rng.randf() < p
	var loser_rounds := 0 if rng.randf() < 0.45 else 1
	return {"a_win": a_wins, "score": [2, loser_rounds] if a_wins else [loser_rounds, 2]}

# ----------------------------------------------------------------------------------------------
# Utilitaires
# ----------------------------------------------------------------------------------------------
func refresh_market(first: bool = false) -> void:
	Market.refresh_market(self, first)

func auto_lineup_if_needed() -> void:
	var valid: Array = []
	for u in lineup:
		if not merc_by_uid(u).is_empty():
			valid.append(u)
	lineup = valid
	if lineup.size() < mini(5, roster.size()):
		auto_lineup()

func _news(t: String, kind: String = "info") -> void:
	news.push_front({"s": season, "w": week, "t": t, "k": kind})
	if news.size() > 120:
		news.resize(120)

func _unlock(id: String) -> bool:
	if achievements.has(id):
		return false
	achievements[id] = {"s": season, "w": week}
	_news("Succès débloqué : %s" % Achievements.name_of(id), "achievement")
	if Engine.get_main_loop() and Game.has_method("achievement_popup"):
		Game.achievement_popup(id)
	return true

func division_name(d: int) -> String:
	return "Division %d" % (d + 1)

func player_position() -> int:
	var s := _sorted_standings(player_div)
	return s.find(player_id) + 1

func is_academy_available() -> bool:
	return roster.size() >= 6

func trophy_count() -> int:
	return trophies.size()

# ----------------------------------------------------------------------------------------------
# Sauvegarde
# ----------------------------------------------------------------------------------------------
func to_dict() -> Dictionary:
	return {"version": version, "team_name": team_name, "logo": logo, "season": season, "week": week, "gold": gold, "difficulty": difficulty, "seed": seed_value,
		"roster": roster, "lineup": lineup, "academy_lineup": academy_lineup, "relic_inv": relic_inv, "facilities": facilities, "staff": staff, "ai_teams": ai_teams,
		"divisions": divisions, "player_div": player_div, "standings": standings, "fixtures": fixtures, "results_log": results_log, "news": news, "history": history,
		"trophies": trophies, "achievements": achievements, "stats": stats, "market": market, "chests": chests, "cup": cup, "hall": hall_of_legends, "week_done": week_done,
		"tower_floor": tower_floor, "saved_at_unix": Time.get_unix_time_from_system(), "saved_at_text": Time.get_datetime_string_from_system(false, true)}

static func from_dict(d: Dictionary) -> Campaign:
	var c := Campaign.new()
	c.team_name = d.get("team_name", "Club")
	c.logo = d.get("logo", c.logo)
	c.season = int(d.get("season", 1))
	c.week = int(d.get("week", 1))
	c.gold = float(d.get("gold", 0))
	c.difficulty = int(d.get("difficulty", 1))
	c.seed_value = int(d.get("seed", 1))
	c.rng.seed = c.seed_value + c.week * 977 + c.season * 31
	c.roster = d.get("roster", [])
	c.lineup = d.get("lineup", [])
	c.academy_lineup = d.get("academy_lineup", [])
	c.relic_inv = d.get("relic_inv", {})
	c.facilities = d.get("facilities", c.facilities)
	c.staff = d.get("staff", {})
	c.ai_teams = d.get("ai_teams", {})
	c.divisions = d.get("divisions", [])
	c.player_div = int(d.get("player_div", 3))
	c.standings = d.get("standings", {})
	c.fixtures = d.get("fixtures", [])
	c.results_log = d.get("results_log", [])
	c.news = d.get("news", [])
	c.history = d.get("history", [])
	c.trophies = d.get("trophies", [])
	c.achievements = d.get("achievements", {})
	c.stats = d.get("stats", c.stats)
	c.market = d.get("market", {"fighters": [], "relics": []})
	c.chests = d.get("chests", [])
	c.cup = d.get("cup", {})
	c.hall_of_legends = d.get("hall", [])
	c.week_done = d.get("week_done", {})
	c.tower_floor = int(d.get("tower_floor", 0))
	return c

func save(path: String = "") -> bool:
	if path == "":
		path = save_path
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(JSON.stringify(to_dict()))
	return true

static func load_from(path: String = "") -> Campaign:
	if path == "":
		path = save_path
	if not FileAccess.file_exists(path):
		return null
	var v: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if v is Dictionary:
		return from_dict(v)
	return null

static func summary_of(path: String = "") -> Dictionary:
	if path == "":
		path = save_path
	if not FileAccess.file_exists(path):
		return {}
	var v: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if v is Dictionary:
		return {"team_name": v.get("team_name", "?"), "season": v.get("season", 1), "week": v.get("week", 1), "gold": v.get("gold", 0), "saved_at_text": v.get("saved_at_text", ""),
			"logo": v.get("logo", {}), "difficulty": v.get("difficulty", 1)}
	return {}
