#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an Abhidhamma volume's nav tree, checked against its printed mātikā.

    python3 pipeline/build_abhidhamma_nav.py <VOL> [--write]

Generic over the piṭaka rather than one builder per volume, because all twelve
share a shape: a book whose top level is a small named sequence (kaṇḍas, vāras,
bhūmis) and whose sections are the headings printed over the body.  The
per-volume part is the SPEC below — the ordered top level, and which second
level entries are groups rather than leaves.  Everything else is measured.

WHY THE TOP LEVEL IS AN ORDERED SEQUENCE AND NOT A SET.  A label is not unique:
29Abhi01 prints "Mātikā" twice — once as the volume's own opening mātikā (a
top) and once inside the Rūpakaṇḍa (a group under it).  Matching by label alone
would put the second one at the top of the tree.  The sequence is consumed in
printed order, so the first is the top and the second is not, and the builder
REFUSES TO WRITE if the sequence does not appear in order.

THE MĀTIKĀ CHECK IS COMPOUND-AWARE, and it has to be.  The printed mātikā runs
a section head together with its first subsection where they share a page:

    mātikā  Dukanikkhepahetugocchaka        body  Dukanikkhepa + Hetugocchaka
    mātikā  Kāmāvacarakusalapadabhājanī     body  Kāmāvacarakusala + Padabhājanī
    mātikā  Rūpāvacarakusalacatukkanaya     body  Rūpāvacarakusala + Catukkanaya

so an entry is matched against ONE body heading or against a run of up to three
consecutive ones.  Requiring a 1:1 match would report eleven defects that are
not defects; ignoring the compounds would let a genuinely missing heading pass.
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = os.path.join(ROOT, 'site/reader/nav.json')

# THE PAṬṬHĀNA'S LEVELS, AS THE EDITION REUSES THEM.  Written once and shared
# by the twenty books of 40Abhi12 because those books are the same six shapes
# four times over — MEASURED per book all the same (the build prints every
# book's tree), never assumed from the shape of another naya.
# SANDHI, and it cost a tree: "Vipākattika" + "ādi" is printed
# **Vipākattikādi**, not "Vipākattika-ādi", so a pattern ending `tika(ādi)?`
# does not match it and the heading fell through to the level table and was
# nested under its own sibling.  The stem therefore ends `tik`/`duk` and the
# vowel belongs to the suffix.
_TIKA = r're:\d+(-\d+)?\.\s+\S*tik(?:a(?:dvaya)?|ādi)$'
# a gocchaka is a NAMED GROUP OF DUKAS and the edition sets it at the duka's own
# level, abbreviating a run of them ("20-54. Saññojanādichagocchaka")
_DUKA = (r're:\d+(-\d+)?\.\s+\S*(?:duk(?:a(?:dvaya)?|ādi)'
         r'|gocchak(?:a|ādi))$')
_PADA = [r're:\d+(-\d+)?\.\s+\S*pada$',
         r're:[A-ZĀĪŪṄÑṆṬḌḶ]\S*pada(?:[-\s].*)?$']
_VARA = [r're:\d+(-\d+)?\.\s+\S*vāra',
         r're:[A-ZĀĪŪṄÑṆṬḌḶ]\S*vāra(?:[-\s].*)?$',
         '1-7. Vārasattaka', 'Paccanīyuddhāra']
_CATU = ['1. Paccayānuloma', '2. Paccayapaccanīya',
         '3. Paccayānulomapaccanīya', '4. Paccayapaccanīyānuloma',
         '1. Paccayānulomādi', '1-4. Paccayacatukka']
# the six paṭṭhānas, each as its own (tops, levels) pair.  A CROSSED book —
# Tikatika, Dukaduka — has the same kind of section on both sides, so its two
# top levels are told apart by POSITION on the printed line (`pairsides`).
_SHAPE = {
 'Tika':     ([_TIKA], [None, _VARA, _CATU]),
 'Duka':     ([_DUKA], [None, _VARA, _CATU]),
 'Dukatika': ([_DUKA], [None, [_TIKA], _PADA, _VARA, _CATU]),
 'Tikaduka': ([_TIKA], [None, [_DUKA], _PADA, _VARA, _CATU]),
 'Tikatika': ([_TIKA], [None, [_TIKA], _PADA, _VARA, _CATU]),
 'Dukaduka': ([_DUKA], [None, [_DUKA], _PADA, _VARA, _CATU]),
}


def _bk(naya, kind, lo, hi, pg):
    """One of 40Abhi12's twenty books: naya x paṭṭhāna, with its own title
    page and homage.  `pg` is the PRINTED page range its own mātikā gives it,
    kept so the build can check the ordinal boundaries against a second
    printed source."""
    tops, levels = _SHAPE[kind]
    return {'title': '%s %spaṭṭhānapāḷi' % (naya, kind), 'kind': kind,
            'naya': naya, 'lo': lo, 'hi': hi, 'pg': pg,
            'tops': tops, 'levels': levels}


