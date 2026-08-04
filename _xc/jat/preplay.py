# -*- coding: utf-8 -*-
"""Same replay, but with the PRE-CHANGE builder (`.prejat`): the control that
says whether a difference is mine or was already there."""
import importlib.util, json, os, sys
from importlib.machinery import SourceFileLoader
ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
def load(p):
    spec = importlib.util.spec_from_loader('bkvp', SourceFileLoader('bkvp', p))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
for vol in sys.argv[1:]:
    m = load(os.path.join(ROOT, 'pipeline', 'build_khu_volume.py.prejat'))
    m.use(vol)
    v, s, u, h, i, rep = m.build()
    out = [vol + ' PRE']
    for name, cur in (('verse', v), ('sections', s), ('uddana', u)):
        sp = os.path.join(ROOT, 'site', 'reader', name, vol + '.json')
        S = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
        R = {str(k): x for k, x in cur.items()}
        moved = [k for k in set(S) & set(R) if S[k] != R[k]]
        out.append('%s %s(moved %d %s)' % (name, 'SAME' if S == R else 'DIFF',
                                           len(moved), sorted(moved)[:6]))
    print('  '.join(out)); sys.stdout.flush()
