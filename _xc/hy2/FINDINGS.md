# The hyphen-space break, and a live corruption in the cross-reference apparatus

2026-08-05, continuing from `_xc/hy1/FINDINGS.md`. Working record `_xc/hy2/`.
**No data touched, no builder changed. Nothing run with `--write`.**

Starting point: `_xc/hy1/FINDINGS.md` §10.4 — 8,790 occurrences of a line-break hyphen
followed by a space *inside a word*, across 109 volumes, controlled at 296/300 against the
printed page. Its proposed repair was to route the bypassed join paths through `hyjoin`.

## 1. Re-measured, and the count stands

`_xc/hy1/hyspace.py` on the current corpus: **8,790 across 109 volumes**, unchanged.
`_xc/hy2/classify.py` counts 8,812 because its regex also admits an uppercase continuation,
which `hyspace.py` excludes; the 22 difference is that and nothing else.

## 2. §10.4's repair is NOT safe as written

`hyjoin` decides a line-end hyphen three ways: peyyāla → keep and space off; next letter a
**vowel** → keep the hyphen and close up; **otherwise → DROP the hyphen** and close up.
Split by which branch would take them:

| | | |
|---|---:|---:|
| next letter a VOWEL — hyphen kept | **7,291** | 82.7% |
| next letter a CONSONANT — hyphen **dropped** | **1,521** | 17.3% |

The consonant branch is where it breaks. The edition sets a real hyphen before a consonant
in the grammatical citation form — `ca-saddo` "the word *ca*", `vā-saddo`, `ādi-saddena`,
`saṁ-saddo`, `da-kārassa` "of the letter *da*". Routing those through `hyjoin` yields
`casaddo`, `vāsaddo`, `dakārassa`.

`01ViT01` p40 makes the case by itself: it prints `ettha vā-saddo padapūraṇe` **mid-line,
hyphen intact**, and two clauses later wraps the same construction, leaving `Vā- saddo` in
the corpus. Same volume, same word, one form correct and one broken.

### 2.1 The discriminator, and it comes from the page

`_xc/hy2/discrim.py`. Not a word list and not the corpus:

> A **soft line-break hyphen exists only at a line end.** The **edition's own** hyphen also
> occurs **mid-line.**

So close the two halves up with the hyphen kept and ask whether that token appears anywhere
in the volume's printed line stream away from a line end. On `01ViT01`: **6 of 17** consonant
cases are confirmed edition hyphens — `ca-saddo`, `Vā-saddo`, `ādi-saddena`, `saṁ-saddo`,
`Ādi-saddena` — and the other 11 are long compounds with no mid-line witness.

**It is high precision and low recall, and that is a limit, not a result.** `ca-saddassa`,
`Go-saddena` and `atthi-saddo` are plainly the same construction and get no witness, because
the *inflected* form does not happen to occur mid-line. `51Vism01` returns 103 of 103
without evidence. **The test finds edition hyphens; it does not clear the rest.** The
outcome is deliberately three-valued and `unknown` is reported, not defaulted.

*(Two defects of my own in the first version, both corrected: the candidate carried a doubled
hyphen, and the comparison was case-sensitive — the continuation half is usually line-initial
and therefore capitalised, so `Vā-saddo` missed a mid-line `vā-saddo` and the KEEP count was
zero.)*

## 3. RETRACTED — §3 as first written was my matcher, not the corpus

> **The whole of §3 below was wrong and is kept as the record of the error.
> The corrected measurement is §3A.**

I reported **111 live corruptions across 28 volumes, 77% of them the `-Ṭṭha`
cross-reference siglum**, and said it blocked requirement 2. **None of that was true.**

`livecheck.py` asked `closed.casefold() in body.casefold()` — a **substring** test. Every
`-Ṭṭha` hit was a substring of an ordinary word: `UdānaṬṭha` casefolds to `udānaṭṭha`, which
sits inside **`Udānaṭṭhakathāyaṁ`** — *Udāna-aṭṭhakathā*, sandhi-joined, exactly as Pāḷi does
it and exactly as the edition prints it. `09DiT02` contains the string `UdānaṬṭha` **zero**
times as a token and five times as a fragment of that ordinary word.

