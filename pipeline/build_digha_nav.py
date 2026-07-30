#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a Dīghanikāya volume's nav tree with the generic nav machinery.

    python3 pipeline/build_digha_nav.py <VOL> [--write]

Same shape as `build_vinaya_nav.py`: the builder in `build_abhidhamma_nav.py`
is generic over the piṭaka — `tops`, `levels`, `matika_gate`,
`matika_centred_gate` and the two printed checks say nothing about the
Abhidhamma — so this file is the SPEC and nothing else.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_abhidhamma_nav as A

DIGHA = {

 # --- 07Di02: ONE BOOK, THE TEN SUTTAS OF THE MAHĀVAGGA --------------------
 #
 # Flatter than any Vinaya volume: the ten suttas are the top level and their
 # sections are LEAVES, so `levels` is `[None]` and there is nothing to memo.
 # The sections are UNNUMBERED (`Pubbenivāsapaṭisaṁyuttakathā`,
 # `Devatāsannipāta`) except the Pāyāsisutta's fourteen similes, which the
 # edition numbers in PARENTHESES — "(2) Cora-upamā" — and which the BODY
 # builder needs `head_paren` to see at all.
 #
 # The mātikā is 0-based pages 3-8 and MEASURED from the pages carrying the
 # `Piṭṭhaṅka` column, not taken from a note (2026-07-26aj's lesson).  Unlike
 # every Vinaya mātikā this one is NOT finer than the body: 155 of its 157
 # entries are printed as body headings, so `matika_gate` can stand here.
 # The two that do not resolve are named below.
 '07Di02': {
   'title': 'Mahāvaggapāḷi',
   'work': 'Suttantapiṭaka',          # kept from the volume's existing node
   'first': 0,
   'matika': (3, 8),
   'matika_gate': True,
   'matika_centred_gate': True,
   'tops': ['1. Mahāpadānasutta', '2. Mahānidānasutta',
            '3. Mahāparinibbānasutta', '4. Mahāsudassanasutta',
            '5. Janavasabhasutta', '6. Mahāgovindasutta',
            '7. Mahāsamayasutta', '8. Sakkapañhasutta',
            '9. Mahāsatipaṭṭhānasutta', '10. Pāyāsisutta'],
   'levels': [None],
   # AN ERRATUM OF THE EDITION, RECORDED NOT CORRECTED.  The mātikā (0-based
   # p7) lists `Indriyasaṁvara`; the body head (0-based p232) prints
   # `Indrīyasaṁvara`, with a long ī.  Printed ONCE on each side, which is
   # exactly the case `errata` is for — it maps the MĀTIKĀ's form onto the
   # BODY's, globally, and that is safe only when neither side repeats.
   'errata': {'Indriyasaṁvara': 'Indrīyasaṁvara'},
   # THE ONE ENTRY OF 157 THAT CANNOT RESOLVE, AND IT IS NOT A DEFECT OF THE
   # TREE.  The mātikā's last entry is `Uddānagāthā` (p283); the body heads
   # that section `Tassuddānaṁ` (0-based p291) and `kat_is_colo` classifies it
   # as a COLOPHON, so it never enters the heads stream and no nav row can
   # exist for it.  That is the SAME open finding as 05Vin05's 53
   # `Tassuddānaṁ.` labels rendering as colophon lines rather than labels —
   # recorded there, recorded here, and NOT worked around by widening the gate.
   # Dropped from the entry check so `matika_gate` can stay TRUE and go on
   # verifying the other 156.
   'matika_drop': ('Uddānagāthā',),
   # NOT AN ERRATUM — the mātikā simply omits a number the BODY prints.  The
   # Pāyāsisutta heads its fourteen similes "(1) Candimasūriya-upamā" while the
   # mātikā lists "Candimasūriya-upamā" bare, and `fold` KEEPS DIGITS (it strips
   # only non-alphanumerics), so "2coraupamā" and "coraupamā" do not match and
   # the gate REFUSED on all fourteen.  `body_errata` supplies the alternative
   # fold, which is what it does mechanically whatever its name.
   # Named per volume rather than by teaching `fold` to strip a leading "(N)":
   # that is shared machinery feeding every volume, and 32Abhi04 heads sections
   # "(175) 10. Navattabbaṁ…" where the parenthesised number is the kathā's
   # number in the whole book and IS part of the label.  Zero blast radius here.
   # THE EDITION ALSO DROPS THE HYPHEN on three of them — body "(5) Jaccandha
   # upamā", "(13) Akkhadhuttaka upamā", "(14) Sāṇabhārika upamā" against the
   # mātikā's hyphenated forms — which `fold` absorbs, so it needs no
   # instrument; recorded here because it is the edition's, not ours.
   'body_errata': {
     '(1) Candimasūriya-upamā':
         'Candimasūriya-upamā',
     '(2) Cora-upamā':
         'Cora-upamā',
     '(3) Gūthakūpapurisa-upamā':
         'Gūthakūpapurisa-upamā',
     '(4) Tāvatiṁsadeva-upamā':
         'Tāvatiṁsadeva-upamā',
     '(5) Jaccandha upamā':
         'Jaccandha upamā',
     '(6) Gabbhinī-upamā':
         'Gabbhinī-upamā',
     '(7) Supinaka-upamā':
         'Supinaka-upamā',
     '(8) Santatta-ayoguḷa-upamā':
         'Santatta-ayoguḷa-upamā',
     '(9) Saṅkhadhama-upamā':
         'Saṅkhadhama-upamā',
     '(10) Aggikajaṭila-upamā':
         'Aggikajaṭila-upamā',
     '(11) Dvesatthavāha-upamā':
         'Dvesatthavāha-upamā',
     '(12) Gūthabhārika-upamā':
         'Gūthabhārika-upamā',
     '(13) Akkhadhuttaka upamā':
         'Akkhadhuttaka upamā',
     '(14) Sāṇabhārika upamā':
         'Sāṇabhārika upamā',
   },
 },

 # --- 06Di01: ONE BOOK, THE THIRTEEN SUTTAS OF THE SĪLAKKHANDHAVAGGA -------
 #
 # !!! THE MĀTIKĀ IS 0-BASED 12-17, AND A `Piṭṭhaṅka` SEARCH DOES NOT GIVE IT.
 # This volume's BACK MATTER — the word index and the `Nānāpāṭhā` variant
 # appendix, 0-based 254-264 — heads its columns `Piṭṭhaṅko` too, so the naive
 # search returns SIXTEEN pages.  Measure it, then LOOK at it.
 '06Di01': {
   'title': 'Sīlakkhandhavaggapāḷi',
   'work': 'Suttantapiṭaka',          # kept from the volume's existing node
   'first': 0,
   'matika': (12, 17),
   'matika_gate': True,
   'matika_centred_gate': True,
   'tops': ['1. Brahmajālasutta', '2. Sāmaññaphalasutta', '3. Ambaṭṭhasutta',
            '4. Soṇadaṇḍasutta', '5. Kūṭadantasutta', '6. Mahālisutta',
            '7. Jāliyasutta', '8. Mahāsīhanādasutta', '9. Poṭṭhapādasutta',
            '10. Subhasutta', '11. Kevaṭṭasutta', '12. Lohiccasutta',
            '13. Tevijjasutta'],
   'levels': [None],
   # EIGHT ERRATA OF THE EDITION, RECORDED NOT CORRECTED.  Each is printed
   # ONCE in the mātikā and ONCE in the body — the condition `errata` requires,
   # and CHECKED, not assumed (counted over both page ranges).  The mātikā form
   # is the key, the body's the value; the tree keeps what the BODY prints.
   'errata': {
     'Antānantavada': 'Antānantavāda',
     'Paritassitavipphanditavāda': 'Paritassitavipphanditavāra',
     'Phassapaccayāvāda': 'Phassapaccayāvāra',
     'Paṇītatalasāmaññaphala': 'Paṇītatarasāmaññaphala',
     'Dvelakkhaṇādassaṇa': 'Dvelakkhaṇādassana',
     'Sīlasamādipaññāsampadā': 'Sīlasamādhipaññāsampadā',
     'Titthiyaparivāsakathā': 'Tatthiyaparivāsakathā',
     'Silakkhandha': 'Sīlakkhandha',
   },
   # NOT ERRATA — the mātikā omits a number the BODY prints, here TRAILING
   # rather than leading: the Sāmaññaphalasutta numbers its eight ñāṇas
   # "Vipassanāñāṇa (1)" … "Āsavakkhayañāṇa (8)" and the mātikā lists them
   # bare.  `fold` KEEPS DIGITS, so they do not fold equal.  Same treatment as
   # 07Di02's leading "(N)", and named per volume for the same reason.
   'body_errata': {
     'Vipassanāñāṇa (1)':
         'Vipassanāñāṇa',
     'Manomayiddhiñāṇa (2)':
         'Manomayiddhiñāṇa',
     'Iddhividhañāṇa (3)':
         'Iddhividhañāṇa',
     'Dibbasotañāṇa (4)':
         'Dibbasotañāṇa',
     'Cetopariyañāṇa (5)':
         'Cetopariyañāṇa',
     'Pubbenivāsānussatiñāṇa (6)':
         'Pubbenivāsānussatiñāṇa',
     'Dibbacakkhuñāṇa (7)':
         'Dibbacakkhuñāṇa',
     'Āsavakkhayañāṇa (8)':
         'Āsavakkhayañāṇa',
   },
   # The same open finding as 07Di02 and 05Vin05: the mātikā's last entry is
   # `Uddānagāthā`, the body heads that section `Tassuddānaṁ` (0-based p253)
   # and `kat_is_colo` classifies it as a COLOPHON, so no nav row can exist for
   # it.  Dropped from the entry check so `matika_gate` keeps verifying the
   # other 144.
   'matika_drop': ('Uddānagāthā',),
 },

 # --- 08Di03: ONE BOOK, THE ELEVEN SUTTAS OF THE PĀTHIKAVAGGA -------------
 '08Di03': {
   'title': 'Pāthikavaggapāḷi',
   'work': 'Suttantapiṭaka',
   'first': 0,
   'matika': (3, 8),
   'matika_gate': True,
   'matika_centred_gate': True,
   'tops': ['1. Pāthikasutta', '2. Udumbarikasutta', '3. Cakkavattisutta',
            '4. Aggaññasutta', '5. Sampasādanīyasutta', '6. Pāsādikasutta',
            '7. Lakkhaṇasutta', '8. Siṅgālasutta', '9. Āṭānāṭiyasutta',
            '10. Saṅgītisutta', '11. Dasuttarasutta'],
   'levels': [None],
   # FIVE ERRATA OF THE EDITION, each printed ONCE in the mātikā and ONCE in
   # the body — counted over both page ranges, not assumed.
   'errata': {
     'Cutūpapātañaṇadesanā': 'Cutūpapātañāṇadesanā',
     'Āyatanapaṇhitāditilakkhaṇaṁ (3-5)': 'Āyatapaṇhitāditilakkhaṇaṁ (3-5)',
     'Parimaṇḍala-anonamajaṇṇuparimasanalakkhaṇāni (15-16)':
         'Parimaṇḍasa-anonamajaṇṇuparimasanalakkhaṇāni (15-16)',
     'Samasanta-susukkadāṭhālakkhaṇāni (31-32)':
         'Samadanta-susukkadāṭhālakkhaṇāni (31-32)',
     'Catuṭhāṇaṁ': 'Catuṭhānaṁ',
   },
   # THE SIXTH DIVERGENCE TAKES `body_errata`, NOT `errata`, AND THE RULE IS
   # THE ONE 35Abhi07 EARNED: `errata` rewrites a mātikā entry GLOBALLY and is
   # right only when the misprint occurs ONCE ON EACH SIDE.  The mātikā prints
   # `Novadhammā` once, but the body prints `Nava dhammā` TWICE (counted), so
   # the alternative goes on the TREE side instead.
   'body_errata': {'Nava dhammā': 'Novadhammā'},
   # As in 06Di01 and 07Di02: the body heads this section `Tassuddānaṁ`, which
   # `kat_is_colo` classifies as a colophon, so no nav row can exist for it.
   'matika_drop': ('Uddānagāthā',),
 },

}

A.SPEC.update(DIGHA)
A.main()
