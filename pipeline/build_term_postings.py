#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit the search index as POSTINGS SHARDS and TEXT CHUNKS, so a search never
downloads a volume it only needs a few rows of.

WRITTEN 2026-09-05, replacing `build_term_buckets.py` and `site/index/tb/`.

WHY.  Measured on the live site that day (claude/search_and_dictionary_speed_brief.md
§1–§2, and pipeline/perf_baseline.json before this change): the wire was ALREADY
gzipped — Pages sends every /index/ file at 0.19–0.25 of its size — so bytes on
the wire were not the missing win.  What a search cost was the PER-VOLUME
`<VOL>.idx.json`: to count `tassā` the pages fetched 117 of them, 43 MB
compressed and 194 MB parsed, because postings and paragraph text lived in the
same file and the file was the unit of fetch.  The `tb/` buckets (key -> volume
list) only told the page WHICH shards to pull; every count still pulled them.

WHAT THIS EMITS.  Additive to the per-volume shards, which stay as the legacy
fallback and the gates' ground truth:

  site/index/tp/index.json   {vols, layers, cap, shards:{name:1}, tx:{vol:[starts]}}
  site/index/tp/<name>.json  {"terms": {key: {"<volIdx>": [[paraIdx, count], …]}}}
                             — the postings of every key whose FOLDED form
                             begins with <name>, so ONE fetch answers a
                             single-word search completely: occurrences,
                             paragraphs, volumes.  <name> is a folded prefix
                             of depth ≥ 2, deepened until the shard fits under
                             CAP — the same idiom, the same client lookup
                             (`shardName`) and the same `_` padding for keys
                             shorter than the depth as the dictionary's
                             stores use.  A shard can still exceed CAP when a
                             single key does (`ca`, `ti`: tens of thousands of
                             paragraphs); that is reported, not hidden.
  site/index/tp/k.txt        every exact key once, sorted, newline-joined —
                             the substring / suffix-wildcard sweep surface,
                             scanned with indexOf and never parsed.  The fold
                             switch folds it on the client; the fold is
                             length-preserving, so offsets carry across.
  site/index/tx/<VOL>/<i>.json {vol, from, paras:[…]} — the paragraphs of one
                             volume in order, packed into chunks of about
                             TXCAP bytes of text, so drawing a result row
                             fetches the chunk that holds it and nothing else.
                             `tx` in the manifest holds each volume's chunk
                             start ordinals; a chunk index is a binary search.

THE KEYS ARE EXACT (2026-09-05; see build_search_index.py) and the shard is
named by the FOLDED prefix, so `tassa` and `tassā` are two keys in one shard:
exact mode reads one of them, the fold switch reads both.  That is why the
name is folded and the key is not.

Verifies itself: every key of every per-volume shard lands in exactly one
postings shard with its postings byte-for-byte; the manifest's `shardName`
walk (re-implemented here) resolves every key to the shard that holds it;
k.txt carries every key once; the text chunks re-concatenate to every
volume's `paras` list exactly.

Usage:  python3 pipeline/build_term_postings.py [--cap BYTES] [--txcap BYTES]
"""
import json, os, sys, collections, bisect, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'site', 'index')
TP = os.path.join(IDX, 'tp')
TX = os.path.join(IDX, 'tx')
CAP = 500_000      # raw bytes per postings shard (about 120 KB gzipped)
TXCAP = 96_000     # raw bytes of paragraph text per chunk (about 24 KB gzipped)

_MAP = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṇ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ḷ': 'l'}


def fold(s):
    return ''.join(_MAP.get(c, c) for c in unicodedata.normalize('NFC', s).lower())


def dumps(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


def shard_name(f, names):
    """The client's walk: the shallowest existing name that prefixes the folded key."""
    for d in range(2, 41):
        n = (f[:d] + '_' * d)[:d]
        if n in names:
            return n
    return None


