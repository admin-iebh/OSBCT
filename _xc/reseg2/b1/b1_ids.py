# -*- coding: utf-8 -*-
"""BLOCKER 1 -- make the paragraph `id` unique under re-segmentation.

WHAT `id` IS.  `_fnprobe/rebuild_corpus.py` (the corpus rebuilder that produced
the shipped 109) sets

    id = slug(book) / slug(vagga) / slug(sutta) / TAIL
    TAIL = str(n)              for a numbered paragraph
         = 'u%d' % pdf_page    for an unnumbered one

MEASURED CLASS OF EVERY COLLISION, shipped AND re-segmented: the members of a
colliding group always share ONE pdf page.  7/7 shipped, 190/190 re-segmented.
There is no multi-page collision anywhere in this volume.  So a WITHIN-PAGE
counter is both sufficient and minimal -- nothing coarser is needed and nothing
finer is available (the paragraph record carries no line index).

THE SCHEME.  Leave a base that is used once alone; disambiguate every member of
a group that is used more than once by appending '.K', K = 1-based rank of the
paragraph in ORDINAL order inside that group.  Because every group is confined
to one page, '.K' IS the within-page counter.

  * already-unique ids never change  (102/109 shipped ids survive verbatim)
  * the suffix is append-only, so `base = id.rsplit('.',1)[0]` recovers it
  * no consumer parses the id (see b1_consumers.md), so a new character class
    cannot break a parse; '.' is URL-safe under encodeURIComponent

Run:  python3 _xc/reseg/b1/b1_ids.py
      python3 _xc/reseg/b1/b1_ids.py --control
"""
import json, os, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def _PRE(p):
    '''prefer the pre-re-segmentation backup, so preparation can be re-run
    after apply2.py has written into site/'''
    q = p + '.prereseg2'
    return q if os.path.exists(os.path.join(ROOT, q)) else p


VOL = os.environ['VOL']
OUT = os.path.join(ROOT, '_xc', 'reseg2', 'b1')


def base_id(p):
    """The id as the corpus rebuilder writes it -- read off the record, never
    recomputed, so this cannot drift from what produced the shipped file."""
    return p['id']


def assign(paras, counter=True, broken_counter=False):
    groups = collections.defaultdict(list)
    for i, p in enumerate(paras):
        groups[base_id(p)].append(i)
    if not counter:
        return [base_id(p) for p in paras]
    out = [None] * len(paras)
    if broken_counter:
        pc = collections.Counter()
        for i, p in enumerate(paras):
            b = base_id(p)
            if len(groups[b]) == 1:
                out[i] = b
            else:
                pc[p.get('pdf_page')] += 1
                out[i] = '%s.%d' % (b, pc[p.get('pdf_page')])
        return out
    for b, idxs in groups.items():
        if len(idxs) == 1:
            out[idxs[0]] = b
        else:
            for k, i in enumerate(sorted(idxs), 1):
                out[i] = '%s.%d' % (b, k)
    return out


def collisions(ids):
    c = collections.Counter(ids)
    return {k: v for k, v in c.items() if v > 1}


def check(paras, ids, label):
    r = {}
    col = collisions(ids)
    r['paras'] = len(paras)
    r['distinct'] = len(set(ids))
    r['colliding_ids'] = len(col)
    r['worst'] = max([0] + list(col.values()))
    by = collections.defaultdict(list)
    for i, p in enumerate(paras):
        by[base_id(p)].append(i)
    multi = [b for b, v in by.items()
             if len(v) > 1 and len({paras[i].get('pdf_page') for i in v}) > 1]
    r['base_groups_spanning_pages'] = len(multi)
    bad_rt = sum(1 for p, nid in zip(paras, ids)
                 if (nid if nid == base_id(p) else nid.rsplit('.', 1)[0]) != base_id(p))
    r['roundtrip_failures'] = bad_rt
    bad_ord = 0
    for b, idxs in by.items():
        if len(idxs) < 2:
            continue
        parts = [ids[i].rsplit('.', 1) for i in sorted(idxs)]
        if any(len(x) != 2 or not x[1].isdigit() for x in parts):
            bad_ord += 1
            continue
        ks = [int(x[1]) for x in parts]
        if ks != list(range(1, len(ks) + 1)):
            bad_ord += 1
    r['order_failures'] = bad_ord
    r['unchanged_ids'] = sum(1 for p, nid in zip(paras, ids) if nid == base_id(p))
    print('%-30s p %4d  distinct %4d  colliding %3d  worst %d-way  '
          'groups spanning pages %d  roundtrip-fail %d  order-fail %d  unchanged %d'
          % (label, r['paras'], r['distinct'], r['colliding_ids'], r['worst'],
             r['base_groups_spanning_pages'], r['roundtrip_failures'],
             r['order_failures'], r['unchanged_ids']))
    return r


def load(path):
    return json.load(open(os.path.join(ROOT, path), encoding='utf-8'))['paragraphs']


def main():
    ship = load(_PRE('site/%s.json' % VOL))
    reseg = load('_xc/reseg2/%s.json' % VOL)
    print('=== BEFORE (no counter) ===')
    check(ship, assign(ship, counter=False), 'shipped, base ids')
    check(reseg, assign(reseg, counter=False), 're-segmented, base ids')
    print('=== AFTER (within-page counter) ===')
    a1 = check(ship, assign(ship), 'shipped, new scheme')
    b1 = check(reseg, assign(reseg), 're-segmented, new scheme')
    assert a1['colliding_ids'] == 0 and b1['colliding_ids'] == 0, 'SCHEME FAILED'

    if '--control' in sys.argv:
        print('=== NEGATIVE CONTROLS (each MUST fire) ===')
        fired = 0
        c = check(reseg, assign(reseg, counter=False), 'CONTROL counter removed')
        ok = c['colliding_ids'] > 0; fired += ok
        print('    -> fired:', ok)
        ids = assign(reseg, broken_counter=True)
        c2 = check(reseg, ids, 'CONTROL per-page counter')
        ok = c2['order_failures'] > 0 or c2['roundtrip_failures'] > 0
        fired += ok
        print('    -> fired:', ok)
        ids = assign(reseg); ids[5] = ids[4]
        c3 = check(reseg, ids, 'CONTROL one id duplicated')
        ok = c3['colliding_ids'] > 0; fired += ok
        print('    -> fired:', ok)
        ids = assign(reseg)
        by = collections.defaultdict(list)
        for i, p in enumerate(reseg):
            by[base_id(p)].append(i)
        g = sorted(next(v for v in by.values() if len(v) > 2))
        ids[g[0]], ids[g[1]] = ids[g[1]], ids[g[0]]
        c4 = check(reseg, ids, 'CONTROL K swapped in a group')
        ok = c4['order_failures'] > 0; fired += ok
        print('    -> fired:', ok)
        print('CONTROLS THAT FIRED: %d of 4' % fired)
        return

    os.makedirs(OUT, exist_ok=True)
    json.dump({'vol': VOL,
               'scheme': 'base + ".K" when the base repeats; K is the 1-based '
                         'ordinal rank inside the group, and every group is '
                         'confined to one pdf page',
               'ids': assign(reseg)},
              open(os.path.join(OUT, 'ids_%s.json' % VOL), 'w', encoding='utf-8'),
              ensure_ascii=False)
    json.dump({'vol': VOL, 'ids': assign(ship)},
              open(os.path.join(OUT, 'ids_shipped_%s.json' % VOL), 'w',
                   encoding='utf-8'), ensure_ascii=False)
    print('wrote', os.path.join(OUT, 'ids_%s.json' % VOL))


if __name__ == '__main__':
    main()
