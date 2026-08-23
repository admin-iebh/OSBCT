# Links landing on the commentary's re-quotation, per book

**Re-measured 2026-08-23** with `pipeline/measure_requotation.py`. The
2026-08-09 table this replaces is kept in §5, because the way it was wrong is
worth more than the numbers it gave.

**Nothing here is permission to write a corpus-wide rule.** How a commentary
relates to its canon is a per-book question (the reader, 2026-08-09), and the
table below is now precise enough to show that it is a question with at least
**three different answers**.

---

## 1. The three shapes

**Shape A — the commentary reprints, then comments in a SEPARATE paragraph
under the same number.** Vimānavatthu, Petavatthu, Buddhavaṁsa, most Jātaka
volumes. Two paragraphs bear the number; the placer takes the first. **This is
the repairable shape**, and it is what `19Khu02 → 27KhuA08` was.

**Shape B — the commentary reprints and comments in the SAME paragraph.**

    31KhuA12 #8   4. “Tisse sikkhassu sikkhāya, ... anāsavā”ti– gāthaṁ abhāsi.
                  Tattha tisseti tassā ālapanaṁ.  Sikkhassu sikkhāyāti ...

The link already lands on the commentary. **Nothing to move, nothing wrong.**
7,437 → this accounts for a large part of what a naive measure calls a defect.

**Shape C — verses run in a block and the comment is COLLECTIVE, after the
last of them.** Therīgāthā, Theragāthā, and two Jātaka volumes. Verified on
the printed page, Therīgāthā-aṭṭhakathā p.13: verses 7, 8, 9, 10 printed in a
run, then `gāthāyo abhāsiṁsu.` and then `Tattha **yuñjassu dhammehī**ti …`
glossing verse **5**, then verse 6, then 7, then 8 — one gloss covering the
whole block, and **its paragraphs are unnumbered**. No same-number test can
ever find them. That is why these pairs report zero movable links, and it is
not a defect in the measurement — it is the book.

## 2. The corrected table

`direct` = direct links examined. `on reprint` = the link lands on a paragraph
that reprints the canon text **and stops there**. `movable` = and a comment
exists elsewhere under the same number, so there is somewhere to move it to.

| canon | layer | direct | on reprint | movable | shape | canon book |
|---|---|---:|---:|---:|:--:|---|
| 23Khu06 | 42KhuA23 | 1645 | 1103 | 1 | **C** | Jātakapāḷi |
| 19Khu02 | 30KhuA11 | 1014 | 887 | 1 | **C** | Theragāthāpāḷi |
| 23Khu06 | 40KhuA21 | 1220 | 823 | **765** | A | Jātakapāḷi |
| 22Khu05 | 39KhuA20 | 1130 | 645 | **590** | A | Jātakapāḷi |
| 21Khu04 | 34KhuA15 | 964 | 601 | **511** | A | Buddhavaṁsapāḷi |
| 19Khu02 | 28KhuA09 | 703 | 592 | **348** | A | Petavatthupāḷi |
| 23Khu06 | 41KhuA22 | 774 | 528 | 0 | **C** | Jātakapāḷi |
| 19Khu02 | 31KhuA12 | 520 | 433 | 0 | **C** | Therīgāthāpāḷi |
| 19Khu02 | 27KhuA08 | 937 | 399 | 0 | A | **REPAIRED 08-23** |
| 22Khu05 | 38KhuA19 | 793 | 310 | **310** | A | Jātakapāḷi |
| 22Khu05 | 40KhuA21 | 335 | 204 | **203** | A | Tiṁsanipāta |
| 18Khu01 | 21KhuA02 | 119 | 112 | 9 | ? | Dhammapadapāḷi |
| 21Khu04 | 35KhuA16 | 312 | 112 | **109** | A | Cariyāpiṭakapāḷi |
| 20Khu03 | 33KhuA14 | 357 | 100 | **100** | A | Therāpadānapāḷi |
| 18Khu01 | 22KhuA03 | 309 | 95 | 1 | ? | Dhammapadapāḷi |
| 22Khu05 | 37KhuA18 | 343 | 88 | **82** | A | Jātakapāḷi |
| 19Khu02 | 29KhuA10 | 251 | 67 | 1 | **C** | Theragāthāpāḷi |
| 40Abhi12 | 50AbhiA03 | 513 | 32 | 32 | ? | Tikatikapaṭṭhāna |
| 27Khu10 | 21KhuT01 | 212 | 30 | 30 | ? | Nettipāḷi |

