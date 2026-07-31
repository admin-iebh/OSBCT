#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Do a canon volume's links point only into the volumes the EDITION assigns it?

`site/concordance.json` records the edition's own canon -> aṭṭhakathā -> ṭīkā
mapping, read from `concordanciatextos.pdf`.  `build_links_bynum.py` never
consults it: it "keeps each canon paragraph's existing TARGET VOLUME and fixes
the ORDINAL inside that volume by a monotonic number match".  So a target volume
that was wrong before the rebuild stays wrong, silently and at scale.

Found by this check on 2026-07-31b: **the Milindapañha (28Khu11), which the
concordance says has NO commentary and NO subcommentary, carried a target on
essentially every numbered paragraph** — into the Nettiṭīkā, the Mahāniddesa,
Udāna, Buddhavaṁsa and Khuddakapāṭha commentaries. The reader drew them as that
paragraph's commentary. A confident wrong link is worse than a missing one.

Usage: python3 _xc/check_link_targets.py
Exit 0 = every link target is one the edition assigns.
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def allowed():
    conc = json.load(open(os.path.join(ROOT, 'site/concordance.json'), encoding='utf-8'))
    ok = {}
    for g in conc['groups']:
        c = set(g['commentary']['files']) | set(g['subcommentary']['files'])
        for f in g['canon']['files']:
            ok.setdefault(f, set()).update(c)
    return ok


def run():
    ok = allowed()
    man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'),
                         encoding='utf-8'))['volumes']
    bad = collections.Counter()
    detail = collections.defaultdict(collections.Counter)
    total = 0
    for vol in sorted(man):
        if man[vol].get('layer') != 'canon':
            continue
        lp = os.path.join(ROOT, 'site/reader/linksk', vol + '.links.json')
        if not os.path.exists(lp):
            continue
        links = json.load(open(lp, encoding='utf-8'))
        allow = ok.get(vol, set())
        for o, e in links.items():
            for slot in ('commentary', 'subcommentary'):
                for t in (e.get(slot) or []):
                    tv = t['key'].split('#')[0]
                    total += 1
                    if tv not in allow:
                        bad[vol] += 1
                        detail[vol][tv] += 1
    return total, bad, detail, ok


if __name__ == '__main__':
    total, bad, detail, ok = run()
    print('link targets checked: %s' % f'{total:,}')
    print('targets the edition does NOT assign to that canon volume: %s\n'
          % f'{sum(bad.values()):,}')
    for vol, n in bad.most_common():
        allow = ', '.join(sorted(ok.get(vol, set()))) or '(none — the edition gives this work no commentary)'
        print('  %-12s %6d wrong-volume target(s)' % (vol, n))
        print('     the edition assigns: %s' % allow)
        for tv, c in detail[vol].most_common(6):
            print('     %6d -> %s' % (c, tv))
    sys.exit(1 if bad else 0)
