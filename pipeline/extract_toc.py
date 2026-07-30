#!/usr/bin/env python3
"""Extract a real, multi-level table of contents from the printed PDF of a
volume. The Chaṭṭhasaṅgāyana edition sets chapter titles as centred lines in a
larger font and sub-chapter titles as centred faux-bold (render-mode 2) lines
at body size. We capture both levels, drop end-markers and back-matter indices,
and anchor each heading to the first paragraph on its PDF page.

Output: site/reader/toc/<VOL>.toc.json
  {"vol":..,"title":..,"chapters":[{"label","key","page","subs":[{"label","key","page"}]}]}
"""
import json, os, re, sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTChar, LTTextLine, LTTextContainer, LAParams

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RM(PDFPageAggregator):
    def render_string(self, ts, *a, **k):
        self._rm = ts.render
        return super().render_string(ts, *a, **k)
    def render_char(self, matrix, font, fontsize, scaling, rise, cid, ncs, gs):
        w = super().render_char(matrix, font, fontsize, scaling, rise, cid, ncs, gs)
        try: self.cur_item._objs[-1].rm = getattr(self, '_rm', 0)
        except Exception: pass
        return w

def _fold(x):
    x = (x or '').lower()
    return ''.join({'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n',
                    'ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'}.get(c, c) for c in x)

# lines to drop entirely (end-markers + back-matter indices + front matter)
DROP = ('nitthit', 'anukkamanik', 'nanapatha', 'gathasuci', 'matika',
        'suci', 'uddana', 'chatthasangiti', 'romanized', 'vibhange', 'vibhango')

def is_backmatter(folded):
    if any(w in folded for w in DROP): return True
    fr = folded.rstrip('.').strip()
    # section/book end-markers: "… samattaṁ", "… niṭṭhitaṁ", "… samatto"
    return fr.endswith(('samatta', 'samattam', 'samatto', 'nitthita', 'nitthitam', 'nitthito'))

def lines_of_pdf(pdf_path):
    rs = PDFResourceManager(); dev = RM(rs, laparams=LAParams())
    ip = PDFPageInterpreter(rs, dev)
    out = []
    with open(pdf_path, 'rb') as f:
        for pi, pg in enumerate(PDFPage.get_pages(f)):
            ip.process_page(pg); lt = dev.get_result(); pw = pg.mediabox[2]
            for el in lt:
                if not isinstance(el, LTTextContainer): continue
                for ln in el:
                    if not isinstance(ln, LTTextLine): continue
                    t = ln.get_text().strip()
                    if not t or len(t) > 55: continue
                    ch = [c for c in ln if isinstance(c, LTChar)]
                    if not ch: continue
                    sz = sum(c.size for c in ch) / len(ch)
                    bold = sum(1 for c in ch if getattr(c, 'rm', 0) == 2) / len(ch)
                    cx = (ln.x0 + ln.x1) / 2
                    centered = abs(cx - pw / 2) < 90
                    out.append((pi, round(sz, 1), round(bold, 1), centered, t))
    return out

def clean(t):
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def strip_num(t):
    return re.sub(r'^\d+\.\s*', '', t).strip()

def titleish(t):
    """A heading is a short title (optionally numbered), not a bold sentence."""
    b = strip_num(t)
    if ',' in b or b.endswith(('ti', 'ti.', '”', '.')): return False
    if not b[:1].isupper(): return False
    return 1 <= len(b.split()) <= 6

ORDINALS = {'pathamo','pathama','pathamam','dutiyo','dutiya','dutiyam','tatiyo','tatiya','tatiyam',
            'catuttho','catuttha','catuttham','pancamo','pancama','pancamam','chattho','chattha','chatthama',
            'sattamo','sattama','atthamo','atthama','navamo','navama','dasamo','dasama','samattam','samatto','samatta'}
