# The Abhidhāna and the APD books now answer to their own headwords

**2026-08-10.** The repair of `claude/dpd_gates_the_abhidhana.md`. Built,
gated, and NOT yet uploaded — see §7, which is the part that is not done.

---

## 1. What was wrong, in one sentence

`_panel/build_eval.py:64–89` builds the `lem` key set as corpus forms → DPD
index → DPD headwords, and then attaches the Abhidhāna (`:265`) and the APD
books (`:500`) **to those lemmas and nothing else** — so an evaluation-only
source that §9 ranks lowest was the gate the §9 authority had to pass, and
163,453 of 210,111 headwords (77.8%) were unreachable from the reader.

## 2. What was built

`stores/lookup_eval/hw/` — a **separate** store, `_panel/build_own.py`, from the
two files the reader named: `_dictsrc/pced_full.jsonl.gz` and
`_dictsrc/pm12e.csv`. Both are gitignored and exist nowhere else.

**`lem` was not widened, not rebuilt and not read.** Nothing an existing gate
depends on changed, which is why nothing could regress; and the panel consults
`hw` only where `lem` has already returned nothing — the path that says "no
entry" today.

**The key is `fold(headword)`** — lowercased AND diacritic-stripped. That closes
the key-case trap the note named (PCED's `acc` is `Yathānisinna`, capitalised,
and `panel.js look()` tries the exact key then `toLowerCase()` only), and it
gives §7's diacritic-insensitive lookup in the same stroke: `Yathānisinna`,
`yathānisinna` and `yathanisinna` are one key. The dictionaries' own accented
spellings are kept in the value's `w` field, so the reader still sees the
headword as the dictionary prints it.

**The manifest is the store's own**, at `stores/lookup_eval/hw/index.json`,
fetched lazily on a miss. `build_eval.py` rewrites the eval `index.json`
wholesale at the end of every run, so an `hw` entry there would vanish on the
next eval rebuild — silently, the way `stores/lookup_eval/family/` vanished from
a commit on 2026-08-09.

## 3. Measured BEFORE it was built — `_panel/measure_own.py`

    185,809 folded keys          (210,111 distinct RAW headwords; fold() joins them)
    145.8 MB of JSON             mean 785 B per key
    largest single key   64 kB   — so NO key needs an overflow file
    6,751 shards, largest 148 kB, none over the 150 kB cap
    shard-name depth 2–10

The cap holds with the sharder alone; `build_own.py` asserts that rather than
assuming it, and stops if a future import breaks it.

**And a finding that was not expected: every Abhidhāna headword is also a PCED
headword under fold().** `pm12e`'s 146,865 folded keys are a subset of PCED's
185,809, so the union is 185,809 and not the two added together — which is what
one would expect of PCED book K, the same digitisation lineage.

## 4. Reachability, after — measured against the shipped store

    book B  Pali Myanmar Dictionary          153,527 →  153,527   100.0%
    book K  Tipiṭaka Pāḷi-Myanmar Dict.      153,527 →  153,527   100.0%
    book R  U Hau Sein's                      58,095 →   58,095   100.0%
    books C · I · N · O · P                                       100.0%
    pm12e   Tipiṭaka Pāḷi-Myanmā-Abhidhāna   152,451 →  152,451   100.0%

against 22.8% before.

## 5. The gates, and the failing run that came first

**`pipeline/check_apd_gear.js` §10 and §11, RUN RED FIRST**, against the build
that has the bug, exactly as the method requires:

    FAIL  yathānisinna has a dictionary tab  [APD]
    FAIL  book B (Pali Myanmar Dictionary) draws a section
    FAIL  book K (Tipiṭaka Pāḷi-Myanmar Dictionary) draws a section
    FAIL  book B carries the Burmese headword
    FAIL  book K carries its definition
    FAIL  the Abhidhāna tab is live for yathānisinna
    FAIL  the Abhidhāna entry draws
    FAIL  the undiacriticked spelling reaches the same entry
    FAILED: 8 assertion(s)

All 40 assertions are green now, and the 27 that existed before were green
before and after.

