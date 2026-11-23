"""Musiques de combat : battle_1, battle_2, boss, chaos_thunder."""
from music_lib import *
import inst


def stereo_loop_noise(S, lo, hi, gain, seed, slope=0.0):
    r = np.random.default_rng(seed)
    n = S.L
    x = np.stack([bandnoise(n, r, lo, hi, slope), bandnoise(n, r, lo, hi, slope)], 1)
    return x * gain


def pad_chords(S, bus, fn, bars, lo, hi, n, center, vel, dur_beats=4.3, lead=0.15, **kw):
    prev = None
    for b in bars:
        prev = voice_lead(prev, S.chord(b), lo, hi, n, center)
        for p in prev:
            S.note(bus, fn, p, b, -lead, dur_beats + lead, vel, 0, 1.0, **kw)


def snare_roll(S, bus, bar, beat0, length_beats, vel0=0.3, vel1=0.9, step=0.25):
    steps = int(length_beats / step)
    for i in range(steps):
        v = vel0 + (vel1 - vel0) * i / max(steps - 1, 1)
        S.hit(bus, inst.snare, bar, beat0 + i * step, v, 0, 0.8, tone=200)


# =====================================================================================
def battle1():
    S = Song('music_battle_1', 140, 48, seed=51)
    S.bus('perc', -6, hall=0.12, room=0.2)
    S.bus('tom', -3, hall=0.1, room=0.2)
    S.bus('bass', 1, hall=0.05, room=0.08, hp_hz=35)
    S.bus('strings', -5, hall=0.4)
    S.bus('brass', 0, hall=0.3, room=0.05)
    S.bus('horn', 0, hall=0.35)
    S.bus('choir', 2, hall=0.55)
    S.bus('violin', -1, hall=0.4)
    S.bus('fx', -3, hall=0.45)
    S.set_prog(1, "Em Em C B")
    S.set_prog(5, "Em C D B Em C D B")
    S.set_prog(13, "Am Em C D Am Em B B")
    S.set_prog(21, "Em C D B Em C D B")
    S.set_prog(29, "Em C Am B Em C Am B")
    S.set_prog(37, "Am Em C D Am Em B B")
    S.set_prog(45, "Em Em C B")
    S.sections = [('intro', 1, 4), ('A', 5, 12), ('B', 13, 20), ("A2", 21, 28), ('break', 29, 36), ("B2", 37, 44), ('outro', 45, 48)]
    OST = [(0, .4, 0, 1.0), (.5, .4, 0, .6), (1, .4, 0, .8), (1.5, .4, 12, .7), (2, .4, 0, 1.0), (2.5, .4, 0, .6), (3, .4, 0, .8), (3.5, .4, 12, .7)]
    drive = bars_range(5, 28) + bars_range(37, 46)
    ostinato(S, 'bass', inst.cello, drive, OST, lo=34, hi=45, vel=0.85, att=0.02, rel=0.08)
    for b in bars_range(1, 48):
        if 29 <= b <= 36 or True:
            S.note('bass', inst.sub_bass, S.chord(b).root_in(28, 39), b, 0, 4.0, 0.7, 0, 1.0)
    # percussion
    S.pattern('perc', inst.taiko, bars_range(1, 4), ["X...x...X...x...", "X...x...X...x...", "X...x...X..xx.xx", "X...X...X...XXXX"], 0.8, pitch=85, dur=1.0)
    S.pattern('perc', inst.taiko, drive, "X..x..x.X..x..x.", 0.85, pitch=82, dur=0.9)
    S.pattern('perc', inst.taiko, bars_range(29, 36), ["X.......x.......", "X.......x...x.x."], 0.8, pitch=80, dur=1.4)
    S.pattern('perc', inst.taiko, [47, 48], ["X...x...X...x...", "X...X...XXXXXXXX"], 0.9, pitch=84, dur=1.0)
    S.pattern('tom', inst.tom, [4, 12, 20, 28, 36, 44], "............xxXX", 0.8, pitch=130)
    S.pattern('tom', inst.tom, bars_range(13, 20) + bars_range(37, 44), "....o.......o.o.", 0.6, pitch=170)
    S.pattern('perc', inst.snare, bars_range(13, 20) + bars_range(37, 44) + bars_range(21, 28), "....x.......x...", 0.55, tone=210)
    S.pattern('perc', inst.hat, bars_range(13, 28) + bars_range(37, 44), "x.o.x.o.x.o.x.o.", 0.5)
    snare_roll(S, 'perc', 36, 0, 4, 0.2, 0.9)
    snare_roll(S, 'perc', 12, 2, 2, 0.3, 0.8)
    snare_roll(S, 'perc', 28, 2, 2, 0.3, 0.8)
    snare_roll(S, 'perc', 44, 2, 2, 0.3, 0.8)
    for bb in (5, 13, 21, 37, 45):
        S.hit('fx', inst.crash, bb, 0, 0.85, 0, 0.8, dur=3.0)
    S.hit('fx', inst.crash, 29, 0, 0.6, 0, 0.7, dur=3.0)
    for bb in (4, 12, 28, 36, 44):
        S.hit('fx', inst.riser, bb, 0, 0.7, 0, 0.7, dur=4 * S.spb, lo=250, hi=6000)
    S.hit('fx', inst.boom, 1, 0, 0.9, 0, 0.9, dur=3.0, pitch=42)
    # cordes
    pad_chords(S, 'strings', inst.strings, bars_range(1, 4), 50, 69, 4, 60, 0.45, att=0.8, rel=0.8, voices=4)
    pad_chords(S, 'strings', inst.strings, bars_range(13, 20) + bars_range(37, 44), 55, 74, 4, 64, 0.65, att=0.3, rel=0.5)
    pad_chords(S, 'strings', inst.strings, bars_range(21, 28), 55, 74, 4, 64, 0.55, att=0.3, rel=0.5)
    pad_chords(S, 'strings', inst.strings, bars_range(45, 48), 50, 69, 4, 60, 0.5, att=0.5, rel=0.8)
    # tremolo staccato (break)
    for b in bars_range(29, 36):
        ch = S.chord(b)
        for i in range(8):
            S.note('strings', inst.strings, ch.root_in(52, 63) + (12 if i % 2 else 0), b, i * .5, .45, 0.4, 0, 1.0, att=0.02, rel=0.08, voices=3)
    # mélodies
    A = "E4:1 E4:.5 G4:.5 B4:1 A4:.5 G4:.5  C5:1.5 B4:.5 G4:1 E4:1  D5:1 A4:.5 D5:.5 F#5:1 E5:.5 D5:.5  B4:1 D#5:1 F#5:2  E4:1 E4:.5 G4:.5 B4:1 A4:.5 G4:.5  C5:1 E5:1 G5:1 E5:1  D5:1 F#5:1 A5:1 F#5:1  F#5:1 D#5:1 B4:2"
    S.melody('brass', inst.brass, A, 5, vel=0.85, att=0.04, rel=0.12)
    S.melody('horn', inst.horn, A, 5, vel=0.6, transpose=-12, att=0.05, rel=0.15)
    S.melody('brass', inst.brass, A, 21, vel=0.9, att=0.04, rel=0.12)
    S.melody('horn', inst.horn, A, 21, vel=0.65, transpose=-12, att=0.05, rel=0.15)
    S.melody('violin', inst.strings, A, 21, vel=0.45, transpose=12, att=0.04, rel=0.1, voices=3)
    B = "A4:1.5 C5:.5 E5:2  E5:1.5 D5:.5 B4:2  C5:1 E5:1 G5:2  F#5:1.5 A5:.5 F#5:2  A5:1.5 G5:.5 E5:1 C5:1  B4:1 E5:1 G5:1 B5:1  D#5:2 F#5:2  B5:1 F#5:1 D#5:2"
    for st in (13, 37):
        S.melody('brass', inst.brass, B, st, vel=0.9, att=0.05, rel=0.2)
        S.melody('choir', inst.choir, B, st, vel=0.85, vowel='a', att=0.12, rel=0.3, voices=5)
        S.melody('horn', inst.horn, B, st, vel=0.65, transpose=-12, att=0.06, rel=0.2)
    BR = "B4:2 E5:2  G5:2 E5:2  E5:2 C5:2  D#5:2 F#5:2  B4:2 E5:2  G5:2 C6:2  A5:2 E5:2  F#5:1 D#5:1 B4:2"
    S.melody('violin', inst.strings, BR, 29, vel=0.7, att=0.12, rel=0.3, voices=4, vcents=10)
    S.melody('choir', inst.choir, BR, 29, vel=0.35, vowel='u', att=0.3, rel=0.5, transpose=-12)
    S.melody('brass', inst.brass, "E5:4 G5:2 E5:2 C5:2 G4:2 D#5:2 F#5:2", 45, vel=0.8, att=0.05, rel=0.3)
    # chœur : accords scandés (A2)
    for b in bars_range(21, 28, ):
        if b % 2 == 1:
            for p in S.chord(b).voicing_near(64, 3):
                S.note('choir', inst.choir, p, b, 0, 1.5, 0.7, 0, 1.0, vowel='o', att=0.05, rel=0.3, voices=4)
    return S


