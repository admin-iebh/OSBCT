#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an Aṅguttaranikāya volume's nav tree with the generic nav machinery.

    python3 pipeline/build_anguttara_nav.py <VOL> [--write]

Same shape as `build_digha_nav.py` / `build_majjhima_nav.py` /
`build_samyutta_nav.py`: the builder in `build_abhidhamma_nav.py` is generic
over the piṭaka, so this file is the SPEC and nothing else.  (The previous
font-heuristic file is kept as `.prespec`.)

ELEVEN NIPĀTAS OVER THREE VOLUMES — four, three and four books, each its own
nav node (`separate_books`).  Beneath a nipāta run PAṆṆĀSAKA -> VAGGA -> SUTTA.

!!! THE PAṆṆĀSAKA RUNG IS OPTIONAL AND TWO BOOKS DO WITHOUT IT ENTIRELY.
Measured from the written `sections/` maps, not assumed: the EKAKANIPĀTA has
NO paṇṇāsaka and no numbered suttas at all — twenty top-level sections and
thirty-eight vaggas — and the EKĀDASAKANIPĀTA has three vaggas with its
suttas directly beneath.  Both take their own `tops`/`levels`.

!!! AND THE EKAKANIPĀTA IS A PAIR-LINE BOOK, the 01Vin01 shape.  The edition
sets "14. Etadaggavagga   1. Paṭhamavagga" on ONE printed line, and the heads
stream already delivers the two at the SAME ordinal with the OUTER one FIRST,
so no `pairsides` is needed: every later repeat of `14. Etadaggavagga`,
`15. Aṭṭhānapāḷi` and `16. Ekadhammapāḷi` is an ANCESTOR REPRINT that
`subtree` skips.  Declaring the inner `N. Paṭhamavagga` rung is what makes the
seventeen repeats collapse into three nodes instead of seventeen rows.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_abhidhamma_nav as A

# A VAGGA rung.  The body sets these plain even where the MĀTIKĀ carries a
# second, paṇṇāsaka-relative number in parentheses ("(6) 1. Nīvaraṇavagga").
# `peyyāla`/`peyyālo` is in the alternation for the Rāgapeyyāla and its kin,
# which are vagga-rung heads that do not end in `vagga`.
VAGGA = r're:\d+\.\s+.*(?:vagga|vaggo|peyyāla|peyyālo)$'

# A SUTTA rung.  A RANGE is real and very common in this nikāya, and the name
# ends EITHER at `sutta` or at the numeral collective / `-ādi` / `-dvaya` form
# the edition uses when it runs several suttas together.
SUTTA = (r're:\d+(?:-\d+)*\.\s+.*(?:sutta|suttaṁ|suttā|suttādi|suttāni|'
         r'suttadvaya|suttadvayaṁ|dvaya|duka|tika|catukka|pañcaka|chakka|'
         r'sattaka|aṭṭhaka|navaka|dasaka|tiṁsaka|navutika|satika)$')

PANNA = r're:(?:\d+\.\s+)?\S*[Pp]aṇṇāsak[aā]$'

L3 = [None, [VAGGA], [SUTTA]]      # paṇṇāsaka / vagga / sutta
L2 = [None, [SUTTA]]               # vagga / sutta   (no paṇṇāsaka)
LV = [None, [VAGGA]]               # Ekakanipāta: outer section / vagga

# The Ekakanipāta's twenty top-level sections, in printed order.
EKAKA_TOPS = ['1. Rūpādivagga', '2. Nīvaraṇappahānavagga', '3. Akammaniyavagga',
              '4. Adantavagga', '5. Paṇihita-acchavagga',
              '6. Accharāsaṅghātavagga', '7. Vīriyārambhādivagga',
              '8. Kalyāṇamittādivagga', '9. Pamādādivagga',
              '10. Dutiyapamādādivagga', '11. Adhammavagga',
              '12. Anāpattivagga', '13. Ekapuggalavagga', '14. Etadaggavagga',
              '15. Aṭṭhānapāḷi', '16. Ekadhammapāḷi',
              '17. Pasādakaradhammavagga', '18. Apara-accharāsaṅghātavagga',
              '19. Kāyagatāsativagga', '20. Amatavagga']

