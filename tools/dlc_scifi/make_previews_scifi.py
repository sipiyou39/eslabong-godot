"""Planches contact du kit sci-fi à partir du GLB exporté (valide COLOR_0 + noms) : matériau test à masque.
   Blender -b --python make_previews_scifi.py -- [bodies|gear|weapons|assembled|all]   puis  ../.venv/bin/python make_previews_scifi.py compose"""
import sys, os, json, math
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
ROOT = os.path.abspath(os.path.join(here, '..', '..'))
KIT = os.path.join(ROOT, 'assets', 'models', 'kit')
PRE = os.path.join(KIT, 'preview_scifi')
TMP = os.environ.get('SF_TMP', os.path.join(PRE, '_tmp'))

if __name__ == '__main__' and 'compose' in sys.argv and 'bpy' not in sys.modules:
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'blender_kit_bodies'))
    import compose
    for jf in sorted(os.listdir(TMP)):
        if jf.startswith('jobs_') and jf.endswith('.json'):
            for job in json.load(open(os.path.join(TMP, jf))):
                job['path'] = os.path.join(PRE, os.path.basename(job['path']))
                compose.sheet(job)
                print('sheet', job['path'])
    sys.exit(0)

sys.path.insert(0, os.path.join(ROOT, 'tools', 'blender_kit_bodies'))
import bpy
import numpy as np
import preview_lib as pl

os.makedirs(TMP, exist_ok=True)
os.makedirs(PRE, exist_ok=True)
what = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'all'
parts_info = json.load(open(os.path.join(ROOT, 'data', 'dlc', 'kit_scifi_parts.json')))
NAMES = parts_info['parts']
JOBS = []


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    out = {}
    for o in [o for o in bpy.data.objects if o not in before]:
        if o.type == 'MESH':
            out[o.name.split('.')[0]] = o
        else:
            o.hide_render = True
    return out


def clean():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def show_only(objs, names):
    for n, o in objs.items():
        o.hide_render = n not in names
        o.hide_viewport = n not in names


def sheet(images, labels, cols, path, tile, title):
    JOBS.append(dict(images=images, labels=labels, cols=cols, path=path, tile=tile, title=title))


def render_tile(cam, path, target, az, el, dist, lens, w=760, h=1040):
    bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = w, h
    pl.aim_camera(cam, target, az, el, dist)
    cam.data.lens = lens
    pl.render(path)


def load_all():
    clean()
    b = import_glb(os.path.join(KIT, 'kit_bodies.glb'))
    g = import_glb(os.path.join(KIT, 'kit_gear.glb'))
    s = import_glb(os.path.join(KIT, 'kit_scifi.glb'))
    mat = pl.test_material()
    pl.set_material(list(b.values()) + list(g.values()) + list(s.values()), mat)
    return b, g, s, mat


PARTS7 = ["torso", "pelvis", "head", "arm_l", "arm_r", "leg_l", "leg_r"]
HUMAN = {f'body_human_{p}' for p in PARTS7}


def bodies():
    b, g, s, mat = load_all()
    allo = {**b, **g, **s}
    cam = pl.setup_scene(760, 1040)
    for sp in ('robot', 'alien'):
        names = {f'body_{sp}_{p}' for p in PARTS7}
        show_only(allo, names)
        imgs = []
        for i, (az, el, tgt, dist, lens) in enumerate([(-28, 12, (0, 0, 0.9), 5.2, 70), (150, 18, (0, 0, 0.9), 5.2, 70), (-22, 8, (0, 0, 1.45), 5.0, 200)]):
            p = os.path.join(TMP, f'b_{sp}_{i}.png')
            render_tile(cam, p, tgt, az, el, dist, lens)
            imgs.append(p)
        sheet(imgs, ['face 3/4', 'dos 3/4', 'tête'], 3, os.path.join(PRE, f'bodies_{sp}.png'), (380, 520), f'body_{sp}_*')


GEAR_VIEWS = {
    'hats': [(-32, 12, (0, 0, 1.5), 2.9, 85), (35, 12, (0, 0, 1.5), 2.9, 85), (150, 14, (0, 0, 1.5), 2.9, 85)],
    'torso': [(-32, 14, (0, 0, 0.95), 3.0, 85), (150, 16, (0, 0, 0.95), 3.0, 85)],
    'skirts': [(-32, 10, (0, 0, 0.62), 3.1, 85), (150, 10, (0, 0, 0.62), 3.1, 85)],
    'shoulders': [(-25, 25, (0, 0, 1.22), 2.7, 85), (150, 20, (0, 0, 1.22), 2.7, 85)],
    'backs': [(180, 10, (0, 0, 1.05), 4.4, 80), (125, 12, (0, 0, 1.05), 4.4, 80)],
}


