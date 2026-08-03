# -*- coding: utf-8 -*-
"""Verify, VOLUME BY VOLUME AGAINST THE PRINTED PAGE, that a shipped
sections k:'gatha' entry really opens with body-column prose.

Independent of build_khu_volume.py: the evidence is _xc/reseg/pline.py's
printed line stream (extract.py's own raw_pages+split_page with the glyph
errata) and locate.py's letter->line map.  The rule applied is the one stated
at the head of build_khu_volume.py and in the task:

    verse  = a RUN of >= 2 consecutive lines at an indent ABOVE the body column
    prose  = returns to the body column

The BODY COLUMN of a page is measured as the page's own modal indent among
the lines that carry more than a few words -- the column the page sets its
running text in.  Reported alongside the raw histogram so the judgement can be
checked by eye rather than taken on trust.
"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import pline, locate

FLAG = [('02Vin02','0',3), ('06VinSg06','0',1), ('14SamA01','0',5),
        ('17AnA01','0',3), ('27Khu10','151',1), ('36Abhi08','0',1),
        ('38Abhi10','0',6), ('41KhuA22','2',4), ('42KhuA23','2',1)]


def body_col(stream, pg):
    """Modal indent on pdf page `pg` among lines of >= 5 words."""
    h = collections.Counter(it[2] for it in stream
                            if it[0] == pg and len(it[3].split()) >= 5)
    if not h:
        h = collections.Counter(it[2] for it in stream if it[0] == pg)
    return (h.most_common(1)[0][0] if h else 0), h


def run(vol, ordk, idx, nshow=14):
    S = json.load(open('%s/site/reader/sections/%s.json' % (ROOT, vol),
                       encoding='utf-8'))
    ent = S[ordk][idx]
    text = str(ent.get('l', ''))
    st = pline.stream(vol)
    P = locate.Page(st)
    sp = P.span(text)
    print('==== %s  sec%s[%d]  k=%s  %d source lines' %
          (vol, ordk, idx, ent.get('k'), text.count('\n') + 1))
    if sp is None:
        print('   NOT FOUND in printed stream -- cannot judge')
        return None
    l0, l1, a, b = sp
    lines = st[l0:l1 + 1]
    pg = lines[0][0]
    bc, hist = body_col(st, pg)
    print('   printed pdf page %d, body column = %d   indent histogram %s' %
          (pg, bc, sorted(hist.items())))
    verdict = []
    for k, it in enumerate(lines[:nshow]):
        if it[0] != pg:
            pg = it[0]; bc, hist = body_col(st, pg)
            print('   --- page %d, body column %d ---' % (pg, bc))
        rel = it[2] - bc
        tag = 'BODY(prose)' if rel <= 2 else ('body+%d' % rel)
        print('   %2d  ind=%3d  %-12s  %s' % (k, it[2], tag, it[3][:88]))
        verdict.append(rel)
    if len(lines) > nshow:
        print('   ... %d more lines' % (len(lines) - nshow))
    lead = 0
    for r in verdict:
        if r <= 2:
            lead += 1
        else:
            break
    print('   >>> LEADING body-column lines: %d' % lead)
    return lead


if __name__ == '__main__':
    only = sys.argv[1:] 
    res = {}
    for v, o, i in FLAG:
        if only and v not in only:
            continue
        try:
            res[v] = run(v, o, i)
        except Exception as e:
            print('==== %s ERROR %r' % (v, e))
        print()
    print('SUMMARY', json.dumps(res))
