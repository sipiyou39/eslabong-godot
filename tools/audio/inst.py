"""Instruments synthétiques partagés (musiques + stingers SFX). Chaque fonction retourne un tableau mono."""
import numpy as np
from scipy import signal as sg
from dsp import *


def _rng(f, rng, salt=0):
    return rng if rng is not None else np.random.default_rng(int(abs(f) * 997) % (2 ** 31) + salt)


def vib(n, cents=6.0, rate=5.2, delay=0.25, r=None):
    t = tarr(n)
    d = np.clip((t - delay) / 0.45, 0, 1)
    ph = 0.0 if r is None else r.uniform(0, 1)
    return 2.0 ** (cents / 1200.0 * d * np.sin(TWO_PI * (rate * t + ph)))


def norm_rms(x, target=0.1):
    r = rms(x)
    return x * (target / r) if r > 1e-9 else x


def _env(n, att, dur, rel, hold=1.0, shape=1.0):
    e = pts([(0, 0), (att, 1), (max(dur, att + 1e-3), hold), (dur + rel, 0)], n)
    return e ** shape


# -------------------------------------------------------------- cordes frottées
def strings(f, dur, vel=0.8, att=0.16, rel=0.4, voices=4, bright=3200.0, rng=None, vcents=6.0):
    r = _rng(f, rng)
    n = N(dur + rel)
    v = vib(n, vcents, 5.0 + r.uniform(-0.4, 0.4), 0.3, r)
    out = np.zeros(n)
    for c in np.linspace(-1, 1, voices):
        out += saw(f * v * 2.0 ** ((c * 11 + r.uniform(-2, 2)) / 1200.0), n, r.uniform(0, 1))
    out /= voices
    fc = min(bright * (0.55 + 0.45 * vel), f * 8.0)
    out = lp(out, fc, 2)
    out = peak_eq(out, 1100, 1.2, 3.0)
    out = out * _env(n, att, dur, rel, 1.0)
    return norm_rms(out, 0.09) * (0.4 + 0.6 * vel)


def cello(f, dur, vel=0.8, att=0.12, rel=0.3, rng=None):
    r = _rng(f, rng, 3)
    n = N(dur + rel)
    v = vib(n, 8, 5.3, 0.2, r)
    out = saw(f * v, n, r.uniform(0, 1)) + 0.7 * saw(f * v * 1.0035, n, r.uniform(0, 1))
    out = lp(out, min(f * 6 * (0.6 + 0.4 * vel), 3500), 2)
    out = peak_eq(out, 280, 1.5, 4.0)
    out *= _env(n, att, dur, rel)
    return norm_rms(out, 0.1) * (0.4 + 0.6 * vel)


def pizz(f, dur, vel=0.8, rng=None):
    r = _rng(f, rng, 5)
    y = ks(f, max(dur, 0.5), t60=0.45, bright=0.75, rng=r)
    y = peak_eq(y, 300, 1.5, 3)
    return y * vel


# -------------------------------------------------------------- cuivres
def brass(f, dur, vel=0.8, att=0.07, rel=0.14, rng=None, bright=1.0):
    r = _rng(f, rng, 7)
    n = N(dur + rel)
    v = vib(n, 4, 5.4, 0.35, r)
    s = saw(f * v, n, r.uniform(0, 1)) + 0.6 * saw(f * v * 1.0045, n, r.uniform(0, 1))
    b = bright * (0.5 + 0.5 * vel)
    fc = pts([(0, f * 1.6), (att * 1.2, f * (3 + 7 * b)), (att * 3 + 0.05, f * (2.6 + 4.5 * b)),
              (max(dur, 0.2), f * (2.4 + 3 * b)), (dur + rel, f * 1.8)], n, log=True)
    y = sweep(s, fc, 'lp', steps=6)
    y = peak_eq(y, 1500, 1.0, 2.5)
    y *= _env(n, att, dur, rel, 0.92)
    return norm_rms(y, 0.1) * (0.35 + 0.65 * vel)


