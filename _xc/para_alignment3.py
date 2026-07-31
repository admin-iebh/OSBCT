#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Which layer does the ṬĪKĀ's paragraph number actually key to?

`para_alignment2.py` found the commentary's lemma in the numbered CANON
paragraph 67.2% of the time (control 14.8% one paragraph away) but the ṭīkā's
only 34.6% (control 5.4%).  Both are far above chance, so both alignments are
real — but the ṭīkā's is markedly weaker, and there is an obvious reason to
suspect the question was aimed at the wrong target: **a ṭīkā comments on the
AṬṬHAKATHĀ, not on the canon.**  Its lemmata should be the commentary's words.

So the same lemma is tested against BOTH: the canon paragraph of that number,
and the commentary paragraph(s) of that number, with the same shift control.
"""
import json, glob, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import para_alignment2 as A

ROOT = A.ROOT
man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'),
                     encoding='utf-8'))['volumes']

# canon key -> commentary ords that claim it
canon2comm = collections.defaultdict(list)
for rp in sorted(glob.glob(os.path.join(ROOT, 'site/reader/links/*.rev.json'))):
    vol = os.path.basename(rp)[:-9]
    if man.get(vol, {}).get('layer') != 'commentary':
        continue
    for o, e in json.load(open(rp, encoding='utf-8')).items():
        if e.get('state') == 'direct' and e.get('canon'):
            canon2comm[e['canon']].append((vol, int(o)))


def run(shift=0):
    hit = collections.Counter(); tot = collections.Counter()
    for rp in sorted(glob.glob(os.path.join(ROOT, 'site/reader/links/*.rev.json'))):
        vol = os.path.basename(rp)[:-9]
        if man.get(vol, {}).get('layer') != 'subcommentary':
            continue
        if A._bold(vol) is None or A.paras(vol) is None:
            continue
        items = sorted((int(o), e) for o, e in json.load(open(rp, encoding='utf-8')).items()
                       if e.get('state') == 'direct' and e.get('canon'))
        for i, (o, e) in enumerate(items):
            lem = A.lemmas(vol, o)
            if not lem:
                continue
            j = i + shift
            if not (0 <= j < len(items)):
                continue
            ck = items[j][1]['canon']
            cv, co = ck.split('#')
            # against the CANON paragraph
            cps = A.paras(cv)
            if cps and 0 <= int(co) < len(cps):
                tot['canon'] += 1
                body = A.squash(A.norm(cps[int(co)].get('text') or ''))
                hit['canon'] += any(l in body for l in lem)
            # against the COMMENTARY paragraph(s) carrying the same number
            tgt = canon2comm.get(ck) or []
            if tgt:
                tot['commentary'] += 1
                found = False
                for av, ao in tgt[:3]:
                    aps = A.paras(av)
                    if not aps or not (0 <= ao < len(aps)):
                        continue
                    body = A.squash(A.norm(aps[ao].get('text') or ''))
                    if any(l in body for l in lem):
                        found = True; break
                hit['commentary'] += found
    return tot, hit


print('ṬĪKĀ lemma found in the paragraph of the same number, by target layer\n')
t0, h0 = run(0)
print('%-14s %8s %10s %8s' % ('target', 'pairs', 'found', 'rate'))
for k in ('canon', 'commentary'):
    print('%-14s %8d %10d %7.1f%%' % (k, t0[k], h0[k], 100.0 * h0[k] / t0[k] if t0[k] else 0))
print('\nCONTROL — same lemma, target k paragraphs away:')
for s in (1, 2, 5, 25):
    t, h = run(s)
    print('  shift %-3d  canon %5.1f%%   commentary %5.1f%%'
          % (s, 100.0 * h['canon'] / t['canon'] if t['canon'] else 0,
             100.0 * h['commentary'] / t['commentary'] if t['commentary'] else 0))
