## THE CENTRED GATE WAS PARTLY BLIND IN SIX VOLUMES — AND I DESTROYED nav.json FINDING OUT (2026-07-30e)

### !!! FIRST, THE DAMAGE, AND IT WAS MINE

A read-only probe (`_tika/cmin_sweep.py`) imported every `build_*_nav.py` to read its
`SPEC`. **`pipeline/build_nav.py` has no `main()` and no `if __name__` guard — its whole
body is module-level — so importing it REBUILT `site/reader/nav.json` from scratch**,
replacing 2.16 MB and **28,612 gated tree rows with 0.53 MB and none**, and printing a
cheerful `wrote nav.json 519 KB` while it did so.

**THIS WAS THE SECOND TIME.** `site/reader/nav.json.damaged_by_29probe` (527,683 bytes,
2026-07-29) is the same file destroyed the same way by the same kind of probe.

Recovered in full: `nav.json.bak26vsmt02` (the last pre-image, 12:01) + one re-run of
`build_lasttika_nav.py 26VsmT02 --write`. Verified **138 volumes, 28,722 tree rows,
`_navdup` PASS** — the count is 110 higher than the backup because the backup predates the
26VsmT02 node it was taken before. The damaged file is kept as
`nav.json.damaged_by_cminsweep`.

**FIXED SO IT CANNOT RECUR:** `build_nav.py` now REFUSES TO BE IMPORTED —

```python
if __name__ != '__main__':
    raise ImportError('build_nav.py is a SCRIPT: importing it rewrites '
                      'site/reader/nav.json and drops every gated tree...')
```

and `cmin_sweep.py` no longer imports anything that writes: it `ast.parse`s each builder,
**strips every top-level bare CALL** (which is exactly the `A.main()` / `main()` at the
foot of each file, the only thing in them that writes) and execs the rest. Assignments and
defs still run, so the SPEC comes out complete.

### THE FINDING ITSELF

`matika_lines` reads a centred mātikā line as one indented **at least 18 spaces**. A
centred line's indent is a function of its LENGTH — a long group head centres further
LEFT — so the reader was skipping long ones entirely. `centred_indent` already existed for
this and the five Vinaya canon volumes already declare 14; nobody had swept for the rest.

Measured against each volume's OWN declared indent (the first run of the sweep compared
against the bare 18 and overstated the loss — 8 volumes, 20 heads):

```
volume     builder                            centred seen -> at 12
17AnA01    build_anguttara_atthakatha_nav.py       6 ->   7
19AnT02    build_anguttara_tika_nav.py            19 ->  22    (three pair-lines)
15SamA02   build_samyutta_atthakatha_nav.py       47 ->  48
16SamA03   build_samyutta_atthakatha_nav.py       73 ->  77
14Sam03    build_samyutta_nav.py                  99 -> 104
52Vism02   build_vism_nav.py                       9 ->  12
```

**Six volumes, 17 printed group heads the gate never saw.** A gate that cannot see an entry
cannot refuse it — 2026-07-29's lesson (*"a gate that finds nothing is indistinguishable
from a gate that passes"*) in a new place.

### AND THE ANSWER TO THE QUESTION IT RAISES: NO READER HOLE

The tree is built from the BODY's headings; the mātikā only checks it. So each of the 17
was resolved separately against `nav.json` and `sections/` (`_tika/cmin_reach.py`):
**15 of 17 were in the tree all along.** The two that were not are both non-sections:

* `17AnA01` `Ekakanipāta Aṅguttaraṭṭhakathā` — **the mātikā's own title line**, printed
  ONCE in the whole file, over the mātikā itself. `matika_drop`.
* `14Sam03` `10. Cattuttha-āmakadhaññapeyyālavagga` — **the edition's own slip**. The body
  heads `10. Catuttha-` and closes it `Catuttha-āmakadhaññapeyyālavaggo dasamo.`;
  `Cattuttha-` occurs once, in the mātikā. Two witnesses against one. Added to that
  volume's existing `errata` map — which already carried FOUR centred errata, so this is a
  fifth of the same kind — and to `data/errata.json` as **E067**, 57 → **58**.