SPEC = {
 '29Abhi01': {
   'title': 'Dhammasaṅgaṇīpāḷi',
   'work': 'Abhidhamma: Dhammasaṅgaṇī',
   'first': 0,
   'matika': (13, 18),          # 0-based pdftotext pages of the front mātikā
   'tops': ['Mātikā', '1. Cittuppādakaṇḍa', '2. Rūpakaṇḍa',
            '3. Nikkhepakaṇḍa', '4. Aṭṭhakathākaṇḍa'],
   # THE SECOND LEVEL, per top and IN PRINTED ORDER.  Everything between one
   # of these and the next is its child; anything before the first is a child
   # of the top itself.  Ordered rather than a set for the same reason the top
   # level is: a label is not unique — "Mātikā" is both a top and a second
   # level inside the Rūpakaṇḍa, and "Kāmāvacarakusala" occurs twice in the
   # Cittuppādakaṇḍa.
   #
   # THE BOOK PROVES THIS NESTING, so it is not a guess.  The Dukamātikā opens
   # at ord22, the thirteen gocchakas and dukas run to "Piṭṭhidukaṁ." at
   # ord121, and the NEXT printed line is the colophon
   # "Abhidhammadukamātikā." closing the whole block — after which
   # "Suttantikadukamātikā" begins as its sibling.  The printed MĀTIKĀ gives no
   # signal at all (it sets Tikamātikā, Dukamātikā and all thirteen at the same
   # indent), exactly as the Netti's mātikā flattens its four vāras and the
   # thirty-four sections under the fourth; the body's own colophons are the
   # second input.  `_abhi01verify.js` asserts the span.
   'mids': {
     'Mātikā':             ['Tikamātikā', 'Dukamātikā', 'Suttantikadukamātikā'],
     '2. Rūpakaṇḍa':       ['Uddesa', 'Mātikā', 'Rūpavibhatti'],
     '3. Nikkhepakaṇḍa':   ['Tikanikkhepa', 'Dukanikkhepa',
                            'Suttantikadukanikkhepa'],
     '4. Aṭṭhakathākaṇḍa': ['Tika-atthuddhāra', 'Duka-atthuddhāra'],
     # 1. Cittuppādakaṇḍa is left flat for now — its 68 sections do have a
     # natural second level (the citta classes: Kāmāvacarakusala,
     # Rūpāvacarakusala, Arūpāvacarakusala, Tebhūmakakusala, Lokuttarakusala,
     # Dvādasa akusala, Abyākatavipāka, Akusalavipāka-abyākata,
     # Ahetukakiriyā-abyākata) but that is a judgement about the book and is
     # not settled here.  REPORTED, not invented.
   },
   # THE EDITION'S OWN, preserved verbatim on both pages and named here only so
   # the check knows they are the same section.  The mātikā (p69) compounds the
   # group head with its first subsection as "Tebhūmakakāmāvacarakusala", but
   # writes the group head WITHOUT its own `-kusala`, where the body (p88) sets
   # "Tebhūmakakusala" and then "Kāmāvacarakusala".  Widening the compound
   # matcher to tolerate a dropped syllable would let a genuinely missing
   # heading through, so it is listed instead.
   'errata': {'Tebhūmakakāmāvacarakusala': 'Tebhūmakakusala Kāmāvacarakusala'},
 },
 '30Abhi02': {
   'title': 'Vibhaṅgapāḷi',
   'work': 'Abhidhamma: Vibhaṅga',
   'first': 0,
   # ITS MĀTIKĀ IS A REAL ORDERED LIST of the body's own headings — 189 dotted
   # entries over 0-based pages 3-10, three levels deep — so `matika_gate` is
   # TRUE here, which it cannot be anywhere in the Paṭṭhāna (an abbreviating
   # index).  This is the second volume in the piṭaka to earn the hard gate.
   'matika': (3, 10),
   # THE TOP LEVEL: the eighteen vibhaṅgas, in printed order, read off the body
   'tops': ['1. Khandhavibhaṅga', '2. Āyatanavibhaṅga', '3. Dhātuvibhaṅga',
            '4. Saccavibhaṅga', '5. Indriyavibhaṅga',
            '6. Paṭiccasamuppādavibhaṅga', '7. Satipaṭṭhānavibhaṅga',
            '8. Sammappadhānavibhaṅga', '9. Iddhipādavibhaṅga',
            '10. Bojjhaṅgavibhaṅga', '11. Maggaṅgavibhaṅga',
            '12. Jhānavibhaṅga', '13. Appamaññāvibhaṅga',
            '14. Sikkhāpadavibhaṅga', '15. Paṭisambhidāvibhaṅga',
            '16. Ñāṇavibhaṅga', '17. Khuddakavatthuvibhaṅga',
            '18. Dhammahadayavibhaṅga'],
   # DEPTH BY NAME, and the sets are the edition's own: a vibhaṅga divides into
   # bhājanīyas and a Pañhāpucchaka (thirteen do), or — in the Ñāṇa and
   # Khuddakavatthu vibhaṅgas — into a mātikā and a niddesa per numerical group,
   # or — in the Dhammahadaya — into ten vāras.  Anything else is a leaf at the
   # current depth, which is what the Pañhāpucchaka's Tika and Duka are, and the
   # khandhas, dhātus and attikas under a bhājanīya or a vāra.
   #
   # NOTE the numbering is NOT uniform and must not be normalised: the
   # Indriyavibhaṅga prints no Suttantabhājanīya, so its two divisions are
   # "1. Abhidhammabhājanīya" and "2. Pañhāpucchaka".  A pattern reads both.
   'levels': [
     None,                                            # level 0 = 'tops'
     [r're:\d+\.\s+(?:Suttanta|Abhidhamma)bhājanīya$',
      r're:\d+\.\s+Pañhāpucchaka$',
      r're:\d+\.\s+\S*mātikā$',
      r're:\d+\.\s+\S*niddesa$',
      r're:\d+\.\s+\S*vāra$'],
   ],
   # THE MĀTIKĀ GLOSSES A REPEATED NAME, and the gloss is not part of the name.
   # The Paṭiccasamuppādavibhaṅga's Abhidhammabhājanīya prints the four
   # catukkas TWICE — once as its own mātikā (1-4) and once as the niddesa
   # (5-8), the body numbering them continuously 1..8 — and the printed mātikā
   # disambiguates the second run by adding "(niddesa)" in parentheses.  The
   # body heads them with the bare names.  Listed here rather than handled by
   # stripping parentheses generally, which would let a genuinely missing
   # heading through.
   'errata': {'5. Paccayacatukka (niddesa)':   '5. Paccayacatukka',
              '6. Hetucatukka (niddesa)':      '6. Hetucatukka',
              '7. Sampayuttacatukka (niddesa)': '7. Sampayuttacatukka',
              '8. Aññamaññacatukka (niddesa)': '8. Aññamaññacatukka'},
 },
 # --- Yamaka I: FIVE yamakas in one volume, and the volume is ONE BHĀGA ------
 # The title page prints "Abhidhammapiṭake / YAMAKAPĀḶI / (Paṭhamo bhāgo)", so
 # this is one node labelled as the edition labels it, with its five inner
 # yamakas as the first tree level — the shape `group_abhidhamma_volumes.py`
 # gave volumes 33-40 and `_abhigroupverify.js` asserts.  NOT `separate_books`:
 # the five yamakas are divisions of the Yamaka, which is ONE of the seven
 # books, where 31Abhi03's two really are two of the seven.
 #
 # THE FRONT MĀTIKĀ IS A REAL ORDERED LIST, one page or two per yamaka, over
 # 0-based pages 3-10 — and page 10 (roman folio "viii") is the page the
 # declared text extent wrongly counted as text (see build_khu_volume.py).
 #
 # THE FOUR LATER YAMAKAS SHARE ONE SHAPE and the Mūlayamaka has its own.
 # "2. Pavatti" is printed as the LEFT half of a pair-line over each of its
 # three vāras, so by the standing rule it stands one level above them; it is
 # a top here and its second and third printings are ANCESTOR REPRINTS, which
 # is also what keeps `_navdup.js`'s adjacent-sibling rule satisfied.
 # !!! THE KHANDHAYAMAKA'S THIRD IS PRINTED WITHOUT IT: p67 sets a bare
 # "3. Uppādanirodhavāra" where the volume's own mātikā (p6) sets the pair.
 # The edition's asymmetry, followed rather than smoothed — the heading still
 # lands under "2. Pavatti" because that is the level it is declared at.
 '33Abhi05': {
   'title': 'Yamakapāḷi (Paṭhamo bhāgo)',
   'label': 'Yamakapāḷi (Paṭhamo bhāgo)',   # this volume's own title page
   'work': 'Abhidhamma: Yamaka',
   'first': 0,
   'matika': (3, 10),
   'tops': [],
   'level_memo': True,
   'matika_reprints': True,
   'books': [
     # THE MŪLAYAMAKA: an Uddesavāra and a Niddesavāra, each split into the
     # Mūlavāra and the nine that follow it, each holding the same four
     # nayacatukkas.  Neither vāra is printed as a heading — the edition names
     # them only where they CLOSE ("Uddesavāro niṭṭhito.") — so the four
     # printed headings stand at the top and the asymmetry is REPORTED, not
     # filled in with a heading the page does not set.
     {'title': 'Mūlayamakapāḷi', 'lo': 0, 'hi': 99,
      'tops': ['1. Mūlavāra-uddesa', '2-10. Hetuvārādi-uddesa',
               '1. Mūlavāraniddesa', '2-10. Hetuvārādiniddesa'],
      'levels': [None,
        ['1. Kusalapada nayacatukka', '2. Akusalapada nayacatukka',
         '3. Abyākatapada nayacatukka', '4. Nāmapada nayacatukka']]},
     {'title': 'Khandhayamakapāḷi', 'lo': 99, 'hi': 312,
     'tops': ['1. Paṇṇattivāra-uddesa', '1. Paṇṇattivāraniddesa',
              '2. Pavatti', '3. Pariññāvāra'],
      'levels': [None,
        ['1. Padasodhanavāra', '2. Padasodhanamūlacakkavāra',
         # SANDHI, and it cost two headings on the first run: Suddha +
         # āyatana is printed **Suddhāyatanavāra**, so a pattern spelling
         # `Suddha` matches the Khandha, Dhātu and Sacca yamakas and NOT the
         # Āyatana one — whose two vāras then fell through to the catch-all
         # and hung under the previous section.  The stem ends at `Suddh` and
         # the vowel belongs to what follows.  (The Paṭṭhāna hit the same
         # trap at `tika`/`tikādi`; see 2026-07-26v.)
         r're:\d+\.\s+Suddh\S*vāra$',
         '1. Uppādavāra', '2. Nirodhavāra', '3. Uppādanirodhavāra'],
        ['1. Paccuppannavāra', '2. Atītavāra', '3. Anāgatavāra',
         '4. Paccuppannātītavāra', '5. Paccuppannānāgatavāra',
         '6. Atītānāgatavāra', 'Anuloma', 'Paccanīka'],
        ['Anulomapuggala', 'Anuloma-okāsa', 'Anulomapuggalokāsa',
         'Paccanīkapuggala', 'Paccanīka-okāsa', 'Paccanīkapuggalokāsa']]},
     {'title': 'Āyatanayamakapāḷi', 'lo': 312, 'hi': 569,
     'tops': ['1. Paṇṇattivāra-uddesa', '1. Paṇṇattivāraniddesa',
              '2. Pavatti', '3. Pariññāvāra'],
      'levels': [None,
        ['1. Padasodhanavāra', '2. Padasodhanamūlacakkavāra',
         # SANDHI, and it cost two headings on the first run: Suddha +
         # āyatana is printed **Suddhāyatanavāra**, so a pattern spelling
         # `Suddha` matches the Khandha, Dhātu and Sacca yamakas and NOT the
         # Āyatana one — whose two vāras then fell through to the catch-all
         # and hung under the previous section.  The stem ends at `Suddh` and
         # the vowel belongs to what follows.  (The Paṭṭhāna hit the same
         # trap at `tika`/`tikādi`; see 2026-07-26v.)
         r're:\d+\.\s+Suddh\S*vāra$',
         '1. Uppādavāra', '2. Nirodhavāra', '3. Uppādanirodhavāra'],
        ['1. Paccuppannavāra', '2. Atītavāra', '3. Anāgatavāra',
         '4. Paccuppannātītavāra', '5. Paccuppannānāgatavāra',
         '6. Atītānāgatavāra', 'Anuloma', 'Paccanīka'],
        ['Anulomapuggala', 'Anuloma-okāsa', 'Anulomapuggalokāsa',
         'Paccanīkapuggala', 'Paccanīka-okāsa', 'Paccanīkapuggalokāsa']]},
     # ABRIDGED BY THE EDITION ITSELF — "(Dhātuyamakaṁ paripuṇṇaṁ peyyālena.)"
     # — so its Pavatti has one vāra and its Pariññāvāra none.  Its own mātikā
     # (p9) lists exactly that.
     {'title': 'Dhātuyamakapāḷi', 'lo': 569, 'hi': 589,
     'tops': ['1. Paṇṇattivāra-uddesa', '1. Paṇṇattivāraniddesa',
              '2. Pavatti', '3. Pariññāvāra'],
      'levels': [None,
        ['1. Padasodhanavāra', '2. Padasodhanamūlacakkavāra',
         # SANDHI, and it cost two headings on the first run: Suddha +
         # āyatana is printed **Suddhāyatanavāra**, so a pattern spelling
         # `Suddha` matches the Khandha, Dhātu and Sacca yamakas and NOT the
         # Āyatana one — whose two vāras then fell through to the catch-all
         # and hung under the previous section.  The stem ends at `Suddh` and
         # the vowel belongs to what follows.  (The Paṭṭhāna hit the same
         # trap at `tika`/`tikādi`; see 2026-07-26v.)
         r're:\d+\.\s+Suddh\S*vāra$',
         '1. Uppādavāra', '2. Nirodhavāra', '3. Uppādanirodhavāra'],
        ['1. Paccuppannavāra', '2. Atītavāra', '3. Anāgatavāra',
         '4. Paccuppannātītavāra', '5. Paccuppannānāgatavāra',
         '6. Atītānāgatavāra', 'Anuloma', 'Paccanīka'],
        ['Anulomapuggala', 'Anuloma-okāsa', 'Anulomapuggalokāsa',
         'Paccanīkapuggala', 'Paccanīka-okāsa', 'Paccanīkapuggalokāsa']]},
     {'title': 'Saccayamakapāḷi', 'lo': 589, 'hi': 762,
     'tops': ['1. Paṇṇattivāra-uddesa', '1. Paṇṇattivāraniddesa',
              '2. Pavatti', '3. Pariññāvāra'],
      'levels': [None,
        ['1. Padasodhanavāra', '2. Padasodhanamūlacakkavāra',
         # SANDHI, and it cost two headings on the first run: Suddha +
         # āyatana is printed **Suddhāyatanavāra**, so a pattern spelling
         # `Suddha` matches the Khandha, Dhātu and Sacca yamakas and NOT the
         # Āyatana one — whose two vāras then fell through to the catch-all
         # and hung under the previous section.  The stem ends at `Suddh` and
         # the vowel belongs to what follows.  (The Paṭṭhāna hit the same
         # trap at `tika`/`tikādi`; see 2026-07-26v.)
         r're:\d+\.\s+Suddh\S*vāra$',
         '1. Uppādavāra', '2. Nirodhavāra', '3. Uppādanirodhavāra'],
        ['1. Paccuppannavāra', '2. Atītavāra', '3. Anāgatavāra',
         '4. Paccuppannātītavāra', '5. Paccuppannānāgatavāra',
         '6. Atītānāgatavāra', 'Anuloma', 'Paccanīka'],
        ['Anulomapuggala', 'Anuloma-okāsa', 'Anulomapuggalokāsa',
         'Paccanīkapuggala', 'Paccanīka-okāsa', 'Paccanīkapuggalokāsa']]},
   ],
 },
 # --- Yamaka II: THREE yamakas, and THREE DIFFERENT SHAPES ------------------
 # One node labelled off its own title page ("Abhidhammapiṭake / YAMAKAPĀḶI /
 # (Dutiyo bhāgo)"), three inner books.  Front mātikā 0-based pages 3-10, one
 # or two per book — the same eight-page, five-header shape as 33Abhi05, so the
 # roman-folio filter added there is what makes it readable here.
 '34Abhi06': {
   'title': 'Yamakapāḷi (Dutiyo bhāgo)',
   'label': 'Yamakapāḷi (Dutiyo bhāgo)',   # this volume's own title page
   'work': 'Abhidhamma: Yamaka',
   'first': 0,
   'matika': (3, 10),
   'tops': [],
   'matika_reprints': True,
   'books': [
     # THE SAṄKHĀRAYAMAKA is 33Abhi05's shape exactly, with one difference the
     # page states: it has THREE paṇṇatti vāras, not four — no
     # Suddhasaṅkhāramūlacakkavāra — and its Pariññāvāra is a single closing
     # section with no vāras under it, which its own mātikā (p5) sets as one
     # dotted entry rather than a group head.
     {'title': 'Saṅkhārayamakapāḷi', 'lo': 0, 'hi': 162,
      'tops': ['1. Paṇṇattivāra-uddesa', '1. Paṇṇattivāraniddesa',
               '2. Pavatti', '3. Pariññāvāra'],
      'levels': [None,
        ['1. Padasodhanavāra', '2. Padasodhanamūlacakkavāra',
         # sandhi: the stem ends at `Suddh` — see 33Abhi05
         r're:\d+\.\s+Suddh\S*vāra$',
         '1. Uppādavāra', '2. Nirodhavāra', '3. Uppādanirodhavāra'],
        ['1. Paccuppannavāra', '2. Atītavāra', '3. Anāgatavāra',
         '4. Paccuppannātītavāra', '5. Paccuppannānāgatavāra',
         '6. Atītānāgatavāra', 'Anuloma', 'Paccanīka'],
        ['Anulomapuggala', 'Anuloma-okāsa', 'Anulomapuggalokāsa',
         'Paccanīkapuggala', 'Paccanīka-okāsa', 'Paccanīkapuggalokāsa']]},
     # THE ANUSAYAYAMAKA: an Uppattiṭṭhānavāra and then the Mahāvāra, whose
     # seven vāras each run ANULOMA then PAṬILOMA.  **The edition prints each
     # vāra's name TWICE**, once over each half, and the mātikā (p6-7) does the
     # same — but the COLOPHONS say it is ONE vāra: "Anusayavāre anulomaṁ.",
     # "Anusayavāre paṭilomaṁ.", then "Anusayavāro." closing both.  So the
     # second printing is an ANCESTOR REPRINT and each vāra is one node with
     # six children.  Splitting it would also put two adjacent siblings of the
     # same name in the tree, which `_navdup.js` refuses.  The cost is that the
     # mātikā's second printing of each name is reported OUT OF ORDER — five
     # of them, named and expected, not a gate.
     {'title': 'Anusayayamakapāḷi', 'lo': 162, 'hi': 511,
      'tops': ['1. Uppattiṭṭhānavāra', '2. Mahāvāra'],
      'levels': [None,
        ['1. Anusayavāra', '2. Sānusayavāra', '3. Pajahanavāra',
         '4. Pariññāvāra', '5. Pahīnavāra', '6. Uppajjanavāra',
         '7. Dhātupucchāvāra', '7. Dhātuvisajjanāvāra'],
        ['Anulomapuggala', 'Anuloma-okāsa', 'Anulomapuggalokāsa',
         'Paṭilomapuggala', 'Paṭiloma-okāsa', 'Paṭilomapuggalokāsa']]},
     # THE CITTAYAMAKA: an Uddesa and a Niddesa of the SAME structure, each
     # holding the Suddhacittasāmañña's three vāras of fourteen, then the two
     # missakavisesas.  "1. Suddhacittasāmañña" is reprinted at the head of the
     # Dhammavāra and the Puggaladhammavāra — in the body AND in the mātikā —
     # and is an ancestor reprint both times.
     {'title': 'Cittayamakapāḷi', 'lo': 511, 'hi': 627,
      'tops': ['Uddesa', 'Niddesa'],
      'levels': [None,
        ['1. Suddhacittasāmañña', '2. Suttantacittamissakavisesa',
         '3. Abhidhammacittamissakavisesa'],
        ['1. Puggalavāra', '2. Dhammavāra', '3. Puggaladhammavāra'],
        ['1. Uppādanirodhakālasambhedavāra', '2. Uppāduppannavāra',
         '3. Nirodhuppannavāra', '4. Uppādavāra', '5. Nirodhavāra',
         '6. Uppādanirodhavāra', '7. Uppajjamānananirodhavāra',
         '8. Uppajjamānuppannavāra', '9. Nirujjhamānuppannavāra',
         '10. Uppannuppādavāra', '11. Atītānāgatavāra',
         '12. Uppannuppajjamānavāra', '13. Niruddhanirujjhamānavāra',
         '14. Atikkantakālavāra']]},
   ],
 },
 # --- Yamaka III: the LAST volume of the Abhidhammapiṭaka -------------------
 # One node labelled off its own title page, two inner books.  Front mātikā
 # 0-based pages 3-8.  Its last printed page closes "Indriyayamakapāḷi
 # niṭṭhitā." AND "Yamakapakaraṇaṁ niṭṭhitaṁ." — the whole sixth book of the
 # piṭaka, not just this bhāga.
 '35Abhi07': {
   'title': 'Yamakapāḷi (Tatiyo bhāgo)',
   'label': 'Yamakapāḷi (Tatiyo bhāgo)',   # this volume's own title page
   'work': 'Abhidhamma: Yamaka',
   'first': 0,
   'matika': (3, 8),
   'tops': [],
   'level_memo': True,
   'matika_reprints': True,
   # THE EDITION'S OWN MISPRINT, preserved verbatim on the page and named here
   # only so the mātikā check knows the two are one section: printed p328 heads
   # the Pariññāvāra's fourth vāra **"4. Paccuppannātītivāra"** — *-īti-* for
   # *-īta-* — where the other four printings of that heading (p28, p50, p71,
   # p229) and this volume's own mātikā (p8) all set "4. Paccuppannātītavāra".
   'body_errata': {'4. Paccuppannātītivāra': '4. Paccuppannātītavāra'},
   'books': [
     # THE DHAMMAYAMAKA — 33Abhi05's shape, except that its third division is
     # the BHĀVANĀVĀRA, not a Pariññāvāra, and the edition sets it as a single
     # closing section with no vāras under it (its mātikā p5 lists it as one
     # dotted entry, and "Bhāvanāvāro." closes it on p81).
     {'title': 'Dhammayamakapāḷi', 'lo': 0, 'hi': 231,
      'tops': ['1. Paṇṇattivāra-uddesa', '1. Paṇṇattivāraniddesa',
               '2. Pavatti', '3. Bhāvanāvāra'],
      'levels': [None,
        ['1. Padasodhanavāra', '2. Padasodhanamūlacakkavāra',
         r're:\d+\.\s+Suddh\S*vāra$',
         '1. Uppādavāra', '2. Nirodhavāra', '3. Uppādanirodhavāra'],
        # !!! `Anuloma`/`Paccanīka` GET A LEVEL OF THEIR OWN HERE, where
        # 33Abhi05 could share one with the six vāras.  Under this volume's
        # Pariññāvāra the six vāras clamp to depth 1 (no middle rung) and
        # EACH CARRIES an Anuloma and a Paccanīka — so declared at the same
        # level, `level_memo` gives the pair the depth it just gave the vāra
        # and they render as its SIBLINGS instead of its children.  Declared
        # one level down they clamp to depth 2 under a vāra wherever the vāra
        # itself sits, which is what the page shows in all three branches.
        ['1. Paccuppannavāra', '2. Atītavāra', '3. Anāgatavāra',
         '4. Paccuppannātītavāra', '5. Paccuppannānāgatavāra',
         '6. Atītānāgatavāra'],
        ['Anuloma', 'Paccanīka'],
        ['Anulomapuggala', 'Anuloma-okāsa', 'Anulomapuggalokāsa',
         'Paccanīkapuggala', 'Paccanīka-okāsa', 'Paccanīkapuggalokāsa']]},
     # THE INDRIYAYAMAKA — the same table, and here `level_memo` is needed for
     # the same reason as in 33Abhi05: the six vāras sit THREE rungs down under
     # "2. Pavatti" and TWO under "3. Pariññāvāra".
     # **Its Pavatti holds only the UPPĀDAVĀRA** — the edition prints no
     # Nirodhavāra and no Uppādanirodhavāra for it, and its own mātikā (p7-p9)
     # goes straight from the Uppādavāra's six vāras to the Pariññāvāra.  The
     # short branch is the page's, not a drop.
     {'title': 'Indriyayamakapāḷi', 'lo': 231, 'hi': 714,
      'tops': ['1. Paṇṇattivāra-uddesa', '1. Paṇṇattivāraniddesa',
               '2. Pavatti', '3. Pariññāvāra'],
      'levels': [None,
        ['1. Padasodhanavāra', '2. Padasodhanamūlacakkavāra',
         r're:\d+\.\s+Suddh\S*vāra$',
         '1. Uppādavāra', '2. Nirodhavāra', '3. Uppādanirodhavāra'],
        ['1. Paccuppannavāra', '2. Atītavāra', '3. Anāgatavāra',
         '4. Paccuppannātītavāra', '4. Paccuppannātītivāra',
         '5. Paccuppannānāgatavāra', '6. Atītānāgatavāra'],
        ['Anuloma', 'Paccanīka'],
        ['Anulomapuggala', 'Anuloma-okāsa', 'Anulomapuggalokāsa',
         'Paccanīkapuggala', 'Paccanīka-okāsa', 'Paccanīkapuggalokāsa']]},
   ],
 },
 '32Abhi04': {
   'title': 'Kathāvatthupāḷi',
   'work': 'Abhidhamma: Kathāvatthu',
   'first': 0,
   'matika': (3, 13),
   # !!! THE FIRST VAGGA HAS NO PRINTED HEADING, and the tree follows the page
   # rather than smoothing it (the user's decision, 2026-07-26aa).  The edition
   # opens straight into "1. Puggalakathā" and names that vagga only where it
   # CLOSES — "Mahāvaggo." at ord305 — while vaggas 2-23 are headed and are
   # reprinted at the head of every kathā under them.  ITS OWN MĀTIKĀ DOES THE
   # SAME: the printed table sets the first vagga's ten kathās as its own group
   # heads and only then begins "2. Dutiyavagga".
   #
   # So the top level is those ten kathās followed by the twenty-two named
   # vaggas — thirty-two entries, asymmetric because the EDITION is asymmetric.
   # A first row taken from the closing colophon was the alternative and was
   # rejected: "Mahāvagga" is a BOOK title elsewhere in this canon (03Vin03 and
   # 07Di02 both print Mahāvaggapāḷi, and three commentary volumes echo it), so
   # a bare row of that name inside the Kathāvatthu would read as one — the
   # collision `_navdup.js` exists to catch.  THE BOOK IS Kathāvatthupāḷi, off
   # its own title page, and nothing here changes that.
   'tops': ['1. Puggalakathā', '2. Parihānikathā', '3. Brahmacariyakathā',
            '3. Odhisokathā', '4. Jahatikathā', '5. Sabbamatthītikathā',
            '6. Atītakkhandhādikathā', '7. Ekaccaṁatthītikathā',
            '8. Satipaṭṭhānakathā', '9. Hevatthikathā',
            '2. Dutiyavagga', '3. Tatiyavagga', '4. Catutthavagga',
            '5. Pañcamavagga', '6. Chaṭṭhavagga', '7. Sattamavagga',
            '8. Aṭṭhamavagga', '9. Navamavagga', '10. Dasamavagga',
            '11. Ekādasamavagga', '12. Dvādasamavagga', '13. Terasamavagga',
            '14. Cuddasamavagga', '15. Pannarasamavagga', '16. Soḷasamavagga',
            '17. Sattarasamavagga', '18. Aṭṭhārasamavagga',
            '19. Ekūnavīsatimavagga', '20. Vīsatimavagga',
            '21. Ekavīsatimavagga', '22. Bāvīsatimavagga',
            '23. Tevīsatimavagga'],
   # THE EDITION'S OWN VARIATIONS BETWEEN ITS MĀTIKĀ AND ITS BODY, each page
   # keeping what it prints and named here only so the check knows they are one
   # section: the mātikā disambiguates the two kathās that share the number 3
   # with "(ka)" and "(kha)", which the body does not, and it spells the
   # fifteenth vagga *Pannārasama* with a long ā where the body sets
   # *Pannarasama*.
   'errata': {'3. Brahmacariyakathā (ka)': '3. Brahmacariyakathā',
              '3. Odhisokathā (kha)': '3. Odhisokathā',
              '15. Pannārasamavagga': '15. Pannarasamavagga',
              # the mātikā spells it Cittiṭṭhiti, the body Cittaṭṭhiti
              '(16) 7. Cittiṭṭhitikathā': '(16) 7. Cittaṭṭhitikathā',
              # the mātikā abbreviates the range 106-108 as 106-8
              '(106-8) 1-3. Tissopi-anusayakathā':
                  '(106-108) 1-3. Tissopi-anusayakathā',
              # and the body closes the compound up where the mātikā spaces it
              '(175) 10. Navattabbaṁbuddhassadinnaṁ mahapphalantikathā':
                  '(175) 10. Navattabbaṁbuddhassadinnaṁmahapphalantikathā'},
   'levels': [
     None,                                            # level 0 = 'tops'
     # a kathā, with or without the absolute number the edition sets in
     # parentheses ("(10) 1. Parūpahārakathā")
     [r're:(?:\(\d+(?:-\d+)?\)\s+)?\d+(?:-\d+)?\.\s+.*kathā$'],
     # the Puggalakathā's own apparatus of arguments, which the mātikā lists
     # under it
     [r're:\d+(?:-\d+)?\.\s+\S*(?:saccikaṭṭha|saṁsandana|yutti|sodhana'
      r'|anuyoga|sādhana|parihāni)\S*$'],
     ['1. Anulomapaccanīka', '2. Paccanīkānuloma'],
   ],
 },
 '31Abhi03': {
   'title': 'Dhātukathāpāḷi',
   'work': 'Abhidhamma: Dhātukathā, Puggalapaññatti',
   'first': 0,
   # BOTH BOOKS PRINT THEIR OWN MĀTIKĀ, and both are real ordered lists: the
   # Dhātukathā's over 0-based pages 3-5, the Puggalapaññatti's on page 6.  The
   # builder's `matika` is one range per volume, and that is enough here because
   # the two mātikās are printed in the same order as the two books, so the
   # forward scan over the combined entry list matches the combined tree.
   'matika': (3, 6),
   'tops': [],
   'books': [
     # THE DHĀTUKATHĀ: an Uddesa of five mātikās, then FOURTEEN nayas, each
     # named twice on the page — once as "N. <Nth>naya" and once as the
     # padaniddesa it performs.  The naya is the outer of the two: the mātikā
     # sets the naya as a centred group head with its padaniddesa beneath it.
     {'title': 'Dhātukathāpāḷi', 'lo': 0, 'hi': 518,
      'tops': ['Uddesa', '1. Paṭhamanaya', '2. Dutiyanaya', '3. Tatiyanaya',
               '4. Catutthanaya', '5. Pañcamanaya', '6. Chaṭṭhanaya',
               '7. Sattamanaya', '8. Aṭṭhamanaya', '9. Navamanaya',
               '10. Dasamanaya', '11. Ekādasamanaya', '12. Dvādasamanaya',
               '13. Terasamanaya', '14. Cuddasamanaya'],
      # DECLARED LITERALLY RATHER THAN BY PATTERN, so that the COLOPHON CHECK
      # can bite: the edition closes each of the fourteen padaniddesas by name
      # and ordinal ("Saṅgahāsaṅgahapadaniddeso paṭhamo."), which is the only
      # independent witness this book offers.  A pattern names no section and
      # the check skips it.  NOTE the edition's own inconsistent spacing —
      # entries 5 and 12 are TWO words where the other twelve are one — kept
      # exactly as printed.
      'levels': [None,
                 ['1. Saṅgahāsaṅgahapadaniddesa',
                  '2. Saṅgahitena-asaṅgahitapadaniddesa',
                  '3. Asaṅgahitenasaṅgahitapadaniddesa',
                  '4. Saṅgahitenasaṅgahitapadaniddesa',
                  '5. Asaṅgahitena asaṅgahitapadaniddesa',
                  '6. Sampayogavippayogapadaniddesa',
                  '7. Sampayuttenavippayuttapadaniddesa',
                  '8. Vippayuttenasampayuttapadaniddesa',
                  '9. Sampayuttenasampayuttapadaniddesa',
                  '10. Vippayuttenavippayuttapadaniddesa',
                  '11. Saṅgahitenasampayuttavippayuttapadaniddesa',
                  '12. Sampayuttena saṅgahitāsaṅgahitapadaniddesa',
                  '13. Asaṅgahitenasampayuttavippayuttapadaniddesa',
                  '14. Vippayuttenasaṅgahitāsaṅgahitapadaniddesa',
                  '1. Nayamātikā', '2. Abbhantaramātikā',
                  '3. Nayamukhamātikā', '4. Lakkhaṇamātikā',
                  '5. Bāhiramātikā']]},
     # THE PUGGALAPAÑÑATTI: a Mātikā of ten uddesas and a Niddesa of ten
     # paññattis — the edition's own two halves, each its own top.
     {'title': 'Puggalapaññattipāḷi', 'lo': 518, 'hi': 890,
      'tops': ['Mātikā', 'Niddesa'],
      'levels': [None,
                 [r're:\d+\.\s+\S*uddesa$',
                  r're:\d+\.\s+\S*paññatti$']]},
   ],
   # THE EDITION'S OWN MISPRINT, and each page keeps what it prints.  The BODY
   # heads the fifth section of the Niddesa "5. Pañcakapaggalapaññatti" —
   # *paggala* for *puggala* — where this volume's own mātikā (p173) and its
   # printed word index both set "Pañcakapuggalapaññatti".  Named here only so
   # the mātikā check knows the two are one section.
   'errata': {'5. Pañcakapuggalapaññatti': '5. Pañcakapaggalapaññatti'},
   # TWO BOOKS OF THE PIṬAKA, not two bhāgas of one work — so TWO nav nodes.
   'separate_books': True,
 },
 '36Abhi08': {
   'title': 'Tikapaṭṭhānapāḷi',
   'label': 'Paṭṭhānapāḷi (Paṭhamo bhāgo)',   # this volume's own title page
   'work': 'Abhidhamma: Paṭṭhāna',
   'first': 0,
   'matika': (3, 28),
   # THE TOP LEVEL, in printed order: the two uddesa sections, the Pucchāvāra,
   # then the five tikas this bhāga covers.
   'tops': ['1. Paccayuddesa', '2. Paccayaniddesa', 'Pucchāvāra',
            '1. Kusalattika', '2. Vedanāttika', '3. Vipākattika',
            '4. Upādinnattika', '5. Saṁkiliṭṭhattika'],
   # DEPTH BY NAME, and why `mids` is not enough here.  The Paṭṭhāna nests four
   # deep under a tika and prints 1477 headings in this volume alone; `mids`
   # gives exactly two levels, so ~1400 of them would land as ONE FLAT LIST
   # under their vāra — the shape the user reported on this very sidebar.
   # Each level below is a closed set of names the edition reuses at that depth
   # throughout the Paṭṭhāna, so the same table should serve 37-40 (to be
   # measured, not assumed).  A heading in none of the sets is a leaf at the
   # current depth, which is what the enumeration heads (Tika, Catukka,
   # Hetuduka …) are.
   'levels': [
     None,                                             # level 0 = 'tops'
     ['1. Paṭiccavāra', '2. Sahajātavāra', '3. Paccayavāra',
      '4. Nissayavāra', '5. Saṁsaṭṭhavāra', '6. Sampayuttavāra',
      '7. Pañhāvāra', 'Ekamūlaka', 'Dumūlakādi'],
     ['1. Paccayānuloma', '2. Paccayapaccanīya',
      '3. Paccayānulomapaccanīya', '4. Paccayapaccanīyānuloma'],
     ['1. Vibhaṅgavāra', '2. Saṅkhyāvāra', 'Saṅkhyāvāra',
      'Pañhāvāra-paccanīyuddhāra', '2. Paccanīyuddhāra',
      'Gaṇanā hetumūlakā', 'Gaṇanamūlaka'],
   ],
   # see the comment at the matcher: the body prefixes the naya's own name to
   # the first paccaya of each Vibhaṅgavāra, the mātikā does not
   'head_prefixes': ['Anuloma', 'Paccanīya', 'Anulomapaccanīya',
                     'Paccanīyānuloma'],
   'matika_gate': False,      # an abbreviating index — see check_colophons
 },
 '37Abhi09': {
   'title': 'Tikapaṭṭhānapāḷi',
   'label': 'Paṭṭhānapāḷi (Dutiyo bhāgo)',    # this volume's own title page
   'work': 'Abhidhamma: Paṭṭhāna',
   'first': 0,
   'matika': (3, 26),
   # THE TOP LEVEL, in printed order: the two uddesa sections, the Pucchāvāra,
   # then the five tikas this bhāga covers.
   # MEASURED off this volume's own printed headings, not carried over: the
   # bhāga opens straight at the sixth tika (36Abhi08 ends at the fifth) and
   # runs to the twenty-second, with no uddesa or Pucchāvāra of its own.
   'tops': ['6. Vitakkattika', '7. Pītittika', '8. Dassanenapahātabbattika',
            '9. Dassanenapahātabbahetukattika', '10. Ācayagāmittika',
            '11. Sekkhattika', '12. Parittattika', '13. Parittārammaṇattika',
            '14. Hīnattika', '15. Micchattaniyatattika',
            '16. Maggārammaṇattika', '17. Uppannattika', '18. Atītattika',
            '19. Atītārammaṇattika', '20. Ajjhattattika',
            '21. Ajjhattārammaṇattika', '22. Sanidassanasappaṭighattika'],
   # DEPTH BY NAME, and why `mids` is not enough here.  The Paṭṭhāna nests four
   # deep under a tika and prints 1477 headings in this volume alone; `mids`
   # gives exactly two levels, so ~1400 of them would land as ONE FLAT LIST
   # under their vāra — the shape the user reported on this very sidebar.
   # Each level below is a closed set of names the edition reuses at that depth
   # throughout the Paṭṭhāna, so the same table should serve 37-40 (to be
   # measured, not assumed).  A heading in none of the sets is a leaf at the
   # current depth, which is what the enumeration heads (Tika, Catukka,
   # Hetuduka …) are.
   'levels': [
     None,                                             # level 0 = 'tops'
     ['1. Paṭiccavāra', '2. Sahajātavāra', '3. Paccayavāra',
      '4. Nissayavāra', '5. Saṁsaṭṭhavāra', '6. Sampayuttavāra',
      '7. Pañhāvāra'],
     ['1. Paccayānuloma', '2. Paccayapaccanīya',
      '3. Paccayānulomapaccanīya', '4. Paccayapaccanīyānuloma'],
     ['1. Vibhaṅgavāra', '2. Saṅkhyāvāra', 'Saṅkhyāvāra',
      'Pañhāvāra-paccanīyuddhāra', '2. Paccanīyuddhāra',
      'Gaṇanā hetumūlakā', 'Gaṇanamūlaka'],
   ],
   # see the comment at the matcher: the body prefixes the naya's own name to
   # the first paccaya of each Vibhaṅgavāra, the mātikā does not
   'head_prefixes': ['Anuloma', 'Paccanīya', 'Anulomapaccanīya',
                     'Paccanīyānuloma'],
   'matika_gate': False,      # an abbreviating index — see check_colophons
 },
 '38Abhi10': {
   'title': 'Dukapaṭṭhānapāḷi',
   'label': 'Paṭṭhānapāḷi (Tatiyo bhāgo)',     # this volume's own title page
   'work': 'Abhidhamma: Paṭṭhāna',
   'first': 0,
   'matika': (3, 5),
   # MEASURED: the volume's top level is the gocchakas and the two "antara"
   # groups, in printed order, and it prints "6-7. Oghayogagocchaka" as ONE
   # node for two.
   'tops': ['1. Hetugocchaka', '2. Cūḷantaraduka', '3. Āsavagocchaka',
            '4. Saññojanagocchaka', '5. Ganthagocchaka',
            '6-7. Oghayogagocchaka', '8. Nīvaraṇagocchaka',
            '9. Parāmāsagocchaka', '10. Mahantaraduka', '11. Upādānagocchaka'],
   'levels': [
     None,                                       # level 0 = 'tops'
     ['re:\\d+(-\\d+)?\\.\\s+\\S+duka$'],           # the 74 numbered dukas
     ['1. Paṭiccavāra', '2. Sahajātavāra', '3. Paccayavāra',
      '4. Nissayavāra', '5. Saṁsaṭṭhavāra', '6. Sampayuttavāra',
      '7. Pañhāvāra', '1-7. Vārasattaka'],
     ['1. Paccayānuloma', '2. Paccayapaccanīya',
      '3. Paccayānulomapaccanīya', '4. Paccayapaccanīyānuloma',
      '1. Paccayānulomādi', '1-4. Paccayacatukka'],
     ['1. Vibhaṅgavāra', '2. Saṅkhyāvāra', 'Saṅkhyāvāra',
      '2. Paccanīyuddhāra', 'Pañhāvāra-paccanīyuddhāra'],
   ],
   'head_prefixes': ['Anuloma', 'Paccanīya', 'Anulomapaccanīya',
                     'Paccanīyānuloma'],
   'matika_gate': False,      # an abbreviating index — see check_colophons
 },
 '39Abhi11': {
   'title': 'Dukapaṭṭhānapāḷi',
   'label': 'Paṭṭhānapāḷi (Catuttho bhāgo)',   # this volume's own title page
   'work': 'Abhidhamma: Paṭṭhāna',
   'first': 0,
   'matika': (3, 8),
   'tops': [],
   # THREE BOOKS, each with its own title page, homage and structure.  The
   # ordinal bounds are the corpus `book` field's, confirmed against the title
   # pages at 0-based 203 and 475.
   #
   # Books 2 and 3 cross a duka with a tika, so their TOP level is an open set
   # the edition names one by one — 111 and 77 of them — and is given as a
   # PATTERN.  Which of the two is on top is the difference between the books
   # and is read off their names: Dukatika puts the duka above, Tikaduka the
   # tika.
   'books': [
     {'title': 'Dukapaṭṭhānapāḷi', 'lo': 0, 'hi': 658,
      'tops': ['12. Kilesagocchaka', '13. Piṭṭhiduka'],
      'levels': [None,
        ['re:\\d+(-\\d+)?\\.\\s+\\S+duka$'],
        ['1. Paṭiccavāra', '2. Sahajātavāra', '3. Paccayavāra',
        '4. Nissayavāra', '5. Saṁsaṭṭhavāra', '6. Sampayuttavāra',
        '7. Pañhāvāra', '1-7. Vārasattaka', '1-7. Paṭiccādivāra',
        're:\\d+(-\\d+)?\\.\\s+\\S*vāra\\b'],
        ['1. Paccayānuloma', '2. Paccayapaccanīya',
        '3. Paccayānulomapaccanīya', '4. Paccayapaccanīyānuloma',
        '1. Paccayānulomādi', '1-4. Paccayacatukka'],
        ['1. Vibhaṅgavāra', '2. Saṅkhyāvāra', 'Saṅkhyāvāra',
        '2. Paccanīyuddhāra', 'Pañhāvāra-paccanīyuddhāra']]},
     {'title': 'Dukatikapaṭṭhānapāḷi', 'lo': 658, 'hi': 2266,
      'tops': ['re:\\d+(-\\d+)?\\.\\s+\\S+duka$'],
      'levels': [None,
        ['re:\\d+(-\\d+)?\\.\\s+\\S+ttika$'],
        ['re:\\d+(-\\d+)?\\.\\s+\\S+pada$'],
        ['1. Paṭiccavāra', '2. Sahajātavāra', '3. Paccayavāra',
        '4. Nissayavāra', '5. Saṁsaṭṭhavāra', '6. Sampayuttavāra',
        '7. Pañhāvāra', '1-7. Vārasattaka', '1-7. Paṭiccādivāra',
        're:\\d+(-\\d+)?\\.\\s+\\S*vāra\\b'],
        ['1. Paccayānuloma', '2. Paccayapaccanīya',
        '3. Paccayānulomapaccanīya', '4. Paccayapaccanīyānuloma',
        '1. Paccayānulomādi', '1-4. Paccayacatukka']]},
     {'title': 'Tikadukapaṭṭhānapāḷi', 'lo': 2266, 'hi': 2985,
      'tops': ['re:\\d+(-\\d+)?\\.\\s+\\S+ttika$'],
      'levels': [None,
        ['re:\\d+(-\\d+)?\\.\\s+\\S+duka$'],
        ['re:\\d+(-\\d+)?\\.\\s+\\S+pada$'],
        ['1. Paṭiccavāra', '2. Sahajātavāra', '3. Paccayavāra',
        '4. Nissayavāra', '5. Saṁsaṭṭhavāra', '6. Sampayuttavāra',
        '7. Pañhāvāra', '1-7. Vārasattaka', '1-7. Paṭiccādivāra',
        're:\\d+(-\\d+)?\\.\\s+\\S*vāra\\b'],
        ['1. Paccayānuloma', '2. Paccayapaccanīya',
        '3. Paccayānulomapaccanīya', '4. Paccayapaccanīyānuloma',
        '1. Paccayānulomādi', '1-4. Paccayacatukka']]},
   ],
   'head_prefixes': ['Anuloma', 'Paccanīya', 'Anulomapaccanīya',
                     'Paccanīyānuloma'],
   'matika_gate': False,      # an abbreviating index — see check_colophons
 },
 '40Abhi12': {
   'title': 'Paṭṭhānapāḷi (Pañcamo bhāgo)',
   'label': 'Paṭṭhānapāḷi (Pañcamo bhāgo)',   # this volume's own title page
   'work': 'Abhidhamma: Paṭṭhāna',
   'first': 0,
   # NO SECTION MĀTIKĀ IS PRINTED IN THIS VOLUME.  Its four pages of front
   # matter carry the cover, the imprint, the Pāḷi alphabet table and ONE
   # mātikā page — and that page lists the twenty BOOKS with their printed
   # page ranges and nothing below them.  So the entry-level check has nothing
   # to run on and the book-level one has a real second input.
   'matika': None,
   'book_matika': (3, 3),
   # THE TEXT EXTENT THE PDF ITSELF DECLARES:
   # "[450 pages = content 4 + text 442 + index 4]" -> 1-based 5-446.
   'text': (4, 445),
   'pairsides': True,
   # the one heading pair whose second half carries no full stop after its
   # number (printed p48); `split_centre` names the same line
   'pair_literals': {
     '1. Hetuduka 19-53 Saññojanādiduka':
         ('1. Hetuduka', '19-53. Saññojanādiduka'),
   },
   # TWENTY BOOKS: the last two of the Dhammānuloma and all six of each of the
   # other three nayas.  Ordinal bounds are the ones the body build measured
   # from the HOMAGE PAGES (the corpus `book` field is wrong in this volume);
   # the printed page ranges are this volume's own mātikā, and the build checks
   # the two against each other.
   'books': [
     _bk('Dhammānuloma',          'Tikatika',    0,  190, (1, 38)),
     _bk('Dhammānuloma',          'Dukaduka',  190,  335, (39, 61)),
     _bk('Dhammapaccanīya',       'Tika',      335,  392, (63, 72)),
     _bk('Dhammapaccanīya',       'Duka',      392,  504, (73, 104)),
     _bk('Dhammapaccanīya',       'Dukatika',  504,  614, (105, 121)),
     _bk('Dhammapaccanīya',       'Tikaduka',  614,  725, (123, 138)),
     _bk('Dhammapaccanīya',       'Tikatika',  725,  828, (139, 157)),
     _bk('Dhammapaccanīya',       'Dukaduka',  828,  908, (159, 172)),
     _bk('Dhammānulomapaccanīya', 'Tika',      908,  986, (173, 195)),
     _bk('Dhammānulomapaccanīya', 'Duka',      986, 1068, (197, 213)),
     _bk('Dhammānulomapaccanīya', 'Dukatika', 1068, 1265, (215, 244)),
     _bk('Dhammānulomapaccanīya', 'Tikaduka', 1265, 1509, (245, 288)),
     _bk('Dhammānulomapaccanīya', 'Tikatika', 1509, 1592, (289, 305)),
     _bk('Dhammānulomapaccanīya', 'Dukaduka', 1592, 1716, (307, 325)),
     _bk('Dhammapaccanīyānuloma', 'Tika',     1716, 1764, (327, 336)),
     _bk('Dhammapaccanīyānuloma', 'Duka',     1764, 1826, (337, 347)),
     _bk('Dhammapaccanīyānuloma', 'Dukatika', 1826, 2020, (349, 375)),
     _bk('Dhammapaccanīyānuloma', 'Tikaduka', 2020, 2173, (377, 401)),
     _bk('Dhammapaccanīyānuloma', 'Tikatika', 2173, 2299, (403, 423)),
     _bk('Dhammapaccanīyānuloma', 'Dukaduka', 2299, 2413, (425, 442)),
   ],
   'head_prefixes': ['Anuloma', 'Paccanīya', 'Anulomapaccanīya',
                     'Paccanīyānuloma'],
   'matika_gate': False,
 },
}

