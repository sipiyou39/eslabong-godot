from wcommon import *
from registry import weapon

PREV_STEEL = None


@weapon("wpn_sword_long", notes="épée longue 1,05 m, lame à gorge, garde courbée")
def sword_long():
    p = []
    p.append(grip(-0.075, 0.075, 0.021))
    p.append(lathe([(0.015, -0.074), (0.03, -0.086), (0.037, -0.104), (0.031, -0.122), (0.014, -0.132), (0, -0.134)], 8, G, bevel=0.003))
    p.append(box((0.058, 0.04, 0.054), (0, 0.092, 0), color=G, bevel=0.005))
    p += quillons(0.094, 0.14, 0.04, 0.028, 0.035, tip=0.016)
    p.append(box((0.026, 0.016, 0.030), (0, 0.112, 0), color=B, bevel=0.003))     # talon
    keys = [(0.1, 0.042, 0.0145), (0.55, 0.039, 0.0115), (0.78, 0.035, 0.0105), (0.86, 0.027, 0.0085), (0.915, 0.014, 0.0055), (0.955, 0, 0)]
    p.append(blade(keys, ring_blade(e=0.2, bev=0.62, fuller=0.16)))
    return p


@weapon("wpn_sword_short", notes="épée courte / glaive 0,8 m")
def sword_short():
    p = []
    p.append(grip(-0.06, 0.06, 0.0185))
    p.append(sphere(0.03, 8, 5, G, pos=(0, -0.085, 0), s=(1, 0.95, 1), bevel=None))
    p.append(box((0.034, 0.03, 0.04), (0, 0.074, 0), color=G, bevel=0.005))
    p += quillons(0.076, 0.085, 0.032, 0.022, 0.012)
    keys = [(0.085, 0.036, 0.0135), (0.20, 0.046, 0.0125), (0.36, 0.05, 0.0115), (0.50, 0.04, 0.0095), (0.60, 0.024, 0.007), (0.655, 0.01, 0.0035), (0.69, 0, 0)]
    p.append(blade(keys, ring_blade(e=0.22, bev=0.6)))
    return p


@weapon("wpn_sword_great", notes="grande épée à deux mains 1,35 m", views="side,tq@bot")
def sword_great():
    p = []
    p.append(grip(-0.12, 0.10, 0.021, sx=1.0))
    p.append(lathe([(0.02, -0.12), (0.04, -0.13), (0.052, -0.15), (0.048, -0.172), (0.03, -0.185), (0, -0.188)], 10, G, bevel=0.004))
    p.append(gem(0.018, color=B, pos=(0, -0.158, 0.0), s=(1, 1, 1)))
    p.append(box((0.07, 0.05, 0.062), (0, 0.126, 0), color=G, bevel=0.006))
    p += quillons(0.128, 0.19, 0.046, 0.032, 0.0, droop=0.07, tip=0.02)
    for s in (1, -1):   # ergots de parade
        p.append(box((0.022, 0.07, 0.03), (s * 0.05, 0.19, 0.0), rot=(0, 0, -s * 12), color=G, bevel=0.004))
    keys = [(0.15, 0.062, 0.0185), (0.5, 0.066, 0.0165), (1.0, 0.059, 0.0140), (1.12, 0.048, 0.0120), (1.2, 0.029, 0.0085), (1.26, 0.011, 0.004), (1.29, 0, 0)]
    p.append(blade(keys, ring_blade(e=0.2, bev=0.64, fuller=0.2)))
    return p


@weapon("wpn_rapier", notes="rapière 1,1 m, garde à coquille")
def rapier():
    p = []
    p.append(grip(-0.06, 0.07, 0.0145, seg=8, pitch=0.026))
    p.append(sphere(0.026, 8, 5, B, pos=(0, -0.088, 0)))
    p.append(lathe([(0.0, 0.126), (0.03, 0.123), (0.06, 0.108), (0.074, 0.085), (0.07, 0.066), (0.058, 0.064), (0.06, 0.082), (0.05, 0.1), (0.028, 0.11), (0.0, 0.112)], 12, G, bevel=0.002))
    p.append(cyl((-0.17, 0.095, 0), (0.17, 0.095, 0), 0.008, 0.008, seg=6, color=G, bevel=0.002).xf())
    for s in (1, -1):
        p.append(sphere(0.014, 6, 4, B, pos=(s * 0.17, 0.095, 0)))
    arc_pts = arc((0, 0, 0), 1.0, 0, 1, 2)  # placeholder
    kn = bezier((0.0, 0.07, 0.05), (0.0, 0.0, 0.11), (0.0, -0.05, 0.1), (0.0, -0.075, 0.03), 12)
    p.append(tube(kn, 0.007, seg=6, color=G))
    keys = [(0.125, 0.015, 0.0085), (0.60, 0.0125, 0.0075), (0.95, 0.0085, 0.006), (1.02, 0.004, 0.003), (1.04, 0, 0)]
    p.append(blade(keys, ring_blade(e=0.25, bev=0.55, fuller=0.0)))
    p.append(cyl((0, 0.126, 0), (0, 0.15, 0), 0.016, 0.011, seg=8, color=B, bevel=0.002))
    return p


@weapon("wpn_katana", notes="katana 1,05 m, lame courbée vers -Z (dos)")
def katana():
    p = []
    p.append(grip(-0.115, 0.095, 0.0165, seg=8, pitch=0.032, sx=0.82, sz=1.0))
    p.append(lathe([(0.0175, -0.117), (0.022, -0.12), (0.022, -0.132), (0.0, -0.135)], 8, G, sx=0.85, bevel=0.002))
    p.append(lathe([(0.0175, 0.092), (0.02, 0.098), (0.02, 0.112), (0.0175, 0.116)], 8, G, sx=0.85, bevel=0.002))
    p.append(torus(0.05, 0.0065, 20, 4, plane="XZ", color=B, pos=(0, 0.124, 0.0), ry=0.044))
    p.append(lathe([(0.0, 0.118), (0.05, 0.118), (0.05, 0.13), (0.0, 0.13)], 20, G, bevel=0.002, sz=0.88))
    p.append(box((0.02, 0.03, 0.03), (0, 0.145, 0), color=B, bevel=0.003))
    L = 0.72
    y0 = 0.158
    k = [(0.0, 0.0165, 0.0085), (0.5, 0.0165, 0.0078), (0.88, 0.0155, 0.0068), (0.95, 0.011, 0.0055), (0.985, 0.0045, 0.003), (1.0, 0, 0)]
    keys = [(y0 + a * L, w, t) for a, w, t in k]
    p.append(blade(keys, ring_sabre(), bend=lambda y: -0.07 * ((y - y0) / L) ** 2, n_sub=3))
    return p


@weapon("wpn_dagger", notes="dague 0,45 m")
def dagger():
    p = []
    p.append(grip(-0.05, 0.05, 0.016, pitch=0.026))
    p.append(sphere(0.022, 8, 5, G, pos=(0, -0.068, 0)))
    p.append(box((0.07, 0.02, 0.034), (0, 0.06, 0), color=G, bevel=0.004))
    for s in (1, -1):
        p.append(sphere(0.012, 6, 4, B, pos=(s * 0.036, 0.06, 0)))
    keys = [(0.07, 0.022, 0.0105), (0.20, 0.0235, 0.0095), (0.30, 0.019, 0.0075), (0.355, 0.009, 0.004), (0.385, 0, 0)]
    p.append(blade(keys, ring_blade(e=0.2, bev=0.55)))
    return p
