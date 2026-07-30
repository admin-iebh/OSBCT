#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the diacritic-insensitive search index from the CURRENT corpora.

!!! WHY THIS FILE EXISTS.  `site/index/` was built on 2026-07-23 and NO BUILDER
WAS EVER COMMITTED — so every corpus rebuilt since (the seven Vinaya Ṭīkā, the
Dīgha/Majjhima/Saṁyutta/Aṅguttara Ṭīkā, 05Kankha, 01VinA01 …) is indexed in its
OLD shape.  Measured 2026-07-30g: **65 of 118 shards disagree with their corpus
on paragraph count**, 07ViT07 holding 22 against 420 and 05Kankha 534 against
932.  Search cannot find text it has no posting for, so those volumes are
substantially unsearchable on the live site.

THE FORMAT IS REPRODUCED, NOT INVENTED.  It was read off the shipped index and
this builder is checked against a volume whose corpus has NOT changed since:
`--verify VOL` rebuilds that volume and compares the result with the shipped
shard, term for term and posting for posting.  01Vin01 is the reference.

    index/terms.compact.json  {vols:[code], layers:[folder], terms:{t:[volIdx]}}
    index/<VOL>.idx.json      {vol, source, paras:[…], inv:{t:[[paraIdx,count]]}}

The `paras` list is a 1:1 copy of the corpus paragraphs — numbered or not — with
`page` carrying the corpus's `printed`.  **`ord` is added**: the shipped format
had no way to name a paragraph except by `id`, which is NOT unique (12,110
collisions across 65 volumes, REBUILD-PLAN.md Phase 2), and a deep link into the
reader needs the ordinal.  Extra keys are ignored by `search.html`.

Usage: python3 pipeline/build_search_index.py [--verify VOL] [--write]
"""
import json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site', 'index')
FOLDER = {'canon': 'pali-unicode', 'commentary': 'atthakatha-unicode',
          'subcommentary': 'tika-unicode'}

# THE FOLD IS THE POINT OF THE INDEX — `nibbana` must find *nibbāna*.  Derived
# from the shipped index's own keys (`taṁ`->`tam`, `katamaṁ`->`katamam`,
# `vā`->`va`) and then checked against it wholesale by `--verify`.
_MAP = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṇ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ḷ': 'l', 'ḹ': 'l', 'ṛ': 'r', 'ś': 's',
        'ṣ': 's', 'ḥ': 'h', 'ẽ': 'e', 'õ': 'o'}


def fold(s):
    s = unicodedata.normalize('NFC', s).lower()
    return ''.join(_MAP.get(c, c) for c in s)


_TOK = re.compile(r'[^a-zāīūṁṃṅñṇṭḍḷ]+', re.I)


def terms_of(text):
    """Every folded term in one paragraph, with its count, in first-seen order."""
    out = {}
    for w in _TOK.split(fold(text or '')):
        if w:
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
