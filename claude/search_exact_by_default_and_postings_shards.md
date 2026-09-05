# Search: exact diacritics by default, and a search that no longer downloads the canon

**2026-09-05.** Closes the brief `search_and_dictionary_speed_brief.md` — its §0 (the
correctness decision), §1 (the measurement it said must come first), §6 levers 0, 2, 4 and 5,
and §7 (the harness and baseline). What it does NOT do is at the end.

## 1. What was measured, before anything was changed

The live site loaded in this session's browser pane; the previous session's failure to load it
was that session's tooling, as the brief said.

**Pages gzips in transit.** `performance.getEntriesByType('resource')` after four searches:
every `/index/` response had `encodedBodySize / decodedBodySize` between 0.19 and 0.25 —
`tb/pa.json` 559 KB on the wire for 2.23 MB, `26VsmT02.idx.json` 662 KB for 2.56 MB. Lever 1
of the brief (pre-compression) was already banked and is closed.

**R2 compresses too** (`content-encoding: zstd`, similar ratio). But every `.json` from
`dict.buddha-dhamma.net` came back `cf-cache-status: DYNAMIC` — not edge-cached at all — and
the cold `lookup/index.json` took 801 ms. The `.gz` shards return `MISS`, i.e. cacheable. This is
a Cloudflare cache-rule setting on the R2 custom domain, not repository work; noted, not done.

**The cost of a search was the per-volume `<VOL>.idx.json`, not the buckets.** `tassā` on the
live site fetched 117 of them: about 40 MB compressed, 190 MB parsed, 4.2 s on a fast link.
`paṭisambhidā` (the `pa` bucket the brief worried about) fetched 58 shards, 25 MB compressed;
the bucket itself was 559 KB. Postings and paragraph text lived in the same file and the file
was the unit of fetch.

**A dictionary lookup was a chain six round trips deep**, with small files throughout:
manifest → freq/gloss/forms → eval manifest + ped → form → dpd/lem → ord. About 1.9 s cold.
Bytes were never the dictionary's cost; §4 of the brief was right.

**Baseline, recorded by the new harness before any change** (`pipeline/perf_search.js`, jsdom
through the pages' own code, gzip -6 per file as the wire cost, 40 ms simulated latency per
fetch so dependent round trips show as `waves`):

| query | req | raw MB | gz MB |
|---|---:|---:|---:|
| search.html cold, median word `yamakasālānaṁ` | 19 | 15.3 | 3.5 |
| `paṭisambhidā` | 105 | 106.1 | 25.6 |
| `tassā` (117 volumes) | 124 | 193.5 | 43.3 |
| `dhamm*` | 126 | 195.2 | 43.5 |
| `*vaggo` (k.txt sweep) | 156 | 121.8 | 29.3 |
| `amakasālāna` (substring sweep) | 57 | 55.1 | 13.2 |
| `evaṁ me sutaṁ` | 155 | 176.3 | 40.4 |
| lookup `tathāgato`, cold | 18 | 1.5 | 0.3 (8 waves) |

That file is kept as `pipeline/perf_baseline_2026-09-05_before.json`.

## 2. §0 — exact by default. Gate red first.

`check_search.js` gained assertions whose truth comes from the **corpus text**, not from any
index (the folded index could not know what it had merged): `anīkaratto` (6 occurrences, 2
volumes) and `anikaratto` (3) fold to one key; each must count only itself; the head must name
the mode; the switch must merge them and say so; `tassā` must count 4,322, not 36,644; a miss in
exact mode must offer the switch. On the build then live (`a164a57cc4c3`) the run was:

    FAIL  reader exact: anīkaratto counts only anīkaratto  [want 6/6 | 9 occurrence(s) …]
    FAIL  reader exact: the head names the mode
    FAIL  reader exact: anikaratto counts only anikaratto  [want 3 | 9 occurrence(s) …]
    FAIL  reader: the fold switch exists
    FAIL  search exact: anīkaratto counts only anīkaratto  [want 6/6 | 9 occurrence(s) …]
    FAIL  search exact: the status names the mode
    FAIL  search exact: tassā is not tassa  [want 4322 | 36,644 occurrence(s) …]
    FAIL  search: the fold switch exists
    FAIL  search exact: a no-match offers the fold switch

(full run: `check_search_red_run_2026-09-05.txt`, delivered with the session; 15 FAIL in all,
the other six being the old phrase assertions whose truth was re-expressed in exact terms.)

**What "exact" means.** A key is the printed token: NFC, lower case, the modern ṃ written as
the edition's ṁ (the corpus carries ṁ only; the niggahita toggle is display-only). Nothing else.
Character census over all 118 volumes: inside words, a–z and ā ī ū ṁ ṅ ñ ṇ ṭ ḍ ḷ, nothing
else; `build_search_index.py` now asserts that on every run. 682,010 exact keys against 643,958
folded; **34,134 folded keys (5.3%) were merging two or more printed forms** — and they are the
common words: `tassa`/`tassā`, `evaṁ`/`evam`, `arati` (274 folded, 159 exact).