def bars_range(a, b, step=1):
    return list(range(a, b + 1, step))


# =====================================================================================
def battle2():
    S = Song('music_battle_2', 152, 56, seed=61)
    S.bus('perc', -5, hall=0.1, room=0.22)
    S.bus('tom', -5, hall=0.1, room=0.22)
    S.bus('bass', 1, hall=0.05, room=0.08, hp_hz=35)
    S.bus('oud', 5, hall=0.2, room=0.12)
    S.bus('strings', -5, hall=0.4)
    S.bus('brass', 0, hall=0.3, room=0.05)
    S.bus('horn', 0, hall=0.35)
    S.bus('choir', 1, hall=0.5)
    S.bus('fx', -3, hall=0.45)
    S.set_prog(1, "A5 A5 Bb5 A5")
    S.set_prog(5, "A5 Bb5 A5 Bb5 A5 Bb5 G5 A5")
    S.set_prog(13, "Dm A Bb A Dm A Bb A")
    S.set_prog(21, "A5 Bb5 A5 Bb5 A5 Bb5 G5 A5")
    S.set_prog(29, "A5 A5 Bb5 Bb5 G5 G5 A5 A5")
    S.set_prog(37, "Dm A Bb A Dm A Bb A")
    S.set_prog(45, "A5 Bb5 A5 Bb5 A5 Bb5 G5 A5")
    S.set_prog(53, "A5 Bb5 G5 A5")
    S.sections = [('intro', 1, 4), ('A', 5, 12), ('B', 13, 20), ('A', 21, 28), ('C', 29, 36), ('B', 37, 44), ("A'", 45, 52), ('outro', 53, 56)]
    A_bars = bars_range(5, 12) + bars_range(21, 28) + bars_range(45, 52)
    B_bars = bars_range(13, 20) + bars_range(37, 44)
    C_bars = bars_range(29, 36)
    OST = [(0, .3, 12, 1.0), (.5, .3, 12, .6), (1, .3, 19, .8), (1.5, .3, 12, .6), (2, .3, 24, .9), (2.5, .3, 12, .6), (3, .3, 19, .8), (3.5, .3, 12, .6)]
    ostinato(S, 'oud', inst.oud, A_bars + bars_range(1, 4) + bars_range(53, 56), OST, lo=45, hi=56, vel=0.7, t60=0.7)
    OST2 = [(i * .5, .3, [12, 12, 19, 12, 12, 24, 19, 12][i], 1.0 if i % 2 == 0 else .6) for i in range(8)]
    ostinato(S, 'oud', inst.oud, B_bars, OST2, lo=45, hi=56, vel=0.55, t60=0.7)
    for b in bars_range(1, 56):
        S.note('bass', inst.sub_bass, S.chord(b).root_in(28, 39), b, 0, 4.0, 0.75, 0, 1.0)
    # basse rythmique
    bass_pattern(S, 'bass', inst.bass_pick, A_bars + B_bars, [(0, .5, 'r', 1.0), (1.5, .4, 'r', .7), (2, .5, 'r', .9), (3.5, .4, '5', .6)], lo=33, hi=44, vel=0.75)
    # percussions tribales
    allp = bars_range(5, 52)
    S.pattern('tom', inst.tom, A_bars + B_bars, "X..x..x.X..x.x..", 0.9, pitch=100)
    S.pattern('tom', inst.tom, A_bars + B_bars, "....o.......o.o.", 0.65, pitch=155)
    S.pattern('tom', inst.tom, C_bars, ["X..x..x.X..x.x..", "X.xx..x.X.xx.xxX", "X..x..x.X..x.x..", "x.xxxxxx..X..x.x"], 0.95, pitch=95)
    S.pattern('tom', inst.tom, C_bars, "..x...x...x...x.", 0.6, pitch=150)
    S.pattern('perc', inst.taiko, A_bars + B_bars, "X.......X.......", 0.85, pitch=84, dur=1.0)
    S.pattern('perc', inst.taiko, bars_range(1, 4), ["X...x...X...x...", "X...x...X...x...", "X...x...X..xx.xx", "X...X...XXXXXXXX"], 0.8, pitch=84, dur=1.0)
    S.pattern('perc', inst.frame_drum, A_bars + B_bars + C_bars, "..x...x...x...x.", 0.55, pitch=125)
    S.pattern('perc', inst.shaker, A_bars + B_bars + C_bars, "xoxoxoxoxoxoxoxo", 0.4)
    S.pattern('perc', inst.tambourine, B_bars, "....x.......x...", 0.45)
    S.pattern('perc', inst.taiko, bars_range(53, 56), ["X...x...X...x...", "X...x...X...x...", "X..x..x.X..x..x.", "X.......X..."], 0.85, pitch=84, dur=1.2)
    for bb in (5, 13, 21, 29, 37, 45):
        S.hit('fx', inst.crash, bb, 0, 0.8, 0, 0.8, dur=3.0)
    for bb in (4, 12, 20, 28, 36, 44, 52):
        S.hit('fx', inst.riser, bb, 0, 0.65, 0, 0.7, dur=4 * S.spb, lo=250, hi=6000)
    snare_roll(S, 'perc', 36, 2, 2, 0.3, 0.9)
    snare_roll(S, 'perc', 28, 2, 2, 0.3, 0.8)
    S.hit('fx', inst.boom, 1, 0, 0.9, 0, 0.9, dur=3.0, pitch=44)
    # nappes
    pad_chords(S, 'strings', inst.strings, bars_range(1, 4) + bars_range(53, 56), 50, 69, 3, 58, 0.5, att=0.7, rel=0.8, voices=4)
    pad_chords(S, 'strings', inst.strings, A_bars, 50, 69, 3, 58, 0.4, att=0.3, rel=0.5)
    pad_chords(S, 'strings', inst.strings, B_bars, 55, 74, 4, 64, 0.6, att=0.3, rel=0.5)
    # mélodies (gamme dominante phrygienne)
    A = "E5:1 E5:.5 F5:.5 E5:1 C#5:1  D5:1.5 C#5:.5 D5:1 F5:1  E5:1 E5:.5 F5:.5 E5:1 A5:1  G5:1 F5:1 D5:2  E5:.5 F5:.5 E5:.5 C#5:.5 A4:1 C#5:1  D5:1 F5:1 G5:2  B4:1 D5:1 G5:2  E5:2 C#5:1 A4:1"
    for st in (5, 21):
        S.melody('brass', inst.brass, A, st, vel=0.85, att=0.04, rel=0.12)
        S.melody('horn', inst.horn, A, st, vel=0.6, transpose=-12, att=0.05, rel=0.15)
    S.melody('brass', inst.brass, A, 45, vel=0.9, att=0.04, rel=0.12)
    S.melody('horn', inst.horn, A, 45, vel=0.65, transpose=-12, att=0.05, rel=0.15)
    S.melody('oud', inst.oud, A, 45, vel=0.7, transpose=12, t60=1.2)
    B = "A5:1.5 G5:.5 F5:1 D5:1  E5:1.5 F5:.5 E5:1 C#5:1  D5:1.5 F5:.5 Bb5:2  C#5:1 E5:1 A5:2  A5:1.5 G5:.5 F5:1 D5:1  E5:1.5 F5:.5 E5:1 C#5:1  D5:1 F5:1 G5:2  A5:1 G5:.5 F5:.5 E5:2"
    for st in (13, 37):
        S.melody('brass', inst.brass, B, st, vel=0.9, att=0.05, rel=0.2)
        S.melody('choir', inst.choir, B, st, vel=0.8, vowel='a', att=0.12, rel=0.3, voices=5)
        S.melody('horn', inst.horn, B, st, vel=0.6, transpose=-12, att=0.06, rel=0.2)
    Cm = "A4:.5 Bb4:.5 C#5:.5 D5:.5 E5:1 F5:.5 E5:.5  D5:.5 C#5:.5 Bb4:.5 A4:.5 G4:.5 C#5:.5 E5:1  D5:1 F5:1 Bb5:1 F5:1  G5:1 F5:1 D5:2  G4:1 B4:1 D5:2  G5:1 F5:.5 E5:.5 D5:2  E5:1 F5:.5 E5:.5 C#5:1 A4:1  A4:.5 C#5:.5 E5:.5 A5:.5 E5:2"
    S.melody('oud', inst.oud, Cm, 29, vel=0.95, t60=1.3)
    S.melody('oud', inst.oud, Cm, 29, vel=0.4, transpose=12, t60=1.3)
    S.melody('brass', inst.brass, "E5:2 C#5:2  D5:2 F5:2  G5:2 D5:2  A4:4", 53, vel=0.8, att=0.05, rel=0.3)
    S.melody('choir', inst.choir, "A4:16", 53, vel=0.4, vowel='u', att=0.5, rel=1.0) if False else None
    return S


