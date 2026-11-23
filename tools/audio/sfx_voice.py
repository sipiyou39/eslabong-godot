"""Voix synthétiques (formants simples) : grognements, cris de mort + foule."""
from sfxlib import *
import inst

VOWELS = {
    'a': (730, 1090, 2440), 'ae': (660, 1720, 2410), 'uh': (640, 1190, 2390), 'o': (570, 840, 2410),
    'oo': (300, 870, 2240), 'i': (270, 2290, 3010), 'e': (530, 1840, 2480), 'er': (490, 1350, 1690),
    'u': (350, 900, 2300),
}
BW = (90, 120, 170)
FG = (1.0, 0.6, 0.32)


def vtrack(v0, v1, n, shift=1.0, bias=0.0):
    """Formants F1..F3 interpolés de la voyelle v0 à v1 (courbe douce)."""
    t = np.linspace(0, 1, n)
    ease = 0.5 - 0.5 * np.cos(np.pi * t)
    out = []
    for k in range(3):
        a, b = VOWELS[v0][k], VOWELS[v1][k]
        fc = (a + (b - a) * ease) * shift
        out.append((fc, max(fc.mean() / BW[k], 2.0), FG[k]))
    return out


def glottal(n, f0, r, jitter=0.012, shim=0.08, tilt=1500.0, rough=0.0, rough_hz=35.0):
    f = np.broadcast_to(np.asarray(f0, float), (n,)) * (1 + jitter * slow_rand(n, r, 55.0))
    src = saw(f, n, r.uniform(0, 1))
    src = lp(src, tilt, 1)
    src *= 1 + shim * slow_rand(n, r, 40.0)
    if rough:
        t = tarr(n)
        src *= 1 - rough * (0.5 + 0.5 * np.sin(TWO_PI * rough_hz * t + r.uniform(0, 6))) ** 1.5
    return src


def voice(dur, f0a, f0b, v0, v1, r, shift=1.0, breath=0.05, tilt=1500.0, rough=0.0, rough_hz=35.0,
          jitter=0.012, drive=1.0, amp=None, curve=1.0):
    n = N(dur)
    f0 = pts([(0, f0a), (dur, f0b)], n, True) if curve == 1.0 else \
        f0a * (f0b / f0a) ** (np.linspace(0, 1, n) ** curve)
    src = glottal(n, f0, r, jitter, 0.08, tilt, rough, rough_hz) + breath * white(n, r)
    y = formants(src, vtrack(v0, v1, n, shift), steps=7)
    if drive > 1.0:
        y = sat(y / (np.std(y) + 1e-9) * 0.7, drive)
    y = y / (np.std(y) + 1e-9)
    if amp is not None:
        y = y * amp
    return y


def aspirate(dur, v, r, shift=1.0):
    n = N(dur)
    return formants(white(n, r), vtrack(v, v, n, shift), steps=2) * perc(n, 0.004, dur * 0.35)


# ------------------------------------------------------------------ grognements
@sfx('voice_grunt_m', 'voice', ['voice', 'grunt', 'male', 'effort'], gain=-3)
def voice_grunt_m(v, r):
    f0 = [118.0, 132.0, 102.0][v - 1]
    pairs = [('uh', 'o'), ('ae', 'uh'), ('o', 'oo')]
    d = [0.36, 0.30, 0.44][v - 1]
    a, b = pairs[v - 1]
    n = N(d)
    am = pts([(0, 0), (0.025, 1), (d * 0.35, 0.9), (d, 0)], n) ** 1.2
    y = voice(d, f0 * 1.12, f0 * 0.82, a, b, r, shift=0.95, breath=0.07, tilt=1900, drive=1.8, amp=am)
    h = aspirate(0.07, a, r, 0.95) * 0.5
    return mix(d + 0.05, [(0, h, 0.5), (0.02, y, 1.0)])


@sfx('voice_grunt_f', 'voice', ['voice', 'grunt', 'female', 'effort'], gain=-3)
def voice_grunt_f(v, r):
    f0 = [215.0, 240.0, 195.0][v - 1]
    pairs = [('ae', 'uh'), ('e', 'ae'), ('a', 'o')]
    d = [0.32, 0.27, 0.38][v - 1]
    a, b = pairs[v - 1]
    n = N(d)
    am = pts([(0, 0), (0.02, 1), (d * 0.4, 0.85), (d, 0)], n) ** 1.2
    y = voice(d, f0 * 1.1, f0 * 0.85, a, b, r, shift=1.17, breath=0.06, tilt=2600, drive=1.5, amp=am)
    h = aspirate(0.06, a, r, 1.17) * 0.4
    return mix(d + 0.05, [(0, h, 0.5), (0.015, y, 1.0)])


