"""Registre des espèces : chaque entrée renvoie un dict {part: Part}."""
from bodies_common import *
import math
from gear_common import tufts, spike
import humanoid, heads


def human():
    return humanoid.build('human', {}, heads.head_human)


def orc():
    P = dict(tw=1.14, td=1.08, aw=1.22, fs=1.2, lw=1.15, foot=1.12, ms=1.0, neck=1.3)
    return humanoid.build('orc', P, heads.head_orc)


def goblin():
    P = dict(tw=0.82, td=0.85, aw=0.62, fs=0.85, lw=0.7, foot=0.9, ms=0.3, neck=0.8, leg='goblin')
    return humanoid.build('goblin', P, heads.head_goblin)


def fur_torso(tw=1.0, td=1.0, rows=((0.9, 5), (0.97, 5), (1.04, 5), (1.1, 3))):
    def f(t):
        pts = []
        for y, n in rows:
            for i in range(n):
                x = (i - (n - 1) / 2) * 0.05 * tw
                z = 0.17 * td * math.sqrt(max(0.05, 1 - (x / (0.27 * tw)) ** 2)) + 0.02
                pts.append((x, y, z))
        t.add(tufts(pts, (0, -0.8, 0.7), length=0.075, r=0.03, seed=2, jitter=0.3), SKIN, angle=60)
        back = [(0, 1.1 - 0.07 * k, -0.17 - 0.01 * k) for k in range(6)]
        t.add(tufts(back, (0, 0.5, -1.0), length=0.09, r=0.034, seed=5, jitter=0.2), SKIN, angle=60)
    return f


def fur_arm(a):
    pts = [(0.325 + 0.02 * math.cos(k * 1.05), 0.84 - 0.05 * (k % 3), 0.02 * math.sin(k * 1.05) + 0.0) for k in range(6)]
    pts = [(0.328 + 0.085 * math.cos(k * 1.047), 0.84 - 0.04 * (k % 3), 0.085 * math.sin(k * 1.047)) for k in range(6)]
    a.add(tufts(pts, (0.2, -1, 0.0), length=0.08, r=0.03, seed=7, jitter=0.25), SKIN, angle=60)


def fur_leg(lg):
    x0 = 0.13
    pts = [(x0 + 0.09 * math.cos(k * 1.047), 0.30 - 0.04 * (k % 2), 0.09 * math.sin(k * 1.047)) for k in range(6)]
    lg.add(tufts(pts, (0, -1, 0.15), length=0.09, r=0.034, seed=9, jitter=0.2), SKIN, angle=60)


def minotaur():
    P = dict(tw=1.15, td=1.1, aw=1.28, fs=1.25, lw=1.18, ms=1.6, leg='hoof', neck=1.6, hump=0.02)
    return humanoid.build('minotaur', P, heads.head_minotaur, torso_extra=fur_torso(1.15, 1.1), arm_extra=fur_arm, leg_extra=fur_leg)


def demon():
    P = dict(tw=1.04, aw=1.08, lw=1.0, ms=1.3, pants_on=False, bracers=False, hand='claw', pelvis_col=R)
    return humanoid.build('demon', P, heads.head_demon, digi='hoof')


def beast():
    P = dict(tw=1.05, td=1.12, aw=1.15, lw=1.05, ms=1.3, pants_on=False, bracers=False, hand='claw', hump=0.025, fs=1.15, pelvis_col=R)
    return humanoid.build('beast', P, heads.head_beast, digi='paw', torso_extra=fur_torso(1.05, 1.12), arm_extra=fur_arm)


REGISTRY = {'human': human, 'orc': orc, 'goblin': goblin, 'minotaur': minotaur, 'demon': demon, 'beast': beast}
try:
    import sp_skeleton
    REGISTRY['skeleton'] = sp_skeleton.build
except ImportError:
    pass
ORDER = ["human", "orc", "goblin", "minotaur", "skeleton", "beast", "demon"]
