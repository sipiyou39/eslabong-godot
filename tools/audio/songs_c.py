"""Musiques : cup (triomphale), victory, defeat."""
from music_lib import *
from songs_b import pad_chords, snare_roll
import inst


def cup():
    S = Song('music_cup', 108, 40, seed=91)
    S.bus('perc', -4, hall=0.2, room=0.15)
    S.bus('bass', 0, hall=0.1, room=0.05, hp_hz=35)
    S.bus('strings', -4, hall=0.45)
    S.bus('violin', 0, hall=0.45)
    S.bus('brass', 0, hall=0.4, room=0.05)
    S.bus('horn', 0, hall=0.45)
    S.bus('choir', 2, hall=0.6)
    S.bus('bell', -2, hall=0.5)
    S.bus('flute', 2, hall=0.4)
    S.bus('harp', 8, hall=0.45)
    S.bus('fx', -3, hall=0.5)
    S.set_prog(1, "D D G A")
    S.set_prog(5, "D A Bm G D A G A")
    S.set_prog(13, "G D Em A G D Em A")
    S.set_prog(21, "Bm G D A Bm G A A")
    S.set_prog(29, "D A Bm G D A G A")
    S.set_prog(37, "D G A A")
    S.sections = [('intro', 1, 4), ('A', 5, 12), ('B', 13, 20), ('C', 21, 28), ("A'", 29, 36), ('outro', 37, 40)]
    # fanfare d'intro
    F = "A4:.5 A4:.5 A4:.5 D5:1.5 R:1  F#5:.5 F#5:.5 F#5:.5 A5:1.5 R:1  G5:1 B5:1 D6:2  C#6:1.5 B5:.5 A5:2"
    S.melody('brass', inst.brass, F, 1, vel=0.95, att=0.03, rel=0.2)
    S.melody('horn', inst.horn, F, 1, vel=0.7, transpose=-12, att=0.05, rel=0.25)
    for i in range(8):
        S.hit('perc', inst.taiko, 3, i * 0.5, 0.4 + 0.07 * i, 0, 0.8, pitch=74, dur=0.8)
    S.hit('perc', inst.taiko, 1, 0, 0.9, 0, 0.8, pitch=74, dur=1.6)
    S.hit('fx', inst.cymbal_swell, 4, 0, 0.7, 0, 0.8, dur=4 * S.spb)
    # thèmes
    A = "A4:1 D5:1 F#5:1.5 E5:.5  A4:1 C#5:1 E5:2  B4:1 D5:1 F#5:1.5 E5:.5  G5:2 E5:1 D5:1  F#5:1.5 A5:.5 D6:2  C#6:1 B5:1 A5:2  B5:1.5 A5:.5 G5:1 D5:1  E5:1 C#5:1 E5:2"
    S.melody('violin', inst.strings, A, 5, vel=0.8, att=0.1, rel=0.3, voices=4, vcents=9)
    S.melody('horn', inst.horn, A, 5, vel=0.55, transpose=-12, att=0.08, rel=0.3)
    S.melody('violin', inst.strings, A, 29, vel=0.85, att=0.08, rel=0.3, voices=5, vcents=9)
    S.melody('brass', inst.brass, A, 29, vel=0.75, att=0.05, rel=0.25)
    S.melody('horn', inst.horn, A, 29, vel=0.7, transpose=-12, att=0.06, rel=0.3)
    S.melody('choir', inst.choir, A, 29, vel=0.5, vowel='a', att=0.15, rel=0.4, voices=5)
    S.melody('bell', inst.bell, A, 29, vel=0.4, transpose=12, tau=0.6)
    B = "D5:1 G5:1 B5:2  A5:1.5 F#5:.5 A5:2  G5:1 B5:1 D6:2  C#6:1.5 B5:.5 A5:2  B5:1.5 A5:.5 G5:1 B5:1  A5:1 F#5:1 A5:1 D6:1  B5:1 G5:1 E5:2  E5:1 A5:1 C#6:2"
    S.melody('brass', inst.brass, B, 13, vel=0.9, att=0.05, rel=0.25)
    S.melody('violin', inst.strings, B, 13, vel=0.7, att=0.06, rel=0.25, voices=5)
    S.melody('choir', inst.choir, B, 13, vel=0.7, vowel='a', att=0.12, rel=0.4, voices=5)
    S.melody('horn', inst.horn, B, 13, vel=0.7, transpose=-12, att=0.06, rel=0.3)
    S.melody('bell', inst.bell, B, 13, vel=0.45, transpose=12, tau=0.6)
    C = "F#5:2 D5:1 B4:1  B4:1.5 D5:.5 G5:2  F#5:1 A5:1 F#5:1 D5:1  E5:2 C#5:2  D5:1 F#5:1 B5:2  G5:1.5 B5:.5 D6:2  A5:2 E5:2  C#5:1 E5:1 A5:2"
    S.melody('flute', inst.flute, C, 21, vel=0.8, breath=0.12)
    S.melody('violin', inst.strings, C, 21, vel=0.45, att=0.15, rel=0.4, voices=3, transpose=-12)
    arp_pattern(S, 'harp', inst.harp, bars_range(21, 28), [0, 2, 1, 3, 2, 4, 3, 2], 0.5, lo=50, n_oct=3, vel=0.55, from_root=True, dur_mult=2.0)
    O = "D5:2 F#5:2  G5:2 B5:2  A5:2 E5:2  C#5:1 E5:1 A5:2"
    S.melody('brass', inst.brass, O, 37, vel=0.85, att=0.06, rel=0.4)
    S.melody('violin', inst.strings, O, 37, vel=0.6, att=0.1, rel=0.5, voices=4)
    # basse / cordes
    bass_pattern(S, 'bass', inst.cello, bars_range(5, 40), [(0, 1.8, 'r', 1.0), (2, 1.8, '5', .8)], lo=38, hi=49, vel=0.8, att=0.05, rel=0.2)
    bass_pattern(S, 'bass', inst.cello, bars_range(1, 4), [(0, 1.8, 'r', 1.0), (2, 1.8, '5', .8)], lo=38, hi=49, vel=0.7, att=0.05, rel=0.2)
    pad_chords(S, 'strings', inst.strings, bars_range(1, 4), 50, 69, 4, 60, 0.45, att=0.4, rel=0.5)
    pad_chords(S, 'strings', inst.strings, bars_range(5, 12), 50, 69, 4, 60, 0.45, att=0.3, rel=0.5)
    pad_chords(S, 'strings', inst.strings, bars_range(13, 20) + bars_range(29, 36), 55, 74, 4, 64, 0.65, att=0.25, rel=0.5)
    pad_chords(S, 'strings', inst.strings, bars_range(21, 28), 50, 69, 4, 60, 0.4, att=0.5, rel=0.7)
    pad_chords(S, 'strings', inst.strings, bars_range(37, 40), 55, 74, 4, 64, 0.6, att=0.3, rel=0.7)
    pad_chords(S, 'choir', inst.choir, bars_range(13, 20) + bars_range(37, 40), 52, 72, 3, 62, 0.4, att=0.4, rel=0.6, vowel='o')
    # percussion
    S.pattern('perc', inst.taiko, bars_range(5, 12) + bars_range(21, 28), ["X.......x.......", "X.......x...x..."], 0.7, pitch=74, dur=1.2)
    S.pattern('perc', inst.taiko, bars_range(13, 20) + bars_range(29, 40), "X.......X...x.x.", 0.9, pitch=74, dur=1.2)
    S.pattern('perc', inst.snare, bars_range(13, 20) + bars_range(29, 40), "x.x.X.x.x.x.X.x.", 0.5, tone=210)
    S.pattern('perc', inst.hat, bars_range(13, 20) + bars_range(29, 36), "..o...o...o...o.", 0.4)
    S.pattern('perc', inst.tambourine, bars_range(21, 28), "....x.......x...", 0.4)
    snare_roll(S, 'perc', 12, 2, 2, 0.3, 0.8)
    snare_roll(S, 'perc', 28, 2, 2, 0.3, 0.8)
    snare_roll(S, 'perc', 40, 2, 2, 0.3, 0.9)
    for bb in (5, 13, 29):
        S.hit('fx', inst.crash, bb, 0, 0.9, 0, 0.8, dur=3.2)
    S.hit('fx', inst.crash, 21, 0, 0.5, 0, 0.7, dur=3.2)
    for bb in (12, 28, 40):
        S.hit('fx', inst.cymbal_swell, bb, 0, 0.7, 0, 0.8, dur=4 * S.spb)
    return S


