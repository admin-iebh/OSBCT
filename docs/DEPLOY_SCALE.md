# The deploy is near a ceiling, and there are three ways off it

**Written 2026-08-06, after a day in which the site failed to publish eight times.**
Nothing here is built. This exists so the decision is made once, on the numbers,
rather than re-derived under pressure the next time a deploy fails.

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

**93% of the files are dictionary shards, and they are far smaller than they are allowed
to be.** The cap is `cap_bytes: 150000`; the DPD shards average **3.8 KB** and 94% are
under 10 KB. They are numerous because the adaptive prefix splits much more finely than
the cap requires, not because they are full.

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

Raise the effective shard size in `_panel/build_lookup.py` and `_panel/build_eval.py` and
rebuild both stores. The panel resolves shards through the manifest, so larger shards are
invisible to it: no reader change at all.

| target shard | dictionary files | whole site |
|---|---:|---:|
| now | 24,597 | 26,576 |
| 64 KB | **5,747** | **~7,700** |
| 150 KB (the existing cap) | **2,452** | **~4,400** |

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

## 6. Recommendation — Option A, then B if it is not enough

**Reshard.** It is the only one of the three that removes a dependency instead of adding
one, and it fixes the cause — 93% of the files are shards that are 4% full — rather than
relocating it. It needs no account, no domain, no CORS, and nothing that has to still
exist in ten years. It is reversible from git history, and the gate that proves it
(`check_lookup_reach.js`, driving the real search box) already exists.

Target **64 KB**, not the 150 KB cap: ~7,700 files, a bounded 64 KB worst case per lookup,
and measure the panel before and after rather than trusting the arithmetic.

**If 7,700 files still does not publish inside ten minutes, go to B.** R2 is the right
second choice because the bucket is the project's own; jsDelivr is the right choice only
if the site must work this afternoon and nothing else will do.

**Do not do nothing.** Re-running works and is not a plan: the site is one bad day at
GitHub away from being unpublishable, and the failure is silent to a reader — the domain
keeps serving the previous build with no sign anything is wrong.
