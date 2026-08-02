#!/usr/bin/env python3
"""Build the EVALUATION lookup data — every dictionary, behind its own flag.

WHAT THIS IS, AND WHY IT IS SEPARATE FROM build_lookup.py
`build_lookup.py` writes what a public build may carry: the edition's own
glosses, corpus counts, and the public-domain PED.  This writes everything
else, into `site/lookup_eval/`, for the reader to consult on their own machine
while the licences are still open questions:

  DPD          Digital Pāḷi Dictionary (Bodhirasa) — CC BY-NC-SA.  §9 also
               settles it before licensing does: DPD is a build-time filter and
               never the panel's voice.  It is here banner'd, for comparison.
  Abhidhāna    Tipiṭaka-Pāḷi-Myanmā-Abhidhāna, Burmese with citations, from the
               pm12e digitisation.  THE lexical authority (§9) — waiting on
               Ven. Subhuti / the pm12e maintainers and the Ministry (§8 Q6).
  PEU          its English rendering; Google-marked entries segregated.
  CPED         Concise Pali-English Dictionary (A.P. Buddhadatta).
  PPN          Dictionary of Pāli Proper Names (Malalasekera), DPPN v1.0.8.
  Nyanatiloka  Buddhist Dictionary — a doctrinal glossary, not a lexicon.
  VRI          Pali-Dictionary, Vipassana Research Institute.
  and the four Burmese dictionaries from the PCED dataset, Zawgyi→Unicode
  converted and census-verified by `zawgyi.py`:
  PWG          Pali Word Grammar (the pm1 grammar/etymology layer)
  TPM          Tipiṭaka Pāḷi-Myanmar Dictionary (a second, independent copy of
               the Abhidhāna's digitisation lineage — the verification witness
               the inventory nominated)
  Roots        Pali Roots Dictionary (ဓာတ်အဘိဓာန်) — relevant to step 4
  UHS          U Hau Sein's Pāḷi-Myanmar Dictionary

NOTHING HERE MAY REACH A PUBLIC BUILD.  The output directory is gitignored and
the panel keeps it behind a second flag, off by default; every tab carries its
own attribution and an evaluation banner.  `site/lookup/` stays what ships.

Sharding, the shard-name scheme and the 150 kB cap are `build_lookup.py`'s, so
one lookup routine in the panel serves both.
"""
import json, os, re, sys, csv, struct, gzip, collections
import html as _html

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
import sources
import zawgyi
from build_lookup import write_shards, fold

OUT = os.path.join(REPO, 'site', 'lookup_eval')
GD = os.environ.get('GD_DIR', '/mnt/user-data/uploads/GoldenDict')
PCED = os.environ.get('PCED_DIR', os.path.join(REPO, '..', 'src/pced/dictionary'))
PM12E = os.environ.get('PM12E', os.path.join(REPO, '..', 'src/dl/pm12e/pm12e.csv'))
DPPN = os.environ.get('DPPN', os.path.join(
    REPO, '..', 'src/dl/othdict/dictionaries/dppn/DPPN.json'))

csv.field_size_limit(10 ** 9)
norm = lambda w: w.lower().replace('ṁ', 'ṃ')
base_of = lambda h: re.sub(r'\s+[\d.]+$', '', h)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- the forms --
log('corpus vocabulary…')
FORMS = set()
for f in os.listdir(os.path.join(REPO, '_vocab/freq')):
    if f == 'index.json' or not f.endswith('.json'):
        continue
    FORMS.update(json.load(open(os.path.join(REPO, '_vocab/freq', f))))
NEED = {}
for w in FORMS:
    NEED.setdefault(norm(w), set()).add(w)
log(f'  {len(FORMS):,} forms, {len(NEED):,} normalised')

# ------------------------------------------------ DPD: form → headword ------
log('DPD index…')
dpd_idx = sources.read_idx(os.path.join(GD, 'dpd', 'dpd.idx'))
dpd_pos = {w: i for i, (w, _, _) in enumerate(dpd_idx)}
form2hw = collections.defaultdict(set)
for w in NEED:
    if w in dpd_pos:
        form2hw[w].add(w)
for w, n in sources.iter_syn(os.path.join(GD, 'dpd', 'dpd.syn.dz')):
    lw = w.lower()
    if lw in NEED:
        form2hw[lw].add(dpd_idx[n][0])
