# -*- coding: utf-8 -*-
"""Lay out, for reading, every printed line that ends in a mid-word hyphen AND
that `check_page_fidelity`'s PAGE side calls verse.

The hyphen decides nothing about verse -- the page does.  So this writes no
verdict.  It puts each candidate back on its printed page, with the indents the
edition sets, and leaves the judgement to the reader.

Source of the candidates: `_xc/hy1/cen/` (census over all 118 volumes).
Source of the page: `_xc/reseg/pline.py`, the same printed line stream every
page-fidelity instrument reads.
"""
import sys, os, json, re, html, collections
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import pline

PEY = re.compile(r'(^|\s)-(?:pa|pe|la)-$')
CTX = 8

# Front contents and back index/appendix (Nanapatha, Lakkhitabbapadanam
# anukkamanika) are NOT the corpus and are not asked to be: check_page_fidelity
# already separates them out as head_pages / tail_pages.  The first cut of this
# sheet read r['rows'], which is the raw printed stream and still holds them, so
# it put 25 back-matter lines in front of the reader -- who caught two of them
# by hand.  Excluded here, and reported rather than dropped.
EDGE = json.load(open('_xc/hy1/edgepg.json')) if os.path.exists('_xc/hy1/edgepg.json') else {}


def on_edge(vol, pg):
    e = EDGE.get(vol) or {}
    for k in ('head', 'tail'):
        r = e.get(k)
        if r and r[0] <= pg <= r[1]:
            return True
    return False

cands, dropped = [], []
for f in sorted(os.listdir('_xc/hy1/cen')):
    j = json.load(open('_xc/hy1/cen/' + f))
    for pg, ind, verdict, text in j.get('page_verse_hyphen', []):
        if PEY.search(text.rstrip()):
            continue                      # a complete token, not a word break
        if on_edge(j['vol'], pg):
            dropped.append((j['vol'], pg, verdict, text))
            continue
        cands.append(dict(vol=j['vol'], pg=pg, ind=ind, verdict=verdict, text=text))

by_vol = collections.defaultdict(list)
for c in cands:
    by_vol[c['vol']].append(c)

items = []
for vol in sorted(by_vol):
    st = pline.stream(vol)
    idx = collections.defaultdict(list)
    for i, l in enumerate(st):
        idx[l[0]].append(i)
    for c in by_vol[vol]:
        page = idx.get(c['pg'], [])
        hit = None
        for i in page:
            if st[i][3].rstrip().endswith('-') and st[i][3][:40] == c['text'][:40]:
                hit = i
                break
        if hit is None:
            for i in page:
                if st[i][3][:40] == c['text'][:40]:
                    hit = i
                    break
        if hit is None:
            c['ctx'] = []
            items.append(c)
            continue
        lo = max(page[0], hit - CTX)
        hi = min(page[-1], hit + CTX)
        c['ctx'] = [[st[i][2], st[i][3], i == hit, i == hit + 1]
                    for i in range(lo, hi + 1)]
        c['page_lines'] = len(page)
        items.append(c)

json.dump(items, open('_xc/hy1/review.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(dropped, open('_xc/hy1/review_dropped.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('back matter excluded: %d (see review_dropped.json)' % len(dropped))
print('candidates: %d across %d volumes' % (len(items), len(by_vol)))
print('with page context recovered: %d' % sum(1 for c in items if c['ctx']))