This is the project's own recurring failure, made by me: a count taken over the corpus and
reported before the thing counted was looked at. The check that caught it was opening one
occurrence and reading its context — which should have come before the sweep, not after.

## 3A. Corrected, on WHOLE TOKENS

`livesweep.py` now matches against the token multiset of the paragraph text.

| | first (substring) | **corrected (token)** |
|---|---:|---:|
| volumes affected | 28 | **10** |
| distinct words | 62 | **13** |
| occurrences | 111 | **18** |
| of which the `-Ṭṭha` siglum | 86 | **0** |

`_xc/hy2/live/` holds the wrong run and `_xc/hy2/live2/` the corrected one; both are kept,
the first as the negative control it should have been.

What actually remains is small and ordinary:

| word, as the page sets it | in the corpus | |
|---|---|---:|
| `dhamma-saṅgītiyā` | `dhammasaṅgītiyā` | 7 |
| `Buddha-bhāsitaṁ` | `Buddhabhāsitaṁ` | 6 |
| `Kasi-vāṇijjā`, `puññakaro-hamasmi`, `Micchādiṭṭhika-tivedī`, `Dubbā-sara-bhūtiṇakādīnaṁ`, `Veḷuriyaka-rodāyoti` | | 1 each |

**18 occurrences is not a corpus-wide fault and does not block anything.** Each needs a page
read before it is even called a fault — the same compound may legitimately appear hyphenated
in one place and closed up in another, and this test cannot tell those apart. **The claim
that the cross-reference apparatus is being corrupted is withdrawn in full.**

## 3B. What §3 was, before the retraction

If the consonant branch is wrong, it is wrong wherever `hyjoin` **runs** — not only on the
paths that bypass it. Test (`_xc/hy2/livecheck.py`, swept by `livesweep.py` → `_xc/hy2/live/`):
for every hyphenated token the **page** sets mid-line, does the **corpus** carry it with the
hyphen removed, and never with it?

**117 volumes measured. 28 carry corruption: 62 distinct words, 111 occurrences.**

| word, as the page sets it | in the corpus | |
|---|---|---:|
| `Dhammapada-Ṭṭha` | `DhammapadaṬṭha` | 19 |
| `Udāna-Ṭṭha` | `UdānaṬṭha` | 18 |
| `Jātaka-Ṭṭha` | `JātakaṬṭha` | 13 |
| `Suttanipāta-Ṭṭha` | `SuttanipātaṬṭha` | 12 |
| `Khuddakapāṭha-Ṭṭha` | `KhuddakapāṭhaṬṭha` | 9 |
| `Buddha-bhāsitaṁ` | `Buddhabhāsitaṁ` | 9 |
| `dhamma-saṅgītiyā` | `dhammasaṅgītiyā` | 7 |
| `Vimāna-Ṭṭha`, `Itivuttaka-Ṭṭha`, `Cariyāpiṭaka-Ṭṭha`, `Therīgāthā-Ṭṭha`, `Abhi-Ṭṭha` … | | |

**86 of the 111 — 77% — have `-Ṭṭha` as their right half.** That is the **Aṭṭhakathā siglum
of the footnote apparatus**: project instructions §5 lists `Ṭṭha` among the variant sigla and
gives `(Aṃ-Ṭṭha 1. 72 piṭṭhe)` → Aṅguttara *commentary*, vol. 1, p. 72 as a
machine-extractable printed cross-reference.

So whenever a footnote citation wraps at a line end, the builder deletes the hyphen and
`Udāna-Ṭṭha` becomes `UdānaṬṭha` — **a citation the extraction pattern can no longer match.**
This is upstream of requirement 2 and it is in shipped text now.

Worst volumes: `10DiT03` 23, `09DiT02` 19, `01ViT01` 11, `35KhuA16` 7, `03ViT03` 6.

**Scale, stated honestly:** 111 occurrences is small beside 8,790. It matters not for its
size but for *what* it is, and because it is a defect in the live builder rather than in a
path the live builder never takes.

## 4. What the repair should be

One mechanism answers §2.1 and §3 together, and it consults the page rather than a list:

> Harvest, per volume, every hyphenated token the printed stream sets **mid-line** — where
> the hyphen cannot be a line-break artefact. `hyjoin` consults that set before its consonant
> branch and keeps the hyphen on a hit.

