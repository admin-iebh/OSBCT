# The word-lookup panel — a roadmap

Written 2026-07-30, as design advice, not as work done. **Nothing here has been
built, piloted or measured.** Every number below is a question to answer, not a
finding.

The goal: **a reader clicks any word in the reader and a panel opens giving its
definition and related information.**

---

## 1. THE FRAMING — THE DICTIONARY IS THE EASY HALF

A reader clicks *yassindriyāni*. A dictionary is keyed by *indriya*. Between the two
sit **sandhi** (`yassa` + `indriyāni`) and **inflection** (nom./acc. pl. n.). Every
dictionary is keyed by lemma; every word on the page is a surface form, often a
joined one.

So "click a word, get a definition" is only superficially a dictionary feature. It is
a **morphological analysis feature with a dictionary attached at the end**.

- **The sandhi solver is not the first step. It is the last.** It is needed for the
  residue, not the bulk.
- **A useful panel can ship with no linguistic machinery at all** — steps 2 and 3.

---

## 2. THE CONSTRAINT, AND WHERE THE DEFINITIONS SHOULD COME FROM

From the project instructions:

> *No dictionary is an authority in this project; a lexicon may be used only as a
> filter (does this string occur?), never as a source of analysis presented to the
> reader.*

That rules out the default design — click a word, show its PED entry. It does **not**
rule out a dictionary panel. It rules out a modern lexicographer being the voice in
it.

| Source | What it gives | Status |
|---|---|---|
| **The Aṭṭhakathā itself** | the tradition's own word-glosses, with page citations | **already converted, gated and cross-linked — 52 volumes on disk** |
| **Abhidhānappadīpikā** | Moggallāna's 12th-c. Pāḷi lexicon, in verse | traditional authority, out of copyright — **not among the 118 volumes; must be sourced** |
| **Saddanīti, Dhātumālā** | roots, in the form the project requires (**√gamu**, not √gam) | already named as authoritative — **also must be sourced** |

**Modern dictionaries enter only as a filter.** Their real value here is not their
glosses but their **inflected-form → lemma tables**, which is the hard part of §1.

- **DPD (Digital Pāḷi Dictionary)** — the most useful, because of those tables.
  Licence **CC BY-NC-SA**: the same share-alike clause the project declined for the
  corpus. Keeping it on the *filter* side of the line is also the cleaner licensing
  position — filtering does not redistribute it.
- **PED (Rhys Davids & Stede)** — public domain, usable as a fallback filter, but
  digitisations vary in quality and would need their own verification pass.

**Attribute every panel line to its source** (working principle 4). A reader must be
able to tell an aṭṭhakathā gloss from an Abhidhānappadīpikā entry from something the
pipeline inferred.

---

## 3. THE SIX STEPS

### Step 1 — Measure the vocabulary

**Detailed in Appendix A — it is the step everything else rests on, and it is easy to
run badly.** In outline: tokenise all 118 volumes, produce the frequency
distribution, and answer *what share of running tokens could be resolved at all*.

Produces the number that scopes everything after it, and a frequency table that is
itself the seed of the index in steps 2–3.

### Step 2 — The click mechanism and the panel shell

Click a word → panel opens → the exact form, its occurrence count, and links to its
other occurrences across all three layers with printed page numbers. No linguistics;
the search index already holds the data.

*"Show me every other place this exact string appears across canon, commentary and
subcommentary"* is a real scholarly tool, and no other Tipiṭaka reader offers it
across all three layers of this edition. It also de-risks the click-targeting
question (§5) before anything linguistic depends on it.

### Step 3 — The aṭṭhakathā's own glosses — **the centre of the feature**

The commentaries gloss words by a formula: the word, then `-ti`, then the
explanation — *indriyānīti …*, *bhikkhaveti …*. That formula should be
machine-extractable by the same pattern work that parsed the printed footnote
cross-references.

Keyed by the glossed word, a click then gives **the tradition's own definition, from
the edition being published, with a page citation.**

