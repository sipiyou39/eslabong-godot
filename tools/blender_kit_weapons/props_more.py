from pcommon import *
from registry import prop
import w_swords, w_hafted, w_misc, w_shields


def chest_lid_parts(W=0.8, Rr=0.25):
    """couvercle : origine = charnière (arête arrière basse), s'étend en +Z (demi-cylindre d'axe X)."""
    p = []
    ang = np.linspace(0, 180, 13)
    prof = [(Rr * math.sin(math.radians(a)), Rr - Rr * math.cos(math.radians(a))) for a in ang]     # (y, z)
    p.append(slab(prof, W / 2, plane="YZ", color=R, bevel=0.008))
    for x in (-W / 2 + 0.08, W / 2 - 0.08):
        arc_pts = np.array([(x, (Rr + 0.012) * math.sin(math.radians(a)), Rr - (Rr + 0.012) * math.cos(math.radians(a))) for a in np.linspace(0, 180, 14)])
        p.append(sweep(arc_pts, np.array([(-1, -1), (1, -1), (1, 1), (-1, 1)]), scale=(0.028, 0.012), ref=(1, 0, 0), color=G, bevel=0.002))
    p.append(box((0.1, 0.075, 0.03), (0, 0.04, 2 * Rr + 0.005), color=G, bevel=0.005))
    p.append(box((0.04, 0.05, 0.02), (0, 0.035, 2 * Rr + 0.025), color=B, bevel=0.004))
    for s in (1, -1):
        p.append(cyl((s * (W / 2 - 0.16), 0.0, -0.005), (s * (W / 2 - 0.04), 0.0, -0.005), 0.024, 0.024, seg=8, color=G, bevel=0.002))
    return p


def chest_body_parts(W=0.8, Hb=0.34, D=0.5, loot=False):
    p = []
    p.append(box((W, Hb, D), (0, Hb / 2, 0), color=R, bevel=0.01))
    for x in (-W / 2 + 0.08, W / 2 - 0.08):
        p.append(box((0.06, Hb + 0.012, D + 0.012), (x, Hb / 2, 0), color=G, bevel=0.005))
    for sx in (1, -1):
        for sz in (1, -1):
            p.append(box((0.07, 0.07, 0.07), (sx * (W / 2 - 0.0), 0.035, sz * (D / 2 - 0.0)), color=G, bevel=0.008))
            p.append(sphere(0.012, 5, 3, B, pos=(sx * (W / 2 + 0.002), Hb - 0.05, sz * (D / 2 - 0.05))))
    p.append(box((W + 0.015, 0.045, D + 0.015), (0, 0.05, 0), color=G, bevel=0.004))
    p.append(box((W + 0.015, 0.035, D + 0.015), (0, Hb - 0.02, 0), color=G, bevel=0.004))
    p.append(box((0.1, 0.1, 0.03), (0, Hb - 0.08, D / 2 + 0.01), color=G, bevel=0.005))
    if loot:
        rng = np.random.RandomState(4)
        p.append(box((W - 0.06, 0.02, D - 0.06), (0, Hb + 0.002, 0), color=G, bevel=0.003))
        for k in range(14):
            x = rng.uniform(-W / 2 + 0.08, W / 2 - 0.08)
            z = rng.uniform(-D / 2 + 0.08, D / 2 - 0.08)
            hh = 0.04 + 0.05 * (1 - (abs(x) / (W / 2)) ** 2)
            p.append(cyl((x, Hb, z), (x + 0.01, Hb + hh, z), 0.04, 0.035, seg=8, color=B, bevel=None))
        p.append(gem(0.04, 0.08, 6, B, pos=(0.1, Hb + 0.1, 0.0)))
    return p


@prop("prop_chest_closed", accent=(1.0, 0.8, 0.3), notes="coffre fermé 0,8x0,6x0,5 (corps + couvercle assemblés). Charnière = (0,0.34,-0.25)")
def chest_closed():
    p = chest_body_parts(loot=False)
    lid = chest_lid_parts()
    p += [q.xf(pos=(0, 0.34, -0.25)) for q in lid]
    return p


@prop("prop_chest_lid", accent=(1.0, 0.8, 0.3), notes="couvercle seul ; ORIGINE = charnière ; pour fermer, le placer en (0,0.34,-0.25) ; ouvrir = rotation autour de X négative")
def chest_lid():
    return chest_lid_parts()


@prop("prop_chest_body_open", accent=(1.0, 0.8, 0.3), notes="EXTRA (hors contrat) : corps du coffre sans couvercle, avec butin visible ; à utiliser avec prop_chest_lid ouvert")
def chest_body_open():
    return chest_body_parts(loot=True)


