# Links moved off the reprint and onto the comment — 27KhuA08, then 28KhuA09

> **2026-08-23, later the same day: the second pair is done too.**
> `19Khu02 → 28KhuA09` (Petavatthu-aṭṭhakathā), **350 links moved**, both named
> cases run red first and verified on printed pages 7, 161 and 191.
>
> **28KhuA09 mixes the shapes, which 27KhuA08 did not.** 101 of its links
> already land on a paragraph that reprints the verse *and then comments in the
> same paragraph* — correct as they stand. `relink_requotation.py` gained the
> `tail()` guard for exactly this, and without it those 101 correct links would
> have been moved off the commentary and onto nothing better. See §9.
>
> Two further findings came out of it, §10 and §11. One of them —
> **5,616 canon paragraphs carrying the previous book's section name** — is
> larger than the repair that exposed it.

---

# 19Khu02 → 27KhuA08: 437 links moved off the reprint and onto the comment

**Done 2026-08-23.** The first of the seventeen pairs in
`claude/link_targets_land_on_the_requotation.md` is repaired. One book, no
corpus-wide rule, gated red first.

Script: `pipeline/relink_requotation.py` (dry run by default).
Gate: `pipeline/check_links.py`, the `REQUOTE_CASES` block.

---

## 1. What was wrong

`27KhuA08` prints each vimāna as nidāna prose → **the canon's verses reprinted
under the canon's own numbers** → **the comments, restarting at the same
numbers**. Both bear the number, so the placer took the first every time. A
reader who opened the Aṭṭhakathā band at `19Khu02` ¶333 was shown the verse he
had just finished reading; the comment sat 44 paragraphs on with nothing
pointing at it. Found 2026-08-09 with the reader —
`claude/vimanavatthu_atthakatha_quotes_then_glosses.md`.

## 2. The gate was made to fail first

Two cases, both read off the printed page before either was asserted:

    FAIL  19Khu02#317 (¶333) -> 27KhuA08#467 : lands on the reprint
    FAIL  19Khu02#0   (¶1)   -> 27KhuA08#4   : lands on the reprint

They are **assertions, not a baseline measure**, and `--record` refuses to
absorb them — a defect that can be recorded as the standard is not a gate.

## 3. Why there is no text threshold — every obvious test was tried and failed

This is the part worth keeping, because all three look right until measured.

| test | fails because | example |
|---|---|---|
| whole-string similarity | the commentary reprints the verse **and appends prose** | a real quote scores 0.53 |
| prefix containment | canon and commentary **disagree on single words** | `padmaṁ`/`paddhaṁ`, `Upapajjati`/`Uppajjati` — a real quote breaks at 50% |
| opening similarity | **fails in both directions** | a quote abridged by peyyala scores 0.35; **a gloss opens by quoting its own lemma** and scores 0.36 |

Positional classification fails too. "Everything after the first
number-decrease is the gloss run" is only **78.2%** right against the decisive
text cases, because a vimāna alternates quote-run and gloss-run more than once —
18 blocks hold two decreases, one holds seven.

**What works is a RELATIVE question, with no threshold at all.** For a canon
paragraph numbered *n*, take the commentary paragraphs also numbered *n* and ask
only: which is *less* like the canon paragraph? In this book that is decisive —
of the 435 canon paragraphs with two candidates, the smallest separation is
**0.30**, and 416 separate by 0.5 or more. `MIN_SEP = 0.15` exists to stop a
future book being decided by a coin toss unnoticed; nothing here approaches it.

**And one correction to the comparison itself, which is where the earlier
measurement went wrong: the canon carries footnote-marker digits INSIDE the
word** — `malyadhare1`, `Imāsāhaṁ1` — and the commentary's reprint does not.
A comparison that keeps them calls **168 verbatim reprints different**.

## 4. What was done, and what was deliberately not

    MOVE quote -> comment                             437
    one candidate: the quote, no comment printed      470   LEFT ALONE
    number absent from the commentary                  92   left alone
    one candidate: already the comment                 28
    no direct link to move                              6
    already on the comment                              1

**The 470 are the edition's silence and were not touched.** The commentary does
not gloss every verse — printed page 130 shows 341, 349, 357, 365 quoted and
page 133 comments on 341 but never on 349, 357 or 365. Inventing a target for
those would manufacture a commentary that was never printed.

Each moved record carries its provenance and its former target:

    {"key": "27KhuA08#511", "state": "direct", "n": 333,
     "by": "requotation", "was": "27KhuA08#467"}

## 5. Verified against the printed page, not the corpus

Four pages rendered from `atthakatha/27KhuA08.pdf` and read:

