#!/usr/bin/env python3
"""Build the SHIPPED word-lookup data for reader2 — licence-clean sources only.

WHAT SHIPS, AND WHY ONLY THIS
  Edition   the edition's own glosses (_gloss/by_volume/, roadmap step 3).  The
            panel's voice, per §9: the aṭṭhakathā and ṭīkā explaining the word.
  counts    corpus occurrence counts (_vocab/freq/).  Measurement, not text.
  PED       The PTS Pali-English Dictionary, Rhys Davids & Stede 1921-25 —
            PUBLIC DOMAIN.  Taken from the PCED dataset (github.com/siongui/data,
            dictionary id "P", 16,158 entries).

WHAT DOES NOT SHIP, AND WHY
  DPD       CC BY-NC-SA, and §9 settles the question before licensing does: the
            panel does not speak in a modern dictionary's voice.  DPD is used
            HERE, at build time, for one thing only — its synonym index, which
            maps an inflected form to its headword.  `dpd.dict.dz` is never
            opened; only `dpd.idx` (headword strings) and `dpd.syn.dz` (the
            form -> headword-offset index).  No DPD text can leak because no
            DPD text is read.
  Abhidhāna, PEU, PPN
            held back pending the confirmations recorded in
            claude/panel_prototype_built.md — Ven. Subhuti / the pm12e
            maintainers, the Ministry question of §8, and PPN's licence.  The
            prototype's code paths for them exist; this is a data decision.
  CPED, DOP, CPD
            filter-side only per §9 / the inventory.

PROXIMITY.  Measured 2026-08-02 (proximity.py, proximity_precision2.py): a
proximity row exists for 6.5% of glossed clicks, and when it exists its phrase
is really in the canon paragraph 57% of the time corpus-wide (Dīgha 84%,
Khuddaka 80%, Majjhima 79%, Vinaya 63%, Aṅguttara 61%, Saṁyutta 39%,
Abhidhamma 36%).  So proximity is NOT the panel's ranking: the Edition tab
leads with occurrences.  A proximity row is promoted only when it passes the
same check that measurement used — the row's bold lemma is actually a phrase of
the paragraph on screen — which the reader's browser can run at click time for
nothing.  That test is what `lemma_stems` in each row is for.

OUTPUT  stores/lookup/{gloss,freq,ped,forms}/<shard>.json + index.json
Sharding follows _vocab/freq/: adaptive prefix, split until no shard exceeds
the byte cap.
"""
import json, os, re, sys, glob, gzip, struct, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(REPO, 'stores', 'lookup')
DPD_DIR = os.environ.get('DPD_DIR', '/mnt/user-data/uploads/GoldenDict/dpd')
PCED_DIR = os.environ.get('PCED_DIR', os.path.join(REPO, '..', 'src/pced/dictionary'))
CAP = 150_000            # bytes; _vocab/freq/'s own ceiling

FOLD = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ḷ': 'l'}
fold = lambda s: ''.join(FOLD.get(c, c) for c in s.lower())
VOWELS = set('aiueo')
PALI = set('aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁ')
PALI |= set(c.upper() for c in PALI)
APOS = {'’', "'"}


def stem(w):
    """Same normalisation the proximity check uses (see proximity_precision.py):
    fold, collapse gemination, drop a trailing nasal, drop a trailing vowel."""
    f = re.sub(r'(.)\1+', r'\1', fold(w))
    while f and (f[-1] in 'mn' or f[-1] in VOWELS):
        f = f[:-1]
    return f


def words(text):
    ok = PALI | {'-'} | APOS
    buf, prev, out = [], '', []
    for i, ch in enumerate(text):
        if ch in ok:
            if ch in APOS or ch == '-':
                nxt = text[i + 1] if i + 1 < len(text) else ''
                if not (prev in PALI and nxt in PALI):
                    if buf:
                        out.append(''.join(buf))
                    buf, prev = [], ch
                    continue
            buf.append(ch)
        elif buf:
            out.append(''.join(buf)); buf = []
        prev = ch
    if buf:
        out.append(''.join(buf))
    return out