# =====================================================================================
def boss():
    S = Song('music_battle_boss', 96, 36, seed=71)
    S.bus('perc', -5, hall=0.2, room=0.2)
    S.bus('tom', 0, hall=0.15, room=0.2)
    S.bus('bass', 1, hall=0.05, room=0.06, hp_hz=30)
    S.bus('strings', -4, hall=0.45)
    S.bus('brass', 0, hall=0.4, room=0.05)
    S.bus('horn', 1, hall=0.45)
    S.bus('choir', 3, hall=0.6)
    S.bus('fx', -2, hall=0.5)
    S.set_prog(1, "Cm Cm Ab G")
    S.set_prog(5, "Cm Cm Ab Bb Cm Fm Db G")
    S.set_prog(13, "Ab Eb Bb Fm Ab Eb G G")
    S.set_prog(21, "Fm Cm Db G Fm G")
    S.set_prog(27, "Cm Cm Ab Bb Cm Fm Db G")
    S.set_prog(35, "Cm G")
    S.sections = [('intro', 1, 4), ('A', 5, 12), ('B', 13, 20), ('C', 21, 26), ("A'", 27, 34), ('outro', 35, 36)]
    A_b = bars_range(5, 12) + bars_range(27, 34)
    OST = [(0, .4, 12, 1.0), (.5, .4, 12, .6), (1, .4, 19, .8), (1.5, .4, 12, .6), (2, .4, 12, 1.0), (2.5, .4, 12, .6), (3, .4, 15, .8), (3.5, .4, 12, .6)]
    ostinato(S, 'bass', inst.cello, A_b + bars_range(13, 20), OST, lo=34, hi=45, vel=0.8, att=0.02, rel=0.08)
    for b in bars_range(1, 36):
        S.note('bass', inst.sub_bass, S.chord(b).root_in(24, 35), b, 0, 4.1, 0.85, 0, 1.0, att=0.08)
    # cors graves : motif
    A = "C3:1 C3:.5 Eb3:.5 G3:1 F3:.5 Eb3:.5  C3:1 C3:.5 Eb3:.5 G3:1 Bb3:1  Ab3:1 Ab3:.5 C4:.5 Eb4:2  Bb3:1 D4:1 F4:2  C3:1 C3:.5 Eb3:.5 G3:1 F3:.5 Eb3:.5  F3:1 F3:.5 Ab3:.5 C4:2  Db3:1 F3:1 Ab3:2  G3:1 B3:1 D4:2"
    for st in (5, 27):
        S.melody('brass', inst.brass, A, st, vel=0.9, att=0.06, rel=0.2, bright=0.6)
        S.melody('horn', inst.horn, A, st, vel=0.8, transpose=-12, att=0.08, rel=0.25)
    Bm = "Eb5:2 C5:1 Eb5:1  Bb4:2 G4:1 Bb4:1  D5:2 F5:1 D5:1  C5:2 Ab4:1 C5:1  Eb5:1.5 F5:.5 Eb5:1 C5:1  G5:2 Bb5:1 G5:1  D5:1 G5:1 B5:2  B5:1 A5:1 G5:2"
    S.melody('choir', inst.choir, Bm, 13, vel=0.95, vowel='a', att=0.12, rel=0.3, voices=6)
    S.melody('choir', inst.choir, Bm, 13, vel=0.7, vowel='o', att=0.12, rel=0.3, voices=4, transpose=-12)
    S.melody('brass', inst.brass, Bm, 13, vel=0.8, att=0.06, rel=0.2, transpose=-12)
    S.melody('horn', inst.horn, Bm, 13, vel=0.75, att=0.08, rel=0.25, transpose=-24)
    # A' : chœur en doublure
    S.melody('choir', inst.choir, A, 27, vel=0.55, vowel='o', att=0.1, rel=0.3, voices=5, transpose=12)
    Cb = "Ab4:4  G4:4  F4:4  D4:2 B3:2  Ab4:4  B4:4"
    S.melody('choir', inst.choir, Cb, 21, vel=0.85, vowel='o', att=0.6, rel=0.8, voices=5)
    S.melody('horn', inst.horn, Cb, 21, vel=0.6, att=0.3, rel=0.6, transpose=-12)
    S.melody('brass', inst.brass, "C4:4  D4:4", 35, vel=0.85, att=0.1, rel=0.6)
    S.melody('choir', inst.choir, "C5:4  B4:4", 35, vel=0.7, vowel='a', att=0.2, rel=1.0)
    # cordes
    pad_chords(S, 'strings', inst.strings, bars_range(1, 4), 48, 67, 4, 58, 0.45, att=0.9, rel=0.9, voices=4)
    pad_chords(S, 'strings', inst.strings, A_b, 50, 69, 4, 60, 0.45, att=0.4, rel=0.6)
    pad_chords(S, 'strings', inst.strings, bars_range(13, 20), 55, 74, 4, 64, 0.7, att=0.3, rel=0.6)
    pad_chords(S, 'strings', inst.strings, bars_range(21, 26), 50, 69, 4, 60, 0.4, att=0.7, rel=0.9)
    pad_chords(S, 'strings', inst.strings, bars_range(35, 36), 50, 69, 4, 60, 0.5, att=0.5, rel=1.0)
    # chœur 'oo' (intro)
    pad_chords(S, 'choir', inst.choir, bars_range(1, 4), 52, 70, 3, 60, 0.35, att=1.0, rel=1.0, vowel='u')
    # percussions
    S.hit('fx', inst.boom, 1, 0, 1.0, 0, 1.0, dur=3.5, pitch=40)
    for bb in (5, 13, 27):
        S.hit('fx', inst.boom, bb, 0, 0.9, 0, 0.9, dur=3.0, pitch=42)
        S.hit('fx', inst.crash, bb, 0, 0.9, 0, 0.8, dur=3.5)
    S.pattern('perc', inst.taiko, bars_range(1, 4), ["X...............", "........x.......", "X..x............", "X.......x..x.x.."], 0.85, pitch=70, dur=2.0)
    S.pattern('perc', inst.taiko, A_b, ["X.......X...x...", "X.......X..x.x.."], 0.9, pitch=74, dur=1.6)
    S.pattern('perc', inst.taiko, bars_range(13, 20), "X..x....X..x.x..", 1.0, pitch=72, dur=1.4)
    S.pattern('tom', inst.tom, bars_range(13, 20) + A_b, "....o.......o.o.", 0.6, pitch=105)
    S.pattern('perc', inst.taiko, bars_range(21, 26), ["X...............", "........x......."], 0.7, pitch=68, dur=2.0)
    S.pattern('perc', inst.taiko, bars_range(35, 36), ["X.......x..x.x..", "X...XXXXXXXXXXXX"], 0.9, pitch=72, dur=1.6)
    S.pattern('perc', inst.snare, bars_range(13, 20) + bars_range(27, 34), "....x.......x...", 0.5, tone=170)
    snare_roll(S, 'perc', 12, 2, 2, 0.3, 0.8)
    snare_roll(S, 'perc', 26, 0, 4, 0.2, 0.95)
    snare_roll(S, 'perc', 20, 2, 2, 0.3, 0.8)
    for bb in (12, 26):
        S.hit('fx', inst.riser, bb if bb == 12 else 26, 0, 0.75, 0, 0.8, dur=4 * S.spb, lo=200, hi=6000)
    S.hit('fx', inst.cymbal_swell, 12, 0, 0.7, 0, 0.8, dur=4 * S.spb)
    return S


