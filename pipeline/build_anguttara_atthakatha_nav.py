#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Navs for the Aṅguttara-Aṭṭhakathā (Manorathapūraṇī), 17AnA01-19AnA03.

ELEVEN BOOKS ACROSS THREE VOLUMES — 1 + 3 + 7, which is the Aṅguttara's eleven
nipātas and so the check that none was missed.  Each volume contributes exactly
ONE top-level node (`_navdup.js`, layer-scoped) and its nipātas are the first
TREE level, via the `books` list with per-book `tops`.

THE TOP LEVEL IS NOT THE SAME SHAPE IN EVERY BOOK, and the printed mātikā says
which it is:

  * most nipātas are divided into PAṆṆĀSAKAS and the paṇṇāsakas are the tops;
  * the Sattaka and Ekādasaka nipātas have none and go straight to VAGGAS;
  * the Ekakanipāta has neither — twenty divisions, of which three
    (`14. Etadaggavagga`, `15. Aṭṭhānapāḷi`, `16. Ekadhammapāḷi`) carry inner
    vaggas of their own and the rest carry suttavaṇṇanās directly.

**In every book the tops run 1..N with no gap**, which is what proves none was
dropped.  The Ekakanipāta's list is the one that had to be read off the mātikā:
its heads stream reprints `14. Etadaggavagga`, `15. Aṭṭhānapāḷi` and
`16. Ekadhammapāḷi` above EACH of their inner vaggas (the ancestor-reprint
pattern `subtree` already skips), so taking the stream's distinct vagga-shaped
heads in order put `14. Etadaggavagga` first and lost 15 and 16 entirely.
"""
import build_abhidhamma_nav as A

WORK = 'Aṅguttara — Manorathapūraṇī + subcommentaries'
VAGGA   = r're:\d+\.\s+.*vagga$'
VAGGAV  = r're:\d+\.\s+.*vagga(?:vaṇṇanā)?$'
VANNANA = r're:\d+(?:-\d+)?\.\s+.*vaṇṇanā$'
L_PAN = [None, [VAGGA], [VANNANA], [r're:.']]     # paṇṇāsaka > vagga > vaṇṇanā
L_VAG = [None, [VANNANA], [r're:.']]              # vagga > vaṇṇanā
PAN5 = ['1. Paṭhamapaṇṇāsaka', '2. Dutiyapaṇṇāsaka', '3. Tatiyapaṇṇāsaka',
        '4. Catutthapaṇṇāsaka', '5. Pañcamapaṇṇāsaka']

ANGUTTARA_A = {
 '17AnA01': {
   'title': 'Aṅguttaraṭṭhakathā (Ekakanipāta)',
   'work': WORK,
   'first': 0,
   'matika': (13, 16),
   # A LONG CENTRED GROUP HEAD CENTRES FURTHER LEFT, and this volume's
   # mātikā sets one line below the 18-space default, so the
   # centred gate could not see it at all (_tika/cmin_sweep.py,
   # 2026-07-30). 12 is where the count stabilises; no dotted entry
   # leaks in — measured on every volume that declares a mātikā range.
   'centred_indent': 12,
   # ...AND THAT LINE IS THE MĀTIKĀ'S OWN TITLE, not a section: the volume
   # prints `Ekakanipāta Aṅguttaraṭṭhakathā` once in the whole file, over
   # the mātikā itself. Dropped, not added to the tree.
   'matika_drop': ('Ekakanipāta Aṅguttaraṭṭhakathā',),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'errata': {'Sāgatattheravatthu': '8. Sāgatattheravatthu'},
   'books': [
     {'title': 'Ekanipātaṭṭhakathā', 'lo': 0, 'hi': 229,
      'tops': ['Ganthārambhakathā',
               '1. Rūpādivaggavaṇṇanā', '2. Nīvaraṇappahānavaggavaṇṇanā',
               '3. Akammaniyavaggavaṇṇanā', '4. Adantavaggavaṇṇanā',
               '5. Paṇihita-acchavaggavaṇṇanā', '6. Accharāsaṅghātavaggavaṇṇanā',
               '7. Vīriyārambhādivaggavaṇṇanā', '8. Kalyāṇamittatādivaggavaṇṇanā',
               '9. Pamādādivaggavaṇṇanā', '10. Dutiyapamādādivaggavaṇṇanā',
               '11. Adhammavaggavaṇṇanā', '12. Anāpattivaggavaṇṇanā',
               '13. Ekapuggalavaggavaṇṇanā', '14. Etadaggavagga',
               '15. Aṭṭhānapāḷi', '16. Ekadhammapāḷi',
               '17. Pasādakaradhammavaggavaṇṇanā',
               '18. Apara-accharāsaṅghātavaggavaṇṇanā',
               '19. Kāyagatāsativaggavaṇṇanā', '20. Amatavaggavaṇṇanā'],
      'levels': [None, [VAGGAV], [r're:.']]},
   ],
 },
 '18AnA02': {
   'title': 'Aṅguttaraṭṭhakathā (Dukādinipāta)',
   'work': WORK,
   'first': 0,
   'matika': (3, 18),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'errata': {'4-9. Sikkhāpadādisuttavaṇṇanā': '4-9. Sikkhāpadasuttādivaṇṇanā'},
   'books': [
     {'title': 'Dukanipātaṭṭhakathā', 'lo': 0, 'hi': 140,
      'tops': PAN5[:3], 'levels': L_PAN},
     {'title': 'Tikanipātaṭṭhakathā', 'lo': 140, 'hi': 277,
      'tops': PAN5[:3], 'levels': L_PAN},
     {'title': 'Catukkanipātaṭṭhakathā', 'lo': 277, 'hi': 465,
      'tops': PAN5, 'levels': L_PAN},
   ],
 },
 '19AnA03': {
   'title': 'Aṅguttaraṭṭhakathā (Pañcakādinipāta)',
   'work': WORK,
   'first': 0,
   'matika': (3, 26),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # Four errata, each printed once on each side; key = mātikā, value = body.
   'errata': {'10. Mahānāmasuttavaṇṇanā':              '10. Māhānāmasuttavaṇṇanā',
              '1-2. Sattaviññāṇaṭṭhitisuttādivaṇṇanā': '1-2. Sattaviññāṇatṭhitisuttādivaṇṇanā',
              '3-4. Sayojanasuttādivaṇṇanā':           '3-4. Saṁyojanasuttādivaṇṇanā',
              '1. Samaṇasaññāsuttavaṇṇā':              '1. Samaṇasaññāsuttavaṇṇanā'},
   'books': [
     {'title': 'Pañcakanipātaṭṭhakathā', 'lo': 0, 'hi': 176,
      'tops': PAN5, 'levels': L_PAN},
     {'title': 'Chakkanipātaṭṭhakathā', 'lo': 176, 'hi': 259,
      'tops': PAN5[:2], 'levels': L_PAN},
     {'title': 'Sattakanipātaṭṭhakathā', 'lo': 259, 'hi': 309,
      'tops': ['1. Dhanavagga', '2. Anusayavagga', '3. Vajjisattakavagga',
               '4. Devatāvagga', '5. Mahāyaññavagga', '6. Abyākatavagga',
               '7. Mahāvagga', '8. Vinayavagga'],
      'levels': L_VAG},
     {'title': 'Aṭṭhakanipātaṭṭhakathā', 'lo': 309, 'hi': 377,
      'tops': PAN5[:2], 'levels': L_PAN},
     {'title': 'Navakanipātaṭṭhakathā', 'lo': 377, 'hi': 417,
      'tops': PAN5[:1], 'levels': L_PAN},
     {'title': 'Dasakanipātaṭṭhakathā', 'lo': 417, 'hi': 507,
      'tops': PAN5[:4], 'levels': L_PAN},
     {'title': 'Ekādasakanipātaṭṭhakathā', 'lo': 507, 'hi': 517,
      'tops': ['1. Nissayavagga', '2. Anussativagga'], 'levels': L_VAG},
   ],
 },
}

A.SPEC.update(ANGUTTARA_A)
A.main()
