# -*- coding: utf-8 -*-
"""Anchor every paragraph (shipped and re-segmented) to the printed page.

Writes _xc/reseg/b3/anchors_<VOL>.json:
  {"ship": [[first_line, last_line, l0, l1], ...], "reseg": [...]}
indices into the printed line stream from pline.py.  An unlocatable paragraph
is recorded as null and COUNTED -- a gap in the evidence, not papered over.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import pline, locate

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
VOL = sys.argv[1] if len(sys.argv) > 1 else '20KhuA01'

pg = locate.Page(pline.stream(VOL))
out = {}
for name, path in (('ship', 'site/%s.json' % VOL),
                   ('reseg', '_xc/reseg/%s.json' % VOL)):
    ps = json.load(open(os.path.join(ROOT, path), encoding='utf-8'))['paragraphs']
    res = []
    cur = 0
    miss = 0
    for p in ps:
        sp = pg.span(p.get('text') or '', cur)
        if sp is None:
            sp = pg.span(p.get('text') or '', 0)
        if sp is None:
            res.append(None); miss += 1
        else:
            res.append(list(sp)); cur = sp[3]
    out[name] = res
    ok = [r for r in res if r]
    mono = all(ok[i][2] <= ok[i + 1][2] for i in range(len(ok) - 1))
    print('%-6s %4d paragraphs   located %4d   unlocatable %d   letter offsets monotonic %s'
          % (name, len(ps), len(ps) - miss, miss, mono))
json.dump(out, open(os.path.join(HERE, 'anchors_%s.json' % VOL), 'w',
                    encoding='utf-8'), ensure_ascii=False)
print('wrote anchors_%s.json' % VOL)
