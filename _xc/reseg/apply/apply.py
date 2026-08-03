# -*- coding: utf-8 -*-
"""Apply the re-segmentation of 20KhuA01 into site/.  Idempotent: reads the
prepared files in _xc/reseg/ and the .prereseg backups, never its own output."""
import json, os, sys, collections
R='/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/'
VOL='20KhuA01'
W='--write' in sys.argv
def J(p): return json.load(open(R+p,encoding='utf-8'))
def put(p,d,**kw):
    if W:
        json.dump(d,open(R+p,'w',encoding='utf-8'),ensure_ascii=False,**kw)
    print('  %-52s %s' % (p, ('wrote' if W else 'would write')+' %d keys'%(len(d) if hasattr(d,'__len__') else 0)))

remap={int(k):v for k,v in J('_xc/reseg/ord_remap_%s.json'%VOL).items()}

# ---- 1. corpus -------------------------------------------------------------
res=J('_xc/reseg/%s.json'%VOL)
ids=J('_xc/reseg/b1/ids_%s.json'%VOL)['ids']
assert len(ids)==len(res['paragraphs'])==673
for i,p in enumerate(res['paragraphs']):
    p['id']=ids[i]
    assert p['key']=='%s#%d'%(VOL,i)
assert len(set(p['id'] for p in res['paragraphs']))==673
print('corpus: 673 paragraphs, 673 distinct ids')
put('site/%s.json'%VOL,res['paragraphs'])   # len print only
if W: json.dump(res,open(R+'site/%s.json'%VOL,'w',encoding='utf-8'),ensure_ascii=False)

# ---- 2. side maps ----------------------------------------------------------
for src,dst in [
  ('_xc/reseg/bold/%s.bold.json'%VOL,      'site/reader/bold/%s.bold.json'%VOL),
  ('_xc/reseg/b2/verse_%s.json'%VOL,       'site/reader/verse/%s.json'%VOL),
  ('_xc/reseg/b2/final_uddana_%s.json'%VOL,'site/reader/uddana/%s.json'%VOL),
  ('_xc/reseg/b2/final_hide_%s.json'%VOL,  'site/reader/hide/%s.json'%VOL),
  ('_xc/reseg/b2/final_sections_%s.json'%VOL,'site/reader/sections/%s.json'%VOL),
  ('_xc/reseg/b3/incipit_%s.json'%VOL,     'site/reader/incipit/%s.json'%VOL),
  ('_xc/reseg/b3/booktitle_%s.json'%VOL,   'site/reader/booktitle/%s.json'%VOL),
  ('_xc/reseg/b3/ord_%s.json'%VOL,         'site/reader/ord/%s.json'%VOL)]:
    put(dst,J(src))

# ---- 3. inbound targets in seven OTHER volumes -----------------------------
tot=0
for v in ('18Khu01','19Khu02','22Khu05','23Khu06','25Khu08','26Khu09','27Khu10'):
    p='site/reader/linksk/%s.links.json'%v
    L=json.load(open(R+p+'.prereseg',encoding='utf-8'))
    n=0
    for ordk,e in L.items():
        for slot in ('commentary','subcommentary'):
            for t in (e.get(slot) or []):
                k=t.get('key') or ''
                if k.startswith(VOL+'#'):
                    o=int(k.split('#')[1]); t['key']='%s#%d'%(VOL,remap[o]); n+=1
    tot+=n
    if W: json.dump(L,open(R+p,'w',encoding='utf-8'),ensure_ascii=False)
    print('  %-52s %d targets remapped' % (p,n))
print('inbound targets remapped: %d' % tot)

# ---- 4. legacy links/<VOL>.rev.json (read by nothing; kept consistent) -----
lr=json.load(open(R+'site/reader/links/%s.rev.json'%VOL+'.prereseg',encoding='utf-8'))
put('site/reader/links/%s.rev.json'%VOL, {str(remap[int(k)]):v for k,v in lr.items()})
