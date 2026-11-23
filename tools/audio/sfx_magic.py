"""SFX de sorts et soins."""
from sfxlib import *
from sfx_combat import circ
import inst


@sigwrap
def arp(notes, step, fn, total, gains=None):
    out = np.zeros(N(total))
    for i, m in enumerate(notes):
        place(out, fn(m), step * i, 1.0 if gains is None else gains[i])
    return out


@sfx('spell_cast_generic', 'spell', ['spell', 'cast', 'magic', 'generic'], gain=-2)
def spell_cast_generic(v, r):
    p = pf(v, 2.0)
    n = N(0.7)
    f = pts([(0, 280 * p), (0.6, 1500 * p)], n, True)
    ris = (sine(f, n) + 0.5 * sine(f * 1.005, n) + 0.25 * sine(f * 2, n)) * pts([(0, 0), (0.55, 1), (0.7, 0)], n) ** 1.4 * 0.35
    sw = whoosh(0.6, 500, 7000, r, 0.9, 1.0, a=1.0) * 0.25
    sp_ = sparkles(0.9, r, 14, 3000, 9500, (0.04, 0.15), 0.14, 0.1, 0.65)
    pop = inst.bell(1568 * p, 0.8, 0.8, 0.3, r) * 0.7 + thump(0.2, 200, 90, 0.05) * 0.4
    return rv(mix(1.4, [(0, ris, 1), (0, sw, 1), (0, sp_, 1), (0.58, pop, 1)]), 'room', 0.28)


@sfx('spell_fire', 'spell', ['spell', 'fire', 'flame', 'cast'], gain=-1)
def spell_fire(v, r):
    p = pf(v, 2.0)
    d = 1.0
    n = N(d)
    fc = pts([(0, 400), (0.35, 1900 * p), (d, 600)], n, True)
    roar = sweep(white(n, r), fc, 'bp', q=0.9, steps=9)
    pulse = 0.65 + 0.35 * np.sin(TWO_PI * (9 + 3 * sp(v)) * tarr(n)) ** 2
    e = pts([(0, 0), (0.15, 0.8), (0.4, 1), (d, 0)], n) ** 1.2
    low = thump(0.5, 100 * p, 45, 0.2) * 0.8
    cr = crackles(d, r, 55, 1500, 6000, 0.7, (0.002, 0.012)) * pts([(0, 0.3), (0.3, 1), (d, 0.2)], n)
    return rv(roar * pulse * e * 0.8 + low + cr, 'small', 0.2)


@sfx('spell_fire_impact', 'spell', ['spell', 'fire', 'impact', 'explosion'], gain=0)
def spell_fire_impact(v, r):
    p = pf(v, 2.0)
    n = N(1.0)
    wh = thump(0.8, 130 * p, 38, 0.25, fall=0.09) * 1.0
    fc = pts([(0, 6000), (0.3, 1200), (1.0, 250)], n, True)
    nz = sweep(white(n, r), fc, 'lp', steps=8) * perc(n, 0.001, 0.25) * 0.9
    cr = crackles(1.0, r, 70, 1500, 6500, 0.6, (0.002, 0.012)) * pts([(0, 0.4), (0.15, 1), (1.0, 0)], n)
    ig = hp_burst(0.15, 2500, 0.03, r) * 0.6
    return rv(sat(wh + nz, 1.3) + cr + ig, 'room', 0.28)


@sfx('spell_ice', 'spell', ['spell', 'ice', 'frost', 'cast'], gain=-2)
def spell_ice(v, r):
    p = pf(v, 2.0)
    notes = [88, 91, 95, 98, 100, 103]
    bells = arp(notes, 0.06, lambda m: inst.bell(midi_hz(m + int(sp(v))), 0.8, 0.7, 0.35, r), 1.2, [0.5] * 6)
    n = N(0.9)
    t = tarr(n)
    fr = hp(white(n, r), 6000, 2) * pts([(0, 0), (0.5, 1), (0.9, 0)], n) ** 1.5 * 0.18
    sh = np.sin(TWO_PI * 5200 * p * t) * (0.5 + 0.5 * np.sin(TWO_PI * 28 * t)) * pts([(0, 0), (0.4, 1), (0.9, 0)], n) * 0.06
    n2 = N(0.5)
    f = pts([(0, 900 * p), (0.45, 3400 * p)], n2, True)
    gl = sine(f, n2) * pts([(0, 0), (0.4, 1), (0.5, 0)], n2) * 0.15
    return rv(bells + fr + sh + gl + sparkles(1.0, r, 10, 4500, 10000, (0.04, 0.12), 0.1, 0, 0.7), 'hall', 0.3)


