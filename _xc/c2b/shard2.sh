#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=$1; N=${2:-16}
mkdir -p $OUT
TODO=$(for v in $(cat _xc/c2b/eligible.txt); do [ -f $OUT/$v.txt ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  ( C2MIXED=$C2MIXED C2TAIL=$C2TAIL DP_DEFAULT=$DP_DEFAULT SUF=$SUF timeout 40 python3 _xc/c2b/replay.py $v > $OUT/$v.txt 2>&1 ) &
  i=$((i+1)); if [ $((i%4)) -eq 0 ]; then wait; fi
done
wait
echo "done: $(ls $OUT | wc -l)/112"
