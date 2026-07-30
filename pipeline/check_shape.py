#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two shape assertions over the shipped side-maps.  Both exist because a USER
reading the page found the defect first and no gate could see it: the three
content gates test whether every printed WORD is present, once, in the right
order, and a wrong SHAPE leaves every word in place.

  1. APPARATUS PROPORTIONATE TO THE PARAGRAPH.  A note is a marker PRINTED in
     the paragraph's own text, so a paragraph cannot carry more notes than it
     has words.  Dimensionless -- no tuned constant.  MEASURED over all 22,854
     anchored paragraphs: the corpus maximum is 0.75 notes per word (18Khu01
     ord1864, 6 notes on 8 words).  The defect this is written for -- 07DiA01
     ord0 carrying 94 notes on a 26-character, 3-word paragraph after its
     corpus was rebuilt under it (2026-07-27af) -- scores 31.3, i.e. FORTY
     TIMES the corpus maximum.  There is no threshold to argue about.

  2. A GĀTHĀ BLOCK THAT IS PROSE.  The reader draws a `gatha` block with a
     <br> between lines, so every printed line becomes a verse line.  That is
     right for a pāda and wrong for a paragraph.  The discriminator is the
     MEASURE: a pāda is short, a body line runs the full column.  MEASURED
     over all 6,802 gāthā blocks of three lines or more, the median line is 31
     characters, p90 is 46 and p99 is 63 -- so a block whose median line
     reaches the body measure is the top fraction of a percent, and the
     Bāhiranidāna's restored prose (~70) sat far outside it.  Reported with
     the sentence test beside it (a pāda ends in ',' or '.'; a run of lines
     each ending in a full stop is a run of sentences).

Neither is a pass/fail gate over the corpus as it stands: assertion 2 is clean
everywhere today, assertion 1 has a standing batch that is named in the report
and must be judged against the printed page, volume by volume.

  python3 pipeline/check_shape.py [VOL...]        # all volumes when none given
"""
import json, os, re, sys, glob, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, 'site', 'reader')
# the top of the measured distribution, not a guess: p99 of the median line
# length over every gāthā block in the corpus is 63 and the maximum is 70.
BODY_MEASURE = 58
MIN_LINES = 3


def _load(p):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def apparatus_shape(vol):
    """[(notes, words, ord)] for paragraphs carrying more notes than words."""
    A = _load(f'{R}/apparatus/{vol}.appk.json')
    if not A:
        return None
    try:
        P = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))['paragraphs']
    except Exception:
        return None
    out, worst = [], (0.0, 0, 0, None)
    for k, notes in A.items():
        i = int(k)
        if i >= len(P):
            out.append((len(notes), -1, i))       # anchored past the corpus
            continue
        w = len((P[i].get('text') or '').split())
        r = len(notes) / max(w, 1)
        if r > worst[0]:
            worst = (r, len(notes), w, i)
        if r > 1.0:
            out.append((len(notes), w, i))
    return out, worst


def gatha_blocks(vol):
    """(where, lines) for every block the reader draws as display verse."""
    S, V, U = (_load(f'{R}/{d}/{vol}.json') for d in ('sections', 'verse', 'uddana'))
    out = []
    for o, arr in S.items():
        for i, x in enumerate(arr):
            if x.get('k') == 'gatha':
                out.append((f'sections ord{o}:{i}', str(x['l']).split('\n')))
    for o, e in V.items():
        for j, g in enumerate(e.get('groups', [])):
            out.append((f'verse.groups ord{o}[{j}]', list(g)))
        for fld in ('before', 'after'):
            x = e.get(fld)
            if x is None:
                continue
            for p in ([x] if isinstance(x, str) else x):
                if isinstance(p, dict) and p.get('gatha'):
                    out.append((f'verse.{fld} ord{o}', list(p['gatha'])))
    for o, arr in U.items():
        for b in arr:
            if not b.get('plain') and b.get('lines'):
                out.append((f'uddana ord{o}', list(b['lines'])))
    return out


SENT = re.compile(r'[.?!](?:["”’\')\]]|ti)?\s*$')


def prose_as_verse(vol):
    out = []
    for where, lines in gatha_blocks(vol):
        if len(lines) < MIN_LINES:
            continue
        med = statistics.median(len(l) for l in lines)
        if med < BODY_MEASURE:
            continue
        # how many of the lines BEFORE the last end a sentence?  a pāda ends
        # in ',' far more often than in '.', so a block of sentences is prose
        # twice over.
        mid = sum(1 for l in lines[:-1] if SENT.search(l.strip()))
        out.append((med, len(lines), mid, where, lines[0]))
    out.sort(reverse=True)
    return out


def main(vols):
    if not vols:
        vols = sorted(os.path.basename(f)[:-5] for f in glob.glob(f'{R}/verse/*.json'))
    bad = pv_tot = 0
    pv_vol = []
    print('=== 1. APPARATUS PROPORTIONATE TO THE PARAGRAPH  (notes must not exceed words)')
    peak = (0.0, 0, 0, None, None)
    for v in vols:
        r = apparatus_shape(v)
        if r is None:
            continue
        out, worst = r
        if worst[0] > peak[0]:
            peak = worst + (v,)
        for notes, w, i in out:
            bad += 1
            print('   FAIL %-11s ord%-6d %4d notes on %s'
                  % (v, i, notes, 'a paragraph the corpus does not have'
                     if w < 0 else '%d word(s)' % w))
    print('   worst ratio in the corpus: %.2f notes/word  (%s ord%s, %d notes on %d words)'
          % (peak[0], peak[4], peak[3], peak[1], peak[2]))
    print('   %d paragraph(s) carry more notes than words' % bad)
    print()
    print('=== 2. A GĀTHĀ BLOCK THAT IS PROSE  (median line >= %d chars, the body measure)'
          % BODY_MEASURE)
    for v in vols:
        o = prose_as_verse(v)
        if not o:
            continue
        pv_tot += len(o)
        pv_vol.append((len(o), v, o))
    pv_vol.sort(reverse=True)
    for n, v, o in pv_vol:
        tot = sum(1 for _, l in gatha_blocks(v) if len(l) >= MIN_LINES)
        print('   %-11s %3d of %4d block(s)' % (v, n, tot))
        for med, nl, mid, where, first in o[:3]:
            print('        %-24s %2d lines, median %3d, %d sentence-end mid-block  %r'
                  % (where, nl, int(med), mid, first[:58]))
    print('   %d block(s) in %d volume(s) to judge against the printed page'
          % (pv_tot, len(pv_vol)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main([a for a in sys.argv[1:] if not a.startswith('--')]))
