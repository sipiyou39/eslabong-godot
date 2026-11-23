"""Boite a outils ART2D : dessin vectoriel sur-echantillonne (Pillow) + eclairage/biseau (numpy/scipy).
Convention : tous les calques sont des float32 HxWx4 PREMULTIPLIES. finalize() reduit en LANCZOS."""
import os, math, json, hashlib, contextlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = ROOT + '/assets'
F32 = np.float32


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], F32) / 255.0


def mix(a, b, t):
    return np.asarray(a, F32) * (1 - t) + np.asarray(b, F32) * t


def lighten(c, t):
    return mix(c, [1, 1, 1], t)


NAVY = np.array([0.03, 0.04, 0.09], F32)


def darken(c, t, tone=NAVY):
    return mix(c, tone, t)


def seed_of(s):
    return int(hashlib.md5(str(s).encode()).hexdigest()[:8], 16)


ELEM = {k: hexc(v) for k, v in dict(
    fire='#ff6a2b', ice='#6fd6ff', lightning='#ffe14a', void='#a06bff', shadow='#7a4fa8', holy='#ffe9a0',
    blood='#e0344a', wind='#8affd8', earth='#b08a4a', arcane='#5aa0ff', nature='#6ad05a', physical='#c9ced8').items()}

# materiaux (hi, lo)
MAT = {
    'steel': (hexc('#f4f8ff'), hexc('#7c889e')),
    'iron': (hexc('#c4cad8'), hexc('#4b5368')),
    'gold': (hexc('#fff2b4'), hexc('#b0701a')),
    'bronze': (hexc('#f0c08a'), hexc('#7a4526')),
    'dark': (hexc('#565c7e'), hexc('#161a2e')),
    'wood': (hexc('#c08a56'), hexc('#5a3820')),
    'bone': (hexc('#fbf5e2'), hexc('#a89a7a')),
    'white': (hexc('#ffffff'), hexc('#c9d4ee')),
}

# ---------------------------------------------------------------- compositing

def blank(w, h=None):
    return np.zeros((h or w, w, 4), F32)


def put(dst, mask, color, op=1.0):
    """over (calque premultiplie) : peint `color` (3,) ou (H,W,3) a travers `mask`."""
    a = (mask * op).astype(F32)
    c = np.asarray(color, F32)
    if c.ndim == 1:
        c = c[None, None, :]
    dst[..., :3] = dst[..., :3] * (1 - a)[..., None] + c * a[..., None]
    dst[..., 3] = dst[..., 3] * (1 - a) + a
    return dst


def over(dst, src):
    dst[:] = src + dst * (1 - src[..., 3:4])
    return dst


def glow(dst, mask, color, k=1.0):
    """melange 'screen' (lueur)."""
    a = np.clip(mask * k, 0, 1).astype(F32)
    c = np.asarray(color, F32)
    if c.ndim == 1:
        c = c[None, None, :]
    dst[..., :3] += a[..., None] * c * (1 - dst[..., :3])
    dst[..., 3] += a * (1 - dst[..., 3])
    return dst


def layer_from(mask, color, op=1.0):
    out = np.zeros(mask.shape + (4,), F32)
    return put(out, mask, color, op)


def finalize(img, w, h):
    """calque premultiplie hi-res -> PIL RGBA straight (LANCZOS)."""
    H, W = img.shape[:2]
    if (W, H) != (w, h):
        ch = [np.asarray(Image.fromarray(np.ascontiguousarray(img[..., i]), 'F').resize((w, h), Image.LANCZOS))
              for i in range(4)]
        img = np.stack(ch, -1)
    a = np.clip(img[..., 3], 0, 1)
    rgb = np.minimum(np.clip(img[..., :3], 0, None), a[..., None])
    st = np.where(a[..., None] > 1e-4, rgb / np.maximum(a[..., None], 1e-4), 0)
    out = np.dstack([np.clip(st, 0, 1) * 255, a * 255])
    return Image.fromarray(np.rint(out).astype(np.uint8), 'RGBA')


def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, optimize=True)


# ---------------------------------------------------------------- masks / filtres

def blur(m, s):
    if s <= 0.01:
        return m
    return ndi.gaussian_filter(m, s, mode='constant')


def shift(m, dx, dy):
    return ndi.shift(m, (dy, dx), order=1, mode='constant')


def edt_in(m):
    return ndi.distance_transform_edt(m >= 0.5).astype(F32)


def dilate(m, r):
    d = ndi.distance_transform_edt(m < 0.5)
    return np.maximum(m, np.clip(r + 0.5 - d, 0, 1)).astype(F32)


