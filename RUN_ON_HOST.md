# Run on the host — 2026-08-26

## The command

```bash
cd ~/Documents/OSBCT
./push.sh
```

`COMMIT_MSG.bak` carries the row-hover fix. The build IS stamped
(`8196f1a01c65` → `2798a6a45568`), so guard 3 will pass, and `push.sh` clears the
stale zero-byte `.git/index.lock` itself — expected, no action needed.

Then, **once Pages has finished**, check cache-busted:

```
https://buddha-dhamma.net/build.json?cb=<anything-new>   ->  2798a6a45568
```

The previous deploy took about **four minutes**; the first two reads still
answered the old stamp. That is now the fifth instance of the same lesson. Do not
conclude a deploy failed from an early read.

## Then look at Columns again — the one thing no gate covers

Open `12Sam01` in **Columns** with **P and A** on, and hover a Pāḷi paragraph.

**Both paragraphs in that row should now take a lighter panel together**, not
just the one you are pointing at. That is the fix. If only the one under the
pointer lights, the fix did not take and I want to know.

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
