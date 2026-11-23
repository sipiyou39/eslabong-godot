# Eslabong — reproduction Godot 4.7 (projet de fan)

Club de mercenaires + arène tactique en temps réel (3D vue de dessus), reconstruit à partir de specs. Projet de fan, non affilié au jeu d'origine ; tous les modèles, sons et icônes sont générés par code (Blender, Python).

## Lancer sur PC / Mac / Linux
1. Installe **Godot 4.7** (version standard, pas .NET) : https://godotengine.org/download
2. Clone ou télécharge ce dépôt (bouton vert **Code** → *Download ZIP*, puis dézippe).
3. Ouvre Godot → **Importer** → choisis `project.godot` → **Importer & modifier**. Le premier import prend quelques minutes (textures, modèles, sons).
4. Appuie sur **F5** (ou ▶ en haut à droite) pour lancer le jeu.

Carte graphique compatible Vulkan/Metal requise (rendu Forward+). Si ça rame : Réglages → Vidéo, désactive SSAO / brouillard volumétrique / profondeur de champ.

## Contrôles (combat)
ZQSD / WASD déplacer • clic gauche attaque (maintenu) • clic droit, A/Q, E, R compétences • ESPACE esquive • TAB changer de combattant • T vitesse x1/x2/x3 • F1-F4 ordres tactiques • H masquer l'interface • ÉCHAP pause. Manette : stick gauche/droit, A/X/Y/B/RB, LB changer. Sans contrôle : mode Manager (IA complète), clic sur un allié pour le prendre en main.

## Contenu
- 57 classes, 46 champions, 18 boss, 5 spéciaux, 618 compétences pilotées par 32 archétypes d'exécution, 81 reliques, 52 équipes.
- Campagne : 4 divisions de 13 clubs, 24 journées, promotion/relégation, marché, installations, personnel, blessures, forme, maîtrises, médailles, renaissance, ascension, shiny, légendaires, coffres, succès.
- Modes : Ligue, Académie 3v3, Coupe des Champions, Chaos Thunder (8 combattants), Coupe spéciale 3v3v3v3, Coupe Draft, Tour du Défi, Defend the Iron Gate (boss Poroxi), Hall des légendes, Entraînement / match personnalisé.
- 5 arènes + QG modélisés dans Blender, 7 espèces modulaires + 78 pièces d'équipement + 48 armes, 282 SFX et 11 musiques synthétisés, 618 icônes de compétences, UI, héraldique, VFX.

## Pour les curieux
`tools/build_catalog.py` génère `data/*.json` (il lui faut les documents de specs d'origine, non inclus). Les scripts de génération d'assets sont dans `tools/` (Blender, audio, art 2D) et contiennent un chemin d'exemple `/path/to/elsasko` à adapter. Notes techniques : `PROJECT_NOTES.md`. Sauvegarde : dossier utilisateur Godot du projet (`eslabong_campaign_1.json`).
