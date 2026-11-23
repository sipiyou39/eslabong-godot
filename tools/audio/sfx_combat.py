"""SFX de combat : mêlée, tirs, impacts, déplacements, divers."""
from sfxlib import *
import inst


def circ(fn, x):
    """Applique un filtrage causal de façon circulaire (boucles sans couture)."""
    n = len(x)
    return fn(np.tile(x, 3))[n:2 * n]


# ------------------------------------------------------------------ mêlée
@sfx('swing_light', 'combat', ['swing', 'melee', 'light', 'whoosh'], gain=-3, n=4)
def swing_light(v, r):
    p = pf(v, 2.2)
    d = 0.21 + 0.015 * sp(v)
    w = whoosh(d, 650 * p, 1500 * p, r, 0.45, 1.5, fmid=3300 * p, a=1.3)
    low = whoosh(d * 1.2, 150, 280, r, 0.5, 0.8, fmid=430 * p) * 0.35
    n = N(d)
    air = hp(white(n, r), 6500, 1) * pts([(0, 0), (d * 0.45, 1), (d, 0)], n) ** 2 * 0.12
    return w * 0.7 + low + air


@sfx('swing_heavy', 'combat', ['swing', 'melee', 'heavy', 'whoosh'], gain=-1, n=4)
def swing_heavy(v, r):
    p = pf(v, 2.0)
    d = 0.4 + 0.03 * sp(v)
    w = whoosh(d, 230 * p, 600 * p, r, 0.5, 1.0, fmid=1500 * p, a=1.5) * 0.8
    n = N(d * 1.1)
    f = pts([(0, 130 * p), (d * 0.55, 95 * p), (d * 1.1, 60 * p)], n, True)
    wub = sine(f, n) * pts([(0, 0), (d * 0.5, 1), (d * 1.1, 0)], n) ** 1.5 * 0.7
    body = lp(white(n, r), 420, 2) * pts([(0, 0), (d * 0.5, 1), (d * 1.1, 0)], n) ** 2 * 0.8
    return w + wub + body


def _slash(r, p, g=1.0):
    cut = hp_burst(0.12, 1800, 0.03, r) * 0.8
    shing = metal_ring(2900 * p, 0.35, 0.12, r, (1, 1.7, 2.9, 4.4, 6.2), (1, .6, .4, .25, .15)) * 0.35
    body = thump(0.2, 220 * p, 90 * p, 0.06) * 0.7
    flesh = lp_burst(0.15, 900, 0.045, r) * 0.7
    return (cut + shing + body + flesh) * g


@sfx('hit_slash', 'combat', ['hit', 'slash', 'blade', 'melee'], gain=-1, n=4)
def hit_slash(v, r):
    p = pf(v, 2.5)
    return rv(_slash(r, p), 'tiny')


@sfx('hit_blunt', 'combat', ['hit', 'blunt', 'mace', 'melee'], gain=0, n=4)
def hit_blunt(v, r):
    p = pf(v, 2.5)
    th = thump(0.4, 150 * p, 60 * p, 0.12, fall=0.06) * 0.9
    body = noise_burst(0.22, 220, 1200, 0.05, r) * 1.2 + lp_burst(0.15, 700, 0.04, r) * 0.5
    crack = noise_burst(0.06, 1000, 3800, 0.012, r) * 0.7
    y = sat(th + body + crack, 1.4)
    return rv(y, 'tiny')


@sfx('hit_pierce', 'combat', ['hit', 'pierce', 'stab', 'melee'], gain=-1, n=4)
def hit_pierce(v, r):
    p = pf(v, 2.5)
    st = hp_burst(0.04, 3200, 0.008, r) * 0.7
    pop = thump(0.1, 750 * p, 220 * p, 0.03) * 0.8
    n = N(0.2)
    fc = pts([(0, 2200), (0.2, 300)], n, True)
    sq = sweep(white(n, r), fc, 'lp', steps=6) * perc(n, 0.002, 0.07) * 0.7
    low = thump(0.15, 120, 70, 0.05) * 0.5
    return rv(st + pop + sq + low, 'tiny')


