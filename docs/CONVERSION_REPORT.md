# OSBCT — Unicode PDF conversion report

Generated 2026-07-21. Covers the `/ToUnicode` injection stage only; no text corpus has been produced yet.

## Result

| | |
|---|---|
| Volumes processed | **118 / 118** (pali 40, atthakatha 52, tika 26) |
| Failures | 0 |
| Pages | 54,269 |
| Extractable characters | 89,737,672 |
| Fonts given a corrected map | 1,228 |
| Character codes remapped | 19,062 |
| Page rendering | unchanged (verified pixel-identical on samples) |

Output is written to `pali-unicode/`, `atthakatha-unicode/`, `tika-unicode/`. The original folders are untouched.

## Method

A `/ToUnicode` CMap is attached to every embedded VZTime font. Glyph selection is unaffected, so pages render exactly as before; only extraction, search and copy-paste change. Per §6 of the project instructions this is preferred over regenerating the PDFs, because page fidelity — and therefore citability — is preserved.

The map is built by composition, not by a fixed byte table:

1. Determine each font's code to legacy character (from its existing `/ToUnicode` if it has one, otherwise from WinAnsiEncoding).
2. Apply the VZTime to Unicode table below.
3. Write the result back as a corrected `/ToUnicode`.

Because the map is attached per font, non-Pāḷi runs are left alone automatically. This is strictly more accurate than converting extracted text with a global byte mapping, which corrupts the `©` in the credits line and turns the Burmese alphabet table on page 3 into plausible-looking nonsense.

## Mapping table

| Legacy | Unicode | Legacy | Unicode |
|---|---|---|---|
| `È` | ā | `Œ` | Ā |
| `Ê` | ī | `¢` | Ī *(new)* |
| `\|` | ū | `\x9D` | Ū *(new)* |
| `Ñ` | ṁ | `©` | Ñ |
| `~` | ṅ | `^` | Ṅ *(new)* |
| `Ò` | ñ | | |
| `Ô` | ṭ | `®` | Ṭ |
| `É` | ḍ | `\x8F` | Ḍ *(new)* |
| `Ó` | ṇ | `ª` | Ṇ *(new)* |
| `Ä` | ḷ | `£` | Ḷ |

Five capitals marked *(new)* were absent from the original project table. Each was identified from context and verified against the printed page. `Ñ` maps to **ṁ** (dot above), following the printed edition rather than the ṃ of the VRI/CST digital edition.

## Font variants encountered

| Variant | Count | Handling |
|---|--:|---|
| TrueType, WinAnsi, no map | 964 | built from WinAnsiEncoding |
| TrueType, re-subset with arbitrary codes | 47 | composed from existing map |
| Type0 / Identity-H composite | 217 | composed from existing map |

The three variants are not distinguishable from the outside; assuming a single one would have silently corrupted or skipped part of the corpus.

## Verification

- Every volume's page count is unchanged.
- Rendering compared pixel-by-pixel at 130–150 dpi on sampled pages across all three layers — zero differing pixels.
- `qpdf --check` passes on samples.
- Character census over all 89.7 M extracted characters: no residual legacy glyphs outside the alphabet-table pages, except as noted below.

## Known defects — unresolved

### 1. Unmappable ligature glyphs in 4 volumes

- `atthakatha/08DiA02.pdf`
- `pali/27Khu10.pdf`
- `tika/12DiT05.pdf`
- `tika/26VsmT02.pdf`

Each contains one composite font whose `/ToUnicode` is **empty in the source PDF** — the glyphs carry no Unicode information at all, so no CMap rewrite can recover them. They appear to be ligatures: in `08DiA02` the sequence `n` + glyph prints as `ṇa`, suggesting the glyph draws a combining dot-below plus `a`.

Affected characters: roughly 16 across the four volumes. These need glyph-level identification (reading outlines from the embedded font) rather than inference. **Flagged, not guessed.**

Note that a character census cannot detect this class of fault, where the glyph extracts as nothing rather than as a wrong character. Any future census should be paired with an orthographic check.

### 2. Errata in the printed edition

Confirmed by rendering the page — e.g. An. vol. 1 p. 184: `appqmāṇena` for *appamāṇena*, `viharāmò` for *viharāmi*, `brāhmā }e eso` for *brahmā me eso*. These are faults of the edition, not of extraction, and per working principle 3 must be recorded as errata with the original reading preserved, never silently corrected. Estimated on the order of one per 500k characters. The erratum register is not yet built.

## Notes

- pikepdf re-encodes streams, so output files are not byte-identical to input (434.8 MB in, 398.1 MB out). Rendering is unaffected, but these are rewritten files.
- Copy-paste into a word processor should use Paste and Match Style (Shift-Option-Cmd-V). Pasting with formatting carries the VZTime font, which has no glyph for `ā` and will display substitutes. The underlying characters are correct either way.
- Search inside a PDF reader is literal: `sangahita` will not find *saṅgahitā*. Diacritic-insensitive matching belongs to the search index, not the PDFs.

