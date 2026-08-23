# Closing 2026-08-09, re-verified 2026-08-23 — where things stand

> **Read this box first; it is newer than the rest of the file.**
>
> **2026-08-23 — nothing is owed and nothing is broken.** Checked, not assumed:
>
> * **The site is current.** Live `build.json`, cache-busted, is
>   **`c97a3f99fdb2` dated 2026-08-16** — the repository's own HEAD build. The
>   *uncached* fetch of the same URL still answers `1f2819473f91 / 2026-08-08`,
>   the v2.6.0 stamp. **That is the third time this cache has told this project
>   the deploy failed.** It has not. Never read a deploy without a cache-buster.
> * **The `hw` store is on R2**, so §3a below is finished, upload and all —
>   see `_xc/hy2/start_here_2026-08-09.md` §0b for the probes and the negative
>   control. `WLV 20260810a` matches the live build.
> * **Every offline gate is green**, re-run today, a week after v2.8.0:
>   `check_links.py` and `check_concordance.py` both "no measure regressed",
>   `check_apd_gear.js` all green, `check_search.js` all green,
>   `check_lookup_reach.js` 12/0.
> * **v2.8.0 is released and deposited**, its DOI read from the record and in
>   `CITATION.cff` (commit `96e1eb0e8`). The niggahita display toggle — edition
>   ṁ ↔ modern ṃ, display only — is live.
>
> **`RUN_ON_HOST.md` is stale**: it still describes the v2.7.1 release, which
> shipped two releases ago. Nothing in it is owed. Do not work from it.

---

## 1. ~~Two commands, then you are done for the day~~ — done, 2026-08-09

```bash
cd ~/Documents/OSBCT
rm -f _probe_band_verse.js      # my jsdom probe; the sandbox cannot delete it
./push.sh                       # COMMIT_MSG.bak carries the findings commit
```

That commit changes no text, moves no link, and touches nothing under
`site/` — so there was **no stamp, no Pages run and no R2 sync needed.**
It was the two findings notes plus the corrected handoff.

## 2. Where things stood on 08-09 (superseded by the box above)

**Shipped and clean.** v2.7.0 and v2.7.1 both released, deposited and in the
citation ledger — `10.5281/zenodo.21863987` and `10.5281/zenodo.21864177`, both
read from the record. Live site serves build `92157e0692e0`, verified
cache-busted. R2 fully synced: bucket counts match git, the origin gate is green
at 38/38, and the family store returns 200. Errata register: **49 confirmed, 18
candidate, 1 resolved, of 68.** Gates green — links and concordance "no measure
regressed", search all green, `check_derived --deep` all fresh.

**Nothing is broken and nothing is unshipped.** Everything below is either work
you parked deliberately, or something nobody has looked at yet.

---

## 3. What to tell a new chat

### 3a. ~~The dictionary gate~~ — **DONE 2026-08-10, UPLOAD CONFIRMED 2026-08-23**

Kept because the account of *why* it was five coupled steps is still the best
description of what a store change costs. All five landed: the new `hw` store
(191,928 keys, largest shard 147,337 B under the 150 kB cap), `lem` untouched,
`check_apd_gear.js` extended and run red first, and the R2 upload — the step
that was owed for thirteen days — now verified against the live origin.
**Only item 5 remains, and it always was separate: the §2/§9 redistribution
question.** What follows is the brief as it was written.

It is not vague, it is **five coupled steps, each with a gate**, and one of them
touches production:

1. The key set roughly **quadruples** — 52,757 → 210,111+ headwords. Sharding,
   the 150 KB byte cap and the gz layer all have to be re-measured, not assumed.
2. The store is **served from Cloudflare R2**, not from Pages. So it needs an
   upload and a `WLV` bump, and until both happen production keeps serving the
   old store while the repo looks fixed. That is the failure mode the DPD family
   rebuild already hit once.
3. `panel.js` needs a new lookup path, and the **APD gear list** must learn the
   new sections.
4. `pipeline/check_apd_gear.js` (27 assertions) must be **extended and made to
   fail on the current build first**.
5. **The licence question gets louder.** These sources sit in `lookup_eval/`
   because redistribution is unresolved (§2, §9). Making 163,453 more headwords
   reachable does not change that, but it does raise the stakes of getting it
   settled — and it must be settled separately, not inside this fix.

Two facts that make it tractable, both verified:

* **The safe design is a NEW store, not a wider `lem`.** Key it on the
  dictionaries' own headwords, leave `lem` and the DPD path untouched, and have
  the panel consult the new store when `lem` misses. Additive, so no existing
  gate can regress.
