# -*- coding: utf-8 -*-
"""Stamp the pbreak maps that already exist, WITHOUT re-deriving them.

THIS ASSERTS FRESHNESS, IT DOES NOT PROVE IT.  118 maps were derived before
`derive.py` learned to record its sources, and re-deriving all of them costs an
hour of PDF parsing.  So the first stamp is a claim about the state of the tree
at the moment it is written, and it is worth exactly as much as the evidence
beside it:

  * `check_derived.py --deep`'s two-address agreement, which is independent of
    any stamp -- it asks whether each record's `rawOffset` and its
    (`drawnIndex`, `drawnOffset`) still name the same printed page opening;
  * the structural check, 0 faults on all 118.

Both are reported by `check_derived.py`.  From here on `derive.py` stamps as it
writes and this script is only needed after another bulk change.

Usage: python3 _xc/pagemark/stamp_existing.py [--write] [VOL...]
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import derive as D

PD = os.path.join(D.ROOT, 'site/reader/pbreak')


def main(a):
    write = '--write' in a
    vols = [x for x in a if not x.startswith('--')] or sorted(
        os.path.basename(f)[:-5] for f in os.listdir(PD)
        if f.endswith('.json') and not f.startswith('_'))
    p = os.path.join(PD, '_stamp.json')
    cur = D.jload(p, {}) or {}
    added = same = moved = 0
    for v in vols:
        st = D.stamp_of(v)
        if v not in cur:
            added += 1
        elif cur[v] == st:
            same += 1
        else:
            moved += 1
        cur[v] = st
    print('%d volumes: %d newly stamped, %d unchanged, %d re-stamped'
          % (len(vols), added, same, moved))
    if write:
        json.dump({k: cur[k] for k in sorted(cur)}, open(p, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=0, sort_keys=True)
        print('wrote %s' % os.path.relpath(p, D.ROOT))
    else:
        print('(dry run -- pass --write)')


if __name__ == '__main__':
    main(sys.argv[1:])
