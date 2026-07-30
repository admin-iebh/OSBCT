#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Navs for the Khuddaka commentaries, 20KhuA01-47KhuA28.

Twenty-eight volumes, of which this file so far carries one.
"""
import build_abhidhamma_nav as A

WORK = 'Khuddaka — commentaries'
KATHA = r're:\d+(?:-\d+)?\.\s+\S*kathā(?:vaṇṇanā)?$'

KHUA = {
 '35KhuA16': {
   'title': 'Cariyāpiṭakaṭṭhakathā',
   'work': WORK,
   'first': 0,
   # 1-based pp4-5 = 0-based 3-4.  The body opens on 1-based p6.  A TWO-page
   # mātikā cannot filter its own title stack, so `matika_drop` names it.
   'matika': (3, 4),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # !!! `Uddānagāthāvaṇṇanā` AND `Nigamanakathā` CANNOT BE TOPS, and the reason
   # is a corpus defect, not a reading of the edition: ord336 runs from printed
   # p267 to p332 — **115,736 characters, SIXTY-SIX PAGES IN ONE PARAGRAPH** —
   # and swallows all three closing sections.  A `sections/` entry is keyed by
   # ORDINAL, so only ONE of the three can be held there, and it is
   # `Pakiṇṇakakathā`.  Declared as tops the other two stop the forward-only
   # walk at its first step and SIX of the eight tops vanish.  The same answer
   # 20KhuA01 ord24 forced, with the reason written down (2026-07-29j).
   'tops': ['Ganthārambhakathā', 'Nidānakathā', '1. Akittivagga',
            '2. Hatthināgavagga', '3. Yudhañjayavagga', 'Pakiṇṇakakathā'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Cariyāpiṭakaṭṭhakathā'],
   # THE EDITION SETS A FOOTNOTE MARKER INSIDE A HEADING'S OWN WORD — p193
   # heads `4. Bhisacariyā2vaṇṇanā`, the marker between `cariyā` and `vaṇṇanā`,
   # where the mātikā (p5) reads `4. Bhisacariyāvaṇṇanā`.  Not a misprint of
   # the NAME: the printed reading is kept and the mātikā's form is the
   # alternative fold.
   'body_errata': {'4. Bhisacariyā2vaṇṇanā': '4. Bhisacariyāvaṇṇanā'},
 },
 '34KhuA15': {
   'title': 'Buddhavaṁsaṭṭhakathā',
   'work': WORK,
   'first': 0,
   # 1-based pp4-5 = 0-based 3-4.  The body opens on 1-based p6.  A TWO-page
   # mātikā cannot filter its own title stack (`matika_headers` needs a line
   # opening three or more pages), so `matika_drop` names it.
   'matika': (3, 4),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # TWO rungs.  `tops` CANNOT MIX A LITERAL WITH A PATTERN, so all thirty are
   # named: the two unnumbered openings plus the mātikā's own 1-28.  Everything
   # else hangs off whichever of them it follows — `Bāhiranidāna` and
   # `Abbhantaranidāna` under `Nidānakathā` (which the BODY heads and the
   # mātikā does not), the three nidāna kathās under `27. Gotama…`, and the
   # five closing kathās under `28. Buddhapakiṇṇakakathā`.
   'tops': [
            'Ganthārambhakathā', 'Nidānakathā',
            '1. Ratanacaṅkamanakaṇḍavaṇṇanā',
            '2. Sumedhapatthanākathāvaṇṇanā',
            '3. Dīpaṅkarabuddhavaṁsavaṇṇanā',
            '4. Koṇḍaññabuddhavaṁsavaṇṇanā', '5. Maṅgalabuddhavaṁsavaṇṇanā',
            '6. Sumanabuddhavaṁsavaṇṇanā', '7. Revatabuddhavaṁsavaṇṇanā',
            '8. Sobhitabuddhavaṁsavaṇṇanā',
            '9. Anomadassībuddhavaṁsavaṇṇanā',
            '10. Padumabuddhavaṁsavaṇṇanā', '11. Nāradabuddhavaṁsavaṇṇanā',
            '12. Padumuttarabuddhavaṁsavaṇṇanā',
            '13. Sumedhabuddhavaṁsavaṇṇanā', '14. Sujātabuddhavaṁsavaṇṇanā',
            '15. Piyadassībuddhavaṁsavaṇṇanā',
            '16. Atthadassībuddhavaṁsavaṇṇanā',
            '17. Dhammadassībuddhavaṁsavaṇṇanā',
            '18. Siddhatthabuddhavaṁsavaṇṇanā',
            '19. Tissabuddhavaṁsavaṇṇanā', '20. Phussabuddhavaṁsavaṇṇanā',
            '21. Vipassībuddhavaṁsavaṇṇanā', '22. Sikhībuddhavaṁsavaṇṇanā',
            '23. Vessabhūbuddhavaṁsavaṇṇanā',
            '24. Kakusandhabuddhavaṁsavaṇṇanā',
            '25. Koṇāgamanabuddhavaṁsavaṇṇanā',
            '26. Kassapabuddhavaṁsavaṇṇanā', '27. Gotamabuddhavaṁsavaṇṇanā',
            '28. Buddhapakiṇṇakakathā'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Buddhavaṁsaṭṭhakathā'],
   # THE BODY AND THE MĀTIKĀ DISAGREE ON ONE KATHĀ NAME AND NOTHING ARBITRATES:
   # p357 heads `Anantarāyikadhammakathā`, the mātikā (p5) reads
   # `Antarāyikadhammakathā`, and this section has NO closing colophon — the
   # third witness that settled all six of 33KhuA14's errata is simply absent
   # here.  So the printed body reading STANDS and the mātikā's form is the
   # alternative fold; which of the two the author wrote is UNRESOLVED and is
   # recorded as such rather than guessed (principle 2).
   'body_errata': {'Anantarāyikadhammakathā': 'Antarāyikadhammakathā'},
 },
 '33KhuA14': {
   'title': 'Apadānaṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   # 1-based pp4-13 = 0-based 3-12.  The body opens on 1-based p14.  TEN mātikā
   # pages, so `matika_headers` filters the running header on its own.
   'matika': (3, 12),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # THREE rungs — `Therāpadāna`, its vaggas, their apadānavaṇṇanās — and the
   # volume opens MID-WORK at the SECOND vagga, because 32KhuA13 carries the
   # Buddhavagga.  `Nigamanakathā` (p316) closes it.
   'tops': ['Therāpadāna', 'Nigamanakathā'],
   'levels': [None, [r're:^\d+\.\s+\S*vagga$'], [r're:.']],
   'matika_drop': ['Apadānaṭṭhakathā', 'Dutiyabhāga'],
   # !!! THE EDITION NUMBERS TWO CONSECUTIVE VAGGAS `10.`  p127 heads
   # `10. Sudhāvagga` and p133 `10. Bhikkhadāyivagga`, where the mātikā reads
   # `11. Bhikkhadāyivagga` — so the eleventh group head was absent from the
   # tree and the centred gate REFUSED it, the only refusal in the volume.
   # Misprinted ONCE and on the BODY side, so `body_errata`: the printed
   # reading stands in the tree and the mātikā's form is the alternative fold.
   # FIVE MORE ERRATA, and the section's OWN closing colophon decides each —
   # which is what splits them four to one rather than five to nothing.
   # MĀTIKĀ misprints -> `errata`:
   #   p5 `Bhāgineyyupāliṭṭhera-`   body p79 + colophon p80 `…pālitthera-`
   #   p8 `…apadānavaṇṇā`  x2       body + colophon `…apadānavaṇṇanā`
   #   p9 `8. Phaladāyakatthera-`   body p172 + colophon p173 `Phalakadāyaka-`
   # !!! THE LAST ONE MUST BE KEYED ON THE WHOLE NUMBERED ENTRY: the mātikā
   # prints `Phaladāyakatthera-apadānavaṇṇanā` THREE times (p7, p8 as `7.` and
   # p9 as `8.`), two of which are a DIFFERENT thera whose name is correct, so
   # a global rewrite of the name would corrupt both (29KhuA10, 2026-07-29d).
   'errata': {'1. Bhāgineyyupāliṭṭhera-apadānavaṇṇanā':
              '1. Bhāgineyyupālitthera-apadānavaṇṇanā',
              '8. Maggasaññakatthera-apadānavaṇṇā':
              '8. Maggasaññakatthera-apadānavaṇṇanā',
              '1. Sereyyakatthera-apadānavaṇṇā':
              '1. Sereyyakatthera-apadānavaṇṇanā',
              '8. Phaladāyakatthera-apadānavaṇṇanā':
              '8. Phalakadāyakatthera-apadānavaṇṇanā'},
   # BODY misprints -> `body_errata`.  `2. Ekatthambhīkatthera-` (p16) is the
   # ODD ONE OUT: the mātikā (p4) AND the section's own colophon (p17) both set
   # a SHORT `i`, so the body head is the misprint even though it is the mātikā
   # that differs from the tree.  **Read the colophon before choosing the key**
   # — on form alone this looks identical to the four above and is not.
   'body_errata': {'10. Bhikkhadāyivagga': '11. Bhikkhadāyivagga',
                   '2. Ekatthambhīkatthera-apadānavaṇṇanā':
                   '2. Ekatthambhikatthera-apadānavaṇṇanā'},
 },
 '32KhuA13': {
   'title': 'Apadānaṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   # A ONE-PAGE MĀTIKĀ — 1-based p4 = 0-based 3, both ends.  The body opens on
   # p5.  `matika_headers` needs a line opening THREE or more pages, so a
   # single-page mātikā cannot filter its own title stack: `matika_drop` names
   # the two lines (25KhuA06, 2026-07-28x).  Its closing
   # `…mātikā niṭṭhitā.` is dropped by `matika_lines` already.
   'matika': (3, 3),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # THREE rungs, and the mātikā's own CENTRED lines are the group heads:
   # `Nidānakathā` and `Therāpadāna` above, `1. Buddhavagga` inside the second.
   # Depth is NOT in the mātikā's indent here — a dotted entry's indent varies
   # with the NAME'S LENGTH, exactly as a centred head's does — so it comes
   # from the `levels` patterns.
   'tops': ['Ganthārambhakathā', 'Nidānakathā', 'Therāpadāna'],
   'levels': [None, [r're:^\d+\.\s+\S*(nidānakathā|vagga)$'], [r're:.']],
   'matika_drop': ['Apadānaṭṭhakathā', 'Paṭhamabhāga'],
 },
 '31KhuA12': {
   'title': 'Therīgāthā-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   # 1-based pp4-7 = 0-based 3-6.  The body opens on 1-based p8.
   'matika': (3, 6),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # TWO rungs, the 30KhuA11 shape: the edition does not divide a therī nipāta
   # into vaggas, so the therīgāthāvaṇṇanās hang straight off it.  Sixteen
   # nipātas as the edition NUMBERS them — it counts 1-16 while naming them
   # Ekaka … Mahā, so the numbers do not track the gāthā counts.  `Nigamanagāthā`
   # (p312) is a real printed head and closes the volume.
   'tops': ['1. Ekakanipāta', '2. Dukanipāta', '3. Tikanipāta',
            '4. Catukkanipāta', '5. Pañcakanipāta', '6. Chakkanipāta',
            '7. Sattakanipāta', '8. Aṭṭhakanipāta',
            # NAMED AS THE EDITION PRINTS IT, misprint and all — `tops` is
            # matched against the printed head stream, so the mātikā's spelling
            # here stopped the forward-only walk dead at the ninth nipāta and
            # eight of the sixteen tops vanished.  `body_errata` below is what
            # reconciles it with the mātikā and the colophon.
            '9. Navanīpāta',
            '10. Ekādasanipāta', '11. Dvādasanipāta', '12. Soḷasanipāta',
            '13. Vīsatinipāta', '14. Tiṁsanipāta', '15. Cattālīsanipāta',
            '16. Mahānipāta', 'Nigamanagāthā'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Therīgāthā-aṭṭhakathā'],
   # !!! THE BODY MISPRINTS A NIPĀTA NAME WITH A LONG `ī`.  p184 heads
   # `9. Navanīpāta`; the mātikā (p6), the section's own colophon (p187) and the
   # body's very next line (`Navanipāte mā su te vaḍḍha…`) all read `Navanipāta`.
   # Misspelt ONCE and on the BODY side, so `body_errata` — the printed reading
   # is preserved and the mātikā's form goes on the tree side (35Abhi07).
   'body_errata': {'9. Navanīpāta': '9. Navanipāta'},
 },
 '30KhuA11': {
   'title': 'Theragāthā-aṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   # 1-based pp4-7 = 0-based 3-6.  The body opens on 1-based p8.
   'matika': (3, 6),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # TWO rungs, not three: from the Catukkanipāta on the edition stops dividing
   # a nipāta into vaggas, so the theragāthāvaṇṇanās hang straight off it.
   # The volume opens MID-WORK — 29KhuA10 closes after the Tikanipāta — so
   # there is no Ganthārambhakathā here and the first top is the Catukkanipāta.
   'tops': ['4. Catukkanipāta', '5. Pañcakanipāta', '6. Chakkanipāta',
            '7. Sattakanipāta', '8. Aṭṭhakanipāta', '9. Navakanipāta',
            '10. Dasakanipāta', '11. Ekādasanipāta', '12. Dvādasakanipāta',
            '13. Terasanipāta', '14. Cuddasakanipāta', '15. Soḷasakanipāta',
            '16. Vīsatinipāta', '17. Tiṁsanipāta', '18. Cattālīsanipāta',
            '19. Paññāsanipāta', '20. Saṭṭhinipāta', '21. Mahānipāta'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Theragāthā-aṭṭhakathā', 'Dutiyabhāga'],
 },
 '29KhuA10': {
   'title': 'Theragāthā-aṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   # 1-based pp4-11 = 0-based 3-10.  The body opens on 1-based p12.  EIGHT
   # mātikā pages, so `matika_headers` can filter the running header on its own
   # (the three-page rule is met); only the FIRST page's title stack needs
   # naming, and the edition sets it as two lines.
   'matika': (3, 10),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # THREE rungs — nipāta, vagga, theragāthāvaṇṇanā — the 27KhuA08 shape.
   # The two opening pieces stand ungrouped, as the mātikā sets them.
   'tops': ['Ganthārambhakathā', 'Nidānagāthāvaṇṇanā',
            '1. Ekakanipāta', '2. Dukanipāta', '3. Tikanipāta'],
   'levels': [None, [r're:\d+\.\s+\S*vagga$'], [r're:.']],
   'matika_drop': ['Theragāthā-aṭṭhakathā', 'Paṭhamabhāga'],
   # !!! THE HEADS-STREAM/MĀTIKĀ DIFF FINDS SIX ERRATA IN THIS VOLUME, THREE ON
   # EACH SIDE, and the tie-breaker in every case is the section's OWN closing
   # colophon two pages later.  Counted on both sides before choosing the key,
   # as START HERE requires.
   #
   # MĀTIKĀ misprints -> `errata` (each keyed on the WHOLE numbered entry,
   # which is printed once; the bare name is not unique — the mātikā lists
   # `Kumāputtattheragāthāvaṇṇanā` for BOTH its 6th and 7th entries, and a
   # global rewrite of the name would corrupt the 6th):
   #   p5  `7. Kumāputtattheragāthāvaṇṇanā`   body p138/p139 `…sahāya…`
   #   p7  `5. Susāradattattheragāthāvaṇṇanā` body p221/p223 `Susāradat…`
   'errata': {'7. Kumāputtattheragāthāvaṇṇanā':
              '7. Kumāputtasahāyattheragāthāvaṇṇanā',
              '5. Susāradattattheragāthāvaṇṇanā':
              '5. Susāradattheragāthāvaṇṇanā'},
   # BODY misprints -> `body_errata`, which keeps the printed reading and puts
   # the mātikā's form on the TREE side (35Abhi07):
   #   p150 `3. Sumaṅgalattheraghāthāvaṇṇanā`     colophon p152 `…gāthā…`
   #   p156 `5 Ramaṇīyavihārittheragāthāvaṇṇanā`  no period after the number
   #   p223 `6. Piyañjahattheragāthāvaṇṇanās`     colophon p225 without the `s`
   #   p471 `10. Sāṭhimattiyattheragāthāvaṇṇanā`  colophon p473 `Sāṭimattiya…`
   'body_errata': {'3. Sumaṅgalattheraghāthāvaṇṇanā':
                   '3. Sumaṅgalattheragāthāvaṇṇanā',
                   '5 Ramaṇīyavihārittheragāthāvaṇṇanā':
                   '5. Ramaṇīyavihārittheragāthāvaṇṇanā',
                   '6. Piyañjahattheragāthāvaṇṇanās':
                   '6. Piyañjahattheragāthāvaṇṇanā',
                   '10. Sāṭhimattiyattheragāthāvaṇṇanā':
                   '10. Sāṭimattiyattheragāthāvaṇṇanā'},
 },
 '28KhuA09': {
   'title': 'Petavatthu-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   # 1-based pp4-6 = 0-based 3-5.  The body opens on 1-based p7.
   'matika': (3, 5),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': ['Ganthārambhakathā', '1. Uragavagga', '2. Ubbarivagga',
            '3. Cūḷavagga', '4. Mahāvagga', 'Nigamanakathā'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Petavatthu-aṭṭhakathā'],
 },
 '27KhuA08': {
   'title': 'Vimānavatthu-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   # 1-based pp4-7 = 0-based 3-6.  The body opens on 1-based p8.
   'matika': (3, 6),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # THREE rungs: the Vimānavatthu's two halves — Itthivimāna and Purisavimāna
   # — then the seven vaggas, then the vimānavaṇṇanās.
   'tops': ['Ganthārambhakathā', '1. Itthivimāna', '2. Purisavimāna',
            'Nigamanakathā'],
   'levels': [None, [r're:\d+\.\s+\S*vagga$'], [r're:.']],
   'matika_drop': ['Vimānavatthu-aṭṭhakathā'],
   # NO `errata` FOR `Pèyāsivagga` ANY MORE.  The body head on p272 read
   # `6. Pèyāsivagga` with a Latin-1 `è` where the mātikā and the vagga's own
   # colophon (p286, `Chaṭṭhassa Pāyāsivaggassa…`) read `ā` — an UNMAPPED GLYPH
   # of the conversion, not a variant of the edition.  It is now CORRECTED from
   # `data/glyph_errata.json` before the builder ever sees the page, so both
   # sides read `Pāyāsivagga` and the entry resolves on its own (2026-07-29a).
 },
 '26KhuA07': {
   'title': 'Suttanipātaṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   # 1-based pp4-6 = 0-based 3-5.  The body opens on 1-based p7.
   'matika': (3, 5),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # The Cūḷavagga from its FOURTH sutta — 25KhuA06 stops after the third —
   # then the Mahā-, Aṭṭhaka- and Pārāyanavaggas, and the three closing pieces
   # the mātikā sets ungrouped.
   # !!! THE VOLUME OPENS MID-VAGGA AND `2. Cūḷavagga` IS NEVER PRINTED HERE —
   # its head belongs to 25KhuA06's body, which is where that vagga began.  So
   # the Cūḷavagga's remaining eleven suttas stand at the top level in their
   # own right, exactly as 47KhuA28's five orphaned ñāṇa-niddesas do, and the
   # vagga label is dropped from the mātikā rather than left refusing.
   'tops': ['4. Maṅgalasuttavaṇṇanā', '5. Sūcilomasuttavaṇṇanā',
            '6. Kapilasutta (Dhammacariyasutta) vaṇṇanā',
            '7. Brāhmaṇadhammikasuttavaṇṇanā',
            '8. Dhammasutta (Nāvāsutta) vaṇṇanā', '9. Kiṁsīlasuttavaṇṇanā',
            '10. Uṭṭhānasuttavaṇṇanā', '11. Rāhulasuttavaṇṇanā',
            '12. Nigrodhakappasutta (Vaṅgīsasutta) vaṇṇanā',
            '13. Sammāparibbājanīyasutta (Mahāsamayasutta) vaṇṇanā',
            '14. Dhammikasuttavaṇṇanā',
            '3. Mahāvagga', '4. Aṭṭhakavagga', '5. Pārāyanavagga',
            'Pārāyanatthutigāthāvaṇṇanā', 'Pārāyanānugītigāthāvaṇṇanā',
            'Nigamanakathā'],
   'levels': [None, [r're:.']],
   # The mātikā runs to three pages, so `matika_headers` filters the running
   # header on its own; the title stack of the FIRST page and the vagga label
   # above are what remain.
   'matika_drop': ['Suttanipātaṭṭhakathā', 'Dutiyabhāga', '2. Cūḷavagga'],
   # !!! `matika_gate` IS FALSE FOR ONE ENTRY, AND IT IS A CORPUS DEFECT.
   # `4. Pūraḷāsasutta (Sundarikabhāradvājasutta) vaṇṇanā` is printed as a
   # centred body heading and the tree cannot hold it: the corpus glued it onto
   # the narrative that follows (ord190, 3,179 characters), and its `4.` became
   # the paragraph's own number.  Same family as 20KhuA01 ord24, 22KhuA03 ord34
   # and 36KhuA17 ord113 — the fix is a corpus split.  NOT `matika_drop`: the
   # edition really prints it in both places.
   'matika_gate': False,
 },
 '25KhuA06': {
   'title': 'Suttanipātaṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   # The front matter is a SINGLE page: 1-based p4 = 0-based 3.  The body opens
   # on 1-based p5.
   'matika': (3, 3),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # Buddhaghosa's Paramatthajotikā II: the Ganthārambhakathā, the whole
   # Uragavagga (12 suttas) and the first three suttas of the Cūḷavagga — the
   # volume stops mid-vagga and 26KhuA07 continues it.
   'tops': ['Ganthārambhakathā', '1. Uragavagga', '2. Cūḷavagga'],
   'levels': [None, [r're:.']],
   # !!! A ONE-PAGE MĀTIKĀ CANNOT HAVE ITS HEADER FILTERED BY `matika_headers`,
   # which drops only a line seen on THREE OR MORE of the range's pages.  This
   # volume's mātikā is a single page, so its own title stack —
   # `Suttanipātaṭṭhakathā` / `Paṭhamabhāga` — was read as two entries and, both
   # being centred, refused the centred gate as well.  `matika_drop` is the
   # right tool HERE (unlike 37KhuA18, where the range had eaten a body page):
   # the edition really prints these lines inside the mātikā and they are its
   # heading, not entries.
   'matika_drop': ['Suttanipātaṭṭhakathā', 'Paṭhamabhāga'],
 },
 '24KhuA05': {
   'title': 'Itivuttakaṭṭhakathā',
   'work': WORK,
   'first': 0,
   # 1-based pp4-8 = 0-based 3-7.  The body opens on 1-based p9.
   'matika': (3, 7),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # Dhammapāla's Paramatthadīpanī on the Itivuttaka: the Ganthārambhakathā,
   # then FOUR nipātas, three of them divided into vaggas and the Catukka not.
   # `Nigamanakathā` closes the body and is NOT in the printed mātikā; left
   # under the Catukkanipāta it made that nipāta 14 children where the edition
   # gives it 13 suttas.
   'tops': ['Ganthārambhakathā', '1. Ekakanipāta', '2. Dukanipāta',
            '3. Tikanipāta', '4. Catukkanipāta', 'Nigamanakathā'],
   'levels': [None, [r're:\d+\.\s+\S*vagga$'], [r're:.']],
 },
 '22KhuA03': {
   'title': 'Dhammapadaṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   # 1-based pp4-12 = 0-based 3-11.  The body opens on 1-based p13.
   'matika': (3, 11),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # Vaggas 9-26 of the Dhammapada — verses 116-423.  No Ganthārambhakathā:
   # the work opened in 21KhuA02 and this volume continues it.
   'tops': ['9. Pāpavagga', '10. Daṇḍavagga', '11. Jarāvagga', '12. Attavagga',
            '13. Lokavagga', '14. Buddhavagga', '15. Sukhavagga',
            '16. Piyavagga', '17. Kodhavagga', '18. Malavagga',
            '19. Dhammaṭṭhavagga', '20. Maggavagga', '21. Pakiṇṇakavagga',
            '22. Nirayavagga', '23. Nāgavagga', '24. Taṇhāvagga',
            '25. Bhikkhuvagga', '26. Brāhmaṇavagga'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Dutiyabhāga'],
   # SIX SPELLING DISAGREEMENTS BETWEEN THE MĀTIKĀ AND THE BODY, mātikā reading
   # -> body reading.  Neither side is corrected; both are preserved and the
   # pair is named so the entry resolves.  `1. Māradhītaravatthu1` is the
   # footnote-marker-inside-a-heading class, third seen after 43KhuA24 and
   # 37KhuA18 — declared as an erratum rather than stripped by rule, because a
   # digit glued to a heading is not always a marker.
   'errata': {'12. Subbabuddhasakyavatthu': '12. Suppabuddhasakyavatthu',
              '8. Bahubhaṇḍibhikkhuvatthu': '8. Bahubhaṇḍikabhikkhuvatthu',
              '10. Attadattattheravatthu': '10. Attadatthattheravatthu',
              '1. Māradhītaravatthu': '1. Māradhītaravatthu1',
              '3. Vaggamudātīriyabhikkhuvatthu': '3. Vaggumudātīriyabhikkhukavatthu',
              '1. Attadaṇḍavatthu': '1. Attadantavatthu'},
   # !!! `matika_gate` IS FALSE FOR ONE ENTRY, AND IT IS A CORPUS DEFECT.
   # `1. Visākhāya sahāyikānaṁ vatthu` is printed as a centred body heading
   # (p76, indent 21) and the tree cannot hold it, because the corpus merged it
   # into the narrative that follows: ord34 reads
   # `1. Visākhāya sahāyikānaṁ vatthu Ko nu hāso kimānandoti imaṁ
   # dhammadesanaṁ…` and its `1.` was then read as the paragraph's VERSE
   # NUMBER — which is why the corpus n-sequence descends 145 -> 1 there.
   # NOT declared `matika_drop`: the edition really prints it, in the mātikā
   # AND in the body, and dropping it would silence the gate and leave the
   # defect unrecorded (37KhuA18, 2026-07-28m).  228 of the 229 entries
   # resolve; the centred gate still holds at 18 of 18.  Same family as
   # 20KhuA01 ord24 and 36KhuA17 ord113 — the fix is a corpus split.
   'matika_gate': False,
 },
 '21KhuA02': {
   'title': 'Dhammapadaṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   # 1-based pp4-7 = 0-based 3-6.  The body opens on 1-based p8.
   'matika': (3, 6),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # The Ganthārambhakathā, then the first EIGHT vaggas of the Dhammapada —
   # verses 1-115 — each printed as a centred numbered head with its vatthus
   # under it.
   'tops': ['Ganthārambhakathā', '1. Yamakavagga', '2. Appamādavagga',
            '3. Cittavagga', '4. Pupphavagga', '5. Bālavagga',
            '6. Paṇḍitavagga', '7. Arahantavagga', '8. Sahassavagga'],
   'levels': [None, [r're:.']],
   # TWO SPELLING DISAGREEMENTS BETWEEN THE MĀTIKĀ AND THE BODY, mātikā
   # reading -> body reading.  Neither side is corrected; both are preserved.
   #   Meghiyattheravatthu / Meghiyattheravattha        (p189)  final -a
   #   Aññatara-ukkaṇṭhita… / Aññatara-ukkaṇḍhita…      (p355)  ṭh / ḍh
   'errata': {'1. Meghiyattheravatthu': '1. Meghiyattheravattha',
              '3. Aññatara-ukkaṇṭhitabhikkhuvatthu':
                  '3. Aññatara-ukkaṇḍhitabhikkhuvatthu'},
 },
 '20KhuA01': {
   'title': 'Khuddakapāṭhaṭṭhakathā',
   'work': WORK,
   'first': 0,
   # 1-based pp14-18 = 0-based 13-17.  The body opens on 1-based p19, so the
   # range stops at 17 — inclusive at both ends (the 37KhuA18 trap).
   'matika': (13, 17),
   # !!! `matika_gate` IS FALSE, AND THE REASON IS A CORPUS DEFECT, NOT AN
   # ABBREVIATING MĀTIKĀ.  TEN entries — `Ekaṁ nāma kintipañhavaṇṇanā` through
   # `Dasa nāma kintipañhavaṇṇanā`, the Kumārapañha's ten answers — are printed
   # as CENTRED BODY HEADINGS (p81, p83, …, p92) and the tree cannot hold them,
   # because the corpus holds printed pp63-74 as ONE paragraph: ord24, 18,719
   # characters, with all ten headings inside its text.  A `sections/` entry is
   # keyed by ORDINAL, so there is no ordinal for a heading in mid-paragraph.
   # NOT declared `matika_drop`: the edition really prints them, and dropping
   # them would silence the gate and leave the defect unrecorded (37KhuA18,
   # 2026-07-28m).  108 of the 118 entries resolve; the centred gate still
   # holds at 9 of 9.  The fix is a corpus split at those ten heads, with the
   # re-key that implies — deferred, and recorded in HANDOFF 2026-07-28r.
   'matika_gate': False,
   'matika_centred_gate': True,
   'level_memo': True,
   # The Paramatthajotikā I: three ungrouped openers, then the NINE works of
   # the Khuddakapāṭha as centred numbered heads, then the closing kathā.
   # `Nigamanakathā` closes the body but is NOT in the printed mātikā.
   'tops': ['Ganthārambhakathā', 'Khuddakavavatthāna', 'Nidānasodhana',
            '1. Saraṇattayavaṇṇanā', '2. Sikkhāpadavaṇṇanā',
            '3. Dvattiṁsākāravaṇṇanā', '4. Kumārapañhavaṇṇanā',
            '5. Maṅgalasuttavaṇṇanā', '6. Ratanasuttavaṇṇanā',
            '7. Tirokuṭṭasuttavaṇṇanā', '8. Nidhikaṇḍasuttavaṇṇanā',
            '9. Mettasuttavaṇṇanā', 'Nigamanakathā'],
   'levels': [None, [r're:.']],
   # FOUR SPELLING DISAGREEMENTS BETWEEN THE MĀTIKĀ AND THE BODY, mātikā
   # reading -> body reading.  Neither side is corrected; both are preserved
   # and the pair is named so the entry resolves.
   #   Bhedābhada- / Bhedābhede-   (p25)   the body has the expected `e`
   #   Aṭṭhuppatti / Aṭṭhuppati    (p80)   the body drops a `t`
   #   Yānīdhāhi-  / Yānīdhāti-    (p157)  the body has the expected `ti`
   #   Suttaṭṭhupatti / Suttaṭṭhuppatti (p201) the body doubles the `p`
   'errata': {'Bhedābhadaphaladīpanā': 'Bhedābhedaphaladīpanā',
              'Aṭṭhuppatti': 'Aṭṭhuppati',
              'Yānīdhāhigāthāvaṇṇanā': 'Yānīdhātigāthāvaṇṇanā',
              'Suttaṭṭhupatti': 'Suttaṭṭhuppatti'},
 },
 '23KhuA04': {
   'title': 'Udānaṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 6),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # The Paramatthadīpanī on the Udāna, and the plainest shape in the layer:
   # `Ganthārambhakathā`, EIGHT vaggas of TEN suttavaṇṇanās each — numbered
   # 1..8 and 1..10 with no gap anywhere, which is the check that none was
   # missed — and `Nigamanakathā`.
   'tops': ['Ganthārambhakathā',
            '1. Bodhivagga', '2. Mucalindavagga', '3. Nandavagga',
            '4. Meghiyavagga', '5. Soṇavagga', '6. Jaccandhavagga',
            '7. Cūḷavagga', '8. Pāṭaligāmiyavagga',
            'Nigamanakathā'],
   'levels': [None, [r're:.']],
   # The edition drops an `l`: the mātikā sets `1. Paṭhamakuṇḍakabhaddiya…`
   # where the body (p327) sets `1. Paṭhamalakuṇḍakabhaddiya…` — and the
   # mātikā's OWN next entry, `2. Dutiyalakuṇḍakabhaddiyasuttavaṇṇanā`, keeps
   # the `l`, so the mātikā is the side that slipped.  Neither is corrected.
   'errata': {'1. Paṭhamakuṇḍakabhaddiyasuttavaṇṇanā':
                  '1. Paṭhamalakuṇḍakabhaddiyasuttavaṇṇanā'},
 },
 '45KhuA26': {
   'title': 'Netti-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 4),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': ['Ganthārambhakathā', '1. Saṅgahavāravaṇṇanā',
            '2. Uddesavāravaṇṇanā', '3. Niddesavāravaṇṇanā',
            '4. Paṭiniddesavāra', 'Nayasamuṭṭhānavāravaṇṇanā',
            'Sāsanapaṭṭhānavāravaṇṇanā', 'Nigamanakathā'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Netti-aṭṭhakathā'],
 },
 '36KhuA17': {
   'title': 'Jātakaṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 9),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': ['Ganthārambhakathā', 'Nidānakathā', '1. Ekakanipāta'],
   'levels': [None, [r're:\d+(?:-\d+)?\.\s+\S*vagga$'], [r're:.']],
   # TWO PRINTED LINES ARE NOT HEADINGS AND THE BUILDER CANNOT BE TOLD SO (see
   # the SPEC note in build_khu_volume.py).  The nav at least does not repeat
   # the mistake: `head_skip` is checked against the edition, so it cannot
   # silently stop matching.
   'head_skip': ['Jātakaṭṭhakathā',
                 'Jetavanamahāvihāre viharanto kathesi. Kaṁ pana ārabbha ayaṁ kathā'],
   'errata': {'4. Cūḷaseṭṭhijātakavaṇṇanā': '4. Cūḷasiṭṭhijātakavaṇṇanā',
              '8. Nandivisālajātakavaṇṇanā (28)':
                  '8. Nandisālajātakavaṇṇanā (28)'},
   'matika_drop': ['Jātakaṭṭhakathā', 'Paṭhamabhāga', 'Uddānagāthā'],
 },
 '37KhuA18': {
   'title': 'Jātakaṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 9),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': ['2. Dukanipāta', '3. Tikanipāta'],
   'levels': [None, [r're:\d+(?:-\d+)?\.\s+\S*vagga$'], [r're:.']],
   'errata': {'6. Kurudhammajātakavaṇṇanā (276)':
                  '6. Kurudhammajātakavaṇṇanā1 (276)'},
   'matika_drop': ['Jātakaṭṭhakathā', 'Dutiyabhāga', 'Uddānagāthā'],
 },
 '41KhuA22': {
   'title': 'Jātakaṭṭhakathā (Chaṭṭho bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 3),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': ['22. Mahānipāta'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Jātakaṭṭhakathā', 'Chaṭṭhabhāga'],
 },
 '38KhuA19': {
   'title': 'Jātakaṭṭhakathā (Tatiyo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 9),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # SIX nipātas, 4 to 9, each divided into VAGGAS — the first volume in the
   # series whose nipātas take a middle rung.
   'tops': ['4. Catukkanipāta', '5. Pañcakanipāta', '6. Chakkanipāta',
            '7. Sattakanipāta', '8. Aṭṭhakanipāta', '9. Navakanipāta'],
   'levels': [None, [r're:\d+(?:-\d+)?\.\s+\S*vagga$'], [r're:.']],
   # Two of the edition's own, both preserved.  The second is a JĀTAKA NUMBER:
   # the mātikā gives the Cetiyajātaka as **422** and the body heads it **442**.
   # 422 is the number the canon carries and the one this nipāta's neighbours
   # are consistent with, so the body is the side that slipped — but the
   # printed reading stands on both sides and nothing is renumbered.
   'errata': {'10. Nandiyamigarājajātakavaṇṇanā (385)':
                  '10. Nandiyajātakavaṇṇanā (385)',
              '6. Cetiyajātakavaṇṇanā (422)':
                  '6. Cetiyajātakavaṇṇanā (442)'},
   'matika_drop': ['Jātakaṭṭhakathā', 'Tatiyabhāga', 'Uddānagāthā'],
 },
 '39KhuA20': {
   'title': 'Jātakaṭṭhakathā (Catuttho bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 6),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # SIX nipātas, numbered 10 to 15 continuing the earlier volumes' count, each
   # a flat list of jātakavaṇṇanās carrying the CANON'S OWN jātaka number in
   # parentheses (439 to …) plus its closing `Uddānagāthā`.
   'tops': ['10. Dasakanipāta', '11. Ekādasakanipāta', '12. Dvādasakanipāta',
            '13. Terasakanipāta', '14. Pakiṇṇakanipāta', '15. Vīsatinipāta'],
   'levels': [None, [r're:.']],
   # `jākata` for `jātaka` — the same class of slip the CANON Jātaka volumes
   # carry (22Khu05 p105 sets `Udapānadūsakajākaka`).  PRESERVED.
   'errata': {'2. Candakinnarījātakavaṇṇanā (485)':
                  '2. Candakinnarījākatavaṇṇanā (485)'},
   # Each nipāta closes with `Uddānagāthā`, which the builder puts in the
   # `uddana` side-map — where it belongs, because the reader draws an uddāna
   # as a centred block after the last paragraph, not as a section.  So the
   # mātikā lists six entries the TREE correctly has no node for.  Dropped
   # with the reason named rather than left to look like six missing sections.
   'matika_drop': ['Uddānagāthā'],
 },
 '40KhuA21': {
   'title': 'Jātakaṭṭhakathā (Pañcamo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 4),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': ['16. Tiṁsanipāta', '17. Cattālīsanipāta', '18. Paṇṇāsanipāta',
            '19. Saṭṭhinipāta', '20. Sattatinipāta', '21. Asītinipāta'],
   'levels': [None, [r're:.']],
   # Two of the edition's own, both preserved: the body sets
   # `Saṅkhāpāla…` for the mātikā's `Saṅkhapāla…`, and `Mahāsaṁsa…` for
   # `Mahāhaṁsa…` — the second is the jātaka of the GREAT GOOSE, so the
   # mātikā is the side that is right and the body the side that slipped.
   'errata': {'4. Saṅkhapālajātakavaṇṇanā (524)':
                  '4. Saṅkhāpālajātakavaṇṇanā (524)',
              '2. Mahāhaṁsajātakavaṇṇanā (534)':
                  '2. Mahāsaṁsajātakavaṇṇanā (534)'},
   # `Jātakaṭṭhakathā` and `Pañcamabhāga` are the MĀTIKĀ PAGE'S OWN TITLE
   # LINES, and each nipāta's closing `Uddānagāthā` goes to the `uddana`
   # side-map rather than the tree — see 39KhuA20.
   'matika_drop': ['Jātakaṭṭhakathā', 'Pañcamabhāga', 'Uddānagāthā'],
 },
 '42KhuA23': {
   'title': 'Jātakaṭṭhakathā (Sattamo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 3),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # ONE nipāta: the Mahānipāta, whose last FIVE great jātakas (543-547, the
   # Bhūridatta to the Vessantara) fill the whole volume.  41KhuA22 holds 1-5.
   'tops': ['22. Mahānipāta'],
   'levels': [None, [r're:.']],
   'matika_drop': ['Jātakaṭṭhakathā', 'Sattamabhāga', 'Uddānagāthā'],
 },
 '43KhuA24': {
   'title': 'Mahāniddesaṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 3),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # The Saddhammapajjotikā on the Mahāniddesa: `Ganthārambhakathā` and the
   # Aṭṭhakavagga's SIXTEEN suttaniddesavaṇṇanās, numbered 1..16 with no gap.
   'tops': ['Ganthārambhakathā', '1. Aṭṭhakavagga'],
   'levels': [None, [r're:.']],
   # !!! A FOOTNOTE MARKER INSIDE A HEADING.  The body sets
   # `12. Cūḷabyūha1suttaniddesavaṇṇanā` and `13. Mahābyūha2suttaniddesa-
   # vaṇṇanā` with the marker embedded in the WORD; the mātikā gives them
   # clean.  Both readings preserved, and the marker is not stripped by rule —
   # a rule that removed a digit from inside a heading would also break the
   # numbered ranges this layer is full of.
   'errata': {'12. Cūḷabyūhasuttaniddesavaṇṇanā':
                  '12. Cūḷabyūha1suttaniddesavaṇṇanā',
              '13. Mahābyūhasuttaniddesavaṇṇanā':
                  '13. Mahābyūha2suttaniddesavaṇṇanā'},
 },
 '44KhuA25': {
   'title': 'Cūḷaniddesaṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 4),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # The Pārāyanavagga's eighteen māṇavasuttaniddesas plus the
   # Khaggavisāṇasutta's four vaggas, and `Nigamanakathā`.  The
   # Khaggavisāṇasutta is entry 19 AND a group with its own children, which is
   # why it is a top rather than a leaf.
   'tops': ['Pārāyanavagga', '19. Khaggavisāṇasuttaniddesavaṇṇanā',
            'Nigamanakathā'],
   'levels': [None, [r're:.']],
   # The body heads the first vagga `Paṭhamavaggavaṇṇanā` where the mātikā
   # numbers it `1.` — and numbers 2, 3 and 4 on both sides.
   'errata': {'1. Paṭhamavaggavaṇṇanā': 'Paṭhamavaggavaṇṇanā'},
 },
 '46KhuA27': {
   'title': 'Paṭisambhidāmaggaṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 5),
   'matika_gate': True,
   'level_memo': True,
   'tops': ['Ganthārambhakathā', '1. Mahāvagga'],
   # Mahāvagga > Ñāṇakathā > the ñāṇa-niddesas (numbered 1 to 64-67 with no
   # gap) > the Sutamayañāṇa's own unnumbered sub-niddesas.
   'levels': [None, ['1. Ñāṇakathā'], [r're:\d+(?:-\d+)?\.\s+\S'], [r're:.']],
   # The body heads the first ñāṇa `1. Sutamayañāṇakathā` (p55) where the
   # mātikā lists `1. Sutamayañāṇaniddesavaṇṇanā`.  Neither corrected.
   'errata': {'1. Sutamayañāṇaniddesavaṇṇanā': '1. Sutamayañāṇakathā'},
   # `Paṭhamabhāga` is the MĀTIKĀ PAGE'S OWN TITLE LINE, not a section — it
   # sits under `Paṭisambhidāmaggaṭṭhakathā` at the head of p i and the leader
   # rule reads it as an entry.  Dropped with the reason named.
   'matika_drop': ['Paṭhamabhāga'],
 },
 '47KhuA28': {
   'title': 'Paṭisambhidāmaggaṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 6),
   'matika_gate': True,
   'level_memo': True,
   # THE TOP LEVEL IS THE PRINTED MĀTIKĀ'S OWN, and it is not uniform, because
   # this volume opens IN THE MIDDLE of a vagga: 46KhuA27 ends inside the
   # Mahāvagga's Ñāṇakathā, so the first five entries are that kathā's
   # remaining ñāṇa-niddesas (68 to 72-73, continuing its numbering), and only
   # then do the Mahāvagga's own kathās 2-10 begin.  The two later vaggas ARE
   # printed as centred heads.  Read off the page rather than normalised.
   'tops': ['68. Indriyaparopariyattañāṇaniddesavaṇṇanā',
            '69. Āsayānusayañāṇaniddesavaṇṇanā',
            '70. Yamakapāṭihīrañāṇaniddesavaṇṇanā',
            '71. Mahākaruṇāñāṇaniddesavaṇṇanā',
            '72-73. Sabbaññutaññāṇaniddesavaṇṇanā',
            '2. Diṭṭhikathā', '3. Ānāpānassatikathā', '4. Indriyakathā',
            '5. Vimokkhakathā', '6. Gatikathāvaṇṇanā', '7. Kammakathāvaṇṇanā',
            '8. Vipallāsakathāvaṇṇanā', '9. Maggakathāvaṇṇanā',
            '10. Maṇḍapeyyakathāvaṇṇanā',
            '2. Yuganaddhavagga', '3. Paññāvagga', 'Nigamanakathā'],
   'levels': [None, [KATHA], [r're:.']],
 },
}

A.SPEC.update(KHUA)
A.main()
