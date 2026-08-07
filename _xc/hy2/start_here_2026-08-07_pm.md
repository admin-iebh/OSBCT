# START HERE — after 2026-08-07 pm

<!-- SESSION END 2026-08-07 (second session that day). Supersedes
     start_here_2026-08-07.md, which is still correct about everything except
     open items 1 and 2: both were worked and item 2 is closed.
     Read this block, then §"Next, in order". -->

## What changed this session

**Open item 2 is CLOSED: the 118 PDFs are off the `r2.dev` development URL.**
`files.buddha-dhamma.net` is connected to `osbct-pdfs` and both constants —
`site/downloads.html:65` and `site/reader/reader2.html:395` — now name it.
Deploy run **31201640186 succeeded in 1m34s**. The reader confirmed a PDF and a
`p. ⧉` page link both load from the new domain, and **the R2.dev subdomain has
been disabled**. `docs/R2_SETUP.md`'s appendix is done.

**That is the second fast deploy in a row** — 1m34s after #126's 2m01s, both
with 1,977 files. Still not the several the 08-07 am handoff asks for before the
publish ceiling can be called *unreachable* rather than merely *un-hit*, but the
evidence is accumulating and nothing has regressed.

**Open item 1 is HALF DONE, and the half that is done is partly wrong.** See
§"The 3,163, and what the reader found in it" below. Do not treat it as closed.

| | |
|---|---:|
| `pipeline/check_pdf_origin.js` against the live bucket | **601 passed, 0 failed** |
| `--selftest` | green, 6 defects each caught in isolation |
| concordance verdicts written | 1,164 links, **1,162 visible chips** |
| `mark_condemned.py --verify` | 0 files differ beyond `dim` |
| `check_dimmed.js` | PASS, 5 assertions, 2 families |
| `check_concordance` / `check_links` / `check_ordinal` | no measure regressed |
| BUILD | `a1a5de8aee10` → `1e7e28f2c125` |
| commit | `36429fbe`, 27 files, 932 insertions |

**`pipeline/check_pdf_origin.js` is new.** It probes all 118 objects for the four
things that fail QUIETLY — `Content-Type`, `Content-Disposition`, Range support,
size — plus `%PDF-` magic. Every one of those can be wrong while the link returns
HTTP 200 and a file, and the reader lands on page 1 of a 400-page volume instead
of the passage he clicked. **CORS is deliberately NOT checked**: both call sites
are `<a href>` navigations, not `fetch()`, so no preflight ever happens. That is
the one place `osbct-pdfs` differs from `osbct-dict`, where step 6 of
`R2_SETUP.md` is mandatory. Written down so nobody adds a policy that does
nothing and nobody assumes one exists.

## The 3,163, and what the reader found in it

**The build-time marking works and the wording is distinct from the 320. The
verdict it states is not established.**

`mark_condemned.py` now writes a `concordance` verdict beside the `ordinal` one;
`dimReason` in reader2.html gives the two families different words;
`check_dimmed.js` grew from 4 assertions to 5, the new one being that the two
tooltips are **not the same text** and neither fell through to `dim_generic` —
the only assertion that catches both families collapsing into one generic
sentence, a regression with no visible symptom.

**FOUR MEASUREMENTS THAT CHANGED THE DESIGN. `--stats` re-derives all of them.**

1. **3,163 is not the number of buttons.** It counts link targets. Only **1,164**
   are `state: direct`; the other 1,999 are `covered` and the reader never draws
   them. `dimOf` reads `r[0].dim`, so what reaches a reader's eye is **1,162
   chips** — the headline overstates by **2.7×**.
2. **Three links are condemned by BOTH checks.** A single `dim` object cannot
   hold two verdicts, so whichever pass ran second would have overwritten the
   first silently. `why` carries the primary and `also` the rest.
3. **Concordance outranks ordinal**, because a wrong volume subsumes a wrong
   sutta inside a volume.
4. **`no_such_layer` is 0.** The branch is written and counted anyway; a
   manufactured target is a different fault from a mis-aimed one. **Two canon
   volumes are absent from the concordance** and are skipped, not condemned —
   silence is not a verdict.

### AND THEN THE READER CHECKED IT AGAINST THE PRINTED PAGE, WHICH IS THE WHOLE METHOD

He opened `20Khu03` ¶247 and ¶248 in the Apadāna commentary PDF and reported
that **those paragraphs are not commented at all**, while ¶250 is, at
`32KhuA13` pdf page 257.

