# The deploy is near a ceiling, and there are three ways off it

**Written 2026-08-06, after a day in which the site failed to publish eight times.**
Nothing here is built. This exists so the decision is made once, on the numbers,
rather than re-derived under pressure the next time a deploy fails.

> **CORRECTED 2026-08-07 from `_xc/reshard/PILOT.md`, which measured what this document
> asserted. Three of its numbers were wrong and one of its options is not implementable as
> described. The corrections are marked inline and the original wording is kept beside
> them, per working principle 3 — the record is not overwritten.**
>
> **The recommendation in §6 was reached on those numbers and is therefore SUSPENDED, not
> merely amended. It must be re-decided, not inherited.** A fourth option that neither §2a
> nor §6 considered is added as §5a.
>
> In short: the shards are not 4% full, they are 10–22% full; §3's lever does not exist;
> the failure list in §1 conflates three unrelated causes; and the 1 GB size cap that
> `9afc115` blamed was never real. Read `_xc/reshard/PILOT.md` before acting on any part
> of this file.

## 1. What actually happens

Every push republishes the **whole** site — 26,576 files, a 216 MB artifact — regardless
of how many files changed. `actions/deploy-pages` then waits for GitHub to finish
publishing them and gives up after **600,000 ms**.

**That ten minutes is a maximum, not a default.** Setting `timeout: 1800000` was tried at
`14f16795`; run #113 answered in its own annotations:

```
Warning: timeout value is greater than the allowed maximum
         - timeout set to the maximum of 600000 milliseconds.
Timeout reached, aborting!
```

So the clock cannot be moved. The artifact is not the problem either — #113 uploaded
`github-pages`, 216 MB, successfully. What runs out of time is GitHub publishing the
file **count**.

**And the site did not change.** The tree that failed at 11m41s is the same 26,576 files,
8 files different in total, that published in **1m52s** the evening before. Measured
against `440b795`: 0 files added. What varies is GitHub's throughput on a given day, and
this site sits so close to the ceiling that their variance decides each run.

Observed on this repository:

| run | | duration |
|---|---|---:|
| #105, #107, #108 | ok | ~2m |
| #110 | FAIL | 11m41s |
| #111 | ok | 9m36s |
| #112, #113, #114 | FAIL | ~11m40s |

### 1a. CORRECTION — this list is three different failures, not one

**As written, every `FAIL` above is offered as evidence for one cause: the clock. At least
three unrelated causes are being counted together, and this table is the evidence base for
§6's recommendation.** Sorted by what actually happened:

