"""Planches contact : importe les GLB exportés (valide donc COLOR_0) et rend avec le matériau test.
   Blender -b --python make_previews.py -- bodies|gear|assembled|all"""
import sys, os, json, math
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import bpy
import preview_lib as pl
import kitlib

ROOT = os.path.abspath(os.path.join(here, '..', '..'))
KIT = os.path.join(ROOT, 'assets', 'models', 'kit')
PRE = os.path.join(KIT, 'preview')
TMP = os.path.join(PRE, '_tmp')
os.makedirs(TMP, exist_ok=True)
what = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'bodies'


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


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def show_only(objs, names):
    for n, o in objs.items():
        o.hide_render = n not in names
        o.hide_viewport = n not in names


JOBS = []


def sheet(images, labels, cols, path, tile=(380, 520), title=None):
    JOBS.append(dict(images=images, labels=labels, cols=cols, path=path, tile=tile, title=title))


def render_tile(cam, path, target, az, el, dist, lens, w=760, h=1040):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = w, h
    pl.aim_camera(cam, target, az, el, dist)
    cam.data.lens = lens
    pl.render(path)


def bodies():
    clean_scene()
    objs = import_glb(os.path.join(KIT, 'kit_bodies.glb'))
    mat = pl.test_material()
    pl.set_material(list(objs.values()), mat)
    cam = pl.setup_scene(760, 1040)
    species = ["human", "orc", "goblin", "minotaur", "skeleton", "beast", "demon"]
    parts = ["torso", "pelvis", "head", "arm_l", "arm_r", "leg_l", "leg_r"]
    for sp in species:
        names = {f'body_{sp}_{p}' for p in parts}
        if not all(n in objs for n in names):
            continue
        show_only(objs, names)
        imgs = []
        for i, (az, el, tgt, dist, lens) in enumerate([(-28, 12, (0, 0, 0.85), 5.2, 70), (150, 18, (0, 0, 0.85), 5.2, 70), (-22, 8, (0, 0, 1.38), 5.0, 200)]):
            p = os.path.join(TMP, f'b_{sp}_{i}.png')
            render_tile(cam, p, tgt, az, el, dist, lens)
            imgs.append(p)
        sheet(imgs, ['face 3/4', 'dos 3/4', 'tête'], 3, os.path.join(PRE, f'bodies_{sp}.png'), tile=(380, 520), title=f'body_{sp}_*')
        print('sheet', sp)



GEAR_VIEWS = {
    'hats': [(-32, 12, (0, 0, 1.55), 2.9, 85), (150, 14, (0, 0, 1.55), 2.9, 85)],
    'torso': [(-32, 14, (0, 0, 0.95), 3.0, 85), (150, 16, (0, 0, 0.95), 3.0, 85)],
    'skirts': [(-32, 10, (0, 0, 0.62), 3.1, 85), (150, 10, (0, 0, 0.62), 3.1, 85)],
    'shoulders': [(-25, 25, (0, 0, 1.22), 2.7, 85), (150, 20, (0, 0, 1.22), 2.7, 85)],
    'backs': [(180, 10, (0, 0, 1.05), 4.4, 80), (125, 12, (0, 0, 1.05), 4.4, 80)],
}


def gear_sheets():
    contract = json.load(open(os.path.join(ROOT, 'data', 'kit_contract.json')))
    clean_scene()
    bodies_o = import_glb(os.path.join(KIT, 'kit_bodies.glb'))
    gear_o = import_glb(os.path.join(KIT, 'kit_gear.glb'))
    mat = pl.test_material()
    pl.set_material(list(bodies_o.values()) + list(gear_o.values()), mat)
    cam = pl.setup_scene(480, 820)
    human = {f'body_human_{p}' for p in ["torso", "pelvis", "head", "arm_l", "arm_r", "leg_l", "leg_r"]}
    groups = {
        'hats': contract['hats'], 'torso': contract['torso_gear'], 'skirts': contract['torso_gear_skirts'],
        'shoulders': [f'shoulder_{n}_l' for n in contract['shoulders']], 'backs': contract['backs'],
    }
    for g, names in groups.items():
        imgs, labels = [], []
        for nm in names:
            show = set(human)
            if g == 'shoulders':
                show |= {nm, nm[:-1] + 'r'}
            else:
                show.add(nm)
            show_only({**bodies_o, **gear_o}, show)
            pair = []
            for vi, (az, el, tgt, dist, lens) in enumerate(GEAR_VIEWS[g]):
                p = os.path.join(TMP, f'g_{nm}_{vi}.png')
                render_tile(cam, p, tgt, az, el, dist, lens, 480, 820)
                pair.append(p)
            imgs.append(pair)
            labels.append(nm.replace('shoulder_', 'sh_') if g == 'shoulders' else nm)
        cols = 4 if g in ('hats', 'torso', 'backs') else 3
        sheet(imgs, labels, cols, os.path.join(PRE, f'gear_{g}.png'), tile=(400, 340), title=f'équipement : {g}')
        print('sheet', g)


