# ArenaBattler (base : jeu « Eslabong » restauré) — règles communes des agents d'assets

Projet Godot 4.7 : arène tactique 3D vue de dessus (caméra ~55°), mercenaires modulaires assemblés depuis un « kit » Blender, arènes Blender. La racine du projet (ROOT) est donnée dans ton prompt ; dans tes scripts calcule-la depuis l'emplacement du script (`Path(__file__).resolve().parents[2]`).

## Direction artistique : RESTER DANS LE STYLE DE L'EXISTANT
Le boss adore le rendu du jeu actuel (persos, sorts, arènes) : il veut que les nouveaux contenus soient **indiscernables en style** de l'existant. Avant de modéliser :
1. Regarde les aperçus existants : `assets/models/kit/preview*/`, `assets/models/arenas/preview/` et les PNG de textures `assets/textures/arena/`.
2. Lis les scripts existants et RÉUTILISE leurs bibliothèques : `tools/blender_kit_bodies/` (humanoid.py, gear_*.py, heads.py…), `tools/blender_kit_weapons/`, `tools/blender_arenas/` (lib_scene.py, lib_geo.py, arena_common.py, tex.py, themes.py, build_*.py).
3. Style : cartoon-réaliste « peint » façon Team Fortress / Clash Royale, proportions un peu stylisées, matières crédibles (métal, cuir, tissu, pierre), palette terreuse et chaude, pas de pastel bonbon, pas de néon fluo, contours ajoutés par le shader du jeu (ne pas en dessiner).
4. Contrat du kit : `data/kit_contract.json` (pivots, noms, masque de couleurs sommets COLOR_0 : R primaire, G secondaire, B accent/métal, reste = peau, A = AO). Tout ce qui est équipement doit respecter les conventions d'origine EXACTEMENT (origine sur le pivot, +Z avant, etc.).
5. Contrat des arènes : demi-taille 26×16 m (`data/arena_layout.json` : obstacles circulaires exacts à reproduire visuellement, torches), nœuds `Torch_*` pour les lumières, mêmes conventions que `assets/models/arenas/arena_*.glb` et `arenas_manifest.json`.

## Contraintes techniques (le jeu doit tourner sur téléphone)
- Pièces de kit : ≤ 1 500 triangles chacune, un seul matériau avec vertex colors comme les pièces existantes.
- Arène : ≤ 70 000 triangles, textures ≤ 2048² au total ≤ 10 Mo par arène (compresse en PNG/JPG sobre, comme les existantes), pas de transparence coûteuse.
- Tout est procédural (Python/Blender CLI), reproductible, rangé dans ton dossier `tools/<ton_domaine>/`. Aucun téléchargement externe.

## Outils
- Python : `tools/.venv/bin/python` (numpy, scipy, pillow, soundfile).
- Blender 5.2 CLI : `/Applications/Blender.app/Contents/MacOS/Blender -b --python script.py` (EEVEE, aperçus ≤ 960×540, ≤ 24 échantillons ; la machine est partagée avec 2 autres agents : sois sobre).
- Vérifie TOUT en rendant des PNG et en les regardant (outil Read sur l'image) ; itère jusqu'à ce que ce soit beau et cohérent avec l'existant.
- Ne lance JAMAIS Godot sur le dossier racine (cache partagé). Pour tester un import, copie dans un projet jetable du scratchpad : `/Applications/Godot.app/Contents/MacOS/Godot --headless --path <tmp> --import`.
- N'écris que dans TES dossiers (listés dans ta mission). Ne modifie ni `src/` ni `data/*.json` existants.
- Rapport final COURT (≤ 200 mots) : fichiers livrés, noms exacts, écarts, limites.
