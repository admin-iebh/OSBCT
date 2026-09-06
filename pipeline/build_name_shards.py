#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit the SECTION NAMES as N-GRAM SHARDS, so a search no longer reads
`index/names.json` whole.

WRITTEN 2026-09-05 (fourth session).  `perf_search.js` gained a "largest
single file" column in the third session and the first thing it found was
this: `site/index/names.json` — 16,998 labels, 33,263 rows, 1.09 MB raw,
255 KB on the wire — fetched by BOTH search UIs before their first query and
scanned by substring on every search.  After `tg/` it was the largest file a
search read, by a factor of two; and the cold first search WAITED for it.

WHAT THIS EMITS, read from names.json (so it is built AFTER
build_name_index.py):

  site/index/tn/index.json   {cap, nlabels, nrows, mind, maxd, vols, layers,
                              grams:{name: rawBytes}}
  site/index/tn/<name>.json  {"labels":[…], "rows":[[li, volIdx, ord,
                              layerIdx, rowIdx], …]} — every label whose
                              FOLDED form contains <name> inside one run of
                              letters, with all of that label's rows.  `li`
                              indexes the shard's own `labels`; `rowIdx` is
                              the row's index in names.json, so a client that
                              merges several shards can restore the file's
                              order exactly.  Rows are in that order.

<name> is a folded n-gram over the LETTERS of a label (a–z after folding —
digits, spaces and punctuation never enter a name, so a name is always a safe
file name), length ≥ MIND, deepened — by the letter that FOLLOWS the gram, `_`
when the gram ends its run of letters — until the shard fits under CAP.  This
is `build_gram_shards.py`'s idiom, unchanged, applied to labels instead of
keys: `sut` may not exist, but `sutt`, `suta`, …, `sut_` do, and their union
is exactly the labels containing `sut`.

HOW THE CLIENT USES IT (site/searchcore.js, `names`): the query is folded,
every substring of length MIND–MAXD of each of its letter runs is a candidate
gram, each resolves to a shard — the name itself, its children, or the
shallowest name prefixing it — with a byte total from the manifest, and the
cheapest wins.  The page then matches every candidate label by SUBSTRING in
the mode's view (exact or folded), ranks and draws, exactly as it did over
the whole file: the gram narrows the candidates, it never decides a match.
A query with no letter run of MIND letters falls back to names.json, which
stays — for that, and for an archive that predates this directory.

A `_`-terminal shard cannot be deepened and may exceed CAP (`na_`: the
labels whose last letters are -na, 353 KB); it is read only when the query
offers nothing cheaper.

Verifies itself: every shard holds exactly the labels containing its name
(in folded view, within a letter run), each with all its rows, in names.json
order; for every gram of every 7th label the client's resolution lands on
shards whose union holds the label; the manifest sizes are the file sizes.

