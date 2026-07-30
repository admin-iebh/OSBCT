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

Writes to site/reader/linksk_new/ for verification before swapping.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site', 'reader', 'linksk_new')
os.makedirs(OUT, exist_ok=True)
_cache = {}
def load(v):
    if v not in _cache:
        _cache[v] = json.load(open(os.path.join(ROOT, 'site', v + '.json')))['paragraphs']
    return _cache[v]
def num(x):
    m = re.match(r'\d+', str(x if x is not None else ''))
    return int(m.group()) if m else None

def carry_vol(old, n, field):
    """target volume per canon ordinal, forward- then backward-filled."""
    tv = [None] * n
    last = None
    for i in range(n):
        arr = old.get(str(i), {}).get(field)
        if arr: last = arr[0]['key'].split('#')[0]
        tv[i] = last
    nxt = None
    for i in range(n - 1, -1, -1):
        if tv[i] is None: tv[i] = nxt
        else: nxt = tv[i]
    return tv

def relink(vol):
    d = load(vol)
    old = json.load(open(os.path.join(ROOT, 'site', 'reader', 'linksk', vol + '.links.json')))
    out = {}
    for field in ('commentary', 'subcommentary'):
        tv = carry_vol(old, len(d), field)
        i = 0
        while i < len(d):
            cv = tv[i]
            j = i
            while j < len(d) and tv[j] == cv: j += 1
            if cv:
                C = load(cv); cn = [num(p.get('n')) for p in C]
                cursor = -1
                for k in range(i, j):
                    N = num(d[k].get('n'))
                    if N is None: continue
                    while cursor + 1 < len(C) and cn[cursor + 1] is not None and cn[cursor + 1] <= N:
                        cursor += 1
                    if cursor >= 0 and cn[cursor] is not None:
                        st = 'direct' if cn[cursor] == N else 'covered'
                        out.setdefault(str(k), {}).setdefault(field, []).append(
                            {'key': f'{cv}#{cursor}', 'state': st, 'n': num(d[k].get('n'))})
            i = j
    json.dump(out, open(os.path.join(OUT, vol + '.links.json'), 'w'), ensure_ascii=False)
    # stats
    da = sum(1 for k in out if any(x['state'] == 'direct' for x in out[k].get('commentary', [])))
    dt = sum(1 for k in out if any(x['state'] == 'direct' for x in out[k].get('subcommentary', [])))
    return len(d), da, dt

if __name__ == '__main__':
    import sys
    man = json.load(open(os.path.join(ROOT, 'site', 'reader', 'manifest.json')))['volumes']
    vols = sys.argv[1:] or sorted(c for c, m in man.items() if m['layer'] == 'canon')
    for v in vols:
        n, da, dt = relink(v)
        print(f"{v}: {n} paras | direct-A {da} | direct-T {dt}")
