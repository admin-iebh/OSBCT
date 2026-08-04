#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=$1; N=${2:-10}
mkdir -p $OUT
i=0; n=0
while read v a b c d; do
  key="$v.$a.$c"
  [ -f "$OUT/$key.txt" ] && continue
  [ $n -ge $N ] && break
  ( timeout 40 python3 pipeline/verify_render_vs_pdf.py $v $a $b $c $d --quiet > $OUT/$key.txt 2>&1 ) &
  i=$((i+1)); n=$((n+1))
  if [ $((i%4)) -eq 0 ]; then wait; fi
done < _xc/c2b/vrargs.txt
wait
echo "$OUT: $(ls $OUT | wc -l)/67"
