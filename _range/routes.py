# -*- coding: utf-8 -*-
"""Two independent routes to the same boundary set: the printed colophon and the
printed section number.  Report how often they agree.  --guard applies the
page-consistency guard to the colophon route."""
import json,re,sys,collections,importlib.util
spec=importlib.util.spec_from_file_location('m','/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/_range/measure.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
GUARD='--guard' in sys.argv
vols=[a for a in sys.argv[1:] if not a.startswith('-')]
tot=collections.Counter()
for v in vols:
    d=m.vol(v); heads=d['headings']; sm=m.sec(v); paras=d['paragraphs']
    anch=[]
    for o in sorted(sm,key=int):
        for x in sm[o]: anch.append((int(o), m.fold(m.strip_num(x.get('l') or ''))))
    colo=set(); ptr=0; rejected=0
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
        ptr=hit+1; b=anch[hit][0]
        if GUARD and 0<b<len(paras):
            pc=h.get('printed'); pa=paras[b-1].get('printed'); pb=paras[b].get('printed')
            if pc is not None and pa is not None and pb is not None and not (pa<=pc<=pb):
                rejected+=1; continue
        colo.add(b)
    numbered=set(int(o) for o in sm for x in sm[o] if re.match(r'^\d+\.\s',x.get('l') or ''))
    both=colo&numbered
    print('%-11s colophon %3d  numbered %3d  agree %3d (%.0f%% of colophon)  colophon-only %2d  numbered-only %3d%s'
          %(v,len(colo),len(numbered),len(both),100*len(both)/max(1,len(colo)),
            len(colo-numbered),len(numbered-colo),'  rejected %d'%rejected if GUARD else ''))
    tot['c']+=len(colo); tot['n']+=len(numbered); tot['b']+=len(both); tot['r']+=rejected
print('TOTAL colophon %d, numbered %d, agree %d (%.1f%% of colophon boundaries)%s'
      %(tot['c'],tot['n'],tot['b'],100*tot['b']/max(1,tot['c']),'  rejected %d'%tot['r'] if GUARD else ''))
