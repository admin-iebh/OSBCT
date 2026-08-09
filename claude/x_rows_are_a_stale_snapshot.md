# The X-rows are not errata — they are sightings in a stale snapshot

**2026-08-09, while applying the reader's review-sheet verdicts.**
Measured before writing anything. Nothing was applied from these rows, and
**no `E078+` register entries were opened.**

## What the apply table planned

`_review/apply_table_2026-08-09.json` ends: *"X-rows need NEW register entries
(E078+)."* Eight of the nine X-rows were judged class A — "the served text
already carries the reader-confirmed reading" — and the plan was to record them
in `data/errata.json` as confirmed errata of the printed edition.

## What the measurement says

**Not one of them is an erratum of the edition, and not one of them is a defect
of the served text.** The Unicode PDFs read correctly at every site.
`pdftotext -layout` over the volumes the build itself reads:

    08DiA02   'āyuparimāṇaṁ hotīti ved'          (X001)
              'cakkhuviññāṇaṁ na jāyati'          (X002)
              'sabbaññutaññāṇena assosi'          (X006)
    12DiT05   'Ḍayhantu vāti pete sandh'          (X008)
    27Khu10   'Ḍahantaṁ1 bālamanveti, b'          (X009)
              'Ḍahantaṁ = Dahantaṁ (Sī,'          — the edition's own apparatus,
                                                    confirming the capital Ḍ

The corrupt forms — `āyuparimān\x8fṁ`, `qayhantu`, `qahantaṁ` — occur **only**
in `corpus/`, and `corpus/` is:

* **gitignored** (`.gitignore:11`, "working directories that duplicate data now
  published under `site/` and `data/`"),
* last written **2026-07-29**, against `site/*.json` rebuilt **2026-08-09**,
* and the sidecars that fed these rows into the sheet
  (`corpus/*.errata.json`, read by `build_glyph_review.py:73`) are dated
  **2026-07-21**.

So the X-rows are three-week-old sightings in a working snapshot the pipeline
has since superseded. Recording them as errata would put nine entries in the
register describing a file nobody serves and git does not keep.

## Two distinct causes, both already fixed upstream

1. **`n` + U+008F → `ṇa`** (X001–X006, all 08DiA02). A *displaced dot*, not a
   substitution: the control byte carries the retroflex dot that belongs under
   the `n`, and a vowel goes missing with it. The 2026-07-21 extraction dropped
   the byte and kept `nṁ`; the current one reads `ṇaṁ`.
2. **`q` → `Ḍ`** (X008, X009). Decoder divergence, not a glyph fault at all —
   the sheet's own note records that `pdftotext` returned `q` where `pymupdf`
   returned `Ḍ` on the first run, which is why `build_glyph_review.py` grew
   glyph-free needles. The current text layer reads `Ḍ` under both.

## The correction this makes to the handoff

`_review/apply_table_2026-08-09.json` states the convention as: *"`corpus/*.txt`
KEEPS the printed (corrupt) reading by principle 3."* **That is the right
observation with the wrong reason, and the wrong reason is load-bearing.**

`corpus/*.txt` keeps the corrupt reading because it is stale and unpublished,
not because a principle protects it. Principle 3 forbids correcting **the
edition**; it has no bearing here, and `build_khu_volume.py:4664` says so in as
many words — *"THIS IS NOT 'correcting the edition' … the edition prints
`Pāyāsivagga`; the CONVERSION lost the `ā`."* What is restored is the edition's
own reading.

The part of the convention that **is** true and does matter: the pair must live
in `data/glyph_errata.json`, because that is where the correction is applied —
over the PDF text layer, before extraction (`pdf_pages()`), guarded by a FATAL
check that every declared substitution is actually present in the printed text.

## Disposition

* X001–X006, X008, X009: **closed by measurement, no register entry.**
* X007: still unanswered by the reader, and now also suspect for the same
  reason — check it against the live PDF before asking again.
* **`corpus/*.errata.json` should stop feeding the review sheet**, or the next
  sheet will re-raise these nine sites. Either refresh the snapshot or have
  `build_glyph_review.py` read the served text. Left for the reader to choose;
  the hazard is recorded, not silently patched.

> **A census over a stale artifact measures the artifact, not the edition.**
> This is the same shape as E021 four hours earlier — a census glyph that was
> the *edition's* own mark — and the same remedy caught both: go and look at the
> printed page.
