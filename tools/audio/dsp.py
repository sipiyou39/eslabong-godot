"""Primitives DSP (numpy/scipy) pour la synthèse audio d'Eslabong."""
import zlib
import numpy as np
from scipy import signal as sg
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 44100
TWO_PI = 2.0 * np.pi


# ---------------------------------------------------------------- utilitaires
def rng_for(name):
    return np.random.default_rng(zlib.crc32(name.encode()) & 0xFFFFFFFF)


def N(sec):
    return int(round(sec * SR))


def tarr(n):
    return np.arange(n) / SR


def dbv(x):
    return 10.0 ** (x / 20.0)


def to_db(x):
    return 20.0 * np.log10(max(float(x), 1e-12))


def midi_hz(m):
    return 440.0 * 2.0 ** ((np.asarray(m, float) - 69.0) / 12.0)


def ratio_semi(s):
    return 2.0 ** (s / 12.0)


def place(buf, x, start, gain=1.0):
    """Ajoute x dans buf à partir de `start` secondes (tronque si dépasse)."""
    i = int(round(start * SR))
    if i >= len(buf) or i + len(x) <= 0:
        return buf
    a, b = max(i, 0), min(i + len(x), len(buf))
    seg = np.array(x[a - i:b - i], dtype=float)
    if b - i < len(x) and len(seg) > 8:
        k = min(N(0.012), len(seg))
        seg[len(seg) - k:] *= np.cos(0.5 * np.pi * np.arange(k) / k) ** 2
    buf[a:b] += gain * seg
    return buf


def pad_to(x, n):
    if len(x) >= n:
        return x[:n]
    return np.concatenate([x, np.zeros((n - len(x),) + x.shape[1:])])


# ---------------------------------------------------------------- enveloppes
def pts(points, n, log=False):
    t = tarr(n)
    ts = [p[0] for p in points]
    vs = [p[1] for p in points]
    if log:
        return np.exp(np.interp(t, ts, np.log(vs)))
    return np.interp(t, ts, vs)


def expd(n, tau):
    return np.exp(-tarr(n) / tau)


