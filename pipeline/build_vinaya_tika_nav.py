#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the seven Vinaya-Ṭīkā volumes — 25 books, GATED against each
volume's own printed mātikā.  SPEC and nothing else; the machinery is
`build_abhidhamma_nav`.

THESE WERE THE LAST TREES IN THE CORPUS NOT GATED AGAINST THE EDITION'S OWN
PRINTED LIST.  The version this replaces stopped at the printed book, because
on 2026-07-29q no Vinaya-Ṭīkā mātikā had been read.  All seven print one, and
unlike the Vinaya CANON's it is NOT finer than the body: 1,732 dotted entries
of which 1,698 resolve against the printed heads, 98 per cent.  So
`matika_gate` is available here, which it never was for the canon.

!!! THE HISTORY THE BOOKS-ONLY FILE CARRIED, KEPT.  `nav.json` once held, under
the Vinaya's subcommentary nikāya, TEN NODES THAT WERE WRONG AND ONE THAT WAS
FABRICATED:

    03ViT03  'Sāratthadīpanīṭīkā III'  #4
    03ViT03  'Vajirabuddhiṭīkā I'      #577      <- the Vajirabuddhiṭīkā is
    03ViT03  'Sāratthadīpanīṭīkā IV'   #582         06ViT06.  No part of it is
                                                    printed in 03ViT03.
    06ViT06  'Vajirabuddhiṭīkā II'     #0        <- there is no II; the work is
                                                    one volume entire.
    07ViT07  'Kaṅkhāvitaraṇīpurāṇaṭīkā'    #0
    07ViT07  'Kaṅkhāvitaraṇī-abhinavaṭīkā' #1    <- the abhinavaṭīkā opens at
                                                    ord115, 118 printed pages in.

and every `first` was keyed to the corpora replaced on 2026-07-29q.

FOUR THINGS THE MEASUREMENT SETTLED, ALL OF WHICH THIS FILE DEPENDS ON.

**`centred_indent: 12` on all seven.**  A centred line's indent falls as its
label grows, so the 18-space default loses 22 printed group heads across these
volumes — 03ViT03 alone loses `3. Vassūpanāyikakkhandhaka`,
`9. Campeyyakkhandhaka` and `10. Kosambakakkhandhaka`.  A gate that cannot see
an entry cannot refuse it.

**THE MĀTIKĀ IS SEGMENTED PER BOOK** (`matika_from`), because 06ViT06 lists the
Bhikkhu-vibhaṅga's kaṇḍas (1 Pārājika … 5 Pācittiya) and then the
Bhikkhunī-vibhaṅga's (1 Pārājika … 4 Pācittiya — no Aniyata, correctly), and
07ViT07 prints `Pārājikakaṇḍa` FOUR times, once per book.  Compared flat, the
second run's `3. Nissaggiyakaṇḍa` is measured against the first's
`4. Nissaggiyakaṇḍa` and the gate reports errata that do not exist.

**THE CLOSING COLOPHON IS THE THIRD WITNESS.**  Every section is closed by a
centred `… niṭṭhitā.` naming it again, so where the mātikā and the body differ
the colophon decides (`_tika/vt_witness.py`, `_tika/vt_gate_scout.py` — and the
probe must strip the section NUMBER first, since a colophon never carries one).
Of the disagreements: **the mātikā is the slip in 12, the body heading in 4, and
18 have no colophon and are UNRESOLVED.**  Every one of the 18 is declared here
too — `body_errata` is what lets the two sides be compared — but each is marked
UNRESOLVED in its comment and none is entered as an erratum.  **The body keeps
what it prints in every case; nothing here corrects the edition.**

**THE MĀTIKĀ'S SHAPE IS THE TREE'S SHAPE.**  Level 1 is `N. Xkaṇḍa` /
`N. Xkhandhaka` / the Parivāra's named sections; level 2, where a book has one,
is `N. Xvagga`, `N. Xpārājika`, `Santhatabhāṇavāra`.  Declared as LITERALS per
book, so `subtree`'s "the top level does not appear in printed order" refusal
is a real check and not a pattern that cannot fail.

