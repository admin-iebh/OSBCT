# Predict EXACTLY what the proposed rule draws, span by span, over all 118 volumes.
# The rule: a string the spine view draws from the printed stream is located in the
# number-stripped corpus paragraph text by a FORWARD-ONLY cursor indexOf; spans
# falling inside it are drawn there.  Not found -> drawn exactly as today.
import json,os,re,sys,collections
R='site/reader'
NUM=re.compile(r'^\s*\d+(-\d+)?\.\s*')
VOLS=sorted(x[:-10] for x in os.listdir(R+'/bold') if x.endswith('.bold.json') and x.count('.')==2)
out={}
G=collections.Counter()
for vol in VOLS:
    try: bold=json.load(open(f'{R}/bold/{vol}.bold.json'))
    except Exception: bold={}
    try: verse=json.load(open(f'{R}/verse/{vol}.json'))
    except Exception: verse={}
    try: inc=json.load(open(f'{R}/incipit/{vol}.json'))
    except Exception: inc={}
    paras=json.load(open(f'site/{vol}.json'))['paragraphs']
    d=collections.Counter()
    for ordk,spans in bold.items():
        o=int(ordk)
        if o>=len(paras): continue
        spans=[s for s in spans if s and s[1]>s[0]]
        if not spans: continue
        text=paras[o].get('text','') or ''
        stripped=NUM.sub('',text); off=len(text)-len(stripped)
        sp=sorted([[max(0,a-off),min(len(stripped),b-off)] for a,b in spans if b-off>0 and a-off<len(stripped)])
        d['spans_total']+=len(spans); d['spans_in_stripped']+=len(sp)
        vm=verse.get(ordk)
        if not vm or 'groups' not in vm:
            # PLAIN branch (with or without a groupless frame).  Today: fmtText.
            # Proposed: fmtBold on the corpus text -> every span drawn.
            d['plain_ords']+=1; d['plain_drawn']+=len(sp); G['plain']+=len(sp)
            continue
        # VERSE branch: build the drawn string list in order
        blocks=[]
        def push(x):
            if x is None: return
            if not isinstance(x,list): blocks.append(str(x)); return
            for p in x:
                if isinstance(p,dict):
                    if 'gatha' in p: blocks.extend(str(l) for l in p['gatha'])
                    elif p.get('t') is not None: blocks.append(str(p['t']))
                else: blocks.append(str(p))
        push(vm.get('before'))
        for g in vm.get('groups',[]): blocks.extend(str(l) for l in g)
        push(vm.get('after'))
        cur=0; covered=[]
        for b in blocks:
            b2=NUM.sub('',b)
            if not b2: continue
            i=stripped.find(b2,cur)
            if i<0: i=stripped.find(b2)          # one retry from the start
            if i<0: continue
            cur=i+len(b2); covered.append((i,cur))
        drawn=0
        for a,b in sp:
            if any(a>=x and b<=y for x,y in covered): drawn+=1
        d['verse_ords']+=1; d['verse_spans']+=len(sp); d['verse_drawn']+=drawn
        G['verse_spans']+=len(sp); G['verse_drawn']+=drawn
    out[vol]=dict(d)
json.dump(out,open('_xc/boldspine/predict.json','w'))
tot=collections.Counter()
for v,d in out.items(): tot.update(d)
print('spans in bold maps                :',tot['spans_total'])
print('spans inside the stripped text    :',tot['spans_in_stripped'])
print('PLAIN-branch ordinals             :',tot['plain_ords'],' spans drawn by the fix:',tot['plain_drawn'])
print('VERSE-branch ordinals             :',tot['verse_ords'],' spans:',tot['verse_spans'])
print('   of which drawable by the rule  :',tot['verse_drawn'],' (%.1f%%)'%(100*tot['verse_drawn']/max(1,tot['verse_spans'])))
print('   NOT drawable                   :',tot['verse_spans']-tot['verse_drawn'])
print('TOTAL spans the spine would draw  :',tot['plain_drawn']+tot['verse_drawn'],
      'of',tot['spans_in_stripped'],'(%.1f%%)'%(100*(tot['plain_drawn']+tot['verse_drawn'])/max(1,tot['spans_in_stripped'])))
print()
print('worst residue (verse spans not drawable):')
for v in sorted(out,key=lambda v:-(out[v].get('verse_spans',0)-out[v].get('verse_drawn',0)))[:12]:
    d=out[v]; print('  %-12s %6d of %6d'%(v,d.get('verse_spans',0)-d.get('verse_drawn',0),d.get('verse_spans',0)))