## Per-volume detail

| Volume | Pages | Chars | WinAnsi | Recoded | Type0 | Codes mapped | Residual | Empty maps |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| `atthakatha/01VinA01.pdf` | 402 | 717,592 | 6 | 0 | 2 | 116 |  |  |
| `atthakatha/02VinA02.pdf` | 358 | 637,330 | 6 | 0 | 4 | 120 |  |  |
| `atthakatha/03VinA03.pdf` | 493 | 812,921 | 6 | 0 | 3 | 118 |  |  |
| `atthakatha/04VinA04.pdf` | 305 | 496,879 | 6 | 0 | 4 | 118 |  |  |
| `atthakatha/05Kankha.pdf` | 418 | 662,399 | 6 | 0 | 3 | 117 |  |  |
| `atthakatha/06VinSg06.pdf` | 473 | 910,047 | 5 | 0 | 1 | 96 |  |  |
| `atthakatha/07DiA01.pdf` | 437 | 758,168 | 6 | 0 | 2 | 116 |  |  |
| `atthakatha/08DiA02.pdf` | 445 | 784,373 | 0 | 6 | 1 | 59 | 7 | 1 |
| `atthakatha/09DiA03.pdf` | 297 | 495,143 | 6 | 0 | 0 | 114 |  |  |
| `atthakatha/10MaA01.pdf` | 449 | 799,648 | 6 | 0 | 4 | 119 |  |  |
| `atthakatha/11MaA02.pdf` | 383 | 691,493 | 6 | 0 | 4 | 120 |  |  |
| `atthakatha/12MaA03.pdf` | 377 | 648,185 | 6 | 0 | 2 | 116 |  |  |
| `atthakatha/13MaA04.pdf` | 293 | 507,365 | 6 | 0 | 2 | 116 |  |  |
| `atthakatha/14SamA01.pdf` | 400 | 679,176 | 6 | 0 | 2 | 117 |  |  |
| `atthakatha/15SamA02.pdf` | 391 | 657,551 | 7 | 0 | 2 | 137 |  |  |
| `atthakatha/16SamA03.pdf` | 422 | 684,924 | 9 | 0 | 2 | 174 |  |  |
| `atthakatha/17AnA01.pdf` | 480 | 882,402 | 6 | 0 | 0 | 114 |  |  |
| `atthakatha/18AnA02.pdf` | 515 | 847,846 | 8 | 0 | 3 | 157 |  |  |
| `atthakatha/19AnA03.pdf` | 482 | 752,515 | 12 | 0 | 2 | 230 |  |  |
| `atthakatha/20KhuA01.pdf` | 269 | 451,292 | 8 | 0 | 2 | 154 |  |  |
| `atthakatha/21KhuA02.pdf` | 503 | 906,682 | 8 | 0 | 2 | 154 |  |  |
| `atthakatha/22KhuA03.pdf` | 528 | 875,370 | 10 | 0 | 2 | 194 |  |  |
| `atthakatha/23KhuA04.pdf` | 477 | 828,337 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/24KhuA05.pdf` | 438 | 735,568 | 7 | 0 | 2 | 135 |  |  |
| `atthakatha/25KhuA06.pdf` | 386 | 668,281 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/26KhuA07.pdf` | 421 | 682,579 | 7 | 0 | 2 | 137 |  |  |
| `atthakatha/27KhuA08.pdf` | 434 | 616,916 | 12 | 0 | 2 | 232 |  |  |
| `atthakatha/28KhuA09.pdf` | 362 | 530,143 | 6 | 0 | 2 | 117 |  |  |
| `atthakatha/29KhuA10.pdf` | 644 | 997,870 | 8 | 0 | 2 | 156 |  |  |
| `atthakatha/30KhuA11.pdf` | 687 | 1,056,383 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/31KhuA12.pdf` | 399 | 569,832 | 8 | 0 | 2 | 155 |  |  |
| `atthakatha/32KhuA13.pdf` | 443 | 735,081 | 6 | 0 | 2 | 117 |  |  |
| `atthakatha/33KhuA14.pdf` | 374 | 593,579 | 7 | 0 | 2 | 135 |  |  |
| `atthakatha/34KhuA15.pdf` | 453 | 715,106 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/35KhuA16.pdf` | 384 | 648,030 | 6 | 0 | 2 | 116 |  |  |
| `atthakatha/36KhuA17.pdf` | 630 | 1,076,437 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/37KhuA18.pdf` | 487 | 793,291 | 8 | 0 | 2 | 156 |  |  |
| `atthakatha/38KhuA19.pdf` | 623 | 976,349 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/39KhuA20.pdf` | 617 | 961,731 | 13 | 0 | 2 | 251 |  |  |
| `atthakatha/40KhuA21.pdf` | 678 | 1,035,706 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/41KhuA22.pdf` | 408 | 640,270 | 6 | 0 | 2 | 116 |  |  |
| `atthakatha/42KhuA23.pdf` | 503 | 717,134 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/43KhuA24.pdf` | 537 | 917,270 | 6 | 0 | 2 | 118 |  |  |
| `atthakatha/44KhuA25.pdf` | 180 | 289,713 | 8 | 0 | 4 | 157 |  |  |
| `atthakatha/45KhuA26.pdf` | 293 | 542,828 | 6 | 0 | 1 | 115 |  |  |
| `atthakatha/46KhuA27.pdf` | 407 | 733,344 | 6 | 0 | 0 | 114 |  |  |
| `atthakatha/47KhuA28.pdf` | 401 | 704,289 | 9 | 0 | 2 | 174 |  |  |
| `atthakatha/48AbhiA01.pdf` | 548 | 956,277 | 7 | 0 | 2 | 135 |  |  |
| `atthakatha/49AbhiA02.pdf` | 530 | 948,272 | 10 | 0 | 2 | 193 |  |  |
| `atthakatha/50AbhiA03.pdf` | 539 | 902,110 | 7 | 0 | 2 | 137 |  |  |
| `atthakatha/51Vism01.pdf` | 411 | 704,760 | 6 | 0 | 2 | 117 |  |  |
| `atthakatha/52Vism02.pdf` | 396 | 678,532 | 6 | 0 | 0 | 114 |  |  |
| `pali/01Vin01.pdf` | 428 | 707,064 | 19 | 0 | 3 | 364 |  |  |
| `pali/02Vin02.pdf` | 511 | 807,237 | 14 | 0 | 3 | 271 |  |  |
| `pali/03Vin03.pdf` | 674 | 1,253,067 | 24 | 0 | 2 | 459 |  |  |
| `pali/04Vin04.pdf` | 554 | 968,352 | 14 | 0 | 7 | 273 |  |  |
| `pali/05Vin05.pdf` | 440 | 679,688 | 14 | 0 | 2 | 268 |  |  |
| `pali/06Di01.pdf` | 265 | 439,084 | 12 | 0 | 0 | 228 |  |  |
| `pali/07Di02.pdf` | 311 | 524,856 | 14 | 0 | 1 | 267 |  |  |
| `pali/08Di03.pdf` | 298 | 471,603 | 0 | 18 | 0 | 171 |  |  |
| `pali/09Ma01.pdf` | 451 | 813,900 | 7 | 0 | 4 | 139 |  |  |
| `pali/10Ma02.pdf` | 477 | 872,743 | 8 | 0 | 2 | 154 |  |  |
| `pali/11Ma03.pdf` | 382 | 701,712 | 8 | 0 | 2 | 156 |  |  |
| `pali/12Sam01.pdf` | 554 | 831,143 | 9 | 0 | 2 | 173 |  |  |
| `pali/13Sam02.pdf` | 610 | 1,043,315 | 10 | 0 | 1 | 191 |  |  |
| `pali/14Sam03.pdf` | 457 | 732,164 | 10 | 0 | 0 | 190 |  |  |
| `pali/15An01.pdf` | 656 | 1,071,184 | 15 | 0 | 3 | 290 |  |  |
| `pali/16An02.pdf` | 573 | 956,759 | 10 | 0 | 2 | 193 |  |  |
| `pali/17An03.pdf` | 614 | 1,027,038 | 10 | 0 | 2 | 192 |  |  |
| `pali/18Khu01.pdf` | 556 | 721,437 | 7 | 0 | 2 | 137 |  |  |
| `pali/19Khu02.pdf` | 547 | 612,281 | 10 | 0 | 2 | 194 |  |  |
| `pali/20Khu03.pdf` | 514 | 608,872 | 9 | 0 | 2 | 175 |  |  |
| `pali/21Khu04.pdf` | 491 | 604,665 | 7 | 0 | 2 | 136 |  |  |
| `pali/22Khu05.pdf` | 522 | 601,053 | 7 | 0 | 2 | 137 |  |  |
| `pali/23Khu06.pdf` | 494 | 633,532 | 7 | 0 | 2 | 137 |  |  |
| `pali/24Khu07.pdf` | 486 | 826,152 | 6 | 0 | 2 | 118 |  |  |
| `pali/25Khu08.pdf` | 347 | 563,049 | 6 | 0 | 4 | 119 |  |  |
| `pali/26Khu09.pdf` | 456 | 818,995 | 6 | 0 | 0 | 114 |  |  |
| `pali/27Khu10.pdf` | 387 | 646,819 | 0 | 8 | 1 | 73 |  | 1 |
| `pali/28Khu11.pdf` | 457 | 732,656 | 10 | 0 | 2 | 193 |  |  |
| `pali/29Abhi01.pdf` | 327 | 502,049 | 6 | 0 | 0 | 114 |  |  |
| `pali/30Abhi02.pdf` | 477 | 779,110 | 8 | 0 | 0 | 152 |  |  |
| `pali/31Abhi03.pdf` | 207 | 306,392 | 6 | 0 | 1 | 115 |  |  |
| `pali/32Abhi04.pdf` | 493 | 790,928 | 9 | 0 | 2 | 172 |  |  |
| `pali/33Abhi05.pdf` | 283 | 483,917 | 7 | 0 | 0 | 133 |  |  |
| `pali/34Abhi06.pdf` | 336 | 571,738 | 8 | 0 | 0 | 152 |  |  |
| `pali/35Abhi07.pdf` | 347 | 663,044 | 9 | 0 | 0 | 171 |  |  |
| `pali/36Abhi08.pdf` | 497 | 746,334 | 32 | 0 | 0 | 608 |  |  |
| `pali/37Abhi09.pdf` | 529 | 850,482 | 19 | 0 | 0 | 361 |  |  |
| `pali/38Abhi10.pdf` | 620 | 959,778 | 6 | 0 | 0 | 114 |  |  |
| `pali/39Abhi11.pdf` | 650 | 923,221 | 7 | 0 | 0 | 133 |  |  |
| `pali/40Abhi12.pdf` | 450 | 639,634 | 7 | 0 | 0 | 133 |  |  |
| `tika/01ViT01.pdf` | 519 | 954,623 | 6 | 0 | 1 | 115 |  |  |
| `tika/02ViT02.pdf` | 509 | 916,216 | 6 | 0 | 3 | 117 |  |  |
| `tika/03ViT03.pdf` | 563 | 929,848 | 12 | 0 | 3 | 232 |  |  |
| `tika/04ViT04.pdf` | 404 | 740,698 | 6 | 0 | 3 | 117 |  |  |
| `tika/05ViT05.pdf` | 363 | 543,781 | 13 | 0 | 2 | 249 |  |  |
| `tika/06ViT06.pdf` | 656 | 1,110,470 | 9 | 0 | 4 | 175 |  |  |
| `tika/07ViT07.pdf` | 528 | 907,282 | 8 | 0 | 3 | 155 |  |  |
| `tika/08DiT01.pdf` | 445 | 811,635 | 10 | 0 | 1 | 191 |  |  |
| `tika/09DiT02.pdf` | 528 | 1,018,695 | 6 | 0 | 1 | 115 |  |  |
| `tika/10DiT03.pdf` | 469 | 879,023 | 7 | 0 | 2 | 136 |  |  |
| `tika/11DiT04.pdf` | 395 | 701,645 | 6 | 0 | 1 | 115 |  |  |
| `tika/12DiT05.pdf` | 313 | 556,592 | 0 | 7 | 1 | 69 |  | 1 |
| `tika/13MaT01.pdf` | 427 | 798,246 | 6 | 0 | 1 | 115 |  |  |
| `tika/14MaT02.pdf` | 354 | 649,026 | 6 | 0 | 2 | 116 |  |  |
| `tika/15MaT03.pdf` | 465 | 839,069 | 7 | 0 | 2 | 136 |  |  |
| `tika/16SaT01.pdf` | 396 | 648,700 | 10 | 0 | 2 | 194 |  |  |
| `tika/17SaT02.pdf` | 619 | 970,468 | 9 | 0 | 2 | 175 |  |  |
| `tika/18AnT01.pdf` | 320 | 582,096 | 7 | 0 | 1 | 134 |  |  |
| `tika/19AnT02.pdf` | 435 | 736,732 | 9 | 0 | 3 | 174 |  |  |
| `tika/20AnT03.pdf` | 408 | 681,085 | 10 | 0 | 1 | 191 |  |  |
| `tika/21KhuT01.pdf` | 532 | 957,027 | 9 | 0 | 1 | 171 |  |  |
| `tika/22AbhiT01.pdf` | 466 | 841,467 | 10 | 0 | 2 | 192 |  |  |
| `tika/23AbhiT02.pdf` | 503 | 841,455 | 13 | 0 | 4 | 251 |  |  |
| `tika/24AbhiT03.pdf` | 619 | 1,003,353 | 18 | 0 | 2 | 344 |  |  |
| `tika/25VsmT01.pdf` | 526 | 947,855 | 6 | 0 | 2 | 118 |  |  |
| `tika/26VsmT02.pdf` | 569 | 1,068,219 | 0 | 8 | 1 | 78 |  | 1 |
