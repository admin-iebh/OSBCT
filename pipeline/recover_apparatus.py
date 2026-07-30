#!/usr/bin/env python3
"""Targeted recovery: for paragraphs whose footnote markers have no note after
re-keying, re-read the volume's page-notes (via extract.py) and attach the
matching note by number on the paragraph's printed page (then the next page)."""
import json,glob,os,re,sys,time
sys.path.insert(0,'pipeline'); import extract as EX
MARK=re.compile(r'[a-zāīūṁṅñṭḍṇḷ](\d{1,2})\b')
def markers(t): return [int(m) for m in MARK.findall(t or '')]
FOLDER={'canon':'pali-unicode','commentary':'atthakatha-unicode','subcommentary':'tika-unicode'}
def pdfpath(vol):
    for f in FOLDER.values():
        p=f'{f}/{vol}.pdf'
        if os.path.exists(p): return p
def lost_paras(vol):
    appk=json.load(open(f'site/reader/apparatus/{vol}.appk.json'))
    paras=json.load(open(f'site/{vol}.json'))['paragraphs']
    out=[]
    for i,p in enumerate(paras):
        mk=set(markers(p['text']))
        if not mk: continue
        got=set(nt.get('n') for nt in appk.get(str(i),[]))
        miss=mk-got
        if miss: out.append((i,p.get('pdf_page'),miss))
    return appk,paras,out
def recover(vol,budget_left):
    appk,paras,lost=lost_paras(vol)
    if not lost: return 0
    pgs,_,_=EX.extract(pdfpath(vol))
    notes_by_page={p['pdf_page']:{nt['n']:nt for nt in p.get('notes',[]) if nt.get('n')} for p in pgs}
    filled=0
    for i,pp,miss in lost:
        cur=appk.get(str(i),[])
        have=set(nt.get('n') for nt in cur)
        for n in sorted(miss):
            note=None
            for cand in (pp,(pp+1) if pp else None):
                if cand in notes_by_page and n in notes_by_page[cand]:
                    note=notes_by_page[cand][n]; break
            if note and n not in have:
                # keep same shape as existing apparatus notes
                rec={'n':n,'text':note.get('text'),'variants':note.get('variants',[]),'xrefs':note.get('xrefs',[])}
                cur.append(rec); have.add(n); filled+=1
        cur.sort(key=lambda x:(x.get('n') or 999))
        appk[str(i)]=cur
    json.dump(appk, open(f'site/reader/apparatus/{vol}.appk.json','w'), ensure_ascii=False)
    return filled
if __name__=='__main__':
    t0=time.time(); budget=float(os.environ.get('APP_BUDGET','40'))
    # find volumes with any loss
    vols=[]
    for f in glob.glob('site/reader/apparatus/*.appk.json'):
        vol=os.path.basename(f).replace('.appk.json','')
        _,_,lost=lost_paras(vol)
        if lost: vols.append((vol,len(lost)))
    vols.sort(key=lambda x:-x[1])
    done_marker='/tmp/app_recovered.txt'
    done=set(open(done_marker).read().split()) if os.path.exists(done_marker) else set()
    total=0
    for vol,nl in vols:
        if vol in done: continue
        if time.time()-t0>budget: print('...budget'); break
        f=recover(vol,budget-(time.time()-t0)); total+=f
        done.add(vol); open(done_marker,'a').write(vol+' ')
        print(f'{vol:12s} lost_paras={nl:4d} notes_filled={f:4d}')
    print(f'filled {total} notes this run; {len(vols)} vols had losses')
