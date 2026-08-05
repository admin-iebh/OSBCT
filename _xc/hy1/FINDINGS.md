# The line-break hyphen is not a cause of class 2, and "a pāda never ends mid-word" is false

2026-08-05. Working record: `_xc/hy1/`. **No data touched, no builder changed.**
Instrument measured first, per the standing rule. HEAD at time of measurement `dcead251`
(one commit past the `0db4a917` named in the handoff; `dcead251` "changed files" is
34 files of `_xc/h1/` and `_xc/boldfid/` probe output, no code).

## 1. The handoff files this fault under the wrong class

`claude/start_here_2026-08-05.md` §"Next, in order" item 1 reads:

> **Class 2 residue, 9,854.** … The **second known cause is the line-break hyphen**
> (`46KhuA27`, `12DiT05`) and it has never been attempted.

`claude/the_run_was_judged_as_a_whole_and_never_split.md` §6.2, which is where the
fault was first recorded, states it correctly and does not mention class 2:

> A display run whose last line ends in a line-break hyphen **is prose**. … one printed
> line is split across two render blocks — the only two volumes `verify_render_vs_pdf`
> loses on.

A prose line drawn as verse is **class 1**. The 08-05 handoff merged the hyphen fault
into the class-2 item; it is not class 2, and repairing it will not move the 9,854.

**Measured.** `check_page_fidelity` on the two witnesses, per printed line:

| | 46KhuA27 | 12DiT05 |
|---|---:|---:|
| class 2 `VERSE_AS_PROSE` | 37 | **2** |
| class 1 `PROSE_AS_VERSE` | 343 | 49 |

Neither volume's class-2 count has anything to do with the hyphen. `12DiT05`'s two
class-2 lines are on p238 and are ordinary prose glosses.

## 2. What the instrument that DOES see this fault reports

`verify_all_volumes` reproduces the 08-04 numbers on the reverse and duplicate axes:
`46KhuA27` **1 lines / 0 chunks / 2 rev / 0 dup**, `12DiT05` **3 / 3 / 6 / 0**.
(The 08-04 doc records `12DiT05` as `43/3/6/0`; the forward-line figure differs
because that run was per book and this one is whole-volume. rev/chunk/dup agree exactly.)

All **8** reverse misses across both volumes are residue entries in a verse side-map's
`before` or `after` array, and every one is a printed line whose two halves became two
entries:

| vol | ord | side | printed line, as the page sets it |
|---|---|---|---|
| 46KhuA27 | 108 | after | `…nivattiñca sa-` / `upāyaṁ. Iti…` |
| 12DiT05 | 285 | before | `…sampattato yathā-` / `upaṭṭhita…` |
| 12DiT05 | 286 | before | `…savisaye pavatti-` / `ākāraviseso,` |
| 12DiT05 | 300 | after | `…dīghanikāyamahā-` / `aṭṭhakathāsārameva…` |

Each costs 2 reverse misses (one per half) and 1 forward line miss.

## 3. Three distinct shapes, and the class checker sees only one of them

| | witness | page class | corpus | verdict | visible to `check_page_fidelity`? |
|---|---|---|---|---|---|
| **A** prose line swallowed INTO a display run | `46KhuA27` p189 | prose | V | `PROSE_AS_VERSE` | yes — as **class 1** |
| **B** display run's LAST line ends mid-word, continuation is prose | `12DiT05` p300 | verse | V | `verse_ok` | **no** |
| **C** both halves page-prose, split into two residue entries | `12DiT05` p281, p282 | prose | P | `prose_ok` | **no** |

**5 of the 6 printed lines involved are scored clean by the class checker.** Shape C is
the majority (4 of 8 reverse misses) and has no display run in it at all, so §6.2's
framing — "a display run whose last line…" — covers only shapes A and B.

## 4. "A pāda never ends mid-word" is refuted by the edition

§6.2 offers that as the licensing principle. It is false, and a blanket rule would
damage real verse in 38 volumes.

Corpus-wide census (`_xc/hy1/cen`, all 118 volumes, `_xc/hy1/census.py`):

- printed lines ending in `-`: **14,396**
- of those, judged **page-verse**: **143**
- **76 of the 143 are the peyyāla `-pa-` / `-pe-` / `-la-`**, a complete token that
  `hyjoin`'s `_PEYYALA_END` already recognises — not a word break at all. *(My first
  pass counted these as hyphen lines. That was a defect in this probe, not in the
  corpus, and it inflated the population by 113%. Corrected here.)*
- **genuine mid-word hyphen on a page-verse line: 67, across 38 volumes.**

Of 69 page-verse hyphen lines in the five volumes read line-by-line
(`_xc/hy1/shape.py`), **68 continue into another page-verse line** — the compound
genuinely spills across the pāda break, and the edition sets it that way:

```
Yo sabbalokātigasabbasobhā-        46KhuA27 p7   ind 23
Yuttehi sabbehi guṇehi yutto.                    ind 23

Namo avijjādikilesajāla-           01VinA01 p15  ind 14
Viddhaṁsino dhammavarassa tassa.                 ind 14

Dukkhaṁ tiracchesu kasāpatoda-     03ViT03 p193  ind 15
Daṇḍābhighātādibhavaṁ anekaṁ.                    ind 15
```

**Exactly one** of the 69 is the §6.2 shape — `12DiT05` p300, whose continuation is
page-prose at indent 0. The discriminator is therefore **not** the hyphen. It is
**whether the continuation line leaves the display run**.

> **§5 and §6 below were written before the pages were read and are superseded by §9.**
> The join rule §5 proposes is not wrong, but it repairs the symptom and leaves the
> fault. Read §9 first.

## 5. What this means for the repair

The rule that survives the measurement is narrow:

> A hyphen-ending line and its continuation are **one printed line** and must land in
> **one render block**. Where they currently land in two, join them with `hyjoin`,
> which already carries the sentence.

That is a statement about **residue entry construction**, not about pāda geometry, and
it covers all three shapes at once without consulting the display run. `hyjoin` is
applied on some paths into `before`/`after` (`build_khu_volume.py` 7751, 7781) and not
on the paths these four ordinals take.

