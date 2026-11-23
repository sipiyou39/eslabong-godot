#!/bin/bash
# Reconstruit tout le DLC grec : kit (GLB + parts.json) -> textures -> arènes -> aperçus -> thèmes.
# usage : build_all.sh [kit] [arenas] [previews]   (sans argument : tout)
D="$(cd "$(dirname "$0")" && pwd)"
B=/Applications/Blender.app/Contents/MacOS/Blender
PY="$D/../.venv/bin/python"
W=${@:-kit arenas previews}
if [[ " $W " == *" kit "* ]]; then
  $B -b --python $D/build_kit_greek.py 2>&1 | grep -E "OVER|EXPORTED|Error|Traceback"
fi
if [[ " $W " == *" arenas "* ]]; then
  for n in olympus underworld atlantis; do
    (cd $D/arena && $PY tex_$n.py)
    $B -b --python $D/arena/build_$n.py 2>&1 | grep -E "^\[export\]|Traceback|Error:"
  done
  $PY $D/make_themes.py
fi
if [[ " $W " == *" previews "* ]]; then
  $D/run_preview.sh all
  for n in olympus underworld atlantis; do
    $D/arena/make.sh $n norebuild game
    cp /private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/greek/ar/${n}_game.png $D/../../assets/models/arenas/preview/$n.png
  done
fi
