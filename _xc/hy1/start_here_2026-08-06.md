# START HERE — after 2026-08-06

**Read this first, then `_xc/hy1/FINDINGS.md`.** The reader's standing requirement is
unchanged:

> "The PDFs are the final authority... first, we need to have in the corpus the same
> material that is in the PDF. Second we need reliable links that take the user to the
> exact and complete passage that is commented."

HEAD **`432e7bfe`** on `main`. **Everything is pushed.** Ten commits landed 08-05/06,
`0e181816` through `432e7bfe`. **No corpus file and no live builder changed. `site/` is
untouched. Nothing was run with `--write`.**

## The method that now governs — unchanged, and it earned its keep ten times

**Compare against the printed page, never against the corpus.** To which this session adds
one rule, learned the hard way:

> **RUN THE INSTRUMENT, DO NOT READ YOUR CACHE OF PART OF IT.**

Three of this session's worst errors were the same shape — inspecting one layer of
something and pronouncing on the whole:
- `paragraph['text']` without the `verse/` side-map → "35Abhi07 is flat". It is not.
- `pline.stream()` without the `j` index → "the blank lines are discarded". They are not.
- a cached `head_pages`/`tail_pages` without the index gaps → "the gate cannot see back
  matter on 26 volumes". It can.

**And one more, which is new and worse:** a page-level statistic fails on a page that lacks
its own reference class. It has now happened **three times** — `vol_margin` on a page of
pure verse, the body-leading mode on a page of dyads, the prose measure on a page of lists.
**If a statistic needs prose to calibrate, take it over the volume, not the page.**

## What is new and stands

| | |
|---|---|
| **The block boundary is in the coordinates.** | `pdftotext -bbox`; a new block begins where the leading exceeds *that page's own* body leading by >3pt. No constant, no per-volume flag. `_xc/hy1/blockmap.py` → `blocks3/` (118 vols, ~1 min). |
| **It reproduces the reader's hand-drawn stanza breaks exactly.** | `06ViT06` p28: block starts on `Paññāvisuddhāya`, `Saṁghañca`, `Samantapāsādikasaññitāya`, `Saññā nimittaṁ` and the prose below — his four groups, no others. |
| **Joined to `pline` at 99.93%** of 1,354,117 body lines. | `blockjoin.py` → `bjoin2/`. Digits dropped from the key (a superscript marker sorts elsewhere in bbox word order; keeping it cost 8%). |
| **`display` ≠ gāthā.** | `display` means *the page sets this apart*. Whether it is verse is a different question no geometry answers. Conflating them is the original §6.2 error. |
| **Ragged vs justified needs TWO signals.** | Right edge against the **volume's** prose measure, AND the line ending. Each covers the other's failing case. Control 10/10. `ragged.py`. |
| **The reserved non-gāthā class is DECIDED.** | The reader: `35Abhi07` p74, `29Abhi01` p14, `26Khu09` p4, `18Khu01` — **all prose**, not gāthā, no class of their own. Prose whose printed line breaks carry meaning. |

## Superseded — do not quote these numbers

- **865 printed lines / 672 blocks** (§16) → **492 / 299**. `39Abhi11`'s 120 were decorative
  rules (`____`), not text.
- **13,910 blocks with no `verse/` entry** → 5,503, and still **not** claimed as a fault.
- **26 volumes aligning below 97%** (§18.2) → **one** (`03ViT03`, 98.74%). The rest was my
  own edge filter.
- **"the hyphen is the second cause of class 2"** → it is not a cause of class 2 at all, and
  "a pāda never ends mid-word" is refuted by the edition in 38 volumes.
- **`34KhuA15` +260 is over-splitting** (§20.2) → most of it is legitimate quoted gāthā.

## Next, in order

1. **THE BLOCKER: three fragments in `35Abhi07`.** The page prints
   `26. Na cakkhu na cakkhundriyaṁ. . Na indriyā na sotindriyaṁ.` as ONE line; with
   `BLOCKBREAK=1` the patch draws `…Na indriyā na` — a fragment. Tightening the cursor from
   substring to exact match did **not** change it, so the cause is elsewhere. **A repair
   that draws a fragment of a printed line is worse than the fault it fixes.** Nothing else
   proceeds until this is found. `python3 _xc/hy1/bbgate.py 35Abhi07`.
2. **Then the rest of the `katha` volumes**, measured with `bbgate.py`, and only then
   `pbreak/` re-derived and the full gate set run old-against-new: `regress`, `check_links`,
   `check_ordinal`, `check_concordance`, `check_bold_fidelity`, `check_layout`,
   `verify_render_vs_pdf`. Bold spans are offsets into `pr.text` and `pbreak` records
   address a sequence of `fmtLine` calls — both are sensitive to exactly this change.
3. **Class 2 (9,854) and class 1 (9,155) are both SUSPECT.** `check_page_fidelity`'s PAGE
   side calls `35Abhi07`'s mātikā lines verse; the reader says prose and the corpus already
   treats them as prose. **An unknown share of both counts are checker false positives.**
   Re-measure before working from them.
4. **Class 4, 11,414** — "needs pages read, not a rule", and pages can now be **rendered and
   read directly** (`pdftoppm -r 115 -png`, then look). This is much cheaper than it was.
5. **Position / re-segmentation** — the largest job. `19AnA03` is 46% under-segmented and
   passes every check. The block map is a second instrument not derived from the corpus.
6. **Requirement 2, the links.** Unchanged. `decision_dim_the_condemned_links.md` never built.

## Hazards

- **`.git` debris**: the sandbox cannot unlink, so every commit made from it leaves
  `tmp_obj_*`. `git gc --prune=now` from the host (run it from inside `~/Documents/OSBCT`).
- **Claude can commit but CANNOT push** — the remote is SSH, the sandbox has no key. No
  model or connector changes that; there is no GitHub connector in the registry.
- `.git/index.lock` and `HEAD.lock` must be `mv`-ed aside around each git call; `rm` fails.
- **`nav.json` rebuild still owed**, now also naming `48AbhiA01`.
- **`pbreak/` must be re-derived after any builder change.**
- `blocks/` (pre-clustering) and `blocks2/` (pre-`xMax`) are kept **as controls** — do not
  delete, and do not read them as current. Current is `blocks3/`.
- `_xc/hy1/dyad.py` and `joined.py` produced **wrong numbers** and are kept only as the
  record of two bad measurements. `joined2.py` is the live one.

## The lesson, restated

The reader's screenshots found faults no check did — and this session, the reader also
found **three faults in my own work**: that `35Abhi07`'s corpus is fine, that the dyads are
two lines, and that the page references I gave him were wrong. **Ship, let him look, and
believe him** — and when he says something you measured is wrong, he is the more likely to
be right.

The other thing that worked: **keeping an independent measure of the same fault.** The
builder alone looked like a success. It was the measure predicting 18 while the repair
delivered 260 — and later `bbgate.py` reading the produced side-map rather than the block
map — that caught the damage. `letters identical` cannot see a break in the wrong place.
