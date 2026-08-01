#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-derive the cross-layer links, constrained to the volumes the EDITION assigns.

THE DEFECT (found 2026-07-31b).  36,997 of 101,157 link targets — 36.6% — point
into a volume `concordanciatextos.pdf` does not give that canon volume.  The
reader draws them as that paragraph's commentary, so a reader of the
**Milindapañha, which the edition gives no commentary at all**, is shown the
Nettiṭīkā and told it is the commentary.

THE MECHANISM, which is why it is so widespread.  `build_links_bynum.py` never
consults the concordance.  It takes the target volume from the PREVIOUS links
via `carry_vol()`, which forward- **and backward-fills** it across the volume:

    tv[i] = the volume of the last link at or before i, else the next one after

So **one stray link propagates across every paragraph around it**.  That is how
the Apadāna acquired 4,841 links into the Nettiṭīkā, and how nine Khuddaka canon
volumes came to claim a ṭīkā the edition gives only to the Netti.

Not staleness, and not a misreading of the concordance — tested with the bolded
lemma: it occurs in the canon paragraph 50.0% of the time for links the
concordance allows (19,511 pairs) and 10.4% for links it does not (4,494).

TWO REPAIRS, and the DEFAULT IS THE CONSERVATIVE ONE.

  `--prune` (default) — remove every target whose volume the edition does not
      assign for that slot, and **change nothing else**.  Every surviving link
      keeps its exact key and state, so the diff is auditable line by line: it
      removes 36,997 wrong targets and touches nothing correct.  A paragraph
      whose only target was wrong stops showing a commentary, which is the
      truth: it was being shown the wrong one.

  `--rederive` — additionally rebuild the carried-volume series from what
      survives and re-run the number match, to recover coverage where the
      edition DOES assign a volume but the wrong one had been filled across it.
      **This moves ordinals in volumes that had nothing wrong with them**
      (measured: 48,531 targets change key), so it is not the default and must
      be verified before it is trusted.  Prefer fixing `build_links_bynum.py`
      itself and rebuilding cleanly.

Where the edition assigns nothing — the Khuddaka ṭīkā outside the Netti, the
whole Milindapañha — the slot is left EMPTY.  That is the truth, and an empty
band is honest where a wrong one is not.

Writes to `_xc/linksk_fixed/` — outside `site/`, so it is neither published
nor hashed into BUILD — and never over the live maps.
Usage: python3 pipeline/fix_link_targets.py [VOL…]
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'site/reader/linksk')
# NOT under site/ — anything there is hashed into BUILD and PUBLISHED.
# The first run put it in site/reader/, which added 40 dead files to the
# live site and moved the cache-buster for every visitor.
OUT = os.path.join(ROOT, '_xc/linksk_fixed')
_cache = {}


def load(v):
    if v not in _cache:
        _cache[v] = json.load(open(os.path.join(ROOT, 'site', v + '.json'),
                                   encoding='utf-8'))['paragraphs']
    return _cache[v]


def num(x):
    m = re.match(r'\d+', str(x if x is not None else ''))
    return int(m.group()) if m else None


def allowed_by_slot():
    """SPINE volume -> {'commentary': {...}, 'subcommentary': {...}}, per the edition.

    !!! KEYED ON THE GROUP'S SPINE, NOT ON THE CANON (fixed 2026-08-01).  The
    first version keyed on `g['canon']['files']`, so the Visuddhimagga group —
    which HAS no canon, and whose aṭṭhakathā 51Vism01/52Vism02 is therefore the
    spine that holds the forward map — got no entry at all.  An absent entry is
    an EMPTY allow-set, and an empty allow-set means `prune()` removes
    everything: extending the run to all forward maps emptied both Vism files,
    **destroying 870 links that had 0 violations.**  Caught by the preservation
    audit, which is the whole reason for counting preserved targets rather than
    trusting the removal count.
    """
    conc = json.load(open(os.path.join(ROOT, 'site/concordance.json'), encoding='utf-8'))
    ok = collections.defaultdict(lambda: {'commentary': set(), 'subcommentary': set()})
    for g in conc['groups']:
        f = {s: list(g[s]['files']) for s in ('canon', 'commentary', 'subcommentary')}
        present = [s for s in ('canon', 'commentary', 'subcommentary') if f[s]]
        if not present:
            continue
        spine, below = present[0], present[1:]
        for v in f[spine]:
            for s in below:
                ok[v][s].update(f[s])
    return ok


def carry_vol(links, n, field, allow):
    """Target volume per canon ordinal — but ONLY volumes the edition assigns.

    Identical to `build_links_bynum.carry_vol` except for the `in allow` guard,
    which is the whole fix: an unassigned volume never enters the series, so it
    can never be filled across its neighbours.
    """
    tv = [None] * n
    last = None
    for i in range(n):
        arr = links.get(str(i), {}).get(field)
        if arr:
            v = arr[0]['key'].split('#')[0]
            if v in allow:
                last = v
        tv[i] = last
    nxt = None
    for i in range(n - 1, -1, -1):
        if tv[i] is None:
            tv[i] = nxt
        else:
            nxt = tv[i]
    return tv