HWS = sorted({h for s in form2hw.values() for h in s})
LEMMAS = sorted({base_of(h) for h in HWS})
log(f'  {len(form2hw):,} forms resolve · {len(HWS):,} headwords · {len(LEMMAS):,} lemmas')

# !!! READ IN OFFSET ORDER, NOT ALPHABETICAL ORDER.  `HWS` is sorted by
# headword, so pulling entries in that order seeks backwards and forwards
# across an 889 MB file 74,146 times.  On a local disk that is merely wasteful;
# over the device bridge, where the user's own machine runs this build, it
# defeats readahead completely -- the first attempt sat in this loop for a
# quarter of an hour and was still going.  Sorting by offset makes the same
# reads monotonic, which is to say sequential.
log('DPD entries…')
dpdf = sources.ensure_dict(os.path.join(GD, 'dpd', 'dpd'))
DPD = {}
by_off = sorted(((dpd_idx[dpd_pos[h]][1], dpd_idx[dpd_pos[h]][2], h) for h in HWS))
for off, sz, h in by_off:
    DPD[h] = sources.dpd_trim(sources.entry(dpdf, off, sz))
log(f'  {len(DPD):,} entries')

# the lemma key set every other dictionary is looked up against
LEMSET = {}
for lem in LEMMAS:
    LEMSET.setdefault(norm(lem), set()).add(lem)

REC = collections.defaultdict(dict)          # lemma -> {source: value}


def put(lem, key, val):
    if val:
        REC[lem][key] = val


# ------------------------------------------------------------- StarDict ----
def stardict(name, dirname, stem, field, trim=None, syn=True):
    idx = sources.read_idx(os.path.join(GD, dirname, stem + '.idx'))
    pos = {w.lstrip('﻿'): (o, s) for w, o, s in idx}
    f = sources.ensure_dict(os.path.join(GD, dirname, stem))
    syn_map = {}
    sp = os.path.join(GD, dirname, stem + '.syn.dz')
    if syn and os.path.exists(sp):
        for w, n in sources.iter_syn(sp):
            syn_map.setdefault(w, idx[n][0])
    n = 0
    for lem in LEMMAS:
        for k in (lem, norm(lem), lem.replace('ṃ', 'ṁ')):
            kk = k if k in pos else syn_map.get(k)
            if kk and kk in pos:
                o, s = pos[kk]
                body = sources.entry(f, o, s)
                put(lem, field, trim(body) if trim else body)
                n += 1
                break
    log(f'  {name}: {n:,} lemmas')
    return n


def body_trim(h):
    m = sources.BODY.search(h)
    b = h[m.end():] if m else h
    b = re.sub(r'</body>\s*</html>\s*$', '', b)
    b = re.sub(r'<script.*?</script>', '', b, flags=re.S)
    b = re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|<head>.*?</head>|<link[^>]*>', '',
               b, flags=re.S)
    return b.strip()


log('StarDict sources…')
stardict('CPED', '00-CPED', 'cped', 'cp', syn=False)
# PEU: keep the Google-Translate marking so the panel can segregate it
peu_idx = sources.read_idx(os.path.join(GD, 'peu', 'peu.idx'))
peu_pos = {w: (o, s) for w, o, s in peu_idx}
peu_syn = {}
for w, n in sources.iter_syn(os.path.join(GD, 'peu', 'peu.syn.dz')):
    peu_syn.setdefault(w, peu_idx[n][0])
peuf = sources.ensure_dict(os.path.join(GD, 'peu', 'peu'))
npeu = nmt = 0
for lem in LEMMAS:
    for k in (lem, norm(lem), lem.replace('ṃ', 'ṁ')):
        kk = k if k in peu_pos else peu_syn.get(k)
        if kk and kk in peu_pos:
            o, s = peu_pos[kk]
            h = sources.entry(peuf, o, s)
            put(lem, 'p', body_trim(h))
            REC[lem]['pk'] = kk
            if 'Google Translate' in h:
                REC[lem]['pm'] = 1
                nmt += 1
            npeu += 1
            break
log(f'  PEU: {npeu:,} lemmas ({nmt:,} machine-translated, segregated)')

# ------------------------------------------------------------------- PPN ----
log('DPPN…')
NAME_B = re.compile(r'<b>(.*?)</b>')
ppn = collections.defaultdict(list)
for row in json.load(open(DPPN)):
    m = NAME_B.search(row.get('name', ''))
    if not m:
        continue
    key = re.sub(r'<[^>]+>', '', m.group(1)).strip().strip('.').lower()
    if key:
        ppn[key].append(row['name'] + row['entry'])
