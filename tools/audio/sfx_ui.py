"""SFX d'interface."""
from sfxlib import *
import inst


@sigwrap
def soft_tone(f, dur, tau, a=0.004, harm=(1.0, 0.28, 0.08)):
    return ping(f, dur, tau, a, harm)


@sfx('ui_click', 'ui', ['ui', 'click', 'button'], gain=-2)
def ui_click(v, r):
    p = pf(v, 1.6)
    n = N(0.1)
    a = sine(pts([(0, 1900 * p), (0.03, 1050 * p)], n, True), n) * perc(n, 0.0007, 0.02)
    b = bp(white(n, r), 2500, 7500, 1) * perc(n, 0.0003, 0.004) * 0.45
    c = sine(310 * p, n) * perc(n, 0.0008, 0.022) * 0.45
    return a + b + c


@sfx('ui_hover', 'ui', ['ui', 'hover', 'soft'], gain=-9)
def ui_hover(v, r):
    p = pf(v, 1.5)
    y = ping(2350 * p, 0.09, 0.022, a=0.006, harm=(1.0, 0.2))
    return y + 0.25 * ping(3500 * p, 0.09, 0.015, a=0.006)


@sfx('ui_confirm', 'ui', ['ui', 'confirm', 'ok'], gain=-2)
def ui_confirm(v, r):
    p = pf(v, 1.5)
    a = soft_tone(659.3 * p, 0.5, 0.11)
    b = soft_tone(987.8 * p, 0.6, 0.17)
    y = mix(0.7, [(0, a, 0.8), (0.085, b, 1.0), (0.085, sparkles(0.5, r, 4, 3000, 8000, (0.03, 0.08), 0.1, 0, 0.2), 1.0)])
    return rv(y, 'small')


@sfx('ui_back', 'ui', ['ui', 'back', 'cancel'], gain=-3)
def ui_back(v, r):
    p = pf(v, 1.5)
    a = soft_tone(784 * p, 0.35, 0.09)
    b = soft_tone(523.3 * p, 0.45, 0.13)
    return rv(mix(0.6, [(0, a, 0.7), (0.08, b, 1.0)]), 'tiny')


@sfx('ui_error', 'ui', ['ui', 'error', 'deny'], gain=-3)
def ui_error(v, r):
    p = pf(v, 1.2)
    out = np.zeros(N(0.42))
    for k, t in enumerate((0.0, 0.14)):
        n = N(0.12)
        f = 150 * p * (1 - 0.06 * k)
        y = saw(f, n) + saw(f * 1.07, n)
        y = lp(y, 650, 2) * 0.6
        y = sat(y, 1.8) * perc(n, 0.004, 0.05)
        y *= np.minimum(1, (n - np.arange(n)) / (0.01 * SR))
        place(out, y, t)
    return out


@sfx('ui_tab', 'ui', ['ui', 'tab', 'tick'], gain=-4)
def ui_tab(v, r):
    p = pf(v, 1.8)
    n = N(0.08)
    t = tarr(n)
    a = (np.sin(TWO_PI * 1250 * p * t) + 0.35 * np.sin(TWO_PI * 2900 * p * t)) * np.exp(-t / 0.014)
    b = bp(white(n, r), 2000, 6000, 1) * perc(n, 0.0003, 0.003) * 0.4
    return a * np.minimum(1, t / 0.0005) + b


@sigwrap
def coin_ping(f, tau, r, dur=0.6):
    n = N(dur)
    P = [(1.0, 1.0, tau), (2.0, 0.55, tau * 0.7), (3.01, 0.3, tau * 0.45), (4.18, 0.22, tau * 0.3), (5.43, 0.12, tau * 0.2)]
    y = bell_partials(f, n, P, r, 0.0008)
    return y * np.minimum(1, tarr(n) / 0.0006)


@sfx('ui_coin', 'ui', ['ui', 'coin', 'gold', 'reward'], gain=-3)
def ui_coin(v, r):
    p = pf(v, 1.2)
    a = coin_ping(987.8 * p, 0.12, r, 0.3) * 0.7
    b = coin_ping(1318.5 * p, 0.28, r, 0.6)
    y = mix(0.8, [(0, a, 0.9), (0.07, b, 1.0), (0.0, noise_burst(0.02, 4000, 9000, 0.004, r), 0.3)])
    return rv(y, 'tiny')


@sfx('ui_levelup', 'ui', ['ui', 'levelup', 'reward', 'jingle'], gain=-1)
def ui_levelup(v, r):
    base = 60 + [0, -1, 1, 2][v - 1]
    notes = [base, base + 4, base + 7, base + 12, base + 16]
    parts = []
    for i, m in enumerate(notes):
        f = midi_hz(m + 12)
        parts.append((0.085 * i, inst.bell(f, 1.2, 0.9, tau=0.5, rng=r), 0.9 if i < 4 else 1.1))
    # nappe de cordes douces + sparkle
    ch = inst.strings(midi_hz(base + 12), 1.0, 0.55, att=0.1, rel=0.6, rng=r) + inst.strings(midi_hz(base + 19), 1.0, 0.5, att=0.1, rel=0.6, rng=r)
    parts.append((0.3, ch, 0.8))
    parts.append((0.1, sparkles(1.4, r, 14, 3500, 9000, (0.05, 0.2), 0.12, 0.0, 1.0), 1.0))
    parts.append((0.0, whoosh(0.4, 500, 4000, r, 0.7, 1.0), 0.18))
    return rv(mix(2.2, parts), 'hall', 0.3)


