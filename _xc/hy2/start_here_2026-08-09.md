# START HERE — 2026-08-09

Supersedes `start_here_2026-08-08_pm.md`, which is still correct about
everything except its items 4a4/4a5 (both now done — see §Done below) and its
stated convention about `corpus/*.txt`, which was wrong for the right
observation and is corrected in `claude/x_rows_are_a_stale_snapshot.md`.

---

## 0. THE DEPLOY IS FINE. THE FIRST INSTRUMENT THAT SAID OTHERWISE WAS A CACHE.

**~~THE SITE IS TWO RELEASES BEHIND~~ — WRONG, AND RETRACTED THE SAME HOUR.**
This section first reported that `buddha-dhamma.net/build.json` served
`1f2819473f91` dated 2026-08-08 — commit `d6c57c3f`, the v2.6.0 metadata — and
concluded that every push of 2026-08-09 had failed to deploy, twelve commits'
worth including the hyphen repair, the italics removal, v2.7.0 and v2.7.1. It
went further and named a mechanism: the ten-minute `deploy-pages` timeout the
workflow file documents at length.

**The reader checked the Actions run list and every run was green** — #187 for
commit `5363249`, 1m33s. Re-fetched with a cache-buster
(`build.json?cb=…`), the live answer is **`92157e0692e0`, dated 2026-08-09**,
identical to the repository. The first fetch had been served from cache; the
second reading of the same URL returned the same stale bytes, which is exactly
what made it look confirmed.

**Verified end to end, not just by the stamp:** the live `errata.json` carries
E042 with `suggested_reading: pathavīkasiṇādivaḍḍhane`, confidence `high`. The
deployed site carries this session's content.

> **THE FAILURE MODE WAS THE PROJECT'S OWN, ONE LAYER OUT.** "Compare against
> the printed page, never against the corpus" has a sibling: *do not read a
> deploy through a cache*. A cached response is an old artefact wearing a fresh
> URL, and believing it produced a confident, detailed, entirely fictional
> diagnosis — complete with a plausible mechanism drawn from the workflow's
> real history. **Any future check of what is LIVE must bust the cache, or it
> is measuring the past.** The corollary held again: when the check disagreed
> with the reader, the check was wrong.

**THE R2 UPLOAD IS UNCONFIRMED, AND CANNOT BE CONFIRMED FROM THE SANDBOX.**
`stores/lookup/` changed with the E042 word, and the DPD refresh of 2026-08-09
has never been verified as uploaded. `pipeline/check_r2_origin.js` run from
here reports 3 passed / 16 failed, but **every failure is `fetch threw: fetch
failed`** — the sandbox has no route to `dict.buddha-dhamma.net`. That is not
evidence about R2.

> **AND THE GATE CANNOT TELL THE DIFFERENCE.** Its negative control —
> "missing shard 404s" — PASSED, for the same reason everything else failed:
> the fetch threw. A control that passes when the network is down is not a
> control. `check_r2_origin.js` needs to distinguish "reachable and absent"
> from "unreachable" before its verdict means anything. Run it on the host
> until then.

---

## Done since the 08-08 pm handoff

* **4a4 APPLIED.** 41 register entries candidate → confirmed (**49 confirmed,
  18 candidate, 1 resolved, of 68**). Eleven suggested readings were WRONG in
  the register and are corrected against the printed page with the superseded
  reading kept. E042 settled by the reader as `vaḍḍhane` — **one word of served
  text moved**, Δ0 in characters, pbreak re-derived byte-equal. E044 confirmed
  as the applied pair already read. The nine X-rows **withdrawn, not recorded**:
  `claude/x_rows_are_a_stale_snapshot.md`.
* **v2.7.0 and v2.7.1 both released and deposited**, DOIs
  `10.5281/zenodo.21863987` and `10.5281/zenodo.21864177`, both read from the
  record and both describing themselves correctly at minting.

---

## Remaining, in the reader's chosen order (links LAST)

### 1. Parked display decisions — and the first of them IS NOT A DISPLAY QUESTION