Thirty pairs carry ten or more; the rest are single figures and are in the
script's own output.

    TOTAL   21,621 direct links   7,437 on a bare reprint   3,369 movable

**The 08-23 repair validates the instrument.** Run against the pair it already
fixed, `19Khu02 → 27KhuA08` now reports **436 already on the comment**, 399
solo reprints the edition never comments on, 73 of shape B, 29 already the
comment — and **0 movable**. Nothing left to do there, which is the right
answer.

## 3. What the count rests on

One threshold is unavoidable: when a canon paragraph has exactly **one**
candidate there is nothing to compare it against, and the call has to be
absolute. `SOLO = 0.60`. **Only 88 paragraphs in the whole corpus sit within
±0.15 of it** — so almost none of the 7,437 depends on where it is set. That
number is printed on every run; if it ever grows, the threshold has started to
matter and should be replaced rather than tuned.

Everything else is decided by a **relative** test with no threshold: of the
commentary paragraphs bearing this number, which is less like the canon
paragraph?

## 4. Where to go next

* **`19Khu02 → 28KhuA09`** (Petavatthu, 348 movable) — same canon volume as the
  repaired pair, same shape, and the most likely to go the same way. This is the
  next one to do.
* Then the three big Jātaka pairs — `40KhuA21` 765, `39KhuA20` 590,
  `38KhuA19` 310 — and `34KhuA15` 511 (Buddhavaṁsa).
* **SHAPE C — DECIDED 2026-08-23 BY THE READER: LEAVE IT AS IT IS.**
  Shown the printed Therīgāthā page — verses 7, 8, 9, 10 in a run, then
  `gāthāyo abhāsiṁsu.` and the collective gloss — his instruction was:
  *"If in the PDF is like this, keep it as it is."*

  So `42KhuA23` 1103, `30KhuA11` 887, `41KhuA22` 528, `31KhuA12` 433 and
  `29KhuA10` 67 — **about 3,000 links — are NOT a defect and are not to be
  repaired.** The reader meets the book as the edition set it: the verses in
  their run, the comment after the last of them. Pointing each verse at a
  collective gloss would impose a structure the edition does not print, which is
  principle 3 — never silently correct the edition — reaching the link layer.

  This closes the largest single block of "on a reprint" counts in §2. They stay
  in the table as a **measurement**, not as a backlog.

  *(Recorded as an interpretation of one sentence. If what was meant was
  narrower — keep the verse run intact but still let a verse reach its gloss —
  say so and it can be reopened; nothing has been built either way.)*
* The `?` rows have not been characterised. Do that before planning them.

Each pair still gets its own named assertion in `check_links.py`, run red
first, and its own printed-page verification. The measurement says where to
look; it does not say what is true.

## 5. The superseded table, and how it was wrong

Measured 2026-08-09 at build `92157e0692e0`, by comparing whole strings. It
reported **4,956** links on a repeat across 17 pairs, and for
`19Khu02 → 27KhuA08`: 500 on a repeat, 267 same-numbered glosses.

Three faults, in increasing order of how much they cost:

1. **It kept the canon's inline footnote-marker digits** — `malyadhare1`,
   `Imāsāhaṁ1` — which the commentary's reprint does not carry. That alone
   called **168 verbatim reprints different** in one pair.
2. **It compared whole strings**, so a reprint with prose appended
   (`… — Ayaṁ gāthā …`) scored 0.53 and was missed.
3. **It could not see shape B or shape C at all.** It had no way to ask whether
   a paragraph reprints *and then comments*, so it could not tell "this link is
   wrong" from "this link is already right" — opposite facts. The four rows it
   reported as `0` same-n glosses were read as *"the test cannot see the
   gloss"*; the truth is that those books do not number their glosses, and the
   right conclusion was not "measure harder" but "this is a different book".

> **The 08-23 instrument made the same class of mistake for an afternoon**, and
> it is recorded in `measure_requotation.py` at `tail()`: reading only the
> paragraph's opening, it reported 514 links on a reprint for `31KhuA12` when
> every one of them already lands on the commentary three words further into
> the same paragraph. It was caught by reading the book, not by checking the
> code. **The measure keeps failing in the same direction — it sees the shape it
> was built for and calls everything else that shape.**
