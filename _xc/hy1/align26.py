# -*- coding: utf-8 -*-
"""What is the 1.78% the block-map/pline join does not align?

18AnA02's residue is the edition's own WORD INDEX -- two columns of
`headword  page  headword  page` -- which `-layout` renders as one line and the
bbox word order does not.  That is back matter, and the question is whether
check_page_fidelity's tail detector simply failed to cover it on these volumes.

A line is called index-like if it holds two or more runs of 2+ spaces AND at
least two bare numbers: that is the two-column shape and not ordinary prose.
"""
import json, os, sys, re, collections
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import pline

IDX = re.compile(r'\s{2,}')
NUM = re.compile(r'(?<!\S)\d{1,4}(?!\S)')
# edge2.json, not edgepg.json: the latter held only head/tail, and
# check_page_fidelity does not find these volumes' word index as a TAIL at all --
# it names it an interior gap matching INDEXRE and subtracts it as `index_lines`.
# 18AnA02 reports tail_pages None and edge 3316 in the same line.
edge = json.load(open('_xc/hy1/edge2.json'))


def isedge(e, p):
    e = e or {}
    for k in ('head', 'tail'):
        r = e.get(k)
        if r and r[0] <= p <= r[1]:
            return True
    for lo, hi in e.get('index', ()):
        if lo <= p <= hi:
            return True
    return False


def indexlike(t):
    return len(IDX.findall(t)) >= 2 and len(NUM.findall(t)) >= 2


rows = []
for f in sorted(os.listdir('_xc/hy1/bjoin2')):
    vol = f[:-5]
    e = edge.get(vol)
    s = pline.stream(vol)
    jj = json.load(open('_xc/hy1/bjoin2/' + f, encoding='utf-8'))
    tot = ok = 0
    bad = []
    for i, l in enumerate(s):
        if isedge(e, l[0]) or l[0] <= 3:
            continue
        tot += 1
        if jj[i] and jj[i][1] != 'unaligned':
            ok += 1
        else:
            bad.append(i)
    if not tot:
        continue
    rate = 100.0 * ok / tot
    if rate >= 99.0:
        continue
    ix = sum(1 for i in bad if indexlike(s[i][3]))
    pgs = sorted({s[i][0] for i in bad if indexlike(s[i][3])})
    rows.append((vol, round(rate, 2), len(bad), ix, len(bad) - ix,
                 (min(pgs), max(pgs)) if pgs else None,
                 (e or {}).get('tail')))
print('%-10s %6s %6s %8s %8s  %-14s %s' %
      ('vol', 'rate', 'unaln', 'index', 'other', 'index pages', 'tail_pages says'))
for r in rows:
    print('%-10s %6.2f %6d %8d %8d  %-14s %s' % r)
print()
print('volumes below 99%%: %d' % len(rows))
print('unaligned body lines in them: %d, of which index-like %d (%.1f%%)'
      % (sum(r[2] for r in rows), sum(r[3] for r in rows),
         100.0 * sum(r[3] for r in rows) / max(1, sum(r[2] for r in rows))))
