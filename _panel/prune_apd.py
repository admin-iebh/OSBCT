#!/usr/bin/env python3
"""Remove the dictionaries named in build_eval.APD_DROP from a store already built.

WHY THIS EXISTS RATHER THAN JUST REBUILDING.  `build_eval.py` is the
authoritative change -- APD_DROP is there, so no future rebuild can bring these
back.  But a full rebuild needs `GD_DIR` (DPD, the Abhidhāna, PEU, CPED, DPPN
and the four Burmese sets all come from ~/GoldenDict), and running it without
that would quietly produce a store missing eighteen dictionaries -- the same
shape of accident as overwriting with `pced_subset`.  This does the same job to
the store in hand, using nothing but the store.

It rewrites the `lem` shards and the manifest.  It does NOT touch `form`, `dpd`
or anything else.

    python3 _panel/prune_apd.py            # report only, changes nothing
    python3 _panel/prune_apd.py --apply
"""
import json, os, sys, collections, gzip

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
STORE = os.path.join(REPO, 'site', 'lookup_eval')
sys.path.insert(0, ROOT)

# import APD_DROP WITHOUT running the build: build_eval.py reads GoldenDict at
# import time, so it cannot simply be imported here.  Parse the literal out of
# the source instead -- one definition, one place, no second copy to drift.
import ast, re


def load_drop():
    src = open(os.path.join(ROOT, 'build_eval.py'), encoding='utf-8').read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'APD_DROP':
            return ast.literal_eval(node.value)
    sys.exit('APD_DROP not found in build_eval.py — nothing to prune by')


DROP = load_drop()
APPLY = '--apply' in sys.argv


def shard_paths():
    d = os.path.join(STORE, 'lem')
    out = []
    for dirpath, _, names in os.walk(d):
        out += [os.path.join(dirpath, n) for n in names
                if n.endswith('.json') or n.endswith('.json.gz')]
    return sorted(out)


def read(p):
    if p.endswith('.gz'):
        return json.loads(gzip.decompress(open(p, 'rb').read()))
    return json.load(open(p, encoding='utf-8'))


def write(p, o):
    b = json.dumps(o, ensure_ascii=False).encode('utf-8')
    if p.endswith('.gz'):
        open(p, 'wb').write(gzip.compress(b, 9, mtime=0))
    else:
        open(p, 'wb').write(b)


def main():
    man_path = os.path.join(STORE, 'index.json')
    man = json.load(open(man_path, encoding='utf-8'))
    books = man.get('apd_books') or {}
    done = man.get('apd_dropped') or {}
    # !!! THIS GUARD USED TO MAKE THE SCRIPT RUN ONCE AND NEVER AGAIN.  It
    # compared APD_DROP against `apd_books` alone, so the moment a run
    # succeeded, every id it had just removed was "an id this store does not
    # have" and the next run refused.  Adding one dictionary to APD_DROP a day
    # later was therefore impossible without editing this file -- discovered
    # 2026-08-03 doing exactly that.
    # An id absent from `apd_books` but recorded in `apd_dropped` is ALREADY
    # PRUNED, which is agreement, not disagreement.  Only an id in neither is
    # the renumbering this guard was written for.
    unknown = [k for k in DROP if k not in books and k not in done]
    if unknown:
        sys.exit(f'APD_DROP names ids this store has never had: {unknown}\n'
                 f'Refusing to run: the store and the drop list disagree.')
    todo = [k for k in DROP if k in books]
    if not todo:
        print('nothing to prune: every id in APD_DROP is already recorded in '
              'apd_dropped')
        return

    rows_before = collections.Counter()
    rows_after = collections.Counter()
    lem_with, lem_emptied, n_shards = 0, 0, 0
    odd = collections.Counter()
    paths = shard_paths()
    print(f'{len(paths):,} lem shards')

    for p in paths:
        o = read(p)
        touched = False
        for lem, rec in o.items():
            # a shard is not uniformly lemma->record: some keys carry scalars
            # (paging markers and the like).  Skip anything that is not a record
            # rather than assume, or the run dies on the first one.
            if not isinstance(rec, dict):
                odd[type(rec).__name__] += 1
                continue
            apd = rec.get('apd')
            if not isinstance(apd, dict) or not apd:
                continue
            for did, bodies in list(apd.items()):
                rows_before[did] += len(bodies)
                if did in DROP:
                    del apd[did]
                    touched = True
                else:
                    rows_after[did] += len(bodies)
            if touched:
                lem_with += 1
                if not apd:
                    del rec['apd']
                    lem_emptied += 1
        if touched:
            n_shards += 1
            if APPLY:
                write(p, o)

    kept = sorted(rows_after, key=lambda k: -rows_after[k])
    dropped = sorted((k for k in rows_before if k in DROP),
                     key=lambda k: -rows_before[k])
    print(f'\nREMOVED — {len(dropped)} dictionaries, '
          f'{sum(rows_before[k] for k in dropped):,} rows')
    for k in dropped:
        print(f'  {k:4s} {rows_before[k]:9,}  {DROP[k]}')
    print(f'\nKEPT — {len(kept)} dictionaries, {sum(rows_after.values()):,} rows')
    for k in kept:
        print(f'  {k:4s} {rows_after[k]:9,}  {books.get(k, {}).get("name", "?")}')
    if odd:
        print(f'  non-record values skipped: {dict(odd)}')
    print(f'\n{n_shards:,} shards affected · {lem_with:,} lemmas lost at least one '
          f'dictionary · {lem_emptied:,} lost their APD block entirely')

    # every kept dictionary must be untouched -- this is the assertion that the
    # prune took out what it meant to and nothing beside it
    for k in kept:
        assert rows_after[k] == rows_before[k], \
            f'{k} changed: {rows_before[k]} -> {rows_after[k]}'
    print('verified: every kept dictionary has exactly its original row count')

    if APPLY:
        man['apd_books'] = {k: v for k, v in books.items() if k not in DROP}
        man['apd_order'] = [k for k in (man.get('apd_order') or []) if k not in DROP]
        man['apd_zawgyi'] = [k for k in (man.get('apd_zawgyi') or []) if k not in DROP]
        man['apd_dropped'] = {k: DROP[k] for k in sorted(DROP)}
        json.dump(man, open(man_path, 'w'), ensure_ascii=False)
        print(f'\nmanifest: apd_order now {man["apd_order"]}')
        print('WRITTEN.  Bump WLV in panel.js and ?v= in reader2.html.')
    else:
        print('\n(report only — pass --apply to write)')


if __name__ == '__main__':
    main()
