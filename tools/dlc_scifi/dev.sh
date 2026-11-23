#!/bin/bash
# usage: dev.sh groupe [noms] [--base robot]  -> planche dans $SF/sheet_<groupe>.png
HERE="$(cd "$(dirname "$0")" && pwd)"
SF=${SF:-/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/sf}
mkdir -p $SF
G=$1; shift
/Applications/Blender.app/Contents/MacOS/Blender -b --python $HERE/dev_sf.py -- $G $SF "$@" 2>&1 | grep -E "^[a-z_*A-Z0-9]+ \[|OVER|Error|Trace|line [0-9]|\.py\"" 
$HERE/../.venv/bin/python - <<PY
import json, sys
sys.path.insert(0, '$HERE/../blender_kit_bodies')
import compose
for job in json.load(open('$SF/jobs_dev.json')):
    compose.sheet(job); print(job['path'])
PY
