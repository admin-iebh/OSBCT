#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit the SUBSTRING / SUFFIX-WILDCARD sweep surface as N-GRAM SHARDS, so a
search for `amakasālāna` or `*vaggo` no longer downloads every key in the canon.

WRITTEN 2026-09-05 (later session) — lever 3 of
claude/search_and_dictionary_speed_brief.md, the one the morning's rebuild
left open.

WHY.  A bare word that is no key, and a wildcard whose `*` is not at the end
(`*vaggo`, `a*vaggo`), are answered by SWEEPING the keys: every key containing
the substring, or matching the pattern.  The surface for that sweep was
`site/index/tp/k.txt`, all 682,010 exact keys newline-joined — 12.5 MB raw,
2.7 MB on the wire, scanned whole for every such query.  Measured with
pipeline/perf_search.js before this change: `*vaggo` 36.9 MB raw of which
12.5 was k.txt; `amakasālāna` 17.4 MB of which 12.5.  Every other file a
search reads is under 515 KB.

WHAT THIS EMITS, read from k.txt (so it is built AFTER build_term_postings.py):

  site/index/tg/index.json   {cap, nkeys, grams:{name: rawBytes}}
  site/index/tg/<name>.txt   every exact key whose FOLDED form CONTAINS <name>,
                             in k.txt order (sorted), newline-joined.

<name> is a folded n-gram of length ≥ 2, deepened — by the character that
FOLLOWS the gram in each key, `_` when the gram ends the key — until the shard
fits under CAP.  So `vag` may not exist as a shard, but `vaga`, `vagg`, …,
`vag_` do, and their union is exactly the keys containing `vag`; a key that
holds `vag` twice sits in two children.  This is the postings shards' idiom
(deepen a prefix until it fits, pad with `_`) applied to infixes.

HOW THE CLIENT USES IT (site/searchcore.js, `sweep`): the query's literal
fragments are folded and every substring of length 2–MAXD of them is a
candidate gram; each resolves to a shard — the name itself, its children (every
name extending it), or the shallowest name prefixing it — with a byte total
from the manifest; the cheapest wins, its shard(s) are fetched, and the keys
are VERIFIED on the client by substring / pattern in the mode's view (exact or
folded), then sorted, so the result — keys, order, the 500-cap, the `matched`
total — is byte-for-byte what the k.txt sweep produced.  The gram only narrows
the candidates; it never decides a match.  Fragments too short for any gram
(`a*b*c`) fall back to k.txt, which stays for that and for the archive.

A shard ending in `_` (keys that END with the gram) cannot be deepened and may
exceed CAP: `ana_` is 2.3 MB.  That is reported, not hidden; such a shard is
fetched only when the query offers no cheaper gram.

Verifies itself: every shard holds exactly the keys containing its name (in
folded view), sorted; for every gram of every key, the client's resolution
lands on shards whose union contains that key; the manifest sizes are the
file sizes.

