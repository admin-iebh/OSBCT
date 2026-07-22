# Structural extraction — prototype findings

Dīgha Nikāya vol. 1, all three layers, run end-to-end from the injected Unicode PDFs.
This is a **prototype**: it establishes what parses reliably and what does not. Nothing
here is settled, and no erratum has been recorded.

## What was produced

| File | Contents |
|---|---|
| `DN.txt`, `DN-A.txt`, `DN-T.txt` | body text, page-anchored, apparatus removed |
| `*.structure.json` | per page: printed number, running head, body, apparatus, parsed notes |
| `links.json` | paragraph number to printed page in each of the three layers |
| `variants.json` | 1,440 variant readings with sigla |
| `xrefs.json` | 560 internal cross-references, resolved to work / volume / page |

## What parses reliably

**Paragraph numbers.** DN 557, DN-A 275, DN-T 268. DN-A and DN-T match the independent
count from the earlier alignment test exactly.

**Cross-layer linking works.** Of 557 canon paragraphs, **247 have both** a commentary and
a subcommentary paragraph — the join key holds in practice, not just in the sample.

**The variant apparatus is regular.** 1,440 readings parsed. Siglum distribution:

| Siglum | Count | | Siglum | Count |
|---|--:|---|---|--:|
| Syā | 544 | | Sī | 500 |
| Ka | 470 | | bahūsu | 79 |
| I | 74 | | Abhinavaṭī | 39 |
| Kaṁ | 34 | | Ṭṭha | 31 |
| ? | 30 | | Ka-Sī | 7 |
| SĪ | 7 | | katthaci | 5 |

The three Burmese-tradition witnesses (Syā, Sī, Ka) dominate, as expected. `?` — the
Council editors' conjectured old reading — occurs 30 times in this volume alone, which
suggests the marker is used freely enough to be worth surfacing in the interface.

**Cross-references.** 560 parsed, almost all in the commentary (319) and subcommentary
(240); the canon itself carries only 1 in this volume.

## What needed fixing during the run

- **Decorative rules were mistaken for the footnote rule.** Sutta titles are underlined
  with a short rule of the same character as the footnote separator. Body text was
  landing in the apparatus. Distinguished by length (62 characters vs 4–6). This would
  have silently corrupted every sutta-opening page.
- **Sutta-opening pages carry no running head**, so no printed page number. Now
  interpolated from the surrounding pages and marked `printed_inferred`.
- **Front matter uses roman numerals** and repeats paragraph-like numbering in the verse
  preface; excluded by detecting the start of the body.

## Flagged — not settled

**1. Out-of-sequence paragraph numbers (3 cases).**

| Layer | Printed page | Reads | Surrounding |
|---|--:|---|---|
| DN-A | 295 | `339. Dujjānoti idampi so…` | next paragraph on the page is 402 |
| DN-T | 170 | `45. Uddhamāghātanāti…` | far from the other §45 on p. 159 |
| DN-T | 353 | `359. Kuṇḍakanti tanutaraṁ taṇḍulasakalaṁ.` | far from the other §359 on p. 337 |

I rendered the DN-A case: the page genuinely prints `339.`, so this is not an extraction
fault. Either the edition's numbering is anomalous here, or it follows a convention I
haven't identified. **Confidence that something is irregular: high. Confidence about the
correct reading: none.** Needs a reader who knows the edition's conventions.

**2. One unnumbered page per volume**, at the start of the back-matter `Nānāpāṭhā`
apparatus, in all three volumes. Consistent across layers, so probably an unnumbered
divider page in the print rather than a parsing fault — but unverified.

**3. Running-head inconsistency.** DN p. 44 heads the sutta `Sāmaññaphalasutta`; p. 45
heads it `Sāmaññāphalasutta`. One is wrong. Candidate erratum, unadjudicated.

**4. Siglum case variants.** `SĪ` (7) and `SYā` (3) appear alongside `Sī` and `Syā`.
Almost certainly the same witnesses with inconsistent capitalisation in the edition, but
normalising them is an editorial act and should be a recorded decision, not a silent
regex.

## Not yet done

- Sutta and vagga headings are not extracted; paragraphs are page-anchored but not yet
  placed in the sutta hierarchy.
- Footnote markers in the body are not yet tied to their apparatus entries — the numbers
  are parsed on both sides but not joined.
- No orthographic validator yet, so the erratum candidate list is not generated.
- Vinaya and Abhidhamma layouts are untested; these rules are calibrated on sutta
  formatting only.
