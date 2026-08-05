#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=$1; PC=$2; N=${3:-10}
mkdir -p $OUT
TODO=$(for v in $(cat _xc/c2b/allvols.txt); do [ -f $OUT/$v.json ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  ( PAGEFID_PAGECOL=$PC timeout 38 python3 pipeline/check_page_fidelity.py $v --out $OUT >/dev/null 2>&1 ) &
  i=$((i+1)); if [ $((i%5)) -eq 0 ]; then wait; fi
done
wait
echo "$OUT: $(ls $OUT/*.json 2>/dev/null | wc -l)/118"
