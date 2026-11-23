from wcommon import *
from registry import weapon


def socket(y, r, h=0.12, color=G, flare=1.35, seg=8):
    return lathe([(r, y), (r * flare, y + 0.03), (r * 1.1, y + h * 0.55), (r * 1.05, y + h)], seg, color, bevel=0.003)


@weapon("wpn_spear", notes="lance 1,95 m, fer en feuille, gland rouge")
def spear():
    p = []
    p.append(haft(-0.62, 0.9, 0.02, 0.021, bow=0.0, seg=8))
    p.append(grip(-0.12, 0.12, 0.0235, pitch=0.034))
    p.append(cone(0.02, 0.08, 6, G, pos=(0, -0.62, 0.0), rot=(180, 0, 0)))
    p.append(band(-0.55, 0.0225, 0.03))
    p.append(socket(0.84, 0.0215, 0.12))
    keys = [(0.94, 0.036, 0.013), (1.01, 0.068, 0.016), (1.08, 0.064, 0.0155), (1.16, 0.042, 0.0115), (1.225, 0.017, 0.0065), (1.27, 0, 0)]
    p.append(blade(keys, ring_blade(e=0.2, bev=0.45, fuller=0.0), n_sub=2))
    # gland (tissu)
    for k in range(6):
        a = 360 * k / 6
        ar = math.radians(a)
        p0 = (0.024 * math.cos(ar), 0.87, 0.024 * math.sin(ar))
        p1 = (0.07 * math.cos(ar), 0.76, 0.07 * math.sin(ar))
        p.append(cyl(p0, p1, 0.012, 0.004, seg=4, color=R))
    return p


@weapon("wpn_halberd", notes="hallebarde 2,1 m : hache, pointe et crochet")
def halberd():
    p = []
    p.append(haft(-0.65, 1.0, 0.0205, 0.022, bow=0.0, seg=8))
    p.append(grip(-0.14, 0.14, 0.0245, pitch=0.036))
    p.append(cone(0.021, 0.09, 6, G, pos=(0, -0.65, 0.0), rot=(180, 0, 0)))
    p.append(band(-0.56, 0.0235, 0.03))
    p.append(band(0.28, 0.0225, 0.03))
    p.append(socket(0.95, 0.021, 0.14))
    head = [(1.0, 0.0), (1.0, 0.04), (1.075, 0.10), (1.13, 0.24), (1.04, 0.31), (0.93, 0.28), (0.86, 0.22), (0.89, 0.12), (0.93, 0.04), (0.93, 0.0)]
    ins = [0, 0, 0.012, 0.05, 0.06, 0.06, 0.05, 0.012, 0, 0]
    hh = [0.02, 0.02, 0.018, 0.013, 0.013, 0.013, 0.013, 0.018, 0.02, 0.02]
    p.append(plate(head, hh, ins))
    # crochet arrière
    hook = [(0.98, -0.02), (1.0, -0.12), (0.99, -0.2), (0.92, -0.215), (0.93, -0.16), (0.945, -0.05)]
    p.append(plate(hook, [0.018, 0.016, 0.014, 0.012, 0.014, 0.018], [0, 0.008, 0.015, 0.0, 0.0, 0], plane="YZ", color=G, edge_color=B))
    keys = [(1.0, 0.032, 0.0135), (1.12, 0.04, 0.0135), (1.22, 0.036, 0.012), (1.29, 0.022, 0.009), (1.35, 0.0, 0.0)]
    p.append(blade(keys, ring_blade(e=0.2, bev=0.5), n_sub=2))
    p.append(box((0.05, 0.08, 0.05), (0, 0.985, 0.0), color=G, bevel=0.006))
    return p


@weapon("wpn_scythe", notes="faux de guerre 1,7 m, lame vers +Z, tranchant intérieur")
def scythe():
    p = []
    p.append(haft(-0.66, 0.98, 0.0185, 0.0195, bow=0.015, seg=8))
    p.append(grip(-0.16, 0.12, 0.0235, pitch=0.036))
    p.append(cone(0.019, 0.08, 6, G, pos=(0, -0.66, 0.0), rot=(180, 0, 0)))
    p.append(band(-0.58, 0.021, 0.028))
    # poignée latérale
    p.append(tube([(0.0, 0.3, 0.0), (0.09, 0.28, -0.02), (0.15, 0.17, -0.02)], 0.0165, seg=6, color=R))
    p.append(sphere(0.02, 6, 4, G, pos=(0.15, 0.17, -0.02)))
    p.append(socket(0.93, 0.021, 0.1))
    Rr = 0.62
    a = np.radians(np.linspace(104, 12, 22))
    zc, yc = 0.0, 1.03 - Rr
    path = np.stack([np.zeros(len(a)), yc + Rr * np.sin(a), zc + Rr * np.cos(a) - 0.0], 1)
    tt = np.linspace(0, 1, len(a))
    wdt = 0.012 + 0.075 * np.sin(np.pi * np.clip(tt * 0.75 + 0.18, 0, 1)) ** 0.9
    wdt = 0.125 * (1 - tt) ** 0.75 + 0.002
    wdt[-1] = 0.0
    th = 0.014 * (1 - tt * 0.5)
    th[-1] = 0.0
    ringp, seg_c = ring_sabre()
    ringp = ringp.copy()
    ringp[:, 1] = (ringp[:, 1] + 1.0) * 0.5      # le dos = la ligne de chemin, tranchant côté +b (intérieur)
    p.append(sweep(path, ringp, scale=np.stack([th, wdt], 1), ref=(1, 0, 0), seg_colors=seg_c, cap_colors=(B, B)))
    p.append(box((0.05, 0.07, 0.06), (0, 1.0, 0.04), color=G, bevel=0.006))
    p.append(cone(0.016, 0.1, 6, B, pos=(0, 1.0, 0.0)))
    return p
