class_name Achievements
extends RefCounted
## Succès (mêmes identifiants que la version Steam d'origine).

const LIST := {
	"ACH_CLUB_FOUNDED": ["Club fondé", "Créer votre club de mercenaires."],
	"ACH_FIRST_WIN": ["Première victoire", "Gagner un match."],
	"ACH_TEN_WINS": ["Dix victoires", "Gagner 10 matchs."],
	"ACH_HUNDRED_KILLS": ["Centurion", "Éliminer 100 ennemis."],
	"ACH_KILLS_25": ["Chasseur", "Éliminer 25 ennemis."],
	"ACH_ASSISTS_100": ["Passeur d'élite", "Réaliser 100 assistances."],
	"ACH_GOLD_MVP": ["MVP en or", "Être désigné meilleur joueur d'un match."],
	"ACH_CLEAN_SWEEP": ["Balayage", "Gagner un match sur le score de 2 manches à 0."],
	"ACH_LEAGUE_CHAMPION": ["Champion de ligue", "Terminer premier de votre division."],
	"ACH_CUP_CHAMPION": ["Champion de coupe", "Remporter une coupe."],
	"ACH_CHAOS_THUNDER_CUP": ["Maître de la foudre", "Gagner la Coupe Chaos Thunder."],
	"ACH_CHAMPIONS_CUP": ["Roi des champions", "Gagner la Coupe des Champions."],
	"ACH_TROPHIES_5": ["Vitrine garnie", "Remporter 5 trophées."],
	"ACH_IRON_GATE_FIVE": ["Gardien de la porte", "Atteindre l'étage 5 de Defend the Iron Gate."],
	"ACH_IRON_GATE_BOSS_POROXI": ["Chasseur de Poroxi", "Vaincre le boss Poroxi."],
	"ACH_NO_CASUALTIES": ["Sans pertes", "Gagner un match sans qu'aucun combattant ne tombe."],
	"ACH_SECOND_WIND": ["Second souffle", "Gagner un match après avoir perdu la première manche."],
	"ACH_ACE": ["As", "Éliminer 4 ennemis avec un seul combattant dans un match."],
	"ACH_TEAM_EFFORT": ["Effort d'équipe", "Tous vos combattants participent à une élimination."],
	"ACH_FIELD_MEDIC": ["Médecin de terrain", "Soigner 1 500 PV dans un match avec un combattant."],
	"ACH_FIRST_SEASON_COMPLETE": ["Première saison", "Terminer une saison."],
	"ACH_PROMOTION_DAY": ["Jour de promotion", "Être promu dans la division supérieure."],
}

static func name_of(id: String) -> String:
	return LIST.get(id, [id, ""])[0]

static func desc_of(id: String) -> String:
	return LIST.get(id, [id, ""])[1]

## Évalué après chaque match du joueur. ctx : {won, rounds_won, rounds_lost, result, lineup_ids, first_round_lost}
static func check_match(c: Campaign, ctx: Dictionary) -> void:
	var won: bool = ctx.get("won", false)
	if won:
		c._unlock("ACH_FIRST_WIN")
		if int(c.stats["wins"]) >= 10:
			c._unlock("ACH_TEN_WINS")
		if int(ctx.get("rounds_lost", 1)) == 0 and int(ctx.get("rounds_won", 0)) >= 2:
			c._unlock("ACH_CLEAN_SWEEP")
		if ctx.get("first_round_lost", false):
			c._unlock("ACH_SECOND_WIND")
		if ctx.get("no_casualties", false):
			c._unlock("ACH_NO_CASUALTIES")
	if int(c.stats["kills"]) >= 25:
		c._unlock("ACH_KILLS_25")
	if int(c.stats["kills"]) >= 100:
		c._unlock("ACH_HUNDRED_KILLS")
	if int(c.stats["assists"]) >= 100:
		c._unlock("ACH_ASSISTS_100")
	if ctx.get("mvp_is_ours", false):
		c._unlock("ACH_GOLD_MVP")
	if ctx.get("ace", false):
		c._unlock("ACH_ACE")
	if ctx.get("team_effort", false):
		c._unlock("ACH_TEAM_EFFORT")
	if ctx.get("field_medic", false):
		c._unlock("ACH_FIELD_MEDIC")
	if c.trophies.size() >= 5:
		c._unlock("ACH_TROPHIES_5")
