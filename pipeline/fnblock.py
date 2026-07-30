#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Where a printed page's FOOTNOTE BLOCK starts when its RULE IS A GRAPHIC.

The edition separates body from apparatus with a horizontal rule.  pdftotext
emits it as a line of underscores on almost every page, and `_{10,}` is how all
three consumers find it: `build_khu_volume.page_lines` cuts the page there,
`verify_render_vs_pdf.pdf_lines` stops the body comparison there, and
`rebuild_apparatus.page_notes` parses the block below it.

On FOURTEEN pages of the corpus the rule is drawn as a GRAPHIC and pdftotext
emits no text line for it.  All three then behave as though the page had no
apparatus at all: the cells fall through into the BODY stream — where four of
them have been read as centred HEADINGS (05Vin05) and three more as body text
(03Vin03 p340) — and `page_notes` returns `{}, []`, so those variant readings
are stored NOWHERE.  Cutting them out of the body without this module would
delete printed text from the edition.

MEASURED OVER ALL 118 VOLUMES, not inferred:

    05Vin05   0-based 51 54 67 110 119 121 140 330 331 382   (10)
    03Vin03   0-based 340                                    ( 1)
    07Di02    0-based 154 155 157                            ( 3)

and nothing else anywhere.  The LOOSE test — any trailing run of cell-shaped
lines on a rule-less page — fires on 95 pages in 37 volumes; the other 81 are
numbered BODY units ("145. Yattha rūpakkhandho nirujjhittha -pa-.",
"12. Payogappaṭippassaddhipaññā phale ñāṇaṁ.").  What separates a footnote
block from them is the VARIANT SIGLUM: at least one cell ends in `(Sī)`,
`(Ka)`, `(Sī, Syā)`, `(?)` or carries `piṭṭhe`.  That is the whole test, and it
is a MEASUREMENT — re-run `_fnprobe/scan_all.py` if the siglum list changes.

IT REFUSES RATHER THAN GUESSES.  Where the block's cells are NUMBERED, every
number must be matched by a footnote MARKER printed in the body above it
(`samatittikaṁ1`, `uccāraṁ2`, `uyyokhajja3`) — 12 of the 14 are backed that
way.  The other 2 are xref-only lines (`* Vi 5. 287 piṭṭhepi.`) which carry no
number to back.  A block with the siglum evidence but WITHOUT the marker
backing is REPORTED and NOT cut, so an unmeasured page falls back to the
status quo visibly instead of being cut on a guess.

INERT BY CONSTRUCTION: `fn_start` returns None the moment the page carries a
`_{10,}` line, so every rule-bearing page in the corpus is untouched.

Works on both `pdftotext -layout` (a two-column block sets several cells on one
line, split on wide gaps) and plain `pdftotext` (each cell arrives on its own
line), because the builder reads the one and the body gate the other.
"""
import re, sys

RULE = re.compile(r'_{10,}')

# Extends rebuild_apparatus.SIGLA with the two forms this edition also prints
# inside Vinaya cells.  Adding to this list LOOSENS the test — re-measure.
SIGLA = ('Sī', 'Syā', 'Kaṁ', 'Kaṃ', 'Ka', 'I', 'Ṭṭha', 'Niddesa', 'Itipi',
         'Sārattha', 'sabbattha', 'bahūsu', 'katthaci', 'sabbatthapi', r'\?')
_SIG = '(?:' + '|'.join(SIGLA) + ')'
SIGTAIL = re.compile(r'\(' + _SIG + r'(?:,\s*' + _SIG + r')*\)\s*$')
# `piṭṭhe` is evidence only inside a CROSS-REFERENCE cell.  Unanchored it also
# matches `33 (ādipiṭṭhesu)` in the printed WORD INDEX, and on its first run
# that would have cut three commentary volumes' index pages (36KhuA17 p594,
# 37KhuA18 p458, 38KhuA19 p579).  The marker backing refused all three anyway;
# this removes them at source, so the two defences stay independent.
XREFPI = re.compile(r'piṭṭhe')

# A cell opens with its marker: "1.", "1-1.", or the "*"/"+" of a cross-reference.
CELL = re.compile(r'^(?:\d+(?:-\d+)?\.?|\*|\+)\s')
XREF = re.compile(r'^[*+]\s')

# The marker as rebuild_apparatus reads it: digits welded to the end of a word
# or to closing punctuation, never a paragraph number (which has space before).
MARK = re.compile(r'(?<=[^\W\d_.)\]”])(\d+)(?!\d)|(?<=[.)\]”])(\d+)(?!\d)')


def _evidence(cell):
    """Does this cell prove the block is an apparatus and not numbered body?"""
    return bool(SIGTAIL.search(cell)) or bool(XREF.match(cell) and XREFPI.search(cell))


def _cells(line):
    return [c.strip() for c in re.split(r'\s{3,}', line.strip()) if c.strip()]


def fn_start(lines, where='', warn=sys.stderr):
    """Index into `lines` of the first FOOTNOTE line, or None.

    `lines` is one page's raw lines, as split from pdftotext output.  None means
    "no graphic-rule block here" — either the page prints its rule (and the
    caller's own `_{10,}` search is authoritative) or there is no apparatus.
    """
    idx = [i for i, l in enumerate(lines) if l.strip()]
    if not idx:
        return None
    if any(RULE.search(lines[i]) for i in idx):
        return None                      # the rule is TEXT: nothing to do here

    # walk up from the foot of the page while the lines are cell-shaped
    run = []
    for i in reversed(idx):
        cs = _cells(lines[i])
        if not cs or not all(CELL.match(c) for c in cs):
            break
        run.insert(0, i)
    if not run:
        return None

    cells = [c for i in run for c in _cells(lines[i])]
    if not any(_evidence(c) for c in cells):
        return None                      # numbered BODY units, not an apparatus

    nums = [int(m.group(1)) for c in cells
            for m in [re.match(r'^(\d+)', c)] if m and not XREF.match(c)]
    if nums:
        body = '\n'.join(lines[i] for i in idx if i < run[0])
        marks = {int(m.group(1) or m.group(2)) for m in MARK.finditer(body)}
        missing = sorted(set(nums) - marks)
        if missing:
            print(f'fnblock: {where}: siglum evidence but marker(s) {missing} '
                  f'not printed above — NOT cut', file=warn)
            return None
    return run[0]
