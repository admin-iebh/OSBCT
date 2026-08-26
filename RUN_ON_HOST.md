# Run on the host — 2026-08-26 (second session of the day)

Everything below was done in the sandbox and is sitting in the working tree.
**Nothing is committed and nothing is pushed**, because the sandbox has no write
access to `.git`.

## 1. Two commands

```bash
cd ~/Documents/OSBCT
rm -f _xc/cols/head_reader2.html   # scratch: HEAD's reader2.html, for the
                                   # before/after control on check_layout.
                                   # The sandbox cannot delete it.
./push.sh                          # COMMIT_MSG.bak carries this session's message
```

`push.sh` clears the stale zero-byte `.git/index.lock` itself — one was left
behind by a `git stash` that the sandbox could not complete. That is guard 1 in
the script and it is expected; no action needed.

The build IS stamped (`2b856038234a` → `8196f1a01c65`), so guard 3 will pass.

## 2. After the push — the one thing that needs an eye, not a gate

**Look at Columns view in a real browser**, `12Sam01` with P and A on. The fix is
gated headlessly and the gate is green, but jsdom does no layout: it can prove
each layer is in its own cell and cannot prove the page *looks* right. Worth
checking in particular:

* the vertical rhythm inside a cell that holds several commentary paragraphs
  (`18Khu01` ¶1 holds nineteen) — `.cell` uses `gap:14px` and zeroes the page
  rule's own margins;
* a long unbroken Pāḷi compound not widening its column (`min-width:0`);
* **row hover.** `.rowline` is `display:contents` and the hover handlers are
  attached to it, which generates no box. If `.rowline.hot .para` has never
  fired in Columns, that is a second defect in the same three lines — recorded
  as a QUESTION, not a finding, in
  `claude/the_columns_were_never_out_of_order.md` §6. It needs a browser.

**And bust the cache when you check the live site, and give Pages time.** That
has now produced a false "the deploy failed" four times.

## 3. Not done, deliberately

* **`site/reader/sections/27KhuA08.json` was NOT rebuilt.** `check_derived`
  reports it as ADVISORY, not blocking. The `sutta` field this session wrote
  feeds the citation, the title bar and `name_at` — verified by rendering:
  ¶244 now offers `Aṭṭhakathā, Dāsivimānavaṇṇanā § (p.82)` and ¶362
  `Aṭṭhakathā, Niddā-suniddāvimānavaṇṇanā § (p.106)`, and both page numbers
  match the pages the headings were read on. But the **☰ Contents is built by
  `buildOutline` from `c.headings`**, a separate artefact, so the Contents for
  this volume does not yet list the 84 sections. The same is true of `19Khu02`
  and `28KhuA09` from the earlier session. Rebuilding the per-volume nav is its
  own piece of work — "NEVER import one; run as a subprocess".
* **`_xc/cols/probe_columns.js` and `probe_27_cite.js` are kept**, not tidied
  away. They are how the two findings were established and they are cheap to
  re-run.
