#!/bin/bash
# swap.sh old|new VOL...
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
W=$1; shift
for v in "$@"; do
  for n in verse sections uddana hide incipit booktitle; do
    f=site/reader/$n/$v.json
    if [ "$W" = old ] && [ -f "$f.preC2" ]; then cp "$f.preC2" "$f"; fi
    if [ "$W" = new ] && [ -f "$f.newC2" ]; then cp "$f.newC2" "$f"; fi
  done
done
