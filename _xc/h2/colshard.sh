#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=_xc/h2/col; N=${1:-16}
mkdir -p $OUT
TODO=$(for v in $(cat _xc/h2/eligible116.txt); do [ -f $OUT/$v.txt ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  ( C2COL=1 timeout 40 python3 _xc/c2b/replay.py $v > $OUT/$v.txt 2>&1 ) &
  i=$((i+1)); if [ $((i%6)) -eq 0 ]; then wait; fi
done
wait
echo "done: $(ls $OUT/*.txt 2>/dev/null | wc -l)/116"
