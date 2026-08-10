#!/usr/bin/env python3
"""GATE: a random sample of headwords, drawn FROM THE SOURCES, must be keys in
the store the reader actually queries.

The discipline is `check_lookup_reach.js`'s, one layer down: a hard-coded list
stops testing the fault the day the store is rebuilt, so the sample is drawn at
run time from `_dictsrc/` — the files themselves — and every word in it is
something a reader could legitimately type after seeing it in one of these
dictionaries.

It answers the question "is every dictionary reachable by its own headword?"
with a number, per dictionary, rather than with an opinion.  100% is the
expected answer for every source the store was built with; anything the store
records in `stardict_missing` is reported as NOT BUILT rather than as 0%,
because those are different facts.

  python3 pipeline/check_hw_reach.py            # 2,000 headwords per source
  python3 pipeline/check_hw_reach.py --all      # every headword (slower)
  python3 pipeline/check_hw_reach.py --n 200

Exit 0 green, 1 if any source built into the store is not fully reachable.
"""
import json, os, re, sys, csv, gzip, glob, random, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, '_panel'))
from build_lookup import fold

HW = os.path.join(REPO, 'stores', 'lookup_eval', 'hw')
DS = os.path.join(REPO, '_dictsrc')
csv.field_size_limit(10 ** 9)
APD_DROP = set('U Q E S A J H T M D F G W Z X V'.split())


def main():
    n = 2000
    if '--n' in sys.argv:
        n = int(sys.argv[sys.argv.index('--n') + 1])
    if '--all' in sys.argv:
        n = 0
    man_p = os.path.join(HW, 'index.json')
    if not os.path.exists(man_p):
        sys.exit(f'no store at {HW} — run _panel/build_own.py first')
    man = json.load(open(man_p, encoding='utf-8'))
    absent = set(man.get('stardict_missing') or [])
    cache = {}

    def present(word):
        f = fold(word)
        for d in range(2, 41):
            name = (f[:d] + '_' * d)[:d]
            if name in man['shards']:
                if name not in cache:
                    p = os.path.join(HW, name + '.json')
                    if os.path.exists(p):
                        cache[name] = json.load(open(p, encoding='utf-8'))
                    else:
                        cache[name] = json.loads(gzip.decompress(
                            open(p + '.gz', 'rb').read()))
                return f in cache[name]
        return False

    # ---- the headwords each source actually carries -------------------------
    src = collections.defaultdict(set)
    p = os.path.join(DS, 'pced_full.jsonl.gz')
    if os.path.exists(p):
        for line in gzip.open(p, 'rt', encoding='utf-8'):
            r = json.loads(line)
            if r['d'] in APD_DROP:
                continue
            w = (r.get('acc') or r.get('hw') or '').strip()
            if w and r.get('b', '').strip():
                src['PCED ' + r['d']].add(w)
    p = os.path.join(DS, 'pm12e.csv')
    if os.path.exists(p):
        for row in csv.reader(open(p, newline='', encoding='utf-8')):
            if row and row[0].strip():
                src['Abhidhāna (pm12e)'].add(row[0].strip())
    p = os.path.join(DS, 'DPPN.json')
    if os.path.exists(p):
        nb = re.compile(r'<b>(.*?)</b>')
        for row in json.load(open(p, encoding='utf-8')):
            m = nb.search(row.get('name', ''))
            if m:
                w = re.sub(r'<[^>]+>', '', m.group(1)).strip().strip('.')
                if w:
                    src['DPPN'].add(w)

    random.seed(0)
    bad = 0
    print(f'store: {man["keys"]:,} keys · {len(man["shards"]):,} shards')
    if absent:
        print(f'NOT BUILT INTO THIS STORE (absent when it ran): {sorted(absent)}')
        print('  those dictionaries are still reachable only through DPD\'s index.')
    for name in sorted(src):
        pool = sorted(src[name])
        sample = pool if not n or n >= len(pool) else random.sample(pool, n)
        ok = sum(present(w) for w in sample)
        pct = 100.0 * ok / max(len(sample), 1)
        flag = 'ok  ' if ok == len(sample) else 'FAIL'
        print(f'  {flag} {name:22s} {len(pool):8,} headwords · '
              f'{ok:,}/{len(sample):,} of the sample reachable ({pct:.1f}%)')
        if ok != len(sample):
            bad += 1
            miss = [w for w in sample if not present(w)][:5]
            print(f'       unreachable, e.g. {miss}')
    print('all green' if not bad else f'FAILED: {bad} source(s) not fully reachable')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
