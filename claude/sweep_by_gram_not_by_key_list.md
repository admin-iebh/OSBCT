# The sweep reads one n-gram shard, not the whole key list

**2026-09-05, third session.** Closes lever 3 of `search_and_dictionary_speed_brief.md`, the
one `search_exact_by_default_and_postings_shards.md` §5 left open: substring and `*`-suffix
searches downloaded and scanned `k.txt`, every key in the canon.

## 1. Measured before anything changed

`pipeline/perf_search.js` against the baseline of the previous session, unchanged, all within
baseline. The two sweep shapes, with `k.txt` marked by the harness:

| query | req | raw MB | gz MB | of which k.txt |
|---|---:|---:|---:|---:|
| `*vaggo` | 214 | 36.9 | 9.01 | 12.5 raw / 2.7 gz |
| `amakasālāna` | 62 | 17.4 | 3.99 | 12.5 raw / 2.7 gz |

Every other file a search reads is under 515 KB (largest postings shard `maha.json`; largest
text chunk 301 KB). `k.txt` was the one file a phone had to hold whole.

The key list itself: 682,010 keys, mean length 14.6, 136 shorter than three characters. Over
their folded forms there are 2,655 distinct trigrams and 8.4 M (key, trigram) pairs; the
commonest trigram (`ana`) is in 170,230 keys. Storing the keys themselves under every trigram
costs 181 MB on disk — fourteen times `k.txt` — but a query reads ONE of them, and that is the
trade this makes: disk for wire.

## 2. Gates red first

`check_search.js`: the assertion that read "the sweep fetched k.txt" now reads the opposite, on
both pages and both sweep shapes, and the counts are still asserted against the ground truth
of `terms.compact.json` + the per-volume shards. `perf_search.js` gained a column, `max`, the
largest single file a query fetched, gated at an absolute 1.25 MB. Red on `20a4d997e795`:

    FAIL  wiring: the substring sweep does not fetch k.txt  [fetched k.txt]
    FAIL  wiring: the substring sweep fetched an n-gram shard (tg/)
    FAIL  wiring: the *-suffix sweep fetched an n-gram shard (tg/)
    FAIL  search wiring: the *-suffix sweep reads a tg/ shard, not k.txt
    FAIL  search wiring: the substring sweep reads a tg/ shard, not k.txt
    search: suffix wildcard  … max 12.47 MB  FAIL max>1.25MB
    search: substring sweep  … max 12.47 MB  FAIL max>1.25MB

(runs delivered with the session as `check_search_red_run_2026-09-05_lever3.txt` and
`perf_search_red_run_2026-09-05_lever3.txt`).

**Two things the red run taught.** A first ceiling of 1 MB went red on EVERY cold query,
because `index/names.json` — the section names, fetched once per page and scanned on every
search — is 1.09 MB. The ceiling was set just above it and names.json is recorded as an open
item, not hidden by the gate. And `/k\.txt/` matched `tg/ipak.txt`: the regex in all three
scripts is now `/tp\/k\.txt/`. A gate that had matched the wrong file would have reported
"fetched k.txt" on a sweep that never did.

## 3. The store: `site/index/tg/`

`pipeline/build_gram_shards.py`, run after `build_term_postings.py`, from `k.txt`:

    site/index/tg/index.json   {cap, nkeys, mind:2, maxd:8, grams:{name: bytes}}   34 KB
    site/index/tg/<name>.txt   the exact keys whose FOLDED form contains <name>, sorted

A name is a folded n-gram, starting at bigrams and deepened — by the character that FOLLOWS the
gram in each key, `_` when the gram ends the key — until the shard is under 500 KB. That is the
postings shards' idiom (deepen a prefix until it fits, pad with `_`) applied to infixes: `vag`
may not exist, but `vaga` … `vagg` … `vag_` do, and their union is exactly the keys containing
`vag`. 2,841 files, 197.7 MB; depths 2:254, 3:1106, 4:1104, 5:337, 6:40. Twelve shards exceed
the cap because a `_`-terminal shard cannot be deepened — `am_` (keys ending in *-aṁ*) is
2.35 MB, `ti_` 1.85 — and a shard like that is read only when the query offers nothing cheaper.

Self-verified in the builder: every shard equals the keys containing its gram, computed
key-by-key from each key's own substrings; for every gram of every 97th key (526,272 of them)
the client's resolution lands on shards whose union holds the key; manifest sizes are file
sizes.

## 4. The client: the gram narrows, the verification decides

`searchcore.js`, `sweep(frags, terminal, test)`: the query's literal fragments are folded and
every substring of length 2–8 is a candidate gram — plus `gram_` for the tail of a terminal
fragment, so `*vaggo` can reach the keys that END in `ggo`. Each resolves to the shard of that
name, else its children (every name extending it), else the shallowest name prefixing it; the
manifest gives each a byte total and the cheapest wins. Its shard(s) are fetched, every key is
tested by the same substring or pattern in the mode's view (exact or folded) that the `k.txt`
scan used, the survivors are sorted, capped at 500 with `matched` the full count.

So the result is what `k.txt` produced — same keys, same order, same cap, same total — and
that was checked, not assumed: 928 query × mode combinations (random substrings, suffixes,
`a*xyz`, `*abc*`, drawn from real keys, plus the edge shapes) through `searchcore.js` with
`tg/` present and with it hidden, **0 differences**. The one query that still reads `k.txt` is
the one with no gram at all (`a*b*c`): `k.txt` stays for that and for the archive — the
manifest missing is a fallback, and `verify_live.py` now fetches `tg/index.json` so that on the
live site it is never a silent one.

## 5. After

Same harness, baseline re-recorded (the harness's own rule when a change is meant to move it):

| query | req | raw MB | gz MB | max MB | before gz |
|---|---:|---:|---:|---:|---:|
| `*vaggo` | 215 | 24.5 | 6.36 | 1.09 | 9.01 |
| `amakasālāna` | 63 | 4.97 | 1.35 | 1.09 | 3.99 |
| everything else | unchanged | | | 1.09 | |

One request more on each (the `tg/` manifest, fetched lazily on the first sweep; the cold path
is untouched). `check_search` green, `check_reader_range` 37/37, `check_archive_fallback`,
`check_lookup_reach` 12/12, `check_columns` green.

## 6. What this does not do

* **`*vaggo` is still 24.5 MB raw.** The 12.5 MB of `k.txt` is gone; what remains is the
  POSTINGS of its 199 keys, which lie in ~150 different prefix-named shards of up to 500 KB.
  Postings named by prefix serve a suffix query badly by construction. A suffix-named postings
  set would be a second 70 MB store; not proposed until real queries are shown to take this
  shape (there are still no logs).
* **`index/names.json` is 1.09 MB**, read whole on every page load of either search UI. Found
  by the new gate; not changed here.
* **Phrase searches** still read every candidate paragraph (`evaṁ me sutaṁ`: 190 chunks) —
  item 2 of the previous session, unchanged.
* **Deploy file count:** `git ls-files site/` grows by 2,842 to ~6,744. The Pages clock note in
  `deploy-pages.yml` applies; 3,902 deployed without incident, 6,744 has not been tried.