# THE ABSOLUTE NUMBER IN PARENTHESES IS PART OF THE ENTRY, not noise.  32Abhi04
# sets every kathā in both the mātikā and the body as "(10) 1. Parūpahārakathā"
# — the kathā's number in the whole book, then its number within its vagga — and
# without the optional group below the mātikā reader saw only 45 of its ~250
# entries.  Kept in the entry text, because the BODY keeps it too, so the two
# fold equal.
# !!! THE DOT LEADERS ARE OPTIONAL, BECAUSE ON A LONG ENTRY THE PAGE HAS NO
# ROOM FOR THEM.  06VinSg06 sets
#     `17. Mañcapīṭhādisaṁghikasenāsanesu paṭipajjitabbavinicchayakathā 86`
# with the folio hard against the title and no leaders at all, so requiring
# them dropped a real entry and the heads-vs-mātikā diff then reported that
# volume's own heading as "not in the mātikā".
# MEASURED over every volume that declares a mātikā range (29 of them):
# exactly NINE lines are added and every one is an entry whose title is too
# long for leaders — 03Vin03 x4, 04Vin04 x2, 15An01 x3 (three Ekakanipāta
# vaggas that were silently absent from that shipped volume's mātikā side).
# No other shape appeared.  Probe: `_fnprobe/matwiden.py`.
# !!! THE DOTTED LEADER IS NOT ALWAYS THREE DOTS.  12MaA03's mātikā sets it as
# FOUR — `1. Kandarakasuttavaṇṇanā       ....   ....      1` — so a leader
# written `(?:\.\.\.\s+)*` consumed three dots and then demanded whitespace
# where the fourth dot stood, and not ONE of that volume's 51 dotted entries
# matched.  The nav reported "mātikā lists 5" (its centred vagga heads alone)
# and every dotted entry was reported as a body heading the mātikā does not
# list, which is the exact inverse of the truth.  A gate that finds nothing is
# indistinguishable from a gate that passes.
# The change can only ADD entries, never remove one, so the risk runs the other
# way: a volume passing today could start failing on entries it had never been
# asked to resolve.  MEASURED OVER ALL 32 VOLUMES THAT DECLARE A `matika`
# RANGE in any nav SPEC in the repo (`_maa03/matregex.py`) — Vinaya, Dīgha,
# Majjhima, Saṁyutta, Aṅguttara, Abhidhamma and the four commentary volumes —
# **every one is entry-for-entry identical, +0 -0**.  Inert everywhere but the
# volume that needed it.
MAT = re.compile(r'^\s*((?:\(\d+(?:-\d+)?\)\s*)?(?:\d+(?:-\d+)?\.\s+)?)'
                 r'([A-ZĀĪŪṄÑṆṬḌḶ][^.]*?)\s+(?:\.{3,}\s+)*\d+\s*$')
