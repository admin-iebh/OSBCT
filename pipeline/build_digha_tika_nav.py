#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the five Dīgha-Ṭīkā volumes.  SPEC and nothing else; the machinery is
`build_abhidhamma_nav`, and the mātikā gate is the point.

!!! THE FIVE NODES THIS REPLACES WERE KEYED TO THE CORPORA REPLACED TODAY, and
every one of their `suttas` entries therefore pointed at a moved ordinal.
2026-07-29k said to treat every Ṭīkā nav node as unverified.

WHY THESE GET A REAL TREE WHERE THE VINAYA ṬĪKĀ GOT ONLY BOOKS.  The Vinaya
Ṭīkā nav stops at the printed book because none of those volumes' mātikās had
been read (2026-07-29q).  **All five Dīgha Ṭīkā print one**, in the roman-folio
front matter, and it is structured exactly as the gate expects — a numbered
sutta head with its vaṇṇanā entries beneath and a printed page for each.  So
here the tree IS gated, and `matika_gate` is on.

    08DiT01  mātikā 0-based 12-17   body 19-423   13 suttas (Sīlakkhandhavagga)
    09DiT02  mātikā          3-4    body  6-505    1 sutta  (Brahmajāla only)
    10DiT03  mātikā          3-7    body  9-445   12 suttas (2-13)
    11DiT04  mātikā          3-9    body 11-368   10 suttas (Mahāvagga)
    12DiT05  mātikā          3-8    body 10-301   11 suttas (Pāthikavagga)

!!! THE EDITION IS NOT CONSISTENT ABOUT THE `-vaṇṇanā` SUFFIX ON A SUTTA HEAD.
08DiT01 prints `3. Ambaṭṭhasuttavaṇṇanā` between `2. Sāmaññaphalasutta` and
`4. Soṇadaṇḍasutta`; 10DiT03 prints it on the fourth and fifth and not on the
rest.  The `tops` pattern admits both forms rather than naming 47 literals, and
the builder still REFUSES if the sequence does not appear in printed order.

