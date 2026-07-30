## THE CORPORA ARE CLEAN — 38 GLYPH SUBSTITUTIONS IN 27 VOLUMES, AND A VERDICT OVERTURNED (2026-07-30d)

`_charcensus/census.py` over all 118 corpora now returns:

```
distinct 0 | occurrences 0 | volumes touched 0
```

It returned 89 places in 49 volumes this morning. Nothing was guessed to get there.

### !!! THE REGISTER'S OWN VERDICT ON ITS THREE HARDEST CLASSES WAS WRONG

This is the finding, and it is worth more than the fixes. The register had written off
`Ù`, `ò` and `−` — 29 of the 89 places — because it had asked *what does this character
stand for* and got no consistent answer:

| class | the verdict this project published | what is true |
|---|---|---|
| `Ù` | MIXED — do not apply without a page check | a NEIGHBOURHOOD fault; settled |
| `ò` | MIXED — do not apply without a page check | a NEIGHBOURHOOD fault; settled |
| `−` | *"a substitution table cannot repair this; the passages must be reset from the page"* | repairable at WORD level, with witnesses up to 112 volumes |

**The character was never the whole fault.** Where the vowel degraded, the retroflex or the
doubled stop beside it degraded with it — so a single-character substitution produces a word
that does not exist, and looks like evidence that the class is unresolvable:

```
vòṭthānasammutiṁ -> vuṭthānasammutiṁ    0 volumes   <- ò->u alone
                 -> vuṭṭhānasammutiṁ    1 volume    <- ò->u AND ṭth->ṭṭh
patÙmaṇḍitaṁ     -> patimaṇḍitaṁ        0 volumes   <- Ù->i alone
                 -> paṭimaṇḍitaṁ       18 volumes   <- Ù->i AND t->ṭ
```

Read as a WORD instead, the `−` class — the one declared unfixable — is the best-witnessed
of all: `ñāṇaṁ` in **112** of 118 volumes, `ārammaṇaṁ` **97**, `viññāṇaṁ` **96**,
`daṭṭhabbo` **89**, `akaraṇato` **69**, `māṇavo` **69**. Twelve of the fourteen corpus
places are witnessed outright; the other two by their halves (`padaṭṭhāna` 57 +
`kāraṇattā` 46; `ārammaṇādhipatipaccaya` 6).

### THE METHOD: THE CORPUS IS ITS OWN LEXICON

The decisive test for a proposed emendation is **how many of the 118 volumes print the
emended word**. This is not a dictionary — the project instructions bar a lexicon as a
source of analysis — it is the edition being asked about its own usage. A reading printed
in 112 volumes is not a conjecture. A reading printed in 0 is refuted, however plausible
the character substitution behind it looked.

`_charcensus/propose.py` derives the candidate and reports the witness count. It does not
apply anything.

### WHAT WAS APPLIED

`_charcensus/apply_fixes.py --write` — a **declared table of 38 rows**, each
`(volume, from, to, witness, min_volumes)`, which **refuses on any mismatch**. 38
substitutions in 27 volumes; 162 of 182 register sightings now carry `apply_from`/`apply_to`.

Dissenting places were applied as they read, not as the majority reads:
`Aòjalī`→`Añjalī` (20Khu03, a proper name in an uddāna) is ñ where the class is u;
`PavesanapavÙṭtha`→`…pavuṭṭha…` (07ViT07) is u where the class is i; 22Khu05's `(Sī, Ù)`
was left alone, because it is a **variant siglum and not a letter**.

Also settled: `⎯` (U+23AF) → `–` in 04Vin04, on the count that the volume prints `–` 216
times and `⎯` twice; and `é`, which was MIXED for the right reason and the wrong
conclusion — two places, two readings, two fixes (`passémi`→`passāmi` 07Di02,
`viharāmé`→`viharāmi` 15An01).

### THE 20 UNAPPLIED SIGHTINGS ARE NOT OPEN FAULTS

17 are PDF-text-layer sightings of matter **the corpus never carried** — `¥` ×8 (all-capital
title lines), the combining-dot places ×7 (NFC, not a wrong glyph), `−` ×1, `Ù` ×1
(02Vin02's `PiÙṭhaṅkā`, in a word index). 3 are **SUBSUMED**: `buddhañān−ṁ` is broken across
a line in the printed text layer, so the builder rightly refused the declaration — and the
shorter `ñān−ṁ`→`ñāṇaṁ` row repairs the place anyway, because it is a substring. Corpus
verified: 18AnT01 reads `buddhañāṇaṁ`, and carries no U+2212 at all.

`register.py` now DERIVES the applied count from the entries rather than believing the
proposal's own `applied` field. That correction alone moved the published figure from
**165** to **162** — the earlier number was generated before the three subsumed rows were
cleared, and it flattered the work by three.

### !!! THE REGRESSION HARNESS NEEDED A NAMED EXEMPTION, AND WHY THAT IS HONEST

`pipeline/regress.py` compares against the baseline builder
`build_khu_volume.py.preniddesa`, which contains **0** occurrences of `GLYPH_ERRATA` — it
has no register mechanism at all and can never reproduce an applied glyph fix. Re-baselining
fixed 26Khu09; it could not fix 20Khu03, whose uddāna and verse maps carry
`Aòjalī`→`Añjalī`. Rather than weaken the comparison, two named exemptions were added:

```python
EXEMPT = {('20Khu03', 'uddana'): 'applied glyph erratum Aòjalī -> Añjalī; '
                                 'the baseline builder has no register',
          ('20Khu03', 'verse'):  'same place, same reason'}
```

`regress check` prints `EXEMPT …` on every run and reports `53/55 … 2 exempt (named above)
[OK]`. **An exemption that is printed is a different thing from a test that was loosened.**

### GATES AFTER

* `check_layout` 15An01, 20Khu03, 26Khu09, 32Abhi04 — **4 clean, 0 layout issues**
* body gate 18AnT01 8/6/16 (the known hyphen class), 19AnT02 0/1/0/0 (the declared splice)
* all 27 touched volumes' side-maps rebuilt, every one `[OK]`
* `build_pagespan.py` re-run for the 26 corrected volumes
* `stamp_build.py --write` → BUILD **`e2cf8320f2bf`** (was `c59b762ad019`)

### A SLIP TO KNOW ABOUT

`cp site/X.json _khua/corpus_pre/X.json` — **that directory does not exist**, and because
the commands were `;`-chained the later `cp`s ran anyway and overwrote `site/` and `corpus/`
for the three Abhidhamma Ṭīkā with no pre-image. Recovered from `git show HEAD:site/<VOL>.json`
and verified identical on paragraph count, character count and page range; one paragraph
differed by a glyph correction already registered (24AbhiT03 ord241 `Nènā-`→`Nānā-`).
**The pre-image directory is `_fnprobe/corpus_pre/`.** Use `&&`, and check the directory first.

