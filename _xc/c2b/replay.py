"""Builder-vs-shipped replay: build each volume in memory and compare the five
side-maps with what is on disk (or with a named suffix)."""
import sys, json, os, io
sys.path.insert(0,'pipeline')
import build_khu_volume as B
R='site/reader'
suf=os.environ.get('SUF','')
for vol in sys.argv[1:]:
    try:
        B.use(vol)
        v,s,u,h,inc,rep=B.build()
    except SystemExit as e:
        print('%-10s REFUSED %s'%(vol,e)); continue
    except Exception as e:
        print('%-10s ERROR %r'%(vol,e)); continue
    diffs=[]
    for n,d in (('verse',v),('sections',s),('uddana',u),('hide',h),('incipit',inc)):
        p='%s/%s/%s.json%s'%(R,n,vol,suf)
        if not os.path.exists(p):
            if d: diffs.append(n+':NOFILE(+%d)'%len(d))
            continue
        old=json.load(io.open(p,encoding='utf-8'))
        if old!=d:
            ks=set(map(str,old))|set(map(str,d))
            nd=sum(1 for k in ks if old.get(k)!=d.get(k))
            diffs.append('%s:%d/%d'%(n,nd,len(ks)))
    bad=[b for b in rep['books'] if b.get('FATAL')]
    mx=rep.get('unnum_mixed',[])
    print('%-10s mixed %4d (%5d vlines)  %s%s'%(vol,len(mx),sum(x['vlines'] for x in mx),
          'IDENTICAL' if not diffs else ' '.join(diffs),
          '  FATAL:'+str(bad[0]['FATAL'])[:60] if bad else ''))
