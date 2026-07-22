# Corpus-wide cross-layer linking

Built from the concordance (which volumes pair) + the interval model (which paragraphs
pair within a pair). Output: `links_all.json`, keyed by concordance group.

## Coverage

| | |
|---|---|
| Canon paragraphs total | 49,454 |
| Linked to a commentary | 46,646 (94%) |
| Linked to a subcommentary | 24,446 (49%) |
| Groups with a commentary | 22 — **14** at ≥90% coverage, 8 below |

Each canon paragraph gets a `direct` / `covered` / (absent) state for both commentary and
subcommentary, with the exact target paragraph ID and printed page.

## What the coverage confirms

- **Milindapañha: 0%** commentary — correct, it has none.
- **Abhidhamma shared block: 100%** — all 13,728 canon paragraphs across ten volumes link
  to the single Pañcapakaraṇa commentary and its one subcommentary.
- **Khuddaka subcommentary: 0%** across most groups — correct, only Netti has a ṭīkā.
- **Jātaka, Apadāna II, Paṭisambhidā: 100%** commentary coverage.

## Low-coverage groups — cause identified, not mysterious

A handful link below 90%: Saṁyutta (47%), Cūḷaniddesa (34%), Dīgha Mahāvagga (71%),
Netti (64%). The cause is the sutta-name join, not missing text:

- **Name variants** between layers — canon `pāyāsi` vs commentary `pāyāsirājañña`.
- **Missing running-head context** — paragraphs on pages before the first running head
  have no sutta assigned, so they can't match by sutta name.

Both are the **canonical sutta-name table** already on the deferred list. Building it —
one reconciled name per sutta per volume, variants recorded as errata — is what lifts
these groups. The linking machinery itself is sound; it's the join key that needs the
name table underneath it.

## Note on granularity

For Vinaya and the shared Abhidhamma block, the concordance only pairs at cluster level
(one commentary covers many canon volumes). Linking there rests entirely on sutta/section
names within the cluster, so its precision is bounded by how cleanly those names align —
another reason the name table matters most for exactly these texts.
