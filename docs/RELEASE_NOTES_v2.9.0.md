# v2.9.0 — search matches diacritics exactly, and stops downloading the canon

*Released 5 September 2026. 118 volumes, 89,512 paragraphs — **unchanged**.*

**No text changed in this release.** The corpus figures are identical to v2.8.0. Anyone
citing the corpus can treat v2.8.0 and v2.9.0 as the same text. What changed is how the
search answers, and how much it costs to ask.

## Diacritics are matched exactly

In Pāḷi *tassa* and *tassā* are different words. Until now every search key was **folded**
(*tassā* stored as *tassa*), so a search for either word reported both: 36,644 occurrences
where *tassā* alone has 4,322. Measured over the whole corpus, 34,134 folded keys (5.3%) were
merging two or more printed forms — and they are the common words.

The index now stores the printed tokens (NFC, lower case, the modern ṃ written as the
edition's ṁ) and matches them by identity. Folding is offered as a switch, **"Ignore
diacritics"**, off by default and remembered per browser; every result line ends with the mode
that produced its count (*exact diacritics* / *diacritics ignored*), and a miss in exact mode
offers the switch rather than folding silently. Section names are matched in the same mode.

With the switch on, counts reproduce v2.8.0's exactly. One deliberate difference: a wildcard
matching more than 500 forms is cut to the 500 *commonest* forms, deterministically, and the
result line says so — previously the cut was in bucket order, and `dhamm*` could answer
88,895 or 4,822 depending on which forms happened to come first.

## The search no longer downloads the canon

Measured on the live site before this release: counting one common word fetched 117
per-volume index files — about 40 MB compressed, 190 MB parsed, 4.2 s on a fast link and a
freeze on a phone — because postings and paragraph text shared a file. Postings now live in
1,031 prefix shards (one fetch counts a word across all 118 volumes) and the text in 1,008
chunks fetched only for the rows drawn. The same search moves 2.3 MB. `site/searchcore.js`
is the one implementation behind both the search page and the reader's box.

`pipeline/perf_search.js` is a new performance gate; the pre-release numbers are kept in
`pipeline/perf_baseline_2026-09-05_before.json`.

## Dictionary panel

Four round trips instead of six per lookup, and the serving origin is now cached at the edge
(measured: every file `HIT` on the second request). No store changed.

## Gated

The new assertions in `pipeline/check_search.js` were made to fail on the v2.8.0 build before
the index was rebuilt (`anīkaratto` 9 → 6, `tassā` 36,644 → 4,322, no switch), and pass now,
legacy fallback included.
