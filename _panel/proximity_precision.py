#!/usr/bin/env python3
"""A mechanical proxy for "is this proximity row really about this paragraph?",
calibrated against the 60 hand verdicts, then run over the whole corpus.

THE PROXY.  A gloss row's lemma is the phrase the commentary printed in bold —
the words it is about.  If the link is right, that phrase is IN the canon
paragraph.  So: fold diacritics, drop each word's final vowel (the commentary
quotes with -ti sandhi: `akusītavuttī` for the canon's `akusītavutti`), and ask
whether every word of the lemma occurs in the paragraph.  Cheap, and it needs
no judgement.

It is only worth quoting if it agrees with a human.  So it is scored first
against proximity_verdicts.json (A/B = the row belongs here, C = it does not),
and the agreement is printed before any corpus number.
"""
import json, os, re, sys, glob, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)

FOLD = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ḷ': 'l'}
PALI = set('aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁ')
PALI |= set(c.upper() for c in PALI)
APOS = {'’', "'"}
MARK = re.compile(r'([a-zāīūṁṅñṭḍṇḷ])(\d{1,2})\b')
DIGITS = re.compile(r'\d+')
clean = lambda t: DIGITS.sub(' ', MARK.sub(r'\1', t))
fold = lambda s: ''.join(FOLD.get(c, c) for c in s.lower())
VOWELS = set('aiueo')


def key(w):
    """Normalise a word to what survives quotation.

    The commentary prints its lemma with the -ti quotation sandhi applied, so
    the canon's `khayaṁ` appears as `khayan` and `piyaṁ` as `piyan`; the two
    editions also differ over gemination (`kammapattā` / `kammappattā`).  So:
    fold diacritics, collapse doubled letters, drop a trailing nasal, drop a
    trailing vowel.  What is left is the stem, which is what has to match.
    """
    f = fold(w)
    f = re.sub(r'(.)\1+', r'\1', f)
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


def pool_of(para_text):
    """The paragraph's normalised stems — built once per paragraph, not once
    per row (the first version rebuilt it inside belongs() and the corpus pass
    did not finish)."""
    pool = set()
    for w in words(clean(para_text)):
        pool.add(key(w))
        for part in w.split('-'):
            pool.add(key(part))
    return pool


def belongs_pool(lemma, pool):
    ws = [w for w in words(lemma) if len(w) > 1]
    return bool(ws) and all(key(w) in pool for w in ws)


def belongs(lemma, para_text):
    """Does every word of the commentary's bold lemma occur in the paragraph?"""
    return belongs_pool(lemma, pool_of(para_text))


