#!/usr/bin/env python3
"""Rebuild cross-layer links on unique keys (<VOL>#<ordinal>).
Primary join: within each concordance group, match canon->commentary/Ṭīkā by
diacritic-folded, prefix-matched sutta name + paragraph number, interval
fallback (exact number => 'direct'; largest commentary number <= canon =>
'covered'). Union fallback: where the precise join misses, convert the existing
(tuned) link to a unique key so coverage never regresses. All keys unique =>
safe against duplicate paragraph numbers."""
import json,os,re
from collections import defaultdict
FOLD={'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'}
def fold(s):
    s=(s or '').lower()
    return re.sub(r'[^a-z]','',''.join(FOLD.get(c,c) for c in s))   # letters only (drop digits/marks)
def load(vol): return json.load(open(f'site/{vol}.json'))['paragraphs']

def build_index(vols):
    # folded sutta -> {vol: sorted [(n,key)]}
    idx=defaultdict(lambda: defaultdict(list))
    for v in vols:
        try: ps=load(v)
        except: continue
        for p in ps:
            if p.get('n') is not None: idx[fold(p.get('sutta'))][v].append((p['n'],p['key']))
    for k in idx:
        for v in idx[k]: idx[k][v].sort()
    return idx

def build_target_resolver(vols):
    """(vol) union: id -> [(n,key)] for converting old links to keys"""
    res=defaultdict(list)
    for v in vols:
        try: ps=load(v)
        except: continue
        for p in ps: res[p['id']].append((p.get('n'),p['key']))
    return res

def match_sutta(keys, cs):
    if not cs: return None
    if cs in keys: return cs
    ext=[k for k in keys if k and k.startswith(cs)]
    if ext: return min(ext,key=len)
    pre=[k for k in keys if k and cs.startswith(k)]
    if pre: return max(pre,key=len)
    return None

def resolve_join(idx, keys, cs, n):
    ms=match_sutta(keys, cs)
    if ms is None or n is None: return []
    out=[]
    for v,lst in idx[ms].items():
        exact=[k for (num,k) in lst if num==n]
        if exact: out.append({'key':exact[0],'state':'direct','n':n}); continue
        le=[(num,k) for (num,k) in lst if num<=n]
        if le: num,k=le[-1]; out.append({'key':k,'state':'covered','n':num})
    return out

def resolve_old(link, resolver):
    """convert an old link {vol,id,n} to {key,state,n} via (id,n)"""
    if not link: return None
    cand=resolver.get(link.get('id'))
    if not cand: return None
    n=link.get('n')
    exact=[k for (nn,k) in cand if nn==n]
    key=exact[0] if exact else cand[0][1]
    return {'key':key,'state':link.get('state','covered'),'n':n,'via':'converted'}

def main():
    m=json.load(open('site/reader/manifest.json'))
    total=withc=witht=fromjoin=fromold=0
    for g in m['groups']:
        avols=g.get('commentary',[]) or []; tvols=g.get('subcommentary',[]) or []
        aidx=build_index(avols); akeys=list(aidx.keys()); ares=build_target_resolver(avols)
        tidx=build_index(tvols); tkeys=list(tidx.keys()); tres=build_target_resolver(tvols)
        for cv in (g.get('canon',[]) or []):
            try: ps=load(cv)
            except: continue
            oldf=f'site/reader/links/{cv}.fwd.json'
            old=json.load(open(oldf)) if os.path.exists(oldf) else {}
            out={}
            for i,p in enumerate(ps):
                cs=fold(p.get('sutta')); n=p.get('n')
                c=resolve_join(aidx,akeys,cs,n)
                t=resolve_join(tidx,tkeys,cs,n)
                if c: fromjoin+=1
                ol=old.get(str(n)) or {}
                if not c:
                    oc=resolve_old(ol.get('commentary'), ares)
                    if oc: c=[oc]; fromold+=1
                if not t:
                    ot=resolve_old(ol.get('subcommentary'), tres)
                    if ot: t=[ot]
                total+=1
                if c: withc+=1
                if t: witht+=1
                if c or t: out[str(i)]={'commentary':c,'subcommentary':t}
            json.dump(out, open(f'site/reader/linksk/{cv}.links.json','w'), ensure_ascii=False)
    print(f'canon paras {total:,} | commentary {withc:,} ({100*withc/total:.1f}%) | subcommentary {witht:,} ({100*witht/total:.1f}%)')
    print(f'  commentary links from precise join: {fromjoin:,} | from converted-old fallback: {fromold:,}')
if __name__=='__main__': main()