# A CENTRED GROUP HEAD'S INDENT IS A FUNCTION OF ITS LENGTH, so the threshold
# is a per-volume measurement and not a constant.  18 is right for the
# Abhidhamma; 03Vin03 sets '3. Vassūpanāyikakkhandhaka' at 17 and 05Vin05
# 'Samuṭṭhānasīsasaṅkhepa' at 16, purely because those names are longer.
# Measured at 14 over every volume that prints a mātikā: it adds exactly those
# three lines in the Vinaya and would add 130 in the Abhidhamma — the printed
# TWO-COLUMN pair-lines, which are not group heads — so it is declared per
# volume (`centred_indent`) and left at 18 everywhere else.
CENTRED_SRC = r'^\s{%d,}((?:\d+\.\s+)?[A-ZĀĪŪṄÑṆṬḌḶ]\S*(?:\s+\S+)*?)\s*$'
CENTRED = re.compile(CENTRED_SRC % 18)


def fold(s):
    return re.sub(r'[^0-9a-zāīūṁṃṅñṇṭḍḷ]', '', s.lower())


# TWO HEADINGS ON ONE PRINTED LINE, AND WHICH HALF IS WHICH.
#
# `split_centre` in build_khu_volume.py splits such a line into two headings
# and emits them left-then-right, but it does not record which half a heading
# came from — and for a CROSSED book that position is the whole structure.
# 40Abhi12's Tikatika crosses a tika with a tika and its Dukaduka a duka with
# a duka, so a `re:` pattern for the top level matches BOTH halves and every
# inner section would open a new top, flattening the tree.  The printed pair
# "1. Kusalattika   1. Vedanāttika" carries the distinction only in its
# POSITION on the line.
#
# So the position is read back off the PRINTED PAGE here rather than by
# changing `split_centre`, which feeds every volume's side-maps.  The rule the
# page states is general: ON A TWO-HEADING LINE THE LEFT HALF STANDS ONE LEVEL
# ABOVE THE RIGHT.  Measured on 40Abhi12: 696 such lines, and the heads stream
# reproduces all 696 in order with none left over — two readings of the same
# edition agreeing exactly, which is why the builder REFUSES if any printed
# pair-line cannot be found in the stream.
_PNUM = r'\d+(?:-\d+)?\.'
PAIR1 = re.compile(r'^(%s\s+\S[^\s].*?)\s{3,}(%s\s+\S.*)$' % (_PNUM, _PNUM))
PAIR2 = re.compile(r'^([A-ZĀĪŪṄÑṆṬḌḶ]\S*(?:\s+\S+){0,3}?)\s{3,}'
                   r'(%s\s+\S.*)$' % _PNUM)