@sfx('hit_magic', 'combat', ['hit', 'magic', 'impact'], gain=-2, n=4)
def hit_magic(v, r):
    p = pf(v, 2.5)
    n = N(0.22)
    f = pts([(0, 380 * p), (0.09, 1900 * p), (0.22, 900 * p)], n, True)
    zap = (sine(f, n) + 0.4 * sine(f * 2, n)) * perc(n, 0.002, 0.07) * 0.6
    bl = inst.bell(1250 * p, 0.6, 0.8, 0.22, r)
    sp_ = sparkles(0.5, r, 8, 3500, 9500, (0.03, 0.1), 0.18, 0, 0.12)
    th = thump(0.25, 150, 60, 0.08) * 0.7
    nz = noise_burst(0.08, 2500, 8000, 0.015, r) * 0.45
    return rv(zap + bl * 0.6 + sp_ + th + nz, 'small')


@sfx('hit_crit', 'combat', ['hit', 'critical', 'impact', 'heavy'], gain=1, n=3)
def hit_crit(v, r):
    p = pf(v, 2.0)
    sl = _slash(r, p * 0.95, 1.0)
    bm = thump(0.7, 150, 55, 0.26, fall=0.08) * 1.0 + noise_burst(0.25, 200, 1400, 0.06, r) * 0.9
    cr = hp_burst(0.25, 2400, 0.05, r) * 0.8
    ding = inst.bell(2350 * p, 0.9, 0.8, 0.3, r) * 0.7
    sub = lp_burst(0.5, 500, 0.18, r) * 0.5
    y = sat(sl + bm + cr + sub, 1.5) + ding
    y = y + sparkles(0.8, r, 10, 3500, 9000, (0.05, 0.2), 0.12, 0.0, 0.3)
    return rv(y, 'room', 0.3)


@sfx('hit_shield_block', 'combat', ['hit', 'shield', 'block', 'metal'], gain=-1, n=4)
def hit_shield_block(v, r):
    p = pf(v, 2.5)
    clang = metal_ring(640 * p, 0.8, 0.28, r, (1, 2.32, 3.9, 5.3, 7.7, 11.2), (1, .75, .5, .35, .25, .15)) * 0.7
    th = thump(0.25, 170 * p, 80 * p, 0.07) * 0.9
    tick = hp_burst(0.05, 2500, 0.01, r) * 0.8
    wood = lp_burst(0.12, 1500, 0.03, r) * 0.5
    return rv(sat(clang + th, 1.3) + tick + wood, 'small')


@sfx('hit_player_hurt', 'combat', ['hit', 'hurt', 'damage', 'player'], gain=-1, n=4)
def hit_player_hurt(v, r):
    p = pf(v, 2.5)
    th = thump(0.32, 140 * p, 70 * p, 0.1, fall=0.05) * 0.8 + noise_burst(0.2, 250, 1400, 0.045, r) * 1.0
    n = N(0.3)
    crunch = sat(lp(saw(92 * p, n), 700, 2), 2.0) * perc(n, 0.002, 0.07) * 0.5
    dull = lp_burst(0.2, 500, 0.07, r) * 0.8
    tone = sine(pts([(0, 420 * p), (0.25, 180 * p)], n, True), n) * perc(n, 0.004, 0.09) * 0.25
    return rv(th + crunch + dull + tone, 'tiny')


# ------------------------------------------------------------------ distance
@sfx('arrow_shoot', 'combat', ['arrow', 'bow', 'shoot', 'ranged'], gain=-3, n=4)
def arrow_shoot(v, r):
    p = pf(v, 2.0)
    tw = inst.ks(175 * p, 0.45, t60=0.28, bright=0.28, pick=0.1, rng=r) * 0.9
    w = whoosh(0.2, 800, 4800 * p, r, 0.35, 1.1, a=1.2) * 0.35
    ck = noise_burst(0.02, 1500, 5000, 0.004, r) * 0.5
    return mix(0.5, [(0, tw, 1), (0.005, w, 1), (0, ck, 1)])


@sfx('arrow_hit', 'combat', ['arrow', 'hit', 'thunk', 'ranged'], gain=-2, n=4)
def arrow_hit(v, r):
    p = pf(v, 2.5)
    th = lp_burst(0.1, 1300, 0.022, r) * 0.9 + thump(0.15, 230 * p, 120 * p, 0.04) * 0.9
    n = N(0.4)
    t = tarr(n)
    shaft = sine(540 * p * (1 + 0.012 * np.sin(TWO_PI * 38 * t)), n) * perc(n, 0.0008, 0.07) * 0.28
    tk = hp_burst(0.03, 3000, 0.006, r) * 0.5
    return rv(th + shaft + tk, 'tiny')


