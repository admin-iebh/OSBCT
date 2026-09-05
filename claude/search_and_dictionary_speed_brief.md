# Making search and the dictionary faster — the brief, and what is NOT yet known

**Written 2026-09-05, and ACTED ON the same day** — see
`search_exact_by_default_and_postings_shards.md` for what was measured (§1 is
answered: Pages and R2 both compress in transit; the cost was the per-volume
shards, 43 MB for one common word), what shipped (§0, levers 0/2/4/5, the
harness and baseline of §7) and what was left (lever 3, `k.txt`). The text
below is kept as written, as the record of the question.

Everything here marked *measured* was measured on the
repo. **The one measurement that decides the whole shape of this work was NOT
taken** — see §1. Do not start optimising before taking it.

---

## 0. A CORRECTNESS DECISION THAT ARRIVED WITH THIS BRIEF, AND IT REVISES A STATED PRINCIPLE

**Reader, 2026-09-05:** *diacritic-insensitive search is a problem, because in
Pāḷi `tassa` and `tassā` are different words. There should be a switch for it,
and the default should be WITH diacritics.*

**This revises §7 of the project instructions**, which currently reads
"**diacritic-insensitive** matching so that `nibbana` finds *nibbāna* (essential
for usability)". That sentence made folding the default. The reader is now
saying the opposite: fold on request, never by default.

**Do not treat this as a preference to be balanced against the old sentence.** It
is the reader correcting a design decision on grounds of the language itself —
`tassa` (genitive/dative masculine) and `tassā` (feminine) are distinct forms,
and a search that silently merges them is reporting occurrences that are not
there. That is principle 4, provenance, reaching the search box: the reader must
be able to tell what they actually asked for.

**Three things follow, and the third is the one that will be forgotten:**

1. **Exact-by-default, fold behind a switch.** The switch state has to be
   visible in the result header, not just in a toggle somewhere — a count is
   meaningless if you cannot tell which question produced it.
2. **`§7` of the project instructions must be edited to match**, or the next
   session reads the old sentence and undoes this. The instructions file is the
   source; the deployed copy is a paste of it. **Change the source, then paste.**
3. **It probably makes search FASTER, not slower**, which is why it belongs in
   this brief rather than in a separate one. Folding widens the candidate set:
   every accented key has to be reachable from an unaccented query, which is
   part of why the sweep surface in §3 exists at all. An exact-first default
   should hit the bucket directly and never reach `k.txt`. **Measure this rather
   than assuming it — but measure it as part of the same work, because doing the
   perf work first and the diacritics change second would mean tuning a path
   that is about to change shape.**

---

## 1. THE MEASUREMENT THAT COMES FIRST, AND WHY NOTHING SHOULD PRECEDE IT

**Is the site already compressed over the wire?**

Nothing under `site/index/` is pre-compressed — there are zero `.gz` files there,
and `.github/workflows/deploy-pages.yml` has no compression step. So every byte
below is a *raw* byte, and the answer to "is search slow because of bytes"
depends entirely on whether GitHub Pages is gzipping these responses in transit.

Measured gzip ratios on the actual files:

| file | raw | gzip -6 | ratio |
|---|---:|---:|---:|
| `tb/pa.json` | 2,227,857 | 535,497 | 24% |
| `tb/k.txt` | 10,196,318 | 2,267,255 | 22% |
| `12Sam01.idx.json` | 1,489,001 | 278,878 | 19% |

**If Pages is NOT compressing**, there is a 4–5× transfer win sitting there and
the work is mostly "get compression on". **If it IS compressing**, that win is
already banked, the bytes are a quarter of what the table says, and the real cost
is elsewhere — parse time, round trips, or the sweep in §3. *These are two
completely different projects.* Deciding between them by reasoning is exactly the
mistake this project keeps recording.

**How to take it.** Open the live reader, run a search, and read
`performance.getEntriesByType('resource')` for the `/index/` requests:
`transferSize` vs `decodedBodySize` vs `duration`. `transferSize` ≈
`decodedBodySize` means no compression. Do it for the dictionary panel too — that
is served from **R2, not Pages**, so it is a separate answer and must be measured
separately.

**A session tried and failed to take this on 2026-09-05**: the live site would
not load in either available browser pane. Do not treat that as evidence about
the site; it is evidence about that session's tooling.

---

## 2. What the search actually fetches — *measured on the repo*

The 22 MB `terms.compact.json` is **no longer** the first-search price; that was
fixed 2026-08-09 and the file is kept only as the legacy fallback and as the
gates' ground truth. The live path is the bucketed index:

