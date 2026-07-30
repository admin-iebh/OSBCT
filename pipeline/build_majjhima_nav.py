#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a Majjhimanikāya volume's nav tree with the generic nav machinery.

    python3 pipeline/build_majjhima_nav.py <VOL> [--write]

Same shape as `build_vinaya_nav.py` and `build_digha_nav.py`: the builder in
`build_abhidhamma_nav.py` is generic over the piṭaka, so this file is the SPEC
and nothing else.  (The previous font-heuristic file is kept as `.prespec`.)

!!! THE MAJJHIMA IS TWO LEVELS, UNLIKE THE DĪGHA'S FLAT ONE.  Each volume is
ONE book whose FIVE VAGGAS are the mātikā's centred group heads, with the
SUTTAS beneath them and the suttas' own sections as leaves.  So `tops` is the
vaggas and `levels` carries a numbered sutta rung — `[None]` would flatten the
whole nikāya onto the vaggas.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_abhidhamma_nav as A

# A sutta rung: numbered, and the name ends at `sutta`.  A RANGE is real — the
# edition runs several suttas together where their text is one.
SUTTA = r're:\d+(?:-\d+)*\.\s+.*sutta$'

MAJJHIMA = {

 '09Ma01': {
   'title': 'Mūlapaṇṇāsapāḷi',
   'work': 'Majjhima Mūlapaṇṇāsa — Papañcasūdanī',   # kept from the volume's node
   'first': 0,
   'matika': (11, 14),
   'matika_gate': True,
   'matika_centred_gate': True,
   'tops': ['1. Mūlapariyāyavagga', '2. Sīhanādavagga', '3. Opammavagga',
            '4. Mahāyamakavagga', '5. Cūḷayamakavagga'],
   'levels': [None, [SUTTA]],
   # AN ERRATUM OF THE EDITION, RECORDED NOT CORRECTED.  The mātikā prints
   # `10. Mūratajjanīyasutta`, the body head `10. Māratajjanīyasutta`.
   # COUNTED IN THE HEADS STREAM, which is the right denominator: ONE heading
   # on each side.  (The six raw body hits are RUNNING HEADERS, which never
   # enter the heads stream — count those and you would wrongly reach for
   # `body_errata`.)
   'errata': {'10. Mūratajjanīyasutta': '10. Māratajjanīyasutta'},
   # The body heads this section `Tassuddānaṁ`, which `kat_is_colo` classifies
   # as a COLOPHON, so no nav row can exist for it.  Five printings, one
   # literal drops all five.  Same open finding as the Dīgha and 05Vin05.
   'matika_drop': ('Uddānagāthā',),
 },

 '10Ma02': {
   'title': 'Majjhimapaṇṇāsapāḷi',
   'work': 'Majjhima Majjhimapaṇṇāsa',
   'first': 0,
   'matika': (3, 5),
   'matika_gate': True,
   'matika_centred_gate': True,
   'tops': ['1. Gahapativagga', '2. Bhikkhuvagga', '3. Paribbājakavagga',
            '4. Rājavagga', '5. Brāhmaṇavagga'],
   'levels': [None, [SUTTA]],
   'errata': {'8. Abhayarājakumārasutta': '8. Abhayarājākumārasutta'},
   'matika_drop': ('Uddānagāthāyo',),
 },

 '11Ma03': {
   'title': 'Uparipaṇṇāsapāḷi',
   'work': 'Majjhima Uparipaṇṇāsa',
   'first': 0,
   'matika': (3, 5),
   'matika_gate': True,
   'matika_centred_gate': True,
   'tops': ['1. Devadahavagga', '2. Anupadavagga', '3. Suññatavagga',
            '4. Vibhaṅgavagga', '5. Saḷāyatanavagga'],
   'levels': [None, [SUTTA]],
   # NOT ERRATA — these two headings carry a FOOTNOTE MARKER inside them, the
   # same shape as 04Vin04 p187 `10. Dutiyanavaka1` and 05Vin05's
   # `Ekamūlaṁ niṭṭhitaṁ1.`  The marker is PRINTED, so the tree keeps it and
   # the mātikā's bare form is supplied as an alternative fold on the TREE
   # side.  `errata` would be a lie about the edition.
   'body_errata': {'2. Pañcattayasutta1': '2. Pañcattayasutta',
                   '5. Cūḷakammavibhaṅgasutta1': '5. Cūḷakammavibhaṅgasutta'},
   'matika_drop': ('Uddānagāthā',),
 },

}

A.SPEC.update(MAJJHIMA)
A.main()
