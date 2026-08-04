# Can the ordinal-keyed bold spans address the text the VERSE branch draws?
# MEASURE ONLY.  For every ordinal that (a) has bold spans and (b) is taken by
# the verse branch in the spine view, ask what the branch actually draws and
# whether the corpus text -- which the spans index -- is any part of it.
import json,os,sys,re
R='site/reader'
VOLS=sorted(x[:-10] for x in os.listdir(R+'/bold') if x.endswith('.bold.json') and '.' not in x[:-10])
NUM=re.compile(r'^\s*\d+(-\d+)?\.\s*')
def flat(x):
    # proseBlocks(): list of str | {gatha:[...]} | {t:..,n:..}
    out=[]
    if x is None: return out
    if not isinstance(x,list): return [str(x)]
    for p in x:
        if isinstance(p,dict):
            if 'gatha' in p: out.append('\n'.join(p['gatha']))
            elif p.get('t') is not None: out.append(str(p['t']))
        else: out.append(str(p))
    return out
tot=dict(ords=0,spans=0)
cls={}
def bump(k,n=1,s=0):
    c=cls.setdefault(k,[0,0]); c[0]+=n; c[1]+=s
per={}
for vol in VOLS:
    try: bold=json.load(open(f'{R}/bold/{vol}.bold.json'))
    except Exception: continue
    if not bold: continue
    try: verse=json.load(open(f'{R}/verse/{vol}.json'))
    except Exception: verse={}
    paras=json.load(open(f'site/{vol}.json'))['paragraphs']
    pv={}
    for ordk,spans in bold.items():
        if not spans: continue
        o=int(ordk)
        if o>=len(paras): bump('NO_PARA',1,len(spans)); continue
        vm=verse.get(ordk)
        if not vm: continue           # plain branch -- fixed by the fmtBold change
        if 'groups' not in vm: continue  # groupless: plain branch + frame
        tot['ords']+=1; tot['spans']+=len(spans)
        text=paras[o].get('text','') or ''
        stripped=NUM.sub('',text); off=len(text)-len(stripped)
        blocks=flat(vm.get('before'))+ [g for grp in vm.get('groups',[]) for g in ['\n'.join(grp)]] + flat(vm.get('after'))
        drawn='\n'.join(blocks)
        # how many spans' text is findable in what is drawn?
        okexact=0; okuniq=0
        for a,b in spans:
            s=text[a:b]
            if not s.strip(): continue
            n=drawn.count(s)
            if n==1: okuniq+=1
            if n>=1: okexact+=1
        # is the corpus text itself a contiguous substring of some drawn block?
        sub=any(stripped and stripped in bl for bl in blocks)
        subs=sum(1 for bl in blocks if bl and bl in stripped)
        k=('EMPTY_GROUPS' if not vm.get('groups') else 'HAS_GROUPS')
        k+= '|textIsBlock' if sub else ('|blocksInText' if subs else '|neither')
        bump(k,1,len(spans))
        d=pv.setdefault(vol,dict(ords=0,spans=0,uniq=0,found=0,textIsBlock=0,blocksInText=0))
        d['ords']+=1; d['spans']+=len(spans); d['uniq']+=okuniq; d['found']+=okexact
        d['textIsBlock']+= 1 if sub else 0
        d['blocksInText']+= 1 if (not sub and subs) else 0
print('ordinals taken by the verse branch WITH bold spans:',tot['ords'],' spans:',tot['spans'])
for k in sorted(cls,key=lambda k:-cls[k][1]): print('  %-34s ords=%6d spans=%7d'%(k,cls[k][0],cls[k][1]))
print()
print('%-12s %6s %8s %8s %8s %8s %8s'%('vol','ords','spans','found','uniq','txtIsBlk','blkInTxt'))
for v in sorted(pv,key=lambda v:-pv[v]['spans'])[:20]:
    d=pv[v]; print('%-12s %6d %8d %8d %8d %8d %8d'%(v,d['ords'],d['spans'],d['found'],d['uniq'],d['textIsBlock'],d['blocksInText']))
tf=sum(d['found'] for d in pv.values()); tu=sum(d['uniq'] for d in pv.values())
print('\nTOTAL spans whose exact letters occur in what the branch draws: %d (%.1f%%), uniquely: %d (%.1f%%)'%(
    tf,100*tf/max(1,tot['spans']),tu,100*tu/max(1,tot['spans'])))