@sfx('crossbow_shoot', 'combat', ['crossbow', 'shoot', 'ranged', 'mechanical'], gain=-2, n=3)
def crossbow_shoot(v, r):
    p = pf(v, 2.0)
    clk = noise_burst(0.025, 2000, 6500, 0.005, r) * 0.7
    tk = thump(0.2, 170 * p, 70 * p, 0.05) * 1.0
    tw = inst.ks(310 * p, 0.35, t60=0.16, bright=0.45, pick=0.1, rng=r) * 0.8
    w = whoosh(0.16, 1500, 6500, r, 0.3, 1.2, a=1.2) * 0.3
    return rv(mix(0.5, [(0, clk, 1), (0, tk, 1), (0.01, tw, 1), (0.01, w, 1)]), 'tiny')


@sfx('bow_draw', 'combat', ['bow', 'draw', 'creak', 'ranged'], gain=-5, n=3)
def bow_draw(v, r):
    p = pf(v, 1.5)
    d = 0.9
    cr = creak(d, r, p, p, 22, 52, 7.0) * 0.8
    n = N(d)
    f = pts([(0, 105 * p), (d, 235 * p)], n, True)
    ten = (sine(f, n) + 0.3 * sine(2 * f, n)) * pts([(0, 0), (d * 0.9, 1), (d, 0.8)], n) ** 1.6 * 0.12
    nock = noise_burst(0.02, 1500, 5000, 0.004, r) * 0.4
    return mix(1.0, [(0, cr, 1), (0, ten, 1), (d, nock, 1)])


# ------------------------------------------------------------------ déplacements
@sfx('dash_whoosh', 'combat', ['dash', 'whoosh', 'movement'], gain=-3, n=4)
def dash_whoosh(v, r):
    p = pf(v, 2.0)
    d = 0.3
    w = whoosh(d, 400 * p, 1500 * p, r, 0.3, 0.9, fmid=4200 * p, a=1.2)
    n = N(d)
    dust = lp(white(n, r), 2500, 1) * pts([(0, 0), (0.08, 1), (d, 0)], n) ** 2 * 0.4
    return w + dust


@sfx('leap_land', 'combat', ['leap', 'land', 'impact', 'movement'], gain=0, n=3)
def leap_land(v, r):
    p = pf(v, 2.0)
    th = thump(0.5, 130 * p, 60 * p, 0.16, fall=0.07) * 0.8 + noise_burst(0.25, 200, 1000, 0.06, r) * 0.9
    dust = lp_burst(0.3, 1800, 0.09, r) * 0.8
    cr = crackles(0.4, r, 40, 1200, 4500, 0.3, (0.002, 0.006))
    return rv(th + dust + cr, 'room', 0.2)


@sfx('footstep_sand', 'combat', ['footstep', 'sand', 'step'], gain=-9, n=4)
def footstep_sand(v, r):
    p = pf(v, 2.0)
    n = N(0.24)
    t = tarr(n)
    sc = bp(white(n, r), 350, 2600 * p, 1) * (np.minimum(1, t / 0.012)) * np.exp(-t / 0.055)
    grain = hp(white(n, r), 2500, 1) * np.exp(-t / 0.03) * 0.25 * (0.5 + 0.5 * np.abs(slow_rand(n, r, 80)))
    th = thump(0.14, 90 * p, 62, 0.035) * 0.5
    return sc + grain + th


@sfx('footstep_stone', 'combat', ['footstep', 'stone', 'step'], gain=-8, n=4)
def footstep_stone(v, r):
    p = pf(v, 2.5)
    tk = noise_burst(0.05, 1100 * p, 4800, 0.012, r) * 0.9 + noise_burst(0.07, 280, 1100, 0.02, r) * 0.9
    th = thump(0.16, 140 * p, 80, 0.04) * 0.5
    clk = ping(r.uniform(1500, 2800) * p, 0.06, 0.012) * 0.25
    return rv(tk + th + clk, 'tiny', 0.15)


