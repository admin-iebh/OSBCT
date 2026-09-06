#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drop from the dictionary manifests the per-shard diagnostics the panel never
reads, so the first lookup of a visit does not download them.

WRITTEN 2026-09-06.  `perf_search.js` gated every row at one 520 KB ceiling
and the lookup rows went red: `stores/lookup_eval/index.json` was 653 KB
(129 KB gz), fetched before the first dictionary lookup of a visit.  563 KB
of it was `shards: {set: {name: {keys: N, bytes: N}}}` — and `panel.js`
tests `m[name]` and nothing else (shardName / eShardName / hwlook).  The
counts are the builder's self-report, useful to a maintainer, useless on the
wire.

WHAT THIS DOES, for each of
    stores/lookup/index.json          (375 KB)
    stores/lookup_eval/index.json     (653 KB)
    stores/lookup_eval/hw/index.json  (272 KB)
  * writes `index.diag.json` beside it holding the per-shard {keys, bytes}
    exactly as they were (a maintainer's file; served if uploaded, fetched by
    nothing);
  * rewrites `shards` as {set: {name: 1}} (or {name: 1} for hw/, which has no
    sets), every other top-level key byte-for-byte unchanged;
  * verifies: the set of shard names per set is identical, every non-`shards`
    key round-trips equal, and the diag file reproduces the original when
    merged back.

Idempotent: a manifest already slimmed is left alone (its diag file must
already exist, or the script refuses — nothing may be lost).

THE STORE IS ON R2.  Nothing here reaches a reader until `pipeline/r2_upload.sh`
runs from the host and `WLV` in site/reader/panel.js is bumped — upload first,
bump second.

Usage:  python3 pipeline/slim_store_manifests.py [--write]
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['stores/lookup/index.json', 'stores/lookup_eval/index.json',
         'stores/lookup_eval/hw/index.json']


def shape(sh):
    """'sets' for {set: {name: entry}}, 'flat' for {name: entry}."""
    first = next(iter(sh.values()))
    return 'sets' if isinstance(first, dict) and first and \
        all(isinstance(v, dict) or v == 1 for v in first.values()) and \
        not ('keys' in first and 'bytes' in first) else 'flat'


def is_slim(sh):
    if shape(sh) == 'sets':
        return all(v == 1 for m in sh.values() for v in m.values())
    return all(v == 1 for v in sh.values())


def split(sh):
    """-> (slim, diag)."""
    if shape(sh) == 'sets':
        return ({s: {n: 1 for n in m} for s, m in sh.items()}, sh)
    return ({n: 1 for n in sh}, sh)


def keyset(sh):
    if shape(sh) == 'sets':
        return {s: sorted(m) for s, m in sh.items()}
    return sorted(sh)


def main():
    write = '--write' in sys.argv
    for rel in FILES:
        p = os.path.join(ROOT, rel); dp = p[:-5] + '.diag.json'
        raw = open(p, 'rb').read(); d = json.loads(raw)
        sh = d['shards']
        before = len(raw)
        if is_slim(sh):
            if not os.path.exists(dp):
                print('REFUSING: %s is already slim but %s is missing' % (rel, os.path.relpath(dp, ROOT))); sys.exit(1)
            print('%-36s already slim (%d bytes), diag present' % (rel, before)); continue
        slim, diag = split(sh)
        # ---- verify before writing anything ---------------------------------
        if keyset(slim) != keyset(diag):
            print('FAIL: shard names differ for', rel); sys.exit(1)
        out = dict(d); out['shards'] = slim
        for k in d:
            if k != 'shards' and out[k] != d[k]:
                print('FAIL: key %s changed' % k); sys.exit(1)
        merged = dict(out); merged['shards'] = diag
        if json.dumps(merged, sort_keys=True) != json.dumps(d, sort_keys=True):
            print('FAIL: diag does not reproduce the original for', rel); sys.exit(1)
        body = json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        print('%-36s %7d -> %7d bytes; shard names %s' % (rel, before, len(body),
              ', '.join('%s:%d' % (s, len(m)) for s, m in slim.items()) if shape(slim) == 'sets' else str(len(slim))))
        if write:
            json.dump({'note': 'per-shard {keys, bytes} removed from index.json on 2026-09-06 — the panel never read them; a maintainer file, fetched by nothing',
                       'shards': diag}, open(dp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
            tmp = p + '.tmp'; open(tmp, 'wb').write(body); os.replace(tmp, p)
            back = json.loads(open(p, 'rb').read())
            if back != out: print('FAIL: re-read differs'); sys.exit(1)
    print('written' if write else 'DRY RUN — pass --write')


if __name__ == '__main__':
    main()
