# START HERE — 2026-08-09

Supersedes `start_here_2026-08-08_pm.md`, which is still correct about
everything except its items 4a4/4a5 (both now done — see §Done below) and its
stated convention about `corpus/*.txt`, which was wrong for the right
observation and is corrected in `claude/x_rows_are_a_stale_snapshot.md`.

---

## 0. TWO THINGS ARE UNFINISHED RIGHT NOW, AND ONE IS LIVE

**THE SITE IS TWO RELEASES BEHIND.** Measured 2026-08-09:
`buddha-dhamma.net/build.json` serves **`1f2819473f91`, dated 2026-08-08**,
while the repository is at **`92157e0692e0`**. So neither v2.7.0 nor v2.7.1
has reached Pages. Zenodo has both deposits (21863987, 21864177); readers have
neither. **A fresh Pages run is the first thing the next session should ask
about** — GitHub → Actions → *Run workflow*, never "Re-run failed jobs".

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

### 1. Parked display decisions — the reader's, untaken
Verbatim-repeat display (5,376 of 22,527), `none` vs `dim`, capping the
concordance tooltip.

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
