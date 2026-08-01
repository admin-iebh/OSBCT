#!/usr/bin/env python3
"""Final consolidated figures + sharded freq output. Run after tokenise.py+verify.py."""
import json, os, collections, pickle, random, math

ROOT = os.path.dirname(os.path.abspath(__file__))
S = pickle.load(open(os.path.join(ROOT, 'dpd_sets.pkl'), 'rb'))
FORMS = S['A'] | S['B'] | S['E']
DEC = S['D']
SHORT = {'ā': 'a', 'ī': 'i', 'ū': 'u'}
norm = lambda w: w.replace('ṁ', 'ṃ')


def variants(x):
    if x and x[-1] in SHORT:
        yield x[:-1] + SHORT[x[-1]]
    if x and x[-1] in 'nmñṅṇ':
        yield x[:-1] + 'ṃ'
    if '’' in x or "'" in x:
        y = x.replace('’', '').replace("'", '')
        yield y
        for p in x.replace("'", '’').split('’'):
            if p:
                yield p


def tier(w):
    x = norm(w)
    if x in FORMS:
        return 1
    vs = list(variants(x))
    if any(v in FORMS for v in vs):
        return 2
    if x in DEC:
        return 3
    if any(v in DEC for v in vs):
        return 4
    return 5


TIERS = {1: 'exact DPD inflected form',
         2: 'after a cheap normalisation (verse -ā/-ī/-ū, final -n for -ṁ, elision mark)',
         3: 'DPD can deconstruct it (sandhi / compound)',
         4: 'deconstructable after normalisation',
         5: 'unresolved by any DPD route'}

FOLD = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ḷ': 'l'}
fold = lambda s: ''.join(FOLD.get(c, c) for c in s.lower())

L = json.load(open(os.path.join(ROOT, 'stats_raw.json')))
res = {'dpd_release': 'v0.4.20260728', 'dpd_licence': 'CC BY-NC-SA 4.0',
       'dpd_forms_in_membership_set': len(FORMS),
       'dpd_deconstructable_keys': len(DEC)}


def block(tag, path):
    ctr = collections.Counter(json.load(open(os.path.join(ROOT, path))))
    N = sum(ctr.values()); V = len(ctr)
    hap = sum(1 for v in ctr.values() if v == 1)
    tt = collections.Counter(); ty = collections.Counter()
    for w, n in ctr.items():
        k = tier(w); tt[k] += n; ty[k] += 1
    ranked = sorted(ctr.values(), reverse=True)
    cov = {}
    cum = 0; i = 0
    for m in (1000, 5000, 10000, 25000, 50000):
        while i < min(m, len(ranked)):
            cum += ranked[i]; i += 1
        cov[m] = cum / N
    d = {'tokens': N, 'types': V, 'hapax': hap,
         'hapax_share_types': hap / V, 'hapax_share_tokens': hap / N,
         'coverage': cov,
         'tier_tokens': {k: tt[k] / N for k in TIERS},
         'tier_types': {k: ty[k] / V for k in TIERS},
         'tier_token_counts': {k: tt[k] for k in TIERS},
         'tier_type_counts': {k: ty[k] for k in TIERS}}
    res[tag] = d
    print(f'\n### {tag}   tokens {N:,}   types {V:,}   hapax {hap:,} '
          f'({hap/V:.1%} of types, {hap/N:.2%} of tokens)')
    print('    top-N type coverage of running tokens: ' +
          '  '.join(f'{m//1000}k={cov[m]:.1%}' for m in cov))
    c = 0
    for k in sorted(TIERS):
        c += tt[k]
        print(f'    {k}. {TIERS[k]:<70} types {ty[k]:>8,}  tokens {tt[k]:>9,} '
              f'= {tt[k]/N:6.2%}   cum {c/N:6.2%}')
    return ctr


print('=== OSBCT vocabulary measurement — final figures ===')
main_split = block('corpus_hyphen_split', 'freq_split.json')
main_join = block('corpus_hyphen_joined', 'freq_join.json')
for layer in ('canon', 'commentary', 'subcommentary'):
    block(layer, f'freq_layer_{layer}_split.json')
block('headings', 'freq_headings.json')
block('hidden_paragraphs', 'freq_hidden.json')

# ---- sharded frequency table -------------------------------------------------
lay = {l: collections.Counter(json.load(open(os.path.join(ROOT, f'freq_layer_{l}_split.json'))))
       for l in ('canon', 'commentary', 'subcommentary')}
# Adaptive prefix length: deepen any shard over TARGET bytes.  The panel loads
# exactly one shard per clicked word, and the site already has a mobile
# performance item open -- a 2.3 MB 'sa' shard would be a new one.
TARGET = 200_000
rows = {w: [n, lay['canon'].get(w, 0), lay['commentary'].get(w, 0),
            lay['subcommentary'].get(w, 0), tier(w)]
        for w, n in main_split.items()}
safe = lambda s: ''.join(c if c.isalpha() else '_' for c in s)


def split(words, depth):
    """Return {shard_key: {form: row}} with each shard under TARGET where possible."""
    buckets = collections.defaultdict(list)
    for w in words:
        buckets[safe(fold(w)[:depth]).ljust(depth, '_')].append(w)
    out = {}
    for k, ws in buckets.items():
        size = sum(len(w.encode()) + 26 for w in ws)
        if size > TARGET and depth < 6 and len(ws) > 1:
            out.update(split(ws, depth + 1))
        else:
            out[k] = {w: rows[w] for w in ws}
    return out


shards = split(list(main_split), 2)
out = os.path.join(ROOT, 'freq')
os.makedirs(out, exist_ok=True)
manifest = {'built_from': 'site/<VOL>.json, 118 volumes',
            'tokeniser': 'tokenise.py (hyphen=split); verified against verify.py',
            'fields': ['count_total', 'count_canon', 'count_commentary',
                       'count_subcommentary', 'dpd_tier'],
            'dpd_tier_meaning': TIERS,
            'dpd_release': 'v0.4.20260728 — used as a MEMBERSHIP TEST ONLY; '
                           'no DPD content is included in this file',
            'shard_key': "adaptive: the shortest prefix of the site's fold() of "
                         "the form, padded with '_' to that length, that names a "
                         "shard in this manifest. Try depth 2 upward.",
            'totals': {'tokens': sum(main_split.values()), 'types': len(main_split)},
            'shards': {}}
for k, v in sorted(shards.items()):
    p = os.path.join(out, k + '.json')
    json.dump(v, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
    manifest['shards'][k] = {'types': len(v), 'bytes': os.path.getsize(p)}
json.dump(manifest, open(os.path.join(out, 'index.json'), 'w'),
          ensure_ascii=False, indent=1)
sz = sum(s['bytes'] for s in manifest['shards'].values())
print(f'\n### freq/ : {len(manifest["shards"])} shards, {sz/1e6:.1f} MB total, '
      f'largest {max(s["bytes"] for s in manifest["shards"].values())/1e6:.2f} MB, '
      f'median {sorted(s["bytes"] for s in manifest["shards"].values())[len(manifest["shards"])//2]/1024:.0f} kB')
res['freq_shards'] = {'n': len(manifest['shards']), 'total_bytes': sz}
json.dump(res, open(os.path.join(ROOT, 'final.json'), 'w'), ensure_ascii=False, indent=1)
print('\nwritten final.json + freq/')
