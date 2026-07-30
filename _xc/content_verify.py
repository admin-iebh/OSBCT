"""Content check on every proposed mapping: does the citing note's own lemma
occur on or near the cited page of the proposed target volume?

The absolute rate is a floor, not a measure — the lemma is extracted crudely and
a note often cites a parallel rather than a quotation.  What matters is the
CONTRAST against a control: the same citations resolved to a deliberately wrong
volume of the same layer.  A mapping that is right beats its control; one that
is wrong does not.
"""
import json,glob,re,collections,sys
def norm(s): return re.sub(r'[^a-zāīūṁṅñṭḍṇḷ ]','',(s or '').lower())
VT={}
def pagetext(vol,pg,w=2):
    if vol not in VT:
        m=collections.defaultdict(list)
        for p in json.load(open(f'site/{vol}.json'))['paragraphs']:
            pr=p.get('printed')
            if isinstance(pr,int): m[pr].append(norm(p.get('text','')))
        VT[vol]=m
    return ' '.join(' '.join(VT[vol].get(pg+d,[])) for d in range(-w,w+1))
MAP=json.load(open('_xc/map.json'))
LONG='|'.join(sorted(MAP['long'],key=len,reverse=True))
SEG=re.compile(r'\b((?:'+LONG+r'|[A-ZĀĪŪṀ][a-zāīūṁṅñṭḍṇḷ]{0,6})(?:-Ṭṭha|-Tṭha|-Ṭī|-Anuṭī)?)\.?\s*(?:(\d+)\s*\.\s*)?(\d+)')
def target(work,vol):
    for suf,key in (('-Ṭṭha','comm'),('-Tṭha','comm'),('-Anuṭī','tika'),('-Ṭī','tika')):
        if work.endswith(suf):
            arr=MAP[key].get(work[:-len(suf)])
            break
    else:
        arr=MAP['bare'].get(work)
    if not arr: return None
    i=(vol or 1)-1
    return arr[i] if 0<=i<len(arr) else None
cites=collections.defaultdict(list)
for f in sorted(glob.glob('site/reader/apparatus/*.appk.json')):
    st=[json.load(open(f))]
    while st:
        o=st.pop()
        if isinstance(o,dict):
            if 'text' in o and 'xrefs' in o:
                t=o.get('text') or ''
                for seg in re.split(r'[;]',t):
                    m=SEG.search(seg)
                    if not m: continue
                    w=m.group(1); tv=target(w,int(m.group(2)) if m.group(2) else None)
                    if not tv: continue
                    lem=[norm(v.get('reading')) for v in (o.get('variants') or []) if v.get('reading')]
                    if not lem:
                        pre=seg[:m.start(1)].strip(' ,;“”')
                        lem=[norm(pre.split(',')[0])]
                    lem=[l for l in lem if len(l)>=8]
                    if lem: cites[w].append((tv,int(m.group(3)),lem))
            st.extend(o.values())
        elif isinstance(o,list): st.extend(o)
ALL=sorted({v for arr in list(MAP['comm'].values())+list(MAP['tika'].values())+list(MAP['bare'].values()) for v in arr})
print(f"{'siglum':18s} {'n':>4s} {'hit':>6s}  {'control':>7s}")
tot=collections.Counter()
for w in sorted(cites,key=lambda w:-len(cites[w])):
    rows=[r for r in cites[w] if r[0] in VT or True]
    hit=ctl=0
    for tv,pg,lem in rows:
        if any(l in pagetext(tv,pg) for l in lem): hit+=1
        cv=ALL[(ALL.index(tv)+7)%len(ALL)]          # a fixed wrong volume, same layer pool
        try:
            if any(l in pagetext(cv,pg) for l in lem): ctl+=1
        except Exception: pass
    n=len(rows); tot['n']+=n; tot['hit']+=hit; tot['ctl']+=ctl
    print(f'{w:18s} {n:4d} {hit:4d} {100*hit/n:4.0f}%  {ctl:4d} {100*ctl/n:3.0f}%')
print(f"\nTOTAL              {tot['n']:4d} {tot['hit']:4d} {100*tot['hit']/tot['n']:4.0f}%  {tot['ctl']:4d} {100*tot['ctl']/tot['n']:3.0f}%")
