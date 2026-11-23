#!/bin/bash
# Reconstruit tout : textures (venv) -> GLB (Blender) -> aperçus PNG -> manifeste.
# usage : build_all.sh [textures] [glb] [preview]   (sans argument : tout)
D=/path/to/elsasko/tools/blender_arenas
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=/path/to/elsasko/tools/.venv/bin/python
O=/path/to/elsasko/assets/models/arenas
W=${@:-textures glb preview}
if [[ " $W " == *" textures "* ]]; then
  for t in colosseum frost forge irongate thunder club; do $PY $D/tex_$t.py; done
fi
if [[ " $W " == *" glb "* ]]; then
  for n in colosseum frost forge irongate thunder club; do $B -b --python $D/build_$n.py 2>&1 | grep -E "^\[export\]|Traceback|Error:"; done
fi
if [[ " $W " == *" preview "* ]]; then
  mkdir -p $O/preview
  for n in colosseum frost forge irongate thunder; do
    $B -b --python $D/render.py -- $O/arena_$n.glb $O/preview/arena_$n.png $n game 1280x720 2>&1 | grep -E "Traceback"
    $B -b --python $D/render.py -- $O/arena_$n.glb $O/preview/arena_${n}_iso.png $n iso 1280x720 2>&1 | grep -E "Traceback"
  done
  $B -b --python $D/render.py -- $O/club_hall.glb $O/preview/club_hall.png club hall 1280x720 2>&1 | grep -E "Traceback"
  $B -b --python $D/render.py -- $O/club_hall.glb $O/preview/club_hall_fireplace.png club fire 1280x720 2>&1 | grep -E "Traceback"
  $B -b --python $D/render.py -- $O/club_hall.glb $O/preview/club_hall_cote.png club hall2 1280x720 2>&1 | grep -E "Traceback"
fi
$PY $D/make_manifest.py