def pair_lines(pages, p0, p1, lit):
    """Every centred line the edition sets as TWO headings, in printed order.

    Mirrors `split_centre`'s two forms (numbered|numbered and, for the volumes
    that declare `split_unnumbered`, unnumbered|numbered) plus the literals it
    names.  A running header has the same two-name shape and is told apart by
    the PRINTED PAGE NUMBER it carries at the far margin.
    """
    out = []
    for pi in range(p0, p1 + 1):
        for l in pages[pi].split('\n'):
            t = l.strip()
            if not t or len(l) - len(l.lstrip()) < 6:
                continue
            k = re.sub(r'\s+', ' ', t)
            if k in lit:
                out.append((lit[k][0], lit[k][1], pi))
                continue
            m = PAIR1.match(t) or PAIR2.match(t)
            if not m:
                continue
            a, b = m.group(1).strip(), m.group(2).strip()
            if re.search(r'\d$', b):
                continue                  # a running header's page number
            if a.endswith('.') or b.endswith('.'):
                continue                  # a colophon, not a heading
            if len(a.split()) > 6 or len(b.split()) > 6:
                continue
            out.append((a, b, pi))
    return out


def mark_rights(heads, pl):
    """Align the printed pair-lines against the heads stream, in LOCKSTEP.

    Returns the set of positions in `heads` that are the RIGHT half of a
    printed pair-line, and how many pair-lines were consumed.  Strict
    lockstep — the next pair-line must be the next same-ordinal adjacent pair
    in the stream — so the count is a real check and not a search that can
    always be satisfied.
    """
    rights, j = set(), 0
    for i in range(len(heads) - 1):
        if j >= len(pl):
            break
        if heads[i][1] != heads[i + 1][1]:
            continue
        if pl[j][0] == heads[i][0] and pl[j][1] == heads[i + 1][0]:
            rights.add(i + 1)
            j += 1
    return rights, j


def matika_headers(pages, p0, p1):
    """The mātikā's OWN running header, measured from its pages.

    36Abhi08 heads every mātikā page "Paṭṭhānapāḷi paṭhamabhāga" and its first
    page with that title split over two lines.  Neither contains the BOOK's
    name ("Tikapaṭṭhānapāḷi"), so the `fold(title)` filter did not see them and
    four header lines entered the entry list.  That is not cosmetic: the entry
    list is matched against the tree with a FORWARD-ONLY pointer, so one
    unmatchable entry strands every real entry after it — which is why
    "Gaṇanā hetumūlakā" and "Na-anantara nasamanantara" were reported absent
    from the tree while sitting in `sections/36Abhi08.json` all along.

    Measured, not declared: a line that opens three or more of these pages is
    the header.  Its individual words are then also dropped, which is what
    takes out the title page's own two lines — they are the same stack broken
    across lines, and nothing else in a mātikā is a bare word of the title.
    """
    seen = {}
    for pi in range(p0, p1 + 1):
        top = [x.strip() for x in pages[pi].split('\n') if x.strip()][:2]
        for t in top:
            k = fold(re.sub(r'\b[ivxl]+\b', '', t.lower()))
            if k:
                seen.setdefault(k, set()).add(pi)
    hdr = {k for k, v in seen.items() if len(v) >= 3}
    return hdr, ''.join(sorted(hdr))


def matika_lines(pages, p0, p1, title, cmin=18):
    """The printed mātikā, in order, as (entry, is_centred).

    THE TWO KINDS ARE NOT THE SAME WITNESS.  A dotted entry may be finer
    than the body — every Vinaya volume lists analytic entries the body
    never heads (`Paṭhamapaññatti`, `Sikkhāpadavibhaṅga, padabhājanīya`) —
    but a CENTRED line is a group head, and those are exactly the body's
    structural headings.  Kept apart so a volume whose entries cannot be a
    gate can still gate on its centred lines (`matika_centred_gate`).
    """
    out = []
    cen_re = CENTRED if cmin == 18 else re.compile(CENTRED_SRC % cmin)
    hdr, hdrall = matika_headers(pages, p0, p1)
    for pi in range(p0, p1 + 1):
        for l in pages[pi].split('\n'):
            t = l.strip()
            if not t or t.startswith('Mātikā ') or t.startswith('Piṭṭhaṅka'):
                continue
            f = fold(re.sub(r'\b[ivxl]+\b', '', t.lower()))
            if f and (f in hdr or (len(f) > 3 and f in hdrall)):
                continue                       # the mātikā's own running header
            if 'niṭṭhitā' in t or fold(title) in fold(t):
                continue                       # the running page-header
            # ...AND A RUNNING HEADER MAY CARRY A ROMAN FOLIO INSTEAD OF AN
            # ARABIC ONE.  33Abhi05's mātikā runs eight pages over five books
            # and heads each with that book's name, so `matika_headers`' "opens
            # three or more pages" test cannot see them; the odd pages set the
            # folio at the FAR margin ("Khandhayamakapāḷi        iii"), which
            # `CENTRED` then reads as one entry.  A dotted entry always ends in
            # an ARABIC page number, so requiring no leaders keeps every real
            # one.  (The even pages set the folio at the LEFT margin, which
            # `CENTRED`'s 18-space opener already excludes.)
            if re.search(r'\s{3,}[ivxl]+\s*$', l) and '...' not in l:
                continue
            m = MAT.match(l)
            if m:
                out.append((((m.group(1) or '') + m.group(2)).strip(), False))
                continue
            c = cen_re.match(l)
            if c and not re.search(r'\d\s*$', c.group(1)):
                out.append((c.group(1).strip(), True))
    return out


def matika(pages, p0, p1, title):
    """The printed mātikā's entries, in order."""
    return [t for t, _c in matika_lines(pages, p0, p1, title)]


def book_matika(pages, p0, p1):
    """40Abhi12's mātikā lists its twenty BOOKS, grouped under centred naya
    heads, each with the printed pages it occupies:

        Dhammānuloma
        Tikatikapaṭṭhānapāḷi        ...   ...     1-38

    That is a second printed witness to the volume's book division — the
    boundaries themselves were measured from the twenty HOMAGE PAGES — so it
    is read here and compared, entry for entry and page for page.
    """
    out, naya = [], None
    for pi in range(p0, p1 + 1):
        for l in pages[pi].split('\n'):
            t = l.strip()
            if not t or t.startswith('Mātikā') or t.startswith('Piṭṭhaṅka'):
                continue
            m = re.match(r'^(\S+paṭṭhānapāḷi)\s+(?:\.\.\.\s+)+'
                         r'(\d+)\s*-\s*(\d+)\s*$', t)
            if m:
                out.append(('%s %s' % (naya, m.group(1)),
                            int(m.group(2)), int(m.group(3))))
                continue
            if re.match(r'^Dhamm\S+$', t):
                naya = t
    return out


def printed_heads(vol):
    """Every printed heading in printed order, as (label, ordinal).

    From BOTH side-maps: `sections/` holds the headings set above a numbered
    unit, `uddana/` plain-block `head` fields those set after one.

    A `sections` entry is a heading only if it is NEITHER display verse NOR
    printed prose.  k:'prose' joined k:'gatha' as a non-heading kind when the
    pre-first-unit emitter learned to tell the two apart (2026-08-03); without
    this skip a prose paragraph printed above a book's first unit — 20KhuA01's
    `Ayaṁ saraṇagamananiddeso Khuddakānaṁ ādi.` — would enter the tree as a
    nav node.
    """
    S = json.load(open(os.path.join(ROOT, 'site/reader/sections', vol + '.json'),
                       encoding='utf-8'))
    U = json.load(open(os.path.join(ROOT, 'site/reader/uddana', vol + '.json'),
                       encoding='utf-8'))
    out = []
    for k in sorted(set(S) | set(U), key=int):
        for e in S.get(k, []):
            if e.get('k') in ('gatha', 'prose', 'booktitle'):
                continue
            out.append((e['l'], int(k)))
        for b in U.get(k, []):
            if b.get('head'):
                out.append((b['head'], int(k)))
    return out


def colophon_ords(vol):
    """Every centred closing line with the ORDINAL it is anchored to."""
    out = []
    U = json.load(open(os.path.join(ROOT, 'site/reader/uddana', vol + '.json'),
                       encoding='utf-8'))
    for k in sorted(U, key=int):
        for b in U[k]:
            if b.get('plain'):
                continue
            for l in b.get('lines', ()):
                if l.strip():
                    out.append((int(k), l.strip()))
    S = json.load(open(os.path.join(ROOT, 'site/reader/sections',
                                    vol + '.json'), encoding='utf-8'))
    for k in sorted(S, key=int):
        for e in S[k]:
            if e.get('k') == 'gatha':
                for l in str(e.get('l', '')).split('\n'):
                    if l.strip():
                        out.append((int(k), l.strip()))
    return out


