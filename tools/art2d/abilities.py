"""Icones de competences 128x128 : medaillon + motifs d'element + glyphe d'archetype + cadre metallique."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from shapes import *
import glyphs as GL
import statuses as STT
from vfx import bolt_pts

S, SS = 128, 4
N = S * SS
OUT = ASSETS + '/icons/abilities'
X, Y = np.meshgrid((np.arange(N, dtype=F32) + 0.5) / N * 2 - 1, (np.arange(N, dtype=F32) + 0.5) / N * 2 - 1)
R = np.hypot(X, Y)
TH = np.arctan2(Y, X)

BG = {'fire': ('#9a3412', '#2a0904'), 'ice': ('#1f6a94', '#06182a'), 'lightning': ('#85720f', '#241c03'), 'void': ('#52308f', '#12082c'),
      'shadow': ('#412a60', '#0e0818'), 'holy': ('#b08a22', '#3a2808'), 'blood': ('#82122a', '#26040a'), 'wind': ('#1f8070', '#062a28'),
      'earth': ('#725026', '#22160a'), 'arcane': ('#2150a6', '#07133a'), 'nature': ('#2e822e', '#0a2a0e'), 'physical': ('#626e84', '#181c28')}


def elem_mats(e):
    b = ELEM[e]
    hot = e in ('void', 'shadow', 'blood')
    return {'core': (np.ones(3, F32), lighten(b, 0.62)),
            'light': (lighten(b, 0.82 if hot else 0.7), mix(b, [0.5, 0.5, 0.5], 0.0) * 0.95),
            'mid': (lighten(b, 0.32), darken(b, 0.55)),
            'dark': (b * 0.7, darken(b, 0.85))}


# ------------------------------------------------------------------ motifs d'arriere-plan (calcules en 256 puis agrandis)
def _uv(n):
    y, x = np.mgrid[0:n, 0:n].astype(F32)
    return (x + 0.5) / n * 2 - 1, (y + 0.5) / n * 2 - 1


def pattern(e, rs, seed):
    n = 256
    x, y = _uv(n)
    r = np.hypot(x, y)
    th = np.arctan2(y, x)
    if e == 'fire':
        fb = fbm(n, n, 3, 4, seed)
        heat = np.clip(((y + 1) / 2 - 0.2) * 1.7 + fb * 0.8, 0, 1) ** 1.7
        st = np.sin(x * 10 + fb * 6) * 0.5 + 0.5
        p = heat * (0.55 + 0.45 * st)
    elif e == 'ice':
        f1, f2 = worley(n, n, 5, seed)
        p = (1 - np.clip((f2 - f1) * 5, 0, 1)) * 0.8 + 0.25 * np.clip(1 - f1, 0, 1) * (np.sin((x + y) * 6) * 0.5 + 0.5)
    elif e == 'lightning':
        D = Draw(n, n, 2, norm=False)
        for k in range(4):
            a = rs.uniform(0, 2 * math.pi)
            p0 = np.array([128 + 150 * math.cos(a), 128 + 150 * math.sin(a)])
            p1 = np.array([128 + 20 * rs.randn(), 128 + 20 * rs.randn()])
            D.path(bolt_pts(p0, p1, rs, 0.18, 5), 2.2)
        m = np.asarray(Image.fromarray(np.ascontiguousarray(D.mask()), 'F').resize((n, n), Image.LANCZOS))
        p = np.clip(m + blur(m, 3) * 0.9 + np.exp(-r * r * 4) * 0.25, 0, 1)
    elif e == 'void':
        ph = 3 * (th - 2.0 * np.log(r + 0.1)) + rs.uniform(0, 6)
        arms = (0.5 + 0.5 * np.cos(ph)) ** 3 * smoothstep(1.05, 0.15, r)
        D = Draw(n, n, 2, norm=False)
        for k in range(26):
            D.circle(rs.uniform(10, 246), rs.uniform(10, 246), rs.uniform(0.8, 1.9))
        st = np.asarray(Image.fromarray(np.ascontiguousarray(D.mask()), 'F').resize((n, n), Image.LANCZOS))
        p = np.clip(arms * 0.8 + st * 1.2, 0, 1)
    elif e == 'shadow':
        base = fbm(n, n, 3, 5, seed)
        wx, wy = fbm(n, n, 2, 3, seed + 1) * 40, fbm(n, n, 2, 3, seed + 2) * 40
        yy, xx = np.mgrid[0:n, 0:n].astype(F32)
        w = ndi.map_coordinates(base, [np.clip(yy + wy, 0, n - 1), np.clip(xx + wx, 0, n - 1)], order=1)
        p = np.clip(w * 0.5 + 0.5, 0, 1) ** 1.8
    elif e == 'holy':
        rays = np.clip(np.cos(14 * th + rs.uniform(0, 6)), 0, 1) ** 6 * smoothstep(1.1, 0.05, r)
        p = np.clip(rays * 0.8 + np.exp(-r * r * 5) * 0.65, 0, 1)
    elif e == 'blood':
        cx, cy = rs.uniform(-0.4, 0.4, 2)
        rr = np.hypot(x - cx, y - cy)
        rip = (0.5 + 0.5 * np.cos(rr * 24)) ** 5 * smoothstep(1.3, 0.1, rr)
        D = Draw(n, n, 2, norm=False)
        for k in range(14):
            D.circle(rs.uniform(10, 246), rs.uniform(150, 250), rs.uniform(1.5, 4.5))
        dr = np.asarray(Image.fromarray(np.ascontiguousarray(D.mask()), 'F').resize((n, n), Image.LANCZOS))
        p = np.clip(rip * 0.75 + dr, 0, 1)
    elif e == 'wind':
        ph = 8 * (th + 1.7 * r) + rs.uniform(0, 6)
        p = np.clip(np.cos(ph), 0, 1) ** 8 * smoothstep(1.1, 0.1, r) * (0.5 + 0.5 * (fbm(n, n, 3, 3, seed) * 0.5 + 0.5)) * 1.6
    elif e == 'earth':
        f1, f2 = worley(n, n, 5, seed)
        fb = fbm(n, n, 4, 4, seed + 3)
        p = np.clip((f2 - f1) * 3.2, 0, 1) * 0.55 + (1 - np.clip(f1 * 1.4, 0, 1)) * 0.3 + fb * 0.15 + 0.1
    elif e == 'arcane':
        p = np.zeros_like(r)
        for r0, ww in ((0.35, 0.012), (0.58, 0.018), (0.8, 0.012)):
            p += np.exp(-((r - r0) / ww) ** 2)
        p += (np.cos(th * 24) > 0.85) * np.exp(-((r - 0.7) / 0.07) ** 2) * 0.8
        D = Draw(n, n, 2, norm=False)
        for k in range(18):
            D.circle(rs.uniform(20, 236), rs.uniform(20, 236), rs.uniform(0.9, 1.8))
        st = np.asarray(Image.fromarray(np.ascontiguousarray(D.mask()), 'F').resize((n, n), Image.LANCZOS))
        p = np.clip(p * 0.7 + st, 0, 1)
    elif e == 'nature':
        ridge = 1 - np.abs(fbm(n, n, 4, 3, seed) * 2.4)
        p = np.clip(smoothstep(0.78, 0.95, ridge) * 0.9 + 0.1 * (fbm(n, n, 6, 3, seed + 4) * 0.5 + 0.5), 0, 1)
    else:  # physical
        s = perlin(n, n, 2, seed, fy=70) * 0.5 + 0.5
        sheen = np.exp(-((x + y * 0.7 - 0.25) / 0.22) ** 2) * 0.8
        p = np.clip(s * 0.55 + sheen, 0, 1)
    p = np.clip(p, 0, 1).astype(F32)
    return np.asarray(Image.fromarray(p, 'F').resize((N, N), Image.BICUBIC))


def overlay(kind):
    if kind == 1:   # points hex
        s = 28.0
        px, py = X * s, Y * s
        q = (np.sin(px * 1.0) * np.sin(py * 1.0))
        return (np.cos(px * 2.2) * np.cos(py * 2.2) > 0.82).astype(F32)
    if kind == 2:
        return (np.sin((X + Y) * 34) > 0.93).astype(F32)
    if kind == 3:
        return (np.cos(R * 40) > 0.94).astype(F32)
    return np.zeros_like(R)


def metal(e, ult, basic):
    b = ELEM[e]
    if ult:
        return MAT['gold']
    if basic:
        return (hexc('#a7b0c4'), hexc('#2c3346'))
    return (mix(hexc('#e6eaf4'), b, 0.16), mix(hexc('#3c445a'), darken(b, 0.7), 0.3))


def frame_layer(e, ult, basic, rs):
    if ult:
        ri, ro = 0.76, 0.94
    elif basic:
        ri, ro = 0.91, 0.975
    else:
        ri, ro = 0.82, 0.965
    P = Parts(S, S, SS)
    hi, lo = metal(e, ult, basic)
    D = P.L('ring', (hi, lo), outline=0.022, bevel=0.05 if not basic else 0.03, spec=0.5)
    D.circle(0, 0, ro)
    D.circle(0, 0, ri, 0)
    b = ELEM[e]
    L = P.L('lis', (lighten(b, 0.55), b * 0.75), outline=0.0, bevel=0.012, spec=0.25)
    L.ring(0, 0, ri + 0.012, 0.03)
    if ult:
        F = P.L('fins', MAT['gold'], outline=0.026, bevel=0.03, spec=0.6)
        for k in range(8):
            with F.at(0, 0, 22.5 + 45 * k):
                F.poly([(ro - 0.05, -0.075), (ro + 0.045, 0), (ro - 0.05, 0.075)])
        G = P.L('gems', (lighten(b, 0.6), darken(b, 0.5)), outline=0.022, bevel=0.03, spec=0.9)
        for a in (0, 90, 180, 270):
            with G.at(0, 0, a):
                G.circle(0.86, 0, 0.052)
        st = P.L('star', MAT['gold'], outline=0.026, bevel=0.035, spec=0.7)
        st.star(0, -0.86, 5, 0.135, 0.06, -90)
        P.L('dia', MAT['gold'], outline=0.024, bevel=0.03).poly([(0, 0.99), (0.06, 0.9), (0, 0.82), (-0.06, 0.9)])
    elif not basic:
        Sd = P.L('stud', MAT['gold'], outline=0.015, bevel=0.02, spec=0.7)
        for k in range(8):
            a = math.radians(22.5 + 45 * k)
            Sd.circle(0.89 * math.cos(a), 0.89 * math.sin(a), 0.026)
    cv = render_parts(P, bevel=0.05, outline=0.022, spec=0.5)
    ph = rs.uniform(0, 6.28)
    sheen = 0.8 + 0.26 * conic(N, N, N / 2, N / 2, ph, 2) + 0.1 * conic(N, N, N / 2, N / 2, ph * 2, 5)
    cv[..., :3] *= sheen[..., None]
    return cv, ri


def pick_variant(g, e, rs, aid):
    nv = GL.NV[g]
    if g == 'bolt':
        allowed = {'fire': [0, 2], 'ice': [1, 3], 'lightning': [4, 1]}.get(e, [0, 1, 3])
        return allowed[rs.randint(len(allowed))]
    if g == 'summon':
        low = aid.lower()
        if any(k in low for k in ('skeleton', 'summon', 'raise', 'specter', 'knight', 'archer', 'vanguard')):
            return 0
        if any(k in low for k in ('wolf', 'pack', 'boar', 'wild')):
            return 3
        return rs.choice([0, 2, 1]) if nv > 2 else 0
    return rs.randint(nv)


ROT_OK = {'slash': 14, 'thrust': 8, 'bolt': 10, 'dash': 8, 'charge': 8, 'beam': 6, 'leap': 6, 'cone': 6, 'volley': 6, 'blink': 8, 'whirl': 20,
          'burst': 10, 'chain': 8, 'hook': 8, 'meteor': 0, 'curse': 6, 'trap': 12, 'drain': 20, 'skull_blade': 4, 'parry': 4, 'swap': 20}
NOFLIP = {'ankh', 'cross', 'cross_aura', 'cross_pulse', 'horn', 'hourglass', 'eye_slash', 'shield', 'arrow_up', 'summon', 'meteor'}


def render_ability(a):
    aid = a['id']
    e = a['element']
    seed = seed_of(aid)
    rs = np.random.RandomState(seed)
    ult, basic = bool(a.get('ultimate')), bool(a.get('basic'))
    M = elem_mats(e)
    hi, lo = [hexc(c) for c in BG[e]]
    jit = 1 + rs.uniform(-0.07, 0.07, 3).astype(F32)
    hi, lo = np.clip(hi * jit, 0, 1), np.clip(lo * jit, 0, 1)
    cv = blank(N)
    frame, ri = frame_layer(e, ult, basic, rs)
    field = np.clip((ri + 0.01 - R) * N / 2 + 0.5, 0, 1)
    cx, cy = rs.uniform(-0.3, -0.05), rs.uniform(-0.4, -0.1)
    t = np.clip(np.hypot(X - cx, Y - cy) / 1.35, 0, 1) ** 0.85
    col = hi[None, None, :] * (1 - t[..., None]) + lo[None, None, :] * t[..., None]
    put(cv, field, col)
    pat = pattern(e, rs, seed % 100000)
    put(cv, field * pat, lighten(hi, 0.55), 0.42)
    ov = overlay(rs.randint(0, 4))
    if ov.max() > 0:
        put(cv, field * blur(ov, 0.8), lighten(hi, 0.5), 0.18)
    put(cv, field * smoothstep(0.35, ri, R), [0.02, 0.02, 0.06], 0.55)
    gl_ = np.exp(-(((X + 0.12) / 0.7) ** 2 + ((Y + 0.55) / 0.23) ** 2)) * (Y < -0.08)
    put(cv, field * gl_, [1, 1, 1], 0.11)
    # glyphe
    g = a['icon_glyph']
    v = pick_variant(g, e, rs, aid)
    G = Parts(S, S, SS)
    rmax = ROT_OK.get(g, 0)
    rot = rs.uniform(-rmax, rmax) if rmax else 0
    flip = (g not in NOFLIP) and rs.rand() < 0.5
    sc = (ri / 0.82) * 1.16
    GL.GLYPHS[g](SubParts(G, 0, 0.0, sc, rot, flip), M, rs, v, e)
    u = G.union()
    glow(cv, blur(u, 0.075 * N / 2) * field, M['light'][1], 0.85)
    gl = render_parts(G, bevel=0.06, outline=0.028, shadow=0.02, spec=0.4)
    gl *= np.clip((ri - 0.02 - R) * N / 2 + 0.5, 0, 1)[..., None]
    over(cv, gl)
    # etincelles d'accent
    A = Parts(S, S, SS)
    D = A.L('acc', M['core'], outline=0.02, bevel=0.03)
    for k in range(rs.randint(2, 5)):
        ang = rs.uniform(0, 6.28)
        rad = rs.uniform(0.6, 0.74) * ri / 0.82
        r_ = rs.uniform(0.035, 0.075)
        if abs(math.cos(ang)) < 0.3 and math.sin(ang) > 0.55:
            continue
        D.star(rad * math.cos(ang), rad * math.sin(ang), 4, r_ * 1.7, r_ * 0.5, -90)
    ac = render_parts(A, bevel=0.03, outline=0.018, spec=0.3)
    ac *= np.clip((ri - 0.02 - R) * N / 2 + 0.5, 0, 1)[..., None]
    over(cv, ac)
    over(cv, frame)
    # badge de statut
    sts = [s for s in (a.get('status') or []) if s in STT.ST]
    if sts:
        B = Parts(S, S, SS)
        STT.badge_parts(sts[0], B, 0.62, 0.62, 0.27)
        bc = render_parts(B, bevel=0.035, outline=0.02, shadow=0.012, spec=0.4, ls=0.27)
        over(cv, bc)
    return finalize(cv, S, S)


def _job(a):
    save(render_ability(a), f'{OUT}/{a["id"]}.png')
    return a['id']


def run(ids=None, procs=10):
    from multiprocessing import Pool
    import glob
    ab = json.load(open(ROOT + '/data/abilities.json'))
    for f in sorted(glob.glob(ROOT + '/data/dlc/abilities_*.json')):
        ab += json.load(open(f))
    seen, jobs = set(), []
    for a in ab:
        if a['id'] in seen or (ids and a['id'] not in ids):
            continue
        seen.add(a['id'])
        jobs.append(a)
    if procs <= 1 or len(jobs) < 12:
        return [_job(a) for a in jobs]
    with Pool(procs) as p:
        return p.map(_job, jobs, chunksize=4)


if __name__ == '__main__':
    ids = sys.argv[1:] or None
    print(len(run(ids)))
