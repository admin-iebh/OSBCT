#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the Vinaya-Aṭṭhakathā volumes (Samantapāsādikā and the two works
printed with it).  SPEC and nothing else; the machinery is
`build_abhidhamma_nav`.

!!! THE VOLUME'S LABEL COMES FROM THE COVER (0-based p0), NOT FROM THE INNER
TITLE PAGE.  01VinA01 and 02VinA02 both set `Pārājikakaṇḍa-aṭṭhakathā` on the
inner page that carries the homage — the page every canon volume's title was
read from — so taking it here would put two nav nodes with identical labels
inside the Vinaya, which `_navdup.js` forbids.  The cover distinguishes them the
way the edition itself does, by BHĀGA: `(Paṭhamo bhāgo)` and `(Dutiyo bhāgo)`.
The reading pane still draws the INNER page, through `booktitle/`, because that
is what that page prints.

    01VinA01   PĀRĀJIKAKAṆḌA-AṬṬHAKATHĀ (Paṭhamo bhāgo)
    02VinA02   PĀRĀJIKAKAṆḌA-AṬṬHAKATHĀ (Dutiyo bhāgo)
    03VinA03   PĀCITYĀDI-AṬṬHAKATHĀ            (Samantapāsādikā nāma)
    04VinA04   CŪḶAVAGGĀDI-AṬṬHAKATHĀ
    05Kankha   KAṄKHĀVITARAṆĪ-AṬṬHAKATHĀ
    06VinSg06  VINAYASAṄGAHAṬṬHAKATHĀ