def perc(n, a=0.003, tau=0.1):
    t = tarr(n)
    att = np.where(t < a, np.sin(0.5 * np.pi * np.minimum(t / max(a, 1e-6), 1.0)) ** 2, 1.0)
    y = att * np.exp(-t / tau)
    k = min(N(0.03), n // 4)
    if k > 1:
        y[n - k:] *= np.cos(0.5 * np.pi * np.arange(k) / k) ** 2
    return y


def adsr(n, a, d, s, r):
    dur = n / SR
    rs = max(dur - r, a + d + 1e-3)
    e = pts([(0, 0), (a, 1), (a + d, s), (rs, s), (dur, 0)], n)
    return e


def swell(n, a, r):
    """Montée/descente douces (pad, nappes)."""
    dur = n / SR
    e = pts([(0, 0), (a, 1), (max(dur - r, a), 1), (dur, 0)], n)
    return np.sin(0.5 * np.pi * e) ** 2


def fade_edges(x, fin=0.0, fout=0.0):
    x = x.copy()
    n = len(x)
    if fin > 0:
        k = min(N(fin), n)
        r = np.sin(0.5 * np.pi * np.arange(k) / max(k, 1)) ** 2
        x[:k] *= r if x.ndim == 1 else r[:, None]
    if fout > 0:
        k = min(N(fout), n)
        r = np.cos(0.5 * np.pi * np.arange(k) / max(k, 1)) ** 2
        x[n - k:] *= r if x.ndim == 1 else r[:, None]
    return x


# ---------------------------------------------------------------- oscillateurs
def phase(f, n, ph0=0.0):
    f = np.broadcast_to(np.asarray(f, float), (n,))
    return ph0 + (np.cumsum(f) - f) / SR


def sine(f, n, ph0=0.0):
    return np.sin(TWO_PI * phase(f, n, ph0))


def _blep(t, dt):
    out = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    out[m] = x + x - x * x - 1.0
    m = t > 1.0 - dt
    x = (t[m] - 1.0) / dt[m]
    out[m] = x * x + x + x + 1.0
    return out


def saw(f, n, ph0=0.0):
    p = phase(f, n, ph0) % 1.0
    dt = np.broadcast_to(np.asarray(f, float), (n,)) / SR
    dt = np.minimum(dt, 0.45)
    return 2.0 * p - 1.0 - _blep(p, dt)


def square(f, n, pw=0.5, ph0=0.0):
    p = phase(f, n, ph0) % 1.0
    dt = np.minimum(np.broadcast_to(np.asarray(f, float), (n,)) / SR, 0.45)
    y = np.where(p < pw, 1.0, -1.0)
    y = y + _blep(p, dt) - _blep((p + 1.0 - pw) % 1.0, dt)
    return y


def tri(f, n, ph0=0.0):
    p = phase(f, n, ph0) % 1.0
    return 2.0 * np.abs(2.0 * p - 1.0) - 1.0


def additive(f, n, amps, ph0=0.0, rng=None):
    """Somme de partiels harmoniques (amps[k] pour (k+1)·f)."""
    f = np.broadcast_to(np.asarray(f, float), (n,))
    out = np.zeros(n)
    for k, a in enumerate(amps, start=1):
        if a == 0:
            continue
        mx = f.max() * k
        if mx > 0.46 * SR:
            continue
        ph = ph0 if rng is None else rng.uniform(0, 1)
        out += a * np.sin(TWO_PI * phase(f * k, n, ph))
    return out


def fm(fc, ratio, index, n, index_env=None):
    """Synthèse FM simple. index peut être un tableau."""
    mod = np.sin(TWO_PI * phase(np.asarray(fc, float) * ratio, n))
    idx = index if index_env is None else index * index_env
    return np.sin(TWO_PI * phase(fc, n) + idx * mod)


def bell_partials(f, n, partials, rng=None, jitter=0.0):
    """partials: liste (ratio, amp, tau)."""
    t = tarr(n)
    out = np.zeros(n)
    for r, a, tau in partials:
        fr = f * r * (1 + (0 if rng is None else rng.uniform(-jitter, jitter)))
        if fr > 0.46 * SR:
            continue
        ph = 0.0 if rng is None else rng.uniform(0, 1)
        out += a * np.sin(TWO_PI * (fr * t + ph)) * np.exp(-t / tau)
    k = min(N(0.05), n // 4)
    if k > 1:
        out[n - k:] *= np.cos(0.5 * np.pi * np.arange(k) / k) ** 2
    return out


# ---------------------------------------------------------------- bruits
def white(n, rng):
    return rng.standard_normal(n)


def shaped(n, rng, shape):
    """Bruit périodique (circulaire) dont l'amplitude spectrale suit shape(freqs)."""
    fr = np.fft.rfftfreq(n, 1.0 / SR)
    mag = shape(fr)
    ph = rng.uniform(0, TWO_PI, len(fr))
    spec = mag * np.exp(1j * ph)
    spec[0] = 0
    x = np.fft.irfft(spec, n)
    return x / (np.std(x) + 1e-12)


def _band(fr, lo, hi, slope_db_oct=0.0):
    lf = np.log2(np.maximum(fr, 1.0))
    a = 1.0 / (1.0 + (np.maximum(lo, 1) / np.maximum(fr, 1.0)) ** 4)
    b = 1.0 / (1.0 + (np.maximum(fr, 1.0) / hi) ** 4)
    m = a * b
    if slope_db_oct:
        m = m * 10.0 ** (slope_db_oct * (lf - np.log2(1000.0)) / 20.0)
    return m


def bandnoise(n, rng, lo, hi, slope=0.0):
    return shaped(n, rng, lambda f: _band(f, lo, hi, slope))


def pink(n, rng):
    return shaped(n, rng, lambda f: 1.0 / np.sqrt(np.maximum(f, 20.0)))


def brown(n, rng):
    return shaped(n, rng, lambda f: 1.0 / np.maximum(f, 20.0))


def slow_rand(n, rng, rate):
    """Modulateur aléatoire lissé, ~[-1, 1], de vitesse caractéristique `rate` Hz (périodique)."""
    x = shaped(n, rng, lambda f: 1.0 / (1.0 + (f / rate) ** 2) ** 1.5 * (f > 0))
    return np.clip(x / 2.5, -1, 1)


# ---------------------------------------------------------------- filtres
def _clamp(fc):
    return float(np.clip(fc, 10.0, 0.45 * SR))


def lp(x, fc, order=2):
    return sg.sosfilt(sg.butter(order, _clamp(fc), 'lowpass', fs=SR, output='sos'), x, axis=0)


def hp(x, fc, order=2):
    return sg.sosfilt(sg.butter(order, _clamp(fc), 'highpass', fs=SR, output='sos'), x, axis=0)


def bp(x, lo, hi, order=2):
    return sg.sosfilt(sg.butter(order, [_clamp(lo), _clamp(hi)], 'bandpass', fs=SR, output='sos'), x, axis=0)


def _bq_bp(fc, q):
    w0 = TWO_PI * _clamp(fc) / SR
    al = np.sin(w0) / (2.0 * q)
    a0 = 1 + al
    return np.array([[al / a0, 0.0, -al / a0, 1.0, -2 * np.cos(w0) / a0, (1 - al) / a0]])


def reson(x, fc, q=8.0, gain=1.0):
    return gain * sg.sosfilt(_bq_bp(fc, q), x, axis=0)


def peak_eq(x, fc, q, gain_db):
    A = 10 ** (gain_db / 40.0)
    w0 = TWO_PI * _clamp(fc) / SR
    al = np.sin(w0) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w0), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w0), 1 - al / A])
    return sg.sosfilt(np.array([np.concatenate([b / a[0], a / a[0]])]), x, axis=0)