**Do not** implement §6.2 as written ("a display run whose last line ends in a hyphen is
prose"): it addresses only shapes A and B, it is silent on the majority shape C, and the
principle it rests on would move 67 real verse lines in 38 volumes.

## 6. Expected movement, to be checked against, not assumed

- `verify_render_vs_pdf`: `46KhuA27` 1/0/2/0 → **0/0/0/0**, `12DiT05` 3/3/6/0 → **0/0/0/0**.
  These are the only two volumes the harness loses on for this cause.
- `check_page_fidelity` class 2: **no movement expected.** 9,854 is untouched by this.
- `check_page_fidelity` class 1: at most **−1** (`46KhuA27` p189, shape A), and only if
  the join also takes that line off the verse branch.
- Any movement beyond this is a side effect and must be read on the page.

## 7. Reproduce

```
python3 pipeline/check_page_fidelity.py 46KhuA27 12DiT05 --dump _xc/hy1
python3 _xc/hy1/probe.py                      # the 8 reverse misses, with text
python3 _xc/hy1/census.py 150                 # resumable; repeat until 118/118
python3 _xc/hy1/shape.py 46KhuA27 12DiT05 01VinA01 03ViT03 27KhuA08
```

## 9. The pages were read, and §5 is the wrong repair

The reader's objection, and it is correct: **the way to decide if something is verse is
to see it in the PDF. A hyphen cannot decide that.** §6.2 used the hyphen as a
classifier. §5 above then proposed a join rule which, while it does not misuse the
hyphen, repairs only the visible break.

Both witness pages read, in full, from `pline` (`_xc/hy1/page.py`):

**`46KhuA27` p189** — 27 printed lines, **no verse on the page**. Every paragraph opens
at indent 4 and continues at indent 0; the sutta quotations are block-indented at 8/9
then 4. The hyphen line is the opening line of an ordinary prose paragraph:

```
ind4      Apica pavattimācikkhanto Bhagavā sahetukaṁ ācikkhi, nivattiñca sa-
ind0  upāyaṁ. Iti pavattinivattitadubhayahetūnaṁ etapparamato cattāreva vuttāni.
```

**`12DiT05` p300** — 25 printed lines, **no verse on the page**. Three consecutive
one-line word glosses sit at indent 4 — lemma, then meaning, the ordinary commentary
shape — and the third runs over:

```
ind4      Mahāṭṭhakathāya sāranti dīghanikāyamahā-aṭṭhakathāyaṁ atthasāraṁ.
ind4      Ekūnasaṭṭhimattoti thokaṁ ūnabhāvato matta-saddaggahaṇaṁ.
ind4      Mūlakaṭṭhakathāsāranti pubbe vuttaṁ dīghanikāyamahā-
ind0  aṭṭhakathāsārameva puna nigamanavasena vadati. Atha vā
```

**The hyphen is not a cause and not a test.** It is only what made one misclassification
*visible*: the word ran past the line end, so the bad block boundary cut a word in half
where it could be seen. Every other line in that stack is misclassified exactly as badly
and leaves no trace. A join rule fixes the visible break and leaves the three glosses on
p300 still drawn as verse.

**The two witnesses fail at different instruments:**

| | page-side classifier | builder | scored |
|---|---|---|---|
| `46KhuA27` p189 | prose — **correct** | verse | `PROSE_AS_VERSE`, class 1 |
| `12DiT05` p300 | verse — **wrong** | verse | `verse_ok`, **invisible** |

The second is the **fifth** time this week the checker, not the corpus, was the thing
that was wrong.

**The real cause behind both is a display column, not a hyphen**: short prose lines
stacked at the paragraph-opening indent are taken for a stack of pādas, because indent
plus shortness is the whole of the evidence. That is the `_kat_cols` / `display_column`
family `0db4a917` addressed in the opposite direction, it produces **class 1**, and it
belongs with the handoff's item 2 (9,155), not item 1.

### What §4's 67 are actually good for

Useless as a rule, useful as a **finder**. The hyphen is a cheap mechanical way to
surface candidate misclassifications for reading — 67 corpus-wide across 38 volumes,
small enough to read one by one.

`_xc/hy1/review_build.py` + `review_html.py` put each of the 67 back on its printed page
with the edition's own indents and write **no verdict**. `_xc/hy1/review.html`.

**Correction to §4.** It reported "68 of 69 continue into another page-verse line" as if
that settled them. Three were verified by eye — `46KhuA27` p7, `01VinA01` p15,
`03ViT03` p193, all genuine verse. **The other 65 were inferred from the continuation
line's indent, which is the same weak geometric evidence that just failed on p300.**
They are candidates, not findings.

The review sheet carries its own control: it contains `12DiT05` p300 (known prose,
classifier wrong) and `46KhuA27` p7 (known verse, classifier right), and the two are
distinguishable at a glance.

## 10. The reader read the sheet, and found three things in it

### 10.1 My sheet carried 25 lines of back matter. It should have carried none.

The reader's first two verdicts were not verse-or-prose answers at all:

> `01Vin01` — these are alternative readings that belong to an Appendix. The
> **Nānāpāṭhā is an Appendix and should not be included in corpus. This rule
> applies to all books.**
> `03Vin03` — all the **Lakkhitabbapadānaṁ anukkamaṇikā** should not be included
> in the corpus. This rule applies for all books.

**The rule is already honoured by the corpus.** Measured: `01Vin01` prints 425 pages
and announces an appendix in the heading of 32 of them; the corpus anchors no
paragraph past p403. `03Vin03` prints 673, announces on 159, and the corpus stops at
p523. **Appendix pages the corpus anchors onto: 0 and 0.**

**The fault was mine.** `census.py` collected candidates from `r['rows']`, which is the
raw printed stream and still holds the front contents and the back index/appendix that
`check_page_fidelity` separates out as `head_pages` / `tail_pages`. **25 of the 67 were
back matter** — Nānāpāṭhā, anukkamaṇikā, padānukkama — and the reader spent two of his
verdicts on pages the instrument had already set aside. `review_build.py` now excludes
them against `_xc/hy1/edgepg.json`; the excluded 25 are kept in `review_dropped.json`
rather than dropped silently. **The body candidate set is 42 across 22 volumes, not 67.**

Note for whoever reads the counts: 4 of the 25 carry a `VERSE_AS_PROSE` verdict
(`01Vin01` p417, `07Di02` p302, `10MaA01` p440, `48AbhiA01` p518, `51Vism01` p395).
They are **not** in the volumes' class-2 totals — `summarise()` subtracts `edge_lines` —
but any probe that reads `rows` directly will pick them up, as this one did.

### 10.2 The verse candidates are verse, and the classifier is right on them

`01VinA01`, `03ViT03`, `06ViT06` — all confirmed genuine verse by the reader, with the
compound genuinely broken across the pāda. **The page-side classifier is right on these**,
and §4's caution stands: they were candidates, and they came back clean.

### 10.3 The real fault under them is the stanza, and it is bigger than the hyphen

> These are verses but please notice that there is **a blank line after the first four
> lines** … In the corpus I don't see those blank lines separating those group of verses.

Read on the data, it is worse than a missing blank line. `06ViT06`'s entire
Ganthārambhakathā — the page the reader screenshotted — is **one flat prose paragraph**:

```
"Paññāvisuddhāya dayāya sabbe, Vimocitā yena vineyyasattā. Taṁ cakkhubhūtaṁ
sirasā namitvā, Lokassa lokantagatassa dhammaṁ. Saṁghañca sīlādiguṇehi yutta-
Mādāya sabbesu padesu sāraṁ. Saṅkhepakāmena mamāsayena, …"
```

Not the stanza breaks alone — **every printed line break is gone**, and the volume's
`verse/` side-map has no entry for that ordinal at all (its keys begin at `8`; this is
index 1). That is the no-`groups` frame shape of
`claude/the_run_was_judged_as_a_whole_and_never_split.md` §1, still standing in the ṭīkā
layer. `06ViT06` carries **151 class-2 lines**.

So the reader's three verse volumes are not a hyphen problem and not a class-1 problem.
They are **class 2**, the handoff's item 1 — reached from the opposite direction.

### 10.4 A corpus-wide text corruption: 8,790 broken words

> There should not be blank line between `āgata-` and `aññenaññapaṭicaraṇavasena`.
> The same between `pana` and `musāvādena`.

`05ViT05` ¶100 in the corpus reads `pāḷiyaṁ āgata- aññenaññapaṭicaraṇavasena`.
`hyjoin` decides a line-end hyphen three ways and **none of them leaves a hyphen
followed by a space inside a word**: peyyāla keeps it and spaces off, a junction before
a vowel keeps it closed up (`āgata-aññenañña…`), a soft break drops it
(`yutta-` + `Mādāya` → `yuttaMādāya`). Where the corpus has `- `, `hyjoin` never ran and
the plain `prev + ' ' + t` path did.

**Corpus-wide: 8,790 occurrences across 109 volumes** (`_xc/hy1/hyspace.py`).
Worst: `09DiT02` 265, `22AbhiT01` 261, `26VsmT02` 243, `23AbhiT02` 238, `24AbhiT03` 230.

**Control** (`_xc/hy1/hyverify.py`), because a count over the corpus is worth nothing
until the page confirms it: for a sample of 300 occurrences over 5 volumes, look for a
printed line that ENDS with the flagged hyphen and a next line that BEGINS with the
continuation. **296 of 300 confirmed a real printed line break — 98.7%.** The 4
unconfirmed are the matcher's limits (page-boundary breaks, footnote markers), not
evidence the corpus is right.

This is a **text** fault, not a layout one: the word is broken in `site/<VOL>.json`
itself. It is upstream of every render question in this document.

## 11. The pages can be rendered and read directly, and the sheet's page numbers were wrong

### 11.1 "Can you see the PDF pages as I see them?" — yes

`pdftoppm -r 115 -png` renders any page of any of the 118 volumes and it can be read
directly, layout, bold, footnotes and all. **This was available the whole time and was not
being used**; every judgement in §§1–10 was made from the extracted line stream instead.
The reader was asked to hand-adjudicate 67 pages that could have been read here.
`_xc/hy1/pg/`.

### 11.2 The sheet's page numbers pointed at the wrong pages

`pline`'s page index is neither the pdftotext page nor the number printed on the page,
and the relation differs per volume — it is anchored to the text extent the PDF declares
in its `Subject`. The sheet labelled the pline index "PDF p", so:

| candidate | sheet said | pdftotext | **printed on the page** |
|---|---:|---:|---:|
| `07ViT07` | p507 | 509 | **488** |
| `07DiA01` | p170 | 170 | **154** |
| `07DiA01` | p135 | 135 | **119** |
| `06ViT06` | p564 | 566 | **537** |

The reader went to p507 and p170 and correctly reported he could not find them.
`_xc/hy1/resolve.py` now locates each candidate's own text in `extract.raw_pages` —
matching on the **ASCII skeleton**, because `raw_pages` returns legacy VZTimes bytes and
a diacritic is a different character on each side — and records both numbers in
`_xc/hy1/pagemap.json`. All 30 distinct pages resolve.

### 11.3 The blank line is on the page and every instrument throws it away — **WRONG, see §12**

The reader's stanza objection has a mechanical cause. `pdftotext -layout` **preserves the
blank lines** between stanzas — they are in the text layer. `pline.stream()` returns
**zero** empty lines: they are filtered out at extraction.

So `check_page_fidelity`, `check_bold_fidelity`, `_xc/pagemark` and the reseg tools all
read a printed line stream with the stanza boundaries already deleted. **The evidence for
the fault the reader found is discarded before any instrument can see it** — which is why
no check has ever reported it, and why it took screenshots.

This is the fifth item on the §9 list of "the checker was the thing that was wrong", and
the largest: it is not a wrong rule but a missing input, and it is upstream of class 2,
class 4 and the verse side-maps alike.

### 11.4 Adjudicated so far, from the rendered pages

| candidate | printed | verdict | note |
|---|---:|---|---|
| `07DiA01` p170 | 154 | **verse** | couplet cited from Ummādantījātaka (fn 6); `ti-ādīsu` straddles the verse→prose boundary |
| `20KhuA01` p232 | 215 | **verse** | two 4-line stanzas, blank line between them plainly on the page |
| `12DiT05` p300 | 291 | **prose** | three one-line glosses at the paragraph indent (§9) |

`07DiA01` p154 and `12DiT05` p300 are the **same shape** — a run's last line ending
mid-word with prose below — and they get **opposite** answers. Shape decides nothing.
Only the page does, which is the reader's original objection, now demonstrated twice.

## 12. §11.3 was wrong twice, and the real signal is 6.0 points

**§11.3 claimed the blank line is in the text layer and `pline` discards it. Both
halves are false.**

**First**, `pline` does not discard the blank lines it receives. `_build()` enumerates
`d['body']` and emits only non-blank lines **carrying their original index `j`**, so a
blank line survives as a jump in `j`. On `20KhuA01` p232 the jumps `26 -> 28` and
`28 -> 30` are exactly the two blank lines before the colophon. The information was
never thrown away; nothing reads it, which is a different fault.

**Second**, and this is why the first mattered less than it looked: **the stanza break is
not in the `-layout` stream at all.** On the same page, pdftotext p233:

```
 4   Evampi atthakusalena Tathāgatena,
 5   Dhammissarena kathitaṁ karaṇīyamatthaṁ.
 6   Katvānubhuyya paramaṁ hadayassa santiṁ,
 7   Santaṁ padaṁ abhisamenti samattapaññā.
 8   Tasmā hi taṁ amatamabbhutamariyakantaṁ,      <- the page sets a gap here
 9   Santaṁ padaṁ abhisamecca viharitukāmo1.
```

Eight verse lines contiguous, no blank line between the stanzas, while the rendered page
plainly shows one. The gap is typographic leading, below the threshold at which `-layout`
breaks a line. **So there was nothing to discard**, and the reader's stanza fault could
not have been found from the line stream by anyone.

### 12.1 It is in the coordinates, and it is a constant

`pdftotext -bbox` gives every word's `y`. Grouped into lines, the leading is bimodal:

| page | body leading | break leading | Δ |
|---|---:|---:|---:|
| `20KhuA01` p233 | 17.2 | 23.2 | **+6.0** |
| `06ViT06` p28 | 15.3 | 21.3 | **+6.0** |
| `06ViT06` p566 | 17.9 | 23.9 | **+6.0** |
| `12DiT05` p300 | 18.5 | 24.5 | **+6.0** |
| `46KhuA27` p7 | 17.0 | 23.0 | **+6.0** |
| `46KhuA27` p189 | 16.7 | 22.7 | **+6.0** |

The body leading differs per volume and per page; **the space before a new block is 6.0
points, exactly, on all six.** That is a fixed space-before in the source, and it marks a
paragraph break and a stanza break alike.

### 12.2 Measured over all 118 volumes, not over the six that suggested it

`_xc/hy1/leadcensus2.py`, 235 pages sampled at random from every volume, 1,231
inter-line gaps larger than the page's own body leading:

```
 +6.0 pt   419  ############################################################
 +5.9 pt    88  ############
 +6.1 pt    50  #######
+16.5 pt    26  ###
+15.0 pt    23  ###
+17.1 pt    21  ###
```

**602 of 1,231 gaps (48.9%) sit at body+6.0 ±1.0**, and there is no competing mode near
it — the remainder is a long tail from +15 upward, which is heading and section spacing.
**114 of 118 volumes show the +6.0 mode.**

*(An earlier run reported 52% and listed deltas of +15 to +26 as failures. That statistic
was wrong: it took each page's second mode, so a page whose only break is a heading gap
scored the heading and counted as a miss. `leadcensus.py` is kept beside `leadcensus2.py`
as the record of the error.)*

The four not showing it — `07Di02`, `21Khu04`, `23Khu06`, `26KhuA07` — were sampled at
**two pages each**, so absence here is very likely sampling. **They must be sampled
properly before anything is built on this**, and if the mode is genuinely absent in a
volume that is a finding in itself.

### 12.3 Why this matters more than anything else in this document

Every classification fault in §§1–11 comes from the same poverty of evidence: **indent and
line length are all the instruments have**, which is why short prose glosses at a
paragraph indent read as pādas (`12DiT05` p300) and why `_kat_cols` and `display_column`
have needed repair after repair.

The 6.0pt space is an **independent** signal. It does not consult indent, it needs no
volume-specific flag, it is measured per page like `display_column_pages`, and it marks
exactly the boundary the corpus keeps losing. It is available on every one of the 118
volumes and no instrument in this project has ever read it.

**Not built.** This is a measurement, not a repair. What it licenses:
a block-boundary map per printed page, which would give the stanza grouping the reader
asked for, the paragraph breaks of §10.4, and a second instrument for the position work
(handoff item 3) that is not derived from the corpus.

## 13. The reserved non-gāthā class, located and verified on the page

Five page references were given to the reader for this decision. **Two were wrong and
three were unverified**, and the labelling sent him to the wrong pages for two more.
Recorded in full because the pattern is the one this project keeps paying for: pages
chosen by keyword and reported without being looked at.

**Fault 1 — pages chosen by keyword.** `26Khu09` was located by searching for `Mātikā`,
which matched the **front-matter contents heading** (`Mātikā … Piṭṭhaṅka`, printed p**vi**),
not the doctrinal mātikā. `35Abhi07` was located by searching `Yamaka`, which matched
first a closing colophon and then the volume's title page.

**Fault 2 — a single line's skeleton is not a page.** `resolve.py` matched one line;
`1. Kusalā kusalā dhammā` occurs both on `35Abhi07`'s first text page and in its contents,
so it returned the contents. `_xc/hy1/locate2.py` scores **every** raw page by how many of
the pline page's line skeletons it holds and requires the winner to beat the runner-up
(35Abhi07: 29 vs 10). **Re-run over the 30 candidate pages of §11.2: 0 disagreements**, so
those resolutions stand.

**Fault 3 — the number given was the one not to give.** The table led with the pdftotext
page and left `printed` blank wherever the running head did not parse — which is exactly
the opening pages that were chosen. The reader navigated by the number offered and landed
on printed p10 of `35Abhi07` (prose, ¶39–40) and printed p33 of `29Abhi01` (prose,
¶102–109), and reasonably asked what the problem was. **The printed number is the only one
worth leading with.**

### Corrected, each one read from the rendered page

| shape | volume | **printed** | pdftotext | what is on it |
|---|---|---:|---:|---|
| Yamaka pairs | `35Abhi07` Indriyayamakapāḷi | **74** | 83 | `3. Na cakkhu na cakkhundriyaṁ.` + ~18 hanging short lines |
| Dukamātikā | `29Abhi01` Dhammasaṅgaṇīpāḷi | **14** | 33 | `107. Nirutti dhammā. (1314)` / `Niruttipathā dhammā. (1314)` |
| Paṭisambhidā mātikā | `26Khu09` Paṭisambhidāmaggapāḷi | **4** | 13 | numbered entries 52–72, one short line each |
| Refuge lists | `18Khu01` Khuddakapāṭhapāḷi | opening, unnumbered | 26 | Saraṇattaya, three triads |
| `(Sattamo bhāgo)` | `42KhuA23` | **not verified** | — | still located by keyword only |

`42KhuA23` is left explicitly unverified rather than guessed a fourth time. Its densest
page-verse page (pline p59, `927. Kathaṁ hi lokāpacito samāno,`) is **genuine gāthā** with
pāda commas, so it is not the reserved shape and the `(Sattamo bhāgo)` case is elsewhere.

### What the verified pages show

All four are the same shape: **a numbered opening line and a hanging stack of short,
uniform lines**, one doctrinal item per line, with the 6.0pt break between units. On
`35Abhi07` p74 the lines end in `.` and carry the peyyāla ` . ` internally; a pāda's comma
is absent from every one. That absence is what `_pada_page` scores, and it scores these
exactly 0 — the negative test that is currently protecting them.

**The 6.0pt break of §12 is present on all four**, one block per numbered unit, so the
block map groups them correctly whatever they are called. The open decision is the label
alone.

## 14. The block map — built, controlled, and it answers the 42

### 14.1 §12's "6.0 points" was too narrow

Sampled properly (40 pages each, `_xc/hy1/lead4.py`), the four volumes of §12.2 split two
ways. `07Di02` and `26KhuA07` do carry the +6.0 mode — their absence was sampling, as
suspected. **`21Khu04` and `23Khu06` do not**, and the reason is not noise:

- `20Khu03` p120 sets **15.5** inside a couplet and **31.0** between stanzas — a whole
  **skipped line**, 2× the leading, not a 6.0pt space. `21Khu04` p61 the same (14.4 / 28.8),
  while *also* using 6.0 before its colophon lines.
- `23Khu06` p60 sets **15.7** and **25.7** — a 10.0pt space.
- `29Abhi01` p120 separates its *paragraphs* by 32.3 over a body of 16.1 — again a skipped
  line.

Per-volume measurement over all 118 (`_xc/hy1/blockgap.py`): **112 volumes' commonest gap
is 6.0**, and six are not — `20Khu03` 14.0, `21Khu04` 13.5, `23Khu06` 10.0, `29Abhi01`
16.0, `31Abhi03` 17.0, `42KhuA23` 15.5.

**An instrument defect of my own, found on the way.** `lead.py` took a line's y from its
first word, and a superscript footnote marker has a smaller `yMin` than the text it sits
on — so the same block gap measured 9.1 on a line opening with a marker and 10.0 on one
without (`23Khu06` p60). Line y is now the **modal** word y and the wobble is gone.

### 14.2 The rule that needs no constant

```
a new block begins wherever the leading exceeds THAT PAGE's own body leading by
more than 3.0 pt
```

This catches the 6.0pt space, the skipped line and the heading gap alike, is measured per
page exactly as `display_column_pages` measures its column, and consults no volume name.
`_xc/hy1/blockmap.py`, all 118 volumes, ~1 minute: 14–23% of printed lines start a block.

### 14.3 It reproduces the reader's own hand-drawn breaks

The reader wrote out where `06ViT06` p28's blank lines belong. The map, from coordinates
alone, marks a block start at `Paññāvisuddhāya`, `Saṁghañca`, `Samantapāsādikasaññitāya`,
`Saññā nimittaṁ` and the prose below — **exactly his four groups and no others.** On
`20KhuA01` p233 it splits the two stanzas at `Tasmā hi taṁ`; on `12DiT05` p300 it makes the
three one-line glosses three separate blocks, which is §9's verdict reached again from
evidence that never touches indent.

### 14.4 Controls

`_xc/hy1/blockctl.py`. **The first version of the shuffle control was vacuous by
construction** — it counted marks, and a count is permutation-invariant, so it returned a
number identical to the honest run on every volume and would have on any input at all.
Rescored by verdicts moved per line:

| vol | th=1 | th=3 | th=8 | th=20 | shuffle moved | flat moved |
|---|---:|---:|---:|---:|---:|---:|
| `06ViT06` | 3661 | 3642 | 2485 | 1334 | 4572 (22.8%) | 2990 (14.9%) |
| `29Abhi01` | 2654 | 2643 | 2265 | 639 | 3188 (33.3%) | 2320 (24.3%) |
| `23Khu06` | 4699 | 4564 | 4239 | 988 | 5194 (32.6%) | 4071 (25.5%) |

Both controls fire hard. **No volume is vacuous.** The 0.5% difference between th=1.0 and
th=3.0 is the bimodality proving itself: there is almost nothing between body+1 and body+3.

### 14.5 Verse-vs-prose from the block, not from a column

With a boundary in hand the discriminator is the **shape of a block**, and it needs no
`display_column` and no line-length test:

| block shape | verdict |
|---|---|
| continuations return to the left margin | **prose** |
| every line at one x, right of the margin | **display** |
| first line **hangs left** of the rest | **display** — a numbered verse item |
| first line indented **further right** than the rest | **prose** — a block quotation |

The margin is a constant of the **volume**, not the page: computed per page it fails on any
page the display dominates (`06ViT06` p28 is 14 verse lines against 4 of prose, so the
modal x was the verse indent and every stanza came out prose) and on a title page with no
prose at all (`46KhuA27` p7).

Control: **5 of 5** on the cases already settled by reading the page.

### 14.6 The 42 candidates, adjudicated

**29 display, 12 prose, 1 unresolved** (`07DiA01` p154, whose needle fails on a superscript
— already read by eye in §11.4 and it is verse).

Spot-checked against renders: `07ViT07` printed 488 → display, matching the reader's own
screenshot of numbered stanzas; `40KhuA21` p450 → prose, an 11-line block quotation;
`51Vism01` printed 227 → prose, and `check_page_fidelity` had called that line page-verse,
so it is **a genuine class-1 fault the map catches**. That page also carries two real
stanzas lower down and the map separates them correctly.

`_xc/hy1/verdicts.json`.

## 15. The reserved class is decided, and the reader found two more faults of mine

### 15.1 Decided: all four are PROSE

The reader, on the four pages of §13:

> `35Abhi07` p74 — *It is prose.*
> `29Abhi01` p14 — *These are not verses. They are just lines from the Mātikā or matrix of
> Suttanta dyads. From 107 to 120 each are dyads, two lines of text.*
> `26Khu09` p4 — *These are not verses. They are just prose statements.*
> `18Khu01` — *These are not verses… the ten precepts in prose.*

**The reserved non-gāthā class is not gāthā and does not need a class of its own. It is
prose whose printed line breaks carry meaning.** The open question in the handoff since
`0db4a917` is closed.

### 15.2 Two corrections to §10.3 and §14, both found by the reader

**(a) `35Abhi07` is NOT flat, and my evidence was the wrong layer.** I read
`paragraph['text']`, found one run-on string, and reported the printed line breaks lost.
The `verse/` side-map holds an `after` array for that ordinal with **one entry per printed
line**:

```
"Na cakkhu na cakkhundriyaṁ. . Na cakkhundriyaṁ na cakkhu.",
"Na sotaṁ na sotindriyaṁ. . Na sotindriyaṁ na sotaṁ.",  …
```

The reader draws it correctly. `check_page_fidelity`'s **page** side calls these lines
verse; the reader says prose and the corpus already treats them as prose — so a share of
`35Abhi07`'s 208 class-2 lines are **false positives of the checker**, not corpus faults.
This is the same error as §11.3: one layer inspected, a conclusion drawn about the whole.
`06ViT06` ord1 was checked at the right layer (no `verse/` entry, `sections/` holds only
three headings) and **is** genuinely flat — that finding stands.

**(b) `29Abhi01`'s dyads ARE joined, exactly as the reader said.** Verified line by line:

```
page   :  107. Nirutti dhammā. (1314)          x84.2
          Niruttipathā dhammā. (1314)          x109.4
corpus :  "Dhātukusalatā ca. (1340) Manasikārakusalatā ca. (1341)"   -- one string
```

### 15.3 The block map had a real defect, and this page exposed it

On `29Abhi01` p33 the within-dyad leading is **14.6** on 11 lines and **14.5** on 3.
`blockmap.py` rounded to 0.1 and took `most_common(1)`, so the 14 body lines split across
two keys and **lost to the block gap at 24.6 (13)**. `base` became the gap, nothing
exceeded `base + 3`, and a page of 14 dyads came out as **one block**.

`blockgap.py` already clustered to 0.5pt for exactly this reason; `blockmap.py` did not.
Fixed by clustering, then averaging the cluster. **112 of 118 volumes change**, so the
defect was corpus-wide and the numbers in §14 were measured on a broken map. The old build
is kept at `_xc/hy1/blocks/` as its own negative control; the current one is
`_xc/hy1/blocks2/`.

Re-run on the corrected map: `29Abhi01` p33 now yields one block per dyad. Controls hold —
shuffle moves 19.6–34.2%, flat 11.8–26.0%, no vacuous volume, adjudicator **5/5** on the
settled cases, and the 42 verdicts are unchanged at 29 / 12 / 1.

### 15.4 `display` is a statement about layout, not about genre

The corrected map labels each Dukamātikā dyad `display` — correctly, because the page sets
it off from running prose with a hanging indent. **The reader says it is prose.** Both are
right, and the words must not be conflated: `display` means *the page sets this apart*, and
whether it is *gāthā* is a different question that no geometry can answer. §6.2 conflated
them and so did I when I called the adjudicator's output a verse verdict. The label the
side-maps carry should say layout; genre needs the caesura, the commentary, or the reader.

## 16. The joined line break, measured corpus-wide

The reader's `29Abhi01` report generalises. Measured with the block map
(`_xc/hy1/joined2.py`), over all 118 volumes:

| | |
|---|---:|
| display blocks of more than one printed line | **52,265** |
| drawn as separate lines — correct | **37,306** |
| **JOINED into one drawn line** | **672**, costing **865 printed lines** |
| partly present | 377 |
| not in the verse map at all | 13,910 |

Concentrated in the Abhidhamma canon: `29Abhi01` 183 lines, `35Abhi07` 122,
`39Abhi11` 120, `38Abhi10` 44, `40Abhi12` 16. `20Khu03` 44 and `27Khu10` 42 follow.

**It is not uniform within a volume.** `35Abhi07` ¶3 keeps its nineteen lines as nineteen
`after` entries; ¶4, the next paragraph, is one flat string. So this is not a volume flag
but something decided per paragraph.

### 16.1 Two wrong measurements preceded this one, and both are discarded

- **`dyad.py`** matched a 24-character prefix. On a text as formulaic as the
  Dhammasaṅgaṇī it matched `cittapassaddhi` to `cittapāguññatā`; every number it produced
  was wrong.
- **`joined.py`** matched whole corpus entries against whole printed blocks by equality.
  The block carries the paragraph number the entry omits, so **1,812 of 1,884 entries
  failed to match** and the 4% that matched were a sample of nothing. It also asked the
  wrong question: a *prose* paragraph's line breaks are not structural — the page wraps it
  and the reader reflows it — so joining them is correct, and a break is only lost where
  the page sets the lines apart.
- **`joined2.py`** iterates DISPLAY BLOCKS instead, and asks of each whether the corpus
  draws its N printed lines as N drawn lines. Its own walker was wrong once too: an entry
  in `after` is **either a string or a dict `{"gatha": [...]}`**, and handling only strings
  made `20KhuA01` report 184 blocks "not in the verse map" when its stanzas are plainly
  there.

**Control:** `20KhuA01` — a volume whose verse is known-good — reports **111 kept, 0
joined**. A measure of this fault that cannot show a clean volume as clean is not
measuring the fault.

### 16.2 Not yet examined

The **13,910 blocks with no verse-map entry at all** are the larger number and are *not*
claimed as a fault here. A block the page sets apart may legitimately live in `sections/`
(a heading) or `uddana/`, or be front matter. Until each is traced to the map that owns
it, the number means only "not in `verse/`".

## 17. The cause, located to two lines

`35Abhi07` and `29Abhi01` are both `'katha'` mode in `SPEC`, so the live path is
`kat_build`. Its `add_prose` (`build_khu_volume.py:6951`) decides every printed line:

```python
if new_para or not open_prose or prev is None:
    after.append(t)          # a NEW drawn line -- the printed break is KEPT
    ...
joined = hyjoin(prev, t)     # otherwise JOINED -- the printed break is LOST
```

and `new_para` is nothing but the line's kind (`:7367`):

```python
add_prose(it[1], kind == 'popen')
```

`kat_items` assigns that kind. In the sibling `nid_items` the rule is visible in one line
(`:5044`):

```python
items.append(('popen' if ind >= base + 3 else 'pcont', t, pg))
```

**Whether a printed line survives as its own line is decided by its indent, and by nothing
else.** `vline` → a gāthā block, breaks kept. `popen` → a new entry, break kept. `pcont` →
joined, break lost. That is the same poverty of evidence behind every fault in this
document: three one-line glosses at a paragraph indent read as pādas (§9), short prose
stacked at the paragraph indent read as verse (§11.4), and here the second line of a
Dukamātikā dyad read as a continuation and swallowed.

**One rule at this site is already correct and should be preserved:** `:6975` forces
`new_para = False` when the previous line ends in a hyphen, because a hyphen means a word
split across lines and not a paragraph boundary. That is the §6.2 hyphen, used correctly —
as evidence about *word continuity*, which is all it can testify to, and never about genre.

### 17.1 What the repair would be, and why it is not made here

The block map supplies exactly the missing evidence: a printed line that begins a new line
**inside a block the page sets apart** is structural, and `new_para` must be true for it;
inside a prose paragraph the break is a wrap and joining is right. That is a statement the
builder can act on and it needs no display column.

It is **not applied** in this session, and the reason is the standing rule. It is a builder
change, so it requires: the block map joined to `pline`'s page/line indexing; a rebuild of
the affected volumes; `pbreak/` re-derived (`check_derived` will otherwise report drift);
`regress`, `check_links`, `check_ordinal`, `check_concordance`, `check_bold_fidelity` and
`check_layout` re-run; and the whole measured against the printed page before anything is
written. A builder change made at the end of a long session, on a map built the same day,
is how the last four regressions happened.

**What is ready:** the fault measured (672 blocks, 865 printed lines), the cause located to
two lines, and the evidence built and controlled.

## 18. The block map joined to `pline` — the boundary is now addressable

The block map was keyed by pdftotext page and bbox line order. Every instrument in this
project reads `pline.stream()`, whose pages count only what `split_page` **accepts** and
whose lines exclude the running head and the footnote apparatus. Until the two are joined
the boundary cannot be used by anything. `_xc/hy1/blockjoin.py`, output `_xc/hy1/bjoin2/`:
one entry per `pline` item, `[block_start, block_kind]`.

**Page axis** — rebuilt exactly as `pline._build` does it: `split_page` over `raw_pages`
with the same glyph-errata patch and the same assertion, recording each accepted page's raw
index. Not an offset: `07ViT07`'s would have been wrong by two.

**Line axis** — `pline`'s lines are a *subsequence* of the bbox lines, so they are aligned
in order by normalised text, never by position.

### 18.1 Digits had to be dropped from the alignment key

First run: **94.57%**. The residue was systematic. A superscript footnote marker has its
own x and a smaller y, so in the bbox word order it lands wherever that x falls — `pline`
reads `viharitukāmo1.` from `-layout` while the bbox line reads `1 Santaṁ … viharitukāmo .`
Keeping the digit made those two strings unequal and cost ~8% of the alignment on some
volumes. Dropping digits from the key — which `check_page_fidelity` already does, reporting
them separately as `digit_only` — took it to **97.86%**, and on body pages to 98.8–100%.

### 18.2 Measured over all 118 volumes

**1,421,684 of 1,447,441 body lines aligned — 98.22%.** Front matter (the alphabet tables,
which are Burmese script in the same font and which §3 of the project instructions says to
skip) and back matter are excluded, as they are from every other body measure.

| block kind of an aligned body line | lines | |
|---|---:|---:|
| prose | 1,218,458 | 85.7% |
| display | 122,065 | 8.6% |
| display? (single-line block, undecided) | 41,814 | 2.9% |
| other | 39,347 | 2.8% |

**26 volumes align below 97%** — worst `18AnA02` 94.25%, `12MaA03` 95.38%, `11MaA02` and
`09DiA03` 95.58%. **This is a stated limit, not a rounding error**, and the repair of §17
must not be applied to a volume whose lines it cannot address. Diagnosing those 26 comes
before any builder change.

> **§18.2's numbers are wrong and §18.4 replaces them.** The denominator was mine, not the
> instrument's: the 26 "low" volumes are an artefact of my own edge filter. The true figure
> is **99.93%**.

### 18.3 Control

The join is checked where the answer is known independently: on `06ViT06` p28 it places a
block start on `Paññāvisuddhāya`, `Saṁghañca`, `Samantapāsādikasaññitāya`, `Saññā nimittaṁ`
and the prose below — **the reader's own hand-drawn structure, in `pline`'s indexing**, and
no start anywhere else in the stanzas.

## 18.4 The 26 low-alignment volumes were my filter, not the join

The residue on `18AnA02` is the edition's own **word index** — two columns of
`headword  page  headword  page`, which `-layout` renders as one line and the bbox word
order does not. **75.1% of the 16,277 unaligned lines across the 26 are that shape.**

The corpus is not carrying those pages, and the reader's appendix rule holds everywhere
checked: `18AnA02`'s corpus ends at printed page 414 and its index begins at 415;
`42KhuA23` ends at 391, index from 395; `23Khu06` 383 against 494.

**So why were they counted as body?** `_xc/hy1/edgepg.json` recorded only `head_pages` and
`tail_pages`, and all 26 report `tail_pages: None`. That looked like a gate defect and was
not: `check_page_fidelity` does not find these indexes as a *tail* at all — it names them
**interior gaps** matching `INDEXRE` and subtracts them as `index_lines`. `18AnA02` prints
`tail_pages None` and `edge 3316` in the same line, which is what gave it away. The gate
was right; my filter read one of its two mechanisms.

`_xc/hy1/edge2.py` records head, tail **and** the named index gaps. Re-measured:

| | |
|---|---:|
| body lines aligned | **1,353,130 of 1,354,117 — 99.93%** |
| volumes below 99% | **1** (`03ViT03`, 98.74%, 175 lines, none index-like) |

| block kind | lines | |
|---|---:|---:|
| prose | 1,159,914 | 85.7% |
| display | 121,915 | 9.0% |
| display? | 41,378 | 3.1% |
| other | 29,923 | 2.2% |

**The lesson is the session's own, again.** I read one of an instrument's two mechanisms,
concluded from it, and reported a defect in someone else's work that was mine — the same
shape as §11.3 (one layer of the corpus) and §15.2 (`paragraph['text']` without the
side-map). The check that caught it was running the gate itself and reading its output
rather than my cache of part of it.

`03ViT03`'s 175 remain genuinely unexplained and are the only thing outstanding here.

## 19. The repair, built and measured — NOT applied

`pipeline/build_khu_volume_bb.py`, a copy of the builder patched behind
**`BLOCKBREAK=1`** (off by default, so the file is its own negative control). The live
`build_khu_volume.py` is untouched, and nothing was run with `--write`.

**The rule.** Every printed line inside a block the page sets apart keeps its own drawn
line. Inside a prose paragraph the break is a wrap and joining stays right. It only ever
ADDS a break, never removes one, and a line the map cannot address leaves the existing
decision alone.

### 19.1 Two wrong versions of the patch first

**(a) Keyed on the wrong page axis.** The cursor read `pline`'s ACCEPTED-page index; the
builder's item stream carries the **raw pdftotext page** (`pdf_pages()` splits `-layout` on
`\f`, `page_lines(pages, i)` takes `pages[i-1]`). Result: **88% of lines unmatched, zero
display lines found** — and the negative control still passed, because a flag that never
fires is identical to a flag that is off. `_xc/hy1/blocks2/` is already keyed by the raw
page, so the §18 join is not needed at this site at all. Fixed: unmatched 5,341 → **1**.