# ---- calibration against the hand verdicts ---------------------------------
# Everything below is the script; the helpers above are imported by
# proximity_variant.py, so it must not run on import.
if __name__ == '__main__':
    samp = json.load(open(os.path.join(ROOT, 'proximity_sample.json')))
    hand = json.load(open(os.path.join(ROOT, 'proximity_verdicts.json')))['verdicts']
    agree = collections.Counter()
    disagree = []
    for i, j in enumerate(samp['judge']):
        v = hand.get(str(i))
        if not v:
            continue
        human = v[0]
        # the proxy fires if ANY proximity row's lemma is in the paragraph
        proxy = any(belongs(r['l'], j['canon']) for r in j['prox'])
        # the proxy's target is A -- "this row's phrase is IN this paragraph".
        # B is by definition a row whose phrase is NOT in the paragraph (a parallel
        # or neighbouring one), so B belongs on the negative side of the proxy.
        human_pos = human == 'A'
        agree[(human, proxy)] += 1
        if human_pos != proxy:
            disagree.append((i, human, proxy, j['word'],
                             j['prox'][0]['l'] if j['prox'] else ''))

    tp = sum(n for (h, p), n in agree.items() if h == 'A' and p)
    fn = sum(n for (h, p), n in agree.items() if h == 'A' and not p)
    fp = sum(n for (h, p), n in agree.items() if h != 'A' and p)
    tn = sum(n for (h, p), n in agree.items() if h != 'A' and not p)
    tot = tp + fn + fp + tn
    nA = sum(n for (h, _), n in agree.items() if h == 'A')
    nB = sum(n for (h, _), n in agree.items() if h == 'B')
    nC = sum(n for (h, _), n in agree.items() if h == 'C')
    print('CALIBRATION of the proxy against the hand verdicts')
    print(f'  hand: A {nA}  B {nB}  C {nC}   (target of the proxy is A)')
    print(f'                        proxy: in paragraph   proxy: not')
    print(f'  hand A       ({nA:2})            {tp:4}              {fn:4}')
    print(f'  hand B or C  ({nB+nC:2})            {fp:4}              {tn:4}')
    print(f'  agreement: {100*(tp+tn)/tot:.1f}%   '
          f'precision {100*tp/max(tp+fp,1):.1f}%   recall {100*tp/max(tp+fn,1):.1f}%')
    print()
    for i, h, p, w, l in disagree:
        print(f'  #{i:<3} human {h}  proxy {"belongs" if p else "not"}  '
              f'{w}  ← lemma {l[:60]!r}')
    print()

    if len(sys.argv) > 1 and sys.argv[1] == '--calibrate-only':
        sys.exit(0)

    # ---- corpus-wide -----------------------------------------------------------
    print('loading glosses…', file=sys.stderr)
    PARA_ROWS = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(REPO, '_gloss/by_volume/*.json'))):
        if os.path.basename(f) == 'index.json':
            continue
        for r in json.load(open(f)):
            if r['n'] is not None:
                PARA_ROWS[(r['vol'], r['n'])].append({'l': r['lemma']})

    links = {}
    for f in sorted(glob.glob(os.path.join(REPO, 'site/reader/links/*.fwd.json'))):
        links[os.path.basename(f).split('.')[0]] = json.load(open(f))

    GROUP = lambda v: ('Vinaya' if v[2:5] == 'Vin' else
                       'Dīgha' if v[2:4] == 'Di' else
                       'Majjhima' if v[2:4] == 'Ma' else
                       'Saṁyutta' if v[2:5] == 'Sam' else
                       'Aṅguttara' if v[2:4] == 'An' else
                       'Khuddaka' if v[2:5] == 'Khu' else
                       'Abhidhamma' if v[2:6] == 'Abhi' else 'other')

    per = collections.defaultdict(lambda: [0, 0])       # group -> [rows, belongs]
    paras = collections.defaultdict(lambda: [0, 0])     # group -> [paras, any belongs]
    print('walking the canon…', file=sys.stderr)
    for vol in sorted(links):
        path = os.path.join(REPO, 'site', vol + '.json')
        if not os.path.exists(path):
            continue
        g = GROUP(vol)
        for p in json.load(open(path))['paragraphs']:
            if p.get('n') is None:
                continue
            rec = links[vol].get(str(p['n']))
            if not rec:
                continue
            tgt = set()
            for layer in ('commentary', 'subcommentary'):
                L = rec.get(layer)
                if L and L.get('vol') is not None and L.get('n') is not None:
                    tgt.add((L['vol'], L['n']))
            if not tgt:
                continue
            # the rows sitting in the linked paragraph(s)
            rows = []
            for k in tgt:
                rows.extend(PARA_ROWS.get(k, []))
            if not rows:
                continue
            paras[g][0] += 1
            ok_any = False
            pool = pool_of(p['text'])
            for r in rows:
                per[g][0] += 1
                if belongs_pool(r['l'], pool):
                    per[g][1] += 1
                    ok_any = True
            if ok_any:
                paras[g][1] += 1

    print('CORPUS-WIDE — of every gloss row sitting in the linked paragraph,')
    print('how many have their bold lemma actually present in the canon paragraph')
    print()
    print(f'  {"group":<12} {"rows":>9} {"lemma present":>15}')
    T = [0, 0]
    for g in ('Vinaya', 'Dīgha', 'Majjhima', 'Saṁyutta', 'Aṅguttara', 'Khuddaka',
              'Abhidhamma'):
        n, ok = per[g]
        if not n:
            continue
        T[0] += n; T[1] += ok
        print(f'  {g:<12} {n:9,} {ok:9,} ({100*ok/n:5.1f}%)')
    print(f'  {"ALL":<12} {T[0]:9,} {T[1]:9,} ({100*T[1]/T[0]:5.1f}%)')