n = 0
for lem in LEMMAS:
    v = ppn.get(lem.lower()) or ppn.get(norm(lem))
    if v:
        put(lem, 'pn', v); n += 1
log(f'  PPN: {n:,} lemmas of {len(ppn):,} names')

# ------------------------------------------------------- Abhidhāna (pm12e) --
# Citation transcoding is build_panel_data.py's, unchanged: the abbreviations
# are a closed set, the Burmese digits deterministic (incl. ၎ for 4 and
# letter-ဝ for 0 inside digit runs), and an abbreviation without a settled
# reading is LEFT IN BURMESE rather than guessed (principle 2).
BUR_ABBR = {
    'တိပိ': 'Tipi', 'ဓာန်': 'Dhān', 'ဋီ': 'ṭī', 'ရူ': 'Rū', 'ဋ္ဌ': 'ṭṭha',
    'ကစ္စည်း': 'Kacc', 'နီတိ': 'Nīti', 'သုတ္တ': 'Sutta', 'ဓာတု': 'Dhātu',
    'ဓာတွတ္ထ': 'Dhātvattha', 'မောဂ်': 'Mog', 'ဏွာဒိ': 'Ṇvādi',
    'နိရုတ္တိ': 'Nirutti', 'သဒ္ဒါ': 'Sadd', 'ပဒ': 'Pada', 'နှာ': 'p.',
    'သာရတ္ထ': 'Sāratth', 'မဏိမဉ္ဇူ': 'Maṇimañjū', 'ဝိဘာဝိနီ': 'Vibhāvinī',
    'အဘိ': 'Abhi', '၎': '〃', 'ဓာ': 'Dhā', 'ဝိ': 'Vi', 'ဒီ': 'Dī', 'မ': 'Ma',
    'သံ': 'Saṁ', 'အံ': 'Aṁ', 'ခု': 'Khu', 'ပဋိသံ': 'Paṭisaṁ', 'ဓမ္မ': 'Dhamma',
    'နေတ္တိ': 'Netti', 'ဝိသုဒ္ဓိ': 'Visuddhi', 'သီ': 'Sī', 'ဇာ': 'Jā',
}
BDIG = str.maketrans('၀၁၂၃၄၅၆၇၈၉၎ဝ', '012345678940')
NUMRUN = r'(?=[၀-၉၎ဝ]*[၀-၉၎])(?:[၀-၉၎]|ဝ(?![ါ-ှ]))+'
CITE_RE = re.compile(
    r'([က-ဿၚ-႟၎][က-ဿၚ-႟]*(?:၊(?:[က-ဿၚ-႟][က-ဿၚ-႟]*|[၀-၉၎]+))*)'
    r'[။၊]\s*(' + NUMRUN + r'(?:\s*[။၊\-]\s*' + NUMRUN + r')*)')


def transcode_cites(text):
    out = []
    for m in CITE_RE.finditer(text or ''):
        head, num = m.group(1), m.group(2)
        parts = []
        for comp in head.split('၊'):
            if re.fullmatch(r'[၀-၉၎]+', comp):
                parts.append(comp.translate(BDIG))
            else:
                parts.append(BUR_ABBR.get(comp, comp))
        n = re.sub(r'\s*[။၊]\s*', '.', num).translate(BDIG)
        out.append(' '.join(parts) + ' ' + n)
    seen, ded = set(), []
    for c in out:
        if c not in seen:
            seen.add(c); ded.append(c)
    return ded


log('Abhidhāna (pm12e.csv)…')
abhi = collections.defaultdict(list)
with open(PM12E, newline='', encoding='utf-8') as f:
    for row in csv.reader(f):
        if not row or not row[0]:
            continue
        r = [x.strip() for x in row[1:5]]
        cites = transcode_cites(r[1]) + transcode_cites(r[3])
        seen, ded = set(), []
        for c in cites:
            if c not in seen:
                seen.add(c); ded.append(c)
        abhi[row[0].strip().lower()].append(r + [ded])
n = 0
for lem in LEMMAS:
    v = abhi.get(lem.lower()) or abhi.get(norm(lem))
    if v:
        put(lem, 'a', v); n += 1
log(f'  Abhidhāna: {n:,} lemmas of {len(abhi):,} roman headwords')

