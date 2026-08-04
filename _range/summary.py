import json,os,sys,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec=importlib.util.spec_from_file_location('m','/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/_range/measure.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ROOT=m.ROOT
LK=f'{ROOT}/site/reader/linksk'
vols=[f[:-len(".links.json")] for f in sorted(os.listdir(LK)) if f.endswith('.links.json')]
import os as _o
m.LAYER=_o.environ.get('LAYER','commentary')
vols=[a for a in sys.argv[1:] if not a.startswith('-')] or vols
tot=collections.Counter(); disagree=[]
per={}
for cv in vols:
    try: out=m.compute(cv)
    except Exception as e: print('ERR',cv,e); continue
    b=a=0; grow=0; n_nc=0; agree=0; arith_over=0; arith_under=0; onlyb=0; onlyn=0; neither=0
    for tv,(res,unm) in out.items():
        for r in res:
            if r['dup']: continue
            b+=1; a+= r['end']-r['o']+1
            if r['src']=='not-in-concordance': n_nc+=1; continue
            if r['end']>r['o']: grow+=1
            nx,bd=r['nxt'],r['b']
            if nx is not None and bd is not None:
                if nx==bd: agree+=1
                elif bd<nx: arith_over+=1; disagree.append((cv,tv,r['canon'],r['o'],nx,bd))
                else: arith_under+=1
            elif bd is not None: onlyb+=1
            elif nx is not None: onlyn+=1
            else: neither+=1
    per[cv]=(b,a,grow,n_nc,agree,arith_over,arith_under,onlyb,onlyn,neither)
    tot['before']+=b; tot['after']+=a; tot['grow']+=grow; tot['nc']+=n_nc
    tot['agree']+=agree; tot['arith_over']+=arith_over; tot['arith_under']+=arith_under
    tot['onlyb']+=onlyb; tot['onlyn']+=onlyn; tot['neither']+=neither
print('volumes:',len(per))
print('drawn A paragraphs  before=%d  after=%d  (+%d, x%.2f)'%(tot['before'],tot['after'],tot['after']-tot['before'],tot['after']/max(1,tot['before'])))
print('links that grow: %d of %d expandable'%(tot['grow'],tot['before']-tot['nc']))
print('refused (target volume not in concordance): %d'%tot['nc'])
both=tot['agree']+tot['arith_over']+tot['arith_under']
print('BOTH bounds present: %d  -> agree %d (%.1f%%)  headings clip arithmetic %d (%.1f%%)  arithmetic clips headings %d (%.1f%%)'
      %(both,tot['agree'],100*tot['agree']/max(1,both),tot['arith_over'],100*tot['arith_over']/max(1,both),tot['arith_under'],100*tot['arith_under']/max(1,both)))
print('boundary only: %d   next-target only: %d   neither (single ¶ or head fallback): %d'%(tot['onlyb'],tot['onlyn'],tot['neither']))
print()
print('%-10s %7s %7s %6s %6s'%('canonvol','before','after','grow','refuse'))
for cv,v in sorted(per.items(), key=lambda kv:-(kv[1][1]-kv[1][0]))[:14]:
    print('%-10s %7d %7d %6d %6d'%(cv,v[0],v[1],v[2],v[3]))
print()
print('sample of arithmetic-crosses-a-section-end (canon, target, nextTarget, boundary):')
for d in disagree[:12]: print('   ',d)
