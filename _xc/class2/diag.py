# -*- coding: utf-8 -*-
"""Why does the page side call a NEAR-band line 'display'?  Read off the page only."""
import sys, os, re, collections, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reseg'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'pipeline'))
import pline
import check_page_fidelity as F

VNUM = re.compile(r'^\s*[\(\[]?\d{1,4}\s*[\.\-–]')

def analyse(vol):
    st = pline.stream(vol)
    lines = [x for x in st if F.letters(x[3])]
    body, W = F.page_geometry(lines)
    n = len(lines)
    nbody = sum(1 for l in lines if l[2] == body)
    near = [l for l in lines if body + F.NEAR <= l[2] < body + F.INSET]
    cls, verse, _ = F.page_classes(lines, body, W)
    # why is each NEAR-band verse line in a block?
    why = collections.Counter()
    ex = collections.defaultdict(list)
    for i, l in enumerate(lines):
        if not verse[i]:
            continue
        if not (body + F.NEAR <= l[2] < body + F.INSET):
            continue
        d = cls[i] == 'disp'
        num = bool(VNUM.match(l[3]))
        k = ('disp' if d else 'ext') + ('+num' if num else '-num')
        why[k] += 1
        if len(ex[k]) < 4:
            ex[k].append((l[0], l[2], l[2] + len(l[3]), l[3][:64]))
    print('%-10s n=%6d body=%d W=%d  body-share=%.1f%%  near=%d (%.1f%%)'
          % (vol, n, body, W, 100.0 * nbody / n, len(near), 100.0 * len(near) / n))
    print('   near-band lines inside a page-verse block: %d' % sum(why.values()))
    for k in sorted(why):
        print('     %-10s %5d' % (k, why[k]))
        for e in ex[k]:
            print('        p%-4d %2d-%2d %s' % e)

for v in sys.argv[1:]:
    analyse(v)