@sfx('spell_ice_impact', 'spell', ['spell', 'ice', 'impact', 'crack'], gain=-1)
def spell_ice_impact(v, r):
    p = pf(v, 2.0)
    crack = hp_burst(0.12, 2800, 0.02, r) * 0.9
    sh = np.zeros(N(0.7))
    for _ in range(20):
        place(sh, ping(r.uniform(2500, 9500) * p, 0.35, r.uniform(0.02, 0.1), 0.0005), r.uniform(0, 0.3), r.uniform(0.1, 0.45))
    th = thump(0.35, 160 * p, 60, 0.1) * 0.9 + lp_burst(0.15, 900, 0.04, r) * 0.5
    bl = inst.bell(1900 * p, 0.7, 0.6, 0.25, r) * 0.5
    return rv(crack + sh + th + bl, 'small', 0.28)


@sfx('ice_shatter', 'spell', ['ice', 'shatter', 'glass', 'break'], gain=-1)
def ice_shatter(v, r):
    p = pf(v, 2.0)
    d = 1.3
    cr = hp_burst(0.4, 2200, 0.12, r) * 0.7
    sh = np.zeros(N(d))
    for _ in range(38):
        st = r.exponential(0.18)
        place(sh, ping(r.uniform(1800, 10500) * p, 0.45, r.uniform(0.02, 0.15), 0.0005, (1.0, 0.2)), st, r.uniform(0.08, 0.4))
    ticks = crackles(d, r, 30, 3000, 9000, 0.4, (0.001, 0.005)) * pts([(0, 1), (d, 0)], N(d))
    th = thump(0.4, 140 * p, 50, 0.11) * 0.7
    return rv(cr + sh + ticks + th, 'room', 0.3)


@sfx('spell_lightning', 'spell', ['spell', 'lightning', 'electric', 'zap'], gain=-1)
def spell_lightning(v, r):
    p = pf(v, 2.0)
    d = 0.8
    n = N(d)
    gate = (slow_rand(n, r, 180.0) > -0.1).astype(float)
    gate = lp(gate, 3000, 1)
    nz = bp(white(n, r), 1200, 9000, 1) * gate * perc(n, 0.001, 0.22)
    f = pts([(0, 3600 * p), (0.25, 600 * p), (d, 160 * p)], n, True)
    sq = sat(sine(f, n) + 0.5 * saw(f * 0.5, n), 2.0) * perc(n, 0.001, 0.2) * 0.35
    buzz = sat(lp(saw(120 * p, n), 2500, 2), 2.0) * pts([(0, 0), (0.05, 1), (d, 0)], n) ** 2 * 0.3
    cr = hp_burst(0.1, 3000, 0.02, r) * 0.8
    zaps = crackles(d, r, 25, 2000, 9000, 0.6, (0.001, 0.006)) * pts([(0, 1), (d, 0)], n)
    return rv(nz * 0.8 + sq + buzz + cr + zaps, 'small', 0.22)


@sfx('thunder_crack', 'spell', ['thunder', 'crack', 'storm', 'ambient'], gain=0)
def thunder_crack(v, r):
    cr = hp_burst(0.35, 800, 0.05, r) * 1.0 + thump(0.3, 200, 80, 0.06) * 0.7
    cr2 = noise_burst(0.5, 200, 2500, 0.12, r) * 0.7
    ru = inst.thunder_rumble(3.0 + 0.4 * v, 1.0, r)
    y = mix(4.0, [(0, cr, 1.0), (0.01, cr2, 1.0), (0.05, ru, 1.1)])
    return rv(y, 'big', 0.25)


@sfx('spell_holy', 'spell', ['spell', 'holy', 'light', 'divine'], gain=-1)
def spell_holy(v, r):
    base = 60 + int(sp(v))
    parts = []
    for m in (0, 4, 7, 12):
        parts.append((0.0, inst.choir(midi_hz(base + m), 0.8, 0.7, 'a', att=0.22, rel=0.8, rng=r), 0.6))
    for i, m in enumerate((12, 16, 19, 24)):
        parts.append((0.15 + 0.07 * i, inst.bell(midi_hz(base + m + 12), 1.2, 0.8, 0.6, r), 0.55))
    parts.append((0.0, sparkles(1.6, r, 18, 3500, 10000, (0.06, 0.2), 0.12, 0, 1.0), 1))
    parts.append((0.0, whoosh(0.5, 800, 6000, r, 0.8, 1.0) * 0.2, 1))
    return rv(mix(2.8, parts), 'hall', 0.3)


