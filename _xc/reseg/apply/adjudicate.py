# -*- coding: utf-8 -*-
"""Third route: decide the disputed apparatus anchors by PRINTED POSITION.

Route A = pipeline/rebuild_apparatus.py on the re-segmented corpus (marker digit
in the candidate paragraph's text, covering-first then a +/-3 page window).
Route B = _xc/reseg/ redistribution of the shipped file (page recovered by
matching (n,text) to the printed footnote cell, then placed inside the old run).

Neither is consulted here.  For each note we take the page its footnote CELL is
printed on, find the marker occurrence in that page's BODY letters, and read off
which re-segmented paragraph's printed extent contains it.
"""
import json, os, re, sys, bisect, subprocess, importlib.util as ilu, collections
R='/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/'
sys.path.insert(0, R+'pipeline'); sys.path.insert(0, R+'_xc/reseg')
import pline, locate
sp=ilu.spec_from_file_location('ra', R+'pipeline/rebuild_apparatus.py')
ra=ilu.module_from_spec(sp); sp.loader.exec_module(ra)
vr=ra.vr

VOL='20KhuA01'
paras=json.load(open(R+'site/%s.json'%VOL))['paragraphs']
pages=subprocess.run(['pdftotext','-layout',ra.pdf_path(VOL),'-'],
                     capture_output=True,text=True).stdout.split('\f')
OFF=vr.page_offset(VOL,paras,pages)
stream=pline.stream(VOL)
PG=locate.Page(stream)
anch=json.load(open(R+'_xc/reseg/b3/anchors_%s.json'%VOL))['reseg']
# letter range of each corpus pdf_page in the printed stream
pg_start={}
pos=0
for it,s in zip(stream,PG.starts):
    pg_start.setdefault(it[0],s)
pgs=sorted(pg_start)
pstarts=[pg_start[p] for p in pgs]
def page_letter_range(p):
    i=pgs.index(p)
    return pstarts[i], (pstarts[i+1] if i+1<len(pgs) else len(PG.text))
pstart=[a[2] for a in anch]
def para_of(lp):
    k=bisect.bisect_right(pstart,lp)-1
    return k if 0<=k<len(anch) and anch[k][2]<=lp<anch[k][3] else None

# note -> page(s) its printed cell appears on
cell_pages=collections.defaultdict(list)
for pi,page in enumerate(pages):
    notes,_=ra.page_notes(page)
    for n,lst in notes.items():
        for t in lst: cell_pages[(n,t.strip())].append(pi-OFF)

A=json.load(open(R+'_xc/reseg/apply/appk_routeA2.json'))
B=json.load(open(R+'_xc/reseg/apparatus/%s.appk.json'%VOL))
def flat(D):
    o=collections.defaultdict(list)
    for k,arr in D.items():
        for a in arr: o[(a.get('n'),(a.get('text') or '').strip())].append(int(k))
    return o
fa,fb=flat(A),flat(B)
dis=[k for k in fa if k in fb and sorted(fa[k])!=sorted(fb[k])]
MK=re.compile(r'[A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ](\d{1,2})(?!\d)')
winA=winB=neither=undecided=0
rows=[]
for k in sorted(dis, key=lambda x:(x[0] or 0,x[1])):
    n,txt=k
    ps=set(cell_pages.get(k,[]))
    if len(ps)!=1: undecided+=1; rows.append((n,txt,'cell on %d pages'%len(ps),None)); continue
    p=ps.pop()
    if p not in pg_start: undecided+=1; rows.append((n,txt,'page %d not in stream'%p,None)); continue
    lo,hi=page_letter_range(p)
    hits=[m.start(1) for m in MK.finditer(PG.text[lo:hi]) if int(m.group(1))==n]
    cands={para_of(lo+h) for h in hits}
    cands.discard(None)
    if len(cands)!=1: undecided+=1; rows.append((n,txt,'%d marker sites on p%d -> %s'%(len(hits),p,sorted(cands)),None)); continue
    truth=cands.pop()
    inA=truth in fa[k]; inB=truth in fb[k]
    if inA and not inB: winA+=1; v='A'
    elif inB and not inA: winB+=1; v='B'
    elif inA and inB: v='both'
    else: neither+=1; v='neither'
    rows.append((n,txt,'p%d -> ord%d  A%s B%s'%(p,truth,fa[k],fb[k]),v))
print('DISPUTED NOTES ADJUDICATED BY PRINTED POSITION: %d'%len(dis))
print('  route A right: %d   route B right: %d   neither: %d   undecided: %d'
      %(winA,winB,neither,undecided))
for n,t,d,v in rows[:40]: print('   %-7s n=%-3s %-46s %r'%(v,n,d,t[:44]))