**The switch.** “Ignore diacritics” (labelled `a = ā` for the first hours, renamed the same day at the reader's request) — a chip beside the layer chips on search.html, a chip in the
dropdown's filter row in reader2. Off by default, remembered in `localStorage['osbct-fold']`
across both pages. Every result line ends `· exact diacritics` or `· diacritics folded`. A
miss in exact mode says `No matches for “patisambhida” (exact diacritics) — fold diacritics
(a = ā) and search again?`; the page never folds on its own. Section names (`names.json`) are
matched in the same mode as the text.

**Folding is resolved on the client from the exact keys**, never stored: a postings shard is
named by the FOLDED prefix, so `tassa` and `tassā` sit in one shard and fold mode reads both
through a per-shard fold map built once; the sweep folds `k.txt` once (the fold is
length-preserving, so offsets carry across to the exact string).

**Fold mode reproduces the old counts exactly** — checked on `tassā` (36,644 / 14,287 / 117),
`paṭisambhidā` (875 / 765 / 58), `evaṁ me sutaṁ` (515 + 168), `*vaggo` (199), `amakasālāna`
(44). One deliberate difference: a wildcard that matches more than 500 forms is now cut to the
**500 commonest** (most paragraphs), deterministically, and the status says so — `dhamm*: the
500 commonest of 3,823 forms`. It used to be cut to the first 500 in bucket order, which was
volume order: `dhamm*` answered 88,895 that way and 4,822 in sorted order. Neither was a total;
now the line does not pretend to be one.

**§7 of the project instructions is revised** — the file is delivered as
`OSBCT_Project_Instructions.md` beside this session's outputs, header comment updated, **paste
into the instructions field still pending** (the knowledge copy is read-only from a session).

## 3. §6 levers 2 and 4, done as one rebuild

`pipeline/build_term_postings.py` (replaces `build_term_buckets.py`; `site/index/tb/` is gone):

    site/index/tp/index.json     manifest: vols, layers, shard names, per-volume chunk starts
    site/index/tp/<name>.json    {terms:{key:{volIdx:[[paraIdx,count],…]}}}, 1,031 shards,
                                 folded-prefix names deepened until ≤ 500 KB raw (the
                                 dictionary's own idiom and `shardName` walk); 70 MB in all
    site/index/tp/k.txt          682,010 keys, 12.5 MB raw, the sweep surface
    site/index/tx/<VOL>/<i>.json 1,008 text chunks, ≈ 96 KB of text each, 105 MB in all

One shard answers a single-word search completely — occurrences, paragraphs, volumes — and
text is fetched only for the rows drawn (or, for a phrase, for the candidates that must be
read to decide adjacency). The per-volume `<VOL>.idx.json` and `terms.compact.json` are
rebuilt with exact keys and STAY: the legacy path (manifest 404 = an unpacked deposit from
before today) and the gates' ground truth. Self-verified: shard union == per-volume postings
byte for byte, every key resolved by the client's walk to the shard holding it, chunks
re-concatenate to every `paras` list.

`site/searchcore.js` is now the **one** implementation; search.html and reader2.html are its
two UIs. The gate inlines it; `stamp_build.py` hashes and versions it; `verify_live.py`
fetches it and the manifest. If the file fails to load the reader still draws — only the box
says so.

**After** (same harness, same rows; `perf_baseline.json` re-recorded with this change, as the
harness's own rules require):

| query | req | raw MB | gz MB | before gz |
|---|---:|---:|---:|---:|
| cold median word | 19 | 2.3 | 0.57 | 3.5 |
| `paṭisambhidā` | 132 | 10.6 | 2.97 | 25.6 |
| `tassā` | 84 | 9.0 | 2.26 | 43.3 |
| `dhamm*` | 48 | 4.9 | 1.31 | 43.5 |
| `*vaggo` | 214 | 36.9 | 9.01 | 29.3 |
| `amakasālāna` | 62 | 17.4 | 3.99 | 13.2 |
| `evaṁ me sutaṁ` | 264 | 24.7 | 5.75 | 40.4 |
| reader2 `tassā` | 45 | 5.3 | 1.35 | 43.3 |

Bytes down 5–30× on every shape except the sweeps, which are bounded by `k.txt` (12.5 MB raw,
2.7 MB gz, once per page load). Requests went UP on three shapes — text chunks are many and
small — so the harness gates bytes and requests separately (≤ +10 % and ≤ +25 %), and the chunk
pool is 16 wide.

## 4. §6 lever 5 — the dictionary chain

`elook('form')` depended on nothing the first tier returned and was started after it; it now
starts beside it, and the pointerdown warm-up fetches all three manifests (edition, eval, hw)
instead of one. Six hops → four, three once the manifests are warm. Harness: cold 8 → 6 waves,
lemma-only word 7 → 4. **No store changed**, so no `r2_upload.sh` run and no `WLV` bump; the
`panel.js?v=` on the script tag is bumped to `20260905a`. `check_lookup_reach.js` 12/12,
`check_apd_gear.js` green.

## 5. What is not done, and why

* **Lever 3, `k.txt`.** Still a 12.5 MB linear scan (2.8 MB on the wire) for substrings and
  `*`-suffixes. Larger than before by the diacritics' UTF-8 bytes. How often real queries take
  it is still unmeasured — there are no query logs. An n-gram set would replace it; not today.
* **Phrase queries read every candidate paragraph.** `evaṁ me sutaṁ` fetched 190 chunks. Positions
  in the postings would let adjacency be decided without text; a bigger store, a later change.
* **R2 edge caching** — a dashboard cache rule, see §1.
* **The instructions paste** — §2 above.
* `27KhuA08`'s ☰ Contents, advisory, from the previous session — untouched.
