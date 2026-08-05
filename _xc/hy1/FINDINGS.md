# The line-break hyphen is not a cause of class 2, and "a pāda never ends mid-word" is false

2026-08-05. Working record: `_xc/hy1/`. **No data touched, no builder changed.**
Instrument measured first, per the standing rule. HEAD at time of measurement `dcead251`
(one commit past the `0db4a917` named in the handoff; `dcead251` "changed files" is
34 files of `_xc/h1/` and `_xc/boldfid/` probe output, no code).

## 1. The handoff files this fault under the wrong class

`claude/start_here_2026-08-05.md` §"Next, in order" item 1 reads:

> **Class 2 residue, 9,854.** … The **second known cause is the line-break hyphen**
> (`46KhuA27`, `12DiT05`) and it has never been attempted.

`claude/the_run_was_judged_as_a_whole_and_never_split.md` §6.2, which is where the
fault was first recorded, states it correctly and does not mention class 2:

> A display run whose last line ends in a line-break hyphen **is prose**. … one printed
> line is split across two render blocks — the only two volumes `verify_render_vs_pdf`
> loses on.

A prose line drawn as verse is **class 1**. The 08-05 handoff merged the hyphen fault
into the class-2 item; it is not class 2, and repairing it will not move the 9,854.

**Measured.** `check_page_fidelity` on the two witnesses, per printed line:

| | 46KhuA27 | 12DiT05 |
|---|---:|---:|
| class 2 `VERSE_AS_PROSE` | 37 | **2** |
| class 1 `PROSE_AS_VERSE` | 343 | 49 |

Neither volume's class-2 count has anything to do with the hyphen. `12DiT05`'s two
class-2 lines are on p238 and are ordinary prose glosses.

## 2. What the instrument that DOES see this fault reports

`verify_all_volumes` reproduces the 08-04 numbers on the reverse and duplicate axes:
`46KhuA27` **1 lines / 0 chunks / 2 rev / 0 dup**, `12DiT05` **3 / 3 / 6 / 0**.
(The 08-04 doc records `12DiT05` as `43/3/6/0`; the forward-line figure differs
because that run was per book and this one is whole-volume. rev/chunk/dup agree exactly.)

All **8** reverse misses across both volumes are residue entries in a verse side-map's
`before` or `after` array, and every one is a printed line whose two halves became two
entries:

| vol | ord | side | printed line, as the page sets it |
|---|---|---|---|
| 46KhuA27 | 108 | after | `…nivattiñca sa-` / `upāyaṁ. Iti…` |
| 12DiT05 | 285 | before | `…sampattato yathā-` / `upaṭṭhita…` |
| 12DiT05 | 286 | before | `…savisaye pavatti-` / `ākāraviseso,` |
| 12DiT05 | 300 | after | `…dīghanikāyamahā-` / `aṭṭhakathāsārameva…` |

Each costs 2 reverse misses (one per half) and 1 forward line miss.

## 3. Three distinct shapes, and the class checker sees only one of them

| | witness | page class | corpus | verdict | visible to `check_page_fidelity`? |
|---|---|---|---|---|---|
| **A** prose line swallowed INTO a display run | `46KhuA27` p189 | prose | V | `PROSE_AS_VERSE` | yes — as **class 1** |
| **B** display run's LAST line ends mid-word, continuation is prose | `12DiT05` p300 | verse | V | `verse_ok` | **no** |
| **C** both halves page-prose, split into two residue entries | `12DiT05` p281, p282 | prose | P | `prose_ok` | **no** |

**5 of the 6 printed lines involved are scored clean by the class checker.** Shape C is
the majority (4 of 8 reverse misses) and has no display run in it at all, so §6.2's
framing — "a display run whose last line…" — covers only shapes A and B.

## 4. "A pāda never ends mid-word" is refuted by the edition

§6.2 offers that as the licensing principle. It is false, and a blanket rule would
damage real verse in 38 volumes.

Corpus-wide census (`_xc/hy1/cen`, all 118 volumes, `_xc/hy1/census.py`):

- printed lines ending in `-`: **14,396**
- of those, judged **page-verse**: **143**
- **76 of the 143 are the peyyāla `-pa-` / `-pe-` / `-la-`**, a complete token that
  `hyjoin`'s `_PEYYALA_END` already recognises — not a word break at all. *(My first
  pass counted these as hyphen lines. That was a defect in this probe, not in the
  corpus, and it inflated the population by 113%. Corrected here.)*
- **genuine mid-word hyphen on a page-verse line: 67, across 38 volumes.**

Of 69 page-verse hyphen lines in the five volumes read line-by-line
(`_xc/hy1/shape.py`), **68 continue into another page-verse line** — the compound
genuinely spills across the pāda break, and the edition sets it that way:

```
Yo sabbalokātigasabbasobhā-        46KhuA27 p7   ind 23
Yuttehi sabbehi guṇehi yutto.                    ind 23

Namo avijjādikilesajāla-           01VinA01 p15  ind 14
Viddhaṁsino dhammavarassa tassa.                 ind 14

Dukkhaṁ tiracchesu kasāpatoda-     03ViT03 p193  ind 15
Daṇḍābhighātādibhavaṁ anekaṁ.                    ind 15
```

**Exactly one** of the 69 is the §6.2 shape — `12DiT05` p300, whose continuation is
page-prose at indent 0. The discriminator is therefore **not** the hyphen. It is
**whether the continuation line leaves the display run**.

## 5. What this means for the repair

The rule that survives the measurement is narrow:

> A hyphen-ending line and its continuation are **one printed line** and must land in
> **one render block**. Where they currently land in two, join them with `hyjoin`,
> which already carries the sentence.

That is a statement about **residue entry construction**, not about pāda geometry, and
it covers all three shapes at once without consulting the display run. `hyjoin` is
applied on some paths into `before`/`after` (`build_khu_volume.py` 7751, 7781) and not
on the paths these four ordinals take.

**Do not** implement §6.2 as written ("a display run whose last line ends in a hyphen is
prose"): it addresses only shapes A and B, it is silent on the majority shape C, and the
principle it rests on would move 67 real verse lines in 38 volumes.

## 6. Expected movement, to be checked against, not assumed

- `verify_render_vs_pdf`: `46KhuA27` 1/0/2/0 → **0/0/0/0**, `12DiT05` 3/3/6/0 → **0/0/0/0**.
  These are the only two volumes the harness loses on for this cause.
- `check_page_fidelity` class 2: **no movement expected.** 9,854 is untouched by this.
- `check_page_fidelity` class 1: at most **−1** (`46KhuA27` p189, shape A), and only if
  the join also takes that line off the verse branch.
- Any movement beyond this is a side effect and must be read on the page.

## 7. Reproduce

```
python3 pipeline/check_page_fidelity.py 46KhuA27 12DiT05 --dump _xc/hy1
python3 _xc/hy1/probe.py                      # the 8 reverse misses, with text
python3 _xc/hy1/census.py 150                 # resumable; repeat until 118/118
python3 _xc/hy1/shape.py 46KhuA27 12DiT05 01VinA01 03ViT03 27KhuA08
```

## 8. Not done

The repair itself. The four ordinals' emission paths in `build_khu_volume.py` are
located but the join is not written, `pbreak/` is not re-derived, and no gate has been
re-run. Nothing in the corpus or the builder was changed by this work.
