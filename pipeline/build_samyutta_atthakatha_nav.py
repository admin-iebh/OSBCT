#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Navs for the Saṁyutta-Aṭṭhakathā (Sāratthappakāsinī), 14SamA01-16SamA03.

FOUR LEVELS, and the printed mātikā states every one of them (0-based p13):

    Ganthārambhakathā          ...   ...   1     <- top, unnumbered
              1. Devatāsaṁyutta                  <- top, CENTRED
                 1. Naḷavagga                    <- depth 1, CENTRED and deeper
     1. Oghataraṇasuttavaṇṇanā ...   ...   3     <- depth 2, a dotted entry
                                                 <- depth 3, sub-kathās

So the tops are the SAṀYUTTAS, which is the same rule the layer has followed
throughout — a commentary book takes the structure of the text it comments on,
and the Saṁyutta is saṁyuttas of vaggas of suttas.  `tops` cannot mix a
literal with a `re:` pattern (`subtree` reads a pattern only when `tops` is a
list of one), and this volume opens with the unnumbered Ganthārambhakathā, so
all twelve are NAMED.

!!! THE TOP LITERALS ARE THE BODY'S SPELLING, NOT THE MĀTIKĀ'S.  The body sets
`7. Brahmaṇasaṁyutta` with a short `a` where the mātikā reads
`7. Brāhmaṇasaṁyutta`; `tops` is matched against the HEADS STREAM, so it takes
the body's reading, and `errata` joins the two sides.  Neither is corrected.
"""
import build_abhidhamma_nav as A

WORK = 'Saṁyutta — Sāratthappakāsinī + subcommentaries'

SAMYUTTA_A = {
 '14SamA01': {
   'title': 'Saṁyuttaṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (13, 24),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # FIVE ERRATA, each printed once in the body and once in the mātikā, so
   # `errata` (which rewrites the mātikā entry globally) is right and
   # `body_errata` is not.  Key = the mātikā's reading, value = the body's.
   # NEITHER SIDE IS CORRECTED; the key only joins them.
   'errata': {'6. Saddhāsuttavaṇṇanā':    '6. Saddhāsuttavaṇṇānā',
              '10. Ghaṭīkārasuttavaṇṇanā': '10. Ghatīkārasuttavaṇṇanā',
              '7. Brāhmaṇasaṁyutta':      '7. Brahmaṇasaṁyutta',
              '4. Bilaṅgikasuttavaṇṇanā': '4. Bilaṅgīkasuttavaṇṇanā',
              '2. Upaṭṭhānasuttavaṇṇanā': '2. Upaṭṭhānasuttavaṇṇānā'},
   'tops': ['Ganthārambhakathā',
            '1. Devatāsaṁyutta', '2. Devaputtasaṁyutta', '3. Kosalasaṁyutta',
            '4. Mārasaṁyutta', '5. Bhikkhunīsaṁyutta', '6. Brahmasaṁyutta',
            '7. Brahmaṇasaṁyutta', '8. Vaṅgīsasaṁyutta', '9. Vanasaṁyutta',
            '10. Yakkhasaṁyutta', '11. Sakkasaṁyutta'],
   'levels': [None, [r're:\d+\.\s+.*vagga$'],
              [r're:\d+(?:-\d+)?\.\s+.*vaṇṇanā$'], [r're:.']],
 },
 # --- 15SamA02 and 16SamA03: TWO BOOKS EACH, one nav node -------------------
 # A commentary volume contributes exactly ONE top-level node (`_navdup.js`,
 # layer-scoped), so the two books are the first TREE level and each carries
 # its own `tops`.  Their saṁyuttas are NAMED rather than patterned because the
 # edition heads some of them `N. Xsaṁyutta` and others `N. Xsaṁyuttavaṇṇanā`,
 # and `tops` cannot mix a literal with a pattern.  **Each book's list runs
 # 1..N with no gap, which is the check that none was missed.**
 '15SamA02': {
   'title': 'Saṁyuttaṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 18),
   # A LONG CENTRED GROUP HEAD CENTRES FURTHER LEFT, and this volume's
   # mātikā sets one line below the 18-space default, so the
   # centred gate could not see it at all (_tika/cmin_sweep.py,
   # 2026-07-30). 12 is where the count stabilises; no dotted entry
   # leaks in — measured on every volume that declares a mātikā range.
   'centred_indent': 12,
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # Four errata, each printed once on each side; key = mātikā, value = body.
   'errata': {'7. Jānussoṇisuttavaṇṇanā':  '7. Jāṇussoṇisuttavaṇṇanā',
              '5. Mahārukkhasuttavaṇṇanā': '5. Mahārukkhasutavaṇṇanā',
              '10. Bilārasuttavaṇṇanā':    '10. Biḷārasuttavaṇṇanā',
              '5. Upādasaṁyuttavaṇṇanā':   '5. Uppādasaṁyuttavaṇṇanā'},
   'books': [
     {'title': 'Nidānavaggasaṁyuttaṭṭhakathā', 'lo': 0, 'hi': 188,
      'tops': ['1. Nidānasaṁyutta', '2. Abhisamayasaṁyutta', '3. Dhātusaṁyutta',
               '4. Anamataggasaṁyutta', '5. Kassapasaṁyutta',
               '6. Lābhasakkārasaṁyutta', '7. Rāhulasaṁyutta',
               '8. Lakkhaṇasaṁyutta', '9. Opammasaṁyutta',
               '10. Bhikkhusaṁyutta'],
      'levels': [None, [r're:\d+\.\s+.*vagga$'],
                 [r're:\d+(?:-\d+)?\.\s+.*vaṇṇanā$'], [r're:.']]},
     {'title': 'Khandhavaggasaṁyuttaṭṭhakathā', 'lo': 188, 'hi': 300,
      'tops': ['1. Khandhasaṁyutta', '2. Rādhasaṁyutta', '3. Diṭṭhisaṁyutta',
               '4. Okkantasaṁyutta', '5. Uppādasaṁyuttavaṇṇanā',
               '6. Kilesasaṁyuttavaṇṇanā', '7. Sāriputtasaṁyutta',
               '8. Nāgasaṁyutta', '9. Supaṇṇasaṁyuttavaṇṇanā',
               '10. Gandhabbakāyasaṁyuttavaṇṇanā', '11. Valāhakasaṁyuttavaṇṇanā',
               '12. Vacchagottasaṁyuttavaṇṇanā', '13. Jhānasaṁyutta'],
      'levels': [None, [r're:\d+\.\s+.*vagga$'],
                 [r're:\d+(?:-\d+)?\.\s+.*vaṇṇanā$'], [r're:.']]},
   ],
 },
 '16SamA03': {
   'title': 'Saṁyuttaṭṭhakathā (Tatiyo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 22),
   # A LONG CENTRED GROUP HEAD CENTRES FURTHER LEFT, and this volume's
   # mātikā sets four lines below the 18-space default, so the
   # centred gate could not see them at all (_tika/cmin_sweep.py,
   # 2026-07-30). 12 is where the count stabilises; no dotted entry
   # leaks in — measured on every volume that declares a mātikā range.
   'centred_indent': 12,
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # Eight errata.  Two of them are the edition's own TYPOGRAPHY rather than a
   # spelling: the body sets `6. Dutiyakāmabhūsutta2 vaṇṇanā` and
   # `4. Mettāsahagatasutta2 vaṇṇanā` with the FOOTNOTE MARKER inside the
   # heading, which splits `suttavaṇṇanā`; `fold` keeps digits, so the two
   # sides cannot meet without being named.  And 0-based p2386 truncates
   # `5-6. Jīvakambavanasamādhisuttādivaṇṇan` — the final `ā` is simply not
   # printed.  All preserved.
   'errata': {'3. Lekantagamanasuttavaṇṇanā':        '3. Lokantagamanasuttavaṇṇanā',
              '5-6. Jivakambavanasamādhisuttādivaṇṇanā':
                  '5-6. Jīvakambavanasamādhisuttādivaṇṇan',
              '2. Devanāsaṁyutta':                   '2. Vedanāsaṁyutta',
              '6. Dutiyakāmabhūsuttavaṇṇanā':        '6. Dutiyakāmabhūsutta2 vaṇṇanā',
              '7. Vodattasuttavaṇṇanā':              '7. Godattasuttavaṇṇanā',
              '7. Dutiya-aññatrabhikkhusuttavaṇṇanā': '7. Dutiya-aññatarabhikkhusuttavaṇṇanā',
              '4. Mettāsahagatasuttavaṇṇanā':        '4. Mettāsahagatasutta2 vaṇṇanā',
              '7. Mahāpaññāvagga':                   '7. Mahāpaññavagga'},
   'books': [
     {'title': 'Saḷāyatanavaggasaṁyuttaṭṭhakathā', 'lo': 0, 'hi': 156,
      'tops': ['1. Saḷāyatanasaṁyutta', '2. Vedanāsaṁyutta',
               '3. Mātugāmasaṁyutta', '4. Jambukhādakasaṁyutta',
               '5. Sāmaṇḍakasaṁyuttavaṇṇanā', '6. Moggallānasaṁyutta',
               '7. Cittasaṁyutta', '8. Gāmaṇisaṁyutta', '9. Asaṅkhatasaṁyutta',
               '10. Abyākatasaṁyutta'],
      'levels': [None, [r're:\d+\.\s+.*vagga$'],
                 [r're:\d+(?:-\d+)?\.\s+.*vaṇṇanā$'], [r're:.']]},
     {'title': 'Mahāvaggasaṁyuttaṭṭhakathā', 'lo': 156, 'hi': 389,
      'tops': ['1. Maggasaṁyutta', '2. Bojjhaṅgasaṁyutta',
               '3. Satipaṭṭhānasaṁyutta', '4. Indriyasaṁyutta',
               '5. Sammappadhānasaṁyuttavaṇṇanā', '6. Balasaṁyuttavaṇṇanā',
               '7. Iddhipādasaṁyutta', '8. Anuruddhasaṁyutta',
               '9. Jhānasaṁyuttavaṇṇanā', '10. Ānāpānasaṁyutta',
               '11. Sotāpattisaṁyutta', '12. Saccasaṁyutta'],
      'levels': [None, [r're:\d+\.\s+.*vagga$'],
                 [r're:\d+(?:-\d+)?\.\s+.*vaṇṇanā$'], [r're:.']]},
   ],
 },
}

A.SPEC.update(SAMYUTTA_A)
A.main()
