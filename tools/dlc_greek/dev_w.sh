#!/bin/bash
# usage: dev_w.sh [prefixes,...]  -> planches armes dans $SP/wsheets
HERE="$(cd "$(dirname "$0")" && pwd)"
SP=/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/greek
BL=/Applications/Blender.app/Contents/MacOS/Blender
PY="$HERE/../.venv/bin/python"
W="$HERE/../blender_kit_weapons"
rm -rf $SP/wr $SP/wsheets; mkdir -p $SP/wr $SP/wsheets
ARGS=""; [ -n "$1" ] && ARGS="$1"
$BL -b --python "$HERE/dev_weapons.py" -- ${ARGS//,/ } 2>&1 | grep -E "TRIS|EXPORTED|Error|Traceback|File |line [0-9]"
$BL -b --python "$W/render_views.py" -- $SP/dev/kit_greekw.glb $SP/wr ${ARGS//,/ } 2>&1 | grep -E "RENDER_DONE|Error|Traceback"
$PY "$W/sheets.py" $SP/wr $SP/dev/kit_greekw_manifest.json $SP/wsheets ws ${PER:-4} side,tq ${ARGS}
