#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STEP 1: HOW MUCH OF THE CORPUS STATES ITS OWN ORDINAL, AND DOES IT AGREE
WITH THE STRUCTURE ALREADY PARSED?

Writes nothing.  Prints two tables.
"""
import json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import ordinal_words as ordinal

SITE = os.path.join(ROOT, 'site')
VOL = re.compile(r'^\d\d[A-Za-z][A-Za-z0-9]*\.json$')

vols = sorted(f[:-5] for f in os.listdir(SITE) if VOL.match(f))
rows, tot = [], collections.Counter()
for v in vols:
    d = json.load(open(os.path.join(SITE, v + '.json'), encoding='utf-8'))
    ps = d.get('paragraphs') or []
    n = st = agree = dis = nosn = gen = 0
    for p in ps:
        n += 1
        o, g, _ = ordinal.read(p.get('text', ''))
        if g is not None:
            gen += 1
        if o is None:
            continue
        st += 1
        sn = p.get('sutta_n')
        try:
            sn = int(sn)
        except (TypeError, ValueError):
            sn = None
        if sn is None:
            nosn += 1
        elif sn == o:
            agree += 1
        else:
            dis += 1
    rows.append((v, n, st, agree, dis, nosn, gen))
    for k, x in zip('n st agree dis nosn gen'.split(), (n, st, agree, dis, nosn, gen)):
        tot[k] += x

rows.sort(key=lambda r: -r[2])
print('%-12s %6s %6s %5s   %6s %6s %6s' % ('vol', 'paras', 'stated', '%', 'agree', 'DISAG', 'no_sn'))
for v, n, st, a, dis, nosn, g in rows:
    if st:
        print('%-12s %6d %6d %4.1f%%   %6d %6d %6d' % (v, n, st, 100.0 * st / n, a, dis, nosn))
print('-' * 58)
print('%-12s %6d %6d %4.1f%%   %6d %6d %6d' % ('TOTAL', tot['n'], tot['st'],
      100.0 * tot['st'] / max(tot['n'], 1), tot['agree'], tot['dis'], tot['nosn']))
d = tot['agree'] + tot['dis']
if d:
    print('\nstated ordinal vs the volume\'s own parsed sutta_n: %.1f%% agree (%d of %d decidable)'
          % (100.0 * tot['agree'] / d, tot['agree'], d))
print('paragraphs stating a genitive containing-unit ordinal: %d' % tot['gen'])
