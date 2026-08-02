#!/usr/bin/env python3
"""Why is proximity coverage 4.8%?  Diagnose before concluding.

Four candidate explanations, each testable:
  1. gloss rows carry no paragraph number (n is null) and so can never match;
  2. the linked commentary paragraph simply has no gloss rows in it;
  3. the commentary glosses only a few words per paragraph, so a click usually
     lands on a word it never discusses -- a property of the EDITION, not a bug;
  4. the link map's single paragraph is too narrow: the commentary on one canon
     paragraph spills over several, or the numbering does not align.

Also measures two widenings that are still not guesses: a +-window around the
linked paragraph, and same-sutta-in-the-linked-volume.
"""
import json, os, re, sys, glob, random, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
SEED = 20260802
rng = random.Random(SEED)

PALI = set('aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁ')
PALI |= set(c.upper() for c in PALI)
APOS = {'’', "'"}
MARK = re.compile(r'([a-zāīūṁṅñṭḍṇḷ])(\d{1,2})\b')
DIGITS = re.compile(r'\d+')
clean = lambda t: DIGITS.sub(' ', MARK.sub(r'\1', t))


def tokens(text):
    ok = PALI | {'-'} | APOS
    buf, prev = [], ''
    for i, ch in enumerate(text):
        if ch in ok:
            if ch in APOS or ch == '-':
                nxt = text[i + 1] if i + 1 < len(text) else ''
                if not (prev in PALI and nxt in PALI):
                    if buf:
                        yield ''.join(buf)
                    buf, prev = [], ch
                    continue
            buf.append(ch)
        elif buf:
            yield ''.join(buf); buf = []
        prev = ch
    if buf:
        yield ''.join(buf)


print('loading glosses…', file=sys.stderr)
by_form = collections.defaultdict(list)
by_para = collections.defaultdict(list)          # (vol, n) -> rows
by_vol_sutta = collections.defaultdict(list)     # (vol, sutta) -> rows
n_null = n_tot = 0
for f in sorted(glob.glob(os.path.join(REPO, '_gloss/by_volume/*.json'))):
    if os.path.basename(f) == 'index.json':
        continue
    for r in json.load(open(f)):
        n_tot += 1
        if r['n'] is None:
            n_null += 1
        slim = {'l': r['lemma'], 'g': r['gloss'], 'v': r['vol'], 'n': r['n'],
                's': r['sutta'], 'cands': r['candidates']}
        for c in r['candidates']:
            by_form[c].append(slim)
        if r['n'] is not None:
            by_para[(r['vol'], r['n'])].append(slim)
        by_vol_sutta[(r['vol'], r['sutta'])].append(slim)

print(f'1. gloss rows with NO paragraph number: {n_null:,} of {n_tot:,} '
      f'({100*n_null/n_tot:.2f}%)')

links = {}
for f in sorted(glob.glob(os.path.join(REPO, 'site/reader/links/*.fwd.json'))):
    links[os.path.basename(f).split('.')[0]] = json.load(open(f))

c = collections.Counter()
per_para_rows = []
per_para_forms = []
for vol in sorted(links):
    path = os.path.join(REPO, 'site', vol + '.json')
    if not os.path.exists(path):
        continue
    doc = json.load(open(path))
    for p in doc['paragraphs']:
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
        c['paras'] += 1
        rows_here = [r for k in tgt for r in by_para.get(k, [])]
        if rows_here:
            c['linked_para_has_rows'] += 1
        per_para_rows.append(len(rows_here))
        # 3. how much of the paragraph does the commentary actually gloss?
        toks = set(tokens(clean(p['text'])))
        toks_l = {t.lower() for t in toks}
        glossed = set()
        for r in rows_here:
            for cand in r['cands']:
                if cand in toks or cand.lower() in toks_l:
                    glossed.add(cand.lower())
        per_para_forms.append((len(glossed), len(toks)))
        # 4. widenings
        win = []
        sut = []
        for v, n in tgt:
            for d in (-2, -1, 0, 1, 2):
                win.extend(by_para.get((v, n + d), []))
        for layer in ('commentary', 'subcommentary'):
            L = rec.get(layer)
            if L and L.get('vol'):
                # sutta name of the linked paragraph, via its own rows
                for r in by_para.get((L['vol'], L.get('n')), []):
                    sut.extend(by_vol_sutta.get((L['vol'], r['s']), []))
                    break
        w = rng.choice(list(toks)) if toks else None
        if not w:
            continue
        allrows = by_form.get(w) or by_form.get(w.lower()) or []
        if not allrows:
            continue
        c['click_glossed'] += 1
        tgtset = set(tgt)
        if any((r['v'], r['n']) in tgtset for r in allrows):
            c['hit_exact'] += 1
        winset = {(r['v'], r['n']) for r in win}
        if any((r['v'], r['n']) in winset for r in allrows):
            c['hit_window'] += 1
        sutset = {(r['v'], r['s']) for r in sut}
        if any((r['v'], r['s']) in sutset for r in allrows):
            c['hit_sutta'] += 1

n = c['paras']
print(f'\n2. linked commentary/ṭīkā paragraph contains at least one gloss row: '
      f'{c["linked_para_has_rows"]:,} of {n:,} ({100*c["linked_para_has_rows"]/n:.2f}%)')
per_para_rows.sort()
print(f'   gloss rows in the linked paragraph(s): median {per_para_rows[len(per_para_rows)//2]}, '
      f'mean {sum(per_para_rows)/len(per_para_rows):.2f}, '
      f'90th pct {per_para_rows[int(.9*len(per_para_rows))]}')

gl = sum(a for a, b in per_para_forms)
tk = sum(b for a, b in per_para_forms)
print(f'\n3. of the canon words in a paragraph, the linked commentary glosses '
      f'{gl:,} of {tk:,} ({100*gl/tk:.2f}%)')

g = c['click_glossed']
print(f'\n4. clicks that get any gloss at all: {g:,}')
for k, label in (('hit_exact', 'exact linked paragraph'),
                 ('hit_window', 'linked paragraph ±2'),
                 ('hit_sutta', 'same sutta in the linked volume')):
    print(f'   {label:<34} {c[k]:6,} ({100*c[k]/g:5.2f}%)')