@sfx('spell_shadow', 'spell', ['spell', 'shadow', 'dark', 'curse'], gain=-1)
def spell_shadow(v, r):
    p = pf(v, 2.0)
    d = 1.2
    n = N(d)
    f = 78 * p
    y = saw(f, n) + saw(f * 1.012, n) + 0.7 * saw(f * 1.5, n)
    fc = pts([(0, 250), (0.5, 1200), (d, 220)], n, True)
    y = sweep(y, fc, 'lp', steps=7) * pts([(0, 0), (0.35, 1), (d, 0)], n) ** 1.3 * 0.5
    wh = np.zeros(n)
    for k in range(3):
        fr = r.uniform(800, 2200)
        fenv = fr * (1 + 0.25 * slow_rand(n, r, 3.0))
        wh += sweep(white(n, r), np.clip(fenv, 300, 5000), 'bp', q=14, steps=7) * (0.4 + 0.6 * np.abs(slow_rand(n, r, 5.0)))
    wh *= pts([(0, 0), (0.5, 1), (d, 0)], n) * 0.15
    th = thump(0.6, 80 * p, 36, 0.25) * 0.8
    sub = sine(pts([(0, 130 * p), (d, 45)], n, True), n) * pts([(0, 0), (0.2, 1), (d, 0)], n) * 0.3
    return rv(mix(d, [(0, y, 1), (0, wh, 1), (0, sub, 1), (0.25, th, 1)]), 'hall', 0.3)


@sfx('spell_void', 'spell', ['spell', 'void', 'dark', 'gravity'], gain=-1)
def spell_void(v, r):
    p = pf(v, 2.0)
    d = 1.4
    n = N(d)
    f = pts([(0, 220 * p), (1.1, 32)], n, True)
    sub = sine(f, n) * pts([(0, 0), (0.05, 1), (1.1, 0.9), (d, 0)], n) * 0.7
    fm_ = ring(sine(f * 4, n) + sine(f * 6.3, n), 233 * p) * pts([(0, 0.2), (0.6, 0.6), (d, 0)], n) * 0.4
    suck = sweep(white(n, r), pts([(0, 4500), (0.8, 300)], n, True), 'bp', q=2.0, steps=8)
    suck *= pts([(0, 0), (0.8, 1), (0.82, 0), (d, 0)], n) ** 1.5 * 0.35
    bm = thump(0.7, 90, 30, 0.3, fall=0.1) * 0.9
    out = sub + fm_ + suck + np.pad(bm, (N(0.8), 0))[:n]
    return rv(out, 'hall', 0.3)


@sfx('spell_arcane', 'spell', ['spell', 'arcane', 'magic', 'sparkle'], gain=-2)
def spell_arcane(v, r):
    base = 64 + int(sp(v))
    pent = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24]
    notes = [base + m for m in pent[:9]]
    nb = N(0.5)
    ie = perc(nb, 0.001, 0.12)
    fb = arp(notes, 0.045, lambda m: fm(midi_hz(m + 12), 3.5, 2.5 * ie + 0.2, nb) * ie * 0.35, 1.2)
    sw = whoosh(0.5, 600, 7000, r, 0.8, 1.0, a=1.0) * 0.2
    sp_ = sparkles(1.2, r, 20, 0, 0, (0.04, 0.14), 0.12, 0.0, 0.8, scale=[base + m + 24 for m in pent])
    return rv(fb + sw + sp_, 'hall', 0.3)


@sfx('spell_nature', 'spell', ['spell', 'nature', 'leaf', 'heal'], gain=-2)
def spell_nature(v, r):
    base = 60 + int(sp(v))
    d = 1.2
    n = N(d)
    ru = bp(white(n, r), 2800, 9000, 1) * (0.45 + 0.55 * np.abs(slow_rand(n, r, 22.0))) * pts([(0, 0), (0.4, 1), (d, 0)], n) ** 1.4 * 0.5
    notes = arp([base, base + 2, base + 4, base + 7, base + 9, base + 12], 0.1, lambda m: inst.marimba(midi_hz(m + 12), 0.5, 0.8, r), 1.0)
    br = inst.pad(midi_hz(base), 1.0, 0.6, att=0.3, rel=0.5, bright=1400, rng=r) * 0.7
    wd = sweep(white(n, r), pts([(0, 400), (0.5, 900), (d, 500)], n, True), 'bp', q=3, steps=6) * pts([(0, 0), (0.5, 1), (d, 0)], n) * 0.12
    return rv(ru + notes * 1.1 + br + wd, 'room', 0.3)


@sfx('spell_wind', 'spell', ['spell', 'wind', 'air', 'gust'], gain=-2)
def spell_wind(v, r):
    p = pf(v, 2.0)
    d = 1.2
    n = N(d)
    fc = pts([(0, 500), (0.5, 2200 * p), (d, 700)], n, True) * (1 + 0.2 * slow_rand(n, r, 4.0))
    g = sweep(pink(n, r), fc, 'bp', q=1.6, steps=9)
    e = pts([(0, 0), (0.45, 1), (d, 0)], n) ** 1.3 * (0.75 + 0.25 * slow_rand(n, r, 6.0))
    wh = np.zeros(n)
    for k in range(2):
        f0 = r.uniform(900, 1700) * p
        fe = f0 * (1 + 0.12 * slow_rand(n, r, 2.5))
        wh += sine(fe, n) * (0.3 + 0.7 * np.abs(slow_rand(n, r, 3.0)))
    wh *= pts([(0, 0), (0.55, 1), (d, 0)], n) * 0.05
    return rv(g * e * 0.8 + wh, 'small', 0.2)


