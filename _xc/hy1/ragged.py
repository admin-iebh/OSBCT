# -*- coding: utf-8 -*-
"""RAGGED vs JUSTIFIED inside a block the page sets apart.

`display` says the page sets a block apart from running prose.  It does NOT say
whether the block's internal line breaks are structural.  Two shapes wear it:

  STANZA / MATIKA LIST -- every line is the edition's own; the breaks must survive.
  BLOCK QUOTATION -- indented as a whole but internally WRAPPED to the measure;
      the breaks are typography and joining them is correct.

Telling them apart needs TWO signals, because each has a case the other misses.

 1. THE RIGHT EDGE, against the VOLUME's prose measure -- not the block's own
    widest line, and not the page's.
      * Block's own max: a stanza's longest pada defines the edge and its three
        siblings sit within tolerance, so every stanza came out justified and
        all four control cases failed.
      * Per page: fails on a page carrying no prose at all -- 29Abhi01 p14 is
        fourteen matika dyads, 35Abhi07 p74 is one hanging stack -- and the
        fallback then measures the LIST.  Third time a page-level statistic has
        failed for want of its reference class on that page; see `vol_margin`
        in adjudicate.py and the body-leading mode in blockmap.py.
      Measured: 20KhuA01 p233 stanza lines end at 298-342 against a volume
      measure of 411; 34KhuA15 p51's quoted prose ends at 367-434.

 2. THE LINE ENDING.  A wrapped line ends mid-sentence; a structural one ends at
    a boundary.  35Abhi07 p74's matika items run 346-407 against a measure of
    411 -- half of them "full" by width -- and every one ends in a full stop.

Neither alone is sufficient: width alone misjudges that matika, and the ending
alone misjudges 06ViT06 p28, whose pada ends in a line-break hyphen.  JUSTIFIED
requires both -- the lines reach the measure AND do not end at a boundary.

The last line of any block is short in both shapes and is excluded.
"""
import statistics

TOL = 25.0
MINFULL = 0.50
MAXTERM = 0.50
TERM = ('.', ',', ';', ':', '?', '!', '–', '—', '”', '’', ')')

_MEASURE = {}


def vol_measure(vol, BL, judge_page, margin):
    """The right edge running PROSE reaches, over the WHOLE VOLUME."""
    if vol in _MEASURE:
        return _MEASURE[vol]
    xs = []
    for pg, pd in BL.items():
        for k, b in judge_page(pd, margin)[2]:
            if k == 'prose':
                xs += [l[4] for l in b[:-1]]
    _MEASURE[vol] = statistics.median(xs) if len(xs) >= 20 else None
    return _MEASURE[vol]


def block_shape(b, edge):
    """'ragged' | 'justified' | None (cannot judge)."""
    if edge is None or len(b) < 2:
        return None
    body = b[:-1]
    full = sum(1 for l in body if l[4] >= edge - TOL) / len(body)
    term = sum(1 for l in body if (l[3] or '').rstrip()[-1:] in TERM) / len(body)
    return 'justified' if (full >= MINFULL and term < MAXTERM) else 'ragged'


def annotate(res, edge):
    """[(kind, block)] -> [(kind, shape, block)]"""
    return [(k, block_shape(b, edge) if k.startswith('display') else None, b)
            for k, b in res]
