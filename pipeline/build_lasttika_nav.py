#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the last three Ṭīkā — the Khuddaka's Netti pair and the two volumes
of the Visuddhimagga-mahāṭīkā.  SPEC only; the machinery is
`build_abhidhamma_nav`, and the mātikā gate is the point (2026-07-29r).

    21KhuT01  mātikā 0-based 3-6   body   8-522   TWO WORKS
              Nettiṭīkā (Dhammapāla) and Nettivibhāvinī (Saddhammapāla), the
              second commenting the Netti afresh rather than the first — so
              its sections are `-atthavibhāvanā` where the first has
              `-vaṇṇanā`, and the two tops lists cannot be shared.
              ONE mātikā PER WORK, pp4-5 and pp6-7, in the bodies' own order.
    25VsmT01  mātikā          3-7   body   9-469   paricchedas 1-11
    26VsmT02  mātikā          3-7   body   9-543   paricchedas 12-23

THE VISUDDHIMAGGA-MAHĀṬĪKĀ IS ONE WORK IN TWO BHĀGAS and the edition says so:
26VsmT02 opens at unit 365 where 25VsmT01 closes at 363, and its own last page
reads `Paṭhamo bhāgo niṭṭhito.` / `Visuddhimaggamahāṭīkā samattā.`  The 23
paricchedas run 1-11 in the first volume and 12-23 in the second, unbroken.