def horn(f, dur, vel=0.8, att=0.14, rel=0.3, rng=None):
    r = _rng(f, rng, 9)
    n = N(dur + rel)
    v = vib(n, 5, 5.0, 0.4, r)
    s = 0.7 * saw(f * v, n, r.uniform(0, 1)) + 0.6 * tri(f * v, n) + 0.3 * saw(f * v * 1.003, n, r.uniform(0, 1))
    fc = pts([(0, f * 2), (att * 1.5, f * (3 + 3 * vel)), (dur, f * (2.6 + 2 * vel)), (dur + rel, f * 1.8)], n, log=True)
    y = sweep(s, fc, 'lp', steps=6)
    y = peak_eq(y, 480, 1.3, 4.0)
    y *= _env(n, att, dur, rel)
    return norm_rms(y, 0.1) * (0.35 + 0.65 * vel)


# -------------------------------------------------------------- voix (chœur)
VOW = {
    'a': [(800, 1.0), (1150, 0.55), (2900, 0.25), (3900, 0.1)],
    'o': [(450, 1.0), (800, 0.55), (2830, 0.2), (3800, 0.08)],
    'u': [(325, 1.0), (700, 0.45), (2700, 0.15), (3800, 0.06)],
    'e': [(420, 1.0), (1800, 0.45), (2600, 0.3), (3500, 0.1)],
    'i': [(290, 1.0), (2200, 0.4), (3000, 0.3), (3500, 0.1)],
}


def choir(f, dur, vel=0.8, vowel='a', att=0.4, rel=0.5, rng=None, voices=4, shift=1.0):
    r = _rng(f, rng, 11)
    n = N(dur + rel)
    v = vib(n, 14, 5.6 + r.uniform(-0.3, 0.3), 0.25, r)
    src = np.zeros(n)
    for c in np.linspace(-1, 1, voices):
        src += saw(f * v * 2.0 ** ((c * 14 + r.uniform(-3, 3)) / 1200.0), n, r.uniform(0, 1))
    src = lp(src / voices, 4500, 1) + 0.04 * white(n, r)
    tracks = [(fc * shift, max(fc * shift / (70 + 0.09 * fc), 3.0), g) for fc, g in VOW[vowel]]
    y = formants(src, tracks)
    y *= _env(n, att, dur, rel)
    return norm_rms(y, 0.09) * (0.4 + 0.6 * vel)


# -------------------------------------------------------------- cordes pincées (Karplus-Strong accordé)
def ks(f, dur, t60=2.0, bright=0.6, pick=0.2, rng=None):
    from scipy.signal import lfilter
    r = _rng(f, rng, 13)
    n = N(dur)
    D = SR / f - 0.5
    Ni = int(np.floor(D))
    frac = D - Ni
    if frac < 0.15:
        Ni -= 1
        frac += 1.0
    a = (1 - frac) / (1 + frac)
    g = 10.0 ** (-3.0 * (D + 0.5) / (SR * t60))
    den = np.zeros(Ni + 3)
    den[0] = 1.0
    den[1] += a
    c = 0.5 * g
    den[Ni] -= c * a
    den[Ni + 1] -= c * (1 + a)
    den[Ni + 2] -= c
    m = Ni + 2
    exc = r.standard_normal(m)
    exc = lp(exc, 400 + bright * 9000, 1)
    k = max(1, int(pick * m))
    exc = exc - np.concatenate([np.zeros(k), exc[:-k]]) * 0.8
    exc -= exc.mean()
    x = np.zeros(n)
    x[:min(m, n)] = exc[:n]
    y = lfilter([1.0, a], den, x)
    y /= (np.max(np.abs(y)) + 1e-9)
    return fade_edges(y, 0, 0.03) * 0.5


def lute(f, dur, vel=0.8, rng=None, t60=1.6):
    r = _rng(f, rng, 15)
    y = ks(f, dur + 0.3, t60=t60, bright=0.42, pick=0.15, rng=r)
    y = peak_eq(y, 240, 1.6, 5.0)
    y = peak_eq(y, 1300, 2.0, 2.5)
    y = lp(y, 5200, 1)
    e = pts([(0, 1), (dur, 1), (dur + 0.3, 0)], len(y))
    return y * e * (0.3 + 0.7 * vel)


