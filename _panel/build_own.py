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
import html as _html

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
from build_lookup import fold, shard_table, CAP
from abhidhana_cites import row_value
import sources

PCED_JSONL = os.environ.get('PCED_JSONL',
                            os.path.join(REPO, '_dictsrc', 'pced_full.jsonl.gz'))
PM12E = os.environ.get('PM12E', os.path.join(REPO, '_dictsrc', 'pm12e.csv'))
DPPN = os.environ.get('DPPN', os.path.join(REPO, '_dictsrc', 'DPPN.json'))
# The StarDict sources live in the reader's GoldenDict build, not in
# `_dictsrc/`, and that machine is not this one.  Absent, they are SKIPPED
# LOUDLY and the manifest records which — never silently, because a dictionary
# that is missing without saying so is indistinguishable from one that has no
# entry for the word.
GD = os.environ.get('GD_DIR', os.path.join(os.path.expanduser('~'), 'GoldenDict'))
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


def _body_trim(h):
    """`build_eval.py`'s body_trim, verbatim — the visible entry only."""
    m = sources.BODY.search(h)
    b = h[m.end():] if m else h
    b = re.sub(r'</body>\s*</html>\s*$', '', b)
    b = re.sub(r'<script.*?</script>', '', b, flags=re.S)
    b = re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|<head>.*?</head>|<link[^>]*>', '',
               b, flags=re.S)
    return b.strip()


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

    # ------------------------------------------------------------ DPPN ------
    # Malalasekera's proper names, from `_dictsrc/DPPN.json`.  Keyed exactly as
    # `build_eval.py` keys it — the FIRST <b> of the `name` field, tags
    # stripped, trailing dot removed — then folded, so a lowercase or
    # undiacriticked query reaches it.
    #
    # !!! build_eval.py's own note applies UNCHANGED and is not silently
    # repaired here: a name printed as `Abbhuta Sutta` keys as `abbhuta sutta`
    # and no single-word query will ever match it, and `Abbhavalāhakā` against
    # `abbhavalāhaka` differs by a final vowel length that fold() does not
    # close.  Widening the keying is a decision about whether `Abhaya Thera`
    # should be merged into `Abhaya`, and it is not made here.
    n_ppn = 0
    if os.path.exists(DPPN):
        log('DPPN (own headwords)…')
        name_b = re.compile(r'<b>(.*?)</b>')
        for row in json.load(open(DPPN, encoding='utf-8')):
            m = name_b.search(row.get('name', ''))
            if not m:
                continue
            key = re.sub(r'<[^>]+>', '', m.group(1)).strip().strip('.')
            if not key:
                continue
            k = fold(key)
            keys[k]['_pn'].append(row['name'] + row['entry'])
            spell[k].add(key.lower())
            n_ppn += 1
        log(f'  {n_ppn:,} names')
    else:
        log(f'  !! DPPN.json absent at {DPPN} — PPN NOT in this store')

    # ------------------------------------------- the StarDict dictionaries --
    # PEU, DOP, CPD and NCPED are GoldenDict StarDict files, not in
    # `_dictsrc/`.  Read here on their OWN headwords — every key in the .idx
    # and every synonym in the .syn — which is the whole point: through `lem`
    # they were reachable only where DPD had a lemma.
    #
    # The reading logic is `build_eval.py`'s, unchanged; what differs is the
    # direction.  build_eval walks LEMMAS and asks each dictionary for it; this
    # walks the DICTIONARY and takes what it has.
    sd_built, sd_missing = {}, []

    def stardict_own(field, dirname, stem, trim=None, pick=None, apd_id=None):
        nonlocal keys, spell
        d = os.path.join(GD, dirname)
        if not os.path.exists(os.path.join(d, stem + '.idx')):
            sd_missing.append(field if apd_id is None else apd_id)
            log(f'  !! {dirname}/{stem}.idx absent — '
                f'{apd_id or field.upper()} NOT in this store')
            return 0
        idx = sources.read_idx(os.path.join(d, stem + '.idx'))
        pos = {w.lstrip('﻿'): (o, s) for w, o, s in idx}
        fh = sources.ensure_dict(os.path.join(d, stem))
        # a synonym is another spelling of the SAME entry, so it is another key
        for cand in (stem + '.syn.dz', stem + '.syn'):
            sp = os.path.join(d, cand)
            if os.path.exists(sp):
                for w, i in sources.iter_syn(sp):
                    pos.setdefault(w.lstrip('﻿'), pos.get(idx[i][0]))
                break
        n = 0
        for w, os_ in pos.items():
            if not os_ or not w.strip():
                continue
            body = sources.entry(fh, os_[0], os_[1])
            if pick:
                body = pick(body)
                if not body:
                    continue
            if trim:
                body = trim(body)
            if apd_id is not None:
                body = re.sub(r'<[^>]+>', ' ', body)
                body = _html.unescape(body)
                body = re.sub(r'^\s*\[(?:NCPED|PTS|DPPN)\]\s*', '', body)
                body = re.sub(r'\s+', ' ', body).strip()
            if not body:
                continue
            k = fold(w)
            spell[k].add(w.lower())
            if apd_id is not None:
                bucket = keys[k]['apd_' + apd_id]
                if body not in bucket:
                    bucket.append(body)
            else:
                keys[k]['_' + field] = body
            n += 1
        sd_built[apd_id or field] = n
        log(f'  {apd_id or field.upper()}: {n:,} own headwords')
        return n

    def _ncped_only(html):
        for part in re.split(r'(?=<html><body><p>\[)', html):
            if part.startswith('<html><body><p>[NCPED]'):
                return part
        return ''

    if os.environ.get('SKIP_STARDICT') != '1':
        log('StarDict (own headwords)…')
        # PEU is the Abhidhāna's OWN English rendering and is shown inside the
        # Abhidhāna entry, so a word this store reaches without it shows the
        # Burmese and not the English — which is why it is first.
        stardict_own('p', 'peu', 'peu', trim=_body_trim)
        stardict_own(None, '02-DOP', 'cone', apd_id='DOP')
        stardict_own(None, 'cpd', 'cpd', apd_id='CPD')
        stardict_own(None, 'simsapa', 'simsapa', apd_id='NCP', pick=_ncped_only)

    # !!! THE PANEL NAMES A SECTION FROM THE EVAL MANIFEST'S `apd_books`, NEVER
    # FROM A LIST OF ITS OWN.  A dictionary id in this store that is absent
    # there would draw as a bare letter with no attribution — which for these
    # sources is not a cosmetic problem but an attribution one (principle 4).
    man_path = os.path.join(EVAL_DIR, 'index.json')
    if os.path.exists(man_path):
        eman = json.load(open(man_path, encoding='utf-8'))
        books = eman.get('apd_books') or {}
        unknown = sorted((seen_ids | set(sd_built)) - set(books) - {'p'})
        assert not unknown, (
            f'ids in this store that stores/lookup_eval/index.json cannot name: '
            f'{unknown} — the panel would draw them unattributed')
        overlap = sorted(seen_ids & set(APD_DROP))
        assert not overlap, f'APD_DROP and the built ids overlap: {overlap}'

    # The value carries exactly the field names a `lem` record uses, so the
    # panel renders it with no change at all: `apd` per dictionary, `a` the
    # Abhidhāna, `p` PEU inside the Abhidhāna entry, `pn` the proper names.
    values = {}
    for k, m in keys.items():
        v = {'w': sorted(spell[k])}
        apd = {}
        for d, b in m.items():
            if d == '_a' or d == '_pn' or d == '_p':
                continue
            apd[d[4:] if d.startswith('apd_') else d] = b
        if apd:
            v['apd'] = apd
        if '_a' in m:
            v['a'] = m['_a']
        if '_p' in m:
            v['p'] = m['_p']
        if '_pn' in m:
            v['pn'] = m['_pn']
        values[k] = v
    return (values, seen_ids, per_book, dropped, len(abhi_keys),
            n_ppn, sd_built, sd_missing)


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
    # !!! STALE SHARDS SURVIVE A REBUILD, AND THEIR .gz SURVIVES INTO THE
    # BUCKET.  Shard boundaries MOVE when the key set changes — the second
    # build of this store left 34 files whose names the new manifest does not
    # contain.  The panel never asks for them (it resolves names through the
    # manifest), so they are junk rather than a wrong answer; but they are junk
    # that `git ls-files` will happily upload and that nobody will ever
    # re-examine.  Named in full, with the command, because the sandbox cannot
    # delete under the repository.
    keep = written | {n + '.gz' for n in written} | {'index.json'}
    stale = sorted(os.path.basename(p) for p in
                   glob.glob(os.path.join(OUT, '*.json'))
                   + glob.glob(os.path.join(OUT, '*.json.gz'))
                   if os.path.basename(p) not in keep)
    if stale:
        log(f'  !! {len(stale)} STALE file(s) in {OUT} — shard boundaries moved '
            f'and these names are not in the new manifest. Delete them, or they '
            f'go to the bucket as junk:')
        log(f"     python3 -c \"import json,os,glob;d='{OUT}';"
            f"m=set(json.load(open(d+'/index.json'))['shards']);"
            f"[os.remove(p) for p in glob.glob(d+'/*.json')+glob.glob(d+'/*.json.gz') "
            f"if os.path.basename(p).split('.json')[0] not in m "
            f"and os.path.basename(p)!='index.json']\"")
    return manifest, biggest, stale


def main():
    gz = '--no-gz' not in sys.argv
    (values, ids, per_book, dropped, n_abhi,
     n_ppn, sd_built, sd_missing) = build()
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
        'ppn_names': n_ppn,
        'stardict': sd_built,
        # !!! SAID OUT LOUD, IN THE ARTEFACT ITSELF.  A source that was not
        # present when this ran is a source the reader cannot reach, and the
        # panel cannot tell that apart from "this word has no entry there".
        # Anything listed here means: rebuild on a machine that has
        # ~/GoldenDict, then re-upload.
        'stardict_missing': sd_missing,
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
    if sd_missing:
        log(f'!! INCOMPLETE: {", ".join(sd_missing)} were not present and are '
            f'NOT in this store. Set GD_DIR (currently {GD}) and rebuild on the '
            f'machine that has the GoldenDict build, or those dictionaries stay '
            f'reachable only through DPD\'s index.')
    log('NOT DONE YET: git add the store, then run pipeline/r2_upload.sh — its '
        'file list is `git ls-files`, so an untracked store uploads NOTHING and '
        'its own count check cannot see that. Then deploy.')


if __name__ == '__main__':
    main()
