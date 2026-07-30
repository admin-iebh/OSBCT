#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild a Khuddaka volume's reader side-maps DIRECTLY FROM THE PRINTED PDF.

19Khu02 = Vimānavatthu + Petavatthu + Theragāthā + Therīgāthā.

THE GOVERNING LESSON (HANDOFF.md): side-maps built by SPLITTING THE CORPUS TEXT
inherit every corpus defect.  This parses `pdftotext -layout` of the printed
edition into an item stream (heading / numbered verse + its printed pāda lines /
prose / colophon / uddāna) and maps it onto corpus ordinals BY VERSE NUMBER.
The corpus (site/19Khu02.json) is never touched — the reader renders
`before + groups + after` from the side-map whenever a verse entry exists, so the
side-map alone controls what is shown.

Corpus defects this repairs, all found by verify_render_vs_pdf.py:
  * dropped printed pāda lines inside a verse (e.g. v1094 loses "Sukuṇḍalī
    kappitakesamassu.", v1098 loses "Bahussute taṇhakkhayūpapanne.");
  * vagga uddāna verses SPLICED onto the tail of the vagga's last paragraph
    (ord155/269/482/631/692) while the same text also renders from uddana/ —
    so it showed twice, once in the wrong role;
  * every Tassuddānaṁ / Tatruddānaṁ and every sutta- and vagga-end colophon of
    Petavatthu, Theragāthā and Therīgāthā missing outright;
  * Theragāthā's opening Nidānagāthā missing outright;
  * three printed section headings captured as corpus paragraphs (ord 388, 390,
    857) — hidden here and re-placed as headings;
  * no verse structure at all: every verse rendered as run-on prose.

Writes: site/reader/{verse,uddana,sections,hide,incipit}/19Khu02.json
Backups: *.pre19build
"""
import json, os, re, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fnblock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R    = os.path.join(ROOT, 'site/reader')

# Per-volume spec: (title, pdf_first, pdf_last, ord_lo, ord_hi, last_verse).
# pdf pages are REAL 1-based printed-PDF pages, taken from that volume's
# structure doc in docs/ — never from the corpus `pdf_page` field, which drifts
# where the PDF has blank separator pages.
# `last_verse` is the edition's own final verse number for the book, used as a
# cross-check; None where verse numbers reset below book level (Apadāna resets
# per VAGGA, so the check does not apply there).
SPEC = {
 '19Khu02': {
   'books': [('Vimānavatthupāḷi', 17, 141,    0, 1034, 1289),
             ('Petavatthupāḷi',  143, 234, 1034, 1848,  814),
             ('Theragāthāpāḷi',  235, 391, 1848, 3136, 1288),
             ('Therīgāthāpāḷi',  393, 451, 3136, 3660,  524)],
   'stems': r'vimānavatthu|petavatthu|theragāthā|therīgāthā|vatthu|vimāna|vagga|nipāta',
   'n_scope': 'book',
 },
 '20Khu03': {
   'books': [('Therāpadānapāḷi', 21, 465, 0, 4461, None)],
   'stems': r'apadāna|vagga',
   'n_scope': 'vagga',
 },
 '21Khu04': {
   'books': [('Therāpadānapāḷi',   16, 200,    0, 2072, None),
             ('Therī-apadānapāḷi', 202, 313, 2072, 3432, None),
             ('Buddhavaṁsapāḷi',   314, 399, 3432, 4502, None),
             ('Cariyāpiṭakapāḷi',  400, 435, 4502, 4858, None)],
   'stems': r'apadāna|buddhavaṁsa|cariya|kaṇḍa|kathā|vagga',
   'n_scope': 'vagga',
 },
 # --- Jātaka: ONE work across two physical volumes -------------------------
 # `n` is the VERSE number and it resets at every NIPĀTA — not per book as in
 # 19Khu02, and NOT per vagga as the handoff predicted.  Measured: 22 nipātas
 # numbered continuously 1-22 across the two volumes (16 + 6), 547 jātakas
 # numbered continuously 1-547 (520 + 27).
 #
 # WHY NOT n_scope 'vagga', which segments on any n-descent and so would have
 # APPEARED to work: three separate things put a false descent into the stream.
 #  (1) 17 jātaka HEADINGS leaked into 22Khu05's corpus carrying the JĀTAKA
 #      number as `n` ("224. * Kumbhilajātaka (2-8-4)") — the same defect as
 #      21Khu04's ord3138, which left 293 verses unmapped.  Hidden before the
 #      map is built, exactly as there.
 #  (2) The edition MISPRINTS three verse numbers (see ERRATA below), and the
 #      corpus faithfully reproduces all three.
 #  (3) 22Khu05 p304's misprint COLLIDES: it prints "24." for verse 29 while
 #      verse 24 already exists in that nipāta, so an n-keyed map silently
 #      drops one of them — no error, just a verse that loses its structure.
 # So 'nipata' scope pairs PDF verse to corpus paragraph BY POSITION within
 # each nipāta and uses `n` only as a cross-check.  That is immune to all
 # three, and it self-verifies: all 22 nipātas pair 1:1, 0 mismatches.
 #
 # Vaggas exist ONLY in nipātas 1-7 (41 of them).  From the Aṭṭhakanipāta on,
 # jātakas sit directly under their nipāta — which is why 22Khu05's corpus
 # `vagga` field sticks on "Gandhāravaggo dutiyo." (a COLOPHON, carried
 # forward for the rest of the volume) and why 23Khu06 has no vagga field at
 # all.  The tree therefore has MIXED DEPTH, as the edition prints it.
 '22Khu05': {
   'books': [('Jātakapāḷi', 27, 426, 0, 2985, None)],
   'stems': r'jātaka|jākaka|vagga|nipāta',
   'n_scope': 'nipata',
   'nipatas': 16,
 },
 '23Khu06': {
   'books': [('Jātakapāḷi', 6, 383, 0, 3675, None)],
   'stems': r'jātaka|jākaka|vagga|nipāta',
   'n_scope': 'nipata',
   'nipatas': 6,
 },
 # --- Niddesa: PROSE EXEGESIS, the first books here that are not verse -------
 # A numbered unit is NOT a verse.  It is one Suttanipāta verse quoted as a
 # LEMMA, followed by the whole niddesa commentary on it — frequently five or
 # more printed pages of prose, with further gāthā quoted inside that prose,
 # closing with "Tenāha Bhagavā–" and the lemma repeated.  The corpus holds all
 # of that as ONE run-on paragraph, which is why these two volumes show 0.5 and
 # 1.1 paragraphs per page against 4-7 for every other Khuddaka volume.
 #
 # THE HANDOFF ASKED WHETHER THAT LOW COUNT IS LEGITIMATE OR A MERGE DEFECT.
 # It is LEGITIMATE, and shown by two independent inputs: the printed page sets
 # exactly one numbered lemma per corpus paragraph (210 printed / 210 corpus,
 # 161 / 161), and the Suttanipāta's own Aṭṭhakavagga has 210 verses against
 # 24Khu07's n = 1..210 with no gap.  Nothing needs un-merging.
 #
 # So `mode: 'niddesa'` replaces the verse machinery for such a book:
 #   * printed lemmas are paired with corpus paragraphs BY POSITION, 1:1, with
 #     `n` kept only as a cross-check.  Position and not number, because the
 #     edition MISPRINTS one of them (see ERRATA) exactly as the Jātaka does,
 #     and a number-keyed map would desync silently from that point on.  The
 #     two sides are independent — the printed lemma lines on one, the corpus
 #     paragraph array on the other — so the 1:1 pairing is a real check;
 #   * the commentary becomes `after`, split into the PRINTED PARAGRAPHS (a
 #     paragraph opens at an indent and continues at the body column), with the
 #     gāthā quoted inside it emitted as {"gatha": [...]} blocks, which the
 #     reader's proseOne() and the harness's _plist() already understand.
 #
 # 25Khu08 IS TWO HALVES, and the edition's own mātikā prints them as two
 # blocks: pages 1-21 set the Pārāyanavagga TEXT (Vatthugāthā, the 16
 # māṇavapucchās, Pārāyanatthuti- and Pārāyanānugītigāthā) as plain verse with
 # no commentary at all, and only from page 24 does the niddesa begin.  The
 # first half is ordinary verse and uses the ordinary verse path.
 '24Khu07': {
   'books': [('Mahāniddesapāḷi', 5, 414, 0, 210, None, 'niddesa')],
   'stems': r'niddesa|niddeso|niddesā|vagga|vaggo|gāthā|pucchā|pāḷi',
   'n_scope': 'book',
   # The corpus captured the printed word index "Saṁvaṇṇitapadānaṁ
   # anukkamaṇikā" as two 15,000-character paragraphs (ord210, ord211).  Same
   # class as the 14Sam03#598 back-matter paragraph an earlier session removed;
   # HIDDEN here rather than removed, because the corpus is no longer edited.
   'backmatter': [210, 211],
 },
 '25Khu08': {
   'books': [('Cūḷaniddesapāḷi',   6,  28,   0, 174, 174),
             ('Cūḷaniddesapāḷi',  29, 312, 174, 335, None, 'niddesa')],
   'stems': r'niddesa|niddeso|niddesā|vagga|vaggo|gāthā|pucchā|pāḷi',
   'n_scope': 'book',
 },
 # --- Paṭisambhidāmagga: prose again, but NOT the Niddesa's prose -----------
 # `mode: 'katha'`.  The handoff predicted this volume would reuse the niddesa
 # path and warned to check its geometry first.  BOTH of that path's
 # assumptions fail here, so it is a separate reader of the page:
 #
 #  (1) THERE IS NO LEMMA.  A niddesa section opens with a display verse and
 #      comments on it; here the number opens the PROSE ITSELF ("1. Kathaṁ
 #      sotāvadhāne paññā sutamaye ñāṇaṁ–").  So a unit has no `groups`, and
 #      the entry is written `{"groups": [], "after": [...]}`: `[]` is TRUTHY in
 #      JS, so `block()` already renders `before + after` and suppresses the
 #      corpus text, while `pr.n` still draws the number outside the block —
 #      exactly the prose shape wanted, with no reader change.  (`render_parts`
 #      DID need a fix: Python's `if e.get('groups')` reads `[]` as false and so
 #      modelled the corpus text as rendered where the reader does not render
 #      it.  A latent reader/harness divergence, now closed; no existing volume
 #      has an empty groups list, so nothing else moves.)
 #
 #  (2) THE BODY COLUMN IS NOT ALWAYS THE PAGE'S LEFTMOST INDENT.  Three page
 #      shapes are printed here and all three are measured rather than assumed:
 #      ordinary prose (continuation at the left margin, paragraphs indented);
 #      the HANGING LISTS that set the Mahāvagga mātikā and one or two other
 #      mātikās, where the number is set to the LEFT of its own continuation;
 #      and the closing Uddānagāthā page, which has no body column at all.
 #
 # Verse quoted inside the prose cannot be told from a prose paragraph opener
 # by indent — measured over the volume, 1,258 non-numbered lines sit in the
 # band 3-7 columns right of the body, of which 917 are short enough to look
 # like verse and nearly all are prose openers.  What separates them is that a
 # prose opener is followed by continuation at the BODY column while a verse
 # line is followed by another line at ITS OWN indent: so verse is a RUN of two
 # or more consecutive lines sharing an indent above the body column.  That
 # yields 24 blocks / 117 lines in the whole volume, of which exactly one sits
 # in the ambiguous band (p302's "Adhimokkhe ca paggāhe…"), and it is verse.
 # Every block is listed by --show, because this is a judgement about the page.
 '26Khu09': {
   'books': [('Paṭisambhidāmaggapāḷi', 10, 428, 0, 405, None, 'katha')],
   # `dasaka` is here because the NAV BUILDER'S MĀTIKĀ CHECK found it missing.
   # The edition prints "Mūlamūlakādidasaka" as a heading on p312 and lists it
   # in its own mātikā, but no other stem reaches it, so it was falling through
   # to the body and rendering as an ordinary prose paragraph — present,
   # contiguous, and in the wrong role, which the body gate reports as 0.
   'stems': (r'niddesa|niddeso|niddesā|kathā|vagga|vaggo|vāra|vāro|gāthā|'
             r'pāḷi|mātikā|chakka|catukka|samodhāna|dasaka'),
   'n_scope': 'book',
   'units_may_be_verse': False,
   # Printed lines that ARE headings but that no stem can reach, listed so the
   # exception is visible rather than absorbed into a looser regex.  The only
   # one here is the edition's own misprint (see ERRATA); it is recognised, and
   # its text is kept exactly as printed.
   'headfix': {'5. Virāgatathā'},
 },
 # --- Netti + Peṭakopadesa: the kathā path, with numbered units that are
 # --- SOMETIMES VERSE ------------------------------------------------------
 # TWO BOOKS IN ONE PHYSICAL VOLUME, each with its own title page, its own
 # mātikā and its own closing colophon ("Nettipakaraṇaṁ niṭṭhitaṁ." p166,
 # "Peṭakopadesapakaraṇaṁ niṭṭhitaṁ." p341).  The standing rule applies: both
 # need their own nav node or one bleeds into the other.
 #
 # The kathā path fits — a numbered unit's content is prose, the body column is
 # the left margin — with ONE addition this volume forces.  `units_may_be_verse`:
 # here a numbered unit is sometimes a GĀTHĀ and sometimes prose, and the two
 # series interleave, which is why the corpus `n` descends twice inside the
 # Netti (4 -> 1 at ord4 and 26 -> 5 at ord30: prose 1-4, then the sixteen
 # hāra verses 1-26, then prose 5 onwards).  Pairing BY POSITION is blind to
 # that; what it cannot be blind to is the SHAPE, because a verse unit rendered
 # as prose loses its line breaks.  The discriminator is the printed geometry
 # and needs no word list: **a numbered unit is verse when the line after it is
 # set at a STRICTLY GREATER indent than the number**, since a prose unit's
 # continuation returns to the body column and a gāthā's pādas do not.
 #
 # 271 printed numbered units against 271 corpus paragraphs, with `n` agreeing
 # on every one — no errata in either book.
 '27Khu10': {
   'books': [('Nettipāḷi',           7, 172,   0, 151, None, 'katha'),
             ('Peṭakopadesapāḷi',  173, 347, 151, 271, None, 'katha')],
   'stems': (r'vāra|vāro|vibhaṅga|sampāta|bhūmi|paṭṭhāna|samuṭṭhāna|saṅkhepa|'
             r'pada|padaṁ|pāḷi|niddesa|vebhaṅgiya|pakaraṇaṁ'),
   'n_scope': 'book',
   # !!! CORRECTED 2026-07-26w.  This was `True`, and 46 of the volume's 271
   # numbered units were drawn as VERSE where the page sets PROSE — the
   # question glued to the quoted gāthā's first pāda and the rest of the gāthā
   # left as a separate block below.  Its body gate was 0/0/0/0 throughout:
   # every word was present, contiguous and unique.
   #
   # `'formula'` applies the citation-dash test and NOT the hanging test (which
   # would misread genuine verse units here — see the comment at `umv`).
   'units_may_be_verse': 'formula',
   # THE BOOK'S OWN CATECHETICAL OPENERS, read off the page and counted.  Over
   # the volume's whole text extent 46 units open with one of these four and
   # every one of the 46 is a prose question answered by a quotation; the
   # other 20 verse-flagged units are genuine gāthā whose first pāda carries
   # the number.  Named, not generalised: a rule loose enough to catch these
   # would also catch the 20.
   #   Tattha katam-  43   (Tattha katamo/katamā/katamaṁ/katamāni X.)
   #   Tatthimāni      1   ("Tatthimāni suttāni.")
   #   Tatridaṁ        1   ("Tatridaṁ niyyānaṁ–", also caught by the dash)
   #   Manopubbaṅgamā  1   ("Manopubbaṅgamā dhammāti gāthā.")
   'prose_openers': (r'(?:Tattha katam|Tatthimāni\b|Tatridaṁ\b'
                     r'|Manopubbaṅgamā dhammāti gāthā\.)'),
   # and once the question is prose, the quotation's own first line — which
   # hangs LEFT of its pādas — must join the gāthā rather than become a
   # one-line prose paragraph above it
   'hanging_quote': True,
   # A DISPLAY BLOCK IS NOT ALWAYS VERSE — the flag 28Khu11 earned, and the
   # comment there predicted this volume would need it.  It does: printed p41
   # sets a PROSE quotation ("Ayuñjantānaṁ vā sattānaṁ yoge…" running on into
   # "So pamādo / duvidho taṇhāmūlako…") with exactly a gāthā's geometry, and
   # pāda punctuation is what separates them.
   'display_prose': True,
   # nine of its pages carry no body column at all and are read as entirely
   # display; on those the CENTRED upper band is the edition's own prose frame
   # around each quotation, not verse
   'display_centre': True,
 },
 # --- Milindapañha: the kathā path again, and the geometry was MEASURED ------
 # ONE book in one physical volume, 261 corpus paragraphs against 259 printed
 # numbered units plus the two leaked headings hidden below.  The page is the
 # kathā shape: the body column is the left margin, a numbered unit IS prose
 # and the number opens it, paragraph openers sit at base+4..6 and display
 # material at base+8 and up.
 #
 # WHAT MEASURING CHANGED, and it is why the handoff says to measure: this
 # volume looks like 27Khu10 — prose units with heavy quoted gāthā — so the
 # obvious move was `units_may_be_verse: True`.  That is WRONG here.  Eleven
 # units are followed by a line at a greater indent, and only ONE of them is a
 # gāthā: the opening "1. Milindo nāma so rājā, …" whose ten pādas are the
 # unit.  The other ten are PROSE that ends in the citation dash and then
 # quotes a verse — "4. Bhante Nāgasena bhāsitampetaṁ Bhagavatā–" — and the
 # flag as it stood would have rendered each of those questions as a verse
 # line, with the quotation's first pāda glued to it and the rest of the
 # quotation left as a separate block.
 # `units_may_be_verse: 'hanging'` adds the one distinction the page does
 # make: A DISPLAY QUOTATION'S FIRST LINE HANGS LEFT OF ITS OWN BODY, so a run
 # followed by a FURTHER run at a still greater indent opens a block of its
 # own and does not belong to the numbered unit.  Measured here: 1 verse unit,
 # 10 prose — every one of the eleven decided correctly.
 # !!! THE SAME SHAPE IS MIS-READ IN SHIPPED 27Khu10; see HANDOFF.md.  That is
 # NOT fixed here, because there the printed page does not separate the two
 # cases geometrically at all and 66 units need a judgement.  The flag is
 # per-book, so 27Khu10 keeps `True` and its output is unchanged — proved by
 # the 9-volume regression.
 '28Khu11': {
   'books': [('Milindapañhapāḷi', 15, 422, 0, 261, None, 'katha')],
   # Deliberately narrow.  The odd heads this book prints are NAMED rather
   # than reached by a loose stem, because `ṭhāna`, `guṇa`, `kāraṇa` and
   # `puggala` are ordinary Pāḷi words and a stem that matched them would take
   # quoted gāthā pādas out of the body — the defect `nid_is_colo` already had
   # to be tightened against once.
   'stems': (r'pañha|pañho|pañhā|vagga|vaggo|kathā|mātikā|pāḷi|'
             r'pubbayogādi|pucchāvisajjanā|parivajjanīyaṭṭhāna|'
             r'vināsakapuggala|guyhamantavidhaṁsaka|paññāpaṭilābhakāraṇa|'
             r'ācariyaguṇa|upāsakaguṇa|nigamana'),
   'n_scope': 'book',
   'units_may_be_verse': 'hanging',
   # A colophon here closes a pañha, a vagga or a kaṇḍa, so the section-word
   # list needs `pañh`; added PER VOLUME rather than to KATSECT, or 26Khu09
   # and 27Khu10 would both move.
   'colo_sect': r'pañh',
   # Four printed colophons that name no section word at all and are set at
   # indent 17-19, below the centred threshold.  Named here so the exception
   # is visible rather than absorbed into a looser test.
   'display_prose': True,
   'orphan_sections': True,
   'colopat': r'^Imasmiṁ vagge \S+ pañhā\.$',
   'colofix': {'Aṭṭha mantanassa parivajjanīyaṭṭhānāni.',
               'Aṭṭha mantavināsakapuggalā.',
               'Nava guyhamantavidhaṁsakā puggalā.',
               'Aṭṭha paññāpaṭilābhakāraṇāni.'},
 },
 # --- Abhidhamma ----------------------------------------------------------
 # THE FIRST VOLUME OF A NEW PIṬAKA, and the kathā path fits it with no
 # argument: body column 0, the mātikās read as hanging lists by `_kat_cols`,
 # and 1780 printed numbered units against 1780 corpus paragraphs with `n`
 # agreeing on every one — first try, no errata.
 #
 # TWO THINGS ARE MEASURED HERE RATHER THAN CARRIED OVER, and both are
 # per-volume so nothing shipped can move.
 #
 #  (1) `heads_by_form` — NO STEM LIST, and a stem list would be WORSE.  This
 #      volume sets 247 distinct display lines and **not one of them carries a
 #      comma, and none is longer than six words**; 99 have no terminal stop
 #      and 148 do.  That is exactly the Netti's rule — A HEADING IS A TITLE
 #      AND CARRIES NO TERMINAL STOP, and its colophon echoes it with one
 #      (`Tika` / `Tikaṁ.`, `Hetugocchaka` / `Hetugocchakaṁ.`,
 #      `Suddhikapaṭipadā` / `Suddhikapaṭipadā.`).  Enumerating stems would
 #      mean silently dropping whichever of the 99 headings I failed to list,
 #      into the body as prose — the wrong-role failure no gate can see.  The
 #      form test cannot reach body text here because the body column is 0,
 #      paragraph openers sit at 4-6, and display begins at 8.
 #
 #  (2) `no_verse` — THIS VOLUME HAS NO GĀTHĀ IN ITS TEXT EXTENT.  Shown, not
 #      assumed: a pāda carries commas, and no display line here has one.  The
 #      only gāthā the file contains are in the Nidānakathā front matter, which
 #      the declared extent correctly excludes.  It matters because the
 #      Rūpakaṇḍa sets its lists ONE ITEM PER PRINTED LINE at a paragraph
 #      indent ("Atthi rūpaṁ upādā, atthi rūpaṁ no upādā."), which the verse-run
 #      rule reads as a gāthā — and `display_prose`'s pāda-punctuation test does
 #      NOT save it, because every one of those items is a complete sentence
 #      ending in a full stop.  Three runs, 29 printed lines, would have been
 #      drawn as italic verse.
 '29Abhi01': {
   'books': [('Dhammasaṅgaṇīpāḷi', 20, 317, 0, 1780, None, 'katha')],
   'stems': r'kaṇḍa|mātikā|pāḷi',      # used only by the nav's head_kind()
   'n_scope': 'book',
   'heads_by_form': True,
   'no_verse': True,
   # THE RŪPAKAṆḌA SETS SECTIONS WITH NO NUMBERED UNIT OF THEIR OWN.  Its
   # eleven divisions — Ekaka, Duka, Tika … Ekādasaka — are each a heading, a
   # body-column opener ("Duvidhena rūpasaṅgaho–"), a list of one item per
   # printed line, then a closing line and a colophon; the next "N." does not
   # come until the division after it.  Without this the whole list landed in
   # the NEXT unit's `before`, i.e. BELOW the colophons that close it and below
   # the following division's heading — printed order destroyed, and the body
   # gate reports 0/0/0/0 because every word is still there.
   'orphan_sections': True,
 },
 # --- Vibhaṅga: the kathā shape again, and MEASURED before being written ----
 # SCOUTED 2026-07-26y and it fits with no argument: **1044 printed numbered
 # units against 1044 corpus paragraphs, n running 1..1044 with no gap, no
 # descent and no repeat** — so no leaked heading takes an ordinal anywhere in
 # the volume, which is what the Paṭṭhāna volumes each needed hiding for.
 #
 # Declared extent: "[477 pages = content 11 + text 453 + index 12 + 1 blank]"
 # -> text 1-based 12-464, so the body gate is 0-based `11 463`.
 #
 # GEOMETRY, measured: body column 0, unit openers at indent 3-8 (mostly 4-5),
 # display at 13 and up.  NO page is a hanging list and NO line carries a 3+
 # space run, so none of `split_centre`'s work applies here — this is the first
 # Abhidhamma volume where the edition never sets two headings on one line.
 #
 # HEADINGS BY FORM, on the same evidence as 29Abhi01: 192 distinct display
 # lines, NONE longer than six words, 127 with no terminal stop and 65 with
 # one — a heading is a title and its colophon echoes it with a stop.
 #
 # !!! AND `no_verse` MUST NOT BE CARRIED OVER FROM 29Abhi01.  This volume
 # prints exactly ONE gāthā, four pādas on printed p450 ("Cha ete kāmāvacarā,
 # sabbakāmasamiddhino…" — the Dhammahadaya's āyuppamāṇa verse), and those four
 # lines are the ONLY display lines in the volume that carry a comma.  Setting
 # the flag would draw them as prose.
 '30Abhi02': {
   'books': [('Vibhaṅgapāḷi', 12, 464, 0, 1044, None, 'katha')],
   'stems': r'vibhaṅga|bhājanīya|pucchaka|vāra|mātikā|niddesa|pāḷi',
   'n_scope': 'book',
   'heads_by_form': True,
   # THE VOLUME PRINTS THREE GĀTHĀ AND 42 PROSE LISTS WITH A GĀTHĀ'S GEOMETRY,
   # and the printed indent is what separates them: the lists sit at 4-7 and the
   # gāthā at 10-14, with nothing at 8 or 9.  See the comment at `verse_indent`.
   'verse_indent': 8,
   # ...and one of those three gāthā IS a numbered unit: printed p441 sets
   # "1029. Ukkhittā puññatejena, kāmarūpagatiṁgatā." with its remaining pādas
   # at indent 10.  Safe here only because `verse_indent` keeps the flag from
   # reading a unit followed by a prose LIST as verse.
   'units_may_be_verse': True,
 },
 # --- Dhātukathā + Puggalapaññatti: TWO books, and a page shape neither
 # 29Abhi01 nor 30Abhi02 has ---------------------------------------------------
 # Declared extent "[207 pages = content 7 + text 185 + index 14 + blank 1]" ->
 # text 1-based 8-192, gate 0-based `7 191`.  The book boundary is ord518, where
 # the corpus `n` RESETS to 1 — confirmed against the second title page and
 # homage at 1-based 108.  (The corpus `book` field mislabels ord518-521 as
 # "Abhidhammapiṭaka", the title page's own first line carried forward.)
 #
 # THE PUGGALAPAÑÑATTI'S MĀTIKĀ SETS EVERY UNIT ON ITS OWN LINE AT THE LEFT
 # MARGIN, one line per unit and no continuation at all — so the page's body
 # column measures as 0, the numbers sit at 0-1, and the `body + 3` floor read
 # all 22 of them as prose continuation (350 printed against 372 corpus).
 # `heads_by_form` is what lifts that floor (it is already the escape 36Abhi08
 # needed for its two flush-left units), and this volume's headings satisfy the
 # form test on the same evidence as 29Abhi01's.
 # --- Yamaka I: FIVE books in one volume, each with its own title page and
 # homage.  Declared extent "[283 pages = content 10 + text 265 + index 7 +
 # blank 1]" -> text 1-based 11-275, gate 0-based `10 274`.  The inner
 # boundaries are the corpus n-RESETS, each confirmed against a printed homage
 # page (1-based 12, 28, 82, 206, 216); the `book` field carries the title
 # page's own first line "Abhidhammapiṭaka" forward over 10 paragraphs and
 # cannot be used on its own.
 '33Abhi05': {
   # !!! THE DECLARED EXTENT IS ONE PAGE EARLY HERE — the first volume where it
   # is.  It gives 0-based 10-274, i.e. 1-based 11-275, but 1-based page 11
   # carries the ROMAN folio "viii" and is the last page of the front mātikā;
   # the text proper opens at 12 with the Mūlayamaka's title page and homage.
   # Left uncorrected, that page's twelve dotted mātikā entries are read as
   # numbered units and the first book comes out 111 printed against 99 corpus.
   # So the body gate for this volume is 0-based `11 274`, not `10 274`.
   'books': [('Mūlayamakapāḷi',    12,  27,   0,  99, None, 'katha'),
             ('Khandhayamakapāḷi', 28,  81,  99, 312, None, 'katha'),
             ('Āyatanayamakapāḷi', 82, 205, 312, 569, None, 'katha'),
             ('Dhātuyamakapāḷi',  206, 215, 569, 589, None, 'katha'),
             # !!! AND THE DECLARED EXTENT IS ONE PAGE SHORT AT THE END TOO.
             # The metadata's TEXT LENGTH is right (265 pages) but its content
             # count is one low, so the whole range is shifted: the text runs
             # 1-based 12-276, not 11-275.  Printed p276 carries the Sacca-
             # yamaka's LAST unit (170, under "6. Atītānāgatavāra"), its
             # "Pariññāvāro." and "Saccayamakapāḷi niṭṭhitā."; the word index
             # opens at 277.  Cut at 275 the book came out 169 printed against
             # 170 corpus.  SO THE BODY GATE IS 0-based `11 275`.
             ('Saccayamakapāḷi',  216, 276, 589, 762, None, 'katha')],
   # `pavatti` and `paññatti` are in the list because the LEAKED-HEADING scan
   # needs them: the corpus captured the printed pair "2. Pavatti   1.
   # Uppādavāra" whole, as a paragraph carrying the first heading's number, in
   # the Āyatana and Sacca yamakas alike.  `_is_double_head` requires BOTH
   # halves to be heading-shaped, and on a corpus paragraph the form test is not
   # available (it has no indent evidence), so the stem list is what decides —
   # "Uppādavāra" ends at `vāra` and "Pavatti" ended at nothing, so the pair was
   # not recognised and each took a unit's ordinal.
   'stems': r'yamaka|vāra|vāro|niddesa|uddesa|pucchā|pavatti|paññatti|pāḷi',
   'n_scope': 'book',
   'heads_by_form': True,
   # THE VOLUME PRINTS EXACTLY ONE GĀTHĀ AND SETS ITS CATECHISM WITH A GĀTHĀ'S
   # GEOMETRY EVERYWHERE ELSE.  The Yamaka asks its questions one statement per
   # printed line ("Sotaṁ sotāyatanaṁ, sotāyatanaṁ sotaṁ."), each a complete
   # sentence with a comma at its centre — a run of lines sharing one indent
   # above the body column, which is a gāthā's own shape, and `display_prose`'s
   # pāda test cannot see it either because every line ends in a full stop.
   # Left alone, 21 blocks of this catechism were drawn as italic verse; the
   # body gate reads 0/0/0/0 on all of them because every word is present.
   #
   # MEASURED OVER THE WHOLE VOLUME, not chosen: the runs fall at indents 4, 6,
   # 7, 8 and 9 (26 of them, every one a catechetical list) and at 12 (two,
   # both the SAME two-line mnemonic "Mūlaṁ hetu nidānañca, sambhavo pabhavena
   # ca. / Samuṭṭhānāhārārammaṇā, paccayo samudayena cāti.", printed once to
   # close the Mūlayamaka's Uddesavāra on p17 and again to close its
   # Niddesavāra on p26), with NOTHING at 10 or 11.  So `verse_indent` is the
   # size of that gap.  `no_verse` is NOT available here — it would draw that
   # mnemonic as prose.
   'verse_indent': 10,
   # p227 wraps a parenthetical editorial note onto a second CENTRED line
   # ("(Yatthakampi sabbattha sadisaṁ. Tantinānākaraṇaṁ heṭṭhā" /
   # "yatthakasadisaṁ.)"), which rendered as two paragraphs.  FOUND
   # 2026-07-26ae while scouting the Vinaya, not when this volume was built;
   # its three gates were re-run after the change.
   'wrap_display': True,
   # THE EDITION'S OWN TYPESETTING SLIP, named one line at a time — the same
   # class as 37Abhi09 p316.  The pair "2. Pavatti   N. …vāra" is printed nine
   # times in this volume and SEVEN of them separate the halves with three
   # spaces, which `split_centre` reads.  Printed p142 and p180 use ONE, so
   # those two lines stayed whole and — starting with a number — were
   # classified as numbered UNITS, which is exactly what put the Āyatanayamaka
   # at 256 printed against 254 corpus.  Widening the rule to one space is not
   # an option: it would split ordinary unit text at its first internal
   # number.  Census over all 284 pages: exactly these two.
   'split_literals': {
     '2. Pavatti 2. Nirodhavāra':                   # pdf p142
         ['2. Pavatti', '2. Nirodhavāra'],
     '2. Pavatti 3. Uppādanirodhavāra':             # pdf p180
         ['2. Pavatti', '3. Uppādanirodhavāra'],
   },
 },
 # --- Kathāvatthu: one book, 918 units, and a heading form no other volume has
 # Declared extent "[493 pages = content 14 + text 454 + index 25]" -> text
 # 1-based 15-468, gate 0-based `14 467`.  918 printed numbered units against
 # 918 corpus paragraphs, first try.
 #
 # HEADS BY FORM, and here the form test is not merely convenient but necessary:
 # its 280 kathā headings share no stem beyond `kathā` itself — the vaggas, the
 # anuyogas, "1. Vādayutti", "1. Suddhasaccikaṭṭha", "1. Nasuttasādhana" share
 # none — and a stem list would silently drop whichever it missed.  MEASURED
 # SAFE HERE: of the display lines at indent 8-17 that the form test would call
 # a heading, ALL EIGHTEEN are headings (long "(N) M. …kathā" names centred low
 # because they are long), and the 176 comma-bearing display lines are rejected
 # by the comma test before it.
 # --- Yamaka II: THREE yamakas in one volume -------------------------------
 # PROVISIONAL — scouted 2026-07-26ad.  Declared extent
 # "[336 pages = content 11 + text 316 + index 9]" -> text 1-based 12-327, and
 # CHECKED AT BOTH ENDS this time: p11 carries the roman folio "viii" and is the
 # last mātikā page, p12 opens the Saṅkhārayamaka's title page and homage, p327
 # closes "Cittayamakapāḷi niṭṭhitā." and p328 opens the word index.  So the
 # metadata is right here and the body gate is 0-based `11 326`.
 # Book boundaries: the corpus n-resets confirmed against the three printed
 # homage pages (1-based 12, 66, 300) — two independent readings that agree.
 '34Abhi06': {
   'books': [('Saṅkhārayamakapāḷi', 12,  65,   0, 162, None, 'katha'),
             ('Anusayayamakapāḷi',  66, 299, 162, 511, None, 'katha'),
             ('Cittayamakapāḷi',   300, 327, 511, 627, None, 'katha')],
   'stems': r'yamaka|vāra|vāro|niddesa|uddesa|pucchā|pavatti|paññatti|pāḷi',
   'n_scope': 'book',
   'heads_by_form': True,
   # THIS VOLUME PRINTS NO GĀTHĀ AT ALL, and it is SHOWN rather than assumed —
   # the same test 29Abhi01 used: a pāda carries commas, and **not one display
   # line in this volume has one**.  Census over all 316 text pages: 175
   # display lines, every one of them a heading, a colophon, a homage or a
   # title stack, and NONE carrying a comma.
   #
   # It is needed because the Yamaka sets its catechism one statement per
   # printed line at a paragraph indent ("Vacī vacīsaṅkhāro, vacīsaṅkhāro
   # vacī."), which is a run of candidates sharing an indent — a gāthā's own
   # shape — and every item ends in a full stop, so `display_prose`'s pāda test
   # cannot see it either.  Four blocks of it were drawn as italic verse; the
   # body gate reads 0/0/0/0 on all four.
   # 33Abhi05 could NOT use this flag — it prints one real mnemonic gāthā and
   # needed `verse_indent` instead.  The two volumes are the same work and the
   # answer is still per volume, because it is a fact about the PAGE.
   'no_verse': True,
   # THE PIṬAKA'S SECOND EMBEDDED UNIT NUMBER, and the first was 36Abhi08's
   # unit 41.  Printed p78 sets "24.Yattha kāmarāgānusayo…" with NO SPACE after
   # the number, so the extraction saw no paragraph boundary and the whole of
   # unit 24 arrived inside ord185, the paragraph carrying n=23.  Declared, not
   # guessed, and CHECKED AGAINST THE TEXT: the host must carry the declared
   # `n`, the marker must be inside it, and the printed stream must offer
   # exactly one unit at that number AND page (unit numbers repeat across
   # vāras, so the page is part of the key).
   'kat_splices': [
     # !!! THE MARK IS NOT ONLY A KEY, IT IS THE TEXT THAT RENDERS — so it
     # must be the printed unit's WHOLE FIRST LINE, exactly as set.  Declared
     # shorter ("…paṭighānusayo ca") the check still passed, because the host
     # really does contain those words, but the printed continuation lines
     # were then joined onto the truncated opening and the page read
     # "…paṭighānusayo ca diṭṭhānusayo ca…" with `mānānusayo ca` gone.  The
     # body gate caught it — 1 chunk missing, 1 not in the PDF — which is
     # exactly what that gate is for.
     {'n': 24, 'pg': 78, 'ord': 185, 'into': 23,
      'mark': '24.Yattha kāmarāgānusayo ca paṭighānusayo ca mānānusayo ca'},
   ],
 },
 # --- Yamaka III: the LAST volume of the Abhidhammapiṭaka --------------------
 # Declared extent "[347 pages = content 9 + text 330 + index 8]" -> text
 # 1-based 10-339, CHECKED AT BOTH ENDS: p9 carries the roman folio "vi" and is
 # the last mātikā page, p10 opens the Dhammayamaka's title page and homage,
 # p339 closes "Indriyayamakapāḷi niṭṭhitā." AND "Yamakapakaraṇaṁ niṭṭhitaṁ." —
 # the whole book of the Yamaka, not just this volume — and p340 opens the word
 # index.  So the body gate is 0-based `9 338`.
 # Two books; boundary = the corpus n-reset at ord231 confirmed against the
 # printed homage page (1-based 82).
 '35Abhi07': {
   'books': [('Dhammayamakapāḷi',  10,  81,   0, 231, None, 'katha'),
             ('Indriyayamakapāḷi', 82, 339, 231, 714, None, 'katha')],
   'stems': r'yamaka|vāra|vāro|niddesa|uddesa|pucchā|pavatti|paññatti|pāḷi',
   'n_scope': 'book',
   'heads_by_form': True,
   'wrap_display': True,
   # NO GĀTHĀ IN THIS VOLUME EITHER, on the same measured test as 34Abhi06:
   # 224 display lines over its 330 text pages and NOT ONE carries a comma.
   # Nine blocks of the Indriyayamaka's catechism ("Sotaṁ sotindriyaṁ. .
   # Sotindriyaṁ sotaṁ.") were being drawn as italic verse.
   'no_verse': True,
 },
 # --- VINAYA 1: Pārājikapāḷi.  PROVISIONAL — scouted 2026-07-26ae -----------
 # The metadata MERGES text and index ("[23 pages of content, 405 pages of text
 # and index]") so its tail is unusable; the extent is MEASURED — the homage is
 # on 1-based p24, the last text page is p404 ("Pārājikapāḷi niṭṭhitā."), p405
 # is a BLANK LEAF and the word index opens at p406.  So the text is 24-404 and
 # the body gate is 0-based `23 403`.
 '01Vin01': {
   # A COLOPHON THE EDITION PRINTS WITHOUT A FULL STOP.  `kat_is_colo`
   # requires the stop, so this line fell through and was read as a
   # HEADING — present, contiguous, and in the wrong role, which every
   # content gate reports as 0.  Found 2026-07-26ai by scanning every
   # volume's heads stream for `niṭṭhit|samatt`: a heading that says a
   # section has ENDED is a colophon.  Three across the corpus.
   'colofix': {'Pārājikapāḷi niṭṭhitā'},
   'books': [('Pārājikapāḷi', 24, 404, 0, 662, None, 'katha')],
   'stems': (r'kaṇḍa|vagga|vaggo|sikkhāpada|sikkhāpadaṁ|pāḷi|vibhaṅga|'
             r'uddāna|uddānaṁ|nidāna'),
   'n_scope': 'book',
   'heads_by_form': True,
   # this book prints uddāna gāthā whose even pādas carry no comma
   'pada_runon': True,
   # p174/p308/p317 set the pātimokkha recitation formula as a CENTRED line
   # wrapped onto a second, and the remainder was reading as a colophon
   'wrap_display': True,
   # A THIRD PAIR-LINE SHAPE: numbered|UNNUMBERED, where `split_centre` reads
   # numbered|numbered and `split_unnumbered` reads unnumbered|numbered.
   # CENSUS over all five Vinaya volumes: exactly ONE line has it, so it is
   # NAMED rather than given a rule that would also split ordinary text.
   'split_literals': {
     '1. Paṭhamapārājika Sudinnabhāṇavāra':        # pdf p36
         ['1. Paṭhamapārājika', 'Sudinnabhāṇavāra'],
   },
 },
 # --- VINAYA 2: Pācittiyapāḷi — TWO title pages and two homages -------------
 # The metadata merges text and index again, so the extent is MEASURED: homage
 # on 1-based p15, the last text page is p484 ("Pācittiyapāḷi niṭṭhitā.") and
 # the word index opens at p485, so the text is 15-484 and the body gate is
 # 0-based `14 483`.  !!! The index's own heading here is "Saṁvaṇṇitapadānaṁ
 # anukkamaṇika" with a SHORT final `a`, which is why a first reading walked
 # past it and made the extent two pages long — `docs/verify_report.md` has
 # been carrying that same wrong range (14-485) for this volume all along.
 # The volume's SECOND title page (p287) heads the **Bhikkhunīvibhaṅga** with
 # its own homage; the corpus boundary is ord661, the paragraph carrying unit
 # 656, which is the first unit printed on that page — two independent readings
 # that agree.  The first half is the Bhikkhuvibhaṅga and the edition does not
 # name it on the page, so it keeps the volume's own title.
 '02Vin02': {
   # A COLOPHON THE EDITION PRINTS WITHOUT A FULL STOP.  `kat_is_colo`
   # requires the stop, so this line fell through and was read as a
   # HEADING — present, contiguous, and in the wrong role, which every
   # content gate reports as 0.  Found 2026-07-26ai by scanning every
   # volume's heads stream for `niṭṭhit|samatt`: a heading that says a
   # section has ENDED is a colophon.  Three across the corpus.
   'colofix': {'Sañciccasikkhāpadaṁ niṭṭhitaṁ sattamaṁ'},
   'books': [('Pācittiyapāḷi',      15, 286,    0,  661, None, 'katha'),
             ('Bhikkhunīvibhaṅga', 287, 484,  661, 1249, None, 'katha')],
   'stems': (r'kaṇḍa|vagga|vaggo|sikkhāpada|sikkhāpadaṁ|pāḷi|vibhaṅga|'
             r'uddāna|uddānaṁ|nidāna'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   'wrap_display': True,
   # THE EDITION'S OWN TYPESETTING SLIPS, named one line at a time — the same
   # class as 37Abhi09 p316 and 33Abhi05 p142/p180.  CENSUS over all five
   # Vinaya volumes: SIX centred pair-lines that `split_centre` cannot read,
   # three of them here.  Two are set with a SINGLE space where the rule wants
   # three; the THIRD is different and is why a rule was not written instead —
   # p472's right half is numbered "8-9-10.", three numbers joined, where the
   # pattern reads at most one range ("8-9."), and widening that pattern would
   # move `HEADNUM`, `_starts_double_head` and the core-stripping regex with
   # it for the sake of one printed line.
   'split_literals': {
     '1. Musāvādavagga 5. Sahaseyyasikkhāpada':            # pdf p40
         ['1. Musāvādavagga', '5. Sahaseyyasikkhāpada'],
     '4. Tuvaṭṭavagga 3. Tatiyasikkhāpada':                # pdf p395
         ['4. Tuvaṭṭavagga', '3. Tatiyasikkhāpada'],
     '9. Chattupāhanavagga 8-9-10. Aṭṭhama navama dasamasikkhāpada':   # p472
         ['9. Chattupāhanavagga', '8-9-10. Aṭṭhama navama dasamasikkhāpada'],
   },
 },
 # --- VINAYA 3: Mahāvaggapāḷi — ten khandhakas, one book ---------------------
 # Declared "[14 pages of content, 511 pages of text, 148 pages of index]" ->
 # text 1-based 15-525, and CHECKED: p525 closes "Mahāvaggapāḷi niṭṭhitā.",
 # p526 is a blank leaf and the commentary index opens at p527.  Body gate
 # 0-based `14 524`.
 '03Vin03': {
   'books': [('Mahāvaggapāḷi', 15, 525, 0, 490, None, 'katha')],
   'stems': (r'kaṇḍa|kkhandhaka|vagga|vaggo|sikkhāpada|sikkhāpadaṁ|pāḷi|'
             r'vibhaṅga|uddāna|uddānaṁ|nidāna|kathā|vatthu|vatthūni|'
             r'anujānanā|kamma|kammaṁ'),
   'n_scope': 'book',
   'heads_by_form': True,
   'head_words': 4,        # measured — see the comment at the form test
   'pada_runon': True,
   'wrap_display': True,
   # 0-based p340's footnote rule is a GRAPHIC (the corpus's only one; see
   # pipeline/fnblock.py), so the extraction ran its three cells into the body
   # and each took an ordinal — ord293 with the whole of p341's opening prose
   # welded on behind `3. Nādikā (Sī, Syā)`.  With the printed side now cut
   # correctly these three have no partner and the count reads 476/479.
   # The prose is on the printed page and the body gate is what proves it.
   # The last pāda of Brahmā's verse plus the bracket closing the
   # editorial insertion opened on p20 — read as a heading, and it had
   # already become a nav row in a WRITTEN volume.
   'headskip': (
       'Aññātāro bhavissantī”ti.]',
   ),
   'backmatter': [291, 292, 293],
 },

 # MAJJHIMANIKĀYA — three volumes, one book each, FIVE VAGGAS apiece.
 # SCOUTED 2026-07-27c.  All three: every corpus paragraph numbered, and
 # `fnblock` finds NO graphic-rule page in any of them.
 # Extents agree with the metadata (checked, after 06Di01): 09Ma01 1-based
 # 16-430, 10Ma02 7-445, 11Ma03 7-358.  Mātikās 0-based 11-14, 3-5, 3-5.
 # !!! 10Ma02's SCOUTED "second homage page" IS NOT ONE — `Namo tassa` occurs
 # on 0-based 346 and 474 inside BODY TEXT and inside the `Gāthāsūci` index.
 # One title page, one book.
 '09Ma01': {
   # !!! `pada_runon` WAS MISSING FROM ALL SIX DĪGHA/MAJJHIMA VOLUMES until
   # 2026-07-27f, and the standing rule says to run this measurement over EVERY
   # volume whenever a new one prints gāthā.  This edition alternates the
   # punctuation of a couplet — first pāda a COMMA, second a FULL STOP — and
   # without the flag every SECOND pāda was classified by form, fell to
   # `centre`, and was flushed to the UDDĀNA map: 09Ma01 p239 sets Brahmā's
   # fourteen pādas at ONE indent (18) and the reader drew seven of them, the
   # even ones, in a block of their own AFTER the verse.  Torn couplets, every
   # word present, 0/0/0/0 on the body gate.
   'pada_runon': True,
   # !!! THE EDITION'S OWN NUMBERING SKIPS 42 AND 43.  The printed page runs
   # `41.` (0-based p36) then `44.` (p37) and the corpus matches it exactly, so
   # `n` ends at 513 over 511 paragraphs.  NOT a defect and NOT corrected.
   'books': [('Mūlapaṇṇāsapāḷi', 16, 430, 0, 511, None, 'katha')],
   # !!! AND THAT IS WHY: THE EDITION SETS BOTH NUMBERS WITH NO SPACE AFTER
   # THE PERIOD — `42.Tassa` and `43.Tassa` — so the extraction saw no boundary
   # and BOTH units arrived inside corpus ord40, the paragraph carrying n=41.
   # The printed side is RIGHT (513 units, 1-513 unbroken); the CORPUS is short
   # by two.  A regex for the numbering gap that required whitespace after the
   # period found only `41.` and made this look like the edition skipping two
   # numbers — it does not.  Fourth and fifth embedded unit number in the
   # corpus (05Vin05 p32 `39.Eḷakalomāni` was the third).
   # THE MARK IS THE TEXT THAT RENDERS, so it is the printed unit's WHOLE FIRST
   # LINE — taken from the page, not retyped.  Declared shorter, all of the
   # declaration's own tests still pass and the continuation lines are joined
   # onto a truncated opening, dropping whatever fell between (34Abhi06).
   'kat_splices': [
     {'n': 42, 'pg': 37, 'ord': 40, 'into': 41,
      'mark': '42.Tassa mayhaṁ brāhmaṇa etadahosi “ye kho keci samaṇā vā'},
     {'n': 43, 'pg': 38, 'ord': 40, 'into': 41,
      'mark': '43.Tassa mayhaṁ brāhmaṇa etadahosi “ye kho keci samaṇā vā'},
   ],
   'stems': r'sutta|suttaṁ|vagga|kathā|vatthu|pāḷi|uddāna',
   'n_scope': 'book',
   'heads_by_form': True,
 },

 '10Ma02': {
   # !!! `pada_runon` WAS MISSING FROM ALL SIX DĪGHA/MAJJHIMA VOLUMES until
   # 2026-07-27f, and the standing rule says to run this measurement over EVERY
   # volume whenever a new one prints gāthā.  This edition alternates the
   # punctuation of a couplet — first pāda a COMMA, second a FULL STOP — and
   # without the flag every SECOND pāda was classified by form, fell to
   # `centre`, and was flushed to the UDDĀNA map: 09Ma01 p239 sets Brahmā's
   # fourteen pādas at ONE indent (18) and the reader drew seven of them, the
   # even ones, in a block of their own AFTER the verse.  Torn couplets, every
   # word present, 0/0/0/0 on the body gate.
   'pada_runon': True,
   'books': [('Majjhimapaṇṇāsapāḷi', 7, 445, 0, 485, None, 'katha')],
   'stems': r'sutta|suttaṁ|vagga|kathā|vatthu|pāḷi|uddāna',
   'n_scope': 'book',
   'heads_by_form': True,
 },

 '11Ma03': {
   # !!! `pada_runon` WAS MISSING FROM ALL SIX DĪGHA/MAJJHIMA VOLUMES until
   # 2026-07-27f, and the standing rule says to run this measurement over EVERY
   # volume whenever a new one prints gāthā.  This edition alternates the
   # punctuation of a couplet — first pāda a COMMA, second a FULL STOP — and
   # without the flag every SECOND pāda was classified by form, fell to
   # `centre`, and was flushed to the UDDĀNA map: 09Ma01 p239 sets Brahmā's
   # fourteen pādas at ONE indent (18) and the reader drew seven of them, the
   # even ones, in a block of their own AFTER the verse.  Torn couplets, every
   # word present, 0/0/0/0 on the body gate.
   'pada_runon': True,
   # !!! TWO UNIT NUMBERS ARE MISPRINTED BY THE EDITION, and they are kept.
   # The sequence runs 253, 254, **225**, 256 (0-based p216) and 420, **411**,
   # 422 (p333) — 255 and 421 with a digit wrong, printed once each, with
   # correct neighbours on both sides.  The corpus reproduces the printed
   # numbers faithfully, so this is the edition's, not ours.  Same class as
   # 03Vin03's `96.` for `69.`  RECORDED AS ERRATA, NOT RENUMBERED.
   'books': [('Uparipaṇṇāsapāḷi', 7, 358, 0, 462, None, 'katha')],
   # A COLOPHON THE FORM TEST READ AS A HEADING — found by the standing
   # `niṭṭhit|samatt` scan of the heads stream.  The other four vaggas close
   # with a line this volume's own rules already catch; only the fourth's was
   # claimed as a heading.
   'colofix': {
               'Yaṁ anupadaṁ vaggavaraṁ dutiyāti.','Vibhaṅgavaggo niṭṭhito catuttho'},
   'stems': r'sutta|suttaṁ|vagga|kathā|vatthu|pāḷi|uddāna',
   'n_scope': 'book',
   'heads_by_form': True,
 },
 # --- SAṂYUTTANIKĀYA: 12Sam01, 13Sam02, 14Sam03 -----------------------------
 #
 # !!! THE FIRST NIKĀYA WHERE ONE VOLUME CARRIES SEVERAL BOOKS.  Three volumes
 # hold FIVE books, each with its own title page and homage, and the unit
 # numbering RESTARTS at each — so `books` takes TWO entries for 12Sam01 and
 # 13Sam02, and `n_scope: 'book'` is not optional here.  The corpus shows the
 # resets plainly: 12Sam01 ord271 `271 -> 1`, 13Sam02 ord361 `716 -> 1`.
 # 14Sam03 is one book and has no reset.
 #
 # Extents agree with the declared metadata in all three (checked, after
 # 06Di01, where they did not): 1-based 40-511, 19-585, 19-433.  `fnblock`
 # finds NO graphic-rule page in any of them.
 #
 # MĀTIKĀS 0-based 13-38, 3-17, 3-17 — and 12Sam01's is NOT the 26-page range
 # with a hole in it that the scout reported.  0-based 26 is a BLANK LEAF (zero
 # text lines) between the Sagāthāvagga mātikā's closing `…mātikā niṭṭhitā.`
 # (p25) and the Nidānavagga mātikā's title page (p27).  Measured, then LOOKED
 # AT, which is the rule 06Di01 earned.
 #
 # !!! `scout_volume.py` REPORTS A HOMAGE PAGE AT 12Sam01 1-based 201 AND IT IS
 # NOT A BOOK BOUNDARY.  That page is `7. Brāhmaṇasaṁyutta / 1. Arahantavagga /
 # 1. Dhanañjānīsutta`, and the three `Namo tassa` hits are the brahmin
 # uttering the homage in the NARRATIVE, quoted.  Same false positive as
 # 10Ma02.  The real boundaries are the title pages at 1-based 282 and 254,
 # each of which prints `Saṁyuttanikāya`, the book title, a rule and the homage.
 '12Sam01': {
   # !!! THE MOST VERSE-DENSE TEXT IN THE CANON — 1,895 of this volume's 3,039
   # display lines carry a comma.  `pada_runon` is what stops a couplet's
   # SECOND pāda being read as a COLOPHON by the form test: the edition
   # alternates a couplet's punctuation (first pāda a comma, second a full
   # stop), and without the flag every second pāda is flushed to the uddāna
   # map with every word still present and 0/0/0/0 on the body gate.  Its
   # absence tore 38 gāthā apart across the Dīgha and Majjhima (2026-07-27f)
   # and left eleven wrong in 31Abhi03 (2026-07-27g).  MANDATORY on all three.
   'pada_runon': True,
   # A PĀDA READ AS A HEADING, and the only one in the canon.  0-based p83 sets
   # the Kāmadasutta's gāthā with the speaker tag inside the first pāda —
   #     Dukkaraṁ vāpi karonti (Kāmadāti Bhagavā)
   #     Sekhā sīlasamāhitā.
   # — and under `heads_by_form` `kat_is_head` asks only for a capital, no
   # comma, no terminal stop and six words or fewer, all of which that line
   # satisfies.  Its own sibling four lines below, `Dullabhaṁ vāpi labhanti,
   # (Kāmadāti Bhagavā)`, is safe ONLY because the edition happened to set a
   # comma there.  Found by the MĀTIKĀ DIFF; every gate reads clean either way,
   # because a wrong ROLE leaves every word in place.
   # NAMED rather than ruled: MEASURED over all 40 canon volumes, a centred
   # line carrying a parenthesised speaker tag with no comma and no terminal
   # stop occurs EXACTLY ONCE — this line.  (40Abhi12 p368's
   # `(Ajjhattattiko na labbhati Paṭiccavārādīsu.)` is a parenthetical
   # editorial note, opens with `(` and so is not reachable by `kat_is_head`
   # at all.)  One literal against widening a shared form test.
   # WHAT IT BECOMES: a `vline` in the gāthā its siblings already form, which
   # is what the page prints.
   'headskip': ['Dukkaraṁ vāpi karonti (Kāmadāti Bhagavā)'],
   'books': [('Sagāthāvaggasaṁyuttapāḷi',  40, 281,   0, 271, None, 'katha'),
             ('Nidānavaggasaṁyuttapāḷi',  282, 511, 271, 517, None, 'katha')],
   # !!! THE PEYYĀLA HEADINGS ARE NAMED BY A NUMERAL COLLECTIVE, NOT BY
   # `sutta`.  Where the edition runs several suttas together it heads them
   # `23-112. Sāragandhādidānūpakārasuttanavutika`, `36-40. Rūpa-appaccu-
   # palakkhaṇādisuttapañcaka`, `2-7. Saṁyojanappahānādisuttachakka` — the name
   # ENDS in the collective (ninety, five, six), and `HEADTXT` anchors the stem
   # at the END of the line.  Without these the heading is not a heading: it
   # falls through to `VERSE`, is read as a numbered UNIT, and 13Sam02 book 1
   # paired 364 printed against 361 corpus paragraphs.
   # ENUMERATED FROM THE PAGE over all three volumes, not guessed — every
   # centred line matching `VERSE` that `HEADTXT` rejected.  `dasaka` covers
   # `ekādasaka` and `dvādasaka` and `tiṁsaka` covers `ttiṁsaka`, because the
   # stem matches as a SUFFIX.
   'stems': (r'sutta|suttaṁ|saṁyutta|saṁyuttaṁ|vagga|vaggo|peyyāla|'
             r'kathā|vatthu|pāḷi|uddāna|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
 },

 '13Sam02': {
   # !!! A COLOPHON THE WHOLE-WORD RULE CANNOT REACH (2026-07-30i): a ONE-WORD
   # COMPOUND in which the ordinal is the FIRST MEMBER and so carries no ending
   # of its own — `Paṭhamavaggavaṇṇanā.`, not `Paṭhamo vaggo.`  Naming them is
   # deliberate: a general "one-word capitalised stopped line" rule was tried and
   # newly claimed TWENTY lines, which is exactly what `kat_is_colo`'s form (2)
   # guards behind a centring test.  Read off the page, one by one, from the
   # release sweep in `_tika/colo_final.log`.
   'colofix': {
               'Dutiyapeyyālavaggo.',
               'Paṭhamapeyyālavaggo.',
   },

   'pada_runon': True,      # 429 of 1,482 display lines carry a comma
   'books': [('Khandhavaggasaṁyuttapāḷi',       19, 253,   0, 361, None, 'katha'),
             ('Saḷāyatanavaggasaṁyuttapāḷi', 254, 585, 361, 722, None, 'katha')],
   # !!! THE PEYYĀLA HEADINGS ARE NAMED BY A NUMERAL COLLECTIVE, NOT BY
   # `sutta`.  Where the edition runs several suttas together it heads them
   # `23-112. Sāragandhādidānūpakārasuttanavutika`, `36-40. Rūpa-appaccu-
   # palakkhaṇādisuttapañcaka`, `2-7. Saṁyojanappahānādisuttachakka` — the name
   # ENDS in the collective (ninety, five, six), and `HEADTXT` anchors the stem
   # at the END of the line.  Without these the heading is not a heading: it
   # falls through to `VERSE`, is read as a numbered UNIT, and 13Sam02 book 1
   # paired 364 printed against 361 corpus paragraphs.
   # ENUMERATED FROM THE PAGE over all three volumes, not guessed — every
   # centred line matching `VERSE` that `HEADTXT` rejected.  `dasaka` covers
   # `ekādasaka` and `dvādasaka` and `tiṁsaka` covers `ttiṁsaka`, because the
   # stem matches as a SUFFIX.
   'stems': (r'sutta|suttaṁ|saṁyutta|saṁyuttaṁ|vagga|vaggo|peyyāla|'
             r'kathā|vatthu|pāḷi|uddāna|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
 },

 '14Sam03': {
   'pada_runon': True,      # 354 of 1,416 display lines carry a comma
   'books': [('Mahāvaggasaṁyuttapāḷi', 19, 433, 0, 598, None, 'katha')],
   # !!! THE PEYYĀLA HEADINGS ARE NAMED BY A NUMERAL COLLECTIVE, NOT BY
   # `sutta`.  Where the edition runs several suttas together it heads them
   # `23-112. Sāragandhādidānūpakārasuttanavutika`, `36-40. Rūpa-appaccu-
   # palakkhaṇādisuttapañcaka`, `2-7. Saṁyojanappahānādisuttachakka` — the name
   # ENDS in the collective (ninety, five, six), and `HEADTXT` anchors the stem
   # at the END of the line.  Without these the heading is not a heading: it
   # falls through to `VERSE`, is read as a numbered UNIT, and 13Sam02 book 1
   # paired 364 printed against 361 corpus paragraphs.
   # ENUMERATED FROM THE PAGE over all three volumes, not guessed — every
   # centred line matching `VERSE` that `HEADTXT` rejected.  `dasaka` covers
   # `ekādasaka` and `dvādasaka` and `tiṁsaka` covers `ttiṁsaka`, because the
   # stem matches as a SUFFIX.
   'stems': (r'sutta|suttaṁ|saṁyutta|saṁyuttaṁ|vagga|vaggo|peyyāla|'
             r'kathā|vatthu|pāḷi|uddāna|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
 },
 # --- AṄGUTTARANIKĀYA: 15An01, 16An02, 17An03 -------------------------------
 #
 # ELEVEN NIPĀTAS OVER THREE VOLUMES — the most books per volume in the canon.
 # Each nipāta has its own title page and homage and restarts its numbering, so
 # `books` takes FOUR, THREE and FOUR entries and `n_scope: 'book'` is
 # mandatory.  Beneath a nipāta run PAṆṆĀSAKA -> VAGGA -> SUTTA.
 #
 # BOOK BOUNDARIES, each read off its own printed title page and confirmed
 # against the corpus `n` reset (two independent witnesses):
 #   15An01  Ekaka 33 . Duka 81 . Tika 131 . Catukka 339      (1-based)
 #   16An02  Pancaka 19 . Chakka 265 . Sattaka 413
 #   17An03  Atthaka 24 . Navaka 186 . Dasaka 280 . Ekadasaka 538
 #
 # !!! TWO OF THE SCOUT'S HOMAGE PAGES ARE NARRATIVE, NOT TITLE PAGES —
 # 15An01 1-based 100 (a THREEFOLD homage inside a quotation) and 16An02
 # 1-based 226.  Same false positive as 12Sam01 and 10Ma02.
 #
 # !!! AND ONE TITLE PAGE THE SCOUT DOES NOT REPORT AT ALL: 17An03's
 # DASAKANIPATA, 0-based 279.  Its homage is misprinted `Namo tassa
 # **Bhagavata** Arahato Sammasambuddhassa.` — see the `HOMAGE` comment.  The
 # corpus `n` reset at ord178 is what said the book was there; the homage scan
 # is not sufficient on its own.
 #
 # THE CORPUS `book` FIELD IS NOT A BOOK WITNESS HERE and must not be used as
 # one: inside the Ekakanipata it flips between `Ekakanipatapali`,
 # `Atthanapali` and `Ekadhammapali` (that nipata's own named sections)
 # thirteen times, and it spells the second book BOTH `Dukakanipatapali`
 # (ord324) and `Dukanipatapali` (ord456) — the edition's own inconsistency.
 #
 # Extents agree with the declared metadata in all three: 1-based 33-612,
 # 19-531, 24-581.  Matikas 0-based 13-31, 3-17, 3-22 (15An01's 0-based 12 is a
 # blank leaf before it).  `fnblock` finds no graphic-rule page.
 '15An01': {
   # !!! `head_paren` IS REQUIRED, AND WITHOUT IT HALF THE VAGGAS VANISH FROM
   # THE TREE.  From the second paṇṇāsaka on, the edition numbers a vagga
   # TWICE — its number within the nipāta and its number within the paṇṇāsaka —
   # and prints the outer one in PARENTHESES: 15An01 0-based p185 sets
   # `(6) 1. Brāhmaṇavagga`.  `kat_is_head` requires the core to open with a
   # CAPITAL, so every such line fell through and was never a heading at all:
   # the Tikanipāta showed FIVE vaggas for eighteen, and its second and third
   # paṇṇāsakas carried ~52 suttas each as DIRECT children.  Same key and same
   # cause as 32Abhi04's `(10) 1. Parūpahārakathā`.  The label keeps BOTH
   # numbers exactly as printed; only the TEST needs the name.
   'head_paren': True,
   # 722 of 1,699 display lines carry a comma.
   'pada_runon': True,
   # TWO COLOPHONS THE FORM TEST READ AS HEADINGS, found by the standing
   # `niṭṭhit|samatt` scan of the heads stream.  `kat_is_colo` requires a
   # TERMINAL STOP and these end in a PARENTHESIS — the Ekakanipāta closes two
   # of its vaggas by ordinal AND by name, "Vaggo sattamo. (Etadaggavaggo
   # niṭṭhito.)" (0-based p59) and "Vaggo catuttho. (Jambudīpapeyyālo
   # niṭṭhito.)" (p71), each with a rule below it and the next section's
   # heading after.  Checked on the page before naming.  The body gate is
   # unmoved by construction; only the role changes.
   'colofix': {'Vaggo sattamo. (Etadaggavaggo niṭṭhito.)',
               'Vaggo catuttho. (Jambudīpapeyyālo niṭṭhito.)'},
   'books': [('Ekakanipātapāḷi',    33,  80,   0, 323, None, 'katha'),
             ('Dukanipātapāḷi',     81, 130, 323, 518, None, 'katha'),
             ('Tikanipātapāḷi',    131, 338, 518, 677, None, 'katha'),
             ('Catukkanipātapāḷi', 339, 612, 677, 952, None, 'katha')],
   'stems': (r'sutta|suttaṁ|nipāta|paṇṇāsaka|vagga|vaggo|peyyāla|'
             r'kathā|vatthu|pāḷi|uddāna|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika|satika'),
   'n_scope': 'book',
   'heads_by_form': True,
 },

 '16An02': {
   # !!! `head_paren` IS REQUIRED, AND WITHOUT IT HALF THE VAGGAS VANISH FROM
   # THE TREE.  From the second paṇṇāsaka on, the edition numbers a vagga
   # TWICE — its number within the nipāta and its number within the paṇṇāsaka —
   # and prints the outer one in PARENTHESES: 15An01 0-based p185 sets
   # `(6) 1. Brāhmaṇavagga`.  `kat_is_head` requires the core to open with a
   # CAPITAL, so every such line fell through and was never a heading at all:
   # the Tikanipāta showed FIVE vaggas for eighteen, and its second and third
   # paṇṇāsakas carried ~52 suttas each as DIRECT children.  Same key and same
   # cause as 32Abhi04's `(10) 1. Parūpahārakathā`.  The label keeps BOTH
   # numbers exactly as printed; only the TEST needs the name.
   'head_paren': True,
   'pada_runon': True,      # 538 of 1,372 display lines carry a comma
   # THREE PĀDAS READ AS HEADINGS, and one root cause: A LINE THAT ENDS IN A
   # STOP FOLLOWED BY A PRINTED MARKER DOES NOT `endswith('.')`.  Under
   # `heads_by_form` `kat_is_head` asks for no terminal stop, six words or
   # fewer, no comma — and a gāthā's last pāda carrying a FOOTNOTE ASTERISK
   # (p72) or the edition's own VERSE NUMBER in parentheses (p485, p486)
   # satisfies all three.  Found by the mātikā diff; no content gate can see it.
   # NAMED, not ruled.  MEASURED over all 40 canon volumes: 728 display lines
   # end that way, in eight volumes — but the question is which of them are
   # actually CLAIMED, and the answer is checked against the shipped heads
   # streams, not inferred: NOT ONE of 05Vin05's, 27Khu10's or 29Abhi01's
   # appears in its `sections/` map (theirs sit at indent 9-10, below their own
   # display gate), and 18Khu01, 22Khu05, 23Khu06 and 25Khu08 do not use this
   # reader at all.  The class is 16An02's alone, and it is three lines.
   'headskip': ['Kammaṁ daḷhaṁ karomi dānīti.*',
                'Kāyassa bhedā nirayaṁ vajanti tā. (1-3)',
                'Kāyassa bhedā sugatiṁ vajanti tā”ti. (4-7)'],
   'books': [('Pañcakanipātapāḷi',  19, 264,   0, 271, None, 'katha'),
             ('Chakkanipātapāḷi',  265, 412, 271, 396, None, 'katha'),
             ('Sattakanipātapāḷi', 413, 531, 396, 497, None, 'katha')],
   'stems': (r'sutta|suttaṁ|nipāta|paṇṇāsaka|vagga|vaggo|peyyāla|'
             r'kathā|vatthu|pāḷi|uddāna|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika|satika'),
   'n_scope': 'book',
   'heads_by_form': True,
 },

 '17An03': {
   # !!! `head_paren` IS REQUIRED, AND WITHOUT IT HALF THE VAGGAS VANISH FROM
   # THE TREE.  From the second paṇṇāsaka on, the edition numbers a vagga
   # TWICE — its number within the nipāta and its number within the paṇṇāsaka —
   # and prints the outer one in PARENTHESES: 15An01 0-based p185 sets
   # `(6) 1. Brāhmaṇavagga`.  `kat_is_head` requires the core to open with a
   # CAPITAL, so every such line fell through and was never a heading at all:
   # the Tikanipāta showed FIVE vaggas for eighteen, and its second and third
   # paṇṇāsakas carried ~52 suttas each as DIRECT children.  Same key and same
   # cause as 32Abhi04's `(10) 1. Parūpahārakathā`.  The label keeps BOTH
   # numbers exactly as printed; only the TEST needs the name.
   'head_paren': True,
   'pada_runon': True,      # 370 of 1,094 display lines carry a comma
   # A COLOPHON PRINTED WITHOUT ITS FULL STOP.  0-based p100 closes the
   # Dānavagga `Dānavaggo catuttho` — no terminal stop — with `Tassuddānaṁ` and
   # the vagga's mnemonic directly below, so `kat_is_colo`'s stop test cannot
   # reach it and the form test claimed it as a heading.  Found by the standing
   # closing-ordinal scan of the heads stream; it is the ONLY one in the three
   # Aṅguttara volumes (15An01 0, 16An02 0, 17An03 1).
   'colofix': {'Dānavaggo catuttho'},
   'books': [('Aṭṭhakanipātapāḷi',    24, 185,   0,  96, None, 'katha'),
             ('Navakanipātapāḷi',    186, 279,  96, 178, None, 'katha'),
             ('Dasakanipātapāḷi',    280, 537, 178, 391, None, 'katha'),
             ('Ekādasakanipātapāḷi', 538, 581, 391, 426, None, 'katha')],
   'stems': (r'sutta|suttaṁ|nipāta|paṇṇāsaka|vagga|vaggo|peyyāla|'
             r'kathā|vatthu|pāḷi|uddāna|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika|satika'),
   'n_scope': 'book',
   'heads_by_form': True,
 },
 # --- VINAYA-AṬṬHAKATHĀ (Samantapāsādikā etc.) ------------------------------
 #
 # !!! THE FIRST COMMENTARY VOLUMES. Read `claude/vinaya_atthakatha_corpus_gap.md`
 # BEFORE ADDING ANOTHER: of the six Vinaya commentary volumes only FOUR have a
 # corpus complete enough to build. 01VinA01 (69% of the printed body, one
 # contiguous 78-page run missing from its start) and 05Kankha (19%, a
 # fragment) are DELIBERATELY ABSENT from this SPEC — the text is not in the
 # corpus and no side-map can put it there.
 #
 # THE CORPUS `book` FIELD IS UNUSABLE IN THIS LAYER. It alternates with
 # `Vinayapiṭaka`, the running header, dozens of times per volume (02VinA02
 # flips 118 times in 240 paragraphs). Books come from the printed TITLE PAGES.
 #
 # NUMBERED UNITS SIT AT INDENT 1-2 here, not the canon's 3-6, so `_kat_cols`'
 # `body + 3` floor would reject every one of them — `heads_by_form` bypasses
 # that floor, which is why it is set on all four.
 '02VinA02': {
   # THE SECOND BHĀGA OF THE SAMANTAPĀSĀDIKĀ'S Pārājikakaṇḍa-aṭṭhakathā, and
   # the volume opens mid-work at `3. Tatiyapārājika`.  ONE book.
   # !!! ITS NAV LABEL IS THE COVER'S, NOT THIS PAGE'S.  0-based p0 reads
   # `PĀRĀJIKAKAṆḌA-AṬṬHAKATHĀ (Dutiyo bhāgo)`; the INNER title page here (p6)
   # prints only `Pārājikakaṇḍa-aṭṭhakathā`, which is also 01VinA01's title, and
   # two nav nodes sharing a label inside one nikāya is what `_navdup.js`
   # forbids.  The bhāga belongs in the nav SPEC, not here.
   # !!! THE CLOSING COLOPHON IS TWO PRINTED LINES WITH A BLANK BETWEEN THEM,
   # and only the second says `niṭṭhitā`.  The edition sets
   #     Samantapāsādikāya Vinayasaṁvaṇṇanāya
   #
   #     Tatiyapārājikavaṇṇanā niṭṭhitā.
   # so the first line reads as a title on its own and was typed as a HEADING,
   # five times.  Present, contiguous, wrong ROLE — invisible to every content
   # gate, and found only by diffing the heads stream against the mātikā, which
   # lists none of the five.  Same shape as 01Vin01's `Pārājikapāḷi niṭṭhitā`.
   'colofix': {'Samantapāsādikāya Vinayasaṁvaṇṇanāya'},
   'books': [('Pārājikakaṇḍa-aṭṭhakathā', 7, 318, 0, 240, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|saṁghādisesa'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,      # 113 of 388 display lines carry a comma
 },

 # --- Dīgha-Aṭṭhakathā: the Sumaṅgalavilāsinī's second and third volumes ----
 # Each is ONE book and each opens at printed p10 with its own homage title
 # page.  The covers name the canon volume they comment on:
 #   08DiA02  MAHĀVAGGAṬṬHAKATHĀ    (Mahāvaggapāḷiyā saṁvaṇṇanā)
 #   09DiA03  PĀTHIKAVAGGAṬṬHAKATHĀ (Pāthikavaggapāḷiyā saṁvaṇṇanā)
 # Their corpora needed no rebuild: both start on the page their body starts
 # (p10), at 99% and 96% of the printed text, because neither opens with the
 # long unnumbered Ganthārambha that hid 78 pages of 01VinA01 and 26 of 07DiA01.
 # 07DiA01's corpus was rebuilt from the PDF (2026-07-27ad): it opens with 26
 # pages of unnumbered Ganthārambha and Bāhiranidāna that `extract.py` dropped,
 # so the shipped corpus began at printed p43 while the body begins at p17.
 '07DiA01': {
   'books': [('Sīlakkhandhavaggaṭṭhakathā', 17, 354, 0, 334, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|saṅgīti'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # !!! THE ROLES BELOW WERE FOUND BY DECLARING THIS VOLUME'S MĀTIKĀ, WHICH
   # THE NAV SPEC HAD NEVER DECLARED (2026-07-27ai).  All three Dīgha-
   # Aṭṭhakathā volumes print one and none was read, so the nav's mātikā check
   # had nothing to check and reported nothing — the same blind spot 12MaA03's
   # four-dot leader created.  Every literal below was checked on the printed
   # page; not one moves a word, so all three shipped at 0/0/0/0 with these
   # roles wrong.
   # THE COLOPHON FRAME, EIGHT TIMES.  The Sumaṅgalavilāsinī closes a sutta
   # over two lines exactly as the Papañcasūdanī does (0-based p152):
   #     Iti Sumaṅgalavilāsiniyā Dīghanikāyaṭṭhakathāyaṁ
   #         Brahmajālasuttavaṇṇanā niṭṭhitā.
   # The stop is on the second line, which `kat_is_colo` already claims, so the
   # first was read as a heading.  This volume uses the LOCATIVE `-yaṁ`;
   # 08DiA02 and 09DiA03 use the genitive `-ya`, so the literals differ by
   # volume and are named by volume.  The last one is the WHOLE BOOK's
   # colophon, `… / Atthavaṇṇanāti.` (0-based p332).
   'colofix': {'Iti Sumaṅgalavilāsiniyā Dīghanikāyaṭṭhakathāyaṁ',
               'Niṭṭhitā ca terasasuttapaṭimaṇḍitassa Sīlakkhandhavaggassa'},
   # FIVE QUOTED VERSE LINES READ AS HEADINGS — the class 12MaA03 named the
   # same day, and the same answer.  Each is the LAST PĀDA of a gāthā whose
   # citation runs on into the prose below, so it closes with the CITATION DASH
   # instead of a stop, which is the one thing `kat_is_head` asks a display
   # line not to have.  Each BECOMES the last `vline` of its own block; nothing
   # is suppressed.  Taken from the heads stream, not retyped.
   'headskip': ('Bhayā hi santo na karonti pāpan”ti9–',
                'Yaṁ vuddhamāgacchati esa bhāro”ti7–',
                'Dasadhā byañjanabuddhiyā pabhedo”ti–',
                'Idañca me dhīra mahāvimānan”ti2–',
                'Tasmā hi amhaṁ daharā na mīyare”ti5–'),
 },
 '08DiA02': {
   'books': [('Mahāvaggaṭṭhakathā', 10, 412, 0, 345, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # !!! THE ROLES BELOW WERE FOUND BY DECLARING THIS VOLUME'S MĀTIKĀ, WHICH
   # THE NAV SPEC HAD NEVER DECLARED (2026-07-27ai).  All three Dīgha-
   # Aṭṭhakathā volumes print one and none was read, so the nav's mātikā check
   # had nothing to check and reported nothing — the same blind spot 12MaA03's
   # four-dot leader created.  Every literal below was checked on the printed
   # page; not one moves a word, so all three shipped at 0/0/0/0 with these
   # roles wrong.
   # THE COLOPHON FRAME, TWICE — and this volume prints it in TWO forms, with
   # and without the opening `Iti`: `Iti Sumaṅgalavilāsiniyā …` closing the
   # Mahāpadānasutta (0-based p62) and the bare genitive closing the
   # Pāyāsirājaññasutta (p344).  Ten suttas, two frames: the edition does not
   # set it at every close, which is why the count is no guide and the heads
   # stream is.
   'colofix': {'Iti Sumaṅgalavilāsiniyā Dīghanikāyaṭṭhakathāya',
               'Sumaṅgalavilāsiniyā Dīghanikāyaṭṭhakathāya'},
   # One quoted verse line read as a heading — the fourth pāda of the gāthā
   # the Nimmitabuddha speaks, closing with the citation dash before
   # "Gāthaṁ abhāsi." (0-based p254).  Becomes the fourth `vline` of its block.
   'headskip': ('Kathaṁ bhikkhu sammā so loke paribbajeyyā”ti1–',),
 },
 # THE MAJJHIMA-AṬṬHAKATHĀ (Papañcasūdanī).  One book per volume; the second
 # `book` value the corpus carries — "Papañcasūdaniyā Majjhimanikāyaṭṭhakathāya"
 # — is the RUNNING FOOTER, not structure, exactly as in the Vinaya block.
 # Measured 2026-07-27ah: 354 ¶, all numbered, n 1-485 with no reset; 453 lines
 # at display indent of which 179 carry a comma, so the volume prints gāthā and
 # `pada_runon` is required (and `no_verse` is not arguable).
 '12MaA03': {
   'books': [('Majjhimapaṇṇāsaṭṭhakathā', 7, 315, 0, 354, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # !!! `Papañcasūdaniyā Majjhimanikāyaṭṭhakathāya` IS NOT A RUNNING FOOTER.
   # 2026-07-27ah called it one ("~50 times, once per page turn… not body
   # text, so suppressing it deletes nothing") and named `headskip` for it.
   # LOOKED AT ON THE PAGE, that is wrong on both counts.  It is the FIRST
   # LINE OF THE TWO-LINE COLOPHON the edition sets at the close of every
   # suttavaṇṇanā — 0-based p14:
   #
   #       Papañcasūdaniyā Majjhimanikāyaṭṭhakathāya
   #
   #                Kandarakasuttavaṇṇanā niṭṭhitā.
   #                            _____
   #
   # i.e. the genitive frame "in the Papañcasūdanī, the commentary on the
   # Majjhimanikāya — the Kandarakasutta-commentary is finished."  The stop is
   # on the SECOND line, which `kat_is_colo` already claims (56 colophons), so
   # the first carried no terminal punctuation and the form test read it as a
   # heading.  It occurs 49 times because the volume closes 50 suttas, not
   # because pages turn: the running headers are `Majjhimapaṇṇāsaṭṭhakathā N`
   # (odd) and `N Majjhimanikāya` (even), and neither is read as a heading.
   #
   # EXACTLY THE SHAPE 08Di03 ALREADY NAMES — `Tīhi vaggehi paṭimaṇḍito sakalo`
   # / `Dīghanikāyo samatto.` — and the same key answers it: **`colofix` gives
   # it the RIGHT role rather than merely denying it the wrong one.**  It is
   # also the same literal class as 01VinA01/02VinA02/03VinA03/04VinA04's
   # `Samantapāsādikāya Vinayasaṁvaṇṇanāya`, which has been in `colofix` since
   # the Vinaya commentary was built.  `headskip` would have demoted a printed
   # colophon line to display verse.
   #
   # ...AND THE EDITION MISPRINTS ITS OWN COLOPHON FRAME ONCE.  0-based p188,
   # closing the Mahāsakuludāyisuttavaṇṇanā, sets
   # `Papañcasūdaniyā majjhimanikāyaṭṭhākathāya` — lowercase `m`, and `ṭṭhā`
   # for `ṭṭha`.  So the frame is printed FIFTY times, not 49: the 49 the
   # earlier scout counted plus this one, which its literal could not match.
   # **The misprint is PRESERVED, not corrected** (working principle 3): the
   # variant is NAMED here so the line gets its right role, and the reading
   # that renders is the edition's own.  Recorded as an erratum in the
   # 2026-07-27ai entry; do NOT fold it to the correct spelling.
   'colofix': {'Papañcasūdaniyā Majjhimanikāyaṭṭhakathāya',
               'Papañcasūdaniyā majjhimanikāyaṭṭhākathāya'},
   # TWO QUOTED VERSE LINES READ AS HEADINGS, AND THEY ARE BODY TEXT.  Both are
   # the FOURTH PĀDA of a four-line gāthā whose citation runs on into the prose
   # below it, so the pāda closes with the CITATION DASH and not a stop —
   # which is the one thing `kat_is_head` asks a display line not to have.
   # Checked on the printed page (0-based p63 = printed 57, p65 = printed 59):
   #
   #   “Khettāni mayhaṁ viditāni loke,        “Āvedhitaṁ piṭṭhito uttamaṅgaṁ,
   #   Yesāhaṁ bījāni patiṭṭhapemi.           Bāhuṁ pasāreti akammaneyyaṁ.
   #   Ye brāhmaṇā jātimantūpapannā,          Setāni akkhīni yathā matassa,
   #   Tānīdha khettāni supesalānī”ti–        Ko me imaṁ puttamakāsi evan”ti–
   #   Gāthaṁ vatvā “imaṁ jammaṁ…             Gāthaṁ abhāsi. Mahāpuriso āha…
   #
   # WHAT EACH BECOMES, asked before it was suppressed: the fourth `vline` of
   # its own gāthā block — nothing is suppressed, only the role changes, which
   # is what `headskip` means.  The proof that the dash is the whole cause is
   # in the volume itself: the SECOND gāthā is printed TWICE, and its p58
   # printing closes `Ko me imaṁ puttamakāsi evan”ti.` WITH the stop and was
   # never read as a heading.
   'headskip': ('Tānīdha khettāni supesalānī”ti–',
                'Ko me imaṁ puttamakāsi evan”ti–'),
 },
 # --- 13MaA04: the Uparipaṇṇāsa commentary, one book ---------------------
 # `scout_volume 13MaA04 extent`: metadata "content 6 + text 254 + index 33",
 # 1-based text 7-260, homage on p7, the folio confirming both edges (p6 is
 # roman `iii`, p261 opens the index).  `corpus`: 306 ¶, all numbered, n 1-461,
 # no reset.  `geometry`: 370 lines at display indent of which 85 carry a
 # comma, so the volume prints gāthā and `pada_runon` is required.
 # === THE ABHIDHAMMA COMMENTARIES ==========================================
 # ALL THREE HAD THEIR CORPUS REBUILT (2026-07-27an), and 50AbhiA03 is the
 # reason the "buildable now / corpus short" split of 2026-07-27ak cannot be
 # trusted as it stands: it read **93%** on the census ratio and still had
 # **25** printed pages more than half absent, its missing run opening at
 # printed p118 with a whole book's narrative.  **The ratio averages over a
 # volume; the per-page test finds a contiguous hole.**  Second volume to fool
 # it after 10MaA01 (89%).
 #     48AbhiA01  70% ->  92%   115 pages more than half absent -> 0   310 -> 344 ¶
 #     49AbhiA02  95% ->  95%     3 -> 0                               325 -> 335 ¶
 #     50AbhiA03  89% ->  94%    25 -> 0                               866 -> 883 ¶
 # Every shipped paragraph survives text for text in all three.
 # === THE VISUDDHIMAGGA ====================================================
 # Not a commentary on any one canon text — the edition calls it
 # `Suttantapiṭake catunnaṁ āgamānaṁ sādhāraṇaṭṭhakathābhūto`, the commentary
 # common to all four āgamas — which is why no canon paragraph links to it and
 # the reader has no route in.  That is the link layer's problem, not the
 # body's, and it is written up separately.
 '51Vism01': {
   # ONE book, one homage page (p8), printed 8-377 with the folio confirming
   # both edges (p7 is roman `iv`, p378 opens the back matter).  364 corpus
   # paragraphs, EVERY ONE numbered, `n` 1-364.
   'books': [('Visuddhimaggo', 8, 377, 0, 364, None, 'katha')],
   # !!! THE SECTION COLOPHON HERE IS THREE OR FOUR LINES, NOT TWO, and only
   # the LAST carries a stop, so every line above it read as a heading:
   #     Iti sādhujanapāmojjatthāya kate Visuddhimagge
   #     [Samādhibhāvanādhikāre]                        <- from the 3rd on
   #     <X>niddeso nāma
   #     <ordinal> paricchedo.
   # The first two paricchedas set `<X>niddeso nāma <ordinal> paricchedo.` on ONE
   # line WITH its stop, which is why only nine of the eleven appear here — the
   # edition changes the setting after the Dhutaṅganiddesa and never changes
   # back.  Two of the nine are its own slips and are PRESERVED:
   # `Anussatikammaṭṭhānaniddesonāma` drops the space, and `Samādhiniddeso nāma4`
   # carries a footnote marker.  Named exactly as printed.
   'colofix': {'Iti sādhujanapāmojjatthāya kate Visuddhimagge',
               'Samādhibhāvanādhikāre',
               'Kammaṭṭhānaggahaṇaniddeso nāma',
               'Pathavīkasiṇaniddeso nāma',
               'Sesakasiṇaniddeso nāma',
               'Asubhakammaṭṭhānaniddeso nāma',
               'Cha-anussatiniddeso nāma',
               'Anussatikammaṭṭhānaniddesonāma',
               'Brahmavihāraniddeso nāma',
               'Āruppaniddeso nāma',
               'Samādhiniddeso nāma4'},
   # Four quoted verse pādas closing a block quotation with the citation dash,
   # each read on its printed page: p44 (the Ambakhādakamahātissatthera verse),
   # p204 (the `Bhagī bhajī bhāgi` etymology), and two on p289 from the
   # Karaṇīyametta and Udāna verses in the Mettābhāvanā.
   'headskip': ('Caje naro dhammamanussaranto”ti–',
                'Bhavantago so Bhagavāti vuccatī”ti–',
                'Sabbasattā bhavantu sukhitattā”ti-ādi–',
                'Tasmā na hiṁse paramattakāmo”ti1–'),
   # A PRINTED HEADING WITH A COMMA IN IT, which `HEADTXT` (`[^,]*`) can never
   # reach — the edition sets `Sīlasaṁkilesa, vodāna` (p48) as one centred head
   # for two topics, and its own mātikā lists it that way too.  Named rather
   # than widening the comma rule, which exists to keep ordinary prose out.
   'headfix': ('Sīlasaṁkilesa, vodāna',),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'bhājanīya|nigamana|mātikā'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '52Vism02': {
   # The Visuddhimagga's second volume, and the two are ONE CONTINUOUS WORK:
   # 51Vism01 numbers 1-364 and this one 365-896, 532 paragraphs, **no gap and
   # no duplicate**, and 896 - 364 = 532 exactly.  That is the check that
   # nothing is missing, and it is why this volume needed NO CORPUS REBUILD —
   # the screen of 2026-07-28b listed it with 1 bad page, and that page (p356)
   # is mostly a long footnote block, which `cover.py` counts as body-measure
   # lines.  A FALSE POSITIVE of the per-page test, the first one seen.
   'books': [('Visuddhimaggo', 8, 363, 0, 532, None, 'katha')],
   'colofix': {'Iti sādhujanapāmojjatthāya kate Visuddhimagge',
               # the same line with the space dropped — the edition's own slip,
               # once, and PRESERVED as printed
               'Iti sādhujanapāmojjatthāyakate Visuddhimagge',
               'Paññābhāvanādhikāre',
               'Indriyasaccaniddeso nāma',
               'Paññābhūminiddeso nāma',
               # `p` for `v`: the edition sets `Diṭṭhipisuddhi…` where its own
               # mātikā and body heading both read `Diṭṭhivisuddhi…`.  PRESERVED
               'Diṭṭhipisuddhiniddeso nāma',
               'Kaṅkhāvitaraṇavisuddhiniddeso nāma',
               'Maggāmaggañāṇadassanavisuddhiniddeso nāma',
               'Paṭipadāñāṇadassanavisuddhiniddeso nāma',
               'Ñāṇadassanavisuddhiniddeso nāma',
               'Paññābhāvanānisaṁsaniddeso nāma'},
   # Two quoted verse pādas closing a block quotation with the citation dash,
   # each read on its printed page: p15 (the `Padumaṁ yathā kokanadaṁ` verse
   # Mahāpanthaka gives Cūḷapanthaka) and p338 (the Visuddhimagga's own opening
   # gāthā, quoted back at the close of the Paññābhāvanā).
   'headskip': ('Tapantamādiccamivantalikkheti2–',
                'Cittaṁ paññañca bhāvayan”ti–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'bhājanīya|nigamana|mātikā'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },
 # === THE KHUDDAKA COMMENTARIES =============================================
 '20KhuA01': {
   # The Khuddakapāṭha-aṭṭhakathā — Buddhaghosa's Paramatthajotikā on the nine
   # texts of the Khuddakapāṭha.  ONE book, printed 19-234, one homage page.
   # CORPUS REBUILT 2026-07-28p: 67 ¶ -> 109.  Bad pages 117 -> 1.
   #
   # `katha`, MEASURED OFF THE PAGE, not assumed from the work: a numbered unit
   # IS prose and the number opens it ("5. Idāni bāhusaccañcāti ettha…", p196
   # "6-7. Evaṁ Bhagavā rañño Māgadhassa…"), with the continuation returning to
   # the body column.  The commentary's own display gāthā sit at indent 13-16
   # with pāda commas.
   'books': [('Khuddakapāṭhaṭṭhakathā', 19, 234, 0, 109, None, 'katha')],
   # The numbers restart in every one of the nine works — five resets in the
   # corpus (ord44, ord64, ord78, ord96, and the 4-5 pair at ord68).
   'n_scope': 'vagga',
   # !!! THE BACK-MATTER TRIM STARTED ONE PRINTED PAGE LATE FOR THE FOURTH TIME
   # (41KhuA22, 42KhuA23, 47KhuA28 before it).  ord107-108 are the first two
   # pages of the volume's word index — `Padānukkamo … Piṭṭhaṅkā` — which the
   # reader would otherwise draw as the closing paragraphs of the body.  Hidden,
   # NOT deleted: the edition's own text stays in the corpus.  Recorded in
   # advance on 2026-07-28p.
   'backmatter': [107, 108],
   # THE COLOPHON FRAME, READ AS A HEADING NINE TIMES — the 12MaA03 shape
   # exactly.  The edition closes every suttavaṇṇanā with a TWO-LINE colophon
   # whose first line is the genitive frame and whose second carries the stop
   # (p200: `Paramatthajotikāya Khuddakapāṭhaṭṭhakathāya` / `Tirokuṭṭasutta-
   # vaṇṇanā niṭṭhitā.`), so the frame has no terminal punctuation and the form
   # test took it for a title.  Counted on the page: the frame is printed TEN
   # times — nine as `…Khuddakapāṭhaṭṭhakathāya` and ONCE, closing the whole
   # work, as `…Khuddakaṭṭhakathāya` WITHOUT `pāṭha`.  Both readings are named
   # here and neither is folded to the other; `colofix` gives the line its
   # right role rather than merely denying it the wrong one.
   'colofix': {'Paramatthajotikāya Khuddakapāṭhaṭṭhakathāya',
               'Paramatthajotikāya Khuddakaṭṭhakathāya'},
   # FOUR QUOTED VERSE LINES READ AS HEADINGS, AND ALL FOUR ARE BODY TEXT.
   # Each is the LAST PĀDA of a display block quotation whose citation runs on
   # into the prose below it, so the pāda closes with the CITATION DASH and not
   # a stop — the one thing `kat_is_head` asks a display line not to have.  The
   # same class as 12MaA03's two, 23KhuA04's one and 51Vism01's two.  Each is
   # printed EXACTLY ONCE (checked against the edition, p19 / p159 / p159 /
   # p200), and what each BECOMES is the closing `vline` of its own gāthā
   # block — nothing is suppressed, only the role changes.
   'headskip': ('Saṁghaṁ saraṇaṁ gacchāmīti–',
                'Pahūtamariyo pakaroti puññan”ti3–',
                'Sadā bhadrāni passatī”ti4–',
                'Tumhehi puññaṁ pasutaṁ anappakan”ti–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|vavatthāna|sodhana|pañha|gāthā'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '21KhuA02': {
   # The Dhammapadaṭṭhakathā, FIRST bhāga — vaggas 1-8, Dhammapada verses
   # 1-115.  ONE book, printed 8-454, one homage page.  CORPUS REBUILT
   # 2026-07-28p: 127 ¶ -> 138.  Bad pages 61 -> 2.
   #
   # `katha` WITH `units_may_be_verse`, and the volume needs BOTH halves of
   # that key because it uses both shapes for the same thing.  A vatthu opens
   # with its Dhammapada verse cited as a lemma, and the edition sets that
   # lemma EITHER as the gāthā itself (p9: `1. Manopubbaṅgamā dhammā,` with
   # its pādas below at a greater indent) OR as prose that names it (p23:
   # `2. Manopubbaṅgamā dhammāti dutiyagāthāpi Sāvatthiyaṁyeva` continuing at
   # the body column).  The DEFAULT geometric test — the line after the number
   # sits at a strictly greater indent — separates the two exactly, and
   # `printed units 127 / corpus ¶ 127` on the first run is the check.
   'books': [('Dhammapadaṭṭhakathā', 8, 454, 0, 138, None, 'katha')],
   # The Dhammapada's numbers do NOT reset per vagga — they run 1-115 straight
   # through the eight vaggas, none missing, and only verses 1 and 2 are
   # numbered twice in the corpus.  Measured, not assumed.
   'n_scope': 'book',
   'units_may_be_verse': True,
   # TWO COLOPHONS THE EDITION PRINTS WITHOUT A FULL STOP, and both are its own
   # typesetting slips rather than a form the book uses.  `kat_is_colo` asks a
   # colophon for a terminal stop, so both fell through and were read as
   # HEADINGS — present, contiguous, and in the wrong role, which every content
   # gate reports as 0.  COUNTED ON THE PAGE: the volume closes 8 vaggas and
   # SEVEN of the eight end `…vaggavaṇṇanā niṭṭhitā.` — only p218's
   # `Cittavaggavaṇṇanā niṭṭhitā` is bare; and of its ~90 vatthu colophons only
   # p23's `Cakkhupālattheravatthu paṭhamaṁ`, the volume's FIRST, is bare.
   # Both readings are preserved as printed; `colofix` gives each its right
   # role rather than merely denying it the wrong one.
   'colofix': {'Cakkhupālattheravatthu paṭhamaṁ',
               'Cittavaggavaṇṇanā niṭṭhitā'},
   # EIGHT QUOTED PĀDAS READ AS HEADINGS, AND ALL EIGHT ARE BODY TEXT — the
   # same class as 12MaA03, 23KhuA04, 51Vism01 and 20KhuA01: the last pāda of a
   # display block quotation whose citation runs on into the prose below, so it
   # closes with the CITATION DASH and not a stop.  Six are in the
   # Maṭṭhakuṇḍalī story's verse dialogue (pp27-30), where the edition quotes
   # the Petavatthu back and forth.  Each is printed EXACTLY ONCE, checked
   # against the edition.  **`Tapantamādiccamivantalikkhe”ti1–` is the SAME
   # pāda 51Vism01 and 52Vism02 needed** and the literal differs only in its
   # footnote marker, which is why a `headskip` literal cannot be shared.
   'headskip': ('Petaṁ kālakatābhipatthayin”ti2–',
                'Tidasānaṁ sahabyataṁ gato”ti2–',
                'Kena kammena gatosi devalokan”ti.1',
                'Ajjeva Buddhaṁ saraṇaṁ vajāmī”ti2–',
                'Sakena dārena ca hohi tuṭṭho”ti1–',
                'Manussabhūto kimakāsi puññan”ti–',
                'So hiṁsito āneyya puna idhā”ti4–',
                'Tapantamādiccamivantalikkhe”ti1–',
                # A NINTH, AND A DIFFERENT SHAPE: not a closing pāda but the
                # OPENING line of a block quotation.  p277 quotes the whole
                # Udāna sutta on Mahākassapa's alms, and its first line hangs
                # left (indent 10) of the block's own body (indent 6), carries
                # no comma, no terminal stop and exactly SIX words — every
                # `heads_by_form` test for a title.  Printed once.
                'Ekaṁ samayaṁ Bhagavā Rājagahe viharati Veḷuvane'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '22KhuA03': {
   # The Dhammapadaṭṭhakathā, SECOND bhāga — vaggas 9-26, Dhammapada verses
   # 116-423.  ONE book, printed 13-468, one homage page.  CORPUS REBUILT
   # 2026-07-28p: 310 ¶ -> 331.  Bad pages 34 -> 1.
   #
   # THE SAME SHAPE AS 21KhuA02 AND IT TOOK ITS SPEC UNCHANGED — `katha` with
   # `units_may_be_verse`, because a vatthu's opening verse-lemma is set
   # sometimes as the gāthā itself and sometimes as prose naming it.
   # `printed units 310 / corpus ¶ 310` on the first run.
   'books': [('Dhammapadaṭṭhakathā', 13, 468, 0, 331, None, 'katha')],
   # The Dhammapada's numbers run 116-423 straight through the eighteen vaggas.
   'n_scope': 'book',
   'units_may_be_verse': True,
   # SIX QUOTED PĀDAS READ AS HEADINGS — the settled class: the last pāda of a
   # display block quotation whose citation runs on into the prose below, so it
   # closes with the CITATION DASH and not a stop.  Each printed exactly once
   # (pp161, 218, 337, 368, 378, 442), checked against the edition.
   'headskip': ('Yo bhāsitassa vijānāti atthan”ti–',
                'Atha so jarasāpi miyyatī”ti1–',
                'Tasseva jantu vinayāya sikkhe”ti1–',
                'Bījāni vuttāni yathāsukhette”ti2–',
                'Gajuttamo sabbaguṇesu aṭṭhā”ti1–',
                'Vasamānesi rasehi sañjayo”ti3–'),
   # NO `colofix` HERE, and that was checked rather than assumed: every one of
   # this volume's 251 colophons carries its terminal stop, unlike 21KhuA02,
   # which prints two without one.
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '35KhuA16': {
   # The CARIYĀPIṬAKAṬṬHAKATHĀ — Dhammapāla's Paramatthadīpanī on the
   # Cariyāpiṭaka, and the LAST of the 52 commentary volumes.  ONE book,
   # printed 6-333, one homage page (p6).  CORPUS REBUILT 2026-07-28p: -> 339 ¶.
   # Metadata and `scout extent` agree.
   'books': [('Cariyāpiṭakaṭṭhakathā', 6, 333, 0, 339, None, 'katha')],
   'units_may_be_verse': True,
   'n_scope': 'vagga',
   'display_prose': 'dash',
   # The two-line genitive frame, three printings (p34, p115, p181), one per
   # vagga.  Measured before naming, as 27KhuA08 requires: the line is in NO
   # corpus paragraph, so `colofix` hides nothing and strands no link target.
   'colofix': {'Paramatthadīpaniyā Cariyāpiṭakasaṁvaṇṇanāya'},
   # THREE citation-dash pādas, each printed once — the settled class, and the
   # only thing check 1 finds in this volume.
   'headskip': ('Pappoti macco amataṁ brahmalokan”ti2–',
                'Karohi puññāni anappakānī”ti2–',
                'Isīhi tvaṁ kīḷasi Devarājā”ti3–'),
   'stems': (r'vaṇṇanā|saṁvaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|'
             r'bhāṇavāra|nidāna|nigamana|mātikā|gāthā|nipāta|cariyā|'
             r'apadāna|thera|therī|bhāga'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '34KhuA15': {
   # The BUDDHAVAṀSAṬṬHAKATHĀ — the Madhuratthavilāsinī, and a THIRD author in
   # this batch: `Bhadantācariyabuddhadattattherena katā`, not Dhammapāla and
   # not the anonymous elder of the Apadāna commentary.  ONE book, printed
   # 6-359, one homage page (p6).  CORPUS REBUILT 2026-07-28p: -> 945 ¶.
   # Metadata and `scout extent` agree.
   # `n` resets to 1 twenty-nine times, once per Buddha's vaṁsa.
   'books': [('Buddhavaṁsaṭṭhakathā', 6, 359, 0, 945, None, 'katha')],
   'units_may_be_verse': True,
   'n_scope': 'vagga',
   'display_prose': 'dash',
   # !!! THIS VOLUME PRINTS ITS STANZA NUMBERS IN THE RIGHT MARGIN, AFTER THE
   # PĀDA'S OWN FULL STOP — `Samayo Mahāvīra aṅgīrasānaṁ.        (9)` — so the
   # form test's `not core.endswith('.')` is satisfied and the closing pāda of
   # every stanza of a long refrain reads as a TITLE.  57 of the volume's 108
   # headings were this.  See `kat_is_head`.
   'margin_verse_numbers': True,
   'colofix': {'Iti Madhuratthavilāsiniyā Buddhavaṁsaṭṭhakathāya',
               'Madhuratthavilāsiniyā Buddhavaṁsaṭṭhakathāya',
               'Ettāvatā catuvīsatiyā Buddhānaṁ Buddhavaṁsavaṇṇanā',
               'Ettāvatā nātisaṅkhepavitthāravasena katāya'},
   'headskip': ('Katamaṁ Tathāgatassa Yamakapāṭihīre ñāṇaṁ? Idha Tathāgato',
                'Koṭisatasahassā arahanto',
                'Sukhaṁ lokapālā mahiṁ pālayantu.1'),
   # !!! A PRINTED HEADING THAT CONTAINS A COMMA IS NOT A HEADING TO
   # `kat_is_head`, BY CONSTRUCTION — `if ',' in core: return False`, because a
   # comma is what marks running text.  p356 sets
   # `Sahajātapariccheda, nakkhattaparicchedakathā` as a centred head at indent
   # 16, and its own mātikā entry (p5) is the same string comma and all, so
   # there is no doubt what it is.  `headfix` names it; the comma rule is left
   # alone, since it is what keeps body prose out of the heads stream.
   'headfix': ('Sahajātapariccheda, nakkhattaparicchedakathā',),
   'stems': (r'vaṇṇanā|saṁvaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|'
             r'bhāṇavāra|nidāna|nigamana|mātikā|gāthā|nipāta|apadāna|thera|'
             r'therī|vaṁsa|bhāga'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '33KhuA14': {
   # The Apadānaṭṭhakathā, SECOND bhāga — the Visuddhajanavilāsinī continued,
   # from the Sīhāsaniyavagga on.  ONE book, printed 14-316, one homage page
   # (p14).  CORPUS REBUILT 2026-07-28p: -> 727 ¶.  Metadata and `scout extent`
   # agree.  `n` resets to 1 THIRTY-SEVEN times, once per thera's apadāna,
   # which is what `n_scope: 'vagga'` is for; not one of them is a book
   # boundary and the volume prints ONE homage.
   'books': [('Apadānaṭṭhakathā', 14, 316, 0, 727, None, 'katha')],
   'units_may_be_verse': True,
   'n_scope': 'vagga',
   'display_prose': 'dash',
   # !!! THE FRAME IS PRINTED EXACTLY ONCE, AT THE VERY END, AND THE SWEEP
   # MISSED IT.  This bhāga closes each of its fifty-six vaggas on a SINGLE
   # stopped line (`…vaggavaṇṇanā samattā.`), so a sweep looking for a stopless
   # line above a close returns nothing and "no frame in this volume" is the
   # obvious reading — it is wrong.  p315 sets
   # `Iti Visuddhajanavilāsiniyā Apadānaṭṭhakathāya` above
   # `Ettāvatā Buddhapaccekabuddhasāvakattherāpadānaṭṭhakathā samattā.`,
   # closing the whole apadāna section rather than a vagga.  FOUND BY READING
   # THE HEAD STREAM, which is the second volume in a row where that check has
   # caught what the sweep could not (29KhuA10 was the first).
   'colofix': {'Iti Visuddhajanavilāsiniyā Apadānaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|saṁvaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|'
             r'bhāṇavāra|nidāna|nigamana|mātikā|gāthā|nipāta|apadāna|thera|'
             r'therī|bhāga'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '32KhuA13': {
   # The APADĀNAṬṬHAKATHĀ — the Visuddhajanavilāsinī, and NOT Dhammapāla:
   # the title page names only `Porāṇikena kenaci therena viracitā`, "composed
   # by some ancient elder".  FIRST bhāga, printed 5-356, one homage page (p5).
   # CORPUS REBUILT 2026-07-28p: -> 506 ¶.  Metadata and `scout extent` agree.
   'books': [('Apadānaṭṭhakathā', 5, 356, 0, 506, None, 'katha')],
   'units_may_be_verse': True,
   # !!! `n` DESCENDS TWICE AND BOTH ARE THE EDITION'S OWN, read on the page
   # before quoting them:
   #   * p263 SETS UNIT `310.` AND ITS THREE LINES TWICE IN SUCCESSION — a
   #     duplicated setting in the printed edition, not a corpus defect and not
   #     a pdftotext artefact: the surrounding text flows correctly around both.
   #     The corpus holds both (ord255 and ord256 are byte-identical) and the
   #     printed stream holds both, so the 1:1 count is unmoved and the reader
   #     draws it twice BECAUSE THE PAGE PRINTS IT TWICE.  Preserved under
   #     principle 3; do not de-duplicate it.
   #   * p309 prints `442.` between 421 and 430, where the run reads 429.  The
   #     same class as 29KhuA10's `130.` for `230.`, and `442.` is legitimately
   #     printed again on p313.
   'n_scope': 'vagga',
   'display_prose': 'dash',
   # The two-line genitive frame, three printings (p118, p146, p232) — the
   # ordinary shape of this layer, and the FIRST volume of the batch to set
   # `Visuddhajanavilāsiniyā` rather than `Paramatthadīpaniyā`.  Its second line
   # carries the stop and varies (`…vaṇṇanā niṭṭhitā.`, `…saṁvaṇṇanā samattā.`),
   # so only the first needs naming.
   'colofix': {'Iti Visuddhajanavilāsiniyā Apadānaṭṭhakathāya'},
   # ONE printed line reads as a heading, and it is the SAME LITERAL 30KhuA11
   # needed at its p505 — the Bakabrahmasutta's opening `Ekaṁ samayaṁ…`, set as
   # a block-opening line HANGING LEFT of its own body (indent 9 over a body at
   # 4).  A shared literal across volumes is unusual for this key (the footnote
   # markers normally differ); here the line carries none, so it is identical.
   # After it the head stream is EXACTLY the printed mātikā: 21 and 21.
   'headskip': ('Ekaṁ samayaṁ Bhagavā Sāvatthiyaṁ viharati Jetavane',),
   'stems': (r'vaṇṇanā|saṁvaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|'
             r'bhāṇavāra|nidāna|nigamana|mātikā|gāthā|nipāta|apadāna|thera|'
             r'therī|bhāga'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '31KhuA12': {
   # The Therīgāthā-aṭṭhakathā — Dhammapāla's Paramatthadīpanī on the
   # Therīgāthā, sixteen nipātas.  ONE book, printed 8-312, one homage page
   # (p8).  CORPUS REBUILT 2026-07-28p: -> 590 ¶.  The metadata
   # ("content 7 + text 305 + index 86 + blank 1") and `scout extent` agree.
   # The same author, the same reader and the same shape as 29KhuA10/30KhuA11,
   # and its `n` runs 1-524 with NO reset at all.
   'books': [('Therīgāthā-aṭṭhakathā', 8, 312, 0, 590, None, 'katha')],
   'units_may_be_verse': True,
   'n_scope': 'vagga',
   'display_prose': 'dash',
   # !!! THE EDITION OMITS THE TERMINAL STOP ON ONE COLOPHON.  p60 sets
   # `Aparā uttamātherīgāthāvaṇṇanā niṭṭhitā` with no period where its
   # eighty-four fellows all carry one, so `kat_is_colo` refused it and the
   # heading branch claimed it — the stop is the one thing that test asks for.
   # ONE literal, printed once.  Naming it costs NOTHING: the line is not a
   # corpus paragraph of its own (the corpus splices it onto the tail of ord72,
   # unit 47), so `colofix` hides nothing and strands no link target.  Measured
   # before choosing, as 27KhuA08 requires.
   'colofix': {'Aparā uttamātherīgāthāvaṇṇanā niṭṭhitā'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā|nipāta|therī|thera|bhāga'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '30KhuA11': {
   # The Theragāthā-aṭṭhakathā, SECOND bhāga — 29KhuA10's continuation, and the
   # two are one work: this volume opens at the Catukkanipāta where that one
   # closed after the Tikanipāta, and runs to the Mahānipāta.  ONE book, printed
   # 8-553, one homage page (p8).  CORPUS REBUILT 2026-07-28p: -> 1101 ¶.
   # The metadata ("content 7 + text 546 + index 134") and `scout extent` agree.
   'books': [('Theragāthā-aṭṭhakathā', 8, 553, 0, 1101, None, 'katha')],
   'units_may_be_verse': True,
   'n_scope': 'vagga',
   'display_prose': 'dash',
   # !!! THE EDITION SETS TWO UNIT NUMBERS WITH NO SPACE AFTER THE PERIOD, and
   # both times `extract.py` saw no boundary, so the printed unit arrived INSIDE
   # the previous corpus paragraph — 1020 printed against 1018.  The sixth and
   # seventh embedded unit number found so far; the same class as 09Ma01's
   # `42.Tassa` and 14SamA01's `64.65.`, and the 1:1 count is the only thing
   # that can see it.  The mark is the printed unit's WHOLE FIRST LINE, because
   # it is not only a key — it is the text that renders (34Abhi06).
   'kat_splices': [
     {'n': 1164, 'pg': 490, 'ord': 976, 'into': 1163,
      'mark': '1164.Añjanīva navā cittā, pūtikāyo alaṅkato.'},
     {'n': 1263, 'pg': 525, 'ord': 1074, 'into': 1262,
      'mark': '1263.So me dhammamadesesi, muni dukkhassa pāragū.'},
   ],
   # NINE PRINTED LINES READ AS HEADINGS, each printed once, and unlike
   # 29KhuA10 — where check 1 came back empty — this volume needs the key badly.
   # THREE are the settled citation-dash class (p192, p196, p203); `Tapantam-
   # ādiccamivantalikkhe”ti2–` is the `Padumaṁ yathā kokanadaṁ` verse AGAIN,
   # the FOURTH volume to need it after 52Vism02, 51Vism01 and 47KhuA28, and
   # the literal differs from all three because the footnote marker does.
   # SIX are inside display PROSE quotations — and two shapes, not one:
   #   * the block-OPENING line HANGING LEFT of its own body (p415 `Katamā
   #     javanapaññā–…` at 11 over a body at 6, p417, p505) — the 21KhuA02 shape;
   #   * !!! an ordinary INTERIOR line of such a block, at the block's OWN
   #     indent (p415 `Uppannuppanne…`, p507 x2), which no earlier volume has
   #     needed.  A FIFTH shape for this key.
   'headskip': ('Taranti nāvāya nadiṁva puṇṇan”ti–',
                'Tapantamādiccamivantalikkhe”ti2–',
                'Moho rajo -pa- vītarajassa sāsane”ti–',
                'Katamā javanapaññā–yaṁ kiñci rūpaṁ atītānāgatapaccuppannaṁ',
                'Uppannuppanne pāpake akusale dhamme nādhivāseti pajahati',
                'Puna caparaṁ bhikkhave Sāriputto vitakkavicārānaṁ vūpasamā',
                'Ekaṁ samayaṁ Bhagavā Sāvatthiyaṁ viharati Jetavane',
                'Brahmapārisajjo tassa brahmuno paṭissutvā yenāyasmā',
                'Mahāmoggallāno evamāha–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā|nipāta|thera|bhāga'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '29KhuA10': {
   # The Theragāthā-aṭṭhakathā — Dhammapāla's Paramatthadīpanī on the
   # Theragāthā, FIRST bhāga: Ekaka-, Duka- and Tikanipāta.  ONE book, printed
   # 12-496, one homage page (p12).  CORPUS REBUILT 2026-07-28p: 262 ¶ -> 453.
   #
   # The metadata AGREES here — "content 11 + text 485 + index 147 + blank 1"
   # puts the text at 12-496 and `scout_volume extent` measures the same, the
   # folio confirming both edges (p11 is roman `viii`, p496 carries printed
   # 485).  Unlike 27KhuA08, whose declared figure ran 20 pages into the index.
   'books': [('Theragāthā-aṭṭhakathā', 12, 496, 0, 453, None, 'katha')],
   # A numbered unit is EITHER the quoted gāthā (its pādas below at a GREATER
   # indent — p49 sets `2. “Upasanto uparato,` at 6 with its second pāda at 9)
   # or the prose comment on it (p53 sets `3. Tattha paññanti` at 5 with the
   # line below at 0).  The DEFAULT indent test separates them; neither the
   # 28Khu11 `hanging` nor the 27Khu10 `formula` answer is needed.
   'units_may_be_verse': True,
   # `n` runs 1-266 and descends three times, and ALL THREE ARE THE EDITION'S
   # OWN, preserved rather than corrected (principle 3):
   #   * ord29/ord30 both print `14.` — p85 numbers the thera's narrative and
   #     p86 numbers the comment on it, because Sivaka's gāthā is quoted inline
   #     and never set as a display block;
   #   * p445 prints `130.` where the run reads 230 (between 229 and 231);
   #   * p475 prints `151.` where the run reads 251 (between 250 and 252).
   # Both misprints stand on the printed side AND in the corpus, so the 1:1
   # pairing is unmoved; `n_scope: 'vagga'` is what lets the descents pass.
   'n_scope': 'vagga',
   # THE COLOPHON-FRAME SWEEP RETURNS THREE LITERALS IN FOUR PRINTINGS — far
   # fewer than its companions, because this volume closes 206 sections and
   # frames only three of them.  `_khua/_probe29/colosweep.py`.
   #   p45, p78   Paramatthadīpaniyā Theragāthāsaṁvaṇṇanāya      (vagga close)
   #   p314       Niṭṭhitā ca Paramatthadīpaniyaṁ Theragāthāvaṇṇanāyaṁ
   #              Vīsādhikasatattheragāthāpaṭimaṇḍitassa
   #              Ekakanipātassa atthavaṇṇanā.                   <- the stop
   # !!! THE SWEEP KEYED ON `niṭṭhitā.` CANNOT SEE THE p314 FRAME, because its
   # closing line ends `atthavaṇṇanā.` instead — 27KhuA08 and 28KhuA09 both set
   # `atthavaṇṇanā niṭṭhitā.` there and hid the difference.  Found by reading
   # the head stream, not by the sweep; widen the sweep when it is next used.
   # MEASURED BOTH WAYS, as 27KhuA08 requires: two of the three literals are in
   # NO corpus paragraph at all and the third (ord245) is already hidden as a
   # leaked heading, so naming them costs ZERO link targets.  Nothing to trade.
   'colofix': {'Paramatthadīpaniyā Theragāthāsaṁvaṇṇanāya',
               'Niṭṭhitā ca Paramatthadīpaniyaṁ Theragāthāvaṇṇanāyaṁ',
               'Vīsādhikasatattheragāthāpaṭimaṇḍitassa'},
   # TWO PROSE QUOTATIONS SET IN A GĀTHĀ'S GEOMETRY — p198 (the Aṅguttara's
   # `Yathā yathāvuso bhikkhu yathāsutaṁ…`) and p222 (`Ye te bhikkhū
   # sīlasampannā…`).  Both break mid-clause, so the pāda-punctuation test
   # separates them.  !!! PLAIN `True` IS WRONG HERE and the difference was
   # measured, not assumed: it takes gāthā blocks 54 -> 40, and SEVEN of the
   # fourteen it removes are REAL gāthā whose closing pāda carries the citation
   # dash (p40, p41, p87, p154, p202, p268) or runs straight on into the
   # sentence below (p391) instead of a stop.  `'dash'` admits `…”ti`, with or
   # without a footnote marker and with or without the dash, as a pāda end:
   # gāthā blocks 54 -> 47, and ALL SEVEN removed are quoted sutta PROSE, each
   # read on its printed page — p198, p222, p243, p247, p344, p345, p442.
   # The three shipped volumes that set `display_prose: True` (27Khu10,
   # 28Khu11, 32Abhi04) were rebuilt builder-vs-builder against
   # `build_khu_volume.py.pre29khua10`: byte-identical on all five side-maps,
   # and `regress check` 55/55.
   'display_prose': 'dash',
   # !!! THE EDITION OMITS THE PERIOD AFTER A HEADING'S NUMBER, ONCE.  p156
   # sets `5 Ramaṇīyavihārittheragāthāvaṇṇanā` where its mātikā entry (p6) and
   # the section's own colophon (p157) both carry it, so the numbered test
   # never fired and the heading was in NO `sections/` entry at all — the tree
   # could not reach it.  Same class as 09Ma01's `42.Tassa`, the other way
   # round.  `headfix` beats the numbered test (2026-07-27ak); the printed
   # reading is kept and the mātikā's form goes on the tree side, in the NAV's
   # `body_errata`.
   'headfix': ('5 Ramaṇīyavihārittheragāthāvaṇṇanā',),
   # THE EDITION MISPRINTS THREE MORE BODY HEADINGS and its own mātikā does not
   # — `3. Sumaṅgalattheraghāthāvaṇṇanā` (p150, `ghāthā`),
   # `6. Piyañjahattheragāthāvaṇṇanās` (p223, a trailing `s`) and
   # `10. Sāṭhimattiyattheragāthāvaṇṇanā` (p471, an intrusive `h`).  Every one
   # is contradicted by the section's OWN closing colophon two pages later, so
   # the body printing is the misprint.  They are NOT declared here:
   # `body_errata` is a key of the NAV builder and `build_khu_volume.py` never
   # reads it — declared here it would be a belief, not a correction.
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā|nipāta|thera|bhāga'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '28KhuA09': {
   # The Petavatthu-aṭṭhakathā — Dhammapāla's Paramatthadīpanī on the
   # Petavatthu, four vaggas — and 27KhuA08's companion in every respect: the
   # same reader, the same vatthu-counting colophon frame.  ONE book, printed
   # 7-276, one homage page.  CORPUS REBUILT 2026-07-28p: 1066 ¶ -> 1121.
   # Bad pages 82 -> 7.
   'books': [('Petavatthu-aṭṭhakathā', 7, 276, 0, 1121, None, 'katha')],
   'n_scope': 'vagga',
   'units_may_be_verse': True,
   # THE SAME VATTHU-COUNTING FRAME AS 27KhuA08, swept the same way and reaching
   # to indent 4.  Seven literals, ten printings.  Its genitive is SHORTER here
   # — `Iti Khuddakaṭṭhakathāya Petavatthusmiṁ`, without `Paramatthadīpaniyā` —
   # and the volume's closing colophon names the author and his monastery on
   # two more stopless lines (p276).
   'colofix': {'Iti Khuddakaṭṭhakathāya Petavatthusmiṁ',
               'Dasavatthupaṭimaṇḍitassa',
               'Dvādasavatthupaṭimaṇḍitassa',
               'Terasavatthupaṭimaṇḍitassa',
               'Soḷasavatthupaṭimaṇḍitassa',
               'Iti Badaratitthavihāravāsinā Munivarayatinā',
               'Bhadantena Ācariyadhammapālena katā'},
   # THREE PRINTED LINES READ AS HEADINGS, each printed once.  Two are the
   # settled citation-dash class (p201, p213); `Avoca tassā mātaraṁ–` (p194) is
   # a prose lead-in closing with the same dash before a block quotation.
   'headskip': ('Avoca tassā mātaraṁ–',
                'Mā khosi piṭṭhimaṁsiko tuvan”ti–',
                'Sabbampi akkhissaṁ6 yathā pajānan”ti–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā|peta'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '27KhuA08': {
   # The Vimānavatthu-aṭṭhakathā — Dhammapāla's Paramatthadīpanī on the
   # Vimānavatthu, seven vaggas.  ONE book, printed 8-342, one homage page.
   # CORPUS REBUILT 2026-07-28p: 1382 ¶ -> 1480.  Bad pages 109 -> 5.
   #
   # !!! THE METADATA'S PAGE COUNT IS NOT THE TEXT EXTENT HERE.  It says
   # "content 7 + text 355 + index 71 + blank 1", which would put the text at
   # 8-362 — but the body closes with the Nigamanakathā on p341 and its final
   # gāthās on p342, p343 is a blank leaf, and the word index
   # (`Saṁvaṇṇitapadānaṁ anukkamaṇikā`) opens on p344.  MEASURED, not declared:
   # 8-342, which is what `scout_volume extent` reports.  Twenty pages of the
   # metadata's "text" are index.
   'books': [('Vimānavatthu-aṭṭhakathā', 8, 342, 0, 1480, None, 'katha')],
   # The canon's gāthā numbers run 1-1287 and the commentary's prose units are
   # numbered with them, so the corpus descends 114 times where a vimāna's
   # comment restarts below the gāthā it has reached.
   'n_scope': 'vagga',
   # A numbered unit is EITHER the quoted gāthā (pādas below at a greater
   # indent) or the prose comment on it — the 21KhuA02 shape.
   'units_may_be_verse': True,
   # THE VAGGA COLOPHON FRAME IS THREE LINES AND ITS MIDDLE LINE COUNTS THE
   # VAGGA'S VATTHUS, so it is a different literal every time (p116):
   #
   #    Iti Paramatthadīpaniyā Khuddakaṭṭhakathāya Vimānavatthusmiṁ
   #                  Ekādasavatthupaṭimaṇḍitassa
   #           Dutiyassa Cittalatāvaggassa atthavaṇṇanā niṭṭhitā.
   #
   # Swept over all 335 text pages — and the sweep had to reach down to indent
   # 4, not 8, because the frame's FIRST line is set at 5.  Seven literals,
   # fifteen printings; the numbered units the same window returns are ordinary
   # body text and are left alone.
   # !!! MEASURED BOTH WAYS BEFORE CHOOSING, because naming these lines HIDES
   # the corpus paragraphs that hold them and a hidden paragraph takes its link
   # targets with it (42KhuA23, 2026-07-28n):
   #
   #        without `colofix`   hidden  5   body 0/5/0/0   links stranded 3
   #        with    `colofix`   hidden 12   body 0/1/0/0   links stranded 9
   #
   # FOUR printed frame lines reach the page that otherwise do not, at the cost
   # of SIX more link targets from 19Khu02 that no longer resolve.  Content
   # wins — the stranded targets are colophons, they still RENDER from the
   # printed stream, and only the ordinal route is lost — but the six are
   # counted here and added to the open link-rebuild item, not waved away.
   'colofix': {'Iti Paramatthadīpaniyā Khuddakaṭṭhakathāya Vimānavatthusmiṁ',
               'Paramatthadīpaniyā Khuddakaṭṭhakathāya',
               'Dasavatthupaṭimaṇḍitassa',
               'Ekādasavatthupaṭimaṇḍitassa',
               'Dvādasavatthupaṭimaṇḍitassa',
               'Cuddasavatthupaṭimaṇḍitassa',
               'Sattarasavatthupaṭimaṇḍitassa'},
   # FOUR QUOTED PĀDAS READ AS HEADINGS, the settled citation-dash class.
   # `Vaṇṇo ca me sabbadisā pabhāsatī”ti–` is printed TWENTY-TWO times — it
   # closes the Vimānavatthu's stock question-gāthā — and every printing is the
   # same pāda in the same role, so one literal demotes all of them.
   'headskip': ('Sabbe na tappāmase dassanena tan”ti1–',
                'Vaṇṇo ca me sabbadisā pabhāsatī”ti–',
                'Tidasānaṁ sahabyataṁ gato”ti–',
                'Passantu puññānaṁ phalaṁ kadariyā”ti–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā|vimāna'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '26KhuA07': {
   # The Suttanipātaṭṭhakathā, SECOND bhāga — the Cūḷavagga from its fourth
   # sutta, then the Mahā-, Aṭṭhaka- and Pārāyanavaggas.  ONE book, printed
   # 7-330, one homage page.  CORPUS REBUILT 2026-07-28p: 675 ¶ -> 736.
   # Bad pages 69 -> 1.
   'books': [('Suttanipātaṭṭhakathā', 7, 330, 0, 736, None, 'katha')],
   # THE COLOPHON FRAME, SWEPT: 114 printings of FOUR literals and nothing
   # else, over all 324 text pages.  **The edition misprints its own frame
   # ONCE** — `Iti paramatthajotikāya Khuddakaṭṭhakathāya` with a lowercase
   # `p`, against 55 printings of the capitalised form — the same class as
   # 12MaA03's `majjhimanikāyaṭṭhākathāya`.  Preserved as printed and NAMED so
   # the line gets its right role; do NOT fold it to the correct spelling.
   'colofix': {'Paramatthajotikāya Khuddakaṭṭhakathāya',
               'Iti Paramatthajotikāya Khuddakaṭṭhakathāya',
               'Iti paramatthajotikāya Khuddakaṭṭhakathāya',
               'Suttanipātaṭṭhakathāya'},
   'n_scope': 'book',
   # !!! FIVE SUTTA HEADINGS CARRY A PARENTHESISED ALTERNATIVE TITLE, AND THE
   # FORM TEST REFUSES THEM.  A numbered line is a heading under
   # `heads_by_form` only when its core is at most `head_words` (default TWO)
   # words: `4. Maṅgalasuttavaṇṇanā` is one word and passes, but
   # `6. Kapilasutta (Dhammacariyasutta) vaṇṇanā` is THREE and became a
   # numbered UNIT — which took an ordinal, so the volume paired 678 printed
   # units against 674 corpus paragraphs and REFUSED TO BUILD.
   #
   # `head_words: 3` fixes four of the five and BREAKS the fifth, which is why
   # this is `headfix` instead.  **The corpus glued `4. Pūraḷāsasutta
   # (Sundarikabhāradvājasutta) vaṇṇanā` onto the narrative that follows it**
   # (ord190, 3,179 characters, its `4.` read as the paragraph's own number —
   # the `145 -> 1` shape 22KhuA03 has at its ord34), so on that ONE the corpus
   # itself holds a unit and the printed side must agree or the count parts
   # company again. So four are NAMED as headings and the fifth is left as the
   # unit the corpus makes it — the wrong role, recorded rather than papered
   # over, and it is why the nav cannot reach that mātikā entry.
   'headfix': ('6. Kapilasutta (Dhammacariyasutta) vaṇṇanā',
               '8. Dhammasutta (Nāvāsutta) vaṇṇanā',
               '12. Nigrodhakappasutta (Vaṅgīsasutta) vaṇṇanā',
               '13. Sammāparibbājanīyasutta (Mahāsamayasutta) vaṇṇanā'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '25KhuA06': {
   # The Suttanipātaṭṭhakathā, FIRST bhāga — Buddhaghosa's Paramatthajotikā II
   # on the Uragavagga and the Cūḷavagga.  ONE book, printed 5-318, one homage
   # page; the front matter is a SINGLE mātikā page.  CORPUS REBUILT
   # 2026-07-28p: 232 ¶ -> 264.  Bad pages 65 -> 1.
   'books': [('Suttanipātaṭṭhakathā', 5, 318, 0, 264, None, 'katha')],
   # The gāthā numbers run 1-260 with NO descent anywhere in the corpus; the
   # gaps (11-13, 32, 46, 95-113 odd, …) are where the commentary takes several
   # gāthās together, not resets.
   'n_scope': 'book',
   # THE TWO-LINE COLOPHON FRAME, PRINTED FIFTEEN TIMES EACH.  Swept, as on
   # 24KhuA05, rather than collected: every stopless centred line standing
   # above a `…niṭṭhitā.` over all 314 text pages returns exactly these two and
   # nothing else.
   #
   #       Paramatthajotikāya Khuddakaṭṭhakathāya
   #                Suttanipātaṭṭhakathāya
   #            Uragasuttavaṇṇanā niṭṭhitā.
   'colofix': {'Paramatthajotikāya Khuddakaṭṭhakathāya',
               'Suttanipātaṭṭhakathāya'},
   # THREE PRINTED LINES READ AS HEADINGS.  Two are the settled citation-dash
   # class (p11, p97).  The third, p168's `Puna caparaṁ bhikkhave idhekacco
   # pāpabhikkhu`, is the OPENING line of a block quotation — the mahācora
   # simile from the Vinaya — hanging LEFT (indent 10) of the block's own body
   # (indent 6), the same shape 21KhuA02 needed at its p277.  Each printed once.
   'headskip': ('Paññāyete pidhīyare”ti–',
                'Yaṁ phassaye sāmayikaṁ vimuttin”ti–',
                'Puna caparaṁ bhikkhave idhekacco pāpabhikkhu'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|gāthā'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '24KhuA05': {
   # The Itivuttakaṭṭhakathā — Dhammapāla's Paramatthadīpanī on the Itivuttaka,
   # 112 suttas in four nipātas.  ONE book, printed 9-363, one homage page.
   # CORPUS REBUILT 2026-07-28p: 109 ¶ -> 115.  Bad pages 34 -> 2.  (Its re-key
   # needed a hand-made baseline; see that entry.)
   'books': [('Itivuttakaṭṭhakathā', 9, 363, 0, 115, None, 'katha')],
   # The sutta numbers run 1-112 straight through the four nipātas — measured,
   # not assumed: no descent anywhere in the corpus.  (23KhuA04, the Udāna
   # commentary of the same Paramatthadīpanī, restarts per vagga and is
   # `n_scope: 'vagga'`; this one does not.)
   'n_scope': 'book',
   # !!! A THREE-LINE COLOPHON FRAME, AND THE FIRST TWO LINES CARRY NO STOP.
   # The edition closes each nipāta with
   #
   #       Paramatthadīpaniyā Khuddakanikāyaṭṭhakathāya
   #                     Itivuttakassa
   #             Ekakanipātavaṇṇanā niṭṭhitā.
   #
   # (p99).  Only the THIRD line has the terminal stop `kat_is_colo` asks for,
   # so the first two were read as HEADINGS — the 12MaA03 / 20KhuA01 class, but
   # two lines deep instead of one.  COUNTED ON THE PAGE: the frame is printed
   # four times, the last of the four prefixed `Iti`, and the volume closes a
   # fifth section with a DIFFERENT genitive — `Iti Paramatthadīpaniyā
   # Itivuttakaṭṭhakathāya`, once.  All four readings are named and none is
   # folded to another.
   # SWEPT, NOT COLLECTED ONE AT A TIME: every stopless centred line standing
   # inside a colophon frame (the line or two above a `…niṭṭhitā.`), over all
   # 355 text pages.  SIX literals, TWELVE printings, and nothing else — the
   # four `N. …suttavaṇṇanā` the same sweep returns are real section headings.
   #   Paramatthadīpaniyā Khuddakanikāyaṭṭhakathāya      4   (nipāta closes)
   #   Itivuttakassa                                     4
   #   Itivuttakavaṇṇanāya                               1   (a sutta close)
   #   Dukanipāte                                        1   (a vagga close)
   #   Iti Paramatthadīpaniyā Itivuttakaṭṭhakathāya      1
   #   Iti Paramatthadīpaniyā Khuddakanikāyaṭṭhakathāya  1
   'colofix': {'Paramatthadīpaniyā Khuddakanikāyaṭṭhakathāya',
               'Iti Paramatthadīpaniyā Khuddakanikāyaṭṭhakathāya',
               'Iti Paramatthadīpaniyā Itivuttakaṭṭhakathāya',
               'Itivuttakassa',
               'Itivuttakavaṇṇanāya',
               'Dukanipāte'},
   # THREE QUOTED PĀDAS READ AS HEADINGS — the settled citation-dash class,
   # each printed exactly once (pp47, 110, 111).
   'headskip': ('Sayaṁkataṁ makkaṭakova jālan”ti7 ca–',
                'Idañca me dhīra mahāvimānan”ti4–',
                'Tasmā hi amhaṁ daharā na mīyare”ti5–',
                # A FOURTH, AND NOT A PĀDA: `Anatthajanano moho -pa-.4` (p53)
                # is a PEYYĀLA line inside a display block quotation, set at the
                # block's own indent.  Short, capitalised, no comma, and its
                # terminal stop is followed by a footnote marker, so every
                # `heads_by_form` test for a title passes.  Printed once.
                'Anatthajanano moho -pa-.4'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'nigamana|mātikā|nipāta|nipāto'),
   'heads_by_form': True,
   'pada_runon': True,
 },
 '23KhuA04': {
   # CORPUS REBUILT 2026-07-28i: 92 ¶ -> 98, restoring 6 unnumbered paragraphs
   # and trimming 197 back-matter ones.  Bad pages 7 -> 1, and that one is a
   # page whose only long line is the footnote RULE — the same false positive
   # 52Vism02 produced.  The shipped corpus began at printed p13: the whole
   # Ganthārambhakathā, pp8-12, was missing.
   'books': [('Udānaṭṭhakathā', 8, 400, 0, 98, None, 'katha')],
   # The Māradhītaro verse's last pāda, closing a block quotation with the
   # citation dash (p232).  **The SAME pāda 47KhuA28 needed**, and the literal
   # differs only in its footnote marker — `…icche”ti3–` there, `…icche”ti2–`
   # here — which is exactly why a `headskip` literal cannot be shared.
   'headskip': ('Pādāpi naṁ samphusituṁ na icche”ti2–',),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|nigamana|mātikā'),
   'n_scope': 'vagga',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '36KhuA17': {
   # Jātakaṭṭhakathā I.  ONE nipāta, the Ekaka — but the volume opens with the
   # Ganthārambhakathā and the whole Nidānakathā, 118 printed pages of prose
   # before the first numbered jātaka.  CORPUS REBUILT 2026-07-28o: 148 ¶ ->
   # 193.  Bad pages 157 -> 2, and both of those are a mātikā page and a rule
   # line, not body loss.
   # TWO BOOKS, because the front matter is not verse.  The Ganthārambhakathā
   # and the whole Nidānakathā fill printed pp 11-128 as THIRTEEN corpus
   # paragraphs with no numbered anchor at all; on the verse path every one of
   # their nine headings piled up above jātaka 1, so the prose drew BEFORE its
   # own headings.  The fourth reader (`heads`, 2026-07-28d) is exactly this
   # case: heading-delimited prose located by content, forward-only.
   'books': [('Ganthārambhakathā + Nidānakathā', 11, 120, 0, 12, None, 'heads'),
             ('Jātakaṭṭhakathā', 121, 548, 12, 193, None)],
   'stems': r'jātaka|jākaka|vagga|nipāta|vaṇṇanā|kathā',
   'n_scope': 'nipata',
   'nipatas': 1,
   # A `before` residue that is already a whole corpus paragraph draws the
   # narrative twice; the body gate cannot see it (2026-07-28o).
   'no_reprint': True,
   # !!! `headskip` WAS TRIED AND WITHDRAWN.  Two printed lines render as
   # headings that are not: `Jātakaṭṭhakathā` (ord1, the running header, in the
   # HEADS book) and `Jetavanamahāvihāre viharanto kathesi. Kaṁ pana ārabbha
   # ayaṁ kathā` (ord13, ordinary prose, in the VERSE book).  The second cannot
   # be declared at all — `kat_is_head` is never called on the verse path, so
   # the builder REFUSES the literal as never met (the 40KhuA21 gap, still
   # open).  The first CAN be declared, and skipping it takes the heads
   # reader's own delimiter away: located falls 3092 -> 377, residue 2721, and
   # the book goes FATAL.  Both are recorded as defects, neither is papered
   # over.
 },
 '37KhuA18': {
   # Jātakaṭṭhakathā II.  TWO nipātas, the Duka and the Tika.  CORPUS REBUILT
   # 2026-07-28m: 347 ¶ -> 380.  Bad pages 34 -> 0.
   'books': [('Jātakaṭṭhakathā', 11, 418, 0, 380, None)],
   'stems': r'jātaka|jākaka|vagga|nipāta|vaṇṇanā|kathā',
   'n_scope': 'nipata',
   'nipatas': 2,
   # A `before` residue that is already a whole corpus paragraph draws the
   # narrative twice; the body gate cannot see it (2026-07-28o).
   'no_reprint': True,
 },
 '41KhuA22': {
   # Jātakaṭṭhakathā VI.  ONE nipāta, the Mahānipāta, five jātakas, no vaggas.
   # CORPUS REBUILT 2026-07-28n: 782 ¶ -> 818.  Bad pages 92 -> 1, and that one
   # is the mātikā's single closing line — the known apparatus-page false
   # positive, not body loss.
   'books': [('Jātakaṭṭhakathā', 5, 336, 0, 818, None)],
   'stems': r'jātaka|jākaka|vagga|nipāta|vaṇṇanā|kathā',
   'n_scope': 'nipata',
   'nipatas': 1,
   # A `before` residue that is already a whole corpus paragraph draws the
   # narrative twice; the body gate cannot see it (2026-07-28o).
   'no_reprint': True,
   # the rebuild's back-matter trim starts one page LATE here: printed pp
   # 333-334 of the word index survive as ord815-817.  Hidden, not deleted.
   'backmatter': [815, 816, 817],
 },
 '38KhuA19': {
   # Jātakaṭṭhakathā III.  SIX nipātas, 4 to 9.  CORPUS REBUILT 2026-07-28m:
   # 835 ¶ -> 856.  Bad pages 28 -> 0, and the coverage ratio goes to 99%.
   'books': [('Jātakaṭṭhakathā', 11, 527, 0, 856, None)],
   'stems': r'jātaka|jākaka|vagga|nipāta|vaṇṇanā|kathā',
   'n_scope': 'nipata',
   'nipatas': 6,
   # A `before` residue that is already a whole corpus paragraph draws the
   # narrative twice; the body gate cannot see it (2026-07-28o).
   'no_reprint': True,
 },
 '39KhuA20': {
   # THE JĀTAKA COMMENTARY IS A VERSE VOLUME, not a `katha` one: its units are
   # the QUOTED GĀTHĀS with the canon's own numbers, pādas below the number,
   # and the commentary's prose hangs off them — the same shape as the canon
   # 22Khu05/23Khu06, which is why it takes the same reader and `n_scope`.
   # SIX nipātas, counted off the printed heads: 10. Dasaka, 11. Ekādasaka,
   # 12. Dvādasaka, 13. Terasaka, 14. Pakiṇṇaka, 15. Vīsati.
   # CORPUS REBUILT 2026-07-28k: 1149 ¶ -> 1158, trimming 192 back-matter ¶.
   # Bad pages 19 -> 2, and both are the footnote-rule false positive.
   'books': [('Jātakaṭṭhakathā', 8, 511, 0, 1158, None)],
   'stems': r'jātaka|jākaka|vagga|nipāta|vaṇṇanā|kathā',
   'n_scope': 'nipata',
   'nipatas': 6,
   # A `before` residue that is already a whole corpus paragraph draws the
   # narrative twice; the body gate cannot see it (2026-07-28o).
   'no_reprint': True,
 },
 '40KhuA21': {
   # Jātakaṭṭhakathā V — the `verse` shape settled on 39KhuA20.  SIX nipātas,
   # 16 to 21, counted off the printed heads.  CORPUS REBUILT 2026-07-28l:
   # 1573 ¶ -> 1583, trimming 119 pages of word index.  Bad pages 27 -> 1 (the
   # footnote rule).
   'books': [('Jātakaṭṭhakathā', 6, 558, 0, 1583, None)],
   # !!! TWO LINES OF ORDINARY PROSE RENDER AS HEADINGS HERE AND THERE IS NO
   # KEY FOR IT ON THE VERSE PATH.  `Khantivādijātaka Mātaṅgajātaka
   # Bharujātaka Sarabhaṅgajātaka` (p104) and `Imassa panatthassa dīpanatthaṁ
   # Khantivādijātaka1` (p124) are the commentary telling the reader which
   # other jātakas to recite at that point; the `jātaka` stem takes them into
   # `HEADTXT`.  `headskip` is a KATHĀ-PATH key — `kat_is_head` consults it and
   # the verse path does not — and declaring it here made the builder REFUSE,
   # `headskip literal(s) never met as a heading`, which is the guard working
   # exactly as intended.  RECORDED, NOT WORKED AROUND: both lines are present,
   # in printed order, and no text is lost; only their role is wrong.  The fix
   # is a verse-path equivalent, which is shared machinery and needs measuring
   # over all 40 canon volumes first.
   'stems': r'jātaka|jākaka|vagga|nipāta|vaṇṇanā|kathā',
   'n_scope': 'nipata',
   'nipatas': 6,
   # A `before` residue that is already a whole corpus paragraph draws the
   # narrative twice; the body gate cannot see it (2026-07-28o).
   'no_reprint': True,
 },
 '42KhuA23': {
   # Jātakaṭṭhakathā VII — ONE nipāta, the Mahānipāta, and its ten great
   # jātakas fill the whole volume.  CORPUS REBUILT 2026-07-28l: 1657 ¶ ->
   # 1690, trimming 111 pages of word index.  Bad pages 27 -> 2 (footnote
   # rules).
   'books': [('Jātakaṭṭhakathā', 5, 391, 0, 1690, None)],
   'stems': r'jātaka|jākaka|vagga|nipāta|vaṇṇanā|kathā',
   'n_scope': 'nipata',
   'nipatas': 1,
   # !!! A DEFECT IN 2026-07-28l, FIXED 2026-07-28n.  The rebuild's back-matter
   # trim started one page late and left the word index's first two paragraphs
   # in the corpus, where the reader drew them as body text.  Hidden, not
   # deleted.  Same page-numbering slip as 41KhuA22.
   'no_reprint': True,
   'backmatter': [1688, 1689],
 },
 '43KhuA24': {
   # The Saddhammapajjotikā on the Mahāniddesa.  ONE book, one homage page.
   # CORPUS REBUILT 2026-07-28i: 209 ¶ -> 214, restoring 5 unnumbered
   # paragraphs and trimming 286 back-matter ones — the volume's word index
   # runs 113 printed pages.  Bad pages 8 -> 0.  The shipped corpus began at
   # printed p13; the Ganthārambhakathā, pp5-12, was missing.
   'books': [('Mahāniddesaṭṭhakathā', 5, 423, 0, 214, None, 'katha')],
   'colofix': {'Saddhammapajjotikāya Mahāniddesaṭṭhakathāya'},
   # The last pāda of a display gāthā, carrying the VERSE NUMBER `(1)` — which
   # is what took it into the heading test, since a parenthesised tail is what
   # `HEADTXT` allows a heading to end with.  Body text (p149).
   'headskip': ('Tathāgato vuccati tena cakkhumāti. (1)',),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|nigamana|mātikā'),
   'n_scope': 'vagga',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '44KhuA25': {
   # The Saddhammapajjotikā on the Cūḷaniddesa; 43KhuA24 is its Mahāniddesa
   # half.  CORPUS REBUILT 2026-07-28j: 145 ¶ -> 152.  Bad pages 17 -> 1 (the
   # footnote rule again).
   'books': [('Cūḷaniddesaṭṭhakathā', 6, 145, 0, 152, None, 'katha')],
   # !!! THE COMMENTARY'S OWN NAME IS SPELT DIFFERENTLY IN THE TWO HALVES.
   # 43KhuA24 sets `Saddhammapajjotikāya`; this volume sets
   # `SaddhammaPPajjotikāya` with a double `p`, thirteen times.  Both preserved
   # as printed; neither volume is corrected to match the other.
   'colofix': {
               'Aṭṭhamagāthāniddesavaṇṇanā.',
               'Catutthagāthāniddesavaṇṇanā.',
               'Chaṭṭhagāthāniddesavaṇṇanā.',
               'Dasamagāthāniddesavaṇṇanā.',
               'Dutiyagāthāniddesavaṇṇanā.',
               'Navamagāthāniddesavaṇṇanā.',
               'Pañcamagāthāniddesavaṇṇanā.',
               'Paṭhamagāthāniddesavaṇṇanā.',
               'Sattamagāthāniddesavaṇṇanā.',
               'Tatiyagāthāniddesavaṇṇanā.','Saddhammappajjotikāya Cūḷaniddesaṭṭhakathāya',
               'Saddhammappajjotikā nāma',
               # a section colophon the edition leaves without its stop, so it
               # fails the form test the way 48AbhiA01's did
               'Kappamāṇavasuttaniddesavaṇṇanā niṭṭhitā'},
   # Four prose LEAD-IN lines that end in the citation dash and introduce a
   # display gāthā, and one quoted pāda.  All body text (pp43-44, 74).
   'headskip': ('Tattha–', 'Tassāyeva sandhārakaṁ–', 'Tassāpi sandhārako–',
                'Evaṁ saṇṭhite cettha yojanānaṁ–',
                'Tathāvidhaṁ sappurisaṁ vadantī”ti.3'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|nigamana|mātikā'),
   'n_scope': 'vagga',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '46KhuA27': {
   # The Saddhammappakāsinī on the Paṭisambhidāmagga, FIRST volume; 47KhuA28
   # continues it, and the body's numbering runs on across the two.
   # CORPUS REBUILT 2026-07-28j: 165 ¶ -> 185, restoring 20 unnumbered
   # paragraphs and trimming 170 back-matter ones.  Bad pages 16 -> 1, and that
   # one is the footnote RULE again.  The shipped corpus began at printed p18.
   'books': [('Paṭisambhidāmaggaṭṭhakathā', 7, 351, 0, 185, None, 'katha')],
   'colofix': {'Saddhammappakāsiniyā Paṭisambhidāmaggaṭṭhakathāya',
               'Saddhammappakāsinī nāma',
               # the volume's own closing frame, and one section colophon whose
               # first line is this long
               'Iti Saddhammappakāsiniyā',
               'Niddesavārasaṅgahitassa vissajjanuddesassa'},
   # FOUR BLOCK-QUOTATION LINES from the viññāṇaṭṭhiti passage, read as
   # headings — the edition sets the same sentence four times with the
   # āyatana's name changed, and capitalises `Ākāsānañcāyatanaṁ` in two of the
   # four and not in the other two.  All four named as printed.
   # Plus two citation-dash / verse-number pādas that have each been needed in
   # another volume already: `Tathāgato vuccati tena cakkhumāti. (1)` is
   # 43KhuA24's, and `Paññāyete pidhīyare”ti4–` is 48AbhiA01's with a different
   # footnote marker.
   'headskip': ('Santi bhikkhave sattā sabbaso Ākāsānañcāyatanaṁ samatikkamma',
                'Santi bhikkhave sattā sabbaso ākāsānañcāyatanaṁ samatikkamma',
                'Santi bhikkhave sattā sabbaso viññāṇañcāyatanaṁ samatikkamma',
                'Tathāgato vuccati tena cakkhumāti. (1)',
                'Paññāyete pidhīyare”ti4–'),
   # TWO MĀTIKĀ ENTRIES ON ONE PRINTED LINE, separated by a SINGLE space, so
   # `split_centre`'s three-space rule cannot see it: p12 sets
   # `1. Ñāṇakathā mātikāvaṇṇanā` where the mātikā lists `1. Ñāṇakathā` and
   # `Mātikāvaṇṇanā`.  The printed lower-case `m` is kept.
   'split_literals': {
     '1. Ñāṇakathā mātikāvaṇṇanā': ('1. Ñāṇakathā', 'mātikāvaṇṇanā'),
   },
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'bhājanīya|nigamana|mātikā|ñāṇa'),
   'n_scope': 'vagga',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '45KhuA26': {
   # The Netti-aṭṭhakathā of Dhammapāla.  ONE book, printed 6-281, one homage
   # page.  A NUMBER OPENS PROSE, so `katha`; the numbers restart inside the
   # work, so `n_scope: 'vagga'`.
   # CORPUS REBUILT 2026-07-28p: 146 ¶ -> 154.  Bad pages 25 -> 0.
   'books': [('Netti-aṭṭhakathā', 6, 281, 0, 154, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'bhājanīya|nigamana|mātikā|ñāṇa|hāra|naya|saṅkhepa|pada'),
   'n_scope': 'vagga',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '47KhuA28': {
   # The Saddhammappakāsinī on the Paṭisambhidāmagga, SECOND volume, and the
   # two are one continuous work: the body opens at `111.` where 46KhuA27 left
   # off.  ONE book, printed 8-330, one homage page.
   #
   # CORPUS REBUILT 2026-07-28h: 205 ¶ -> 214, restoring 11 unnumbered
   # paragraphs and TRIMMING 232 back-matter ones — the shipped corpus carried
   # the volume's 70-page word index, two of whose pages were numbered
   # paragraphs (`1. 331; Saṁ-Ṭṭha 2. 41)  236 …`).  Bad pages 2 -> 0; the two
   # were printed pp329-330, the closing uddāna gāthās and the nigamana.
   'books': [('Paṭisambhidāmaggaṭṭhakathā', 8, 330, 0, 214, None, 'katha')],
   # The two-line colophon frame, eight times, plus the volume's own closing
   # line — the same shape as every other commentary in the layer.
   'colofix': {'Saddhammappakāsiniyā Paṭisambhidāmaggaṭṭhakathāya',
               'Saddhammappakāsinī nāma'},
   # Two quoted verse pādas closing a block quotation with the citation dash,
   # each read on its printed page: p267 (the `Padumaṁ yathā kokanadaṁ` verse
   # Mahāpanthaka gives Cūḷapanthaka — **the THIRD volume to need this same
   # verse** after 52Vism02 and 51Vism01's neighbourhood) and p286 (the
   # Māradhītaro verse).
   'headskip': ('Tapantamādiccamivantalikkhe”ti3–',
                'Pādāpi naṁ samphusituṁ na icche”ti3–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|vatthu|'
             r'vāra|vāro|uddāna|niddesa|niddeso|kaṇḍa|bhāṇavāra|nidāna|'
             r'bhājanīya|nigamana|mātikā|ñāṇa'),
   'n_scope': 'vagga',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '48AbhiA01': {
   # The AṬṬHASĀLINĪ, on the Dhammasaṅgaṇī: ONE book, one homage page (p16),
   # printed text 16-469 with the folio confirming both edges (p15 is roman
   # `xii`, p470 opens the back matter).  344 corpus paragraphs of which 310
   # carry a number; `n` runs to 1577 with SIX resets, and only THREE of them
   # return to 1 — ord30 (`1. “Kusalā dhammā…”`, the Tikamātikā), ord52
   # (`1-6. Dukamātikāyaṁ pana…`) and ord70 (`1. Idāni yathāni nikkhittāya
   # mātikāya…`, the Cittuppādakaṇḍa proper).  The other three are BACK-STEPS
   # (269->177, 452->427, 1313->1216) and so are not boundaries — the same
   # reading 17AnA01 and 19AnA03 forced.  The three that DO return to 1 are not
   # boundaries either: they are the DHAMMASAṂGAṆĪ’S OWN numbering restarting
   # under the commentary, and the volume prints ONE homage, so `books` takes
   # ONE entry and the kaṇḍas are `tops` inside it.
   'books': [('Aṭṭhasālinī-aṭṭhakathā', 16, 469, 0, 344, None, 'katha')],
   # The colophon frame prints in TWO forms, measured over the body: the
   # hyphenated `…Dhammasaṅgaha-aṭṭhakathāya` four times and the compounded
   # `…Dhammasaṅgahaṭṭhakathāya` once.  Both are declared; neither is corrected.
   'colofix': {'Aṭṭhasāliniyā Dhammasaṅgaha-aṭṭhakathāya',
               'Aṭṭhasāliniyā Dhammasaṅgahaṭṭhakathāya',
               # THREE MORE COLOPHON LINES, each read as a heading for its own
               # reason, and each checked on the printed page first.
               #  * `Niṭṭhitā ca tīhi mahāvārehi maṇḍetvā niddiṭṭhassa`
               #    (printed p199) is the FIRST line of a two-line section
               #    colophon whose second is `Paṭhamacittassa atthavaṇṇanā.` —
               #    the same shape as 12MaA03's, and the reason that one has to
               #    be looked at rather than suppressed.
               #  * `Aṭṭhakathākaṇḍavaṇṇanā niṭṭhitā` (p451) IS a colophon by
               #    every other test and fails only on the terminal stop, WHICH
               #    THE EDITION OMITS HERE and prints on all four of its
               #    siblings (`Cittuppādakaṇḍakathā niṭṭhitā.`,
               #    `Rūpakaṇḍavaṇṇanā niṭṭhitā.`, `Nikkhepakaṇḍavaṇṇanā
               #    niṭṭhitā.`, `kāmāvacarakusalaniddeso samatto.`).  Recorded
               #    as an erratum of the edition; NOT corrected — the missing
               #    stop stays missing and only the role is named.
               #  * `Aṭṭhasālinī nāma` (p454) is the first line of the volume's
               #    closing colophon, second line `Dhammasaṅgaha-aṭṭhakathā
               #    niṭṭhitā.` — the same line-shape 18AnA02 needed for
               #    `Manorathapūraṇī nāma`.
               'Niṭṭhitā ca tīhi mahāvārehi maṇḍetvā niddiṭṭhassa',
               'Aṭṭhakathākaṇḍavaṇṇanā niṭṭhitā',
               'Aṭṭhasālinī nāma'},
   # THREE BODY LINES READ AS HEADINGS, all quotation, none suppressed as text:
   # two citation-dash pādas closing a quoted gāthā (`Sikkhāpahānagambhī-…` on
   # p22, `Paññāyete pidhīyare”ti3–` on p385) and one opening line of an
   # indented Milindapañha block quotation (p185) — the THIRD volume to need
   # that same Milindapañha passage after 09DiA03 and 49AbhiA02.  Every one of
   # these stays exactly where it is; only its role changes.
   'headskip': ('Sikkhāpahānagambhī-bhāvañca paridīpayeti–',
                'Dukkaraṁ mahārāja Bhagavatā katanti. Kiṁ bhante',
                'Paññāyete pidhīyare”ti3–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vibhaṅga|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|'
             r'nidāna|bhājanīya|pucchaka|nigamana|mātikā'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '50AbhiA03': {
   # !!! A COLOPHON THE WHOLE-WORD RULE CANNOT REACH (2026-07-30i): a ONE-WORD
   # COMPOUND in which the ordinal is the FIRST MEMBER and so carries no ending
   # of its own — `Paṭhamavaggavaṇṇanā.`, not `Paṭhamo vaggo.`  Naming them is
   # deliberate: a general "one-word capitalised stopped line" rule was tried and
   # newly claimed TWENTY lines, which is exactly what `kat_is_colo`'s form (2)
   # guards behind a centring test.  Read off the page, one by one, from the
   # release sweep in `_tika/colo_final.log`.
   'colofix': {
               'Catutthovaggo.',
   },

   # The PAÑCAPAKARAṆA-AṬṬHAKATHĀ: FIVE books in one volume, each with its own
   # title page and homage, measured — `scout_volume 50AbhiA03 extent` finds
   # five homage pages and the five title lines read
   # `Dhātukathā-aṭṭhakathā`, `Puggalapaññatti-aṭṭhakathā`,
   # `Kathāvatthu-aṭṭhakathā`, `Yamakappakaraṇaṭṭhakathā` and
   # `Paṭṭhānappakaraṇaṭṭhakathā`.  That is the check: the Abhidhamma's last
   # five books are exactly these, and 29Abhi01/30Abhi02 hold the first two.
   #
   # !!! THE 37 `n` RESETS ARE NOT BOUNDARIES.  Only four of them fall at a
   # title page; the rest are the NAYA restarts inside the Dhātukathā and the
   # Paṭṭhāna, where the edition numbers each naya from 1 — and several of the
   # "resets" `scout_volume` reports are not paragraphs at all but printed
   # HEADINGS leaked into the corpus (`7. Sattamanaya sampayuttena-
   # vippayuttapadavaṇṇanā`), which carry the heading's own ordinal.  The book
   # boundaries come from the HOMAGE PAGES and are checked against the corpus
   # paragraph that opens each one.
   'books': [('Dhātukathā-aṭṭhakathā',        14,  37,   0,  64, None, 'katha'),
             ('Puggalapaññatti-aṭṭhakathā',   38, 117,  64, 210, None, 'katha'),
             ('Kathāvatthu-aṭṭhakathā',      118, 299, 210, 606, None, 'katha'),
             ('Yamakappakaraṇaṭṭhakathā',    300, 353, 606, 688, None, 'katha'),
             ('Paṭṭhānappakaraṇaṭṭhakathā',  354, 512, 688, 883, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vibhaṅga|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|'
             r'nidāna|bhājanīya|pucchaka|nigamana|mātikā|yamaka|paṭṭhāna|'
             r'paññatti|naya'),
   # A DIVISION HEAD SHARING ITS PRINTED LINE WITH ITS FIRST SUBDIVISION — the
   # shape 36Abhi08 named and this volume repeats four times in the Paṭṭhāna's
   # Pucchāvāra and once in the Yamaka's Niddesa, always with a run of spaces
   # between the two halves.  The volume's own front mātikā confirms every one
   # of the pairs (idx 9 and 11 centre the outer name above the numbered list).
   'split_unnumbered': True,
   # ...AND TWICE THE EDITION SETS THAT PAIR WITH A SINGLE SPACE, where the
   # rule above wants three, so the line stayed whole and rendered as one
   # heading with a space in the middle.  Named, one line at a time, exactly as
   # 37Abhi09's p289 slip is.  The third is the Yamaka's own opening, where the
   # outer name is NUMBERED and the inner one is not — and the edition prints
   # the inner one in LOWER CASE (`uddesavāravaṇṇanā` where its mātikā, p vi,
   # sets `Uddesavāravaṇṇanā`).  The printed reading is kept as printed; the
   # nav names the pair.
   'split_literals': {
     'Mahāvāra 1. Anusayavāravaṇṇanā':
         ('Mahāvāra', '1. Anusayavāravaṇṇanā'),
     'Paccayaniddesa 1. Hetupaccayaniddesavaṇṇanā':
         ('Paccayaniddesa', '1. Hetupaccayaniddesavaṇṇanā'),
     '1. Mūlayamaka uddesavāravaṇṇanā':
         ('1. Mūlayamaka', 'uddesavāravaṇṇanā'),
   },
   # THREE QUOTED VERSE PĀDAS closing an indented block quotation, read as
   # headings because they open with a capital and carry no terminal stop.  All
   # three are body text and stay where they are; only the role changes.  Each
   # was read on its printed page first: p8 (the Dhātukathā's uddāna gāthā),
   # p41 (the Sutta-nipāta's Upasīvamāṇavapucchā, quoted twice on the page —
   # the FIRST printing ends `saṅkhaṁ.` and is not flagged) and p177 (the
   # Dhammapada's `Alaṅkato cepi samaṁ careyya` verse).
   # ...and FIVE more in the Paṭṭhāna's closing pages: the last pāda of the
   # `Tikañca Paṭṭhānavaraṁ dukuttamaṁ` gāthā, which the edition prints four
   # times with a different fourth line each time (pp482, 483, 483, 484), and
   # the one-word lead-in `Ettāvatā–` that introduces it.  All body text.
   'headskip': ('Anidassanaṁ punadeva sappaṭighaṁ upādā”ti–',
                'Atthaṁ paleti1 na upeti saṅkhan”ti2–',
                'So brāhmaṇo so samaṇo sa bhikkhū’ti”1',
                'Cha anulomamhi nayā sugambhīrāti–',
                'Cha paccanīyamhi nayā sugambhīrāti–',
                'Cha anulomapaccanīyamhi nayā sugambhīrāti–',
                'Cha paccanīyānulomamhi nayā sugambhīrāti–',
                'Ettāvatā–'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '49AbhiA02': {
   # The Sammohavinodanī, on the Vibhaṅga: ONE book, 0 corpus `n` resets, n
   # runs to 1030.  Its only gap was the unnumbered NIGAMANAKATHĀ at the end
   # (printed pp516-517) plus one short page — the same shape as 13MaA04's.
   'books': [('Vibhaṅgaṭṭhakathā', 10, 517, 0, 335, None, 'katha')],
   # The colophon frame, 18 times, one form only (measured: `grep -o` returns
   # a single variant).  This volume prints NO citation-dash pāda, so
   # `headskip` is absent by measurement rather than by omission.
   'colofix': {
               'Catutthabalaniddesavaṇṇanā.',
               'Chaṭṭhabalaniddesavaṇṇanā.',
               'Dutiyabalaniddesavaṇṇanā.',
               'Navamabalaniddesavaṇṇanā.',
               'Pañcamabalaniddesavaṇṇanā.',
               'Paṭhamabalaniddesavaṇṇanā.',
               'Sattamabalaniddesavaṇṇanā.',
               'Tatiyabalaniddesavaṇṇanā.','Sammohavinodaniyā Vibhaṅgaṭṭhakathāya'},
   # THREE LINES INSIDE INDENTED BLOCK QUOTATIONS, read as headings — not
   # citation-dash pādas but the same underlying cause, a quoted line that
   # happens to open with a capital and end without a stop.  Two are from the
   # Milindapañha passage on why two Buddhas do not arise at once, and one of
   # them — `Sammāsambuddhā ekakkhaṇe nuppajjanti. Yadi mahārāja dve` — is the
   # SAME LINE 09DiA03 quotes and needed `headskip` for.  The third closes a
   # kuhanavatthu quotation.  All three are body text and stay exactly where
   # they are; only the role changes.
   'headskip': ('Sammāsambuddhā ekakkhaṇe nuppajjanti. Yadi mahārāja dve',
                'Buddho”ti “asamasamo Buddho”ti “appaṭisamo Buddho”ti “appaṭibhāgo',
                'Yath’āha–katamaṁ sāmantajappanasaṅkhātaṁ'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vibhaṅga|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|'
             r'nidāna|bhājanīya|pucchaka|nigamana|mātikā'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },
 # === THE AṄGUTTARA-AṬṬHAKATHĀ (Manorathapūraṇī), three bhāgas =============
 # !!! EACH VOLUME PRINTS ONE HOMAGE PAGE AND EACH CARRIES SEVERAL NIPĀTAS, so
 # the homage scan is useless here and the book boundaries come from the `n`
 # RESETS and the printed title pages instead.  That is the trap 2026-07-27j
 # recorded, where the edition misprinted the homage itself and hid a whole
 # book from `scout_volume.py`'s scan; only the reset found it.
 #
 # ELEVEN BOOKS ACROSS THE THREE VOLUMES, WHICH IS THE CHECK: the Aṅguttara has
 # eleven nipātas — Ekaka, Duka, Tika, Catukka, Pañcaka, Chakka, Sattaka,
 # Aṭṭhaka, Navaka, Dasaka, Ekādasaka — and 1 + 3 + 7 accounts for every one.
 #
 # ...AND NOT EVERY RESET IS A BOOK BOUNDARY.  17AnA01's only reset is a
 # BACK-STEP (394 -> 389) whose paragraph reads `389-401. Iddhipādesu chandaṁ…`
 # — a peyyāla RANGE, not a new book; 19AnA03 ord171 is the same shape
 # (294 -> 250).  A reset is a boundary only when it returns to 1.
 '17AnA01': {
   # !!! A COLOPHON THE WHOLE-WORD RULE CANNOT REACH (2026-07-30i): a ONE-WORD
   # COMPOUND in which the ordinal is the FIRST MEMBER and so carries no ending
   # of its own — `Paṭhamavaggavaṇṇanā.`, not `Paṭhamo vaggo.`  Naming them is
   # deliberate: a general "one-word capitalised stopped line" rule was tried and
   # newly claimed TWENTY lines, which is exactly what `kat_is_colo`'s form (2)
   # guards behind a centring test.  Read off the page, one by one, from the
   # release sweep in `_tika/colo_final.log`.
   'colofix': {
               'Catutthavaggavaṇṇanā.',
               'Dutiyavaggavaṇṇanā.',
               'Paṭhamavaggavaṇṇanā.',
               'Tatiyavaggavaṇṇanā.',
   },

   'books': [('Ekanipātaṭṭhakathā', 18, 433, 0, 229, None, 'katha')],
   # Two last pādas closing with the citation dash — the Sātāgira/Hemavata
   # dialogue quoted from the Suttanipāta, each stanza carrying its speaker tag
   # in parentheses inside the FIRST pāda and the citation dash on the last.
   'headskip': ('Handa passāma Gotaman”ti–',
                'Saṅkappa’ssa vasīkatā”ti1–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|nipāta|nipāto|paṇṇāsaka|vagga|'
             r'vaggo|pāḷi|aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '18AnA02': {
   # The page boundaries are the PRINTED OPENINGS, found by locating each
   # nipāta's own first line (`N. Xnipātassa paṭhame …`), not inferred from the
   # corpus `pdf_page` — whose offset is per volume and is 0 here and -1 in
   # 19AnA03.  Derived from the corpus they were a page out at both seams and
   # the 1:1 count refused: the Tikanipāta's last unit sits on 1-based p266 and
   # the Catukkanipāta opens on p268, with p267 BLANK between them.
   # ord463 is a real unit with the NEXT heading glued onto its tail by the
   # extraction — see `leak_keep` in the leaked-heading test.  RECORDED, not
   # corrected: the paragraph renders as the edition's own text, and the
   # heading it swallowed is also drawn from the printed stream above it.
   'leak_keep': {463},
   'colofix': {'Manorathapūraṇiyā Aṅguttaranikāyaṭṭhakathāya'},
   'headskip': ('Eko care khaggavisāṇakappo”ti2–',),
   # `head_paren` — the mātikā lists TEN vaggas the heads stream does not have,
   # `(6) 1. Puggalavaggavaṇṇanā` through `(15) 5. Samāpattivaggavaṇṇanā`, every
   # one numbered TWICE by the edition and so opening with `(`, which
   # `kat_is_head` never reaches.  Same key and cause as 16SamA03's and the
   # Aṅguttara canon's (2026-07-27j).
   'head_paren': True,
   'books': [('Dukanipātaṭṭhakathā',     20,  87,   0, 140, None, 'katha'),
             ('Tikanipātaṭṭhakathā',     88, 267, 140, 277, None, 'katha'),
             ('Catukkanipātaṭṭhakathā', 268, 416, 277, 465, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|nipāta|nipāto|paṇṇāsaka|vagga|'
             r'vaggo|pāḷi|aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },
 '19AnA03': {
   'books': [('Pañcakanipātaṭṭhakathā',    28, 113,   0, 176, None, 'katha'),
             ('Chakkanipātaṭṭhakathā',    114, 171, 176, 259, None, 'katha'),
             ('Sattakanipātaṭṭhakathā',   172, 219, 259, 309, None, 'katha'),
             ('Aṭṭhakanipātaṭṭhakathā',   220, 283, 309, 377, None, 'katha'),
             ('Navakanipātaṭṭhakathā',    284, 313, 377, 417, None, 'katha'),
             ('Dasakanipātaṭṭhakathā',    314, 369, 417, 507, None, 'katha'),
             ('Ekādasakanipātaṭṭhakathā', 370, 384, 507, 517, None, 'katha')],
   # The frame five times, plus the WHOLE WORK's closing colophon — this is the
   # last bhāga of the Manorathapūraṇī.
   'colofix': {'Manorathapūraṇiyā Aṅguttaranikāyaṭṭhakathāya', 'Manorathapūraṇī nāma'},
   # TWO HEADINGS ON ONE PRINTED LINE, and `head_paren` is what hid it: with
   # the key on, `kat_is_head` claims the WHOLE line before the
   # `_is_double_head` branch below can see it, so the vagga and the
   # suttavaṇṇanā arrived as a single heading and the mātikā reported
   # `1. Āvaraṇasuttavaṇṇanā` absent from the tree.
   # A CENSUS, not a discovery one at a time: over all three Aṅguttara
   # commentary volumes exactly ONE heading line carries a 3-or-more space run
   # separating two halves — 17AnA01 has none, 18AnA02 none, this one has this.
   'split_literals': {
     '(6) 1. Nīvaraṇavagga 1. Āvaraṇasuttavaṇṇanā':
         ['(6) 1. Nīvaraṇavagga', '1. Āvaraṇasuttavaṇṇanā'],
   },
   'headskip': ('Saṇikaṁ jīrati āyupālayan”ti1–',),
   'head_paren': True,
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|nipāta|nipāto|paṇṇāsaka|vagga|'
             r'vaggo|pāḷi|aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },
 # === THE SAṀYUTTA-AṬṬHAKATHĀ (Sāratthappakāsinī), three bhāgas ============
 # Scouted 2026-07-27ak.  The layer census puts all three at 95-96% coverage,
 # and the per-page test confirms it.  The bhāga division is the EDITION'S and
 # does not follow the canon's: 14SamA01 is the Sagāthāvagga alone, while
 # 15SamA02 and 16SamA03 carry TWO books each — the cover says so
 # (`Nidānavaggapāḷiyā **ca** Khandhavaggapāḷiyā **ca** saṁvaṇṇanābhūtā`), the
 # HOMAGE pages say so (1-based 20 and 248; 24 and 176), and the corpus `n`
 # RESET says so (ord188 246->1; ord156 420->1).  Three witnesses agreeing.
 '14SamA01': {
   # !!! THE EDITION MISPRINTS A UNIT RANGE'S SEPARATOR, AND IT COST A UNIT.
   # 0-based p114 sets `64.65. Catutthe kiṁsu saṁyojanoti…` with a PERIOD
   # where the range separator belongs — its own neighbours four lines above
   # read `62-63. Dutiye…` and the heading over it reads `4-5.
   # Saṁyojanasuttādivaṇṇanā`, so the intended number is `64-65.`.
   # `extract.py`'s PARA wants `\.\s+` and `64.65.` offers no space, so the
   # extraction saw NO BOUNDARY and the whole unit arrived inside the
   # paragraph carrying n=62: printed 255 units against 254 corpus paragraphs,
   # and the 1:1 count REFUSED to build.  Same shape as 36Abhi08's
   # `41.Nevavipāka…`, and the same key.
   # **The misprint is PRESERVED** (working principle 3): `mark` is the printed
   # unit's WHOLE FIRST LINE exactly as the edition sets it, which is also what
   # renders — declared shorter, all three of the declaration's own tests still
   # pass and the continuation lines join onto a truncated opening.
   'kat_splices': [
     {'ord': 59, 'into': 62, 'n': 64, 'pg': 114,
      'mark': '64.65. Catutthe kiṁsu saṁyojanoti kiṁsaṁyojano kiṁbandhano.'},
   ],
   'books': [('Sagāthāvaggasaṁyuttaṭṭhakathā', 26, 350, 0, 254, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|saṁyutta|saṁyuttaṁ|vagga|vaggo|'
             r'pāḷi|aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # The colophon frame again — the Sāratthappakāsinī's, in the two forms this
   # volume prints (with and without the opening `Iti`), three times in all.
   # Same class as the Papañcasūdanī's and the Sumaṅgalavilāsinī's.
   'colofix': {'Sāratthappakāsiniyā Saṁyuttanikāyaṭṭhakathāya',
               'Iti Sāratthappakāsiniyā Saṁyuttanikāyaṭṭhakathāya'},
   # Three last pādas closing with the citation dash.  `Nāgo tādi pavuccate
   # tathattā”ti–` is the SAME pāda 10MaA01 quotes, and it carries a footnote
   # marker there (`…tathattā”ti1–`) and none here — which is exactly why the
   # literal is the printed line and cannot be shared between volumes.
   'headskip': ('Bhikkhūpi te hehinti kāmabhogī”ti–',
                'Nāgo tādi pavuccate tathattā”ti–',
                'Jarābhivegena maddiyantī”ti–'),
 },
 '15SamA02': {
   # THE EDITION MISPRINTS A RANGE SEPARATOR AGAIN, and this time in a HEADING.
   # 0-based p211 sets `3. 10. Suvaṇṇanikkhasuttādivaṇṇanā` where its own
   # mātikā reads `3-10.` and its neighbour four lines above reads
   # `1-2. Suvaṇṇapātisuttādivaṇṇanā`.  The stray period made the line match
   # `VERSE`, and the internal period then failed the numbered-heading test, so
   # it was read as a numbered UNIT: 189 printed against 188 corpus, and the
   # 1:1 count refused to build.  Sister erratum to 14SamA01's `64.65.`, and
   # the misprint is PRESERVED — `headfix` names the line exactly as printed.
   'headfix': ('3. 10. Suvaṇṇanikkhasuttādivaṇṇanā',),
   'books': [('Nidānavaggasaṁyuttaṭṭhakathā',   20, 247,   0, 188, None, 'katha'),
             ('Khandhavaggasaṁyuttaṭṭhakathā', 248, 343, 188, 300, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|saṁyutta|saṁyuttaṁ|vagga|vaggo|'
             r'pāḷi|aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   'colofix': {'Iti Sāratthappakāsiniyā Saṁyuttanikāyaṭṭhakathāya'},
   # Three last pādas closing with the citation dash, checked on the page.
   'headskip': ('Na ca parittase tāni alabhamāno”ti1–',
                'Pucchāmi taṁ Mātali devasārathī”ti2–',
                'Paññāyete pidhīyare”ti3–'),
 },
 '16SamA03': {
   'books': [('Saḷāyatanavaggasaṁyuttaṭṭhakathā', 24, 175,   0, 156, None, 'katha'),
             ('Mahāvaggasaṁyuttaṭṭhakathā',      176, 364, 156, 389, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|saṁyutta|saṁyuttaṁ|vagga|vaggo|'
             r'pāḷi|aṭṭhakathā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|'
             r'duka|tika|catukka|pañcaka|chakka|sattaka|aṭṭhaka|navaka|'
             r'dasaka|tiṁsaka|navutika'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # The frame twice, plus the WHOLE WORK's closing colophon — this is the last
   # bhāga of the Sāratthappakāsinī, so 0-based p388 sets
   # `Sāratthappakāsinī nāma / Saṁyuttanikāyaṭṭhakathā niṭṭhitā.`  The same two
   # words head the COVER (p8), which is outside this book's page range.
   # This volume prints NO citation-dash pāda: `headskip` is empty by
   # measurement, not by omission.
   'colofix': {'Iti Sāratthappakāsiniyā Saṁyuttanikāyaṭṭhakathāya',
               'Sāratthappakāsinī nāma'},
   # `head_paren` — the edition numbers one section TWICE, `(6) 1.
   # Avijjāvaggavaṇṇanā` (0-based p1149 of the layout, and its own mātikā lists
   # it the same way).  `kat_is_head` wants a capital, and a line opening with
   # `(` never reaches it, so the heading did not exist in the stream at all
   # and the nav REFUSED: "in the mātikā, absent from the tree".  Same key and
   # same cause as the Aṅguttara's `(6) 1. Brāhmaṇavagga` (2026-07-27j).
   'head_paren': True,
 },
 # --- 11MaA02: the Mūlapaṇṇāsa commentary, second bhāga --------------------
 # !!! ITS GAP IS IN THE MIDDLE, WHICH NO VOLUME'S HAS BEEN BEFORE.  Its corpus
 # ran ¶239 (`pdf_page` 310) straight to ¶240 (317): printed pp311-316, six
 # pages of the Brahmanimantanika narrative, in no paragraph at all — dropped
 # by `extract.py` for the usual reason (unnumbered) but not at a boundary a
 # front-matter rebuild would reach.  `_fnprobe/rebuild_corpus.py` had never
 # been asked for a mid-volume run and is now measured on one: **position in
 # the volume is irrelevant to it** — the restored `else` opens an unnumbered
 # paragraph wherever the numbering stops, and the flush-at-headings bound
 # applies the same.  Four unnumbered paragraphs recovered, anchored pp312-314
 # and running through 316.
 #     before   corpus 92% of printed chars   5 pages more than half absent
 #     after    corpus 93%                    0 pages
 # 249 -> 256 ¶ after trimming 162 back-matter ¶ (58 index pages); every one of
 # the 249 shipped paragraphs survives text for text; `pdf_page` monotonic.
 '11MaA02': {
   'books': [('Mūlapaṇṇāsaṭṭhakathā', 6, 325, 0, 256, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|bhāga'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # The colophon frame, 30 times, all correct in this volume.
   'colofix': {'Papañcasūdaniyā Majjhimanikāyaṭṭhakathāya'},
   # Eight quoted verse lines read as headings, five distinct — every one the
   # LAST PĀDA of its gāthā, closing with the CITATION DASH.
   # `Suttappabuddhova anussarāmī”ti1–` is printed FOUR times, once per stanza
   # of the Brahmanimantanika's recollection, and three of those four stand in
   # the pages this volume's corpus did not hold until today's rebuild.
   # !!! `Dasadhā byañjanabuddhiyā pabhedoti1–` HAS NO CLOSING QUOTE, where
   # 07DiA01 prints the same pāda as `…pabhedo”ti–`.  The literal is the
   # printed line, so the two volumes cannot share it — and that difference is
   # the edition's, not a transcription slip: 07DiA01 p116 sets the quote mark
   # and 11MaA02 p69 does not.
   'headskip': ('Hitvā tuvaṁ pabbaja brahmadattā”ti3–',
                'Dasadhā byañjanabuddhiyā pabhedoti1–',
                'Yaṁ vuddhamāgacchati esa bhāro”ti3–',
                'Ñatvā sayaṁ lokamimaṁ parañcā”ti3–',
                'Suttappabuddhova anussarāmī”ti1–'),
 },
 # --- 10MaA01: the Mūlapaṇṇāsa commentary, first bhāga ---------------------
 # ITS CORPUS WAS REBUILT FROM THE PDF (2026-07-27ai).  `extract.py` opens a
 # paragraph only on a `NN.` marker, and this volume opens with the
 # Papañcasūdanī's Ganthārambhakathā and Nidānakathā — printed pp1-29, 0-based
 # pdf pp17-46 — which carry no unit number, so none of it existed in any
 # corpus.  **The recipe's one-line test does NOT find this** (2026-07-27ah):
 # the corpus's first `pdf_page` and the body's first printed page are BOTH 18,
 # because its first paragraph is ANCHORED to p18 while the TEXT of pp18-46 is
 # absent.  An anchor is not coverage.  What found it is the per-page
 # measurement — `_fnprobe/cover.py`, "does any printed body page have more
 # than half its long lines absent":
 #     before   corpus 89% of printed chars   22 pages more than half absent
 #     after    corpus 94%                     0 pages
 # 188 -> 197 ¶ after trimming 97 back-matter ¶ (the 34-page word index, which
 # the rebuild restores because it too is unnumbered).  Every one of the 188
 # shipped paragraphs survives text for text; `pdf_page` monotonic 17..414.
 '10MaA01': {
   'books': [('Mūlapaṇṇāsaṭṭhakathā', 18, 415, 0, 197, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|'
             r'ārambha|bhāga'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # The colophon frame, 20 times — this volume prints it correctly every time
   # (measured: `grep -o 'Papañcasūdaniyā \S*'` returns one form, 20 hits).
   # ...AND THE VOLUME'S OWN CLOSING COLOPHON, which the generic form test does
   # NOT claim.  `kat_is_colo` form (1) wants the section name and `niṭṭhita-`
   # ADJACENT; the edition writes `Mūlapaṇṇāsaṭṭhakathāya **paṭhamo bhāgo**
   # niṭṭhito.` (0-based p414) with the bhāga between them, so the line fell
   # through to the body and became a VISIBLE unnumbered corpus paragraph.
   # That is worse than a wrong role here: the reader draws a commentary volume
   # only through `targetsFor()`, and a visible unnumbered paragraph with no
   # LATER numbered paragraph to hang off cannot be linked at all — this one
   # would have been in the corpus, in the tree, and on no page.  `colofix`
   # hides it and `uddana/` draws it, which is what 07DiA01's
   # `Niṭṭhitā ca terasasuttapaṭimaṇḍitassa Sīlakkhandhavaggassa` already does.
   # 13MaA04's `Majjhimanikāyaṭṭhakathā sabbākārena niṭṭhitā.` is the same
   # shape (an adverb between the name and the verb) and the same class.
   'colofix': {'Papañcasūdaniyā Majjhimanikāyaṭṭhakathāya',
               'Mūlapaṇṇāsaṭṭhakathāya paṭhamo bhāgo niṭṭhito.'},
   # Four quoted verse lines read as headings, all last pādas closing with the
   # CITATION DASH.  Two of them — `Idañca me dhīra mahāvimānan”ti` and
   # `Tasmā hi amhaṁ daharā na mīyare”ti` — are the SAME two the Sumaṅgalavilāsinī
   # quotes in 07DiA01, from the Puṇṇaka and Mahādhammapāla jātakas, and they
   # carry DIFFERENT footnote markers here (2 and 1, against 2 and 5 there).
   # The marker is part of the printed line and so part of the literal, which
   # is why these cannot be shared between volumes.
   'headskip': ('Saccavhayo brahme upāsito me”ti3–',
                'Nāgo tādi pavuccate tathattā”ti1–',
                'Idañca me dhīra mahāvimānan”ti2–',
                'Tasmā hi amhaṁ daharā na mīyare”ti1–'),
 },
 '13MaA04': {
   'books': [('Uparipaṇṇāsaṭṭhakathā', 7, 260, 0, 306, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nigamana'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # THE COLOPHON FRAME, 52 TIMES — and this volume prints a SECOND misprint of
   # it, a different one from 12MaA03's.  0-based p88, closing the
   # Sāmagāmasuttavaṇṇanā, sets `Papañcasūdaniyā **K**ajjhimanikāyaṭṭhakathāya`.
   # So across the two Majjhima commentary volumes built so far the frame is
   # printed 102 times and the edition misspells it twice, each differently
   # (12MaA03 p188 `majjhimanikāyaṭṭhākathāya`, here `Kajjhima-`).  **Both
   # preserved**, both NAMED so the line gets its right role.
   # The third literal is the WHOLE WORK's closing colophon (p292):
   #     Papañcasūdanī nāma
   #     Majjhimanikāyaṭṭhakathā sabbākārena niṭṭhitā.
   # The same two words also head the TITLE PAGE, which is 0-based p0 and
   # outside this book's page range, so nothing else can match.
   'colofix': {'Papañcasūdaniyā Majjhimanikāyaṭṭhakathāya',
               'Papañcasūdaniyā Kajjhimanikāyaṭṭhakathāya',
               'Papañcasūdanī nāma'},
   # THREE QUOTED VERSE LINES READ AS HEADINGS, and all three are the same
   # refrain: the Ratanasutta's `Etena saccena suvatthi hotū”ti`, quoted three
   # times in the Nandakovādasuttavaṇṇanā's account of the golden plate
   # (0-based pp198-200).  Each is the LAST PĀDA of its stanza and closes with
   # the CITATION DASH, so it becomes the last `vline` of its own block.  Two
   # literals cover the three, because two carry footnote marker 1 and one
   # marker 2 — the marker is part of the printed line and so part of the
   # literal.
   'headskip': ('Etena saccena suvatthi hotū”ti1–',
                'Etena saccena suvatthi hotū”ti2–'),
 },
 '09DiA03': {
   'books': [('Pāthikavaggaṭṭhakathā', 10, 261, 0, 293, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
   # !!! THE ROLES BELOW WERE FOUND BY DECLARING THIS VOLUME'S MĀTIKĀ, WHICH
   # THE NAV SPEC HAD NEVER DECLARED (2026-07-27ai).  All three Dīgha-
   # Aṭṭhakathā volumes print one and none was read, so the nav's mātikā check
   # had nothing to check and reported nothing — the same blind spot 12MaA03's
   # four-dot leader created.  Every literal below was checked on the printed
   # page; not one moves a word, so all three shipped at 0/0/0/0 with these
   # roles wrong.
   # THE COLOPHON FRAME, EIGHT TIMES — seven correct and ONE MISPRINT.  0-based
   # p152 sets `Sumaṅgalavilāsiniyā Dīghanikayaṭṭhakathāya`, short `a` in
   # `nikaya`.  **The misprint is PRESERVED** (working principle 3): the
   # variant is NAMED so the line gets its right role, and what renders is the
   # edition's own reading.  The third literal is the WHOLE BOOK's colophon,
   # `Sumaṅgalavilāsinī nāma / Dīghanikāyaṭṭhakathā niṭṭhitā.` (p292); the same
   # words also stand mid-sentence on p291 (`… katā ayaṁ Sumaṅgalavilāsinī
   # nāma`), but that is a different LINE and `colofix` matches whole lines.
   'colofix': {'Sumaṅgalavilāsiniyā Dīghanikāyaṭṭhakathāya',
               'Sumaṅgalavilāsiniyā Dīghanikayaṭṭhakathāya',
               'Sumaṅgalavilāsinī nāma'},
   # A LINE INSIDE A BLOCK QUOTATION, READ AS A HEADING.  0-based p125 quotes
   # the Milindapañha at a display indent, and one line of that prose happens
   # to open with a capital, carry no comma and end without a stop.  It is body
   # text and stays exactly where it is; only the role changes.
   'headskip': ('Sammāsambuddhā ekakkhaṇe nuppajjanti. Yadi mahārāja dve',),
   # AND ONE REAL HEADING THE COLOPHON BRANCH CLAIMED.  The edition sets
   # `Pañhabyākaraṇādicatukkavaṇṇanā.` (0-based p205) WITH a terminal stop
   # where its neighbours — `Sotāpattiyaṅgādicatukkavaṇṇanā`,
   # `Dakkhiṇāvisuddhādicatukkavaṇṇanā` — print none, so `kat_is_colo` took it
   # and the mātikā lists a section the tree does not have.  `headfix` beats
   # the colophon test, which is what "named" means.
   'headfix': {'Pañhabyākaraṇādicatukkavaṇṇanā.'},
 },

 # --- 01VinA01: ONE BOOK, and 78 pages of it were absent until 2026-07-27s ---
 # Cover `PĀRĀJIKAKAṆḌA-AṬṬHAKATHĀ (Paṭhamo bhāgo)`; inner title page 1-based
 # p15, body p15-359, then the indexes.  Its corpus was rebuilt from the PDF
 # because `extract.py` dropped every line outside a numbered unit and this
 # volume opens with the Ganthārambhakathā and the whole Bāhiranidāna — pages
 # 15-92, unnumbered running prose, the account of the councils.
 '01VinA01': {
   'colofix': {'Samantapāsādikāya Vinayasaṁvaṇṇanāya'},
   'books': [('Pārājikakaṇḍa-aṭṭhakathā', 15, 359, 0, 175, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|saṁghādisesa|'
             r'nidāna|saṅgīti'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 05Kankha: FOUR BOOKS — the two pātimokkhas and then their commentary --
 # Cover `KAṄKHĀVITARAṆĪ-AṬṬHAKATHĀ`, but the volume opens with the CANONICAL
 # text it comments on: `Dvemātikāpāḷi`, the two pātimokkhas, each with its own
 # homage title page.  Only the third book is the aṭṭhakathā proper.  That is
 # why so little of this volume is numbered — a pātimokkha is recited, not
 # numbered — and why its corpus read 19% before the rebuild.
 '05Kankha': {
   # !!! ONE PRINTED VOLUME, TWO LAYERS.  Printed p20 opens `Dvemātikāpāḷi` —
   # the two pātimokkhas, each with its own homage title page, 46% of the
   # printed body — and printed p102 opens `Kaṅkhāvitaraṇī-aṭṭhakathā`, which
   # is what the cover titles the whole volume.  **The Dvemātikāpāḷi appears
   # NOWHERE in the 40 canon volumes**, so this resource holds that canonical
   # text only inside a commentary-layer volume.  Settled 2026-07-28d: the
   # volume stays in the `commentary` layer, which is what it is as published,
   # and the NAV names the two halves for what they are so the provenance is
   # visible.  `manifest.json` carries one layer per volume; making it
   # per-book is a separate, scoped change and is not made here.
   #
   # FOUR BOOKS, and the bounds are the corpus paragraph that carries each
   # homage — NOT the ones this SPEC carried before, which were out by two at
   # the second seam and by three at the third and cost book 4 its whole body
   # the first time the reader was run over it.
   'books': [('Bhikkhupātimokkhapāḷi',       20,  55,   0, 251, None, 'heads'),
             ('Bhikkhunīpātimokkhapāḷi',     56, 101, 251, 591, None, 'heads'),
             ('Kaṅkhāvitaraṇī-aṭṭhakathā',  102, 311, 591, 799, None, 'heads'),
             ('Bhikkhunīpātimokkhavaṇṇanā', 312, 376, 799, 930, None, 'heads')],
   # ord930 and ord931 are the printed WORD INDEX (`Padānukkamo Piṭṭhaṅko`,
   # `Akatasahāyaṁ 295 …`), captured as corpus paragraphs.  Not body text.
   'backmatter': [930, 931],
   # The section colophon frame, TWO lines and sometimes THREE:
   #     [Iti] Kaṅkhāvitaraṇiyā pātimokkhavaṇṇanāya
   #     [Bhikkhunipātimokkhe]
   #     <X>vaṇṇanā niṭṭhitā.
   # Only the last carries a stop, so the lines above it read as headings —
   # eight, five and two occurrences measured over the printed body.  The
   # `Iti` is present twice and absent eight times; both readings are named
   # and neither is corrected.
   'colofix': {
               'Soḷasamavaggo.','Kaṅkhāvitaraṇiyā pātimokkhavaṇṇanāya',
               'Iti Kaṅkhāvitaraṇiyā pātimokkhavaṇṇanāya',
               'Bhikkhunipātimokkhe'},
   # The opening line of the seven adhikaraṇasamathā, set centred under the
   # `Adhikaraṇasamatha` head and carrying no stop, so it read as a second
   # heading — once in each pātimokkha, and the edition spells it differently
   # each time (`samatāya` p35, `samathāya` p81).  BODY TEXT; both readings
   # named as printed and neither corrected.
   'headskip': ('Uppannuppannānaṁ adhikaraṇānaṁ samatāya vūpasamāya',
                'Uppannuppannānaṁ adhikaraṇānaṁ samathāya vūpasamāya'),
   # TWO PRINTED HEADINGS WHOSE NUMBER `HEADNUM` CANNOT READ, both in the
   # Bhikkhunīpātimokkhavaṇṇanā and both listed in the volume's own mātikā:
   # `1 -pa- 4. Methunadhammasikkhāpadavaṇṇanā` (p312) writes the PEYYĀLA into
   # the range, and `8-9-10. Sikkhamāna-ummaddāpanādisikkhāpadavaṇṇanā` (p371)
   # is a TRIPLE range where every other heading in the volume gives a pair.
   # Read as body text, each was located, folded into its paragraph and never
   # became a section — the nav then reported both as mātikā entries with no
   # node.  `headfix` gives them the role; the reading is untouched.
   'headfix': ('1 -pa- 4. Methunadhammasikkhāpadavaṇṇanā',
               '8-9-10. Sikkhamāna-ummaddāpanādisikkhāpadavaṇṇanā'),
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|pātimokkha|nidāna'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },


 # --- 03VinA03: THREE BOOKS, and the numbering runs THROUGH the first seam ---
 # Cover `PĀCITYĀDI-AṬṬHAKATHĀ`, and it holds three works, each opening with
 # its own homage title page (1-based p12 / p184 / p244):
 #     Pācityādi-aṭṭhakathā          p12-183    ord   0-295
 #     Bhikkhunīvibhaṅgavaṇṇanā      p184-243   ord 295-463
 #     Mahāvagga-aṭṭhakathā          p244-448   ord 463-738
 # !!! THE MIDDLE BOUNDARY HAS NO `n` RESET, and that is the edition's doing,
 # not a defect: the Bhikkhunīvibhaṅga's commentary CONTINUES the Pācittiya's
 # unit numbering (ord295 is n=656, straight on from ord294's 655).  Only the
 # third book restarts, at ord463 (1228 -> 1).  Measured, not assumed.
 # p243 is a BLANK page — ord463 carries `pdf_page 243` because the corpus
 # anchored the Mahāvagga's first unit to it; the printed unit begins on p244
 # under the title page.
 '03VinA03': {
   # The Bhikkhunīvibhaṅga's colophons carry the work name on the FIRST line
   # too — `Samantapāsādikāya Vinayasaṁvaṇṇanāya Bhikkhunīvibhaṅge` — so the
   # exact literal 02VinA02 uses does not reach them.
   'colofix': {'Samantapāsādikāya Vinayasaṁvaṇṇanāya',
               'Samantapāsādikāya Vinayasaṁvaṇṇanāya Bhikkhunīvibhaṅge'},
   'books': [('Pācityādi-aṭṭhakathā',      12, 183,   0, 295, None, 'katha'),
             ('Bhikkhunīvibhaṅgavaṇṇanā', 184, 243, 295, 463, None, 'katha'),
             ('Mahāvagga-aṭṭhakathā',     244, 448, 463, 738, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|saṁghādisesa|'
             r'khandhaka|pācittiya|pāṭidesanīya|sekhiya|adhikaraṇa'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,      # 138 of 1104 display lines carry a comma
 },

 # --- 04VinA04: TWO BOOKS ---------------------------------------------------
 # Cover `CŪḶAVAGGĀDI-AṬṬHAKATHĀ`; inner title pages at 1-based p12 and p148.
 '04VinA04': {
   'colofix': {'Samantapāsādikāya Vinayasaṁvaṇṇanāya'},
   # The seam is clean both ways: the `n` run restarts at ord186 (457 -> 1) on
   # exactly the page the Parivāra's title page opens, 1-based p148.
   'books': [('Cūḷavaggādi-aṭṭhakathā', 12, 147,   0, 186, None, 'katha'),
             ('Parivāra-aṭṭhakathā',   148, 276, 186, 300, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|bhāga|khandhaka|parivāra'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,      # 87 of 401 display lines carry a comma
 },

 '06VinSg06': {
   # ONE BOOK, and the simplest of the four: its mātikā (0-based 3-4) is a FLAT
   # list of 36 sections — `Ganthārambhakathā`, 34 numbered
   # `…vinicchayakathā`, `Nigamanakathā` — with no vagga rung at all.
   'books': [('Vinayasaṅgahaṭṭhakathā', 6, 473, 0, 327, None, 'katha')],
   'stems': (r'kathā|vinicchaya|vaṇṇanā|vāra|vāro|pāḷi|uddāna|'
             r'khandhaka|sikkhāpada|saṅgaha'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,      # 208 of 577 display lines carry a comma
   # THE SECTION CLOSING FORMULA, printed at the end of each of the 34
   # vinicchayakathās — "Iti Pāḷimuttakavinayavinicchayasaṅgahe …" — carries no
   # terminal stop, so `kat_is_colo` cannot reach it and the form test claimed
   # it as a HEADING 33 times.  One literal for 33 printings, plus the variant
   # the edition sets once at 0-based p302.
   'colofix': {'Iti Pāḷimuttakavinayavinicchayasaṅgahe',
               'Iti Pāḷimuttakavinayavinicchayasaṅgahe sabbākārato'},
   # THE FOUR THAT REMAIN AFTER THE SUCCESSOR RULE AND THE COLOPHON, each
   # checked on its page.  `Mañcapīṭhādisaṁghikasenāsanesu` is the WRAPPED
   # first half of the running header for section 17, whose full heading is
   # `17. Mañcapīṭhādisaṁghikasenāsanesu paṭipajjitabbavinicchayakathā`;
   # `Byattena bhikkhunā paṭibalena saṁgho ñāpetabbo–` is the kammavācā lead-in
   # and ends in the citation dash; `Ayaṁ tāva …` is quoted prose whose
   # successor happens to open with a capital, which is the one shape the
   # successor rule cannot see.
   'headskip': ['Vinayapiṭaka',
                'Mañcapīṭhādisaṁghikasenāsanesu',
                'Ayaṁ tāva antovasse vassūpanāyikadivasavasena',
                'Byattena bhikkhunā paṭibalena saṁgho ñāpetabbo–'],
 },

 # ==========================================================================
 # THE VINAYA ṬĪKĀ — seven volumes, the subcommentary layer's first builds.
 # Every page and every ordinal below is MEASURED, not carried over from a
 # note: extents at both ends in `_tika/EXTENTS.md`, book heads by a
 # CASE-INSENSITIVE homage scan confirmed against the printed title line
 # (`_tika/bookheads.py`), ord bounds counted off the page (`_tika/ordprobe.py`).
 # Corpora rebuilt and staged 2026-07-29p, installed 2026-07-29q.
 #
 # !!! THE PAGE NUMBERS HERE ARE TRUE 1-BASED PDF PAGES, like every other SPEC
 # in this file — `build()` reads `pdftotext` output directly, so they are NOT
 # the corpus's drifted `pdf_page` (2026-07-29p).  Only `_khua/rebuild.py`'s
 # trim takes corpus units, and those were converted with `_seam/trimbounds.py`.
 #
 # !!! THE SEAM BELONGS TO A WORK'S FIRST VOLUME.  The Ganthārambha +
 # Bāhiranidāna prelude opens a WORK, so 01ViT01, 04ViT04 and 06ViT06 carry it
 # and the continuation volumes 02ViT02, 03ViT03 and 05ViT05 do not.
 # --------------------------------------------------------------------------

 # ==========================================================================
 # THE AṄGUTTARA ṬĪKĀ — three volumes, ELEVEN books, and the books are the
 # NIPĀTAS.
 #
 #   18AnT01  Ekakanipāta-aṅguttaraṭīkā       18-305
 #   19AnT02  Dukanipāta-aṅguttaraṭīkā        18-91    Tika  92-237   Catukka 238-413
 #   20AnT03  Pañcaka  20-99   Chakka 100-167   Sattaka 168-221   Aṭṭhaka 222-285
 #            Navaka  286-323  Dasaka 324-375   Ekādasaka 376-390
 #
 # !!! ONLY THE VOLUME'S FIRST BOOK CARRIES A HOMAGE.  The homage scan returns
 # ONE title page per volume, yet 19AnT02's cover reads `Dukādinipāta` and
 # 20AnT03's `Pañcakādinipāta`.  The inner nipātas open with a blank verso and a
 # centred head and NO homage — so the seam had to be read off the RUNNING
 # HEADER, which prints `Chakkanipāta-aṅguttaraṭīkā`, `Sattakanipāta-…` and so
 # on, one per nipāta.  A homage scan alone would have made these three
 # volumes three books instead of eleven.
 #
 # 20AnT03's blank versos are pp167 and 285, before the Sattaka and the Navaka
 # (`_seam/trimbounds.py`: TRIM 20 388); 18AnT01 needs -1 for a blank at p13 in
 # its front matter; 19AnT02 needs none.
 # --------------------------------------------------------------------------

 '18AnT01': {
   # !!! THE PAṆṆĀSAKA-RELATIVE VAGGA HEAD CARRIES ITS NIPĀTA-WIDE NUMBER IN
   # PARENTHESES — `(6) 1. Puggalavaggavaṇṇanā` — exactly as the canon
   # 15An01-17An03 and the commentary 18AnA02/19AnA03 do, and `kat_is_head`
   # wants the core to open with a CAPITAL.  Without `head_paren` every vagga
   # of every paṇṇāsaka after the first fell through to the body as a
   # paragraph opening: present, contiguous, and in the wrong role, which the
   # body gate reads 0/0/0/0.  THE NAV'S MĀTIKĀ GATE IS WHAT REPORTED IT.
   'head_paren': True,
   'books': [('Ekakanipāta-aṅguttaraṭīkā', 18, 305, 0, 223, None, 'katha')],
   # The colophon frame — `Iti manorathapūraṇiyā aṅguttaranikāyaṭṭhakathāya` /
   # `<X>vaṇṇanāya anuttānatthadīpanā samattā.`, the stop on the second line.
   'colofix': {'Iti manorathapūraṇiyā aṅguttaranikāyaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|nipāta|nipāto|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|paṇṇāsaka'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # !!! THE EDITION SETS TWO UNIT-NUMBER RANGES WITH A PERIOD FOR A SEPARATOR,
 # and the two cost different things.  14SamA01's `64.65.` and 15SamA02's
 # `3. 10.` are the same class.
 #   p83  `191.200. Dukkassa vaḍḍhi etesanti…` — `extract.py`'s PARA rule wants
 #        `\.\s+` and finds none after `191.`, so the whole unit arrived INSIDE
 #        the paragraph carrying n=187.  `kat_splices`.
 #   p145 `54.55. Tatiye yesaṁ rāgādīnaṁ…`     — here the extraction DID break
 #        the paragraph but could not parse the number, so the paragraph is
 #        present, in the right place, with the number inside its own text and
 #        `n = None`.  Nothing is spliced and nothing is missing, so neither
 #        existing key fits: `kat_renum` says "this paragraph IS printed unit
 #        54", and refuses unless the paragraph really carries no number, its
 #        text really begins with the printed opening, and the printed stream
 #        really offers exactly one unit 54 on p145.
 # Both were found by the 1:1 count and by nothing else — 111 against 110 and
 # 113 against 112.  `site/19AnT02.json` is not edited either way.
 '19AnT02': {
   # !!! THE PAṆṆĀSAKA-RELATIVE VAGGA HEAD CARRIES ITS NIPĀTA-WIDE NUMBER IN
   # PARENTHESES — `(6) 1. Puggalavaggavaṇṇanā` — exactly as the canon
   # 15An01-17An03 and the commentary 18AnA02/19AnA03 do, and `kat_is_head`
   # wants the core to open with a CAPITAL.  Without `head_paren` every vagga
   # of every paṇṇāsaka after the first fell through to the body as a
   # paragraph opening: present, contiguous, and in the wrong role, which the
   # body gate reads 0/0/0/0.  THE NAV'S MĀTIKĀ GATE IS WHAT REPORTED IT.
   'head_paren': True,
   'kat_splices': [
     {'n': 191, 'pg': 83, 'ord': 110, 'into': 187,
      'mark': '200. Dukkassa vaḍḍhi etesanti dukkhavaḍḍhikā. Ye hi dukkhaṁ'},
   ],
   'kat_renum': [
     {'ord': 159, 'n': 54, 'pg': 145,
      'mark': '54.55. Tatiye yesaṁ rāgādīnaṁ appahānena purisassa'},
   ],
   'books': [('Dukanipāta-aṅguttaraṭīkā',     18,  91,   0, 113, None, 'katha'),
             ('Tikanipāta-aṅguttaraṭīkā',     92, 237, 113, 226, None, 'katha'),
             ('Catukkanipāta-aṅguttaraṭīkā', 238, 413, 226, 367, None, 'katha')],
   'colofix': {'Iti manorathapūraṇiyā aṅguttaranikāyaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|nipāta|nipāto|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|paṇṇāsaka'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # ==========================================================================
 # THE ABHIDHAMMA ṬĪKĀ — three volumes, and EACH CARRIES TWO WORKS: Ānanda's
 # MŪLAṬĪKĀ and Dhammapāla's ANUṬĪKĀ upon it.  Fourteen books in all.
 #
 # !!! THE FIRST WORK'S OWN WORD INDEX IS PRINTED BETWEEN THE TWO, hundreds of
 # pages before the end of the volume, so no page-level trim could see it —
 # 155 paragraphs / 56,971 characters across the three.  Cut by declared
 # ordinal run with `_tika/cut_index_run.py`, which keeps the next work's title
 # line (the run-on had glued it to the last index paragraph).  The book page
 # ranges below therefore SKIP those pages, and `kat_items` never reads them.
 #
 # THE CHECK THAT NO BOOK WAS MISSED IS THE EDITION'S OWN: the anuṭīkā
 # comments on the SAME numbered units as the mūlaṭīkā, so the two halves must
 # show the same `n` range book for book — 1577/1577, 1030/1030, and in
 # 24AbhiT03 456/456, 209/209, 917/917, 435/435, 49/49.  They do.
 # ==========================================================================

 # ==========================================================================
 # THE LAST THREE ṬĪKĀ — the Khuddaka's Netti pair and the two volumes of the
 # Visuddhimagga-mahāṭīkā (Paramatthamañjūsā).
 #
 # 21KhuT01 CARRIES TWO WORKS, and the first one's word index is printed
 # between them (pp160-166) exactly as the three Abhidhamma Ṭīkā do — cut by
 # declared ordinal run, so the book page ranges below skip those pages.
 #
 # 26VsmT02 CONTINUES 25VsmT01'S NUMBERING (n 365..892 against 1..363) — the
 # two volumes are ONE work in two bhāgas, which is why neither restarts.
 # ==========================================================================

 '21KhuT01': {
   'books': [('Nettiṭīkā',        8, 158,   0, 138, None, 'katha'),
             ('Nettivibhāvinī', 167, 522, 138, 287, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vibhāvinī|vatthu|vāra|vāro|uddāna|uddesa|niddesa|niddeso|kaṇḍa|'
             r'bhāṇavāra|nidāna|bhājanīya|nigamana|mātikā|hāra|naya|nayo|'
             r'pariccheda|paṭṭhāna|pakaraṇa'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '25VsmT01': {
   'books': [('Visuddhimaggamahāṭīkā', 9, 469, 0, 354, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vibhāvinī|vatthu|vāra|vāro|uddāna|uddesa|niddesa|niddeso|kaṇḍa|'
             r'bhāṇavāra|nidāna|bhājanīya|nigamana|mātikā|hāra|naya|nayo|'
             r'pariccheda|paṭṭhāna|pakaraṇa'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '26VsmT02': {
   'books': [('Visuddhimaggamahāṭīkā', 9, 543, 0, 521, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vibhāvinī|vatthu|vāra|vāro|uddāna|uddesa|niddesa|niddeso|kaṇḍa|'
             r'bhāṇavāra|nidāna|bhājanīya|nigamana|mātikā|hāra|naya|nayo|'
             r'pariccheda|paṭṭhāna|pakaraṇa'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '22AbhiT01': {
   'books': [('Dhammasaṅgaṇīmūlaṭīkā',  22, 224,   0, 261, None, 'katha'),
             ('Dhammasaṅgaṇī-anuṭīkā', 241, 460, 261, 477, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vibhaṅga|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|ṭīkā|mūlaṭīkā|anuṭīkā|vatthu|vāra|vāro|uddāna|'
             r'niddesa|kaṇḍa|bhāṇavāra|nidāna|bhājanīya|pucchaka|nigamana|'
             r'mātikā|yamaka|paṭṭhāna|paññatti|pakaraṇa|naya'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '23AbhiT02': {
   'books': [('Vibhaṅgamūlaṭīkā',  16, 250,   0, 277, None, 'katha'),
             ('Vibhaṅga-anuṭīkā', 266, 494, 277, 519, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vibhaṅga|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|ṭīkā|mūlaṭīkā|anuṭīkā|vatthu|vāra|vāro|uddāna|'
             r'niddesa|kaṇḍa|bhāṇavāra|nidāna|bhājanīya|pucchaka|nigamana|'
             r'mātikā|yamaka|paṭṭhāna|paññatti|pakaraṇa|naya'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '24AbhiT03': {
   # !!! A COLOPHON THE WHOLE-WORD RULE CANNOT REACH (2026-07-30i): a ONE-WORD
   # COMPOUND in which the ordinal is the FIRST MEMBER and so carries no ending
   # of its own — `Paṭhamavaggavaṇṇanā.`, not `Paṭhamo vaggo.`  Naming them is
   # deliberate: a general "one-word capitalised stopped line" rule was tried and
   # newly claimed TWENTY lines, which is exactly what `kat_is_colo`'s form (2)
   # guards behind a centring test.  Read off the page, one by one, from the
   # release sweep in `_tika/colo_final.log`.
   'colofix': {
               'Pahīnavāravaṇṇanā niṭṭhitā',
               'Pañcamavaggavaṇṇanā.',
   },

   # !!! THIS VOLUME NUMBERS ITS SECTION HEADINGS, and a NUMBERED display line
   # is decided by the numbered rule, not by the generic form test — the rule
   # this file has carried since 36Abhi08's unit 388.  Twenty-eight of them are
   # stored as numbered corpus paragraphs and correctly hidden as leaked
   # headings; on EIGHT the printed stream took them as UNITS as well, and the
   # 1:1 count refused to build.  Read on the page, every one is a centred
   # title with its own numbered unit directly beneath it:
   #     p240  `1. Kusalattika 1. Paṭiccavāravaṇṇanā`  then  `42-44. Tevīsati…`
   # `headfix` is the standing escape — "a line NAMED here is a heading
   # wherever it sits".  Six distinct literals; two of them are printed in both
   # the mūlaṭīkā and the anuṭīkā.
   'headfix': {'6. Aṭṭhamakassa indriya kathāvaṇṇanā',
               '1. Kusalattika 1. Paṭiccavāravaṇṇanā',
               '1. Paccayānuloma 1. Vibhaṅgavāra',
               '1. Paccayānuloma 1. Vibhaṅgavāravaṇṇanā',
               '1. Paccayānuloma 2. Saṅkhyāvāra',
               '11. Ekādasamanaya saṅgahitena sampayuttavippayuttapadavaṇṇanā'},
   # !!! AND ONE UNIT RANGE IS PRINTED WITH A PERIOD FOR ITS SEPARATOR.
   # p163 sets `10.17. Vāyanaṭṭhenāti…` where every one of its neighbours reads
   # `1-9.`, `18-21.`, `206-208.`.  The extractor cannot parse it, so corpus
   # ord357 carries `n = None` and the book paired 48 printed against 47.
   # 19AnT02's class, the second sighting; RECORDED as an erratum of the
   # edition, not corrected — `kat_renum` only lets the paragraph pair.
   'kat_renum': [{'ord': 357, 'n': 10, 'pg': 163,
                  'mark': '10.17. Vāyanaṭṭhenāti pasāraṇaṭṭhena, '
                          'pākaṭabhāvaṭṭhena vā.'}],
   'books': [('Dhātukathāpakaraṇamūlaṭīkā',       37,  62,    0,   39, None, 'katha'),
             ('Puggalapaññattipakaraṇamūlaṭīkā',  63,  81,   39,  111, None, 'katha'),
             ('Kathāvatthupakaraṇamūlaṭīkā',      83, 152,  111,  343, None, 'katha'),
             ('Yamakapakaraṇamūlaṭīkā',          153, 200,  343,  394, None, 'katha'),
             ('Paṭṭhānapakaraṇamūlaṭīkā',        201, 284,  394,  534, None, 'katha'),
             ('Dhātukathāpakaraṇa-anuṭīkā',      288, 320,  534,  572, None, 'katha'),
             ('Puggalapaññattipakaraṇa-anuṭīkā', 322, 342,  572,  630, None, 'katha'),
             ('Kathāvatthupakaraṇa-anuṭīkā',     344, 444,  630,  846, None, 'katha'),
             ('Yamakapakaraṇa-anuṭīkā',          446, 509,  846,  897, None, 'katha'),
             ('Paṭṭhānapakaraṇa-anuṭīkā',        510, 610,  897, 1022, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vibhaṅga|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|ṭīkā|mūlaṭīkā|anuṭīkā|vatthu|vāra|vāro|uddāna|'
             r'niddesa|kaṇḍa|bhāṇavāra|nidāna|bhājanīya|pucchaka|nigamana|'
             r'mātikā|yamaka|paṭṭhāna|paññatti|pakaraṇa|naya'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '20AnT03': {
   # !!! THE PAṆṆĀSAKA-RELATIVE VAGGA HEAD CARRIES ITS NIPĀTA-WIDE NUMBER IN
   # PARENTHESES — `(6) 1. Puggalavaggavaṇṇanā` — exactly as the canon
   # 15An01-17An03 and the commentary 18AnA02/19AnA03 do, and `kat_is_head`
   # wants the core to open with a CAPITAL.  Without `head_paren` every vagga
   # of every paṇṇāsaka after the first fell through to the body as a
   # paragraph opening: present, contiguous, and in the wrong role, which the
   # body gate reads 0/0/0/0.  THE NAV'S MĀTIKĀ GATE IS WHAT REPORTED IT.
   'head_paren': True,
   'books': [('Pañcakanipāta-aṅguttaraṭīkā',    20,  99,   0, 128, None, 'katha'),
             ('Chakkanipāta-aṅguttaraṭīkā',    100, 167, 128, 189, None, 'katha'),
             ('Sattakanipāta-aṅguttaraṭīkā',   168, 221, 189, 227, None, 'katha'),
             ('Aṭṭhakanipāta-aṅguttaraṭīkā',   222, 285, 227, 261, None, 'katha'),
             ('Navakanipāta-aṅguttaraṭīkā',    286, 323, 261, 290, None, 'katha'),
             ('Dasakanipāta-aṅguttaraṭīkā',    324, 375, 290, 338, None, 'katha'),
             ('Ekādasakanipāta-aṅguttaraṭīkā', 376, 390, 338, 345, None, 'katha')],
   'colofix': {'Iti manorathapūraṇiyā aṅguttaranikāyaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|nipāta|nipāto|vagga|vaggo|pāḷi|'
             r'aṭṭhakathā|ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla|paṇṇāsaka'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # ==========================================================================
 # THE SAṀYUTTA ṬĪKĀ — two volumes, Dhammapāla's Līnatthappakāsanā on the
 # Sāratthappakāsinī, and the second carries FOUR of the five vaggas.
 #
 #   16SaT01  Sagāthāvaggasaṁyuttaṭīkā       26-370
 #   17SaT02  Nidānavaggasaṁyuttaṭīkā        37-236
 #            Khandhavaggasaṁyuttaṭīkā      237-315
 #            Saḷāyatanavaggasaṁyuttaṭīkā   317-427
 #            Mahāvaggasaṁyuttaṭīkā         429-587
 #
 # !!! THE BOOK TITLE IS THE RUNNING HEADER'S FORM, NOT THE TITLE PAGE'S.  Each
 # title page sets a THREE-LINE stack — `Suttantapiṭaka / Nidānavagga /
 # Saṁyuttaṭīkā` — whose last line is the same on all four books, so taking it
 # would give this volume four books of one name.  The running header prints
 # `Nidānavaggasaṁyuttaṭīkā`, which is distinct, is the edition's own, and is
 # exactly the form 15SamA02 and 16SamA03 already use for the commentary.  The
 # title page's three lines are filtered from the body by `titlestack`, which
 # takes them from `booktitle/` — so this volume needs the second build pass.
 #
 # p316 and p428 are the BLANK versos before the third and fourth title pages,
 # which is why 17SaT02's trim converts -2 at its tail (`_seam/trimbounds.py`:
 # TRIM 37 585) and 16SaT01 -1 for a blank at p13 in its front matter.
 # --------------------------------------------------------------------------

 '16SaT01': {
   'books': [('Sagāthāvaggasaṁyuttaṭīkā', 26, 370, 0, 297, None, 'katha')],
   # The colophon frame — `Sāratthappakāsiniyā saṁyuttanikāyaṭṭhakathāya` /
   # `<X>vaṇṇanāya līnatthappakāsanā samattā.`, the stop on the second line.
   # Lowercase, where 14SamA01 capitalises the work name.
   # ...AND ONE OF THE ELEVEN FRAMES IS THREE LINES, not two: p253 sets
   #     Sāratthappakāsiniyā saṁyuttanikāyaṭṭhakathāya
   #     Bhikkhunīsaṁyuttavaṇṇanāya
   #     Līnatthappakāsanā samattā.
   # so the MIDDLE line has no stop either.  The other ten close up the last two
   # into one line.  Found by the nav's mātikā diff; named, not re-ruled.
   'colofix': {'Sāratthappakāsiniyā saṁyuttanikāyaṭṭhakathāya',
               'Bhikkhunīsaṁyuttavaṇṇanāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|saṁyutta|saṁyuttaṁ|vagga|vaggo|'
             r'pāḷi|aṭṭhakathā|ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '17SaT02': {
   'books': [('Nidānavaggasaṁyuttaṭīkā',      37, 236,   0, 202, None, 'katha'),
             ('Khandhavaggasaṁyuttaṭīkā',    237, 315, 202, 315, None, 'katha'),
             ('Saḷāyatanavaggasaṁyuttaṭīkā', 317, 427, 315, 466, None, 'katha'),
             ('Mahāvaggasaṁyuttaṭīkā',       429, 587, 466, 678, None, 'katha')],
   'colofix': {'Sāratthappakāsiniyā saṁyuttanikāyaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|saṁyutta|saṁyuttaṁ|vagga|vaggo|'
             r'pāḷi|aṭṭhakathā|ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|'
             r'bhāṇavāra|nidāna|peyyāla'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # ==========================================================================
 # THE MAJJHIMA ṬĪKĀ — three volumes, Dhammapāla's Līnatthappakāsanā on the
 # Papañcasūdanī, and the third carries TWO WORKS.
 #
 #   13MaT01  Mūlapaṇṇāsaṭīkā      (Paṭhamo bhāgo)      18-411
 #   14MaT02  Mūlapaṇṇāsaṭīkā      (Dutiyo bhāgo)        7-330
 #   15MaT03  Majjhimapaṇṇāsaṭīkā                       10-218
 #            Uparipaṇṇāsaṭīkā                         220-451
 #
 # 15MaT03's cover names both works (`Majjhimapaṇṇāsaṭīkā / Tathā– /
 # Uparipaṇṇāsaṭīkā`) and the seam is a printed title page with its own homage
 # at p220, with p219 the blank verso before it — the reason that volume needs
 # a −1 trim conversion above the seam.  13MaT01 needs one too, for a blank at
 # p13 in its front matter (`_seam/trimbounds.py`: TRIM 17 410).
 #
 # 13MaT01 AND 14MaT02 SHARE A BOOK TITLE, as the edition prints it; the BHĀGA
 # belongs in the nav SPEC (02VinA02's rule).
 # --------------------------------------------------------------------------

 '13MaT01': {
   'books': [('Mūlapaṇṇāsaṭīkā', 18, 411, 0, 169, None, 'katha')],
   # The colophon frame, once — `Papañcasūdaniyā majjhimanikāyaṭṭhakathāya` /
   # `<X>vaṇṇanāya līnatthappakāsanā samattā.`  The Ṭīkā set the work name
   # LOWERCASE where 10MaA01 capitalises it, so the literal is its own.
   'colofix': {'Papañcasūdaniyā majjhimanikāyaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|'
             r'ārambha|bhāga|paṇṇāsa'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '14MaT02': {
   'books': [('Mūlapaṇṇāsaṭīkā', 7, 330, 0, 317, None, 'katha')],
   'colofix': {'Papañcasūdaniyā majjhimanikāyaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|'
             r'ārambha|bhāga|paṇṇāsa'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 15MaT03: TWO WORKS IN ONE VOLUME -------------------------------------
 # ord334 (printed p218) closes `Saṅgāravasuttavaṇṇanāya līnatthappakāsanā
 # samattā.`; p219 is BLANK; ord335 (p220) is the Uparipaṇṇāsa's own homage
 # title page and ord336 opens its unit 1.  Counted, not computed.
 '15MaT03': {
   'books': [('Majjhimapaṇṇāsaṭīkā',  10, 218,   0, 335, None, 'katha'),
             ('Uparipaṇṇāsaṭīkā',    220, 451, 335, 644, None, 'katha')],
   # !!! THE EDITION SETS ONE UNIT NUMBER ALONE ON ITS OWN LINE, FLUSH RIGHT.
   # Printed p13 prints
   #
   #     4                           Majjhimanikāya
   #                                                                        3.
   #     Kārakabhāvanti paṭipattiyaṁ paṭipajjanakabhāvaṁ. Mayampi nāma gihī
   #
   # — the `3.` at indent 79, its unit's first words on the NEXT line at
   # indent 0.  The numbered rule wants `N.` and its text on ONE line, so the
   # extraction saw no unit there at all and the whole of unit 3 arrived inside
   # the paragraph carrying n=2 (ord3).  The PRINTED side does see it, which is
   # how the 1:1 count found it: 333 printed against 332 corpus.
   # 36Abhi08's class — `41.Nevavipāka…` with no space — reached the same way
   # from the other side, and the same key answers it.  THE DECLARATION VERIFIES
   # ITSELF: `kat_splices` refuses unless the host really carries n=2, really
   # contains the marker, and the printed stream really offers exactly one unit
   # numbered 3 on p13.  Nothing in `site/15MaT03.json` is edited.
   'kat_splices': [
     {'n': 3, 'pg': 13, 'ord': 3, 'into': 2,
      # THE MARK IS THE WHOLE PRINTED FIRST LINE, because it is what the
      # reader draws: `add_prose` emits the marker and nothing else.  Given
      # only the first sentence, the render skipped `Mayampi nāma gihī` and
      # the gate's REVERSE direction reported ord3's `after` diverging at
      # word 3 of 105 — which is how the short marker was caught.
      'mark': 'Kārakabhāvanti paṭipattiyaṁ paṭipajjanakabhāvaṁ. Mayampi nāma gihī'},
   ],
   'colofix': {'Papañcasūdaniyā majjhimanikāyaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|'
             r'ārambha|bhāga|paṇṇāsa'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # ==========================================================================
 # THE DĪGHA ṬĪKĀ — five volumes, THREE WORKS, and every one of them ONE BOOK.
 # Extents hand-measured at both ends off the printed page (`_tika/pagescan.py`,
 # `_seam/ends2.py`); book heads by the case-insensitive homage scan over the
 # REBUILT corpora (`_tika/bookheads.py`), which returns exactly one
 # homage-OPENING paragraph in each — 09DiT02's second hit is the homage quoted
 # inside a gāthā at printed p135, not a title page.
 #
 #   08DiT01  Sīlakkhandhavaggaṭīkā            Dhammapāla        19-423
 #   09DiT02  Sīlakkhandhavagga-abhinavaṭīkā   Ñāṇābhivaṁsa        6-505  (I)
 #   10DiT03  Sīlakkhandhavagga-abhinavaṭīkā   Ñāṇābhivaṁsa        9-445  (II)
 #   11DiT04  Mahāvaggaṭīkā                    Dhammapāla         11-368
 #   12DiT05  Pāthikavaggaṭīkā                 Dhammapāla         10-301
 #
 # NO PAGE CONVERSION WAS NEEDED ON ANY OF THE FIVE: every blank verso falls
 # AFTER the body (`_seam/trimbounds.py` reports 0/0 on all five), so the
 # corpus's `pdf_page` and the true index agree throughout the body.  These are
 # true 1-based PDF pages either way, like every other SPEC in this file.
 #
 # 09DiT02 AND 10DiT03 SHARE A BOOK TITLE — the Sādhuvilāsinī's two bhāgas both
 # head their title page `Sīlakkhandhavagga-abhinavaṭīkā`.  That is what the
 # page prints and it stays; the BHĀGA belongs in the nav SPEC, which is
 # 02VinA02's rule.
 # --------------------------------------------------------------------------

 '08DiT01': {
   'books': [('Sīlakkhandhavaggaṭīkā', 19, 423, 0, 315, None, 'katha')],
   # THE COLOPHON FRAME, ONCE — printed p303 sets
   #     Sumaṅgalavilāsiniyā Sāmaññaphalasuttavaṇṇanāya
   #     Līnatthappakāsanā.
   # and only the second line carries the stop, so the first read as a heading
   # and became a `sections/` entry at ord143.  07DiA01's shape; the same key.
   'colofix': {'Sumaṅgalavilāsiniyā Sāmaññaphalasuttavaṇṇanāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|saṅgīti'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '09DiT02': {
   'books': [('Sīlakkhandhavagga-abhinavaṭīkā', 6, 505, 0, 94, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|saṅgīti'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '10DiT03': {
   'books': [('Sīlakkhandhavagga-abhinavaṭīkā', 9, 445, 0, 249, None, 'katha')],
   # The same frame, in 07DiA01's LOCATIVE form (`-yaṁ`), once — ord66.
   # AND A COLOPHON WHOSE STOP THE EDITION DROPS: printed p409 sets
   # `Poṭṭhapādasuttavaṇṇanā niṭṭhitā` at indent 22 with no full stop, so the
   # form test read it as a heading — 31KhuA12's class (2026-07-29f).  Named,
   # and the missing stop is PRESERVED.
   'colofix': {'Iti Sumaṅgalavilāsiniyā Dīghanikāyaṭṭhakathāyaṁ',
               'Poṭṭhapādasuttavaṇṇanā niṭṭhitā'},
   # TWO PROSE LINES READ AS HEADINGS, both on printed p264, and both for the
   # one reason `kat_is_head` cannot rule out: each introduces a quoted gāthā
   # and therefore closes with the CITATION DASH instead of a stop.  The class
   # 07DiA01 and 12MaA03 named; each becomes ordinary body text again and
   # nothing is suppressed.
   'headskip': ('Tassa ca puttapaputtaparamparaṁ sandhāya evaṁ vadanti–',
                'Idaṁ Aṭṭhakathānuparodhavacanaṁ. Yaṁ pana dīpavaṁse vuttaṁ–'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|saṅgīti'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '11DiT04': {
   'books': [('Mahāvaggaṭīkā', 11, 368, 0, 339, None, 'katha')],
   # !!! TWELVE PRINTED HEADINGS OPEN WITH A PARENTHESISED NUMBER, AND NOT ONE
   # OF THEM REACHED `sections/`.  The Pāyāsirājañña's similes are set
   # `(1) Candimasūriya-upamāvaṇṇanā` … `(14) Sāṇabhārika-upamāvaṇṇanā`
   # (printed pp361-365).  `kat_is_head` wants a heading to open with a CAPITAL
   # and the numbered rule wants `N.`, so a `(N)` line satisfies neither: the
   # volume's own mātikā (pp9-10) lists all twelve and the tree could reach
   # none — 18AnA02 ord463's class, and the same escape.  Found by the nav's
   # mātikā gate; every literal is taken from the printed page, INCLUDING
   # `(11) Dve satthavāha-upamāvaṇṇanā`, which the body spaces and the mātikā
   # closes up.  The edition also SKIPS (4), (5) and (12) in its own numbering,
   # in both the mātikā and the body — recorded, not corrected.
   'headfix': ('(1) Candimasūriya-upamāvaṇṇanā',
               '(2) Cora-upamāvaṇṇanā',
               '(3) Gūthakūpapurisa-upamāvaṇṇanā',
               '(6) Gabbhinī-upamāvaṇṇanā',
               '(7) Supinaka-upamāvaṇṇanā',
               '(8) Santatta-ayoguḷa-upamāvaṇṇanā',
               '(9) Saṅkhadhama-upamāvaṇṇanā',
               '(10) Aggikajaṭila-upamāvaṇṇanā',
               '(11) Dve satthavāha-upamāvaṇṇanā',
               '(13) Akkhadhuttaka-upamāvaṇṇanā',
               '(14) Sāṇabhārika-upamāvaṇṇanā'),
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|saṅgīti'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 '12DiT05': {
   'books': [('Pāthikavaggaṭīkā', 10, 301, 0, 301, None, 'katha')],
   # !!! THE COLOPHON FRAME ELEVEN TIMES, AND THIS VOLUME SETS THE WORK NAME
   # LOWERCASE.  Every sutta closes over two lines —
   #     Sumaṅgalavilāsiniyā dīghanikāyaṭṭhakathāya
   #     <X>suttavaṇṇanāya līnatthappakāsanā.
   # — with the stop on the second, so all eleven first lines were `sections/`
   # entries: present, contiguous, in the WRONG ROLE, which no content gate can
   # see.  Found by the nav's mātikā diff, which lists them as body headings the
   # mātikā does not carry — the same way 07DiA01's eight were found.
   'colofix': {'Sumaṅgalavilāsiniyā dīghanikāyaṭṭhakathāya'},
   'stems': (r'vaṇṇanā|kathā|sutta|suttaṁ|vagga|vaggo|pāḷi|aṭṭhakathā|ṭīkā|'
             r'vatthu|vāra|vāro|uddāna|niddesa|kaṇḍa|bhāṇavāra|nidāna|saṅgīti'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 01ViT01: Sāratthadīpanī I — TWO BOOKS, 01VinA01's own shape ----------
 # ord11 (printed p209) is the Bāhiranidāna's closing colophon; ord12 (p210)
 # opens `Verañjakaṇḍavaṇṇanā` at unit 1.  The heads book carries NO numbered
 # paragraph at all — 194 printed pages, 12 corpus paragraphs.
 '01ViT01': {
   'books': [('Ganthārambhakathā + Bāhiranidānavaṇṇanā', 16, 209,  0,  12, None, 'heads'),
             ('Verañjakaṇḍavaṇṇanā',                    210, 475, 12,  45, None, 'katha')],
   'colofix': {'Iti samantapāsādikāya vinayaṭṭhakathāya sāratthadīpaniyaṁ'},
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|'
             r'saṁghādisesa|nidāna|saṅgīti|khandhaka|parivāra|nayo'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 02ViT02: Sāratthadīpanī II — ONE book, a continuation volume ---------
 # Opens mid-work at `1. Pārājikakaṇḍa` (unit 24) and closes
 # `Nissaggiyavaṇṇanā niṭṭhitā.`  The bhāga belongs in the nav SPEC, not here
 # (02VinA02's rule), so the book takes the cover's own title.
 # !!! ITS UNIT STREAM STEPS BACK TWICE AND CARRIES 32 FALSE ANCHORS.
 # 159 -> 136 at printed p189 is recorded UNRESOLVED (2026-07-29p); 232 -> 223
 # at p306; and pp314-320 set the sixteen dreams of King Kosala as `1.`-`16.`
 # and their sixteen interpretations as a second `1.`-`16.` at the body indent.
 # NONE of that reaches the pairing: `kat_build` pairs printed units to corpus
 # paragraphs BY POSITION and keeps `n` only as a cross-check, so the printed
 # reading stands untouched and uncorrected.
 '02ViT02': {
   'books': [('Sāratthadīpanīṭīkā', 10, 457, 0, 344, None, 'katha')],
   'colofix': {
               'Catuppadakathāvaṇṇanā niṭṭhitā',
               'Pañcavīsati-avahārakathāvaṇṇanā niṭṭhitā','Iti samantapāsādikāya vinayaṭṭhakathāya sāratthadīpaniyaṁ'},
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|'
             r'saṁghādisesa|nidāna|saṅgīti|khandhaka|parivāra|nayo'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 03ViT03: Sāratthadīpanī III — FIVE books ------------------------------
 # Homage title pages at printed pp22 / 132 / 152 / 386 / 476, each confirmed
 # against the title line above its rule.  The Bhikkhunīvibhaṅga does NOT reset
 # the unit stream (647 -> 656, straight on), exactly as 03VinA03's middle
 # boundary does not; the three khandhaka books do.
 '03ViT03': {
   'books': [('Pācittiyakaṇḍa',            22, 131,   0, 179, None, 'katha'),
             ('Bhikkhunīvibhaṅgavaṇṇanā', 132, 151, 179, 240, None, 'katha'),
             ('Mahāvagga',                152, 385, 240, 454, None, 'katha'),
             ('Cūḷavagga',                386, 475, 454, 593, None, 'katha'),
             ('Parivāra',                 476, 517, 593, 671, None, 'katha')],
   'colofix': {
               'Katipucchāvāravaṇṇanā niṭṭhitā','Iti samantapāsādikāya vinayaṭṭhakathāya sāratthadīpaniyaṁ'},
   # THREE PARAGRAPHS THE LEAK TEST FLAGS AND THE PRINTED STREAM DOES NOT.
   # `_tika/unitdiff.py` walks the printed numbered stream against the corpus
   # `n` stream 1:1: books 0, 2 and 4 agree NUMBER FOR NUMBER, 173/173,
   # 210/210, 74/74, with no divergence anywhere.  So hiding any of these three
   # takes an ordinal the printed side still emits a unit for, and every unit
   # after it pairs with the wrong paragraph.
   # !!! ord145 WAS THE THIRD, AND IT IS NOW CORRECTED (2026-07-30f).  The
   #     note here read: `10. Chandaṁ adatvā gamanasikkhāpadavaṇṇanā`
   #     (printed p116) IS a heading, but a NUMBERED one, and `kat_items`'
   #     numbered rule takes precedence over the generic form test, so the
   #     PRINTED side reads it as unit 10 too — both sides consistent, the role
   #     wrong on both, RECORDED not corrected.  That was right about the
   #     diagnosis and wrong about the remedy: the reason hiding it was refused
   #     is that the printed side still emitted a unit for it, and `headfix`
   #     (below) moves the PRINTED side, so the two now move TOGETHER —
   #     172 printed against 172 corpus.  The mātikā gate is what forced the
   #     question: this entry was the volume's one unreachable mātikā row.
   #   ord433 `367-369. Bhikkhussa kālakateti …` is an ordinary numbered unit.
   #   ord607 `298. Vivādādhikaraṇassa … Samathā samathassa
   #     sādhāraṇavārakathāvaṇṇanā` is a unit with the NEXT heading glued onto
   #     its tail by the extraction — 18AnA02 ord463's shape exactly.
   'leak_keep': (433, 607),
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|'
             r'saṁghādisesa|nidāna|saṅgīti|khandhaka|parivāra|nayo'),
      # !!! A CENTRED HEADING WHOSE CORE RUNS TO THREE WORDS, AND `head_words`
   # DEFAULTS TO TWO — SO IT WAS LOST (2026-07-30f).  p95 sets
   #
   #     10. Chandaṁ adatvā gamanasikkhāpadavaṇṇanā
   #
   # between `9. Kammapaṭibāhana-` and `11. Dubbala-`, both of which reached
   # `sections/`; this one did not, and its own closing colophon
   # (`Chandaṁ adatvā gamanasikkhāpadavaṇṇanā niṭṭhitā.`) is printed two lines
   # below it.  No content gate can see this — the text is on the page either
   # way; the MĀTIKĀ GATE reported it as the volume's one absent entry.
   #
   # MEASURED BEFORE IT WAS WIDENED (`_tika/vt_headwords.py`): this volume
   # prints exactly ONE centred, numbered, capitalised, stem-ending line whose
   # core exceeds `head_words`, and it is this one.  The other six Vinaya Ṭīkā
   # print none.  So 3 admits the printed heading and nothing else — asserted
   # by diffing the side-maps, not assumed.
   # !!! A CENTRED HEADING WHOSE CORE RUNS TO THREE WORDS, AND `head_words`
   # DEFAULTS TO TWO — SO IT WAS LOST (2026-07-30f).  p95 sets
   #
   #     10. Chandaṁ adatvā gamanasikkhāpadavaṇṇanā
   #
   # between `9. Kammapaṭibāhana-` and `11. Dubbala-`, both of which reached
   # `sections/`; this one did not, and its own closing colophon
   # (`Chandaṁ adatvā gamanasikkhāpadavaṇṇanā niṭṭhitā.`) is printed four lines
   # below it.  No content gate can see this — the text is on the page either
   # way; the MĀTIKĀ GATE reported it as this volume's ONE absent entry.
   #
   # `head_words: 3` WAS TRIED AND BREAKS THE VOLUME: book 1 went from
   # `printed units 173 / corpus ¶ 173  headings 103  [OK]` to
   # `172 / 173 … headings 0  FATAL`, because a printed numbered UNIT with a
   # three-word opening is then taken for a heading and the pairing parts
   # company.  That is 45KhuA26's lesson exactly — `head_words: 3` fixes four
   # of five and breaks the fifth — so this is `headfix`, which names the line
   # and widens nothing.
   #
   # MEASURED FIRST (`_tika/vt_headwords.py`): this volume prints exactly ONE
   # centred, numbered, capitalised, stem-ending line whose core exceeds
   # `head_words`, and it is this one; the other six Vinaya Ṭīkā print none.
   'headfix': ('10. Chandaṁ adatvā gamanasikkhāpadavaṇṇanā',),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 04ViT04: Vimativinodanī I — TWO BOOKS, the same seam -----------------
 # ord9 (printed p47) closes the Bāhiranidāna; ord10 (p48) opens
 # `Verañjakaṇḍavaṇṇanā` — and that book's FIRST NUMBERED ANCHOR is 28 pages
 # later, at p76, opening at `2.`  The shipped corpus began at exactly that
 # anchor, which is all `extract.py` could see (2026-07-29p).
 '04ViT04': {
   'books': [('Ganthārambhakathā + Bāhiranidānakathāvaṇṇanā', 10,  47,  0,  10, None, 'heads'),
             ('Verañjakaṇḍavaṇṇanā',                          48, 371, 10, 302, None, 'katha')],
   'colofix': {'Iti samantapāsādikāya vinayaṭṭhakathāya vimativinodaniyaṁ'},
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|'
             r'saṁghādisesa|nidāna|saṅgīti|khandhaka|parivāra|nayo'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 05ViT05: Vimativinodanī II — FIVE books, and the cleanest of the seven
 # Homage title pages at printed pp19 / 85 / 101 / 229 / 289.  Its unit stream
 # has no duplicate and no descent inside any book.
 '05ViT05': {
   'books': [('Pācittiyakaṇḍa',            19,  84,   0, 179, None, 'katha'),
             ('Bhikkhunīvibhaṅgavaṇṇanā',  85, 100, 179, 233, None, 'katha'),
             ('Mahāvaggavaṇṇanā',         101, 228, 233, 450, None, 'katha'),
             ('Cūḷavaggavaṇṇanā',         229, 288, 450, 592, None, 'katha'),
             ('Parivāravaṇṇanā',          289, 340, 592, 693, None, 'katha')],
   'colofix': {'Iti samantapāsādikāya vinayaṭṭhakathāya vimativinodaniyaṁ'},
   # !!! THREE SECTION HEADINGS THE EDITION PRINTS WITH A TERMINAL FULL STOP
   # (2026-07-30f).  `kat_is_head` refuses a stopped line — a heading is not a
   # sentence, and that rule is exactly what keeps colophons out of the heading
   # role — but this volume stops three of its own openings:
   #
   #     Saṁghabhedakakathāvaṇṇanā.          (p254, closed p255 `… niṭṭhitā.`)
   #     Anuvijjakassa paṭipattivaṇṇanā.     (p299, closed p301)
   #     Kathinādijānitabbavibhāgavaṇṇanā.   (p304, closed p305)
   #
   # Each opens a section whose first numbered unit follows on the next line
   # and which is closed, pages later, by `… niṭṭhitā.` under the same name —
   # so the role is not in doubt, and each is listed in the volume's own
   # mātikā.  All three reached NO `sections/` entry; the MĀTIKĀ GATE is what
   # reported them, as this volume's three absent rows.  NAMED rather than
   # ruled: widening `kat_is_head` to admit stopped lines would hand it every
   # colophon in the corpus.
   #
   # SWEPT (`_tika/vt_stopped_head.py`): eight stopped centred heading-shaped
   # lines across the seven Vinaya Ṭīkā.  These three are openings; the other
   # five (02ViT02 x1, 04ViT04 x1, 06ViT06 x3, all of the form
   # `X-vaṇṇanānayo.`) read as CLOSINGS and none of them is listed in its
   # volume's mātikā, so they are recorded as `colopat`/`colofix` candidates
   # and NOT declared here.
   'headfix': ('Saṁghabhedakakathāvaṇṇanā.',
               'Anuvijjakassa paṭipattivaṇṇanā.',
               'Kathinādijānitabbavibhāgavaṇṇanā.'),
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|'
             r'saṁghādisesa|nidāna|saṅgīti|khandhaka|parivāra|nayo'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 06ViT06: Vajirabuddhiṭīkā — one WORK in one volume, SIX books --------
 # Homage title pages at printed pp28 / 378 / 418 / 534 / 570, and **p570
 # prints `sammāsambuddhassa` with a LOWERCASE s** — a scan keyed on the
 # capital returns four heads for five (2026-07-29p).  The seam is p56/p57 and
 # the first numbered anchor is 14 pages later, at p71.
 # !!! ITS SUTTAVIBHAṄGA BOOK RESETS AT THE KAṆḌA, WITH NO TITLE PAGE:
 # `4. Nissaggiyakaṇḍa` at p241 (453 -> 1) and `5. Pācittiyakaṇḍa` at p313
 # (657 -> 1).  These are NOT book heads — no homage, no title page — so they
 # stay inside the Verañjakaṇḍa book, where `kat_build`'s positional pairing
 # is indifferent to them.  RECORDED, not corrected.
 '06ViT06': {
   # !!! A COLOPHON THE EDITION PRINTS WITHOUT ITS FULL STOP (2026-07-30i).
   # `kat_is_colo` requires the terminal stop — that rule is what keeps ordinary
   # sentences out of the colophon role — so these fell through and were typed as
   # HEADINGS in `sections/`, opening a section the edition is closing.
   # THE EDITION IS INCONSISTENT WITH ITSELF, AND SAYS SO ON ITS OWN PAGES:
   # 24AbhiT03 prints `Pahīnavāravaṇṇanā niṭṭhitā` at one indent and
   # `Pahīnavāravaṇṇanā niṭṭhitā.` at another — the same colophon, both ways.  So
   # the missing stop is the edition's, not our extraction's, and these are NAMED
   # rather than the stop rule being relaxed for every volume.  05Vin05 carries the
   # same declaration for the same reason.
   'colofix': {
               'Dvebhāgasikkhāpadavaṇṇanā niṭṭhitā',
   },

   'books': [('Ganthārambhakathā + Bāhiranidānavaṇṇanā', 28,  56,   0,   8, None, 'heads'),
             ('Verañjakaṇḍavaṇṇanā',                     57, 377,   8, 387, None, 'katha'),
             ('Bhikkhunīvibhaṅgavaṇṇanā',               378, 417, 387, 487, None, 'katha'),
             ('Mahāvaggavaṇṇanā',                       418, 533, 487, 660, None, 'katha'),
             ('Cūḷavaggavaṇṇanā',                       534, 569, 660, 765, None, 'katha'),
             ('Parivāravaṇṇanā',                        570, 612, 765, 860, None, 'katha')],
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|bhāga|pārājika|'
             r'saṁghādisesa|nidāna|saṅgīti|khandhaka|parivāra|nayo'),
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- 07ViT07: the Kaṅkhāvitaraṇī ṭīkās — TWO WORKS, FOUR BOOKS -----------
 # !!! FOUR, NOT TWO.  2026-07-29n/p recorded this volume as `heads p22-139 |
 # heads p140-510`.  The homage scan over the REBUILT corpus finds four title
 # pages — pp22 / 130 / 140 / 472 — and each is confirmed by its printed title
 # line: each work commentates the Bhikkhu- and then the Bhikkhunīpātimokkha,
 # which is exactly 05Kankha's four-book shape.  The two-book reading was
 # measured on a corpus of 22 paragraphs and is superseded.
 # Both works are heading-delimited prose: 420 paragraphs carry 22 numbers
 # between them, so `katha` has nothing to pair against and `heads` is the
 # reader.  p139 and p471 are BLANK versos before a title page.
 '07ViT07': {
   # THE COLOPHON FRAME IS TWO PRINTED LINES AND ONLY THE SECOND CARRIES A
   # STOP — 05Kankha's shape exactly, and the same key answers it.  Under
   # `heads_by_form` the generic colophon test needs an INDENT, and
   # `head_build`'s untouched-paragraph sweep calls `kat_is_colo(raw)` with
   # none, so every one of these had to be NAMED.  Both readings of the work
   # name are printed and both stand: `kaṅkhāvitaraṇiyā` here is LOWERCASE
   # where 05Kankha sets `Kaṅkhāvitaraṇiyā`.
   # The six SECOND lines that the sweep still could not reach: each names a
   # section and says it is finished, so form (1) of `kat_is_colo` would take
   # them on sight — but that form is guarded behind `heads_by_form`'s indent
   # test, which `head_build` cannot supply.  Named, not re-ruled.
   'colofix': {'Iti kaṅkhāvitaraṇiyā pātimokkhavaṇṇanāya',
               'Vinayatthamañjūsāyaṁ līnatthappakāsaniyaṁ',
               'Tiṁsabhojanappaṭisaṁyuttasikkhāpadavaṇṇanā niṭṭhitā.',
               'Bhikkhunipātimokkhe pārājikavaṇṇanā niṭṭhitā.',
               'Bhikkhunipātimokkhe saṁghādisesavaṇṇanā niṭṭhitā.',
               'Bhikkhunipātimokkhe nissaggiyavaṇṇanā niṭṭhitā.',
               'Bhikkhunipātimokkhe pācittiyavaṇṇanā niṭṭhitā.',
               'Bhikkhunipātimokkhe pāṭidesanīyavaṇṇanā niṭṭhitā.'},
   'books': [('Kaṅkhāvitaraṇīpurāṇaṭīkā',    22, 129,   0, 100, None, 'heads'),
             ('Bhikkhunīpātimokkhavaṇṇanā', 130, 138, 100, 115, None, 'heads'),
             ('Kaṅkhāvitaraṇī-abhinavaṭīkā',140, 471, 115, 302, None, 'heads'),
             ('Bhikkhunīpātimokkhavaṇṇanā', 472, 510, 302, 420, None, 'heads')],
   'stems': (r'vaṇṇanā|kathā|kaṇḍa|vagga|vaggo|sikkhāpada|pāḷi|aṭṭhakathā|'
             r'ṭīkā|vatthu|vāra|vāro|uddāna|niddesa|pātimokkha|nidāna|'
             r'pārājika|saṁghādisesa|sekhiya|adhikaraṇasamatha|nayo'),
   # !!! TWO NUMBERED HEADINGS ON ONE LINE, SEPARATED BY A SINGLE SPACE —
   # AND BOTH WERE LOST (2026-07-30f).  p64 (0-based pdf 84) opens the
   # Nissaggiya with
   #
   #     1. Cīvaravagga 1. Kathinasikkhāpadavaṇṇanā
   #
   # the vagga run together with its first sikkhāpada.  `head_split`'s generic
   # rule needs `\s{3,}` between the two numbers, so this line matched neither
   # the split rule nor `kat_is_head`, and the WHOLE LINE was dropped: neither
   # heading reached `sections/`, and `Cīvaravagga` occurs 0 times in the
   # volume's corpus text.  **No content gate can see this** — the body text is
   # complete and contiguous either way; the MĀTIKĀ GATE is what reported it,
   # as two absent entries, which is the 11DiT04 lesson again.
   #
   # The same pair IS captured at ord146, where the abhinavaṭīkā sets the two
   # on separate lines — so this is one printed line, not a rule that is wrong.
   # Swept over every volume under `site/` for centred lines carrying a second
   # number with no three-space run (`_tika/vt_narrowgap.py`): **116 volumes
   # clean, 18Khu01 checked separately and clean, this is the only one.**
   # Declared rather than widened, for the reason `split_unnumbered` gives:
   # the three-space form is what every shipped volume was measured against.
   'split_literals': {
     '1. Cīvaravagga 1. Kathinasikkhāpadavaṇṇanā':
         ['1. Cīvaravagga', '1. Kathinasikkhāpadavaṇṇanā']},
   'n_scope': 'book',
   'heads_by_form': True,
   'pada_runon': True,
 },

 # --- VINAYA 4: Cūḷavaggapāḷi — twelve khandhakas, one book -----------------
 # Declared "[11 pages of content, 508 pages of text, 35 pages of index]" ->
 # text 1-based 12-519, which the measured extent reproduces exactly.
 # Body gate 0-based `11 518`.
 '04Vin04': {
   'books': [('Cūḷavaggapāḷi', 12, 519, 0, 458, None, 'katha')],
   'stems': (r'kaṇḍa|kkhandhaka|vagga|vaggo|sikkhāpada|sikkhāpadaṁ|pāḷi|'
             r'vibhaṅga|uddāna|uddānaṁ|nidāna|kathā|vatthu|vatthūni|'
             r'anujānanā|kamma|kammaṁ|acchariya'),
   'n_scope': 'book',
   'heads_by_form': True,
   'head_words': 4,
   'pada_runon': True,
   'wrap_display': True,
   # this volume is the first with uddāna pages at BOTH columns (8 at the body
   # column, 17 at a display indent), so it is the first whose uddāna cross
   # between them at a page break — see the override in `kat_items`
   'udd_run': True,
 },
 # --- VINAYA 5: Parivārapāḷi — the last volume of the Vinayapiṭaka ----------
 # Declared "[14 pages of content, 390 pages of text, 36 pages of index]" ->
 # text 1-based 15-404, which the measured extent reproduces exactly.
 # Body gate 0-based `14 403`.
 '05Vin05': {
   # A COLOPHON THE EDITION PRINTS WITHOUT A FULL STOP.  `kat_is_colo`
   # requires the stop, so this line fell through and was read as a
   # HEADING — present, contiguous, and in the wrong role, which every
   # content gate reports as 0.  Found 2026-07-26ai by scanning every
   # volume's heads stream for `niṭṭhit|samatt`: a heading that says a
   # section has ENDED is a colophon.  Three across the corpus.
   'colofix': {'Ekuttarikaṁ niṭṭhitaṁ'},
   'books': [('Parivārapāḷi', 15, 404, 0, 519, None, 'katha')],
   # !!! `kamma|kammaṁ` IS NOT A HEADING STEM IN THIS VOLUME, though it is in
   # 04Vin04.  The Parivāra opens units with four-word phrases that END at it —
   # printed p394 "482. Cattāri kammāni apalokanakammaṁ ñattikammaṁ" and p396
   # "489. …" — so with it in the list the numbered form test claimed them as
   # HEADINGS and both units vanished from the printed stream.
   # MEASURED before removing it: of the numbered lines of four words or fewer,
   # 214 are CENTRED at body+14 and are genuine headings, and exactly THREE are
   # claimed by the stem test alone from low on the page — p177's
   # "12. Corivuṭṭhāpanasamuṭṭhāna", which is a real heading pushed down by its
   # own length and is rescued by `samuṭṭhāna`, and those two units.  And NO
   # centred heading in this volume ends at kamma/kammaṁ, so removing it costs
   # nothing on the heading side.
   # THE STEM LIST IS A MEASUREMENT PER VOLUME, exactly as `head_words` is.
   'stems': (r'kaṇḍa|kkhandhaka|vagga|vaggo|sikkhāpada|sikkhāpadaṁ|pāḷi|'
             r'vibhaṅga|uddāna|uddānaṁ|nidāna|kathā|vatthu|vatthūni|'
             r'anujānanā|vāra|vāro|pucchā|samatha|samuṭṭhāna'),
   'n_scope': 'book',
   'heads_by_form': True,
   'head_words': 4,
   'pada_runon': True,
   'wrap_display': True,
   'udd_run': True,
   # the three centred pair-lines `split_centre` cannot read, censused over
   # all five Vinaya volumes (2026-07-26ae)
   # A FOOTNOTE CELL SPLICED ONTO THE FOLLOWING PARAGRAPH.  The extraction
   # joined printed p122's only footnote — "1. Rathiyāya vā (Ka)" — onto the
   # body paragraph that opens p123, and gave the result the FOOTNOTE's own
   # number as its `n`, so the corpus carries a numbered paragraph the printed
   # stream cannot: `page_lines` stops at the rule, correctly.
   # Hiding it loses nothing — the kathā path draws the body from the PRINTED
   # stream, and "Attānaṁ vā paraṁ vā nirayena vā…" is there on p123, checked.
   # !!! THOSE FIVE ARE NOW HIDDEN TOO, and the note above them was right only
   # while the PRINTED side was also wrong.  Until 2026-07-26ak `page_lines`
   # admitted this volume's ten graphic-rule footnote blocks into the printed
   # stream, so each of these corpus paragraphs PAIRED with the printed cell it
   # had been spliced onto — two defects holding each other up, and the 1:1
   # count check saw 505/505.  With `fnblock` cutting the page correctly the
   # printed cells are gone and exactly FIVE printed units go with them
   # (p54 x2, p119, p140, p382 — counted, not assumed), so the same five corpus
   # paragraphs must be hidden or the count breaks 500/505.
   # THE TEXT IS NOT LOST: ord147, 225, 238 and 495 carry real body text after
   # the cell, and the kathā path draws the body from the PRINTED stream, where
   # it stands on the following page.  That is not asserted — the body gate at
   # minw 1 is what proves it, and it is why this may not be done by eye.
   # ord133 is the same shape and was ALREADY hidden as a leaked heading.
   # !!! ord208 IS NOT.  2026-07-26aj recorded it as a seventh instance; it is
   # a clean body paragraph (n=202, p110), and p110's cell is the xref
   # `* Aṁ 3. 311 piṭṭhepi`, which never took an ordinal.  That finding is
   # withdrawn.
   # Seven pādas of the Palibodhapañhābyākaraṇa (p324-325) whose
   # parenthesised ANSWER NUMBER leaves them with no terminal stop, so
   # the form test drew each as a centred heading inside a gāthā.
   'headskip': (
       'Cīvare niṭṭhite cīvarapalibodho chijjati. (2)',
       'Dve palibodhā apubbaṁ acarimaṁ chijjanti. (3)',
       'Cīvare naṭṭhe cīvarapalibodho chijjati. (4)',
       'Tassa saha savanena āvāsapalibodho chijjati. (5)',
       'Cīvarāsāya upacchinnāya cīvarapalibodho chijjati. (6)',
       'Tassa bahisīme1 āvāsapalibodho chijjati. (7)',
       'Dve palibodhā apubbaṁ acarimaṁ chijjantīti. (8)',
   ),
   'backmatter': [146, 147, 225, 227, 238, 495],
   # THE PIṬAKA'S THIRD EMBEDDED UNIT NUMBER — printed p32 sets
   # "39.Eḷakalomāni…" with NO SPACE, so the extraction saw no boundary and
   # unit 39's text arrived inside ord38, the paragraph carrying n=38.  The
   # mark is the printed unit's WHOLE FIRST LINE (2026-07-26ad).
   'kat_splices': [
     {'n': 39, 'pg': 32, 'ord': 38, 'into': 38,
      'mark': '39.Eḷakalomāni paṭiggahetvā tiyojanaṁ atikkāmentassa nissaggiyaṁ'},
   ],
   'split_literals': {
     '2. Katāpattivāra 1. Pārājikakaṇḍa':           # pdf p69
         ['2. Katāpattivāra', '1. Pārājikakaṇḍa'],
     '1. Katthapaññattivāra 1. Pārājikakaṇḍa':      # pdf p110, p159
         ['1. Katthapaññattivāra', '1. Pārājikakaṇḍa'],
   },
 },

 # DĪGHANIKĀYA II — one book, the ten suttas of the Mahāvagga.
 # SCOUTED 2026-07-27: extent 1-based 10-292 (0-based body gate `9 291`);
 # 0-based 292 is the printed word index.  444 corpus paragraphs, ALL numbered.
 # Geometry: the body column is 0 (6,433 lines), numbered units sit at indent
 # 3-6, display material at 8+.  768 display lines of which 454 carry a COMMA,
 # so the volume really does print gāthā and `no_verse` is out.
 # !!! ITS TWO `n` RESETS ARE NOT THE EDITION'S — they are the graphic-rule
 # footnote cells of 0-based p154/155/157 taken into the corpus as numbered
 # paragraphs (ord256, ord257, ord260; see pipeline/fnblock.py).  Read as real
 # resets they would have put two phantom book boundaries into this SPEC.
 '07Di02': {
   # !!! `pada_runon` WAS MISSING FROM ALL SIX DĪGHA/MAJJHIMA VOLUMES until
   # 2026-07-27f, and the standing rule says to run this measurement over EVERY
   # volume whenever a new one prints gāthā.  This edition alternates the
   # punctuation of a couplet — first pāda a COMMA, second a FULL STOP — and
   # without the flag every SECOND pāda was classified by form, fell to
   # `centre`, and was flushed to the UDDĀNA map: 09Ma01 p239 sets Brahmā's
   # fourteen pādas at ONE indent (18) and the reader drew seven of them, the
   # even ones, in a block of their own AFTER the verse.  Torn couplets, every
   # word present, 0/0/0/0 on the body gate.
   'pada_runon': True,
   'books': [('Mahāvaggapāḷi', 10, 292, 0, 444, None, 'katha')],
   # Used ONLY by the nav's head_kind().  A stem list would be WORSE than the
   # form test here, which is what `heads_by_form` is for: the mātikā's 147
   # entries end at dozens of distinct forms — -kathā, -upamā, -vāda, -sabhā,
   # -paññatti, -purisa, -pabbajjā, -vaṇṇa, -samuppāda, -tā — with no stem
   # shared by more than a handful.
   'stems': r'sutta|suttaṁ|kathā|pāḷi|vagga|uddāna',
   'n_scope': 'book',
   'heads_by_form': True,
   # THE PĀYĀSISUTTA HEADS ITS FOURTEEN SIMILES WITH A PARENTHESISED NUMBER
   # FIRST — "(1) Candimasūriya-upamā", "(2) Cora-upamā" — and `kat_is_head`
   # requires the core to open with a CAPITAL, so without this every one of
   # them fell through and was read as body prose.  Found by comparing the
   # heads stream against the mātikā: 14 of the 16 entries the body appeared
   # not to head are these, and all 14 are printed and centred at indent 25-30.
   # (Same key 32Abhi04 needed for "(175) 10. Navattabbaṁ…".)
   'head_paren': True,
   # A COLOPHON THE FORM TEST READ AS A HEADING.  Scanning the heads stream for
   # `niṭṭhit|samatt` — a heading that says a section has ENDED is a colophon —
   # finds exactly one in this volume.
   'colofix': {'Ānāpānapabbaṁ niṭṭhitaṁ'},
   # `head_words` MEASURED over all 147 mātikā entries: 133 are ONE word and 14
   # are two, and NOT ONE carries an internal period.  So the default cap of 2
   # is right for this volume and is declared nowhere — but it was measured,
   # not assumed.
   # THE THREE GRAPHIC-RULE FOOTNOTE CELLS THE CORPUS TOOK AS PARAGRAPHS.
   # ord256 is the cell alone; ord257 and ord260 carry the cell with the
   # following page's real body text welded on behind it — the same shape as
   # 05Vin05 ord147.  With `fnblock` cutting those pages the printed side no
   # longer has them, so without this the count reads 441/444.  CONFIRMED that
   # way before declaring it: the build was run first and the shortfall was
   # exactly three.  The welded body text is NOT lost — the kathā path draws
   # the body from the PRINTED stream, and the body gate at minw 1 is what
   # proves it.
   'backmatter': [256, 257, 260],
 },

 # DĪGHANIKĀYA I — one book, the thirteen suttas of the Sīlakkhandhavagga.
 # SCOUTED 2026-07-27.  559 corpus paragraphs, ALL numbered, ZERO `n` resets,
 # and `fnblock` finds NO graphic-rule page here — the cleanest canon volume
 # scouted so far.
 # !!! ITS EXTENT IS NOT THE ONE THE PDF DECLARES.  The metadata says 1-based
 # 20-255; the printed FOLIO says 19-254, and it was checked at BOTH ENDS
 # (33Abhi05's lesson, where the head was corrected and the tail left):
 # 0-based 17 carries the roman folio `xvi`, 0-based 18 is the TITLE PAGE and
 # so printed page 1, 0-based 19 carries printed `2`; at the tail 0-based 253
 # carries `236` and closes `Sīlakkhandhavaggapāḷi niṭṭhitā.`, and 0-based 254
 # opens the printed word index `Lakkhitabbapadānaṁ anukkamaṇikā`.  The
 # declared LENGTH (236 pages) is right and the OFFSET is wrong, at both ends —
 # exactly 33Abhi05's shape.  Body gate 0-based: `18 253`.
 # !!! THE MĀTIKĀ IS 0-BASED 12-17 AND NOT WHAT A `Piṭṭhaṅka` SEARCH RETURNS:
 # this volume's BACK MATTER (the word index and the `Nānāpāṭhā` variant
 # appendix, 0-based 254-264) heads its columns `Piṭṭhaṅko` too, so the naive
 # search returns sixteen pages.  Measure the mātikā, then look at it.
 '06Di01': {
   # !!! `pada_runon` WAS MISSING FROM ALL SIX DĪGHA/MAJJHIMA VOLUMES until
   # 2026-07-27f, and the standing rule says to run this measurement over EVERY
   # volume whenever a new one prints gāthā.  This edition alternates the
   # punctuation of a couplet — first pāda a COMMA, second a FULL STOP — and
   # without the flag every SECOND pāda was classified by form, fell to
   # `centre`, and was flushed to the UDDĀNA map: 09Ma01 p239 sets Brahmā's
   # fourteen pādas at ONE indent (18) and the reader drew seven of them, the
   # even ones, in a block of their own AFTER the verse.  Torn couplets, every
   # word present, 0/0/0/0 on the body gate.
   'pada_runon': True,
   'books': [('Sīlakkhandhavaggapāḷi', 19, 254, 0, 559, None, 'katha')],
   # used only by the nav's head_kind(); as in 07Di02 a stem list cannot carry
   # this volume — its 132 mātikā entries end at dozens of distinct forms.
   'stems': r'sutta|suttaṁ|kathā|vatthu|vāra|pāḷi|vagga|uddāna',
   'n_scope': 'book',
   'heads_by_form': True,
   # A SECTION HEADING THE EDITION PRINTS WITH A FULL STOP, so `kat_is_colo`
   # claimed it as a colophon.  0-based p148 sets `Dasa-ākāra.` at indent 31
   # and unit 343 opens directly beneath it; the mātikā lists it at printed
   # p131 immediately after `Tisso vidhā`, which IS read as a heading.  Found
   # by diffing the heads stream against the mātikā — no content gate can see
   # a wrong ROLE.  (The inverse of 07Di02's `colofix`.)
   'headfix': {'Dasa-ākāra.'},
 },

 # DĪGHANIKĀYA III — one book, the eleven suttas of the Pāthikavagga.
 # SCOUTED 2026-07-27.  360 corpus paragraphs, all numbered, ZERO `n` resets,
 # no graphic-rule page.  Extent CONFIRMED BY FOLIO at both ends and it agrees
 # with the metadata for once: 0-based 8 closes the mātikā, 0-based 9 is the
 # title page, 0-based 268 carries printed `260`, 0-based 269 opens the word
 # index.  Body gate 0-based `9 268`.  Mātikā 0-based 3-8.
 '08Di03': {
   # !!! `pada_runon` WAS MISSING FROM ALL SIX DĪGHA/MAJJHIMA VOLUMES until
   # 2026-07-27f, and the standing rule says to run this measurement over EVERY
   # volume whenever a new one prints gāthā.  This edition alternates the
   # punctuation of a couplet — first pāda a COMMA, second a FULL STOP — and
   # without the flag every SECOND pāda was classified by form, fell to
   # `centre`, and was flushed to the UDDĀNA map: 09Ma01 p239 sets Brahmā's
   # fourteen pādas at ONE indent (18) and the reader drew seven of them, the
   # even ones, in a block of their own AFTER the verse.  Torn couplets, every
   # word present, 0/0/0/0 on the body gate.
   'pada_runon': True,
   'books': [('Pāthikavaggapāḷi', 10, 269, 0, 360, None, 'katha')],
   'stems': r'sutta|suttaṁ|kathā|vatthu|vāra|pāḷi|vagga|uddāna',
   'n_scope': 'book',
   'heads_by_form': True,
   # TWO COLOPHONS THE FORM TEST READ AS HEADINGS.
   #  * `Dasuttarasuttaṁ niṭṭhitaṁ ekādasamaṁ` — the standing `niṭṭhit|samatt`
   #    scan finds it; it closes the volume's last sutta and prints no stop.
   #  * `Tīhi vaggehi paṭimaṇḍito sakalo` — the FIRST LINE OF A TWO-LINE
   #    COLOPHON, `… / Dīghanikāyo samatto.` (0-based p268).  The stop is on
   #    the second line, so the first had no terminal punctuation and was read
   #    as a heading.  It is a colophon LINE, so `colofix` gives it the right
   #    role rather than merely denying it the wrong one.
   'colofix': {'Dasuttarasuttaṁ niṭṭhitaṁ ekādasamaṁ',
               'Tīhi vaggehi paṭimaṇḍito sakalo'},
   # THE DASUTTARASUTTA'S ENUMERATED DYADS, READ AS HEADINGS.  The sutta lists
   # pairs of qualities and numbers each in parentheses AFTER the stop —
   # `Ajjavañca lajjavañca. (13)` — so the line ends in `)` and the form test
   # saw no terminal punctuation.  They sit at INDENT 4, the body column, in an
   # unbroken run; they are body text and nothing more.  Same shape as
   # 05Vin05's Palibodhapañhābyākaraṇa pādas, and the same key.
   # Taken from the build's own `--show` listing, not retyped.
   'headskip': (
     'Dhātukusalatā ca manasikārakusalatā ca. (10)',
     'Āyatanakusalatā ca paṭiccasamuppādakusalatā ca. (11)',
     'Ṭhānakusalatā ca aṭṭhānakusalatā ca. (12)',
     'Ajjavañca lajjavañca. (13)',
     'Khanti ca soraccañca. (14)',
     'Sākhalyañca paṭisanthāro ca. (15)',
     'Avihiṁsā ca soceyyañca. (16)',
     'Muṭṭhassaccañca asampajaññañca. (17)',
     'Sati ca sampajaññañca. (18)',
     'Paṭisaṅkhānabalañca1 bhāvanābalañca. (21)',
     'Satibalañca samādhibalañca. (22)',
     'Samatho ca vipassanā ca. (23)',
     'Samathanimittañca paggahanimittañca. (24)',
     'Paggaho ca avikkhepo ca. (25)',
     'Sīlavipatti ca diṭṭhivipatti ca. (26)',
     'Sīlasampadā ca diṭṭhisampadā ca. (27)',
     'Sīlavisuddhi ca diṭṭhivisuddhi ca. (28)',
   ),
 },
 '32Abhi04': {
   'books': [('Kathāvatthupāḷi', 15, 468, 0, 918, None, 'katha')],
   'stems': r'kathā|vagga|vaggo|anuyoga|yutti|pāḷi',
   'n_scope': 'book',
   'heads_by_form': True,
   'head_paren': True,
   # !!! FOUND 2026-07-26af WHILE BUILDING 03Vin03, not when this volume was
   # built: 45 of the gāthā it quotes had pādas classified as COLOPHONS and
   # drawn as centred closing lines ("Tayassu dhammā jahitā bhavanti.",
   # "Sīlabbataṁ vāpi yadatthi kiñci." and 43 more).  0/0/0/0 from the body
   # gate.  Three gates and `_abhi04verify.js` re-run.
   'pada_runon': True,
   # A DISPLAY BLOCK IS NOT ALWAYS VERSE.  This book quotes suttas constantly —
   # 35 of its 37 display blocks are genuine gāthā — but two are its own
   # DIALOGUE set at the same indent, and both open with the book's own formula
   # "Attheva suttantoti, āmantā." ("Is there such a sutta? — Yes.").  The pāda
   # test catches one of them (its second line runs on); the other has both
   # lines ending in a full stop, so the formula is what decides it, named as in
   # 27Khu10 rather than generalised.
   'display_prose': True,
   'prose_openers': r'Attheva suttantoti',
   # ITS LONGEST HEADING IS CENTRED AT INDENT 7, below the display gate, and is
   # NAMED here rather than reached by loosening that gate — see the comment at
   # the `headfix` branch.  A census over the volume's text extent finds exactly
   # one heading below the gate.
   'headfix': ('(175) 10. Navattabbaṁbuddhassadinnaṁmahapphalantikathā',),
 },
 '31Abhi03': {
   # !!! `pada_runon` BELONGS HERE AND WAS NEVER SET.  HANDOFF has recorded
   # since 2026-07-26 that it "corrected FOUR shipped volumes — 31Abhi03 (11)"
   # — but the flag was absent, so the eleven were never actually corrected.
   # Measured 2026-07-27g: with the flag on, exactly ELEVEN lines stop being
   # colophons, every one a second pāda of a Dhātukathā mnemonic couplet
   # (`Itthipumaṁ jīvitaṁ nāmarūpaṁ.`, `Dhātūsu satta dvepi ca indriyato.`).
   # THE REASON IT COULD NOT BE SET BEFORE was collateral: the comma clause
   # also demoted `Ekakaṁ.` (p110 indent 38), a REAL colophon closing the
   # Ekaka-uddesa, because the line above it is the list item
   # `54. …paṭipanno,` at indent 6.  Requiring the comma to be a NEIGHBOUR's
   # (|Δindent| <= 2) fixes that — proven byte-identical on all thirteen
   # volumes that already carry `pada_runon` — and `Ekakaṁ.` now survives.
   'pada_runon': True,
   'books': [('Dhātukathāpāḷi',       8, 107,   0, 518, None, 'katha'),
             ('Puggalapaññattipāḷi',108, 192, 518, 890, None, 'katha')],
   'stems': r'kathā|paññatti|uddesa|niddesa|mātikā|vāra|pāḷi',
   'n_scope': 'book',
   'heads_by_form': True,
   # THE SAME MEASUREMENT AS 30Abhi02, and it separates the two books cleanly:
   # the Dhātukathā's nine uddāna gāthā sit at indents 8, 12 and 13, and the one
   # run in the Puggalapaññatti sits at 6 and is PROSE — its catechetical
   # "Kathañca puggalo oṇatuṇṇato hoti -pa-." set one clause per printed line.
   'verse_indent': 8,
 },
 # --- Paṭṭhāna I: the same kathā shape, MEASURED not carried over ----------
 # 1091 corpus paragraphs of which 91 are LEAKED HEADINGS — the edition sets
 # two centred headings on one line ("1. Kusalattika   1. Paṭiccavāra") and the
 # corpus captured 91 of those lines whole, as paragraphs carrying the first
 # heading's number.  Hidden before the pairing, as everywhere else.
 # `heads_by_form` fits here too, but a numbered line needed the extra test
 # documented in `kat_items`: this book's 69 numbered headings are all one or
 # two words, carry no internal period and sit at indent 22-30, while its units
 # do not — and two of its units sit flush at the left margin.
 '36Abhi08': {
   'books': [('Tikapaṭṭhānapāḷi', 30, 493, 0, 1091, None, 'katha')],
   'stems': (r'vāra|vāro|paṭṭhāna|attika|duka|dukaṁ|tika|tikaṁ|mūlaka|'
             r'mūlakaṁ|uddesa|niddesa|pada|padaṁ|anuloma|anulomaṁ|'
             r'paccanīya|paccanīyaṁ'),
   'n_scope': 'book',
   'heads_by_form': True,
   'no_verse': True,
   'orphan_sections': True,
   'head_order': True,
   'split_unnumbered': True,
   'kat_splices': [
     {'n': 41, 'pg': 373, 'ord': 831, 'into': 40,
      'mark': '41.Nevavipākanavipākadhammadhammaṁ paṭicca'},
   ],
   # !!! FOUND 2026-07-26ae WHILE SCOUTING THE VINAYA, not when this volume was
   # built: 8 of its uddāna PĀDAS were classified as COLOPHONS and drawn as
   # centred closing lines in the middle of a section ("Dukaṁ tikañceva tikaṁ
   # dukañca." / "Cha anulomamhi nayā sugambhīrāti.", p44-p47).  Under
   # `heads_by_form` a colophon is decided by form alone and the second pāda of
   # a couplet has exactly that form; the line above it ends in a COMMA, so it
   # is mid-sentence.  0/0/0/0 from the body gate either way.  Gates re-run.
   'pada_runon': True,
   # p160 wraps a parenthetical editorial note onto a second CENTRED line
   # ("(Saṁsaṭṭhattaṁ nāma sampayuttattaṁ, sampayuttattaṁ nāma" /
   # "saṁsaṭṭhattaṁ.)"), which rendered as two paragraphs.  FOUND
   # 2026-07-26ae while scouting the Vinaya; three gates re-run.
   'wrap_display': True,
 },
'37Abhi09': {
   'books': [('Tikapaṭṭhānapāḷi', 28, 520, 0, 1268, None, 'katha')],
   'stems': (r'vāra|vāro|paṭṭhāna|attika|duka|dukaṁ|tika|tikaṁ|mūlaka|'
             r'mūlakaṁ|uddesa|niddesa|pada|padaṁ|anuloma|anulomaṁ|'
             r'paccanīya|paccanīyaṁ'),
   'n_scope': 'book',
   'heads_by_form': True,
   'no_verse': True,
   'orphan_sections': True,
   'head_order': True,
   'split_unnumbered': True,
   # A CENSUS, not a discovery one at a time: over the volume's whole text
   # extent exactly TWO display lines carry two numbered halves separated by
   # one or two spaces.  36Abhi08 has none.  Both are here.
   'split_literals': {
     '2. Paccayapaccanīya 2. Saṅkhyāvāra':          # pdf p316
         ['2. Paccayapaccanīya', '2. Saṅkhyāvāra'],
     '19. Atītārammaṇattika 7. Pañhāvāra':          # pdf p449
         ['19. Atītārammaṇattika', '7. Pañhāvāra'],
   },
 },
'38Abhi10': {
   'books': [('Dukapaṭṭhānapāḷi', 7, 611, 0, 2060, None, 'katha')],
   'stems': (r'vāra|vāro|paṭṭhāna|attika|duka|dukaṁ|tika|tikaṁ|mūlaka|'
             r'mūlakaṁ|uddesa|niddesa|pada|padaṁ|anuloma|anulomaṁ|'
             r'paccanīya|paccanīyaṁ'),
   'n_scope': 'book',
   'heads_by_form': True,
   'no_verse': True,
   'orphan_sections': True,
   'head_order': True,
   'split_unnumbered': True,
   # A census over the volume's text extent finds exactly ONE heading pair in
   # which a half carries no space after its number: printed p87 sets
   # "1. Paccayānuloma      1.Vibhaṅgavāra".  Read whole it starts with a
   # number and became a UNIT.
   # THE EDITION'S OWN MISSPELLING, preserved verbatim and named here only so
   # the builder RECOGNISES the line: printed p159 sets "Saṅkhyāvara" with a
   # short 'a' where every other occurrence in the piṭaka reads "Saṅkhyāvāra".
   # It leaked into the corpus as ord517 and, unhidden, took a unit's ordinal.
   # The corpus opens at unit 2: printed unit 1 is in NO corpus paragraph.
   'kat_missing': [
     {'n': 1, 'pg': 7,
      'absent': 'Hetuṁ dhammaṁ paṭicca hetu dhammo uppajjati hetupaccayā'},
   ],
   'headfix': ('2. Paccayapaccanīya      2. Saṅkhyāvara',),
   'split_literals': {
     '1. Paccayānuloma 1.Vibhaṅgavāra':
         ['1. Paccayānuloma', '1. Vibhaṅgavāra'],
   },
 },
'39Abhi11': {
   # THREE inner books, each with its own title page and homage, measured
   # off the corpus `book` field and confirmed against those pages:
   #   0-based 203 and 475 are the second and third title pages, 474 is blank.
   'books': [('Dukapaṭṭhānapāḷi',      10, 203,    0,  658, None, 'katha'),
             ('Dukatikapaṭṭhānapāḷi', 204, 474,  658, 2266, None, 'katha'),
             ('Tikadukapaṭṭhānapāḷi', 476, 645, 2266, 2985, None, 'katha')],
   'stems': (r'vāra|vāro|paṭṭhāna|attika|duka|dukaṁ|tika|tikaṁ|mūlaka|'
             r'mūlakaṁ|uddesa|niddesa|pada|padaṁ|anuloma|anulomaṁ|'
             r'paccanīya|paccanīyaṁ'),
   'n_scope': 'book',
   'heads_by_form': True,
   'no_verse': True,
   'orphan_sections': True,
   'head_order': True,
   'split_unnumbered': True,

 },
'40Abhi12': {
   # TWENTY BOOKS.  The edition prints a title page and a homage for every
   # naya x paṭṭhāna pair, and this volume carries the last two of the
   # Dhammānuloma plus all six of each of the other three nayas.  The
   # boundaries are the HOMAGE PAGES — the corpus `book` field is wrong here
   # (it labels pdf 174, still inside Dhammapaccanīya Dukaduka, as
   # Dhammānulomapaccanīya Tika).
   #
   # ERRATUM, preserved: the title page at 0-based 176 reads
   # "Abhidhammapiṭika" for Abhidhammapiṭaka.
   'books': [
             ('Dhammānuloma Tikatikapaṭṭhānapāḷi',              5,   42,     0,   190, None, 'katha'),
             ('Dhammānuloma Dukadukapaṭṭhānapāḷi',             43,   66,   190,   335, None, 'katha'),
             ('Dhammapaccanīya Tikapaṭṭhānapāḷi',              67,   76,   335,   392, None, 'katha'),
             ('Dhammapaccanīya Dukapaṭṭhānapāḷi',              77,  108,   392,   504, None, 'katha'),
             ('Dhammapaccanīya Dukatikapaṭṭhānapāḷi',         109,  126,   504,   614, None, 'katha'),
             ('Dhammapaccanīya Tikadukapaṭṭhānapāḷi',         127,  142,   614,   725, None, 'katha'),
             ('Dhammapaccanīya Tikatikapaṭṭhānapāḷi',         143,  162,   725,   828, None, 'katha'),
             ('Dhammapaccanīya Dukadukapaṭṭhānapāḷi',         163,  176,   828,   908, None, 'katha'),
             ('Dhammānulomapaccanīya Tikapaṭṭhānapāḷi',       177,  200,   908,   986, None, 'katha'),
             ('Dhammānulomapaccanīya Dukapaṭṭhānapāḷi',       201,  218,   986,  1068, None, 'katha'),
             ('Dhammānulomapaccanīya Dukatikapaṭṭhānapāḷi',   219,  248,  1068,  1265, None, 'katha'),
             ('Dhammānulomapaccanīya Tikadukapaṭṭhānapāḷi',   249,  292,  1265,  1509, None, 'katha'),
             ('Dhammānulomapaccanīya Tikatikapaṭṭhānapāḷi',   293,  310,  1509,  1592, None, 'katha'),
             ('Dhammānulomapaccanīya Dukadukapaṭṭhānapāḷi',   311,  330,  1592,  1716, None, 'katha'),
             ('Dhammapaccanīyānuloma Tikapaṭṭhānapāḷi',       331,  340,  1716,  1764, None, 'katha'),
             ('Dhammapaccanīyānuloma Dukapaṭṭhānapāḷi',       341,  352,  1764,  1826, None, 'katha'),
             ('Dhammapaccanīyānuloma Dukatikapaṭṭhānapāḷi',   353,  380,  1826,  2020, None, 'katha'),
             ('Dhammapaccanīyānuloma Tikadukapaṭṭhānapāḷi',   381,  406,  2020,  2173, None, 'katha'),
             ('Dhammapaccanīyānuloma Tikatikapaṭṭhānapāḷi',   407,  428,  2173,  2299, None, 'katha'),
             ('Dhammapaccanīyānuloma Dukadukapaṭṭhānapāḷi',   429,  446,  2299,  2413, None, 'katha'),
            ],
   'stems': (r'vāra|vāro|paṭṭhāna|attika|duka|dukaṁ|tika|tikaṁ|mūlaka|'
             r'mūlakaṁ|uddesa|niddesa|pada|padaṁ|anuloma|anulomaṁ|'
             r'paccanīya|paccanīyaṁ'),
   'n_scope': 'book',
   'heads_by_form': True,
   'no_verse': True,
   'orphan_sections': True,
   'head_order': True,
   'split_unnumbered': True,
   # A census over the volume's text extent finds exactly ONE heading pair
   # whose second half carries NO FULL STOP after its number: printed p48 sets
   # "1. Hetuduka    19-53 Saññojanādiduka".  Making the stop optional in the
   # general rule would split ordinary unit text; naming the line does not.
   'split_literals': {
     '1. Hetuduka 19-53 Saññojanādiduka':
         ['1. Hetuduka', '19-53. Saññojanādiduka'],
   },

 },
}

# The edition's own misprints, RECORDED AND PRESERVED VERBATIM — never
# corrected in the text.  They are listed here only so the builder can
# RECOGNISE them: each puts a false descent into the verse-number stream, and
# the first also collides with a real verse number in the same nipāta.
#   22Khu05 p304  prints "24."   where the sequence requires 29
#   23Khu06 p374  prints "2324." where the sequence requires 2342
#   23Khu06 p383  prints "1440." where the sequence requires 2440
# Two further irregularities are typographic rather than numeric, and must be
# RECOGNISED or the line is read as a pāda instead of as a heading:
#   22Khu05 p105  "271. Udapānadūsakajākaka (3-3-1)" — the edition sets
#                 'jākaka' for 'jātaka'; hence the `jākaka` stem above.  It is
#                 the ONLY heading in either volume outside the normal stems.
#   22Khu05 p79   "6. Na taṁ daḷhavagga" — the vagga name is typeset with
#                 internal spaces, though its own colophon closes it up as
#                 "Nataṁdaḷhavaggo chaṭṭho.".  HEADTXT's `[^,]*` already spans
#                 the spaces so this needs no special case, but it is recorded
#                 because any tighter regex would silently drop the heading.
#   25Khu08 p229 opens the Khaggavisāṇasuttaniddesa with "211." where the
#                 sequence requires 121 — the previous lemma is 120 and the
#                 next is 122.  The corpus reproduces the misprint faithfully
#                 (ord294 carries n=211), so pairing BY POSITION places it
#                 correctly and the mismatch is REPORTED rather than absorbed.
#                 A number-keyed map would have read it as an ascent to 211
#                 followed by a descent to 122, i.e. a false segment boundary.
ERRATA = {
 '22Khu05': [{'pdf_page': 304, 'printed': '24.',   'sequence_requires': 29,
              'note': 'collides with the real verse 24 in the same nipāta'}],
 '23Khu06': [{'pdf_page': 374, 'printed': '2324.', 'sequence_requires': 2342},
             {'pdf_page': 383, 'printed': '1440.', 'sequence_requires': 2440}],
 '25Khu08': [{'pdf_page': 233, 'printed': '211.', 'sequence_requires': 121,
              'note': 'opens Khaggavisāṇasuttaniddesa; corpus ord294 keeps it'}],
 # 30Abhi02 closes the last of its eighteen vibhaṅgas "Dhammahadayavibhaṅgo
 # niṭṭhoto." (printed p453) where the other seventeen all read "niṭṭhito." —
 # 'o' for 'i'.  PRESERVED VERBATIM; it needed no `headfix` because the
 # colophon test recognises it by its section name and terminal stop, so this
 # entry exists only so that a later change cannot silently correct it.
 # 31Abhi03 carries TWO misprints, both preserved verbatim and each on its own
 # page.  (1) The BODY heads the fifth section of the Puggalapaññatti's Niddesa
 # "5. Pañcakapaggalapaññatti" — *paggala* for *puggala* — where the volume's own
 # mātikā and its printed word index both set *puggala*; named in the nav
 # builder's `errata` so the mātikā check knows the two are one section.
 # (2) The fourth padaniddesa's COLOPHON reads "Saṅgahitena saṅgahitapasaniddeso
 # catuttho." — *pasaniddeso* for *padaniddeso* — which is why the colophon check
 # reports that one section as not testable rather than failing on it.
 '31Abhi03': [{'pdf_page': 175, 'printed': '5. Pañcakapaggalapaññatti',
               'sequence_requires': 'Pañcakapuggalapaññatti',
               'note': "the body's spelling; the mātikā and index set puggala"},
              {'pdf_page': 45, 'printed': 'Saṅgahitena saṅgahitapasaniddeso '
                                          'catuttho.',
               'sequence_requires': 'padaniddeso',
               'note': 'the other thirteen colophons read padaniddeso'}],
 '30Abhi02': [{'pdf_page': 464, 'printed': 'Dhammahadayavibhaṅgo niṭṭhoto.',
               'sequence_requires': 'niṭṭhito',
               'note': 'the other seventeen vibhaṅga colophons read niṭṭhito'}],
 # 26Khu09 p333 heads the fifth kathā of the Yuganaddhavagga "5. Virāgatathā"
 # where its OWN mātikā (p8) sets "5. Virāgakathā" — 't' for 'k', the same
 # class of typographic misprint as 22Khu05's 'jākaka' for 'jātaka'.  Kept
 # verbatim on the page and listed in SPEC['26Khu09']['headfix'] so that it is
 # still RECOGNISED as a heading; a stem loose enough to match it on its own
 # would be `tathā`, which is among the commonest words in this very volume
 # ("tathā avitathā anaññathā") and would swallow ordinary prose.
 '26Khu09': [{'pdf_page': 333, 'printed': '5. Virāgatathā',
              'matika_has': '5. Virāgakathā'}],
 # 27Khu10's Netti mātikā (p ii) lists "13. Sodanahāravibhaṅga" where the body
 # heads it "13. Sodhanahāravibhaṅga" — the mātikā drops the 'h'.  The SAME
 # mātikā spells the matching sampāta "13. Sodhanahārasampāta" with it, so the
 # two printed pages disagree with each other and one of them with itself.
 # Both are kept exactly as each page sets them; only the nav check is told
 # they are one section.
 '27Khu10': [{'pdf_page': 4, 'printed': '13. Sodanahāravibhaṅga',
              'body_has': '13. Sodhanahāravibhaṅga', 'where': 'Netti mātikā'}],
 # 28Khu11's are unusually many, and two of them are the edition disagreeing
 # with its own arithmetic rather than with its own spelling.  Every one is
 # kept exactly as the page that carries it prints it; the nav check is told
 # which pairs are one section (ERRATUM_SAME in build_milinda_nav.py).
 '28Khu11': [
   # --- structural -------------------------------------------------------
   {'printed': 'the kaṇḍa heads run 1, 2, 4, 5, 6',
    'note': 'there is no "3." anywhere in the body, although the text names '
            'six divisions (p2 "pubbayogo Milindapañhaṁ lakkhaṇapañhaṁ '
            'meṇḍakapañhaṁ anumānapañhaṁ opammakathāpañhan"ti) and the '
            'Nigamana (p407) says "chasu kaṇḍesu"'},
   {'where': 'front mātikā', 'printed': '5. Opammakathāpañha',
    'body_has': '6. Opammakathāpañha',
    'note': 'the mātikā gives "5." to both the fifth kaṇḍa and the sixth'},
   {'where': 'Nigamana p407', 'printed': 'bāvīsativagga° (22 vaggas)',
    'body_has': '23 vaggas', 'note': "the edition's own count of its own pages"},
   {'pdf_page': 250, 'printed': '(3)',
    'note': 'p236 numbers the third pañha of the Anumāna Buddhavagga in '
            'PARENTHESES where every other unit opens "N. ", so it is not a '
            'numbered unit; the corpus spliced its whole text onto ord164'},
   {'pdf_page': 419, 'printed': 'Ito paraṁ rājaṅgapañhādikā aṭṭhatiṁsa pañhā '
                                'vinaṭṭhā …',
    'note': 'the edition records that 38 pañhas are lost; the Opammakathā '
            'mātikā (p345-348) lists them although no body text follows'},
   # --- spelling, body first, mātikā second ------------------------------
   {'body': '6. Satapattaṅgapañhā',  'matika': '6. Satapattaṅgapañha'},
   {'body': '10. Dīghaṭṭhipañha',    'matika': '10. Dhīghaṭṭhipañha'},
   {'body': '15. Viññāṇanānatthapañha', 'matika': '15. Viññāṇanānātthapañha'},
   {'body': '4. Paṭisandahanapuggalavediyanapañha',
    'matika': '4. Paṭisandahanapuggalavediyapañha'},
   {'body': '6. Apuññapañha',        'matika': '6. Apaññapañha'},
   {'body': '7. Bhikkhusaṁghapariharaṇapañha',
    'matika': '7. Bhikkhusaṁghaparihāraṇapañha'},
   {'body': '10. Dhammadesanāya appossukkapañha',
    'matika': '10. Dhammadesanāya appossukapañha'},
   {'body': '5. Dvinnaṁ lokuppannānaṁ samakabhāvapañha',
    'matika': '5. Dvannaṁ lokuppannānaṁ samakabhāvapañha'},
   {'body': '3. Bījaṅgapañha',       'matika': '3. Vījaṅgapañha'},
   {'body': '9. Bāḷisikaṅgapañha',   'matika': '9. Bhāḷisikaṅgapañha'},
   {'body': '9. Vahāhaṅgapañha',     'matika': '9. Varāhaṅgapañha'},
   {'body': 'Sīhavaggo pañcamo. (p392)',
    'matika': 'Sīlavaggo pañcamo. (p345)'},
   {'printed': 'Imasmiṁ vagge dvādassa pañhā. (p186)',
    'note': "'dvādassa' for 'dvādasa'"},
 ],
}

VOL = None; BOOKS = None; PDF = None; HEADTXT = None

# Literals named in `headskip` that were actually met on the printed page.
# The build REFUSES if a declared literal is never printed, so the list cannot
# rot into a lie about the edition — the same discipline the nav builder's
# `head_skip` already has.
HEADSKIP_SEEN = set()

# Literals named in `coloskip` that were actually met as a candidate
# colophon.  Same discipline as `headskip`: the build REFUSES if a
# declared literal is never met, so the list cannot rot.
COLOSKIP_SEEN = set()


def headskip(t):
    """A line NAMED in `headskip` is NOT a heading, wherever it sits.

    The inverse of `headfix`, and it exists for the opposite failure.  Under
    `heads_by_form` a line is a heading if it LOOKS like one, and this edition
    prints body lines that do: 05Vin05's Palibodhapañhābyākaraṇa answers each
    question with a numbered pāda — "Cīvare niṭṭhite cīvarapalibodho chijjati.
    (2)" — whose parenthesised answer-number leaves it with no terminal stop,
    so seven of them were drawn as centred HEADINGS in the middle of a gāthā;
    and 03Vin03 p23 closes Brahmā's verse with "Aññātāro bhavissantī”ti.]", the
    last pāda plus the bracket closing the editorial insertion opened on p20.

    NOTHING IS SUPPRESSED.  The line keeps its place and every word of its
    text — only its ROLE changes, from a heading to the display line it is.  So
    `verify_render_vs_pdf.py` is unmoved BY CONSTRUCTION, which is the point:
    the body gate cannot see this class at all (all eight read 0/0/0/0 for as
    long as they have been wrong), and what moves is `check_layout.js`, the
    reader, and the nav — where a false heading takes real sections as its
    CHILDREN.  That is why it must be named and not merely hidden.

    A literal, never a pattern: each of the eight is a sentence of the text and
    a rule general enough to catch them would catch real headings too.
    """
    if t.strip() in SPEC[VOL].get('headskip', ()):
        HEADSKIP_SEEN.add(t.strip())
        return True
    return False


def use(vol):
    """Bind the module to one volume's spec."""
    global VOL, BOOKS, PDF, HEADTXT
    VOL = vol
    BOOKS = SPEC[vol]['books']
    # THE PDF IS NOT ALWAYS UNDER `pali-unicode`.  The 52 commentary volumes
    # live in `atthakatha-unicode` and the 26 subcommentaries in `tika-unicode`,
    # which is the same three-folder search `verify_render_vs_pdf.py`,
    # `rebuild_apparatus.py` and `build_incipit.py` have always done.  Inert for
    # every canon volume by construction — `pali-unicode` is tried first and all
    # forty are there.
    PDF = next((_p for _d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode')
                for _p in [os.path.join(ROOT, _d, vol + '.pdf')]
                if os.path.exists(_p)),
               os.path.join(ROOT, 'pali-unicode', vol + '.pdf'))
    # The parenthesised tail after a heading is not always a single number.
    # 20Khu03/21Khu04 set "(5)"; the Jātaka sets the jātaka's nipāta-vagga-
    # position triple, "(2-8-4)", and one uddāna carries "(6652)".  Widened to
    # digits/dots/spaces/hyphens, which is a strict superset of the old
    # `(\d+)` — the 19Khu02 regression is what proves it changes nothing there.
    HEADTXT = re.compile(r'^[A-ZĀĪŪṄÑṆṬḌḶ][^,]*(' + SPEC[vol]['stems']
                         + r')\d*\s*(\([\d\s.–-]+\))?$')

FNRULE = re.compile(r'^\s*_{20,}\s*$')
DECOR  = re.compile(r'^\s*_{3,19}\s*$')
# !!! A UNIT NUMBER IS NOT ALWAYS A SINGLE NUMBER — IT CAN BE A RANGE.
# The Saṁyutta's peyyāla sections number one printed unit for several
# suttas at once: 14Sam03 0-based p39 sets `42-47. Sace vo bhikkhave…` at
# indent 5 under the heading `2-7. Saṁyojanappahānādisuttachakka`, and the
# corpus holds it as ONE paragraph with n=42.  Matching only `^N.` made 94
# printed units invisible to the page reader — 13Sam02 337/361 and 345/361,
# 14Sam03 544/598 — which reads as a corpus overrun and is nothing of the
# kind.  `HEADNUM` below has admitted the same form for HEADINGS since the
# Apadāna's `3-1.`; this is that form on the unit side.  The captured number
# is the FIRST of the range, which is what the corpus `n` carries.
#
# VERSE IS SHARED MACHINERY (16 call sites, including the body-column
# measurement `_kat_cols`), so it was MEASURED OLD-vs-NEW OVER ALL 36
# VOLUMES IN SPEC BEFORE APPLYING — build each twice with the same builder
# and diff the five side-maps (`_fnprobe/rangediff.py`, which enumerates
# what changes rather than counting it).  THIRTY-FOUR ARE BYTE-IDENTICAL,
# printed-unit and colophon counts unmoved, and the only two that move are
# 13Sam02 and 14Sam03.  12Sam01 is inert: it prints no range.
VERSE  = re.compile(r'^(\d+)(?:-\d+)?\.\s*(.*)$')
# A heading's number is not always a plain "N.".  The Apadāna numbers the third
# group of Buddhavagga as "3-1." … "3-10." (Sāriputta, Mahāmoggallāna,
# Khadiravaniyarevata, Ānanda and six more).  Matching only "^N." dropped all ten
# out of the headings and into the colophon stream, so they rendered as centred
# uddāna lines and never reached the tree or the Contents.
HEADNUM = re.compile(r'^\d+(?:-\d+)?\.\s')
# THE EDITION CAPITALISES "Tassa" IN TWO VOLUMES — 38Abhi10 (its only homage)
# and 31Abhi03 (one of its two).  Unrecognised, the line is not lifted into
# `incipit` at all: it stays in the body AND the reader draws its built-in
# fallback above it, so the page shows the homage twice.  Matched either way
# here; the incipit keeps the printed capital verbatim.
# !!! ...AND THE EDITION MISPRINTS THE HOMAGE ITSELF IN ONE PLACE:
# `Namo tassa **Bhagavatā** Arahato Sammāsambuddhassa.`  17An03 0-based p279
# is the DASAKANIPĀTA's title page and sets it that way, so the line was not
# lifted into `incipit` at all — it stayed in the body, was classified
# `gatha`, and the reader drew its built-in fallback homage above it, which
# is the page-shows-it-twice failure described just above.  17An03 built with
# THREE incipits for FOUR books, and no content gate could see it.
# MEASURED over all 40 canon volumes: the whole-line form occurs in 17An03 x1
# and 18Khu01 x1 and NOWHERE else.  **18Khu01 is SHIPPED and is NOT affected**
# — checked directly rather than assumed: `incipit/18Khu01.json` already holds
# the misprint verbatim at ord705 (Suttanipāta), because that volume is built
# by `build_suttanipata.py` and never consults this pattern.
# MEASURED OLD-vs-NEW OVER ALL 39 VOLUMES IN SPEC (`_fnprobe/homagediff.py`):
# THIRTY-EIGHT ARE BYTE-IDENTICAL and the only one that moves is 17An03.
# The incipit keeps the printed spelling verbatim; nothing is corrected.
# !!! THE EDITION MISPRINTS ITS OWN HOMAGE, and this is the THIRD slip the
# pattern has had to absorb: `Namo Tassa` and `Bhagavatā` were the first two
# (2026-07-27j, where the misprint hid a whole book from the homage scan),
# and 05Kankha adds `SammāsamBuddhassa` with a capital B in THREE of its four
# books.  Widened by one character class; measured old-vs-new by rebuilding
# every volume that has side-maps (`_kankha/homage_measure.py`).
HOMAGE = re.compile(r'Namo [Tt]assa Bhagavat[oā] Arahato Sammāsam[Bb]uddhassa')
# !!! `Tassudānaṁ` — ONE `d` — IS THE EDITION'S OWN MISPRINT, AND IT MUST BE
# RECOGNISED OR THE LABEL IS NOT A LABEL.  14Sam03 0-based p233 centres it at
# indent 32 above the Balakaraṇīyavagga's two mnemonic pādas, with the vagga
# colophon directly above and a rule below; unmatched here it fell to the
# heading test and entered the heads stream as a HEADING, stranding its two
# pādas in `verse[...]['before']`.  Found by the MĀTIKĀ DIFF — no content gate
# can see it, because every word is present.
# The printed spelling is PRESERVED VERBATIM and never corrected; the same
# treatment `PROSEOPEN` below already gives two other misprints of this edition
# ("Ittaṁ sudaṁ", "abhiāsitthāti").
# !!! AND IT REACHES A SHIPPED VOLUME.  Measured over all 40 canon volumes, the
# whole-line form occurs in 14Sam03 x1 and **20Khu03 x2** and nowhere else.  In
# 20Khu03 (ord1412 Sakacintaniyavagga, ord3133 Ekapadumiyavagga) the label was
# sitting as the FIRST LINE of the uddāna block with `label: null` — the same
# wrong role, shipped.  MEASURED OLD-vs-NEW OVER ALL 36 VOLUMES IN SPEC
# (`_fnprobe/udlbldiff.py`): thirty-four byte-identical, and the only two that
# move are these.
UDDLBL = re.compile(r'^(Tassuddānaṁ|Tassudānaṁ|Tatruddānaṁ|Atha vagguddānaṁ|'
                    r'Vagguddānaṁ|[A-ZĀĪŪṄÑṆṬḌḶ]\S*uddānaṁ|Nidānagāthā)\d*$')
# A body-column line that OPENS a prose run.  Indent cannot decide this: the
# edition sets the closing formula "Itthaṁ sudaṁ … abhāsitthāti." flush with the
# verse number on one page and flush with the pādas on the next (p235 vs p236),
# so alignment is not authority.  Classify by form and render it consistently as
# prose; the run then continues until the next verse number or centred line.
# NOTE the edition's own spellings here are not uniform, and two are outright
# printing errors which are preserved verbatim (never corrected) but must still
# be RECOGNISED, or the closing formula is read as a pāda and lands inside the
# verse: 20Khu03 prints "Ittaṁ sudaṁ" at ord2676 and "abhiāsitthāti" at ord3110.
PROSEOPEN = re.compile(r'^(Itt[h]?h?aṁ sudaṁ|Ittaṁ sudaṁ|\(|“|Idha bhante|Evaṁ me sutaṁ)')
DIVISION = re.compile(r'(itthivimāna|purisavimāna)$', re.I)
NIPATA   = re.compile(r'nipāta\d*$', re.I)
VAGGA    = re.compile(r'vagga\d*$', re.I)
# A heading may carry the edition's `*`/`+` cross-reference marker between its
# number and its name ("224. * Kumbhilajātaka (2-8-4)").  Strip it before the
# heading test, or every starred jātaka heading is read as a verse.  This is
# safe for ordinary verse text that also opens with `*` ("224. * Sace vo
# vuyhamānānaṁ, sattannaṁ…") because HEADTXT's `[^,]*` cannot span the comma
# and the pattern is anchored at both ends.
STAR = re.compile(r'^[*+]\s*')


def head_body(s):
    """A heading's text with its cross-reference marker removed."""
    return STAR.sub('', s.strip())


def _add_line(lst, s):
    """Append a printed line to a centred block, rejoining line-end hyphenation.

    The uddāna verses hyphenate compounds across the line break — 22Khu05 p266
    sets "Atha pāni yudhañcayako ca dasa-" / "Ratha saṁvara pāragatena navāti."
    for *Dasaratha*.  The body path already rejoined on the hyphen; the centred
    path did not, so those two printed lines were never matched as the one line
    the edition means.  Rejoin ON THE HYPHEN AND NOTHING ELSE — every wider rule
    also swallows ordinary wraps and fabricates words, and two such rules have
    already been caught here by the 19Khu02 regression.
    """
    if lst and lst[-1].endswith('-'):
        lst[-1] = hyjoin(lst[-1], s)
    else:
        lst.append(s)


def _norm(s):
    """Letters only, folded — for comparing printed text against corpus text."""
    return re.sub(r'[^a-zāīūṁṃṅñṇṭḍḷ]', '', (s or '').lower())


def _spliced(para, txt, words=4):
    """Did the corpus merge this printed verse into `para`?

    Tested by CONTENT: the verse's opening words must already be inside that
    paragraph.  Deliberately not tested by the stray verse number left in the
    text — a footnote marker ("…Yāmuno4. Catuppadoyaṁ…") can imitate a number
    but cannot imitate the words.
    """
    head = _norm(' '.join(txt.split()[:words]))
    return bool(head) and head in _norm(para.get('text'))


def is_nipata_head(t):
    """Is this centred line a NIPĀTA heading ('2. Dukanipāta')?"""
    return bool(HEADNUM.match(t)) and head_kind(t) == 'book' \
        and NIPATA.search(re.sub(r'^\d+(?:-\d+)?\.\s*', '', t).strip())


# THE GLYPH ERRATUM REGISTER.  `data/glyph_errata.json` records every residual
# non-Pāḷi character the §3 census finds — unmapped glyphs of the VZTimes
# conversion, NOT readings of the edition.  An entry is APPLIED here only when
# it carries `apply_from` and `apply_to`; `fix` alone is a belief and changes
# nothing.  Correcting one is therefore a data edit, not a code edit.
#
# !!! THIS IS NOT "CORRECTING THE EDITION" — working principle 3 forbids that
# and does not bear on this.  The edition prints `Pāyāsivagga`; the CONVERSION
# lost the `ā`, and its own colophon two pages later proves it.  What is
# restored is the edition's own reading.
def _glyph_errata():
    try:
        reg = json.load(open(os.path.join(ROOT, 'data', 'glyph_errata.json'),
                             encoding='utf-8'))
    except Exception:
        return {}
    out = {}
    for e in reg.get('entries', ()):
        if e.get('apply_from') and e.get('apply_to'):
            out.setdefault(e['vol'], {})[e['apply_from']] = e['apply_to']
    return out


GLYPH_ERRATA = _glyph_errata()


def pdf_pages():
    txt = subprocess.run(['pdftotext', '-layout', PDF, '-'],
                         capture_output=True, text=True).stdout
    # EVERY DECLARED SUBSTITUTION MUST BE MET, or the register has rotted — the
    # same guard `headskip` carries.
    for a, b in GLYPH_ERRATA.get(VOL, {}).items():
        if a not in txt:
            raise SystemExit('FATAL: glyph erratum %r declared for %s is not in '
                             'the printed text' % (a, VOL))
        txt = txt.replace(a, b)
    return txt.split('\f')


def page_lines(pages, i):
    raw = [l.rstrip() for l in pages[i - 1].split('\n')]
    # On fourteen pages of the corpus the footnote rule is drawn as a GRAPHIC
    # and pdftotext emits no text line for it, so FNRULE never fires and the
    # apparatus cells enter the printed stream — read as centred HEADINGS on
    # four pages of 05Vin05 and as body text on 03Vin03 p340.  `fn_start`
    # returns None on every page whose rule IS text, so this cannot move a page
    # that already cut correctly.  See pipeline/fnblock.py.
    cut = fnblock.fn_start(raw, where=f'page {i}')
    out = []
    for j, l in enumerate(raw):
        if FNRULE.match(l) or (cut is not None and j >= cut):
            break                                    # footnote block -> end of page
        if l.strip() and not DECOR.match(l):
            out.append(l)
    if out and (re.match(r'^\s*\d+\s{2,}\D', out[0]) or re.search(r'\s{3,}\d+\s*$', out[0])):
        out = out[1:]                                # running page-header
    return [(len(l) - len(l.lstrip()), l.strip()) for l in out]


def join_floating(lines):
    """Join a verse number that is set ALONE on its line to the line below.

    The edition sometimes prints the number on its own and starts the pādas on
    the next line, at a different indent (22Khu05 p214 v18, p356 v188, p400
    v125, p410 v228; 23Khu06 p165 v140).  Left alone, the verse item carries no
    text, fails to map, and its pādas are then appended to the PREVIOUS verse —
    so the words are all still present and no content gate can see anything
    wrong, while the verse has silently lost its number and its frame.  This is
    the same 'floating verse number' the Dhammapada work already had to handle.
    """
    out, i = [], 0
    while i < len(lines):
        ind, t = lines[i]
        m = VERSE.match(t)
        if (m and not m.group(2).strip() and i + 1 < len(lines)
                and not VERSE.match(lines[i + 1][1])):
            out.append((ind, t + ' ' + lines[i + 1][1]))
            i += 2
            continue
        out.append((ind, t))
        i += 1
    return out


def items_for(pages, p0, p1):
    """('centre',txt,pg) | ('verse',n,txt,pg) | ('pada',txt,pg) | ('prose',txt,pg)"""
    items = []
    for pg in range(p0, p1 + 1):
        lines = join_floating(page_lines(pages, pg))
        if not lines:
            continue
        vind = [i for i, t in lines if VERSE.match(t) and i < 20]
        if not vind:
            # A page with no verse number on it is a colophon / uddāna page
            # (p234, p391).  There is no body column to measure against, so the
            # indent rule would call its uddāna lines body text — they are not.
            for ind, t in lines:
                items.append(('homage', t, pg) if HOMAGE.search(t) else ('centre', t, pg))
            continue
        body = min(vind)
        centred = body + 12
        prose_run = False
        for ind, t in lines:
            m = VERSE.match(t)
            if HOMAGE.search(t):
                items.append(('homage', t, pg)); prose_run = False
            elif ind >= centred:
                items.append(('centre', t, pg)); prose_run = False
            elif m and HEADTXT.match(head_body(m.group(2))):
                items.append(('centre', t, pg)); prose_run = False
            elif m:
                items.append(('verse', int(m.group(1)), m.group(2), pg)); prose_run = False
            elif PROSEOPEN.match(t) or prose_run:
                items.append(('prose', t, pg)); prose_run = True
            else:
                items.append(('pada', t, pg))
    return items


def split_centre(t):
    """Two centred headings typeset on ONE line.

    The Mañjiṭṭhakavagga head shares its line with the division head, so it
    extracted as '1. Itthivimāna      4. Mañjiṭṭhakavagga'.  A run of 3+ spaces
    between two heading-shaped halves is the separator.
    """
    # THE EDITION'S OWN TYPESETTING SLIPS, named one line at a time.  37Abhi09
    # prints the pair "2. Paccayapaccanīya  2. Saṅkhyāvāra" 44 times, and on
    # printed p289 exactly ONE of them is set with a SINGLE space.  The rule
    # below wants three, so that line stayed whole and — starting with a
    # number — was classified as a numbered UNIT, which is what put the volume
    # one unit over.  Widening the rule to one space is not an option: it would
    # split ordinary unit text at its first internal number.  So the line is
    # NAMED, and `_is_double_head` sees the split through this same function.
    lit = SPEC[VOL].get('split_literals') or {}
    if lit:
        # keyed on the line with its internal whitespace COLLAPSED, so a
        # declaration does not have to reproduce the exact run of spaces
        # `pdftotext -layout` happens to emit
        _k = re.sub(r'\s+', ' ', t.strip())
        if _k in lit:
            return list(lit[_k])
    # `\d+(?:-\d+)?\.` — the RANGE form the rest of this file already accepts
    # (HEADNUM does).  38Abhi10 sets "27. Ganthaniyaduka    1-7. Vārasattaka",
    # and the narrower pattern left that pair joined.
    m = re.match(r'^(\d+(?:-\d+)?\.\s+\S[^\s].*?)\s{3,}'
                 r'(\d+(?:-\d+)?\.\s+\S.*)$', t)
    if m:
        return [m.group(1).strip(), m.group(2).strip()]
    # AN UNNUMBERED HEAD SHARING ITS LINE WITH A NUMBERED ONE.  36Abhi08
    # printed p9 opens the Pucchāvāra with two such lines —
    # "Pucchāvāra    1. Paccayānuloma" and "Ekamūlaka    1. Kusalapada" —
    # a division and its first subdivision, exactly the shape above but with
    # the outer name unnumbered, so the rule above could not see it and both
    # pairs rendered as ONE heading with a run of spaces in the middle.  The
    # volume's own front mātikā confirms the nesting (p2 sets "Pucchāvāra
    # 1. Paccayānuloma" and centres "Ekamūlaka" beneath it).
    # Gated per volume: the numbered form is what every shipped volume was
    # measured against, and widening it for all of them is a change no
    # regression here can justify.
    if SPEC[VOL].get('split_unnumbered'):
        m = re.match(r'^([A-ZĀĪŪṄÑṆṬḌḶ]\S*(?:\s+\S+){0,3}?)\s{3,}'
                     r'(\d+(?:-\d+)?\.\s+\S.*)$', t)
        if m:
            return [m.group(1).strip(), m.group(2).strip()]
    return [t]


def head_kind(txt):
    """sections `k`: 'book' (division / nipāta) > 'vagga' > 'sutta' (leaf)."""
    core = re.sub(r'^\d+(?:-\d+)?\.\s*', '', txt).strip()
    if DIVISION.search(core) or NIPATA.search(core):
        return 'book'
    if VAGGA.search(core):
        return 'vagga'
    return 'sutta'


# ---------------------------------------------------------------------------
# NIDDESA PATH.  Everything below is reached only from a book whose SPEC entry
# carries mode='niddesa'; the verse path above is untouched, which is what the
# 19Khu02 / 20Khu03 / 21Khu04 regression proves rather than assumes.
# ---------------------------------------------------------------------------

# A heading, tested BY CONTENT — indent alone cannot decide it here, because
# the gāthā quoted inside the commentary is set at indents 8-23 and overlaps
# the heading indents.  But content alone cannot decide it either: the prose
# opener "Pucchāmi taṁ Bhagavā brūhi metanti pucchāti tisso pucchā" ends in
# 'pucchā' and matches this pattern exactly.  So BOTH are required — content
# AND a display indent — and each of the two false positives found in 25Khu08
# is killed by the indent, each real heading by the content.
NIDHEAD = re.compile(r'^[A-ZĀĪŪṄÑṆṬḌḶ][^,]*'
                     r'(niddesa|niddeso|niddesā|vagga|vaggo|gāthā|pucchā|pāḷi)'
                     r'\d*\s*$')
# A colophon closes a section: "Kāmasuttaniddeso paṭhamo.", "Catuttho vaggo.",
# "Vatthugāthā niṭṭhitā.", "Aṭṭhakavaggamhi soḷasa suttaniddesā samattā.",
# "Mahāniddesapāḷi niṭṭhitā."  It is short, carries no comma, and names both a
# SECTION and either that section's completion or its ordinal position.
#
# !!! BOTH HALVES ARE NEEDED, AND THE REPORT IS WHAT SHOWED IT.  The ordinal /
# completion word alone pulled four gāthā PĀDAS out of the commentary and into
# the colophon stream — 24Khu07 p227/228 "Diṭṭhī hi tesampi tathā samattā." and
# p235 "Diṭṭhī hi sā tassa tathā samattā." — because 'samattā' is also ordinary
# Pāḷi.  Every word of them would still have been present and contiguous in the
# render, so the body harness would have reported 0 and the defect would have
# shipped: content in the wrong role, the failure this project keeps meeting.
# Requiring a section stem as well kills all four and loses no real colophon.
# The `--show` listing stays, because this discriminator is a judgement about
# the edition's wording and belongs under a human eye.
NIDORD = (r'niṭṭhit|samatt|paṭham|dutiy|tatiy|catuttha|catutth|pañcam|chaṭṭh|'
          r'sattam|aṭṭham|navam|dasam|ekādasam|dvādasam|terasam|cuddasam|'
          r'pannarasam|soḷasam|sattarasam|aṭṭhārasam|ekūnavīsatim|vīsatim')
NIDCOLO = re.compile(r'\b(?:' + NIDORD + r')', re.I)
# !!! THE UNINDENTED ARM NEEDED A STRONGER WORD TEST THAN `NIDCOLO` (2026-07-30h).
# `NIDCOLO` anchors only the START of a word, so `chaṭṭh` opens
# *Chaṭṭhakāmāvacara…* and `paṭham` opens *paṭhamasutte* — ordinary prose, taken
# out of the body and rendered as an uddāna block.  The edition closes a section
# in exactly TWO printed ways and both can be tested as whole words:
#
#   (1) it SAYS the section is finished — `niṭṭhitā`, `niṭṭhito`, `samattā`.
#   (2) it says WHERE THE SECTION STANDS, and the ordinal is then in the
#       NOMINATIVE — `Paṭhamo vaggo.`, `Khandhaniddeso nāma cuddasamo
#       paricchedo.`, `…ekādasamo.` — where prose declines it into a compound or
#       a locative: `paṭhamasutte`, `paṭhamagāthāya`, `Vīsatime vagge`,
#       `dutiyampi`.
#
# THE ENDING IS THE TEST, NOT THE POSITION.  A first draft required the ordinal
# to be the LAST word and released 03VinA03's seven `Paṭhamo vaggo.` /
# `Dutiyo vaggo.`, which are real colophons.  And `e` is NOT admitted: 33KhuA14's
# seven `Vīsatime vagge …` remarks turn on exactly that, and admitting it claims
# all seven — which is also why that volume needs no `colopat`.
# A FOOTNOTE DIGIT MAY SIT BETWEEN THE ORDINAL AND THE STOP: 16An02 closes three
# vaggas `Sītivaggo navamo2.`, `Ānisaṁsavaggo dasamo1.`, `Tikavaggo ekādasamo1.`
#
# MEASURED over every `heads_by_form` volume before applying
# (`_tika/colo_wholeword.py`): lines released to the body, and **0 newly
# claimed** — this rule only ever narrows.  A colophon it cannot reach is named
# in `colofix`, which refuses if the literal stops matching the page.
NIDDONE = re.compile(r'\b(?:niṭṭhit|samatt)[aāiīoōuūṁṃ]*\b', re.I)
_ORDINAL = (r'paṭham|dutiy|tatiy|catuttha|catutth|pañcam|chaṭṭh|sattam|aṭṭham|'
            r'navam|dasam|ekādasam|dvādasam|terasam|cuddasam|pannarasam|'
            r'soḷasam|sattarasam|aṭṭhārasam|ekūnavīsatim|vīsatim')
NIDSTANDS = re.compile(r'\b(?:' + _ORDINAL + r')(?:o|ā|aṁ|aṃ)\d{0,2}\b', re.I)
NIDSECT = re.compile(r'niddes|vagg|gāthā|pucchā|pāḷi', re.I)
# A display line that OPENS lowercase (or with an opening quote followed by
# one) continues the printed line above it.  See `kat_is_colo`.
COLO_LOWER = re.compile(r'^[“”"‘’]?[a-zāīūṁṅñṇṭḍḷ]')


def nid_is_colo(t):
    return (t.endswith('.') and ',' not in t and len(t.split()) <= 7
            and bool(NIDCOLO.search(t)) and bool(NIDSECT.search(t)))


def nid_items(pages, p0, p1, report):
    """('head'|'colo'|'homage'|'popen'|'pcont'|'vline', txt, pg) and
       ('lemma', n, txt, pg).

    Geometry, measured over both volumes rather than assumed:
      indent base+0..+2  prose CONTINUATION (the body column; 8,718 lines in
                         24Khu07 and 5,672 in 25Khu08 sit here)
      indent base+3..+7  prose PARAGRAPH OPENER, or the lemma's first line
                         when it carries a number
      indent base+8 and up
                         display: the lemma's remaining pādas, gāthā quoted
                         inside the commentary, headings and colophons
    `base` is the page's own leftmost indent, so a page whose margin shifts is
    read on its own terms.  A page with NO body column at all (25Khu08's last
    page sets only the closing gāthā and "Catuttho vaggo.") has base > 2 and is
    read as entirely display material — the same rule the verse path uses for a
    page with no verse number on it.
    """
    items = []
    for pg in range(p0, p1 + 1):
        lines = join_floating(page_lines(pages, pg))
        if not lines:
            continue
        base = min(i for i, _ in lines)
        display_only = base > 2
        for ind, t in lines:
            if HOMAGE.search(t):
                items.append(('homage', t, pg)); continue
            core = head_body(re.sub(r'^\d+(?:-\d+)?\.\s*', '', t)).strip()
            disp = display_only or ind >= base + 8
            if disp and NIDHEAD.match(core):
                items.append(('head', t, pg)); continue
            if disp and nid_is_colo(t):
                items.append(('colo', t, pg)); continue
            if disp:
                items.append(('vline', t, pg)); continue
            m = VERSE.match(t)
            if ind >= base + 3 and m:
                items.append(('lemma', int(m.group(1)), m.group(2), pg)); continue
            items.append(('popen' if ind >= base + 3 else 'pcont', t, pg))
    return items


def nid_build(pages, paras, title, p0, p1, o0, o1,
              verse, sections, uddana, incipit, report):
    """Map one niddesa book's printed stream onto its corpus paragraphs."""
    items = nid_items(pages, p0, p1, report)
    printed = [it for it in items if it[0] == 'lemma']
    ords = list(range(o0, o1))
    rec = {'book': title, 'mode': 'niddesa',
           'printed_lemmas': len(printed), 'corpus_paras': len(ords),
           'nmismatch': [], 'heads': [], 'colos': [],
           'prose_paras': 0, 'gatha_blocks': 0}
    report['books'].append(rec)
    if len(printed) != len(ords):
        # The whole method rests on this pairing, so a drift is fatal and named
        # rather than absorbed into a partial build.
        rec['FATAL'] = ('printed lemmas %d != corpus paragraphs %d'
                        % (len(printed), len(ords)))
        return
    for k, it in enumerate(printed):
        if it[1] != paras[ords[k]].get('n'):
            rec['nmismatch'].append({'pos': k, 'printed': it[1], 'pg': it[3],
                                     'ord': ords[k],
                                     'corpus_n': paras[ords[k]].get('n')})

    seq = iter(ords)
    cur = None            # ord of the lemma being assembled
    groups = []           # the lemma's own printed lines
    after = []            # printed paragraphs / gāthā blocks of the commentary
    pend_heads = []       # headings awaiting their lemma
    pend_centre = []      # colophons awaiting the previous lemma
    pend_before = []      # printed after a heading, before its lemma
    open_prose = False    # a prose paragraph is currently accumulating
    open_gatha = None     # a gāthā block is currently accumulating

    def flush():
        if cur is None:
            return
        e = {'groups': [g for g in groups if g]}
        if pend_before_of.get(cur):
            e['before'] = pend_before_of.pop(cur)
        if after:
            e['after'] = list(after)
        verse[str(cur)] = e

    pend_before_of = {}

    def add_prose(t, new_para):
        nonlocal open_prose, open_gatha
        open_gatha = None
        if new_para or not open_prose or not after or not isinstance(after[-1], str):
            after.append(t)
            rec['prose_paras'] += 1
            open_prose = True
            return
        # LINE-END HYPHENATION, joined on the hyphen and nothing else — every
        # wider rule also swallows ordinary wraps and fabricates words.
        after[-1] = hyjoin(after[-1], t)

    for it in items:
        kind = it[0]
        if kind == 'homage':
            incipit[str(o0)] = it[1].strip()
            continue
        # The title page's own stack — the collection name above the book name.
        # Both are drawn by pipeline/build_booktitles.py into booktitle/<VOL>,
        # so neither belongs in the body stream.  The book's own name matches
        # NIDHEAD through the 'pāḷi' stem and so arrives as a heading, but
        # "Khuddakanikāya" matches nothing and would otherwise fall through to
        # the first lemma's `before` as a stray one-word paragraph.
        if kind != 'lemma' and it[1].strip() in (title, 'Khuddakanikāya'):
            continue
        if kind == 'head':
            t = it[1].strip()
            pend_heads.append({'l': t, 'k': head_kind(t)})
            rec['heads'].append({'pg': it[2], 'l': t})
            open_prose = False; open_gatha = None
            continue
        if kind == 'colo':
            pend_centre.append({'label': None, 'lines': [it[1].strip()],
                                'app': []})
            rec['colos'].append({'pg': it[2], 'l': it[1].strip()})
            open_prose = False; open_gatha = None
            continue
        if kind == 'lemma':
            flush()
            prev = cur
            cur = next(seq)
            groups, after = [[it[2]]], []
            open_prose = False; open_gatha = None
            if pend_centre:
                # A colophon closes the PREVIOUS section, so it renders after
                # the previous paragraph — never above the new heading.  Anchor
                # to that paragraph explicitly rather than to `cur - 1`: a
                # hidden ordinal between two units would otherwise swallow the
                # block, since a side-map anchored to a hidden paragraph never
                # renders.  Neither Niddesa volume has one between units, so
                # this changes nothing here; it is corrected because 26Khu09
                # does and the two paths must not differ on it.
                uddana.setdefault(str(prev if prev is not None else cur),
                                  []).extend(pend_centre)
                pend_centre = []
            if pend_heads:
                sections[str(cur)] = pend_heads
                pend_heads = []
            if pend_before:
                pend_before_of[cur] = list(pend_before)
                pend_before = []
            continue
        # popen / pcont / vline
        if cur is None or pend_heads:
            # printed after a heading and before its lemma: the section's own
            # opener ("Atha Guhaṭṭhakasuttaniddesaṁ vakkhati–"), which belongs
            # to the heading's paragraph and not to the previous one
            pend_before.append(it[1])
            continue
        if kind == 'vline':
            if not after and not open_prose:
                groups[0].append(it[1])       # the lemma's remaining pādas
                continue
            if open_gatha is not None:
                _add_line(open_gatha['gatha'], it[1])
            else:
                open_gatha = {'gatha': [it[1]]}
                after.append(open_gatha)
                rec['gatha_blocks'] += 1
            open_prose = False
            continue
        add_prose(it[1], kind == 'popen')

    flush()
    if pend_centre:
        uddana.setdefault(str(cur), []).extend(pend_centre)
    if pend_heads:
        report['unmapped'].append({'book': title, 'trailing_heads': pend_heads})
    if pend_before:
        report['unmapped'].append({'book': title, 'trailing_before': pend_before})


# ---------------------------------------------------------------------------
# KATHĀ PATH — prose whose numbered unit has no verse lemma, and whose body
# column is not always the page's leftmost indent.  Reached only from a book
# with mode='katha'; the verse and niddesa paths above are untouched.
# ---------------------------------------------------------------------------

# A colophon here names a section and its completion or position, as in the
# niddesa path, but the sections are kathās, vāras and bhāṇavāras rather than
# suttaniddesas — so the section-word list differs and is kept separate rather
# than widened, which would loosen the niddesa test as a side effect.
KATSECT = re.compile(r'niddes|vagg|kathā|vāra|vāro|gāthā|pāḷi|mātikā|chakka|'
                     r'catukka|bhāṇavār|bhūmi|paṭṭhān|pakaraṇ|vibhaṅg|sampāt',
                     re.I)


def katsect():
    """KATSECT plus this volume's own section words, if it declares any.

    Kept per-volume: 28Khu11's colophons close a `pañha`, and adding that to
    the shared pattern would move 26Khu09 and 27Khu10 as a side effect.  The
    9-volume regression is what proves it does not.
    """
    extra = SPEC[VOL].get('colo_sect')
    return re.compile(KATSECT.pattern + '|' + extra, re.I) if extra else KATSECT


# --- THE LINE-END HYPHEN: three joins, not one -------------------------------
#
# A printed line ending in `-` was joined `prev[:-1] + t` at SIX separate sites,
# i.e. the hyphen was assumed to be a soft word break EVERYWHERE.  Measured over
# all 118 volumes (`_hyphen/`), that is true of a fifth of them:
#
#   PEYYALA  3,906   the line ends with a STANDALONE `-pa-` / `-pe-` / `-la-`
#   VOWEL    7,557   the next line opens with a VOWEL
#   OTHER    2,614   everything else
#
# and the EDITION ITSELF decides which is which.  Pass 1 built a corpus-wide
# index of every hyphenated pair and every un-hyphenated word printed INLINE —
# taken only from line interiors, so no break can vote on itself — and pass 2
# looked up both candidates for every break:
#
#   VOWEL   2,545 KEEP :     2 JOIN     the hyphen is the edition's own
#   OTHER      65 KEEP :   716 JOIN     a genuine soft word break
#
# So a vowel junction keeps its hyphen and takes NO space (`pathavī-ādīsu`,
# `catu-iriyāpatha`, `sakadāgāmi-anāgāmi`), and everything else joins as before.
# OTHER's 65 KEEP are the edition's grammatical citation forms — `ta-kāro`,
# `taṁ-saddassa`, `na-kāro` — plus apparatus sigla; they are left joining,
# which is what 92% of the decided evidence says.
#
# THE PEYYĀLA MARK IS NOT A JUNCTION AT ALL.  `-pa-` is a COMPLETE TOKEN with
# its own closing hyphen, so the join keeps the hyphen AND adds a space.  The
# word lookup cannot decide it and must not be asked to: `pa` + `taṁ` is the
# real word `pataṁ` and `pa` + `hoti` is `pahoti`, so the evidence votes JOIN
# on 146 breaks where the truth is a printed `-pa-` followed by a new word.
# Before this, 2,647 peyyāla marks in 46 side-map files were rendering as
# `-paavikkhepo` where the edition prints `-pa- avikkhepo`.
#
# THE BODY GATE CANNOT SEE ANY OF THIS — it strips line-end hyphens on both
# sides, so the parser and its own checker shared the blind spot, exactly as
# they did for the graphic footnote rule (2026-07-26ak).
_PEYYALA_END = re.compile(r'(^|\s)-(?:pa|pe|la)-$')
_FIRSTLET = re.compile(r'[A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṆṇṬṭḌḍḶḷ]')
_VOWELS = set('aāiīuūeoAĀĪĪIUŪEO') | set('AĀIĪUŪEO')


def hyjoin(prev, t):
    """Join a printed line to the one below it, deciding its line-end hyphen."""
    if not prev.endswith('-'):
        return prev + ' ' + t
    if _PEYYALA_END.search(prev):
        return prev + ' ' + t          # a complete token: keep it and space off
    m = _FIRSTLET.search(t)
    if m and m.group(0) in _VOWELS:
        return prev + t                # the edition's own hyphen at a junction
    return prev[:-1] + t               # a soft word break


def kat_is_colo(t, ind=None, body=0):
    """Is this display line a section-closing colophon?

    Two printed forms, and they need different evidence.

    (1) It names a section AND says either that it is finished or where it
        stands ("Sutamayañāṇaniddeso paṭhamo.", "Mātikā niṭṭhitā.").  The words
        are decisive on their own, so no indent is required — 26Khu09 sets
        these at indent 13.

    (2) It says NEITHER.  The Netti closes its vāras with the bare name in the
        nominative — "Saṅgahavāro.", "Uddesavāro.", "Niddesavāro." — and its
        hārasampātas with "Niyutto …".  `kat_is_head` matches those perfectly,
        so without this they would OPEN their sections instead of closing them;
        what separates them from the headings they echo ("1. Saṅgahavāra") is
        that A HEADING IS A TITLE AND CARRIES NO TERMINAL STOP.  But that test
        alone is far too weak, because a section word can fall INSIDE an
        ordinary word: `vāra` inside "nivāraṇaṁ", `bhūmi` inside "Apāyabhūmiṁ",
        `gāthā` inside "uddānagāthā".  It took six quoted verse pādas out of
        27Khu10's body — "Sotānaṁ kiṁ nivāraṇaṁ.", "Apāyabhūmiṁ asubhena
        kammunā.", "Imā dasa tesaṁ uddānagāthā." and three more.  So this form
        must also be CENTRED: measured, the real ones sit at indent 22-35 and
        every false one at 9-17.  Form (1) is deliberately left un-guarded, or
        26Khu09's colophons at 13 would all be lost.
    """
    # !!! `colofix` WAS UNREACHABLE ON EVERY `heads_by_form` VOLUME — the
    # branch below RETURNS, so a literal named in `colofix` was never consulted
    # for 01Vin01-05Vin05, 31Abhi03, 32Abhi04 or any other volume that
    # classifies by form.  Declaring one had no effect and reported no error.
    # Found 2026-07-26ai.  The named literals are checked FIRST, which is what
    # "named" is supposed to mean.
    if t in SPEC[VOL].get('coloskip', ()):
        # !!! THE UNINDENTED FORM-(1) FALLBACK TAKES A LINE OF ORDINARY PROSE
        # WHEN BOTH OF ITS WORD TESTS LAND INSIDE ORDINARY WORDS.  `NIDCOLO`
        # and `NIDSECT` are substring searches, and 19AnT02 p170 sets the body
        # line
        #     `samudāyo samāsattho. Chaṭṭhakāmāvacaradevaggahaṇaṁ
        #      paccāsattinayena.`
        # which satisfies BOTH — `chaṭṭh` opens "Chaṭṭhakāmāvacara…" and `vagg`
        # sits inside "de-VAGG-ahaṇaṁ" — while carrying a terminal stop, no
        # comma and four words.  It was pulled out of the body and rendered as
        # an uddāna block at the foot of the sutta: present, contiguous in the
        # corpus, and in the WRONG ROLE.  Found by the body gate's
        # MISSING-CHUNK arm, 2026-07-29.
        # Declared per volume rather than tightened in NIDCOLO/NIDSECT, because
        # a word-boundary anchor would kill the real colophons those regexes
        # exist for — `niddes` in "Sutamayañāṇaniddeso" is a substring too.
        COLOSKIP_SEEN.add(t)
        return False
    if t in SPEC[VOL].get('colofix', ()):
        return True
    if SPEC[VOL].get('heads_by_form'):
        # the other half of the same rule: a display line WITH a terminal stop.
        # THE INDENT FLOOR IS A PROXY FOR CENTRED, AND IT FAILS ON A LONG NAME —
        # a centred line's indent falls as its name grows.  31Abhi03 sets
        # "Saṅgahitena sampayuttavippayuttapadaniddeso ekādasamo." at indent 7
        # where the other thirteen padaniddesa colophons sit at 20 and above,
        # and it was read as ordinary prose: present, contiguous, in the wrong
        # role, and 0/0/0/0 from the body gate.  So where the WORDS are decisive
        # — the line both NAMES a section and says it is finished or where it
        # stands, which is form (1) above and what `NIDCOLO`/`NIDSECT` already
        # test — no indent is required.
        # !!! ...AND A LINE THAT OPENS WITH A UNIT NUMBER IS NOT A COLOPHON BY
        # THE GENERIC FORM TEST.  The HEADING branch of `kat_items` has always
        # said so — "a NUMBERED line is decided by the numbered rule below, not
        # by the generic form test" — but the COLOPHON branch runs FIRST and
        # carried no such guard, so a numbered unit that happens to be short,
        # unpunctuated within and closed by a stop was claimed as a colophon
        # before the numbered rule could see it.  13Sam02 p200 and p202 print
        # the peyyāla instruction `251-274. (Dutiyavagge viya catuvīsati
        # suttāni pūretabbāni.).` as a UNIT at indent 4 — six words, terminal
        # stop, no comma — and both were taken, so the Khandhavagga paired 359
        # printed against 361 corpus paragraphs and REFUSED TO BUILD.  A wrong
        # role that the 1:1 count check caught only because it took an ordinal
        # with it.
        # `colofix` still wins: it is consulted above this, which is what
        # "named" is supposed to mean.
        # MEASURED OLD-vs-NEW OVER ALL 36 VOLUMES IN SPEC BEFORE APPLYING
        # (`_fnprobe/colonumdiff.py`, wrapping this function — it has exactly
        # ONE call site, so the wrapper IS the branch guard): THIRTY-FIVE ARE
        # BYTE-IDENTICAL on all five side-maps with printed-unit and colophon
        # counts unmoved, and the only volume that moves is 13Sam02.
        # !!! ...AND A LINE THAT BEGINS WITH A LOWERCASE LETTER IS THE
        # CONTINUATION OF A WRAPPED BODY LINE, NEVER A COLOPHON.  The
        # unindented arm below rests on `NIDCOLO` and `NIDSECT`, and BOTH are
        # substring searches: `chaṭṭh` opens "Chaṭṭhakāmāvacara…" and `vagg`
        # sits inside "de-VAGG-ahaṇaṁ", so 19AnT02 p170's body line
        # `samudāyo samāsattho. Chaṭṭhakāmāvacaradevaggahaṇaṁ
        # paccāsattinayena.` satisfied both and was rendered as an uddāna block
        # at the foot of the sutta.  A colophon NAMES a section and is always
        # capitalised, so this guard cannot reach a real one; it is a fact about
        # the edition's form, not a judgement.  MEASURED over all 94
        # `heads_by_form` volumes before applying (`_tika/colofallback2.py`):
        # 46 lines change role, every one of them lowercase-initial body prose,
        # and 39 capital-initial hits are left for a human eye — listed in
        # `claude/false_colophons_by_substring.md`.
        # The INDENTED arm is deliberately left alone: it rests on geometry,
        # not on these two regexes.
        return (t.endswith('.') and ',' not in t and len(t.split()) <= 6
                and ind is not None
                and not VERSE.match(t)
                and (ind >= body + 8
                     or (not COLO_LOWER.match(t)
                         and (bool(NIDDONE.search(t)) or bool(NIDSTANDS.search(t)))
                         and bool(NIDSECT.search(t)))))
    if t in SPEC[VOL].get('colofix', ()):
        return True
    # A printed FORM this book uses that names no section and carries no
    # ordinal: "Imasmiṁ vagge soḷasa pañhā." closes fifteen of 28Khu11's
    # twenty-two vaggas with the count of its pañhas.  Thirteen are set at
    # indent 20+ and the centred test already reached them; two (p78, p327)
    # sit at 18 and were falling through to the body as ordinary prose —
    # present, contiguous, and in the wrong role, which the body gate reports
    # as 0.  Declared per volume as a pattern rather than as fifteen literals,
    # since only the numeral differs.
    pat = SPEC[VOL].get('colopat')
    if pat and re.match(pat, t):
        return True
    if not (t.endswith('.') and ',' not in t and bool(katsect().search(t))):
        return False
    if len(t.split()) <= 7 and bool(NIDCOLO.search(t)):
        return True
    if len(t.split()) > 4:
        return False
    # (1b) The ordinal by its ENDING rather than by a word list.  NIDCOLO names
    # the ordinals up to twenty, and 26Khu09 runs to seventy-three: its
    # "Sallekhaṭṭhañāṇaniddeso sattatiṁsatimo.", "Āsayānusayañāṇaniddeso
    # navasaṭṭhimo." and thirty more were not reached by any of those words.
    # Every Pāḷi ordinal above the fourth ends in -ma, so the nominative ends
    # -mo / -mā / -maṁ; none of the six false positives this test had to reject
    # does ("nivāraṇaṁ", "kammunā", "padāni", "uddānagāthā").
    if re.search(r'm[oāa]ṁ?\.$', t):
        return True
    return ind is not None and ind >= body + 20


def kat_is_head(core, printed=True):
    """A heading, tested more loosely than HEADTXT — and here is why.

    HEADTXT is `^[A-Z…][^,]*(stem)…$`: the capital is consumed first, so the
    stem has to be a PROPER suffix of the line.  Every niddesa heading is
    "<Name>suttaniddesa" and satisfies that, but this volume sets headings that
    ARE the bare stem — "1. Mātikā" and "2. Niddesa" head the two halves of the
    Suññakathā — and for those the stem would have to match "ātikā" / "iddesa".
    Both fell through to the numbered-unit test and were read as body text.
    So: start with a capital, carry no comma, and END at the stem, matched
    case-insensitively.  Kept local to this path rather than widened in
    HEADTXT, which five shipped volumes depend on.
    """
    # !!! A LINE THAT ENDS IN A HYPHEN IS THE FIRST HALF OF A WRAPPED LINE,
    # NEVER A TITLE.  01VinA01's Ganthārambhakathā sets its opening gāthā as
    # centred pādas that wrap — `Namo avijjādikilesajāla-` / `Guṇehi yo
    # sīlasamādhipaññā-` — and every form test passes them: a capital, no
    # comma, short, no terminal stop.  They surfaced only when that volume's
    # 78 unnumbered opening pages entered the corpus (2026-07-27s); no volume
    # built before then had such an opening to test the rule against.
    # MEASURED over every shipped side-map that holds headings: exactly TWO
    # entries anywhere end in a hyphen, both of them these, in this volume.
    # So the rule cannot move anything already built.
    if core.rstrip().endswith('-'):
        return False
    # !!! ...AND A LINE THAT ENDS IN A QUESTION MARK IS A QUESTION, NEVER A
    # TITLE.  The edition quotes catechetical prose at a display indent — the
    # Puggalapaññatti's `Katamo ca puggalo dhammappamāṇo dhammappasanno?`
    # inside 19AnT02 p295's block quotation, the Vibhaṅga's `Tattha katamaṁ
    # kāmesumicchācārā veramaṇī sikkhāpadaṁ?` twice in 02ViT02 — and every form
    # test passes them: a capital, no comma, six words or fewer, and no
    # TERMINAL STOP, because the mark is a question mark.  MEASURED over every
    # shipped side-map that holds headings: exactly THREE entries anywhere end
    # in `?`, and all three are these.  So the rule takes nothing else.
    if core.rstrip().endswith('?'):
        return False
    if ',' in core or not re.match(r'^[A-ZĀĪŪṄÑṆṬḌḶ]', core):
        return False
    # BY FORM, not by vocabulary — see SPEC['29Abhi01'].  A volume that sets
    # every display line as a short comma-free title needs no stem list, and
    # enumerating one would silently drop the headings the list missed.
    # `printed=False` when the caller is testing a CORPUS PARAGRAPH rather than
    # a centred printed line.  The form test rests entirely on the line being
    # centred — without that evidence it takes ordinary short paragraphs: it
    # claimed 36 of 29Abhi01's Dukamātikā paragraphs ("101. Vijjābhāgino
    # dhammā. (1303) Avijjābhāgino dhammā. (1304)") as leaked headings, which
    # would have hidden them from the render and broken the 1:1 pairing.
    if SPEC[VOL].get('heads_by_form') and printed:
        # !!! A STANZA NUMBER PRINTED IN THE RIGHT MARGIN HIDES THE PĀDA'S OWN
        # STOP.  34KhuA15 sets the fourth pāda of a long refrain as
        # `Samayo Mahāvīra aṅgīrasānaṁ.             (9)` — the terminal full
        # stop is there, but the margin number follows it, so `endswith('.')`
        # is False and the form test claims the line as a title.  It did so
        # 57 times in that volume, more than half of its 108 headings.
        # `margin_verse_numbers` strips a trailing `(N)` before the stop test.
        # Per-volume, so nothing shipped can move; measured over all 118
        # printed volumes, the shape occurs in 34KhuA15 (65 lines) and NOWHERE
        # ELSE among the volumes of this batch.
        c = (re.sub(r'\s*\(\d+\)\s*$', '', core)
             if SPEC[VOL].get('margin_verse_numbers') else core)
        return len(c.split()) <= 6 and not c.endswith('.')
    return bool(re.search(r'(?:' + SPEC[VOL]['stems'] + r')\d*\s*'
                          r'(\([\d\s.–-]+\))?$', core, re.I))


def kat_book_body(pages, p0, p1):
    """The BOOK's body column, measured once over the pages that establish one.

    Measuring it per page is not safe.  A page can be almost entirely quoted
    gāthā — 27Khu10 p133 sets one numbered unit and eleven verse lines and has
    no line at the left margin at all — and the per-page measurement then
    returns the VERSE indent as the body column, after which the page's own
    numbered unit sits to the LEFT of it and is read as prose continuation.
    That lost exactly one of the Netti's 151 units, and the pairing check is
    what refused to build on it.
    """
    from collections import Counter
    c = Counter()
    for pg in range(p0, p1 + 1):
        lines = page_lines(pages, pg)
        oth = [i for i, t in lines if i < 20 and not VERSE.match(t)]
        if len(oth) < 6:
            continue                      # too little evidence to vote
        seen, twice = set(), set()
        for i in oth:
            (twice if i in seen else seen).add(i)
        if twice:
            c[min(twice)] += 1
    return c.most_common(1)[0][0] if c else 0


def _kat_cols(lines, body0):
    """(number column, body column, is-hanging-list) for one page.

    The book's column is used unless the page is a HANGING LIST, where the
    number is set to the LEFT of its own continuation (26Khu09's mātikās).  A
    page that merely happens to carry no left-margin line — an all-verse page —
    is NOT one: what tells them apart is that a list has MANY numbered lines
    and an all-verse page has one or two.
    """
    num = sorted(i for i, t in lines if i < 20 and VERSE.match(t))
    oth = [i for i, t in lines if i < 20 and not VERSE.match(t)]
    seen, twice = set(), set()
    for i in oth:
        (twice if i in seen else seen).add(i)
    pbody = min(twice) if twice else (min(oth) if oth else (num[0] if num else 0))
    numc = num[0] if num else None
    hanging = numc is not None and numc < pbody and len(num) >= 3
    body = pbody if hanging else (body0 if pbody > body0 + 2 else pbody)
    return numc, body, hanging


def it_text(t):
    """A numbered line's text, without its number."""
    m = VERSE.match(t)
    return m.group(2).strip() if m else t.strip()


def _is_double_head(t):
    # `\d+(?:-\d+)*\.` — a LIST of numbers, not just a range.  The edition
    # heads three sikkhāpadas printed together "8-9-10. Aṭṭhama navama
    # dasamasikkhāpada" (02Vin02 p472), and with the narrower `(?:-\d+)?` the
    # strip did not match at all, so the core still began with a digit and
    # `kat_is_head` refused it for want of a capital — the pair stayed whole and
    # took a unit's ordinal.  Widened HERE and in `_starts_double_head` only:
    # both are reached solely from the kathā path, so no verse-mode volume can
    # see it, and the 55-map regression proves that.
    parts = split_centre(t.strip())
    return len(parts) > 1 and all(
        kat_is_head(head_body(re.sub(r'^\d+(?:-\d+)*\.\s*', '', x)).strip())
        for x in parts)


def _starts_double_head(t):
    """A corpus paragraph that BEGINS with two centred headings and RUNS ON.

    The extraction sometimes captures a heading pair together with the material
    printed under it as ONE paragraph — 38Abhi10 ord640
    ("1. Paccayānuloma  1. Vibhaṅgavāra (Pañhāvāre hetupaccayepi…)") and
    ord1170, and 40Abhi12 ord190.  A census over the whole Paṭṭhāna finds
    exactly those three and none elsewhere in the Abhidhamma.  Left visible
    each takes a unit's ordinal AND carries the heading's number, so the
    pairing desyncs from there to the end of the book.

    Hiding is safe here in a way it is not for an ordinary paragraph: the kathā
    path draws both the headings and the prose from the PRINTED stream, so
    nothing leaves the body gate's sight — which is what that gate then proves.

    `kat_is_head(..., printed=True)` is right for the two halves even though
    the caller is a corpus paragraph: the 3+ space run BETWEEN them is itself
    the centring evidence that the `printed` flag normally stands in for.
    """
    m = re.match(r'^(\d+(?:-\d+)*\.\s+\S+)\s{3,}(\d+(?:-\d+)*\.\s+\S+)\s+\S', t)
    if not m:
        return False
    return all(kat_is_head(head_body(re.sub(r'^\d+(?:-\d+)*\.\s*', '', x)).strip())
               for x in (m.group(1), m.group(2)))


def kat_items(pages, p0, p1):
    """('homage'|'head'|'colo'|'udd'|'vline'|'popen'|'pcont', txt, pg)
       and ('unit', n, txt, pg)."""
    items = []
    body0 = kat_book_body(pages, p0, p1)
    # AN UDDĀNA IS ONE BLOCK EVEN WHEN IT CHANGES COLUMN AT A PAGE BREAK, so
    # this state is carried ACROSS pages — see the override at the foot of the
    # page loop.  It is the only thing in this function that is.
    in_udd = False
    # !!! A NARRATIVE HOMAGE IS NOT THE BOOK'S OWN, and treating it as one both
    # DELETED IT FROM THE BODY and OVERWROTE the title page's incipit.  Every
    # line matching `HOMAGE` was classified 'homage', and the consumer writes
    # each to the SAME key — the book's first visible ordinal — so the LAST won,
    # while the branch's `continue` meant the line never reached the body at all.
    # In a book that QUOTES the homage in its narrative that is text loss plus a
    # wrong incipit, and it reached TWO volumes already called done:
    #   10Ma02  incipit[0] held the narrative comma-form from p346, and
    #           Brahmāyu's threefold homage was missing from verse[387]
    #   12Sam01 uddana[186] held ONE of the Dhanañjānī brahmin's THREE lines
    # plus 15An01 (incipit[323] held the Ārāmadaṇḍa quotation) and 16An02.
    # THE DISCRIMINATOR IS POSITION AND NEEDS NO VOCABULARY: a book's own
    # homage stands on its TITLE PAGE, BEFORE that book's first numbered unit;
    # every narrative one is quoted after it.  MEASURED OLD-vs-NEW OVER ALL 39
    # SPEC VOLUMES (`_fnprobe/homagepos.py`): THIRTY-FIVE ARE BYTE-IDENTICAL and
    # the only four that move are the four named above, each a correction.
    seen_unit = False          # has this BOOK printed a numbered unit yet?
    for pg in range(p0, p1 + 1):
        lines = join_floating(page_lines(pages, pg))
        if not lines:
            continue
        numcol, body, hanging = _kat_cols(lines, body0)
        # A DISPLAY LINE THAT WRAPS IS STILL ONE LINE.  35Abhi07 p83 sets two
        # of its catechetical statements too long for the measure —
        #     Na somanassaṁ na somanassindriyaṁ. . Na somanassindriyaṁ na
        #     somanassaṁ.
        # — and the remainder, alone on its line at the display indent, is one
        # word ending in a full stop, which is a COLOPHON by every test this
        # file has. Two of them rendered as centred closing lines in the middle
        # of a vāra. The body gate reads 0/0/0/0 on both, because every word is
        # present and in order; the `--show` listing is what showed it.
        #
        # THE SIGNAL IS THE CAPITAL. In this edition every heading, colophon,
        # homage, title and pāda opens with one, and a wrapped remainder does
        # not. MEASURED over all twelve Abhidhamma volumes: 10,789 display
        # lines, and a display line that begins lowercase directly under
        # another at the SAME indent occurs EXACTLY TWICE — these two. So the
        # rule cannot be reaching anything else here, and 33Abhi05 and
        # 34Abhi06 are confirmed unaffected rather than assumed to be.
        # Gated per volume all the same; the 55-map regression is what proves
        # it inert on the Khuddaka.
        # ...AND THE INDENT IS NOT PART OF THE SIGNAL — the CAPITAL is.  This
        # first required the wrapped line to sit at the SAME indent, which is
        # true of 35Abhi07's two but false of every other instance, because a
        # CENTRED line's remainder is centred too and so lands somewhere else
        # entirely: 01Vin01 p174 sets "Ime kho panāyasmanto terasa
        # saṁghādisesā" at 15 and "dhammā uddesaṁ āgacchanti." at 21.
        # RE-MEASURED without it over the twelve Abhidhamma volumes and the
        # five Vinaya ones: still only SEVEN instances in all, and every one is
        # a genuine wrap — 35Abhi07 x2, 01Vin01 x3, and one apiece in 33Abhi05
        # (p227) and 36Abhi08 (p160), where a parenthetical editorial note was
        # rendering as two paragraphs.  Those two are shipped volumes and the
        # flag is now set for them as well; their three gates were re-run.
        if SPEC[VOL].get('wrap_display'):
            _m = []
            for _i, _t in lines:
                # ...AND THE LINE ABOVE NEED NOT BE A DISPLAY LINE EITHER.
                # 02Vin02 p286 sets the same recitation formula this rule was
                # written for at the BODY column and centres only its
                # remainder.  What is being recognised is a line that CANNOT
                # begin anything — the capital says so — so where the line
                # above sits is not part of the evidence.
                if (_m and _i >= body + 8
                        and re.match(r'^[a-zāīūṁṅñṇṭḍḷ]', _t)):
                    _m[-1] = (_m[-1][0], _m[-1][1] + ' ' + _t)
                else:
                    _m.append((_i, _t))
            lines = _m
        # A page with no numbered line and nothing at the body column is all
        # display — the closing Uddānagāthā page is set that way.
        disp_only = numcol is None and not [i for i, t in lines if i <= body + 2]
        # A PAGE READ AS ENTIRELY DISPLAY STILL HAS TWO BANDS, and everything
        # in the upper one is CENTRED PROSE, not a pāda.  27Khu10 sets nine
        # such pages, and on them the edition frames each quoted gāthā with its
        # own prose — "Tattha katamo assādo–" above it and "Ayaṁ assādo."
        # below, both centred — while the pādas sit in a left-aligned block.
        # Because `run` is forced true on such a page, all of it was arriving
        # as ONE gāthā: printed p6 gave a single 24-line italic block holding
        # six quotations and their twelve frame lines.  The body gate reports
        # 0/0/0/0 on it — every word is present, contiguous and in order.
        #
        # MEASURED, NOT CHOSEN: over those nine pages the indents fall in two
        # clusters, 6-15 (196 pāda lines) and 19-35 (34 frame lines), with
        # NOTHING at 16, 17 or 18.  So the split is the page's own largest gap,
        # and the rule refuses to fire unless there really is one.
        centre_from = None
        if disp_only and SPEC[VOL].get('display_centre'):
            _inds = sorted({i for i, _t in lines})
            _gap = max(zip([b - a for a, b in zip(_inds, _inds[1:])],
                           _inds[1:]), default=(0, None))
            if _gap[0] >= 4 and _gap[1] is not None and _gap[1] >= 18:
                centre_from = _gap[1]
        kinds = []
        # A PĀDA THAT COMPLETES A SENTENCE THE LINE ABOVE IT BEGAN IS NOT A
        # COLOPHON.  Under `heads_by_form` a colophon is decided by form alone —
        # ends in a stop, no comma, six words or fewer — and in a book that
        # prints gāthā that is also the shape of every SECOND pāda of a couplet:
        #
        #     Na dukkaraṁ viriyamathopi maccuno,      <- a candidate
        #     Bhāyāvuso vippaṭisāri sammā.            <- read as a COLOPHON
        #
        # so 01Vin01's uddāna were being cut in half, eighteen of them, and the
        # body gate reads 0/0/0/0 on every one because the words are all there.
        # THE DISCRIMINATOR IS THE EDITION'S OWN PUNCTUATION: the line above
        # ends in a COMMA, so it is mid-sentence, and a closing line never
        # follows one.  MEASURED over all seventeen volumes that have a SPEC:
        # it reclassifies 75 lines and NOT ONE of them carries a closing word
        # (`niṭṭhita`, `samatta`, an ordinal) — i.e. it takes no real colophon
        # anywhere.  Gated per volume all the same.
        # (A rule keyed on "shares its indent with a neighbour" was tried first
        # and REJECTED on measurement: it loses real colophons in 33Abhi05,
        # 31Abhi03, 32Abhi04, 35Abhi07 and 40Abhi12, which print two of them
        # adjacently at one indent.)
        _runon = SPEC[VOL].get('pada_runon')
        # ...AND THE TEST IS THE WHOLE RUN, not only the line above.  01Vin01's
        # couplets alternate comma / stop, so looking one line back reaches
        # them; 03Vin03 prints long gāthā in which EVERY pāda ends in a stop
        # and only some carry a comma at the caesura, and there the line above
        # says nothing.  What the page says is that they are ONE BLOCK: a
        # maximal run of display lines at a single indent.  If any line in that
        # run carries a comma, the run is verse and none of it is a closing
        # line.
        #
        # THE ONE EXCEPTION IS THE EDITION'S OWN STRICT COLOPHON FORM — a line
        # that both NAMES a section and says it is FINISHED.  31Abhi03 p94 sets
        # "Asaṅgahitena sampayuttavippayuttapadaniddeso terasamo." at the SAME
        # indent as the six gāthā lines above it, and without this it would be
        # swallowed with them.  MEASURED over every kathā book with a SPEC: the
        # run test reclassifies 476 lines and the strict form rescues exactly
        # that one.
        _runidx = set()
        if _runon:
            _i2 = 0
            while _i2 < len(lines):
                if lines[_i2][0] < body + 8:
                    _i2 += 1
                    continue
                _j2 = _i2 + 1
                while _j2 < len(lines) and lines[_j2][0] == lines[_i2][0]:
                    _j2 += 1
                if _j2 - _i2 >= 2 and any(',' in lines[_k][1]
                                          for _k in range(_i2, _j2)):
                    _runidx.update(range(_i2, _j2))
                _i2 = _j2
        for _li, (ind, t) in enumerate(lines):
            m = VERSE.match(t)
            disp = disp_only or ind >= body + 8
            # A HEADING MAY CARRY ITS ABSOLUTE NUMBER IN PARENTHESES FIRST.
            # 32Abhi04 heads every one of its 280 kathās "(10) 1.
            # Parūpahārakathā" — the kathā's number in the whole book, then its
            # number within its vagga — and "(106-108) 1-3. Tissopi-anusayakathā"
            # where three run together.  `kat_is_head` requires the core to open
            # with a CAPITAL, so without this every one of them fell through.
            # The label keeps both numbers exactly as printed; only the TEST
            # needs the name.
            _c = t
            if SPEC[VOL].get('head_paren'):
                _c = re.sub(r'^\(\d+(?:-\d+)?\)\s*', '', _c)
            core = head_body(re.sub(r'^\d+(?:-\d+)?\.\s*', '', _c)).strip()
            if HOMAGE.search(t) and not seen_unit:
                kinds.append('homage')
            elif disp and UDDLBL.match(t):
                kinds.append('udd')
            # COLOPHON BEFORE HEADING: the Netti closes a vāra with the bare
            # name ("Saṅgahavāro.") which the heading test also matches, and
            # only the terminal stop tells them apart.
            # ...and the DISPLAY GATE IS DROPPED where the volume classifies by
            # form, because `kat_is_colo` is given the indent and decides for
            # itself: it still requires `body + 8` unless the line both NAMES a
            # section and says it is finished, which is form (1) and needs no
            # indent.  Without this the function's own relaxation is unreachable
            # — the caller had already refused the line.  Proved inert on
            # 29Abhi01, 30Abhi02 and 36-40, all byte-identical.
            elif ((disp or SPEC[VOL].get('heads_by_form'))
                  # (the line above need not be a display line: a display
                  # quotation's FIRST line HANGS LEFT of its own pādas, below
                  # the gate, which is how 02Vin02 p91's "* “Adhicetaso
                  # appamajjato," sits at indent 7 with its gāthā at 9)
                  and not (_runon
                           and (_li in _runidx
                                # ...AND THE COMMA MUST BE A NEIGHBOUR'S, NOT
                                # ANY LINE'S.  A couplet's two pādas sit at the
                                # SAME indent (09Ma01 p239 sets all fourteen at
                                # 18), so a comma on a line at a completely
                                # different indent says nothing about this one.
                                # Without the check 31Abhi03 p110 loses a REAL
                                # colophon: `Ekakaṁ.` at indent 38 closes the
                                # Ekaka-uddesa — a rule and `2. Duka-uddesa`
                                # follow it — but the line above is the list
                                # item `54. …paṭipanno,` at indent 6, and its
                                # comma was being read as this line's.
                                or (_li
                                    and lines[_li - 1][1].rstrip().endswith(',')
                                    and abs(lines[_li - 1][0] - ind) <= 2))
                           and not (NIDCOLO.search(t) and NIDSECT.search(t)))
                  # ...AND `headfix` BEATS THE COLOPHON TEST.  Its stated
                  # meaning is "a line NAMED here IS A HEADING WHEREVER IT
                  # SITS", but this branch runs FIRST and claimed the line
                  # before the heading branch could honour that.  06Di01 p149
                  # heads a section `Dasa-ākāra.` — WITH A TERMINAL STOP — and
                  # `kat_is_colo` took it for a colophon; the mātikā lists it
                  # at p131 beside `Tisso vidhā`, which IS a heading, and unit
                  # 343 opens directly under it.  The body gate reads 0/0/0/0
                  # either way, because the line is present; only the mātikā
                  # diff could see it.
                  # Inert wherever `headfix` is empty, which is every volume
                  # but three, and none of those three names a line this branch
                  # would claim.  Proved: regress 55/55 and BUILDER-vs-BUILDER
                  # byte-identical over all other SPEC volumes.
                  and t.strip() not in SPEC[VOL].get('headfix', ())
                  and kat_is_colo(t, ind, body)):
                kinds.append('colo')
            # A NUMBERED line is decided by the numbered rule below, not by the
            # generic form test — that test knows nothing about the number and
            # took 36Abhi08's unit 388 as a heading.
            # ...AND A LINE NAMED IN `headfix` IS A HEADING WHEREVER IT SITS.
            # The display gate `body + 8` assumes a centred heading is indented,
            # but a centred line's indent falls as its name grows: 32Abhi04 sets
            # "(175) 10. Navattabbaṁbuddhassadinnaṁmahapphalantikathā" — its
            # longest — at indent 7, and it was read as body prose.  The body
            # gate reads 0/0/0/0 either way, because the line is present; THE
            # MĀTIKĀ CHECK is what reported it.  Letting measured CENTRING stand
            # in for the gate was tried and rejected: it moves every
            # `heads_by_form` volume, and even confined to this one it took two
            # body lines and still missed this one.  So the line is NAMED.
            # !!! A LINE WHOSE SUCCESSOR BEGINS LOWERCASE IS MID-SENTENCE, AND
            # A HEADING IS NEVER CONTINUED BY ONE.  Under `heads_by_form`
            # `kat_is_head` asks only for a capital, six words or fewer, no
            # comma and no terminal stop — and the COMMENTARY quotes canonical
            # kammavācā PROSE at a display indent constantly, so every such
            # quoted line satisfies it.  06VinSg06 (Vinayasaṅgaha, the first
            # commentary volume attempted) had 66 of its 106 headings wrong:
            #
            #   p114   9| Sammato saṁghena itthannāmo vihāro kappiyabhūmi khamati
            #          6| saṁghassa, tasmā tuṇhī, evametaṁ dhārayāmī”ti.
            #
            # THE SIGNAL IS THE CAPITAL, and this file already carries the
            # measurement behind it — "in this edition every heading, colophon,
            # homage, title and pāda opens with one".  `wrap_display` uses it
            # for the line ITSELF; this uses it for the line BELOW.
            # `headfix` still wins: a literal named there is a heading wherever
            # it sits, which is what "named" means.
            #
            # MEASURED OLD-vs-NEW OVER ALL 39 VOLUMES IN SPEC
            # (`_fnprobe/headnext.py`), a shipped canon volume run FIRST as a
            # control: **THIRTY-EIGHT ARE BYTE-IDENTICAL** on all five
            # side-maps.  Exactly two move:
            #   06VinSg06  31 quoted-formula lines demoted — the target
            #   15An01     TWO RUNNING HEADERS demoted, and that is a
            #              CORRECTION, checked on the page: 0-based p292 sets
            #              the real stack `3. Tatiyapaṇṇāsaka / (11) 1.
            #              Sambodhavagga / 1. Pubbevasambodhasutta`, while p294
            #              and p298 repeat `(11) 1. Sambodhavagga` as the page
            #              header above body text continuing mid-sentence.  The
            #              REAL heading at p292 is kept.
            #              (p296 is a THIRD such running header and SURVIVES,
            #              because its successor happens to open with a capital
            #              — a pre-existing defect this rule neither fixes nor
            #              worsens.  Recorded, not worked around.)
            elif ((disp or t.strip() in SPEC[VOL].get('headfix', ()))
                  and not (m and SPEC[VOL].get('heads_by_form'))
                  and (kat_is_head(core)
                       or t.strip() in SPEC[VOL].get('headfix', ()))
                  and (t.strip() in SPEC[VOL].get('headfix', ())
                       or not (SPEC[VOL].get('heads_by_form')
                               and _li + 1 < len(lines)
                               and re.match(r'^[a-zāīūṁṅñṇṭḍḷ]',
                                            lines[_li + 1][1])))
                  and not headskip(t)):
                kinds.append('head')
            # TWO HEADINGS ON ONE LINE, SET IN THE BODY COLUMN.  28Khu11 p245
            # sets "1. Buddhavagga        1. Dvinnaṁ Buddhānaṁ
            # anuppajjamānapañha" at indent 5, not centred like the same shape
            # on p38 and p117 — so the display test never saw it and it was
            # read as the Anumānapañha's first NUMBERED UNIT.  That is worse
            # than a wrong role: it took an ordinal, so every unit after it
            # paired with the wrong paragraph, and the 1:1 count check is what
            # refused to build on it.  The signal is the edition's own
            # typography and does not depend on indent: a run of 3+ spaces
            # separating two halves that are BOTH heading-shaped.  Requiring
            # both halves is what keeps ordinary prose out.
            elif m and _is_double_head(t):
                kinds.append('head')
            # A NUMBERED LINE, under `heads_by_form`.  The form test alone is
            # ambiguous once a line carries a number: 36Abhi08 p142 sets the
            # UNIT "388. Navipākapaccayā hetuyā tīṇi. (Saṁkhittaṁ.
            # Paripuṇṇaṁ.) Avigate" whose core is six words with no terminal
            # stop — indistinguishable by form from the heading "2.
            # Paccayaniddesa".  Measured over the volume the two are entirely
            # separate on three axes at once: its 69 numbered headings are ALL
            # one or two words, carry NO internal period, and sit at indent
            # 22-30, while every numbered unit is longer, or lower, or both.
            # So a numbered line is a heading only when it is centred AND
            # short AND unpunctuated within.
            # ...OR THE WORDS ARE DECISIVE AND NO INDENT IS NEEDED, which is
            # the same allowance `kat_is_colo` form (1) makes.  The `body + 14`
            # floor assumes a centred heading is INDENTED, but a centred line's
            # indent falls as its name grows: 31Abhi03 centres fourteen
            # "-padaniddesa" section heads and the four longest land at indent
            # 12-13, so they were read as numbered UNITS and that book came out
            # 522 printed against 518 corpus.  A line that is two words or
            # fewer, carries no internal period AND ENDS AT ONE OF THE VOLUME'S
            # OWN HEADING STEMS is a heading wherever it sits.
            # ...AND THE WORD CAP IS A MEASUREMENT, NOT A CONSTANT.  Two is
            # what 36Abhi08 measured, and every Abhidhamma volume since has
            # agreed; 03Vin03's section titles are THREE and four words
            # ("Āpattiyā adassane ukkhittakavatthūni", "Saṁghe bhinne
            # cīvaruppādakathā"), so four of them were read as numbered UNITS.
            # MEASURED over that volume: of its 769 numbered printed lines,
            # 282 are <=4 words with no internal period AND centred at
            # body+14 or beyond, and every one of those is a section title;
            # the 473 that are longer are all units; and of the 14 that are
            # short but sit LOW, the six ending at a heading stem are titles
            # whose own length pushed them down and the rest are units the
            # stem test correctly refuses.  Left per volume, defaulting to
            # the 2 every shipped volume was measured at.
            # ...AND A LINE NAMED IN `headfix` IS A HEADING HERE TOO.  That key's
            # stated meaning is "a heading WHEREVER IT SITS", and it was not
            # true of a NUMBERED line: the first heading branch is guarded by
            # `not (m and heads_by_form)`, so a `headfix` literal that matches
            # `VERSE` could never reach it.  15SamA02 p211 is the case —
            # the edition sets `3. 10. Suvaṇṇanikkhasuttādivaṇṇanā` where its
            # own mātikā reads `3-10.`, a misprinted range separator, and the
            # internal period from the misprint fails the `'.' not in core`
            # test below.  The heading was read as a UNIT and the book paired
            # 189 printed against 188 corpus and REFUSED to build.
            # MEASURED BEFORE APPLYING: only FIVE volumes carry a `headfix` at
            # all, and of their literals only two match `VERSE` — 26Khu09's
            # `5. Virāgatathā`, whose volume is not `heads_by_form` so this
            # branch cannot reach it, and 38Abhi10's
            # `2. Paccayapaccanīya      2. Saṅkhyāvara`, which is already
            # claimed by the `_is_double_head` branch ABOVE this one.  Then
            # measured old-vs-new over every SPEC volume.
            elif (m and SPEC[VOL].get('heads_by_form')
                  and (t.strip() in SPEC[VOL].get('headfix', ())
                       or (len(core.split()) <= SPEC[VOL].get('head_words', 2)
                           and '.' not in core[:-1]
                           and (ind >= body + 14
                                or re.search(r'(?:' + SPEC[VOL]['stems'] + r')\d*$',
                                             core, re.I))))):
                kinds.append('head')
            # …and otherwise it is a UNIT WHEREVER IT SITS.  The `body + 3`
            # floor exists to stop a mid-paragraph number being read as one,
            # but this edition sets a numbered unit flush at the left margin
            # when the page is mostly display — 36Abhi08 p308 does it twice
            # (units 652 and 653) — and those two were being read as prose
            # continuation, which broke the 1:1 pairing.  Safe here because the
            # heading cases above are already taken and `VERSE` anchors the
            # number at the start of a line, which a wrapped continuation never
            # does.  Measured: exactly two such units, no false positives.
            elif m and (hanging or ind >= body + 3
                        or SPEC[VOL].get('heads_by_form')):
                kinds.append('unit')
                seen_unit = True
            # the upper band of an all-display page: centred prose (above)
            elif centre_from is not None and ind >= centre_from:
                kinds.append('popen')
            elif disp_only or ind >= body + 3:
                kinds.append('cand')       # verse or prose opener — decided below
            else:
                kinds.append('pcont')
        # A NUMBERED UNIT THAT IS A GĀTHĀ.  Decided by the printed geometry: the
        # line after the number is set at a STRICTLY GREATER indent, where a
        # prose unit's continuation returns to the body column.  Its pādas are
        # the following lines sharing that indent.  Run before the verse-run
        # pass below, so those pādas are not first taken for prose openers.
        umv = SPEC[VOL].get('units_may_be_verse')
        if umv:
            for i, k in enumerate(kinds):
                if k != 'unit' or i + 1 >= len(kinds):
                    continue
                if kinds[i + 1] != 'cand' or lines[i + 1][0] <= lines[i][0]:
                    continue
                # VERSE SITS AT A DISPLAY INDENT, AND A LIST DOES NOT.  30Abhi02
                # sets its enumerations one item per printed line at the
                # PARAGRAPH indent ("Duvidhena vedanākkhandho–atthi sahetuko,
                # atthi ahetuko."), which is a run of candidates sharing an
                # indent — a gāthā's own shape — and every item is a complete
                # sentence ending in a full stop, so `display_prose`'s pāda test
                # cannot see it either (29Abhi01 met the same thing and answered
                # it with `no_verse`, which is not available here because this
                # volume does print gāthā).
                #
                # MEASURED, NOT CHOSEN: over the whole volume the runs fall at
                # indents 4-7 (42 of them, every one a prose list) and 10-14
                # (three, every one a gāthā checked against the page), with
                # NOTHING at 8 or 9.  So `verse_indent` is the size of that gap
                # and the flag is per volume.
                _vi = SPEC[VOL].get('verse_indent')
                if _vi is not None and lines[i + 1][0] < body + _vi:
                    continue
                j, ind0 = i + 1, lines[i + 1][0]
                while j < len(kinds) and kinds[j] == 'cand' and lines[j][0] == ind0:
                    j += 1
                # 'hanging' — TWO THINGS THE PAGE ITSELF SAYS, and both are
                # needed.  28Khu11 has ELEVEN units followed by a line at a
                # greater indent and only ONE of them is a gāthā; the other ten
                # are prose that quotes one.
                #  (a) THE CITATION DASH.  The edition ends a prose lead-in
                #      with "–" where the quotation follows ("4. Bhante
                #      Nāgasena bhāsitampetaṁ Bhagavatā–").  A pāda never ends
                #      that way, so a unit whose own line ends in the dash is
                #      prose whatever follows it.  This alone decides all
                #      eleven correctly; it is the decisive test.
                #  (b) A DISPLAY QUOTATION'S FIRST LINE HANGS LEFT of its own
                #      body — the marker and the opening quote are set to the
                #      left and the remaining pādas further right — so a run
                #      followed by another candidate run at a STILL GREATER
                #      indent opens a block of its own and is not a pāda of the
                #      numbered unit.
                # !!! 27Khu10 NEEDS A THIRD ANSWER, and the reason is that
                # NEITHER geometric test works there.  Its page does not
                # separate the two cases at all: p15's genuine verse unit
                # "14. Sabbo samādhi ñāṇamūlako…" and p203's prose unit
                # "26. Tattha katamaṁ ñāṇaṁ." have IDENTICAL geometry — number
                # at indent 4, the lines below at a greater indent — and
                # neither carries the citation dash.  And test (b) is worse
                # than useless there: unit 95's gāthā is followed by
                # "Idaṁ vāsanābhāgiyaṁ suttaṁ." at indent 20, a candidate at a
                # STILL GREATER indent, so (b) would call a genuine verse unit
                # prose.  So 27Khu10 gets `'formula'` — the dash test only —
                # plus `prose_openers` below.
                #
                # WHAT DECIDES IT IS THE BOOK'S OWN IDIOM.  The Netti and the
                # Peṭakopadesa are catechetical: they ask "Tattha katamo X." and
                # answer with a quoted gāthā.  That opener is a complete PROSE
                # sentence, and no pāda in either work begins that way.
                # Measured over the volume: 66 of its 271 units were being
                # drawn as verse and 46 of those 66 open with one of four
                # printed formulae; the other 20 are genuine gāthā, checked
                # against the page one at a time.  A named formula, not a
                # widened rule — the rule that would cover it would also
                # swallow the 20.
                _po = SPEC[VOL].get('prose_openers')
                if _po and re.match(_po, it_text(lines[i][1])):
                    continue
                if umv in ('hanging', 'formula'):
                    #  (a) THE CITATION DASH — see below; a pāda never ends in
                    #      one.  It is what decides 27Khu10's "Tatridaṁ
                    #      niyyānaṁ–", whose display block is not verse at all
                    #      but the printed LIST of the niyyāna.
                    if re.search(r'[–—:]$', it_text(lines[i][1])):
                        continue
                if umv == 'hanging':
                    if (j < len(kinds) and kinds[j] == 'cand'
                            and lines[j][0] > ind0):
                        continue
                kinds[i] = 'uverse'
                for j2 in range(i + 1, j):
                    kinds[j2] = 'upada'
        # VERSE RUNS.  A prose opener is followed by continuation at the body
        # column; a verse line is followed by another line at ITS OWN indent.
        # So a maximal run of >=2 consecutive candidates sharing one indent is
        # verse, and a run of one is a prose paragraph opener.
        # THE CATECHETICAL OPENER IS NEVER A PĀDA, numbered or not.  The same
        # formula that decides a numbered unit (`prose_openers`) is printed
        # WITHOUT a number wherever the answer to the previous question runs on
        # — "Tattha katamā jarā.", "Tattha katamaṁ neyyaṁ.",
        # "Tattha katamaṁ lobhādhiṭṭhānaṁ." — and two of them side by side make
        # a run of two, which the run rule reads as verse.  27Khu10 had three
        # gāthā blocks opening with one.
        _po = SPEC[VOL].get('prose_openers')
        _isopen = (lambda t: bool(re.match(_po, it_text(t)))) if _po \
            else (lambda t: False)
        i = 0
        while i < len(kinds):
            if kinds[i] != 'cand':
                i += 1
                continue
            if _isopen(lines[i][1]):
                kinds[i] = 'popen'
                i += 1
                continue
            j = i + 1
            while (j < len(kinds) and kinds[j] == 'cand'
                   and lines[j][0] == lines[i][0]
                   and not _isopen(lines[j][1])):
                j += 1
            run = (j - i) >= 2 or disp_only
            # the same gate on a run as on a unit's pādas — see the comment at
            # `verse_indent` above
            _vi = SPEC[VOL].get('verse_indent')
            if _vi is not None and lines[i][0] < body + _vi:
                run = False
            if SPEC[VOL].get('no_verse'):
                run = False        # measured: this book prints no gāthā
            # A DISPLAY QUOTATION'S FIRST LINE HANGS LEFT OF ITS OWN BODY, and
            # a run of ONE is what that looks like.  28Khu11 recorded the shape
            # and used it to keep a numbered unit OUT of the quotation; here it
            # is needed the other way round.  Once 27Khu10's "26. Tattha katamo
            # adhippāyo." is prose, the quotation it introduces is printed
            #
            #     26. Tattha katamo adhippāyo.                  (indent 4)
            #      + “Dhammo have rakkhati dhammacāriṁ,          (indent 5)
            #          Chattaṁ mahantaṁ yatha vassakāle.         (indent 9)
            #          …
            #
            # so the marker line is a run of one and would be drawn as a PROSE
            # paragraph with the gāthā's remaining pādas as a separate block
            # below it — the same split, one line further down.  A single
            # candidate immediately followed by a run of two or more at a
            # GREATER indent is that line, and it belongs to the gāthā.
            # Gated per volume.
            # WHAT MARKS THE HANGING LINE is the edition's own apparatus: the
            # CITATION MARKER (`*`, `**`, `+`) and/or the OPENING QUOTE are set
            # to the left of the pādas, which is WHY the line hangs.  Requiring
            # that keeps an ordinary one-line prose paragraph out of the gāthā
            # below it — 27Khu10 p176 sets "Aṭṭhimā Ānanda dānupapattiyo
            # ekuttarike suttaṁ, ayaṁ jāti." immediately above one, and it is
            # prose.  The following run may be a single pāda: the edition sets
            # plenty of two-pāda quotations, and both of ord54's and ord158's
            # are that shape.
            if (not run and SPEC[VOL].get('hanging_quote')
                    and re.match(r'^(?:\*+|\+|[“‘])', lines[i][1].strip())
                    and j < len(kinds) and kinds[j] == 'cand'
                    and lines[j][0] > lines[i][0]):
                _k = j + 1
                while (_k < len(kinds) and kinds[_k] == 'cand'
                       and lines[_k][0] == lines[j][0]):
                    _k += 1
                if _k - j >= 1:
                    # the hanging line AND its pādas are ONE run, so the
                    # pāda-punctuation test below sees the whole quotation and
                    # `open_gatha` is not closed between the two indents
                    j, run = _k, True
            # A DISPLAY BLOCK IS NOT ALWAYS VERSE.  This edition also indents
            # long PROSE quotations from the suttas, and they have the same
            # geometry as a gāthā — a run of lines sharing one indent above the
            # body column.  28Khu11 sets nine of them (p153, p154, p226, p374,
            # p382, p400, p403 and two more), and every one was being emitted
            # as a {"gatha": …} block, i.e. rendered as italic verse with the
            # printed line breaks kept.  Present, contiguous, unique: 0/0/0/0
            # from the body gate.
            # What separates them is PĀDA PUNCTUATION, not indent: a gāthā
            # breaks at the end of each pāda, so every line but the last ends
            # in a comma or a full stop, while a prose quotation breaks
            # wherever the measure runs out and its lines end mid-clause.
            # Gated per volume: 26Khu09 and 27Khu10 print the same shape and
            # are almost certainly affected too, but fixing them moves two
            # shipped volumes and belongs with their own re-gating (HANDOFF).
            if run and SPEC[VOL].get('display_prose'):
                # A run of several: every line but the LAST must be a pāda.
                # A run of one — only possible on a page with no body column
                # at all, which is read as entirely display — must itself be a
                # pāda: 28Khu11 p37 sets the lead-in "Tenāhu–" alone above the
                # gāthā it introduces, on a page with nothing at the margin, so
                # it was being drawn as the block's first verse line.
                # THE LAST LINE COUNTS TOO.  A gāthā's final pāda ends in a
                # full stop; a PROSE quotation's last line runs on into the
                # paragraph below it, and that is the clearest tell of all —
                # 27Khu10 p41 sets "Ayuñjantānaṁ vā sattānaṁ yoge, …" whose
                # second line ends "So pamādo" and continues "duvidho
                # taṇhāmūlako…" in the next block.  Tested all-but-last when
                # this was written; measured over the eleven regression
                # volumes, requiring the last line as well moves NOTHING except
                # 27Khu10 — 28Khu11, which is the volume the flag was written
                # for, is byte-identical.
                tail = j
                # !!! AND A GĀTHĀ'S LAST PĀDA DOES NOT ALWAYS CARRY A STOP.
                # Where the edition quotes a gāthā INTO the prose below it, the
                # closing pāda ends in the CITATION DASH — `…bandhanan”ti15–`
                # (29KhuA10 p40), `…vijānatan”ti–` (p87) — which is the same
                # line-end `headskip` exists for.  Tested `[,.]$` alone on that
                # volume it demotes SEVEN REAL GĀTHĀ BLOCKS to fix seven prose
                # ones, so the flag is worth nothing there.
                # A NEW VALUE, NOT A WIDER RULE: `display_prose: 'dash'` admits
                # the dash as a pāda end; plain `True` is unchanged, so 27Khu10,
                # 28Khu11 and 32Abhi04 — the three shipped volumes that set it —
                # cannot move.  Measured: all three byte-identical, regress 55/55.
                # The closing form is `…”ti`, with or without a footnote
                # marker and with or without the dash — p391 re-quotes a gāthā
                # whose last pāda runs straight on into the sentence below and
                # so carries NEITHER.  A prose quotation that runs on does not
                # end in `”ti` at all (27Khu10 p41 ends `So pamādo`), so the
                # test keeps the power the last-line rule was added for.
                _pada = (r'[,.]$|”\s*ti\d*\s*[–-]?$'
                         if SPEC[VOL].get('display_prose') == 'dash' else r'[,.]$')
                if not all(re.search(_pada, lines[k][1])
                           for k in range(i, tail)):
                    kinds[i] = 'popen'
                    for k in range(i + 1, j):
                        kinds[k] = 'pcont'
                    i = j
                    continue
            for k in range(i, j):
                kinds[k] = 'vline' if run else 'popen'
            i = j
        # !!! AN UDDĀNA THAT CHANGES COLUMN AT A PAGE BREAK.  `_kat_cols`
        # measures the body column PER PAGE, and that is right: it is what lets
        # every volume find its own paragraph indent.  But a mnemonic uddāna
        # can be the WHOLE of a page, and then the body column measures 0 and
        # the uddāna's own lines sit AT it — so the same printed block is
        # `pcont` (prose) on a page it fills and `vline` (verse) on a page it
        # shares.  04Vin04's Senāsanakkhandhaka uddāna runs p344 at indent 0,
        # p345 at 6, p346 at 0.  Classified two ways it is EMITTED two ways —
        # prose joins the running string in `after`, verse opens a gāthā block
        # — so the render reads p344 straight into p346 and the middle turns up
        # elsewhere.  Nothing is lost, which is why `PDF-lines-missing` stays 0
        # and only the ORDER check sees it.
        #
        # THE EDITION ITSELF MARKS THE BLOCK: "Tassuddānaṁ" opens it and the
        # section's own colophon closes it.  So the label decides the whole
        # run, wherever its lines happen to sit, and the state is carried
        # across the page break.  A numbered unit or a heading ends it too —
        # those cannot occur inside an uddāna and are the safety net if a
        # colophon is ever missed.
        #
        # The closing line is recognised WITHOUT an indent test for the same
        # reason the pādas are: on a page the uddāna fills, the colophon sits
        # at the body column too ("Senāsanakkhandhako niṭṭhito." on p346 was
        # arriving as prose).  It must NAME a section and say it is finished,
        # which is `kat_is_colo`'s own strictest form.
        #
        # DO NOT REACH FOR A WIDER DISPLAY GATE HERE.  The per-page body
        # measurement is load-bearing for every shipped volume; this is a fact
        # about one BLOCK, not about the page.  Gated per volume.
        if SPEC[VOL].get('udd_run'):
            for _u, (_ind, _t) in enumerate(lines):
                if kinds[_u] == 'udd':
                    in_udd = True
                    continue
                if not in_udd:
                    continue
                if kinds[_u] in ('unit', 'uverse', 'head', 'homage'):
                    in_udd = False
                    continue
                if (_t.endswith('.') and ',' not in _t and len(_t.split()) <= 6
                        and NIDCOLO.search(_t)):
                    kinds[_u] = 'colo'
                    in_udd = False
                    continue
                kinds[_u] = 'vline'
        for (ind, t), k in zip(lines, kinds):
            if k in ('unit', 'uverse'):
                m = VERSE.match(t)
                items.append((k, int(m.group(1)), m.group(2), pg))
            else:
                items.append((k, t, pg))
    return items


def unnum_runs(items, paras, cands):
    """Align each UNNUMBERED corpus paragraph against a contiguous run of
    printed items.

    SELF-VERIFYING, and that is the whole point: the run's joined text must
    EQUAL the paragraph's, normalised for whitespace.  A run is never guessed
    at, so a paragraph the printed stream does not reproduce exactly is
    REPORTED and left hidden rather than half-placed.

    A LINE-END HYPHEN IS JOINED EITHER WAY.  The corpus keeps
    "...sakadagami- anagami..." with the hyphen AND the space; the body gate
    strips it.  Both candidates are tested against the paragraph itself, so
    the paragraph decides which join the extraction made.

    A `head` / `colo` / `udd` item whose text the paragraph does NOT contain is
    SKIPPED and returned separately: the corpus paragraph spans a printed
    heading the extraction did not break on (01VinA01's `Bahiranidanakatha`).
    One whose text the paragraph DOES contain is a misread line, not a
    heading -- the extraction proves it is body text -- and is returned in
    `used` like any other line.

    Returns {ord: (a, b, used, skipped)}.
    """
    def _n(x):
        return re.sub(r'\s+', ' ', (x or '')).strip()
    def _t(it):
        return _n(it[2] if it[0] in ('unit', 'uverse') else it[1])
    texts = [_t(it) for it in items]
    out, frm = {}, 0
    for o in cands:
        want = _n(paras[o].get('text') or '')
        if not want:
            continue
        hit = None
        for a in range(frm, len(items)):
            if not texts[a] or not want.startswith(texts[a][:25]):
                continue
            acc, used, skipped = '', [], []
            for b in range(a, len(items)):
                k = items[b][0]
                if k in ('unit', 'uverse', 'homage') and b > a:
                    break
                t = texts[b]
                cnd = ([acc[:-1] + t, acc + ' ' + t] if acc.endswith('-')
                       else [acc + ' ' + t] if acc else [t])
                nxt = next((c for c in cnd if want.startswith(c)), None)
                if nxt is None:
                    if k in ('head', 'colo', 'udd'):
                        skipped.append(b)
                        continue
                    break
                acc = nxt
                used.append(b)
                if acc == want:
                    hit = (a, b, used, skipped)
                    break
            if hit:
                break
        if hit:
            out[o] = hit
            frm = hit[1] + 1
    return out



# ---------------------------------------------------------------------------
# HEADING-DELIMITED PROSE.  THE FOURTH PAGE-READER, and it is reached only from
# a book whose SPEC entry carries mode='heads'.
#
# WHY IT HAS TO EXIST.  The other three readers all pair a printed ANCHOR
# against a corpus paragraph: `verse` wants pādas under a number, `niddesa` a
# display lemma plus prose, `katha` a number opening prose.  05Kankha has FIVE
# numbered units in 275 printed pages -- its structure is carried entirely by
# the centred kathā headings -- so there is nothing to pair, and in its first
# two books the mismatch runs the other way, because the pātimokkha's
# SIKKHĀPADA numbers are read as unit numbers (304 printed against 220 corpus).
# Diagnosed 2026-07-27aa; this is that reader.
#
# THE ANCHOR IS THE TEXT ITSELF.  A printed body line is located in the corpus
# paragraph that contains it, searching FORWARD ONLY from the last paragraph
# already located -- the printed stream and the corpus run in the same order,
# so forward-only is both correct and what disambiguates a repeated line.
# MEASURED BEFORE THIS WAS WRITTEN (`_kankha/probe2.py`, `probe4.py`):
#
#     383 printed headings, 383 anchored, 0 unanchored
#     8,996 of 8,999 printed body lines located in the corpus
#     930 corpus paragraphs, 927 touched; the 3 that are not are the two
#     homages and one leaked colophon
#
# A MINIMUM KEY LENGTH WAS TRIED AND REJECTED.  With the book bounds WRONG, one
# ten-character line (`veditabbaṁ.`) matched a paragraph past the one it
# belonged to and the forward pointer could never come back -- 121 of book 4's
# 131 paragraphs were lost to it.  The obvious fix is to forbid a short line
# from moving the pointer; swept over 0/12/16/20/24/30/40 with the bounds
# CORRECTED it changes nothing at all (3 untouched, 3 residue, at every value).
# The defect was the bounds, not the line, so the rule is not added.
#
# WHAT IT REFUSES.  An untouched corpus paragraph is one the printed stream
# never confirmed.  Those that are the book's homage or a leaked heading or
# colophon are hidden and drawn from the printed stream; ANY OTHER untouched
# paragraph is reported by ordinal, and more than 2% of a book is FATAL --
# silently skipping text is worse than refusing to build.
# ---------------------------------------------------------------------------

_SQ = re.compile(r'[^0-9a-zāīūṁṃṅñṇṭḍḷ]')


def _sq(s):
    return _SQ.sub('', (s or '').lower())


def head_build(pages, paras, title, p0, p1, o0, o1,
               verse, sections, uddana, hide, incipit, report):
    """Map one heading-delimited book's printed stream onto its corpus."""
    items = kat_items(pages, p0, p1)
    blob = {o: _sq(paras[o].get('text')) for o in range(o0, o1)}
    rec = {'book': title, 'mode': 'heads', 'corpus_paras': o1 - o0,
           'printed_lines': 0, 'located': 0, 'residue': 0,
           'heads': [], 'colos': [], 'untouched': [], 'untouched_visible': [],
           'unanchored_heads': []}
    report['books'].append(rec)

    BODY = ('popen', 'pcont', 'cand', 'vline', 'pada', 'unit')
    st = {'cur': o0, 'ord': None}
    touched = set()
    pend_heads, pend_before, after, pend_colo = [], [], [], []

    def close():
        """Attach whatever has accumulated to the paragraph just located."""
        o = st['ord']
        if o is None:
            return
        if after:
            # !!! NO `groups` KEY.  An entry that carries one — even an EMPTY
            # one — makes both `render_parts` and the reader take the VERSE
            # branch, which renders `before + after` and NOT the corpus text.
            # Written as `{'groups': []}` the three residue lines of this
            # volume REPLACED the paragraphs they were attached to, and the
            # body gate reported 287 printed lines missing that are in fact in
            # the corpus.  Without the key both take the prose branch:
            # `before` + the corpus text + `after`.
            e = verse.setdefault(str(o), {})
            e.setdefault('after', []).extend(after)
            del after[:]
        if pend_colo:
            uddana.setdefault(str(o), []).extend(pend_colo)
            del pend_colo[:]

    for it in items:
        kind = it[0]
        txt = it[1]
        if kind in ('pada', 'prose', 'centre', 'head') and txt.strip() == title:
            continue                       # the book's own name; `booktitle/` draws it
        if kind == 'homage':
            incipit[str(next((_o for _o in range(o0, o1) if str(_o) not in hide), o0))] = txt.strip()
            continue
        if kind in ('head', 'centre'):
            # TWO HEADINGS ON ONE PRINTED LINE, the same rule `kat_build` uses.
            # 05Kankha sets `1. Musāvādavagga      1. Musāvādasikkhāpadavaṇṇanā`
            # — a vagga and its first sikkhāpada — seven times; taken whole they
            # rendered as one heading with a run of spaces in the middle, AND the
            # corpus paragraph below opens with the same joined string, so the
            # pair showed twice.  Splitting them fixes both at once.
            for part in split_centre(txt.strip()):
                pend_heads.append({'l': part, 'k': head_kind(part)})
                rec['heads'].append({'pg': it[2] if len(it) > 2 else None, 'l': part})
            continue
        if kind in ('colo', 'udd'):
            pend_colo.append({'label': None, 'lines': [txt.strip()], 'app': []})
            rec['colos'].append({'l': txt.strip()})
            continue
        if kind not in BODY:
            continue
        # !!! A `unit` ITEM CARRIES ITS NUMBER IN `it[1]` AND ITS TEXT IN
        # `it[2]`, so `txt` IS AN INT THERE.  The key already read `it[2]`;
        # the residue branch below did not, and on 07ViT07 -- the first `heads`
        # book whose printed stream carries numbered units that the corpus does
        # not hold -- it raised `'int' object has no attribute 'strip'`.
        # 05Kankha and 36KhuA17 never reached it: every one of their units is
        # located, so the residue branch had never seen a `unit` item.
        # Measured before landing: both of those volumes rebuild BYTE-IDENTICAL
        # on all five side-maps after this change.
        btxt = it[2] if kind == 'unit' else txt
        key = _sq(btxt)[:60]
        if not key:
            continue
        rec['printed_lines'] += 1
        o = next((k for k in range(st['cur'], o1) if key in blob[k]), None)
        if o is None:
            # printed body text the corpus does not hold -- the residue
            rec['residue'] += 1
            tgt = pend_before if pend_heads else after
            if tgt and tgt[-1].endswith('-'):
                tgt[-1] = hyjoin(tgt[-1], btxt.strip())
            else:
                tgt.append(btxt.strip())
            continue
        rec['located'] += 1
        if o != st['ord']:
            close()
        st['cur'] = o
        st['ord'] = o
        touched.add(o)
        if pend_heads:
            sections.setdefault(str(o), []).extend(pend_heads)
            pend_heads = []
        if pend_before:
            e = verse.setdefault(str(o), {})      # no `groups` — see above
            e.setdefault('before', []).extend(pend_before)
            pend_before = []
    close()
    if pend_heads:
        rec['unanchored_heads'] = [h['l'] for h in pend_heads]

    for o in range(o0, o1):
        if o in touched:
            continue
        raw = (paras[o].get('text') or '').strip()
        rec['untouched'].append({'ord': o, 'text': raw[:80]})
        # !!! NEVER HIDE THE PARAGRAPH THAT ANCHORS THE INCIPIT.  A side-map
        # entry on a hidden ordinal never renders, and the booktitle stack is
        # written to the same ordinal later, so hiding it silently drops BOTH.
        # The reader already strips the embedded homage from a visible
        # paragraph that carries an incipit (`render_parts`/`block()`), which
        # is exactly what every verse-path volume relies on.  Census over all
        # side-maps: FOUR entries corpus-wide were anchored to a hidden
        # ordinal, all four written by this reader — 36KhuA17 ord0 (incipit AND
        # booktitle) and 05Kankha ord591/ord799, whose books 3 and 4 have been
        # rendering with NO homage since 2026-07-28f.
        if str(o) in incipit:
            pass
        elif (raw in incipit.values() or kat_is_head(raw, printed=False)
                or kat_is_colo(raw)):
            hide[str(o)] = 1                # drawn from the printed stream instead
        else:
            rec['untouched_visible'].append({'ord': o, 'text': raw[:80]})
    n = len(rec['untouched_visible'])
    if n and n * 50 > (o1 - o0):
        rec['FATAL'] = ('%d of %d corpus paragraphs are not confirmed by the '
                        'printed stream (more than 2%%)' % (n, o1 - o0))

def kat_build(pages, paras, title, p0, p1, o0, o1,
              verse, sections, uddana, hide, incipit, report):
    """Map one kathā book's printed stream onto its corpus paragraphs."""
    items = kat_items(pages, p0, p1)
    # THE TITLE PAGE'S OWN STACK, taken from `booktitle/<VOL>.json` rather than
    # from a constant.  It was `(title, 'Khuddakanikāya')`, which is the whole
    # Khuddaka and nothing else; 29Abhi01's page sets "Abhidhammapiṭaka" above
    # its book name, and that line was arriving as a heading of the body.  The
    # booktitle map already holds the printed stack in order for all 40 canon
    # volumes (build_booktitles.py), so it is the right source.
    titlestack = {title, 'Khuddakanikāya'}
    _bt = os.path.join(R, 'booktitle', VOL + '.json')
    if os.path.exists(_bt):
        for _v in json.load(open(_bt, encoding='utf-8')).values():
            for _l in ([_v] if isinstance(_v, str) else _v):
                titlestack.add(_l.strip())
    printed = [it for it in items if it[0] in ('unit', 'uverse')]
    # LEAKED HEADINGS, hidden BEFORE the pairing, exactly as in the verse path.
    # 26Khu09 ord351 is the printed line "7. Dhammacakkakathā   1. Saccavāra" —
    # two centred headings typeset on one line — captured whole as a corpus
    # paragraph and carrying the KATHĀ's number as its `n`.  Left in, it takes
    # up an ordinal and every unit after it pairs with the wrong paragraph.
    # The headings themselves are not lost: the PDF stream supplies them.
    # LEAKED HEADINGS RECOGNISED AGAINST THE PRINTED STREAM ITSELF.
    #
    # The stem test asks whether a corpus paragraph LOOKS like a heading.  That
    # cannot see 39Abhi11's, because the extraction joined TWO CONSECUTIVE
    # centred lines into one paragraph with a single space —
    #
    #     1-7. Paṭiccādivāra              (printed on its own line)
    #     Paccayacatukka-hetu             (printed on the next)
    #     -> corpus "1-7. Paṭiccādivāra Paccayacatukka-hetu"
    #
    # — and the result ends in "hetu", which is no heading stem, so 88 of them
    # stayed visible and took 88 units' ordinals.  There is no need to GUESS:
    # this book's own printed heading stream is already in hand, so a paragraph
    # that reproduces a run of consecutive printed headings IS those headings.
    _hs = [split_centre(it[1].strip()) for it in items if it[0] == 'head']
    _hs = [x for parts in _hs for x in parts]
    _runs = set()
    for _a in range(len(_hs)):
        _acc = ''
        for _b in range(_a, min(_a + 3, len(_hs))):
            _acc = (_acc + ' ' + _hs[_b]).strip()
            _runs.add(re.sub(r'\s+', ' ', _acc))

    for o in range(o0, o1):
        raw = (paras[o].get('text') or '').strip()
        t = head_body(re.sub(r'^\d+(?:-\d+)?\.\s*', '', raw))
        _norm = re.sub(r'\s+', ' ', raw)
        # FIVE WAYS TO BE A LEAKED HEADING, not one: the stem test; a DOUBLE
        # heading (neither half is a suffix of the whole line); a double
        # heading that RUNS ON into the material printed under it; a run of
        # consecutive printed headings the extraction joined; and the
        # edition's own misspellings, named in `headfix`.
        # ...AND A UNIT WHOSE TAIL THE EXTRACTION GLUED A HEADING ONTO IS NOT
        # A LEAKED HEADING.  The stem test asks whether a corpus paragraph
        # LOOKS like a heading, and a paragraph ENDING in a heading stem does.
        # 18AnA02 ord463 is a real unit — `264-273. Kammapathavaggepi dasapi
        # kammapathā lokiyalokuttaramissakāva kathitā.` — with the NEXT
        # heading, `(28) 8. Rāgapeyyālavaṇṇanā`, swallowed onto its end,
        # because that heading opens with `(` and the extraction does not
        # break there.  Hidden, its unit vanished from the book and the 1:1
        # count refused: 188 printed against 187 corpus.
        # `leak_keep` NAMES the ordinal and REFUSES if it is not in fact
        # flagged, so the declaration cannot rot into a lie about the corpus.
        # The divergence is RECORDED, not corrected — the same treatment
        # `unnum_spanning` gives 01VinA01 ¶14, which spans a printed heading
        # the extraction likewise did not break on.
        if o in SPEC[VOL].get('leak_keep', ()):
            if not (kat_is_head(t, printed=False) or _is_double_head(raw)
                    or _starts_double_head(raw) or _norm in _runs
                    or raw in SPEC[VOL].get('headfix', ())):
                rec['FATAL'] = ('declared `leak_keep` ord%d is not flagged as a '
                                'leaked heading; the declaration has rotted' % o)
                return
            report.setdefault('leak_kept', []).append({'ord': o, 'text': raw})
            continue
        if (kat_is_head(t, printed=False) or _is_double_head(raw)
                or _starts_double_head(raw) or _norm in _runs
                or raw in SPEC[VOL].get('headfix', ())):
            hide[str(o)] = 1
            report['leaked'].append({'ord': o, 'text': raw})
    # !!! AN UNNUMBERED CORPUS PARAGRAPH IS NOT RENDERED FROM THE CORPUS,
    # BECAUSE THE KATHĀ PATH ALREADY DRAWS IT FROM THE PRINTED STREAM.
    # Unnumbered printed prose reaches the page through `pend_before` /
    # `add_prose`, as the following unit's `before` — which is exactly why
    # 01Vin01 gates 0/0/0/0 although `extract.py` dropped 28 of its paragraphs.
    # Once those paragraphs ARE in the corpus (01VinA01, 05Kankha, rebuilt
    # 2026-07-27s because their unnumbered opening is 78 and 20 pages of
    # narrative, not a stray line), rendering them from the corpus as well
    # would draw every one of those lines TWICE.
    # So they are hidden from the render and kept in the corpus, where they are
    # what makes the Bāhiranidāna searchable, linkable and citable at all.
    # MEASURED before landing: of the 45 SPEC volumes with a corpus, ONLY those
    # two have a visible paragraph carrying no number (37 of 175, 398 of 932)
    # and the other 43 have none — so on everything already built this is inert
    # by construction, not by argument.
    _un = [o for o in range(o0, o1)
           if str(o) not in hide and paras[o].get('n') is None]
    _runs2 = unnum_runs(items, paras, _un)
    suppress, reclass, unnum_ords, unspan = set(), set(), set(), {}
    for o in _un:
        raw = (paras[o].get('text') or '').strip()
        r = _runs2.get(o)
        if r is None:
            # The printed stream does not reproduce this paragraph exactly.
            # FLAG IT AND LEAVE IT AS IT WAS -- half-placing it would put
            # printed text and corpus text on the page together.
            hide[str(o)] = 1
            report.setdefault('unnum_unaligned', []).append(
                {'ord': o, 'chars': len(raw), 'text': raw[:80]})
            continue
        a, b, used, skipped = r
        kinds = set(items[i][0] for i in used)
        def _rc(i, o=o, used=used):
            # ONLY INSIDE A LONGER PARAGRAPH.  A run that IS one structural
            # item is a corpus paragraph that holds a whole printed heading or
            # colophon (01VinA01 ord68, `Vinayadharassa ca lakkhanadikatha.`);
            # it keeps that role.  A structural item that shares its paragraph
            # with body text is a MISREAD LINE -- the extraction, which breaks
            # at headings, put it inside a paragraph -- and is drawn as one.
            if len(used) < 2:
                return
            reclass.add(i)
            report.setdefault('unnum_reclass', []).append(
                {'ord': o, 'was': items[i][0], 'pg': items[i][2],
                 'l': items[i][1]})
        if re.sub(r'\s+', ' ', raw) in titlestack:
            # the title page's own stack, which `booktitle/` draws
            hide[str(o)] = 1
            report.setdefault('unnum_title', []).append({'ord': o, 'l': raw})
            continue
        if not (kinds & {'popen', 'pcont', 'cand'}):
            # DISPLAY VERSE, a colophon, or the book's own homage.  None of
            # those is body prose, so the printed stream keeps them and the
            # corpus copy stays hidden -- the render needs the printed LINE
            # BREAKS, which the corpus paragraph does not hold.
            hide[str(o)] = 1
            for i in used:
                if items[i][0] in ('head', 'colo', 'udd'):
                    _rc(i)
            continue
        unnum_ords.add(o)
        suppress.update(used)
        for i in used:
            if items[i][0] in ('head', 'colo', 'udd'):
                _rc(i)
        if skipped:
            unspan[o] = list(skipped)
            suppress.update(skipped)
            report.setdefault('unnum_spanning', []).append(
                {'ord': o, 'heads': [items[i][1] for i in skipped],
                 'pg': [items[i][2] for i in skipped]})
    unnum_at = {}
    for o in unnum_ords:
        unnum_at[_runs2[o][0]] = o
    report.setdefault('unnumbered', []).extend(sorted(unnum_ords))
    # !!! A CORPUS PARAGRAPH WHOSE NUMBER THE EXTRACTION COULD NOT PARSE IS
    # STILL THAT UNIT.  19AnT02 p145 sets `54.55. Tatiye yesaṁ rāgādīnaṁ…` — a
    # range whose separator is a PERIOD, the class 14SamA01's `64.65.` and
    # 15SamA02's `3. 10.` already carry — and `extract.py`'s number rule wants
    # `\d+(-\d+)?\.\s`, so the paragraph arrived with `n = None`.  The text is
    # PRESENT, in the right place, with the number inside it; only the field is
    # empty, and the 1:1 count is the only thing that can see that (113 printed
    # against 112 corpus).  `kat_splices` does not fit — nothing is spliced —
    # and `kat_missing` correctly REFUSES, because the words are in the corpus.
    #
    # SELF-VERIFYING, three ways, like every other declaration here: the
    # paragraph must really carry no number, its text must really begin with
    # the declared printed opening, and the printed stream must offer exactly
    # one unit at that (number, page).  Nothing in `site/*.json` is edited.
    _renum, _renum_ok, _renum_err = set(), [], None
    for rp in SPEC[VOL].get('kat_renum', ()):
        if not (o0 <= rp['ord'] < o1):
            continue
        _t = (paras[rp['ord']].get('text') or '').strip()
        _hit = [k for k, it in enumerate(printed)
                if it[1] == rp['n'] and it[3] == rp['pg']]
        if paras[rp['ord']].get('n') is not None or not _t.startswith(rp['mark']) \
                or len(_hit) != 1:
            _renum_err = (
                'declared `kat_renum` ord%d does not hold: the paragraph carries '
                'n=%s (expected none), its text %s with %r, and the printed '
                'stream offers %d unit(s) numbered %s on p%s (expected 1)'
                % (rp['ord'], paras[rp['ord']].get('n'),
                   'begins' if _t.startswith(rp['mark']) else 'does NOT begin',
                   rp['mark'][:40], len(_hit), rp['n'], rp['pg']))
            break
        _renum.add(rp['ord'])
        _renum_ok.append({'ord': rp['ord'], 'n': rp['n'], 'pg': rp['pg'],
                          'text': _t[:60]})
    # THE RENUMBERED PARAGRAPH MUST ALSO BE UN-HIDDEN.  The kathā path hides
    # every unnumbered corpus paragraph, because it already draws that prose
    # from the printed stream — but this one is not prose, it is a UNIT whose
    # number was unreadable, and a hidden ordinal is not in `ords` at all, so
    # declaring it without this changed nothing and the count stayed 112.
    for _o in _renum:
        hide.pop(str(_o), None)
    ords = [o for o in range(o0, o1) if str(o) not in hide]
    pair_ords = [o for o in ords
                 if paras[o].get('n') is not None or o in _renum]
    rec = {'book': title, 'mode': 'katha',
           'printed_units': len(printed), 'corpus_paras': len(pair_ords),
           'unnum_prose': len(unnum_ords),
           'nmismatch': [], 'heads': [], 'colos': [], 'gathas': [],
           'prose_paras': 0, 'splices': []}
    report['books'].append(rec)
    if _renum_err:
        rec['FATAL'] = _renum_err
        return
    if _renum_ok:
        rec['renumbered'] = _renum_ok
    # PRINTED UNITS THE CORPUS DOES NOT HOLD AT ALL.  38Abhi10's printed unit 1
    # is simply ABSENT — the corpus opens at unit 2 and no paragraph anywhere
    # holds its words.  site/*.json is not edited: the unit is dropped from the
    # pairing and RECORDED, and it is not lost from the page either, because
    # the kathā path draws the body from the PRINTED stream and emits it into
    # the FOLLOWING unit's `before`, above that paragraph, with its number.
    #
    # THE DECLARATION VERIFIES ITSELF, and its check is the MIRROR of a
    # splice's: a splice requires the text to be PRESENT in the declared host,
    # an absence requires it to be present NOWHERE.  Both must also match
    # exactly one printed unit at that (number, page).
    missing_lead = {}
    for mp in SPEC[VOL].get('kat_missing', ()):
        hit = [k for k, it in enumerate(printed)
               if it[1] == mp['n'] and it[3] == mp['pg']]
        cnt = sum(1 for o in range(o0, o1)
                  if mp['absent'] in (paras[o].get('text') or ''))
        if len(hit) != 1 or cnt:
            rec['FATAL'] = (
                'declared corpus ABSENCE (printed unit %s, p%s) does not hold: '
                'the printed stream offers %d unit(s) at that number and page, '
                'and the corpus holds %d paragraph(s) containing its opening '
                'words (expected 1 and 0)' % (mp['n'], mp['pg'], len(hit), cnt))
            return
        it = printed.pop(hit[0])
        missing_lead[(it[1], it[3])] = it[2]
        rec.setdefault('absent', []).append(
            {'n': it[1], 'pg': it[3], 'text': it[2][:60]})
    # KNOWN CORPUS SPLICES — declared per volume, CHECKED AGAINST THE TEXT.
    # 36Abhi08 sets unit 41 as "41.Nevavipāka…" with NO SPACE after the number,
    # so the extraction saw no boundary and its whole text arrived inside the
    # paragraph carrying n=40.  Unit numbers repeat across vāras, so the PAGE
    # is part of the key.
    splice_lead = {}
    for sp in SPEC[VOL].get('kat_splices', ()):
        if not (o0 <= sp['ord'] < o1):
            continue
        host = paras[sp['ord']]
        htxt = (host.get('text') or '')
        hit = [k for k, it in enumerate(printed)
               if it[1] == sp['n'] and it[3] == sp['pg']]
        if host.get('n') != sp['into'] or sp['mark'] not in htxt or len(hit) != 1:
            rec['FATAL'] = (
                'declared corpus splice (printed unit %s, p%s, inside ord%d) '
                'does not hold: host n=%s (declared %s), marker %s, printed '
                'stream offers %d unit(s) at that number and page'
                % (sp['n'], sp['pg'], sp['ord'], host.get('n'), sp['into'],
                   'present' if sp['mark'] in htxt else 'ABSENT', len(hit)))
            return
        it = printed.pop(hit[0])
        splice_lead[(it[1], it[3])] = sp['mark']
        rec['splices'].append({'n': it[1], 'pg': it[3], 'ord': sp['ord'],
                               'into': sp['into'], 'text': it[2][:60]})
    rec['printed_units'] = len(printed)
    # PAIRED AGAINST THE NUMBERED PARAGRAPHS, WALKED OVER ALL OF THEM.  `ords`
    # served both jobs, and they part company the moment the corpus holds a
    # paragraph with no number: an unnumbered paragraph must be ANCHORED but
    # must not be PAIRED.  In every volume with no unnumbered prose the two
    # lists are the same list, so the 1:1 count keeps exactly the meaning it
    # has always had.
    if len(printed) != len(pair_ords):
        rec['FATAL'] = ('printed numbered units %d != corpus paragraphs %d'
                        % (len(printed), len(pair_ords)))
        return
    for k, it in enumerate(printed):
        if it[1] != paras[pair_ords[k]].get('n'):
            rec['nmismatch'].append({'pos': k, 'printed': it[1], 'pg': it[3],
                                     'ord': pair_ords[k],
                                     'corpus_n': paras[pair_ords[k]].get('n')})

    seq = iter(pair_ords)
    units_done = 0
    last = False                # the last numbered unit has been consumed
    tail_open = False           # ...and a HEADING has been printed after it
    tail_head = None            # that heading, awaiting the text it heads
    tail_hk = None              # ...and its weight, so it is not drawn as a
                                #    vatthu title under the sections it heads
    cur = None
    after = []
    groups = []                 # a unit that is itself a gāthā
    pend_heads, pend_centre, pend_before = [], [], []
    pend_seq = []               # the same material, in PRINTED order
    pend_open = []              # printed BEFORE the book's first unit
    opened = False
    open_prose = False
    open_gatha = None
    before_of = {}

    def flush():
        if cur is None:
            return
        # AN UNNUMBERED ANCHOR GETS NO `groups` KEY.  Both the reader and the
        # body gate take the verse branch -- rendering `before + after` and
        # NOT the corpus text -- for any entry that HAS a `groups` key, even
        # an empty one.  This paragraph's body IS the corpus text, so the
        # entry carries only what the print adds around it, and is omitted
        # entirely when the print adds nothing.
        e = {} if cur in unnum_ords else {'groups': [g for g in groups if g]}
        if before_of.get(cur):
            e['before'] = before_of.pop(cur)
        if after:
            e['after'] = list(after)
        if e:
            verse[str(cur)] = e

    def tail_add(kind, txt, pg):
        """Append one printed item to the uddāna stream of the current unit.

        Used for material the page sets AFTER a heading that has no numbered
        unit, and for everything after the book's last unit.  Prose uses the
        `plain` block shape (which already carries a `head`), verse the centred
        block — the two shapes `uddanaHTML` and `render_parts` already know.
        """
        nonlocal tail_head, tail_hk
        if kind == 'head':
            if tail_head is not None:
                pend_centre.append({'plain': True, 'head': tail_head,
                                    'hk': tail_hk, 'lines': [], 'app': []})
            tail_head = txt
            tail_hk = head_kind(txt)
            rec['heads'].append({'pg': pg, 'l': txt, 'tail': True})
            return
        if kind == 'vline':
            if tail_head is not None:
                pend_centre.append({'plain': True, 'head': tail_head,
                                    'hk': tail_hk, 'lines': [], 'app': []})
                tail_head = None
            if (pend_centre and not pend_centre[-1].get('plain')
                    and pend_centre[-1].get('label') is None
                    and pend_centre[-1].get('_verse')):
                _add_line(pend_centre[-1]['lines'], txt)
            else:
                pend_centre.append({'label': None, 'lines': [txt], 'app': [],
                                    '_verse': True})
                rec['gathas'].append({'pg': pg, 'l': txt, 'tail': True})
            return
        if (kind != 'popen' and pend_centre and pend_centre[-1].get('plain')
                and pend_centre[-1]['lines'] and tail_head is None):
            b = pend_centre[-1]['lines']
            b[-1] = hyjoin(b[-1], txt)
        else:
            pend_centre.append({'plain': True, 'head': tail_head,
                                'hk': tail_hk, 'lines': [txt], 'app': []})
            rec['prose_paras'] += 1
            tail_head = None

    def add_prose(t, new_para, num=None):
        nonlocal open_prose, open_gatha
        open_gatha = None
        if num is not None:
            # A NUMBERED PROSE PARAGRAPH INSIDE ANOTHER UNIT'S BLOCK — a
            # printed unit the corpus spliced or dropped.  It has no ordinal of
            # its own, so it cannot carry the number the reader hangs beside a
            # paragraph, and `fmtText` STRIPS a leading "NN." because that is
            # how every other paragraph number reaches it.  This shape carries
            # the number explicitly and `proseOne` draws it as a .pn.
            after.append({'n': num, 't': t})
            rec['prose_paras'] += 1
            open_prose = True
            return
        tail = after[-1] if after else None
        prev = (tail if isinstance(tail, str)
                else tail.get('t') if isinstance(tail, dict) and 't' in tail
                else None)
        # A LINE-END HYPHEN IS NEVER A PARAGRAPH BOUNDARY.  39Abhi11 p76 sets a
        # parenthetical whose every line is INDENTED, so each read as a new
        # paragraph — including "…dassanenapahātabbahetukaduka-" and its
        # continuation "sadisā." — and the compound came out as two words in
        # two blocks.  The hyphen settles it: it is a word split across lines,
        # the same reason the body gate rejoins them before comparing.
        if prev is not None and prev.endswith('-'):
            new_para = False
        if new_para or not open_prose or prev is None:
            after.append(t)
            rec['prose_paras'] += 1
            open_prose = True
            return
        joined = hyjoin(prev, t)
        if isinstance(tail, str):
            after[-1] = joined
        else:
            tail['t'] = joined

    for _ix, it in enumerate(items):
        # !!! AN UNNUMBERED CORPUS PROSE PARAGRAPH IS AN ANCHOR, exactly as a
        # numbered unit is.  It opens here, so the headings printed above it
        # land in ITS `sections` entry and are drawn above IT -- carried
        # forward to the book's first numbered unit they were drawn below 26
        # pages of text they head.  (2026-07-27ah, reversing 2026-07-27v.)
        _uo = unnum_at.get(_ix)
        if _uo is not None:
            flush()
            prev = cur
            cur = _uo
            after, groups = [], []
            open_prose = False; open_gatha = None
            if not opened:
                opened = True
                if pend_open:
                    sections[str(cur)] = pend_open
                    pend_open = []
                pend_heads, pend_centre = [], []
            elif pend_centre:
                uddana.setdefault(str(prev if prev is not None else cur),
                                  []).extend(pend_centre)
                pend_centre = []
            if pend_heads:
                sections.setdefault(str(cur), []).extend(pend_heads)
                pend_heads = []
            if pend_before:
                for b in pend_before:
                    if isinstance(b, dict):
                        b.pop('_open', None)
                before_of[cur] = list(pend_before)
                pend_before = []
            pend_seq = []
            for _si in unspan.get(_uo, ()):
                # a printed heading the extraction did not break on, so it
                # sits INSIDE this paragraph.  It cannot be drawn where the
                # page sets it; it is drawn above the paragraph it opens and
                # the divergence is recorded (`unnum_spanning`).
                _sl = items[_si][1].strip()
                sections.setdefault(str(cur), []).append(
                    {'l': _sl, 'k': head_kind(_sl)})
                rec['heads'].append({'pg': items[_si][2], 'l': _sl,
                                     'spanning': True})
        if _ix in suppress:
            continue                    # the corpus holds this line
        kind = 'vline' if _ix in reclass else it[0]
        if kind == 'homage':
            # ANCHOR THE HOMAGE TO THE FIRST VISIBLE ORDINAL, NOT TO o0.
            # 37Abhi09's ord0 and ord1 are leaked headings and therefore HIDDEN,
            # and a side-map anchored to a hidden paragraph is skipped by both
            # block() and render_parts — so the volume's own homage silently
            # never rendered.  Same shape as the uddāna anchoring bug that lost
            # "Paṭisambhidākathā niṭṭhitā." on 26Khu09.
            incipit[str(next((_o for _o in range(o0, o1)
                              if str(_o) not in hide), o0))] = it[1].strip()
            continue
        if kind not in ('unit', 'uverse') and it[1].strip() in titlestack:
            continue                       # the title page's own stack
        # A HEADING WITH NO NUMBERED UNIT OF ITS OWN.  `pend_heads` /
        # `pend_before` exist for the ordinary case — a heading, a line or two
        # of intro prose, then that section's first unit — and they attach
        # everything to the NEXT unit.  28Khu11 breaks that twice: the
        # Dhutaṅgapañha (printed 330-347) and the Opammakathā mātikā
        # (printed 348-353) are each headed, run for many pages, and carry no
        # numbered unit at all, so 489 printed lines were piling up in ord194's
        # `before` — rendered as 489 one-line paragraphs BELOW a stack of five
        # headings that the page sets in two groups far apart.
        # The tell that a heading has no unit is that a COLOPHON arrives while
        # it is still pending: a colophon closes a section, so the section is
        # over and no unit came.  At that point the heading and its text belong
        # to the PREVIOUS unit's uddāna stream, which the reader draws after
        # that paragraph — i.e. exactly where the page sets them — and which
        # `render_parts` models in full, so nothing leaves the body gate's
        # sight.  A later heading closes the stream again, because it may still
        # be the heading of the next unit.
        if (kind in ('colo', 'udd') and pend_heads and not tail_open
                and SPEC[VOL].get('orphan_sections')):
            # Replayed from `pend_seq`, which is the ONLY record of the printed
            # ORDER between the two: 28Khu11 p115 sets "Ācariyaguṇa", its
            # prose, then "Upāsakaguṇa" and its prose, and replaying
            # pend_heads then pend_before put both headings above both
            # paragraphs — so the first heading lost its own text to the
            # second.
            for k2, x in pend_seq:
                tail_add(k2, x, it[2])
            pend_heads, pend_before, pend_seq = [], [], []
            tail_open = True
        if tail_open and kind == 'head' and not last:
            tail_open = False
        if last and kind == 'head':
            tail_open = True
        # ONLY ONCE A HEADING HAS OPENED A TRAILING SECTION.  Plain prose after
        # the last unit already belongs to that unit's `after` and renders
        # correctly there — 26Khu09 and 27Khu10 both end that way, and
        # diverting it would move two shipped volumes for nothing.  What had
        # nowhere to go is material under a heading printed after the last
        # unit, because a heading is only ever attached to the NEXT unit.
        if tail_open and kind in ('head', 'vline', 'popen', 'pcont', 'cand'):
            # Material the page sets after a heading that has no numbered unit,
            # and everything after the book's last unit.  It goes into the
            # uddāna stream anchored to the current unit, IN PRINTED ORDER,
            # because `block()` draws uddāna blocks after `before`/`groups`/
            # `after` — which is exactly where the page sets them.
            if kind == 'head':
                for part in split_centre(it[1].strip()):
                    tail_add('head', part, it[2])
            else:
                tail_add(kind, it[1], it[2])
            continue
        if kind == 'head':
            # TWO HEADINGS CAN SHARE ONE PRINTED LINE, as they do in 19Khu02.
            # p351 sets "7. Dhammacakkakathā        1. Saccavāra" — the kathā
            # and its first vāra — and the corpus captured that same line as a
            # paragraph (hidden above).  Left joined, the tree would gain a
            # kathā named after both.
            for part in split_centre(it[1].strip()):
                (pend_open if not opened else pend_heads).append(
                    {'l': part, 'k': head_kind(part)})
                if opened:
                    pend_seq.append(('head', part))
                rec['heads'].append({'pg': it[2], 'l': part})
            open_prose = False; open_gatha = None
            continue
        if kind in ('colo', 'udd'):
            if not opened:
                # A colophon printed before the book's first unit closes a
                # section that is itself before it, so it keeps its printed
                # place in `sections` rather than being carried forward.  It is
                # emitted as k:'gatha' — display material the corpus does not
                # hold, the mechanism 19Khu02's Nidānagāthā already uses — and
                # NOT as a heading class: the Netti's "Saṅgahavāro." closes its
                # section and would otherwise both look like a heading and be
                # picked up as a node by the nav builder.
                pend_open.append({'l': it[1].strip(), 'k': 'gatha'})
            elif kind == 'udd':
                pend_centre.append({'label': it[1].strip(), 'lines': [], 'app': []})
            else:
                pend_centre.append({'label': None, 'lines': [it[1].strip()], 'app': []})
            rec['colos'].append({'pg': it[2], 'l': it[1].strip()})
            open_prose = False; open_gatha = None
            continue
        if kind in ('unit', 'uverse'):
            if (it[1], it[3]) in missing_lead:
                # A printed unit the corpus does not hold (declared and checked
                # above).  It consumes no ordinal, and goes into the NEXT
                # unit's `before` so the page keeps its printed order.
                pend_before.append({'n': it[1], 't': it[2]})
                pend_seq.append((kind, it[2]))
                rec['prose_paras'] += 1
                continue
            if (it[1], it[3]) in splice_lead:
                # A printed unit the corpus spliced into the preceding
                # paragraph.  No ordinal to consume, but NOT dropped: its
                # opening is emitted into the CURRENT unit's prose exactly as
                # the page sets it, number and all.
                add_prose(re.sub(r'^\d+\.\s*', '',
                                 splice_lead[(it[1], it[3])]),
                          True, num=it[1])
                continue
            flush()
            prev = cur
            cur = next(seq)
            units_done += 1
            last = units_done == len(pair_ords)
            after, groups = [], ([[it[2]]] if kind == 'uverse' else [])
            open_prose = False; open_gatha = None
            if not opened:
                # EVERYTHING PRINTED BEFORE THE BOOK'S FIRST UNIT goes into
                # `sections` in printed order, as the verse path already does.
                # The Netti opens with a whole section — the Saṅgahavāra's ten
                # gāthā between their heading and their colophon — before its
                # first numbered unit.  Folded into that unit's `before` they
                # would render as its intro prose, and the colophon that closes
                # them would render AFTER it, i.e. below text it precedes.
                opened = True
                if pend_open:
                    sections[str(cur)] = pend_open
                    pend_open = []
                pend_heads, pend_centre = [], []
            elif SPEC[VOL].get('head_order') and pend_seq:
                # PRINTED ORDER BETWEEN A HEADING, ITS PROSE, AND THE NEXT
                # HEADING — at a UNIT boundary.  36Abhi08 p92 sets "Tika", its
                # own text, "(Yathā hetumūlakaṁ…)", then "Adhipatiduka", then
                # the unit; replaying `pend_heads` and `pend_before` as two
                # lists put BOTH headings above BOTH paragraphs, so "Tika" lost
                # its text to "Adhipatiduka".  Same defect `pend_seq` already
                # fixed for 28Khu11, but that repair fires only on a COLOPHON
                # and here none comes.  Everything up to the LAST RUN OF
                # HEADINGS goes to the previous unit's uddāna stream, which
                # `block()` draws after that paragraph; only the trailing
                # headings stay in `sections`.  With the headings all at the
                # front the split point is 0 and nothing moves.
                j = len(pend_seq)
                while j and pend_seq[j - 1][0] == 'head':
                    j -= 1
                if j:
                    nh = len(rec['heads'])
                    for k2, x in pend_seq[:j]:
                        tail_add(k2, x, None)
                    if tail_head is not None:
                        pend_centre.append({'plain': True, 'head': tail_head,
                                            'hk': tail_hk, 'lines': [],
                                            'app': []})
                        tail_head = tail_hk = None
                    del rec['heads'][nh:]      # already recorded, not new
                    # POSITIONAL, NOT BY VALUE.  The trailing head-run is the
                    # LAST n entries of `pend_heads`; filtering by label kept
                    # every copy of a label occurring on both sides of the
                    # split.  38Abhi10 p341 sets "50. Parāmāsaduka
                    # 5. Saṁsaṭṭhavāra", prose, then "50. Parāmāsaduka
                    # 7. Pañhāvāra" — the value filter left the duka's name in
                    # `sections` TWICE and dropped "5. Saṁsaṭṭhavāra" from the
                    # page.  `check_layout.js` caught it; no content gate could.
                    keep = sum(1 for k2, _ in pend_seq[j:] if k2 == 'head')
                    pend_heads = pend_heads[len(pend_heads) - keep:] if keep else []
                    pend_before = []
                if pend_centre:
                    uddana.setdefault(str(prev if prev is not None else cur),
                                      []).extend(pend_centre)
                    pend_centre = []
            elif pend_centre:
                # ANCHOR TO THE PREVIOUS UNIT, NOT TO `cur - 1`.  A hidden
                # ordinal can sit between two units — 26Khu09's ord351 is the
                # leaked "7. Dhammacakkakathā  1. Saccavāra" line — and a
                # side-map block anchored to a hidden paragraph is skipped by
                # both block() and render_parts, so it silently never renders.
                # That is how "Paṭisambhidākathā niṭṭhitā." went missing.
                uddana.setdefault(str(prev if prev is not None else cur),
                                  []).extend(pend_centre)
                pend_centre = []
            if pend_heads:
                sections.setdefault(str(cur), []).extend(pend_heads)
                pend_heads = []
            if pend_before:
                for b in pend_before:
                    if isinstance(b, dict):
                        b.pop('_open', None)
                before_of[cur] = list(pend_before)
                pend_before = []
            pend_seq = []
            if kind == 'unit':
                add_prose(it[2], True)     # the unit's own opening paragraph,
            continue                       # already stripped of its number
        if kind == 'upada':
            # a pāda of a unit that is itself a gāthā
            if groups:
                _add_line(groups[0], it[1])
            continue
        if not opened:
            # display verse printed before the book's first unit — the Netti's
            # ten opening Saṅgahavāra gāthā.  `sections` entries may carry
            # k:'gatha', which is how 19Khu02's Nidānagāthā is placed.
            if pend_open and pend_open[-1]['k'] == 'gatha':
                pend_open[-1]['l'] += '\n' + it[1]
            else:
                pend_open.append({'l': it[1], 'k': 'gatha'})
            continue
        if cur is None or pend_heads:
            # ONE ENTRY PER PRINTED PARAGRAPH, not per printed LINE.  `before`
            # entries each render as their own block, so appending line by line
            # broke a section's intro prose into one-line paragraphs — and made
            # each of those lines a render block that has to match the print on
            # its own, which is why the reverse direction reported them.  The
            # same popen/pcont rule `add_prose` uses.
            if not SPEC[VOL].get('orphan_sections'):
                pend_before.append(it[1])
                continue
            pend_seq.append((kind, it[1]))
            if kind == 'vline':
                if (pend_before and isinstance(pend_before[-1], dict)
                        and pend_before[-1].get('_open')):
                    _add_line(pend_before[-1]['gatha'], it[1])
                else:
                    pend_before.append({'gatha': [it[1]], '_open': True})
                continue
            for b in pend_before:
                if isinstance(b, dict):
                    b.pop('_open', None)
            _tl = pend_before[-1] if pend_before else None
            _pv = (_tl if isinstance(_tl, str)
                   else _tl.get('t') if isinstance(_tl, dict) and 't' in _tl
                   else None)
            if (kind != 'popen' or (_pv is not None and _pv.endswith('-'))) \
                    and _pv is not None:
                _j = hyjoin(_pv, it[1])
                if isinstance(_tl, str):
                    pend_before[-1] = _j
                else:
                    _tl['t'] = _j
            else:
                pend_before.append(it[1])
            continue
        if (SPEC[VOL].get('head_order') and pend_centre and not tail_open
                and kind in ('popen', 'pcont', 'cand', 'vline')):
            # PROSE PRINTED BETWEEN TWO COLOPHONS.  36Abhi08 p110 closes the
            # Nissayavāra as colophon / "(Paccayattaṁ nāma nissayattaṁ…)" /
            # colophon.  `after` is drawn BEFORE the uddāna blocks that hold
            # the colophons, so that line jumped above both — printed order
            # lost though every word was present.  Once a colophon is queued
            # the unit is closed, so what follows joins the same stream.
            tail_add(kind, it[1], it[2])
            continue
        if kind == 'vline':
            # a line of an open centred block (an uddāna's own verse) belongs to
            # that block, not to the paragraph before it
            if pend_centre and pend_centre[-1].get('label'):
                _add_line(pend_centre[-1]['lines'], it[1])
                continue
            if open_gatha is not None:
                _add_line(open_gatha['gatha'], it[1])
            else:
                open_gatha = {'gatha': [it[1]]}
                after.append(open_gatha)
                rec['gathas'].append({'pg': it[2], 'l': it[1]})
            open_prose = False
            continue
        add_prose(it[1], kind == 'popen')

    flush()
    if tail_head is not None:
        pend_centre.append({'plain': True, 'head': tail_head, 'hk': tail_hk,
                            'lines': [], 'app': []})
    for b in pend_centre:
        b.pop('_verse', None)
        if b.get('plain') and b.get('head') is None:
            b.pop('head'); b.pop('hk', None)
    if pend_centre:
        uddana.setdefault(str(cur), []).extend(pend_centre)
    if pend_heads:
        report['unmapped'].append({'book': title, 'trailing_heads': pend_heads})
    if pend_before:
        report['unmapped'].append({'book': title, 'trailing_before': pend_before})


def build():
    pages = pdf_pages()
    paras = json.load(open(os.path.join(ROOT, 'site', VOL + '.json')))['paragraphs']
    verse, sections, uddana, hide, incipit = {}, {}, {}, {}, {}
    open_before = {}
    report = {'books': [], 'unmapped': [], 'leaked': []}

    for bk in SPEC[VOL].get('backmatter', []):
        # printed back matter the extraction captured as a corpus paragraph
        hide[str(bk)] = 1

    for bkspec in BOOKS:
        title, p0, p1, o0, o1, lastv = bkspec[:6]
        mode = bkspec[6] if len(bkspec) > 6 else 'verse'
        if mode == 'niddesa':
            nid_build(pages, paras, title, p0, p1, o0, o1,
                      verse, sections, uddana, incipit, report)
            continue
        if mode == 'katha':
            kat_build(pages, paras, title, p0, p1, o0, o1,
                      verse, sections, uddana, hide, incipit, report)
            continue
        if mode == 'heads':
            head_build(pages, paras, title, p0, p1, o0, o1,
                       verse, sections, uddana, hide, incipit, report)
            continue
        items = items_for(pages, p0, p1)
        # Corpus paragraphs whose TEXT is a printed heading (leaked into the
        # corpus).  This MUST run before the number map: a leaked heading carries
        # the heading's own ordinal as `n`, so 21Khu04's ord3138 ("10. …") sits
        # between verses 425 and 426 and fires a spurious vagga reset, desyncing
        # the per-vagga counter against the PDF for the rest of the book — that
        # alone left 293 verses unmapped.
        for o in range(o0, o1):
            t = head_body(re.sub(r'^\d+\.\s*', '',
                                 (paras[o].get('text') or '').strip()))
            if HEADTXT.match(t):
                hide[str(o)] = 1
                report['leaked'].append({'ord': o, 'text': (paras[o].get('text') or '').strip()})

        # Corpus verse-number -> ordinal.  Where `n` runs continuously over the
        # whole book a plain first-occurrence map is right.  In the Apadāna `n`
        # RESETS AT EVERY VAGGA, so the same number occurs ~56 times per book and
        # a plain map would collapse them all onto the first vagga; there the map
        # is keyed by (reset-index, n) and the PDF walk tracks the same counter.
        # In the JĀTAKA `n` resets per NIPĀTA, and the edition misprints three
        # verse numbers (ERRATA), one of which collides with a real verse in
        # the same nipāta.  So there the key is not the number at all: PDF
        # verse and corpus paragraph are paired BY POSITION within each
        # nipāta, and `n` is kept only as a cross-check (`ncheck`).  The
        # corpus's nipāta run comes from its `book` field — which flip-flops
        # with 'Jātakapāḷi', so only the '…nipāta' forms are read, the same
        # rule this project already needed for Aṅguttara and 19Khu02.
        scope = SPEC[VOL]['n_scope']
        per_vagga  = scope == 'vagga'
        per_nipata = scope == 'nipata'
        n2ord, seg = {}, 0
        prev = None
        nip_i, lastb = -1, None
        for o in range(o0, o1):
            if per_nipata:
                b = (paras[o].get('book') or '')
                if b.endswith('nipāta'):
                    if b != lastb:
                        nip_i += 1
                    lastb = b
            n = paras[o].get('n')
            if not isinstance(n, int) or str(o) in hide:
                continue
            if per_nipata:
                # A LIST, not a single ordinal, and consumed in printed order.
                # The edition misprints three verse numbers (ERRATA) and one of
                # them — 22Khu05 p304's "24." for 29 — repeats a number that
                # already occurs in the same nipāta.  Keeping every ordinal
                # that claims a number, and consuming them in order, places
                # both correctly; a single-value map silently dropped one.
                n2ord.setdefault((nip_i, n), []).append(o)
                continue
            if per_vagga and prev is not None and n <= prev:
                seg += 1
            prev = n
            key = (seg, n) if per_vagga else n
            if key not in n2ord:
                n2ord[key] = o

        pend_heads, pend_centre = [], []      # headings / colophons awaiting placement
        pend_open = []                        # printed-order material before verse 1
        pend_before = []                      # printed AFTER a heading, before its verse
        cur_ord, cur_groups, cur_after = None, [], []
        cur_nums = []              # printed number of each group, when >1
        cur_plain = None           # a spliced verse emitted as its own block
        vseen = set()
        opened = False
        pseg, pprev = 0, None      # PDF-side mirror of the per-vagga reset counter
        pnip = -1                  # PDF-side mirror of the per-nipāta counter
        merged = []                # printed verses the corpus SPLICED together
        paired_ct = 0              # printed verses placed on their own ordinal
        # A vagga's closing material — "<Name>vimānaṁ ekādasamaṁ." then
        # "Tassuddānaṁ" then the mnemonic verse — is set at the PĀDA indent, not
        # the centred indent, once it shares a page with verses.  Without this
        # flag those lines were appended to the last verse's groups, which is
        # exactly the splice the corpus itself makes (ord155/269/482/...).  So:
        # a centred COLOPHON or uddāna label opens a tail; everything in the body
        # column after it belongs to that tail until the next verse number.
        in_tail = False
        items_extra = []

        def flush():
            """close the current verse: write its groups + trailing prose."""
            if cur_ord is None:
                return
            e = {'groups': [g for g in cur_groups if g]}
            # Only a corpus paragraph holding MORE THAN ONE printed verse needs
            # per-group numbers; every other volume produces exactly one group,
            # so this never fires for them and their output stays byte-identical.
            if len(e['groups']) > 1 and len(cur_nums) == len(e['groups']):
                e['nums'] = list(cur_nums)
            if open_before.get(str(cur_ord)):
                e['before'] = open_before.pop(str(cur_ord))
            if cur_after:
                e['after'] = list(cur_after)
            # ...AND THE SAME FOR A RESIDUE LINE.  Under `udd_in_corpus` a
            # `before`/`after` line whose whole text is already a corpus
            # paragraph is dropped for the same reason a block line is: the
            # body draws it.  Measured over every volume's verse map, ONE line
            # corpus-wide is in that state (42KhuA23 ord1646's `before`, which
            # is corpus ord1645), so nothing else can move.
            if _cwhole:
                for _k in ('before', 'after'):
                    if _k not in e:
                        continue
                    _v = e[_k]
                    _xs = [_v] if isinstance(_v, str) else list(_v)
                    # THE WHOLE RESIDUE FIRST.  `before` is stored one printed
                    # LINE per entry, so a narrative that the corpus already
                    # holds as its own paragraph is not caught line by line —
                    # only its JOIN matches.  Every Jātaka volume is in this
                    # state and the body gate cannot see it, because each line
                    # occurs once in the printed stream and the corpus
                    # paragraph occurs once too.
                    _j = _cwhole.get(_sq(' '.join(x for x in _xs
                                                  if isinstance(x, str))))
                    if _j is not None and _j != cur_ord:
                        del e[_k]
                        continue
                    _xs = [x for x in _xs
                           if not (isinstance(x, str)
                                   and _cwhole.get(_sq(x), cur_ord) != cur_ord)]
                    if _xs:
                        e[_k] = _xs
                    else:
                        del e[_k]
            verse[str(cur_ord)] = e

        # A CENTRED LINE THAT IS ALREADY A WHOLE CORPUS PARAGRAPH IS BODY PROSE.
        # 42KhuA23 prints two narrative lead-ins ("Tato nāgarājā mahāsattaṁ
        # disvā gāthamāha–") immediately after a kaṇḍa colophon; the corpus
        # holds each as its own unnumbered paragraph AND the block absorbed the
        # printed line, so the reader drew both.  Measured over every volume's
        # uddāna map: 28 block lines are also a whole corpus paragraph, and the
        # corpus side is ALREADY HIDDEN in 26 of them — only these two are
        # drawn twice.  Hiding is not available here: 23Khu06 links to both
        # ordinals, and a hidden paragraph takes its links with it.  So the
        # block gives the line up and the corpus keeps it.  Gated per volume.
        _cwhole = {}
        if SPEC[VOL].get('no_reprint'):
            for _i in range(o0, o1):
                if str(_i) in hide:
                    continue          # a hidden paragraph draws nothing
                _k = _sq(paras[_i].get('text'))
                if _k and len(_k) > 25:
                    _cwhole.setdefault(_k, _i)

        def place_centre(blocks, after_ord):
            """colophons + uddāna verses render AFTER the previous paragraph."""
            if after_ord is None or not blocks:
                return
            if _cwhole:
                kept = []
                for b in blocks:
                    b = dict(b)
                    b['lines'] = [l for l in b.get('lines', [])
                                  if _cwhole.get(_sq(l), after_ord) == after_ord]
                    if b['lines'] or b.get('label') or b.get('head'):
                        kept.append(b)
                blocks = kept
                if not blocks:
                    return
            uddana.setdefault(str(after_ord), []).extend(blocks)

        for it in items:
            kind = it[0]
            if kind in ('pada', 'prose', 'centre') and it[1].strip() == title:
                # The book's own name, printed large above the homage.  It is set
                # at its own indent and so is not reliably classified as centred:
                # on 20Khu03 p21 it sits at indent 11 against a body column of 3
                # and was being swept into the opening gāthā block, where it
                # rendered small, italic and left-aligned instead of as a title.
                # The name is emitted by pipeline/build_booktitles.py into its own
                # side-map (booktitle/<VOL>.json), which every volume can have —
                # a sections file cannot be added to a volume that lacks one
                # without switching its heading path and losing its headings.
                continue
            if kind == 'verse':
                n, txt = it[1], it[2]
                if per_nipata:
                    lst = n2ord.get((pnip, n))
                    o_ = lst.pop(0) if lst else None
                    if o_ is None:
                        # No corpus paragraph claims this printed number.  The
                        # usual cause is a CORPUS SPLICE: two printed verses
                        # merged into one paragraph, with the second verse's
                        # own number left sitting inside the text
                        # ("…matoti. 109.Sobhati maccho Gaṅgeyyo…").  Confirm
                        # by CONTENT, not by the stray number — a footnote
                        # marker can imitate the number, but it cannot imitate
                        # the verse's opening words.
                        if cur_ord is not None and _spliced(paras[cur_ord], txt):
                            if pend_heads or pend_centre:
                                # The two spliced verses are NOT part of the
                                # same section — the edition prints a colophon
                                # and/or the next jātaka's heading between them
                                # (22Khu05 p80: v108, "Vīrakajātakaṁ
                                # catutthaṁ.", "205. Gaṅgeyyajātaka (2-6-5)",
                                # v109).  Folding v109 into v108's paragraph
                                # would render it ABOVE its own heading, so it
                                # goes out as its own numbered block instead,
                                # after the colophon and under its heading.
                                if pend_centre:
                                    place_centre(pend_centre, cur_ord)
                                    pend_centre = []
                                blk = {'plain': True, 'n': n, 'lines': [txt],
                                       'app': []}
                                if pend_heads:
                                    blk['head'] = pend_heads[0]['l']
                                    if len(pend_heads) > 1:
                                        sections.setdefault(str(cur_ord), [])
                                    pend_heads = []
                                place_centre([blk], cur_ord)
                                cur_plain = blk
                                merged.append({'n': n, 'ord': cur_ord,
                                               'pg': it[3], 'text': txt[:60],
                                               'own_block': True})
                                in_tail = False
                                continue
                            cur_groups.append([txt])
                            cur_nums.append(n)
                            cur_plain = None
                            merged.append({'n': n, 'ord': cur_ord, 'pg': it[3],
                                           'text': txt[:60]})
                            in_tail = False
                            continue
                        report['unmapped'].append({'book': title, 'n': n,
                                                   'pg': it[3], 'text': txt[:70]})
                        continue
                    flush()
                    o = o_
                    paired_ct += 1
                    if not opened:
                        opened = True
                        if pend_open:
                            sections[str(o)] = pend_open
                            pend_open = []
                        pend_heads, pend_centre = [], []
                    else:
                        if pend_centre:
                            place_centre(pend_centre, cur_ord)
                            pend_centre = []
                        if pend_heads:
                            sections[str(o)] = pend_heads
                            pend_heads = []
                    cur_ord, cur_groups, cur_after = o, [[txt]], []
                    cur_nums = [n]
                    cur_plain = None
                    if pend_before:
                        open_before[str(o)] = list(pend_before)
                        pend_before = []
                    in_tail = False
                    continue
                if per_vagga:
                    if pprev is not None and n <= pprev:
                        pseg += 1
                    pprev = n
                    vkey = (pseg, n)
                else:
                    vkey = n
                o = n2ord.get(vkey)
                if o is None or vkey in vseen:
                    report['unmapped'].append({'book': title, 'n': n, 'pg': it[3],
                                               'text': txt[:70]})
                    continue
                vseen.add(vkey)
                flush()
                if not opened:
                    # Everything printed between the book's title page and its
                    # first verse — title headings AND display verse such as
                    # Theragāthā's Nidānagāthā — goes into `sections` in printed
                    # order, so the page's own sequence survives.
                    opened = True
                    if pend_open:
                        sections[str(o)] = pend_open
                        pend_open = []
                    pend_heads, pend_centre = [], []
                else:
                    if pend_centre:
                        place_centre(pend_centre, cur_ord)
                        pend_centre = []
                    if pend_heads:
                        sections[str(o)] = pend_heads
                        pend_heads = []
                cur_ord, cur_groups, cur_after = o, [[txt]], []
                if pend_before:
                    open_before[str(o)] = list(pend_before)
                    pend_before = []
                in_tail = False
            elif kind in ('pada', 'prose'):
                if not opened:
                    if kind == 'pada' and pend_open and pend_open[-1]['k'] == 'gatha':
                        pend_open[-1]['l'] += '\n' + it[1]
                    else:
                        pend_open.append({'l': it[1], 'k': 'gatha'})
                elif pend_heads:
                    # same precedence as in the centred branch: a heading is open,
                    # so this is its opener and belongs to the heading's own verse,
                    # not to the previous section's closing block
                    pend_before.append(it[1])
                elif in_tail and pend_centre:
                    _add_line(pend_centre[-1]['lines'], it[1])
                elif cur_plain is not None and kind == 'pada':
                    # continuation pādas of a spliced verse that was emitted as
                    # its own block rather than folded into the paragraph
                    _add_line(cur_plain['lines'], it[1])
                elif kind == 'pada':
                    if cur_groups:
                        cur_groups[-1].append(it[1])
                elif cur_ord is not None:
                    # LINE-END HYPHENATION.  20Khu03 p342 sets
                    # "…imā gāthāyo abhi-" / "āsitthāti." — one word, hyphenated
                    # across the break.  Rejoin on the hyphen and nothing else:
                    # every wider rule also swallows ordinary wraps and then
                    # FABRICATES words ("abhiṇhaṁ" + "ovadatīti." ->
                    # "abhiṇhaṁovadatīti.").  The harness joins intra-word hyphens
                    # the same way, so the two agree.
                    prev = cur_after[-1] if cur_after else ''
                    if prev.endswith('-'):
                        cur_after[-1] = hyjoin(prev, it[1])
                    else:
                        cur_after.append(it[1])
            elif kind == 'homage':
                incipit[str(o0)] = it[1].strip()
            elif kind == 'centre' and len(split_centre(it[1])) > 1:
                for part in split_centre(it[1]):
                    items_extra.append(part)
                for part in items_extra:
                    if per_nipata and is_nipata_head(part):
                        pnip += 1
                        ppos = 0
                    pend_heads.append({'l': part, 'k': head_kind(part)})
                items_extra = []
            else:                                     # centre
                t = it[1]
                if t.strip() == 'Khuddakanikāya':
                    continue                          # series line above the title
                # A NIPĀTA heading opens a new verse-numbering segment.  This
                # is checked BEFORE the opened/not-opened split because the
                # book's FIRST nipāta head is printed on the title page, i.e.
                # while `opened` is still False — miss it there and every
                # nipāta index is off by one for the whole volume.
                if per_nipata and is_nipata_head(t):
                    pnip += 1
                    ppos = 0
                # A HEADING IS NOT ALWAYS NUMBERED.  25Khu08 sets three of them
                # bare — "Pārāyanavagga" over the whole book, and
                # "Pārāyanatthutigāthā" / "Pārāyanānugītigāthā" over its last
                # two sections, all three listed as sections in the edition's
                # own mātikā.  Testing only HEADNUM sent them down the colophon
                # path, where they rendered as centred closing material after
                # the PREVIOUS section instead of as that section's own title —
                # and, being present and contiguous, they passed the body gate
                # untouched.  Recognise a heading by CONTENT as well, as every
                # other part of this file already does.
                headish = HEADNUM.match(t) or HEADTXT.match(head_body(t))
                if not opened:
                    if UDDLBL.match(t):
                        pend_open.append({'l': t, 'k': 'vagga'})
                    elif headish:
                        pend_open.append({'l': t, 'k': head_kind(t)})
                    elif pend_open and pend_open[-1]['k'] == 'gatha':
                        pend_open[-1]['l'] += '\n' + t
                    else:
                        pend_open.append({'l': t, 'k': 'gatha'})
                    continue
                if UDDLBL.match(t):
                    pend_centre.append({'label': t, 'lines': [], 'app': []})
                    in_tail = True
                elif headish:
                    pend_heads.append({'l': t, 'k': head_kind(t)})   # heading: no tail
                elif pend_heads:
                    # A heading has been seen and its verse has not arrived yet, so
                    # this line is the section's OPENER, not the previous section's
                    # closing material: the page sets "Paccekabuddhāpadānaṁ
                    # samattaṁ." / "3-1. Sāriputtatthera-apadāna" / "Atha
                    # therāpadānaṁ suṇātha–".  Attaching it to the previous
                    # paragraph's uddāna block rendered it ABOVE its own heading.
                    pend_before.append(t)
                elif pend_centre and pend_centre[-1].get('label'):
                    _add_line(pend_centre[-1]['lines'], t)  # a line of the open uddāna
                    in_tail = True
                else:
                    pend_centre.append({'label': None, 'lines': [t], 'app': []})
                    in_tail = True
        flush()
        if pend_centre:
            place_centre(pend_centre, cur_ord)
        if pend_heads:
            report['unmapped'].append({'book': title, 'trailing_heads': pend_heads})
        rec = {'book': title, 'verses_mapped': len(vseen), 'expected': lastv}
        if per_nipata:
            # Self-verification, and the reason this scope is trustworthy: the
            # PDF's own nipāta headings must produce the same number of
            # segments as the corpus `book` field does, and every segment must
            # pair 1:1.  Both counts are reported so a drift is visible rather
            # than absorbed.
            rec['pdf_nipatas']    = pnip + 1
            rec['corpus_nipatas'] = nip_i + 1
            rec['expect_nipatas'] = SPEC[VOL].get('nipatas')
            rec['paired']         = paired_ct
            rec['merged']         = merged
            # Corpus paragraphs that claimed a verse number but that the PDF
            # walk never consumed.  Should be empty: a leftover means a printed
            # verse was missed, which is the failure this whole scope exists to
            # make visible rather than absorb.
            rec['unconsumed']     = sorted(o for v in n2ord.values() for o in v)
        report['books'].append(rec)

    # tidy: a block with neither lines nor head nor label holds nothing and is
    # dropped.  A block carrying a HEAD and no lines is kept — that is a
    # printed heading immediately followed by another heading, which is how
    # 28Khu11 sets "Meṇḍakapañhārambhakathā / Aṭṭhamantaparivajjanīyaṭṭhāna"
    # and "Ācariyaguṇa / Upāsakaguṇa".  This filter was silently deleting the
    # first of each pair.
    #
    # A block carrying a LABEL and no lines is kept too, and used not to be.
    # An uddāna label is a PRINTED LINE; it has no lines of its own only when
    # the verses it labels are not centred lines — either a numbered UNIT
    # (05Vin05 p171 "Samuṭṭhānassuddānaṁ", whose verses are unit 268) or an
    # uddāna the edition sets as PROSE, which the corpus absorbs into the
    # preceding paragraph (32Abhi04, 23 of them).  Dropping the block deleted
    # the printed label from the render.
    #
    # MEASURED over all 27 volumes in SPEC before the change (_udd_probe.py):
    # the shape occurs in exactly two volumes — 05Vin05 (1) and 32Abhi04 (24).
    # The other 25 are byte-identical.  It is invisible to the body gate
    # wherever the same label renders elsewhere in the volume: 32Abhi04 prints
    # "Tassuddānaṁ" 27 times and rendered 4, and read 0/0/0/0.
    for k in list(uddana):
        for b in uddana[k]:
            # internal markers, and a null head/weight on an ordinary block
            b.pop('_verse', None)
            if b.get('plain') and b.get('head') is None:
                b.pop('head', None); b.pop('hk', None)
        uddana[k] = [b for b in uddana[k]
                     if b.get('lines') or b.get('head') or b.get('label')]
        if not uddana[k]:
            del uddana[k]
    # EVERY DECLARED LITERAL MUST BE PRINTED.  A `headskip` entry that no page
    # carries is either a typo or a line the edition no longer sets, and either
    # way the list has stopped describing the volume.  Refuse rather than let
    # it rot.
    _hs = set(SPEC[VOL].get('headskip', ()))
    _unmet = sorted(_hs - HEADSKIP_SEEN)
    if _unmet:
        raise SystemExit('REFUSING: headskip literal(s) never met as a heading '
                         'in %s: %r' % (VOL, _unmet))
    _cs = set(SPEC[VOL].get('coloskip', ()))
    _unmetc = sorted(_cs - COLOSKIP_SEEN)
    if _unmetc:
        raise SystemExit('REFUSING: coloskip literal(s) never met as a '
                         'candidate colophon in %s: %r' % (VOL, _unmetc))

    return verse, sections, uddana, hide, incipit, report


def write(name, data):
    p = os.path.join(R, name, VOL + '.json')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p) and not os.path.exists(p + '.pre19build'):
        shutil.copy(p, p + '.pre19build')
    json.dump(data, open(p, 'w'), ensure_ascii=False)
    return p


if __name__ == '__main__':
    use(sys.argv[1])
    v, s, u, h, inc, rep = build()
    print('verse entries %d | sections %d | uddana anchors %d | hidden %d | incipits %d'
          % (len(v), len(s), len(u), len(h), len(inc)))
    for b in rep['books']:
        if b.get('mode') == 'katha':
            ok = not b.get('FATAL') and b['printed_units'] == b['corpus_paras']
            print('   %-22s KATHĀ  printed units %d / corpus ¶ %d   headings %d   '
                  'colophons %d   prose ¶ %d   gāthā blocks %d   [%s]'
                  % (b['book'], b['printed_units'], b['corpus_paras'],
                     len(b['heads']), len(b['colos']), b['prose_paras'],
                     len(b['gathas']), 'OK' if ok else 'CHECK'))
            if b.get('FATAL'):
                print('        FATAL:', b['FATAL'])
            for x in b.get('absent', ()):
                print('        CORPUS ABSENCE (recorded, not corrected): printed '
                      'unit %s at p%s is in NO corpus paragraph; rendered from '
                      'the printed page above the next unit — %r'
                      % (x['n'], x['pg'], x['text']))
            for x in b.get('splices', ()):
                print('        CORPUS SPLICE (recorded, not corrected): printed '
                      'unit %s at p%s is inside corpus ord%s, the paragraph of '
                      'unit %s — %r' % (x['n'], x['pg'], x['ord'], x['into'],
                                        x['text']))
            for x in b['nmismatch'][:20]:
                print('        N MISMATCH: printed %r at p%s pairs with corpus '
                      'ord%s whose n is %s' % (x['printed'], x['pg'], x['ord'],
                                               x['corpus_n']))
            if '--show' in sys.argv:
                for x in b['heads']:  print('        HEAD  p%-4s %s' % (x['pg'], x['l']))
                for x in b['colos']:  print('        COLO  p%-4s %s' % (x['pg'], x['l']))
                for x in b['gathas']: print('        GĀTHĀ p%-4s %s' % (x['pg'], x['l']))
            continue
        if b.get('mode') == 'niddesa':
            ok = (not b.get('FATAL')
                  and b['printed_lemmas'] == b['corpus_paras'])
            print('   %-18s NIDDESA  printed lemmas %d / corpus ¶ %d   '
                  'headings %d   colophons %d   prose ¶ %d   gāthā blocks %d   [%s]'
                  % (b['book'], b['printed_lemmas'], b['corpus_paras'],
                     len(b['heads']), len(b['colos']), b['prose_paras'],
                     b['gatha_blocks'], 'OK' if ok else 'CHECK'))
            if b.get('FATAL'):
                print('        FATAL:', b['FATAL'])
            for x in b['nmismatch']:
                print('        EDITION MISPRINT (preserved): printed %r at p%s '
                      'pairs with corpus ord%s whose n is %s'
                      % (x['printed'], x['pg'], x['ord'], x['corpus_n']))
            if '--show' in sys.argv:
                for x in b['heads']: print('        HEAD  p%-4s %s' % (x['pg'], x['l']))
                for x in b['colos']: print('        COLO  p%-4s %s' % (x['pg'], x['l']))
            continue
        if 'pdf_nipatas' in b:
            ok = (b['pdf_nipatas'] == b['corpus_nipatas'] == b['expect_nipatas']
                  and not b['unconsumed'])
            print('   %-12s nipātas pdf %d / corpus %d / expected %s   '
                  'verses paired %d   corpus splices repaired %d   '
                  'corpus ¶ never matched %d   [%s]'
                  % (b['book'], b['pdf_nipatas'], b['corpus_nipatas'],
                     b['expect_nipatas'], b['paired'], len(b['merged']),
                     len(b['unconsumed']), 'OK' if ok else 'CHECK'))
            for x in b['merged']:
                print('        SPLICE: printed verse %s (p%s) was merged into corpus ord%s — %r'
                      % (x['n'], x['pg'], x['ord'], x['text']))
            if b['unconsumed']:
                print('        UNCONSUMED corpus ordinals:', b['unconsumed'][:20])
            continue
        if b.get('mode') == 'heads':
            # THE FOURTH READER REPORTS WHAT IT LOCATED AND WHAT IT DID NOT.
            # `untouched_visible` is the number that matters: a corpus
            # paragraph the printed stream never confirmed AND that is not a
            # homage, heading or colophon drawn from the print instead.
            print('   %-28s HEADS  printed lines %5d / located %5d   residue %3d   '
                  'corpus ¶ %4d   headings %4d   colophons %4d   '
                  'unconfirmed ¶ %d   [%s]'
                  % (b['book'], b['printed_lines'], b['located'], b['residue'],
                     b['corpus_paras'], len(b['heads']), len(b['colos']),
                     len(b['untouched_visible']),
                     'FATAL' if b.get('FATAL') else 'OK'))
            if b.get('FATAL'):
                print('        FATAL:', b['FATAL'])
            for x in b['untouched_visible'][:8]:
                print('        UNCONFIRMED ord%-4d %r' % (x['ord'], x['text']))
            if b['unanchored_heads']:
                print('        HEADINGS NEVER ANCHORED:', b['unanchored_heads'][:6])
            continue
        print('   %-20s verses mapped %d%s' % (b['book'], b['verses_mapped'],
              (' / %d' % b['expected']) if b['expected'] else ' (n resets per vagga; no book-level total)'))
    print('   leaked corpus headings hidden: %s' % [x['ord'] for x in rep['leaked']])
    if rep['unmapped']:
        print('   UNMAPPED (%d):' % len(rep['unmapped']))
        for x in rep['unmapped'][:15]:
            print('     ', x)
    # A BOOK'S TITLE PAGE BELONGS ABOVE THAT BOOK'S FIRST PARAGRAPH.
    #
    # `build_booktitles.py` keys the stack by a page estimate, and that key can
    # be BOTH misplaced and invisible: 39Abhi11's second title page was keyed
    # to ord654 — six paragraphs before the book it heads even begins, and
    # itself a hidden leaked heading — so the stack never rendered at all.
    # This is the only place that knows both the book boundaries and what is
    # hidden, so the map is aligned here and every move is REPORTED.
    #
    # It refuses unless there is exactly one entry per book, which is the only
    # case where the i-th stack heads the i-th book without guessing.
    _bt = os.path.join(R, 'booktitle', VOL + '.json')
    _btd = None
    if os.path.exists(_bt):
        _old = json.load(open(_bt, encoding='utf-8'))
        _firsts = [next((_o for _o in range(_bs[3], _bs[4])
                         if str(_o) not in h), _bs[3]) for _bs in BOOKS]
        _keys = sorted(_old, key=int)
        if len(_keys) == len(_firsts):
            _new = {}
            for _k, _f in zip(_keys, _firsts):
                if int(_k) != _f:
                    print('   BOOKTITLE re-keyed: ord%s -> ord%d (that book\'s '
                          'first visible paragraph)' % (_k, _f))
                _new[str(_f)] = _old[_k]
            if _new != _old:
                _btd = _new
        else:
            # FEWER STACKS THAN BOOKS — read the missing ones off the page.
            # `build_booktitles.py` found 9 of 40Abhi12's 20 title pages, so
            # eleven books would have rendered with no title at all.  The
            # edition states each one plainly: the centred lines above the rule
            # on that book's first page, with the homage removed.  Derived from
            # the printed page and REPORTED line by line, never invented.
            _new = {}
            for _bs, _f in zip(BOOKS, _firsts):
                _st = []
                for _l in pdf_pages()[_bs[1] - 1].split('\n'):
                    _t = _l.strip()
                    if not _t:
                        continue
                    if set(_t) <= set('_ ') or HOMAGE.search(_t):
                        break
                    _st.append(_t)
                # A STACK OF ONE IS A STACK.  This wanted two lines because
                # 40Abhi12's twenty title pages all set the naya above the
                # book name; 02Vin02's SECOND title page sets only
                # "Bhikkhunīvibhaṅga", without repeating "Vinayapiṭaka" above
                # it.  Refused, the derivation aborted for the WHOLE volume,
                # so that book had no title stack at all — and because
                # `kat_build` filters the title line out of the body on the
                # understanding that `booktitle/` will draw it, the line
                # vanished from the page entirely.  The body gate is what
                # found it: one PDF line missing.
                if len(_st) < 1 or len(_st) > 4:
                    print('   BOOKTITLE NOT derived for %r: its first page does '
                          'not open with a title stack (%r)' % (_bs[0], _st[:4]))
                    _new = None
                    break
                _new[str(_f)] = _st
            if _new is not None and _new != _old:
                print('   BOOKTITLE derived from the printed title pages: %d '
                      'stack(s) for %d book(s) (the map held %d)'
                      % (len(_new), len(_firsts), len(_keys)))
                for _k in sorted(_new, key=int):
                    print('        ord%-6s %s' % (_k, ' / '.join(_new[_k])))
                _btd = _new
    if '--write' in sys.argv:
        for n, d in (('verse', v), ('sections', s), ('uddana', u), ('hide', h), ('incipit', inc)):
            print('  wrote', write(n, d))
        if _btd:
            print('  wrote', write('booktitle', _btd))
    else:
        print('DRY RUN — pass --write to save')