def gear_sheets():
    b, g, s, mat = load_all()
    allo = {**b, **g, **s}
    cam = pl.setup_scene(480, 820)
    groups = {
        'hats': [n for n in NAMES if n.startswith(('helm_', 'hat_', 'hair_'))],
        'torso': [n for n in NAMES if n.startswith('armor_') and not n.endswith('_skirt')],
        'skirts': [n for n in NAMES if n.endswith('_skirt')],
        'shoulders': [n for n in NAMES if n.startswith('shoulder_') and n.endswith('_l')],
        'backs': [n for n in NAMES if n.startswith('back_')],
    }
    for grp, names in groups.items():
        imgs, labels = [], []
        for nm in names:
            show = set(HUMAN)
            show.add(nm)
            if grp == 'shoulders':
                show.add(nm[:-1] + 'r')
            show_only(allo, show)
            row = []
            for vi, (az, el, tgt, dist, lens) in enumerate(GEAR_VIEWS[grp]):
                p = os.path.join(TMP, f'g_{nm}_{vi}.png')
                render_tile(cam, p, tgt, az, el, dist, lens, 480, 820)
                row.append(p)
            imgs.append(row)
            labels.append(nm.replace('shoulder_', 'sh_'))
        cols = 3 if grp in ('hats', 'shoulders') else 4
        tw = 450 if grp == 'hats' else 400
        sheet(imgs, labels, cols, os.path.join(PRE, f'gear_{grp}.png'), (tw, 340), f'équipement : {grp}')


def bbox_of(o):
    V = np.array([list(v.co) for v in o.data.vertices]) + np.array(list(o.location))
    return V.min(0), V.max(0)


def weapon_sheets():
    b, g, s, mat = load_all()
    allo = {**b, **g, **s}
    cam = pl.setup_scene(520, 520)
    names = [n for n in NAMES if n.startswith(('wpn_', 'summon_'))]
    imgs, labels = [], []
    for nm in names:
        show_only(allo, {nm})
        mn, mx = bbox_of(allo[nm])
        ctr = (mn + mx) / 2
        ext = float(np.max(mx - mn))
        row = []
        for vi, (az, el) in enumerate(((-90, 8), (-38, 22))):
            p = os.path.join(TMP, f'w_{nm}_{vi}.png')
            render_tile(cam, p, tuple(ctr), az, el, ext * 2.45 + 0.35, 70, 520, 520)
            row.append(p)
        imgs.append(row)
        labels.append(f"{nm}  {ext:.2f} m")
    sheet(imgs, labels, 3, os.path.join(PRE, 'weapons_summons.png'), (420, 210), 'armes et invocations sci-fi')


