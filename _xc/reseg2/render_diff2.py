# -*- coding: utf-8 -*-
"""Every divergence between shipped and new render, by resynchronising scan,
each adjudicated against the PRINTED PAGE."""
import os, sys, io, contextlib
V = sys.argv[1]
os.environ['VOL'] = V
sys.path.insert(0, os.path.abspath('_xc/reseg2'))
import importlib.util
spec = importlib.util.spec_from_file_location('b2', '_xc/reseg2/b2/b2_verse.py')
m = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(m)
with contextlib.redirect_stdout(io.StringIO()):
    same, delta = m.build(write=False, quiet=True)
a = ''.join(m._CHUNKS[-2]); b = ''.join(m._CHUNKS[-1])
PGT = m.PG.text
print('%s  identical=%s delta=%+d  len %d/%d' % (V, same, delta, len(a), len(b)))
i = j = 0
n = 0
while i < len(a) and j < len(b):
    if a[i] == b[j]:
        i += 1; j += 1; continue
    n += 1
    # resynchronise: find the shortest k such that a[i+k:i+k+50] == b[j+?..]
    best = None
    for da in range(0, 4000):
        key = a[i + da:i + da + 50]
        if len(key) < 50: break
        p = b.find(key, j, j + 8000)
        if p >= 0:
            best = (da, p - j); break
    if best is None:
        print('  #%d  could not resynchronise at old %d / new %d' % (n, i, j)); break
    da, db = best
    old_only, new_only = a[i:i + da], b[j:j + db]
    moved = new_only or old_only
    pi = PGT.find(moved[:50])
    nxt_page = PGT[pi + len(moved[:50]): pi + len(moved[:50]) + 24] if pi >= 0 else ''
    nxt = a[i + da:i + da + 24]
    verdict = 'undecided'
    if pi >= 0:
        verdict = ('NEW matches the page (the block belongs HERE)'
                   if nxt_page[:16] == nxt[:16] else
                   'page disagrees with BOTH at 16 letters')
    print('  #%d at old %d / new %d : old-only %d letters, new-only %d letters  page@%s  %s'
          % (n, i, j, da, db, pi, verdict))
    if old_only: print('       only in SHIPPED : %r' % old_only[:90])
    if new_only: print('       only in NEW     : %r' % new_only[:90])
    print('       both continue   : %r' % nxt)
    i += da; j += db
print('total divergences: %d' % n)
