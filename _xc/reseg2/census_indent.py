# -*- coding: utf-8 -*-
"""pdftotext indent census over the printed line stream, per volume."""
import sys, os, json, collections
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import pline
for v in sys.argv[1:]:
    s = pline.stream(v)
    c = collections.Counter(it[2] for it in s)
    tot = len(s)
    d = json.load(open('site/%s.json' % v, encoding='utf-8'))
    ps = d['paragraphs'] if isinstance(d, dict) else d
    print('%-10s  %6d lines  %5d shipped ¶' % (v, tot, len(ps)))
    for ind in sorted(c):
        if c[ind] >= 20:
            print('     indent %2d  %6d  %5.1f%%' % (ind, c[ind], 100.0*c[ind]/tot))
    band = sum(c[i] for i in range(3, 7))
    print('     band 3-6: %d   band 7+: %d   indent 0: %d' % (band, sum(c[i] for i in c if i >= 7), c[0]))
