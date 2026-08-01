#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Do the cross-layer links point only into the volumes the EDITION assigns?

`site/concordance.json` records the edition's own canon -> aṭṭhakathā -> ṭīkā
mapping, read from `concordanciatextos.pdf`.  `build_links_bynum.py` never
consults it: it "keeps each canon paragraph's existing TARGET VOLUME and fixes
the ORDINAL inside that volume by a monotonic number match".  So a target volume
that was wrong before the rebuild stays wrong, silently and at scale.

Found by the first version of this check on 2026-07-31b: **the Milindapañha
(28Khu11), which the concordance says has NO commentary and NO subcommentary,
carried a target on essentially every numbered paragraph.**

-----------------------------------------------------------------------------
2026-08-01 — TWO DEFECTS IN THE FIRST VERSION OF THIS CHECK, both corrected
here.  Recorded because its published numbers were wrong.

  1. **It assumed the link layer's spine is always the canon.**  It is not.  A
     group's SPINE is its topmost present band, and the Visuddhimagga group has
     **no canon at all**, so its spine is the *commentary* (51Vism01, 52Vism02)
     and its ṭīkā's `rev` map points its `canon` field back at a commentary
     volume.  `reader2.html` already routes on "is this volume its group's
     spine?" and says so in a comment at `jumpFrom`; this check did not.
     Consequence: **870 of the 2,408 rev violations it reported were its own
     false positives** — 26VsmT02 -> 52Vism02 (520) and 25VsmT01 -> 51Vism01
     (350), i.e. the two largest entries and 36% of the total.  **The real rev
     figure is 1,538 (5.8%), not 2,408 (9.1%).**

  2. **It filtered on `manifest.layer == 'canon'`, so it never opened the two
     Vism forward maps at all.**  They hold 870 targets, checked here for the
     first time: **0 violations.**  The forward total is therefore 102,027
     targets, not 101,157; the violation count is unchanged at 36,997 (36.3%).

-----------------------------------------------------------------------------
The two classes, which must be treated differently (see `fix_link_targets.py`):

  Class A — the edition assigns NO volume for that slot, so the target cannot
      be right whatever it is.  No judgement involved.
  Class C — the edition assigns some volume for that slot but not this one.  A
      commentary volume can straddle two canon volumes, so some of these are
      real seams.  Not adjudicable by volume identity alone.

Usage: python3 _xc/check_link_targets.py [--quiet]
       LINKSK=_xc/linksk_fixed python3 _xc/check_link_targets.py   (check a candidate)
Exit 0 = every link target is one the edition assigns.
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKSK = os.environ.get('LINKSK') or os.path.join(ROOT, 'site/reader/linksk')
SLOTS = ('canon', 'commentary', 'subcommentary')


def concordance_model():
    """Spine-aware allow-lists, built the way `reader2.html` routes.

    Returns (allow_fwd, allow_rev, assigns_any, slots_of):
      allow_fwd[spine_vol][slot]  volumes that spine volume may point at
      allow_rev[layer_vol]        spine volumes that layer volume may point back at
      assigns_any[spine_vol][slot] non-empty iff the edition assigns anything there
      slots_of[layer_vol]         the slot name(s) that layer volume occupies
    """
    conc = json.load(open(os.path.join(ROOT, 'site/concordance.json'), encoding='utf-8'))
    allow_fwd = collections.defaultdict(lambda: {'commentary': set(), 'subcommentary': set()})
    assigns = collections.defaultdict(lambda: {'commentary': set(), 'subcommentary': set()})
    allow_rev = collections.defaultdict(set)
    slots_of = collections.defaultdict(set)
    for g in conc['groups']:
        f = {s: list(g[s]['files']) for s in SLOTS}
        present = [s for s in SLOTS if f[s]]
        if not present:
            continue
        spine, below = present[0], present[1:]
        for s in below:
            for v in f[spine]:
                allow_fwd[v][s].update(f[s])
                assigns[v][s].update(f[s])
            for v in f[s]:
                slots_of[v].add(s)
                allow_rev[v].update(f[spine])
    return allow_fwd, allow_rev, assigns, slots_of


def scan_forward(allow_fwd, assigns):
    tot = 0
    cls = collections.defaultdict(collections.Counter)      # vol -> {'A':n,'C':n}
    det = collections.defaultdict(collections.Counter)      # vol -> target vol counts
    for fn in sorted(os.listdir(LINKSK)):
        if not fn.endswith('.links.json'):
            continue
        v = fn[:-len('.links.json')]
        d = json.load(open(os.path.join(LINKSK, fn), encoding='utf-8'))
        al = allow_fwd.get(v, {'commentary': set(), 'subcommentary': set()})
        for _o, e in d.items():
            for slot in ('commentary', 'subcommentary'):
                for t in (e.get(slot) or []):
                    tot += 1
                    tv = t['key'].split('#')[0]
                    if tv in al[slot]:
                        continue
                    cls[v]['A' if not assigns.get(v, al)[slot] else 'C'] += 1
                    det[v][tv] += 1
    return tot, cls, det


def scan_rev(allow_rev, assigns, slots_of):
    tot = 0
    cls = collections.defaultdict(collections.Counter)
    det = collections.defaultdict(collections.Counter)
    for fn in sorted(os.listdir(LINKSK)):
        if not fn.endswith('.rev.json'):
            continue
        v = fn[:-len('.rev.json')]
        d = json.load(open(os.path.join(LINKSK, fn), encoding='utf-8'))
        al = allow_rev.get(v, set())
        mine = slots_of.get(v, set())
        for _o, e in d.items():
            tot += 1
            sv = (e.get('canon') or '').split('#')[0]
            if sv in al:
                continue
            # Class A iff the spine volume it names assigns NOTHING in this
            # volume's own slot — then no target in that direction can be right.
            possible = any(assigns.get(sv, {}).get(s) for s in mine)
            cls[v]['C' if possible else 'A'] += 1
            det[v][sv] += 1
    return tot, cls, det


def report(title, tot, cls, det, limit=12):
    A = sum(c['A'] for c in cls.values())
    C = sum(c['C'] for c in cls.values())
    print('%s: %s entries, %s violations (%.1f%%) — Class A %s, Class C %s'
          % (title, f'{tot:,}', f'{A + C:,}', 100.0 * (A + C) / tot if tot else 0.0,
             f'{A:,}', f'{C:,}'))
    for v, c in sorted(cls.items(), key=lambda kv: -sum(kv[1].values()))[:limit]:
        print('   %-12s %6d  (A %5d  C %5d)  -> %s'
              % (v, sum(c.values()), c['A'], c['C'],
                 ', '.join('%s:%d' % (k, n) for k, n in det[v].most_common(4))))
    return A + C


if __name__ == '__main__':
    quiet = '--quiet' in sys.argv
    allow_fwd, allow_rev, assigns, slots_of = concordance_model()
    ft, fc, fd = scan_forward(allow_fwd, assigns)
    rt, rc, rd = scan_rev(allow_rev, assigns, slots_of)
    nf = report('FORWARD (<VOL>.links.json)', ft, fc, fd, 0 if quiet else 12)
    print()
    nr = report('REVERSE (<VOL>.rev.json)  ', rt, rc, rd, 0 if quiet else 12)
    sys.exit(1 if (nf or nr) else 0)
