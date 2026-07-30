#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the three Majjhima-Ṭīkā volumes.  SPEC only; the machinery is
`build_abhidhamma_nav`, and the mātikā gate is the point (2026-07-29r).

!!! THE FOUR NODES THIS REPLACES WERE KEYED TO THE CORPORA REPLACED TODAY.
15MaT03 carried two of them, `Majjhimapaṇṇāsaṭīkā` at #2 and `Uparipaṇṇāsaṭīkā`
at #332 — the seam is at ord335 on the rebuilt corpus — and both of 13MaT01's
and 14MaT02's `suttas` lists pointed at moved ordinals.

THE SHAPE IS NOT THE DĪGHA'S.  There the tops are the suttas; the Majjhima
prints VAGGAS of ten suttas, so the tops are the vaggas and the suttas are the
level below them.

    13MaT01  mātikā 0-based 13-16   body  18-411   1 vagga  (Mūlapariyāya)
    14MaT02  mātikā          3-5    body   7-330   4 vaggas (Sīhanāda-Cūḷayamaka)
    15MaT03  mātikā          3-8    body  10-451   5 + 5 vaggas, TWO BOOKS

15MaT03 prints TWO mātikās, one per work, at pp4-6 and pp7-9 — and they stand
in the same order as the two bodies, so one range covers both and the gate
consumes them in printed order.

13MaT01 opens with the Ganthārambha and the Nidāna material, eighteen ordinals
before its single vagga head; those become the leading top, as 08DiT01's and
09DiT02's Ganthārambha already do.

Usage: python3 pipeline/build_majjhima_tika_nav.py <VOL> [--write]
"""
import build_abhidhamma_nav as A

MULA = 'Majjhima Mūlapaṇṇāsa — Papañcasūdanī'
VAGGA = r're:\d+\.\s+\S*vagga$'
SUTTA = r're:\d+\.\s+\S*sutta(?:vaṇṇanā)?$'
LEAF = [r're:.']

MAT = {
 # --- 13MaT01: the Mūlapariyāyavagga, behind 18 ordinals of Ganthārambha ----
 '13MaT01': {
   'title': 'Mūlapaṇṇāsaṭīkā',
   'label': 'Mūlapaṇṇāsaṭīkā (Paṭhamo bhāgo)',
   'work': MULA,
   'first': 1,
   'matika': (13, 16),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': [VAGGA],
   'levels': [None, [SUTTA], LEAF],
 },
 # --- 14MaT02: the other four vaggas of the Mūlapaṇṇāsa --------------------
 # !!! ITS MĀTIKĀ MISNAMES A VAGGA.  p5 lists `3. Ovādavagga`; the body heads
 # it `3. Opammavagga` (p84) and closes it `Niṭṭhitā ca opammavaggavaṇṇanā.`
 # (p185).  Two witnesses against one, and the Mūlapaṇṇāsa's third vagga IS
 # the Opamma — there is no Ovādavagga in the Majjhima.  The body keeps what
 # it prints; `body_errata` gives the gate the mātikā's form.
 '14MaT02': {
   # `Dutiyabhāga` is the MĀTIKĀ PAGE'S OWN SECOND TITLE LINE (p4:
   # `Mūlapaṇṇāsaṭīkā / Dutiyabhāga / _____ / Mātikā`), not a section —
   # 09DiT02's `Paṭhamabhāga`, the same page furniture.
   'matika_drop': ('Dutiyabhāga',),
   # AND IT TRANSPOSES A SUTTA NAME: mātikā p6 `10. Mātarajjanīyasuttavaṇṇanā`
   # against the body's p321 `10. Māratajjanīyasuttavaṇṇanā`.  MN 50 is the
   # **Māratajjanīya**, the rebuking of MĀRA; `māta-` is not the word.
   'body_errata': {'3. Opammavagga': '3. Ovādavagga',
                   '10. Māratajjanīyasuttavaṇṇanā':
                       '10. Mātarajjanīyasuttavaṇṇanā'},
   'title': 'Mūlapaṇṇāsaṭīkā',
   'label': 'Mūlapaṇṇāsaṭīkā (Dutiyo bhāgo)',
   'work': MULA,
   'first': 1,
   'matika': (3, 5),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': [VAGGA],
   'levels': [None, [SUTTA], LEAF],
 },
 # --- 15MaT03: TWO WORKS, five vaggas each --------------------------------
 # !!! ONE BODY HEADING CARRIES A FOOTNOTE MARKER AND THE MĀTIKĀ DOES NOT.
 # p380 heads `5. Cūḷakammavibhaṅgasuttavaṇṇanā1` — the `1` is a printed
 # footnote reference ON THE SECTION TITLE — against the mātikā's p8
 # `5. Cūḷakammavibhaṅgasuttavaṇṇanā`.  The marker is part of the printed line
 # and so part of the literal, the same reason a `headskip` literal cannot be
 # shared between volumes.
 # AND ONE BODY HEADING TRANSPOSES ITS VOWELS: p400 `10. Dhātuvubhaṅga-`
 # against the mātikā's `Dhātuvibhaṅga-`; MN 140 is the **Dhātuvibhaṅga** and
 # the body's own closing colophon (p413) reads `Dhātuvibhaṅgasuttavaṇṇanāya`.
 # Two witnesses against one, and the body keeps what it prints.
 '15MaT03': {
   'body_errata': {'5. Cūḷakammavibhaṅgasuttavaṇṇanā1':
                       '5. Cūḷakammavibhaṅgasuttavaṇṇanā',
                   '10. Dhātuvubhaṅgasuttavaṇṇanā':
                       '10. Dhātuvibhaṅgasuttavaṇṇanā'},
   'title': 'Majjhimapaṇṇāsaṭīkā',
   'label': 'Majjhimapaṇṇāsaṭīkā + Uparipaṇṇāsaṭīkā',
   'work': 'Majjhima Uparipaṇṇāsa',
   'first': 2,
   'matika': (3, 8),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'books': [
     {'title': 'Majjhimapaṇṇāsaṭīkā', 'lo': 0, 'hi': 335,
      'tops': [VAGGA], 'levels': [None, [SUTTA], LEAF]},
     {'title': 'Uparipaṇṇāsaṭīkā', 'lo': 335, 'hi': 644,
      'tops': [VAGGA], 'levels': [None, [SUTTA], LEAF]},
   ],
 },
}

A.SPEC.update(MAT)
A.main()
