import re,collections,sys
sys.path.insert(0,'pipeline')
import extract as E
pgs=E.raw_pages('atthakatha-unicode/20KhuA01.pdf')
LO,HI=19,234   # 1-based pdf pages of the body, from site/20KhuA01.json
c=collections.Counter(); byline=[]
for i,pg in enumerate(pgs,1):
    if not (LO<=i<=HI): continue
    d=E.split_page(pg)
    if not d: continue
    for ln in d['body']:
        if not ln.strip(): continue
        ind=len(ln)-len(ln.lstrip())
        c[ind]+=1; byline.append((i,ind,ln.strip()))
tot=sum(c.values())
print('body lines in pdf pages %d-%d: %d'%(LO,HI,tot))
for k in sorted(c): print('  indent %3d  %6d  %5.2f%%'%(k,c[k],100*c[k]/tot))