def prune(vol, allow, only_empty=True):
    """Remove disallowed targets. Everything surviving is byte-identical.

    THE DEFAULT REMOVES ONLY CLASS A — slots where the edition assigns NO volume
    at all, so no judgement is involved: the Khuddaka ṭīkā (the edition gives one
    only to the Netti) and the whole Milindapañha. **22,719 targets, every one of
    them impossible.**

    The other 14,278 are NOT cleanly wrong, and I could not separate them
    reliably. A commentary volume can straddle two canon volumes — the Jātaka
    commentary runs continuously across 22Khu05 and 23Khu06 — so
    `20Khu03 -> 33KhuA14` may be a genuine seam, while `39Abhi11 -> 48AbhiA01`
    (Paṭṭhāna IV pointing at the Dhammasaṅgaṇī commentary) plainly is not. Any
    grouping coarse enough to call the first legitimate calls the second
    legitimate too. **Deciding those needs a finer test than volume identity —
    do not guess at them.** `--all-violations` prunes them as well; it is not
    the default and should not be run without checking what it removes.
    """
    old = json.load(open(os.path.join(SRC, vol + '.links.json'), encoding='utf-8'))
    out = {}
    for o, e in old.items():
        keep = {}
        for field in ('commentary', 'subcommentary'):
            arr = e.get(field) or []
            av = allow[field]
            if only_empty and av:
                keep[field] = arr                      # leave judgement calls alone
                continue
            arr = [t for t in arr if t['key'].split('#')[0] in av]
            if arr:
                keep[field] = arr
        keep = {k: v for k, v in keep.items() if v}
        if keep:
            out[o] = keep
    return old, out


def relink(vol, allow):
    d = load(vol)
    old = json.load(open(os.path.join(SRC, vol + '.links.json'), encoding='utf-8'))
    out = {}
    for field in ('commentary', 'subcommentary'):
        av = allow[field]
        if not av:                      # the edition assigns nothing: leave it empty
            continue
        tv = carry_vol(old, len(d), field, av)
        i = 0
        while i < len(d):
            cv = tv[i]
            j = i
            while j < len(d) and tv[j] == cv:
                j += 1
            if cv:
                # !!! THE ORIGINAL WALK COULD NEVER START (latent in
                # `build_links_bynum.py`, hit here 2026-07-31b).  It advanced
                # with `cn[cursor+1] is not None and cn[cursor+1] <= N`, so if
                # the target volume's FIRST paragraph is unnumbered the
                # condition is false at cursor=-1 and the whole range emits
                # nothing.  Ṭīkā volumes open with an unnumbered title line
                # (`08DiT01#0` is "Sīlakkhandhavaggaṭīkā"), so constraining the
                # ranges to assigned volumes — which moves where each range
                # begins — wiped every subcommentary link on the first run.
                # Walking a list of the NUMBERED paragraphs only removes the
                # trap: unnumbered paragraphs are skipped rather than blocking.
                C = load(cv)
                idx = [(t, num(p.get('n'))) for t, p in enumerate(C)]
                idx = [(t, nn) for t, nn in idx if nn is not None]
                cursor = -1                      # position within `idx`
                for k in range(i, j):
                    N = num(d[k].get('n'))
                    if N is None:
                        continue
                    while cursor + 1 < len(idx) and idx[cursor + 1][1] <= N:
                        cursor += 1
                    if cursor >= 0:
                        tord, tn = idx[cursor]
                        st = 'direct' if tn == N else 'covered'
                        out.setdefault(str(k), {}).setdefault(field, []).append(
                            {'key': f'{cv}#{tord}', 'state': st, 'n': N})
            i = j
    return old, out


def count(links, allow):
    tot = bad = direct = 0
    for o, e in links.items():
        for slot in ('commentary', 'subcommentary'):
            for t in (e.get(slot) or []):
                tot += 1
                if t['key'].split('#')[0] not in allow[slot]:
                    bad += 1
                if t.get('state') == 'direct':
                    direct += 1
    return tot, bad, direct




# ---------------------------------------------------------------------------
# THE REVERSE MAPS — added 2026-08-01, and the reason nothing was swapped in on
# 07-31c.  Pruning the forward maps alone leaves `linksk/<VOL>.rev.json` still
# asserting that those ṭīkā paragraphs belong to those canon volumes, so a
# reader who opened 21KhuT01 and pressed P would still land in the Apadāna.
# The two maps are separately derived and must be pruned together.
#
# `rev.json` is `{layer_ordinal: {"canon": "<SPINE>#<ord>", "state": ...}}`.
# **The `canon` field does not always name a canon volume.**  A group's SPINE is
# its topmost present band, and the Visuddhimagga group has no canon, so
# 25VsmT01/26VsmT02 point back at 51Vism01/52Vism02 — the aṭṭhakathā standing in
# the spine's place.  `reader2.html` routes on "is this its group's spine?" at
# `jumpFrom`; the first version of `check_link_targets.py` did not, and reported
# those 870 legitimate entries as violations.  See that file's header.

SLOTS3 = ('canon', 'commentary', 'subcommentary')


