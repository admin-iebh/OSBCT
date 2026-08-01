#!/usr/bin/env python3
"""Rebuild cross-layer links by paragraph-number match.

The Chaṭṭha Saṅgāyana edition numbers each commentary / sub-commentary
paragraph to match the canon paragraph it explains (comm n=352 explains canon
n=352). The old interval-join linker got stuck on peyyāla passages, pinning
many canon paragraphs onto one commentary paragraph. This rebuild:

  * keeps each canon paragraph's existing TARGET VOLUME (so multi-volume
    commentaries such as Vinaya / Aṅguttara are never misrouted), and
  * fixes the ORDINAL inside that volume by a monotonic number match — canon N
    -> the commentary paragraph numbered N (state 'direct'); when the commentary
    has no paragraph N it falls back to the nearest earlier one (state 'covered').

THREE DEFECTS, all fixed 2026-08-01e.  Each is recorded because each produced a
result that looked fine.

1. !!! THE WALK COULD NEVER START ON A VOLUME WHOSE FIRST PARAGRAPH IS
   UNNUMBERED.  The cursor advanced with
   `cn[cursor+1] is not None and cn[cursor+1] <= N`, which at cursor=-1 tests
   `cn[0]`; if that is None the condition is false forever and the whole range
   emits NOTHING.  Ṭīkā volumes open with an unnumbered title line
   (`08DiT01#0` = "Sīlakkhandhavaggaṭīkā").  It did not bite before only because
   the ranges happened to begin elsewhere; constraining them exposes it at once.
   Fixed by walking a list of the NUMBERED paragraphs, so unnumbered ones are
   skipped rather than blocking.

2. !!! `carry_vol()` NEVER CONSULTED THE CONCORDANCE.  It takes the target
   volume from the PREVIOUS links and forward- AND backward-fills it, so **one
   stray link propagates over everything around it** — this is how the Apadāna
   acquired 4,841 links into the Nettiṭīkā.  Fixed: a volume the edition does
   not assign for that slot never enters the series, so it cannot be filled
   across its neighbours.  Spine-aware: a group's spine is its topmost present
   band, and the Visuddhimagga group has no canon, so its aṭṭhakathā holds the
   forward map.

3. !!! IT WROTE INSIDE `site/`.  `linksk_new/` is published by
   `deploy-pages.yml` and hashed into BUILD, so a dry run added dead files to
   the live site and moved the cache-buster for every visitor.  Output is now
   `_xc/linksk_rebuild/`.

!!!!! AND THE REBUILD ITSELF IS A REGRESSION. DO NOT SWAP IT IN (measured
2026-08-01e).  HANDOFF has recommended since 07-31b that "the real repair is to
teach `build_links_bynum.py` the concordance and rebuild".  That was done here,
with all three defects above fixed, and then MEASURED against the live maps:

                    targets   direct   reachable ¶   lemma rate   shift-1
    LIVE (pruned)    68,193   31,046   26,243 (71.1%)     48.6%     15.7%
    REBUILD          76,751   25,301   19,675 (53.3%)     44.4%     12.5%

**It loses on BOTH axes at once** — 6,568 fewer layer paragraphs reachable AND
weaker evidence per link — so there is no coverage/precision trade to weigh.
52 volumes lose, 12 gain, and the losses are catastrophic where the numbering
does not align: 40KhuA21 1,562 -> 461, 39KhuA20 1,138 -> 173, 05Kankha 478 ->
102, and **07ViT07 383 -> 1, which is the exact defect 07-30c repaired.**

THE MECHANISM IS VISIBLE IN THE COUNTS: the rebuild emits MORE targets (76,751)
onto FEWER distinct paragraphs (19,675).  Constraining `carry_vol` to assigned
volumes makes each range LONGER, and over a long range the monotonic number
match falls back to `covered` on the nearest earlier paragraph again and again —
**collapsing many canon paragraphs onto one commentary paragraph, which is the
precise failure this file's own docstring says the OLD interval-join linker had.**
Removing the wrong VOLUME does not make the ORDINAL match right.

SO: the prune is the better repair, and this rebuild should not be run against
the live maps.  What would actually raise reachability is the design sketched on
2026-07-27ah and never built — **number PROPOSES, content CONFIRMS**.  The
confirmer now exists: `_xc/classc_lemma.py` scores a proposed link by whether the
target quotes the canon paragraph, with a shift control to separate alignment
from vocabulary.  That is the direction; this is not.

The three fixes above are kept because each is a real defect regardless.

Writes to _xc/linksk_rebuild/ for verification before swapping.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_xc', 'linksk_rebuild')   # NOT under site/ — see defect 3
os.makedirs(OUT, exist_ok=True)
_cache = {}
SLOTS3 = ('canon', 'commentary', 'subcommentary')


def allowed_by_slot():
    """SPINE volume -> {slot: {volumes the edition assigns}}.  Defect 2."""
    import collections
    conc = json.load(open(os.path.join(ROOT, 'site/concordance.json'), encoding='utf-8'))
    ok = collections.defaultdict(lambda: {'commentary': set(), 'subcommentary': set()})
    for g in conc['groups']:
        f = {s: list(g[s]['files']) for s in SLOTS3}
        pres = [s for s in SLOTS3 if f[s]]
        if not pres:
            continue
        spine, below = pres[0], pres[1:]
        for v in f[spine]:
            for s in below:
                ok[v][s].update(f[s])
    return ok
def load(v):
    if v not in _cache:
        _cache[v] = json.load(open(os.path.join(ROOT, 'site', v + '.json')))['paragraphs']
    return _cache[v]
def num(x):
    m = re.match(r'\d+', str(x if x is not None else ''))
    return int(m.group()) if m else None

def carry_vol(old, n, field, allow):
    """Target volume per canon ordinal, forward- then backward-filled.

    THE `in allow` GUARD IS DEFECT 2's FIX and is the whole of it: a volume the
    edition does not assign for this slot never enters the series, so it can
    never be filled across its neighbours.
    """
    tv = [None] * n
    last = None
    for i in range(n):
        arr = old.get(str(i), {}).get(field)
        if arr:
            v = arr[0]['key'].split('#')[0]
            if v in allow:
                last = v
        tv[i] = last
    nxt = None
    for i in range(n - 1, -1, -1):
        if tv[i] is None: tv[i] = nxt
        else: nxt = tv[i]
    return tv

def relink(vol, ok=None):
    d = load(vol)
    old = json.load(open(os.path.join(ROOT, 'site', 'reader', 'linksk', vol + '.links.json')))
    ok = ok if ok is not None else allowed_by_slot()
    out = {}
    for field in ('commentary', 'subcommentary'):
        allow = ok[vol][field]
        if not allow:            # the edition assigns nothing here: leave it empty
            continue
        tv = carry_vol(old, len(d), field, allow)
        i = 0
        while i < len(d):
            cv = tv[i]
            j = i
            while j < len(d) and tv[j] == cv: j += 1
            if cv:
                C = load(cv)
                # DEFECT 1: walk the NUMBERED paragraphs only.  Indexing the raw
                # array stalls at cursor=-1 whenever C[0] carries no number.
                idx = [(t, num(p.get('n'))) for t, p in enumerate(C)]
                idx = [(t, nn) for t, nn in idx if nn is not None]
                cursor = -1
                for k in range(i, j):
                    N = num(d[k].get('n'))
                    if N is None: continue
                    while cursor + 1 < len(idx) and idx[cursor + 1][1] <= N:
                        cursor += 1
                    if cursor >= 0:
                        tord, tn = idx[cursor]
                        st = 'direct' if tn == N else 'covered'
                        out.setdefault(str(k), {}).setdefault(field, []).append(
                            {'key': f'{cv}#{tord}', 'state': st, 'n': N})
            i = j
    json.dump(out, open(os.path.join(OUT, vol + '.links.json'), 'w'), ensure_ascii=False)
    # stats
    da = sum(1 for k in out if any(x['state'] == 'direct' for x in out[k].get('commentary', [])))
    dt = sum(1 for k in out if any(x['state'] == 'direct' for x in out[k].get('subcommentary', [])))
    return len(d), da, dt

if __name__ == '__main__':
    import sys
    man = json.load(open(os.path.join(ROOT, 'site', 'reader', 'manifest.json')))['volumes']
    ok = allowed_by_slot()
    vols = [a for a in sys.argv[1:] if not a.startswith('-')] or \
           sorted(f[:-len('.links.json')]
                  for f in os.listdir(os.path.join(ROOT, 'site/reader/linksk'))
                  if f.endswith('.links.json'))
    print('writing to _xc/linksk_rebuild/ — the live maps are untouched\n')
    for v in vols:
        n, da, dt = relink(v, ok)
        print(f"{v}: {n} paras | direct-A {da} | direct-T {dt}")
