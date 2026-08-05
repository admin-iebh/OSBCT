# -*- coding: utf-8 -*-
"""Is 'block break = body leading + 6.0pt' a property of the edition, or of six
pages?  Sample pages across every volume and test it.

Reported as a DISTRIBUTION, not a yes/no: the claim is only worth having if the
second mode is separated from the first by a constant, on volumes chosen without
reference to the six that suggested it."""
import os, sys, random, collections, json
sys.path.insert(0, os.path.abspath('_xc/hy1'))
from lead import page_lines, leads

random.seed(7)
FOLD = ('pali-unicode', 'atthakatha-unicode', 'tika-unicode')
vols = []
for d in FOLD:
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith('.pdf'):
                vols.append((f[:-4], d + '/' + f))
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 400
import time
t0 = time.time()
deltas, per, bad = collections.Counter(), [], []
for vol, path in vols:
    if time.time() - t0 > budget:
        break
    try:
        import subprocess, re
        npg = int(re.search(r'Pages:\s+(\d+)', subprocess.run(
            ['pdfinfo', path], capture_output=True).stdout.decode()).group(1))
    except Exception:
        continue
    for p in random.sample(range(max(1, npg // 6), max(2, npg - npg // 6)), min(3, max(1, npg - 2))):
        try:
            rows = page_lines(path, p)
        except Exception:
            continue
        L = [g for g in leads(rows) if 5 < g < 45]
        if len(L) < 8:
            continue
        c = collections.Counter(L)
        base = c.most_common(1)[0][0]
        brks = [g for g in L if g > base + 2.5]
        if not brks:
            continue
        # the SECOND mode, not the max: the max is a heading gap
        b2 = collections.Counter(round(g - base, 1) for g in brks).most_common(1)[0][0]
        deltas[b2] += 1
        per.append((vol, p, base, b2))
        if not (5.0 <= b2 <= 7.0):
            bad.append((vol, p, base, b2))
print('pages measured: %d   volumes: %d' % (len(per), len({v for v, *_ in per})))
print()
print('delta (break leading - body leading), commonest values:')
for d, n in deltas.most_common(10):
    print('   %+5.1f pt   %4d pages%s' % (d, n, '   <-- ' if 5.0 <= d <= 7.0 else ''))
tot = sum(deltas.values())
inb = sum(n for d, n in deltas.items() if 5.0 <= d <= 7.0)
print()
print('within 6.0 +/- 1.0 pt : %d / %d  (%.1f%%)' % (inb, tot, 100.0 * inb / max(1, tot)))
print('outside               : %d' % len(bad))
for v, p, b, d in bad[:12]:
    print('   %-10s p%-5d body %.1f  delta %+.1f' % (v, p, b, d))
json.dump(per, open('_xc/hy1/leadcensus.json', 'w'))
