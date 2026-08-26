# The section names the edition prints and the corpus does not carry

**Measured 2026-08-26, and APPLIED to `19Khu02` the same day — §7.**
Instrument: `pipeline/extract_sections.py`. Gate: `pipeline/check_sections.py`.
§§1–6 were written before the write and say "nothing has been written"; they are
kept as they were and §7 is what supersedes them.

---

## 1. How this was found, and why the first question was wrong

A link repair moved one link onto a target that happened to have a section name,
which made a name comparison possible for the first time — and it disagreed.
Chasing that: `name_at` carried the last `sutta` field forward **across book
boundaries**, so the Petavatthu's first 340 paragraphs in `19Khu02` answered to
a *Vimānavatthu* section name. Corpus-wide, **5,616 paragraphs in 44 volumes**
sit before their own book's first section name.

I asked the reader whether such a paragraph should fall back to the vagga name
or show nothing. **Both answers are wrong.** The edition prints a section name
there. Printed page (`pali-unicode/19Khu02.pdf` p.143), read:

    Khuddakanikāya
    Petavatthupāḷi
    Namo tassa Bhagavato Arahato Sammāsambuddhassa.
        1. Uragavagga
      1. Khettūpamapetavatthu
    1. Khettūpamā arahanto, dāyakā kassakūpamā. ...
    3. Idheva kusalaṁ katvā, ...
        Khettūpamapetavatthu paṭhamaṁ.
      2. Sūkaramukhapetavatthu
    4. Kāyo te sabbasovaṇṇo, ...

`19Khu02` holds **3,660 paragraphs and 3 distinct `sutta` values** — one of
which is a closing marker, `Suttapetavatthu ekādasamaṁ.` This is not a display
fallback question. **It is missing extracted data.**

## 2. The instrument

`pali-unicode/*.pdf` — the volumes this project already repaired — return clean
Unicode from `pdftotext`. No legacy decoding is involved.

A heading and a verse are both numbered lines. A heading is short, has no comma,
does not end in a full stop, and ends on a section word (`-vatthu`, `-vagga`,
`-sutta`, `-gāthā`, `-nipāta`, …). A verse is long and punctuated.

**Two things make it work, and both were learned by getting them wrong first:**

* **The running head must be dropped.** Every page opens with the nikāya or book
  name. `1. Uragavagga` at the top of forty pages reads as forty headings.
* **EVERY HEADING MUST ANCHOR, and that is what keeps the Mātikā out.** The front
  matter lists every section name in order; read as headings, they place hundreds
  of sections on page 16. A Mātikā entry is followed by another Mātikā entry; a
  body heading is followed by its first verse. Requiring that a verse follows —
  and taking its number as the anchor — separates the two sources cleanly. It is
  not a tidiness check; it is the discriminator.

## 3. Self-verification, which is the number to trust

`--check` walks the headings in order and resolves each anchor against the
corpus. On `19Khu02`:

    501 headings, 501 anchors resolved IN ORDER,
    0 restarts, 0 unresolvable, 0 going backwards

and the first placements match the printed page exactly — Paṭhama-, Dutiya-,
Tatiya-, Catuttha-pīṭhavimānavatthu on ¶1, 8, 15, 23, which is what p.1 of the
Vimānavatthu prints.

## 4. The extent — a LOWER BOUND, and it must not be quoted as the defect

Over the 40 canon volumes: **4,279 headings found, 1,301 of them absent from the
corpus.** Worst:

| volume | paragraphs | printed | in corpus | missing |
|---|---:|---:|---:|---:|
| 19Khu02 | 3,660 | 465 | 3 | **464** |
| 28Khu11 | 261 | 231 | 0 | **231** |
| 18Khu01 | 1,869 | 317 | 235 | 98 |
| 03Vin03 | 490 | 56 | 0 | 56 |
| 05Vin05 | 519 | 55 | 0 | 55 |
| 14Sam03 | 598 | 484 | 484 | 53 |
| 26Khu09 | 405 | 57 | 8 | 53 |

**But the instrument is blind wherever headings are not numbered lines ending in
a section word**, and the table says so on its face:

    20Khu03   4,461 paragraphs,  1 heading found   -- Apadāna; certainly hundreds
    29Abhi01  1,780 paragraphs,  0 found
    36-40Abhi        0 found in any of the five
    06Di01    the corpus already has 14 where this finds 1

Those are not volumes where the edition prints no sections. They are volumes
this reads badly. **1,301 is a floor.** Do not write from this script into any
volume whose `--check` does not resolve cleanly.

## 5. What has NOT been done, and the decision it needs

**Nothing has been written into the corpus.** Writing 498 section names into a
served volume changes what a reader sees on every page of it, and it feeds
`name_at`, the nav tree and the ☰ Contents. That deserves its own gate, run red
first, and a printed-page spot check of a sample — the same protocol as the link
repairs, not a bulk write on the strength of a resolution count.

Open, and the reader's:

1. **Apply to `19Khu02` alone first?** It is the worst volume, it resolves
   501/501, and one volume is the unit this project has settled on.
