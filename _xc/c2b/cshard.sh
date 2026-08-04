#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=_xc/c2b/cen3; N=${1:-8}
TODO=$(for v in $(cat _xc/c2b/allvols.txt); do [ -f $OUT/$v.json ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  ( timeout 42 python3 pipeline/check_page_fidelity.py $v --out $OUT >/dev/null 2>&1 ) &
  i=$((i+1)); if [ $((i%4)) -eq 0 ]; then wait; fi
done
wait
echo "census: $(ls $OUT/*.json | wc -l)/118"