def shelf_hi(x, fc, gain_db):
    """Étagère aiguë simple : x + (gain-1)*hp(x)."""
    return x + (dbv(gain_db) - 1.0) * hp(x, fc, 1)


def shelf_lo(x, fc, gain_db):
    return x + (dbv(gain_db) - 1.0) * lp(x, fc, 1)


def sweep(x, fc_env, kind='lp', q=0.8, steps=10):
    """Filtre à fréquence variable (morphing entre `steps` filtres fixes)."""
    fc_env = np.broadcast_to(np.asarray(fc_env, float), (len(x),)).copy()
    fc_env = np.clip(fc_env, 20.0, 0.45 * SR)
    fmin, fmax = fc_env.min(), fc_env.max()

    def one(g):
        if kind == 'lp':
            return lp(x, g, 2)
        if kind == 'hp':
            return hp(x, g, 2)
        if kind == 'bp':
            return reson(x, g, q)
        if kind == 'lp4':
            return lp(x, g, 4)
        raise ValueError(kind)

    if fmax / fmin < 1.04:
        return one(float(np.sqrt(fmin * fmax)))
    grid = np.geomspace(fmin, fmax, steps)
    outs = np.stack([one(g) for g in grid])
    pos = (np.log(fc_env) - np.log(fmin)) / (np.log(fmax) - np.log(fmin)) * (steps - 1)
    i0 = np.clip(np.floor(pos).astype(int), 0, steps - 2)
    fr = pos - i0
    idx = np.arange(len(x))
    return outs[i0, idx] * (1 - fr) + outs[i0 + 1, idx] * fr


def formants(x, tracks, steps=8):
    """Banque de résonateurs parallèles. tracks : liste (fc|env, q, gain)."""
    out = np.zeros_like(x)
    for fc, q, g in tracks:
        if np.ndim(fc) == 0:
            out += g * reson(x, fc, q)
        else:
            out += g * sweep(x, fc, 'bp', q=q, steps=steps)
    return out


def dc_block(x, fc=20.0):
    return hp(x, fc, 1)


# ---------------------------------------------------------------- effets
def sat(x, drive=2.0):
    return np.tanh(drive * x) / np.tanh(drive)


def ring(x, f):
    return x * np.sin(TWO_PI * f * tarr(len(x)))


def echo(x, time, fb=0.35, mix=0.3, damp=4000.0, taps=5):
    d = N(time)
    out = np.zeros(len(x) + d * taps)
    out[:len(x)] = x
    cur = x
    g = 1.0
    for k in range(1, taps + 1):
        cur = lp(cur, damp, 1)
        out[d * k:d * k + len(x)] += mix * g * cur
        g *= fb
    return out


