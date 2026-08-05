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

## 3. The larger finding: `hyjoin` is corrupting the corpus TODAY

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
