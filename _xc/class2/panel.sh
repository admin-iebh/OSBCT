#!/bin/bash
cd /sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
CFG=$1; shift
for V in "$@"; do
  if [ "$CFG" = "old" ]; then
    PAGEFID_SHARP=0 python3 pipeline/check_page_fidelity.py $V > _xc/class2/cmp/$V.$CFG.txt 2>/dev/null &
  else
    PAGEFID_RULES=$CFG python3 pipeline/check_page_fidelity.py $V > _xc/class2/cmp/$V.$CFG.txt 2>/dev/null &
  fi
done
wait
