# -*- coding: utf-8 -*-
"""Collate `pipeline/check_bold_fidelity.py --all --out _xc/boldfid/census`."""
import os, json, sys, collections

D = os.path.dirname(os.path.abspath(__file__))
CEN = os.path.join(D, 'census')
R = {}
for f in sorted(os.listdir(CEN)):
    if f.endswith('.json'):
        R[f[:-5]] = json.load(open(os.path.join(CEN, f), encoding='utf-8'))
S = dict((v, R[v]['stat']) for v in R)


def tot(k):
    return sum(s.get(k, 0) for s in S.values())


def top(k, n=12, also=None):
    r = sorted(S.items(), key=lambda kv: -kv[1].get(k, 0))[:n]
    return [(v, s.get(k, 0)) + ((s.get(also, 0),) if also else ()) for v, s in r
            if s.get(k, 0)]


L = []
P = L.append
P('BOLD FIDELITY CENSUS -- %d volumes' % len(S))
P('')
P('  printed body lines read from the PDF       %10d' % tot('page_lines'))
P('    located in the data stream               %10d  (%.2f%%)'
  % (tot('line_found'), 100.0 * tot('line_found') / max(1, tot('page_lines'))))
P('      by the forward cursor                  %10d' % tot('line_found_fwd'))
P('      by the backward window                 %10d' % tot('line_found_back'))
P('      by an unanchored search  (SOFT)        %10d' % tot('line_found_any'))
P('    not located                              %10d  (%.2f%%)'
  % (tot('line_absent'), 100.0 * tot('line_absent') / max(1, tot('page_lines'))))
P('      bold runs inside those lines           %10d' % tot('page_runs_in_absent_lines'))
P('')
P('  BOLD RUNS ON THE PRINTED PAGE              %10d' % tot('page_runs'))
P('    exactly what the corpus carries          %10d  (%.2f%%)'
  % (tot('EXACT'), 100.0 * tot('EXACT') / max(1, tot('page_runs'))))
P('    MISSED    - bold on the page, none in the corpus   %10d' % tot('MISSED'))
P('    MISALIGNED_part - corpus covers only part of it    %10d' % tot('MISALIGNED_part'))
P('    MISALIGNED_long - corpus bolds beyond it           %10d' % tot('MISALIGNED_long'))
P('    SPURIOUS  - bold in the corpus, none on the page   %10d' % tot('SPURIOUS'))
P('      of the above, resting on a SOFT line match: EXACT %d  MISSED %d  PART %d  SPUR %d'
  % (tot('EXACT_soft'), tot('MISSED_soft'), tot('MISALIGNED_part_soft'),
     tot('SPURIOUS_soft')))
P('')
P('  the same page runs by WHAT THEY SIT IN')
P('    P  running prose (where a lemma lives)   %10d   missed %7d' % (tot('page_runs_cls_P'), tot('MISSED_P')))
P('    H  a heading / title / uddana            %10d   missed %7d' % (tot('page_runs_cls_H'), tot('MISSED_H')))
P('    V  display verse                         %10d   missed %7d' % (tot('page_runs_cls_V'), tot('MISSED_V')))
P('')
P('  THE DATA')
P('    bold spans in bold/<VOL>.bold.json       %10d' % tot('spans_in_data'))
P('    bold spans in bold/<VOL>.sect.json       %10d' % tot('sect_spans_in_data'))
P('    paragraphs carrying at least one span    %10d' % tot('paras_with_bold'))
P('    letters the data marks bold              %10d' % tot('data_bold_letters'))
P('')
P('  WHAT THE READER DRAWS')
P('    letters bold in the BAND view            %10d' % tot('band_bold_letters'))
P('    letters bold in the SPINE view           %10d' % tot('spine_bold_letters'))
P('    page bold runs present in the data but NOT DRAWN in the spine view %d'
  % tot('in_data_not_drawn_spine'))
P('    spans on ordinals whose paragraph text the verse branch replaces   %d'
  % tot('spans_on_verse_branch_ordinals'))
P('')
P('RANKED BY MISSED (page bold the corpus does not carry)')
P('  %-11s %7s %7s %7s %7s %7s' % ('vol', 'MISSED', 'in P', 'in H', 'in V', 'runs'))
for v, n in top('MISSED', 25):
    s = S[v]
    P('  %-11s %7d %7d %7d %7d %7d' % (v, n, s.get('MISSED_P', 0),
                                       s.get('MISSED_H', 0), s.get('MISSED_V', 0),
                                       s.get('page_runs', 0)))
P('')
P('RANKED BY MISSED_P ONLY -- bold in RUNNING PROSE the corpus does not carry')
for v, n in top('MISSED_P', 25):
    P('  %-11s %6d   of %6d prose runs   (%.1f%%)  soft %d'
      % (v, n, S[v].get('page_runs_cls_P', 0),
         100.0 * n / max(1, S[v].get('page_runs_cls_P', 0)),
         S[v].get('MISSED_soft', 0)))
P('')
P('RANKED BY SPURIOUS')
for v, n in top('SPURIOUS', 20):
    P('  %-11s %6d' % (v, n))
P('')
P('RANKED BY MISALIGNED (part + long)')
mis = sorted(S.items(), key=lambda kv: -(kv[1].get('MISALIGNED_part', 0)
                                         + kv[1].get('MISALIGNED_long', 0)))[:20]
for v, s in mis:
    n = s.get('MISALIGNED_part', 0) + s.get('MISALIGNED_long', 0)
    if n:
        P('  %-11s %6d   (part %d, long %d)' % (v, n, s.get('MISALIGNED_part', 0),
                                                s.get('MISALIGNED_long', 0)))
P('')
P('VOLUMES WITH NO BOLD DATA AT ALL')
z = [v for v in sorted(S) if not S[v].get('spans_in_data')]
P('  %d: %s' % (len(z), ' '.join(z)))
P('')
P('PER VOLUME')
P('  %-11s %7s %7s %6s %6s %6s %6s %7s %7s' % ('vol', 'lines', 'pruns', 'EXACT',
                                               'MISS', 'PART', 'LONG', 'SPUR', 'spans'))
for v in sorted(S):
    s = S[v]
    P('  %-11s %7d %7d %6d %6d %6d %6d %7d %7d'
      % (v, s.get('page_lines', 0), s.get('page_runs', 0), s.get('EXACT', 0),
         s.get('MISSED', 0), s.get('MISALIGNED_part', 0),
         s.get('MISALIGNED_long', 0), s.get('SPURIOUS', 0),
         s.get('spans_in_data', 0)))
txt = '\n'.join(L)
open(os.path.join(D, 'CENSUS.txt'), 'w', encoding='utf-8').write(txt + '\n')
print(txt)