def main():
    global CAP, TXCAP
    if '--cap' in sys.argv: CAP = int(sys.argv[sys.argv.index('--cap') + 1])
    if '--txcap' in sys.argv: TXCAP = int(sys.argv[sys.argv.index('--txcap') + 1])
    man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'), encoding='utf-8'))['volumes']
    vols = sorted(man)
    FOLDER = {'canon': 'pali-unicode', 'commentary': 'atthakatha-unicode',
              'subcommentary': 'tika-unicode'}
    layers = [FOLDER.get(man[v]['layer'], 'pali-unicode') for v in vols]

    # ---- gather postings per key, and pack the text ------------------------
    post = collections.defaultdict(dict)          # key -> {vi: [[pi,c],…]}
    tx_starts = {}
    n_chunks = 0
    os.makedirs(TP, exist_ok=True)
    shards_seen = set()
    for vi, vol in enumerate(vols):
        sh = json.load(open(os.path.join(IDX, vol + '.idx.json'), encoding='utf-8'))
        for k, pl in sh['inv'].items():
            post[k][str(vi)] = pl
        # text chunks
        d = os.path.join(TX, vol); os.makedirs(d, exist_ok=True)
        starts, cur, size, ci = [], [], 0, 0
        P = sh['paras']
        for pi, p in enumerate(P):
            b = len((p.get('text') or '').encode('utf-8'))
            if cur and size + b > TXCAP:
                json.dump({'vol': vol, 'from': starts[-1], 'paras': cur},
                          open(os.path.join(d, '%d.json' % ci), 'w', encoding='utf-8'),
                          ensure_ascii=False, separators=(',', ':'))
                ci += 1; cur, size = [], 0
            if not cur: starts.append(pi)
            cur.append(p); size += b
        if cur:
            json.dump({'vol': vol, 'from': starts[-1], 'paras': cur},
                      open(os.path.join(d, '%d.json' % ci), 'w', encoding='utf-8'),
                      ensure_ascii=False, separators=(',', ':'))
            ci += 1
        # stale chunks from a previous build
        for f in os.listdir(d):
            if f.endswith('.json') and int(f[:-5]) >= ci:
                try: os.remove(os.path.join(d, f))
                except OSError: json.dump({'vol': vol, 'from': len(P), 'paras': []}, open(os.path.join(d, f), 'w'))
        tx_starts[vol] = starts
        n_chunks += ci
        print('  %-10s %5d ¶  %6d keys  %3d text chunks' % (vol, len(P), len(sh['inv']), ci))

    keys = sorted(post)
    print('%d exact keys across %d volumes' % (len(keys), len(vols)))
    bad = set()
    for k in keys: bad.update(set(fold(k)) - set('abcdefghijklmnopqrstuvwxyz'))
    if bad:
        print('REFUSING: folded keys carry characters outside a-z:', sorted(bad)); sys.exit(1)

    # ---- shard by folded prefix, deepening while over CAP ------------------
    size_of = {k: len(dumps(k)) + 1 + len(dumps(post[k])) + 1 for k in keys}
    groups = collections.defaultdict(list)
    for k in keys:
        f = fold(k); groups[(f[:2] + '__')[:2]].append(k)
    final = {}
    queue = sorted(groups.items())
    n_over = 0
    while queue:
        name, ks = queue.pop()
        d = len(name)
        total = sum(size_of[k] for k in ks) + 12
        splittable = not name.endswith('_') and any(len(fold(k)) > d for k in ks)
        if total <= CAP or not splittable:
            final[name] = ks
            if total > CAP: n_over += 1
            continue
        sub = collections.defaultdict(list)
        for k in ks:
            f = fold(k); sub[(f[:d + 1] + '_' * (d + 1))[:d + 1]].append(k)
        queue.extend(sorted(sub.items()))
    names = set(final)
    for name, ks in final.items():
        json.dump({'terms': {k: post[k] for k in ks}},
                  open(os.path.join(TP, name + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, separators=(',', ':'))
    open(os.path.join(TP, 'k.txt'), 'w', encoding='utf-8').write('\n'.join(keys))
    manifest = {'vols': vols, 'layers': layers, 'cap': CAP, 'txcap': TXCAP,
                'nkeys': len(keys), 'shards': {n: 1 for n in sorted(names)},
                'tx': tx_starts}
    json.dump(manifest, open(os.path.join(TP, 'index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    for f in os.listdir(TP):
        if f.endswith('.json') and f != 'index.json' and f[:-5] not in names:
            try: os.remove(os.path.join(TP, f)); print('removed stale shard:', f)
            except OSError:
                json.dump({'terms': {}}, open(os.path.join(TP, f), 'w')); print('emptied stale shard:', f)

    # ---- self-verification --------------------------------------------------
    back = {}
    for name in names:
        for k, v in json.load(open(os.path.join(TP, name + '.json'), encoding='utf-8'))['terms'].items():
            if k in back: print('FAIL: key in two shards:', k); sys.exit(1)
            back[k] = v
            got = shard_name(fold(k), names)
            if got != name:
                print('FAIL: shardName(%r) -> %r but the key is in %r' % (k, got, name)); sys.exit(1)
    if set(back) != set(post) or any(back[k] != post[k] for k in post):
        print('FAIL: shard union differs from the per-volume postings'); sys.exit(1)
    kt = open(os.path.join(TP, 'k.txt'), encoding='utf-8').read().split('\n')
    if kt != keys or len(set(kt)) != len(kt):
        print('FAIL: k.txt does not carry every key exactly once, sorted'); sys.exit(1)
    for vi, vol in enumerate(vols):
        sh = json.load(open(os.path.join(IDX, vol + '.idx.json'), encoding='utf-8'))
        got = []
        for ci in range(len(tx_starts[vol])):
            c = json.load(open(os.path.join(TX, vol, '%d.json' % ci), encoding='utf-8'))
            if c['from'] != len(got): print('FAIL: chunk start mismatch', vol, ci); sys.exit(1)
            got.extend(c['paras'])
        if got != sh['paras']:
            print('FAIL: text chunks do not reproduce', vol); sys.exit(1)
        # the client's chunk lookup: bisect on starts
        for pi in (0, len(sh['paras']) // 2, len(sh['paras']) - 1):
            ci = bisect.bisect_right(tx_starts[vol], pi) - 1
            if not (tx_starts[vol][ci] <= pi and (ci + 1 == len(tx_starts[vol]) or pi < tx_starts[vol][ci + 1])):
                print('FAIL: chunk bisect', vol, pi); sys.exit(1)
    sizes = sorted(((os.path.getsize(os.path.join(TP, n + '.json')), n) for n in names), reverse=True)
    total = sum(s for s, _ in sizes)
    print('postings shards: %d files, %.1f MB total, %d over CAP=%d (single-key shards)'
          % (len(names), total / 1e6, n_over, CAP))
    print('largest:', ', '.join('%s %.2f MB' % (n, s / 1e6) for s, n in sizes[:6]))
    txtotal = sum(os.path.getsize(os.path.join(TX, v, f)) for v in vols for f in os.listdir(os.path.join(TX, v)))
    print('text chunks: %d files, %.1f MB total; manifest %d bytes; k.txt %.1f MB'
          % (n_chunks, txtotal / 1e6, os.path.getsize(os.path.join(TP, 'index.json')),
             os.path.getsize(os.path.join(TP, 'k.txt')) / 1e6))
    print('shard union == per-volume postings: EXACT (%d keys); text chunks == paras: EXACT' % len(back))


if __name__ == '__main__':
    main()
