#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit the term index in prefix buckets, so the first search of a page load
does not pay for the whole map.

WHY.  `terms.compact.json` is 22 MB raw / 5.3 MB gzipped and 643,965 keys.
Before ANY search can answer, the whole of it must download and — the worse
half — parse: 643,965 strings and as many arrays is past what iOS Safari
gives a tab, which is the 2026-07-31b freeze report on search.html, and it
is most of "the search is slow" on a cold load anywhere.  Measured 2026-08-08:
the substring sweep itself is 7–15 ms; the load is the cost.

WHAT THIS EMITS (additive — `terms.compact.json` stays, both as the gates'
ground truth and as the fallback for a reader shipped before the UIs learn
the buckets):

  site/index/tb/meta.json     {"vols": [...], "layers": [...]} — tiny, first
  site/index/tb/k.txt         every term key, newline-joined, ~7 MB raw and
                              ~1.6 MB gzipped — the SWEEP surface: a substring
                              or suffix-wildcard scan is `indexOf` over one
                              string, with NO JSON parse of 643,965 entries
  site/index/tb/<p2>.json     {"terms": {key: [volIdx...]}} for every key
                              whose fold starts with those two letters;
                              1-letter keys go to `<c>_.json`

The charset of the folded keys is a–z only (checked at build time and
asserted), so bucket filenames are safe as-is.  273 buckets; the largest
(`pa`) holds 62,924 keys ≈ 2.1 MB raw — the worst single fetch, against
22 MB for everything today.

THE CONSUMERS ARE NOT WIRED YET.  This build is data only; reader2.html and
search.html still read `terms.compact.json`.  The wiring is the delicate
half — `matchTerms` goes async and every await must respect the keystroke
ticket — and it is done as its own change with the gate extended first.

Usage:  python3 pipeline/build_term_buckets.py
Verifies itself: every key lands in exactly one bucket, the union of buckets
reproduces the source map EXACTLY, and k.txt carries every key once.
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'site', 'index', 'terms.compact.json')
OUT = os.path.join(ROOT, 'site', 'index', 'tb')

def main():
    T = json.load(open(SRC, encoding='utf-8'))
    terms, vols, layers = T['terms'], T['vols'], T['layers']
    chars = set()
    for k in terms: chars.update(k)
    bad = chars - set('abcdefghijklmnopqrstuvwxyz')
    if bad:
        print('REFUSING: keys carry characters outside a-z:', sorted(bad))
        sys.exit(1)
    os.makedirs(OUT, exist_ok=True)

    buckets = collections.defaultdict(dict)
    for k, v in terms.items():
        p = k[:2] if len(k) > 1 else k + '_'
        buckets[p][k] = v

    json.dump({'vols': vols, 'layers': layers},
              open(os.path.join(OUT, 'meta.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    keys = sorted(terms)
    open(os.path.join(OUT, 'k.txt'), 'w', encoding='utf-8').write('\n'.join(keys))
    for p, m in buckets.items():
        json.dump({'terms': m}, open(os.path.join(OUT, p + '.json'), 'w',
                  encoding='utf-8'), ensure_ascii=False)

    # ---- self-verification: the union of what was written IS the source ----
    back = {}
    nfiles = 0
    for f in os.listdir(OUT):
        if f in ('meta.json', 'k.txt') or not f.endswith('.json'): continue
        nfiles += 1
        for k, v in json.load(open(os.path.join(OUT, f), encoding='utf-8'))['terms'].items():
            if k in back:
                print('FAIL: key in two buckets:', k); sys.exit(1)
            back[k] = v
    if back != terms:
        print('FAIL: bucket union differs from the source map'); sys.exit(1)
    kt = open(os.path.join(OUT, 'k.txt'), encoding='utf-8').read().split('\n')
    if sorted(kt) != keys or len(kt) != len(set(kt)):
        print('FAIL: k.txt does not carry every key exactly once'); sys.exit(1)
    sizes = sorted(((os.path.getsize(os.path.join(OUT, f)), f)
                    for f in os.listdir(OUT)), reverse=True)
    total = sum(s for s, _ in sizes)
    print('buckets: %d files, %.1f MB total (source %.1f MB)' %
          (nfiles, total / 1e6, os.path.getsize(SRC) / 1e6))
    print('largest:', ', '.join('%s %.2f MB' % (f, s / 1e6) for s, f in sizes[:4]))
    print('bucket union == source map: EXACT (%d keys)' % len(back))

if __name__ == '__main__':
    main()
