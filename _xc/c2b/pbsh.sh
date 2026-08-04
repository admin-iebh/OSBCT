#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=_xc/c2b/pb; N=${1:-10}
TODO=$(for v in $(cat _xc/c2b/changedvols.txt); do [ -f $OUT/$v.json ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  ( timeout 40 python3 _xc/pagemark/derive.py $v --out $OUT >/dev/null 2>&1 ) &
  i=$((i+1)); if [ $((i%4)) -eq 0 ]; then wait; fi
done
wait
echo "pb: $(ls $OUT/*.json|wc -l)/39"
