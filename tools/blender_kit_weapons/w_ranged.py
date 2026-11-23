from wcommon import *
from registry import weapon


def bow_parts(half, depth, limb, tipw, k=2.0, n=24, wrap=0.085, string_r=0.0055, tip_color=B, lam=False, recurve_in=False):
    p = []
    t = np.linspace(-1, 1, n)
    y = half * t
    z = -depth * (t ** 2 * (1 + k) - k * t ** 4)
    path = np.stack([np.zeros(n), y, z], 1)
    s = np.abs(t)
    sx = limb[0] + (tipw[0] - limb[0]) * s ** 1.3
    sz = limb[1] + (tipw[1] - limb[1]) * s ** 1.3
    # renflement central (poignée)
    sx = sx * (1 + 0.35 * np.exp(-(t / 0.1) ** 2))
    p.append(sweep(path, circle2(8), scale=np.stack([sx, sz], 1), ref=(1, 0, 0), color=R))
    # poignée cuir
    p.append(lathe([(0.021, -wrap), (0.025, -wrap + 0.012), (0.025, wrap - 0.012), (0.021, wrap)], 8, R, bevel=0.002, sx=1.0, sz=1.0).xf(pos=(0, 0, 0)))
    p.append(band(wrap + 0.015, 0.0255, 0.022, G, seg=8))
    p.append(band(-wrap - 0.015, 0.0255, 0.022, G, seg=8))
    tipz = z[-1]
    for sgn, i in ((1, -1), (-1, 0)):
        tp = path[i]
        p.append(sphere(0.014, 6, 4, tip_color, pos=tp + np.array([0, sgn * 0.005, 0.0]), s=(0.8, 1.3, 0.9)))
    # corde
    a, b = path[0], path[-1]
    p.append(tube([a, (a + b) / 2 + np.array([0, 0, -0.004]), b], string_r, seg=4, color=G))
    p.append(sphere(0.011, 6, 4, B, pos=(0, 0.0, tipz + 0.001), s=(0.8, 1.6, 0.8)))
    return p, tipz


@weapon("wpn_bow_long", notes="arc long 1,5 m ; branches le long de Y, ventre +Z, corde -Z", views="side,front")
def bow_long():
    p, _ = bow_parts(0.75, 0.2, (0.027, 0.02), (0.011, 0.009), k=2.0)
    # plaque de repos de flèche
    p.append(box((0.02, 0.05, 0.026), (0.0, 0.07, 0.012), color=G, bevel=0.003))
    for s in (1, -1):
        tt = 0.56
        zz = -0.2 * (tt ** 2 * 3 - 2 * tt ** 4)
        p.append(band(0.0, 0.017, 0.016, G, seg=8).xf(pos=(0, s * 0.75 * tt, zz), rot=(s * 14, 0, 0)))
    return p


@weapon("wpn_bow_short", notes="arc court recourbé 1,0 m")
def bow_short():
    p, _ = bow_parts(0.5, 0.17, (0.028, 0.021), (0.011, 0.009), k=3.0, wrap=0.07)
    p.append(box((0.02, 0.045, 0.026), (0.0, 0.06, 0.012), color=G, bevel=0.003))
    return p