The link data agrees once you look at the neighbourhood:

```
¶246  covered  32KhuA13#216     <- correct volume
¶247  direct   41KhuA22#251     <- offset +4.  the odd one out
¶248  covered  41KhuA22#251
¶249  direct   32KhuA13#217     <- correct volume resumes
```

Genuine links into `32KhuA13` sit at offsets around −24 to −36, drifting slowly
the way a real alignment does. ¶247 jumps to **+4**, and so do ¶279→283 and
¶335→339 — exactly +4 each time. That is a bare paragraph-**number** match into
whatever volume happened to own a paragraph 251. `41KhuA22` is the **Jātaka**
commentary, volume VI. It has nothing to do with the Apadāna.

**So ¶247 is not a mis-aimed link. It is a manufactured one.** ¶247 and ¶248
fall in the gap between `#216` and `#217`; the commentary has nothing for them,
and the builder invented a target from the number.

### WHAT THIS MEANS FOR WHAT SHIPPED, STATED PLAINLY (principle 5)

**The tooltip now on 1,164 links says "the concordance does not pair this volume
with X". That is true and it is not the finding.** It describes the link. The
reader's question is about the *paragraph* — is it commented at all — and that
was never checked. The two are different claims and only the first was tested.

**A split shown to the reader mid-session and WITHDRAWN.** 702 "same work, other
volume" versus 462 "different work" — `20Khu03 → 33KhuA14` (Apadāna commentary
II) against `20Khu03 → 41KhuA22` (Jātaka). It reads as meaningful and it is not:
`33KhuA14` is not acceptable because both volumes say *Apadānaṭṭhakathā*, and
`41KhuA22` is not wrong because it says *Jātaka*. The work name was standing in
for evidence not gathered — the section name is the test. **Do not quote 702/462
as if they measured something.** They are recorded here only so that a later
reader who finds them in the transcript knows they were retracted.

## The reader's method, given this session, and it governs the next one

Stated by him, in his words where it matters, because it is the specification:

- **The PDF is the authority.** Whether a paragraph is commented is a fact about
  the printed commentary, not about the link data. Open the Aṭṭhakathā the
  concordance pairs with that canon volume and look for a passage matching the
  Pāḷi. No passage → not commented.
- **The concordance decides which commentary is ELIGIBLE, before any number is
  looked at.** `41KhuA22` comments the Jātaka; for an Apadāna paragraph it was
  never a candidate, so its paragraph 251 is irrelevant. **The defect is that the
  builder used the number as an address across the whole corpus and the
  concordance was never consulted at all.** `check_concordance.py` was the first
  thing that ever compared the links against it.
- **Several commentary volumes is not an ambiguity.** Use the section name —
  sutta or other title — and search it across all eligible volumes; the volume
  falls out of the name.
- **The commentary glosses WORDS from the Pāḷi**, so the shared token is the
  confirmation that this is the passage.
- **The reader's own preference on order: start with the paragraph number.**
  Reconciled, and he is right once the volume is fixed: concordance → number →
  name and gloss. The number never gets to choose the volume.

**THE HAZARD IN THE ABSENCE TEST, AND IT FAILS IN THE DANGEROUS DIRECTION.**
Sandhi. The commentary quotes the word as it stands and the canon may carry it
fused — *indriyāni* inside *yassindriyāni*. A plain string match misses it and
reports "no gloss found", which becomes "this paragraph is not commented" — a
confident denial that looks exactly like a real result. §7 of the project
instructions already names sandhi-aware search as dependent on the Kaccāyana
work. **So the instrument must report THREE states — commented, not commented,
cannot establish — and only the middle one earns the reader's wording.**
Collapsing the third into the second turns an untested absence into a claim, on
a scale of hundreds.

## NEW, and it is not a display bug: the Commentaries' unnumbered front matter

**Reported by the reader; measured this session.** Each commentary opens with
verse and prose carrying **no paragraph number**, and it must be reachable from
the left pane.

- **The text IS in the corpus.** `32KhuA13` opens with 11 unnumbered records
  spanning printed pages **1–105** — `Ganthārambhakathā`, `Nidānakathā`,
  `Dūrenidānakathā`, `Sumedhakathā`. The `headings` array carries them with
  `printed` and `pdf_page`. Nothing was lost in extraction.
- **The nav is keyed on the paragraph number.**
  `site/reader/sections/32KhuA13.json` has keys `3, 4, 5, 7, 8, 11`. A record
  with `n: null` has no key and cannot appear in the pane.