def erode(m, r):
    d = ndi.distance_transform_edt(m >= 0.5)
    return np.minimum(m, np.clip(d - r + 0.5, 0, 1)).astype(F32)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def vgrad(H, W, hi, lo, y0=0.0, y1=None):
    y1 = H if y1 is None else y1
    t = np.clip((np.arange(H, dtype=F32) - y0) / max(y1 - y0, 1), 0, 1)[:, None, None]
    c = np.asarray(hi, F32) * (1 - t) + np.asarray(lo, F32) * t
    return np.broadcast_to(c, (H, W, 3)).copy()


def radial(H, W, cx, cy, r, c0, c1, power=1.0):
    y, x = np.mgrid[0:H, 0:W].astype(F32)
    t = np.clip(np.hypot(x - cx, y - cy) / r, 0, 1) ** power
    return (np.asarray(c0, F32) * (1 - t[..., None]) + np.asarray(c1, F32) * t[..., None]).astype(F32)


def bbox_rows(a, thr=0.05):
    rows = np.where((a > thr).any(1))[0]
    return (rows[0], rows[-1] + 1) if len(rows) else (0, a.shape[0])


def lit(alpha, dist, hi, lo, bevel, depth=1.0, light=(-0.5, -0.7), lz=0.75, strength=1.0,
        spec=0.3, spec_pow=24, spec_col=(1, 1, 1), grad=None, fmin=0.25, fmax=1.9, rows=None):
    """Eclaire un masque avec un biseau. alpha: couverture 0..1, dist: distance interieure (px). Retourne RGBA premultiplie."""
    H, W = alpha.shape
    h = np.clip(dist / max(bevel, 1e-3), 0, 1)
    h = h * h * (3 - 2 * h)
    h = ndi.gaussian_filter(h, max(bevel * 0.10, 0.6))
    gy, gx = np.gradient(h)
    s = depth * bevel
    nx, ny = -gx * s, -gy * s
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + 1)
    nx, ny, nz = nx * inv, ny * inv, inv
    L = np.array([light[0], light[1], lz], F32)
    L /= np.linalg.norm(L)
    f = 1 + strength * ((nx * L[0] + ny * L[1] + nz * L[2]) / L[2] - 1)
    f = np.clip(f, fmin, fmax)
    Hv = L + np.array([0, 0, 1.0], F32)
    Hv /= np.linalg.norm(Hv)
    sp = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1) ** spec_pow
    sp0 = Hv[2] ** spec_pow
    sp = np.clip((sp - sp0) / (1 - sp0), 0, 1)
    if grad is None:
        y0, y1 = rows if rows else bbox_rows(alpha)
        grad = vgrad(H, W, hi, lo, y0, y1)
    rgb = grad * f[..., None] + spec * sp[..., None] * np.asarray(spec_col, F32)
    out = np.empty((H, W, 4), F32)
    out[..., :3] = np.clip(rgb, 0, 1.6) * alpha[..., None]
    out[..., 3] = alpha
    return out


def lit_mask(mask, hi, lo, bevel, **kw):
    return lit(mask, edt_in(mask), hi, lo, bevel, **kw)


def inner_shadow(dst, mask, dx, dy, bl, color=(0, 0, 0), op=0.5):
    sh = blur(shift(1 - mask, dx, dy), bl) * mask
    return put(dst, sh, color, op)


def drop_shadow(dst, mask, dx, dy, bl, color=(0, 0, 0), op=0.5):
    return put(dst, blur(shift(mask, dx, dy), bl), color, op)


def conic(H, W, cx, cy, phase=0.0, k=2):
    y, x = np.mgrid[0:H, 0:W].astype(F32)
    return np.cos(k * (np.arctan2(y - cy, x - cx) - phase))


# ---------------------------------------------------------------- dessin vectoriel

