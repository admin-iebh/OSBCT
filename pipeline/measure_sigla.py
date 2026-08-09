#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEASURE the unnumbered-siglum notes — no repair.

WHY.  Resolving E021 (2026-08-09) exposed that the apparatus extraction
mishandles notes keyed by SYMBOLS rather than digits.  Two witnessed cases in
10Ma02 alone: the `+` note on printed p.247 is absent from the live apparatus
(¶296 / ord 295 has no appk entry at all), and the `( )` note on p.246 was
glued onto the tail of numbered note 2 under ord 294.  Nobody knows the
corpus-wide extent.  This script counts it.

WHAT IS COUNTED.  In every volume's paragraph text: the marks `( )`,
standalone `+`, standalone `*`, and standalone `x` (the E021 class).  For each
paragraph carrying a mark, the ord-keyed apparatus (`<vol>.appk.json`) says
whether ANY entry exists there.  Classification is deliberately coarse:

    no-entry   — the paragraph has a symbol mark and NO apparatus entry at
                 all.  If the edition keys a foot-note to that mark, the note
                 is unreachable: the witnessed ¶296 shape.
    entry      — an apparatus entry exists.  Whether the symbol's own note is
                 inside it, standalone or glued, is NOT decided here — that
                 needs the printed page per site (the ¶295 gluing was only
                 established that way).  Flag, don't guess.

SELFTEST.  The two witnessed 10Ma02 cases must come out as witnessed, or this
instrument is reporting its own mistakes as the corpus's (the check_fn_markers
lesson).  Fatal if they do not.

Usage:  python3 pipeline/measure_sigla.py
Output: table on stdout; _review/sigla_report.json with every site.
"""
import json, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

LETTER = 'A-Za-zāīūṁṃṅñṭḍṇḷĀĪŪṀṄÑṬḌṆḶ'
MARKS = {
    'paren': re.compile(r'\( \)'),
    'plus':  re.compile(r'(?<!\S)\+(?!\S)'),
    'star':  re.compile(r'(?<!\S)\*(?=\s)'),
    'x':     re.compile(r'(?<![%s])x(?![%s])' % (LETTER, LETTER)),
}


def main():
    vols = sorted(f[:-5] for f in os.listdir('site') if f.endswith('.json'))
    rows, per = [], collections.Counter()
    for vol in vols:
        try:
            d = json.load(open('site/%s.json' % vol, encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(d, dict) or 'paragraphs' not in d:
            continue
        ap = 'site/reader/apparatus/%s.appk.json' % vol
        appk = json.load(open(ap, encoding='utf-8')) if os.path.exists(ap) else {}
        for i, p in enumerate(d['paragraphs']):
            t = p.get('text') or ''
            found = {c: [m.start() for m in rx.finditer(t)]
                     for c, rx in MARKS.items()}
            found = {c: v for c, v in found.items() if v}
            if not found:
                continue
            fate = 'entry' if str(i) in appk else 'no-entry'
            for c, offs in found.items():
                per[(c, fate)] += len(offs)
                per[(c, 'paragraphs')] += 1
            rows.append({'vol': vol, 'ord': i, 'n': p.get('n'), 'fate': fate,
                         'marks': {c: offs for c, offs in found.items()},
                         'peek': t[max(0, min(v[0] for v in found.values()) - 30):
                                   min(v[0] for v in found.values()) + 40]})

    # ---- selftest: the two witnessed cases, exactly as witnessed ----
    w = {(r['vol'], r['ord']): r for r in rows}
    a = w.get(('10Ma02', 295))
    assert a and a['fate'] == 'no-entry' and 'plus' in a['marks'] \
        and 'x' in a['marks'], 'SELFTEST: 10Ma02 ord 295 (+, x, no entry) not seen: %r' % a
    b = w.get(('10Ma02', 294))
    assert b and b['fate'] == 'entry' and 'paren' in b['marks'], \
        'SELFTEST: 10Ma02 ord 294 (( ), entry present) not seen: %r' % b
    print('selftest ok: both witnessed 10Ma02 cases reported as witnessed\n')

    print('%-6s %10s %10s %12s' % ('class', 'marks', 'no-entry', 'entry'))
    for c in MARKS:
        ne, en = per[(c, 'no-entry')], per[(c, 'entry')]
        print('%-6s %10d %10d %12d' % (c, ne + en, ne, en))
    nv = len({r['vol'] for r in rows})
    print('\n%d marked paragraphs in %d volumes; %d with no apparatus entry'
          % (len(rows), nv, sum(1 for r in rows if r['fate'] == 'no-entry')))
    os.makedirs('_review', exist_ok=True)
    json.dump(rows, open('_review/sigla_report.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('detail: _review/sigla_report.json')


if __name__ == '__main__':
    main()
