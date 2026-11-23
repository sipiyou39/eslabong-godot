"""Contrôle qualité par calcul : niveaux, clics, DC, boucles, spectre + planches spectrogrammes (PNG)."""
import sys, os, glob, json
import numpy as np
import soundfile as sf
from scipy import signal as sg
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'audio'))
SCRATCH = '/tmp/eslabong_scratch'


def db(x):
    return 20 * np.log10(max(float(x), 1e-12))


def analyze(path, loop=False):
    x, sr = sf.read(path, dtype='float64')
    mono = x if x.ndim == 1 else x.mean(axis=1)
    n = len(mono)
    pk = np.max(np.abs(x))
    rms = np.sqrt(np.mean(mono ** 2))
    # court terme : fenêtre de 300 ms la plus forte
    w = int(0.3 * sr)
    if n > w:
        cs = np.concatenate([[0.0], np.cumsum(mono ** 2)])
        st = np.sqrt(((cs[w:] - cs[:-w]) / w).max())
    else:
        st = rms
    f, P = sg.welch(mono, sr, nperseg=min(4096, n))
    cent = float((f * P).sum() / (P.sum() + 1e-18))
    d = np.diff(mono)
    out = dict(dur=n / sr, ch=1 if x.ndim == 1 else x.shape[1], peak_db=db(pk), rms_db=db(rms), st_db=db(st),
               crest=db(pk) - db(rms), centroid=cent, dc=float(np.mean(mono)),
               start=float(np.max(np.abs(x[:2]))), end=float(np.max(np.abs(x[-2:]))),
               nan=bool(np.isnan(x).any()), clip=int(np.sum(np.abs(x) >= 0.9999)),
               maxjump=float(np.max(np.abs(d))) if len(d) else 0.0)
    # tranche de 20 ms la plus longue de silence en milieu
    if loop:
        seam = abs(float(mono[0] - mono[-1]))
        out['seam'] = seam
        out['seam_ratio'] = seam / (np.percentile(np.abs(d), 99) + 1e-9)
    return out


def clicks(x, sr=44100):
    """Détecte les discontinuités (clics) en milieu de son : saut de dérivée seconde très supérieur au contexte,
    hors attaques (le contexte précédent doit être non silencieux)."""
    m = x if x.ndim == 1 else x.mean(axis=1)
    d2 = np.abs(np.diff(m, 2))
    w = int(0.004 * sr)
    pre = np.convolve(m ** 2, np.ones(w) / w, mode='full')[:len(m)]
    ctx = np.sqrt(np.maximum(np.convolve(d2 ** 2, np.ones(w) / w, mode='full')[:len(d2)], 1e-14))
    pk = np.max(np.abs(m))
    out = []
    i = 0
    n = len(d2)
    for i in np.nonzero((d2 > 0.012 * pk / 0.7) & (d2 > 12 * np.roll(ctx, int(0.0005 * sr))))[0]:
        if i < int(0.03 * sr) or i > n - 5:
            continue
        # contexte précédent non silencieux (sinon c'est une attaque légitime)
        if np.sqrt(pre[max(i - w, 0)]) < 0.02 * pk:
            continue
        if not out or i - out[-1] > int(0.01 * sr):
            out.append(int(i))
    return out


def check_all(files=None):
    issues = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'sfx', '*.wav'))):
        base = os.path.basename(p)
        if files and not any(f in base for f in files):
            continue
        loop = 'loop' in base
        a = analyze(p, loop)
        msg = []
        if a['nan']:
            msg.append('NaN')
        if a['clip']:
            msg.append(f"clip{a['clip']}")
        if a['peak_db'] > -2.5 or a['peak_db'] < -3.6:
            msg.append(f"peak{a['peak_db']:.1f}")
        if abs(a['dc']) > 0.003:
            msg.append(f"dc{a['dc']:.4f}")
        if not loop and (a['start'] > 0.01):
            msg.append(f"start{a['start']:.3f}")
        if not loop and (a['end'] > 0.003):
            msg.append(f"end{a['end']:.4f}")
        if loop and a['seam_ratio'] > 1.5:
            msg.append(f"seam{a['seam_ratio']:.2f}")
        if a['dur'] < 0.04 or a['dur'] > 25:
            msg.append(f"dur{a['dur']:.2f}")
        xx, _ = sf.read(p)
        ck = clicks(xx)
        if ck:
            msg.append('clicks@' + ','.join(f'{c/44100:.3f}' for c in ck[:4]))
        if msg:
            issues.append((base, msg))
        print(f"{base:32s} {a['dur']:5.2f}s ch{a['ch']} pk{a['peak_db']:6.1f} rms{a['rms_db']:6.1f} st{a['st_db']:6.1f} cr{a['crest']:5.1f} cent{a['centroid']:6.0f} {' '.join(msg)}")
    print('ISSUES:', len(issues))
    for i in issues:
        print(' ', i)


