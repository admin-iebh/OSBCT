# The Vimānavatthu-aṭṭhakathā quotes first and comments after — and every link lands on the quote

**Found 2026-08-09, with the reader, reading the printed page and the rendered
reader together.** Measured at build `92157e0692e0`. **Nothing was changed. No
link was moved, no rule was written into the pipeline.**

---

## 1. What the book does

`27KhuA08` (Vimānavatthu-aṭṭhakathā) does not proceed verse-by-verse. For each
vimāna it prints, in this order:

1. **unnumbered prose** — the *nidāna*: `Sattatantiṁ sumadhuranti Guttilavimānaṁ.
   Tassa kā uppatti? Bhagavati Rājagahe viharante āyasmā …` (idx 460, p.125);
2. **a run of the canon's verses, reprinted in full and under the canon's own
   numbers** — 327, 328, 329, 330 … 613, 614, 615, then 617, 618 (idx 461–510,
   pp.127–133);
3. **the comments, restarting at the same numbers** — 333, 334, 341, 373, 381,
   389, 397, 405, 413, 437, 445, 477, 517, 525, 557, 565, 573, then 617, 618
   (idx 511–529, pp.133–134);

and then begins again with the next vimāna. Measured over the whole volume:

    1,480 paragraphs
       98  unnumbered prose (the nidānas)
      620  QUOTE  — the paragraph reprints the canon verse
      762  gloss
      106  points where the paragraph number DECREASES inside the volume

The two kinds are easy to tell apart once you look, and impossible to tell apart
from the number alone:

    27KhuA08 #467  p.130   333. “Vatthuttamadāyikā nārī, Pavarā hoti naresu nārīsu.
                                Evaṁ piyarūpadāyikā manāpaṁ, Dibbaṁ sā labhate
                                upecca ṭhānaṁ.
    27KhuA08 #511  p.133   333. Tattha vatthuttamadāyikāti vatthānaṁ uttamaṁ
                                seṭṭhaṁ, vatthesu vā bahūsu uccinitvā gahitaṁ …

The first is the edition quoting the canon back. The second is the commentary.
**Both are numbered 333.**

## 2. What the reader does with them

It links to the first one. Measured in `site/reader/linksk/19Khu02.links.json`:

    canon ord 317 (n=333)  ->  27KhuA08#467    the QUOTE
    canon ord 413 (n=618)  ->  27KhuA08#510    the QUOTE
    canon ord   0 (n=1)    ->  27KhuA08#4      the QUOTE   (gloss at #11, p.8)

So a reader who turns on the Aṭṭhakathā band at `19Khu02` ¶333 is shown the verse
he has just finished reading, set as prose, and the comment on it is seven, or
eighty, or two hundred paragraphs further on with nothing pointing at it.

**This is not a display problem.** It was carried on the to-do list as one — "the
verbatim repeat, 5,376 of 22,527" — and the fix was imagined as hiding or
styling the duplicate. The duplicate is the *link target*. Hiding it would have
hidden the only thing the link reaches.

Corpus-wide, over `site/reader/linksk/`:

    32,504  direct links examined
     4,956  land on a paragraph whose text IS the canon paragraph's (15.25%)
        17  volume pairs affected, every one a Khuddaka verse work

4,956 against 5,376 known verbatim repeats means **nearly every repeat in the
corpus is a live link target**.

## 3. Why there is no corpus-wide rule, and why we did not write one

The obvious rule — *if the target is a re-quotation, move the link to the next
paragraph with the same number* — fails on this volume's own numbers.

**The offset is not constant.** Over the 301 quote→gloss pairs in `27KhuA08`
where a same-numbered gloss exists at all:

    offset  1  2  3  4  5  6  7  8  9 10 11 12 13 15 17 18 19 20 22 23 24 25 26 38 39 44
    pairs   6 30 30 18 28 42 33 26 16 12  3  6  7  3  3  1  2  2  3  5  9  8  3  2  1  2

Twenty-six distinct offsets, from 1 to 44.

**And half the quotes have no gloss at all.** 620 quotes, 301 with a
same-numbered gloss after them. The edition simply does not comment on every
verse — the same silence recorded elsewhere as `uttānatthāneva`, "these are
self-evident". A rule that moves the link forward would, for those, move it onto
the *next vimāna's* material.

**Other books do not even have the same shape.** Four of the seventeen affected
pairs have **zero** same-numbered glosses by this test — `23Khu06 → 42KhuA23`
(755 links on a quote), `19Khu02 → 30KhuA11` (668), `23Khu06 → 41KhuA22` (381),
`19Khu02 → 31KhuA12` (320). `31KhuA12` is the pair the older handoff already
documented by hand — ord 3294 → 207 where the gloss is 210 — so the gloss IS
there, three paragraphs on, carrying a different number. The test cannot see it.
Per-book table: `claude/link_targets_land_on_the_requotation.md`.

> **The reader, 2026-08-09: "how the Commentary and Subcommentary are related to
> the Pāḷi has to be taken one book at a time."** The numbers above are that
> statement in figures. This is the same wall as
> `claude/paragraph_numbers_are_not_a_key.md`: a structure that looks uniform
> from the number is not uniform in the book.

## 4. What a fix for THIS book would need

Stated so the next session can start, not as a decision:

* **Classify each numbered commentary paragraph as quote or gloss**, by comparing
  its text against the canon paragraph it claims — not by its number, and not by
  its position. The classification above did exactly this and is cheap.
* **Link the canon paragraph to its gloss where one exists**, and where none
  exists say so — the edition's silence is information, and turning it into a
  link to the quote hides it. Compare the existing `not_commented` treatment.
* **Keep the quote reachable**, since it is the edition's own text: it belongs in
  the commentary volume's own stream, where it already is.
* **Gate it before changing it.** `pipeline/check_links.py` is the ratchet; a new
  assertion should fail on the current build — at `19Khu02` ¶333 → `27KhuA08#467`
  — before anything moves.

## 5. Also true, and separate

The band flattens the quoted verse to prose. `reader2.html:1932` sets
`asSpine = kind==='canon' || !!(opts&&opts.spine)` and the verse branch at :2153
runs only when that is true, so a commentary paragraph drawn as a band under the
canon never takes it — the comment at :1929 says this deliberately. Rendered and
confirmed: the band block for `19Khu02` ¶618 has zero child `<div>`s while the
canon above it has three lines. `verse/27KhuA08.json` already holds the pādas.
That is the standing item *"the verse branch for band blocks"*, and it is a
smaller thing than this one.

## 6. How this was found, which is the part worth keeping

Three wrong answers preceded it, all mine, all of the same kind:

1. a mockup with **fabricated Pāḷi** in it, because I wanted an illustration and
   did not go and read one;
2. "the reader flattens the verse", inferred from a JSON `text` field — killed by
   the reader's screenshot, because line breaks come from `verse/`, not from
   `text`;
3. a classifier that keyed the canon by paragraph number and so compared against
   the wrong verse — **the very failure this project already has a note about**.

The finding arrived only when the reader described what the book actually does,
in one paragraph, from having read it. Every measurement here was written to
check *his* description, and each one confirmed it.

> **THE STRUCTURE OF A BOOK IS NOT DERIVABLE FROM ITS NUMBERS. ASK SOMEONE WHO
> HAS READ IT, THEN GO AND MEASURE WHAT THEY SAID.**
