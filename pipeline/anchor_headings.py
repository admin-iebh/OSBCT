#!/usr/bin/env python3
"""Precise, paragraph-level heading anchoring.

The page-level anchor (first paragraph on the heading's PDF page) collides
multiple headings onto one paragraph and misplaces mid-page headings. This
reads the PDF in reading order, pairs each heading with the paragraph that
immediately follows it, and maps that paragraph to our corpus by its opening
text (which is unique) — so every heading gets its own exact anchor key.

Output: reuses extract_toc helpers; produces {vol, books:[{title,key,chapters:[{label,key,subs:[{label,key}]}]}]}
"""
import json, os, re, sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTChar, LTTextLine, LTTextContainer, LAParams

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import importlib.util
_spec = importlib.util.spec_from_file_location('etoc', os.path.join(ROOT, 'pipeline', 'extract_toc.py'))
_m = importlib.util.module_from_spec(_spec)
_src = open(os.path.join(ROOT, 'pipeline', 'extract_toc.py')).read().split("if __name__")[0]
exec(_src, _m.__dict__)
RM = _m.RM; _fold = _m._fold; clean = _m.clean; titleish = _m.titleish
is_backmatter = _m.is_backmatter; is_endmarker = _m.is_endmarker; is_label = _m.is_label
genitive_index = _m.genitive_index; strip_num = _m.strip_num
TITLE_MIN = _m.TITLE_MIN; CHAP_SUFFIX = _m.CHAP_SUFFIX

def parse_events(pdf_path):
    """Ordered stream of ('head',label,size,bold) and ('para',opening_text)."""
    rs = PDFResourceManager(); dev = RM(rs, laparams=LAParams())
    ip = PDFPageInterpreter(rs, dev)
    events = []
    with open(pdf_path, 'rb') as f:
        for pi, pg in enumerate(PDFPage.get_pages(f)):
            ip.process_page(pg); lt = dev.get_result(); pw = pg.mediabox[2]
            lines = []
            for el in lt:
                if not isinstance(el, LTTextContainer): continue
                for ln in el:
                    if isinstance(ln, LTTextLine):
                        ch = [c for c in ln if isinstance(c, LTChar)]
                        if ch: lines.append((ln.y1, ln, ch))
            lines.sort(key=lambda t: -t[0])          # top to bottom
            for _, ln, ch in lines:
                t = ln.get_text().strip()
                if not t: continue
                sz = sum(c.size for c in ch) / len(ch)
                bold = sum(1 for c in ch if getattr(c, 'rm', 0) == 2) / len(ch)
                cx = (ln.x0 + ln.x1) / 2; centered = abs(cx - pw / 2) < 90
                left = ln.x0 < pw * 0.34
                if centered and len(t) <= 55 and (sz >= TITLE_MIN or sz >= 13 or (bold >= 0.6 and sz >= 11)):
                    ct = clean(t); f = _fold(ct)
                    if len(ct) < 4 or re.match(r'^[_\d\s.]+$', ct): continue
                    if is_backmatter(f) or is_endmarker(f) or is_label(f) or genitive_index(f): continue
                    lvl = 'title' if sz >= TITLE_MIN else ('chap' if sz >= 15 else 'sub')
                    events.append(('head', ct, sz, bold, lvl, pi))
                elif left and re.match(r'^\d+\.\s', t):
                    body = re.sub(r'^\d+\.\s*', '', t)
                    events.append(('para', body, pi))
    return events

# --- clean-label recovery from the corpus headings array (built with ToUnicode) ---
PALI = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ .()-0123456789')
def is_garbled(s):
    return any(c not in PALI for c in (s or ''))
FRONT = ('buddhavasse', 'marammavasse', 'nidanakatha', 'sanketa', 'romanized', 'chatthasangiti')
def is_front(f):
    return any(w in f for w in FRONT) or bool(re.match(r'^\d{3,4}$', f.strip()))

def clean_headings(vol):
    """ordered clean section/heading labels from the corpus, page-keyed."""
    d = json.load(open(os.path.join(ROOT, 'site', vol + '.json')))
    out = []
    for h in d.get('headings', []):
        t = (h.get('title') or '').strip()
        f = _fold(t)
        if not t or re.match(r'^[_\s.]+$', t): continue
        if is_backmatter(f) or is_endmarker(f) or is_front(f) or is_label(f): continue
        if t.rstrip('.').endswith(('bhāṇavāro', 'bhāṇavāraṁ')): continue   # recitation markers
        out.append((h.get('pdf_page'), t))
    return out

def corpus_index(vol):
    d = json.load(open(os.path.join(ROOT, 'site', vol + '.json')))['paragraphs']
    idx = []
    for p in d:
        tx = re.sub(r'^\s*\d+(-\d+)?\.\s*', '', p.get('text', ''))
        idx.append((p['key'], _fold(re.sub(r'[^A-Za-zĀĪŪṀṂṄÑṬḌṆḶāīūṁṃṅñṭḍṇḷ ]', '', tx))[:36].strip()))
    return idx

def anchor_for(events, ei, idx, ptr):
    """key for the paragraph following event ei; advances search pointer."""
    for j in range(ei + 1, len(events)):
        if events[j][0] == 'para':
            want = _fold(re.sub(r'[^A-Za-zĀĪŪṀṂṄÑṬḌṆḶāīūṁṃṅñṭḍṇḷ ]', '', events[j][1]))[:28].strip()
            if len(want) < 6: continue
            for k in range(ptr, len(idx)):
                if idx[k][1].startswith(want[:20]) or want[:20] in idx[k][1]:
                    return idx[k][0], k + 1
            for k in range(0, len(idx)):        # fallback: global
                if idx[k][1].startswith(want[:20]):
                    return idx[k][0], k + 1
            return None, ptr
    return None, ptr

def build(vol, pdf_path):
    events = parse_events(pdf_path)
    idx = corpus_index(vol)
    # book boundaries = title-level heads
    heads = [(i, e) for i, e in enumerate(events) if e[0] == 'head']
    titles = [(i, e[1]) for i, e in heads if e[4] == 'title']
    if not titles: titles = [(heads[0][0], None)]
    books = []; ptr = 0
    for bi, (ti, btitle) in enumerate(titles):
        nend = titles[bi + 1][0] if bi + 1 < len(titles) else len(events)
        chapters = []
        for i in range(ti, nend):
            e = events[i]
            if e[0] != 'head' or e[4] == 'title': continue
            key, ptr = anchor_for(events, i, idx, ptr)
            if key is None: continue
            if e[4] == 'chap' or (not chapters):
                chapters.append({'label': e[1], 'key': key, 'subs': []})
            else:
                chapters[-1]['subs'].append({'label': e[1], 'key': key})
        bkey = chapters[0]['key'] if chapters else idx[0][0]
        books.append({'title': btitle or vol, 'key': bkey, 'chapters': chapters})
    return {'vol': vol, 'books': books}

if __name__ == '__main__':
    for vol in sys.argv[1:]:
        r = build(vol, os.path.join(ROOT, 'pali-unicode', vol + '.pdf'))
        for b in r['books']:
            ns = sum(len(c['subs']) for c in b['chapters'])
            print(f"{vol} | {b['title']}: {len(b['chapters'])} chapters, {ns} subs")
