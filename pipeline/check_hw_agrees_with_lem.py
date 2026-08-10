#!/usr/bin/env python3
"""GATE: the own-headword store agrees with the store built beside it.

`_panel/build_own.py` re-reads `_dictsrc/pced_full.jsonl.gz` and
`_dictsrc/pm12e.csv` with its OWN copy of the Abhidhāna citation transcoding
(`_panel/abhidhana_cites.py`), because importing `build_eval.py` would drag in a
DPD index read and make the fix depend on the very dictionary it is undoing.  A
copy that drifts is worse than either, so this is the mechanism that holds the
two together: for every key the two stores share, what `hw` says must contain
what `lem` already said.

WHAT IT ASSERTS, AND WHY IT IS A CONTAINMENT AND NOT AN EQUALITY.
`build_eval.py` keys the Abhidhāna on `row[0].lower()` and the APD on
`fold(hw|acc|cap)`; `build_own.py` keys both on `fold(headword)`.  fold()
collapses diacritics as well as case, so one `hw` key can legitimately gather
rows from several `lem` keys.  Extra rows are therefore expected and are
COUNTED; a MISSING row is a defect and fails.

  python3 pipeline/check_hw_agrees_with_lem.py
  python3 pipeline/check_hw_agrees_with_lem.py --sample 2000   # faster

Exit 0 green, 1 on any missing row.
"""
import json, os, sys, gzip, glob, random, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, '_panel'))
from build_lookup import fold

# the three APD sections that come from GoldenDict StarDict files rather than
# from `_dictsrc/`, and which `build_own.py` therefore does not carry
STARDICT_ONLY = {'DOP', 'CPD', 'NCP'}

EVAL = os.path.join(REPO, 'stores', 'lookup_eval')
LEM = os.path.join(EVAL, 'lem')
HW = os.path.join(EVAL, 'hw')


def readshard(p):
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    if os.path.exists(p + '.gz'):
        return json.loads(gzip.decompress(open(p + '.gz', 'rb').read()))
    return None


def hw_index():
    man = readshard(os.path.join(HW, 'index.json'))
    if not man:
        sys.exit(f'no manifest at {HW}/index.json — run _panel/build_own.py first')
    return man


def hw_get(man, cache, key):
    f = fold(key)
    for d in range(2, 41):
        name = (f[:d] + '_' * d)[:d]
        if name in man['shards']:
            if name not in cache:
                cache[name] = readshard(os.path.join(HW, name + '.json')) or {}
            return cache[name].get(f)
    return None


def lem_value(key, v):
    """A lem shard value may be an overflow marker; the rows are then paged by
    key under lem/big/.  Reassemble, exactly as panel.js elook() does."""
    if not (isinstance(v, dict) and v.get('big') and v.get('pages')):
        return v
    safe = ''.join(c if (c.isalnum() and c.isascii()) else '-%d-' % ord(c)
                   for c in fold(key))
    out = {}
    for i in range(v['pages']):
        pg = readshard(os.path.join(LEM, 'big', f'{safe}.{i}.json'))
        if pg and isinstance(pg.get('rows'), dict):
            out.update(pg['rows'])
    return out


