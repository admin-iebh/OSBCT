import pdfplumber, collections, json
pdf = pdfplumber.open('atthakatha-unicode/20KhuA01.pdf')
import sys
LO,HI=int(sys.argv[1]),int(sys.argv[2])
lead=collections.Counter(); rows_out=[]
for pno in range(LO,HI+1):
    pg=pdf.pages[pno-1]
    rows=collections.defaultdict(list)
    for ch in pg.chars: rows[round(ch['top'],0)].append(ch)
    ordered=sorted(rows)
    lines=[]
    for top in ordered:
        cs=sorted(rows[top],key=lambda c:c['x0'])
        x0=round(cs[0]['x0'],1)
        t=''.join(c['text'] for c in cs)
        if not t.strip(): continue
        lines.append((x0,t))
    # drop the running head (first line) and everything from the footnote rule down
    cut=next((i for i,(x,t) in enumerate(lines) if t.strip().startswith('___'*3)),len(lines))
    for x0,t in lines[1:cut]:
        if abs(x0-62.6)>0.5: continue          # centred heads / superscripts
        n=len(t)-len(t.lstrip())
        lead[n]+=1
        rows_out.append((pno,n,t.strip()))
json.dump(rows_out,open(''+'_xc/reseg/plumb_lines_%d.json'%LO+'','w'),ensure_ascii=False)
tot=sum(lead.values())
print('body lines at the body column x0=62.6, pdf pages %d-%d: %d'%(LO,HI,tot))
for k in sorted(lead): print('   leading spaces %2d : %6d  %5.2f%%'%(k,lead[k],100*lead[k]/tot))
pdf.close()