@sfx('ui_unlock', 'ui', ['ui', 'unlock', 'lock', 'reward'], gain=-2)
def ui_unlock(v, r):
    p = pf(v, 1.2)
    parts = []
    for i, t in enumerate((0.0, 0.07)):
        c = noise_burst(0.04, 2200, 6500, 0.007, r, 0.0003) * 0.6
        m = metal_ring(1650 * p * (1 + 0.12 * i), 0.18, 0.05, r, (1, 2.4, 4.1), (1, 0.4, 0.2))
        parts.append((t, c + 0.5 * m, 1.0))
    parts.append((0.0, thump(0.15, 160, 90, 0.04), 0.5))
    n = N(0.35)
    f = pts([(0, 650 * p), (0.3, 2300 * p)], n, True)
    gl = (sine(f, n) + 0.3 * sine(2 * f, n)) * pts([(0, 0), (0.05, 1), (0.35, 0)], n) * 0.35
    parts.append((0.13, gl, 1.0))
    parts.append((0.3, inst.bell(1568 * p, 1.0, 0.9, 0.5, r), 0.8))
    parts.append((0.22, sparkles(0.8, r, 8, 3500, 9000, (0.05, 0.15), 0.12, 0.0, 0.4), 1.0))
    return rv(mix(1.4, parts), 'small')


@sfx('ui_open_panel', 'ui', ['ui', 'panel', 'open', 'whoosh'], gain=-4)
def ui_open_panel(v, r):
    p = pf(v, 1.5)
    w = whoosh(0.24, 350 * p, 2800 * p, r, 0.7, 0.9, a=1.3) * 0.5
    n = N(0.26)
    f = pts([(0, 380 * p), (0.2, 640 * p)], n, True)
    tn = sine(f, n) * pts([(0, 0), (0.12, 1), (0.26, 0)], n) * 0.3
    s = thump(0.15, 180 * p, 120 * p, 0.04) * 0.4
    return mix(0.3, [(0, w, 1), (0, tn, 1), (0.17, s, 1)])


@sfx('ui_close_panel', 'ui', ['ui', 'panel', 'close', 'whoosh'], gain=-4)
def ui_close_panel(v, r):
    p = pf(v, 1.5)
    w = whoosh(0.2, 2600 * p, 320 * p, r, 0.3, 0.9, a=1.3) * 0.5
    n = N(0.22)
    f = pts([(0, 640 * p), (0.2, 360 * p)], n, True)
    tn = sine(f, n) * pts([(0, 0), (0.05, 1), (0.22, 0)], n) * 0.28
    s = thump(0.12, 150 * p, 100 * p, 0.035) * 0.45
    return mix(0.26, [(0, w, 1), (0, tn, 1), (0.14, s, 1)])


@sfx('ui_chest_open', 'ui', ['ui', 'chest', 'open', 'reward'], gain=-1)
def ui_chest_open(v, r):
    p = pf(v, 1.0)
    cr = creak(0.6, r, 1.0 * p, 1.0 * p, 34, 60) * 0.55
    latch = (noise_burst(0.05, 1500, 5000, 0.01, r) * 0.6 + thump(0.2, 140, 70, 0.07) * 0.8)
    base = 60 + [0, 2, -2, 5][v - 1]
    parts = [(0.0, latch, 0.8), (0.04, cr, 1.0)]
    for i, m in enumerate((base, base + 4, base + 7, base + 11)):
        parts.append((0.55 + 0.06 * i, inst.bell(midi_hz(m + 12), 1.4, 0.7, 0.7, r), 0.7))
    pd = inst.pad(midi_hz(base), 1.1, 0.7, att=0.35, rel=0.8, rng=r) + inst.pad(midi_hz(base + 7), 1.1, 0.7, att=0.35, rel=0.8, rng=r)
    parts.append((0.5, pd, 0.9))
    parts.append((0.55, sparkles(1.5, r, 16, 3000, 9500, (0.06, 0.25), 0.14, 0, 1.0), 1.0))
    return rv(mix(2.4, parts), 'hall', 0.3)


