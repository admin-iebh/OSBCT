#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per-volume list of BLANK PDF pages, so the reader's page link opens the right
leaf of the file.

WHY THIS EXISTS.  `extract.py` numbers `pdf_page` AFTER dropping blank pages
(2026-07-29p), so the corpus field is the index among NON-BLANK pages, not the
index in the file.  The reader writes

    <a href="…/<VOL>.pdf#page={pdf_page}">p.{printed}</a>

and on a volume with a blank verso before body pages that anchor is short by the
number of blanks above it — measured 2026-07-29t over all 118 volumes,
**40 are wrong, by up to 11 pages** (40Abhi12), and 78 are exact.  The `printed`
label itself is right everywhere: it is parsed from the running header.

THE CORPUS IS NOT TOUCHED.  The user's decision of 2026-07-29q stands — the
drift is left in place and converted where it is used.  This is that conversion,
for the one consumer that had never had it.

    true page = corpus page + (number of blanks at or below the true page)

which the reader walks as: for each blank b in ascending order, if b <= t then
t += 1.

Output: `site/reader/pdfblanks.json` = {VOL: [blank true-page indices]}, omitting
every volume with none.  Usage: python3 pipeline/build_pdfblanks.py [--write]
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT + '/pipeline')
import extract as E

def pdf_of(v):
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = '%s/%s/%s.pdf' % (ROOT, d, v)
        if os.path.exists(p): return p

vols = sorted(f[:-5] for f in os.listdir(ROOT + '/site') if f.endswith('.json'))
out, worst = {}, []
for vol in vols:
    try:
        d = json.load(open('%s/site/%s.json' % (ROOT, vol), encoding='utf-8'))
        ps = d['paragraphs']
    except Exception:
        continue
    t = '%s/_seam/%s.txt' % (ROOT, vol)
    pages = (open(t, encoding='utf-8').read().split('\f') if os.path.exists(t)
             else E.raw_pages(pdf_of(vol)))
    blanks = [i + 1 for i, x in enumerate(pages) if not E.split_page(x)]
    # only the blanks that can move a BODY page matter; keep them all anyway,
    # the list is a handful of integers and a trailing one is inert.
    if not blanks:
        continue
    last = max(p['pdf_page'] for p in ps if isinstance(p.get('pdf_page'), int))
    shift = sum(1 for b in blanks if b <= last + len(blanks))
    if shift:
        out[vol] = blanks
        worst.append((shift, vol))
worst.sort(reverse=True)
print('%d of %d volume(s) need an offset; worst: %s'
      % (len(out), len(vols), ', '.join('%s +%d' % (v, s) for s, v in worst[:6])))
if '--write' in sys.argv:
    p = ROOT + '/site/reader/pdfblanks.json'
    json.dump(out, open(p, 'w'), ensure_ascii=False)
    print('wrote %s (%d bytes)' % (p, os.path.getsize(p)))
else:
    print('DRY RUN — pass --write')
