class_name NameGen
extends RefCounted
## Générateur de noms de mercenaires et d'équipes.

const FIRST := ["Aldous", "Dorian", "Farooq", "Leonard", "Ravi", "Kaede", "Quinn", "Cheruiyot", "Milena", "Oswin", "Felgrom", "Brynja", "Tavish", "Isolde", "Garrick",
	"Sorcha", "Bodil", "Hakon", "Zephyr", "Marguerite", "Ottoline", "Cassian", "Nadia", "Teodor", "Ysolde", "Bram", "Selene", "Magnus", "Ilvara", "Rurik", "Perrin", "Dagny",
	"Lucan", "Odalys", "Kestrel", "Vesper", "Thane", "Mirela", "Joss", "Anouk", "Fenwick", "Sigrun", "Casimir", "Emeric", "Nyla", "Wulfric", "Tamsin", "Orsino", "Valka", "Gideon",
	"Rhosyn", "Balthazar", "Ingrid", "Corvin", "Aurelie", "Dmitri", "Halvar", "Elowen", "Soren", "Beatrix", "Kaito", "Zora", "Lazlo", "Maeve", "Torvald", "Priya", "Evander", "Oona"]
const EPITHET := ["the Tracker", "the Weekend Warrior", "the Flamekeeper", "of the Overdraft Fee", "the Unyielding", "Ironhand", "the Quiet", "Stormborn", "the Gilded",
	"Whisperblade", "the Reckless", "Oathbreaker", "the Lucky", "Coldeye", "the Grim", "Longstride", "the Patient", "Bonesaw", "Brightshield", "the Undying"]

static func random_name(rnd: RandomNumberGenerator, epithet_chance: float = 0.12) -> String:
	var n: String = FIRST[rnd.randi() % FIRST.size()]
	if rnd.randf() < epithet_chance:
		n += " " + EPITHET[rnd.randi() % EPITHET.size()]
	return n
