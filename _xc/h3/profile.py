# -*- coding: utf-8 -*-
import json,sys,collections,re,io
# verse profile, as the 1757a61a measurement defined it:
#   inset 3-7 above the body column, length short of the measure by 10,
#   and a pada comma at the caesura (a comma with text either side).
CAES=re.compile(u'[’”\']?[,;–] ')
for v in sys.argv[1:]:
    A=json.load(open('_xc/h3/rA/%s.rows.json'%v)); B=json.load(open('_xc/h3/rB/%s.rows.json'%v))
    body=A['body_col']; W=A['measure']; Bm=A['body_measure']
    ra,rb=A['rows'],B['rows']
    assert len(ra)==len(rb)
    idx=[i for i in range(len(ra)) if ra[i][3]!='verse' and rb[i][3]=='verse']
    n=len(idx)
    if not n: print(v,'none'); continue
    ins=[rb[i][1]-body for i in idx]
    ln=[rb[i][2]-rb[i][1] for i in idx]
    def prof(i):
        t=rb[i][6].strip()
        m=CAES.search(t[3:-1]) if len(t)>6 else None
        return (3<=rb[i][1]-body<=7) and (rb[i][2] < Bm-10) and bool(m)
    ok=sum(1 for i in idx if prof(i))
    car=sum(1 for i in idx if CAES.search(rb[i][6].strip()[3:-1] or ' '))
    # what the corpus draws them as
    dr=collections.Counter(rb[i][4] for i in idx)
    vd=collections.Counter(rb[i][5] for i in idx)
    print('%-10s newly page-verse %5d  mean inset %.1f  mean len %.1f (Bm %d)  profile %d (%.0f%%)  caesura %d (%.0f%%)'
          %(v,n,sum(ins)/float(n),sum(ln)/float(n),Bm,ok,100.0*ok/n,car,100.0*car/n))
    print('           drawn: %s'%dict(dr))
    print('           verdict: %s'%dict(vd))
