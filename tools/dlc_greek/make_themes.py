"""Écrit data/dlc/theme_<id>.json (clés exactes d'Arena.THEMES) pour les 3 arènes grecques."""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
TH = {
    'olympus': {"file": "arena_olympus.glb", "sun": "#ffe6b8", "sun_e": 1.5, "sun_rot": [-48, -30, 0], "sky_top": "#2a4a9a", "sky_hor": "#ffd890", "ambient": "#a8b4dc",
                "ambient_e": 0.7, "fog": "#f0d8b0", "fog_d": 0.0022, "torch": "#ffc860", "ember": "#ffe0a0", "ground_a": "#e8dcc4", "ground_b": "#c8b890", "line": "#d8aa40",
                "name": "Mont Olympe"},
    'underworld': {"file": "arena_underworld.glb", "sun": "#8affd0", "sun_e": 1.0, "sun_rot": [-55, 25, 0], "sky_top": "#0a0410", "sky_hor": "#4a1810", "ambient": "#5a4a6a",
                   "ambient_e": 0.62, "fog": "#2a1218", "fog_d": 0.009, "torch": "#4affc0", "ember": "#a0ffd8", "ground_a": "#2c2833", "ground_b": "#1a171f", "line": "#4affc0",
                   "name": "Les Enfers"},
    'atlantis': {"file": "arena_atlantis.glb", "sun": "#a8fff0", "sun_e": 1.3, "sun_rot": [-62, 15, 0], "sky_top": "#04283a", "sky_hor": "#0e7088", "ambient": "#5fb8c8",
                 "ambient_e": 0.8, "fog": "#0c5a70", "fog_d": 0.012, "torch": "#7affea", "ember": "#c8fff6", "ground_a": "#b8d6d0", "ground_b": "#7aa8a8", "line": "#ffe08a",
                 "name": "Atlantide"},
}
os.makedirs(os.path.join(ROOT, 'data', 'dlc'), exist_ok=True)
for k, v in TH.items():
    json.dump(v, open(os.path.join(ROOT, 'data', 'dlc', f'theme_{k}.json'), 'w'), indent=1, ensure_ascii=False)
    print('theme', k)
