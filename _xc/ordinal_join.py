#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STEP 2: DOES THE STATED ORDINAL AGREE WITH THE LINK ALREADY IN THE FILE,
AND DOES IT BEAT ITS OWN FLOOR?

The commentary states which sutta of its vagga it glosses.  The canon side
already carries that number: `sutta_n` is the sutta's position in its vagga.
So for every canon->commentary link, two independent numbers can be compared.

THE FLOOR IS NOT OPTIONAL.  `sutta_n` runs 1..10 over most of the Aṅguttara,
so agreement by chance is not small.  Every rate is printed beside the same
test against the canon paragraph FAR places away, and beside the rate expected
from the observed distribution of sutta_n alone.

AND THE CROSS-CHECK IS A CRITERION THE ORDINAL CANNOT SEE: links carrying
`by: name` were placed by the 2026-08-02 name repair, which knows nothing of
these words.  Agreement there is the validation; disagreement there is a
warning about this route, not about the name repair.

Usage:  python3 _xc/ordinal_join.py [--far 25]
Writes nothing.
"""
import json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import ordinal_words as ordinal

SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
FAR = 25
for i, a in enumerate(sys.argv):
    if a == '--far':
        FAR = int(sys.argv[i + 1])

_cache = {}
def vol(v):
    if v not in _cache:
        try:
            _cache[v] = json.load(open(os.path.join(SITE, v + '.json'), encoding='utf-8')).get('paragraphs') or []
        except IOError:
            _cache[v] = []
    return _cache[v]

def sn(p):
    try:
        return int(p.get('sutta_n'))
    except (TypeError, ValueError):
        return None

def key_idx(k):
    v, _, i = k.partition('#')
    return v, int(i)

S = collections.defaultdict(lambda: collections.Counter())
sn_dist = collections.Counter()
perv = collections.defaultdict(lambda: collections.Counter())

for f in sorted(os.listdir(LINKS)):
    if not f.endswith('.links.json'):
        continue
    cv = f[:-len('.links.json')]
    cps = vol(cv)
    if not cps:
        continue
    links = json.load(open(os.path.join(LINKS, f), encoding='utf-8'))
    for si, rec in links.items():
        i = int(si)
        if i >= len(cps):
            continue
        for layer in ('commentary', 'subcommentary'):
            for ent in rec.get(layer) or []:
                tv, ti = key_idx(ent['key'])
                tps = vol(tv)
                if ti >= len(tps):
                    continue
                o, _g, _w = ordinal.read(tps[ti].get('text', ''))
                if o is None:
                    continue
                a = sn(cps[i])
                if a is None:
                    continue
                sn_dist[a] += 1
                buckets = ['ALL', layer, 'state:' + str(ent.get('state')),
                           'by:' + str(ent.get('by')), 'vol:' + cv]
                far = []
                for d in (-FAR, FAR):
                    j = i + d
                    if 0 <= j < len(cps):
                        b = sn(cps[j])
                        if b is not None:
                            far.append(b == o)
                for bk in buckets:
                    tgt = perv[bk] if bk.startswith('vol:') else S[bk]
                    tgt['n'] += 1
                    tgt['hit'] += (a == o)
                    tgt['far_n'] += len(far)
                    tgt['far_hit'] += sum(far)

def line(name, c):
    if not c['n']:
        return
    fl = 100.0 * c['far_hit'] / c['far_n'] if c['far_n'] else float('nan')
    hi = 100.0 * c['hit'] / c['n']
    print('%-22s n=%6d   agree %5.1f%%   floor(shift %d) %5.1f%%   margin %+5.1f'
          % (name, c['n'], hi, FAR, fl, hi - fl))

tot = sum(sn_dist.values())
chance = 100.0 * sum((v / tot) ** 2 for v in sn_dist.values()) if tot else 0
print('canon-side sutta_n distribution over the tested links: %d values, '
      'top %s' % (tot, sn_dist.most_common(5)))
print('agreement expected from that distribution alone: %.1f%%\n' % chance)
for k in ['ALL', 'commentary', 'subcommentary']:
    line(k, S[k])
print()
for k in sorted(S):
    if k.startswith(('state:', 'by:')):
        line(k, S[k])
print('\nper canon volume (>=100 tested):')
for k, c in sorted(perv.items(), key=lambda x: -x[1]['n']):
    if c['n'] >= 100:
        line(k, c)
