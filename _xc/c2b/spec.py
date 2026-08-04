import sys, json
sys.path.insert(0,'pipeline')
import build_khu_volume as B
ks=[]
for v,s in B.SPEC.items():
    modes=set((bk[6] if len(bk)>6 else 'verse') for bk in s.get('books',[]))
    ks.append((v,sorted(modes)))
for v,m in sorted(ks): print(v,m)
print('total',len(ks))