* `tb/meta.json` — **3.5 KB**, fetched once. Fine.
* **274 postings buckets**, 22 MB total. **Median 5.6 KB** — but savagely
  lopsided:

      top 1 bucket  = 10.1% of all bucket bytes   (pa.json, 2.2 MB)
      top 5         = 31.3%                        (sa.json 2.1 MB, …)
      top 10        = 43.7%
      top 50        = 84.1%

  So a search for a word beginning `pa` or `sa` — which in Pāḷi is a great many
  of them — pulls megabytes, while the median search pulls almost nothing. **Any
  average here is a lie; the distribution is the finding.**
* `<vol>.idx.json` to render hits — **mean 1.6 MB, largest 2.5 MB**
  (`26VsmT02`), 194 MB across 118 volumes. Fetched per volume a hit lands in.

## 3. `k.txt` — 10.2 MB, and it is NOT only for wildcards

`tb/k.txt` is every key in one newline-joined string, scanned with `indexOf` and
never parsed. It is fetched by `tbSweepSub` and `tbSweepRx`.

**Read `tbSweepSub`'s trigger carefully before assuming this is a wildcard-only
cost.** A plain word that is *not present as an exact key in its bucket* and is
≥3 characters falls through to the substring sweep — which is the documented
behaviour ("a bare word also matches inside longer words"), and it means an
ordinary search can pull 10.2 MB. **Measure how often a real query takes that
path** before designing around it. If it is common, this is the single biggest
item in the whole brief.

## 4. The dictionary side is in better shape — check before touching

`panel.js` already: shards under a **150 kB cap**, requests `.gz` explicitly, and
**sniffs the body** rather than trusting the URL, because a `.gz` can arrive
either opaque or already inflated depending on the host. `hw` is 191,928 keys.

So the likely wins here are **round trips and shard selection, not size**. Count
the fetches one lookup makes (`index.json` manifests, `freq/`, the set shard,
`hw/index.json`, `family/`) and see how many are serial where they could be
parallel or cached. Measure before assuming.

## 5. Constraints that are not negotiable

* **The dictionary stores are served from R2, not Pages.** Any store change is
  not done until `r2_upload.sh` has run *and* `WLV` is bumped — otherwise
  production serves the old store while the repo looks fixed. That failure mode
  has already happened once here.
* **`check_search.js`, `check_apd_gear.js`, `check_lookup_reach.js` must stay
  green**, and a new assertion should be made to **fail on the current build
  first**. A perf change that quietly changes *results* is a correctness
  regression wearing a stopwatch.
* **`stamp_build.py --write` after any change under `site/`**, and it is **not
  idempotent** — see `NEXT_SESSION.md`.
* **Cache-bust when reading the live site, and give Pages time.** Five false
  "the deploy failed" readings so far.

## 6. Candidate levers, in the order the measurement will probably rank them

Listed so they are not forgotten — **not** as a plan. §1 decides which survive.

0. **Exact-by-default (§0)** — do this first, or the rest is tuning a path that
   is about to change shape.
1. **Pre-compress, or confirm the host already does.** Cheapest by far if absent.
2. **Split the fat buckets.** `pa` and `sa` are 10% and 9.5% of bucket bytes on
   their own; a third character (`pat`, `par`, …) for oversized buckets only
   would cut the worst case hard and leave the median untouched. The dictionary
   store already uses exactly this idiom with its 150 kB cap — **reuse it rather
   than inventing a second one.**
3. **Kill or shrink the `k.txt` path** if §3 shows real queries hit it. A
   prefix/suffix structure, or an n-gram bucket set, instead of a 10 MB linear
   scan.
4. **The per-volume `idx` split** — postings and text separately, so rendering a
   hit does not pull 1.6 MB of text to show a snippet. This is already on the
   backlog as "the search heavy half", parked with the note *"only if common-word
   searches actually hurt you in use."* **They now reportedly do; that note is
   the thing being revisited, so say so explicitly rather than re-parking it.**
5. **Dictionary round trips** — §4.

## 7. What "faster" means here — agree it before optimising

There is **no performance gate in this repo**, so there is currently no number
that can regress. Before changing anything, write down what is being measured:
cold first search vs warm; a median word vs a `pa`/`sa` word vs a wildcard; a
laptop vs the phone that the bucketing work was originally done for (an iOS
freeze is what prompted it). **Then build the harness that reports it**, and
record a baseline, so the work can be shown to have done something. Otherwise
this ends as a set of plausible changes with no evidence.
