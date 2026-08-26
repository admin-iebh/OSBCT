# Commands to run on the host — 2026-08-26 (section names)

> **DONE 2026-08-26. Kept as the record of how it went, not as work owed.**
> Both `pbreak` files came back byte-identical (`8cb75b08…`, `8362787b…`), the
> stamp went to `2b856038234a`, and the live site serves it. Nothing below is
> outstanding.

**This one was NOT optional and NOT just a push.** The sandbox could not rebuild
one derived artefact, and `stamp_build.py` will keep refusing until it is done.
That refusal is correct — it is the 2026-07-30i guard, which exists to stop a
stale artefact being published under a fresh cache-buster.

---

## 1. Rebuild the one artefact the sandbox could not

`derive.py` skips an existing output, and the sandbox cannot unlink the old
file, so this must happen here:

```bash
cd ~/Documents/OSBCT
rm -f .git/index.lock
for v in 19Khu02 28KhuA09; do
  mv site/reader/pbreak/$v.json /tmp/$v.pbreak.old
  python3 _xc/pagemark/derive.py $v --out site/reader/pbreak
done
```

**Then check they came back the same**, which is the point of doing it rather
than forcing past it:

```bash
md5sum /tmp/19Khu02.pbreak.old  site/reader/pbreak/19Khu02.json
md5sum /tmp/28KhuA09.pbreak.old site/reader/pbreak/28KhuA09.json
```

The two hashes should match — the section-name write added a `sutta` field and
touched no text and no page data. `pagespan.json` was rebuilt in the sandbox and
came back **byte-identical** (`9ce1a269…`), and the search index's `inv` — the
searchable terms — is unchanged, so a matching hash here is the expected result.
**If they differ, stop and look**: something changed that should not have.

## 2. Stamp

```bash
python3 pipeline/stamp_build.py --write
```

It refused before step 1 with three stale artefacts (`pagespan`, `search index`,
`pbreak`); the first two are already rebuilt. Do **not** use `--force`.

## 3. Look at the diff

```bash
git status --short
python3 pipeline/check_sections.py     # 4 named cases, all read off printed pages
python3 pipeline/check_links.py
python3 pipeline/check_concordance.py
```

`site/19Khu02.json` gains a `sutta` field on 3,653 of 3,660 paragraphs — 3
distinct names become 444. `site/index/19Khu02.idx.json` changes only in its
`paras` block, which is what search results display; `inv` is untouched.

## 4. Commit, push, Pages

```bash
./push.sh
```

Then GitHub → Actions → **Run workflow**. Never "Re-run failed jobs".

```bash
curl -s "https://buddha-dhamma.net/build.json?cb=$RANDOM" ; echo
```

Read it cache-busted or you are measuring the past — that has now given a false
"the deploy failed" three times.

**No R2 sync.** Nothing under `stores/` changed.

## 5. Then look at it as a reader — this is the part that matters

Open `19Khu02` and page through the Petavatthu. Every paragraph should now sit
under the section the edition prints — `Khettūpamapetavatthu`,
`Sūkaramukhapetavatthu`, and so on — where before the whole first third of the
book was headed with a *Vimānavatthu* section name.

Two things to look at while you are there, both recorded and neither repaired:

* **ord 483** carries the vagga `'Itthivimāna      4. Mañjiṭṭhakavagga'` — two
  headings glued together with the index left in. The edition prints
  `Mañjiṭṭhakavagga`. 24 of the other 25 vaggas agree with the edition.
* **Three headings are still stored as numbered PARAGRAPHS** — ord 388
  `'17. Valliphaladā yikāvimānavatthu (6)'`, ord 390, ord 857. They collide with
  real paragraph numbers and they broke a classifier earlier today. They should
  leave the paragraph stream now that the names are carried properly.

---

## Not done, and deliberately

**`28KhuA09` IS DONE TOO** — 51 section names, 1 distinct becomes 47, and the
Mātikā agrees at 51. **`name-match` recovered and rose above where it started:
76.442 -> 76.141 -> 76.67%, over 17,440 links.** That was the prediction written
down before it was tested, and it held.

**`27KhuA08` REFUSES and is left alone.** Its body scan finds 83 headings where
the Mātikā lists 79, and until that is understood it must not be written: a
miscounted heading does not leave a gap, it spreads the previous section over
the missing one — the very defect being repaired. Whoever picks it up: the four
extra are the thing to find. Full account:
`claude/sections_the_edition_prints.md` §7-8.

The other 116 volumes are untouched. The canon reader is blind in 20Khu03,
29Abhi01 and 36-40Abhi; the commentary reader has been tried on exactly two
volumes.

## The ordering rule, for the next actual release

**CUT THE TAG LAST.** Every metadata file committed and pushed before the tag
exists, or Zenodo mints a deposit describing the previous release. Broken three
times. `v2.7.0` is a lightweight tag with a DOI — **leave it**.