All six now declare `centred_indent: 12` (where the count stabilises; **no dotted entry
leaks in** — checked on every volume that declares a mātikā range) and all six gates pass
seeing everything: 6/6, 16/16, 38/38, 76/76, **94/94**, 12/12. Nodes rewritten, `_navdup`
PASS, BUILD **`1b6ead6ab910`**.

### THE SEVEN VINAYA ṬĪKĀ — MEASURED, NOT YET BUILT

All seven print a usable mātikā and, unlike the Vinaya CANON, **it is not finer than the
body**: 1,732 dotted entries of which **1,698 resolve against the printed heads (98%)**.
So `matika_gate: True` is available here, which it never was for the canon.

```
volume    mātikā pdf   entries (absent)  centred (absent)  printed heads  SPEC books
01ViT01      14-15        23  ( 0)           3  (2)             27            2
02ViT02       4-9        113  ( 2)          12  (3)            129            1
03ViT03       4-21       360  ( 6)          43  (5)            411            5
04ViT04       4-9        122  ( 2)          14  (3)            136            2
05ViT05       4-18       284  ( 7)          60  (5)            346            5
06ViT06       4-27       459  (10)          72  (…)            541            6
07ViT07       4-21       371  ( 7)          55  (1)            423            4
```

**cmin=12 is right for these too** — at 18 the reader loses 22 centred group heads across
the seven (03ViT03 alone loses `3. Vassūpanāyikakkhandhaka`, `9. Campeyyakkhandhaka`,
`10. Kosambakakkhandhaka`).

**THE MĀTIKĀ MUST BE SEGMENTED PER BOOK BEFORE IT IS COMPARED.** 06ViT06 appeared to print
`3. Nissaggiyakaṇḍa` where the body heads `4. Nissaggiyakaṇḍa` — not an erratum at all: the
volume's mātikā runs the Bhikkhu-vibhaṅga's kaṇḍas (1 Pārājika … 5 Pācittiya) and then the
Bhikkhunī-vibhaṅga's (1 Pārājika … 4 Pācittiya, no Aniyata, correctly), and a FLAT
comparison crosses them. A flat gate would have reported two errata that do not exist.

**A THIRD WITNESS SETTLES EVERY DISAGREEMENT: THE COLOPHON.** Every section is closed by a
centred `… niṭṭhitā.` naming it again, so where mātikā and body differ the colophon casts
the deciding vote (`_tika/vt_witness.py` — and note it must strip the section NUMBER first,
since a colophon never carries one; the first run reported "no colophon" for six places
that are closed by name on the page). Of 34 disagreements: **12 say the mātikā is the slip,
4 say the body heading is, 18 have no colophon and stay unresolved.** Two of the body-side
ones are worth naming — 07ViT07 p433 heads `60. Āvupoṇisikkhāpadavaṇṇanā` where its own
mātikā and colophon both read `Āvudhapāṇi-`, and 06ViT06 heads
`1. Bhūtagāmasikkhāpada**daṇṇanā**` for `-vaṇṇanā`. **Both are the printed page, not our
conversion** — checked directly in `pdftotext` output.

**FIVE COLOPHONS ARE TYPED AS HEADINGS in `sections/`** — 02ViT02 ord61 + ord85, 03ViT03
ord603, 06ViT06 ord194, 24AbhiT03 ord378 — all of the form `X niṭṭhitā`. Small, and the
inverse of the false-colophon class of 2026-07-30a.

**NEXT:** write the seven SPEC entries (tops = `re:\d+\. \S*(kaṇḍa|khandhaka)$` plus the
named Parivāra sections; level 2 = `re:\d+\. \S*vagga$`), with `centred_indent: 12`,
per-book mātikā segmentation, and `body_errata` for the 16 colophon-settled disagreements.

