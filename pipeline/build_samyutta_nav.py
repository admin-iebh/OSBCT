#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a Saṁyuttanikāya volume's nav tree with the generic nav machinery.

    python3 pipeline/build_samyutta_nav.py <VOL> [--write]

Same shape as `build_digha_nav.py` / `build_majjhima_nav.py`: the builder in
`build_abhidhamma_nav.py` is generic over the piṭaka, so this file is the SPEC
and nothing else.  (The previous font-heuristic file is kept as `.prespec`.)

!!! THIS IS THE FIRST NIKĀYA WHERE ONE VOLUME CARRIES SEVERAL BOOKS, and the
first that is THREE LEVELS DEEP.  Three volumes hold FIVE books, each with its
own title page and homage, so 12Sam01 and 13Sam02 take TWO `books` entries and
TWO nav nodes apiece (`separate_books`), exactly as 31Abhi03 does.  Beneath a
book run SAṀYUTTA -> VAGGA -> SUTTA, so `levels` carries TWO rungs where the
Majjhima has one and the Dīgha none.

MEASURED, not assumed.  Saṁyutta heads per book from the written `sections/`
map: 11 + 10 (12Sam01), 13 + 10 (13Sam02), 12 (14Sam03) — each list identical
to that book's corpus `book`-field runs, which is a second independent witness.

!!! THE VAGGA RUNG IS OPTIONAL, and that is what makes ONE `levels` table serve
every saṁyutta.  Eight of 12Sam01's twenty-one saṁyuttas print no vagga at all
(Bhikkhunī, Vaṅgīsa, Vana, Yakkha, Abhisamaya, Kassapa, Opamma, Bhikkhu) and
head their suttas directly; the builder's `min(hit, len(stack))` clamp lands a
sutta declared at depth 2 at depth 1 there.  Same mechanism as 01Vin01's
sikkhāpadas.

!!! THE MĀTIKĀ IS COARSER THAN THE BODY IN TWO OF THE THREE VOLUMES, so
`matika_gate` is FALSE for 13Sam02 and 14Sam03 — the same call the Vinaya
needed.  Where the edition runs several suttas together the mātikā prints ONE
entry for the run (`4-6. Yadaniccasuttādi`, `1-2. Vihārasuttāni`,
`3-4. Parihānasuttādīni`) while the body heads each sutta separately: 426 of
13Sam02's 733 body headings and a comparable share of 14Sam03's have no mātikā
entry.  12Sam01's mātikā IS 1:1 with its body — only two errata and the
standing `Uddānagāthā` finding fail to resolve — so it keeps `matika_gate`.
**`matika_centred_gate` is TRUE on all three**: every centred mātikā line in
all five books resolves to a body heading once the errata below are applied.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_abhidhamma_nav as A

# A VAGGA rung.  The body sets these plain — `1. Naḷavagga` — even where the
# MĀTIKĀ carries a second, paṇṇāsaka-relative number in parentheses
# (`(6) 1. Upayavagga`, 13Sam02 p4); the parenthesised form is a mātikā-side
# form only and never reaches the heads stream, so the pattern does not need
# it.  `peyyāla` is in the alternation for 12Sam01's `9. Antarapeyyāla`, a
# vagga-rung head that does not end in `vagga`.
VAGGA = r're:\d+\.\s+.*(?:vagga|peyyāla)$'

# A SUTTA rung.  A RANGE is real and common here — the peyyāla sections head
# `2-7. Saṁyojanappahānādisuttachakka` for six suttas at once — and the name
# ends EITHER at `sutta` or at the NUMERAL COLLECTIVE that counts the run
# (duka, tika, catukka, pañcaka, chakka, sattaka, aṭṭhaka, navaka, dasaka,
# ekādasaka, dvādasaka, tiṁsaka, navutika).  Enumerated from the page over all
# three volumes, the same list `stems` carries in build_khu_volume.py.
SUTTA = (r're:\d+(?:-\d+)*\.\s+.*(?:sutta|suttaṁ|duka|tika|catukka|pañcaka|'
         r'chakka|sattaka|aṭṭhaka|navaka|dasaka|tiṁsaka|navutika)$')

LEVELS = [None, [VAGGA], [SUTTA]]

