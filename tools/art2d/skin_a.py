"""Skin UI partie A : panneaux, boutons, barres, sliders (9-patch)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

SS = 4
OUT = ASSETS + '/ui/skin'
MAN = {}
C = {k: hexc(v) for k, v in dict(
    ink='#05070d', ink2='#0b0f1a', night='#0e1424', anth='#171c28', anth2='#232a3d', steel_hi='#5a6786', steel_lo='#252d42',
    gold_hi='#ffe9a0', gold_mid='#e0ae4a', gold_lo='#8c5a1c', amber='#f2b84a', parch_hi='#e4d3a6', parch_lo='#bda470').items()}


def reg(name, im, margins, note=''):
    save(im, f'{OUT}/{name}.png')
    MAN[name + '.png'] = {'margins': list(margins), 'size': [im.width, im.height], 'note': note}
    mp = OUT + '/ui_manifest.json'
    cur = json.load(open(mp)) if os.path.exists(mp) else {}
    cur[name + '.png'] = MAN[name + '.png']
    json.dump(dict(sorted(cur.items())), open(mp, 'w'), indent=1, ensure_ascii=False)


def noise_tex(NW, NH, seed, f=6):
    return fbm(NW, NH, f=f, octaves=4, seed=seed) * 0.5 + 0.5


def slab(W, H, r, *, pad=0, outline=2.0, rim=None, bt=3.0, face=None, inner_dark=0.5, noise=0.0, seed=1, gloss=0.0,
         pressed=False, face_alpha=1.0, light=(-0.35, -0.85), rim_strength=1.0, hollow=False, vig=0.25, glow_col=None,
         glow_k=0.0, face_inset_light=0.0, tab=False, rim_spec=0.35, outline_col=None, depth=1.0):
    NW, NH = W * SS, H * SS
    ext = (r + 2) * SS if tab else 0
    sd = sdf_rrect(NW, NH + ext, pad * SS, pad * SS, NW - pad * SS, NH + ext - (pad * SS if not tab else -ext), r * SS)[:NH]
    img = blank(NW, NH)
    put(img, cov(sd), C['ink'] if outline_col is None else outline_col)
    sd_r = sd + outline * SS
    a_rim = cov(sd_r)
    lt = (light[0] * (-1 if pressed else 1), light[1] * (-1 if pressed else 1))
    if rim is not None and bt > 0:
        over(img, lit(a_rim, np.maximum(-sd_r, 0), rim[0], rim[1], bt * SS, light=lt, strength=rim_strength, spec=rim_spec,
                      depth=depth, rows=(0, NH)))
    sd_f = sd + (outline + bt) * SS
    a_face = cov(sd_f)
    df = np.maximum(-sd_f, 0)
    if hollow:
        inner = cov(sd_f) * (1 - cov(sd_f + 1.5 * SS))
        put(img, inner, C['ink'], 0.9)
        img *= (1 - cov(sd_f + 1.5 * SS))[..., None]
        return img
    hi, lo = face
    col = vgrad(NH, NW, hi, lo, 0, NH)
    if noise > 0:
        n = noise_tex(NW, NH, seed)
        col = col * (1 + noise * (n[..., None] - 0.5) * 2)
    col = col * (1 - vig * np.exp(-df / (16 * SS)))[..., None]
    if face_inset_light > 0:
        col = col + face_inset_light * np.exp(-df / (2.0 * SS))[..., None] * (1 if not pressed else 0.3)
    fl = np.empty_like(img)
    fl[..., :3] = np.clip(col, 0, 1.5) * a_face[..., None] * face_alpha
    fl[..., 3] = a_face * face_alpha
    if face_alpha < 1:
        img *= (1 - a_face)[..., None] * 0 + 1  # garde le rim
        img[..., :4] *= (1 - a_face)[..., None]
    over(img, fl) if face_alpha >= 1 else over(img, fl)
    # ombre interieure du rim
    sh = np.exp(-df / (2.6 * SS)) * inner_dark * a_face
    if pressed:
        sh = sh * 1.3
    put(img, sh * (1 - 0.0), C['ink'], 1.0)
    if pressed:  # ombre portee interne haut
        y = np.arange(NH, dtype=F32)[:, None]
        put(img, np.clip(1 - (y - (outline + bt) * SS) / (7 * SS), 0, 1) ** 2 * a_face, C['ink'], 0.45)
    if gloss > 0:
        y = np.arange(NH, dtype=F32)[:, None]
        t = (y - (outline + bt) * SS) / (NH * 0.5)
        g = np.clip(1 - t, 0, 1) ** 1.6 * a_face
        put(img, g, [1, 1, 1], gloss)
    if glow_col is not None:
        glow(img, np.exp(-df / (5 * SS)) * a_face, glow_col, glow_k)
    return img


def ornament_corner(Wd, Hd, W, H, col_hi=None, col_lo=None, inset=5, length=18, w=2.2, diamond=True):
    """crochets d'angle dores, retournent un calque premultiplie."""
    col_hi = MAT['gold'][0] if col_hi is None else col_hi
    col_lo = MAT['gold'][1] if col_lo is None else col_lo
    D = Draw(W, H, SS, norm=False)
    for (cx, cy, sx, sy) in ((inset, inset, 1, 1), (W - inset, inset, -1, 1), (inset, H - inset, 1, -1), (W - inset, H - inset, -1, -1)):
        D.path([(cx, cy + sy * length), (cx, cy), (cx + sx * length, cy)], w)
        if diamond:
            D.poly([(cx - sx * 1, cy - sy * 1 - 3.2 * sy), (cx + 3.4 * sx - sx, cy - sy * 1), (cx - sx, cy + 3.2 * sy - sy), (cx - 3.4 * sx - sx, cy - sy)])
    m = D.mask()
    return lit(m, edt_in(m), col_hi, col_lo, 1.4 * SS, spec=0.5, rows=(0, H * SS)), m