@sfx('voice_orc', 'voice', ['voice', 'orc', 'growl', 'monster'], gain=-2)
def voice_orc(v, r):
    f0 = [72.0, 64.0, 80.0][v - 1]
    d = [0.78, 0.9, 0.66][v - 1]
    n = N(d)
    am = pts([(0, 0), (0.05, 1), (d * 0.55, 0.95), (d, 0)], n) ** 1.1
    y = voice(d, f0 * 1.15, f0 * 0.7, 'o', 'uh', r, shift=0.82, breath=0.1, tilt=1400, rough=0.55,
              rough_hz=[34, 29, 41][v - 1], jitter=0.03, drive=3.0, amp=am)
    low = sine(pts([(0, f0 * 0.9), (d, f0 * 0.5)], n, True), n) * am * 0.4
    y = lp(y + low, 3800, 2)
    return rv(y, 'tiny', 0.12)


@sfx('voice_goblin', 'voice', ['voice', 'goblin', 'laugh', 'creature'], gain=-3)
def voice_goblin(v, r):
    nb = [3, 4, 3][v - 1]
    base = [380.0, 440.0, 330.0][v - 1]
    d = 0.13
    out = np.zeros(N(0.18 * nb + 0.2))
    for i in range(nb):
        n = N(d)
        am = pts([(0, 0), (0.012, 1), (d * 0.5, 0.8), (d, 0)], n)
        f0a = base * (1 + 0.08 * i)
        y = voice(d, f0a, f0a * 1.3, 'e', 'i', r, shift=1.28, breath=0.12, tilt=3200, jitter=0.03, drive=1.6, amp=am)
        nas = reson(y, 1050, 8) * 0.5
        place(out, y + nas, 0.17 * i, 1.0 - 0.1 * i)
    return rv(out, 'tiny', 0.1)


@sfx('voice_beast', 'voice', ['voice', 'beast', 'roar', 'monster'], gain=-2)
def voice_beast(v, r):
    f0 = [62.0, 54.0, 74.0][v - 1]
    d = [1.15, 1.3, 0.95][v - 1]
    n = N(d)
    am = pts([(0, 0), (0.06, 1), (d * 0.5, 1), (d, 0)], n) ** 1.1
    y = voice(d, f0 * 1.3, f0 * 0.75, 'uh', 'a', r, shift=0.78, breath=0.25, tilt=2500, rough=0.65,
              rough_hz=[31, 26, 38][v - 1], jitter=0.05, drive=3.5, amp=am)
    hiss = bp(white(n, r), 1200, 6000, 1) * am * (0.5 + 0.5 * np.abs(slow_rand(n, r, 30.0))) * 0.25
    return rv(lp(y + hiss, 5500, 2), 'small', 0.2)


@sfx('voice_death', 'voice', ['voice', 'death', 'scream', 'dying'], gain=-2)
def voice_death(v, r):
    f0 = [150.0, 250.0, 120.0][v - 1]
    d = [1.15, 1.0, 1.35][v - 1]
    shift = [0.95, 1.18, 0.88][v - 1]
    n = N(d)
    am = pts([(0, 0), (0.05, 1), (d * 0.45, 0.9), (d * 0.85, 0.3), (d, 0)], n) ** 1.2
    y = voice(d, f0 * 1.3, f0 * 0.38, 'a', 'o', r, shift=shift, breath=0.12 + 0.08 * (v == 3), tilt=2200,
              rough=0.25, rough_hz=22, jitter=0.03, drive=1.7, amp=am, curve=0.85)
    ex = aspirate(0.5, 'o', r, shift) * pts([(0, 0), (0.15, 1), (0.5, 0)], N(0.5)) * 0.35
    return rv(mix(d + 0.6, [(0, y, 1.0), (d * 0.8, ex, 1.0)]), 'small', 0.22)


# ------------------------------------------------------------------ foule
def crowd_unit(dur, f0a, f0b, v0, r, shift=1.0, att=0.1, rel=0.2):
    n = N(dur)
    f = pts([(0, f0a), (dur, f0b)], n, True) * vibr(n, r)
    src = lp(saw(f, n, r.uniform(0, 1)), 2800, 1) + 0.06 * white(n, r)
    fm_ = [(VOWELS[v0][k] * shift, max(VOWELS[v0][k] * shift / BW[k], 2.0), FG[k]) for k in range(3)]
    y = formants(src, fm_)
    y = y / (np.std(y) + 1e-9)
    return y * swell(n, min(att, dur * 0.45), min(rel, dur * 0.45))