Usage:  python3 pipeline/build_name_shards.py [--cap BYTES]
"""
import json, os, sys, re, collections, unicodedata, bisect

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'site', 'index')
TN = os.path.join(IDX, 'tn')
CAP = 200_000      # raw bytes per shard (about 40 KB gzipped)
MIND, MAXD = 2, 8

_MAP = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṇ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ḷ': 'l'}
RUN = re.compile(r'[a-z]+')


def fold(s):
    return ''.join(_MAP.get(c, c) for c in unicodedata.normalize('NFC', s).lower())


def shard_json(labels, rows_by, members):
    """members: sorted label indices.  Rows in names.json order."""
    ls = [labels[i] for i in members]
    loc = {i: j for j, i in enumerate(members)}
    rows = sorted((r[4], r) for i in members for r in rows_by[i])
    return json.dumps({'labels': ls, 'rows': [[loc[r[0]], r[1], r[2], r[3], r[4]] for _, r in rows]},
                      ensure_ascii=False, separators=(',', ':'))


def main():
    global CAP
    if '--cap' in sys.argv: CAP = int(sys.argv[sys.argv.index('--cap') + 1])
    D = json.load(open(os.path.join(IDX, 'names.json'), encoding='utf-8'))
    labels, R = D['labels'], D['rows']
    if len(set(labels)) != len(labels):
        print('REFUSING: names.json labels are not unique'); sys.exit(1)
    rows_by = collections.defaultdict(list)
    for gi, (li, vi, o, ly) in enumerate(R):
        rows_by[li].append((li, vi, o, ly, gi))
    fk = [fold(l) for l in labels]
    # the bytes a label costs in a shard: its label, quoted, plus its rows
    lb = [len(json.dumps(labels[i], ensure_ascii=False).encode('utf-8')) + 1
          + sum(len(json.dumps(list(r[1:]), separators=(',', ':'))) + 4 for r in rows_by[i])
          for i in range(len(labels))]
    print('%d labels, %d rows from names.json' % (len(labels), len(R)))

    # ---- group by bigram over letter runs, deepen while over CAP -----------
    groups = collections.defaultdict(set)
    for i, f in enumerate(fk):
        for m in RUN.finditer(f):
            s = m.group()
            for j in range(len(s) - MIND + 1):
                groups[s[j:j + MIND]].add(i)
    final = {}
    queue = sorted(groups.items())
    n_over = 0
    while queue:
        name, ks = queue.pop()
        d = len(name)
        total = sum(lb[i] for i in ks)
        if total <= CAP or name.endswith('_') or d >= MAXD:
            final[name] = ks
            if total > CAP: n_over += 1
            continue
        sub = collections.defaultdict(set)
        for i in ks:
            for m in RUN.finditer(fk[i]):
                s = m.group(); j = s.find(name)
                while j >= 0:
                    sub[(s[j:j + d + 1] + '_')[:d + 1]].add(i)
                    j = s.find(name, j + 1)
        queue.extend(sorted(sub.items()))
    names = set(final)

    os.makedirs(TN, exist_ok=True)
    sizes = {}
    for name, ks in final.items():
        body = shard_json(labels, rows_by, sorted(ks))
        p = os.path.join(TN, name + '.json')
        open(p, 'w', encoding='utf-8').write(body)
        sizes[name] = os.path.getsize(p)
    for f in os.listdir(TN):
        if f.endswith('.json') and f != 'index.json' and f[:-5] not in names:
            try: os.remove(os.path.join(TN, f)); print('removed stale shard:', f)
            except OSError:
                open(os.path.join(TN, f), 'w').write(''); print('emptied stale shard:', f)
    manifest = {'cap': CAP, 'nlabels': len(labels), 'nrows': len(R), 'mind': MIND, 'maxd': MAXD,
                'vols': D['vols'], 'layers': D['layers'],
                'grams': {n: sizes[n] for n in sorted(names)}}
    json.dump(manifest, open(os.path.join(TN, 'index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))

    # ---- self-verification -----------------------------------------------
    # 1. each shard = exactly the labels whose folded letter runs contain its
    #    bare name (a `_` name: a run that ENDS with the gram), computed
    #    label-by-label from the label's own substrings, not from `groups`;
    #    every row of each, in names.json order
    want = collections.defaultdict(list)
    for i, f in enumerate(fk):
        seen = set()
        for m in RUN.finditer(f):
            s = m.group()
            for L in range(MIND, min(MAXD, len(s)) + 1):
                for j in range(len(s) - L + 1):
                    g = s[j:j + L]
                    if g in names: seen.add(g)
                    if j + L == len(s) and L < MAXD and g + '_' in names: seen.add(g + '_')
        for g in seen: want[g].append(i)
    for name in names:
        got = json.load(open(os.path.join(TN, name + '.json'), encoding='utf-8'))
        w = want.get(name, [])
        if got['labels'] != [labels[i] for i in w]:
            print('FAIL: shard %s holds %d labels, expected %d' % (name, len(got['labels']), len(w))); sys.exit(1)
        wrows = sorted(r[4] for i in w for r in rows_by[i])
        if [r[4] for r in got['rows']] != wrows:
            print('FAIL: shard %s rows differ' % name); sys.exit(1)
        for r in got['rows']:
            li, vi, o, ly, gi = r
            if labels[R[gi][0]] != got['labels'][li] or R[gi][1:] != [vi, o, ly]:
                print('FAIL: shard %s row %d is not names.json row %d' % (name, li, gi)); sys.exit(1)
    # 2. the client's resolution, re-implemented: shard g if it exists, else
    #    every name extending g, else the shallowest name prefixing g.  For
    #    every 7th label and every gram of it, the union must hold the label.
    snames = sorted(names)
    def resolve(g):
        if g in names: return [g]
        lo = bisect.bisect_left(snames, g); hi = bisect.bisect_left(snames, g + '~')
        kids = snames[lo:hi]
        if kids: return kids
        for d in range(MIND, len(g) + 1):
            if g[:d] in names: return [g[:d]]
        return []
    members = {n: set(json.load(open(os.path.join(TN, n + '.json'), encoding='utf-8'))['labels']) for n in names}
    checked = 0
    for i in range(0, len(labels), 7):
        for m in RUN.finditer(fk[i]):
            s = m.group()
            for L in range(MIND, min(MAXD, len(s)) + 1):
                for j in range(len(s) - L + 1):
                    g = s[j:j + L]; r = resolve(g)
                    if not r or not any(labels[i] in members[n] for n in r):
                        print('FAIL: label %r gram %r resolves to %r which lacks it' % (labels[i], g, r)); sys.exit(1)
                    checked += 1
    # 3. manifest sizes are file sizes
    for n in names:
        if manifest['grams'][n] != os.path.getsize(os.path.join(TN, n + '.json')):
            print('FAIL: manifest size differs for', n); sys.exit(1)
    total = sum(sizes.values())
    big = sorted(((s, n) for n, s in sizes.items()), reverse=True)
    print('name shards: %d files, %.1f MB total, %d over CAP=%d (all `_`-terminal); manifest %d bytes'
          % (len(names), total / 1e6, n_over, CAP, os.path.getsize(os.path.join(TN, 'index.json'))))
    print('largest:', ', '.join('%s %.0f KB' % (n, s / 1e3) for s, n in big[:6]))
    print('depth histogram:', dict(sorted(collections.Counter(len(n) for n in names).items())))
    print('every shard == labels containing its gram, with their rows, in file order: EXACT; '
          '%d (label, gram) resolutions land: EXACT' % checked)


if __name__ == '__main__':
    main()
