# -*- coding: utf-8 -*-
import sys, os, json, re, importlib
sys.path.insert(0, os.path.abspath('pipeline'))
VOL='35Abhi07'
os.environ['BLOCKBREAK']='0'
m=importlib.import_module('build_khu_volume_bb'); m.use(VOL)
pages=m.pdf_pages()
print('=== -layout lines ENDING with "Na indriya na" (any diacritic) ===')
n=0
for pi,pg in enumerate(pages,1):
    ls=pg.split('\n')
    for li,ln in enumerate(ls):
        s=ln.rstrip()
        if s.endswith('Na indriyā na') or s.endswith('na indriyā na'):
            n+=1
            if n<=8:
                print('  raw pg %d line %d | %r' % (pi,li,s[-70:]))
                print('              next | %r' % (ls[li+1].rstrip()[:70] if li+1<len(ls) else '<EOP>'))
print('total: %d' % n)

BL=json.load(open('_xc/hy1/blocks3/%s.json'%VOL,encoding='utf-8'))
print()
print('=== blocks3 lines ENDING with the same ===')
n=0
for pg,pd in sorted(BL.items(), key=lambda kv:int(kv[0])):
    for i,l in enumerate(pd['lines']):
        if l[3].rstrip().endswith('indriyā na'):
            n+=1
            if n<=8:
                print('  raw pg %s row %d start=%d xMax=%s | %s' % (pg,i,l[2],l[4],l[3][-60:]))
print('total: %d' % n)