@prop("prop_trophy_cup", accent=(1.0, 0.8, 0.25), notes="coupe trophée 0,75 m sur socle bois")
def trophy_cup():
    p = []
    p.append(box((0.34, 0.1, 0.34), (0, 0.05, 0), color=R, bevel=0.012))
    p.append(box((0.26, 0.05, 0.26), (0, 0.125, 0), color=R, bevel=0.008))
    p.append(box((0.14, 0.035, 0.016), (0, 0.06, 0.172), color=B, bevel=0.003))
    p.append(lathe([(0.0, 0.15), (0.12, 0.15), (0.12, 0.18), (0.07, 0.21), (0.045, 0.26), (0.05, 0.33), (0.035, 0.4), (0.0, 0.4)], 12, B, bevel=0.003))
    p.append(lathe([(0.0, 0.4), (0.06, 0.41), (0.085, 0.47), (0.13, 0.55), (0.165, 0.66), (0.17, 0.74), (0.155, 0.74), (0.15, 0.68), (0.11, 0.57), (0.0, 0.5)], 14, B, bevel=0.003))
    for s in (1, -1):
        h = bezier((s * 0.1, 0.62, 0), (s * 0.28, 0.66, 0), (s * 0.28, 0.46, 0), (s * 0.08, 0.5, 0), 10)
        p.append(tube(h, 0.017, seg=6, color=B))
    p.append(gem(0.04, 0.09, 6, G, pos=(0, 0.58, 0.14), rot=(90, 0, 0)))
    p.append(torus(0.09, 0.012, 16, 4, plane="XZ", pos=(0, 0.2, 0), color=G))
    return p


@prop("prop_coin_stack", accent=(1.0, 0.82, 0.3), notes="tas de pièces d'or : 3 piles + pièces éparses, 0,3 m")
def coin_stack():
    p = []
    rng = np.random.RandomState(7)
    def stack(cx, cz, n, r=0.06, h=0.018):
        out = []
        for i in range(n):
            ox, oz = rng.uniform(-0.006, 0.006, 2)
            out.append(cyl((cx + ox, i * h, cz + oz), (cx + ox, (i + 1) * h - 0.002, cz + oz), r, r, seg=9, color=B if i % 4 != 3 else G, bevel=None))
        return out
    p += stack(0.0, 0.0, 9)
    p += stack(0.14, 0.05, 6)
    p += stack(-0.11, 0.1, 4)
    p += stack(0.08, -0.13, 3)
    for k in range(7):
        a = rng.uniform(0, 6.28)
        r = rng.uniform(0.22, 0.34)
        p.append(cyl((r * math.cos(a), 0.012, r * math.sin(a)), (r * math.cos(a), 0.03, r * math.sin(a)), 0.055, 0.055, seg=8, color=B, bevel=None).xf(rot=(rng.uniform(-18, 18), 0, rng.uniform(-18, 18))))
    p.append(lathe([(0.0, 0.0), (0.12, 0.0), (0.08, 0.05), (0.0, 0.09)], 8, B).xf(pos=(-0.08, 0.0, -0.16)))
    return p


