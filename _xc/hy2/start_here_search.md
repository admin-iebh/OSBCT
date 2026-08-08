# START HERE — the reader's search box

<!-- Written 2026-08-08 at the end of the apparatus session, for a fresh chat.
     Read `_xc/hy2/start_here_2026-08-08_pm.md` FIRST for the state of the
     repository; this file is only about the search box. -->

## DONE 2026-08-08 (search session) — all three asks; not yet committed

Commit message in `COMMIT_MSG.bak` (`COMMIT_MSG_search.bak` is an identical
leftover — delete it on the host; `rm` is blocked from the sandbox).
BUILD `ab3632cc3580` →
`3bcc7431b9a5`.  Gate: **`pipeline/check_search.js`** — 10 assertions against
ground truth computed from the shards; `--selftest /tmp/reader2_HEAD.html`
(i.e. the pre-fix build, `git show f82db5ab:site/reader/reader2.html`) fails
7 of 10, reproducing the reader's "No matches" verbatim.

  1. **Rows** carry `book · sutta · volume` in `.sr-where`, book resolved from
     `booktitle/` exactly as the ¶-tooltip does (all 118 indexed volumes now
     carry a non-empty stack — the 79-volume census is stale), NEVER the corpus
     `book` field.  Verified on the brief's own example: 07Di02 rows say
     `Mahāvaggapāḷi`, not `Pubbenivāsa-`.
  2. **Multi-word**: split → per-word matchTerms (exact wins, so `me`/`ca`
     resolve) → volume intersection → per-paragraph posting intersection →
     adjacency by folded-phrase `indexOf`.  Phrase hits counted by occurrence;
     all-words-apart paragraphs listed after, labelled "not adjacent", never
     merged.  `markInEl` marks the phrase, or each word where no text node
     carries it whole.  Measured: `evaṁ me sutaṁ` 105 vols; 07Di02 18 AND / 10
     phrase.
  3. **Slow**: measured first, as this file asked.  (b) sweep over 643,965
     keys = 7–15 ms, cap lands early — not the cost.  (a) 22 MB, paid once,
     says so on screen — left alone.  (c) WAS the cost: shards (avg 1.64 MB,
     194 MB total, up to 118 per common word) were awaited ONE PER ITERATION.
     Now fetched 8 at a time.  Also closed on the way: `shard()` cached jget's
     empty fallback on a failed fetch — the 2026-08-02 term-map trap, one
     function up.  Promise cached, deleted on failure.

  Placeholder now says "words or a phrase" (en + es, `r2_search_ph`).

  ~~**Left open here:** `search.html` still answers one word only…~~ **CLOSED
  later the same day** (reader hit `sabbe saṅkhārā` on search.html, screenshot):
  the whole port landed there — multi-word, booktitle/ rows, 8-wide shard pool,
  and its `shard()` had NO error handling at all (one lost request threw out of
  `run()`).  Same session added, to BOTH boxes: **`*` wildcard** (`.*` against
  term keys, `\S*` against running text so a star cannot cross a word; ≥3
  literal letters, same 500 cap), **heads that count everything found** ("N
  occurrence(s) in P paragraph(s), V volume(s)", V = phrase volumes only), and
  to the reader box: **layer chips** in the dropdown (not a select — `.search`
  is 90px on a phone) and a **"?" help chip** opening bilingual instructions;
  search.html carries the same text in its footer via `i18n.js`.
  `pipeline/check_search.js` now boots BOTH pages, 26 assertions, selftest
  fails 20/26 on the pre-fix pair (old reader = `git show
  f82db5ab:site/reader/reader2.html`, old search = `git show
  d1b01414:site/search.html`).  Measured live: `sabbe saṅkhārā` → 280
  occurrences, 166 paragraphs, 61 volumes, +90 non-adjacent, 2.7 s cold in
  jsdom.  BUILD `3bcc7431b9a5` → `5fd3c711bc8e`, commit message in
  `COMMIT_MSG.bak`.

  **Still untouched:** ~~the 22 MB first-load~~ and the per-volume shard model.
  **2026-08-09: the reader chose the moderate half and its DATA is built** —
  `pipeline/build_term_buckets.py` → `site/index/tb/`: `meta.json`
  (vols/layers), `k.txt` (all 643,965 keys newline-joined, 10.2 MB raw /
  2.27 MB gz — the sweep surface, `indexOf` over one string, NO giant JSON
  parse), 273 `<p2>.json` postings buckets (largest `pa` 2.23 MB raw /
  0.54 MB gz).  Self-verified: bucket union == source map EXACTLY.  The UIs
  ARE NOT WIRED — they still read `terms.compact.json`, which stays as gate
  ground-truth and fallback.

  **WIRED, same day (2026-08-09 pm), gate first as briefed** — both UIs on
  the buckets, 40 assertions all green, selftest fails exactly the five
  wiring facts on the unwired build.  Exact word → its bucket; sweep →
  k.txt + candidate buckets; `xxx*` → one bucket; meta-404 → legacy
  fallback, proven by hiding tb/.  Every new await carries its ticket
  check.  What remains of search speed is ONLY the heavy half (per-volume
  shard split), waiting on the reader's live-network verdict for
  common-word searches.  The original brief, for the record: `matchTerms` goes async —
  exact word → its p2 bucket only; substring or `*xxx` sweep → `k.txt`
  (cached as ONE STRING, scanned with indexOf) then fetch only the buckets
  the ≤500 candidates live in; `xxx*` prefix wildcard → its bucket alone.
  EVERY NEW AWAIT NEEDS ITS OWN `if(my!==sSeq) return` — the race trap is
  the whole reason the wiring is its own change.  Wire reader2.html and
  search.html identically (they have drifted before), extend
  `check_search.js` first so it fails on the unwired build only where wiring
  is asserted, and keep the `terms.compact.json` path as the fallback when
  `tb/` 404s (an unpacked old archive).  The per-volume shard model (the
  heavy half) waits for the reader's live-network verdict.

  **Same-day follow-ups, all reader-reported, all gated (commits after
  `1af292ec`):** the mark's dark-theme contrast (6.89:1 → 14.48:1, the
  `mark.shl` idiom in both boxes); rows ordered Pāḷi → Aṭṭhakathā → Ṭīkā by
  sorting `vis` itself; per-layer row caps (30/14 reader, 70/35 search —
  `arati` holds EXACTLY 80 canon paragraphs and the old global cap of 80 drew
  nothing else); the chip click that closed the dropdown (microtasks run
  between listeners, the repaint detached the target, `contains()` lied —
  `composedPath()` doesn't); `Tipiṭaka` → `Pāḷi` everywhere on search.html;
  and search.html's layer select replaced by the reader's chip row.
  `pipeline/check_search.js` ended the day at 34 assertions, each shown to
  fail on the build that had its bug.

The reader asked for three things, in this order of interest:

  1. more information on a result row — the book and sutta, not just `Pāḷi ¶52`;
  2. searching more than one word;
  3. it is slow, and "if I type a word after searching one it does not search
     anymore".

**2 and 3 are partly the same bug.** Establish that before planning anything.

## Where the code is

`site/reader/reader2.html`:

    ~3282  doSearch(q)        the whole box
    ~3279  the `input` listener, 180 ms debounce
    ~3255  matchTerms(ft)     which index terms a query matches
           foldS(s)           diacritic folding
           ensureTerms()      loads `index/terms.compact.json`
           shard(vi)          loads `index/<VOL>.idx.json`, cached

`site/index/`: `terms.compact.json` (**22 MB**, `{terms:{term->[volIdx]}, vols:[],
layers:[]}`) and 118 `<VOL>.idx.json` shards (**234 MB total**).

Built by `pipeline/build_search_index.py`. `site/search.html` is a SECOND
implementation of the same search and the two have drifted apart before — check
whether a change belongs in both.

## 1. The row already has everything it needs. MEASURED.

The shard's paragraph objects are NOT bare text. `31KhuA12.idx.json` paragraph 20:

    {"id": "Therīgāthāaṭṭhakathā/X/X/u28", "n": null, "page": 21,
     "sutta": null, "book": "Therīgāthā-aṭṭhakathā", "vagga": null,
     "peyyala": false, "text": "Karotha buddhasāsananti Visākhāya …"}

So `book`, `sutta`, `vagga`, `page`, `n` are all in hand at the moment the row is
built. The row currently prints only

    <span class="sr-lay">Pāḷi ¶52</span>

**This is a display change in one template string. No reindexing.**

!!! BUT `book` IS NOT THE BOOK IN 61 OF 118 VOLUMES. `reader2.html` says so at
`block()`: `07Di02` carries `Pubbenivāsapaṭisaṁyuttakathā` as the `book` of all
335 paragraphs of the Mahāparinibbānasutta — a kathā, one level too deep — while
the real book sits in `vagga`. The reader's own tooltip stopped using `book` for
that reason and derives the book from `booktitle/<VOL>.json`, the stack the
edition prints on the book's own title page, keyed by the ordinal the book opens
at. **A search row that prints `book` naively will name the wrong book on half
the corpus.** Either resolve it the way `block()` does, or prefer `sutta` and
fall back to the volume title. Decide it on evidence, not on the field name.

## 2 and 3. Why a second word kills the box

`matchTerms` does exactly two things:

    if(TERMS.terms[ft]) return [ft];        // exact term
    ... else sweep every term key for `ft` as a SUBSTRING, cap 500

The term keys are single words. A query with a space is neither an exact term nor
a substring of any single-word key, so `matchTerms` returns `[]`, `vis` is null,
and the box paints "No matches for …". **That is the whole of "it does not search
anymore" — it is not a hang and not a stale-state bug.** Confirm by typing a
query with a space and watching `matchTerms` return an empty array.

Multi-word therefore needs: split the folded query on whitespace, resolve each
word to its terms, intersect the volume lists, intersect the per-paragraph
postings, and — for a phrase — verify adjacency in `p.text`. The snippet builder
also assumes one contiguous match (`f.indexOf(fq)`) and will need to mark
several.

**The slowness has three separate causes and they need separating before any of
them is "fixed":**

  a. `ensureTerms()` pulls **22 MB** before the first search of a page load can
     answer anything. There is already a "Loading the search index…" line for
     this, added because a silent box was reported as broken.
  b. The substring sweep runs over EVERY term key on every keystroke that is not
     an exact term — which is most keystrokes while a word is being typed. The
     3-character floor and the 500 cap are already there for this reason; the
     comment records `og` matching 500 terms across most of the corpus.
  c. One shard is fetched per matching volume. A common word means many shards
     out of 234 MB.

**Measure which of the three dominates before changing any of them.** A prefix
index, or a first-3-letters bucket map, would address (b) without touching (a) or
(c); they are not the same fix.

## The traps this box has already fallen into — do not re-open them

  - **The race.** `doSearch` awaits three things, so an early keystroke can paint
    over a later one: typing `oghasutta` once showed "11,043 occurrence(s) for
    “og”". Every call takes a ticket `my=++sSeq` and paints only if it is still
    newest. **Any new await needs its own `if(my!==sSeq) return;` after it.**
  - **`p.key` never existed.** The occurrence rows called `openKey(p.key, …)` and
    `key` is present on **0 of 86,365** indexed paragraphs; `ord` is on all of
    them. Every occurrence click opened `'undefine'#NaN`, drew nothing, and the
    band reported "No Aṭṭhakathā is linked to the passages on screen" — a wrong
    answer that reads as an honest one. A row with no ordinal is now drawn with
    NO onclick rather than a dead one.
  - **A failed fetch must not be cached as an answer.** `TERMS` was once left as
    `{terms:{}}` after a failed load, so the box answered "no matches" forever.
  - **Centring is not arriving.** `openHit` scrolls to the WORD, not the
    paragraph; a commentary paragraph is routinely taller than the window.

## How to verify anything here

`pipeline/check_fn_markers.js` is the pattern: it boots `reader2.html` in jsdom
with a `fetch` that reads the repository, drives the real UI, and asserts against
the rendered DOM. Copy its `boot`/`ready` preamble. **jsdom OOMs at about 20
volumes in one process — run in batches of 3 to 8.**

And the project's rule, which cost four wrong diagnoses in one day: RUN THE
INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG, and when a check disagrees with
the reader, suspect the check first.

## Before touching anything

`stamp_build.py --write` after every change under `site/`, then `./push.sh`.
