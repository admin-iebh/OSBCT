#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE CORRECTOR, RUN AGAIN ON A VAGGA FIELD THAT HOLDS A VAGGA.

`_xc/ordinal_corrector.py` proposed 18 of 320 and none agreed with the name,
because 296 failed at `no_region`: the paragraph `vagga` field held whatever
heading the parse last saw.  `pipeline/build_vagga.py` derives the field from
the edition's own vagga headings instead.  Same corrector, same judge, one input
replaced.

THE JUDGE IS STILL THE SECTION NAME, which the ordinal never consults, and the
bar is still the one `_xc/residue_split2.py` set: a proposal that does not beat
the link already in the file is not a repair.

AND IT STILL DOES NOT REPAIR.  30 proposals of 320 disagreements, 3.7% name
agreement against the current link's 3.4% -- inside float noise of no change.
The derived field did what it was built to do: `no_region` fell 296 -> 180.  The
remaining failure is not regional.  Splitting the 320:

    195   the canon's vagga IS present in the target volume, and no paragraph
          in it states the wanted ordinal
     92   the canon's vagga is absent from the target volume -- the link is
          wrong at a level above the vagga, which the NAME sees and this cannot
     33   no derived vagga on the canon side

The first line is the ceiling, and it is arithmetic: the ordinal is printed on
3,617 paragraphs of 86,365.  A rule that can only land on a paragraph which
states its own ordinal can repair at most a twentieth of the corpus, and only
where the target happens to be one of those.

SO THE ORDINAL IS A DETECTOR.  Three candidate correctors have now been built and
refuted -- this one, `_xc/ordinal_corrector.py`, `_xc/ordinal_repair.py`.  Do not
build a fourth without first raising the number in that last paragraph.

Writes nothing.
"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import ordinal_words as ordinal
import relink_by_name as RBN

LINKS = os.path.join(ROOT, 'site', 'reader', 'linksk')
VAG = os.path.join(ROOT, '_xc', 'vagga')

_v = {}
def vag(v):
    if v not in _v:
        try:
            _v[v] = json.load(open(os.path.join(VAG, v + '.json'), encoding='utf-8'))['byOrd']
        except IOError:
            _v[v] = {}
    return _v[v]

def vstem(v, i):
    r = vag(v).get(str(i))
    return r['stem'] if r else None

_o = {}
def ords(v):
    """{(vagga stem, stated ordinal): [indexes]} for the target volume."""
    if v not in _o:
        m = collections.defaultdict(list)
        for i, p in enumerate(RBN.P(v)):
            o, _g, _w = ordinal.read(p.get('text', ''))
            if o is not None:
                m[(vstem(v, i), o)].append(i)
        _o[v] = m
    return _o[v]

def sn(p):
    try:
        return int(p.get('sutta_n'))
    except (TypeError, ValueError):
        return None

R = collections.Counter()
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
        if a is None:
            continue
        cname = RBN.stem(RBN.canon_name(cv, i))
        cvag = vstem(cv, i)
        for layer in ('commentary', 'subcommentary'):
            for ent in rec.get(layer) or []:
                if ent.get('state') != 'direct':
                    continue
                tv, _, tis = (ent.get('key') or '').partition('#')
                if not tis.isdigit():
                    continue
                ti = int(tis)
                tps = RBN.P(tv)
                if ti >= len(tps):
                    continue
                o, _g, _w = ordinal.read(tps[ti].get('text', ''))
                if o is None or o == a:
                    continue
                R['disagree'] += 1
                if not cvag:
                    R['no_canon_vagga'] += 1
                    continue
                cands = ords(tv).get((cvag, a), [])
                if not cands:
                    R['no_region'] += 1
                    continue
                if len(cands) > 1:
                    R['ambiguous'] += 1
                    continue
                j = cands[0]
                R['proposed'] += 1
                nc = RBN.stem(tps[ti].get('sutta'))
                nn = RBN.stem(tps[j].get('sutta'))
                if cname and nc:
                    J['cur_n'] += 1
                    J['cur_hit'] += (cname == nc)
                if cname and nn:
                    J['new_n'] += 1
                    J['new_hit'] += (cname == nn)
                if cname and nn == cname and nc != cname and len(ex) < 12:
                    ex.append((cv, i, cname, ent['key'], nc or '-', o,
                               '%s#%d' % (tv, j), a))

print('CORRECTOR on the derived vagga field')
for k in ('disagree', 'proposed', 'ambiguous', 'no_region', 'no_canon_vagga'):
    print('  %-16s %5d' % (k, R[k]))
print('\nJUDGED BY THE SECTION NAME, which the ordinal never consulted:')
if J['cur_n']:
    print('  current target    name agrees %5.1f%%  (%d of %d)'
          % (100.0 * J['cur_hit'] / J['cur_n'], J['cur_hit'], J['cur_n']))
if J['new_n']:
    print('  ordinal proposal  name agrees %5.1f%%  (%d of %d)'
          % (100.0 * J['new_hit'] / J['new_n'], J['new_hit'], J['new_n']))
print('\nproposals that are named right where the current link is not:')
for e in ex:
    print('  %s#%-5d %-20s  now %-14s %-18s (says %2d)  ->  %-14s (wanted %d)'
          % (e[0], e[1], e[2][:20], e[3], e[4][:18], e[5], e[6], e[7]))
