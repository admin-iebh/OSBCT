#!/bin/bash
# resumable presentation sweep over the commentary + subcommentary layers
cd "$(dirname "$0")"
LOG=_fnprobe/check_layout_AT.log
touch $LOG
VOLS=$(node -e "
const m=require('./site/reader/manifest.json').volumes;const fs=require('fs');
console.log(Object.keys(m).filter(v=>m[v].layer!=='canon'&&fs.existsSync('site/'+v+'.json')).sort().join(' '));")
for v in $VOLS; do
  grep -q "	$v	" $LOG && continue
  out=$(timeout 120 node pipeline/check_layout.js $v 2>&1 | grep -v "^OSBCT" | grep -v "^$" | head -8 | tr '\n' '|')
  printf '%s\t%s\t%s\n' "$(date -u +%H:%M:%S)" "$v" "$out" >> $LOG
done
