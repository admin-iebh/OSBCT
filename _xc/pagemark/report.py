# -*- coding: utf-8 -*-
"""Collate _xc/pagemark/census/*.json.  MEASURE ONLY."""
import json, os, glob, collections, statistics
D = os.path.dirname(os.path.abspath(__file__))
RESEG = ('20KhuA01', '21KhuA02', '23KhuA04', '24KhuA05')
rows = {}
for f in sorted(glob.glob(os.path.join(D, 'census', '*.json'))):
    d = json.load(open(f, encoding='utf-8'))
    rows[d['vol']] = d
tot = collections.Counter()
for v, d in rows.items():
    tot.update(d['stat'])
P = tot['pages'] or 1
print('PAGE-MARKER CENSUS — %d volumes, %d printed pages judged' % (len(rows), tot['pages']))
print()
print('  marker on the exact letter the page turns at   %7d  %5.1f%%' % (tot['EXACT'], 100.0*tot['EXACT']/P))
print('  marker LATE                                    %7d  %5.1f%%' % (tot['LATE'], 100.0*tot['LATE']/P))
print('  marker EARLY                                   %7d  %5.1f%%' % (tot['EARLY'], 100.0*tot['EARLY']/P))
print('  no marker drawn for that printed page at all   %7d' % tot['marker_missing'])
print('  page whose first line could not be located     %7d' % tot['page_unlocated'])
print()
print('  page break falls INSIDE a corpus paragraph     %7d  %5.1f%%' % (tot['break_inside_paragraph'], 100.0*tot['break_inside_paragraph']/P))
print('  page break falls BETWEEN two paragraphs        %7d  %5.1f%%' % (tot['break_at_boundary'], 100.0*tot['break_at_boundary']/P))
print()
late_l, late_c = [], []
for v, d in rows.items():
    for r in d['rows']:
        if r[5] == 'LATE':
            late_l.append(r[4]); late_c.append(r[3])
late_l.sort(); late_c.sort()
def pc(a, q): return a[min(len(a)-1, int(q*len(a)))] if a else 0
print('DRIFT OF A LATE MARKER (%d of them)' % len(late_l))
print('              lines   chars')
for q, name in ((0.10,'p10'),(0.25,'p25'),(0.50,'median'),(0.75,'p75'),(0.90,'p90'),(0.99,'p99')):
    print('  %-8s %7d %7d' % (name, pc(late_l,q), pc(late_c,q)))
print('  %-8s %7d %7d' % ('max', late_l[-1] if late_l else 0, late_c[-1] if late_c else 0))
print('  %-8s %7.1f %7.1f' % ('mean', statistics.mean(late_l) if late_l else 0,
                              statistics.mean(late_c) if late_c else 0))
print('  a late marker sits at or before the page it names for %d of %d pages'
      % (len(late_l), tot['pages']))
h = collections.Counter()
for x in late_l:
    h['0' if x == 0 else ('1-2' if x <= 2 else ('3-5' if x <= 5 else ('6-10' if x <= 10
        else ('11-20' if x <= 20 else ('21-40' if x <= 40 else '>40')))))] += 1
print('\n  lines late:  ' + '  '.join('%s=%d' % (k, h[k]) for k in ('0','1-2','3-5','6-10','11-20','21-40','>40')))
print('\nWORST VOLUMES by share of printed pages whose marker is not exact')
print('%-12s %6s %7s %7s %7s %7s  %s' % ('vol','pages','exact%','late','medln','maxln','inside%'))
def key(v):
    s = rows[v]['stat']; p = s.get('pages',0) or 1
    return -(1.0 - s.get('EXACT',0)/p), -s.get('pages',0)
for v in sorted(rows, key=lambda v: (rows[v]['stat'].get('EXACT',0)/(rows[v]['stat'].get('pages',0) or 1), -rows[v]['stat'].get('pages',0)))[:20]:
    s = rows[v]['stat']; p = s.get('pages',0) or 1
    ll = sorted(r[4] for r in rows[v]['rows'] if r[5]=='LATE')
    print('%-12s %6d %6.1f%% %7d %7d %7d  %5.1f%%' % (v, s.get('pages',0), 100.0*s.get('EXACT',0)/p,
          s.get('LATE',0), ll[len(ll)//2] if ll else 0, ll[-1] if ll else 0,
          100.0*s.get('break_inside_paragraph',0)/p))
print('\nBEST VOLUMES')
for v in sorted(rows, key=lambda v: (-rows[v]['stat'].get('EXACT',0)/(rows[v]['stat'].get('pages',0) or 1), -rows[v]['stat'].get('pages',0)))[:10]:
    s = rows[v]['stat']; p = s.get('pages',0) or 1
    print('%-12s %6d %6.1f%%' % (v, s.get('pages',0), 100.0*s.get('EXACT',0)/p))
print('\nRE-SEGMENTED vs NOT')
for grp, sel in (('re-segmented (%s)' % ', '.join(RESEG), lambda v: v in RESEG),
                 ('everything else', lambda v: v not in RESEG)):
    t = collections.Counter()
    ll = []
    for v, d in rows.items():
        if not sel(v):
            continue
        t.update(d['stat'])
        ll += [r[4] for r in d['rows'] if r[5]=='LATE']
    p = t['pages'] or 1
    ll.sort()
    print('  %-34s vols=%3d pages=%6d exact=%5.1f%%  inside=%5.1f%%  median late lines=%d'
          % (grp, sum(1 for v in rows if sel(v)), t['pages'], 100.0*t['EXACT']/p,
             100.0*t['break_inside_paragraph']/p, ll[len(ll)//2] if ll else 0))
for v in RESEG:
    if v in rows:
        s = rows[v]['stat']; p = s.get('pages',0) or 1
        print('    %-11s pages=%5d exact=%5.1f%% inside=%5.1f%%' % (v, s.get('pages',0),
              100.0*s.get('EXACT',0)/p, 100.0*s.get('break_inside_paragraph',0)/p))
print('\nlines not located anywhere in the corpus: %d of %d (%.2f%%)'
      % (tot['lines_unlocated'], tot['lines_total'], 100.0*tot['lines_unlocated']/(tot['lines_total'] or 1)))
