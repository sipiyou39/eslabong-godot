"""Constructeur de corps humanoïdes paramétrique (torse, bassin, bras, jambes) ; les têtes sont fournies par espèce."""
from bodies_common import *

DEFAULT_P = dict(
    tw=1.0, td=1.0,            # carrure du torse (x, z)
    aw=1.0, fs=1.0,            # rayon des bras, taille des poings
    lw=1.0, foot=1.0,          # rayon des jambes, taille des pieds
    ms=1.0,                    # intensité du modelé musculaire
    pants=R, boots=G, bracer=G, belt=G,
    leg='boot',                # boot | hoof | digi_hoof | digi_paw | goblin
    hand='fist',               # fist | claw
    bracers=True, belt_on=True, pants_on=True,
    neck=1.0, belly=0.0, hump=0.0,
)


def lerp_rows(keys, y):
    keys = sorted(keys, key=lambda k: k[0])
    ys = [k[0] for k in keys]
    return [float(np.interp(y, ys, [k[i] for k in keys])) for i in range(1, len(keys[0]))]


def arm_rows(keys, ys):
    out = []
    for y in ys:
        rx, rz, cx, cz = lerp_rows(keys, y)
        out.append((y, rx, rz, cx, cz))
    return out


def make_torso(nm, P, extra=None):
    t = Part(nm("torso"), PV["torso"])
    tw, td = P['tw'], P['td']
    bl = P['belly']
    rows = [(0.72, 0.17 * tw, 0.12 * td, 0.0), (0.80, 0.18 * tw, 0.13 * td, 0.0 + bl * 0.5), (0.90, 0.215 * tw, 0.155 * td, 0.005 + bl),
            (1.00, 0.26 * tw, 0.17 * td, 0.012 + bl * 0.3), (1.07, 0.275 * tw, 0.172 * td, 0.012),
            (1.13, 0.245 * tw, 0.15 * td, 0.0 - P['hump'] * 0.5), (1.17, 0.125 * tw * P['neck'], 0.10 * td, -0.005 - P['hump']),
            (1.19, 0.08 * tw, 0.07 * td, -0.005 - P['hump'])]
    tg = rows_loft(rows, n=30, e=2.3, k=22)
    m = P['ms']
    zf = 0.16 * td + 0.005
    for sx in (-1, 1):
        stamp(tg, (sx * 0.1 * tw, 1.05, zf), (0.075 * tw, 0.05, 0.05), 0.04 * m)
    stamp(tg, (0.0, 0.97, zf + 0.01), (0.012, 0.16, 0.05), -0.012 * m)
    for yy in (0.93, 0.86):
        stamp(tg, (0.05 * tw, yy, zf + 0.0), (0.04, 0.026, 0.05), 0.02 * m, mirror=True)
    stamp(tg, (0.0, 1.145, -0.05 - P['hump']), (0.15 * tw, 0.05, 0.08), 0.02 * m + P['hump'] * 0.4)
    stamp(tg, (0.1 * tw, 1.0, -0.14 * td), (0.07, 0.1, 0.05), 0.012 * m, mirror=True)
    stamp(tg, (0.0, 0.95, -0.15 * td), (0.012, 0.2, 0.05), -0.01 * m)
    t.add(tg, SKIN, angle=None)
    if extra:
        extra(t)
    return t


def make_pelvis(nm, P, extra=None):
    p = Part(nm("pelvis"), PV["pelvis"])
    tw, td = P['tw'] * 0.96, P['td']
    rows = [(0.60, 0.15 * tw, 0.115 * td, 0.0), (0.66, 0.20 * tw, 0.145 * td, 0.005), (0.74, 0.215 * tw, 0.152 * td, 0.005),
            (0.82, 0.20 * tw, 0.146 * td, 0.005), (0.86, 0.14 * tw, 0.11 * td, 0.0)]
    p.add(rows_loft(rows, n=20, e=2.3), P.get('pelvis_col') or (P['pants'] if P['pants_on'] else SKIN), sub=1, angle=60)
    if P['belt_on']:
        belt = rows_loft([(0.775, 0.222 * tw, 0.159 * td, 0.006), (0.835, 0.216 * tw, 0.154 * td, 0.006)], n=24, e=2.3, cap0='ngon', cap1='ngon')
        p.add(belt, P['belt'], angle=60)
        p.add(rbox(0.04, 0.034, 0.015, r=0.012).t(0, 0.805, 0.167 * td), B)
        p.add([rbox(0.022, 0.04, 0.014, r=0.01).t(sx * 0.13 * tw, 0.79, 0.145 * td).ry(sx * -25, about=(sx * 0.13 * tw, 0.79, 0.145 * td))
               for sx in (-1, 1)], P['belt'])
    if extra:
        extra(p)
    return p


