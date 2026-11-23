#!/bin/bash
# usage: dev_sheet.sh groupe noms|all   -> $SP/sheet_<groupe>.png
cd "$(dirname "$0")"
SP=/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/greek
mkdir -p $SP
/Applications/Blender.app/Contents/MacOS/Blender -b --python dev_gear_greek.py -- $1 $2 $SP 2>&1 | grep -E "^PART|Error|Trace|line [0-9]|\.py\"|Exception"
../.venv/bin/python - <<PY
import json, sys
sys.path.insert(0, '../blender_kit_bodies')
import compose
for job in json.load(open('$SP/jobs_dev.json')):
    compose.sheet(job); print(job['path'])
PY
