#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE 77 CONDEMNED LINKS WHOSE SUTTA IS COMMENTED ON IN A DIFFERENT VOLUME.

Three criteria now separate the same 320 links, and the third is the one that
says what to do about them.  Where the canon sutta's name appears as a section
in the commentary layer:

                        in target vol   nowhere   another vol
    ordinal AGREES           87.1%        7.1%        5.8%     (n=2139)
    ordinal CONDEMNS          2.2%       73.8%       24.1%     (n= 320)

That contrast is the control this rests on.  Absence is not normal: a link the
ordinal blesses lands in a volume that names the sutta 87% of the time.

`relink_by_name.py` cannot reach any of these -- 313 of 320 take its
`no matching section in target volume` branch -- because it deliberately never
re-routes volumes, and `build_links_bynum.py` recorded why: a WHOLESALE rebuild
constrained by the concordance lost on both axes at once.

THIS IS NOT THAT.  It moves one link at a time, only where the sutta's name
occurs as a section in EXACTLY ONE other commentary volume, and only where the
ordinal already condemns the link that is there.  A named destination for a
named sutta.

THE JUDGE IS THE ORDINAL, WHICH TOOK NO PART IN THE SELECTION.  The destination
is chosen by name and the paragraph inside it by `relink_by_name.place()` -- the
printed number, its own rule.  Then the arriving paragraph is asked what it says
it is glossing.  Placing by the ordinal and then testing the ordinal would prove
nothing; this does not do that.

AND IT IS NOT GOOD ENOUGH TO WRITE.  40 re-routes, 30 of them judgeable, and the
arriving paragraph states the canon's own position 9 times -- 30.0%.  Above the
9.2% chance rate and nowhere near the 87.0% that uncondemned links score.  The
destination volume may well be right; the paragraph chosen inside it is picked by
the printed number, which is the key that was never a key.

WHAT IT DID FIND is a cluster that turned out to be the real lead: 8 of the 9
confirmed re-routes run `18Khu01` -> `24KhuA05` while the live link points at
`23KhuA04`.  A whole run of links from one canon volume aimed at the wrong
commentary volume is not a placement fault, and chasing it produced
`pipeline/check_concordance.py` and the 3,163 targets that violate the edition's
own volume map.  Kept for that, and for the 30.0%.

Writes nothing.
"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import ordinal_words as ordinal
import relink_by_name as RBN

LINKS = os.path.join(ROOT, 'site', 'reader', 'linksk')
LAYER = json.load(open(os.path.join(ROOT, '_xc', 'vol_layer.json'), encoding='utf-8'))

INDEX = collections.defaultdict(set)
for v, lay in LAYER.items():
    if lay == 'canon':
        continue
    for a, b, nm in RBN.sections(RBN.P(v)):
        k = RBN.stem(nm)
        if k:
            INDEX[k].add(v)


def sn(p):
    try:
        return int(p.get('sutta_n'))
    except (TypeError, ValueError):
        return None


C = collections.Counter()
ex = []
for f in sorted(os.listdir(LINKS)):
    if not f.endswith('.links.json'):
        continue
    cv = f[:-len('.links.json')]
    cps = RBN.P(cv)
    if not cps:
        continue
    for si, rec in json.load(open(os.path.join(LINKS, f), encoding='utf-8')).items():
        i = int(si)
        if i >= len(cps):
            continue
        a = sn(cps[i])
        if a is None:
            continue
        ck = RBN.stem(RBN.canon_name(cv, i) or '')
        if not ck:
            continue
        n = cps[i].get('n')
        for layer in ('commentary', 'subcommentary'):
            for ent in rec.get(layer) or []:
                if ent.get('state') != 'direct':
                    continue
                key = ent.get('key') or ''
                if '#' not in key:
                    continue
                tv, o = key.rsplit('#', 1)
                o = int(o)
                tps = RBN.P(tv)
                if o >= len(tps):
                    continue
                od, _g, _w = ordinal.read(tps[o].get('text', ''))
                if od is None or od == a:
                    continue
                homes = (INDEX.get(ck) or set()) - {tv}
                # keep the destination in the same layer the link claims
                homes = {h for h in homes if LAYER.get(h) == LAYER.get(tv)}
                if not homes:
                    C['no other volume names it'] += 1
                    continue
                if len(homes) > 1:
                    C['several other volumes name it'] += 1
                    continue
                dv = homes.pop()
                cands = RBN.secs(dv)[1].get(ck) or []
                if not cands:
                    C['section vanished'] += 1
                    continue
                nn = ent.get('n', n)
                j, st = RBN.place(dv, cands[0][0], cands[0][1],
                                  nn if nn is not None else 1)
                C['rerouted'] += 1
                dps = RBN.P(dv)
                nod, _g2, _w2 = ordinal.read(dps[j].get('text', ''))
                if nod is None:
                    C['arrives where no ordinal is stated'] += 1
                else:
                    C['ordinal judged'] += 1
                    C['ordinal AGREES'] += (nod == a)
                    if nod == a and len(ex) < 12:
                        ex.append((cv, i, ck, key, od, '%s#%d' % (dv, j), nod, a, st))

print('TARGETED RE-ROUTE of ordinal-condemned links')
for k in ('rerouted', 'ordinal judged', 'ordinal AGREES',
          'arrives where no ordinal is stated', 'several other volumes name it',
          'no other volume names it', 'section vanished'):
    print('  %-38s %4d' % (k, C[k]))
if C['ordinal judged']:
    print('\n  the re-routed target states the canon\'s own position %.1f%% of the '
          'time (%d of %d)' % (100.0 * C['ordinal AGREES'] / C['ordinal judged'],
                               C['ordinal AGREES'], C['ordinal judged']))
    print('  the links they replace: 0 of %d, by construction' % C['ordinal judged'])
print('\nconfirmed re-routes:')
for e in ex:
    print('  %s#%-5d %-22s  %-14s(said %2d)  ->  %-14s(says %2d = canon %2d, %s)'
          % (e[0], e[1], e[2][:22], e[3], e[4], e[5], e[6], e[7], e[8]))
