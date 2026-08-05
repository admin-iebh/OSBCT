# -*- coding: utf-8 -*-
"""The three fragments, in their BLOCK, with the block's ragged/justified verdict."""
import sys, os, json
sys.path.insert(0, os.path.abspath('_xc/hy1'))
import adjudicate as _A, ragged as _R
VOL='35Abhi07'
_A.B='_xc/hy1/blocks3'
BL=json.load(open('_xc/hy1/blocks3/%s.json'%VOL,encoding='utf-8'))
margin=_A.vol_margin(VOL,BL)
edge=_R.vol_measure(VOL,BL,_A.judge_page,margin)
print('vol_margin=%s   vol prose measure (edge)=%s   TOL=%s -> full if xMax>=%.1f'
      % (margin, edge, _R.TOL, edge-_R.TOL))
NEED=('Na cakkhu na cakkhundriyaṁ. . Na indriyā na',
      'Na somanassaṁ na somanassindriyaṁ. . Na indriyā na',
      'Na domanassaṁ na domanassindriyaṁ. . Na indriyā na')
for pg,pd in sorted(BL.items(), key=lambda kv:int(kv[0])):
    for k,sh,b in _R.annotate(_A.judge_page(pd,margin)[2], edge):
        txts=[l[3].rstrip() for l in b]
        hit=[i for i,t in enumerate(txts) if any(t.endswith(n) for n in NEED)]
        if not hit: continue
        body=b[:-1] or b
        full=sum(1 for l in body if l[4]>=edge-_R.TOL)/len(body)
        term=sum(1 for l in body if (l[3] or '').rstrip()[-1:] in _R.TERM)/len(body)
        print()
        print('--- raw pg %s  kind=%s  SHAPE=%s  lines=%d  full=%.2f term=%.2f'
              % (pg,k,sh,len(b),full,term))
        for i,l in enumerate(b):
            mark='  <<< FRAGMENT' if i in hit else ''
            print('   %2d x=%-6.1f xMax=%-6.1f %s | %s%s'
                  % (i,l[1],l[4],'FULL' if l[4]>=edge-_R.TOL else '    ',l[3][:78],mark))
