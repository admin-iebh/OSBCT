#!/usr/bin/env python3
"""Invert forward links -> reverse links (commentary/Ṭīkā key -> canon key),
sharded by the target volume and keyed by the target paragraph's ordinal.
Powers the reader's '↩ Canon' from a commentary/subcommentary paragraph."""
import json,glob,os
from collections import defaultdict
rev=defaultdict(dict)   # target_vol -> {target_ordinal: {canon:key, state}}
for lf in glob.glob('site/reader/linksk/*.links.json'):
    cv=os.path.basename(lf).replace('.links.json','')
    links=json.load(open(lf))
    for i,e in links.items():
        canon_key=f'{cv}#{i}'
        for layer in ('commentary','subcommentary'):
            for tgt in (e.get(layer) or []):
                if not tgt or not tgt.get('key'): continue
                tv,tord=tgt['key'].split('#')
                prev=rev[tv].get(tord)
                if prev and prev.get('state')=='direct' and tgt.get('state')!='direct': continue
                rev[tv][tord]={'canon':canon_key,'state':tgt.get('state')}
n=0
for tv,d in rev.items():
    json.dump(d, open(f'site/reader/linksk/{tv}.rev.json','w'), ensure_ascii=False); n+=len(d)
print(f'reverse links: {n:,} target paragraphs across {len(rev)} volumes')
