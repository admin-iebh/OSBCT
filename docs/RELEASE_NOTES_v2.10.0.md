# v2.10.0 — a phrase is consecutive words; two more files stop being downloaded whole

*Released 6 September 2026. 118 volumes, 89,512 paragraphs — **unchanged**.*

**No text changed in this release.** The corpus figures are identical to v2.9.0. Anyone
citing the corpus can treat v2.9.0 and v2.10.0 as the same text. What changed is what a
phrase search counts, and how much a search costs to ask.

## A phrase is consecutive words

Until now a phrase was counted as a **substring of the paragraph's text**. That counted
*tassa bhagavato* inside *etassa bhagavato* — 63 paragraphs that are not the phrase — and
refused *dhammā”ti* for `dhammā ti`, because the edition closes the quotative particle up
against its word and the substring wanted a space between them.

A phrase now matches as **consecutive tokens**: each word matches a token the way the
single-word search matches it (an exact key, or a wildcard over keys), and the words must
follow each other, whatever punctuation the edition prints between them. Every phrase result
line names the rule beside the diacritics mode: `· consecutive words · exact diacritics`.

Counts move in both directions. Measured over all 89,512 paragraphs (paragraphs / occurrences):

| phrase | v2.9.0 (substring) | v2.10.0 (tokens) |
|---|---:|---:|
| `evaṁ me sutaṁ` | 494 / 510 | 494 / 510 |
| `bhagavā etadavoca` | 380 / 416 | 380 / 416 |
| `tassa bhagavato` | 379 / 527 | 318 / 437 |
| `atha kho bhagavā` | 875 / 1,327 | 865 / 1,314 |
| `sabbe saṅkhārā` | 166 / 280 | 161 / 272 |
| `kāyena vācāya` | 124 / 183 | 134 / 195 |
| `dhamm* ti` | 168 / 190 | 1,016 / 1,469 |

`pipeline/measure_phrase_semantics.py` in the deposit computes both rules for any phrase.

A **position store** — postings carrying word positions, so adjacency could be decided
without reading the text — was measured and deliberately not built: it would have answered
this rule, and the rule could be applied to the text the page already reads at no cost in
bytes. The numbers for building one are recorded should a need appear.

## Two more files stop being downloaded whole

* A substring search (`amakasālāna`) or a `*`-suffix search (`*vaggo`) used to download the
  whole key list — 682,010 keys, 12.5 MB — and scan it. It now reads **one n-gram shard**
  (`index/tg/`, 2,841 files) holding the keys that contain the query's cheapest gram, and
  verifies each key itself; 928 query × mode combinations against the old path, 0 differences.
* The section names — 16,998 printed headings, 1.09 MB — were fetched whole by both search
  pages before their first query. They are now read as **one shard** (`index/tn/`, 890 files)
  in the same way; 1,712 combinations, 0 differences. The first search of a visit moves 1.2 MB
  instead of 2.3 MB.

The largest file any search fetches is now 514 KB, and `pipeline/perf_search.js` fails if
that ceiling is crossed.

## Also

A ↑ button on the search page returns to the top of a long result list.

## Gated

Every new assertion in `pipeline/check_search.js` was made to fail on the previous build
before the change that satisfies it — the phrase rule (12 assertions), the section names (16),
the sweep (5, and two rows of the performance gate) — and the red runs are recorded in the session notes under `claude/`.
