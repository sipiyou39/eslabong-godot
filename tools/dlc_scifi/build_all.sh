#!/bin/bash
# Reconstruit tout le DLC sci-fi : textures (venv) -> kit GLB -> arènes GLB -> aperçus -> thèmes.
# usage : build_all.sh [kit] [textures] [arenas] [previews]   (sans argument : tout)
D="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$D/../.." && pwd)"
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=$ROOT/tools/.venv/bin/python
W=${@:-kit textures arenas previews}
if [[ " $W " == *" kit "* ]]; then
  $B -b --python $D/build_kit_scifi.py 2>&1 | grep -E "^\[|OVER|TOTAL|Error|Traceback"
fi
if [[ " $W " == *" textures "* ]]; then
  for t in station alien reactor; do $PY $D/tex_$t.py > /dev/null; done
fi
if [[ " $W " == *" arenas "* ]]; then
  for n in station alien reactor; do $B -b --python $D/build_$n.py 2>&1 | grep -E "^\[export\]|Traceback|Error"; done
fi
if [[ " $W " == *" previews "* ]]; then
  mkdir -p $ROOT/assets/models/arenas/preview
  for n in station alien reactor; do
    $B -b --python $D/render_sf.py -- $ROOT/assets/models/arenas/arena_$n.glb $ROOT/assets/models/arenas/preview/$n.png $n game 960x540 2>&1 | grep -E "Traceback"
  done
  $D/prev.sh all
fi
python3 $D/write_themes.py
