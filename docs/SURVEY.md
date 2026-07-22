# Layout survey — seven volumes across the canon

Ran the Dīgha-calibrated extractor against one representative volume from each layout
family, to find out whether the parsing rules generalise before scaling to 118 volumes.

## Result

| Volume | Pages | Paragraphs | Range | Restarts | Rule pages | Notes | Unparsed | Variants | Xrefs |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| DN-prose | 264 | 557 | 3–559 | 0 | 92 | 175 | 4 | 197 | 1 |
| Vinaya | 425 | 660 | 2–662 | 3 | 140 | 210 | 12 | 197 | 16 |
| Samyutta | 549 | 516 | 1–271 | 1 | 269 | 534 | 19 | 623 | 2 |
| Anguttara | 653 | 897 | 1–611 | 4 | 381 | 817 | 51 | 827 | 102 |
| Khu-verse | 550 | 1865 | 1–1155 | 14 | 407 | 1254 | 83 | 1301 | 135 |
| Khu-prose | 386 | 270 | 1–170 | 3 | 256 | 691 | 79 | 412 | 300 |
| Abhidhamma | 325 | 1775 | 1–1616 | 2 | 45 | 69 | 0 | 70 | 0 |

## Headline: one parser, not five

The page conventions are uniform across the whole canon. Running heads, the 62-character
footnote rule, the apparatus layout and the siglum syntax behave the same in Vinaya,
Saṁyutta, Aṅguttara, Khuddaka verse, Khuddaka prose and Abhidhamma as they do in Dīgha.
No family needs its own parser — the same rules apply throughout, which was the main
thing at risk.

## Correction: paragraph numbers restart at each division

**This revises the earlier conclusion that paragraph number alone is a valid join key.**

Dīgha vol. 1 contains a single vagga, so its numbering runs continuously 1–559 and
appeared to be volume-unique. It is not. Numbering restarts at each major division:

- Saṁyutta vol. 1 — 1 restart: Sagāthāvagga runs 1–271, then Nidānavagga begins again at 1
  (printed p. 243).
- Aṅguttara vol. 1 — 4 restarts, one per nipāta.
- Khuddaka verse — 14 restarts, since the volume bundles several independent works.
- Vinaya — 3; Abhidhamma — 2; Dīgha — 0.

So the citable key is **(division, paragraph)**, not (volume, paragraph). Cross-layer
linking still works — the commentary follows the same divisions — but the identifier
needs the division component, and any URL scheme or link table must carry it. Building
on the volume-level assumption would have produced silent mislinks precisely where a
volume holds more than one division, which is most of the canon.

## Parser faults found and fixed

**Sutta headings were being counted as paragraphs.** `2. Nimokkhasutta` matches the
same pattern as a numbered paragraph. Dīgha concealed this because its sutta titles fall
in the running head and were consumed as page headers; in Saṁyutta, where suttas are
short and titles sit mid-page, it produced 560 spurious paragraphs. Now separated by
indentation and shape — which also yields the **sutta/vagga hierarchy** as a by-product
(829 headings in Saṁyutta vol. 1), a piece of work that was still outstanding.

**Verse lines were then caught as headings.** Metrical lines are short and centred like
titles. Distinguished by punctuation and quote marks.

## Still open

- **Aṅguttara shows 269 numbering gaps.** Probably the *peyyāla* abbreviations, where the
  edition elides repetitive series and skips numbers accordingly — but unverified. This
  needs checking before Aṅguttara is trusted.
- **Unparsed apparatus notes: 4–11% depending on volume** (Khuddaka worst at 83/1254 and
  79/691). These are notes where neither a variant nor a cross-reference was recognised.
  Needs a sample review to see whether they are genuinely different note types or
  patterns the regex misses.
- **Abhidhamma has almost no apparatus** — 45 rule pages of 325, 69 notes, no
  cross-references at all. Consistent with the nature of the text, but worth confirming
  it is not an extraction failure.
- Footnote markers in the body are still not joined to their apparatus entries.
- No orthographic validator yet, so no erratum candidate list.
