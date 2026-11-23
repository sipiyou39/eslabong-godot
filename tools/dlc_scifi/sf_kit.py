"""Registre du kit sci-fi : groupes -> fonctions renvoyant Part ou [Part]."""
import importlib

GROUPS = {}
_MODS = [('species', 'sf_species', 'SPECIES_FN'), ('hats', 'sf_hats', 'HATS'), ('torso', 'sf_torso', 'TORSO'), ('skirts', 'sf_torso', 'SKIRTS'),
         ('shoulders', 'sf_shoulders', 'SHOULDERS'), ('backs', 'sf_backs', 'BACKS'), ('weapons', 'sf_weapons', 'WEAPONS'), ('summons', 'sf_summons', 'SUMMONS')]
for g, mod, attr in _MODS:
    try:
        m = importlib.import_module(mod)
    except ImportError as e:
        if mod in str(e):
            continue
        raise
    if hasattr(m, attr):
        GROUPS[g] = getattr(m, attr)
    elif g == 'species' and hasattr(m, 'SPECIES'):
        GROUPS[g] = list(m.SPECIES.values())
SPECIES_ORDER = ['robot', 'alien']
