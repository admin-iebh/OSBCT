#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPEN QUESTION #1: do paragraph numbers align across canon, aṭṭhakathā, ṭīkā?

The project instructions record it as REPORTED and UNVERIFIED — "which would
make them the join key for cross-referencing... test it on samples across all
three layers before designing around it."  It has gated the dictionary and
cross-reference design ever since.

THE TEST.  The corpus already holds a reverse map per non-canon volume:
`site/reader/links/<VOL>.rev.json`, ord -> {canon: 'VOL#ord', state}.  Where
`state == 'direct'` the builder is asserting THIS commentary paragraph comments
on THAT canon paragraph.  So: on those pairs, does the edition's own printed
paragraph number `n` agree on both sides?

If the numbering is shared, agreement should be near-total on `direct` pairs.
If it is not shared, agreement should be no better than chance.

THE CONTROL, which is what makes the answer mean anything.  A commentary
paragraph is compared against the canon paragraph its neighbour links to
(shifted by k places within the same volume pair).  Same volumes, same number
distributions, wrong pairing.  Whatever agreement rate the shift produces is
what coincidence alone buys — the numbers are small integers and repeat often,
so the naive rate is NOT zero and reading it without a control would be the
error the instructions warn against.
"""
import json, glob, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def nmap(vol):
    p = os.path.join(ROOT, 'site', vol + '.json')
    if not os.path.exists(p):
        return None
    return [q.get('n') for q in json.load(open(p, encoding='utf-8'))['paragraphs']]


def run(shift=0, layer_filter=None):
    man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'),
                        encoding='utf-8'))['volumes']
    cache = {}
    per = collections.defaultdict(lambda: [0, 0])          # layer -> [pairs, agree]
    pervol = {}
    for rp in sorted(glob.glob(os.path.join(ROOT, 'site/reader/links/*.rev.json'))):
        vol = os.path.basename(rp)[:-9]
        layer = man.get(vol, {}).get('layer', '?')
        if layer_filter and layer != layer_filter:
            continue
        rev = json.load(open(rp, encoding='utf-8'))
        if vol not in cache:
            cache[vol] = nmap(vol)
        mine = cache[vol]
        if mine is None:
            continue
        items = [(int(o), e) for o, e in rev.items()
                 if e.get('state') == 'direct' and e.get('canon')]
        items.sort()
        n = a = 0
        for i, (o, e) in enumerate(items):
            j = i + shift
            if not (0 <= j < len(items)):
                continue
            cv, co = items[j][1]['canon'].split('#')
            if cv not in cache:
                cache[cv] = nmap(cv)
            other = cache[cv]
            if other is None or not (0 <= o < len(mine)) or not (0 <= int(co) < len(other)):
                continue
            x, y = mine[o], other[int(co)]
            if x is None or y is None:
                continue
            n += 1
            a += (str(x) == str(y))
        if n:
            per[layer][0] += n; per[layer][1] += a
            pervol[vol] = (n, a)
    return per, pervol


if __name__ == '__main__':
    print('paragraph-number agreement on `direct` canon<->layer pairs\n')
    print('%-16s %10s %10s %8s' % ('layer', 'pairs', 'agree', 'rate'))
    real, pervol = run(0)
    for lay in sorted(real):
        n, a = real[lay]
        print('%-16s %10d %10d %7.1f%%' % (lay, n, a, 100.0 * a / n))
    print('\nCONTROL — same pairs, canon side shifted by k within the volume:')
    for k in (1, 2, 5, 25):
        ctl, _ = run(k)
        line = '  shift %-3d' % k
        for lay in sorted(real):
            n, a = ctl.get(lay, (0, 0))
            line += '  %s %5.1f%%' % (lay[:4], (100.0 * a / n) if n else 0.0)
        print(line)
    print('\nworst and best volumes (real pairing):')
    rows = sorted(pervol.items(), key=lambda kv: kv[1][1] / max(kv[1][0], 1))
    for v, (n, a) in rows[:5] + rows[-5:]:
        print('   %-12s %6d pairs %6.1f%%' % (v, n, 100.0 * a / n))
