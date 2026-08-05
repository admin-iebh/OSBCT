# -*- coding: utf-8 -*-
"""Locate a pline page in the raw pdftotext pages ROBUSTLY.

resolve.py matched ONE line's ASCII skeleton.  That is fine when the line is
distinctive and wrong when it is not: '1. Kusalā kusalā dhammā' occurs both on
35Abhi07's first text page and in its front-matter contents, so the single-line
match returned the contents page and the render showed the wrong thing twice.

Score every raw page by HOW MANY of the pline page's line skeletons it contains,
and require the winner to beat the runner-up.  A page is 20-30 lines; a contents
page will share one or two, the real page shares nearly all."""
import sys, os, re
sys.path.insert(0, os.path.abspath('pipeline'))
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import extract, pline

SKEL = re.compile(r'[^A-Za-z]')
n = lambda s: SKEL.sub('', s or '')
HEADNUM = re.compile(r'^\s*(\d{1,4})\s+\S|\S\s+(\d{1,4})\s*$')
_cache = {}


def src_of(vol):
    return next(p for p in ('pali-unicode/%s.pdf', 'atthakatha-unicode/%s.pdf',
                            'tika-unicode/%s.pdf') if os.path.exists(p % vol)) % vol


def locate(vol, plpg):
    if vol not in _cache:
        _cache[vol] = (extract.raw_pages(src_of(vol)),
                       [n(p) for p in extract.raw_pages(src_of(vol))])
    pgs, npgs = _cache[vol]
    keys = [n(l[3])[:22] for l in pline.stream(vol) if l[0] == plpg]
    keys = [k for k in keys if len(k) >= 14]
    if not keys:
        return None, None, 0, 0
    sc = [(sum(1 for k in keys if k in npgs[i]), i) for i in range(len(pgs))]
    sc.sort(reverse=True)
    best, second = sc[0], (sc[1] if len(sc) > 1 else (0, -1))
    pdfp = best[1] + 1
    printed = None
    h = [l for l in pgs[best[1]].split('\n') if l.strip()][:1]
    if h:
        m = HEADNUM.match(h[0])
        if m:
            printed = int(m.group(1) or m.group(2))
    return pdfp, printed, best[0], second[0]


if __name__ == '__main__':
    for a in sys.argv[1:]:
        vol, pg = a.split(':')
        p, pr, b, s = locate(vol, int(pg))
        print('%-10s pline p%-5s -> pdftotext p%-5s printed %-6s  matched %d of page, runner-up %d'
              % (vol, pg, p, pr, b, s))
