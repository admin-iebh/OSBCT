# -*- coding: utf-8 -*-
"""Every consumer of the paragraph `id`, and what the new scheme does to it.

The survey is `grep`-complete over the LIVE files in site/ and pipeline/ (the
.bak/.pre* copies are excluded -- there are 180 of them and none is served).
"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from b1_ids import assign
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
VOL = '20KhuA01'

print("""CONSUMERS OF `id` (grep over live site/ and pipeline/):

 1 pipeline/rekey_apparatus.py:16   byid[p['id']].append(i)
       apparatus/<VOL>.app.json is KEYED BY id; this converts it to the
       ordinal-keyed .appk.json the reader loads.  Treats the id as an OPAQUE
       string and already handles duplicates by footnote-marker matching.
       *** THE ONE HARD DEPENDENCY: .app.json's keys must match the corpus. ***
 2 pipeline/build_links.py:35,61    build_target_resolver / resolve_old
       id -> [(n,key)], used only to convert legacy links/<vol>.fwd.json (which
       carry ids) into <VOL>#<ord> keys.  Opaque string.
 3 pipeline/build_search_index.py:73  copies `id` into the shard's paras
       Carried, not parsed; the shard also carries `ord`, which is what search
       now uses.
 4 site/search.html:232            fallback deep link '#'+vol+'/'+id
       Only when a shard has no `ord`.  encodeURIComponent'd.
 5 site/reader/reader2.html:2406   resolveHash: paras.findIndex(p=>p.id===rest)
       Accepts the old '#VOL/<id>' bookmark form; linear scan, first match.
       Its own comment records 12,110 corpus-wide collisions as the reason
       search stopped emitting ids.
 (site/errata.html:110 `e.id` is an ERRATUM record id, not a paragraph id.)

NOTHING PARSES THE id.  No split('/'), no regex over it, anywhere.  So an
appended '.K' cannot break a consumer's parse; the only thing that can break is
a LOOKUP against a file that stores the old ids -- consumer 1 and consumer 2.
""")

ship = json.load(open('%s/site/%s.json' % (ROOT, VOL), encoding='utf-8'))['paragraphs']
reseg = json.load(open('%s/_xc/reseg/%s.json' % (ROOT, VOL), encoding='utf-8'))['paragraphs']
app = json.load(open('%s/site/reader/apparatus/%s.app.json' % (ROOT, VOL), encoding='utf-8'))

for label, paras in (('shipped corpus', ship), ('re-segmented corpus', reseg)):
    for scheme, ids in (('old ids', [p['id'] for p in paras]),
                        ('new ids', assign(paras))):
        by = collections.defaultdict(list)
        for i, x in enumerate(ids):
            by[x].append(i)
        hit = sum(1 for k in app if k in by)
        amb = sum(1 for k in app if len(by.get(k, ())) > 1)
        print('  %-20s %-8s apparatus keys that resolve: %2d of %2d   '
              'resolving to MORE THAN ONE paragraph: %d'
              % (label, scheme, hit, len(app), amb))
print("""
READING: the new scheme costs the apparatus NOTHING that re-segmentation had
not already cost it -- .app.json is keyed on `book/vagga/sutta/n`, and the
numbered opener keeps its `n` and its id under re-segmentation.  What it does
NOT fix is that a note now resolves to the OPENER of a run rather than to the
paragraph that carries its marker.  That is the apparatus problem of the
phase-1 doc section 4, and the answer there stands: re-run
pipeline/rebuild_apparatus.py against the re-segmented corpus.""")

# --- the one measured cost, and the one-line mitigation ---------------------
# Exactly ONE apparatus key stops resolving: the numbered collision
# `Khuddakapāṭhaṭṭhakathā/X/Tirokuṭṭasuttavaṇṇanā/4`, whose two paragraphs
# become ...4.1 and ...4.2.  rekey_apparatus.py only has to index by BASE as
# well, and its existing marker-distribution branch then runs unchanged.
import re
BASE = re.compile(r'\.\d+$')
for label, paras in (('re-segmented corpus', reseg),):
    ids = assign(paras)
    by = collections.defaultdict(list)
    for i, x in enumerate(ids):
        by[x].append(i)
        b = BASE.sub('', x)
        if b != x:
            by[b].append(i)
    hit = sum(1 for k in app if k in by)
    dist = sum(1 for k in app if len(by.get(k, ())) > 1)
    print('  %-20s new ids + BASE index: apparatus keys that resolve: %d of %d '
          '(%d go through the existing duplicate-id distribution branch)'
          % (label, hit, len(app), dist))
