#!/usr/bin/env python3
"""Measure the range rule: before (one paragraph per link) vs after (a run)."""
import json,re,sys,os,collections
ROOT='/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
D={}
def vol(v):
    if v not in D: D[v]=json.load(open(f'{ROOT}/site/{v}.json'))
    return D[v]
S={}
def sec(v):
    if v not in S:
        try: S[v]=json.load(open(f'{ROOT}/site/reader/sections/{v}.json'))
        except Exception: S[v]={}
    return S[v]
def fold(s):
    s=(s or '').lower()
    for a,b in [('ā','a'),('ī','i'),('ū','u'),('ṁ','m'),('ṃ','m'),('ṅ','n'),('ñ','n'),('ṭ','t'),('ḍ','d'),('ṇ','n'),('ḷ','l')]:
        s=s.replace(a,b)
    return re.sub(r'[^a-z ]','',s).strip()
def strip_num(t): return re.sub(r'^\s*\d+(-\d+)?\.\s*','',(t or '').strip())
def is_end(t):
    w=fold(t).split()
    return bool(w) and any(w[-1].endswith(x) for x in ('nitthita','nitthitam','nitthito','samatta','samattam','samatto'))

B={}
def bounds(v):
    """work-level boundary ordinals in volume v: colophon-attested + numbered heads."""
    if v in B: return B[v]
    d=vol(v); heads=d.get('headings',[]); sm=sec(v)
    anch=[]
    for o in sorted(sm,key=int):
        for x in sm[o]: anch.append((int(o), fold(strip_num(x.get('l') or '')), x.get('l') or ''))
    colo=set(); unmatched=[]
    ptr=0
    for i,h in enumerate(heads):
        if not is_end(h.get('title')): continue
        j=i+1
        while j<len(heads) and (re.match(r'^[_\s.]*$',heads[j].get('title') or '') or is_end(heads[j].get('title'))): j+=1
        if j>=len(heads): unmatched.append((h.get('title'),'EOV')); continue
        want=fold(strip_num(heads[j]['title']))
        if len(want)<4: unmatched.append((h.get('title'),'SHORT')); continue
        hit=None
        for k in range(ptr,len(anch)):
            if anch[k][1]==want: hit=k;break
        if hit is None:
            for k in range(len(anch)):
                if anch[k][1]==want: hit=k;break
        if hit is None: unmatched.append((h.get('title'),heads[j]['title'])); continue
        ptr=hit+1; b_=anch[hit][0]; ps=d['paragraphs']
        if 0<b_<len(ps):
            pc=h.get('printed'); pa=ps[b_-1].get('printed'); pb=ps[b_].get('printed')
            if pc is not None and pa is not None and pb is not None and not (pa<=pc<=pb): continue
        colo.add(b_)
    numbered=set(int(o) for o in sm for x in sm[o] if re.match(r'^\d+\.\s',x.get('l') or ''))
    B[v]=(colo,numbered,unmatched)
    return B[v]

def allheads(v): return sorted(int(o) for o in sec(v))

CONC=None
def group_of(v):
    global CONC
    if CONC is None:
        c=json.load(open(f'{ROOT}/site/concordance.json'))
        CONC={}
        for g in c['groups']:
            for k in ('canon','commentary','subcommentary'):
                for f in ((g.get(k) or {}).get('files') or []): CONC[f]=g['group']
    return CONC.get(v)

LAYER='commentary'
def compute(canonvol):
    links=json.load(open(f'{ROOT}/site/reader/linksk/{canonvol}.links.json'))
    # per target volume, ordered list of (canonOrd, tgtOrd)
    per=collections.defaultdict(list)
    for k in sorted(links,key=int):
        for t in (links[k].get(LAYER) or []):
            if t.get('state')!='direct': continue
            tv,to=t['key'].rsplit('#',1)
            per[tv].append((int(k),int(to)))
    out={}
    for tv,L in per.items():
        allowed = group_of(tv)==group_of(canonvol) and group_of(tv) is not None
        colo,numbered,unm=bounds(tv)
        BND=sorted(colo|numbered)
        HD=allheads(tv)
        n=len(vol(tv)['paragraphs'])
        seen=set(); res=[]
        O=sorted(set(o2 for (_,o2) in L))
        for idx,(ci,o) in enumerate(L):
            nxt=min([x for x in O if x>o], default=None)
            b=min([x for x in BND if x>o], default=None)
            src=None
            if nxt is None and b is None:
                c=min([x for x in HD if x>o], default=None)
                end=(c-1) if c is not None else o; src='head' if c is not None else 'none'
            else:
                cand=[x for x in (nxt,b) if x is not None]
                end=min(cand)-1
                src=('target' if nxt is not None and nxt==min(cand) else 'bound')
                if nxt is not None and b is not None and nxt==b: src='both'
            if not allowed: end=o; src='not-in-concordance'
            end=max(end,o); end=min(end,n-1)
            dup = (tv,o) in seen; seen.add((tv,o))
            res.append(dict(canon=ci,o=o,end=end,src=src,dup=dup,nxt=nxt,b=b))
        out[tv]=(res,unm)
    return out

if __name__=='__main__':
    for cv in sys.argv[1:]:
        out=compute(cv)
        print(f'===== {cv}')
        for tv,(res,unm) in sorted(out.items()):
            n=len(vol(tv)['paragraphs'])
            live=[r for r in res if not r['dup']]
            before=len(live)                      # one paragraph each
            after=sum(r['end']-r['o']+1 for r in live)
            longer=[r for r in live if r['end']>r['o']]
            srcs=collections.Counter(r['src'] for r in live)
            print(f'  -> {tv} ({n} ¶): {len(res)} direct links, {len(live)} distinct targets')
            print(f'     drawn ¶ before={before}  after={after}  (+{after-before}); {len(longer)} links grow; sources={dict(srcs)}')
            if unm: print(f'     unmatched colophons: {unm[:4]}')
            mx=sorted(live,key=lambda r:-(r["end"]-r["o"]))[:5]
            print('     longest runs:', [(r['canon'],f"{r['o']}..{r['end']}",r['src']) for r in mx])
