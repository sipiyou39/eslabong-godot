"""Écrit assets/audio/manifest.json à partir des fichiers réellement présents (mesures recalculées)."""
import os, json, glob
import numpy as np
import soundfile as sf
import qa
import build_sfx, sfxlib
from dsp import SR

ROOT = qa.ROOT
CAT_MAP = {'ui': ('ui', 'ui'), 'combat': ('combat', 'combat'), 'spell': ('combat', 'spell'), 'match': ('match', 'match'),
           'ambience': ('match', 'ambience'), 'voice': ('voice', 'voice')}
BUS = {'ui': 'ui', 'combat': 'sfx', 'match': 'sfx', 'voice': 'voice'}
TARGET_ST = {'ui': -14.0, 'combat': -14.0, 'match': -13.0, 'voice': -14.0}

MUSIC = {
    'music_menu': dict(key='D minor', tags=['menu', 'epic', 'dark', 'medieval', 'slow', 'choir', 'strings', 'horns'],
                       desc='Menu principal : cordes, cors, choeur synthétique, timbales, thème lent en ré mineur',
                       recommended_loop=True),
    'music_club': dict(key='G major', tags=['club', 'warm', 'folk', 'lute', 'flute', 'tavern'],
                       desc='Club / gestion : luth, flûte, percussions douces, sol majeur', recommended_loop=True),
    'music_battle_1': dict(key='E minor', tags=['battle', 'tense', 'taiko', 'brass', 'tribal'],
                           desc='Combat 1 : taiko, ostinato de cordes graves, cuivres, mi mineur', recommended_loop=True),
    'music_battle_2': dict(key='A phrygian dominant', tags=['battle', 'tense', 'tribal', 'toms', 'oud', 'exotic'],
                           desc='Combat 2 : toms tribaux, oud, cuivres, mode phrygien dominant sur la', recommended_loop=True),
    'music_battle_boss': dict(key='C minor', tags=['battle', 'boss', 'heavy', 'dramatic', 'choir', 'low brass'],
                              desc='Boss : cuivres graves, choeur, timbales massives, do mineur', recommended_loop=True),
    'music_cup': dict(key='D major', tags=['cup', 'triumphant', 'fanfare', 'brass', 'orchestral'],
                      desc='Coupe : fanfares de cuivres, cordes, timbales, ré majeur', recommended_loop=True),
    'music_chaos_thunder': dict(key='F minor', tags=['chaos', 'electric', 'storm', 'thunder', 'synth'],
                                desc='Chaos / orage : arpèges synthé, basse saturée, batterie, tonnerre, fa mineur',
                                recommended_loop=True),
    'music_draft': dict(key='G dorian', tags=['draft', 'suspense', 'light', 'pizzicato', 'celesta'],
                        desc='Draft : pizzicati, célesta, flûte, suspense léger, sol dorien', recommended_loop=True),
    'music_chest': dict(key='C major', tags=['chest', 'magic', 'short', 'harp', 'bells', 'sparkle'],
                        desc='Ouverture de coffre : harpe, cloches, choeur, 20 s', recommended_loop=True),
    'music_victory': dict(key='F major', tags=['victory', 'fanfare', 'jingle', 'brass', 'orchestral'],
                          desc='Victoire : fanfare et thème triomphal, 30 s', recommended_loop=False),
    'music_defeat': dict(key='B minor', tags=['defeat', 'sad', 'dark', 'cello', 'slow'],
                         desc='Défaite : violoncelle et cors, si mineur sombre, 30 s', recommended_loop=False),
}


