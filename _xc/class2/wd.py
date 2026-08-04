# -*- coding: utf-8 -*-
import sys, os, re, collections
sys.path.insert(0, '_xc/reseg'); sys.path.insert(0, 'pipeline')
import pline, check_page_fidelity as F
VNUM = re.compile(r'^\s*[\(\[‘“’”]{0,2}\d{1,4}\s*[\.\-–]')
def q(a, p):
    a = sorted(a); return a[min(len(a)-1, int(len(a)*p))] if a else None
for vol in sys.argv[1:]:
    lines = [x for x in pline.stream(vol) if F.letters(x[3])]
    body, W = F.page_geometry(lines)
    # ground-truth pada lines: carry a leading verse number AND sit off the body column
    num = [l[2]+len(l[3]) for l in lines if l[2] >= body+F.NEAR and VNUM.match(l[3])]
    # unambiguous display: indent >= body+INSET, in a same-page run of >=2 small step
    far = [i for i,l in enumerate(lines) if l[2] >= body+F.INSET]
    fs = set(far); runs=[]
    for i in far:
        if (i-1 in fs and lines[i-1][0]==lines[i][0] and abs(lines[i][2]-lines[i-1][2])<=F.RUNTOL) or \
           (i+1 in fs and lines[i+1][0]==lines[i][0] and abs(lines[i+1][2]-lines[i][2])<=F.RUNTOL):
            runs.append(lines[i][2]+len(lines[i][3]))
    bod = [l[2]+len(l[3]) for l in lines if l[2]==body]
    print('%-10s body=%d W=%d | num n=%5s p50=%s p90=%s p975=%s max=%s | farblk n=%5s p50=%s p90=%s p975=%s | body p50=%s p90=%s'
          % (vol, body, W, len(num), q(num,.5), q(num,.9), q(num,.975), max(num) if num else None,
             len(runs), q(runs,.5), q(runs,.9), q(runs,.975), q(bod,.5), q(bod,.9)))