def victory():
    S = Song('music_victory', 120, 15, seed=95)
    S.bus('perc', -4, hall=0.2, room=0.15)
    S.bus('bass', 0, hall=0.1, room=0.05, hp_hz=35)
    S.bus('strings', -4, hall=0.45)
    S.bus('violin', 0, hall=0.45)
    S.bus('brass', 0, hall=0.4, room=0.05)
    S.bus('horn', 0, hall=0.45)
    S.bus('choir', 2, hall=0.6)
    S.bus('bell', -2, hall=0.5)
    S.bus('fx', -3, hall=0.5)
    S.set_prog(1, "F F")
    S.set_prog(3, "F C Dm Bb")
    S.set_prog(7, "F C Bb C")
    S.set_prog(11, "Dm Bb F C")
    S.set_prog(15, "C")
    S.sections = [('fanfare', 1, 2), ('A', 3, 6), ('B', 7, 10), ('grand', 11, 14), ('tail', 15, 15)]
    F = "C5:.5 C5:.5 C5:.5 F5:1.5 R:1  A5:.5 A5:.5 A5:.5 C6:1.5 R:1"
    S.melody('brass', inst.brass, F, 1, vel=0.95, att=0.03, rel=0.2)
    S.melody('horn', inst.horn, F, 1, vel=0.7, transpose=-12, att=0.05, rel=0.25)
    A = "A4:1 C5:1 F5:1.5 E5:.5  G5:1 E5:1 C5:2  D5:1 F5:1 A5:1.5 G5:.5  F5:1 D5:1 Bb4:2"
    S.melody('violin', inst.strings, A, 3, vel=0.8, att=0.08, rel=0.3, voices=4, vcents=9)
    S.melody('horn', inst.horn, A, 3, vel=0.6, transpose=-12, att=0.08, rel=0.3)
    Bt = "A5:1 G5:1 F5:2  E5:1 G5:1 C6:2  D6:1 C6:1 Bb5:2  C6:1.5 G5:.5 E5:2"
    S.melody('brass', inst.brass, Bt, 7, vel=0.9, att=0.05, rel=0.25)
    S.melody('violin', inst.strings, Bt, 7, vel=0.7, att=0.06, rel=0.25, voices=5)
    S.melody('horn', inst.horn, Bt, 7, vel=0.7, transpose=-12, att=0.06, rel=0.3)
    G = "F5:2 A5:2  Bb5:1.5 A5:.5 F5:2  A5:1 C6:1 F6:2  E6:1.5 D6:.5 C6:2"
    S.melody('brass', inst.brass, G, 11, vel=0.95, att=0.05, rel=0.3)
    S.melody('violin', inst.strings, G, 11, vel=0.8, att=0.06, rel=0.3, voices=5)
    S.melody('choir', inst.choir, G, 11, vel=0.8, vowel='a', att=0.12, rel=0.4, voices=5)
    S.melody('horn', inst.horn, G, 11, vel=0.7, transpose=-12, att=0.06, rel=0.3)
    S.melody('bell', inst.bell, G, 11, vel=0.5, transpose=12, tau=0.6)
    S.melody('brass', inst.brass, "G5:2 C6:2", 15, vel=0.8, att=0.06, rel=0.5)
    S.melody('violin', inst.strings, "G5:2 C6:2", 15, vel=0.6, att=0.1, rel=0.5)
    bass_pattern(S, 'bass', inst.cello, bars_range(1, 15), [(0, 1.8, 'r', 1.0), (2, 1.8, '5', .8)], lo=36, hi=47, vel=0.8, att=0.05, rel=0.2)
    pad_chords(S, 'strings', inst.strings, bars_range(1, 6), 50, 69, 4, 60, 0.5, att=0.2, rel=0.5)
    pad_chords(S, 'strings', inst.strings, bars_range(7, 15), 55, 74, 4, 64, 0.65, att=0.2, rel=0.5)
    pad_chords(S, 'choir', inst.choir, bars_range(7, 10), 52, 72, 3, 62, 0.4, att=0.3, rel=0.5, vowel='o')
    S.hit('perc', inst.taiko, 1, 0, 1.0, 0, 0.9, pitch=87, dur=1.6)
    for i in range(8):
        S.hit('perc', inst.taiko, 2, 2 + i * 0.25, 0.4 + 0.08 * i, 0, 0.8, pitch=87, dur=0.8)
    S.pattern('perc', inst.taiko, bars_range(3, 6), "X.......x.......", 0.7, pitch=87, dur=1.2)
    S.pattern('perc', inst.taiko, bars_range(7, 15), "X.......X...x.x.", 0.9, pitch=87, dur=1.2)
    S.pattern('perc', inst.snare, bars_range(7, 15), "x.x.X.x.x.x.X.x.", 0.5, tone=210)
    snare_roll(S, 'perc', 10, 2, 2, 0.3, 0.9)
    for bb in (3, 7, 11):
        S.hit('fx', inst.crash, bb, 0, 0.9, 0, 0.8, dur=3.0)
    S.hit('fx', inst.crash, 1, 0, 0.7, 0, 0.8, dur=3.0)
    S.hit('fx', inst.cymbal_swell, 10, 0, 0.7, 0, 0.8, dur=4 * S.spb)
    return S


