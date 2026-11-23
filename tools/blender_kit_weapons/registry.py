"""Registre des modèles : chaque module de dessin enregistre ses fonctions via @weapon / @prop."""
REG = []


def _reg(kind, name, accent, notes, pair, ao, views, scale=None):
    def deco(fn):
        REG.append(dict(kind=kind, name=name, fn=fn, accent=accent, notes=notes, pair=pair, ao=ao, views=views, scale=scale))
        return fn
    return deco


def weapon(name, accent=None, notes="", pair=False, ao=0.10, views="side,tq", scale=None):
    return _reg("weapon", name, accent, notes, pair, ao, views, scale)


def prop(name, accent=None, notes="", ao=0.18, views="tq,side", scale=None):
    return _reg("prop", name, accent, notes, False, ao, views, scale)
