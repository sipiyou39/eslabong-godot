# Règles communes (tous les agents d'assets)

Projet : jeu Godot 4.7 « Eslabong » (arène tactique 3D vue de dessus, club de mercenaires), racine `/path/to/elsasko`.
Objectif visuel : qualité « triple A » stylisée (type Hades / Dota Underlords / Battlerite / Bastion), lisible en vue de dessus inclinée (~55°), palette riche et cohérente, silhouettes fortes, bords biseautés, pas de formes "primitives brutes".

* Python : `/path/to/elsasko/tools/.venv/bin/python` (numpy, scipy, pillow, soundfile déjà installés — tu peux `pip install` d'autres paquets dans CE venv si besoin).
* Blender 5.2.2 en ligne de commande : `/Applications/Blender.app/Contents/MacOS/Blender -b --python script.py` (écris tes scripts dans ton dossier `tools/<ton_domaine>/`). Pour vérifier visuellement, rends des PNG (EEVEE ou Cycles low-sample) et regarde-les avec l'outil Read (il affiche les images). Itère jusqu'à ce que ça soit beau.
* Ne lance JAMAIS Godot sur `/path/to/elsasko` (cache partagé avec l'intégrateur). Si tu veux tester un import GLB, copie ton fichier dans un projet Godot jetable dans ton scratchpad (`/Applications/Godot.app/Contents/MacOS/Godot --headless --path <tmp> --import`).
* N'écris QUE dans les dossiers qui t'appartiennent (listés dans ta mission). Ne modifie pas `data/*.json` ni `src/`.
* Aucun téléchargement de ressources externes : tout est généré procéduralement (code), sauf polices déjà présentes dans `assets/fonts/`.
* Tout est fait main par script → rends tes scripts reproductibles et commente-les peu mais proprement.
* À la fin, réponds avec un compte rendu COURT (max 200 mots) : fichiers livrés, écarts par rapport au contrat, limites connues.
