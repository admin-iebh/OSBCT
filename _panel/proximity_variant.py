#!/usr/bin/env python3
"""One more variant, because the measurement suggested it.

The exact-paragraph proximity rule fires on 6.5% of glossed clicks and is right
57% of the time.  What made the right ones right was that the row's bold lemma
was a phrase of the paragraph on screen.  So test that condition ON ITS OWN,
without the link map:

    promote a gloss row when its bold lemma is fully present in the paragraph
    the reader is in.

That is not a guess and not a ranking heuristic -- it is a checkable statement
about the row ("this explains a phrase that stands in front of you"), and it
reaches the parallel-passage commentary that the link map cannot see (sample
item #41: the exactly right row for Sn 872 sits in the Niddesa, not in the
linked Suttanipāta commentary).

Reports the coverage of:
  L  in the linked commentary/ṭīkā paragraph AND lemma present
  P  lemma present, from anywhere in the corpus
"""
import json, os, re, sys, glob, random, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
from proximity_precision import pool_of, belongs_pool, clean, PALI, APOS

rng = random.Random(20260802)


def tokens(text):
    ok = PALI | {'-'} | APOS
    buf, prev, out = [], '', []
    for i, ch in enumerate(text):
        if ch in ok:
            if ch in APOS or ch == '-':
                nxt = text[i + 1] if i + 1 < len(text) else ''
                if not (prev in PALI and nxt in PALI):
                    if buf:
                        out.append(''.join(buf))
                    buf, prev = [], ch
                    continue
            buf.append(ch)
        elif buf:
            out.append(''.join(buf)); buf = []
        prev = ch
    if buf:
        out.append(''.join(buf))
    return out


print('loading…', file=sys.stderr)
by_form = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(REPO, '_gloss/by_volume/*.json'))):
    if os.path.basename(f) == 'index.json':
        continue
    for r in json.load(open(f)):
        slim = {'l': r['lemma'], 'v': r['vol'], 'n': r['n'], 'w': r['words']}
        for cd in r['candidates']:
            by_form[cd].append(slim)

links = {}
for f in sorted(glob.glob(os.path.join(REPO, 'site/reader/links/*.fwd.json'))):
    links[os.path.basename(f).split('.')[0]] = json.load(open(f))

c = collections.Counter()
mw = collections.Counter()
for vol in sorted(links):
    path = os.path.join(REPO, 'site', vol + '.json')
    if not os.path.exists(path):
        continue
    for p in json.load(open(path))['paragraphs']:
        if p.get('n') is None:
            continue
        rec = links[vol].get(str(p['n']))
        if not rec:
            continue
        tgt = set()
        for layer in ('commentary', 'subcommentary'):
            L = rec.get(layer)
            if L and L.get('vol') is not None and L.get('n') is not None:
                tgt.add((L['vol'], L['n']))
        toks = tokens(clean(p['text']))
        if not toks:
            continue
        pool = pool_of(p['text'])
        for _ in range(3):
            w = toks[rng.randrange(len(toks))]
            rows = by_form.get(w) or by_form.get(w.lower()) or []
            c['clicks'] += 1
            if not rows:
                continue
            c['glossed'] += 1
            present = [r for r in rows if belongs_pool(r['l'], pool)]
            linked = [r for r in present if (r['v'], r['n']) in tgt]
            if linked:
                c['L'] += 1
            if present:
                c['P'] += 1
                mw[min(max(r['w'] for r in present), 6)] += 1
                if len(rows) > 50:
                    c['P_bigband'] += 1
            if len(rows) > 50:
                c['bigband'] += 1

g = c['glossed']
print()
print(f"clicks {c['clicks']:,}   with any gloss {g:,} ({100*g/c['clicks']:.1f}%)")
print(f"  L  linked paragraph AND lemma present   {c['L']:7,} "
      f"({100*c['L']/g:5.2f}% of glossed clicks)")
print(f"  P  lemma present, from anywhere         {c['P']:7,} "
      f"({100*c['P']/g:5.2f}% of glossed clicks)")
print(f"     of the >50-row band ({c['bigband']:,} clicks), P fires on "
      f"{c['P_bigband']:,} ({100*c['P_bigband']/max(c['bigband'],1):.1f}%)")
print()
print('  longest lemma promoted, by word count:')
for k in sorted(mw):
    print(f'    {k}{"+" if k==6 else ""} words  {mw[k]:7,}')
