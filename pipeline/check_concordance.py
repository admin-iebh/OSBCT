#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does a cross-layer link stay inside the volumes the concordance allows?

WHY THIS EXISTS.  `site/concordance.json` is the edition's own volume-level map
of canon -> commentary -> subcommentary, hand-verified against the printed
`concordanciatextos.pdf`.  It says, for example, that Apadāna I (`20Khu03`) is
commented on by `32KhuA13` and nothing else, and that Dhammasaṅgaṇī's
subcommentary is `22AbhiT01`.  Nothing had ever checked the links against it.

3,163 of 67,323 link targets -- 4.7% -- point at a volume the concordance does
not pair with that canon volume, and the pattern is the signature of the
monotonic number walk running past a volume boundary: `20Khu03` reaches
`33KhuA14`, the commentary on Apadāna **II**; `22Khu05` (Jātaka I) reaches
`40KhuA21`, the commentary on Jātaka **II**; `29Abhi01` and `32Abhi04` reach
each other's subcommentaries.

TWO KINDS, AND THEY ARE NOT THE SAME FAULT:

  outside      the concordance names volumes for this layer and the target is
               not among them.  A wrong volume -- the link's paragraph may be
               fine, its volume is not.
  no such      the concordance names NO volume for this layer: the edition says
  layer        this canon volume has no commentary (or no subcommentary) at all.
               A link there is not mis-aimed, it is manufactured -- the same
               family as the targets removed in `6f7e5629`.

THIS IS NOT A REBUILD.  `build_links_bynum.py` recorded that a full rebuild
constrained by the concordance LOST on both axes at once.  This asserts an
invariant and counts the violations; it moves nothing.

WHY A RATCHET.  Some violations may yet prove legitimate -- the concordance is
volume-level and the relation is many-to-many -- so a zero is not claimed to be
available.  This records the current numbers and fails when they get worse.

Usage:
  python3 pipeline/check_concordance.py
  python3 pipeline/check_concordance.py --record
  python3 pipeline/check_concordance.py --detail
Exit 0 = no measure regressed.
"""
import json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
BASE = os.path.join(HERE, 'concordance_baseline.json')
LAYERS = ('commentary', 'subcommentary')


def allowed():
    c = json.load(open(os.path.join(SITE, 'concordance.json'), encoding='utf-8'))
    a = collections.defaultdict(lambda: {l: set() for l in LAYERS})
    seen = collections.defaultdict(lambda: {l: False for l in LAYERS})
    for g in c['groups']:
        for f in (g.get('canon') or {}).get('files') or []:
            for l in LAYERS:
                a[f][l] |= set((g.get(l) or {}).get('files') or [])
                seen[f][l] = True
    return a, seen


def measure(detail=False):
    a, seen = allowed()
    m = collections.Counter()
    pairs = collections.Counter()
    for f in sorted(os.listdir(LINKS)):
        if not f.endswith('.links.json'):
            continue
        cv = f[:-len('.links.json')]
        if cv not in a:
            m['canon volume absent from concordance'] += 1
            continue
        L = json.load(open(os.path.join(LINKS, f), encoding='utf-8'))
        for rec in L.values():
            for l in LAYERS:
                for ent in rec.get(l) or []:
                    k = ent.get('key') or ''
                    if '#' not in k:
                        continue
                    tv = k.rsplit('#', 1)[0]
                    m['targets'] += 1
                    if tv in a[cv][l]:
                        continue
                    if not a[cv][l]:
                        m['no_such_layer'] += 1
                        pairs[(cv, l, tv, 'no such layer')] += 1
                    else:
                        m['outside'] += 1
                        pairs[(cv, l, tv, 'outside')] += 1
    return m, pairs


def rates(m):
    t = max(1, m['targets'])
    return {
        'targets': m['targets'],
        'outside': m['outside'],
        'no_such_layer': m['no_such_layer'],
        'violation_pct': round(100.0 * (m['outside'] + m['no_such_layer']) / t, 3),
    }


if __name__ == '__main__':
    m, pairs = measure()
    r = rates(m)
    base = json.load(open(BASE, encoding='utf-8')) if os.path.exists(BASE) else None
    print('cross-layer links against %s' % os.path.join(SITE, 'concordance.json'))
    fails = []
    for k in ('targets', 'outside', 'no_such_layer', 'violation_pct'):
        line = '  %-18s %8s' % (k, r[k])
        if base and k in base:
            line += '   was %s' % base[k]
            worse = (r[k] < base[k]) if k == 'targets' else (r[k] > base[k] + 0.001)
            if worse:
                line += '   REGRESSED'
                fails.append('%s %s -> %s' % (k, base[k], r[k]))
        print(line)
    if '--detail' in sys.argv:
        print('\n%-10s %-14s %-10s %-14s %s' % ('canon', 'layer', 'target', 'kind', 'n'))
        for (cv, l, tv, kind), n in pairs.most_common(30):
            print('%-10s %-14s %-10s %-14s %d' % (cv, l, tv, kind, n))
    if '--record' in sys.argv:
        json.dump(r, open(BASE, 'w', encoding='utf-8'), indent=1)
        print('\nbaseline recorded')
        sys.exit(0)
    if fails:
        print('\nCONCORDANCE VIOLATIONS REGRESSED:')
        for x in fails:
            print('  - %s' % x)
        sys.exit(1)
    print('\nno measure regressed')
