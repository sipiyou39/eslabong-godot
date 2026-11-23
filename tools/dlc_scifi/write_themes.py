"""Écrit data/dlc/theme_<id>.json (clés EXACTES de Arena.THEMES) : python3 write_themes.py"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sf_themes import GAME_THEMES

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
KEYS = ["file", "sun", "sun_e", "sun_rot", "sky_top", "sky_hor", "ambient", "ambient_e", "fog", "fog_d", "torch", "ember", "ground_a", "ground_b", "line", "name"]
os.makedirs(os.path.join(ROOT, 'data', 'dlc'), exist_ok=True)
for k, v in GAME_THEMES.items():
    assert list(v.keys()) == KEYS, k
    with open(os.path.join(ROOT, 'data', 'dlc', f'theme_{k}.json'), 'w') as f:
        json.dump(v, f, indent=1, ensure_ascii=False)
    print('theme', k)