**`pipeline/check_hw_agrees_with_lem.py` — NEW, and the reason it exists.**
`build_own.py` re-reads pm12e with its own copy of the Abhidhāna citation
transcoding (`_panel/abhidhana_cites.py`), because importing `build_eval.py`
would drag in a DPD index read and make the fix depend on the dictionary it is
undoing. A copy that drifts is worse than either, so the two are held together
by a mechanism and not by intention: every key the two stores share must carry
in `hw` everything it already carried in `lem`.

    lem entries with a dictionary payload : 47,826
      key absent from hw                  : 0
      Abhidhāna: 34,731 checked · 0 MISSING · 5,038 extra (fold() gathers more)
      APD      : 47,824 checked · 0 MISSING · 0 extra

Zero missing rows over 34,731 Abhidhāna entries is the evidence that the copied
transcoder agrees with `build_eval.py`'s.

> **THE FIRST RUN OF THAT GATE FAILED, AND IT WAS THE GATE.** It reported 1,574
> keys "absent from hw"; every one of them carries DOP, CPD or NCPED **alone**.
> Those three are StarDict files under GoldenDict, injected into the APD map by
> `build_eval.py`; they are not in `_dictsrc/` and this build does not read
> them. **Recorded, not fixed: those three are therefore still reachable only
> through `lem`, which is to say only through DPD's index** — the same defect,
> in a corner this repair does not reach. Widening it needs the GoldenDict
> build present, which is why it was not done blind.

**`pipeline/check_lookup_reach.js`** now names `yathānisinna` in its sample —
named rather than sampled, because the sample is drawn from `lem` and `lem` is
exactly what cannot contain it.

## 6. The search box needed its own wire, and finding that out was luck

Wiring `hw` into `lookup()` alone made the word answer when a reader **clicks**
it in the text, while the search box went on saying "not found" — because the
box asks `inDicts()`, and `inDicts()` asked the three sets keyed through DPD.
**Negative control, run deliberately** with `hwlook` removed from `inDicts` and
nothing else changed:

    FAIL "yathānisinna" resolves through the search box
         got: "No entry for “yathānisinna” in the corpus or the dictionaries"

That is the `atappaka` defect of 2026-08-05 one store later: a word the reader
can read in a dictionary must be a word the reader can type.

## 7. NOT DONE — and the job is not done without it

* **`pipeline/r2_upload.sh` has NOT been run.** The panel fetches this store
  from `https://dict.buddha-dhamma.net/lookup_eval/hw/`, not from the site.
  6,751 shard `.gz` and one `index.json` are new objects in the bucket. Until
  that runs, production reaches the same "no entry" it does today — everything
  green above is green through the unpacked-archive fallback.
* **`WLV` is bumped to `20260810a`** and `reader2.html`'s `panel.js?v=` to the
  same. **Bump AFTER the upload, not before**: a reader who gets the new
  version against a bucket with no `hw/` gets a 404.
* `pipeline/check_r2_origin.js` **cannot** confirm any of this from the sandbox
  — it has no route to the bucket, and its negative control passes when the
  network is down. Run it on the host.
* ~~`python3 pipeline/stamp_build.py --write` refuses, and correctly~~ —
  **WRONG, AND IT WAS THE CHECK.** It refused because it was run with `--fast`,
  which skips the rebuild-and-compare and leaves only the mtime screen, and the
  mtime screen's own docstring warns that it raised a false alarm on
  `pdfblanks` once already. The deep run says `pdfblanks` is **byte-identical to
  a fresh build** and *all derived artefacts fresh*. The four remaining items
  (apparatus, linksk, sections, nav) are advisory and non-blocking.
  **And the deep check had never been able to run on the reader's own machine
  at all**: it shells out to `pdftotext`, which was not installed there, so
  every deploy from that machine has used `--fast` or `--force` — the one gate
  that catches stale derived data has been inert at the moment it matters most.
  Poppler installed 2026-08-10; the gate is real there now.

## 8. Also fixed, cheaply — the miss message was wrong about the corpus

