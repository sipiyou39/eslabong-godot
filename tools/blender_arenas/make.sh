#!/bin/bash
# usage: make.sh <nom> [vue ...]   -> build + rendu(s) de contrôle dans le scratchpad
B=/Applications/Blender.app/Contents/MacOS/Blender
D=/path/to/elsasko/tools/blender_arenas
O=/path/to/elsasko/assets/models/arenas
S=/tmp/eslabong_scratch/ar
N=$1; shift
if [ "$N" = "club" ]; then F=club_hall; else F=arena_$N; fi
if [ "$1" = "norebuild" ]; then shift; else
  $B -b --python $D/build_$N.py 2>&1 | grep -E "^\[|Error|Traceback|File \"|line [0-9]|spectateurs|WARN|Exception" | head -40
fi
for V in "$@"; do
  SAFE=$(echo $V | tr ',:' '__')
  $B -b --python $D/render.py -- $O/$F.glb $S/${N}_$SAFE.png $N $V 2>&1 | grep -E "Traceback|RuntimeError" 
done
