#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prune the Class C link targets that carry no evidence of any relation.

CLASS C (14,278 forward targets) is where the edition assigns SOMETHING for that
slot but not the volume the link names.  07-31c left it alone, correctly, on the
ground that "any grouping coarse enough to call the first legitimate calls the
second legitimate too" — which is true of VOLUME IDENTITY, the thing that was
tried.  It is not true of the bolded lemma, which measures each pair directly.

THE EVIDENCE (`_xc/classc_lemma.py`, 2026-08-01d).  A commentary paragraph opens
by quoting the canon words it is about; `bold/` marks those quotations from the
edition's typography, never from a number.  Scoring each `(canon -> target)` pair
and controlling by re-scoring the same lemma against a canon paragraph k places
away:

    ALLOWED   48.7% at shift 0, 16.0% at shift 1, 3.7% at shift 25 (21,651 pairs)
    CLASS C   12.0% at shift 0,  2.1% at shift 1, 1.2% at shift 25  (3,796 pairs)

Per pair the distribution is bimodal with NOTHING between 15.8% and 27.8%:

    20Khu03 -> 33KhuA14   82.0% -> 9.6% at shift 1   SEAM (better than the allowed mean)
    22Khu05 -> 40KhuA21   48.1% -> 3.9%              SEAM (the Jātaka commentary)
    21Khu04 -> 32KhuA13   40.0% -> 0.0%              seam, n=10
    20Khu03 -> 35KhuA16   27.8% -> 0.0%              probable seam
    33Abhi05 -> 48AbhiA01 15.8% -> 5.3/10.5/5.3/5.9  NOT a seam: the control never falls
    39Abhi11 -> 48AbhiA01  1.9% -> 1.3%              noise, as 07-31c predicted

!!! THE CONTROL IS THE ARGUMENT, NOT THE RATE.  A real alignment collapses when
displaced by one paragraph.  `33Abhi05 -> 48AbhiA01` looks like a weak seam at
15.8% and its control refuses to fall — shared vocabulary, not alignment.  Judged
on the rate alone it would have been kept.

THREE OUTCOMES, and the third is deliberate:
  KEEP     pairs at or above THRESHOLD (measured seams)
  DROP     pairs below it with enough scored links to judge
  LEAVE    pairs with fewer than MINSCORED scored links — NOT judgeable by this
           method, so not touched.  1,812 targets.  An unjudged link is left
           standing; it is not swept in with the ones that were measured.

The rev maps get the SAME per-pair verdicts, because pruning one direction alone
leaves the other asserting the relation (the lesson of 07-31c).

