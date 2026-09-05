#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the search index from the CURRENT corpora — EXACT keys since
2026-09-05.

!!! WHY THIS FILE EXISTS.  `site/index/` was built on 2026-07-23 and NO BUILDER
WAS EVER COMMITTED — so every corpus rebuilt since (the seven Vinaya Ṭīkā, the
Dīgha/Majjhima/Saṁyutta/Aṅguttara Ṭīkā, 05Kankha, 01VinA01 …) is indexed in its
OLD shape.  Measured 2026-07-30g: **65 of 118 shards disagree with their corpus
on paragraph count**, 07ViT07 holding 22 against 420 and 05Kankha 534 against
932.  Search cannot find text it has no posting for, so those volumes were
substantially unsearchable on the live site.

!!! THE KEYS ARE EXACT NOW, NOT FOLDED (2026-09-05, reader: "in Pāḷi `tassa`
and `tassā` are different words").  Until this date every key was folded —
`tassā` -> `tassa` — so a search for either reported the occurrences of both,
36,644 against the 4,322 that are actually `tassā`.  A key is now the token as
the edition prints it: NFC, lower-cased, and the modern ṃ written as the
edition's ṁ (the corpus carries ṁ only; the reader's niggahita toggle is
display-only).  Nothing else is changed.  Measured over the corpus: 682,010
exact keys against 643,958 folded; 34,134 folded keys (5.3%) were merging two
or more printed forms.  Diacritic folding is still offered — as a switch in the
UI, resolved on the client from these keys (`site/index/tp/`, built from the
shards by `build_term_postings.py`) — never as the stored form.
`--verify VOL` against a shard built before this date will therefore report
`DIFFERS` on the term set: that is the change, not a fault.

    index/terms.compact.json  {vols:[code], layers:[folder], terms:{t:[volIdx]}}
    index/<VOL>.idx.json      {vol, source, paras:[…], inv:{t:[[paraIdx,count]]}}

The `paras` list is a 1:1 copy of the corpus paragraphs — numbered or not — with
`page` carrying the corpus's `printed`.  **`ord` is added**: the shipped format
had no way to name a paragraph except by `id`, which is NOT unique (12,110
collisions across 65 volumes, REBUILD-PLAN.md Phase 2), and a deep link into the
reader needs the ordinal.  Extra keys are ignored by `search.html`.

These per-volume shards are no longer what the pages fetch for a search
(2026-09-05: `tp/` postings shards and `tx/` text chunks are — see
`build_term_postings.py`).  They remain the legacy fallback for an unpacked
deposit without `tp/`, and the gates' ground truth.

