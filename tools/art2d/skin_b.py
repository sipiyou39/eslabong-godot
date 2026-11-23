"""Skin UI partie B : ornements, logo, plaques, fonds."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from shapes import *
import skin_a
from skin_a import reg, slab, C, SS, OUT


def divider_gold():
    W, H = 512, 8
    NW, NH = W * SS, H * SS
    x, y = grid(NW, NH)
    cy = NH / 2
    img = blank(NW, NH)
    fade = smoothstep(0, 90 * SS, x) * smoothstep(0, 90 * SS, NW - x)
    core = cov(np.abs(y - cy) - 1.1 * SS) * fade
    t = np.clip((y - (cy - 1.1 * SS)) / (2.2 * SS), 0, 1)[..., None]
    col = mix(MAT['gold'][0], MAT['gold'][1], t)
    put(img, core, col)
    put(img, cov(np.abs(y - cy) - 3 * SS) * fade * 0.0, [1, 1, 1])
    glow(img, np.exp(-np.abs(y - cy) / (1.8 * SS)) * fade, C['gold_mid'], 0.25)
    D = Draw(W, H, SS, norm=False)
    D.poly([(256, 0.4), (262.2, 4), (256, 7.6), (249.8, 4)])
    for dx in (-26, 26):
        D.poly([(256 + dx, 2), (256 + dx + 2, 4), (256 + dx, 6), (256 + dx - 2, 4)])
    m = D.mask()
    over(img, lit(m, edt_in(m), MAT['gold'][0], MAT['gold'][1], 2.2 * SS, spec=0.7, rows=(0, NH)))
    return img


def corner_ornament():
    W = H = 64
    D = Draw(W, H, SS, norm=False)
    D.path([(6, 58), (6, 12), (12, 6), (58, 6)], 4.2)
    D.path([(14, 40), (14, 18), (18, 14), (40, 14)], 2.0)
    D.circle(6.5, 6.5, 4.6)
    D.poly([(22, 6), (30, 6), (26, 2)])
    D.poly([(6, 22), (6, 30), (2, 26)])
    # volute
    D.path(catmull([(22, 24), (28, 22), (32, 26), (29, 31), (25, 29)], 8), 1.9)
    m = D.mask()
    img = blank(W * SS)
    drop_shadow(img, m, 0.6 * SS, 1.0 * SS, 1.5 * SS, C['ink'], 0.75)
    put(img, dilate(m, 0.6 * SS), C['ink'])
    over(img, lit(m, edt_in(m), MAT['gold'][0], MAT['gold'][1], 2.2 * SS, spec=0.7, rows=(0, W * SS)))
    G = Draw(W, H, SS, norm=False)
    G.circle(6.5, 6.5, 2.4)
    g = G.mask()
    over(img, lit(g, edt_in(g), MAT['ruby'][0], MAT['ruby'][1], 1.6 * SS, spec=0.9, rows=(0, W * SS)))
    return img


def banner_ribbon():
    W, H = 256, 64
    NW, NH = W * SS, H * SS
    D = Draw(W, H, SS, norm=False)
    # corps central + queues pliees
    D.poly([(30, 10), (W - 30, 10), (W - 30, 46), (30, 46)])
    D.poly([(0, 18), (34, 18), (34, 56), (0, 56), (12, 37)])
    D.poly([(W, 18), (W - 34, 18), (W - 34, 56), (W, 56), (W - 12, 37)])
    m = D.mask()
    img = blank(NW, NH)
    drop_shadow(img, m, 0, 1.5 * SS, 2 * SS, C['ink'], 0.6)
    put(img, dilate(m, 1.6 * SS), C['ink'])
    over(img, lit(m, edt_in(m), hexc('#d8485a'), hexc('#6a0f22'), 3.0 * SS, spec=0.3, depth=0.8, rows=(0, NH)))
    # plis sombres
    F = Draw(W, H, SS, norm=False)
    F.poly([(30, 46), (34, 56), (34, 46)])
    F.poly([(W - 30, 46), (W - 34, 56), (W - 34, 46)])
    f = F.mask()
    put(img, f, hexc('#2a0510'), 0.9)
    x, y = grid(NW, NH)
    # liserés or
    for yy in (16.5, 40):
        put(img, cov(np.abs(y - yy * SS) - 0.9 * SS) * cov(np.abs(x - NW / 2) - (W / 2 - 22) * SS) * m, MAT['gold'][0], 0.9)
    return img


def hexagon_sd(NW, NH, cx, cy, R, rot_pointy=True):
    x, y = grid(NW, NH)
    px, py = np.abs(x - cx), np.abs(y - cy)
    # hexagone pointe en haut : rayon R (sommet)
    k = np.array([-0.8660254, 0.5, 0.57735027])
    qx, qy = py, px  # pointe en haut -> permuter
    qx, qy = np.abs(y - cy), np.abs(x - cx)
    dp = k[0] * qy + k[1] * qx
    qy2 = qy - 2.0 * np.minimum(dp, 0) * k[0]
    qx2 = qx - 2.0 * np.minimum(dp, 0) * k[1]
    qy3 = qy2 - np.clip(qy2, -k[2] * R * 0.866, k[2] * R * 0.866)
    d = np.hypot(qy3, qx2 - R * 0.866) * np.sign(qx2 - R * 0.866)
    return d


def hex_slot():
    W = H = 96
    NW = NH = W * SS
    # polygone hexa pointy-top via Draw
    def hexmask(r):
        D = Draw(W, H, SS, norm=False)
        D.ngon(48, 48, 6, r, -90)
        return D.mask()
    mo, mr, mf = hexmask(46), hexmask(43), hexmask(38)
    img = blank(NW)
    drop_shadow(img, mo, 0, 1.5 * SS, 2 * SS, C['ink'], 0.6)
    put(img, mo, C['ink'])
    over(img, lit(mr, edt_in(mr), hexc('#aebce0'), hexc('#2a3248'), 3.0 * SS, spec=0.5, rows=(0, NW)))
    face = vgrad(NH, NW, hexc('#0a0e18'), hexc('#1a2236'), 0, NH)
    put(img, mf, face)
    inner_shadow(img, mf, 0, 2.5 * SS, 4 * SS, C['ink'], 0.8)
    return img


def slot_square(hover=False):
    W = H = 80
    kw = dict(r=9, outline=2.0, bt=2.6, face=(hexc('#0a0e18'), hexc('#1b2338')), vig=0.0, inner_dark=0.0, pressed=True, rim_strength=0.9)
    if hover:
        kw.update(rim=(MAT['gold'][0], hexc('#8a5a1c')), glow_col=hexc('#ffd36a'), glow_k=0.28)
    else:
        kw.update(rim=(hexc('#98a6c8'), hexc('#2a3248')))
    img = slab(W, H, **kw)
    NW = W * SS
    y = np.arange(NW, dtype=F32)[:, None]
    a = cov(sdf_rrect(NW, NW, 0, 0, NW, NW, 9 * SS) + 4.6 * SS)
    put(img, np.clip(1 - (y - 4.6 * SS) / (9 * SS), 0, 1) ** 2 * a, C['ink'], 0.55)
    return img


def toast_bg():
    W, H = 256, 64
    img = slab(W, H, 8, rim=(hexc('#d6a850'), hexc('#6a4515')), bt=1.4, outline=1.5, face=(hexc('#1c2338'), hexc('#0c101b')), vig=0.2,
               inner_dark=0.35, gloss=0.08, noise=0.03)
    NW, NH = W * SS, H * SS
    x, y = grid(NW, NH)
    bar = cov(sdf_rrect(NW, NH, 8 * SS, 8 * SS, 13 * SS, NH - 8 * SS, 2 * SS))
    put(img, bar, vgrad(NH, NW, MAT['gold'][0], MAT['gold'][1], 8 * SS, NH - 8 * SS))
    return img


def title_plate():
    W, H = 1024, 256
    ss = 2
    NW, NH = W * ss, H * ss
    D = Draw(W, H, ss, norm=False)
    # plaque : corps central + pointes latérales (cartouche)
    body = [(110, 70), (W - 110, 70), (W - 70, 128), (W - 110, 186), (110, 186), (70, 128)]
    D.poly(body)
    D.poly([(56, 128), (118, 98), (118, 158)])
    D.poly([(W - 56, 128), (W - 118, 98), (W - 118, 158)])
    m = D.mask()
    img = blank(NW, NH)
    drop_shadow(img, m, 0, 4 * ss, 6 * ss, C['ink'], 0.7)
    put(img, dilate(m, 4 * ss), C['ink'])
    over(img, lit(m, edt_in(m), hexc('#ffe9a0'), hexc('#7a4a12'), 7 * ss, spec=0.7, rows=(0, NH)))
    inner = erode(m, 8 * ss)
    put(img, inner, C['ink'])
    inner2 = erode(m, 9.5 * ss)
    face = vgrad(NH, NW, hexc('#27304a'), hexc('#0c101b'), 60 * ss, 196 * ss)
    n = fbm(NW, NH, 8, 4, seed=11) * 0.5 + 0.5
    face = face * (1 + (n[..., None] - 0.5) * 0.18)
    put(img, inner2, face)
    # vignette interne + lueur haute
    x, y = grid(NW, NH)
    d = edt_in(inner2)
    put(img, np.exp(-d / (14 * ss)) * inner2, C['ink'], 0.5)
    put(img, np.clip(1 - (y - 70 * ss) / (36 * ss), 0, 1) ** 2 * inner2, [1, 1, 1], 0.07)
    # liseré or interne
    ring = inner2 * (1 - erode(inner2, 1.4 * ss))
    put(img, erode(inner2, 7 * ss) * (1 - erode(inner2, 8.2 * ss)), hexc('#e0ae4a'), 0.7)
    # gemmes
    G = Draw(W, H, ss, norm=False)
    for cx in (92, W - 92):
        G.poly([(cx, 112), (cx + 10, 128), (cx, 144), (cx - 10, 128)])
    g = G.mask()
    over(img, lit(g, edt_in(g), MAT['ruby'][0], MAT['ruby'][1], 4 * ss, spec=0.9, rows=(0, NH)))
    # ornements haut/bas
    for yy in (80, 176):
        ln = cov(np.abs(y - yy * ss) - 0.9 * ss) * smoothstep(150 * ss, 260 * ss, x) * smoothstep(150 * ss, 260 * ss, NW - x)
        put(img, ln * (1 - 0.0) * inner2, hexc('#e0ae4a'), 0.55)
    return img


def logo_emblem():
    N = 512
    ss = 3
    NN = N * ss
    P = Parts(N, N, ss)
    sword(P, -0.80, 0.80, -45, L=1.95, w=0.21, tag='s1', guard_w=0.34)
    sword(P, 0.80, 0.80, -135, L=1.95, w=0.21, tag='s2', guard_w=0.34)
    sp = shield_pts(0.46, -0.36, 0.78)
    P.L('rim', (hexc('#fff0b0'), hexc('#8a5a1c')), bevel=0.055, outline=0.025).poly(sp)
    ip = shield_pts(0.385, -0.29, 0.70)
    T = P.L('top', (hexc('#2c3f7a'), hexc('#0e1736')), outline=0.0, bevel=0.07)
    T.poly(ip)
    T.rect(-1, 0.04, 1, 1, v=0)
    B = P.L('bot', (hexc('#d8405a'), hexc('#5a0a20')), outline=0.0, bevel=0.07)
    B.poly(ip)
    B.rect(-1, -1, 1, 0.04, v=0)
    P.L('fess', 'gold', outline=0.012, bevel=0.03).rect(-0.40, 0.0, 0.40, 0.075)
    S = P.L('star', 'gold', outline=0.012, bevel=0.04)
    S.star(0, -0.14, 5, 0.15, 0.066)
    C_ = P.L('chev', 'gold', outline=0.012, bevel=0.04)
    C_.path([(-0.24, 0.42), (0, 0.24), (0.24, 0.42)], 0.08)
    crown(P, 0, -0.48, 1.1, tag='cr', pts=3)
    cv = blank(NN)
    g = radial(NN, NN, NN / 2, NN * 0.52, NN * 0.50, hexc('#ff9a3a'), hexc('#ff6a2b'), 1.0)
    d = np.clip(1 - np.hypot(*(np.mgrid[0:NN, 0:NN].astype(F32) - NN / 2 * 1.0)) / (NN * 0.5), 0, 1)
    glow(cv, d ** 2.2, hexc('#ff8a3a'), 0.55)
    glow(cv, d ** 5, hexc('#ffe0a0'), 0.35)
    render_parts(P, bevel=0.05, outline=0.02, shadow=0.02, canvas=cv, spec=0.5)
    # reflet diagonal sur l'ecu
    ipm = P.layers['top'][0].mask() + P.layers['bot'][0].mask()
    x, y = grid(NN, NN)
    band = smoothstep(0, 1, 1 - np.abs((x - y * 0.6) - NN * 0.15) / (NN * 0.05))
    put(cv, band * np.clip(ipm, 0, 1), [1, 1, 1], 0.08)
    return cv, N


def menu_bg():
    W, H = 1920, 1080
    y = np.linspace(0, 1, H, dtype=F32)[:, None, None]
    stops = [(0.0, '#05070f'), (0.45, '#0c1226'), (0.8, '#1a1228'), (1.0, '#2a1318')]
    col = np.zeros((H, 1, 3), F32)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        seg = np.clip((y - t0) / (t1 - t0), 0, 1) * ((y >= t0) & (y <= t1))
        col = np.where((y >= t0) & (y <= t1), hexc(c0) * (1 - seg) + hexc(c1) * seg, col)
    img = np.broadcast_to(col, (H, W, 3)).copy()
    xg, yg = np.meshgrid(np.arange(W, dtype=F32), np.arange(H, dtype=F32))
    gl = np.exp(-(((xg - W * 0.5) / (W * 0.45)) ** 2 + ((yg - H * 1.02) / (H * 0.55)) ** 2))
    img += gl[..., None] * hexc('#ff6a2b') * 0.20
    gl2 = np.exp(-(((xg - W * 0.5) / (W * 0.18)) ** 2 + ((yg - H * 1.05) / (H * 0.25)) ** 2))
    img += gl2[..., None] * hexc('#ffb060') * 0.12
    # brume
    mist = fbm(W, H, 3, 5, seed=5) * 0.5 + 0.5
    mist = mist * np.clip((yg / H - 0.35) * 1.6, 0, 1)
    img += mist[..., None] * hexc('#3a2a4a') * 0.16
    # halos bleus en haut
    gl3 = np.exp(-(((xg - W * 0.2) / (W * 0.3)) ** 2 + ((yg - H * 0.1) / (H * 0.35)) ** 2))
    img += gl3[..., None] * hexc('#2a4a9a') * 0.07
    # braises
    rs = np.random.RandomState(7)
    acc = np.zeros((H, W), F32)
    acol = np.zeros((H, W, 3), F32)
    for i in range(520):
        yy = H * (1 - rs.rand() ** 2.2)
        xx = rs.rand() * W
        r = 0.8 + rs.rand() ** 2 * 3.2
        br = (0.35 + rs.rand() * 0.65) * (0.5 + 0.5 * yy / H)
        R = int(r * 5) + 2
        x0, x1, y0, y1 = int(xx) - R, int(xx) + R + 1, int(yy) - R, int(yy) + R + 1
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            continue
        gy, gx = np.mgrid[y0:y1, x0:x1].astype(F32)
        d2 = ((gx - xx) ** 2 + (gy - yy) ** 2) / (r * r)
        s = (np.exp(-d2 * 1.6) + 0.25 * np.exp(-d2 * 0.15)) * br
        acc[y0:y1, x0:x1] += s
        t = np.clip(s, 0, 1)[..., None]
        acol[y0:y1, x0:x1] += t * (hexc('#ff8a3a') * 0.6 + hexc('#ffe0a0') * 0.4 * np.exp(-d2 * 3)[..., None])
    img += acol * 0.9
    for i in range(40):  # bokeh
        xx, yy, r = rs.rand() * W, H * (0.3 + 0.7 * rs.rand()), 14 + rs.rand() * 36
        R = int(r * 1.5)
        x0, x1, y0, y1 = int(xx) - R, int(xx) + R, int(yy) - R, int(yy) + R
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            continue
        gy, gx = np.mgrid[y0:y1, x0:x1].astype(F32)
        d = np.hypot(gx - xx, gy - yy) / r
        s = (np.clip(1 - d, 0, 1) ** 0.5 * 0.5 + (np.abs(d - 0.95) < 0.08) * 0.3) * (d < 1.0)
        img[y0:y1, x0:x1] += s[..., None] * hexc('#ff9a50') * 0.025
    vig = np.clip(1 - (((xg - W / 2) / (W * 0.62)) ** 2 + ((yg - H / 2) / (H * 0.7)) ** 2), 0, 1)
    img *= (0.45 + 0.55 * vig)[..., None]
    img += (np.random.RandomState(3).rand(H, W, 1).astype(F32) - 0.5) * 0.012
    return Image.fromarray(np.rint(np.clip(img, 0, 1) * 255).astype(np.uint8), 'RGB')


def stonewall():
    N = 1024
    rows = 8
    rh = N // rows
    rs = np.random.RandomState(21)
    x, y = np.meshgrid(np.arange(N, dtype=F32), np.arange(N, dtype=F32))
    bid = np.zeros((N, N), np.int32)
    ex = np.zeros((N, N), F32)  # distance horizontale au bord de brique
    ey = np.zeros((N, N), F32)
    tint = np.zeros((N, N), F32)
    k = 0
    for r in range(rows):
        n = 4
        ws = rs.uniform(0.75, 1.25, n)
        ws = ws / ws.sum() * N
        off = rs.randint(0, N)
        edges = np.concatenate([[0], np.cumsum(ws)]) + off
        sl = slice(r * rh, (r + 1) * rh)
        xs = (x[sl] - off) % N
        bounds = np.concatenate([[0], np.cumsum(ws)])
        for b in range(n):
            msk = (xs >= bounds[b]) & (xs < bounds[b + 1])
            dl = xs - bounds[b]
            dr = bounds[b + 1] - xs
            e = np.minimum(dl, dr)
            sub = ex[sl]
            sub[msk] = e[msk]
            ex[sl] = sub
            sb = tint[sl]
            sb[msk] = rs.uniform(-1, 1)
            tint[sl] = sb
            k += 1
        yy = y[sl] - r * rh
        ey[sl] = np.minimum(yy, rh - 1 - yy)
    e = np.minimum(ex, ey)
    mortar = 5.0
    nz = fbm(N, N, 8, 5, seed=2)
    nz2 = fbm(N, N, 32, 3, seed=4)
    e = e + nz * 5 + nz2 * 1.5
    h = smoothstep(mortar, mortar + 14, e)
    h = h * (0.82 + 0.18 * (nz * 0.5 + 0.5)) + nz2 * 0.05
    h = ndi.gaussian_filter(h, 1.2, mode='wrap')
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    nx, ny = -gx * 14, -gy * 14
    inv = 1 / np.sqrt(nx * nx + ny * ny + 1)
    L = np.array([-0.5, -0.6, 0.62])
    L /= np.linalg.norm(L)
    diff = (nx * inv * L[0] + ny * inv * L[1] + inv * L[2]) / L[2]
    base = mix(hexc('#2a2f3e'), hexc('#4a4f60'), (tint[..., None] * 0.5 + 0.5)) * (1 + (nz2[..., None]) * 0.25)
    base = base * (1 + 0.18 * (nz[..., None]))
    col = base * np.clip(diff, 0.3, 1.8)[..., None]
    col = mix(hexc('#06070c'), col, np.clip(h * 1.2, 0.0, 1)[..., None] ** 0.6)
    return Image.fromarray(np.rint(np.clip(col, 0, 1) * 255).astype(np.uint8), 'RGB')


def main():
    reg('divider_gold', finalize(divider_gold(), 512, 8), [64, 0, 64, 0], 'séparateur horizontal doré')
    reg('corner_ornament', finalize(corner_ornament(), 64, 64), [0, 0, 0, 0], 'ornement d\'angle haut-gauche (pivoter pour les autres)')
    reg('banner_ribbon', finalize(banner_ribbon(), 256, 64), [44, 0, 44, 0], 'ruban rouge à queues')
    reg('hex_slot', finalize(hex_slot(), 96, 96), [0, 0, 0, 0], 'emplacement hexagonal (pointe en haut)')
    reg('slot_square', finalize(slot_square(False), 80, 80), [14, 14, 14, 14], 'emplacement carré')
    reg('slot_square_hover', finalize(slot_square(True), 80, 80), [14, 14, 14, 14], 'emplacement carré survolé')
    reg('toast_bg', finalize(toast_bg(), 256, 64), [18, 14, 18, 14], 'notification')
    reg('title_plate', finalize(title_plate(), 1024, 256), [140, 60, 140, 60], 'plaque de titre (zone centrale vide pour le texte)')
    cv, N = logo_emblem()
    reg('logo_emblem', finalize(cv, N, N), [0, 0, 0, 0], 'logo du jeu 512x512')
    save(menu_bg(), OUT + '/../skin/menu_bg_gradient.png')
    save(stonewall(), OUT + '/bg_stonewall.png')
    mp = OUT + '/ui_manifest.json'
    cur = json.load(open(mp))
    cur['menu_bg_gradient.png'] = {'margins': [0, 0, 0, 0], 'size': [1920, 1080], 'note': 'fond de menu (dégradé + braises)'}
    cur['bg_stonewall.png'] = {'margins': [0, 0, 0, 0], 'size': [1024, 1024], 'note': 'mur de pierre tileable'}
    json.dump(dict(sorted(cur.items())), open(mp, 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
