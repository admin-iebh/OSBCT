# -*- coding: utf-8 -*-
"""Every flagged entry with its printed indents and TWO LINES OF PRINTED
CONTEXT either side, so a lone raised line can be told apart from a prose
paragraph opener: an opener is followed by body-column continuation, a
CENTRED TITLE is not."""
import json, os, sys, collections
ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import pline
rows = json.load(open(ROOT + '/_xc/italic9/sweep.json'))
for r in rows:
    if len(sys.argv) > 1 and r['vol'] not in sys.argv[1:]:
        continue
    st = pline.stream(r['vol']); bc = r['bc']
    print('==== %s sec%s[%d]  %d lines  bc=%d  %s'
          % (r['vol'], r['ord'], r['idx'], r['nlines'], bc,
             ''.join('%s%d' % (k, e-s+1) for k, s, e in r['blocks'])))
    lo, hi = max(0, r['l0']-2), min(len(st), r['l1']+3)
    for k in range(lo, hi):
        it = st[k]
        inside = r['l0'] <= k <= r['l1']
        kd = r['kind'][k-r['l0']] if inside else '.'
        if r['nlines'] > 12 and inside and not (k-r['l0'] < 4 or k > r['l1']-3):
            if k-r['l0'] == 4:
                print('       ... %d lines ...' % (r['nlines']-7))
            continue
        print('  %s p%-4d ind=%3d rel=%+3d %s  %s'
              % ('IN ' if inside else 'ctx', it[0], it[2], it[2]-bc, kd, it[3][:78]))
    print()
