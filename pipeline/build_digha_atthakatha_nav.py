#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nav for the Dīgha-Aṭṭhakathā (Sumaṅgalavilāsinī).  SPEC and nothing else.

The label is the COVER's, as everywhere in this layer:
    07DiA01   SĪLAKKHANDHAVAGGAṬṬHAKATHĀ
    08DiA02   MAHĀVAGGAṬṬHAKATHĀ
    09DiA03   PĀTHIKAVAGGAṬṬHAKATHĀ

Each is ONE book and its tops are the SUTTAS of the canon volume it comments on
— the rule the Vinaya block established: a commentary book takes its structure
from the text it comments on.  So `tops` is an open numbered set, not a list.

!!! ALL THREE PRINT A MĀTIKĀ AND NONE OF THEM DECLARED ONE (added 2026-07-27ai).
They shipped with `matika lists 0` — the check had nothing to check, which is
indistinguishable from a check that passes.  Declaring it found a wrong ROLE in
every one of the three: the two-line colophon frame `Sumaṅgalavilāsiniyā
Dīghanikāyaṭṭhakathāya(ṁ)` read as a heading, quoted verse pādas closing with
the citation dash read as headings, a section heading the edition sets WITH a
terminal stop claimed by the colophon branch, and eight of the edition's own
errata.  All of it was fixed in `build_khu_volume.SPEC`; the heads streams now
equal the mātikā entry counts exactly — 127, 152, 147.

**The Dīgha mātikā is a different shape from the Majjhima's.** Here the CENTRED
group head is the SUTTA and the dotted entries are the sub-kathās beneath it,
which is why `tops` is the sutta pattern; in 12MaA03 the centred head is the
VAGGA and the dotted entries are the suttavaṇṇanās.  Both are the same rule —
the commentary takes the structure of the text it comments on — read off two
differently shaped nikāyas.

07DiA01 is absent until its corpus is rebuilt: it opens with 26 pages of
unnumbered Ganthārambha and Bāhiranidāna that `extract.py` dropped, so its
corpus starts at printed p43 while its body starts at p17.
"""
import build_abhidhamma_nav as A

WORK = 'Dīgha — Sumaṅgalavilāsinī + subcommentaries'
SUTTA = r're:\d+\.\s+.*sutta$'

DIGHA_A = {
 # --- 07DiA01: the Ganthārambha and Nidānakathā, then the thirteen suttas ---
 # Its tops CANNOT be the bare sutta pattern the other two use, because this
 # volume opens with the Sumaṅgalavilāsinī's own preface and the account of the
 # councils — 26 printed pages that entered the corpus only when it was rebuilt
 # from the PDF (2026-07-27ad).  So the tops are named: two unnumbered heads
 # and then the thirteen Sīlakkhandhavagga suttas.
 '07DiA01': {
   'title': 'Sīlakkhandhavaggaṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (11, 15),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # FIVE ERRATA, each printed ONCE in the body and ONCE in the mātikā, so
   # `errata` (which rewrites the mātikā entry globally) is the right key and
   # `body_errata` is not.  Key = the mātikā's reading, value = the body's.
   # NEITHER IS CORRECTED: both readings stand where the edition sets them.
   #   p111  body `…vaṇṇānā`   mātikā `…vaṇṇanā`
   #   p132  body `Komara…`    mātikā `Komāra…`
   #   p317  body `Subhamāṇava…` mātikā `Subhamāṇavaka…`
   #   p321  body `Iddhipāṭihāriya-aṇṇanā` — the body drops the `v` altogether
   #   p329  body `Tayocodanāraha…`  mātikā `Tayocodanārahasatthu…`
   'errata': {'Diṭṭhadhammanibbānavādavaṇṇanā': 'Diṭṭhadhammanibbānavādavaṇṇānā',
              'Komārabhaccajīvakakathāvaṇṇanā': 'Komarabhaccajīvakakathāvaṇṇanā',
              'Subhamāṇavakavatthuvaṇṇanā':     'Subhamāṇavavatthuvaṇṇanā',
              'Iddhipāṭihāriyavaṇṇanā':         'Iddhipāṭihāriya-aṇṇanā',
              'Tayocodanārahasatthuvaṇṇanā':    'Tayocodanārahavaṇṇanā'},
   'tops': ['Ganthārambhakathā', 'Nidānakathā',
            '1. Brahmajālasutta', '2. Sāmaññaphalasutta', '3. Ambaṭṭhasutta',
            '4. Soṇadaṇḍasutta', '5. Kūṭadantasutta', '6. Mahālisutta',
            '7. Jāliyasutta', '8. Mahāsīhanādasutta', '9. Poṭṭhapādasutta',
            '10. Subhasutta', '11. Kevaṭṭasutta', '12. Lohiccasutta',
            '13. Tevijjasutta'],
   'levels': [None, [r're:.']],
 },
 '08DiA02': {
   'title': 'Mahāvaggaṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 8),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # ONE ERRATUM, printed once on each side: the body sets
   # `Catusaṁvajanīyaṭhānavaṇṇanā` (0-based p143) where the mātikā sets
   # `Catusaṁvejanīya…`.  `saṁvejanīya` (from saṁvega) is the expected form, so
   # here the BODY carries the misprint — which changes nothing about how it is
   # handled: the reading stands and the two sides are joined, not corrected.
   'errata': {'Catusaṁvejanīyaṭhānavaṇṇanā': 'Catusaṁvajanīyaṭhānavaṇṇanā'},
   'tops': [SUTTA],
   'levels': [None, [r're:.']],
 },
 '09DiA03': {
   'title': 'Pāthikavaggaṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 8),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # TWO ERRATA.  `2. Udumbarikasutta` is the body's reading and the canonical
   # name (Udumbarikasīhanādasutta); the MĀTIKĀ misprints `2. Udumbariyasutta`.
   # `Sīhapubbaddhakāyādilakkhaṇāvaṇṇanā (17-19)` is the body's, with a long
   # `ā` the mātikā does not print.  Both preserved.
   'errata': {'2. Udumbariyasutta': '2. Udumbarikasutta',
              'Sīhapubbaddhakāyādilakkhaṇavaṇṇanā (17-19)':
                  'Sīhapubbaddhakāyādilakkhaṇāvaṇṇanā (17-19)'},
   'tops': [SUTTA],
   'levels': [None, [r're:.']],
 },
}

A.SPEC.update(DIGHA_A)
A.main()
