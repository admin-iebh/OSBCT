# Full corpus extraction — all 118 volumes

Every volume processed, no failures. Output is one `.json` (structure) and one `.txt`
(readable, page- and ID-anchored) per volume in this folder.

## Totals

| | |
|---|---|
| Volumes | 118 / 118 |
| Pages | 54,037 |
| Paragraphs | 83,751 |
| Peyyāla ranges expanded | 1,995 |
| Suttas / sections | 9,431 |
| Apparatus notes | 70,766 |
| **Variant readings** | **54,239** |
| **Cross-references** | **31,541** |

The variant apparatus — 54,239 readings with sigla — is the number that matters
most for §5. As far as I know this is the first time this edition's apparatus exists as
structured data.

## What is solid

- Extraction ran clean on all three layers and every layout family.
- Peyyāla ranges (`102-109.`) are expanded to their covered numbers, marked `peyyala:true`,
  text untouched.
- Apparatus parse rate is high: 1,921 unparsed of 70,766 (2.7%),
  the rest being editorial prose notes rather than failures.
- Hierarchical IDs (`book/vagga/sutta/n`) are emitted for every paragraph.

## Two things NOT yet trustworthy — flagged

**1. The numbering-gap count (54,138) is dominated by a labelling artifact, not missing text.**
It is concentrated in Abhidhamma and Khuddaka, where sub-sections whose names end in
`-pāḷi` (e.g. `Aṭṭhānapāḷi`) trip the book-vs-vagga classifier and split one continuous
paragraph sequence into several buckets. The per-book gap metric then counts the bucket
boundaries as gaps. **No paragraphs are lost** — this is a hierarchy-labelling problem in
the most deeply nested texts. It needs the book/vagga classifier refined before the metric
means anything. Until then, gap counts for Abhidhamma and Khuddaka volumes should be
ignored, not trusted.

**2. The orthographic erratum scan is too narrow — 18 candidates is an undercount.**
This first-pass scan flags only non-Pāḷi ASCII and control characters in paragraph text.
It correctly re-found the known cases (e.g. the 7 ligature-glyph residues in `08DiA02`,
the `appqmāṇena` class), but it cannot see errata that produce a *legal* Pāḷi letter —
`n` for `ṇ`, a dropped consonant — which are likely the larger class. The real erratum
register needs the witness-comparison method discussed earlier, not just an orthographic
filter. Treat these 18 as the tip, not the total.

## Still deferred (as agreed)

- Book/vagga classifier refinement for Abhidhamma and Khuddaka (item 1 above).
- Canonical sutta-name table, to absorb running-head errata like Sāmaññaphala.
- Reclassifying the ~2.7% prose apparatus notes as `comment`.
- Cross-layer link tables corpus-wide (only Dīgha built so far).
- Broadened / witness-based erratum detection.
