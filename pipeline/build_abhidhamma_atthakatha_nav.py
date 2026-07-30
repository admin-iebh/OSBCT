#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Navs for the Abhidhamma commentaries, 48AbhiA01-50AbhiA03.

    48AbhiA01  AṬṬHASĀLINĪ            on the Dhammasaṅgaṇī
    49AbhiA02  SAMMOHAVINODANĪ        on the Vibhaṅga
    50AbhiA03  PAÑCAPAKARAṆA-AṬṬHAKATHĀ  on the remaining FIVE books

All three had their corpus rebuilt on 2026-07-27an.
"""
import build_abhidhamma_nav as A

WORK = 'Abhidhamma — commentaries'
VANNANA = r're:\d+(?:-\d+)?\.\s+.*vaṇṇanā$'

ABHIDHAMMA_A = {
 '48AbhiA01': {
   'title': 'Aṭṭhasālinī-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (13, 14),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # THE TOP LEVEL IS THE ONE THE CANON VOLUME HAS.  29Abhi01, the
   # Dhammasaṅgaṇī itself, sets `Mātikā` + the four kaṇḍas; the commentary
   # replaces the bare Mātikā with its own `Ganthārambhakathā` and keeps the
   # four.  Both the printed mātikā (pp xi-xii) and the body set all five
   # CENTRED, which `matika_centred_gate` checks.
   'tops': ['Ganthārambhakathā', '1. Cittuppādakaṇḍa', '2. Rūpakaṇḍa',
            '3. Nikkhepakaṇḍa', '4. Aṭṭhakathākaṇḍa'],
   # THE SECOND LEVEL IS THE PRINTED MĀTIKĀ'S OWN FLUSH-LEFT ENTRIES, listed as
   # the BODY prints them.  The mātikā distinguishes the two depths by INDENT —
   # flush left for these, indented for their children — so this list is read
   # off the page, not invented.  Anything else falls to level 2.
   'levels': [None,
     ['Nidānakathā',
      'Tikamātikāpadavaṇṇanā', 'Dukamātikāpadavaṇṇanā',
      'Suttantikadukamātikāpadavaṇṇanā', 'Kāmāvacarakusalapadabhājanīya',
      'Kāmāvacarakusala dvārakathā', 'Rūpāvacarakusalavaṇṇanā',
      'Arūpāvacarakusalavaṇṇanā', 'Tebhūmakakusalavaṇṇanā',
      'Lokuttarakusalavaṇṇanā', 'Akusalapada dhammuddesavārakathā',
      'Abyākatapada ahetukakusalavipāka',
      'Uddesavaṇṇanā', 'Rūpavibhatti-ekakaniddesavaṇṇanā', 'Pakiṇṇakakathā',
      'Tikanikkhepakathā', 'Dukanikkhepakathā', 'Suttantikadukanikkhepakathā',
      'Tika-atthuddhāravaṇṇanā', 'Duka-atthuddhāravaṇṇanā', 'Nigamanakathā'],
     [r're:.']],
   # Two mātikā entries the body heads differently; one each side, so `errata`.
   #  * the mātikā names the whole section `Dhammuddesavārakathā` (p150) —
   #    which is also what its CLOSING colophon says (`Dhammuddesavārakathā
   #    niṭṭhitā.`, p194) — where the opening heading on p150 is the fuller
   #    `Dhammuddesavāra phassapañcamakarāsivaṇṇanā`.
   #  * `Koṭṭhāsavāravaṇṇanā` (p196) is headed `Koṭṭhāsavāra` in the body.
   # Neither side is corrected; the two readings are named as the same section.
   'errata': {'Dhammuddesavārakathā': 'Dhammuddesavāra phassapañcamakarāsivaṇṇanā',
              'Koṭṭhāsavāravaṇṇanā':  'Koṭṭhāsavāra'},
   # !!! `body_errata`, NOT `errata`.  The mātikā lists `Niddesavārakathā`
   # TWICE — p180 under the Kāmāvacarakusaladvārakathā and p294 under the
   # Akusalapada — and the body heads the first `Kāmāvacarakusala
   # niddesavārakathā` (ord89) and the second `Niddesavārakathā` (ord156).
   # `errata` rewrites a mātikā reading GLOBALLY and would collapse both
   # entries onto the first body heading, stranding ord156.  Same distinction
   # 49AbhiA02's `Pañcakaniddesavaṇṇā` and 35Abhi07's `Nava dhammā` taught.
   'body_errata': {'Kāmāvacarakusala niddesavārakathā': 'Niddesavārakathā'},
 },
 '49AbhiA02': {
   'title': 'Sammohavinodanī-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 8),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # Four errata, key = mātikā reading, value = body reading.  The last is not
   # a spelling at all: the MĀTIKĀ runs two body headings onto one line, where
   # the body prints `Dhammānupassanāniddesavaṇṇanā` and `Nīvaraṇapabba`
   # separately.  Joined to the first of the two; neither side corrected.
   'errata': {'Jārāniddesa':                    'Jarāniddesa',
              'Vedānānupassanādi-uddesavaṇṇanā': 'Vedanānupassanādi-uddesavaṇṇanā',
              'Vedānānupassanāniddesavaṇṇanā':   'Vedanānupassanāniddesavaṇṇanā',
              'Dhammānupassanāniddesavaṇṇanā nīvaraṇapabba':
                  'Dhammānupassanāniddesavaṇṇanā',
             },
   # !!! `body_errata`, NOT `errata`.  `5. Pañcakaniddesavaṇṇanā` is printed
   # TWICE in the body — correctly at ord293 and as `…vaṇṇā` at ord204 — and
   # the mātikā lists it twice as well (printed pp402 and 485).  `errata`
   # rewrites a mātikā entry GLOBALLY and is right only when the misprint
   # occurs ONCE ON EACH SIDE; here it would rewrite both mātikā entries to the
   # misprint and strand the correctly-spelt body heading.  `body_errata` puts
   # the alternative on the TREE side instead, so each printing keeps its own
   # reading.  Same distinction 35Abhi07's `Nava dhammā` taught (2026-07-26ad).
   'body_errata': {'5. Pañcakaniddesavaṇṇā': '5. Pañcakaniddesavaṇṇanā'},
   # The eighteen vibhaṅgas, NUMBERED 1..18 WITH NO GAP — which is the check
   # that none was missed, and the same eighteen the canon 30Abhi02 carries.
   'tops': ['1. Khandhavibhaṅga', '2. Āyatanavibhaṅga', '3. Dhātuvibhaṅga',
            '4. Saccavibhaṅga', '5. Indriyavibhaṅga',
            '6. Paṭiccasamuppādavibhaṅga', '7. Satipaṭṭhānavibhaṅga',
            '8. Sammappadhānavibhaṅga', '9. Iddhipādavibhaṅga',
            '10. Bojjhaṅgavibhaṅga', '11. Maggaṅgavibhaṅga',
            '12. Jhānavibhaṅga', '13. Appamaññāvibhaṅga',
            '14. Sikkhāpadavibhaṅga', '15. Paṭisambhidāvibhaṅga',
            '16. Ñāṇavibhaṅga', '17. Khuddakavatthuvibhaṅga',
            '18. Dhammahadayavibhaṅga'],
   'levels': [None, [VANNANA], [r're:.']],
 },
 '50AbhiA03': {
   'title': 'Pañcapakaraṇa-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 12),
   'matika_gate': True,
   'level_memo': True,
   'tops': [],
   # FIVE BOOKS, each with its own title page and homage, and each with its own
   # section of the printed front mātikā (idx 3, 4, 4-7, 8-9, 10-12).  The
   # ordinal bounds are the corpus paragraphs that open each homage page,
   # checked against the title pages at 0-based 13, 37, 117, 299 and 353.
   'books': [
     {'title': 'Dhātukathā-aṭṭhakathā', 'lo': 0, 'hi': 64,
      'tops': ['1. Mātikāvaṇṇanā', '2. Niddesavaṇṇanā', 'Nigamanakathā'],
      'levels': [None, [r're:.']]},
     {'title': 'Puggalapaññatti-aṭṭhakathā', 'lo': 64, 'hi': 210,
      'tops': ['1. Mātikāvaṇṇanā', '2. Niddesavaṇṇanā', 'Nigamanakathā'],
      'levels': [None, [r're:.']]},
     # THE KATHĀVATTHU'S FIRST VAGGA IS NOT PRINTED AS A VAGGA.  Its nine
     # kathās are set as centred heads in their own right and the printed
     # mātikā lists them at the same depth as the vaggas that follow, so the
     # top level here is `Nidānakathā`, those nine, then vaggas 2-23 and the
     # closing `Nigamanakathā` — the page's own order, not a normalisation.
     {'title': 'Kathāvatthu-aṭṭhakathā', 'lo': 210, 'hi': 606,
      'tops': ['Nidānakathā',
               '1. Puggalakathā', '2. Parihānikathā', '3. Brahmacariyakathā',
               '4. Jahatikathā', '5. Sabbamatthītikathā',
               '6. Atītakkhandhādikathā', '7. Ekaccaṁatthītikathā',
               '8. Satipaṭṭhānakathāvaṇṇanā', '9. Hevatthikathāvaṇṇanā',
               '2. Dutiyavagga',
               '3. Tatiyavagga',
               '4. Catutthavagga',
               '5. Pañcamavagga',
               '6. Chaṭṭhavagga',
               '7. Sattamavagga',
               '8. Aṭṭhamavagga',
               '9. Navamavagga',
               '10. Dasamavagga',
               '11. Ekādasamavagga',
               '12. Dvādasamavagga',
               '13. Terasamavagga',
               '14. Cuddasamavagga',
               '15. Pannarasamavagga',
               '16. Soḷasamavagga',
               '17. Sattarasamavagga',
               '18. Aṭṭhārasamavagga',
               '19. Ekūnavīsatimavagga',
               '20. Vīsatimavagga',
               '21. Ekavīsatimavagga',
               '22. Bāvīsatimavagga',
               '23. Tevīsatimavagga',
               'Nigamanakathā'],
      'levels': [None, [r're:.']]},
     {'title': 'Yamakappakaraṇaṭṭhakathā', 'lo': 606, 'hi': 688,
      'tops': ['1. Mūlayamaka', '2. Khandhayamaka', '3. Āyatanayamaka', '4. Dhātuyamaka', '5. Saccayamaka', '6. Saṅkhārayamaka', '7. Anusayayamaka', '8. Cittayamaka', '9. Dhammayamaka', '10. Indriyayamaka', 'Nigamanakathā'],
      # `Mahāvāra` and `Niddesa` are divisions INSIDE a yamaka (the Anusaya's
      # and the Citta's), each sharing its printed line with its first vāra —
      # see `split_unnumbered` / `split_literals` in the builder's SPEC.
      'levels': [None, ['Mahāvāra', 'Niddesa'], [r're:.']]},
     {'title': 'Paṭṭhānappakaraṇaṭṭhakathā', 'lo': 688, 'hi': 883,
      'tops': [
               'Paccayuddesavaṇṇanā',
               'Paccayaniddesa',
               'Paccayaniddesapakiṇṇakavinicchayakathā',
               'Pucchāvāra',
               '1. Kusalattika',
               '2. Vedanāttikavaṇṇanā',
               '3. Vipākattikavaṇṇanā',
               '4. Upādinnattikavaṇṇanā',
               '5-22. Saṁkiliṭṭhattikādivaṇṇanā',
               '2. Dukapaṭṭhānavaṇṇanā',
               '3. Dukatikapaṭṭhānavaṇṇanā',
               '4. Tikadukapaṭṭhānavaṇṇanā',
               '5. Tikatikapaṭṭhānavaṇṇanā',
               '6. Dukadukapaṭṭhānavaṇṇanā',
               '7-12. Paccanīyapaṭṭhānavaṇṇanā',
               '13-18. Anulomapaccanīyapaṭṭhānavaṇṇanā',
               '19-24. Paccanīyānulomapaṭṭhānavaṇṇanā',
               'Nigamanakathā'],
      'levels': [None, [r're:.']]},
   ],
   # THE MĀTIKĀ'S `-ādi` COMPRESSION, twenty-three times.  From the second
   # vagga on, the Kathāvatthu's mātikā names each vagga by its FIRST kathā
   # with `-ādi` appended (`1. Balakathādivaṇṇanā` for what the body heads
   # `1. Balakathāvaṇṇanā`), and the Dhātukathā's mātikā does the same for
   # `2. Abbhantaramātikādivaṇṇanā`.  Each is named rather than stripped by a
   # rule: a rule that dropped `ādi` before `vaṇṇanā` would also rewrite the
   # SEVEN entries where `-ādi` is part of the section's own name and the body
   # prints it too (`15-18. Ñātakānuyogādivaṇṇanā`,
   # `5-22. Saṁkiliṭṭhattikādivaṇṇanā` and five more), which the diff proves by
   # matching those without help.  Neither side is corrected.
   #
   # The last entry is not a compression but a misprint: the mātikā sets
   # `1. Vādayuttiparihānivaṇṇanā` where the body (p141) sets
   # `1. Vādayuttiparihānavaṇṇanā`, `i` for `a`.  PRESERVED on both sides.
   'errata': {
      '2. Abbhantaramātikādivaṇṇanā':
          '2. Abbhantaramātikāvaṇṇanā',
      '1. Parūpahārādivaṇṇanā':
          '1. Parūpahāravaṇṇanā',
      '1. Balakathādivaṇṇanā':
          '1. Balakathāvaṇṇanā',
      '1. Gihissa arahātikathādivaṇṇanā':
          '1. Gihissa arahātikathāvaṇṇanā',
      '1. Vimuttikathādivaṇṇanā':
          '1. Vimuttikathāvaṇṇanā',
      '1. Niyāmakathādivaṇṇanā':
          '1. Niyāmakathāvaṇṇanā',
      '1. Saṅgahitakathādivaṇṇanā':
          '1. Saṅgahitakathāvaṇṇanā',
      '1. Chagatikathādivaṇṇanā':
          '1. Chagatikathāvaṇṇanā',
      '1. Ānisaṁsadassāvīkathādivaṇṇanā':
          '1. Ānisaṁsadassāvīkathāvaṇṇanā',
      '1. Nirodhakathādivaṇṇanā':
          '1. Nirodhakathāvaṇṇanā',
      '1-3. Tissopi-anusayakathādivaṇṇanā':
          '1-3. Tissopi-anusayakathāvaṇṇanā',
      '1. Saṁvaro kammantikathādivaṇṇanā':
          '1. Saṁvaro kammantikathāvaṇṇanā',
      '1. Kappaṭṭhakathādivaṇṇanā':
          '1. Kappaṭṭhakathāvaṇṇanā',
      '1. Kusalākusalapaṭisandahanakathādivaṇṇanā':
          '1. Kusalākusalapaṭisandahanakathāvaṇṇanā',
      '1. Paccayatākathādivaṇṇanā':
          '1. Paccayatākathāvaṇṇanā',
      '1. Niggahakathādivaṇṇanā':
          '1. Niggahakathāvaṇṇanā',
      '1. Atthi-arahatopuññūpacayakathādivaṇṇanā':
          '1. Atthi-arahatopuññūpacayakathāvaṇṇanā',
      '1. Manussalokakathādivaṇṇanā':
          '1. Manussalokakathāvaṇṇanā',
      '1. Kilesapajahanakathādivaṇṇanā':
          '1. Kilesapajahanakathāvaṇṇanā',
      '1. Asañciccakathādivaṇṇanā':
          '1. Asañciccakathāvaṇṇanā',
      '1. Sāsanakathādivaṇṇanā':
          '1. Sāsanakathāvaṇṇanā',
      '1. Parinibbānakathādivaṇṇanā':
          '1. Parinibbānakathāvaṇṇanā',
      '1. Ekādhippāyakathādivaṇṇanā':
          '1. Ekādhippāyakathāvaṇṇanā',
      '1. Vādayuttiparihānivaṇṇanā':
          '1. Vādayuttiparihānavaṇṇanā',
   },
   # !!! FLAGGED, NOT SILENCED.  `1. Paccayānulomavaṇṇanā` (printed p394) is a
   # real centred heading that the CORPUS REBUILD swallowed: `rebuild_corpus.py`
   # restored the unnumbered prose below it and did not break at the heading, so
   # ord716 begins `Pucchāvāra    1. Paccayānulomavaṇṇanā Evaṁ
   # anulomapaṭṭhānādīsu…` and the printed line is drawn as the first words of
   # that paragraph instead of as its heading.  Its three siblings
   # (`2. Paccayapaccanīyavaṇṇanā`, `3. Anulomapaccanīyavaṇṇanā`,
   # `4. Paccanīyānulomavaṇṇanā`) are NOT in the corpus and are read from the
   # printed stream, so only this one is affected.  Same class as 01VinA01 ¶14
   # and 18AnA02 ord463 — the divergence is RECORDED, not corrected, and no
   # text is lost or moved.
   'matika_drop': ['1. Paccayānulomavaṇṇanā'],
 },
}

A.SPEC.update(ABHIDHAMMA_A)
A.main()