"No entry for X in the corpus or the dictionaries" is false about its first half
for any stem the edition only ever prints inflected. **`corpusPrefix()` now
offers the corpus forms that begin with what was typed, above the message**, one
shard fetch, on the miss path only. It is the mirror of the `atappaka` fallback
at `panel.js:714`: that one made a dictionary **headword** typable, this one
makes a **stem the edition only inflects** findable.

Gated on `yathāvuttamattha`, chosen because it is a genuine miss in *all* of
freq, ped, lem, dpd and hw, with 4 corpus forms and 91 occurrences — so the gate
presses the fallback and not a lookup that would have succeeded anyway. The
forms shown are pulled from `lookup/freq`; none is invented.

## 9. Untouched, deliberately

The §2 / §9 **redistribution** question. These sources sit in `lookup_eval/`
because their redistribution is unresolved, and that is exactly as unresolved as
it was. What changed is that even in evaluation, where the reader may lawfully
consult them, three quarters of the lexicon is no longer unreachable.

---

## 10. Two defects found on the reader's first live look, 2026-08-10

**THE UPLOAD SHIPPED NOTHING, AND THE INSTRUCTION WAS THE CAUSE.**
`pipeline/r2_upload.sh` derives its file list from `git ls-files` — deliberately,
after the 2026-08-07 incident where walking the filesystem pushed 11,229
gitignored DPD shards to the bucket. The session's own instruction was
"R2 FIRST, then commit", which for a store that is not tracked yet means
`git ls-files` names none of it and the upload copies **zero** new objects.
Worse, the script's own safety check cannot see it: it compares the bucket count
against `git ls-files | wc -l`, and both sides exclude the same 6,752 files, so
it reports a match. **The ordering rule is: `git add` (or commit) FIRST, then
upload, then deploy.** The script's header records the hazard it was written
for; it does not record this one, which is its mirror image.

**THE PREFIX LIST DROPPED THE COMMONEST FORM IT WAS DESCRIBING.**
The reader's screenshot showed *7 forms · 16 occurrences* for `yathānisinna`
where the corpus has **12 and 52**. A literal prefix match cannot see a stem
whose final vowel has inflected: `yathānisinnova` (27 occurrences, more than
half the total), `yathānisinneneva`, `yathānisinnesu`, `yathānisinno`,
`yathānisinnoyeva`. The count line stated 7 and 16 as though they were the
answer — **a summary contradicting the data it summarises, one day after that
was written into the method.** `prefixOf()` now trims one trailing vowel or
nasal from the folded query, and the heading names the prefix actually matched
(`yathānisinn`, accented, sliced from the typed string because fold() is one
character for one), so the panel no longer claims to have matched the word.
Gated at `check_apd_gear.js` §11.

---

## 11. Widened to every dictionary the panel serves — 2026-08-10, second pass

The reader: *"All dictionaries should be reachable through the search box in the
word lookup pane."* He is right, and the first pass built only what the task's
constraint 1 named — the two files in `_dictsrc/`. The rest of the APD tab is
DPPN plus four StarDict dictionaries, and they were still gated by DPD.

**Done and verified here: DPPN.** `_dictsrc/DPPN.json` was already in the
folder. 13,642 names on their own headwords; `check_hw_agrees_with_lem.py`
checks 2,210 shared keys with 0 missing. Store now 191,928 keys · 7,155 shards
· largest 147 kB.

**Written, and NOT verifiable here: PEU, DOP, CPD, NCPED.** These are GoldenDict
StarDict files, not in `_dictsrc/`, and that build is not on this machine.
`build_own.py` now reads them on their own headwords — every `.idx` key and
every `.syn` spelling — using `sources.py`, the same reader `build_eval.py`
uses. Absent, they are **skipped loudly**, and the manifest records the fact in
`stardict_missing`. `check_hw_agrees_with_lem.py` reads that field instead of a
hard-coded list, so **the gate tightens by itself** the moment the store is
rebuilt where they exist, rather than going on excusing an absence nobody
rechecks. PEU matters most of the four: it is the Abhidhāna's own English
rendering, shown inside the Abhidhāna entry, so a word reached through this
store shows the Burmese and not the English until it is built.

