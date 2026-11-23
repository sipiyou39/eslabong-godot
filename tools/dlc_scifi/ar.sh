#!/bin/bash
# usage: ar.sh <station|alien|reactor> [build|norebuild] [vue ...]   (textures: ../.venv/bin/python tex_<id>.py)
HERE="$(cd "$(dirname "$0")" && pwd)"
B=/Applications/Blender.app/Contents/MacOS/Blender
ROOT="$(cd "$HERE/../.." && pwd)"
S=${SF_AR:-/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/sfa}
mkdir -p $S
N=$1; shift
if [ "$1" = "norebuild" ]; then shift; else
  [ "$1" = "build" ] && shift
  $B -b --python $HERE/build_$N.py 2>&1 | grep -E "^\[|Error|Traceback|File \"|line [0-9]|spectateurs|WARN|Exception|tris" | head -40
fi
for V in "$@"; do
  SAFE=$(echo $V | tr ',:' '__')
  $B -b --python $HERE/render_sf.py -- $ROOT/assets/models/arenas/arena_$N.glb $S/${N}_$SAFE.png $N $V ${RES:-1280x720} 2>&1 | grep -E "Traceback|RuntimeError|Error"
done
