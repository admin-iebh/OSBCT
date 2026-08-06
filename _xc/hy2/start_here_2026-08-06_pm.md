# START HERE — after 2026-08-06

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

Both were asked and neither was answered. **Do not decide them alone.**

1. **The commentary repeats the canon paragraph verbatim 5,376 times of 22,527** (exact
   text equality). That is what produces the numbering that looks broken — `19Khu02`
   ¶618 canon, then the Aṭṭhakathā band opening with ¶618 saying the identical words,
   then glosses at 333, 334, 341. Both series are the edition's. The options put to him:
   mark it as a quotation; hide it only when the canon band is on; leave it; or explain
   it in a tooltip. **The edition must not be silently corrected — but what is DRAWN is a
   display decision.**
2. **`none` vs `dim`.** He called a grey dashed dead button "dimmed", which is also what
   the new condemned-link chip is called. Two states, one word. Decide before the 3,163
   concordance violations arrive in the same style.

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
