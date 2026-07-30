#!/usr/bin/env python3
"""Build the reader navigation tree: three colour-coded layers, each
nikāya/piṭaka -> book -> section. Combined physical volumes are split into
their constituent books using the layer suffix (-pāḷi / -aṭṭhakathā / -ṭīkā),
which distinguishes real book names from piṭaka labels and sub-divisions."""
import json,os,re
from collections import defaultdict

# !!! THIS FILE IS A SCRIPT, NOT A MODULE — ITS WHOLE BODY IS MODULE-LEVEL AND
# IT REWRITES site/reader/nav.json FROM SCRATCH THE MOMENT IT IS IMPORTED.
# That has now destroyed a gated nav.json TWICE, both times from a read-only
# probe that imported the nav builders to read their SPECs:
# `nav.json.damaged_by_29probe` (2026-07-29) and
# `nav.json.damaged_by_cminsweep` (2026-07-30) — 2.1 MB and 28,612 tree rows
# replaced by 0.5 MB and none, silently, with a cheerful "wrote nav.json".
# There is no main() to guard, so the IMPORT itself is refused.  A probe that
# needs this file's SPEC must parse it (ast), not import it.
if __name__ != '__main__':
    raise ImportError(
        'build_nav.py is a SCRIPT: importing it rewrites site/reader/nav.json '
        'and drops every gated tree. Run it (python3 pipeline/build_nav.py), '
        'or parse it with ast — do not import it.')
NIKORDER=['Vinayapiṭaka','Dīghanikāya','Majjhimanikāya','Saṁyuttanikāya',
          'Aṅguttaranikāya','Khuddakanikāya','Abhidhammapiṭaka','Visuddhimagga','Other']

def nikaya_of(vol):
    c=re.sub(r'^\d+','',vol)
    if c.startswith(('Vsm','Vism')): return 'Visuddhimagga'
    if c.startswith(('Vin','ViT','Kankha')): return 'Vinayapiṭaka'
    if c.startswith('Di'): return 'Dīghanikāya'
    if c.startswith('Ma'): return 'Majjhimanikāya'
    if c.startswith(('Sam','SaT')): return 'Saṁyuttanikāya'
    if c.startswith('An'): return 'Aṅguttaranikāya'
    if c.startswith('Khu'): return 'Khuddakanikāya'
    if c.startswith('Abhi'): return 'Abhidhammapiṭaka'
    return 'Other'

def _fold(x):
    x=(x or '').lower(); return ''.join({'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'}.get(c,c) for c in x)

def clean_label(s):
    s=re.sub(r'\s+',' ',(s or '').strip())
    s=re.sub(r'^\((?:\d+|[ivxlcdmIVXLCDM]+)\)\s*','',s)
    s2=re.sub(r'^.*\d+\.\s+','',s)
    return (s2 or s).strip().rstrip('.')

PITAKA={'Vinayapiṭaka','Suttapiṭaka','Abhidhammapiṭaka'}
def is_book(layer,b):
    """True if b is a real book title for this layer (ends in the layer suffix,
    is not a piṭaka label or a running-head phrase)."""
    if not b or b=='X' or b in PITAKA: return False
    if b.startswith('Iti ') or b.rstrip().endswith('.'): return False
    f=_fold(b)
    if layer=='canon': return f.endswith('pali')
    if layer=='commentary': return f.endswith('tthakatha') or f.endswith('atthakatha')
    return f.endswith('tika')

def book_nodes(layer,paras):
    starts=[]; last=None
    for i,p in enumerate(paras):
        b=p.get('book')
        if is_book(layer,b) and b!=last: starts.append((i,b)); last=b
    nodes=[]
    for idx,(si,bt) in enumerate(starts):
        ei=starts[idx+1][0] if idx+1<len(starts) else len(paras)
        nodes.append({'start':si,'end':ei,'book':bt})
    return nodes

