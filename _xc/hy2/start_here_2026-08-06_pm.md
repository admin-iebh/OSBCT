# START HERE — after 2026-08-06

> **SUPERSEDED 2026-08-07. READ `_xc/hy2/start_here_2026-08-07.md` FIRST.**
>
> This file is still correct about almost everything, and its §1a evidence on the
> verbatim-repeat question must not be lost. But its headline task — the A/B/C/D decision —
> **was made and executed on 2026-08-07: D + B.** The stores are in `stores/`, served from
> `dict.buddha-dhamma.net`, `site/` is 1,977 files, and run #126 published in 2m01s.
>
> This pointer exists because this file says "that decision is the next real piece of work",
> and an agent reading it top-to-bottom would act on that. Same drift the project
> instructions record for §9 and `DEPLOY_SCALE.md` §6.

<!-- SESSION END 2026-08-06 evening. Read this block, then §"Next, in order".
     Two files are uncommitted: this one, and `_xc/reshard/PILOT.md`. -->

## What changed this session

1. **The resharding pilot ran. `_xc/reshard/PILOT.md` is the record and supersedes
   `docs/DEPLOY_SCALE.md` §2–§3 where they disagree.** The gate passed — `build_lookup.py`
   reproduces the shipped `gloss` store (180,025 of 180,025 keys, 99.98% byte-identical,
   the 40 differences all overflow-promotion, no text). **But §2's "3.8 KB average, 4%
   full" is the GZIPPED size measured against an UNCOMPRESSED 150 KB cap** — the shards
   are 15–33 KB, 10–22% full. And **§3's "raise the effective shard size" has no knob**:
   `shard_table` starts at prefix depth 2 and only ever splits deeper, never merges.
   Simulated depth-1 merging: `dpd` 11,229 → 11,229, `lem` 4,954 → 4,954. **Option A is
   not impossible — it needs a new grouping scheme plus the matching change to the
   shard-naming contract `panel.js` computes on the client. It is not a parameter change.**

2. **The 1 GB Pages cap was never the constraint, and I revived that error mid-session
   before the repo corrected me.** `deploy-pages.yml` already records it: the 1.62 GB
   figure was the local working tree with untracked build output; **CI checks out 833 MB
   in 26,576 files**, independently re-measured this session. The prune step was removed.
   Do not reintroduce it, and do not treat bytes as the problem — **the file count and the
   ten-minute clock are.**

3. **Run #120 was a THIRD kind of failure and must not be filed with the timeouts.**
   `The job was not acquired by Runner of type hosted even after multiple attempts` — the
   job never started, no artifact was produced, the 15m10s was spent waiting for a machine.
   Nothing local caused it. `DEPLOY_SCALE.md`'s duration table is the evidence base for the
   resharding decision; putting a runner-availability failure into it corrupts that.

4. **Where the stores should live — discussed, NOT decided.** The workflow publishes
   `path: ./site` and nothing else, so **moving the stores out of `site/` removes them from
   the Pages artifact while keeping them in the repo.** That is the move that fixes the file
   count, and it is separate from where they are *served* from. `panel.js:541-542` is the
   whole switch:

   ```js
   var BASE  = '../lookup/';
   var EBASE = '../lookup_eval/';
   ```

   So a bucket can be trialled with every file left exactly where it is, reversible in two
   lines. **The argument that has not been weighed against R2: the stores are tracked, so
   they are inside the Zenodo deposit.** Move them to a bucket and a future reader holding
   only the archived DOI gets a reader whose dictionary panel is empty. The shape that
   answers both — stores in the repo but outside `site/`, served from R2, jsDelivr in
   reserve — **is a proposal, not a decision.**

   `jfetch` sniffs gzip magic bytes because a host may or may not set
   `Content-Encoding: gzip` and localhost never does. **That path must be tested against
   the real bucket.** It is where a trial would actually fail.

5. **Decided by the reader:** the APD tab's defaults and gear (see below), and DOP kept
   with its copyright information shown. **Parked by the reader:** the verbatim-repeat
   display and `none` vs `dim`.

