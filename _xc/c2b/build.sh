#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
OUT=_xc/c2b/built; N=${1:-12}
mkdir -p $OUT
TODO=$(for v in $(cat _xc/c2b/eligible.txt); do [ -f $OUT/$v.txt ] || echo $v; done | head -$N)
i=0
for v in $TODO; do
  (
   for n in verse sections uddana hide incipit booktitle; do
     f=site/reader/$n/$v.json; [ -f "$f" ] && [ ! -f "$f.preC2" ] && cp "$f" "$f.preC2"
   done
   timeout 40 python3 pipeline/build_khu_volume.py $v --write > $OUT/$v.txt 2>&1
  ) &
  i=$((i+1)); if [ $((i%4)) -eq 0 ]; then wait; fi
done
wait
echo "built: $(ls $OUT | wc -l)/112"
