#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a Vinaya volume's nav tree with the generic nav machinery.

    python3 pipeline/build_vinaya_nav.py <VOL> [--write]

The builder in `build_abhidhamma_nav.py` is generic over the pitaka — `tops`,
`levels`, `matika_gate`, `level_memo` and the two printed checks (the front
matika and the body's own colophons) say nothing about the Abhidhamma.  What is
per-pitaka is only the SPEC, so this file is the SPEC and nothing else.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_abhidhamma_nav as A

# THE THREE FORMS THE EDITION USES FOR A NUMBERED SECTION, measured over the
# five volumes' heads streams.  A sikkhāpada may carry a RANGE of numbers —
# 02Vin02 p… sets '8-9-10. Aṭṭhama navama dasamasikkhāpada' for three rules
# whose text is one — so the number is `\d+(?:-\d+)*`.
# AND ITS NAME MAY BE SEVERAL WORDS: '8-9-10. Aṭṭhama navama dasamasikkhāpada'
# (02Vin02) and '1. Sattanagaresu paññattasikkhāpada' (05Vin05).  Measured over
# all five heads streams, widening `\S*` to `.*` adds exactly THREE headings in
# the whole piṭaka and no other: those two sikkhāpadas and one vagga,
# 05Vin05's '4. Apaññatte paññattavagga'.  It adds nothing for a pārājika.
# Left tight
# a multi-word sikkhāpada falls through the level table and nests under its own
# elder sibling — which is what the tree showed for the 8-9-10 rule.
PARAJIKA = r're:\d+(?:-\d+)*\.\s+\S*pārājika$'
VAGGA    = r're:\d+(?:-\d+)*\.\s+.*vagga$'
NUMBERED = r're:\d+(?:-\d+)*\.\s+\S'
SIKKHA   = r're:\d+(?:-\d+)*\.\s+.*sikkhāpada$'

VINAYA = {




 # --- 05Vin05: NINETEEN CHAPTERS, THE FIRST TWO FOUR LEVELS DEEP ------------
 #
 # !!! THIS VOLUME'S NAV IS **NOT WRITTEN** (2026-07-26aj).  The SPEC below is
 # correct as far as it goes — 19 tops, all 21 of the mātikā's centred group
 # heads resolve — but FOUR of the volume's printed 'headings' are FOOTNOTE
 # CELLS, and in the tree they take real sections as children:
 #   '1. Uppādentassa(Syā)' and '2. Upassuti (?)  3. Khiyyadhammaṁ (Ka)'
 #   (0-based p51), '1. Samatitthikaṁ (Ka)' (p67), '1. Rathiyāya vā (Ka)'
 #   (p121)
 # The cause is in build_khu_volume.py, not here: `page_lines` cuts the page at
 # `FNRULE` (`_{20,}`), and on EIGHT pages of this volume the edition's
 # footnote rule is a GRAPHIC that pdftotext emits no text line for (0-based
 # 51, 54, 67, 110, 119, 121, 140, 382), so the cells enter the printed stream.
 # MEASURED: 05Vin05 is the only volume where this happens — the other four
 # Vinaya volumes have 0 such pages (79/120/134/140 rule-bearing pages each),
 # and no other volume in SPEC has a head-classified line ending in a variant
 # siglum.  Fixing it belongs with the BODY and needs its three gates; a
 # `head_skip` here would only hide it, since the reader still draws those four
 # lines as centred headings.  Build it, read the tree, and leave it unwritten
 # until the body fix lands — the same choice this volume's side-maps got in
 # 2026-07-26ah.
 # The Parivāra's tops are UNNUMBERED and are exactly the mātikā's own centred
 # group heads.  Its first two chapters run vāra > kaṇḍa > vagga under the top;
 # the other seventeen run one numbered level and stop, which is what
 # `level_memo` is for.  A numbered head is a VĀRA-level section unless it names
 # a kaṇḍa or a vagga, so level 1 excludes those two endings explicitly rather
 # than listing the ~120 forms the chapter titles take.
 '05Vin05': {
   'title': 'Parivārapāḷi',
   'work': 'Vinaya — Samantapāsādikā + subcommentaries',
   'first': 0,
   'matika': (3, 13),
   'matika_gate': False,
   'centred_indent': 14,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': ['Bhikkhuvibhaṅga', 'Bhikkhunīvibhaṅga', 'Samuṭṭhānasīsasaṅkhepa',
            'Antarapeyyāla', 'Samathabheda', 'Ekuttarikanaya',
            'Uposathādipucchāvissajjanā', 'Gāthāsaṅgaṇika', 'Adhikaraṇabheda',
            'Aparagāthāsaṅgaṇika', 'Codanākaṇḍa', 'Cūḷasaṅgāma',
            'Mahāsaṅgāma', 'Kathinabheda', 'Upālipañcaka',
            'Atthāpattisamuṭṭhāna', 'Dutiyagāthāsaṅgaṇika',
            'Sedamocanagāthā', 'Pañcavagga'],
   'levels': [None,
              [r're:\d+(?:-\d+)*\.\s+(?!.*(?:kaṇḍa|kaṇḍādi|vagga)$).'],
              [r're:\d+(?:-\d+)*\.\s+\S*(?:kaṇḍa|kaṇḍādi)$'],
              [VAGGA]],
   # THE MĀTIKĀ AND THE BODY SPELL TWO CHAPTER TITLES DIFFERENTLY, once each.
   # p11 sets 'Uposathādipucchāvisajjanā' with a single s where the body head
   # (ord348) doubles it, and 'Dutiyagāthāsaṅgaṇi' where the body has
   # 'Dutiyagāthāsaṅgaṇika'.  Both pages keep what they print.
   'errata': {'Uposathādipucchāvisajjanā': 'Uposathādipucchāvissajjanā',
              'Dutiyagāthāsaṅgaṇi': 'Dutiyagāthāsaṅgaṇika'},
 },
 # --- 04Vin04: TWELVE KHANDHAKAS, NUMBERED SECTIONS, UNNUMBERED SUB-BLOCKS --
 # Each khandhaka restarts its section numbering at 1, so the numbers say
 # nothing across khandhakas and the khandhaka heads are again the top level.
 # The sub-blocks (Adhammakammadvādasaka, Ākaṅkhamānachakka, …) are printed
 # WITHOUT a number and are leaves under the section they analyse.
 '04Vin04': {
   'title': 'Cūḷavaggapāḷi',
   'work': 'Vinaya — Samantapāsādikā + subcommentaries',
   'first': 0,
   'matika': (3, 10),
   'matika_gate': False,
   'centred_indent': 14,
   'matika_centred_gate': True,
   'tops': ['1. Kammakkhandhaka', '2. Pārivāsikakkhandhaka',
            '3. Samuccayakkhandhaka', '4. Samathakkhandhaka',
            '5. Khuddakavatthukkhandhaka', '6. Senāsanakkhandhaka',
            '7. Saṁghabhedakakkhandhaka', '8. Vattakkhandhaka',
            '9. Pātimokkhaṭṭhapanakkhandhaka', '10. Bhikkhunikkhandhaka',
            '11. Pañcasatikakkhandhaka', '12. Sattasatikakkhandhaka'],
   # !!! ONE SUB-BLOCK IS PRINTED WITH A NUMBER AND ITS TWO PARALLELS ARE NOT.
   # 0-based p64 sets '1. Nappaṭippassambhetabbatecattālīsaka'; p75 and p86 set
   # the same heading bare, and the volume's own mātikā (p4) lists all three
   # without a number.  Claimed by the numbered pattern it would stand as a
   # SIBLING of sections 5, 6 and 7 — the tree reading 5, 1, 6, 7 — where its
   # two parallels are leaves inside their section.  The numeral is the
   # edition's, printed once, and is KEPT in the label; only the level table is
   # told not to read it as a section number.
   'levels': [None,
              [r're:(?!1\. Nappaṭippassambhetabbatecattālīsaka$)'
               r'\d+(?:-\d+)*\.\s+\S']],
   # THE SECTION'S OWN NAME, IN THE LOCATIVE, REPRINTED OVER EACH OF ITS
   # SUB-BLOCKS — the left half of a printed pair-line, exactly as 01Vin01
   # reprints '1. Cīvaravagga' over each of its ten sikkhāpadas.  It does not
   # fold equal to the section it names ('5. Āpattiyā adassane
   # ukkhepanīyakamma' vs '…kamme'), so `subtree`'s ancestor test cannot see it.
   # !!! THE FOURTH IS THE EDITION'S OWN MISPRINT — p71 sets 'diṭṭhāyā' where
   # its four siblings set 'diṭṭhiyā'.  Named as printed, not corrected.
   'head_skip': ['Āpattiyā adassane ukkhepanīyakamme',
                 'Āpattiyā appaṭikamme ukkhepanīyakamme',
                 'Pāpikāya diṭṭhiyā appaṭinissagge ukkhepanīyakamme',
                 'Pāpikāya diṭṭhāyā appaṭinissagge ukkhepanīyakamme'],
 },
 # --- 03Vin03: TEN KHANDHAKAS, ONE RUNNING SECTION NUMBER ------------------
 # The Mahāvagga numbers its sections 1-280 STRAIGHT THROUGH the ten
 # khandhakas, so the number alone says nothing about depth and the khandhaka
 # heads are the whole of the top level.  No `level_memo`: there is one
 # declared level, so there is nothing for the memo to remember.
 '03Vin03': {
   'title': 'Mahāvaggapāḷi',
   'work': 'Vinaya — Samantapāsādikā + subcommentaries',
   'first': 0,
   'matika': (3, 13),
   'matika_gate': False,
   'centred_indent': 14,
   'matika_centred_gate': True,
   'tops': ['1. Mahākhandhaka', '2. Uposathakkhandhaka',
            '3. Vassūpanāyikakkhandhaka', '4. Pavāraṇākkhandhaka',
            '5. Cammakkhandhaka', '6. Bhesajjakkhandhaka',
            '7. Kathinakkhandhaka', '8. Cīvarakkhandhaka',
            '9. Campeyyakkhandhaka', '10. Kosambakakkhandhaka'],
   'levels': [None, [NUMBERED]],
   # !!! THE BODY MISPRINTS A SECTION NUMBER, AND THE EDITION IS NOT CORRECTED.
   # The running numbering goes 68, then 96, then 70.  The volume's own mātikā
   # (0-based p5) lists '69. Pātimokkhuddesānujānanā ... 140'; the body head on
   # 0-based p153 sets '96. Pātimokkhuddesānujānanā' — the digits transposed,
   # printed once.  The tree keeps what the BODY prints, and `body_errata` puts
   # the mātikā's form alongside it so the two are known to be one section.
   # RECORD IT AS AN ERRATUM of the edition; do not renumber the tree.
   'body_errata': {'96. Pātimokkhuddesānujānanā':
                   '69. Pātimokkhuddesānujānanā'},
 },
 # --- 02Vin02: TWO VIBHAṄGAS, AND THE EDITION NAMES ONLY ONE OF THEM --------
 # The volume runs the Bhikkhuvibhaṅga's last four kaṇḍas straight on from
 # 01Vin01 and then sets a title page, "Bhikkhunīvibhaṅga", at ord661.  ITS OWN
 # MĀTIKĀ DOES EXACTLY THAT TOO: it opens on '5. Pācittiyakaṇḍa' with no group
 # head above it and prints one group head, 'Bhikkhunīvibhaṅga', before the
 # bhikkhunī kaṇḍas.  So the top level is asymmetric — four kaṇḍas, then one
 # named division holding seven — and `nowrap` is what says the first book gets
 # no node.  The alternative would need a name the edition never prints here:
 # 'Pācittiyapāḷi' is the WHOLE volume and heads the bhikkhunī pages as well.
 '02Vin02': {
   'title': 'Pācittiyapāḷi',
   'work': 'Vinaya — Samantapāsādikā + subcommentaries',
   'first': 0,
   'matika': (3, 13),
   'matika_gate': False,
   'centred_indent': 14,
   'matika_centred_gate': True,
   # THE MĀTIKĀ'S FIRST PAGE MISPRINTS THE VOLUME'S OWN NAME — 0-based p3 heads
   # the table 'Pācittiyapāli', with a short a and a plain l, where every other
   # page of the volume sets 'Pācittiyapāḷi'.  It is the mātikā's own running
   # header, so it is furniture and not an entry; `matika_headers` cannot see it
   # because it opens ONE page.  The misprint is not corrected anywhere — it is
   # named here so the centred gate does not read it as a missing section.
   'matika_drop': ['Pācittiyapāli'],
   # AND ITS SIXTH VAGGA IS MISPRINTED IN THE MĀTIKĀ AND NOWHERE ELSE.  0-based
   # p5 heads the group '6. Surāpāṇavagga' with a retroflex ṇ and, three lines
   # below, lists '1. Surāpānasikkhāpada' with the dental n.  The BODY sets
   # '6. Surāpānavagga' over each of the vagga's ten sikkhāpadas (0-based
   # p157-p174, eleven printings) and closes it 'Surāpānavaggo chaṭṭho.' —
   # surā-pāna, drinking.  One printing on each side, so `errata` is the right
   # instrument; the edition is not corrected, the two forms are only declared
   # to be one section.
   'errata': {'6. Surāpāṇavagga': '6. Surāpānavagga'},
   'level_memo': True,
   'tops': [],
   # the body reprints the division's name over five of its seven kaṇḍas, in
   # the locative and with a short i
   'head_skip': ['Bhikkhunivibhaṅge'],
   'books': [
     {'title': None, 'nowrap': True, 'lo': 0, 'hi': 661,
      'tops': ['5. Pācittiyakaṇḍa', '6. Pāṭidesanīyakaṇḍa', '7. Sekhiyakaṇḍa',
               '8. Adhikaraṇasamatha'],
      'levels': [None, [VAGGA], [SIKKHA]]},
     {'title': 'Bhikkhunīvibhaṅga', 'lo': 661, 'hi': 10**9,
      'tops': ['1. Pārājikakaṇḍa', '2. Saṁghādisesakaṇḍa', '3. Nissaggiyakaṇḍa',
               '4. Pācittiyakaṇḍa', '5. Pāṭidesanīyakaṇḍa', '6. Sekhiyakaṇḍa',
               '7. Adhikaraṇasamatha'],
      'levels': [None, [VAGGA, PARAJIKA], [SIKKHA]]},
   ],
 },
 '01Vin01': {
   'title': 'Pārājikapāḷi',
   'work': 'Vinaya — Samantapāsādikā + subcommentaries',
   'first': 0,
   # 0-based pdftotext pages of the front mātikā.  !!! IT OPENS ON PAGE 13,
   # not 14: that page carries 'Verañjakaṇḍa', the whole Pārājikakaṇḍa head
   # and pārājikas 1-3, and dropping it loses eight of the 52 centred group
   # heads the gate below runs on.
   'matika': (13, 22),
   # ITS ENTRIES ARE FINER THAN THE BODY — a Paṭhamapaññatti, an Anupaññatti
   # and a 'Sikkhāpadavibhaṅga, padabhājanīya' under each sikkhāpada, none of
   # which the body heads — so the entry-level gate cannot be true here.  Its
   # CENTRED lines are a different witness and every one must resolve.
   'matika_gate': False,
   'centred_indent': 14,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': ['Verañjakaṇḍa', '1. Pārājikakaṇḍa', '2. Saṁghādisesakaṇḍa',
            '3. Aniyatakaṇḍa', '4. Nissaggiyakaṇḍa'],
   'levels': [None, [PARAJIKA, VAGGA], [SIKKHA]],
 },
}

A.SPEC.update(VINAYA)
A.main()