**PILOT ON ONE VOLUME FIRST**, as the commentary work was piloted on 02VinA02.
Extract from a single aṭṭhakathā, verify against the printed pages, count the yield.
**The yield is unknown until this is run — do not plan around a guess.**

### Step 4 — Traditional lexicon entries

Abhidhānappadīpikā for vocabulary; Saddanīti's Dhātumālā for roots.

**Check the dependency now:** neither is among the 118 volumes. If they exist only as
the same legacy-font PDFs, that is a conversion sub-project — not hard, given it has
been done 118 times, but not free.

### Step 5 — Morphology: form → lemma

Inflection tables derived from Kaccāyana, so *indriyāni* resolves to *indriya* with
its grammatical identification. This is where the **Kaccāyana Pāḷi-Español** work
joins this project. A modern lexicon enters here as a filter on candidate analyses.

### Step 6 — The sandhi solver

Split *yassindriyāni* → *yassa* + *indriyāni*, then feed step 5. Hardest, most
error-prone, needed only for what earlier steps could not resolve. By this point step
1 will have said how much text that is — and if it is 8% of tokens, it may reasonably
wait indefinitely.

**Steps 2 and 3 ship a genuinely useful panel with no linguistic machinery
whatsoever.** Everything from 4 onward improves the coverage of a thing that already
works.

---

## 4. DESIGN RULE — PARTIAL COVERAGE MUST BE HONEST

Working principle 2, *flag rather than guess*.

- **Resolved** — show the entry, and say what it was resolved *as*.
- **Ambiguous** — show all analyses as alternatives. **Do not rank them by a guess
  and do not silently pick the first.**
- **Unresolved** — say so plainly, and fall back on the occurrences of that exact
  string across the corpus.

A reader told *"this form is not yet analysed; here are its 47 occurrences"* is being
helped honestly. A reader shown a confident wrong lemma is being misled and will not
know it. **The second is worse than showing nothing** — the same judgement that
killed the forward-walk join for the direct links.

Consider publishing the coverage figure on the site itself.

---

## 5. TWO ENGINEERING DECISIONS TO TAKE EARLY

**Do not wrap every word in a `<span>`.** Paragraphs run to tens of thousands of
characters; a per-word DOM would multiply node counts across a 118-volume reader,
slow rendering, and risk breaking copy-paste and the existing search highlighting.
Recover the clicked word from the text node via caret position instead.

**Shard the index like `names.json`.** Shard by initial letters, load on demand,
cache per session. **Nothing here needs a server.**

---

## 6. GIVE IT A GATE

Sample N words per volume; report coverage, ambiguity and miss rates; and **check
that nothing is ever displayed as resolved when it was inferred.**

The argument: on 2026-07-30, 23,386 cross-references were parsed correctly for weeks
and never reached the reader, and not one of the three existing gates could see it.
A feature whose value is what appears in a panel needs a gate that opens the panel.

---

## 7. SMALLER THINGS WORTH GETTING RIGHT

- **Panel chrome goes through `i18n.js`; the Pāḷi never does.**
- **Roots cited as √gamu, never √gam.**
- **Do not let the panel become a second reader.** Headword, provenance-marked gloss,
  grammatical identification where known, occurrences, links. "And so on" is where
  this feature would quietly become a year.
- **Every extraction is verified against the printed page.** A gloss index built by
  pattern-matching inherits every defect of the pattern.

---

# APPENDIX A — STEP 1 IN DETAIL

Cheap to run and easy to run *wrong*. Three of the traps below come from defects this
project has already recorded, and each would silently corrupt the result rather than
fail loudly.

## A.1 Decide what counts as a word — before counting

- **Tokenise on whitespace and punctuation, with the Pāḷi alphabet as the whitelist.**
- **!!! STRIP THE FOOTNOTE MARKERS FIRST.** The apparatus marker is a **digit glued
  to a word** — `rekey_apparatus.py` finds them with
  `[a-zāīūṁṅñṭḍṇḷ](\d{1,2})\b`. Left in, `dhammo` and `dhammo1` count apart: the type
  count inflates and thousands of real words fall into the hapax tail.
