# -*- coding: utf-8 -*-
"""24KhuA05's design run is not letter-identical to the SHIPPED render (it has
3 justified divergences the page adjudicates in its favour), so `identical`
cannot discriminate the two delta-0 controls.  Count DIVERGENCES instead."""
import os, sys, io, contextlib
V = sys.argv[1]; os.environ['VOL'] = V
sys.path.insert(0, os.path.abspath('_xc/reseg2'))
import importlib.util
spec = importlib.util.spec_from_file_location('b2', '_xc/reseg2/b2/b2_verse.py')
m = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(m)

def diverge():
    a = ''.join(m._CHUNKS[-2]); b = ''.join(m._CHUNKS[-1])
    i = j = n = 0; tot = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]: i += 1; j += 1; continue
        n += 1; best = None
        for da in range(0, 6000):
            key = a[i+da:i+da+50]
            if len(key) < 50: break
            p = b.find(key, j, j+20000)
            if p >= 0: best = (da, p - j); break
        if best is None: return n, -1
        tot += max(best[0], best[1]); i += best[0]; j += best[1]
    return n, tot

for label, kw in [('DESIGN', {}),
                  ('CONTROL uddana anchored FIRST of run', dict(udd_anchor='first')),
                  ('CONTROL leaked-heading/uddana hide disabled', dict(leak_hide=False))]:
    with contextlib.redirect_stdout(io.StringIO()):
        same, delta = m.build(write=False, quiet=True, **kw)
    n, tot = diverge()
    print('%-46s identical=%-5s delta=%+d  divergences=%d (%d letters)'
          % (label, same, delta, n, tot))
