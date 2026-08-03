#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Derive the reverse link maps from the forward ones. They had drifted apart.

WHY.  Reader, 2026-08-03: "you removed the T from the Aratisutta, only A
remains, but in the A of the Aratisutta there is a T button."  Chasing it found
two faults, and this is the second and larger one.

`hasBand()` answers for a paragraph in a BAND by going through
`linksk/<VOL>.rev.json` back to its canon record.  For the Aratisutta's
commentary paragraph, `19AnA03#255`, that map has NO ENTRY -- while the forward
map says plainly

    16An02 #383  commentary -> {"key": "19AnA03#255", "state": "direct",
                                "n": 113, "by": "name"}

`19AnA03.rev.json` holds 168 entries for a volume the forward maps reach far
more often than that.  The rev maps were never rebuilt after
`pipeline/relink_by_name.py` moved 4,043 targets on 2026-08-02, so every
repaired link is invisible from the band side.  The reader saw it as one
paragraph answering two ways about the same fact.

WHAT THIS DOES.  The forward maps are the authority; the reverse is derivable
from them and nothing else.  For every target of every canon record:

    rev[target_vol][target_ord] = {canon: "<canon vol>#<ord>", state, slot}

`state` is carried through unchanged -- `direct` and `covered` both, because
`covered` records stay in the maps as the evidence they are (see
`claude/half_the_links_were_never_said.md`) and it is the READER that filters
to `direct`.  A rev map that dropped them would decide that question here, in
the data, where it cannot be revisited.

WHERE TWO CANON PARAGRAPHS CLAIM THE SAME TARGET, `direct` wins over `covered`,
and then the LOWER canon ordinal, so the answer is deterministic and does not
depend on file order.

SAFETY.  Writes to `_xc/linksk_rev_new/` by default and prints the comparison.
`--apply` writes into `site/reader/linksk/`.  Every existing file is compared
before anything is written: a volume that LOSES entries is reported, because
that would mean the forward maps no longer reach something the reverse map
still claimed.

Usage:
  python3 pipeline/build_rev.py            # dry run, compare only
  python3 pipeline/build_rev.py --apply
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS = os.path.join(ROOT, 'site', 'reader', 'linksk')
OUT = os.path.join(ROOT, '_xc', 'linksk_rev_new')
SLOTS = ('commentary', 'subcommentary')


def build():
    rev = collections.defaultdict(dict)
    for fn in sorted(os.listdir(LINKS)):
        if not fn.endswith('.links.json'):
            continue
        cv = fn[:-len('.links.json')]
        L = json.load(open(os.path.join(LINKS, fn), encoding='utf-8'))
        for ordk, e in L.items():
            try:
                i = int(ordk)
            except ValueError:
                continue
            for slot in SLOTS:
                for t in (e.get(slot) or []):
                    key = t.get('key') or ''
                    if '#' not in key:
                        continue
                    tv, to = key.rsplit('#', 1)
                    cand = {'canon': '%s#%d' % (cv, i),
                            'state': t.get('state'), 'slot': slot}
                    cur = rev[tv].get(to)
                    if cur is None:
                        rev[tv][to] = cand
                        continue
                    # direct beats covered; then the lower canon ordinal
                    better = ((cur['state'] != 'direct' and cand['state'] == 'direct')
                              or (cur['state'] == cand['state']
                                  and int(cur['canon'].rsplit('#', 1)[1]) > i))
                    if better:
                        rev[tv][to] = cand
    return rev


def main():
    apply_ = '--apply' in sys.argv
    rev = build()
    dest = LINKS if apply_ else OUT
    os.makedirs(dest, exist_ok=True)
    grew = shrank = same = new = 0
    lost = []
    print('%-12s %8s %8s %8s' % ('volume', 'was', 'now', 'delta'))
    for tv in sorted(rev):
        old_p = os.path.join(LINKS, tv + '.rev.json')
        old = json.load(open(old_p, encoding='utf-8')) if os.path.exists(old_p) else None
        n_old = len(old) if old is not None else 0
        n_new = len(rev[tv])
        if old is None:
            new += 1
        elif n_new > n_old:
            grew += 1
        elif n_new < n_old:
            shrank += 1
            missing = [k for k in old if k not in rev[tv]]
            lost.append((tv, n_old, n_new, missing[:5]))
        else:
            same += 1
        if abs(n_new - n_old) > 0:
            print('%-12s %8d %8d %+8d' % (tv, n_old, n_new, n_new - n_old))
        with open(os.path.join(dest, tv + '.rev.json'), 'w', encoding='utf-8') as fh:
            json.dump(rev[tv], fh, ensure_ascii=False)
    print('\n%d volumes grew, %d shrank, %d unchanged, %d new' % (grew, shrank, same, new))
    if lost:
        print('\nSHRANK — the forward maps no longer reach these, check before applying:')
        for tv, a, b, ex in lost[:12]:
            print('   %-12s %d -> %d   e.g. ords %s' % (tv, a, b, ex))
    # the invariant this exists for
    bad = 0
    for fn in sorted(os.listdir(LINKS)):
        if not fn.endswith('.links.json'):
            continue
        cv = fn[:-len('.links.json')]
        L = json.load(open(os.path.join(LINKS, fn), encoding='utf-8'))
        for ordk, e in L.items():
            for slot in SLOTS:
                for t in (e.get(slot) or []):
                    if t.get('state') != 'direct':
                        continue
                    key = t.get('key') or ''
                    if '#' not in key:
                        continue
                    tv, to = key.rsplit('#', 1)
                    if to not in rev.get(tv, {}):
                        bad += 1
    print('\ndirect forward links with no reverse entry: %d  (must be 0)' % bad)
    print('written to %s%s' % (dest, '' if apply_ else '   [dry run — pass --apply]'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
