"""Outils de texture communs aux arènes sci-fi (python du venv : numpy, scipy, pillow). S'appuie sur tools/blender_arenas/tex.py (ROOT corrigé)."""
import os
import sys
import math
import numpy as np
import arena_env
arena_env.load('tex')
import tex as T                                 # noqa: E402
from tex import *                               # noqa: E402,F401,F403
from PIL import Image                           # noqa: E402

TEXDIR = arena_env.TEXDIR
os.makedirs(TEXDIR, exist_ok=True)


def savej(name, arr, q=90):
    """albédo en JPEG (sobre) dans assets/textures/arena."""
    a = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    if a.ndim == 3 and a.shape[2] == 1:
        a = a[:, :, 0]
    path = os.path.join(TEXDIR, name)
    Image.fromarray(a).save(path, quality=q, optimize=True, subsampling=0)
    print('texture', name, a.shape, os.path.getsize(path) // 1024, 'Ko')


def savep(name, arr):
    a = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    if a.ndim == 3 and a.shape[2] == 1:
        a = a[:, :, 0]
    path = os.path.join(TEXDIR, name)
    Image.fromarray(a).save(path, optimize=True)
    print('texture', name, a.shape, os.path.getsize(path) // 1024, 'Ko')


def savej_n(name, arr, q=93):
    savej(name, arr, q)


def tile_pair(prefix, col, height, nstr=2.0, scale_m=2.0, size=512, nfmt='jpg'):
    savej(prefix + '.jpg', col)
    if height is not None:
        n = to_normal(height, nstr, scale_m / size, wrap=True)
        (savej_n if nfmt == 'jpg' else savep)(prefix + ('_n.jpg' if nfmt == 'jpg' else '_n.png'), n)


def scratches(X, Y, seed, density=0.5, length=0.8, size=512, scale_m=2.0):
    """rayures fines orientées (masque 0..1, tileable approximatif)."""
    rg = np.random.default_rng(seed)
    m = np.zeros(X.shape, np.float32)
    ang = rg.uniform(0, math.pi, 30)
    for a in ang:
        c, s = math.cos(a), math.sin(a)
        u = (X * c + Y * s) * (0.5 / scale_m * 8)
        v = (-X * s + Y * c) * (24 / scale_m)
        n = fbm(u * 0.5, v * 0.05, 2, int(a * 1000) % 997, None)
        line = smooth(0.03, 0.0, np.abs(np.sin(v * 3.1 + n * 3)) * 0 + np.abs(((v * 0.8) % 1.0) - 0.5) - 0.48)
    return m


def png2jpg(prefix, q=90):
    """convertit prefix.png et prefix_n.png (écrits par tex.py) en JPEG et supprime les PNG."""
    for suf in ('', '_n'):
        p = os.path.join(TEXDIR, prefix + suf + '.png')
        if os.path.exists(p):
            Image.open(p).convert('RGB').save(os.path.join(TEXDIR, prefix + suf + '.jpg'), quality=q, optimize=True)
            os.remove(p)
            print('texture', prefix + suf + '.jpg')
