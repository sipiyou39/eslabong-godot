"""Planches contact du kit grec : importe kit_bodies.glb + kit_greek.glb (valide donc COLOR_0) et rend avec le matériau test.
   Blender -b --python preview_greek.py -- gear|gods|all [--glb chemin] [--out dossier]
Les planches (PNG) sont assemblées ensuite par compose.py (Pillow) : python preview_greek.py est suivi de run_preview.sh."""
import sys, os, json, math
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import gk_paths
ROOT = gk_paths.ROOT
sys.path.insert(0, os.path.join(ROOT, 'tools', 'blender_kit_bodies'))
import bpy
import preview_lib as pl

argv = sys.argv[sys.argv.index('--') + 1:]
what = argv[0]
KIT = os.path.join(ROOT, 'assets', 'models', 'kit')
GLB = argv[argv.index('--glb') + 1] if '--glb' in argv else os.path.join(KIT, 'kit_greek.glb')
TMP = os.path.join(gk_paths.SP, 'pv')
os.makedirs(TMP, exist_ok=True)
JOBS = []


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    out = {}
    for o in new:
        if o.type == 'MESH':
            out[o.name.split('.')[0]] = o
        else:
            o.hide_render = True
    return out


def show_only(objs, names):
    for n, o in objs.items():
        o.hide_render = n not in names
        o.hide_viewport = n not in names


def render_tile(cam, path, target, az, el, dist, lens, w, h):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = w, h
    pl.aim_camera(cam, target, az, el, dist)
    cam.data.lens = lens
    pl.render(path)


def to_bl(p):
    return (p[0], -p[2], p[1])


BODY = ["torso", "pelvis", "head", "arm_l", "arm_r", "leg_l", "leg_r"]
HAND = {'l': (0.34, 0.62, 0.02), 'r': (-0.34, 0.62, 0.02)}

ALL = json.load(open(os.path.join(ROOT, 'data', 'dlc', 'kit_greek_parts.json')))['parts'] if os.path.exists(os.path.join(ROOT, 'data', 'dlc', 'kit_greek_parts.json')) else []
if '--glb' in argv:
    ALL = None

GEAR = {
    'heads': (['helm_corinthian', 'crown_laurel', 'helm_winged', 'helm_hades', 'crown_sun', 'crown_moon', 'hair_beard_long', 'hair_snakes', 'helm_ares'],
              [(-32, 12, (0, 0, 1.52), 3.0, 85), (0, 8, (0, 0, 1.52), 3.0, 85), (150, 14, (0, 0, 1.52), 3.0, 85)], 3),
    'torso': (['armor_toga', 'armor_cuirass_greek', 'armor_chiton'],
              [(-32, 14, (0, 0, 0.85), 3.9, 85), (0, 8, (0, 0, 0.85), 3.9, 85), (150, 16, (0, 0, 0.85), 3.9, 85)], 3),
    'shoulders': (['shoulder_laurel', 'shoulder_gorget', 'shoulder_pteruges'],
                  [(-25, 25, (0, 0, 1.12), 3.0, 85), (0, 10, (0, 0, 1.12), 3.0, 85), (150, 20, (0, 0, 1.12), 3.0, 85)], 3),
    'backs': (['back_cape_royal', 'back_wings_hermes', 'back_sun_disk', 'back_tail_snake', 'back_quiver_gold', 'back_aegis'],
              [(150, 14, (0, 0, 0.95), 5.0, 70), (115, 12, (0, 0, 0.95), 5.0, 70), (-32, 12, (0, 0, 0.95), 5.0, 70)], 3),
}


def gear_sheets():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bodies_o = import_glb(os.path.join(KIT, 'kit_bodies.glb'))
    gear_o = import_glb(GLB)
    mat = pl.test_material()
    pl.set_material(list(bodies_o.values()) + list(gear_o.values()), mat)
    cam = pl.setup_scene(480, 520)
    human = {f'body_human_{p}' for p in BODY}
    allo = {**bodies_o, **gear_o}
    for g, (names, views, cols) in GEAR.items():
        imgs, labels = [], []
        for nm in names:
            show = set(human) | {nm}
            if g == 'shoulders':
                show = set(human) | {nm + '_l', nm + '_r'}
            if g == 'torso':
                show |= {nm + '_skirt'}
            show_only(allo, show)
            tri = 0
            pics = []
            for vi, (az, el, tgt, dist, lens) in enumerate(views):
                p = os.path.join(TMP, f'g_{nm}_{vi}.png')
                render_tile(cam, p, tgt, az, el, dist, lens, 480, 520)
                pics.append(p)
            imgs.append(pics)
            labels.append(nm)
        JOBS.append(dict(images=imgs, labels=labels, cols=2 if g != 'torso' else 1, path=os.path.join(OUTDIR, f'greek_{g}.png'), tile=[300 * len(views), 330] if g != 'torso' else [900, 400],
                         title=f'DLC Olympe — équipement : {g}'))
        print('sheet', g)


