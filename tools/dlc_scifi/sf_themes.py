"""Éclairage des rendus de contrôle (EEVEE) des arènes sci-fi + thèmes du jeu (data/dlc/theme_<id>.json, clés de Arena.THEMES)."""
THEMES = {
    'station': dict(
        sky=(0.012, 0.02, 0.05), sky_str=1.0, exposure=0.15,
        suns=[dict(dir=(0.45, -0.62, -0.55), c=(1.0, 0.85, 0.7), e=3.4, ang=3),
              dict(dir=(-0.5, -0.3, 0.75), c=(0.55, 0.75, 1.0), e=0.9, ang=20)],
        torch=dict(c=(1.0, 0.55, 0.2), e=170),
        light=dict(c=(0.5, 0.9, 1.0), e=260),
    ),
    'alien': dict(
        sky=(0.62, 0.30, 0.18), sky_str=0.95, exposure=0.1,
        suns=[dict(dir=(0.5, -0.5, -0.7), c=(1.0, 0.72, 0.45), e=4.6, ang=3),
              dict(dir=(-0.4, -0.3, 0.8), c=(0.8, 0.5, 0.5), e=0.6, ang=20)],
        torch=dict(c=(1.0, 0.6, 0.25), e=190),
        light=dict(c=(0.4, 0.95, 0.85), e=120),
    ),
    'reactor': dict(
        sky=(0.05, 0.06, 0.07), sky_str=1.0, exposure=0.35,
        suns=[dict(dir=(0.3, -0.75, -0.5), c=(1.0, 0.78, 0.55), e=2.2, ang=6),
              dict(dir=(-0.5, -0.35, 0.7), c=(0.55, 0.85, 0.95), e=0.8, ang=20)],
        torch=dict(c=(1.0, 0.5, 0.18), e=230),
        light=dict(c=(0.35, 0.9, 0.85), e=500),
    ),
}

GAME_THEMES = {
    'station': {"file": "arena_station.glb", "sun": "#ffe2c8", "sun_e": 1.35, "sun_rot": [-52, 28, 0],
                "sky_top": "#04060f", "sky_hor": "#1c2c48", "ambient": "#7080a0", "ambient_e": 0.72,
                "fog": "#18222f", "fog_d": 0.003, "torch": "#ff9a40", "ember": "#5ad8ca",
                "ground_a": "#6c7078", "ground_b": "#454850", "line": "#e8a24a", "name": "Station Orbitale"},
    'alien': {"file": "arena_alien.glb", "sun": "#ffd2a4", "sun_e": 1.55, "sun_rot": [-46, -36, 0],
              "sky_top": "#7a3a2c", "sky_hor": "#e8975c", "ambient": "#b47a5e", "ambient_e": 0.72,
              "fog": "#c8825c", "fog_d": 0.0045, "torch": "#ffb264", "ember": "#5ee2d2",
              "ground_a": "#a8563c", "ground_b": "#7a3b29", "line": "#f2c890", "name": "Planète Rouge"},
    'reactor': {"file": "arena_reactor.glb", "sun": "#ffc890", "sun_e": 1.05, "sun_rot": [-55, 14, 0],
                "sky_top": "#10151b", "sky_hor": "#2c343c", "ambient": "#7a838e", "ambient_e": 0.68,
                "fog": "#222b31", "fog_d": 0.006, "torch": "#ff9040", "ember": "#42dac8",
                "ground_a": "#5a5e62", "ground_b": "#3c4044", "line": "#ff9a3a", "name": "Cœur de Réacteur"},
}
