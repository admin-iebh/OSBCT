#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Navs for the Majjhima-Aṭṭhakathā (Papañcasūdanī), 10MaA01-13MaA04.

!!! THE MAJJHIMA COMMENTARY DOES NOT TAKE THE DĪGHA'S TOPS, AND THE BUILDER
REFUSED UNTIL IT WAS TOLD SO.  The rule this layer has followed since the
Vinaya block — a commentary book takes its structure from the text it comments
on — still holds; what changed is the text.  The three Dīgha volumes comment on
a nikāya whose SUTTAS are the top level, so `re:\\d+\\.\\s+.*sutta$` was right
there.  10Ma02 is five VAGGAS of ten suttas each, so here the top level is the
vagga and the suttavaṇṇanās hang beneath it:

    1. Gahapativagga                          <- top
        1. Kandarakasuttavaṇṇanā              <- depth 1
        4. Potaliyasuttavaṇṇanā
            Kāmādīnavakathāvaṇṇanā            <- depth 2, the sub-kathā
    2. Bhikkhuvagga
        ...

Three levels, and the third is not decoration: the volume prints exactly one
sub-kathā (`Kāmādīnavakathāvaṇṇanā`, 0-based p36) and the printed mātikā sets
it unnumbered and indented under the Potaliyasutta, which is where it belongs.