P5 = ['1. Paṭhamapaṇṇāsaka', '2. Dutiyapaṇṇāsaka', '3. Tatiyapaṇṇāsaka',
      '4. Catutthapaṇṇāsaka', '5. Pañcamapaṇṇāsaka']

ANGUTTARA = {

 '15An01': {
   'title': 'Ekakanipātapāḷi',
   'work': 'Aṅguttara — Manorathapūraṇī',
   'first': 0,
   'matika': (13, 31),
   # FALSE: this mātikā abbreviates runs of suttas the body heads one by one.
   'matika_gate': False,
   'matika_centred_gate': True,
   'tops': [],
   'level_memo': True,
   'separate_books': True,
   'books': [
     {'title': 'Ekakanipātapāḷi',   'lo': 0,   'hi': 323,
      'tops': EKAKA_TOPS, 'levels': LV},
     {'title': 'Dukanipātapāḷi',    'lo': 323, 'hi': 518,
      'tops': P5[:3], 'levels': L3},
     {'title': 'Tikanipātapāḷi',    'lo': 518, 'hi': 677,
      'tops': P5[:3], 'levels': L3},
     {'title': 'Catukkanipātapāḷi', 'lo': 677, 'hi': 952,
      'tops': P5, 'levels': L3},
   ],
 },

 '16An02': {
   'title': 'Pañcakanipātapāḷi',
   'work': 'Aṅguttara — Manorathapūraṇī',
   'first': 0,
   'matika': (3, 17),
   'matika_gate': False,
   'matika_centred_gate': True,
   'tops': [],
   'level_memo': True,
   'separate_books': True,
   'books': [
     {'title': 'Pañcakanipātapāḷi', 'lo': 0,   'hi': 271,
      'tops': P5, 'levels': L3},
     {'title': 'Chakkanipātapāḷi',  'lo': 271, 'hi': 396,
      'tops': P5[:2], 'levels': L3},
     # !!! THE SATTAKANIPĀTA'S SINGLE PAṆṆĀSAKA IS PRINTED WITHOUT AN ORDINAL —
     # its title page sets a bare `Paṇṇāsaka` where every other book numbers it.
     # Read off the page, not normalised.
     {'title': 'Sattakanipātapāḷi', 'lo': 396, 'hi': 497,
      'tops': ['Paṇṇāsaka'], 'levels': L3},
   ],
 },

 '17An03': {
   'title': 'Aṭṭhakanipātapāḷi',
   'work': 'Aṅguttara — Manorathapūraṇī',
   'first': 0,
   'matika': (3, 22),
   'matika_gate': False,
   'matika_centred_gate': True,
   'tops': [],
   'level_memo': True,
   'separate_books': True,
   'books': [
     {'title': 'Aṭṭhakanipātapāḷi',    'lo': 0,   'hi': 96,
      'tops': P5[:2], 'levels': L3},
     {'title': 'Navakanipātapāḷi',     'lo': 96,  'hi': 178,
      'tops': P5[:2], 'levels': L3},
     {'title': 'Dasakanipātapāḷi',     'lo': 178, 'hi': 391,
      'tops': P5[:4], 'levels': L3},
     # NO PAṆṆĀSAKA AT ALL — its title page goes straight to `1. Nissayavagga`.
     {'title': 'Ekādasakanipātapāḷi', 'lo': 391, 'hi': 426,
      'tops': ['1. Nissayavagga', '2. Anussativagga', '3. Sāmaññavagga'],
      'levels': L2},
   ],
 },

}

A.SPEC.update(ANGUTTARA)
A.main()