def finish(img, W, H):
    return finalize(img, W, H)


# ------------------------------------------------------------------ panneaux
def panel_dark():
    W = H = 128
    img = slab(W, H, 10, rim=(C['steel_hi'], C['steel_lo']), bt=3, face=(C['anth2'], hexc('#10141f')), noise=0.05, vig=0.35,
               inner_dark=0.55, gloss=0.04)
    # fin liseré intérieur
    return img


def panel_dark_gold():
    W = H = 128
    img = slab(W, H, 8, rim=(MAT['gold'][0], MAT['gold'][1]), bt=2.2, outline=2, face=(hexc('#222a3f'), hexc('#0f1420')), noise=0.05,
               vig=0.35, inner_dark=0.6, gloss=0.05, rim_spec=0.6)
    # second liseré fin, intérieur
    sd = sdf_rrect(W * SS, H * SS, 8 * SS, 8 * SS, (W - 8) * SS, (H - 8) * SS, 4 * SS)
    ln = cov(sd + 0.7 * SS) * (1 - cov(sd - 0.7 * SS + 1.4 * SS))
    ln = cov(np.abs(sd) - 0.55 * SS)
    put(img, ln, C['gold_mid'], 0.5)
    orn, m = ornament_corner(0, 0, W, H, inset=6, length=20, w=2.6)
    drop_shadow(img, m, 0.5 * SS, 0.8 * SS, 1.2 * SS, C['ink'], 0.7)
    over(img, orn)
    return img


def panel_glass():
    W = H = 128
    NW = W * SS
    img = slab(W, H, 12, rim=(hexc('#aab9dd'), hexc('#4d5c84')), bt=1.6, outline=1.5, face=(hexc('#24385c'), hexc('#0e1a30')),
               face_alpha=0.62, vig=0.2, inner_dark=0.15, gloss=0.16, noise=0.03, rim_strength=0.8)
    return img


