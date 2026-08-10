#!/usr/bin/env python3
"""MEASURE, BEFORE BUILDING, what keying the APD and the Abhidhāna on their OWN
headwords costs — key count, shard count, largest shard against the 150 kB cap,
and how many keys have to go to their own overflow file.

Written for `claude/dpd_gates_the_abhidhana.md` §5 ("Size it first"), which is
the third constraint of the 2026-08-10 task: the key set roughly quadruples,
52,757 → 210,000+, and shard counts, byte caps and the R2 sync all need
measuring BEFORE anything is written.  Nothing here writes a store.

Reads `_dictsrc/pced_full.jsonl.gz` (Zawgyi already converted) and
`_dictsrc/pm12e.csv`.  Both are gitignored and exist nowhere else.

  python3 _panel/measure_own.py            # full measure
  python3 _panel/measure_own.py --quick    # counts only, no shard simulation
"""
import json, os, re, sys, csv, gzip, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
from build_lookup import fold, shard_table, CAP

PCED_JSONL = os.path.join(REPO, '_dictsrc', 'pced_full.jsonl.gz')
PM12E = os.path.join(REPO, '_dictsrc', 'pm12e.csv')
csv.field_size_limit(10 ** 9)

# THE SAME EXCLUSIONS THE lem BUILD MAKES, COPIED DELIBERATELY RATHER THAN
# IMPORTED.  `build_eval.py` computes APD_DROP at module scope, below a DPD
# index read that needs GoldenDict, so importing it here would need the whole
# 889 MB DPD build present just to count headwords.  The list is asserted
# against the store manifest in build_own.py, so the two cannot drift silently.
APD_DROP = set('U Q E S A J H T M D F G W Z X V'.split())


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def pced_rows():
    with gzip.open(PCED_JSONL, 'rt', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            if r['d'] in APD_DROP:
                continue
            yield r


def main():
    quick = '--quick' in sys.argv
    log('PCED…')
    # key -> {dict_id: [bodies]}; and the accented spellings that produced it
    keys = collections.defaultdict(lambda: collections.defaultdict(list))
    spell = collections.defaultdict(set)
    per_book = collections.Counter()
    raw_hw = collections.defaultdict(set)      # book -> distinct raw headwords
    n = 0
    for r in pced_rows():
        body = re.sub(r'\s+', ' ', r['b']).strip()
        if not body:
            continue
        acc = (r.get('acc') or r['hw'] or '').strip()
        if not acc:
            continue
        raw_hw[r['d']].add(acc.lower())
        k = fold(acc)
        bucket = keys[k][r['d']]
        if body not in bucket:
            bucket.append(body)
        spell[k].add(acc.lower())
        per_book[r['d']] += 1
        n += 1
        if n % 200000 == 0:
            log(f'  {n:,} rows · {len(keys):,} keys')
    log(f'  {n:,} rows kept · {len(keys):,} folded keys · '
        f'{len(per_book)} dictionaries')

    log('Abhidhāna (pm12e.csv)…')
    abhi_keys = set()
    na = 0
    with open(PM12E, newline='', encoding='utf-8') as f:
        for row in csv.reader(f):
            if not row or not row[0].strip():
                continue
            hw = row[0].strip()
            k = fold(hw)
            abhi_keys.add(k)
            spell[k].add(hw.lower())
            keys[k]['_a'].append([x.strip() for x in row[1:5]])
            na += 1
    log(f'  {na:,} rows · {len(abhi_keys):,} folded keys')

    log('')
    log(f'TOTAL distinct folded keys: {len(keys):,}')
    log(f'  from the Abhidhāna only : '
        f'{len(abhi_keys - set(k for k in keys if any(d != "_a" for d in keys[k]))):,}')
    for b in sorted(per_book, key=lambda b: -per_book[b]):
        log(f'    {b}: {per_book[b]:9,} rows · {len(raw_hw[b]):8,} distinct headwords')

    if quick:
        return

    log('')
    log('sizing the values…')
    ent = lambda k, v: (len(k.encode()) + 3
                        + len(json.dumps(v, ensure_ascii=False).encode()) + 1)
    sizes, total = {}, 0
    for k, m in keys.items():
        v = {'w': sorted(spell[k])}
        apd = {d: b for d, b in m.items() if d != '_a'}
        if apd:
            v['apd'] = apd
        if '_a' in m:
            v['a'] = m['_a']
        s = ent(k, v)
        sizes[k] = s
        total += s
    log(f'  {total/1e6:.1f} MB of JSON in {len(sizes):,} keys · '
        f'mean {total/len(sizes):.0f} B · max {max(sizes.values())/1000:.0f} kB')
    over = sorted((b for b in sizes.values() if b > CAP), reverse=True)
    log(f'  keys larger than the {CAP/1000:.0f} kB cap ON THEIR OWN: {len(over)}'
        + (f' (largest {over[0]/1000:.0f} kB)' if over else ''))
    third = [b for b in sizes.values() if b > CAP // 3]
    log(f'  keys over CAP//3 (build_lookup\'s overflow threshold): {len(third):,}')

    log('')
    log('simulating the shard table (this is the expensive part)…')
    assign, manifest = shard_table(sizes)
    big = max(m['bytes'] for m in manifest.values())
    log(f'  {len(manifest):,} shards · largest {big/1000:.0f} kB · '
        f'mean {sum(m["bytes"] for m in manifest.values())/len(manifest)/1000:.1f} kB')
    log(f'  shards over the cap (must go to overflow files): '
        f'{sum(1 for m in manifest.values() if m["bytes"] > CAP)}')
    depths = collections.Counter(len(g) for g in manifest)
    log('  shard-name depth: ' + ' · '.join(f'{d}:{c}' for d, c in sorted(depths.items())))
    log('')
    log(f'  R2 object count added: ~{len(manifest):,} shard files '
        f'(+ overflow), against 17,280 tracked today.')


if __name__ == '__main__':
    main()
