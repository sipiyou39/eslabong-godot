#!/bin/bash
# usage: dev_sheet.sh group i0 i1 [species]
cd "$(dirname "$0")"
SP=/tmp/eslabong_scratch
/Applications/Blender.app/Contents/MacOS/Blender -b --python dev_gear.py -- $1 $2 $3 $SP $4 2>&1 | grep -E "^[a-z_]+ [0-9]+$|Error|Trace|line [0-9]|\.py"
../.venv/bin/python - <<PY
import json, sys
sys.path.insert(0, '.')
import compose
for job in json.load(open('$SP/jobs_dev.json')):
    compose.sheet(job); print(job['path'])
PY
