"""Construit tous les SFX .wav + statistiques (JSON) dans le scratch/manifest partiel.
Usage : python build_sfx.py [filtre_sous_chaine ...]"""
import sys, os, json, time, importlib
import numpy as np
from dsp import *
import sfxlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'audio', 'sfx')
OUT = os.path.abspath(OUT)
STATS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sfx_stats.json')
MODULES = ['sfx_ui', 'sfx_combat', 'sfx_magic', 'sfx_match', 'sfx_voice']


def load():
    for m in MODULES:
        try:
            importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name != m:
                raise


def render(name, spec, v):
    r = rng_for(f"{name}_{v}")
    y = np.asarray(spec['fn'](v, r), float)
    if spec['loop']:
        y = y - np.mean(y, axis=0)
        p = peak(y)
        y = y * (dbv(spec['peak']) / p)
    else:
        y = finish(y, spec['peak'], crest=spec['crest'])
    return y


def main(filters):
    load()
    os.makedirs(OUT, exist_ok=True)
    stats = {}
    if os.path.exists(STATS):
        stats = json.load(open(STATS))
    for name, spec in sfxlib.REG.items():
        if filters and not any(f in name for f in filters):
            continue
        for v in range(1, spec['n'] + 1):
            t0 = time.time()
            try:
                y = render(name, spec, v)
            except Exception as e:
                import traceback
                print(f"!! {name}_{v}: {e}")
                traceback.print_exc()
                continue
            fn = f"{name}_{v}.wav"
            write_wav(os.path.join(OUT, fn), y)
            if spec['loop']:
                add_smpl_loop(os.path.join(OUT, fn), len(y))
            stats[fn] = dict(name=name, variant=v, dur=round(len(y) / SR, 3), ch=1 if y.ndim == 1 else 2,
                             peak_db=round(to_db(peak(y)), 2), rms_db=round(to_db(rms(y)), 2))
            print(f"{fn:34s} {len(y)/SR:5.2f}s pk={stats[fn]['peak_db']:6.1f} rms={stats[fn]['rms_db']:6.1f} ({time.time()-t0:.2f}s)")
    json.dump(stats, open(STATS, 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1:])
