#!/usr/bin/env python3
"""Build `stores/lookup_eval/hw/` — the APD books and the Tipiṭaka
Pāḷi-Myanmā-Abhidhāna keyed on THEIR OWN HEADWORDS.

WHY THIS EXISTS, IN ONE PARAGRAPH.  `build_eval.py` builds the `lem` key set as
corpus forms → DPD index → DPD headwords, and then attaches the Abhidhāna and
all twenty-four APD books TO THOSE LEMMAS AND NOTHING ELSE.  So the question the
build asks is not "does the Abhidhāna have this word?" but "does DPD have a
headword for some corpus form of it?", and 163,453 of 210,111 headwords —
77.8% — are unreachable from the reader.  §9 admits the Abhidhāna as the only
dictionary that is an authority and ranks DPD lowest; the build inverts that
exactly.  The reader met it as `yathānisinna` returning "no entry" while
dictionary.sutta.org answered it from books B and K, both of which are in our
own `_dictsrc/`.  Full note: `claude/dpd_gates_the_abhidhana.md`.

WHAT THIS DOES AND, MORE IMPORTANTLY, WHAT IT DOES NOT.

  * It writes a SEPARATE store.  `lem` is not widened, not rebuilt, not read.
    Nothing that passes a gate today can regress, because nothing it depends on
    changes.  The panel consults `hw` only where `lem` has already returned
    nothing — the path that says "no entry" today.
  * It keys on `fold(headword)`, not on the raw accented form.  `panel.js
    look()` tries the exact key then `toLowerCase()`, so a store keyed on
    PCED's `acc` (`Yathānisinna`, capitalised) would be unreachable from a
    lowercase query — the key-case trap the note names.  fold() lowercases AND
    strips diacritics, which closes that and gives §7's diacritic-insensitive
    lookup at the same time; the accented spellings are kept in the value's `w`
    field so the reader still sees the dictionary's own headword.
  * It carries NO DPD, no PED, no PEU, no PPN.  Those reach the reader through
    `lem` exactly as they do today.  This store is the two things §9 names and
    the build silenced: the Abhidhāna, and the APD books.
  * It does NOT touch the §2/§9 redistribution question.  These sources sit in
    `lookup_eval/` because their redistribution is unresolved and that is
    unchanged here; what is fixed is that even in evaluation, where the reader
    may lawfully consult them, three quarters of the lexicon was unreachable.

SIZE, MEASURED BEFORE IT WAS BUILT (`_panel/measure_own.py`, 2026-08-10):
185,809 folded keys · 145.8 MB of JSON · mean 785 B · largest single key 64 kB,
so NO key needs an overflow file · 6,714 shards, largest 150 kB, none over the
cap.  Every Abhidhāna headword is also a PCED headword under fold(), so the
union is PCED's 185,809 and not the two sets added together.

THE MANIFEST IS THIS STORE'S OWN, AND THAT IS ON PURPOSE.  `build_eval.py`
rewrites `stores/lookup_eval/index.json` wholesale at the end of every run, so
an `hw` entry added there would vanish on the next eval rebuild — silently, the
way `stores/lookup_eval/family/` vanished from a commit in 2026-08-09.  The
shard table therefore lives in `stores/lookup_eval/hw/index.json` and is fetched
lazily, only on a miss.

  python3 _panel/build_own.py            # build, gzip, write the manifest
  python3 _panel/build_own.py --no-gz    # plain .json only (local inspection)

AFTER RUNNING, TWO THINGS ARE STILL OUTSTANDING AND THE JOB IS NOT DONE
WITHOUT THEM: `pipeline/r2_upload.sh` must run (the panel fetches this store
from the R2 bucket, not from the site), and `WLV` in `site/reader/panel.js`
must be bumped (every fetch is versioned `?v=WLV`; without a bump a reader who
has the old manifest cached keeps it).

SANDBOX NOTE.  Files under the repository cannot be DELETED from the sandbox
("Operation not permitted"), so this script never deletes: it overwrites, and
REPORTS any file in the output directory that this run did not write, for the
host to remove.  A stale shard nobody notices is exactly the failure this
project keeps meeting.
"""
import json, os, re, sys, csv, gzip, glob, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
from build_lookup import fold, shard_table, CAP
from abhidhana_cites import row_value

PCED_JSONL = os.environ.get('PCED_JSONL',
                            os.path.join(REPO, '_dictsrc', 'pced_full.jsonl.gz'))