_ir_cache = {}


def make_ir(rt60=1.5, pre=0.0, damp=0.5, seed=1, size=1.0, ch=0):
    key = (round(rt60, 3), round(pre, 4), round(damp, 3), seed, round(size, 3), ch)
    if key in _ir_cache:
        return _ir_cache[key]
    n = N(rt60 * 1.05 + 0.05)
    r = np.random.default_rng(seed * 101 + ch * 7919)
    t = tarr(n)
    w = r.standard_normal(n)
    lo = lp(w, 450, 2)
    mid = bp(w, 450, 3800, 2)
    hi = hp(w, 3800, 2)

    def dec(rt):
        return 10.0 ** (-3.0 * t / rt)

    ir = lo * dec(rt60 * 1.15) * 1.2 + mid * dec(rt60) + hi * dec(max(rt60 * damp, 0.05)) * 0.8
    ir *= 1.0 - np.exp(-t / (0.006 * size + 0.002))
    for _ in range(10):
        d = r.uniform(0.003, 0.045 * size)
        i = int(d * SR)
        if i < n:
            ir[i] += r.choice([-1, 1]) * r.uniform(0.4, 1.2) * (1.0 - d / (0.06 * size + 0.02))
    if pre > 0:
        ir = np.concatenate([np.zeros(N(pre)), ir])
    ir = fade_edges(ir, 0, 0.05)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
    _ir_cache[key] = ir
    return ir


def reverb(x, rt60=1.5, wet=0.3, pre=0.0, damp=0.5, seed=1, size=1.0, tail=None, stereo=None):
    """Réverbération par convolution. x : mono (n,) ou stéréo (n,2).
    Retourne même forme, rallongée de `tail` s (défaut : ~rt60)."""
    stereo_in = x.ndim == 2
    if stereo is None:
        stereo = stereo_in
    tail_n = N(rt60 if tail is None else tail)
    n = len(x)
    out_n = n + tail_n
    if not stereo:
        ir = make_ir(rt60, pre, damp, seed, size, 0)
        y = sg.fftconvolve(x if not stereo_in else x.mean(axis=1), ir)[:out_n]
        res = np.zeros(out_n)
        res[:n] += x if not stereo_in else x.mean(axis=1)
        res[:len(y)] += wet * y
        return res
    res = np.zeros((out_n, 2))
    for c in range(2):
        src = x[:, c] if stereo_in else x
        ir = make_ir(rt60, pre, damp, seed, size, c)
        y = sg.fftconvolve(src, ir)[:out_n]
        res[:n, c] += src
        res[:len(y), c] += wet * y
    return res


def reverb_circ(x, rt60=2.0, wet=0.3, pre=0.0, damp=0.5, seed=1, size=1.0):
    """Réverbération circulaire (boucles) : la queue est repliée sur le début. x stéréo."""
    L = len(x)
    res = np.zeros((L, 2))
    for c in range(2):
        src = x[:, c] if x.ndim == 2 else x
        ir = make_ir(rt60, pre, damp, seed, size, c)
        y = sg.fftconvolve(src, ir)
        wetc = np.zeros(L)
        k = 0
        while k * L < len(y):
            seg = y[k * L:(k + 1) * L]
            wetc[:len(seg)] += seg
            k += 1
        res[:, c] = src + wet * wetc
    return res


def pan(x, p):
    """Panoramique équi-puissance, p in [-1, 1]. Retourne (n, 2)."""
    a = (p + 1.0) * 0.25 * np.pi
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)


def haas(x, ms=12.0, side=1):
    d = N(ms / 1000.0)
    y = np.concatenate([np.zeros(d), x])[:len(x)]
    return np.stack([x, y], 1) if side > 0 else np.stack([y, x], 1)


def to_mono(x):
    return x if x.ndim == 1 else x.mean(axis=1)


def speed(x, ratio):
    """Changement de vitesse (hauteur+durée) par interpolation."""
    n = int((len(x) - 1) / ratio)
    idx = np.arange(n) * ratio
    return np.interp(idx, np.arange(len(x)), x)


