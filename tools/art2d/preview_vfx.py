import sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
V = ASSETS + '/textures/vfx'
PV = ASSETS + '/ui/preview'
def tinted(name, tint=None, bg=(26, 30, 42)):
    im = Image.open(f'{V}/{name}.png').convert('RGBA')
    if tint:
        a = np.asarray(im).astype(np.float32)
        a[..., :3] = a[..., :3] * np.array(tint, np.float32) / 255.0
        im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return im
def sheet(names, cols, cell, out, tints=None):
    tints = tints or {}
    ims = [tinted(n, tints.get(n)) for n in names]
    contact(ims, cols, cell, out, bg=(26, 30, 42), pad=4)
if __name__ == '__main__':
    A = ['soft_glow', 'glow_ring', 'spark_star4', 'spark_cross', 'flare_streak', 'ember', 'smoke_puff_0', 'smoke_puff_1', 'smoke_puff_2', 'smoke_puff_3', 'dust_puff',
         'fire_tongue_0', 'fire_tongue_1', 'fire_tongue_2', 'fire_tongue_3', 'flame_sprite_sheet', 'ice_shard_0', 'ice_shard_1', 'ice_shard_2', 'snow_flake',
         'lightning_bolt_0', 'lightning_bolt_1', 'lightning_bolt_2', 'lightning_bolt_3', 'lightning_arc']
    t = {'fire_tongue_%d' % i: (255, 150, 60) for i in range(4)}
    t['flame_sprite_sheet'] = (255, 150, 60)
    t.update({'ice_shard_%d' % i: (150, 220, 255) for i in range(3)})
    t.update({'lightning_bolt_%d' % i: (255, 235, 120) for i in range(4)})
    t['lightning_arc'] = (255, 235, 120); t['ember'] = (255, 140, 50); t['snow_flake'] = (200, 235, 255)
    sheet(A, 7, 200, PV + '/vfx_1.png', t)
    B = ['slash_arc_%d' % i for i in range(5)] + ['slash_cross', 'hit_flash_star', 'shock_ring', 'magic_swirl', 'heal_plus', 'leaf', 'feather', 'bat_silhouette', 'crack_decal', 'scorch_decal', 'frost_decal',
         'shadow_blob', 'light_ray', 'droplet', 'shield_hex'] + ['rune_circle_%d' % i for i in range(6)] + ['rune_glyph_sheet', 'noise_perlin', 'noise_cell', 'gradient_ramp_toon', 'vignette', 'film_grain']
    t2 = {'heal_plus': (140, 255, 160), 'leaf': (120, 220, 90), 'droplet': (110, 200, 255), 'shield_hex': (110, 190, 255), 'shock_ring': (255, 220, 160), 'magic_swirl': (190, 140, 255),
          'light_ray': (255, 240, 180), 'frost_decal': (170, 230, 255), 'hit_flash_star': (255, 230, 150)}
    t2.update({'slash_arc_%d' % i: (255, 245, 220) for i in range(5)})
    t2.update({'rune_circle_%d' % i: (170, 130, 255) for i in range(6)}); t2['rune_glyph_sheet'] = (170, 130, 255)
    sheet(B, 8, 170, PV + '/vfx_2.png', t2)
