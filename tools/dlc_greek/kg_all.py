"""Registre des pièces d'équipement grecques."""
GROUPS = {}
try:
    from kg_heads import HEADS
    GROUPS['heads'] = HEADS
except ImportError as e:
    print('kg_heads:', e)
try:
    from kg_torso import TORSO, SKIRTS
    GROUPS['torso'] = TORSO
    GROUPS['skirts'] = SKIRTS
except ImportError as e:
    print('kg_torso:', e)
try:
    from kg_shoulders import SHOULDERS
    GROUPS['shoulders'] = SHOULDERS
except ImportError as e:
    print('kg_shoulders:', e)
try:
    from kg_backs import BACKS
    GROUPS['backs'] = BACKS
except ImportError as e:
    print('kg_backs:', e)
