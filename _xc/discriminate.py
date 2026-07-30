"""Decide Dī-Ṭī 1/2/3 by CONTENT, not by page-range fit.

For each citation `Dī-Ṭī v. p` the citing note carries a lemma or variant
reading.  A correct target volume should contain that string on or about
printed page p; a wrong one should not.  Candidates are scored on the same
citations, so the comparison is like-for-like.
"""
import json,glob,re,collections,unicodedata
def norm(s): return re.sub(r'[^a-zāīūṁṅñṭḍṇḷ ]','',(s or '').lower())
VOLTEXT={}
def pagetext(vol,pg,w=1):
    if vol not in VOLTEXT:
        ps=json.load(open(f'site/{vol}.json'))['paragraphs']
        m=collections.defaultdict(list)
        for p in ps:
            pr=p.get('printed')
            if isinstance(pr,int): m[pr].append(norm(p.get('text','')))
        VOLTEXT[vol]=m
    m=VOLTEXT[vol]
    return ' '.join(' '.join(m.get(pg+d,[])) for d in range(-w,w+1))
SEG=re.compile(r'(Dī-Ṭī)\.?\s*(?:(\d+)\s*\.\s*)?(\d+)')
cites=[]
for f in sorted(glob.glob('site/reader/apparatus/*.appk.json')):
    st=[json.load(open(f))]
    while st:
        o=st.pop()
        if isinstance(o,dict):
            if 'text' in o and 'xrefs' in o:
                t=o.get('text') or ''
                m=SEG.search(t)
                if m and m.group(2):
                    # the note's own lemma: its variants' readings, else the words before the citation
                    lem=[v.get('reading') for v in (o.get('variants') or []) if v.get('reading')]
                    if not lem:
                        pre=t[:m.start()].strip(' ,;')
                        lem=[pre.split(',')[0]] if pre else []
                    lem=[norm(x) for x in lem if x and len(norm(x))>=8]
                    if lem: cites.append((int(m.group(2)),int(m.group(3)),lem))
            st.extend(o.values())
        elif isinstance(o,list): st.extend(o)
CAND={'A vagga-ṭīkā  ':['08DiT01','11DiT04','12DiT05'],
      'B abhinava-ṭīkā':['08DiT01','09DiT02','10DiT03']}
print('citations with a usable lemma:',len(cites))
for name,arr in CAND.items():
    hit=0;tot=0
    for vol,pg,lems in cites:
        if not(0<vol<=len(arr)): continue
        tot+=1
        txt=pagetext(arr[vol-1],pg,2)
        if any(l in txt for l in lems): hit+=1
    print(f'  {name}  {arr}  lemma found on/near the cited page: {hit}/{tot}  ({100*hit/max(tot,1):.1f}%)')
