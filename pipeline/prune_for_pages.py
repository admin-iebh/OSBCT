# -*- coding: utf-8 -*-
"""Shrink the PUBLISHED copy of site/ so GitHub Pages can accept it.

The deploy of `8c86ae0` failed. Measured cause: `site/` is **1.62 GB** and
GitHub Pages publishes at most 1 GB. Two things account for nearly all of the
excess, and neither is served to a reader:

  1. **478 MB of backup files** — `nav.json.prereseg`, `reader2.html.bak_topbar`,
     `pageindex.json.bak_20260730_stale` and 1,748 more. 411 MB of it in
     `site/reader/` alone. They are working history and belong in the repository;
     nothing fetches them.
  2. **362 MB of plain JSON that is never requested.** `site/lookup_eval/dpd/`
     carries 11,229 `.json` files *and* their 11,229 `.gz` counterparts, and
     `index.json` declares `gz: ["dpd"]`. `panel.js` `jfetch(url, gz)` fetches
     `url + '.gz'` when the manifest says so and **never falls back to the plain
     file** — verified in the source, not assumed. So for a gz set the `.json`
     is dead weight in the published tree.

1.62 GB − 478 MB − 362 MB = **0.78 GB**, under the limit with room.

THIS RUNS ON THE CHECKOUT INSIDE THE WORKFLOW, NOT ON THE REPOSITORY. Nothing
is deleted from git; the pruning exists only in the artifact that is uploaded.
Dry run unless `--write`, and it prints what it removes so the deploy log is a
record rather than a mystery.

    python3 pipeline/prune_for_pages.py
    python3 pipeline/prune_for_pages.py --write
"""
import os, re, sys, json, collections

ROOT = 'site'
WRITE = '--write' in sys.argv
M = 1024 ** 2

# Conservative and explicit.  A bare `*.pre*` would match a real asset one day;
# these are the shapes actually present, each anchored at the end of the name.
BACKUP = re.compile(
    r'\.(?:bak|bak_[A-Za-z0-9_]+|bak[A-Za-z0-9]+'
    r'|pre[A-Za-z0-9_]*|damaged_by_[A-Za-z0-9_]+|stale|old)$')


def gz_redundant():
    """plain .json files whose set is declared gz AND whose .gz exists"""
    out = []
    for store in ('lookup', 'lookup_eval'):
        idx = os.path.join(ROOT, store, 'index.json')
        if not os.path.exists(idx):
            continue
        try:
            man = json.load(open(idx, encoding='utf-8'))
        except Exception:
            continue
        for s in (man.get('gz') or []):
            d = os.path.join(ROOT, store, s)
            if not os.path.isdir(d):
                continue
            for f in os.listdir(d):
                if not f.endswith('.json'):
                    continue
                if os.path.exists(os.path.join(d, f + '.gz')):
                    out.append(os.path.join(d, f))
    return out


def main():
    if not os.path.isdir(ROOT):
        print('no %s/ here' % ROOT); return 1
    backups, total = [], 0
    for r, dirs, files in os.walk(ROOT):
        for f in files:
            p = os.path.join(r, f)
            try:
                total += os.path.getsize(p)
            except OSError:
                continue
            if BACKUP.search(f):
                backups.append(p)
    gzr = gz_redundant()
    sz = lambda L: sum(os.path.getsize(p) for p in L if os.path.exists(p))
    b, g = sz(backups), sz(gzr)
    print('site/ before            %8.2f GB' % (total / 1024.0 ** 3))
    print('  backup files          %5d files  %8.0f MB' % (len(backups), b / M))
    print('  redundant plain json  %5d files  %8.0f MB  (a .gz sibling exists and the manifest declares the set gz)'
          % (len(gzr), g / M))
    print('site/ after             %8.2f GB' % ((total - b - g) / 1024.0 ** 3))
    by = collections.Counter(os.path.dirname(p) for p in backups)
    print()
    print('  backups by directory, largest first:')
    for d, n in by.most_common(6):
        print('    %-34s %4d' % (d, n))
    if not WRITE:
        print('\nDRY RUN — pass --write')
        return 0
    n = 0
    for p in backups + gzr:
        try:
            os.remove(p); n += 1
        except OSError as e:
            print('  could not remove %s (%s)' % (p, e))
    print('\nremoved %d files from the artifact copy' % n)
    return 0


sys.exit(main())
