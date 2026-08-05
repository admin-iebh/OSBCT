# -*- coding: utf-8 -*-
"""Does pipeline/extract.py as it stands REPRODUCE the shipped site/<VOL>.json?

pipeline/README.md says several auxiliary scripts "were run in a scratch
environment and are being consolidated back into this directory", so this is
not assumed either way.  Patching extract.py:204 is worthless if the file that
produced the corpus is not this one.

Compares paragraph COUNT and paragraph TEXT, and reports the first divergences
rather than a boolean.
"""
import sys, os, json, difflib

sys.path.insert(0, os.path.abspath('pipeline'))
import extract as E


def pdf_of(vol):
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = '%s/%s.pdf' % (d, vol)
        if os.path.exists(p):
            return p
    raise SystemExit('no pdf for ' + vol)


def main(vol):
    pgs, paras, heads = E.extract(pdf_of(vol))
    ship = json.load(open('site/%s.json' % vol, encoding='utf-8'))['paragraphs']
    print('== %s ==' % vol)
    print('   paragraphs  extract.py %5d   shipped %5d   %s'
          % (len(paras), len(ship),
             'SAME COUNT' if len(paras) == len(ship) else '*** DIFFERENT ***'))
    a = [(p.get('text') or '').strip() for p in paras]
    b = [(p.get('text') or '').strip() for p in ship]
    same = sum(1 for x, y in zip(a, b) if x == y)
    n = min(len(a), len(b))
    print('   texts identical at the same index: %d of %d  (%.1f%%)'
          % (same, n, 100.0 * same / max(1, n)))
    # also: does the shipped text exist ANYWHERE in the extract output?
    sa = set(a)
    print('   shipped texts present anywhere in extract output: %d of %d (%.1f%%)'
          % (sum(1 for y in b if y in sa), len(b),
             100.0 * sum(1 for y in b if y in sa) / max(1, len(b))))
    shown = 0
    for i in range(n):
        if a[i] != b[i] and shown < 3:
            shown += 1
            print('   -- first divergence #%d at index %d' % (shown, i))
            print('      SHIPPED    | %s' % b[i][:150])
            print('      extract.py | %s' % a[i][:150])
            for d in list(difflib.unified_diff(
                    b[i].split(), a[i].split(), lineterm='', n=0))[2:8]:
                print('        %s' % d)
    if shown == 0:
        print('   no text divergence in the compared range')


for v in sys.argv[1:]:
    main(v)
