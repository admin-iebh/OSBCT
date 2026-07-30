#!/usr/bin/env python3
"""Build a compact printed-page -> ordinal index per volume, so apparatus
cross-references (work + printed page) can resolve to a paragraph key."""
import json,glob,os
out={}
for js in sorted(glob.glob('site/*.json')):
    vol=os.path.basename(js).replace('.json','')
    try: d=json.load(open(js))
    except: continue
    if not isinstance(d,dict) or 'paragraphs' not in d: continue
    pg={}
    for i,p in enumerate(d['paragraphs']):
        pr=p.get('printed')
        if pr is not None and str(pr) not in pg: pg[str(pr)]=i   # first paragraph on that printed page
    if pg: out[vol]=pg
json.dump(out, open('site/reader/pageindex.json','w'), ensure_ascii=False)
print('page index:',len(out),'volumes,',sum(len(v) for v in out.values()),'pages,',os.path.getsize('site/reader/pageindex.json')//1024,'KB')
