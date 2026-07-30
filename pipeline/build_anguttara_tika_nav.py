#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the three Aṅguttara-Ṭīkā volumes.  SPEC only; the machinery is
`build_abhidhamma_nav`, and the mātikā gate is the point (2026-07-29r).

!!! THE ELEVEN NODES THIS REPLACES WERE GENERATED, NOT READ.  One per printed
book, each with a `first` and nothing under it, and every one of them keyed to
the corpora replaced today.

THE SHAPE IS THE COMMENTARY'S, AND THE PRINTED MĀTIKĀ SAYS SO — nipāta,
paṇṇāsaka, vagga, suttavaṇṇanā.  `build_anguttara_atthakatha_nav.py` reads the
same four levels off 17AnA01-19AnA03, and the eleven books here are the same
eleven nipātas:

    18AnT01  mātikā 0-based 13-16   body  17-304   Ekaka                1 book
    19AnT02  mātikā          3-16   body  17-412   Duka/Tika/Catukka    3 books
    20AnT03  mātikā          3-18   body  19-389   Pañcaka..Ekādasaka   7 books

!!! THE EKAKANIPĀTA'S TOPS DO NOT RUN 1..N WITHOUT A GAP, AND THAT IS THE
EDITION, NOT A LOSS.  17AnA01 heads all twenty of the Ekakanipāta's divisions
and the unbroken 1..20 is what proves none was dropped.  This ṭīkā is an
*anuttānatthadīpanā* — it comments only where the commentary is not plain — and
it heads SEVENTEEN of them: 9, 11 and 12 are not printed at all.  Checked
against the volume's own mātikā, which lists no entry under them either.  So
the tops are named as literals and the run is 1-8, 10, 13-20.

The three that carry inner vaggas of their own — `14. Etadaggavagga`,
`15. Aṭṭhānapāḷi`, `16. Ekadhammapāḷi` — are reprinted above EACH inner vagga,
the ancestor-reprint pattern `subtree` already skips; exactly as in 17AnA01.

!!! AND THE SATTAKANIPĀTA'S ONE PAṆṆĀSAKA HAS NO NUMBER.  20AnT03 p168 heads it
`Paṇṇāsaka`, bare, and puts all EIGHT of the nipāta's vaggas under it — where
19AnA03 gave the Sattaka vagga tops with no paṇṇāsaka at all.  Taken as printed:
one top named `Paṇṇāsaka`, eight vaggas below it.

