# Commands to run on the host — v2.7.1

Run from the repository root, in order.

**Ordering rule, and it is the one this project has broken three times:
CUT THE TAG LAST.** Every metadata file must be committed and pushed before
the tag exists, or Zenodo mints a deposit describing the previous release.
Steps 1–4 first; the tag is step 5.

---

## 1. Delete what the sandbox could not

```bash
cd ~/Documents/OSBCT

# the zero-byte git lock the sandbox leaves behind (push.sh also does this)
rm -f .git/index.lock

# backups made before writing the register — keep them until you have read
# the diff, then remove
rm -f data/errata.json.pre_verdicts data/glyph_errata.json.pre_verdicts

# the old pbreak file, moved aside so derive.py would rewrite it; the new one
# came back BYTE-EQUAL, so this is pure leftover
rm -f site/reader/pbreak/25VsmT01.json.preE042

# left over from earlier sessions, still listed as hazards in the handoff
rm -rf _review/clips            # first review run, superseded by clips_b/
rm -f _xc/hy2/_dump.js _xc/hy2/_gap.js
```

## 2. Look at the diff before committing

```bash
git status --short
git diff --stat

# the only served text that changed — should be ONE character, ī -> e
git diff site/25VsmT01.json

# the three checklist files must ALL say 2.7.1
grep '"version"' .zenodo.json
grep '^version:' CITATION.cff
grep OSBCT_VERSION site/i18n.js | head -1
```

## 3. Commit and push

`COMMIT_MSG.bak` carries the v2.7.1 message (kept also as
`COMMIT_MSG_verdicts.bak`). `push.sh` re-checks the stale lock, the stale
message and the forgotten stamp, then prompts before committing.

```bash
./push.sh
```

By hand, if you prefer:

```bash
git add -A && git commit -F COMMIT_MSG.bak && git push
```

## 4. Fresh Pages run, and the R2 sync

GitHub → Actions → **Run workflow**. Never "Re-run failed jobs".
Then hard-reload the reader (Cmd-Shift-R).

```bash
bash pipeline/r2_upload.sh
```

**Required this time.** Five files under `stores/lookup/` changed with the
E042 word, and the DPD refresh from the 08-09 session has still never been
uploaded — until it is, production serves the old dictionary store.
`--checksum` sends only what changed.

## 5. NOW cut the tag — annotated, unlike v2.7.0

```bash
git tag -a v2.7.1 -F RELEASE_271.bak
git push origin v2.7.1
```

`v2.7.0` was cut lightweight, which is why `git tag -n99 v2.7.0` shows its
commit message instead of a tag message. Nothing is broken by that and it
should be **left alone** — it has a DOI now. This one goes back to the house
pattern.

## 6. The GitHub Release

Title and body are in `RELEASE_271.bak`.

```bash
gh release create v2.7.1 \
  --title "v2.7.1 — one word moves, nine sites are withdrawn, and the register stops contradicting itself" \
  --notes-file <(sed -n '/^----$/,$p' RELEASE_271.bak | tail -n +2)
```

or paste by hand at `.../releases/new?tag=v2.7.1`.

## 7. After Zenodo mints the v2.7.1 DOI

Read it **from the record**, not from a guess, and add it to the ledger in
`CITATION.cff` — the same way v2.7.0's `10.5281/zenodo.21863987` was added
this session. Tell me the DOI and I will write the entry.

---

## Already done, for the record

* `v2.7.0` is deposited: **10.5281/zenodo.21863987**, "Published August 9,
  2026 | Version 2.7.0", with its `New in 2.7.0` paragraph already on the
  record at minting. Third consecutive deposit to arrive describing itself
  correctly; no in-place correction needed. It is now in `CITATION.cff`.
* Its GitHub Release, if you still want one, is in `RELEASE_270.bak`.
