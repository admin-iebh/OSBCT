#!/usr/bin/env python3
"""OSBCT Phase 1a — render-mode bold extraction.
For each volume: read the injected PDF, capture text render mode per glyph
(mode 2 = the faux-bold stroke that marks lemmata / titles), build a BODY
character signature (drop apparatus <size 11 and the running-head line), then
positionally align each corpus paragraph's letters to the signature and record
bold as character-offset spans. Sentence-level fallback recovers paragraphs the
whole-paragraph match misses. Output: site/reader/bold/<VOL>.bold.json.
"""
import sys, os, json, unicodedata, time
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTChar

NFC=lambda s: unicodedata.normalize('NFC', s or '')
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER={'canon':'pali-unicode','commentary':'atthakatha-unicode','subcommentary':'tika-unicode'}
OUT=os.path.join(ROOT,'site','reader','bold')

class RM(PDFPageAggregator):
    def __init__(self,*a,**k): super().__init__(*a,**k); self._r=0
    def render_string(self,ts,*a,**k): self._r=getattr(ts,'render',0); return super().render_string(ts,*a,**k)
    def render_char(self,*a,**k):
        adv=super().render_char(*a,**k); o=self.cur_item._objs
        if o and isinstance(o[-1],LTChar): o[-1].rendermode=self._r
        return adv
def _walk(o):
    for e in o:
        if isinstance(e,LTChar): yield e
        elif hasattr(e,'__iter__'): yield from _walk(e)

def body_signature(pdf_path):
    """Return (sig_letters_lowercased, bold_flags[]) for the whole volume body."""
    rs=PDFResourceManager(); dev=RM(rs); ip=PDFPageInterpreter(rs,dev)
    sig=[]; bold=[]
    with open(pdf_path,'rb') as f:
        for pg in PDFPage.get_pages(f):
            ip.process_page(pg)
            chars=[c for c in _walk(dev.get_result()) if c.size>=11]
            if not chars: continue
            # adaptive running-head drop: if the top line is separated by a gap, drop it
            ys=sorted({round(c.y1) for c in chars}, reverse=True)
            drop=None
            if len(ys)>=2 and (ys[0]-ys[1])>16: drop=ys[0]
            chars=[c for c in chars if round(c.y1)!=drop]
            chars.sort(key=lambda c:(-round(c.y1,0), c.x0))
            for c in chars:
                for ch in NFC(c.get_text()):
                    if ch.isalpha():
                        sig.append(ch.lower()); bold.append(getattr(c,'rendermode',0)==2)
    return ''.join(sig), bold

def _letters(txt):
    L=[]; idx=[]
    for i,ch in enumerate(txt):
        if ch.isalpha(): L.append(ch.lower()); idx.append(i)
    return ''.join(L), idx

def _spans_from(idxmap, bold, q):
    bi=set(idxmap[k] for k in range(len(idxmap)) if bold[q+k])
    spans=[]; s=prev=None
    for i in sorted(bi):
        if s is None: s=prev=i
        elif i==prev+1: prev=i
        else: spans.append([s,prev+1]); s=prev=i
    if s is not None: spans.append([s,prev+1])
    return spans

def align_paragraph(txt, sig, bold):
    """Return (spans, matched_bool). Whole-paragraph exact match, else sentence fallback."""
    txt=NFC(txt)
    ps, idx = _letters(txt)
    if len(ps)<8: return [], True   # too short to bold; treat as covered
    q=sig.find(ps)
    if q>=0:
        return _spans_from(idx, bold, q), True
    # ---- sentence-level fallback ----
    marked=txt.replace('','')
    # split into sentence chunks, keep offsets
    import re
    spans=[]; cursor=0; anchored=False
    pos=0
    for m in re.finditer(r'[^.?–!]*[.?–!]+\s*|[^.?–!]+$', txt):
        seg=m.group(0); segstart=m.start()
        sl=[]; sidx=[]
        for j,ch in enumerate(seg):
            if ch.isalpha(): sl.append(ch.lower()); sidx.append(segstart+j)
        sps=''.join(sl)
        if len(sps)<8: continue
        qq=sig.find(sps, cursor)
        if qq<0: qq=sig.find(sps)
        if qq<0: continue
        cursor=qq+len(sps); anchored=True
        spans+= _spans_from(sidx, bold, qq)
    return spans, anchored

