#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STEP 4: THE ORDINAL IS A DETECTOR. IS IT ALSO A CORRECTOR?

Step 3 found the candidate rule "same vagga as the CURRENT target" proposes
nothing better, and printed why: where the ordinal disagrees the current target
is usually in the wrong region altogether, so its vagga cannot select the right
one.  The region has to come from the CANON side.

So this tries the architecture of `pipeline/relink_by_name.py` with one part
replaced: name selects the region, and the ORDINAL -- not the printed paragraph
number -- places the link inside it.  The ordinal cannot repeat inside a vagga;
the paragraph number demonstrably can.

Judged, as before, by the sutta name, which the ordinal never consults.

IT DOES NOT WORK, AND THE REASON IS NOT THE ORDINAL.  Of 320 disagreeing direct
links it proposes 18, and those 18 agree with the name 0 times.  296 fail at
`no_region`: the canon `vagga` field does not hold a vagga.  It holds whatever
heading the structure parse last saw -- `sagāthāvaggasaṁyutta` for a canon
paragraph, `pattavaggacīvaraacchindanasikkhāpada` for a Vinaya one -- so there is
nothing in the target volume for it to match.  A corrector needs a region
selector and the corpus does not currently carry one at vagga level.

SO THE ORDINAL IS A DETECTOR AND NOT A CORRECTOR, and this file exists to say so
with numbers, so it is not built a third time.  What it detects is real: where it
condemns a link and the name can judge, the name agrees 96.9% of the time (221 of
228), and it condemns 92 more that carry no name on either side.

Writes nothing.
"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import ordinal_words as ordinal
import relink_by_name as RBN

LINKS = os.path.join(ROOT, 'site', 'reader', 'linksk')

_o = {}
def ords(v):
    if v not in _o:
        m = collections.defaultdict(list)
        for i, p in enumerate(RBN.P(v)):
            o, _g, _w = ordinal.read(p.get('text', ''))
            if o is not None:
                m[(RBN.stem(p.get('vagga')), o)].append(i)
        _o[v] = m
    return _o[v]

def sn(p):
    try:
        return int(p.get('sutta_n'))
    except (TypeError, ValueError):
        return None

X = collections.Counter()          # 2x2 of ordinal verdict vs name verdict
R = collections.Counter()          # corrector outcomes
J = collections.Counter()
ex = []

for f in sorted(os.listdir(LINKS)):
    if not f.endswith('.links.json'):
        continue
    cv = f[:-len('.links.json')]
    cps = RBN.P(cv)
    if not cps:
        continue
    links = json.load(open(os.path.join(LINKS, f), encoding='utf-8'))
    for si, rec in links.items():
        i = int(si)
        if i >= len(cps):
            continue
        a = sn(cps[i])
        cname = RBN.stem(RBN.canon_name(cv, i))
        cvag = RBN.stem(cps[i].get('vagga'))
        for layer in ('commentary', 'subcommentary'):
            for ent in rec.get(layer) or []:
                if ent.get('state') != 'direct':
                    continue
                tv, _, tis = ent['key'].partition('#')
                ti = int(tis)
                tps = RBN.P(tv)
                if ti >= len(tps) or a is None:
                    continue
                o, _g, _w = ordinal.read(tps[ti].get('text', ''))
                if o is None:
                    continue
                nc = RBN.stem(tps[ti].get('sutta'))
                nverd = ('nameless' if not (cname and nc)
                         else 'name_ok' if cname == nc else 'name_bad')
                X[('ord_ok' if o == a else 'ord_bad', nverd)] += 1
                if o == a:
                    continue
                # --- the corrector: canon's vagga selects the region,
                #     the stated ordinal places inside it
                cands = ords(tv).get((cvag, a), []) if cvag else []
                if not cands:
                    R['no_region'] += 1
                    continue
                if len(cands) > 1:
                    R['ambiguous'] += 1
                    continue
                j = cands[0]
                R['proposed'] += 1
                nn = RBN.stem(tps[j].get('sutta'))
                if cname and nn:
                    J['new_n'] += 1
                    J['new_hit'] += (cname == nn)
                if cname and nc:
                    J['cur_n'] += 1
                    J['cur_hit'] += (cname == nc)
                if cname and nn and nn == cname and nc != cname and len(ex) < 12:
                    ex.append((cv, i, cname, ent['key'], nc, o, '%s#%d' % (tv, j), a))

print('DIRECT links, ordinal verdict x name verdict')
print('%-10s %10s %10s %10s' % ('', 'name_ok', 'name_bad', 'nameless'))
for r in ('ord_ok', 'ord_bad'):
    print('%-10s %10d %10d %10d' % (r, X[(r, 'name_ok')], X[(r, 'name_bad')], X[(r, 'nameless')]))
t = sum(X.values())
nb = X[('ord_bad', 'name_ok')] + X[('ord_bad', 'name_bad')]
if nb:
    print('\nwhere the ordinal says WRONG and the name can judge, the name agrees it is wrong '
          '%.1f%% of the time (%d of %d)' % (100.0 * X[('ord_bad', 'name_bad')] / nb,
                                             X[('ord_bad', 'name_bad')], nb))
print('the ordinal condemns %d links the name cannot judge at all' % X[('ord_bad', 'nameless')])

print('\nCORRECTOR (canon vagga selects region, ordinal places)')
for k in ('proposed', 'ambiguous', 'no_region'):
    print('  %-12s %5d' % (k, R[k]))
if J['cur_n']:
    print('  current target  name agrees %5.1f%% (%d/%d)' % (100.0 * J['cur_hit'] / J['cur_n'], J['cur_hit'], J['cur_n']))
if J['new_n']:
    print('  ordinal proposal name agrees %5.1f%% (%d/%d)' % (100.0 * J['new_hit'] / J['new_n'], J['new_hit'], J['new_n']))
for e in ex:
    print('  ', e)
