# -*- coding: utf-8 -*-
"""Composition of NEAR-band lines the page side puts inside a verse block."""
import sys, os, re, collections
sys.path.insert(0,'_xc/reseg'); sys.path.insert(0,'pipeline')
import pline, check_page_fidelity as F
DASH = re.compile(u'[–—‐-]\\s*$')
def q(a,p):
    a=sorted(a); return a[min(len(a)-1,int(len(a)*p))] if a else 0
for vol in sys.argv[1:]:
    lines=[x for x in pline.stream(vol) if F.letters(x[3])]
    body,W=F.page_geometry(lines)
    cls,verse,_=F.page_classes(lines,body,W)
    bod=[l[2]+len(l[3]) for l in lines if l[2]==body]
    bp75=q(bod,.75)
    c=collections.Counter(); ends=[]
    far_ends=[]
    for i,l in enumerate(lines):
        e=l[2]+len(l[3])
        if verse[i] and l[2]>=body+F.INSET: far_ends.append((e,DASH.search(l[3]) is not None))
        if not verse[i] or not (body+F.NEAR<=l[2]<body+F.INSET): continue
        c['near_in_block']+=1; ends.append(e)
        if DASH.search(l[3]): c['dash_end']+=1
        if e>bp75-6: c['long(>bp75-6)']+=1
        if DASH.search(l[3]) or e>bp75-6: c['dash_or_long']+=1
    fd=sum(1 for e,d in far_ends if d)
    print('%-10s body p75=%d  near-in-block=%d  ends p50=%d p90=%d | dash=%d long=%d either=%d || FAR verse lines=%d dash-enders=%d (%.2f%%)'
          %(vol,bp75,c['near_in_block'],q(ends,.5),q(ends,.9),c['dash_end'],c['long(>bp75-6)'],c['dash_or_long'],
            len(far_ends),fd,100.0*fd/max(1,len(far_ends))))
