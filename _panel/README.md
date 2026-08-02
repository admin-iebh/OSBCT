# _panel — word-lookup panel PROTOTYPE (pilot volume 09Ma01)

2026-08-01, built in a Cowork cloud session. **Standalone pilot: nothing here
touches `site/`.** Dictionary roadmap step 2's shell, piloted with real data
from every source at once so they can be compared.

    cd _panel
    python3 -m http.server 8931      # fetch() does not work from file://
    open http://localhost:8931/

Click any word. Caret-based recovery (no per-word spans, roadmap §5); a glued
apparatus digit is stripped; the elision mark joins (`Tāni’ssa`).

**Recursive lookup:** clicking a Pāḷi word *inside* the panel looks it up too,
keeping the paragraph context for proximity; a ‹ back button returns. It fires
only when the pilot dataset has something for the word — the shards cover the
pilot volume's vocabulary, so words that occur only inside dictionary entries
are silent no-ops (corpus-wide data removes this limit at integration).

## The tabs — sources are never merged (principle 4)

| tab | source | status |
|---|---|---|
| **DPD** (default) | Digital Pāḷi Dictionary, GoldenDict build 2026-05-01 | **EVALUATION ONLY.** Marked with a banner. Decided 2026-08-01: no DPD gloss ships (§9 + CC BY-NC-SA). What survives to integration is its form→lemma resolution (the permitted filter use), its per-form grammar table, and the deconstructor — shown as unranked alternatives. |
| **Abhidhāna** | Tipiṭaka-Pāḷi-Myanmā-Abhidhāna, Burmese text with citations intact — `pm12e.csv` (2020-12-09) from `bksubhuti/Tipitaka-Pali-Projector` `legacy/pm12e.zip` | The lexical authority (§9). Citations are passed through as printed, **plus a transcoded roman line** (closed abbreviation set; Burmese digits incl. ၎=4 and letter-ဝ=0 in digit runs; unknown abbreviations left in Burmese, never guessed). Each entry carries an **"English (PEU) ⇣" reveal** showing PEU's rendering inline — attributed, machine-marked entries labelled as such on the button itself. |
| **PEU** | PEU StarDict 2024-02-24 (encoded by Bodhirasa) | Attributed as *English rendering of the Abhidhāna*, never as the authority. Entries carrying the literal `Google Translate` marker are **withheld behind an explicit reveal**, never mixed (55,767 of 200,456 corpus-wide). |
| **CPED** | Concise Pali English Dictionary (A.P. Buddhadatta) — local StarDict, 21,099 entries | Modern lexicon: reference tab, §9 filter side. Tooltip carries the full name (the dictionary's own metadata says *Concise*, not *Critical*). |
| **DOP** | Dictionary of Pāli by Margaret Cone — local StarDict, 37,391 entries (identical count to the other-dictionaries dump) | Modern lexicon: reference tab. The digitisation is **partial by letter** (a/k/p rich; m has 2 entries, s 418, y/r/l ~1 each) — an absent DOP tab is usually the digitisation's gap, not the join failing. Homonyms shown numbered. |
| **PPN** | Dictionary of Pāli Proper Names (G.P. Malalasekera) — `DPPN.json` from `digitalpalidictionary/other-dictionaries` **v1.0.8** (13,642 entries) | Modern lexicon: reference tab. Chosen over the local StarDict PPN, which carries only 1,367 entries. |
| **Edition** | `_gloss/` step-3 rows — the edition's own bold+`-ti` glosses | **Proximity first**: rows from the commentary/ṭīkā paragraph the existing link map ties to the canon paragraph clicked, then the rest. `truncated` rows say "continues in the text". Pilot data: the 7 Majjhima aṭṭhakathā/ṭīkā volumes only (19,718 rows). |

Corpus counts in the header come from `_vocab/freq/` (step 1).
Unresolved forms get the §4 treatment: *"not resolved — occurrences only"*,
never a confident wrong lemma.

## Files

- `build_panel_data.py` — builds `data/` (~112 MB, generated; keep out of git
  like `_vocab/freq/`). Needs: `site/09Ma01.json` + links, `_gloss/by_volume/`,
  `_vocab/freq/`, the GoldenDict StarDict dirs (peu, dpd, dpd-grammar,
  dpd-deconstructor, 00-CPED, 02-DOP), `pm12e.csv`, and `dppn/DPPN.json`
  (from other-dictionaries v1.0.8). `PANEL_SRC` env points at the dir that
  holds them. Its tokeniser replicates `_vocab/tokenise.py` and is verified
  against a second code path at run time (same discipline as `verify.py`).
- `index.html` — the prototype page, self-contained. Chrome strings are
  collected in `STR{}`; at integration they go through `i18n.js` (§7).
- `gate.py` — **the gate that opens the panel** (roadmap §6). Clicks a
  stratified sample of words in real Chromium and asserts the display against
  the data files: header word, corpus count, per-tab counts, §4 unresolved
  honesty, machine-translation segregation, source separation.
  Run: server up, then `python3 gate.py`. Last run: 38 words, 0 failures
  (and a negative control confirmed the assertions fire).
- `shot.py` — screenshot/interaction probe at real device dimensions.

## Measured layout facts (Chromium, not reasoned)

- ≥ ~1140px is what three columns actually need: 46rem text (736px) + 400px
  panel. At 950px the text column is squeezed to 550px.
- ≤ 900px the panel is a bottom sheet (60vh) — measured at 390×844: sheet
  opens over the text, clicked word stays visible, tabs and chips usable.
- **Integration note:** the real reader's left pane becomes an overlay below
  861px. A right side-panel therefore only fits the reader at ≥ ~1140px;
  between 861 and 1140 the bottom sheet is the only honest layout.

## Not in this pilot

PTS/PED tab (needs its own verification pass), lemma-level occurrence links,
per-gloss page numbers (a corpus change — rows carry the paragraph's range),
gloss rows from the other 82 volumes, `05Kankha` layer decision, and the
definition-vs-comment row classification (open item from step 3).
