"""Aides pour l'équipement : coques qui épousent la tête / le torse humains, tissus, fourrure."""
from bodies_common import *
from heads import HUMAN_ROWS, leaf

HEAD_P = PIVOTS["head"]
TORSO_P = PIVOTS["torso"]
PELVIS_P = PIVOTS["pelvis"]

TORSO_ROWS = [(0.72, 0.17, 0.12, 0.0), (0.80, 0.18, 0.13, 0.0), (0.90, 0.215, 0.155, 0.005), (1.00, 0.26, 0.17, 0.012),
              (1.07, 0.275, 0.172, 0.012), (1.13, 0.245, 0.15, 0.0), (1.17, 0.125, 0.10, -0.005)]


def interp_rows(rows, y):
    ys = [r[0] for r in rows]
    return [float(np.interp(y, ys, [r[i] for r in rows])) for i in range(1, 4)]


def head_surface(y, th, rows=HUMAN_ROWS):
    """point de la surface du crâne humain à l'angle th (0=+x, pi/2=+z=avant) et la hauteur y ; retourne (x,z)."""
    rx, rz, cz = interp_rows(rows, y)
    e = 2.3
    c, s = math.cos(th), math.sin(th)
    return rx * np.sign(c) * abs(c) ** (2 / e), cz + rz * np.sign(s) * abs(s) ** (2 / e), rx, rz


def head_cap(ybot, g_out=0.03, g_in=0.0, n=30, k=9, ytop=1.648, p=1.0, bulge=0.0, rows=HUMAN_ROWS, front=0.032):
    """calotte épousant le crâne humain ; ybot(theta) = hauteur du bord inférieur selon l'angle ;
    solide fermé (couche extérieure g_out, intérieure g_in)."""
    def grid(g):
        V = []
        for i in range(n):
            th = 2 * math.pi * i / n
            yb = ybot(th)
            for j in range(k):
                t = j / (k - 1)
                y = yb + (ytop - yb) * (t ** p)
                if j == k - 1:
                    V.append((0.0, ytop + g, interp_rows(rows, ytop - 0.002)[2]))
                    continue
                x, z, rx, rz = head_surface(y, th, rows)
                nx, nz = x / max(rx, 1e-3), (z - interp_rows(rows, y)[2]) / max(rz, 1e-3)
                nl = math.hypot(nx, nz) + 1e-9
                gg = g + bulge * math.sin(math.pi * t)
                if g > 0:
                    gg += front * max(0.0, math.sin(th)) ** 2 * max(0.0, 1.0 - (y - 1.46) / 0.1) * (1.0 if y > 1.3 else 0.0) * min(1.0, (y - 1.30) / 0.1)
                V.append((x + gg * nx / nl, y + g * 0.25 * t, z + gg * nz / nl))
        return np.array(V)
    Vo, Vi = grid(g_out), grid(g_in)
    V = np.vstack([Vo, Vi])
    off = len(Vo)
    F = []
    for i in range(n):
        i2 = (i + 1) % n
        for j in range(k - 2):
            F.append((i * k + j, i2 * k + j, i2 * k + j + 1, i * k + j + 1))
        F.append((i * k + k - 2, i2 * k + k - 2, i2 * k + k - 1))
    # bord inférieur : relie couche ext et int
    for i in range(n):
        i2 = (i + 1) % n
        F.append((i * k, off + i * k, off + i2 * k, i2 * k))
    return Geo(V, F).fix()


def torso_shell(y0=0.74, y1=1.17, gx=0.02, gz=0.02, n=24, k=10, e=2.3, sx=1.0, sz=1.0, cz_shift=0.0, cap=True, extra=None, chest=0.03):
    ys = np.linspace(y0, y1, k)
    rows = []
    for y in ys:
        rx, rz, cz = interp_rows(TORSO_ROWS, y)
        b = chest * math.exp(-0.5 * ((y - 1.04) / 0.09) ** 2)      # bombement des pectoraux
        rows.append((y, rx * sx + gx, rz * sz + gz + b * 0.5, cz + cz_shift + b * 0.5))
    return rows_loft(rows, n=n, e=e, cap0='ngon' if cap else None, cap1='ngon' if cap else None)


def torso_r(y):
    return interp_rows(TORSO_ROWS, y)


def skirt(y_top, y_bot, top_r, bot_r, n=24, k=7, folds=0, fold_amp=0.0, hem_fn=None, e=2.3, cz=0.0, front_open=0.0, cx=0.0, curve=1.0, e_bot=None):
    """jupe / basque : anneaux de y_top (rayons top_r=(rx,rz)) à y_bot (bot_r) ; plis sinusoïdaux ; hem_fn(theta)->décalage vertical du bas."""
    rings = []
    for j in range(k):
        t = j / (k - 1)
        tt = t ** curve
        y0 = y_top + (y_bot - y_top) * t
        rx = top_r[0] + (bot_r[0] - top_r[0]) * tt
        rz = top_r[1] + (bot_r[1] - top_r[1]) * tt
        ee = e if e_bot is None else e + (e_bot - e) * t
        pts = sec(y0, rx, rz, cx, cz, n, ee)
        th = 2 * np.pi * np.arange(n) / n
        if folds:
            amp = fold_amp * t ** 1.2
            pts[:, 0] += np.cos(th) * amp * np.cos(th * folds)
            pts[:, 2] += np.sin(th) * amp * np.cos(th * folds)
        if hem_fn is not None and j >= k - 2:
            w = 1.0 if j == k - 1 else 0.35
            pts[:, 1] += np.array([hem_fn(a) for a in th]) * w
        rings.append(pts)
    return loft(rings, 'ngon', 'ngon')


