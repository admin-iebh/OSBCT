#!/bin/bash
# swap.sh old|new VOL...
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
W=$1; shift
for v in "$@"; do
  for n in verse sections uddana hide incipit booktitle pbreak; do
    f=site/reader/$n/$v.json
    if [ "$W" = old ] && [ -f "$f.preDC" ]; then cp "$f.preDC" "$f"; fi
    if [ "$W" = new ] && [ -f "$f.newDC" ]; then cp "$f.newDC" "$f"; fi
  done
done
echo "swapped to $W: $*"
