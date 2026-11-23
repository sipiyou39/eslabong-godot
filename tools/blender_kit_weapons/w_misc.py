from wcommon import *
from registry import weapon


def link(c, T, N, a=0.02, b=0.012, r=0.0052, color=G, n=6):
    T, N = unit(T), unit(N)
    ph = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pts = np.asarray(c) + np.outer(np.cos(ph) * a, T) + np.outer(np.sin(ph) * b, N)
    return tube(pts, r, seg=4, color=color, closed_path=True)


def chain(path, a=0.02, b=0.0125, r=0.0052, color=G, spacing=None):
    path = np.asarray(path, float)
    seglen = np.linalg.norm(np.diff(path, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seglen)])
    sp = spacing or (a * 1.55)
    ds = np.arange(0, cum[-1], sp)
    out = []
    side = np.array([1.0, 0, 0])
    for k, d in enumerate(ds):
        i = min(np.searchsorted(cum, d, side="right") - 1, len(path) - 2)
        f = (d - cum[i]) / max(seglen[i], 1e-9)
        c = path[i] * (1 - f) + path[i + 1] * f
        T = path[i + 1] - path[i]
        N = side if k % 2 == 0 else np.cross(T, side)
        if np.linalg.norm(N) < 1e-6:
            N = np.array([0, 0, 1.0])
        N = N - unit(T) * (N @ unit(T))
        out.append(link(c, T, N, a, b, r, color))
    return out


@weapon("wpn_tome", accent=(0.6, 0.7, 1.0), notes="grimoire 0,3 m, dos vers -Z, face +Z, dos du livre côté -X", views="front,tq")
def tome():
    p = []
    W, H, T = 0.22, 0.3, 0.075
    p.append(box((W, H, 0.014), (0, 0, T / 2 - 0.007), color=R, bevel=0.005))
    p.append(box((W, H, 0.014), (0, 0, -T / 2 + 0.007), color=R, bevel=0.005))
    p.append(box((0.026, H, T), (-W / 2 + 0.013, 0, 0), color=R, bevel=0.006))
    p.append(box((W - 0.03, H - 0.024, T - 0.024), (0.008, 0, 0), color=K, bevel=0.002))
    for s in (1, -1):
        for yy in (s * (H / 2 - 0.02),):
            p.append(box((0.05, 0.05, 0.012), (W / 2 - 0.025, yy, T / 2 + 0.002), color=G, bevel=0.003))
            p.append(box((0.05, 0.05, 0.012), (-W / 2 + 0.025, yy, T / 2 + 0.002), color=G, bevel=0.003))
            p.append(box((0.05, 0.05, 0.012), (W / 2 - 0.025, yy, -T / 2 - 0.002), color=G, bevel=0.003))
            p.append(box((0.05, 0.05, 0.012), (-W / 2 + 0.025, yy, -T / 2 - 0.002), color=G, bevel=0.003))
    for yy in (-0.095, 0.0, 0.095):
        p.append(box((0.032, 0.014, T + 0.012), (-W / 2 + 0.013, yy, 0), color=G, bevel=0.003))
    # fermoir
    p.append(box((0.026, 0.07, 0.012), (W / 2 - 0.004, 0, T / 2 + 0.002), color=G, bevel=0.003))
    p.append(box((0.016, 0.07, T + 0.01), (W / 2 + 0.002, 0, 0), color=G, bevel=0.003))
    # emblème : gemme + anneau
    p.append(gem(0.034, 0.05, 6, B, pos=(0.004, 0.015, T / 2 + 0.008), rot=(90, 0, 0), s=(1, 0.4, 1)))
    p.append(torus(0.062, 0.006, 20, 4, plane="XY", color=B, pos=(0.004, 0.015, T / 2 + 0.004)))
    for k in range(4):
        a = math.radians(90 * k)
        p.append(cone(0.01, 0.034, 4, B, pos=(0.004 + 0.07 * math.cos(a), 0.015 + 0.07 * math.sin(a), T / 2 + 0.004), rot=(0, 0, -90 * k)))
    return p


