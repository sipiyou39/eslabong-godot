#!/bin/bash
# Reconstruit les 4 arènes de base (volcano glacier sky jungle) : textures (venv) -> GLB (Blender) -> aperçus 960x540 -> contrôle de contrat.
# usage : build_all.sh [textures] [glb] [preview] [check]   (sans argument : tout)
D="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$D/../.." && pwd)"
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=$ROOT/tools/.venv/bin/python
IDS="volcano glacier sky jungle"
W=${@:-textures glb preview check}
if [[ " $W " == *" textures "* ]]; then
  for t in $IDS; do $PY $D/tex_$t.py | tail -1; done
fi
if [[ " $W " == *" glb "* ]]; then
  for n in $IDS; do $B -b --python $D/build_$n.py 2>&1 | grep -E "^\[export\]|Traceback|Error:"; done
fi
if [[ " $W " == *" preview "* ]]; then
  for n in $IDS; do $D/preview.sh $n; done
fi
if [[ " $W " == *" check "* ]]; then
  $PY $D/check_glb.py $IDS
fi
