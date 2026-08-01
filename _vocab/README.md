# _vocab — roadmap step 1, the vocabulary measurement

2026-08-01. Read-only measurement over `site/<VOL>.json` (118 volumes). It writes
nothing into `site/` and imports no nav builder, per dictionary_roadmap Appendix A.7.

    python3 tokenise.py    # census + frequency tables            (~50 s)
    python3 verify.py      # independent recount, must print PASS (~40 s)
    python3 report.py      # final figures + freq/ shards          (~60 s)

`tokenise.py` walks the string character by character; `verify.py` tokenises the
same corpus with a regular expression and requires the two multisets to be
identical. That check is not decoration — it caught a real bug in `tokenise.py`
on the first run (the edition encodes its elision mark as both U+2019 and U+0027;
only the first was being treated as word-internal, splitting 199 forms apart).

`freq/` is the sharded frequency table: `index.json` plus 1,119 shards keyed by
the shortest prefix of the site's own `fold()` that names a shard (try depth 2
upward). Row = `[total, canon, commentary, subcommentary, dpd_tier]`.

**No dictionary content is in any of these files.** DPD v0.4.20260728 was used as
a membership test — *does this string occur in the inflected-form list* — and
nothing from it is shipped or shown. `dpd_tier` records which tier of that test a
form reached; it is a coverage statistic, not a lemma.

`glyph_erratum_candidates.json` — 8 non-Pāḷi Latin letters found by the character
census. **Candidates, not applied.** Check each against the printed page before
anything goes into `data/glyph_errata.json`.