PM12E = os.environ.get('PM12E', os.path.join(REPO, '_dictsrc', 'pm12e.csv'))
EVAL_DIR = os.path.join(REPO, 'stores', 'lookup_eval')
OUT = os.path.join(EVAL_DIR, 'hw')
csv.field_size_limit(10 ** 9)

# THE SAME EXCLUSIONS `build_eval.py` MAKES — the Vietnamese, Japanese and
# Chinese dictionaries the reader asked not to build, and `V`, which is
# Malalasekera twice.  Copied rather than imported for the reason
# `abhidhana_cites.py` records, and ASSERTED against the eval manifest below:
# if PCED renumbers, or if build_eval's list changes, this build stops.
APD_DROP = {
    'U': 'Pali Viet Dictionary — Bửu Chơn',
    'Q': 'Pali Viet Vinaya Terms — Giác Nguyên',
    'E': 'Pali Viet Abhidhamma Terms — Tịnh Sự',
    'S': '《パーリ语辞典》水野弘元',
    'A': '《パーリ语辞典》增补改订 水野弘元',
    'J': '《パーリ语辞典-勘误表》覓寂尊者',
    'H': '《汉译パーリ语辞典》黃秉榮譯',
    'T': '《汉译パーリ语辞典》李瑩譯',
    'M': '《巴利语汇解》玛欣德尊者',
    'D': '《巴汉词典》Mahāñāṇo Bhikkhu',
    'F': '《巴汉词典》明法尊者增订',
    'G': '《巴利语字汇》葛印卡',
    'W': '《巴英术语汇编》温宗堃',
    'Z': '《巴汉佛学辞汇》张文明',
    'X': '《巴利语入门》释性恩',
    'V': 'Pali Proper Names Dictionary — the duplicate of DPPN.json',
}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def build():
    log('PCED (own headwords)…')
    keys = collections.defaultdict(lambda: collections.defaultdict(list))
    spell = collections.defaultdict(set)
    per_book = collections.Counter()
    seen_ids, dropped, n = set(), collections.Counter(), 0
    op = gzip.open if PCED_JSONL.endswith('.gz') else open
    with op(PCED_JSONL, 'rt', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            did = r['d']
            if did in APD_DROP:
                dropped[did] += 1
                continue
            # bodies in pced_full.jsonl.gz are ALREADY Zawgyi→Unicode converted
            # and census-verified (`_panel/zawgyi.py`); build_eval writes this
            # file with `already_converted=True` and so does this build.
            body = re.sub(r'\s+', ' ', r['b']).strip()
            acc = (r.get('acc') or r.get('hw') or '').strip()
            if not body or not acc:
                continue
            seen_ids.add(did)
            k = fold(acc)
            bucket = keys[k][did]
            if body not in bucket:          # the same dedupe `_take` makes
                bucket.append(body)
            spell[k].add(acc.lower())
            per_book[did] += 1
            n += 1
    log(f'  {n:,} rows · {len(keys):,} folded keys · {len(seen_ids)} dictionaries')

    log('Abhidhāna (pm12e.csv, own headwords)…')
    na, abhi_keys = 0, set()
    with open(PM12E, newline='', encoding='utf-8') as f:
        for row in csv.reader(f):
            if not row or not row[0].strip():
                continue
            hw = row[0].strip()
            k = fold(hw)
            keys[k]['_a'].append(row_value(row))
            spell[k].add(hw.lower())
            abhi_keys.add(k)
            na += 1
    log(f'  {na:,} rows · {len(abhi_keys):,} folded keys')

    # !!! THE PANEL NAMES A SECTION FROM THE EVAL MANIFEST'S `apd_books`, NEVER
    # FROM A LIST OF ITS OWN.  A dictionary id in this store that is absent
    # there would draw as a bare letter with no attribution — which for these
    # sources is not a cosmetic problem but an attribution one (principle 4).
    man_path = os.path.join(EVAL_DIR, 'index.json')
    if os.path.exists(man_path):
        eman = json.load(open(man_path, encoding='utf-8'))
        books = eman.get('apd_books') or {}
        unknown = sorted(seen_ids - set(books))
        assert not unknown, (
            f'ids in this store that stores/lookup_eval/index.json cannot name: '
            f'{unknown} — the panel would draw them unattributed')
        overlap = sorted(seen_ids & set(APD_DROP))
        assert not overlap, f'APD_DROP and the built ids overlap: {overlap}'

    values = {}
    for k, m in keys.items():
        v = {'w': sorted(spell[k])}
        apd = {d: b for d, b in m.items() if d != '_a'}
        if apd:
            v['apd'] = apd
        if '_a' in m:
            v['a'] = m['_a']
        values[k] = v
    return values, seen_ids, per_book, dropped, len(abhi_keys)


def write(values, gz=True):
    os.makedirs(OUT, exist_ok=True)
    before = {os.path.basename(p) for p in glob.glob(os.path.join(OUT, '*.json'))}
    ent = lambda k, v: (len(k.encode()) + 3
                        + len(json.dumps(v, ensure_ascii=False).encode()) + 1)
    sizes = {k: ent(k, v) for k, v in values.items()}
    # MEASURED FIRST (_panel/measure_own.py): no single key exceeds the cap, so
    # this store needs no overflow files at all and the sharder alone keeps the
    # promise.  Asserted rather than assumed — if a future dictionary import
    # breaks it, this stops instead of quietly shipping a 400 kB shard.
    over = {k: b for k, b in sizes.items() if b > CAP}
    assert not over, (f'{len(over)} keys exceed the {CAP} B cap on their own '
                      f'(largest {max(over, key=over.get)!r}); this store has no '
                      f'overflow path — see build_lookup.write_shards')
    assign, manifest = shard_table(sizes)
    buckets = collections.defaultdict(dict)
    for k, v in values.items():
        buckets[assign[k]][k] = v
    biggest, written = 0, set()
    for g, obj in buckets.items():
        p = os.path.join(OUT, g + '.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
        written.add(g + '.json')
        biggest = max(biggest, os.path.getsize(p))
        if gz:
            b = open(p, 'rb').read()
            gzb = gzip.compress(b, 9, mtime=0)   # mtime=0: byte-identical reruns
            open(p + '.gz', 'wb').write(gzb)
            # verify EVERY shard round-trips, not a sample — gzip_shards.py's
            # discipline, and for the same reason: a shard that inflates to
            # something else is a wrong dictionary entry on a reader's screen.
            assert gzip.decompress(open(p + '.gz', 'rb').read()) == b, \
                f'{g}.json.gz does not round-trip'
    log(f'  {len(values):,} keys · {len(buckets):,} shards · '
        f'largest {biggest/1000:.0f} kB (cap {CAP/1000:.0f} kB)')
    stale = sorted(before - written - {'index.json'})
    if stale:
        log(f'  !! {len(stale)} file(s) in {OUT} this run did not write. The '
            f'sandbox cannot delete; remove them on the host: {stale[:10]}'
            + (' …' if len(stale) > 10 else ''))
    return manifest, biggest, stale


def main():
    gz = '--no-gz' not in sys.argv
    values, ids, per_book, dropped, n_abhi = build()
    log('writing shards…')
    manifest, biggest, stale = write(values, gz=gz)
    json.dump({
        'built': '_panel/build_own.py',
        'purpose': 'The APD books and the Tipiṭaka Pāḷi-Myanmā-Abhidhāna keyed '
                   'on their OWN headwords, so that neither needs a DPD lemma '
                   'to be reachable. EVALUATION ONLY, exactly as the rest of '
                   'stores/lookup_eval/ is: §2 and §9 redistribution unchanged.',
        'why': 'claude/dpd_gates_the_abhidhana.md — 163,453 of 210,111 headwords '
               '(77.8%) were unreachable because the lem key set is DPD\'s.',
        'key': 'fold(headword): lowercased and diacritic-stripped, the same '
               'fold() build_lookup.py shards by. The dictionaries\' own '
               'accented spellings are the value\'s `w` field.',
        'shard_key': "same as stores/lookup/: adaptive prefix of the key, padded "
                     "with '_', shortest that names a shard in this manifest",
        'cap_bytes': CAP,
        'largest_bytes': biggest,
        'keys': len(values),
        'abhidhana_keys': n_abhi,
        'apd_rows': {k: per_book[k] for k in sorted(per_book)},
        'apd_dropped': {k: dropped[k] for k in sorted(dropped)},
        'note': 'apd_books, apd_order and apd_zawgyi are NOT repeated here: the '
                'panel takes every label, attribution and Zawgyi flag from '
                'stores/lookup_eval/index.json, so the two cannot drift.',
        'gz': ['hw'] if gz else [],
        'shards': manifest,
    }, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'),
        ensure_ascii=False)
    log(f'index.json written · {len(manifest):,} shards'
        + (' · gzipped' if gz else ' · NOT gzipped'))
    log('')
    log('NOT DONE YET: run pipeline/r2_upload.sh (the panel fetches this store '
        'from the R2 bucket) and bump WLV in site/reader/panel.js.')


if __name__ == '__main__':
    main()