def jag_hem(amp=0.05, teeth=14, seed=3):
    rng = np.random.RandomState(seed)
    ph = rng.rand(64) * 6.28
    def f(a):
        return -amp * (0.5 + 0.5 * abs(math.sin(a * teeth * 0.5 + ph[int(a * 10) % 64] * 0.3)))
    return f


def tufts(centers, direction, length=0.09, r=0.03, n=6, spread=0.0, seed=1, jitter=0.35):
    """touffes de poils (pointes coniques) ; centers liste de points, direction vecteur moyen."""
    rng = np.random.RandomState(seed)
    out = []
    d0 = np.asarray(direction, float)
    d0 = d0 / np.linalg.norm(d0)
    for c in centers:
        c = np.asarray(c, float)
        d = d0 + rng.randn(3) * jitter
        d /= np.linalg.norm(d)
        L = length * (0.7 + 0.6 * rng.rand())
        out.append(spike(c, c + d * L, r=r * (0.8 + 0.4 * rng.rand()), n=n, bulge=0.75))
    return out


def ring_pts(cx, y, cz, rx, rz, n, e=2.3):
    return sec(y, rx, rz, cx, cz, n, e)


def torso_pt(y, ang_deg, off=0.0, e=2.3, gx=0.05, gz=0.036, chest=0.03):
    """point au-dessus de la coque de torse (tsh) : `off` ~ ancienne convention (marge 0.03 déjà incluse dans la coque)."""
    rx, rz, cz = interp_rows(TORSO_ROWS, y)
    b = chest * math.exp(-0.5 * ((y - 1.04) / 0.09) ** 2)
    rx, rz, cz = rx + gx, rz + gz + b * 0.5, cz + b * 0.5
    th = math.radians(ang_deg)
    c, s = math.cos(th), math.sin(th)
    x = rx * np.sign(c) * abs(c) ** (2 / e)
    z = cz + rz * np.sign(s) * abs(s) ** (2 / e)
    n_ = np.array([x / rx, 0, (z - cz) / rz])
    n_ = n_ / (np.linalg.norm(n_) + 1e-9)
    return np.array([x, y, z]) + n_ * max(off - 0.03, 0.006)


def strap(pts, w=0.03, th=0.012, n=6):
    """sangle/bande suivant des points ; section aplatie."""
    path = curve(pts, 3) if len(pts) > 2 else np.array(pts, float)
    return tube(path, [(w, th)] * len(path), n=n, e=3.0, cap0='ngon', cap1='ngon')


def cloth_sheet(fn, nu=9, nv=8, thick=0.012, nz=(0, 0, -1)):
    """nappe de tissu épaissie : fn(u∈[-1,1], v∈[0,1]) -> point ; épaisseur le long de nz."""
    P = np.array([[fn(-1 + 2 * i / (nu - 1), j / (nv - 1)) for i in range(nu)] for j in range(nv)], float)
    nzv = np.asarray(nz, float)
    Pi = P + nzv * thick
    V = np.vstack([P.reshape(-1, 3), Pi.reshape(-1, 3)])
    off = nu * nv
    idx = lambda j, i: j * nu + i
    F = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            F.append((idx(j, i), idx(j, i + 1), idx(j + 1, i + 1), idx(j + 1, i)))
            F.append((off + idx(j, i), off + idx(j + 1, i), off + idx(j + 1, i + 1), off + idx(j, i + 1)))
    for j in range(nv - 1):
        F.append((idx(j, 0), idx(j + 1, 0), off + idx(j + 1, 0), off + idx(j, 0)))
        F.append((idx(j, nu - 1), off + idx(j, nu - 1), off + idx(j + 1, nu - 1), idx(j + 1, nu - 1)))
    for i in range(nu - 1):
        F.append((idx(0, i), off + idx(0, i), off + idx(0, i + 1), idx(0, i + 1)))
        F.append((idx(nv - 1, i), idx(nv - 1, i + 1), off + idx(nv - 1, i + 1), off + idx(nv - 1, i)))
    return Geo(V, F).fix()


def ring_band(y0, y1, rx, rz, cz=0.0, cx=0.0, n=28, e=2.3, flare=0.0):
    return rows_loft([(y0, rx + flare, rz + flare, cz, cx), (y1, rx, rz, cz, cx)], n=n, e=e, cap0='ngon', cap1='ngon')


def ang_pt(cx, cy, cz, rx, rz, ang_deg, e=2.3):
    th = math.radians(ang_deg)
    c, s = math.cos(th), math.sin(th)
    return np.array([cx + rx * np.sign(c) * abs(c) ** (2 / e), cy, cz + rz * np.sign(s) * abs(s) ** (2 / e)])