2. **What happens to the vagga heading**, which the extractor also picks up
   (`1. Uragavagga`)? It is a real printed heading at a different level. The
   corpus has a separate `vagga` field already populated — so the vagga rows are
   probably a cross-check on that field rather than something to write.
3. **The three headings already stored as numbered PARAGRAPHS** in `19Khu02` —
   `17. Valliphaladā yikāvimānavatthu (6)` at ord 388, and two more — collide
   with real paragraph numbers and broke a classifier earlier today. They should
   be removed from the paragraph stream when the names are written properly, not
   left to be both.

## 6. Noticed while verifying, not chased

`19Khu02` ord 1034 records `pdf_page: 142`, but the page carrying its text is
**143** — page 142 renders blank. One sample only; the Aṭṭhakathā volumes
checked today matched exactly (`27KhuA08` #467 says 137 and page 137 carries
it). So this is not general, but `pdf_page` for `19Khu02` is worth a check
before anything relies on it.

---

## 7. APPLIED to 19Khu02, 2026-08-26 — and what it cost the name-match gate

`pipeline/check_sections.py` was **run red first** on all four of its cases:

    FAIL  19Khu02#0    is None, the edition prints 'Paṭhamapīṭhavimānavatthu'  p.1
    FAIL  19Khu02#291  is None, the edition prints 'Pallaṅkavimānavatthu'      p.45
    FAIL  19Khu02#1034 is None, the edition prints 'Khettūpamapetavatthu'      p.143
    FAIL  19Khu02 carries a section name with a parenthesised index

Then written: **476 section names over 3,660 paragraphs; distinct 3 → 444.**
All four cases green, and the write is idempotent.

**The vagga rows were NOT written**, and answering the reader's second question:
they are a cross-check on the `vagga` field, which already exists and already
agrees on **24 of 25**. The one disagreement is a real find and is reported, not
repaired — ord 483 carries `'Itthivimāna      4. Mañjiṭṭhakavagga'`, two headings
glued together with the index left in, where the edition prints
`Mañjiṭṭhakavagga`.

### name-match fell, 76.442 → 76.141, and the reason matters

**Because the fix is half-applied, and half is worse than none for this measure.**
The canon side now carries the section names the edition prints; the commentary
side still carries the old defect. So the comparison went from wrong-against-
wrong to right-against-wrong:

    19Khu02 ¶1381  canon 'Kaṇṇamuṇḍapetivatthu'  (correct, now)
                -> 28KhuA09#503 'Suttapetavatthuvaṇṇanā'  (still the stale
                   carried-forward name — 28KhuA09 has 1 distinct sutta value)

86 pairs in `19Khu02` are now checkable where far fewer were; 78 of them
disagree, and most of those disagreements are the commentary side being wrong.

**The baseline was re-recorded rather than the change reverted**, because the
canon names are verified against three printed pages and are what a reader sees,
while name-match is a proxy that is currently comparing a repaired side against
an unrepaired one. **It should recover — and rise above where it started — when
the commentary volumes get their section names.** If it does not, that is a
finding and this paragraph is the thing to hold it to.

### The commentary extractor does not exist, and `--write` now refuses

The obvious move — point the same reader at `atthakatha-unicode/` — was tried
and **fails**:

    27KhuA08   14 headings for a 1,480-paragraph volume, 1 resolving backwards
    28KhuA09    6 headings, and `Pañcaputtakhādakapetivatthuvaṇṇanā` anchored
                to ¶1, which is `Khettūpamā arahanto` — plainly wrong

The commentaries name sections `...vaṇṇanā` and do not number the heading line
the way the canon does, so a number-anchored reader has nothing to hold. Adding
`vaṇṇanā` to the pattern was not enough. `write()` now refuses any volume
outside `pali-unicode/`, and refuses any volume yielding fewer than one heading
per hundred paragraphs. **A commentary reader is the next piece of work in this
line, and until it exists the canon-side repair is deliberately incomplete.**

## 8. The commentary reader — 28KhuA09 done, 27KhuA08 refused

**Built 2026-08-26, after §7 recorded that it did not exist.**

**The difference is not the name, it is what follows the heading.** A canon
heading is followed by its first numbered verse, so the verse number anchors it.
A commentary heading is followed by the *nidāna prose* and there is no number in
sight for many lines. Printed p.9 of `28KhuA09`, read:

    Khettūpamapetavatthuvaṇṇanā niṭṭhitā.
    ─────
         2. Sūkaramukhapetavatthuvaṇṇanā
    Kāyo te sabbasovaṇṇoti idaṁ Satthari Rājagahaṁ upanissāya Veḷuvane ...

So the anchor is **text, not number**: take the prose line that follows and find
the corpus paragraph opening with it. `28KhuA09` 51/51 anchored, `27KhuA08`
83/83 — zero unmatched in both.