* **That design needs no GoldenDict.** `_panel/build_eval.py:48` reads
  `GD_DIR`, defaulting to a path that no longer exists — re-running the whole
  eval build would need the GoldenDict folder mounted again. But the two files
  the fix needs, `_dictsrc/pced_full.jsonl.gz` (24 MB) and `_dictsrc/pm12e.csv`
  (42 MB), are **in the folder already**.

**One hazard to state up front: `_dictsrc/` is gitignored** (`.gitignore:183`).
Those sources exist on your machine and nowhere else — not in git, not in the
Zenodo deposit. Do not let a session assume it can re-fetch them.

Paste this:

> Continuing OSBCT. Repo at Documents/OSBCT; request access to that folder.
> Read `_xc/hy2/start_here_2026-08-09.md` §0b, then
> `claude/dpd_gates_the_abhidhana.md` in full.
>
> The task: make the Tipiṭaka Pāḷi-Myanmā-Abhidhāna and the APD books reachable
> by their OWN headwords instead of through DPD's index. Today 163,453 of
> 210,111 headwords (77.8%) are unreachable because `_panel/build_eval.py:64–89`
> keys everything on `LEMMAS`, which is built from DPD. §9 makes the Abhidhāna
> the only dictionary that is an authority and ranks DPD lowest; the build
> inverts that.
>
> Constraints, in order:
> 1. Do NOT widen `lem`. Build a SEPARATE store from `_dictsrc/pced_full.jsonl.gz`
>    and `_dictsrc/pm12e.csv` — both already in the folder — keyed on the
>    dictionaries' own accented headwords. Additive, so no existing gate can
>    regress. `_dictsrc/` is gitignored; it exists nowhere else.
> 2. Mind the key case: PCED's `acc` is capitalised (`Yathānisinna`) while
>    `panel.js look()` tries the exact key then `toLowerCase()`. Fold on write.
> 3. Measure sharding and the 150 KB cap BEFORE building. The key set roughly
>    quadruples.
> 4. Extend `pipeline/check_apd_gear.js` and make the new assertion FAIL on the
>    current build first — `yathānisinna` must return the book B and book K
>    entries. Show me the failing run before the fix.
> 5. The store is served from R2: the job is not done until `r2_upload.sh` has
>    run and `WLV` is bumped. Say so explicitly when you reach that point.
> 6. Do not touch the §2/§9 redistribution question. It is separate.
>
> Separately and cheaply, if there is time: a prefix fallback in the word-lookup
> pane before the "no entry" message, showing the corpus forms that begin with
> what was typed. `lookup/freq` already has them — 12 forms of `yathānisinna`,
> 52 occurrences. It is the mirror of the `atappaka` fix at `panel.js:714`.

### 3b. Alternative, if you would rather do the links

> Continuing OSBCT. Repo at Documents/OSBCT; request access to that folder.
> Read `_xc/hy2/start_here_2026-08-09.md` — it supersedes the 08-08 pm handoff
> and carries three retractions from that session, which are there on purpose.
> Then read `claude/vimanavatthu_atthakatha_quotes_then_glosses.md`.
>
> The work I want to start is item 1 of that handoff: the commentary→canon link
> for `19Khu02 → 27KhuA08`, taken as one book. The structure is already measured
> — quotes reprinted under the canon's numbers, then glosses restarting at the
> same numbers — and every link currently lands on the quote. Do not write a
> corpus-wide rule; the offsets take 26 distinct values in that one volume and
> half the quotes have no gloss at all.
>
> Before changing anything, add the failing assertion to `pipeline/check_links.py`
> — `19Khu02` ¶333 must not resolve to `27KhuA08#467`, which is the verse
> reprinted, when the comment is `#511`. Make it fail on the current build first.

**The four rules that were earned the hard way on 08-09, and should be said to
any session that starts fresh:**

1. **Never typeset filler Pāḷi**, not even in a sketch. A mockup of this corpus
   is a claim about this corpus. Pull the paragraph.
2. **Render, do not infer.** Line breaks come from `verse/`, not from the `text`
   field; nothing about the reader can be concluded from the source.
3. **Bust the cache when measuring what is live**, or you are measuring the past.
4. **Never key the canon by paragraph number** — see
   `claude/paragraph_numbers_are_not_a_key.md`. It caught me again on 08-09.

---

## 4. Everything that remains

### Ready to decide — yours, nothing blocks them

* **`none` vs `dim`.** A dead "no commentary" and a condemned "link disputed"
  are both grey dashed chips and both called dimmed. 3,163 concordance
  violations are due to arrive in whichever style is chosen. Options were
  sketched; **nothing has been rendered against the real reader** — worth an
  hour to photograph both states before deciding.
* **Capping the concordance tooltip.** Seven volume codes for `18Khu01`. Cap at
  three with "+4 more", show a count only, or leave it.
