import json,glob,re,collections
P=json.load(open('site/reader/pageindex.json'))
RANGE={v:(min(int(k) for k in P[v]),max(int(k) for k in P[v])) for v in P}
SEG=re.compile(r'([A-ZĀĪŪṀ][A-Za-zāīūṁṅñṭḍṇḷĀĪŪṀ]{0,14}(?:-(?:Ṭṭha|Tṭha|Ṭī|Anuṭī))?)\.?\s*(?:(\d+)\s*\.\s*)?(\d+(?:-\d+)?)\s*(?=[,;]|\s|$)')
TAIL=re.compile(r'piṭṭh',re.I)
# candidate assignments to TEST — several rivals for the ambiguous ones
CAND={
 'Sārattha-Ṭī':[['01ViT01','02ViT02','03ViT03']],
 'Vimati-Ṭī':[['04ViT04','05ViT05']],
 'Vajira-Ṭī':[['06ViT06']],
 'Dī-Ṭī':[['08DiT01','11DiT04','12DiT05'],
          ['08DiT01','09DiT02','10DiT03'],
          ['08DiT01','09DiT02','10DiT03','11DiT04','12DiT05']],
 'Ma-Ṭī':[['13MaT01','14MaT02','15MaT03']],
 'Saṁ-Ṭī':[['16SaT01','17SaT02']],
 'Aṁ-Ṭī':[['18AnT01','19AnT02','20AnT03']],
 'Netti-Ṭī':[['21KhuT01']],
 'Visuddhi-Ṭī':[['25VsmT01','26VsmT02']],
 'Mūlaṭī':[['22AbhiT01','23AbhiT02','24AbhiT03']],
 'Anuṭī':[['22AbhiT01','23AbhiT02','24AbhiT03']],
 'Mahāṭīkā':[['25VsmT01','26VsmT02']],
}
obs=collections.defaultdict(list)
for f in sorted(glob.glob('site/reader/apparatus/*.appk.json')):
    src=f.split('/')[-1].split('.')[0]
    st=[json.load(open(f))]
    while st:
        o=st.pop()
        if isinstance(o,dict):
            if 'xrefs' in o and 'text' in o:
                t=o.get('text') or ''
                if TAIL.search(t):
                    for seg in re.split(r'[;]',t):
                        m=SEG.search(seg)
                        if m and m.group(1) in CAND:
                            obs[m.group(1)].append((src,int(m.group(2)) if m.group(2) else None,int(m.group(3).split('-')[0])))
            st.extend(o.values())
        elif isinstance(o,list): st.extend(o)
for w in CAND:
    rows=obs.get(w,[])
    if not rows: print(f'{w:14s}  (no occurrences)'); continue
    print(f'{w:14s}  n={len(rows)}   vols cited: {sorted(set(v for _,v,_ in rows), key=lambda x:(x is None,x))}')
    for arr in CAND[w]:
        ok=bad=0; ex=[]
        for src,vol,pg in rows:
            i=(vol or 1)-1
            if not(0<=i<len(arr)): bad+=1; ex.append((src,vol,pg,'VOL-OOR')); continue
            lo,hi=RANGE[arr[i]]
            if lo<=pg<=hi: ok+=1
            else:
                bad+=1
                if len(ex)<4: ex.append((src,vol,pg,f'{arr[i]} {lo}-{hi}'))
        print(f'     {100*ok/len(rows):5.1f}%  {ok:4d}/{len(rows):4d}  {arr}')
        if bad and len(CAND[w])==1:
            for e in ex[:4]: print('           miss',e)
