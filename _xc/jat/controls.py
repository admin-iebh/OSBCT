# -*- coding: utf-8 -*-
"""`check_page_fidelity.py --controls`, one control per call, because the bridge
kills a 45 s call and seven full passes over a Jātaka volume do not fit in one.
The honest verdict vector is cached on disk and every control is scored the same
way the harness scores it: HOW MANY PRINTED LINES CHANGE VERDICT."""
import json, os, sys
ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import check_page_fidelity as C
vol = sys.argv[1]
cache = '%s/_xc/jat/ctl_%s_honest.json' % (ROOT, vol)
if not os.path.exists(cache):
    r = C.run(vol, verbose=True)
    json.dump([x[5] for x in r['rows']], open(cache, 'w'))
    print(C.summarise(r) + '   [honest]')
    sys.exit(0)
bv = json.load(open(cache))
for cn in sys.argv[2:]:
    r = C.run(vol, control=cn, verbose=True)
    rv = [x[5] for x in r['rows']]
    n = sum(1 for a, b in zip(bv, rv) if a != b) + abs(len(bv) - len(rv))
    print(C.summarise(r) + '   [%s] fired on %d of %d lines%s'
          % (cn, n, len(bv), '   *** VACUOUS ***' if n == 0 else ''))
    sys.stdout.flush()