**THE VERBATIM-REPEAT ITEM IS A LINK DEFECT. FOUND WITH THE READER 2026-08-09;
see `claude/vimanavatthu_atthakatha_quotes_then_glosses.md`.** The
Vimānavatthu-aṭṭhakathā prints, per vimāna: unnumbered nidāna prose, then the
canon's verses REPRINTED under the canon's own numbers, then the comments
RESTARTING at those same numbers. `27KhuA08`: 1,480 paragraphs — 620 quotes, 762
glosses, 98 prose, 106 points where the number decreases. **Every link lands on
the quote.** `19Khu02` ¶333 → `27KhuA08#467` (the verse reprinted) when the
comment is `#511`. Corpus-wide: **4,956 of 32,504 direct links (15.25%) land on
a re-quotation, across 17 volume pairs, all Khuddaka verse works** — against
5,376 known verbatim repeats, i.e. nearly all of them are live link targets.
Hiding the duplicate, which is what the parked item proposed, would have hidden
the only thing the link reaches.

**AND NO CORPUS-WIDE RULE IS AVAILABLE.** In `27KhuA08` the quote→gloss offset
takes **26 distinct values from 1 to 44**, and only 301 of 620 quotes have a
same-numbered gloss at all — the edition does not comment on every verse.
Four of the seventeen pairs have ZERO same-numbered glosses, including
`19Khu02 → 31KhuA12`, whose gloss the older handoff already located by hand
three paragraphs on under a DIFFERENT number. Per-book worksheet:
`claude/link_targets_land_on_the_requotation.md`.

> **The reader, 2026-08-09: "how the Commentary and Subcommentary are related to
> the Pāḷi has to be taken one book at a time."** Take it one book at a time.
> `19Khu02 → 27KhuA08` is the one already read and measured; start there.

Still genuinely display decisions, and still the reader's: `none` vs `dim`,
capping the concordance tooltip.

**!!! A DISPLAY MOCKUP OF THE FIRST OF THESE CONTAINED FABRICATED PĀḶI, 2026-08-09.**
Asked to show the options, I wrote a plausible-looking verse —
`Yathā pi rukkho asamaṁ phalaṁ…` — instead of reading one. It is not in the
edition, not in the corpus, not anywhere. The reader caught it on sight and
asked where it came from. **It reached no file** (the repository was searched;
the fabrication existed only in the chat widget), but that is blast radius, not
excuse. **A mockup of this corpus is still a claim about this corpus. Never
typeset filler Pāḷi — pull the paragraph, even for a sketch.** This is the same
principle as "compare against the printed page", applied to the one artefact
nobody thought to apply it to.

**MEASURED WHILE FIXING IT, AND IT QUESTIONS THE HANDOFF'S OWN EXAMPLE.** The
real pair at this site is `19Khu02` ¶618 (printed p.48) against `27KhuA08`
idx 510 / ¶618 (printed p.133), and **they are NOT exactly equal**:

    canon        Imāsāhaṁ1 dhammaṁ sutvā2, … Svāhaṁ tattha gamissāmi3,
                 yattha gantvā na socareti.
    commentary   Imāsāhaṁ dhammaṁ sutvā, … Svāhaṁ tattha gamissāmi,
                 yatta gantvā na socare”ti.

Three differences: the canon carries footnote markers 1/2/3 and the commentary
none; **`yattha` against `yatta`**; and `socareti` against `socare”ti`. So this
pair is *not* one of the 5,376 exact-text-equality cases the item is about — the
handoff has been illustrating the verbatim-repeat question with a near-repeat.
`yattha`/`yatta` in particular is either a real difference between the two
printed layers or an extraction defect, and **nobody has looked at the printed
page to say which**. Settle that before using this site as the example again.

**AND THE "FLATTENING" CLAIM WAS ALSO WRONG AS FIRST STATED.** I read the
`text` field of `27KhuA08.json`, saw one prose run, and said the reader draws it
flat. The reader's own screenshot of `19Khu02` ¶618 killed that: it draws THREE
LINES with markers and apparatus, matching printed p.48 exactly — and its `text`
field is a single prose run too. **The line breaks come from `verse/`, not from
`text`, so nothing about the reader can be concluded from the text field.**
Reading the source instead of rendering it, again, and the third check of the
day to be wrong before the thing it was checking.

**What the CODE says, still unrendered and therefore still a hypothesis.**
`reader2.html:1932` sets `const asSpine = kind==='canon' || !!(opts&&opts.spine)`
and the verse branch at :2153 runs only `if(asSpine && vmap && vmap.groups)`. So
the pādas are drawn whenever the volume is the spine or the canon — and would be
flattened only where a commentary paragraph is drawn as a **band** beside the
canon, which is exactly the view the "printed twice" complaint comes from. That
matches the item already standing open as *"the verse branch for band blocks"*.

