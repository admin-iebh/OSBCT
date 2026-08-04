# -*- coding: utf-8 -*-
"""Where in the corpus does each class-2 line live, and did the verse machinery
   see that ordinal at all?"""
import sys, os, json, collections
sys.path.insert(0,'pipeline')
import check_page_fidelity as F
def run(vol, dumpdir):
    r=json.load(open('%s/%s.rows.json'%(dumpdir,vol)))
    rows=r['rows']
    c=json.load(open('site/%s.json'%vol))
    ps=c['paragraphs']
    vm=json.load(open('site/reader/verse/%s.json'%vol)) if os.path.exists('site/reader/verse/%s.json'%vol) else {}
    sc=json.load(open('site/reader/sections/%s.json'%vol)) if os.path.exists('site/reader/sections/%s.json'%vol) else {}
    # letter string per paragraph, in order
    buf=[];spans=[]
    for i,p in enumerate(ps):
        s=F.letters(p.get('text',''))
        spans.append((len(''.join(buf)), len(''.join(buf))+len(s), i)); buf.append(s)
    C=''.join(buf)
    import bisect
    starts=[a for a,_,_ in spans]
    out=collections.Counter(); byord=collections.Counter()
    cur=0
    for x in rows:
        if x[5]!='VERSE_AS_PROSE': continue
        t=F.letters(x[6])
        j=C.find(t,max(0,cur-4000))
        if j<0: j=C.find(t)
        if j<0: out['not_in_paragraphs']+=1; continue
        cur=j+len(t)
        k=max(0,bisect.bisect_right(starts,j)-1)
        o=spans[k][2]
        byord[o]+=1
        has_v = str(o) in vm
        has_g = has_v and bool(vm[str(o)].get('groups'))
        has_s = str(o) in sc
        out[('verse_entry' if has_v else 'no_verse_entry')+('+groups' if has_g else '')+('+sect' if has_s else '')]+=1
    print('==',vol,'class-2 lines by corpus provenance')
    for k,v in out.most_common(): print('   %-30s %5d'%(k,v))
    print('   paragraphs touched: %d ; worst: %s'%(len(byord), byord.most_common(6)))
    return byord, ps, vm
for v in sys.argv[1:]:
    run(v,'_xc/c2b/d2')
