import sys, json, os
sys.path.insert(0,'pipeline')
import build_khu_volume as B
vol=sys.argv[1]
B.use(vol)
v,s,u,h,inc,rep=B.build()
bk=rep['books'][0]
mx=rep.get('unnum_mixed',[])
print(vol,'unnum_prose',bk.get('unnum_prose'),'mixed',len(mx),
      'mixed vlines',sum(x['vlines'] for x in mx),
      'reclass',len(rep.get('unnum_reclass',[])),
      'units',bk['printed_units'],'corpus',bk['corpus_paras'],'FATAL',bk.get('FATAL'))
print('mixed sample',mx[:8])
for k in ['2','3','4']:
    print('verse[%s]='%k, json.dumps(v.get(k),ensure_ascii=False)[:400])
print('sect[2]=',json.dumps(s.get('2'),ensure_ascii=False)[:200])
