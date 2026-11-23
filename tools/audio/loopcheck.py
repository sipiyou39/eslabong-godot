"""Vérifie une musique : niveaux par section, couture de boucle (wav décodé de l'ogg), clics."""
import sys, os, subprocess, numpy as np, soundfile as sf
import qa
from dsp import SR, to_db


def check(name, bars=None, bpm=None):
    ogg = os.path.join(qa.ROOT, 'music', name + '.ogg')
    wav = os.path.join(qa.SCRATCH, name + '_dec.wav')
    subprocess.run(['/opt/homebrew/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', ogg, wav], check=True)
    x, sr = sf.read(wav)
    m = x.mean(axis=1)
    n = len(m)
    # niveau par fenêtre de 4 s
    win = 4 * sr
    lv = [round(to_db(np.sqrt(np.mean(m[i:i + win] ** 2))), 1) for i in range(0, n - win + 1, win)]
    # couture : saut à la jonction vs saut typique
    d = np.abs(np.diff(np.roll(m, n // 2)))
    j = n // 2 - 1
    ctx = np.percentile(d, 99.5)
    # énergie HF autour de la couture (clic) vs ailleurs
    import scipy.signal as sg
    hf = sg.sosfilt(sg.butter(4, 6000, 'highpass', fs=sr, output='sos'), np.roll(m, n // 2))
    seam_hf = np.sqrt(np.mean(hf[j - 200:j + 200] ** 2))
    typ_hf = np.sqrt(np.mean(hf ** 2))
    print(f"{name}: {n/sr:.1f}s peak {to_db(np.max(np.abs(x))):.1f} rms {to_db(np.sqrt(np.mean(m**2))):.1f}")
    print('   level/4s:', lv)
    print(f'   seam jump {d[j]:.4f} (p99.5 {ctx:.4f})  HF@seam {to_db(seam_hf):.1f} vs avg {to_db(typ_hf):.1f} dB')
    # fade check : début/fin
    print(f'   start |x|={np.max(np.abs(x[:3])):.4f} end |x|={np.max(np.abs(x[-3:])):.4f}  clip={int(np.sum(np.abs(x)>=0.9999))}')


if __name__ == '__main__':
    for n in sys.argv[1:]:
        check(n)