@sfx('spell_earth', 'spell', ['spell', 'earth', 'rock', 'rumble'], gain=-1)
def spell_earth(v, r):
    p = pf(v, 2.0)
    d = 1.3
    n = N(d)
    ru = lp(brown(n, r), 260, 2) * pts([(0, 0), (0.15, 1), (0.9, 0.7), (d, 0)], n) * (0.7 + 0.3 * np.abs(slow_rand(n, r, 12.0)))
    out = ru * 0.8 + bp(brown(n, r), 300, 1500, 1) * pts([(0, 0), (0.15, 1), (0.9, 0.5), (d, 0)], n) * 0.5
    for t0, g in ((0.0, 1.0), (0.32, 0.7), (0.6, 0.55)):
        place(out, thump(0.4, 110 * p, 55, 0.13) * g, t0)
    for _ in range(7):
        st = r.uniform(0.05, 0.9)
        place(out, noise_burst(0.15, 250, 2600, r.uniform(0.02, 0.05), r) * r.uniform(0.7, 1.3), st)
    out += crackles(d, r, 25, 600, 2800, 0.35, (0.004, 0.02))
    return rv(sat(out, 1.3), 'room', 0.25)


@sfx('spell_blood', 'spell', ['spell', 'blood', 'dark', 'wet'], gain=-1)
def spell_blood(v, r):
    p = pf(v, 2.0)
    d = 1.1
    n = N(d)
    wet = bp(white(n, r), 250, 1800, 1) * (0.4 + 0.6 * np.abs(slow_rand(n, r, 14.0))) * pts([(0, 0), (0.1, 1), (d, 0)], n) * 0.7
    out = wet.copy()
    for _ in range(11):
        st = r.uniform(0.0, 0.8)
        m = N(0.05)
        f = pts([(0, r.uniform(120, 220)), (0.05, r.uniform(280, 520))], m, True)
        pop = (sine(f, m) + 0.5 * sine(f * 2, m)) * pts([(0, 0), (0.005, 1), (0.05, 0)], m) * r.uniform(0.5, 0.9)
        place(out, pop, st)
    for t0, g in ((0.0, 1.0), (0.2, 0.75)):
        place(out, thump(0.3, 75 * p, 45, 0.12) * g, t0)
    dr = sine(pts([(0, 90 * p), (d, 60)], n, True), n) * pts([(0, 0), (0.3, 1), (d, 0)], n) * 0.2
    return rv(out + dr, 'small', 0.25)


# ------------------------------------------------------------------ soins
@sfx('heal_chime', 'spell', ['heal', 'chime', 'positive', 'magic'], gain=-2)
def heal_chime(v, r):
    base = 79 + int(sp(v))
    notes = [base, base + 4, base + 7, base + 11, base + 14]
    b = arp(notes, 0.075, lambda m: inst.bell(midi_hz(m), 1.0, 0.8, 0.5, r), 1.4, [0.8, 0.8, 0.8, 0.8, 1.0])
    s = sparkles(1.2, r, 10, 4000, 10000, (0.05, 0.2), 0.1, 0.0, 0.6)
    pd = inst.pad(midi_hz(base - 24), 0.8, 0.5, att=0.2, rel=0.6, bright=1600, rng=r) * 0.5
    return rv(b + s + pd, 'hall', 0.3)


@sfx('heal_big', 'spell', ['heal', 'big', 'holy', 'magic'], gain=-1)
def heal_big(v, r):
    base = 62 + int(sp(v))
    parts = []
    for i, m in enumerate((0, 4, 7, 11, 12, 16, 19, 23, 24)):
        parts.append((0.07 * i, inst.harp(midi_hz(base + m + 12), 1.2, 0.8, r), 0.7))
        parts.append((0.07 * i, inst.bell(midi_hz(base + m + 24), 1.4, 0.7, 0.6, r), 0.35))
    for m in (0, 7, 12, 16):
        parts.append((0.15, inst.choir(midi_hz(base + m), 1.3, 0.75, 'o', att=0.4, rel=1.0, rng=r), 0.6))
    parts.append((0.0, inst.riser(0.8, 0.5, r, 500, 8000), 0.4))
    parts.append((0.6, sparkles(2.0, r, 26, 3500, 10000, (0.06, 0.25), 0.13, 0, 1.4), 1))
    return rv(mix(4.0, parts), 'hall', 0.33)
