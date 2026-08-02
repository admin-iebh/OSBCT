#!/usr/bin/env python3
"""Proximity measurement — the first item of next_session_after_step3.md.

THE QUESTION.  For a high-frequency word a click can return hundreds of gloss
rows.  Roadmap §4 forbids ranking them by guess.  The one ranking that is not a
guess is PROXIMITY: put first the gloss that occurs in the commentary/ṭīkā
paragraph which the *existing link map* already ties to the canon paragraph the
reader is standing in.  Whether that gloss is the RIGHT one is unmeasured.

Two questions, not one:

  A. COVERAGE — how often does a proximity row exist at all?  Mechanical,
     no judgement.  Measured under two models of who clicks what, because a
     uniform-random click understates a real reader: readers click words they
     do not know, and those are the rare words the commentary is most likely to
     gloss.  Model 1 = uniform over the paragraph's tokens.  Model 2 = the
     rarest token in the paragraph by corpus frequency (_vocab/freq/), an
     upper bound on "the reader clicks what puzzles them".
     Three proximity tiers: the exact linked paragraph, that paragraph ±2, and
     the same sutta inside the linked volume.

  B. PRECISION — a hand-judging sheet.  A stratified sample of (canon
     paragraph, clicked word) pairs where the word has >= 2 gloss rows AND a
     proximity row exists, with the canon sentence, the proximity row(s) and a
     sample of the rest, laid out for a human to read and rule on.

The frame is every canon volume with a forward link map (all 40) and every
gloss row in _gloss/by_volume/ (all 90 volumes) -- not the 7-volume panel
pilot, so the answer is about the corpus, not about Majjhima.

Read-only outside _panel/.
"""
import json, os, re, sys, glob, random, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
SEED = 20260802
N_JUDGE_PER_BAND = 15

PALI = set('aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁ')
PALI |= set(c.upper() for c in PALI)
APOS = {'’', "'"}
MARK = re.compile(r'([a-zāīūṁṅñṭḍṇḷ])(\d{1,2})\b')
DIGITS = re.compile(r'\d+')
clean = lambda t: DIGITS.sub(' ', MARK.sub(r'\1', t))

FOLD = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ḷ': 'l'}
fold = lambda s: ''.join(FOLD.get(c, c) for c in s.lower())


def freq_shard(w):
    """_vocab/freq/'s adaptive prefix scheme: try longest prefix file first."""
    f = fold(w)
    for k in (4, 3, 2, 1):
        p = f[:k]
        if len(p) < k:
            continue
        yield p


def tokens_with_pos(text):
    ok = PALI | {'-'} | APOS
    buf, start, prev = [], None, ''
    for i, ch in enumerate(text):
        if ch in ok:
            if ch in APOS or ch == '-':
                nxt = text[i + 1] if i + 1 < len(text) else ''
                if not (prev in PALI and nxt in PALI):
                    if buf:
                        yield ''.join(buf), start
                    buf, start, prev = [], None, ch
                    continue
            if not buf:
                start = i
            buf.append(ch)
        elif buf:
            yield ''.join(buf), start
            buf, start = [], None
        prev = ch
    if buf:
        yield ''.join(buf), start


# --- corpus frequency (for the "reader clicks the puzzling word" model) ------
print('loading corpus frequencies…', file=sys.stderr)
FREQ = {}
for f in glob.glob(os.path.join(REPO, '_vocab/freq/*.json')):
    if os.path.basename(f) == 'index.json':      # the shard manifest, not counts
        continue
    for k, v in json.load(open(f)).items():
        FREQ[k] = v[0]
print(f'  {len(FREQ):,} forms', file=sys.stderr)

# --- the glosses ------------------------------------------------------------
print('loading glosses…', file=sys.stderr)
by_form = collections.defaultdict(list)
by_para = collections.defaultdict(list)
by_vol_sutta = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(REPO, '_gloss/by_volume/*.json'))):
    if os.path.basename(f) == 'index.json':
        continue
    for r in json.load(open(f)):
        slim = {'l': r['lemma'], 'g': r['gloss'], 'v': r['vol'], 'n': r['n'],
                'pf': r['printed_first'], 's': r['sutta'], 't': r['truncated'],
                'q': r['quoted_lemma'], 'w': r['words'], 'ctx': r['context']}
        for cd in r['candidates']:
            by_form[cd].append(slim)
        if r['n'] is not None:
            by_para[(r['vol'], r['n'])].append(slim)
        by_vol_sutta[(r['vol'], r['sutta'])].append(slim)

links = {}
for f in sorted(glob.glob(os.path.join(REPO, 'site/reader/links/*.fwd.json'))):
    links[os.path.basename(f).split('.')[0]] = json.load(open(f))


def band(n):
    return '0' if n == 0 else '1' if n == 1 else '2-3' if n <= 3 \
        else '4-10' if n <= 10 else '11-50' if n <= 50 else '>50'


rng = random.Random(SEED)
c = collections.Counter()
band_pool = collections.defaultdict(list)