def defeat():
    S = Song('music_defeat', 64, 8, seed=97)
    S.bus('perc', -3, hall=0.4, room=0.1)
    S.bus('cello', 0, hall=0.5)
    S.bus('horn', 0, hall=0.55)
    S.bus('strings', -3, hall=0.6)
    S.bus('violin', -2, hall=0.6)
    S.bus('choir', 0, hall=0.7)
    S.bus('bass', 0, hall=0.2, hp_hz=30)
    S.bus('fx', -4, hall=0.6)
    S.set_prog(1, "Bm G Em F# Bm G Em F#")
    S.sections = [('all', 1, 8)]
    M = "F#4:2 D4:1 E4:1  B4:2 A4:1 G4:1  G4:2 E4:1 G4:1  C#5:2 A#4:2  D5:2 B4:2  B4:1 D5:1 G4:2  G4:1 B4:1 E5:2  A#4:2 C#5:2"
    S.melody('cello', inst.cello, M, 1, vel=0.85, att=0.2, rel=0.5, transpose=0)
    S.melody('horn', inst.horn, M, 1, vel=0.55, att=0.25, rel=0.6, transpose=0)
    S.melody('violin', inst.strings, M, 5, vel=0.45, att=0.3, rel=0.6, voices=3, transpose=12, vcents=10)
    pad_chords(S, 'strings', inst.strings, bars_range(1, 8), 46, 65, 4, 56, 0.5, dur_beats=4.4, att=0.9, rel=1.2, voices=4)
    pad_chords(S, 'choir', inst.choir, bars_range(1, 8), 52, 70, 3, 60, 0.4, dur_beats=4.4, att=1.0, rel=1.2, vowel='u')
    for b in bars_range(1, 8):
        S.note('bass', inst.sub_bass, S.chord(b).root_in(28, 40), b, 0, 4.2, 0.8, 0, 1.0, att=0.15)
        S.note('bass', inst.cello, S.chord(b).root_in(36, 47), b, 0, 4.2, 0.55, 0, 1.0, att=0.3, rel=0.6)
    S.pattern('perc', inst.taiko, bars_range(1, 8), ["X...............", "................", "X..........x....", "........x......."], 0.7, pitch=62, dur=2.2)
    S.hit('fx', inst.boom, 1, 0, 0.7, 0, 0.8, dur=3.5, pitch=38)
    S.hit('fx', inst.cymbal_swell, 8, 0, 0.5, 0, 0.7, dur=4 * S.spb)
    return S
