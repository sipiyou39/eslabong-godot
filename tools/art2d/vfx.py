"""Textures VFX : blanc/gris + alpha (RGB defini partout, pas de frange noire)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

OUT = ASSETS + '/textures/vfx'
PI = math.pi


def uv(W, H=None):
    H = H or W
    y, x = np.mgrid[0:H, 0:W].astype(F32)
    return (x + 0.5) / W * 2 - 1, (y + 0.5) / H * 2 - 1


def down(a, w, h=None):
    h = h or w
    if a.shape[1] == w and a.shape[0] == h:
        return a
    return np.clip(np.asarray(Image.fromarray(np.ascontiguousarray(a.astype(F32)), 'F').resize((w, h), Image.LANCZOS)), -1, 2)


def S(name, g, a):
    im = to_pil_gray_alpha(g, a)
    save(im, f'{OUT}/{name}.png')
    return im


def rad_fall(r, p=2.0):
    return np.clip(1 - r, 0, 1) ** p


def soft_glow():
    x, y = uv(256)
    r = np.hypot(x, y)
    a = np.exp(-r * r * 5.0) * smoothstep(1.0, 0.82, r)
    a = np.clip(a * 1.02 + 0.25 * rad_fall(r, 3) , 0, 1) * smoothstep(1.0, 0.8, r)
    return np.ones_like(a), a


def glow_ring():
    x, y = uv(256)
    r = np.hypot(x, y)
    a = np.exp(-((r - 0.68) / 0.085) ** 2) + 0.35 * np.exp(-((r - 0.68) / 0.22) ** 2) + 0.1 * rad_fall(r / 0.68, 2)
    a = np.clip(a, 0, 1) * smoothstep(1.0, 0.86, r)
    return np.ones_like(a), a


def spark_star4():
    x, y = uv(256)
    r = np.hypot(x, y)
    ax, ay = np.abs(x), np.abs(y)
    star = np.clip(1 - (np.sqrt(ax) + np.sqrt(ay)) / 1.0, 0, 1) ** 1.6  # astroide
    spikes = np.exp(-ay * 34) * np.clip(1 - ax, 0, 1) ** 3 + np.exp(-ax * 34) * np.clip(1 - ay, 0, 1) ** 3
    core = np.exp(-r * r * 60)
    halo = np.exp(-r * r * 9) * 0.35
    a = np.clip(star * 0.9 + spikes * 0.8 + core + halo, 0, 1) * smoothstep(1, 0.85, r)
    return np.ones_like(a), a


def spark_cross():
    x, y = uv(256)
    r = np.hypot(x, y)
    a = np.zeros_like(r)
    for ang, L, w in ((0, 1.0, 40), (90, 1.0, 40), (45, 0.55, 55), (135, 0.55, 55)):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        u, v = x * c + y * s, -x * s + y * c
        a += np.exp(-np.abs(v) * w) * np.clip(1 - np.abs(u) / L, 0, 1) ** 2.2
    a += np.exp(-r * r * 40) * 1.2 + np.exp(-r * r * 8) * 0.25
    a = np.clip(a, 0, 1) * smoothstep(1, 0.85, r)
    return np.ones_like(a), a


def flare_streak():
    W, H = 256, 64
    x, y = uv(W, H)
    y = y * (H / W) * 1.0 * 4 / 4  # conserver 64 px de haut
    ay = np.abs(np.mgrid[0:H, 0:W][0].astype(F32) + 0.5 - H / 2) / (H / 2)
    ax = np.abs(x)
    streak = np.exp(-ay * 14) * np.clip(1 - ax, 0, 1) ** 1.6
    core = np.exp(-((ax * 5) ** 2 + (ay * 3.2) ** 2) * 2)
    thin = np.exp(-ay * 40) * np.clip(1 - ax, 0, 1) ** 0.7
    a = np.clip(streak * 0.75 + core + thin * 0.55, 0, 1) * smoothstep(1, 0.9, ax)
    return np.ones_like(a), a


def smoke(seed, N=256, squash=1.0, density=1.0):
    x, y = uv(N)
    y = y / squash
    r = np.hypot(x, y)
    wx = fbm(N, N, 3, 3, seed + 5) * 0.28
    wy = fbm(N, N, 3, 3, seed + 9) * 0.28
    n = fbm(N, N, 4, 5, seed, gain=0.55)
    n2 = fbm(N, N, 8, 3, seed + 31)
    rr = np.hypot(x + wx, y + wy)
    blob = 1 - rr / 0.82
    h = blob + n * 0.55 + n2 * 0.18
    a = smoothstep(0.02, 0.55, h) * density
    a = np.clip(a, 0, 1) * smoothstep(1.0, 0.78, r)
    gy, gx = np.gradient(ndi.gaussian_filter(h, 3.0))
    shade = np.clip(0.62 - gy * 18 * 0.9 + gx * 6, 0.25, 1.0)
    g = np.clip(shade * (0.9 + 0.1 * n2) + 0.1, 0.2, 1)
    return g, np.clip(a * (0.55 + 0.45 * smoothstep(0, 0.6, h)), 0, 1)


def flame_field(N, seed, scroll=0):
    return None


def tongue(D, base, height, wmax, lean, sway, phase, n=48):
    t = np.linspace(0, 1, n)
    x = base[0] + lean * t ** 1.6 + sway * np.sin(2 * PI * 0.8 * t + phase) * t
    y = base[1] - height * t
    pts = np.stack([x, y], 1)
    def wfn(u):
        if u < 0.22:
            return wmax * math.sqrt(max(0.0, 1 - ((u - 0.22) / 0.22) ** 2)) * 1.0 + 0.001
        return wmax * max(0.0, 1 - (u - 0.22) / 0.78) ** 1.2 + 0.001
    D.taper(pts, wfn)


def flame(N, seed, sway=0.3, lean=0.0, noise_amp=0.16, phase=0.0, scroll=0, width=0.5, nfield=None, tphase=0.0):
    ss = 3
    G = np.zeros((N * ss, N * ss), F32)
    layers = []
    # (base_x, height, width, lean, sway, grey)
    rs = np.random.RandomState(seed)
    sw, ln0 = sway * 0.32, lean * 0.55
    specs = [(0.0, 1.72, width * 0.9, ln0, sw, 0.50),
             (-width * 0.5, 1.05, width * 0.46, ln0 * 0.5 - 0.07, -sw * 0.8, 0.50),
             (width * 0.5, 0.9, width * 0.42, ln0 * 0.5 + 0.09, sw * 0.7, 0.50),
             (0.0, 1.3, width * 0.6, ln0 * 0.8, sw * 0.9, 0.78),
             (0.0, 0.8, width * 0.34, ln0 * 0.4, sw * 0.5, 1.0)]
    A = np.zeros_like(G)
    for (bx, h, w, ln, sy, gv) in specs:
        D = Draw(N, N, ss)
        tongue(D, (bx, 0.9), h, w, ln, sy, phase + bx * 3)
        m = D.mask()
        G = np.where(m > 0.5, gv, G) if gv > 0.6 else np.maximum(G, m * gv)
        if gv <= 0.6:
            A = np.maximum(A, m)
        else:
            A = np.maximum(A, m)
    G = blur(G, 5 * ss * 0.5)
    A = blur(A, 1.5 * ss * 0.6)
    g, a = down(G, N), down(A, N)
    nz1 = np.roll(fbm(N, N, 4, 3, seed + 1), -scroll, axis=0)
    nz2 = np.roll(fbm(N, N, 4, 3, seed + 2), -scroll, axis=0)
    yy, xx = np.mgrid[0:N, 0:N].astype(F32)
    vv = np.clip(1 - yy / N, 0, 1)
    amp = N * 0.07 * noise_amp / 0.16
    cdx = nz1 * amp * (0.2 + vv)
    cdy = nz2 * amp * 0.5 * (0.2 + vv)
    coords = [np.clip(yy + cdy, 0, N - 1), np.clip(xx + cdx, 0, N - 1)]
    g = ndi.map_coordinates(g, coords, order=1)
    a = ndi.map_coordinates(a, coords, order=1)
    g = np.clip(0.38 + g * 0.72, 0, 1)
    a = np.clip(a * 1.15, 0, 1) * smoothstep(0.0, 0.03, vv)
    return g.astype(F32), a.astype(F32)


def fire_tongue(i):
    p = [dict(sway=0.5, lean=0.10, noise_amp=0.18, phase=0.3, width=0.52),
         dict(sway=-0.6, lean=-0.16, noise_amp=0.16, phase=1.6, width=0.46),
         dict(sway=0.8, lean=0.26, noise_amp=0.2, phase=2.6, width=0.42),
         dict(sway=-0.3, lean=0.0, noise_amp=0.14, phase=4.0, width=0.58)][i]
    return flame(256, 100 + i * 7, **p)


def flame_sheet():
    N = 256
    G = np.zeros((1024, 1024), F32)
    A = np.zeros((1024, 1024), F32)
    for k in range(16):
        t = k / 16
        g, a = flame(N, 77, sway=0.5 * math.sin(2 * PI * t), lean=0.1 * math.sin(2 * PI * t + 1),
                     noise_amp=0.2, phase=2 * PI * t, scroll=int(N * t), width=0.5)
        r, c = divmod(k, 4)
        G[r * N:(r + 1) * N, c * N:(c + 1) * N] = g
        A[r * N:(r + 1) * N, c * N:(c + 1) * N] = a
    return G, A


def ember():
    x, y = uv(256)
    r = np.hypot(x, y)
    a = np.clip(np.exp(-r * r * 36) * 1.1 + 0.35 * np.exp(-r * r * 7) + 0.1 * np.exp(-r * r * 2.5), 0, 1) * smoothstep(1, 0.8, r)
    g = np.clip(0.75 + 0.25 * np.exp(-r * r * 30), 0, 1)
    return g, a


def ice_shard(i):
    N, ss = 256, 3
    cfgs = [[(0, 0.0, 1.0, 0.2)], [(-9, -0.2, 0.78, 0.15), (13, 0.12, 0.98, 0.18), (40, 0.3, 0.52, 0.12)],
            [(-22, -0.22, 0.55, 0.14), (-4, 0.0, 0.86, 0.16), (11, 0.18, 0.66, 0.13), (26, 0.36, 0.42, 0.1), (-36, -0.4, 0.38, 0.1)]][i]
    M = N * ss
    G = np.zeros((M, M), F32)
    A = np.zeros((M, M), F32)
    E = np.zeros((M, M), F32)
    yy = np.mgrid[0:M, 0:M][0].astype(F32) / M
    for (ang, ox, L, w) in sorted(cfgs, key=lambda c: c[2]):
        base_y = 0.92
        ln = 1.62 * L
        shoulder = base_y - ln * 0.78
        tip = (w * 0.12, base_y - ln)
        facets = [([(-w, base_y), (-w, shoulder), (-w * 0.35, shoulder - 0.02), (-w * 0.35, base_y)], 0.92),
                  ([(-w * 0.35, base_y), (-w * 0.35, shoulder - 0.02), (w * 0.4, shoulder), (w * 0.4, base_y)], 1.0),
                  ([(w * 0.4, base_y), (w * 0.4, shoulder), (w, shoulder + 0.02), (w, base_y)], 0.5),
                  ([(-w, shoulder), (-w * 0.35, shoulder - 0.02), tip], 0.98),
                  ([(-w * 0.35, shoulder - 0.02), (w * 0.4, shoulder), tip], 0.74),
                  ([(w * 0.4, shoulder), (w, shoulder + 0.02), tip], 0.42)]
        full = Draw(N, N, ss)
        with full.at(ox, 0, ang):
            full.poly([(-w, base_y), (-w, shoulder), tip, (w, shoulder + 0.02), (w, base_y)])
        fm = full.mask()
        Gc = np.zeros_like(G)
        for pts, val in facets:
            D = Draw(N, N, ss)
            with D.at(ox, 0, ang):
                D.poly(pts)
            Gc = np.where(D.mask() > 0.5, val * (0.82 + 0.3 * (1 - np.clip((yy - 0.1) / 0.8, 0, 1))), Gc)
        Ed = Draw(N, N, ss)
        with Ed.at(ox, 0, ang):
            for pts, val in facets:
                Ed.path(pts, 0.012, closed=True)
        Ec = Ed.mask() * fm
        sel = fm > 0.5
        G = np.where(sel, Gc, G)
        E = np.where(sel, Ec, E)
        A = np.maximum(A, fm)
    G = np.clip(np.maximum(G, E), 0, 1)
    d = edt_in(A)
    inner = np.clip(0.85 + 0.15 * np.clip(d / (10 * ss), 0, 1), 0, 1)
    return down(G, N), down(np.clip(A * inner + E * 0.2, 0, 1), N)


def snow_flake():
    N, ss = 256, 4
    D = Draw(N, N, ss)
    for k in range(6):
        with D.at(0, 0, k * 60 - 90):
            D.path([(0, 0), (0.82, 0)], 0.055)
            for t, L in ((0.28, 0.2), (0.5, 0.3), (0.68, 0.16)):
                for sgn in (-1, 1):
                    D.path([(t, 0), (t + L * 0.75, sgn * L * 0.8)], 0.04)
            D.poly([(0.8, 0), (0.9, 0.05), (1.0, 0), (0.9, -0.05)])
    D.ngon(0, 0, 6, 0.16, 0)
    m = down(D.mask(), N)
    glowm = blur(m, 4)
    a = np.clip(m + glowm * 0.45, 0, 1)
    return np.ones_like(a), a


def bolt_pts(p0, p1, rs, disp, depth):
    pts = [np.array(p0, float), np.array(p1, float)]
    for _ in range(depth):
        new = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            mid = (a + b) / 2
            d = b - a
            nrm = np.array([-d[1], d[0]]) / max(np.hypot(*d), 1e-9)
            mid = mid + nrm * rs.uniform(-1, 1) * disp * np.hypot(*d)
            new += [mid, b]
        pts = new
        disp *= 0.62
    return np.array(pts)


def render_bolt(W, H, pts_list, widths, ss=4):
    D = Draw(W, H, ss, norm=False)
    for pts, w in zip(pts_list, widths):
        D.path(pts, w)
    m = down(D.mask(), W, H)
    a = m + blur(m, 3.0) * 1.0 + blur(m, 9) * 0.6
    return np.clip(a, 0, 1), m


def lightning_bolt(i):
    W, H = 512, 64
    rs = np.random.RandomState(300 + i)
    main = bolt_pts((14, 32), (W - 14, 32 + rs.uniform(-5, 5)), rs, [0.1, 0.13, 0.16, 0.12][i], 7)
    main[:, 1] = np.clip(main[:, 1], 11, H - 11)
    pl, ws = [main], [7.0]
    for _ in range([2, 3, 1, 4][i]):
        k = rs.randint(len(main) // 5, len(main) * 4 // 5)
        s = main[k]
        dirn = np.array([1.0, rs.choice([-1, 1]) * rs.uniform(0.3, 0.8)])
        e = s + dirn / np.hypot(*dirn) * rs.uniform(50, 110)
        e[1] = np.clip(e[1], 10, H - 10)
        br = bolt_pts(s, e, rs, 0.2, 5)
        br[:, 1] = np.clip(br[:, 1], 10, H - 10)
        pl.append(br)
        ws.append(4.0)
    a, m = render_bolt(W, H, pl, ws)
    x = np.linspace(0, 1, W)[None, :]
    a = a * smoothstep(0, 0.06, x) * smoothstep(1, 0.94, x)
    return np.ones_like(a), a


def lightning_arc():
    N = 256
    rs = np.random.RandomState(911)
    t = np.linspace(-0.85, 0.85, 40)
    base = np.stack([128 + 104 * np.sin(t), 70 + 120 * (1 - np.cos(t))], 1)
    pts = base + rs.normal(0, 3.5, base.shape)
    pl = [pts]
    ws = [7.0]
    for k in (10, 22, 31):
        s = pts[k]
        e = s + np.array([rs.uniform(-26, 26), rs.uniform(18, 34)])
        br = bolt_pts(s, e, rs, 0.3, 4)
        pl.append(br)
        ws.append(4.0)
    a, m = render_bolt(N, N, pl, ws)
    return np.ones_like(a), a


def crescent_mask(N, R1, R2, dx, rot=0, cy=0.0):
    x, y = uv(N)
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    xr, yr = x * c + y * s, -x * s + y * c
    d1 = np.hypot(xr, yr - cy) - R1
    d2 = np.hypot(xr - dx, yr - cy) - R2
    return d1, d2


def slash_arc(i):
    N = 256
    x, y = uv(N)
    sh = [(0.0, 0.92, 0.28, 0.84), (0.0, 0.95, 0.12, 0.9), (0.0, 0.92, 0.36, 0.8), (-0.1, 0.93, 0.3, 0.86), (0.0, 0.97, 0.2, 0.9)][i]
    d1 = np.hypot(x - sh[0], y) - sh[1]
    d2 = np.hypot(x - sh[2], y) - sh[3]
    inside = np.maximum(d1, -d2)
    body = smoothstep(0.012, -0.01, inside)
    t = np.clip(d2 / 0.16, 0, 1)
    br = np.exp(-d2 * 16) * 0.7 + 0.35 * (1 - t) ** 2
    a = body * np.clip(0.5 + br, 0, 1)
    if i == 3:
        n = fbm(N, N, 6, 4, 8)
        a *= np.clip(0.78 + n * 0.8, 0, 1) * smoothstep(-0.015, 0.05, -d1 + n * 0.03)
    if i == 4:
        extra = np.exp(-np.abs(np.hypot(x - 0.6, y) - 1.2) * 40) * 0.4 * smoothstep(0.1, 0.9, -x + 0.7)
        a = np.maximum(a, extra * (np.abs(y) < 0.85))
    if i == 2:
        d3 = np.hypot(x - 0.1, y) - 0.97
        d4 = np.hypot(x - 0.46, y) - 0.9
        a = np.maximum(a, smoothstep(0.012, -0.01, np.maximum(d3, -d4)) * 0.55 * (np.exp(-d4 * 8) * 0.8 + 0.2) * smoothstep(-0.3, -0.7, x * 1.0 + 0.0) * 0 + a * 0)
    a = a * smoothstep(1.35, 1.0, np.abs(np.arctan2(y, -x)))
    a = a * smoothstep(1.0, 0.9, np.hypot(x, y))
    return 0.78 + 0.22 * np.clip(br, 0, 1), np.clip(a, 0, 1)


def slash_cross():
    N = 256
    x, y = uv(N)
    a = np.zeros_like(x)
    for ang in (45, -45):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        u, v = x * c + y * s, -x * s + y * c
        L = np.clip(1 - np.abs(u) / 0.95, 0, 1)
        wprof = 0.075 * L ** 0.9
        a = np.maximum(a, smoothstep(wprof + 0.015, wprof * 0.4, np.abs(v)) * (L > 0))
        a = np.maximum(a, np.exp(-np.abs(v) * 22) * L ** 1.5 * 0.45)
    r = np.hypot(x, y)
    a = np.clip(a + np.exp(-r * r * 30) * 0.8, 0, 1)
    return np.ones_like(a), a


def hit_flash_star():
    N = 256
    x, y = uv(N)
    r = np.hypot(x, y)
    th = np.arctan2(y, x)
    rs = np.random.RandomState(5)
    n_sp = 11
    ang = (np.arange(n_sp) + rs.uniform(-0.25, 0.25, n_sp)) * 2 * PI / n_sp
    lens = rs.uniform(0.62, 1.0, n_sp)
    wid = rs.uniform(0.09, 0.16, n_sp)
    prof = np.zeros_like(r)
    for a0, l0, w0 in zip(ang, lens, wid):
        dth = np.abs(((th - a0 + PI) % (2 * PI)) - PI)
        prof = np.maximum(prof, np.clip(1 - dth / (w0 * (1.3 - r / l0 * 0.9)), 0, 1) * np.clip(1 - r / l0, 0, 1) ** 0.7)
    a = np.clip(prof * 1.15 + np.exp(-r * r * 20) * 1.3, 0, 1) * smoothstep(1.0, 0.92, r)
    return np.ones_like(a), a


def shock_ring():
    N = 256
    x, y = uv(N)
    r = np.hypot(x, y)
    n = fbm(N, N, 3, 3, 12) * 0.012
    rr = r + n
    outer = smoothstep(0.94, 0.89, rr)
    inner = smoothstep(0.5, 0.9, rr) ** 2.0
    a = np.clip(outer * inner + np.exp(-((rr - 0.9) / 0.02) ** 2) * 0.6, 0, 1)
    return np.ones_like(a), a


def rune_glyph(D, cx, cy, size, seed, rot=0, w=0.02):
    rs = np.random.RandomState(seed)
    lat = [(c, r) for c in range(3) for r in range(5)]
    def P(c, r):
        return ((c - 1) * 0.5 * size, (r - 2) * 0.5 * size)
    with D.at(cx, cy, rot):
        if rs.rand() < 0.7:
            a, b = rs.randint(0, 2), rs.randint(3, 5)
            D.path([P(1, a), P(1, b)], w)
        n = rs.randint(2, 5)
        for _ in range(n):
            p, q = lat[rs.randint(len(lat))], lat[rs.randint(len(lat))]
            if p == q or abs(p[0] - q[0]) + abs(p[1] - q[1]) > 4:
                continue
            D.path([P(*p), P(*q)], w)
        if rs.rand() < 0.3:
            D.circle(*P(1, 2 + rs.choice([-2, 2])), w * 1.3)


def rune_circle(i):
    N, ss = 512, 3
    D = Draw(N, N, ss)
    w = 0.012
    R = 0.96
    def ring(r, ww=w, a0=0, a1=360, dash=None):
        if dash:
            n, fill = dash
            for k in range(n):
                s = a0 + (a1 - a0) * k / n
                D.arc(0, 0, r, s, s + (a1 - a0) / n * fill, ww)
        else:
            D.arc(0, 0, r, a0, a1, ww) if (a1 - a0) < 360 else D.ring(0, 0, r, ww)
    def ticks(r0, r1, n, ww=w, off=0):
        for k in range(n):
            a = math.radians(off + 360 * k / n)
            D.line(r0 * math.cos(a), r0 * math.sin(a), r1 * math.cos(a), r1 * math.sin(a), ww)
    def runes(r, n, size, seed, ww=0.012):
        for k in range(n):
            a = 360 * k / n
            rr = math.radians(a)
            rune_glyph(D, r * math.cos(rr), r * math.sin(rr), size, seed + k * 13, rot=a + 90, w=ww)
    def pgon(n, r, rot=-90, ww=w):
        pts = [(r * math.cos(math.radians(rot + 360 * k / n)), r * math.sin(math.radians(rot + 360 * k / n))) for k in range(n)]
        D.path(pts, ww, closed=True)
    def star(n, r, skip, rot=-90, ww=w):
        pts = [(r * math.cos(math.radians(rot + 360 * k / n)), r * math.sin(math.radians(rot + 360 * k / n))) for k in range(n)]
        for k in range(n):
            D.line(*pts[k], *pts[(k + skip * (1 + k * 0)) % n], ww) if False else D.line(*pts[k], *pts[(k + skip) % n], ww)
    if i == 0:
        ring(R, 0.02); ring(R - 0.04); ring(0.74, 0.016); ring(0.58)
        ticks(R - 0.04, R - 0.1, 72, 0.008)
        runes(0.665, 14, 0.1, 10)
        star(6, 0.58, 2); ring(0.3, 0.014); ticks(0.3, 0.2, 6, 0.012, 0)
        pgon(6, 0.14)
    elif i == 1:
        ring(R, 0.02); ring(0.9); ring(0.7, 0.018); ring(0.62)
        for k in range(10):
            a = 360 * k / 10
            with D.at(0, 0, a):
                D.poly([(0.9, -0.03), (0.9, 0.03), (0.98, 0)])
        runes(0.8, 20, 0.075, 40, 0.01)
        star(5, 0.62, 2, ww=0.014); star(5, 0.3, 2); ring(0.3, 0.012)
    elif i == 2:
        ring(R, 0.014, dash=(48, 0.7)); ring(0.88, 0.02); ring(0.82)
        runes(0.76, 8, 0.12, 90)
        ring(0.68, 0.016); ring(0.4, 0.012, dash=(24, 0.6))
        pgon(8, 0.52, -90 + 22.5); pgon(8, 0.3, -90)
        for k in range(8):
            a = math.radians(360 * k / 8 - 90 + 22.5)
            D.line(0.52 * math.cos(a), 0.52 * math.sin(a), 0.3 * math.cos(a + 0.4), 0.3 * math.sin(a + 0.4), 0.01)
    elif i == 3:
        ring(0.62, 0.02); ring(0.54)
        for k in range(24):
            a = 360 * k / 24
            L = 0.98 if k % 2 == 0 else 0.84
            with D.at(0, 0, a):
                D.poly([(0.7, -0.018), (L, 0), (0.7, 0.018)])
        runes(0.58, 12, 0.07, 120, 0.009)
        ring(0.4, 0.014); ring(0.36); D.circle(0, 0, 0.05)
        for k in range(8):
            a = math.radians(45 * k)
            D.line(0.36 * math.cos(a), 0.36 * math.sin(a), 0.14 * math.cos(a), 0.14 * math.sin(a), 0.008)
    elif i == 4:
        ring(R, 0.016); ring(0.9, 0.012)
        ticks(0.9, 0.83, 120, 0.006); ticks(0.9, 0.78, 12, 0.014)
        for ang in (0, 45):
            with D.at(0, 0, ang):
                D.rect(-0.55, -0.55, 0.55, 0.55) if False else D.path([(-0.55, -0.55), (0.55, -0.55), (0.55, 0.55), (-0.55, 0.55)], 0.016, closed=True)
        ring(0.6, 0.01); runes(0.72, 16, 0.07, 160, 0.009); ring(0.26, 0.016)
        runes(0.1, 1, 0.12, 170, 0.012)
    else:
        ring(R, 0.02, a0=10, a1=170); ring(R, 0.02, a0=190, a1=350)
        ring(0.86, 0.014, a0=-40, a1=100); ring(0.86, 0.014, a0=140, a1=280)
        ring(0.76, 0.012); runes(0.67, 10, 0.1, 210)
        ring(0.58, 0.016)
        for k in range(3):
            a = math.radians(90 + 120 * k)
            D.ring(0.17 * math.cos(a), 0.17 * math.sin(a), 0.22, 0.012)
        ring(0.46, 0.01, dash=(36, 0.5)); star(3, 0.58, 1, ww=0.012)
    m = down(D.mask(), N)
    a = np.clip(m + blur(m, 2.5) * 0.55 + blur(m, 9) * 0.25, 0, 1)
    return np.ones_like(a), a


def rune_sheet():
    N, ss = 512, 3
    D = Draw(N, N, ss)
    for k in range(16):
        r, c = divmod(k, 4)
        cx, cy = (c + 0.5) / 4 * 2 - 1, (r + 0.5) / 4 * 2 - 1
        rune_glyph(D, cx, cy, 0.34, 500 + k * 7, w=0.018)
        with D.at(cx, cy):
            D.ring(0, 0, 0.19, 0.008)
    m = down(D.mask(), N)
    a = np.clip(m + blur(m, 2.2) * 0.5, 0, 1)
    return np.ones_like(a), a


def magic_swirl():
    N = 256
    x, y = uv(N)
    r = np.hypot(x, y) + 1e-4
    th = np.arctan2(y, x)
    arms = 3
    ph = arms * (th - 2.2 * np.log(r + 0.12))
    a = (0.5 + 0.5 * np.cos(ph)) ** 2.5
    a *= smoothstep(0.98, 0.45, r) * smoothstep(0.0, 0.16, r) ** 0.5
    a += np.exp(-r * r * 40) * 0.9
    a = np.clip(a, 0, 1)
    g = np.clip(0.7 + 0.3 * a, 0, 1)
    return g, a


def heal_plus():
    N, ss = 256, 4
    D = Draw(N, N, ss)
    D.rrect(-0.2, -0.62, 0.2, 0.62, 0.12)
    D.rrect(-0.62, -0.2, 0.62, 0.2, 0.12)
    m = down(D.mask(), N)
    d = edt_in(m)
    h = np.clip(d / 14, 0, 1)
    shade = 0.78 + 0.22 * h
    a = np.clip(m + blur(m, 9) * 0.6, 0, 1)
    return np.clip(shade, 0, 1), a


def leaf():
    N, ss = 256, 4
    D = Draw(N, N, ss)
    top = [(0.0, -0.92), (0.3, -0.6), (0.44, -0.2), (0.32, 0.25), (0.0, 0.62)]
    left = [(-x, y) for x, y in top]
    pts = catmull(top + [(0.0, 0.62)] [:-1] + [(0.0, 0.62)], 12)
    pts_l = catmull([(0.0, 0.62), (-0.32, 0.25), (-0.44, -0.2), (-0.3, -0.6), (0.0, -0.92)], 12)
    outline = np.vstack([pts, pts_l])
    D.poly(outline)
    D.path([(0, 0.62), (0, 0.9)], 0.04)
    m = down(D.mask(), N)
    V = Draw(N, N, ss)
    V.line(0, 0.62, 0, -0.8, 0.035)
    for k in range(6):
        t = 0.5 - k * 0.24
        V.line(0, t, 0.3, t - 0.25, 0.02)
        V.line(0, t, -0.3, t - 0.25, 0.02)
    v = down(V.mask(), N)
    d = edt_in(m)
    x, y = uv(N)
    half = np.where(x > 0, 1.0, 0.82)
    g = (0.6 + 0.4 * np.clip(d / 28, 0, 1)) * half
    g = np.clip(g * (1 + 0.35 * v) + 0.12 * v, 0, 1)
    return g, np.clip(m, 0, 1)


def feather():
    N, ss = 256, 4
    D = Draw(N, N, ss)
    spine = catmull([(-0.12, 0.95), (0.0, 0.4), (0.18, -0.2), (0.12, -0.88)], 20)
    t = np.linspace(0, 1, len(spine))
    tg = np.gradient(spine, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True)
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    prof = np.where(t < 0.1, 0.0, np.sin(np.clip((t - 0.1) / 0.9, 0, 1) ** 0.8 * PI) ** 0.75 * 0.3 + 0.02)
    L = spine + nr * prof[:, None]
    R = spine - nr * (prof * 1.12)[:, None]
    D.poly(np.vstack([L, R[::-1]]))
    m = down(D.mask(), N)
    B = Draw(N, N, ss)
    B.path(spine, 0.03)
    sp = down(B.mask(), N)
    x, y = uv(N)
    n = fbm(N, N, 24, 2, 5) * 0.5 + 0.5
    d = edt_in(m)
    g = np.clip(0.9 - 0.1 * n + 0.1 * np.clip(d / 12, 0, 1) + 0.12 * sp - 0.3 * (np.clip(1 - d / 4, 0, 1)) * 0.3, 0.4, 1)
    rim = np.clip(1 - d / 9, 0, 1)
    return g, np.clip(m * (0.8 + 0.2 * (1 - rim)), 0, 1)


def bat_silhouette():
    N, ss = 256, 4
    D = Draw(N, N, ss)
    for sx in (-1, 1):
        top = bez([(0.08, -0.12), (0.35, -0.7), (0.8, -0.62), (0.98, -0.28)], 16)
        anchors = [(0.98, -0.28), (0.74, 0.14), (0.5, 0.0), (0.3, 0.26), (0.08, 0.1)]
        trail = []
        for a, b in zip(anchors[:-1], anchors[1:]):
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.16)
            trail += list(bez([a, mid, b], 8)[1:])
        D.poly([(sx * p[0], p[1]) for p in list(top) + trail])
        D.poly([(sx * 0.03, -0.36), (sx * 0.1, -0.64), (sx * 0.17, -0.34)])
    D.ell(0, -0.04, 0.15, 0.36)
    D.circle(0, -0.4, 0.14)
    D.poly([(-0.07, 0.15), (0.07, 0.15), (0.03, 0.4), (-0.03, 0.4)])
    D.circle(-0.05, -0.42, 0.025, 0)
    D.circle(0.05, -0.42, 0.025, 0)
    m = down(D.mask(), N)
    d = edt_in(m)
    g = 0.85 + 0.15 * np.clip(d / 10, 0, 1)
    return g, m


def crack_decal():
    N, ss = 256, 3
    D = Draw(N, N, ss)
    rs = np.random.RandomState(31)
    def branch(p, ang, L, w, depth):
        pts = [np.array(p)]
        a = ang
        step = L / 8
        for _ in range(8):
            a += rs.uniform(-0.45, 0.45)
            pts.append(pts[-1] + step * np.array([math.cos(a), math.sin(a)]))
        pts = np.array(pts)
        D.taper(pts, lambda t: w * (1 - t * 0.9))
        if depth > 0:
            for k in (3, 5):
                if rs.rand() < 0.75:
                    branch(pts[k], a + rs.choice([-1, 1]) * rs.uniform(0.5, 1.0), L * 0.5, w * 0.6, depth - 1)
    for k in range(7):
        branch((0, 0), 2 * PI * k / 7 + rs.uniform(-0.3, 0.3), rs.uniform(0.55, 0.9), 0.05, 2)
    D.circle(0, 0, 0.04)
    m = down(D.mask(), N)
    x, y = uv(N)
    fade = smoothstep(1.0, 0.6, np.hypot(x, y))
    a = np.clip(m * fade, 0, 1)
    g = np.clip(0.28 + 0.72 * np.clip(edt_in(m) / 3.0, 0, 1), 0, 1)
    return g, np.clip(a + blur(a, 3) * 0.3, 0, 1)


def scorch_decal():
    N = 256
    x, y = uv(N)
    th = np.arctan2(y, x)
    r = np.hypot(x, y)
    n = fbm(N, N, 5, 5, 61)
    streak = perlin(N, N, 1, 7)  # lent
    ang_n = fbm(N, 1, 6, 2, 3)[0] if False else 0
    wob = 1 + 0.22 * np.sin(th * 5 + 1) * 0.5 + 0.18 * np.sin(th * 11 + 2) * 0.4
    rr = r / (0.72 * wob) + n * 0.28
    a = smoothstep(1.0, 0.35, rr) * smoothstep(1.0, 0.8, r)
    spikes = np.clip(np.sin(th * 17 + n * 6) * 0.5 + 0.5, 0, 1) ** 4 * smoothstep(1.0, 0.5, r) * 0.45 * smoothstep(0.3, 0.7, r)
    a = np.clip(a + spikes * smoothstep(0.95, 0.6, r), 0, 1)
    g = np.clip(0.06 + 0.2 * smoothstep(0.2, 1.0, rr) + 0.06 * n, 0, 0.5)
    return g, np.clip(a * 0.95, 0, 1)


def frost_decal():
    N = 256
    x, y = uv(N)
    r = np.hypot(x, y)
    th = np.arctan2(y, x)
    f1, f2 = worley(N, N, 9, 3)
    edge = np.clip((f2 - f1) * 3.0, 0, 1)
    n = fbm(N, N, 4, 4, 9)
    # branches radiales
    br = np.clip(np.cos(th * 6) * 0.5 + 0.5, 0, 1) ** 8
    base = smoothstep(0.98, 0.15, r + n * 0.25)
    cells = (1 - edge) * 0.55 + 0.45
    a = np.clip(base * (0.25 + 0.75 * (1 - edge * 0.9)) + br * smoothstep(0.95, 0.2, r) * 0.55 * smoothstep(0.0, 0.2, r), 0, 1)
    a *= smoothstep(1.0, 0.82, r)
    g = np.clip(0.8 + 0.2 * (1 - edge) - 0.1 * n, 0.5, 1)
    return g, np.clip(a, 0, 1)


def shadow_blob():
    N = 256
    x, y = uv(N)
    n = fbm(N, N, 4, 3, 77) * 0.12
    r = np.hypot(x * 0.96, y) + n
    a = smoothstep(0.98, 0.15, r) ** 1.4
    return np.zeros_like(a), a


def light_ray():
    N = 256
    x, y = uv(N)
    yy = (y + 1) / 2
    # rayons divergeant du haut
    th = np.arctan2(x, yy + 0.25)
    nz = fbm(N, 1, 10, 3, 17)[0] if False else None
    rs = np.random.RandomState(5)
    a = np.zeros_like(x)
    for k in range(9):
        a0 = rs.uniform(-0.42, 0.42)
        wdt = rs.uniform(0.012, 0.05)
        a += np.exp(-((th - a0) / wdt) ** 2) * rs.uniform(0.4, 1.0)
    a *= np.clip(1 - yy, 0, 1) ** 1.3 * smoothstep(0.0, 0.08, yy)
    a += np.exp(-(x * 3) ** 2) * np.clip(1 - yy, 0, 1) ** 2 * 0.25
    a *= smoothstep(1.0, 0.7, np.abs(x) * 1.15)
    return np.ones_like(a), np.clip(a, 0, 1)


def droplet():
    N, ss = 256, 4
    D = Draw(N, N, ss)
    D.circle(0, 0.28, 0.5)
    D.poly([(-0.46, 0.08), (0, -0.88), (0.46, 0.08)])
    D.poly(catmull([(-0.47, 0.12), (-0.3, -0.25), (0, -0.88), (0.3, -0.25), (0.47, 0.12)], 10))
    m = down(D.mask(), N)
    d = edt_in(m)
    x, y = uv(N)
    h = np.clip(d / 70, 0, 1)
    shade = 0.65 + 0.35 * h
    rim = np.clip(1 - d / 7, 0, 1)
    hl = np.exp(-(((x + 0.2) / 0.1) ** 2 + ((y - 0.15) / 0.2) ** 2))
    g = np.clip(shade + rim * 0.25 + hl * 0.5, 0, 1)
    a = np.clip(m * (0.45 + 0.35 * rim + 0.3 * hl + 0.25 * (1 - h)), 0, 1)
    return g, a


def shield_hex():
    N = 256
    x, y = uv(N)
    s = 7.0
    px, py = x * s, y * s * 1.1547
    # grille hexagonale : distance au bord de cellule
    def hexdist(px, py):
        qx = px * 2 / 3
        qy = (-px / 3 + math.sqrt(3) / 3 * py)
        rx, ry = np.round(qx), np.round(qy)
        rz = np.round(-qx - qy)
        dx, dy, dz = np.abs(rx - qx), np.abs(ry - qy), np.abs(rz - (-qx - qy))
        m = (dx > dy) & (dx > dz)
        rx = np.where(m, -ry - rz, rx)
        m2 = (~m) & (dy > dz)
        ry = np.where(m2, -rx - rz, ry)
        fx, fy = qx - rx, qy - ry
        # coords cartesiennes locales
        lx = fx * 1.5
        ly = (fx * 0.5 + fy) * math.sqrt(3)
        ax, ay = np.abs(lx), np.abs(ly)
        return 1 - np.maximum(ay, ax * 0.5 + ay * 0.866025 * 0 + (ax * 0.5 + ay * 0.5 * 1.7320508 * 0)) , (rx, ry)
    # version simple : hex distance via 3 axes
    k = np.array([0.0, 1.0]), np.array([0.866025, 0.5]), np.array([-0.866025, 0.5])
    hx = hy = None
    # coordonnees axiales
    q = (2 / 3 * px)
    rr = (-1 / 3 * px + math.sqrt(3) / 3 * py)
    cx_ = np.round(q); cz_ = np.round(rr); cy_ = np.round(-q - rr)
    dq, dr_, dy_ = np.abs(cx_ - q), np.abs(cz_ - rr), np.abs(cy_ - (-q - rr))
    fix_q = (dq > dr_) & (dq > dy_)
    cx_ = np.where(fix_q, -cz_ - cy_, cx_)
    fix_r = (~fix_q) & (dr_ > dy_)
    cz_ = np.where(fix_r, -cx_ - cy_, cz_)
    lx = px - 1.5 * cx_
    ly = py - math.sqrt(3) * (cz_ + cx_ / 2)
    ax, ay = np.abs(lx), np.abs(ly)
    hd = np.maximum(ay * 1.0 / 0.866025, ax + ay * 0.57735)  # ~1 au bord
    edge = smoothstep(0.80, 0.93, hd)
    r = np.hypot(x, y)
    fres = smoothstep(0.2, 0.95, r) ** 1.5
    cellrnd = (np.sin(cx_ * 12.9898 + cz_ * 78.233) * 43758.5453) % 1.0
    a = np.clip(edge * 0.95 + (0.06 + 0.1 * cellrnd) * (1 - edge), 0, 1) * (0.35 + 0.65 * fres)
    a = np.clip(a + fres * 0.18, 0, 1) * smoothstep(1.0, 0.93, r)
    return np.ones_like(a), a


def noise_perlin():
    n = fbm(512, 512, 4, 6, 1) * 0.5 + 0.5
    return norm01(n), np.ones((512, 512), F32)


def noise_cell():
    f1, f2 = worley(512, 512, 10, 4)
    v = 1 - np.clip(f1 * 1.15, 0, 1)
    v = 0.7 * v + 0.3 * np.clip((f2 - f1) * 2, 0, 1)
    return norm01(v), np.ones((512, 512), F32)


def gradient_ramp_toon():
    W, H = 256, 4
    x = np.linspace(0, 1, W)
    def band(t, e0, w=0.012):
        return smoothstep(e0 - w, e0 + w, t)
    v = 0.30 + 0.28 * band(x, 0.30) + 0.24 * band(x, 0.58) + 0.18 * band(x, 0.84)
    shadow = hexc('#7a7ca8')
    light = hexc('#fff3e0')
    t = (v - v.min()) / (v.max() - v.min())
    rgb = shadow[None, :] * (1 - t[:, None]) + light[None, :] * t[:, None]
    rgb = rgb * v[:, None] / np.maximum(0.3 + 0.7 * t[:, None], 0.3) * 1.0
    rgb = np.clip(rgb / rgb.max() * 1.0, 0, 1)
    rgb = np.repeat(rgb[None, :, :], H, 0)
    return rgb, np.ones((H, W), F32)


def vignette():
    N = 1024
    x, y = uv(N)
    r = np.hypot(x, y) / 1.41421
    a = smoothstep(0.38, 1.0, r) ** 1.6 * 0.95
    return np.zeros_like(a), a


def film_grain():
    rs = np.random.RandomState(17)
    n = rs.normal(0.5, 0.18, (256, 256)).astype(F32)
    n = ndi.gaussian_filter(n, 0.6, mode='wrap') * 1.6 - 0.3
    return np.clip(n, 0, 1), np.ones((256, 256), F32)


def run():
    jobs = {'soft_glow': soft_glow, 'glow_ring': glow_ring, 'spark_star4': spark_star4, 'spark_cross': spark_cross,
            'flare_streak': flare_streak, 'ember': ember, 'snow_flake': snow_flake, 'lightning_arc': lightning_arc,
            'slash_cross': slash_cross, 'hit_flash_star': hit_flash_star, 'shock_ring': shock_ring, 'rune_glyph_sheet': rune_sheet,
            'magic_swirl': magic_swirl, 'heal_plus': heal_plus, 'leaf': leaf, 'feather': feather, 'bat_silhouette': bat_silhouette,
            'crack_decal': crack_decal, 'scorch_decal': scorch_decal, 'frost_decal': frost_decal, 'shadow_blob': shadow_blob,
            'light_ray': light_ray, 'droplet': droplet, 'shield_hex': shield_hex, 'noise_perlin': noise_perlin, 'noise_cell': noise_cell,
            'gradient_ramp_toon': gradient_ramp_toon, 'vignette': vignette, 'film_grain': film_grain, 'flame_sprite_sheet': flame_sheet}
    for i in range(4):
        jobs[f'smoke_puff_{i}'] = (lambda i=i: smoke(10 + i * 3, squash=[1.0, 0.85, 1.1, 0.9][i]))
        jobs[f'fire_tongue_{i}'] = (lambda i=i: fire_tongue(i))
        jobs[f'lightning_bolt_{i}'] = (lambda i=i: lightning_bolt(i))
    for i in range(3):
        jobs[f'ice_shard_{i}'] = (lambda i=i: ice_shard(i))
    for i in range(5):
        jobs[f'slash_arc_{i}'] = (lambda i=i: slash_arc(i))
    for i in range(6):
        jobs[f'rune_circle_{i}'] = (lambda i=i: rune_circle(i))
    jobs['dust_puff'] = lambda: smoke(77, squash=0.7, density=0.7)
    only = sys.argv[1:]
    for k, f in jobs.items():
        if only and not any(k.startswith(o) for o in only):
            continue
        g, a = f()
        S(k, g, a)
    return list(jobs)


if __name__ == '__main__':
    names = run()
    print(len(names))