**SETTLED BY RENDERING, 2026-08-09 — jsdom over the real reader at build
`92157e0692e0`, `19Khu02#413` (¶618, printed p.48) with the A layer clicked on.**
The band draws **20** blocks under that one canon paragraph, in this order:

    618.  333. 334. 341. 373. 381. 389. 397. 405. 413. 437. 445.
    477. 517. 525. 557. 565. 573.  617. 618.

* **The first block IS the verbatim repeat** — `Imāsāhaṁ dhammaṁ sutvā, kāhāmi
  kusalaṁ bahuṁ…`, printed p.133 — and it renders with **zero child `<div>`s:
  ONE PROSE RUN.** The canon paragraph immediately above it renders as three
  lines. So the flattening is real, it is confined to the band, and it is
  exactly what makes the page read as a duplicate.
* The last two blocks (617, 618) are the genuine glosses and are prose in the
  edition too — correctly drawn.
* The reader's own screenshot showed the canon in the `P`-only view, where the
  verse branch runs and everything is right. **The defect is invisible until the
  A layer is on**, which is why three earlier readings of this missed it.

**So it is a DEFECT, not a display decision, and the code says so in its own
comment** (`reader2.html:1929`): the verse branch was opened "for the SPINE only
… and not for a band block hanging under a canon paragraph, which is a different
question and is left exactly as it was". That is the standing item *"the verse
branch for band blocks"*. Fixing it needs the same care the spine fix needed —
`hide/` maps are written assuming the branch runs, and on 20KhuA01 ten hidden
ordinals are `merge-absorbed` into neighbours' verse entries.

**Do the `asSpine` fix FIRST. Only then ask the display question**, which
becomes a much cleaner one: should the band repeat a verse the canon is already
showing beside it?

**Also visible in that render, and NOT this item:** the band pulls 18 further
paragraphs that gloss *other* verses (333–573) in between. That is link
precision — the placer — which is the work parked deliberately last.

Verified separately, by reading the store: `verse/27KhuA08.json` key `510` holds
the three pādas, so the data for the fix is already shipped.

### 2. Search heavy half
Per-volume shard split into postings + text — **only** if the reader's
live-network verdict says common-word searches hurt.

### 3. What remains of the hyphen family
The consonant branch (1,521, ca-saddo class, unadjudicated per hy2 §2);
`extract.py:204` hygiene; and the **~17% undrawn bold spans still
unexplained** — smaller since the repair, so **remeasure before believing the
number**.

### 4. Housekeeping
The NINE kintipañha heads still tail-of-paragraph (deferred corpus split,
2026-07-28r; the two dropped gāthā heads are the same family). `check_derived`'s
flag: the legacy links artifact is loaded by nothing — **reader to decide retire
vs rebuild**. BLOCKBREAK off. `position` unmeasured for 114 of 118 volumes. The
WLV gate. The offline package (§2 permission first). `.gitignore`'s stale store
rule.

### 4a. The unnumbered-siglum extraction class — MEASURED, NOT REPAIRED
Opened by E021 and sized by `pipeline/measure_sigla.py`: **2,535 paragraphs in
76 volumes carry a `*`, `+`, `x` or `( )` mark, and 1,427 have no apparatus
entry at all** (`( )` 188/28, `+` 597/298, `*` 3,470/2,067, `x` 1/1). Two known
defects behind it: the `+` note is **absent** from `10Ma02.app.json` for ¶296
(text survives in `_xc/hy1/blocks*/10Ma02.json`), and unnumbered-siglum notes
elsewhere are **glued** onto numbered ones (¶295 note 2 carries the `( )` note
appended). "Entry present" deliberately does not claim the note is there
standalone — the gluing needed the printed page to see. Detail
`_review/sigla_report.json`.

### 4a2. Loose ends from the review sheet
**X007 is unanswered and now suspect** — it is an 08DiA02 sidecar row of the
same stale-snapshot class as the eight that were withdrawn; **check it against
the live PDF before asking the reader again**. And
**`corpus/*.errata.json` should stop feeding the review sheet**
(`build_glyph_review.py:73`) or the next sheet re-raises the withdrawn nine:
either refresh the snapshot or have the sheet read the served text. Reader's
choice; nothing patched silently.