def is_endmarker(f):
    w = f.rstrip('.').split()
    if not w: return False
    last = re.sub(r'\d+$', '', w[-1])
    if last in ORDINALS: return True
    return w[-1].rstrip('.').rstrip('0123456789') in ('samattaṁ',) or any(
        w[-1].rstrip('.0123456789').endswith(s) for s in ('nitthita','nitthitam','nitthito','samatta','samattam','samatto'))

CHAP_SUFFIX = ('vagga','vaggo','nipata','kanda','kandam','samyutta','samyutto','pannasaka','pannasako',
               'khandhaka','pannasa','pannasaka')

def paras_by_page(vol):
    d = json.load(open(os.path.join(ROOT, 'site', vol + '.json')))['paragraphs']
    firstkey = {}
    for p in d:
        pg = p.get('pdf_page')
        if pg is not None and pg not in firstkey:
            firstkey[pg] = p['key']
    pages = sorted(firstkey)
    def key_for(pi):
        # first paragraph starting on this page, else nearest following page
        for pg in pages:
            if pg >= pi: return firstkey[pg], p_printed.get(pg, pg)
        return (d[-1]['key'], p_printed.get(pages[-1], pi)) if d else (None, pi)
    p_printed = {}
    for p in d:
        pg = p.get('pdf_page')
        if pg is not None and pg not in p_printed:
            p_printed[pg] = p.get('printed', pg)
    return key_for

def first_content_pi(vol):
    d = json.load(open(os.path.join(ROOT, 'site', vol + '.json')))['paragraphs']
    pgs = [p['pdf_page'] for p in d if p.get('pdf_page') is not None]
    return min(pgs) if pgs else 0

TITLE_MIN = 28.0     # book-title font (34–36); nikāya label is 24
CHAP_LO, CHAP_HI = 15.0, 26.0

def is_label(f):
    """nikāya / piṭaka running labels that are not chapters."""
    return f.endswith('nikaya') or f in ('vinayapitaka', 'suttapitaka', 'abhidhammapitaka')

def genitive_index(f):
    """running-head / index genitives like 'Sīlakkhandhavaggapāḷiyā'."""
    return f.endswith(('paliya', 'paliyam', 'pitake', 'pitakassa', 'nikaye', 'gathaya'))

