#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=$1; SH=$2
mkdir -p $OUT
mapfile -t V < _xc/class2/vols.txt
for k in 0 1 2 3; do
  ( LIST=""; i=0
    for x in "${V[@]}"; do if [ $((i % 4)) -eq $k ]; then LIST="$LIST $x"; fi; i=$((i+1)); done
    PAGEFID_SHARP=$SH python3 pipeline/check_page_fidelity.py $LIST --out $OUT --budget 34 >/dev/null 2>&1 ) &
done
wait
ls $OUT | wc -l