# ----------------------------------------------------------------------------------------- personnages assemblés
HAND = {'l': (0.34, 0.62, 0.02), 'r': (-0.34, 0.62, 0.02)}
CHARS = {
    'human_knight': dict(sp='human', gear=['helm_knight', 'armor_plate', 'armor_plate_skirt', 'shoulder_plate_l', 'shoulder_plate_r', 'back_cape_long'],
                         r='wpn_sword_long', l='wpn_shield_kite', skin=(0.93, 0.76, 0.6), pal=((0.55, 0.58, 0.66), (0.36, 0.22, 0.12), (1.0, 0.78, 0.2)), scale=1.0),
    'orc_berserker': dict(sp='orc', gear=['helm_horned', 'armor_leather', 'armor_fur_skirt', 'shoulder_spiked_l', 'shoulder_spiked_r'],
                          r='wpn_axe_great', l=None, skin=(0.42, 0.6, 0.3), pal=((0.45, 0.2, 0.12), (0.3, 0.2, 0.12), (0.8, 0.8, 0.8)), scale=1.0),
    'goblin_rogue': dict(sp='goblin', gear=['hood_rogue', 'armor_vest_ranger', 'armor_ragged_skirt', 'shoulder_leather_l', 'shoulder_leather_r', 'back_quiver'],
                         r='wpn_dagger', l='wpn_dagger', skin=(0.5, 0.68, 0.28), pal=((0.22, 0.28, 0.2), (0.35, 0.22, 0.12), (0.9, 0.8, 0.3)), scale=0.8),
    'minotaur': dict(sp='minotaur', gear=['armor_wraps', 'armor_scale_skirt', 'shoulder_bone_l', 'shoulder_bone_r'],
                     r='wpn_axe_double', l=None, skin=(0.5, 0.33, 0.22), pal=((0.55, 0.45, 0.35), (0.25, 0.17, 0.1), (0.9, 0.75, 0.3)), scale=1.35),
    'skeleton_mage': dict(sp='skeleton', gear=['hat_wizard', 'armor_cult_robe', 'armor_cult_robe_skirt', 'shoulder_mantle_l', 'shoulder_mantle_r'],
                          r='wpn_staff_skull', l='wpn_tome', skin=(0.88, 0.85, 0.74), pal=((0.25, 0.12, 0.38), (0.15, 0.1, 0.2), (0.4, 0.9, 0.9)), scale=1.0),
    'beast': dict(sp='beast', gear=['armor_ragged', 'shoulder_fur_l', 'shoulder_fur_r', 'back_tail_beast'],
                  r='wpn_claws_r', l='wpn_claws_l', skin=(0.5, 0.4, 0.33), pal=((0.4, 0.3, 0.2), (0.25, 0.18, 0.12), (0.9, 0.8, 0.5)), scale=1.0),
    'demon_caster': dict(sp='demon', gear=['helm_demon' if False else 'hat_none', 'armor_robe', 'armor_robe_skirt', 'shoulder_flame_l', 'shoulder_flame_r', 'back_wings_bat', 'back_tail_demon'],
                         r='wpn_staff_fire', l=None, skin=(0.72, 0.2, 0.16), pal=((0.2, 0.15, 0.18), (0.4, 0.1, 0.1), (1.0, 0.55, 0.1)), scale=1.0),
}


def to_bl(p):
    return (p[0], -p[2], p[1])


def assembled():
    clean_scene()
    bodies_o = import_glb(os.path.join(KIT, 'kit_bodies.glb'))
    gear_o = import_glb(os.path.join(KIT, 'kit_gear.glb'))
    wp = os.path.join(KIT, 'kit_weapons.glb')
    weap_o = import_glb(wp) if os.path.exists(wp) else {}
    allo = {**bodies_o, **gear_o}
    cam = pl.setup_scene(520, 760)
    parts = ["torso", "pelvis", "head", "arm_l", "arm_r", "leg_l", "leg_r"]
    for name, c in CHARS.items():
        show = {f'body_{c["sp"]}_{p}' for p in parts} | set(c['gear'])
        mat = pl.test_material(c['pal'][0], c['pal'][1], c['pal'][2], c['skin'], name='M_' + name)
        for o in allo.values():
            o.hide_render = True
        shown = [allo[n] for n in show if n in allo]
        for o in shown:
            o.hide_render = False
        for o in weap_o.values():
            o.hide_render = True
        wobjs = []
        for side in ('r', 'l'):
            w = c.get(side)
            if w and w in weap_o:
                o = weap_o[w]
                o.hide_render = False
                o.location = to_bl(HAND[side])
                wobjs.append(o)
        objs_all = shown + wobjs
        pl.set_material(objs_all, mat)
        # échelle de jeu via parent vide
        em = bpy.data.objects.new('root', None)
        bpy.context.scene.collection.objects.link(em)
        em.scale = (c['scale'],) * 3
        saved = []
        for o in objs_all:
            saved.append((o, o.parent))
            o.parent = em
        sc = c['scale']
        imgs = []
        for i, (az, el, tgt, dist, lens) in enumerate([(-28, 12, (0, 0, 0.9 * sc), 5.6 * sc ** 0.5, 70), (150, 18, (0, 0, 0.9 * sc), 5.6 * sc ** 0.5, 70),
                                                         (-30, 55, (0, 0, 0.8 * sc), 6.0 * sc ** 0.5, 70)]):
            p = os.path.join(TMP, f'a_{name}_{i}.png')
            render_tile(cam, p, tgt, az, el, dist, lens, 520, 760)
            imgs.append(p)
        for o, par in saved:
            o.parent = None
        bpy.data.objects.remove(em)
        for o in wobjs:
            o.location = (0, 0, 0)
        sheet(imgs, ['face 3/4', 'dos 3/4', 'vue jeu 55°'], 3, os.path.join(PRE, f'assembled_{name}.png'), tile=(380, 555), title=name)
        print('sheet', name)


if what in ('bodies', 'all'):
    bodies()
if what in ('gear', 'all'):
    gear_sheets()
if what in ('assembled', 'all'):
    assembled()
with open(os.path.join(TMP, 'jobs_%s.json' % what), 'w') as f:
    json.dump(JOBS, f)
