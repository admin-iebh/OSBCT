#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Each paragraph's printed page RANGE, so a badge never hides a page turn.

`printed` is the folio of the page a paragraph BEGINS on, and in the canon that
is the whole story — 06Di01 averages 2.4 paragraphs to a printed page.  In the
Ṭīkā it is not: 08DiT01 holds a paragraph that runs across **49 printed pages**,
and a badge reading `p.34` on it silently swallows pages 35-51.

So the LAST page is measured too, by locating the paragraph's closing words in
the printed text (`_seam/<VOL>.txt`, the same bytes `extract.py` read).  The
result is written only where it differs from `printed`, so the map stays small
and a volume with short paragraphs contributes nothing.

SELF-CHECKING, three ways, and a paragraph that fails any of them is left out
rather than guessed at:
  * the closing words must occur on exactly ONE page of the volume;
  * that page must not precede the paragraph's own start page;
  * it must not pass the NEXT paragraph's start page.

Output: `site/reader/pagespan.json` = {VOL: {ord: last_printed_page}}.
Usage: python3 pipeline/build_pagespan.py [VOL…] [--write]
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT + '/pipeline')
import extract as E
# WHITESPACE **AND HYPHENS** ARE DROPPED FROM BOTH SIDES.  The builder joins a
# line-end hyphen (`hyjoin`) and the edition also hyphenates inside a word, so a
# tail can differ from the printed page by nothing but a `-`.  Removing it on
# BOTH sides cannot create a false match that the whitespace rule did not
# already allow.  Measured: 06Di01's unresolved paragraphs 142 -> 3.
sq = lambda t: re.sub(r'[\s\u00ad-]+', '', t or '')

def pdf_of(v):
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = '%s/%s/%s.pdf' % (ROOT, d, v)
        if os.path.exists(p): return p

args = [a for a in sys.argv[1:] if not a.startswith('--')]
vols = args or sorted(f[:-5] for f in os.listdir(ROOT + '/site') if f.endswith('.json'))
out, tot, skipped = {}, 0, 0
for vol in vols:
    try:
        ps = json.load(open('%s/site/%s.json' % (ROOT, vol), encoding='utf-8'))['paragraphs']
    except Exception:
        continue
    t = '%s/_seam/%s.txt' % (ROOT, vol)
    pages = (open(t, encoding='utf-8').read().split('\f') if os.path.exists(t)
             else E.raw_pages(pdf_of(vol)))
    # printed folio of every page, read from the running header
    folio = {}
    for i, pg in enumerate(pages, 1):
        f, _ = E.parse_header(next((l for l in pg.split('\n') if l.strip()), ''))
        if isinstance(f, int): folio[i] = f
    # !!! NOT EVERY PAGE'S HEADER PARSES AS A FOLIO — a title page, a book head
    # or a page whose header the parser cannot read carries none, and 06Di01
    # lost 142 paragraphs to `folio.get(...) is None` before this.  The folios
    # are consecutive, so one is derived by walking back to the nearest page
    # that has one and adding the difference.  Exact, not interpolated.
    def fol(i):
        for j in range(i, 0, -1):
            if j in folio:
                return folio[j] + (i - j)
        return None
    sqp = [sq(x) for x in pages]
    m, miss = {}, 0
    for o, p in enumerate(ps):
        txt = p.get('text') or ''
        pr = p.get('printed')
        if not isinstance(pr, int) or len(txt) < 400:
            continue                       # short paragraph: it cannot span
        # THE SEARCH IS BOUNDED BELOW BY THE PARAGRAPH'S OWN START PAGE, which
        # removes almost all ambiguity: a formula that recurs through a volume
        # is unique once the pages before this paragraph are out of scope.
        # And the tail is tried at three lengths, because the final 60
        # characters can straddle the page break itself and then match no
        # single page at all — 06Di01 lost 169 paragraphs to that before the
        # shorter windows were added, and loses 3 after.
        start = next((i for i, f in folio.items() if f == pr), 1)
        last = None
        for w in (60, 40, 25):
            tail = sq(txt)[-w:]
            hits = [i for i in range(start, len(sqp) + 1) if tail in sqp[i - 1]]
            if len(hits) == 1:
                last = fol(hits[0]); break
        if last is None:
            miss += 1; continue
        nxt = next((ps[k].get('printed') for k in range(o + 1, len(ps))
                    if isinstance(ps[k].get('printed'), int)), None)
        if last is None or last < pr or (nxt is not None and last > nxt):
            miss += 1; continue
        if last > pr:
            m[str(o)] = last
    skipped += miss
    if m:
        out[vol] = m; tot += len(m)
        widest = max(m.items(), key=lambda kv: kv[1] - ps[int(kv[0])]['printed'])
        w = widest[1] - ps[int(widest[0])]['printed']
        print('%-10s %4d ¶  %4d span >1 page (widest ord%s: p.%d-%d, %d pages)  %d unresolved'
              % (vol, len(ps), len(m), widest[0], ps[int(widest[0])]['printed'], widest[1], w + 1, miss))
print('\n%d volume(s), %d paragraph(s) with a page RANGE, %d left out as unresolved'
      % (len(out), tot, skipped))
if '--write' in sys.argv:
    p = ROOT + '/site/reader/pagespan.json'
    # !!! A PARTIAL RUN MUST MERGE, NOT REPLACE.  Naming two volumes on the
    # command line and writing `out` alone dropped the other 112 from the map —
    # 193 KB down to 3 KB — and nothing would have said so: the reader simply
    # stops showing page ranges for every volume that was not named.  Found
    # immediately after doing exactly that, 2026-07-29u.
    if args and os.path.exists(p):
        prev = json.load(open(p, encoding='utf-8'))
        prev.update(out)
        out = prev
        print('   merged into the existing map: %d volume(s) in all' % len(out))
    json.dump(out, open(p, 'w'), ensure_ascii=False)
    print('wrote %s (%d KB)' % (p, os.path.getsize(p) // 1024))
else:
    print('DRY RUN — pass --write')
