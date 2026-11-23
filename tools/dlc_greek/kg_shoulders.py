"""Épaulières grecques : shoulder_<nom>_l / _r, origine = pivot épaule (0.30,1.10,0)."""
from gk import *


def sh_laurel():
    out = [(place(dome(0.105, 0.065, n=14, steps=3), 20), R, {'angle': 60}), (rim(0.105, 20, -0.02, 0.011), G, {})]
    leaves = []
    C = SC.copy()
    for ring, (phb, pht, rho, cnt, off) in enumerate([(14, 62, 0.112, 11, 0.0), (52, 100, 0.118, 12, 0.5), (84, 128, 0.124, 11, 0.0)]):
        for i in range(cnt):
            a = 2 * math.pi * (i + off) / cnt
            ca, sa = math.cos(a), math.sin(a)

            def pt(phi, r):
                ph = math.radians(phi)
                return C + np.array([r * math.sin(ph) * ca, r * math.cos(ph) - 0.02 * (ph > 1.2), r * math.sin(ph) * sa])
            b = pt(phb, rho)
            t = pt(pht, rho * 1.12)
            nrm = np.array([math.sin(math.radians(pht)) * ca, math.cos(math.radians(pht)), math.sin(math.radians(pht)) * sa])
            leaves.append(leaf4(b, t, 0.034, 0.007, up=nrm))
    out.append((merge(leaves), B, {'angle': 80}))
    out.append((place(sphere(0.018, 0.018, 0.018, n=6, m=4), 20, 0.0, 0.085), B, {}))
    return mk("laurel", out)


def sh_gorget():
    out = []
    for k, (rr, h, dy, dx) in enumerate([(0.158, 0.1, 0.0, 0.0), (0.128, 0.09, 0.03, 0.0)]):
        out.append((place(dome(rr, h, n=18, steps=4), 20, dx, dy), R, {'angle': 60}))
        out.append((rim(rr, 20, dy - 0.02, 0.012, dx, 0.0), B, {}))
    out.append((place(sphere(0.042, 0.036, 0.042, n=8, m=5), 20, 0.0, 0.12), B, {}))
    for i in range(8):
        a = 2 * math.pi * i / 8
        out.append((place(sphere(0.01, 0.01, 0.01, n=5, m=3), 20, 0.15 * math.cos(a), 0.0, 0.15 * math.sin(a)), B, {}))
    return mk("gorget", out)


def sh_pteruges():
    out = [(place(dome(0.13, 0.075, n=18, steps=4), 20), R, {'angle': 60}), (rim(0.13, 20, -0.02, 0.012), B, {})]
    cx = 0.318
    hem = lambda a: -0.03 * (0.5 - 0.5 * math.cos(9 * a))
    out.append((skirt(1.15, 0.9, (0.128, 0.128), (0.15, 0.15), n=27, k=4, folds=9, fold_amp=0.012, cx=cx, cz=0.0, hem_fn=hem, e=2.0), G, {'angle': 50}))
    hem2 = lambda a: -0.025 * (0.5 - 0.5 * math.cos(9 * a + math.pi))
    out.append((skirt(1.17, 0.97, (0.12, 0.12), (0.14, 0.14), n=27, k=4, folds=9, fold_amp=0.01, cx=cx, cz=0.0, hem_fn=hem2, e=2.0), R, {'angle': 50}))
    for i in range(9):
        a = 2 * math.pi * i / 9 + 0.1
        out.append((sphere(0.009, 0.009, 0.009, n=5, m=3).t(cx + 0.14 * math.cos(a), 1.08, 0.14 * math.sin(a)), B, {}))
    out.append((place(sphere(0.02, 0.02, 0.02, n=6, m=4), 20, 0.0, 0.082), B, {}))
    return mk("pteruges", out)


SHOULDERS = [sh_laurel, sh_gorget, sh_pteruges]
