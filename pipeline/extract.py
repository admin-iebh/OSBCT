"""OSBCT structural extractor v2 — hierarchy-aware.
Emits paragraphs addressed as (division, sutta, n) rather than bare numbers."""
import re,json,subprocess,os

RULE   = re.compile(r'^\s*_{30,}\s*$')          # footnote rule (~62); decorative rules are 4-6
PARA   = re.compile(r'^\s*(\d{1,4})\.\s+(?=\S)')
NUMTIT = re.compile(r'^(\d{1,4})\.\s+(.*)$')
BOOKWORD = re.compile(r'(nipāta|saṁyutta|khandhaka|paṇṇāsaka|pāḷi|piṭaka|aṭṭhakathā|ṭīkā)', re.I)
VAGGAWORD= re.compile(r'(vagga|vaggo)', re.I)
DIVWORD  = re.compile(r'(vagga|vaggo|nipāta|saṁyutta|khandhaka|paṇṇāsaka|pāḷi|piṭaka|aṭṭhakathā|ṭīkā)', re.I)
SUTWORD = re.compile(r'(sutta|suttaṁ)', re.I)
ENDWORD = re.compile(r'(niṭṭhit|samatt)', re.I)
XREF_TAIL = re.compile(r'piṭṭh(?:e|esu|epi|esupi|ādīsu)', re.I)
XREF_SEG  = re.compile(r'\b([A-ZĀĪŪṀ][a-zāīūṁṅñṭḍṇḷ]{0,6}(?:-Ṭṭha|-Ṭī)?)\.?\s*(?:(\d+)\s*\.\s*)?((?:\d+(?:-\d+)?)(?:\s*,\s*\d+(?:-\d+)?)*)')

def parse_xrefs(txt):
    """Handles: 'Aṁ 1. 60 piṭṭhe', 'Khu 10. 144-5 piṭṭhesupi.',
    'Khu 2. 224, 334.', 'Dī 2. 42; Upari 127; Khu 10. 37 piṭṭhesupi.'"""
    out=[]
    if not (XREF_TAIL.search(txt) or re.search(r'\b[A-ZĀĪŪṀ][a-zāīūṁ]{0,6}\.?\s*\d+\s*\.\s*\d',txt)):
        return out
    also=bool(re.search(r'pi\b|pi\.',txt))
    for seg in re.split(r'[;]',txt):
        m=XREF_SEG.search(seg)
        if not m: continue
        work=m.group(1); vol=int(m.group(2)) if m.group(2) else None
        for chunk in m.group(3).split(','):
            chunk=chunk.strip()
            if '-' in chunk:
                a,b=chunk.split('-',1)
                a=int(a); b=int(b)
                if b<a: b=int(str(a)[:len(str(a))-len(str(b))]+str(b))   # 144-5 -> 144-145
                out.append({'work':work,'vol':vol,'page':a,'page_to':b,'also':also})
            elif chunk.isdigit():
                out.append({'work':work,'vol':vol,'page':int(chunk),'also':also})
    return out

def raw_pages(pdf):
    t=subprocess.run(['pdftotext','-enc','UTF-8','-layout',pdf,'-'],
                     capture_output=True).stdout.decode('utf-8','replace')
    return t.split('\x0c')

def parse_header(line):
    s=line.strip()
    if not s: return None,None
    m=re.match(r'^(\d{1,4})\s+(\S.*)$',s)
    if m: return int(m.group(1)),m.group(2).strip()
    m=re.match(r'^(.*\S)\s+(\d{1,4})$',s)
    if m: return int(m.group(2)),m.group(1).strip()
    m=re.match(r'^(.*\S)\s+([ivxlcdm]{1,7})$',s)
    if m: return ('roman',m.group(2)),m.group(1).strip()
    m=re.match(r'^([ivxlcdm]{1,7})\s+(\S.*)$',s)
    if m: return ('roman',m.group(1)),m.group(2).strip()
    return None,s

def split_page(pg):
    lines=pg.split('\n')
    hi=next((i for i,l in enumerate(lines) if l.strip()),None)
    if hi is None: return None
    pno,title=parse_header(lines[hi])
    ridx=[i for i,l in enumerate(lines) if RULE.match(l)]
    ri=ridx[-1] if ridx else None
    return dict(printed=pno,head=title,
                body=lines[hi+1:ri] if ri is not None else lines[hi+1:],
                app=lines[ri+1:] if ri is not None else [],
                has_rule=ri is not None)

def classify_heading(st,indent):
    if not st or indent<12 or len(st)>70 or ',' in st: return None
    if st.startswith(('“','‘','"')): return None
    core=re.sub(r'^\d{1,4}\.\s*','',st)
    if not (DIVWORD.search(st) or SUTWORD.search(st) or len(core.split())<=2): return None
    if ENDWORD.search(st):  return 'end'
    if SUTWORD.search(st):  return 'sutta'
    if VAGGAWORD.search(st):return 'vagga'      # narrower level (recto head)
    if BOOKWORD.search(st): return 'book'       # broader level (verso head)
    return 'section'

