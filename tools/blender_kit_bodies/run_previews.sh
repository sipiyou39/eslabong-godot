#!/bin/bash
# usage: run_previews.sh bodies|gear|assembled
cd "$(dirname "$0")"
/Applications/Blender.app/Contents/MacOS/Blender -b --python make_previews.py -- "$1" 2>&1 | grep -E "^sheet|Error|Trace|line [0-9]"
../.venv/bin/python compose.py "$1"