Usage: python3 pipeline/build_lasttika_nav.py <VOL> [--write]
"""
import build_abhidhamma_nav as A

WNET = 'Nettippakaraṇa — Nettiṭīkā + Nettivibhāvinī'
WVSM = 'Visuddhimagga — Paramatthamañjūsā'
LEAF = [r're:.']

NETTI_T = ['Ganthārambhakathāvaṇṇanā', 'Nidānakathāvaṇṇanā',
           '1. Saṅgahavāravaṇṇanā', '2. Uddesavāravaṇṇanā',
           '3. Niddesavāravaṇṇanā', '4. Paṭiniddesavāra']
NETTI_V = ['Ganthārambhakathā',
           '1. Saṅgahavāra-atthavibhāvanā', '2. Uddesavāra-atthavibhāvanā',
           '3. Niddesavāra-atthavibhāvanā', '4. Paṭiniddesavāra-atthavibhāvanā']
VSM1 = ['Ganthārambhakathā', 'Nidānādikathāvaṇṇanā',
        '1. Sīlaniddesavaṇṇanā', '2. Dhutaṅganiddesavaṇṇanā',
        '3. Kammaṭṭhānaggahaṇaniddesavaṇṇanā', '4. Pathavīkasiṇaniddesavaṇṇanā',
        '5. Sesakasiṇaniddesavaṇṇanā', '6. Asubhakammaṭṭhānaniddesavaṇṇanā',
        '7. Cha-anussatiniddesavaṇṇanā', '8. Anussatikammaṭṭhānaniddesavaṇṇanā',
        '9. Brāhmavihāraniddesavaṇṇanā', '10. Āruppaniddesavaṇṇanā',
        '11. Samādhiniddesavaṇṇanā']
VSM2 = ['12. Iddhividhaniddesavaṇṇanā', '13. Abhiññāniddesavaṇṇanā',
        '14. Khandhaniddesavaṇṇanā', '15. Āyatanadhātuniddesavaṇṇanā',
        '16. Indriyasaccaniddesavaṇṇanā', '17. Paññābhūminiddesavaṇṇanā',
        '18. Diṭṭhivisuddhiniddesavaṇṇanā',
        '19. Kaṅkhāvitaraṇavisuddhiniddesavaṇṇanā',
        '20. Maggāmaggañāṇadassanavisuddhiniddesavaṇṇanā',
        '21. Paṭipadāñāṇadassanavisuddhiniddesavaṇṇanā',
        '22. Ñāṇadassanavisuddhiniddesavaṇṇanā',
        '23. Paññābhāvanānisaṁsaniddesavaṇṇanā']

LAST_T = {
 # ONE MĀTIKĀ-VS-BODY DIVERGENCE: mātikā p4 `3. Niddesavāra` against the
 # body's p32 `3. Niddesavāravaṇṇanā` — the mātikā drops the `-vaṇṇanā` its own
 # neighbours carry.  RECORDED; no third witness is needed for a suffix the
 # same list uses five lines above.
 '21KhuT01': {
   'body_errata': {'3. Niddesavāravaṇṇanā': '3. Niddesavāra'},
   'title': 'Nettiṭīkā + Nettivibhāvinī',
   'work': WNET,
   'first': 1,
   'matika': (3, 6),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'books': [
     {'title': 'Nettiṭīkā', 'lo': 0, 'hi': 138,
      'tops': NETTI_T, 'levels': [None, LEAF]},
     {'title': 'Nettivibhāvinī', 'lo': 138, 'hi': 287,
      'tops': NETTI_V, 'levels': [None, LEAF]},
   ],
 },
 # !!! FOUR MĀTIKĀ-VS-BODY DIVERGENCES, and THREE OF THEM ARE THE BODY'S.
 #   mātikā p5 `Dhutaṅgapakiṇṇakakathāvaṇṇanā`  body p111 `…kakahā-` — a LOST
 #     `t`; it is *kathā*.  BODY SLIPPED.
 #   mātikā p8 `Catudhātuvavatthānabhāvanāvaṇṇanā`  body p432 `Catudhātuvatthā-`
 #     — a LOST `va`; it is *vavatthāna*, determining.  BODY SLIPPED.
 #   mātikā p7 `9. Brahmavihāraniddesavaṇṇanā`  body p358 `Brāhmavihāra-` —
 #     the Visuddhimagga's ninth chapter is the BRAHMAVIHĀRA-niddesa, and
 #     51Vism01 prints `Brahmavihāra` twice with `Brāhma-` nowhere.  BODY.
 #   mātikā p4 `Sīlasaṁkilesa, vodānavaṇṇanā`  body `…kilesa vodāna…` — a comma
 #     the body does not set.  No third witness; RECORDED.
 '25VsmT01': {
   'body_errata': {
     'Sīlasaṁkilesa vodānavaṇṇanā':     'Sīlasaṁkilesa, vodānavaṇṇanā',
     'Dhutaṅgapakiṇṇakakahāvaṇṇanā':    'Dhutaṅgapakiṇṇakakathāvaṇṇanā',
     '9. Brāhmavihāraniddesavaṇṇanā':   '9. Brahmavihāraniddesavaṇṇanā',
     'Catudhātuvatthānabhāvanāvaṇṇanā': 'Catudhātuvavatthānabhāvanāvaṇṇanā'},
   'title': 'Visuddhimaggamahāṭīkā',
   'label': 'Visuddhimaggamahāṭīkā (Paṭhamo bhāgo)',
   'work': WVSM,
   'first': 1,
   'matika': (3, 7),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': VSM1,
   'levels': [None, LEAF],
 },
 # !!! THIS VOLUME PRINTS ITS OWN ERRATA SLIP, and it is not a section.
 # `Sodhanapattaṁ` (p218 of the file) heads a corrigendum: "p479 line 19 reads
 # `dvattiṁsajavanavīthīsū`, an unsound reading; take it as
 # `dvattijavanavīthīsū`" — and cites its own first bhāga p191 and the
 # Sāratthadīpanī p378 in support.  It is the EDITION correcting itself, so it
 # belongs in the errata record, not in the tree.  `matika_drop`.
 '26VsmT02': {
   'matika_drop': ('Sodhanapattaṁ',),
   'title': 'Visuddhimaggamahāṭīkā',
   'label': 'Visuddhimaggamahāṭīkā (Dutiyo bhāgo)',
   'work': WVSM,
   'first': 1,
   'matika': (3, 7),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': VSM2,
   'levels': [None, LEAF],
 },
}

A.SPEC.update(LAST_T)
A.main()
