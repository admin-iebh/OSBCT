#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the two Saṁyutta-Ṭīkā volumes.  SPEC only; the machinery is
`build_abhidhamma_nav`, and the mātikā gate is the point (2026-07-29r).

THE SHAPE IS THE CANON SAṀYUTTA'S, THREE LEVELS DEEP: the tops are the
SAṀYUTTAS, the vaggas sit under them and the suttas under those.  The Dīgha's
tops are its suttas and the Majjhima's its vaggas; a nikāya's tree follows the
nikāya, not the layer.

    16SaT01  mātikā 0-based 13-24   body  26-370   11 saṁyuttas (Sagāthāvagga)
    17SaT02  mātikā          3-35   body  37-587   35 saṁyuttas in FOUR books

17SaT02 carries FOUR of the five vaggas, each with its own homage title page —
pp37 / 237 / 317 / 429, with p316 and p428 the blank versos before the third and
fourth.  Its ONE mātikā covers all four in the bodies' own order, so a single
range serves, as 15MaT03's two did.

!!! THE BOOK TITLE IS THE RUNNING HEADER'S FORM.  Each title page sets
`Suttantapiṭaka / <Vagga> / Saṁyuttaṭīkā`, whose last line is the same on all
four; the running header prints `Nidānavaggasaṁyuttaṭīkā`, which is distinct and
is the form 15SamA02 and 16SamA03 already use for the commentary.