def panel_header():
    W, H = 256, 64
    img = slab(W, H, 8, rim=(MAT['gold'][0], MAT['gold'][1]), bt=2.0, face=(hexc('#2e3752'), hexc('#161c2c')), noise=0.04, gloss=0.10,
               rim_spec=0.5, vig=0.25)
    NW, NH = W * SS, H * SS
    x, y = grid(NW, NH)
    # liseré doré bas
    put(img, cov(np.abs(y - (H - 11) * SS) - 0.7 * SS) * (smoothstep(8 * SS, 40 * SS, x) * smoothstep(8 * SS, 40 * SS, NW - x)), C['gold_mid'], 0.85)
    # pastilles aux extrémités
    D = Draw(W, H, SS, norm=False)
    for cx in (15, W - 15):
        D.poly([(cx, H / 2 - 9), (cx + 7, H / 2), (cx, H / 2 + 9), (cx - 7, H / 2)])
    m = D.mask()
    drop_shadow(img, m, 0.4 * SS, 0.8 * SS, 1.2 * SS, C['ink'], 0.7)
    over(img, lit(m, edt_in(m), MAT['gold'][0], MAT['gold'][1], 2.5 * SS, spec=0.6, rows=(0, NH)))
    return img


def panel_inset():
    W = H = 96
    img = slab(W, H, 6, rim=(hexc('#05070c'), hexc('#363f58')), bt=2.0, outline=1.0, face=(hexc('#0b0f19'), hexc('#121827')),
               noise=0.05, vig=0.1, inner_dark=0.0, pressed=True, rim_strength=0.9)
    NW, NH = W * SS, H * SS
    y = np.arange(NH, dtype=F32)[:, None]
    a = cov(sdf_rrect(NW, NH, 0, 0, NW, NH, 6 * SS) + 3 * SS)
    put(img, np.clip(1 - (y - 3 * SS) / (8 * SS), 0, 1) ** 2 * a, C['ink'], 0.6)
    return img


def panel_parchment():
    W = H = 128
    NW = NH = W * SS
    img = slab(W, H, 6, rim=(hexc('#8a6a3a'), hexc('#3e2a14')), bt=2.0, outline=1.5, face=(C['parch_hi'], C['parch_lo']), noise=0.0,
               vig=0.0, inner_dark=0.0)
    a = cov(sdf_rrect(NW, NH, 0, 0, NW, NH, 6 * SS) + 3.5 * SS)
    n = fbm(NW, NH, 5, 5, seed=3) * 0.5 + 0.5
    n2 = fbm(NW, NH, 24, 3, seed=9) * 0.5 + 0.5
    tint = (n[..., None] - 0.5) * 0.18 + (n2[..., None] - 0.5) * 0.06
    base = vgrad(NH, NW, C['parch_hi'], C['parch_lo'], 0, NH) * (1 + tint)
    d = np.maximum(-(sdf_rrect(NW, NH, 0, 0, NW, NH, 6 * SS) + 3.5 * SS), 0)
    burn = np.exp(-d / (11 * SS))[..., None]
    base = mix(base, hexc('#5a3a1a'), np.clip(burn * 0.55, 0, 1))
    put(img, a, base)
    inner_shadow(img, a, 0, 0, 0, C['ink'], 0)
    return img


def card_frame(rar=None):
    W, H = 192, 256
    cols = {'common': ('#c9ced8', '#6b7284'), 'uncommon': ('#8ff08a', '#2f8a3c'), 'rare': ('#7fc4ff', '#2559b8'),
            'epic': ('#d9a0ff', '#6b2fb8'), 'legendary': ('#ffe9a0', '#c0701a')}
    if rar is None:
        hi, lo = MAT['gold']
        rim = (hexc('#c9a45a'), hexc('#5e4318'))
        glow_c = None
    else:
        hi, lo = hexc(cols[rar][0]), hexc(cols[rar][1])
        rim = (hi, lo)
        glow_c = hi
    img = slab(W, H, 12, rim=rim, bt=5, outline=2.5, face=(hexc('#222a3f'), hexc('#0d111c')), noise=0.05, vig=0.4, inner_dark=0.7,
               gloss=0.05, rim_spec=0.7, glow_col=glow_c, glow_k=0.18 if rar else 0)
    NW, NH = W * SS, H * SS
    # liseré intérieur + coins ornés
    sd = sdf_rrect(NW, NH, 11 * SS, 11 * SS, NW - 11 * SS, NH - 11 * SS, 6 * SS)
    put(img, cov(np.abs(sd) - 0.6 * SS), hi if rar else C['gold_mid'], 0.55)
    orn, m = ornament_corner(0, 0, W, H, col_hi=hi if rar else None, col_lo=lo if rar else None, inset=14, length=22, w=3.0)
    drop_shadow(img, m, 0.5 * SS, 0.8 * SS, 1.2 * SS, C['ink'], 0.7)
    over(img, orn)
    return img