def harp(f, dur, vel=0.8, rng=None):
    r = _rng(f, rng, 17)
    y = ks(f, dur + 0.5, t60=3.0, bright=0.5, pick=0.3, rng=r)
    y = peak_eq(y, 400, 1.2, 2)
    e = pts([(0, 1), (dur, 1), (dur + 0.5, 0)], len(y))
    return y * e * (0.3 + 0.7 * vel)


# -------------------------------------------------------------- bois / cloches / mallets
def flute(f, dur, vel=0.7, att=0.07, rel=0.14, breath=0.12, rng=None):
    r = _rng(f, rng, 19)
    n = N(dur + rel)
    v = vib(n, 11, 5.0 + r.uniform(-0.3, 0.3), 0.35, r)
    fr = f * v
    tone = sine(fr, n) + 0.32 * sine(2 * fr, n) + 0.1 * sine(3 * fr, n) + 0.04 * sine(4 * fr, n)
    t = tarr(n)
    nz = reson(white(n, r), f * 2.2, 1.6) * 0.5
    bre = breath * (1.0 + 2.2 * np.exp(-t / 0.06))
    y = tone + nz * bre * 2.0
    y *= _env(n, att, dur, rel, 0.88)
    return norm_rms(y, 0.08) * (0.4 + 0.6 * vel)


def bell(f, dur, vel=0.8, tau=1.0, rng=None):
    n = N(dur)
    P = [(1.0, 1.0, tau), (2.0, 0.5, tau * 0.6), (2.76, 0.4, tau * 0.45), (4.07, 0.22, tau * 0.3),
         (5.4, 0.16, tau * 0.22), (8.93, 0.08, tau * 0.12)]
    y = bell_partials(f, n, P, rng, 0.0005)
    y *= np.minimum(1.0, tarr(n) / 0.002)
    y = fade_edges(y, 0, min(0.05, dur * 0.3))
    return y * 0.35 * vel


def celesta(f, dur, vel=0.8, rng=None):
    n = N(dur)
    P = [(1.0, 1.0, 0.8), (2.0, 0.18, 0.3), (4.0, 0.3, 0.12), (6.0, 0.08, 0.06)]
    y = bell_partials(f, n, P)
    y *= np.minimum(1.0, tarr(n) / 0.0015)
    y = fade_edges(y, 0, min(0.05, dur * 0.3))
    return y * 0.4 * vel


def marimba(f, dur, vel=0.8, rng=None):
    r = _rng(f, rng, 21)
    n = N(dur)
    P = [(1.0, 1.0, 0.35), (3.9, 0.3, 0.06), (9.8, 0.08, 0.025)]
    y = bell_partials(f, n, P)
    t = tarr(n)
    y += 0.2 * lp(white(n, r), 3000, 1) * np.exp(-t / 0.008)
    y *= np.minimum(1.0, t / 0.001)
    y = fade_edges(y, 0, min(0.05, dur * 0.3))
    return y * 0.45 * vel


# -------------------------------------------------------------- basses / synthés
def bass_pick(f, dur, vel=0.8, rng=None):
    r = _rng(f, rng, 23)
    n = N(dur + 0.12)
    s = saw(f, n) * 0.6 + tri(f, n) * 0.5 + sine(f, n) * 0.5
    t = tarr(n)
    fc = f * (2.0 + 5.0 * vel * np.exp(-t / 0.08))
    y = sweep(s, np.clip(fc, 40, 8000), 'lp', steps=6)
    e = pts([(0, 0), (0.006, 1), (dur, 0.85), (dur + 0.12, 0)], n)
    return norm_rms(y * e, 0.1) * (0.4 + 0.6 * vel)


