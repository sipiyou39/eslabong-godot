"""SFX de match : cor, compte à rebours, fanfares."""
from sfxlib import *
import inst


def play(events, total):
    """events : (fn, midi, start_sec, dur_sec, vel, gain)."""
    out = np.zeros(N(total))
    for fn, m, st, d, vel, g in events:
        place(out, fn(midi_hz(m), d, vel), st, g)
    return out


@sfx('round_start_horn', 'match', ['match', 'horn', 'start', 'round'], n=2, gain=0)
def round_start_horn(v, r):
    base = [43, 45][v - 1]  # G2 / A2
    ev = [(lambda f, d, vel: inst.horn(f, d, vel, att=0.09, rel=0.5, rng=r), base + 12, 0.0, 0.55, 0.95, 1.0),
          (lambda f, d, vel: inst.horn(f, d, vel, att=0.1, rel=0.9, rng=r), base + 19, 0.62, 1.2, 1.0, 1.0),
          (lambda f, d, vel: inst.brass(f, d, vel, att=0.06, rel=0.6, rng=r), base + 19, 0.62, 1.2, 0.8, 0.7),
          (lambda f, d, vel: inst.brass(f, d, vel, att=0.06, rel=0.5, rng=r), base + 24, 0.62, 1.2, 0.7, 0.5),
          (lambda f, d, vel: inst.horn(f, d, vel, att=0.09, rel=0.5, rng=r), base, 0.0, 1.8, 0.8, 0.8)]
    y = play(ev, 3.0)
    place(y, inst.taiko(0.9, 78, 1.6, r), 0.0, 0.6)
    place(y, inst.taiko(1.0, 70, 1.8, r), 0.62, 0.8)
    place(y, inst.cymbal_swell(0.6, 0.5, r), 0.05, 0.4)
    return rv(y, 'hall', 0.3)


@sfx('countdown_beep', 'match', ['match', 'countdown', 'beep', 'tick'], n=2, gain=-3)
def countdown_beep(v, r):
    f = [880.0, 784.0][v - 1]
    n = N(0.2)
    y = (sine(f, n) + 0.25 * sine(2 * f, n) + 0.1 * tri(f, n)) * pts([(0, 0), (0.008, 1), (0.12, 0.8), (0.2, 0)], n)
    return rv(y * 0.7, 'tiny', 0.15)


@sfx('countdown_go', 'match', ['match', 'countdown', 'go', 'start'], n=2, gain=-1)
def countdown_go(v, r):
    f = [1318.5, 1174.7][v - 1]
    n = N(0.6)
    t = tarr(n)
    y = (sine(f, n) + 0.4 * sine(2 * f, n) + 0.2 * sine(1.5 * f, n)) * pts([(0, 0), (0.008, 1), (0.3, 0.7), (0.6, 0)], n)
    b = inst.bell(f * 2, 0.8, 0.8, 0.35, r) * 0.7
    th = thump(0.3, 220, 100, 0.07) * 0.6
    w = whoosh(0.3, 800, 6000, r, 0.4, 1.0) * 0.2
    return rv(y * 0.6 + b + th + w, 'small', 0.25)


@sfx('timer_warning', 'match', ['match', 'timer', 'warning', 'beep'], n=2, gain=-3)
def timer_warning(v, r):
    f = [1046.5, 987.8][v - 1]
    out = np.zeros(N(0.85))
    for i in range(3):
        n = N(0.1)
        y = (sine(f, n) + 0.3 * sine(2 * f, n)) * pts([(0, 0), (0.006, 1), (0.07, 0.8), (0.1, 0)], n)
        place(out, y, 0.19 * i, 0.8 + 0.1 * i)
    return rv(out * 0.7, 'tiny', 0.15)


@sfx('announcer_whoosh', 'match', ['match', 'announcer', 'whoosh', 'transition'], n=3, gain=-3)
def announcer_whoosh(v, r):
    p = pf(v, 2.0)
    d = 0.9
    n = N(d)
    w = whoosh(d, 250 * p, 2500 * p, r, 0.45, 0.9, fmid=6500 * p, a=1.3)
    sub = sine(pts([(0, 55), (0.4, 130), (d, 45)], n, True), n) * pts([(0, 0), (0.4, 1), (d, 0)], n) * 0.4
    air = hp(white(n, r), 5000, 1) * pts([(0, 0), (0.4, 1), (d, 0)], n) ** 2 * 0.15
    return rv(w + sub + air, 'hall', 0.3)


