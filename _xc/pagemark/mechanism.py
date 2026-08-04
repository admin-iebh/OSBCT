# -*- coding: utf-8 -*-
"""VERIFY the mechanism rather than assume it.

The claim is: a paragraph carries ONE `pdf_page`/`printed` -- the page it STARTS
on -- so the marker can only be placed at a paragraph boundary and drifts
wherever a paragraph spans a page break.  Two things follow and are testable:

  1. a paragraph's `printed` equals the printed page of its FIRST printed line;
  2. the number of pages a paragraph SPANS is exactly the number of markers
     that have to wait for the next boundary.
"""
import sys, os, json, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline')); sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import check_page_fidelity as CPF, pline
letters, Index = CPF.letters, CPF.Index
for vol in sys.argv[1:]:
    c = json.load(open('%s/site/%s.json' % (ROOT, vol), encoding='utf-8'))
    paras = c['paragraphs']
    buf, starts = [], []
    pos = 0
    for p in paras:
        s = letters(p.get('text', '') or ''); starts.append(pos); buf.append(s); pos += len(s)
    C = ''.join(buf); IX = Index(C)
    ends = [starts[i] + len(buf[i]) for i in range(len(paras))]
    st = pline.stream(vol)
    pgs = [p['pdf_page'] for p in paras if p.get('pdf_page')]
    LO, HI = min(pgs), max(pgs)
    lines = [x for x in st if LO <= x[0] <= HI and letters(x[3])]
    loc, cur = [], 0
    for l in lines:
        t = letters(l[3]); j = IX.find(t, cur)
        if j < 0: j = IX.find(t, max(0, cur - 40000))
        if j < 0: j = IX.findany(t)
        if j >= 0: cur = j + len(t)
        loc.append(j)
    # pages each paragraph's located lines touch
    span = collections.defaultdict(set)
    import bisect
    for k, l in enumerate(lines):
        if loc[k] < 0: continue
        i = max(0, bisect.bisect_right(starts, loc[k]) - 1)
        if starts[i] <= loc[k] < ends[i]: span[i].add(l[0])
    ok = bad = nospan = 0
    ex = []
    multi = collections.Counter()
    for i, p in enumerate(paras):
        s = span.get(i)
        if not s: nospan += 1; continue
        multi[min(len(s), 6)] += 1
        if min(s) == p.get('pdf_page'): ok += 1
        else:
            bad += 1
            if len(ex) < 5: ex.append((i, p.get('pdf_page'), sorted(s)[:4]))
    tot_extra = sum((len(s) - 1) for s in span.values())
    print('%-11s paragraphs=%5d  pdf_page == page of its FIRST located line: %d ok, %d wrong, %d unlocated'
          % (vol, len(paras), ok, bad, nospan))
    print('            paragraphs spanning 1/2/3/4/5/6+ printed pages: '
          + '/'.join(str(multi[k]) for k in range(1, 7)))
    print('            page turns swallowed inside a paragraph (sum of spans-1): %d' % tot_extra)
    if ex: print('            first wrong: %s' % (ex,))
