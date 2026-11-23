"""Paramètres d'éclairage des rendus de contrôle (EEVEE) + palettes pour le manifeste."""
THEMES = {
    'colosseum': dict(
        sky=(0.55, 0.32, 0.30), sky_str=0.9, exposure=0.0,
        suns=[dict(dir=(0.55, -0.42, -0.72), c=(1.0, 0.62, 0.34), e=5.5, ang=3),
              dict(dir=(-0.4, -0.3, 0.8), c=(0.55, 0.6, 1.0), e=0.5, ang=20)],
        torch=dict(c=(1.0, 0.55, 0.2), e=260),
    ),
    'frost': dict(
        sky=(0.35, 0.5, 0.7), sky_str=1.1, exposure=0.0,
        suns=[dict(dir=(-0.4, -0.6, -0.6), c=(0.75, 0.85, 1.0), e=3.5, ang=4),
              dict(dir=(0.6, -0.3, 0.7), c=(0.5, 0.65, 1.0), e=0.8, ang=20)],
        torch=dict(c=(0.35, 0.65, 1.0), e=300),
    ),
    'forge': dict(
        sky=(0.22, 0.07, 0.04), sky_str=1.0, exposure=0.7,
        suns=[dict(dir=(0.3, -0.7, -0.5), c=(1.0, 0.45, 0.2), e=2.2, ang=6),
              dict(dir=(-0.5, -0.3, 0.7), c=(1.0, 0.4, 0.15), e=0.8, ang=25)],
        torch=dict(c=(1.0, 0.45, 0.12), e=350),
    ),
    'irongate': dict(
        sky=(0.4, 0.4, 0.45), sky_str=1.0, exposure=0.0,
        suns=[dict(dir=(-0.5, -0.55, -0.65), c=(1.0, 0.85, 0.65), e=4.0, ang=3),
              dict(dir=(0.5, -0.3, 0.7), c=(0.6, 0.7, 1.0), e=0.6, ang=20)],
        torch=dict(c=(1.0, 0.55, 0.2), e=250),
    ),
    'thunder': dict(
        sky=(0.10, 0.08, 0.22), sky_str=1.0, exposure=0.1,
        suns=[dict(dir=(0.2, -0.8, -0.4), c=(0.55, 0.6, 1.0), e=2.2, ang=8),
              dict(dir=(-0.6, -0.3, 0.6), c=(0.85, 0.45, 1.0), e=1.0, ang=20)],
        torch=dict(c=(0.6, 0.45, 1.0), e=350),
    ),
    'club': dict(
        views={'hall': ((0, 15, -27), (0, 3.5, 2), 55), 'hall2': ((-22, 11, -20), (0, 3, 2), 50), 'fire': ((0, 3.5, -2), (0, 3.5, 10), 60), 'top': ((0, 40, -8), (0, 0, 0), 50)},
        sky=(0.25, 0.17, 0.12), sky_str=0.8, exposure=0.2,
        suns=[dict(dir=(0.35, -0.65, 0.5), c=(1.0, 0.8, 0.55), e=4.0, ang=3),
              dict(dir=(0.0, -0.4, -0.9), c=(1.0, 0.7, 0.45), e=0.7, ang=30)],
        torch=dict(c=(1.0, 0.55, 0.22), e=500),
        light=dict(c=(1.0, 0.7, 0.4), e=250),
    ),
}

THEMES.update({
    'volcano': dict(
        sky=(0.42, 0.10, 0.03), sky_top=(0.03, 0.012, 0.012), sky_str=1.0, exposure=0.55,
        suns=[dict(dir=(0.26, -0.79, -0.56), c=(1.0, 0.55, 0.30), e=2.6, ang=6),
              dict(dir=(-0.5, -0.3, 0.7), c=(1.0, 0.4, 0.2), e=0.7, ang=25)],
        torch=dict(c=(1.0, 0.45, 0.14), e=320),
    ),
    'glacier': dict(
        sky=(0.35, 0.52, 0.62), sky_top=(0.03, 0.07, 0.22), sky_str=1.0, exposure=0.05,
        suns=[dict(dir=(-0.35, -0.55, -0.6), c=(0.85, 0.92, 1.0), e=3.6, ang=4),
              dict(dir=(0.6, -0.3, 0.7), c=(0.5, 0.65, 1.0), e=0.7, ang=20)],
        torch=dict(c=(1.0, 0.62, 0.25), e=300),
    ),
    'sky': dict(
        sky=(1.0, 0.52, 0.2), sky_top=(0.08, 0.1, 0.32), sky_str=1.0, exposure=0.15,
        suns=[dict(dir=(0.5, -0.45, -0.7), c=(1.0, 0.72, 0.42), e=4.2, ang=3),
              dict(dir=(-0.4, -0.3, 0.8), c=(0.8, 0.7, 1.0), e=0.7, ang=20)],
        torch=dict(c=(1.0, 0.65, 0.25), e=240),
    ),
    'jungle': dict(
        sky=(0.5, 0.6, 0.42), sky_top=(0.06, 0.2, 0.3), sky_str=1.0, exposure=0.0,
        suns=[dict(dir=(-0.3, -0.85, -0.45), c=(1.0, 0.92, 0.7), e=4.0, ang=3),
              dict(dir=(0.5, -0.3, 0.7), c=(0.55, 0.8, 0.6), e=0.6, ang=25)],
        torch=dict(c=(1.0, 0.6, 0.2), e=260),
    ),
})