def vibr(n, r, depth=0.01, rate=5.3):
    return 1.0 + depth * np.sin(TWO_PI * (rate * tarr(n) + r.uniform(0, 1)))


def crowd_texture(dur, r, units, f0r, vowels, ulen, shift=(0.85, 1.25), gain=0.12, att=0.08, rel=0.2,
                  t0=0.0, t1=None, f0_slope=1.0, circular=False, shape=None):
    """Renvoie un tableau stéréo (n,2) rempli d'unités vocales panoramiquées."""
    n = N(dur)
    out = np.zeros((n, 2))
    t1 = dur if t1 is None else t1
    for _ in range(units):
        ln = r.uniform(*ulen)
        st = r.uniform(t0, t1)
        f0 = r.uniform(*f0r)
        sh = r.uniform(*shift)
        u = crowd_unit(ln, f0, f0 * f0_slope * r.uniform(0.92, 1.08), r.choice(vowels), r, sh, att, rel)
        g = gain * r.uniform(0.4, 1.0)
        if shape is not None:
            g *= float(np.interp(st + ln / 2, shape[0], shape[1]))
        st2 = pan(u, r.uniform(-0.9, 0.9)) * g
        i = int(st * SR)
        if circular:
            idx = (np.arange(len(u)) + i) % n
            out[idx] += st2
        else:
            a = min(len(u), n - i)
            if a > 0:
                out[i:i + a] += st2[:a]
    return out


def clap_burst(r, lvl=1.0):
    d = r.uniform(0.012, 0.03)
    return noise_burst(d * 6, r.uniform(900, 1800), r.uniform(4000, 8000), d, r, 0.0003) * lvl


def claps(dur, r, rate, t0, t1, lvl=0.3, circular=False, shape=None):
    n = N(dur)
    out = np.zeros((n, 2))
    cnt = r.poisson(rate * (t1 - t0))
    for _ in range(cnt):
        st = r.uniform(t0, t1)
        b = clap_burst(r, lvl * r.uniform(0.3, 1.0))
        if shape is not None:
            b = b * float(np.interp(st, shape[0], shape[1]))
        s2 = pan(b, r.uniform(-0.95, 0.95))
        i = int(st * SR)
        if circular:
            idx = (np.arange(len(b)) + i) % n
            out[idx] += s2
        else:
            a = min(len(b), n - i)
            if a > 0:
                out[i:i + a] += s2[:a]
    return out


def stereo_noise(n, r, lo, hi, slope=0.0):
    return np.stack([bandnoise(n, r, lo, hi, slope), bandnoise(n, r, lo, hi, slope)], 1)


@sfx('crowd_ambience_loop', 'ambience', ['crowd', 'ambience', 'loop', 'arena', 'murmur'], n=2, loop=True,
     stereo=True, gain=-8, peak=-3.0)
def crowd_ambience_loop(v, r):
    T = 20.0
    n = N(T)
    # murmure : bruit formanté, périodique, modulé lentement
    mur = np.zeros((n, 2))
    for c in range(2):
        b1 = shaped(n, r, lambda f: _bandf(f, 180, 900, -3)) * 0.8
        b2 = shaped(n, r, lambda f: _bandf(f, 700, 2600, -2)) * 0.5
        b3 = shaped(n, r, lambda f: _bandf(f, 2600, 7000, -4)) * 0.12
        am1 = 1 + 0.30 * slow_rand(n, r, 0.5)
        am2 = 1 + 0.45 * slow_rand(n, r, 1.8)
        mur[:, c] = b1 * am1 + b2 * am2 + b3
    mur *= 0.5
    # voix individuelles (balbutiements)
    vo = crowd_texture(T, r, 190, (95, 260), ['a', 'o', 'uh', 'e', 'er', 'ae'], (0.18, 0.7), (0.85, 1.25), 0.05,
                       0.06, 0.12, circular=True)
    # quelques vagues plus fortes (rires / réactions) à positions fixes pour le caractère de la foule
    wave = crowd_texture(T, r, 16, (140, 250), ['a', 'o', 'e'], (0.9, 1.7), (0.9, 1.2), 0.07, 0.3, 0.5,
                         circular=True)
    cl = claps(T, r, 3.0, 0, T, 0.05, circular=True)
    swell_env = 1 + 0.22 * slow_rand(n, r, 0.25)
    y = (mur + vo + wave + cl) * swell_env[:, None]
    y = reverb_circ(y, 2.2, 0.35, 0.02, 0.45, seed=7 + v)
    return y