def sub_bass(f, dur, vel=0.8, att=0.02, rel=0.15, rng=None):
    n = N(dur + rel)
    y = sine(f, n) + 0.25 * sine(2 * f, n) + 0.1 * sine(3 * f, n)
    return norm_rms(y * _env(n, att, dur, rel), 0.11) * (0.4 + 0.6 * vel)


def pad(f, dur, vel=0.6, att=0.9, rel=1.0, bright=1800.0, rng=None, voices=5):
    r = _rng(f, rng, 25)
    n = N(dur + rel)
    out = np.zeros(n)
    for c in np.linspace(-1, 1, voices):
        out += saw(f * 2.0 ** ((c * 13 + r.uniform(-3, 3)) / 1200.0), n, r.uniform(0, 1))
    out /= voices
    fc = pts([(0, bright * 0.5), (att * 2, bright), (dur, bright * 0.8), (dur + rel, bright * 0.4)], n, log=True)
    out = sweep(out, np.minimum(fc, f * 9), 'lp', steps=5)
    out *= swell(n, att, rel)
    return norm_rms(out, 0.08) * (0.4 + 0.6 * vel)


def synth_lead(f, dur, vel=0.8, cutoff=3000.0, att=0.01, rel=0.12, rng=None, drive=1.5):
    r = _rng(f, rng, 27)
    n = N(dur + rel)
    s = saw(f, n, r.uniform(0, 1)) + 0.8 * saw(f * 1.006, n, r.uniform(0, 1)) + 0.5 * square(f * 0.5, n)
    fc = pts([(0, cutoff * 2.0), (0.12, cutoff), (dur + rel, cutoff * 0.5)], n, log=True)
    y = sweep(s, fc, 'bp', q=2.2, steps=7) * 0.8 + 0.3 * sweep(s, fc * 0.8, 'lp', steps=5)
    y = sat(y * 0.6, drive)
    y *= _env(n, att, dur, rel)
    return norm_rms(y, 0.1) * (0.4 + 0.6 * vel)


def synth_pluck(f, dur, vel=0.8, cutoff=2500.0, rng=None):
    r = _rng(f, rng, 29)
    n = N(dur + 0.08)
    s = saw(f, n, r.uniform(0, 1)) + 0.7 * saw(f * 1.007, n, r.uniform(0, 1))
    t = tarr(n)
    fc = cutoff * (0.2 + 1.8 * vel * np.exp(-t / 0.09)) + 150
    y = sweep(s, fc, 'lp', steps=6)
    y *= pts([(0, 0), (0.003, 1), (dur * 0.5, 0.35), (dur + 0.08, 0)], n)
    return norm_rms(y, 0.09) * (0.4 + 0.6 * vel)


# -------------------------------------------------------------- percussions
def taiko(vel=1.0, pitch=88.0, dur=1.6, rng=None):
    r = _rng(pitch, rng, 31)
    n = N(dur)
    t = tarr(n)
    f = pts([(0, pitch * 2.0), (0.025, pitch * 1.25), (0.3, pitch)], n, log=True)
    body = sine(f, n) * np.exp(-t / 0.42)
    body += 0.35 * sine(f * 1.58, n) * np.exp(-t / 0.18)
    body += 0.25 * sine(f * 0.5, n) * np.exp(-t / 0.5)
    skin = bp(white(n, r), 700, 3200, 1) * np.exp(-t / 0.014) * 0.7
    thump = lp(white(n, r), 300, 2) * np.exp(-t / 0.06) * 0.8
    y = body + skin + thump
    y *= np.minimum(1.0, t / 0.0015)
    return fade_edges(y, 0, 0.1) * 0.55 * vel


def tom(pitch=140.0, vel=1.0, dur=0.7, rng=None):
    r = _rng(pitch, rng, 33)
    n = N(dur)
    t = tarr(n)
    f = pts([(0, pitch * 1.6), (0.02, pitch * 1.15), (0.2, pitch)], n, log=True)
    y = sine(f, n) * np.exp(-t / 0.2) + 0.2 * sine(f * 1.5, n) * np.exp(-t / 0.08)
    y += 0.5 * bp(white(n, r), 1200, 4500, 1) * np.exp(-t / 0.01)
    y *= np.minimum(1.0, t / 0.001)
    return fade_edges(y, 0, 0.08) * 0.6 * vel


