import json,os,sys,collections
def tot(d):
    t=collections.Counter(); per={}
    for f in sorted(os.listdir(d)):
        r=json.load(open(os.path.join(d,f)))
        s=r['stats']
        n=r['printed_lines']-s.get('edge_lines',0)-s.get('index_lines',0)
        miss=s.get('absent',0)+s.get('partial',0)-s.get('edge_absent',0)-s.get('index_absent',0)
        row=dict(c1=s.get('PROSE_AS_VERSE',0),c2=s.get('VERSE_AS_PROSE',0),
                 c3=s.get('PROSE_AS_UDDANA',0),c4=s.get('VERSE_AS_HEADING',0),
                 miss=miss,pV=s.get('page_verse',0),pP=s.get('page_prose',0),
                 lone=s.get('lone_display',0),vok=s.get('verse_ok',0),
                 pok=s.get('prose_ok',0),digit=s.get('digit_only',0),n=n)
        per[r['vol']]=row
        for k,v in row.items(): t[k]+=v
    return t,per
a,pa=tot(sys.argv[1]); b,pb=tot(sys.argv[2])
print('%-8s %10s %10s %10s'%('','OLD','NEW','delta'))
for k in ('c1','c2','c3','c4','pV','pP','lone','vok','pok','miss','digit','n'):
    print('%-8s %10d %10d %+10d'%(k,a[k],b[k],b[k]-a[k]))
print()
print('largest class-2 movers')
d=sorted(pa, key=lambda v: pb[v]['c2']-pa[v]['c2'])
for v in d[:14]: print('  %-10s c2 %5d -> %5d (%+5d)   c1 %4d -> %4d   c4 %4d -> %4d'%(v,pa[v]['c2'],pb[v]['c2'],pb[v]['c2']-pa[v]['c2'],pa[v]['c1'],pb[v]['c1'],pa[v]['c4'],pb[v]['c4']))
print('  ...')
for v in d[-6:]: print('  %-10s c2 %5d -> %5d (%+5d)   c1 %4d -> %4d   c4 %4d -> %4d'%(v,pa[v]['c2'],pb[v]['c2'],pb[v]['c2']-pa[v]['c2'],pa[v]['c1'],pb[v]['c1'],pa[v]['c4'],pb[v]['c4']))
print()
print('largest class-1 risers')
d1=sorted(pa, key=lambda v: pa[v]['c1']-pb[v]['c1'])
for v in d1[:10]: print('  %-10s c1 %4d -> %4d (%+4d)  c2 %5d -> %5d'%(v,pa[v]['c1'],pb[v]['c1'],pb[v]['c1']-pa[v]['c1'],pa[v]['c2'],pb[v]['c2']))
json.dump({'old':pa,'new':pb},open('_xc/class2/census_cmp.json','w'))
