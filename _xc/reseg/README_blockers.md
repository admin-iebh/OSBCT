# The three blockers, cleared — `_xc/reseg/` only, nothing under `site/` touched

2026-08-03, following `7e3a9c0a` (re-segmentation prototype) and `4d4a1db7`
(bold redistribution).  All output is under `_xc/reseg/`; `git status` shows
untracked additions and nothing else.

## The evidence source

`pline.py` builds the volume's **printed line stream** — `extract.py`'s own
`raw_pages` + `split_page` with the glyph-errata register — and `locate.py`
turns it into one letter string with a letter → line map.  Every anchoring
decision below is made by **printed position**, and every check is decided by
the printed page.  The old→new ordinal remap is never consulted in an
assignment, which is what makes the checks independent of what they check.

`b3/locate_paras.py` anchors every paragraph to that stream.  **673 of 673
re-segmented paragraphs locate as a contiguous run of printed lines; 99 of 109
shipped ones do** (a shipped lump can span a heading, which the corpus drops,
so its letters are not contiguous).  That is an independent corroboration of
the re-segmentation itself, from a source `reseg.py` did not use for the test.

## Blocker 1 — `id`  (`b1/`)

`id` = `slug(book)/slug(vagga)/slug(sutta)/TAIL`, TAIL = `n` or `u<pdf_page>`
(`_fnprobe/rebuild_corpus.py:55`).

Every colliding group in this volume — 7/7 shipped, 190/190 re-segmented — sits
on **one pdf page**, and the shipped numbered collision
(`…/Tirokuṭṭasuttavaṇṇanā/4`, twice on p192) is the same class.  Scheme: leave a
base used once alone; give every member of a repeated base a suffix `.K`, K the
1-based ordinal rank inside the group.  Confined to a page, that IS a
within-page counter; ranked inside the group, it also survives the 4,125 groups
that DO span pages elsewhere in the corpus.

    673 ¶ -> 673 distinct ids, 0 collisions.  Shipped: 109 -> 109, 0.
    Applied to all 118 shipped volumes: 0 volumes still colliding.
    4 of 4 negative controls fire.

No consumer parses the id (survey in `b1_consumers.py`).  One measured cost:
1 of 58 `apparatus/*.app.json` keys stops resolving; indexing by base as well
in `rekey_apparatus.py` restores 58/58.

## Blocker 2 — `verse/`  (`b2/`)

**What it is keyed to:** the 67 entries carrying a `groups` key are exactly the
67 numbered corpus paragraphs — `pair_ords` in `build_khu_volume.py`'s kathā
path, which pair 1:1 with the printed NUMBERED UNITS.  So the key is the
printed unit, and a unit is a RUN.  The other 4 entries have no `groups` key
and `reader2.html:1474` therefore ignores them entirely; all four hold printed
gāthā the corpus does not contain.  **Four restored verses are in the map and
have never reached the page.**

**What the entries hold**, against the re-segmented corpus letters:
`before` prose 25 (all in corpus), `after` prose 378 (all in corpus),
`after` gāthā 65 (all in corpus), `after` gāthā 6 (absent — restored verse).

That is the finding the design turns on: the kathā substitution exists because
the corpus lumps a printed unit and the page sets it as many blocks.
Re-segmentation puts those blocks in the corpus, so the substitution's only
remaining jobs are the 6 absent gāthā and the line breaks of the 65 the corpus
holds run-on.

**Design.** Locate all 474 blocks on the printed page with a monotone cursor;
assign each to the new paragraph whose printed extent contains it; merge only
the 7 groups a block straddles (9 paragraphs absorbed, added to `hide/`); drop
an entry only when its blocks say letter-for-letter what its paragraphs already
say.  63 entries survive, 250 are dropped as provably redundant.

    per-entry SEMANTIC check: 63 of 63 entries reproduce the PRINTED PAGE over
      their own extent, exactly.
    RENDERED-LETTER EQUIVALENCE: 316,378 letters shipped, 316,378 new,
      delta 0, identical.  (A re-implementation of reader2.html's own render
      order: front matter, sections, the verse branch gated on `vmap.groups`,
      body, uddāna.)
    8 of 8 negative controls break the equivalence, including the
      MONOTONIC remap the doc warned about (delta +111,858).

`RESTORE=1` additionally puts the 4 unrendered restored gāthā back, through
`sections/` with `k:'gatha'` — the path `reader2.html:1735` already has for
"display verse the page prints above a paragraph and the corpus does not hold".
Deliberate delta: **+189 letters**.  Default is `RESTORE=0` so the equivalence
above is an equality and not an equality-plus-an-excuse.

## Blocker 3 — `uddana/`, `hide/`, `sections/`  (`b3/`)

* **`uddana/` — LAST of the run**, verified by printed order: 23 of 33 blocks
  are printed in the gap after the anchor paragraph and before the next.
  The other 9 are **not recovered from print at all — the corpus holds them
  too**, invisible until now because their containing paragraph was a numbered
  unit drawn from the printed stream.  1 IS a whole new paragraph (hidden);
  8 are the tail of a longer one (the verse entry keeps substituting without
  them).  4 of 4 controls fire; first-of-run misplaces 32 of 33.
* **`hide/` — the whole run.**  Hidden letters identical, 810 = 810.  Honest
  qualification: **inert in this volume** — all 3 shipped keys sit on unsplit
  paragraphs.  Demonstrated on a split ordinal instead: pointer semantics would
  leave 1,710 letters of old ord 0 on the page.  `hide/` GAINS 11 ordinals
  (9 merge-absorbed, 1 uddāna-claimed, 1 leaked heading).
* **`sections/` — NOT first-of-run.**  First-of-run is right for 97 of 109
  headings and wrong for 12.  Anchored by printed position instead: 105 ok.
  8 headings land on a different new ordinal.  The reason is real: the printed
  heading sits above prose the old corpus had swallowed into the PREVIOUS lump,
  and the shipped page gets it right only because `verse/`'s `before` blocks
  lift that prose out.  The equivalence check found this at ord548 as a pure
  ordering difference (delta 0, not identical).
* **`incipit/`, `booktitle/`, `ord/`** — also per-paragraph, also unlisted.
  incipit and booktitle first-of-run; `ord/` (n → ordinal) first-of-run,
  17 of 17 land on a paragraph carrying that `n`.

## Outputs

    b1/ids_20KhuA01.json                 673 ids, 0 collisions
    b1/ids_shipped_20KhuA01.json         the same rule on the shipped 109
    b2/verse_20KhuA01.json               63 entries
    b2/final_hide_20KhuA01.json          hide/, run-expanded + 11 gained
    b2/final_uddana_20KhuA01.json        last-of-run, stepped off hidden anchors
    b2/final_sections_20KhuA01.json      printed-position anchoring
    b3/{incipit,booktitle,ord}_20KhuA01.json
    b3/anchors_20KhuA01.json             every paragraph's printed extent
    RESULTS_b1.log RESULTS_b2.log RESULTS_b3.log RESULTS_inventory.log