def crossbow_parts(S=1.0, heavy=False):
    p = []
    top = 0.10 * S
    bot = 0.04 * S
    prof = [(top, -0.31 * S), (-0.085 * S, -0.30 * S), (-0.03 * S, -0.1 * S), (bot, 0.0), (bot, 0.44 * S), (top, 0.44 * S)]
    ins = [0.01, 0.01, 0.01, 0.0, 0.0, 0.0]
    hh = [0.027 * S] * 6
    p.append(plate(prof, hh, [0.012 * S, 0.012 * S, 0.012 * S, 0.012 * S, 0.012 * S, 0.012 * S], color=R, edge_color=R))
    # pistolet
    p.append(box((0.05 * S, 0.14 * S, 0.055 * S), (0, -0.02 * S, -0.04 * S), rot=(-14, 0, 0), color=R, bevel=0.006))
    # rail + noix
    p.append(box((0.026 * S, 0.014 * S, 0.5 * S), (0, top + 0.004 * S, 0.19 * S), color=G, bevel=0.003))
    p.append(box((0.034 * S, 0.026 * S, 0.04 * S), (0, top + 0.012 * S, 0.0), color=B, bevel=0.004))
    # pontet + détente
    gp = bezier((0, bot, 0.06 * S), (0, -0.07 * S, 0.075 * S), (0, -0.075 * S, -0.02 * S), (0, bot - 0.01 * S, -0.045 * S), 10)
    p.append(tube(gp, 0.006 * S, seg=5, color=G))
    p.append(box((0.01 * S, 0.04 * S, 0.012 * S), (0, 0.0, 0.01 * S), rot=(15, 0, 0), color=G, bevel=0.002))
    # crosse
    p.append(box((0.06 * S, 0.14 * S, 0.02 * S), (0, 0.005 * S, -0.305 * S), rot=(-4, 0, 0), color=G, bevel=0.004))
    # arc (prod)
    zp = 0.33 * S
    half = (0.40 if not heavy else 0.46) * S
    n = 18
    t = np.linspace(-1, 1, n)
    path = np.stack([half * t, np.full(n, top + 0.01 * S), zp + 0.1 * S * t ** 2 * (1.0 if not heavy else 0.8)], 1)
    s = np.abs(t)
    sy = (0.028 + 0.0 * s) * S * (1.0 - 0.45 * s ** 1.5) * (1.0 if not heavy else 1.15)
    sz = (0.02) * S * (1.0 - 0.4 * s ** 1.5)
    col = G if heavy else R
    p.append(sweep(path, circle2(6), scale=np.stack([sy, sy * 0 + sz], 1), ref=(0, 1, 0), color=col))
    if heavy:   # lames d'acier superposées + renforts
        path2 = path.copy()
        path2[:, 1] += 0.0
        p.append(sweep(path2, np.array([(-1, -1), (1, -1), (1, 1), (-1, 1)]), scale=np.stack([sy * 0.55, sz * 1.15], 1), ref=(0, 1, 0), color=B, bevel=0.003).xf(pos=(0, 0.0, 0.0)))
    p.append(box((0.1 * S, 0.06 * S, 0.075 * S), (0, top + 0.01 * S, zp), color=G, bevel=0.006))
    for sgn in (1, -1):
        p.append(sphere(0.015 * S, 6, 4, B, pos=path[0 if sgn < 0 else -1] + np.array([0, 0, 0.0])))
    # étrier
    p.append(torus(0.042 * S, 0.008 * S, 14, 5, plane="YZ", pos=(0, top + 0.01 * S, zp + 0.1 * S), color=G, ry=0.055 * S))
    # corde (tendue vers la noix)
    nut = np.array([0, top + 0.03 * S, 0.0])
    for sgn in (1, -1):
        tip = path[0 if sgn < 0 else -1] + np.array([0, 0.0, -0.005])
        p.append(tube([tip, (tip + nut) / 2 + np.array([0, 0.003 * S, 0]), nut], 0.0045 * S, seg=4, color=G))
    # carreau
    bz0, bz1 = 0.0, (0.44 + (0.05 if heavy else 0.03)) * S
    p.append(cyl((0, top + 0.03 * S, bz0), (0, top + 0.03 * S, bz1), 0.0075 * S, 0.0075 * S, seg=5, color=R))
    p.append(cyl((0, top + 0.03 * S, bz1), (0, top + 0.03 * S, bz1 + 0.07 * S), 0.0165 * S, 0.0, seg=4, color=B, phase=45))
    for k in range(3):
        a = k * 120
        ar = math.radians(a + 90)
        p.append(box((0.003, 0.028 * S, 0.06 * S), (0.0, top + 0.03 * S, 0.035 * S), rot=(0, 0, a), color=G, bevel=None).xf(pos=(0, 0, 0)) if False else
                 box((0.004, 0.034 * S, 0.06 * S), (0.0, 0, 0), rot=(0, 0, a), color=G, bevel=None).xf(pos=(0, top + 0.03 * S, 0.035 * S)))
    return p


@weapon("wpn_crossbow", notes="arbalète 0,8 m ; canon +Z, crosse -Z, carreau chargé", views="top,tq")
def crossbow():
    return crossbow_parts(1.0, False)


@weapon("wpn_crossbow_heavy", notes="arbalète lourde 1,0 m, arc d'acier et moulinet", views="top,tq")
def crossbow_heavy():
    S = 1.2
    p = crossbow_parts(S, True)
    # moulinet de bandage à l'arrière
    for sgn in (1, -1):
        p.append(cyl((sgn * 0.034 * S, 0.075 * S, -0.26 * S), (sgn * 0.06 * S, 0.075 * S, -0.26 * S), 0.045 * S, 0.045 * S, seg=10, color=G, bevel=0.004, roll=0).xf() if False else
                 cyl((sgn * 0.034 * S, 0.07 * S, -0.26 * S), (sgn * 0.07 * S, 0.07 * S, -0.26 * S), 0.048 * S, 0.048 * S, seg=10, color=G, bevel=0.004))
        for k in range(4):
            a = 45 + 90 * k
            ar = math.radians(a)
            p.append(box((0.016 * S, 0.008 * S, 0.1 * S), (sgn * 0.075 * S, 0.07 * S + 0.0, -0.26 * S), rot=(a, 0, 0), color=B, bevel=0.002))
    p.append(cyl((-0.08 * S, 0.07 * S, -0.26 * S), (0.08 * S, 0.07 * S, -0.26 * S), 0.01 * S, 0.01 * S, seg=6, color=G))
    p.append(box((0.07 * S, 0.012 * S, 0.12 * S), (0, 0.108 * S, 0.0), color=G, bevel=0.003))
    return p