class Draw:
    """Masque 'L' sur-echantillonne. norm=True : coordonnees -1..1 (y vers le bas), 1 = demi-taille."""

    def __init__(self, w, h=None, ss=4, norm=True):
        self.w, self.h, self.ss = w, h or w, ss
        self.img = Image.new('L', (self.w * ss, self.h * ss), 0)
        self.d = ImageDraw.Draw(self.img)
        if norm:
            s = min(self.w, self.h) / 2 * ss
            self.base = np.array([[s, 0, self.w / 2 * ss], [0, s, self.h / 2 * ss], [0, 0, 1]], float)
        else:
            self.base = np.array([[ss, 0, 0], [0, ss, 0], [0, 0, 1]], float)
        self.stack = [np.eye(3)]

    @property
    def M(self):
        return self.base @ self.stack[-1]

    @property
    def unit(self):
        return math.sqrt(abs(np.linalg.det(self.M[:2, :2])))

    @contextlib.contextmanager
    def at(self, tx=0, ty=0, rot=0, sx=1, sy=None):
        sy = sx if sy is None else sy
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        m = np.array([[c * sx, -s * sy, tx], [s * sx, c * sy, ty], [0, 0, 1]])
        self.stack.append(self.stack[-1] @ m)
        try:
            yield self
        finally:
            self.stack.pop()

    def tf(self, pts):
        p = np.asarray(pts, float).reshape(-1, 2)
        M = self.M
        q = p @ M[:2, :2].T + M[:2, 2]
        return [tuple(r) for r in q]

    def poly(self, pts, v=255):
        self.d.polygon(self.tf(pts), fill=v)
        return self

    def ell(self, cx, cy, rx, ry=None, rot=0, v=255):
        ry = rx if ry is None else ry
        n = int(max(24, min(400, max(rx, ry) * self.unit * 1.3)))
        t = np.linspace(0, 2 * np.pi, n, endpoint=False)
        x, y = rx * np.cos(t), ry * np.sin(t)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        return self.poly(np.stack([cx + x * c - y * s, cy + x * s + y * c], 1), v)

    def circle(self, cx, cy, r, v=255):
        return self.ell(cx, cy, r, r, 0, v)

    def rect(self, x0, y0, x1, y1, v=255):
        return self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], v)

    def rrect(self, x0, y0, x1, y1, r, v=255, n=10):
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        pts = []
        for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for k in range(n + 1):
                a = math.radians(a0 + 90 * k / n)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return self.poly(pts, v)

    def path(self, pts, w, closed=False, v=255, cap=True):
        pts = np.asarray(pts, float)
        if closed:
            pts = np.vstack([pts, pts[:1]])
        h = w / 2
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            d = b - a
            L = np.hypot(*d)
            if L < 1e-9:
                continue
            nx, ny = -d[1] / L * h, d[0] / L * h
            self.poly([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], v)
        rng = range(len(pts)) if cap else range(1, len(pts) - 1)
        if closed:
            rng = range(len(pts) - 1)
        step = 1 if len(pts) < 60 else 2
        for i in list(rng)[::step]:
            self.ell(pts[i][0], pts[i][1], h, h, 0, v)
        return self

    def line(self, x0, y0, x1, y1, w, v=255):
        return self.path([(x0, y0), (x1, y1)], w, v=v)

    @staticmethod
    def arc_pts(cx, cy, rx, ry, a0, a1, n=None):
        n = n or max(8, int(abs(a1 - a0) / 6))
        t = np.radians(np.linspace(a0, a1, n))
        return np.stack([cx + rx * np.cos(t), cy + ry * np.sin(t)], 1)

    def arc(self, cx, cy, r, a0, a1, w, v=255):
        return self.path(self.arc_pts(cx, cy, r, r, a0, a1), w, v=v)

    def ring(self, cx, cy, r, w, v=255):
        return self.path(self.arc_pts(cx, cy, r, r, 0, 360, 96)[:-1], w, closed=True, v=v)

    def taper(self, pts, wfn, v=255):
        pts = np.asarray(pts, float)
        n = len(pts)
        tg = np.gradient(pts, axis=0)
        tg /= np.maximum(np.linalg.norm(tg, axis=1, keepdims=True), 1e-9)
        nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
        w = np.array([wfn(t) for t in np.linspace(0, 1, n)]) / 2
        return self.poly(np.vstack([pts + nr * w[:, None], (pts - nr * w[:, None])[::-1]]), v)

    def star(self, cx, cy, n, ro, ri, rot=-90, v=255):
        pts = []
        for i in range(2 * n):
            r = ro if i % 2 == 0 else ri
            a = math.radians(rot + 180 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return self.poly(pts, v)

    def ngon(self, cx, cy, n, r, rot=-90, v=255):
        return self.poly([(cx + r * math.cos(math.radians(rot + 360 * i / n)),
                           cy + r * math.sin(math.radians(rot + 360 * i / n))) for i in range(n)], v)

    def mask(self):
        return np.asarray(self.img, F32) / 255.0


def bez(pts, n=24):
    # De Casteljau explicite
    pts = np.asarray(pts, float)
    out = []
    for tt in np.linspace(0, 1, n):
        q = pts.copy()
        while len(q) > 1:
            q = q[:-1] * (1 - tt) + q[1:] * tt
        out.append(q[0])
    return np.array(out)


def catmull(pts, n=10, closed=False):
    p = np.asarray(pts, float)
    if closed:
        p = np.vstack([p[-1:], p, p[:2]])
    else:
        p = np.vstack([p[:1], p, p[-1:]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(p[-2])
    return np.array(out)


# ---------------------------------------------------------------- SDF analytiques (px)

def grid(W, H):
    y, x = np.mgrid[0:H, 0:W].astype(F32)
    return x + 0.5, y + 0.5


def sdf_rrect(W, H, x0, y0, x1, y1, r):
    x, y = grid(W, H)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    qx = np.abs(x - cx) - ((x1 - x0) / 2 - r)
    qy = np.abs(y - cy) - ((y1 - y0) / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def sdf_circle(W, H, cx, cy, r):
    x, y = grid(W, H)
    return np.hypot(x - cx, y - cy) - r


def cov(sdf):
    """SDF (px) -> couverture 0..1 antialiasee."""
    return np.clip(0.5 - sdf, 0, 1).astype(F32)


# ---------------------------------------------------------------- bruit

def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def perlin(W, H, f, seed=0, fy=None):
    """Perlin periodique (tileable) avec f cellules en x (fy en y)."""
    fy = fy or f
    rs = np.random.RandomState(seed)
    ang = rs.rand(fy, f) * 2 * np.pi
    gx, gy = np.cos(ang), np.sin(ang)
    x = np.arange(W) / W * f
    y = np.arange(H) / H * fy
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fyy = (x - x0)[None, :], (y - y0)[:, None]
    x0m, x1m = x0 % f, (x0 + 1) % f
    y0m, y1m = y0 % fy, (y0 + 1) % fy

    def dotg(yi, xi, dx, dy):
        return gx[yi][:, xi] * dx + gy[yi][:, xi] * dy
    n00 = dotg(y0m, x0m, fx, fyy)
    n10 = dotg(y0m, x1m, fx - 1, fyy)
    n01 = dotg(y1m, x0m, fx, fyy - 1)
    n11 = dotg(y1m, x1m, fx - 1, fyy - 1)
    u, v = _fade(fx), _fade(fyy)
    return ((n00 * (1 - u) + n10 * u) * (1 - v) + (n01 * (1 - u) + n11 * u) * v).astype(F32) * 1.4


def fbm(W, H, f=4, octaves=5, seed=0, gain=0.5, lac=2):
    out = np.zeros((H, W), F32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        out += amp * perlin(W, H, f * lac ** o, seed + o * 17)
        tot += amp
        amp *= gain
    return out / tot


def worley(W, H, n, seed=0, jitter=1.0):
    """Bruit cellulaire periodique : retourne (F1, F2) en unites de cellule."""
    rs = np.random.RandomState(seed)
    px = 0.5 + (rs.rand(n, n) - 0.5) * jitter
    py = 0.5 + (rs.rand(n, n) - 0.5) * jitter
    x = np.arange(W)[None, :] / W * n
    y = np.arange(H)[:, None] / H * n
    cx, cy = np.floor(x).astype(int), np.floor(y).astype(int)
    f1 = np.full((H, W), 9.0, F32)
    f2 = np.full((H, W), 9.0, F32)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ix, iy = (cx + dx) % n, (cy + dy) % n
            qx = cx + dx + px[iy, ix]
            qy = cy + dy + py[iy, ix]
            d = np.hypot(x - qx, y - qy).astype(F32)
            f2 = np.minimum(f2, np.maximum(f1, d))
            f1 = np.minimum(f1, d)
    return f1, f2


def norm01(a):
    a = np.asarray(a, F32)
    lo, hi = a.min(), a.max()
    return (a - lo) / max(hi - lo, 1e-9)


# ---------------------------------------------------------------- sauvegarde / planches

def to_pil_gray_alpha(g, a, w=None, h=None):
    """g: gris 0..1 (H,W) ou RGB (H,W,3), a: alpha 0..1 -> RGBA straight, RGB defini partout (pas de frange noire)."""
    g = np.asarray(g, F32)
    if g.ndim == 2:
        g = np.dstack([g, g, g])
    out = np.dstack([np.clip(g, 0, 1) * 255, np.clip(a, 0, 1) * 255])
    return Image.fromarray(np.rint(out).astype(np.uint8), 'RGBA')


def contact(paths_or_imgs, cols, cell, out_path, bg=(40, 44, 56), pad=6, label=None):
    ims = []
    for p in paths_or_imgs:
        im = Image.open(p).convert('RGBA') if isinstance(p, str) else p.convert('RGBA')
        ims.append(im)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * (cell + pad) + pad, rows * (cell + pad) + pad), bg + (255,))
    for i, im in enumerate(ims):
        sc = min(cell / im.width, cell / im.height)
        if sc != 1:
            im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
        x = pad + (i % cols) * (cell + pad) + (cell - im.width) // 2
        y = pad + (i // cols) * (cell + pad) + (cell - im.height) // 2
        sheet.alpha_composite(im, (x, y))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.convert('RGB').save(out_path)
    return out_path