print('walking the canon…', file=sys.stderr)
for vol in sorted(links):
    path = os.path.join(REPO, 'site', vol + '.json')
    if not os.path.exists(path):
        continue
    for p in json.load(open(path))['paragraphs']:
        if p.get('n') is None:
            continue
        rec = links[vol].get(str(p['n']))
        if not rec:
            continue
        tgt = []
        for layer in ('commentary', 'subcommentary'):
            L = rec.get(layer)
            if L and L.get('vol') is not None and L.get('n') is not None:
                tgt.append((L['vol'], L['n']))
        if not tgt:
            continue
        toks = list(tokens_with_pos(clean(p['text'])))
        if not toks:
            continue
        c['paras'] += 1

        exact = set(tgt)
        window = {(v, n + d) for v, n in tgt for d in (-2, -1, 0, 1, 2)}
        suttas = set()
        for v, n in tgt:
            for r in by_para.get((v, n), []):
                suttas.add((v, r['s']))
                break

        def score(word):
            rows = by_form.get(word) or by_form.get(word.lower()) or []
            if not rows:
                return rows, None
            tier = None
            if any((r['v'], r['n']) in exact for r in rows):
                tier = 'exact'
            elif any((r['v'], r['n']) in window for r in rows):
                tier = 'window'
            elif any((r['v'], r['s']) in suttas for r in rows):
                tier = 'sutta'
            return rows, tier

        # model 1 — uniform click
        w1 = toks[rng.randrange(len(toks))][0]
        rows1, tier1 = score(w1)
        c['m1'] += 1
        c['m1_' + band(len(rows1))] += 1
        if rows1:
            c['m1_glossed'] += 1
            if tier1:
                c['m1_' + tier1] += 1
                c[f'm1_{tier1}_{band(len(rows1))}'] += 1

        # model 2 — the rarest token in the paragraph
        w2 = min((t for t, _ in toks), key=lambda t: FREQ.get(t, FREQ.get(t.lower(), 0)))
        rows2, tier2 = score(w2)
        c['m2'] += 1
        if rows2:
            c['m2_glossed'] += 1
            if tier2:
                c['m2_' + tier2] += 1

        # judging pool: uniform click, >=2 rows, an EXACT proximity row present
        if len(rows1) >= 2 and tier1 == 'exact':
            band_pool[band(len(rows1))].append(
                dict(vol=vol, n=p['n'], word=w1, text=p['text'],
                     sutta=p.get('sutta'), printed=p.get('printed'),
                     rows=rows1, exact=exact, window=window, suttas=suttas))

out = []
A = out.append
A('A. COVERAGE')
A(f'   frame: {c["paras"]:,} canon paragraphs that carry a forward link map')
A('')
A('   Model 1 — a uniform-random click in the paragraph')
A(f'     clicks that get any gloss at all   {c["m1_glossed"]:7,} '
  f'({100*c["m1_glossed"]/c["m1"]:5.2f}% of clicks)')
for k, label in (('exact', 'the exact linked paragraph'),
                 ('window', 'the linked paragraph ±2'),
                 ('sutta', 'the same sutta in that volume')):
    v = c['m1_' + k]
    A(f'     proximity: {label:<32} {v:6,} '
      f'({100*v/c["m1"]:5.2f}% of clicks, {100*v/c["m1_glossed"]:5.2f}% of glossed clicks)')
cum = c['m1_exact'] + c['m1_window'] + c['m1_sutta']
A(f'     any of the three tiers                          {cum:6,} '
  f'({100*cum/c["m1"]:5.2f}% of clicks, {100*cum/c["m1_glossed"]:5.2f}% of glossed clicks)')
A('')
A('     by how many gloss rows the clicked word has:')
A('       rows      clicks    exact-paragraph proximity')
for b in ('1', '2-3', '4-10', '11-50', '>50'):
    n = c['m1_' + b]
    if not n:
        continue
    A(f'       {b:>6}   {n:7,}    {c["m1_exact_"+b]:6,} ({100*c["m1_exact_"+b]/n:5.2f}%)')
A('')
A('   Model 2 — the reader clicks the RAREST word in the paragraph')
A('   (an upper bound: readers look up what puzzles them, and the commentary')
A('    glosses the unusual word far more often than the common one)')
A(f'     clicks that get any gloss at all   {c["m2_glossed"]:7,} '
  f'({100*c["m2_glossed"]/c["m2"]:5.2f}% of clicks)')
for k, label in (('exact', 'the exact linked paragraph'),
                 ('window', 'the linked paragraph ±2'),
                 ('sutta', 'the same sutta in that volume')):
    v = c['m2_' + k]
    A(f'     proximity: {label:<32} {v:6,} '
      f'({100*v/c["m2"]:5.2f}% of clicks, {100*v/max(c["m2_glossed"],1):5.2f}% of glossed clicks)')

judge = []
for b in ('2-3', '4-10', '11-50', '>50'):
    pool = band_pool[b]
    rng.shuffle(pool)
    for it in pool[:N_JUDGE_PER_BAND]:
        prox = [r for r in it['rows'] if (r['v'], r['n']) in it['exact']]
        rest = [r for r in it['rows'] if (r['v'], r['n']) not in it['exact']]
        rng.shuffle(rest)
        judge.append({'band': b, 'vol': it['vol'], 'para': it['n'],
                      'printed': it['printed'], 'sutta': it['sutta'],
                      'word': it['word'], 'n_rows': len(it['rows']),
                      'n_prox': len(prox), 'canon': it['text'],
                      'prox': prox, 'others': rest[:4],
                      'verdict': None, 'note': None})

json.dump({'seed': SEED, 'counts': dict(c), 'judge': judge},
          open(os.path.join(ROOT, 'proximity_sample.json'), 'w'),
          ensure_ascii=False, indent=1)

A('')
A(f'B. JUDGING SHEET — {len(judge)} items → _panel/proximity_sample.json')
for b in ('2-3', '4-10', '11-50', '>50'):
    A(f'   band {b:>6}: {sum(1 for j in judge if j["band"]==b)} of '
      f'{len(band_pool[b]):,} eligible')
print('\n'.join(out))
open(os.path.join(ROOT, 'proximity_report.txt'), 'w').write('\n'.join(out) + '\n')
