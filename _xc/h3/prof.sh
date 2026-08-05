#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
mkdir -p _xc/h3/rA _xc/h3/rB
for v in "$@"; do
 ( [ -f _xc/h3/rA/$v.rows.json ] || PAGEFID_PAGECOL=0 timeout 38 python3 pipeline/check_page_fidelity.py $v --dump _xc/h3/rA >/dev/null 2>&1 ) &
 ( [ -f _xc/h3/rB/$v.rows.json ] || timeout 38 python3 pipeline/check_page_fidelity.py $v --dump _xc/h3/rB >/dev/null 2>&1 ) &
done
wait
ls _xc/h3/rB | wc -l
