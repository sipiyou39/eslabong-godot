# Eslabong (clone Godot 4.7) — notes de projet

Specs sources : `tools/eslabong-specifications.md` + annexes. Catalogues générés par `tools/.venv/bin/python tools/build_catalog.py` → `data/*.json` (618 ids de compétences uniques / 619 ressources, 57 classes, 46 champions, 18 boss, 5 spéciaux, 81 reliques, 52 équipes).

## Lancer / vérifier
- Compiler : `G=/Applications/Godot.app/Contents/MacOS/Godot; $G --headless --path . --quit 2>&1 | grep -A2 "SCRIPT ERROR"`
- **Après tout nouveau `class_name` ou asset : `$G --headless --path . --import`** (cache de classes globales).
- Combat de test (captures) : `$G --path . --resolution 1600x900 -- --test-battle --auto --shot=/tmp/x.png --shot-delay=8 --seed=11 --theme=colosseum`
- Planche de modèles : `-- --test-model --ids=Merc_Mage_Fire,... --shot=/tmp/m.png [--no-outline]`
- Pas de `timeout` sous macOS : lancer en arrière-plan + boucle `sleep` sur l'existence du PNG, puis `pkill -f "Godot.*test-"`.

## Architecture (src/)
- autoload : Data (catalogues), Settings (settings.cfg + InputMap), Audio (SFX/musiques tolérants), Game (scènes, fondu, postfx, polices).
- battle/ : Battle (manches, dégâts, caméra, input joueur), Fighter, FighterAI, Abilities (exécuteurs par archétype), Projectile, Zone, Arena (GLB Blender + éclairage par thème + tempête), CharacterModel (rig modulaire du kit, animations procédurales), Kit (chargeur de pièces GLB), Vfx, BattleHUD.
- campaign/ : Campaign (état, ligue 4 divisions x13, 24 journées, coupes), MercLogic (naissance/croissance/niveaux/maîtrises/médailles/blessures), Market (marché, reliques, installations, personnel), Results (configs de matchs, application des résultats, avancement de semaine, fin de saison), Achievements, MatchFactory, NameGen.
- ui/ : UI (thème sombre/or, composants), UIBar, CharacterStage (portrait 3D SubViewport) + écrans.
- shaders/ : toon_character (masque palette R/G/B + AO alpha, **pas d'ALPHA écrit** : dithering pour fantôme, sinon l'outline noircit les pièces), outline (coque inversée), telegraph, ground_fallback, postfx.

## Contrats d'assets (agents)
`data/kit_contract.json` (pivots, noms de pièces), `data/arena_layout.json`, briefs dans `tools/briefs/`. Les pièces manquantes → repli en primitives (CharacterModel._build_fallback).

## État final / limites connues
- Export Mac : pas de modèles d'export macOS installés → `Godot --headless --export-pack "macOS" build/Eslabong.pck`, puis `build/Eslabong.app` = copie de Godot.app (exécutable renommé `Eslabong`, `Eslabong.pck` dans Contents/Resources, signature ad hoc). Pour un export propre : installer les export templates 4.7.2.
- QA réelle par agent Haiku (2 essais) : le rendu de la fenêtre se figeait quand elle était pilotée en arrière-plan (clics non pris en compte), donc non concluant ; le reste est validé par des runs scriptés (combats IA de toutes les classes, tous les modes, simulation de 3 saisons, captures d'écran des écrans).
- Sauvegarde : `user://eslabong_campaign_1.json` (les runs de test écrivent dans `user://test_run_save.json`). L'ancien `campaign_autosave_1.json` du dossier app_userdata est un reliquat de test, plus lu.
- Non implémenté / simplifié : langue anglaise (réglage sans effet), Tomes de développement, jalons de stats (`stat_milestones`), Tour du Défi en PvE local au lieu de PvP asynchrone, formules exactes d'armure/résistance (inconnues dans les specs : formule maison 100/(100+1.6×déf)).
