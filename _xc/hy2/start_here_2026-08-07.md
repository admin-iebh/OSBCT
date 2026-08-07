# START HERE — after 2026-08-07

<!-- SESSION END 2026-08-07. Supersedes start_here_2026-08-06_pm.md, which is
     still correct about everything except the deploy: that is now done.
     Read this block, then §"Next, in order". -->

## What changed this session

**The A/B/C/D decision was made by the reader and executed the same day: D + B.**
The stores are out of `site/` and in `stores/`, still tracked; they are served from a
Cloudflare R2 bucket at `dict.buddha-dhamma.net`. `docs/DEPLOY_SCALE.md` §6 is no longer
suspended — **§6a is the instruction and everything below it in §6 is the superseded
record.**

**Measured, not projected:**

| | |
|---|---:|
| `git ls-files site/` | **1,977** (was 26,576) |
| `git ls-files stores/` | 24,599 |
| tracked bytes in `site/` | 473 MB |
| objects in the bucket | 24,599 — `lookup` 7,319, `lookup_eval` 17,280 |
| **deploy run #126** | **2m 01s, success** |
| `curl -sI https://buddha-dhamma.net/lookup/index.json` | **404** |
| deployed `panel.js` | `var BASE = 'https://dict.buddha-dhamma.net/lookup/'` |
| the reader on the live site | **word lookup works** |

**One 2-minute run does NOT prove the fix, and should not be written down as if it did.**
Run #123 published all 26,576 files in 2m05s on a healthy day — §1a records it. What
changed is that the ceiling should now be *unreachable* rather than merely *un-hit*. The
next several deploys are the evidence. **If a run still times out at ~11m40s with 1,977
files, the file count was never the cause** and §1a's other two shapes are where to look:
an unacquired runner, or a pending deployment holding the environment.

**Option A (resharding) was NOT built and is not needed for the deploy.** §3a's re-pricing
stands and is unaffected: `CAP` is a ceiling the sharder never merges against, so it was
never the parameter change §3 described. Shard sizes are unchanged, so **per-lookup
bandwidth is unchanged** — the latency cost §3 accepted as A's price is simply not paid.

**The gate that made this safe:** `pipeline/check_r2_origin.js`, written before the bucket
existed and run against localhost first, where it produced 22 content passes and **16 CORS
failures** — the correct answer there, and the evidence that its CORS check is not a rubber
stamp. Against the real bucket, before and after the relocation: **38 passed, 0 failed**,
including three negative controls. It detects the store root, so it works either side of
the move.

**What the gate settled that could not be known beforehand:**

- **R2 serves the `.gz` shards OPAQUE** — `Content-Type: application/gzip`, no
  `Content-Encoding` — the same state GitHub Pages serves them in. So `jfetch`'s magic-byte
  branch is **unchanged in production**. This is the thing localhost can never test, because
  `python3 -m http.server` never sets that header.
- **The shard names are not URL-safe, in two ways, and neither is named in §4 or §5a.**
  164 are not ASCII (`’ ‘ “ ” ° √`); **458 contain a space** — the larger group and the one
  that hides, because a space is printable ASCII and slips through any "is it ascii" test.
  None contains `% # ? + &`. All survive the round trip byte-identical. Both are probed on
  purpose now; the space case was first hit by accident.

## Errors made this session, and where they are recorded

Per working principle 5. All four were caught by an instrument rather than by reasoning.

1. **`r2_upload.sh` uploaded 11,229 gitignored files** — `lookup_eval/dpd/*.json`, the
   uncompressed originals. It walked the filesystem instead of `git ls-files`.
   `lookup_eval` landed 28,509 objects against 17,280 tracked; 28,509 is exactly the count
   on disk. **§1a states this hazard in as many words and the script was written after that
   sentence.** Reading a warning is not running the instrument. Deleted from the bucket;
   the script now takes its file list from `git ls-files -z`. Commit `def078a8`.
2. **The panel.js change broke `check_lookup_reach.js`** — the gate §3a names as the control
   for this exact move. Its offline stub only knew `'../lookup/'`. Run before fixing:
   **0 passed, 6 failed**, every one "No entry for … in the corpus or the dictionaries".
   Fixed to detect the store root. Commit `40f54870`.
3. **A wrong instruction given to the reader:** verify rclone with `rclone tree osbct-r2:`.
   That **fails on a correctly-scoped token** — listing buckets is an account-level
   operation. The failure reads as a credentials problem and is not one. Replaced with a
   round trip (copy, ls, cat, delete, ls) that checks content, not exit codes, because the
   bucket was empty and "nothing" is what both success and silent failure print.
   Commit `01dafd41`.
4. **An arithmetic slip stated as fact**: `lookup` given as 7,318 from memory; it is 7,319.
   Corrected in the next message, before it could be acted on.

## Open items created or confirmed this session

1. **`check_lookup_reach.js` fails on `sāmugiya`, and it is NOT from this work.** Verified
   by restoring `panel.js` from `65c478ab~1` and re-running: identical word, identical
   output. **Observation, not diagnosis:** the word reaches the store — four tabs draw,
   `DPDAbhidhānaAPDGloss` — while the panel simultaneously reports `wl_none`, its no-entry
   state. Something resolves partially. **Do not close this until it is understood**: a
   panel that draws tabs and says "no entry" in the same breath is the confident-wrong-
   answer shape.
