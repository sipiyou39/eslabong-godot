#!/bin/bash
# usage: preview.sh <id> [vue]  -> assets/models/arenas/preview/<id>.png (960x540, vue de jeu par défaut)
D="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$D/../.." && pwd)"
B=/Applications/Blender.app/Contents/MacOS/Blender
mkdir -p "$ROOT/assets/models/arenas/preview"
$B -b --python $D/render.py -- $ROOT/assets/models/arenas/arena_$1.glb $ROOT/assets/models/arenas/preview/$1.png $1 ${2:-game} 960x540 2>&1 | grep -E "Traceback|RuntimeError"
