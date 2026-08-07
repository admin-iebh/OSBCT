# Errata in the deposits themselves

Not errata in the *edition* — those are `site/errata.html`, and the rule there is the same
as here: **the record is annotated, never overwritten** (working principle 3).

This file records defects in the archived deposits: what was deposited, what is wrong with
it, what was done about it, and how a reader can verify the statement for themselves. A
deposit carries a DOI and is permanent. Correcting one quietly is not available, and
pretending it was always right is worse than saying what happened.

---

## v2.4.0 — the deposited files declare version 2.3.0

**Discovered 2026-08-07, minutes after the deposit was minted.**

### What is wrong

The archived tarball of v2.4.0 contains a `.zenodo.json` whose `"version"` field reads
**`2.3.0`**, and whose `description` carries the *"New in 2.3.0"* paragraph. In the same
tarball, `CITATION.cff` reads `version: "2.4.0"`. **Two files in one deposit disagree about
which release it is.**

### Why

The `v2.4.0` tag was cut at commit `c9236cbe`, which bumped `CITATION.cff` but not
`.zenodo.json`. The fix — commit `6799bcc6` — was made afterwards and is therefore **not in
the tag**, and not in the archive Zenodo built from it.

The underlying cause is worth stating plainly, because it is the third time this project's
citation metadata has been a release behind and the first time the cause was of this kind:
**the maintained file was not the read file.** Zenodo's documentation is explicit that when
a `.zenodo.json` exists in the repository root, `CITATION.cff` is *ignored entirely* — not
deprioritised, ignored. The version bump had been done, carefully, on the file Zenodo does
not read. `.zenodo.json` is JSON and cannot carry a comment explaining this, which is
plausibly how it drifted while every other file in this repository explains itself.

### What is NOT affected

`git diff v2.4.0..6799bcc6` touches **exactly two files**: `.zenodo.json` and
`CITATION.cff`. **No corpus file, no reader file, no gate, no dictionary shard differs.**
The archived text, the 118 volumes, the 89,512 paragraphs, the apparatus and the code in
the v2.4.0 deposit are all correct and are the ones the release notes describe. Anyone
using the deposit *as a corpus* is unaffected.

### What was done

1. **The Zenodo record's metadata was corrected in place** — version set to `2.4.0`, the
   description replaced with the corrected text. Zenodo permits metadata editing after
   publication and **the DOI is unaffected** by it. So anything that reads the record's
   metadata — a citation, a search index, the landing page — is now right.
2. **The archived files were left exactly as deposited.** They cannot be changed without
   minting a new version, and minting one to correct two metadata lines would put a second
   DOI on an identical corpus, which is a worse outcome for anyone trying to cite this.
3. **This entry was written**, and `CITATION.cff` now carries a note at its head naming both
   files that a release must touch, so the cause does not recur.

### How to verify this statement

```
git diff --stat v2.4.0..6799bcc6        # two files, no corpus change
git show v2.4.0:.zenodo.json | grep version    # "2.3.0" — as deposited
git show v2.4.0:CITATION.cff  | grep '^version' # "2.4.0" — the disagreement
```

### The lesson, for the next release

The release checklist is **both** files, every time, before the tag is cut:

| file | what to change |
|---|---|
| `.zenodo.json` | `version`, and the *"New in x.y.z"* paragraph of `description` |
| `CITATION.cff` | `version`, `date-released`, and the new DOI once Zenodo has minted it |

And the ordering that would have prevented this: **cut the tag last**, after every metadata
file is committed and pushed, not between two of them.