**(b) Required the line to START a block.** It fired 166 times and changed nothing,
because `add_prose` already opens a new entry when `not open_prose`. Tracing one dyad
showed why the condition was wrong:

```
unit    pg=33  'Nirutti dhammā. (1314)'         <- becomes the ordinal itself
pcont   pg=33  'Niruttipathā dhammā. (1314)'    <- joined onto it
```

A dyad is **one block of two lines whose first line is the `unit`**, so the line that must
survive is the block's *second*. The rule is every line in a display block, not the opener.

### 19.2 Measured

Built twice in one process, flag off against flag on, and the side-maps diffed
(`_xc/hy1/bbdiff.py`). The builder's own `prose ¶` summary counter does not move and is
not the measure — the artefact is.

| volume | drawn lines | ordinals changed | letters | other maps |
|---|---|---:|---|---|
| `29Abhi01` | 1,884 → **2,062** (+178) | 159 | **identical** | identical |
| `35Abhi07` | 1,746 → **1,908** (+162) | 69 | **identical** | identical |
| `39Abhi11` | 5,503 → 5,503 (+0) | 0 | identical | identical |
| `20KhuA01` | 911 → 911 (+0) | 0 | identical | identical |

**`letters identical` is the point**: no text is added or lost, only printed line breaks
restored. `sections`, `uddana`, `hide` and `incipit` are byte-identical on every volume.

