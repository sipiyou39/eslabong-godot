class_name DraftSeries
extends RefCounted
## Enchaînement des 3 matchs de la Coupe Draft (équipe composée de combattants draftés, hors effectif).

static func start_match(c: Campaign, ev: Dictionary) -> void:
	var run: Dictionary = c.draft_run
	var idx := int(run["match"])
	var rnd := RandomNumberGenerator.new()
	rnd.seed = c.seed_value + c.week * 131 + idx * 17 + c.season
	var lvl: int = int(run["level"]) + idx
	var opp := MatchFactory.random_team(["Quart de finale", "Demi-finale", "Finale"][idx] + " — Draft", 5, lvl, rnd)
	var mine: Array = []
	for m in run["picks"]:
		mine.append(MercLogic.combatant_spec(m, {}))
	var cfg := {"teams": [{"name": c.team_name + " (Draft)", "fighters": mine, "logo": c.logo}, opp], "arena": "colosseum", "rounds_to_win": 2, "player_team": 0, "allow_control": true,
		"mode": "draft", "music": "music_draft", "auto_control": true}
	cfg["on_finish"] = Callable(DraftSeries, "after_match").bind(c, ev)
	Game.start_battle(cfg)

static func after_match(res: Dictionary, c: Campaign, ev: Dictionary) -> void:
	var run: Dictionary = c.draft_run
	var won: bool = int(res.get("winner", 1)) == 0 and not bool(res.get("forfeit", false))
	if won:
		run["wins"] = int(run["wins"]) + 1
		run["match"] = int(run["match"]) + 1
	if won and int(run["match"]) < 3:
		start_match(c, ev)
		return
	_finish(c, ev)

static func _finish(c: Campaign, ev: Dictionary) -> void:
	var wins := int(c.draft_run["wins"])
	var gold: int = [100, 450, 1000, 2400][clampi(wins, 0, 3)]
	gold = int(gold * [0.85, 1.0, 1.15, 1.35][clampi(c.difficulty, 0, 3)])
	c.gold += gold
	var rep := {"kind": "draft", "won": wins >= 2, "gold": gold, "fighters": [], "chest": {}, "news": [], "mvp": "", "result": {"wins": [wins, 3 - wins]}, "event": {"label": "Coupe Draft — %d victoire(s)" % wins, "kind": "draft"}, "placement": 4 - wins}
	if wins >= 1:
		rep["chest"] = Market.open_chest(c, wins)
	if wins >= 3:
		c.trophies.append({"name": "Coupe Draft", "s": c.season, "w": c.week})
		c.stats["trophies"] = int(c.stats["trophies"]) + 1
		c._unlock("ACH_CUP_CHAMPION")
		c._news("🏆 Vous remportez la Coupe Draft !", "trophy")
	if c.trophies.size() >= 5:
		c._unlock("ACH_TROPHIES_5")
	c.week_done["draft"] = true
	c._news("Coupe Draft terminée : %d victoire(s), +%s or." % [wins, Game.format_gold(gold)], "match")
	c.draft_run = {}
	c.save()
	Game.pending_report = rep
	Game.goto_hub()
