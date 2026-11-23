"""Musiques : menu, club, draft, chest."""
from music_lib import *
import inst


def sec_vel(bar, table, default=0.6):
    for (a, b), v in table.items():
        if a <= bar <= b:
            return v
    return default


# =====================================================================================
def menu():
    S = Song('music_menu', 72, 30, seed=11)
    S.bus('strings', -6, hall=0.55, room=0.05)
    S.bus('violin', -1, hall=0.55)
    S.bus('cello', -1, hall=0.35)
    S.bus('horn', 3, hall=0.5)
    S.bus('brass', -2, hall=0.45)
    S.bus('choir', 4, hall=0.65)
    S.bus('harp', 9, hall=0.45)
    S.bus('perc', -2, hall=0.3, room=0.06)
    S.bus('fx', -4, hall=0.4)
    S.set_prog(1, "Dm Dm Bb C")
    S.set_prog(5, "Dm Dm Bb C Dm Gm Bb A")
    S.set_prog(13, "Bb F Gm A Bb C Dm A")
    S.set_prog(21, "Gm Dm Bb F Gm A")
    S.set_prog(27, "Dm Bb C A")
    S.sections = [('intro', 1, 4), ('A', 5, 12), ('B', 13, 20), ('C', 21, 26), ('outro', 27, 30)]
    allb = bars_range(1, 30)
    vel_str = {(1, 4): 0.45, (5, 12): 0.55, (13, 20): 0.8, (21, 26): 0.5, (27, 30): 0.55}
    # cordes : nappes conduites
    prev = None
    for b in allb:
        v = sec_vel(b, vel_str)
        ch = S.chord(b)
        prev = voice_lead(prev, ch, 50, 69, 4, 60)
        for p in prev:
            S.note('strings', inst.strings, p, b, -0.3, 4.9, v, 0.0, 1.0, att=0.55, rel=0.9)
    # violoncelle : fondamentale tenue
    for b in allb:
        ch = S.chord(b)
        S.note('cello', inst.cello, ch.root_in(38, 50), b, 0, 4.1, 0.6 if b < 13 else 0.8, 0.0, 1.0, att=0.3, rel=0.5)
    # ostinato violoncelle (A)
    ostinato(S, 'cello', inst.cello, bars_range(5, 12),
             [(0, .45, 12, 1.0), (.5, .45, 19, .6), (1, .45, 24, .8), (1.5, .45, 19, .6),
              (2, .45, 12, .9), (2.5, .45, 19, .6), (3, .45, 24, .8), (3.5, .45, 19, .6)], lo=38, hi=50, vel=0.5, att=0.03, rel=0.1)
    # ostinato cordes staccato (B)
    ostinato(S, 'strings', inst.strings, bars_range(13, 20),
             [(i * .5, .4, 12 + (7 if i % 4 == 2 else 0), 1.0 if i % 2 == 0 else .7) for i in range(8)],
             lo=50, hi=62, vel=0.45, att=0.02, rel=0.08, voices=3)
    # cors graves en B
    for b in bars_range(13, 20):
        ch = S.chord(b)
        S.note('horn', inst.horn, ch.root_in(41, 53), b, 0, 4.0, 0.75, 0, 1.0, att=0.25, rel=0.6)
    # chœur : nappe 'oo' (intro, pont, outro)
    for rng_, vv in ((bars_range(1, 4), 0.5), (bars_range(21, 26), 0.55), (bars_range(27, 30), 0.55)):
        prev = None
        for b in rng_:
            prev = voice_lead(prev, S.chord(b), 55, 74, 3, 64)
            for p in prev:
                S.note('choir', inst.choir, p, b, -0.2, 4.6, vv * 0.7, 0, 1.0, vowel='u', att=0.8, rel=1.0, voices=4)
    # mélodies
    A = "D4:2 F4:1 A4:1  A4:1.5 G4:.5 F4:1 D4:1  D5:2 C5:1 Bb4:1  E5:1.5 D5:.5 C5:1 G4:1  D5:2 A4:1 F4:1  G4:1.5 Bb4:.5 D5:1 C5:1  D5:1 F5:1 D5:1 Bb4:1  A4:1 C#5:1 E5:2"
    S.melody('horn', inst.horn, A, 5, vel=0.8, att=0.12, rel=0.35)
    S.melody('horn', inst.horn, "D5:3 C5:1  G4:4", 3, vel=0.55, att=0.2, rel=0.6)
    B = "F5:2 D5:1 F5:1  A5:2 G5:1 F5:1  G5:1.5 F5:.5 D5:1 Bb4:1  E5:1 A5:2 E5:1  F5:2 D5:1 F5:1  G5:2 E5:1 G5:1  A5:1.5 G5:.5 F5:1 D5:1  E5:2 C#5:1 E5:1"
    S.melody('choir', inst.choir, B, 13, vel=0.95, vowel='a', att=0.18, rel=0.5, voices=5)
    S.melody('brass', inst.brass, B, 13, vel=0.7, att=0.06, rel=0.3, transpose=-12)
    S.melody('horn', inst.horn, B, 13, vel=0.7, att=0.1, rel=0.3, transpose=-12)
    C = "Bb4:2 D5:2  A4:2 F4:1 A4:1  D5:2 F5:2  C5:2 A4:1 C5:1  Bb4:1 D5:1 G5:2  E5:2 A5:2"
    S.melody('violin', inst.strings, C, 21, vel=0.7, att=0.18, rel=0.5, voices=3, vcents=9)
    O = "D5:3 C5:1  Bb4:3 C5:1  G4:2 E4:2  C#5:2 E5:2"
    S.melody('horn', inst.horn, O, 27, vel=0.75, att=0.14, rel=0.5)
    # harpe
    arp_pattern(S, 'harp', inst.harp, [3, 4], [0, 1, 2, 3, 2, 1, 3, 2], 0.5, lo=50, n_oct=2, vel=0.55)
    arp_pattern(S, 'harp', inst.harp, bars_range(21, 26), [0, 2, 1, 3, 2, 4, 3, 2], 0.5, lo=50, n_oct=2, vel=0.5)
    arp_pattern(S, 'harp', inst.harp, bars_range(5, 12), [3, 4, 5, 4], 1.0, lo=55, n_oct=2, vel=0.4)
    # percussions
    S.hit('perc', inst.boom, 1, 0, 1.0, 0, 0.9, dur=3.0, pitch=44)
    S.pattern('perc', inst.taiko, [1, 3, 2, 4], ["X...............", "................", "X...............", "......x........."], 0.8, pitch=84, dur=1.8)
    S.pattern('perc', inst.taiko, bars_range(5, 12), ["X...............", "X.......x......."], 0.7, pitch=82, dur=1.6)
    S.pattern('perc', inst.taiko, bars_range(13, 19), "X.......x...x.x.", 0.95, pitch=80, dur=1.5)
    S.pattern('perc', inst.taiko, [20], "X.......xxxxXXXX", 0.95, pitch=80, dur=1.2)
    S.pattern('perc', inst.taiko, bars_range(21, 26), ["X...............", "........x......."], 0.6, pitch=78, dur=1.6)
    S.pattern('perc', inst.taiko, bars_range(27, 30), ["X.......x.......", "X..............."], 0.7, pitch=82, dur=1.6)
    S.pattern('perc', inst.tom, bars_range(13, 20), "....x.......x...", 0.5, pitch=120)
    for bb in (5, 13, 21, 27):
        S.hit('perc', inst.crash, bb, 0, 0.8, 0, 0.7, dur=3.5)
    for bb, d in ((12, 4.0), (26, 4.0)):
        S.hit('fx', inst.cymbal_swell, bb, 0, 0.7, 0, 0.9, dur=d * S.spb)
    S.hit('fx', inst.riser, 12, 0, 0.7, 0, 0.8, dur=4 * S.spb, lo=200, hi=5000)
    return S