def check_book_colophons(vol, sp):
    """THE EDITION'S OWN BOOK-CLOSING LINES, read against the book division.

    A naya x paṭṭhāna book closes "Dhammānulome Tikatikapaṭṭhānaṁ niṭṭhitaṁ."
    — it names both the naya and the paṭṭhāna, so it is a THIRD printed witness
    to a division that was measured from the homage pages and checked against
    the mātikā.  The edition does not close every book this way, so the test
    runs FROM the colophons it does print: each must fall inside the ordinal
    range of the book it names, and nowhere else.
    """
    co = colophon_ords(vol)
    closed, bad = 0, []
    for bk in sp['books']:
        if not bk.get('naya'):
            continue
        want = '%se %spaṭṭhānaṁ niṭṭhitaṁ.' % (bk['naya'][:-1], bk['kind'])
        hits = [o for o, l in co if l == want]
        if not hits:
            continue
        closed += 1
        outside = [o for o in hits if not (bk['lo'] <= o < bk['hi'])]
        if outside or len(hits) > 1:
            bad.append((want, hits, bk['lo'], bk['hi']))
    return closed, bad


def colophons(vol):
    """Every centred closing line the body prints, from BOTH side-maps.

    `uddana/` holds the colophons set after a numbered unit; `sections/` holds,
    as k:'gatha', the ones printed before a book's first unit — which is where
    "Paccayuddeso." lives, and reading only the first map made this check
    report the volume's own opening section as never closed.
    """
    out = []
    U = json.load(open(os.path.join(ROOT, 'site/reader/uddana', vol + '.json'),
                       encoding='utf-8'))
    for k in sorted(U, key=int):
        for b in U[k]:
            if b.get('plain'):
                continue
            for l in b.get('lines', ()):
                out.append(l.strip())
    S = json.load(open(os.path.join(ROOT, 'site/reader/sections', vol + '.json'),
                       encoding='utf-8'))
    for k in sorted(S, key=int):
        for e in S[k]:
            if e.get('k') == 'gatha':
                for l in str(e.get('l', '')).split('\n'):
                    out.append(l.strip())
    return [x for x in out if x]


def check_colophons(vol, sp, flat):
    """The edition's own closing lines, read AGAINST the tree.

    A colophon is the edition stating that a section has ENDED, so it is a
    second witness to the shape of the book, independent of the mātikā — the
    same input that settled 29Abhi01's Dukamātikā nesting, and unlike an index
    it cannot abbreviate.

    THE TEST RUNS FROM THE COLOPHONS, NOT FROM THE TREE, and that direction is
    the whole point.  Asking "is every node closed?" fails on sections the
    edition simply never closes — it prints no colophon for a Vibhaṅgavāra or a
    Saṅkhyāvāra, and a check that demands one is measuring its own assumption.
    Asking "does every section the edition CLOSES exist in the tree?" cannot be
    satisfied by an assumption: if the book says "Paṭiccavāro." and no
    Paṭiccavāra node exists, a printed section has been dropped.
    """
    names = list(sp.get('tops') or [])
    _lvls = [sp.get('levels')] + [b['levels'] for b in sp.get('books', [])]
    for b in sp.get('books', []):
        names += list(b['tops'])
    for lvl in _lvls:
        for lv in (lvl or [])[1:]:
            # a PATTERN names no section, so there is nothing to look for
            names += [x for x in (lv or ()) if not str(x).startswith('re:')]
    names = [x for x in dict.fromkeys(names) if not str(x).startswith('re:')]
    have = {fold(re.sub(r'^\d+\.\s*', '', x)) for x in flat}
    closed, unclosed, missing = [], [], []
    colo = colophons(vol)
    for w in names:
        stem = fold(re.sub(r'^\d+\.\s*', '', w))
        base = stem[:-1] if stem else stem
        # a colophon inflects the name it closes: Paṭiccavāra -> "Paṭiccavāro.",
        # Kusalattika -> "Kusalattikaṁ niṭṭhitaṁ."
        if base and any(fold(c).startswith(base) for c in colo):
            closed.append(w)
            if stem not in have:
                missing.append(w)
        else:
            unclosed.append(w)
    return colo, closed, unclosed, missing