* **p.130** — ¶333 set as verse inside the run 330–336, 341, 349, 357, 365. The reprint.
* **p.133** — the run ends at 618, then `333. Tattha **vatthuttamadāyikā**ti …` restarts. The comment.
* **p.104** — the decisive one for the closest call. ¶233 appears **twice on the same page**: `233. “Uposathāti maṁ aññaṁsu, Sāketāyaṁ upāsikā -pa-.` in the verse run, and `233. Tattha **Uposathāti maṁ aññaṁsū**ti …` below it. The quote is peyyala-abridged and the gloss opens on its lemma — both failure modes of §3 visible in one place, and the relative test gets it right.
* **p.333** — ¶1287 as `Tattha **dunnikkhittaṁ mālan**ti …`, the new target.

## 6. Gates

    check_links.py       n-match 55.93% (unchanged — the gloss carries the same
                         number), name-match 76.13% (unchanged),
                         reachable 28203 -> 28210, both named cases ok
    negative control     fires: n-match 55.927 -> 4.091
    check_concordance.py no measure regressed
    build_rev.py         re-run to convergence; direct forward links with no
                         reverse entry: 0

Baseline re-recorded at `reachable 28210`, so the repair is now the floor.

---

## 7. Three things found on the way, none of them repaired

Reported under principle 5, with their extent.

**7a. The 08-09 worksheet understates this pair, and by the same cause
everywhere.** — **RE-MEASURED THE SAME DAY; the worksheet is rewritten and the
answer was bigger than "the numbers were low": the pairs fall into three
different book shapes, and only one of them is repairable. See
`claude/link_targets_land_on_the_requotation.md` §1.** The original note
follows. It records `19Khu02 → 27KhuA08` as **500** links on a repeat with
**267** same-numbered glosses found. Measured with footnote-marker digits
stripped, it is **907** links landing on a reprint (437 with a gloss to move to,
470 without) and **435** same-numbered gloss pairs. The whole-string test also
missed the peyyala-abridged and prose-appended quotes. **The other sixteen rows
of that table are understated for the same reason and should be re-measured
before any of them is planned against.** In particular the four rows reading
"same-n gloss found: 0" — `23Khu06 → 42KhuA23`, `19Khu02 → 30KhuA11`,
`23Khu06 → 41KhuA22`, `19Khu02 → 31KhuA12` — are the ones most likely to be
wrong, and `31KhuA12` is already known by hand to have a gloss the test could
not see.

**7b. The reverse maps had drifted again, independently of this work.** Running
`build_rev.py` against the *untouched* forward maps already changed three
volumes: `32KhuA13` **+33** entries, `26KhuA07` −1, `27KhuA08` −1, and two more
volumes changed a winner without changing a count (`28KhuA09` ord 566 was
attributed to `20Khu03#386`, the forward maps say `19Khu02#1420`;
`41KhuA22` had five of the same kind). This is exactly the fault
`build_rev.py` was written for on 2026-08-03: a link repair that is not followed
by a rev rebuild leaves the band side answering with the old target. **The
rebuild has been applied**, so it is fixed — but it means link repairs between
08-03 and now did not all rebuild, and the gate suite never noticed. A check
that rev is derivable from the forward maps would be cheap and is not written.

**7c. A stray link across books.** `19Khu02` ¶199 of **Petavatthupāḷi** carries a
direct link into `27KhuA08#313`, the *Vimānavatthu* commentary. It is excluded
from this repair by the book filter and is left as it was. One instance seen; not
counted corpus-wide.

**Also noted, not acted on:** the commentary and the canon disagree on single
words at several places — `27KhuA08#510` reads `yatta` where `19Khu02` ¶618 reads
`yattha`; `#48` reads `Paddhacuṇṇā` against `Padmacuṇṇā`; `#98` `paddhaṁ` against
`padmaṁ`. These are between two volumes of the same edition and belong to the
errata register's question, not to this one. Not entered — they have not been
checked against the printed page of *both* volumes.

## 8. What is next in this line

The remaining sixteen pairs, one book at a time, **after** 7a is re-measured.
`19Khu02 → 28KhuA09` is the natural next one: same canon volume, offset 3, and
221 same-numbered glosses by the old undercounting test, so probably many more.
The four "0 glosses found" pairs are a different shape and need a reader's
description of what those books do before any measurement will mean anything.

---

# Part two — 19Khu02 → 28KhuA09, Petavatthu-aṭṭhakathā

## 9. Same shape, but not purely — and the guard that mattered

