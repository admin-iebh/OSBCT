# -*- coding: utf-8 -*-
"""Redistribute bold/<VOL>.bold.json across the re-segmented paragraphs, and
PROVE it semantically, independently of the arithmetic that built it.

`bold/<VOL>.bold.json` is {ord: [[a,b], ...]} -- half-open CHARACTER offsets
into the paragraph's raw `text`.  The refinement is SPACE-JOINED (extract.py
continues with `cur['text'] += ' ' + st`), so for old paragraph P covering new
N1..Nk:  start(N1)=0, start(Ni)=start(Ni-1)+len(Ni-1)+1.  Asserted, not assumed.

THE PROOF: the substring each span selects AFTER the split must be
byte-identical to the one it selected BEFORE.  Controls: shift-by-one and
all-spans-to-first-of-run must both break it.

    python3 _xc/reseg2/bold.py <VOL> [--write]
"""
import json, os, sys, collections
ROOT = os.path.abspath('.')
VOL = [a for a in sys.argv[1:] if not a.startswith('-')][0]


def _PRE(p):
    q = p + '.prereseg2'
    return q if os.path.exists(os.path.join(ROOT, q)) else p


def J(p):
    return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))


ship = J(_PRE('site/%s.json' % VOL))['paragraphs']
new = J('_xc/reseg2/%s.json' % VOL)['paragraphs']
rm = {int(k): v for k, v in J('_xc/reseg2/ord_remap_%s.json' % VOL).items()}
bold = J(_PRE('site/reader/bold/%s.bold.json' % VOL))

RUN, START = {}, {}
for i in sorted(rm):
    s = rm[i]
    e = rm[i + 1] if (i + 1) in rm else len(new)
    RUN[i] = list(range(s, e))
    off, st = 0, {}
    for j in RUN[i]:
        st[j] = off
        off += len(new[j]['text'] or '') + 1
    START[i] = st
    joined = ' '.join(new[j]['text'] or '' for j in RUN[i])
    assert joined == (ship[i]['text'] or ''), 'NOT A REFINEMENT at old ord %d' % i
print('%s  refinement asserted: %d shipped ¶ == space-join of %d new ¶, exact'
      % (VOL, len(rm), len(new)))


def redistribute(mode='design'):
    nb = collections.defaultdict(list)
    strad = 0
    pairs = []                      # (old_ord, [a,b], new_ord, [a',b'])
    for k, spans in bold.items():
        i = int(k)
        st = START[i]
        for a, b in spans:
            if mode == 'first':
                j = RUN[i][0]
                nb[str(j)].append([a, b])
                pairs.append((i, [a, b], j, [a, b]))
                continue
            j = None
            for cand in RUN[i]:
                Ln = len(new[cand]['text'] or '')
                if st[cand] <= a < st[cand] + Ln:
                    j = cand
                    break
            if j is None or b > st[j] + len(new[j]['text'] or ''):
                strad += 1
                continue
            d = 1 if mode == 'shift' else 0
            nb[str(j)].append([a - st[j] + d, b - st[j] + d])
            pairs.append((i, [a, b], j, [a - st[j] + d, b - st[j] + d]))
    return nb, strad, pairs


def prove(pairs, label):
    ok = bad = 0
    for oi, (a, b), nj, (c, d) in pairs:
        before = (ship[oi]['text'] or '')[a:b]
        after = (new[nj]['text'] or '')[c:d]
        if before == after:
            ok += 1
        else:
            bad += 1
    print('   %-38s spans %5d   substring identical %5d   DIFFERENT %5d'
          % (label, len(pairs), ok, bad))
    return bad


nb, strad, pairs = redistribute()
tot = sum(len(v) for v in bold.values())
print('   bold: %d keys / %d spans in -> %d keys / %d spans out, %d unplaceable '
      '(straddling a boundary or on a joining space)'
      % (len(bold), tot, len(nb), sum(len(v) for v in nb.values()), strad))
print('  SEMANTIC PROOF (independent of the offset arithmetic):')
bad = prove(pairs, 'design')
print('  NEGATIVE CONTROLS (each MUST break it):')
_, _, p_shift = redistribute('shift')
b1 = prove(p_shift, 'CONTROL every offset shifted +1')
_, _, p_first = redistribute('first')
b2 = prove(p_first, 'CONTROL all spans left on first-of-run')
print('  controls that fired: %d of 2' % ((b1 > 0) + (b2 > 0)))
assert bad == 0, 'SEMANTIC PROOF FAILED'
if '--write' in sys.argv:
    os.makedirs(ROOT + '/_xc/reseg2/bold', exist_ok=True)
    json.dump({k: nb[k] for k in sorted(nb, key=int)},
              open('%s/_xc/reseg2/bold/%s.bold.json' % (ROOT, VOL), 'w', encoding='utf-8'),
              ensure_ascii=False)
    print('  WROTE _xc/reseg2/bold/%s.bold.json' % VOL)
