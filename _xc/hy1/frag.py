# -*- coding: utf-8 -*-
"""Locate the three 35Abhi07 fragments in BOTH streams: the builder's -layout
item stream and the bbox block map.  No hypothesis -- print what each holds."""
import sys, os, json, re, importlib
sys.path.insert(0, os.path.abspath('pipeline'))
sys.path.insert(0, os.path.abspath('_xc/hy1'))
VOL = '35Abhi07'
NEEDLE = 'Na indriyā na'

os.environ['BLOCKBREAK'] = '0'
m = importlib.import_module('build_khu_volume_bb')
m.use(VOL)

# --- 1. the builder's raw -layout page lines -------------------------------
pages = m.pdf_pages()
print('=== -layout stream: lines containing the needle ===')
hits = []
for pi, pg in enumerate(pages, 1):
    for li, ln in enumerate(pg.split('\n')):
        if NEEDLE in ln:
            hits.append((pi, li, ln))
print('total -layout lines with needle: %d' % len(hits))
for pi, li, ln in hits[:6]:
    print('  raw pg %-4d line %-3d | %r' % (pi, li, ln.rstrip()[:110]))

# --- 2. the same lines in the bbox block map -------------------------------
BL = json.load(open('_xc/hy1/blocks3/%s.json' % VOL, encoding='utf-8'))
print()
print('=== blocks3 (bbox): lines containing the needle ===')
bh = []
for pg, pd in BL.items():
    for i, l in enumerate(pd['lines']):
        if NEEDLE in l[3]:
            bh.append((int(pg), i, l))
print('total bbox lines with needle: %d' % len(bh))
for pg, i, l in bh[:6]:
    print('  raw pg %-4d row %-3d y=%-7s x=%-6s start=%d xMax=%-6s | %s'
          % (pg, i, l[0], l[1], l[2], l[4], l[3][:90]))