# ------------------------------------------------------------------ PCED ----
# THE ĀMANTETI BUG, AND IT WAS TWO BUGS (2026-08-02, user-reported: clicking
# `āmanteti` gave two sources where dictionary.sutta.org gives ten).
#
#  1. THE KEY WAS THE WRONG COLUMN.  PCED stores each entry three ways: column
#     3 is the headword with its DIACRITICS STRIPPED (`amanteti`), column 4 is
#     the accented form (`āmanteti`), column 5 the capitalised one.  The first
#     build keyed on column 3 and looked it up with an accented lemma from DPD.
#     Those match only for words that have no diacritics at all: **468,611 of
#     504,414 rows — 92.9% — could never be found**, whatever else was right.
#     That, not the dictionary list, is why VRI reached 1,664 lemmas of 13,508
#     and Nyanatiloka 161 of 923.
#
#  2. ONLY SIX OF THE TWENTY-FOUR were imported.  The reader asked for "all the
#     English ones, and the Burmese ones too"; the site also carries Chinese,
#     Japanese and Vietnamese dictionaries, and those are what the missing
#     sources for `āmanteti` turned out to be (Mahāñāṇo, Ming-fa, Mizuno, Bửu
#     Chơn). All of them are imported now, and the panel renders them from the
#     book table rather than a hardcoded list, so the set cannot drift again.
#
# Lookup is now diacritic-insensitive on BOTH sides — fold() the key and
# fold() the lemma — which is also what §7 requires of search and what the site
# itself does.
log('PCED…')
BOOKS = {}
bpath = os.path.join(PCED, 'dict-books.csv')
if os.path.exists(bpath):
    for r in csv.reader(open(bpath, encoding='utf-8')):
        if len(r) > 3 and r[0] != 'b_lang':
            BOOKS[r[1]] = {'lang': r[0], 'name': r[2].strip(), 'author': r[3].strip()}
BOOKS_JSON = os.environ.get('PCED_BOOKS')
if not BOOKS and BOOKS_JSON and os.path.exists(BOOKS_JSON):
    BOOKS = json.load(open(BOOKS_JSON, encoding='utf-8'))

# THE VIETNAMESE, JAPANESE AND CHINESE DICTIONARIES ARE NOT BUILT (user, 2026-08-02).
#
# !!! FILTER BY ID, NEVER BY `BOOKS[id]['lang']`.  PCED's own language tags are
# wrong for exactly the dictionaries being dropped here: all three Vietnamese
# ones are tagged 'E' (English) and every Japanese-source one is tagged 'C'.
# A `lang` filter would keep the Vietnamese, drop nothing Japanese by name, and
# take out things nobody asked to lose.  So the list is explicit, each id
# carries the title it stands for, and the whole thing is asserted against
# `BOOKS` at build time -- if PCED ever renumbers, the build stops rather than
# silently pruning the wrong dictionary.
APD_DROP = {
    # Vietnamese
    'U': 'Pali Viet Dictionary — Bửu Chơn',
    'Q': 'Pali Viet Vinaya Terms — Giác Nguyên',
    'E': 'Pali Viet Abhidhamma Terms — Tịnh Sự',
    # Japanese (Mizuno Kōgen and its errata)
    'S': '《パーリ语辞典》水野弘元',
    'A': '《パーリ语辞典》增补改订 水野弘元',
    'J': '《パーリ语辞典-勘误表》覓寂尊者',
    # Chinese — including the two Chinese renderings of Mizuno
    'H': '《汉译パーリ语辞典》黃秉榮譯',
    'T': '《汉译パーリ语辞典》李瑩譯',
    'M': '《巴利语汇解》玛欣德尊者',
    'D': '《巴汉词典》Mahāñāṇo Bhikkhu',
    'F': '《巴汉词典》明法尊者增订',
    'G': '《巴利语字汇》葛印卡',
    'W': '《巴英术语汇编》温宗堃',
    'Z': '《巴汉佛学辞汇》张文明',
    'X': '《巴利语入门》释性恩',
}

# Order of presentation: English, then Burmese.  (Vietnamese and the
# Chinese/Japanese group used to follow; they are in APD_DROP now.)
APD_ORDER = ['P', 'C', 'N', 'I', 'V',            # English
             'K', 'B', 'R', 'O']                 # Burmese