# ---------------------------------------------------------------- dynamique / finition
def limiter(x, thr, look=0.003, hold=0.03, circular=False):
    a = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    g = np.minimum(1.0, thr / np.maximum(a, 1e-9))
    mode = 'wrap' if circular else 'nearest'
    g = minimum_filter1d(g, size=2 * N(hold) + 1, mode=mode)
    g = uniform_filter1d(g, size=2 * N(look) + 1, mode=mode)
    g = np.minimum(g, 1.0)
    return x * (g if x.ndim == 1 else g[:, None])


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))


def peak(x):
    return float(np.max(np.abs(x)))


def tame_crest(x, max_crest_db=15.0):
    """Écrête en douceur les transitoires trop pointus avant normalisation."""
    nz = np.abs(x) > 0.02 * peak(x)
    r = rms(x[nz]) if nz.any() else rms(x)
    thr = r * dbv(max_crest_db)
    if peak(x) > thr:
        x = limiter(x, thr, look=0.0015, hold=0.01)
    return x


def trim_tail(x, floor_db=-58.0, keep=0.0):
    p = peak(x)
    thr = p * dbv(floor_db)
    a = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    idx = np.nonzero(a > thr)[0]
    if len(idx) == 0:
        return x
    end = min(len(x), idx[-1] + 1 + N(keep))
    return x[:end]


def finish(x, peak_db=-3.0, fin=0.0012, fout=0.015, trim=True, crest=15.0, loop=False):
    x = np.asarray(x, float)
    if not loop:
        x = x - np.mean(x, axis=0)
        x = dc_block(x, 18.0)
        if trim:
            x = trim_tail(x, -56.0, 0.0)
        if crest:
            x = tame_crest(x, crest)
        x = fade_edges(x, fin, fout)
    p = peak(x)
    if p > 0:
        x = x * (dbv(peak_db) / p)
    return x


def write_wav(path, x):
    import soundfile as sf
    sf.write(path, np.clip(x, -1, 1), SR, subtype='PCM_16')


class Sig(np.ndarray):
    """ndarray dont l'addition/soustraction de longueurs différentes complète par du silence."""

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if method == '__call__' and len(inputs) == 2 and ufunc in (np.add, np.subtract):
            a, b = inputs
            if (isinstance(a, np.ndarray) and isinstance(b, np.ndarray) and a.ndim == 1 and b.ndim == 1
                    and len(a) != len(b)):
                n = max(len(a), len(b))
                a = np.concatenate([np.asarray(a), np.zeros(n - len(a))])
                b = np.concatenate([np.asarray(b), np.zeros(n - len(b))])
                inputs = (a, b)
        inputs = tuple(np.asarray(i) if isinstance(i, Sig) else i for i in inputs)
        if 'out' in kwargs:
            kwargs['out'] = tuple(np.asarray(o) if isinstance(o, Sig) else o for o in kwargs['out'])
        res = getattr(ufunc, method)(*inputs, **kwargs)
        if isinstance(res, np.ndarray) and res.ndim >= 1:
            return res.view(Sig)
        return res


def sigwrap(fn):
    def w(*a, **k):
        y = fn(*a, **k)
        return y.view(Sig) if isinstance(y, np.ndarray) and y.ndim >= 1 else y
    w.__name__ = fn.__name__
    w.__doc__ = fn.__doc__
    return w


def wrap_module(ns, names):
    for nme in names:
        ns[nme] = sigwrap(ns[nme])


def add_smpl_loop(path, n):
    """Ajoute un chunk RIFF 'smpl' (boucle avant 0..n-1) : Godot détecte la boucle depuis le WAV."""
    import struct
    with open(path, 'rb') as f:
        data = f.read()
    smpl = struct.pack('<9I', 0, 0, int(1e9 / SR), 60, 0, 0, 0, 1, 0) + struct.pack('<6I', 0, 0, 0, n - 1, 0, 0)
    data += b'smpl' + struct.pack('<I', len(smpl)) + smpl
    data = data[:4] + struct.pack('<I', len(data) - 8) + data[8:]
    with open(path, 'wb') as f:
        f.write(data)
