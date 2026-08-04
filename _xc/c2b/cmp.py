import json, os, sys
import os as _o
A=_o.environ.get('CA','_xc/c2b/cen0'); Bd=_o.environ.get('CB','_xc/c2b/cen3')
keys=['PROSE_AS_VERSE','VERSE_AS_PROSE','PROSE_AS_UDDANA','VERSE_AS_HEADING','lone_display',
      'page_verse','page_prose','verse_ok','prose_ok','digit_only']
tot={}, {}
ta={k:0 for k in keys}; tb={k:0 for k in keys}
miss_a=miss_b=0; pl_a=pl_b=0
rows=[]
for f in sorted(os.listdir(A)):
    v=f[:-5]
    a=json.load(open(os.path.join(A,f)))
    b=json.load(open(os.path.join(Bd,f)))
    sa,sb=a['stats'],b['stats']
    for k in keys: ta[k]+=sa.get(k,0); tb[k]+=sb.get(k,0)
    miss_a+=sa.get('absent',0); miss_b+=sb.get('absent',0)
    pl_a+=a['printed_lines']; pl_b+=b['printed_lines']
    d2=sb.get('VERSE_AS_PROSE',0)-sa.get('VERSE_AS_PROSE',0)
    d1=sb.get('PROSE_AS_VERSE',0)-sa.get('PROSE_AS_VERSE',0)
    d3=sb.get('PROSE_AS_UDDANA',0)-sa.get('PROSE_AS_UDDANA',0)
    d4=sb.get('VERSE_AS_HEADING',0)-sa.get('VERSE_AS_HEADING',0)
    if d1 or d2 or d3 or d4:
        rows.append((d2,v,sa.get('VERSE_AS_PROSE',0),sb.get('VERSE_AS_PROSE',0),d1,d3,d4))
print('%-10s %8s %8s   %8s %8s %8s'%('vol','c2 old','c2 new','d c1','d c3','d c4'))
for r in sorted(rows):
    print('%-10s %8d %8d   %+8d %+8d %+8d'%(r[1],r[2],r[3],r[4],r[5],r[6]))
print()
print('%-18s %10s %10s %10s'%('class','old','new','delta'))
for k in keys:
    print('%-18s %10d %10d %+10d'%(k,ta[k],tb[k],tb[k]-ta[k]))
print('%-18s %10d %10d %+10d'%('printed_lines',pl_a,pl_b,pl_b-pl_a))
print('%-18s %10d %10d %+10d'%('absent(miss)',miss_a,miss_b,miss_b-miss_a))