def tooltip():
    W = H = 96
    return slab(W, H, 6, rim=(hexc('#d6a850'), hexc('#6a4515')), bt=1.4, outline=1.5, face=(hexc('#161b2a'), hexc('#0a0d16')),
                vig=0.2, inner_dark=0.3, noise=0.03)


# ------------------------------------------------------------------ boutons
BTN = {
    'primary': dict(face=('#ffd36a', '#c0701a'), rim=('#fff1b8', '#7a4410'), glowc='#ffe08a'),
    'secondary': dict(face=('#4a5c86', '#242e4a'), rim=('#9fb2dc', '#2b3550'), glowc='#8fb4ff'),
    'danger': dict(face=('#e8505e', '#8f1a2c'), rim=('#ffb0b0', '#5a0e1a'), glowc='#ff7a80'),
}


def button(kind, state, W=160, H=56):
    d = BTN[kind]
    fh, fl = hexc(d['face'][0]), hexc(d['face'][1])
    rh, rl = hexc(d['rim'][0]), hexc(d['rim'][1])
    kw = dict(r=11, outline=2.2, bt=3.2, vig=0.18, inner_dark=0.35, gloss=0.22, noise=0.0, rim_spec=0.5)
    if state == 'hover':
        fh, fl = lighten(fh, 0.22), lighten(fl, 0.15)
        rh = lighten(rh, 0.2)
        kw.update(glow_col=hexc(d['glowc']), glow_k=0.35, gloss=0.3)
    elif state == 'pressed':
        fh, fl = darken(fl, 0.05), darken(fl, 0.35)
        rh, rl = darken(rh, 0.3), darken(rl, 0.3)
        kw.update(pressed=True, gloss=0.04, inner_dark=0.5)
    elif state == 'disabled':
        g = lambda c: hexc('#555a68') if c is fh else hexc('#383c48')
        fh, fl = hexc('#4f5462'), hexc('#343845')
        rh, rl = hexc('#6b7184'), hexc('#2c303b')
        kw.update(gloss=0.05, inner_dark=0.2, rim_spec=0.15)
    img = slab(W, H, face=(fh, fl), rim=(rh, rl), **kw)
    return img


def btn_tab(active):
    W, H = 128, 44
    if active:
        img = slab(W, H, 9, tab=True, rim=(MAT['gold'][0], MAT['gold'][1]), bt=2.0, outline=2, face=(hexc('#3a4668'), hexc('#1f2740')), gloss=0.2,
                   glow_col=hexc('#ffe08a'), glow_k=0.1, rim_spec=0.5)
    else:
        img = slab(W, H, 9, tab=True, rim=(hexc('#58647f'), hexc('#262d42')), bt=2.0, outline=2, face=(hexc('#222a3f'), hexc('#121725')), gloss=0.06)
    return img


def btn_icon(state):
    W = H = 56
    face = ('#3d4c72', '#1f2842')
    rim = ('#aebce0', '#2b3550')
    fh, fl, rh, rl = [hexc(x) for x in face + rim]
    kw = dict(r=12, outline=2.0, bt=3.0, gloss=0.18, inner_dark=0.4, vig=0.2)
    if state == 'hover':
        fh, fl, rh = lighten(fh, 0.2), lighten(fl, 0.14), lighten(rh, 0.2)
        kw.update(glow_col=hexc('#9ec0ff'), glow_k=0.35)
    elif state == 'pressed':
        fh, fl = darken(fl, 0.1), darken(fl, 0.4)
        rh, rl = darken(rh, 0.35), darken(rl, 0.3)
        kw.update(pressed=True, gloss=0.03)
    return slab(W, H, face=(fh, fl), rim=(rh, rl), **kw)


