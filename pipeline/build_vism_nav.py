#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the Visuddhimagga, 51Vism01 (and 52Vism02 when it is built).

The Visuddhimagga is not a commentary on any one canon text — the title page
calls it `Suttantapiṭake catunnaṁ āgamānaṁ sādhāraṇaṭṭhakathābhūto`, the
commentary common to all four āgamas — so no canon paragraph links to it and
the reader has no route in.  That is the link layer's problem; the tree below
is still what the edition prints.

ONE THING ABOUT THIS VOLUME'S PRINTED STRUCTURE, and it is the whole reason
this file exists: **THE EDITION NUMBERS A SECTION HEADING IN SOME PARICCHEDAS
AND NOT IN OTHERS.**  The mātikā (pp i-iv) numbers all 100 of its entries; the
body prints the Sīlaniddesa's eleven sections UNNUMBERED (`Sīlasarūpādikathā`)
and the Dhutaṅganiddesa's fourteen NUMBERED (`1. Paṁsukūlikaṅgakathā`), and it
goes on alternating.  That is a typesetting inconsistency of the edition, not
99 misprints, and declaring `errata` for it would bury the ONE entry that
really is a misprint.

The evidence that it is exactly that: with the mātikā's number allowed for, the
two streams are identical POSITION FOR POSITION — 100 against 100 — with
exactly one difference, `17. Pañcakajjhānakathā` against the body's
`Pañcakajjhānaṁkathā`.  Hence `matika_unnum`, gated per volume and measured
+0 -0 over all 33 volumes that declare a `matika` range.

The eleven paricchedas ARE printed as centred headings (`1. Sīlaniddesa` …
`11. Samādhiniddesa`), numbered 1..11 with no gap — which is the check that
none was missed — so they are `tops`, not `books`: the volume prints ONE title
page and ONE homage and is one work.  Their closing colophons are three and
four lines here rather than two; see `colofix` in the builder's SPEC.
"""
import build_abhidhamma_nav as A

WORK = 'Visuddhimagga (common to all three piṭakas)'


VISM = {
 '51Vism01': {
   'title': 'Visuddhimaggo (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 6),
   'matika_gate': True,
   'matika_centred_gate': True,
   'matika_unnum': True,
   'level_memo': True,
   # `Nidānādikathā` sits ABOVE the first pariccheda in the mātikā and in the
   # body — it belongs to no niddesa — so it is a top in its own right.
   'tops': ['Nidānādikathā',
            '1. Sīlaniddesa', '2. Dhutaṅganiddesa',
            '3. Kammaṭṭhānaggahaṇaniddesa', '4. Pathavīkasiṇaniddesa',
            '5. Sesakasiṇaniddesa', '6. Asubhakammaṭṭhānaniddesa',
            '7. Cha-anussatiniddesa', '8. Anussatikammaṭṭhānaniddesa',
            '9. Brahmavihāraniddesa', '10. Āruppaniddesa',
            '11. Samādhiniddesa'],
   # The printed mātikā shows exactly TWO levels — niddesa and section — and no
   # third anywhere, so everything below a top is a leaf.
   'levels': [None, [r're:.']],
   # THE VOLUME'S ONE ERRATUM.  The mātikā (p iii) sets
   # `17. Pañcakajjhānakathā`; the body (p163) sets `Pañcakajjhānaṁkathā`, with
   # an `ṁ` the word does not take.  Neither side is corrected; the two
   # readings are named as the same section.  It is the ONLY position at which
   # the mātikā and the heads stream differ once the mātikā's numbering is
   # allowed for — which is what makes `matika_unnum` a convention rather than
   # a way of hiding misprints.
   'errata': {'17. Pañcakajjhānakathā': 'Pañcakajjhānaṁkathā'},
 },
 '52Vism02': {
   'title': 'Visuddhimaggo (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 6),
   # A LONG CENTRED GROUP HEAD CENTRES FURTHER LEFT, and this volume's
   # mātikā sets three lines below the 18-space default, so the
   # centred gate could not see them at all (_tika/cmin_sweep.py,
   # 2026-07-30). 12 is where the count stabilises; no dotted entry
   # leaks in — measured on every volume that declares a mātikā range.
   'centred_indent': 12,
   'matika_gate': True,
   'matika_centred_gate': True,
   'matika_unnum': True,
   'level_memo': True,
   # THE PARICCHEDAS CONTINUE VOLUME 1'S NUMBERING — 12 to 23, no gap — which
   # is the same check the paragraph numbers give: 51Vism01 runs n 1-364 and
   # this volume 365-896, 532 paragraphs, and 896 - 364 = 532 exactly.
   'tops': ['12. Iddhividhaniddesa', '13. Abhiññāniddesa',
            '14. Khandhaniddesa', '15. Āyatanadhātuniddesa',
            '16. Indriyasaccaniddesa', '17. Paññābhūminiddesa',
            '18. Diṭṭhivisuddhiniddesa',
            '19. Kaṅkhāvitaraṇavisuddhiniddesa',
            '20. Maggāmaggañāṇadassanavisuddhiniddesa',
            '21. Paṭipadāñāṇadassanavisuddhiniddesa',
            '22. Ñāṇadassanavisuddhiniddesa',
            '23. Paññābhāvanānisaṁsaniddesa'],
   'levels': [None, [r're:.']],
   # THREE ERRATA, both readings preserved:
   #  * `4. Cutūpapātañāṇakathā` against the body's `Cuthūpapātañāṇakathā`
   #    (p53) — a `th` the word does not take;
   #  * the mātikā GLOSSES a name the body prints bare, `3. Dukkhaniddesakathā
   #    (Jātiniddesa)` where the body sets `Dukkhaniddesakathā` and then
   #    `Jātiniddesa` as its own heading beneath.  Joined to the first; the
   #    gloss is not part of the name.  Same shape as 30Abhi02's `(niddesa)`;
   #  * `Nigamakathā` against the body's `Nigamanakathā` (p354).
   'errata': {'4. Cutūpapātañāṇakathā':            'Cuthūpapātañāṇakathā',
              '3. Dukkhaniddesakathā (Jātiniddesa)': 'Dukkhaniddesakathā',
              'Nigamakathā':                       'Nigamanakathā'},
 },
}

A.SPEC.update(VISM)
A.main()
