# The section names are read as one n-gram shard, not whole

**2026-09-05, fourth session.** Closes item 1 of the third session's list: `index/names.json`.

## 1. Measured before anything changed

`names.json` — every printed heading, so a sutta can be found by its name — is 16,998
interned labels and 33,263 rows (label, volume, ordinal, layer): **1,087,042 bytes raw,
255 KB gzipped**; the labels are 536 KB of it, the rows 550 KB. Both search UIs fetched it
whole before their first query and scanned every label by substring on every search.
`perf_search.js` (`max` column, added in the third session) on `e54900ddf`, all within
baseline: **every cold query's largest file was this one, 1.09 MB** — twice the largest
postings shard (`maha.json`, 514 KB) — and the cold median word read 2.28 MB raw, of which
names.json was 1.09. On search.html the first query *waited* for it (`await
ensureNamesOnly()` before `S.search`); on reader2 likewise (`await ensureNames()`).

Its shape over the labels' folded letters: 24 characters per label on average; every
substring of length 2–8 of each label's letter runs is a candidate gram, as in `tg/`.

## 2. Gates red first

`check_search.js` had **no assertion at all on the section hits** — a change here could not
have gone red. It gained, on both pages: the painted list for `oghataraṇa`, `nidānavaṇṇanā`,
`vagga` (2,590 rows, 40 drawn) and `abhabbasutta` must equal, row for row, what
**names.json ranks under the page's own rule** (re-stated in the gate: search.html ranks exact
matches, then opening matches, then shorter, then `localeCompare`; reader2 exact then
shorter); `abhabbasutta`, a name in no running text, must still be "Found in the section
titles"; the layer chip must filter the names; `mangalasutta` must find *Maṅgalasutta* only
with the fold switch (0 exact, 5 folded); and the wiring: a `tn/` shard fetched, `names.json`
never. `perf_search.js`'s ceiling dropped from 1.25 MB to **520 KB** (just above the largest
postings shard) — and the dictionary rows, whose `lookup_eval/index.json` is 653 KB on R2,
got their own ceiling of 700 KB, named as an open item in the file rather than hidden under
one loosened number. Red on `e54900ddf`:

    FAIL  wiring: section names come from a tn/ shard
    FAIL  wiring: names.json is not read whole  [fetched names.json]
    FAIL  search wiring: section names come from a tn/ shard
    FAIL  search wiring: names.json is not read whole  [fetched names.json]
    perf: 10 of 11 search/reader rows  FAIL max>0.52MB  (max 1.09)

(the ranking assertions were green on the old path first — which is what shows they state the
pages' rule and not a hoped-for one; runs delivered as `check_search_red_run_2026-09-05_names.txt`
and `perf_search_red_run_2026-09-05_names.txt`.)

## 3. The store: `site/index/tn/`

`pipeline/build_name_shards.py`, run after `build_name_index.py`, from `names.json`:

    site/index/tn/index.json   {cap, nlabels, nrows, mind:2, maxd:8, vols, layers,
                                grams:{name: bytes}}                              12 KB
    site/index/tn/<name>.json  {"labels":[…], "rows":[[li, vol, ord, layer, rowIdx], …]}

A name is a folded n-gram over the **letters** of a label (digits, spaces, punctuation
never enter a name, so a name is always a safe file name), deepened by the following letter
— `_` when the gram ends its run — until under 200 KB: `build_gram_shards.py`'s idiom
unchanged. Each shard carries its labels with **all** their rows, and each row its index in
names.json, so a client that merges several shards restores the file's order exactly.
**890 files, 22.9 MB on disk**; depths 2:200, 3:344, 4:188, 5:81, 6:43, 7:29, 8:5. Seven
`_`-terminal shards exceed the cap — `na_` (labels whose last letters are *-na*, i.e. the
thousands of *-vaṇṇanā*) is 548 KB — and are read only when a query offers nothing cheaper;
none of the gate's queries does. Self-verified: every shard equals the labels containing its
gram, with their rows, in file order; for every gram of every 7th label (272,442 resolutions)
the client's resolution lands on shards whose union holds the label; manifest sizes are file
sizes.

## 4. The client

`searchcore.js names(fq)`: the query is folded, every substring of length 2–8 of each letter
run is a candidate, each resolves as `resolveGram` already did for `tg/` (the shard, else its
children, else the shallowest prefix), the cheapest is fetched and the shards merged into an
object of **names.json's shape** — `{vols, layers, labels, rows}`, rows in file order. The
page's own substring test, layer filter, ranking and drawing then run over it **unchanged**:
the gram narrows, the page decides. A gram no label contains proves the answer empty without a
fetch. `undefined` (no run of two letters, e.g. `1.`, or no manifest — an archive) sends the page
to names.json as before; both pages now start the names fetch **beside** the search instead of
before it.

Checked, not assumed: `pipeline/check_name_shards.js` — 1,712 query × mode combinations
(whole labels, random substrings with and without diacritics, labels minus their number, last
words, tails, one- and two-letter strings, digits, strings no label contains), the page's rule
over `names()`'s output against the same rule over names.json: **0 differences**; 314 fell
back (no gram), 4 proved empty by the manifest, 743 distinct shards read. Kept as a gate.

## 5. After

Same harness; baseline re-recorded with this change, as its rule requires:

| query | req | raw MB | gz MB | max MB | before raw / gz / max |
|---|---:|---:|---:|---:|---|
| cold median word | 20 | 1.22 | 0.33 | 0.22 | 2.28 / 0.57 / 1.09 |
| `tassā` | 85 | 7.96 | 2.03 | 0.34 | 8.99 / 2.26 / 1.09 |
| `nibbana` (no diacritics) | 6 | 0.41 | 0.10 | 0.25 | 1.45 / 0.34 / 1.09 |
| every other search row | +1 | −1.06 | −0.24 | ≤ 0.51 | max was 1.09 |
| reader2 cold word | 20 | 1.22 | 0.33 | 0.22 | 2.28 / 0.57 / 1.09 |

One request more per query (manifest once, then a shard per distinct gram), 0.24 MB gz less on
every cold search, waves 9 → 6 on the cold word. `check_search` green (16 new assertions),
`check_name_shards` green, `check_reader_range` 37/37, `check_archive_fallback` 11/11,
`check_lookup_reach` 12/12, `check_columns` green. `verify_live.py` fetches `tn/index.json`.

## 6. What this does not do

* The seven `_`-terminal shards over the cap (`na_` 548 KB) exceed the 520 KB ceiling if a
  query ever offers nothing cheaper than them (`na` alone, or `-ana` at the end of every run);
  reported here, not hidden — the same shape as `tg/am_`.
* A one-letter query on search.html still reads names.json whole (the fallback): no gram.
* reader2's box searches on every keystroke; as a word is typed, its cheapest gram changes and
  a few shards are read in turn (each ≤ 200 KB, cached per gram). Not measured against a
  typing session; the harness measures whole queries.
* `lookup_eval/index.json`, 653 KB on R2, is now the largest file any page reads — a
  dictionary-store change (`r2_upload.sh` + `WLV`), recorded in `perf_search.js` as an open
  item with its own ceiling.
* Items 2–5 of the third session's list are untouched: phrase positions (measured, not
  built), `*vaggo`'s 23.4 MB of prefix-named postings, `27KhuA08`'s Contents, the release bump.