- **690 unnumbered leading records across 63 volumes.** Largest:
  `20KhuA01` **298**, `24KhuA05` 79, `07ViT07` 62, `01VinA01` 19, `32KhuA13` 11.

**It is the same defect as the Jātaka link.** The paragraph number is used as an
address in three separate places — the nav keys on it, the link builder walks
it, the cross-layer join used it — and fails the same way each time: absent in
the front matter, non-unique across volumes, restarting in 90 of 118. August
established it is not a key for linking. **It is not a key for navigation
either**, and that went unnoticed because the material it hides sits before
everything anyone was looking at.

## Errors made this session, and where they are recorded

Per working principle 5. Both were mine, both in `check_pdf_origin.js`, and both
were caught by RUNNING it rather than by reading it.

1. **The Range check required `bytes 0-1023/` literally**, so a well-behaved host
   answering `bytes 0-28/29` for a short object was reported as having no Range
   support. **No real volume is under 1 MB, so it would never have fired in
   production** — it would have sat there reading as a passing check while
   testing the wrong thing, and been trusted by the next reader. Caught by the
   selftest. The selftest also gained a truncation case, because the header
   claimed the size check caught truncation and nothing demonstrated it — a claim
   in a comment with no instrument behind it.
2. **The origin regex scanned the whole file and matched a COMMENT.**
   `downloads.html:64` carries the commented-out `pub-xxxxxxxx.r2.dev`
   placeholder from `DOWNLOADS-R2-SETUP.md`, one line above the real
   declaration. The gate fetched from a bucket that does not exist, Cloudflare
   answered **401**, and **that 401 was reported to the reader as evidence the
   live origin had been disabled and the site was down. It had not been and it
   was not.** Caught by `site constants agree` — the only check that compares the
   gate's own inputs to each other, and worth more than it looks. A placeholder
   guard is now a named assertion so the next occurrence is diagnosed in one line
   instead of an afternoon.

**A regex that scans a whole file will find the documentation before it finds
the code.** That is the transferable lesson and it applies to every other
constant-reading gate in `pipeline/`.

## Next, in order

1. **The full matching run, ONE CANON VOLUME AT A TIME, with the reader
   answering the pairing questions.** He offered this explicitly and it is the
   right division of labour: the machine finds where links disagree with the
   concordance, only he can say whether the concordance is right when they do.

   **Ask VOLUME-level questions, never paragraph-level.** One line from him
   resolves hundreds of links. The model question:

   > `20Khu03` (Apadāna I) — the concordance gives its commentary as `32KhuA13`
   > alone. 357 paragraphs point at `33KhuA14` (Apadāna commentary II) and 18 at
   > `41KhuA22` (Jātaka commentary VI). Does the Apadāna commentary continue into
   > volume II for this canon volume?

   Where the printed page is genuinely needed, give him volume, printed page and
   the Pāḷi so he can go straight there.

   **Start with `20Khu03`**: shared context already (he verified ¶247 and ¶248),
   the most violations of any volume (469), and it exercises both shapes at once.

   **Read `pipeline/link_by_gloss.py` and `relink_by_name.py` FIRST** — the
   technique exists and must not be reinvented.

2. **Measure whether the number suffices once volume and section are fixed.**
   This is the reader's proposal and it has never been tested. August measured
   the number across the corpus (40.3% wrong sutta); it did NOT measure the
   number *inside a concordance-eligible pair, inside a name-matched section*.
   If that comes back high, his rule stands as written and the name and gloss are
   only the check on it. Answer it with a measurement, not by quoting August.

3. **The nav front matter.** Key the sections on the printed page rather than the
   paragraph number so the 690 records become reachable. Self-contained, touches
   no link data, immediately checkable against the PDF. Good first unit of work.

4. **Then and only then, the tooltip wording.** The reader wants it to say the
   paragraph is not commented. It cannot say that until step 1 establishes it.

5. **A rebuild is the known-wrong move.** `build_links_bynum.py` records that a
   full rebuild constrained by the concordance **lost on both axes at once**. The
   repair is per-link, name-and-gloss anchored, with `check_links.py` as the
   ratchet.

## Still open from the previous handoff — unchanged unless noted

**Parked by the reader and NOT to be decided alone:** the verbatim-repeat display
(5,376 of 22,527) and `none` vs `dim`.

**Decided 2026-08-06, not started:** the APD tab's defaults and gear.