def frame_drum(pitch=110.0, vel=1.0, dur=0.6, rng=None):
    r = _rng(pitch, rng, 35)
    n = N(dur)
    t = tarr(n)
    f = pts([(0, pitch * 1.4), (0.03, pitch)], n, log=True)
    y = sine(f, n) * np.exp(-t / 0.13) + 0.25 * bp(white(n, r), 500, 2500, 1) * np.exp(-t / 0.02)
    y *= np.minimum(1.0, t / 0.001)
    return fade_edges(y, 0, 0.06) * 0.6 * vel


def kick(vel=1.0, rng=None, dur=0.5, pitch=52.0):
    r = _rng(pitch, rng, 37)
    n = N(dur)
    t = tarr(n)
    f = pts([(0, 160), (0.02, 90), (0.1, pitch)], n, log=True)
    y = sine(f, n) * np.exp(-t / 0.16) + 0.4 * lp(white(n, r), 2500, 2) * np.exp(-t / 0.006)
    y *= np.minimum(1.0, t / 0.0008)
    return fade_edges(y, 0, 0.05) * 0.8 * vel


def snare(vel=1.0, rng=None, dur=0.35, tone=190.0):
    r = _rng(tone, rng, 39)
    n = N(dur)
    t = tarr(n)
    y = sine(tone, n) * np.exp(-t / 0.05) * 0.5
    y += hp(white(n, r), 1800, 2) * np.exp(-t / 0.09) * 0.7
    y *= np.minimum(1.0, t / 0.0008)
    return fade_edges(y, 0, 0.05) * 0.6 * vel


def shaker(vel=0.6, rng=None, dur=0.12):
    r = _rng(vel, rng, 41)
    n = N(dur)
    t = tarr(n)
    y = bp(white(n, r), 4500, 11000, 1) * (1 - np.exp(-t / 0.012)) * np.exp(-t / 0.035)
    return fade_edges(y, 0, 0.03) * 0.5 * vel


def tambourine(vel=0.6, rng=None, dur=0.3):
    r = _rng(vel, rng, 43)
    n = N(dur)
    t = tarr(n)
    y = hp(white(n, r), 5500, 2) * np.exp(-t / 0.05) * 0.5
    for fr in (6200, 7400, 8800, 9900):
        y += 0.12 * np.sin(TWO_PI * fr * t + r.uniform(0, 6)) * np.exp(-t / 0.09)
    y *= np.minimum(1.0, t / 0.0006)
    return fade_edges(y, 0, 0.08) * 0.5 * vel


def woodblock(pitch=900.0, vel=0.7, dur=0.15, rng=None):
    n = N(dur)
    t = tarr(n)
    y = (np.sin(TWO_PI * pitch * t) + 0.4 * np.sin(TWO_PI * pitch * 2.4 * t)) * np.exp(-t / 0.025)
    y *= np.minimum(1.0, t / 0.0004)
    return fade_edges(y, 0, 0.03) * 0.5 * vel


def hat(vel=0.6, rng=None, dur=0.1):
    r = _rng(vel, rng, 45)
    n = N(dur)
    t = tarr(n)
    y = hp(white(n, r), 7000, 2) * np.exp(-t / 0.02)
    return fade_edges(y, 0, 0.02) * 0.4 * vel


def crash(vel=0.8, rng=None, dur=3.0):
    r = _rng(vel, rng, 47)
    n = N(dur)
    t = tarr(n)
    w = hp(white(n, r), 3000, 2)
    y = w * (0.5 * np.exp(-t / 0.35) + 0.5 * np.exp(-t / 1.1))
    for fr in (3100, 4300, 5700, 7300, 9100):
        y += 0.05 * np.sin(TWO_PI * fr * t + r.uniform(0, 6)) * np.exp(-t / 1.2)
    y *= np.minimum(1.0, t / 0.002)
    return fade_edges(y, 0, 0.4) * 0.4 * vel


