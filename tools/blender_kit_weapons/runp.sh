#!/bin/bash
# usage: runp.sh [prefixes]  -> construit les props, rend, planches
HERE="$(cd "$(dirname "$0")" && pwd)"
SP=/tmp/eslabong_scratch
KIT="$HERE/../../assets/models/kit"
[ -n "$1" ] && KIT=$SP/dev
BL=/Applications/Blender.app/Contents/MacOS/Blender
PY="$HERE/../.venv/bin/python"
ONLY="$1"
rm -rf $SP/rp; mkdir -p $SP/rp $SP/psheets
if [ -n "$ONLY" ]; then BARGS="-- --only $ONLY"; else BARGS=""; fi
$BL -b --python "$HERE/build_props.py" $BARGS 2>&1 | grep -E "tris=|EXPORTED|Error|Traceback|error|File |line "
$BL -b --python "$HERE/render_views.py" -- "$KIT/kit_props.glb" $SP/rp $( [ -n "$ONLY" ] && echo ${ONLY//,/ } ) 2>&1 | grep -E "RENDER_DONE|Error|Traceback"
$PY "$HERE/sheets.py" $SP/rp "$KIT/kit_props_manifest.json" $SP/psheets ps ${PER:-6} tq,side ${ONLY}
if [ -z "$ONLY" ]; then
  mkdir -p "$KIT/preview_weapons"; rm -f "$KIT"/preview_weapons/props_*.png
  i=1; for f in $(ls $SP/psheets/ps_*.png | sort); do cp "$f" "$KIT/preview_weapons/props_$(printf %02d $i).png"; i=$((i+1)); done
fi
