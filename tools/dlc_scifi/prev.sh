#!/bin/bash
# usage: prev.sh [bodies|gear|weapons|assembled|all]  -> planches dans assets/models/kit/preview_scifi/
HERE="$(cd "$(dirname "$0")" && pwd)"
export SF_TMP=${SF_TMP:-/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/sfp}
mkdir -p $SF_TMP
/Applications/Blender.app/Contents/MacOS/Blender -b --python $HERE/make_previews_scifi.py -- ${1:-all} 2>&1 | grep -E "Error|Trace|line [0-9]|\.py\""
$HERE/../.venv/bin/python $HERE/make_previews_scifi.py compose