def parse_apparatus(app_lines):
    toks=[]
    for l in app_lines:
        if not l.strip(): continue
        toks+= [p for p in re.split(r'\s{2,}',l.strip()) if p]
    notes=[];cur=None
    for tk in toks:
        m=re.match(r'^(\d{1,3})\.\s*(.*)$',tk); s=re.match(r'^([*†])\s*(.*)$',tk)
        if m:
            if cur: notes.append(cur)
            cur={'n':int(m.group(1)),'text':m.group(2)}
        elif s:
            if cur: notes.append(cur)
            cur={'n':None,'mark':s.group(1),'text':s.group(2)}
        elif cur is not None: cur['text']+=' '+tk
    if cur: notes.append(cur)
    out=[]
    for nt in notes:
        txt=nt['text'].strip(); rec=dict(nt,text=txt,variants=[],xrefs=[])
        rec['xrefs']=parse_xrefs(txt)
        stripped=XREF_SEG.sub('',txt)
        for m in re.finditer(r'([^,;()]+?)\s*\(([^)]*)\)',stripped):
            reading=m.group(1).strip(' .'); sig=[x.strip() for x in re.split(r'[,;]',m.group(2)) if x.strip()]
            if reading and sig: rec['variants'].append({'reading':reading,'sigla':sig})
        out.append(rec)
    return out

def slug(s):
    return re.sub(r'[^A-Za-zĀāĪīŪūṀṁṄṅÑñṬṭḌḍṆṇḶḷ0-9]+','',s)[:40]

def extract(pdf):
    pgs=[p for p in (split_page(x) for x in raw_pages(pdf)) if p]
    for i,p in enumerate(pgs,1): p['pdf_page']=i; p['notes']=parse_apparatus(p['app'])
    # front matter / page interpolation
    # body starts at the invocation, which every volume opens with; fall back to page numbering
    first=next((i for i,p in enumerate(pgs)
                if any('Namo tassa Bhagavato' in l for l in p['body'])),None)
    if first is None:
        first=next((i for i,p in enumerate(pgs) if isinstance(p['printed'],int) and p['printed']<=3),0)
    for i,p in enumerate(pgs): p['front_matter']= i<first
    body=[p for p in pgs if not p['front_matter']]
    for i,p in enumerate(body):
        if isinstance(p['printed'],int): continue
        nxt=next((j for j in range(i+1,len(body)) if isinstance(body[j]['printed'],int)),None)
        prv=next((j for j in range(i-1,-1,-1) if isinstance(body[j]['printed'],int)),None)
        if nxt is not None: p['printed']=body[nxt]['printed']-(nxt-i); p['printed_inferred']=True
        elif prv is not None: p['printed']=body[prv]['printed']+(i-prv); p['printed_inferred']=True
    # single ordered pass: maintain division / sutta context
    book=None; vagga=None; sutta=None; paras=[]; heads=[]; cur=None
    def flush():
        nonlocal cur
        if cur: paras.append(cur); cur=None
    for p in body:
        # running heads alternate: division on verso, sutta on recto (§5)
        ht=p['head'] or ''
        hk=classify_heading(ht,99)
        if hk in ('sutta','vagga','book'):
            mh=NUMTIT.match(ht.strip())
            num=int(mh.group(1)) if mh else None
            title=(mh.group(2) if mh else ht).strip()
            if hk=='book':
                if not book or book['title']!=title: book={'n':num,'title':title}
            elif hk=='vagga':
                if not vagga or vagga['title']!=title: vagga={'n':num,'title':title}
            elif hk=='sutta':
                if not sutta or sutta['title']!=title: flush(); sutta={'n':num,'title':title}
        for ln in p['body']:
            st=ln.strip()
            if not st: continue
            kind=classify_heading(st,len(ln)-len(ln.lstrip()))
            if kind:
                mh=NUMTIT.match(st)
                num=int(mh.group(1)) if mh else None
                title=mh.group(2) if mh else st
                heads.append({'kind':kind,'n':num,'title':title,
                              'printed':p['printed'],'pdf_page':p['pdf_page']})
                if kind=='book':     flush(); book={'n':num,'title':title}; vagga=None; sutta=None
                elif kind=='vagga':  flush(); vagga={'n':num,'title':title}; sutta=None
                elif kind=='sutta':  flush(); sutta={'n':num,'title':title}
                elif kind=='end':    flush()
                continue
            m=PARA.match(ln)
            if m:
                flush()
                n=int(m.group(1))
                cur={'n':n,
                     'book':book['title'] if book else None,
                     'vagga':vagga['title'] if vagga else None,
                     'sutta':sutta['title'] if sutta else None,
                     'sutta_n':sutta['n'] if sutta else None,
                     'printed':p['printed'],'pdf_page':p['pdf_page'],'text':st,
                     'id':'/'.join([slug(book['title']) if book else 'X',
                                    slug(vagga['title']) if vagga else 'X',
                                    slug(sutta['title']) if sutta else 'X', str(n)])}
            elif cur is not None: cur['text']+=' '+st
    flush()
    return pgs,paras,heads
