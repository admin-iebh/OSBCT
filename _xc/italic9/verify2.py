# -*- coding: utf-8 -*-
"""Second pass: body column measured VOLUME-WIDE (modal indent over every
printed body line in the volume), which is robust on short/title pages where
the per-page mode was not.  Full line dump, and the verse/prose rule applied
mechanically: a run of >= 2 consecutive lines at rel > +2 is VERSE; anything
at the body column, and any lone raised line, is prose."""
import json, os, sys, collections
ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import pline, locate

FLAG = [('02Vin02','0',3), ('06VinSg06','0',1), ('14SamA01','0',5),
        ('17AnA01','0',3), ('27Khu10','151',1), ('36Abhi08','0',1),
        ('38Abhi10','0',6), ('41KhuA22','2',4), ('42KhuA23','2',1)]

def bodycol(st):
    return collections.Counter(it[2] for it in st).most_common(1)[0][0]

def classify(lines, bc):
    rel = [it[2]-bc for it in lines]; kind=[]; i=0
    while i < len(lines):
        if rel[i] > 2:
            j=i
            while j+1 < len(lines) and rel[j+1] > 2: j+=1
            n=j-i+1
            kind += ['VERSE' if n>=2 else 'lone^'] * n
            i=j+1
        else:
            kind.append('prose'); i+=1
    return rel, kind

def run(vol, ordk, idx):
    S = json.load(open('%s/site/reader/sections/%s.json' % (ROOT, vol), encoding='utf-8'))
    ent = S[ordk][idx]; text = str(ent.get('l',''))
    st = pline.stream(vol); P = locate.Page(st); bc = bodycol(st)
    H = collections.Counter(it[2] for it in st)
    sp = P.span(text)
    print('==== %s sec%s[%d]  VOLUME body column = %d  (top indents %s)' %
          (vol, ordk, idx, bc, H.most_common(6)))
    if sp is None: print('  NOT FOUND'); return
    l0,l1,a,b = sp; lines = st[l0:l1+1]
    print('  %d printed lines, pdf pages %d-%d' % (len(lines), lines[0][0], lines[-1][0]))
    rel, kind = classify(lines, bc)
    for k,(it,r,kd) in enumerate(zip(lines,rel,kind)):
        print('   %3d p%-4d ind=%3d rel=%+3d %-6s %s' % (k,it[0],it[2],r,kd,it[3][:82]))
    print('  TALLY %s' % dict(collections.Counter(kind)))

for v,o,i in FLAG:
    if len(sys.argv)>1 and v not in sys.argv[1:]: continue
    run(v,o,i); print()
