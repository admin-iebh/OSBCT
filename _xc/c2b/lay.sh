#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=$1; N=${2:-6}
mkdir -p $OUT
TODO=$(for v in $(cat _xc/c2b/changedvols.txt); do [ -f $OUT/$v.txt ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  ( timeout 40 node pipeline/check_layout.js $v > $OUT/$v.txt 2>&1 ) &
  i=$((i+1)); if [ $((i%3)) -eq 0 ]; then wait; fi
done
wait
echo "$OUT: $(ls $OUT|wc -l)/39"
