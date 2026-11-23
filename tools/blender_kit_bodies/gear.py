"""Registre des pièces d'équipement."""
from gear_hats import HATS
GROUPS = {'hats': HATS}
try:
    from gear_torso import TORSO, SKIRTS
    GROUPS['torso'] = TORSO
    GROUPS['skirts'] = SKIRTS
except ImportError:
    pass
try:
    from gear_shoulders import SHOULDERS
    GROUPS['shoulders'] = SHOULDERS
except ImportError:
    pass
try:
    from gear_backs import BACKS
    GROUPS['backs'] = BACKS
except ImportError:
    pass
