#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does a paragraph answer to the section name the edition prints above it?

WHY.  `19Khu02` carried **3 distinct `sutta` values over 3,660 paragraphs**, and
one of them, `Rasuttamadāyikāvimānavatthu (4)`, was spread across dozens of
sections it has nothing to do with.  So the Petavatthu's opening paragraphs
answered to a Vimānavatthu section name — reader-visible, on every page.
Full account: `claude/sections_the_edition_prints.md`.

NAMED CASES, READ OFF THE PRINTED PAGE BEFORE BEING ASSERTED, exactly as the
re-quotation cases in `check_links.py` were:

  p.143  `1. Uragavagga` / `1. Khettūpamapetavatthu` above `1. Khettūpamā
         arahanto, dāyakā kassakūpamā.`  -> ord 1034 is Khettūpamapetavatthu
  p.1    `1. Pīṭhavagga` / `1. Paṭhamapīṭhavimānavatthu` above `1. Pīṭhaṁ te
         sovaṇṇamayaṁ uḷāraṁ`            -> ord 0 is Paṭhamapīṭhavimānavatthu
  p.45   `3. Pallaṅkavimānavatthu` above `307. Pallaṅkaseṭṭhe maṇisoṇṇacitte`

AND ONE NEGATIVE, because the artifact has a shape.  The edition prints
`3. Pallaṅkavimānavatthu` — plain.  It does NOT print a parenthesised index
after the name.  So any `sutta` value ending in `(4)` is the old extraction
talking, not the edition, and none may survive.

Usage:
  python3 pipeline/check_sections.py
Exit 0 = every case holds.
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')

# volume, ordinal, the section name the edition prints, the printed page read
CASES = [
    ('19Khu02',    0, 'Paṭhamapīṭhavimānavatthu', 'p.1'),
    ('19Khu02',  291, 'Pallaṅkavimānavatthu',     'p.45'),
    ('19Khu02', 1034, 'Khettūpamapetavatthu',     'p.143'),
    # 28KhuA09, the commentary side.  Printed p.9 read: the closer
    # `Khettūpamapetavatthuvaṇṇanā niṭṭhitā.`, a rule, then the bold heading
    # `2. Sūkaramukhapetavatthuvaṇṇanā`, then `Kāyo te sabbasovaṇṇoti idaṁ
    # Satthari Rājagahaṁ upanissāya Veḷuvane ...` — which is ord 10.
    ('28KhuA09',   3, 'Khettūpamapetavatthuvaṇṇanā',  'p.5'),
    ('28KhuA09',  10, 'Sūkaramukhapetavatthuvaṇṇanā', 'p.9'),
]

ARTIFACT = re.compile(r'\(\s*\d+\s*\)\s*$')


def paras(vol):
    f = os.path.join(SITE, vol + '.json')
    d = json.load(open(f, encoding='utf-8'))
    return d.get('paragraphs') or d.get('paras') or []


def main():
    fails = []
    print('section names, against the printed page')
    seen = {}
    for vol, o, want, page in CASES:
        C = seen.get(vol) or seen.setdefault(vol, paras(vol))
        got = C[o].get('sutta') if o < len(C) else None
        if got == want:
            print('  ok    %s#%d -> %r  (%s)' % (vol, o, got, page))
        else:
            print('  FAIL  %s#%d is %r, the edition prints %r at %s'
                  % (vol, o, got, want, page))
            fails.append('%s#%d is %r, not %r' % (vol, o, got, want))

    for vol in sorted(seen):
        C = seen[vol]
        bad = sorted(set(p['sutta'] for p in C
                         if p.get('sutta') and ARTIFACT.search(p['sutta'])))
        if bad:
            print('  FAIL  %s carries %d section name(s) with a parenthesised '
                  'index, which the edition does not print: %s'
                  % (vol, len(bad), ', '.join(repr(b) for b in bad[:3])))
            fails.append('%s: %d artifact section name(s)' % (vol, len(bad)))
        else:
            print('  ok    %s: no section name carries a parenthesised index' % vol)
        n = len(set(p.get('sutta') for p in C if p.get('sutta')))
        print('        %s: %d distinct section names over %d paragraphs'
              % (vol, n, len(C)))

    if fails:
        print('\nSECTIONS FAILED:')
        for f in fails:
            print('  - %s' % f)
        sys.exit(1)
    print('\nevery named case holds')


if __name__ == '__main__':
    main()
