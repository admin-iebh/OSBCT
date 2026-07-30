#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the three Abhidhamma-Ṭīkā volumes.  SPEC only; the machinery is
`build_abhidhamma_nav`, and the mātikā gate is the point (2026-07-29r).

!!! THE THREE NODES THIS REPLACES WERE GENERATED, NOT READ — and `_navdup`
has been listing all three as "awaiting a real nav, several top nodes".

EACH VOLUME CARRIES TWO WORKS: Ānanda's MŪLAṬĪKĀ and Dhammapāla's ANUṬĪKĀ
upon it.  Fourteen books in all, and the two halves of each volume have the
SAME structure — 4 kaṇḍas each, 18 vibhaṅgas each, five pakaraṇas each — which
is the check that no book was missed.

    22AbhiT01  mātikā 0-based 13-20   body  22-460   2 books   4 + 4 kaṇḍas
    23AbhiT02  mātikā          3-14   body  16-494   2 books  18 + 18 vibhaṅgas
    24AbhiT03  mātikā          3-35   body  37-610  10 books   5 + 5 pakaraṇas

EACH VOLUME PRINTS TWO MĀTIKĀS, one per work, and they stand in the bodies'
own order — so a single range covers both, as 15MaT03's two did.

!!! AND THE BOOK PAGE RANGES SKIP THE FIRST WORK'S WORD INDEX, which this
edition prints BETWEEN the two works.  See `_tika/cut_index_run.py`.