**AND THE MĀTIKĀ IS THE COMPLETENESS CHECK, which matters more than the count.**
A heading the body scan MISSES does not leave a gap. It leaves the previous
section's name spread over the missing one's paragraphs — **precisely the defect
being repaired, re-created by a partial repair.** So the body scan must find as
many headings as the front matter lists, or it must not write:

    28KhuA09   body 51, Mātikā 51   -> WRITTEN.  1 distinct name becomes 47
    27KhuA08   body 83, Mātikā 79   -> REFUSED

`27KhuA08` finds four MORE than the Mātikā lists, which is its own puzzle and is
not resolved here. Finding those four is the next step for that volume.

## 8a. The four were found, and the MĀTIKĀ READER was the thing that was wrong

**2026-08-26 (later the same day). `27KhuA08` is written: 84 section names, 1,480
paragraphs, distinct 0 → 83.**

The four extras were `Dāsivimānavaṇṇanā`, `Lakhumāvimānavaṇṇanā`,
`Paṭhamabhikkhādāyikāvimānavaṇṇanā` and `Dutiyabhikkhādāyikāvimānavaṇṇanā`. The
diff was one-sided from the start — four in the body with no Mātikā counterpart,
and **nothing in the Mātikā that the body lacked** — which is the shape of a
reader that is dropping entries, not of a body scan inventing them.

**All four are printed in the Mātikā.** Rendered and read, not inferred:

    p.ii   ...17. Kesakārīvimānavaṇṇanā
                  2. Cittalatāvagga
               1. Dāsivimānavaṇṇanā        }  a run of TWO, then the page ends
               2. Lakhumāvimānavaṇṇanā     }
    p.iii  ...  7. Uposathāvimānavaṇṇanā
             8-9. Niddā-suniddāvimānavaṇṇanā
              10. Paṭhamabhikkhādāyikāvimānavaṇṇanā  }  another run of two,
              11. Dutiyabhikkhādāyikāvimānavaṇṇanā   }  then a vagga line

**Two faults, and they are independent.** `matika()` kept a name only inside a
run of four or more consecutive matching lines — a proxy for "this is the front
matter" that fails wherever the printed list is interrupted, which it is at every
vagga heading and every page foot. And `NUM` was `^(\d+)\.`, which does not match
`8-9.`: the edition numbers a section covering two vimānas as a **range**. That
one broke the Mātikā run in half *and* made the section invisible to the body
scan as well.

So the true count is **84 on both sides**, exact set agreement, and the earlier
"body 83, Mātikā 79" was two instruments failing on the same line for different
reasons.

**§8's own rule is what saved this.** The Mātikā gate refused rather than
writing, and had it merely counted rather than refused, `Niddā-suniddā`'s nine
paragraphs would have gone out under `Uposathāvimānavaṇṇanā` — the defect being
repaired, re-created by the repair. **The completeness check earned its keep by
being wrong in the safe direction.**

### What was changed, and the controls

* `NUM` now reads `^(\d+)(?:-\d+)?\.` — first number captured, so callers still
  get an int.
* `matika()` is scoped to the pages carrying the running head `Mātikā` instead of
  to run length, falling back to the old rule if a volume has no such page.
* `pipeline/check_sections.py` gained the four cases, **run red first** — all
  four `is None` on the build as it stood — each read off a rendered page (p.82,
  p.106, p.107, p.108).

Controls, because a change to a shared pattern is a change to every volume that
uses it:

    19Khu02   re-run --write  ->  BYTE-IDENTICAL (837e72c1…), still 501/501
    28KhuA09  re-run --write  ->  BYTE-IDENTICAL (91ee6ad0…), still 51/51
    27KhuA08  written, then re-run  ->  idempotent (69fb0890…)
    pbreak    fresh derivation of 27KhuA08 == the file on disk, so the write
              touched nothing but the `sutta` field

`name-match` went **76.669 → 77.231%, over 18,582 links, up from 17,440** — more
pairs checkable and a higher share agreeing, the same shape §7 predicted and §8
measured. Baseline re-recorded; the old one is kept at
`pipeline/links_baseline.json.presections27`.

### Not a defect: `Ambavimānavaṇṇanā` twice

84 sections, 83 distinct names. The edition itself lists `Ambavimānavaṇṇanā` in
two vaggas — Mātikā entries 45 and 78, body headings `8.` and `5.`, landing on
ord 763 and ord 1254, two different stories. Checked before it was written off,
because a repeated name is exactly what a misplacement looks like.

### Still open on this volume

The three §5 items are untouched, and one new question: `matika()`'s page
scoping keys on the literal string `Mātikā` in a running head. It held on the two
commentary volumes tried. **It has not been tried on the other 50**, and a volume
whose front matter is headed differently falls back to the run-length rule —
which will undercount in exactly the way described above and refuse. Refusing is
safe; being surprised by it is not.

### The prediction held

§7 said name-match should recover and rise above where it started once the
commentary side was done. Measured:

    76.442  before any section work
    76.141  canon side written, commentary side still wrong
    76.670  both written                     over 17,440 links, up from 16,669

More pairs are checkable and more of them agree. That is the shape a real repair
makes, and it is the reason §7's baseline drop was recorded rather than reverted.