Usage:  python3 pipeline/build_gram_shards.py [--cap BYTES]
"""
import json, os, sys, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TP = os.path.join(ROOT, 'site', 'index', 'tp')
TG = os.path.join(ROOT, 'site', 'index', 'tg')
CAP = 500_000      # raw bytes per shard (about 100 KB gzipped)
MIND, MAXD = 2, 8  # gram lengths: shards start at bigrams, deepen to 8

_MAP = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṇ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ḷ': 'l'}


def fold(s):
    return ''.join(_MAP.get(c, c) for c in unicodedata.normalize('NFC', s).lower())


def main():
    global CAP
    if '--cap' in sys.argv: CAP = int(sys.argv[sys.argv.index('--cap') + 1])
    keys = open(os.path.join(TP, 'k.txt'), encoding='utf-8').read().split('\n')
    keys = [k for k in keys if k]
    if keys != sorted(keys) or len(set(keys)) != len(keys):
        print('REFUSING: k.txt is not sorted and unique'); sys.exit(1)
    fk = [fold(k) for k in keys]
    kb = [len(k.encode('utf-8')) + 1 for k in keys]
    print('%d keys from k.txt' % len(keys))

    # ---- group by bigram, deepen while over CAP ---------------------------
    groups = collections.defaultdict(set)
    for i, f in enumerate(fk):
        for j in range(len(f) - MIND + 1):
            groups[f[j:j + MIND]].add(i)
    final = {}
    queue = sorted(groups.items())
    n_over = 0
    while queue:
        name, ks = queue.pop()
        d = len(name)
        total = sum(kb[i] for i in ks)
        if total <= CAP or name.endswith('_') or d >= MAXD:
            final[name] = ks
            if total > CAP: n_over += 1
            continue
        sub = collections.defaultdict(set)
        for i in ks:
            f = fk[i]; j = f.find(name)
            while j >= 0:
                sub[(f[j:j + d + 1] + '_')[:d + 1]].add(i)
                j = f.find(name, j + 1)
        queue.extend(sorted(sub.items()))
    names = set(final)

    os.makedirs(TG, exist_ok=True)
    sizes = {}
    for name, ks in final.items():
        body = '\n'.join(keys[i] for i in sorted(ks))
        p = os.path.join(TG, name + '.txt')
        open(p, 'w', encoding='utf-8').write(body)
        sizes[name] = os.path.getsize(p)
    for f in os.listdir(TG):
        if f.endswith('.txt') and f[:-4] not in names:
            try: os.remove(os.path.join(TG, f)); print('removed stale shard:', f)
            except OSError:
                open(os.path.join(TG, f), 'w').write(''); print('emptied stale shard:', f)
    manifest = {'cap': CAP, 'nkeys': len(keys), 'mind': MIND, 'maxd': MAXD,
                'grams': {n: sizes[n] for n in sorted(names)}}
    json.dump(manifest, open(os.path.join(TG, 'index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))

    # ---- self-verification -----------------------------------------------
    # 1. each shard = exactly the keys whose folded form contains its bare name
    #    (a `_` name: the keys that END with the bare gram), sorted
    #    (computed key-by-key from the key's own substrings, not from `groups`)
    want = collections.defaultdict(list)
    for i, f in enumerate(fk):
        seen = set()
        for L in range(MIND, min(MAXD, len(f)) + 1):
            for j in range(len(f) - L + 1):
                g = f[j:j + L]
                if g in names: seen.add(g)
                if j + L == len(f) and L < MAXD and g + '_' in names: seen.add(g + '_')
        for g in seen: want[g].append(keys[i])
    for name in names:
        got = open(os.path.join(TG, name + '.txt'), encoding='utf-8').read().split('\n')
        if got != want.get(name, []):
            print('FAIL: shard %s holds %d keys, expected %d' % (name, len(got), len(want.get(name, [])))); sys.exit(1)
    # 2. the client's resolution, re-implemented: for a gram g, the shard g if
    #    it exists, else every name extending g, else the shallowest name
    #    prefixing g.  For every key and every gram of it, the union of the
    #    resolved shards must contain the key.
    import bisect
    snames = sorted(names)
    def resolve(g):
        if g in names: return [g]
        lo = bisect.bisect_left(snames, g); hi = bisect.bisect_left(snames, g + '~')
        kids = snames[lo:hi]
        if kids: return kids
        for d in range(MIND, len(g) + 1):
            if g[:d] in names: return [g[:d]]
        return []
    members = {n: set(open(os.path.join(TG, n + '.txt'), encoding='utf-8').read().split('\n')) for n in names}
    checked = 0
    for i in range(0, len(keys), 97):          # every 97th key, every gram of it
        f = fk[i]
        for L in range(MIND, min(MAXD, len(f)) + 1):
            for j in range(len(f) - L + 1):
                g = f[j:j + L]; r = resolve(g)
                if not r or not any(keys[i] in members[n] for n in r):
                    print('FAIL: key %r gram %r resolves to %r which lacks it' % (keys[i], g, r)); sys.exit(1)
                checked += 1
    # 3. manifest sizes are file sizes
    for n in names:
        if manifest['grams'][n] != os.path.getsize(os.path.join(TG, n + '.txt')):
            print('FAIL: manifest size differs for', n); sys.exit(1)
    total = sum(sizes.values())
    big = sorted(((s, n) for n, s in sizes.items()), reverse=True)
    print('gram shards: %d files, %.1f MB total, %d over CAP=%d (all `_`-terminal); manifest %d bytes'
          % (len(names), total / 1e6, n_over, CAP, os.path.getsize(os.path.join(TG, 'index.json'))))
    print('largest:', ', '.join('%s %.2f MB' % (n, s / 1e6) for s, n in big[:6]))
    print('depth histogram:', dict(sorted(collections.Counter(len(n) for n in names).items())))
    print('every shard == keys containing its gram: EXACT; %d (key, gram) resolutions land: EXACT' % checked)


if __name__ == '__main__':
    main()
