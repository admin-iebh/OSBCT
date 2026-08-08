# START HERE — 2026-08-08 pm

<!-- Supersedes start_here_2026-08-08.md, which is still correct about everything
     except its open item 1b (the apparatus half is DONE and its diagnosis was
     wrong) and its open item 1 (evidence gathered, decision still the reader's).
     Read §State, then §"Next, in order". -->

## State

**Done, not yet committed: the footnote markers, twice over.**
`pipeline/check_fn_markers.js` carries two assertions; all 118 volumes green on
both; the selftest catches the injected defect on both.
BUILD `6151ac21bbbd` → `04d4b285be40`. Commit message in `COMMIT_MSG.bak`.

  1. **Markers lost to the bold lemma** — 3,480 of 70,598 (4.93%).
  2. **Markers after a closing bracket** — 684 more, `)` 433, `”` 237, `’` 14,
     which the letter-only class could never see. Reader's own example proves
     the rule: `gāthamāha)`³ carries `( ) natthi (Sī)`, and the parenthesis the
     marker stands after IS the parenthesis the note calls absent.
  3. **The note made reachable from the marker** — ord 210 is 19,871 characters
     and its note block sat six screens below the marker. Tooltip on each
     marker. Pairing is positional and claimed only where the marker count and
     the note count agree (45,901 of 69,000, 66.5%); otherwise every candidate is
     shown and the tooltip says the pairing is not established.
  4. **Each printed page's notes drawn at the foot of that page** — which is
     where the edition sets them, and the reader's third report was that they
     were not there. Ord 210 spans SIXTEEN pages, 146–162, and every note sat in
     one block at the end. The page is derived from the MARKER's offset against
     `pbreak/`, because the apparatus data carries no page: `<vol>.app.json` is
     keyed `Work/X/X/<paragraph number>`. **45,901 of 73,431 notes (62.5%)**
     placeable; on paragraphs that actually cross a break, 30,124 of 54,426
     (55.3%). The rest stay in the end-of-paragraph block.

  5. **The opening quote moved to the page it opens** — `pbreak` cut between the
     `“` and `Diṭṭho`, stranding a quote mark alone at the foot of p. 146. The
     PRINTED page settles it: pdf 154 opens `“Diṭṭho hi me”ti`. **1,562 of
     35,043 mid-paragraph breaks (4.46%)** land after an opening mark — 1,459
     `“`, 62 `(`, 41 `‘`. Seven of ten random cases resolved against the PDF, all
     seven with the quote on the new page, none against.

**The gate now carries three assertions**, and the third found a defect the
moment it existed: four volumes drew MORE note rows than the data holds, because
`pbreak` can name the same page twice and the foot was emitted twice. A page is
spent once drawn. All 118 volumes: **55,453 notes, 55,453 rows**; 50,239 markers
backed by a note, 50,239 carrying it.

**Unchanged: `_xc/linksk_toc/20Khu03.links.json`** still holds vaggas 2–42 →
`33KhuA14`, still NOT applied. Nothing was written to `site/reader/linksk/`.

## THE APPARATUS ITEM IS CLOSED, AND THE 08-08 HANDOFF DIAGNOSED IT WRONG

The handoff said "establish whether the A band renders apparatus at all or only
the canon layer does". It renders it everywhere. Measured in the real reader:
`31KhuA12` 111 paragraphs whose data carries notes, 111 that drew the `.appx`
block; `32KhuA13` 125 of 125; `09DiT02` 62 of 62; every band, every layer.

What was actually missing was the MARKER — the digit glued to the annotated
word. Five call sites assembled the HTML and then ran `([letter])(\d{1,2})` over
it, and a bold lemma ending on the annotated letter broke the adjacency:
`<b class="lemma">Apadāne</b>2`. **3,480 of 70,598 markers, 4.93%**, 1,817 ṭīkā,
1,494 aṭṭhakathā, 169 canon — which is exactly where the reader met it and
exactly why it looked inconsistent inside one paragraph.

The handoff's own example was right and its reasoning was not: `31KhuA12` ord 210
DOES carry seven notes and DID draw them; what it did not draw was
*Apadāne*<sup>4</sup>. **Reading the source instead of rendering it is what put
the diagnosis one layer away from the fault.** Run the instrument against the
build that has the bug.

## THE ORDINAL-WORD SPAN — EVIDENCE GATHERED, DECISION NOT TAKEN

Set aside when the reader redirected to the apparatus. The measurement stands
and it says the reader was right on 08-07.

`33KhuA14` ords 561–569 are the whole of commentary vagga 40, printed pp. 202–205.
Read them straight through:

    561  (no n)  Cattālīsamavagge apadāne ... Pilindavacchattherassa apadānaṁ.  [intro]
    562  n=1     1. So ekadivasaṁ Satthu santike ...                            [gloss]
    563  n=3     3. Bahū me'dhigatā bhogāti ...                                 [gloss]
    564  (no n)  Dutiyatatiyacatutthapañcamāpadānāni UTTĀNĀNEVĀTI.              [dismissal]
    565  (no n)  Chaṭṭhāpadāne ... Bākulattherassa apadānaṁ.                    [intro]
    566  n=386   386. So arahā hutvā ...                                        [gloss]
    567  (no n)  Sattamāpadāne ... Girimānandattherassa apadānaṁ.               [intro]
    568  n=419   419. So arahattaṁ patvā ...                                    [gloss]
    569  (no n)  Aṭṭhamanavamadasamāpadānāni UTTĀNATTHĀNEVĀTI.                  [dismissal]

The placer currently produces, for vagga 40, **2 links by number and 132 by
ordinal word** — and the 132 land like this:

    ord 564  ← 33 canon paragraphs   "the 2nd, 3rd, 4th and 5th are self-evident"
    ord 565  ← 33 canon paragraphs
    ord 567  ← 30 canon paragraphs
    ord 569  ← 36 canon paragraphs   "the 8th, 9th and 10th are self-evident"

**69 of those 132 links point at a one-line sentence saying the commentary has
nothing to say.** `uttānāni eva` is the edition declaring silence, and the
placer is reading the declaration as a gloss. A reader who clicks is shown
"these are plain".

So the ordinal-word paragraphs are TWO kinds and the code treats them as one:

  - **intro** (561, 565, 567) — names the apadāna, quotes its opening words
    (`nagare Haṁsavatiyāti-ādikaṁ`), tells the elder's story. Real commentary,
    but on the apadāna's OPENING, not on all 257 of its verses.
  - **dismissal** (564, 569) — `uttānāni eva`, `uttānatthāni eva`. The opposite
    of a gloss. These should place NOTHING and their canon span is
    `not_commented`, which is what the edition says in so many words.

**A second defect, found in the same measurement and not in the handoff:** the
ordinal-word candidate SHADOWS the numbered one, because `place()` takes
`cand[0]`, the earliest candidate at or after the floor, and the intro sits
before the numbered gloss. Vagga 40 escapes it only because `Cattālīsama-`
(fortieth) is above the `v <= 12` cut in `APOS` and so ord 561 places nothing.
Where the intro IS matched, canon 1 and canon 3 would both land on the intro and
the paragraphs the edition itself numbers `1.` and `3.` would never be reached.
**Look for this before changing anything else: it moves links off paragraphs the
edition addressed by number, which is the strongest evidence there is.**

Recommended, for the reader to accept or refuse:

  1. an ordinal-word paragraph whose opening is a `uttāna-` dismissal places
     nothing, and its canon span is `not_commented`;
  2. an ordinal-word intro places only the FIRST canon paragraph of the apadāna
     it names — the one whose words it quotes — not the whole span;
  3. a numbered candidate beats an ordinal-word candidate for the same n,
     whatever their order.

All three REDUCE the link count, which is the direction §"SANDHI COST THREE
SEPARATE FIXES" warns about — so measure before and after, and check the drop
lands on the paragraphs above and nowhere else.

## Next, in order

1. **The three recommendations above**, as the reader decides them. Still blocks
   applying vaggas 2–42.
2. **The verbatim-repeat link target** — the other defect the reader found on
   08-07, untouched. `19Khu02` ord 3294 → `31KhuA12` ord **207**, which is the
   canon verse repeated, where the gloss is ord **210**. Record carries
   `by: None`, so it is an old-builder link. **Measure how many of the 5,376
   verbatim repeats are link targets before deciding.**
3. **The three inversions** (vaggas 18, 34, 35).
4. **Spot-check against the printed page** before applying —
   `_xc/hy2/20Khu03_vaggas2-42_dryrun.md`.
5. **The concordance gate** when vaggas 2–42 land. Reader's decision, not taken.
6. **`fix_vagga_heads.py` on the other 17 volumes**, one at a time.
7. **Audit the remaining `pipeline/` baselines for drift.**
8. **`20KhuA01` ord 174** carries a section head the nav does not.

## THE BOLD LEMMAS THE READER FOUND MISSING — MEASURED, NOT FIXED

Reader, 2026-08-08: "in the phrase *Tattha Buddhavīrāti* **Buddhavīrā** should be
bold ... also *Namo tyatthū* ... and *Sabbasattānamuttamā* and *yo maṁ dukkhā
pamocesi, aññañca bahukaṁ janan* and *sabbadukkhan*. I wonder if there are other
bolds missing."

There are, and every one he named is on ONE drawn line.

**The spans are all present in the data.** `bold/31KhuA12.bold.json` ord 210
carries 41 spans including `(120,130) Buddhavīrā`, `Namo`, `tyatthū`,
`Sabbasattānamuttamā`, `yo`, `maṁ`, `dukkhā`, `pamocesi`. Nothing is missing from
the extraction. What fails is the LOCATE: the verse branch draws the printed line
stream and finds each drawn line in the corpus paragraph by `indexOf`, and this
line is not found.

**The cause is the unrepaired line-break hyphen** — the open item the previous
handoff lists as "the hyphen repair (8,790 words, 109 volumes)". At character 125
the corpus text reads `catubbidhasammappadhānavīriya- nipphattiyā` and the drawn
line reads `catubbidhasammappadhānavīriyanipphattiyā`. One hyphen, and the whole
line loses its bold — and with it eight of the lemmas the reader was looking for.

**MEASURED over five volumes, 31,391 spans: 25,233 drawn (80.4%). A
hyphen-tolerant locate would draw 26,032 (82.9%) — +799 spans.** Per volume:
31KhuA12 95.0→95.6, 32KhuA13 89.7→90.1, 09DiT02 64.3→68.0, 25VsmT01 79.1→82.9,
29KhuA10 94.0→94.2.

**This partly contradicts what `reader2.html` says about itself.** Its comment
records 85.9% located and concludes the rest "are not reachable from the
ordinal-keyed spans and no reader change fixes them". For the hyphen class that
is false: joining `- ` before matching reaches them, and the reader's own example
is one. The other ~17% remains unexplained and unmeasured.

**Design note for whoever does it:** locate in the JOINED string and draw the
JOINED string with spans mapped into that address space. Mapping back to the raw
text and drawing that would put `vīriya- nipphattiyā` on the page — a hyphen the
reader would then be right to report.

## Opened by this session, not closed

**397 note numbers have no marker anywhere in their paragraph's text**, in any
form — counted while measuring the bracket forms. They are notes keyed to an
ordinal whose text does not carry the digit at all, so either the keying or the
extraction is off by a paragraph. Nobody has looked. It is 0.9% of 44,917.

**The marker→note pairing is unestablished for a third of the corpus.** 45,901
of 69,000 markers sit in a digit whose marker count and note count agree, and the
reader is told plainly about the other 23,099 rather than being shown a guess.
Closing that gap means keying notes to the marker's OFFSET, not to its number —
which is the same shape of problem as the paragraph number not being a key.

**The verse map re-segments markers away from the paragraph text**, and nobody
has asked why. `check_fn_markers.js` reports the number on every volume that has
one: 09DiT02 907 in `text` against 868 in the drawn lines, 19Khu02 927 against
925, 27Khu10 494 against **564 the other way**. The gate deliberately does not
absorb it. It is a question about `verse/`, not about the apparatus, and it is
the kind of quiet divergence §"a one-sided ratchet is silent in one direction"
is about.

## Still open from the previous handoff — unchanged

Parked by the reader: the verbatim-repeat display (5,376 of 22,527), `none` vs
`dim`, the APD tab's defaults and gear, capping the concordance tooltip.

BLOCKBREAK still off; the hyphen repair (8,790 words, 109 volumes); classes 1
and 2 suspect; **position, unmeasured for 114 of 118 volumes**; the verse branch
for band blocks; the `WLV` gate; `.gitignore`'s stale store rule; the offline
package (§2 permission before bundling PDFs); `claude/` has never existed in git
though four files cite it; Node 20 deprecation on the Pages workflow.

## Hazards — unchanged, plus two

- **`.git` is write-protected from the sandbox.** Commit message goes to the
  repository root with a `*.bak` name.
- **Files under `_xc/` cannot be deleted from the sandbox either** — `rm` returns
  "Operation not permitted". `_xc/hy2/_dump.js` and `_xc/hy2/_gap.js` are
  throwaway probes left behind for that reason; delete them on the host.
- **jsdom OOMs at about 20 volumes in one process.** `check_fn_markers.js --all`
  dies around `06VinSg06` with `Ineffective mark-compacts near heap limit`. Run
  it in batches of 4–8 volumes per process; the 118-volume sweep was done that
  way.
- Do not write an angle-bracket placeholder into a shell command.
- Clear git locks on the host at the end of every session.
- Never "Re-run failed jobs" on Pages; start a fresh run.
- **`stamp_build.py --write` is not optional after any change under `site/`.**
  Done this session, twice: `6151ac21bbbd` → `f051d390acfe` → `eac8bb93c9fd`.
- **Run the placer for the range LAST.**

## The method

> **RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.**

> **COMPARE AGAINST THE PRINTED PAGE, NEVER AGAINST THE CORPUS — AND THAT
> INCLUDES COMPARING AGAINST YOUR OWN OUTPUT.**

> **A REFACTOR THAT TURNS LINKS INTO ASSERTIONS OF SILENCE IS THE MOST DANGEROUS
> SHAPE OF CHANGE IN THIS PIPELINE.**

And the addition this session earned:

> **WHEN A CHECK DISAGREES WITH THE READER, SUSPECT THE CHECK FIRST.** Two
> versions of `check_fn_markers.js` reported their own mistakes as the reader's
> failures — 30 invented markers that were the verse map, then a near-total
> blackout that was an exclusion throwing away the ṭīkā's own prose. Both would
> have been believed if the numbers had been slightly less absurd. Every gate in
> `pipeline/` should be assumed to have one of these in it until it has been
> made to fail on purpose.