**`docs/DEPLOY_SCALE.md` IS NOW CORRECTED (2026-08-07).** §2 and §3 are struck through with
§2b and §3a beside them, §1a separates the three failure causes, **§5a adds Option D —
relocate the stores out of `site/` and keep them in the repo, which preserves the Zenodo
deposit** — and **§6 is SUSPENDED pending a fresh decision across A / B / C / D.** That
decision is the next real piece of work and it belongs to the reader.

**Corrections still owed:** `FINDINGS.md` §11.5 (stale, contradicts §11.3); this file's
hazard list, which says
`gh` is installed and authenticated — **it is not present in every sandbox, and was not in
this one**; and `site/reader/panel.js:14`, which says the Abhidhāna, PEU and PPN are not
shipped while line 104 says every visitor gets every tab.

**The method held and caught two of my own errors this session** — a claim that the site
was 39,538 files (working tree, not `git ls-files`) and the 1 GB revival above. Both were
caught by reading the artefact before reporting. Keep doing that.


**Supersedes the earlier draft of this file, whose headline said the deploy was the
blocker. It was; it no longer is. v2.3.0 is published, archived and live.**

The reader's standing requirement is unchanged:

> "The PDFs are the final authority... first, we need to have in the corpus the same
> material that is in the PDF. Second we need reliable links that take the user to the
> exact and complete passage that is commented."

## State

**v2.3.0 released, deployed and deposited.** DOI `10.5281/zenodo.21826574`; concept DOI
`10.5281/zenodo.21495338`. `CITATION.cff` now lists every deposit including v2.2.0's,
which existed since 2 August and was simply never recorded. Corpus: **118 volumes,
89,512 paragraphs**, 54,036 variant readings, 27,153 cross-references.

Release notes: `docs/RELEASE_NOTES_v2.3.0.md`. They are honest about what is not done,
and that section is the useful part of this file too.

## The two questions that belong to the reader

**PARKED 2026-08-06 by the reader: "keep this in the to-do-list for the time being."**
Both were put to him twice. Neither is decided. **Do not decide them alone, and do not
treat parking as leave-as-is** — question 1 acquired evidence while it was being asked,
recorded below, and that evidence is the part that must not be lost.

1. **The commentary repeats the canon paragraph verbatim 5,376 times of 22,527** (exact
   text equality). That is what produces the numbering that looks broken — `19Khu02`
   ¶618 canon, then the Aṭṭhakathā band opening with ¶618 saying the identical words,
   then glosses at 333, 334, 341. Both series are the edition's. The options put to him:
   mark it as a quotation; hide it only when the canon band is on; leave it; or explain
   it in a tooltip. **The edition must not be silently corrected — but what is DRAWN is a
   display decision.**
2. **`none` vs `dim`.** He called a grey dashed dead button "dimmed", which is also what
   the new condemned-link chip is called. Two states, one word. Decide before the 3,163
   concordance violations arrive in the same style. The options put to him: make absence
   look properly dead (flat grey, no border, no hover, not clickable) while the condemned
   link stays a clickable chip with a warning; or distinguish by colour only; or change
   the wording and leave the styling alone. **Nothing measured here — no screenshot of
   either state has been read.**

### 1a. Measured while the question was being asked — the band flattens the edition's verse

Read on the printed page, not inferred. `27KhuA08` (Vimānavatthu-aṭṭhakathā) **p.133**
(`pdf_page` 140, rendered and read) prints `617.` and `618.` as **indented verse, three
pādas on three lines**, closing `…na socare”ti` with the edition's own quotation mark, and
then `333.` `334.` `341.` as ordinary prose. **So the 618 is the edition's own number in
the commentary volume — nothing was injected by the builder and nothing can be corrected.**

The reader draws that lemma as a single prose run. That flattening is a large part of why
it reads as a duplicate rather than as the verse being glossed.

**The data to draw it correctly is already shipped.** `site/reader/verse/27KhuA08.json`
key `510` — the paragraph's **index** — holds exactly those three pādas. It is not drawn
because of `site/reader/reader2.html:1678`:

```js
const asSpine = kind==='canon' || !!(opts&&opts.spine);
```

The 08-03 comment directly above it says so in terms: the verse branch was opened for the
spine only, "and not for a band block hanging under a canon paragraph, which is a different
question and is left exactly as it was." **That different question is this one.**

Two hazards, both to be settled before the branch is opened for bands:

- **`hide/` is written on the assumption the branch runs** (same comment, measured on
  `20KhuA01`: ten of fourteen hidden ordinals are merge-absorbed into a neighbour's verse
  entry). Opening it for bands can re-emit or double-emit those paragraphs.
- **`27KhuA08`'s verse map is index-keyed** (1,387 keys, max 1479, 1,480 paragraphs; key
  `618` is paragraph *index* 618, `n=667`, an unrelated paragraph). This is the mixed
  index/`n` convention that produced the `50AbhiA03` bold defect — FINDINGS §11.1. Decide
  the convention **once per volume with no fallback**, and skip and say so where it cannot
  be decided.

**Not established:** whether any volume's verse map is `n`-keyed, or how many volumes are
affected. Only `27KhuA08` was measured.

## DECIDED 2026-08-06 — the APD tab gets defaults and a gear

The reader's decision, in his own terms: **two sections open by default, in this order —
CPED then PED — with a gear icon to selectively choose one or more of the others.**

Scope agreed and closed: **Edition, Abhidhāna and DPD are NOT in the gear.** The first two
because they *are* §9's authority; DPD because §9 excludes it as a voice however it is
licensed. Same exclusion, opposite grounds, and the popover should say so in one line so
the absence reads as deliberate.

The remaining APD sections (`ny`, `vri`, `ppn`, `uhs`, `rt`, `tpm`, `pwg`, and `DOP`/`CPD`/
`NCP` where the eval build supplies them) are off by default and available in the gear.

**Hidden must not mean absent.** A switched-off section still draws a one-line collapsed
header **with its count**, and only when it has a hit for that word — `Proper Names · 1` —
opening in place on click, for that word only. This is the reason PPN can be off by
default without disappearing: it is silent on almost every word and decisive on the few
that carry a name, and a reader who has never seen it will not go hunting in a gear menu
for it. The same line lets a Burmese reader find the four Burmese sources without knowing
the gear exists. `.wl-n` already carries counts on the tab buttons.

Gear state persists in `localStorage`, beside `osbct-wle`.

**DOP — DECIDED: keep it, with its copyright information shown, noting it is available at
gandhari.org.** The reader's decision, recorded as given.

