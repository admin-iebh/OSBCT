# -*- coding: utf-8 -*-
"""Per-volume BLOCK GAP: how much extra leading the edition puts before a new
block (paragraph or stanza), measured, not assumed.

+6.0pt is the commonest value and it is NOT universal: 23Khu06 sets 10.0, and
21Khu04 separates its stanzas with a whole skipped line (gap == body leading)
while still using 6.0 elsewhere.  So the constant is measured per volume the same
self-verifying way `display_column_pages` measures its column -- from the
distribution's own second mode -- and a volume whose distribution has no clear
second mode is reported as UNSET rather than given a default.

Resumable: one row per volume, --budget seconds.
"""
import sys, os, json, collections, random, subprocess, re, time
sys.path.insert(0, os.path.abspath('_xc/hy1'))
from lead import page_lines, leads

OUT = '_xc/hy1/blockgap.json'
NPAGE = 14
random.seed(5)
done = json.load(open(OUT)) if os.path.exists(OUT) else {}
vols = []
for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith('.pdf'):
                vols.append((f[:-4], d + '/' + f))
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 400
t0 = time.time()
for vol, src in vols:
    if vol in done:
        continue
    if time.time() - t0 > budget:
        print('BUDGET -- %d done, %d left' % (len(done), len(vols) - len(done))); break
    try:
        npg = int(re.search(r'Pages:\s+(\d+)', subprocess.run(
            ['pdfinfo', src], capture_output=True).stdout.decode()).group(1))
    except Exception:
        continue
    lo, hi = max(1, npg // 8), max(2, npg - npg // 8)
    gaps, bodies, npages = collections.Counter(), [], 0
    for p in sorted(random.sample(range(lo, hi), min(NPAGE, hi - lo))):
        try:
            rows = page_lines(src, p)
        except Exception:
            continue
        L = [g for g in leads(rows) if 5 < g < 80]
        if len(L) < 8:
            continue
        npages += 1
        base = collections.Counter(L).most_common(1)[0][0]
        bodies.append(base)
        for g in L:
            d = round(g - base, 1)
            if 2.0 < d < 30.0:
                gaps[d] += 1
    if not gaps:
        done[vol] = {'gap': None, 'why': 'no gaps', 'pages': npages}
    else:
        # cluster to 0.5pt so +5.9/+6.0/+6.1 count as one mode
        cl = collections.Counter(round(d * 2) / 2.0 for d in gaps.elements())
        (g1, n1), = cl.most_common(1)
        tot = sum(cl.values())
        n2 = max([n for g, n in cl.items() if abs(g - g1) > 1.0] or [0])
        done[vol] = {'gap': g1, 'share': round(n1 / tot, 3), 'runner_up': n2,
                     'body_med': sorted(bodies)[len(bodies) // 2] if bodies else None,
                     'pages': npages, 'gaps': n1}
    json.dump(done, open(OUT, 'w'), indent=0)
    d = done[vol]
    print('%-10s gap %-6s share %-6s body %-6s pages %2d' %
          (vol, d.get('gap'), d.get('share'), d.get('body_med'), d.get('pages')), flush=True)
print('TOTAL %d / %d' % (len(done), len(vols)))