ZAWGYI_IDS = {'B', 'K', 'O', 'R'}
assert not (APD_DROP.keys() & set(APD_ORDER)), \
    f'APD_DROP and APD_ORDER overlap: {APD_DROP.keys() & set(APD_ORDER)}'

pced = collections.defaultdict(lambda: collections.defaultdict(list))
zg_left = collections.Counter()
seen_ids = set()
dropped = collections.Counter()   # what APD_DROP kept out, reported at the end


def _take(dict_id, row, already_converted):
    """row = the raw PCED row.  Key on the ACCENTED form, folded."""
    if dict_id in APD_DROP:
        dropped[dict_id] += 1
        return
    seen_ids.add(dict_id)
    body = row['b']
    if dict_id in ZAWGYI_IDS:
        if not already_converted:
            body = zawgyi.convert(body)
        for ch in body:
            if 0x1060 <= ord(ch) <= 0x109F:
                zg_left[dict_id] += 1
    body = re.sub(r'\s+', ' ', body).strip()
    if not body:
        return
    # every spelling PCED gives, folded, so an accented lemma finds it.
    #
    # !!! THE SET DEDUPED THE RAW SPELLINGS AND fold() THEN COLLAPSED THEM.
    # PCED stores each entry three ways -- headword, accented, capitalised --
    # and `Nandana`/`nandana`/`nandanā` are three distinct raw strings that fold
    # to ONE key, so the same body was appended once per distinct spelling.
    # Measured before the fix, over 600 shards and 74,198 rows: 60.9% of every
    # APD row in the store was an exact duplicate, and 100% of lemmas were
    # affected.  Dedupe on the key that is actually used, and on the body, since
    # two spellings may legitimately carry different bodies.
    for k in {fold(k) for k in (row['hw'], row.get('acc') or '',
                                row.get('cap') or '') if k}:
        bucket = pced[k][dict_id]
        if body not in bucket:
            bucket.append(body)


