# Resharding pilot — 2026-08-06

Run at the reader's instruction, to convert "how long would resharding take" from a guess
into a number. **Nothing written to `site/`. No store rebuilt in place.** The one rebuild
was into `/tmp/pilot/out/` and compared against what is shipped.

---

## 1. The gate: does `build_lookup.py` still reproduce the shipped store? — YES for `gloss`

`_gloss/by_volume/` and `_vocab/freq/` are present, so the `gloss` store can be rebuilt
from its real inputs. It was, into a scratch directory, and compared key by key.

| | |
|---|---:|
| shipped keys | **180,025** |
| rebuilt keys | **180,025** |
| only in shipped / only in rebuilt | **0 / 0** |
| common keys **byte-identical** | **179,985 (99.98%)** |
| common keys differing | **40** |

**All 40 differences are the same kind, and none of them is text.** In each, the rebuild
promoted the key to an overflow file and the shipped store keeps its rows inline —
`bhante`, `bhikkhū`, `yo`, `vuttan`, `tesaṁ` and 35 others. Shipped holds the rows; rebuilt
holds the marker `{"big":257,"pages":3}` and writes the rows to `gloss/big/`.

Visible in the file counts: shipped 4,103 shards + 300 overflow; rebuilt 3,976 + 379.

**This is the opposite of the corpus result in `FINDINGS.md` §7.** The panel build
reproduces its own output. Resharding is a resharding job, not a migration.

### 1.1 But the overflow promotion is not deterministic, and that must be pinned first

The `allow_big` loop in `write_shards` re-probes up to 200 times, and picks the key to
promote with `max(...)` over a set. Same inputs, different run, different 40 keys is the
likely explanation, and it means **an old-against-new diff will always carry this noise** —
which makes it impossible to tell a real regression from it. Pin the promotion order
(sort the candidate set) **before** any reshard, or every verification afterwards is
ambiguous.

### 1.2 Two of the four stores cannot be rebuilt here

`build_lookup.py` reads:

```
DPD_DIR  = /mnt/user-data/uploads/GoldenDict/dpd      NOT PRESENT
PCED_DIR = <repo>/../src/pced/dictionary              NOT PRESENT
```

Both are scratch-environment paths — the hazard `pipeline/README.md` records, arriving in
`_panel/` as well. So `ped` and `forms` were not tested. The PCED data is in the repo, in
`_dictsrc/` (`pced_full.jsonl.gz`, `pced_books.json`, `pced_part.aa`/`.ab`, 117 MB), in a
different form from what the script expects. **Recoverable, not lost, and not yet done.**

---

## 2. `DEPLOY_SCALE.md` is right about the file count and wrong about how full the shards are

The document's headline is confirmed: **`git ls-files site/` = 26,576**, exactly as stated.
The 39,538 files on disk are not a contradiction — 11,229 of the excess are the untracked
DPD `.json` originals that `.gitignore` deliberately keeps locally so a rebuild need not
start from nothing. They are not deployed. *(This was measured as a discrepancy first and
retracted on checking `git ls-files`; recorded here so it is not rediscovered.)*

**What is wrong is §2's "avg shard 3.8 KB".** That figure is the **gzipped** size —
11,229 DPD shards, 42 MB of `.json.gz`. The `cap_bytes: 150000` it is compared against is a
cap on the **uncompressed** JSON, and uncompressed those same shards are **379 MB, ~33 KB
each**. So the claim "93% of the files are dictionary shards, and they are far smaller than
they are allowed to be … 4% full" overstates the headroom by roughly nine times. Measured
uncompressed averages: `dpd` 33 KB, `lem` 31 KB, `gloss` 24 KB, `form` 23 KB, `freq` 19 KB,
`wn` 15 KB — against a 150 KB cap, so 10–22% full, not 4%.

---

## 3. The bigger problem: §3's plan is not implementable as written

§3 says "raise the effective shard size in `_panel/build_lookup.py` and
`_panel/build_eval.py`". **There is no such knob.** `CAP = 150_000` is a ceiling, and
`shard_table` never merges:

```python
assign, work = {}, [(2, list(keys_bytes.items()))]     # starts at depth 2
...
if total > CAP and len(gi) > 1:
    work.append((depth + 1, gi))                       # only ever splits DEEPER
```

The floor is **depth 2**: every distinct two-character folded prefix gets its own file
however small it is. That minimum granularity is what produces the file count — not
over-splitting against the cap, which is what §2 assumed. Raising CAP merges nothing.

**Simulated** — merging every depth-2 shard up to depth 1 wherever the total fits:

| store | now | depth-1 @150 KB | depth-1 @64 KB |
|---|---:|---:|---:|
| `dpd` | 11,229 | **11,229** | 11,229 |
| `lem` | 4,954 | **4,954** | 4,954 |
| `gloss` | 4,103 | **4,084** | 4,084 |
| `freq` | 1,342 | **1,342** | 1,342 |
| `wn` | 1,067 | 1,007 | 1,025 |
| `ped` | 296 | 224 | 267 |
| `forms` | 209 | 110 | 135 |

**Essentially nothing.** Every first-character group in the large stores is far over any
cap, so it re-splits immediately. The stores that shrink are the small ones that were never
the problem.

**So fewer files requires a different grouping, not a different parameter** — pack keys
into cap-sized buckets and let `index.json` name them, instead of deriving the shard name
from a prefix. That is a change to the shard-naming contract, which `panel.js` implements
on the client (`shard_key`: "the shortest prefix of `fold(form)`, padded with `_`, that
names a shard in this manifest; try depth 2 upward"). Reader and builder must change
together, and `check_lookup_reach.js` is the control.

**§3's estimate of ~7,700 files at a 64 KB target does not survive this.** It was computed
from the 3.8 KB average, which is the compressed one.

---

## 4. So: how long

- **The gate is passed** for `gloss`, which was the risk. Not a migration.
- **`ped`/`forms` reproducibility is untested** and needs `_dictsrc/` wired into
  `build_lookup.py` first. Small, unblocked, not done.
- **The reshard itself is bigger than §3 implies**: not a constant, but a new grouping plus
  the matching change in `panel.js`, verified by `check_lookup_reach.js` and a key-by-key
  old-against-new diff — with the overflow promotion pinned first (§1.1) so that diff means
  anything.
- **Before any of it, `DEPLOY_SCALE.md` §2 and §3 need correcting**, because the option was
  recommended on a number that is off by ~9×, and Option B (R2) was rejected against it.
  **The recommendation may not survive the correction. Re-decide, don't inherit.**

Nothing here says resharding is wrong. It says the arithmetic it was chosen on was wrong,
and the choice should be made again on these numbers.
