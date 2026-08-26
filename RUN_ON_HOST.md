# Run on the host — 2026-08-26

## The command

```bash
cd ~/Documents/OSBCT
./push.sh
```

`COMMIT_MSG.bak` carries the highlight-contrast fix. The build IS stamped
(`2798a6a45568` → `3d1e09456afa`), so guard 3 will pass, and `push.sh` clears the
stale zero-byte `.git/index.lock` itself — expected, no action needed.

Then, **once Pages has finished**, check cache-busted:

```
https://buddha-dhamma.net/build.json?cb=<anything-new>   ->  3d1e09456afa
```

The previous deploy took about **four minutes**; the first two reads still
answered the old stamp. That is now the fifth instance of the same lesson. Do not
conclude a deploy failed from an early read.

## Then look at Columns again — the one thing no gate covers

Open `12Sam01` in **Columns** with **P and A** on, and hover a Pāḷi paragraph.

**Both paragraphs in that row should now take a clearly lighter panel together**,
with a defined outline — not just the one you are pointing at.

The wiring was already right before this build; what changed is that the panel
is now `--active` with a `--faint` outline instead of `--hover` with a `--line`
one. Measured in a real browser, the old pair sat **15 levels out of 255** from
the page in the dark theme, which is why it read as "only one lights": the only
unmistakable change was the toolbar, and the toolbar appears on one paragraph.
The new pair is 23 levels dark, 26 light.

If it is still hard to see, say so — the number is now gated
(`check_columns.js`, minimum 20, negative control run against the old value), so
raising it is a one-line change to a threshold that is documented as derived
from your reading rather than picked.

Everything else there was checked and is fine: the columns hold their own layers
(reported fine), the spacing in a cell holding a long commentary run (reported
fine), and the hover buttons (confirmed by screenshot, correctly layer-aware —
A|T on the canon paragraph, P|T on the commentary).

**Why this still needs an eye.** `pipeline/check_columns.js` proves the wiring —
an event arriving at a cell reaches the row — but jsdom has no layout and no
hit-testing, so it cannot prove the pointer would ever reach the cell. That is
exactly the half that was broken, and it was a reader looking at the screen that
found it. Instrument for the wiring, reader for the pointer.

## Not done, deliberately

* **`site/reader/sections/` was NOT rebuilt** for `19Khu02`, `28KhuA09` or
  `27KhuA08`. `check_derived` reports it as ADVISORY, not blocking. The `sutta`
  field feeds the citation and title bar — verified by rendering: `27KhuA08` ¶244
  offers `Aṭṭhakathā, Dāsivimānavaṇṇanā § (p.82)` and ¶362
  `Aṭṭhakathā, Niddā-suniddāvimānavaṇṇanā § (p.106)`, both page numbers matching
  the pages the headings were read on. But the **☰ Contents is built by
  `buildOutline` from `c.headings`**, a separate artefact, so it does not yet
  list those sections. Rebuilding the per-volume nav is its own piece of work —
  "NEVER import one; run as a subprocess".
* **`_xc/cols/probe_columns.js` and `probe_27_cite.js` are kept**, not tidied
  away. They are how the findings were established and they are cheap to re-run.

## One property of the tooling, so it does not mislead

`stamp_build.py` **is not idempotent**: BUILD is a hash over the JSON under
`site/`, and `site/build.json` is one of those files, so writing the stamp
changes the input to the next stamp. A dry run right after a `--write` reports a
different number and nothing is wrong. Do not re-run `--write` "to be safe" — it
produces a spurious build and dirties a clean tree. Verify a deploy by comparing
the fetched `build.json` against the committed `site/build.json`.