# ---------------------------------------------------------------- planches
def _cmap(v):
    v = np.clip(v, 0, 1)
    r = np.clip(3 * v - 1.0, 0, 1)
    g = np.clip(3 * v - 0.2 - (v > 0.8) * 0, 0, 1) * (v > 0.1)
    b = np.clip(1.5 - 3 * np.abs(v - 0.3), 0, 1) * 0.9 + np.clip(3 * v - 2, 0, 1)
    return np.stack([r * 255, g * 200 * (0.5 + 0.5 * v), np.clip(b, 0, 1) * 255], -1).astype(np.uint8)


def spec_image(path, w=520, h=150, fmax=12000):
    x, sr = sf.read(path, dtype='float64')
    mono = x if x.ndim == 1 else x.mean(axis=1)
    nper = 1024 if len(mono) < sr * 6 else 2048
    f, t, S = sg.spectrogram(mono, sr, nperseg=nper, noverlap=nper * 3 // 4, mode='magnitude')
    keep = f <= fmax
    S = 20 * np.log10(S[keep] + 1e-7)
    S = (S - (S.max() - 80)) / 80
    img = _cmap(S[::-1])
    im = Image.fromarray(img).resize((w, h), Image.BILINEAR)
    # forme d'onde
    wv = Image.new('RGB', (w, 40), (20, 20, 28))
    dr = ImageDraw.Draw(wv)
    seg = np.array_split(np.abs(mono), w)
    for i, s in enumerate(seg):
        a = s.max() if len(s) else 0
        dr.line([(i, 20 - a * 19), (i, 20 + a * 19)], fill=(120, 200, 255))
    out = Image.new('RGB', (w, h + 40 + 14), (0, 0, 0))
    out.paste(wv, (0, 14))
    out.paste(im, (0, 54))
    ImageDraw.Draw(out).text((2, 1), f"{os.path.basename(path)} {len(mono)/sr:.2f}s", fill=(255, 255, 255))
    return out


def sheet(names, out_name='sheet.png', cols=2, sub='sfx'):
    ims = []
    for nme in names:
        p = os.path.join(ROOT, sub, nme if nme.endswith(('.wav', '.ogg')) else nme + '.wav')
        if sub == 'music' and not os.path.exists(p):
            continue
        ims.append(spec_image(p))
    rows = (len(ims) + cols - 1) // cols
    W = ims[0].width
    H = ims[0].height
    S = Image.new('RGB', (cols * W, rows * H))
    for i, im in enumerate(ims):
        S.paste(im, ((i % cols) * W, (i // cols) * H))
    p = os.path.join(SCRATCH, out_name)
    S.save(p)
    print(p)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sheet':
        sheet(sys.argv[3:], sys.argv[2])
    else:
        check_all(sys.argv[1:])


def a_weight_db(f):
    f2 = np.maximum(f, 1.0) ** 2
    ra = (12194.0 ** 2 * f2 ** 2) / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194.0 ** 2))
    return 20 * np.log10(ra + 1e-12) + 2.0


def a_share_above(path, fc=200.0):
    x, sr = sf.read(path, dtype='float64')
    m = x if x.ndim == 1 else x.mean(axis=1)
    f, P = sg.welch(m, sr, nperseg=min(4096, len(m)))
    Pa = P * 10 ** (a_weight_db(f) / 10)
    return float(Pa[f > fc].sum() / Pa.sum())