# =====================================================================================
def club():
    S = Song('music_club', 100, 36, seed=21)
    S.bus('lute', 3, hall=0.28, room=0.1)
    S.bus('flute', 1, hall=0.32, room=0.05)
    S.bus('bass', -2, hall=0.05, room=0.06, hp_hz=40)
    S.bus('pad', -9, hall=0.45)
    S.bus('perc', -3, hall=0.1, room=0.2)
    S.bus('fx', -6, hall=0.4)
    S.set_prog(1, "G D Em C")
    S.set_prog(5, "G D Em C G D C D")
    S.set_prog(13, "Em C G D Em Am C D")
    S.set_prog(21, "Am C G D")
    S.set_prog(25, "G D Em C G D C D")
    S.set_prog(33, "G Em C D")
    S.sections = [('intro', 1, 4), ('A', 5, 12), ('B', 13, 20), ('bridge', 21, 24), ("A'", 25, 32), ('outro', 33, 36)]
    P8 = [0, 2, 1, 3, 2, 1, 3, 2]
    # luth : arpéges
    arp_pattern(S, 'lute', inst.lute, bars_range(1, 4), P8, 0.5, lo=48, n_oct=2, vel=0.7, from_root=True)
    arp_pattern(S, 'lute', inst.lute, bars_range(5, 12), P8, 0.5, lo=48, n_oct=2, vel=0.55, from_root=True)
    arp_pattern(S, 'lute', inst.lute, bars_range(13, 20), [0, 2, 1, 3, 1, 2, 3, 2], 0.5, lo=48, n_oct=2, vel=0.42, from_root=True)
    arp_pattern(S, 'lute', inst.lute, bars_range(21, 24), P8, 0.5, lo=48, n_oct=2, vel=0.6, from_root=True)
    arp_pattern(S, 'lute', inst.lute, bars_range(25, 32), P8, 0.5, lo=48, n_oct=2, vel=0.55, from_root=True)
    arp_pattern(S, 'lute', inst.lute, bars_range(33, 36), P8, 0.5, lo=48, n_oct=2, vel=0.6, from_root=True)
    # mélodies
    A = "B4:1 D5:1 G5:1.5 F#5:.5  A5:1 F#5:1 D5:2  E5:1 G5:1 B4:1.5 A4:.5  C5:1.5 E5:.5 G5:1 E5:1  B4:1 D5:1 G5:1.5 F#5:.5  A5:1 F#5:1 E5:1 D5:1  E5:1 C5:1 D5:1 E5:1  A4:1 F#5:1 D5:2"
    S.melody('flute', inst.flute, A, 5, vel=0.8, breath=0.14)
    B = "B4:1 E5:1 G5:1 B5:1  G5:1.5 E5:.5 C5:2  D5:1 G5:1 B5:2  A5:1.5 F#5:.5 D5:2  E5:1 G5:1 B5:1 G5:1  A5:1.5 C6:.5 A5:1 E5:1  G5:1 E5:1 C5:1 E5:1  D5:1 F#5:1 A5:2"
    S.melody('lute', inst.lute, B, 13, vel=0.95, t60=2.0)
    S.melody('flute', inst.flute, "E5:4  E5:2 G5:2  D5:4  F#5:4  G5:4  E5:4  G5:4  A5:4", 13, vel=0.5, breath=0.12)
    S.melody('flute', inst.flute, "E5:4 G5:2 E5:2 D5:4 F#5:2 A5:2", 21, vel=0.7)
    S.melody('flute', inst.flute, A, 25, vel=0.85, breath=0.14)
    S.melody('lute', inst.lute, A, 25, vel=0.6, transpose=-12)
    S.melody('flute', inst.flute, "G5:2 B4:2  E5:2 G5:2  C5:1 E5:1 G5:2  A5:1 F#5:1 D5:2", 33, vel=0.75)
    # basse
    bass_pattern(S, 'bass', inst.bass_pick, bars_range(3, 36), [(0, .9, 'r', 1.0), (2, .9, '5', .8), (3.5, .4, '5', .45)], lo=31, hi=42, vel=0.6)
    # nappe douce
    prev = None
    for b in bars_range(13, 32):
        prev = voice_lead(prev, S.chord(b), 52, 70, 3, 60)
        for p in prev:
            S.note('pad', inst.strings, p, b, -0.2, 4.4, 0.32, 0, 1.0, att=0.5, rel=0.8, voices=3)
    # percussions
    S.pattern('perc', inst.frame_drum, bars_range(5, 12), "X.......x.......", 0.45, pitch=105)
    S.pattern('perc', inst.frame_drum, bars_range(13, 20), "X...o...x...o.x.", 0.6, pitch=105)
    S.pattern('perc', inst.frame_drum, bars_range(21, 24), "X.......x.......", 0.45, pitch=105)
    S.pattern('perc', inst.frame_drum, bars_range(25, 32), "X...o...x...o.x.", 0.6, pitch=105)
    S.pattern('perc', inst.frame_drum, bars_range(33, 36), "X.......x.......", 0.45, pitch=105)
    S.pattern('perc', inst.shaker, bars_range(9, 12) + bars_range(13, 20) + bars_range(25, 32), "x.o.x.o.x.o.x.o.", 0.4)
    S.pattern('perc', inst.tambourine, bars_range(13, 20) + bars_range(25, 32), "....x.......x...", 0.45)
    S.pattern('perc', inst.woodblock, bars_range(21, 24), "..o...o...o...o.", 0.3, pitch=1100)
    return S


