# Closing 2026-08-09 — what to run, and what to tell the next session

---

## 1. Two commands, then you are done for the day

```bash
cd ~/Documents/OSBCT
rm -f _probe_band_verse.js      # my jsdom probe; the sandbox cannot delete it
./push.sh                       # COMMIT_MSG.bak carries the findings commit
```

That commit changes no text, moves no link, and touches nothing under
`site/` — so there is **no stamp, no Pages run and no R2 sync needed.**
It is the two findings notes plus the corrected handoff.

## 2. Where things stand

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

Paste this:

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

* `19Khu02 → 27KhuA08` first: measured, read, and the note above says what a fix
  needs. 17 pairs in total —
  `claude/link_targets_land_on_the_requotation.md`.
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
* **Two gate gaps.** `check_r2_origin.js` cannot tell "reachable and absent"
  from "unreachable" — its negative control passes when the network is down —
  and it covers neither `lookup_eval/family/` nor `form/`.
* `v2.7.0` is a lightweight tag where v2.4.0–v2.6.0 are annotated. It has a DOI.
  **Leave it**; recorded so nobody rediscovers it as a defect.