# =====================================================================================
def chaos():
    S = Song('music_chaos_thunder', 132, 48, seed=81)
    S.bus('kick', -8, hall=0.05, room=0.1)
    S.bus('perc', 0, hall=0.12, room=0.2)
    S.bus('bass', 1, hall=0.03, room=0.05, hp_hz=32)
    S.bus('arp', 2, hall=0.3, room=0.1)
    S.bus('lead', 2, hall=0.35, room=0.08)
    S.bus('pad', -6, hall=0.5)
    S.bus('choir', 1, hall=0.6)
    S.bus('fx', -2, hall=0.5)
    S.bus('rain', -4, hall=0.1)
    S.set_prog(1, "Fm Fm Db C")
    S.set_prog(5, "Fm Db Ab Eb Fm Db Ab C")
    S.set_prog(13, "Fm Db Bbm C Fm Db Bbm C")
    S.set_prog(21, "Db Ab Eb C Db Ab Eb C")
    S.set_prog(29, "Fm Db Ab Eb Fm Db Ab C")
    S.set_prog(37, "Fm Db Bbm C Fm Db Bbm C")
    S.set_prog(45, "Fm Db Eb C")
    S.sections = [('intro', 1, 4), ('A', 5, 12), ('B', 13, 20), ('break', 21, 28), ("A'", 29, 36), ("B'", 37, 44), ('outro', 45, 48)]
    A_b = bars_range(5, 12) + bars_range(29, 36)
    B_b = bars_range(13, 20) + bars_range(37, 44)
    drive = A_b + B_b
    OST = [(0, .45, 0, 1.0), (.5, .45, 0, .6), (1, .45, 0, .8), (1.5, .45, 12, .7), (2, .45, 0, 1.0), (2.5, .45, 0, .6), (3, .45, 0, .8), (3.5, .45, 12, .7)]
    ostinato(S, 'bass', inst.bass_pick, drive, OST, lo=29, hi=40, vel=0.85)
    for b in bars_range(1, 48):
        S.note('bass', inst.sub_bass, S.chord(b).root_in(24, 35), b, 0, 4.0, 0.7, 0, 1.0)
    # arpèges 16es (filtre qui s'ouvre)
    P16 = [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 4, 3, 2, 1, 2]
    for b in bars_range(1, 48):
        if b in (1, 2):
            continue
        base_c = 1800 + 90 * b if b < 21 else (1500 if b < 29 else 2600)
        v = 0.4 if b < 5 or b > 44 else (0.5 if 21 <= b <= 28 else 0.6)
        arp_pattern(S, 'arp', inst.synth_pluck, [b], P16, 0.25, lo=53, n_oct=3, vel=v, from_root=True, cutoff=base_c, dur_mult=0.9, accent=(1.0, 0.55, 0.75, 0.55))
    # mélodies synthé
    LA = "C5:1.5 Ab4:.5 F4:2  Db5:1.5 Ab4:.5 F4:2  Eb5:1.5 C5:.5 Ab4:2  Bb4:1.5 G4:.5 Eb4:2  C5:1.5 Ab4:.5 F4:2  Db5:1.5 F5:.5 Ab5:2  Eb5:1.5 C5:.5 Ab4:2  G4:1.5 C5:.5 E5:2"
    S.melody('lead', inst.synth_lead, LA, 29, vel=0.7, cutoff=2600, att=0.01, rel=0.12)
    S.melody('lead', inst.synth_lead, LA, 5, vel=0.6, cutoff=2000, att=0.01, rel=0.12)
    LB = "C5:1 C5:.5 Db5:.5 C5:1 Ab4:1  Db5:1 F5:1 Ab5:2  F5:1.5 Eb5:.5 Db5:1 Bb4:1  E5:1 G5:1 C6:2  F5:1 Ab5:1 C6:2  Db6:1 Bb5:1 Ab5:2  F5:1 Db5:1 Bb4:2  G4:1 C5:1 E5:2"
    for st in (13, 37):
        S.melody('lead', inst.synth_lead, LB, st, vel=0.85, cutoff=3200, att=0.01, rel=0.15)
    S.melody('choir', inst.choir, LB, 37, vel=0.7, vowel='a', att=0.1, rel=0.3, voices=5)
    S.melody('lead', inst.synth_lead, "C5:4 Ab4:2 F4:2 Db5:2 F5:2 E5:2 G4:2", 45, vel=0.75, cutoff=2400)
    # break : nappe sombre + chœur
    pad_chords(S, 'pad', inst.pad, bars_range(21, 28), 48, 70, 4, 58, 0.5, att=1.0, rel=1.2, bright=1200)
    pad_chords(S, 'choir', inst.choir, bars_range(21, 28), 52, 72, 3, 62, 0.4, att=0.8, rel=1.0, vowel='o')
    pad_chords(S, 'pad', inst.pad, bars_range(1, 4), 48, 70, 4, 58, 0.4, att=1.0, rel=1.2, bright=900)
    pad_chords(S, 'pad', inst.pad, B_b + A_b + bars_range(45, 48), 48, 70, 4, 58, 0.35, att=0.4, rel=0.6, bright=1600)
    # batterie
    KICK = "X.....x.X.....x."
    S.pattern('kick', inst.kick, drive, "X...X...X...X...", 0.9)
    S.pattern('kick', inst.kick, B_b, "X.x.X...X.x.X.x.", 0.9)
    S.pattern('kick', inst.kick, bars_range(3, 4) + bars_range(21, 28) + bars_range(45, 48), "X.......X.......", 0.8)
    S.pattern('perc', inst.snare, drive, "....X.......X...", 0.8, tone=200)
    S.pattern('perc', inst.hat, drive, "x.o.x.o.x.o.x.o.", 0.5)
    S.pattern('perc', inst.hat, B_b, "xoxoxoxoxoxoxoxo", 0.5)
    S.pattern('perc', inst.taiko, B_b, "X.......X.......", 0.7, pitch=78, dur=1.2)
    S.pattern('perc', inst.taiko, bars_range(21, 28), ["X...............", "........x......."], 0.7, pitch=70, dur=1.6)
    S.pattern('perc', inst.snare, [4, 12, 20, 28, 36, 44], "............xxXX", 0.8, tone=200)
    snare_roll(S, 'perc', 28, 0, 4, 0.2, 0.95)
    for bb in (5, 13, 29, 37):
        S.hit('fx', inst.crash, bb, 0, 0.85, 0, 0.8, dur=3.0)
    for bb in (4, 12, 20, 36, 44):
        S.hit('fx', inst.riser, bb, 0, 0.7, 0, 0.7, dur=4 * S.spb, lo=250, hi=7000)
    S.hit('fx', inst.riser, 24, 0, 0.6, 0, 0.7, dur=16 * S.spb, lo=200, hi=6000) if False else None
    S.hit('fx', inst.riser, 25, 0, 0.8, 0, 0.8, dur=16 * S.spb, lo=200, hi=7000)
    # orage : grondements + éclairs + pluie
    for bb, pan_ in ((1, -0.4), (9, 0.5), (21, -0.3), (25, 0.4), (33, -0.5), (41, 0.3), (47, 0.0)):
        S.hit('fx', inst.thunder_rumble, bb, 0, 0.9, pan_, 1.0, dur=3.8)
    for bb, bt, pan_ in ((1, 0, 0.5), (5, 0, -0.6), (13, 0, 0.4), (21, 0, -0.5), (25, 2, 0.6), (29, 0, 0.0), (37, 0, -0.3), (41, 2, 0.5), (47, 2, 0.0)):
        S.hit('fx', inst.zap, bb, bt, 0.9, pan_, 1.0, dur=0.6)
    rain = stereo_loop_noise(S, 2500, 9500, 0.045, 3, -2.0)
    env = 0.7 + 0.3 * slow_rand(S.L, np.random.default_rng(9), 0.2)
    S.add('rain', rain * env[:, None], 0.0)
    return S