HAND = {'l': (0.34, 0.62, 0.02), 'r': (-0.34, 0.62, 0.02)}
CHARS = {
    'robot_mech': dict(sp='robot', gear=['armor_mech', 'armor_mech_skirt', 'shoulder_dome_l', 'shoulder_dome_r', 'back_reactor'],
                       r='wpn_gauntlet_r', l='wpn_gauntlet_l', skin=(0.62, 0.64, 0.68), pal=((0.78, 0.38, 0.12), (0.18, 0.2, 0.24), (0.25, 0.9, 0.95)), scale=1.0),
    'alien_psi': dict(sp='alien', gear=['armor_psi_robe', 'armor_psi_robe_skirt'],
                      r='wpn_plasma_staff', l='wpn_controller', skin=(0.58, 0.74, 0.58), pal=((0.3, 0.2, 0.52), (0.14, 0.11, 0.24), (0.4, 1.0, 0.9)), scale=1.0),
    'astronaut_blaster': dict(sp='human', gear=['helm_astronaut', 'armor_spacesuit', 'armor_spacesuit_skirt', 'back_jetpack', 'shoulder_tech_l', 'shoulder_tech_r'],
                              r='wpn_blaster', l=None, skin=(0.93, 0.76, 0.6), pal=((0.9, 0.9, 0.92), (0.8, 0.4, 0.1), (0.3, 0.75, 0.95)), scale=1.0),
    'cyborg_rifle': dict(sp='human', gear=['helm_cyborg', 'armor_exo', 'armor_exo_skirt', 'shoulder_tech_l', 'shoulder_tech_r', 'back_antenna_dish'],
                         r='wpn_rifle_plasma', l=None, skin=(0.85, 0.66, 0.52), pal=((0.55, 0.57, 0.62), (0.16, 0.17, 0.2), (0.95, 0.35, 0.2)), scale=1.0),
    'medic_drone': dict(sp='human', gear=['hair_tech', 'armor_medic', 'armor_medic_skirt', 'back_drone', 'shoulder_jet_l', 'shoulder_jet_r'],
                        r='wpn_med_gun', l='wpn_energy_shield', skin=(0.78, 0.58, 0.45), pal=((0.92, 0.93, 0.95), (0.3, 0.32, 0.36), (0.9, 0.2, 0.25)), scale=1.0),
    'pilot_blade': dict(sp='human', gear=['helm_pilot', 'armor_jacket_tech', 'armor_jacket_tech_skirt', 'shoulder_jet_l', 'shoulder_jet_r', 'back_jetpack'],
                        r='wpn_energy_blade', l=None, skin=(0.9, 0.72, 0.58), pal=((0.45, 0.3, 0.2), (0.2, 0.17, 0.15), (0.3, 0.95, 0.85)), scale=1.0),
    'robot_wrench': dict(sp='robot', gear=['armor_exo', 'helm_visor', 'shoulder_tech_l', 'shoulder_tech_r', 'back_drone'],
                         r='wpn_wrench', l='wpn_energy_shield', skin=(0.7, 0.55, 0.35), pal=((0.7, 0.2, 0.15), (0.22, 0.2, 0.2), (1.0, 0.8, 0.2)), scale=1.0),
    'alien_visor': dict(sp='alien', gear=['hat_antenna', 'armor_spacesuit', 'shoulder_dome_l', 'shoulder_dome_r'],
                        r='wpn_railgun', l=None, skin=(0.62, 0.72, 0.5), pal=((0.85, 0.5, 0.15), (0.25, 0.25, 0.3), (0.3, 0.9, 0.9)), scale=1.0),
}


def to_bl(p):
    return (p[0], -p[2], p[1])


def assembled():
    b, g, s, mat = load_all()
    allo = {**b, **g, **s}
    cam = pl.setup_scene(520, 760)
    for name, c in CHARS.items():
        show = {f'body_{c["sp"]}_{p}' for p in PARTS7} | set(c['gear'])
        m = pl.test_material(c['pal'][0], c['pal'][1], c['pal'][2], c['skin'], name='M_' + name)
        for o in allo.values():
            o.hide_render = True
            o.location = o.location
        shown = [allo[n] for n in show if n in allo]
        wob = []
        for side in ('r', 'l'):
            w = c.get(side)
            if w and w in allo:
                o = allo[w]
                o.hide_render = False
                o.location = to_bl(HAND[side])
                wob.append(o)
        for o in shown:
            o.hide_render = False
        pl.set_material(shown + wob, m)
        imgs = []
        for i, (az, el, tgt, dist, lens) in enumerate([(-28, 12, (0, 0, 0.95), 5.6, 70), (150, 18, (0, 0, 0.95), 5.6, 70), (-30, 55, (0, 0, 0.85), 6.0, 70)]):
            p = os.path.join(TMP, f'a_{name}_{i}.png')
            render_tile(cam, p, tgt, az, el, dist, lens, 520, 760)
            imgs.append(p)
        for o in wob:
            o.location = (0, 0, 0) if False else o.location
        # remettre les armes à l'origine des nœuds (positions d'export) : on les recharge si besoin
        for n in ([c.get('r'), c.get('l')]):
            if n and n in allo:
                allo[n].location = (0, 0, 0)
        sheet(imgs, ['face 3/4', 'dos 3/4', 'vue jeu 55°'], 3, os.path.join(PRE, f'assembled_{name}.png'), (380, 555), name)


if what in ('bodies', 'all'):
    bodies()
if what in ('gear', 'all'):
    gear_sheets()
if what in ('weapons', 'all'):
    weapon_sheets()
if what in ('assembled', 'all'):
    assembled()
with open(os.path.join(TMP, 'jobs_%s.json' % what), 'w') as f:
    json.dump(JOBS, f)