### 4b. The errata register and the PDFs
**18 candidates remain** in the register. What remains of 4b: the **per-entry
audit of the 22 other-layer entries** (sections/ headings, incipit maps), and
the **PDF correction itself** — ToUnicode injection, one volume first — which is
**ON STANDBY by the reader's decision** and connects to the §6 scope question.
`docs/PDF_ERRATA.md` (regenerate with `pipeline/build_pdf_errata_doc.py`) is the
work list. Every candidate stays pending scholarly confirmation.

### 5. THE LINKS — postponed by the reader, deliberately last
The three placer recommendations (block applying 20Khu03 vaggas 2–42, computed
in `_xc/linksk_toc/`); **the shadowing defect FIRST** — it moves links off
paragraphs the edition addressed by number, the strongest evidence there is; the
verbatim-repeat target measure (`19Khu02` ord 3294 → `31KhuA12` ord 207 where the
gloss is 210 — measure how many of the 5,376 repeats are link targets first); the
three inversions (vaggas 18, 34, 35); the spot-check against the printed page
(`_xc/hy2/20Khu03_vaggas2-42_dryrun.md`); the concordance gate when vaggas 2–42
land. And the assessment of 08-08: a printed-page ground-truth sample and
provenance tiers in the UI are what turn "accurate" into a number.

---

## Opened, not closed — nobody has looked

* **397 note numbers have no marker anywhere in their paragraph's text**, in any
  form. 0.9% of 44,917. Either the keying or the extraction is off by a paragraph.
* **The marker→note pairing is unestablished for a third of the corpus** —
  45,901 of 69,000 markers sit where marker count and note count agree; the
  reader is told plainly about the other 23,099 rather than shown a guess.
  Closing it means keying notes to the marker's OFFSET, not its number — the
  same shape as the paragraph number not being a key.
* **The verse map re-segments markers away from the paragraph text.**
  `check_fn_markers.js` reports it on every volume that has one (09DiT02 907 vs
  868, 27Khu10 494 vs **564 the other way**) and deliberately does not absorb it.
  A question about `verse/`, not the apparatus.
* **`v2.7.0` is a lightweight tag** where v2.4.0–v2.6.0 are annotated. Harmless,
  it has a DOI, **leave it**; recorded so nobody rediscovers it as a defect.

---

## Hazards — unchanged

* `.git` is write-protected from the sandbox; commit message goes to the root
  as `*.bak`. **Files under the repo cannot be DELETED from the sandbox either**
  — `rm` returns "Operation not permitted". Left for the host this session:
  `_review/clips/`, `_xc/hy2/_dump.js`, `_xc/hy2/_gap.js`,
  `site/reader/pbreak/25VsmT01.json.preE042`, and the two `*.pre_verdicts`
  backups under `data/`.
* jsdom OOMs at about 20 volumes in one process — run `check_fn_markers.js` in
  batches of 4–8.
* Do not write an angle-bracket placeholder into a shell command.
* Clear git locks on the host at the end of every session.
* Never "Re-run failed jobs" on Pages; start a fresh run.
* **`stamp_build.py --write` is not optional after any change under `site/`.**
* **Run the placer for the range LAST.**

---

## The method

> **RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.**

> **COMPARE AGAINST THE PRINTED PAGE, NEVER AGAINST THE CORPUS — AND THAT
> INCLUDES COMPARING AGAINST YOUR OWN OUTPUT.**

> **A REFACTOR THAT TURNS LINKS INTO ASSERTIONS OF SILENCE IS THE MOST
> DANGEROUS SHAPE OF CHANGE IN THIS PIPELINE.**

> **WHEN A CHECK DISAGREES WITH THE READER, SUSPECT THE CHECK FIRST.** Earned
> again on 2026-08-09, twice in one session: a probe reported ten sound rows as
> failures because it matched the reader's typed string instead of the
> adjudicated one, and a second reported three live corrections as missing
> because it demanded a prefix where the register keys on the longer hyphenated
> word. Both were the check.

And the two this session added:

> **A CENSUS OVER A STALE ARTEFACT MEASURES THE ARTEFACT, NOT THE EDITION.**

> **A SUMMARY CAN CONTRADICT THE DATA IT SUMMARISES, AND THE SUMMARY IS WHAT
> GETS READ.** `glyph_errata.json` called a class unanimous — "7/7, high" —
> while one of its own entries had always carried the dissenting correction.
> Nothing was broken by it; a machine reading the summary to propose the next
> correction would have been.