# ------------------------------------------------------------------ explosions
@sfx('explosion_small', 'combat', ['explosion', 'boom', 'small'], gain=0, n=3)
def explosion_small(v, r):
    p = pf(v, 1.5)
    bm = thump(0.8, 140 * p, 55, 0.28, fall=0.1) * 1.0
    n = N(0.9)
    fc = pts([(0, 7000), (0.25, 1500), (0.9, 200)], n, True)
    nz = sweep(white(n, r), fc, 'lp', steps=8) * perc(n, 0.001, 0.22) * 1.0
    cr = hp_burst(0.12, 2500, 0.025, r) * 0.7
    deb = crackles(0.9, r, 60, 1500, 6000, 0.45, (0.003, 0.012))
    deb *= pts([(0, 0.2), (0.15, 1), (0.9, 0)], N(0.9))
    return rv(sat(bm + nz, 1.4) + cr + deb, 'room', 0.3)


@sfx('explosion_big', 'combat', ['explosion', 'boom', 'big', 'heavy'], gain=1, n=3)
def explosion_big(v, r):
    p = pf(v, 1.5)
    bm = thump(1.8, 110 * p, 50, 0.6, fall=0.14) * 1.0
    n = N(2.0)
    fc = pts([(0, 6000), (0.4, 1200), (2.0, 120)], n, True)
    nz = sweep(white(n, r), fc, 'lp', steps=8) * perc(n, 0.001, 0.5)
    pops = np.zeros(n)
    for t0, g in ((0.0, 1.0), (0.11, 0.7), (0.27, 0.55)):
        place(pops, lp_burst(0.5, 1800, 0.12, r) * g, t0)
    cr = hp_burst(0.2, 2000, 0.04, r) * 0.8
    deb = crackles(2.0, r, 70, 1200, 5500, 0.4, (0.003, 0.014))
    deb *= pts([(0, 0.1), (0.3, 1), (2.0, 0)], n)
    rum = lp(brown(n, r), 200, 2) * perc(n, 0.01, 0.9) * 0.5
    return rv(sat(bm + nz * 1.2 + pops * 1.0 + rum, 1.4) + cr + deb, 'big', 0.33)


# ------------------------------------------------------------------ boucles
@sfx('beam_loop', 'combat', ['loop', 'beam', 'energy', 'hum'], n=2, loop=True, gain=-7)
def beam_loop(v, r):
    T = 2.0
    n = N(T)
    t = tarr(n)
    f0 = [110.0, 130.5, 98.0, 123.5][v - 1]
    base = circ(lambda x: lp(x, 1600, 2), saw(f0, n)) * 0.45 + saw(f0 * 1.5 + 0.5, n) * 0.0
    hum = sine(f0, n) * 0.6 + sine(f0 * 2 + 1.5, n) * 0.3
    sh_f = f0 * 8
    mod = np.sin(TWO_PI * 7.5 * t)
    shim = np.sin(TWO_PI * (sh_f * t) + 2.2 * mod) * 0.18 + np.sin(TWO_PI * (sh_f * 1.5 * t) + 1.6 * np.sin(TWO_PI * 5.5 * t)) * 0.1
    nz = bandnoise(n, r, 900, 4200, 0) * 0.28
    flut = 1.0 + 0.18 * np.sin(TWO_PI * 6.0 * t) + 0.10 * np.sin(TWO_PI * 11.0 * t + 1.0)
    y = (base + hum + shim + nz) * flut
    y = sat(y * 0.6, 1.5)
    return y


@sfx('fire_loop', 'combat', ['loop', 'fire', 'flame', 'burn'], n=2, loop=True, gain=-8)
def fire_loop(v, r):
    T = 3.0
    n = N(T)
    roar = shaped(n, r, lambda f: _band_f(f, 60, 1400, -6)) * 0.7
    am = 1.0 + 0.35 * slow_rand(n, r, 3.0)
    roar = roar * am
    mid = shaped(n, r, lambda f: _band_f(f, 500, 4500, -3)) * 0.22 * (1.0 + 0.5 * slow_rand(n, r, 7.0))
    hiss = shaped(n, r, lambda f: _band_f(f, 5000, 12000, 0)) * 0.06
    cr = crackles(T, r, 42, 1500, 6500, 0.9, (0.002, 0.014), circular=True)
    pops = crackles(T, r, 5, 500, 2500, 1.0, (0.008, 0.025), circular=True)
    return roar + mid + hiss + cr * 0.6 + pops * 0.5


def _band_f(f, lo, hi, slope):
    from dsp import _band
    return _band(f, lo, hi, slope)