def extract_volume(vol, pdf_path, opening_map=None):
    """Extract every book in a (possibly combined) volume, each with its
    chapters and sub-chapters, from the printed PDF headings."""
    opening_map = opening_map or {}
    rows = lines_of_pdf(pdf_path)
    key_for = paras_by_page(vol)
    d = json.load(open(os.path.join(ROOT, 'site', vol + '.json')))['paragraphs']
    start_pi = min([p['pdf_page'] for p in d if p.get('pdf_page') is not None] or [0])
    # book boundaries = size>=28 centred titles (not nikāya labels)
    marks = []
    for pi, sz, bold, cen, t in rows:
        if pi < 2 or not cen or sz < TITLE_MIN: continue   # title page precedes 1st para
        ct = clean(t); f = _fold(ct)
        if is_label(f) or genitive_index(f) or len(ct) < 4: continue
        if marks and marks[-1][0] == pi and marks[-1][1] == ct: continue
        marks.append((pi, ct))
    if not marks:                                  # fallback: single untitled book
        bf = next((p.get('book') for p in d if _fold(p.get('book') or '').endswith('pali')), None)
        marks = [(start_pi, bf or vol)]
    books = []
    for bi, (bpi, btitle) in enumerate(marks):
        nend = marks[bi + 1][0] if bi + 1 < len(marks) else 10 ** 9
        # gather candidate headings in this book's page range
        cands = []
        for pi, sz, bold, cen, t in rows:
            if pi < bpi or pi >= nend or not cen: continue
            ct = clean(t); f = _fold(ct)
            if is_backmatter(f) or is_endmarker(f) or is_label(f) or genitive_index(f): continue
            if re.match(r'^[_\d\s.]+$', ct) or len(ct) < 4: continue
            if f == _fold(btitle): continue                       # the title line itself
            big = CHAP_LO <= sz < CHAP_HI
            small = bold >= 0.6 and 11.0 <= sz < CHAP_LO
            if not (big or small) or not titleish(ct): continue
            cands.append({'pi': pi, 'sz': sz, 'big': big, 'ct': ct, 'f': f})
        # decide the chapter tier: size-16 headings if any; else the structural
        # (vagga/nipāta/…) size-12 headings; else everything is a chapter (Khuddakapāṭha)
        has_big = any(c['big'] for c in cands)
        def is_chap(c):
            if has_big: return c['big']
            return strip_num(c['ct']) and _fold(strip_num(c['ct'])).endswith(CHAP_SUFFIX)
        struct = any(is_chap(c) for c in cands)
        chapters = []
        for c in cands:
            chap = is_chap(c) if (has_big or struct) else True
            key, page = key_for(c['pi'])
            if chap:
                if chapters and chapters[-1]['label'] == c['ct']: continue
                chapters.append({'label': c['ct'], 'key': key, 'page': page, 'subs': []})
            else:
                if not chapters: continue
                subs = chapters[-1]['subs']
                if c['ct'] == chapters[-1]['label']: continue
                if subs and subs[-1]['label'] == c['ct'] and subs[-1]['key'] == key: continue
                subs.append({'label': c['ct'], 'key': key, 'page': page})
        # opening chapter shares the title page → anchor to first paragraph of book
        bkey, bpage = key_for(bpi)
        if not chapters or chapters[0]['key'] != bkey:
            name = opening_map.get(btitle)
            if not name:                            # derive from the book field of the first paragraph
                bord = int(bkey.split('#')[1]); b0 = _fold((d[bord].get('book') or '') if bord < len(d) else '')
                bookf = d[bord].get('book') if bord < len(d) else None
                if b0.endswith(('khandhaka', 'kanda')):
                    name = bookf
                    if chapters and re.match(r'^2\.\s', chapters[0]['label']): name = '1. ' + name
            if name:
                chapters.insert(0, {'label': name, 'key': bkey, 'page': bpage, 'subs': []})
        # number repeated sub labels
        for c in chapters:
            cnt = {}
            for s in c['subs']: cnt[s['label']] = cnt.get(s['label'], 0) + 1
            seen2 = {}
            for s in c['subs']:
                if cnt[s['label']] > 1:
                    seen2[s['label']] = seen2.get(s['label'], 0) + 1
                    s['label'] = f"{s['label']} ({seen2[s['label']]})"
        books.append({'title': clean(btitle), 'key': bkey, 'chapters': chapters})
    return {'vol': vol, 'books': books}

