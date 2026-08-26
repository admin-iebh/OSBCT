# The columns were never out of order — the rows emitted too many cells

**Reader-reported 2026-08-26**, with a screenshot of `12Sam01`
(Oghataraṇasutta), P and A both on, view `Columns`:

> the left column, headed **PĀḶI (TIPIṬAKA)**, was empty but for a `page 1` rule;
> the right column, headed **AṬṬHAKATHĀ**, carried the **canon** text of the
> sutta — `Evaṁ me sutaṁ–ekaṁ samayaṁ Bhagavā Sāvatthiyaṁ viharati Jetavane…`,
> apparatus and all.

The report was "P should be on the left and A on the right".

## 1. The obvious reading of that report is wrong, and checking cost nothing

`activeKeys()` is `['canon','A','T'].filter(k=>state.active[k])`. Canon is first
**by construction**; there is no ordering to get wrong, and the two headings in
the screenshot were already in the right order. Reordering anything would have
moved the headings away from the columns and made it worse.

So the question was not *which order* but **what is in each cell** — and that is
a question about a render, not about the source. `_xc/cols/probe_columns.js`
boots the real reader over the real data in jsdom, sets
`view='columns'`, `active={canon,A}`, and dumps every child of the first rows.

## 2. What it found

    -- row 0, 4 cell(s)
       cell 0  class="pgrule"        "page 1 ⧉"
       cell 1  class="para canon"    "1. Evaṁ me sutaṁ–ekaṁ samayaṁ Bhagavā …"
       cell 2  class="pgrule"        "page 3 ⧉"
       cell 3  class="para l-A"      "1. Yaṁ panetaṁ “evaṁ me sutan”ti-ādikaṁ …"

**`.grid` is the grid; `.rowline` is `display:contents`.** So every child a row
emits is a *direct grid item*. With two columns, four items wrap: `page 1` takes
column 1, the **canon paragraph takes column 2** — under the Aṭṭhakathā heading —
and the rest falls onto an implicit row. That is the screenshot, exactly.

Two things make a row emit more items than there are columns:

1. **`block()` returns `rule + <div class="para">`.** Wherever a printed page
   turns at that paragraph it prepends a `<div class="pgrule">`, and that rule
   takes a cell.
2. **A band cell with several targets is several `.para` siblings**, not one
   cell. `ts.map(t=>block(k,t.key,t)).join('')`.

Measured before anything was changed:

| volume | bands | rows | rows emitting too many | cells holding the wrong layer |
|---|---|---:|---:|---:|
| 12Sam01 | P+A   | 517  | 176 | 270 |
| 12Sam01 | P+A+T | 517  | 248 | 505 |
| 12Sam01 | P+T   | 517  | 186 | 279 |
| 18Khu01 | P+A   | 1869 | 741 | 778 |
| 09Ma01  | P+A   | 511  | 140 | 237 |

`18Khu01` row 0 emitted **twenty-three** items into two columns: one canon
paragraph against a nineteen-paragraph commentary run.

## 3. The fix, and why it is the wrapper and not the order

Each key's contribution is wrapped in one `<div class="cell">`. The count is then
`keys.length` **whatever any one cell contains** — so it holds for P+A, P+T, A+T
and P+A+T alike, which is what "fix it for everything" needs. An empty string
from `block()` (an unloaded volume) still yields an empty cell and the alignment
survives that too.

    .cell{min-width:0;display:flex;flex-direction:column;gap:14px}
    .cell>.pgrule{margin:0}

`min-width:0` keeps a long unbroken Pāḷi compound from widening its track; the
flex gap restores the 14px the grid row-gap used to give between stacked
paragraphs, and the rule's own margins are dropped inside a cell so the two do
not add up.

## 4. The gate

`pipeline/check_columns.js`, **run red on all five cases above before the fix**
and green on all five after. It asserts the invariant, not the symptom: *a row
emits exactly one grid item per active layer, and the item at index k carries the
layer at `activeKeys()[k]`*. Asserting "canon is left" would have passed on the
broken build, because canon *was* left — in the header.

It boots **a fresh window per case**: sharing one window kept every volume any
case had loaded in `cache`, and three openings of a Saṁyutta volume with all
three bands on hit node's 2 GB ceiling and aborted the run *after* it had printed
passes. A gate that dies mid-way looks like a gate that ran.

## 5. Controls

* `check_layout.js` on `12Sam01 18Khu01 09Ma01 27KhuA08` gives **byte-identical
  output before and after** — run against `HEAD`'s `reader2.html` through
  `OSBCT_READER`. Its three FAILs (`page-rule-misplaced`, `page-rule-repeated`)
  are **pre-existing and in the SINGLE view**, which this did not touch.
* `check_search`, `check_dimmed`, `check_reader_range`, `check_runcut`,
  `check_tipplace`, `check_apd_gear`, `check_lookup_reach` all green.