Usage: python3 pipeline/build_anguttara_tika_nav.py <VOL> [--write]
"""
import build_abhidhamma_nav as A

WORK = 'Aṅguttara — Manorathapūraṇī + subcommentaries'
# !!! THE PAṆṆĀSAKA-RELATIVE NUMBER IS PRINTED IN PARENTHESES FROM THE SECOND
# PAṆṆĀSAKA ON.  This edition heads the sixth vagga of a nipāta
# `(6) 1. Puggalavaggavaṇṇanā` — the nipāta-wide number in brackets, then the
# number inside the paṇṇāsaka.  17AnA01-19AnA03's `\d+\.` regex never saw one,
# because the commentary's own heads carry no bracket; here it silently left
# every vagga of every paṇṇāsaka after the first out of the tree, and the
# mātikā gate is what said so.
VAGGA   = r're:\(?\d+\)?\.?\s*\d*\.?\s*.*vagga$'
VAGGAV  = r're:\(?\d+\)?\.?\s*\d*\.?\s*.*vagga(?:vaṇṇanā)?$'
VANNANA = r're:\d+(?:-\d+)?\.\s+.*vaṇṇanā$'
LEAF = [r're:.']
L_PAN = [None, [VAGGAV], [VANNANA], LEAF]     # paṇṇāsaka > vagga > vaṇṇanā
L_VAG = [None, [VANNANA], LEAF]               # vagga > vaṇṇanā
PAN5 = ['1. Paṭhamapaṇṇāsaka', '2. Dutiyapaṇṇāsaka', '3. Tatiyapaṇṇāsaka',
        '4. Catutthapaṇṇāsaka', '5. Pañcamapaṇṇāsaka']

ANGUTTARA_T = {
 # --- 18AnT01: the Ekakanipāta, one book, seventeen printed divisions ------
 # !!! SEVEN MĀTIKĀ-VS-BODY DIVERGENCES, ALL IN THE ETADAGGAVAGGA AND ONE NAME.
 # The mātikā (p xi-xiv) heads the Etadaggavagga's inner vaggas WITHOUT the
 # `vaṇṇanā` the body prints — `2. Dutiyavagga` against the body's p159
 # `2. Dutiyavaggavaṇṇanā`, and so through the seventh.  Its `1. Paṭhamavagga`
 # agrees with the body, so the edition is inconsistent with ITSELF inside one
 # list of seven.  Given on the TREE side as an alternative fold, never as a
 # global rewrite: `2. Dutiyavaggavaṇṇanā` is ALSO printed under
 # `15. Aṭṭhānapāḷi` and under `16. Ekadhammapāḷi`, where both sides agree, and
 # a global rewrite would send the forward-only matcher to the wrong one.
 # AND ONE NAME LOSES A SYLLABLE: mātikā `Siṅgālamātātherīvatthu` against the
 # body's p199 `Siṅgālakamātātherīvatthu`.  TWO further witnesses say the body
 # is right — the canon 15An01 prints `Siṅgālakamātāti` and the commentary
 # 17AnA01 prints `Siṅgālakamātā` four times.  MĀTIKĀ SLIPPED.  Recorded; the
 # mātikā keeps what it prints.
 '18AnT01': {
   'body_errata': {'2. Dutiyavaggavaṇṇanā':   '2. Dutiyavagga',
                   '3. Tatiyavaggavaṇṇanā':   '3. Tatiyavagga',
                   '4. Catutthavaggavaṇṇanā': '4. Catutthavagga',
                   '5. Pañcamavaggavaṇṇanā':  '5. Pañcamavagga',
                   '6. Chaṭṭhavaggavaṇṇanā':  '6. Chaṭṭhavagga',
                   '7. Sattamavaggavaṇṇanā':  '7. Sattamavagga',
                   'Siṅgālakamātātherīvatthu': 'Siṅgālamātātherīvatthu'},
   'title': 'Aṅguttaraṭīkā (Ekakanipāta)',
   'work': WORK,
   'first': 2,
   'matika': (13, 16),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'books': [
     {'title': 'Ekakanipāta-aṅguttaraṭīkā', 'lo': 0, 'hi': 223,
      'tops': ['Ganthārambhakathāvaṇṇanā',
               '1. Rūpādivaggavaṇṇanā', '2. Nīvaraṇappahānavaggavaṇṇanā',
               '3. Akammaniyavaggavaṇṇanā', '4. Adantavaggavaṇṇanā',
               '5. Paṇihita-acchavaggavaṇṇanā', '6. Accharāsaṅghātavaggavaṇṇanā',
               '7. Vīriyārambhādivaggavaṇṇanā', '8. Kalyāṇamittādivaggavaṇṇanā',
               '10. Dutiyapamādādivaggavaṇṇanā', '13. Ekapuggalavaggavaṇṇanā',
               '14. Etadaggavagga', '15. Aṭṭhānapāḷi', '16. Ekadhammapāḷi',
               '17. Pasādakaradhammavaggavaṇṇanā',
               '18. Apara-accharāsaṅghātavaggavaṇṇanā',
               '19. Kāyagatāsativaggavaṇṇanā', '20. Amatavaggavaṇṇanā'],
      'levels': [None, [VAGGAV], LEAF]},
   ],
 },
 # --- 19AnT02: Duka, Tika, Catukka — 3 + 3 + 5 paṇṇāsakas -----------------
 # !!! NINE MĀTIKĀ-VS-BODY DIVERGENCES, AND A THIRD WITNESS DECIDES EIGHT.
 # Each pair was read on BOTH printed pages with `_tika/matdiff.py`, then put
 # to the canon 15An01 and the commentary 18AnA02, which print these names
 # dozens of times between them.  Neither side is corrected; `body_errata`
 # only lets the gate compare the two.
 #   mātikā p6  `4. Nidānasuttavaṇṇanā`   body p117 `Nidāni-`   — canon 3x,
 #     commentary 3x, and THIS VOLUME prints `Nidānasutta` once.  BODY.
 #   mātikā p7  `6. Sāḷasuttavaṇṇanā`     body p184 `Sāḷha-`    — canon 6x,
 #     commentary 6x, this volume 8x, and the mātikā's form NOWHERE.  MĀTIKĀ.
 #   mātikā p8  `1. Chandasuttavaṇṇanā`   body p197 `Channa-`   — AN 3.72 is
 #     the wanderer CHANNA; the mātikā's form occurs nowhere.  MĀTIKĀ.
 #   mātikā p8  `8. Sīlapabbatasuttavaṇṇanā` body p200 `Sīlabbata-` — AN 3.78
 #     is *sīlabbata*, precepts-and-vows, not a mountain.  MĀTIKĀ.
 #   mātikā p14 `(12) 2. Ekasivagga`      body p342 `Kesivagga` — canon 21x,
 #     commentary 17x, this volume 6x.  KESI the horse-trainer.  MĀTIKĀ.
 #   mātikā p15 `8. Jambālīsuttavaṇṇanā`  body p369 `Jabbālī-`  — canon 3x,
 #     commentary 3x, and this volume once.  BODY.
 #   mātikā p15 `8. Upakasuttavaṇṇanā`    body p377 `Upada-`    — AN 4.188 is
 #     UPAKA Maṇḍikāputta; canon 3x, commentary 3x, this volume once.  BODY.
 #   mātikā p16 `2. Āpattibhayasuttādivaṇṇanā` body p410 `Āvatti-` — canon 29x,
 #     commentary 17x, and THIS VOLUME'S OWN BODY 11x against its one.  BODY.
 #   mātikā p13 `9. Vaṇijjasuttavaṇṇanā`  body p333 `…suttādi-` — the edition
 #     disagreeing with itself about `-ādi-`.  NO THIRD WITNESS.  RECORDED.
 '19AnT02': {
   # The mātikā's `Tikanipāta` (p5) and `Catukkanipāta` (p9) are its own book
   # dividers, printed as the two inner books' TITLE-PAGE lines — `titlestack`
   # filters them from the body and the tree expresses them as the book nodes.
   # 14MaT02's `Dutiyabhāga`, the same page furniture.  The FIRST book's
   # divider is not here: 19AnT02's opening title stack reads `Suttantapiṭaka /
   # Dukādinipāta / Aṅguttaraṭīkā`, so its `Dukanipāta` is a real body heading
   # and matches.
   'matika_drop': ('Tikanipāta', 'Catukkanipāta'),
   'body_errata': {'4. Nidānisuttavaṇṇanā':        '4. Nidānasuttavaṇṇanā',
                   '6. Sāḷhasuttavaṇṇanā':         '6. Sāḷasuttavaṇṇanā',
                   '1. Channasuttavaṇṇanā':        '1. Chandasuttavaṇṇanā',
                   '8. Sīlabbatasuttavaṇṇanā':     '8. Sīlapabbatasuttavaṇṇanā',
                   '(12) 2. Kesivagga':            '(12) 2. Ekasivagga',
                   '8. Jabbālīsuttavaṇṇanā':       '8. Jambālīsuttavaṇṇanā',
                   '8. Upadasuttavaṇṇanā':         '8. Upakasuttavaṇṇanā',
                   '2. Āvattibhayasuttādivaṇṇanā': '2. Āpattibhayasuttādivaṇṇanā',
                   '9. Vaṇijjasuttādivaṇṇanā':     '9. Vaṇijjasuttavaṇṇanā'},
   'title': 'Aṅguttaraṭīkā (Dukādinipāta)',
   'work': WORK,
   'first': 1,
   'matika': (3, 16),
   # A LONG CENTRED GROUP HEAD CENTRES FURTHER LEFT, and this volume's
   # mātikā sets three pair-lines below the 18-space default, so the
   # centred gate could not see them at all (_tika/cmin_sweep.py,
   # 2026-07-30). 12 is where the count stabilises; no dotted entry
   # leaks in — measured on every volume that declares a mātikā range.
   'centred_indent': 12,
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'books': [
     {'title': 'Dukanipāta-aṅguttaraṭīkā',   'lo': 0,   'hi': 113,
      'tops': PAN5[:3], 'levels': L_PAN},
     {'title': 'Tikanipāta-aṅguttaraṭīkā',   'lo': 113, 'hi': 226,
      'tops': PAN5[:3], 'levels': L_PAN},
     {'title': 'Catukkanipāta-aṅguttaraṭīkā', 'lo': 226, 'hi': 367,
      'tops': PAN5, 'levels': L_PAN},
   ],
 },
 # --- 20AnT03: Pañcaka to Ekādasaka, seven books --------------------------
 # !!! SEVEN MORE MĀTIKĀ-VS-BODY DIVERGENCES, five of them settled by the
 # canon 16An02/17An03 and the commentary 19AnA03.
 #   mātikā p7  `5. Pattanāsuttādivaṇṇanā`   body p65  `Patthanā-` — commentary
 #     3x `Patthanāsutta`, this volume 2x `Patthanā`, the mātikā's form
 #     nowhere.  MĀTIKĀ.
 #   mātikā p11 `2. Āravaraṇasuttādivaṇṇanā` body p165 `Āvaraṇa-`  — canon 6x,
 #     commentary 8x.  MĀTIKĀ.
 #   mātikā p15 `(8) 2. Yamakavagga`         body p283 `(8) 3.`    — the
 #     Aṭṭhakanipāta's Yamakavagga is `(8) 3.` in BOTH the canon and the
 #     commentary; `(7) 2.` is the DASAKANIPĀTA's, and the mātikā has crossed
 #     the two.  MĀTIKĀ.
 #   mātikā p16 `1. Tiṭṭhānasuttavaṇṇanā`    body p308 `Tiṭhāna-`  — canon 3x,
 #     commentary 3x, this volume 4x.  *Ti-ṭhāna*, three grounds.  MĀTIKĀ.
 #   mātikā p19 `1. Nissaggiyavagga`         body p376 `Nissaya-`  — canon 21x,
 #     commentary 9x, this volume 4x.  MĀTIKĀ.
 #   mātikā p6  `5. Paṭhamayodhājīvasuttādivaṇṇanā` body p48 without `-ādi-`,
 #     and mātikā p16 `4. Gāvī-upamāsuttavaṇṇanā` body p316 without the hyphen
 #     — the edition disagreeing with itself, and on the hyphen BOTH the canon
 #     and the commentary print BOTH forms.  NO THIRD WITNESS.  RECORDED.
 '20AnT03': {
   # Six book dividers, the same page furniture as 19AnT02's two: each inner
   # nipāta's title-page line, filtered from the body by `titlestack` and
   # expressed in the tree as the book node.  `Pañcakanipāta`, the first, is a
   # real body heading and matches.
   'matika_drop': ('Chakkanipāta', 'Sattakanipāta', 'Aṭṭhakanipāta',
                   'Navakanipāta', 'Dasakanipāta', 'Ekādasakanipāta'),
   'body_errata': {'5. Patthanāsuttādivaṇṇanā':  '5. Pattanāsuttādivaṇṇanā',
                   '2. Āvaraṇasuttādivaṇṇanā':   '2. Āravaraṇasuttādivaṇṇanā',
                   '(8) 3. Yamakavagga':         '(8) 2. Yamakavagga',
                   '1. Tiṭhānasuttavaṇṇanā':     '1. Tiṭṭhānasuttavaṇṇanā',
                   '1. Nissayavagga':            '1. Nissaggiyavagga',
                   '5. Paṭhamayodhājīvasuttavaṇṇanā':
                       '5. Paṭhamayodhājīvasuttādivaṇṇanā',
                   '4. Gāvīupamāsuttavaṇṇanā':   '4. Gāvī-upamāsuttavaṇṇanā'},
   'title': 'Aṅguttaraṭīkā (Pañcakādinipāta)',
   'work': WORK,
   'first': 1,
   'matika': (3, 18),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'books': [
     {'title': 'Pañcakanipāta-aṅguttaraṭīkā',    'lo': 0,   'hi': 128,
      'tops': PAN5, 'levels': L_PAN},
     {'title': 'Chakkanipāta-aṅguttaraṭīkā',     'lo': 128, 'hi': 189,
      'tops': PAN5[:2], 'levels': L_PAN},
     {'title': 'Sattakanipāta-aṅguttaraṭīkā',    'lo': 189, 'hi': 227,
      'tops': ['Paṇṇāsaka'], 'levels': L_PAN},
     {'title': 'Aṭṭhakanipāta-aṅguttaraṭīkā',    'lo': 227, 'hi': 261,
      'tops': PAN5[:2], 'levels': L_PAN},
     {'title': 'Navakanipāta-aṅguttaraṭīkā',     'lo': 261, 'hi': 290,
      'tops': PAN5[:1], 'levels': L_PAN},
     {'title': 'Dasakanipāta-aṅguttaraṭīkā',     'lo': 290, 'hi': 338,
      'tops': PAN5[:4], 'levels': L_PAN},
     {'title': 'Ekādasakanipāta-aṅguttaraṭīkā',  'lo': 338, 'hi': 345,
      'tops': ['1. Nissayavagga', '2. Anussativagga'], 'levels': L_VAG},
   ],
 },
}

A.SPEC.update(ANGUTTARA_T)
A.main()