@weapon("wpn_orb", accent=(0.7, 0.4, 1.0), notes="orbe 0,24 m dans un support à griffes, dos vers -Z", views="front,tq")
def orb():
    p = []
    p.append(sphere(0.098, 14, 10, B, pos=(0, 0.0, 0.0)))
    p.append(lathe([(0.03, -0.17), (0.045, -0.15), (0.05, -0.13), (0.07, -0.108), (0.05, -0.095), (0.0, -0.095)], 10, G, bevel=0.002).xf(rot=(0, 0, 0)))
    p += prongs_xy()
    p.append(torus(0.108, 0.009, 24, 5, plane="XZ", color=G).xf(rot=(0, 0, 28)))
    p.append(torus(0.118, 0.007, 24, 5, plane="XY", color=G).xf(rot=(0, 35, 0)))
    for k in range(4):
        a = math.radians(90 * k + 45)
        p.append(gem(0.014, 0.034, 4, B, pos=(0.115 * math.cos(a), 0.115 * math.sin(a), 0.0), rot=(0, 0, -90 * k)))
    # support dos (vers -Z)
    p.append(lathe([(0.05, 0.0), (0.07, 0.015), (0.055, 0.04), (0.03, 0.05)], 10, G, bevel=0.002).xf(rot=(-90, 0, 0), pos=(0, 0, -0.1)))
    return p


def prongs_xy():
    out = []
    for k in range(3):
        a = math.radians(120 * k + 30)
        ca, sa = math.cos(a), math.sin(a)
        pts = bezier((0.04 * ca, -0.12, 0.04 * sa), (0.13 * ca, -0.1, 0.13 * sa), (0.14 * ca, -0.02, 0.14 * sa), (0.1 * ca, 0.06, 0.1 * sa), 9)
        out.append(tube(pts, np.linspace(0.011, 0.006, 9), seg=5, color=G))
    return out


@weapon("wpn_whip", accent=(1.0, 0.7, 0.3), notes="fouet 1,5 m : poignée + lanière en S, pointe vers +Y puis +Z", views="side,tq@top")
def whip():
    p = []
    p.append(grip(-0.11, 0.1, 0.0205, pitch=0.032))
    p.append(sphere(0.026, 8, 5, G, pos=(0, -0.125, 0.0)))
    p.append(band(0.105, 0.0225, 0.024, G))
    p.append(sphere(0.012, 5, 3, B, pos=(0.0, 0.125, 0)))
    seg1 = bezier((0, 0.12, 0), (0, 0.3, 0.02), (0.02, 0.5, 0.15), (0.0, 0.62, 0.34), 12)
    seg2 = bezier((0, 0.62, 0.34), (-0.02, 0.7, 0.5), (0.0, 0.62, 0.7), (0.05, 0.46, 0.78), 12)
    seg3 = bezier((0.05, 0.46, 0.78), (0.1, 0.34, 0.84), (0.18, 0.28, 0.76), (0.2, 0.34, 0.66), 10)
    path = np.concatenate([seg1, seg2[1:], seg3[1:]])
    t = np.linspace(0, 1, len(path))
    rad = 0.0125 * (1 - t) ** 0.8 + 0.0035
    p.append(tube(path, rad, seg=5, color=R))
    p.append(sphere(0.011, 5, 3, B, pos=path[-1]))
    return p


def glove_base(thumb=True):
    p = []
    p.append(lathe([(0.052, -0.17), (0.062, -0.15), (0.06, -0.1), (0.05, -0.07)], 10, G, bevel=0.003))
    p.append(band(-0.13, 0.062, 0.016, B, seg=10, flare=1.0))
    p.append(box((0.085, 0.12, 0.1), (0, -0.0, 0.0), color=R, bevel=0.018))
    for k in range(4):   # doigts repliés
        p.append(box((0.05, 0.05, 0.026), (0.0, 0.065, -0.037 + k * 0.025), color=R, bevel=0.007))
    if thumb:
        p.append(box((0.03, 0.026, 0.07), (-0.045, 0.025, 0.035), rot=(0, 0, 0), color=R, bevel=0.008))
    return p


@weapon("wpn_claws", accent=(0.9, 0.95, 1.0), pair=True, notes="gants à griffes (gauche = +X ; droite = miroir) : 3 lames vers +Y", views="side,tq")
def claws():
    p = glove_base()
    p.append(box((0.07, 0.03, 0.115), (0, 0.095, 0.0), color=G, bevel=0.006))
    for zi, L in ((-0.036, 0.36), (0.0, 0.43), (0.036, 0.36)):
        keys = [(0.105, 0.0165, 0.0075), (0.105 + L * 0.5, 0.0145, 0.0068), (0.105 + L * 0.85, 0.009, 0.0045), (0.105 + L, 0.0, 0.0)]
        p.append(blade(keys, ring_blade(e=0.2, bev=0.5), bend=lambda y, zi=zi, L=L: 0.18 * ((y - 0.105) / L) ** 2 * (0.5 + L), n_sub=3, base=(0, 0, zi)))
    return p