def make_arm(nm, P, extra=None):
    a = Part(nm("arm_l"), PV["arm_l"])
    k = P['aw']
    keys = [(1.19, 0.04 * k, 0.04 * k, 0.29, 0.0), (1.17, 0.07 * k, 0.07 * k, 0.295, 0.0), (1.16, 0.085 * k, 0.085 * k, 0.30, 0.0),
            (1.10, 0.098 * k, 0.098 * k, 0.305, 0.0), (1.02, 0.088 * k, 0.088 * k, 0.31, 0.0),
            (0.93, 0.075 * k, 0.075 * k, 0.315, -0.005), (0.87, 0.07 * k, 0.07 * k, 0.32, -0.008), (0.80, 0.078 * k, 0.078 * k, 0.328, 0.005),
            (0.72, 0.063 * k, 0.063 * k, 0.336, 0.015), (0.67, 0.055 * k, 0.055 * k, 0.34, 0.02)]
    ys = [1.19, 1.17, 1.15, 1.12, 1.07, 1.00, 0.93, 0.87, 0.80, 0.74, 0.69, 0.665]
    ag = limb(arm_rows(keys, ys), n=16)
    m = P['ms']
    stamp(ag, (0.325, 0.99, 0.045), (0.05, 0.07, 0.05), 0.014 * m)       # biceps
    stamp(ag, (0.30, 0.93, -0.06), (0.05, 0.07, 0.05), 0.012 * m)        # triceps
    a.add(ag, SKIN, sub=1, angle=60)
    if P['bracers']:
        bys = [0.81, 0.79, 0.75, 0.71, 0.675]
        br = arm_rows(keys, bys)
        br = [(y, rx + 0.014, rz + 0.014, cx, cz) for y, rx, rz, cx, cz in br]
        a.add(limb(br, n=16, cap0='ngon', cap1='ngon'), P['bracer'], angle=60)
    f = P['fs']
    a.add(fist((0.34, 0.612, 0.025), hx=0.058 * f, hy=0.06 * f, hz=0.058 * f, side=1), SKIN, angle=55)
    if P['hand'] == 'claw':
        cl = []
        for dy in (-0.68, -0.23, 0.23, 0.68):
            cl.append(spike((0.34, 0.612 + dy * 0.06 * f, 0.025 + 0.058 * f * 0.9), (0.34, 0.612 + dy * 0.06 * f - 0.012, 0.025 + 0.058 * f * 0.9 + 0.075 * f),
                            r=0.013 * f, n=6, bulge=0.7))
        a.add(cl, G if False else SKIN, angle=60)
    if extra:
        extra(a)
    return a


def make_leg(nm, P, extra=None):
    lg = Part(nm("leg_l"), PV["leg_l"])
    x0 = 0.13
    k = P['lw']
    st = P['leg']
    pc = P['pants'] if P['pants_on'] else SKIN
    if st in ('boot', 'goblin', 'hoof'):
        pk = [(0.77, 0.105 * k, 0.11 * k, x0, 0.0), (0.66, 0.10 * k, 0.105 * k, x0, 0.0), (0.52, 0.086 * k, 0.09 * k, x0, 0.0),
              (0.44, 0.078 * k, 0.082 * k, x0, 0.0), (0.36, 0.076 * k, 0.078 * k, x0, -0.004), (0.28, 0.072 * k, 0.072 * k, x0, 0.0)]
        lgm = limb([(y,) + tuple(lerp_rows(pk, y)) for y in (0.77, 0.72, 0.66, 0.59, 0.52, 0.44, 0.36, 0.28)], n=16)
        stamp(lgm, (x0, 0.58, 0.07), (0.05, 0.09, 0.05), 0.012 * P['ms'])
        lg.add(lgm, pc, sub=1, angle=60)
    if st in ('boot', 'goblin'):
        fk = P['foot']
        kk = max(k, 0.9)
        shaft = limb([(0.10, 0.08 * kk, 0.08 * kk, x0, 0.0), (0.22, 0.085 * kk, 0.085 * kk, x0, 0.0), (0.31, 0.09 * kk, 0.09 * kk, x0, 0.0),
                      (0.335, 0.095 * kk, 0.095 * kk, x0, 0.0)], n=16, cap0='ngon', cap1='ngon')
        lg.add(shaft, P['boots'], sub=1, angle=60)
        cuff = limb([(0.29, 0.098 * kk, 0.098 * kk, x0, 0.0), (0.34, 0.108 * kk, 0.108 * kk, x0, 0.0), (0.375, 0.104 * kk, 0.104 * kk, x0, 0.0)],
                    n=16, cap0='ngon', cap1='ngon')
        lg.add(cuff, P['boots'], angle=60)
        fw = fk
        pt = 1.25 if st == 'goblin' else 1.0
        foot = zloft([(-0.085, 0.045 * fw, 0.04, 0.062, x0), (-0.055, 0.076 * fw, 0.07, 0.07, x0), (0.0, 0.088 * fw, 0.08, 0.077, x0),
                      (0.08, 0.09 * fw, 0.062, 0.062, x0), (0.16 * pt, 0.084 * fw, 0.05, 0.052, x0), (0.215 * pt, 0.058 * fw, 0.037, 0.042, x0),
                      (0.245 * pt, 0.0, 0, 0.038, x0)], n=16, e=2.4)
        lg.add(foot, P['boots'], sub=1, angle=60)
        sole = zloft([(-0.092, 0.05 * fw, 0.021, 0.021, x0), (-0.04, 0.082 * fw, 0.021, 0.021, x0), (0.1, 0.095 * fw, 0.021, 0.021, x0),
                      (0.2 * pt, 0.075 * fw, 0.021, 0.021, x0), (0.252 * pt, 0.04 * fw, 0.021, 0.021, x0)], n=16, e=3.0)
        lg.add(sole, P['boots'], angle=60)
        lg.add(rbox(0.012, 0.03, 0.012, r=0.006).t(x0 + 0.092 * kk, 0.22, 0.02), B)
    elif st == 'hoof':
        # jambe velue droite + sabot fendu
        fur = limb([(0.30, 0.074 * k, 0.074 * k, x0, 0.0), (0.22, 0.068 * k, 0.07 * k, x0, 0.0), (0.12, 0.066 * k, 0.068 * k, x0, 0.0),
                    (0.075, 0.07 * k, 0.074 * k, x0, 0.005)], n=14, cap0='fan', cap1='ngon')
        lg.add(fur, SKIN, sub=1, angle=60)
        lg.add(hoof_geo(x0, k), P['boots'] if False else SKIN, angle=55)
    if extra:
        extra(lg)
    return lg


