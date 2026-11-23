"""Voile atmosphérique de l'aperçu (brume de profondeur approchée par un dégradé vertical : le haut de l'image = le plus loin).
usage : python post.py <png> <theme>"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from themes import THEMES
path, theme = sys.argv[1], sys.argv[2]
P = THEMES[theme].get('post')
if P:
    im = np.asarray(Image.open(path).convert('RGB'), np.float32) / 255.0
    H, W, _ = im.shape
    y = np.linspace(0, 1, H)[:, None]
    f = np.clip(P['top'] * (1 - y) ** P['gamma'] + P['glob'], 0, 0.95)[..., None]
    out = im * (1 - f) + np.array(P['c'], np.float32) * f
    Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path)
    print('post', theme)
