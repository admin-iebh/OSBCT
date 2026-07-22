# Extractor v2 — hierarchy, interval linking, apparatus

## Model changes

**Paragraphs are addressed hierarchically**, not by bare number:
`Ekakanipātapāḷi/Dutiyapamādādivagga/X/101`. Three levels — book, vagga, sutta — derived
mainly from the running heads, which alternate broader (verso) and narrower (recto)
exactly as §5 describes. IDs are unique in every volume tested: Dīgha 559/559,
Saṁyutta 517/517, Aṅguttara 901/901.

**Commentary links are intervals, not points.** A commentary paragraph governs the canon
from its own number until the next commentary paragraph. Under this model Dīgha vol. 1 is
**100% covered**: 272 canon paragraphs have a direct comment, 285 are governed by a
preceding one, none precede the first comment. Subcommentary: 264 direct, 293 governed.

Each canon paragraph therefore carries one of three states — `direct`, `covered` (with a
pointer to the governing paragraph), or `none` for texts with no commentary at all.

**The validator is inverted.** Canon without commentary is normal and is never flagged.
The meaningful anomaly is a *commentary* paragraph with no canon counterpart.

## Fixes made

| Fault | Effect | Status |
|---|---|---|
| Body start detected by page number | Dropped canon §§1–2 | Fixed — anchored on the `Namo tassa` invocation |
| Book and vagga flattened into one level | Alternating running heads split each division; produced 269 phantom "gaps" | Fixed — Saṁyutta and Dīgha now show zero gaps |
| Cross-reference regex too narrow | 78% of unparsed notes were missed citations | Fixed — now handles `piṭṭhesupi`, ranges (`144-5`), comma lists, and `;`-separated multi-work citations |

Apparatus parsing across three volumes: unparsed notes fell from **9.5% to 1.7%**, and
extracted cross-references rose from ~435 to **1,404**. Dīgha commentary alone now yields
609 cross-references, up from 319.

## Open — unresolved

**Aṅguttara still shows numbering gaps within a book (490).** My earlier guess that these
are *peyyāla* elisions is **not confirmed** — the level-flattening fix cleared the gaps in
Saṁyutta and Dīgha but not here. Aṅguttara appears to carry two numbering systems at once
(a running number and a per-vagga sutta number in parentheses, e.g. `. Pañcamaṁ.`, `(3)`).
Needs investigation before Aṅguttara is trusted. **Flagged, not guessed.**

**Eight sutta-name mismatches in Dīgha**, all in Sāmaññaphalasutta, caused by the
running-head erratum (`Sāmaññaphalasutta` p. 44 vs `Sāmaññāphalasutta` p. 45). Linking
needs a canonical name table per volume, with the variant recorded as an erratum rather
than silently folded.

**Remaining 1.7% unparsed notes** — mostly editorial remarks in prose
(`Ayaṁ nakāro Sī-Syā-I-potthakesu na dissati`), which are a distinct note type, not a
parsing failure. They should probably be captured as `comment` rather than forced into
the variant or citation schema.