JSONL = os.environ.get('PCED_JSONL')
if JSONL and os.path.exists(JSONL):
    import gzip as _gz
    op = _gz.open if JSONL.endswith('.gz') else open
    with op(JSONL, 'rt', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            _take(r['d'], r, True)
    log(f'  from {os.path.basename(JSONL)} (Zawgyi already converted)')
else:
    for fn in ('dict_words_1.csv', 'dict_words_2.csv'):
        for row in csv.reader(open(os.path.join(PCED, fn), encoding='utf-8')):
            if len(row) < 7:
                continue
            _take(row[2], {'hw': row[3], 'acc': row[4], 'cap': row[5], 'b': row[6]},
                  False)

# ------------------------------------------- StarDict into the aggregate ----
# The reader asked for DOP, CPD and NCPED, and for everything that is not the
# Abhidhāna or DPD to live inside the APD tab.  So these do NOT get tabs of
# their own: they are injected into the same `pced` map the PCED dictionaries
# use, which means the panel picks them up with no change at all -- it renders
# one section per id in the build's book table, never from a list of its own.
#
# Ids are multi-character on purpose.  PCED already owns 24 single letters and
# a collision would silently merge two dictionaries into one section.
#
# NCPED has no standalone file.  It exists only inside `simsapa`, which is a
# MERGE of four dictionaries -- Nyanatiloka, DPPN, NCPED and PTS PED -- three of
# which are already sections here.  Taking simsapa whole would reintroduce
# exactly the duplication this build was just fixed for.  Its entries are
# tagged by source (`<p>[NCPED]</p>`), so only that block is taken.
def _ncped_only(html):
    for part in re.split(r'(?=<html><body><p>\[)', html):
        if part.startswith('<html><body><p>[NCPED]'):
            return part
    return ''


def stardict_into_apd(dict_id, dirname, stem, name, author, lang='E', pick=None):
    d = os.path.join(GD, dirname)
    if not os.path.exists(os.path.join(d, stem + '.idx')):
        log(f'  {dict_id}: {dirname}/ not present — skipped')
        return 0
    idx = sources.read_idx(os.path.join(d, stem + '.idx'))
    pos = {w.lstrip('\ufeff'): (o, sz) for w, o, sz in idx}
    fh = sources.ensure_dict(os.path.join(d, stem))
    syn = {}
    for cand in (stem + '.syn.dz', stem + '.syn'):     # DOP ships it uncompressed
        sp = os.path.join(d, cand)
        if os.path.exists(sp):
            for w, i in sources.iter_syn(sp):
                syn.setdefault(w, idx[i][0])
            break
    BOOKS[dict_id] = {'lang': lang, 'name': name, 'author': author}
    # !!! WITHOUT THIS THE SECTION IS INVISIBLE.  The manifest builds both
    # `apd_books` and `apd_order` from `seen_ids`, which only `_take` fills.  A
    # dictionary absent from that set gets no book entry and no place in the
    # order, and the panel -- which renders strictly from the book table -- draws
    # nothing for it, with the data sitting right there in the shard.
    seen_ids.add(dict_id)
    hit = 0
    for lem in LEMMAS:
        for k in (lem, norm(lem), lem.replace('ṃ', 'ṁ')):
            kk = k if k in pos else syn.get(k)
            if not (kk and kk in pos):
                continue
            o, sz = pos[kk]
            body = sources.entry(fh, o, sz)
            if pick:
                body = pick(body)
            # APD bodies are rendered as ESCAPED plain text, so flatten here --
            # and unescape entities while doing it, or `&amp;` reaches the reader
            # as the five literal characters rather than an ampersand.
            body = re.sub(r'<[^>]+>', ' ', body)
            body = _html.unescape(body)
            # simsapa tags each merged source inline; the tag is how NCPED was
            # found, and it has no business being shown as part of the entry
            body = re.sub(r'^\s*\[(?:NCPED|PTS|DPPN)\]\s*', '', body)
            body = re.sub(r'\s+', ' ', body).strip()
            if body:
                bucket = pced[fold(lem)][dict_id]
                if body not in bucket:
                    bucket.append(body)
                hit += 1
            break
    log(f'  {dict_id} {name}: {hit:,} lemmas')
    return hit


if os.environ.get('SKIP_EXTRA') != '1':
    log('StarDict → APD…')
    stardict_into_apd('DOP', '02-DOP', 'cone', 'A Dictionary of Pāli',
                      'Margaret Cone — Pali Text Society, in copyright')
    stardict_into_apd('CPD', 'cpd', 'cpd', 'A Critical Pāli Dictionary',
                      'V. Trenckner et al. — Royal Danish Academy, Copenhagen')
    stardict_into_apd('NCP', 'simsapa', 'simsapa',
                      'New Concise Pāli-English Dictionary',
                      'NCPED — extracted from the Simsapa combined dictionary',
                      pick=_ncped_only)
    APD_ORDER.extend(['DOP', 'CPD', 'NCP'])

n = collections.Counter()
for lem in LEMMAS:
    e = pced.get(fold(lem))
    if not e:
        continue
    apd = {}
    for did, v in e.items():
        apd[did] = v
        n[did] += 1
    if apd:
        put(lem, 'apd', apd)
# No silent caps: say what was left out and how much of it there was.
if BOOKS:
    unknown = [k for k in APD_DROP if k not in BOOKS]
    assert not unknown, f'APD_DROP names ids PCED does not have: {unknown}'
missing = [k for k in APD_DROP if not dropped[k]]
log(f'  APD_DROP: {len(APD_DROP)} dictionaries excluded, '
    f'{sum(dropped.values()):,} rows not stored')
for k in sorted(dropped, key=lambda k: -dropped[k]):
    log(f'    {k}  {dropped[k]:8,}  {APD_DROP[k]}')
if missing:
    log(f'  !! these APD_DROP ids matched NOTHING: {missing} — either PCED has '
        f'renumbered or the source is not being read')
log(f'  {len(seen_ids)} dictionaries · lemmas reached: '
    + ' · '.join(f'{d}={n[d]:,}' for d in APD_ORDER if n[d]))
if zg_left:
    log(f'  !!! Zawgyi characters surviving conversion (flagged, not patched): '
        f'{dict(zg_left)}')

# ------------------------------------------------------------------ write ---
log('writing shards…')
os.makedirs(OUT, exist_ok=True)
import build_lookup
build_lookup.OUT = OUT                    # reuse the shipped sharder verbatim

FORMREC = {}
for w in FORMS:
    hs = sorted(form2hw.get(norm(w), ()))
    if not hs:
        continue
    bs = sorted({base_of(h) for h in hs})
    FORMREC[w] = {'h': hs, 'b': [b for b in bs if b in REC]}

m_form, n_form, b_form, _ = write_shards('form', FORMREC)
m_dpd, n_dpd, b_dpd, big_dpd = write_shards('dpd', DPD, allow_big=True)
m_lem, n_lem, b_lem, big_lem = write_shards('lem', dict(REC), allow_big=True)

json.dump({
    'built': 'build_eval.py',
    'purpose': 'EVALUATION ONLY. Local build; must not reach a public site. '
               'Every source here has an unresolved redistribution licence or '
               'is excluded by §9 as a voice.',
    'shard_key': "same as site/lookup/: adaptive prefix of fold(key), padded "
                 "with '_', shortest that names a shard in this manifest",
    'sets': {'form': n_form, 'dpd': n_dpd, 'lem': n_lem},
    'largest_bytes': {'form': b_form, 'dpd': b_dpd, 'lem': b_lem},
    # !!! THE FIRST BUILD OMITTED THIS AND EVERY EVALUATION TAB CAME UP EMPTY.
    # The panel finds a shard by trying prefixes against the manifest; with no
    # manifest there is no shard name, so every lookup returned null and all
    # eleven tabs rendered disabled -- with no error anywhere to say why.  The
    # shipped index.json has carried `shards` from the start; this one did not.
    'shards': {'form': m_form, 'dpd': m_dpd, 'lem': m_lem},
    # the panel renders one APD section per dictionary from THIS table, not
    # from a list of its own, so the two cannot drift apart again
    'apd_books': {k: BOOKS.get(k, {'name': k, 'author': '', 'lang': '?'})
                  for k in sorted(seen_ids)},
    'apd_order': [k for k in APD_ORDER if k in seen_ids]
                 + sorted(seen_ids - set(APD_ORDER)),
    'apd_zawgyi': sorted(ZAWGYI_IDS & seen_ids),
    'sources': {
        'dpd': 'Digital Pāḷi Dictionary (Bodhirasa), GoldenDict build — '
               'CC BY-NC-SA 4.0. EVALUATION ONLY; §9 excludes it as a voice.',
        'abhidhana': 'Tipiṭaka-Pāḷi-Myanmā-Abhidhāna (Ministry of Religious '
                     'Affairs, Yangon) via pm12e.csv 2020-12-09, '
                     'bksubhuti/Tipitaka-Pali-Projector. Citations as printed '
                     'plus a transcoded roman line. Permission unconfirmed (§8 Q6).',
        'peu': 'PEU StarDict 2024-02-24, encoded by Bodhirasa — the Abhidhāna\'s '
               'English rendering. Google-Translate entries flagged, never mixed.',
        'cped': 'Concise Pali-English Dictionary, A.P. Buddhadatta.',
        'ppn': 'Dictionary of Pāli Proper Names, G.P. Malalasekera — DPPN.json, '
               'digitalpalidictionary/other-dictionaries v1.0.8.',
        'nyanatiloka': 'Buddhist Dictionary, Nyanatiloka Mahāthera — PCED "N". '
                       'A doctrinal glossary, not a lexicon.',
        'vri': 'Pali-Dictionary, Vipassana Research Institute — PCED "I".',
        'pwg': 'Pali Word Grammar from the Pali Myanmar Dictionary — PCED "B", '
               'Burmese, Zawgyi→Unicode by _panel/zawgyi.py.',
        'tpm': 'Tipiṭaka Pāḷi-Myanmar Dictionary — PCED "K", Burmese, '
               'Zawgyi→Unicode. A second copy of the Abhidhāna\'s digitisation '
               'lineage: the verification witness the inventory nominated.',
        'roots': 'Pali Roots Dictionary (ဓာတ်အဘိဓာန်) — PCED "O", Burmese, '
                 'Zawgyi→Unicode. Relevant to step 4 (Saddanīti Dhātumālā).',
        'uhs': 'U Hau Sein\'s Pāḷi-Myanmar Dictionary — PCED "R", Burmese, '
               'Zawgyi→Unicode.',
    },
    'zawgyi': {
        'converter': '_panel/zawgyi.py — Rabbit ruleset, vendored, with three '
                     'corrections found by the character census (§3): the dead '
                     'JS-literal rule for U+1073/1074, the absent rules for '
                     'U+1066/1067, and the self-referential rule for U+1091.',
        'unconverted_left': dict(zg_left),
        'unconverted_note': 'kinzi marks with no consonant before them; '
                            'flagged rather than guessed (principle 2)',
    },
}, open(os.path.join(OUT, 'index.json'), 'w'), ensure_ascii=False, indent=1)
log('index.json written')