**The unresolved point travels with it, per working principle 2.** PTS announced on
28 March 2024 that the three published volumes are at `gandhari.org/dictionary?section=dop`
and "free for all to search and use" — free *access on that site*. Their copyright page
lists the works they have released under Creative Commons: **PED is on it** (CC BY-NC 3.0,
2013, "permission is granted to reproduce, reformat, transmit and distribute these works for
non-commercial use"); **DOP is on neither list**, and is still sold in three volumes. An
attribution notice records whose text it is; it is not a grant to redistribute it, and
placing DOP behind a gear does not change that OSBCT would serve Cone's text from its own
domain. `.gitignore` already says so in its own words: "DOP in copyright … must not enter a
public repo."

**The version with no exposure, if it is wanted:** show the DOP row as headword + link to
that word at gandhari.org. The reader gets Cone in full from PTS's own sanctioned copy and
OSBCT redistributes nothing. Otherwise the ask goes to PTS directly — a charity, which has
licensed before, and whose president posted that announcement.

**DOP is also not in the default pair, and this is not an oversight.**
`_panel/build_eval.py:489` records it as *"Margaret Cone — Pali Text Society, in
copyright"*, and `_panel/build_lookup.py:449` lists `DPD / DOP / CPD / CPED` as
*"filter-side only per §9"*. The 2026-08-02 note in `panel.js` that turned the eval flag
default-on names the settled licences as DPD, the Abhidhāna and PEU — **it does not name
DOP, CPD or NCPED.** Comment strings are not a licence audit; this is flagged, not
asserted. Confirm the redistribution basis before promoting Cone to a default section.

**Also stale, same class as `FINDINGS.md` §11.5:** `site/reader/panel.js:14` still says
"Abhidhāna, PEU and PPN are NOT here", contradicted by line 104 ninety lines below, which
says every visitor gets every tab. Both sit in the file an agent reads top-to-bottom.

Not started. `site/reader/panel.js` only — no store rebuild, no corpus change.

## Next, in order

1. **The 3,163 concordance-violating links**, dimmed with *distinct* wording from the
   320 — a wrong volume and a wrong sutta inside the right volume are different things
   to say. The path is proven: `pipeline/mark_condemned.py` writes the verdict onto the
   link entry at build time, `pipeline/check_dimmed.js` gates it with a discrimination
   control.
2. **Resharding**, and read `docs/DEPLOY_SCALE.md` before touching it. 93% of the site's
   26,576 files are dictionary shards averaging 3.8 KB against a 150 KB cap. Target
   **64 KB**, not the cap: bigger shards mean each lookup downloads more, and that trade
   is the whole reason not to just take the maximum.
3. **BLOCKBREAK** — still off. Two real mid-sentence lines unread (`32KhuA13`
   `…seyyathāpi nāma`, `24KhuA05` `…Ācariyadhammapālena katā`); `joined2.py` still reads
   `blocks2/` while the repair reads `blocks3/`, so measure and repair are not comparable.
4. **The hyphen repair** — 8,790 words still broken. Applied and reverted; it cannot go
   in without the builder's paragraph matcher changing with it. `_xc/hy2/FINDINGS.md` §11.3.
5. **Class 1 and class 2 are suspect** and must be re-measured before anything is planned
   from them: the page-side classifier calls `35Abhi07`'s mātikā verse and the reader says
   prose.
6. **Position** — unmeasured for 114 of 118 volumes. The largest thing outstanding.
7. **The verse branch for band blocks** — §1a above. Parked with the decision it belongs
   to, but it is a fidelity gap against the printed page, not a display preference, so it
   does not expire if the display question is answered "leave it".
8. **`FINDINGS.md` §11.5 is stale and contradicts §11.3 above it.** Its table reports the
   hyphen-space count as `8,790 → 1,501 in 96 volumes`, but §11.3 reverted all 185 files
   to `481c7221` and verified the return to **8,790 in 109 volumes**. An agent reading
   §11.5 alone would believe the migration is in place. **Not corrected here** — reported,
   per working principle 5, and left for the reader to confirm before the record is edited.

## Hazards

- **NEVER use "Re-run failed jobs" on the Pages workflow.** Each re-run adds another
  artifact named `github-pages` to the same run; four of them produced
  `Multiple artifacts named "github-pages" ... Artifact count is 4`, which cannot be
  recovered for that run. Start a fresh run: `gh workflow run deploy-pages.yml`.
- **The Pages deploy sits on a ten-minute ceiling that CANNOT be raised** — 600000 ms is
  the maximum, not the default. Some runs take 2 minutes and some 11. Retrying works.
  `docs/DEPLOY_SCALE.md` has the whole analysis.
- **`gh` is now installed and authenticated.** `gh run view --log-failed` prints the real
  error. Use it before theorising; four wrong diagnoses on 08-06 came from not having it.
- **Git cannot commit unaided in the sandbox**: `mv` `.git/index.lock`, `.git/HEAD.lock`,
  `.git/packed-refs.lock` and `.git/refs/tags/*.lock` aside around each call. `rm` fails.
  Tags cannot be moved once created, for the same reason.
- **`git checkout -- <path>` cannot restore a file** (unlink fails). Restore with
  `git show HEAD:<path>` written back in place, truncate-and-write.
- **Claude can commit but CANNOT push.**
- `nav.json` rebuild still owed, naming `48AbhiA01`.
- `pbreak/` must be re-derived after any builder change.

## The method, and the lesson of this session in particular

**Compare against the printed page, never against the corpus.** To which 08-06 adds, at
its own expense:

> **RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.**

Every gate written that day passed on the broken code until it was run against it —
`check_lookup_reach` reported 7 of 7 passing on the very build it was written to catch,
because the interface is in Spanish and its miss-test was an English regex. The negative
control caught that, and three more like it.

And the reader's own scoreboard for the day: **three wrong locators** (an index given as
a printed number; the wrong volume; a printed number that is not unique within its
volume), **one retracted measurement** (111 "corruptions" that were a substring matcher),
**one repair written to the corpus and reverted**, and **four wrong diagnoses of a deploy
failure** whose actual error message was one click away the whole time.

Every one came from reporting before looking at the thing reported. **Read the artefact,
render the page, run the gate against the old code. Then speak.**