Usage: python3 pipeline/build_samyutta_tika_nav.py <VOL> [--write]
"""
import build_abhidhamma_nav as A

WORK = 'Saṁyutta — Sāratthappakāsinī'
SAM = r're:\d+\.\s+\S*saṁyutta$'
VAGGA = [r're:\(?\d+(-\d+)?\)?\.?\s*\d*[-\d]*\.?\s*\S*vagga(ādi)?$', r're:\S*vagga$']
LEAF = [r're:.']

SAT = {
 # --- 16SaT01: the Sagāthāvagga, eleven saṁyuttas -------------------------
 # It opens with the Ganthārambha, which becomes the leading top as 08DiT01's
 # and 13MaT01's do.
 # EIGHT MĀTIKĀ-VS-BODY DIVERGENCES, every one read on both pages, and in six
 # of them a THIRD witness decides.  Neither side is corrected; `body_errata`
 # only lets the gate compare the two.
 #   mātikā p14 `4. Khattayasuttavaṇṇanā`   body p103 `Khattiya-` AND the body's
 #     own colophon `Khattiyasuttavaṇṇanā niṭṭhitā.`  MĀTIKĀ SLIPPED.
 #   mātikā p18 `7-8. Nandanasutta…`        body p184 `Nandasutta…` AND its
 #     colophon.  SN 2.7 is the devaputta NANDA.  MĀTIKĀ SLIPPED.
 #   mātikā p23 `8. Vaṅgisasaṁyutta`        body p307 `Vaṅgīsa-`.  MĀTIKĀ.
 #   mātikā p18 `4. Ghaṭīkārasuttavaṇṇanā`  body p182 `Ghāṭīkāra-` AND the
 #     body's own colophon reads `Ghaṭīkāra-`.  BODY SLIPPED.
 #   mātikā p21 `9. Selāsuttavaṇṇanā`       body p252 `Selābhutta-` AND its
 #     colophon reads `Selāsutta-`.  BODY SLIPPED.
 #   mātikā p21 `1. Brahmāyācanasuttavaṇṇanā`  body p254 `2.` — and THREE
 #     witnesses say 1: this mātikā, the canon 12Sam01 (`1. Brahmāyācanasutta`)
 #     and the commentary 14SamA01 (`1. Brahmāyācanasuttavaṇṇanā`).  BODY.
 #   mātikā p18 `2. Anāthapiṇḍikasutta`     body p175 `2. Anāthapiṇḍhikavagga` —
 #     ONE ERROR ON EACH SIDE.  It is a VAGGA head, so the body is right there
 #     and the mātikā's `sutta` is wrong; and the body's `-piṇḍhika-` is wrong,
 #     which the body's own p180 `Anāthapiṇḍikasuttavaṇṇanā` shows.  NOT SETTLED
 #     as one reading — both errors are recorded.
 #   body p303 `7. Vanakammikasuttavaṇṇanā3` — !!! THE HEADING CARRIES A PRINTED
 #     FOOTNOTE MARKER, and so does its colophon (`…vaṇṇanā1 niṭṭhitā.`).
 #     15MaT03 p380's class; the marker is part of the printed line.
 '16SaT01': {
   'body_errata': {
     '4. Khattiyasuttavaṇṇanā':                '4. Khattayasuttavaṇṇanā',
     '7-8. Nandasuttanandivisālasuttavaṇṇanā': '7-8. Nandanasuttanandivisālasuttavaṇṇanā',
     '8. Vaṅgīsasaṁyutta':                     '8. Vaṅgisasaṁyutta',
     '4. Ghāṭīkārasuttavaṇṇanā':               '4. Ghaṭīkārasuttavaṇṇanā',
     '9. Selābhuttavaṇṇanā':                   '9. Selāsuttavaṇṇanā',
     '2. Brahmāyācanasuttavaṇṇanā':            '1. Brahmāyācanasuttavaṇṇanā',
     '2. Anāthapiṇḍhikavagga':                 '2. Anāthapiṇḍikasutta',
     '7. Vanakammikasuttavaṇṇanā3':            '7. Vanakammikasuttavaṇṇanā',
     # body p219 `3. Titiyavagga` against the mātikā AND the body's own p240
     # and p367, all three `3. Tatiyavagga`.  BODY SLIPPED.
     '3. Titiyavagga':                         '3. Tatiyavagga'},
   'title': 'Sagāthāvaggasaṁyuttaṭīkā',
   'work': WORK,
   'first': 1,
   'matika': (13, 24),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'tops': [SAM],
   'levels': [None, VAGGA, LEAF],
 },
 # --- 17SaT02: FOUR books, thirty-five saṁyuttas --------------------------
 # FOURTEEN MORE MĀTIKĀ-VS-BODY DIVERGENCES, each read on both printed pages
 # with `_tika/matdiff.py`.  Same treatment throughout: `body_errata` gives the
 # gate the mātikā's form, the body keeps what it prints, neither is corrected.
 # Where the word itself decides, it is named:
 #   mātikā `5. Samādisuttavaṇṇanā`      body `Samādhi-`  — *samādhi*.  MĀTIKĀ.
 #   mātikā `3. Upāyivagga`              body `Udāyi-`    — the elder UDĀYĪ.
 #   mātikā `1. Sabbasuttavaṇṇanā`       body `Sabbasuta-` — a lost `t`.  BODY.
 #   mātikā `1. Caṇḍasuttavaṇṇanā`       body `Caṇḍha-`   — an intrusive `h`.
 #   mātikā `1. Santuṭṭhasuttavaṇṇanā`   body `…vaṇṇana`  — a lost final ā.
 # The rest are the edition disagreeing with itself about `-ādi-`, `-vaṇṇanā`
 # and one hyphen, and no third witness settles them; they are RECORDED.
 '17SaT02': {
   # !!! ONE MĀTIKĀ ENTRY IS PRESENT ON BOTH SIDES AND STILL WILL NOT MATCH IN
   # ORDER.  `(6) 1. Avijjāvaggavaṇṇanā` is printed in the mātikā (p19) and in
   # the body (p327), verbatim — but this volume prints an `Avijjāvagga` THREE
   # times, in three different saṁyuttas (pp296, 327, 429), and the ordered
   # matcher consumed the wrong occurrence.  Dropped from the MĀTIKĀ SIDE ONLY,
   # which says "do not check this one", not "it is not printed"; the other 771
   # entries stay gated.  This is the same repeated-name problem that made
   # `build_samyutta_nav.py` turn `matika_gate` OFF for 13Sam02 and 14Sam03 —
   # here it costs one entry instead of the whole check.
   'matika_drop': ('(6) 1. Avijjāvaggavaṇṇanā',),
   'body_errata': {
     '9. Bāhiraphassanānattasuttādivaṇṇanā': '9. Bāhiraphassanānattasuttāvaṇṇanā',
     '1. Santuṭṭhasuttavaṇṇana':             '1. Santuṭṭhasuttavaṇṇanā',
     '5. Samādhisuttavaṇṇanā':               '5. Samādisuttavaṇṇanā',
     '4. Upādānaparipavattasuttavaṇṇanā':    '4. Upādānaparivattasuttavaṇṇanā',
     '8-10. Rajanīyasaṇṭhitasuttādivaṇṇanā': '8-10. Rajanīyasaṇṭhitasuttavaṇṇanā',
     '1. Sabbasutavaṇṇanā':                  '1. Sabbasuttavaṇṇanā',
     '1. Caṇḍhasuttavaṇṇanā':                '1. Caṇḍasuttavaṇṇanā',
     '3. Udāyivagga':                        '3. Upāyivagga',
     '6. Sūkarakhatavagga':                  '6. Sūkaravagga',
     '7. Bodhipakkhiyavaggavaṇṇanā':         '7. Bodhipakkhiyavagga',
     '5. Sammappadhānasaṁyuttavaṇṇanā':      '5. Sammappadhānasaṁyutta',
     '6. Balasaṁyuttavaṇṇanā':               '6. Balasaṁyutta',
     '9. Jhānasaṁyuttavaṇṇanā':              '9. Jhānasaṁyutta',
     '3-10. PaṭhamaĀnandasuttādivaṇṇanā':    '3-10. Paṭhama-ānandasuttādivaṇṇanā'},
   'title': 'Nidānavaggasaṁyuttaṭīkā',
   'label': 'Saṁyuttaṭīkā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 1,
   'matika': (3, 35),
   'matika_gate': True,
   'matika_centred_gate': False,
   'level_memo': True,
   'books': [
     {'title': 'Nidānavaggasaṁyuttaṭīkā',      'lo': 0,   'hi': 202,
      'tops': [SAM], 'levels': [None, VAGGA, LEAF]},
     {'title': 'Khandhavaggasaṁyuttaṭīkā',     'lo': 202, 'hi': 315,
      'tops': [SAM], 'levels': [None, VAGGA, LEAF]},
     {'title': 'Saḷāyatanavaggasaṁyuttaṭīkā',  'lo': 315, 'hi': 466,
      'tops': [SAM], 'levels': [None, VAGGA, LEAF]},
     {'title': 'Mahāvaggasaṁyuttaṭīkā',        'lo': 466, 'hi': 678,
      'tops': [SAM], 'levels': [None, VAGGA, LEAF]},
   ],
 },
}

A.SPEC.update(SAT)
A.main()