This covers all 111 of §3 by construction, covers `discrim.py`'s KEEP set, needs no word
list, and adds no rule the edition has not itself demonstrated. It leaves `unknown` alone.

## 5. Order of work, and what is NOT established

1. **The vowel branch, 7,291 (82.7%).** Applying `hyjoin` to the bypassed paths introduces
   **no new rule** — it applies the builder's existing, shipped decision to lines that
   missed it, and no counter-evidence to it has been found. This is the safe majority.
2. **§3's 111**, with the mid-line set. Small, bounded, and it is the one that blocks links.
3. **The consonant branch's remaining ~1,400.** `discrim.py` clears a minority and leaves
   the rest genuinely open. **Not adjudicated, and not to be swept into either branch.**

**Not established here:** that the vowel branch is right in every case — only that it is the
builder's own existing rule and that nothing contradicts it; and any number for how many of
the 1,521 are edition hyphens. Nothing has been repaired.

## 6. The bypass site is located, and it is NOT in `build_khu_volume.py`

`pipeline/extract.py:204`, the paragraph accumulator:

```python
elif cur is not None: cur['text']+=' '+st
```

**A plain space, with no hyphen decision of any kind.** That is where all 8,790 come from,
and it confirms §10.4's diagnosis while correcting its location: the fault is not that
`hyjoin` was skipped on one of `build_khu_volume.py`'s paths, but that the **paragraph text
is built by a different module that has no `hyjoin` at all.**

The two layers divide cleanly:

| artefact | built by | hyphen handling |
|---|---|---|
| `site/<VOL>.json` `paragraphs[].text` | `pipeline/extract.py` | **none** |
| `site/reader/verse/<VOL>.json` drawn lines | `pipeline/build_khu_volume.py` | `hyjoin`, 11 call sites |

### 6.1 A blocker that must be settled before any repair

`pipeline/README.md` states plainly:

> "Several auxiliary scripts (font injection, index build, apparatus attachment, concordance
> parsing, link generation) **were run in a scratch environment and are being consolidated
> back into this directory.** … The published corpus does not depend on re-running them."

So it is **not established that `extract.py` as it stands regenerates the shipped
`site/<VOL>.json`.** Patching line 204 is worthless — or worse — if the file that produced
the corpus is not this one. **Establish reproducibility first**: run `extract.py` on one
volume and diff its paragraph text against the shipped `site/<VOL>.json`. If it does not
reproduce, the repair is a migration problem before it is a hyphen problem, and that is a
different and larger job than §10.4 implies.

Nothing has been patched, and this is the reason.

## 7. Reproducibility measured over all 118 volumes — and the answer changes the repair

`_xc/hy2/repro.py` / `repro_sweep.py` → `_xc/hy2/repro/`. Compared two ways, because the
first way alone is misleading: paragraph text **at the same index**, and paragraph text
**present anywhere** in `extract.py`'s output.

| | |
|---|---:|
| identical at the same index (text AND segmentation) | **25** |
| text coverage 100% | 25 |
| text coverage 95–100% | **32** |
| text coverage 50–95% | **56** |
| **text coverage under 50%** | **5** |
| paragraph-count mismatch | 83 |

**The same-index figure is the wrong measure and 66 volumes "failing" it is an artefact.**
`40Abhi12` scores 0% same-index and 97% coverage: the text is all there, offset by a handful
of segmentation differences. What `extract.py` no longer reproduces is the **paragraph
segmentation** — which is expected, because the re-segmentation work has been rewriting those
boundaries since phase 1.

Genuinely not produced at all — **five volumes**:

| | coverage | extract.py | shipped |
|---|---:|---:|---:|
| `20KhuA01` | 0.4% | 63 | 673 |
| `23KhuA04` | 1.2% | 92 | 1,029 |
| `24KhuA05` | 1.3% | 106 | 895 |
| `21KhuA02` | 3.1% | 127 | 1,010 |
| `07ViT07` | 4.0% | 18 | 420 |

Four of those five are exactly the volumes the 08-05 handoff lists as **"once unbuildable"**
and fixed at `85901cb6` with SPEC book bounds following the re-segmentation. They are not a
new mystery; they are the volumes whose paragraph set is now owned downstream.

