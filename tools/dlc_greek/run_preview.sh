#!/bin/bash
# usage: run_preview.sh gear|gods|all [glb] [out]   (par défaut : GLB livré -> assets/models/kit/preview_greek)
cd "$(dirname "$0")"
SP=/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/greek
EXTRA=""; [ -n "$2" ] && EXTRA="--glb $2"; [ -n "$3" ] && EXTRA="$EXTRA --out $3"
/Applications/Blender.app/Contents/MacOS/Blender -b --python preview_greek.py -- $1 $EXTRA 2>&1 | grep -E "^sheet|Error|Trace|line [0-9]|\.py\""
../.venv/bin/python - <<PY
import json, sys
sys.path.insert(0, '../blender_kit_bodies')
import compose
for job in json.load(open('$SP/pv/jobs_$1.json')):
    compose.sheet(job); print(job['path'])
PY