- **!!! EXCLUDE THE SIX PARAGRAPHS THAT CARRY A PRINTED WORD INDEX INSIDE THE BODY** —
  03Vin03 ord489, 24Khu07 ord210 + ord211, 34KhuA15 ord944, 38KhuA19 ord855,
  51Vism01 ord363 (HANDOFF 2026-07-29q). **An alphabetical index is a word list.**
  Injected into a vocabulary count it inflates types, flattens the frequency curve and
  makes coverage look far worse than it is. 300,000+ characters of it.
- **Exclude the page rule** `── page N ⧉ ──` and other render furniture.
- **Decide the hyphen question and report BOTH ways.** Count hyphenated compounds as
  single tokens and as split tokens; the two numbers bracket the truth.
- **Decide what to do with `hide/` paragraphs and the 2,422 canon paragraphs anchored
  to hidden ordinals.** They are in the corpus but on no page of the site. Count them
  separately rather than silently in or out.

## A.2 Corpus-internal statistics — no external data needed

- **Tokens and types**, overall, per layer (canon / aṭṭhakathā / ṭīkā) and per volume.
- **The cumulative coverage curve** — share of *running tokens* covered by the top 1k,
  5k, 10k, 25k, 50k types. **This is the number the whole roadmap turns on.**
- **Hapax legomena**, count and share — the tail frequency will never reach.
- **Length distribution**, in characters and syllables. Long forms are where
  compounding and sandhi live.
- **A character census over tokens.** Every token must be Pāḷi-alphabet characters and
  nothing else; residue flags an extraction defect rather than a vocabulary fact —
  **self-verifying, exactly as §3 of the project instructions prescribes.**

## A.3 The coverage probe — and why it is permitted

**"Resolvable by exact match" cannot be computed without a list of forms**, and the
project has no lemma list. The only cheap source is DPD's or PED's inflected-form
tables.

Using them here is a **membership test** — *does this string occur in the list* — and
nothing from them is shown to a reader. That is precisely the use the constraint
permits. State it explicitly in the report so nobody later mistakes it for the project
adopting a dictionary.

Report **two** numbers, per layer: share of **types** in the list, and share of
**running tokens**. **The token number is the one that matters** — types are dominated
by the tail; tokens are what a reader clicks.

## A.4 Ground truth on a sample

"How much of the corpus is sandhi?" cannot be answered by a machine that cannot yet
split sandhi. Any automated estimate (form length, vowel patterns) is a **proxy** and
must be labelled one.

Draw **~200 tokens by frequency-weighted sampling** and hand-classify each as simple
inflected / compound / sandhi-joined / proper name / uninflected particle. That gives
an honest split between what step 5 would fix and what needs step 6, and calibrates
the proxy so the corpus-wide figure carries a known error rather than being a guess
dressed as a statistic.

## A.5 Write the decision rule BEFORE the numbers arrive

- **≥60% of running tokens** in the form list → build steps 2–3 now.
- **40–60%** → build, but lead the panel with **occurrences** and treat glosses as the
  bonus rather than the promise.
- **<40%** → the aṭṭhakathā gloss route (step 3) *is* the feature, and the lemma route
  waits for the Kaccāyana work.

## A.6 Outputs

- **A report** with every number above and the sample classification.
- **`freq.json`, sharded** — not a throwaway: it is the seed of the index in steps 2–3.
- **A decision**, per A.5.

## A.7 Operational

Tokenising tens of megabytes is seconds of CPU, but the device shell is capped at
**45 s** and background jobs do not survive between calls — write it resumable and
budgeted, as `_stale/sweep.sh` and `_xref/verify_xref_links.js` are. It is a
read-only measurement: **it must not write into `site/`**, and it must not import a
nav builder.