# ---------------------------------------------------------------- sharding --
def shard_table(keys_bytes):
    """Adaptive prefix sharding, as _vocab/freq/ does it: start at depth 2 and
    split any bucket over the cap one character deeper.

    !!! The first version capped the depth at 8 and produced a 282 kB freq
    shard and a 1.2 MB gloss shard -- both over the roadmap's 150 kB ceiling,
    because a great many Pāḷi forms share a prefix far longer than 8 (every
    `abhisambujjh-`).  There is no reason to cap the depth: it splits until the
    bucket fits or holds ONE key, and a single key that is still too large is
    handled separately (see write_shards)."""
    def bucket(k, d):
        return (fold(k)[:d] + '_' * d)[:d]

    assign, work = {}, [(2, list(keys_bytes.items()))]
    manifest = {}
    while work:
        depth, items = work.pop()
        groups = collections.defaultdict(list)
        for k, b in items:
            groups[bucket(k, depth)].append((k, b))
        if len(groups) == 1 and depth > 40:          # pathological guard
            g, gi = next(iter(groups.items()))
            for k, _ in gi:
                assign[k] = g
            manifest[g] = {'keys': len(gi), 'bytes': sum(b for _, b in gi)}
            continue
        for g, gi in groups.items():
            total = sum(b for _, b in gi) + 2 * len(gi)
            if total > CAP and len(gi) > 1:
                work.append((depth + 1, gi))
            else:
                for k, _ in gi:
                    assign[k] = g
                manifest[g] = {'keys': len(gi), 'bytes': total}
    return assign, manifest


def safe(k):
    """A filesystem-safe name for a one-key overflow file, and one the browser
    can compute: fold(), then anything outside [a-z0-9] as its code point."""
    return ''.join(c if c.isalnum() and c.isascii() else '-%d-' % ord(c)
                   for c in fold(k))