@sfx('ui_chest_rare', 'ui', ['ui', 'chest', 'rare', 'epic', 'reward'], gain=0)
def ui_chest_rare(v, r):
    p = pf(v, 1.0)
    cr = creak(0.5, r, 0.9 * p, 0.9 * p, 30, 52) * 0.5
    latch = (noise_burst(0.05, 1500, 5000, 0.01, r) * 0.6 + thump(0.25, 120, 55, 0.09) * 1.0)
    base = 62 + [0, 2, -2, 5][v - 1]
    parts = [(0.0, latch, 0.9), (0.04, cr, 1.0), (0.45, boom_soft(r), 0.7)]
    for i, m in enumerate((0, 4, 7, 11, 14, 16, 19)):
        parts.append((0.5 + 0.055 * i, inst.bell(midi_hz(base + m + 12), 2.0, 0.8, 1.0, r), 0.75))
    for m in (0, 7, 12, 16):
        parts.append((0.5, inst.choir(midi_hz(base + m - 12 + (12 if m > 7 else 0)), 1.6, 0.6, 'a', att=0.5, rel=1.0, rng=r), 0.7))
    parts.append((0.45, inst.cymbal_swell(1.0, 0.6, r), 0.5))
    parts.append((0.5, sparkles(2.5, r, 30, 3000, 10000, (0.08, 0.3), 0.15, 0, 1.8), 1.0))
    return rv(mix(4.0, parts), 'hall', 0.34)


@sigwrap
def boom_soft(r):
    return thump(0.7, 90, 38, 0.25) * 0.8 + lp_burst(0.3, 500, 0.08, r) * 0.4


@sfx('ui_buy', 'ui', ['ui', 'buy', 'purchase', 'coin'], gain=-2)
def ui_buy(v, r):
    p = pf(v, 1.2)
    ka = noise_burst(0.03, 1800, 6000, 0.006, r) * 0.5 + thump(0.08, 200, 110, 0.02) * 0.4
    ching = coin_ping(2093 * p, 0.35, r, 0.9) + 0.6 * coin_ping(3136 * p, 0.2, r, 0.5)
    c1 = coin_ping(1760 * p, 0.12, r, 0.3) * 0.6
    c2 = coin_ping(1480 * p, 0.12, r, 0.3) * 0.5
    y = mix(1.1, [(0, ka, 1), (0.1, ching, 0.85), (0.02, c1, 0.7), (0.06, c2, 0.7)])
    return rv(y, 'tiny')


@sfx('ui_sell', 'ui', ['ui', 'sell', 'coin'], gain=-2)
def ui_sell(v, r):
    p = pf(v, 1.3)
    parts = []
    t = 0.0
    for i in range(5):
        f = r.uniform(2300, 3700) * p
        parts.append((t, coin_ping(f, 0.09, r, 0.35), 0.8 - 0.1 * i))
        t += r.uniform(0.045, 0.085)
    parts.append((0.0, noise_burst(0.04, 3000, 8000, 0.008, r), 0.3))
    parts.append((0.28, coin_ping(1568 * p, 0.3, r, 0.7), 0.6))
    return rv(mix(1.0, parts), 'tiny')


@sfx('ui_achievement', 'ui', ['ui', 'achievement', 'trophy', 'jingle'], gain=0)
def ui_achievement(v, r):
    base = 55 + [0, 2, -2, 5][v - 1]
    parts = []
    mel = [(0, 0, 0.16), (4, 0.16, 0.16), (7, 0.32, 0.16), (12, 0.48, 0.9)]
    for m, t, d in mel:
        parts.append((t, inst.horn(midi_hz(base + 12 + m), d + 0.05, 0.75, att=0.05, rel=0.35, rng=r), 0.8))
        parts.append((t, inst.bell(midi_hz(base + 24 + m), 1.5, 0.8, 0.8, r), 0.6))
    for m in (0, 7, 12, 16):
        parts.append((0.48, inst.strings(midi_hz(base + 12 + m), 1.0, 0.8, att=0.1, rel=0.8, rng=r), 0.7))
    parts.append((0.48, inst.taiko(0.9, 82, 1.2, r), 0.7))
    parts.append((0.48, inst.crash(0.5, r, 2.0), 0.5))
    parts.append((0.5, sparkles(2.0, r, 24, 3000, 9500, (0.08, 0.3), 0.14, 0, 1.4), 1.0))
    return rv(mix(3.2, parts), 'hall', 0.3)


@sfx('ui_notification', 'ui', ['ui', 'notification', 'ding'], gain=-3)
def ui_notification(v, r):
    p = pf(v, 1.5)
    a = inst.marimba(880 * p, 0.35, 0.9, r)
    b = inst.marimba(659.3 * p, 0.5, 1.0, r)
    ba = inst.bell(1760 * p, 0.5, 0.5, 0.2, r)
    y = mix(0.8, [(0, a, 0.9), (0.15, b, 1.0), (0.0, ba, 0.4)])
    return rv(y, 'small')


@sfx('ui_page', 'ui', ['ui', 'page', 'paper', 'turn'], gain=-4)
def ui_page(v, r):
    p = pf(v, 2.0)
    n = N(0.32)
    t = tarr(n)
    w = bp(white(n, r), 1400 * p, 7500, 1)
    flut = 0.55 + 0.45 * np.abs(slow_rand(n, r, 60.0))
    e = pts([(0, 0), (0.025, 1), (0.1, 0.45), (0.17, 0.8), (0.32, 0)], n) ** 1.5
    y = w * flut * e
    y2 = hp(white(n, r), 4500, 1) * perc(n, 0.001, 0.025) * 0.2
    return y + y2