def cymbal_swell(dur=3.0, vel=0.8, rng=None):
    r = _rng(dur, rng, 49)
    n = N(dur)
    t = tarr(n)
    w = hp(white(n, r), 2500, 2)
    e = (t / dur) ** 2.5
    return fade_edges(w * e, 0, 0.05) * 0.4 * vel


def riser(dur=3.0, vel=0.8, rng=None, lo=300.0, hi=7000.0):
    r = _rng(dur, rng, 51)
    n = N(dur)
    w = white(n, r)
    fc = pts([(0, lo), (dur, hi)], n, log=True)
    y = sweep(w, fc, 'bp', q=1.2, steps=9)
    e = (tarr(n) / dur) ** 1.8
    return fade_edges(y * e, 0.01, 0.01) * 0.5 * vel


def boom(vel=1.0, dur=2.5, rng=None, pitch=48.0):
    r = _rng(pitch, rng, 53)
    n = N(dur)
    t = tarr(n)
    f = pts([(0, pitch * 3), (0.08, pitch * 1.4), (0.5, pitch)], n, log=True)
    y = sine(f, n) * np.exp(-t / 0.9)
    y += 0.7 * lp(white(n, r), 500, 2) * np.exp(-t / 0.3)
    y += 0.3 * hp(white(n, r), 2500, 1) * np.exp(-t / 0.05)
    y *= np.minimum(1.0, t / 0.002)
    return fade_edges(y, 0, 0.3) * 0.6 * vel


def thunder_rumble(dur=3.0, vel=1.0, rng=None):
    r = _rng(dur, rng, 55)
    n = N(dur)
    t = tarr(n)
    w = brown(n, r)
    fc = pts([(0, 400), (0.4, 220), (dur, 70)], n, log=True)
    y = sweep(w, fc, 'lp', steps=6)
    e = (1 - np.exp(-t / 0.05)) * np.exp(-t / (dur * 0.35))
    e *= 0.6 + 0.4 * np.abs(slow_rand(n, r, 6.0))
    y = y * e
    y += 0.3 * hp(white(n, r), 2000, 1) * np.exp(-t / 0.02)
    return fade_edges(norm_rms(y, 0.15), 0.002, 0.2) * vel



def oud(f, dur, vel=0.8, rng=None, t60=1.0):
    r = _rng(f, rng, 61)
    y = ks(f, dur + 0.25, t60=t60, bright=0.62, pick=0.12, rng=r)
    y = peak_eq(y, 280, 1.5, 4.0)
    y = lp(y, 6500, 1)
    e = pts([(0, 1), (dur, 1), (dur + 0.25, 0)], len(y))
    return y * e * (0.35 + 0.65 * vel) * 1.4


def zap(vel=0.8, rng=None, dur=0.6):
    r = _rng(dur, rng, 63)
    n = N(dur)
    t = tarr(n)
    y = hp(white(n, r), 2500, 2) * np.exp(-t / 0.03)
    for _ in range(r.integers(3, 8)):
        st = r.uniform(0, dur * 0.7)
        d = r.uniform(0.004, 0.02)
        b = hp(white(N(d * 6), r), 1800, 1) * np.exp(-tarr(N(d * 6)) / d)
        place(y, b, st, r.uniform(0.2, 0.8))
    f = pts([(0, 5200), (0.12, 900), (dur, 200)], n, True)
    y += 0.25 * sine(f, n) * np.exp(-t / 0.1)
    return fade_edges(y * np.minimum(1, t / 0.0004), 0, 0.2) * 0.5 * vel

import types as _types
wrap_module(globals(), [k for k, v in list(globals().items()) if isinstance(v, _types.FunctionType)
                        and not k.startswith('_') and k not in ('vib', 'norm_rms', 'wrap_module', 'sigwrap')
                        and v.__module__ == __name__])
