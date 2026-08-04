import sys
sys.path.insert(0,'pipeline')
import build_khu_volume as B
for v in [l.strip() for l in open('_xc/c2b/changedvols.txt')]:
    s=B.SPEC.get(v)
    if not s: continue
    for bk in s['books']:
        print('%s %d %d %d %d'%(v,bk[1]-1,bk[2],bk[3],bk[4]))
