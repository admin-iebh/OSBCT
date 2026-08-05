# -*- coding: utf-8 -*-
"""The reserved non-gatha display class: locate each named instance on the page.

These are the five shapes the handoff says are protected by the caesura test in
`_pada_page` and on which the reader has not decided whether they get their own
class.  Rendered so the decision can be made from the page."""
import sys, os, json, subprocess, re, collections
sys.path.insert(0, os.path.abspath('pipeline'))
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import extract, pline

SKEL = re.compile(r'[^A-Za-z]')
n = lambda s: SKEL.sub('', s or '')
HEADNUM = re.compile(r'^\s*(\d{1,4})\s+\S|\S\s+(\d{1,4})\s*$')
CASES = [('35Abhi07', 81, 'the 37 Yamaka pairs'),
         ('26Khu09', 9, "the Patisambhida matika"),
         ('29Abhi01', 32, "the Dukamatika -- 'Niruttipatha dhamma. (1314)'"),
         ('18Khu01', 25, 'the refuge lists'),
         ('42KhuA23', 5, "'(Sattamo bhago)' and its four siblings")]
out = []
for vol, plpg, what in CASES:
    st = [l for l in pline.stream(vol) if l[0] == plpg]
    if not st:
        print('%-10s pline p%d empty' % (vol, plpg)); continue
    src = next(p for p in ('pali-unicode/%s.pdf', 'atthakatha-unicode/%s.pdf',
                           'tika-unicode/%s.pdf') if os.path.exists(p % vol)) % vol
    pgs = extract.raw_pages(src)
    key = n(st[min(3, len(st) - 1)][3])[:24]
    idx = [i for i, p in enumerate(pgs) if key and key in n(p)]
    pdfp = idx[0] + 1 if idx else None
    printed = None
    if pdfp:
        h = [l for l in pgs[pdfp - 1].split('\n') if l.strip()][:1]
        if h:
            m = HEADNUM.match(h[0])
            if m:
                printed = int(m.group(1) or m.group(2))
        subprocess.run(['pdftoppm', '-f', str(pdfp), '-l', str(pdfp), '-r', '115',
                        '-png', '-singlefile', src, '_xc/hy1/pg/RESERVED_%s_%d' % (vol, plpg)],
                       check=True)
    out.append((vol, plpg, pdfp, printed, what))
    print('%-10s %-46s pline p%-4d  pdftotext p%-4s  PRINTED %s'
          % (vol, what, plpg, pdfp, printed))
json.dump(out, open('_xc/hy1/reserved.json', 'w'))