Usage: python3 pipeline/build_abhidhamma_tika_nav.py <VOL> [--write]
"""
import build_abhidhamma_nav as A

W22 = 'Dhammasaṅgaṇī — Aṭṭhasālinī + subcommentaries'
W23 = 'Vibhaṅga — Sammohavinodanī + subcommentaries'
W24 = 'Pañcapakaraṇa — Pañcappakaraṇaṭṭhakathā + subcommentaries'

LEAF = [r're:.']

# --- 22AbhiT01: the Dhammasaṅgaṇī's four kaṇḍas, twice --------------------
KANDA = ['Vīsatigāthāvaṇṇanā', 'Nidānakathāvaṇṇanā',
         '1. Cittuppādakaṇḍa', '2. Rūpakaṇḍa',
         '3. Nikkhepakaṇḍa', '4. Aṭṭhakathākaṇḍa']

# --- 23AbhiT02: the eighteen vibhaṅgas, twice -----------------------------
VIBH = ['1. Khandhavibhaṅga', '2. Āyatanavibhaṅga', '3. Dhātuvibhaṅga',
        '4. Saccavibhaṅga', '5. Indriyavibhaṅga', '6. Paṭiccasamuppādavibhaṅga',
        '7. Satipaṭṭhānavibhaṅga', '8. Sammappadhānavibhaṅga',
        '9. Iddhipādavibhaṅga', '10. Bojjhaṅgavibhaṅga', '11. Maggaṅgavibhaṅga',
        '12. Jhānavibhaṅga', '13. Appamaññāvibhaṅga', '14. Sikkhāpadavibhaṅga',
        '15. Paṭisambhidāvibhaṅga', '16. Ñāṇavibhaṅga',
        '17. Khuddakavatthuvibhaṅga', '18. Dhammahadayavibhaṅga']
VLEV = [None, [r're:\d+\.\s+(?:Suttanta|Abhidhamma)bhājanīya(?:vaṇṇanā)?$',
               r're:\d+\.\s+Pañhapucchaka(?:vaṇṇanā)?$',
               r're:\d+\.\s+\S*niddesa(?:vaṇṇanā)?$',
               r're:\d+\.\s+\S*vāra(?:vaṇṇanā)?$',
               r're:^Uddesavaṇṇanā$'], LEAF]

# --- 24AbhiT03: the five pakaraṇas, twice ---------------------------------
DHATU = ['Ganthārambhavaṇṇanā', '1. Mātikāvaṇṇanā', '2. Niddesavaṇṇanā']
PUGG = ['1. Mātikāvaṇṇanā', '2. Niddesavaṇṇanā']
KVAGGA = ['Mahāvagga'] + ['%d. %svagga' % (i, n) for i, n in [
    (2, 'Dutiya'), (3, 'Tatiya'), (4, 'Catuttha'), (5, 'Pañcama'), (6, 'Chaṭṭha'),
    (7, 'Sattama'), (8, 'Aṭṭhama'), (9, 'Navama'), (10, 'Dasama'),
    (11, 'Ekādasama'), (12, 'Dvādasama'), (13, 'Terasama'), (14, 'Cuddasama'),
    (15, 'Pannarasama'), (16, 'Soḷasama'), (17, 'Sattarasama'),
    (18, 'Aṭṭhārasama'), (19, 'Ekūnavīsatima'), (20, 'Vīsatima'),
    (21, 'Ekavīsatima'), (22, 'Bāvīsatima'), (23, 'Tevīsatima')]]
# !!! A REGEX TOP THAT MATCHES TWICE BREAKS THE ORDER CHECK, and this volume
# offers three chances to do it: `Paccayaniddesa` opens both the first paccaya
# and the pakiṇṇaka-vinicchaya, `Pucchāvāra` heads two of its three vāras, and
# the Mūlayamaka has NO bare name head — its uddesa- and niddesa-vāra lines
# both carry it.  So every top here is a LITERAL, taken from the page.
# AND THE TWO HALVES DO NOT SET THEM THE SAME WAY: the anuṭīkā heads its first
# paccaya `Paccayaniddesa` / `1. Hetupaccayaniddesavaṇṇanā` on two lines where
# the mūlaṭīkā runs them together, and it prints NO `Mahāvagga` over the
# Kathāvatthu's first vagga.  Hence the paired lists.
YAMAKA = ['Ganthārambhavaṇṇanā', '1. Mūlayamaka uddesavāravaṇṇanā',
          '2. Khandhayamaka', '3. Āyatanayamaka', '4. Dhātuyamakavaṇṇanā',
          '5. Saccayamaka', '6. Saṅkhārayamaka', '7. Anusayayamaka',
          '8. Cittayamaka', '9. Dhammayamaka', '10. Indriyayamaka']
_PATT_TAIL = ['Pucchāvāra 2. Paccayapaccanīyavaṇṇanā',
              '1. Kusalattika 1. Paṭiccavāravaṇṇanā',
              '2. Vedanāttikavaṇṇanā', '3. Vipākattikavaṇṇanā',
              '4. Upādinnattikavaṇṇanā', '6. Vitakkattikavaṇṇanā']
PATT_MULA = (['Ganthārambhavaṇṇanā', 'Paccayuddesavaṇṇanā',
              'Paccayaniddesa 1. Hetupaccayaniddesavaṇṇanā'] + _PATT_TAIL)
PATT_ANU = (['Ganthārambhavaṇṇanā', 'Paccayuddesavaṇṇanā',
             'Paccayaniddesa'] + _PATT_TAIL)

ABHI_T = {
 # !!! SIX MĀTIKĀ-VS-BODY DIVERGENCES, each read on both printed pages with
 # `_tika/matdiff.py`.  Four are the edition disagreeing with itself about a
 # SPACE or a CAPITAL inside a compound; one is a real misprint, and one is a
 # mātikā entry the body prints as half of a longer line.
 #   mātikā p16 `Kiriyābhākata`   body p158 `Kiriyābyākata` — and the mātikā's
 #     OWN p16 lists `Kiriyābyākatakathāvaṇṇanā`, as do the body's p143 heading
 #     and its closing colophon.  Three witnesses to one.  MĀTIKĀ SLIPPED.
 #   mātikā `Akusalapadadhammuddesavāra`   body `Akusalapada dhammuddesavāra`
 #   mātikā `Upādābhājanīyakathāvaṇṇanā`   body `Upādābhājanīyakathā vaṇṇanā`
 #   mātikā `Kāmāvacarakusalaniddesa…`     body `Kāmāvacarakusala niddesa…`
 #   mātikā `Catukkanaya-Paṭhamajjhāna…`   body `…-paṭhamajjhāna…` — a capital.
 #     No third witness for these four; RECORDED as they stand.
 # AND THE MĀTIKĀ SPLITS ONE BODY HEADING IN TWO: it lists `Abyākatapada` and
 # `Ahetukakusalavipākavaṇṇanā` on separate lines where the body prints the one
 # line `Abyākatapada ahetukakusalavipākavaṇṇanā` (p145, and again in the
 # anuṭīkā).  The first half is dropped from the MĀTIKĀ SIDE — which says "do
 # not check this one", not "it is not printed" — and the body's whole line is
 # given the second half's form.
 '22AbhiT01': {
   'matika_drop': ('Abyākatapada',),
   'body_errata': {
     'Abyākatapada ahetukakusalavipākavaṇṇanā': 'Ahetukakusalavipākavaṇṇanā',
     'Akusalapada dhammuddesavāra':             'Akusalapadadhammuddesavāra',
     'Kiriyābyākata':                           'Kiriyābhākata',
     'Upādābhājanīyakathā vaṇṇanā':             'Upādābhājanīyakathāvaṇṇanā',
     'Kāmāvacarakusala niddesavārakathāvaṇṇanā':
         'Kāmāvacarakusalaniddesavārakathāvaṇṇanā',
     'Catukkanaya-paṭhamajjhānakathāvaṇṇanā':
         'Catukkanaya-Paṭhamajjhānakathāvaṇṇanā'},
   'title': 'Dhammasaṅgaṇīṭīkā',
   'work': W22,
   'first': 2,
   'matika': (13, 20),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'books': [
     {'title': 'Dhammasaṅgaṇīmūlaṭīkā', 'lo': 0, 'hi': 261,
      'tops': KANDA, 'levels': [None, LEAF]},
     {'title': 'Dhammasaṅgaṇī-anuṭīkā', 'lo': 261, 'hi': 477,
      'tops': KANDA, 'levels': [None, LEAF]},
   ],
 },
 # !!! TWO MĀTIKĀ-VS-BODY DIVERGENCES, and a third witness settles both.
 #   mātikā p12 `Vedenānupassanādi-uddesavaṇṇanā`  body p164 `Vedanā-` — it is
 #     *vedanā*, the feeling, and the whole satipaṭṭhāna literature agrees.
 #     MĀTIKĀ SLIPPED.
 #   body p498 `6. Chakkanidesavaṇṇanā` — a LOST `d`.  The mātikā lists
 #     `Chakkaniddesavaṇṇanā` four times and the body itself prints it
 #     correctly at ord176, ord249 and ord438, with a matching colophon.
 #     Four witnesses to one.  BODY SLIPPED.
 # AND ONE LINE OF QUOTED PROSE WAS READ AS A HEADING: p309's block quotation
 # is set at a display indent throughout, so `Samuditantim pākaṭoyamattho.
 # Evañca katvā yadeke vadanti` — mid-sentence, no terminal stop — satisfied
 # the form test.  10DiT03 p264's class.  `headskip`.
 '23AbhiT02': {
   'head_skip': ('Samuditantim pākaṭoyamattho. Evañca katvā yadeke vadanti',),
   'body_errata': {
     'Vedanānupassanādi-uddesavaṇṇanā': 'Vedenānupassanādi-uddesavaṇṇanā',
     '6. Chakkanidesavaṇṇanā':          '6. Chakkaniddesavaṇṇanā'},
   'title': 'Vibhaṅgaṭīkā',
   'work': W23,
   'first': 2,
   'matika': (3, 14),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'books': [
     {'title': 'Vibhaṅgamūlaṭīkā', 'lo': 0, 'hi': 277,
      'tops': VIBH, 'levels': VLEV},
     {'title': 'Vibhaṅga-anuṭīkā', 'lo': 277, 'hi': 519,
      'tops': VIBH, 'levels': VLEV},
   ],
 },
 # !!! ELEVEN MĀTIKĀ-VS-BODY DIVERGENCES, and the canon settles three.
 #   mātikā p4  `Gandhārambhavaṇṇanā`   body `Ganthārambha-` — it is *gantha*,
 #     a composition, and every other volume in the corpus prints it so.
 #   mātikā p8  `1. Vādayuttaparihāni…`  body `Vādayutti-` — the canon 32Abhi04
 #     prints `Vādayutti` three times and `Vādayutta` never.  MĀTIKĀ.
 #   mātikā p8  `4. Jātikathāvaṇṇanā`    body `4. Jahatikathā-` — 32Abhi04
 #     prints `Jahatikathā`, and this volume's own body five times.  MĀTIKĀ.
 #   mātikā p9  `4. Vimuccamanakathā…`   body `Vimuccamāna-` — a lost length.
 #   mātikā p26 `1. Gihissa-arahātikathā…`  body `-arahati-`.
 #   plus `Yathākammūpagata-`/`-upagata-`, `Natthi-Vigata-Avigata-`/
 #   `Natthivigata-avigata-`, and two places where the mātikā closes a compound
 #   the body spaces (`Paṭhamanayasaṅgahā-`, `Aṭṭhamakassa indriyakathā-`).
 #   No third witness for those five; RECORDED as they stand.
 #
 # AND THE MĀTIKĀ SPLITS FOUR BODY HEADINGS IN TWO.  The body prints
 # `Mahāvāra 1. Anusayavāravaṇṇanā`, `Pucchāvāra 2. Paccayapaccanīyavaṇṇanā`,
 # `1. Mūlayamaka uddesavāravaṇṇanā` and `1. Paccayānuloma 1. Vibhaṅgavāra` as
 # ONE line each; the mātikā lists the two halves separately.  The first half
 # is dropped from the MĀTIKĀ SIDE — "do not check this one", not "it is not
 # printed" — and the body's whole line is given the second half's form.
 # (`Mahāvāra` is set with a single space in the mūlaṭīkā and four in the
 # anuṭīkā, so it needs both literals.)
 '24AbhiT03': {
   'matika_drop': ('Mahāvāra', 'Pucchāvāra', '1. Mūlayamaka',
                   '1. Paccayānulomavaṇṇanā'),
   'body_errata': {
     'Ganthārambhavaṇṇanā':                  'Gandhārambhavaṇṇanā',
     '1. Paṭhamanaya saṅgahāsaṅgahapadavaṇṇanā':
         '1. Paṭhamanayasaṅgahāsaṅgahapadavaṇṇanā',
     '1. Vādayuttiparihānikathāvaṇṇanā':     '1. Vādayuttaparihānikathāvaṇṇanā',
     '4. Jahatikathāvaṇṇanā':                '4. Jātikathāvaṇṇanā',
     '4. Vimuccamānakathāvaṇṇanā':           '4. Vimuccamanakathāvaṇṇanā',
     '9. Yathākammupagatañāṇakathāvaṇṇanā':
         '9. Yathākammūpagatañāṇakathāvaṇṇanā',
     '6. Aṭṭhamakassa indriya kathāvaṇṇanā':
         '6. Aṭṭhamakassa indriyakathāvaṇṇanā',
     '1. Gihissa-arahatikathāvaṇṇanā':       '1. Gihissa-arahātikathāvaṇṇanā',
     '22-24. Natthivigata-avigatapaccayaniddesavaṇṇanā':
         '22-24. Natthi-Vigata-Avigatapaccayaniddesavaṇṇanā',
     'Mahāvāra 1. Anusayavāravaṇṇanā':       '1. Anusayavāravaṇṇanā',
     'Mahāvāra    1. Anusayavāravaṇṇanā':    '1. Anusayavāravaṇṇanā',
     'Pucchāvāra 2. Paccayapaccanīyavaṇṇanā': '2. Paccayapaccanīyavaṇṇanā',
     'Pucchāvāra 3. Anulomapaccanīyavaṇṇanā': '3. Anulomapaccanīyavaṇṇanā',
     'Anulomapaccanīyavaṇṇanā':               '3. Anulomapaccanīyavaṇṇanā'},
   'title': 'Pañcapakaraṇaṭīkā',
   'work': W24,
   'first': 2,
   'matika': (3, 35),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'books': [
     {'title': 'Dhātukathāpakaraṇamūlaṭīkā', 'lo': 0, 'hi': 39,
      'tops': DHATU, 'levels': [None, LEAF]},
     {'title': 'Puggalapaññattipakaraṇamūlaṭīkā', 'lo': 39, 'hi': 111,
      'tops': PUGG, 'levels': [None, LEAF]},
     {'title': 'Kathāvatthupakaraṇamūlaṭīkā', 'lo': 111, 'hi': 343,
      'tops': ['Ganthārambhakathāvaṇṇanā', 'Nidānakathāvaṇṇanā'] + KVAGGA,
      'levels': [None, LEAF]},
     {'title': 'Yamakapakaraṇamūlaṭīkā', 'lo': 343, 'hi': 394,
      'tops': YAMAKA, 'levels': [None, LEAF]},
     {'title': 'Paṭṭhānapakaraṇamūlaṭīkā', 'lo': 394, 'hi': 534,
      'tops': PATT_MULA, 'levels': [None, LEAF]},
     {'title': 'Dhātukathāpakaraṇa-anuṭīkā', 'lo': 534, 'hi': 572,
      'tops': DHATU, 'levels': [None, LEAF]},
     {'title': 'Puggalapaññattipakaraṇa-anuṭīkā', 'lo': 572, 'hi': 630,
      'tops': PUGG, 'levels': [None, LEAF]},
     {'title': 'Kathāvatthupakaraṇa-anuṭīkā', 'lo': 630, 'hi': 846,
      'tops': ['Ganthārambhavaṇṇanā', 'Nidānakathāvaṇṇanā'] + KVAGGA[1:],
      'levels': [None, LEAF]},
     {'title': 'Yamakapakaraṇa-anuṭīkā', 'lo': 846, 'hi': 897,
      'tops': YAMAKA, 'levels': [None, LEAF]},
     {'title': 'Paṭṭhānapakaraṇa-anuṭīkā', 'lo': 897, 'hi': 1022,
      'tops': PATT_ANU, 'levels': [None, LEAF]},
   ],
 },
}

A.SPEC.update(ABHI_T)
A.main()
