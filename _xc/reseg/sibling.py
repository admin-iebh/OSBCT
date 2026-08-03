import pdfplumber, collections, json, sys, os, statistics
def census(vol):
    for d in ('pali-unicode','atthakatha-unicode','tika-unicode'):
        p='%s/%s.pdf'%(d,vol)
        if os.path.exists(p): break
    ps=json.load(open('site/%s.json'%vol,encoding='utf-8'))['paragraphs']
    LO=min(x['pdf_page'] for x in ps); HI=max(x['pdf_page'] for x in ps)
    pdf=pdfplumber.open(p); lead=collections.Counter(); x0c=collections.Counter()
    for pno in range(LO,min(HI,len(pdf.pages))+1):
        rows=collections.defaultdict(list)
        for ch in pdf.pages[pno-1].chars: rows[round(ch['top'],0)].append(ch)
        lines=[]
        for t in sorted(rows):
            cs=sorted(rows[t],key=lambda c:c['x0'])
            tx=''.join(c['text'] for c in cs)
            if tx.strip(): lines.append((round(cs[0]['x0'],1),tx))
        if not lines: continue
        cut=next((k for k,(x,t) in enumerate(lines) if t.strip().startswith('_________')),len(lines))
        for x,t in lines[1:cut]:
            x0c[x]+=1
    body=x0c.most_common(1)[0][0]
    for pno in range(LO,min(HI,len(pdf.pages))+1):
        rows=collections.defaultdict(list)
        for ch in pdf.pages[pno-1].chars: rows[round(ch['top'],0)].append(ch)
        lines=[]
        for t in sorted(rows):
            cs=sorted(rows[t],key=lambda c:c['x0'])
            tx=''.join(c['text'] for c in cs)
            if tx.strip(): lines.append((round(cs[0]['x0'],1),tx))
        if not lines: continue
        cut=next((k for k,(x,t) in enumerate(lines) if t.strip().startswith('_________')),len(lines))
        for x,t in lines[1:cut]:
            if abs(x-body)<=0.5: lead[len(t)-len(t.lstrip())]+=1
    pdf.close()
    L=[len(x['text']) for x in ps]
    print('%-10s shipped %5d ¶ (median %5d)  body col x0=%.1f  pages %d-%d'
          %(vol,len(ps),statistics.median(L),body,LO,HI))
    print('            leading-space census: %s'%dict(sorted(lead.items())))
    o=lead.get(1,0)
    print('            ONE-SPACE OPENERS: %d  -> ~%d ¶, median ~%d chars'
          %(o,o,sum(L)//max(o,1)))
for v in sys.argv[1:]: census(v)
