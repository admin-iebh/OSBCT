# -*- coding: utf-8 -*-
"""Enumerate EVERY divergence between the shipped render and the new render and
adjudicate each against the PRINTED PAGE.  delta 0 + identical=False means a
pure re-ordering; this says which order the page agrees with, region by region.
Compared as CHUNK LISTS (a few thousand items), not as 500k-character strings."""
import os, sys, io, contextlib, difflib
V = sys.argv[1]
os.environ['VOL'] = V
sys.path.insert(0, os.path.abspath('_xc/reseg2'))
import importlib.util
spec = importlib.util.spec_from_file_location('b2', '_xc/reseg2/b2/b2_verse.py')
m = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(m)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    same, delta = m.build(write=False, quiet=True)
A, B = m._CHUNKS[-2], m._CHUNKS[-1]
print('%s  identical=%s  delta=%+d   chunks shipped %d / new %d'
      % (V, same, delta, len(A), len(B)))
if same:
    raise SystemExit(0)
A2 = [c for c in A if c]
B2 = [c for c in B if c]
PGT = m.PG.text
ops = [o for o in difflib.SequenceMatcher(None, A2, B2, autojunk=False).get_opcodes()
       if o[0] != 'equal']
print('divergent regions: %d' % len(ops))
for tag, i1, i2, j1, j2 in ops:
    olds, news = A2[i1:i2], B2[j1:j2]
    moved = (olds or news)[0]
    pi = PGT.find(moved[:60])
    nxt_page = PGT[pi + len(moved[:60]): pi + len(moved[:60]) + 30] if pi >= 0 else ''
    nxt_old = ''.join(A2[i2:i2 + 2])[:30]
    nxt_new = ''.join(B2[j2:j2 + 2])[:30]
    v = ('NEW matches the page' if nxt_page and nxt_page[:18] == nxt_new[:18]
         else 'OLD matches the page' if nxt_page and nxt_page[:18] == nxt_old[:18]
         else 'undecided')
    print('  %-8s old %d chunk(s) / new %d   page@%-7s  %s' % (tag, i2-i1, j2-j1, pi, v))
    print('      moved     : %r' % moved[:76])
    print('      page next : %r' % nxt_page)
    print('      old next  : %r' % nxt_old)
    print('      new next  : %r' % nxt_new)
