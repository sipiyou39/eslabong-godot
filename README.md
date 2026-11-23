# ArenaBattler

Club de mercenaires et arène tactique 3D en temps réel, pour **mobile** (téléphone / tablette) et **PC / Mac**. Fait avec **Godot 4.7**. Tous les modèles, icônes, sons et musiques sont générés par code (Blender, Python) : aucun asset externe.

## Lancer sur PC / Mac / Linux
1. Installe **Godot 4.7** (version standard, pas .NET) : https://godotengine.org/download
2. Clone ou télécharge ce dépôt (bouton vert **Code** → *Download ZIP*, puis dézippe).
3. Ouvre Godot → **Importer** → choisis `project.godot` → **Importer & modifier**. Le premier import prend quelques minutes (textures, modèles, sons).
4. Appuie sur **F5** (ou ▶ en haut à droite).

Carte graphique compatible Vulkan/Metal requise. Si ça rame : Réglages → Mobile / Vidéo (ombres, effets d'écran).
Pour essayer l'interface tactile à la souris : Réglages → Mobile → *Type de commandes* = Tactile.

## Contrôles
- **Mobile / tactile** : joystick flottant à gauche (pose le pouce n'importe où dans la moitié gauche), 6 boutons à droite : attaque, dash et 4 compétences. **Appui** = lancer automatique (cible choisie pour toi, anticipation du mouvement) ; **glisser** depuis un bouton = viser à la main (aimantation douce vers les ennemis) ; ramener le doigt au centre du bouton = annuler ; **maintenir** l'attaque = tir continu. Toucher un allié dans la liste en haut = prendre son contrôle. L'aide à la visée se règle dans Réglages → Mobile.
- **Clavier / souris** : ZQSD ou WASD déplacer • clic gauche attaque (maintenu) • clic droit, A/Q, E, R compétences • ESPACE esquive • TAB changer de combattant • T vitesse x1/x2/x3 • F1-F4 ordres tactiques • H masquer l'interface • ÉCHAP pause. Manette prise en charge.

## Contenu
- 73 classes (57 + 16 des packs), 46 champions, 18 boss, 5 spéciaux, 700+ compétences, 81 reliques, 52 équipes.
- **Campagne** : 4 divisions de 13 clubs, 24 journées, promotion/relégation, marché, installations, personnel, blessures, forme, maîtrises, médailles, renaissance, ascension, shiny, légendaires, coffres, succès.
- **Modes** : Ligue, Académie 3v3, Coupe des Champions, Chaos Thunder (8 combattants), Coupe spéciale 3v3v3v3, Coupe Draft, Tour du Défi, Defend the Iron Gate (boss), Hall des légendes, Entraînement / match personnalisé.
- **Packs (DLC)**, activables depuis le menu principal → *Packs (DLC)* (gratuits dans cette version) :
  - **Cosmos** — science-fiction : 8 classes (Marine Orbital, Titan Mécanique, Sergent Plasma, Spectre, Sniper Rail, Psion, Docteur Nano, Pilote de Drones) et 3 arènes (Station Orbitale, Planète Rouge, Cœur de Réacteur).
  - **Olympe** — dieux grecs : 8 classes (Zeus, Athéna, Poséidon, Hadès, Artémis, Apollon, Arès, Méduse) et 3 arènes (Mont Olympe, Les Enfers, Atlantide).
- Arènes de base : Colisée, Forteresse de Glace, Forge Volcanique, Porte de Fer, Chaos Thunder + Cratère de Lave, Glacier des Géants, Îles des Nuages, Temple de la Jungle.

## Pour les curieux
Données dans `data/` ; packs dans `data/dlc/` (générés par `tools/build_dlc_data.py`). Les scripts de génération d'assets sont dans `tools/` (Blender, audio, art 2D). Notes techniques : `PROJECT_NOTES.md`. Sauvegarde : dossier utilisateur Godot du projet (`arenabattler_campaign_1.json`).
