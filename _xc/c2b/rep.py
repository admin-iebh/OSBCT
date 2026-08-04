import sys, json
sys.path.insert(0,'pipeline')
import build_khu_volume as B
vol=sys.argv[1]
B.use(vol)
v,s,u,h,inc,rep=B.build()
bk=rep['books'][0]
print('unnum_prose',bk.get('unnum_prose'),'printed_units',bk['printed_units'],'corpus',bk['corpus_paras'],'gathas',len(bk['gathas']))
un=rep.get('unnumbered',[])
print('unnumbered ords:',un[:40],'... n=',len(un))
print('unnum_unaligned:',len(rep.get('unnum_unaligned',[])))
paras=json.load(open('site/%s.json'%vol))['paragraphs']
for o in un[:3]:
    print('--- ord',o,'len',len(paras[o]['text']),repr(paras[o]['text'][:200]))
print('verse keys sample', list(v)[:12], 'total', len(v))
for k in ['2','3','4']:
    print('verse[%s]='%k, json.dumps(v.get(k),ensure_ascii=False)[:300])
