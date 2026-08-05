#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=$1; N=${2:-6}
mkdir -p $OUT
TODO=$(for v in $(cat _xc/h2/moved19.txt); do [ -f $OUT/$v.json ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  ( timeout 40 python3 pipeline/check_page_fidelity.py $v --out $OUT >/dev/null 2>&1 ) &
  i=$((i+1)); if [ $((i%5)) -eq 0 ]; then wait; fi
done
wait
echo "$(ls $OUT/*.json 2>/dev/null | wc -l)/19"