def rev_model():
    """(allow_rev, assigns, slots_of) — spine-aware, the way the reader routes."""
    conc = json.load(open(os.path.join(ROOT, 'site/concordance.json'), encoding='utf-8'))
    allow_rev = collections.defaultdict(set)
    assigns = collections.defaultdict(lambda: {'commentary': set(), 'subcommentary': set()})
    slots_of = collections.defaultdict(set)
    for g in conc['groups']:
        f = {s: list(g[s]['files']) for s in SLOTS3}
        present = [s for s in SLOTS3 if f[s]]
        if not present:
            continue
        spine, below = present[0], present[1:]
        for s in below:
            for v in f[spine]:
                assigns[v][s].update(f[s])
            for v in f[s]:
                slots_of[v].add(s)
                allow_rev[v].update(f[spine])
    return allow_rev, assigns, slots_of


def prune_rev(vol, allow_rev, assigns, slots_of, all_violations=False):
    """Class A only by default: drop entries naming a spine volume that assigns
    NOTHING in this volume's own slot, so no target in that direction can be
    right.  Everything kept is byte-identical."""
    old = json.load(open(os.path.join(SRC, vol + '.rev.json'), encoding='utf-8'))
    al = allow_rev.get(vol, set())
    mine = slots_of.get(vol, set())
    out = {}
    for o, e in old.items():
        sv = (e.get('canon') or '').split('#')[0]
        if sv not in al:
            possible = any(assigns.get(sv, {}).get(s) for s in mine)
            if all_violations or not possible:
                continue
        out[o] = e
    return old, out


def run_rev(all_violations=False):
    allow_rev, assigns, slots_of = rev_model()
    files = sorted(f for f in os.listdir(SRC) if f.endswith('.rev.json'))
    ot = nt = 0
    print('\n%-12s %10s %10s %10s' % ('vol', 'entries', 'removed', 'kept'))
    for fn in files:
        v = fn[:-len('.rev.json')]
        old, new = prune_rev(v, allow_rev, assigns, slots_of, all_violations)
        json.dump(new, open(os.path.join(OUT, fn), 'w', encoding='utf-8'),
                  ensure_ascii=False)
        ot += len(old); nt += len(new)
        if len(old) != len(new):
            print('%-12s %10d %10d %10d' % (v, len(old), len(old) - len(new), len(new)))
    print('%-12s %10d %10d %10d' % ('TOTAL', ot, ot - nt, nt))
    print('%d rev maps written to _xc/linksk_fixed/' % len(files))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    ok = allowed_by_slot()
    man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'),
                         encoding='utf-8'))['volumes']
    REDERIVE = '--rederive' in sys.argv
    ALLV = '--all-violations' in sys.argv
    print('mode: %s\n' % ('REDERIVE — ordinals move in volumes that were fine; verify before trusting'
                          if REDERIVE else
                          ('PRUNE ALL VIOLATIONS — includes 14,278 the concordance cannot adjudicate'
                           if ALLV else
                           'PRUNE CLASS A (default) — only slots the edition assigns nothing at all')))
    # EVERY volume that HAS a forward map, not every canon volume.  Selecting on
    # `manifest.layer == 'canon'` skipped 51Vism01 and 52Vism02 — the
    # Visuddhimagga group has no canon, so its aṭṭhakathā is the spine and holds
    # the forward map.  They carry 870 targets and 0 violations, but omitting
    # them left `_xc/linksk_fixed/` an INCOMPLETE mirror, which is a trap at
    # apply time: copying the directory over `linksk/` would have deleted them.
    vols = [v for v in sys.argv[1:] if not v.startswith('-')] or \
           sorted(f[:-len('.links.json')] for f in os.listdir(SRC)
                  if f.endswith('.links.json'))
    T = collections.Counter()
    print('%-12s %26s   %26s' % ('', 'BEFORE', 'AFTER'))
    print('%-12s %8s %8s %8s   %8s %8s %8s'
          % ('vol', 'targets', 'wrong', 'direct', 'targets', 'wrong', 'direct'))
    for v in vols:
        if not os.path.exists(os.path.join(SRC, v + '.links.json')):
            continue
        allow = ok[v]
        old, new = relink(v, allow) if REDERIVE else prune(v, allow, only_empty=ALLV is False)
        o = count(old, allow); n = count(new, allow)
        json.dump(new, open(os.path.join(OUT, v + '.links.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False)
        T['ot'] += o[0]; T['ob'] += o[1]; T['od'] += o[2]
        T['nt'] += n[0]; T['nb'] += n[1]; T['nd'] += n[2]
        if o[1] or o[0] != n[0]:
            print('%-12s %8d %8d %8d   %8d %8d %8d' % (v, o[0], o[1], o[2], n[0], n[1], n[2]))
    print('\n%-12s %8d %8d %8d   %8d %8d %8d'
          % ('TOTAL', T['ot'], T['ob'], T['od'], T['nt'], T['nb'], T['nd']))
    run_rev(all_violations=ALLV)
    print('\nwritten to _xc/linksk_fixed/ — outside site/, the live maps are untouched')