1. ~~**The 3,163 concordance-violating links**~~ — **marked and drawn, verdict
   NOT established.** See above. Not closed.
2. **BLOCKBREAK** — still off. `joined2.py` reads `blocks2/`, the repair reads
   `blocks3/`.
3. **The hyphen repair** — 8,790 words in 109 volumes. `_xc/hy2/FINDINGS.md` §11.3.
4. **Class 1 and class 2 are suspect** and must be re-measured.
5. **Position** — unmeasured for 114 of 118 volumes. The largest thing outstanding.
6. **The verse branch for band blocks.**
7. **The `WLV` gate is owed.** `panel.js:346` and reader2.html's `<script>` `?v=`.
   Bucket `Cache-Control` stays at one day until the gate exists.
8. **`.gitignore`'s store rule is stale.** Removing it is the reader's call.
9. **A downloadable package that runs locally, PDFs included.**
   `docs/OFFLINE_PACKAGE.md`. §2's distribution permission must be confirmed
   before bundling the PDFs.

## New open items

10. **`claude/` HAS NEVER EXISTED IN GIT.** No commit on any branch has ever
    contained it. Yet the project instructions cite
    `claude/paragraph_numbers_are_not_a_key.md`,
    `claude/links_repaired_by_name.md` and `claude/roots_provenance_and_dpd.md`;
    `mark_condemned.py`, `check_dimmed.js` and `reader2.html` all cite
    `claude/decision_dim_the_condemned_links.md` as the reader's decision of
    2026-08-03; and `.gitignore:176` refers to it. **Item 1 was built from the
    specification in `reader2.html`'s own comments instead**, which was explicit
    enough. But a directory that four files treat as authoritative and that the
    repository has never held needs either restoring or the citations correcting.
11. **Node 20 deprecation on the Pages workflow.** `actions/checkout@v4`,
    `configure-pages@v5`, `deploy-pages@v4` and `upload-artifact@v4` all target
    Node 20 and are currently being FORCED onto Node 24. Advisory today, a hard
    failure whenever GitHub stops forcing. A version bump in `deploy-pages.yml`.
12. **The concordance tooltip lists every allowed volume** — seven volume codes
    for `18Khu01`, which is long for a chip. **Capping it is a display question
    and was left to the reader**, deliberately not decided.
13. **`COMMIT_MSG.bak` is in the repository root.** Gitignored via `*.bak`, so it
    cannot be staged. `rm COMMIT_MSG.bak` when convenient.

## Hazards

Unchanged from the 08-07 am handoff, which remains the reference, plus:

- **`.git` IS WRITE-PROTECTED FROM THIS SANDBOX.** A commit message file cannot
  be written to `.git/`. Write it to the repository root with a `*.bak` name —
  `.gitignore:67` excludes it, so `git add -A` cannot stage it by accident.
- **DO NOT WRITE A PLACEHOLDER IN ANGLE BRACKETS INTO A SHELL COMMAND FOR THE
  READER.** `git commit -F <message-file>` is a redirect in zsh and dies with
  `parse error near '\n'`. It happened this session. Give a real path.
- **Clear the git locks on the host at the end of every session:**
  `find .git -maxdepth 2 -name '*.lock*' -size 0 -delete`. One was left at the
  end of this one.
- **Never "Re-run failed jobs" on the Pages workflow**; start a fresh run with
  `gh workflow run deploy-pages.yml`.
- **`stamp_build.py --write` IS NOT OPTIONAL after any change under `site/`.**
  Everything the reader fetches carries `?v=BUILD`. 16 `linksk` files changed
  this session; without the bump a returning visitor keeps the cached link data
  and sees none of it. All blocking freshness checks were green; the four
  advisory ones — `apparatus`, `links (legacy)`, `sections`, `nav.json` — are
  pre-existing and do not block.

## The method

Unchanged, and it earned its keep twice more today:

> **RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.**

Both of this session's errors were caught by running something and neither by
thinking about it. And the addition this session earned:

> **COMPARE AGAINST THE PRINTED PAGE, NEVER AGAINST THE CORPUS — AND THAT
> INCLUDES COMPARING AGAINST YOUR OWN OUTPUT.**

The 1,164 verdicts passed every gate in `pipeline/` and were still stating a
claim nobody had checked. It took the reader opening the Apadāna commentary at
page 257 to find it. **A green ratchet is evidence that nothing got worse. It is
not evidence that the thing is true.**