@sfx('victory_fanfare', 'match', ['match', 'victory', 'fanfare', 'stinger'], n=2, gain=0)
def victory_fanfare(v, r):
    key = [0, 2][v - 1]  # D majeur / E majeur
    D4 = 62 + key
    beat = 0.5
    T = 4.0

    br = lambda f, d, vel: inst.brass(f, d, vel, att=0.04, rel=0.35, rng=r)
    hn = lambda f, d, vel: inst.horn(f, d, vel, att=0.06, rel=0.5, rng=r)
    st = lambda f, d, vel: inst.strings(f, d, vel, att=0.08, rel=0.9, rng=r)
    ev = []
    # annonce en triolets : A4 A4 A4
    for i in range(3):
        ev.append((br, D4 + 7, beat * i / 3, beat / 3 * 0.9, 0.85, 0.9))
        ev.append((br, D4 + 2, beat * i / 3, beat / 3 * 0.9, 0.7, 0.5))
    # D5 long, puis C#5 D5 E5, puis F#5 → accord final
    ev.append((br, D4 + 12, beat * 1, beat * 1.45, 1.0, 1.0))
    ev.append((hn, D4 + 7, beat * 1, beat * 1.45, 0.8, 0.8))
    ev.append((hn, D4 - 5, beat * 1, beat * 1.45, 0.8, 0.8))
    ev.append((br, D4 + 11, beat * 2.5, beat * 0.45, 0.9, 0.9))
    ev.append((br, D4 + 12, beat * 3, beat * 0.45, 0.9, 0.9))
    ev.append((br, D4 + 14, beat * 3.5, beat * 0.45, 0.95, 0.9))
    ev.append((hn, D4 + 4, beat * 2.5, beat * 1.45, 0.8, 0.7))
    ev.append((hn, D4 - 3, beat * 2.5, beat * 1.45, 0.8, 0.8))
    fin = beat * 4
    L = 3.2
    ev += [(br, D4 + 16, fin, L, 1.0, 1.0), (br, D4 + 12, fin, L, 0.85, 0.8), (br, D4 + 7, fin, L, 0.85, 0.7),
           (hn, D4 + 4, fin, L, 0.85, 0.8), (hn, D4 - 5, fin, L, 0.9, 0.9), (hn, D4 - 12, fin, L, 0.9, 0.9),
           (st, D4 + 12, fin, L, 0.9, 0.8), (st, D4 + 16, fin, L, 0.9, 0.8), (st, D4 + 19, fin, L, 0.9, 0.8),
           (st, D4 + 24, fin, L, 0.8, 0.6)]
    y = play(ev, T + 1.2)
    # timbales : roulement puis frappe, cymbale
    for i in range(8):
        place(y, inst.taiko(0.45 + 0.07 * i, 92, 0.5, r), beat * 2.0 + i * 0.12, 0.55)
    place(y, inst.taiko(1.0, 82, 1.8, r), fin, 0.9)
    place(y, inst.taiko(0.9, 62, 1.8, r), fin, 0.7)
    place(y, inst.crash(0.9, r, 2.5), fin, 0.7)
    place(y, inst.taiko(0.7, 90, 0.9, r), 0.0, 0.6)
    for i, m in enumerate((0, 4, 7, 12, 16, 19, 24)):
        place(y, inst.bell(midi_hz(D4 + 24 + m), 1.5, 0.7, 0.8, r), fin + 0.06 * i, 0.3)
    y = rv(y, 'hall', 0.3)
    y = y[:N(T)]
    return fade_edges(y, 0, 0.5)


@sfx('defeat_sting', 'match', ['match', 'defeat', 'sting', 'stinger', 'sad'], n=2, gain=-1)
def defeat_sting(v, r):
    D3 = 50 + [0, -2][v - 1]
    beat = 1.0
    T = 3.0
    st = lambda f, d, vel: inst.strings(f, d, vel, att=0.25, rel=1.1, rng=r)
    hn = lambda f, d, vel: inst.horn(f, d, vel, att=0.15, rel=0.8, rng=r)
    cl = lambda f, d, vel: inst.cello(f, d, vel, att=0.2, rel=0.8, rng=r)
    ev = [(hn, D3 + 24, 0.0, 0.9, 0.85, 0.9), (hn, D3 + 22, 1.0, 0.45, 0.8, 0.9),
          (hn, D3 + 20, 1.5, 0.45, 0.8, 0.9), (hn, D3 + 17, 2.0, 1.4, 0.9, 1.0),
          (st, D3 + 12, 0.0, 3.0, 0.7, 0.8), (st, D3 + 15, 0.0, 3.0, 0.7, 0.8), (st, D3 + 19, 0.0, 3.0, 0.7, 0.7),
          (cl, D3, 0.0, 3.0, 0.9, 1.0), (cl, D3 - 12, 2.0, 1.5, 0.9, 0.8)]
    y = play(ev, T + 1.5)
    place(y, inst.taiko(1.0, 62, 2.0, r), 0.0, 0.9)
    place(y, inst.taiko(0.8, 56, 2.0, r), 2.0, 0.8)
    y = rv(y, 'hall', 0.32)
    return fade_edges(y[:N(T)], 0, 0.7)
