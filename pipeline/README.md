# Pipeline

The corpus was produced by an automated pipeline. This directory holds the core extraction code;
the full method, parameters, and verification results are documented in [`../docs/`](../docs/).

## Stages

1. **Unicode conversion** — a corrected `/ToUnicode` map is injected into each embedded VZTimes
   font, so pages render identically to the print while the text layer becomes valid Unicode.
   Self-verified by a character census over all ~73M characters (see
   [`../docs/CONVERSION_REPORT.md`](../docs/CONVERSION_REPORT.md)).
2. **Structural extraction** (`extract.py`) — parses each volume into a hierarchy
   (book / vagga / sutta / paragraph), anchored to printed page numbers, with peyyāla ranges
   expanded and the footnote apparatus parsed into variant readings and cross-references.
3. **Cross-layer linking** — canon paragraphs are linked to commentary and subcommentary using the
   shared paragraph numbering under an interval model, scoped by the volume concordance
   (`../data/concordance.json`). Result: `../data/links_all.json`
   (see [`../docs/LINKS_REPORT.md`](../docs/LINKS_REPORT.md)).
4. **Search index** — a diacritic-folded inverted index, sharded per volume (`site/index/`).

## Note on completeness

`extract.py` is the structural extractor. Several auxiliary scripts (font injection, index build,
apparatus attachment, concordance parsing, link generation) were run in a scratch environment and
are being consolidated back into this directory. Their logic is fully described in the reports in
[`../docs/`](../docs/), and their outputs are all present under `../data/` and `site/`. The
published corpus does not depend on re-running them.