# =====================================================================================
def draft():
    S = Song('music_draft', 84, 28, seed=31)
    S.bus('pizz', 12, hall=0.3, room=0.1)
    S.bus('celesta', 0, hall=0.45)
    S.bus('flute', 1, hall=0.4)
    S.bus('bass', 0, hall=0.05, room=0.05, hp_hz=40)
    S.bus('pad', -8, hall=0.5)
    S.bus('perc', -3, hall=0.15, room=0.15)
    S.bus('fx', -6, hall=0.45)
    S.set_prog(1, "Gm C Gm C")
    S.set_prog(5, "Gm C Gm D Gm C Gm D")
    S.set_prog(13, "Eb F Gm D Eb F Cm D")
    S.set_prog(21, "Gm C Gm D Gm C")
    S.set_prog(27, "Gm D")
    S.sections = [('intro', 1, 4), ('A', 5, 12), ('B', 13, 20), ("A'", 21, 26), ('outro', 27, 28)]
    # ostinato pizzicato
    arp_pattern(S, 'pizz', inst.pizz, bars_range(5, 12), [0, 2, 1, 2, 0, 2, 1, 2], 0.5, lo=48, n_oct=2, vel=0.55, from_root=True)
    arp_pattern(S, 'pizz', inst.pizz, bars_range(13, 20), [0, 2, 1, 3, 0, 2, 1, 3], 0.5, lo=48, n_oct=2, vel=0.5, from_root=True)
    arp_pattern(S, 'pizz', inst.pizz, bars_range(21, 28), [0, 2, 1, 2, 0, 2, 1, 2], 0.5, lo=48, n_oct=2, vel=0.55, from_root=True)
    arp_pattern(S, 'pizz', inst.pizz, bars_range(1, 4), [0, 2], 1.0, lo=48, n_oct=2, vel=0.45, from_root=True)
    # basse pizz
    bass_pattern(S, 'bass', inst.bass_pick, bars_range(3, 28), [(0, 1.4, 'r', 1.0), (2, 1.4, '5', .7)], lo=36, hi=47, vel=0.5)
    # mélodies
    A = "D5:1 G5:1 F5:.5 D5:.5 Bb4:1  E5:1 C5:1 G4:2  Bb4:1 D5:1 G5:1 F5:1  F#5:1 A5:1 D5:2  D5:1 G5:1 F5:.5 D5:.5 Bb4:1  E5:1 C5:1 G4:1 C5:1  Bb4:1 D5:1 G5:2  A5:1 F#5:1 D5:2"
    S.melody('celesta', inst.celesta, A, 5, vel=0.8)
    B = "G5:2 Bb5:1 G5:1  A5:2 C6:1 A5:1  Bb5:1.5 A5:.5 G5:2  F#5:2 A5:2  Bb5:1 G5:1 Eb5:2  C6:1 A5:1 F5:2  G5:1 Eb5:1 C5:2  A5:1 F#5:1 D5:2"
    S.melody('flute', inst.flute, B, 13, vel=0.75, breath=0.13)
    S.melody('celesta', inst.celesta, B, 13, vel=0.35, transpose=12)
    S.melody('celesta', inst.celesta, A.split("  F#5:1 A5:1")[0] + "  F#5:1 A5:1 D5:2  D5:1 G5:1 F5:.5 D5:.5 Bb4:1  E5:1 C5:1 G4:1 C5:1", 21, vel=0.75)
    S.melody('celesta', inst.celesta, "G5:2 Bb4:2  A5:2 F#5:2", 27, vel=0.7)
    S.melody('flute', inst.flute, "Bb5:4 | ".replace(" | ", "") + " A5:4", 21, vel=0.45) if False else None
    # nappe
    prev = None
    for b in bars_range(13, 28):
        prev = voice_lead(prev, S.chord(b), 50, 68, 3, 58)
        for p in prev:
            S.note('pad', inst.strings, p, b, -0.2, 4.4, 0.3 if b < 21 else 0.22, 0, 1.0, att=0.6, rel=0.9, voices=3)
    prev = None
    for b in bars_range(1, 4):
        prev = voice_lead(prev, S.chord(b), 50, 66, 3, 58)
        for p in prev:
            S.note('pad', inst.pad, p, b, -0.2, 4.4, 0.35, 0, 1.0, att=1.0, rel=1.2, bright=900)
    # tic-tac / cœur
    S.pattern('perc', inst.woodblock, bars_range(1, 28), "x.o.x.o.x.o.x.o.", 0.22, pitch=1500)
    S.pattern('perc', inst.frame_drum, bars_range(1, 4), "X..x............", 0.55, pitch=70)
    S.pattern('perc', inst.frame_drum, bars_range(5, 28), "X..x....o.......", 0.5, pitch=72)
    S.pattern('perc', inst.taiko, [13, 17, 21], "X...............", 0.45, pitch=70, dur=1.6)
    S.pattern('perc', inst.taiko, bars_range(15, 16) + bars_range(19, 20), "........x.......", 0.45, pitch=68, dur=1.6)
    S.hit('fx', inst.riser, 12, 0, 0.45, 0, 0.8, dur=4 * S.spb, lo=300, hi=4500)
    S.hit('fx', inst.cymbal_swell, 20, 0, 0.5, 0, 0.8, dur=4 * S.spb)
    return S