@prop("prop_banner_stand", accent=(0.9, 0.2, 0.2), notes="support de bannière 2,0 m avec bannière rouge (R) et emblème (B)")
def banner_stand():
    p = []
    p.append(box((0.5, 0.06, 0.12), (0, 0.03, 0), color=G, bevel=0.012))
    p.append(box((0.12, 0.06, 0.5), (0, 0.03, 0), color=G, bevel=0.012))
    p.append(lathe([(0.1, 0.06), (0.07, 0.12), (0.04, 0.22)], 8, G, bevel=0.003))
    p.append(cyl((0, 0.06, 0), (0, 1.95, 0), 0.03, 0.024, seg=8, color=R, bevel=None))
    p.append(cyl((-0.3, 1.78, 0), (0.3, 1.78, 0), 0.02, 0.02, seg=6, color=R, bevel=None))
    for s in (1, -1):
        p.append(sphere(0.035, 6, 4, B, pos=(s * 0.31, 1.78, 0)))
    p.append(cone(0.04, 0.14, 6, B, pos=(0, 1.93, 0)))
    # bannière ondulée
    nx, ny = 6, 10
    W, H = 0.5, 1.15
    top = 1.76
    rings = []
    for j in range(ny + 1):
        v = j / ny
        row = []
        for i in range(nx + 1):
            u = i / nx
            x = (u - 0.5) * W
            tip = 0.0
            if v > 0.82:
                tip = (v - 0.82) / 0.18 * (abs(u - 0.5) * 0.55)
            y = top - v * H + tip * 0.6 * 0
            z = 0.015 * math.sin(v * 6.0 + u * 3.0) * (0.3 + v)
            row.append((x, y, z))
        rings.append(row)
    # tissu : feuille mince (2 faces)
    Vf, Ff, Cf = [], [], []
    Vb = []
    cols = (nx + 1)
    for j in range(ny + 1):
        for i in range(nx + 1):
            x, y, z = rings[j][i]
            if j > int(ny * 0.84):
                f = (j - int(ny * 0.84)) / (ny - int(ny * 0.84))
                y -= f * 0.18 * (1 - abs(i / nx - 0.5) * 2)
            Vf.append((x, y, z + 0.006))
            Vb.append((x, y, z - 0.006))
    n_f = len(Vf)
    for j in range(ny):
        for i in range(nx):
            a, b, c, d = j * cols + i, j * cols + i + 1, (j + 1) * cols + i + 1, (j + 1) * cols + i
            Ff.append((a, b, c, d)); Cf.append(R)
            Ff.append((n_f + d, n_f + c, n_f + b, n_f + a)); Cf.append(R)
    for j in range(ny):
        Ff.append((j * cols, (j + 1) * cols, n_f + (j + 1) * cols, n_f + j * cols)); Cf.append(G)
        Ff.append(((j + 1) * cols + nx, j * cols + nx, n_f + j * cols + nx, n_f + (j + 1) * cols + nx)); Cf.append(G)
    for i in range(nx):
        Ff.append((i + 1, i, n_f + i, n_f + i + 1)); Cf.append(G)
        Ff.append(((ny) * cols + i, (ny) * cols + i + 1, n_f + ny * cols + i + 1, n_f + ny * cols + i)); Cf.append(G)
    p.append(mk(np.array(Vf + Vb), Ff, Cf))
    p.append(box((0.54, 0.05, 0.03), (0, top + 0.01, 0.0), color=G, bevel=0.005))
    p.append(lathe([(0.0, 0.0), (0.09, 0.012), (0.1, 0.03), (0.0, 0.042)], 8, B, bevel=0.002).xf(rot=(90, 0, 0), pos=(0, 1.35, 0.026)))
    p.append(gem(0.06, 0.14, 4, B, pos=(0, 1.35, 0.045), rot=(90, 0, 0)))
    p.append(box((0.5, 0.025, 0.015), (0, 1.62, 0.025), color=B, bevel=0.002))
    p.append(box((0.5, 0.025, 0.015), (0, 1.1, 0.025), color=B, bevel=0.002))
    return p


@prop("prop_training_dummy", notes="mannequin d'entraînement 1,7 m, bois et paille")
def training_dummy():
    p = []
    p.append(box((0.62, 0.07, 0.14), (0, 0.035, 0), color=R, bevel=0.01))
    p.append(box((0.14, 0.07, 0.62), (0, 0.035, 0), color=R, bevel=0.01))
    p.append(cyl((0, 0.05, 0), (0, 1.35, 0), 0.045, 0.045, seg=8, color=R, bevel=None))
    p.append(lathe([(0.0, 0.0), (0.12, 0.01), (0.17, 0.12), (0.18, 0.3), (0.15, 0.5), (0.09, 0.58), (0.0, 0.6)], 10, K).xf(pos=(0, 0.72, 0.0)))
    for yy in (0.82, 1.0, 1.18):
        p.append(band(yy, 0.185 - 0.01 * abs(yy - 1.0) * 3, 0.04, R, seg=10, flare=1.05))
    p.append(cyl((-0.4, 1.12, 0), (0.4, 1.12, 0), 0.032, 0.032, seg=6, color=R, bevel=None))
    for s in (1, -1):
        p.append(sphere(0.07, 7, 5, K, pos=(s * 0.42, 1.12, 0)))
        p.append(band(1.12, 0.04, 0.03, G, pos=(0, 0, 0)).xf(rot=(0, 0, 90)).xf(pos=(s * 0.3, 1.12 - 1.12 + 0.0, 0)) if False else
                 box((0.02, 0.09, 0.09), (s * 0.34, 1.12, 0), color=G, bevel=0.004))
    p.append(sphere(0.13, 9, 6, K, pos=(0, 1.5, 0), s=(0.95, 1.1, 1.0)))
    p.append(box((0.07, 0.014, 0.01), (0, 1.5, 0.13), color=G, bevel=None))
    p.append(box((0.014, 0.07, 0.01), (0, 1.5, 0.131), color=G, bevel=None))
    p.append(band(1.4, 0.075, 0.03, R, seg=8))
    return p


