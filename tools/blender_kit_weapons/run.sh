#!/bin/bash
# usage: run.sh [build_args...]  -> construit, rend, planches
HERE="$(cd "$(dirname "$0")" && pwd)"
SP=/tmp/eslabong_scratch
KIT="$HERE/../../assets/models/kit"
[ -n "$1" ] && KIT=$SP/dev
BL=/Applications/Blender.app/Contents/MacOS/Blender
PY="$HERE/../.venv/bin/python"
ONLY="$1"        # préfixes séparés par des virgules (optionnel)
rm -rf $SP/r; mkdir -p $SP/r $SP/sheets
if [ -n "$ONLY" ]; then BARGS="-- --only $ONLY"; else BARGS=""; fi
$BL -b --python "$HERE/build_weapons.py" $BARGS 2>&1 | grep -E "tris=|EXPORTED|Error|Traceback|error|File " 
$BL -b --python "$HERE/render_views.py" -- "$KIT/kit_weapons.glb" $SP/r $( [ -n "$VIEWS" ] && echo --views $VIEWS ) $( [ -n "$ONLY" ] && echo ${ONLY//,/ } ) 2>&1 | grep -E "RENDER_DONE|Error|Traceback"
$PY "$HERE/sheets.py" $SP/r "$KIT/kit_weapons_manifest.json" $SP/sheets sh ${PER:-6} ${VIEWS:-side,tq} ${ONLY}
# publication des planches si build complet
if [ -z "$ONLY" ]; then
  mkdir -p "$KIT/preview_weapons"; rm -f "$KIT"/preview_weapons/weapons_*.png
  i=1; for f in $(ls $SP/sheets/sh_*.png | sort); do cp "$f" "$KIT/preview_weapons/weapons_$(printf %02d $i).png"; i=$((i+1)); done
fi