### 7.1 So the repair is a CORPUS MIGRATION, not a builder patch

Patching `extract.py:204` and re-running would **undo the re-segmentation on 93 volumes**.
That is not a repair, it is a regression, and it is the most important thing this section
establishes.

The hyphen-space fix does not need re-extraction. It is a **pure string transformation on
`paragraphs[].text`** — delete one character — and it should be applied to the shipped
corpus in place. `extract.py:204` should still be corrected so the fault is not reintroduced
by any future extraction, but that is hygiene, not the repair.

## 8. What the migration costs: 128,054 bold spans

`_xc/hy2/exposure.py`. Bold is stored as `[start, end]` **character offsets into
`paragraphs[].text`** — verified rather than assumed: `35Abhi07` ord32 span `[3, 10]` is
exactly `Pavatti`, `[16, 26]` exactly `Uppādavāra`. Deleting a character therefore moves
every span that begins after it.

| | |
|---|---:|
| vowel-branch deletions | **7,291** in 4,612 paragraphs, 101 volumes |
| of those paragraphs, carrying bold | 4,334 |
| bold spans in them | 202,995 |
| **spans that must shift** | **128,054** |

This is mechanical and exactly determined — for each deleted index `h`, every offset `> h`
in that paragraph decrements by one — but it is 128k edits and it must be right, because a
span off by one bolds the wrong letters and **`check_bold_fidelity` compares against the
page, so it will catch it**. That is the control, and it already exists.

Peyyāla is excluded from the deletion set by construction (`-pa- ` keeps its space).

### 8.1 The order this implies

1. Write the migration as a **standalone, idempotent script over `site/*.json` plus
   `site/reader/bold/*.bold.json`**, dry-run first, reporting per volume.
2. Check whether anything **else** is keyed to text offsets — `apparatus/`, `linksk/`,
   `incipit/`, `hide/` were not audited here and **must be** before a write.
3. Run `check_bold_fidelity` old-against-new. It reads the printed page, so it is a real
   control and not a corpus-derived one.
4. Only then the 111→**18** of §3A, each read on the page first, and the ~1,400 consonant
   cases, which remain unadjudicated.

## 9. The offset audit: only `bold/` moves

`_xc/hy2/offsets_audit.py`, which decides by **slicing**, not by field name.

| artefact | holds | action |
|---|---|---|
| `bold/` | **`[start,end]` offsets** into `paragraphs[].text` — 7,540 pairs on `09DiT02`, e.g. `[0,17]` = `Sīlakkhandhavagga` | **must shift** |
| `verse/` `sections/` `uddana/` `incipit/` `booktitle/` | verbatim drawn-line strings | see §9.1 — **no change needed** |
| `apparatus/` `links/` `linksk/` `hide/` `xrefs/` `ord/` `pbreak/` | no offsets, no verbatim paragraph text | none |

### 9.1 The side-maps already hold the closed form

`_xc/hy2/sidecheck.py`. Those maps are produced by `build_khu_volume.py`, which **has**
`hyjoin`; the paragraph text is produced by `extract.py`, which has none. So the two layers
were already inconsistent:

| volume | occurrences | side-map ALREADY closed | side-map has the same break |
|---|---:|---:|---:|
| `09DiT02` | 210 | **207** | **0** |
| `22AbhiT01` | 211 | **188** | **0** |
| `01ViT01` | 140 | **79** | **0** |

**Not once does a side-map carry the broken form.** The repair does not change the corpus so
much as make the paragraph text agree with what the reader is already shown.

## 10. Read on the printed page before writing

`01ViT01` raw p20 = printed **p5** (`_xc/hy2/pg_01ViT01-020.png`), rendered and read:

```
antarāyanibandhanasakalasaṁkilesaviddhaṁsanāya pahoti, bhayādi-
upaddavañca nivāreti. Tasmā suvuttaṁ “saṁvaṇṇanārambhe
```

One word, `bhayādi-upaddavañca`, broken across two printed lines. The corpus had
`bhayādi- upaddavañca`. The same page also shows the two cases the migration must **not**
touch, and does not: the peyyāla `“yo kappa -pa- mahākāruṇikassa tassā”ti` (masked out), and
the consonant case `bhūmantarapaccayākārasamayantara- / kathānaṁ`, which needs the hyphen
*dropped* and belongs to the un-adjudicated ~1,400.