01VinA01 and 05Kankha are ABSENT on purpose: their corpora are 69% and 19% of
the printed text (`claude/vinaya_atthakatha_corpus_gap.md`).  A nav over a
corpus with a 78-page hole would list sections that cannot be opened.
"""
import build_abhidhamma_nav as A

WORK = 'Vinaya — Samantapāsādikā + subcommentaries'

VINA = {
 # --- 06VinSg06: ONE BOOK, A FLAT MĀTIKĀ, 37 PRINTED HEADINGS ---------------
 # Sāriputta's Vinayasaṅgaha, not Buddhaghosa's.  Its mātikā (0-based 3-4) is
 # flat — 36 entries, no centred group heads — and the body prints exactly
 # those 36 plus `Pakiṇṇakakaṇḍamātikā`, the heading of the Pakiṇṇakakaṇḍa's
 # OWN mātikā, which the front mātikā does not list because it is not a kathā.
 # So the tree is flat too: no `levels` below the top.
 '06VinSg06': {
   'title': 'Vinayasaṅgahaṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 4),
   'matika_gate': True,
   'matika_centred_gate': False,
   # !!! THE EDITION MISPRINTS ITS OWN SECTION HEADING, ONCE.
   # p36 heads the section `8. Adhiṭthānavikappanavinicchayakathā` with a
   # single ṭ where the mātikā (p3) and the closing colophon both set
   # `Adhiṭṭhāna-` — two witnesses against one, and *adhiṭṭhāna* (adhi + √ṭhā)
   # is the word.  The BODY KEEPS WHAT IT PRINTS; this supplies the mātikā's
   # form to the gate so the two sides can be compared.  Erratum, not a
   # correction of the edition.
   'body_errata': {'8. Adhiṭthānavikappanavinicchayakathā':
                   '8. Adhiṭṭhānavikappanavinicchayakathā'},
   'tops': ['Ganthārambhakathā',
            '1. Divāseyyavinicchayakathā',
            '2. Parikkhāravinicchayakathā',
            '3. Bhesajjādikaraṇavinicchayakathā',
            '4. Viññattivinicchayakathā',
            '5. Kulasaṅgahavinicchayakathā',
            '6. Macchamaṁsavinicchayakathā',
            '7. Anāmāsavinicchayakathā',
            '8. Adhiṭthānavikappanavinicchayakathā',
            '9. Cīvaravippavāsavinicchayakathā',
            '10. Bhaṇḍapaṭisāmanavinicchayakathā',
            '11. Kayavikkayasamāpattivinicchayakathā',
            '12. Rūpiyādipaṭiggahaṇavinicchayakathā',
            '13. Dānalakkhaṇādivinicchayakathā',
            '14. Pathavīkhaṇanavinicchayakathā',
            '15. Bhūtagāmavinicchayakathā',
            '16. Sahaseyyavinicchayakathā',
            '17. Mañcapīṭhādisaṁghikasenāsanesu paṭipajjitabbavinicchayakathā',
            '18. Kālikavinicchayakathā',
            '19. Kappiyabhūmivinicchayakathā',
            '20. Paṭiggahaṇavinicchayakathā',
            '21. Pavāraṇāvinicchayakathā',
            '22. Pabbajjāvinicchayakathā',
            '23. Nissayavinicchayakathā',
            '24. Sīmāvinicchayakathā',
            '25. Uposathapavāraṇāvinicchayakathā',
            '26. Vassūpanāyikavinicchayakathā',
            '27. Upajjhāyādivattavinicchayakathā',
            '28. Catupaccayabhājanīyavinicchayakathā',
            '29. Kathinatthāravinicchayakathā',
            '30. Garubhaṇḍavinicchayakathā',
            '31. Codanādivinicchayakathā',
            '32. Garukāpattivuṭṭhānavinicchayakathā',
            '33. Kammākammavinicchayakathā',
            'Pakiṇṇakakaṇḍamātikā',
            '34. Pakiṇṇakavinicchayakathā',
            'Nigamanakathā'],
   'levels': [None],
 },
 # --- 02VinA02: THE SECOND BHĀGA, OPENING MID-WORK AT `3. Tatiyapārājika` ---
 # The mātikā (0-based 3-5) heads itself `Dutiyabhāga` and then sets the four
 # kaṇḍas as CENTRED group heads.  Two of them are not tops here: the volume
 # opens inside `1. Pārājikakaṇḍa`, so the body never prints that heading and
 # the two pārājikas it does print stand at the top of this bhāga instead.
 #
 # THE NISSAGGIYA HAS A VAGGA RUNG THE OTHER KAṆḌAS DO NOT — Cīvara, Kosiya
 # and Patta — so the depth is not uniform and `level_memo` carries it, the
 # same non-uniform case 33Abhi05 earned it for.
 '02VinA02': {
   'title': 'Pārājikakaṇḍa-aṭṭhakathā',
   # the COVER's form, with the bhāga: 01VinA01 sets the identical inner title
   'label': 'Pārājikakaṇḍa-aṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 5),
   'matika_gate': False,      # the mātikā compounds two of its entries (below)
   'matika_centred_gate': False,
   'level_memo': True,
   # !!! A SECOND MISPRINT IN A SECTION HEADING, again one witness against one:
   # p225 heads `4. Nissaggiyakaṇṭa` where the mātikā sets `4. Nissaggiyakaṇḍa`
   # — and the volume's other three kaṇḍas are all printed `-kaṇḍa`.  The body
   # keeps what it prints; this gives the gate the mātikā's form.
   'body_errata': {'4. Nissaggiyakaṇṭa': '4. Nissaggiyakaṇḍa'},
   'tops': ['3. Tatiyapārājika', '4. Catutthapārājika',
            '2. Saṁghādisesakaṇḍa', '3. Aniyatakaṇḍa', '4. Nissaggiyakaṇṭa'],
   'levels': [None, [r're:\d+\.\s+\S*vagga$'], [r're:.']],
 },
 # --- 04VinA04: TWO BOOKS, and the second repeats the canon Parivāra's shape --
 # Cover `CŪḶAVAGGĀDI-AṬṬHAKATHĀ`.  Book 1 is the twelve khandhakas, numbered
 # on the page (`1. Kammakkhandhaka` … `12. Sattasatikakkhandhaka`), each with
 # its kathās beneath.  Book 2 is the Parivāra's commentary and its tops are
 # the SAME nineteen unnumbered divisions 05Vin05 declares for the canon text.
 '04VinA04': {
   'title': 'Cūḷavaggādi-aṭṭhakathā',
   'label': 'Cūḷavaggādi-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 10),
   'matika_gate': False,
   'matika_centred_gate': False,
   'level_memo': True,
   'books': [
     {'title': 'Cūḷavaggādi-aṭṭhakathā', 'lo': 0, 'hi': 186,
      'tops': [r're:\d+\.\s+.*kkhandhaka$'],
      'levels': [None, [r're:.']]},
     {'title': 'Parivāra-aṭṭhakathā', 'lo': 186, 'hi': 300,
      'tops': ['Soḷasamahāvāra', 'Mahāvibhaṅge ca Bhikkhunivibhaṅge ca',
               'Antarapeyyāla', 'Khandhakapucchāvāra', 'Ekuttarikanaya',
               'Uposathādipucchāvissajjanā', 'Paṭhamagāthāsaṅgaṇika',
               'Adhikaraṇabheda', 'Dutiyagāthāsaṅgaṇika', 'Codanākaṇḍa',
               'Cūḷasaṅgāma', 'Mahāsaṅgāma', 'Kathinabheda', 'Upālipañcaka',
               'Aparadutiyagāthāsaṅgaṇika', 'Sedamocanagāthā', 'Pañcavagga'],
      'levels': [None, [r're:.']]},
   ],
 },
 # --- 03VinA03: THREE BOOKS, three different top shapes ---------------------
 # Cover `PĀCITYĀDI-AṬṬHAKATHĀ`, `Samantapāsādikā nāma`.  Each book takes its
 # tops from the structure of the canon text it comments on, which is the
 # lesson 04VinA04's Parivāra taught:
 #   Pācityādi          -> the KAṆḌAS (5. Pācittiya, 6. Pāṭidesanīya,
 #                         7. Sekhiya, 8. Sattādhikaraṇasamatha), vaggas below
 #                         the Pācittiya only -> non-uniform depth, `level_memo`
 #   Bhikkhunīvibhaṅga  -> its own kaṇḍas, vaggas below the Pācittiya
 #   Mahāvagga          -> the KHANDHAKAS, an open numbered set
 '03VinA03': {
   'title': 'Pācityādi-aṭṭhakathā',
   # !!! ONE NODE PER PRINTED VOLUME, NOT PER INNER BOOK.  01VinA01-04VinA04
   # are four bhāgas of ONE work, the Samantapāsādikā — 03VinA03's own cover
   # says so, `Samantapāsādikā nāma / PĀCITYĀDI-AṬṬHAKATHĀ`.  Its three inner
   # divisions mirror the canon's Vinaya divisions; they are not separate works
   # the way the Dhātukathā and Puggalapaññatti are two of the Abhidhamma's
   # seven books, which is the case `separate_books` exists for.  Declaring it
   # here put NINE names in the sidebar where the edition prints SIX volumes.
   'label': 'Pācityādi-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 10),
   'matika_gate': False,
   'matika_centred_gate': False,
   'level_memo': True,
   'books': [
     {'title': 'Pācityādi-aṭṭhakathā', 'lo': 0, 'hi': 295,
      'tops': [r're:\d+\.\s+(?:.*kaṇḍa|Sattādhikaraṇasamatha)$'],
      'levels': [None, [r're:\d+\.\s+\S*vagga$'], [r're:.']]},
     {'title': 'Bhikkhunīvibhaṅgavaṇṇanā', 'lo': 295, 'hi': 463,
      'tops': [r're:\d+\.\s+.*kaṇḍa$'],
      'levels': [None, [r're:\d+\.\s+\S*vagga$'], [r're:.']]},
     {'title': 'Mahāvagga-aṭṭhakathā', 'lo': 463, 'hi': 738,
      'tops': [r're:\d+\.\s+.*kkhandhaka$'],
      'levels': [None, [r're:.']]},
   ],
 },
 # --- 01VinA01: ONE BOOK — the Bāhiranidāna, then the first two pārājikas ----
 # Cover `PĀRĀJIKAKAṆḌA-AṬṬHAKATHĀ (Paṭhamo bhāgo)`; 02VinA02 sets the same
 # inner title, so the BHĀGA is what keeps the two nav nodes apart.
 # Its first 78 printed pages are the Ganthārambha and the Bāhiranidāna — the
 # three councils — which entered the corpus only on 2026-07-27s; before that
 # this volume had no nav worth writing because two thirds of it was absent.
 '01VinA01': {
   'title': 'Pārājikakaṇḍa-aṭṭhakathā',
   'label': 'Pārājikakaṇḍa-aṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika_gate': False,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': ['Ganthārambhakathā', 'Bāhiranidānakathā', 'Verañjakaṇḍavaṇṇanā',
            '1. Pārājikakaṇḍa'],
   'levels': [None, [r're:\d+\.\s'], [r're:.']],
 },
}

A.SPEC.update(VINA)
A.main()