def _bandf(f, lo, hi, slope):
    from dsp import _band
    return _band(f, lo, hi, slope)


@sfx('crowd_cheer', 'ambience', ['crowd', 'cheer', 'applause', 'victory'], n=3, stereo=True, gain=-2)
def crowd_cheer(v, r):
    d = 3.0 + 0.2 * v
    n = N(d)
    env = (pts([(0, 0), (0.35, 0.8), (0.7, 1), (d * 0.7, 0.85), (d, 0)], n)) ** 1.2
    shape = ([0, 0.35, 0.7, d * 0.7, d], [0.1, 0.8, 1, 0.85, 0.2])
    bed = np.zeros((n, 2))
    for c in range(2):
        bed[:, c] = (bandnoise(n, r, 350, 3200, -2) * 0.6 + bandnoise(n, r, 3200, 8000, -4) * 0.15) * env
    vo = crowd_texture(d, r, 90, (150, 340), ['a', 'o', 'e', 'ae'], (0.3, 0.9), (0.85, 1.3), 0.1, 0.07, 0.2,
                       0.0, d * 0.9, f0_slope=1.12, shape=shape)
    cl = claps(d, r, 70, 0.35, d * 0.95, 0.3, shape=shape)
    out = fade_edges(bed * 0.5 + vo + cl, 0, 0.2)
    # un sifflet
    wn = N(0.5)
    wt = tarr(wn)
    fw = 2600 * (1 + 0.05 * np.sin(TWO_PI * 6 * wt)) * (1 + 0.1 * wt)
    wh = sine(fw, wn) * (0.6 + 0.4 * np.sin(TWO_PI * 38 * wt)) * pts([(0, 0), (0.05, 1), (0.4, 0.8), (0.5, 0)], wn) * 0.05
    place(out[:, 0], wh, r.uniform(0.6, 1.2), 1.0)
    place(out[:, 1], wh, r.uniform(0.6, 1.2), 0.5)
    return reverb(out, 1.8, 0.28, 0.015, 0.5, seed=11 + v, tail=1.0)


@sfx('crowd_gasp', 'ambience', ['crowd', 'gasp', 'surprise', 'reaction'], n=3, stereo=True, gain=-3)
def crowd_gasp(v, r):
    d = 1.5
    n = N(d)
    env = pts([(0, 0), (0.45, 1), (0.6, 0.7), (d, 0)], n) ** 1.3
    inh = np.zeros((n, 2))
    for c in range(2):
        fc = pts([(0, 1200), (0.5, 3800), (d, 1500)], n, True)
        inh[:, c] = sweep(white(n, r), fc, 'bp', q=1.3, steps=8) * env * 0.5
    shape = ([0, 0.4, 0.55, d], [0.2, 1, 0.8, 0.1])
    vo = crowd_texture(d, r, 34, (170, 320), ['o', 'oo', 'a'], (0.35, 0.8), (0.85, 1.3), 0.12, 0.12, 0.25,
                       0.25, 0.7, f0_slope=1.2, shape=shape)
    out = fade_edges(inh + vo, 0, 0.2)
    return reverb(out, 1.5, 0.3, 0.015, 0.5, seed=13 + v, tail=0.8)


@sfx('crowd_boo', 'ambience', ['crowd', 'boo', 'disapproval', 'reaction'], n=3, stereo=True, gain=-3)
def crowd_boo(v, r):
    d = 2.6
    n = N(d)
    env = pts([(0, 0), (0.4, 0.8), (1.0, 1), (1.9, 0.8), (d, 0)], n) ** 1.2
    shape = ([0, 0.4, 1.0, 1.9, d], [0.1, 0.8, 1, 0.8, 0.1])
    bed = np.zeros((n, 2))
    for c in range(2):
        bed[:, c] = lp(bandnoise(n, r, 120, 1200, -3), 900, 1) * env * 0.35
    vo = crowd_texture(d, r, 26, (105, 190), ['u', 'oo', 'o'], (0.9, 1.6), (0.82, 1.15), 0.11, 0.3, 0.45,
                       0.0, d * 0.6, f0_slope=0.82, shape=shape)
    return reverb(fade_edges(bed + vo, 0, 0.25), 1.8, 0.3, 0.02, 0.45, seed=17 + v, tail=1.0)