def write_shards(name, data, allow_big=False):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, '*.json')) + glob.glob(os.path.join(d, 'big', '*.json')):
        os.remove(f)
    # !!! size the ENTRY, not the value.  The first version counted only
    # json.dumps(value) plus two bytes and so under-measured every shard by the
    # length of its keys -- which is most of a freq shard.  That is how a 150 kB
    # cap produced a 282 kB file.
    entry = lambda k, v: (len(k.encode()) + 3
                          + len(json.dumps(v, ensure_ascii=False).encode()) + 1)
    sizes = {k: entry(k, v) for k, v in data.items()}

    # a single key over the cap cannot be sharded away: `tattha` alone carries
    # 718 gloss rows.  Those go to their own file, fetched only when the reader
    # actually opens that word -- the shard keeps the count so the tab can say
    # how many there are without loading them.
    # !!! A FIXED THRESHOLD DOES NOT KEEP THE CAP.  With `> CAP//2` the eval
    # build produced a 227 kB `lem` shard: a bucket whose keys are individually
    # under the threshold but which cannot be split any further, because they
    # share a fold() prefix all the way down.  Prefix sharding alone cannot fix
    # that -- the only lever left is to send keys to their own files.  So the
    # threshold starts low and the buckets are RE-CHECKED afterwards: any
    # bucket still over the cap gives up its largest key, and it repeats until
    # every shard fits.  The cap is a promise about what a phone downloads; it
    # is not decoration.
    bigkeys = {k for k, b in sizes.items() if allow_big and b > CAP // 3}
    if allow_big:
        for _ in range(200):
            probe = {k: (entry(k, {'big': 1, 'pages': 1}) if k in bigkeys
                         else sizes[k]) for k in data}
            assign_p, _m = shard_table(probe)
            over = collections.defaultdict(list)
            for k in data:
                over[assign_p[k]].append(k)
            worst = None
            for g, ks in over.items():
                tot = sum(probe[k] for k in ks)
                if tot > CAP:
                    cand = max((k for k in ks if k not in bigkeys),
                               key=lambda k: sizes[k], default=None)
                    if cand is not None:
                        worst = cand if worst is None or sizes[cand] > sizes[worst] \
                                else worst
            if worst is None:
                break
            bigkeys.add(worst)
    PAGE = 120
    if bigkeys:
        os.makedirs(os.path.join(d, 'big'), exist_ok=True)
        for k in bigkeys:
            rows = data[k]
            # !!! NOT EVERY OVERSIZE VALUE IS A LIST OF GLOSS ROWS.  build_eval
            # reuses this sharder for DPD entries (one HTML string) and lemma
            # records (a dict of sources); `rows[0]` on either is a KeyError,
            # which is how the first eval build died.  Only a list of gloss rows
            # can be ordered and paged; anything else goes in one page whole.
            if not isinstance(rows, list):
                # a dict value (a lemma record) is split by KEY across pages so
                # no single overflow file breaks the cap either; page 0 carries
                # the key list so the panel knows what is coming.
                if isinstance(rows, dict):
                    ks = sorted(rows)
                    pages, cur, cursz = [], {}, 0
                    for kk in ks:
                        sz = len(json.dumps(rows[kk], ensure_ascii=False).encode())
                        if cur and cursz + sz > CAP:
                            pages.append(cur); cur, cursz = {}, 0
                        cur[kk] = rows[kk]; cursz += sz
                    if cur:
                        pages.append(cur)
                    for i, pg in enumerate(pages or [{}]):
                        json.dump({'n': len(ks), 'pages': max(len(pages), 1),
                                   'page': i, 'keys': ks, 'rows': pg},
                                  open(os.path.join(d, 'big', f'{safe(k)}.{i}.json'), 'w'),
                                  ensure_ascii=False, separators=(',', ':'))
                    continue
                json.dump({'n': 1, 'pages': 1, 'page': 0, 'rows': rows},
                          open(os.path.join(d, 'big', f'{safe(k)}.0.json'), 'w'),
                          ensure_ascii=False, separators=(',', ':'))
                continue
            # order is the EDITION's own -- volume, then paragraph.  Not a
            # ranking (roadmap §4 forbids ranking by guess); just the order the
            # books stand in, stated so the reader knows what they are seeing.
            if rows and isinstance(rows[0], dict) and 'v' in rows[0]:
                rows = sorted(rows, key=lambda r: (r['v'], r['n'] if r['n'] is not None else 0))
            pages = [rows[i:i + PAGE] for i in range(0, len(rows), PAGE)] or [[]]
            for i, pg in enumerate(pages):
                json.dump({'n': len(rows), 'pages': len(pages), 'page': i, 'rows': pg},
                          open(os.path.join(d, 'big', f'{safe(k)}.{i}.json'), 'w'),
                          ensure_ascii=False, separators=(',', ':'))

    def marker(k):
        v = data[k]
        if isinstance(v, list):
            return {'big': len(v), 'pages': (len(v) + PAGE - 1) // PAGE}
        return {'big': 1, 'pages': 1}         # one whole value, one page

    shard_data = {k: (marker(k) if k in bigkeys else data[k]) for k in data}
    sizes2 = {k: entry(k, v) for k, v in shard_data.items()}
    assign, manifest = shard_table(sizes2)
    buckets = collections.defaultdict(dict)
    for k, v in shard_data.items():
        buckets[assign[k]][k] = v
    big = 0
    for g, obj in buckets.items():
        p = os.path.join(d, g + '.json')
        json.dump(obj, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
        big = max(big, os.path.getsize(p))
    bigmax = 0
    for f in glob.glob(os.path.join(d, 'big', '*.json')):
        bigmax = max(bigmax, os.path.getsize(f))
    print(f'  {name}: {len(data):,} keys, {len(buckets)} shards, '
          f'largest {big/1000:.0f} kB'
          + (f'; {len(bigkeys)} overflow files, largest {bigmax/1000:.0f} kB'
             if bigkeys else ''))
    return manifest, len(data), big, sorted(bigkeys)


# ------------------------------------------------------------ the glosses --
def load_glosses():
    print('glosses…', file=sys.stderr)
    by_form = collections.defaultdict(list)
    n = 0
    for f in sorted(glob.glob(os.path.join(REPO, '_gloss/by_volume/*.json'))):
        if os.path.basename(f) == 'index.json':
            continue
        for r in json.load(open(f)):
            n += 1
            row = {
                'l': r['lemma'],
                'g': r['gloss'],
                'v': r['vol'],
                'n': r['n'],
                'p': r['printed_first'],
                's': r['sutta'],
                # the number of words the edition printed in bold
                'w': r['words'],
                # The stems of the bold lemma: the browser tests these against
                # the paragraph on screen before promoting the row (see the
                # PROXIMITY note above).  Cheap to ship, and it is what turns a
                # 57%-right guess into a check.
                #
                # !!! A LIST WITH ITS REPEATS, NOT A SET.  The first version
                # deduplicated, and `Tassa tassā` — two words, one stem — came
                # out as a single-stem lemma: it then counted as "one word" for
                # grouping, and its presence test passed on a paragraph holding
                # a single `tassa`.  Both wrong, and the reader gate caught
                # both.  With repeats kept, the test is a multiset containment:
                # a two-word lemma needs two matching words on the page.
                'k': sorted(stem(w) for w in words(r['lemma']) if len(w) > 1),
            }
            if r['truncated']:
                row['t'] = 1
            if r['quoted_lemma']:
                row['q'] = 1
            if r['series_head']:
                row['h'] = 1
            for cd in r['candidates']:
                by_form[cd].append(row)
    print(f'  {n:,} gloss rows over {len(by_form):,} keyed forms', file=sys.stderr)
    return by_form


# ------------------------------------------------------------- the counts --
def load_freq():
    print('counts…', file=sys.stderr)
    freq = {}
    for f in glob.glob(os.path.join(REPO, '_vocab/freq/*.json')):
        if os.path.basename(f) == 'index.json':
            continue
        freq.update(json.load(open(f)))
    print(f'  {len(freq):,} forms', file=sys.stderr)
    return freq


# ------------------------ DPD, build-time filter only: the synonym index ----
def read_stardict_idx(path):
    """StarDict .idx: word\\0 offset(4) size(4).  Returns the ordered list of
    headwords -- strings only, no definitions are read."""
    raw = open(path, 'rb').read()
    out, i, n = [], 0, len(raw)
    while i < n:
        j = raw.index(b'\0', i)
        out.append((raw[i:j].decode('utf-8'), struct.unpack('>I', raw[j + 1:j + 5])[0]))
        i = j + 9
    return out


def read_stardict_syn(path, headwords):
    """StarDict .syn: word\\0 index(4) -> the headword at that index."""
    raw = gzip.open(path, 'rb').read() if path.endswith('.dz') else open(path, 'rb').read()
    syn = collections.defaultdict(set)
    i, n = 0, len(raw)
    while i < n:
        j = raw.index(b'\0', i)
        w = raw[i:j].decode('utf-8')
        idx = struct.unpack('>I', raw[j + 1:j + 5])[0]
        if idx < len(headwords):
            syn[w].add(headwords[idx][0])
        i = j + 5
    return syn


def load_dpd_index():
    print('DPD form→headword index (build-time filter only; no DPD text is read)…',
          file=sys.stderr)
    idx = read_stardict_idx(os.path.join(DPD_DIR, 'dpd.idx'))
    syn = read_stardict_syn(os.path.join(DPD_DIR, 'dpd.syn.dz'), idx)
    print(f'  {len(idx):,} headwords, {len(syn):,} inflected forms', file=sys.stderr)
    return idx, syn


# ------------------------------------------------------------------- PED ---
FULLWIDTH = {'，': ', ', '（': ' (', '）': ') ', '；': '; ', '：': ': ',
             '。': '. ', '、': ', ', '［': '[', '］': ']'}


def load_ped():
    print('PED (PTS 1921–25, public domain)…', file=sys.stderr)
    import csv
    csv.field_size_limit(10 ** 9)
    ped = collections.defaultdict(list)
    n = 0
    for fn in ('dict_words_1.csv', 'dict_words_2.csv'):
        p = os.path.join(PCED_DIR, fn)
        for row in csv.reader(open(p, encoding='utf-8')):
            if len(row) < 7 or row[2] != 'P':
                continue
            n += 1
            hw, body = row[3], row[6]
            for a, b in FULLWIDTH.items():
                body = body.replace(a, b)
            body = re.sub(r'\s+', ' ', body).strip()
            ped[hw].append(body)
    print(f'  {n:,} entries over {len(ped):,} headwords', file=sys.stderr)
    return ped


# ------------------------------------------------------------------ main ---
def main():
    os.makedirs(OUT, exist_ok=True)
    gloss = load_glosses()
    freq = load_freq()
    ped = load_ped()
    idx, syn = load_dpd_index()

    # PED is keyed by lemma; the reader clicks an inflected form.  Resolve
    # through DPD's synonym index, then keep only the (form -> PED headword)
    # pairs.  Nothing of DPD survives into the output but the pairing.
    print('resolving forms → PED headwords…', file=sys.stderr)
    ped_keys = {}
    for h in ped:
        ped_keys.setdefault(fold(h.lstrip('°')), []).append(h)
    forms = {}
    hit = 0
    for form in freq:
        cands = set()
        for h in syn.get(form, set()) | syn.get(form.lower(), set()):
            base = re.sub(r'\s*\d+$', '', h)
            for pk in ped_keys.get(fold(base), ()):
                cands.add(pk)
        # a form that IS a PED headword needs no index
        for pk in ped_keys.get(fold(form), ()):
            cands.add(pk)
        if cands:
            forms[form] = sorted(cands)
            hit += 1
    print(f'  {hit:,} of {len(freq):,} forms reach a PED headword '
          f'({100*hit/len(freq):.1f}%)', file=sys.stderr)

    # ship only the PED entries something can reach
    reachable = {h for v in forms.values() for h in v}
    ped_ship = {h: ped[h] for h in reachable}
    print(f'  shipping {len(ped_ship):,} of {len(ped):,} PED headwords',
          file=sys.stderr)

    print('writing shards…')
    m_gloss, n_gloss, b_gloss, big_gloss = write_shards(
        'gloss', {k: v for k, v in gloss.items()}, allow_big=True)
    m_freq, n_freq, b_freq, _ = write_shards('freq', freq)
    m_ped, n_ped, b_ped, big_ped = write_shards('ped', ped_ship, allow_big=True)
    m_forms, n_forms, b_forms, _ = write_shards('forms', forms)

    json.dump({
        'built': 'build_lookup.py',
        'shard_key': "adaptive: the shortest prefix of fold(form), padded with "
                     "'_', that names a shard in this manifest; try depth 2 upward",
        'cap_bytes': CAP,
        'sets': {
            'gloss': {'keys': n_gloss, 'largest_bytes': b_gloss,
                      'overflow': big_gloss,
                      'overflow_note': 'these forms carry more rows than a '
                                       'shard may hold; their rows live in '
                                       'gloss/big/<safe(form)>.json and the '
                                       'shard records only the count',
                      'source': "the edition's own glosses, _gloss/by_volume/ "
                                "(roadmap step 3, 187,248 rows over 90 volumes)"},
            'freq': {'keys': n_freq, 'largest_bytes': b_freq,
                     'source': '_vocab/freq/ (roadmap step 1, 8,054,256 tokens)'},
            'ped': {'keys': n_ped, 'largest_bytes': b_ped,
                    'source': "PTS Pali-English Dictionary, Rhys Davids & Stede "
                              "1921-25 — public domain; via the PCED dataset "
                              "(github.com/siongui/data, dictionary id P)"},
            'forms': {'keys': n_forms, 'largest_bytes': b_forms,
                      'source': "form → PED headword.  Resolved with DPD's "
                                "synonym index as a BUILD-TIME FILTER (§9); "
                                "dpd.dict.dz is never opened and no DPD text "
                                "is present in any shipped file."},
        },
        'withheld': {
            'Abhidhāna / PEU': 'awaiting Ven. Subhuti / pm12e maintainers, and '
                               'the Ministry question of §8',
            'PPN': 'awaiting its licence check',
            'DPD / DOP / CPD / CPED': 'filter-side only per §9',
        },
        'shards': {'gloss': m_gloss, 'freq': m_freq, 'ped': m_ped, 'forms': m_forms},
    }, open(os.path.join(OUT, 'index.json'), 'w'), ensure_ascii=False, indent=1)
    print('index.json written')


if __name__ == '__main__':
    main()
