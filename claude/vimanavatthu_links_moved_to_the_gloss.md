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
everywhere.** It records `19Khu02 → 27KhuA08` as **500** links on a repeat with
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