@prop("prop_weapon_rack", notes="râtelier d'armes 1,6 m de large (épées, hache, bouclier)", ao=0.14)
def weapon_rack():
    p = []
    for s in (1, -1):
        p.append(box((0.09, 1.5, 0.09), (s * 0.78, 0.75, 0), color=R, bevel=0.01))
        p.append(box((0.09, 0.09, 0.5), (s * 0.78, 0.045, 0), color=R, bevel=0.01))
        p.append(sphere(0.05, 6, 4, G, pos=(s * 0.78, 1.52, 0)))
    for y in (1.12, 0.62):
        p.append(box((1.64, 0.07, 0.07), (0, y, -0.03), color=R, bevel=0.008))
        for s in (1, -1):
            p.append(box((0.08, 0.1, 0.1), (s * 0.78, y, -0.03), color=G, bevel=0.005))
    for x in np.linspace(-0.55, 0.55, 4):
        for y in (1.12, 0.62):
            p.append(cyl((x, y, -0.02), (x, y + 0.02, 0.1), 0.02, 0.014, seg=5, color=G))
    p.append(box((1.64, 0.06, 0.4), (0, 0.3, 0.1), color=R, bevel=0.008))
    # armes (versions du kit) : épée, dague, hache, + bouclier simple et lances
    def put(parts, pos, rot, s=1.0):
        return [q.xf(rot=rot).xf(pos=pos, s=s) for q in parts]
    p += put(w_swords.sword_short(), (-0.5, 1.15, 0.1), (0, 0, 90))
    p += put(w_swords.dagger(), (0.5, 1.2, 0.1), (0, 0, 90))
    p += put(w_hafted.axe_hand(), (-0.4, 0.66, 0.1), (0, 0, 90))
    p.append(lathe([(0.0, -0.012), (0.2, -0.014), (0.2, 0.012), (0.1, 0.03), (0.0, 0.034)], 14, R, bevel=None).xf(rot=(90, 0, 0), pos=(0.5, 0.82, 0.13)))
    p.append(torus(0.2, 0.014, 18, 4, plane="XY", color=G, pos=(0.5, 0.82, 0.13)))
    p.append(sphere(0.045, 8, 5, B, pos=(0.5, 0.82, 0.17), s=(1, 1, 0.55)))
    for x in (0.1, 0.22):
        p.append(cyl((x, 0.3, 0.1), (x, 1.5, 0.1), 0.016, 0.016, seg=6, color=R))
        p.append(cone(0.03, 0.14, 4, B, pos=(x, 1.5, 0.1)))
    return p


def crystal_cluster(seed, n=7, h=0.9):
    rng = np.random.RandomState(seed)
    p = []
    p.append(lathe([(0.0, 0.0), (0.3, 0.0), (0.27, 0.07), (0.15, 0.13), (0.0, 0.15)], 7, G, bevel=0.004, phase=12))
    specs = [(0.0, 0.0, h, 0.085, 0, 0)]
    for k in range(n - 1):
        a = rng.uniform(0, 360)
        rr = rng.uniform(0.07, 0.19)
        hh = h * rng.uniform(0.35, 0.7)
        rd = rng.uniform(0.04, 0.07)
        tilt = rng.uniform(14, 34)
        specs.append((rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a)), hh, rd, a, tilt))
    for x, z, hh, rd, a, tilt in specs:
        c = lathe([(0.0, -0.02), (rd, 0.0), (rd * 0.95, hh * 0.68), (0.0, hh)], 6, B, phase=a)
        ar = math.radians(a)
        p.append(c.xf(rot=(math.sin(ar) * tilt, 0, -math.cos(ar) * tilt), pos=(x, 0.1, z)))
    return p


@prop("prop_crystal_blue", accent=(0.3, 0.6, 1.0), notes="amas de cristaux bleus 1,0 m, base rocheuse")
def crystal_blue():
    return crystal_cluster(3, 7, 0.9)


@prop("prop_crystal_red", accent=(1.0, 0.2, 0.25), notes="amas de cristaux rouges 0,95 m, base rocheuse")
def crystal_red():
    return crystal_cluster(11, 8, 0.82)


