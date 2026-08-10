# DPD decides which words the Abhidhāna may answer — and it silences 77% of it

**Found 2026-08-09 from the reader's report that `yathānisinna` returns "no
entry", while `dictionary.sutta.org` answers it from the Pali Myanmar Dictionary
and the Tipiṭaka Pāḷi-Myanmar Dictionary.** He was right, and the word is in our
own sources. Measured at build `92157e0692e0`. **Nothing changed.**

---

## 1. The word is here, in both dictionaries he named

`_dictsrc/pced_full.jsonl.gz`, three entries:

    book B  Pali Myanmar Dictionary            hw='yathanisinna'   acc='Yathānisinna'
            yathānisinna（ti） ယထာနိသိန္န（တိ） [yathā+nisinna] [ယထာ+နိသိန္န]
    book K  Tipiṭaka Pāḷi-Myanmar Dictionary   hw='yathanisinna'   acc='Yathānisinna'
            yathānisinna：ယထာနိသိန္န（တိ）[ယထာ+နိသိန္န] နေ-ထိုင်-မြဲတိုင်းသော။
    book R  U Hau Sein's Pāḷi-Myanmar Dict.    hw='yathanisinnam'  acc='Yathānisinnaṃ'

and `_dictsrc/pm12e.csv:145524` — the Abhidhāna itself, with its own analysis:

    yathānisinna,ယထာနိသိန္န(တိ),[ယထာ+နိသိန္န],[yathā+nisinna],နေ-ထိုင်-မြဲတိုင်းသော။,

The corpus uses the stem **52 times in 12 forms**, 34 in the Aṭṭhakathā and 18 in
the Ṭīkā, **0 in the canon** — a commentarial idiom, which is why a reader meets
it and the panel does not know it.

## 2. Why the panel cannot see any of it

`_panel/build_eval.py:64–89`. The key set of the whole `lem` store is built in
one direction:

    corpus forms (_vocab/freq, 685,350)
        ↓  dpd.idx exact match, or dpd.syn.dz synonym
    DPD headwords  (HWS)
        ↓  base_of()
    LEMMAS   ← the key set

and then **every other dictionary is attached to those lemmas and to nothing
else**: the Abhidhāna at `:265` (`abhi.get(lem.lower())`), the twenty-four APD
books at `:500` (`pced.get(fold(lem))`).

So the question the build actually asks is not *"does the Abhidhāna have this
word?"* but *"does DPD have a headword for some corpus form of it?"*

`yathānisinna` is a compound. All twelve of its corpus forms carry
`dpd_tier: 3` in `_vocab/freq` — *"DPD can deconstruct it (sandhi / compound)"*,
which is precisely the tier meaning **DPD has no headword for it**. It therefore
never enters `LEMMAS`, and rows B, K and R are discarded at build time with the
answer sitting in the file.

## 3. The size of it

    lem keys in the shipped store          52,757
    distinct PCED headwords               210,111
        reachable in the panel             46,658   22.2%
        DROPPED                           163,453   77.8%

    B  Pali Myanmar Dictionary            153,527 headwords → 35,022 reachable (22.8%)
    K  Tipiṭaka Pāḷi-Myanmar Dictionary   153,527 headwords → 35,022 reachable (22.8%)
    R  U Hau Sein's Pāḷi-Myanmar Dict.     58,095 headwords → 29,501 reachable (50.8%)

    pm12e Tipiṭaka Pāḷi-Myanmā-Abhidhāna  152,451 headwords → 34,730 reachable (22.8%)

**Better than three quarters of the Sixth Council's own lexicon is in this
repository and cannot be reached from the reader.**

## 4. Why this is not merely a bug

Project instructions §9 admits the Tipiṭaka-Pāḷi-Myanmā-Abhidhāna as **the only
dictionary that is an authority**, on the ground that it is "the Sixth Council's
own lexicon over the Sixth Council's own edition", and demotes DPD, PED, CPD,
DOP, NCPED and the rest to "reference only … not the final authority but tools".

The build inverts that exactly. **DPD — an evaluation-only source whose own
licence is unresolved, and which §9 places lowest — is the gate through which the
named authority must pass.** Where DPD is silent, the Abhidhāna is silenced,
whatever it says.

That is not a policy anyone chose. `LEMMAS` came from DPD because DPD's index is
what maps an inflected corpus form to a headword, which is a real and useful
thing to do. The defect is that the same set was then reused as the key set for
sources that have their own headwords and need no such help.

## 5. What a fix would have to do

Stated for the next session, not decided:

* **Key the APD and Abhidhāna stores on their OWN headwords**, not on `LEMMAS`.
  Both files carry an accented headword (`acc`, and column 0 of `pm12e.csv`);
  neither needs DPD to be found by a reader who types the word.
* **Keep DPD's index for what it is good at** — resolving an inflected corpus
  form to a lemma. That is a lookup aid, not a membership test.
* **Mind the key case.** PCED's `acc` is capitalised (`Yathānisinna`) while `hw`
  is diacritic-stripped (`yathanisinna`). `panel.js look()` tries the exact key
  then `toLowerCase()`, so a store keyed on `acc` as-is would be unreachable from
  a lowercase query. Fold on write, or try the capitalised form on read.
* **Size it first.** Keying on their own headwords takes the store from 52,757
  keys to something over 210,000; shard counts, byte caps and the R2 sync all
  need measuring before it is built, and the `check_apd_gear.js` gate extended.
* **§9 and §2 apply to release, not to this.** These sources are in
  `lookup_eval/` because their redistribution is unresolved — that question is
  untouched by this note and must be settled separately. What is measured here is
  that even in evaluation, where the reader may lawfully use them, 77.8% is
  unreachable.

## 6. Also worth fixing, separately and cheaply

The failure message says *"No entry for X in the corpus or the dictionaries."*
The corpus half of that is false here: `lookup/freq` holds the twelve forms with
their counts and layers. A **prefix fallback before the message** — showing the
corpus forms that begin with what was typed — would have answered the reader
immediately, costs nothing on the common path, and does not depend on any of the
above. Compare `panel.js:714`, the dictionary fallback added for the `atappaka`
report of 2026-08-05: this is its mirror — that one made *headwords* typable,
this one would make *stems the edition only ever inflects* findable.

---

> **THE READER WAS RIGHT AND THE FIRST ANSWER WAS WRONG.** I reported that the
> word "is not in any dictionary we carry" after checking eight store
> directories. The store is not the corpus of sources; `_dictsrc/` is, and the
> stores are a 22% projection of it chosen by a dictionary the project's own
> instructions rank last. **Check the source, not the derived artefact** — the
> same lesson as `claude/x_rows_are_a_stale_snapshot.md`, arriving from the
> opposite direction: there I trusted a stale artefact over the edition, here a
> filtered artefact over the sources.