# ------------------------------------------------------------------ barres
def bar_frame():
    W, H = 256, 32
    return slab(W, H, 11, rim=(hexc('#8895b5'), hexc('#2a3248')), bt=2.6, outline=2.0, hollow=True, rim_spec=0.5)


def bar_bg():
    W, H = 256, 32
    return slab(W, H, 11, outline=2.0, bt=0, face=(hexc('#07090f'), hexc('#161c2b')), vig=0.0, inner_dark=0.6, noise=0.0)


def bar_fill(hi, lo, W=256, H=32, stripes=False):
    NW, NH = W * SS, H * SS
    sd = sdf_rrect(NW, NH, 0, 0, NW, NH, 11 * SS)
    a = cov(sd)
    d = np.maximum(-sd, 0)
    hi, lo = hexc(hi), hexc(lo)
    y = np.arange(NH, dtype=F32)[:, None, None] / NH
    # degradé vertical avec zone claire en haut-milieu, sombre en bas
    col = np.broadcast_to(mix(lighten(hi, 0.15), lo, np.clip(y * 1.25, 0, 1)), (NH, NW, 3)).copy()
    col = col * (1 - 0.35 * np.exp(-d / (3 * SS)))[..., None] + 0.0
    img = blank(NW, NH)
    put(img, a, col)
    yy = np.arange(NH, dtype=F32)[:, None]
    gloss = np.clip(1 - np.abs(yy - NH * 0.28) / (NH * 0.2), 0, 1) ** 1.4 * a
    put(img, gloss * 0.9, [1, 1, 1], 0.28)
    put(img, np.clip(1 - np.abs(yy - NH * 0.86) / (NH * 0.14), 0, 1) * a * 0.6, lighten(hi, 0.4), 0.25)
    if stripes:
        x = np.arange(NW, dtype=F32)[None, :]
        s = (np.sin((x + yy) / (4 * SS) * np.pi) > 0.3).astype(F32) * a
        put(img, s, [1, 1, 1], 0.07)
    return img


def slider_track():
    W, H = 128, 12
    return slab(W, H, 5, outline=1.5, bt=0, face=(hexc('#05070c'), hexc('#1a2132')), vig=0, inner_dark=0.6)


def slider_grabber():
    W = H = 28
    NW = W * SS
    D = Draw(W, H, SS, norm=False)
    D.circle(14, 14, 12)
    m = D.mask()
    img = blank(NW)
    drop_shadow(img, m, 0, 1.5 * SS, 1.5 * SS, C['ink'], 0.7)
    put(img, dilate(m, 0), C['ink'])
    inner = erode(m, 1.8 * SS)
    over(img, lit(m, edt_in(m), hexc('#fff1b8'), hexc('#a86a1a'), 4 * SS, spec=0.6, rows=(0, NW)))
    over(img, lit(inner, edt_in(inner), hexc('#ffd36a'), hexc('#c0701a'), 5 * SS, spec=0.5, rows=(0, NW), light=(-0.3, -0.9)))
    D2 = Draw(W, H, SS, norm=False)
    D2.circle(14, 14, 3.4)
    m2 = D2.mask()
    put(img, m2, hexc('#6b3c0c'), 0.85)
    return img


def checkbox(on):
    W = H = 32
    NW = W * SS
    img = slab(W, H, 6, rim=(hexc('#8895b5'), hexc('#2a3248')), bt=2.0, outline=1.8,
               face=(hexc('#0a0e18'), hexc('#1a2236')) if not on else (hexc('#3a2c14'), hexc('#1c1408')), vig=0.2, inner_dark=0.5, pressed=not on)
    if on:
        D = Draw(W, H, SS, norm=False)
        D.path([(8, 16.5), (13.5, 22), (24, 9.5)], 4.0)
        m = D.mask()
        glow(img, blur(m, 3 * SS), hexc('#ffd36a'), 0.7)
        drop_shadow(img, m, 0.4 * SS, 0.9 * SS, 0.8 * SS, C['ink'], 0.8)
        over(img, lit(m, edt_in(m), hexc('#fff6c8'), hexc('#e0a030'), 2.2 * SS, spec=0.5, rows=(6 * SS, 26 * SS)))
    return img


