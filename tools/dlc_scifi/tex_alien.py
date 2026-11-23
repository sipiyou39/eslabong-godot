"""Textures de « Planète Rouge » : poussière martienne craquelée, roche stratifiée, maçonnerie de ruines, tôle de base abandonnée, lunes."""
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from tex_lib import *

NAME = 'alien'


def ground():
    c = Canvas()
    X, Z = c.X, c.Z
    depth = c.depth
    n_big = fbm(X / 7.0, Z / 7.0, 4, 1)
    n_mid = fbm(X * 0.8, Z * 0.8, 5, 2)
    n_fine = fbm(X * 9, Z * 9, 4, 3)
    base = grad(np.clip(n_big * 0.6 + n_mid * 0.5, 0, 1), [(0.0, hexc('#8a4630')), (0.45, hexc('#b4663f')), (0.8, hexc('#cc8650')), (1.0, hexc('#dca072'))])
    # rides de sable (vent) : sinusoïdes déformées
    wob = fbm(X * 0.35, Z * 0.35, 4, 4) * 6.0
    rip = 0.5 + 0.5 * np.sin((X * 0.8 + Z * 1.3 + wob) * 3.2)
    base = base * (0.9 + 0.16 * rip[..., None]) * (0.9 + 0.2 * n_fine[..., None])
    # craquelures (Voronoi) : terre séchée
    f1, f2, cid = cell(X * 0.55 + n_mid * 0.6, Z * 0.55 + n_mid * 0.6, 7)
    e = (f2 - f1) / 0.55
    crack = smooth(0.05, 0.012, e) * smooth(0.35, 0.65, fbm(X * 0.4, Z * 0.4, 4, 9))
    base = base * (1 - 0.55 * crack[..., None]) * (0.9 + 0.2 * cid[..., None])
    plate = smooth(0.0, 0.5, e)
    base = base * (0.85 + 0.2 * plate[..., None])
    hgt = (n_fine * 0.004 + n_mid * 0.03 + rip * 0.01 - crack * 0.03 + plate * 0.03).astype(np.float32)
    img = base
    emis = np.zeros((GH, GW, 3), np.float32)
    # cailloux
    peb = blobs(c, 900, 0.04, 0.16, 5, region=None, strength=1.0)
    img = comp(img, hexc('#5d2a22'), peb * 0.5)
    # dalles de la place centrale (ancienne plateforme d'atterrissage) : pierre claire jointoyée
    R = np.hypot(X, Z)
    ang = np.arctan2(Z, X)
    disc_ = c.circle(0, 0, 6.5)
    ringc = np.floor(R / 1.3)
    nseg = np.maximum(6, (ringc * 5).astype(np.int64))
    seg = np.floor((ang + math.pi) / (2 * math.pi) * nseg)
    jr = np.abs(((R % 1.3) / 1.3) - 0.5) * 1.3
    ja = np.abs(((((ang + math.pi) / (2 * math.pi)) * nseg) % 1.0) - 0.5) * (R * 2 * math.pi / np.maximum(nseg, 1))
    jd = np.minimum(0.65 - jr, 0.5 * (R * 2 * math.pi / np.maximum(nseg, 1)) - ja)
    pid = hash01(ringc.astype(np.int64), seg.astype(np.int64), 3)
    stone = grad(np.clip(pid * 0.7 + n_fine * 0.3, 0, 1), [(0, hexc('#8c6048')), (0.5, hexc('#a07050')), (1, hexc('#b08460'))])
    stone = stone * (0.9 + 0.2 * n_mid[..., None])
    stone = comp(stone, hexc('#6a3a2c'), smooth(0.03, 0.005, np.abs(jd)) * 0.9)
    stone = comp(stone, hexc('#7a3a2a'), smooth(0.55, 0.8, fbm(X * 1.5, Z * 1.5, 5, 21)) * 0.35)
    img = comp(img, stone, disc_ * 0.97)
    # anneau gravé + glyphes lumineux (cristal)
    rune = np.maximum(c.ring(0, 0, 5.8, 0.1), c.ring(0, 0, 3.0, 0.08))
    rune = np.maximum(rune, draw_segs(c, rune_segs(0, 0, 4.4, 24, 0.55, seed=5), 0.05))
    star = [(0.7 * math.cos(a), 0.7 * math.sin(a), 2.8 * math.cos(a), 2.8 * math.sin(a)) for a in [k * math.pi / 3 for k in range(6)]]
    rune = np.maximum(rune, draw_segs(c, star, 0.07))
    rune = np.maximum(rune, c.circle(0, 0, 0.6))
    wornr = 0.45 + 0.55 * smooth(0.25, 0.55, fbm(X * 1.8, Z * 1.8, 5, 31))
    rune = rune * wornr
    img = comp(img, hexc('#5a2a20'), c.ring(0, 0, 5.8, 0.16) * 0.5)
    img = comp(img, hexc('#6af0e0'), rune * 0.85)
    emis += rune[..., None] * hexc('#3ad8c8') * 0.7
    # zones d'équipe : disques gravés orange / teal
    for sgn, col in ((-1, '#ffe6a8'), (1, '#3ad0c0')):
        cx = 19.0 * sgn
        z_ = np.maximum(c.ring(cx, 0, 3.7, 0.2), c.ring(cx, 0, 2.5, 0.1))
        z_ = np.maximum(z_, draw_segs(c, rune_segs(cx, 0, 3.1, 14, 0.4, seed=9 + sgn), 0.04))
        z_ = np.maximum(z_, c.dashed(13.0 * sgn, -12.5, 13.0 * sgn, 12.5, 0.14, 0.9, 0.55))
        z_ = z_ * (0.45 + 0.55 * smooth(0.25, 0.6, fbm(X * 2.2, Z * 2.2, 4, 41 + sgn)))
        img = comp(img, hexc('#4a2018'), c.ring(cx, 0, 3.7, 0.3) * 0.35)
        img = comp(img, hexc(col), z_ * 0.8)
        emis += z_[..., None] * hexc(col) * 0.5
    # pieds d'obstacles : roche sombre
    for (ox, oz, r) in OBST:
        d = np.hypot(X - ox, Z - oz)
        img = comp(img, hexc('#4a2620'), smooth(r + 0.7, r + 0.1, d) * 0.55)
        img = comp(img, hexc('#2a1512'), smooth(r + 0.05, r - 0.1, d))
    # poussière accumulée au pied des murs + AO de contact
    img = comp(img, hexc('#d9946a'), smooth(1.4, 0.0, depth) * 0.25)
    ao = c.contact_ao(wall=0.32, wall_len=0.9, obst=0.4, obst_len=0.6)
    img = img * (0.55 + 0.45 * ao[..., None])
    savej(NAME + '_ground.jpg', img, 88)
    savep(NAME + '_ground_n.png', to_normal(down(hgt, 2), 3.0, MPP * 2))
    savep(NAME + '_ground_e.png', np.clip(down(emis, 2), 0, 1))


