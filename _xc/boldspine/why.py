import json,os,re,collections
R='site/reader';NUM=re.compile(r'^\s*\d+(-\d+)?\.\s*')
W=collections.Counter(); EX=[]
for vol in ['13MaT01','25VsmT01','17SaT02','09DiT02','19AnA03','20KhuA01']:
    bold=json.load(open(f'{R}/bold/{vol}.bold.json'))
    try: verse=json.load(open(f'{R}/verse/{vol}.json'))
    except Exception: verse={}
    paras=json.load(open(f'site/{vol}.json'))['paragraphs']
    for ordk,spans in bold.items():
        o=int(ordk); vm=verse.get(ordk)
        if o>=len(paras) or not vm or 'groups' not in vm: continue
        text=paras[o].get('text','') or ''; stripped=NUM.sub('',text); off=len(text)-len(stripped)
        sp=sorted([[max(0,a-off),min(len(stripped),b-off)] for a,b in spans if b-off>0 and a-off<len(stripped)])
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
        cur=0; cov=[]; miss=0
        for b in blocks:
            b2=NUM.sub('',b)
            if not b2: continue
            i=stripped.find(b2,cur)
            if i<0: i=stripped.find(b2)
            if i<0: miss+=1; continue
            cur=i+len(b2); cov.append((i,cur))
        for a,b in sp:
            if any(a>=x and b<=y for x,y in cov): W['drawn']+=1; continue
            if any(b>x and a<y for x,y in cov): W['STRADDLES_two_blocks']+=1
            elif miss: W['block_not_located']+=1
            else: W['outside_every_block']+=1
            if len(EX)<6: EX.append((vol,ordk,repr(stripped[a:b])[:60],'miss=%d ncov=%d'%(miss,len(cov))))
for k,v in W.most_common(): print('%-24s %7d'%(k,v))
for e in EX: print(e)
