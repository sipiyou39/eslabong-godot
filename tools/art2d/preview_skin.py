import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
SK = ASSETS + '/ui/skin'
PV = ASSETS + '/ui/preview'

def ninepatch(im, m, size):
    l, t, r, b = m
    W, H = im.size
    w, h = size
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    xs = [(0, l, 0, l), (l, W - r, l, w - r), (W - r, W, w - r, w)]
    ys = [(0, t, 0, t), (t, H - b, t, h - b), (H - b, H, h - b, h)]
    for (sx0, sx1, dx0, dx1) in xs:
        for (sy0, sy1, dy0, dy1) in ys:
            if sx1 <= sx0 or sy1 <= sy0 or dx1 <= dx0 or dy1 <= dy0:
                continue
            piece = im.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.BILINEAR)
            out.alpha_composite(piece, (dx0, dy0))
    return out

def sheet(names, sizes, cols, out, bg=(52, 56, 70), pad=14):
    man = json.load(open(SK + '/ui_manifest.json'))
    items = []
    for n, sz in zip(names, sizes):
        im = Image.open(f'{SK}/{n}.png').convert('RGBA')
        m = man[n + '.png']['margins']
        sz = sz or im.size
        items.append(ninepatch(im, m, sz) if any(m) else im)
    cw = max(i.width for i in items) + pad
    chh = max(i.height for i in items) + pad
    rows = (len(items) + cols - 1) // cols
    S = Image.new('RGBA', (cols * cw + pad, rows * chh + pad), bg + (255,))
    # damier léger
    for i, it in enumerate(items):
        S.alpha_composite(it, (pad + (i % cols) * cw, pad + (i // cols) * chh))
    os.makedirs(PV, exist_ok=True)
    S.convert('RGB').save(out)

if __name__ == '__main__':
    which = sys.argv[1]
    if which == 'panels':
        names = ['panel_dark', 'panel_dark_gold', 'panel_glass', 'panel_header', 'panel_inset', 'panel_parchment', 'tooltip', 'card_frame', 'rarity_card_epic', 'rarity_card_legendary']
        sizes = [(220, 150), (220, 150), (220, 150), (320, 56), (220, 150), (220, 150), (200, 90), (170, 230), (170, 230), (170, 230)]
        sheet(names, sizes, 4, PV + '/skin_panels.png')
    if which == 'buttons':
        names = [f'btn_{k}_{s}' for k in ('primary', 'secondary', 'danger') for s in ('normal', 'hover', 'pressed', 'disabled')]
        names += ['btn_tab_normal', 'btn_tab_active', 'btn_icon_normal', 'btn_icon_hover', 'btn_icon_pressed']
        sizes = [(170, 56)] * 12 + [(130, 44), (130, 44), (56, 56), (56, 56), (56, 56)]
        sheet(names, sizes, 4, PV + '/skin_buttons.png')
    if which == 'bars':
        names = ['bar_bg', 'bar_frame', 'bar_fill_hp', 'bar_fill_mana', 'bar_fill_stamina', 'bar_fill_xp', 'bar_fill_gold', 'slider_track', 'slider_grabber', 'checkbox_off', 'checkbox_on', 'scroll_track', 'scroll_grabber']
        sizes = [(300, 32), (300, 32), (300, 32), (180, 32), (240, 32), (260, 32), (300, 32), (220, 12), None, None, None, (14, 120), (14, 60)]
        sheet(names, sizes, 2, PV + '/skin_bars.png')
