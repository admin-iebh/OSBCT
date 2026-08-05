#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
N=${1:-5}
TODO=$(for v in $(cat _xc/h2/moved19.txt); do [ -f site/reader/pbreak/$v.json ] || echo $v; done | head -$N)
for v in $TODO; do timeout 40 python3 _xc/pagemark/derive.py $v --out site/reader/pbreak >/dev/null 2>&1; done
echo "left: $(for v in $(cat _xc/h2/moved19.txt); do [ -f site/reader/pbreak/$v.json ] || echo $v; done | wc -l)"