def main():
    n_sample = 0
    if '--sample' in sys.argv:
        n_sample = int(sys.argv[sys.argv.index('--sample') + 1])
    man = hw_index()
    cache = {}
    # !!! WHAT MAY BE DEMANDED OF `hw` IS WHAT `hw` WAS BUILT WITH, AND THE
    # STORE SAYS SO ITSELF.  `build_own.py` records in its manifest which
    # sources were absent when it ran (`stardict_missing`) — PEU, DOP, CPD and
    # NCPED live in a GoldenDict build that is not on every machine.  Reading
    # that instead of hard-coding a list means this gate tightens by itself the
    # moment the store is rebuilt somewhere they exist, rather than going on
    # excusing an absence nobody rechecks.
    absent = set(man.get('stardict_missing') or [])
    if absent:
        print(f'NOTE: the store records these as absent when it was built: '
              f'{sorted(absent)} — not demanded of it here.')
    shards = sorted(glob.glob(os.path.join(LEM, '*.json')))
    if not shards:
        shards = sorted(glob.glob(os.path.join(LEM, '*.json.gz')))
        shards = [s[:-3] for s in shards]
    if n_sample:
        random.seed(0)
        shards = random.sample(shards, min(n_sample, len(shards)))

    seen = miss_key = 0
    a_checked = a_missing = a_extra = 0
    apd_checked = apd_missing = apd_extra = 0
    pn_checked = pn_missing = 0
    missing_examples = []
    per_book_missing = collections.Counter()

    for sp in shards:
        o = readshard(sp) or {}
        for key, v in o.items():
            v = lem_value(key, v)
            if not isinstance(v, dict):
                continue
            # !!! ONLY WHAT build_own.py READS MAY BE DEMANDED OF IT.  The first
            # run of this gate reported 1,574 keys "absent from hw" and it was
            # the CHECK that was wrong: every one of them carries DOP, CPD or
            # NCPED alone.  Those three are StarDict files under GoldenDict,
            # injected into the APD map by `build_eval.py`; they are not in
            # `_dictsrc/` and `build_own.py` does not read them, by the
            # constraint that this store is built from the two files that are.
            #
            # RECORDED, NOT FIXED: those three dictionaries are therefore still
            # reachable ONLY through `lem`, which is to say only through DPD's
            # index — the same defect as the one being repaired here, in a
            # corner it does not reach.  Whoever widens this: they need the
            # GoldenDict build present, which is why it was not done blind.
            payload = bool(v.get('a')) or bool(v.get('pn')) or any(
                d not in absent for d in (v.get('apd') or {}))
            if not payload:
                continue
            seen += 1
            h = hw_get(man, cache, key)
            if h is None:
                miss_key += 1
                if len(missing_examples) < 10:
                    missing_examples.append(('key absent', key, ''))
                continue
            if v.get('a'):
                a_checked += 1
                hs = [json.dumps(r, ensure_ascii=False, sort_keys=True)
                      for r in (h.get('a') or [])]
                ls = [json.dumps(r, ensure_ascii=False, sort_keys=True)
                      for r in v['a']]
                lost = [r for r in ls if r not in hs]
                if lost:
                    a_missing += 1
                    if len(missing_examples) < 10:
                        missing_examples.append(('abhidhāna row', key, lost[0][:90]))
                a_extra += max(0, len(hs) - len(ls))
            if v.get('pn'):
                pn_checked += 1
                hs = h.get('pn') or []
                lost = [r for r in v['pn'] if r not in hs]
                if lost:
                    pn_missing += 1
                    if len(missing_examples) < 10:
                        missing_examples.append(('ppn', key, lost[0][:90]))
            if v.get('apd'):
                apd_checked += 1
                hm = h.get('apd') or {}
                for did, bodies in v['apd'].items():
                    if did in absent:
                        continue          # not present when the store was built
                    hb = hm.get(did) or []
                    lost = [b for b in bodies if b not in hb]
                    if lost:
                        apd_missing += 1
                        per_book_missing[did] += len(lost)
                        if len(missing_examples) < 10:
                            missing_examples.append(('apd ' + did, key, lost[0][:90]))
                    apd_extra += max(0, len(hb) - len(bodies))

    print(f'lem entries with a dictionary payload : {seen:,}')
    print(f'  key absent from hw                  : {miss_key:,}')
    print(f'  Abhidhāna: {a_checked:,} checked · {a_missing:,} with a MISSING row '
          f'· {a_extra:,} extra rows (fold() gathers more, as designed)')
    print(f'  PPN      : {pn_checked:,} checked · {pn_missing:,} with a MISSING name')
    print(f'  APD      : {apd_checked:,} checked · {apd_missing:,} with a MISSING '
          f'body · {apd_extra:,} extra bodies')
    if per_book_missing:
        print('  missing by book: '
              + ' · '.join(f'{k}={v}' for k, v in per_book_missing.most_common()))
    for kind, key, detail in missing_examples:
        print(f'    {kind:16s} {key!r}  {detail}')
    bad = miss_key + a_missing + apd_missing + pn_missing
    print('all green' if not bad else f'FAILED: {bad} entr(ies) lose content')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
