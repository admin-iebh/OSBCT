# -*- coding: utf-8 -*-
"""Refines leadcensus.py, whose statistic was wrong.

That run took each page's SECOND MODE and asked if it was +6.0.  On a page whose
only break is a heading gap there is no paragraph break to find, so it scored the
heading and counted as a miss -- which is why it reported 52% and listed pages
with deltas of +15 to +26.  Those are not counterexamples, they are pages with no
paragraph on them.

The right question is per GAP, not per page: of all inter-line gaps larger than
the body leading, how many sit at body+6, and does every volume show that mode?"""
import os, sys, random, collections, json, time, subprocess, re
sys.path.insert(0, os.path.abspath('_xc/hy1'))
from lead import page_lines, leads

random.seed(23)
vols = []
for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith('.pdf'):
                vols.append((f[:-4], d + '/' + f))
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 400
t0 = time.time()
allgaps, byvol, npages = collections.Counter(), collections.defaultdict(collections.Counter), 0
for vol, path in vols:
    if time.time() - t0 > budget:
        print('BUDGET after %d volumes' % len(byvol)); break
    try:
        npg = int(re.search(r'Pages:\s+(\d+)', subprocess.run(
            ['pdfinfo', path], capture_output=True).stdout.decode()).group(1))
    except Exception:
        continue
    for p in random.sample(range(max(1, npg // 6), max(2, npg - npg // 6)), min(2, max(1, npg - 2))):
        try:
            rows = page_lines(path, p)
        except Exception:
            continue
        L = [g for g in leads(rows) if 5 < g < 80]
        if len(L) < 8:
            continue
        npages += 1
        base = collections.Counter(L).most_common(1)[0][0]
        for g in L:
            d = round(g - base, 1)
            if d > 2.0:
                allgaps[d] += 1
                byvol[vol][d] += 1
print('pages %d   volumes %d   gaps above body leading %d' % (npages, len(byvol), sum(allgaps.values())))
print()
print('gap size above body leading:')
for d, n in allgaps.most_common(8):
    print('   %+5.1f pt  %5d  %s' % (d, n, '#' * int(60.0 * n / max(allgaps.values()))))
tot = sum(allgaps.values())
six = sum(n for d, n in allgaps.items() if 5.0 <= d <= 7.0)
print()
print('at body+6.0 +/- 1.0 : %d / %d gaps  (%.1f%%)' % (six, tot, 100.0 * six / max(1, tot)))
have = [v for v, c in byvol.items() if any(5.0 <= d <= 7.0 for d in c)]
print('volumes showing the +6.0 mode at all : %d / %d' % (len(have), len(byvol)))
miss = [v for v in byvol if v not in have]
print('volumes NOT showing it : %s' % (miss if miss else 'none'))
json.dump({v: dict(c) for v, c in byvol.items()}, open('_xc/hy1/leadcensus2.json', 'w'))