# ------------------------------------------------------------------ boucliers & statuts
@sfx('shield_up', 'combat', ['shield', 'buff', 'defense', 'magic'], gain=-2, n=3)
def shield_up(v, r):
    p = pf(v, 2.0)
    n = N(0.7)
    f = pts([(0, 240 * p), (0.45, 820 * p)], n, True)
    ris = (sine(f, n) + 0.4 * sine(f * 2, n) + 0.2 * sine(f * 3, n)) * pts([(0, 0), (0.4, 1), (0.7, 0)], n) ** 1.3 * 0.35
    shing = metal_ring(2200 * p, 0.6, 0.25, r, (1, 1.5, 2.1, 3.2), (1, .6, .4, .3)) * 0.3
    hum = inst.pad(midi_hz(55 + sp(v)), 0.7, 0.8, att=0.15, rel=0.3, bright=1500, rng=r) * 0.8
    sw = whoosh(0.4, 600, 5000 * p, r, 0.8, 1.0) * 0.18
    y = mix(1.0, [(0, ris, 1), (0.35, shing, 1), (0, hum, 1), (0, sw, 1), (0.38, sparkles(0.5, r, 6, 3500, 9000, (0.05, 0.15), 0.16, 0, 0.2), 1)])
    return rv(y, 'small')


@sfx('shield_break', 'combat', ['shield', 'break', 'shatter', 'glass'], gain=0, n=3)
def shield_break(v, r):
    p = pf(v, 2.0)
    cr = hp_burst(0.3, 2500, 0.08, r) * 0.8
    mt = metal_ring(900 * p, 0.7, 0.2, r, (1, 2.32, 3.9, 5.3, 7.7), (1, .7, .5, .4, .25)) * 0.5
    sh = np.zeros(N(0.8))
    for _ in range(26):
        place(sh, ping(r.uniform(2200, 9500), 0.4, r.uniform(0.02, 0.12), 0.0006), r.uniform(0, 0.4), r.uniform(0.1, 0.4))
    bm = thump(0.6, 120 * p, 40, 0.2, fall=0.07) * 0.9
    return rv(sat(cr + mt + bm, 1.3) + sh, 'room', 0.3)


@sfx('stun_hit', 'combat', ['stun', 'status', 'impact', 'dizzy'], gain=-1, n=3)
def stun_hit(v, r):
    p = pf(v, 2.0)
    th = thump(0.3, 150 * p, 62, 0.08) * 1.0 + lp_burst(0.1, 900, 0.03, r) * 0.6
    n = N(0.9)
    t = tarr(n)
    f = 1050 * p * (1 - 0.35 * t / 0.9)
    wob = np.sin(TWO_PI * np.cumsum(f * (1 + 0.04 * np.sin(TWO_PI * 11 * t))) / SR) * np.exp(-t / 0.3) * 0.4
    ring_ = metal_ring(820 * p, 0.8, 0.3, r, (1, 2.1, 3.4), (1, .5, .3)) * 0.35
    return rv(th + wob + ring_, 'small')


@sfx('buff_up', 'combat', ['buff', 'status', 'rise', 'magic'], gain=-3, n=3)
def buff_up(v, r):
    p = pf(v, 2.0)
    out = []
    for i, m in enumerate((0, 5, 12)):
        n = N(0.22)
        f = 440 * p * 2 ** (m / 12)
        fv = pts([(0, f * 0.97), (0.05, f)], n)
        y = (sine(fv, n) + 0.3 * sine(fv * 2, n)) * perc(n, 0.004, 0.09) * 0.5
        out.append((0.075 * i, y, 1.0))
    sw = whoosh(0.3, 800, 6000, r, 0.8, 1.0, a=1.0) * 0.22
    sp_ = sparkles(0.5, r, 7, 3500, 9000, (0.04, 0.12), 0.14, 0.1, 0.3)
    return rv(mix(0.8, out + [(0, sw, 1), (0, sp_, 1)]), 'small')


@sfx('debuff_down', 'combat', ['debuff', 'status', 'fall', 'curse'], gain=-3, n=3)
def debuff_down(v, r):
    p = pf(v, 2.0)
    n = N(0.65)
    t = tarr(n)
    f = pts([(0, 360 * p), (0.55, 130 * p)], n, True)
    y = saw(f, n) + saw(f * 1.012, n)
    fc = pts([(0, 1400), (0.6, 280)], n, True)
    y = sweep(y, fc, 'lp', steps=6) * (1 + 0.3 * np.sin(TWO_PI * 12 * t))
    y *= pts([(0, 0), (0.03, 1), (0.4, 0.8), (0.65, 0)], n) * 0.45
    th = thump(0.3, 100 * p, 55, 0.1) * 0.5
    return rv(y + th, 'small')