### The tab counted its dictionaries and drew none of them

Reader-reported, and **rendered to confirm rather than reasoned about**: with
the default gear, `yathānisinna` showed `APD 2` over a body holding one grey
line. The only sections that open by default are CPED and PED — his decision of
2026-08-06 — and the word is in neither. `Akalaṅka`, whose one source is the
proper-names section, said `APD 1` and drew nothing at all.

The defaults are unchanged. What is fixed is the case they cannot cover: **if
nothing would be open, the first section opens.** No persisted state is
touched, and any word that has CPED or PED behaves exactly as before. A count
with nothing behind it is the failure this panel keeps being caught by, and
"hidden must not mean absent" is why the summary line exists at all. Gated at
`check_apd_gear.js` §12 on `Akalaṅka`, which is a Malalasekera name and nothing
else — absent from freq, ped, lem and dpd, with no APD row and no Abhidhāna row,
so it exists in the panel only if DPPN was keyed on its own headword.

### Where it stands

| source | reachable by its own headword |
|---|---|
| the Abhidhāna (pm12e) | yes |
| PCED books P C N I K B R O | yes |
| DPPN (proper names) | yes |
| PEU, DOP, CPD, NCPED | **only after a rebuild with `~/GoldenDict` present** |
| DPD | no — and §9 excludes it as a voice in any case |

---

## 12. The search box silently corrected what was typed — 2026-08-10

**Reader: "If I type `kiriya` it should not change to `kiriyā`. If I type
`itthi` it should not correct to `itthī` after pressing enter."**

Measured, and both typed spellings are real words of the edition:

    kiriyā  296 occurrences   ·   kiriya   4
    itthī   825              ·   itthi   45

`resolveTyped` had checked the exact key **only when the query carried a
diacritic**; a plain-ASCII query went to the commonest form folding to it. That
order was set on 2026-08-05 for a real reason — `nibbana` occurs once and
`nibbāna` 17,211, so exact-first sent a reader to a hapax — but what it did in
practice was open a word the reader had not typed, **with nothing said**.

**Exact now wins, always.** The frequency argument is answered a different way
rather than discarded: `siblings()` offers every other corpus form that folds to
the same string, commonest first, as clickable chips under the counts line —
*Also spelt: kiriyā 296*. Same information, no substitution, and the shard is
the one `resolveTyped` already fetched, so it costs no request.

A query that is **not** a corpus form still falls through to the fold match, or
diacritics would stop being optional (§7) and the search box's own placeholder
would be a lie: `pathavikasina` still reaches `pathavīkasiṇā`. Gated at
`check_apd_gear.js` §13, all three cases.

**Consequence to be aware of, stated rather than buried:** typing `nibbana` now
opens `nibbana`, the single canonical occurrence, with *Also spelt: nibbāna 49*
beside it. That is the 2026-08-05 decision reversed, deliberately and at the
reader's instruction.

## 13. PCED book `C` is contaminated — REPORTED, NOT FIXED

Found while choosing a word to recommend for testing, which is the only reason
it was seen at all. Book `C` is labelled *"Concise P-E Dictionary — Concise
Pali-English Dictionary by A.P. Buddhadatta Mahathera"*, and **1,773 of its
22,564 rows (7.9%) are Japanese or Chinese**:

    Abhayagiri：m. アバヤギリ（Abhayagiri的片假名發音），無畏山 [寺].

That is text shown to the reader under the name of an author who did not write
it — principle 4, reaching the screen. **It pre-dates this work**: 1,780 such
bodies are already in `lem` and live today, so `hw` did not introduce it, only
widened its reach.

Not repaired, because the repair is a choice and the evidence does not settle
it: either book `C` is a mislabelled merge in the PCED dataset, or PCED's book
table names it wrongly, and telling those apart needs the PCED source rather
than our derived copy. Whoever takes it: the marker is cheap —
`re.search(r'[぀-ヿ一-鿿]', body)` — but dropping every row that matches would
also drop any legitimate entry that quotes a Chinese term, so measure before
cutting.
