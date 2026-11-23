# Mission DIEUX GRECS (DLC « Olympe ») : pièces de kit + 3 arènes

Lis d'abord `COMMON3.md`. Dossiers à toi : `assets/models/kit/kit_greek.glb` (+ `assets/models/kit/preview_greek/`), `data/dlc/kit_greek_parts.json`, `assets/models/arenas/arena_olympus.glb|arena_underworld.glb|arena_atlantis.glb`, `assets/textures/arena/` (SEULEMENT les fichiers préfixés par tes ids d'arène), `assets/models/arenas/preview/<id>.png`, `tools/dlc_greek/`.

## Partie 1 — Kit grec `assets/models/kit/kit_greek.glb`
UN seul GLB (même format que kit_gear.glb / kit_weapons.glb : nœuds nommés, origines sur les pivots, vertex colors COLOR_0 masque R/G/B + A=AO). Les dieux utilisent l'espèce `human` existante (pas de nouveau corps). Pièces EXACTES (noms imposés) :
- Têtes/couvre-chefs (joint tête) : `helm_corinthian` (casque corinthien à crête), `crown_laurel` (couronne de lauriers), `helm_winged` (casque ailé), `helm_hades` (casque sombre à cornes courtes et flammes), `crown_sun` (couronne à rayons de soleil), `crown_moon` (diadème croissant de lune), `hair_beard_long` (cheveux longs + grande barbe majestueuse de Zeus/Poséidon), `hair_snakes` (chevelure de serpents de Méduse), `helm_ares` (casque de guerre à crête rouge haute et visière).
- Torse (+ `_skirt` sur le bassin si pertinent) : `armor_toga` (toge drapée sur une épaule), `armor_cuirass_greek` (cuirasse musclée de bronze + ptérugès), `armor_chiton` (tunique plissée courte).
- Épaulières (`shoulder_<nom>_l` / `_r`) : `laurel` (feuilles dorées), `gorget` (épaulière ronde de bronze), `pteruges` (lanières de cuir).
- Dos : `back_cape_royal` (grande cape pourpre à agrafe), `back_wings_hermes` (petites ailes), `back_sun_disk` (disque solaire doré derrière la tête/le dos), `back_tail_snake` (queue de serpent), `back_quiver_gold` (carquois doré), `back_aegis` (peau de chèvre/égide).
- Armes (origine = prise en main, axe +Y, avant +Z) : `wpn_thunderbolt` (foudre dorée en zigzag), `wpn_trident` (trident de Poséidon), `wpn_bident` (fourche à deux pointes d'Hadès), `wpn_lyre` (lyre dorée, off-hand style cast, centrée), `wpn_bow_golden` (arc doré, ventre +Z), `wpn_kopis` (épée courbe grecque), `wpn_spear_greek` (lance à feuille), `wpn_caduceus` (bâton à serpents ailé), `wpn_shield_aegis` (bouclier à tête de Gorgone, plan XY, face +Z), `wpn_shield_hoplon` (bouclier rond de hoplite).
- Invocations : `summon_shade` (ombre/spectre d'Hadès), `summon_owl` (chouette d'Athéna).
Livre aussi `data/dlc/kit_greek_parts.json` : {"parts": [noms], "triangles": {nom: n}}.

## Partie 2 — 3 arènes grecques (ordre de priorité)
Même gabarit/disposition d'obstacles que les arènes existantes (voir COMMON3 §5), même qualité que `arena_colosseum.glb`, palette : marbre patiné, bronze, or terni, ciel doré ou orageux :
1. `olympus` « Mont Olympe » : terrasse de marbre au sommet d'une montagne ABOVE the clouds, colonnes dorées, temple de Zeus au fond, mer de nuages tout autour, foudre lointaine.
2. `underworld` « Les Enfers » : cavernes d'Hadès, fleuve Styx vert-bleuté, rochers noirs, flammes spectrales discrètes, portes de bronze, lueur braise sombre.
3. `atlantis` « Atlantide » : temple sous-marin de Poséidon, colonnes corail et coquillages géants, rayons de lumière bleu-vert profond sobre, bulles, statue de tridents.
Pour chacune : `assets/models/arenas/arena_<id>.glb`, aperçu `assets/models/arenas/preview/<id>.png` (≤ 960×540), et `data/dlc/theme_<id>.json` avec EXACTEMENT les clés de `Arena.THEMES` (voir `src/battle/Arena.gd`) : {"file": "arena_<id>.glb", "sun": "#hex", "sun_e": n, "sun_rot": [x,y,z], "sky_top", "sky_hor", "ambient", "ambient_e", "fog", "fog_d", "torch", "ember", "ground_a", "ground_b", "line", "name": "nom FR"}.
Livre arène par arène. Priorité : kit (partie 1) puis olympus, underworld, atlantis.
