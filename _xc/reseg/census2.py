import re,collections,sys
sys.path.insert(0,'pipeline')
import extract as E
pgs=E.raw_pages('atthakatha-unicode/20KhuA01.pdf')
LO,HI=19,234
mins=collections.Counter(); pagemin={}
samples=collections.defaultdict(list)
for i,pg in enumerate(pgs,1):
    if not (LO<=i<=HI): continue
    d=E.split_page(pg)
    if not d: continue
    inds=[len(l)-len(l.lstrip()) for l in d['body'] if l.strip()]
    if not inds: continue
    pagemin[i]=min(inds); mins[min(inds)]+=1
    for l in d['body']:
        if not l.strip(): continue
        ind=len(l)-len(l.lstrip())
        if ind in (1,3,4,5,6,7,8,9,10,11) and len(samples[ind])<4:
            samples[ind].append((i,l.strip()[:88]))
print('per-page min body indent:', dict(sorted(mins.items())))
print('pages whose min indent != 0:', [p for p,m in pagemin.items() if m!=0][:30])
for k in sorted(samples):
    print('--- indent',k)
    for p,t in samples[k]: print('   p%-4d %s'%(p,t))
