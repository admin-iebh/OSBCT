# -*- coding: utf-8 -*-
"""INDEPENDENT check of the boundary set: the printed PAGE.

The boundary at ordinal b is claimed because the edition prints `X niṭṭhitā.`
just before the head anchored at b.  That colophon carries its own printed page
number, which took no part in choosing b.  So:

    printed(paragraph b-1)  <=  printed(colophon)  <=  printed(paragraph b)

Anything else means the ordinal and the colophon are on different pages and the
boundary is in the wrong place.  `--shift N` moves every boundary by N and must
make the check fail: a check that cannot fail is not a check.
"""
import json,re,sys,os,collections
sys.path.insert(0,'/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/_range')
import importlib.util
spec=importlib.util.spec_from_file_location('m','/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/_range/measure.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

SHIFT=0
if '--shift' in sys.argv: SHIFT=int(sys.argv[sys.argv.index('--shift')+1])
vols=[a for a in sys.argv[1:] if not a.startswith('-') and not a.isdigit()]

tot=collections.Counter()
for v in vols:
    d=m.vol(v); heads=d['headings']; sm=m.sec(v); paras=d['paragraphs']
    anch=[]
    for o in sorted(sm,key=int):
        for x in sm[o]: anch.append((int(o), m.fold(m.strip_num(x.get('l') or ''))))
    ptr=0; checked=0; bad=[]
    for i,h in enumerate(heads):
        if not m.is_end(h.get('title')): continue
        j=i+1
        while j<len(heads) and (re.match(r'^[_\s.]*$',heads[j].get('title') or '') or m.is_end(heads[j].get('title'))): j+=1
        if j>=len(heads): continue
        want=m.fold(m.strip_num(heads[j]['title']))
        if len(want)<4: continue
        hit=None
        for k in range(ptr,len(anch)):
            if anch[k][1]==want: hit=k;break
        if hit is None:
            for k in range(len(anch)):
                if anch[k][1]==want: hit=k;break
        if hit is None: continue
        ptr=hit+1
        b=anch[hit][0]+SHIFT
        if b<1 or b>=len(paras): continue
        pc=h.get('printed'); pa=paras[b-1].get('printed'); pb=paras[b].get('printed')
        checked+=1
        if pc is None or pa is None or pb is None: continue
        if not (pa<=pc<=pb): bad.append((h.get('title'),b,pa,pc,pb))
    tot['checked']+=checked; tot['bad']+=len(bad)
    print('%-11s boundaries checked %3d  page-inconsistent %3d %s'%(v,checked,len(bad),bad[:3]))
print('TOTAL checked %d, inconsistent %d (%.1f%%)%s'%(tot['checked'],tot['bad'],
      100*tot['bad']/max(1,tot['checked']), '   [SHIFT %+d]'%SHIFT if SHIFT else ''))
sys.exit(1 if (SHIFT==0 and tot['bad']) or (SHIFT!=0 and tot['bad']==0) else 0)
