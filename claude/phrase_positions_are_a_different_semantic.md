# Phrase positions: measured, not built — they would answer a different question

**2026-09-06.** Item 2 of the third session's list. That session measured the **cost** of
positions (+66 % on every single-word search inside `tp/`; a separate `tq/` store otherwise).
This measures whether positions could **reproduce the page's answer** at all. They cannot.

## What a phrase means on the page today

`searchcore.js search()`: every candidate paragraph carrying all the words is read, and the
phrase is counted as a **substring of the normalised text** — `indexOf('evaṁ me sutaṁ')`, or
for a wildcard the regex `dhamm\S* ti`. Single spaces, the edition's punctuation in place.

## What a position store could decide without the text

Consecutive **tokens**, each matching its query word the way a single-word search does (an
exact key, or a wildcard pattern over keys). `pipeline/measure_phrase_semantics.py` computes
both over all 89,512 paragraphs, resolving a bare word to its exact key as the page does:

| phrase | text: paras / occ | tokens: paras / occ | text-only | tokens-only |
|---|---:|---:|---:|---:|
| `evaṁ me sutaṁ` | 494 / 510 | 494 / 510 | 0 | 0 |
| `bhagavā etadavoca` | 380 / 416 | 380 / 416 | 0 | 0 |
| `dukkhaṁ ariyasaccaṁ` | 84 / 127 | 84 / 127 | 0 | 0 |
| `tassa bhagavato` | 379 / 527 | 318 / 437 | **63** | 2 |
| `atha kho bhagavā` | 875 / 1,327 | 865 / 1,314 | 11 | 1 |
| `bhikkhave dhammā` | 205 / 293 | 191 / 268 | 14 | 0 |
| `sabbe saṅkhārā` | 166 / 280 | 161 / 272 | 5 | 0 |
| `ekaṁ samayaṁ bhagavā` | 705 / 708 | 700 / 703 | 5 | 0 |
| `kāyena vācāya` | 124 / 183 | 134 / 195 | 0 | **10** |
| `dhamm* ti` | 168 / 190 | 1,016 / 1,469 | **127** | **975** |
| `sabb* dhamm*` | 421 / 652 | 416 / 646 | 5 | 0 |

**Text-only** paragraphs are ones the page counts today and tokens would not: the phrase's
first word ending a longer token (`tassa bhagavato` inside *etassa bhagavato* — 63 of the
379), its last word beginning one (`sabbe saṅkhārā` inside *sabbe saṅkhārāti*), a wildcard
matching mid-token (`dhamm* ti` inside *adhammaṁ ti*). **Tokens-only** paragraphs are ones
tokens would count and the page does not: consecutive tokens with the edition's punctuation
between them — *kāyena, vācāya*; *dhammā”ti*, the quotative *ti* closed up against its word,
which is why `dhamm* ti` goes from 168 to 1,016.

So positions are not a prefilter for the current semantic in either direction: a paragraph
the positions reject may be one the text accepts, and vice versa. They could only replace the
text read by **replacing the semantic**.

## The decision, which is the reader's

1. **Keep the text semantic.** Then a phrase must read its candidates, positions save nothing,
   and this item closes as "not buildable without altering results". The over-count in
   `tassa bhagavato` (63 paragraphs of *etassa*) stays, and is the same kind of thing the
   diacritics decision removed from single words.
2. **Change to the token semantic** — a phrase is consecutive tokens. Counts change on most
   phrases (the table is the size of it), *dhammā”ti* becomes an occurrence of `dhammā ti`,
   *etassa bhagavato* stops being one of `tassa bhagavato`. Then a separate position store
   (`tq/`, sharded like `tp/`, fetched only for phrases; builder re-tokenises with
   `build_search_index.py`'s `_TOK`) decides adjacency without text; only drawn rows are read.
   Gate red first: `check_search.js`'s phrase truths would be re-stated in tokens and the
   result line would have to name the semantic, as it names the diacritics mode.

## Decided and done the same day: the token rule, on the text the page already reads

The reader chose the token semantic; the recommendation was to change the **rule** and not
build the **store** — the third session had shown the byte win of positions is smaller than it
looks (`evaṁ me sutaṁ` draws 212 of its 663 candidates and needs their text anyway), and there
are no logs saying anyone types the `dhamm* ti` kind. Tokenising each candidate's text on the
client costs milliseconds and no bytes; a `tq/` store can be built later on the same rule if a
measured need appears, and the gate for it already exists.

**Gate red first.** `check_search.js`'s `truth()` re-stated in tokens, plus twelve assertions
on both pages: `tassa bhagavato` must count 437 in 318 paragraphs (not 527 in 379) with 1,727
apart, `kāyena vācāya` 195 in 134 (not 183 in 124) with 265 apart, and the result line must
name the rule. Red on `a1cac54f3ff2`, 12 FAIL (`check_search_red_run_2026-09-06_phrase.txt`).
The older phrase assertions (`yamakasālānaṁ antare`, the wildcard-in-phrase, the layer chip)
stayed green under the token truth, which is the table above saying the two rules coincide there.

**Then the client.** `searchcore.js`: `phraseCount(text, sets)` tokenises the paragraph with
the builder's own `_TOK` and counts runs where token *j+i* is one of word *i*'s resolved keys;
both `search()` and `legacySearch()` use it, the text regex is gone. Every result line for a
phrase now ends `· consecutive words · exact diacritics` (i18n `s_consec`, en and es); the help
text on both pages says a comma or a closing quote between the words does not break the
phrase. The gate's counts agree with `measure_phrase_semantics.py`'s — two implementations, one
answer. `perf_search` unchanged (same candidates read); every other gate green.

**What changed for a reader.** Counts on phrases where a word bled into a longer token fall
(`tassa bhagavato` 527 → 437); counts where the edition prints punctuation inside the phrase
rise (`kāyena vācāya` 183 → 195; `dhamm* ti` 190 → 1,469 occurrences — the quotative *ti*).
`evaṁ me sutaṁ`, `bhagavā etadavoca`, `dukkhaṁ ariyasaccaṁ` are unchanged.

**Not done.** The position store. The phrase path still reads every candidate paragraph;
the numbers in the third session's note are still the cost of building one.
