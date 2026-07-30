import json,glob,re,collections,sys
P=json.load(open('site/reader/pageindex.json'))
RANGE={v:(min(int(k) for k in P[v] if k.lstrip("-").isdigit()),
          max(int(k) for k in P[v] if k.lstrip("-").isdigit())) for v in P}
SEG=re.compile(r'([A-ZĀĪŪṀ][A-Za-zāīūṁṅñṭḍṇḷĀĪŪṀ]{0,14}(?:-(?:Ṭṭha|Tṭha))?)\.?\s*(?:(\d+)\s*\.\s*)?(\d+(?:-\d+)?)\s*(?=[,;]|\s|$)')
TAIL=re.compile(r'piṭṭh(?:e|esu|epi|esupi|ādīsu|ādīsupi)',re.I)
PROP={
 'Khuddakapāṭha':['20KhuA01'],'Dhammapada':['21KhuA02','22KhuA03'],'Udāna':['23KhuA04'],
 'Itivuttaka':['24KhuA05'],'Suttanipāta':['25KhuA06','26KhuA07'],'Vimāna':['27KhuA08'],
 'Peta':['28KhuA09'],'Theragāthā':['29KhuA10','30KhuA11'],'Thera':['29KhuA10','30KhuA11'],
 'Therīgāthā':['31KhuA12'],'Apadāna':['32KhuA13','33KhuA14'],'Apādāna':['32KhuA13','33KhuA14'],
 'Buddhavaṁsa':['34KhuA15'],'Cariyāpiṭaka':['35KhuA16'],'Cariyā':['35KhuA16'],
 'Jātaka':['36KhuA17','37KhuA18','38KhuA19','39KhuA20','40KhuA21','41KhuA22','42KhuA23'],
 'Mahāniddesa':['43KhuA24'],'Cūḷaniddesa':['44KhuA25'],'Netti':['45KhuA26'],
 'Paṭisaṁ':['46KhuA27','47KhuA28'],'Paṭisam':['46KhuA27','47KhuA28'],'Paṭīsaṁ':['46KhuA27','47KhuA28'],
 'Kaṅkhā':['05Kankha'],'Vinayasaṅgaha':['06VinSg06'],
}
UNSUF={'Visuddhi':['51Vism01','52Vism02']}
stat=collections.defaultdict(lambda:[0,0,[]])
for f in sorted(glob.glob('site/reader/apparatus/*.appk.json')):
    src=f.split('/')[-1].split('.')[0]
    j=json.load(open(f))
    st=[j]
    while st:
        o=st.pop()
        if isinstance(o,dict):
            if 'xrefs' in o and 'text' in o:
                t=o.get('text') or ''
                if TAIL.search(t):
                    for seg in re.split(r'[;]',t):
                        m=SEG.search(seg)
                        if not m: continue
                        w=m.group(1); vol=int(m.group(2)) if m.group(2) else None
                        pg=int(m.group(3).split('-')[0])
                        base,arr=None,None
                        if w.endswith('-Ṭṭha') or w.endswith('-Tṭha'):
                            base=w[:-5]; arr=PROP.get(base)
                        else:
                            base=w; arr=UNSUF.get(base)
                        if not arr: continue
                        idx=(vol or 1)-1
                        key=base
                        s=stat[key]; s[0]+=1
                        if idx<0 or idx>=len(arr): s[2].append((src,w,vol,pg,'VOL-OOR')); continue
                        tv=arr[idx]; lo,hi=RANGE.get(tv,(0,0))
                        if lo<=pg<=hi: s[1]+=1
                        else: s[2].append((src,w,vol,pg,f'{tv} {lo}-{hi}'))
            st.extend(o.values())
        elif isinstance(o,list): st.extend(o)
print(f"{'work':16s} {'n':>5s} {'inrange':>7s} {'pct':>6s}")
for k in sorted(stat,key=lambda k:-stat[k][0]):
    n,ok,bad=stat[k]
    print(f"{k:16s} {n:5d} {ok:7d} {100*ok/n:5.1f}%")
print()
for k in sorted(stat,key=lambda k:-stat[k][0]):
    n,ok,bad=stat[k]
    if bad:
        print(f"--- {k}: {len(bad)} out of range")
        for b in bad[:8]: print('    ',b)