# ------------------------------------------------------------------ utilitaires de combat
@sfx('summon', 'combat', ['summon', 'magic', 'spawn'], gain=0, n=3)
def summon(v, r):
    p = pf(v, 1.5)
    sw = whoosh(0.8, 200, 3200 * p, r, 0.95, 1.4, a=1.0) * 0.6
    n = N(0.8)
    f = pts([(0, 70 * p), (0.8, 260 * p)], n, True)
    gat = (saw(f, n) * 0.4 + sine(f * 2, n) * 0.3)
    gat = lp(gat, 1800, 2) * pts([(0, 0), (0.75, 1), (0.8, 0)], n) ** 1.8 * 0.6
    bm = thump(1.0, 100 * p, 36, 0.3, fall=0.08) * 1.0 + lp_burst(0.4, 700, 0.1, r) * 0.7
    base = 57 + int(sp(v))
    ch = np.zeros(N(1.5))
    for m in (0, 7, 12, 15):
        place(ch, inst.choir(midi_hz(base + m), 0.9, 0.7, 'o', att=0.12, rel=0.9, rng=r), 0)
    bl = inst.bell(midi_hz(base + 24), 1.2, 0.8, 0.7, r)
    y = mix(3.0, [(0, sw, 1), (0, gat, 1), (0.78, bm, 1), (0.8, ch, 0.8), (0.8, bl, 0.6),
                  (0.8, sparkles(1.5, r, 16, 3000, 9000, (0.06, 0.25), 0.13, 0, 1.0), 1)])
    return rv(y, 'hall', 0.3)


@sfx('teleport_blink', 'combat', ['teleport', 'blink', 'magic', 'movement'], gain=-2, n=3)
def teleport_blink(v, r):
    p = pf(v, 2.0)
    n = N(0.2)
    f = pts([(0, 260 * p), (0.14, 3600 * p)], n, True)
    zip1 = fm(f, 2.0, 2.0, n) * pts([(0, 0), (0.14, 1), (0.2, 0)], n) * 0.4
    rw = whoosh(0.16, 3000, 400, r, 0.2, 1.0, a=1.2) * 0.35
    n2 = N(0.22)
    f2 = pts([(0, 3200 * p), (0.2, 500 * p)], n2, True)
    zip2 = fm(f2, 1.5, 1.5, n2) * perc(n2, 0.002, 0.07) * 0.35
    pop = thump(0.15, 260 * p, 90, 0.03) * 0.7 + noise_burst(0.04, 2000, 8000, 0.008, r) * 0.6
    y = mix(0.5, [(0, zip1, 1), (0, rw, 1), (0.18, pop, 1), (0.19, zip2, 1)])
    return rv(y, 'small')


@sfx('projectile_whoosh', 'combat', ['projectile', 'whoosh', 'passby'], gain=-4, n=4)
def projectile_whoosh(v, r):
    p = pf(v, 2.0)
    d = 0.55
    n = N(d)
    fc = pts([(0, 3600 * p), (0.25, 1700 * p), (d, 600 * p)], n, True)
    y = sweep(white(n, r), fc, 'bp', q=2.0, steps=9)
    e = pts([(0, 0.05), (0.22, 1), (d, 0)], n) ** 1.4
    f = pts([(0, 1500 * p), (d, 420 * p)], n, True)
    tn = sine(f, n) * e * 0.08
    return y * e + tn


@sfx('trap_snap', 'combat', ['trap', 'snap', 'metal', 'spring'], gain=-1, n=3)
def trap_snap(v, r):
    p = pf(v, 2.0)
    clk = noise_burst(0.04, 1800, 7000, 0.007, r) * 0.9
    mt = metal_ring(1300 * p, 0.5, 0.09, r, (1, 2.4, 4.1, 6.3), (1, .6, .4, .3)) * 0.6
    n = N(0.5)
    t = tarr(n)
    boing = np.sin(TWO_PI * np.cumsum(360 * p * (1 + 0.1 * np.exp(-t / 0.12) * np.sin(TWO_PI * 24 * t))) / SR) * perc(n, 0.002, 0.11) * 0.4
    th = thump(0.2, 150, 70, 0.05) * 0.9
    return rv(clk + mt + boing + th, 'small')