SAMYUTTA = {

 '12Sam01': {
   'title': 'Sagāthāvaggasaṁyuttapāḷi',
   'work': 'Saṁyutta — Sāratthappakāsinī',   # kept from the volume's own node
   'first': 0,
   # 0-based 13-38, and the "hole at 26" the scout reported is NOT one: page 26
   # is a BLANK LEAF between the Sagāthāvagga mātikā's closing
   # `…mātikā niṭṭhitā.` (p25) and the Nidānavagga mātikā's title page (p27).
   # Measured, then LOOKED AT.
   'matika': (13, 38),
   'matika_gate': True,
   'matika_centred_gate': True,
   'tops': [],
   # !!! REQUIRED, AND THE VAGGA-LESS SAṀYUTTAS ARE WHY.  `levels` declares
   # the sutta rung at depth 2, and under a saṁyutta that prints no vagga
   # the clamp `min(hit, len(stack))` lands the FIRST sutta at depth 1 and
   # then nests every following sutta inside the last, one per rung.  Without
   # the memo 12Sam01's Bhikkhunī-, Vaṅgīsa-, Vana- and Yakkhasaṁyutta each
   # showed ONE child instead of their ten suttas, with every row still
   # present and no checker firing.  Same mechanism, same fix, as 01Vin01's
   # five sub-entries printed as SIBLINGS under a pārājika.
   'level_memo': True,
   'separate_books': True,
   'books': [
     {'title': 'Sagāthāvaggasaṁyuttapāḷi', 'lo': 0, 'hi': 271,
      'tops': ['1. Devatāsaṁyutta', '2. Devaputtasaṁyutta',
               '3. Kosalasaṁyutta', '4. Mārasaṁyutta',
               '5. Bhikkhunīsaṁyutta', '6. Brahmasaṁyutta',
               '7. Brāhmaṇasaṁyutta', '8. Vaṅgīsasaṁyutta',
               '9. Vanasaṁyutta', '10. Yakkhasaṁyutta',
               '11. Sakkasaṁyutta'],
      'levels': LEVELS},
     {'title': 'Nidānavaggasaṁyuttapāḷi', 'lo': 271, 'hi': 517,
      'tops': ['1. Nidānasaṁyutta', '2. Abhisamayasaṁyutta',
               '3. Dhātusaṁyutta', '4. Anamataggasaṁyutta',
               '5. Kassapasaṁyutta', '6. Lābhasakkārasaṁyutta',
               '7. Rāhulasaṁyutta', '8. Lakkhaṇasaṁyutta',
               '9. Opammasaṁyutta', '10. Bhikkhusaṁyutta'],
      'levels': LEVELS},
   ],
   # TWO ERRATA OF THE EDITION, RECORDED NOT CORRECTED, and COUNTED ON BOTH
   # SIDES before `errata` was chosen: each form is printed exactly ONCE in the
   # mātikā and ONCE in the heads stream, and neither form appears on the other
   # side at all — which is the condition this key requires.  The tree keeps
   # what the BODY prints.
   'errata': {'2. Moḷiyaphagguṇasutta': '2. Moḷiyaphaggunasutta',
              '7. Jānussoṇisutta': '7. Jāṇussoṇisutta'},
   # The standing open finding, the same on every Dīgha and Majjhima volume and
   # on 05Vin05: the mātikā lists `Uddānagāthā`, the body heads that section
   # `Tassuddānaṁ`, `kat_is_colo` classifies it as a COLOPHON, and so no nav
   # row can exist for it.  Fifty-five printings here; one literal drops them
   # all and `matika_gate` goes on verifying the rest.
   'matika_drop': ('Uddānagāthā',),
 },

 '13Sam02': {
   'title': 'Khandhavaggasaṁyuttapāḷi',
   'work': 'Saṁyutta — Sāratthappakāsinī',
   'first': 0,
   'matika': (3, 17),
   # FALSE, and measured: 426 of this volume's 733 body headings have no mātikā
   # entry, because the mātikā prints ONE entry per RUN of suttas where the
   # body heads each one.  Its CENTRED lines are 1:1 with the body's structural
   # headings, which is the part that can be a gate.
   'matika_gate': False,
   'matika_centred_gate': True,
   'tops': [],
   # !!! REQUIRED, AND THE VAGGA-LESS SAṀYUTTAS ARE WHY.  `levels` declares
   # the sutta rung at depth 2, and under a saṁyutta that prints no vagga
   # the clamp `min(hit, len(stack))` lands the FIRST sutta at depth 1 and
   # then nests every following sutta inside the last, one per rung.  Without
   # the memo 12Sam01's Bhikkhunī-, Vaṅgīsa-, Vana- and Yakkhasaṁyutta each
   # showed ONE child instead of their ten suttas, with every row still
   # present and no checker firing.  Same mechanism, same fix, as 01Vin01's
   # five sub-entries printed as SIBLINGS under a pārājika.
   'level_memo': True,
   'separate_books': True,
   'books': [
     {'title': 'Khandhavaggasaṁyuttapāḷi', 'lo': 0, 'hi': 361,
      'tops': ['1. Khandhasaṁyutta', '2. Rādhasaṁyutta', '3. Diṭṭhisaṁyutta',
               '4. Okkantasaṁyutta', '5. Uppādasaṁyutta', '6. Kilesasaṁyutta',
               '7. Sāriputtasaṁyutta', '8. Nāgasaṁyutta', '9. Supaṇṇasaṁyutta',
               '10. Gandhabbakāyasaṁyutta', '11. Valāhakasaṁyutta',
               '12. Vacchagottasaṁyutta', '13. Jhānasaṁyutta'],
      'levels': LEVELS},
     {'title': 'Saḷāyatanavaggasaṁyuttapāḷi', 'lo': 361, 'hi': 722,
      # !!! `9. Asaṅkhatasaṁyutta` IS A TOP, and the mātikā is why it looks as
      # though it is not: the mātikā sets it `(9) Asaṅkhatasaṁyutta`, which
      # `CENTRED` cannot match because the line opens with a parenthesis.  The
      # BODY heads it plainly, so it is read off the heads stream like the
      # other nine.
      'tops': ['1. Saḷāyatanasaṁyutta', '2. Vedanāsaṁyutta',
               '3. Mātugāmasaṁyutta', '4. Jambukhādakasaṁyutta',
               '5. Sāmaṇḍakasaṁyutta', '6. Moggallānasaṁyutta',
               '7. Cittasaṁyutta', '8. Gāmaṇisaṁyutta',
               '9. Asaṅkhatasaṁyutta', '10. Abyākatasaṁyutta'],
      'levels': LEVELS},
   ],
   # FIVE ERRATA OF THE EDITION, RECORDED NOT CORRECTED.  Each is COUNTED ON
   # BOTH SIDES — printed once in the mātikā, once in the heads stream, with
   # neither form appearing on the other side — which is the condition
   # `errata` requires.  Nothing gates on them here (`matika_gate` is False);
   # they are declared so the residue is honestly only the mātikā's own
   # abbreviations.
   'errata': {'4. Upādānapārivattasutta':     '4. Upādānaparipavattasutta',
              '8. Rajaṇīyasaṇṭhitasutta':     '8. Rajanīyasaṇṭhitasutta',
              '5. Bandanasutta':              '5. Bandhanasutta',
              '1. Vesālisutta':               '1. Vesālīsutta',
              '10. Dhammakathikapucchāsutta': '10. Dhammakathikapucchasutta'},
   # !!! OPEN, AND NOT CAUSED BY THE KEYS ABOVE.  This volume's mātikā scan
   # reports **165 out of order** with NO `errata` declared at all, and 167
   # with all five — so the five add two and are not the cause.  (I first read
   # the 167 as theirs and bisected on that assumption; the baseline run
   # settled it.  Recorded because a wrong diagnosis left in a comment is worse
   # than none.)  The scan's forward pointer is moved by an entry that matches
   # far from where the scan sits, which is the 35Abhi07 shape, and the likely
   # cause is this mātikā's abbreviated run-entries falling back to
   # `try_match(..., start=0)` and matching early.  It is NOT a gate here —
   # `matika_gate` is False, the CENTRED gate is 35/35 and the colophon gate
   # 23/23 — but it is unexplained and should be understood before any volume
   # relies on the entry scan's order.  14Sam03 has the same coarse mātikā and
   # ten errata and stays at 0, so it is not simply "coarse mātikā".
 },

 '14Sam03': {
   'title': 'Mahāvaggasaṁyuttapāḷi',
   'work': 'Saṁyutta — Sāratthappakāsinī',
   'first': 0,
   'matika': (3, 17),
   # A LONG CENTRED GROUP HEAD CENTRES FURTHER LEFT, and this volume's
   # mātikā sets five lines below the 18-space default, so the
   # centred gate could not see them at all (_tika/cmin_sweep.py,
   # 2026-07-30). 12 is where the count stabilises; no dotted entry
   # leaks in — measured on every volume that declares a mātikā range.
   'centred_indent': 12,
   # FALSE for the same reason as 13Sam02: the mātikā abbreviates runs
   # (`1-2. Vihārasuttāni`, `3-4. Parihānasuttādīni`, `8-10. Paṭipannasuttādīni`)
   # where the body heads each sutta.
   'matika_gate': False,
   'matika_centred_gate': True,
   'tops': [],
   # !!! REQUIRED, AND THE VAGGA-LESS SAṀYUTTAS ARE WHY.  `levels` declares
   # the sutta rung at depth 2, and under a saṁyutta that prints no vagga
   # the clamp `min(hit, len(stack))` lands the FIRST sutta at depth 1 and
   # then nests every following sutta inside the last, one per rung.  Without
   # the memo 12Sam01's Bhikkhunī-, Vaṅgīsa-, Vana- and Yakkhasaṁyutta each
   # showed ONE child instead of their ten suttas, with every row still
   # present and no checker firing.  Same mechanism, same fix, as 01Vin01's
   # five sub-entries printed as SIBLINGS under a pārājika.
   'level_memo': True,
   'books': [
     {'title': 'Mahāvaggasaṁyuttapāḷi', 'lo': 0, 'hi': 598,
      'tops': ['1. Maggasaṁyutta', '2. Bojjhaṅgasaṁyutta',
               '3. Satipaṭṭhānasaṁyutta', '4. Indriyasaṁyutta',
               '5. Sammappadhānasaṁyutta', '6. Balasaṁyutta',
               '7. Iddhipādasaṁyutta', '8. Anuruddhasaṁyutta',
               '9. Jhānasaṁyutta', '10. Ānāpānasaṁyutta',
               '11. Sotāpattisaṁyutta', '12. Saccasaṁyutta'],
      'levels': LEVELS},
   ],
   # FOUR ERRATA OF THE EDITION, RECORDED NOT CORRECTED, all four on CENTRED
   # lines and so all four load-bearing for `matika_centred_gate`.  COUNTED ON
   # BOTH SIDES: each is printed once in the mātikā and once in the heads
   # stream, and neither form appears on the other side.
   # The fourth is a misprinted NUMBER, not a misspelt name — the mātikā (p14)
   # runs `1. Veḷudvāravagga`, `10. Rājakārāmavagga`, `3. Saraṇānivagga`, a ten
   # between a one and a three, where the body heads it `2. Rājakārāmavagga`.
   # SIX MORE, all on ordinary dotted entries and all counted the same way.
   # The last is a printed RANGE misprint, not a misspelling: the mātikā gives
   # `334-356.` where the body heads `334-345.`
   'errata': {'2. Bojjaṅgasaṁyutta':       '2. Bojjhaṅgasaṁyutta',
              '4. Indriyasuṁyutta':        '4. Indriyasaṁyutta',
              '6. Bhalakaraṇīyavagga':     '6. Balakaraṇīyavagga',
              '10. Rājakārāmavagga':       '2. Rājakārāmavagga',
              '4. Jāṇussonibrāhmaṇasutta': '4. Jāṇussoṇibrāhmaṇasutta',
              '5. Bhāhiyasutta':           '5. Bāhiyasutta',
              '3. Chandasamādisutta':      '3. Chandasamādhisutta',
              '6. Paṇasutta':              '6. Pāṇasutta',
              '6. Andakārasutta':          '6. Andhakārasutta',
              '334-356. Punabalādisutta':  '334-345. Punabalādisutta',
              # A FIFTH CENTRED ERRATUM, and it was invisible until
              # `centred_indent` came down to 12: the mātikā prints
              # `10. Cattuttha-`, the body heading AND its vagga
              # colophon both print `Catuttha-`. The mātikā form
              # occurs ONCE in the whole volume, the body form twice.
              '10. Cattuttha-āmakadhaññapeyyālavagga':
                  '10. Catuttha-āmakadhaññapeyyālavagga'},
   'matika_drop': ('Uddānagāthā',),
 },

}

A.SPEC.update(SAMYUTTA)
A.main()