## 11. APPLIED — and a defect I wrote to the corpus and had to restore

**`_xc/hy2/migrate.py`. 7,291 deletions, 4,612 paragraphs, 101 volumes. 127,867 bold spans
shifted.**

### 11.1 The defect, and the control that caught it

The first write used a **per-paragraph fallback** for the bold key: `str(i)` if present, else
`str(p['n'])`. `50AbhiA03`'s map is **index**-keyed; paragraph index 348 carries `n=366`, has
no key `'348'`, so it fell through to `'366'` — a real key belonging to paragraph index 366 —
and that paragraph's spans were shifted by **a different paragraph's deletions**.

`check_bold_fidelity` caught it: `50AbhiA03` moved **EXACT 3018 → 3017, PART 1 → 2**. One
span in 202,995, and the gate found it.

The corpus was restored from `HEAD` before anything else was done. *(`git checkout` cannot
do it here — the sandbox cannot unlink, so restoration is `git show HEAD:<path>` written back
in place, truncate-and-write. 185 files, verified by `hyspace.py` returning to 8,790.)*

The convention is now decided **once per volume** by which mapping makes the spans slice
cleanly, with **no fallback**; a volume whose convention cannot be decided is skipped and
said to be skipped.

### 11.2 Measured, warm cache both sides

`check_bold_fidelity` on the nine most affected volumes, run twice each side because the
gate differs on a cold pdfminer cache (08-05 hazard).

| | |
|---|---:|
| **EXACT / MISS / PART / LONG / SPUR** | **unchanged on all nine — 0 metrics moved** |
| `notdrawn` | **7,435 → 2,458 (−4,977)** |

`notdrawn` is a bold run the checker could not locate in the drawn text. Closing the hyphen
makes the paragraph text agree with the side-map, so **4,977 bold runs that could not be
placed now can be**. That is an improvement the gate measured against the printed page, not
against the corpus.

Internal control, in the script and run every time: for each span the selected substring must
be identical before and after, except where a deleted space lay **inside** the span, in which
case it must equal the old substring minus that space. **0 unexplained.** The one inside-span
case corpus-wide is `04VinA04` ord160, `'tvā puna- upa'` → `'tvā puna-upa'`.

### 11.3 REVERTED. The migration breaks the builder's paragraph matching.

**`check_bold_fidelity` passing was not enough, and I nearly stopped there.** The gate reads
the shipped side-maps and the printed page; it does not ask whether the BUILDER still
reproduces those side-maps from the repaired text. It does not.

Measured by restoring one volume's pre-migration text, rebuilding, restoring the migrated
text, rebuilding, and comparing — so the two numbers differ in nothing but the repair:

| `09DiT02` | drawn lines |
|---|---:|
| shipped side-map | 2,012 |
| fresh build from **pre**-migration text | **2,012 — exact** |
| fresh build from **post**-migration text | **4,489** |
| attributable to the migration | **+2,477 (+123%)** |
| pre-existing staleness | **0** |

**Before the repair the builder reproduced the shipped side-map exactly. After it, it does
not.** And the extra lines are not a finding — they are a collapse:

```
ordinals   84 -> 81          three ordinals LOST
ord 7     144 -> 3,178       +3,034 lines, one per printed line
```

The builder failed to locate three paragraph boundaries, merged their content into ord 7, and
fell back to emitting every printed line separately. Closing the hyphen in
`paragraphs[].text` stopped the builder matching its own printed-line join. Also measured:
`01ViT01` +573, `20KhuA01` +60, `43KhuA24` −70; `35Abhi07` unchanged.

**All 185 corpus files were reverted to `481c7221` in place**, verified by `hyspace.py`
returning to 8,790 and `20KhuA01` returning to 911 drawn lines.

### 11.4 What this costs and what it teaches

`notdrawn` falling 7,435 → 2,458 was real and is now given up with the revert. It was also
**not the whole picture**, and reporting it as success would have been wrong: the same change
that let 4,977 bold runs find their place destroyed three paragraph boundaries in one volume.

