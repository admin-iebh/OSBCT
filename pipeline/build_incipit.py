#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the per-volume incipit side-map: `site/reader/incipit/<VOL>.json`.

The edition prints the homage "Namo tassa Bhagavato Arahato Sammāsambuddhassa."
once at the head of EVERY book, as a centred display line — not as body text.
Two things were wrong across the corpus:

  * the reader emitted it only for the first book of a physical volume, from a
    hardcoded lowercase string (so the wording could not follow the page: the
    Suttanipāta prints "Bhagavatā" where the other books print "Bhagavato"); and
  * in nine volumes the extractor had swallowed it into the following
    paragraph's text, so it rendered as ordinary prose AND, where the reader's
    built-in copy also fired, twice over.

This builder writes `{ord: "<printed text>"}` per volume.  The reader renders
that as `.incipit` above the paragraph and strips the same line off the head of
the paragraph body, so an embedded copy is displayed once, in the right role,
with the wording the page actually uses.  The corpus is never modified.

A dedicated side-map (rather than a `sections/` entry) is deliberate: a volume
that gains a `sections/` file switches the reader's whole heading strategy to
`secmap`, so a one-line sections file would silently drop every inline heading
that volume currently draws from its `headings` array.

Usage: python3 pipeline/build_incipit.py [--write] [--vol V ...]
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOMAGE = re.compile(r'Namo\s+tassa\s+\S+\s+[Aa]rahato\s+Sammāsambuddhassa\.?')

# Books whose homage the extraction dropped entirely, so it cannot be found in
# any paragraph: {vol: {ord: pdf page index that opens the book}}.
BOOK_STARTS = {'18Khu01': {0: 25, 89: 37, 513: 101, 593: 219, 705: 303}}


def pdf_path(vol):
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = f'{ROOT}/{d}/{vol}.pdf'
        if os.path.exists(p): return p
    raise SystemExit(f'no PDF for {vol}')


def pdf_pages(vol):
    return subprocess.run(['pdftotext', '-layout', pdf_path(vol), '-'],
                          capture_output=True, text=True).stdout.split('\f')


def printed_forms(pages):
    """Homage occurrences the volume prints AS A DISPLAY LINE OF THEIR OWN.

    The homage also occurs inside narrative — a character utters it ("tikkhattuṁ
    udānaṁ udānesi– 'Namo tassa…'") — and that is ordinary body text, not a book
    head.  Requiring the printed line to consist of nothing but the homage
    separates the two."""
    out = []
    for pi, pg in enumerate(pages):
        for l in pg.split('\n'):
            t = l.strip()
            m = HOMAGE.search(t)
            if m and m.group(0) == t:
                out.append((pi, t))
    return out


def build(vol, verbose=True):
    paras = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))['paragraphs']
    pages = pdf_pages(vol)
    printed = printed_forms(pages)
    inc, unresolved = {}, []

    # (a) homage swallowed into a paragraph's text — anchor it to that paragraph
    for i, p in enumerate(paras):
        m = HOMAGE.search(p['text'])
        if not m: continue
        pre = p['text'][max(0, m.start() - 60):m.start()]
        # quoted / uttered inside narrative -> body text, leave it alone
        if re.search(r'udān|[“”"‘\']', pre): continue
        # a genuine book head is preceded by the closing colophon of the previous
        # book and/or the new book's title ("…paṭṭhānaṁ niṭṭhitaṁ. Dukapaṭṭhānapāḷi")
        if m.start() > 0 and not re.search(r'pāḷi|niṭṭhit|samatt', pre): continue
        # The context test above is what separates a book head from narrative;
        # the printed display line is used only to take the WORDING from the page
        # (books vary: "Bhagavato" vs "Bhagavatā"), falling back to the corpus.
        pp = p.get('pdf_page')
        near = [t for pi, t in printed if pp and abs(pi - pp) <= 3]
        inc[str(i)] = near[0] if near else m.group(0)

    # (b) homage printed but absent from the corpus — needs an explicit anchor
    for ord_, pg in BOOK_STARTS.get(vol, {}).items():
        line = next((t for pi, t in printed if abs(pi - pg) <= 2), None)
        if line: inc[str(ord_)] = line
        else: unresolved.append(('book-start', ord_, pg))

    # The reader still emits its built-in homage for the FIRST book of a volume
    # (base===0), so one printed-but-unanchored copy is expected and fine.
    # Anything beyond that is a book head the render is missing entirely.
    slack = 1 if '0' not in inc else 0
    if len(printed) - len(inc) > slack:
        unresolved.append(('printed %d, anchored %d -> %d book head(s) unaccounted'
                           % (len(printed), len(inc), len(printed) - len(inc) - slack), None, None))
    if verbose and (inc or unresolved):
        print(f'{vol:11s} printed {len(printed):3d}  anchored {len(inc):3d}'
              + (f'  UNRESOLVED {unresolved}' if unresolved else ''))
    return inc, unresolved


def main():
    a = sys.argv[1:]
    write = '--write' in a
    man = json.load(open(f'{ROOT}/site/reader/manifest.json', encoding='utf-8'))['volumes']
    vols = a[a.index('--vol') + 1:] if '--vol' in a else sorted(man)
    os.makedirs(f'{ROOT}/site/reader/incipit', exist_ok=True)
    total, flagged = 0, []
    for vol in vols:
        inc, unresolved = build(vol)
        if unresolved: flagged.append((vol, unresolved))
        total += len(inc)
        if write:
            path = f'{ROOT}/site/reader/incipit/{vol}.json'
            json.dump({k: inc[k] for k in sorted(inc, key=int)},
                      open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'\n{total} incipit anchors across {len(vols)} volumes'
          + ('' if write else '   [dry-run: pass --write]'))
    if flagged:
        print('FLAGGED (printed homages this builder could not anchor — do NOT guess, '
              'they need the book boundary for that volume):')
        for v, u in flagged: print(f'   {v}: {u}')


if __name__ == '__main__':
    main()
