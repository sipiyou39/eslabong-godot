"""Écrit assets/models/arenas/arenas_manifest.json (à lancer avec le python du venv)."""
import json
import os
import struct

OUT = "/path/to/elsasko/assets/models/arenas"

THEMES = {
    "arena_colosseum": dict(
        theme="colosseum", label="Colisée de sable doré", mode="arena", crowd=True,
        dominant_colors=["#d9ae68", "#e9d9b0", "#a3262c", "#dcab3c", "#b89a6a", "#3a2a22"],
        sky_top="#6a4a7a", sky_horizon="#ff9a5a", fog_color="#d9906a", fog_density=0.004,
        sun_color="#ffb070", sun_energy=1.4, sun_dir=[0.55, -0.42, -0.72], ambient_color="#8a5a52", ambient_energy=0.7,
        torch_color="#ff8a3a", torch_energy=2.2, glow="moderate", mood="chaud crépuscule"),
    "arena_frost": dict(
        theme="frost", label="Forteresse de glace", mode="arena", crowd=True,
        dominant_colors=["#4f93bd", "#a6d8ee", "#eef4fb", "#7f93a8", "#2f5f9e", "#52d8ff"],
        sky_top="#2a4a7a", sky_horizon="#bcd8f0", fog_color="#a9c6e0", fog_density=0.006,
        sun_color="#c4d8ff", sun_energy=1.1, sun_dir=[-0.4, -0.6, -0.6], ambient_color="#7a98c0", ambient_energy=0.9,
        torch_color="#4fb8ff", torch_energy=2.6, glow="strong (cristaux, runes, flammes bleues)", mood="froid, clair, givré"),
    "arena_forge": dict(
        theme="forge", label="Forge volcanique", mode="arena", crowd=True,
        dominant_colors=["#2a2220", "#ff6a1a", "#ffb43a", "#7a2f22", "#3a3a40", "#161212"],
        sky_top="#1a0805", sky_horizon="#7a2a10", fog_color="#4a1a0e", fog_density=0.008,
        sun_color="#ff7a3a", sun_energy=0.7, sun_dir=[0.3, -0.7, -0.5], ambient_color="#4a2218", ambient_energy=0.6,
        torch_color="#ff7a1c", torch_energy=3.0, glow="very strong (lave émissive)", mood="sombre, brûlant, enfumé"),
    "arena_irongate": dict(
        theme="irongate", label="Porte de fer (Defend the Iron Gate)", mode="arena", crowd=True,
        dominant_colors=["#85806f", "#55555c", "#2d3a52", "#5a4a38", "#b8bcc4", "#4e6a2e"],
        sky_top="#5a6070", sky_horizon="#b8b2a8", fog_color="#9a968e", fog_density=0.005,
        sun_color="#ffd9a8", sun_energy=1.2, sun_dir=[-0.5, -0.55, -0.65], ambient_color="#707484", ambient_energy=0.8,
        torch_color="#ff8a3a", torch_energy=2.4, glow="light (torches)", mood="gris, guerre, torches",
        notes="Grande porte de fer côté +X (hors terrain, x>=26), défenseurs vers +X."),
    "arena_thunder": dict(
        theme="thunder", label="Chaos Thunder", mode="arena", crowd=False,
        dominant_colors=["#211e36", "#4fd6ff", "#b46bff", "#2f2b4d", "#9fe8ff", "#0b0a14"],
        sky_top="#0a0818", sky_horizon="#3a2a66", fog_color="#241a46", fog_density=0.004,
        sun_color="#8a98ff", sun_energy=0.7, sun_dir=[0.2, -0.8, -0.4], ambient_color="#2a2250", ambient_energy=0.8,
        torch_color="#a974ff", torch_energy=3.0, glow="very strong (runes, énergie, cristaux)", mood="orage surnaturel",
        notes="Plateforme flottante : ciel d'orage + éclairs à fournir par le jeu ; îles/anneaux dans le décor."),
    "club_hall": dict(
        theme="club", label="Salle du club de mercenaires", mode="hub", crowd=False,
        dominant_colors=["#c0a077", "#a98660", "#8c1f26", "#d4a53a", "#6a4426", "#2e1d11"],
        sky_top="#2a2018", sky_horizon="#6a5a48", fog_color="#4a3a2a", fog_density=0.0,
        sun_color="#ffd9a0", sun_energy=1.3, sun_dir=[0.35, -0.65, 0.5], ambient_color="#6a5040", ambient_energy=0.8,
        torch_color="#ff8a3a", torch_energy=3.0, glow="moderate (cheminée, lustres)", mood="chaleureux, intérieur",
        notes="Centrée à l'origine, ~28x20 m (x ±14, z ±10). Côté caméra = -Z ouvert (plafond voûté coupé). Torch_01 cheminée, Torch_02..05 lustres, Torch_06..09 appliques, Torch_10 bougies de la table. Obstacle_01..06 = table, râteliers A/B, mannequins, tonneaux, coffre."),
}


def glb_info(path):
    d = open(path, 'rb').read()
    l = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20 + l])
    tris = 0
    for m in j['meshes']:
        for p in m['primitives']:
            tris += j['accessors'][p['indices']]['count'] // 3
    return dict(size_mb=round(len(d) / 1e6, 2), triangles=tris, materials=len(j['materials']), images=len(j.get('images', [])),
                nodes=sorted(n['name'] for n in j['nodes'] if 'name' in n))


man = dict(version=1, units="meters", up="+Y (glTF y-up)", terrain=dict(half_extents=[26.0, 16.0], corner_radius=5.0, wall_height=3.2),
           notes="COLOR_0 contient l'AO cuit multiplié par la teinte ; matériaux M_*; émissifs (flammes/lave/runes/cristaux) à rehausser par glow + lumières sur Torch_*/Light_*. "
                 "Torch_01..10 = positions de data/arena_layout.json, y = hauteur de flamme (2.2 m).", files={})
for name, meta in THEMES.items():
    p = os.path.join(OUT, name + ".glb")
    if not os.path.exists(p):
        continue
    info = glb_info(p)
    nodes = info.pop('nodes')
    meta = dict(meta)
    meta.update(info)
    meta['preview'] = f"preview/{name}.png"
    meta['empties'] = [n for n in nodes if n.startswith('Torch_') or n.startswith('Light_')]
    meta['banners'] = [n for n in nodes if n.startswith('Banner_')]
    man['files'][name + ".glb"] = meta
json.dump(man, open(os.path.join(OUT, "arenas_manifest.json"), 'w'), indent=2, ensure_ascii=False)
print("manifest ok", list(man['files'].keys()))