@sfx('bat_swarm', 'combat', ['bat', 'swarm', 'flutter', 'creature'], gain=-3, n=3)
def bat_swarm(v, r):
    d = 1.6
    n = N(d)
    t = tarr(n)
    out = np.zeros(n)
    for k in range(7):
        st = r.uniform(0, 0.5)
        ln = r.uniform(0.8, 1.1)
        m = N(ln)
        rate = r.uniform(13, 22)
        flap = (0.5 + 0.5 * np.sin(TWO_PI * rate * tarr(m) + r.uniform(0, 6))) ** 2
        w = bp(white(m, r), 700, 2600, 1) * flap * pts([(0, 0), (ln * 0.4, 1), (ln, 0)], m)
        place(out, w, st, 0.22)
    for k in range(9):
        st = r.uniform(0.05, 1.1)
        ln = r.uniform(0.04, 0.1)
        m = N(ln)
        f0 = r.uniform(4200, 8500)
        f = pts([(0, f0), (ln, f0 * r.choice([0.7, 1.3]))], m, True)
        sq = sine(f, m) * pts([(0, 0), (ln * 0.2, 1), (ln, 0)], m)
        place(out, sq, st, r.uniform(0.04, 0.1))
    return rv(out, 'room', 0.2)


@sfx('chain_clink', 'combat', ['chain', 'clink', 'metal'], gain=-3, n=3)
def chain_clink(v, r):
    p = pf(v, 2.0)
    out = np.zeros(N(0.8))
    t = 0.0
    for i in range(r.integers(4, 7)):
        f = r.uniform(1800, 3200) * p
        m = metal_ring(f, 0.2, r.uniform(0.03, 0.08), r, (1, 2.5, 4.3, 6.1), (1, .5, .35, .2))
        place(out, m, t, (0.9 - 0.1 * i) * r.uniform(0.7, 1.0))
        place(out, noise_burst(0.02, 2500, 8000, 0.004, r), t, 0.25)
        t += r.uniform(0.04, 0.1)
    out += lp_burst(0.5, 800, 0.1, r) * 0.15
    return rv(out, 'tiny')


@sfx('bell_toll', 'combat', ['bell', 'toll', 'ambient', 'ominous'], gain=-1, n=3)
def bell_toll(v, r):
    base = [196.0, 174.6, 220.0][v - 1]
    d = 5.0
    n = N(d)
    P = [(0.5, 0.5, 4.5), (1.0, 1.0, 3.6), (1.2, 0.55, 2.8), (1.5, 0.45, 2.4), (2.0, 0.55, 2.0), (2.5, 0.3, 1.5),
         (3.0, 0.25, 1.1), (4.1, 0.18, 0.8), (5.4, 0.12, 0.5)]
    y = bell_partials(base, n, P, r, 0.0004)
    y2 = bell_partials(base * 1.0016, n, P, r, 0.0004)
    st = hp_burst(0.1, 1500, 0.02, r) * 0.4 + thump(0.3, 140, 70, 0.1) * 0.4
    sig = (y + y2 * 0.6) * 0.5 + st
    sig = fade_edges(sig * np.minimum(1.0, tarr(len(sig)) / 0.001), 0, 1.8)
    return rv(sig, 'hall', 0.25)


# ------------------------------------------------------------------ morts & récompenses
@sfx('death_light', 'combat', ['death', 'light', 'fall'], gain=-1, n=3)
def death_light(v, r):
    p = pf(v, 2.0)
    n = N(0.7)
    th = thump(0.4, 150 * p, 65, 0.14, fall=0.08) * 0.8 + noise_burst(0.25, 200, 1200, 0.06, r) * 0.9
    fc = pts([(0, 2500), (0.5, 250)], n, True)
    fall = sweep(white(n, r), fc, 'lp', steps=6) * pts([(0, 0), (0.04, 1), (0.5, 0)], n) ** 1.5 * 0.5
    f = pts([(0, 300 * p), (0.6, 110 * p)], n, True)
    sigh = sine(f, n) * pts([(0, 0), (0.05, 1), (0.6, 0)], n) * 0.18
    return rv(th + fall + sigh, 'small')