GODS = {
    'zeus': dict(gear=['hair_beard_long', 'armor_toga', 'armor_toga_skirt', 'shoulder_laurel_l', 'shoulder_laurel_r', 'back_cape_royal'], r='wpn_thunderbolt', l=None,
                 skin=(0.93, 0.76, 0.62), pal=((0.42, 0.16, 0.52), (0.88, 0.88, 0.92), (1.0, 0.8, 0.25))),
    'poseidon': dict(gear=['hair_beard_long', 'crown_laurel', 'armor_chiton', 'armor_chiton_skirt', 'shoulder_gorget_l', 'shoulder_gorget_r'], r='wpn_trident', l=None,
                     skin=(0.85, 0.7, 0.58), pal=((0.1, 0.36, 0.56), (0.72, 0.88, 0.88), (0.95, 0.78, 0.3))),
    'hades': dict(gear=['helm_hades', 'armor_toga', 'armor_toga_skirt', 'shoulder_pteruges_l', 'shoulder_pteruges_r', 'back_cape_royal'], r='wpn_bident', l=None,
                  skin=(0.72, 0.68, 0.7), pal=((0.16, 0.1, 0.22), (0.24, 0.24, 0.3), (0.45, 0.95, 0.6))),
    'athena': dict(gear=['helm_corinthian', 'armor_cuirass_greek', 'armor_cuirass_greek_skirt', 'shoulder_gorget_l', 'shoulder_gorget_r', 'back_aegis'], r='wpn_spear_greek', l='wpn_shield_aegis',
                   skin=(0.95, 0.8, 0.68), pal=((0.78, 0.55, 0.26), (0.92, 0.9, 0.82), (1.0, 0.82, 0.3))),
    'apollon': dict(gear=['crown_sun', 'armor_chiton', 'armor_chiton_skirt', 'shoulder_laurel_l', 'shoulder_laurel_r', 'back_sun_disk'], r=None, l='wpn_lyre',
                    skin=(0.95, 0.8, 0.64), pal=((0.96, 0.9, 0.7), (0.55, 0.35, 0.18), (1.0, 0.82, 0.25))),
    'artemis': dict(gear=['crown_moon', 'armor_chiton', 'armor_chiton_skirt', 'shoulder_pteruges_l', 'shoulder_pteruges_r', 'back_quiver_gold'], r=None, l='wpn_bow_golden',
                    skin=(0.95, 0.8, 0.66), pal=((0.22, 0.42, 0.28), (0.78, 0.82, 0.9), (0.9, 0.85, 0.5))),
    'hermes': dict(gear=['helm_winged', 'armor_chiton', 'armor_chiton_skirt', 'shoulder_laurel_l', 'shoulder_laurel_r', 'back_wings_hermes'], r='wpn_caduceus', l=None,
                   skin=(0.9, 0.72, 0.58), pal=((0.86, 0.9, 0.96), (0.5, 0.32, 0.16), (1.0, 0.82, 0.3))),
    'ares': dict(gear=['helm_ares', 'armor_cuirass_greek', 'armor_cuirass_greek_skirt', 'shoulder_pteruges_l', 'shoulder_pteruges_r', 'back_cape_royal'], r='wpn_kopis', l='wpn_shield_hoplon',
                 skin=(0.85, 0.66, 0.52), pal=((0.62, 0.12, 0.1), (0.72, 0.14, 0.12), (0.82, 0.58, 0.22))),
    'meduse': dict(gear=['hair_snakes', 'armor_toga', 'armor_toga_skirt', 'back_tail_snake'], r='wpn_bow_golden', l=None,
                   skin=(0.62, 0.78, 0.55), pal=((0.2, 0.36, 0.2), (0.3, 0.58, 0.22), (1.0, 0.85, 0.2))),
}


def gods_sheets():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bodies_o = import_glb(os.path.join(KIT, 'kit_bodies.glb'))
    gear_o = import_glb(GLB)
    cam = pl.setup_scene(520, 760)
    allo = {**bodies_o, **gear_o}
    for name, c in GODS.items():
        show = {f'body_human_{p}' for p in BODY} | set(c['gear'])
        mat = pl.test_material(c['pal'][0], c['pal'][1], c['pal'][2], c['skin'], name='M_' + name)
        for o in allo.values():
            o.hide_render = True
        shown = [allo[n] for n in show if n in allo]
        for o in shown:
            o.hide_render = False
        wobjs = []
        for side in ('r', 'l'):
            w = c.get(side)
            if w and w in allo:
                o = allo[w]
                o.hide_render = False
                o.location = to_bl(HAND[side])
                wobjs.append(o)
        pl.set_material(shown + wobjs, mat)
        imgs = []
        for i, (az, el, tgt, dist, lens) in enumerate([(-28, 12, (0, 0, 0.95), 5.6, 70), (150, 18, (0, 0, 0.95), 5.6, 70), (-30, 55, (0, 0, 0.8), 6.0, 70)]):
            p = os.path.join(TMP, f'a_{name}_{i}.png')
            render_tile(cam, p, tgt, az, el, dist, lens, 520, 760)
            imgs.append(p)
        for o in wobjs:
            o.location = (0, 0, 0)
            o.hide_render = True
        JOBS.append(dict(images=imgs, labels=['face 3/4', 'dos 3/4', 'vue jeu 55°'], cols=3, path=os.path.join(OUTDIR, f'assembled_{name}.png'), tile=[380, 555], title=name))
        print('sheet', name)


OUTDIR = argv[argv.index('--out') + 1] if '--out' in argv else os.path.join(KIT, 'preview_greek')
os.makedirs(OUTDIR, exist_ok=True)
if what in ('gear', 'all'):
    gear_sheets()
if what in ('gods', 'all'):
    gods_sheets()
with open(os.path.join(TMP, f'jobs_{what}.json'), 'w') as f:
    json.dump(JOBS, f)