def main():
    build_sfx.load()
    mstats = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_stats.json')))
    files = []
    families = {}
    for name, spec in sfxlib.REG.items():
        cat, grp = CAT_MAP[spec['cat']]
        for v in range(1, spec['n'] + 1):
            fn = f"{name}_{v}.wav"
            p = os.path.join(ROOT, 'sfx', fn)
            a = qa.analyze(p, spec['loop'])
            info = sf.info(p)
            gain = float(np.clip(TARGET_ST[cat] - a['st_db'], -12.0, 3.0)) + spec['gain']
            if spec['cat'] == 'ambience' and spec['loop']:
                gain = -8.0
            if spec['loop'] and name != 'crowd_ambience_loop':
                gain = float(np.clip(gain, -14, 3))
            files.append(dict(name=f"{name}_{v}", family=name, variant=v, file=f"sfx/{fn}", category=cat, group=grp,
                              bus=('ambience' if spec['cat'] == 'ambience' and spec['loop'] else BUS[cat]),
                              duration=round(info.frames / info.samplerate, 3), loop=bool(spec['loop']),
                              channels=info.channels, sample_rate=info.samplerate, format='wav/pcm16',
                              tags=spec['tags'], peak_db=round(a['peak_db'], 1), rms_db=round(a['rms_db'], 1),
                              gain_db=round(gain, 1)))
            families.setdefault(name, dict(variants=spec['n'], category=cat, group=grp, loop=bool(spec['loop']), files=[]))['files'].append(f"sfx/{fn}")
    for name, md in MUSIC.items():
        p = os.path.join(ROOT, 'music', name + '.ogg')
        info = sf.info(p)
        st = mstats[name]
        dur = info.frames / info.samplerate
        a = qa.analyze(p, True)
        files.append(dict(name=name, family=name, variant=1, file=f"music/{name}.ogg", category='music', group='music',
                          bus='music', duration=round(dur, 3), loop=True, recommended_loop=md['recommended_loop'],
                          loop_start=0.0, loop_end=round(dur, 3), channels=info.channels,
                          sample_rate=info.samplerate, format='ogg/vorbis q6', bpm=st['bpm'], bars=st['bars'], key=md['key'],
                          tags=md['tags'], description=md['desc'], peak_db=round(a['peak_db'], 1), rms_db=round(a['rms_db'], 1),
                          gain_db=round(float(np.clip(-22.0 - a['rms_db'], -14, 0)), 1)))
        families[name] = dict(variants=1, category='music', group='music', loop=True, files=[f"music/{name}.ogg"])
    man = dict(
        version=1, sample_rate=SR, root='res://assets/audio/',
        generator='tools/audio (numpy/scipy, 100% procedural) : python build_sfx.py ; python build_music.py ; python build_manifest.py',
        notes=[
            "files[] : un élément par fichier. 'family' = nom de base ; choisir une variante au hasard parmi families[family].files.",
            "SFX : wav 44,1 kHz 16 bit, mono (ambiances/foule en stéréo), pic normalisé à -3 dBFS, début/fin sans clic.",
            "gain_db : volume conseillé (dB) pour égaliser la sonie perçue (mesure sur la fenêtre de 300 ms la plus forte) ; à régler avec volume_db du lecteur.",
            "loop=true : boucle sans couture. Les WAV en boucle contiennent un chunk 'smpl' (Godot : loop_mode 'Detect From WAV'). Les OGG musique : mettre stream.loop = true (ou loop=true à l'import).",
            "Musiques : ogg vorbis stéréo (q6), la fin raccorde le début (rendu circulaire, queue de réverbération repliée sur l'intro) ; loop_start=0, loop_end=durée.",
            "recommended_loop=false (music_victory, music_defeat) : jingles de 30 s à jouer une fois ; ils restent bouclables sans clic.",
        ],
        counts=dict(sfx_files=sum(1 for f in files if f['category'] != 'music'), sfx_families=sum(1 for v in families.values() if v['category'] != 'music'),
                    music=len(MUSIC)),
        files=files, families=families)
    with open(os.path.join(ROOT, 'manifest.json'), 'w') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    print('manifest:', man['counts'], 'files', len(files))


if __name__ == '__main__':
    main()
