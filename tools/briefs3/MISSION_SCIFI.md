# Mission SCI-FI (DLC « Cosmos ») : pièces de kit + 3 arènes

Lis d'abord `COMMON3.md`. Dossiers à toi : `assets/models/kit/kit_scifi.glb` (+ `assets/models/kit/preview_scifi/`), `data/dlc/kit_scifi_parts.json` (liste de tes pièces), `assets/models/arenas/arena_station.glb|arena_alien.glb|arena_reactor.glb`, `assets/textures/arena/` (SEULEMENT les fichiers préfixés par tes ids d'arène), `assets/models/arenas/preview/<id>.png`, `tools/dlc_scifi/`.

## Partie 1 — Kit science-fiction `assets/models/kit/kit_scifi.glb`
UN seul GLB (même format que kit_gear.glb / kit_bodies.glb / kit_weapons.glb : toutes les pièces comme nœuds nommés, origines sur les pivots, vertex colors COLOR_0 masque R/G/B + A=AO). Pièces EXACTES (noms imposés, le code du jeu les référence) :
- Espèces (7 pièces chacune : `body_<espece>_{pelvis,torso,head,arm_l,arm_r,leg_l,leg_r}`) : `robot` (corps métallique articulé, tête ronde avec écran/visière, un peu plus massif ; cartoon) et `alien` (tête grosse allongée, grands yeux sombres, 3 doigts, peau lisse ; silhouette fine).
- Couvre-chefs (joint tête) : `helm_astronaut` (dôme de verre, col métal), `helm_visor` (casque tactique + visière), `helm_cyborg` (demi-visage mécanique + oeil optique), `helm_pilot` (casque aviateur + lunettes), `hat_antenna` (petit bonnet à antennes), `hair_tech` (coiffure rasée avec rangées de LED éteintes, style punk futuriste).
- Torse (joint torse, + variante `_skirt` sur le bassin si pertinent) : `armor_spacesuit`, `armor_exo` (exosquelette léger), `armor_jacket_tech` (veste technique à col), `armor_mech` (plastron de mécha massif), `armor_medic` (combinaison blanche à croix), `armor_psi_robe` (robe futuriste d'alien).
- Épaulières (`shoulder_<nom>_l` / `_r`) : `tech`, `jet` (propulseur), `dome` (épaulière en dôme).
- Dos : `back_jetpack`, `back_drone` (petit drone flottant derrière l'épaule), `back_antenna_dish`, `back_reactor` (bloc réacteur massif).
- Armes (origine = prise en main, axe +Y, avant vers +Z, comme le contrat) : `wpn_blaster` (pistolet laser, canon vers +Z), `wpn_rifle_plasma` (fusil), `wpn_railgun` (long fusil sniper, canon +Z), `wpn_energy_blade` (épée d'énergie, lame le long de +Y), `wpn_energy_dagger` (paire en 2 pièces `_l` et `_r`), `wpn_energy_shield` (bouclier hexagonal, plan XY, face +Z), `wpn_wrench` (clé à molette géante), `wpn_gauntlet` (paire `_l`/`_r`, gros gants de combat mécaniques), `wpn_plasma_staff` (bâton à orbe de plasma), `wpn_controller` (manette holographique d'off-hand, centrée), `wpn_med_gun` (pistolet seringue).
- Invocations : `summon_drone` (drone volant), `summon_turret_laser` (tourelle).
Les couleurs du jeu viennent du masque (primaire/secondaire/accent) : concentre-toi sur les formes et les détails de matière.
Livre aussi `data/dlc/kit_scifi_parts.json` : {"species": [...], "parts": [noms], "triangles": {nom: n}}.

## Partie 2 — 3 arènes science-fiction (ordre de priorité)
Même gabarit/disposition d'obstacles que les arènes existantes (voir COMMON3 §5), même qualité que `arena_colosseum.glb`/`arena_forge.glb`, palette terreuse (acier usé, béton, rouille, laiton, verre fumé, petites lampes orange/teal discrètes ; AUCUN néon fluo/cyberpunk) :
1. `station` « Station Orbitale » : pont d'une station spatiale rétro-industrielle, baie vitrée sur la Terre et les étoiles au fond, panneaux métalliques, tuyaux, caillebotis.
2. `alien` « Planète Rouge » : désert rocheux martien, arches de roche, cristaux, deux lunes, ciel poussiéreux orangé, ruines d'une base abandonnée.
3. `reactor` « Cœur de Réacteur » : salle de réacteur, anneaux de confinement, cuves, passerelles, lueur orange/teal douce.
Pour chacune : `assets/models/arenas/arena_<id>.glb`, aperçu `assets/models/arenas/preview/<id>.png` (rendu de contrôle ≤ 960×540), et un fichier de thème `data/dlc/theme_<id>.json` avec EXACTEMENT les clés de `Arena.THEMES` (voir `src/battle/Arena.gd`) : {"file": "arena_<id>.glb", "sun": "#hex", "sun_e": n, "sun_rot": [x,y,z], "sky_top", "sky_hor", "ambient", "ambient_e", "fog", "fog_d", "torch", "ember", "ground_a", "ground_b", "line", "name": "nom FR"}.
Livre arène par arène (GLB valide dès qu'une est finie). Priorité : kit (partie 1) puis station, alien, reactor.