| cause | how it shows | what fixes it |
|---|---|---|
| **the ten-minute publish ceiling** | `Timeout reached, aborting!` at ~11m40s | fewer files — §3, §4, §5, §5a |
| **runner never acquired the job** | `The job was not acquired by Runner of type hosted even after multiple attempts`; **no artifact produced**; #120, 15m10s | nothing local. Start a new run |
| **a pending deployment holding the environment** | a deployment stuck at *Ready to deploy*, `Active`, for 18 hours (#121); every later run dies in seconds (#122, 30s) | cancel the stuck run, then one fresh run |
| **the 1 GB Pages size cap** | ~~`9afc115`: "site/ is 1.62 GB against a 1 GB limit"~~ | **NOTHING — IT WAS NEVER REAL.** See below |

**The 1 GB cap was a misdiagnosis and `deploy-pages.yml` already records the retraction:**
the 1.62 GB was the **local working tree**, which carries untracked build output. What CI
checks out is **833 MB in 26,576 files**, re-measured independently on 2026-08-07
(`git ls-files site/` for the count, `stat` over that list for the bytes). The prune step
added on that premise was removed. **Do not reintroduce it, and do not treat bytes as the
constraint.** `site/lookup_eval/dpd/*.json` is gitignored and only the `.gz` is tracked;
measuring the working tree counts 11,229 files and ~360 MB that are never deployed.

**And the site publishes fine when GitHub is healthy.** Measured 2026-08-06/07 on an
essentially unchanged tree: #115 1m43s ok, #117 13m37s ok, #119 5m33s ok, **#123 2m05s
ok**. The variance is real and this document's own reading of it — "a race, not a fault" —
is confirmed from the healthy side. **That does not make resharding unnecessary; it does
mean the site is not in danger this week, and the decision below can be made carefully
rather than under pressure.**

**Two traps found the hard way.** `cancel-in-progress: true` cancelled a deploy in flight
(#109, at 5m34s) — changed to `false` at `162e66d7`, because cancelling a Pages deployment
mid-publish is a bad idea whatever else is true. And **re-running a failed job adds a
second artifact of the same name to the same run**; four retries produced
`Multiple artifacts named "github-pages" ... Artifact count is 4`, which is unrecoverable
for that run. **Never use "Re-run failed jobs" on this workflow — start a new run**
(`workflow_dispatch` is enabled).

## 2. Where the files are

| store | files | MB | avg shard |
|---|---:|---:|---:|
| `lookup_eval/dpd` | 11,229 | 42 | **3.8 KB** |
| `lookup_eval/lem` | 5,244 | 163 | 31.9 KB |
| `lookup/gloss` | 4,403 | 94 | 21.9 KB |
| `lookup/freq` | 1,342 | 21 | 16.2 KB |
| `lookup/wn` | 1,068 | 15 | 14.2 KB |
| `lookup_eval/form`, `lookup/ped`, `lookup/forms` | 1,311 | 24 | ~19 KB |
| **the dictionary stores** | **24,597** | **~360** | |
| everything else — reader, index, 118 volumes | **1,979** | ~473 | |

~~**93% of the files are dictionary shards, and they are far smaller than they are allowed
to be.** The cap is `cap_bytes: 150000`; the DPD shards average **3.8 KB** and 94% are
under 10 KB. They are numerous because the adaptive prefix splits much more finely than
the cap requires, not because they are full.~~

### 2b. CORRECTION — 3.8 KB is the GZIPPED size, and the cap is on the uncompressed JSON

**The paragraph above is struck through because both of its claims are wrong, and the
recommendation in §6 rests on them.**

DPD is published gzipped and only gzipped — 11,229 `.json.gz` totalling **42 MB**, which
is where "11,229 files, 42 MB, 3.8 KB" comes from. `cap_bytes: 150000` is a ceiling on the
**uncompressed** JSON that the panel inflates and parses. Uncompressed, those same shards
are **379 MB — about 33 KB each.** Comparing a compressed average against an uncompressed
cap overstates the headroom by roughly nine times.

Measured uncompressed averages (`_xc/reshard/PILOT.md` §2):

| store | shards | avg **uncompressed** | % of the 150 KB cap |
|---|---:|---:|---:|
| `dpd` | 11,229 | **33 KB** | 22% |
| `lem` | 4,954 | 31 KB | 21% |
| `gloss` | 4,103 | 24 KB | 16% |
| `form` | 806 | 23 KB | 15% |
| `freq` | 1,342 | 19 KB | 13% |
| `wn` | 1,067 | 15 KB | 10% |

**Not 4% full. Ten to twenty-two per cent full.** The second claim fails with the first:
the shards are not numerous because the prefix "splits much more finely than the cap
requires" — see §3a, it splits exactly when the cap requires and never otherwise.

The file *count* in this section is correct and was re-verified: `git ls-files site/` is
**26,576**.

## 2a. The two questions, which are not the same question

An earlier draft of this listed three *places* to move the files — R2, jsDelivr, a second
Cloudflare Pages project — and then three *options* A/B/C in which A was resharding. That
conflated two different decisions and is worth separating once:

| | question | answers |
|---|---|---|
| **Do we move the files at all?** | | **A** stays on GitHub Pages and makes fewer files |
| **If we move them, where to?** | | **B** Cloudflare R2 · **C** jsDelivr |

**Resharding is not a hosting choice.** It changes nothing about where anything lives; it
merges tiny shards into fewer, larger ones so GitHub Pages has less to publish.

**A second Cloudflare Pages project is not on the list** because it fails on arrival: the
free plan caps at **20,000 files** and the dictionary stores alone are 24,433. It would
need resharding first, at which point resharding has already solved the problem.

## 3. Option A — reshard into fewer, larger files

~~Raise the effective shard size in `_panel/build_lookup.py` and `_panel/build_eval.py` and
rebuild both stores. The panel resolves shards through the manifest, so larger shards are
invisible to it: no reader change at all.~~

| ~~target shard~~ | ~~dictionary files~~ | ~~whole site~~ |
|---|---:|---:|
| now | 24,597 | 26,576 |
| ~~64 KB~~ | ~~**5,747**~~ | ~~**~7,700**~~ |
| ~~150 KB (the existing cap)~~ | ~~**2,452**~~ | ~~**~4,400**~~ |

### 3a. CORRECTION — there is no such knob, and the projected counts do not hold

**"Raise the effective shard size" describes a lever that does not exist.** `CAP` is a
ceiling, not a target, and `shard_table` never merges — it starts at prefix depth 2 and
only ever splits *deeper*:

```python
assign, work = {}, [(2, list(keys_bytes.items()))]     # starts at depth 2
...
if total > CAP and len(gi) > 1:
    work.append((depth + 1, gi))                       # only ever splits DEEPER
```

The floor is **depth 2**: every distinct two-character folded prefix gets its own file
however small it is. **That minimum granularity is what produces the file count** — not
over-splitting against the cap. Raising `CAP` merges nothing, because nothing is merged in
the first place.

Simulated (`_xc/reshard/PILOT.md` §3) — merging every depth-2 shard up to depth 1 wherever
the total fits:

| store | now | depth-1 @150 KB | depth-1 @64 KB |
|---|---:|---:|---:|
| `dpd` | 11,229 | **11,229** | 11,229 |
| `lem` | 4,954 | **4,954** | 4,954 |
| `gloss` | 4,103 | 4,084 | 4,084 |
| `freq` | 1,342 | **1,342** | 1,342 |
| `wn` | 1,067 | 1,007 | 1,025 |
| `ped` | 296 | 224 | 267 |
| `forms` | 209 | 110 | 135 |

**Essentially nothing.** Every first-character group in the large stores is far over any
cap and re-splits immediately; only the small stores shrink, and they were never the
problem. **The struck-through "~7,700 files at 64 KB" was computed from the compressed
average of §2 and does not survive its correction.**

**Option A is not closed — it is re-priced.** Fewer files requires *a different grouping*:
pack keys into cap-sized buckets and let `index.json` name them, instead of deriving the
shard name from a prefix. That changes the shard-naming contract, which `panel.js`
implements on the client (`shard_key`: "the shortest prefix of `fold(form)`, padded with
`_`, that names a shard in this manifest; try depth 2 upward"). **Builder and reader must
change together and be verified as one change**, with `check_lookup_reach.js` as the
control. That is a materially larger job than "raise a constant and rebuild".

**One prerequisite, and it is cheap:** the overflow promotion in `write_shards` is not
deterministic — it re-probes up to 200 times and picks by `max()` over a set. A rebuild of
`gloss` from unchanged inputs reproduced 179,985 of 180,025 keys byte-identically and
differed on 40 **solely** in which keys were promoted to overflow files. Pin that order
before any reshard, or every old-against-new verification carries noise that cannot be
told from a regression.

**What the pilot did establish, and it is good news:** `build_lookup.py` still reproduces
its own shipped output. Identical key set, no text differences. **Resharding is a
resharding job, not a migration** — unlike the corpus case in `_xc/hy2/FINDINGS.md` §7.
`ped` and `forms` remain untested because `DPD_DIR` and `PCED_DIR` point at scratch paths
that do not exist in the repo; the PCED data is present in `_dictsrc/` in another form.

**The trade nobody should skip: bigger shards mean each word lookup downloads more.**
A DPD lookup today pulls ~3.8 KB. At the 150 KB cap it could pull 150 KB. That is a real
regression in panel latency on a slow connection, paid on every lookup, to fix a problem
that appears on every deploy. **64 KB is the more honest target** — a 4× file reduction
for a bounded 64 KB worst case — and the number should be chosen by measuring, not
assumed.

- **for:** one origin, no third party, no CORS, no DNS, nothing new to keep alive; reversible, since the old stores are in git history
- **against:** rebuilds shipped data; every key must be proved still reachable; costs panel bandwidth
- **already have:** `pipeline/check_lookup_reach.js` drives the real search box, and a key-by-key diff of old against new stores is straightforward

## 4. Option B — move the stores to Cloudflare R2

Put `lookup/` and `lookup_eval/` in an R2 bucket behind a custom domain (say
`dict.buddha-dhamma.net`) and point `BASE` and `EBASE` in `panel.js` at it. Pages then
publishes ~2,000 files in seconds, permanently.

- **for:** the deploy problem disappears rather than shrinks; no file-count limit; free egress; an R2 bucket is already mentioned in `site/DEPLOY.md` for the PDFs, so the account exists; the shards stay small, so panel latency is untouched
- **against:** a second origin is a second thing that can fail, and a second thing to keep alive for as long as the site lasts; CORS must be right or every fetch fails; the corpus and its dictionaries stop being one deployable unit
- **watch:** `jfetch` sniffs the gzip magic bytes because a host may or may not set
  `Content-Encoding: gzip`, and localhost never does. That path must be tested against the
  real bucket, not a local server.

**Cost of the extra origin, honestly:** one DNS lookup and TLS handshake on the first
lookup of a session, roughly 50–200 ms, once. After that the connection is reused and
per-shard latency is comparable — both are CDNs, the shards are kilobytes, and latency
dominates transfer. It may even be faster, depending on edge coverage.

## 5. Option C — jsDelivr over the existing repository

`https://cdn.jsdelivr.net/gh/admin-iebh/OSBCT@<tag>/site/lookup/…`. Nothing to host,
nothing to upload, the files stay exactly where they are.

- **for:** working the same afternoon; no infrastructure; free
- **against:** a scholarly corpus meant to outlast its tooling acquires a dependency on a
  third party's free tier; needs a tag pinned and bumped when the stores change; if it is
  down the dictionary tabs go empty

## 5a. Option D — RELOCATE the stores out of `site/`, and keep them in the repo

**Added 2026-08-07. Neither §2a nor §6 considered it, and it changes the shape of the
choice.**

The workflow publishes one path and nothing else:

```yaml
- name: Upload site/ as the Pages artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: ./site
```

So moving `lookup/` and `lookup_eval/` **out of `site/`** — to `stores/` in the same
repository — removes ~24,600 files from the Pages artifact **without deleting them from the
project**. Pages drops to roughly 2,000 files. The stores are then served from wherever
§4 or §5 decides, and the repo keeps the authoritative copy.

**Why this matters more than it first appears: the deposits.** The stores are tracked, so
they are inside the Zenodo deposit that carries the DOI. Move them to a bucket *instead* of
the repo and a future reader holding only the archived deposit gets the corpus and a reader
whose dictionary panel is empty — silently, and years later. **For a corpus whose stated
purpose is to outlast its tooling, that is a real loss and an invisible one.** Relocation
inside the repo preserves it; migration out of the repo does not.

**Relocation is not a hosting choice either.** It is orthogonal to §4 and §5: it decides
what Pages *publishes*, not what the reader *fetches*. The two questions compose —

| | |
|---|---|
| stores in `site/`, served from Pages | today. 26,576 files, the clock is a race |
| stores in `stores/`, served from R2 | Pages ~2,000 files; archived in the deposit; one new origin |
| stores in `stores/`, served from jsDelivr | Pages ~2,000 files; archived; no account, third-party tier |
| stores merged and left in `site/` | Option A alone; see §3a for its true cost |

**The trial costs nothing and requires no migration**, which is the strongest practical
point in favour of settling this soon. The whole switch is two constants in
`site/reader/panel.js`:

```js
var BASE  = '../lookup/';
var EBASE = '../lookup_eval/';
```

Point them at a bucket with every file left exactly where it is, and revert by editing two
lines. **Files are only removed from `site/` once the new origin is proven.**

**What a trial must actually test**, because it is where one would fail: `jfetch` sniffs
gzip magic bytes since a host may or may not set `Content-Encoding: gzip`, and localhost
never does. **Test against the real bucket, not a local server.**

## 6. Recommendation — SUSPENDED, and to be re-decided

> **This recommendation was reached on §2's "4% full" and §3's "~7,700 files at 64 KB".
> Both are corrected above; neither survives. The reasoning is kept verbatim below because
> it is the record of how the choice was made, but it must NOT be acted on as it stands.**
>
> **What has changed for the decision:**
> - Option A is not a parameter change but a new grouping plus a matching change to the
>   client's shard-naming contract (§3a). It costs more than this section assumed.
> - Its stated benefit — a 4× file reduction — was computed from a compressed average and
>   is unquantified until the new grouping is designed.
> - The 1 GB byte pressure that appeared to strengthen the case for moving files **was
>   never real** (§1a). Bytes are not a constraint; the file count is.
> - **Option D (§5a) did not exist when this was written**, and it addresses the file count
>   while keeping the stores inside the citable deposit.
> - The site publishes in ~2 minutes when GitHub is healthy (#123). There is time to decide
>   properly.
>
> **Re-decide across A / B / C / D on the corrected figures. Do not inherit the conclusion
> below.**

~~**Reshard.** It is the only one of the three that removes a dependency instead of adding
one, and it fixes the cause — 93% of the files are shards that are 4% full — rather than
relocating it.~~ It needs no account, no domain, no CORS, and nothing that has to still
exist in ten years. It is reversible from git history, and the gate that proves it
(`check_lookup_reach.js`, driving the real search box) already exists.

~~Target **64 KB**, not the 150 KB cap: ~7,700 files, a bounded 64 KB worst case per lookup,
and measure the panel before and after rather than trusting the arithmetic.~~

~~**If 7,700 files still does not publish inside ten minutes, go to B.** R2 is the right
second choice because the bucket is the project's own; jsDelivr is the right choice only
if the site must work this afternoon and nothing else will do.~~

**Do not do nothing.** Re-running works and is not a plan: the site is one bad day at
GitHub away from being unpublishable, and the failure is silent to a reader — the domain
keeps serving the previous build with no sign anything is wrong.

*(That last paragraph stands, and is the one part of §6 the corrections strengthen rather
than undermine — with the amendment that a bad day at GitHub now has three known shapes,
not one: the clock, an unacquired runner, and a pending deployment that holds the
environment until it is cancelled. Only the first is a file-count problem.)*