def hoof_geo(x0, k=1.0, z0=0.03):
    out = []
    for sx in (-1, 1):
        h = lathe([(0.045 * k, 0.0), (0.05 * k, 0.012), (0.044 * k, 0.07), (0.028 * k, 0.088), (0.0, 0.092)], n=12, rz=1.7).t(x0 + sx * 0.032 * k, 0.0, z0 + 0.03)
        out.append(h)
    return merge(out)


def digi_leg(nm, P, paw=False, extra=None, fur=False):
    """jambe digitigrade (demon / bête) : cuisse -> genou -> jarret -> métatarse -> sabot ou patte."""
    lg = Part(nm("leg_l"), PV["leg_l"])
    x0 = 0.13
    k = P['lw']
    path = curve([(x0, 0.78, -0.01), (x0, 0.62, 0.035), (x0, 0.47, 0.065), (x0, 0.34, 0.01), (x0, 0.245, -0.07), (x0, 0.14, -0.035), (x0, 0.075, 0.03)], 3)
    # rayons le long du chemin (interpolés sur l'indice)
    keys = [0.108, 0.1, 0.082, 0.068, 0.058, 0.048, 0.05]
    kx = np.linspace(0, len(keys) - 1, len(path))
    rr = np.interp(kx, range(len(keys)), keys) * k
    rad = [(r * 1.05, r) for r in rr]
    g = tube(path, rad, n=16, cap0='ngon', cap1='ngon', up=(0, 0, 1.0))
    stamp(g, (x0, 0.6, 0.1), (0.06, 0.09, 0.05), 0.012 * P['ms'])
    lg.add(g, P['pants'] if (P['pants_on']) else SKIN, sub=0, angle=60)
    if paw:
        foot = zloft([(-0.04, 0.05, 0.04, 0.05, x0), (0.0, 0.065, 0.05, 0.06, x0), (0.07, 0.07, 0.04, 0.045, x0), (0.14, 0.07, 0.032, 0.035, x0),
                      (0.19, 0.05, 0.026, 0.03, x0), (0.215, 0.0, 0, 0.028, x0)], n=14, e=2.2)
        lg.add(foot, SKIN, sub=1, angle=60)
        cl = []
        for sx in (-1, 0, 1):
            cl.append(spike((x0 + sx * 0.032, 0.03, 0.195), (x0 + sx * 0.036, 0.012, 0.265), r=0.014, n=6, bulge=0.8))
        lg.add(cl, SKIN, angle=60)
        lg.add(sphere(0.02, 0.016, 0.03, n=8, m=5).t(x0, 0.075, -0.09), SKIN)
    else:
        lg.add(hoof_geo(x0, 1.15 * k, z0=0.015), SKIN, angle=55)
    if extra:
        extra(lg)
    return lg


def build(species, P=None, head_fn=None, torso_extra=None, pelvis_extra=None, arm_extra=None, leg_extra=None, digi=None):
    Q = dict(DEFAULT_P)
    if P:
        Q.update(P)
    nm = lambda p: f"body_{species}_{p}"
    parts = {}
    parts["torso"] = make_torso(nm, Q, torso_extra)
    parts["pelvis"] = make_pelvis(nm, Q, pelvis_extra)
    parts["head"] = head_fn(nm("head"), Q)
    a = make_arm(nm, Q, arm_extra)
    parts["arm_l"] = a
    parts["arm_r"] = a.mirrored(nm("arm_r"), PV["arm_r"])
    if digi:
        lg = digi_leg(nm, Q, paw=(digi == 'paw'), extra=leg_extra)
    else:
        lg = make_leg(nm, Q, leg_extra)
    parts["leg_l"] = lg
    parts["leg_r"] = lg.mirrored(nm("leg_r"), PV["leg_r"])
    return parts