@weapon("wpn_fists", accent=(1.0, 0.85, 0.4), pair=True, notes="gantelets de lutteur (gauche = +X ; droite = miroir), poing vers +Y", views="side,tq")
def fists():
    p = glove_base()
    p.append(box((0.08, 0.034, 0.118), (0, 0.098, 0.0), color=G, bevel=0.008))
    for k in range(4):
        p.append(sphere(0.0165, 6, 4, B, pos=(0, 0.118, -0.04 + k * 0.027)))
        p.append(cone(0.011, 0.034, 4, B, pos=(0, 0.124, -0.04 + k * 0.027)))
    p.append(box((0.095, 0.03, 0.11), (0, -0.045, 0.0), color=G, bevel=0.007))
    return p


@weapon("wpn_paddles", accent=(0.55, 0.9, 1.0), pair=True, notes="palette de défibrillateur (gauche = +X ; droite = miroir), face +Z", views="side,tq")
def paddles():
    p = []
    p.append(lathe([(0.0225, -0.1), (0.027, -0.09), (0.027, 0.05), (0.022, 0.07)], 8, R, bevel=0.003))
    p.append(band(-0.1, 0.0, 0.0) if False else sphere(0.027, 6, 4, G, pos=(0, -0.102, 0.0)))
    p.append(band(0.0, 0.0285, 0.016, G))
    p.append(box((0.03, 0.026, 0.02), (0.0, 0.03, 0.026), color=B, bevel=0.004))
    p.append(tube([(0, 0.065, 0.0), (0, 0.11, 0.0), (0, 0.14, 0.03)], 0.016, seg=6, color=G))
    cy, cz = 0.18, 0.04
    disc = lathe([(0.0, -0.03), (0.098, -0.03), (0.104, -0.01), (0.1, 0.03), (0.075, 0.042), (0.0, 0.042)], 16, G, bevel=0.002)
    p.append(disc.xf(rot=(90, 0, 0), pos=(0, cy, cz)))
    p.append(lathe([(0.0, 0.0), (0.078, 0.0), (0.078, 0.01), (0.0, 0.012)], 16, B, bevel=0.002).xf(rot=(90, 0, 0), pos=(0, cy, cz + 0.044)))
    p.append(torus(0.088, 0.005, 20, 4, plane="XY", color=B, pos=(0, cy, cz + 0.048)))
    p.append(tube(bezier((0, -0.1, 0.0), (0, -0.2, 0.0), (0.0, -0.22, 0.05), (0.0, -0.3, 0.02), 10), 0.007, seg=4, color=G))
    return p


@weapon("wpn_censer", accent=(1.0, 0.55, 0.2), notes="encensoir sur chaîne, perche 0,85 m", views="side,tq")
def censer():
    p = []
    p.append(haft(-0.3, 0.45, 0.019, 0.0165, bow=0.0, seg=8))
    p.append(grip(-0.14, 0.1, 0.0225, pitch=0.034))
    p.append(sphere(0.026, 8, 5, G, pos=(0, -0.305, 0.0)))
    p.append(band(0.45, 0.022, 0.03))
    arm = bezier((0, 0.45, 0), (0, 0.58, 0.0), (0, 0.6, 0.15), (0, 0.5, 0.22), 10)
    p.append(tube(arm, 0.013, seg=6, color=G))
    p.append(sphere(0.017, 6, 4, B, pos=arm[-1]))
    ch = [(0, 0.49, 0.22), (0, 0.38, 0.22), (0, 0.27, 0.22)]
    p += chain(ch, 0.026, 0.015, 0.0055)
    cy = 0.14
    cz = 0.22
    p.append(lathe([(0.0, -0.095), (0.04, -0.09), (0.075, -0.045), (0.088, 0.0), (0.0, 0.0)], 12, G, bevel=0.002).xf(pos=(0, cy, cz)))
    p.append(lathe([(0.079, 0.0), (0.083, 0.012), (0.079, 0.022), (0.0, 0.022)], 12, B, bevel=0.0015).xf(pos=(0, cy + 0.0, cz)))
    p.append(lathe([(0.0, 0.0), (0.085, 0.0), (0.078, 0.04), (0.055, 0.08), (0.03, 0.105), (0.0, 0.118)], 12, G, bevel=0.002).xf(pos=(0, cy + 0.02, cz)))
    for k in range(6):
        a = math.radians(60 * k)
        p.append(box((0.01, 0.1, 0.01), (0.084 * math.cos(a), cy + 0.02, 0.084 * math.sin(a)), color=G, bevel=0.0015).xf(pos=(0, 0, 0)) if False else
                 sphere(0.01, 5, 3, B, pos=(0.075 * math.cos(a), cy + 0.052, cz + 0.075 * math.sin(a))))
    p.append(sphere(0.017, 6, 4, B, pos=(0, cy + 0.146, cz)))
    return p