def process_volume(layer, vol):
    pdf=os.path.join(ROOT, FOLDER[layer], vol+'.pdf')
    js=os.path.join(ROOT,'site', vol+'.json')
    paras=json.load(open(js))['paragraphs']
    sig,bold=body_signature(pdf)
    out={}; n_have=n_bold=n_miss=0
    for i,p in enumerate(paras):
        spans,matched=align_paragraph(p['text'], sig, bold)
        n_have+=1
        if spans: out[str(i)]=spans; n_bold+=1   # key by ordinal position (ids are not unique)
        if not matched: n_miss+=1
    json.dump(out, open(os.path.join(OUT, vol+'.bold.json'),'w'), ensure_ascii=False)
    return {'vol':vol,'layer':layer,'paras':n_have,'with_bold':n_bold,'unaligned':n_miss,'sig_len':len(sig)}

def process_sections(layer, vol):
    """Bold spans for the k:'gatha' entries of sections/<VOL>.json.

    THE SECTIONS PATH CARRIED NO BOLD AT ALL: it renders through `fmtText`,
    which takes no spans, because it was written for a four-pada opening gatha
    and never asked to carry a lemma.  A sections entry's text comes from the
    PRINTED stream, not from a corpus paragraph, so the ordinal-keyed spans in
    bold/<VOL>.bold.json cannot address it and translating their offsets would
    be guesswork.  It is aligned against the SAME render-mode signature
    instead -- the same evidence, no translation.

    Keyed "<anchor ordinal>:<index within that anchor's list>".
    MEASURED over the whole corpus 2026-07-27ah: 17 such entries in 12
    volumes, all 17 align, and exactly ONE carries bold (07DiA01, the
    Sumangalavilasini's opening gatha, 8 spans / 82 characters).
    """
    sec = os.path.join(ROOT, 'site', 'reader', 'sections', vol + '.json')
    if not os.path.exists(sec):
        return None
    S = json.load(open(sec, encoding='utf-8'))
    ent = [(o, i, x) for o, arr in S.items()
           for i, x in enumerate(arr) if x.get('k') == 'gatha']
    if not ent:
        return None
    sig, bold = body_signature(os.path.join(ROOT, FOLDER[layer], vol + '.pdf'))
    out, miss = {}, 0
    for o, i, x in ent:
        spans, matched = align_paragraph(str(x['l']).replace('\n', ' '), sig, bold)
        if not matched:
            miss += 1
        if spans:
            out['%s:%d' % (o, i)] = spans
    json.dump(out, open(os.path.join(OUT, vol + '.sect.json'), 'w'),
              ensure_ascii=False)
    return {'vol': vol, 'entries': len(ent), 'with_bold': len(out),
            'unaligned': miss}


def layer_of(vol):
    for layer,folder in FOLDER.items():
        if os.path.exists(os.path.join(ROOT,folder,vol+'.pdf')): return layer
    return None

if __name__=='__main__':
    vols=sys.argv[1:]
    if '--sections-only' in vols:
        # writes bold/<VOL>.sect.json and NOTHING else -- the .bold.json maps
        # are not touched, so this has no blast radius on the ordinal spans.
        for vol in [v for v in vols if v != '--sections-only']:
            layer=layer_of(vol)
            if not layer: print('SKIP (no pdf):',vol); continue
            r=process_sections(layer,vol)
            print('%-12s %s' % (vol, 'no sections gatha entries' if r is None
                  else 'entries=%d with_bold=%d unaligned=%d'
                       % (r['entries'],r['with_bold'],r['unaligned'])))
        sys.exit(0)
    report=[]
    t0=time.time()
    force='--force' in vols
    vols=[v for v in vols if v!='--force']
    budget=float(os.environ.get('BOLD_BUDGET','40'))
    for vol in vols:
        if time.time()-t0>budget: print('...budget reached, stopping'); break
        layer=layer_of(vol)
        if not layer: print('SKIP (no pdf):',vol); continue
        outp=os.path.join(OUT, vol+'.bold.json')
        if os.path.exists(outp) and not force: continue
        r=process_volume(layer,vol); report.append(r)
        print(f"{vol:12s} {layer:13s} paras={r['paras']:5d} bold={r['with_bold']:5d} unaligned={r['unaligned']:4d}")
    print(f"did {len(report)} vols in {time.time()-t0:.1f}s")
