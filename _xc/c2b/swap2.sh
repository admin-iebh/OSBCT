#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
W=$1
for v in $(cat _xc/c2b/changedvols.txt); do
  for n in verse sections uddana hide incipit booktitle pbreak; do
    f=site/reader/$n/$v.json
    [ "$W" = old ] && [ -f "$f.preC2" ] && cp "$f.preC2" "$f"
    [ "$W" = new ] && [ -f "$f.newC2" ] && cp "$f.newC2" "$f"
  done
done
echo "swapped $W"