def tiles():
    tile_rock('alien_rock', 512, '#34161a', '#6a3a2c', '#a8704c', seed=1501, strata=0.9, crack=0.6)
    png2jpg('alien_rock')
    tile_ashlar('alien_stone', 512, palette=('#9a6a4e', '#8a5a40', '#a67858', '#7e5038'), joint='#3a2018', rows=6, block_w=(1.0, 1.9), seed=1502, wear=0.5, shade=0.14)
    png2jpg('alien_stone')
    tile_metal('alien_metal', 512, base='#b4ac9c', seed=1503, rust=0.6, rust_col='#7a3a1c', scale_m=2.0, plates=2, rivets=True)
    png2jpg('alien_metal')
    tile_metal('alien_iron', 512, base='#5a5048', seed=1504, rust=0.75, rust_col='#8a4220', scale_m=2.0, plates=4, rivets=False)
    png2jpg('alien_iron')
    tile_noise('alien_sand', 512, base='#b86a44', var=0.22, seed=1505, scale=1.2, grain=0.1, tint2='#8a4a30')
    Image.open(os.path.join(TEXDIR, 'alien_sand.png')).convert('RGB').save(os.path.join(TEXDIR, 'alien_sand.jpg'), quality=90)
    os.remove(os.path.join(TEXDIR, 'alien_sand.png'))
    tile_noise('alien_cloth', 512, base='#a8602c', var=0.25, seed=1506, scale=1.4, grain=0.09, tint2='#5a3a28')
    Image.open(os.path.join(TEXDIR, 'alien_cloth.png')).convert('RGB').save(os.path.join(TEXDIR, 'alien_cloth.jpg'), quality=90)
    os.remove(os.path.join(TEXDIR, 'alien_cloth.png'))


def moon():
    W, H = 512, 256
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(H) + 0.5) / H
    U, V = np.meshgrid(u, v)
    X = U * 12.0
    Y = V * 6.0
    base = grad(fbm(X * 0.8, Y * 0.8, 5, 61, (10, 5)), [(0, hexc('#8a7a70')), (0.5, hexc('#b0a090')), (1, hexc('#d0c4b4'))])
    for k, (sc_, sd, amp) in enumerate(((3.0, 62, 0.35), (7.0, 63, 0.3), (15.0, 64, 0.22))):
        f1, f2, cid = cell(X * sc_ / 3.0 * 0.5 + 0.0, Y * sc_ / 3.0 * 0.5, sd, (int(12 * sc_ / 6.0) or 1, int(6 * sc_ / 6.0) or 1))
        rim = smooth(0.18, 0.1, np.abs(f1 - 0.32)) * 0.6
        bowl = smooth(0.3, 0.1, f1)
        base = base * (1 - 0.25 * bowl[..., None] * amp * 2) * (1 + 0.25 * rim[..., None] * amp * 2)
    savej('alien_moon.jpg', base, 90)


if __name__ == '__main__':
    what = sys.argv[1:] or ['ground', 'tiles', 'moon']
    if 'tiles' in what:
        tiles()
    if 'ground' in what:
        ground()
    if 'moon' in what:
        moon()
