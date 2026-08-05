# -*- coding: utf-8 -*-
"""The four volumes that showed no +6.0 mode in leadcensus2, sampled properly.

They were sampled at TWO pages each there, so absence was very likely sampling.
Genuine absence would be a finding, so it is tested rather than assumed: 40 pages
each, spread across the volume's text extent."""
import sys, os, collections, random, subprocess, re
sys.path.insert(0, os.path.abspath('_xc/hy1'))
from lead import page_lines, leads

random.seed(101)
VOLS = ['07Di02', '21Khu04', '23Khu06', '26KhuA07']
for vol in VOLS:
    src = next(p for p in ('pali-unicode/%s.pdf', 'atthakatha-unicode/%s.pdf',
                           'tika-unicode/%s.pdf') if os.path.exists(p % vol)) % vol
    npg = int(re.search(r'Pages:\s+(\d+)', subprocess.run(
        ['pdfinfo', src], capture_output=True).stdout.decode()).group(1))
    lo, hi = max(1, npg // 8), max(2, npg - npg // 8)
    pages = sorted(random.sample(range(lo, hi), min(40, hi - lo)))
    gaps, npages = collections.Counter(), 0
    for p in pages:
        try:
            rows = page_lines(src, p)
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
                gaps[d] += 1
    tot = sum(gaps.values())
    six = sum(n for d, n in gaps.items() if 5.0 <= d <= 7.0)
    print('%-10s pages %2d   gaps %4d   at body+6.0+/-1.0 : %4d (%.1f%%)   top: %s'
          % (vol, npages, tot, six, 100.0 * six / max(1, tot),
             [('%+.1f' % d, n) for d, n in gaps.most_common(4)]), flush=True)