2. **The 118 PDFs are served from the `r2.dev` development URL.** `osbct-pdfs` has no custom
   domain and its Public Development URL is enabled; `site/downloads.html` and
   `site/reader/reader2.html` both point at
   `https://pub-825764a1384f4cc8bb611b95a1a636ff.r2.dev`. Cloudflare documents that path as
   rate-limited and not for production. **The PDFs are the final authority (§1) and the
   standing requirement is that a link reaches the exact and complete passage** — a
   rate-limited origin fails that quietly and only under load. Full repair, in order, in
   `docs/R2_SETUP.md` appendix. `site/DOWNLOADS-R2-SETUP.md` step 1 presents `r2.dev`
   first, which is how it happened, and is part of the fix. **Not measured:** whether the
   limit has ever been hit; Cloudflare does not publish the threshold.
3. **The `WLV` gate is owed.** `panel.js:346` versions every fetch `?v=WLV` and it must be
   bumped whenever the stores are rebuilt, as must the `?v=` on reader2.html's `<script>`.
   That is a human step with nothing behind it. **Bucket `Cache-Control` is deliberately set
   to one day, not a year, because of this** — a forgotten bump against a long cache cannot
   be recovered for a reader who has already loaded the page. Raise it after the gate
   exists, not before.
4. **`.gitignore`'s store rule was already stale before this session.** It ignores the
   lookup store while all 7,319 files are tracked, force-added past it; its own comment says
   the rule should have gone the day the data was published. Moved to `stores/` and
   documented, **not removed** — removing it is the reader's call.
5. **Five `.bak` files** in `_panel/` and `pipeline/` from this session's `sed` runs. They
   are gitignored and harmless. The sandbox cannot delete files (`rm` and `mv` both return
   *Operation not permitted*), so: `rm _panel/*.bak pipeline/*.bak` on the reader's machine.

## Still open from the previous handoff — unchanged unless noted

**Parked by the reader and NOT to be decided alone:** the verbatim-repeat display (5,376 of
22,527) and `none` vs `dim`. §1a of the 08-06 handoff carries the measured evidence on the
first and must not be lost.

**Decided 2026-08-06, not started:** the APD tab's defaults and gear — CPED then PED open by
default, gear for the rest, hidden never meaning absent. `panel.js` only.

1. **The 3,163 concordance-violating links**, dimmed with wording distinct from the 320.
   Path proven: `mark_condemned.py` writes the verdict at build time, `check_dimmed.js`
   gates it.
2. ~~**Resharding**~~ — **superseded for the deploy.** Not needed to fix the file count, and
   §3a's costing stands if it is ever wanted for another reason.
3. **BLOCKBREAK** — still off. `joined2.py` reads `blocks2/` while the repair reads
   `blocks3/`, so measure and repair are not comparable.
4. **The hyphen repair** — 8,790 words still broken; cannot land without the builder's
   paragraph matcher changing with it. `_xc/hy2/FINDINGS.md` §11.3.
5. **Class 1 and class 2 are suspect** and must be re-measured before anything is planned
   from them.
6. **Position** — unmeasured for 114 of 118 volumes. The largest thing outstanding.
7. **The verse branch for band blocks** — a fidelity gap against the printed page, so it does
   not expire if the display question is answered "leave it".
8. **`FINDINGS.md` §11.5 is stale and contradicts §11.3.** Still not corrected; still the
   reader's to confirm.

## Hazards

- **NEVER use "Re-run failed jobs" on the Pages workflow.** Each re-run adds another artifact
  named `github-pages` to the same run and the run becomes unrecoverable. Start a fresh one:
  `gh workflow run deploy-pages.yml`.
- **The ten-minute publish ceiling cannot be raised.** 600000 ms is the maximum.
- **`gh` is NOT present in every sandbox** — it was not in this one. The 08-06 handoff's
  hazard list says it is installed and authenticated; that is the correction that file
  already owed and this one repeats.
- **Git cannot commit unaided in the sandbox**: `mv` `.git/index.lock`, `.git/HEAD.lock`,
  `.git/packed-refs.lock` aside around each call. Confirmed again all session — every commit
  emitted `unable to unlink` warnings and succeeded anyway.
- **`rm` AND `mv` both fail in the sandbox** with *Operation not permitted*. The 08-06 note
  said `mv` works as the workaround for `rm`; it does for `.git` lock files and **not** for
  ordinary files. That is why five `.bak` files are still on disk.
- **Claude can commit but CANNOT push.**
- **Do not put a quoted phrase inside a `git commit -m "…"` string** in the sandbox shell —
  it broke a commit this session. Write the message to a file and use `-F`.
- `nav.json` rebuild still owed, naming `48AbhiA01`.
- `pbreak/` must be re-derived after any builder change.

## The method

**Compare against the printed page, never against the corpus.** And 08-06's addition, which
earned its keep four times today:

> **RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.**

Every one of this session's four errors was caught by running something, and none by
thinking about it. The upload bug was caught by a count check that compares against
`git ls-files` rather than against what it just uploaded — a check that counted its own
output would have reported success. The broken gate was caught by running it before fixing
it. The pre-existing `sāmugiya` failure was attributed by restoring the old file and
re-running rather than by assuming.

**And the order that made the whole migration safe: prove, then move.** The origin was
tested with every file left exactly where it was, and the reader was opened in a browser and
seen to draw a real gloss, before a single file was relocated. At every point before the
last commit, reverting was editing two lines.
