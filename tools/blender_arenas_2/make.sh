#!/bin/bash
# usage: make.sh <id> [vue ...]  -> build GLB + rendus de contrôle (scratchpad)
D="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$D/../.." && pwd)"
B=/Applications/Blender.app/Contents/MacOS/Blender
S=${SCRATCH:-/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/ar}
mkdir -p "$S"
N=$1; shift
if [ "$1" = "norebuild" ]; then shift; else
  $B -b --python $D/build_$N.py 2>&1 | grep -E "^\[|Error|Traceback|File \"|line [0-9]|WARN|Exception|rror" | head -40
fi
for V in "$@"; do
  SAFE=$(echo $V | tr ',:' '__')
  $B -b --python $D/render.py -- $ROOT/assets/models/arenas/arena_$N.glb $S/${N}_$SAFE.png $N $V 960x540 2>&1 | grep -E "Traceback|RuntimeError" | grep -v "Shadow buffer"
done