def main():
    vol = sys.argv[1]
    sp = SPEC[vol]
    title = sp['title']
    # THE VOLUME MAY NOT BE IN `pali-unicode`.  Same three-folder search
    # `build_khu_volume.use()` and `scout_volume.py` already carry — without it
    # a commentary volume's nav builds against an empty page list and every
    # mātikā gate silently reports zero.
    pdf = next((_p for _d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode')
                for _p in [os.path.join(ROOT, _d, vol + '.pdf')]
                if os.path.exists(_p)),
               os.path.join(ROOT, 'pali-unicode', vol + '.pdf'))
    pages = subprocess.run(['pdftotext', '-layout', pdf, '-'],
                           capture_output=True, text=True).stdout.split('\f')
    npara = len(json.load(open(os.path.join(ROOT, 'site', vol + '.json'),
                               encoding='utf-8'))['paragraphs'])

    heads = printed_heads(vol)

    # A DECLARED `head_skip` LITERAL MUST BE PRINTED.  A skip list that no
    # longer matches the page would silently stop skipping — or, worse, would
    # look like it was still doing something.  It is a measurement of the
    # edition, so it is checked against the edition.
    for _lit in sp.get('head_skip', ()):
        _n = sum(1 for _l, _o in heads if _l == _lit)
        print('    head_skip %r: printed %d time(s)' % (_lit, _n))
        if not _n:
            print('    REFUSED — head_skip %r is not printed in this volume'
                  % _lit)
            sp['_fail'] = True

    # WHICH HEADINGS ARE THE RIGHT HALF OF A PRINTED PAIR-LINE.  Read off the
    # page, aligned in lockstep against the heads stream, and REFUSED if the
    # two readings do not agree entirely.
    rights = set()
    if sp.get('pairsides'):
        pl = pair_lines(pages, sp['text'][0], sp['text'][1],
                        sp.get('pair_literals', {}))
        rights, used = mark_rights(heads, pl)
        print('    pair-lines: %d printed, %d aligned in the heads stream '
              '(%d right halves)' % (len(pl), used, len(rights)))
        if used != len(pl):
            print('    REFUSED — printed pair-line %d of %d is not in the '
                  'heads stream: %r | %r (0-based page %d)'
                  % (used + 1, len(pl), pl[used][0], pl[used][1], pl[used][2]))
            sp['_fail'] = True
    heads = [(l, o, i in rights) for i, (l, o) in enumerate(heads)]

    def subtree(hs, tops, levels):
        """One book's tree.  `tops` is an ordered sequence consumed in printed
        order, or a single 're:' PATTERN when the top level is an open set —
        which it is for the Dukatika and Tikaduka paṭṭhānas, whose tops are the
        hundred-odd numbered dukas and tikas the edition names one by one.
        """
        pat = (tops[0][3:] if len(tops) == 1 and str(tops[0]).startswith('re:')
               else None)
        tops = list(tops)
        tree, stack, gi, reprints = [], [], 0, 0
        # A DECLARED LEVEL KEEPS THE DEPTH IT WAS FIRST GIVEN UNDER ITS TOP.
        #
        # `levels` is a table of DEPTHS, and every shipped volume's book has a
        # uniform one — a gocchaka holds dukas holds vāras holds catukkas, the
        # same number of rungs everywhere — so `min(hit, len(stack))` never
        # actually clamps and this memo is inert.  33Abhi05 is the first book
        # whose two halves are NOT the same depth: the Yamaka sets six vāras
        # ("1. Paccuppannavāra" … "6. Atītānāgatavāra") THREE rungs down under
        # "2. Pavatti" (Pavatti > Uppādavāra > Paccuppannavāra) and TWO rungs
        # down under "3. Pariññāvāra", which has no middle rung at all.
        #
        # Declared at the deeper level the first Pariññāvāra vāra clamps to the
        # right place and the next five nest INSIDE it, one per rung, six deep;
        # declared at the shallower one Pavatti's vāras become siblings of
        # their own parent.  Neither is what the page prints.  So the clamp is
        # REMEMBERED: the first vāra under Pariññāvāra clamps to depth 1 and
        # its five siblings are placed at depth 1 too, while under Pavatti the
        # same level is placed at 2 and stays there.  The memo is cleared at
        # every new top and truncated above whatever level was just placed.
        # Gated per volume; 29Abhi01/30Abhi02/31Abhi03/32Abhi04 and 36-40 all
        # rebuild byte-identical with it on, which is what "inert" means here.
        memo = {}
        remember = sp.get('level_memo')
        # A DIVISION'S NAME REPRINTED OVER EACH OF ITS PARTS, where the fold
        # test cannot see it.  `subtree` already skips an ancestor reprint —
        # that is how 01Vin01's vagga name, printed again over each of its ten
        # sikkhāpadas, becomes 27 skips and not 27 rows.  02Vin02 prints the
        # same kind of reprint for a name that is NOT on the stack and does not
        # fold equal to the node it names: the body sets 'Bhikkhunivibhaṅge'
        # (locative, short i) above five of the Bhikkhunīvibhaṅga's seven
        # kaṇḍas, where the division's own title page reads 'Bhikkhunīvibhaṅga'.
        # Named per volume rather than reached by normalising ī to i, which
        # would fold together names the edition keeps apart.  Every declared
        # literal must actually be printed — checked below, so it cannot rot.
        skips = set(sp.get('head_skip', ()))

        def place(node, depth):
            del stack[depth:]
            (stack[-1]['kids'] if stack else tree).append(node)
            stack.append(node)

        prev = -1          # the depth the PREVIOUS heading was placed at
        for lab, ordi, right in hs:
            if lab in skips:
                reprints += 1
                continue
            node = {'label': lab, 'key': '%s#%d' % (vol, ordi), 'kids': []}
            anc = next((d for d, x in enumerate(stack)
                        if fold(lab) == fold(x['label'])), None)
            # THE RIGHT HALF OF A PRINTED PAIR-LINE STANDS ONE LEVEL BELOW THE
            # LEFT.  This is the only thing that can separate the two levels of
            # a CROSSED book, where both halves are the same kind of section
            # and so match the same pattern.  Gated per volume (`pairsides`):
            # it would move 36Abhi08, whose page sets "Pucchāvāra
            # 1. Paccayānuloma" on one line while its measured level table puts
            # Ekamūlaka between them, and that volume is shipped and gated.
            if right and prev >= 0:
                place(node, min(prev + 1, len(stack)))
                prev = len(stack) - 1
                continue
            if pat is not None:
                # AN ANCESTOR REPRINTED IS NOT A NEW TOP.  The Paṭṭhāna
                # reprints the outer section's name at the head of every inner
                # one, and with an open (`re:`) top level that reprint matched
                # the pattern and opened a duplicate top: 39Abhi11 shipped with
                # "1. Hetuduka" twenty-two times and "1. Kusalattika"
                # fifty-two times in its sidebar.  The reprint test therefore
                # runs BEFORE the top test wherever the top level is a pattern.
                if anc is not None:
                    reprints += 1; prev = anc
                    continue
                if re.match(pat, lab):
                    place(node, 0); gi = len(tops); prev = 0; memo.clear()
                    continue
            elif gi < len(tops) and fold(lab) == fold(tops[gi]):
                place(node, 0); gi += 1; prev = 0; memo.clear()
                continue
            if not stack:
                place(node, 0); prev = 0; memo.clear()
                continue
            if anc is not None:
                reprints += 1; prev = anc
                continue
            hit = None
            for d in range(1, len(levels)):
                for x in (levels[d] or ()):
                    ok = (re.match(x[3:], lab) if isinstance(x, str)
                          and x.startswith('re:') else fold(lab) == fold(x))
                    if ok:
                        hit = d
                        break
                if hit is not None:
                    break
            if hit is not None:
                d = memo.get(hit) if remember else None
                if d is None or d > len(stack):
                    d = min(hit, len(stack))
                place(node, d); prev = len(stack) - 1
                if remember:
                    memo[hit] = d
                    for _k in [_k for _k in memo if _k > hit]:
                        del memo[_k]
            else:
                stack[-1]['kids'].append(node); prev = len(stack)
        return tree, reprints, (gi >= len(tops))

    # A VOLUME MAY CARRY SEVERAL BOOKS, each with its own title page, homage
    # and structure — 39Abhi11 has three and 40Abhi12 six.  Each gets its own
    # subtree under a node labelled as the edition labels it, which is the
    # shape `group_abhidhamma_volumes.py` gave these volumes and
    # `_abhigroupverify.js` asserts.
    reprints, tops, gi = 0, list(sp.get('tops', [])), 0
    if sp.get('books'):
        _btp = os.path.join(ROOT, 'site/reader/booktitle', vol + '.json')
        _bt = json.load(open(_btp, encoding='utf-8')) if os.path.exists(_btp) else {}
        for _bk in sp['books']:
            if 'anchor' in _bk and _bt and str(_bk['anchor']) not in _bt:
                print('    REFUSED — %s: anchor %d is not a booktitle key (%s)'
                      % (_bk['title'], _bk['anchor'], sorted(_bt)))
                sp['_fail'] = True
        tree = []
        for bk in sp['books']:
            hs = [h for h in heads if bk['lo'] <= h[1] < bk['hi']]
            sub, rp, ok = subtree(hs, bk['tops'], bk['levels'])
            reprints += rp
            if not ok:
                print('    REFUSED — %s: the top level does not appear in '
                      'printed order' % bk['title'])
                sp['_fail'] = True
            # A BOOK THE EDITION DOES NOT NAME GETS NO NODE.  02Vin02's own
            # mātikā opens straight into '5. Pācittiyakaṇḍa' and prints a group
            # head only for the Bhikkhunīvibhaṅga, so the volume's top level is
            # asymmetric — four kaṇḍas, then one named division holding seven.
            # Wrapping the first part too would need a name the edition never
            # prints ('Pācittiyapāḷi' is the WHOLE volume: it heads the
            # Bhikkhunīvibhaṅga's pages as well).  Asymmetric because the
            # EDITION is asymmetric, as 32Abhi04's first vagga already is.
            if bk.get('nowrap'):
                tree.extend(sub)
            else:
                # !!! A BOOK'S `lo` MAY BE A HIDDEN ORDINAL, AND A LINK THAT
                # POINTS AT ONE RENDERS NOTHING (2026-07-29t).  Every book of
                # 03ViT03, 05ViT05 and the last four of 06ViT06 opens on its
                # TITLE PAGE, which is hidden, so `lo` is exactly the ordinal
                # the reader cannot draw — and `booktitle/` keys the first
                # VISIBLE ordinal, which is where the book's name is drawn.
                # Declared per book rather than derived, and CHECKED against
                # `booktitle/` below, which is the same anchor rule the
                # books-only Vinaya-Ṭīkā nav asserted (2026-07-28t/u).
                tree.append({'label': bk['title'],
                             'key': '%s#%d' % (vol, bk.get('anchor', bk['lo'])),
                             'kids': sub})
        gi = len(tops)
    else:
        allmids = sp.get('mids', {})
        levels = sp.get('levels')
        if levels:
            tree, reprints, ok = subtree(heads, tops, levels)
            gi = len(tops) if ok else 0
        else:
            tree, top, mid, mids, mi = [], None, None, [], 0
            for lab, ordi, _right in heads:
                node = {'label': lab, 'key': '%s#%d' % (vol, ordi), 'kids': []}
                if gi < len(tops) and fold(lab) == fold(tops[gi]):
                    tree.append(node); top, mid, gi = node, None, gi + 1
                    mids, mi = allmids.get(node['label'], []), 0
                    continue
                if top is None:
                    tree.append(node); top = node
                    mids, mi = allmids.get(node['label'], []), 0
                    continue
                if mi < len(mids) and fold(lab) == fold(mids[mi]):
                    top['kids'].append(node); mid = node; mi += 1
                    continue
                (mid or top)['kids'].append(node)
            for t, ms in allmids.items():
                got = [k['label'] for k in (next((x for x in tree
                                                  if x['label'] == t),
                                                 {'kids': []}))['kids']]
                for mm in ms:
                    if not any(fold(mm) == fold(g) for g in got):
                        print('    REFUSED — declared second level %r not '
                              'found under %r; got %s' % (mm, t, got[:6]))
                        sp['_fail'] = True

    fail = (gi < len(tops)) or sp.get('_fail', False)
    # ...and say WHICH top only when there is one to name.  With `books` the
    # volume-level `tops` is empty and the refusal has already been printed per
    # book, so indexing it raised IndexError and buried the real message.
    if gi < len(tops):
        print('    REFUSED — the top level does not appear in printed order; '
              'stopped at %r' % tops[gi])

    flat, ancs = [], []
    def walk(ns, anc=()):
        for n in ns:
            flat.append(n['label']); ancs.append(anc)
            walk(n['kids'], anc + (n['label'],))
    walk(tree)

    # THE BOOK-LEVEL MĀTIKĀ, where the volume prints one.  40Abhi12's single
    # mātikā page lists its twenty books and the printed pages each occupies,
    # so it checks the book division — which was measured from the twenty
    # homage pages — against a second printed source.
    if sp.get('book_matika'):
        bm = book_matika(pages, sp['book_matika'][0], sp['book_matika'][1])
        got = [n['label'] for n in tree]
        want = [x[0] for x in bm]
        print('    book mātikā lists %d books; the tree has %d  [%s]'
              % (len(want), len(got), 'OK' if want == got else 'CHECK'))
        if want != got:
            for a, b in zip(want + [''] * len(got), got + [''] * len(want)):
                if a != b:
                    print('    REFUSED — book mātikā %r, tree %r' % (a, b))
                    break
            fail = True
        off = sp['text'][0]          # printed page 1 is 0-based pdf page `off`
        bad = 0
        for (lab, pa, pb), bk in zip(bm, sp['books']):
            # the mātikā gives the book's own TEXT pages; the build's range
            # opens on that book's TITLE PAGE and may close on a blank leaf
            if not (bk['pg'] == (pa, pb)):
                print('    REFUSED — %s: mātikā prints %d-%d, SPEC records %s'
                      % (lab, pa, pb, bk['pg']))
                bad += 1
        if bad:
            fail = True
        else:
            print('    all %d printed page ranges agree with the mātikā '
                  '(printed p1 = 0-based pdf p%d)' % (len(bm), off))

    centred = set()
    if sp.get('matika'):
        _ml = matika_lines(pages, sp['matika'][0], sp['matika'][1], title,
                            sp.get('centred_indent', 18))
        drop = set(sp.get('matika_drop', ()))
        mat = [t for t, _c in _ml if t not in drop]
        centred = {t for t, _c in _ml if _c and t not in drop}
        # !!! THE BODY RUNS A GROUP HEAD TOGETHER WITH ITS FIRST LEAF, ON ONE
        # PRINTED LINE.  Every Sāratthadīpanī-family volume opens the first
        # pārājika `1. Paṭhamapārājika sudinnabhāṇavāravaṇṇanā` where its
        # mātikā centres `1. Paṭhamapārājika` and dots `Sudinnabhāṇavāravaṇṇanā`
        # beneath it — TWO mātikā rows against ONE body heading.
        #
        # `try_match` already matches one mātikā entry against several tree
        # labels; this is the MIRROR of that and it has no other expression.
        # The alternative — splitting the printed line into two headings — was
        # rejected: the page sets one line with one capital, and the second
        # half is printed LOWERCASE, so a split would draw a heading the
        # edition does not set.  (Contrast 07ViT07 p64, whose second half
        # carries its own NUMBER and capital; that one IS split, in
        # `build_khu_volume`'s `split_literals`.)
        #
        # Declared per volume and CHECKED: the joined form must be printed as
        # a heading, or the build refuses.  A glue rule that no longer matches
        # the page would otherwise go on silently gluing.
        glue = sp.get('matika_glue', ())
        if glue:
            _hf = {fold(h[0]) for h in heads}
            _out, _k = [], 0
            while _k < len(mat):
                if mat[_k] in glue and _k + 1 < len(mat):
                    _j = mat[_k] + ' ' + mat[_k + 1]
                    if fold(_j) not in _hf:
                        print('    REFUSED — matika_glue %r + %r gives %r, '
                              'which is not printed as a heading'
                              % (mat[_k], mat[_k + 1], _j))
                        sp['_fail'] = True
                    _out.append(_j); _k += 2
                else:
                    _out.append(mat[_k]); _k += 1
            print('    matika_glue: %d mātikā row pair(s) joined, each checked '
                  'against the printed heading' % ((len(mat) - len(_out))))
            mat = _out
    else:
        mat = []
        print('    no section mātikā is printed in this volume — the '
              'entry-level check has nothing to run on')
    era = sp.get('errata', {})

    # THE BODY NAMES THE NAYA, THE MĀTIKĀ DOES NOT.  Each Vibhaṅgavāra opens
    # its enumeration with the naya's own name in front of the first paccaya —
    # body "Anuloma hetu" and "Paccanīya nahetu" where the mātikā lists plain
    # "Hetu" and "Nahetu".  That is not an erratum and not a missing heading:
    # the prefix is the parent node's name, which the mātikā expresses by
    # setting the entry under "1. Paccayānuloma  1. Vibhaṅgavāra" instead.
    #
    # It cannot be handled by `errata`, which maps a label globally: the body
    # also prints a bare "Hetu" elsewhere, and mapping every mātikā "Hetu" to
    # "Anuloma hetu" would send the matcher to the wrong one.  So the prefix is
    # stripped on the BODY side as an ALTERNATIVE fold, tried alongside the
    # literal one.  Left unhandled it is not a cosmetic miss — the matcher is
    # forward-only, so the first mismatch sent it 170 headings down the book
    # and stranded six later entries that were present all along.
    pre = sp.get('head_prefixes', ())
    # !!! AN ERRATUM IN THE BODY IS NOT AN ERRATUM IN THE MĀTIKĀ, and `errata`
    # cannot express the difference: it rewrites a mātikā entry GLOBALLY, which
    # is right when the misprint occurs once on each side (31Abhi03) and wrong
    # when the same heading is printed several times and only ONE printing is
    # misspelt.  35Abhi07 heads the Pariññāvāra's fourth vāra
    # "4. Paccuppannātītivāra" on p328 and "4. Paccuppannātītavāra" on p28,
    # p50, p71 and p229; its mātikā sets the correct form five times.  Rewritten
    # globally, all five mātikā entries matched only the misprinted node — and
    # the pointer, which is forward-only, jumped 195 sections into the NEXT book
    # and stranded 71 entries behind it.
    # So the alternative belongs on the TREE side: the misprinted label ALSO
    # folds as the form the mātikā uses, through the same slot `head_prefixes`
    # already uses, and the four correct printings keep matching literally.
    bera = sp.get('body_errata', {})

    def folds(lab):
        out = [fold(lab)]
        if lab in bera:
            f = fold(bera[lab])
            if f and f not in out:
                out.append(f)
        for x in pre:
            if lab.lower().startswith(x.lower() + ' '):
                f = fold(lab[len(x):])
                if f and f not in out:
                    out.append(f)
        return out

    def run_gate(mat, flat, ancs):
        """One pass of the mātikā gate over ONE stream of tree labels.

        Lifted out of `main` unchanged so it can be run PER BOOK — see the
        segmentation below.  With one segment it is the same scan it always
        was, over the same `flat`, and every shipped volume rebuilds
        byte-identical.
        """
        i, missing, compound = 0, [], 0
        alt = [folds(x) for x in flat]

        # THE MATCH, AND WHY IT IS TWO QUESTIONS AND NOT ONE.
        #
        # "Is any printed section missing from the tree?" and "does the mātikā run
        # in the same order as the body?" were one forward-only scan.  On this
        # volume that conflates them destructively: the mātikā reuses bare paccaya
        # names (Hetu, Ārammaṇa, Adhipati …) at every one of the ~40 vāra sections,
        # so a single mismatch does not just miss — the pointer lands on the NEXT
        # section's copy of the name and every later entry is measured from the
        # wrong place.  That is how six entries were reported absent while sitting
        # in `sections/36Abhi08.json` all along.
        #
        # So each entry is now searched from the pointer first and, failing that,
        # from the start; a hit behind the pointer is counted as OUT OF ORDER, not
        # as missing, and the pointer does not follow it.  Only a hit found nowhere
        # is missing, and only that refuses the write.
        def try_match(fm, start, allow_pre):
            for x in range(start, len(flat)):
                acc = ''
                for k in range(x, min(x + 3, len(flat))):
                    f = alt[k][0]
                    if (allow_pre and len(alt[k]) > 1
                            and not fm.startswith(acc + f)):
                        f = alt[k][1]
                    acc += f
                    if acc == fm:
                        return k, k > x
                    if not fm.startswith(acc):
                        break
            return None, False

        outoforder = 0
        # !!! THE MĀTIKĀ REPRINTS AN ANCESTOR'S NAME EXACTLY AS THE BODY DOES, and
        # the tree has no node for a reprint — `subtree` skips it.  `head_prefixes`
        # is this rule on the body side; this is its mirror, and it is read OFF THE
        # TREE rather than from a list typed here, so it cannot be typed wrong.
        # (It replaces the hand-typed list this file briefly carried, which named
        # '2. Pavatti' for 33Abhi05 — same result there, and no table.)
        #
        # It matters far more than it looks.  The pointer is FORWARD-ONLY, so a
        # reprint that is not recognised is searched for AHEAD — and in a book that
        # says the same thing twice it is FOUND, in the next section.  34Abhi06's
        # Cittayamaka prints an Uddesa and a Niddesa with IDENTICAL entry lists and
        # reprints "1. Suddhacittasāmañña" over each of its three vāras; the first
        # unrecognised reprint sent the pointer out of the Uddesa and into the
        # Niddesa, and every one of the 57 entries after it was then measured from
        # the wrong place.  Nothing was missing and the tree was right — the CHECK
        # was wrong, which is exactly the failure this scan's own comment warns of.
        #
        # TWO SHAPES, both keyed on the chain of the LAST MATCHED node:
        #  (1) the entry IS an ancestor's name -> a reprint, skipped, pointer held;
        #  (2) the entry OPENS with one -> the pair-line "2. Pavatti  2.
        #      Nirodhavāra", where the tree holds ONE "2. Pavatti" with three
        #      children, so only the FIRST such line folds equal to two adjacent
        #      labels and the other two must match on their right half alone.
        # The literal fold is always tried FIRST, so nothing that matched before
        # can stop matching.
        def chain(i):
            # the labels on the path to the last matched node, that node last
            return (list(ancs[i - 1]) + [flat[i - 1]]) if i > 0 else []

        def entry_folds(raw, i):
            out = [fold(raw)]
            # !!! A MĀTIKĀ THAT NUMBERS ITS ENTRIES WHERE THE BODY DOES NOT.
            # 51Vism01 numbers all 100 of its mātikā entries (`1. Sīlasarūpādikathā`)
            # and prints every one of them UNNUMBERED as a centred head
            # (`Sīlasarūpādikathā`).  That is an editorial convention of the volume,
            # not 99 separate misprints, and declaring 99 `errata` for it would bury
            # the ONE entry that really is a misprint.  The evidence that it is a
            # convention: with the number stripped the two streams are identical
            # POSITION FOR POSITION, 100 against 100, with exactly one difference —
            # `17. Pañcakajjhānakathā` against the body's `Pañcakajjhānaṁkathā`.
            # GATED PER VOLUME and off everywhere else, so it cannot loosen a
            # shipped volume's gate: measured over all 33 volumes that declare a
            # `matika` range, +0 -0.
            if sp.get('matika_unnum'):
                f = fold(re.sub(r'^\d+(?:-\d+)?\.\s*', '', raw.strip()))
                if f and f not in out:
                    out.append(f)
            # !!! A MĀTIKĀ THAT OMITS THE `-vaṇṇanā` ITS BODY SETS ON A GROUP
            # HEAD.  06ViT06 does this for FIFTY-ONE of its 540 mātikā rows —
            # every kaṇḍa, khandhaka, vagga and Parivāra section of its last four
            # books — while its first two books carry neither side's suffix.  That
            # is an editorial convention of the volume, not fifty-one misprints,
            # and declaring them as `body_errata` would bury the four rows that
            # really are disagreements.  51Vism01's `matika_unnum` is the same
            # judgement about the same kind of uniformity.
            #
            # Tried only AFTER the literal fold, so nothing that matched before can
            # stop matching, and GATED PER VOLUME: measured over the seven Vinaya
            # Ṭīkā, it resolves 51 rows in 06ViT06 and 0, 1, 1, 1, 0, 0 in the
            # other six — which is why the other six declare their singletons as
            # `body_errata` instead and do not carry this key.
            for _sx in (sp.get('matika_suffix') or ()):
                f = fold(raw.strip() + _sx)
                if f and f not in out:
                    out.append(f)
            k = re.sub(r'\s+', ' ', raw.strip())
            if sp.get('matika_reprints'):
                for x in chain(i):
                    if k.startswith(x + ' '):
                        f = fold(k[len(x):])
                        if f and f not in out:
                            out.append(f)
            return out

        matreprints = 0
        for m in mat:
            raw = era.get(m, m)
            if sp.get('matika_reprints') and i > 0 and \
                    fold(re.sub(r'\s+', ' ', raw.strip())) in [fold(x) for x in chain(i)]:
                matreprints += 1
                continue
            hit = cmp = None
            for fm in entry_folds(raw, i):
                for start, pre_ok in ((i, False), (i, True), (0, False), (0, True)):
                    hit, cmp = try_match(fm, start, pre_ok)
                    if hit is not None:
                        break
                if hit is not None:
                    break
            if hit is None:
                missing.append(m)
                continue
            if cmp:
                compound += 1
            if hit >= i:
                i = hit + 1
            else:
                outoforder += 1
        return missing, compound, outoforder, matreprints

    # !!! THE MĀTIKĀ MUST BE SEGMENTED PER BOOK, OR IT INVENTS ERRATA.
    # 06ViT06 lists the Bhikkhu-vibhaṅga's kaṇḍas (1 Pārājika … 5 Pācittiya)
    # and then the Bhikkhunī-vibhaṅga's (1 Pārājika … 4 Pācittiya — no
    # Aniyata, correctly).  Compared flat, the second run's `3. Nissaggiyakaṇḍa`
    # is measured against the first run's `4. Nissaggiyakaṇḍa` and the gate
    # reports two errata that do not exist; 07ViT07 prints `Pārājikakaṇḍa`
    # FOUR times, once per book, and a forward-only pointer that starts in the
    # wrong one strands everything behind it.
    #
    # Each book after the first declares the mātikā row that OPENS it
    # (`matika_from`).  The boundaries are consumed SEQUENTIALLY, so a label
    # the volume prints four times resolves by position and not by name, and
    # the build REFUSES if a declared boundary is not printed or if the
    # segments do not come out one per book node.
    #
    # Off by default: with no `matika_from` the whole mātikā is one segment
    # against the whole tree, which is what every shipped volume was measured
    # against.
    def _walk1(node):
        f2, a2 = [], []
        def w(ns, anc=()):
            for x in ns:
                f2.append(x['label']); a2.append(anc)
                w(x['kids'], anc + (x['label'],))
        w([node])
        return f2, a2

    segs, bnd = [], [b.get('matika_from') for b in sp.get('books', ())][1:]
    if mat and bnd and all(bnd):
        rows, cur, bi = [], [], 0
        for m in mat:
            if bi < len(bnd) and m == bnd[bi]:
                rows.append(cur); cur = []; bi += 1
            cur.append(m)
        rows.append(cur)
        if bi != len(bnd):
            print('    REFUSED — mātikā boundary %r is not printed' % bnd[bi])
            fail = True
        elif len(rows) != len(tree):
            print('    REFUSED — %d mātikā segment(s) against %d book node(s)'
                  % (len(rows), len(tree)))
            fail = True
        else:
            for _n, _r in zip(tree, rows):
                _f2, _a2 = _walk1(_n)
                segs.append((_r, _f2, _a2, _n['label']))
    if not segs:
        segs = [(mat, flat, ancs, None)]
    missing, compound, outoforder, matreprints = [], 0, 0, 0
    for _r, _f2, _a2, _lab in segs:
        _ms, _cp, _oo, _mr = run_gate(_r, _f2, _a2)
        if _lab is not None:
            print('    %-46s %3d mātikā row(s), %3d tree row(s), %2d unresolved'
                  % (_lab, len(_r), len(_f2), len(_ms)))
        missing += _ms; compound += _cp; outoforder += _oo; matreprints += _mr

    # ...AND THIS LIST MUST KNOW ABOUT `matika_suffix` TOO.  Without it,
    # 06ViT06 reported 59 "body headings the mātikā does not list" — 51 of them
    # the very rows the suffix rule had just resolved.  A printed claim that is
    # wrong is worse than no claim.
    _msx = tuple(sp.get('matika_suffix') or ())
    def _mforms(m):
        m = era.get(m, m)
        return [fold(m)] + [fold(m.strip() + x) for x in _msx]
    _mf = [f for m in mat for f in _mforms(m)]
    extra = [x for x in flat
             if not any(f in g for f in folds(x) for g in _mf)]

    print('%s  %d top / %d sections   mātikā lists %d (%d compound, %d its own '
          'ancestor reprints)  %d body reprints skipped  %d out of order  [%s]'
          % (title, len(tree), len(flat) - len(tree), len(mat), compound,
             matreprints, reprints, outoforder,
             'CHECK' if ((missing and sp.get('matika_gate', True)) or fail)
             else 'OK'))
    for n in tree:
        print('    %-24s %2d children, %3d sections'
              % (n['label'], len(n['kids']), sum(1 for _ in _flat(n['kids']))))
        for k in n['kids']:
            if k['kids']:
                print('        %-26s %d' % (k['label'], len(k['kids'])))
    if extra and mat:
        print('    body headings the mātikā does not list (%d, KEPT — they are '
              'printed): %s' % (len(extra), ', '.join(extra)))
    # THE MĀTIKĀ AS A GATE ONLY WHERE THE MĀTIKĀ IS A LIST.  29Abhi01's is a
    # plain ordered list of the body's own headings and every entry must
    # resolve.  The Paṭṭhāna's is an abbreviating INDEX — one "-ādi" line
    # standing for a run of printed headings, two-column lines, and shorter
    # names for headings the body prints in full — so requiring 1:1 there means
    # adding rule after rule until the check can no longer fail, which is worse
    # than no check.  Where it is not a gate the number is still REPORTED, and
    # the tree is gated on the colophons instead.
    gate = sp.get('matika_gate', True)
    for m in missing[:12]:
        print('    %s — in the mātikā, absent from the tree: %r'
              % ('REFUSED' if gate else 'reported', m))
    if len(missing) > 12:
        print('    ... %d more' % (len(missing) - 12))
    if missing and not gate:
        print('    %d of %d mātikā entries resolve (%d unresolved, all of them '
              'the mātikā\'s own abbreviations — not a gate here)'
              % (len(mat) - len(missing), len(mat), len(missing)))
    if missing and gate:
        fail = True

    # THE CENTRED LINES ARE A GATE EVEN WHERE THE ENTRIES ARE NOT.  Every
    # Vinaya volume prints a mātikā FINER than its body — it lists a
    # Paṭhamapaññatti and a padabhājanīya under each sikkhāpada, which the body
    # never heads — so `matika_gate` cannot be true there.  But its CENTRED
    # lines are the body's own structural headings (52 of them in 01Vin01: the
    # kaṇḍas, pārājikas, vaggas and sikkhāpadas), and every one of those must
    # resolve or a printed section is missing from the tree.  Gated per volume:
    # the Paṭṭhāna's centred lines are its index's own abbreviations and would
    # not resolve, which is the whole reason `matika_gate` is false there.
    if sp.get('matika_centred_gate'):
        cmiss = [m for m in missing if m in centred]
        print('    mātikā centred group heads: %d printed, %d resolve in the '
              'tree' % (len(centred), len(centred) - len(cmiss)))
        for m in cmiss[:12]:
            print('    REFUSED — a centred mātikā group head absent from the '
                  'tree: %r' % m)
        if cmiss:
            fail = True

    if sp.get('books') and any(b.get('naya') for b in sp['books']):
        nclosed, bad = check_book_colophons(vol, sp)
        print('    book colophons: the edition closes %d of the %d books by '
              'name, and each falls inside that book\'s own ordinals'
              % (nclosed, len(sp['books'])))
        for want, hits, lo, hi in bad:
            print('    REFUSED — %r is anchored at %s, outside ord %d-%d'
                  % (want, hits, lo, hi))
            fail = True

    if sp.get('levels') or sp.get('books'):
        colo, closed, unclosed, gone = check_colophons(vol, sp, flat)
        print('    colophons: %d printed; the edition closes %d of the %d '
              'declared sections, and all %d are in the tree'
              % (len(colo), len(closed), len(closed) + len(unclosed),
                 len(closed) - len(gone)))
        if unclosed:
            print('    (no colophon printed for, so not testable this way: %s)'
                  % ', '.join(unclosed))
        for w in gone:
            print('    REFUSED — the book prints a colophon closing %r and the '
                  'tree has no such section' % w)
            fail = True

    keys = [n['key'] for n in _flat(tree)]
    oor = [k for k in keys if not (0 <= int(k.split('#')[1]) < npara)]
    if oor:
        print('    REFUSED — keys out of range:', oor[:5]); fail = True
    print('    %d nav keys, %d out of range' % (len(keys), len(oor)))
    if fail:
        raise SystemExit('NOT WRITTEN')

    nav = json.load(open(NAV, encoding='utf-8'))
    # REPLACE EVERY NODE FOR THIS VOLUME — the invariant is one node per BOOK,
    # and a builder that replaces "the" node leaves the others behind.
    slot = None
    for lay in nav['layers']:
        for nik in lay.get('nikayas', []):
            vols = nik.get('volumes', [])
            hits = [i for i, v in enumerate(vols) if v.get('vol') == vol]
            if hits:
                slot = (vols, hits)
    if slot is None:
        raise SystemExit('no nav volume node for ' + vol)
    # A VOLUME THAT IS ONE BHĀGA OF A LARGER BOOK keeps the label its own title
    # page prints and carries its inner book as the first tree level — the
    # shape `group_abhidhamma_volumes.py` gave volumes 33-40 after the sidebar
    # was reported as a mess, and which `_abhigroupverify.js` asserts.
    out = tree
    # A multi-book volume ALREADY has one node per book — wrapping those in a
    # further node named after the first book is what produced a single inner
    # book "Dukapaṭṭhānapāḷi" spanning the whole of 39Abhi11.
    if sp.get('label') and not sp.get('books'):
        out = [{'label': title, 'key': '%s#%d' % (vol, sp['first']),
                'kids': tree}]
    # !!! THE INVARIANT IS ONE NODE PER BOOK, NOT PER VOLUME, and a volume can
    # hold two books OF THE PIṬAKA rather than two bhāgas of one work.
    # 31Abhi03 is that case: the Dhātukathā and the Puggalapaññatti are two of
    # the Abhidhamma's SEVEN books and each has its own nav node — nesting the
    # second under the first invents a book the edition does not print, which is
    # precisely the error `group_abhidhamma_volumes.py` was written to undo in
    # the other direction.  Written as one node per book when the SPEC says so;
    # `_abhigroupverify.js` caught the wrong shape immediately (12 volume rows
    # where the piṭaka has 13).
    if sp.get('separate_books'):
        nodes = [{'vol': vol, 'work': sp['work'], 'title': bk['title'],
                  'first': '%s#%d' % (vol, bk['lo']), 'tree': t['kids']}
                 for bk, t in zip(sp['books'], out)]
    else:
        nodes = [{'vol': vol, 'work': sp['work'], 'title': sp.get('label', title),
                  'first': '%s#%d' % (vol, sp['first']), 'tree': out}]
    lst, hits = slot
    print('replacing %d existing nav node(s) for %s with %d'
          % (len(hits), vol, len(nodes)))
    for i in reversed(hits):
        del lst[i]
    lst[hits[0]:hits[0]] = nodes
    if len([v for v in lst if v.get('vol') == vol]) != len(nodes):
        raise SystemExit('NOT WRITTEN — wrong node count after the splice')
    if '--write' in sys.argv:
        bak = NAV + '.bak' + vol.lower()
        if not os.path.exists(bak):
            shutil.copy(NAV, bak)
        json.dump(nav, open(NAV, 'w', encoding='utf-8'), ensure_ascii=False)
        print('wrote', NAV)
    else:
        print('DRY RUN — pass --write to save')


def _flat(ns):
    for n in ns:
        yield n
        for x in _flat(n['kids']):
            yield x


if __name__ == '__main__':
    main()