def extract(vol, pdf_path, title, chap_min=15.0, opening=None):
    rows = lines_of_pdf(pdf_path)
    key_for = paras_by_page(vol)
    start_pi = first_content_pi(vol)
    tfold = _fold(title)            # e.g. "parajikapali"
    tstem = tfold.rstrip('i')       # "parajikapal" -> matches genitive "parajikapaliya"
    chapters = []
    for pi, sz, bold, centered, t in rows:
        if pi < start_pi: continue        # drop front matter (colophon, script guide)
        if not centered: continue
        ct = clean(t); f = _fold(ct)
        # stop at the book-end marker (e.g. "Pārājikapāḷi niṭṭhitā"); chapter-end
        # markers like "Pārājikakaṇḍaṁ niṭṭhitaṁ" don't match the full book stem
        if 'nitthit' in f and f.startswith(tstem):
            break
        if is_backmatter(f): continue
        if re.match(r'^[_\d\s.]+$', ct) or len(ct) < 4: continue
        # drop index headers that repeat the book title in the genitive
        if f.startswith(tstem) : continue
        if f in ('vinayapitaka', 'suttapitaka', 'abhidhammapitaka'): continue
        if sz >= chap_min:               # chapter level
            key, page = key_for(pi)
            if chapters and chapters[-1]['label'] == ct: continue
            chapters.append({'label': ct, 'key': key, 'page': page, 'subs': []})
        elif bold >= 0.6 and 11.0 <= sz < chap_min and titleish(ct):  # sub-chapter
            if not chapters: continue
            key, page = key_for(pi)
            if ct == chapters[-1]['label']: continue
            subs = chapters[-1]['subs']
            if subs and subs[-1]['label'] == ct and subs[-1]['key'] == key: continue
            subs.append({'label': ct, 'key': key, 'page': page})
    # The first chapter of most volumes shares the volume title page, so it has
    # no separate mid-page heading and is missed. Anchor it to the first paragraph.
    d = json.load(open(os.path.join(ROOT, 'site', vol + '.json')))['paragraphs']
    key0, printed0, book0 = d[0]['key'], d[0].get('printed', 1), d[0].get('book') or ''
    if not chapters or chapters[0]['key'] != key0:
        name = opening
        if not name:                       # derive from the book field if chapter-like
            bf = _fold(book0)
            if bf.endswith(('khandhaka', 'kanda')):
                name = book0
                if chapters and re.match(r'^2\.\s', chapters[0]['label']):
                    name = '1. ' + name
        if name:
            chapters.insert(0, {'label': name, 'key': key0, 'page': printed0, 'subs': []})
    # number sub-headings that repeat within a chapter (e.g. Vinītavatthu)
    for c in chapters:
        cnt = {}
        for s in c['subs']:
            cnt[s['label']] = cnt.get(s['label'], 0) + 1
        seen2 = {}
        for s in c['subs']:
            if cnt[s['label']] > 1:
                seen2[s['label']] = seen2.get(s['label'], 0) + 1
                s['label'] = f"{s['label']} ({seen2[s['label']]})"
    return {'vol': vol, 'title': title, 'chapters': chapters}

# The five books of the Vinayapiṭaka, one per physical volume.
# (code, book title, opening-chapter name for the section that shares the title page)
VINAYA = [
    ('01Vin01', 'Pārājikapāḷi', None),
    ('02Vin02', 'Pācittiyapāḷi', '5. Pācittiyakaṇḍa'),
    ('03Vin03', 'Mahāvaggapāḷi', None),
    ('04Vin04', 'Cūḷavaggapāḷi', None),
    ('05Vin05', 'Parivārapāḷi', 'Mahāvibhaṅga'),
]

# opening-chapter names for books whose first section shares the title page
OPENING = {'Pācittiyapāḷi': '5. Pācittiyakaṇḍa', 'Parivārapāḷi': 'Mahāvibhaṅga'}

if __name__ == '__main__':
    import sys, time
    outdir = os.path.join(ROOT, 'site', 'reader', 'toc')
    os.makedirs(outdir, exist_ok=True)
    man = json.load(open(os.path.join(ROOT, 'site', 'reader', 'manifest.json')))['volumes']
    canon = [c for c, m in man.items() if m['layer'] == 'canon']
    budget = float(os.environ.get('TOC_BUDGET', '1e9'))
    force = '--force' in sys.argv
    t0 = time.time(); done = 0
    for vol in canon:
        out = os.path.join(outdir, vol + '.toc.json')
        if os.path.exists(out) and not force: continue
        if time.time() - t0 > budget: print('...budget reached'); break
        r = extract_volume(vol, os.path.join(ROOT, 'pali-unicode', vol + '.pdf'), OPENING)
        json.dump(r, open(out, 'w'), ensure_ascii=False)
        nb = len(r['books']); nc = sum(len(b['chapters']) for b in r['books'])
        print(f"{vol}: {nb} book(s), {nc} chapters -> {[b['title'] for b in r['books']]}")
        done += 1
    print(f"done {done} volumes in {time.time()-t0:.0f}s")
