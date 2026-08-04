#!/bin/bash
# usage: shard.sh OUTDIR ENVSET N   -- run up to N volumes not yet done, 4 in parallel
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=$1; N=${2:-16}
mkdir -p $OUT
TODO=$(for v in $(cat _xc/c2b/vols.txt); do [ -f $OUT/$v.txt ] || echo $v; done | head -$N)
echo "todo: $(echo $TODO | wc -w)"
i=0
for v in $TODO; do
  ( C2MIXED=$C2MIXED SUF=$SUF timeout 40 python3 _xc/c2b/replay.py $v > $OUT/$v.txt 2>&1 ) &
  i=$((i+1))
  if [ $((i%4)) -eq 0 ]; then wait; fi
done
wait
echo "done: $(ls $OUT | wc -l)/117"
