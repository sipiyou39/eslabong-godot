"""Paramètres d'éclairage des rendus de contrôle (EEVEE) des arènes grecques."""
THEMES = {
    'olympus': dict(
        post=dict(c=(0.95, 0.8, 0.6), top=0.22, glob=0.0, gamma=1.6),
        sky=(0.42, 0.55, 0.9), sky_str=1.0, exposure=-0.35,
        suns=[dict(dir=(0.45, -0.5, -0.6), c=(1.0, 0.86, 0.62), e=4.8, ang=3),
              dict(dir=(-0.4, -0.3, 0.8), c=(0.6, 0.7, 1.0), e=0.8, ang=20)],
        torch=dict(c=(1.0, 0.75, 0.35), e=260),
        points=[dict(p=(0, 5, -20), c=(1.0, 0.8, 0.45), e=3000, r=3.0), dict(p=(0, 6.5, -31), c=(1.0, 0.82, 0.5), e=6000, r=3.0)],
    ),
    'underworld': dict(
        post=dict(c=(0.22, 0.07, 0.06), top=0.45, glob=0.03, gamma=1.2),
        sky=(0.10, 0.06, 0.08), sky_str=1.0, exposure=0.6,
        suns=[dict(dir=(0.3, -0.7, -0.4), c=(0.5, 0.9, 0.75), e=1.2, ang=8),
              dict(dir=(-0.5, -0.3, 0.7), c=(1.0, 0.4, 0.2), e=0.7, ang=25)],
        torch=dict(c=(0.35, 1.0, 0.7), e=330),
    ),
    'atlantis': dict(
        post=dict(c=(0.07, 0.42, 0.52), top=0.6, glob=0.16, gamma=1.1),
        sky=(0.06, 0.28, 0.38), sky_str=1.0, exposure=0.35,
        suns=[dict(dir=(0.25, -0.9, -0.2), c=(0.7, 1.0, 0.95), e=2.8, ang=6),
              dict(dir=(-0.5, -0.3, 0.7), c=(0.4, 0.8, 1.0), e=0.8, ang=25)],
        torch=dict(c=(0.5, 1.0, 0.9), e=280),
    ),
}