# =====================================================================================
def chest():
    S = Song('music_chest', 96, 8, seed=41)
    S.bus('harp', 4, hall=0.5, room=0.05)
    S.bus('bell', 0, hall=0.55)
    S.bus('choir', 0, hall=0.7)
    S.bus('pad', -7, hall=0.55)
    S.bus('bass', -3, hall=0.1, hp_hz=40)
    S.bus('perc', -5, hall=0.3, room=0.1)
    S.bus('fx', -3, hall=0.5)
    S.set_prog(1, "C Am F G C Em F G")
    S.sections = [('all', 1, 8)]
    arp_pattern(S, 'harp', inst.harp, bars_range(1, 8), [0, 1, 2, 3, 4, 3, 2, 1], 0.5, lo=48, n_oct=3, vel=0.6, from_root=True, dur_mult=2.5)
    M = "E5:1 G5:1 C6:2  A5:1 G5:1 E5:2  F5:1 A5:1 C6:2  B5:1 G5:1 D5:2  E5:1 G5:1 C6:1 E6:1  B5:1 G5:1 E5:2  A5:1 C6:1 F6:2  D6:1 B5:1 G5:2"
    S.melody('bell', inst.bell, M, 1, vel=0.75, tau=0.9)
    S.melody('bell', inst.celesta, M, 1, vel=0.45, transpose=12)
    prev = None
    for b in bars_range(1, 8):
        prev = voice_lead(prev, S.chord(b), 55, 76, 3, 64)
        for p in prev:
            S.note('choir', inst.choir, p, b, -0.3, 4.8, 0.5, 0, 1.0, vowel='a', att=0.7, rel=1.0, voices=4)
            S.note('pad', inst.strings, p - 12, b, -0.3, 4.8, 0.4, 0, 1.0, att=0.6, rel=1.0, voices=3)
    bass_pattern(S, 'bass', inst.bass_pick, bars_range(1, 8), [(0, 1.5, 'r', 1.0), (2, 1.5, '5', .7)], lo=36, hi=47, vel=0.45)
    S.pattern('perc', inst.shaker, bars_range(1, 8), "x.o.x.o.x.o.x.o.", 0.35)
    S.pattern('perc', inst.frame_drum, bars_range(1, 8), "X.......x.......", 0.4, pitch=110)
    S.pattern('perc', inst.tambourine, bars_range(5, 8), "....x.......x...", 0.35)
    # étincelles
    rr = np.random.default_rng(5)
    for _ in range(40):
        b = int(rr.integers(1, 9))
        beat = float(rr.choice([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]))
        S.note('fx', inst.celesta, int(rr.choice([84, 88, 91, 95, 96, 100, 103])), b, beat, 0.6, float(rr.uniform(0.15, 0.4)), rr.uniform(-0.8, 0.8))
    S.hit('fx', inst.cymbal_swell, 4, 2, 0.45, 0, 0.8, dur=2 * S.spb + 4 * S.spb)
    return S