Usage: python3 pipeline/build_search_index.py [--verify VOL] [--write]
"""
import json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site', 'index')
FOLDER = {'canon': 'pali-unicode', 'commentary': 'atthakatha-unicode',
          'subcommentary': 'tika-unicode'}

# THE KEY IS THE PRINTED TOKEN.  `canon()` is the whole normalisation: NFC,
# lower case, ṃ -> ṁ.  The character census over all 118 volumes (2026-09-05)
# finds exactly a–z plus ā ī ū ṁ ṅ ñ ṇ ṭ ḍ ḷ inside words, and nothing else;
# `build()` asserts that again on every run so a stray glyph cannot enter the
# index unnoticed.
PALI = set('abcdefghijklmnopqrstuvwxyzāīūṁṅñṇṭḍḷ')


def canon(s):
    return unicodedata.normalize('NFC', s or '').lower().replace('ṃ', 'ṁ')


# kept for the fold switch's consumers and for `build_term_postings.py`, which
# names its shards by the FOLDED prefix so a folded query can find them
_MAP = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṇ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ḷ': 'l'}


def fold(s):
    return ''.join(_MAP.get(c, c) for c in canon(s))


_TOK = re.compile(r'[^a-zāīūṁṃṅñṇṭḍḷ]+', re.I)


def terms_of(text):
    """Every exact term in one paragraph, with its count, in first-seen order."""
    out = {}
    for w in _TOK.split(canon(text)):
        if w:
            bad = set(w) - PALI
            if bad:
                raise SystemExit('REFUSING: token %r carries %r outside the Pāḷi '
                                 'alphabet' % (w, sorted(bad)))
            out[w] = out.get(w, 0) + 1
    return out


def volumes():
    man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'),
                         encoding='utf-8'))['volumes']
    return sorted(man), man


def build(vol, man):
    P = json.load(open(os.path.join(ROOT, 'site', vol + '.json'),
                       encoding='utf-8'))['paragraphs']
    folder = FOLDER.get(man[vol]['layer'], 'pali-unicode')
    paras, inv = [], {}
    for i, p in enumerate(P):
        paras.append({'id': p.get('id'), 'n': p.get('n'), 'page': p.get('printed'),
                      'sutta': p.get('sutta'), 'book': p.get('book'),
                      'vagga': p.get('vagga'), 'peyyala': bool(p.get('peyyala')),
                      'text': p.get('text') or '', 'ord': i})
        for t, c in terms_of(p.get('text')).items():
            inv.setdefault(t, []).append([i, c])
    return {'vol': vol, 'source': '%s/%s.pdf' % (folder, vol),
            'paras': paras, 'inv': inv}, folder


def verify(vol, man):
    got, _ = build(vol, man)
    ref = json.load(open(os.path.join(OUT, vol + '.idx.json'), encoding='utf-8'))
    bad = 0
    if len(got['paras']) != len(ref['paras']):
        print('  paras %d against shipped %d — this volume has been rebuilt '
              'since the index was made; pick an unchanged one'
              % (len(got['paras']), len(ref['paras'])))
        return False
    if got['source'] != ref['source']:
        print('  source %r against %r' % (got['source'], ref['source'])); bad += 1
    a, b = set(got['inv']), set(ref['inv'])
    if a != b:
        print('  terms: %d built, %d shipped, %d only-built %s, %d only-shipped %s'
              % (len(a), len(b), len(a - b), sorted(a - b)[:6],
                 len(b - a), sorted(b - a)[:6]))
        bad += 1
    for t in sorted(a & b):
        if got['inv'][t] != ref['inv'][t]:
            print('  postings differ for %r: %r vs %r'
                  % (t, got['inv'][t][:4], ref['inv'][t][:4])); bad += 1
            if bad > 4:
                break
    print('  %s: %d paragraphs, %d terms — %s'
          % (vol, len(got['paras']), len(a), 'IDENTICAL' if not bad else 'DIFFERS'))
    return not bad


def main():
    vols, man = volumes()
    if '--verify' in sys.argv:
        v = sys.argv[sys.argv.index('--verify') + 1]
        sys.exit(0 if verify(v, man) else 1)
    write = '--write' in sys.argv
    # THE WHOLE INDEX DOES NOT FIT IN ONE CALL through the device bridge (45 s),
    # and a run killed mid-`json.dump` leaves a TRUNCATED shard that parses as
    # nothing.  So shards are written per named volume and `--terms` rebuilds
    # the compact term map afterwards FROM THE SHARDS ON DISK — which also
    # means the map can never describe shards that were not written.
    if '--terms' in sys.argv:
        terms, layers = {}, []
        for vi, vol in enumerate(vols):
            sh = json.load(open(os.path.join(OUT, vol + '.idx.json'),
                                encoding='utf-8'))
            layers.append(FOLDER.get(man[vol]['layer'], 'pali-unicode'))
            for t in sh['inv']:
                terms.setdefault(t, []).append(vi)
        comp = {'vols': vols, 'layers': layers, 'terms': terms}
        print('%d volumes, %d distinct terms' % (len(vols), len(terms)))
        if write:
            json.dump(comp, open(os.path.join(OUT, 'terms.compact.json'), 'w'),
                      ensure_ascii=False)
            print('wrote terms.compact.json')
        return
    named = [a for a in sys.argv[1:] if not a.startswith('--')]
    for vol in (named or vols):
        sh, folder = build(vol, man)
        if write:
            tmp = os.path.join(OUT, vol + '.idx.json.tmp')
            json.dump(sh, open(tmp, 'w'), ensure_ascii=False)
            os.replace(tmp, os.path.join(OUT, vol + '.idx.json'))
        print('  %-10s %5d ¶  %6d terms%s'
              % (vol, len(sh['paras']), len(sh['inv']), '  wrote' if write else ''))
    if not write:
        print('DRY RUN — pass --write')


if __name__ == '__main__':
    main()