* **The legacy links artifact** `check_derived` flags — loaded by nothing.
  Retire or rebuild.
* **The search heavy half** — per-volume shard split into postings + text. Only
  if common-word searches actually hurt you in use.

### The links — one book at a time

* ~~`19Khu02 → 27KhuA08` first~~ — **DONE 2026-08-23. 437 links moved off the
  reprint and onto the comment**, gated red first, verified on four printed
  pages, 470 uncommented verses deliberately left alone.
  `claude/vimanavatthu_links_moved_to_the_gloss.md`. 16 pairs remain.
* **RE-MEASURE THE WORKSHEET BEFORE USING IT.** Every figure in
  `claude/link_targets_land_on_the_requotation.md` is an undercount — its test
  keeps the canon's inline footnote-marker digits, so it called 168 verbatim
  reprints different in this pair alone (500 → 907, 267 → 435). The four rows
  reading "0 glosses found" are the least trustworthy.
* Next in this line: `19Khu02 → 28KhuA09` — same canon volume, offset 3.
* **The shadowing defect FIRST** within the placer work: it moves links off
  paragraphs the edition addressed *by number*, which is the strongest evidence
  there is.
* Then: the three placer recommendations (blocking 20Khu03 vaggas 2–42, computed
  in `_xc/linksk_toc/`), the three inversions (vaggas 18, 34, 35), the
  printed-page spot check `_xc/hy2/20Khu03_vaggas2-42_dryrun.md`, the
  concordance gate when vaggas 2–42 land.
* A printed-page ground-truth sample and provenance tiers in the UI are what
  turn "accurate" into a number.

### Measured, not repaired

* **The unnumbered-siglum class.** 2,535 paragraphs in 76 volumes carry a `*`,
  `+`, `x` or `( )` mark; **1,427 have no apparatus entry at all.** Two known
  defects: the `+` note absent from `10Ma02.app.json` ¶296, and unnumbered notes
  glued onto numbered ones. `_review/sigla_report.json`.
* **The verse branch for band blocks** (`asSpine`). Confirmed by rendering.
  Needs care: `hide/` maps assume the branch runs, and on 20KhuA01 ten hidden
  ordinals are merge-absorbed into neighbours' verse entries.
* **The hyphen family's remainder** — the consonant branch (1,521, ca-saddo
  class, unadjudicated), `extract.py:204` hygiene, and the undrawn bold spans:
  **remeasure before believing the old ~17%.**
* **18 register candidates**, plus the per-entry audit of the 22 other-layer
  entries. The PDF correction itself (ToUnicode injection, one volume first)
  stays on standby by your decision.

### Never looked at

* **397 note numbers have no marker anywhere in their paragraph** — 0.9% of
  44,917. Either the keying or the extraction is off by a paragraph.
* **The marker→note pairing is unestablished for a third of the corpus** —
  23,099 of 69,000. Closing it means keying notes to the marker's OFFSET.
* **The verse map re-segments markers away from the paragraph text** — 27Khu10
  reports 494 against 564 *the other way*. A question about `verse/`.
* **X007**, now suspect for the same stale-snapshot reason as the nine
  withdrawn. Check it against the live PDF before asking about it again.
* **`corpus/*.errata.json` still feeds the review sheet** — refresh the snapshot
  or have `build_glyph_review.py` read the served text, or the next sheet
  re-raises the nine withdrawn sites.

### Housekeeping

* Nine kintipañha heads still tail-of-paragraph; BLOCKBREAK off; `position`
  unmeasured for 114 of 118 volumes; the WLV gate; the offline package (§2
  permission first); `.gitignore`'s stale store rule.
* **Three gate gaps.** `check_r2_origin.js` cannot tell "reachable and absent"
  from "unreachable" — its negative control passes when the network is down —
  and it covers neither `lookup_eval/family/` nor `form/`. The shape of a real
  404 from that bucket is now known (empty body, no `Content-Type`, unlike a
  present object's `application/gzip`), so the discrimination is cheap to add.
* **And the third, found 2026-08-23: nothing checks that the reverse link maps
  are derivable from the forward ones.** They had drifted again — `32KhuA13`
  was missing 33 entries, and `28KhuA09`/`41KhuA22` had six entries attributed
  to the wrong canon paragraph — all of it predating this session's work and
  none of it noticed by any gate. Rebuilt and now consistent, but the same
  silence will return after the next link repair that forgets `build_rev.py`.
  §7b of `claude/vimanavatthu_links_moved_to_the_gloss.md`.
* `v2.7.0` is a lightweight tag where v2.4.0–v2.6.0 are annotated. It has a DOI.
  **Leave it**; recorded so nobody rediscovers it as a defect.
