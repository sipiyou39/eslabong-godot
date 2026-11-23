"""Registre SFX + briques de synthèse communes."""
import numpy as np
from dsp import *

REG = {}
SPREAD = [0.0, -1.0, 1.0, 0.5]


def sfx(name, cat, tags=(), n=3, loop=False, stereo=False, gain=0.0, peak=-3.0, crest=15.0):
    def deco(fn):
        REG[name] = dict(fn=fn, cat=cat, tags=list(tags), n=n, loop=loop, stereo=stereo, gain=gain,
                         peak=peak, crest=crest)
        return fn
    return deco


def sp(v):
    return SPREAD[(v - 1) % 4]


def pf(v, amt=1.0):
    """Facteur de hauteur propre à la variante v."""
    return 2.0 ** (sp(v) * amt / 12.0)


# ------------------------------------------------------------------ briques
RV = {'tiny': (0.25, 0.20), 'small': (0.5, 0.25), 'room': (0.95, 0.28), 'hall': (1.9, 0.30),
      'big': (3.2, 0.32), 'cave': (4.6, 0.38)}


def rv(x, kind='room', wet=None, seed=3):
    rt, w = RV[kind]
    return reverb(x, rt, w if wet is None else wet, 0.0, 0.5, seed=seed, stereo=False if x.ndim == 1 else True,
                  tail=rt * 0.8)


def mix(total, parts):
    """parts: liste (start_sec, array, gain)."""
    n = N(total)
    out = np.zeros(n)
    for s, x, g in parts:
        place(out, x, s, g)
    return out


def noise_burst(dur, lo, hi, tau, r, a=0.0008, order=1):
    n = N(dur)
    return bp(white(n, r), lo, hi, order) * perc(n, a, tau)


def hp_burst(dur, fc, tau, r, a=0.0005):
    n = N(dur)
    return hp(white(n, r), fc, 2) * perc(n, a, tau)


def lp_burst(dur, fc, tau, r, a=0.001):
    n = N(dur)
    return lp(white(n, r), fc, 2) * perc(n, a, tau)


def thump(dur, f0, f1, tau, fall=0.05, a=0.001, harm=0.45):
    """Impact grave : sinus à chute de hauteur + 2e/3e harmoniques (audible sur petits haut-parleurs)."""
    n = N(dur)
    f = pts([(0, f0), (fall, max(f1, 55.0))], n, log=True)
    y = sine(f, n) + harm * sine(f * 2.0, n) + 0.5 * harm * sine(f * 3.0, n)
    return 0.62 * y * perc(n, a, tau)


def ping(f, dur, tau, a=0.001, harm=(1.0,)):
    n = N(dur)
    y = np.zeros(n)
    for k, h in enumerate(harm, start=1):
        if f * k < 0.45 * SR:
            y += h * sine(f * k, n)
    return y * perc(n, a, tau)


def whoosh(dur, f0, f1, r, peak=0.5, q=1.0, fmid=None, a=1.5, slope=0.0):
    n = N(dur)
    fm_ = fmid if fmid is not None else np.sqrt(f0 * f1) * 1.3
    fc = pts([(0, f0), (dur * peak, fm_), (dur, f1)], n, log=True)
    y = sweep(white(n, r), fc, 'bp', q=q, steps=9)
    e = pts([(0, 0), (dur * peak, 1), (dur, 0)], n) ** a
    return y * e


def sparkles(dur, r, count, fmin=2000, fmax=7000, tau=(0.05, 0.25), amp=0.3, t0=0.0, t1=None, scale=None):
    n = N(dur)
    out = np.zeros(n)
    t1 = dur * 0.8 if t1 is None else t1
    for _ in range(count):
        st = r.uniform(t0, t1)
        if scale is not None:
            f = midi_hz(r.choice(scale))
        else:
            f = np.exp(r.uniform(np.log(fmin), np.log(fmax)))
        d = r.uniform(*tau)
        p = ping(f, d * 4, d, a=0.0008, harm=(1.0, 0.25))
        place(out, p, st, amp * r.uniform(0.4, 1.0))
    return out


def metal_ring(f, dur, tau, r, ratios=(1.0, 2.32, 4.25, 6.63, 9.38), amps=None, jitter=0.01):
    n = N(dur)
    t = tarr(n)
    out = np.zeros(n)
    for i, ra in enumerate(ratios):
        fr = f * ra * (1 + r.uniform(-jitter, jitter))
        if fr > 0.45 * SR:
            continue
        a = 1.0 / (1 + 0.5 * i) if amps is None else amps[i]
        out += a * np.sin(TWO_PI * (fr * t + r.uniform(0, 1))) * np.exp(-t / (tau / (1 + 0.45 * i)))
    return fade_edges(out * np.minimum(1.0, t / 0.0004), 0, min(0.04, dur * 0.25))


def crackles(dur, r, rate, lo=1500, hi=7000, level=1.0, tau=(0.002, 0.012), circular=False):
    """Impulsions de crépitement aléatoires (feu, débris). rate = événements/s."""
    n = N(dur)
    out = np.zeros(n)
    cnt = r.poisson(rate * dur)
    for _ in range(cnt):
        st = r.uniform(0, dur)
        d = r.uniform(*tau)
        b = noise_burst(d * 8, lo * r.uniform(0.6, 1.4), hi * r.uniform(0.6, 1.2), d, r, 0.0003)
        amp = level * r.uniform(0.15, 1.0) ** 2
        i = int(st * SR)
        if circular:
            idx = (np.arange(len(b)) + i) % n
            out[idx] += amp * b
        else:
            place(out, b, st, amp)
    return out


def creak(dur, r, f0=1.0, f1=1.0, rate0=38.0, rate1=70.0, q=6.0):
    """Grincement bois/cuir : train d'impulsions irrégulier passé dans des résonances."""
    n = N(dur)
    rate = pts([(0, rate0), (dur, rate1)], n) * (1 + 0.35 * slow_rand(n, r, 9.0))
    src = saw(np.maximum(rate, 5.0), n)
    src = np.maximum(src, -0.2) ** 1 + 0.15 * white(n, r)
    y = reson(src, 720 * f0, q) + 0.8 * reson(src, 1350 * f1, q) + 0.4 * reson(src, 2400 * f1, q)
    am = 0.55 + 0.45 * np.abs(slow_rand(n, r, 14.0))
    return y * am * swell(n, dur * 0.35, dur * 0.4)


def seq(parts_fn, times, total, gains=None):
    out = np.zeros(N(total))
    for i, t in enumerate(times):
        place(out, parts_fn(i), t, 1.0 if gains is None else gains[i])
    return out


MIDI = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def nm(name):
    """'C#4' -> midi."""
    s = name.strip()
    base = MIDI[s[0]]
    i = 1
    while i < len(s) and s[i] in '#b':
        base += 1 if s[i] == '#' else -1
        i += 1
    return base + 12 * (int(s[i:]) + 1)


import types as _types
wrap_module(globals(), ['mix', 'noise_burst', 'hp_burst', 'lp_burst', 'thump', 'ping', 'whoosh', 'sparkles',
                        'metal_ring', 'crackles', 'creak', 'seq', 'rv'])
