#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for 05Kankha — the one volume in the layer that holds BOTH canonical
Pāḷi and its commentary.

Printed p20 opens `Dvemātikāpāḷi`, the two pātimokkhas, each with its own homage
title page and 46% of the printed body between them; printed p102 opens
`Kaṅkhāvitaraṇī-aṭṭhakathā`, which is what the cover titles the whole volume.
The Dvemātikāpāḷi appears NOWHERE in the 40 canon volumes.  Settled 2026-07-28d:
the volume stays in the `commentary` layer, which is what it is as published,
and the nav NAMES the two halves so the provenance is visible.

The volume's `title` is the only string here that is not the edition's own — it
joins the two printed titles with `+`.  Everything else, book titles included,
is read off the page.

STRUCTURE, from the printed mātikā (0-based idx 3-18) and confirmed against the
heads stream:

    Bhikkhupātimokkhapāḷi        ¶   0- 251   NINE uddesas, flat
    Bhikkhunīpātimokkhapāḷi      ¶ 251- 591   the same EIGHT, without Aniyatuddesa
    Kaṅkhāvitaraṇī-aṭṭhakathā    ¶ 591- 799   kaṇḍa > vagga > sikkhāpadavaṇṇanā
    Bhikkhunīpātimokkhavaṇṇanā   ¶ 799- 930   the same, and the Pārājikakaṇḍa
                                              divides Sādhāraṇa / Asādhāraṇa

`matika_centred_gate` is OFF, and deliberately: this volume's front matter has
TWO running headers that alternate page by page (`Kaṅkhāvitaraṇī-aṭṭhakathā`
and the section's own name), and `A.matika` strips only one, so the centred-head
list would carry the other as an entry.  Flagged rather than worked around.
"""
import build_abhidhamma_nav as A

WORK = 'Vinaya — Samantapāsādikā + subcommentaries'
VAGGA = r're:\d+(?:-\d+)?\.\s+\S*vagga$'

# The nine uddesas of the Bhikkhupātimokkha, AS THE BODY PRINTS THEM — the
# edition sets `Nissaggiya pācittiya` and `Suddha pācittiya` with a space where
# its own mātikā closes them up, and `Paṭidesanīya` without the first `ā`.
UDD1 = ['Nidānuddesa', 'Pārājikuddesa', 'Saṁghādisesuddesa', 'Aniyatuddesa',
        'Nissaggiya pācittiya', 'Suddha pācittiya', 'Paṭidesanīya', 'Sekhiya',
        'Adhikaraṇasamatha']
UDD2 = ['Nidānuddesa', 'Pārājikuddesa', 'Saṁghādisesuddesa',
        'Nissaggiya pācittiya', 'Suddha pācittiya', 'Pāṭidesanīya', 'Sekhiya',
        'Adhikaraṇasamatha']

KANKHA = {
 '05Kankha': {
   'title': 'Dvemātikāpāḷi + Kaṅkhāvitaraṇī-aṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 18),
   'matika_gate': True,
   'level_memo': True,
   'tops': [],
   'books': [
     {'title': 'Bhikkhupātimokkhapāḷi', 'lo': 0, 'hi': 251,
      'tops': ['Dvemātikāpāḷi'] + UDD1, 'levels': [None]},
     {'title': 'Bhikkhunīpātimokkhapāḷi', 'lo': 251, 'hi': 591,
      'tops': UDD2, 'levels': [None]},
     {'title': 'Kaṅkhāvitaraṇī-aṭṭhakathā', 'lo': 591, 'hi': 799,
      'tops': ['Ganthārambhakathā', 'Nidānavaṇṇanā', 'Pārājikakaṇḍa',
               'Saṁghādisesakaṇḍa', 'Aniyatakaṇḍa', 'Nissaggiyakaṇḍa',
               'Pācittiyakaṇḍa', 'Pāṭidesanīyakaṇḍa', 'Sekhiyakaṇḍa'],
      'levels': [None, [VAGGA], [r're:.']]},
     {'title': 'Bhikkhunīpātimokkhavaṇṇanā', 'lo': 799, 'hi': 930,
      'tops': ['Pārājikakaṇḍa', 'Saṁghādisesakaṇḍa', 'Nissaggiyakaṇḍa',
               'Pācittiyakaṇḍa', 'Pāṭidesanīyakaṇḍa', 'Nigamanakathā'],
      # the Pārājikakaṇḍa divides by whether a sikkhāpada is shared with the
      # bhikkhus, which the mātikā centres and the body prints as two heads
      'levels': [None, ['Sādhāraṇapārājika', 'Asādhāraṇapārājika', VAGGA],
                 [r're:.']]},
   ],
   # THE EDITION'S OWN, both readings preserved.  The first four are the body
   # dropping an `h` or moving a number; the fifth is the body writing the
   # peyyāla `-pa-` into a heading where the mātikā gives the range.
   'errata': {'7. Dhammadesanāsikkhāpadavaṇṇanā':
                  '7. Dhammadesanāsikkāpadavaṇṇanā',
              '3. Vikālagāmappavesanasikkhāpadavaṇṇanā':
                  '3. Vikālagāmappavesanasikkāpadavaṇṇanā',
              '1. Āvasathasikkhāpadavaṇṇanā':
                  '2. Āvasathasikkhāpadavaṇṇanā',
              '1. Lasuṇasikkhāpadavaṇṇanā':
                  '2. Lasuṇasikkhāpadavaṇṇanā',
              '1-4. Methunasikkhāpadavaṇṇanā':
                  '1 -pa- 4. Methunadhammasikkhāpadavaṇṇanā',
              # a RANGE written two ways by the same edition: the mātikā gives
              # the pair, the body (p371) numbers all three
              '8-10. Sikkhamāna-ummaddāpanādisikkhāpadavaṇṇanā':
                  '8-9-10. Sikkhamāna-ummaddāpanādisikkhāpadavaṇṇanā',
             },
   # !!! `body_errata`, NOT `errata`.  The mātikā sets `Pāṭidesanīya` in BOTH
   # pātimokkhas and the body sets `Paṭidesanīya` in the first and
   # `Pāṭidesanīya` in the second.  `errata` rewrites a mātikā reading globally
   # and would collapse both entries onto the first body heading, stranding the
   # second.  Same distinction 48AbhiA01, 49AbhiA02 and 35Abhi07 taught.
   'body_errata': {'Paṭidesanīya': 'Pāṭidesanīya'},
 },
}

A.SPEC.update(KANKHA)
A.main()