@prop("prop_brazier", accent=(1.0, 0.55, 0.15), notes="brasero 1,05 m, flammes en accent B")
def brazier():
    p = []
    for k in range(3):
        a = math.radians(120 * k + 30)
        foot = np.array([0.3 * math.cos(a), 0.0, 0.3 * math.sin(a)])
        top = np.array([0.15 * math.cos(a), 0.62, 0.15 * math.sin(a)])
        p.append(cyl(foot, top, 0.03, 0.04, seg=6, color=G))
        p.append(sphere(0.045, 6, 4, G, pos=foot + np.array([0, 0.046, 0])))
    p.append(lathe([(0.0, 0.58), (0.16, 0.6), (0.25, 0.7), (0.3, 0.82), (0.31, 0.86), (0.27, 0.86), (0.0, 0.7)], 12, G, bevel=0.003))
    p.append(band(0.86, 0.31, 0.04, R, seg=12, flare=1.0))
    for k in range(6):
        a = math.radians(60 * k)
        p.append(cone(0.03, 0.09, 4, G, pos=(0.31 * math.cos(a), 0.86, 0.31 * math.sin(a))))
    p.append(lathe([(0.0, 0.8), (0.2, 0.83), (0.24, 0.86), (0.0, 0.88)], 10, B))
    p.append(lathe([(0.0, 0.0), (0.12, 0.05), (0.15, 0.15), (0.1, 0.3), (0.05, 0.42), (0.0, 0.55)], 8, B).xf(pos=(0, 0.85, 0)))
    for k in range(4):
        a = math.radians(90 * k + 20)
        p.append(lathe([(0.0, 0.0), (0.06, 0.03), (0.05, 0.12), (0.0, 0.27)], 6, B).xf(rot=(math.sin(a) * 28, 0, -math.cos(a) * 28)).xf(pos=(0.15 * math.cos(a), 0.86, 0.15 * math.sin(a))))
    return p


@prop("prop_barrel", notes="tonneau 0,95 m, cerclages métal (G)")
def barrel():
    p = []
    prof = [(0.0, 0.0), (0.27, 0.0), (0.3, 0.04), (0.35, 0.25), (0.38, 0.47), (0.35, 0.69), (0.3, 0.9), (0.27, 0.94), (0.0, 0.94)]
    p.append(lathe(prof, 12, R, bevel=None))
    for y, r in ((0.12, 0.325), (0.3, 0.364), (0.64, 0.364), (0.82, 0.325)):
        p.append(band(y, r, 0.055, G, seg=12, flare=1.04))
    p.append(lathe([(0.0, 0.0), (0.26, 0.0), (0.26, 0.012), (0.0, 0.012)], 12, G).xf(pos=(0, 0.94, 0)))
    for k in range(3):
        p.append(box((0.5, 0.012, 0.045), (0, 0.955, -0.12 + k * 0.12), color=R, bevel=0.003))
    p.append(cyl((0.0, 0.5, 0.36), (0, 0.5, 0.42), 0.03, 0.026, seg=6, color=G))
    p.append(sphere(0.022, 5, 3, B, pos=(0, 0.5, 0.425)))
    return p


@prop("prop_crate", notes="caisse en bois 0,7 m, renforts métal")
def crate():
    p = []
    S = 0.7
    p.append(box((S, S, S), (0, S / 2, 0), color=R, bevel=0.012))
    e = 0.05
    for sx in (1, -1):
        for sz in (1, -1):
            p.append(box((e, S + 0.02, e), (sx * (S / 2 - e / 2 + 0.005), S / 2, sz * (S / 2 - e / 2 + 0.005)), color=R, bevel=0.006))
    for sy in (0, 1):
        y = e / 2 if sy == 0 else S - e / 2
        p.append(box((S + 0.02, e, e), (0, y, S / 2 - e / 2 + 0.005), color=R, bevel=0.006))
        p.append(box((S + 0.02, e, e), (0, y, -S / 2 + e / 2 - 0.005), color=R, bevel=0.006))
        p.append(box((e, e, S + 0.02), (S / 2 - e / 2 + 0.005, y, 0), color=R, bevel=0.006))
        p.append(box((e, e, S + 0.02), (-S / 2 + e / 2 - 0.005, y, 0), color=R, bevel=0.006))
    for z in (S / 2 + 0.004, -S / 2 - 0.004):
        d = math.degrees(math.atan2(S - 2 * e, S - 2 * e))
        p.append(box((0.04, math.sqrt(2) * (S - 2 * e), 0.016), (0, S / 2, z), rot=(0, 0, 45), color=R, bevel=0.003))
    for x in (S / 2 + 0.004, -S / 2 - 0.004):
        p.append(box((0.016, math.sqrt(2) * (S - 2 * e), 0.04), (x, S / 2, 0), rot=(45, 0, 0), color=R, bevel=0.003))
    for sx in (1, -1):
        for sz in (1, -1):
            for sy in (0, 1):
                p.append(box((0.08, 0.08, 0.08), (sx * (S / 2 - 0.01), 0.04 + sy * (S - 0.08), sz * (S / 2 - 0.01)), color=G, bevel=0.01))
    return p
