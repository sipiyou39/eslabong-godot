"""Rend les musiques (boucles circulaires), encode en .ogg (ffmpeg libvorbis q6), vérifie.
Usage : python build_music.py [nom ...]"""
import sys, os, json, subprocess, time, importlib
import numpy as np
import soundfile as sf
from dsp import *

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'audio', 'music'))
TMP = '/tmp/eslabong_scratch/music_wav'
STATS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_stats.json')
TRACKS = {
    'music_menu': ('songs_a', 'menu'), 'music_club': ('songs_a', 'club'), 'music_draft': ('songs_a', 'draft'),
    'music_chest': ('songs_a', 'chest'),
    'music_battle_1': ('songs_b', 'battle1'), 'music_battle_2': ('songs_b', 'battle2'),
    'music_battle_boss': ('songs_b', 'boss'), 'music_chaos_thunder': ('songs_b', 'chaos'),
    'music_cup': ('songs_c', 'cup'), 'music_victory': ('songs_c', 'victory'), 'music_defeat': ('songs_c', 'defeat'),
}


def main(names):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    stats = json.load(open(STATS)) if os.path.exists(STATS) else {}
    for name, (mod, fn) in TRACKS.items():
        if names and not any(n in name for n in names):
            continue
        try:
            m = importlib.import_module(mod)
        except ModuleNotFoundError as e:
            if e.name == mod:
                continue
            raise
        if not hasattr(m, fn):
            continue
        t0 = time.time()
        S = getattr(m, fn)()
        x = S.master()
        for w in S.lint:
            print('   LINT', w)
        wav = os.path.join(TMP, name + '.wav')
        sf.write(wav, x, SR, subtype='PCM_16')
        ogg = os.path.join(OUT, name + '.ogg')
        subprocess.run(['/opt/homebrew/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'libvorbis', '-q:a', '6', ogg], check=True)
        stats[name] = dict(dur=round(len(x) / SR, 3), bpm=S.bpm, bars=S.bars, peak_db=round(to_db(peak(x)), 2),
                           rms_db=round(to_db(rms(x)), 2), size_kb=round(os.path.getsize(ogg) / 1024))
        print(f"{name}: {len(x)/SR:.1f}s  ogg {stats[name]['size_kb']} KB  ({time.time()-t0:.1f}s)")
    json.dump(stats, open(STATS, 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1:])
