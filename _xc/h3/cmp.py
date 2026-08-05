import json,sys,glob,collections,os
A,B=sys.argv[1],sys.argv[2]
K=('VERSE_AS_PROSE','PROSE_AS_VERSE','PROSE_AS_UDDANA','VERSE_AS_HEADING','lone_display','page_verse','page_prose','absent','partial','digit_only')
ta=collections.Counter(); tb=collections.Counter(); rows=[]
for f in sorted(glob.glob(A+'/*.json')):
    v=os.path.basename(f)[:-5]
    g=B+'/'+v+'.json'
    if not os.path.exists(g): print('MISSING',v); continue
    a=json.load(open(f)); b=json.load(open(g))
    assert a['printed_lines']==b['printed_lines'], (v,a['printed_lines'],b['printed_lines'])
    sa,sb=a['stats'],b['stats']
    for k in K: ta[k]+=sa.get(k,0); tb[k]+=sb.get(k,0)
    ta['printed']+=a['printed_lines']; tb['printed']+=b['printed_lines']
    d2=sb.get('VERSE_AS_PROSE',0)-sa.get('VERSE_AS_PROSE',0)
    d1=sb.get('PROSE_AS_VERSE',0)-sa.get('PROSE_AS_VERSE',0)
    d3=sb.get('PROSE_AS_UDDANA',0)-sa.get('PROSE_AS_UDDANA',0)
    d4=sb.get('VERSE_AS_HEADING',0)-sa.get('VERSE_AS_HEADING',0)
    if d1 or d2 or d3 or d4:
        rows.append((v,sa.get('VERSE_AS_PROSE',0),sb.get('VERSE_AS_PROSE',0),d1,d3,d4,
                     b.get('pages_lowered',0),b.get('pages_total',0),a['display_col']))
rows.sort(key=lambda r:-(r[2]-r[1]))
print('%-10s %8s %8s %7s %6s %6s  %s'%('vol','c2 A','c2 B','d c1','d c3','d c4','pages lowered'))
for r in rows: print('%-10s %8d %8d %+7d %+6d %+6d  %d/%d  DCOLv=%d'%r)
print('volumes moved:',len(rows))
print()
for k in K+('printed',):
    print('%-16s %9d -> %9d  %+d'%(k,ta[k],tb[k],tb[k]-ta[k]))