Usage: python3 pipeline/build_vinaya_tika_nav.py <VOL> [--write]
"""
import build_abhidhamma_nav as A

WORK = 'Vinaya — Samantapāsādikā + subcommentaries'
LEAF = [r're:.']
FLAT = [r're:.']          # tops: an open set — every printed head is a top

VIT = {
  # -----------------------------------------------------------------------
  '01ViT01': {
   'title': 'Sāratthadīpanīṭīkā',
   'label': 'Sāratthadīpanī I',
   'work': WORK, 'first': 0,
   'matika': (13, 14),
   'matika_gate': True, 'matika_centred_gate': False,
   'centred_indent': 12, 'level_memo': True,
   # THE MĀTIKĀ PAGE'S OWN SECOND TITLE LINE, printed above the rule with the
   # volume name and answering to no section — 09DiT02's `Paṭhamabhāga`
   # exactly, and dropped for the same reason, from the mātikā side only.
   'matika_drop': ('Paṭhamabhāga',),
   # the title page's stack, printed as headings and drawn by `booktitle/`
   'head_skip': ('Vinayapiṭaka', 'Sāratthadīpanīṭīkā'),
   'books': [
     {'title': 'Ganthārambhakathā + Bāhiranidānavaṇṇanā',
      'lo': 0, 'hi': 12, 'anchor': 0,
      'tops': [
          'Bāhiranidānakathā',
      ],
      'levels': [None, LEAF]},
     {'title': 'Verañjakaṇḍavaṇṇanā',
      'lo': 12, 'hi': 45, 'anchor': 12,
      'matika_from': 'Verañjakaṇḍavaṇṇanā',
      'tops': FLAT,
      'levels': [None, LEAF]},
   ],
  },
  # -----------------------------------------------------------------------
  '02ViT02': {
   'title': 'Sāratthadīpanīṭīkā',
   'label': 'Sāratthadīpanī II',
   'work': WORK, 'first': 2,
   'matika': (3, 8),
   'matika_gate': True, 'matika_centred_gate': False,
   'centred_indent': 12, 'level_memo': True,
   # `1. Paṭhamapārājika` + `Sudinnabhāṇavāravaṇṇanā` are ONE printed heading.
   'matika_glue': ('1. Paṭhamapārājika',),
   # THE MĀTIKĀ ABBREVIATES WITH A PEYYĀLA WHERE THE BODY PRINTS IN FULL:
   # p6 `Adhiṭṭhāyāti -pa- payogakathāvaṇṇanā` against the body's p120
   # `Adhiṭṭhāyāti mātikāvasena āṇattikapayogakathāvaṇṇanā`, and the closing
   # colophon sets the full form.  That is the edition abbreviating its own
   # index, not a misprint, so it is normalised on the MĀTIKĀ side and not
   # entered as an erratum.
   'errata': {'Adhiṭṭhāyāti -pa- payogakathāvaṇṇanā':
              'Adhiṭṭhāyāti mātikāvasena āṇattikapayogakathāvaṇṇanā'},
   'body_errata': {
     # MĀTIKĀ IS THE SLIP — body p278 and the closing colophon both set
     # `4. Catutthapārājikavaṇṇanā`; the mātikā drops the `-vaṇṇanā`.
     '4. Catutthapārājikavaṇṇanā': '4. Catutthapārājika',
     # UNRESOLVED — body p384 `1. Civaravagga` with a SHORT i against the
     # mātikā's `1. Cīvaravagga`, and NO colophon closes the vagga by name, so
     # it is one witness against one.  *cīvara* is the word and every other
     # volume of the seven prints `Cīvaravagga`, but this volume does not say
     # so, and a reading is not settled by what other volumes print unless the
     # question is a conversion fault.  Declared so the two sides can be
     # compared; NOT entered as an erratum, and the body keeps what it prints.
     '1. Civaravagga': '1. Cīvaravagga'},
   'books': [
     {'title': 'Sāratthadīpanīṭīkā',
      'lo': 0, 'hi': 344, 'anchor': 2,
      'tops': [
          '1. Pārājikakaṇḍa',
          '2. Saṁghādisesakaṇḍa',
          '3. Aniyatakaṇḍa',
          '4. Nissaggiyakaṇḍa',
      ],
      'levels': [None, [
          '1. Paṭhamapārājika sudinnabhāṇavāravaṇṇanā',
          'Santhatabhāṇavāra',
          '2. Dutiyapārājika',
          '3. Tatiyapārājika',
          '4. Catutthapārājikavaṇṇanā',
          '1. Civaravagga',   # CHECK  mātikā '1. Cīvaravagga'
          '2. Kosiyavagga',
          '3. Pattavagga',
      ], LEAF]},
   ],
  },
  # -----------------------------------------------------------------------
  '03ViT03': {
   'title': 'Sāratthadīpanīṭīkā',
   'label': 'Sāratthadīpanī III',
   'work': WORK, 'first': 2,
   'matika': (3, 20),
   'matika_gate': True, 'matika_centred_gate': False,
   'centred_indent': 12, 'level_memo': True,
   'body_errata': {
     # MĀTIKĀ IS THE SLIP — body and colophon agree in both.
     '4. Padasodhammasikkhāpadavaṇṇanā': '4. Vadasodhammasikkhāpadavaṇṇanā',
     'Nissayapaṭippassaddhikathāvaṇṇanā': 'Nissayappaṭippassaddhikathāvaṇṇanā',
     # THE MĀTIKĀ OMITS A `-vaṇṇanā` THE BODY SETS, once in this volume — one
     # occurrence, so it is a literal here and not 06ViT06's volume-wide
     # `matika_suffix`.
     'Dutiyagāthāsaṅgaṇikavaṇṇanā': 'Dutiyagāthāsaṅgaṇika',
     # UNRESOLVED — no colophon closes either form by name.  Declared so the
     # gate can compare; the body keeps what it prints; no erratum entered.
     'Patimokkhuddesaka-ajjhesanādikathāvaṇṇanā':
         'Pātimokkhuddesaka-ajjhesanādikathāvaṇṇanā',
     'Antarāye anāpattivassacchedakavaṇṇanā':
         'Antarāye anāpattivassacchedakathāvaṇṇanā',
     'Apalokanakammakathāvaṇṇanā': 'Apalokenakammakathāvaṇṇanā'},
   'books': [
     {'title': 'Pācittiyakaṇḍa',
      'lo': 0, 'hi': 179, 'anchor': 2,
      'tops': [
          '5. Pācittiyakaṇḍa',
          '6. Pāṭidesanīyakaṇḍa',
          '7. Sekhiyakaṇḍa',
      ],
      'levels': [None, [
          '1. Musāvādavagga',
          '2. Bhūtagāmavagga',
          '3. Ovādavagga',
          '4. Bhojanavagga',
          '5. Acelakavagga',
          '6. Surāpānavagga',
          '7. Sappāṇakavagga',
          '8. Sahadhammikavagga',
          '9. Rājavagga',
      ], LEAF]},
     {'title': 'Bhikkhunīvibhaṅgavaṇṇanā',
      'lo': 179, 'hi': 240, 'anchor': 180,
      'matika_from': 'Bhikkhunīvibhaṅgavaṇṇanā',
      'tops': [
          '1. Pārājikakaṇḍa',
          '2. Saṁghādisesakaṇḍa',
          '4. Pācittiyakaṇḍa',
          '5. Pāṭidesanīyakaṇḍa',
      ],
      'levels': [None, LEAF]},
     {'title': 'Mahāvagga',
      'lo': 240, 'hi': 454, 'anchor': 241,
      'matika_from': 'Mahāvagga',
      'tops': [
          '1. Mahākhandhaka',
          '2. Uposathakkhandhaka',
          '3. Vassūpanāyikakkhandhaka',
          '4. Pavāraṇakkhandhaka',
          '5. Cammakkhandhaka',
          '6. Bhesajjakkhandhaka',
          '7. Kathinakkhandhaka',
          '8. Cīvarakkhandhaka',
          '9. Campeyyakkhandhaka',
          '10. Kosambakakkhandhaka',
      ],
      'levels': [None, LEAF]},
     {'title': 'Cūḷavagga',
      'lo': 454, 'hi': 593, 'anchor': 455,
      'matika_from': 'Cūḷavagga',
      'tops': [
          '1. Kammakkhandhaka',
          '2. Pārivāsikakkhandhaka',
          '3. Samuccayakkhandhaka',
          '4. Samathakkhandhaka',
          '5. Khuddakavatthukkhandhaka',
          '6. Senāsanakkhandhaka',
          '7. Saṁghabhedakakkhandhaka',
          '8. Vattakkhandhaka',
          '9. Pātimokkhaṭṭhapanakkhandhaka',
          '10. Bhikkhunikkhandhaka',
          '11. Pañcasatikakkhandhaka',
          '12. Sattasatikakkhandhaka',
      ],
      'levels': [None, LEAF]},
     {'title': 'Parivāra',
      'lo': 593, 'hi': 671, 'anchor': 594,
      'matika_from': 'Parivāra',
      'tops': [
          'Soḷasamahāvāra',
          'Antarapeyyāla',
          'Samathabheda',
          'Khandhakapucchāvāra',
          'Ekuttarikanaya',
          'Paṭhamagāthāsaṅgaṇika',
          'Dutiyagāthāsaṅgaṇikavaṇṇanā',
          'Aparadutiyagāthāsaṅgaṇika',
          'Sedamocanagāthā',
          'Pañcavagga',
      ],
      'levels': [None, LEAF]},
   ],
  },
  # -----------------------------------------------------------------------
  '04ViT04': {
   'title': 'Vimativinodanīṭīkā',
   'label': 'Vimativinodanī I',
   'work': WORK, 'first': 0,
   'matika': (3, 8),
   'matika_gate': True, 'matika_centred_gate': False,
   'centred_indent': 12, 'level_memo': True,
   'matika_glue': ('1. Paṭhamapārājika',),
   'head_skip': ('Vinayapiṭaka', 'Vimativinodanīṭīkā'),
   'body_errata': {
     # UNRESOLVED, both — no colophon closes either form by name.
     '2. Dutiyapārājikavaṇṇanā': '2. Dutiyapārājika',
     'Vatthukāmavārakathāvaṇṇanā': 'Vattukāmavārakathāvaṇṇanā'},
   'books': [
     {'title': 'Ganthārambhakathā + Bāhiranidānakathāvaṇṇanā',
      'lo': 0, 'hi': 10, 'anchor': 0,
      'tops': [
          'Bāhiranidānakathā',
      ],
      'levels': [None, LEAF]},
     {'title': 'Verañjakaṇḍavaṇṇanā',
      'lo': 10, 'hi': 302, 'anchor': 10,
      'matika_from': 'Verañjakaṇḍavaṇṇanā',
      'tops': [
          '1. Pārājikakaṇḍa',
          '2. Saṁghādisesakaṇḍa',
          '3. Aniyatakaṇḍa',
          '4. Nissaggiyakaṇḍa',
      ],
      'levels': [None, [
          '1. Paṭhamapārājika sudinnabhāṇavāravaṇṇanā',
          'Santhatabhāṇavāra',
          '2. Dutiyapārājikavaṇṇanā',
          '3. Tatiyapārājika',
          '4. Catutthapārājika',
          '1. Cīvaravagga',
          '2. Kosiyavagga',
          '3. Pattavagga',
      ], LEAF]},
   ],
  },
  # -----------------------------------------------------------------------
  '05ViT05': {
   'title': 'Vimativinodanīṭīkā',
   'label': 'Vimativinodanī II',
   'work': WORK, 'first': 2,
   'matika': (3, 17),
   'matika_gate': True, 'matika_centred_gate': False,
   'centred_indent': 12, 'level_memo': True,
   'body_errata': {
     # BODY IS THE SLIP — the mātikā and the closing colophon agree against it.
     '5. Paṭhamapavāraṇasikkhāpadavaṇṇanā': '5. Paṭhamapavāraṇāsikkhāpadavaṇṇanā',
     'Mahāpajātigotamīvatthukathāvaṇṇanā': 'Mahāpajāpatigotamīvatthukathāvaṇṇanā',
     # MĀTIKĀ IS THE SLIP — body and colophon agree.
     '5. Kabalavaggavaṇṇanā': '5. Kabaḷavaggavaṇṇanā',
     'Cha āpattisamuṭṭhānavāravaṇṇanā': 'Cha āpattisamuṭṭhānapāravaṇṇanā',
     # UNRESOLVED — body p306 `Upāḷipañcaka` against the mātikā's
     # `Upālipañcaka`, no colophon either way.  One witness against one.
     'Upāḷipañcaka': 'Upālipañcaka'},
   'books': [
     {'title': 'Pācittiyakaṇḍa',
      'lo': 0, 'hi': 179, 'anchor': 2,
      'tops': [
          '5. Pācittiyakaṇḍa',
          '6. Pāṭidesanīyakaṇḍa',
          '7. Sekhiyakaṇḍa',
      ],
      'levels': [None, [
          '1. Musāvādavagga',
          '2. Bhūtagāmavagga',
          '3. Ovādavagga',
          '4. Bhojanavagga',
          '5. Acelakavagga',
          '6. Surāpānavagga',
          '7. Sappāṇakavagga',
          '8. Sahadhammikavagga',
          '9. Rājavagga',
      ], LEAF]},
     {'title': 'Bhikkhunīvibhaṅgavaṇṇanā',
      'lo': 179, 'hi': 233, 'anchor': 180,
      'matika_from': 'Bhikkhunīvibhaṅgavaṇṇanā',
      'tops': [
          '1. Pārājikakaṇḍa',
          '2. Saṁghādisesakaṇḍa',
          '3. Nissaggiyakaṇḍa',
          '4. Pācittiyakaṇḍa',
          '5. Pāṭidesanīyakaṇḍa',
      ],
      'levels': [None, [
          '1. Lasuṇavagga',
          '2. Andhakāravagga',
          '3. Naggavagga',
          '4. Tuvaṭṭavagga',
          '5. Cittāgāravagga',
          '8. Kumāribhūtavagga',
      ], LEAF]},
     {'title': 'Mahāvaggavaṇṇanā',
      'lo': 233, 'hi': 450, 'anchor': 234,
      'matika_from': 'Mahāvaggavaṇṇanā',
      'tops': [
          '1. Mahākhandhaka',
          '2. Uposathakkhandhaka',
          '3. Vassūpanāyikakkhandhaka',
          '4. Pavāraṇākkhandhaka',
          '5. Cammakkhandhaka',
          '6. Bhesajjakkhandhaka',
          '7. Kathinakkhandhaka',
          '8. Cīvarakkhandhaka',
          '9. Campeyyakkhandhaka',
          '10. Kosambakakkhandhaka',
      ],
      'levels': [None, LEAF]},
     {'title': 'Cūḷavaggavaṇṇanā',
      'lo': 450, 'hi': 592, 'anchor': 451,
      'matika_from': 'Cūḷavaggavaṇṇanā',
      'tops': [
          '1. Kammakkhandhaka',
          '2. Pārivāsikakkhandhaka',
          '3. Samuccayakkhandhaka',
          '4. Samathakkhandhaka',
          '5. Khuddakavatthukkhandhaka',
          '6. Senāsanakkhandhaka',
          '7. Saṁghabhedakakkhandhaka',
          '8. Vattakkhandhaka',
          '9. Pātimokkhaṭṭhapanakkhandhaka',
          '10. Bhikkhunikkhandhaka',
          '11. Pañcasatikakkhandhaka',
          '12. Sattasatikakkhandhaka',
      ],
      'levels': [None, LEAF]},
     {'title': 'Parivāravaṇṇanā',
      'lo': 592, 'hi': 693, 'anchor': 593,
      'matika_from': 'Parivāravaṇṇanā',
      'tops': [
          'Mahāvagga',
          'Antarapeyyāla',
          'Samathabheda',
          'Khandhakapucchāvāra',
          'Ekuttarikanaya',
          'Paññattivagga',
          'Paṭhamagāthāsaṅgaṇika',
          'Adhikaraṇabheda',
          'Dutiyagāthāsaṅgaṇika',
          'Codanākaṇḍa',
          'Cūḷasaṅgāma',
          'Mahāsaṅgāma',
          'Kathinabheda',
          'Saṅgahavagga',
          'Upāḷipañcaka',   # CHECK  mātikā 'Upālipañcaka'
          'Aparadutiyagāthāsaṅgaṇika',
          'Sedamocanagāthā',
          'Pañcavagga',
      ],
      'levels': [None, LEAF]},
   ],
  },
  # -----------------------------------------------------------------------
  '06ViT06': {
   'title': 'Vajirabuddhiṭīkā',
   'label': 'Vajirabuddhiṭīkā',
   'work': WORK, 'first': 0,
   'matika': (3, 26),
   'matika_gate': True, 'matika_centred_gate': False,
   'centred_indent': 12, 'level_memo': True,
   # !!! THIS VOLUME'S MĀTIKĀ OMITS THE `-vaṇṇanā` ITS BODY SETS ON A GROUP
   # HEAD — 51 of its 540 rows, every kaṇḍa, khandhaka, vagga and Parivāra
   # section of its last four books, while its first two books carry neither
   # side's suffix.  A convention of the volume, not 51 misprints: declared as
   # ONE rule so the four rows that really are disagreements stay visible.
   # Measured across the seven: 51 here, 0/1/1/1/0/0 elsewhere, which is why
   # the other six declare their singletons as `body_errata` instead.
   'matika_suffix': ('vaṇṇanā',),
   'matika_glue': ('1. Paṭhamapārājika',),
   # !!! HERE THE MĀTIKĀ IS FINER THAN THE BODY, in exactly two places, and
   # both are the Parivāra's `-ādi` headings.  The mātikā names the sub-vāras
   #     `Yatthavāra, pucchāvāravaṇṇanā`      (p546)
   #     `Samathavāra, vissajjanāvāravaṇṇanā` (p548)
   # where the body heads the group and says "and the rest":
   #     `Cha-āpattisamuṭṭhānavārādivaṇṇanā`  (ord776)
   #     `Adhikaraṇapariyāyavārādivaṇṇanā`    (ord782)
   # — the `-ādi` is the edition's own statement that the heading covers more
   # than it names, so there is no missing heading to find and nothing to
   # correct.  Dropped from the MĀTIKĀ side with the reason, as 09DiT02's
   # `Paṭhamabhāga` is, and NOT entered as an erratum.
   'matika_drop': ('Yatthavāra, pucchāvāravaṇṇanā',
                   'Samathavāra, vissajjanāvāravaṇṇanā'),
   'head_skip': ('Vinayapiṭaka', 'Vajirabuddhiṭīkā'),
   'body_errata': {
     # BODY IS THE SLIP — p286 heads `1. Bhūtagāmasikkhāpadadaṇṇanā` for
     # `-vaṇṇanā`, and its own mātikā and colophon both read `-vaṇṇanā`.
     # **THE PRINTED PAGE, NOT OUR CONVERSION** — checked in `pdftotext`.
     '1. Bhūtagāmasikkhāpadadaṇṇanā': '1. Bhūtagāmasikkhāpadavaṇṇanā',
     # MĀTIKĀ IS THE SLIP — body and colophon agree.
     'Vatthukāmavārakathāvaṇṇanā': 'Vattukāmavārakathāvaṇṇanā',
     # UNRESOLVED — no colophon closes either form by name.
     'Pavāraṇādānanujānanakathāvaṇṇanā': 'Pavāraṇādānānujānanakathāvaṇṇanā',
     'Vassaṁvutthānaṁanuppannacīvarakathāvaṇṇanā':
         'Vassaṁvuttānaṁanuppannacīvarakathāvaṇṇanā',
     'Katāpattivārādivaṇṇanā': 'Kathāpattivārādivaṇṇanā',
     'Catukkavāravaṇṇanā': 'Catutthavāravaṇṇanā',
     'Pañcakavāravaṇṇanā': 'Pañcamavāravaṇṇanā'},
   'books': [
     {'title': 'Ganthārambhakathā + Bāhiranidānavaṇṇanā',
      'lo': 0, 'hi': 8, 'anchor': 0,
      'tops': [
          'Bāhiranidānakathāvaṇṇanā',
      ],
      'levels': [None, LEAF]},
     {'title': 'Verañjakaṇḍavaṇṇanā',
      'lo': 8, 'hi': 387, 'anchor': 8,
      'matika_from': 'Verañjakaṇḍa',
      'tops': [
          '1. Pārājikakaṇḍa',
          '2. Saṁghādisesakaṇḍa',
          '3. Aniyatakaṇḍa',
          '4. Nissaggiyakaṇḍa',
          '5. Pācittiyakaṇḍa',
          '6. Pāṭidesanīyakaṇḍa',
          '7. Sekhiyakaṇḍa',
      ],
      'levels': [None, [
          '1. Paṭhamapārājika sudinnabhāṇavāravaṇṇanā',
          '2. Dutiyapārājika',
          '3. Tatiyapārājika',
          '4. Catutthapārājika',
          '1. Cīvaravagga',
          '2. Kosiyavagga',
          '3. Pattavagga',
          '1. Musāvādavagga',
          '2. Bhūtagāmavagga',
          '3. Ovādavagga',
          '4. Bhojanavagga',
          '5. Acelakavagga',
          '6. Surāpānavagga',
          '7. Sappāṇakavagga',
          '8. Sahadhammikavagga',
          '9. Ratanavagga',
      ], LEAF]},
     {'title': 'Bhikkhunīvibhaṅgavaṇṇanā',
      'lo': 387, 'hi': 487, 'anchor': 388,
      'matika_from': 'Bhikkhunīvibhaṅga',
      'tops': [
          '1. Pārājikakaṇḍavaṇṇanā',
          '2. Saṁghādisesakaṇḍavaṇṇanā',
          '3. Nissaggiyakaṇḍavaṇṇanā',
          '4. Pācittiyakaṇḍavaṇṇanā',
      ],
      'levels': [None, [
          '1. Lasuṇavagga',
          '2. Andhakāravaggavaṇṇanā',
          '3. Naggavaggavaṇṇanā',
          '4. Tuvaṭṭavaggavaṇṇanā',
          '5. Cittāgāravaggavaṇṇanā',
          '6. Ārāmavaggavaṇṇanā',
          '7. Gabbhinivaggavaṇṇanā',
          '8. Kumāribhūtavaggavaṇṇanā',
          '9. Chattupāhanavaggavaṇṇanā',
      ], LEAF]},
     {'title': 'Mahāvaggavaṇṇanā',
      'lo': 487, 'hi': 660, 'anchor': 488,
      'matika_from': 'Mahāvaggavaṇṇanā',
      'tops': [
          '1. Mahākhandhakavaṇṇanā',
          '2. Uposathakkhandhakavaṇṇanā',
          '3. Vassūpanāyikakkhandhakavaṇṇanā',
          '4. Pavāraṇākkhandhakavaṇṇanā',
          '5. Cammakkhandhakavaṇṇanā',
          '6. Bhesajjakkhandhakavaṇṇanā',
          '7. Kathinakkhandhakavaṇṇanā',
          '8. Cīvarakkhandhakavaṇṇanā',
          '9. Campeyyakkhandhakavaṇṇanā',
          '10. Kosambakakkhandhakavaṇṇanā',
      ],
      'levels': [None, LEAF]},
     {'title': 'Cūḷavaggavaṇṇanā',
      'lo': 660, 'hi': 765, 'anchor': 661,
      'matika_from': 'Cūḷavaggavaṇṇanā',
      'tops': [
          '1. Kammakkhandhakavaṇṇanā',
          '2. Pārivāsikakkhandhakavaṇṇanā',
          '3. Samuccayakkhandhakavaṇṇanā',
          '4. Samathakkhandhakavaṇṇanā',
          '5. Khuddakavatthukkhandhakavaṇṇanā',
          '6. Senāsanakkhandhakavaṇṇanā',
          '7. Saṁghabhedakakkhandhakavaṇṇanā',
          '8. Vattakkhandhakavaṇṇanā',
          '9. Pātimokkhaṭṭhapanakkhandhakavaṇṇanā',
          '10. Bhikkhunikkhandhakavaṇṇanā',
          '11. Pañcasatikakkhandhakavaṇṇanā',
          '12. Sattasatikakkhandhakavaṇṇanā',
      ],
      'levels': [None, LEAF]},
     {'title': 'Parivāravaṇṇanā',
      'lo': 765, 'hi': 860, 'anchor': 766,
      'matika_from': 'Parivāravaṇṇanā',
      'tops': [
          'Soḷasamahāvāravaṇṇanā',
          'Samuṭṭhānasīsavaṇṇanā',
          'Antarapeyyāla',
          'Samathabhedavaṇṇanā',
          'Khandhakapucchāvāravaṇṇanā',
          'Ekuttarikanayavaṇṇanā',
          'Paṭhamagāthāsaṅgaṇikavaṇṇanā',
          'Adhikaraṇabhedavaṇṇanā',
          'Dutiyagāthāsaṅgaṇikavaṇṇanā',
          'Codanākaṇḍavaṇṇanā',
          'Cūḷasaṅgāmavaṇṇanā',
          'Mahāsaṅgāmavaṇṇanā',
          'Kathinabhedavaṇṇanā',
          'Upālipañcakavaṇṇanā',
          'Dutiyagāthāsaṅgaṇikavaṇṇanā',
          'Sedamocanagāthāvaṇṇanā',
          'Pañcavagga',
      ],
      'levels': [None, LEAF]},
   ],
  },
  # -----------------------------------------------------------------------
  '07ViT07': {
   'title': 'Kaṅkhāvitaraṇīpurāṇaṭīkā',
   'label': 'Kaṅkhāvitaraṇīpurāṇaṭīkā + Kaṅkhāvitaraṇī-abhinavaṭīkā',
   'work': WORK, 'first': 0,
   'matika': (3, 20),
   'matika_gate': True, 'matika_centred_gate': False,
   'centred_indent': 12, 'level_memo': True,
   'body_errata': {
     # BODY IS THE SLIP — the mātikā and the closing colophon agree against it.
     # p433 `60. Āvupoṇisikkhāpadavaṇṇanā` where both read `Āvudhapāṇi-`;
     # **THE PRINTED PAGE, NOT OUR CONVERSION** — checked in `pdftotext`.
     '60. Āvupoṇisikkhāpadavaṇṇanā': '60. Āvudhapāṇisikkhāpadavaṇṇanā',
     '9. Paṇitabhojanasikkhāpadavaṇṇanā': '9. Paṇītabhojanasikkhāpadavaṇṇanā',
     # MĀTIKĀ IS THE SLIP — body and colophon agree.
     '10. Rājasikkhāpadavaṇṇanā': '10. Rājāsikkhāpadavaṇṇanā',
     '8. Sannidhikārakasikkhāpadavaṇṇanā': '8. Sinnidhikārakasikkhāpadavaṇṇanā',
     '3. Hasadhammasikkhāpadavaṇṇanā': '3. Hāsadhammasikkhāpadavaṇṇanā',
     '61-62. Pādukasikkhāpadavaṇṇanā': '61-62. Padukasikkhāpadavaṇṇanā',
     '1. Methunadhammasikkhāpadavaṇṇanā': '1. Methunasikkhāpadavaṇṇanā',
     # THREE NAMES FOR ONE SECTION, AND NONE OF THEM IS A MISPRINT.  The
     # mātikā lists `Pakiṇṇakavaṇṇanā` (p84), the body heads
     # `Tatridaṁ pakiṇṇakaṁ` — "herein this is the miscellany", the edition
     # naming the section in a sentence — and the closing colophon reads
     # `Pakiṇṇakaṁ niṭṭhitaṁ.`  All three are printed and all three stand.
     # Declared so the two sides can be compared; the body keeps what it
     # prints, and this is NOT an erratum.
     'Tatridaṁ pakiṇṇakaṁ': 'Pakiṇṇakavaṇṇanā'},
   'books': [
     {'title': 'Kaṅkhāvitaraṇīpurāṇaṭīkā',
      'lo': 0, 'hi': 100, 'anchor': 0,
      'tops': [
          'Pārājikakaṇḍa',
          'Saṁghādisesakaṇḍa',
          'Aniyatakaṇḍa',
          'Nissaggiyakaṇḍa',
          'Pācittiyakaṇḍa',
          'Pāṭidesanīyakaṇḍa',
      ],
      'levels': [None, [
          '1. Cīvaravagga',
          '2. Eḷakalomavagga',
          '3. Pattavagga',
          '4. Bhojanavagga',
          '5. Acelakavagga',
          '6. Surāpānavagga',
          '7. Sappāṇakavagga',
          '8. Sahadhammikavagga',
          '9. Ratanavagga',
      ], LEAF]},
     {'title': 'Bhikkhunīpātimokkhavaṇṇanā',
      'lo': 100, 'hi': 115, 'anchor': 100,
      'matika_from': 'Bhikkhunīpātimokkhavaṇṇanā',
      'tops': [
          'Saṁghādisesakaṇḍa',
          'Pācittiyakaṇḍa',
      ],
      'levels': [None, LEAF]},
     {'title': 'Kaṅkhāvitaraṇī-abhinavaṭīkā',
      'lo': 115, 'hi': 302, 'anchor': 115,
      'matika_from': 'Ganthārambhakathā',
      'tops': [
          'Pārājikakaṇḍa',
          'Saṁghādisesakaṇḍa',
          'Aniyatakaṇḍa',
          'Nissaggiyakaṇḍa',
          'Pācittiyakaṇḍa',
          'Pāṭidesanīyakaṇḍa',
          'Sekhiyakaṇḍa',
      ],
      'levels': [None, [
          '1. Cīvaravagga',
          '2. Eḷakalomavagga',
          '3. Pattavagga',
          '1. Musāvādavagga',
          '2. Bhūtagāmavagga',
          '3. Ovādavagga',
          '4. Bhojanavagga',
          '5. Acelakavagga',
          '6. Surāpānavagga',
          '7. Sappāṇakavagga',
          '8. Sahadhammikavagga',
          '9. Ratanavagga',
      ], LEAF]},
     {'title': 'Bhikkhunīpātimokkhavaṇṇanā',
      'lo': 302, 'hi': 420, 'anchor': 302,
      'matika_from': 'Bhikkhunīpātimokkhavaṇṇanā',
      'tops': [
          'Pārājikakaṇḍa',
          'Saṁghādisesakaṇḍa',
          'Nissaggiyakaṇḍa',
          'Pācittiyakaṇḍa',
          'Pāṭidesanīyakaṇḍa',
      ],
      'levels': [None, [
          'Sādhāraṇapārājika',
          'Asādhāraṇapārājika',
          '1. Pattavagga',
          '2. Cīvaravagga',
          '1. Lasuṇavagga',
          '2. Rattandhakāravagga',
          '3. Naggavagga',
          '4. Tuvaṭṭavagga',
          '5. Cittāgāravagga',
          '6. Ārāmavagga',
          '7. Gabbhinīvagga',
          '8. Kumāribhūtavagga',
          '9. Chattupāhanavagga',
      ], LEAF]},
   ],
  },
}

A.SPEC.update(VIT)
A.main()