def sections(paras,s,e):
    out=[]; seen=set()
    for p in paras[s:e]:
        sv=None
        for f in ('sutta','vagga'):
            v=p.get(f)
            if v and v!='X': sv=v; break
        if not sv: continue
        lab=clean_label(re.sub(r'\s*\(\d+\)\s*$','',sv))
        nk=re.sub(r'[^a-z]','',_fold(lab))
        if not nk or nk in seen: continue
        seen.add(nk); out.append({'label':str(len(out)+1)+'. '+lab,'key':p['key']})
    return out

_SUF={'canon':('pali',),'commentary':('tthakatha','atthakatha'),'subcommentary':('tika',)}
def volume_title(layer,paras,work,code):
    sufs=_SUF.get(layer,())
    def ok(v):
        f=_fold(v); return v and v!='X' and any(f.endswith(s) for s in sufs)
    for field in ('vagga','book'):
        for p in paras:
            if ok(p.get(field)): return p.get(field)
    w=(work or '').split('—')[-1].strip() or (work or '').split(':')[-1].strip()
    return re.sub(r'\s*\(.*?\)','',w).strip() or code

man=json.load(open('site/reader/manifest.json'))['volumes']
LAYORDER={'canon':0,'commentary':1,'subcommentary':2}
LAYNAME={'canon':'Pāḷi','commentary':'Aṭṭhakathā','subcommentary':'Ṭīkā'}
tree={l:{} for l in LAYORDER}
def vol_order_key(v):
    m=re.match(r'^(\d+)',v); return (int(m.group(1)) if m else 999, v)

audit=[]
for code,meta in man.items():
    layer=meta['layer']
    if layer not in tree: continue
    paras=json.load(open(f'site/{code}.json'))['paragraphs']
    if not paras: continue
    title=volume_title(layer,paras,meta.get('work'),code)
    bns=book_nodes(layer,paras)
    nk=nikaya_of(code)
    if len(bns)<=1:
        secs=sections(paras,0,len(paras)) or [{'label':title,'key':paras[0]['key']}]
        tree[layer].setdefault(nk,[]).append({'vol':code,'work':meta.get('work',code),'title':title,'first':paras[0]['key'],'suttas':secs})
        if not bns: audit.append((code,layer,'no book marker -> single node ('+title+')'))
    else:
        for bn in bns:
            secs=sections(paras,bn['start'],bn['end'])
            tree[layer].setdefault(nk,[]).append({'vol':code,'work':meta.get('work',code),'title':clean_label(bn['book']),'first':paras[bn['start']]['key'],'suttas':secs})
        audit.append((code,layer,'%d books: %s' % (len(bns),' / '.join(clean_label(b['book']) for b in bns))))

# number book-nodes that share a title within a nikāya (Visuddhimagga I/II, Dhammapadaṭṭhakathā I/II…)
ROMAN=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI']
for layer in tree:
    for nk in tree[layer]:
        bt=defaultdict(list)
        for v in tree[layer][nk]: bt[v['title']].append(v)
        for t,vs in bt.items():
            if len(vs)>1:
                for i,v in enumerate(vs):  # already in nikāya/volume order
                    v['title']=t+' '+(ROMAN[i] if i<len(ROMAN) else str(i+1))

out={'layers':[]}
for layer in sorted(tree,key=lambda l:LAYORDER[l]):
    niks=[]
    for nk in NIKORDER:
        if nk not in tree[layer]: continue
        niks.append({'nikaya':nk,'volumes':tree[layer][nk]})
    out['layers'].append({'layer':layer,'label':LAYNAME[layer],'nikayas':niks})
json.dump(out, open('site/reader/nav.json','w'), ensure_ascii=False)
json.dump(audit, open('site/reader/_nav_audit.json','w'), ensure_ascii=False, indent=1)
for L in out['layers']:
    nv=sum(len(n['volumes']) for n in L['nikayas']); ns=sum(len(v['suttas']) for n in L['nikayas'] for v in n['volumes'])
    print(f"{L['label']:12s}: {nv} book-nodes, {ns} sections")
print('wrote nav.json', os.path.getsize('site/reader/nav.json')//1024,'KB; audit ->',len(audit),'volumes')
