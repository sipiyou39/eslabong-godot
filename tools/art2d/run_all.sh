#!/bin/sh
# Regenere tous les assets ART2D (depuis tools/art2d) : sh run_all.sh
cd "$(dirname "$0")"
PY=../.venv/bin/python
$PY skin_a.py && $PY skin_b.py && $PY vfx.py && $PY uiicons.py && $PY statuses.py && $PY abilities.py && $PY classes.py && $PY relics.py && $PY heraldry.py && $PY make_previews.py
