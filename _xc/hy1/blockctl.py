# -*- coding: utf-8 -*-
"""Controls on the block map.  A check that cannot fail is not a check.

 1. THRESHOLD SWEEP -- if the answer is the same at 1.0 and at 8.0 the threshold
    is doing nothing and the signal is not what is claimed.
 2. SHUFFLE -- shuffle each page's leadings and compare WHICH LINES are marked.
    !! The first version of this control COUNTED the marks, and a count is
    permutation-invariant, so it returned a number identical to the honest run on
    every volume and would have done so on any input whatsoever.  It is scored by
    VERDICTS MOVED, per line, like every other control in this project.
 3. FLAT -- give every line the body leading.  Starts must fall to ~1 per page
    (the first line only).  If not, the rule is firing on something else.
 4. VACUITY -- report any volume where the map finds no block starts at all.
"""
import json, os, sys, random, collections
random.seed(3)
B = '_xc/hy1/blocks2'
vols = sys.argv[1:] or ['06ViT06', '20KhuA01', '12DiT05', '46KhuA27', '29Abhi01', '23Khu06']


def marks(pg, thresh, mode='honest'):
    ys = [l[0] for l in pg['lines']]
    gaps = [ys[i] - ys[i - 1] for i in range(1, len(ys))]
    base = pg['body']
    if mode == 'shuffle':
        random.shuffle(gaps)
    elif mode == 'flat':
        gaps = [base] * len(gaps)
    return [1] + [1 if g > base + thresh else 0 for g in gaps]


def starts(pg, thresh, mode='honest'):
    return sum(marks(pg, thresh, mode))


def moved(pg, thresh, mode):
    a, b = marks(pg, thresh, 'honest'), marks(pg, thresh, mode)
    return sum(1 for x, y in zip(a, b) if x != y)


print('block starts at each threshold, then CONTROLS scored by verdicts moved per line')
print('%-10s %7s %7s %7s %7s | %14s %14s %8s' %
      ('vol', 'th=1', 'th=3', 'th=8', 'th=20', 'shuffle moved', 'flat moved', 'lines'))
for v in vols:
    d = json.load(open('%s/%s.json' % (B, v), encoding='utf-8'))
    cnt = [sum(starts(p, th) for p in d.values()) for th in (1.0, 3.0, 8.0, 20.0)]
    sh = sum(moved(p, 3.0, 'shuffle') for p in d.values())
    fl = sum(moved(p, 3.0, 'flat') for p in d.values())
    nl = sum(len(p['lines']) for p in d.values())
    print('%-10s %7d %7d %7d %7d | %6d (%4.1f%%) %6d (%4.1f%%) %8d'
          % (v, *cnt, sh, 100.0 * sh / nl, fl, 100.0 * fl / nl, nl))
print()
empty = []
for f in sorted(os.listdir(B)):
    d = json.load(open(B + '/' + f, encoding='utf-8'))
    n = sum(sum(l[2] for l in p['lines']) for p in d.values())
    if n == 0:
        empty.append(f[:-5])
print('volumes where the map finds NO block start (vacuous): %s' % (empty or 'none'))