* `check_fn_markers.js` OOMs at node's default heap and passes at
  `--max-old-space-size=6144`. **Not a regression**: it never sets `state.view`,
  so it never renders the columns branch. Pre-existing harness ceiling.

## 6. The second defect in the same three lines — asked as a question, answered by the reader

`.rowline` is `display:contents`, and the reader attached
`onmouseenter`/`onmouseleave` **to the rowline itself** to drive
`.rowline.hot .para`. An element with `display:contents` generates no box, so the
pointer can never enter it and `mouseenter` never fires.

This was written up as a **question, not a finding**, because jsdom does no
layout and no hit-testing: the probe that settled §2 could not settle this. It
went to the reader with a description of exactly what to look for.

**Answered 2026-08-26: "only the one I'm on."** Pointing at the Pāḷi paragraph
left the Aṭṭhakathā paragraph opposite it flat. The row-pairing highlight had
never worked in Columns view.

### Why it survived so long

`.para:hover .tools` is **pure CSS on a real box** and always worked. So hovering
a paragraph *did* something visible — the jump chips, facsimile, copy-text and
copy-citation buttons faded in, correctly layer-aware (A|T on the canon
paragraph, P|T on the commentary). The row looked alive. The half that was
missing is the half that matters in a two-column view: **which commentary belongs
to the verse beside it**, when the two columns have drifted apart vertically, as
they always do — a commentary paragraph is usually many times longer than the
verse it comments on.

### The fix, and what the gate can honestly claim

Handlers move to `.cell`, which is a real box in every engine; each toggles
`hot` on its parent `.rowline`. Moving between the two cells of one row fires
leave-then-enter in the same turn, so `hot` ends up set with no paint between.

`check_columns.js` dispatches `mouseenter` **at a cell** and asserts the **row**
goes hot, and off again on `mouseleave`. Red on the old wiring
(`{"on":false,"off":true}`), green after.

**What that gate proves and what it does not.** It proves the WIRING: an event
arriving at a cell reaches the row. It cannot prove the pointer would ever reach
that cell, because jsdom has no layout — and that is precisely the half that was
broken. **The instrument settled the wiring; a reader settled the pointer.**

## 7. The gate went green and the reader still said "only one lights"

**And the reader was right, for the third time in this one defect.**

The wiring fix shipped, `check_columns.js` passed, and the report came back
unchanged. Measured in a real browser on the live build — not inferred, and not
in jsdom, which cannot answer this:

| pointer on | row `hot` | Pāḷi bg | Aṭṭhakathā bg |
|---|---|---|---|
| the Pāḷi paragraph | yes | `rgb(35,32,25)` | `rgb(35,32,25)` |
| the Aṭṭhakathā paragraph | yes | `rgb(35,32,25)` | `rgb(35,32,25)` |

Both paragraphs took the identical highlight, in both directions. **The wiring
was fixed and the feature was still useless**, because the page is
`rgb(20,18,16)` and `--hover` is `rgb(35,32,25)` — **15 levels out of 255**. The
only unmistakable change on hover is the toolbar, and the toolbar appears on the
paragraph under the pointer alone. So "only one lights" was an accurate report of
what a person can see; the asymmetry was the buttons, not the highlight.

A correction to §6 while here: the earlier claim that the coloured left bar
"brightens" on a hot row was wrong. `.rowline.hot .para{border-color:var(--line)}`
sets all four sides, and the per-layer rules only put the left bar **back** to
the colour it already had. The entire visible difference was a faint panel and a
faint 1px outline.

Now `--active` with a `--faint` outline, chosen by the reader.

### The assertion that would have caught it

A gate on "does the class get applied" is not a gate on the feature.
`check_columns.js` now reads the CSS tokens and asserts a minimum separation
between the hot background and the page **in both palettes**:

    light  --active #efe7d7 vs --bg #f7f5f1 = 26 levels   ok
    dark   --active #2b2618 vs --bg #141210 = 23 levels   ok

**The threshold is derived, not picked.** `--hover` measures 15 dark / 16 light
and was reported invisible; `--active` measures 23 / 26 and was reported
readable. 20 is the only round number separating the rejected value from the
accepted one. **Negative control run**: putting `--hover` back makes the gate
fail on both themes with "a reader could not see this". If a future palette
change trips this, the question is whether a reader can still see it — not what
number would make it pass.

### The shape of this whole defect, worth keeping

Three rounds, and the instrument was wrong in a different way each time:

1. The reader said "P should be on the left". **The order was never wrong** — the
   rows emitted too many cells.
2. The wiring gate could not see the hover at all, because jsdom has no
   hit-testing. **A reader answered it.**
3. The wiring gate went green while the feature stayed invisible. **A reader
   answered that too**, and only then did a measurable assertion exist.

Each round the gate was extended to cover what the reader had just caught. None
of the three would have been found by running the gates.
