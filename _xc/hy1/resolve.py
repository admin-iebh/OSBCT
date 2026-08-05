# -*- coding: utf-8 -*-
"""Resolve each candidate to the two page numbers a human needs.

`pline`'s page index is neither the pdftotext page nor the number printed on the
page.  It is anchored to the text extent the PDF declares in its `Subject`, and
the anchor differs per volume: on 07DiA01 pline page == pdftotext page, on
07ViT07 pline 507 == pdftotext 509 == PRINTED 488.  The first sheet labelled the
pline index 'PDF p', so the reader went looking for p507 and found the wrong
page.  Resolved here by LOCATING the candidate's own text, not by arithmetic.
"""
import sys, os, json, re
sys.path.insert(0, os.path.abspath('pipeline'))
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import extract, pline

# raw_pages returns the LEGACY VZTimes bytes, not Unicode, so a diacritic on
# either side is a different character.  Match on the ASCII SKELETON -- drop
# every non-ASCII-letter from both -- which survives the encoding difference.
SKEL = re.compile(r'[^A-Za-z]')
n = lambda s: SKEL.sub('', s or '')
# the printed number sits in the running head, alternating left and right
HEADNUM = re.compile(r'^\s*(\d{1,4})\s+\S|\S\s+(\d{1,4})\s*$')

items = json.load(open('_xc/hy1/review.json', encoding='utf-8'))
cache, out = {}, {}
for c in items:
    vol, pg = c['vol'], c['pg']
    if (vol, pg) in out:
        continue
    if vol not in cache:
        cache[vol] = extract.raw_pages(
            next(p for p in ('pali/%s.pdf', 'atthakatha/%s.pdf', 'tika/%s.pdf')
                 if os.path.exists(p % vol)) % vol)
    pgs = cache[vol]
    key = n(c['text'])[:24]
    idx = [i for i, p in enumerate(pgs) if key and key in n(p)]
    pdfpage = idx[0] + 1 if idx else None
    printed = None
    if pdfpage:
        head = [l for l in pgs[pdfpage - 1].split('\n') if l.strip()][:1]
        if head:
            m = HEADNUM.match(head[0])
            if m:
                printed = int(m.group(1) or m.group(2))
    out[(vol, pg)] = {'pdftotext': pdfpage, 'printed': printed}
    print('%-10s pline p%-5d -> pdftotext p%-5s printed %s'
          % (vol, pg, pdfpage, printed), flush=True)
json.dump({'%s|%d' % k: v for k, v in out.items()},
          open('_xc/hy1/pagemap.json', 'w'), indent=1)