Printed page 7 shows it plainly: the verse run ends at ¶3 with
`imā gāthā abhāsi.` and the commentary restarts `1. **Tattha khettūpamā**ti
khittaṁ vuttaṁ bījaṁ tāyati …`. Page 161 the same: `397. **Akammakāmā**ti
sādhūhi akattabbaṁ kammaṁ akusalaṁ kāmentīti …`. Shape A, as in 27KhuA08.

    MOVE quote -> comment                                    350
    one candidate: the quote, no comment printed             244
    number absent from the commentary                        107
    reprints AND comments in one paragraph — correct as is   101
    no direct link to move                                     8
    already on the comment                                     5
    one candidate: already the comment                         3
    tie on opening, broken by the tail                         2

**The 101 are the point.** 27KhuA08 is pure shape A, so the question never
arose there. 28KhuA09 mixes: many of its paragraphs reprint the verse and then
comment *in the same paragraph*, which `opening()` scores 1.0 — identical to a
bare reprint. Moving those would have taken 101 links off the commentary. The
`tail()` guard, written for `measure_requotation.py` an hour earlier after the
same mistake was made about `31KhuA12`, is what stopped it.

> **A repair script that is right for one book is not thereby right for the
> next.** The guard was not added because 28KhuA09 was inspected and found to
> need it; it was added because the *measure* had already been caught. Had the
> order been reversed, 101 correct links would have moved and every gate would
> have stayed green.

**Two cases were decided by a tie-break that is worth recording.** At canon
¶486 and ¶760 both candidates *open* with the verse, so `opening` cannot
separate them and `MIN_SEP` refused the call. The difference is length: 13
words against 41. Printed page 191 shows why — inside the gloss run the edition
re-quotes the verse in full (`Tena vuttaṁ—`, then verse 486 set as verse) and
then comments `**Tattha paṭihatā**ti paṭihatacittā …`. So the second candidate
is a re-quotation *and* the comment. The tie is broken on `tail`, and only when
exactly one of the two continues past the verse.

## 10. The ratchet fired, and it was right to

After the move, two aggregates fell:

    name-match   76.126 -> 76.122   (one link)
    reachable    28210  -> 28209    (one paragraph)

Neither was waved through, and they turned out to be different in kind.

**`reachable` −1 is the arithmetic of the repair and is accepted.** 350 links
moved off reprints; some reprints lost their only referrer while the glosses
gained one. The reprint is still the edition's own text in the commentary's own
stream, where a reader reaches it by reading — it is simply no longer a link
target, which is what was intended. **But note the measure cannot tell this from
deletion**, which is what it exists to catch, so any future repair of this kind
must explain its −1 rather than re-record it.

**`name-match` −0.004 was not the repair at all.** It was one link becoming
*checkable* for the first time and immediately disagreeing — see §11.

## 11. NEW AND LARGER THAN THE REPAIR — 5,616 paragraphs answer to the wrong book's section name

`check_links.py:name_at()` carried the last `sutta` field forward, and **carried
it across book boundaries**. A book's opening paragraphs often carry no `sutta`
field at all:

    19Khu02  Petavatthupāḷi starts at ord 1034
             its first paragraph carrying a `sutta` field is ord 1374
             => ords 1034-1373, 340 paragraphs, answered with a
                VIMĀNAVATTHU section name

Ord 1371 — a Petavatthu verse — answered `Rasuttamadāyikāvimānavatthu (4)`.

Corpus-wide: **5,616 canon paragraphs in 44 volumes** sit before their own
book's first section name. Worst: `19Khu02` 678, `01Vin01` 399, `28KhuA09` 397,
`02ViT02` 318, `26VsmT02` 299, `25Khu08` 295.

**What this did to the measure.** `name_at` now stops at a book boundary and
answers `None` there, so the pair is not counted rather than counted wrongly.
The effect on the gate is not small:

    before   name-match 76.126%  of 20,784 links
    after    name-match 76.442%  of 16,657 links

**4,127 of 20,784 name comparisons — 19.9% — were being made against a section
name belonging to a different book.** The honest figure is *higher*, so the
measure had been understating itself; but it was also silently counting
agreements and disagreements that meant nothing either way. Baseline re-recorded
at the corrected figures.

**THE UNDERLYING DEFECT IS NOT REPAIRED, only stopped from being measured.** The
corpus still has 5,616 paragraphs with no section of their own, and **the reader
still shows them under the previous book's heading.** That is a nav/section
builder question and it is now the most substantial known defect on the list.
It was found only because a link repair moved one link onto a target that
happened to have a name.

## 12. Gates, part two

    check_links.py        n-match 55.93% unchanged; name-match 76.44% of 16,657
                          (measure corrected, see §11); reachable 28209;
                          all FOUR named cases ok
    negative control      fires: n-match 55.928 -> 4.085
    check_concordance.py  no measure regressed
    check_dimmed.js       PASS ; check_search.js all green
    build_rev.py          re-run; 0 direct forward links without a reverse entry
    stamp                 26a5cf36582c
