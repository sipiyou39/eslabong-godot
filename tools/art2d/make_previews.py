"""Planches contact (assets/ui/preview) pour controle visuel."""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import preview_skin as ps, preview_vfx as pv, sheets as sh

PV = ASSETS + '/ui/preview'


def tint(p, col):
    a = np.asarray(Image.open(p).convert('RGBA')).astype(np.float32)
    a[..., :3] *= np.array(col, np.float32) / 255.0
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def main():
    ps.sheet(['panel_dark', 'panel_dark_gold', 'panel_glass', 'panel_header', 'panel_inset', 'panel_parchment', 'tooltip', 'card_frame', 'rarity_card_epic', 'rarity_card_legendary'],
             [(220, 150), (220, 150), (220, 150), (320, 56), (220, 150), (220, 150), (200, 90), (170, 230), (170, 230), (170, 230)], 4, PV + '/skin_panels.png')
    names = [f'btn_{k}_{s}' for k in ('primary', 'secondary', 'danger') for s in ('normal', 'hover', 'pressed', 'disabled')] + ['btn_tab_normal', 'btn_tab_active', 'btn_icon_normal', 'btn_icon_hover', 'btn_icon_pressed']
    ps.sheet(names, [(170, 56)] * 12 + [(130, 44), (130, 44), (56, 56), (56, 56), (56, 56)], 4, PV + '/skin_buttons.png')
    ps.sheet(['bar_bg', 'bar_frame', 'bar_fill_hp', 'bar_fill_mana', 'bar_fill_stamina', 'bar_fill_xp', 'bar_fill_gold', 'slider_track', 'slider_grabber', 'checkbox_off', 'checkbox_on', 'scroll_track', 'scroll_grabber'],
             [(300, 32), (300, 32), (300, 32), (180, 32), (240, 32), (260, 32), (300, 32), (220, 12), None, None, None, (14, 120), (14, 60)], 2, PV + '/skin_bars.png')
    SK = ASSETS + '/ui/skin'
    S = Image.new('RGBA', (1500, 760), (44, 48, 62, 255))
    def p(n, xy, sc=1):
        im = Image.open(f'{SK}/{n}.png').convert('RGBA')
        if sc != 1:
            im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        S.alpha_composite(im, xy)
    p('logo_emblem', (10, 10), 0.9); p('title_plate', (480, 10), 0.7); p('divider_gold', (480, 200)); p('banner_ribbon', (480, 230))
    p('hex_slot', (480, 310)); p('slot_square', (600, 320)); p('slot_square_hover', (700, 320)); p('corner_ornament', (800, 320)); p('toast_bg', (900, 320))
    S.alpha_composite(Image.open(f'{SK}/bg_stonewall.png').convert('RGBA').resize((300, 300), Image.LANCZOS), (480, 420))
    S.alpha_composite(Image.open(f'{SK}/menu_bg_gradient.png').convert('RGBA').resize((480, 270), Image.LANCZOS), (800, 420))
    S.convert('RGB').save(PV + '/skin_misc.png')
    # vfx
    A = ['soft_glow', 'glow_ring', 'spark_star4', 'spark_cross', 'flare_streak', 'ember', 'smoke_puff_0', 'smoke_puff_1', 'smoke_puff_2', 'smoke_puff_3', 'dust_puff', 'fire_tongue_0', 'fire_tongue_1', 'fire_tongue_2', 'fire_tongue_3',
         'flame_sprite_sheet', 'ice_shard_0', 'ice_shard_1', 'ice_shard_2', 'snow_flake', 'lightning_bolt_0', 'lightning_bolt_1', 'lightning_bolt_2', 'lightning_bolt_3', 'lightning_arc']
    t = {'fire_tongue_%d' % i: (255, 150, 60) for i in range(4)}; t['flame_sprite_sheet'] = (255, 150, 60); t['ember'] = (255, 140, 50)
    t.update({'ice_shard_%d' % i: (150, 220, 255) for i in range(3)}); t.update({'lightning_bolt_%d' % i: (255, 235, 120) for i in range(4)}); t['lightning_arc'] = (255, 235, 120); t['snow_flake'] = (200, 235, 255)
    pv.sheet(A, 7, 200, PV + '/vfx_1.png', t)
    B = ['slash_arc_%d' % i for i in range(5)] + ['slash_cross', 'hit_flash_star', 'shock_ring', 'magic_swirl', 'heal_plus', 'leaf', 'feather', 'bat_silhouette', 'crack_decal', 'scorch_decal', 'frost_decal',
        'shadow_blob', 'light_ray', 'droplet', 'shield_hex'] + ['rune_circle_%d' % i for i in range(6)] + ['rune_glyph_sheet', 'noise_perlin', 'noise_cell', 'gradient_ramp_toon', 'vignette', 'film_grain']
    t2 = {'heal_plus': (140, 255, 160), 'leaf': (120, 220, 90), 'droplet': (110, 200, 255), 'shield_hex': (110, 190, 255), 'shock_ring': (255, 220, 160), 'magic_swirl': (190, 140, 255), 'light_ray': (255, 240, 180),
          'frost_decal': (170, 230, 255), 'hit_flash_star': (255, 230, 150)}
    t2.update({'slash_arc_%d' % i: (255, 245, 220) for i in range(5)}); t2.update({'rune_circle_%d' % i: (170, 130, 255) for i in range(6)}); t2['rune_glyph_sheet'] = (170, 130, 255)
    pv.sheet(B, 8, 170, PV + '/vfx_2.png', t2)
    # icones
    sh.folder_sheet(ASSETS + '/ui/icons', PV + '/ui_icons.png', 13, 80, scale=1.6)
    sh.folder_sheet(ASSETS + '/icons/status', PV + '/status_icons.png', 11, 84, scale=2.4)
    sh.folder_sheet(ASSETS + '/icons/classes', PV + '/classes.png', 10, 100)
    ab = json.load(open(ROOT + '/data/abilities.json'))
    import random
    fs = sorted(glob.glob(ASSETS + '/icons/abilities/*.png'))
    random.seed(5)
    contact(random.sample(fs, 84), 12, 100, PV + '/abilities_sample.png', pad=3)
    contact([ASSETS + f'/icons/abilities/{a["id"]}.png' for a in ab if a.get('ultimate')], 7, 128, PV + '/abilities_ultimates.png', pad=3)
    # un par glyphe
    seen, one = set(), []
    for a in ab:
        if a['icon_glyph'] not in seen:
            seen.add(a['icon_glyph']); one.append(ASSETS + f'/icons/abilities/{a["id"]}.png')
    contact(one, 8, 128, PV + '/abilities_by_glyph.png', pad=3)
    rl = json.load(open(ROOT + '/data/relics.json'))
    byk = {r['key']: r for r in rl['relics']}
    ims = []
    for k in rl['names']:
        ic = Image.open(ASSETS + f'/icons/relics/{k}.png').convert('RGBA')
        ic.alpha_composite(Image.open(ASSETS + f'/ui/skin/rarity_{byk[k]["rarity"]}.png').convert('RGBA'))
        ims.append(ic)
    contact(ims, 9, 96, PV + '/relics.png', pad=4)
    H = ASSETS + '/ui/heraldry'
    contact([tint(f'{H}/charge_{i:03d}.png', (235, 220, 170)) for i in range(64)], 16, 80, PV + '/heraldry_charges.png', pad=3)
    contact([tint(f'{H}/division_{i:02d}.png', (200, 200, 230)) for i in range(16)] + [tint(f'{H}/shield_{i:02d}.png', (200, 200, 230)) for i in range(8)], 12, 96, PV + '/heraldry_divs.png', pad=3)


if __name__ == '__main__':
    main()
