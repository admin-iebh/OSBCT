#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STEP 3: CAN THE STATED ORDINAL MOVE A WRONG LINK ONTO THE RIGHT SUTTA,
AND DOES THE PROPOSAL BEAT THE LINK ALREADY IN THE FILE ON A CRITERION IT
CANNOT SEE?

`_xc/ordinal_join.py` measured the signal: 87.0% agreement on `direct` links
against a 5.1% shift-25 floor.  Agreement is not repair.  This asks the only
question that licenses writing anything:

    where the ordinal DISAGREES with the current target, is there another
    paragraph in the same vagga of the same volume whose stated ordinal is
    the canon paragraph's `sutta_n` -- and is THAT one the better link?

THE JUDGE IS THE NAME, which the ordinal cannot see.  `pipeline/relink_by_name.py`
stems section names on both sides; this reuses that stemmer unchanged.  On the
subset where both sides are named, it reports name agreement for the CURRENT
target and for the PROPOSED one.  A proposal that does not beat the current link
there is not a repair, and this script's job is to say so before anything is
written.

SUPERSEDED BY `_xc/ordinal_corrector.py`.  The candidate rule here -- "another
paragraph in the vagga of the CURRENT target" -- proposes 129 and scores 1.0% on
the name, exactly what the link it would replace scores.  It cannot do better:
where the ordinal disagrees the current target is usually in the wrong region
altogether, so its own vagga is the wrong place to look.  Kept for the number.

Writes nothing.  Prints tables.
"""
import json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import ordinal_words as ordinal
import relink_by_name as RBN

SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')

_o = {}
def ords(v):
    """{index: ordinal} for every paragraph in v that states one, plus the
    vagga stem it sits in."""
    if v not in _o:
        ps = RBN.P(v)
        m = {}
        for i, p in enumerate(ps):
            o, _g, _w = ordinal.read(p.get('text', ''))
            if o is not None:
                m[i] = (o, RBN.stem(p.get('vagga')))
        _o[v] = m
    return _o[v]

def sn(p):
    try:
        return int(p.get('sutta_n'))
    except (TypeError, ValueError):
        return None

C = collections.Counter()
name_cur = collections.Counter()
name_new = collections.Counter()
examples = []

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
        for layer in ('commentary', 'subcommentary'):
            for ent in rec.get(layer) or []:
                if ent.get('state') != 'direct':
                    continue
                tv, _, tis = ent['key'].partition('#')
                ti = int(tis)
                om = ords(tv)
                if ti not in om or a is None:
                    continue
                o, tvag = om[ti]
                C['tested'] += 1
                if o == a:
                    C['agree'] += 1
                    continue
                C['disagree'] += 1
                cands = [j for j, (oo, vv) in om.items() if oo == a and vv == tvag]
                if not cands:
                    C['no_candidate'] += 1
                    continue
                if len(cands) > 1:
                    C['ambiguous'] += 1
                    continue
                C['unique_proposal'] += 1
                j = cands[0]
                tps = RBN.P(tv)
                nc = RBN.stem(tps[ti].get('sutta'))
                nn = RBN.stem(tps[j].get('sutta'))
                if cname and nc:
                    name_cur['n'] += 1
                    name_cur['hit'] += (cname == nc)
                if cname and nn:
                    name_new['n'] += 1
                    name_new['hit'] += (cname == nn)
                if cname and nc and nn and len(examples) < 15 and nn == cname != nc:
                    examples.append((cv, i, cname, ent['key'], nc, o, '%s#%d' % (tv, j), nn, a))

print('DIRECT links where both sides give a number')
for k in ('tested', 'agree', 'disagree', 'no_candidate', 'ambiguous', 'unique_proposal'):
    print('  %-16s %6d   %5.1f%%' % (k, C[k], 100.0 * C[k] / max(1, C['tested'])))

print('\nTHE HELD-OUT JUDGE -- section name, which the ordinal never consulted')
for nm, c in (('current target', name_cur), ('ordinal proposal', name_new)):
    if c['n']:
        print('  %-18s name agrees %5.1f%%  (%d of %d)'
              % (nm, 100.0 * c['hit'] / c['n'], c['hit'], c['n']))

print('\nexamples where the proposal is named right and the current link is not:')
for cv, i, cn, ck, nc, o, nk, nn, a in examples:
    print('  %s#%-5d %-22s  now %-14s %-20s (says %2d)  ->  %-14s %-20s (says %2d, wanted %d)'
          % (cv, i, cn[:22], ck, nc[:20], o, nk, nn[:20], a, a))
