#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WHY DID THE NAME REPAIR NOT FIRE ON THE LINKS THE ORDINAL CONDEMNS?

`relink_by_name.py` moves a link when the canon paragraph's section name matches
a section in the TARGET VOLUME.  It deliberately never re-routes volumes.  The
ordinal condemns 320 `direct` links; the name concurs on 96.9% of the ones it
can judge, so the repair should have fired and did not.  This replays its
decision on exactly those links and reports which branch each took.

AND THEN IT ASKS THE QUESTION THAT DECIDES WHAT THE LINK IS WORTH: is there a
section with the canon sutta's name ANYWHERE in the commentary layer?

  same volume     the repair should have fired.  A defect in it.
  another volume  the target volume is wrong, not the ordinal inside it.  Only
                  a re-route reaches this, and `build_links_bynum.py` recorded
                  that a re-route constrained by the concordance lost on both
                  axes -- so this is evidence to weigh, not a licence.
  nowhere         the commentary does not gloss this sutta under this name.
                  The link should not be MOVED.  It should not EXIST.

Writes nothing.
"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import ordinal_words as ordinal
import relink_by_name as RBN

SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')

LAYER = json.load(open(os.path.join(ROOT, '_xc', 'vol_layer.json'), encoding='utf-8'))

# every section name in every non-canon volume, stem -> volumes
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


B = collections.Counter()     # relink branch
W = collections.Counter()     # where the name lives
ex = collections.defaultdict(list)

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
        cname = RBN.canon_name(cv, i)
        ck = RBN.stem(cname) if cname else None
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
                # --- replay relink_by_name's branch
                n = ent.get('n', cps[i].get('n'))
                if not ck or n is None:
                    B['no anchor (canon section unnamed)'] += 1
                    br = 'no anchor'
                else:
                    cands = RBN.secs(tv)[1].get(ck) or []
                    if not cands:
                        B['no matching section in target volume'] += 1
                        br = 'no section'
                    else:
                        j, st = RBN.place(tv, cands[0][0], cands[0][1], n)
                        if j == o:
                            B['fired, and chose this very paragraph'] += 1
                            br = 'chose it'
                        else:
                            B['would MOVE it -- the repair has not been re-run'] += 1
                            br = 'would move'
                # --- where does the canon name live in the commentary layer?
                homes = INDEX.get(ck) or set() if ck else set()
                if not ck:
                    w = 'canon paragraph has no section name'
                elif not homes:
                    w = 'NOWHERE in any commentary volume'
                elif tv in homes:
                    w = 'in the target volume'
                else:
                    w = 'in another volume: %s' % ','.join(sorted(homes)[:2])
                W[w.split(':')[0]] += 1
                if len(ex[br]) < 4:
                    ex[br].append((cv, i, ck or '-', key, od, a, w))

print('THE %d ORDINAL-CONDEMNED DIRECT LINKS, by the branch relink_by_name takes'
      % sum(B.values()))
for k, c in B.most_common():
    print('  %-46s %4d' % (k, c))
print('\nwhere a section with the canon sutta\'s name actually lives:')
for k, c in W.most_common():
    print('  %-46s %4d' % (k, c))
print()
for br, rows in ex.items():
    print('--- %s' % br)
    for cv, i, ck, key, od, a, w in rows:
        print('    %s#%-5d %-24s -> %-14s says %2d, canon is %2d   [%s]'
              % (cv, i, ck[:24], key, od, a, w))