def scroll_track():
    W, H = 14, 64
    return slab(W, H, 5, outline=1.2, bt=0, face=(hexc('#07090f'), hexc('#161c2b')), vig=0, inner_dark=0.6)


def scroll_grabber():
    W, H = 14, 64
    return slab(W, H, 5, outline=1.4, bt=2.0, rim=(hexc('#aebce0'), hexc('#2b3550')), face=(hexc('#4a5c86'), hexc('#27304c')), gloss=0.15, vig=0.1, inner_dark=0.3)


def main():
    out = [('panel_dark', panel_dark(), 128, 128, [20] * 4, '9-patch sombre acier'),
           ('panel_dark_gold', panel_dark_gold(), 128, 128, [24] * 4, 'liseré or + coins'),
           ('panel_glass', panel_glass(), 128, 128, [20] * 4, 'verre translucide'),
           ('panel_header', panel_header(), 256, 64, [30, 16, 30, 16], 'bandeau titre'),
           ('panel_inset', panel_inset(), 96, 96, [12] * 4, 'zone en creux'),
           ('panel_parchment', panel_parchment(), 128, 128, [22] * 4, 'parchemin'),
           ('card_frame', card_frame(), 192, 256, [28] * 4, 'carte ornée (centre opaque sombre)'),
           ('tooltip', tooltip(), 96, 96, [12] * 4, 'infobulle')]
    for r in ('common', 'uncommon', 'rare', 'epic', 'legendary'):
        out.append((f'rarity_card_{r}', card_frame(r), 192, 256, [28] * 4, f'carte rareté {r}'))
    for k in BTN:
        for st in ('normal', 'hover', 'pressed', 'disabled'):
            out.append((f'btn_{k}_{st}', button(k, st), 160, 56, [18, 16, 18, 18], f'bouton {k} {st}'))
    out += [('btn_tab_normal', btn_tab(False), 128, 44, [14, 14, 14, 4], 'onglet'),
            ('btn_tab_active', btn_tab(True), 128, 44, [14, 14, 14, 4], 'onglet actif')]
    for st in ('normal', 'hover', 'pressed'):
        out.append((f'btn_icon_{st}', btn_icon(st), 56, 56, [16] * 4, 'bouton icône'))
    out += [('bar_frame', bar_frame(), 256, 32, [12, 12, 12, 12], 'cadre de barre (centre transparent)'),
            ('bar_bg', bar_bg(), 256, 32, [12, 12, 12, 12], 'fond de barre'),
            ('bar_fill_hp', bar_fill('#ff6a6a', '#a8122a'), 256, 32, [12, 12, 12, 12], 'remplissage'),
            ('bar_fill_mana', bar_fill('#7cc4ff', '#2150c8'), 256, 32, [12, 12, 12, 12], 'remplissage'),
            ('bar_fill_stamina', bar_fill('#d6f65a', '#3f9a2a'), 256, 32, [12, 12, 12, 12], 'remplissage'),
            ('bar_fill_xp', bar_fill('#cf96ff', '#612bc0', stripes=True), 256, 32, [12, 12, 12, 12], 'remplissage'),
            ('bar_fill_gold', bar_fill('#ffe27a', '#b8741a'), 256, 32, [12, 12, 12, 12], 'remplissage'),
            ('slider_track', slider_track(), 128, 12, [6, 6, 6, 6], 'piste'),
            ('slider_grabber', slider_grabber(), 28, 28, [0, 0, 0, 0], 'poignée'),
            ('checkbox_off', checkbox(False), 32, 32, [0, 0, 0, 0], 'case'),
            ('checkbox_on', checkbox(True), 32, 32, [0, 0, 0, 0], 'case cochée'),
            ('scroll_track', scroll_track(), 14, 64, [6, 6, 6, 6], 'piste'),
            ('scroll_grabber', scroll_grabber(), 14, 64, [6, 8, 6, 8], 'ascenseur')]
    for name, img, W, H, m, note in out:
        reg(name, finalize(img, W, H), m, note)
    return out


if __name__ == '__main__':
    main()
    print(len(MAN))
