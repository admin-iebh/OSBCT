#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=_xc/h3/built; N=${1:-6}
mkdir -p $OUT
TODO=$(for v in $(cat _xc/h2/moved19.txt); do [ -f $OUT/$v.txt ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  ( C2COL=1 timeout 40 python3 pipeline/build_khu_volume.py $v --write > $OUT/$v.txt 2>&1 ) &
  i=$((i+1)); if [ $((i%5)) -eq 0 ]; then wait; fi
done
wait
echo "$(ls $OUT/*.txt 2>/dev/null | wc -l)/19"