Writes to `_xc/linksk_classc/` — outside site/, so nothing is published or
hashed into BUILD.  Usage: python3 pipeline/prune_class_c.py [--threshold 25]
"""
import json, os, sys, collections, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'site/reader/linksk')
OUT = os.path.join(ROOT, '_xc/linksk_classc')
THRESHOLD = 25.0
MINSCORED = 10

_s = importlib.util.spec_from_file_location('cl', os.path.join(ROOT, '_xc/classc_lemma.py'))
CL = importlib.util.module_from_spec(_s)
_s.loader.exec_module(CL)
SLOTS3 = ('canon', 'commentary', 'subcommentary')


def rev_model():
    conc = json.load(open(os.path.join(ROOT, 'site/concordance.json'), encoding='utf-8'))
    allow_rev = collections.defaultdict(set)
    assigns = collections.defaultdict(lambda: {'commentary': set(), 'subcommentary': set()})
    slots_of = collections.defaultdict(set)
    for g in conc['groups']:
        f = {s: list(g[s]['files']) for s in SLOTS3}
        pres = [s for s in SLOTS3 if f[s]]
        if not pres:
            continue
        spine, below = pres[0], pres[1:]
        for s in below:
            for v in f[spine]:
                assigns[v][s].update(f[s])
            for v in f[s]:
                slots_of[v].add(s)
                allow_rev[v].update(f[spine])
    return allow_rev, assigns, slots_of


def verdicts(threshold):
    """(canon, target) -> 'KEEP' | 'DROP' | 'LEAVE', from the lemma evidence."""
    _, _, bytarget = CL.run(0)
    out = {}
    for k, (n, hit) in bytarget.items():
        if n < MINSCORED:
            out[k] = 'LEAVE'
        else:
            out[k] = 'KEEP' if 100.0 * hit / n >= threshold else 'DROP'
    return out, bytarget


def main():
    thr = THRESHOLD
    if '--threshold' in sys.argv:
        thr = float(sys.argv[sys.argv.index('--threshold') + 1])
    os.makedirs(OUT, exist_ok=True)
    allow_fwd = CL.model()
    allow_rev, assigns, slots_of = rev_model()
    V, scored = verdicts(thr)

    print('threshold %.0f%%, minimum %d scored links to judge a pair\n' % (thr, MINSCORED))
    keep = sorted([k for k, v in V.items() if v == 'KEEP'])
    print('SEAMS KEPT (%d pairs):' % len(keep))
    for k in keep:
        n, h = scored[k]
        print('   %-10s -> %-10s  %5.1f%% on %d scored' % (k[0], k[1], 100.0 * h / n, n))

    counts = collections.Counter()
    # ---- forward ----
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.links.json'):
            continue
        cv = fn[:-len('.links.json')]
        al = allow_fwd.get(cv)
        old = json.load(open(os.path.join(SRC, fn), encoding='utf-8'))
        new = {}
        for o, e in old.items():
            k2 = {}
            for slot in ('commentary', 'subcommentary'):
                arr = []
                for t in (e.get(slot) or []):
                    tv = t['key'].split('#')[0]
                    if not al or tv in al[slot]:
                        arr.append(t); counts['fwd_allowed'] += 1; continue
                    d = V.get((cv, tv), 'LEAVE')
                    counts['fwd_' + d.lower()] += 1
                    if d != 'DROP':
                        arr.append(t)
                if arr:
                    k2[slot] = arr
            if k2:
                new[o] = k2
        json.dump(new, open(os.path.join(OUT, fn), 'w', encoding='utf-8'), ensure_ascii=False)
    # ---- reverse, same verdicts ----
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.rev.json'):
            continue
        lv = fn[:-len('.rev.json')]
        al = allow_rev.get(lv, set())
        mine = slots_of.get(lv, set())
        old = json.load(open(os.path.join(SRC, fn), encoding='utf-8'))
        new = {}
        for o, e in old.items():
            sv = (e.get('canon') or '').split('#')[0]
            if sv in al:
                counts['rev_allowed'] += 1
                new[o] = e; continue
            if not any(assigns.get(sv, {}).get(s) for s in mine):
                counts['rev_classA'] += 1          # should be 0 — Class A is applied
                continue
            d = V.get((sv, lv), 'LEAVE')
            counts['rev_' + d.lower()] += 1
            if d != 'DROP':
                new[o] = e
        json.dump(new, open(os.path.join(OUT, fn), 'w', encoding='utf-8'), ensure_ascii=False)

    print('\nFORWARD   allowed %s · seam kept %s · dropped %s · left unjudged %s'
          % tuple(f'{counts["fwd_" + k]:,}' for k in ('allowed', 'keep', 'drop', 'leave')))
    print('REVERSE   allowed %s · seam kept %s · dropped %s · left unjudged %s%s'
          % (tuple(f'{counts["rev_" + k]:,}' for k in ('allowed', 'keep', 'drop', 'leave'))
             + ('   [Class A residue %d]' % counts['rev_classa'] if counts['rev_classa'] else '',)))
    print('\nwritten to _xc/linksk_classc/ — the live maps are untouched')


if __name__ == '__main__':
    main()
