# -*- coding: utf-8 -*-
"""Candidate measurement: the volume's DISPLAY COLUMN, read off the page."""
import sys, collections
sys.path.insert(0,'_xc/reseg'); sys.path.insert(0,'pipeline')
import pline, check_page_fidelity as F
def q(a,p):
    a=sorted(a); return a[min(len(a)-1,int(len(a)*p))] if a else 0
def geom(lines):
    body,W = F.page_geometry(lines)
    Bm = q([l[2]+len(l[3]) for l in lines if l[2]==body], .75) or (W-6)
    return body,W,Bm
def dcol(lines, body, Bm, frac=0.90):
    thr = Bm-8
    best = body+F.INSET
    for d in range(body+2, body+F.INSET+1):
        a=[l for l in lines if l[2]>=d]
        if len(a) < 0.02*len(lines): break
        sh = sum(1 for l in a if l[2]+len(l[3])<=thr)/float(len(a))
        if sh>=frac:
            best=d; break
    return best
for v in sys.argv[1:]:
    lines=[x for x in pline.stream(v) if F.letters(x[3])]
    body,W,Bm=geom(lines)
    prof=[]
    for d in range(body+2, body+F.INSET+3):
        a=[l for l in lines if l[2]>=d]
        if not a: continue
        sh=sum(1 for l in a if l[2]+len(l[3])<=Bm-8)/float(len(a))
        prof.append('%d:%.0f%%(%d)'%(d,100*sh,len(a)))
    print('%-10s body=%d W=%d Bm=%d  DCOL=%d | %s'%(v,body,W,Bm,dcol(lines,body,Bm),' '.join(prof)))
