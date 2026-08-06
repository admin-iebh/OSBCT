# v2.3.0 — the printed page becomes the standard

*Released 6 August 2026. 118 volumes, 89,512 paragraphs.*

Until this release, almost every check in this project compared the corpus with
itself, and a volume that had lost its structure passed all of them. This release
is the one where the **printed page** became the thing the corpus is measured
against — and most of what follows was found that way.

## Corpus

- **Four Khuddaka commentaries re-segmented against the printed page.**
  `20KhuA01`, `21KhuA02`, `23KhuA04` and `24KhuA05` go from **460 paragraphs to
  3,607**. They had been stored as lumps: 67 breaks where the page sets 664.
- **2,976 printed lines were in the repository and had never been drawn.** The
  verse branch was gated on a key that three builders deliberately omit.
- **The seven Jātaka commentaries were one job.** One missing measurement fed two
  branches; 30,619 printed lines were set wrong and **30,512 are now set as the
  page sets them**.
- **Page-verse drawn as prose falls from 23,164 printed lines to 9,854.**
- **SPEC book bounds now follow the re-segmentation**, so four volumes that could
  not be rebuilt at all are buildable again.

## Reader

- **A canon paragraph's commentary is a range, not a point.** The reader drew the
  first paragraph of a nineteen-paragraph section and silently dropped the other
  eighteen.
- **Long runs collapse behind a "Read more" control**, cut by a **1,500-character
  budget over whole paragraphs** rather than by a paragraph count. A paragraph in
  this corpus varies fifty-fold in length, so a fixed count showed anywhere from
  200 characters to most of a book.
- **293,266 bold runs were in the repository and off the screen** in the spine
  view. The edition's bold is now drawn, and checked against the printed page.
- **Every paragraph carries its printed page breaks.**
- **The 320 links the commentary's own stated ordinal condemns are dimmed and say
  which check condemned them.** They still open — the reader's decision of
  2026-08-03 was to show the doubt, not to decide on the reader's behalf.
- **A tab left open when a new build ships can find out and say so.**
- **Tooltips are rendered on `<body>`** so nothing clips them, and the panel's
  duplicate CSS renderer is gone: one `data-tip`, one tooltip.

## Word panel

- **A word in the dictionaries can now be typed.** The search box was gated on
  `lookup/freq` — the words that *occur in the Tipiṭaka* — while the panel it
  opens is mostly dictionaries; and the evaluation store was entered through
  inflected surface forms only. **66% of lemma entries and 77% of DPD headwords
  were unreachable.** Reported by the reader as `atappaka`, a word plainly
  present in the Abhidhāna.

## Instruments — the change beneath all of the above

- **`check_page_fidelity.py`** — the first check that compares the corpus with the
  **printed page** rather than with itself, and its census over all 118 volumes.
- **`check_bold_fidelity`** (bold read from text render mode 2), **`check_derived`**
  (staleness of derived artefacts), **`check_layout`** (jsdom, on the device),
  and **`check_dimmed`**, **`check_runcut`**, **`check_tipplace`**,
  **`check_lookup_reach`**.
- **A block-boundary map taken from the PDF's own coordinates**: a new block
  begins where the leading exceeds *that page's own* body leading by more than
  3pt. No constant, no per-volume flag — and it reproduces the reader's
  hand-drawn stanza breaks exactly.

## Measured and deliberately not applied

- **BLOCKBREAK** restores 492 lost printed line breaks. Measured across all 101
  `katha` volumes with the letters byte-identical, and left behind its flag
  because two mid-sentence lines are still unexplained.
- **The hyphen repair.** 8,790 words are broken by a line-break hyphen followed by
  a space. It was applied, measured, and **reverted**: it stops the builder
  reproducing its own side-maps (`09DiT02` 2,012 → 4,489 drawn lines, three
  ordinals lost). The words are still broken. The repair needs the builder's
  paragraph matcher changed with it.

## Known limits, stated rather than hidden

- **Position** — whether a paragraph is broken where the page breaks it — is
  **unmeasured for 114 of 118 volumes**.
- **The class 1 and class 2 counts are suspect.** The page-side classifier calls
  the Yamaka's mātikā verse; the reader says prose, and the corpus already treats
  it as prose. An unknown share of both counts are the checker being wrong.
- **The site is 26,576 files and publishes against a ten-minute ceiling that
  cannot be raised.** See `docs/DEPLOY_SCALE.md`.

## Citing this version

`CITATION.cff` and `.zenodo.json` are updated to 2.3.0. Figures in them are
**counted, not carried forward** — paragraphs from the 118 `site/<VOL>.json`,
variants and cross-references from `site/reader/apparatus/` — so they can be
re-derived from the deposit itself. The previous deposit's variant and
cross-reference figures could not be reproduced by that method and have been
restated as measured rather than repeated.

`v2.2.0` has **no DOI recorded**: it was tagged and, so far as this repository
knows, never deposited. That gap is left visible rather than filled with a guess.