@sfx('death_heavy', 'combat', ['death', 'heavy', 'fall', 'boom'], gain=0, n=3)
def death_heavy(v, r):
    p = pf(v, 2.0)
    bm = thump(1.0, 120 * p, 55, 0.4, fall=0.1) * 0.9 + noise_burst(0.5, 150, 1300, 0.12, r) * 1.0
    n = N(1.3)
    arm = np.zeros(n)
    for i in range(10):
        st = r.uniform(0.0, 0.5)
        place(arm, metal_ring(r.uniform(900, 3200), 0.2, r.uniform(0.02, 0.06), r, (1, 2.5, 4.3), (1, .5, .3)), st, r.uniform(0.1, 0.4) * (1 - st))
    rum = lp(brown(n, r), 220, 2) * perc(n, 0.01, 0.4) * 0.5
    fall = lp_burst(0.5, 1200, 0.12, r) * 0.9
    return rv(sat(bm + rum, 1.3) + arm + fall, 'room', 0.3)


@sfx('kill_ding', 'combat', ['kill', 'ding', 'reward', 'ui'], gain=-2, n=3)
def kill_ding(v, r):
    p = pf(v, 1.5)
    b = inst.bell(1760 * p, 0.9, 0.9, 0.35, r)
    b2 = inst.bell(2637 * p, 0.7, 0.6, 0.22, r)
    th = thump(0.15, 220, 110, 0.04) * 0.4
    tk = noise_burst(0.02, 3000, 9000, 0.004, r) * 0.35
    return rv(mix(1.0, [(0, b, 1), (0.04, b2, 0.8), (0, th, 1), (0, tk, 1)]), 'tiny')


@sfx('gold_pickup', 'combat', ['gold', 'pickup', 'coin', 'reward'], gain=-3, n=4)
def gold_pickup(v, r):
    p = pf(v, 1.5)
    out = np.zeros(N(0.7))
    for i, m in enumerate((0, 4, 7)):
        f = 1318.5 * p * 2 ** (m / 12)
        n = N(0.5)
        P = [(1.0, 1.0, 0.18), (2.0, 0.5, 0.1), (3.0, 0.3, 0.07), (4.2, 0.18, 0.05)]
        y = bell_partials(f, n, P, r, 0.0008) * np.minimum(1, tarr(n) / 0.0006)
        place(out, y, 0.055 * i, 0.8)
    out += sparkles(0.7, r, 6, 4000, 10000, (0.03, 0.1), 0.1, 0.05, 0.3)
    return rv(out, 'tiny')


@sfx('coin_clink', 'combat', ['coin', 'clink', 'metal'], gain=-3, n=4)
def coin_clink(v, r):
    p = pf(v, 2.5)
    f = r.uniform(2600, 3400) * p
    y = metal_ring(f, 0.5, 0.15, r, (1, 2.31, 3.17, 5.2, 7.1), (1, .6, .5, .3, .2), jitter=0.02)
    tk = noise_burst(0.02, 3500, 9000, 0.003, r) * 0.5
    return rv(y + tk, 'tiny')


@sfx('resurrect', 'combat', ['resurrect', 'revive', 'holy', 'magic'], gain=0, n=2)
def resurrect(v, r):
    base = 55 + (0 if v == 1 else 2)
    parts = []
    prog = [(0, [0, 7, 12, 16]), (0.55, [5, 12, 17, 21]), (1.1, [7, 14, 19, 23])]
    for t0, ms in prog:
        for m in ms:
            parts.append((t0, inst.choir(midi_hz(base + m + 12), 1.2, 0.8, 'a', att=0.35, rel=1.2, rng=r), 0.55))
    for i, m in enumerate((0, 4, 7, 11, 12, 16, 19, 24)):
        parts.append((0.5 + 0.1 * i, inst.bell(midi_hz(base + 24 + m), 1.8, 0.7, 0.9, r), 0.6))
    parts.append((0.0, inst.riser(1.5, 0.6, r, 400, 9000), 0.5))
    parts.append((1.5, inst.boom(0.5, 2.0, r, 60), 0.45))
    parts.append((1.4, sparkles(2.5, r, 34, 3000, 10000, (0.08, 0.3), 0.14, 0, 1.8), 1.0))
    return rv(mix(5.0, parts), 'hall', 0.33)
