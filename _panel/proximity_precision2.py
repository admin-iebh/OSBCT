#!/usr/bin/env python3
"""The proximity number that matches what the panel actually does.

proximity_precision.py asked a broader question -- of EVERY row sitting in the
linked paragraph, is its phrase in the canon paragraph -- and that denominator
is wrong for the panel: a commentary paragraph glosses many phrases, and most
of them are not the one the reader clicked.

What the panel does is narrower.  The reader clicks word W; the panel keeps the
rows keyed to W; of those it puts FIRST the ones sitting in the linked
paragraph.  So the question is: when such a row exists, is its bold lemma
really a phrase of THIS canon paragraph?

That is exactly the question the 60 hand verdicts answered (A vs B/C), and the
proxy agreed with the human on 56 of 60.  Here it is run over every simulated
click in the corpus, split by nikāya, because the hand sample suggested the
answer is not the same everywhere.
"""
import json, os, re, sys, glob, random, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
SEED = 20260802

sys.path.insert(0, ROOT)
from proximity_precision import pool_of, belongs_pool, words, clean, PALI, APOS

rng = random.Random(SEED)


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


print('loading glosses…', file=sys.stderr)
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

GROUP = lambda v: ('Vinaya' if v[2:5] == 'Vin' else
                   'Dīgha' if v[2:4] == 'Di' else
                   'Majjhima' if v[2:4] == 'Ma' else
                   'Saṁyutta' if v[2:5] == 'Sam' else
                   'Aṅguttara' if v[2:4] == 'An' else
                   'Khuddaka' if v[2:5] == 'Khu' else
                   'Abhidhamma' if v[2:6] == 'Abhi' else 'other')

# per group: [clicks, glossed clicks, clicks with a proximity row,
#             of those, at least one proximity row whose lemma is in the para]
st = collections.defaultdict(lambda: [0, 0, 0, 0])
CLICKS_PER_PARA = 3          # three independent clicks per paragraph

print('walking the canon…', file=sys.stderr)
for vol in sorted(links):
    path = os.path.join(REPO, 'site', vol + '.json')
    if not os.path.exists(path):
        continue
    g = GROUP(vol)
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
        if not tgt:
            continue
        toks = tokens(clean(p['text']))
        if not toks:
            continue
        pool = pool_of(p['text'])
        for _ in range(CLICKS_PER_PARA):
            w = toks[rng.randrange(len(toks))]
            rows = by_form.get(w) or by_form.get(w.lower()) or []
            st[g][0] += 1
            if not rows:
                continue
            st[g][1] += 1
            prox = [r for r in rows if (r['v'], r['n']) in tgt]
            if not prox:
                continue
            st[g][2] += 1
            if any(belongs_pool(r['l'], pool) for r in prox):
                st[g][3] += 1

print()
print('PROXIMITY, as the panel uses it')
print('  a click that returns gloss rows; of those rows, the ones sitting in')
print('  the linked commentary/ṭīkā paragraph are shown first.  How often is')
print('  such a row really about a phrase of this canon paragraph?')
print()
print(f'  {"group":<12} {"clicks":>9} {"glossed":>9} {"proximity":>10} '
      f'{"of those, phrase is here":>26}')
T = [0, 0, 0, 0]
for g in ('Vinaya', 'Dīgha', 'Majjhima', 'Saṁyutta', 'Aṅguttara', 'Khuddaka',
          'Abhidhamma'):
    a, b, c, d = st[g]
    if not a:
        continue
    for i, v in enumerate((a, b, c, d)):
        T[i] += v
    print(f'  {g:<12} {a:9,} {b:9,} {c:10,} ({100*c/b:4.1f}%) '
          f'{d:9,} ({100*d/max(c,1):5.1f}%)')
a, b, c, d = T
print(f'  {"ALL":<12} {a:9,} {b:9,} {c:10,} ({100*c/b:4.1f}%) '
      f'{d:9,} ({100*d/max(c,1):5.1f}%)')
print()
print('  Read: proximity fires on a small share of glossed clicks, and when it')
print('  fires outside the Abhidhamma it is nearly always about this passage.')