Usage: python3 pipeline/build_digha_tika_nav.py <VOL> [--write]
"""
import build_abhidhamma_nav as A

SIL = 'Dīgha Sīlakkhandhavagga — Sumaṅgalavilāsinī'
# a sutta head, with or without the `-vaṇṇanā` the edition adds inconsistently
SUTTA = r're:\d+\.\s+\S*sutta(?:vaṇṇanā)?$'
LEAF = [r're:.']

DIT = {
 # --- 08DiT01: Dhammapāla's Sīlakkhandhavaggaṭīkā, all thirteen suttas ------
 # Its mātikā and its body differ in six places, every one read on both pages.
 # TWO ARE BODY MISPRINTS WITH A WITNESS EACH:
 #   body p317 `Dutiya-ibbhapādavaṇṇanā` — and the body's OWN siblings p315
 #     `Paṭhama-ibbhavādavaṇṇanā` and p317 `Tatiya-ibbhavādavaṇṇanā` read
 #     `-vāda`, as does the mātikā for all three.  Two witnesses against one.
 #   body p422 `Brahmalokamaggadesanāvaṇṇanā` against the mātikā's
 #     `Brāhmaloka-`; *brahmaloka* is the word and p421's own prose sets
 #     `brahmalokamaggasaññāya`.  Here the BODY is right and the mātikā slipped
 #     — which is why nothing is corrected on either side, only compared.
 '08DiT01': {
   'body_errata': {
     # THE BODY NUMBERS THE SĀMAÑÑAPHALA'S FRUITS AND THE MĀTIKĀ DOES NOT —
     # `(1)`, `(2)`, `(3-7)`, `(8)` — in BOTH volumes that carry them.
     'Vipassanāñāṇakathāvaṇṇanā (1)':    'Vipassanāñāṇakathāvaṇṇanā',
     'Manomayiddhiñāṇakathāvaṇṇanā (2)': 'Manomayiddhiñāṇakathāvaṇṇanā',
     'Iddhividhañāṇādikathāvaṇṇanā (3-7)': 'Iddhividhañāṇādikathāvaṇṇanā',
     'Āsavakkhayañāṇakathāvaṇṇanā (8)':  'Āsavakkhayañāṇakathāvaṇṇanā',
     'Dutiya-ibbhapādavaṇṇanā':      'Dutiya-ibbhavādavaṇṇanā',
     'Brahmalokamaggadesanāvaṇṇanā': 'Brāhmalokamaggadesanāvaṇṇanā'},
   'title': 'Sīlakkhandhavaggaṭīkā',
   'label': 'Sīlakkhandhavaggaṭīkā',
   'work': SIL,
   'first': 2,
   'matika': (12, 17),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': [SUTTA],
   'levels': [None, LEAF],
 },
 # --- 09DiT02: the Sādhuvilāsinī I — FIVE HUNDRED PAGES ON ONE SUTTA --------
 # Ñāṇābhivaṁsa's abhinavaṭīkā gives the whole of its first bhāga to the
 # Brahmajāla, so the volume has exactly ONE top.  The label carries the bhāga
 # because 10DiT03 sets the identical inner title — 01VinA01/02VinA02's rule.
 '09DiT02': {
   # `Paṭhamabhāga` is the MĀTIKĀ PAGE'S OWN SECOND TITLE LINE, printed above
   # the rule with the volume name (p4: `Sīlakkhandhavagga-abhinavaṭīkā /
   # Paṭhamabhāga / _____ / Mātikā`).  It is not a section and no body heading
   # answers to it; dropped from the mātikā side only.
   'matika_drop': ('Paṭhamabhāga',),
   # THE BODY MISPRINTS ONE HEADING AND ITS OWN MĀTIKĀ DOES NOT: p455 heads
   # `Dīṭṭhadhammanibbānavādavaṇṇanā` with a LONG ī where the mātikā (p4) and
   # the volume's own prose two pages later (p457,
   # `attano diṭṭhadhammanibbānavādassa`) both set the short one — two
   # witnesses against one, and *diṭṭhadhamma* is the word.  The body keeps
   # what it prints.
   'body_errata': {'Dīṭṭhadhammanibbānavādavaṇṇanā':
                   'Diṭṭhadhammanibbānavādavaṇṇanā'},
   'title': 'Sīlakkhandhavagga-abhinavaṭīkā',
   'label': 'Sīlakkhandhavagga-abhinavaṭīkā (Paṭhamo bhāgo)',
   'work': SIL,
   'first': 3,
   'matika': (3, 4),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': [SUTTA],
   'levels': [None, LEAF],
 },
 # --- 10DiT03: the Sādhuvilāsinī II — suttas 2-13 --------------------------
 # Seven divergences, all read on both pages.  The mātikā DROPS `-vaṇṇanā`
 # from two of its sutta heads (p5 `4. Soṇadaṇḍasutta`, p6 `5. Kūṭadantasutta`)
 # where the body sets it, and it misprints the teacher's name: p4
 # `Ajitakesalakambalavādavaṇṇanā` against the body's p53
 # `Ajitakesakambalavādavaṇṇanā` — Ajita KESAKAMBALA, the hair-blanket ascetic.
 '10DiT03': {
   'body_errata': {
     # THE BODY NUMBERS THE SĀMAÑÑAPHALA'S FRUITS AND THE MĀTIKĀ DOES NOT —
     # `(1)`, `(2)`, `(3-7)`, `(8)` — in BOTH volumes that carry them.
     'Vipassanāñāṇakathāvaṇṇanā (1)':    'Vipassanāñāṇakathāvaṇṇanā',
     'Manomayiddhiñāṇakathāvaṇṇanā (2)': 'Manomayiddhiñāṇakathāvaṇṇanā',
     'Iddhividhañāṇādikathāvaṇṇanā (3-7)': 'Iddhividhañāṇādikathāvaṇṇanā',
     'Āsavakkhayañāṇakathāvaṇṇanā (8)':  'Āsavakkhayañāṇakathāvaṇṇanā',
     'Ajitakesakambalavādavaṇṇanā': 'Ajitakesalakambalavādavaṇṇanā',
     '4. Soṇadaṇḍasuttavaṇṇanā':    '4. Soṇadaṇḍasutta',
     '5. Kūṭadantasuttavaṇṇanā':    '5. Kūṭadantasutta',
     # body p320 `Dasa-akāravaṇṇanā` against the mātikā's p6 `Dasa-ākāra-`,
     # and the body's OWN next line reads `ākāro, kāraṇanti` — two witnesses
     # for the long ā against the heading's short one.
     'Dasa-akāravaṇṇanā':           'Dasa-ākāravaṇṇanā'},
   'title': 'Sīlakkhandhavagga-abhinavaṭīkā',
   'label': 'Sīlakkhandhavagga-abhinavaṭīkā (Dutiyo bhāgo)',
   'work': SIL,
   'first': 2,
   'matika': (3, 7),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': [SUTTA],
   'levels': [None, LEAF],
 },
 # --- 11DiT04: Dhammapāla on the Mahāvagga, ten suttas ---------------------
 # !!! ITS MĀTIKĀ SETS THE FIRST SUTTA WITHOUT ITS NUMBER — `Mahāpadānasutta`
 # (p4) against the body's `1. Mahāpadānasutta` (p11), where every other sutta
 # carries the number on both sides — and it CLOSES UP the eleventh simile,
 # `(11) Dvesatthavāha-upamāvaṇṇanā` against the body's `(11) Dve
 # satthavāha-upamāvaṇṇanā` (p365).  Both read on both pages.  The body keeps
 # what it prints; `body_errata` gives the gate the mātikā's form.
 '11DiT04': {
   'body_errata': {'1. Mahāpadānasutta': 'Mahāpadānasutta',
                   '(11) Dve satthavāha-upamāvaṇṇanā':
                       '(11) Dvesatthavāha-upamāvaṇṇanā'},
   'title': 'Mahāvaggaṭīkā',
   'label': 'Mahāvaggaṭīkā',
   'work': 'Dīgha Mahāvagga',
   'first': 1,
   'matika': (3, 9),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': [SUTTA],
   'levels': [None, LEAF],
 },
 # --- 12DiT05: Dhammapāla on the Pāthikavagga, eleven suttas ---------------
 # !!! THE MĀTIKĀ AND THE BODY DISAGREE BY ONE LETTER IN THREE PLACES, and each
 # was read on both pages before being declared.  `body_errata` supplies the
 # MĀTIKĀ's form to the gate so the two sides can be compared; **the body keeps
 # what it prints** and neither side is corrected — 06VinSg06's treatment.
 #
 #   mātikā p6  `Paṭivadādesanāvaṇṇanā`        body p84  `Paṭipadādesanāvaṇṇanā`
 #     — *paṭipadā* is the word; `paṭivada` is not Pāḷi.  The mātikā slipped.
 #   mātikā p6  `Suppahiṭṭhitapādatāla…`       body p109 `Suppatiṭṭhitapādatāla…`
 #     — *suppatiṭṭhitapāda* is the first of the thirty-two marks.  Likewise.
 #   mātikā p4  `Acelakapāthikaputtavatthu…`   body p16  `Acelapāthikaputtavatthu…`
 #     — ONE WITNESS AGAINST ONE.  Both *acela* and *acelaka* are Pāḷi, and the
 #     mātikā's own next entry, `Acelakaḷāramaṭṭakavatthuvaṇṇanā`, is `Acela` +
 #     `Kaḷāramaṭṭaka` in both places, so the compositor may have carried the
 #     `-ka` across.  DN 24 reads *acelo pāthikaputto*.  NOT SETTLED HERE.
 '12DiT05': {
   'body_errata': {
     'Acelapāthikaputtavatthuvaṇṇanā':        'Acelakapāthikaputtavatthuvaṇṇanā',
     'Paṭipadādesanāvaṇṇanā':                 'Paṭivadādesanāvaṇṇanā',
     'Suppatiṭṭhitapādatālakkhaṇavaṇṇanā (1)': 'Suppahiṭṭhitapādatālakkhaṇavaṇṇanā (1)'},
   'title': 'Pāthikavaggaṭīkā',
   'label': 'Pāthikavaggaṭīkā',
   'work': 'Dīgha Pāthikavagga',
   'first': 1,
   'matika': (3, 8),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': [SUTTA],
   'levels': [None, LEAF],
 },
}

A.SPEC.update(DIT)
A.main()
