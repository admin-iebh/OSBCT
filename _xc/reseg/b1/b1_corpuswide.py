# -*- coding: utf-8 -*-
"""Is the within-page counter enough EVERYWHERE, or only in 20KhuA01?

Two questions, both measured over every shipped volume:
 1. is every colliding id group confined to ONE pdf page?  (if not, the
    within-page counter is not sufficient corpus-wide and the scheme has to
    say so rather than be assumed)
 2. build_links.build_target_resolver() pools ids across ALL the volumes of a
    concordance group, so a cross-VOLUME id collision is a real defect there.
    How many are there?
"""
import json, os, glob, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
vols = sorted(os.path.basename(f)[:-5] for f in glob.glob(ROOT + '/site/*.json')
              if os.path.basename(f)[0].isdigit())
tot = coll = spanning = 0
worst = []
allids = collections.defaultdict(set)
for v in vols:
    try:
        ps = json.load(open('%s/site/%s.json' % (ROOT, v), encoding='utf-8'))['paragraphs']
    except Exception:
        continue
    by = collections.defaultdict(list)
    for i, p in enumerate(ps):
        by[p['id']].append(i)
        allids[p['id']].add(v)
    tot += len(ps)
    g = {k: x for k, x in by.items() if len(x) > 1}
    coll += sum(len(x) - 1 for x in g.values())
    sp = [k for k, x in g.items() if len({ps[i].get('pdf_page') for i in x}) > 1]
    spanning += len(sp)
    if sp:
        worst.append((v, len(sp), sp[:2]))
print('volumes %d   paragraphs %d   duplicate-id paragraphs %d'
      % (len(vols), tot, coll))
print('colliding id groups that span MORE THAN ONE pdf page: %d' % spanning)
for w in worst[:15]:
    print('   ', w)
xv = {k: sorted(s) for k, s in allids.items() if len(s) > 1}
print('ids used in more than one VOLUME: %d  (build_links pools these)' % len(xv))
for k in list(xv)[:5]:
    print('   ', k, xv[k][:4])

# --- and does the SCHEME (rank inside the group, not inside the page) clear
#     every volume, including the 4,125 groups that span pages? -------------
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b1_ids import assign, collisions
bad = []
for v in vols:
    try:
        ps = json.load(open('%s/site/%s.json' % (ROOT, v), encoding='utf-8'))['paragraphs']
    except Exception:
        continue
    c = collisions(assign(ps))
    if c:
        bad.append((v, len(c)))
print('SCHEME applied to all %d shipped volumes -> volumes still colliding: %d'
      % (len(vols), len(bad)), bad[:10])