```
OFF | Kusalā dhammā. (363, 985, 1384) Akusalā dhammā. (365, 427, 986, 1385) Abyākatā…
ON  | Kusalā dhammā. (363, 985, 1384)
ON  | Akusalā dhammā. (365, 427, 986, 1385)
ON  | Abyākatā dhammā. (431, 583, 987, 1386)
```

**`20KhuA01` not moving is the control** — a volume §16 measured at 0 joined blocks must
not move, and does not.

### 19.3 Coverage is partial and the gap is named

The measured fault is **865 printed lines**; this delivers **340** on two volumes.
**`39Abhi11` does not move although §16 measured 120 lost lines there, and it is `katha`
mode like the two that do.** Unexplained. `20Khu03` and `21Khu04` are `verse` mode, which
this patch does not touch at all.

**Not applied, and it should not be until:** `39Abhi11` is explained; the remaining `katha`
volumes are measured; `pbreak/` is re-derived; and `regress`, `check_links`,
`check_ordinal`, `check_concordance`, `check_bold_fidelity`, `check_layout` and
`verify_render_vs_pdf` are run old-against-new. Bold spans are offsets into `pr.text` and
`pbreak` records address a sequence of `fmtLine` calls — both are sensitive to exactly this
change.

## 8. Not done

The repair itself. The four ordinals' emission paths in `build_khu_volume.py` are
located but the join is not written, `pbreak/` is not re-derived, and no gate has been
re-run. Nothing in the corpus or the builder was changed by this work.
