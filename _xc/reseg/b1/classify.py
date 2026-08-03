# What CLASS are the collisions -- shipped, and re-segmented?
import json,collections
R='/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/'
V='20KhuA01'
def cls(ps):
    by=collections.defaultdict(list)
    for i,p in enumerate(ps): by[p['id']].append(i)
    groups={k:v for k,v in by.items() if len(v)>1}
    c=collections.Counter()
    for k,v in groups.items():
        kinds=set('num' if ps[i].get('n') is not None else 'unnum' for i in v)
        pages=set(ps[i].get('pdf_page') for i in v)
        c[(tuple(sorted(kinds)), 'samepage' if len(pages)==1 else 'multipage')]+=1
    return by,groups,c
for name,path in (('shipped','site/%s.json'%V),('reseg','_xc/reseg/%s.json'%V)):
    ps=json.load(open(R+path))['paragraphs']
    by,g,c=cls(ps)
    print('%-8s %d ¶  %d distinct  %d colliding ids  worst %d-way'%(name,len(ps),len(by),len(g),max([len(v) for v in by.values()])))
    print('   classes:',dict(c))
    if name=='shipped':
        for k,v in g.items():
            print('   ',k,v,[ps[i].get('n') for i in v],[ps[i].get('pdf_page') for i in v])
