#!/bin/bash
# One SUBPROCESS PER VOLUME — build_khu_volume memoises page reads in module
# globals and `use()` only rebinds some of them, so a single long-lived process
# could carry one volume's cache into the next.  Resumable: a volume already in
# results.txt is skipped.  BUDGET seconds then stops, because device_bash is
# capped at 45s and background jobs do not survive between calls.
cd "$(dirname "$0")/.."
BUDGET=${1:-35}
START=$SECONDS
touch _stale/results.txt
for V in $(python3 -c "
import sys; sys.path.insert(0,'pipeline')
import build_khu_volume as B
print('\n'.join(sorted(B.SPEC)))"); do
  grep -q "  *$V " _stale/results.txt 2>/dev/null && continue
  grep -qE "^(SAME|DIFF|ERR) +$V\b" _stale/results.txt 2>/dev/null && continue
  [ $((SECONDS-START)) -ge $BUDGET ] && { echo "-- budget reached --"; break; }
  timeout 120 python3 _stale/dryrun_one.py "$V" >> _stale/results.txt 2>&1 \
    || echo "ERR    $V   driver timeout/crash" >> _stale/results.txt
done
echo "done: $(wc -l < _stale/results.txt) / 117"