10MaA01 and 11MaA02 are absent until their corpora are rebuilt: 10MaA01 opens
with an unnumbered Ganthārambha (printed pp18-40 hold no corpus text at all,
though its first paragraph is ANCHORED to p18 — an anchor is not coverage), and
11MaA02 has a six-page hole in the middle at printed pp311-316.  Scouted
2026-07-27ah.
"""
import build_abhidhamma_nav as A

WORK = 'Majjhima — Papañcasūdanī + subcommentaries'
VAGGA = r're:\d+\.\s+.*vagga$'
VANNANA = r're:\d+\.\s+.*vaṇṇanā$'

MAJJHIMA_A = {
 # --- 10MaA01: the preface stands ABOVE the vagga structure ----------------
 # Its corpus was rebuilt on 2026-07-27ai to recover the Ganthārambhakathā and
 # Nidānakathā — printed pp1-29, which no corpus held.  So its tops cannot be
 # the bare vagga pattern its three neighbours use: they are the two named
 # preface heads and THEN the vaggas, exactly as 07DiA01's are the two named
 # heads and then the thirteen suttas.  The rule underneath is unchanged; the
 # preface simply sits above the structure, as it does in 01VinA01 too.  The
 # printed mātikā states this itself (0-based p13): `Ganthārambhakathā` and
 # `Nidānakathā` are set at the same margin as the CENTRED `1. Mūlapariyāyavagga`
 # that follows them, not indented under it.
 '10MaA01': {
   'title': 'Mūlapaṇṇāsaṭṭhakathā (Paṭhamo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (13, 16),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   # !!! `tops` CANNOT MIX A LITERAL WITH A PATTERN.  `subtree` reads a `re:`
   # top only when `tops` is a list of ONE — "or a single 're:' PATTERN when
   # the top level is an open set" — so `['Ganthārambhakathā', 'Nidānakathā',
   # VAGGA]` silently made the two vaggas children of the Nidānakathā and the
   # builder REFUSED on the order check.  The vaggas are therefore NAMED, as
   # 07DiA01's thirteen suttas are, which costs nothing: this bhāga carries
   # exactly two of them.  Do not widen `subtree` for this — it feeds every
   # volume's tree.
   'tops': ['Ganthārambhakathā', 'Nidānakathā',
            '1. Mūlapariyāyavagga', '2. Sīhanādavagga'],
   'levels': [None, [VANNANA], [r're:.']],
 },
 # --- 11MaA02: three vaggas, and a mātikā the reader mis-reads by ONE line --
 # Its corpus was rebuilt on 2026-07-27ai for a SIX-PAGE HOLE IN THE MIDDLE
 # (printed pp311-316), the first volume in the layer whose gap was not at an
 # edge.  Its tops are the plain vagga pattern — it carries no preface, which
 # is 10MaA01's; this is the second bhāga and opens straight at `3. Opammavagga`.
 #
 # !!! `matika_drop` FOR THE TITLE STACK.  `matika_headers` identifies a
 # mātikā's running header as "a line that opens three or more of its pages",
 # and this mātikā is TWO pages, so the rule can never fire and `Dutiyabhāga` —
 # the second line of the title stack on its first page — entered the entry
 # list.  One unresolvable entry is enough to make `matika_gate` unusable.
 # I tried the general rule the page seems to state — nothing above the
 # `Mātikā … Piṭṭhaṅka` column head is an entry — and MEASURED it over every
 # volume that declares a mātikā (`_maa02/matkolumn.py`): it is NOT safe.  It
 # removes 31 entries across the layer and several are REAL, printed above the
 # column head on their page: 33Abhi05's five book heads and four
 # `1. Paṇṇattivāra-uddesa`, 37Abhi09's four `2. Paccayapaccanīya
 # 1. Vibhaṅgavāra` pair-lines, 15An01's three `1. Paṭhamapaṇṇāsaka`; and
 # 16An02 GAINS one.  So the line is NAMED here instead, which is what
 # `matika_drop` is for.  (38Abhi10 carries the same `Tatiyabhāga` artefact and
 # is `matika_gate: False`, so it has never been visible there.)
 '11MaA02': {
   'title': 'Mūlapaṇṇāsaṭṭhakathā (Dutiyo bhāgo)',
   'work': WORK,
   'first': 0,
   'matika': (3, 4),
   # BOTH lines of the stack, because the `fold(title) in fold(t)` filter that
   # normally removes the first one cannot see it here: this node is labelled
   # with its BHĀGA, as the standing rule requires, so `fold(title)` is
   # `mūlapaṇṇāsaṭṭhakathādutiyobhāgo` and the printed line is bare
   # `Mūlapaṇṇāsaṭṭhakathā`.  10MaA01 carries the same title-with-bhāga and is
   # unaffected only because ITS mātikā runs four pages, so the running-header
   # rule reaches it.
   'matika_drop': ('Mūlapaṇṇāsaṭṭhakathā', 'Dutiyabhāga'),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': [VAGGA],
   'levels': [None, [VANNANA], [r're:.']],
 },
 '12MaA03': {
   'title': 'Majjhimapaṇṇāsaṭṭhakathā',
   'work': WORK,
   'first': 0,
   # THE MĀTIKĀ IS A GATE HERE, WHICH IT IS NOT IN THE DĪGHA COMMENTARY.
   # 0-based pp3-5 print a plain ordered list of this volume's own body
   # headings — five centred vagga heads and 51 dotted entries — and after the
   # `colofix`/`headskip` roles were settled it is IDENTICAL, entry for entry
   # and in order, to the built heads stream (56/56, `_maa03/matdiff.py`).
   # Before that the stream carried 108.  So this volume can afford the
   # stronger setting: every mātikā entry must resolve in the tree, and every
   # centred group head with it.
   'matika': (3, 5),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': [VAGGA],
   'levels': [None, [VANNANA], [r're:.']],
 },
 # --- 13MaA04: the same three levels, and the mātikā states the depth --------
 # Its mātikā expresses depth by INDENT, which settles two questions the
 # 12MaA03 mātikā never raised:
 #   * the seven `…ratanavaṇṇanā` sub-kathās under `9. Bālapaṇḍitasuttavaṇṇanā`
 #     (0-based p4) are set at indent 7 where the numbered entries sit at 1, so
 #     they are one level DEEPER — the third level, which is what it is for;
 #   * `Nigamanakathā` (p5) is set at the NUMBERED entries' own text column,
 #     not deeper, so it is a SIBLING of the suttavaṇṇanās and not a child of
 #     the last one.  It carries no number, so it has to be named at level 1 or
 #     the `re:.` leaf would take it a level too deep.
 '13MaA04': {
   'title': 'Uparipaṇṇāsaṭṭhakathā',
   'work': WORK,
   'first': 0,
   'matika': (3, 5),
   'matika_gate': True,
   'matika_centred_gate': True,
   'level_memo': True,
   'tops': [VAGGA],
   'levels': [None, [VANNANA, 'Nigamanakathā'], [r're:.']],
 },
}

A.SPEC.update(MAJJHIMA_A)
A.main()
