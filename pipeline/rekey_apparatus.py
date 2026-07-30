#!/usr/bin/env python3
"""Re-key apparatus from id-keyed to ordinal-keyed, disambiguating duplicate-id
groups by matching footnote marker numbers in each paragraph's text. Also
measures true data loss (dup-id members whose markers have no surviving note)."""
import json,glob,os,re,sys
from collections import defaultdict
MARK=re.compile(r'[a-zāīūṁṅñṭḍṇḷ](\d{1,2})\b')
def markers(txt): return set(int(m) for m in MARK.findall(txt or ''))
OUT='site/reader/apparatus'
def rekey(vol):
    appf=f'{OUT}/{vol}.app.json'
    if not os.path.exists(appf): return None
    app=json.load(open(appf))
    paras=json.load(open(f'site/{vol}.json'))['paragraphs']
    byid=defaultdict(list)
    for i,p in enumerate(paras): byid[p['id']].append(i)
    out={}; lost_paras=0; lost_notes=0; distributed=0
    for pid,notes in app.items():
        idxs=byid.get(pid,[])
        if not idxs: continue
        if len(idxs)==1:
            out[str(idxs[0])]=notes; continue
        # duplicate id: attach each note to the member whose text carries its marker number
        distributed+=1
        assigned=defaultdict(list)
        for nt in notes:
            n=nt.get('n')
            targets=[i for i in idxs if n in markers(paras[i]['text'])] if n else []
            if targets:
                for t in targets[:1]: assigned[t].append(nt)  # first match
            else:
                # can't place -> attach to first member (best effort)
                assigned[idxs[0]].append(nt)
        for i,nl in assigned.items(): out[str(i)]=out.get(str(i),[])+nl
        # true loss: members that HAVE markers but received NO notes for them
        for i in idxs:
            mk=markers(paras[i]['text'])
            got=set(nt.get('n') for nt in out.get(str(i),[]))
            missing=mk-got
            if missing:
                lost_paras+=1; lost_notes+=len(missing)
    json.dump(out, open(f'{OUT}/{vol}.appk.json','w'), ensure_ascii=False)
    return {'vol':vol,'dup_ids':distributed,'lost_paras':lost_paras,'lost_notes':lost_notes,'entries':len(out)}

if __name__=='__main__':
    vols=[os.path.basename(f).replace('.app.json','') for f in glob.glob(f'{OUT}/*.app.json')]
    tot=defaultdict(int); rows=[]
    for v in sorted(vols):
        r=rekey(v)
        if r:
            rows.append(r)
            for k in ('dup_ids','lost_paras','lost_notes','entries'): tot[k]+=r[k]
    print(f"volumes {len(rows)} | ordinal entries {tot['entries']:,} | dup-id groups distributed {tot['dup_ids']:,}")
    print(f"TRUE LOSS — paragraphs with unrecoverable markers: {tot['lost_paras']:,} | missing notes: {tot['lost_notes']:,}")
    for r in sorted(rows,key=lambda x:-x['lost_paras'])[:10]:
        if r['lost_paras']: print(f"  {r['vol']:12s} lost_paras={r['lost_paras']:4d} lost_notes={r['lost_notes']:4d}")