@weapon("wpn_flail", accent=(1.0, 0.8, 0.5), notes="fléau d'armes 0,75 m, boule hérissée au bout d'une chaîne", views="side,tq")
def flail():
    p = []
    p.append(haft(-0.24, 0.2, 0.0185, 0.0185, bow=0.0))
    p.append(grip(-0.16, 0.1, 0.0235, pitch=0.034))
    p.append(sphere(0.027, 8, 5, G, pos=(0, -0.245, 0.0)))
    p.append(band(0.2, 0.025, 0.03))
    p.append(sphere(0.02, 6, 4, B, pos=(0, 0.23, 0)))
    path = bezier((0, 0.23, 0), (0, 0.45, 0.04), (0, 0.5, 0.3), (0, 0.22, 0.46), 14)
    p += chain(path, 0.03, 0.017, 0.0065)
    c = np.array([0, 0.14, 0.52])
    p.append(sphere(0.07, 10, 7, G, pos=c))
    p.append(torus(0.015, 0.006, 8, 4, plane="YZ", color=G, pos=(0, 0.2, 0.47)))
    pts = []
    for i in range(5):
        for j in range(6 if 0 < i < 4 else 1):
            th = math.pi * i / 4
            ph = 2 * math.pi * j / (6 if 0 < i < 4 else 1) + (math.pi / 6 if i % 2 else 0)
            d = np.array([math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph)])
            if d[2] < -0.75:
                continue
            pts.append(d)
    for d in pts:
        p.append(cyl(c + d * 0.06, c + d * 0.125, 0.017, 0.0, seg=4, color=B, phase=45))
    return p


@weapon("wpn_lantern", accent=(1.0, 0.75, 0.3), notes="lanterne 0,45 m portée par l'anse (origine = anse, lanterne sous Y=0)", views="side,tq")
def lantern():
    p = []
    arch = arc((0, -0.035, 0), 0.06, 0, 180, 12, "XY", ry=0.06)
    p.append(tube(arch, 0.0125, seg=6, color=G))
    p.append(grip(-0.012, 0.012, 0.0, color=R) if False else tube(arch[3:9], 0.019, seg=7, color=R))
    for s in (1, -1):
        p.append(sphere(0.016, 6, 4, B, pos=(s * 0.06, -0.035, 0)))
    p.append(torus(0.03, 0.007, 14, 4, plane="XZ", pos=(0, -0.045, 0), color=G))
    # toit
    p.append(lathe([(0.0, 0.0), (0.04, 0.012), (0.105, -0.03), (0.125, -0.07), (0.1, -0.075), (0.0, -0.075)], 6, G, bevel=0.003).xf(pos=(0, -0.05, 0), rot=(0, 30, 0)))
    p.append(sphere(0.02, 6, 4, B, pos=(0, -0.04, 0)))
    # verre (6 pans)
    p.append(lathe([(0.075, -0.13), (0.094, -0.18), (0.094, -0.3), (0.082, -0.355)], 6, B, phase=30, bevel=None).xf(pos=(0, 0.0, 0)))
    for k in range(6):
        a = math.radians(60 * k)
        ca, sa = math.cos(a), math.sin(a)
        p.append(cyl((0.108 * ca * 0.82, -0.13, 0.108 * sa * 0.82), (0.098 * ca, -0.358, 0.098 * sa), 0.01, 0.01, seg=4, color=G))
    p.append(lathe([(0.0, -0.355), (0.082, -0.355), (0.1, -0.375), (0.08, -0.41), (0.0, -0.41)], 6, G, bevel=0.003, phase=30))
    p.append(torus(0.0795, 0.011, 6, 4, plane="XZ", pos=(0, -0.135, 0), color=G, ).xf(pos=(0, 0, 0)))
    p.append(sphere(0.02, 6, 4, B, pos=(0, -0.405, 0)))
    return p