**The missing control is named.** Every gate run was against the *shipped* artefacts. None
asked *does the builder still produce them*. That control now exists as a procedure and must
run on any text-level change:

> restore pre, build, restore post, build, diff the side-maps.

**The repair is not abandoned, but it is not a text edit alone.** It must be made together
with whatever in `build_khu_volume.py` matches paragraph text to printed lines, and the pair
measured as one change. Locating that matcher is the next step and is not done here.

### 11.5 State

> **CORRECTED 2026-08-07. THIS TABLE DESCRIBED A STATE THAT NO LONGER EXISTED WHEN IT WAS
> WRITTEN, AND IT CONTRADICTED §11.3 DIRECTLY, twelve lines above it.**
>
> §11.3 records that **all 185 corpus files were reverted to `481c7221`**. The "after"
> column below is the *migrated* state — the one that was reverted — presented as the
> current one. **An agent reading §11.5 alone would believe the migration is in place and
> plan from it.**
>
> **Measured 2026-08-07, twice, by two independent implementations** — `_xc/hy1/hyspace.py`
> and a separate recount written without reference to it, so a shared bug in one would not
> produce the same number in the other:
>
> | | |
> |---|---:|
> | hyphen-space occurrences **now** | **8,790 in 109 volumes** |
>
> That is the pre-migration figure exactly, which is what §11.3 says the revert restored.
> **The repair is NOT in place.** The 8,790 words are still broken, and the work remains as
> §11.3 leaves it: the text edit cannot land without the change to whatever in
> `build_khu_volume.py` matches paragraph text to printed lines, measured as one change.
>
> The original table is kept below per working principle 3. It is not wrong about what it
> measured — it is wrong about *when*.

| | before | after |
|---|---:|---:|
| hyphen-space occurrences | **8,790** in 109 volumes | **1,501** in 96 volumes |

*(The row above is the state DURING the migration, now reverted. See the correction.)*

The 1,501 remaining are the consonant branch of §2 — **not a residue, a different and
unadjudicated question**. `extract.py:204` is still uncorrected, so a future extraction would
reintroduce the fault; that is hygiene and is not done here.

## 11.6 THE BLOCKER OF §11.3 IS BROKEN (2026-08-08, second session)

The matcher §11.4 said must change with the text is the **paragraph-run placer**
(`build_khu_volume.py`, the `cnd` list in the run matcher).  On a hyphen-ended
accumulation it tried two joins — drop-and-close, keep-with-space — and the
migration's KEEP-AND-CLOSE form (`hyjoin`'s own vowel branch) was simply missing.
One candidate, appended last.

Measured as one change on 09DiT02, per §11.4's own procedure: fix alone on
unmigrated text → all five side-maps BYTE-IDENTICAL; migrate + rebuild → 84
ordinals / 2,012 lines EXACT (not 81 / 4,489), side-maps byte-identical again;
`check_bold_fidelity` warm both sides → EXACT/MISS/PART/LONG/SPUR unmoved at
5609/173/2/0/1, `notdrawn` **1,862 → 720**.  Pilot then REVERTED (hyspace.py
returns 8,790/109 — the §11.3 verification), so the corpus-wide apply can land
as ONE operation: migrate all volumes, rebuild, re-emit the search index
(terms come from the text), run every gate old-against-new, move the bold
baseline deliberately.

## 11.7 LANDED (2026-08-08, third session) — pipeline/apply_hyphen_repair.py

All of §11.6's plan, plus the dimension the §11 audit predates: pbreak/
rawOffsets (derived 2026-08-08, offsets into the very text the repair edits).
7,291 deletions / 127,867 spans (the § figures exactly), 7,548 pbreak offsets
shifted with zero anchor moves — then all 101 volumes RE-DERIVED from the
printed page and every one EQUAL to the arithmetic shift.  hyspace 8,790 →
1,501/96 (§11.5 exactly).  Two builder witnesses byte-identical.  Search index
re-emitted, 643,965 terms unchanged.  Bold baseline moved deliberately:
**339,569 → 381,912 drawn (+42,343), no volume lost a lemma.**  Every ratchet
green.  What remains of the hyphen question is §2's consonant branch (1,521)
and extract.py:204 hygiene — nothing else.
