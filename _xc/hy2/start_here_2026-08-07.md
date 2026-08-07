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

## Later the same day — v2.4.0 shipped, and one thing was nearly lost in it

<!-- Appended after the block above was written. The session continued past it. -->

**v2.4.0 is released and deposited.** DOI `10.5281/zenodo.21840816`; concept DOI unchanged
at `10.5281/zenodo.21495338`. Notes: `docs/RELEASE_NOTES_v2.4.0.md`. **No text changed** —
118 volumes and 89,512 paragraphs, re-counted rather than carried forward, so v2.3.0 and
v2.4.0 name the same corpus.

**The thing that was nearly lost, and it is the whole argument of §5a.** Option D keeps the
stores in the repository so they stay inside the deposit — and `git archive` confirms all
24,599 are in the tarball. But `panel.js` had been pointed at the bucket **with no
fallback**, so an unpacked deposit would have held every shard on disk beside a reader
looking for a domain that may not exist in ten years. Empty tabs, no error, files right
there. **Preserving the data and teaching the reader to ignore it is worse than not
preserving it, because it looks fine.** `jfetch` now retries against
`../../stores/lookup/` on any failure; the branch is inert in production, where that path
cannot climb above the document root.

`pipeline/check_archive_fallback.js` is the gate. **It compares rather than asserts**, and
that is the point: its first version asserted "every word resolves with the bucket gone",
failed on 2 of 4, and both turned out to be the pre-existing `sāmugiya` defect. It would
have blocked a release for somebody else's bug. It now runs each word twice — bucket
answering, bucket refused — and requires the results to be **identical**, so a pre-existing
defect cancels and only a fallback regression shows. Five controls, two of which exist only
to prove the two runs really differ.

**`stores/index.html`** answers the bare domain, which returned "Object not found" — correct
R2 behaviour, since public buckets do not list at the root. **R2 has no index-document
support**, checked before writing the file: the object alone does nothing, and a URL-rewrite
rule on the zone maps `/` to `/index.html`. If the root 404s again, look at the rule, not the
upload.

**Two more errors, both mine, both on the record.**

5. **`.zenodo.json` was still on 2.3.0 while `CITATION.cff` had been bumped.** Zenodo ignores
   `CITATION.cff` *entirely* when a `.zenodo.json` exists — not deprioritised, ignored. The
   version bump had been done carefully on the file Zenodo does not read. Third time this
   project's citation metadata has been a release behind, and the first time the cause was
   effort spent in the wrong place rather than an omission.
6. **And it was caught too late.** The tag was already cut at the commit before the fix, so
   **the deposited tarball declares 2.3.0**. The Zenodo record's metadata was corrected in
   place (which does not affect the DOI); the archived files could not be. Written up in
   **`docs/DEPOSIT_ERRATA.md`** with the commands to verify every sentence of it.
   `git diff v2.4.0..HEAD` touches **two metadata files and nothing else** — no corpus, no
   reader, no gate — so the deposit is sound *as a corpus*.

**The rule that follows, now written in `CITATION.cff` and the erratum:** a release touches
**both** metadata files, and **the tag is cut last**, after every one of them is committed
and pushed — not between two of them.

**Deliberately not done:** Zenodo's *Edit published files* would let the zip be replaced and
the inconsistency erased. A published DOI whose files quietly change afterwards is a worse
property for a preservation corpus than a published DOI with a documented erratum — the md5
would move under anyone who had already verified it. Immutable-and-annotated over
mutable-and-tidy.

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

1. ~~**`check_lookup_reach.js` fails on `sāmugiya`.**~~ **CLOSED the same day, and it was
   never a reader defect — the gate could not serve one of the stores.**

   `check_lookup_reach`'s jsdom fetch stub read every file as **UTF-8 text** and offered
   only `json()` and `text()`. `jfetch` reaches for `r.arrayBuffer()` on any `.gz`, got
   `undefined`, threw, and the throw was swallowed by jfetch's own `.catch(() => null)`.
   **The entire `dpd` store — the one store published gzipped — was silently invisible
   inside that gate.** Every word with content elsewhere passed and hid it. `sāmugiya` is
   the one word in the sample whose *only* content is DPD (`DPD 1 | Abhidhāna(dis) |
   APD(dis) | Gloss(dis)`), so it alone reported "no entry". **6 passed, 0 failed** after
   the stub was given an `arrayBuffer()`.

   **The lesson is worth more than the fix.** A test rig that cannot serve one of the
   stores will accuse the program of exactly the fault the rig has, and will do so *in the
   program's own words* — which is why it read as a reader bug for days and was written
   into this file as one.

   **And the first diagnosis was wrong.** It was called a race, and the poll loop was
   rewritten to wait for the panel to settle. That rewrite was run and **still failed**,
   which is what sent the search back to the stub. The settle logic was kept — waiting for
   the panel's own completion signal beats breaking on its first utterance — but it is
   labelled in the file as *not the fix*, so the next reader does not inherit a false
   account. Guessing twice and checking twice is what got there; the checking is the part
   to repeat.
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

6. **A downloadable package that runs locally, PDFs included.** Asked for by the reader on
   2026-08-07, for later. **Most of it already works** — the archive fallback means an
   unpacked checkout is a working offline reader, and there is no CDN dependency anywhere in
   `site/`. Two things remain: the **PDFs are not in the repository** (they are in the
   `osbct-pdfs` bucket, ~386 MB, and §2's distribution permission must be confirmed before
   bundling them), and a **launcher**, because the server must sit at the repository root —
   serve `site/` instead and the reader loads with empty dictionary tabs and no error.
   Measurements and the build plan: `docs/OFFLINE_PACKAGE.md`.

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
