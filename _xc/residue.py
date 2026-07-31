#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""How many canon paragraphs have no commentary the reader can show?

WHY THIS FILE EXISTS.  The figure has drifted.  The handoff records "**9,164**
numbered ¶ with NO rev entry (27.4% of 33,398)"; a quick check on 2026-07-31
using `links/<VOL>.fwd.json` gave 1,034 of 49,451 (2.1%).  Both cannot be right,
and neither states its method, so the number could not be defended.

**The two disagree because they read DIFFERENT FILES.**  There are two link maps
per volume and only one of them is the reader's:

  * `site/reader/linksk/<VOL>.links.json` — keyed by ORDINAL, values are ARRAYS
    of targets. `loadLinks()` fetches this. **This is what the reader draws.**
  * `site/reader/links/<VOL>.fwd.json`    — keyed differently, one target each.
    Loaded by nothing in `reader2.html`.

So the only figure that answers the question a reader would ask — *is there a
commentary here?* — is the one computed from `linksk/`.  That is what this
measures, and the method is stated here so the number stops moving.

Definitions, all of them deliberate:
  * universe  = paragraphs in CANON volumes carrying a printed number (`n`).
                Unnumbered paragraphs are headings, uddāna and front matter.
  * direct    = at least one target whose own state is `direct`
  * covered   = targets exist, but all are `covered` (the commentary treats this
                paragraph inside a block anchored earlier)
  * none      = no target at all: the residue

Milindapañha (28Khu11) has NO commentary in the edition — the concordance says
so — and is reported separately rather than counted as a defect.

Usage: python3 _xc/residue.py
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_COMMENTARY = {'28Khu11'}          # per concordanciatextos.pdf


def run():
    man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'),
                         encoding='utf-8'))['volumes']
    tot = collections.Counter()
    rows = []
    for vol in sorted(man):
        if man[vol].get('layer') != 'canon':
            continue
        vp = os.path.join(ROOT, 'site', vol + '.json')
        lp = os.path.join(ROOT, 'site/reader/linksk', vol + '.links.json')
        if not os.path.exists(vp):
            continue
        paras = json.load(open(vp, encoding='utf-8'))['paragraphs']
        links = json.load(open(lp, encoding='utf-8')) if os.path.exists(lp) else {}
        c = collections.Counter()
        for i, p in enumerate(paras):
            if p.get('n') is None:
                continue
            c['numbered'] += 1
            e = links.get(str(i)) or {}
            tg = (e.get('commentary') or []) + (e.get('subcommentary') or [])
            if not tg:
                c['none'] += 1
            elif any(t.get('state') == 'direct' for t in tg):
                c['direct'] += 1
            else:
                c['covered'] += 1
        rows.append((vol, c))
        if vol not in NO_COMMENTARY:
            for k in c:
                tot[k] += c[k]
    return rows, tot


if __name__ == '__main__':
    rows, tot = run()
    n = tot['numbered']
    print('CANON PARAGRAPHS WITH A PRINTED NUMBER (excluding Milindapañha, which')
    print('the edition gives no commentary): %s\n' % f'{n:,}')
    for k, lab in (('direct', 'a DIRECT commentary/ṭīkā target'),
                   ('covered', 'only COVERED (inside an earlier block)'),
                   ('none', 'NO target at all  <- the residue')):
        print('  %-38s %8s  %5.1f%%' % (lab, f'{tot[k]:,}', 100.0 * tot[k] / n))
    print('\nby volume (residue first):')
    print('  %-12s %8s %8s %8s %8s' % ('vol', 'numbered', 'direct', 'covered', 'none'))
    for vol, c in sorted(rows, key=lambda r: -r[1]['none']):
        if not c['numbered']:
            continue
        mark = '   (no commentary in the edition)' if vol in NO_COMMENTARY else ''
        if c['none'] or mark:
            print('  %-12s %8d %8d %8d %8d%s'
                  % (vol, c['numbered'], c['direct'], c['covered'], c['none'], mark))
